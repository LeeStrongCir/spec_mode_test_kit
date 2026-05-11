"""
Integration tests for POST /api/v1/lecs-hosts/{id}/start endpoint.

Validates state machine logic:
- "stopped" -> "starting" and "failed" -> "starting" transitions allowed
- Transitional states reject all operations
- Non-listed transitions return 403 Forbidden
- Authorization and authentication checks
"""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.db import async_session_factory
from app.models.user import User, UserStatus
from app.security.jwt import create_access_token
from app.services.password_service import hash_password


async def _create_host(db_session, user, *, status: str, host_id: uuid.UUID | None = None):
    """Seed a LECSHost record directly into the database with the given status."""
    from app.models.lecs_host import LECSHost

    if host_id is None:
        host_id = uuid.uuid4()

    host = LECSHost(
        id=host_id,
        user_id=user.id,
        hostname=f"testhost_{host_id.hex[:8]}",
        billing_mode="subscription",
        instance_type="economy",
        spec_id="eco-2c2g",
        vcpu=2,
        ram_gb=2,
        system_disk_gb=40,
        os_image="huawei_euler",
        ip_mode="dhcp",
        status=status,
        duration=1,
        unit_price=100.0,
        username="admin",
        password_hash=hash_password("TestPass123!"),
    )
    db_session.add(host)
    await db_session.commit()
    await db_session.refresh(host)
    return host


# ---------------------------------------------------------------------------
# TC-041: Stopped start — "stopped" -> "starting"
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_start_host_stopped_to_starting(authenticated_client: AsyncClient, db_session, test_user):
    """POST /api/v1/lecs-hosts/{id}/start from 'stopped' state returns 200 and transitions to 'starting'."""
    host = await _create_host(db_session, test_user, status="stopped")

    response = await authenticated_client.post(f"/api/v1/lecs-hosts/{host.id}/start")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "starting"
    assert "task_id" in body or body.get("async") is True  # async execution indicator

    # Verify DB state changed
    async with async_session_factory() as session:
        result = await session.execute(select(host.__class__).where(host.__class__.id == host.id))
        updated = result.scalars().first()
        assert updated.status == "starting"


# ---------------------------------------------------------------------------
# TC-042: Failed start — "failed" -> "starting"
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_start_host_failed_to_starting(authenticated_client: AsyncClient, db_session, test_user):
    """POST /api/v1/lecs-hosts/{id}/start from 'failed' state returns 200 and transitions to 'starting'."""
    host = await _create_host(db_session, test_user, status="failed")

    response = await authenticated_client.post(f"/api/v1/lecs-hosts/{host.id}/start")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "starting"
    assert "task_id" in body or body.get("async") is True  # async execution indicator

    # Verify DB state changed
    async with async_session_factory() as session:
        result = await session.execute(select(host.__class__).where(host.__class__.id == host.id))
        updated = result.scalars().first()
        assert updated.status == "starting"


# ---------------------------------------------------------------------------
# TC-API-041: Wrong state — "normal" host cannot be started
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_start_host_already_normal(authenticated_client: AsyncClient, db_session, test_user):
    """POST start on a 'normal' host returns 403 Forbidden."""
    host = await _create_host(db_session, test_user, status="normal")

    response = await authenticated_client.post(f"/api/v1/lecs-hosts/{host.id}/start")

    assert response.status_code == 403


# ---------------------------------------------------------------------------
# TC-043: Wrong state — "shutting_down" host cannot be started
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_start_host_while_shutting_down(authenticated_client: AsyncClient, db_session, test_user):
    """POST start on a 'shutting_down' host returns 403 Forbidden (transitional state protection)."""
    host = await _create_host(db_session, test_user, status="shutting_down")

    response = await authenticated_client.post(f"/api/v1/lecs-hosts/{host.id}/start")

    assert response.status_code == 403


# ---------------------------------------------------------------------------
# TC-043: Transitional state retry — "starting" host cannot be started again
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_start_host_already_starting(authenticated_client: AsyncClient, db_session, test_user):
    """POST start on a 'starting' host returns 403 (concurrent operation protection)."""
    host = await _create_host(db_session, test_user, status="starting")

    response = await authenticated_client.post(f"/api/v1/lecs-hosts/{host.id}/start")

    assert response.status_code == 403


# ---------------------------------------------------------------------------
# TC-043: Wrong state — "creating" host cannot be started
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_start_host_while_creating(authenticated_client: AsyncClient, db_session, test_user):
    """POST start on a 'creating' host returns 403 or 409 (transitional state)."""
    host = await _create_host(db_session, test_user, status="creating")

    response = await authenticated_client.post(f"/api/v1/lecs-hosts/{host.id}/start")

    assert response.status_code in (403, 409)


# ---------------------------------------------------------------------------
# TC-043: Wrong state — "deleting" host cannot be started
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_start_host_while_deleting(authenticated_client: AsyncClient, db_session, test_user):
    """POST start on a 'deleting' host returns 403 or 409 (transitional state)."""
    host = await _create_host(db_session, test_user, status="deleting")

    response = await authenticated_client.post(f"/api/v1/lecs-hosts/{host.id}/start")

    assert response.status_code in (403, 409)


# ---------------------------------------------------------------------------
# TC-API-041: 401 Unauthenticated
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_start_host_unauthenticated(unauthenticated_client: AsyncClient, db_session, test_user):
    """POST start without authentication returns 401 Unauthorized."""
    host = await _create_host(db_session, test_user, status="stopped")

    response = await unauthenticated_client.post(f"/api/v1/lecs-hosts/{host.id}/start")

    assert response.status_code == 401


# ---------------------------------------------------------------------------
# TC-API-041: 403 Cross-user — User B tries to start User A's host
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_start_host_cross_user(authenticated_client_b: AsyncClient, db_session, test_user):
    """User B tries to start User A's host → 403 Forbidden."""
    host = await _create_host(db_session, test_user, status="stopped")

    response = await authenticated_client_b.post(f"/api/v1/lecs-hosts/{host.id}/start")

    assert response.status_code == 403


# ---------------------------------------------------------------------------
# TC-API-041: Non-existent host
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_start_host_not_found(authenticated_client: AsyncClient):
    """POST start for a non-existent host ID returns 404 Not Found."""
    fake_id = uuid.uuid4()

    response = await authenticated_client.post(f"/api/v1/lecs-hosts/{fake_id}/start")

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Async indicator verification
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_start_host_async_response(authenticated_client: AsyncClient, db_session, test_user):
    """POST start response indicates async execution (task_id or async flag)."""
    host = await _create_host(db_session, test_user, status="stopped")

    response = await authenticated_client.post(f"/api/v1/lecs-hosts/{host.id}/start")

    assert response.status_code == 200
    body = response.json()
    # Response must indicate async operation
    has_async_indicator = (
        "task_id" in body
        or body.get("async") is True
        or "message" in body
        or body.get("status") == "starting"
    )
    assert has_async_indicator, f"Response should indicate async execution: {body}"

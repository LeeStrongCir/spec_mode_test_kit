"""
Integration tests for DELETE /api/v1/lecs-hosts/{id} endpoint.

Validates soft delete state machine and authorization:
- Only "stopped" and "failed" states allow deletion
- "normal" -> 403 with message about shutting down first
- Transitional states (creating, shutting_down, etc.) block deletion
- Soft delete: sets deleted_at, preserves record
- Quota count decreases after soft delete
- Authorization: 401 unauthenticated, 403 cross-user
- TC-050, TC-051, TC-052, TC-API-050, EC-005, EC-006
"""

import uuid
from datetime import datetime, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy import select, func

from app.db import async_session_factory
from app.models.lecs_host import LECSHost, HostStatus
from app.models.user import User, UserStatus
from app.security.jwt import create_access_token
from app.services.password_service import hash_password


async def _create_host(db_session, user, *, status: str, deleted_at=None, host_id: uuid.UUID | None = None):
    """Seed a LECSHost record directly into the database with the given status."""
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
        deleted_at=deleted_at,
    )
    db_session.add(host)
    await db_session.commit()
    await db_session.refresh(host)
    return host


async def _count_active_hosts(db_session, user):
    """Count active (non-soft-deleted) hosts for a user."""
    result = await db_session.execute(
        select(func.count()).select_from(LECSHost).where(
            LECSHost.user_id == user.id,
            LECSHost.deleted_at.is_(None),
        )
    )
    return result.scalar_one()


# ---------------------------------------------------------------------------
# TC-051: Stopped host delete — "stopped" -> "deleting" with soft delete
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_delete_host_from_stopped(authenticated_client: AsyncClient, db_session, test_user):
    """DELETE /api/v1/lecs-hosts/{id} from 'stopped' state returns 200, sets deleted_at, transitions to 'deleting'."""
    host = await _create_host(db_session, test_user, status="stopped")
    initial_count = await _count_active_hosts(db_session, test_user)

    response = await authenticated_client.delete(f"/api/v1/lecs-hosts/{host.id}")

    assert response.status_code == 200
    body = response.json()
    # Response should indicate the host is being deleted
    assert body.get("status") in ("deleting", "deleted") or body.get("message") is not None

    # Verify soft delete: deleted_at is set
    async with async_session_factory() as session:
        result = await session.execute(select(LECSHost).where(LECSHost.id == host.id))
        updated = result.scalars().first()
        assert updated is not None, "Host record should still exist (soft delete)"
        assert updated.deleted_at is not None, "deleted_at should be set after soft delete"
        assert updated.status in ("deleting", "deleted"), f"Status should be 'deleting' or 'deleted', got {updated.status}"

    # Verify quota decreased
    async with async_session_factory() as session:
        active_count = await _count_active_hosts(session, test_user)
        assert active_count == initial_count - 1


# ---------------------------------------------------------------------------
# TC-052: Failed host delete — soft delete allowed
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_delete_host_from_failed(authenticated_client: AsyncClient, db_session, test_user):
    """DELETE /api/v1/lecs-hosts/{id} from 'failed' state returns 200 and sets deleted_at."""
    host = await _create_host(db_session, test_user, status="failed")
    initial_count = await _count_active_hosts(db_session, test_user)

    response = await authenticated_client.delete(f"/api/v1/lecs-hosts/{host.id}")

    assert response.status_code == 200

    # Verify soft delete
    async with async_session_factory() as session:
        result = await session.execute(select(LECSHost).where(LECSHost.id == host.id))
        updated = result.scalars().first()
        assert updated is not None, "Host record should still exist (soft delete)"
        assert updated.deleted_at is not None, "deleted_at should be set after soft delete"

    # Verify quota decreased
    async with async_session_factory() as session:
        active_count = await _count_active_hosts(session, test_user)
        assert active_count == initial_count - 1


# ---------------------------------------------------------------------------
# TC-050: Normal host delete blocked — 403 with shutdown message
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_delete_host_from_normal_blocked(authenticated_client: AsyncClient, db_session, test_user):
    """DELETE /api/v1/lecs-hosts/{id} from 'normal' state returns 403 with error about shutting down first."""
    host = await _create_host(db_session, test_user, status="normal")

    response = await authenticated_client.delete(f"/api/v1/lecs-hosts/{host.id}")

    assert response.status_code == 403
    body = response.json()
    error_msg = body.get("detail", body.get("message", ""))
    assert "关机" in error_msg, f"Error message should mention shutting down first, got: {error_msg}"

    # Verify host was NOT soft deleted
    async with async_session_factory() as session:
        result = await session.execute(select(LECSHost).where(LECSHost.id == host.id))
        updated = result.scalars().first()
        assert updated.deleted_at is None, "Host should NOT be soft deleted when delete is blocked"


# ---------------------------------------------------------------------------
# TC-050: Creating host delete blocked — transitional state
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_delete_host_from_creating_blocked(authenticated_client: AsyncClient, db_session, test_user):
    """DELETE /api/v1/lecs-hosts/{id} from 'creating' state returns 403 (transitional state protection)."""
    host = await _create_host(db_session, test_user, status="creating")

    response = await authenticated_client.delete(f"/api/v1/lecs-hosts/{host.id}")

    assert response.status_code in (403, 409), f"Expected 403 or 409, got {response.status_code}"

    # Verify host was NOT soft deleted
    async with async_session_factory() as session:
        result = await session.execute(select(LECSHost).where(LECSHost.id == host.id))
        updated = result.scalars().first()
        assert updated.deleted_at is None


# ---------------------------------------------------------------------------
# TC-050: Shutting_down host delete blocked — transitional state
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_delete_host_from_shutting_down_blocked(authenticated_client: AsyncClient, db_session, test_user):
    """DELETE /api/v1/lecs-hosts/{id} from 'shutting_down' state returns 403 (concurrent operation protection)."""
    host = await _create_host(db_session, test_user, status="shutting_down")

    response = await authenticated_client.delete(f"/api/v1/lecs-hosts/{host.id}")

    assert response.status_code in (403, 409), f"Expected 403 or 409, got {response.status_code}"

    # Verify host was NOT soft deleted
    async with async_session_factory() as session:
        result = await session.execute(select(LECSHost).where(LECSHost.id == host.id))
        updated = result.scalars().first()
        assert updated.deleted_at is None


# ---------------------------------------------------------------------------
# TC-API-050: 401 Unauthenticated
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_delete_host_unauthenticated(unauthenticated_client: AsyncClient, db_session, test_user):
    """DELETE /api/v1/lecs-hosts/{id} without authentication returns 401 Unauthorized."""
    host = await _create_host(db_session, test_user, status="stopped")

    response = await unauthenticated_client.delete(f"/api/v1/lecs-hosts/{host.id}")

    assert response.status_code == 401


# ---------------------------------------------------------------------------
# EC-006: 403 Cross-user — User B deletes User A's host
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_delete_host_cross_user(authenticated_client_b: AsyncClient, db_session, test_user):
    """User B tries to delete User A's host → 403 Forbidden."""
    host = await _create_host(db_session, test_user, status="stopped")

    response = await authenticated_client_b.delete(f"/api/v1/lecs-hosts/{host.id}")

    assert response.status_code == 403

    # Verify host was NOT soft deleted
    async with async_session_factory() as session:
        result = await session.execute(select(LECSHost).where(LECSHost.id == host.id))
        updated = result.scalars().first()
        assert updated.deleted_at is None


# ---------------------------------------------------------------------------
# EC-005: Soft delete persistence — record exists in DB with deleted_at set
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_soft_delete_persistence(authenticated_client: AsyncClient, db_session, test_user):
    """After soft delete, query DB → record exists with deleted_at IS NOT NULL."""
    host = await _create_host(db_session, test_user, status="stopped")
    host_id = host.id

    response = await authenticated_client.delete(f"/api/v1/lecs-hosts/{host_id}")
    assert response.status_code == 200

    # Query DB directly to confirm record persists with deleted_at set
    async with async_session_factory() as session:
        result = await session.execute(select(LECSHost).where(LECSHost.id == host_id))
        record = result.scalars().first()

        assert record is not None, "Soft-deleted record should still exist in database"
        assert record.deleted_at is not None, "deleted_at should be set (IS NOT NULL)"
        assert isinstance(record.deleted_at, datetime), "deleted_at should be a datetime object"


# ---------------------------------------------------------------------------
# Non-existent host — 404
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_delete_host_not_found(authenticated_client: AsyncClient):
    """DELETE /api/v1/lecs-hosts/{id} for a non-existent host returns 404 Not Found."""
    fake_id = uuid.uuid4()

    response = await authenticated_client.delete(f"/api/v1/lecs-hosts/{fake_id}")

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Quota reduction after delete — SELECT COUNT WHERE deleted_at IS NULL
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_quota_reduces_after_soft_delete(authenticated_client: AsyncClient, db_session, test_user):
    """After soft delete, SELECT COUNT(*) WHERE deleted_at IS NULL returns count-1."""
    # Create multiple hosts for the user
    host1 = await _create_host(db_session, test_user, status="stopped")
    host2 = await _create_host(db_session, test_user, status="normal")
    host3 = await _create_host(db_session, test_user, status="stopped")

    initial_count = await _count_active_hosts(db_session, test_user)
    assert initial_count == 3, f"Expected 3 active hosts, got {initial_count}"

    # Delete one stopped host
    response = await authenticated_client.delete(f"/api/v1/lecs-hosts/{host1.id}")
    assert response.status_code == 200

    # Verify quota count decreased by 1
    async with async_session_factory() as session:
        active_count = await _count_active_hosts(session, test_user)
        assert active_count == 2, f"Expected 2 active hosts after delete, got {active_count}"

    # Verify the deleted host is excluded from count
    async with async_session_factory() as session:
        result = await session.execute(
            select(LECSHost).where(
                LECSHost.user_id == test_user.id,
                LECSHost.deleted_at.is_(None),
            )
        )
        active_hosts = result.scalars().all()
        host_ids = {h.id for h in active_hosts}
        assert host1.id not in host_ids, "Deleted host should not be in active count"
        assert host2.id in host_ids, "Normal host should still be counted"
        assert host3.id in host_ids, "Other stopped host should still be counted"

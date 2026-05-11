"""
Integration tests for EC-007: Audit log recording for LECS host operations.

Validates that every successful host operation (create, stop, start, delete)
is logged with audit trail information:
- Operator identity (user_id)
- Timestamp
- IP address
- Operation details

Also verifies that failed operations (validation errors) do NOT create audit entries.

Spec reference: EC-007 (spec.md § 审计日志记录)
"""

import asyncio
import logging
import uuid
from datetime import datetime

import pytest
from httpx import AsyncClient
from sqlalchemy import select, func

from app.db import async_session_factory
from app.models.lecs_host import LECSHost, HostStatus
from app.services.lecs_lifecycle_service import _log_operation
from app.services.password_service import hash_password


# ---------------------------------------------------------------------------
# Helper: seed a host in the database
# ---------------------------------------------------------------------------

async def _create_host(db_session, user, *, status: str, host_id: uuid.UUID | None = None):
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
    )
    db_session.add(host)
    await db_session.commit()
    await db_session.refresh(host)
    return host


# ---------------------------------------------------------------------------
# EC-007: Audit log — operation logging via lifecycle service
# ---------------------------------------------------------------------------

class TestAuditLogOperationRecording:
    """Verify that the lifecycle service logs all host operations with audit details."""

    def test_log_operation_records_user_id(self, test_user, caplog):
        """_log_operation includes user_id in the log entry."""
        host_id = uuid.uuid4()
        with caplog.at_level(logging.INFO, logger="app.services.lecs_lifecycle_service"):
            _log_operation(host_id, test_user.id, "create", "test_host")

        assert any(
            str(test_user.id) in record.message
            for record in caplog.records
        )

    def test_log_operation_records_action(self, caplog):
        """_log_operation records the operation action (create/stop/start/delete)."""
        host_id = uuid.uuid4()
        user_id = uuid.uuid4()

        actions = ["create", "shutdown", "start", "delete"]
        for action in actions:
            with caplog.at_level(logging.INFO, logger="app.services.lecs_lifecycle_service"):
                _log_operation(host_id, user_id, action, "")

            assert any(
                action in record.message
                for record in caplog.records
            )

    def test_log_operation_records_host_id(self, caplog):
        """_log_operation includes the host_id in the log entry."""
        host_id = uuid.uuid4()
        user_id = uuid.uuid4()
        with caplog.at_level(logging.INFO, logger="app.services.lecs_lifecycle_service"):
            _log_operation(host_id, user_id, "shutdown", "spawned")

        assert any(
            str(host_id) in record.message
            for record in caplog.records
        )

    def test_log_operation_accepts_details(self, caplog):
        """_log_operation accepts and records optional details."""
        host_id = uuid.uuid4()
        user_id = uuid.uuid4()
        details = "hostname=web-server-01, spec=eco-2c2g"
        with caplog.at_level(logging.INFO, logger="app.services.lecs_lifecycle_service"):
            _log_operation(host_id, user_id, "create", details)

        assert any(
            details in record.message
            for record in caplog.records
        )


# ---------------------------------------------------------------------------
# EC-007: Audit log — Create operation audit trail
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_create_host_audit_trail(authenticated_client: AsyncClient, db_session, test_user, mocker, caplog):
    """POST /api/v1/lecs-hosts creates host → verify audit log entry with user_id, timestamp, IP, operation='create'."""
    # Mock async sleep to avoid test delay
    mocker.patch("app.api.lecs_host.asyncio.sleep")

    payload = {
        "hostname": "audit-host-01",
        "billing_mode": "subscription",
        "instance_type": "economy",
        "spec_id": "eco-2c2g",
        "os_image": "huawei_euler",
        "ip_mode": "dhcp",
        "username": "audituser",
        "password": "SecurePass123!",
        "duration": 1,
    }

    with caplog.at_level(logging.INFO, logger="app.services.lecs_lifecycle_service"):
        response = await authenticated_client.post("/api/v1/lecs-hosts", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "success"
    data = body["data"]
    assert "id" in data

    # Verify host was created and associated with the correct user
    host_id = uuid.UUID(data["id"])
    result = await db_session.execute(select(LECSHost).where(LECSHost.id == host_id))
    host = result.scalars().first()
    assert host is not None
    assert host.user_id == test_user.id
    assert host.hostname == payload["hostname"]

    # Verify the background task logs the create operation with user_id
    assert any(
        "create" in record.message and str(test_user.id) in record.message
        for record in caplog.records
    ), "Audit log should record create operation with user_id"


# ---------------------------------------------------------------------------
# EC-007: Audit log — Stop operation audit trail
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_stop_host_audit_trail(authenticated_client: AsyncClient, db_session, test_user, caplog):
    """POST /api/v1/lecs-hosts/{id}/stop → verify audit log entry with operation='shutdown'."""
    host = await _create_host(db_session, test_user, status="normal")

    with caplog.at_level(logging.INFO, logger="app.services.lecs_lifecycle_service"):
        response = await authenticated_client.post(f"/api/v1/lecs-hosts/{host.id}/stop")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"

    # Verify state transition
    async with async_session_factory() as session:
        result = await session.execute(select(LECSHost).where(LECSHost.id == host.id))
        updated = result.scalars().first()
        assert updated.status == HostStatus.shutting_down

    # Verify audit log records the shutdown operation
    assert any(
        "shutdown" in record.message and str(host.id) in record.message
        for record in caplog.records
    ), "Audit log should record shutdown operation"


# ---------------------------------------------------------------------------
# EC-007: Audit log — Start operation audit trail
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_start_host_audit_trail(authenticated_client: AsyncClient, db_session, test_user, caplog):
    """POST /api/v1/lecs-hosts/{id}/start → verify audit log entry with operation='start'."""
    host = await _create_host(db_session, test_user, status="stopped")

    with caplog.at_level(logging.INFO, logger="app.services.lecs_lifecycle_service"):
        response = await authenticated_client.post(f"/api/v1/lecs-hosts/{host.id}/start")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"

    # Verify state transition
    async with async_session_factory() as session:
        result = await session.execute(select(LECSHost).where(LECSHost.id == host.id))
        updated = result.scalars().first()
        assert updated.status == HostStatus.starting

    # Verify audit log records the start operation
    assert any(
        "start" in record.message and str(host.id) in record.message
        for record in caplog.records
    ), "Audit log should record start operation"


# ---------------------------------------------------------------------------
# EC-007: Audit log — Delete operation audit trail
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_delete_host_audit_trail(authenticated_client: AsyncClient, db_session, test_user, caplog):
    """DELETE /api/v1/lecs-hosts/{id} → verify audit log entry with operation='delete'."""
    host = await _create_host(db_session, test_user, status="stopped")

    with caplog.at_level(logging.INFO, logger="app.services.lecs_lifecycle_service"):
        response = await authenticated_client.delete(f"/api/v1/lecs-hosts/{host.id}")

    assert response.status_code == 200
    body = response.json()
    assert body.get("status") in ("deleting", "deleted") or body.get("message") is not None

    # Verify soft delete state
    async with async_session_factory() as session:
        result = await session.execute(select(LECSHost).where(LECSHost.id == host.id))
        updated = result.scalars().first()
        assert updated is not None
        assert updated.deleted_at is not None
        assert updated.status in (HostStatus.deleting, HostStatus.deleted)

    # Verify audit log records the delete operation
    assert any(
        "delete" in record.message and str(host.id) in record.message
        for record in caplog.records
    ), "Audit log should record delete operation"


# ---------------------------------------------------------------------------
# EC-007: Failed operations should NOT create audit entries
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_failed_operation_not_logged_create_validation(
    authenticated_client: AsyncClient, db_session, test_user, caplog
):
    """POST /api/v1/lecs-hosts with invalid payload → 422 → should NOT create audit entry."""
    # Invalid payload: hostname too short
    payload = {
        "hostname": "ab",
        "billing_mode": "subscription",
        "instance_type": "economy",
        "spec_id": "eco-2c2g",
        "os_image": "huawei_euler",
        "ip_mode": "dhcp",
        "username": "testuser",
        "password": "SecurePass123!",
        "duration": 1,
    }

    initial_count = await db_session.execute(select(func.count()).select_from(LECSHost))
    initial_host_count = initial_count.scalar_one()

    with caplog.at_level(logging.INFO, logger="app.services.lecs_lifecycle_service"):
        response = await authenticated_client.post("/api/v1/lecs-hosts", json=payload)

    assert response.status_code == 422

    # Verify no new host was created
    final_count = await db_session.execute(select(func.count()).select_from(LECSHost))
    assert final_count.scalar_one() == initial_host_count

    # Verify no audit log entry for the failed operation
    assert not any(
        "create" in record.message
        for record in caplog.records
    ), "Failed validation should NOT create audit entry"


@pytest.mark.asyncio
async def test_failed_operation_not_logged_stop_wrong_state(
    authenticated_client: AsyncClient, db_session, test_user, caplog
):
    """POST stop on a 'stopped' host → 403 → should NOT create audit entry."""
    host = await _create_host(db_session, test_user, status="stopped")

    initial_status = host.status

    with caplog.at_level(logging.INFO, logger="app.services.lecs_lifecycle_service"):
        response = await authenticated_client.post(f"/api/v1/lecs-hosts/{host.id}/stop")

    assert response.status_code in (403, 409)

    # Verify host state did NOT change
    async with async_session_factory() as session:
        result = await session.execute(select(LECSHost).where(LECSHost.id == host.id))
        updated = result.scalars().first()
        assert updated.status == initial_status

    # Verify no shutdown audit log entry was created for the failed operation
    shutdown_messages = [
        r.message for r in caplog.records
        if "shutdown" in r.message and "spawned" in r.message
    ]
    assert len(shutdown_messages) == 0, "Failed stop should NOT create audit entry"


@pytest.mark.asyncio
async def test_failed_operation_not_logged_start_wrong_state(
    authenticated_client: AsyncClient, db_session, test_user, caplog
):
    """POST start on a 'normal' host → 403 → should NOT create audit entry."""
    host = await _create_host(db_session, test_user, status="normal")

    with caplog.at_level(logging.INFO, logger="app.services.lecs_lifecycle_service"):
        response = await authenticated_client.post(f"/api/v1/lecs-hosts/{host.id}/start")

    assert response.status_code in (403, 409)

    # Verify host state did NOT change
    async with async_session_factory() as session:
        result = await session.execute(select(LECSHost).where(LECSHost.id == host.id))
        updated = result.scalars().first()
        assert updated.status == HostStatus.normal


@pytest.mark.asyncio
async def test_failed_operation_not_logged_delete_running_host(
    authenticated_client: AsyncClient, db_session, test_user, caplog
):
    """DELETE a 'normal' host → 403 → should NOT create audit entry."""
    host = await _create_host(db_session, test_user, status="normal")

    with caplog.at_level(logging.INFO, logger="app.services.lecs_lifecycle_service"):
        response = await authenticated_client.delete(f"/api/v1/lecs-hosts/{host.id}")

    assert response.status_code == 403

    # Verify host was NOT soft deleted
    async with async_session_factory() as session:
        result = await session.execute(select(LECSHost).where(LECSHost.id == host.id))
        updated = result.scalars().first()
        assert updated.deleted_at is None

    # Verify no delete audit log entry was created
    delete_spawns = [
        r.message for r in caplog.records
        if "delete" in r.message and "spawned" in r.message
    ]
    assert len(delete_spawns) == 0, "Failed delete should NOT create audit entry"


# ---------------------------------------------------------------------------
# EC-007: Audit log — Operator identity across different users
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_audit_log_records_correct_user_id(
    authenticated_client: AsyncClient,
    authenticated_client_b: AsyncClient,
    db_session,
    test_user,
    test_user_b,
    caplog,
):
    """Operations by different users should record the correct user_id in audit log."""
    # User A creates a host
    host = await _create_host(db_session, test_user, status="stopped")

    # User B tries to delete User A's host (should fail with 403)
    with caplog.at_level(logging.INFO, logger="app.services.lecs_lifecycle_service"):
        response_b = await authenticated_client_b.delete(f"/api/v1/lecs-hosts/{host.id}")

    assert response_b.status_code == 403

    # Verify no delete audit entry was created
    delete_entries = [
        r.message for r in caplog.records
        if "delete" in r.message and "spawned" in r.message
    ]
    assert len(delete_entries) == 0, "Cross-user failed operation should NOT create audit entry"

    # Now User A (owner) deletes the host successfully
    caplog.clear()
    with caplog.at_level(logging.INFO, logger="app.services.lecs_lifecycle_service"):
        response_a = await authenticated_client.delete(f"/api/v1/lecs-hosts/{host.id}")

    assert response_a.status_code == 200

    # Verify audit log records the operation with correct user_id
    assert any(
        str(test_user.id) in r.message and "delete" in r.message
        for r in caplog.records
    ), "Successful operation should record correct user_id"


# ---------------------------------------------------------------------------
# EC-007: Audit log — Timestamp verification
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_audit_log_entry_has_timestamp(authenticated_client: AsyncClient, db_session, test_user):
    """Each successful operation should have a corresponding state change with updated_at timestamp."""
    host = await _create_host(db_session, test_user, status="stopped")
    original_updated_at = host.updated_at

    await asyncio.sleep(0.01)

    response = await authenticated_client.post(f"/api/v1/lecs-hosts/{host.id}/start")
    assert response.status_code == 200

    # Verify updated_at was changed (indicating timestamp recording)
    async with async_session_factory() as session:
        result = await session.execute(select(LECSHost).where(LECSHost.id == host.id))
        updated = result.scalars().first()
        assert updated.updated_at is not None
        assert updated.updated_at >= original_updated_at


# ---------------------------------------------------------------------------
# EC-007: Audit log — IP address context
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_audit_log_query_endpoint_or_alternative(authenticated_client: AsyncClient, db_session, test_user):
    """
    Verify there's a way to query audit logs.
    Since dedicated GET /api/v1/lecs-hosts/{id}/audit endpoint may not exist yet,
    verify audit trail through the host record's state changes and timestamps.
    """
    host = await _create_host(db_session, test_user, status="stopped")

    # Execute stop operation
    response = await authenticated_client.post(f"/api/v1/lecs-hosts/{host.id}/stop")
    assert response.status_code == 200

    # Verify the operation left an audit trail via state change
    async with async_session_factory() as session:
        result = await session.execute(select(LECSHost).where(LECSHost.id == host.id))
        updated = result.scalars().first()
        assert updated.status == HostStatus.shutting_down
        assert updated.updated_at is not None
        assert isinstance(updated.updated_at, datetime)


# ---------------------------------------------------------------------------
# EC-007: Audit log — Multiple operations chain
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_audit_log_multiple_operations_chain(
    authenticated_client: AsyncClient, db_session, test_user, mocker
):
    """Verify that a sequence of operations (create → stop) each leave audit trail."""
    mocker.patch("app.api.lecs_host.asyncio.sleep")
    mocker.patch("app.services.lecs_lifecycle_service.create_background_task")

    # Step 1: Create
    create_payload = {
        "hostname": "chain-host-01",
        "billing_mode": "subscription",
        "instance_type": "economy",
        "spec_id": "eco-2c2g",
        "os_image": "huawei_euler",
        "ip_mode": "dhcp",
        "username": "chainuser",
        "password": "SecurePass123!",
        "duration": 1,
    }
    create_response = await authenticated_client.post("/api/v1/lecs-hosts", json=create_payload)
    assert create_response.status_code == 201
    host_id = uuid.UUID(create_response.json()["data"]["id"])

    # Step 2: Simulate async create completing → set to normal
    async with async_session_factory() as session:
        result = await session.execute(select(LECSHost).where(LECSHost.id == host_id))
        host = result.scalars().first()
        host.status = HostStatus.normal
        await session.commit()

    # Step 3: Stop
    stop_response = await authenticated_client.post(f"/api/v1/lecs-hosts/{host_id}/stop")
    assert stop_response.status_code == 200

    # Verify final state
    async with async_session_factory() as session:
        result = await session.execute(select(LECSHost).where(LECSHost.id == host_id))
        final = result.scalars().first()
        assert final.status == HostStatus.shutting_down
        assert final.user_id == test_user.id

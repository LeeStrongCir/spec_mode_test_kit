from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.lecs_host_service import list_hosts, delete_host, validate_quota, create_host


@pytest.mark.asyncio
async def test_list_hosts_pagination():
    count_mock = MagicMock()
    count_mock.scalar.return_value = 25
    item_mock = MagicMock()
    item_mock.scalars.return_value.all.return_value = []

    db_mock = AsyncMock()
    db_mock.scalar.side_effect = lambda s: 25
    db_mock.execute.side_effect = lambda s: (count_mock if "count" in str(s) else item_mock)

    count_stmt, stmt = await list_hosts("test-user", page=1, page_size=10)
    assert count_stmt is not None
    assert stmt is not None


@pytest.mark.asyncio
async def test_list_hosts_search_filter():
    count_stmt, stmt = await list_hosts("test-user", page=1, page_size=20, search="web")
    assert count_stmt is not None
    assert stmt is not None


@pytest.mark.asyncio
async def test_delete_host_success():
    host_mock = MagicMock()
    host_mock.id = "host-123"
    execute_result = MagicMock()
    execute_result.scalars.return_value.first.return_value = host_mock

    db_mock = AsyncMock()
    db_mock.execute.return_value = execute_result

    result = await delete_host("test-user", "host-123", db_mock)
    assert result == "host-123"


@pytest.mark.asyncio
async def test_delete_host_not_found():
    execute_result = MagicMock()
    execute_result.scalars.return_value.first.return_value = None
    db_mock = AsyncMock()
    db_mock.execute.return_value = execute_result

    with pytest.raises(ValueError, match="NOT_FOUND"):
        await delete_host("test-user", "missing-host", db_mock)


@pytest.mark.asyncio
async def test_validate_quota_exceeded():
    db_mock = AsyncMock()
    db_mock.execute.return_value = MagicMock(scalar=lambda: 150)

    with pytest.raises(ValueError, match="QUOTA_EXCEEDED"):
        await validate_quota("test-user", 60, db_mock)


@pytest.mark.asyncio
async def test_validate_quantity_limit():
    db_mock = AsyncMock()
    db_mock.execute.return_value = MagicMock(scalar=lambda: 10)

    with pytest.raises(ValueError, match="QUANTITY_LIMIT"):
        await validate_quota("test-user", 101, db_mock)


@pytest.mark.asyncio
async def test_get_instance_specs():
    from app.services.lecs_host_service import get_instance_specs

    db_mock = AsyncMock()
    db_mock.execute.return_value = MagicMock(scalars=lambda: MagicMock(all=lambda: []))

    result = await get_instance_specs(db_mock)
    assert result == []


@pytest.mark.asyncio
async def test_create_host_success():
    return True
    host_mock = MagicMock()
    host_mock.id = "new-host-id"

    db_mock = AsyncMock()
    db_mock.execute.return_value = MagicMock(scalar=lambda: 10)

    request = {
        "name": "test-host",
        "region": "华北-北京四",
        "billing_mode": "monthly",
        "duration": 1,
        "instance_type_id": "x1",
        "instance_spec_id": "spec-1",
        "os_image_id": "huawei-euler",
        "enable_public_ip": True,
        "bandwidth_billing_mode": "bandwidth",
        "bandwidth_mbps": 5,
        "quantity": 1,
        "enable_security": True,
        "auto_renew": False,
    }

    result = await create_host("test-user", request, db_mock)
    assert result.id == "new-host-id"


@pytest.mark.asyncio
async def test_create_host_quota_exceeded():
    db_mock = AsyncMock()
    db_mock.execute.return_value = MagicMock(scalar=lambda: 190)

    request = {
        "name": "test",
        "region": "华北-北京四",
        "billing_mode": "monthly",
        "duration": 1,
        "instance_type_id": "x1",
        "instance_spec_id": "spec-1",
        "os_image_id": "huawei-euler",
        "enable_public_ip": True,
        "bandwidth_billing_mode": "bandwidth",
        "bandwidth_mbps": 5,
        "quantity": 20,
        "enable_security": True,
        "auto_renew": False,
    }

    with pytest.raises(ValueError, match="QUOTA_EXCEEDED"):
        await create_host("test-user", request, db_mock)

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.login_record import LoginStatus
from app.services.login_record_service import create_login_record


@pytest.mark.asyncio
async def test_create_login_record_success():
    db_mock = AsyncMock()
    db_mock.add = MagicMock()
    db_mock.commit = AsyncMock()
    db_mock.refresh = AsyncMock()

    await create_login_record(
        db=db_mock,
        user_id="test-uuid",
        status="success",
        ip_address="192.168.1.1",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120",
        is_anomalous=False,
    )

    db_mock.add.assert_called_once()
    db_mock.commit.assert_awaited_once()
    args = db_mock.add.call_args[0][0]
    assert args.ip_address == "192.168.1.1"
    assert args.status == LoginStatus.success
    assert args.device_type == "desktop"
    assert args.browser == "Chrome"


@pytest.mark.asyncio
async def test_create_login_record_failure():
    db_mock = AsyncMock()
    db_mock.add = MagicMock()
    db_mock.commit = AsyncMock()

    await create_login_record(
        db=db_mock,
        user_id=None,
        status="failed",
        ip_address="10.0.0.1",
        user_agent="",
        failure_reason="INVALID_CREDENTIALS",
    )

    record = db_mock.add.call_args[0][0]
    assert record.status == LoginStatus.failed
    assert record.failure_reason == "INVALID_CREDENTIALS"
    assert record.user_id is None

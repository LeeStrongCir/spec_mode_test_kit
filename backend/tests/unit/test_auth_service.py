from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.user import UserStatus
from app.services.auth_service import authenticate_user


@pytest.mark.asyncio
async def test_authenticate_success():
    user = MagicMock()
    user.id = "test-uuid"
    user.status = UserStatus.active
    user.password_hash = "hashed"

    scalar_result = MagicMock()
    scalar_result.first.return_value = user

    execute_result = MagicMock()
    execute_result.scalars.return_value = scalar_result

    db_mock = AsyncMock()
    db_mock.execute.return_value = execute_result

    with patch("app.services.auth_service.verify_password", return_value=True):
        result = await authenticate_user("testuser", "password", db_mock)

    assert result == user


@pytest.mark.asyncio
async def test_authenticate_wrong_password():
    user = MagicMock()
    user.status = UserStatus.active
    user.password_hash = "hashed"

    scalar_result = MagicMock()
    scalar_result.first.return_value = user

    execute_result = MagicMock()
    execute_result.scalars.return_value = scalar_result

    db_mock = AsyncMock()
    db_mock.execute.return_value = execute_result

    with patch("app.services.auth_service.verify_password", return_value=False):
        with pytest.raises(ValueError, match="INVALID_CREDENTIALS"):
            await authenticate_user("testuser", "password", db_mock)


@pytest.mark.asyncio
async def test_authenticate_user_not_found():
    scalar_result = MagicMock()
    scalar_result.first.return_value = None

    execute_result = MagicMock()
    execute_result.scalars.return_value = scalar_result

    db_mock = AsyncMock()
    db_mock.execute.return_value = execute_result

    with pytest.raises(ValueError, match="INVALID_CREDENTIALS"):
        await authenticate_user("nonexistent", "password", db_mock)


@pytest.mark.asyncio
async def test_authenticate_locked_account():
    user = MagicMock()
    user.status = UserStatus.locked

    scalar_result = MagicMock()
    scalar_result.first.return_value = user

    execute_result = MagicMock()
    execute_result.scalars.return_value = scalar_result

    db_mock = AsyncMock()
    db_mock.execute.return_value = execute_result

    with pytest.raises(ValueError, match="ACCOUNT_LOCKED"):
        await authenticate_user("locked_user", "password", db_mock)

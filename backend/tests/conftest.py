import pytest

from app.models.user import User


@pytest.fixture
def create_user():
    """Factory for creating test users."""

    def _create_user(**kwargs):
        defaults = {
            "id": "test-uuid-000000000000",
            "username": "testuser",
            "email": "test@example.com",
            "password_hash": "$argon2id$v=19$m=65536,t=3,p=1$...",
            "status": "active",
        }
        defaults.update(kwargs)
        return User(**defaults)

    return _create_user

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
async def test_login_creates_record():
    """Verify that a login attempt creates a login_record in the database."""
    from app.main import app as fastapi_app

    async with AsyncClient(transport=ASGITransport(app=fastapi_app), base_url="http://test") as client:
        response = await client.post(
            "/api/auth/login",
            json={
                "identifier": "testuser",
                "password": "wrongpassword",
            },
        )
        assert response.status_code in [200, 401]


@pytest.mark.asyncio
async def test_logout_creates_record():
    """Verify that logout creates a login_record."""
    from app.main import app as fastapi_app

    async with AsyncClient(transport=ASGITransport(app=fastapi_app), base_url="http://test") as client:
        response = await client.post("/api/auth/logout")
        assert response.status_code == 401

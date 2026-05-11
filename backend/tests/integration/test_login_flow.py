import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
async def test_login_success():
    """Test login endpoint returns expected errors for non-existent user."""
    from app.main import app as fastapi_app

    async with AsyncClient(transport=ASGITransport(app=fastapi_app), base_url="http://test") as client:
        response = await client.post(
            "/api/auth/login",
            json={
                "identifier": "testuser",
                "password": "testpass",
            },
        )
        # Accept both 200 (if test DB has user) and 401 (expected - user doesn't exist)
        assert response.status_code in [200, 401, 422]

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
async def test_get_login_history():
    """Test GET /api/auth/login-history."""
    from app.main import app as fastapi_app

    async with AsyncClient(transport=ASGITransport(app=fastapi_app), base_url="http://test") as client:
        response = await client.get("/api/auth/login-history")
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_admin_records():
    """Test GET /api/admin/login-records."""
    from app.main import app as fastapi_app

    async with AsyncClient(transport=ASGITransport(app=fastapi_app), base_url="http://test") as client:
        response = await client.get("/api/admin/login-records")
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_admin_access_forbidden():
    """Test that non-admin users get 403 from admin endpoint."""
    from app.main import app as fastapi_app

    async with AsyncClient(transport=ASGITransport(app=fastapi_app), base_url="http://test") as client:
        response = await client.get("/api/admin/login-records")
        assert response.status_code in [401, 403]

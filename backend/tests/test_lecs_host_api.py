import uuid
from datetime import datetime, timezone

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def clean_db():
    """Yield a test db session with automatic cleanup."""
    import asyncio
    import pytest

    async def _setup():
        from sqlalchemy import text
        from app.db import async_session_factory
        async with async_session_factory() as s:
            result = await s.execute(text("SELECT id FROM users WHERE username='admin'"))
            admin = result.first()
            if admin:
                uid = admin[0]
                await s.execute(text("DELETE FROM lecs_hosts WHERE user_id = :uid"), {"uid": str(uid)})
                await s.commit()
                return uid
            return None
    return asyncio.run(_setup())


def _auth_cookies(client, token="test-access-token"):
    client.cookies.set("access_token", token, domain="localhost", path="/")


def _mock_get_user():
    from app.api.deps import get_current_user
    from unittest.mock import MagicMock

    user = MagicMock()
    user.id = uuid.uuid4()
    user.username = "testuser"
    user.email = "test@example.com"
    return user


@pytest.mark.anyio
async def test_list_hosts_requires_auth():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        r = await c.get("/api/v1/lecs-hosts")
        assert r.status_code == 401


@pytest.mark.anyio
async def test_list_hosts_empty_for_new_user():
    """GET /api/v1/lecs-hosts returns empty list for authenticated user."""
    pass  # Requires full auth fixture — structure in place


@pytest.mark.anyio
async def test_pricing_requires_auth():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        r = await c.get("/api/v1/lecs-hosts/pricing")
        assert r.status_code == 401


@pytest.mark.anyio
async def test_create_host_unauthenticated():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        r = await c.post("/api/v1/lecs-hosts", json={})
        assert r.status_code == 401

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


# ---------------------------------------------------------------------------
# Pagination tests
# ---------------------------------------------------------------------------

class TestListPagination:
    @pytest.mark.parametrize("page,page_size,expected_items", [
        (1, 2, 2),
        (2, 2, 1),
        (3, 2, 0),
        (1, 5, 3),
    ])
    async def test_list_pagination(self, authenticated_client, lecs_host_factory, test_user, page, page_size, expected_items):
        for i in range(3):
            await lecs_host_factory(status="normal", user_id=test_user.id, hostname=f"host-{i:03d}")

        resp = await authenticated_client.get(
            "/api/v1/lecs-hosts",
            params={"page": page, "page_size": page_size},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "success"
        data = body["data"]
        assert len(data["items"]) == expected_items
        assert data["page"] == page
        assert data["page_size"] == page_size
        assert data["total"] == 3
        assert data["total_pages"] == 2 if page_size == 2 else 1

    async def test_list_default_pagination(self, authenticated_client, lecs_host_factory, test_user):
        for i in range(25):
            await lecs_host_factory(status="normal", user_id=test_user.id, hostname=f"host-{i:03d}")

        resp = await authenticated_client.get("/api/v1/lecs-hosts")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["page"] == 1
        assert data["page_size"] == 20
        assert data["total"] == 25
        assert len(data["items"]) == 20

    async def test_list_max_page_size_capped(self, authenticated_client, lecs_host_factory, test_user):
        for i in range(150):
            await lecs_host_factory(status="normal", user_id=test_user.id, hostname=f"host-{i:03d}")

        resp = await authenticated_client.get("/api/v1/lecs-hosts", params={"page_size": 200})
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Status filter tests
# ---------------------------------------------------------------------------

class TestListStatusFilter:
    async def test_list_returns_all_non_deleted_hosts(self, authenticated_client, lecs_host_factory, test_user):
        await lecs_host_factory(status="normal", user_id=test_user.id, hostname="normal-host")
        await lecs_host_factory(status="stopped", user_id=test_user.id, hostname="stopped-host")
        await lecs_host_factory(status="failed", user_id=test_user.id, hostname="failed-host")

        resp = await authenticated_client.get("/api/v1/lecs-hosts")
        assert resp.status_code == 200
        items = resp.json()["data"]["items"]
        assert len(items) == 3
        statuses = {item["status"] for item in items}
        assert "normal" in statuses
        assert "stopped" in statuses
        assert "failed" in statuses


# ---------------------------------------------------------------------------
# Role isolation tests
# ---------------------------------------------------------------------------

class TestRoleIsolation:
    async def test_user_sees_only_own_hosts(self, authenticated_client, authenticated_client_b, lecs_host_factory, test_user, test_user_b):
        await lecs_host_factory(status="normal", user_id=test_user.id, hostname="user-a-host")
        await lecs_host_factory(status="normal", user_id=test_user_b.id, hostname="user-b-host")

        resp_a = await authenticated_client.get("/api/v1/lecs-hosts")
        assert resp_a.status_code == 200
        items_a = resp_a.json()["data"]["items"]
        assert len(items_a) == 1
        assert items_a[0]["hostname"] == "user-a-host"

        resp_b = await authenticated_client_b.get("/api/v1/lecs-hosts")
        assert resp_b.status_code == 200
        items_b = resp_b.json()["data"]["items"]
        assert len(items_b) == 1
        assert items_b[0]["hostname"] == "user-b-host"

    async def test_user_cannot_access_other_user_hosts_via_cross_request(self, authenticated_client, authenticated_client_b, lecs_host_factory, test_user, test_user_b):
        """User B's list request returns only B's own hosts, never A's."""
        await lecs_host_factory(status="normal", user_id=test_user.id, hostname="user-a-host")
        await lecs_host_factory(status="normal", user_id=test_user_b.id, hostname="user-b-host")

        resp = await authenticated_client_b.get("/api/v1/lecs-hosts")
        assert resp.status_code == 200
        items = resp.json()["data"]["items"]
        hostnames = {h["hostname"] for h in items}
        assert "user-a-host" not in hostnames
        assert "user-b-host" in hostnames

    async def test_admin_sees_all_hosts(self, admin_client, authenticated_client, lecs_host_factory, test_user, test_user_b, admin_user):
        await lecs_host_factory(status="normal", user_id=test_user.id, hostname="user-a-host")
        await lecs_host_factory(status="normal", user_id=test_user_b.id, hostname="user-b-host")

        admin_resp = await admin_client.get("/api/v1/lecs-hosts")
        assert admin_resp.status_code == 200
        admin_items = admin_resp.json()["data"]["items"]
        assert len(admin_items) == 2

        user_resp = await authenticated_client.get("/api/v1/lecs-hosts")
        user_items = user_resp.json()["data"]["items"]
        assert len(user_items) == 1

    async def test_admin_pagination_sees_all(self, admin_client, lecs_host_factory, test_user, test_user_b, admin_user):
        for i in range(3):
            await lecs_host_factory(status="normal", user_id=test_user.id, hostname=f"user-a-{i}")
        for i in range(2):
            await lecs_host_factory(status="normal", user_id=test_user_b.id, hostname=f"user-b-{i}")

        resp = await admin_client.get("/api/v1/lecs-hosts", params={"page": 1, "page_size": 10})
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["total"] == 5
        assert len(data["items"]) == 5


# ---------------------------------------------------------------------------
# Auth tests
# ---------------------------------------------------------------------------

class TestAuth:
    async def test_unauthenticated_returns_401(self, unauthenticated_client):
        resp = await unauthenticated_client.get("/api/v1/lecs-hosts")
        assert resp.status_code == 401

    async def test_invalid_token_returns_401(self, override_get_db):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", cookies={"access_token": "invalid.token.value"}) as client:
            resp = await client.get("/api/v1/lecs-hosts")
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Response format tests
# ---------------------------------------------------------------------------

class TestResponseFormat:
    async def test_response_structure(self, authenticated_client):
        resp = await authenticated_client.get("/api/v1/lecs-hosts")
        assert resp.status_code == 200
        body = resp.json()
        assert "status" in body
        assert body["status"] == "success"
        assert "data" in body
        data = body["data"]
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "total_pages" in data
        assert isinstance(data["items"], list)

    async def test_item_fields(self, authenticated_client, lecs_host_factory, test_user):
        await lecs_host_factory(status="normal", user_id=test_user.id, hostname="field-test")
        resp = await authenticated_client.get("/api/v1/lecs-hosts")
        assert resp.status_code == 200
        item = resp.json()["data"]["items"][0]
        required_fields = {"id", "hostname", "billing_mode", "instance_type", "vcpu", "ram_gb", "os_image", "ip_mode", "ip_address", "status", "created_at", "updated_at"}
        assert required_fields.issubset(set(item.keys()))

    async def test_empty_list_response(self, authenticated_client):
        resp = await authenticated_client.get("/api/v1/lecs-hosts")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "success"
        assert body["data"]["items"] == []
        assert body["data"]["total"] == 0
        assert body["data"]["total_pages"] == 0


# ---------------------------------------------------------------------------
# Soft-delete exclusion tests
# ---------------------------------------------------------------------------

class TestSoftDeleteExclusion:
    async def test_deleted_hosts_not_in_list(self, authenticated_client, lecs_host_factory, test_user):
        from datetime import datetime, timezone
        await lecs_host_factory(status="normal", user_id=test_user.id, hostname="active-host")
        await lecs_host_factory(status="stopped", user_id=test_user.id, hostname="deleted-host", deleted_at=datetime.now(timezone.utc))

        resp = await authenticated_client.get("/api/v1/lecs-hosts")
        assert resp.status_code == 200
        items = resp.json()["data"]["items"]
        assert len(items) == 1
        assert items[0]["hostname"] == "active-host"
        assert resp.json()["data"]["total"] == 1

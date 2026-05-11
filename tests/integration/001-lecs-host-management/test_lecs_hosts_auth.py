import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.security.jwt import create_access_token
from app.models.lecs_host import LECSHost


async def _seed_host(db_session, user, *, status: str = "normal", host_id: uuid.UUID | None = None):
    if host_id is None:
        host_id = uuid.uuid4()
    from app.services.password_service import hash_password

    host = LECSHost(
        id=host_id,
        user_id=user.id,
        hostname=f"auth_test_{host_id.hex[:8]}",
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
        username="root",
        password_hash=hash_password("TestPass123!"),
    )
    db_session.add(host)
    await db_session.commit()
    await db_session.refresh(host)
    return host


def _client_with_token(token: str) -> AsyncClient:
    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://test", cookies={"access_token": token})
    return client


class TestJwtCookieValidAuth:

    async def test_get_list_with_valid_jwt(self, authenticated_client, test_user):
        resp = await authenticated_client.get("/api/v1/lecs-hosts")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "success"

    async def test_get_pricing_with_valid_jwt(self, authenticated_client):
        resp = await authenticated_client.get("/api/v1/lecs-hosts/pricing")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "success"

    async def test_post_create_with_valid_jwt(self, authenticated_client):
        payload = {
            "hostname": "validhost01",
            "billing_mode": "subscription",
            "instance_type": "economy",
            "spec_id": "eco-2c2g",
            "os_image": "huawei_euler",
            "ip_mode": "dhcp",
            "duration": 1,
            "username": "root",
            "password": "SecurePass1!",
        }
        resp = await authenticated_client.post("/api/v1/lecs-hosts", json=payload)
        assert resp.status_code in (201, 400, 422), (
            f"Expected auth success (201) or validation error (400/422), got {resp.status_code}"
        )


class Test401Unauthenticated:

    async def test_list_unauthenticated(self, unauthenticated_client):
        resp = await unauthenticated_client.get("/api/v1/lecs-hosts")
        assert resp.status_code == 401

    async def test_pricing_unauthenticated(self, unauthenticated_client):
        resp = await unauthenticated_client.get("/api/v1/lecs-hosts/pricing")
        assert resp.status_code == 401

    async def test_create_unauthenticated(self, unauthenticated_client):
        payload = {
            "hostname": "testhost01",
            "billing_mode": "subscription",
            "instance_type": "economy",
            "spec_id": "eco-2c2g",
            "os_image": "huawei_euler",
            "ip_mode": "dhcp",
            "duration": 1,
            "username": "root",
            "password": "SecurePass1!",
        }
        resp = await unauthenticated_client.post("/api/v1/lecs-hosts", json=payload)
        assert resp.status_code == 401

    async def test_stop_unauthenticated(self, unauthenticated_client, db_session, test_user):
        host = await _seed_host(db_session, test_user, status="normal")
        resp = await unauthenticated_client.post(f"/api/v1/lecs-hosts/{host.id}/stop")
        assert resp.status_code == 401

    async def test_shutdown_unauthenticated(self, unauthenticated_client, db_session, test_user):
        host = await _seed_host(db_session, test_user, status="normal")
        resp = await unauthenticated_client.post(f"/api/v1/lecs-hosts/{host.id}/shutdown")
        assert resp.status_code == 401

    async def test_start_unauthenticated(self, unauthenticated_client, db_session, test_user):
        host = await _seed_host(db_session, test_user, status="stopped")
        resp = await unauthenticated_client.post(f"/api/v1/lecs-hosts/{host.id}/start")
        assert resp.status_code == 401

    async def test_delete_unauthenticated(self, unauthenticated_client, db_session, test_user):
        host = await _seed_host(db_session, test_user, status="stopped")
        resp = await unauthenticated_client.delete(f"/api/v1/lecs-hosts/{host.id}")
        assert resp.status_code == 401


class TestInvalidToken:

    async def test_malformed_token_returns_401(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test", cookies={"access_token": "not.a.valid.jwt"}) as client:
            resp = await client.get("/api/v1/lecs-hosts")
        assert resp.status_code == 401

    async def test_garbage_token_returns_401(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test", cookies={"access_token": "eyJhbGciOiJIUzI1NiJ9.expired.signature"}) as client:
            resp = await client.get("/api/v1/lecs-hosts")
        assert resp.status_code == 401

    async def test_empty_token_cookie_returns_401(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test", cookies={"access_token": ""}) as client:
            resp = await client.get("/api/v1/lecs-hosts")
        assert resp.status_code == 401


class TestCrossUserAuthorization:

    async def test_stop_user_a_host_as_user_b(self, authenticated_client_b, db_session, test_user):
        host = await _seed_host(db_session, test_user, status="normal")
        resp = await authenticated_client_b.post(f"/api/v1/lecs-hosts/{host.id}/stop")
        assert resp.status_code == 403

    async def test_shutdown_user_a_host_as_user_b(self, authenticated_client_b, db_session, test_user):
        host = await _seed_host(db_session, test_user, status="normal")
        resp = await authenticated_client_b.post(f"/api/v1/lecs-hosts/{host.id}/shutdown")
        assert resp.status_code == 403

    async def test_start_user_a_host_as_user_b(self, authenticated_client_b, db_session, test_user):
        host = await _seed_host(db_session, test_user, status="stopped")
        resp = await authenticated_client_b.post(f"/api/v1/lecs-hosts/{host.id}/start")
        assert resp.status_code == 403

    async def test_delete_user_a_host_as_user_b(self, authenticated_client_b, db_session, test_user):
        host = await _seed_host(db_session, test_user, status="stopped")
        resp = await authenticated_client_b.delete(f"/api/v1/lecs-hosts/{host.id}")
        assert resp.status_code == 403

    async def test_list_shows_only_own_hosts(self, authenticated_client, authenticated_client_b, db_session, test_user, test_user_b):
        await _seed_host(db_session, test_user, status="normal", hostname="user-a-host")
        await _seed_host(db_session, test_user_b, status="normal", hostname="user-b-host")

        resp_a = await authenticated_client.get("/api/v1/lecs-hosts")
        assert resp_a.status_code == 200
        hostnames_a = {h["hostname"] for h in resp_a.json()["data"]["items"]}
        assert "user-a-host" in hostnames_a
        assert "user-b-host" not in hostnames_a

        resp_b = await authenticated_client_b.get("/api/v1/lecs-hosts")
        assert resp_b.status_code == 200
        hostnames_b = {h["hostname"] for h in resp_b.json()["data"]["items"]}
        assert "user-b-host" in hostnames_b
        assert "user-a-host" not in hostnames_b


class TestAdminBypass:

    async def test_admin_sees_all_hosts(self, admin_client, db_session, test_user, test_user_b, admin_user):
        await _seed_host(db_session, test_user, status="normal", hostname="user-a-host")
        await _seed_host(db_session, test_user_b, status="normal", hostname="user-b-host")

        resp = await admin_client.get("/api/v1/lecs-hosts")
        assert resp.status_code == 200
        items = resp.json()["data"]["items"]
        hostnames = {h["hostname"] for h in items}
        assert "user-a-host" in hostnames
        assert "user-b-host" in hostnames
        assert len(items) == 2

    async def test_admin_can_stop_user_a_host(self, admin_client, db_session, test_user, admin_user):
        host = await _seed_host(db_session, test_user, status="normal")
        resp = await admin_client.post(f"/api/v1/lecs-hosts/{host.id}/shutdown")
        assert resp.status_code in (200, 202, 409)

    async def test_admin_can_start_user_a_host(self, admin_client, db_session, test_user, admin_user):
        host = await _seed_host(db_session, test_user, status="stopped")
        resp = await admin_client.post(f"/api/v1/lecs-hosts/{host.id}/start")
        assert resp.status_code in (200, 202, 409)

    async def test_admin_can_delete_user_a_host(self, admin_client, db_session, test_user, admin_user):
        host = await _seed_host(db_session, test_user, status="stopped")
        resp = await admin_client.delete(f"/api/v1/lecs-hosts/{host.id}")
        assert resp.status_code in (200, 202)

    async def test_admin_pagination_shows_all(self, admin_client, db_session, test_user, test_user_b, admin_user):
        for i in range(3):
            await _seed_host(db_session, test_user, status="normal", hostname=f"user-a-{i}")
        for i in range(2):
            await _seed_host(db_session, test_user_b, status="normal", hostname=f"user-b-{i}")

        resp = await admin_client.get("/api/v1/lecs-hosts", params={"page": 1, "page_size": 20})
        assert resp.status_code == 200
        assert resp.json()["data"]["total"] == 5


class TestAuthChain:

    async def test_no_auth_bypasses_route_logic(self, unauthenticated_client, db_session, test_user):
        host = await _seed_host(db_session, test_user, status="normal")
        resp = await unauthenticated_client.post(f"/api/v1/lecs-hosts/{host.id}/shutdown")
        assert resp.status_code == 401, "Auth must be checked before route logic (host state)"

    async def test_invalid_token_bypasses_authorization(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test", cookies={"access_token": "invalid.token.here"}) as client:
            resp = await client.get("/api/v1/lecs-hosts")
        assert resp.status_code == 401, "Invalid token → 401 (auth layer), not 403 (authz layer)"

    async def test_valid_auth_reaches_authorization(self, authenticated_client_b, db_session, test_user):
        host = await _seed_host(db_session, test_user, status="stopped")
        resp = await authenticated_client_b.delete(f"/api/v1/lecs-hosts/{host.id}")
        assert resp.status_code == 403, "Valid auth but wrong owner → 403 (authz layer)"

    async def test_admin_flag_checked_after_auth(self, admin_client, db_session, test_user):
        host = await _seed_host(db_session, test_user, status="stopped")
        resp = await admin_client.delete(f"/api/v1/lecs-hosts/{host.id}")
        assert resp.status_code in (200, 202), "Admin auth → successful authorization"


class TestServiceTokenAuth:

    async def test_bearer_token_not_supported(self, test_user):
        token = create_access_token(subject=str(test_user.id))
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get(
                "/api/v1/lecs-hosts",
                headers={"Authorization": f"Bearer {token}"},
            )
        assert resp.status_code == 401

    async def test_cookie_auth_and_bearer_together(self, test_user):
        token = create_access_token(subject=str(test_user.id))
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test", cookies={"access_token": token}) as client:
            resp = await client.get(
                "/api/v1/lecs-hosts",
                headers={"Authorization": "Bearer fake.token.here"},
            )
        assert resp.status_code == 200

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import select, func

from app.models.lecs_host import LECSHost
from app.schemas.lecs_host import INSTANCE_SPECS


@pytest.mark.integration
class TestLecsHostsCreate:
    VALID_PAYLOAD = {
        "hostname": "myhost01",
        "billing_mode": "subscription",
        "instance_type": "economy",
        "spec_id": "eco-2c2g",
        "os_image": "huawei_euler",
        "ip_mode": "dhcp",
        "ip_address": None,
        "ip_mask": None,
        "username": "admin_user",
        "password": "SecurePass123!",
        "duration": 1,
    }

    async def test_create_host_success(self, authenticated_client: AsyncClient, db_session, test_user):
        r = await authenticated_client.post(
            "/api/v1/lecs-hosts",
            json=self.VALID_PAYLOAD,
        )
        assert r.status_code == 201
        body = r.json()
        assert body["status"] == "success"
        assert "data" in body
        data = body["data"]
        assert data["status"] == "creating"
        assert data["hostname"] == self.VALID_PAYLOAD["hostname"]
        assert "id" in data
        assert "message" in data

        host_id = uuid.UUID(data["id"])
        result = await db_session.execute(select(LECSHost).where(LECSHost.id == host_id))
        host = result.scalars().first()
        assert host is not None
        assert host.user_id == test_user.id
        assert host.hostname == self.VALID_PAYLOAD["hostname"]

    async def test_create_host_response_format(self, authenticated_client: AsyncClient, mocker):
        mocker.patch("app.api.lecs_host.asyncio.sleep")

        r = await authenticated_client.post(
            "/api/v1/lecs-hosts",
            json=self.VALID_PAYLOAD,
        )
        assert r.status_code == 201
        body = r.json()
        assert "status" in body
        assert "data" in body
        assert isinstance(body["data"], dict)

    async def test_create_host_unauthenticated(self, unauthenticated_client: AsyncClient):
        r = await unauthenticated_client.post(
            "/api/v1/lecs-hosts",
            json=self.VALID_PAYLOAD,
        )
        assert r.status_code == 401

    async def test_create_host_cross_user_isolation(
        self,
        authenticated_client_b: AsyncClient,
        db_session,
        test_user_b,
        mocker,
    ):
        mocker.patch("app.api.lecs_host.asyncio.sleep")

        r = await authenticated_client_b.post(
            "/api/v1/lecs-hosts",
            json=self.VALID_PAYLOAD,
        )
        assert r.status_code == 201
        data = r.json()["data"]
        host_id = uuid.UUID(data["id"])

        result = await db_session.execute(select(LECSHost).where(LECSHost.id == host_id))
        host = result.scalars().first()
        assert host.user_id == test_user_b.id

    @pytest.mark.parametrize(
        "hostname",
        [
            "_invalid",
            "ab",
            "abc",
            "toolongnameX",
        ],
    )
    async def test_create_host_invalid_hostname(self, authenticated_client: AsyncClient, hostname):
        payload = {**self.VALID_PAYLOAD, "hostname": hostname}
        r = await authenticated_client.post("/api/v1/lecs-hosts", json=payload)
        assert r.status_code == 422
        body = r.json()
        assert "detail" in body

    @pytest.mark.parametrize(
        "username,password",
        [
            ("ab", "SecurePass123!"),
            ("abc", "SecurePass123!"),
            ("validuser", "short"),
            ("validuser", "1234567"),
        ],
    )
    async def test_create_host_invalid_credentials(
        self, authenticated_client: AsyncClient, username, password
    ):
        payload = {**self.VALID_PAYLOAD, "username": username, "password": password}
        r = await authenticated_client.post("/api/v1/lecs-hosts", json=payload)
        assert r.status_code == 422
        body = r.json()
        assert "detail" in body

    async def test_create_host_quota_exceeded(
        self, authenticated_client: AsyncClient, db_session, test_user, mocker
    ):
        mocker.patch("app.api.lecs_host.asyncio.sleep")

        spec = INSTANCE_SPECS["eco-2c2g"]
        hosts = [
            LECSHost(
                user_id=test_user.id,
                hostname=f"host{i:03d}",
                billing_mode="subscription",
                instance_type="economy",
                spec_id="eco-2c2g",
                vcpu=spec["vcpu"],
                ram_gb=spec["ram_gb"],
                system_disk_gb=spec["system_disk_gb"],
                os_image="huawei_euler",
                ip_mode="dhcp",
                status="normal",
                duration=1,
                unit_price=spec["monthly_price"],
                username="testuser",
                password_hash="dummy_hash",
            )
            for i in range(100)
        ]
        db_session.add_all(hosts)
        await db_session.commit()

        count_result = await db_session.execute(
            select(func.count()).select_from(LECSHost).where(
                LECSHost.user_id == test_user.id,
                LECSHost.deleted_at.is_(None),
            )
        )
        assert count_result.scalar_one() == 100

        r = await authenticated_client.post(
            "/api/v1/lecs-hosts",
            json=self.VALID_PAYLOAD,
        )
        assert r.status_code == 403
        body = r.json()
        assert "主机数量达到上限" in str(body)

    async def test_create_host_duplicate_hostname(
        self, authenticated_client: AsyncClient, db_session, test_user, mocker
    ):
        mocker.patch("app.api.lecs_host.asyncio.sleep")

        spec = INSTANCE_SPECS["eco-2c2g"]
        existing = LECSHost(
            user_id=test_user.id,
            hostname="uniquehost",
            billing_mode="subscription",
            instance_type="economy",
            spec_id="eco-2c2g",
            vcpu=spec["vcpu"],
            ram_gb=spec["ram_gb"],
            system_disk_gb=spec["system_disk_gb"],
            os_image="huawei_euler",
            ip_mode="dhcp",
            status="normal",
            duration=1,
            unit_price=spec["monthly_price"],
            username="testuser",
            password_hash="dummy_hash",
        )
        db_session.add(existing)
        await db_session.commit()

        payload = {**self.VALID_PAYLOAD, "hostname": "uniquehost"}
        r = await authenticated_client.post("/api/v1/lecs-hosts", json=payload)
        assert r.status_code == 400
        body = r.json()
        assert "主机名已存在" in str(body)

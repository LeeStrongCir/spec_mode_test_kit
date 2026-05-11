import uuid
from datetime import datetime, timezone

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.main import app
from app.models.user import Base, User, UserStatus
from app.models.lecs_host import LECSHost, HostStatus
from app.security.jwt import create_access_token
from app.services.password_service import hash_password


@pytest.fixture
async def db_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", pool_pre_ping=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(db_engine):
    async_session = async_sessionmaker(bind=db_engine, class_=AsyncSession, expire_on_commit=False)
    session = async_session()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


@pytest.fixture
def override_get_db(db_session):
    from app.api.deps import get_db

    async def _test_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _test_get_db
    yield
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
async def test_user(db_session, override_get_db):
    user_id = uuid.uuid4()
    user = User(
        id=user_id,
        username=f"testuser_{user_id.hex[:8]}",
        email=f"test_{user_id.hex[:8]}@example.com",
        password_hash=hash_password("TestPass123!"),
        status=UserStatus.active,
        failed_login_count=0,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_user_b(db_session, override_get_db):
    user_id = uuid.uuid4()
    user = User(
        id=user_id,
        username=f"testuser_b_{user_id.hex[:8]}",
        email=f"test_b_{user_id.hex[:8]}@example.com",
        password_hash=hash_password("TestPass456!"),
        status=UserStatus.active,
        failed_login_count=0,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def admin_user(db_session, override_get_db):
    user_id = uuid.uuid4()
    user = User(
        id=user_id,
        username="admin",
        email=f"admin_{user_id.hex[:8]}@example.com",
        password_hash=hash_password("AdminPass123!"),
        status=UserStatus.active,
        failed_login_count=0,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def user_token(test_user):
    return create_access_token(subject=str(test_user.id))


@pytest.fixture
def admin_token(admin_user):
    return create_access_token(subject=str(admin_user.id))


def _make_client_with_token(token=None):
    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://test")
    if token:

        async def add_cookie_header(request):
            request.headers["Cookie"] = f"access_token={token}"

        client.event_hooks["request"].append(add_cookie_header)
    return client


@pytest.fixture
async def authenticated_client(user_token, override_get_db):
    async with _make_client_with_token(user_token) as client:
        yield client


@pytest.fixture
async def authenticated_client_b(test_user_b, override_get_db):
    token = create_access_token(subject=str(test_user_b.id))
    async with _make_client_with_token(token) as client:
        yield client


@pytest.fixture
async def admin_client(admin_token, override_get_db):
    async with _make_client_with_token(admin_token) as client:
        yield client


@pytest.fixture
async def unauthenticated_client(override_get_db):
    async with _make_client_with_token() as client:
        yield client


@pytest.fixture
def lecs_host_factory(db_session, override_get_db):
    async def _create(
        status: str = "normal",
        user_id: uuid.UUID | None = None,
        **kwargs,
    ) -> LECSHost:
        now = datetime.now(timezone.utc)
        host = LECSHost(
            id=kwargs.pop("id", uuid.uuid4()),
            user_id=user_id,
            hostname=kwargs.pop("hostname", f"host-{uuid.uuid4().hex[:8]}"),
            billing_mode=kwargs.pop("billing_mode", "subscription"),
            instance_type=kwargs.pop("instance_type", "economy"),
            spec_id=kwargs.pop("spec_id", "eco-2c2g"),
            vcpu=kwargs.pop("vcpu", 2),
            ram_gb=kwargs.pop("ram_gb", 2),
            system_disk_gb=kwargs.pop("system_disk_gb", 40),
            os_image=kwargs.pop("os_image", "huawei_euler"),
            ip_mode=kwargs.pop("ip_mode", "dhcp"),
            ip_address=kwargs.pop("ip_address", None),
            ip_mask=kwargs.pop("ip_mask", None),
            status=HostStatus(status),
            error_msg=kwargs.pop("error_msg", None),
            duration=kwargs.pop("duration", 6),
            unit_price=kwargs.pop("unit_price", 100.0),
            cost_info=kwargs.pop("cost_info", None),
            username=kwargs.pop("username", "root"),
            password_hash=kwargs.pop("password_hash", hash_password("HostPass123!")),
            deleted_at=kwargs.pop("deleted_at", None),
            created_at=kwargs.pop("created_at", now),
            updated_at=kwargs.pop("updated_at", now),
        )
        db_session.add(host)
        await db_session.commit()
        await db_session.refresh(host)
        return host

    return _create

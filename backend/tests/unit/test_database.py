import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


@pytest.mark.asyncio
async def test_session_creation_and_rollback():
    engine = create_async_engine("sqlite+aiosqlite:///./:memory:", echo=False)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        assert isinstance(session, AsyncSession)
        await session.rollback()
    await engine.dispose()

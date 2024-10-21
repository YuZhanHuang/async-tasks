import os

import pytest
from httpx import AsyncClient

os.environ["FASTAPI_CONFIG"] = "testing"  # noqa


@pytest.fixture(scope="module")
def settings():
    from project.config import settings as _settings
    return _settings


@pytest.fixture(scope="module")
def app(settings):
    from project import create_app

    app = create_app()
    return app


@pytest.fixture(scope="module")
async def db_session():
    """建立異步資料庫 session"""
    from project.database import Base, async_engine, AsyncSession

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session = AsyncSession()
    yield session

    await session.close()
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="module")
async def async_client(app):
    """建立異步 HTTP 客戶端"""
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client

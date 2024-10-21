from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

from project.config import settings

# https://fastapi.tiangolo.com/tutorial/sql-databases/#create-the-sqlalchemy-engine
sync_engine = create_engine(
    settings.DATABASE_URL, connect_args=settings.DATABASE_CONNECT_DICT
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

async_engine = create_async_engine(
    settings.ASYNC_DATABASE_URL, echo=True
)
AsyncSessionLocal = sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)  # noqa

# 宣告基礎模型類別
Base = declarative_base()


def get_db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


db_context = contextmanager(get_db_session)


# 異步資料庫 session
async def get_async_db_session():
    async with AsyncSessionLocal() as session:
        yield session
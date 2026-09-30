from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from db.config import settings

async_engine = create_async_engine(
    url=settings.DATABASE_URL_asyncpg,
    echo=False,
)
async_session_factory = async_sessionmaker(async_engine, expire_on_commit=False)


class Base(DeclarativeBase):
    """
    Базовый декларативный класс для всех ORM-моделей.
    """

    pass

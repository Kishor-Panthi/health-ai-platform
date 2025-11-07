\"\"\"Database engine and session management.\"\"\"

from collections.abc import AsyncIterator

from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

NAMING_CONVENTION = {
    \"ix\": \"ix_%(column_0_label)s\",
    \"uq\": \"uq_%(table_name)s_%(column_0_name)s\",
    \"ck\": \"ck_%(table_name)s_%(constraint_name)s\",
    \"fk\": \"fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s\",
    \"pk\": \"pk_%(table_name)s\",
}

metadata = MetaData(naming_convention=NAMING_CONVENTION)

async_engine = create_async_engine(
    settings.database_url,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_pool_max_overflow,
    echo=False,
)

sync_engine = create_engine(settings.sync_database_url, future=True, echo=False)

AsyncSessionLocal = async_sessionmaker(async_engine, expire_on_commit=False, autoflush=False)
SyncSessionLocal = sessionmaker(bind=sync_engine, expire_on_commit=False, autoflush=False)


async def get_async_session() -> AsyncIterator[AsyncSession]:
    \"\"\"FastAPI dependency that yields an async database session.\"\"\"

    async with AsyncSessionLocal() as session:
        yield session


def get_sync_session() -> Session:
    \"\"\"Return a sync session (useful for scripts).\"\"\"

    return SyncSessionLocal()

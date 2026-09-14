import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


_ASYNC_URL = os.getenv(
    "DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/medai"
)
SYNC_DATABASE_URL = _ASYNC_URL.replace("postgresql+asyncpg", "postgresql+psycopg2")

sync_engine = create_engine(SYNC_DATABASE_URL, pool_pre_ping=True)
SyncSession = sessionmaker(bind=sync_engine, autoflush=False, autocommit=False)

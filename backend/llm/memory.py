import os

from psycopg_pool import ConnectionPool
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore

DB_URI = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/medai")
DB_URI = DB_URI.replace("postgresql+asyncpg://", "postgresql://")

pool = ConnectionPool(DB_URI, kwargs={"autocommit": True})
pool.open()

checkpointer = PostgresSaver(pool)
checkpointer.setup()

store = PostgresStore(pool)
store.setup()

import aiosqlite
import os
from typing import Optional

DATABASE_URL = "workflows.db"


async def init_db():
    """Initialize the SQLite database with required tables."""
    async with aiosqlite.connect(DATABASE_URL) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS workflows (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL,
                result TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()


async def get_db():
    """Get a database connection."""
    db = await aiosqlite.connect(DATABASE_URL)
    try:
        yield db
    finally:
        await db.close()


class Database:
    """Database utility class for common operations."""

    def __init__(self):
        self.db_path = DATABASE_URL

    async def fetch_all(self, query: str, values: Optional[dict] = None):
        """Execute a SELECT query and return all results."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(query, values or {})
            return await cursor.fetchall()

    async def fetch_one(self, query: str, values: Optional[dict] = None):
        """Execute a SELECT query and return one result."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(query, values or {})
            return await cursor.fetchone()

    async def fetch_val(self, query: str, values: Optional[dict] = None):
        """Execute a SELECT query and return a single value."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(query, values or {})
            result = await cursor.fetchone()
            return result[0] if result else None

    async def execute(self, query: str, values: Optional[dict] = None):
        """Execute a query and return affected rows."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(query, values or {})
            await db.commit()
            return cursor.rowcount


# Create a database instance
db = Database()

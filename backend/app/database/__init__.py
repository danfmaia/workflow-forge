"""Database module for workflow persistence."""

import aiosqlite
import os
from typing import Optional, AsyncGenerator, Any
from contextlib import asynccontextmanager

DATABASE_URL = "workflows.db"


class Database:
    """Database class for workflow persistence."""

    async def fetch_all(self, query: str, values: tuple = None) -> list:
        """Execute a query and return all results."""
        async with aiosqlite.connect(DATABASE_URL) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(query, values or ()) as cursor:
                return await cursor.fetchall()

    async def fetch_one(self, query: str, values: tuple = None) -> Optional[dict]:
        """Execute a query and return one result."""
        async with aiosqlite.connect(DATABASE_URL) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(query, values or ()) as cursor:
                return await cursor.fetchone()

    async def fetch_val(self, query: str, values: tuple = None) -> Optional[Any]:
        """Execute a query and return a single value."""
        async with aiosqlite.connect(DATABASE_URL) as db:
            async with db.execute(query, values or ()) as cursor:
                result = await cursor.fetchone()
                return result[0] if result else None

    async def execute(self, query: str, values: tuple = None) -> None:
        """Execute a query without returning results."""
        async with aiosqlite.connect(DATABASE_URL) as db:
            await db.execute(query, values or ())
            await db.commit()


async def init_db():
    """Initialize the database with required tables."""
    async with aiosqlite.connect(DATABASE_URL) as db:
        # Create workflows table
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

        # Create workflow_executions table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS workflow_executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workflow_id TEXT NOT NULL,
                execution_time REAL,
                status TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (workflow_id) REFERENCES workflows(id)
            )
        """)

        await db.commit()


@asynccontextmanager
async def get_db() -> AsyncGenerator[Database, None]:
    """Get a database instance as an async context manager."""
    db = Database()
    try:
        yield db
    finally:
        # No explicit cleanup needed as each operation manages its own connection
        pass

# Create a global database instance
db = Database()

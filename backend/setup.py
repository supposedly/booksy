import aiofiles
import aioredis
import asyncio
from functools import wraps
from .typedef import User

async def create_pg_tables(conn):
    with open('/app/backend/sql/schema_setup.sql', 'r') as f:
        await conn.execute(f.read())

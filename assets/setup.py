import aiofiles
import asyncio

async def create_pg_tables(conn):
    async with aiofiles.open('./static/sql/schema_setup.sql', 'r') as f:
        await conn.execute(f.readall())

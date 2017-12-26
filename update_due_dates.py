import os
import asyncpg

query = """
UPDATE items
   SET fines = 
         CASE
           WHEN current_date > items.due_date
             THEN (current_date - items.due_date) * locations.fine_amt
           ELSE 0
         END
  FROM locations
WHERE mid = currval(pg_get_serial_sequence('items', 'mid'));
"""

async def update_fines():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    values = await conn.fetch(query)
    await conn.close()

loop = asyncio.get_event_loop()
loop.run_until_complete(update_fines())

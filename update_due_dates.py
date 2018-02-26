import os
import asyncio

import asyncpg

query = '''
UPDATE items
   SET fines =
         CASE
           WHEN current_date > items.due_date
             THEN (current_date - items.due_date) * locations.fine_amt
           ELSE 0 -- if the item isn't due yet, then set its fines to $0.00
         END
  FROM locations
 WHERE items.lid = locations.lid;
'''

# I COULD do this synchronously and with less boilerplate using
# regular ol' psycopg2, but asyncpg is faster by a lot so eh

async def update_fines():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    await conn.execute(query)
    await conn.close()

loop = asyncio.get_event_loop()
loop.run_until_complete(update_fines())

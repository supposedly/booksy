import os
import asyncio

import asyncpg

# update fines and purge old signups

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
 
DELETE FROM signups WHERE current_date - date >= 1;
'''

# I COULD do this synchronously and with a bit less boilerplate using
# regular ol' psycopg2, but ... eh

async def update_fines():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    try:
        await conn.execute(query)
    finally:
        await conn.close()

loop = asyncio.get_event_loop()
loop.run_until_complete(update_fines())

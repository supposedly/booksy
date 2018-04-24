import asyncio
import os
import datetime as dt

import asyncpg

# update fines and purge old signups

update_fines = '''
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

async def update_all():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    try:
        await conn.execute(update_fines)
    finally:
        await conn.close()

loop = asyncio.get_event_loop()
loop.run_until_complete(update_all())

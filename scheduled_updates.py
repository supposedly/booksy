import asyncio
import datetime as dt
import os

now = dt.datetime.now

import asyncpg


# update fines and purge old signups
# then record weekly report data
update_query = '''
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

-----

DELETE FROM weeklies WHERE report_day = '{0}';

INSERT INTO weeklies (type, mid, lid, title, issued_to, due_date, fines, report_day)
SELECT 'item', items.mid, items.lid, items.title, items.issued_to, items.due_date, items.fines, locations.report_day
  FROM items JOIN locations ON locations.lid = items.lid
 WHERE locations.report_day = '{0}';

INSERT INTO weeklies (type, uid, rid, username, report_day)
SELECT 'member', members.uid, members.rid, members.username, locations.report_day
  FROM members JOIN locations ON locations.lid = members.lid
 WHERE locations.report_day = '{0}';

INSERT INTO weeklies (type, mid, uid, report_day)
SELECT 'hold', holds.mid, holds.uid, locations.report_day
  FROM holds JOIN items ON holds.mid = items.mid JOIN locations ON locations.lid = items.lid
 WHERE locations.report_day = '{0}';

UPDATE locations SET last_report_date = current_date WHERE report_day = '{0}';
'''

async def update_all():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    try:
        await conn.execute(update_query.format(now().strftime('%A').lower()))
    finally:
        await conn.close()

loop = asyncio.get_event_loop()
loop.run_until_complete(update_all())
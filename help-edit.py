"""
My help articles aren't stored in this repository, but rather in the project's
PostgreSQL DB. This script lets me edit them easily.

Honestly, although I wrote this whole file in one night and was done with
it after two hours at most, I'm almost more proud of its functionality
than I am of the whole rest of the project.
It's pretty cool.
"""
import asyncio
import subprocess
import os
import ssl
import tempfile
import textwrap

import asyncpg


class HelpItem:
    TITLEPAD = 0
    
    def __init__(self, rec: asyncpg.Record, conn: asyncpg.Connection, *, loop: asyncio.AbstractEventLoop, new: bool = False):
        self._conn = conn
        self._loop = loop
        
        self._id = rec['id']
        
        if new:
            self.title = self.brief = self.content = ''
        else:
            self.title = rec['title']
            self.brief = rec['brief'] or ''
            self.content = rec['content']
        
        self.__class__.TITLEPAD = max(self.__class__.TITLEPAD, len(self.title))
    
    def __iter__(self):
        yield f'{self.id: >2}'
        yield f'{self.title: <{self.__class__.TITLEPAD}}'
        if self.brief is None:
            raise StopIteration
        yield textwrap.shorten(self.brief, width=50, placeholder='...')
    
    @property
    def id(self):
        return self._id
    
    async def _update(self, column, new):
        await self._conn.execute(f'''UPDATE help SET {column} = $2::text WHERE id = $1::bigint''', self._id, new)
        return new
    
    async def edit_title(self, new=None):
        if new is None:
            print('', *textwrap.wrap(self.title), sep='\n  ')
            new = await self._loop.run_in_executor(None, input, '\ntitle> ')
            if not new:
                return
        self.title = await self._update('title', new)
        self.__class__.TITLEPAD = max(self.__class__.TITLEPAD, len(new))
    
    async def edit_brief(self, new=None):
        if new is None:
            print('', *textwrap.wrap(self.brief), sep='\n  ')
            new = await self._loop.run_in_executor(None, input, '\nbrief> ')
            if not new:
                return
        self.brief = await self._update('brief', new)
    
    async def edit_content(self):
        with tempfile.NamedTemporaryFile('w+', delete=False) as tmp:
            tmp.write(self.content)
            tmp.flush()
        os.rename(tmp.name, tmp.name + '.md')
        tmp.name += '.md'
        await self._loop.run_in_executor(None, subprocess.call, ['gedit', '-w', tmp.name])
        with open(tmp.name) as tmp:
            new = tmp.read()
        os.unlink(tmp.name)
        self.content = await self._update('content', new)


async def do(items: list, conn: asyncpg.Connection, *, loop: asyncio.AbstractEventLoop):
    msg = ''
    while True:
        print('ID\tTITLE', ' '*(HelpItem.TITLEPAD-5), '\tBRIEF', sep='', end='\n\n')
        print('\n'.join(map('\t'.join, items.values())))
        print('', msg, sep='\n')
        inp = await loop.run_in_executor(None, input, '\n> ')
        try:
            ID, column, *new = inp.split(None, 3)
        except ValueError:
            if not inp.startswith('new'):
                if inp in ('exit', 'quit', 'q'):
                    break
                if inp.isdigit():
                    msg = f"{inp}: {getattr(items.get(int(inp)), 'title', '')}"
                os.system('clear')
                continue
            # Create new help item
            await conn.execute('''INSERT INTO help SELECT''')
            item = HelpItem(
              {'id': await conn.fetchval('''SELECT last_value FROM help_id_seq''')},
              conn,
              loop=loop,
              new=True
              )
            print('ID:', item.id)
            await item.edit_title()
            await item.edit_brief()
            await item.edit_content()
            items[item.id] = item
            continue
        if ID == 'do':
            try:
                msg = await conn.fetch(' '.join((column, *new)))
            except Exception as e:
                msg = f'{type(e).__name__}: {e}'
            os.system('clear')
            continue
        try:
            meth = getattr(items[int(ID)], 'edit_' + column.lower())
        except (KeyError, AttributeError) as e:
            msg = str(e)
            os.system('clear')
            continue
        except ValueError:
            break
        msg = f"{ID} ({column}): {items[int(ID)].title}"
        await (meth() if column == 'content' else meth(*new))
        os.system('clear')


async def main(pg_url: str, ssl_ctx: ssl.SSLContext, *, loop: asyncio.AbstractEventLoop):
    conn = await asyncpg.connect(pg_url, loop=loop, ssl=ssl_ctx)
    await do(
      {r['id']: HelpItem(r, conn, loop=loop) for r in await conn.fetch('''SELECT * FROM help''')},
      conn,
      loop=loop
      )
    await conn.close()


if __name__ == '__main__':
    os.system('clear')
    
    pg_url = subprocess.run(
        'heroku pg:credentials:url -a booksy-db'.split(),
        stdout=subprocess.PIPE
      ).stdout.decode().split()[-1]
    
    ssl_ctx: ssl.SSLContext = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(pg_url, ssl_ctx, loop=loop))

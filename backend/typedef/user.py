import asyncio
import functools
import io
import datetime as dt
from decimal import Decimal
from asyncio import iscoroutinefunction as is_coro

import asyncpg
import pandas

from ..core import AsyncInit
from ..attributes import Perms, Maxes, Locks


#################################################
try:
    import bcrypt
except ModuleNotFoundError: # means I'm testing (can't access app.config.TESTING from here) (don't have libffi/bcrypt on home PC)
    import types
    def __hashpw(pw, *_, **__):
        return pw.encode()
    def __gensalt(*_, **__):
        return 0
    def __checkpw(*_, **__):
        return True # blegh
    bcrypt = types.SimpleNamespace(
      hashpw = __hashpw,
      gensalt = __gensalt,
      checkpw = __checkpw
    )
#################################################


class User(AsyncInit):
    @staticmethod
    def do_imports():
        global Location, Role, MediaItem, MediaType, User
        from . import Location, Role, MediaItem, MediaType, User
    
    async def __init__(self, uid, app, *, location=None, role=None):
        self._app = app
        self.pool = self._app.pg_pool
        self.acquire = self.pool.acquire
        try:
            self.user_id = self.uid = int(uid)
        except TypeError:
            raise ValueError('No user exists with this username!')
        async with self.acquire() as conn:
            query = '''SELECT username, fullname, lid, rid, manages, email, phone, type, recent, perms, maxes, locks, pwhash FROM members WHERE uid = $1::bigint;'''
            (
              username, name, lid,
              rid, manages, email,
              phone, self._type, recent,
              permbin, maxbin, lockbin,
              self._pwhash
            ) = await conn.fetchrow(query, self.uid)
            query = '''SELECT count(*) FROM holds WHERE uid = $1::bigint'''
            holds = await conn.fetchval(query, self.uid)
            query = '''SELECT count(*) FROM items WHERE issued_to = $1::bigint'''
            self.num_checkouts = await conn.fetchval(query, self.uid)
        self.location = location if isinstance(location, Location) else await Location(lid, self._app)
        self.role = role if isinstance(role, Role) else await Role(rid, self._app, location=self.location)
        self.lid, self.rid = lid, rid
        self.holds = holds
        self.username = username
        self.name = name
        self.email = email
        self.phone = phone
        self.manages = manages
        self.recent = recent
        self._permnum = permbin
        self._maxnum = maxbin
        self._locknum = lockbin
        self.is_checkout = bool(self._type) # == 1
    
    def to_dict(self) -> dict:
        props = ['user_id', 'username', 'name', 'lid', 'manages', 'rid', 'email', 'phone', 'is_checkout', 'perms', 'recent']
        rel = {i: getattr(self, i, None) for i in props}
        rel['locname'] = self.location.name
        rel['rolename'] = self.role.name
        return rel
    
    @property
    def cannot_check_out(self):
        able = self.locks.checkouts, self.maxes.checkout_duration
        if all(able): # success
            return False
        ret = ("You can't check anything out at the moment"
        
        + ('' if able[0] else
            ' (currently using {} of {} allowed concurrent checkouts'
                .format(self.num_checkouts, self.locks.checkouts))
        
        + ('' if able[1] else '; allowed to check out for 0 weeks'))
        return ret + ('' if able[0] else ')')
    
    @classmethod
    async def create(cls, app, **kwargs):
        props = ['username', 'pwhash', 'lid', 'email', 'phone']
        query = '''
        INSERT INTO members (
                      username, pwhash,
                      lid,
                      email, phone
                      )
             SELECT $1::text, $2::bytea,
                    $3::bigint,
                    $4::text, $5::text
        '''
        await app.pg_pool.execute(query, *(kwargs[i] for i in props))
        return await cls(uid, app)
    
    @classmethod
    async def from_identifiers(cls, username=None, location=None, lid=None, *, app):
        """
        Returns a new User instance, given a username and location ID.
        (More specifically, it grabs the user's ID from the above combo
        and, once found, passes it to __init__())
        """
        if lid and location is None:
            location = await Location(int(lid), app)
        query = '''SELECT uid FROM members WHERE username = $1::text AND lid = $2::bigint'''
        uid = await app.pg_pool.fetchval(query, username, location.lid)
        return await cls(uid, app)
    
    def edit_perms(self, **new):
        self.perms.edit(**new)
    
    def edit_perms_from_seq(self, *new):
        self.perms.edit_from_seq(*new)
    
    async def verify_pw(self, pw):
        return await self._app.aexec(self._app.ppe, bcrypt.checkpw, pw.encode(), self._pwhash)
    
    async def delete(self):
        """
        Get rid of & clean up after a member on deletion.
        """
        queries = '''
        DELETE FROM members
         WHERE uid = $1::bigint
        ''', '''
        DELETE FROM holds
         WHERE uid = $1::bigint  
        ''', '''
        UPDATE items
           SET issued_to = NULL,
               due_date = NULL,
               fines = NULL
         WHERE issued_to = $1::bigint
        '''
        async with self.acquire() as conn:
            [await conn.execute(query, self.uid) for query in queries]
    
    async def notifs(self):
        async with self.acquire() as conn:
            # could probably do this in one line
            holds = await conn.fetchval('''
            SELECT count(*) FROM holds, items
             WHERE holds.uid = $1::bigint
               AND items.mid = holds.mid
               AND items.issued_to IS NULL
            ''', self.uid)
            fines = await conn.fetchval('''SELECT sum(fines) AS fines FROM items WHERE issued_to = $1::bigint''', self.uid)
            overdue = await conn.fetchval('''SELECT count(*) AS overdue FROM items WHERE due_date < current_date;''')
        
        response = []
        def add(type_, message):
            response.append({"type": type_, "text": message})
        
        if holds:
            add('notification', f'You have {holds} holds available.')
        if overdue:
            add('warning', f'You have {overdue} overdue items.')
        if fines:
            add('warning', f'You have ${fines} in overdue fines.')
        if self.cannot_check_out:
            add('alert', self.cannot_check_out)
        return response
    
    async def hold(self, *, title, author, type_, genre, item=None):
        if item is None:
            item = await self.location.search(title=title, genre=genre, type_=str(type_), author=author, max_results=1, where_taken=True)
        templ = '''
       SELECT count(*)
         FROM items
        WHERE lower(title) = lower($1::text)
          AND lower(author) = lower($2::text)
          AND lower(type) = lower($3::text)
          AND lower(genre) = lower($4::text)
        '''
        async with self.acquire() as conn:
            if await conn.fetchval(templ + """AND issued_to IS NULL""", title, author, str(type_), genre):
                return 'Item is already available!'
            if await conn.fetchval(templ + """AND issued_to = $5::bigint""", title, author, str(type_), genre, self.uid):
                return 'You have this item checked out already!'
            query = '''
            INSERT INTO holds
              (uid, mid, created)
            SELECT $1::bigint, $2::bigint, current_date
            '''
            try:
                await conn.execute(query, self.uid, item.mid)
            except asyncpg.exceptions.UniqueViolationError:
                return 'You already have a hold placed on this item!'
    
    async def clear_hold(self, item):
        query = '''
        DELETE FROM holds
              WHERE uid = $1::bigint
                AND mid = $2::bigint
        '''
        return await self.pool.execute(query, self.uid, item.mid)
    
    async def edit(self, username, rid, fullname):
        query = '''
        UPDATE members
           SET username = $2::text,
               rid = $3::bigint,
               fullname = $4::text
         WHERE uid = $1::bigint
        '''
        await self.pool.execute(query, self.uid, username, rid, fullname)
    
    async def edit_self(self, name, pw):
        """
        Differs from just edit(), ofc; this method allows user to
        change their own password.
        """
        query = '''
        UPDATE members
           SET fullname = COALESCE($2::text, fullname),
               pwhash = COALESCE($3::bytea, pwhash)
         WHERE uid = $1::bigint
        '''
        pwhash = await self._app.aexec(self._app.ppe, bcrypt.hashpw, pw.encode(), bcrypt.gensalt(12))
        await self.pool.execute(query, self.uid, name, pwhash)
    
    async def items(self):
        query = '''
        SELECT mid, title, author, type, genre, image, due_date FROM items WHERE issued_to = $1::bigint
        '''
        return [{j: str(i[j]) for j in ('mid', 'title', 'author', 'genre', 'type', 'image', 'due_date')} for i in await self.pool.fetch(query, self.uid)]
    
    async def held(self):
        query = '''
        SELECT items.mid AS mid,
               items.title AS title,
               items.type AS type,
               items.author AS author,
               items.genre AS genre,
               items.image AS image
          FROM holds, items
         WHERE holds.uid = $1::bigint AND items.mid = holds.mid
        '''
        return [{j: i[j] for j in ('mid', 'title', 'author', 'genre', 'type', 'image')} for i in await self.pool.fetch(query, self.uid)]
    
    @property
    def checkouts_left(self) -> int:
        return self.locks.checkouts - self.num_checkouts
    
    @property
    def perms(self):
        if self._permnum is None:
            return self.role.perms
        return Perms(self._permnum)
    
    @property
    def maxes(self):
        if self._maxnum is None:
            return self.role.maxes
        return Maxes(self._maxnum)
    
    @property
    def locks(self):
        if self._locknum is None:
            return self.role.locks
        return Locks(self._locknum)

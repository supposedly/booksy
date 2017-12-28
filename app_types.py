"""
I have a feeling this isn't proper usage of the term 'container'
Just a bunch of type definitions :)
"""

import asyncio
import datetime as dt
from asyncio import iscoroutinefunction as is_coro

from app_resources import LazyProperty, AsyncInit, RoleAttrMixin

class MediaType(AsyncInit, RoleAttrMixin):
    async def __init__(self, name, location, app):
        self.name = name
        self.app = app
        self.pool = self.app.pg_pool
        self.location = await Location(location, self.app) if isinstance(location, int) else location
    
    async def get_items(self):
        async with self.pool.acquire() as conn:
            query = """
            SELECT mid
              FROM items
             WHERE media_type == $1
               AND lid = $2::bigint
            """
            return await conn.fetch(query, self.name, self.lid)
    
    @property
    async def maxes(self):
        async with self.pool.acquire() as conn:
            query = """SELECT maxes FROM items WHERE media_type = $1::text"""
            maxbin = await conn.fetch(query, self.name)
        return self._maxes(maxbin)
    
    async def set_maxes(self, new):
        async with self.app.pg_pool.acquire() as conn:
            query = """
            UPDATE items
               SET maxes = $1::bigint
             WHERE media_type = $1::text
            """
            await conn.execute(query, new, self.name)
    
    @property
    async def locks(self):
        async with self.pool.acquire() as conn:
            query = """SELECT locks FROM items WHERE media_type = $1::text"""
            lockbin = await conn.fetch(query, self.name)
        return self._locks(lockbin)
    
    async def set_locks(self, new):
        async with self.pool.acquire() as conn:
            query = """
            UPDATE items
               SET locks = $1::bigint
             WHERE media_type = $2::text
            """
            await conn.execute(query, new, self.name)


class MediaItem(AsyncInit, RoleAttrMixin):
    _aiolock = asyncio.Lock()
    async def __init__(self, mid, app):
        with await aiolock:
            self.mid = mid
            self.app = app
            async with self.pool.acquire() as conn:
                query = """
                SELECT type, isbn, lid, author, title, published, genre, issued_to, due_date, fines, acquired, maxes
                 FROM items
                WHERE mid = $1::bigint
                """
                # this is so ugly
                self._type, self.isbn, self.lid, \
                self.author, self.title,         \
                self.published, self.genre,      \
                self._issued_uid, self.due_date, \
                self.fines, self.acquired,       \
                self.maxes = await conn.fetchrow(query, self.mid)
            self.location = await Location(self.lid, self.app)
            self.available = not self._issued_uid
            self.issued_to = await User(self._issued_uid, self.app)
            self.type = await MediaType(self._type, self.lid, self.app)
    
    async def issue(self, uid):
        user = User(uid, self.app)
        with await _aiolock:
            async with self.pool.acquire() as conn:
                query = """
                UPDATE items
                   SET issued_to = $1, -- uid given as param
                       due_date = current_date + $2, -- time-allowed parameter calculated in python bc would be awful in plpgsql
                       fines = 0
                 WHERE mid = $3;
                 """
                 await conn.execute(uid, 7 * user.maxes['checkout duration'], self.mid)
             self.issued_to = user
             self.due_date = dt.datetime.utcnow() + dt.timedelta(weeks=user.maxes['checkout duration'])
             self.fines = 0
    
    async def return(self):
        with await _aiolock:
            async with self.pool.acquire() as conn:
                query = """
                UPDATE items
                   SET issued_to = NULL,
                       due_date = NULL,
                       fines = NULL
                 WHERE mid = $1;
                """
                await conn.execte(uid, self.mid)
    
    async def remove(self):
        """
        Proxy for Location().remove(MediaItem())
        """
        await self.location.remove_item(self)


class Location(AsyncInit):
    _aiolock = asyncio.Lock()
    async def __init__(self, lid, app):
        self.app = app
        self.pool = self.app.pg_pool
        self.lid = lid
        with await _aiolock:
            async with self.pool.acquire() as conn:
                query = """SELECT name, ip, fine_amt, fine_interval FROM locations WHERE lid = $1::bigint"""
                name, ip, fine_amt, fine_interval = await conn.fetchrow(query)
        self.name = name
        self.ip = ip
        self.fine_amt = fine_amt
        self.fine_interval = fine_interval
    
    async def add_media_type(self, type_name: str):
        with await _aiolock:
            async with self.pool.acquire() as conn:
                query = """
                UPDATE locations
                   SET media_types = array_append(media_types, $1::text)
                 WHERE lid = $2::bigint
                """
                await conn.execute(query, type_name, self.lid)
            return await Media
    
    async def remove_media_type(self, type_name: str):
        with await _aiolock:
            async with self.app.pg_pool.acquire


class Role(AsyncInit, RoleAttrMixin):
    _aiolock = asyncio.Lock()
    async def __init__(self, rid, app):
        self.app = app
        self.pool = self.app.pg_pool
        self.rid = rid
        with await _aiolock:
            async with self.pool.acquire() as conn:
                query = """SELECT lid, name, permissions, maxes, locks FROM roles WHERE rid = $1::bigint"""
                lid, name, permbin, maxbin, lockbin = await conn.fetchrow(query, self.rid)
        self.location = await Location(lid, self.app)
        self.name = name
        self._permbin = permbin
        self._maxbin = maxbin
        self._lockbin = lockbin
        # straightforward, convert the perms number to binary string
        # e.g. 45 --> '1011010'.
        # ...
        # Then, split the signed maxes/locks into their
        # constituent bytes
        # e.g. 200449 --> (1, 15, 3, 0, 0, 0, 0, 0)
        # because 200449 is binary 0b000000110000111100000001
        # and 0b00000011 == 3, 0b00001111 == 15, 0b00000001 == 1
        # All the extra (0,)s are in case I ever decide to add more
        # locks/permissions, so I can just slot it into one of the
        # existing 0 values without having to refactor the entire database
        # Also I can never use the last byte because smallint is signed, lol
    
    @LazyProperty
    def perms(self):
        return self._perms(self._permbin)
    
    @LazyProperty
    def maxes(self):
        return self._maxes(self._maxbin)
    
    @LazyProperty
    def locks(self):
        return self._locks(self._lockbin)
    
    @LazyProperty
    def location(self):
        return await Location(lid)


class Permission(RoleAttrMixin):
    def __init__(self):

class User(AsyncInit, RoleAttrMixin):
    _aiolock = asyncio.Lock()
    async def __init__(self, uid, app):
        self.app = app
        self.pool = self.app.pg_pool
        self.user_id = self.uid = uid
        with await _aiolock:
            async with self.app.pg_pool.acquire() as conn:
                query = """SELECT username, lid, rid, manages, email, phone, type, maxes, locks FROM members WHERE uid = lower($1::text);"""
                username, lid, rid, manages, email, phone, self._type, maxbin, lockbin = await conn.fetchrow(query, uid)
        self.role = await Role(rid)
        self.location = await Location(lid)
        self.email = email
        self.phone = phone
        self.manages = manages
        self.type = ('member', 'library')[self._type] # whether they are a library-wide checkout account or not
        self._maxbin = maxbin
        self._lockbin = lockbin
    
    def to_dict(self) -> dict:
        props = ['user_id', 'username', 'lid', 'manages', 'rid', 'email', 'phone', 'type']
        return {i: getattr(self, i, None) for i in props}
    
    @classmethod
    async def from_identifiers(cls, username, lid) -> User:
        """
        Returns a new User instance, given a username and location ID.
        """
        with await _aiolock:
            async with self.pool.acquire() as conn:
                query = """SELECT uid FROM members WHERE username = $1 AND lid = $2::bigint"""
                uid = await conn.fetchval(query, username, lid)
        return await cls(uid)
    
    @property
    def can_check_out(self, userdict) -> bool:
        return self.maxes['checkouts'] and self.maxes['checkout duration'] and self.locks['checkout threshold']
    
    async def num_current_checkouts(self) -> int:
        with await _aiolock:
            async with self.pool.acquire() as conn:
                query = """SELECT count(*) FROM items WHERE uid = $1::bigint"""
                return await conn.fetchval(self.uid)
    
    @property
    def maxes(self) -> dict:
        return self._maxes(self._maxbin) or self.role.maxes
    
    @property
    def locks(self) -> dict:
        return self._locks(self._lockbin) or self.role.locks

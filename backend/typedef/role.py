import asyncio
import functools
import io
import datetime as dt
from decimal import Decimal
from asyncio import iscoroutinefunction as is_coro

import asyncpg
import pandas


from ..core import AsyncInit
from ..attributes import Perms, Limits, Locks


class Role(AsyncInit):
    """
    Defines a role, i.e. an abstract container for authorization stuff.
    
    location   (Location): The location this role is bound to
    name       (str):      Role's given name
    is_default (bool):     Whether this is one of the 3 roles created by default
    rid        (int):      Role's unique ID
    _permnbin,
    _limnbin,               Shorthand for role.perms/limits/locks.raw, but
    _locknbin   (int):      not intended to be exposed outside this class
    """
    @staticmethod
    def do_imports():
        global Location, MediaItem, MediaType, User
        from . import Location, MediaItem, MediaType, User
    
    async def __init__(self, rid, app, *, location=None):
        self._app = app
        self.pool = self._app.pg_pool
        self.acquire = self.pool.acquire
        self.rid = int(rid)
        query = '''SELECT lid, name, isdefault, permissions, limits, locks FROM roles WHERE rid = $1::bigint'''
        try:
            lid, name, default, permbin, limbin, lockbin = await self.pool.fetchrow(query, self.rid)
        except TypeError:
            raise TypeError('role') # to be fed back to application as '{role} does not exist!'
        self.location = await Location(lid, self._app) if location is None else location
        self.name = name
        self.is_default = default
        # Comments below pertain to these three lines
        self._permbin = permbin
        self._limbin = limbin
        self._lockbin = lockbin
        # Straightforward, convert the perms number to binary string
        # e.g. 45 --> '1011010'.
        # 
        # Then, split the signed limits/locks into their
        # constituent bytes
        # e.g. 200449 --> (1, 15, 3, 0, 0, 0, 0, 0)
        # because 200449 is binary 0b000000110000111100000001
        # and 0b00000011 == 3 | 0b00001111 == 15 | 0b00000001 == 1
        # The extraneous (0,) bits are in case I ever decide to add more
        # locks/permissions, so I can just slot it into one of the
        # existing 0 bits without having to refactor the entire database.
        # Also I can never use the last byte because smallint is signed, lol
    
    def __str__(self):
        return str(self.rid)
    
    def to_dict(self) -> dict:
        return {
          'rid': self.rid,
          'name': self.name,
          'perms_raw': self.perms.raw,
          'perms': self.perms.props,
          'limits': self.limits.props,
          'locks': self.locks.props
          }
    
    @staticmethod
    def attrs_from(*, seqs=None, kws=None):
        """
        Returns attrs (perms/limits/locks) from whichever of
        seqs (sequences, see PackedField.seq in core.py) and
        kws (kwargs, see PackedField.from_kwargs) is not-None first.
        """
        if kws is None:
            perms = Perms.from_seq(seqs['perms'])
            limits = Limits.from_seq(seqs['limits'])
            locks = Locks.from_seq(seqs['locks'])
        else:
            perms = Perms.from_kwargs(**kws['perms'])
            limits = Limits.from_kwargs(**kws['limits'])
            locks = Locks.from_kwargs(**kws['locks'])
        return perms, limits, locks
    
    async def set_attrs(self, perms, limits, locks, name):
        """
        Edits all of this role's attrs.
        Also edits its name, if applicable.
        """
        query = '''
        UPDATE roles
           SET name = $2::text,
               permissions = $3::smallint,
               limits = $4::bigint,
               locks = $5::bigint
         WHERE rid = $1::bigint
        '''
        await self.pool.execute(query, self.rid, name, perms.raw, limits.raw, locks.raw)
    
    
    async def delete(self):
        """Deletes this role."""
        query = '''DELETE FROM roles WHERE rid = $1::bigint'''
        await self.pool.execute(query, self.rid)
    
    async def num_members(self):
        """This could probably be an attr set in __init__..."""
        query = '''SELECT count(*) FROM members WHERE rid = $1::bigint'''
        return await self.pool.fetchval(query, self.rid)
    
    @property
    def perms(self):
        return Perms(self._permbin)
    
    @property
    def limits(self):
        return Limits(self._limbin)
    
    @property
    def locks(self):
        return Locks(self._lockbin)

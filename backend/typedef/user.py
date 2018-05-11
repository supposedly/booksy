import asyncpg
from types import ModuleType

import bcrypt

from ..core import AsyncInit
from ..attributes import Perms, Limits, Locks


# These are 'variable annotations', used in python 3.6 for introducing
# a variable before actually assigning to it. I'm just using them here
# so pylint stops whinging about my do_imports() method using `global`
MediaItem: ModuleType
MediaType: ModuleType
Location: ModuleType
Role: ModuleType


class User(AsyncInit):
    """
    Defines any user of the app.
    
    location    (Location): User's location (their library)
    role        (Role):     User's role
    is_checkout (bool):     Whether the user is actually a self-checkout patron account
    manages     (bool):     Whether the user owns their location
    username    (str):      User's username
    name        (str):      User's full name
    email       (str):      User's email (unused here)
    phone       (str):      User's phone number (entirely unused)
    recent      (int):      Genre of user's most-recent checkout
    holds       (int):      Quantity of items the user has on hold
    lid, rid    (int):      Shorthand for user.location.lid and user.role.rid
    _permnum,
    _limnum,               Shorthand for user.perms/limits/locks.raw, but
    _locknum    (int):      not intended to be exposed outside this class
    """
    @staticmethod
    def do_imports():
        global Location, Role, MediaItem, MediaType
        from . import Location, Role, MediaItem, MediaType
    
    async def __init__(self, uid, app, *, location=None, role=None):
        self._app = app
        self.pool = self._app.pg_pool
        self.acquire = self.pool.acquire
        try:
            self.user_id = self.uid = int(uid)
        except TypeError:
            raise ValueError('No user exists with this username!')
        async with self.acquire() as conn:
            query = '''SELECT username, fullname, lid, rid, manages, email, phone, type, recent, perms, limits, locks, pwhash FROM members WHERE uid = $1::bigint;'''
            (
              username, name, lid,
              rid, manages, email,
              phone, self._type, recent,
              permbin, limbin, lockbin,
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
        self._limnum = limbin
        self._locknum = lockbin
        self.is_checkout = bool(self._type)  # == 1
    
    def __eq__(self, other):
        return type(other) is type(self) and other.uid == self.uid
    
    def to_dict(self) -> dict:
        props = ['user_id', 'username', 'name', 'lid', 'manages', 'rid', 'email', 'phone', 'is_checkout', 'perms', 'recent']
        rel = {i: getattr(self, i, None) for i in props}
        rel['locname'] = self.location.name
        rel['rolename'] = self.role.name
        return rel
    
    def beats(self, other=None, *, perms=None, and_has=None):
        if perms is None and not hasattr(other, 'perms'):
            raise TypeError(f"invalid type for comparison with '{type(self).__name__}': '{type(other).__name__}'")
        if not (other or perms):
            raise TypeError("expecting either `perms' or an `other' user to compare against; got neither")
        
        if self.perms.raw == 127 or self == other:
            return True
        
        if self.perms.raw > (perms.raw if perms else other.perms.raw):
            if and_has is not None:
                return self.perms.namemap[and_has]
            return True
        return False
    
    @property
    def cannot_check_out(self):
        """
        Determines whether this user is prohibited from checking out,
        and if not, why.
        (could be that they've checked out too many books already or
        that their checkout duration is restricted to 0)
        """
        chk, dur = self.locks.checkouts, self.limits.checkout_duration
        if chk and dur:  # user is able to check out -- that is, unless the item's type's limits won't allow it
            return False
        ret = (
          "You can't check anything out at the moment"
          + (
            '' if chk else
            ' (currently using {} of {} allowed concurrent checkouts'
            .format(self.num_checkouts, self.locks.checkouts)
            )
          + ('' if dur else '; allowed to check out for 0 weeks')
          )
        return ret + ('' if chk else ')')  # construct dynamic notif string
    
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
        """Just shorthand"""
        self.perms.edit(**new)
    
    def edit_perms_from_seq(self, *new):
        """Just shorthand"""
        self.perms.edit_from_seq(*new)
    
    async def delete(self):
        """
        Get rid of & clean up after a member.
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
            async with conn.transaction():
                [await conn.execute(query, self.uid) for query in queries]
    
    async def notifs(self):
        """
        Construct a user's notifications, which appear on the checkout
        page and serve info regarding whether the user has holds available
        or fines accrued or items overdue.
        """
        async with self.acquire() as conn:
            holds = await conn.fetchval('''
            SELECT count(*) FROM holds, items
             WHERE holds.uid = $1::bigint
               AND items.mid = holds.mid
               AND items.issued_to IS NULL
            ''', self.uid)
            
            fines = await conn.fetchval('''
              SELECT sum(fines) AS fines
                FROM items
               WHERE issued_to = $1::bigint
             ''', self.uid)
            
            overdue = await conn.fetchval('''
              SELECT count(*) AS overdue
                FROM items
               WHERE due_date < current_date
                 AND issued_to = $1::bigint
               ''', self.uid)
        
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
        """
        Places a hold from this user on an item.
        All the extra attrs are to determine whether the item (as a whole, i.e.
        not just the specifically-requested media ID) is available at all
        before allowing the hold.
        """
        if item is None:
            item = await self.location.search(title=title, genre=genre, type_=type_ and str(type_), author=author, max_results=1, where_taken=True)
        templ = '''
       SELECT count(*)
         FROM items
        WHERE lower(title) = lower($1::text)
          AND lower(author) = lower($2::text)
          AND lower(type) = lower($3::text)
          AND lower(genre) = lower($4::text)
        '''
        async with self.acquire() as conn:
            if await conn.fetchval(templ + '''AND issued_to IS NULL''', title, author, str(type_), genre):
                return 'Item is already available!'
            if await conn.fetchval(templ + '''AND issued_to = $5::bigint''', title, author, str(type_), genre, self.uid):
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
        """
        Removes a hold.
        """
        query = '''
        DELETE FROM holds
              WHERE uid = $1::bigint
                AND mid = $2::bigint
        '''
        return await self.pool.execute(query, self.uid, item.mid)
    
    async def edit(self, username, rid, fullname):
        """
        Edits all this user's info.
        """
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
        Differs from above edit(): this method allows user to
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
        """
        Returns all this user's checked-out items.
        """
        query = '''
        SELECT mid, title, author, type, genre, image, due_date FROM items WHERE issued_to = $1::bigint
        '''
        return [{j: str(i[j]) for j in ('mid', 'title', 'author', 'genre', 'type', 'image', 'due_date')} for i in await self.pool.fetch(query, self.uid)]
    
    async def held(self):
        """
        Returns all items this user has on hold.
        """
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
        """
        Returns how many more items this user is allowed
        to check out, taking into account their max-allowed
        checkouts (from their role) and their current
        number of checkouts.
        """
        return self.locks.checkouts - self.num_checkouts
    
    @property
    def perms(self):
        if self.is_checkout:  # Checkout accounts have no perms
            return Perms(0)
        if self._permnum is None:
            return self.role.perms
        return Perms(self._permnum)
    
    @property
    def limits(self):
        if self._limnum is None:
            return self.role.limits
        return Limits(self._limnum)
    
    @property
    def locks(self):
        if self._locknum is None:
            return self.role.locks
        return Locks(self._locknum)

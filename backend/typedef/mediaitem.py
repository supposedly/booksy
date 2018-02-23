import datetime as dt
from decimal import Decimal

# 

from ..core import AsyncInit
from ..attributes import Perms, Maxes, Locks


class MediaItem(AsyncInit):
    """
    Defines a single item of media.
    Instance methods include:
    
    to_dict: Called to pass item data to front end.
    set_maxes: Unused currently. Sets item-specific Maxes, and is able
      to set either on a single instance of an item or across all items
      with the same title & author & type
    status: Whether item is checked out
    pay_off: Clear fines
    edit: Edits the item's metadata
    issue_to: Check out to a given user
    check_in: Check item in
    remove: Delete from library's records
    """
    
    @staticmethod
    def do_imports():
        global Location, Role, MediaItem, MediaType, User
        from . import Location, Role, MediaItem, MediaType, User
    
    props = ['mid', 'genre', 'type',
             'isbn', 'lid', 'fines',
             'title', 'author', 'published', 
             'image', 'price', 'length',
             'available', 'due_date']
    async def __init__(self, mid, app):
        try:
            self.mid = int(mid)
        except (ValueError, TypeError):
            raise TypeError('item with this ID')
        self.app = app
        self.pool = app.pg_pool
        self.acquire = self.pool.acquire
        query = '''
        SELECT type, isbn, lid, author, title, published, genre, issued_to, due_date, fines, acquired, maxes, image, length, price
          FROM items
         WHERE mid = $1::bigint
        '''
        try:
            (
             self._type, self.isbn, self.lid,
             self.author, self.title,
             self.published, self.genre,
             self._issued_uid, self.due_date,
             self.fines, self.acquired,
             self.maxes, self.image,
             self.length, self.price
            ) = await self.pool.fetchrow(query, self.mid)
        except TypeError:
            raise TypeError('item') # to be fed back to the client as "{item} does not exist!"
        self.location = await Location(self.lid, self.app)
        self.available = not self._issued_uid
        self.issued_to = None if self._issued_uid is None else await User(self._issued_uid, self.app, location=self.location)
        self.type = await MediaType(self._type, self.lid, self.app)
        self.maxes = None if self.maxes is None else Maxes(self.maxes)
    
    def to_dict(self):
        retdir = {attr: str(getattr(self, attr, None)) for attr in self.props}
        retdir['type_'], retdir['available'] = self._type, not self.issued_to
        return retdir
    
    async def set_maxes(self, newmaxes: Maxes, *, mid=True):
        if not isinstance(newmaxes, Maxes):
            raise TypeError('Argument must be of type Maxes')
        query = '''
        UPDATE items
           SET maxes = $1::bigint
         WHERE {}
        '''.format('mid = $2::bigint' if mid else "title ILIKE '%' || $2::text || '%' AND author ILIKE '%' || $3::text || '%'") #TODO: add mediatype comparison as well
        await self.pool.execute(query, newmaxes.num, *([self.mid] if mid else [self.title, self.author]))
        self.maxes = newmaxes
    
    async def status(self, *, resp = {'issued_to': None, 'due_date': None, 'fines': None}):
        query = '''
        SELECT
              CASE
                WHEN issued_to IS NOT NULL
                THEN (issued_to, due_date, fines)
              END
         FROM items
        '''
        check = await self.pool.fetchrow(query)
        try:
            issued_to, due_date, fines = check
        except ValueError:
            pass
        else:
            # hacky? probably. But it just updates, for instance,
            # resp['issued_to'] to the local value of the `issued_to' variable
            resp = {i: locals()[i] for i in resp}
        return resp
    
    async def pay_off(self):
        query = '''
        UPDATE items
           SET fines = 0::numeric
         WHERE mid = $1::bigint
        '''
        return await self.pool.execute(query, self.mid)
    
    async def edit(self, title, author, genre, type_, price, length, published, isbn):
        query = '''
        UPDATE items
           SET title = $2::text,
               author = $3::text,
               genre = $4::text,
               type = $5::text,
               price = $6::numeric,
               length = $7::int,
               published = $8::int,
               isbn = $9::text
         WHERE mid = $1::bigint
        '''
        await self.pool.execute(query, self.mid, title, author, genre, type_, round(Decimal(price), 2), int(length), int(published), isbn)
    
    async def issue_to(self, user):
        """
        Set user's recent genre to self.genre,
        set item's issued_to to the user's ID,
        and clear the user's holds on the item
        """
        infinite = user.maxes.checkout_duration >= 255
        async with self.acquire() as conn:
            query = '''
            UPDATE members
               SET recent = $2::text
             WHERE uid = $1::bigint;
            '''
            await conn.execute(query, user.uid, self.genre)
            
            query = '''
            UPDATE items
               SET issued_to = $1::bigint, -- uid given as param
                   due_date = {}, -- time-allowed parameter calculated in python bc would be awful to do in plpgsql
                   fines = 0
             WHERE mid = $2::bigint;
            '''.format("'Infinity'::date" if infinite else 'current_date + $3::int')
            # as many weeks as specified UNLESS the user has no restrictions on checkout time
            # in which case infinity (which postgres allows in date fields, handily enough)
            params = [query, user.uid, self.mid]
            if not infinite:
                params.append(7*user.maxes.checkout_duration)
            await conn.execute(*params)
            query = '''
            DELETE FROM holds
             WHERE mid = $1::bigint
               AND uid = $2::bigint
            '''
            await conn.execute(query, self.mid, user.uid)
        self.issued_to = user
        self.due_date = 'never.' if infinite else dt.datetime.utcnow() + dt.timedelta(weeks=user.maxes.checkout_duration)
        self.fines = 0
        self.available = False
    
    async def check_in(self):
        query = '''
        UPDATE items
           SET issued_to = NULL,
               due_date = NULL,
               fines = NULL
         WHERE mid = $1::bigint;
        '''
        await self.pool.execute(query, self.mid)
        self.available = True
    
    async def remove(self):
        """
        Just a proxy method for Location().remove_item(MediaItem())
        """
        await self.location.remove_item(item=self)
    
    @property
    def perms(self):
        if self._permnum is None:
            return self.type.perms
        return Perms(self._permnum)
    
    @property
    def maxes(self):
        if self._maxnum is None:
            return self.type.maxes
        return Maxes(self._maxnum)
    
    @property
    def locks(self):
        if self._locknum is None:
            return self.type.locks
        return Locks(self._locknum)

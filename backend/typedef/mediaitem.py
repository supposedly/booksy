import datetime as dt
import types
from decimal import Decimal

from ..core import AsyncInit
from ..attributes import Perms, Maxes, Locks


class MediaItem(AsyncInit):
    """
    Defines an item of media, e.g. a book or CD.
    
    location    (Location):  The library this media item is located in.
    type        (MediaType): The MediaType object representing the item's type.
    issued_to   (User):      The User object, if applicable, of the member item is checked out to.
    fines       (Decimal):   Amount in USD of fines on item, if checked out and overdue; 0 if checked out and not overdue, None if not checked out.
    length      (Decimal):   How 'long' item is, though the unit of length ('minutes', 'pages'...) is defined on its media type.
    price       (Decimal):   How much item costs.
    available   (bool):      Whether item is not checked out to anybody.
    acquired    (date):      What day item was added to library.
    published   (date):      Specifically a datetime.date object; what year item was published.
    due_date    (date):      Due date if item is checked out, or None otherwise.
    mid         (int):       Item's unique ID, used on its barcode and when checking in/out.
    lid         (int):       Shorthand for item.location.lid.
    _issued_uid (int):       The raw uID of the member item is checked out to; not intended to be exposed elsewhere.
    _maxnum     (int):       (UNUSED) contains the raw number of item's max overrides (was implemented on media *types* in the final project).
    genre       (str):       Name of item's genre.
    image       (str):       A link to Google Books' image for item (really only works on books and maybe audio recordings of books).
    author      (str):       Name of item's author or creator.
    title       (str):       Title of item.
    _type       (str):       Shorthand for item.type.name, but not intended to be exposed outside this class.
    isbn        (str):       Item's ISBN (if defined by user), or if not then whichever of its ISBN-10/-13 was available on Google Books' API.
    """
    
    props = [
      'mid', 'genre', 'type',
      'isbn', 'lid', 'fines',
      'title', 'author', 'published', 
      'image', 'price', 'length',
      'available', 'due_date'
      ]
    
    @staticmethod
    def do_imports():
        global Location, Role, MediaItem, MediaType, User
        from . import Location, Role, MediaItem, MediaType, User
    
    async def __init__(self, mid, app):
        try:
            self.mid = int(mid)
        except (ValueError, TypeError):
            raise TypeError('item with this ID') # passed to frontend as 'Item with this ID does not exist'
        self._app = app
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
             self._maxnum, self.image,
             self.length, self.price
            ) = await self.pool.fetchrow(query, self.mid)
        except TypeError:
            raise TypeError('item') # to be fed back to the client as "item does not exist!"
        self.location = await Location(self.lid, self._app)
        self.available = not self._issued_uid
        self.issued_to = None if self._issued_uid is None else await User(self._issued_uid, self._app, location=self.location)
        self.type = None if self._type is None else await MediaType(self._type, self.location, self._app)
    
    def to_dict(self):
        retdir = {attr: str(getattr(self, attr, None)) for attr in self.props}
        retdir['type'] = self.type.to_dict() if self.type else ''
        retdir['available'] = not self.issued_to
        return retdir
    
    async def set_maxes(self, newmaxes: Maxes, *, mid=True):
        """
        Changes this item's maxes... not implemented, because
        this overriding was eventually relegated to just media types.
        """
        if not isinstance(newmaxes, Maxes):
            raise TypeError('Argument must be of type Maxes')
        query = '''
        UPDATE items
           SET maxes = $1::bigint
         WHERE {}
        '''.format(
          'mid = $2::bigint'
          if mid
          else
          "title ILIKE '%' || $2::text || '%' AND author ILIKE '%' || $3::text || '%'"
          )
        await self.pool.execute(query, newmaxes.num, *([self.mid] if mid else [self.title, self.author, self.type]))
        self.maxes = newmaxes
    
    async def status(self):
        """
        Unused, but returns an item's status:
        
        whom it's checked out to,
        its due date,
        how much in fines has accrued thus far on it,
        
        and None if it's not checked out at all.
        """
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
            resp = {i: locals()[i] for i in ('issued_to', 'due_date', 'fines')}
        return resp
    
    async def pay_off(self):
        """
        Clears this item's fines.
        """
        query = '''
        UPDATE items
           SET fines = 0::numeric
         WHERE mid = $1::bigint
        '''
        return await self.pool.execute(query, self.mid)
    
    async def edit(self, title, author, genre, type_, price, length, published, isbn):
        """
        Edits all of this item's info.
        type_ is a string holding the type's name, not a MediaType object.
        """
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
        # Give priority to mediatype/mediaitem maxes over user/role maxes --
        # unless a max on the mediatype/mediaitem is 254, the 'null' code,
        # in which case refer to to user/role maxes
        if self.maxes is None:
            maxes = user.maxes
        else:
            maxes = types.SimpleNamespace(
              **{
                  k: v
                if v != 254 else
                  user.maxes.namemap[k]
                for k, v in
                  self.maxes.namemap.items()
                }
              )
        infinite = maxes.checkout_duration >= 255
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
            # ^as many weeks as specified UNLESS there is no restriction on checkout duration
            # in which case Infinity (a value postgres allows in date fields, handily enough)
            params = [query, user.uid, self.mid]
            if not infinite:
                params.append(7*maxes.checkout_duration)
            await conn.execute(*params)
            query = '''
            DELETE FROM holds
             WHERE mid = $1::bigint
               AND uid = $2::bigint
            '''
            await conn.execute(query, self.mid, user.uid)
        self.issued_to = user
        self.due_date = 'never.' if infinite else dt.datetime.utcnow() + dt.timedelta(weeks=maxes.checkout_duration)
        self.fines = 0
        self.available = False
    
    async def check_in(self):
        """
        Returns a checked-out item.
        """
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
    def maxes(self):
        """
        Because item-specific maxes were again not implemented,
        this just returns either the item's type's maxes or None
        """
        if not self.type:
            return None
        if not self._maxnum:
            return self.type.maxes
        return {k: v if v != 254 else self.type.maxes[k] for k, v in Maxes(self._maxnum).namemap.items()}

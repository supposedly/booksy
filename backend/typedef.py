"""
Just a bunch of type definitions :)
"""
import asyncio
import csv
import datetime as dt
from asyncio import iscoroutinefunction as is_coro

from .core import AsyncInit, WithLock, lockquire
from .resources import Perms, Maxes, Locks

# aiofiles isn't working for some reason so screw it I'll just do this
REGISTER_LOCATION = """
INSERT INTO locations (
              name, ip,
              color, image
            )
     SELECT $1::text, $2::text,
            $2::smallint, $3::bytea;

-- ROLES SETUP --

INSERT INTO roles (
              lid, name,
              permissions, 
              maxes, locks
              )
     SELECT currval(pg_get_serial_sequence('locations', 'lid')),
            'Admin'::text,
            32767::smallint, -- maximum smallint value, so every permission bc admin
            9223372036854775807::bigint, -- maximum bigint value, so no maxes
            9223372036854775807::bigint; -- maximum bigint value, so no locks

INSERT INTO roles (
              lid, name, 
              permissions, 
              maxes, locks
              )
     SELECT currval(pg_get_serial_sequence('locations', 'lid')),
            'Organizer'::text,
            55::smallint, -- 0110111
            1028::bigint, -- 4, 4, 0...
            5140::bigint; -- 20, 20, 0 . . .

INSERT INTO roles (
              lid, name, 
              permissions, 
              maxes, locks
              )
     SELECT currval(pg_get_serial_sequence('locations', 'lid')),
            'Subscriber'::text,
            0::smallint, -- 0000000
            514::bigint, -- 2, 2, 0 . . .
            5135::bigint; -- 15, 15, 0 . . .

-- END ROLES SETUP --

-- ACCOUNTS SETUP --

INSERT INTO members (
              username, pwhash,
              lid, rid,
              fullname,
              manages, type
              )
     SELECT $4::text, $5::bytea, -- checkout acct; username determined by backend (usually school initials plus '-checkout-XX' [unique digits])
            currval(pg_get_serial_sequence('locations', 'lid')),
            currval(pg_get_serial_sequence('roles', 'rid')),
            locations.name + ' Patron',
            false, 1
       FROM locations
      WHERE lid = currval(pg_get_serial_sequence('locations', 'lid'))

INSERT INTO members (
              username, pwhash,
              lid, rid,
              fullname, email, phone,
              manages, type
              )
     SELECT $6::text, $7::bytea, -- admin acct; username determined by backend (usually school initials + '-admin')
            currval(pg_get_serial_sequence('locations', 'lid')),
            currval(pg_get_serial_sequence('roles', 'rid')),
            $8::text, $9::text, $10::text,
            true, 0;

-- END ACCOUNTS SETUP --

SELECT currval(pg_get_serial_sequence('locations', 'lid'))
"""

class MediaType(AsyncInit, WithLock):
    props = [
      'name', 
    ]
    async def __init__(self, name, location, app):
        self.name = name
        self.app = app
        self.pool = app.pg_pool
        self.acquire = self.pool.acquire
        self.location = location if isinstance(location, Location) else await Location(int(location), self.app)
        async with self.app.pg_pool.acquire() as conn:
            maxnum = await conn.fetchval("""SELECT maxes FROM items WHERE type = $1::text""", self.name)
        self.maxes = None if maxnum is None else Maxes(maxnum)
    
    def __str__(self):
        return self.name
    
    def to_dict(self):
        return None # Not implemented?NSDFO:a;sldkjfasd
    
    @lockquire()
    async def get_items(self, conn):
        query = """
        SELECT mid
          FROM items
         WHERE media_type == $1
           AND lid = $2::bigint
        """
        return await conn.fetch(query, self.name, self.lid)
    
    @lockquire()
    async def set_maxes(self, conn, newmaxes: Maxes):
        if not isinstance(newmaxes, Maxes):
            raise TypeError('Argument must be of type Maxes')
        query = """
        UPDATE items
           SET maxes = $1::bigint
         WHERE media_type = $2::text
        """
        await conn.execute(query, newmaxes.num, self.name)
        self.maxes = newmaxes
    

class MediaItem(AsyncInit, WithLock):
    props = ['mid', 'type', 'genre',
             'isbn', 'lid', 
             'title', 'author', 'published', 
           # 'issued_to', 'due_date', 'fines',
           # 'acquired', 'maxes',
             'image']
    async def __init__(self, mid, app):
        self.mid = int(mid)
        self.app = app
        self.pool = app.pg_pool
        self.acquire = self.pool.acquire
        async with self.__class__._aiolock, self.acquire() as conn:
            query = """
            SELECT type, isbn, lid, author, title, published, genre, issued_to, due_date, fines, acquired, maxes, image
             FROM items
            WHERE mid = $1::bigint
            """
            try:
                # this is so ugly
                self._type, self.isbn, self.lid, \
                self.author, self.title,         \
                self.published, self.genre,      \
                self._issued_uid, self.due_date, \
                self.fines, self.acquired,       \
                self.maxes, self.image = await conn.fetchrow(query, self.mid)
            except TypeError:
                raise TypeError('item')
        self.location = await Location(self.lid, self.app)
        self.available = not self._issued_uid
        self.issued_to = None if self._issued_uid is None else await User(self._issued_uid, self.app)
        self.type = await MediaType(self._type, self.lid, self.app)
        self.maxes = None if self.maxes is None else Maxes(self.maxes)
    
    def __str__(self):
        return str(self.mid)
    
    def to_dict(self, verbose=False):
        if not verbose:
          retdir = {attr: str(getattr(self, attr, None)) for attr in self.props}
        else:
          pass ###
        retdir['available'] = not self.issued_to
        return retdir
    
    @lockquire()
    async def set_maxes(self, conn, newmaxes: Maxes, *, mid=True):
        if not isinstance(newmaxes, Maxes):
            raise TypeError('Argument must be of type Maxes')
        query = """
        UPDATE items
           SET maxes = $1::bigint
         WHERE {}
        """.format('mid = $2::bigint' if mid else "title ILIKE '%' || $2::text || '%' AND author ILIKE '%' || $3::text || '%'")
        await conn.execute(query, newmaxes.num, *([self.mid] if mid else [self.title, self.author]))
        self.maxes = newmaxes
    
    @lockquire(lock=False)
    async def status(self, conn, *, resp = {'issued_to': None, 'due_date': None, 'fines': None}):
        async with self.__class__._aiolock:
            query = """
            SELECT
                  CASE
                    WHEN issued_to IS NOT NULL
                    THEN (issued_to, due_date, fines)
                  END
             FROM items
            """
            check = await conn.fetchrow(query)
        try:
            issued_to, due_date, fines = check
        except ValueError:
            pass
        else:
            # hacky? probably. But it just updates, for instance,
            # resp['issued_to'] to the local value of the `issued_to' variable
            resp = {i: locals()[i] for i in resp}
        return resp
    
    @lockquire(lock=False)
    async def issue_to(self, conn, user):
        infinite = user.maxes.checkout_duration >= 255
        async with self.__class__._aiolock:
            query = """
            UPDATE members
               SET recent = $2::text
             WHERE uid = $1::bigint;
            """
            await conn.execute(query, user.uid, self.genre)
            
            query = """
            UPDATE items
               SET issued_to = $1::bigint, -- uid given as param
                   due_date = {}, -- time-allowed parameter calculated in python bc would be awful to do in plpgsql
                   fines = 0
             WHERE mid = $2::bigint;
            """.format("'Infinity'::date" if infinite else 'current_date + $4::int')
            # as many weeks as specified UNLESS the user has no restrictions on checkout time
            # in which case infinity (which postgres allows in date fields, handily enough)
            params = [query, user.uid, self.mid]
            if not infinite:
                params.append(7*user.maxes.checkout_duration)
            await conn.execute(*params)
            
        self.issued_to = user
        self.due_date = dt.datetime.max if infinite else dt.datetime.utcnow() + dt.timedelta(weeks=user.maxes.checkout_duration)
        self.fines = 0
        self.available = False
    
    @lockquire()
    async def check_in(self, conn):
        query = """
        UPDATE items
           SET issued_to = NULL,
               due_date = NULL,
               fines = NULL
         WHERE mid = $1::bigint;
        """
        await conn.execute(query, self.mid)
        self.available = True
    
    async def remove(self):
        """
        Just a proxy method for Location().remove_item(MediaItem())
        """
        await self.location.remove_item(self)


class Location(AsyncInit, WithLock):
    props = [
      'lid',
      'name', 'ip',
      'color', 'image',
      'username',
      'fine_amt', 'fine_interval'
      ]
    async def __init__(self, lid, app, *, owner=None):
        self.app = app
        self.pool = self.app.pg_pool
        self.acquire = self.pool.acquire
        self.lid = int(lid)
        async with self.__class__._aiolock, self.acquire() as conn:
            query = """SELECT name, ip, fine_amt, fine_interval, color, image FROM locations WHERE lid = $1::bigint"""
            name, ip, fine_amt, fine_interval, color, image = await conn.fetchrow(query, self.lid)
            query = """SELECT uid FROM members WHERE lid = $1 AND manages = true"""
            uid = await conn.fetchval(query, self.lid)
        self.owner = await User(uid, self.app, location=self) if owner is None else owner # just for consistency; don't think the `else` will ever be used though
        self.name = name
        self.ip = ip
        self.fine_amt = fine_amt
        self.fine_interval = fine_interval
        self.color = color
        self.image = image
    
    def __str__(self):
        return str(self.lid)
    
    def to_dict(self):
        return {i: getattr(self, i, None) for i in self.props} + {'owner_id', (self.owner).id}
    
    async def media_type(self, type_name: str):
        return await MediaType(type_name, self, self.app)
    
    @staticmethod
    def gb_image_query(title=None, author=None, isbn=None):
        """
        Searches for a book's image using the Google Books API
        """
        no_punc = str.maketrans('', '', """!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~""")
        author = author.translate(no_punc) # strip punctuation
        title = title.translate(no_punc)
        isbn = isbn.translate(no_punc)
        
        query = 'https://www.googleapis.com/books/v1/volumes?q='
        end = '&maxResults=1'
        if not all(title, author) and not isbn:
            return None
        if isbn:
            isbn = ''.join(isbn.split('-')[:2]) # get rid of trailing number and remove hyphens
            query += f'isbn:{isbn}'
        else:
            query += f'intitle:"{title.replace(" ", "+")}"+inauthor:"{author.replace(" ", "+")}"'
        return query + end
    
    @classmethod
    async def instate(cls, rqst, **kwargs):
        """In this order:"""
        props = [
          'name', 'ip', 'color',# 'image',
          'username', 'pwhash',
          'admin_username', 'admin_pwhash',
          'admin_name', 'admin_email', 'admin_phone'
          ]
        args = [kwargs.get(attr, rqst.ip if attr=='ip' else None) for attr in props]
        async with cls._aiolock, rqst.app.pg_pool.acquire() as conn:
            lid = await conn.fetchval(REGISTER_LOCATION, *args) # returns lID
        return cls(lid, rqst.app)
    
    @classmethod
    async def from_ip(cls, rqst):
        async with cls._aiolock, rqst.app.pg_pool.acquire() as conn:
            query = """
            SELECT lid
              FROM locations
             WHERE ip = $1::text
            """
            result = await conn.fetchval(query, rqst.ip)
        if result:
            return cls(result, rqst.app)
        return None
    
    @lockquire()
    async def report(self, conn, **do):
        """
        Total current checkouts / per role, total current overdues / per role,
        total current overdue fines / per role,
        current holds / per role, current available vs. unavailable holds,
        qty of each media type checked out, qty of each media type in library...
        
        Args: checkouts, overdues, fines, holds, hold_ratio, types_out, type_totals
        - each can be assigned either a bool or the string value 'per_role'
        """
        checkouts = do.pop('checkouts', False)
        overdues = do.pop('overdues', False)
        fines = do.pop('fines', False)
        holds = do.pop('holds', False)
        items = do.pop('type_totals', False)
        
        all_to_search = await self.roles()
        all_users = await self.users()
        res = {}
        
        if checkouts:
            res['checkouts'] = {}
            to_search = all_roles if checkouts == 'per_role' else all_users if checkouts == 'per_user' else {}
            key = 'name' if checkouts == 'per_role' else 'username' if checkouts == 'per_user' else None
            param = 'rid' if checkouts == 'per_role' else 'username' if checkouts == 'per_user' else None
            query = """
            SELECT count(*)/2
              FROM members, items
             WHERE items.issued_to IS NOT NULL
               AND (
                     SELECT rid
                       FROM members
                      WHERE uid = items.issued_to
                   ) {} $1::bigint
            """.format('=' if items else 'IS NOT')
            for item in to_search:
                res['checkouts'].append({item.get(key, None): await conn.fetch(query, item.get(param, None))})
        
        if overdues:
            res['overdues'] = {}
            to_search = all_roles if checkouts == 'per_role' else all_users if checkouts == 'per_user' else {}
            key = 'name' if checkouts == 'per_role' else 'username' if checkouts == 'per_user' else None
            param = 'rid' if checkouts == 'per_role' else 'username' if checkouts == 'per_user' else None
            query = """
            SELECT count(*)/2
              FROM members, items
             WHERE items.issued_to IS NOT NULL
               AND items.due_date < current_date
               AND (
                     SELECT rid
                       FROM members
                      WHERE uid = items.issued_to
                   ) {} $1::bigint
            """.format('=' if items else 'IS NOT')
            for item in to_search:
                res['overdues'].append({item.get(key, None): await conn.fetch(query, item.get(param, None))})
        
        if fines:
            res['fines'] = {}
            to_search = all_roles if checkouts == 'per_role' else all_users if checkouts == 'per_user' else {}
            key = 'name' if checkouts == 'per_role' else 'username' if checkouts == 'per_user' else None
            param = 'rid' if checkouts == 'per_role' else 'username' if checkouts == 'per_user' else None
            query = """
            SELECT sum(items.fines)
              FROM members, items
             WHERE items.issued_to IS NOT NULL
               AND (
                     SELECT rid
                       FROM members
                      WHERE uid = items.issued_to
                   ) {} $1::bigint
            """.format('=' if items else 'IS NOT')
            for item in to_search:
                res['fines'].append({item.get(key, None): await conn.fetch(query, item.get(param, None))})
        
        if holds:
            res['holds'] = {}
            to_search = all_roles if checkouts == 'per_role' else all_users if checkouts == 'per_user' else {}
            key = 'name' if checkouts == 'per_role' else 'username' if checkouts == 'per_user' else None
            param = 'rid' if checkouts == 'per_role' else 'username' if checkouts == 'per_user' else None
            query = """
            SELECT count(*)
              FROM members, holds
             WHERE (SELECT lid FROM members WHERE uid = holds.uid) = $2::bigint
               AND (
                     SELECT rid
                       FROM members
                      WHERE uid = holds.uid
                   ) {} $1::bigint
            """.format('=' if items else 'IS NOT')
            for item in to_search:
                res['holds'].append({item.get(key, None): await conn.fetch(query, item.get(param, None), self.lid)})
        
        if items:
            res['items'] = {await conn.fetch("""SELECT count(*) FROM items WHERE lid = $1::bigint""", self.lid)}
        
        return res
        
    
    @lockquire()
    async def report_names(self, do):
        """
        Current overdue fines, items per member;
        current holds available per member
        (only usernames)
        
        args: fines, items, holds
        """
        if 'fines' in do:
            pass
    
    @lockquire(lock=False)
    async def get_user(self, conn, username: str):
        async with self.__class__._aiolock:
            query = """SELECT uid FROM members WHERE username = $1::text AND lid = $2::bigint AND type = 0"""
            uid = await conn.fetchval(query)
        return await User(uid)
    
    @lockquire(lock=False)
    async def users(self, conn, roles=True, *, cont=0, max_results=20):
        users = []
        async with self.__class__._aiolock:
            for role in await self.get_roles():
                query = """SELECT uid, username, fullname FROM members WHERE lid = $1::bigint AND rid = $2::bigint AND type = 0""" \
                        """LIMIT {} OFFSET {}""".format(max_results, cont)
                users.append({role.name: await conn.fetch(query, self.lid)})
        return {res: [{j: i[j] for j in ('uid', 'username', 'fullname')} for i in users[res]] for res in users}
    
    @lockquire(lock=False)
    async def search(self, conn, *, title=None, genre=None, type_=None, author=None, cont=0, max_results=20, where_taken=None):
        search_terms = title, genre, type_, author
        async with self.__class__._aiolock:
            query = (
                """SELECT DISTINCT ON (lower(title)) title, mid, author, genre, type FROM items WHERE true """ # stupid hack coming up
                + ("""AND title ILIKE '%' || ${}::text || '%' """ if title else '')
                + ("""AND genre ILIKE '%' || ${}::text || '%' """ if genre else '')
                + ("""AND author ILIKE '%' || ${}::text || '%' """ if author else '')
                + ("""AND type ILIKE '%' || ${}::text || '%' """ if type_ else '')
                + ("""AND false """ if not any(search_terms) else '') # because 'WHERE true' otherwise returns everything if not any(search_terms)
                + ("""WHERE issued_to IS {} NULL""".format(('', 'NOT')[where_taken]) if where_taken is not None else '')
                + ("""ORDER BY title""") # just to establish a consistent order for `cont' param
                ).format(*range(1, 1+sum(map(bool, search_terms)))) \
                + ("""LIMIT {} OFFSET {}""").format(max_results, cont) # these are ok not to parameterize because they're internal
            results = await conn.fetch(query, *filter(bool, search_terms))
        if where_taken is not None: # this means I'm calling it from in here and so I probably want an actual MediaItem or at least no junk
            if max_results == 1:
                return await MediaItem(*results)
            return [i['mid'] for i in results]
        # I'd have liked to provide a full MediaItem for each result,
        # but that would take so so so so so unbearably long on Heroku's DB speeds,
        # not to mention being just pretty all-around inefficient.
        # Instead I'll have to have the app shoot a GET request to /media/info
        # for the pertinent mID when one specific item is requested.
        return [{j: i[j] for j in ('mid', 'author', 'genre', 'type')} for i in results]
    
    @lockquire(lock=False)
    async def roles(self, conn):
        async with self.__class__._aiolock:
            query = """
            SELECT rid, name, permissions AS perms, maxes, locks FROM roles WHERE lid = $1
            """
            res = [{j: i[j] for j in ('rid', 'name', 'perms', 'maxes', 'locks')} for i in await conn.fetch(query, self.lid)]
        for i in res:
            i['perms'] = Perms(i['perms']).all
            i['maxes'] = Maxes(i['maxes']).all
            i['locks'] = Locks(i['locks']).all
        return res
    
    @lockquire()
    async def add_role(self, conn, name, *, kws=None, seqs=None):
        perms, maxes, locks = Role.attrs_from(seqs=seqs, kws=kws)
        query = """
        INSERT INTO roles (
                      lid, name,
                      permissions, maxes, locks
                      )
             SELECT $1::bigint, $2::text,
                    $3::smallint, $4::bigint, $5::bigint;
        SELECT currval(pg_get_serial_sequence('roles', 'rid'))
        """
        rid = await conn.fetchval(query, self.lid, name, perms.raw, maxes.raw, locks.raw)
        return await Role(rid)
    
    @lockquire()
    async def delete_role(self, conn, rid):
        query = """DELETE FROM roles WHERE rid = $1::bigint"""
        await conn.execute(query, rid)
    
    @lockquire()
    async def edit(self, conn, to_edit, new):
        """
        :to_edit: can be any value; this method
        handles typecasting on its own.
        """
        query = f"""
        UPDATE locations
           SET {to_edit} = $1::{'bytea' if to_edit=='image' else 'text'}
         WHERE lid = $2
        """
        await conn.execute(query, new, self.lid)
    
    @lockquire(lock=False, db=False)
    async def image(self):
        raise NotImplementedError
    
    @lockquire()
    async def media_types(self, conn):
        query = """SELECT media_types FROM locations WHERE lid = $1"""
        return await conn.fetchval(query, self.lid)
    
    @lockquire()
    async def add_media_type(self, conn, type_name: str):
        query = """
        UPDATE locations
           SET media_types = array_append(media_types, $1::text)
         WHERE lid = $2::bigint
        """
        await conn.execute(query, type_name, self.lid)
        return await self.media_type(type_name)
    
    @lockquire()
    async def remove_media_type(self, conn, type_name: str):
        query = """
        UPDATE locations
           SET media_types = array_remove(media_types, $1::text)
         WHERE lid = $2::bigint
        """
        await conn.execute(query, type_name, self.lid)
        return 'success' ###
    
    @lockquire(lock=False)
    async def add_media(self, conn, **kwargs):
        kwgs = [kwargs.get(i, None) for i in ('title', 'author', 'isbn')]
        async with app.sem, app.session.get(self.gb_img_query(*kwgs)) as resp:
            rel = await resp.json()
        ident = rel.get('industryIdentifiers', None)
        img = rel.get('imageLinks', '')
        if ident:
            ident, *_ = [sub['identifier'] for sub in ident if 'isbn' in sub['type'].lower()]
        if img:
            img = img.get('smallThumbnail', img.get('thumbnail', ''))
        kwargs['isbn'] = kwargs['isbn'] or ident
        
        args = (kwargs[attr] for attr in MediaItem.props)
        async with self.__class__._aiolock:
            query = """
            INSERT INTO items (
                          type, genre,
                          isbn, lid, 
                          title, author, published,
                          acquired, maxes,
                          image
                          )
                 SELECT $2::text, $3::text,
                        $4::text, $5::bigint,
                        $6::text, $7::text, $8::date,
                        current_date, $9::bigint,
                        $1::text;
            """
            await conn.execute(query, img, *args)
    
    @lockquire()
    async def remove_item(self, conn, item):
        item = item if isinstance(item, MediaItem) else await MediaItem(item, self.app)
        query = """
        DELETE FROM items
        WHERE mid = $1
        """
        return await conn.execute(query, item.mid)
    
class Role(AsyncInit, WithLock):
    async def __init__(self, rid, app, *, location=None):
        self.app = app
        self.pool = self.app.pg_pool
        self.acquire = self.pool.acquire
        self.rid = int(rid)
        async with self.__class__._aiolock, self.acquire() as conn:
            query = """SELECT lid, name, permissions, maxes, locks FROM roles WHERE rid = $1::bigint"""
            try:
                lid, name, permbin, maxbin, lockbin = await conn.fetchrow(query, self.rid)
            except TypeError:
                raise TypeError('role')
        self.location = await Location(lid, self.app) if location is None else location
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
    
    def __str__(self):
        return str(self.rid)
    
    def to_dict(self) -> dict:
        return {'name': self.name, 'perms': self.perms.all, 'maxes': self.maxes.all, 'locks': self.locks.all}
    
    async def set_attrs(self, perms, maxes, locks):
        async with self.__class__._aiolock, self.app.pg_pool.acquire() as conn:
            query = """
            UPDATE roles
               SET permissions = $2::smallint,
                   maxes = $3::bigint,
                   locks = $4::bigint
             WHERE rid = $1::bigint
            """
            await conn.execute(query, self.rid, perms.raw, maxes.raw, locks.raw)
    
    @staticmethod
    def attrs_from(*, seqs=None, kws=None):
        if kws is None:
            perms = Perms.from_seq(seqs['perms'])
            maxes = Maxes.from_seq(seqs['maxes'])
            locks = Locks.from_seq(seqs['locks'])
        else:
            perms = Perms.from_kwargs(**kws['perms'])
            maxes = Maxes.from_kwargs(**kws['maxes'])
            locks = Locks.from_kwargs(**kws['locks'])
        return perms, maxes, locks
    
    
    @property
    def perms(self):
        return Perms(self._permbin)
    
    @property
    def maxes(self):
        return Maxes(self._maxbin)
    
    @property
    def locks(self):
        return Locks(self._lockbin)
    
class User(AsyncInit, WithLock):
    async def __init__(self, uid, app, *, location=None, role=None):
        self.app = app
        self.pool = self.app.pg_pool
        self.acquire = self.pool.acquire
        self.user_id = self.uid = int(uid)
        async with self.__class__._aiolock, self.acquire() as conn:
            query = """SELECT username, fullname, lid, rid, manages, email, phone, type, recent, perms, maxes, locks FROM members WHERE uid = $1::bigint;"""
            username, name, lid, rid, manages, email, phone, self._type, recent, permbin, maxbin, lockbin = await conn.fetchrow(query, self.uid)
            query = """SELECT count(*) FROM holds WHERE uid = $1::bigint"""
            holds = await conn.fetchval(query, self.uid)
            query = """SELECT count(*) FROM items WHERE issued_to = $1::bigint"""
            self.num_checkouts = await conn.fetchval(query, self.uid)
        self.location = await Location(lid, self.app) if location is None else location
        self.role = await Role(rid, self.app, location=self.location) if role is None else role
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
        rel['can_return_items'] = self.perms.can_return_items
        return rel
    
    @property
    def cannot_check_out(self):
        if self.maxes.checkout_duration and self.checkouts_left:
            # success
            return False
        ret = "You can't check anything out at the moment."
        + ('' if able[0] else ' (currently using {} of {} allowed concurrent '
                                    'checkouts)'.format(self.num_checkouts,
                                                        self.locks.checkouts)
               )
        + '' if able[1] else ' (allowed to check out for 0 weeks)'
        return ret
    
    @classmethod
    async def create(cls, app, **kwargs):
        props = ['username', 'pwhash', 'lid', 'email', 'phone']
        async with cls._aiolock, app.pg_pool.acquire() as conn:
            query = """
            INSERT INTO members (
                          username, pwhash,
                          lid,
                          email, phone
                          )
                 SELECT $1::text, $2::bytea,
                        $3::bigint,
                        $4::text, $5::text
            """
            await conn.execute(query, *(kwargs[i] for i in props))
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
        async with cls._aiolock, app.pg_pool.acquire() as conn:
            query = """SELECT uid FROM members WHERE username = $1::text AND lid = $2::bigint"""
            uid = await conn.fetchval(query, username, location.lid)
        return await cls(uid, app)
    
    async def edit_perms(self, **new):
        return self.perms.edit(**new) # returns None
    
    async def edit_perms_from_seq(self, **new):
        return self.perms.edit_from_seq(**new) # returns None
    
    @lockquire()
    async def notifs(self, conn):
        # could probably do this in one line
        holds = await conn.fetchval("""SELECT count(*) FROM holds WHERE uid = $1::bigint""", self.uid)
        fines = await conn.fetchval("""SELECT sum(fines) AS fines FROM items WHERE issued_to = $1::bigint""", self.uid)
        overdue = await conn.fetchval("""SELECT count(*) AS overdue FROM items WHERE due_date < current_date;""")
        
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
    
    @lockquire()
    async def hold(self, conn, *, item=None, title=None):
        if item is None:
            item = await self.location.search(title=title, max_results=1, where_available=False)
        if await conn.fetchval("""SELECT count(*) FROM members WHERE lower(title) = $1::text AND issued_to IS NULL""", title):
            return 'Item is already available!'
        query = """
        INSERT INTO holds
          (uid, mid, created)
        SELECT $1::bigint, $2::bigint, current_date
        """
        await conn.execute(query, self.uid, item.mid)
    
    @lockquire()
    async def edit(self, conn, to_edit, new):
        query = f"""
        UPDATE members
           SET {to_edit} = $1::text
         WHERE lid = $2
        """
        await conn.execute(query, new, self.lid)
    
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

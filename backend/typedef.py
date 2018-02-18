"""
Just a bunch of type definitions :)
"""
import asyncio
import functools
import io
import datetime as dt
from decimal import Decimal
from asyncio import iscoroutinefunction as is_coro

import asyncpg
import pandas

from .core import AsyncInit
from .resources import Perms, Maxes, Locks

class MediaType(AsyncInit):
    """
    Defines a kind of media, e.g. books or audiotapes.
    Currently unused but I very much hope to implement it at a later date.
    """
    props = [
      'name', 
    ]
    async def __init__(self, name, location, app):
        self.name = name
        self.app = app
        self.pool = app.pg_pool
        self.acquire = self.pool.acquire
        self.location = location if isinstance(location, Location) else await Location(int(location), self.app)
        maxnum = await self.pool.fetchval('''SELECT maxes FROM items WHERE type = $1::text''', self.name)
        self.maxes = None if maxnum is None else Maxes(maxnum)
    
    def __str__(self):
        return self.name
    
    def to_dict(self):
        return None # Not implemented
    
    async def get_items(self):
        query = '''
        SELECT mid
          FROM items
         WHERE media_type == $1
           AND lid = $2::bigint
        '''
        return await self.pool.fetch(query, self.name, self.lid)
    
    async def set_maxes(self, newmaxes: Maxes):
        if not isinstance(newmaxes, Maxes):
            raise TypeError('Argument must be of type Maxes')
        query = '''
        UPDATE items
           SET maxes = $1::bigint
         WHERE media_type = $2::text
        '''
        await self.pool.execute(query, newmaxes.num, self.name)
        self.maxes = newmaxes
    

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


class Location(AsyncInit):
    """
    Defines a library. Instance methods:
        
    """
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
        async with self.acquire() as conn:
            query = '''SELECT name, ip, fine_amt, fine_interval, color, image FROM locations WHERE lid = $1::bigint'''
            name, ip, fine_amt, fine_interval, color, image = await conn.fetchrow(query, self.lid)
            query = '''SELECT uid FROM members WHERE lid = $1 AND manages = true'''
            ouid = await conn.fetchval(query, self.lid)
        self.owner = await User(ouid, self.app, location=self) if owner is None else owner # just for consistency; don't think the `else` will ever be used though
        self.name = name
        self.ip = ip
        self.fine_amt = fine_amt
        self.fine_interval = fine_interval
        self.color = color
        self.image = image
    
    def __str__(self):
        """Unused but eh"""
        return str(self.lid)
    
    def to_dict(self):
        return {i: getattr(self, i, None) for i in self.props} + {'owner_id', (self.owner).id}
    
    async def media_type(self, type_name: str):
        return await MediaType(type_name, self, self.app)
    
    @staticmethod
    def gb_image_query(title='', author='', isbn=''):
        """
        Generates a query to find a book's image using the Google Books API
        """
        # first two args map to each other; str.maketrans('ab', 'xy') turns a->x and b->y
        # third arg is chars to map to nothing (i.e. to delete)
        # so i'm just deleting (almost) all punctuation
        no_punc = str.maketrans('', '', """!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~""")
        author = author.translate(no_punc)
        title = title.translate(no_punc)
        isbn = isbn.translate(no_punc)
        
        query = 'https://www.googleapis.com/books/v1/volumes?q='
        end = '&maxResults=1'
        if not all((title, author)) and not isbn:
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
        with open('./backend/sql/register_location.sql') as register_location:
            lid = await rqst.app.pg_pool.fetchval(register_location.read(), *args) # returns lID
        return cls(lid, rqst.app)
    
    @classmethod
    async def from_ip(cls, rqst):
        query = '''
        SELECT lid
          FROM locations
         WHERE ip = $1::text
        '''
        result = await rqst.app.pg_pool.fetchval(query, rqst.ip)
        if result:
            return cls(result, rqst.app)
        return None
    
    async def members_from_csv(self, file, rid):
        """
        Batch addition of members.
        
        Input MUST be in the form of a standards-compliant
        CSV file WITH a header, and columns in this order:
        
        fullname,username,password
        """
        def fix(df):
            """
            Fix+reorder all necessary attributes to match DB in the user CSV dataframe.
            """
            # to ensure the generated salt is random, redo it for every row
            df.password.apply(df.password.str.encode, 'utf-8')#functools.partial(bcrypt.hashpw, salt=lambda: bcrypt.gensalt(12)))
            # assign the given role ID to all members
            df['rid'] = int(rid)
            # Rearrange to remain compliant with asyncpg's copy_to_table
            # (that is, to fit with my table setup, because this method
            # accepts no 'ordering' argument)
            # Unfortunately this means that it needs to be returned, because
            # while attributes can be modified 'in-place', the entire object
            # cannot
            return df[['rid', 'fullname', 'username', 'password']]
        # I'm using the 'app.ppe' ProcessPoolExecutor instead of the 'None'
        # default ThreadPoolExecutor because these are CPU-bound operations
        # and not I/O-bound (which means you get better performance with a
        # ProcessPoolExecutor)
        
        # load the file as a Pandas dataframe
        df = await self.app.aexec(None, pandas.read_csv, file)
        # encode password column to make it usable for bcrypt
        df.password = self.app.aexec(None, df.password.str.encode, 'utf-8')
        df = await self.app.aexec(None, fix, df)
        with io.BytesIO() as bIO:
            await self.app.aexec(None, df.to_csv, bIO)
            bIO.seek(0)
            async with self.acquire() as conn:
                return await conn.copy_to_table(
                  'members',
                  source=bIO,
                  columns=['rid', 'fullname', 'username', 'pwhash'],
                  format='csv',
                  header=True)
        # w amre la alla that it works
    
    async def report(self, **do):
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
        
        all_roles = await self.roles()
        all_users = await self.members(by_role=False)
        res = {}
        
        if checkouts:
            to_search = all_roles if checkouts == 'per_role' else all_users if checkouts == 'per_user' else [{}]
            column = 'checkouts', checkouts
            key = 'name' if checkouts == 'per_role' else 'username' if checkouts == 'per_user' else None
            param = 'rid' if checkouts == 'per_role' else 'username' if checkouts == 'per_user' else None
            query = '''
            SELECT DISTINCT ON (items.mid) items.title
              FROM members, items
             WHERE items.issued_to IS NOT NULL
            '''
        if overdues:
            to_search = all_roles if overdues == 'per_role' else all_users if overdues == 'per_user' else [{}]
            column = 'overdues', overdues
            key = 'name' if overdues == 'per_role' else 'username' if overdues == 'per_user' else None
            param = 'rid' if overdues == 'per_role' else 'username' if overdues == 'per_user' else None
            query = '''
            SELECT DISTINCT ON (items.mid) items.title
              FROM members, items
             WHERE items.issued_to IS NOT NULL
               AND items.due_date < current_date
            '''
        
        if fines:
            to_search = all_roles if fines == 'per_role' else all_users if fines == 'per_user' else [{}]
            column = 'fines', fines
            key = 'name' if fines == 'per_role' else 'username' if fines == 'per_user' else None
            param = 'rid' if fines == 'per_role' else 'username' if fines == 'per_user' else None
            query = '''
            SELECT sum(items.fines)
              FROM members, items
             WHERE items.issued_to IS NOT NULL
            '''
        
        if holds:
            to_search = all_roles if holds == 'per_role' else all_users if holds == 'per_user' else [{}]
            column = 'holds', holds
            key = 'name' if holds == 'per_role' else 'username' if holds == 'per_user' else None
            param = 'rid' if holds == 'per_role' else 'username' if holds == 'per_user' else None
            query = '''
            SELECT DISTINCT ON (items.mid) items.title
              FROM members, holds, items
             WHERE (SELECT lid FROM members WHERE uid = holds.uid) = ${}::bigint
            '''.format(1 if holds == 'all' else 2)
        
        async with self.acquire() as conn:
            if any((checkouts, overdues, fines, holds)):
                res[column[0]] = []
                query += ('''
                 AND (
                       SELECT username
                         FROM members
                        WHERE uid = items.issued_to
                     ) = $1::text
                ''' if column[1] == 'per_user' else '''
                 AND (
                       SELECT rid
                         FROM members
                        WHERE uid = items.issued_to
                     ) = $1::bigint
                ''' if column[1] == 'per_role' else '''
                 AND (
                       SELECT username
                         FROM members
                        WHERE uid = items.issued_to
                     ) IS NOT NULL
                ''')
                for item in to_search:
                    search = (
                      conn.fetch(query, self.lid) if holds and holds == 'all' else
                      conn.fetch(query, item.get(param, None), self.lid) if holds else
                      conn.fetch(query, item.get(param, None)) if column[1] != 'all' else
                      conn.fetch(query)
                    )
                    res[column[0]].append({'ident': item.get(key, None), 'res': await search})
            if items:
                # unused
                # I'm not even sure what I was trying to do, in retrospect. Why is this a set?
                res['items'] = {await conn.fetchval('''SELECT count(*) FROM items WHERE lid = $1::bigint''', self.lid)}
        return res
    
    async def get_user(self, username: str):
        query = '''SELECT uid FROM members WHERE username = $1::text AND lid = $2::bigint AND type = 0'''
        uid = await self.pool.fetchval(query)
        return await User(uid, self.app, location=self)
    
    async def members(self, by_role=True, *, limit=True, cont=0, max_results=15):
        roles = {}
        async with self.acquire() as conn:
            if by_role:
                for role in await self.roles():
                    query = '''SELECT uid, username, fullname FROM members WHERE lid = $1::bigint AND rid = $2::bigint AND type = 0''' \
                            + ('''LIMIT {} OFFSET {}'''.format(max_results, cont) if limit else '')
                    roles[role['name']] = (role['rid'], await conn.fetch(query, self.lid, role['rid']))
                return [{'name': role, 'rid': rid, 'data': [{j: i[j] for j in ('uid', 'username', 'fullname')} for i in user]} for role, (rid, user) in roles.items()]
            query = '''SELECT uid, username, fullname FROM members WHERE lid = $1::bigint AND type = 0''' \
                    + ("""LIMIT {} OFFSET {}""".format(max_results, cont) if limit else '')
            return [{j: i[j] for j in ('uid', 'username', 'fullname')} for i in await conn.fetch(query, self.lid)]
    
    async def add_member(self, username, pwhash: "hash this beforehand", rid, fullname):
        # the following is for my own at-home testing (I can't download libffi, which
        # bcrypt depends on); it will never EVER be triggered in a prod environment.
        if isinstance(pwhash, str): pwhash = pwhash.encode('utf-8')
        query = '''
        INSERT INTO members (
                  username, pwhash,
                  lid, rid,
                  fullname, email, phone,
                  manages, type
                  )
         SELECT $1::text, $2::bytea,
                $3::bigint, -- self.lid
                $4::bigint,
                $5::text,
                NULL, NULL, -- not going to do these
                false, 0;
        '''
        await self.pool.execute(query, username, pwhash, self.lid, rid, fullname)
    
    async def remove_member(self, uid):
        # hm. should this be a method of User?
        query = '''
        DELETE FROM members
              WHERE uid = $1::bigint
        '''
        return await self.pool.execute(query, uid)
    
    async def search(self, *, title=None, genre=None, type_=None, author=None, cont=0, max_results=20, where_taken=None):
        search_terms = title, genre, author, type_
        query = (
              '''SELECT DISTINCT ON (lower(title)) title, mid, author, genre, type, image FROM items WHERE true ''' # stupid hack coming up
              + ('''AND title ILIKE '%' || ${}::text || '%' ''' if title else '')
              + ('''AND genre ILIKE '%' || ${}::text || '%' ''' if genre else '')
              + ('''AND author ILIKE '%' || ${}::text || '%' ''' if author else '')
              + ('''AND type ILIKE '%' || ${}::text || '%' ''' if type_ else '')
              + ('''AND false ''' if not any(search_terms) else '') # because 'WHERE true' otherwise returns everything if not any(search_terms)
              + ('''AND issued_to IS {} NULL '''.format(('', 'NOT')[where_taken or 0]))
              + ('''ORDER BY lower(title) ''') # just to establish a consistent order for `cont' param
            ).format(*range(1, 1+sum(map(bool, search_terms)))) \
            + ('''LIMIT {} OFFSET {} ''').format(max_results, cont) # these are ok not to parameterize because they're internal
        results = await self.pool.fetch(query, *filter(bool, search_terms))
        if where_taken is not None: # this means I'm calling it from in here and so I probably want an actual MediaItem or at least no junk
            if max_results == 1:
                return await MediaItem(results[0]['mid'], app=self.app)
            return [i['mid'] for i in results]
        # I'd have liked to provide a full MediaItem for each result,
        # but that would take so so so so so unbearably long on Heroku's DB speeds,
        # not to mention being just pretty all-around inefficient.
        # Instead I'll have the app shoot a GET request to /media/info
        # for the pertinent mID when one specific item is requested.
        return [{j: i[j] for j in ('mid', 'title', 'author', 'genre', 'type', 'image')} for i in results]
    
    async def roles(self):
        async with self.acquire() as conn:
            query = '''
            SELECT rid, name, permissions AS perms,  maxes, locks FROM roles WHERE lid = $1
            '''
            q2ery = '''SELECT count(*) FROM members WHERE rid = $1::bigint'''
            res = [{j: i[j] for j in ('rid', 'name', 'perms', 'maxes', 'locks')} for i in await conn.fetch(query, self.lid)]
            for i in res:
                i['perms'] = Perms(i['perms']).all
                i['maxes'] = Maxes(i['maxes']).all
                i['locks'] = Locks(i['locks']).all
                i['count'] = await conn.fetchval(q2ery, i['rid'])
        return res
    
    async def add_role(self, name, *, kws=None, seqs=None):
        perms, maxes, locks = Role.attrs_from(seqs=seqs, kws=kws)
        async with self.acquire() as conn:
            query = '''
            INSERT INTO roles (
                          lid, name,
                          permissions, maxes, locks
                          )
                 SELECT $1::bigint, $2::text,
                        $3::smallint, $4::bigint, $5::bigint;
            '''
            await conn.execute(query, self.lid, name, perms.raw, maxes.raw, locks.raw)
            rid = await conn.fetchval('''SELECT currval(pg_get_serial_sequence('roles', 'rid'))''')
        return await Role(rid, self.app, location=self)
    
    async def items(self, *, cont=0, max_results=5):
        query = '''
        SELECT mid, type, title, author, genre, image
          FROM items
         WHERE lid = $1::bigint
      ORDER BY title
         LIMIT {}
        OFFSET {}
        '''.format(max_results, cont)
        res = await self.pool.fetch(query, self.lid)
        return [{j: i[j] for j in ('mid', 'type', 'title', 'author', 'genre', 'image')} for i in res]
    
    async def edit(self, to_edit, new):
        """
        This is insecure. Very insecure.
        """
        to_edit = to_edit.replace('=', '') # should take care of it but still ew
        query = f'''
        UPDATE locations
           SET {to_edit} = $1::{'bytea' if to_edit=='image' else 'text'}
         WHERE lid = $2
        '''
        await self.pool.execute(query, new, self.lid)
    
    async def image(self):
        raise NotImplementedError
        # and may never be ...
    
    async def media_types(self):
        query = '''SELECT media_types FROM locations WHERE lid = $1::bigint'''
        # fetchval because it's an array (not a bunch of records)
        return await self.pool.fetchval(query, self.lid)
    
    async def add_media_type(self, type_name: str):
        query = '''
        UPDATE locations
           SET media_types = array_append(media_types, $1::text)
         WHERE lid = $2::bigint
        '''
        await self.pool.execute(query, type_name, self.lid)
        return await self.media_type(type_name)
    
    async def remove_media_type(self, type_name: str):
        query = '''
        UPDATE locations
           SET media_types = array_remove(media_types, $1::text)
         WHERE lid = $2::bigint
        '''
        await self.pool.execute(query, type_name, self.lid)
        return 'success' ###
    
    async def genres(self):
        query = '''
        SELECT DISTINCT lower(genre) AS genre FROM items WHERE lid = $1::bigint ORDER BY lower(genre)
        '''
        return [i['genre'] for i in await self.pool.fetch(query, self.lid)]
    
    async def add_media(self, title, author, published, type_, genre, isbn, price, length):
        ident = img = ''
        try:
            async with self.app.sem, self.app.session.get(self.gb_image_query(title, author)) as resp:
                rel = (await resp.json())['items'][0]['volumeInfo']
        except KeyError:
            pass
        else:
            ident = rel.get('industryIdentifiers', None)
            img = rel.get('imageLinks', '')
            if ident:
                # get isbn
                ident, *_ = [i['identifier'] for i in ident if 'isbn' in i['type'].lower()]
            if img:
                img = img.get('smallThumbnail', img.get('thumbnail', '')).replace('http://', 'https://')
        args = type_, genre, ident or isbn, self.lid, title, author, int(published), round(Decimal(price), 2), int(length)
        async with self.acquire() as conn:
            query = '''
            INSERT INTO items (
                          type, genre,
                          isbn, lid, 
                          title, author, published,
                          price, length,
                          acquired, maxes,
                          image
                          )
                 SELECT $2::text, $3::text,
                        $4::text, $5::bigint,
                        $6::text, $7::text, $8::int,
                        $9::numeric, $10::int,
                        current_date, NULL,
                        $1::text;
            '''
            await conn.execute(query, img, *args)
            mid = await conn.fetchval('''SELECT currval(pg_get_serial_sequence('items', 'mid'))''')
        return await MediaItem(mid, self.app)
    
    async def remove_item(self, item):
        item = item if isinstance(item, MediaItem) else await MediaItem(item, self.app)
        query = '''
        DELETE FROM items
        WHERE mid = $1::bigint
        '''
        return await self.pool.execute(query, item.mid)
    
class Role(AsyncInit):
    async def __init__(self, rid, app, *, location=None):
        self.app = app
        self.pool = self.app.pg_pool
        self.acquire = self.pool.acquire
        self.rid = int(rid)
        query = '''SELECT lid, name, permissions, maxes, locks FROM roles WHERE rid = $1::bigint'''
        try:
            lid, name, permbin, maxbin, lockbin = await self.pool.fetchrow(query, self.rid)
        except TypeError:
            raise TypeError('role') # to be fed back to application as '{role} does not exist!'
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
        return {
          'rid': self.rid,
          'name': self.name,
          'perms': self.perms.all,
          'maxes': self.maxes.all,
          'locks': self.locks.all
          }
    
    async def set_attrs(self, perms, maxes, locks, name):
        query = '''
        UPDATE roles
           SET name = $2::text,
               permissions = $3::smallint,
               maxes = $4::bigint,
               locks = $5::bigint
         WHERE rid = $1::bigint
        '''
        await self.pool.execute(query, self.rid, name, perms.raw, maxes.raw, locks.raw)
    
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
    
    
    async def delete(self):
        query = '''DELETE FROM roles WHERE rid = $1::bigint'''
        await self.pool.execute(query, self.rid)
    
    async def num_members(self):
        query = '''SELECT count(*) FROM members WHERE rid = $1::bigint'''
        return await self.pool.fetchval(query, self.rid)
    
    @property
    def perms(self):
        return Perms(self._permbin)
    
    @property
    def maxes(self):
        return Maxes(self._maxbin)
    
    @property
    def locks(self):
        return Locks(self._lockbin)
    
class User(AsyncInit):
    async def __init__(self, uid, app, *, location=None, role=None):
        self.app = app
        self.pool = self.app.pg_pool
        self.acquire = self.pool.acquire
        try:
            self.user_id = self.uid = int(uid)
        except TypeError:
            raise ValueError('No user exists with this username!')
        async with self.acquire() as conn:
            query = '''SELECT username, fullname, lid, rid, manages, email, phone, type, recent, perms, maxes, locks FROM members WHERE uid = $1::bigint;'''
            username, name, lid, rid, manages, email, phone, self._type, recent, permbin, maxbin, lockbin = await conn.fetchrow(query, self.uid)
            query = '''SELECT count(*) FROM holds WHERE uid = $1::bigint'''
            holds = await conn.fetchval(query, self.uid)
            query = '''SELECT count(*) FROM items WHERE issued_to = $1::bigint'''
            self.num_checkouts = await conn.fetchval(query, self.uid)
        self.location = await Location(lid, self.app) if location is None else location
        self.role = await Role(rid, self.app, location=self.location) if role is None else role
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
    
    async def edit_perms(self, **new):
        return self.perms.edit(**new) # returns None
    
    async def edit_perms_from_seq(self, **new):
        return self.perms.edit_from_seq(**new) # returns None
    
    async def notifs(self):
        async with self.acquire() as conn:
            # could probably do this in one line
            holds = await conn.fetchval('''SELECT count(*) FROM holds WHERE uid = $1::bigint''', self.uid)
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

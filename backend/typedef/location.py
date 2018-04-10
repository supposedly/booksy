import aiofiles
import functools
import io
import random
import uuid
import string
from decimal import Decimal

import pandas

from ..core import AsyncInit
from ..attributes import Perms, Maxes, Locks


# first two args map to each other; str.maketrans('ab', 'xy') turns a->x and b->y
# third arg is chars to map to nothing (i.e. to delete)
# so i'm just deleting (almost) all punctuation
GBQUERY = str.maketrans('', '', """!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~""")
NO_PUNC = str.maketrans('', '', string.punctuation)


#################################################
try:
    import bcrypt
except ModuleNotFoundError: # means I'm testing (can't access app.config.TESTING from here) (don't have libffi/bcrypt on home PC)
    import types
    def __hashpw(pw: bytes, *_, **__):
        return pw
    def __gensalt(*_, **__):
        return 0
    bcrypt = types.SimpleNamespace(
      hashpw=__hashpw,
      gensalt=__gensalt
    )
#################################################



class Location(AsyncInit):
    """
    Defines a library, or 'location'.
    
    owner         (User):     Admin account of location.
    image         (BytesIO):  (UNUSED) The location's "display picture".
    fine_amt      (Decimal):  How much a user is charged each interval for keeping an overdue item.
    name          (str):      Location's name.
    ip            (str):      (UNUSED) Location's IP address/block; intended to allow members to not enter location ID if signing in while physically at it.
    fine_interval (int):      How often overdue fines are compounded.
    _color        (int):      Raw number representing location's preferred color/scheme. Private variable.
    color         (str):      _color, but string-formatted to work as an input to ngx-color-picker.
    """
    props = [
      'lid',
      'name',
      'ip',
      'color', '_color',
      'fine_amt',
      'fine_interval'
      ]
    
    @staticmethod
    def do_imports():
        global Role, MediaItem, MediaType, User
        from . import Role, MediaItem, MediaType, User
    
    async def __init__(self, lid, app, *, owner=None):
        self._app = app
        self.pool = self._app.pg_pool
        self.acquire = self.pool.acquire
        self.lid = int(lid)
        async with self.acquire() as conn:
            query = '''SELECT name, ip, fine_amt, fine_interval, color, image FROM locations WHERE lid = $1::bigint'''
            name, ip, fine_amt, fine_interval, color, image = await conn.fetchrow(query, self.lid)
            query = '''SELECT uid FROM members WHERE lid = $1 AND manages = true'''
            ouid = await conn.fetchval(query, self.lid)
        self.owner = await User(ouid, self._app, location=self) if owner is None else owner # just for consistency; don't think the `else` will ever be used though
        self.name = name
        self.ip = ip
        self.fine_amt = fine_amt
        self.fine_interval = fine_interval
        self._color = color or 0xf7f7f7
        self.color = '#' + hex(color)[2:] if color else '#f7f7f7'
        self.image = image
    
    def to_dict(self):
        return {i: getattr(self, i, None) for i in self.props}
    
    @staticmethod
    def gb_image_query(title='', author='', isbn=''):
        """
        Generates a query to find a book's image using the Google Books API
        """
        author = author.translate(GBQUERY)
        title = title.translate(GBQUERY)
        isbn = isbn.translate(GBQUERY)
        
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
    
    @staticmethod
    async def prelim_signup(rqst, email, locname, color, adminname):
        """
        Stores the given info to the 'signups' table's purgatory until
        they verify.
        Also generates admin+checkout usernames based on the location name.
        """
        # Some Person's Full Name High School
        # ->
        # spnfh
        # (initials up to the 5th word)
        base = ''.join(word[0] for word in locname.split(None, 4)).lower()
        chk_usr, admin_usr = f'{base}-checkout', f'{base}-admin'
        token = uuid.uuid4().hex
        
        query = '''
        INSERT INTO signups (
          date, key, email,
          name, color,
          username, -- for checkout acct
          adminname,
          adminuser -- for admin acct (ofc)
        )
        SELECT current_date, $1::text, $2::text,
               $3::text, $4::int,
               $5::text,
               $6::text,
               $7::text
        '''
        await rqst.app.pg_pool.execute(
          query,
          token, email,
          locname, color,
          chk_usr,
          adminname,
          admin_usr
          )
        return token
    
    @classmethod
    async def instate(cls, rqst, token, checkoutpw, adminpw):
        """Takes a location from signup-table purgatory to the main DB"""
        # args in this order:
        props = [
          'name', 'ip', 'color',
          'adminuser', 'adminpwhash',         # these are for admin account
          'adminname', 'email', 'adminphone', # these aren't used, especially adminphone
          'username', 'pwhash'                # these are for the checkout account
          ]
        fetch = dict(
          await rqst.app.pg_pool.fetchrow('''
            SELECT email, name, color,
                   username, pwhash,
                   adminname,
                   adminuser, adminpwhash
              FROM signups
             WHERE key = $1::text
            ''', token))
        fetch['ip'] = rqst.ip
        fetch['pwhash'] = await rqst.app.aexec(None, bcrypt.hashpw, checkoutpw.encode(), bcrypt.gensalt(12))
        fetch['adminpwhash'] = await rqst.app.aexec(None, bcrypt.hashpw, adminpw.encode(), bcrypt.gensalt(12))
        
        args = [fetch.get(attr, rqst.ip if attr=='ip' else None) for attr in props]
        async with rqst.app.pg_pool.acquire() as conn:
            async with conn.transaction(), aiofiles.open('./backend/sql/register_location.sql') as f:
                # Transaction because we want to roll everything back if something goes wrong
                for query in (await f.read()).split(';'):
                    stmt = await conn.prepare(query)
                    # This'd be the same sort of weirdness as what's
                    # in location.search(), although slightly saner.
                    #
                    # asyncpg again complains w/error if passed more
                    # parameters than a given query's requesting, so
                    # we get the exact amount of params it wants rn:
                    numparams = len(stmt.get_parameters())
                    # Then execute it with that many parameters from
                    # the beginning of the arguments list:
                    lid = await stmt.fetchval(*args[:numparams]) # returns lID at end because run with fetchval
                    # ...and, finally, strip the params we just used
                    # from it.
                    args = args[numparams:]
        return fetch['name'], lid, fetch['username'], fetch['adminuser']
        # return cls(lid, rqst.app)
    
    @classmethod
    async def from_ip(cls, rqst):
        """
        Unused, but intended to help implement the 'no lID if at location'
        thing.
        """
        query = '''
        SELECT lid
          FROM locations
         WHERE ip = $1::text
        '''
        result = await rqst.app.pg_pool.fetchval(query, rqst.ip)
        if result:
            return await cls(result, rqst.app)
        return None
    
    async def members_from_csv(self, file, rid):
        """
        Batch addition of members.
        
        Input MUST be in the form of a standards-compliant
        CSV file WITH a header, and columns in this order:
        
        fullname,username,password
        
        (NOT IMPLEMENTED)
        """
        def fix(df):
            """
            Fix+reorder all necessary attributes to match DB in the user CSV dataframe.
            """
            df.password = df.password.apply(lambda pw: bcrypt.hashpw(pw, salt=bcrypt.gensalt(12)))
            # assign the given role ID to all members
            df['rid'] = int(rid)
            # Rearrange to remain compliant with asyncpg's copy_to_table
            # (that is, to fit with my table setup, because this method
            # accepts no 'ordering' argument)
            # Unfortunately this means that it needs to be returned, because
            # while attributes can be modified 'in-place', the entire object
            # cannot
            return df[['rid', 'fullname', 'username', 'password']]
        
        # load the file as a Pandas dataframe
        df = await self._app.aexec(None, pandas.read_csv, file)
        # encode password column to make it usable for bcrypt
        df.password = await self._app.aexec(None, df.password.str.encode, 'utf-8')
        df = await self._app.aexec(None, fix, df)
        with io.BytesIO() as bIO:
            await self._app.aexec(None, df.to_csv, bIO)
            bIO.seek(0)
            async with self.acquire() as conn:
                return await conn.copy_to_table(
                  'members',
                  source=bIO,
                  columns=['rid', 'fullname', 'username', 'pwhash'],
                  format='csv',
                  header=True
                  )
        # w amre la alla that it works
    
    async def report(self, **do):
        """
        `do` will be in the format:
        
        {'checkouts': 'per_user', 'overdues': False, 'fines': False, 'holds': False, 'items': False}
        
        or something similar, with only one of the values being non-False. This will be the value to
        generate a report for.
        """
        def query_setup(name: str, var: object):
            num = (var == 'per_user') or 2*(var == 'per_role')
            
            to_search = search_opts[num]
            # all_roles if var == 'per_role' else all_users if var == 'per_user' else [{}]
            key = (None, 'username', 'name')[num]
            # 'name' if var == 'per_role' else 'username' if var == 'per_user' else None
            param = (None, 'username', 'rid')[num]
            # 'rid' if var == 'per_role' else 'username' if var == 'per_user' else None
            return to_search, key, param
        
        if do['checkouts']:
            col = 'checkouts'
            query = '''
            SELECT DISTINCT ON (items.mid) items.title || ' (#' || items.mid || '; ' || items.due_date || ')' AS title
              FROM members, items
             WHERE items.issued_to IS NOT NULL
            '''
        elif do['overdues']:
            col = 'overdues'
            query = '''
            SELECT DISTINCT ON (items.mid) items.title || ' (#' || items.mid || '; ' || items.due_date || ')' AS title
              FROM members, items
             WHERE items.issued_to IS NOT NULL
               AND items.due_date < current_date
            '''
        elif do['fines']:
            col = 'fines'
            query = '''
            SELECT '$' || items.fines AS fines
              FROM members, items
             WHERE items.issued_to IS NOT NULL
               AND items.fines > 0
               AND members.uid = items.issued_to
            '''
        elif do['holds']:
            col = 'holds'
            query = '''
            SELECT items.title
              FROM items, holds
             WHERE holds.mid = items.mid
            '''
        res = {col: []}
        umn = do[col]
        query += ('''
         AND (
               SELECT username
                 FROM members
                WHERE uid = {}
             ) = $1::text
        ''' if umn == 'per_user' else '''
         AND (
               SELECT rid
                 FROM members
                WHERE uid = {}
             ) = $1::bigint
        ''' if umn == 'per_role' else '''
         AND (
               SELECT username
                 FROM members
                WHERE uid = {}
             ) IS NOT NULL
        ''').format('holds.uid' if col == 'holds' else 'items.issued_to')
        search_opts = [{}], await self.members(by_role=False), await self.roles()
        to_search, key, param = query_setup(col, umn)
        async with self.acquire() as conn:
            for obj in to_search:
                search = (
                  conn.fetch(query) if umn == 'all' else
                  conn.fetch(query, obj.get(param, None))
                )
                res[col].append({'ident': obj.get(key, 'All users'), 'res': await search})
        return res
    
    async def get_user(self, username: str):
        """
        Grabs a user object from its username.
        """
        query = '''SELECT uid FROM members WHERE username = $1::text AND lid = $2::bigint AND type = 0'''
        uid = await self.pool.fetchval(query)
        return await User(uid, self._app, location=self)
    
    async def members(self, by_role=True, *, limit=True, cont=0, max_results=15):
        """
        Serves all of this location's members.
        """
        roles = {}
        async with self.acquire() as conn:
            if by_role:
                for role in await self.roles():
                    query = '''SELECT uid, username, fullname FROM members WHERE lid = $1::bigint AND rid = $2::bigint AND type = 0''' \
                            + ('''LIMIT {} OFFSET {}'''.format(max_results, cont) if limit else '')
                    roles[role['name']] = (role['rid'], await conn.fetch(query, self.lid, role['rid']))
                return [{'name': role, 'rid': rid, 'data': [{j: i[j] for j in ('uid', 'username', 'fullname')} for i in user]} for role, (rid, user) in roles.items()]
            query = '''SELECT uid, username, fullname FROM members WHERE lid = $1::bigint AND type = 0''' \
                    + ('''LIMIT {} OFFSET {}'''.format(max_results, cont) if limit else '')
            return [{j: i[j] for j in ('uid', 'username', 'fullname')} for i in await conn.fetch(query, self.lid)]
    
    async def add_member(self, username, password, rid, fullname):
        """
        Adds a new member to this location, given the above info.
        """
        pwhash = await self._app.aexec(self._app.ppe, bcrypt.hashpw, password.encode('utf-8'), bcrypt.gensalt(12))
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
    
    async def search(self, *, title=None, genre=None, type_=None, author=None, cont=0, max_results=5, where_taken=None):
        """
        The below weirdness is necessary because asyncpg does not allow
        keyword-based arguments in queries, and it also does not support
        'ignoring' certain arguments, so I have to instead construct a
        query with *only* the expressions I'm looking for.
        """
        search_terms = title, genre, author, type_
        query = (
              '''SELECT DISTINCT ON (lower(title)) title, mid, author, genre, type, issued_to, image FROM items WHERE true ''' # stupid hack coming up
              + ('''AND title ILIKE '%' || ${}::text || '%' ''' if title else '')
              + ('''AND genre ILIKE '%' || ${}::text || '%' ''' if genre else '')
              + ('''AND author ILIKE '%' || ${}::text || '%' ''' if author else '')
              + ('''AND type ILIKE '%' || ${}::text || '%' ''' if type_ else '')
              + ('''AND false ''' if not any(search_terms) else '') # because 'WHERE true' otherwise returns everything if not any(search_terms)
              + ('''AND issued_to IS {} NULL '''.format(('', 'NOT')[where_taken]) if where_taken is not None else '')
              + ('''ORDER BY lower(title) ''') # just to establish a consistent order for `cont' param
            ).format(*range(1, 1+sum(map(bool, search_terms)))) \
            + ('''LIMIT {} OFFSET {} ''').format(max_results, cont) # these are ok not to parameterize because they're internal
        results = await self.pool.fetch(query, *filter(bool, search_terms))
        if where_taken is not None: # this means I'm calling it from in here and so I probably want an actual MediaItem or at least no junk
            if max_results == 1:
                return await MediaItem(results[0]['mid'], app=self._app)
            return [i['mid'] for i in results]
        # I'd have liked to provide a full MediaItem for each result,
        # but that would take so so so so so unbearably long on Heroku's DB speeds,
        # not to mention being just pretty all-around inefficient
        return [{j: i[j] for j in ('mid', 'title', 'author', 'genre', 'type', 'issued_to', 'image')} for i in results]
    
    async def roles(self, *, lower_than: Perms.raw = None):
        """
        Serves all this location's roles.
        lower_than is an optional argument that, when given,
        effects 'filtering' -- only returns the roles whose
        permissions number is lower than it, to prevent less-endowed
        operators from assigning higher-permed roles to members.
        """
        async with self.acquire() as conn:
            query = '''
            SELECT rid, name, isdefault, permissions AS perms, maxes, locks
              FROM roles
             WHERE lid = $1::bigint
            '''
            sums = '''SELECT count(*) FROM members WHERE rid = $1::bigint'''
            res = [{j: i[j] for j in ('rid', 'name', 'isdefault', 'perms', 'maxes', 'locks')} for i in await conn.fetch(query, self.lid)]
            if lower_than and lower_than < 127: # if it isn't an admin role
                res = [i for i in res if i['perms'] < lower_than]
            for i in res:
                i['perms'] = Perms(i['perms']).props
                i['maxes'] = Maxes(i['maxes']).props
                i['locks'] = Locks(i['locks']).props
                i['count'] = await conn.fetchval(sums, i['rid'])
        return res
    
    async def add_role(self, name, *, kws=None, seqs=None):
        """
        Adds a new role to a location, taking either keyword arguments
        (kws) for each of its perms/maxes/locks, or sequences (seqs)
        from either of which the perms/maxes/locks objects can be
        constructed.
        """
        perms, maxes, locks = Role.attrs_from(seqs=seqs, kws=kws)
        async with self.acquire() as conn:
            query = '''
            INSERT INTO roles (
                          lid, name, isdefault,
                          permissions, maxes, locks
                          )
                 SELECT $1::bigint, $2::text, FALSE,
                        $3::smallint, $4::bigint, $5::bigint;
            '''
            await conn.execute(query, self.lid, name, perms.raw, maxes.raw, locks.raw)
            rid = await conn.fetchval('''SELECT currval(pg_get_serial_sequence('roles', 'rid'))''')
        return await Role(rid, self._app, location=self)
    
    async def items(self, *, cont=0, max_results=5):
        """
        Returns all this location's items in chunks of
        max_results items, on page cont.
        """
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
    
    async def edit(self, locname, color, checkoutpw, fine_amt, fine_interval):
        """Checkout password can be empty"""
        fine_amt = Decimal(str(fine_amt))
        fine_interval = int(fine_interval)
        query = '''
          UPDATE locations
             SET name = COALESCE($2::text, name),
                 color = COALESCE($3::int, color),
                 fine_amt = COALESCE($4::numeric, fine_amt),
                 fine_interval = COALESCE($5::integer, fine_interval)
           WHERE lid = $1::bigint
        '''
        await self.pool.execute(query, self.lid, locname, color, fine_amt, fine_interval)
        checkout_pwhash = checkoutpw
        if checkoutpw is not None:
            checkout_pwhash = await self._app.aexec(None, bcrypt.hashpw, checkoutpw.encode(), bcrypt.gensalt(12))
        query = '''
        SELECT pwhash FROM members
         WHERE lid = $1::bigint
           AND type = 1
        '''
        query = '''
        UPDATE members
           SET pwhash = COALESCE($2::bytea, pwhash)
         WHERE lid = $1::bigint
           AND type = 1
        '''
        await self.pool.execute(query, self.lid, checkout_pwhash)
    
    async def image(self):
        raise NotImplementedError
        # and may never be ...
    
    async def media_types(self):
        """
        Returns all this location's media types, with their maxes included as a Maxes obj.
        """
        query = '''SELECT name, maxes FROM mtypes WHERE lid = $1::bigint'''
        return [{'name': i['name'], 'maxes': Maxes(i['maxes'])} for i in await self.pool.fetch(query, self.lid)]
    
    async def add_media_type(self, name, unit, maxes: Maxes.props):
        """
        Adds a new media type to the location from its name,
        unit of length, and max overrides.
        """
        query = '''
        INSERT INTO mtypes (name, unit, maxes, lid)
        SELECT $1::text, $2::text, $3::bigint, $4::bigint
        '''
        await self.pool.execute(query, name.lower(), unit.lower(), Maxes.from_kwargs(**maxes).raw, self.lid)
        return await MediaType(name.lower(), self, self._app)
    
    async def edit_media_type(self, mtype, *, maxes=None, name=None, unit=None):
        """
        Edit's a media type's maxes, unit, and name.
        """
        mtype = await MediaType(mtype.lower(), self, self._app)
        await mtype.edit(maxes=maxes and Maxes.from_kwargs(**maxes).raw, name=name.lower(), unit=unit)
    
    async def remove_media_type(self, name):
        """
        Gets rid of a media type, making sure to clean up where
        any media items might have it.
        (If this isn't done MediaItem throws "this type doesn't exist yet"
        whenever you try to access one of said items' info)
        """
        query = '''
        DELETE FROM mtypes
         WHERE name = $1::text
           AND lid = $2::bigint
        '''
        await self.pool.execute(query, name, self.lid)
        query = '''
        UPDATE items
           SET type = NULL
         WHERE type = $1::text
           AND lid = $2::bigint
        '''
        await self.pool.execute(query, name, self.lid)
    
    async def genres(self):
        """
        Grabs all a location's genres.
        There's no actual table storing genres, of course --
        -- they're literally just names and one item isn't enough data
        to necessitate a whole table ofc --
        -- so I grab whatever's in the genres column of the items table.
        """
        query = '''
        SELECT DISTINCT lower(genre) AS genre FROM items WHERE lid = $1::bigint ORDER BY lower(genre)
        '''
        return [i['genre'] for i in await self.pool.fetch(query, self.lid)]
    
    async def rename_genre(self, cur, to):
        """
        Changes the name of a genre, from [cur]rent value [to] a new value
        """
        await self.pool.execute(
          '''UPDATE items SET genre = lower($2::text) WHERE genre = lower($1::text)''', cur, to
          )
    
    async def remove_genre(self, genre):
        """
        Removes a genre from this location.
        """
        await self.pool.execute(
          '''UPDATE items SET genre = NULL WHERE genre = lower($1::text)''', genre
          )
    
    async def add_media(self, title, author, published, type_, genre, isbn, price, length):
        """
        Adds a new media item to location.
        Genre will be added regardless of whether it's new, because
        again there's no table or anything keeping track of genres.
        Item's price will be converted to a proper representation of its
        value through the Decimal class before being passed to
        PostgreSQL.
        """
        ident = img = ''
        try:
            async with self._app.sem, self._app.session.get(self.gb_image_query(title, author)) as resp:
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
        args = type_.name, genre, ident or isbn, self.lid, title, author, int(published), round(Decimal(price), 2), int(length)
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
                 SELECT $2::text, lower($3::text),
                        $4::text, $5::bigint,
                        $6::text, $7::text, $8::int,
                        $9::numeric, $10::int,
                        current_date, NULL,
                        $1::text;
            '''
            await conn.execute(query, img, *args)
            mid = await conn.fetchval('''SELECT currval(pg_get_serial_sequence('items', 'mid'))''')
        return await MediaItem(mid, self._app)
    
    async def remove_item(self, item):
        """
        86es a media item.
        No need for cleanup (like, of fine data or whatever)
        because that's all stored in the item's table row regardless,
        so it'll be gone on deleting the row.
        This of course means that any fines on the item will be cleared
        without having to be paid off.
        """
        item = item if isinstance(item, MediaItem) else await MediaItem(item, self._app)
        query = '''
        DELETE FROM items
        WHERE mid = $1::bigint
        '''
        return await self.pool.execute(query, item.mid)

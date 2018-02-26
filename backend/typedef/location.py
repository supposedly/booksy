import functools
import io
from decimal import Decimal

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
    bcrypt = types.SimpleNamespace(
      hashpw = __hashpw,
      gensalt = __gensalt
    )
#################################################


class Location(AsyncInit):
    """
    Defines a library. TODO: Instance methods.
    """
    props = [
      'lid',
      'name', 'ip',
      'color', 'image',
      'fine_amt', 'fine_interval'
      ]
    
    @staticmethod
    def do_imports():
        global Location, Role, MediaItem, MediaType, User
        from . import Location, Role, MediaItem, MediaType, User
    
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
        self.color = color
        self.image = image
    
    def __str__(self):
        """Unused but eh"""
        return str(self.lid)
    
    def to_dict(self):
        return {i: getattr(self, i, None) for i in self.props} + {'owner_id', (self.owner).id}
    
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
    async def instate(cls, rqst, pw, **kwargs):
        """In this order:"""
        props = [
          'name', 'ip', 'color',##'image',
          'username', 'pwhash', # these are for the checkout account
          'admin_username', 'admin_pwhash',
          'admin_name', 'admin_email', 'admin_phone' # these aren't used
          ]
        kwargs[''] = await self._app.aexec(self._app.ppe, bcrypt.hashpw, pw.encode(), bcrypt.gensalt(12))
        args = [kwargs.get(attr, rqst.ip if attr=='ip' else None) for attr in props]
        with open('./backend/sql/register_location.sql') as register_location:
            for query in register_location.read().split(';'):
                lid = await rqst.app.pg_pool.fetchval(query, *args) # returns lID
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
            df.password = df.password.apply(functools.partial(bcrypt.hashpw, salt=lambda: bcrypt.gensalt(12)))
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
        df.password = self._app.aexec(None, df.password.str.encode, 'utf-8')
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
        return await User(uid, self._app, location=self)
    
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
    
    async def search(self, *, title=None, genre=None, type_=None, author=None, cont=0, max_results=5, where_taken=None):
        """
        The below weirdness is necessary because asyncpg does not allow
        keyword-based arguments in queries, and it also does not support
        'ignoring' certain arguments, so I have to instead construct a
        query with *only* the expressions I'm looking for.
        """
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
                return await MediaItem(results[0]['mid'], app=self._app)
            return [i['mid'] for i in results]
        # I'd have liked to provide a full MediaItem for each result,
        # but that would take so so so so so unbearably long on Heroku's DB speeds,
        # not to mention being just pretty all-around inefficient
        return [{j: i[j] for j in ('mid', 'title', 'author', 'genre', 'type', 'image')} for i in results]
    
    async def roles(self):
        async with self.acquire() as conn:
            query = '''
            SELECT rid, name, isdefault, permissions AS perms, maxes, locks
              FROM roles
             WHERE lid = $1::bigint
            '''
            q2ery = '''SELECT count(*) FROM members WHERE rid = $1::bigint'''
            res = [{j: i[j] for j in ('rid', 'name', 'isdefault', 'perms', 'maxes', 'locks')} for i in await conn.fetch(query, self.lid)]
            for i in res:
                i['perms'] = Perms(i['perms']).props
                i['maxes'] = Maxes(i['maxes']).props
                i['locks'] = Locks(i['locks']).props
                i['count'] = await conn.fetchval(q2ery, i['rid'])
        return res
    
    async def add_role(self, name, *, kws=None, seqs=None):
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
        props = [
          'media_types',
          'name', 'ip',
          'color', 'image',
          'fine_amt', 'fine_interval'
          ]
        col_names = props[1:] + ['media_types']
        query = f'''
          UPDATE locations
             SET name = COALESCE($1::text, name),
                 ip = COALESCE($2::text, ip),
                 fine_amt = COALESCE($3::numeric, fine_amt),
                 fine_interval = COALESCE($4::numeric, fine_interval),
                 image = COALESCE($5::bytea, image),
                 color = COALESCE($6::smallint, color)
           WHERE lid = $2::bigint
        '''
        await self.pool.execute(query, new, self.lid)
    
    async def image(self):
        raise NotImplementedError
        # and may never be ...
    
    async def media_types(self):
        query = '''SELECT name, maxes FROM mtypes WHERE lid = $1::bigint'''
        return [{'name': i['name'], 'maxes': Maxes(i['maxes'])} for i in await self.pool.fetch(query, self.lid)]
    
    async def add_media_type(self, name, unit, maxes: 'Maxes.namemap'):
        query = '''
        INSERT INTO mtypes (name, unit, maxes, lid)
        SELECT $1::text, $2::text, $3::bigint, $4::bigint
        '''
        await self.pool.execute(query, unit.lower(), name.lower(), Maxes.from_kwargs(**maxes).raw, self.lid)
        return await MediaType(name, self, self._app)
    
    async def edit_media_type(self, mtype, *, maxes=None, name=None, unit=None):
        """
        Edit's a media type's maxes and name.
        """
        mtype = await MediaType(mtype, self, self._app)
        await mtype.edit(maxes=maxes and Maxes.from_kwargs(**maxes).raw, name=name, unit=unit)
    
    async def remove_media_type(self, name):
        """
        Gets rid of a media type, also making sure to clean up where
        any media items might have it.
        (Else MediaItem just throws "this type doesn't exist yet"
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
        """Changes the name of a genre, from [cur]rent value [to] a new value"""
        await self.pool.execute(
          '''UPDATE items SET genre = lower($2::text) WHERE genre = lower($1::text)''', cur, to
          )
    
    async def remove_genre(self, genre):
        await self.pool.execute(
          '''UPDATE items SET genre = NULL WHERE genre = lower($1::text)''', genre
          )
    
    async def add_media(self, title, author, published, type_, genre, isbn, price, length):
        """
        Adds a new media item to location.
        Genre will be added regardless of whether it's new, because
        again there's no table or anything storing genres.
        Price will be converted to a proper representation of its
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

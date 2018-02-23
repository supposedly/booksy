from ..core import AsyncInit
from ..attributes import Perms, Maxes, Locks


class MediaType(AsyncInit):
    """
    Defines a kind of media, e.g. books or audiotapes.
    Currently unused but I very much hope to implement it at a later date.
    """
    props = [
      'name', 
    ]
    
    @staticmethod
    def do_imports():
        global Location, Role, MediaItem, MediaType, User
        from . import Location, Role, MediaItem, MediaType, User
    
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
    
    async def set_maxes(self, newmaxnum):
        query = '''
        UPDATE items
           SET maxes = $1::bigint
         WHERE media_type = $2::text
        '''
        await self.pool.execute(query, newmaxnum, self.name)
        self.maxes = newmaxes

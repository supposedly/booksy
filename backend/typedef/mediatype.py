from ..core import AsyncInit
from ..attributes import Limits


class MediaType(AsyncInit):
    """
    Defines a kind of media, e.g. books or audiotapes.
    Have limits defined on them that override user/role limits
    and are overridden by item limits.
    
    location (Location): The location this media type is bound to
    limits    (Limits):    The above-mentioned overrides
    name     (str):      Media type's name
    unit     (str):      Media type's unit of length, e.g. "pages" or "minutes"
    """
    @staticmethod
    def do_imports():
        global Location, Role, MediaItem, User
        from . import Location, Role, MediaItem, User
        global get_user, get_role, get_location, get_media_item
        from . import get_user, get_role, get_location, get_media_item
    
    async def __init__(self, name, location, app):
        self._app = app
        self.pool = app.pg_pool
        self.acquire = self.pool.acquire
        self.location = location if isinstance(location, Location) else await get_location(int(location), self._app)
        self.name = name
        check = await self.pool.fetchval('''SELECT name FROM mtypes WHERE name = $1::text AND lid = $2::bigint''', self.name, self.location.lid)
        if not check:
            raise ValueError('This type does not exist yet')
        res = await self.pool.fetchrow('''SELECT unit, limits FROM mtypes WHERE name = $1::text AND lid = $2::bigint''', self.name, self.location.lid)
        self.limits = Limits(res['limits']) if res['limits'] else None
        self.unit = res['unit']
    
    def __str__(self):
        return self.name if hasattr(self, 'name') else ''
    
    def to_dict(self):
        return {'name': self.name, 'unit': self.unit, 'limits': self.limits.props}

    async def edit(self, *, limits: int = None, name=None, unit=None):
        """
        Edits all of this media type's info.
        
        limits is the raw number, not a 'props' dict or a sequence.
        """
        query = '''
        UPDATE mtypes
          SET limits = COALESCE($3::bigint, limits),
              name = COALESCE($4::text, name),
              unit = COALESCE($5::text, unit)
        WHERE name = $1::text
          AND lid = $2::bigint
        '''
        await self.pool.execute(query, self.name, self.location.lid, limits, name, unit)
        self.limits, self.name = Limits(limits), name

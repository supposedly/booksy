import sanic
import sanic_jwt as jwt
from sanic_jwt import decorators as jwtdec

from . import uid_get, rqst_get
from . import Location, Role, MediaType, MediaItem, User

types = sanic.Blueprint('location_media_types', url_prefix='/types')

@types.get('/')
@uid_get('location')
@jwtdec.protected()
async def get_location_media_types(rqst, location):
    return sanic.response.json({'types': await location.media_types()}, status=200)

@types.get('/info')
@uid_get('location')
@rqst_get('name')
@jwtdec.protected()
async def get_media_type_info(rqst, location, *, name):
    mtype = await MediaType(name, location, rqst.app)
    return sanic.response.json({'props': mtype.to_dict()}, status=200)

@types.post('/add')
@rqst_get('user', 'add')
@jwtdec.protected()
async def add_location_media_type(rqst, user, *, add: {'name': str, 'maxes': dict}):
    if not user.perms.can_manage_media:
        sanic.exceptions.abort(401, "You aren't allowed to manage media types.")
    if add.name.lower() in {i.name.lower() for i in await user.location.media_types()}:
        sanic.exceptions.abort(409, 'This media type already exists!')
    await user.location.add_media_type(**add)
    return sanic.response.raw(b'', status=204)

@types.post('/remove')
@rqst_get('user', 'remove')
@jwtdec.protected()
async def remove_location_media_type(rqst, user, *, remove: str):
    if not user.perms.can_manage_media:
        sanic.exceptions.abort(401, "You aren't allowed to manage media types.")
    await user.location.remove_media_type(remove)
    return sanic.response.raw(b'', status=204)

@types.post('/edit')
@rqst_get('user', 'edit', 'maxes', 'name') # name is the new name, edit is the old name (i.e. what to rename from)
@jwtdec.protected()
async def edit_location_media_type(rqst, user, *, edit: str, maxes, name: str):
    await user.location.edit_media_type(edit, maxes=maxes, name=name)
    return sanic.response.raw(b'', status=204)

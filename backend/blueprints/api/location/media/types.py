import sanic
from asyncpg.exceptions import UniqueViolationError
from sanic_jwt import decorators as jwtdec

from . import uid_get, rqst_get
from . import MediaType

types = sanic.Blueprint('location_media_types', url_prefix='/types')


@types.get('/')
@uid_get('location')
@jwtdec.protected()
async def get_location_media_types(rqst, location):
    """
    Serves all media types (as serialized dicts) defined on a location.
    """
    return sanic.response.json({'types': await location.media_types()}, status=200)


@types.get('/info')
@uid_get('location')
@rqst_get('name')
@jwtdec.protected()
async def get_media_type_info(rqst, location, *, name):
    """
    Serves attrs of a requested media type given its name.
    """
    mtype = await MediaType(name, location, rqst.app)
    return sanic.response.json({'type': mtype.to_dict()}, status=200)


@types.post('/add')
@rqst_get('user', 'add')
@jwtdec.protected()
async def add_location_media_type(rqst, user, *, add: {'name': str, 'unit': str, 'limits': dict}):
    """
    Adds a new media type to the location, taking its name, unit of length, and max overrides.
    """
    if not user.perms.can_manage_media:
        sanic.exceptions.abort(401, "You aren't allowed to manage media types.")
    if 'name' not in add or not add['name']:
        sanic.exceptions.abort(422, "add_media_type() missing 1 required positional argument: 'name'")
    if 'unit' not in add or not add['unit']:
        sanic.exceptions.abort(422, "add_media_type() missing 1 required positional argument: 'unit'")
    try:
        await user.location.add_media_type(**add)
    except UniqueViolationError:
        sanic.exceptions.abort(409, 'This media type already exists!')
    except Exception as e:
        sanic.exceptions.abort(422, e)
    return sanic.response.raw(b'', status=204)


@types.post('/remove')
@rqst_get('user', 'remove')
@jwtdec.protected()
async def remove_location_media_type(rqst, user, *, remove: str):
    """
    Gets rid of a media type, assigning 'none' to the items that had it.
    """
    if not user.perms.can_manage_media:
        sanic.exceptions.abort(401, "You aren't allowed to manage media types.")
    await user.location.remove_media_type(remove)
    return sanic.response.raw(b'', status=204)


@types.post('/edit')
@rqst_get('user', 'edit', 'limits', 'name', 'unit')  # name is the new name, edit is the old name (i.e. what to rename from)
@jwtdec.protected()
async def edit_location_media_type(rqst, user, *, edit: str, limits, name: str, unit: str):
    """
    Edits all attrs of a media type.
    """
    await user.location.edit_media_type(edit, limits=limits, name=name, unit=unit)
    return sanic.response.raw(b'', status=204)

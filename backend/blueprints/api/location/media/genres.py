import sanic
import sanic_jwt as jwt
from sanic_jwt import decorators as jwtdec

from . import uid_get, rqst_get
from . import Location, Role, MediaType, MediaItem, User

genres = sanic.Blueprint('location_media_genres', url_prefix='/genres')

@genres.get('/')
@uid_get('location')
async def get_location_genres(rqst, location):
    return sanic.response.json(await location.genres(), status=200)

@genres.post('/edit')
@uid_get('location', 'perms')
@rqst_get('genre', 'to')
async def edit_genre(rqst, location, perms, *, genre, to):
    """Edit the name of the given genre."""
    if not perms.can_manage_media:
        sanic.exceptions.abort(403, "You aren't allowed to edit genre names.")
    await location.rename_genre(genre, to)
    return sanic.response.raw(b'', status=204)

@genres.post('/remove')
@uid_get('location', 'perms')
@rqst_get('genre')
async def rm_genre(rqst, location, perms, *, genre):
    """Get rid of the given genre."""
    if not perms.can_manage_media:
        sanic.exceptions.abort(403, "You aren't allowed to delete genres.")
    await location.remove_genre(genre)
    return sanic.response.raw(b'', status=204)

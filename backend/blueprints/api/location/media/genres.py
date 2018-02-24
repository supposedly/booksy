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

"""/api/location/edit"""
import sanic
import sanic_jwt as jwt
from sanic_jwt import decorators as jwtdec

from . import uid_get, rqst_get
from . import Location, Role, MediaType, MediaItem, User

edit = sanic.Blueprint('location_edit_api', url_prefix='/edit')

@edit.post('/<action:(name|image|color)>')
@uid_get('location')
@jwtdec.protected()
async def edit_location_info(rqst, location, *, action):
    """
    Catch-all endpoint for updating a location's info
    """
    sanic.exceptions.abort(501, "Left unimplemented for FBLA demo")
    await location.edit(action, new)
    return sanic.response.raw(status=204)

"""/api/location/edit"""
import sanic
import sanic_jwt as jwt
from sanic_jwt import decorators as jwtdec

from .import uid_get, rqst_get
from .import Location, Role, MediaType, MediaItem, User

media = sanic.Blueprint('location_edit_api', url_prefix='/edit')

@uid_get('location')
@loc.post('/<action:(name|image|color)>')
@jwtdec.protect()
async def edit_location_info(rqst, location, action):
    """
    Catch-all endpoint for updating a location's info
    """
    try:
        new = rqst.json['new']
    except KeyError:
        sanic.exceptions.abort(422, 'Missing new info')
    await location.edit(action, new)
    return sanic.response.raw(status=204)

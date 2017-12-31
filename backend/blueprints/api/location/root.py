"""/api/location"""
import sanic
import sanic_jwt as jwt
from sanic_jwt import decorators as jwtdec

from .import uid_get, rqst_get
from .import Location, Role, MediaType, MediaItem, User

root = sanic.Blueprint('location_api', url_prefix='')

@uid_get('location')
@root.get('/')
async def return_location_repr(rqst, location):
    return sanic.response.json(location.to_dict(), status=200)

@uid_get('location')
@root.get('/<attr:(name|image|color)>')
async def return_location_attr(rqst, user, attr):
    return sanic.response.json({attr: getattr(location, attr)}, status=200)

@root.get('/is-registered')
async def is_location_registered(rqst):
    if not rqst.ip:
        return sanic.response.json({'registered': False, 'reason': 'No IP address found'})
    location = await Location.from_ip(rqst.ip)
    if location is not None:
        return sanic.response.json({'registered': True, 'lid': location.id}, status=200)
    else:
        return sanic.response.json({'registered': False, 'reason': 'Not found in DB'})

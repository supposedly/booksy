"""/api/location"""
import sanic
import sanic_jwt as jwt
from sanic_jwt import decorators as jwtdec

from .import uid_get, rqst_get
from .import Location, Role, MediaType, MediaItem, User

root = sanic.Blueprint('location_api', url_prefix='')

@root.get('/')
@uid_get('location')
async def give_location_repr(rqst, location):
    return sanic.response.json(location.to_dict(), status=200)

@root.get('/<attr:(name|image|color)>')
@uid_get('location')
async def return_location_attr(rqst, user, attr):
    return sanic.response.json({attr: getattr(location, attr)}, status=200)

@root.get('/is-registered')
async def is_location_registered(rqst):
    if not rqst.ip:
        return sanic.response.json({'registered': False, 'reason': 'No IP address found'})
    location = await Location.from_ip(rqst)
    if location is not None:
        return sanic.response.json({'registered': True, 'lid': location.id}, status=200)
    else:
        return sanic.response.json({'registered': False, 'reason': 'Not found in DB'})

@root.get('/report')
@rqst_get('do')
@uid_get('location', 'perms')
@jwtdec.protected()
async def serve_a_report(rqst, location, perms, do):
    if not perms.can_generate_reports:
        sanic.exceptions.abort(403, "You aren't allowed to generate reports.")
    return sanic.response.json(await location.report(**do))

import sanic
import sanic_jwt as jwt
from sanic_jwt import decorators as jwtdec

from ...typedef import Location, Role, MediaItem, MediaType, User

loc = sanic.Blueprint('location_api', url_prefix='/location')

@loc.get('/')
async def return_location_repr(rqst):
    try:
        location = await Location(rqst.raw_args['lid'], rqst.app)
    except KeyError:
        sanic.exceptions.abort(422, 'Missing location ID')
    return sanic.response.json(location.to_dict(), status=200)

@loc.get('/<attr:(name|image|color)>')
async def return_location_attr(rqst, attr):
    try:
        location = await Location(rqst.raw_args['lid'], rqst.app)
    except KeyError:
        sanic.exceptions.abort(422, 'Missing location ID')
    return sanic.response.json({'Attribute': getattr(location, attr)}, status=200)

@loc.get('/is-registered')
async def is_location_registered(rqst):
    if not rqst.ip:
        sanic.exceptions.abort(422, 'Unobtainable or unregistered IP')
    location = await Location.from_ip(rqst.ip)
    if location:
        return sanic.response.json({'processed': True, 'lid': location.id}, status=200)
    else:
        return sanic.response.raw(status=404)

@loc.post('/edit/<action:(name|image|color)>')
@jwtdec.protect()
async def edit_location_info(rqst, action):
    """
    Catch-all endpoint for updating a location's info
    """
    try:
        location = await Location(rqst.form['lid'], rqst.app)
        new = rqst.form['new']
    except KeyError:
        sanic.exceptions.abort(422, 'Missing media type name')
    await location.edit(action, new)
    return sanic.response.raw(status=204)

@loc.get('/media-types')
@jwtdec.protect()
async def get_location_media_types(rqst):
    try:
        location = await Location(rqst.raw_args['lid'], rqst.app)
    except KeyError:
        sanic.exceptions.abort(422, 'Missing location ID')
    return sanic.response.json(await location.media_types())

@loc.post('/media-types/<action:(add|remove)>')
@jwtdec.protect()
async def edit_location_media_types(rqst, action):
    try:
        type_name = rqst.form['name']
        location = await Location(rqst.form['lid'], rqst.app)
    except KeyError:
        sanic.exceptions.abort(422, 'Missing media type name')
    if action == 'add':
        return sanic.response.json(
          await location.add_media_type(type_name),
          status=200
        )
    await location.remove_media_type(type_name)
    return sanic.response.raw(status=204)

@loc.post('/members/add')
@jwtdec.protect()
async def add_member_to_location(rqst):
    try:
        location = await Location(rqst.form['lid'], rqst.app)
        userdata = rqst.form['data']
    except KeyError:
        sanic.exceptions.abort(422, 'Missing location ID')
    return await location.add_member(**userdata)

"""/api/media"""

import sanic
import sanic_jwt as jwt
from sanic_jwt import decorators as jwtdec

from ...typedef import Location, Role, MediaItem, MediaType, User

media = sanic.Blueprint.group('media_api', url_prefix='/media')

@media.get('/api/media/check')
async def get_media_status(rqst):
    try:
        item = await MediaItem(rqst.raw_args['mid'])
    except KeyError:
        sanic.exceptions.abort(422, 'Missing item ID')
    return sanic.response.json(item.status, status=200)

@media.post('/api/media/check/out')
@jwtdec.protected()
async def issue_item(rqst):
    try:
        item = await MediaItem(rqst.form['mid'], rqst.app)
        user = await User(rqst.form['uid'], rqst.app)
    except KeyError:
        sanic.exceptions.abort(422, 'Missing item or user ID')
    forbidden = user.perms.can_check_out
    if forbidden is not None:
        # `forbidden' will be None if everything's good
        # and a string w/ missing permissions otherwise
        # so if it's nonempty we know smthng went wrong
        sanic.exceptions.abort(403, forbidden)
    await item.issue_to(user)
    return sanic.response.raw(status=204) 

@media.post('/api/media/check/in')
@jwtdec.protected()
async def return_item(rqst):
    try:
        item = await MediaItem(rqst.raw_args['mid'], rqst.app)
        user = await User(rqst.raw_args['uid'], rqst.app)
    except KeyError:
        sanic.exceptions.abort(422, 'Missing item or user ID')
    if not user.perms.can_return_items:
        sanic.exceptions.abort(403, 'User is missing permission to return items.')
    await item.check_in()
    return sanic.response.raw(status=204)

@media.get('/api/media/info')
@jwtdec.protected()
async def get_media_info(rqst):
    try:
        item = await MediaItem(rqst.raw_args['mid'], rqst.app)
    except KeyError:
        sanic.exceptions.abort(422, 'Missing item ID')
    return sanic.response.json(item.to_dict(), status=200)

@media.post('/api/media/add')
@jwtdec.protected()
async def add_media_item_to_db(rqst):
    try:
        data = rqst.form['data']
        location = await Location(rqst.form['lid'], rqst.app)
    except KeyError:
        sanic.exceptions.abort(422, 'Missing item data or location ID')
    await location.add_media(**data)
    return sanic.response.raw(status=204)

@media.post('/api/media/remove')
@jwtdec.protected()
async def remove_media_item_from_db(rqst):
    try:
        item = await MediaItem(rqst.form['mid'], rqst.app)
        # location = await Location(rqst.form['lid'], rqst.app)
    except KeyError:
        sanic.exceptions.abort(422, 'Missing item ID')
    await item.remove()
    return sanic.response.raw(status=204)

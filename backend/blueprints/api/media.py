"""/api/media"""
import sanic
import sanic_jwt as jwt
from sanic_jwt import decorators as jwtdec

from .import uid_get, rqst_get
from .import Location, Role, MediaType, MediaItem, User

media = sanic.Blueprint('media_api', url_prefix='/media')

@media.post('/hold')
@rqst_get('user', 'item')
@jwtdec.protected()
async def put_item_on_hold(rqst, user, item):
    if user.cannot_check_out:
        sanic.exceptions.abort(403, "You aren't allowed to place holds.")
    if user.holds > user.maxes.holds:
        sanic.exceptions.abort(403, "You aren't allowed to place any more holds.")
    if not item._issued_uid:
        sanic.exceptions.abort(409, "This item is already available.")
    err = await user.hold(title=item.title, author=item.author, type_=item.type, genre=item.genre)
    if err:
        sanic.exceptions.abort(403, err)
    return sanic.response.raw(b'', status=204)

@media.get('/check')
@rqst_get('item')
async def get_bool_available(rqst, item):
    """
    This might be unnecessary... I might be able to just
    handle the 'check' by aborting from /check/out, no?
    """
    issued_to = item.issued_to.username if item.issued_to and item.issued_to.username else item._issued_uid
    try:
        return sanic.response.json({'available': item.available, 'issuedTo': issued_to, 'issuedUid': item._issued_uid}, status=200)
    except AttributeError:
        sanic.exceptions.abort(422, "User does not exist.")

@media.post('/edit')
@rqst_get('user', 'item', 'title', 'author', 'genre', 'type_', 'price', 'length', 'published', 'isbn')
async def edit_item(rqst, user, item, *args):
    await item.edit(*args)
    return sanic.response.json(item.to_dict(), status=200)

@media.get('/check/verbose')
@rqst_get('item')
async def get_media_status(rqst, item):
    # unused
    return sanic.response.json(item.status, status=200)

@media.post('/check/out')
@rqst_get('item', 'username', 'location')
@jwtdec.protected()
async def issue_item(rqst, item, username, location):
    try:
        user = await User.from_identifiers(username, location, app=rqst.app)
    except ValueError as e:
        sanic.exceptions.abort(404, e)
    if user.cannot_check_out:
        sanic.exceptions.abort(403, "You aren't allowed to check out.")
    if not item.available and user.uid != item._issued_uid:
        # will never be triggered unless I forget to query /check first
        sanic.exceptions.abort(409, f'Item is checked out to {issued_to}.')
    await item.issue_to(user=user)
    return sanic.response.json({'checked': 'out', 'title': item.title, 'author': item.author, 'image': item.image}, status=200)

@media.post('/check/in')
@rqst_get('item', 'username', 'location')
@jwtdec.protected()
async def return_item(rqst, item, username, location):
    try:
        user = await User.from_identifiers(username, location, app=rqst.app)
    except ValueError as e:
        sanic.exceptions.abort(404, e)
    if user.is_checkout or not user.perms.can_return_items:
        sanic.exceptions.abort(403, "You aren't allowed to return items.")
    if item.fines:
        sanic.exceptions.abort(403, "This item's fines must be paid off before it is returned.")
    await item.check_in()
    return sanic.response.raw(b'', status=204)

@media.get('/info')
@rqst_get('item')
@jwtdec.protected()
async def get_media_info(rqst, item):
    return sanic.response.json({'info': item.to_dict()}, status=200)

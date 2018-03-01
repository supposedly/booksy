"""/api/media"""
import sanic
import sanic_jwt as jwt
from sanic_jwt import decorators as jwtdec

from . import uid_get, rqst_get
from . import Location, Role, MediaType, MediaItem, User

media = sanic.Blueprint('media_api', url_prefix='/media')

@media.post('/hold')
@rqst_get('user', 'item')
@jwtdec.protected()
async def put_item_on_hold(rqst, user, *, item):
    """
    Places an item on hold, assigning it to 
    
    Unfortunately does not operate on whole items (i.e. all items with
    the same genre+mediatype+title+author), just a specific media ID.
    """
    if user.cannot_check_out:
        sanic.exceptions.abort(403, "You aren't allowed to place holds.")
    if user.holds > user.maxes.holds:
        sanic.exceptions.abort(403, "You aren't allowed to place any more holds.")
    if not item._issued_uid:
        sanic.exceptions.abort(409, "This item is already available.")
    err = await user.hold(title=item.title, author=item.author, type_=item.type, genre=item.genre)
    if err: # if it the user's not allowed to do this err will be a truthy str, otherwise None
        sanic.exceptions.abort(403, err)
    return sanic.response.raw(b'', status=204)

@media.post('/clear-fines')
@rqst_get('user', 'item') # user making the request (NOT the user with the fines), and then the item to be paid off
@jwtdec.protected()
async def pay_item_off(rqst, user, *, item):
    """
    Reset an item's fines to 0 while it's checked out.
    This does not stop the fines from incrementing next interval.
    """
    if not user.perms.can_manage_media:
        sanic.exceptions.abort(403, "You aren't allowed to mark fines paid.")
    await item.pay_off()
    return sanic.response.raw(b'', 204)

@media.post('/edit')
@rqst_get('user', 'item', 'title', 'author', 'genre', 'type_', 'price', 'length', 'published', 'isbn')
@jwtdec.protected()
async def edit_item(rqst, user, *, item, title, author, genre, type_, price, length, published, isbn):
    """
    Edit all of an item's info. type_ is the type's name or a dict with it, not a MediaType object.
    """
    if not user.perms.can_manage_media:
        sanic.exceptions.abort(403, "You aren't allowed to edit media.")
    await item.edit(title, author, genre, type_ if isinstance(type_, str) else type_['name'], price, length, published, isbn)
    return sanic.response.json(item.to_dict(), status=200)

@media.post('/delete')
@rqst_get('item', 'user')
async def del_item(rqst, user, *, item):
    """
    Delete an item altogether.
    This clears any fines on it, too.
    """
    if not user.perms.can_manage_media:
        sanic.exceptions.abort(403, "You aren't allowed to delete media.")
    await item.delete()

@media.get('/check')
@rqst_get('item')
async def get_item_available(rqst, *, item):
    """
    Could technically handle this 'check' by aborting
    from /check/out if the user doesn't have permissions,
    but this way I can get the frontend to show an explicit
    error before the checkout is actually attempted
    """
    issued_to = None
    if item.issued_to:
        issued_to = item.issued_to.username
    try:
        return sanic.response.json({'available': item.available, 'issued_to': {'name': issued_to, 'uid': item._issued_uid}}, status=200)
    except AttributeError:
        sanic.exceptions.abort(422, "User does not exist.")

@media.post('/check/out')
@rqst_get('item', 'username', 'location')
@jwtdec.protected()
async def issue_item(rqst, location, username, *, item):
    """
    Checks an item out to a user.
    
    Because of the existence of checkout accounts (which do not have uIDs),
    this cannot take a user ID -- it instead needs the location and username,
    from which the user's identity will be deduced.
    """
    try:
        user = await User.from_identifiers(username, location, app=rqst.app)
    except ValueError as err:
        sanic.exceptions.abort(404, err)
    if user.cannot_check_out or not item.maxes.checkout_duration:
        sanic.exceptions.abort(403, "You aren't allowed to check this item out.")
    if not item.available and user.uid != item._issued_uid:
        # will never be triggered really unless I forget to query /check first
        sanic.exceptions.abort(409, f'Item is checked out to {issued_to}.')
    await item.issue_to(user=user)
    return sanic.response.json({'checked': 'out', 'title': item.title, 'author': item.author, 'image': item.image, 'due': str(item.due_date)}, status=200)

@media.post('/check/in')
@rqst_get('item', 'username', 'location')
@jwtdec.protected()
async def return_item(rqst, location, username, *, item):
    """
    Because adminstrative users can check OTHER people's items in,
    I cannot do this solely by grabbing the uID, a similar effect
    to issue_item().
    Instead I have to ask for the username+location of the member
    whose item is being checked in.
    """
    try:
        user = await User.from_identifiers(username, location, app=rqst.app)
    except ValueError as e:
        sanic.exceptions.abort(404, e)
    if user.is_checkout or not user.perms.can_return_items:
        sanic.exceptions.abort(403, "You aren't allowed to return items.")
    if item.fines:
        sanic.exceptions.abort(409, "This item's fines must be paid off before it is returned.")
    await item.check_in()
    return sanic.response.raw(b'', status=204)

@media.get('/check/verbose')
@rqst_get('item')
async def get_media_full_status(rqst, *, item):
    """
    I thought I might implement a status page, but never found a need to.
    """
    return NotImplemented
  # return sanic.response.json(item.status, status=200)

@media.get('/info')
@rqst_get('item')
@jwtdec.protected()
async def get_media_info(rqst, *, item):
    """Serve all of a media item's important attributes."""
    return sanic.response.json({'info': item.to_dict()}, status=200)

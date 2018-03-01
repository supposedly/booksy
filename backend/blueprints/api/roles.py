"""/api/role-attrs"""
import sanic
import sanic_jwt as jwt
from sanic_jwt import decorators as jwtdec

from . import uid_get, rqst_get
from . import Location, Role, MediaType, MediaItem, User

roles = sanic.Blueprint('roles_api', url_prefix='/roles')

@roles.get('/me')
@uid_get()
@jwtdec.protected()
async def provide_me_attrs(rqst, user):
    """
    Provides all attributes - permissions, maxes, and lock thresholds -
    for current user.
    
    Requires current session's Role ID from client.
    """
  # resp = {'rid': user.role.rid, 'perms': user.perms, 'maxes': user.maxes, 'locks': user.locks}
    resp = {i: getattr(user, i) for i in ('perms', 'maxes', 'locks')}
    return sanic.response.json(resp, status=200)

@roles.get('/me/<attr:(perms|maxes|locks)>')
@uid_get()
@jwtdec.protected()
async def provide_specific_me_attr(rqst, user, *, attr):
    """
    Provides a specific attribute (of perms/maxes/locks) for requesting role.
    """
    if attr not in ('perms', 'maxes', 'locks'):
        # won't ever be called, for obvious reason
        # (that is, bc of the regex in the roles.get deco)
        sanic.exceptions.abort(422)
    return sanic.response.json(getattr(user, attr), status=200)

@roles.post('/edit')
@rqst_get('role', 'user', 'name', 'seqs')
@jwtdec.protected()
async def edit_role(rqst, role, user, *, name, seqs):
    """
    Edits a role's attributes, taking in a sequence (seqs) of its
    perms, maxes, and locks, plus its modified name.
    """
    new = Role.attrs_from(kws=seqs) # new[0] == perms
    if user.perms.raw <= new[0].raw or not user.perms.can_manage_roles:
        # Users can only modify roles *below* them in perms hierarchy
        sanic.exceptions.abort(403, "You aren't allowed to modify this role.")
    if name.lower() in ('admin', 'organizer', 'subscriber'):
        sanic.exceptions.abort(401, 'That name is reserved.')
    await role.set_attrs(*new, name=name)
    return sanic.response.raw(b'', status=204)

@roles.put('/delete')
@rqst_get('user', 'role')
@jwtdec.protected()
async def delete_role(rqst, user, *, role):
    if await role.num_members():
        sanic.exceptions.abort(403, "You can't delete a role with members assigned to it.")
    if role.is_default:
        sanic.exceptions.abort("Default roles cannot be deleted.")
    if user.perms.raw <= role.perms.raw or not user.perms.can_manage_roles:
        sanic.exceptions.abort("You aren't allowed to delete this role.")
    await role.delete()
    return sanic.response.raw('', status=204)

@roles.get('/detail')
@rqst_get('role', 'user')
@jwtdec.protected()
async def provide_specific_role(rqst, role, *, user):
    """
    Provides attributes for a requested role.
    """
    if not user.perms.can_manage_roles:
        sanic.exceptions.abort(403, "You aren't allowed to view role properties.")
    return sanic.response.json(role.to_dict(), status=200)

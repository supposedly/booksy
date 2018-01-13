"""/api/role-attrs"""
import sanic
import sanic_jwt as jwt
from sanic_jwt import decorators as jwtdec

from .import uid_get, rqst_get
from .import Location, Role, MediaType, MediaItem, User

roles = sanic.Blueprint('role_attrs_api', url_prefix='/roles')

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
async def provide_specific_me_attr(rqst, user, attr):
    """
    Provides a specific attribute of the three above for current role.
    
    Requires current session's Role ID from client.
    """
    if attr not in ('perms', 'maxes', 'locks'):
        # won't ever be called, for obvious reason
        sanic.exceptions.abort(422)
    resp = getattr(user, attr)
    return sanic.response.json(resp, status=200)

@roles.post('/edit')
@rqst_get('role', 'user', 'name', 'seqs')
@jwtdec.protected()
async def edit_role(rqst, role, user, name, seqs):
    if not user.perms.can_manage_roles:
        sanic.exceptions.abort(403, "You aren't allowed to modify roles.")
    await role.set_attrs(*Role.attrs_from(kws=seqs), name=name)
    return sanic.response.raw(b'', status=204)

@roles.put('/delete')
@rqst_get('role', 'user')
@jwtdec.protected()
async def delete_role(rqst, role, user):
    if await role.num_members():
        sanic.exceptions.abort(403, "You can't delete a role with members assigned to it.")
    if role.name.lower() in ('admin', 'organizer', 'subscriber'): # sorta useless because they can change the name (I should've put a flag in the DB for this)
        sanic.exceptions.abort("Default roles cannot be deleted.")
    await role.delete()
    return sanic.response.raw('', status=204)

@roles.get('/detail')
@rqst_get('role', 'user')
@jwtdec.protected()
async def provide_specific_role(rqst, role, user):
    """
    Provides attributes for a requested role.
    """
    if not user.perms.can_manage_roles:
        sanic.exceptions.abort(403, "You aren't allowed to modify roles.")
    return sanic.response.json(role.to_dict(), status=200)

"""/api/role-attrs"""
import sanic
import sanic_jwt as jwt
from sanic_jwt import decorators as jwtdec

from .import uid_get, rqst_get
from .import Location, Role, MediaType, MediaItem, User

roles = sanic.Blueprint('role_attrs_api', url_prefix='/roles')

@roles.get('/my-attrs')
@uid_get('role')
@jwtdec.protected()
async def provide_role_attrs(rqst, role):
    """
    Provides all attributes - permissions, maxes, and lock thresholds -
    for current role.
    
    Requires current session's Role ID from client.
    """
    resp = {'id': role.rid, 'perms': role.perms, 'maxes': role.maxes, 'locks': role.locks}
    return sanic.response.json(resp, status=200)

@roles.get('/my-attrs/<attr:(perms|maxes|locks)>')
@uid_get('role')
@jwtdec.protected()
async def provide_specific_role_attr(rqst, role, attr):
    """
    Provides a specific attribute of the three above for current role.
    
    Requires current session's Role ID from client.
    """
    if attr not in ('perms', 'maxes', 'locks'):
        # won't ever be called, for obvious reason
        sanic.exceptions.abort(422)
    resp = getattr(role, attr)
    return sanic.response.json(resp, status=200)

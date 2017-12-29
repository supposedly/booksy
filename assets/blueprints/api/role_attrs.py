"""/api/role-attrs"""
import sanic
import sanic_jwt as jwt
from sanic_jwt import decorators as jwtdec

from ...typedef import Role

role = sanic.Blueprint('role_attrs_api', url_prefix='/role-attrs')

@role.get('/')
@jwtdec.protected()
async def provide_role_attrs(rqst):
    """
    Provides all attributes - permissions, maxes, and lock thresholds -
    for current role.
    
    Requires current session's Role ID from client.
    """
    try:
        role = await Role(rqst.raw_args['rid'], rqst.app)
    except KeyError: # if no role ID given as param
        sanic.exceptions.abort(422)
    role = await Role(rid, rqst.app)
    resp = {'perms': role.perms, 'maxes': role.maxes, 'locks': role.locks}
    return sanic.response.json(resp, status=200)

@role.get('/<attr:(perms|maxes|locks)>')
@jwtdec.protected()
async def provide_specific_role_attr(rqst, attr):
    """
    Provides a specific attribute of the three above for current role.
    
    Requires current session's Role ID from client.
    """
    try:
        role = await Role(rqst.raw_args['rid'], rqst.app)
    except KeyError:
        sanic.exceptions.abort(422, 'No role ID given')
    if attr not in ('perms', 'maxes', 'locks'):
        # won't ever be called, for obvious reason
        sanic.exceptions.abort(422)
    role = await Role(rid, rqst.app)
    resp = getattr(role, attr)
    return sanic.response.json(resp, status=200)

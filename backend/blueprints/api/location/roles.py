"""/location/roles"""
import sanic
from sanic_jwt import decorators as jwtdec

from . import uid_get, rqst_get

roles = sanic.Blueprint('location_roles_api', url_prefix='/roles')


@roles.get('/')
@uid_get('perms', 'location')
@jwtdec.protected()
async def all_roles(rqst, location, *, perms):
    """
    Serves all a location's roles.
    """
    return sanic.response.json({'roles': await location.roles()}, status=200)


@roles.get('/filtered')
@uid_get('perms', 'location')
async def filtered_roles(rqst, location, *, perms):
    """
    Serves the location's roles, filtered so that none have higher permissions than those of
    the logged-in user.
    This is utilized in the member-info screen, where the user will not be allowed to assign
    a role to a member if they themselves do not have a role higher than it in the hierarchy.
    """
    return sanic.response.json({'roles': await location.roles(lower_than=perms.raw)}, status=200)


@roles.post('/add')
@rqst_get('user', 'name', 'seqs')
@jwtdec.protected()
async def add_role_to_location(rqst, user, *, name, seqs):
    """
    Adds a new role, taking a sequence (seqs) of its perms, limits, and locks,
    to the locatin.
    """
    if not user.perms.can_manage_roles:
        sanic.exceptions.abort(403, "You aren't allowed to modify roles.")
    role = await user.location.add_role(name=name, kws=seqs)
    return sanic.response.json({'rid': role.rid}, status=200)

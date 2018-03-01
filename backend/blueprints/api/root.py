"""/api"""
import sanic
import sanic_jwt as jwt
from sanic_jwt import decorators as jwtdec

from . import uid_get, rqst_get
from . import Location, Role, MediaType, MediaItem, User

root = sanic.Blueprint('attrs_api', url_prefix='')

@root.get('/attrs')
@uid_get('perms', 'location')
@jwtdec.protected()
async def serve_attrs(rqst, perms, location):
    """
    Catch-all combination of location-related attributes.
    """
    resp = {
      'types': await location.media_types(),
      'genres': await location.genres(),
      'color': location.color,
      }
    resp['names'] = {
      'perms': [
        None, # -- line 42 --
        'Manage accounts (edit names, usernames and passwords)',
        'Manage media (add items, edit metadata)',
        'Manage roles (edit permissions and names)',
        None, # -- line 43 --
        'Generate & view reports',
        'Return items',
        ],
      'maxes': [
        'Maximum checkout duration allowed (in weeks)',
        'Number of renewals allowed per checkout',
        'Number of holds allowed at a time',
        ],
      'locks': [
        'Maximum concurrent checkouts allowed',
        'Maximum $USD in fines allowed at a time',
        ]
      }
    if perms.can_manage_location: # Don't want to expose these to someone not allowed to modify them
        resp['names']['perms'][0] = 'Manage location (edit name, info, etc.)'
        resp['names']['perms'][4] = (
          'Create administrative roles '
          '(ones that can provide other roles with '
          'the "Manage location" permission)'
          )
    return sanic.response.json(resp, status=200)

"""/api"""
import sanic
import sanic_jwt as jwt
from sanic_jwt import decorators as jwtdec

from .import uid_get, rqst_get
from .import Location, Role, MediaType, MediaItem, User

root = sanic.Blueprint('attrs_api', url_prefix='')

@root.get('/attrs')
@uid_get('perms', 'location')
@jwtdec.protected()
async def serve_attrs(rqst, perms, location):
    """
    Catch-all combination of the location-related attributes
    """
    resp = {}
    resp['types'] = await location.media_types()
    resp['genres'] = await location.genres()
    resp['names'] = {
      'perms': [
      # 'Manage location (edit name, info, etc.)',
        'Manage accounts (edit names, usernames and passwords)',
        'Manage media (add items, edit metadata)',
        'Manage roles (edit permissions and names)',
       # Create administrative roles (yada yada)
        'Generate & view reports',
        'Return items',
        ],
      'maxes': [
        'Maximum checkout duration allowed (in weeks)',
        'Number of renewals allowed at a time',
        'Number of holds allowed at a time',
        ],
      'locks': [
        'Maximum concurrent checkouts allowed',
        'Maximum $USD in fines allowed at a time',
      ]
    }
    if perms.can_manage_location:
        resp['names']['perms'].insert(0, 
          'Manage location (edit name, info, etc.)')
        resp['names']['perms'].insert(3, 
          'Create administrative roles '
          '(ones that can provide other roles with '
          'the "Manage location" permission)')
    return sanic.response.json(resp, status=200)

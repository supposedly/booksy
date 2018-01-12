"""/stock/attrs"""
import sanic
import sanic_jwt as jwt
from sanic_jwt import decorators as jwtdec

from .import uid_get, rqst_get
from .import Location, Role, MediaType, MediaItem, User
from ...resources import Perms, Maxes, Locks

attrs = sanic.Blueprint('attr_stock', url_prefix='/attrs')

@attrs.get('/names')
async def serve_attr_names(rqst):
    # return sanic.response.json({i.__name__.lower(): filter(bool, i._names) for i in (Perms, Maxes, Locks)}, status=200)
    res = {
      'perms': [
        'Manage location (edit name, info, etc.)',
        'Manage accounts (edit names, usernames and passwords)',
        'Manage media (add items, edit metadata)',
        'Manage roles (edit permissions and names)',
        'Create administrative roles (i.e. ones that can create other administrative roles and give them the "Mange location" permission)',
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
    return sanic.response.json(res, status=200)

@attrs.get('/signup-form')
async def serve_signup_form(rqst):
    res = {}
    return sanic.response.json(res)

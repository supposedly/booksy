"""/stock/buttons"""
import sanic
import sanic_jwt as jwt
from sanic_jwt import decorators as jwtdec

from ...typedef import Location, Role, MediaItem, MediaType, User

btn = sanic.Blueprint('button_stock', url_prefix='/buttons')

@btn.get('/main-header')
async def expose_header_buttons(rqst):
    """
    Essentially a static resource; don't think I have anything to add.
    Keeping it here, though, so I can change it ... if I ever want to.
    
    Serves header buttons (via the angular webapp's HeadButtonService)
    to display at the top of every page.
    
    Requires nothing from client, being static.
    """
    resp = [{"text": 'home'}, {"text": 'help'}, {"text": 'about'}]
    return sanic.response.json(resp, status=200)

@btn.get('/home-sidebar')
@jwtdec.protected()
async def expose_home_sidebar_buttons(rqst):
    """
    Almost a static resource like above, but this time varies depending
    on user's role. I'm ALMOST positive it should work alright this way
    (as long as I understand... HTTP requests and Angular5 services and
    whatnot).
    
    Serves sidebar buttons to display in the "Home" tab of the webapp.
    Varies depending on user's permissions; ie if a non-administrative
    member visits the home page, this endpoint will not serve them the
    'generate reports' or 'manage media' or 'manage location' buttons.
    
    Default, available-to-everyone buttons are:
    - Checkout
    - Find media (search)
    - My dashboard (list of member's own media)
    - My account (modify/view member's own account info)
    
    Additional buttons, all requiring "Chieftain"-tier perms:
    - Reports (view status over a time period)
    - Manage Media (manage location's media items)
    - Manage Location (manage location's info)
    
    Requires current session's Role ID from client.
    """
    # Doesn't matter how long my function names are because I'm not
    # calling them directly, heh
    try:
        role = await Role(rqst.raw_args['rid'], rqst.app)
    except KeyError:
        sanic.exceptions.abort(422, 'No role ID given')
    except Exception:
        sanic.exceptions.abort(500)
    side_buttons = [
      {"text": 'checkout'},
      {"text": 'find media', "dest": '/search'},
      {"text": 'my dashboard', "dest": '/dashboard'},
      {"text": 'my account', "dest": '/account'},
    ]
    if role.perms.can_generate_reports: # self-documenting!
        side_buttons.append({"text": 'reports', "color": '#9feca0'})
    if role.perms.can_manage_media:
        side_buttons.append({"text": 'manage media', "dest": '/media', "color": '#ec9fa0'})
    if int(role.perms.bin[0:5]):
        # if has any of the following permissions:
        # Manage Location Info, Manage Accounts, Manage Roles,
        # Create Administrative Roles, Manage Media
        side_buttons.append({"text": 'manage location', "dest": '/manage', "color": '#ec9fa0'})
    return sanic.response.json(side_buttons, status=200)

@btn.get('/mgmt-header')
@jwtdec.protected()
async def expose_management_buttons(rqst):
    """
    Much like expose_home_sidebar_buttons() above, this function serves
    the 'management header' buttons, encountered when any Chieftain is
    able to visit the 'Manage Location' item in the Home-page sidebar.
    
    Available buttons:
    - Location info (requires Administrator)
    - Create/delete accounts (requires Manage Accounts perm)
    - Roles and Permissions (requires Manage Roles perm)
    
    Requires current session's Role ID from client.
    """
    try:
        role = await Role(rqst.raw_args['rid'], rqst.app)
    except KeyError:
        sanic.exceptions.abort(422, 'No role ID given')
    head_buttons = []
    if role.perms.can_manage_locations:
        head_buttons.append({"text": 'location info', "dest": '/manage/location'}
    if role.perms.can_manage_accounts:
        head_buttons.append({"text": 'create/delete accounts', "dest": '/manage/accounts'})
    if role.perms.can_manage_roles:
        head_buttons.append({"text": 'roles and permissions', "dest": '/manage/roles'})
    return sanic.response.json(head_buttons, status=200)

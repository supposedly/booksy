"""/api/signup"""
import sanic
import sanic_jwt as jwt
from sanic_jwt import decorators as jwtdec

from .import uid_get, rqst_get
from .import Location, Role, MediaType, MediaItem, User

signup = sanic.Blueprint('signup_api', url_prefix='/signup')

@signup.post('/library')
async def create_location(rqst):
    """
    App will prompt user to enter a:
      location name `name',
      color `color',
      MAYBE NOT `image',
      checkout account password `pwhash',
      admin account password `admin_pwhash',
      admin name `admin_name',
      admin email and/or phone. `admin_email', `admin_phone'
      
      ALSO BOOLEAN checkbox asking "Does your location funnel all
      user traffic through a single IP address? (If so, check this box
      to allow us to automatically detect when your users are logging
      in from here -- that way, we can infer their location ID and
      spare them from having to keep entering it to sign in!
    """
    await Location.instate(rqst.json) # just gonna have Angular do the ordering
    return sanic.response.raw(status=200)
    

@signup.post('/member')
async def member_signup(rqst):
    sanic.exceptions.abort(404)
    return None
    # hmm

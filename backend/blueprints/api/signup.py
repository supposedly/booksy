"""/api/signup"""
import asyncio
import bcrypt

import sanic

from . import Location

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
    sanic.exceptions.abort(501, "Left unimplemented for FBLA demo.")
    kwargs = rqst.json
    app_loop = asyncio.get_event_loop()
    kwargs['pwhash'] = await app_loop.run_in_executor(rqst.app.ppe, bcrypt.hashpw, kwargs['password'], bcrypt.gensalt(15))
    await Location.instate(rqst, **kwargs)  # just gonna have Angular get kwargs in order here
    return sanic.response.raw(status=200)
    

@signup.post('/member')
async def member_signup(rqst):
    """
    I was originally entertaining the idea of allowing
    users to sign up on their own and select a location
    ID to be added to, but ended up opting not to.
    
    Members can instead be added to a location by its
    operators.
    """
    sanic.exceptions.abort(410, "Not implemented.")
    return NotImplemented

#TODO IF HAVE TIME: CHANGE ALL YOUR AWFUL FUNCTIONS TO METHODS OF USER/ROLE/MEDIA/LOCATION CLASS
# update: had time :-)

import asyncio
import itertools
import os
import struct
from urllib import parse

import aioredis
import asyncpg
import bcrypt
import sanic
import uvloop
import sanic_jwt as jwt
import sanic_jwt.decorator as jwtdec
from sanic import Sanic

import app_setup
from type_container import Location, Role, MediaItem, MediaType, User


# Create a Sanic application for this file.
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
app = Sanic(__name__)

async def auth(rqst, *args, **kwargs):
    """
    /auth
    Authenticate a user's credentials through sanic-jwt to give them
    access to the application.
    """
    try:
        # standard fare. get username and password from the app's request
        uid = request.json['username'].lower()
        user_type = request.json['type'].lower()
        password = request.json['password'].encode('utf-8')
    except KeyError:
        # this will always be handled client-side regardless, but...
        # ...just in case, I guess
        raise jwt.exceptions.AuthenticationFailed('Missing username or password.')
    # look up the username/pw pair in the database
    async with app.pg_pool.acquire() as conn:
        try:
            query = """SELECT lid FROM locations WHERE ip == $1::text"""
            lid = await conn.execute(query, rqst.remote_addr)
        except AttributeError:
            raise jwt.exceptions.AuthenticationFailed('Invalid username or password.')
        query = """SELECT pwhash FROM members WHERE uid = $1::int"""
        pwhash = await conn.fetch(query, uid)
        if uid is None or not bcrypt.checkpw(password, pwhash):
                # (we shouldn't specify which of pw/username is invalid lest an attacker
                # use the info to enumerate possible passwords/usernames)
                raise jwt.exceptions.AuthenticationFailed('Invalid username or password.')
    return await User.from_identifiers(uid, lid)

async def retrieve_user(rqst, payload, *args, **kwargs):
    """/auth/me"""
    if payload:
        uid = payload.get('user_id', None)
        return await User(uid, app)
    else:
        return None

async def store_rtoken(uid, rtoken, *args, **kwargs):
    """/auth/refresh"""
    async with app.rd_pool.get() as conn:
        await conn.set(uid, rtoken)

async def retrieve_rtoken(uid, *args, **kwargs):
    """/auth/refresh"""
    async with app.rd_pool.get() as conn:
        return await conn.get(uid)

# Initialize with JSON Web Token (JWT) authentication for logins.
# First argument for it is the Sanic app object, and subsequent
# parameters are helper functions for authentication & security.
jwt.initialize(app,
  authenticate=authenticate,
  retrieve_user=retrieve_user, # could probably be a lambda but meh
  store_refresh_token=store_rtoken,
  retrieve_refresh_token=retrieve_rtoken)

# Config variables for JWT authentication. See sanic-jwt docs on GitHub
# for more info.
app.config.SANIC_JWT_COOKIE_SET = True # Store token in cookies instead of making the client webapp send them
app.config.SANIC_JWT_REFRESH_TOKEN_ENABLED = True
app.config.SANIC_JWT_SECRET = os.getenv('SANIC_JWT_SECRET') # it's a secret to everybody!
app.config.SANIC_JWT_CLAIM_IAT = True # perhaps for invalidating long sessions
app.config.SANIC_JWT_CLAIM_NBF = True # why not, more security
app.config.SANIC_JWT_CLAIM_NBF_DELTA = 2 # token becomes checkable 2s after creation

# app.static('/', '/dist/index.html/') # Route everything to Angular's file, even if the user navigates directly to it

@app.listener('before_server_start')
async def set_up_dbs(app, loop):
    app.pg_pool = await asyncpg.create_pool(dsn=os.getenv('DATABASE_URL'), loop=loop)
    async with app.pg_pool.acquire() as conn:
        await res.create_pg_tables(conn)
    if os.getenv('REDIS_URL', None) is None: # can't do nothin bout this
        app.config.SANIC_JWT_REFRESH_TOKEN_ENABLED = False
    else:
        app.rd_pool = await aioredis.create_pool(
                      os.getenv('REDIS_URL'),
                      minsize=5,
                      maxsize=10,
                      loop=loop)

@app.listener('before_server_stop')
async def close_dbs(app, loop):
    await app.pg_pool.close()
    app.rd_pool.close()
    await app.rd_pool.wait_closed()
    print('Shutting down.')

@app.get('/stock/buttons/main-header')
async def expose_header_buttons(rqst):
    resp = [{"text": 'home'}, {"text": 'help'}, {"text": 'about'}]
    return sanic.response.json(resp)

@app.get('/stock/buttons/sidebar')
@jwtdec.protected()
async def expose_side_buttons(rqst):
    try:
        rid = rqst.raw_args['rid']
    except KeyError: # if no role ID given as param
        sanic.exceptions.abort(422)
    role = await Role(rid, app)
    perms = role.perms
    side_buttons = [
      {"text": 'checkout'},
      {"text": 'find media', "dest": '/search'},
      {"text": 'my dashboard', "dest": '/dashboard'},
      {"text": 'my account', "dest": '/account'},
    ]
    if perms['generate reports']:
        side_buttons.append({"text": 'reports', "color": '#9feca0'})
    if perms['manage media']:
        # if has permission to Manage Media
        side_buttons.append({"text": 'manage media', "dest": '/media', "color": '#ec9fa0'})
    if if any(perms[i] for i in ('manage location info', 'manage accounts', 'manage roles', 'create administrative roles', 'manage media')):
        # if has any of the following permissions:
        # Manage Location Info, Manage Accounts, Manage Roles,
        # Create Administrative Roles, Manage Media
        side_buttons.append({"text": 'manage location', "dest": '/manage', "color": '#ec9fa0'})
    return sanic.response.json(side_buttons)

@app.get('/stock/buttons/mgmt-header')
@jwtdec.protected()
async def expose_management_buttons(rqst):
    try:
        role = await Role(rqst.raw_args['rid'])
    except KeyError:
        sanic.exceptions.abort(422)
    head_buttons = []
    if int(perms[0]):
        # if has permission to Manage Location Info
        head_buttons.append({"text": 'location info', "dest": '/manage/location'}
    if int(perms[1]):
        # if has permission to Manage Accounts
        head_buttons.append({"text": 'create/delete accounts', "dest": '/manage/accounts'})
    if int(perms[2]):
        # if has permission to Manage Roles
        head_buttons.append({"text": 'roles and permissions', "dest": '/manage/roles'})
    return sanic.response.json(head_buttons)

@app.get('/stock/role-perms')
@jwtdec.protected()
async def give_role_perms(rqst):
    try:
        rid = rqst.raw_args['rid']
    except KeyError: # if no role ID given as param
        sanic.exceptions.abort(422)
    perms, maxes, locks = await get_role_perms(rid)
    resp = {
      "perms": {perm: boolean for perm, boolean in zip(res.permissions, perms)},
      "maxes": {name: value for name, value in zip(res.maximums, maxes)},
      "locks": {lock: value for lock, value in zip(res.acct_locks, locks)}
    }
    return sanic.response.json(resp, status=200)

@app.get('/api/location/is-registered')
async def is_location_registered(rqst):
    if not rqst.remote_addr:
        sanic.exceptions.abort(422, 'Unobtainable or unregistered IP')
    async with app.pg_pool.acquire() as conn:
        query = """SELECT lid FROM locations WHERE """

@app.post('/api/media/check/out')
@jwtdec.protected()
async def issue_item(rqst):
    try:
        mid = rqst.raw_args['mid']
        uid = rqst.raw_args['uid']
    except KeyError:
        sanic.exceptions.abort(422)
    if not await check_media_perms(uid):
        sanic.exceptions.abort(422)
    

@app.post('/api/media/check/in')
@jwtdec.protected()
async def return_item(rqst):
    async with app.pg_pool.acquire() as conn:
        

@app.get('/api/media/check')
async def get_media_status(rqst):
    return

@app.get('/api/media/info')
@jwtdec.protected()
async def get_media_info(rqst):
    return

@app.post('/api/media/acquire')
@jwtdec.protected()
async def add_media_item_to_db(rqst): # doesn't matter how long my function names are because I'm not going to be calling them directly, heh
    async with app.pg_pool.acquire() as conn:
        
@app.post('/api/media/remove')
@jwtdec.protected()
async def remove_media_item_from_db(rqst):
    async with app.pg_pool.acquire() as conn:

@app.post

app.run(host='0.0.0.0', port=os.environ.get('PORT', 8000), debug=True, workers=5)

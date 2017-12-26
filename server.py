import asyncio, uvloop
import asyncpg, aioredis
import itertools
import os, struct
import bcrypt, hashlib
import sanic
from urllib import parse

import sanic_jwt as jwt
import sanic_jwt.decorator as jwtdec
from sanic import Sanic

import app_setup as setup

# Create a Sanic application for this file.
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
app = Sanic(__name__)

async def get_user_obj(username, conn=None, *, close=None):
    if conn is None:
        conn = await app.pg_pool.acquire()
        close = 1
    query = """SELECT lid, rid, manages, email, phone, type FROM members WHERE username = ($1)::text;"""
    lid, rid, manages, email, phone, user_type = await conn.fetch(query, uid)
    if close is not None:
        await conn.close()
    return {"user_id": uid, "lid": lid, "manages": manages, "rid": rid, "email": email, "phone": phone, "type": user_type}

async def auth(request, *args, **kwargs):
    """
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
        raise jwt.exceptions.AuthenticationFailed("Missing username or password.")
    # look up the username/pw pair in the database
    async with app.pg_pool.acquire() as conn:
        query = """SELECT pwhash FROM members WHERE uid = ($1)::int"""
        try:
            if not uid.isdigit(): # convert username to ID if not already
                uid = await conn.fetch("""SELECT uid FROM members WHERE username = ($1)""")
            pwhash = await conn.fetch(query, uid)
            
            if not bcrypt.checkpw(password, pwhash):
                # (we shouldn't specify which of pw/username is invalid lest an attacker
                # use the info to enumerate possible passwords/usernames)
                raise jwt.exceptions.AuthenticationFailed("Invalid username or password.")
        
        except: # if username/uid is invalid -- but except what in particular?
            raise exceptions.AuthenticationFailed("Invalid username or password.")
    return await get_user_obj(uid, conn)

async def get_user(rqst, payload, *args, **kwargs):
    if payload:
        uid = payload.get('user_id', None)
        return await get_user_obj(uid)
    else:
        return None

async def store_rtoken(uid, rtoken, *args, **kwargs):
    async with app.rd_pool.get() as conn:
        await conn.set(uid, rtoken)

async def get_rtoken(uid, *args, **kwargs):
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
"""app.config.SANIC_JWT_USER_ID = 'uid'"""
# UNFORTUNATELY sanic-jwt doesn't always respect the above so I'll have to leave it untouched for now
app.config.SANIC_JWT_COOKIE_SET = True # Store token in cookies instead of making the application send them
app.config.SANIC_JWT_REFRESH_TOKEN_ENABLED = True
app.config.SANIC_JWT_SECRET = os.environ.get('SANIC_JWT_SECRET') # it's a secret to everybody!
app.config.SANIC_JWT_CLAIM_IAT = True # perhaps for invalidating long sessions
app.config.SANIC_JWT_CLAIM_NBF = True # why not, more security
app.config.SANIC_JWT_CLAIM_NBF_DELTA = 2 # token becomes checkable 2s after creation

# app.static('/', '/dist/index.html/') # Route everything to Angular's file, even if the user navigates directly to it

@app.listener('before_server_start')
async def setup_dbs(app, loop):
    redis_db = parse.urlparse(os.getenv('REDIS_URL', None))
    if redis_db.hostname is None: # can't do nuthin bout this
        app.config.SANIC_JWT_REFRESH_TOKEN_ENABLED = False
    else:
        app.rd_pool = await aioredis.create_pool(
                      os.getenv('REDIS_URL'),
                      minsize=5,
                      maxsize=10,
                      loop=loop
                      )
    app.pg_pool = await asyncpg.create_pool(dsn=os.getenv('DATABASE_URL'), loop=loop)
    async with app.pg_pool.acquire() as conn:
        await setup.create_pg_tables(conn)

async def get_role_perms(rid):
    async with app.pg_pool.acquire() as conn:
        query = """SELECT permissions, maxes, locks FROM roles WHERE rid = ($1)::int"""
        perms, maxes, locks = await conn.fetch(query, rid)
        
        # straightforward, convert number to binary string
        # e.g. 45 --> '10110100'
        perms = format(int(perms), '<016b') 
        
        # split an unsigned long into its constituent bytes
        maxes = struct.unpack('8B', struct.pack('<q', int(maxes)))
        locks = struct.unpack('8B', struct.pack('<q', int(locks)))
        # e.g. 200449 --> (1, 15, 3, 0, 0, 0, 0, 0)
        # because 200449 is binary 0b000000110000111100000001
        # and 0b00000011 == 3, 0b00001111 == 15, 0b00000001 == 1
        # All the extra (0,)s are in case I ever decide to add more
        # locks/permissions, so I can just slot it into one of the
        # existing 0 values without having to refactor the entire database
        # funnily enough I can never use the last byte bc it's signed
    return perms, maxes, locks

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
    perms, *_ = await get_role_perms(rid)
    # *_ is unpacking the remaining two values into a single
    # throwaway variable _, because we only care about perms here
    side_buttons = [
      {"text": 'checkout'},
      {"text": 'find media', "dest": '/search'},
      {"text": 'my dashboard', "dest": '/dashboard'},
      {"text": 'my account', "dest": '/account'},
    ]
    if int(perms[5]):
        # if has permission to Generate Reports
        side_buttons.append({"text": 'reports', "color": '#9feca0'})
    if int(perms[4]):
        # if has permission to Manage Media
        side_buttons.append({"text": 'manage media', "dest": '/media', "color": '#ec9fa0'})
    if int(perms[0:5]):
        # if has any of the following permissions:
        # Manage Location Info, Manage Accounts, Manage Roles,
        # Create Administrative Roles, Manage Media
        side_buttons.append({"text": 'manage location', "dest": '/manage', "color": '#ec9fa0'})
    return sanic.response.json(side_buttons)

@app.get('/stock/buttons/mgmt-header')
@jwtdec.protected()
async def expose_management_buttons(rqst):
    try:
        rid = rqst.raw_args['rid']
    except KeyError:
        sanic.exceptions.abort(422)
    perms, *_ = await get_role_perms(rid)
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

@app.route('/stock/role-perms')
@jwtdec.protected()
async def give_role_perms(rqst):
    try:
        rid = rqst.raw_args['rid']
    except KeyError: # if no role ID given as param
        sanic.exceptions.abort(422)
    perms, maxes, locks = await get_role_perms(rid)
    resp = {
      "perms": {perm: boolean for perm, boolean in zip(setup.permissions, perms)},
      "maxes": {name: value for name, value in zip(setup.maximums, maxes)},
      "locks": {lock: value for lock, value in zip(setup.acct_locks, locks)}
    }
    return sanic.response.json(resp, status=200)

@app.post('/api/check/out')
async def issue_item(rqst):
    try:
        mid = rqst.raw_args['mid']
    except KeyError:
        sanic.exceptions.abort(422)
    

@app.post('/api/check/in')
async def return_item

@app.post('/api/media/add')
async def add_item_to_db(rqst):
    async with app.pg_pool.acquire() as conn:
        


app.run(host='0.0.0.0', port=os.environ.get('PORT', 8000), debug=True, workers=5)

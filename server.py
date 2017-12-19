import asyncio, uvloop
import asyncpg#, asyncio_redis
import itertools
import os, struct
import bcrypt, hashlib
import sanic
import sanic_jwt as jwt
import sanic_jwt.decorator as jwtdec
import app_setup as setup
from sanic import Sanic
from urllib import parse
from app_setup import User, authenticate # my own class for setting things up without uglifying this prgm

# Create a Sanic application for this file, then proceed to
# initialize with JSON Web Token (JWT) authentication for logins.
# First argument for jwt.initialize is the Sanic app object, and
# second argument is the function (here imported to avoid clogging
# global namespace) that JWT should call for authentication.
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
app = Sanic(__name__)
jwt.initialize(app, authenticate)

# Config variables for JWT authentication. See sanic-jwt docs on GitHub
# for more info.
app.config.SANIC_JWT_USER_ID = 'uid'
app.config.SANIC_JWT_SECRET = os.environ.get('SANIC_JWT_SECRET') # it's a secret to everybody!
app.config.SANIC_JWT_CLAIM_IAT = True # perhaps for invalidating long sessions
app.config.SANIC_JWT_CLAIM_NBF = True # why not, more security
app.config.SANIC_JWT_CLAIM_NBF_DELTA = 2 # token becomes checkable 2s after creation

# app.static('/', '/dist/index.html/') # Route everything to Angular's file, even if the user navigates directly to it

@app.listener('before_server_start')
async def setup_dbs(app, loop):
    app.pg_pool = await asyncpg.create_pool(dsn=os.environ.get('DATABASE_URL'), loop=loop)
    # WILL REMOVE this context manager. It's just here because I don't have psql on my
    # computer and therefore no way to manage the database on my own lol
    async with app.pg_pool.acquire() as conn:
        query = """
        CREATE TABLE locations (
          lid BIGSERIAL PRIMARY KEY,
          username TEXT UNIQUE,
          name TEXT,
          ip TEXT UNIQUE,
          pwhash TEXT,
          fine_amt NUMERIC DEFAULT 0.10,
          fine_interval INT DEFAULT 1
        );
        CREATE TABLE members (
          uid BIGSERIAL PRIMARY KEY,
          username TEXT UNIQUE,
          fullname TEXT,
          email TEXT,
          phone TEXT,
          lid TEXT,
          manages BOOL,
          rid BIGINT,
          pwhash TEXT,
          extra TEXT
        );
        CREATE TABLE items (
          mid BIGSERIAL PRIMARY KEY,
          type TEXT,
          isbn TEXT,
          lid BIGINT,
          title TEXT,
          author TEXT,
          published DATE,
          genre TEXT,
          issuedto BIGINT,
          days_overdue INT,
          fines NUMERIC,
          acquired TIMESTAMP
        );
        CREATE TABLE holds (
          mid BIGINT,
          uid BIGINT,
          PRIMARY KEY(mid, uid)
        );
        CREATE TABLE roles (
          rid BIGSERIAL PRIMARY KEY,
          lid BIGINT,
          name TEXT,
          permissions SMALLINT,
          maxes BIGINT,
          locks BIGINT
        );
        """
        await conn.execute(query)

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

@app.route('/api/roles')
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

@app.get('/stock/sidebuttons')
@jwtdec.protected()
async def expose_side_buttons(rqst):
    try:
        rid = rqst.raw_args['rid']
    except KeyError: # if no role ID given as param
        sanic.exceptions.abort(422)
    perms, *_ = await get_role_perms(rid)
    # *_ is unpacking (google that) the other two values into a
    # throwaway variable _, because we only care about perms here
    side_buttons = [
      {"text": 'checkout'},
      {"text": 'find media', "dest": '/search'},
      {"text": 'my dashboard', "dest": '/dashboard'},
      {"text": 'my account', "dest": '/account'},
    ]
    if int(perms[5]):
        side_buttons.append({"text": 'reports', "color": '#9feca0'}
    if int(perms[4]):
        side_buttons.append({"text": 'manage media', "dest": '/media', "color": '#ec9fa0'})
    if int(perms[0:5]):
        side_buttons.append({"text": 'manage location', "dest": '/manage', "color": '#ec9fa0'})
    return sanic.response.json(side_buttons)

@app.get('/stock/headerbuttons')

@app.get('/api/mgmt-header')
@jwtdec.protected()
async def expose_management_buttons(rqst):
    try:
        rid = rqst.raw_args['rid']
    except KeyError:
        sanic.exceptions.abort(422)
    perms, *_ = await get_role_perms(rid)
    head_buttons = []
    if int(perms[0]):
        head_buttons.append({"text": 'location info', "dest": '/manage/location'}
    if int(perms[1]):
        head_buttons.append({"text": 'create/delete accounts', "dest": '/manage/accounts'})
    if int(perms[2])
          head_buttons.append({"text": 'roles and permissions', "dest": '/roles'})
    return sanic.response.json(head_buttons)

@app.post('/api/add/media')
async def add_item_to_db(rqst):
    try:
        

app.run(host='0.0.0.0', port=os.environ.get('PORT', 8000), debug=True, workers=5)

import asyncio
import itertools
import os
import struct
from concurrent.futures import ProcessPoolExecutor
from glob import glob
from urllib import parse

import aiohttp
import aioredis
import asyncpg
import bcrypt
import binascii
import Crypto
import sanic
import urllib
import uvloop
import sanic_jwt as jwt
from Crypto.Cipher import AES
from Crypto.Util import Counter
from sanic_jwt import decorators as jwtdec
from sanic import Sanic

from backend import setup, deco
from backend.typedef import Location, Role, MediaItem, MediaType, User
from backend.blueprints import bp
from email_verify import send_email

# make it go faster <3
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
# Create a Sanic application for this file.
app = Sanic('Booksy')
# For checking API access later. (See function force_angular())
app.safe_segments = ('?', '.html', '.js', '.ts', '/auth', 'auth/', 'api/', 'stock/')
# "Blueprints", i.e. separate files containing endpoint info to
# avoid clogging up this main file.
# They can be found in ./backend/blueprints
app.blueprint(bp)
app.config.TESTING = False # tells my blueprints to act like the real deal
SIGNUP_KEY = os.getenv('LOCATION_VERIFICATION_KEY') # For location signup token generation

async def authenticate(rqst, *args, **kwargs):
    """
    /auth
    Authenticate a user's credentials through sanic-jwt to give them
    access to the application.
    """
    try:
        # standard fare. get username and password from the app's request
        username = rqst.json['user_id'].lower()
        password = rqst.json['password'].encode('utf-8')
        lid = int(rqst.json['lid'])
    except KeyError:
        # this will always be handled client-side regardless, but...
        # ...just in case, I guess
        raise jwt.exceptions.AuthenticationFailed('Missing username or password.')
    # look up the username/pw pair in the database
    async with app.acquire() as conn:
        query = """SELECT pwhash FROM members WHERE lid = $1::bigint AND username = $2::text"""
        pwhash = await conn.fetchval(query, lid, username)
    bvalid = await app.aexec(app.ppe, bcrypt.checkpw, password, pwhash)
    if not all((username, password, pwhash, bvalid)):
            # (we shouldn't specify which of pw/username is invalid,
            # lest some hypothetical attacker use the info to
            # enumerate possible usernames/passwords)
            return False # raises an error (which is good!)
    return await User.from_identifiers(username=username, lid=lid, app=rqst.app)


async def retrieve_user(rqst, payload, *args, **kwargs):
    """/auth/me"""
    if payload:
        uid = payload.get('user_id', None)
        return await User(uid, rqst.app)

async def store_rtoken(user_id, refresh_token, *args, **kwargs):
    """/auth/refresh"""
    async with app.rd_pool.get() as conn:
        await conn.execute('set', user_id, refresh_token)
        await conn.execute('set', refresh_token, user_id) # for retrieving user from rtoken

async def retrieve_rtoken(user_id, *args, **kwargs):
    """/auth/refresh"""
    async with app.rd_pool.get() as conn:
        await conn.execute('get', user_id)

async def revoke_rtoken(user_id, *args, **kwargs):
    """/auth/logout"""
    async with app.rd_pool.get() as conn:
        await conn.execute('del', await conn.execute('get', user_id))
        await conn.execute('del', user_id)


def _int_from(iv):
    """Take an os.urandom-like string and return int from its hexval"""
    return int(binascii.hexlify(iv), 16)

def encrypt(txt):
    """Encrypt a verification token to put in URL"""
    iv = os.urandom(16)
    ct = Counter.new(128, initial_value=_int_from(iv))
    ciph = AES.new(SIGNUP_KEY, AES.MODE_CTR, counter=ct)
    return base64.urlsafe_b64encode(iv+ciph.encrypt(txt))

def decrypt(enc):
    """Decrypt a verification token from URL"""
    ct = Counter.new(128, initial_value=_int_from(enc[:16]))
    ciph = AES.new(SIGNUP_KEY, AES.MODE_CTR, counter=ct)
    return ciph.decrypt(base64.urlsafe_b64decode(enc[16:]))


# Initialize with JSON Web Token (JWT) authentication for logins.
# First argument passed is the Sanic app object, and subsequent
# parameters are helper functions for authentication & security.
jwt.initialize(
  app,
  authenticate=authenticate,
  retrieve_user=retrieve_user,
  store_refresh_token=store_rtoken,
  retrieve_refresh_token=retrieve_rtoken,
  revoke_refresh_token=revoke_rtoken
  )

# Config variables for JWT authentication.
app.config.SANIC_JWT_COOKIE_SET = True # Store token in cookies instead of making the client webapp send them
                                       # ...this may also open things up for XSRF. but I don't know enough about
                                       # that to be sure as to how to deal with or ameliorate it
app.config.SANIC_JWT_REFRESH_TOKEN_ENABLED = True # Use refresh tokens
app.config.SANIC_JWT_SECRET = os.environ['SANIC_JWT_SECRET'] # it's a secret to everybody!
app.config.SANIC_JWT_CLAIM_IAT = True # perhaps for long sessions

# Get the filenames generated by Angular's AOT build
# (could probably slim this down, sorta just threw stuff together until it worked)
olddir = os.getcwd()
os.chdir('/app/dist')
filenames = 'index.html', 'styles*.css', 'inline*.js', 'main*.js', 'polyfills*.js', 'scripts*.js'
relative = [glob(i) for i in filenames]
os.chdir(olddir)
absolute = [glob(i) for i in map('/app/dist/'.__add__, filenames)]
# Route user requests to Angular's files by redirecting, say,
# /api/whatever to /app/dist/api/whatever
for rel, absol in zip(relative, absolute):
    app.static(rel[0], absol[0])

@app.listener('before_server_start')
async def set_up_dbs(app, loop):
    """
    Establishes a connection to the environment's Postgres and Redis DBs
    for use in (first) authenticating and (then) storing refresh tokens.
    """
    app.session = aiohttp.ClientSession()
    app.sem = asyncio.Semaphore(4, loop=loop) # limit concurrency of aiohttp requests to Google Books
    app.filesem = asyncio.Semaphore(255, loop=loop) # limit concurrency of file reads without forcing one at a time
    
    app.ppe = ProcessPoolExecutor(4)
    app.aexec = loop.run_in_executor
    
    app.pg_pool = await asyncpg.create_pool(dsn=os.getenv('DATABASE_URL'), max_size=15, loop=loop)
    app.acquire = app.pg_pool.acquire
    
    [i.do_imports() for i in [Location, Role, MediaType, MediaItem, User]]
    async with app.acquire() as conn:
        await setup.create_pg_tables(conn)
    if os.getenv('REDIS_URL') is None: # Means I'm testing (don't have Redis on home PC)
        app.config.SANIC_JWT_REFRESH_TOKEN_ENABLED = False
    else:
        app.rd_pool = await aioredis.create_pool(
                        os.getenv('REDIS_URL'),
                        minsize=5,
                        maxsize=15,
                        loop=loop
                        )

@app.listener('before_server_stop')
async def close_dbs(app, loop):
    """
    Gracefully close all acquired connections before shutting off.
    """
    print('Shutting down.')
    await app.pg_pool.close()
    app.rd_pool.close()
    await app.rd_pool.wait_closed()
    await app.session.close()

@app.middleware('request')
async def force_angular(rqst):
    """
    Let through any requestes with URLs containing strings in `safe`,
    because this denotes API access; else redirect to Angular's files
    """
    if not any(i in rqst.url for i in app.safe_segments):
        try:
            url = rqst.url[3+rqst.url.find('://'):]
            path = urllib.parse.quote(url.split('/', 1)[1])
            return sanic.response.redirect(f'/index.html/?redirect={path}')
        except IndexError:
            return sanic.response.redirect('/index.html')

@app.route('/login')
async def login_refresh_fix(rqst):
    """
    Occasionally when you refresh on the login page it'll show an ugly
    error: URL /login not found. This fixes that.
    """
    return sanic.response.redirect('/index.html/?redirect=login')

@app.route('/verify')
async def verify_location_signup(rqst, token):
    """Expects a URL param: ?token=<token>"""

@app.middleware('response')
async def force_no_cache(rqst, resp):
    """
    This is ABSOLUTELY necessary because browsers will otherwise cache
    the sidebar buttons(which, of course, are supposed to be delivered
    by calculating the CURRENT user's permissions, not whomever an
    IP logged in as previously)
    """
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'

if __name__ == '__main__':
    # more than 1 worker and you get too many DB connections :((
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)), debug=True, workers=1)

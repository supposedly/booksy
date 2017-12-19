import asyncio, uvloop
import asyncpg, asyncio_redis
import os, bcrypt, hashlib
import sanic, sanic_session, sanic_auth
import sanic_cors as scors
from sanic import Sanic
from sanic_jinja2 import SanicJinja2 as Jinja2 # abusing this a little bit
from urllib import parse

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
app = Sanic(__name__)
app.config.AUTH_LOGIN_ENDPOINT = 'login'
auth = sanic_auth.Auth(app)
cors = scors.CORS(app)
varpass = Jinja2(app)

app.static('/favicon.ico', './favicon.ico')
app.static('/icons', './icons')
app.static('/head', './static/headfile.html')

@app.listener('before_server_start')
async def setup_dbs(app, loop):
    app.pg_pool = await asyncpg.create_pool(dsn=os.environ.get('DATABASE_URL'), loop=loop)
    async with app.pg_pool.acquire() as conn:
        query = """
        CREATE TABLE locations (
          lid BIGSERIAL PRIMARY KEY,
          username TEXT UNIQUE,
          name TEXT,
          ip TEXT UNIQUE,
          pwhash TEXT,
          extra TEXT
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
          issuedto BIGINT,
          due TIMESTAMP,
          fines MONEY,
          acquired TIMESTAMP,
          extra TEXT
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
    redis_db = parse.urlparse(os.environ.get('REDIS_URL', None))
    if redis_db.hostname is None: # fall back to in-memory storage
        app.sess_interface = sanic_session.InMemorySessionInterface()
    else:
        async def get_rd_pool(app):
            if not hasattr(app, 'rd_pool'):
                app.rd_pool = await asyncio_redis.Pool.create(
                              host=redis_db.hostname,
                              port=redis_db.port,
                              passowrd=redis_db.password,
                              loop=loop,
                              poolsize=10)
            return app.rd_pool
        app.sess_interface = sanic_session.RedisSessionInterface(get_rd_pool)

@app.middleware('request')
async def add_session_to_request(rqst):
    "Access-Control-Allow-Origin"
    print(await app.sess_interface.open(rqst))

@app.middleware('response')
async def save_session(rqst, resp):
    await app.sess_interface.save(rqst, resp)

LOGIN_FORM = '''
<h2>Please sign in</h2>
<p>{}</p>
<form action="" method="POST">
  <input class="username" id="name" name="username"
    placeholder="username" type="text" value=""><br>
  <input class="password" id="password" name="password"
    placeholder="password" type="password" value=""><br>
  <input id="submit" name="submit" type="submit" value="Sign In">
</form>
'''

LIBRARY_LOGIN_FORM = '''
<h2>Please sign in with your username or ID</h2>
<p>{}</p>
<form action="" method="POST">
  <input class="username" id="username" name="username" placeholder="username" type="text" value="">
  <br>
  <input class="password" id="password" name="password" placeholder="password" type="password" value="">
  <br>
  <input class="remember" id="remember" name="remember" type="checkbox" checked> Remember me
  <br>
  <input id="submit" name="submit" type="submit" value="Sign Up">
</form>
'''

SIGNUP_FORM = '''
<h2>Please sign up</h2>
<p>{}</p>
<form action="" method="POST">
  <input class="username" id="username" name="username" placeholder="username" type="text" value="">
  <br>
  <input class="password" id="password" name="password" placeholder="password" type="password" value="">
  <br>
  <input class="email" id="email" name="email" placeholder="email" type="text" value="">
  <br>
  <input class="remember" id="remember" name="remember" type="checkbox" checked> Remember me
  <br>
  <input id="submit" name="submit" type="submit" value="Sign Up">
</form>
'''

SIGNUP_ADMIN = '''
<h2>Sign up for a library</h2>
<p>{}</p>
<form action="" method="POST">
  <input class="locname" id="locname" name="locname" placeholder="name of your institution" type="text" value="">
  <br>
  <input class="username" id="username" name="username" placeholder="your administrator username" type="text" value="">
  <br>
  <input class="password" id="password" name="password" placeholder="password" type="password" value="">
  <br>
  <input class="email" id="email" name="email" placeholder="email" type="text" value="">
  <input id="submit" name="submit" type="submit" value="Sign Up">
</form>
'''

@app.route('/login', methods=['GET', 'POST'])
async def login(rqst):
    if rqst.method == 'POST':
        username = rqst.form.get('username')
        password = rqst.form.get('password').encode('utf-8')
        async with app.pg_pool.acquire() as conn:
            query = """SELECT pwhash FROM {} WHERE uid = ($1)""".format('uid' if username.isdigit() else 'members')
            pwhash = await conn.fetchval(query, username)
            if bcrypt.checkpw(password, pwhash):
                user

@app.route('/signup', methods=['GET', 'POST'])
async def signup(rqst):
    if request.method == 'POST':
        username = rqst.form.get('username')
        if username.isdigit():
            return SIGNUP_FORM.format('Username must contain at least one letter')
        

@app.route('/')
@auth.login_required(user_keyword='user')
async def index(request):
    with open(
    return varpass.render('index.html', 

app.run(host='0.0.0.0', port=os.environ.get('PORT', 8000), debug=True, workers=5)

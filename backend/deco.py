from functools import wraps

import sanic

from .typedef import Location, Role, MediaType, MediaItem, User

async def user_from_rqst(rqst):
    """
    Takes advantage of the app's running refresh-token cache to grab the
    user object attached to a session.
    
    This replaces my god-awful first attempt at the same, which entailed
    that the client send their *own* user ID once logged in - as in, the
    only requirements for being able to access the backend were that you
    were logged in and provided a user ID.
    This in effect meant that *literally anyone* could access *literally
    anything*, as long as they were logged in to an account (& it didn't
    matter which) and sent any extant user ID along with their requests.
    
    This is what I believe is called a "security hole".
    
    So here's this instead which delegates the uID fetching to the back-
    end and back-end only, and if a token doesn't exist in the in-memory
    cache it'll fetch it from the redis db
    """
    rtoken = rqst.app.auth._get_refresh_token(rqst)
    try:
        uid = rqst.app.rtoken_cache[rtoken]
    except KeyError:
        async with rqst.app.rd_pool.get() as conn:
            rqst.app.rtoken_cache[rtoken] = uid = await conn.execute('get', rtoken)
    return await User(uid, rqst.app)


def uid_get(*attrs, user=False):
    """
    Grabs the user ID from a request, turns it into a User object,
    and then gets whatever attributes out of it are requested.
    """
    if 'user' in attrs:
        attrs = tuple(i for i in attrs if i != 'user')
        user = True
    def decorator(func):
        @wraps(func)
        async def wrapper(rqst, *args, **kwargs):
            try:
                user_obj = await user_from_rqst(rqst)
            except KeyError:
                sanic.exceptions.abort(422, 'No user ID given')
            vals = {'user': user_obj} if user or not attrs else {}
            vals.update({i: getattr(user_obj, i) for i in attrs})
            return await func(rqst, *args, **vals, **kwargs)
        return wrapper
    return decorator


def rqst_get(*attrs, user=False, form=False, files=None):
    """
    Grabs the pertinent key from a request, and, if matching
    an object name, converts its value; else just returns its
    value raw.
    e.g. if the requestor wants to convey a media item, they
    can include in their request the parameter {mid: some ID}.
    
    Then, if a route-handler function is decorated in the
    backend with @rqst_get('item'), the wrapper will see
    the 'mid' param and convert it automatically to a media
    item.
    
    If the @rqst_get() call also includes a random argument
    like 'text' that doesn't match any objects, however,
    the 'raw' value of this parameter will be passed from
    request to handler function.
    """
    if 'user' in attrs:
        attrs = tuple(i for i in attrs if i != 'user')
        user = True
    def decorator(func):
        @wraps(func)
        async def wrapper(rqst, *args, **kwargs):
            maps = {'item': (MediaItem, 'mid'), 'location': (Location, 'lid'), 'role': (Role, 'rid')}
            container = rqst.raw_args if rqst.method == 'GET' else rqst.form if form else rqst.json
            try:
                vals = {i: await maps[i][0](container[maps[i][1]], rqst.app) if i in maps else None if i == 'null' else container[i] for i in attrs}
            except KeyError:
                sanic.exceptions.abort(422, 'Missing required attributes.')
            except TypeError as obj:
                sanic.exceptions.abort(404, f'{str(obj)[0].upper()+str(obj)[1:]} does not exist.')
            if form:
                vals = {k: v[0] if isinstance(v, list) and len(v) == 1 else v for k, v in vals.items()}
            if user:
                vals['user'] = await user_from_rqst(rqst)
            if files:
                for name in files:
                    vals[name] = rqst.files.get(name, None)
            return await func(rqst, *args, **vals, **kwargs)
        return wrapper
    return decorator

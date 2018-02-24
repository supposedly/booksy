from functools import wraps

import sanic

from .typedef import Location, Role, MediaType, MediaItem, User


def uid_get(*attrs, user=False):
    def decorator(func):
        @wraps(func)
        async def wrapper(rqst, *args, **kwargs):
            """
            So I don't have to keep typing out the same try-except.
            Grabs the User ID from a request and then gets whatever
            requested info out of it.
            """
            try:
                uid = (rqst.raw_args if rqst.method == 'GET' else rqst.json)['uid']
                user_obj = await User(uid, rqst.app)
            except KeyError:
                sanic.exceptions.abort(422, 'No user ID given')
            vals = {'user': user_obj} if user or not attrs else {}
            vals.update({i: getattr(user_obj, i) for i in attrs})
            return await func(rqst, *args, **vals, **kwargs)
        return wrapper
    return decorator

def rqst_get(*attrs):
    def decorator(func):
        @wraps(func)
        async def wrapper(rqst, *args, **kwargs):
            """
            Another try-except abstraction.
            Grabs requested info from a request and, if matching
            an object name, converts it; else just returns data
            """
            maps = {'item': (MediaItem, 'mid'), 'location': (Location, 'lid'), 'role': (Role, 'rid'), 'user': (User, 'uid')}
            container = rqst.raw_args if rqst.method == 'GET' else rqst.json
            try:
                vals = {i: await maps[i][0](container[maps[i][1]], rqst.app) if i in maps else None if i == 'null' else container[i] for i in attrs}
            except KeyError:
                sanic.exceptions.abort(422, 'Missing required attributes.')
            except TypeError as obj:
                sanic.exceptions.abort(404, f'{str(obj)[0].upper()+str(obj)[1:]} does not exist.')
            return await func(rqst, *args, **vals, **kwargs)
        return wrapper
    return decorator

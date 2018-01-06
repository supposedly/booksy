from functools import wraps

import sanic

from .typedef import Location, Role, MediaType, MediaItem, User

def uid_get(*attrs, user=False):
    def decorator(func):
        """
        To be placed directly after the sanic routing deco
        so that it can make use of the request info
        """
        @wraps(func)
        async def wrapper(rqst, *args, **kwargs):
            """
            So I don't have to keep typing out the same try-except.
            Grabs the User ID from a request and then gets whatever
            requested info out of it.
            """
            try:
                uid = getattr(rqst, 'json' if rqst.method == 'POST' else 'raw_args')['uid']
                user = await User(uid, rqst.app)
            except KeyError:
                sanic.exceptions.abort(422, 'No user ID given')
            vals = [user] if user or not attrs else []
            if attrs:
                vals += [getattr(user, i) for i in attrs]
            return await func(rqst, *vals, *args, **kwargs)
        return wrapper
    return decorator

def rqst_get(*attrs):
    def decorator(func):
        @wraps(func)
        async def wrapper(rqst, *args, **kwargs):
            """
            Another try-except abstraction.
            Grabs any requested info from a request and, if matching
            the keywords, converts it to an Object; else just gives
            the text
            """
            maps = {'item': (MediaItem, 'mid'), 'location': (Location, 'lid'), 'role': (Role, 'rid'), 'user': (User, 'uid')}
            container = getattr(rqst, 'json' if rqst.method == 'POST' else 'raw_args')
            try:
                vals = [await maps[i][0](container[maps[i][1]], rqst.app) if i in maps else container[i] for i in attrs]
            except KeyError:
                sanic.exceptions.abort(422, 'Missing requested attributes')
            return await func(rqst, *vals, *args, **kwargs)
        return wrapper
    return decorator

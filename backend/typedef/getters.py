import asyncio
import functools

from . import Location, Role, MediaItem, MediaType
from .user import User

__all__ = 'get_user', 'get_role', 'get_media_item', 'get_mtype', 'get_location'


class Cacheable:
    """
    From user "crvv" on StackOverflow.
    Allows functools.lru_caching of coroutine functions.
    """
    def __init__(self, co):
        self.co = co
        self.done = False
        self.result = None
        self.lock = asyncio.Lock()

    def __await__(self):
        with (yield from self.lock):
            if self.done:
                return self.result
            self.result = yield from self.co.__await__()
            self.done = True
            return self.result


def cacheable(f):
    """
    Decorator that makes use of above class, from the same user.
    """
    def wrapped(*args, **kwargs):
        return Cacheable(f(*args, **kwargs))
    return wrapped


def of(parent):
    """
    For emulating classmethods. Sets the child as a function attribute
    of the parent.
    """
    def wrapper(child):
        setattr(parent, child.__name__, child)
        return parent
    return wrapper


def async_lru_cache(maxsize=128, typed=False):
    def wrapper(func):
        return functools.lru_cache(maxsize, typed)(cacheable(func))
    return wrapper

# -------- #

@async_lru_cache()
async def get_location(*args, **kwargs):
    return await Location(*args, **kwargs)


@async_lru_cache()
async def get_role(*args, **kwargs):
    return await Role(*args, **kwargs)


@async_lru_cache()
async def get_mtype(*args, **kwargs):
    return await MediaType(*args, **kwargs)


@async_lru_cache()
async def get_media_item(*args, **kwargs):
    item = await MediaItem(*args, **kwargs)
    print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA', item.title, item.available)
    return item


@async_lru_cache()
async def get_user(*args, **kwargs):
    return await User(*args, **kwargs)


@async_lru_cache()
@of(get_user)
async def from_identifiers(*args, **kwargs):
    return await User.from_identifiers(*args, **kwargs)
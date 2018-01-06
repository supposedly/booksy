"""
Base classes & core funcs for the server side to inherit from.
"""
import asyncio
import contextlib
import struct
from functools import wraps
from asyncio import iscoroutinefunction as is_coro

def lockquire(lock=True, db=True, sem=False, file=False):
    """
    `lock' can be set to False when the function contains other stuff
    that doesn't require the lock (so as to release it sooner for other
    class instances to use).
    I don't think anyone would ever find a practical reason to set `db'
    to False, but it's still there just in case.
    
    db:   Acquire a connection to the sanic app's global postgres
           connection pool for DB fetching/writing
    sem:  Acquire a lock with the app's global asyncio.Semaphore(),
           used to limit concurrent requests to external APIs
           (namely Google Books here)
    file: Acquire a lock with the app's other global Semaphore(),
           this time used for limiting concurrent file reads (NOT
           WRITES; that would be handled by a lock), because i saw
           that linux doesn't handle that automatically and it can
           cause strange stuff if too many reads happen at once
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            """
            A decorator, equivalent to starting a method with
            `with await asyncio.Lock()` followed by
            `async with asyncpg.Pool().acquire()`, picking/
            choosing as specified above.
            (lockquire = 'lock and acquire')
            """
            # acquire whatever's necessary
            if lock: await self.__class__._aiolock.acquire()
            if db: conn = await self.app.pg_pool.acquire()
            if sem: await self.app.sem.acquire()
            if file: await self.app.filesem.acquire()
            try:
                # get return value here
                value = await func(conn, *args, **kwargs)
            except:
                # do nothing, let it propagate
                raise
            else:
                # return the above return value
                return value
            finally:
                # ALWAYS release acquisitions
                if file: await self.app.filesem.acquire()
                if sem: self.app.sem.release()
                if db: await self.app.pg_pool.release(conn)
                if lock: self.__class__._aiolock.release()
        return wrapper
    return decorator


class LazyProperty:
    """
    Allows definition of properties calculated once and once only.
    From user Cyclone on StackOverflow; modified slightly to look more
    coherent for my own benefit and to work with asyncio's coroutines.
    
    UNUSED as of 4 January 2018. May reintroduce in the future; dunno.
    """
    def __init__(self, method):
        self.method = method
        self.method_name = method.__name__
    
    async def __get__(self, obj, cls):
        if not obj:
            return None
        if is_coro(self.method):
            ret_value = await self.method(obj)
        else:
            ret_value = self.method(obj)
        setattr(obj, self.method_name, ret_value)
        return ret_value


class AsyncInit:
    """
    Neat trick from user khazhyk on StackOverflow.
    Allows asynchronous __init__() in inheritors.
    """
    async def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls)
        await obj.__init__(*args, **kwargs)
        return obj
    async def __init__(self):
        pass


class WithLock:
    @classmethod
    def _init_lock(cls, loop):
        cls._aiolock = asyncio.Lock(loop=loop)


class PackedByteFieldMixin:
    """
    Making this a mixin just in case I for whatever reason find a use
    for a data type that follows the same format as PermList.
    
    raw: The raw number, e.g. 45
    bin: Binary string representing `raw', e.g. '0101101'
    seq: A sequence representing `bin', e.g. (0, 1, 0, 1, 1, 0, 1)
    names: A dictionary with name:boolean pairs mapping to `seq'.
    
    Each value in `names' is also added to the instance's attributes,
    prefixed with "can_". For example, obj.names['do_thing']
    can more-easily be accessed as `obj.can_do_thing'.
    """
    def __init__(self, num):
        self.raw = num
        self.bin = format(int(self.raw), f'0{7}b') #XXX: 7 is magic number >:(
        self.seq = map(int, tuple(self.bin))
        #print(self.raw, list(self.seq))
        self.names = {name: bool(value) for name, value in zip(self._names, self.seq)}
        for k, v in self.names.items():
            # Allow, for example, obj.manage_location instead of obj.names['manage_location']
            setattr(self, f'can_{k}', v)
    
    @classmethod
    def from_kwargs(cls, **kwargs):
        # raise NotImplementedError("Don't think I actually need this because this class won't be accessed by app")
        return cls(int(''.join(str(i) for i in map(int, (kwargs.get(name, False) for name in cls._names))), 2))
    
    def edit(self, **kwargs):
        """
        Edit properties of the subclassed instance from kwargs,
        as in cls.edit(whatever=4, something=True, ...). If
        attempting to create from a dict, simply **unpack it and
        this will work as normal.
        """
        # update values, keeping current value if not given to update
        self.names = {name: kwargs.get(name, self.names[name]) for name in self._names}
        # create this sequence anew
        self.seq = map(int, tuple(self.names.values()))
        # Create 'binary' string by joining the sequence.
        # Note that the order here (dict_values->int->str)
        # is indeed necessary, but only because the values
        # are initially bools, not ints ... so the obvious
        # 'simpler' method is unfortunately invalid
        self.bin = ''.join(map(str, self.seq))
        # convert bin to decimal for a number
        self.raw = int(self.bin, 2)
    
    def edit_from_seq(self, new):
        """
        Eventually identical to .edit(), but takes an iterable sequence
        instead of kwargs.
        """
        self.seq = new
        self.bin = ''.join(self.seq)
        self.raw = int(bin, 2)
        self.names = {name: bool(value) for name, value in zip(self._names, self.seq)}


class PackedBigIntMixin:
    """
    I noticed I'd basically copy/pasted the following methods for
    each of MaxList and LockList, so this mixin provides the
    functionality to each class for half the code.
    
    raw: The raw number, e.g. 200449
    seq: A sequence representing `raw', e.g. (1, 15, 3, 0, 0, 0, 0, 0)
    names: A dictionary with name:value key pairs; values are booleans.
    
    Each value in `names' is also added to the instance's attributes.
    For example, obj.names['some_value'] can more-easily be accessed
    as `obj.some_value'.
    """
    def __init__(self, num):
        self.raw = num
        self.seq = struct.unpack('8B', struct.pack('<q', int(self.raw)))
        self.names = {name: value for name, value in zip(filter(bool, self._names), self.seq)}
        for k, v in self.names.items():
            setattr(self, k, v)
    
    @classmethod
    def from_kwargs(cls, filler=255, **kwargs):
        """
        Create an instance of the subclassed type from kwargs,
        as in cls.from_kwargs(whatever=4, something=True, ...). If
        attempting to create from a dict, simply **unpack it and
        this will work as normal.
        """
        # raise NotImplementedError("Don't think I actually need this because this class won't be accessed by app")
        return cls(struct.unpack('q', struct.pack('8B', *(kwargs.get(i, filler) for i in cls._names)))[0])
    
    def edit(self, **kwargs):
        self.names = {name: kwargs.get(name, self.names[name]) for name in filter(bool, self._names)}
        self.raw = struct.unpack('q', struct.pack('8B', *(self.names.get(i, self.seq[k]) for k, i in enumerate(self._names))))[0]
        self.seq = struct.unpack('8B', struct.pack('<q', int(self.raw)))

"""
Base classes & core funcs for the app's other files to inherit from.
"""
import contextlib
import struct
from functools import wraps

def lockquire(lock=True, db=True):
    """
    `lock' can be set to False when the function contains heavy operations
    that don't require an acquired lock (so as to release it sooner
    for other class instances to use).
    I don't think one would ever find a practical reason to set `db'
    to False, but it's available regardless for completeness.
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
            try:
                # get return value here
                value = func(conn, *args, **kwargs)
            except:
                # do nothing, let it propagate
                raise
            else:
                # return the above return value
                return value
            finally:
                # ALWAYS release necessary acquisitions
                if lock: self._aiolock.release()
                if db: await self.app.pg_pool.release(conn)
        return wrapper
    return decorator

class LazyProperty:
    """
    Allows definition of properties calculated once and once only.
    From user Cyclone on StackOverflow; modified slightly to look more
    coherent for my own benefit and to work with asyncio's coroutines.
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
    Neat trick from user khazyk on StackOverflow.
    Allows asynchronous __init__() in inheritors.
    """
    async def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls)
        await obj.__init__(*args, **kwargs)
        return obj
    async def __init__(self):
        pass

class PackedByteFieldMixin:
    """
    Making this a mixin just in case I for whatever reason find a use
    for a data type that follows the same format as PermList.
    
    raw: The raw number, e.g. 45
    bin: Binary string representing `raw', e.g. '0101101'
    seq: A sequence representing `bin', e.g. (0, 1, 0, 1, 1, 0, 1)
    names: A dictionary with name:value key pairs; values are booleans.
    ATTRS: Each value in names is also added to the instance's attrs,
           prefixed with "can_". For example, obj.names['do_thing']
           can more-easily be accessed as obj.can_do_thing.
    """
    def __init__(self, num):
        self.raw = num
        self.bin = format(int(self.raw), f'0{len(self._names)}b')
        self.seq = map(int, tuple(self.bin))
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
    ATTRS: Each value in names is also added to the instance's attrs,
           prefixed with "can_". For example, obj.names['do_thing']
           can more-easily be accessed as obj.can_do_thing.
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

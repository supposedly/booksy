class LazyProperty:
    """
    Allows creation of properties to be calculated once and once only.
    From user Cyclone on StackOverflow; modified slightly to look more
    coherent for my own benefit and to work with asyncio.
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
    Allows asynchronous __init__() in subclasses.
    """
    async def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls)
        await obj.__init__(*args, **kwargs)
        return obj
    async def __init__(self):
        pass

class Permission:
    permissions = [
      'manage location',
      'manage accounts',
      'manage roles',
      'create administrative roles',
      'manage media',
      'generate reports',
      ]
    def __init__(self, perm)

class RoleAttrMixin:
    permissions = [
      'manage location',
      'manage accounts',
      'manage roles',
      'create administrative roles',
      'manage media',
      'generate reports',
      ]
    maximums = [
      'checkout duration',
      'renewals',
      'checkouts',
      # flipped because little-endian
      # same with acct_locks
      ]
    acct_locks = [
      'checkout threshold',
      'fine threshold',
      ]
    # Total number of permissions to account for
    NUM_PERMS = 7
    
    def __binperms(self, permbin):
        if permbin is None:
            return None
        return format(int(permbin), f'0{NUM_PERMS}b')
    
    def __maxnums(self, maxbin):
        if maxbin is None:
            return None
        return tuple(struct.unpack('8b', struct.pack('<q', int(maxbin))))
    
    def __locknums(self, lockbin):
        if lockbin is None:
            return None
        return tuple(struct.unpack('8b', struct.pack('<q', int(lockbin))))
    
    def _perms(self, binperms: str) -> dict:
        if binperms is None:
            return None
        if not isinstance(binperms, str):
            binperms = self.__binperms(binperms)
        return {perm: boolean for perm, boolean in zip(permissions, binperms)}
    
    def _maxes(self, maxnums: tuple) -> dict:
        if maxnums is None:
            return None
        if not isinstance(maxnums, tuple):
            maxnums = self.__maxnums(maxnums)
        return {name: value for name, value in zip(maximums, maxnums)}
    
    def _locks(self, locknums: tuple) -> dict:
        if locknums is None:
            return None
        if not isinstance(locknums, tuple):
            locknums = self.__locknums(locknums)
        return {lock: value for lock, value in zip(acct_locks, locknums)}

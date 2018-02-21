"""
Base classes & core functions for the rest to inherit or inherit from.
"""
import abc
import asyncio
import contextlib
import struct
from abc import abstractmethod
from functools import wraps
from asyncio import iscoroutinefunction as is_coro


class LazyProperty:
    """
    Allows definition of properties calculated once and once only.
    From user Cyclone on StackOverflow; modified slightly to look more
    coherent for my own benefit and to work with asyncio's coroutines.
    
    UNUSED as of 4 January 2018. May reintroduce in the future... dunno.
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


class PackedField(metaclass=abc.ABCMeta):
    __slots__ = 'raw', 'seq', 'namemap', '_names'
    
    @classmethod
    @abstractmethod
    def from_seq(cls):
        """Allows field to be constructed from a numerical iterable."""
        raise NotImplementedError
    
    @classmethod
    @abstractmethod
    def from_kwargs(cls):
        """
        Allows field to be constructed by defining specific attrs.
        These attrs will be determined by the field's subclass,
        not the field itself.
        """
        raise NotImplementedError
    
    @property
    @abstractmethod
    def props(self):
        """Returns dict containing all slotted properties."""
        raise NotImplementedError
    
    @abstractmethod
    def edit(self):
        """Edits a certain attr or certain attrs of self."""
        raise NotImplementedError


class PackedByteFieldMixin(PackedField):
    """
    Representation of a 'packed field': a single byte, each of whose
    bits acts as an on/off flag for some elsewhere-defined value.
    For now, it's only used in Perms.
    
    raw: The raw number, e.g. 45
    bin: Binary string representing `raw', e.g. '0101101'
    seq: A sequence representing `bin', e.g. (0, 1, 0, 1, 1, 0, 1)
    names: A dictionary with name:boolean pairs mapping to `seq'.
    
    Each value in `names' is also added to the instance's attributes,
    prefixed with "can_". For example, obj.namemap['do_thing']
    can more-easily be accessed as `obj.can_do_thing'.
    """
    __slots__ = 'bin',
    
    def __init__(self, num, *, maxlen=7):
        """
        >>> Perms(65)
        <Perms-type PackedByteFieldMixin raw=65 bin='1000001' seq=(1, 0, 0, 0, 0, 0, 1)>
        """
        # Regarding 'maxlen=7':
        # It's just the length of a byte minus 1, AKA the max amount of
        # data I can store in a signed single-byte packed field.
        self.raw = num
        self.bin = format(self.raw, f'0{maxlen}b')
        self.seq = tuple(map(int, tuple(self.bin)))
        self.namemap = {name: bool(value) for name, value in zip(self._names, self.seq)}
        # Allow, for example, obj.can_manage_location instead of obj.namemap['manage_location']
        for k, v in self.namemap.items():
            setattr(self, f'can_{k}', v)
    
    def __repr__(self):
        return f'<{"-type ".join(i.__name__ for i in type(self).__mro__[:-1])} raw={self.raw!r} bin={self.bin!r} seq={self.seq!r}>'
    
    @classmethod
    def from_kwargs(cls, **kwargs):
        """
        >>> Perms.from_kwargs(manage_location=True, return_items=True)
        <Perms-type PackedByteFieldMixin raw=65 bin='1000001' seq=(1, 0, 0, 0, 0, 0, 1)>
        """
        return cls(int(''.join(str(i) for i in map(int, (kwargs.get(name, False) for name in cls._names))), 2))
    
    @classmethod
    def from_seq(cls, seq):
        """
        >>> Perms.from_seq('1000001')
        <Perms-type PackedByteFieldMixin raw=65 bin='1000001' seq=(1, 0, 0, 0, 0, 0, 1)>
        >>> Perms.from_seq([1, 0, 0, 0, 0, 0, 1])
        <Perms-type PackedByteFieldMixin raw=65 bin='1000001' seq=(1, 0, 0, 0, 0, 0, 1)>
        >>> # etc...
        """
        return cls(int(''.join(seq), 2))
    
    @property
    def props(self):
        return {'raw': self.raw, 'bin': self.bin, 'seq': self.seq, 'names': self.namemap}
    
    def edit(self, **kwargs):
        """
        Edit properties of the subclassed instance from kwargs,
        as in cls.edit(whatever=4, something=True, ...). If
        attempting to create from a dict, simply **unpack it and
        this will work as normal.
        """
        # update values, keeping current value if not given to update
        self.namemap = {name: kwargs.get(name, self.namemap[name]) for name in self._names}
        # create this sequence anew
        self.seq = tuple(map(int, self.namemap.values()))
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
        self.namemap = {name: bool(value) for name, value in zip(self._names, self.seq)}


class PackedBigIntMixin(PackedField):
    """
    This
    
    raw: The raw number, e.g. 200449
    seq: A sequence representing `raw', e.g. (1, 15, 3, 0, 0, 0, 0, 0)
    names: A dictionary with name:value key pairs; values are booleans.
    
    Each value in `names' is also added to the instance's attributes.
    For example, obj.namemap['some_value'] can more-easily be accessed
    as `obj.some_value'.
    """
    
    def __init__(self, num):
        """
        The only time this would practicably be called is when
        creating an object from the raw number stored in the DB.
        If instantiating manually, one of the classmethods would
        likely be used instead.
        
        >>> Maxes(-16119292)
        <Maxes-type PackedBigIntMixin raw=-16119292 seq=(4, 10, 10, 255
        , 255, 255, 255, 255) names={'checkout_duration': 4, 'renewals'
        : 10, 'holds': 10}>
        >>>
        >>>
        >>> Locks(-62972)
        <Locks-type PackedBigIntMixin raw=-62972 seq=(4, 10, 255, 255, 
        255, 255, 255, 255) names={'checkouts': 4, 'fines': 10}>
        """
        self.raw = num
        self.seq = struct.unpack('8B', struct.pack('<q', self.raw))
        self.namemap = {name: value for name, value in zip(filter(bool, self._names), self.seq)}
        for k, v in self.namemap.items():
            setattr(self, k, v)
    
    def __repr__(self):
        return f'<{"-type ".join(i.__name__ for i in type(self).__mro__[:-1])} raw={self.raw!r} seq={self.seq!r} names={self.namemap!r}>'
    
    @classmethod
    def from_kwargs(cls, filler=255, **kwargs):
        """
        >>> Maxes.from_kwargs(checkout_duration=4,renewals=10,holds=10)
        <Maxes-type PackedBigIntMixin raw=-16119292 seq=(4, 10, 10, 255
        , 255, 255, 255, 255) names={'checkout_duration': 4, 'renewals'
        : 10, 'holds': 10}>
        >>>
        >>>
        >>> Locks.from_kwargs(checkouts=4, fines=10)
        <Locks-type PackedBigIntMixin raw=-62972 seq=(4, 10, 255, 255, 
        255, 255, 255, 255) names={'checkouts': 4, 'fines': 10}>
        """
        return cls(*struct.unpack('q', struct.pack('8B', *(kwargs.get(i, filler) for i in cls._names))))
    
    @classmethod
    def from_seq(cls, seq, *, filler=255):
        """
        >>> Maxes.from_seq([4, 10, 10])
        <Maxes-type PackedBigIntMixin raw=-16119292 seq=(4, 10, 10, 255
        , 255, 255, 255, 255) names={'checkout_duration': 4, 'renewals'
        : 10, 'holds': 10}>
        >>>
        >>>
        >>> Locks.from_seq([4, 10])
        <Locks-type PackedBigIntMixin raw=-62972 seq=(4, 10, 255, 255, 
        255, 255, 255, 255) names={'checkouts': 4, 'fines': 10}>
        """
        fill = [filler] * (8 - len(seq))
        return cls(*struct.unpack('q', struct.pack('8B', *seq, *fill)))
    
    @property
    def props(self):
        return {'raw': self.raw, 'seq': self.seq, 'names': self.namemap}
    
    def edit(self, **kwargs):
        self.namemap = {name: kwargs.get(name, self.namemap[name]) for name in filter(bool, self._names)}
        self.raw = struct.unpack('q', struct.pack('8B', *(self.namemap.get(i, self.seq[k]) for k, i in enumerate(self._names))))[0]
        self.seq = struct.unpack('8B', struct.pack('<q', int(self.raw)))

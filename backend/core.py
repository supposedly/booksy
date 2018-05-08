"""
Base classes & core functions for the rest to inherit or inherit from.
"""
import abc
import struct
from abc import abstractmethod


class AsyncInit:
    """
    Neat trick from user khazhyk on StackOverflow.
    Allows asynchronous __init__() in inheritors.
    
    (Vital to everything!)
    """
    async def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls)
        await obj.__init__(*args, **kwargs)
        return obj
    
    async def __init__(self):
        pass


class PackedField(metaclass=abc.ABCMeta):
    """
    There are certain items in the database that I store as "packed
    fields", i.e. arrays condensed into a single integer for ease of
    storage.
    There are moreover two types of packed fields I use: those that
    store their info in a bigint, where each said item comprises
    a single byte (a number going up to 255),
    
    -- and those that store their info in a single byte, where each
    item comprises a single on/off (1/0) 'flag' bit.
    
    These two share enough in common, of course, that I figured it'd
    be handy to define an abstract base class for them.
    """
    __slots__ = 'raw', 'seq', 'namemap', '_names',
    _names: list
    namemap: dict
    seq: list
    raw: int
    
    @classmethod
    @abstractmethod
    def from_seq(cls):
        """Allows field to be constructed from a numeric iterable."""
        raise NotImplementedError
    
    @classmethod
    @abstractmethod
    def from_kwargs(cls):
        """
        Allows field to be constructed by defining specific attrs.
        These attrs will be defined by the field's inheritors,
        via the _names property, not by the field class itself.
        """
        raise NotImplementedError
    
    @property
    @abstractmethod
    def props(self):
        """Returns a dict containing all slotted properties."""
        raise NotImplementedError
    
    @abstractmethod
    def edit(self):
        """Edits a certain attr or certain attrs of self via kwargs."""
        raise NotImplementedError


class PackedByteField(PackedField):
    """
    Representation of a 'packed field': a single byte, each of whose
    bits acts as an on/off flag for some elsewhere-defined value.
    For now, it's only used in Perms.
    
    raw: The raw number, e.g. 45
    bin: Binary string representing `raw', e.g. '0101101'.
    seq: A sequence representing `bin', e.g. (0, 1, 0, 1, 1, 0, 1)
    props: A dictionary with name: boolean pairs mapping to `seq'.
    
    Each value in `props' is also added to the instance's attributes,
    prefixed with "can_". For example, obj.props['do_thing']
    can more-easily be accessed as `obj.can_do_thing'.
    """
    __slots__ = 'bin',
    
    def __init__(self, num, *, maxlen=7):
        """
        >>> Perms(65)
        <Perms-type PackedByteField-type PackedField raw=65 bin='1000001' seq=(1, 0, 0, 0, 0, 0, 1)>
        """
        # Regarding 'maxlen=7':
        # It's just the length of a byte minus 1, AKA the max amount of
        # data I can store in a signed single-byte packed field.
        self.raw = num
        self.bin = format(self.raw, f'0{maxlen}b')
        self.seq = tuple(map(int, tuple(self.bin)))
        self.namemap = {name: bool(value) for name, value in zip(self._names, self.seq)}
        for k, v in self.namemap.items():
            # This allows, for example, `obj.can_manage_location` instead of `obj.namemap['manage_location']`
            setattr(self, f'can_{k}', v)
    
    def __repr__(self):
        """
        The genexp at the beginning is to generate a string resembling:
        <Perms-type PackedByteField-type PackedField ... >
        """
        return f'<{"-type ".join(i.__name__ for i in type(self).__mro__[:-1])}, raw={self.raw!r}, bin={self.bin}, seq={self.seq!r}>'
    
    @classmethod
    def from_kwargs(cls, **kwargs):
        """
        >>> Perms.from_kwargs(manage_location=True, return_items=True)
        <Perms-type PackedByteField-type PackedField raw=65 bin='1000001' seq=(1, 0, 0, 0, 0, 0, 1)>
        """
        return cls(int(''.join(str(i) for i in map(int, (kwargs.get(name, False) for name in cls._names))), 2))
    
    @classmethod
    def from_seq(cls, seq):
        """
        >>> Perms.from_seq('1000001')
        <Perms-type PackedByteField-type PackedField, raw=65, bin=1000001, seq=(1, 0, 0, 0, 0, 0, 1)>
        >>> Perms.from_seq([1, 0, 0, 0, 0, 0, 1])
        <Perms-type PackedByteField-type PackedField, raw=65, bin=1000001, seq=(1, 0, 0, 0, 0, 0, 1)>
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
        # 'simpler' method of joining from the name map is
        # unfortunately invalid
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


class PackedBigInt(PackedField):
    """
    # SPECIAL VALUES:
    #   255: Infinity
    #   254: NULL (Look one level up to a less-specific max)
    #   253: Default filler
    #   251-252: Undefined but reserved
    #   0-250: Regular values (inputs cannot exceed 250)
    
    raw: The raw number, e.g. 200449
    seq: A sequence representing `raw', e.g. (1, 15, 3, 253, 253, 253, 253, 253)
    props: A dictionary with name:value key pairs; values are booleans.
    
    Each value in `props' is also added to the instance's attributes.
    For example, obj.props['some_value'] can more-easily be accessed
    as `obj.some_value'.
    """
    
    def __init__(self, num):
        """
        The only time this would practicably be called is when
        creating an object from the raw number stored in the DB.
        If instantiating manually, one of the classmethods would
        likely be used instead.
        
        >>> Limits(-144680345691944444)
        <Limits-type PackedBigInt-type PackedField raw=-14468034569
        2141052 seq=(4, 10, 10, 253, 253, 253, 253, 253) namemap={'chec
        kout_duration': 4, 'renewals': 10, 'holds': 10}>
        >>>
        >>>
        >>> Locks(-144680345676215804)
        <Locks-type PackedBigInt-type PackedField raw=-14468034567
        6215804 seq=(4, 10, 253, 253, 253, 253, 253, 253) namemap={'che
        ckouts': 4, 'fines': 10}>
        
        This also doesn't autofill empty fields, because a number won't
        have any 'empty' spots in it.
        """
        self.raw = num
        self.seq = struct.unpack('8B', struct.pack('<q', self.raw))
        self.namemap = {name: value for name, value in zip(filter(bool, self._names), self.seq)}
        for k, v in self.namemap.items():
            setattr(self, k, v)
    
    def __repr__(self):
        """
        The genexp at the beginning is to generate a string resembling:
        <Limits-type PackedBigInt-type PackedField ... >
        """
        return f'<{"-type ".join(i.__name__ for i in type(self).__mro__[:-1])}, raw={self.raw!r}, seq={self.seq!r}, namemap={self.namemap!r}>'
    
    @classmethod
    def from_kwargs(cls, filler=253, **kwargs):
        """
        >>> Limits.from_kwargs(checkout_duration=4, renewals=10, holds=10)
        <Limits-type PackedBigInt-type PackedField raw=-14468034569
        2141052 seq=(4, 10, 10, 253, 253, 253, 253, 253) namemap={'chec
        kout_duration': 4, 'renewals': 10, 'holds': 10}>
        >>>
        >>>
        >>> Locks.from_kwargs(checkouts=4, fines=10)
        <Locks-type PackedBigInt-type PackedField raw=-14468034567
        6215804 seq=(4, 10, 253, 253, 253, 253, 253, 253) namemap={'che
        ckouts': 4, 'fines': 10}>
        """
        return cls(*struct.unpack('q', struct.pack('8B', *(kwargs.get(i, filler) for i in cls._names))))
    
    @classmethod
    def from_seq(cls, seq, *, filler=253):
        """
        >>> Limits.from_seq([4, 10, 10])
        <Limits-type PackedBigInt-type PackedField raw=-14468034569
        2141052 seq=(4, 10, 10, 253, 253, 253, 253, 253) namemap={'chec
        kout_duration': 4, 'renewals': 10, 'holds': 10}>
        >>>
        >>>
        >>> Locks.from_seq([4, 10])
        <Locks-type PackedBigInt-type PackedField raw=-14468034567
        6215804 seq=(4, 10, 253, 253, 253, 253, 253, 253) namemap={'che
        ckouts': 4, 'fines': 10}>
        """
        fill = [filler] * (8 - len(seq))  # expand sequence to 8 bytes
        return cls(*struct.unpack('q', struct.pack('8B', *seq, *fill)))
    
    @property
    def props(self):
        return {'raw': self.raw, 'seq': self.seq, 'names': self.namemap}
    
    def edit(self, **kwargs):
        self.namemap = {name: kwargs.get(name, self.namemap[name]) for name in filter(bool, self._names)}
        [self.raw] = struct.unpack('q', struct.pack('8B', *(self.namemap.get(i, self.seq[k]) for k, i in enumerate(self._names))))
        self.seq = struct.unpack('8B', struct.pack('<q', int(self.raw)))

"""
Just the three types: Perms, Maxes, Locks.
I may actually be able to remove this entirely and just implement the
distinct types as some sort of dictionary with the mixins...
"""
from .core import PackedByteFieldMixin, PackedBigIntMixin

class Perms(PackedByteFieldMixin):
    _names = [
      'manage_location',
      'manage_accounts',
      'manage_roles',
      'create_admin_roles',
      'manage_media',
      'generate_reports',
      'return_items',
      ]
    
    def __init__(self, permnum):
        super().__init__(permnum)


class Maxes(PackedBigIntMixin):
    _names = [
      'checkout_duration',
      'renewals',
      'holds',
      False,
      False,
      False,
      False,
      None
      ]
    
    def __init__(self, maxnum):
        super().__init__(maxnum)


class Locks(PackedBigIntMixin):
    _names = [
      'checkouts', # checkout threshold
      'fines', # fine threshold
      False,
      False,
      False,
      False,
      False,
      None
      ]
    
    def __init__(self, locknum):
        super().__init__(locknum)

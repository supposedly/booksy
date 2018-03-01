"""
These are just data classes, essentially, but they're the only 'outlet'
between the rest of the backend and their core.py base classes.

(that is, nowhere else will you see the term 'PackedByteFieldMixin';
just 'Perms')
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


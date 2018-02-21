"""Essentially just data classes. They store their 'names' attributes."""

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


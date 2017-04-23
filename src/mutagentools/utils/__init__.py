#!/usr/bin/env python
# -*- coding: utf-8 -*-

import six


def contains_any(lst, *items):
    """Returns true if the list contains any of the given items."""
    for item in items:
        if item in lst:
            return True

    return False


def first(lst):
    """Return the first value in a list or None."""
    return lst[0] if len(lst) > 0 else None


def first_of_list(lst):
    """Returns the first entry in a list, or if this is not a list, the value itself."""
    return first(lst) if isinstance(lst, (list, tuple)) else lst


def fold_text_keys(dct):
    """Collapses dictionary key entries which are lists of single strings."""
    for key, value in dct.items():
        if isinstance(value, (list, set)) and len(value) == 1 and ( \
                isinstance(value[0], six.string_types) or isinstance(value[0], int)):
            dct[key] = value[0]


def pop_keys(dct, *key_names):
    """Pops and returns all found keys in the dictionary."""
    return list(
        filter(lambda i: i,
            map(lambda i: dct.pop(i) if i in dct.keys() else None, key_names)
        )
    )

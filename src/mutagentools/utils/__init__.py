#!/usr/bin/env python
# -*- coding: utf-8 -*-

import six


def fold_text_keys(dct):
    """Collapses dictionary key entries which are lists of single strings."""
    for key, value in dct.items():
        if isinstance(value, (list, set)) and len(value) == 1 and ( \
                isinstance(value[0], six.string_types) or isinstance(value[0], int)):
            dct[key] = value[0]

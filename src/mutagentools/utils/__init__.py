#!/usr/bin/env python
# -*- coding: utf-8 -*-

def fold_text_keys(dct):
    """Collapses dictionary key entries which are lists of single strings."""
    for key, value in dct.items():
        if isinstance(value, (list, set)) and len(value) == 1 and isinstance(value[0], (str, int)):
            dct[key] = value[0]

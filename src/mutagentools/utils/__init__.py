#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def fold_text_keys(dct):
    """Collapses dictionary key entries which are lists of single strings."""
    for key, value in dct.items():
        if isinstance(value, (list, set)) and len(value) == 1 and isinstance(value[0], str):
            dct[key] = value[0]

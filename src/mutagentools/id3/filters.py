#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from mutagen.id3 import APIC


def non_picture_tags(id3):
    """Returns a dictionary of non-picture tags in key-value format."""
    return { i[0]: i[1] for i in id3.items() if not isinstance(i[1], APIC) }

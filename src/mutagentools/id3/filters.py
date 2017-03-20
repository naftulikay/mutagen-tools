#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from mutagen.id3 import APIC

import re

GOOGLE_PLAY_METADATA = re.compile(r'^PRIV:Google', re.I)


def private_google_tags(id3):
    """Returns a dictionary of private Google Play Music tags from a given file."""
    return { i[0]: i[1] for i in id3.items() if GOOGLE_PLAY_METADATA.search(i[0]) }


def non_picture_tags(id3):
    """Returns a dictionary of non-picture tags in key-value format."""
    return { i[0]: i[1] for i in id3.items() if not isinstance(i[1], APIC) }

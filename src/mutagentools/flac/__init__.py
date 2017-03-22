#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from base64 import b64encode

from mutagen.id3 import PictureType

from mutagentools.flac.convert import convert_flac_to_id3
from mutagentools.utils import fold_text_keys


def to_json_dict(flac, include_pics=False, flatten=False):
    """Outputs FLAC tags in a JSON-compatible format."""
    result = {}

    # flac is so damn easy
    for key, value in (flac.tags or {}).items():
        result[key.lower()] = value

    # include pictures if need be
    if include_pics and len(flac.pictures) > 0:
        result['pictures'] = []
        for picture in flac.pictures:
            result['pictures'].append({
                'data': b64encode(picture.data).decode('utf-8'),
                'desc': picture.desc,
                'mime': picture.mime,
                'type': picture.type,
                'type_friendly': str(PictureType.from_bytes(bytes([picture.type]), 'little')).split('.')[-1]
            })

    # flatten if need be
    if flatten:
        fold_text_keys(result)

    return result

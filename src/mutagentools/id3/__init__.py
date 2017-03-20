#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from base64 import b64encode

from itertools import accumulate

from mutagen.id3 import (
    NumericTextFrame, TextFrame, UrlFrame, BinaryFrame, APIC,
)

from mutagen.id3._specs import (
    BinaryDataSpec, ByteSpec, EncodedTextSpec, IntegerSpec, Latin1TextSpec, SizedIntegerSpec, StringSpec
)

import mutagentools.id3.filters

from mutagentools.id3.filters import (
    private_google_tags, non_picture_tags,
)


def to_json_dict(id3, include_pics=False, flatten=False):
    """Outputs ID3 tags in a JSON-compatible format."""
    result = {}

    for key in id3.keys() if include_pics else non_picture_tags(id3).keys():
        # account for these types:
        #  - NumericTextFrame (can be represented by number)
        #  - TextFrame - str
        #  - UrlFrame - dict
        #  - BinaryFrame - dict(data=base64)
        #  - APIC - dict(data=base64)
        #  - Frame - dict()
        frames = id3.getall(key)
        first_frame = frames[0]
        frame_name = first_frame.FrameID
        values = result.get(frame_name, [])

        if isinstance(first_frame, NumericTextFrame):
            # integer-representable text frame
            values += [int(text) for frame in id3.getall(key) for text in frame.text]
        elif isinstance(first_frame, TextFrame):
            # generic text string
            values += [str(text) for frame in id3.getall(key) for text in frame.text]
        elif isinstance(first_frame, UrlFrame):
            # url
            values += [url for frame in id3.getall(key) for url in \
                ([frame.url] if isinstance(frame.url, (bytes, str)) else frame.url)]
        elif isinstance(first_frame, BinaryFrame):
            # raw, binary data, encode to base64
            values = b64encode(first_frame.data)
        elif isinstance(first_frame, APIC):
            # structured picture tag, encode data to base64
            values += [{
                'data': b64encode(first_frame.data).decode('utf-8'),
                'desc': first_frame.desc,
                'mime': first_frame.mime,
                'type': int(first_frame.type),
                'type_friendly': str(first_frame.type).split('.')[-1],
            }]
        else:
            # it's a generic structured frame, break it down
            for frame in frames:
                struct = {}

                for fspec in frame._framespec:
                    if isinstance(fspec, BinaryDataSpec):
                        struct[fspec.name] = b64encode(getattr(frame,fspec.name))
                    elif isinstance(fspec, (EncodedTextSpec, Latin1TextSpec, StringSpec)):
                        struct[fspec.name] = getattr(frame,fspec.name)
                    elif isinstance(fspec, (ByteSpec, IntegerSpec, SizedIntegerSpec)):
                        struct[fspec.name] = int(getattr(frame, fspec.name))
                    else:
                        pass

                values.append(struct)

        result[frame_name] = values

    # if we're supposed to flatten, do it now
    if flatten:
        for key, value in result.items():
            if isinstance(value, (list, set)) and len(value) == 1:
                result[key] = value[0]

    return result


def strip_private_tags(id3, save=True):
    """Removes all private identifying tags from a given ID3 instance."""
    private_tags = list(private_google_tags(id3).keys())

    for k in private_tags:
        # remove the tag
        id3.pop(k)

    if save:
        id3.save()

    return private_tags

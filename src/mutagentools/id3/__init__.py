#!/usr/bin/env python
# -*- coding: utf-8 -*-

from base64 import b64encode

from mutagen.id3 import (
    NumericTextFrame, TextFrame, UrlFrame, BinaryFrame, APIC, TXXX, UFID
)

from mutagen.id3._specs import (
    BinaryDataSpec, ByteSpec, EncodedTextSpec, IntegerSpec, Latin1TextSpec, SizedIntegerSpec, StringSpec
)

import mutagentools.id3.filters

from mutagentools.id3.filters import (
    private_google_tags, non_picture_tags,
)

from mutagentools.utils import fold_text_keys


def to_json_dict(id3, include_pics=False, flatten=False):
    """Outputs ID3 tags in a JSON-compatible format."""
    result = {}

    frame_names = set(map(lambda f: f.FrameID, id3.values()))

    if not include_pics:
        # filter pictures if asked
        frame_names = set(filter(lambda f: f != 'APIC', frame_names))

    for frame_name in frame_names:
        frames = list(filter(lambda f: f.FrameID == frame_name, id3.values()))
        values = result.get(frame_name, [])

        if isinstance(frames[0], TXXX):
            values = values if isinstance(values, dict) else {}
            values.update({ f.desc: f.text for f in frames })
        elif isinstance(frames[0], UFID):
            values = values if isinstance(values, dict) else {}
            values.update({ f.owner: f.data.decode('utf-8') for f in frames })
        elif isinstance(frames[0], NumericTextFrame):
            # integer-representable text frame
            values += [int(text) for frame in frames for text in frame.text]
        elif isinstance(frames[0], TextFrame):
            # generic text string
            values += [str(text) for frame in frames for text in frame.text]
        elif isinstance(frames[0], UrlFrame):
            # url
            values += [url for frame in frames for url in \
                ([frame.url] if isinstance(frame.url, (bytes, str)) else frame.url)]
        elif isinstance(frames[0], BinaryFrame):
            # raw, binary data, encode to base64
            values += [b64encode(frame.data).decode('utf-8') for frame in frames]
        elif isinstance(frames[0], APIC):
            # structured picture tag, encode data to base64
            values += [{
                'data': b64encode(frame.data).decode('utf-8'),
                'desc': frame.desc,
                'mime': frame.mime,
                'type': int(frame.type),
                'type_friendly': str(frame.type).split('.')[-1],
            } for frame in frames]
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
        fold_text_keys(result)
        fold_text_keys(result.get('TXXX')) if 'TXXX' in result.keys() else None

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

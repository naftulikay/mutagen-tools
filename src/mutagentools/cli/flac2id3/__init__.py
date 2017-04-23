#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import sys

from mutagen.flac import FLAC
from mutagen.mp3 import MP3

from mutagentools.flac import convert_flac_to_id3


def main(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description="Copies FLAC Vorbis tags to an ID3 compliant file.")
    parser.add_argument('-d', '--delete', action='store_true',
        help="Delete all tags in the destination ID3 file before copying tags over.")
    parser.add_argument('flac_file', type=argparse.FileType('r'), help="FLAC file to copy tags from.")
    parser.add_argument('id3_file', type=argparse.FileType('r'), help="ID3 compliant file to copy tags to.")
    args = parser.parse_args(args)

    # open FLAC file
    src = FLAC(args.flac_file.name)

    # open MP3/ID3 file
    dest = MP3(args.id3_file.name)

    if not dest.tags:
        dest.add_tags()

    # if we are meant to clear the dest tags, clear them
    dest.tags.clear() if args.delete else None

    # now, copy over the tags
    list(map(lambda t: dest.tags.add(t), convert_flac_to_id3(src)))

    # save; writing ID3v1 tags and ID3v2.4 tags
    dest.tags.save(args.id3_file.name, 2, 4)


if __name__ == "__main__":
    main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse

from mutagen.flac import FLAC
from mutagen.id3 import ID3
from mutagen.mp3 import MP3

from mutagentools.flac import convert_flac_to_id3


def main():
    parser = argparse.ArgumentParser(description="Copies FLAC Vorbis tags to an ID3 compliant file.")
    parser.add_argument('-d', '--delete', action='store_true',
        help="Delete all tags in the destination ID3 file before copying tags over.")
    parser.add_argument('flac_file', type=argparse.FileType('r'), help="FLAC file to copy tags from.")
    parser.add_argument('id3_file', type=argparse.FileType('r'), help="ID3 compliant file to copy tags to.")
    args = parser.parse_args()

    # open FLAC file
    src = FLAC(args.flac_file.name)

    # open MP3/ID3 file
    dest = ID3(args.id3_file.name)

    # if we are meant to clear the dest tags, clear them
    dest.clear() if args.delete else None

    # now, copy over the tags
    list(map(lambda t: dest.add(t), convert_flac_to_id3(src)))

    # save; writing ID3v1 tags and ID3v2.4 tags
    dest.save(args.id3_file.name, 2, 4)


if __name__ == "__main__":
    main()

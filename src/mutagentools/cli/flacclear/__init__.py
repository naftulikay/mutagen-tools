#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse

from mutagen.flac import FLAC


def main():
    parser = argparse.ArgumentParser(description="Clear all tags from a FLAC file.")
    parser.add_argument('-v', '--verbose', action='store_true', help="Verbose output.")
    parser.add_argument('flac_file', type=argparse.FileType('r'), nargs='+',
        help="FLAC file(s) to remove tags from.")
    args = parser.parse_args()

    for flac_file in args.flac_file:
        if args.verbose:
            print("Removing FLAC tags and pictures from {}...".format(flac_file.name))

        f = FLAC(flac_file.name)
        f.clear()
        f.clear_pictures()
        f.save()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse

from mutagen.id3 import ID3


def main():
    parser = argparse.ArgumentParser(description="Clear all ID3 tags from a file.")
    parser.add_argument('-v', '--verbose', action='store_true', help="Verbose output.")
    parser.add_argument('id3_file', type=argparse.FileType('r'), nargs='+',
        help="ID3 containing file(s) to remove tags from.")
    args = parser.parse_args()

    for id3_file in args.id3_file:
        if args.verbose:
            print("Removing ID3 tags from {}...".format(id3_file.name))

        f = ID3(id3_file.name)
        f.clear()
        f.save()


if __name__ == "__main__":
    main()

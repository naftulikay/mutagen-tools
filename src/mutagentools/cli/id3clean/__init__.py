#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mutagen.mp3 import MP3

from mutagentools.id3 import strip_private_tags

import argparse


def main():
    parser = argparse.ArgumentParser(description="Removes private identifying tags from MP3 files.")
    parser.add_argument('-v', '--verbose', help="Verbose output.", action="store_true")
    parser.add_argument('id3_file', help="MP3 file(s) to strip tracker tags from.", type=argparse.FileType('r'),
        nargs="+")
    args = parser.parse_args()

    for id3_file in args.id3_file:
        if args.verbose:
            print("Stripping private identifying tags from {}...".format(id3_file.name))

        private_tags = strip_private_tags(MP3(id3_file.name))

        if args.verbose and len(private_tags) > 0:
            for tag in private_tags:
                print("  Removing Tag {}...".format(tag))


if __name__ == "__main__":
    main()

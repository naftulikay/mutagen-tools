#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json

from mutagen.mp3 import MP3
from mutagentools.id3 import to_json_dict


def main():
    parser = argparse.ArgumentParser(description="Renders a file's ID3 tags in JSON format.")
    parser.add_argument('-n', '--no-flatten', action='store_true', help="Don't flatten single-entry arrays.")
    parser.add_argument('-p', '--pictures', action="store_true", help="Include base64-encoded pictures in output.")
    parser.add_argument('id3_file', type=argparse.FileType('r'), nargs='+',
        help="File(s) to extract information from.")
    args = parser.parse_args()

    result = []

    for id3_file in args.id3_file:
        result.append({
            'file': id3_file.name,
            'tags': to_json_dict(MP3(id3_file.name).tags or {}, include_pics=args.pictures, flatten=not args.no_flatten)
        })

    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()

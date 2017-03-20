#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from mutagentools.flac import to_json_dict

from mutagen.flac import FLAC

import argparse
import json


def main():
    parser = argparse.ArgumentParser(description="Renders a file's FLAC tags in JSON format.")
    parser.add_argument('-n', '--no-flatten', action='store_true', help="Don't flatten single-entry arrays.")
    parser.add_argument('-p', '--pictures', action="store_true", help="Include base64-encoded pictures in output.")
    parser.add_argument('flac_file', type=argparse.FileType('r'), nargs='+',
        help="File(s) to extract information from.")
    args = parser.parse_args()

    result = []

    for flac_file in args.flac_file:
        result.append({
            'file': flac_file.name,
            'tags': to_json_dict(FLAC(flac_file.name), include_pics=args.pictures, flatten=not args.no_flatten)
        })

    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()

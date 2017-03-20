#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from base64 import b64encode

from mutagen.flac import FLAC

from mutagentools.flac import to_json_dict

import os

import unittest

from unittest import mock
from unittest.mock import patch


class MainTestCase(unittest.TestCase):

    def test_to_json_dict(self):
        """Tests formatting FLAC metadata as a JSON-compatible dict."""
        fixture = FLAC(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'fixtures/fixture.flac'))

        result = to_json_dict(fixture)

        # test that the album was imported
        self.assertIn('album', result.keys())
        self.assertEqual(1, len(result.get('album')))
        self.assertIn('Album', result.get('album'))

        # test that both artists were imported
        self.assertIn('artist', result.keys())
        self.assertEqual(2, len(result.get('artist')))
        self.assertIn('Artist 1', result.get('artist'))
        self.assertIn('Artist 2', result.get('artist'))

        # test that pictures aren't included by default
        self.assertNotIn('pictures', result.keys())

    def test_to_json_dict_pictures(self):
        """Tests formatting FLAC metadata as a JSON-compatible dict with pictures."""
        fixture = FLAC(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'fixtures/fixture.flac'))

        result = to_json_dict(fixture, include_pics=True)

        self.assertIn('pictures', result.keys())
        self.assertEqual(1, len(result.get('pictures')))

        op = fixture.pictures[0]
        p = result.get('pictures')[0]

        # test the attributes
        self.assertEqual(b64encode(op.data).decode('utf-8'), p.get('data'))
        self.assertEqual(op.desc, p.get('desc'))
        self.assertEqual(op.mime, p.get('mime'))
        self.assertEqual(op.type, p.get('type'))
        self.assertEqual('COVER_FRONT', p.get('type_friendly'))

    def test_to_json_dict_flatten(self):
        """Tests formatting FLAC metadata as a JSON-compatible flat dictionary."""
        fixture = FLAC(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'fixtures/fixture.flac'))

        result = to_json_dict(fixture, flatten=True)

        # test that the album was flattened
        self.assertIn('album', result.keys())
        self.assertEqual('Album',result.get('album'))

        # test that both artists were imported
        self.assertIn('artist', result.keys())
        self.assertEqual(2, len(result.get('artist')))
        self.assertIn('Artist 1', result.get('artist'))
        self.assertIn('Artist 2', result.get('artist'))

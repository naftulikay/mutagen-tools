#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mock
import mutagentools
import os
import unittest

from mock import patch
from mutagen.id3 import ID3
from mutagen.mp3 import MP3
from mutagentools.cli.flac2id3 import main as flac2id3_main

FILENAME = os.path.realpath(__file__)
DIRNAME = os.path.dirname(FILENAME)


class IntegrationTest(unittest.TestCase):

    @patch('mutagentools.cli.flac2id3.MP3', autospec=True)
    def test_no_id3(self, mock_MP3):
        """Tests that copying a blank FLAC to an MP3 without an ID3 header doesn't crash."""
        blank_id3 = os.path.join(DIRNAME, *('../../id3/fixtures/no-id3.mp3'.split('/')))
        blank_flac= os.path.join(DIRNAME, *('../../flac/fixtures/blank.flac'.split('/')))

        instance = mock.MagicMock()
        mock_MP3.return_value = instance

        result = []

        tags = mock.MagicMock(spec=ID3)
        instance.tags = tags
        instance.tags.add.side_effect = lambda a: result.append(a)

        self.assertTrue(os.path.isfile(blank_id3))
        self.assertTrue(os.path.isfile(blank_flac))

        # run it
        flac2id3_main([blank_flac, blank_id3])

        # make sure that a save was attempted
        tags.save.assert_called_with(blank_id3, 2, 4)

        # it should insert TPOS by default, so yeah:
        self.assertEqual(1, len(result))

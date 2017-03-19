#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from mutagen.id3 import (
    APIC, ID3, Encoding, PictureType, TIT2,
)

from mutagentools.id3.filters import non_picture_tags

import unittest


class FilterTestCase(unittest.TestCase):

    def test_non_picture_tags(self):
        """Tests that the non_picture_tags filter function returns only non-picture tags."""
        with open('/dev/zero', 'rb') as r:
            picture_binary = r.read(1024)

        fixture = ID3()
        # add multiple images
        fixture.add(APIC(encoding=Encoding.UTF8, mime="image/jpeg", type=PictureType.COVER_FRONT, desc="Cover",
            data=picture_binary))
        fixture.add(APIC(encoding=Encoding.UTF8, mime="image/jpeg", type=PictureType.COVER_BACK, desc="Back Cover",
            data=picture_binary))
        # add a track title
        fixture.add(TIT2(encoding=Encoding.UTF8, text="A Song"))

        # the only thing it should contain is the TIT2 tag
        self.assertEqual(['TIT2'], list(non_picture_tags(fixture).keys()))

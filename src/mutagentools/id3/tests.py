#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from mutagen.id3 import (
    APIC, ID3, Encoding, PictureType, PRIV, TIT2,
)

from mutagentools.id3 import (
    strip_private_tags,
)

from mutagentools.id3.filters import (
    private_google_tags,
    non_picture_tags,
)

from unittest import mock
from unittest.mock import patch

import unittest


class MainTestCase(unittest.TestCase):

    @patch.object(ID3, 'save', new_callable=mock.MagicMock, return_value=None)
    def test_strip_private_tags(self, mock_save):
        """Tests that stripping of private tags works as expected."""
        self.assertTrue(isinstance(mock_save, mock.MagicMock))

        fixture = ID3()
        # add a title
        fixture.add(TIT2(encoding=Encoding.UTF8, text="A Song"))
        # add a banned google private tag
        fixture.add(PRIV(encoding=Encoding.UTF8, owner="Google/StoreId", data=b'rT9HEn6sL6tN7yhk6oDQfpi1ip6'))

        # should return list of stripped tags
        self.assertEqual(['PRIV:Google/StoreId:rT9HEn6sL6tN7yhk6oDQfpi1ip6'], strip_private_tags(fixture))
        # should not contain that tag anymore
        self.assertNotIn('PRIV:Google/StoreId:rT9HEn6sL6tN7yhk6oDQfpi1ip6', fixture)
        # should by default call save
        mock_save.assert_called_with()

        # reset the mock and try again without save
        mock_save.reset_mock()
        fixture.add(PRIV(encoding=Encoding.UTF8, owner="Google/StoreId", data=b'rT9HEn6sL6tN7yhk6oDQfpi1ip6'))
        strip_private_tags(fixture, save=False)

        # with save=False, should not have saved
        self.assertFalse(mock_save.called)


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

    def test_private_google_tags(self):
        """Tests that the filter returns only private Google metadata tags."""
        fixture = ID3()
        # add a track title
        fixture.add(TIT2(encoding=Encoding.UTF8, text="A Song"))
        # add other random priv tag
        fixture.add(PRIV(encoding=Encoding.UTF8, owner="Naftuli/Word", data=b'YASS'))
        # add private google tags
        fixture.add(PRIV(encoding=Encoding.UTF8, owner="Google/StoreId", data=b'rT9HEn6sL6tN7yhk6oDQfpi1ip6'))
        fixture.add(PRIV(encoding=Encoding.UTF8, owner="Google/StoreLabelCode", data=b'HOD3zSlIr8rjcwXXiS'))

        # the only thing it should contain is the private google tags
        keys = private_google_tags(fixture).keys()

        self.assertEqual(2, len(keys))
        self.assertIn('PRIV:Google/StoreId:rT9HEn6sL6tN7yhk6oDQfpi1ip6', keys)
        self.assertIn('PRIV:Google/StoreLabelCode:HOD3zSlIr8rjcwXXiS', keys)

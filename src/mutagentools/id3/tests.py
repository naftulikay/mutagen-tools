#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from base64 import b64encode

from mutagen.id3 import (
    APIC, ID3, Encoding, PictureType, PRIV, TIT2, TPE2, WCOM, WCOP, TBPM, TYER, MCDI
)

from mutagentools.id3 import (
    strip_private_tags,
    to_json_dict,
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

    def test_to_json_dict(self):
        """Tests that conversion to a JSON-compatible map works as expected."""
        picture_binary = bytes([0x00] * 32)

        fixture = ID3()
        # test that single numeric text entries get represented
        fixture.add(TBPM(encoding=Encoding.UTF8, text="140"))
        # test that multiple numeric text entries get represented
        fixture.add(TYER(encoding=Encoding.UTF8, text=["2012", "2016"]))
        # test that url entries get represented
        fixture.add(WCOP(url="https://naftuli.com"))
        # test multi-url entries
        fixture.add(WCOM(url="https://naftuli.com"))
        fixture.add(WCOM(url="https://naftuli.wtf"))
        # test that single entries get represented
        fixture.add(TPE2(encoding=Encoding.UTF8, text="Album Artist"))
        # test that multiple entries get represented
        fixture.add(TIT2(encoding=Encoding.UTF8, text=["Title 1", "Title 2"]))
        # test that binary data will or will not be represented
        fixture.add(MCDI(data=bytes([0x00] * 8)))
        # test that pictures will or will not be represented
        fixture.add(APIC(encoding=Encoding.UTF8, mime="image/jpeg", type=PictureType.COVER_FRONT, desc="Cover",
            data=picture_binary))
        fixture.add(APIC(encoding=Encoding.UTF8, mime="image/jpeg", type=PictureType.COVER_BACK, desc="Back Cover",
            data=picture_binary))
        # test that structured frames will be properly represented
        fixture.add(PRIV(owner="Naftuli", data=b"something"))
        fixture.add(PRIV(owner="The Dude", data=b"amazing"))

        # get the value
        result = to_json_dict(fixture)

        # test single numeric text value
        self.assertIn('TBPM', result.keys())
        self.assertEquals(1, len(result.get('TBPM')))
        self.assertIn(140, result.get('TBPM'))

        # test multiple numeric text value
        self.assertIn('TYER', result.keys())
        self.assertEquals(2, len(result.get('TYER')))
        self.assertIn(2012, result.get('TYER'))
        self.assertIn(2016, result.get('TYER'))

        # test single url entries
        self.assertIn('WCOP', result.keys())
        self.assertEqual(1, len(result.get('WCOP')))
        self.assertIn('https://naftuli.com', result.get('WCOP'))

        # test multiple url entries
        self.assertIn('WCOM', result.keys())
        self.assertEqual(2, len(result.get('WCOM')))
        self.assertIn('https://naftuli.com', result.get('WCOM'))
        self.assertIn('https://naftuli.wtf', result.get('WCOM'))

        # test single text entries
        self.assertIn('TPE2', result.keys())
        self.assertEqual(1, len(result.get('TPE2')))
        self.assertIn("Album Artist", result.get('TPE2'))

        # test multiple text entries
        self.assertIn('TIT2', result.keys())
        self.assertEqual(2, len(result.get('TIT2')))
        self.assertIn("Title 1", result.get('TIT2'))
        self.assertIn("Title 2", result.get('TIT2'))

        # test binary data
        self.assertIn('MCDI', result.keys())
        self.assertEqual(b64encode(bytes([0x00] * 8)), result.get('MCDI'))

        # test that pictures aren't included by default
        self.assertNotIn('APIC', result.keys())

        # test non-standard frames
        self.assertIn('PRIV', result.keys())
        self.assertEqual(2, len(result.get('PRIV')))
        self.assertIn({ 'owner': 'Naftuli', 'data': b64encode(b'something') }, result.get('PRIV'))
        self.assertIn({ 'owner': 'The Dude', 'data': b64encode(b'amazing') }, result.get('PRIV'))

        # run again, making sure that APIC shows up this time
        result = to_json_dict(fixture, include_pics=True)

        self.assertEqual(2, len(result.get('APIC')))

        self.assertIn({
            'data': b64encode(bytes([0x00] * 32)).decode('utf-8'),
            'desc': "Cover",
            'mime': 'image/jpeg',
            'type': 3,
            'type_friendly': "COVER_FRONT",
        }, result.get('APIC'))

        self.assertIn({
            'data': b64encode(bytes([0x00] * 32)).decode('utf-8'),
            'desc': 'Back Cover',
            'mime': 'image/jpeg',
            'type': 4,
            'type_friendly': "COVER_BACK",
        }, result.get('APIC'))

    def test_to_json_dict_flat(self):
        """Tests the flat json dict."""
        fixture = ID3()
        fixture.add(TPE2(encoding=Encoding.UTF8, text="Album Artist"))
        fixture.add(TIT2(encoding=Encoding.UTF8, text=["Title 1", "Title 2"]))
        fixture.add(APIC(encoding=Encoding.UTF8, mime="image/jpeg", type=PictureType.COVER_FRONT, desc="Cover",
            data=bytes([0x00]*8)))

        result = to_json_dict(fixture, flatten=True, include_pics=True)

        # test that it flattens the TPE2
        self.assertIn('TPE2', result.keys())
        self.assertEqual("Album Artist", result.get('TPE2'))

        # test that it does _NOT_ flatten the TIT2
        self.assertIn('TIT2', result.keys())
        self.assertEqual(2, len(result.get('TIT2')))
        self.assertIn("Title 1", result.get('TIT2'))
        self.assertIn("Title 2", result.get('TIT2'))

        # test that it does not flatten a single picture
        self.assertIsNotNone(result.get('APIC', None))
        self.assertTrue(isinstance(result.get('APIC'), list))
        self.assertEqual(1, len(result.get('APIC')))


class FilterTestCase(unittest.TestCase):

    def test_non_picture_tags(self):
        """Tests that the non_picture_tags filter function returns only non-picture tags."""
        picture_binary = bytes([0x00] * 32)

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

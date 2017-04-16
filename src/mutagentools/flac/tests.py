#!/usr/bin/env python
# -*- coding: utf-8 -*-

from base64 import b64encode

from mutagen.flac import FLAC, Picture
from mutagen.id3 import (
    APIC, ID3, MCDI, TALB, TCOM, TCON, TDRC, TIT2, TLEN, TPE1, TPE2, TPOS, TPUB, TRCK, UFID
)

from mutagentools.flac import to_json_dict
from mutagentools.flac.convert import (
    convert_flac_to_id3,
    convert_generic_to_txxx,
    convert_encoder_to_txxx,
    convert_encoded_by_to_txxx,
    convert_encoder_settings_to_txxx,
    convert_disc_number_to_tpos,
    convert_track_number_to_trck,
    convert_genre_to_tcon,
    convert_length_to_tlen,
    convert_mbid_to_ufid,
    convert_album_to_talb,
    convert_organization_to_tpub,
    convert_albumartist_to_tpe2,
    convert_artist_to_tpe1,
    convert_date_to_tdrc,
    convert_title_to_tit2,
    convert_composer_to_tcom,
    convert_picture_to_apic,
    convert_toc_to_mcdi,
)

import json
import mock
import os
import struct
import unittest

from mock import patch


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

        result = to_json_dict(fixture, flatten=True, include_pics=True)

        # test that the album was flattened
        self.assertIn('album', result.keys())
        self.assertEqual('Album',result.get('album'))

        # test that both artists were imported
        self.assertIn('artist', result.keys())
        self.assertEqual(2, len(result.get('artist')))
        self.assertIn('Artist 1', result.get('artist'))
        self.assertIn('Artist 2', result.get('artist'))

        # test that the picture was not flattened
        self.assertIsNotNone(result.get('pictures', None))
        self.assertTrue(isinstance(result.get('pictures'), list))
        self.assertEqual(1, len(result.get('pictures')))


class FullConversionTestCase(unittest.TestCase):

    def test_convert_flac_to_id3(self):
        """Tests full conversion of a series of FLAC key-value pairs into an array of ID3 tags."""
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "fixtures/sample-flac-tags.json")) as f:
            fixture = json.load(f)

        flac_mock = mock.MagicMock()
        flac_mock.tags = fixture

        # create mock pictures
        cover_front = Picture()
        cover_front.type = 3
        cover_front.desc = 'Cover Front'
        cover_front.mime = 'image/jpeg'
        cover_front.data = [0x00] * 8

        cover_back = Picture()
        cover_back.type = 4
        cover_back.desc = 'Cover Back'
        cover_back.mime = 'image/jpeg'
        cover_back.data = [0x00] * 8

        flac_mock.pictures = [cover_front, cover_back]

        result = convert_flac_to_id3(flac_mock)

        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, list))

        # form it into a single ID3 object
        id3 = ID3()
        for tag in result:
            id3.add(tag)

        # album artist/artist/composer
        self.assertEqual(fixture.get('albumartist'), id3.get('TPE2'))
        self.assertEqual(fixture.get('artist'), id3.get('TPE1'))
        self.assertEqual(fixture.get('composer'), id3.get('TCOM'))

        # album/disk id/date/genre/publisher org
        self.assertEqual(fixture.get('album'), id3.get('TALB'))
        self.assertEqual(['1/1'], id3.get('TPOS'))
        self.assertEqual(fixture.get('date'), id3.get('TDRC'))
        self.assertEqual([fixture.get('genre')] + list(fixture.get('style')), id3.get('TCON'))
        self.assertEqual([fixture.get('organization')], id3.get('TPUB'))

        # album toc and musicbrainz id
        self.assertIsNotNone(id3.get('MCDI'))
        self.assertEqual(28, struct.unpack('>I', id3.get('MCDI').data[0:4])[0])

        self.assertEqual(fixture.get('mbid').encode('ascii'), id3.get('UFID:http://musicbrainz.org').data)

        # track/track number/length
        self.assertEqual(fixture.get('title'), id3.get('TIT2'))
        self.assertEqual(['01/28'], id3.get('TRCK'))
        self.assertEqual(['152826'], id3.get('TLEN'))

        # make sure that CRC got dropped
        self.assertIsNone(id3.get('TXXX:crc'))

        # encoding tags
        self.assertEqual(fixture.get('encoder'), id3.get('TXXX:original encoder'))
        self.assertEqual(fixture.get('encoded by'), id3.get('TXXX:originally encoded by'))
        self.assertEqual(fixture.get('encoder settings'), id3.get('TXXX:original encoder settings'))

        # test that miscellaneous tags got brought in
        self.assertEqual(fixture.get('source'), id3.get('TXXX:source'))
        self.assertEqual(fixture.get('profile'), id3.get('TXXX:profile'))
        self.assertEqual(fixture.get('cddb disc id'), id3.get('TXXX:cddb disc id'))
        self.assertEqual(fixture.get('accurateripdiscid'), id3.get('TXXX:accurateripdiscid'))
        self.assertEqual(fixture.get('accurateripresult'), id3.get('TXXX:accurateripresult'))

        # test that there's only a fixed number of TXXX tags there
        self.assertEqual(8, len(list(filter(lambda t: t.FrameID == "TXXX", id3.values()))))

        # test that pictures work
        apic_list = list(filter(lambda t: t.FrameID == 'APIC', id3.values()))
        apic_front = list(filter(lambda p: p.type == 3, apic_list))[0]
        apic_back = list(filter(lambda p: p.type == 4, apic_list))[0]
        self.assertEqual(2, len(apic_list))
        # test front picture
        self.assertEqual(cover_front.type, apic_front.type)
        self.assertEqual(cover_front.mime, apic_front.mime)
        self.assertEqual(cover_front.desc, apic_front.desc)
        self.assertEqual(bytes(cover_front.data), apic_front.data)
        # test back picture
        self.assertEqual(cover_back.type, apic_back.type)
        self.assertEqual(cover_back.mime, apic_back.mime)
        self.assertEqual(cover_back.desc, apic_back.desc)
        self.assertEqual(bytes(cover_back.data), apic_back.data)

    def test_convert_flac_to_id3_track(self):
        """
        Test that converting FLAC tags to ID3 tags for complicated tracknumber tags.

        Sometimes we'll get a bullshit tracknumber tag which will be %d/%d which we will need to expand and resolve
        properly into correct ID3 format.
        """

        flac_mock = mock.MagicMock()
        flac_mock.tags = { 'tracknumber': '1/5' }

        id3 = ID3()
        list(map(lambda t: id3.add(t), convert_flac_to_id3(flac_mock)))

        self.assertEqual(['01/05'], id3.get('TRCK'))

    def test_convert_flac_to_id3_adds_tpos(self):
        """Test that convert_flac_to_id3 adds TPOS if not present."""
        flac_mock = mock.MagicMock()
        flac_mock.tags = {}

        id3 = ID3()
        list(map(lambda t: id3.add(t), convert_flac_to_id3(flac_mock)))

        self.assertEqual(['1/1'], id3.get('TPOS'))


class IndividualConversionTestCase(unittest.TestCase):

    def test_convert_generic_to_txxx(self):
        """Test converting a generic FLAC Vorbis comment into a TXXX tag."""
        key, value = "accurateripdiscid", "028-0030bb28-03c552e0-8b0b7f1c-1"

        result = convert_generic_to_txxx(key, value)

        self.assertIsNotNone(result)
        self.assertEqual(key, result.desc)
        self.assertEqual([value], result.text)

    def test_convert_encoder_to_txxx(self):
        """Test converting an encoder tag to a TXXX tag."""
        value = "FLAC 1.2.1"
        result = convert_encoder_to_txxx(value)

        self.assertIsNotNone(result)
        self.assertEqual("original encoder", result.desc)
        self.assertEqual([value], result.text)

    def test_convert_encoded_by_to_txxx(self):
        """Test converting an encoded by tag to a TXXX tag."""
        value = "dBpoweramp Release 14.2"
        result = convert_encoded_by_to_txxx(value)

        self.assertIsNotNone(result)
        self.assertEqual("originally encoded by", result.desc)
        self.assertEqual([value], result.text)

    def test_convert_encoder_settings_to_txxx(self):
        """Test converting an encoder settings tag to a TXXX tag."""
        value = "-compression-level-5 -verify"
        result = convert_encoder_settings_to_txxx(value)

        self.assertIsNotNone(result)
        self.assertEqual("original encoder settings", result.desc)
        self.assertEqual([value], result.text)

    def test_convert_disc_number_to_tpos(self):
        """Test converting a FLAC disc number to TPOS."""
        # first test with only a disc number
        disc_number = "2"
        result = convert_disc_number_to_tpos(disc_number)

        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, TPOS))
        self.assertEqual(["2"], result.text)

        # test with disc number and total discs
        disc_number = "2"
        total_discs = "5"
        result = convert_disc_number_to_tpos(disc_number, total_discs)

        self.assertEqual(["2/5"], result.text)

    def test_convert_tracknumber_to_trck(self):
        """Test converting a FLAC track number to TRCK."""
        # first test with only a track number
        track_number = "1"
        result = convert_track_number_to_trck(track_number)

        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, TRCK))
        self.assertEqual(["01"], result.text)

        # next, test with both track number and track count
        track_number = "3"
        total_tracks = "9"
        result = convert_track_number_to_trck(track_number, total_tracks)

        self.assertEqual(["03/09"], result.text)

        # next, futz around with arrays
        result = convert_track_number_to_trck([1], [13])
        self.assertEqual(["01/13"], result.text)


    def test_convert_genre_to_tcon(self):
        """Test converting a FLAC genre tag to a TCON ID3 tag."""
        fixture = "Genre"
        result = convert_genre_to_tcon(fixture)

        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, TCON))
        self.assertEqual([fixture], result.text)

        fixture = ["Genre 1", "Genre 2"]
        fixture_s = ["Style 1", "Style 2"]
        result = convert_genre_to_tcon(fixture, fixture_s)

        self.assertEqual(["Genre 1", "Genre 2", "Style 1", "Style 2"], result.text)

    def test_convert_length_to_tlen(self):
        """Test converting a FLAC length tag to a TLEN ID3 tag."""
        # test with single instance
        fixture = 12345
        result = convert_length_to_tlen(fixture)

        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, TLEN))
        self.assertEqual([str(fixture)], result.text)

        # test with an array
        fixture = ['12345']
        result = convert_length_to_tlen(fixture)

        self.assertEqual(fixture, result.text)


    def test_convert_mbid_to_ufid(self):
        """Test converting a MusicBrainz ID to an ID3 UFID tag."""
        fixture = "a56e6f46-f45b-4271-b389-904297463aaf"
        result = convert_mbid_to_ufid(fixture)

        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, UFID))
        self.assertEqual('http://musicbrainz.org', result.owner)
        self.assertEqual(bytes(fixture, 'ascii'), result.data)

    def test_convert_album_to_talb(self):
        """Test converting a FLAC album to a TALB ID3 tag."""
        fixture = "Album"
        result = convert_album_to_talb(fixture)

        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, TALB))
        self.assertEqual([fixture], result.text)

    def test_convert_organization_to_tpub(self):
        """Test converting a FLAC organization to a TPUB ID3 tag."""
        fixture = "Organization"
        result = convert_organization_to_tpub(fixture)

        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, TPUB))
        self.assertEqual([fixture], result.text)

    def test_convert_albumartist_to_tpe2(self):
        """Test converting a FLAC album artist tag into a TPE2 ID3 tag."""
        fixture = "Album Artist"
        result = convert_albumartist_to_tpe2(fixture)

        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, TPE2))
        self.assertEqual([fixture], result.text)

    def test_convert_artist_to_tpe1(self):
        """Test converting a FLAC artist tag into a TPE1 ID3 tag."""
        fixture = "Artist 1"
        result = convert_artist_to_tpe1(fixture)

        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, TPE1))
        self.assertEqual(result.text, [fixture])

        # test multiple artists
        fixture = ["Artist 1", "Artist 2"]
        result = convert_artist_to_tpe1(fixture)

        self.assertEqual(result.text, fixture)

    def test_convert_date_to_tdrc(self):
        """Test converting a FLAC date tag into a TDRC ID3 tag."""
        fixture = "2017"
        result = convert_date_to_tdrc(fixture)

        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, TDRC))
        # mutagen renders this value as an ID3TimeStamp, so map it to a string
        self.assertEqual(list(map(lambda i: str(i), result.text)), [fixture])

    def test_convert_title_to_tit2(self):
        """Test converting a FLAC title tag into a TIT2 ID3 tag."""
        fixture = "Title"
        result = convert_title_to_tit2(fixture)

        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, TIT2))
        self.assertEqual(result.text, [fixture])

    def test_convert_composer_to_tcom(self):
        """Tests converting a FLAC composer tag into a TCOM ID3 tag."""
        # test single string
        fixture = "Composer 1"
        result = convert_composer_to_tcom(fixture)

        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, TCOM))
        self.assertEqual(result.text, [fixture])

        # test an array
        fixture = ["Composer 1", "Composer 2"]
        result = convert_composer_to_tcom(fixture)

        self.assertEqual(result.text, fixture)

    def test_convert_picture_to_apic(self):
        """Tests converting a FLAC picture to an APIC ID3 tag."""
        fixture = Picture()
        fixture.desc = "OMG DESC"
        fixture.data = bytes([0x00] * 8)
        fixture.mime = "image/jpeg"
        fixture.type = 3

        result = convert_picture_to_apic(fixture)

        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, APIC))

        # test properties
        self.assertEqual(fixture.desc, result.desc)
        self.assertEqual(fixture.data, result.data)
        self.assertEqual(fixture.mime, result.mime)
        self.assertEqual(fixture.type, result.type)

    def test_convert_toc_to_mcdi(self):
        """Tests converting a FLAC CDTOC to an MCDI ID3 tag."""
        fixture = b"1C+96+2D5C+30DE+5B58+7F78+AB96+D9FE+DDC8+101B6+12A96+14C97+17183+17324+19F19+1C986+1E1DD+1E7F1+20524+221BE+22674+23809+26B9F+27F2F+2B19E+2D23F+2FA58+31C6E+3355F+35F04"
        fixture_len = len(fixture.split(b"+"))

        result = convert_toc_to_mcdi(fixture)

        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, MCDI))

        # test length
        self.assertEqual(4 + ((fixture_len - 1) * 8), len(result.data))

        # test track count
        self.assertEqual(28, struct.unpack('>I', result.data[0:4])[0])
        # test that first track begins at sector 150
        self.assertEqual(150, struct.unpack('>Q', result.data[4:12])[0])

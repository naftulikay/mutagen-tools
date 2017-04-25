#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mutagen.id3 import (
    APIC, ID3, MCDI, TALB, TCON, TCOM, TDRC, TIT2, TLEN, TPE1, TPE2, TPOS, TPUB, TRCK, TXXX, UFID, Encoding
)

from mutagentools.utils import (
    contains_any,
    first,
    first_of_list,
    pop_keys,
)

import re
import six
import struct


PART_OF_SET = re.compile(r'^(?P<number>\d+)/(?P<total>\d+)$')


def convert_flac_to_id3(flac):
    """Convert FLAC tags to ID3 tags."""
    result = []
    tags = dict(flac.tags)

    # remove crc because we don't care about the original FLAC's CRC
    tags.pop('crc') if 'crc' in tags.keys() else None

    # artist related tags
    if contains_any(tags.keys(), 'albumartist', 'album artist'):
        result.append(convert_albumartist_to_tpe2(first(pop_keys(tags, 'albumartist', 'album artist'))))

    if contains_any(tags.keys(), 'artist', 'author'):
        result.append(convert_artist_to_tpe1(first(pop_keys(tags, 'artist', 'author'))))

    if 'composer' in tags.keys():
        result.append(convert_composer_to_tcom(tags.pop('composer')))

    # album related tags
    if 'album' in tags.keys():
        result.append(convert_album_to_talb(tags.pop('album')))

    if 'genre' in tags.keys():
        result.append(convert_genre_to_tcon(tags.pop('genre'), tags.pop('style') if 'style' in tags.keys() else []))

    if 'discnumber' in tags.keys():
        result.append(convert_disc_number_to_tpos(first_of_list(tags.pop('discnumber')),
            first_of_list(first(pop_keys(tags, 'totaldiscs', 'disctotal')))))

    if contains_any(tags.keys(), 'date', 'year'):
        result.append(convert_date_to_tdrc(first(pop_keys(tags, 'date', 'year'))))

    if 'organization' in tags.keys():
        result.append(convert_organization_to_tpub(tags.pop('organization')))

    if 'cdtoc' in tags.keys():
        result.append(convert_toc_to_mcdi(tags.pop('cdtoc')))

    if 'mbid' in tags.keys():
        result.append(convert_mbid_to_ufid(tags.pop('mbid')))

    # track related tags
    if 'title' in tags.keys():
        result.append(convert_title_to_tit2(tags.pop('title')))

    if 'tracknumber' in tags.keys():
        tracknumber = first_of_list(tags.pop('tracknumber'))
        totaltracks = first_of_list(first(pop_keys(tags, 'totaltracks', 'tracktotal')))

        if PART_OF_SET.match(tracknumber):
            # it's a complicated dude
            tracknumber, totaltracks = PART_OF_SET.match(tracknumber).groups()

        result.append(convert_track_number_to_trck(tracknumber, totaltracks))

    if 'length' in tags.keys():
        result.append(convert_length_to_tlen(tags.pop('length')))

    # encoding tags
    if 'encoder' in tags.keys():
        result.append(convert_encoder_to_txxx(tags.pop('encoder')))

    if 'encoded by' in tags.keys():
        result.append(convert_encoded_by_to_txxx(tags.pop('encoded by')))

    if 'encoder settings' in tags.keys():
        result.append(convert_encoder_settings_to_txxx(tags.pop('encoder settings')))

    # catch the rest in txxx
    for tag in tags:
        result.append(convert_generic_to_txxx(tag, tags.get(tag)))

    # add the pictures
    for picture in flac.pictures:
        result.append(APIC(
            encoding=Encoding.UTF8,
            type=picture.type,
            desc=picture.desc,
            mime=picture.mime,
            data=bytes(picture.data))
        )

    # if there is no disc number, add one manually
    if not 'TPOS' in list(map(lambda t: t.FrameID, result)):
        result.append(convert_disc_number_to_tpos('1', '1'))

    return result


def convert_generic_to_txxx(flac_key, flac_value):
    """Converts a generic FLAC Vorbis comment into a TXXX tag."""
    return TXXX(encoding=Encoding.UTF8, desc=flac_key, text=flac_value)


def convert_encoder_to_txxx(flac_encoder):
    """Converts a FLAC encoder Vorbis comment into a TXXX tag."""
    return TXXX(encoding=Encoding.UTF8, desc="original encoder", text=flac_encoder)


def convert_encoded_by_to_txxx(flac_encoded_by):
    """Converts a FLAC encoded by Vorbis comment into a TXXX tag."""
    return TXXX(encoding=Encoding.UTF8, desc="originally encoded by", text=flac_encoded_by)


def convert_encoder_settings_to_txxx(flac_encoder_settings):
    """Converts a FLAC encoder settings Vorbis comment into a TXXX tag."""
    return TXXX(encoding=Encoding.UTF8, desc="original encoder settings", text=flac_encoder_settings)


def convert_disc_number_to_tpos(flac_discnumber, flac_totaldiscs=None):
    """Converts a FLAC disc number and optionally total discs into a TPOS tag."""
    # unwrap
    flac_discnumber = flac_discnumber if not isinstance(flac_discnumber, list) else flac_discnumber[0]

    value = "{:01}".format(int(flac_discnumber))

    if flac_totaldiscs and len(flac_totaldiscs) > 0:
        if isinstance(flac_totaldiscs, list):
            # unpack
            flac_totaldiscs = flac_totaldiscs[0]

        value = "{}/{:01}".format(value, int(flac_totaldiscs))

    return TPOS(encoding=Encoding.UTF8, text=value)


def convert_track_number_to_trck(flac_tracknumber, flac_totaltracks=None):
    """Converts a FLAC track number and optionally total tracks into a TRCK tag."""
    if isinstance(flac_tracknumber, list):
        # unpack
        flac_tracknumber = flac_tracknumber[0]

    value = "{:02}".format(int(flac_tracknumber))

    if flac_totaltracks and len(flac_totaltracks) > 0:
        if isinstance(flac_totaltracks, list):
            # unpack
            flac_totaltracks = flac_totaltracks[0]

        value = "{}/{:02}".format(value, int(flac_totaltracks))

    return TRCK(encoding=Encoding.UTF8, text=value)


def convert_genre_to_tcon(flac_genre, flac_style=None):
    """Converts a FLAC genre and optionally styles into a TCON tag."""
    # convert both to lists
    flac_genre = flac_genre if isinstance(flac_genre, list) else [flac_genre]
    flac_style = flac_style if isinstance(flac_style, list) else [flac_style]

    # create a list of non-empty genres from the genres and styles
    genre_list = list(filter(lambda i: i is not None, flac_genre + flac_style))

    # return genres first, followed by styles
    return TCON(encoding=Encoding.UTF8, text=genre_list)


def convert_length_to_tlen(flac_length):
    """Converts a FLAC length in milliseconds into a TLEN tag."""
    if isinstance(flac_length, (set, list)):
        flac_length = flac_length[0]

    return TLEN(encoding=Encoding.UTF8, text=str(flac_length))


def convert_mbid_to_ufid(flac_mbid):
    """Converts a FLAC MusicBrainz ID into a UFID tag."""
    if isinstance(flac_mbid, list):
        # flatten that shita
        flac_mbid = flac_mbid[0]

    return UFID(owner="http://musicbrainz.org", data=flac_mbid if isinstance(flac_mbid, six.binary_type) else \
        six.b(flac_mbid))


def convert_album_to_talb(flac_album):
    """Converts a FLAC album to a TALB tag."""
    return TALB(encoding=Encoding.UTF8, text=flac_album)


def convert_organization_to_tpub(flac_organization):
    """Converts a FLAC organization (record label) into a TPUB tag."""
    return TPUB(encoding=Encoding.UTF8, text=flac_organization)


def convert_albumartist_to_tpe2(flac_albumartist):
    """Converts a FLAC album artist into a TPE2 tag."""
    return TPE2(encoding=Encoding.UTF8, text=flac_albumartist)


def convert_artist_to_tpe1(flac_artist):
    """Converts a FLAC artist into a TPE1 tag."""
    return TPE1(encoding=Encoding.UTF8, text=flac_artist)


def convert_title_to_tit2(flac_title):
    """Converts a FLAC title into a TIT2 tag."""
    return TIT2(encoding=Encoding.UTF8, text=flac_title)


def convert_date_to_tdrc(flac_date):
    """Converts a FLAC date into a TDRC tag."""
    return TDRC(encoding=Encoding.UTF8, text=flac_date)


def convert_composer_to_tcom(composer):
    """Converts a FLAC composer tag into a TCOM."""
    return TCOM(encoding=Encoding.UTF8, text=composer)


def convert_picture_to_apic(flac_picture):
    """Converts a FLAC picture into an APIC tag."""
    return APIC(encoding=Encoding.UTF8, mime=flac_picture.mime, type=flac_picture.type, desc=flac_picture.desc,
        data=flac_picture.data)


def convert_toc_to_mcdi(flac_toc):
    """Converts a FLAC formatted CDTOC into an MCDI ID3 tag."""
    # docs https://forum.dbpoweramp.com/showthread.php?16705-FLAC-amp-Ogg-Vorbis-Storage-of-CDTOC
    if not (isinstance(flac_toc, six.string_types) or isinstance(flac_toc, six.binary_type)) \
            and isinstance(flac_toc, (list, set)):
        # if it's a list and not just a sequence of bytes or characters, get the first entry
        flac_toc = flac_toc[0]

    # split the string/bytes on a '+' separator, parsing each entry as integers
    toc = [int(i, 16) for i in flac_toc.split(b'+' if isinstance(flac_toc, six.binary_type) else '+')]

    # track count is a 32bit unsigned integer; each address is a 64bit unsigned integer
    track_count, track_addresses = struct.pack('>I', toc[0]), list(map(lambda a: struct.pack('>Q', a), toc[1:]))

    # flatten out all of the bytes for the various entries and produce one long byte stream
    return MCDI(data=b''.join([track_count] + track_addresses))

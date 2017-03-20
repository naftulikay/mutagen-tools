#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mutagentools.id3.filters

from mutagentools.id3.filters import private_google_tags


def strip_private_tags(id3, save=True):
    """Removes all private identifying tags from a given ID3 instance."""
    private_tags = list(private_google_tags(id3).keys())

    for k in private_tags:
        # remove the tag
        id3.pop(k)

    if save:
        id3.save()

    return private_tags

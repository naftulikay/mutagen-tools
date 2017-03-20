#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from mutagentools.utils import fold_text_keys


import unittest

from unittest import mock
from unittest.mock import patch


class MainTestCase(unittest.TestCase):

    def test_fold_text_keys(self):
        """Tests that fold_text_keys collapses properly."""
        fixture = {
            'a': 'b',
            'b': ['a'],
            'c': ['a', 'b'],
            'd': [{ 'a': 'b' }],
        }

        fold_text_keys(fixture)

        # key a should not have changed
        self.assertEqual('b', fixture.get('a'))
        # key b should have been flattened
        self.assertEqual('a', fixture.get('b'))
        # key c should not have been flattened
        self.assertEqual(['a', 'b'], fixture.get('c'))
        # key d should not have been flattened
        self.assertEqual([{ 'a': 'b' }], fixture.get('d'))

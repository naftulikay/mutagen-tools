#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mutagentools.utils import (
    contains_any,
    first,
    first_of_list,
    fold_text_keys,
    pop_keys,
)


import mock
import unittest

from mock import patch


class MainTestCase(unittest.TestCase):

    def test_contains_any(self):
        """Tests that contains_any does the thing."""
        self.assertTrue(contains_any(['thing', 'other'], 'thing'))
        self.assertTrue(contains_any(['thing', 'other'], 'thing', 'other'))
        self.assertFalse(contains_any(['other'], 'nope'))

    def test_first(self):
        """Tests that first does the thing."""
        self.assertEqual('one', first(['one']))
        self.assertEqual('one', first(['one', 'two', 'three']))
        self.assertIsNone(first([]))

    def test_first_of_list(self):
        """Tests that first_of_list returns the right first value."""
        self.assertEqual(b'12345', first_of_list(b'12345'))
        self.assertEqual('45678', first_of_list('45678'))
        self.assertEqual('90123', first_of_list(['90123']))
        self.assertEqual('45678', first_of_list(('45678',)))

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

    def test_pop_keys(self):
        """Tests that pop_extant pops extant keys."""
        fixture = {
            'a': 1,
            'b': 2,
            'c': 3
        }
        self.assertEqual([1, 2], pop_keys(fixture, 'a', 'b'))
        self.assertEqual({'c': 3}, fixture)

# -*- coding: UTF-8 -*-
__author__ = 'johan'

import unittest
import shutil
import os
from torganizer.files import SoundFileMP3, SoundFileGeneric


def testfile(f):
    # simple helper for tests
    p = os.path.join('tests/resources/testdir', f)
    shutil.copy('tests/resources/sample.mp3', p)
    return p


class TestTorganizerSoundFileGeneric(unittest.TestCase):

    def setUp(self):
        self.testdir = 'tests/resources/testdir'
        if os.path.exists(self.testdir):
            shutil.rmtree(self.testdir)
        os.mkdir(self.testdir)

    def test_parse_file_name(self):
        f = testfile('01 - Title Name.mp3')
        o = SoundFileGeneric(f)
        self.assertEqual('01', o.track_number)
        self.assertEqual('Title Name', o.title_name)
        self.assertEqual('01 - Title Name.mp3', str(o))

        f = testfile('01. Title Name .mp3')
        o = SoundFileGeneric(f)
        self.assertEqual('01', o.track_number)
        self.assertEqual('Title Name', o.title_name)
        self.assertEqual('01 - Title Name.mp3', str(o))

        f = testfile('01 Title Name.mp3')
        o = SoundFileGeneric(f)
        self.assertEqual('01', o.track_number)
        self.assertEqual('Title Name', o.title_name)
        self.assertEqual('01 - Title Name.mp3', str(o))

        f = testfile('01-aphex_twin-minipops_67_(120.2)(source_field_mix).mp3')
        o = SoundFileGeneric(f)
        self.assertEqual('01', o.track_number)
        self.assertEqual('minipops 67 (120.2)(source field mix)', o.title_name)
        self.assertEqual('Aphex Twin', o.artist_name)
        self.assertEqual('01 - minipops 67 (120.2)(source field mix).mp3', str(o))

        f = testfile('07 Muffler - Strange Minds (Album Version).mp3')
        o = SoundFileGeneric(f)
        self.assertEqual('07', o.track_number)
        self.assertEqual('Strange Minds (Album Version)', o.title_name)
        self.assertIsNone(o.artist_name)
        self.assertEqual('07 - Strange Minds (Album Version).mp3', str(o))

        # stuff like this won't be parsable, if no metadata provided
        # it is off to the manual processing bin
        f = testfile('Kent - En Plats I Solen - 02 - Ismael.mp3')
        o = SoundFileGeneric(f)
        self.assertIsNone(o.track_number)
        self.assertIsNone(o.artist_name)
        self.assertIsNone(o.title_name)
        with self.assertRaises(Exception):
            str(o)

    def tearDown(self):
        shutil.rmtree(self.testdir)
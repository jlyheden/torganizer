__author__ = 'johan'

import unittest
import ntpath
from torganizer.types import *


class TestTorganizerMusicType(unittest.TestCase):

    def setUp(self):
        self.os_path_orig = os.path

    def test_parse_filepath(self):

        # simple test
        path = "/path/to/Artist Name - Album Name"
        o = MusicType(src_path=path, dst_path="")
        self.assertEqual(o.get_album_name(), "Album Name")
        self.assertEqual(o.get_artist_name(), "Artist Name")

        # with multi -
        path = "/path/to/Artist Name - Album - Name"
        o = MusicType(src_path=path, dst_path="")
        self.assertEqual(o.get_album_name(), "Album - Name")
        self.assertEqual(o.get_artist_name(), "Artist Name")

        # with whitespace replacements
        path = "/path/to/Artist_Name_-_Album_Name"
        o = MusicType(src_path=path, dst_path="")
        self.assertEqual(o.get_album_name(), "Album Name")
        self.assertEqual(o.get_artist_name(), "Artist Name")

        # windows syntax - monkey patching included
        os.path = ntpath
        path = r"c:\path\to\Artist Name - Album Name"
        o = MusicType(src_path=path, dst_path="")
        self.assertEqual(o.get_artist_name(), "Artist Name")
        self.assertEqual(o.get_album_name(), "Album Name")
        os.path = self.os_path_orig

    def test_full_dst_path(self):

        src = "/path/to/Artist_Name_-_Album_Name_(2014)"
        o = MusicType(src_path=src, dst_path="/stuff")
        self.assertEqual(o.full_path_to_dst(), "/stuff/Artist Name/Album Name (2014)")

        os.path = ntpath
        src = r'C:\path\to\Artist_Name_-_Album_Name_(2014)'
        o = MusicType(src_path=src, dst_path=r'C:\stuff')
        self.assertEqual(o.full_path_to_dst(), r'C:\stuff\Artist Name\Album Name (2014)')
        os.path = self.os_path_orig

    def test_analyze_files(self):
        # monkey patching
        os_listdir_orig = os.listdir
        os.listdir = lambda x: ['file.nfo', '01 - Title 1.mp3', '02 - Title 2.MP3']
        o = MusicType(src_path="", dst_path="")
        self.assertDictEqual(o.analyze_files(), {
            '01 - Title 1.mp3': CopyAction,
            '02 - Title 2.MP3': CopyAction
        })
        os.listdir = os_listdir_orig


if __name__ == '__main__':
    unittest()
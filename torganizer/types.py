__author__ = 'johan'

import re
import os
import shutil
import logging
from torganizer.actions import CopyAction, DummyCopyAction
from torganizer.files import SoundFileMP3
from mutagen.id3 import ID3
from collections import Counter

logger = logging.getLogger(__name__)


class BaseType(object):
    """
    Inherit from the BaseType
    """

    # override in child class
    file_types = {}
    file_types_ignore = []
    file_types_fallback_action = DummyCopyAction

    def __init__(self, src_path, dst_path, tmp_path):
        self.src_path = src_path
        self.dst_path = dst_path
        self.tmp_path = tmp_path
        self.tmp_path_full = os.path.join(
            tmp_path,
            os.path.basename(src_path)
        )
        self.files_action = {}

    @staticmethod
    def sanitize_name(name):
        return re.sub(u"_", " ", name).lstrip().rstrip()

    @staticmethod
    def move_files(src, dst):
        shutil.move(src, dst)

    def analyze_files(self):
        for f in os.listdir(self.src_path):
            ending = os.path.splitext(f)[1].lower()
            try:
                if ending not in self.file_types_ignore:
                    self.files_action[f] = self.file_types[ending]
            except KeyError:
                self.files_action[f] = self.file_types_fallback_action

    def copy_to_dst(self):
        pass

    def copy_to_tmp(self, files_action):
        if os.path.exists(self.tmp_path_full):
            os.rmdir(self.tmp_path_full)
        os.mkdir(self.tmp_path_full)
        for fn, action in files_action:
            src = os.path.join(self.src_path, fn)
            dst = os.path.join(self.tmp_path_full, fn)
            action(src, dst).do()

    def post_process_tmp(self):
        pass

    def post_process_dst(self):
        pass

    def full_path_to_dst(self):
        pass


class MusicType(BaseType):

    file_types = {
        '.mp3': CopyAction,
        '.ogg': CopyAction,
        '.wma': CopyAction
    }
    file_types_ignore = ['.nfo']

    def __init__(self, src_path, dst_path, tmp_path, parse_metadata=False):
        super(MusicType, self).__init__(src_path=src_path, dst_path=dst_path, tmp_path=tmp_path)
        self.parse_metadata = parse_metadata
        self.album_name = self.get_album_name_from_path()
        self.artist_name = self.get_artist_name_from_path()

    def get_album_name_from_path(self):
        bn = os.path.basename(self.src_path)
        return self.sanitize_name("-".join(bn.split('-')[1:])).title()

    def get_artist_name_from_path(self):
        bn = os.path.basename(self.src_path)
        return self.sanitize_name("-".join(bn.split('-')[:1])).title()

    def full_path_to_dst(self):
        return os.path.join(self.dst_path, self.artist_name, self.album_name)

    def get_album_details_from_id3(self, d):
        artist_name = []
        album_name = []
        for x in os.listdir(d):
            if os.path.splitext(x)[1] in self.file_types.keys():
                f = os.path.join(d, x)
                f_id3 = ID3(f)
                artist_name.append(f_id3['TPE1'].text[0]).title()
                album_name.append(f_id3['TALB'].text[0]).title()
        return Counter(artist_name).most_common()[0][0], abn.most_common()[0][0]

    def post_process_tmp(self):
        if self.parse_metadata:
            tmp_artist, tmp_album = self.get_album_details_from_id3(self.tmp_path_full)
            if tmp_artist:
                logger.debug("Found artist name '%s' from id3 tag, using it instead" % ())
                self.artist_name = tmp_artist
            if tmp_album:
                self.album_name = tmp_album
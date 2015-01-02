__author__ = 'johan'

import re
import os
import shutil
from torganizer.actions import CopyAction, DummyCopyAction


class BaseType(object):
    """
    Inherit from the BaseType
    """

    # override in child class
    file_types = {}
    file_types_ignore = []
    file_types_fallback_action = DummyCopyAction

    def __init__(self, src_path, dst_path):
        self.src_path = src_path
        self.dst_path = dst_path

    @staticmethod
    def sanitize_name(name):
        return re.sub(u"_", " ", name).lstrip().rstrip()

    @staticmethod
    def move_files(src, dst):
        shutil.move(src, dst)

    def analyze_files(self):
        files = os.listdir(self.src_path)
        file_action = {}
        for f in files:
            ending = os.path.splitext(f)[1].lower()
            try:
                if ending not in self.file_types_ignore:
                    file_action[f] = self.file_types[ending]
            except KeyError:
                file_action[f] = self.file_types_fallback_action
        return file_action

    def tmp_directory(self):
        return os.path.join(self.t)

    def copy(self):
        pass

    def dummy_copy(self, src_path, dst_path):
        """
        Use for fallback files or whatever files you want to skip
        :return:
        """
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

    def __init__(self, src_path, dst_path, parse_metadata=False):
        super(MusicType, self).__init__(src_path=src_path, dst_path=dst_path)
        self.parse_metadata = parse_metadata
        self.album_name = self.get_album_name()
        self.artist_name = self.get_artist_name()

    def get_album_name(self):
        bn = os.path.basename(self.src_path)
        return self.sanitize_name("-".join(bn.split('-')[1:]))

    def get_artist_name(self):
        bn = os.path.basename(self.src_path)
        return self.sanitize_name("-".join(bn.split('-')[:1]))

    def full_path_to_dst(self):
        return os.path.join(self.dst_path, self.artist_name, self.album_name)


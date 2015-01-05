__author__ = 'johan'

import os
import shutil
import logging
from torganizer.actions import action_factory
from torganizer.files import soundfile_factory
from torganizer.utils import sanitize_string, unicode_squash
from collections import Counter

logger = logging.getLogger(__name__)


class BaseHandler(object):
    """
    Inherit from the BaseType
    """

    # override in child class
    file_types = []
    file_types_ignore = []

    def __init__(self, src_path, dst_path, tmp_path):
        self.src_path = src_path
        self.dst_path = dst_path
        self.dst_path_full = None
        self.tmp_path = tmp_path
        self.tmp_path_full = os.path.join(tmp_path, os.path.basename(src_path))
        self.files_action = {}
        self.analyze_files()

    def analyze_files(self):
        for f in os.listdir(self.src_path):
            ending = os.path.splitext(f)[1].lower()
            if ending not in self.file_types_ignore:
                self.files_action[f] = action_factory(f)

    def copy_to_dst(self):
        if not os.path.exists(self.dst_path_full):
            logger.info("Destination directory '%s' does not exist. Creating it" % self.dst_path_full)
            os.makedirs(self.dst_path_full)
        for x in os.listdir(self.tmp_path_full):
            shutil.copy(os.path.join(self.tmp_path_full, x), self.dst_path_full)

    def copy_to_tmp(self):
        if os.path.exists(self.tmp_path_full):
            shutil.rmtree(self.tmp_path_full)
        os.mkdir(self.tmp_path_full)
        for fn, action in self.files_action.items():
            src = os.path.join(self.src_path, fn)
            dst = os.path.join(self.tmp_path_full, fn)
            # could thread this
            action().do(src, dst)

    def post_process_tmp(self):
        pass

    def post_process_dst(self):
        logger.info("Purging tmp directory '%s'" % self.tmp_path_full)
        shutil.rmtree(self.tmp_path_full)

    def full_path_to_dst(self):
        pass

    @staticmethod
    def rename_file(src, dst):
        if src == dst:
            logger.debug("Not renaming file '%s' to '%s', destination is identical to source" % (src, dst))
        else:
            logger.debug("Renaming file '%s' to '%s'" % (src, dst))
            os.rename(src, dst)

    def execute(self):
        self.copy_to_tmp()
        self.post_process_tmp()
        self.copy_to_dst()
        self.post_process_dst()


class MusicHandler(BaseHandler):

    file_types = ['.mp3']
    file_types_ignore = ['.nfo']

    def __init__(self, src_path, dst_path, tmp_path, parse_metadata=False):
        super(MusicHandler, self).__init__(src_path=src_path, dst_path=dst_path, tmp_path=tmp_path)
        self.parse_metadata = parse_metadata
        self.album_name = self.get_album_name_from_path()
        self.artist_name = self.get_artist_name_from_path()

    def get_album_name_from_path(self):
        bn = os.path.basename(self.src_path)
        return sanitize_string("-".join(bn.split('-')[1:])).title()

    def get_artist_name_from_path(self):
        bn = os.path.basename(self.src_path)
        return sanitize_string("-".join(bn.split('-')[:1])).title()

    def full_path_to_dst(self):
        return os.path.join(self.dst_path, self.artist_name, self.album_name)

    def is_compilation(self):
        if os.path.basename(self.src_path).lower().startswith('va'):
            return True
        else:
            return False

    def post_process_tmp(self):
        """
        TODO: no support for directory trees (cd1/ cd2/) etc
        Scans files for metadata for artist name and album name
        Renames files based on name and metadata analytics

        :return:
        """
        album_names = []
        artist_names = []
        for f in os.listdir(self.tmp_path_full):
            ext = os.path.splitext(f)[1]
            if ext in self.file_types:
                soundfile_class = soundfile_factory(f)
                soundfile = soundfile_class(os.path.join(self.tmp_path_full, f))
                if not self.is_compilation():
                    album_names.append(soundfile.album_name)
                    artist_names.append(soundfile.artist_name)
                self.rename_file(soundfile.filename_path, os.path.join(self.tmp_path_full, str(soundfile)))
        if len(album_names) > 0:
            self.album_name = Counter(album_names).most_common()[0][0]
        if len(artist_names) > 0:
            self.artist_name = Counter(artist_names).most_common()[0][0]
        self.dst_path_full = unicode_squash(os.path.join(self.dst_path, self.artist_name, self.album_name))

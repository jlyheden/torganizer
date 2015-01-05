__author__ = 'johan'

import os
import shutil
import logging
from torganizer.actions import action_factory
from torganizer.files import soundfile_factory
from torganizer.utils import sanitize_string

logger = logging.getLogger(__name__)


class BaseHandler(object):
    """
    Inherit from the BaseType
    """

    # override in child class
    file_types = []
    file_types_ignore = []

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.dst_path_full = None
        self.tmp_path_full = os.path.join(self.tmp_path, os.path.basename(self.src_path))
        self.files_action = {}
        self.files_process = {}

    def analyze_files(self):
        pass

    def copy_to_dst(self):
        for value in self.files_process.values():
            value.copy(self.dst_path)

    def copy_to_tmp(self):
        if os.path.exists(self.tmp_path_full):
            shutil.rmtree(self.tmp_path_full)
        os.makedirs(self.tmp_path_full)
        for action in self.files_action.values():
            action.do()

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
        self.analyze_files()
        self.copy_to_tmp()
        self.post_process_tmp()
        self.copy_to_dst()
        self.post_process_dst()

    def is_copied(self, f):
        return os.path.splitext(f)[1] not in self.file_types_ignore


class MusicHandler(BaseHandler):

    file_types = ['.mp3']
    file_types_ignore = ['.nfo', '.cue', '.log', '.m3u']

    def is_handled(self, f):
        return os.path.splitext(f)[1].lower() in self.file_types

    def analyze_files(self):
        """
        We probably need to handle each type of media differently
        For example, music we want to retain sub folders for multi CD albums so that
        this folder metadata is preserved.

        :return:
        """
        for walk in os.walk(self.src_path):
            walk_dir = walk[0]
            walk_dir_files = walk[2]
            subfolder = walk_dir.lstrip(self.src_path)
            for walk_file in walk_dir_files:
                walk_file_path = os.path.join(walk_dir, walk_file)
                if self.is_copied(walk_file):
                    action = action_factory(walk_file)
                    self.files_action[walk_file_path] = action(src=walk_file_path, dst=os.path.join(self.tmp_path_full,
                                                                                                    subfolder))

    def post_process_tmp(self):
        """
        TODO: no support for directory trees (cd1/ cd2/) etc
        Scans files for metadata for artist name and album name
        Renames files based on name and metadata analytics

        :return:
        """
        for walk in os.walk(self.tmp_path_full):
            walk_dir = walk[0]
            walk_dir_files = walk[2]
            subfolder = walk_dir.lstrip(self.tmp_path_full)
            for walk_file in walk_dir_files:
                walk_file_path = os.path.join(walk_dir, walk_file)
                if self.is_handled(walk_file):
                    SoundFileFactoryClass = soundfile_factory(walk_file)
                    soundfile = SoundFileFactoryClass(walk_file_path)
                    if self.lastfm_apikey:
                        soundfile.lastfm_apikey = self.lastfm_apikey
                        soundfile.parse_lastfm_data()
                    soundfile.persist()
                    self.files_process[walk_file] = soundfile
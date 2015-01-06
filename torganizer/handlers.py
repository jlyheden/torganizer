__author__ = 'johan'

import os
import shutil
import logging
from torganizer.actions import action_factory
from torganizer.files import soundfile_factory, SeriesFile
from torganizer.utils import walk_directory
logger = logging.getLogger(__name__)


class BaseHandler(object):
    """
    Use this class for constructing actual media type handlers
    """

    # override in child class
    file_types = []
    file_types_ignore = []
    archive_file_types = ['.zip', '.rar']

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.dst_path_full = None
        self.tmp_path_full = os.path.join(self.tmp_path, os.path.basename(self.src_path))
        self.files_action = {}
        self.files_process = {}
        self.failed_files = []

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
        for f in self.failed_files:
            sub_dir = os.path.basename(os.path.dirname(f))
            unsort_dir = os.path.join(self.unsorted_path, sub_dir)
            if not os.path.exists(unsort_dir):
                os.makedirs(unsort_dir)
            shutil.copy(f, unsort_dir)
            logger.warning("Copied failed file '%s' to unsorted directory '%s'" % (f, unsort_dir))

    def cleanup(self):
        logger.info("Purging tmp directory '%s'" % self.tmp_path_full)
        shutil.rmtree(self.tmp_path_full)

    def execute(self):
        self.analyze_files()
        self.copy_to_tmp()
        self.post_process_tmp()
        self.copy_to_dst()
        self.post_process_dst()
        self.cleanup()

    def is_copied(self, f):
        return os.path.splitext(f)[1] not in self.file_types_ignore

    def is_handled(self, f):
        return os.path.splitext(f)[1].lower() in self.file_types


class MusicHandler(BaseHandler):

    file_types = ['.mp3']
    file_types_ignore = ['.nfo', '.cue', '.log', '.m3u']

    def analyze_files(self):
        for f in walk_directory(self.src_path):
            subfolder = os.path.dirname(f)[len(self.src_path):].lstrip(os.sep)
            if self.is_copied(f):
                dst_path = os.path.join(self.tmp_path_full, subfolder)
                ActionFactoryClass = action_factory(f)
                self.files_action[f] = ActionFactoryClass(src=f, dst=dst_path)

    def post_process_tmp(self):
        for f in walk_directory(self.tmp_path_full):
            if self.is_handled(f):
                SoundFileFactoryClass = soundfile_factory(f)
                soundfile = SoundFileFactoryClass(f)
                if self.lastfm_apikey:
                    soundfile.lastfm_apikey = self.lastfm_apikey
                    soundfile.parse_lastfm_data()
                soundfile.persist()
                self.files_process[f] = soundfile


class SeriesHandler(BaseHandler):

    file_types = ['.mkv', '.avi', '.wmv', '.divx', '.idx', '.sub', '.srt']
    file_types_ignore = ['.nfo', '.sfv']
    dir_ignore = ['sample']

    def analyze_files(self):
        for f in walk_directory(self.src_path, ignore_dirs=self.dir_ignore, ignore_dirs_case_insensitive=True):
            if self.is_copied(f):
                Action = action_factory(f)
                self.files_action[f] = Action(src=f, dst=self.tmp_path_full)

    def post_process_tmp(self):
        # walk tmp path, could be more archives to extract
        for f in walk_directory(self.tmp_path_full):
            if os.path.splitext(f)[1] in self.archive_file_types:
                logger.debug("Found archive '%s' in tmp folder" % f)
                Action = action_factory(f)
                a = Action(src=f, dst=self.tmp_path_full)
                a.do()

        # then walk again to process the final files
        for f in walk_directory(self.tmp_path_full):
            if self.is_handled(f):
                try:
                    seriesfile = SeriesFile(f)
                except Exception, ex:
                    logger.error("Failed to parse file '%s' for metadata. Exception was: %s" %
                                 (f, str(ex)))
                    self.failed_files.append(f)
                else:
                    seriesfile.persist()
                    self.files_process[f] = seriesfile

__author__ = 'johan'

import os
import shutil
import logging
import subprocess

logger = logging.getLogger(__name__)
PATH = os.environ['PATH']


class BaseAction(object):
    pass


class CopyAction(BaseAction):

    @staticmethod
    def do(src_path, dst_path):
        logger.debug("Copying file %s to %s" % (src_path, dst_path))
        shutil.copy(src_path, dst_path)


class DummyCopyAction(BaseAction):

    @staticmethod
    def do(src_path, dst_path):
        logger.debug("Dummy logger for file %s" % src_path)


class UnrarAction(BaseAction):

    def __init__(self):
        s = subprocess.Popen([
            'unrar',
            '--help'
        ], stdout=subprocess.PIPE)
        s.communicate()
        if s.returncode != 0:
            raise Exception("Executable 'unrar' not installed in path %s" % PATH)

    @staticmethod
    def do(src_path, dst_path):
        cmd = [
            'unrar',
            '-x',
            src_path,
            dst_path
        ]
        logger.debug("Extracting file %s to %s, command: '%s'" % (src_path, dst_path, " ".join(cmd)))
        s = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        r = s.communicate()
        if s.returncode != 0:
            raise Exception("Failed to extract file %s. Output from command: %s" % (src_path, r[1]))


class UnzipAction(BaseAction):
    pass
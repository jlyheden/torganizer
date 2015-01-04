__author__ = 'johan'

import re
import os
import shutil
import logging
import subprocess

logger = logging.getLogger(__name__)
PATH = os.environ['PATH']


def action_factory(f):
    ext = os.path.splitext(f)[1].lower()
    if ext == '.rar':
        return UnrarAction
    elif re.match(r"\.r[0-9]{2}", ext):
        return DummyCopyAction
    elif ext == '.zip':
        return UnzipAction
    else:
        return CopyAction


class BaseAction(object):

    @staticmethod
    def run_cmd(cmd, *args):
        p_list = [cmd] + list(args)
        logger.debug("Executing command: '%s'" % " ".join(p_list))
        p = subprocess.Popen(p_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = p.communicate()
        if p.returncode != 0:
            raise Exception("Failed to execute command '%s' in path: %s. Output from command: %s" % (" ".join(p_list),
                                                                                                     PATH, output[1]))


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
        self.run_cmd('unrar', '--help')

    def do(self, src_path, dst_path):
        self.run_cmd('unrar', '-x', src_path, dst_path)


class UnzipAction(BaseAction):

    def __init__(self):
        self.run_cmd('unzip', '-h')

    def do(self, src_path, dst_path):
        self.run_cmd('unzip', src_path, '-d', dst_path)
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

    def __init__(self, src, dst):
        self.src = src
        self.dst = dst

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

    def do(self):
        logger.debug("Copying file %s to %s" % (self.src, self.dst))
        if not os.path.exists(self.dst):
            logger.info("Destination path %s does not exist. Creating it" % self.dst)
            os.makedirs(self.dst)
        shutil.copy(self.src, self.dst)


class DummyCopyAction(BaseAction):

    def do(self):
        logger.debug("Dummy logger for file %s" % self.src)


class UnrarAction(BaseAction):

    def __init__(self, src, dst):
        super(UnrarAction, self).__init__(src, dst)
        self.run_cmd('unrar', '--help')

    def do(self):
        self.run_cmd('unrar', '-x', self.src, self.dst)


class UnzipAction(BaseAction):

    def __init__(self, src, dst):
        super(UnzipAction, self).__init__(src, dst)
        self.run_cmd('unzip', '-h')

    def do(self):
        self.run_cmd('unzip', self.src, '-d', self.dst)
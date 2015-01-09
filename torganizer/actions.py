# -*- coding: UTF-8 -*-
__author__ = 'johan'

import re
import os
import shutil
import logging
import subprocess

logger = logging.getLogger(__name__)
PATH = os.environ['PATH']


def action_factory(f):
    name, ext = os.path.splitext(f)
    ext = ext.lower()
    if ext == '.rar':
        if name.endswith('part1') or name.endswith('part01') or name.endswith('part001'):
            return UnrarAction
        if re.search(r"part[0-9]+$", name):
            return DummyCopyAction
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
        logger.debug("Executing command: '%s'" % " ".join(p_list).decode('utf-8'))
        p = subprocess.Popen(p_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = p.communicate()
        return p.returncode, output[0], output[1]


class CopyAction(BaseAction):

    def do(self):
        logger.debug("Copying file %s to %s" % (self.src.decode('utf-8'), self.dst.decode('utf-8')))
        if not os.path.exists(self.dst):
            logger.info("Destination path %s does not exist. Creating it" % self.dst.decode('utf-8'))
            os.makedirs(self.dst)
        shutil.copy(self.src, self.dst)


class DummyCopyAction(BaseAction):

    def do(self):
        logger.debug("Ignoring file %s" % self.src.decode('utf-8'))


class UnrarAction(BaseAction):

    def __init__(self, src, dst):
        super(UnrarAction, self).__init__(src, dst)
        returncode, stdout, stderr = self.run_cmd('unrar', '--help')
        if returncode == 127:
            raise Exception("Could not find unrar executable in path: %s" % PATH)
        logger.debug("Found unrar executable")

    def do(self):
        logger.debug("Extracting file '%s' to '%s'" % (self.src.decode('utf-8'), self.dst.decode('utf-8')))
        returncode, stdout, stderr = self.run_cmd('unrar', 'x', self.src.decode('utf-8'), self.dst.decode('utf-8'))
        if returncode != 0:
            raise Exception("Failed to extract file %s. Output from unzip: %s" % (self.src, stderr))


class UnzipAction(BaseAction):

    def __init__(self, src, dst):
        super(UnzipAction, self).__init__(src, dst)
        returncode, stdout, stderr = self.run_cmd('unzip')
        if returncode == 127:
            raise Exception("Could not find unzip executable in path: %s" % PATH)
        logger.debug("Found unzip executable")

    def do(self):
        logger.debug("Extracting file '%s' to '%s'" % (self.src.decode('utf-8'), self.dst.decode('utf-8')))
        returncode, stdout, stderr = self.run_cmd('unzip', self.src, '-d', self.dst)
        if returncode != 0:
            raise Exception("Failed to extract file %s. Output from unzip: %s" % (self.src, stderr))
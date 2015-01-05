__author__ = 'johan'

import yaml
import os


def get_config(f):
    return yaml.load(file(f, 'r'))


def setup(config, path):
    dirname = os.path.dirname(path)
    module = __import__('torganizer.handlers')
    for handler in config['handlers'].values():
        if handler['src'] == dirname:
            klass = getattr(module, handler['handler'])
            return klass(handler['src'], handler['dst'], config['tmp_path'])
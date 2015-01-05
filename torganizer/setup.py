__author__ = 'johan'

import logging
import yaml
import os


def get_config(f):
    return yaml.load(file(f, 'r'))


def setup_logging(config):
    levels = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'error': logging.ERROR
    }
    logging.basicConfig(level=levels[config['loglevel']])


def setup(config, path):
    from torganizer.handlers import MusicHandler
    handlers = {
        'MusicHandler': MusicHandler
    }
    dirname = os.path.dirname(path)
    for handler in config['handlers'].values():
        if handler['src'] == dirname:
            klass = handlers[handler['handler']]
            return klass(path, handler['dst'], config['tmp_path'])
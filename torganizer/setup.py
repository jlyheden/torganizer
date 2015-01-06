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
    from torganizer.handlers import MusicHandler, SeriesHandler
    handlers = {
        'MusicHandler': MusicHandler,
        'SeriesHandler': SeriesHandler
    }
    for handler in config['handlers'].values():
        if path.startswith(handler['scan_path']):
            klass = handlers[handler['handler']]
            return klass(src_path=path, **handler)
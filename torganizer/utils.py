# -*- coding: UTF-8 -*-
__author__ = 'johan'

from urllib import urlencode
import urllib2
import xml.etree.ElementTree as ET
import logging
import os

logger = logging.getLogger(__name__)

SQUASH_MAP = {
    u"å": "a",
    u"ä": "a",
    u"ö": "o",
    u"û": "ue",
    u"é": "e",
    u"ó": "o",
    u"ü": "u"
}


def unicode_squash(s):
    """
    Squashes special characters

    :param s: string to squash
    :type s: unicode
    :return: squashed string
    :rtype: str
    """
    rs = s
    for k, v in SQUASH_MAP.items():
        rs = rs.replace(k, v)
    return str(rs)


def sanitize_string(s, title=False, strip_dots=False):
    """
    Replace underscore with whitespace
    Optionally titles the string

    :param s: string to sanitize
    :param title: if string should be titled
    :type s: str
    :type title: bool
    :return: sanitized string
    :rtype: str
    """
    rs = s.replace("/", "-")
    if strip_dots:
        rs = rs.replace(".", " ")
    rs = rs.replace("_", " ").lstrip().rstrip()
    if title:
        return rs.title()
    else:
        return rs


def occurrence_in_string(c, s):
    """
    Return number of occurrences of character in string

    :param c: character to search for
    :param s: string to search
    :type c: str
    :type s: str
    :return: number of matches
    :rtype: int
    """
    return len([x for x in s if x == c])


def lastfm_apicall(api_key, **kwargs):
    """

    :param api_key: lastfm api key
    :param kwargs: key/value query params
    :type api_key: str
    :type kwargs: dict
    :return: xml response
    :rtype: xml.etree.ElementTree
    """
    params = kwargs.copy()
    params['api_key'] = api_key
    url = "http://ws.audioscrobbler.com/2.0/?%s" % urlencode(params)
    logger.debug("Preparing LastFM api call: '%s'" % url)
    request = urllib2.Request(url)
    request.add_header('Accept', 'application/xml')
    response = urllib2.urlopen(request)
    return ET.fromstring(response.read())


def walk_directory(path, ignore_dirs=[], ignore_dirs_case_insensitive=True):
    """
    Walks directory structure and returns a list of fully qualified filenames
    :param path: path to walk
    :param ignore_dirs: list of dirs to exclude from walk
    :param ignore_dirs_case_insensitive: if ignore should disregard casing differences
    :type path: str
    :type ignore_dirs: list
    :type ignore_dirs_case_insensitive: bool
    :return: list of files
    :rtype: list
    """
    def dirname(dd):
        if ignore_dirs_case_insensitive:
            return dd.lower()
        else:
            return dd
    rv = []
    if ignore_dirs_case_insensitive:
        ignore_dirs = [d.lower() for d in ignore_dirs]
    for walk in os.walk(path, topdown=True):
        walk[1][:] = [d for d in walk[1] if dirname(d) not in ignore_dirs]
        walk_dir = walk[0]
        walk_dir_files = walk[2]
        for walk_file in walk_dir_files:
            walk_file_path = os.path.join(walk_dir, walk_file)
            rv.append(walk_file_path)
    return rv
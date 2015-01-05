# -*- coding: UTF-8 -*-
__author__ = 'johan'

from urllib import urlencode
import urllib2
import xml.etree.ElementTree as ET
import logging

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


def sanitize_string(s, title=False):
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
    rs = s.replace("_", " ").lstrip().rstrip()
    rs = rs.replace("/", "-")
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

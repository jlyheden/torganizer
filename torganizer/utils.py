# -*- coding: UTF-8 -*-
__author__ = 'johan'

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

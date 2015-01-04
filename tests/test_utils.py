# -*- coding: UTF-8 -*-
__author__ = 'johan'

import unittest
from torganizer.utils import *


class TestTorganizerUtils(unittest.TestCase):

    def test_unicode_squash(self):
        self.assertEqual("lok", unicode_squash(u"lök"))
        self.assertEqual("Sigur Ros", unicode_squash(u"Sigur Rós"))
        self.assertEqual("Gunter", unicode_squash(u"Günter"))

    def test_sanitize_string(self):
        self.assertEqual("test string", sanitize_string("_test_string_"))
        self.assertEqual("Test String", sanitize_string("_test_string_", title=True))
        self.assertEqual("Test String", sanitize_string("___TEST_STRING_", title=True))
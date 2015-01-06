__author__ = 'johan'

import unittest
from torganizer.actions import *


class TestTorganizerActionFactory(unittest.TestCase):

    def test_actionfactory(self):
        self.assertEqual(UnrarAction, action_factory("/path/filename.part1.rar"))
        self.assertEqual(DummyCopyAction, action_factory("/path/filename.part11.rar"))
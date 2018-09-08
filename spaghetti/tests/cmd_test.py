from unittest import TestCase

import spaghetti.command_line as cmd
from spaghetti.mapper import Search


class TestCmd(TestCase):
    def test_search_started(self):
        output = cmd.main("Test")
        self.assertTrue(isinstance(output, Search))

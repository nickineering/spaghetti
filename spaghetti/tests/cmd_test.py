from unittest import TestCase
import unittest

import spaghetti.command_line as cmd
from spaghetti.search import Search


class TestCmd(TestCase):
    def test_search_started(self):
        output = cmd.main("Test")
        self.assertTrue(isinstance(output, Search))


if __name__ == '__main__':
    # begin the unittest.main()
    unittest.main()

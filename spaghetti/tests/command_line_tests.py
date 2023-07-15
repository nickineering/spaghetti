from unittest import TestCase
import unittest
import io
import sys

import spaghetti.command_line as cmd
from spaghetti.state import Mode


class CommandLineTest(TestCase):
    name = "Test"

    def setUp(self):
        pass

    def test_prints_output(self):
        self.capturedOutput = io.StringIO()  # Create StringIO object
        sys.stdout = self.capturedOutput  # and redirect stdout.
        cmd.main(self.name)  # Call function.
        sys.stdout = sys.__stdout__  # Reset redirect.
        self.assertIsNotNone(self.capturedOutput.getvalue())

    def test_filename_in_args(self):
        args = cmd.get_input(self.name)
        self.assertEqual(args.filename[0], self.name)

    def test_default_mode_is_normal(self):
        args = cmd.get_input(self.name)
        self.assertEqual(args.mode, Mode.NORMAL)


if __name__ == "__main__":
    # begin the unittest.main()
    unittest.main()

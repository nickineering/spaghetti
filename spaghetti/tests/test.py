from unittest import TestCase
import unittest

import spaghetti.command_line as cmd
from spaghetti.search import Search
from spaghetti.func_node import FuncNode


class Testing(TestCase):
    name = "Test"

    def setUp(self):
        self.output = cmd.main(self.name)
        self.node = FuncNode(name=self.name)
        self.node_equal = FuncNode(name=self.name)
        self.node2 = FuncNode(name=self.name+"2")
        self.node.add_edge(self.node2)
        self.node2.add_edge(self.node, dependency=True)

    def test_search_started(self):
        self.assertTrue(isinstance(self.output, Search))

    def test_node_repr(self):
        self.assertIn(self.name, repr(self.node))

    def test_edge_added(self):
        self.assertIn(self.node, self.node2.get_edges(dependency=True))

    def test_edge_in_edges_str(self):
        self.assertIn(self.name, self.node2.get_edges_str(dependency=True))

    def test_node_equal(self):
        self.assertEqual(self.node, self.node_equal)


if __name__ == '__main__':
    # begin the unittest.main()
    unittest.main()

import unittest
from unittest import TestCase

import networkx

from spaghetti.measurements import Measurements


class CommandLineTest(TestCase):
    name = "Test"

    def setUp(self):
        graph = networkx.DiGraph()
        graph.add_node((0, 1))
        graph.add_node((0, 2))

        self.measure = Measurements(graph)

    def test_positive_max_degree(self):
        self.assertGreaterEqual(self.measure.max_degree, 0)

    def test_positive_node_number(self):
        self.assertGreaterEqual(self.measure.node_num, 0)

    def test_positive_mean_degree(self):
        self.assertGreaterEqual(self.measure.mean_degree, 0)

    def test_positive_connectivity(self):
        self.assertGreaterEqual(self.measure.node_connectivity, 0)


if __name__ == "__main__":
    # begin the unittest.main()
    unittest.main()

import networkx
import statistics


class Measurements:

    def __init__(self, nxg):
        self.nxg = nxg
        degree_sequence = sorted([d for n, d in self.nxg.degree()], reverse=True)
        # all_pairs_con = networkx.algorithms.approximation.connectivity.all_pairs_node_connectivity(self.nxg)
        all_pairs_con = networkx.algorithms.connectivity.connectivity.all_pairs_node_connectivity(
            self.nxg.to_undirected())

        self.node_connectivity = networkx.algorithms.connectivity.connectivity.node_connectivity(
            self.nxg.to_undirected())
        self.max_degree = max(degree_sequence)
        self.mean_degree = statistics.mean(degree_sequence)
        self.node_num = self.nxg.number_of_nodes()
        self.num_connected_nodes = 0
        self.potential_pairs = 0
        for node in all_pairs_con:
            for pair in all_pairs_con[node]:
                self.potential_pairs += 1
                if all_pairs_con[node][pair] > 0:
                    self.num_connected_nodes += 1

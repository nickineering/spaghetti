import ast
import os
import networkx
import statistics
import matplotlib.pyplot as plt
import time
from spaghetti.ast_parser import EdgeDetector, NodeCreator


class Search:

    def __init__(self, args):
        self.args = args
        self.tree = {}
        self.creator = {}
        self.files = []
        self.graph = {}
        self.nxg = None
        self.searched_files = set()
        self.searched_directories = set()
        self.crawled_imports = set()
        self.uncrawled = set()
        self.unsure_nodes = set()

        self.crawl_files()
        self.process_files()
        self.output_text()
        if self.args.draw is True:
            self.draw_graph()

    def crawl_files(self):
        for filename in self.args.filename:
            filename = os.path.abspath(os.path.expanduser(filename))
            if os.path.isdir(filename):
                self.searched_directories.add(filename + os.sep)
                for file in os.walk(filename, followlinks=True):
                    for i in range(len(file[2])):
                        found_filename = file[0] + os.sep + file[2][i]
                        if found_filename[-3:] == ".py":
                            self.append_graph(found_filename)
            else:
                # Adds ".py" to the end of the file if that was not specified.
                if filename[-3:] != ".py":
                    filename += ".py"
                if os.path.isfile(filename):
                    self.searched_files.add(filename)
                    self.append_graph(filename)
                else:
                    print("Error: Could not find %s" % filename)

    # Adds to the existing graph object.
    def append_graph(self, file):
        self.tree[file] = ast.parse(open(file).read())
        # print(ast.dump(self.tree[file]))
        creator = NodeCreator(search=self, filename=file)
        creator.visit(self.tree[file])
        self.files.append(file)

    def process_files(self):
        # Processes each file.
        for file in self.files:
            logger = EdgeDetector(search=self, filename=file)
            logger.visit(self.tree[file])
        self.nxg = self.get_nx_graph()

    # Prints the results including a list of functions and their dependencies in the terminal.
    def output_text(self):
        indent = ""

        if self.args.raw is not True:
            searched_str = " ".join(self.searched_files) + " ".join(self.searched_directories)

            if searched_str != "":

                if len(self.crawled_imports) is not 0:
                    imports_str = ", ".join(sorted(self.crawled_imports))
                    print("Also crawled these imports: %s" % imports_str)

                if len(self.uncrawled) is not 0:
                    uncrawled_str = ", ".join(sorted(self.uncrawled))
                    print("Failed to crawl these imports: %s" % uncrawled_str)

                if len(self.unsure_nodes) is not 0:
                    unsure_str = ", ".join(sorted(self.unsure_nodes))
                    print("Could not include the following functions: %s" % unsure_str)

                if self.args.measurements is True:
                    print()
                    self.print_measurements()

                if self.args.inverse is True:
                    dependents_string = "Dependencies"
                else:
                    dependents_string = "Dependents"
                indent = "-40"
                title_str = "\n%" + indent + "s %" + indent + "s\n"
                print(title_str % ("Function Name", dependents_string))

        # Prints each line of the data.
        format_string = "%" + indent + "s %" + indent + "s"
        for node in sorted(self.graph, key=lambda the_node: the_node.get_string()):
            if node.is_hidden() is False:
                print(format_string % (node, node.get_edges_str(inverse=self.args.inverse)))

    # Gets a networkx representation of the graph. Does not include secondary nodes so the measurement is more precise.
    def get_nx_graph(self):
        nxg = networkx.DiGraph()
        for node in self.graph:
            if node.is_secondary() is False:
                nxg.add_node(node)
        for node in self.graph:
            if node.is_secondary() is False:
                for edge in node.get_edges():
                    if edge.is_secondary() is False:
                        if self.args.inverse is False:
                            nxg.add_edge(node, edge)
                        else:
                            nxg.add_edge(edge, node)
        return nxg

    def draw_graph(self):
        if self.args.simple is False:
            title = " ".join(self.args.filename)
            plt.title(title)
            node_size = 75
            width = 2
            font_size = 10
        else:
            node_size = 400
            width = 4
            font_size = 20

        # pos = networkx.spectral_layout(self.nxg)  # positions for all nodes
        pos = networkx.spring_layout(self.nxg, k=3)
        networkx.draw_networkx_nodes(self.nxg, pos, node_size=node_size)
        networkx.draw_networkx_edges(self.nxg, pos, edge_color='blue', arrowsize=40, width=width)
        description = networkx.draw_networkx_labels(self.nxg, pos, font_size=font_size, font_family='sans-serif',
                                                    font_weight='bold')
        for node, t in description.items():
            t.set_clip_on(False)

        directory = "dependency_graphs"
        filename = "graph_" + repr(time.time()) + ".png"
        plt.axis('off')

        if not os.path.isdir(directory):
            os.mkdir(directory)
        plt.savefig(directory + os.sep + filename)

    def print_experimental_measurements(self):
        maximal_independent_set = networkx.algorithms.mis.maximal_independent_set(self.nxg.to_undirected())
        degree_centrality = networkx.algorithms.centrality.degree_centrality(self.nxg)
        edge_load_centrality = networkx.algorithms.centrality.edge_load_centrality(self.nxg)
        global_reaching_centrality = networkx.algorithms.centrality.global_reaching_centrality(self.nxg)
        # Very slow
        average_connectivity = networkx.algorithms.connectivity.connectivity.average_node_connectivity(self.nxg)

        print('Maximal independent set: ' + repr(maximal_independent_set))
        print('Degree Centrality: ' + repr(degree_centrality))
        print('Edge Load Centrality: ' + repr(edge_load_centrality))
        print('Global reaching centrality: ' + repr(global_reaching_centrality))
        print('Average Connectivity: {0:.2f}'.format(average_connectivity))

        is_connected = networkx.is_connected(self.nxg.to_undirected())
        degree_histogram = networkx.classes.function.degree_histogram(self.nxg)
        density = networkx.classes.function.density(self.nxg)
        edge_connectivity = networkx.algorithms.connectivity.connectivity.edge_connectivity(self.nxg.to_undirected())

        print('Degree Histogram: ' + repr(degree_histogram))
        print('Density: ' + repr(density))
        print('Is connected: ' + repr(is_connected))
        print('Edge Connectivity: {0:.2f}'.format(edge_connectivity))
        if is_connected:
            minimum_edge_cut = networkx.algorithms.connectivity.cuts.minimum_edge_cut(self.nxg)
            print('Minimum edge cut: ' + repr(minimum_edge_cut))

    def print_measurements(self):
        degree_sequence = sorted([d for n, d in self.nxg.degree()], reverse=True)
        node_connectivity = networkx.algorithms.connectivity.connectivity.node_connectivity(self.nxg.to_undirected())
        max_degree = max(degree_sequence)
        mean_degree = statistics.mean(degree_sequence)
        # all_pairs_con = networkx.algorithms.approximation.connectivity.all_pairs_node_connectivity(self.nxg)
        all_pairs_con = networkx.algorithms.connectivity.connectivity.all_pairs_node_connectivity(
            self.nxg.to_undirected())
        node_num = self.nxg.number_of_nodes()
        num_connected_nodes = 0
        potential_pairs = 0
        for node in all_pairs_con:
            for pair in all_pairs_con[node]:
                potential_pairs += 1
                if all_pairs_con[node][pair] > 0:
                    num_connected_nodes += 1
        # print("Number of one-way node connections: " + repr(num_connected_nodes))
        # print("Potential one-way node connections: " + repr(potential_pairs))
        print('The average number of dependents and dependencies per function: {0:.2f}'.format(mean_degree))
        print('The maximum number of dependents and dependencies per function: ' + repr(max_degree))
        if node_connectivity == 0:
            print('There are isolated functions or groups of isolated functions. Severity: {0:.2f}%'.format(
                100 - 100 * (num_connected_nodes / potential_pairs)))
        else:
            print('There are no isolated functions or groups of isolated functions. At least {:d} function(s) that '
                  'would need to be removed to isolate at least 1 function.'.format(node_connectivity))
        print('Total functions found in the search area: ' + repr(node_num))

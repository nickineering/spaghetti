import ast
import os
import networkx
from ast_parser import EdgeDetector, NodeCreator
from state import Mode


class Search:

    def __init__(self, filename, inverse=False, builtins=False, mode=Mode.NORMAL):
        self.filename = filename
        self.inverse = inverse
        self.builtins = builtins
        self.mode = mode
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
        self.create_edges()

    def crawl_files(self):
        for filename in self.filename:
            filename = os.path.abspath(os.path.expanduser(filename))
            if os.path.isdir(filename):
                self.searched_directories.add(filename + os.sep)
                for file in os.walk(filename, followlinks=True):
                    for i in range(len(file[2])):
                        found_filename = file[0] + os.sep + file[2][i]
                        if found_filename[-3:] == ".py":
                            self.add_file_to_graph(found_filename)
            else:
                # Adds ".py" to the end of the file if that was not specified.
                if filename[-3:] != ".py":
                    filename += ".py"
                if os.path.isfile(filename):
                    self.searched_files.add(filename)
                    self.add_file_to_graph(filename)
                else:
                    print("Error: Could not find %s" % filename)

    # Adds to the existing graph object.
    def add_file_to_graph(self, file):
        self.tree[file] = ast.parse(open(file).read())
        # print(ast.dump(self.tree[file]))
        creator = NodeCreator(search=self, filename=file)
        creator.visit(self.tree[file])
        self.files.append(file)

    def create_edges(self):
        # Processes each file.
        for file in self.files:
            detector = EdgeDetector(search=self, filename=file)
            detector.visit(self.tree[file])

    def get_graph_str(self, indent=0):
        # Prints each line of the data.
        graph_str = ""
        format_string = "%" + indent + "s %" + indent + "s\n"
        for node in sorted(self.graph, key=lambda the_node: the_node.get_string()):
            if node.is_hidden() is False:
                graph_str += format_string % (node, node.get_edges_str(dependency=self.inverse))
        return graph_str

    # For extension purposes only
    def get_graph(self):
        return self.graph

    # Gets a networkx representation of the graph. Does not include secondary nodes so the measurement is more precise.
    def get_nx_graph(self):
        if self.nxg is not None:
            return self.nxg
        else:
            nxg = networkx.DiGraph()
            for node in self.graph:
                if node.is_secondary() is False:
                    nxg.add_node(node)
            for node in self.graph:
                if node.is_secondary() is False:
                    for edge in node.get_edges():
                        if edge.is_secondary() is False:
                            if self.inverse is False:
                                nxg.add_edge(node, edge)
                            else:
                                nxg.add_edge(edge, node)
            self.nxg = nxg
            return nxg

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

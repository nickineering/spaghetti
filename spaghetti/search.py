import ast
import os

import networkx

try:
    from spaghetti.ast_parser import EdgeDetector, NodeCreator
    from spaghetti.state import Mode
except ImportError:
    from ast_parser import EdgeDetector, NodeCreator
    from state import Mode


# Conducts a search of given filenames or directories. Produces a Networkx functional dependency graph and associated metadata.
class Search:
    def __init__(self, filenames, inverse=False, mode=Mode.NORMAL):
        self.filenames = filenames
        self.inverse = inverse
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

        # Begins main execution
        self.crawl_files()
        self.create_edges()

    # Finds the all Python files in the filenames list and calls create_nodes() to add them
    def crawl_files(self):
        for filename in self.filenames:
            filename = os.path.abspath(os.path.expanduser(filename))
            if os.path.isdir(filename):
                self.searched_directories.add(filename + os.sep)
                for file in os.walk(filename, followlinks=True):
                    for i in range(len(file[2])):
                        found_filename = file[0] + os.sep + file[2][i]
                        if found_filename[-3:] == ".py":
                            self.create_nodes(found_filename)
            else:
                # Adds ".py" to the end of the file if that was not specified.
                if filename[-3:] != ".py":
                    filename += ".py"
                if os.path.isfile(filename):
                    self.searched_files.add(filename)
                    self.create_nodes(filename)
                else:
                    print("Error: Could not find %s" % filename)

    # Creates nodes in the given file
    def create_nodes(self, file):
        self.tree[file] = ast.parse(open(file).read())
        creator = NodeCreator(search=self, filename=file)
        creator.visit(self.tree[file])
        self.files.append(file)

    # Creates all edges for the graph
    def create_edges(self):
        for file in self.files:
            detector = EdgeDetector(search=self, filename=file)
            detector.visit(self.tree[file])

    def get_graph(self):
        return self.graph

    # Gets a networkx representation of the graph. Does not include nodes that are not from the primary search area
    # so that the measurement is more precise.
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

    # Returns a textual representation of the graph
    def get_graph_str(self, indent=0):
        # Prints each line of the data.
        graph_str = ""
        format_string = "%" + indent + "s %" + indent + "s\n"
        for node in sorted(self.graph, key=lambda the_node: the_node.get_string()):
            if node.is_hidden() is False:
                graph_str += format_string % (
                    node,
                    node.get_edges_str(dependency=self.inverse),
                )
        return graph_str

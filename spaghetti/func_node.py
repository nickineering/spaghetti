import os
from spaghetti.state import Mode


# Represents function nodes in the graph.
class FuncNode:

    def __init__(self, filename="", class_name="", name="", depth=0, ast_node=None, mode=Mode.NORMAL):
        self._filename = filename
        self._class_name = class_name
        self._name = name
        self._depth = depth

        # All of the other nodes this node calls.
        self._dependencies = set()
        # All the other nodes that call this node.
        self._dependents = set()
        self._ast_node = ast_node
        self.mode = mode

    def __repr__(self):
        return self.get_filename() + self._class_name + "." + self._name

    def __eq__(self, other):
        return (
            self.__class__ == other.__class__ and
            self.get_string() == other.get_string()
        )

    # This prevents creating multiple nodes at the same position in the graph.
    def __hash__(self):
        return hash((self._filename, self._class_name, self._name))

    def get_filename(self):
        if self.mode is Mode.LONG:
            return self._filename.split(os.getcwd() + os.sep)[-1] + ":"
        elif self.mode is Mode.NORMAL:
            return self._filename.split(os.sep)[-1] + ":"
        else:
            return ""

    def get_class(self):
        return self._class_name

    def get_name(self):
        return self._name

    def add_edge(self, edge, dependency=False):
        if dependency is True:
            self._dependencies.add(edge)
        else:
            self._dependents.add(edge)

    def get_edges(self, dependency=False):
        if dependency is True:
            return self._dependencies
        else:
            return self._dependents

    def get_ast_node(self):
        return self._ast_node

    def get_string(self):
        return self._filename + self._class_name + self._name

    # Returns true if identifier might be used by the AST to identify the node.
    def is_identifier(self, identifier):
        if self._filename == identifier or self._class_name == identifier or self._name == identifier:
            return True
        else:
            return False

    def is_hidden(self):
        if self._depth > 0 and len(self._dependencies) == 0 and len(self._dependents) == 0:
            return True
        else:
            return False

    def is_secondary(self):
        if self._depth > 0:
            return True
        else:
            return False

    # Returns a string of all the edges.
    def get_edges_str(self, dependency=False):
        return_str = ""
        for edge in sorted(self.get_edges(dependency=dependency), key=lambda the_node: the_node.get_string()):
            return_str += "(" + repr(edge) + ") "
        return return_str

    def get_indegree(self):
        return len(self._dependents)

    def get_outdegree(self):
        return len(self._dependencies)

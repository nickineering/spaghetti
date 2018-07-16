import ast
import argparse
import os


# Represents function nodes in the graph.
class FuncNode:

    def __init__(self, filename="", class_name="", name=""):
        self._filename = filename
        self._class_name = class_name
        self._name = name

        # All of the other nodes this node calls.
        self._calls = set()
        # All the other nodes that call this node.
        self._called_by = set()

    def __repr__(self):
        return self._class_name + "." + self._name

    def __eq__(self, other):
        return (
            self.__class__ == other.__class__ and
            self._filename == other.get_filename() and
            self._class_name == other.get_class() and
            self._name == other.get_name()
        )

    # This prevents creating multiple nodes at the same position in the graph.
    def __hash__(self):
        return hash((self._filename, self._class_name, self._name))

    def get_filename(self):
        return self._filename

    def get_class(self):
        return self._class_name

    def get_name(self):
        return self._name

    def add_call(self, call):
        self._calls.add(call)

    def add_called_by(self, called_by):
        self._called_by.add(called_by)

    def get_calls(self):
        return self._calls

    def get_called_by(self):
        return self._called_by

    def get_calls_str(self, calls=False):
        if calls is True:
            edges = self._calls
        else:
            edges = self._called_by
        return_str = ""
        for call in edges:
            return_str += "(" + repr(call) + ")"
        return return_str


# The class that parses the AST.
class FuncLister(ast.NodeVisitor):
    current_class = ""
    current_function = ""
    graph = {}

    def __init__(self, filename="", built_ins=False):
        self.filename = filename
        self.allow_built_ins = built_ins

        # Removes file extension.
        self.current_filename = self.filename[:-3]
        # Removes directory for simplicity. Should be included in future versions.
        self.current_filename = self.current_filename.split(os.sep)[-1]

    def visit_ClassDef(self, node):
        self.current_class = node.name
        self.generic_visit(node)

    # Creates a node for the function even though it might not be connected to any other nodes.
    def visit_FunctionDef(self, node):
        self.current_function = node.name
        current_node = FuncNode(filename=self.current_filename, class_name=self.current_class,
                                name=self.current_function)
        self.add_node(current_node)
        self.generic_visit(node)

    # Records actual function calls
    def visit_Call(self, node):

        # Begin makeshift area. There should be a more efficient way to do this, but basically it is trying to determine
        # enough information about the node being called to generate that node's hash so the two can be linked.
        class_name = ""
        try:
            call = node.func.id
        except AttributeError:
            try:
                call = node.func.attr
                class_name = node.func.value.id
            except AttributeError:
                call = node.func.value.id
        try:
            call_file = node.func.value.id
        except AttributeError:
            call_file = self.current_filename

        if class_name == "self":
            class_name = self.current_class
            call_file = self.current_filename
        if class_name == call_file:
            class_name = ""

        # End makeshift area.

        # Checks if the current call is to a built-in function.
        is_built_in = False
        if call in dir(__builtins__):
            is_built_in = True
            call_file = ''

        if is_built_in is False or self.allow_built_ins is True:
            this_node = FuncNode(filename=self.current_filename, class_name=self.current_class, name=self.current_function)
            self.add_node(this_node)
            called_node = FuncNode(filename=call_file, class_name=class_name, name=call)
            self.add_node(called_node)

            # This works even if the node was not added to the graph because the existing node's hash would be the same.
            self.graph[this_node].add_call(called_node)
            self.graph[called_node].add_called_by(this_node)

            # print(repr(self.graph[this_node]) + " " + self.graph[this_node].get_calls_str())
            # print(ast.dump(node))
            # print()

        self.generic_visit(node)

    # Returns the graph this instance created.
    def get_graph(self):
        return self.graph

    # Adds the given node to the graph if it is not already in it.
    def add_node(self, node):
        if node not in self.graph:
            self.graph[node] = node


# Main initial execution of the script via the command-line.
def main():
    # Configures the command-line interface.
    parser = argparse.ArgumentParser(description='Graph interfunctional Python dependencies.')
    parser.add_argument('--filename', '-f', metavar='F', type=str, nargs=1,
                        help="Specify the name of the file to be examined.")
    parser.add_argument('--built-ins', '-b', action='store_true',
                        help="Also graph when Python's built in functions are used.")
    parser.add_argument('--debug', '-d', dest='debug', action='store_true', default=False,
                        help="Enable debugging output.")
    args = parser.parse_args()

    # Processes the input parameters.
    DEBUG = args.debug
    if args.filename:
        filename = args.filename[0]
    else:
        filename = input("Filename to examine: ")

    # Adds ".py" to the end of the file if that was not specified.
    if filename[-3:] != ".py":
        filename += ".py"

    # Creates the AST in the "tree" variable and then uses the FuncLister class to parse it.
    tree = ast.parse(open(filename).read())
    lister = FuncLister(filename, args.built_ins)
    lister.visit(tree)

    # Outputs the graph parsed from the AST in string form.
    output_graph = lister.get_graph()
    for node in output_graph:
        print(repr(node) + " " + repr(node.get_calls_str()))

    pass


# Calls the main function to start the script.
if __name__ == "__main__":
    main()

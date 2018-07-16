import ast
import argparse
import os


# Represents function nodes in the graph.
class FuncNode:

    def __init__(self, filename="", class_name="", name="", ast_node=None):
        self._filename = filename
        self._class_name = class_name
        self._name = name

        # All of the other nodes this node calls.
        self._calls = set()
        # All the other nodes that call this node.
        self._called_by = set()
        self._ast_node = ast_node

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

    def get_ast_node(self):
        return self._ast_node


# Parent class for basic AST parsing. Meant to be extended depending on the task.
class ASTParser(ast.NodeVisitor):
    current_class = ""
    current_function = ""
    graph = {}

    def __init__(self, filename="", graph=None, built_ins=False):
        self.filename = filename
        self.allow_built_ins = built_ins

        # Removes file extension.
        self.current_filename = self.filename[:-3]
        # Removes directory for simplicity. Should be included in future versions.
        self.current_filename = self.current_filename.split(os.sep)[-1]

        if graph is not None:
            self.graph = graph

    def visit_ClassDef(self, node):
        self.current_class = node.name
        self.generic_visit(node)

    # Creates a node for the function even though it might not be connected to any other nodes.
    def visit_FunctionDef(self, node):
        self.current_function = node.name
        self.generic_visit(node)

    # Returns the graph this instance created.
    def get_graph(self):
        return self.graph

    # Adds the given node to the graph if it is not already in it.
    def add_node(self, node):
        if node not in self.graph:
            self.graph[node] = node


# Searches AST for nodes and adds them to the graph.
class NodeCreator(ASTParser):

    # Creates a node for the function even though it might not be connected to any other nodes.
    def visit_FunctionDef(self, node):
        self.current_function = node.name
        current_node = FuncNode(filename=self.current_filename, class_name=self.current_class,
                                name=self.current_function, ast_node=node)
        self.add_node(current_node)
        self.generic_visit(node)


# Detects connections in the AST and adds them as edges in the graph.
class EdgeDetector(ASTParser):

    # Records actual function calls
    def visit_Call(self, node):

        # There should be a more efficient way to do this, but basically it is trying to determine enough information
        # about the node being called to generate that node's hash so the two can be linked.
        try:
            call = node.func.id
        except AttributeError:
            try:
                call = node.func.attr
                # class_name = node.func.value.id
            except AttributeError:
                call = node.func.value.id

        # Checks if the current call is to a built-in function.
        is_built_in = False
        if call in dir(__builtins__):
            is_built_in = True
        if is_built_in is False or self.allow_built_ins is True:
            called_node = None
            already_found = False
            for n in self.graph:
                # Searches the graph for a node that resembles the called node. Might not work if multiple nodes are
                # named the same or if the node is not in the graph.
                if n.get_name() == call:
                    called_node = n
                    if already_found is True:
                        print("Mapper could not definitively determine the instance of " + call + " that was called by " +
                              self.current_function)
                    already_found = True

                if n.get_ast_node() == node:
                    this_node = n

            # This ideally would never be called. It only exists because the author is presently unaware of a
            # definitive way to determine the identity of a function called in an AST node.
            if called_node is None:
                if is_built_in is True:
                    class_name = "Builtins"
                    call_file = "System"
                else:
                    class_name = "Unknown"
                    call_file = "Unknown"
                called_node = FuncNode(filename=call_file, class_name=class_name, name=call)

            # Creates this node if it was not already in the graph.
            try:
                this_node
            except NameError:
                this_node = FuncNode(filename=self.current_filename, class_name=self.current_class, name=self.current_function)

            # Ensures that the relevant nodes are in the graph if they were not already.
            self.add_node(this_node)
            self.add_node(called_node)

            # This works even if the node was not added to the graph because the existing node's hash would be the same.
            self.graph[this_node].add_call(called_node)
            self.graph[called_node].add_called_by(this_node)

            # print(repr(self.graph[this_node]) + " " + self.graph[this_node].get_calls_str())
            # print(ast.dump(node))
            # print()

        self.generic_visit(node)


# Main initial execution of the script via the command-line.
def main():
    # Configures the command-line interface.
    parser = argparse.ArgumentParser(description='Graph interfunctional Python dependencies. For all functions searched'
                                                 '(listed far left) the functions to the right depend on it.')
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
    creator = NodeCreator(filename)
    creator.visit(tree)
    graph = creator.get_graph()
    logger = EdgeDetector(filename, graph, args.built_ins)
    logger.visit(tree)

    # Outputs the graph parsed from the AST in string form.
    for node in graph:
        print(repr(node) + " " + repr(node.get_calls_str()))

    pass


# Calls the main function to start the script.
if __name__ == "__main__":
    main()

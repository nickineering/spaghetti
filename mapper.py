import ast
import argparse
import os

tree = {}
creator = {}
py_files = []
graph = {}
logger = {}
searched_files = []
searched_directories = []


# Represents function nodes in the graph.
class FuncNode:

    def __init__(self, filename="", class_name="", name="", ast_node=None):
        self._filename = filename
        self._class_name = class_name
        self._name = name

        # All of the other nodes this node calls.
        self._dependencies = set()
        # All the other nodes that call this node.
        self._dependents = set()
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

    def get_string(self):
        return self.get_filename() + self.get_class() + self.get_name()

    def get_filename(self):
        return self._filename

    def get_class(self):
        return self._class_name

    # Returns true if identifier might be used by the AST to identify the node.
    def is_identifier(self, identifier):
        if self._filename == identifier or self._class_name == identifier:
            return True
        else:
            return False

    def get_name(self):
        return self._name

    def add_dependency(self, dependency):
        self._dependencies.add(dependency)

    def get_dependencies(self):
        return self._dependencies

    def add_dependent(self, dependent):
        self._dependents.add(dependent)

    def get_dependents(self):
        return self._dependents

    # Returns a string of all the edges.
    def get_edges_str(self, inverse=False):
        if inverse is True:
            edges = self._dependencies
        else:
            edges = self._dependents
        return_str = ""
        for edge in sorted(edges, key=lambda the_node: the_node.get_string()):
            return_str += "(" + repr(edge) + ")"
        return return_str

    def get_ast_node(self):
        return self._ast_node


# Parent class for basic AST parsing. Meant to be extended depending on the task.
class ASTParser(ast.NodeVisitor):
    graph = {}

    def __init__(self, filename="", built_ins=False):
        self.current_class = ""
        self.current_function = ""
        self.filename = filename
        self.allow_built_ins = built_ins

        # Removes file extension.
        self.current_filename = self.filename[:-3]
        # Removes directory for simplicity. Should be included in future versions.
        self.current_filename = self.current_filename.split(os.sep)[-1]

    def visit_ClassDef(self, node):
        self.handle_node(node, "current_class", self.generic_visit)

    def visit_FunctionDef(self, node):
        self.handle_node(node, "current_function", self.generic_visit)

    def handle_node(self, node, title, handler):
        old_title = self.__dict__[title]
        self.__dict__[title] = node.name
        handler(node)
        self.__dict__[title] = old_title

    # Returns the graph this instance created.
    def get_graph(self):
        return self.graph

    # Adds the given node to the graph if it is not already in it.
    def add_node(self, node):
        if node not in self.graph:
            self.graph[node] = node


# Searches AST for nodes and adds them to the graph.
class NodeCreator(ASTParser):

    def visit_ClassDef(self, node):
        self.handle_node(node, "current_class", self.add_class_node)

    def add_class_node(self, node):
        current_node = FuncNode(filename=self.current_filename, class_name=self.current_class,
                                name="__init__")
        self.add_node(current_node)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.handle_node(node, "current_function", self.add_function_node)

    # Creates a node for the function even though it might not be connected to any other nodes.
    def add_function_node(self, node):
        current_node = FuncNode(filename=self.current_filename, class_name=self.current_class,
                                name=self.current_function, ast_node=node)
        self.add_node(current_node)
        self.generic_visit(node)


# Detects connections in the AST and adds them as edges in the graph.
class EdgeDetector(ASTParser):

    # Records actual function calls
    def visit_Call(self, node):
        # print(ast.dump(node))

        # Checks for information to reconstruct the fully qualified name of the node. Not enough data is in the AST
        # to always be able to find the right node.
        if "value" in dir(node.func):
            dependency = node.func.attr
            try:
                home = node.func.value.id
            except AttributeError:
                home = self.current_class
        else:
            dependency = node.func.id
            home = self.current_filename

        # Checks if the current call is to a built-in function.
        is_built_in = False
        if dependency in dir(__builtins__):  # sys.builtin_module_names
            is_built_in = True

        if is_built_in is False or self.allow_built_ins is True:
            dependency_node = None
            already_found = False
            # Searches the graph and selects the node being referenced.
            for n in self.graph:
                if n.get_name() == dependency:
                    if already_found is True:
                        # If there is a conflict and this is a more exact match save this.
                        if n.is_identifier(home) is True and dependency_node.is_identifier(home) is False:
                            dependency_node = n
                        # Do nothing if existing node is better.
                        if n.is_identifier(home) is False and dependency_node.is_identifier(home) is True:
                            pass
                        # If neither or both match throw an error. This should not happen normally.
                        else:
                            print("Mapper could not definitively determine the instance of " + dependency +
                                  " that was called by " + self.current_function)
                    else:
                        dependency_node = n
                    already_found = True

                if n.get_ast_node() == node:
                    this_node = n

            # Creates this node if it was not already in the graph.
            try:
                this_node
            except NameError:
                if self.current_function == "":
                    self.current_function = "__main__"

                this_node = FuncNode(filename=self.current_filename, class_name=self.current_class,
                                     name=self.current_function, ast_node=node)

            self.add_edge(is_built_in, dependency, this_node, dependency_node,)

        self.generic_visit(node)

    # Adds an edge to the graph.
    def add_edge(self, is_built_in, dependency, this_node, dependency_node=None,):
        # Error handling if the node's identity could not be determined.
        if dependency_node is None:
            if is_built_in is True:
                class_name = "Builtins"
                dependency_file = "System"
            else:
                class_name = "Unknown"
                dependency_file = "Unknown"
            dependency_node = FuncNode(filename=dependency_file, class_name=class_name, name=dependency)

        # Ensures that the relevant nodes are in the graph if they were not already.
        self.add_node(this_node)
        self.add_node(dependency_node)

        # This works even if the node was not added to the graph because the existing node's hash would be the same.
        self.graph[this_node].add_dependency(dependency_node)
        self.graph[dependency_node].add_dependent(this_node)


# Gets input data
def get_input():
    # Configures the command-line interface.
    parser = argparse.ArgumentParser(description='Graph interfunctional Python dependencies. Searches given modules '
                                                 'and/or directories and lists included functions along with their '
                                                 'dependents.')
    parser.add_argument('filename', metavar='F', type=str, nargs="*",
                        help="the name(s) of files and directories to examine")
    parser.add_argument('--inverse', '-i', action='store_true', default=False,
                        help="inverse output so that dependencies are listed instead of dependents")
    parser.add_argument('--built-ins', '-b', action='store_true',
                        help="also graph when Python's built in functions are used")
    parser.add_argument('--raw', '-r', action='store_true', default=False,
                        help="remove instruction text and formatting")
    args = parser.parse_args()

    # Processes the input parameters.
    if args.filename is None:
        args.filename[0] = input("Filename to examine: ")

    return args


# Adds to the existing graph object.
def append_graph(found_filename):
    tree[found_filename] = ast.parse(open(found_filename).read())
    creator[found_filename] = NodeCreator(found_filename)
    creator[found_filename].visit(tree[found_filename])
    py_files.append(found_filename)
    return {**graph, **creator[found_filename].get_graph()}


# Prints the results including a list of functions and their dependencies in the terminal.
def output_text(args):
    indent = ""
    if args.raw is not True:
        searched_str = ""
        if searched_files is not []:
            for file in searched_files:
                searched_str += file + " "
        if searched_directories is not []:
            for directory in searched_directories:
                searched_str += directory + " "

        if searched_str != "":
            print("Mapper searched: %s\n" % searched_str)
            if args.inverse is True:
                dependents_string = "Dependencies"
            else:
                dependents_string = "Dependents"
            indent = "-30"
            title_str = "%" + indent + "s %" + indent + "s\n"
            print(title_str % ("Function Name", dependents_string))

    # Prints each line of the data.
    for node in sorted(graph, key=lambda the_node: the_node.get_string()):
        format_string = "%" + indent + "s %" + indent + "s"
        print(format_string % (node, node.get_edges_str(inverse=args.inverse)))


# Main initial execution of the script via the command-line.
def main():
    global graph
    args = get_input()

    if args.filename is not None:
        for filename in args.filename:
            if os.path.isdir(filename):
                searched_directories.append(filename)
                for file in os.walk(filename, followlinks=True):
                    for i in range(len(file[2])):
                        found_filename = file[0] + os.sep + file[2][i]
                        if found_filename[-3:] == ".py":
                            graph = append_graph(found_filename)
            else:
                # Adds ".py" to the end of the file if that was not specified.
                if filename[-3:] != ".py":
                    filename += ".py"
                if os.path.isfile(filename):
                    searched_files.append(filename)
                    graph = append_graph(filename)
                else:
                    print("Error: File %s was not found" % filename)

    # Processes each file.
    for file in py_files:
        logger[file] = EdgeDetector(file, args.built_ins)
        logger[file].visit(tree[file])
        graph = {**graph, **logger[file].get_graph()}

    output_text(args)


# Calls the main function to start the script.
if __name__ == "__main__":
    main()

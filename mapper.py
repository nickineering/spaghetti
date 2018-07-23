import ast
import argparse
import os
import sys


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

    def get_filename(self):
        return self._filename

    def get_class(self):
        return self._class_name

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

    def get_edges_str(self, dependencies=False):
        if dependencies is True:
            edges = self._dependencies
        else:
            edges = self._dependents
        return_str = ""
        for edge in edges:
            return_str += "(" + repr(edge) + ")"
        return return_str

    def get_ast_node(self):
        return self._ast_node


# Parent class for basic AST parsing. Meant to be extended depending on the task.
class ASTParser(ast.NodeVisitor):
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

        if "value" in dir(node.func):
            dependency = node.func.attr
            home = node.func.value.id
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
            for n in self.graph:
                # Searches the graph for a node that resembles the called node. Might not work if multiple nodes are
                # named the same or if the node is not in the graph.
                if n.get_name() == dependency:
                    if already_found is True:
                        if n.is_identifier(home) is True and dependency_node.is_identifier(home) is False:
                            dependency_node = n
                        if n.is_identifier(home) is False and dependency_node.is_identifier(home) is False:
                            print("Mapper could not definitively determine the instance of " + dependency
                              + " that was called by " +
                              self.current_function)
                    else:
                        dependency_node = n
                    already_found = True

                if n.get_ast_node() == node:
                    this_node = n

            # This ideally would never be called. It only exists because the author is presently unaware of a
            # definitive way to determine the identity of a function called in an AST node.
            if dependency_node is None:
                if is_built_in is True:
                    class_name = "Builtins"
                    dependency_file = "System"
                else:
                    class_name = "Unknown"
                    dependency_file = "Unknown"
                dependency_node = FuncNode(filename=dependency_file, class_name=class_name, name=dependency)

            # Creates this node if it was not already in the graph.
            try:
                this_node
            except NameError:
                this_node = FuncNode(filename=self.current_filename, class_name=self.current_class,
                                     name=self.current_function, ast_node=node)

            # Ensures that the relevant nodes are in the graph if they were not already.
            self.add_node(this_node)
            self.add_node(dependency_node)

            # This works even if the node was not added to the graph because the existing node's hash would be the same.
            self.graph[this_node].add_dependency(dependency_node)
            self.graph[dependency_node].add_dependent(this_node)

        self.generic_visit(node)


# Main initial execution of the script via the command-line.
def main():

    def create_graph(found_filename):
        tree[found_filename] = ast.parse(open(found_filename).read())
        creator[found_filename] = NodeCreator(found_filename)
        creator[found_filename].visit(tree[found_filename])
        py_files.append(found_filename)
        return {**graph, **creator[found_filename].get_graph()}

    # Configures the command-line interface.
    parser = argparse.ArgumentParser(description='Graph interfunctional Python dependencies. Searches given modules and'
                                                 ' lists included functions along with their dependents.')
    parser.add_argument('--filename', '-f', metavar='F', type=str, nargs="*",
                        help="Specify the name of the file to examine. Only one file or directory at once.")
    parser.add_argument('--directory', '-d', metavar='D', type=str, nargs="*",
                        help="Specify the directory to examine. Only one file or directory at once.")
    parser.add_argument('--inverse', '-i', action='store_true', default=False,
                        help="Inverse output so that dependencies are listed instead of dependents.")
    parser.add_argument('--built-ins', '-b', action='store_true',
                        help="Also graph when Python's built in functions are used.")
    parser.add_argument('--raw', '-r', action='store_true', default=False,
                        help="Remove instruction text and formatting.")
    args = parser.parse_args()

    # Processes the input parameters.
    if args.directory is None and args.filename is None:
        args.filename[0] = input("Filename to examine: ")

    tree = {}
    creator = {}
    py_files = []
    graph = {}
    logger = {}
    searched_files = []
    searched_directories = []

    if args.filename is not None:
        for file in args.filename:
            try:
                # Adds ".py" to the end of the file if that was not specified.
                if file[-3:] != ".py":
                    file += ".py"

                file_dir = file.split(os.sep)
                working_dir_str = sys.path[0] + os.sep
                for directory in file_dir[:-1]:
                    working_dir_str += directory
                graph = {**graph, **create_graph(file)}
                searched_files.append(file)
            except FileNotFoundError:
                print("Error: File %s was not found" % file)

    if args.directory is not None:
        for directory in args.directory:
            working_dir_str = sys.path[0] + os.sep + directory
            if os.path.isdir(working_dir_str):
                searched_directories.append(directory)
                for file in os.walk(working_dir_str, followlinks=True):
                    for i in range(len(file[2])):
                        found_filename = file[0] + os.sep + file[2][i]
                        if found_filename[-3:] == ".py":
                            graph = {**graph, **create_graph(found_filename)}
            else:
                print("Error: Directory %s was not found" % directory)

    for file in py_files:
        logger[file] = EdgeDetector(file, args.built_ins)
        logger[file].visit(tree[file])
        graph = {**graph, **logger[file].get_graph()}

    # Outputs the graph parsed from the AST in string form.
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
            print("Mapper searched: " + searched_str)
            print()
            if args.inverse is True:
                dependents_string = "Dependencies"
            else:
                dependents_string = "Dependents"
            print("%-20s %-20s" % ("Function Name", dependents_string))
            print()
            indent = "-20"

    for node in graph:
        format_string = "%" + indent + "s %" + indent + "s"
        print(format_string % (node, node.get_edges_str(dependencies=args.inverse)))


# Calls the main function to start the script.
if __name__ == "__main__":
    main()

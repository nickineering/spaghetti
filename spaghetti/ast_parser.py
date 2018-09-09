import importlib
import ast
import os
from spaghetti.func_node import FuncNode


# Parent class for basic AST parsing. Meant to be extended depending on the task.
class ASTParser(ast.NodeVisitor):

    def __init__(self, search, filename="", recursive=0):
        self.current_class = ""
        self.current_function = ""
        self.filename = filename
        self.search = search
        self._uncrawled = set()

        # Removes file extension.
        # self.current_filename = self.filename[:-3]
        self.current_filename = self.filename
        # Removes directory for simplicity. Should be included in future versions.
        self.current_filename = self.current_filename.split(os.sep)[-1]
        self.directory = ""
        self.recursive = recursive
        if self.recursive == 0:
            for x in self.filename.split(os.sep)[:-1]:
                self.directory += x + os.sep
            self.directory = self.directory.replace(os.getcwd() + os.sep, "")
        # self.full_directory = os.getcwd() + os.sep + self.directory

    def visit_ClassDef(self, node):
        self.handle_node(node, "current_class", self.generic_visit)

    def visit_FunctionDef(self, node):
        self.handle_node(node, "current_function", self.generic_visit)

    def handle_node(self, node, title, handler):
        old_title = self.__dict__[title]
        self.__dict__[title] = node.name
        handler(node)
        self.__dict__[title] = old_title

    # Adds the given node to the graph if it is not already in it.
    def add_node(self, node):
        if node not in self.search.graph:
            self.search.graph[node] = node


# Searches AST for nodes and adds them to the graph.
class NodeCreator(ASTParser):

    def visit_Import(self, node):
        # print(ast.dump(node))
        if self.recursive < 1:
            for reference in node.names:
                folders = self.directory.split(os.sep)
                self.crawl_import(node, reference, folders)

    def crawl_import(self, node, reference, folders, folder_index=0):
        try:
            folder = ""
            x = len(folders) - folder_index
            while x < len(folders) - 1:
                if folders[x] != "":
                    folder += folders[x] + "."
                x += 1
            imported_name = folder + reference.name
            # if imported_name not in self.search.imports:
            imported = importlib.import_module(imported_name)
            # relative_imported = imported.__file__.replace(os.getcwd() + os.sep, "")
            visitor = NodeCreator(search=self.search, filename=imported.__file__, recursive=self.recursive+1)
            tree_file = open(imported.__file__)
            tree = ast.parse(tree_file.read())
            visitor.visit(tree)
            self.search.crawled_imports.add(imported_name)
        except ImportError:
            if folder_index < len(folders):
                self.crawl_import(node, reference, folders, folder_index+1)
            else:
                self.search.uncrawled.add(reference.name)
        except AttributeError:
            self.search.uncrawled.add(reference.name)

    def visit_ClassDef(self, node):
        self.handle_node(node, "current_class", self.add_class_node)

    def add_class_node(self, node):
        current_node = FuncNode(filename=self.current_filename, class_name=self.current_class,
                                name="__init__", depth=self.recursive)
        self.add_node(current_node)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.handle_node(node, "current_function", self.add_function_node)

    # Creates a node for the function even though it might not be connected to any other nodes.
    def add_function_node(self, node):
        current_node = FuncNode(filename=self.current_filename, class_name=self.current_class,
                                name=self.current_function, depth=self.recursive, ast_node=node)
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
            try:
                dependency = node.func.id
                home = self.current_filename
            except AttributeError:
                print("AST Error")
                self.generic_visit(node)
                return

        # Checks if the current call is to a built-in function.
        is_built_in = False
        if dependency in dir(__builtins__):  # sys.builtin_module_names
            is_built_in = True

        if is_built_in is False or self.search.args.built_ins is True:
            dependency_node = None
            already_found = False
            # Searches the graph and selects the node being referenced.
            for n in self.search.graph:
                if n.get_name() == dependency or (n.get_name() == "__init__" and n.get_class() == dependency):
                    if already_found is True:
                        # If there is a conflict and this is a more exact match save this.
                        if n.is_identifier(home) is True and dependency_node.is_identifier(home) is False:
                            dependency_node = n
                        # Do nothing if existing node is better.
                        if n.is_identifier(home) is False and dependency_node.is_identifier(home) is True:
                            pass
                        # If neither or both match throw an error. This should not happen normally.
                        else:
                            self.search.unsure_nodes.add(self.current_filename + ":" + self.current_function + "(" +
                                                         dependency + ")")
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
    def add_edge(self, is_built_in, dependency, this_node, dependency_node=None):
        # Error handling if the node's identity could not be determined.
        if dependency_node is None:
            if is_built_in is True:
                class_name = "Builtins"
                dependency_file = "System"
            else:
                class_name = "Unknown"
                dependency_file = "Unknown"
            dependency_node = FuncNode(filename=dependency_file, class_name=class_name, name=dependency, depth=1)

        # Ensures that the relevant nodes are in the graph if they were not already.
        self.add_node(this_node)
        self.add_node(dependency_node)

        # This works even if the node was not added to the graph because the existing node's hash would be the same.
        self.search.graph[this_node].add_edge(dependency_node, dependency=True)
        self.search.graph[dependency_node].add_edge(this_node, dependency=False)
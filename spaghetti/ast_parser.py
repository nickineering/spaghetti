import importlib
import ast
import os
import builtins

try:
    from spaghetti.func_node import FuncNode
except ImportError:
    from func_node import FuncNode


# Parent class for basic AST parsing. Meant to be extended depending on the task
class ASTParser(ast.NodeVisitor):
    def __init__(self, search, filename="", recursive=0):
        self.search = search
        self.filename = filename
        self.recursive = recursive

        self.directory = ""
        # self.current_filename = self.filename[:-3] # Removes file extension.
        self.current_filename = self.filename
        self.current_class = ""
        self.current_function = ""

        if self.recursive == 0:
            for x in self.filename.split(os.sep)[:-1]:
                self.directory += x + os.sep
            self.directory = self.directory.replace(os.getcwd() + os.sep, "")

    def visit_ClassDef(self, node):
        self.handle_node(node, "current_class", self.generic_visit)

    def visit_FunctionDef(self, node):
        self.handle_node(node, "current_function", self.generic_visit)

    # Ensures that subclasses and inner functions do not permanently change the parent's name
    def handle_node(self, node, title, handler):
        old_title = self.__dict__[title]
        self.__dict__[title] = node.name
        handler(node)
        self.__dict__[title] = old_title

    # Adds the given node to the graph if it is not already in it
    def add_node(self, node):
        if node not in self.search.graph:
            self.search.graph[node] = node


# Searches AST for nodes and adds them to the graph
class NodeCreator(ASTParser):
    # Ensures that imported code is graphed as well
    def visit_Import(self, node):
        if self.recursive < 1:
            for reference in node.names:
                folders = self.directory.split(os.sep)
                self.crawl_import(node, reference, folders)

    # Utility function that recursively retries to crawl hard imports
    def crawl_import(self, node, reference, folders, folder_index=0):
        try:
            folder = ""
            x = len(folders) - folder_index
            while x < len(folders) - 1:
                if folders[x] != "":
                    folder += folders[x] + "."
                x += 1
            imported_name = folder + reference.name
            imported = importlib.import_module(imported_name)
            visitor = NodeCreator(
                search=self.search,
                filename=imported.__file__,
                recursive=self.recursive + 1,
            )
            tree_file = open(imported.__file__)
            tree = ast.parse(tree_file.read())
            visitor.visit(tree)
            self.search.crawled_imports.add(imported_name)
        except ImportError:
            if folder_index < len(folders):
                self.crawl_import(node, reference, folders, folder_index + 1)
            else:
                self.search.uncrawled.add(reference.name)
        except AttributeError:
            self.search.uncrawled.add(reference.name)

    def visit_ClassDef(self, node):
        self.handle_node(node, "current_class", self.add_class_node)

    # Creates a node for the class even though it might not be connected to any other nodes
    def add_class_node(self, node):
        current_node = FuncNode(
            filename=self.current_filename,
            class_name=self.current_class,
            name="__init__",
            depth=self.recursive,
            mode=self.search.mode,
        )
        self.add_node(current_node)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.handle_node(node, "current_function", self.add_function_node)

    # Creates a node for the function even though it might not be connected to any other nodes
    def add_function_node(self, node):
        current_node = FuncNode(
            filename=self.current_filename,
            class_name=self.current_class,
            name=self.current_function,
            depth=self.recursive,
            ast_node=node,
            mode=self.search.mode,
        )
        self.add_node(current_node)
        self.generic_visit(node)


# Detects connections in the AST and adds them as edges in the graph
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
                self.generic_visit(node)
                return

        dependency_node = None
        already_found = False

        # Searches the graph and selects the node being referenced
        for n in self.search.graph:
            if n.get_name() == dependency or (
                n.get_name() == "__init__" and n.get_class() == dependency
            ):
                if already_found is True:
                    # If there is a conflict and this is a more exact match save this
                    if (
                        n.is_identifier(home) is True
                        and dependency_node.is_identifier(home) is False
                    ):
                        dependency_node = n
                    # Do nothing if existing node is better.
                    if (
                        n.is_identifier(home) is False
                        and dependency_node.is_identifier(home) is True
                    ):
                        pass
                    # If neither or both match throw an error. This should not happen normally.
                    else:
                        self.search.unsure_nodes.add(
                            self.current_filename
                            + ":"
                            + self.current_function
                            + "("
                            + dependency
                            + ")"
                        )
                else:
                    dependency_node = n
                    already_found = True

            if n.get_ast_node() == node:
                this_node = n

        # Creates this node if it was not already in the graph
        try:
            this_node
        except NameError:
            if self.current_function == "":
                self.current_function = "__main__"

            this_node = FuncNode(
                filename=self.current_filename,
                class_name=self.current_class,
                name=self.current_function,
                ast_node=node,
                mode=self.search.mode,
            )

        self.add_edge(
            dependency,
            this_node,
            dependency_node,
        )
        self.generic_visit(node)

    # Adds an edge to the graph
    def add_edge(self, dependency, this_node, dependency_node=None):
        # Error handling if the node's identity could not be determined
        if dependency_node is None:
            if dependency in dir(builtins):  # sys.builtin_module_names
                class_name = "Builtins"
                dependency_file = "System"
            else:
                class_name = "Unknown"
                dependency_file = "Unknown"
            dependency_node = FuncNode(
                filename=dependency_file,
                class_name=class_name,
                name=dependency,
                depth=1,
                mode=self.search.mode,
            )

        # Ensures that the relevant nodes are in the graph if they were not already
        self.add_node(this_node)
        self.add_node(dependency_node)

        # This works even if the node was not added to the graph because the existing node's hash would be the same.
        self.search.graph[this_node].add_edge(dependency_node, dependency=True)
        self.search.graph[dependency_node].add_edge(this_node, dependency=False)

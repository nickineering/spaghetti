import ast
import argparse
import copy
import builtins
import os


class FuncNode:

    def __init__(self, filename="", class_name="", name=""):
        self._filename = filename
        self._class_name = class_name
        self._name = name
        self._calls = set()

    def __repr__(self):
        return self._class_name + "." + self._name

    def __eq__(self, other):
        return (
            self.__class__ == other.__class__ and
            self._filename == other.get_filename() and
            self._class_name == other.get_class() and
            self._name == other.get_name()
        )

    def __hash__(self):
        return hash((self._filename, self._class_name, self._name))

    def set_filename(self, filename):
        self._filename = filename

    def get_filename(self):
        return self._filename

    def set_class(self, class_name):
        self._class_name = class_name

    def get_class(self):
        return self._class_name

    def set_name(self, name):
        self._name = name

    def get_name(self):
        return self._name

    def add_call(self, call):
        self._calls.add(call)

    def clear_calls(self):
        self._calls.clear()

    def get_calls(self):
        return self._calls

    def get_calls_str(self):
        return_str = ""
        for call in self._calls:
            return_str += "(" + repr(call) + ")"
        return return_str


class FuncLister(ast.NodeVisitor):
    filename = ""
    current_class = ""
    current_function = ""
    theGraph = {}

    def __init__(self, filename, built_ins=False):
        self.filename = filename
        self.allow_built_ins = built_ins
        self.current_filename = self.filename[:-3]
        self.current_filename = self.current_filename.split(os.sep)[-1]

    def visit_ClassDef(self, node):
        # print("Class " + node.name)
        self.current_class = node.name
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        # print("Def " + node.name)
        self.current_function = node.name
        current_node = FuncNode(filename=self.current_filename, class_name=self.current_class, name=self.current_function)
        if current_node not in self.theGraph:
            self.theGraph[current_node] = current_node

        self.generic_visit(node)

    def visit_Call(self, node):
        # print("Call " + node.func.id + " from " + self.current_func)
        # Should check here if it is a built-in function
        # print("Current: " + self.current_func)
        # print(ast.dump(node))

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

        is_built_in = False
        if call in dir(__builtins__):
            is_built_in = True
            call_file = ''


        if is_built_in is False or self.allow_built_ins is True:

            callNode = FuncNode(filename=call_file, class_name=class_name, name=call)
            if callNode not in self.theGraph:
                self.theGraph[callNode] = callNode

            funcNode = FuncNode(filename=self.current_filename, class_name=self.current_class, name=self.current_function)
            if funcNode not in self.theGraph:
                self.theGraph[funcNode] = funcNode
            self.theGraph[funcNode].add_call(callNode)
            # print(repr(self.theGraph[funcNode]) + " " + self.theGraph[funcNode].get_calls_str())
            # print(ast.dump(node))
            # print()

        self.generic_visit(node)

    def get_graph(self):
        return self.theGraph


parser = argparse.ArgumentParser(description='Graph interfunctional Python dependencies.')
parser.add_argument('--filename', '-f', metavar='F', type=str, nargs=1,
                    help="Specify the name of the file to be examined.")
parser.add_argument('--built-ins', '-b', action='store_true',
                    help="Also graph when Python's built in functions are used.")
parser.add_argument('--debug', '-d', dest='debug', action='store_true', default=False,
                    help="Enable debugging output.")

args = parser.parse_args()
DEBUG = args.debug

if args.filename:
    filename = args.filename[0]
else:
    filename = input("Filename to examine: ")

if filename[-3:] != ".py":
    filename += ".py"

tree = ast.parse(open(filename).read())
lister = FuncLister(filename, args.built_ins)
lister.visit(tree)

testGraph = lister.get_graph()
for node in testGraph:
    print(repr(node) + " " + repr(node.get_calls_str()))
print("Complete")

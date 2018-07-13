import ast
import argparse
# import builtins


class FuncNode:
    _name = ""
    _class_name = ""

    def __init__(self, name="none", class_name="none"):
        self._name = name
        self._class_name = class_name

    def get_name(self):
        return self._name

    def get_class(self):
        return self._class_name

    def set_name(self, name):
        self._name = name

    def set_class(self, class_name):
        self._class_name = class_name


class FuncLister(ast.NodeVisitor):
    funcNode = FuncNode()
    theGraph = {}
    built_ins = False

    def __init__(self, built_ins=False):
        self.built_ins = built_ins

    def visit_ClassDef(self, node):
        # print("Class " + node.name)
        self.current_class = node.name
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        # print("Def " + node.name)
        self.current_func = node.name
        self.generic_visit(node)

    def visit_Call(self, node):
        # print("Call " + node.func.id + " from " + self.current_func)
        # Should check here if it is a built-in function
        # print("Current: " + self.current_func)
        # print(ast.dump(node))
        if self.current_func in self.theGraph:
            try:
                self.theGraph[self.current_func].append([node.func.id, self.current_class])
            except AttributeError:
                self.theGraph[self.current_func].append([node.func.attr, self.current_class])
                pass
        else:
            try:
                self.theGraph[self.current_func] = [[node.func.id], self.current_class]
            except AttributeError:
                print(ast.dump(node))
                # self.theGraph[self.current_func] = [node.func.value.id]
                pass
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
lister = FuncLister(args.built_ins)
lister.visit(tree)

testGraph = lister.get_graph()
for node in testGraph:
    for call in testGraph[node]:
        print(node + " " + call[1] + "." + call[0])
print("Complete")

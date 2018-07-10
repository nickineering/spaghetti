import ast, argparse


class FuncLister(ast.NodeVisitor):
    current_func = "file"
    theGraph = {}
    built_ins = False

    def __init__(self, built_ins=False):
        self.built_ins = built_ins

    def visit_FunctionDef(self, node):
        # print("Def " + node.name)
        self.current_func = node.name
        self.generic_visit(node)

    def visit_Call(self, node):
        # print("Call " + node.func.id + " from " + self.current_func)
        # Should check here if it is a built-in function
        if self.current_func in self.theGraph:
            self.theGraph[self.current_func].append(node.func.id)
        else:
            self.theGraph[self.current_func] = [node.func.id]
        self.generic_visit(node)

    def get_graph(self):
        return self.theGraph


parser = argparse.ArgumentParser(description='Graph interfunctional Python dependencies.')
parser.add_argument('--filename', '-f', metavar='F', type=str, nargs=1,
                    help="Specify the name of the file to be examined.")
parser.add_argument('--built-ins', '-b', action='store_true',
                    help="Also graph when Python's built in functions are used.")

args = parser.parse_args()
if args.filename:
    filename = args.filename[0]
else:
    filename = input("Filename to examine: ")

if filename[-3:] != ".py":
    filename += ".py"

tree = ast.parse(open(filename).read())
FuncLister(args.built_ins).visit(tree)

testGraph = FuncLister().get_graph()
for node in testGraph:
    for call in testGraph[node]:
        print(node + " " + call)
print("Complete")

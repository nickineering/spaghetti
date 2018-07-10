import ast, sys, argparse


class FuncLister(ast.NodeVisitor):
    current_func = "file"
    theGraph = {}

    def visit_FunctionDef(self, node):
        # print("Def " + node.name)
        self.current_func = node.name
        self.generic_visit(node)

    def visit_Call(self, node):
        # print("Call " + node.func.id + " from " + self.current_func)
        if self.current_func in self.theGraph:
            self.theGraph[self.current_func].append(node.func.id)
        else:
            self.theGraph[self.current_func] = [node.func.id]
        self.generic_visit(node)

    def get_graph(self):
        return self.theGraph


parser = argparse.ArgumentParser(description='Graph interfunctional Python dependencies.')
parser.add_argument('--filename', '-f', metavar='F', type=str, nargs=1, help='Specify filename')
args = parser.parse_args()
if args.filename:
    filename = args.filename[0]
else:
    filename = input("Filename to examine: ")

if filename[-3:] != ".py":
    filename += ".py"

tree = ast.parse(open(filename).read())
FuncLister().visit(tree)

testGraph = FuncLister().get_graph()
print("Complete")

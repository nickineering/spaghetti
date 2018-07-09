import ast


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


tree = ast.parse(open('TestFunctions.py').read())
FuncLister().visit(tree)


testGraph = FuncLister().get_graph()
print("Complete")

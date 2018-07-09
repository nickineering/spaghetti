import TestFunctions, inspect, ast

# TestFunctions.function1()
# print(inspect.getmembers(TestFunctions))
# print(open('TestFunctions.py').read())

tree = ast.parse(open('TestFunctions.py').read())
# print(ast.dump(tree))


# class FuncLister(ast.NodeVisitor):
#     def visit_FunctionDef(self, node):
#         print(node.name)
#         self.generic_visit(node)
#
#
# FuncLister().visit(tree)

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        print(node.name)
    elif isinstance(node, ast.Call):
        print(node.func.id)


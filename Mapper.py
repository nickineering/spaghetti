import ast


# Not fully recursive
def search_function(root):
    # print("Running sf")
    # print(ast.dump(root))

    for node in ast.iter_child_nodes(root):
        # print(ast.dump(node))
        if isinstance(node, ast.FunctionDef):
            print("Def " + node.name)
            search_function(node)
        if isinstance(node, ast.Call):
            print("Call " + node.func.id + " from " + root.func.id)

    # print("Finished sf")


tree = ast.parse(open('TestFunctions.py').read())

theGraph = {}

# print(ast.dump(tree))
search_function(tree)

# for node in theGraph:
#     print(node)

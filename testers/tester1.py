from testers import tester2


def function1():
    print("function1")
    function2()
    tester2.t2function1()


def function2():
    print("function2")


def function3():
    recursive_function(5)
    print("function3")
    # t2Class = tester2.T2Class()
    # t2Class.t2method2()


def function4():
    print("function4")
    function1()
    outer_function()


def recursive_function (remaining):
    print("recursive_function " + remaining + " remaining")
    if remaining > 0:
        recursive_function(remaining-1)


def outer_function():
    print("outer_function")

    def inner_function():
        print("inner_function")
        function2()

    inner_function()


class TestClass():

    def __init__(self):
        print("__init__")
        self.method4()

    def method1(self):
        print("method1")

    def method2(self):
        print("method2")
        self.method3()
        function2()

    def method3(self):
        print("method3")

    def method4(self):
        print("method4")
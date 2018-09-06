import tester2
from tester2 import T2SubClass
import non_existant_import


def function1():
    print("function1")
    function2()
    tester2.t2function1()
    print(lambda_example(5))


def function2():
    print("function2")


def function3():
    print("function3")
    recursive_function(5)
    t2_class = tester2.T2Class()
    t2_class.t2method2()


def function4():
    print("function4")
    function1()
    outer_function()


def recursive_function(remaining):
    print("recursive_function " + repr(remaining) + " remaining")
    if int(remaining) > 0:
        recursive_function(remaining-1)


def outer_function():
    print("outer_function")

    def inner_function():
        print("inner_function")
        function2()

    print("outer_function after inner_function declaration")
    inner_function()


def lambda_example(n):
    return lambda x: x + n


class TestClass:

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
        self.method1()

    def method4(self):
        print("method4")


if __name__ == "__main__":
    outer_function()
    function3()
    sub = T2SubClass()
    sub.t2sub1()
    sub.t2method1()
    tc = TestClass()

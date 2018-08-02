def t2function1():
    print("t2function1")


def t2function2():
    print("t2function2")
    t2function2()


def t2function3():
    print("t2function3")


class T2Class:

    def t2method1(self):
        print("T2method1")

    def t2method2(self):
        print("T2method2")


class T2SubClass(T2Class):

    def __init__(self):
        print("T2SubClass.__init__")

    def t2sub1(self):
        print("t2sub1")


if __name__ == "__main__":
    print("tester2")

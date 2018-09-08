def a():
    print("a")
    b()
    c()


def b():
    print("b")
    d()


def c():
    print("c")
    d()


def d():
    print("d")
    e()
    f()


def e():
    print("e")
    g()


def f():
    print("f")


def g():
    print("g")
    f()

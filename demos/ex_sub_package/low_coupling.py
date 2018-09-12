def f1():
    f4()


def f2():
    f3()


def f3():
    f1()


def f4():
    pass


def f5():
    f2()


def f6():
    f1()


def f7():
    f3()


def f8():
    f2()

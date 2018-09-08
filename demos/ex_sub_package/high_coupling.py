def f1():
    f4()
    f4()


def f2():
    f1()
    f3()
    f1()


def f3():
    f1()


def f4():
    pass


def f5():
    f2()
    f2()


def f6():
    f1()
    f2()
    f5()


def f7():
    f3()
    f2()
    f5()


def f8():
    f2()
    f5()

def invisible_dependency():
    print("I'm invisible")


def dependent():
    cloak = invisible_dependency
    cloak()


dependent()

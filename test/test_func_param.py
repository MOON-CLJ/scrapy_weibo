def a():
    print 'hehe'
    return 5


def b(a=a()):
    print a

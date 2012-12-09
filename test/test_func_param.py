"""
>>> from test_func_param import c
hehe
"""


def a():
    print 'hehe'
    return 5


def c():
    print "haha"


def b(a=a()):
    print a

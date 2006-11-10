"""
This module defines common functions and exception class definitions
used all over VisTrails.
"""

################################################################################

def invert(d):
    """invert(dict) -> dict. Returns an inverted dictionary by
    switching key-value pairs."""
    return dict([[v,k] for k,v in d.items()])

################################################################################

def unimplemented():
    """Raises UnimplementedException."""
    raise UnimplementedException()

def abstract():
    """Raises AbstractException.""" 
    raise AbstractException()

################################################################################

class NoMakeConnection(Exception):
    """NoMakeConnection is raised when a VisConnection doesn't know
    how to create a live version of itself. This is an internal error
    that should never be seen by a user. Please report a bug if you
    see this."""
    def __init__(self, conn):
        self.conn = conn
    def __str__(self):
        return "Connection %s has no makeConnection method" % self.conn

class NoSummon(Exception):
    """NoSummon is raised when a VisObject doesn't know how to create
    a live version of itself. This is an internal error that should
    never be seen by a user. Please report a bug if you see this."""
    def __init__(self, obj):
        self.obj = obj
    def __str__(self):
        return "Module %s has no summon method" % self.obj

class MissingPlugin(Exception):
    """MissingPlugin is raised when a plugin is needed by a pipeline,
    but the plugin is not present in the VisTrails registry."""
    def __init__(self, pluginName):
        self.name = pluginName
    def __str__(self):
        return "Plugin '%s' is missing" % pluginName

class UnimplementedException(Exception):
    """UnimplementedException is raised when some interface hasn't
    been implemented yet. This is an internal error that should never
    be seen by a user. Please report a bug if you see this."""
    def __str__(self):
	return "Object is Unimplemented"

class AbstractException(Exception):
    """AbstractException is raised when an abstract method is called.
    This is an internal error that should never be seen by a
    user. Please report a bug if you see this."""
    def __str__(self):
	return "Abstract Method was called"

class VistrailsInternalError(Exception):
    """VistrailsInternalError is raised when an unexpected internal
    inconsistency happens. This is (clearly) an internal error that
    should never be seen by a user. Please report a bug if you see
    this."""
    def __init__(self, msg):
        self.emsg = msg
    def __str__(self):
        return "Vistrails Internal Error: " + str(self.emsg)

class InvalidVistrailModuleType(Exception):
    """InvalidVistrailModuleType is raised when a module type is
    inconsistent with the surroundings. (For example, a Filter being
    used where an Object is expected). This is probably an internal
    error, so please report a bug if you see it."""
    def __init__(self, mt):
        self.emt = mt
    def __str__(self):
        return "Invalid Module Type: " + str(self.emt)

class VersionTooLow(Exception):
    """VersionTooLow is raised when you're running an outdated version
    of some necessary software or package."""
    def __init__(self, sw, required_version):
        self.sw = sw
        self.required_version = required_version
    def __str__(self):
	return ("Your version of '" +
                sw +
                "' is too low. Please upgrade to " +
                required_version +
                " or later")

################################################################################

# Only works for functions with NO kwargs!
def memo_method(method):
    """memo_method is a method decorator that memoizes results of the
    decorated method, trading off memory for time by caching previous
    results of the calls."""
    attrname = "_%s_memo_result" % id(method)
    memo = {}
    def decorated(self, *args):
        try:
            return memo[args]
        except KeyError:
            result = method(self, *args)
            memo[args] = result
            return result
    warn = "(This is a memoized method: Don't mutate the return value you're given.)"
    if method.__doc__:
        decorated.__doc__ = method.__doc__ + "\n\n" + warn
    else:
        decorated.__doc__ = warn
    return decorated

################################################################################

def all(bool_list, pred = lambda x: x):
    """all(list, [pred]) -> Boolean - Returns true if all elements are
    true.  If pred is given, it is applied to the list elements first"""
    for b in bool_list:
        if not pred(b):
            return False
    return True

def any(bool_list, pred = lambda x: x):
    """any(bool_list, [pred]) -> Boolean - Returns true if any element
    is true.  If pred is given, it is applied to the list elements
    first"""
    for b in bool_list:
        if pred(b):
            return True
    return False

def withIndex(lst):
    """withIndex(list) -> [(index, element)] - Returns a list with
    elements and their indices. Useful for iterating through the list."""
    return zip(range(len(lst)), lst)

def eprint(*args):
    """eprint(*args) -> False - Prints the arguments, then returns
    false. Useful inside a lambda expression, for example."""
    for v in args:
        print v,
    print

def uniq(l):
    if len(l) == 0:
        return []
    a = copy.copy(l)
    a.sort()
    l1 = a[:-1] 
    l2 = a[1:]
    return [a[0]] + [next for (i, next) in zip(l1, l2) if i != next]

class InstanceObject(object):
    def __init__(self, **kw):
        self.__dict__.update(kw)

def appendToDictOfLists(dict, key, value):
    """Appends /value/ to /dict/[/key/], or creates entry such that
    /dict/[/key/] == [/value/]."""
    try:
        dict[key].append(value)
    except KeyError:
        dict[key] = [value]

################################################################################

import unittest

class _TestFibo(object):
    @memo_method
    def f(self, x):
        if x == 0: return 0
        if x == 1: return 1
        return self.f(x-1) + self.f(x-2)

class TestCommon(unittest.TestCase):
    def testAppendToDictOfLists(self):
        f = {}
        self.assertEquals(f.has_key(1), False)
        appendToDictOfLists(f, 1, 1)
        self.assertEquals(f.has_key(1), True)
        self.assertEquals(f[1], [1])
        appendToDictOfLists(f, 1, 1)
        self.assertEquals(f.has_key(1), True)
        self.assertEquals(f[1], [1, 1])
        appendToDictOfLists(f, 1, 2)
        self.assertEquals(f.has_key(1), True)
        self.assertEquals(f[1], [1, 1, 2])
        appendToDictOfLists(f, 2, "Foo")
        self.assertEquals(f.has_key(2), True)
        self.assertEquals(f[2], ["Foo"])
        
    def testMemo(self):
        import time
        t1 = time.time()
        for i in xrange(10000):
            _TestFibo().f(102)
        t2 = time.time()
        for i in xrange(10000):
            _TestFibo().f(104)
        t3 = time.time()
        for i in xrange(10000):
            _TestFibo().f(106)
        t4 = time.time()
        d1 = t2 - t1
        d2 = t3 - t2
        d3 = t4 - t3
        if d1 == 0: r1 = 0
        else: r1 = d2 / d1
        if d2 == 0: r2 = 0
        else: r2 = d3 / d2
        self.assertEquals(r1< 2.618, True)
        self.assertEquals(r2< 2.618, True)
    def testMemo2(self):
        count = [0]
        class C1(object):
            pass
        class C2(object):
            pass
        class TestClassMemo(object):
            def __init__(self, cell):
                self.cell = cell
            @memo_method
            def f(self, cl, x):
                self.cell[0] += 1
                return x
        t = TestClassMemo(count)
        self.assertEquals(count[0], 0)
        t.f(C1, 0)
        self.assertEquals(count[0], 1)
        t.f(C1, 0)
        self.assertEquals(count[0], 1)
        t.f(C1, 1)
        self.assertEquals(count[0], 2)
        t.f(C2, 0)
        self.assertEquals(count[0], 3)
if __name__ == '__main__':
    unittest.main()

"""Defines a trace decorator that traces function calls. This is not currently
thread-safe. It won't crash, but the bump() printouts might not be correct."""

import sys
from core.data_structures import Stack
_output_file = sys.stderr

__current_method_name = Stack()

def _indent():
    _output_file.write(' ' * (len(__current_method_name)-1))

def trace_method(method):
    """trace_method is a method decorator that traces entry-exit of
    functions."""
    def decorated(self, *args, **kwargs):
        __current_method_name.push([method.__name__, 0])
        _indent()
        _output_file.write(method.__name__ + ".enter\n")
        result = method(self, *args, **kwargs)
        _indent()
        _output_file.write(method.__name__ + ".exit\n")
        __current_method_name.pop()
        return result
    return decorated

def bump_trace():
    __current_method_name.top()[1] += 1
    _indent()
    _output_file.write('%s.%s\n' % tuple(__current_method_name.top()))

###############################################################################

import unittest
import tempfile
import os

@trace_method
def test_fun(p1):
    return p1 + 5

@trace_method
def test_fun_2(p1):
    bump_trace()
    result = test_fun(p1) + 3
    bump_trace()
    return result

class TestTraceMethod(unittest.TestCase):

    def testTrace1(self):
        global _output_file
        (fd, name) = tempfile.mkstemp()
        os.close(fd)
        _output_file = file(name, 'w')

        x = test_fun(10)
        self.assertEquals(x, 15)
        
        _output_file.close()
        _output_file = sys.stderr

        output = "".join(file(name, 'r').readlines())
        self.assertEquals(output,
                          'test_fun.enter\n' +
                          'test_fun.exit\n')
        os.unlink(name)

    def testTrace2(self):
        global _output_file
        (fd, name) = tempfile.mkstemp()
        os.close(fd)
        _output_file = file(name, 'w')

        x = test_fun_2(10)
        self.assertEquals(x, 18)
        
        _output_file.close()
        _output_file = sys.stderr

        output = "".join(file(name, 'r').readlines())
        self.assertEquals(output,
                          'test_fun_2.enter\n' +
                          'test_fun_2.1\n' +
                          ' test_fun.enter\n' +
                          ' test_fun.exit\n' +
                          'test_fun_2.2\n' +
                          'test_fun_2.exit\n')
        os.unlink(name)

if __name__ == '__main__':
    unittest.main()

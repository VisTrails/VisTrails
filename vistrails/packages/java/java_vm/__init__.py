from __future__ import absolute_import

import functools
import os
import platform
import sys

from vistrails.core.bundles.pyimport import py_import


JavaException = None


USING_JYTHON = platform.system() in ['Java', 'JAVA']


__all__ = ['get_java_vm', 'get_class', 'build_jarray', 'implement_interface',
           'add_to_classpath', 'JavaException', 'USING_JYTHON']


if USING_JYTHON:
    # We are running inside Jython
    from .jython import *
else:
    try:
        raise ImportError # Deactivated for now
        import pyjnius
    except ImportError:
        try:
            import jpype
        except ImportError:
            py_import('jnius', {})
        else:
            # We don't have pyjnius but we have JPype
            from .jpype import *
    else:
        # We have pyjnius
        from .pyjnius import *


##############################################################################

import unittest


class TestInterfaceCallback(unittest.TestCase):
    def setUp(self):
        self._vm = get_java_vm()

    def test_callback_class(self):
        class InterfImpl(object):
            def __init__(self, testcase):
                self.testcase = testcase

            def callback(self, number, name):
                self.testcase.assertEqual(number, 42)
                self.testcase.assertEqual(name, u"answer")
                self.testcase.assertTrue(isinstance(name, (unicode, str)))
        # No class decorator in 2.5 syntax
        InterfImpl = implement('tests.jproxy.CallbackInterface')(InterfImpl)

        proxy = InterfImpl(self)
        self._vm.tests.jproxy.CallbackUser.use(proxy)


class TestInterfaceBean(unittest.TestCase):
    def setUp(self):
        self._vm = get_java_vm()

    def test_bean_class(self):
        class BeanImpl(object):
            def getNumber(self):
                return 42
            def getName(self):
                return "answer"
        # No class decorator in 2.5 syntax
        BeanImpl = implement('tests.jproxy.BeanInterface')(BeanImpl)
        proxy = BeanImpl()
        self._vm.tests.jproxy.BeanUser.use(proxy)


class TestJava(unittest.TestCase):
    def setUp(self):
        self._vm = get_java_vm()

    def test_std_class(self):
        Math = self._vm.java.lang.Math
        self.assertAlmostEqual(Math.abs(-4), 4)

    def test_get_class(self):
        Math = get_class('java.lang.Math')
        self.assertAlmostEqual(Math.abs(-4), 4)

    def test_arrays(self):
        Arrays = self._vm.java.util.Arrays
        array = build_jarray('int', [4, 2, 1, 2])
        Arrays.sort(array)
        exp = [1, 2, 2, 4]
        for i in xrange(4):
            self.assertEqual(array[i], exp[i])


if __name__ == '__main__':
    unittest.main()

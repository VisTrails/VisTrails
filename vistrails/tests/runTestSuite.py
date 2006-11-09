#!/usr/bin/env python

"""Runs all tests available in VisTrails modules, by importing all of
them, stealing the classes that look like unit tests, and running
unittest.main() on this script."""

import sys
import os

# Makes sure we can import modules as if we were running VisTrails
# from the root directory
if __name__ == '__main__':
    _thisDir = sys.argv[0]
else:
    _thisDir = sys.modules[__name__].__file__
_thisDir = os.path.split(_thisDir)[0]
if not _thisDir:
    root_directory = './../'
else:
    root_directory = _thisDir + '/../'
sys.path.append(root_directory)

# creates a bogus qt app so that testing can happen
import gui.qt
app = gui.qt.createBogusQtApp()

def subprint(s, overline=False):
    """Prints line with underline (and optionally overline) ASCII dashes."""
    if overline:
        print "-" * len(s)
    print s
    print "-" * len(s)

print "Test Suite for VisTrails"

import unittest

mainTestSuite = unittest.TestSuite()

def getTestCases(module):
    """Return all test cases from the module. Test cases are classes derived
    from unittest.TestCase"""
    result = []
    import inspect
    for member_name in dir(module):
        member = getattr(module, member_name)
        if inspect.isclass(member) and issubclass(member, unittest.TestCase):
            result.append(member)
    return result


subprint("Trying to import all modules")
for (p, subdirs, files) in os.walk(root_directory):
    if p.find('.svn') != -1:
        continue
    for filename in files:
        if not filename.endswith('.py'):
            continue
        module = p[5:] + '/' + filename[:-3]
        if module.startswith('tests'):
            continue
        if module.startswith('/'):
            continue
        if module.startswith('\\'):
            continue
        if module.startswith('packages'):
            continue
        if module.endswith('__init__'):
            continue
        if '#' in module:
            continue
        print "%s %s |" % (" " * (40 - len(module)), module),

        module = module.replace('/','.')
        module = module.replace('\\','.')
        if '.' in module:
            m = __import__(module, globals(), locals(), ['foo'])
        else:
            m = __import__(module)

        testCases = getTestCases(m)
        for testCase in testCases:
            suite = unittest.TestLoader().loadTestsFromTestCase(testCase)
            mainTestSuite.addTests(suite)

        if not testCases:
            print "WARNING: %s has no tests!" % filename
        else:
            print "Ok: %s test cases." % len(testCases)

unittest.TextTestRunner().run(mainTestSuite)

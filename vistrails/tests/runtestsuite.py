#!/usr/bin/env python

"""Runs all tests available in VisTrails modules by importing all of
them, stealing the classes that look like unit tests, and running
all of them.

runtestsuite.py also reports all VisTrails modules that don't export
any unit tests, as a crude measure of code coverage.

"""

import os
import sys
import unittest

# Makes sure we can import modules as if we were running VisTrails
# from the root directory
if __name__ == '__main__':
    _this_dir = sys.argv[0]
else:
    _this_dir = sys.modules[__name__].__file__
_this_dir = os.path.split(_this_dir)[0]
if not _this_dir:
    root_directory = './../'
else:
    root_directory = _this_dir + '/../'
sys.path.append(root_directory)

###############################################################################
# Utility

def sub_print(s, overline=False):
    """Prints line with underline (and optionally overline) ASCII dashes."""
    if overline:
        print "-" * len(s)
    print s
    print "-" * len(s)

def get_test_cases(module):
    """Return all test cases from the module. Test cases are classes derived
    from unittest.TestCase"""
    result = []
    import inspect
    for member_name in dir(module):
        member = getattr(module, member_name)
        if inspect.isclass(member) and issubclass(member, unittest.TestCase):
            result.append(member)
    return result

###############################################################################

# creates a bogus qt app so that testing can happen
import gui.qt
app = gui.qt.createBogusQtApp()

print "Test Suite for VisTrails"

main_test_suite = unittest.TestSuite()

sub_print("Trying to import all modules")
for (p, subdirs, files) in os.walk(root_directory):
    # skip subversion subdirectories
    if p.find('.svn') != -1:
        continue
    for filename in files:
        # skip files that don't look like VisTrails python modules
        if not filename.endswith('.py'):
            continue
        module = p[5:] + '/' + filename[:-3]
        if (module.startswith('tests') or
            module.startswith('/') or
            module.startswith('\\') or
            module.startswith('packages') or
            ('#' in module)):
            continue
        if ('system' in module and not
            module.endswith('__init__')):
            continue
        if (not ('system' in module) and
            module.endswith('__init__')):
            continue
        print "%s %s |" % (" " * (40 - len(module)), module),

        # use qualified import names with periods instead of
        # slashes to avoid duplicates in sys.modules
        module = module.replace('/','.')
        module = module.replace('\\','.')
        if '.' in module:
            m = __import__(module, globals(), locals(), ['foo'])
        else:
            m = __import__(module)

        test_cases = get_test_cases(m)
        for test_case in test_cases:
            suite = unittest.TestLoader().loadTestsFromTestCase(test_case)
            main_test_suite.addTests(suite)

        if not test_cases:
            print "WARNING: %s has no tests!" % filename
        else:
            print "Ok: %s test cases." % len(test_cases)

unittest.TextTestRunner().run(main_test_suite)

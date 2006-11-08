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
root_directory = _thisDir + '/../'

sys.path.append(root_directory)

# creates a bogus qt app so that testing can happen

import gui.qt
app = gui.qt.createBogusQtApp()

for (p, subdirs, files) in os.walk(root_directory):
    if p.find('.svn') != -1:
        continue
    for filename in files:
        if not filename.endswith('.py'):
            continue
        module = p[5:] + '/' + filename[:-3]
        if module.startswith('tests'):
            continue
        if module.startswith('packages'):
            continue
        print module
        m = __import__(module)
            

#!/usr/bin/env python
###############################################################################
##
## Copyright (C) 2006-2011, University of Utah. 
## All rights reserved.
## Contact: contact@vistrails.org
##
## This file is part of VisTrails.
##
## "Redistribution and use in source and binary forms, with or without 
## modification, are permitted provided that the following conditions are met:
##
##  - Redistributions of source code must retain the above copyright notice, 
##    this list of conditions and the following disclaimer.
##  - Redistributions in binary form must reproduce the above copyright 
##    notice, this list of conditions and the following disclaimer in the 
##    documentation and/or other materials provided with the distribution.
##  - Neither the name of the University of Utah nor the names of its 
##    contributors may be used to endorse or promote products derived from 
##    this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
## AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
## THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR 
## PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR 
## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; 
## OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
## WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR 
## OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF 
## ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
###############################################################################

"""Runs all tests available in VisTrails modules by importing all of
them, stealing the classes that look like unit tests, and running
all of them.

runtestsuite.py also reports all VisTrails modules that don't export
any unit tests, as a crude measure of code coverage.

"""

import os
import sys
import unittest
import os.path
import optparse

# Makes sure we can import modules as if we were running VisTrails
# from the root directory
if __name__ == '__main__':
    _this_dir = sys.argv[0]
else:
    _this_dir = sys.modules[__name__].__file__
_this_dir = os.path.split(_this_dir)[0]
if not _this_dir:
    root_directory = os.path.join('.','..')
else:
    root_directory = os.path.join(_this_dir,  '..')
sys.path.append(root_directory)

import tests

###############################################################################
# Testing Examples

EXAMPLES_PATH = os.path.join(_this_dir, '..', '..', 'examples')
#dictionary of examples that will be run with the workflows that will be ignored
VT_EXAMPLES = { 'EMBOSS_webservices.vt': [],
                'KEGGPathway.vt': [],
                'KEGG_SearchEntities_webservice.vt': [],
                'KEGG_webservices.vt': [],
                'brain_vistrail.vt': [],
                'chebi_webservice.vt': [],
                'head.vt': [],
                'infovis.vt': [],
                'noaa_webservices.vt': [],
                'offscreen.vt': [],
                'plot.vt': [],
                'spx.vt': [],
                'structure_or_id_webservice.vt': [],
                'terminator.vt': ["Isosurface Script"],
                'triangle_area.vt': [],
                'vtk.vt': [],
                'vtk_book_3rd_p189.vt': ["quadric", "SmapleFunction",
                                         "Almost there"],
                'vtk_book_3rd_p193.vt': ["modules", "connections",
                                         "lookup table"],
                'vtk_http.vt': [],
    }


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

from optparse import OptionParser
usage = "Usage: %prog [options] [module1 module2 ...]"
parser = OptionParser(usage=usage)
parser.add_option("-V", "--verbose", action="store", type="int",
                  default=None, dest="verbose",
                  help="set verboseness level(0--2, default=0, "
                  "higher means more verbose)")
parser.add_option("-e", "--examples", action="store_true",
                  default=None,
                  help="will run vistrails examples")

(options, args) = parser.parse_args()
verbose = 0
if options.verbose:
    verbose = options.verbose
test_examples = False 
if options.examples:
    test_examples = True
test_modules = None
if len(args) > 0:
    test_modules = set(args)

###############################################################################
# reinitializing arguments and options so VisTrails does not try parsing them
sys.argv = sys.argv[:1]

# creates the app so that testing can happen
import gui.application

# We need the windows so we can test events, etc.
gui.application.start_application({'interactiveMode': True,
                                   'nologger': True})

print "Test Suite for VisTrails"

main_test_suite = unittest.TestSuite()

if test_modules:
    sub_print("Trying to import some of the modules")
else:
    sub_print("Trying to import all modules")

for (p, subdirs, files) in os.walk(root_directory):
    # skip subversion subdirectories
    if p.find('.svn') != -1:
        continue
    for filename in files:
        # skip files that don't look like VisTrails python modules
        if not filename.endswith('.py'):
            continue
#        module = p[5:] + '/' + filename[:-3]
        module = p[len(root_directory)+1:] + os.sep + filename[:-3]
        if (module.startswith('tests') or
            module.startswith(os.sep) or
            module.startswith('\\') or
            ('#' in module)):
            continue
        if ('system' in module and not
            module.endswith('__init__')):
            continue
        if test_modules and not module in test_modules:
            continue
        msg = ("%s %s |" % (" " * (40 - len(module)), module))

        # use qualified import names with periods instead of
        # slashes to avoid duplicates in sys.modules
        module = module.replace('/','.')
        module = module.replace('\\','.')
        if module.endswith('__init__'):
            module = module[:-9]
        try:
            if '.' in module:
                m = __import__(module, globals(), locals(), ['foo'])
            else:
                m = __import__(module)
        except tests.NotModule:
            if verbose >= 1:
                print "Skipping %s, not an importable module" % filename
        except:
            print msg, "ERROR: Could not import module!"
            continue

        test_cases = get_test_cases(m)
        for test_case in test_cases:
            suite = unittest.TestLoader().loadTestsFromTestCase(test_case)
            main_test_suite.addTests(suite)

        if not test_cases and verbose >= 1:
            print msg, "WARNING: %s has no tests!" % filename
        elif verbose >= 2:
            print msg, "Ok: %s test cases." % len(test_cases)

unittest.TextTestRunner().run(main_test_suite)
if test_examples:
    import core.db.io
    import core.db.locator
    import core.console_mode
    print "Testing examples:"
    summary = {}
    nworkflows = 0
    nvtfiles = 0
    for vtfile in VT_EXAMPLES.keys():
        try:
            errs = []
            filename = os.path.join(EXAMPLES_PATH,
                                    vtfile)
            print filename
            locator = core.db.locator.FileLocator(os.path.abspath(filename))
            (v, abstractions, thumbnails, mashups) = core.db.io.load_vistrail(locator)
            w_list = []
            for version,tag in v.get_tagMap().iteritems():
                if tag not in VT_EXAMPLES[vtfile]:
                    w_list.append((locator,version))
                    nworkflows += 1
            if len(w_list) > 0:
                errs = core.console_mode.run(w_list, update_vistrail=False)
                summary[vtfile] = errs
        except Exception, e:
            errs.append((vtfile,"None", "None", str(e)))
            summary[vtfile] = errs
        nvtfiles += 1

    print "-----------------------------------------------------------------"
    print "Summary of Examples: %s workflows in %s vistrail files"%(nworkflows,
                                                                    nvtfiles)
    print ""
    errors = False
    for vtfile, errs in summary.iteritems():        
        print vtfile
        if len(errs) > 0:
            for err in errs:
                print("   *** Error in %s:%s:%s -- %s" % err)
            errors = True
        else:
            print "  Ok."
    print "-----------------------------------------------------------------"
    if errors:
        print "There were errors. See summary for more information"
    else:
        print "Examples ran successfully."
gui.application.get_vistrails_application().finishSession()
gui.application.stop_application()

#!/usr/bin/env python
###############################################################################
##
## Copyright (C) 2011-2013, NYU-Poly.
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
#import doctest
import os
import sys
import traceback
import unittest
import os.path
import optparse
from optparse import OptionParser

# Makes sure we can import modules as if we were running VisTrails
# from the root directory
_this_dir = os.path.dirname(os.path.realpath(__file__))
root_directory = os.path.realpath(os.path.join(_this_dir,  '..'))
sys.path.append(os.path.realpath(os.path.join(root_directory, '..')))

def setNewPyQtAPI():
    try:
        import sip
        # We now use the new PyQt API - IPython needs it
        sip.setapi('QString', 2)
        sip.setapi('QVariant', 2)
    except:
        print "Could not set PyQt API, is PyQt4 installed?"
setNewPyQtAPI()

import vistrails.tests
import vistrails.core
import vistrails.core.db.io
import vistrails.core.db.locator
import vistrails.gui.application

###############################################################################
# Testing Examples

EXAMPLES_PATH = os.path.join(_this_dir, '..', '..', 'examples')
#dictionary of examples that will be run with the workflows that will be ignored
VT_EXAMPLES = { 'EMBOSS_webservices.vt': ["ProphetOutput"],
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

###############################################################################

usage = "Usage: %prog [options] [module1 module2 ...]"
parser = OptionParser(usage=usage)
parser.add_option("-V", "--verbose", action="store", type="int",
                  default=0, dest="verbose",
                  help="set verboseness level(0--2, default=0, "
                  "higher means more verbose)")
parser.add_option("-e", "--examples", action="store_true",
                  default=False,
                  help="run vistrails examples")
parser.add_option("-i", "--images", action="store_true",
                  default=False,
                  help="perform image comparisons")

(options, args) = parser.parse_args()
# remove empty strings
args = filter(len, args)
verbose = options.verbose
test_examples = options.examples
test_images = options.images
test_modules = None
if len(args) > 0:
    test_modules = set(args)

###############################################################################
# reinitializing arguments and options so VisTrails does not try parsing them
sys.argv = sys.argv[:1]

# creates the app so that testing can happen

# We need the windows so we can test events, etc.
v = vistrails.gui.application.start_application({'interactiveMode': True,
                                       'nologger': True,
                                       'singleInstance': False,
                                       'fixedSpreadsheetCells': True})
if v != 0:
    app = vistrails.gui.application.get_vistrails_application()
    if app:
        app.finishSession()
    sys.exit(v)

# disable first vistrail
app = vistrails.gui.application.get_vistrails_application()
app.builderWindow.auto_view = False
app.builderWindow.close_all_vistrails(True)

print "Test Suite for VisTrails"

tests_passed = True

main_test_suite = unittest.TestSuite()
test_loader = unittest.TestLoader()

if test_modules:
    sub_print("Trying to import some of the modules")
else:
    sub_print("Trying to import all modules")

for (p, subdirs, files) in os.walk(root_directory):
    # skip subversion subdirectories
    if p.find('.svn') != -1 or p.find('.git') != -1 :
        continue
    for filename in files:
        # skip files that don't look like VisTrails python modules
        if not filename.endswith('.py'):
            continue
        module = os.path.join("vistrails", p[len(root_directory)+1:],
                              filename[:-3])
        if (module.startswith(os.sep) or
            ('#' in module)):
            continue

        # use qualified import names with periods instead of
        # slashes to avoid duplicates in sys.modules
        module = module.replace('/','.')
        module = module.replace('\\','.')
        if module.endswith('__init__'):
            module = module[:-9]

        if test_modules and not module in test_modules:
            continue
        if module.startswith('vistrails.tests.run'):
            continue
        if module.startswith('vistrails.tests.resources'):
            continue
        if ('system' in module and not
            module.endswith('__init__')):
            continue

        msg = ("%s %s |" % (" " * (40 - len(module)), module))

        m = None
        try:
            if '.' in module:
                m = __import__(module, globals(), locals(), ['foo'])
            else:
                m = __import__(module)
        except vistrails.tests.NotModule:
            if verbose >= 1:
                print "Skipping %s, not an importable module" % filename
            continue
        except:
            print msg, "ERROR: Could not import module!"
            if verbose >= 1:
                traceback.print_exc(file=sys.stdout)
            continue

        # Load the unittest TestCases
        suite = test_loader.loadTestsFromModule(m)

        # Load the doctests
        #try:
        #    suite.addTests(doctest.DocTestSuite(m))
        #except ValueError:
        #    pass # No doctest is fine, we check that some tests exist later
        # The doctests are currently opt-in; a load_tests method can be
        # defined to build a DocTestSuite
        # This is because some modules have interpreter-formatted examples that
        # are NOT doctests, and because mining the codebase for doctests is
        # painfully slow

        main_test_suite.addTests(suite)

        if suite.countTestCases() == 0 and verbose >= 1:
            print msg, "WARNING: %s has no tests!" % filename
        elif verbose >= 2:
            print msg, "Ok: %s test cases." % len(suite.countTestCases())

sub_print("Imported modules. Running %d tests..." %
          main_test_suite.countTestCases(),
          overline=True)

############## TEST VISTRAIL IMAGES ####################
# Compares thumbnails with the generated images to detect broken visualizations

image_tests = [("terminator.vt", [("terminator_isosurface", "Isosurface"),
                                  ("terminator_VRSW", "Volume Rendering SW"),
                                  ("terminator_CPSW", "Clipping Plane SW"),
                                  ("terminator_CRSW", "Combined Rendering SW"),
                                  ("terminator_ISSW", "Image Slices SW")])
               ]
def compare_thumbnails(prev, next):
    import vtk
    #vtkImageDifference assumes RGB, so strip alpha
    def removeAlpha(file):
        freader = vtk.vtkPNGReader()
        freader.SetFileName(file)
        removealpha = vtk.vtkImageExtractComponents()
        removealpha.SetComponents(0,1,2)
        removealpha.SetInputConnection(freader.GetOutputPort())
        removealpha.Update()
        return removealpha.GetOutput()
    #do the image comparison
    a = removeAlpha(prev)
    b = removeAlpha(next)
    idiff = vtk.vtkImageDifference()
    idiff.SetInput(a)
    idiff.SetImage(b)
    idiff.Update()
    return idiff.GetThresholdedError()

def image_test_generator(vtfile, version):
    from vistrails.core.db.locator import FileLocator
    from vistrails.core.db.io import load_vistrail
    import vistrails.core.console_mode
    def test(self):
        try:
            errs = []
            filename = os.path.join(EXAMPLES_PATH, vtfile)
            locator = FileLocator(os.path.abspath(filename))
            (v, abstractions, thumbnails, mashups) = load_vistrail(locator)
            errs = vistrails.core.console_mode.run(
                    [(locator, version)],
                    update_vistrail=False,
                    extra_info={'compare_thumbnails': compare_thumbnails})
            if len(errs) > 0:
                for err in errs:
                    print("   *** Error in %s:%s:%s -- %s" % err)
                    self.fail(str(err))
        except Exception, e:
            self.fail(str(e))
    return test

class TestVistrailImages(unittest.TestCase):
    pass

if not test_modules or test_images:
    for vt, t in image_tests:
        for name, version in t:
            test_name = 'test_%s' % name
            test = image_test_generator(vt, version)
            setattr(TestVistrailImages, test_name, test)
            main_test_suite.addTest(TestVistrailImages(test_name))

############## RUN TEST SUITE ####################

result = unittest.TextTestRunner().run(main_test_suite)

if not result.wasSuccessful():
    tests_passed = False

sub_print("Tests finished.", overline=True)

if test_examples:
    import vistrails.core.console_mode
    sub_print("Testing examples:")
    summary = {}
    nworkflows = 0
    nvtfiles = 0
    for vtfile in VT_EXAMPLES.keys():
        try:
            errs = []
            filename = os.path.join(EXAMPLES_PATH,
                                    vtfile)
            print filename
            locator = vistrails.core.db.locator.FileLocator(os.path.abspath(filename))
            (v, abstractions, thumbnails, mashups) = vistrails.core.db.io.load_vistrail(locator)
            w_list = []
            for version,tag in v.get_tagMap().iteritems():
                if tag not in VT_EXAMPLES[vtfile]:
                    w_list.append((locator,version))
                    nworkflows += 1
            if len(w_list) > 0:
                errs = vistrails.core.console_mode.run(w_list, update_vistrail=False)
                summary[vtfile] = errs
        except Exception, e:
            errs.append((vtfile,"None", "None", str(e)))
            summary[vtfile] = errs
        nvtfiles += 1

    print "-" * 79
    print "Summary of Examples: %s workflows in %s vistrail files" % (
              nworkflows, nvtfiles)
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
    print "-" * 79
    if errors:
        tests_passed = False
        sub_print("There were errors. See summary for more information")
    else:
        sub_print("Examples ran successfully.")

vistrails.gui.application.get_vistrails_application().finishSession()
vistrails.gui.application.stop_application()

# Test Runners can use the return value to know if the tests passed
sys.exit(0 if tests_passed else 1)

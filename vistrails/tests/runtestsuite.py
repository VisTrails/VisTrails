#!/usr/bin/env python
# pragma: no testimport
###############################################################################
##
## Copyright (C) 2011-2014, NYU-Poly.
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

import atexit
from distutils.version import LooseVersion
#import doctest
import locale
import os
import sys
import traceback
import os.path
import optparse
from optparse import OptionParser
import platform
import re
import shutil
import tempfile

# Makes sure we can import modules as if we were running VisTrails
# from the root directory
_this_dir = os.path.dirname(os.path.realpath(__file__))
root_directory = os.path.realpath(os.path.join(_this_dir,  '..'))
sys.path.insert(0, os.path.realpath(os.path.join(root_directory, '..')))

# Use a different temporary directory
test_temp_dir = tempfile.mkdtemp(prefix='vt_testsuite_')
tempfile.tempdir = test_temp_dir
@apply
class clean_tempdir(object):
    def __init__(self):
        atexit.register(self.clean)
        self.listdir = os.listdir
        self.isdir = os.path.isdir
        self.test_temp_dir = test_temp_dir
        self.rmtree = shutil.rmtree
        self.out = sys.stdout.write
    def clean(self):
        nb_dirs = 0
        nb_files = 0
        for f in self.listdir(self.test_temp_dir):
            if self.isdir(f):
                nb_dirs += 1
            else:
                nb_files += 1
        if nb_dirs > 0 or nb_files > 0:
            self.out("Warning: %d dirs and %d files were left behind in "
                     "tempdir, cleaning up\n" % (nb_dirs, nb_files))
        self.rmtree(self.test_temp_dir, ignore_errors=True)

def setNewPyQtAPI():
    try:
        import sip
        # We now use the new PyQt API - IPython needs it
        sip.setapi('QString', 2)
        sip.setapi('QVariant', 2)
    except Exception:
        print "Could not set PyQt API, is PyQt4 installed?"
setNewPyQtAPI()

# Log to the console
import vistrails.core.debug
vistrails.core.debug.DebugPrint.getInstance().log_to_console()

import vistrails.tests
import vistrails.core
import vistrails.core.db.io
import vistrails.core.db.locator
from vistrails.core import debug
import vistrails.gui.application
from vistrails.core.system import vistrails_root_directory, \
                                  vistrails_examples_directory
from vistrails.core.packagemanager import get_package_manager

# VisTrails does funny stuff with unittest/unittest2, be sure to load that
# after vistrails
import unittest

###############################################################################
# Testing Examples

EXAMPLES_PATH = vistrails_examples_directory()
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
parser.add_option("--installbundles", action='store_true',
                  default=False,
                  help=("Attempt to install missing Python packages "
                        "automatically"))
parser.add_option("-S", "--startup", action="store", type="str", default=None,
                  dest="dotVistrails",
                  help="Set startup file (default is temporary directory)")
parser.add_option('-L', '--locale', action='store', type='str', default='',
                  dest='locale',
                  help="set locale to this string")
parser.add_option('-D', '--debug', action='store_true',
                  default=False,
                  help="start interactive debugger on unexpected error")

(options, args) = parser.parse_args()
# remove empty strings
args = filter(len, args)
verbose = options.verbose
locale.setlocale(locale.LC_ALL, options.locale or '')
test_examples = options.examples
test_images = options.images
installbundles = options.installbundles
dotVistrails = options.dotVistrails
debug_mode = options.debug
test_modules = None
if len(args) > 0:
    test_modules = args
elif os.path.exists(EXAMPLES_PATH):
    test_images = True

def module_filter(name):
    if test_modules is None:
        return True
    for mod in test_modules:
        if name.startswith(mod):
            return True
    return False

###############################################################################
# reinitializing arguments and options so VisTrails does not try parsing them
sys.argv = sys.argv[:1]

# creates the app so that testing can happen

# We need the windows so we can test events, etc.
optionsDict = {
        'batch': False,
        'executionLog': False,
        'singleInstance': False,
        'installBundles': installbundles,
        'enablePackagesSilently': True,
        'handlerDontAsk': True,
        'developperDebugger': debug_mode,
    }
if dotVistrails:
    optionsDict['dotVistrails'] = dotVistrails
else:
    optionsDict['spawned'] = True
v = vistrails.gui.application.start_application(optionsDict)
if v != 0:
    app = vistrails.gui.application.get_vistrails_application()
    if app:
        app.finishSession()
    sys.exit(v)

# make sure that fixedCellSize is turned on
spreadsheet_conf = get_package_manager().get_package_configuration("spreadsheet")
spreadsheet_conf.fixedCellSize = True

# disable first vistrail
app = vistrails.gui.application.get_vistrails_application()
app.builderWindow.auto_view = False
app.builderWindow.close_all_vistrails(True)

print "Test Suite for VisTrails"
print "Locale settings: %s" % ', '.join('%s: %s' % (s, locale.setlocale(getattr(locale, s), None)) for s in ('LC_ALL', 'LC_TIME'))
print "Running on %s" % ', '.join(platform.uname())
print "Python is %s" % sys.version
try:
    from PyQt4 import QtCore
    print "Using PyQt4 %s with Qt %s" % (QtCore.PYQT_VERSION_STR, QtCore.qVersion())
except ImportError:
    print "PyQt4 not available"
for pkg in ('numpy', 'scipy', 'matplotlib'):
    try:
        ipkg = __import__(pkg, globals(), locals(), [], -1)
        print "Using %s %s" % (pkg, ipkg.__version__)
    except ImportError:
        print "%s not available" % pkg
try:
    import vtk
    print "Using vtk %s" % vtk.vtkVersion().GetVTKVersion()
except ImportError:
    print "vtk not available"


print ""

tests_passed = True

main_test_suite = unittest.TestSuite()
test_loader = unittest.TestLoader()

import_skip_regex = re.compile(r'(?i)# *pragma[: ]*no *testimport')

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
        module_file = os.path.join(p, filename)
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

        if not module_filter(module):
            continue
        if module.startswith('vistrails.tests.resources'):
            continue
        if ('.system.' in module and not
            module.endswith('__init__')):
            continue
        with open(module_file) as fp:
            l = fp.readline()
            if l.startswith('#!'): # shebang
                l = fp.readline()
            if import_skip_regex.match(l):
                if verbose >= 1:
                    print >>sys.stderr, ("Skipping %s, not an importable "
                                         "module" % module)
                continue

        m = None
        try:
            if '.' in module:
                m = __import__(module, globals(), locals(), ['foo'])
            else:
                m = __import__(module)
        except BaseException:
            print >>sys.stderr, "ERROR: Could not import module: %s" % module
            if verbose >= 1:
                traceback.print_exc(file=sys.stderr)
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
            print >>sys.stderr, "WARNING: module has no tests: %s" % module
        elif verbose >= 2:
            print >>sys.stderr, "OK: module as %d test cases: %s" % (
                    suite.countTestCases(),
                    module)

sub_print("Imported modules. Running %d tests%s..." % (
          main_test_suite.countTestCases(),
          ", and thumbnails comparison" if test_images else ''),
          overline=True)

############## TEST VISTRAIL IMAGES ####################
# Compares thumbnails with the generated images to detect broken visualizations

image_tests = [("terminator.vt", [("terminator_isosurface", "Isosurface"),
                                  ("terminator_VRSW", "Volume Rendering SW"),
                                  ("terminator_CPSW", "Clipping Plane SW"),
                                  ("terminator_CRSW", "Combined Rendering SW"),
                                  ("terminator_ISSW", "Image Slices SW")])
               ]
compare_use_vtk = False
try:
    import vtk
    if LooseVersion(vtk.vtkVersion().GetVTKVersion()) >= LooseVersion('5.8.0'):
        compare_use_vtk = True
except ImportError:
    pass
if compare_use_vtk:
    def compare_thumbnails(prev, next):
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
else:
    try:
        from scipy.misc import imread
    except ImportError:
        imread = None
    if test_images:
        print "Warning: old VTK version detected, NOT comparing thumbnails"
    if imread is not None:
        def compare_thumbnails(prev, next):
            prev_img = imread(prev)
            next_img = imread(next)
            assert len(prev_img.shape) == 3
            assert len(next_img.shape) == 3
            if prev_img.shape[:2] == next_img.shape[:2]:
                return 0
            else:
                return float('Inf')
    else:
        def compare_thumbnails(prev, next):
            if os.path.isfile(prev) and os.path.isfile(next):
                return 0
            else:
                return float('Inf')

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
            self.fail(debug.format_exception(e))
    return test

class TestVistrailImages(unittest.TestCase):
    pass

if test_images:
    for vt, t in image_tests:
        for name, version in t:
            test_name = 'test_%s' % name
            test = image_test_generator(vt, version)
            setattr(TestVistrailImages, test_name, test)
            main_test_suite.addTest(TestVistrailImages(test_name))

############## RUN TEST SUITE ####################

class TestResult(unittest.TextTestResult):
    def addSkip(self, test, reason):
        self.stream.writeln("skipped '{0}': {1}".format(str(test), reason))
        super(TestResult, self).addSkip(test, reason)

runner = unittest.TextTestRunner(
        verbosity=max(verbose, 1),
        resultclass=TestResult)
result = runner.run(main_test_suite)

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
            errs.append((vtfile,"None", "None", debug.format_exception(e)))
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

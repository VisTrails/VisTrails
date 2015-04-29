###############################################################################
##
## Copyright (C) 2014-2015, New York University.
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
##  - Neither the name of the New York University nor the names of its
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

from __future__ import division

import contextlib
import logging
import os
import sys
import unittest

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO


def enable_package(identifier):
    """Enables a package.
    """
    from vistrails.core.modules.module_registry import MissingPackage
    from vistrails.core.packagemanager import get_package_manager

    pm = get_package_manager()

    try:
        pm.get_package(identifier)
    except MissingPackage:
        dep_graph = pm.build_dependency_graph([identifier])
        for pkg_id in pm.get_ordered_dependencies(dep_graph):
            pkg = pm.identifier_is_available(pkg_id)
            if pkg is None:
                raise
            pm.late_enable_package(pkg.codepath)


def execute(modules, connections=[], add_port_specs=[],
            enable_pkg=True, full_results=False):
    """Build a pipeline and execute it.

    This is useful to simply build a pipeline in a test case, and run it. When
    doing that, intercept_result() can be used to check the results of each
    module.

    modules is a list of module tuples describing the modules to be created,
    with the following format:
        [('ModuleName', 'package.identifier', [
            # Functions
            ('port_name', [
                # Function parameters
                ('Signature', 'value-as-string'),
            ]),
        ])]

    connections is a list of tuples describing the connections to make, with
    the following format:
        [
            (source_module_index, 'source_port_name',
             dest_module_index, 'dest_module_name'),
         ]

    add_port_specs is a list of specs to add to modules, with the following
    format:
        [
            (mod_id, 'input'/'output', 'portname',
             '(port_sig)'),
        ]
    It is useful to test modules that can have custom ports through a
    configuration widget.

    The function returns the 'errors' dict it gets from the interpreter, so you
    should use a construct like self.assertFalse(execute(...)) if the execution
    is not supposed to fail.


    For example, this creates (and runs) an Integer module with its value set
    to 44, connected to a PythonCalc module, connected to a StandardOutput:

    self.assertFalse(execute([
            ('Float', 'org.vistrails.vistrails.basic', [
                ('value', [('Float', '44.0')]),
            ]),
            ('PythonCalc', 'org.vistrails.vistrails.pythoncalc', [
                ('value2', [('Float', '2.0')]),
                ('op', [('String', '-')]),
            ]),
            ('StandardOutput', 'org.vistrails.vistrails.basic', []),
        ],
        [
            (0, 'value', 1, 'value1'),
            (1, 'value', 2, 'value'),
        ]))
    """
    from vistrails.core.db.locator import XMLFileLocator
    from vistrails.core.modules.module_registry import MissingPackage
    from vistrails.core.packagemanager import get_package_manager
    from vistrails.core.utils import DummyView
    from vistrails.core.vistrail.connection import Connection
    from vistrails.core.vistrail.module import Module
    from vistrails.core.vistrail.module_function import ModuleFunction
    from vistrails.core.vistrail.module_param import ModuleParam
    from vistrails.core.vistrail.pipeline import Pipeline
    from vistrails.core.vistrail.port import Port
    from vistrails.core.vistrail.port_spec import PortSpec
    from vistrails.core.interpreter.noncached import Interpreter

    pm = get_package_manager()

    port_spec_per_module = {} # mod_id -> [portspec: PortSpec]
    j = 0
    for i, (mod_id, inout, name, sig) in enumerate(add_port_specs):
        mod_specs = port_spec_per_module.setdefault(mod_id, [])
        ps = PortSpec(id=i,
                      name=name,
                      type=inout,
                      sigstring=sig,
                      sort_key=-1)
        for psi in ps.port_spec_items:
            psi.id = j
            j += 1
        mod_specs.append(ps)

    pipeline = Pipeline()
    module_list = []
    for i, (name, identifier, functions) in enumerate(modules):
        function_list = []
        try:
            pkg = pm.get_package(identifier)
        except MissingPackage:
            if not enable_pkg:
                raise
            enable_package(identifier)
            pkg = pm.get_package(identifier)

        for func_name, params in functions:
            param_list = []
            for j, (param_type, param_val) in enumerate(params):
                param_list.append(ModuleParam(pos=j,
                                              type=param_type,
                                              val=param_val))
            function_list.append(ModuleFunction(name=func_name,
                                                parameters=param_list))
        name = name.rsplit('|', 1)
        if len(name) == 2:
            namespace, name = name
        else:
            namespace = None
            name, = name
        module = Module(name=name,
                        namespace=namespace,
                        package=identifier,
                        version=pkg.version,
                        id=i,
                        functions=function_list)
        for port_spec in port_spec_per_module.get(i, []):
            module.add_port_spec(port_spec)
        pipeline.add_module(module)
        module_list.append(module)

    for i, (sid, sport, did, dport) in enumerate(connections):
        s_sig = module_list[sid].get_port_spec(sport, 'output').sigstring
        d_sig = module_list[did].get_port_spec(dport, 'input').sigstring
        pipeline.add_connection(Connection(
                id=i,
                ports=[
                    Port(id=i*2,
                         type='source',
                         moduleId=sid,
                         name=sport,
                         signature=s_sig),
                    Port(id=i*2+1,
                         type='destination',
                         moduleId=did,
                         name=dport,
                         signature=d_sig),
                ]))

    interpreter = Interpreter.get()
    result = interpreter.execute(
            pipeline,
            locator=XMLFileLocator('foo.xml'),
            current_version=1,
            view=DummyView())
    if full_results:
        return result
    else:
        # Allows to do self.assertFalse(execute(...))
        return result.errors


def run_file(filename, tag_filter=lambda x: True):
    """Loads a .vt file and runs all the tagged versions in it.
    """
    import vistrails.core.db.io
    from vistrails.core.db.locator import FileLocator
    from vistrails.core.system import vistrails_root_directory
    from vistrails.core.vistrail.controller import VistrailController

    filename = os.path.join(vistrails_root_directory(), '..', filename)
    locator = FileLocator(filename)
    loaded_objs = vistrails.core.db.io.load_vistrail(locator)
    controller = VistrailController(loaded_objs[0], locator, *loaded_objs[1:])

    errors = []
    for version, name in controller.vistrail.get_tagMap().iteritems():
        if tag_filter(name):
            controller.change_selected_version(version)
            (result,), _ = controller.execute_current_workflow()
            if result.errors:
                errors.append(("%d: %s" % (version, name), result.errors))

    return errors


@contextlib.contextmanager
def intercept_result(module, output_name):
    """This temporarily hooks a module to intercept its results.

    It is used as a context manager, for instance:
    class MyModule(Module):
        def compute(self):
            self.set_output('res', 42)
        ...
    with intercept_result(MyModule, 'res') as results:
        self.assertFalse(execute(...))
    self.assertEqual(results, [42])
    """
    actual_setResult = module.set_output
    old_setResult = module.__dict__.get('set_output', None)
    results = []
    modules_index = {}  # Maps a Module to an index in the list, so a module
            # can change its result
    def new_setResult(self, name, value):
        if name == output_name:
            if self in modules_index:
                results[modules_index[self]] = value
            else:
                modules_index[self] = len(results)
                results.append(value)
        actual_setResult(self, name, value)
    module.set_output = new_setResult
    try:
        yield results
    finally:
        if old_setResult is not None:
            module.set_output = old_setResult
        else:
            del module.set_output


def intercept_results(*args):
    """This calls intercept_result() several times.

    You can pass it multiple modules and port names and it will nest the
    managers, for instance:
    with intercept_results(ModOne, 'one1', 'one2', ModTwo, 'two1', 'two2') as (
            one1, one2, two1, two2):
        self.assertFalse(execute(...))
    """
    from vistrails.core.modules.vistrails_module import Module

    ctx = []
    current_module = None
    for arg in args:
        if isinstance(arg, type) and issubclass(arg, Module):
            current_module = arg
        elif isinstance(arg, basestring):
            if current_module is None:
                raise ValueError
            ctx.append(intercept_result(current_module, arg))
        else:
            raise TypeError
    return contextlib.nested(*ctx)


@contextlib.contextmanager
def capture_stream(stream):
    lines = []
    old = getattr(sys, stream)
    sio = StringIO.StringIO()
    setattr(sys, stream, sio)
    try:
        yield lines
    finally:
        setattr(sys, stream,  old)
        lines.extend(sio.getvalue().split('\n'))
        if lines and not lines[-1]:
            del lines[-1]


@contextlib.contextmanager
def capture_stdout():
    with capture_stream('stdout') as lines:
        yield lines


@contextlib.contextmanager
def capture_stderr():
    with capture_stream('stderr') as lines:
        yield lines


class MockLogHandler(logging.Handler):
    """Mock logging handler to check for expected logs.
    """
    def __init__(self, mock_logger, *args, **kwargs):
        self._mock_logger = mock_logger
        self.reset()
        logging.Handler.__init__(self, *args, **kwargs)

    def emit(self, record):
        self.messages[record.levelname.lower()].append(record.getMessage())

    def reset(self):
        self.messages = {
            'debug': [],
            'info': [],
            'warning': [],
            'error': [],
            'critical': [],
        }

    def __enter__(self):
        if hasattr(logging, '_acquireLock'):
            logging._acquireLock()
        try:
            self._orig_handlers = self._mock_logger.handlers
            self._mock_logger.handlers = [self]
        finally:
            if hasattr(logging, '_acquireLock'):
                logging._releaseLock()
        return self

    def __exit__(self, etype, evalue, etraceback):
        if hasattr(logging, '_acquireLock'):
            logging._acquireLock()
        try:
            self._mock_logger.handlers = self._orig_handlers
        finally:
            if hasattr(logging, '_acquireLock'):
                logging._releaseLock()


def _id(obj):
    return obj


class SkippingChecker(object):
    """This mechanism allows to specify the checks you expect to fail.

    VisTrails has lots of dependencies, some of which not easy to setup.
    Running the test suite on your machine only tests what is available,
    skipping over tests that can't run because of missing dependencies.

    However, we want to make sure the right tests run on automated build
    machines. For that reason, this mechanism allows to specify a whitelist of
    the tests that are allowed to skip; if a disallowed test skips, an error
    will be reported so we'll know about it (and add the dependency to the
    machine, change our requirements, or fix the test if skipping was a
    mistake).
    """
    def __init__(self):
        self.allowed_tests = None

    def skippable(self, dependency_specs):
        if isinstance(dependency_specs, basestring):
            dependency_specs = dependency_specs,

        # Not using a whitelist; assume this is fine. The fact that this was
        # skipped will still be logged if the testsuite is verbose
        if self.allowed_tests is None:
            return True
        # Check against whitelist
        else:
            for dep in dependency_specs:
                path = []
                for comp in dep.split('.'):
                    path.append(comp)
                    if tuple(path) in self.allowed_tests:
                        return True

        return False

    def skip_test(self, dependency_specs, reason=None):
        """Skip this test, if allowed.

        This raises SkipTest, same as unittest.TestCase.skipTest(), except that
        if a list of skippable tests has been provided, this will fail if the
        test does not appear in the list.

        This allows the test runner to specify the tests it expects to be
        skipped, and fail if another test fails.

        There is no need to use this method when skipping a test that cannot
        run or is known to be broken on the current architecture.
        """
        if reason:
            args = reason,
        else:
            args = ()

        if self.skippable(dependency_specs):
            raise unittest.SkipTest(*args)
        else:
            raise AssertionError("Failing on disallowed skip_test(%r)" %
                                 ", ".join(args))

    def set_allowed_skips(self, tests):
        """Sets the tests that can be skipped.

        If tests is not None, skipping a test that doesn't appear in this list
        will fail instead.
        """
        self.allowed_tests = set(tuple(t.split('.')) for t in tests)


_test_skipping_checker = SkippingChecker()

skippable_test = _test_skipping_checker.skippable
skip_test_checked = _test_skipping_checker.skip_test
set_skippable_tests = _test_skipping_checker.set_allowed_skips


class TestSkippingChecker(unittest.TestCase):
    def do_skip(self, checker, deps, should_raise):
        try:
            checker.skip_test(deps)
        except unittest.SkipTest:
            if should_raise:
                self.fail("Skipping this test should have been disallowed")
        except AssertionError:
            if not should_raise:
                self.fail("Skipping this test should have been allowed")

    def test_checker(self):
        checker = SkippingChecker()
        checker.set_allowed_skips(['vtk',
                                   'mpl.hist',
                                   'sql.postgre', 'sql.mysql'])
        self.assertEqual(checker.allowed_tests,
                         set([('vtk',),
                              ('mpl', 'hist'),
                              ('sql', 'postgre'), ('sql', 'mysql')]))

        self.do_skip(checker, 'vtk', False)
        self.do_skip(checker, 'numpy', True)
        self.do_skip(checker, ['mpl'], True)
        self.do_skip(checker, ['vtk', 'numpy'], False)
        self.do_skip(checker, ['vtk.offscreen', 'numpy'], False)
        self.do_skip(checker, ['sql.oracle'], True)
        self.do_skip(checker, ['sql.mysql'], False)

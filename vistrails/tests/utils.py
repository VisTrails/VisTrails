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
import sys

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

from vistrails.core.modules.vistrails_module import Module
from vistrails.core.vistrail import enable_package


__all__ = ['enable_package', 'execute', 'intercept_result',
           'intercept_results', 'capture_stdout', 'capture_stderr',
           'MockLogHandler']


def execute(modules, connections=[], add_port_specs=[],
            enable_pkg=True, full_results=False):
    """Build a pipeline and execute it.

    This is useful to simply build a pipeline in a test case, and run it. When
    doing that, intercept_result() can be used to check the results of each
    module.

    The pipeline arguments are specified in
    :func:`vistrails.core.vistrail.build_pipeline()`.

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
    from vistrails.core.vistrail import build_pipeline
    from vistrails.core.db.locator import XMLFileLocator
    from vistrails.core.utils import DummyView
    from vistrails.core.interpreter.noncached import Interpreter

    pipeline = build_pipeline(modules, connections, add_port_specs, enable_pkg)

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
    # Maps a Module to an index in the list, so a module can change its result
    modules_index = {}
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

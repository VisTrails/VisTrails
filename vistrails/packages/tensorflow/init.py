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

import functools
import tensorflow
import types

from vistrails.core import debug
from vistrails.core.modules.config import ModuleSettings
from vistrails.core.modules.module_registry import get_module_registry
from .base import Op, TFOperation, Variable, _modules as base_modules, wrapped


def apply_kw(f, kw1):
    @functools.wraps(f)
    def wrapped(**kw2):
        kwargs = dict(kw1)
        kwargs.update(kw2)
        return f(**kwargs)
    return wrapped


class AutoOperation(TFOperation):
    _settings = ModuleSettings(abstract=True)

    def compute(self):
        immediate = {}
        stored = {}
        for name, descr, type_ in self.args:
            if self.has_input(name):
                value = self.get_input(name)
                if type_ is TFOperation or type_ is Variable:
                    stored[name] = value
                else:
                    immediate[name] = value

        f = apply_kw(getattr(tensorflow, self.op), immediate)
        self.set_output('output', Op(f, stored))


def get_indent(s):
    indent = 0
    for c in s:
        if c == ' ':
            indent += 1
        elif c == '\t':
            debug.warning("Found a tab in Google docstring!")
            indent += 4
        else:
            break
    return indent


def read_args(docstring):
    lines = iter(docstring.splitlines(False))
    rec_line = ''
    try:
        # Find the "Args:" line
        line = next(lines)
        while line.strip() != 'Args:':
            line = next(lines)
        indent_header = get_indent(line)
        indent_item = None

        # Loop on rest of lines, adding indented lines to the previous one
        line = next(lines)
        while line.strip():
            indent = get_indent(line)
            line = line.strip()
            if indent_item is None:
                indent_item = indent
                if indent_item <= indent_header:
                    break
                rec_line = line
            elif indent > indent_item:
                rec_line += ' ' + line
            elif indent < indent_item:
                break
            elif rec_line:
                yield rec_line
                rec_line = line

            line = next(lines)
    except StopIteration:
        pass
    if rec_line:
        yield rec_line


def initialize():
    from tensorflow.python.ops import standard_ops

    reg = get_module_registry()

    for module in base_modules:
        reg.add_module(module)

    reg.add_module(AutoOperation)

    def handle_package(pkg, namespace, exclude=set()):
        modules = set()

        for name in dir(pkg):
            if name in exclude:
                continue

            op = getattr(pkg, name)
            if isinstance(op, types.ModuleType) or name.startswith('_'):
                continue
            if not callable(op):
                continue
            if op.__doc__ is None:
                debug.log("Object has no __doc__: %r" % op)
                continue

            args = []
            for line in read_args(op.__doc__):
                if not ':' in line:
                    debug.log("Malformated argument in op %s's doc" % name)
                    continue
                arg, descr = line.split(':', 1)
                descr = descr.strip()

                if ((name == 'assign' or name.startswith('assign_')) and
                        arg == 'ref'):
                    type_ = Variable
                elif descr.lower().startswith("A list "):
                    type_ = '(basic:List)'
                elif arg == 'dtype' or arg == 'name':
                    type_ = '(basic:String)'
                else:
                    type_ = TFOperation
                args.append((arg, descr, type_))
            if not args:
                debug.log("Didn't find 'Args:' in op %s's doc; skipping" %
                          name)
                continue

            input_ports = [(arg, type_)
                           for (arg, descr, type_) in args]
            reg.add_module(type(name, (AutoOperation,),
                                {'args': args, 'op': name,
                                 '_input_ports': input_ports,
                                 '__doc__': op.__doc__}),
                           namespace=namespace)
            modules.add(name)

        return modules

    done = set(wrapped)
    done.update(handle_package(standard_ops, '', done))
    done.update(handle_package(tensorflow.train, 'train', done))
    done.update(handle_package(tensorflow.nn, 'nn', done))
    done.update(handle_package(tensorflow.image, 'image', done))


###############################################################################

import unittest


class TestParser(unittest.TestCase):
    def test_get_indent(self):
        self.assertEqual(get_indent('hello world'), 0)
        self.assertEqual(get_indent('  hello world'), 2)
        self.assertEqual(get_indent('    hello world'), 4)

    def test_read_args(self):
        doc = """\
Does a thing.

  This module does something.

  Args:
    one: First description
    two: Second
         description
"""
        doc = doc.strip()
        expected = ["one: First description", "two: Second description"]
        self.assertEqual(list(read_args(doc + '\n')), expected)
        self.assertEqual(list(read_args(doc)), expected)
        self.assertEqual(list(read_args(doc + '\n  Returns:\n')), expected)

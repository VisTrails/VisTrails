###############################################################################
##
## Copyright (C) 2014-2016, New York University.
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
import re
import tensorflow
import types

from vistrails.core import debug
from vistrails.core.modules.config import ModuleSettings
from vistrails.core.modules.module_registry import get_module_registry

from .base import Op, TFOperation, Variable, Optimizer, \
    _modules as base_modules, wrapped


def apply_kw(f, kw1):
    @functools.wraps(f)
    def wrapped(**kw2):
        kwargs = dict(kw1)
        kwargs.update(kw2)
        return f(**kwargs)
    return wrapped


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


_re_arg_bool = re.compile(r'^(?:A(?:n optional)? `bool`)|'
                          r'(?:If `?(?:true|false)`?)|'
                          r'Boolean', re.IGNORECASE)
_re_arg_int = re.compile(r'^(?:An integer)|(?:A Python integer)|'
                         r'(?:integer)', re.IGNORECASE)


def guess_args(obj, doc, op_name=None):
    args = []
    for line in read_args(doc):
        if not ':' in line:
            debug.log("Malformated argument in doc: %r" % obj)
            continue
        arg, descr = line.split(':', 1)
        descr = descr.strip()

        if arg == 'shape':
            type_ = '(basic:List)'
        elif (op_name is not None and
                (op_name == 'assign' or op_name.startswith('assign_')) and
                arg == 'ref'):
            type_ = Variable
        elif (_re_arg_bool.search(descr) is not None):
            type_ = '(basic:Boolean)'
        elif (_re_arg_int.search(descr) is not None):
            type_ = '(basic:Integer)'
        elif descr.lower().startswith("A list "):
            type_ = '(basic:List)'
        elif arg == 'dtype' or arg == 'name':
            type_ = '(basic:String)'
        else:
            type_ = TFOperation
        args.append((arg, descr, type_))
    if not args:
        debug.log("Didn't find 'Args:' in doc; skipping: %r" %
                  obj)
    return args


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

        f = apply_kw(self.op[0], immediate)
        self.set_output('output', Op(f, stored))


def register_operations(reg, pkg, namespace, exclude=set()):
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

        args = guess_args(op, op.__doc__, op_name=name)

        input_ports = [(arg, type_)
                       for arg, descr, type_ in args]
        reg.add_module(type(name, (AutoOperation,),
                            {'args': args, 'op': (op,),
                             '_input_ports': input_ports,
                             '__doc__': op.__doc__}),
                       namespace=namespace)
        modules.add(name)

    return modules


class AutoOptimizer(Optimizer):
    _settings = ModuleSettings(abstract=True)
    _output_ports = [('optimizer', Optimizer)]

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

        f = apply_kw(self.class_[0], immediate)
        self.set_output('optimizer', Op(f, stored))


def register_optimizers(reg):
    modules = set()

    for name in dir(tensorflow.train):
        if name == 'Optimizer' or not name.endswith('Optimizer'):
            continue

        class_ = getattr(tensorflow.train, name)
        if class_.__doc__ is None:
            debug.log("Object has no __doc__: %s" % class_)
            continue

        args = guess_args(class_, class_.__init__.__doc__)

        input_ports = [(arg, type_)
                       for arg, descr, type_ in args]
        reg.add_module(type(name, (AutoOptimizer,),
                            {'args': args, 'class_': (class_,),
                             '_input_ports': input_ports,
                             '__doc__': class_.__doc__}),
                       namespace='train|optimizer')
        modules.add(name)

    return modules


def initialize():
    from tensorflow.python.ops import standard_ops

    reg = get_module_registry()

    for module in base_modules:
        reg.add_module(module)

    # Optimizers
    reg.add_module(AutoOptimizer)

    optimizers = set(['Optimizer'])
    optimizers.update(register_optimizers(reg))

    # Operations
    reg.add_module(AutoOperation)

    ops = set(wrapped)
    ops.update(register_operations(reg, standard_ops, '', ops))
    ops.update(register_operations(reg, tensorflow.train, 'train',
                                   ops | optimizers))
    ops.update(register_operations(reg, tensorflow.nn, 'nn', ops))
    ops.update(register_operations(reg, tensorflow.image, 'image', ops))


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

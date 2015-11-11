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

import tensorflow

from vistrails.core.modules.vistrails_module import Module


class Op(object):
    def __init__(self, op, *args):
        assert all(isinstance(a, Op) for a in args)
        self.op = op
        self.args = args

    def build(self, output_map):
        if self in output_map:
            return output_map[self]
        else:
            args = [a.build(output_map) for a in self.args]
            obj = self.op(*args)
            output_map[self] = obj
            return obj


class TFOperation(Module):
    """A TensorFlow operation that will be run by Run as part of the graph.
    """
    _output_ports = [
        ('output', '(org.vistrails.vistrails.tensorflow:TFOperation)')]

    def compute(self):
        raise NotImplementedError


class Constant(TFOperation):
    """A TensorFlow operation that simply output a constant into the graph.

    Note that it is only constant from TensorFlow's point of view; it can be
    the output of another VisTrails module.
    """
    _input_ports = [('value', '(basic:List)')]

    def compute(self):
        value = self.get_input('value')
        self.set_output('output', Op(lambda: tensorflow.constant(value)))


class Cast(TFOperation):
    """Casts tensors to the specific scalar type.
    """
    _input_ports = [('value', TFOperation),
                    ('type', '(basic:String)')]

    def compute(self):
        value = self.get_input('value')
        type_ = self.get_input('type')
        self.set_output('output',
                        Op(lambda x: tensorflow.cast(x, type_), value))


class Variable(TFOperation):
    """A variable, that update its state between TensorFlow iterations.
    """
    _input_ports = [('initial_value', TFOperation)]
    _output_ports = [
        ('output', '(org.vistrails.vistrails.tensorflow:Variable)')]

    def compute(self):
        initial_value = self.get_input('initial_value')
        self.set_output('output', Op(tensorflow.Variable, initial_value))


class Assign(TFOperation):
    """Assign a value to a variable.
    """
    _input_ports = [('variable', Variable),
                    ('value', TFOperation)]

    def compute(self):
        var = self.get_input('variable')
        value = self.get_input('value')

        self.set_output(
            'output',
            Op(lambda var_, value_: var_.assign(value_), var, value))


class AssignAdd(TFOperation):
    """Assign a value to a variable.
    """
    _input_ports = [('variable', Variable),
                    ('value', TFOperation)]

    def compute(self):
        var = self.get_input('variable')
        value = self.get_input('value')

        self.set_output(
            'output',
            Op(lambda var_, value_: var_.assign_add(value_), var, value))


class RunResult(object):
    def __init__(self, session, fetch_map):
        self.session = session
        self.fetch_map = fetch_map


class Run(Module):
    """Instanciate and run a TensorFlow graph to make the results available.
    """
    _input_ports = [('output', TFOperation, {'depth': 1}),
                    ('iterations', '(basic:Integer)')]
    _output_ports = [('result', '(org.vistrails.vistrails.tensorflow:Run)')]

    def compute(self):
        outputs = self.get_input('output')
        iterations = self.get_input('iterations')

        graph = tensorflow.Graph()
        session = tensorflow.Session(graph=graph)
        with graph.as_default():
            output_map = {}
            for op in outputs:
                op.build(output_map)

            session.run(tensorflow.initialize_all_variables())

        fetches = list(output_map.itervalues())

        for i in xrange(iterations):
            session.run(fetches)

        self.set_output('result', RunResult(session, output_map))


class Fetch(Module):
    """Fetch the output of a TensorFlow operation after the graph has been run.
    """
    _input_ports = [('result', Run),
                    ('op', TFOperation)]
    _output_ports = [('value', '(basic:List)')]

    def compute(self):
        result = self.get_input('result')
        op = self.get_input('op')

        value = result.fetch_map[op].eval(result.session)

        self.set_output('value', value)

from .autogen import _modules as auto_modules

_modules = [TFOperation, Constant, Cast, Variable, Assign, AssignAdd,
            Run, Fetch] + auto_modules

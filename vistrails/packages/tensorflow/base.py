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

import itertools
import tensorflow

from vistrails.core.modules.config import ModuleSettings
from vistrails.core.modules.vistrails_module import Module, ModuleError


class Op(object):
    def __init__(self, op, args):
        """Constructor from a function and its arguments.

        This is the type actually passed on TFOperation ports. It represents a
        future TensorFlow operation; the actual operation is only created from
        the Run module, allowing multiple graphs to be used (and the same
        VisTrails-defined graph to be used from multiple Run modules).

        :type args: dict | collections.Iterable
        """
        self.op = op
        self.args = args

    def build(self, operation_map):
        """Builds the graph, by instanciating the operations recursively.
        """
        if self in operation_map:
            return operation_map[self]
        else:
            def build(op):
                if isinstance(op, list):
                    return [build(e) for e in op]
                else:
                    return op.build(operation_map)
            if isinstance(self.args, dict):
                kwargs = dict((k, build(v))
                            for k, v in self.args.iteritems())
                obj = self.op(**kwargs)
            else:
                args = [build(a) for a in self.args]
                obj = self.op(*args)
            operation_map[self] = obj
            return obj


class TFOperation(Module):
    """A TensorFlow operation that will be run by Run as part of the graph.
    """
    _settings = ModuleSettings(abstract=True)
    _output_ports = [
        ('output', '(org.vistrails.vistrails.tensorflow:TFOperation)')]

    def compute(self):
        raise NotImplementedError


class constant(TFOperation):
    """A TensorFlow operation that simply output a constant into the graph.

    Note that it is only constant from TensorFlow's point of view; it can be
    the output of another VisTrails module.
    """
    _input_ports = [('value', '(basic:Variant)')]

    def compute(self):
        value = self.get_input('value')
        self.set_output('output', Op(lambda: tensorflow.constant(value), []))


class cast(TFOperation):
    """Casts tensors to the specific scalar type.
    """
    _input_ports = [('value', TFOperation),
                    ('type', '(basic:String)')]

    def compute(self):
        value = self.get_input('value')
        type_ = self.get_input('type')
        self.set_output('output',
                        Op(lambda x: tensorflow.cast(x, type_), [value]))


class Variable(TFOperation):
    """A variable, that update its state between TensorFlow iterations.
    """
    _input_ports = [('initial_value', TFOperation)]
    _output_ports = [
        ('output', '(org.vistrails.vistrails.tensorflow:Variable)')]

    def compute(self):
        initial_value = self.get_input('initial_value')
        self.set_output('output', Op(tensorflow.Variable, [initial_value]))


class Optimizer(Module):
    _settings = ModuleSettings(abstract=True,
                               namespace='train|optimizer')


class minimize(TFOperation):
    __doc__ = tensorflow.train.Optimizer.__doc__

    _settings = ModuleSettings(namespace='train|optimizer')
    _input_ports = [('optimizer', Optimizer),
                    ('loss', TFOperation),
                    ('global_step', Variable, {'optional': True}),
                    ('var_list', Variable, {'depth': 1, 'optional': True}),
                    ('gate_gradients', '(basic:String)',
                     {'optional': True, 'entry_types': '["enum"]',
                      'values': '[["GATE_NONE", "GATE_OP", "GATE_GRAPH"]]'}),
                    ('name', '(basic:String)', {'optional': True})]

    _GATE_GRADIENTS = {'GATE_NONE': tensorflow.train.Optimizer.GATE_NONE,
                       'GATE_OP': tensorflow.train.Optimizer.GATE_OP,
                       'GATE_GRAPH': tensorflow.train.Optimizer.GATE_GRAPH}

    def compute(self):
        if self.has_input('gate_gradients'):
            gate_gradients = self._GATE_GRADIENTS[
                self.get_input('gate_gradients')]
        else:
            gate_gradients = None
        name = self.force_get_input('name')

        def output(optimizer, loss, **kwargs):
            kw = {'loss': loss, 'name': name}
            if gate_gradients is not None:
                kw['gate_gradients'] = gate_gradients
            kw.update(kwargs)
            ret = optimizer.minimize(**kw)
            return ret

        kwargs = {'optimizer': self.get_input('optimizer'),
                  'loss': self.get_input('loss')}
        if self.has_input('global_step'):
            kwargs['global_step'] = self.get_input('global_step')
        if self.has_input('var_list'):
            kwargs['var_list'] = self.get_input('var_list')
        self.set_output('output', Op(output, kwargs))


class RunResult(object):
    def __init__(self, graph, session, operation_map, fetch_map):
        self.graph = graph
        self.session = session
        self.operation_map = operation_map
        self.fetch_map = fetch_map


class FeedGenerator(Module):
    _settings = ModuleSettings(abstract=True)


class run(Module):
    """Instanciate and run a TensorFlow graph to make the results available.
    """
    _input_ports = [('output', TFOperation, {'depth': 1}),
                    ('iterations', '(basic:Integer)',
                     {'optional': True, 'defaults': '["1"]'}),
                    ('after', '(org.vistrails.vistrails.tensorflow:run)'),
                    ('feed_generator', FeedGenerator)]
    _output_ports = [('result', '(org.vistrails.vistrails.tensorflow:run)')]

    def compute(self):
        outputs = self.get_input('output')
        iterations = self.get_input('iterations')
        if self.has_input('feed_generator'):
            feeds = self.get_input('feed_generator')()
        else:
            feeds = None

        if self.has_input('after'):
            after = self.get_input('after')
            graph = after.graph
            session = after.session
            operation_map = after.operation_map
        else:
            graph = tensorflow.Graph()
            session = tensorflow.Session(graph=graph)
            operation_map = {}

        fetches = []
        with graph.as_default():
            for op in outputs:
                fetches.append(op.build(operation_map))

            if not self.has_input('after'):
                session.run(tensorflow.initialize_all_variables())

        for i in xrange(iterations):
            feed_dict = None
            if feeds is not None:
                try:
                    feed_dict = next(feeds)
                except StopIteration:
                    feeds = None
                else:
                    feed_dict = dict((operation_map[op], value)
                                     for op, value in feed_dict.iteritems())
            out = session.run(fetches, feed_dict=feed_dict)

        fetch_map = dict(itertools.izip(outputs, out))

        self.set_output('result', RunResult(graph, session, operation_map,
                                            fetch_map))


class fetch(Module):
    """Fetch the output of a TensorFlow operation after the graph has been run.
    """
    _input_ports = [('result', run),
                    ('op', TFOperation)]
    _output_ports = [('value', '(basic:List)')]

    def compute(self):
        result = self.get_input('result')
        op = self.get_input('op')

        try:
            value = result.fetch_map[op]
        except KeyError:
            raise ModuleError(self, "Requested operation was not passed in "
                                    "the list of outputs of the run module")

        self.set_output('value', value)


_modules = [TFOperation, constant, cast, Variable,
            Optimizer, minimize,
            FeedGenerator, run, fetch]

wrapped = set(['constant', 'cast', 'Variable'])

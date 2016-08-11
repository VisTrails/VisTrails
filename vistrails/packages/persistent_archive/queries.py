###############################################################################
##
## Copyright (C) 2014-2016, New York University.
## Copyright (C) 2013-2014, NYU-Poly.
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

from file_archive.parser import parse_expression

from vistrails.core.modules.basic_modules import Constant, Integer, String
from vistrails.core.modules.config import IPort, OPort
from vistrails.core.modules.vistrails_module import Module, ModuleError


def find_subclass(cls, subname):
    """Find a subclass by name.
    """
    l = [cls]
    while l:
        l2 = []
        for c in l:
            if c.__name__ == subname:
                return c
            l2 += c.__subclasses__()
        l = l2
    return None


class QueryCondition(Constant):
    """Base class for query conditions.

    This is abstract and implemented by modules Query*
    """
    _input_ports = [
            IPort('key', String)]

    @staticmethod
    def translate_to_python(c, top_class=None, text_query=True):
        try:
            i = c.index('(')
        except ValueError:
            if text_query:
                return TextQuery(c)
            raise ValueError("Invalid QueryCondition syntax")
        clsname = c[:i]
        cls = find_subclass(top_class or QueryCondition, clsname)
        if cls is not None:
            return cls(*eval(c[i+1:-1]))
        elif text_query:
            return TextQuery(c)
        else:
            raise ValueError("No such condition type: %s" % clsname)

    @staticmethod
    def translate_to_string(cond):
        return str(cond)

    @staticmethod
    def validate(cond):
        return isinstance(cond, QueryCondition)

    def __str__(self):
        raise NotImplementedError

    def __repr__(self):
        return self.__str__()

QueryCondition._output_ports = [
        OPort('value', QueryCondition)]


class TextQuery(QueryCondition):
    """A query from a text expression.
    """
    def __init__(self, text):
        self.query = text
        self.conditions = parse_expression(text)

    def __str__(self):
        return self.query


class Metadata(QueryCondition):
    """Base class for metadata pairs.

    This is abstract and implemented by modules Equal*

    This both provides a metadata pair, as the 'metadata' attribute, for
    inserting, and conditions, through the 'conditions' attribute.
    """
    _input_ports = [
            IPort('key', String),
            IPort('value', Module)]

    def __init__(self, *args):
        super(Metadata, self).__init__()

        if args:
            self.key, self.value = args
            self.set_results()
        else:
            self.key, self.value = None, None

    @staticmethod
    def translate_to_python(c):
        return QueryCondition.translate_to_python(
                c,
                top_class=Metadata, text_query=False)

    def compute(self):
        self.key = self.get_input('key')
        self.value = self.get_input('value')

        self.set_results()

    def set_results(self):
        self.conditions = {self.key: {'type': self._type, 'equal': self.value}}
        self.metadata = (self.key, self.value)
        self.set_output('value', self)

    def __str__(self):
        return '%s(%r, %r)' % (self.__class__.__name__, self.key, self.value)

    @staticmethod
    def get_widget_class():
        from .widgets import MetadataConstantWidget
        return MetadataConstantWidget

Metadata._output_ports = [
        OPort('value', Metadata)]


class EqualString(Metadata):
    """A string metadata.

    A piece of metadata with a value of type string. When used in a query,
    means "key has a value of type string equal to <value>".
    """
    _input_ports = [
            IPort('key', String),
            IPort('value', String)]

    _type = 'str'


class EqualInt(Metadata):
    """An integer metadata.

    A piece of metadata with a value of type integer. When used in a query,
    means "key has a value of type integer equal to <value>".
    """
    _input_ports = [
            IPort('key', String),
            IPort('value', Integer)]

    _type = 'int'

    def __init__(self, *args):
        if args:
            key, value = args
            assert isinstance(value, (int, long))
        Metadata.__init__(self, *args)


class IntInRange(QueryCondition):
    """An integer range condition.

    Means "key has a value of type integer which lies between <lower_bound> and
    <higher_bound>".

    Note that you can omit one of the bounds.
    """
    _input_ports = [
            IPort('key', String),
            IPort('lower_bound', Integer, optional=True),
            IPort('higher_bound', Integer, optional=True)]

    def __init__(self, *args):
        super(IntInRange, self).__init__()

        if args:
            self.key, self.low, self.high = args
            assert isinstance(self.low, (int, long))
            assert isinstance(self.high, (int, long))
            self.set_results()
        else:
            self.key, self.low, self.high = None, None, None

    def compute(self):
        self.key = self.get_input('key')
        if self.has_input('lower_bound'):
            self.low = self.get_input('lower_bound')
        if self.has_input('higher_bound'):
            self.high = self.get_input('higher_bound')
        if not (self.low is not None or self.high is not None):
            raise ModuleError(self, "No bound set")
        self.set_results()

    def set_results(self):
        dct = {}
        if self.low is not None:
            dct['gt'] = self.low
        if self.high is not None:
            dct['lt'] = self.high
        dct['type'] = 'int'

        self.conditions = {self.key: dct}
        self.set_output('value', self)

    def __str__(self):
        return '%s(%r, %r, %r)' % ('IntInRange', self.key, self.low, self.high)

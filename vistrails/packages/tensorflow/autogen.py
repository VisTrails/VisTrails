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

from .base import Op, TFOperation


# TODO: These should be auto-generated


class Multiply(TFOperation):
    _input_ports = [('a', TFOperation),
                    ('b', TFOperation)]

    def compute(self):
        a = self.get_input('a')
        b = self.get_input('b')
        self.set_output('output', Op(lambda a_, b_: a_ * b_, a, b))


class Add(TFOperation):
    _input_ports = [('a', TFOperation),
                    ('b', TFOperation)]

    def compute(self):
        a = self.get_input('a')
        b = self.get_input('b')
        self.set_output('output', Op(lambda a_, b_: a_ + b_, a, b))


class LessThan(TFOperation):
    _input_ports = [('a', TFOperation),
                    ('b', TFOperation)]

    def compute(self):
        a = self.get_input('a')
        b = self.get_input('b')
        self.set_output('output', Op(lambda a_, b_: a_ < b_, a, b))


class LessThanScalar(TFOperation):
    _input_ports = [('a', TFOperation),
                    ('b', '(basic:Float)')]

    def compute(self):
        a = self.get_input('a')
        b = self.get_input('b')
        self.set_output('output', Op(lambda a_: a_ < b, a))


class ComplexAbs(TFOperation):
    _input_ports = [('complex', TFOperation)]

    def compute(self):
        complex = self.get_input('complex')
        self.set_output('output', Op(tensorflow.complex_abs, complex))


class ZerosLike(TFOperation):
    _input_ports = [('value', TFOperation),
                    ('type', '(basic:String)')]

    def compute(self):
        value = self.get_input('value')
        type_ = self.get_input('type')
        self.set_output('output',
                        Op(lambda x: tensorflow.zeros_like(x, type_), value))


_modules = [Multiply, Add, LessThan, LessThanScalar, ComplexAbs, ZerosLike]

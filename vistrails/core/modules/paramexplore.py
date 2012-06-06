###############################################################################
##
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
##############################################################################

import traceback
from core import debug
from core.modules.basic_modules import Color



class BaseLinearInterpolator(object):
    def __init__(self, ptype, mn, mx, steps):
        self._ptype = ptype
        self._mn = mn
        self._mx = mx
        self._steps = steps
    def get_values(self):
        cast = self._ptype
        begin = self._mn
        end = self._mx
        size = self._steps
        if size<=1:
            return [begin]
        result = [cast(begin + (((end-begin)*i) / cast(size-1)))
                  for i in xrange(size)]
        return result

class IntegerLinearInterpolator(BaseLinearInterpolator):
    def __init__(self, mn, mx, steps):
        BaseLinearInterpolator.__init__(self, int, mn, mx, steps)

class FloatLinearInterpolator(BaseLinearInterpolator):
    def __init__(self, mn, mx, steps):
        BaseLinearInterpolator.__init__(self, float, mn, mx, steps)

class BaseColorInterpolator(object):

    def __init__(self, ifunc, begin, end, size):
        self._ifunc = ifunc
        self.begin = begin
        self.end = end
        self.size = size

    def get_values(self):
        if self.size <= 1:
            return [self.begin]
        result = [self._ifunc(self.begin, self.end, self.size, i)
                  for i in xrange(self.size)]
        return result

class RGBColorInterpolator(BaseColorInterpolator):

    def __init__(self, begin, end, size):
        def fun(b, e, s, i):
            b = [float(x) for x in b.split(',')]
            e = [float(x) for x in e.split(',')]
            u = float(i) / (float(s) - 1.0)
            [r,g,b] = [b[i] + u * (e[i] - b[i]) for i in [0,1,2]]
            return Color.to_string(r, g, b)
        BaseColorInterpolator.__init__(self, fun, begin, end, size)

class HSVColorInterpolator(BaseColorInterpolator):
    def __init__(self, begin, end, size):
        def fun(b, e, s, i):
            b = [float(x) for x in b.split(',')]
            e = [float(x) for x in e.split(',')]
            u = float(i) / (float(s) - 1.0)

            # Use QtGui.QColor as easy converter between rgb and hsv
            # FIXME: we should not use QtGui here
            try:
                from PyQt4 import QtGui
            except:
                debug.critical("HSVColorInterpolator cannot be used without QtGui")
                return 
            color_b = QtGui.QColor(int(b[0] * 255),
                                   int(b[1] * 255),
                                   int(b[2] * 255))
            color_e = QtGui.QColor(int(e[0] * 255),
                                   int(e[1] * 255),
                                   int(e[2] * 255))

            b_hsv = [color_b.hueF(), color_b.saturationF(), color_b.valueF()]
            e_hsv = [color_e.hueF(), color_e.saturationF(), color_e.valueF()]

            [new_h, new_s, new_v] = [b_hsv[i] + u * (e_hsv[i] - b_hsv[i])
                                     for i in [0,1,2]]
            new_color = QtGui.QColor()
            new_color.setHsvF(new_h, new_s, new_v)
            return Color.to_string(new_color.redF(),
                                   new_color.greenF(),
                                   new_color.blueF())
        BaseColorInterpolator.__init__(self, fun, begin, end, size)

class UserDefinedFunctionInterpolator(object):
    def __init__(self, ptype, code, steps):
        self._ptype = ptype
        self._code = code
        self._steps = steps
    def get_values(self):
        def get():
            import code
            values = []
            d = {}
            try:
                exec(self._code) in {}, d
            except Exception, e:
                return [self._ptype.default_value] * self._steps
            def evaluate(i):
                try:
                    v = d['value'](i)
                    if v == None:
                        return self._ptype.default_value
                    return v
                except Exception, e:
                    return str(e)
            return [evaluate(i) for i in xrange(self._steps)]
        result = get()
        
        if not all(self._ptype.validate(x) for x in result):
            try:
                # FIXME: We should throw an error here instead
                from gui.utils import show_warning
                show_warning('Failed Validation',
                             'One of the <i>%s</i>\'s user defined '
                             'functions has failed validation, '
                             'which usually means it generated a '
                             'value of a type different '
                             'than that specified by the '
                             'parameter. Parameter Exploration '
                             'aborted.' % self._ptype)
            except:
                pass
            return None
        return result

################################################################################

import unittest

class TestLinearInterpolator(unittest.TestCase):

    def test_int(self):
        x = BaseLinearInterpolator(int, 0, 999, 1000)
        assert x.get_values() == range(1000)

    def test_float(self):
        # test the property that differences in value must be linearly
        # proportional to differences in index for a linear interpolation
        import random
        s = random.randint(4, 10000)
        v1 = random.random()
        v2 = random.random()
        mn = min(v1, v2)
        mx = max(v1, v2)
        x = BaseLinearInterpolator(float, mn, mx, s).get_values()
        v1 = random.randint(0, s-1)
        v2 = 0
        while v2 == v1:
            v2 = random.randint(0, s-1)
        v3 = random.randint(0, s-1)
        v4 = 0
        while v3 == v4:
            v4 = random.randint(0, s-1)
        r1 = (v2 - v1) / (x[v2] - x[v1])
        r2 = (v4 - v3) / (x[v4] - x[v3])
        assert abs(r1 - r2) < 1e-6        

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

from vistrails.core import debug
from vistrails.core.modules.basic_modules import Color
from vistrails.core.utils.color import rgb2hsv, hsv2rgb


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
        if size <= 1:
            return [begin]
        result = [cast(begin + ((end - begin) * i / cast(size - 1)))
                  for i in xrange(size)]
        return result


class IntegerLinearInterpolator(BaseLinearInterpolator):
    def __init__(self, mn, mx, steps):
        BaseLinearInterpolator.__init__(self, int, mn, mx, steps)


class FloatLinearInterpolator(BaseLinearInterpolator):
    def __init__(self, mn, mx, steps):
        BaseLinearInterpolator.__init__(self, float, mn, mx, steps)


###############################################################################

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
        BaseColorInterpolator.__init__(self, None, begin, end, size)

    def get_values(self):
        b = [float(x) for x in self.begin.split(',')]
        e = [float(x) for x in self.end.split(',')]

        b_hsv = rgb2hsv(b)
        e_hsv = rgb2hsv(e)

        size_fact = 1.0 / (float(self.size) - 1.0)

        # Ignore the undefined hues
        if b_hsv[0] is None:
            b_hsv[0] = e_hsv[0]
        elif e_hsv[0] is None:
            e_hsv[0] = b_hsv[0]

        if b_hsv[0] is None:
            # There is no hue at all!
            b_hsv[0] = e_hsv[0] = 0.0 # unused value
            hue_step = 0.0
        else:
            # Compute hue
            # Because the hue is an angle, there is two ways to interpolate it;
            # choose the shorter path
            diff1 = e_hsv[0] - b_hsv[0]
            diff2 = e_hsv[0] - b_hsv[0] + 360.0
            if diff2 >= 360.0:
                diff2 -= 360.0
            assert 0.0 <= diff2 < 360.0
            if abs(diff1) < abs(diff2):
                hue_step = diff1
            else:
                hue_step = diff2

        colors = []
        for i in xrange(self.size):
            u = i * size_fact
            hue = b_hsv[0] + u * hue_step
            if hue < 0.0:
                hue += 360.0
            elif hue > 360.0:
                hue -= 360.0
            colors.append(Color.to_string(*hsv2rgb((
                    hue,
                    b_hsv[1] + u * (e_hsv[1] - b_hsv[1]),
                    b_hsv[2] + u * (e_hsv[2] - b_hsv[2])
                ))))

        return colors


###############################################################################

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
                    if v is None:
                        return self._ptype.default_value
                    return v
                except Exception, e:
                    return debug.format_exception(e)
            return [evaluate(i) for i in xrange(self._steps)]
        result = get()

        if not all(self._ptype.validate(x) for x in result):
            # FIXME: We should throw an error here instead
            debug.critical(
                    'Failed Validation',
                    'One of the <i>%s</i>\'s user defined functions has '
                    'failed validation, which usually means it generated a '
                    'value of a type different than that specified by the '
                    'parameter. Parameter Exploration aborted.' % self._ptype)
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
        s = random.randint(40, 1000)
        v1 = random.random()
        v2 = random.random()
        # avoid very small differences
        while abs(v2 - v1) < 0.01:
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

        self.assertTrue(abs(r1 - r2) < 1e-6, "r1=%.20f\nr2=%.20f"%(r1,r2))

class TestColorInterpolation(unittest.TestCase):
    def test_rgb_interpolation(self):
        interp = RGBColorInterpolator('0.5,0.7,0.8', '0.5,0.9,0.3', 6)
        self.assertEqual(interp.get_values(),
                         ['0.5,0.7,0.8', '0.5,0.74,0.7', '0.5,0.78,0.6',
                          '0.5,0.82,0.5', '0.5,0.86,0.4', '0.5,0.9,0.3'])

    def test_hsv_interpolation(self):
        tests = [((120.0, 0.8, 0.2), (170.0, 0.5, 0.2),
                  [(120.0, 0.8, 0.2), (130.0, 0.74, 0.2), (140.0, 0.68, 0.2),
                   (150.0, 0.62, 0.2), (160.0, 0.56, 0.2), (170.0, 0.5, 0.2)]),
                 ((260.0, 0.2, 0.7), (40.0, 0.8, 0.1),
                  [(260.0, 0.2, 0.7), (288.0, 0.32, 0.58), (316.0, 0.44, 0.46),
                   (344.0, 0.56, 0.34), (12.0, 0.68, 0.22), (40.0, 0.8, 0.1)])]

        for b, e, expected in tests:
            b = hsv2rgb(b)
            e = hsv2rgb(e)
            interp = HSVColorInterpolator(','.join(str(c) for c in b),
                                          ','.join(str(c) for c in e),
                                          6)
            for i, color in enumerate(interp.get_values()):
                color = [float(e) for e in color.split(',')]
                color = rgb2hsv(color)
                self.assertAlmostEqual(color[0], expected[i][0], delta=0.2)
                self.assertAlmostEqual(color[1], expected[i][1], delta=0.005)
                self.assertAlmostEqual(color[2], expected[i][2], delta=0.005)

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
"""enum helps create enumeration classes.

"""
from __future__ import division

from itertools import izip

def enum(className, enumValues, doc = None):
    """enum(className: str, enumValues: [str], doc = None) -> class.
    Creates a new enumeration class. For example:

    >>> import enum
    >>> Colors = enum.enum('Colors',
                           ['Red', 'Green', 'Blue'],
                           "Enumeration of primary colors")

    will create a class that can be used as follows:

    >>> x = Colors.Red
    >>> y = Colors.Blue
    >>> x == y
    False
    >>> z = Colors.REd
    Traceback (most recent call last):
      File "<stdin>", line 1, in ?
    AttributeError: type object 'Colors' has no attribute 'REd'
    >>> z = Colors.Red
    >>> z == x
    True
    >>> x.__doc__
    'Enumeration of primary colors'
    
    """                  
    def __init__(self, v):
        self.__v = v
        
    def str(v):
        return the_enum.st[v]
    
    def __str__(self):
        return the_enum.str(self.__v)
    
    def __repr__(self):
        return className + "." + the_enum.str(self.__v)
    
    def __eq__(self, other):
        try:
            return (self.__v == other.__v and 
                    self.__className == other.__className)
        except AttributeError:
            return False

    def __ne__(self, other):
        return not (self == other)

    def from_str(v):
        return the_enum(the_enum.st.index(v))

    the_enum = type(className, (object, ),
                   {'__init__': __init__,
                    'str': staticmethod(str),
                    'from_str': staticmethod(from_str),
                    '__str__': __str__,
                    '__repr__': __repr__,
                    'st': enumValues,
                    '__className': className,
                    '__eq__': __eq__,
                    '__ne__': __ne__,
                    '__doc__': doc,
                    '__hash__': lambda self: self.__v})
    for (v, x) in izip(enumValues, xrange(len(enumValues))):
        setattr(the_enum, v, the_enum(x))
    return the_enum

################################################################################

import unittest

class TestEnum(unittest.TestCase):

    def test1(self):
        e1 = enum('e1', ['v1', 'v2', 'v3'])
        self.assertEquals(e1.v1, e1.v1)
        self.assertEquals(e1.v2, e1.v2)
        self.assertEquals(e1.v3, e1.v3)
        self.assertNotEquals(e1.v1, e1.v2)
        self.assertNotEquals(e1.v1, e1.v3)
        self.assertNotEquals(e1.v2, e1.v3)
        self.assertNotEquals(e1.v2, e1.v1)
        self.assertNotEquals(e1.v3, e1.v1)
        self.assertNotEquals(e1.v3, e1.v2)

    def test2(self):
        e1 = enum('e1', ['v1', 'v2', 'v3'])
        e2 = enum('e1', ['v1', 'v2', 'v3'])
        self.assertEquals(e1.v1, e2.v1)

    def test3(self):
        e1 = enum('e1', ['v1', 'v2', 'v3'])
        self.assertNotEquals(e1.v1, 5)

    def test4(self):
        e2 = enum('e1', ['v1', 'v2', 'v3'])
        x = e2.v2
        import copy
        y = copy.copy(x)
        self.assertEquals(x, y)

if __name__ == '__main__':
    unittest.main()

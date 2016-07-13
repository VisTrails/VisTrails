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
"""Simple stack data structure."""

###############################################################################

from __future__ import division

class EmptyStack(Exception):
    pass


class Stack(object):

    def __init__(self):
        object.__init__(self)
        self.__cell = []
        self.__size = 0

    def top(self):
        """Returns the top of the stack."""
        if not self.__cell:
            raise EmptyStack()
        else:
            return self.__cell[0]

    def push(self, obj):
        """Pushes an element onto the stack."""
        self.__cell = [obj, self.__cell]
        self.__size += 1

    def pop(self):
        """Pops the top off of the stack."""
        if not self.__cell:
            raise EmptyStack()
        else:
            self.__cell = self.__cell[1]
            self.__size -= 1

    def __len__(self):
        return self.__size

    def __get_size(self):
        return self.__size

    size = property(__get_size, doc="The size of the stack.")

###############################################################################

import unittest

class TestStack(unittest.TestCase):

    def test_basic(self):
        s = Stack()
        self.assertEquals(s.size, 0)
        s.push(10)
        self.assertEquals(s.top(), 10)
        self.assertEquals(len(s), 1)
        s.pop()
        self.assertEquals(len(s), 0)
        self.assertEquals(0, s.size)

    def test_pop_empty_raises(self):
        s = Stack()
        self.assertRaises(EmptyStack, s.pop)

    def test_top_empty_raises(self):
        s = Stack()
        self.assertRaises(EmptyStack, s.top)

if __name__ == '__main__':
    unittest.main()

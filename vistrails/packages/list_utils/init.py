###############################################################################
##
## Copyright (C) 2014-2017, New York University.
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

from vistrails.core.modules.config import IPort, OPort
from vistrails.core.modules.vistrails_module import Module, ModuleError


class Concat(Module):
    """Concatenate two lists.
    """
    _input_ports = [IPort('left', 'basic:Variant', depth=1),
                    IPort('right', 'basic:Variant', depth=1)]
    _output_ports = [OPort('value', 'basic:Variant', depth=1)]

    def compute(self):
        out = self.get_input('left') + self.get_input('right')
        self.set_output('value', out)


class Flatten(Module):
    """Flattens a list by one level.

    Examples:

    - `[[1, 2, 3]] -> [1, 2, 3]`
    - `[[1, 2], [3, 4]] -> [1, 2, 3, 4]`
    - `[[[1, 2], [3]], [[4, 5], [6]]]` -> `[[1, 2, 3], [4, 5]]`
    """
    _input_ports = [IPort('value', 'basic:Variant', depth=2)]
    _output_ports = [OPort('value', 'basic:Variant', depth=1)]

    def compute(self):
        it = iter(self.get_input('value'))
        try:
            value = next(it)
        except StopIteration:
            value = []
        else:
            for v in it:
                value += v
        self.set_output('value', value)


class UnlistOne(Module):
    """Unpacks a list into its element, if it only has one.

    If the list has more than one element, errors out.
    """
    _input_ports = [IPort('list', 'basic:Variant', depth=1)]
    _output_ports = [OPort('element', 'basic:Variant')]

    def compute(self):
        list_ = self.get_input('list')
        if len(list_) != 1:
            raise ModuleError(self, "Length is %d != 1" % len(list_))
        self.set_output('element', list_[0])


_modules = [Concat, Flatten, UnlistOne]

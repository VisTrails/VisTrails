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

from vistrails.core.modules.basic_modules import Color, Path, PathObject
from vistrails.core.utils import InstanceObject

#### Automatic conversion between some vistrail and python types ####
def convert_input_param(value, _type):
    if issubclass(_type, Path):
        return value.name
    if issubclass(_type, Color):
        return value.tuple
    return value

def convert_output_param(value, _type):
    if issubclass(_type, Path):
        return PathObject(value)
    if issubclass(_type, Color):
        return InstanceObject(tuple=value)
    return value

def convert_input(value, signature):
    if len(signature) == 1:
        return convert_input_param(value, signature[0][0])
    return tuple([convert_input_param(v, t[0]) for v, t in zip(value, signature)])

def convert_output(value, signature):
    if len(signature) == 1:
        return convert_output_param(value, signature[0][0])
    return tuple([convert_output_param(v, t[0]) for v, t in zip(value, signature)])


def get_input_spec(cls, name):
    """ Get named input spec from self or superclass
    """
    klasses = iter(cls.__mro__)
    base = cls
    while base and hasattr(base, '_input_spec_table'):
        if name in base._input_spec_table:
            return base._input_spec_table[name]
        base = klasses.next()
    return None

def get_output_spec(cls, name):
    """ Get named output spec from self or superclass
    """
    klasses = iter(cls.__mro__)
    base = cls
    while base and hasattr(base, '_output_spec_table'):
        if name in base._output_spec_table:
            return base._output_spec_table[name]
        base = klasses.next()
    return None

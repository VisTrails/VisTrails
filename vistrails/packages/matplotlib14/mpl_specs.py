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

import inspect
import mixins

from vistrails.core.wrapper.specs import SpecList, FunctionSpec, \
    FunctionInputPortSpec, FunctionOutputPortSpec


def capfirst(s):
    return s[0].upper() + s[1:]


######### MIXIN CODE ###########

_mixin_classes = None


def load_mixin_classes():
    return dict(inspect.getmembers(mixins, inspect.isclass))


def get_mixin_classes():
    global _mixin_classes
    if _mixin_classes is None:
        _mixin_classes = load_mixin_classes()
    return _mixin_classes


######### MATPLOTLIB FUNCTION SPEC ###########


class PropertyMixin:
    def is_property(self):
        return self.port_type == "__property__"

    def get_property_type(self):
        return "Mpl%sProperties" % \
            capfirst(self.property_type.rsplit('.', 1)[1])


class MPLInputPortSpec(PropertyMixin, FunctionInputPortSpec):
    attrs = {"constructor_arg": (False, False, True), # Add as constructor arg
             "not_setp": (False, False, True),        # Should we not set properties
             "property_type": "",
             "translations": (None, True, True)}      # Translation function(s) (dict or string)
    attrs.update(FunctionInputPortSpec.attrs)


class MPLOutputPortSpec(PropertyMixin, FunctionOutputPortSpec):
    attrs = {"compute_name": "",
             "property_key": None,
             "plural": (False, False, True),
             "compute_parent": "",
             "property_type": "",
             }
    attrs.update(FunctionOutputPortSpec.attrs)


class MPLFunctionSpec(FunctionSpec):
    """ Specification for wrapping a python function
    """
    InputSpecType = MPLInputPortSpec
    OutputSpecType = MPLOutputPortSpec

    def __init__(self, **kwargs):
        FunctionSpec.__init__(self, **kwargs)
        self._mixin_class = None
        self._mixin_functions = None

    def get_input_args(self):
        args = [ps for ps in self.input_port_specs if ps.in_args]
        args.sort(key=lambda ps: ps.arg_pos)
        if len(args) > 1 and len(args) != (args[-1].arg_pos + 1):
            raise ValueError("Argument positions are numbered incorrectly")
        return args

    def get_mixin_name(self):
        return self.module_name + "Mixin"

    def get_returned_output_port_specs(self):
        return [ps for ps in self.output_port_specs
                if ps.property_key is not None]

    def has_mixin(self):
        if self._mixin_class is None:
            mixin_classes = get_mixin_classes()
            if self.get_mixin_name() in mixin_classes:
                self._mixin_class = mixin_classes[self.get_mixin_name()]
            else:
                self._mixin_class = False
        return (self._mixin_class is not False)

    def get_mixin_function(self, f_name):
        if not self.has_mixin():
            return None
        if self._mixin_functions is None:
            self._mixin_functions = \
                dict(inspect.getmembers(self._mixin_class, inspect.ismethod))
        if f_name in self._mixin_functions:
            s = inspect.getsource(self._mixin_functions[f_name])
            return s[s.find(':')+1:].strip()
        return None

    def get_compute_before(self):
        return self.get_mixin_function("compute_before")

    def get_compute_inner(self):
        return self.get_mixin_function("compute_inner")

    def get_compute_after(self):
        return self.get_mixin_function("compute_after")

    def get_init(self):
        return self.get_mixin_function("__init__")


MPLSpecList = SpecList



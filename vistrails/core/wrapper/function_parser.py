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
"""
methods for parsing a function signature and generating a partial
module specification
"""


from types import BuiltinFunctionType

import inspect

from specs import FunctionSpec, FunctionInputPortSpec, FunctionOutputPortSpec


def get_value_and_type(s):
    try:
        val = eval(s)
        if isinstance(val, type) or isinstance(val, BuiltinFunctionType):
            return (None, None)
    except Exception:
        val = s
    port_type = get_type_from_val(val)
    return (val, port_type)


def get_type_from_val(val):
    if isinstance(val, float):
        return "basic:Float"
    elif isinstance(val, bool):
        return "basic:Boolean"
    elif isinstance(val, (int, long)):
        return "basic:Integer"
    elif isinstance(val, basestring):
        return "basic:String"
    elif isinstance(val, list) or isinstance(val, tuple):
        return "basic:List"
    return None


def get_port_specs_from_signature(f):
    attributes, args, kwargs, defaults = inspect.getargspec(f)

    input_specs = []
    default_offset = len(attributes) - len(defaults)
    for i, attr in enumerate(attributes):
        if i < default_offset:
            port_type = 'basic:Variant'
            default = None
            # No default means it is required and usually used with connections
            min_conns = 1
            show_port = True
        else:
            default, port_type = \
                get_value_and_type(defaults[i - default_offset])
            if port_type is None:
                port_type = 'basic:Variant'
            min_conns = 0
            show_port = False

        print attr, port_type, i, [default], min_conns, show_port

        input_spec = FunctionInputPortSpec(attr,
                                           port_type=port_type,
                                           in_args=True,
                                           arg_pos=i,
                                           defaults=[default] if default else None,
                                           min_conns=min_conns,
                                           show_port=show_port,
                                           sort_key=i)
        input_specs.append(input_spec)
    return input_specs


def get_spec_from_function(f, name=None, code_ref=None):

    if isinstance(f, basestring):
        if name is None:
            name = f.rsplit('.', 1)[-1]
        if code_ref is None:
            code_ref = f
    else:
        if name is None:
            name = f.__name__
        if code_ref is None:
            code_ref = f.__module__ + '.' + f.__name__

    # parse function signature
    input_specs = get_port_specs_from_signature(f)

    # Set output by default as a Variant port named 'value'
    output_spec = FunctionOutputPortSpec('value',
                                         port_type='basic:Variant',
                                         show_port=True)
    spec = FunctionSpec(module_name=name,
                        code_ref=code_ref,
                        docstring=f.__doc__ or '',
                        output_type='object',
                        input_port_specs=input_specs,
                        output_port_specs=[output_spec])
    return spec

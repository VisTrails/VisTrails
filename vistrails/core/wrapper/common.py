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

from string import Template


def convert_port(port, value, patches, direction):
    """ translate port values between vistrail and native types
    port - PortSpec
    value - port value
    translations - dict(port_type: translator_function)
    """
    port_types = port.get_port_type()
    if isinstance(port_types, list):
        return value
    patch_name = '%s#%s' % (port_types, direction)
    if patch_name not in patches:
        return value
    patch = patches[patch_name]
    code = Template(patch).substitute(input='value',output='output')
    output = None
    locals_ = locals()
    exec code + '\n' in locals_, locals_
    if locals_.get('output') is not None:
        output = locals_['output']
    return output


def get_patches(cls, method_name):
    """ Get all named patches in self and superclass for a method_name
    """
    klasses = iter(cls.__mro__)
    base = cls
    patches = []
    while base and hasattr(base, '_module_spec'):
        spec = base._module_spec
        if spec.patches and method_name in spec.patches:
            for patch in spec.patches[method_name]:
                if patch not in patches:
                    patches.insert(0, patch)
        base = klasses.next()
    return patches

def convert_port_script(code, port, port_name, translations, port_type):
    """ create port translation code between vistrail and native types
    code - string
    port - PortSpec
    translations - dict(port_type: translator_function)
    port_type - 'input' or 'output'
    """
    if port_type == 'input':
        translations = translations['input_script']
        conv_name = 'input_t'
    else:
        translations = translations['output_script']
        conv_name = 'output_t'
    port_types = port.get_port_type()
    if port_types in translations:
        # FIXME: only add once and not both input/output
        code.append(translations[port_types])
        code.append('%s = %s(%s)' % (port_name, conv_name, port.name))


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

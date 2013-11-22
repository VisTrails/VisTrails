###############################################################################
##
## Copyright (C) 2011-2013, NYU-Poly.
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
###############################################################################

from itertools import izip

from .errors import IncompleteImplementation, InvalidOutput, \
    ModuleBreakpoint, ModuleError, ModuleErrors, ModuleSuspended, \
    NeedsInputPort
from .module import Module, ModuleConnector, new_module
from .parallel import parallelizable


###############################################################################

class NotCacheable(object):
    """This Mixin marks a Module as not being cacheable.

    It will get reexecuted every time even if it gets the exact same input on
    its ports.
    """
    def is_cacheable(self):
        return False


################################################################################

class Converter(Module):
    """Base class for automatic conversion modules.

    Modules that subclass Converter will be inserted automatically when
    connecting incompatible ports, if possible.

    You must override the 'in_value' and 'out_value' ports by providing the
    types your module actually matches.

    Alternatively, you can override the classmethod can_convert() to provide
    a custom condition.
    """
    @classmethod
    def can_convert(cls, sub_descs, super_descs):
        from vistrails.core.modules.module_registry import get_module_registry
        from vistrails.core.system import get_vistrails_basic_pkg_id
        reg = get_module_registry()
        basic_pkg = get_vistrails_basic_pkg_id()
        variant_desc = reg.get_descriptor_by_name(basic_pkg, 'Variant')
        desc = reg.get_descriptor(cls)

        def check_types(sub_descs, super_descs):
            for (sub_desc, super_desc) in izip(sub_descs, super_descs):
                if (sub_desc == variant_desc or super_desc == variant_desc):
                    continue
                if not reg.is_descriptor_subclass(sub_desc, super_desc):
                    return False
            return True

        in_port = reg.get_port_spec_from_descriptor(
                desc,
                'in_value', 'input')
        if (len(sub_descs) != len(in_port.descriptors()) or
                not check_types(sub_descs, in_port.descriptors())):
            return False
        out_port = reg.get_port_spec_from_descriptor(
                desc,
                'out_value', 'output')
        if (len(out_port.descriptors()) != len(super_descs)
                or not check_types(out_port.descriptors(), super_descs)):
            return False

        return True

    def compute(self):
        raise NotImplementedError

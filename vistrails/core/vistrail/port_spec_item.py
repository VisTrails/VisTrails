###############################################################################
##
## Copyright (C) 2006-2012, University of Utah. 
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

import copy
from db.domain import DBPortSpecItem

class PortSpecItem(DBPortSpecItem):

    ##########################################################################
    # Constructors and copy

    def __init__(self, *args, **kwargs):
        if "sigstring" in kwargs:
            sigstring = kwargs["sigstring"]
            sigs = sigstring.split(":", 2)
            del kwargs["sigstring"]
            if len(sigs) < 2:
                raise Exception("sigstring '%s' must contain both package"
                                " identifier and module name" % sigstring)
            if "package" not in kwargs:
                kwargs["package"] = sigs[0]
            if "module" not in kwargs:
                kwargs["module"] = sigs[1]
            if "namesapce" not in kwargs and len(sigs) > 2:
                kwargs["namespace"] = sigs[2]
        if "values" in kwargs:
            if not isinstance(kwargs["values"], basestring):
                kwargs["values"] = str(kwargs["values"])
        if 'id' not in kwargs:
            kwargs['id'] = -1
        DBPortSpecItem.__init__(self, *args, **kwargs)
        self.set_defaults()

    def set_defaults(self, other=None):
        if other is None:
            self._values = None
            self._sigstring = None
            self._descriptor = None
        else:
            self._values = copy.copy(other._values)
            self._sigstring = other._sigstring
            self._descriptor = other._descriptor

    def __copy__(self):
        """__copy__() -> PortSpecItem - Returns a clone of itself"""
        return self.do_copy()

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBPortSpecItem.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = PortSpecItem
        cp.set_defaults(self)
        return cp

    @staticmethod
    def convert(_portSpecItem):
        if _portSpecItem.__class__ == PortSpecItem:
            return
	_portSpecItem.__class__ = PortSpecItem
        _portSpecItem.set_defaults()

    id = DBPortSpecItem.db_id
    pos = DBPortSpecItem.db_pos
    label = DBPortSpecItem.db_label
    default = DBPortSpecItem.db_default
    entry_type = DBPortSpecItem.db_entry_type

    def _get_module(self):
        return self.db_module
    def _set_module(self, module):
        if self.db_module != module:
            self._sigstring = None
            self._descriptor = None
            self.db_module = module
    module = property(_get_module, _set_module)

    def _get_package(self):
        return self.db_package
    def _set_package(self, package):
        if self.db_package != package:
            self._sigstring = None
            self._descriptor = None
            self.db_package = package
    package = property(_get_package, _set_package)
    
    def _get_namespace(self):
        return self.db_namespace
    def _set_namespace(self, ns):
        if self.db_namespace != ns:
            self._sigstring = None
            self._descriptor = None
            self.db_namespace = ns
    namespace = property(_get_namespace, _set_namespace)

    def _get_sigstring(self):
        if self._sigstring is None:
            self._sigstring = \
                ("%s:%s:%s" % (self.package, self.module, self.namespace) 
                 if self.namespace else "%s:%s" % (self.package, self.module))
        return self._sigstring
    sigstring = property(_get_sigstring)

    def _get_descriptor(self):
        if self._descriptor is None:
            from core.modules.module_registry import get_module_registry
            reg = get_module_registry()
            if self.package is None:
                self._descriptor = \
                    reg.get_descriptor_from_name_only(self.module)
                self.db_package = self._descriptor.identifier
                self.db_namespace = self._descriptor.namespace
            else:
                self._descriptor = reg.get_descriptor_by_name(self.package,
                                                              self.module,
                                                              self.namespace)
        return self._descriptor
    descriptor = property(_get_descriptor)

    def _get_values(self):
        if self._values is None:
            # don't use eval here...
            self._values = eval(self.db_values)
        return self._values
    def _set_values(self, values):
        if not isinstance(values, basestring):
            self._values = values
            self.db_values = str(values)
        else:
            self.db_values = values
            # don't use eval here...
            self._values = eval(values)
    values = property(_get_values, _set_values)


################################################################################
# Testing

import unittest
from db.domain import IdScope

class TestPortSpecItem(unittest.TestCase):
    def create_port_spec_item(self):
        return PortSpecItem(id=0, pos=0, 
                            module="String", 
                            package="edu.utah.sci.vistrails.basic", 
                            label="testLabel", 
                            default="abc", 
                            values=["abc", "def", "ghi"], 
                            entry_type="enum")

    def test_change_descriptor(self):
        psi = self.create_port_spec_item()
        d1 = psi.descriptor
        s1 = psi.sigstring
        psi.module = "Integer"
        d2 = psi.descriptor
        s2 = psi.sigstring
        assert(d1 != d2)
        assert(s1 != s2)

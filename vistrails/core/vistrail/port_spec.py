###############################################################################
##
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

import __builtin__
from itertools import izip

from core.data_structures.bijectivedict import Bidict
from core.utils import enum, VistrailsInternalError
from db.domain import DBPortSpec

################################################################################

PortEndPoint = enum('PortEndPoint',
                    ['Invalid', 'Source', 'Destination'])

################################################################################

class PortSpec(DBPortSpec):

    port_type_map = Bidict([('input', 'destination'),
                            ('output', 'source'),
                            ('invalid', 'invalid')])
    end_point_map = Bidict([('source', PortEndPoint.Source),
                            ('destination', PortEndPoint.Destination),
                            ('invalid', PortEndPoint.Invalid)])

    ##########################################################################
    # Constructors and copy

    def __init__(self, *args, **kwargs):
        signature = None
        if 'signature' in kwargs:
            signature = kwargs['signature']
            del kwargs['signature']
        if 'optional' not in kwargs:
            kwargs['optional'] = 0 # False
        elif type(kwargs['optional']) != type(0):
            if type(kwargs['optional']) == type(True):
                if kwargs['optional']:
                    kwargs['optional'] = 1
                else:
                    kwargs['optional'] = 0
            else:
                raise VistrailsInternalError("Cannot parse 'optional' kw "
                                             "-- must be an int or bool")
        if 'sort_key' not in kwargs:
            kwargs['sort_key'] = -1
        if 'id' not in kwargs:
            kwargs['id'] = -1
        if 'tooltip' in kwargs:
            self._tooltip = kwargs['tooltip']
            del kwargs['tooltip']
        else:
            self._tooltip = None
        DBPortSpec.__init__(self, *args, **kwargs)

        self._entries = None
        self._descriptors = None
        self._short_sigstring = None
        self._labels = None
        self._defaults = None
        if signature is not None:
            self.create_entries(signature)
        if not self.sigstring and self._entries is not None:
            # create sigstring from entries
            self.create_sigstring_and_descriptors()
# DAKOOP: removed this---we will check in module_registry and pipeline 
# validation, this way, we can let errors go all the way up
#         elif self._entries is None and self.sigstring:
#             # create entries from sigstring
#             self.create_entries_and_descriptors()
#         else:
#             raise VistrailsInternalError("Need to specify signature or "
#                                          "sigstring to create PortSpec")
        if self._entries is not None and self._tooltip is None:
            self.create_tooltip()
        self.is_valid = True

    def __copy__(self):
        return PortSpec.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBPortSpec.do_copy(self, new_ids, id_scope, id_remap)
        cp._entries = copy.copy(self._entries)
        cp._descriptors = copy.copy(self._descriptors)
        cp._short_sigstring = self._short_sigstring
        cp._labels = self._labels
        cp._defaults = self._defaults
        cp._tooltip = self._tooltip
        cp.is_valid = self.is_valid
        cp.__class__ = PortSpec
        if cp._entries is not None:
            cp.create_tooltip()
        return cp

    @staticmethod
    def convert(_port_spec):
        from core.modules.module_registry import module_registry_loaded, \
            ModuleRegistryException
        if _port_spec.__class__ == PortSpec:
            return
        _port_spec.__class__ = PortSpec
        _port_spec._entries = None
        _port_spec._descriptors = None
        _port_spec._short_sigstring = None
        _port_spec._labels = None
        _port_spec._defaults = None
        _port_spec._tooltip = None
        _port_spec.is_valid = True
        # FIXME probably can just let validation take care of this...
        if module_registry_loaded():
            try:
                _port_spec.create_entries_and_descriptors()
                _port_spec.create_tooltip()
            except ModuleRegistryException, e:
                _port_spec._descriptors = None
                _port_spec._entries = None
                # raise e
        else:
            _port_spec._descriptors = None
            _port_spec._entries = None

    @staticmethod
    def from_sigstring(sigstring):
        """from_sig(sigstring: string) -> PortSpec

        Returns a portspec from the given sigstring.

        """
        return PortSpec(sigstring=sigstring)

    ##########################################################################
    # Properties

    id = DBPortSpec.db_id
    name = DBPortSpec.db_name
    type = DBPortSpec.db_type
    optional = DBPortSpec.db_optional
    sort_key = DBPortSpec.db_sort_key
    sigstring = DBPortSpec.db_sigstring

    def _get_labels(self):
        if self._labels is None:
            if not self.db_labels:
                self._labels = None
            else:
                labels = eval(self.db_labels)
                if type(labels) == type(''):
                    labels = (labels,)
                else:
                    try:
                        it = iter(labels)
                    except TypeError:
                        labels = (labels,)
                self._labels = labels
        return self._labels
    labels = property(_get_labels)

    def _get_defaults(self):
        if self._defaults is None:
            if not self.db_defaults:
                self._defaults = None
            else:
                defaults = eval(self.db_defaults)
                if type(defaults) == type(''):
                    defaults = (defaults,)
                else:
                    try:
                        it = iter(defaults)
                    except TypeError:
                        defaults = (defaults,)
                self._defaults = defaults
        return self._defaults
    defaults = property(_get_defaults)
    
    def _get_short_sigstring(self):
        if self._short_sigstring is None:
            self.create_tooltip()
        return self._short_sigstring
    short_sigstring = property(_get_short_sigstring)

    def _get_signature(self):
        if self._entries is None:
            self.create_entries_and_descriptors()
        if self._entries is not None:
            return self._entries
        return None
    signature = property(_get_signature)

    def toolTip(self):
        if self._tooltip is None:
            self.create_tooltip()
        return self._tooltip

    ##########################################################################
    # Methods

    def create_entries(self, signature):
        # This is reasonably messy code. The intent is that a
        # signature given by the user in a call like this
        # add_input_port(module, name, signature) should be one of the
        # following:

        # type only: add_input_port(_, _, Float)
        # type plus description: add_input_port(_, _, (Float, 'radius'))

        # multiple parameters, where each parameter can be either of the above:
        # add_input_port(_, _, [Float, (Integer, 'count')])

        from core.modules.module_registry import get_module_registry
        registry = get_module_registry()
        self._entries = []
        def canonicalize(sig_item):
            if type(sig_item) == __builtin__.tuple:
                # assert len(sig_item) == 2
                # assert type(sig_item[0]) == __builtin__.type
                # assert type(sig_item[1]) == __builtin__.str
                return sig_item
            elif type(sig_item) == __builtin__.list:
                return (registry.get_descriptor_by_name('edu.utah.sci.vistrails.basic',
                                                        'List').module,
                        '<no description>')
            else:
                # type(sig_item) == __builtin__.type:
                return (sig_item, '<no description>')

        # def _add_entry(sig_item):
        if type(signature) != __builtin__.list:
            self._entries.append(canonicalize(signature))
        else:
            self._entries.extend(canonicalize(item) for item in signature)

    def create_sigstring_and_descriptors(self):
        """create_sigstring() -> None

        Creates string with the signature of the portspec.

        """
        from core.modules.module_registry import get_module_registry, \
            module_registry_loaded
        if not module_registry_loaded():
            return None
        registry = get_module_registry()
        sig_list = []
        self._descriptors = []

        for (klass, _) in self._entries:
            descriptor = registry.get_descriptor(klass)
            sig_list.append(descriptor.sigstring)
            self._descriptors.append(descriptor)

        self.sigstring = "(" + ",".join(sig_list) + ")"

    def create_descriptor_list(self):
        from core.modules.module_registry import get_module_registry, \
            module_registry_loaded
        if not module_registry_loaded():
            return None
        registry = get_module_registry()
        assert self.sigstring[0] == '(' and self.sigstring[-1] == ')'

        recompute_sigstring = False
        self._descriptors = []
        if self.sigstring != '()':
            for sig in self.sigstring[1:-1].split(','):
                k = sig.split(':', 2)
                if len(k) < 2:
                    d = registry.get_descriptor_from_name_only(k[0])
                    self._descriptors.append(d)
                    recompute_sigstring = True
                else:
                    d = registry.get_descriptor_by_name(*k)
                    self._descriptors.append(d)

        if recompute_sigstring:
            self.sigstring = "(" + \
                ",".join(d.sigstring for d in self._descriptors) + ")"
            self.create_tooltip()

    def create_entries_and_descriptors(self):
        """create_entries_from_sigstring() -> None

        Populates self._entries using self.sigstring
        
        """

        self.create_descriptor_list()
        self._entries = []
        for d in self._descriptors:
            if d.module is None:
                self._entries = None
                break
            self._entries.append((d.module, '<no description>'))

    def create_tooltip(self):
        """Creates a short_sigstring that does not include package names for
        use with the tooltip. Note, however, that such sigstrings
        can't be used to reconstruct a spec. They should only be used
        for human-readable purposes.
        """
        if self._descriptors is None:
            self.create_descriptor_list()
            if self._descriptors is None:
                return None

        self._short_sigstring = \
            "(" + ",".join(d.name for d in self._descriptors) + ")"
        if self.type in ['input', 'output']:
            port_string = self.type.capitalize()
        else:
            port_string = 'Invalid'
        self._tooltip = "%s port %s\n%s" % (port_string,
                                            self.name,
                                            self._short_sigstring)
        
    # FIXME DAK: Can I move this?
    # FIXME cscheid: I hope so, because I need to import port_spec from
    #                module_function and so I'm pushing the circular import
    #                under this.
    def create_module_function(self):
        """create_module_function() -> ModuleFunction

        creates a ModuleFunction object from self.

        """
        from core.vistrail.module_function import ModuleFunction
        from core.vistrail.module_param import ModuleParam
        def from_source_port():
            f = ModuleFunction()
            f.name = self.name
            if len(self._descriptors) > 0:
                f.returnType = self._descriptors[0].name
            return f

        def from_destination_port():
            f = ModuleFunction()
            f.name = self.name
            for descriptor in self._descriptors:
                p = ModuleParam()
                p.identifier = descriptor.identifier
                p.namespace = descriptor.namespace
                p.type = descriptor.name
                
                p.name = '<no description>'
                f.addParameter(p)
            return f

        if self.type == 'output':
            return from_source_port()
        elif self.type == 'input':
            return from_destination_port()
        else:
            raise VistrailsInternalError("Was expecting a valid endpoint")
        

    def types(self):
        if self._entries is None:
            self.create_entries_and_descriptors()
        if self._entries is not None:
            return [entry[0] for entry in self._entries]
        return None

    def descriptors(self):
        if self._descriptors is None:
            self.create_descriptor_list()
        return self._descriptors

    ##########################################################################
    # Operators
    
    def __str__(self):
        """__str__() -> str - Returns a string representation of an PortSpec
        object. 

        """
        rep = "<portSpec id=%s name=%s type=%s signature=%s />"
        return  rep % (str(self.id), str(self.name), 
                       str(self.type), str(self.sigstring))

    def __eq__(self, other):
        """ __eq__(other: PortSpec) -> boolean
        Returns True if self and other have the same attributes. Used by == 
        operator. 
        
        """
        if self is None and other is None:
            return True
        if type(self) != type(other) or \
                self.name != other.name or \
                self.type != other.type:
            return False
        if self._descriptors is None:
            self.create_descriptor_list()
        if other._descriptors is None:
            other.create_descriptor_list()
        for (mine, their) in izip(self._descriptors, other._descriptors):
            if mine != their:
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def type_equals(self, other):
        """type_equals(other: PortSpec) -> Bool

        Checks equality ignoring description strings. Only cares about types.
        Does not do subtyping or supertyping: match must be perfect.

        """
        if self._descriptors is None:
            self.create_descriptor_list()
        if other._descriptors is None:
            other.create_descriptor_list()
        if self is None and other is None:
            return True
        for (mine, their) in izip(self._descriptors, other._descriptors):
            if mine != their:
                return False
        return True
        
    def key_no_id(self):
        """key_no_id(): tuple. returns a tuple that identifies
        the port without caring about ids. Used for sorting
        port lists."""
        return (self.type,
                self.name,
                self.signature)

################################################################################
# Testing

import unittest
import copy
from db.domain import IdScope

class TestPortSpec(unittest.TestCase):

    def create_port_spec(self, id_scope=IdScope()):
        # FIXME add a valid port spec
        port_spec = PortSpec(id=id_scope.getNewId(PortSpec.vtType),
                             name='SetValue',
                             type='input',
                             sigstring='(edu.utah.sci.vistrails.basic:String)',
                             )
        return port_spec

    def test_copy(self):
        id_scope = IdScope()
        
        s1 = self.create_port_spec(id_scope)
        s2 = copy.copy(s1)
        self.assertEquals(s1, s2)
        self.assertEquals(s1.id, s2.id)
        s3 = s1.do_copy(True, id_scope, {})
        self.assertEquals(s1, s3)
        self.assertNotEquals(s1.id, s3.id)

    def test_serialization(self):
        import core.db.io
        s1 = self.create_port_spec()
        xml_str = core.db.io.serialize(s1)
        s2 = core.db.io.unserialize(xml_str, PortSpec)
        self.assertEquals(s1, s2)
        self.assertEquals(s1.id, s2.id)

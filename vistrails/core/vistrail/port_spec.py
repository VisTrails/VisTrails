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

from itertools import izip
import operator

from vistrails.core.data_structures.bijectivedict import Bidict
from vistrails.core.modules.utils import create_port_spec_string, parse_port_spec_string
from vistrails.core.system import get_vistrails_basic_pkg_id, \
    get_module_registry
from vistrails.core.utils import enum, VistrailsInternalError
from vistrails.core.vistrail.port_spec_item import PortSpecItem
from vistrails.db.domain import DBPortSpec, IdScope

from ast import literal_eval
import unittest
import copy

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
        sigstring = None
        if 'sigstring' in kwargs:
            sigstring = kwargs['sigstring']
            del kwargs['sigstring']
        defaults = None
        if 'defaults' in kwargs:
            defaults = kwargs['defaults']
            del kwargs['defaults']
        labels = None
        if 'labels' in kwargs:
            labels = kwargs['labels']
            del kwargs['labels']
        values = None
        if 'values' in kwargs:
            values = kwargs['values']
            del kwargs['values']
        entry_types = None
        if 'entry_types' in kwargs:
            entry_types = kwargs['entry_types']
            del kwargs['entry_types']

        if 'items' in kwargs and 'portSpecItems' not in kwargs:
            kwargs['portSpecItems'] = kwargs['items']
            del kwargs['items']

        if 'optional' not in kwargs:
            kwargs['optional'] = 0 # False
        elif not isinstance(kwargs['optional'], (int, long)):
            if isinstance(kwargs['optional'], bool):
                if kwargs['optional']:
                    kwargs['optional'] = 1
                else:
                    kwargs['optional'] = 0
            else:
                raise VistrailsInternalError("Cannot parse 'optional' kw "
                                             "-- must be an int or bool")
        if 'min_conns' not in kwargs:
            kwargs['min_conns'] = 0
        elif kwargs['optional'] == 1 and kwargs['min_conns'] > 0:
            raise VistrailsInternalError("A mandatory port cannot be set "
                                         "to optional")
        if 'max_conns' not in kwargs:
            kwargs['max_conns'] = -1
        if kwargs['min_conns'] >= 0 and kwargs['max_conns'] >= 0 and \
                kwargs['min_conns'] > kwargs['max_conns']:
            raise VistrailsInternalError("Minimum number of connections "
                                         "cannot be greater than maximum "
                                         "number of connections")
            
        if 'sort_key' not in kwargs:
            kwargs['sort_key'] = -1
        if 'depth' not in kwargs:
            kwargs['depth'] = 0
        if 'id' not in kwargs:
            kwargs['id'] = -1
        if 'tooltip' in kwargs:
            self._tooltip = kwargs['tooltip']
            del kwargs['tooltip']
        else:
            self._tooltip = None

        if 'docstring' in kwargs:
            self._docstring = kwargs['docstring']
            del kwargs['docstring']
        else:
            self._docstring = None
        if 'shape' in kwargs:
            self._shape = kwargs['shape']
            del kwargs['shape']
        else:
            self._shape = None

        DBPortSpec.__init__(self, *args, **kwargs)

        if sum(1 for container in (self.port_spec_items, signature, sigstring)
               if container) > 1:
            raise ValueError("Please specify only one of portSpecItems,"
                             " signature, or sigstring kwargs.")
        self.create_spec_items(self.port_spec_items, signature, sigstring, 
                               defaults, labels, values, entry_types)

        self._short_sigstring = None
        # if signature is not None:
        #     self.create_entries(signature)
        # if not self.sigstring and self._entries is not None:
        #     # create sigstring from entries
        #     self.create_sigstring_and_descriptors()
# DAKOOP: removed this---we will check in module_registry and pipeline 
# validation, this way, we can let errors go all the way up
#         elif self._entries is None and self.sigstring:
#             # create entries from sigstring
#             self.create_entries_and_descriptors()
#         else:
#             raise VistrailsInternalError("Need to specify signature or "
#                                          "sigstring to create PortSpec")
        # if self._entries is not None and self._tooltip is None:
        #     self.create_tooltip()
        self.is_valid = True

    def __copy__(self):
        return PortSpec.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBPortSpec.do_copy(self, new_ids, id_scope, id_remap)
        cp._short_sigstring = self._short_sigstring
        cp._tooltip = self._tooltip
        cp._shape = self._shape
        cp._docstring = self._docstring
        cp.is_valid = self.is_valid
        cp.__class__ = PortSpec
        # if cp._entries is not None:
        #     cp.create_tooltip()
        return cp

    @staticmethod
    def convert(_port_spec):
        if _port_spec.__class__ == PortSpec:
            return
        _port_spec.__class__ = PortSpec
        for _port_spec_item in _port_spec.db_portSpecItems:
            PortSpecItem.convert(_port_spec_item)
        _port_spec._short_sigstring = None
        _port_spec._tooltip = None
        _port_spec._shape = None
        _port_spec._docstring = None
        _port_spec.is_valid = True

        _port_spec.port_spec_items.sort(key=operator.attrgetter('db_pos'))

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
    min_conns = DBPortSpec.db_min_conns
    max_conns = DBPortSpec.db_max_conns
    _depth = DBPortSpec.db_depth
    port_spec_items = DBPortSpec.db_portSpecItems
    items = DBPortSpec.db_portSpecItems

    def _get_sigstring(self):
        return create_port_spec_string([i.spec_tuple 
                                        for i in self.port_spec_items])
    sigstring = property(_get_sigstring)

    def is_mandatory(self):
        return (self.min_conns > 0)

    def _get_labels(self):
        return [i.label for i in self.port_spec_items]
    labels = property(_get_labels)

    def _get_defaults(self):
        return [i.default for i in self.port_spec_items]
    defaults = property(_get_defaults)
    
    def _get_short_sigstring(self):
        if self._short_sigstring is None:
            self.create_tooltip()
        return self._short_sigstring
    short_sigstring = property(_get_short_sigstring)

    def _get_signature(self):
        signature = []
        for i in self.port_spec_items:
            signature.append((i.descriptor.module, i.label))
        return signature
    signature = property(_get_signature)

    def _get_depth(self):
        return self._depth or 0
    def _set_depth(self, depth):
        self._depth = depth
    depth = property(_get_depth, _set_depth)

    def toolTip(self):
        if self._tooltip is None:
            self.create_tooltip()
        return self._tooltip

    def shape(self):
        return self._shape
    
    def docstring(self):
        return self._docstring

    def descriptors(self):
        return [i.descriptor for i in self.port_spec_items]

    ##########################################################################
    # Methods

    def _resize_attrs(self, target, *lists):
        for rlist in lists:
            if len(target) > len(rlist):
                rlist.extend(None for i in xrange(len(target)-len(rlist)))

    def _set_attrs(self, item, *attrs):
        attr_order = ['default', 'label', 'values', 'entry_type']
        if item is None:
            kwargs = dict(izip(attr_order, attrs))
            return kwargs
        else:
            for (attr_key, attr) in izip(attr_order, attrs):
                if attr is not None:
                    setattr(item, attr_key, attr)


    def create_spec_items(self, items=None, signature=None, sigstring=None, 
                          defaults=None, labels=None, values=None, 
                          entry_types=None):
        if defaults is None:
            defaults = []
        elif isinstance(defaults, basestring):
            defaults = literal_eval(defaults)
        if labels is None:
            labels = []
        elif isinstance(labels, basestring):
            labels = literal_eval(labels)
        if values is None:
            values = []
        elif isinstance(values, basestring):
            values = literal_eval(values)
        if entry_types is None:
            entry_types = []
        elif isinstance(entry_types, basestring):
            entry_types = literal_eval(entry_types)
        attrs = [defaults, labels, values, entry_types]
        if items:
            self.set_items(items, *attrs)
        elif signature is not None:
            items = self.get_items_from_entries(signature, *attrs)
        elif sigstring is not None:
            items = self.get_items_from_sigstring(sigstring, *attrs)
        self.port_spec_items = items

    def set_items(self, items, *attrs):
        self._resize_attrs(items, *attrs)
        for i, item_tuple in enumerate(izip(items, *attrs)):
            item_tuple[0].pos = i
            self._set_attrs(*item_tuple)

    def get_items_from_entries(self, signature, *attrs):
        # This is reasonably messy code. The intent is that a
        # signature given by the user in a call like this
        # add_input_port(module, name, signature) should be one of the
        # following:

        # type only: add_input_port(_, _, Float)
        # type plus description: add_input_port(_, _, (Float, 'radius'))

        # multiple parameters, where each parameter can be either of the above:
        # add_input_port(_, _, [Float, (Integer, 'count')])

        registry = get_module_registry()
        def canonicalize(sig_item):
            if isinstance(sig_item, tuple):
                # assert len(sig_item) == 2
                # assert isinstance(sig_item[0], type)
                # assert isinstance(sig_item[1], str)
                descriptor = registry.get_descriptor(sig_item[0])
                label = sig_item[1]
                return (descriptor, label)
            elif isinstance(sig_item, list):
                descriptor = registry.get_descriptor_by_name(
                    get_vistrails_basic_pkg_id(), 'List')
                return (descriptor, None)
            else:
                # isinstance(sig_item, type):
                return (registry.get_descriptor(sig_item), None)

        # def _add_entry(sig_item):
        ps_items = []
        if not isinstance(signature, list):
            signature = [signature]
        self._resize_attrs(signature, *attrs)
        for i, item_tuple in enumerate(izip(signature, *attrs)):
            descriptor, item_label = canonicalize(item_tuple[0])
            kwargs = self._set_attrs(None, *item_tuple[1:])
            if not kwargs['label']:
                if item_label != "<no description>":
                    kwargs['label'] = item_label
            ps_item = PortSpecItem(pos=i, 
                                   package=descriptor.identifier,
                                   module=descriptor.name,
                                   namespace=descriptor.namespace,
                                   **kwargs)
            ps_items.append(ps_item)
        return ps_items

    def get_items_from_sigstring(self, sigstring, *attrs):
        ps_items = []
        specs_list = parse_port_spec_string(sigstring)
        if len(specs_list) == 0:
            return ps_items

        self._resize_attrs(specs_list, *attrs)
        for i, item_tuple in enumerate(izip(specs_list, *attrs)):
            kwargs = self._set_attrs(None, *item_tuple[1:])
            ps_item = PortSpecItem(pos=i,
                                   package=item_tuple[0][0],
                                   module=item_tuple[0][1],
                                   namespace=item_tuple[0][2],
                                   **kwargs)
            ps_items.append(ps_item)
        return ps_items

    def create_tooltip(self):
        """Creates a short_sigstring that does not include package names for
        use with the tooltip. Note, however, that such sigstrings
        can't be used to reconstruct a spec. They should only be used
        for human-readable purposes.
        """

        self._short_sigstring = \
            "(" + ",".join(d.name for d in self.descriptors()) + ")"
        if self.type in ['input', 'output']:
            port_string = self.type.capitalize()
        else:
            port_string = 'Invalid'
        _depth = " (depth %s)" % self.depth if self.depth else ''
        self._tooltip = "%s port %s\n%s%s" % (port_string,
                                            self.name,
                                            self._short_sigstring,
                                            _depth)
        
    ##########################################################################
    # Operators
    
    def __str__(self):
        """__str__() -> str - Returns a string representation of an PortSpec
        object. 

        """
        rep = "<portSpec id=%s name=%s type=%s signature=%s depth=%s />"
        return  rep % (str(self.id), str(self.name), 
                       str(self.type), str(self.sigstring), str(self.depth))

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
        if len(self.descriptors()) != len(other.descriptors()):
            return False
        for (mine, their) in izip(self.descriptors(), other.descriptors()):
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
        if self is None and other is None:
            return True
        if len(self.descriptors()) != len(other.descriptors()):
            return False
        for (mine, their) in izip(self.descriptors(), other.descriptors()):
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


class TestPortSpec(unittest.TestCase):

    def create_port_spec(self, id_scope=IdScope()):
        # FIXME add a valid port spec
        port_spec = PortSpec(id=id_scope.getNewId(PortSpec.vtType),
                             name='SetValue',
                             type='input',
                             sigstring='(%s:String)' % \
                                 get_vistrails_basic_pkg_id(),
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
        import vistrails.core.db.io
        s1 = self.create_port_spec()
        xml_str = vistrails.core.db.io.serialize(s1)
        s2 = vistrails.core.db.io.unserialize(xml_str, PortSpec)
        self.assertEquals(s1, s2)
        self.assertEquals(s1.id, s2.id)

    def test_create_from_signature(self):
        from vistrails.core.modules.basic_modules import Float
        port_spec = PortSpec(id=-1,
                             name="SetXYZ",
                             type='input',
                             signature=[(Float, "x"), (Float, "y"), 
                                        (Float, "z")])

    def test_create_from_items(self):
        basic_pkg = get_vistrails_basic_pkg_id()
        item_a = PortSpecItem(pos=0,
                              package=basic_pkg,
                              module="Integer",
                              label="a",
                              default="123")
        item_b = PortSpecItem(pos=1,
                              package=basic_pkg,
                              module="String",
                              label="b",
                              default="abc")
        port_spec = PortSpec(id=-1,
                             name="SetValue",
                             type='input',
                             portSpecItems=[item_a, item_b])
        

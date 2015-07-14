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

import ast
from xml.etree import cElementTree as ET

def parse_props(props):
    """ Parse the attribute properties
        props can be an object or a tuple of len 1-3

    """
    default_val, is_subelt, eval = props, False, False
    if isinstance(props, tuple):
        if len(props)>0:
            default_val = props[0]
        if len(props)>1:
            is_subelt = props[1]
        if len(props)>2:
            eval = props[2]
    return default_val, is_subelt, eval

class SpecList(object):
    """ A class with module specifications and custom code
        This describes how the wrapped methods/classes will
        maps to modules in vistrails
    """

    def __init__(self, module_specs=None):
        if module_specs is None:
            module_specs = []
        self.module_specs = module_specs

    def write_to_xml(self, fname):
        root = ET.Element("specs")
        for spec in self.module_specs:
            root.append(spec.to_xml())
        tree = ET.ElementTree(root)

        def indent(elem, level=0):
            i = "\n" + level*"  "
            if len(elem):
                if not elem.text or not elem.text.strip():
                    elem.text = i + "  "
                if not elem.tail or not elem.tail.strip():
                    elem.tail = i
                for elem in elem:
                    indent(elem, level+1)
                if not elem.tail or not elem.tail.strip():
                    elem.tail = i
            else:
                if level and (not elem.tail or not elem.tail.strip()):
                    elem.tail = i
        indent(tree.getroot())

        tree.write(fname)

    @staticmethod
    def read_from_xml(fname, klass=None):
        if klass is None:
            klass = ModuleSpec
        module_specs = []
        tree = ET.parse(fname)
        for elt in tree.getroot():
            if elt.tag == klass.xml_name:
                module_specs.append(klass.from_xml(elt))
        retval = SpecList(module_specs)
        # for spec in retval.module_specs:
        #     print "==", spec.name, "=="
        #     for ps in spec.port_specs:
        #         print " ", ps.arg, ps.name
        return retval

######### BASE MODULE SPEC ###########

class PortSpec(object):
    """ Represents specification of a port
    """
    xml_name = "portSpec"
    # value as string means default value
    # value as tuple means (default value, [is subelement, [run eval]])
    # Subelement: Should be serialized as a subelement (For large texts)
    # eval: serialize as string and use eval to get value back

    # Properties to use when creating Port
    prop_attrs = {
        "docstring": ("", True),            # documentation
        "min_conns": (0, False, True),      # set min_conns (1=required)
        "max_conns": (-1, False, True),     # Set max_conns (default -1)
        "show_port": (False, False, True),  # Set not optional (use connection)
        "sort_key": (-1, False, True),      # sort_key
        "shape": (None, False, True),       # physical shape
        "depth": (0, False, True)           # expected list depth
        }
    # other attributes
    attrs = {
        "name": "",                         # port name
        "port_type": None                   # type signature in vistrails
    }
    attrs.update(prop_attrs)

    def __init__(self, **kwargs):
        self.set_defaults(**kwargs)

    def set_defaults(self, **kwargs):
        for attr, props in self.attrs.iteritems():
            default_val, is_subelt, run_eval = parse_props(props)
            setattr(self, attr, kwargs.get(attr, default_val))

    def get_port_attrs(self):
        """ Returns a prop_attrs dict that will be passed to Port()

        """
        attrs = {}
        for attr, props in self.prop_attrs.iteritems():
            default_val, is_subelt, run_eval = parse_props(props)
            value = getattr(self, attr)
            if hasattr(self, attr) and value != default_val:
                attrs[attr] = value
        # Translate "show_port" -> "not optional"
        if 'show_port' in attrs:
            del attrs['show_port']
        else:
            attrs['optional'] = True
        return attrs

    def to_xml(self, elt=None):
        if elt is None:
            elt = ET.Element(self.xml_name)
        for attr, props in self.attrs.iteritems():
            attr_val = getattr(self, attr)
            default_val, is_subelt, run_eval = parse_props(props)
            if default_val != attr_val:
                if is_subelt:
                    subelt = ET.Element(attr)
                    subelt.text = unicode(getattr(self, attr))
                    elt.append(subelt)
                else:
                    elt.set(attr, unicode(attr_val))
        return elt

    @classmethod
    def internal_from_xml(cls, elt, obj=None):
        if obj is None:
            obj = cls()

        child_elts = {}
        for child in elt.getchildren():
            # if child.tag not in obj.attrs:
            #     raise RuntimeError('Cannot deal with tag "%s"' % child.tag)
            if child.tag not in child_elts:
                child_elts[child.tag] = []
            child_elts[child.tag].append(child)

        kwargs = {}
        for attr, props in obj.attrs.iteritems():
            default_val, is_subelt, run_eval = parse_props(props)
            attr_vals = []
            if is_subelt:
                if attr in child_elts:
                    attr_vals = [c.text for c in child_elts[attr]
                                 if c.text is not None]
            else:
                attr_val = elt.get(attr)
                if attr_val is not None:
                    attr_vals = [attr_val]

            if len(attr_vals) > 1:
                raise ValueError('Should have only one value for '
                                'attribute "%s"' % attr)
            if len(attr_vals) > 0:
                attr_val = attr_vals[0]
                if run_eval:
                    try:
                        kwargs[attr] = ast.literal_eval(attr_val)
                    except (NameError, SyntaxError, ValueError):
                        kwargs[attr] = attr_val
                else:
                    kwargs[attr] = attr_val
        obj.set_defaults(**kwargs)
        return obj, child_elts

    @classmethod
    def from_xml(cls, elt, obj=None):
        obj, child_elts = cls.internal_from_xml(elt, obj)
        return obj

    @classmethod
    def create_from_xml(cls, elt):
        if elt.tag == cls.InputSpecType.xml_name:
            return cls.InputSpecType.from_xml(elt)
        elif elt.tag == cls.OutputSpecType.xml_name:
            return cls.OutputSpecType.from_xml(elt)
        raise TypeError('Cannot create spec from element of type "%s"' %
                        elt.tag)

    def get_port_type(self):
        """ Get port type from a possibly flattened list

        """
        if self.port_type is None:
            return "basic:Null"
        try:
            port_types = ast.literal_eval(self.port_type)

            def flatten(t):
                if not isinstance(t, list):
                    raise Exception("Expected a list")
                flat = []
                for elt in t:
                    if isinstance(elt, list):
                        flat.extend(flatten(elt))
                    else:
                        flat.append(elt)
                return flat
            return ','.join(flatten(port_types))
        except (SyntaxError, ValueError):
            pass
        return self.port_type

    def get_prepend_params(self):
        if self.prepend_params is None:
            return []
        return self.prepend_params


class InputPortSpec(PortSpec):
    xml_name = "inputPortSpec"

    prop_attrs = {
        "entry_types": (None, True, True), # custom entry type (like enum)
        "values": (None, True, True),      # values for enums
        "labels": (None, True, True),      # custom labels on enum values
        "defaults": (None, True, True),    # default value list
        }

    attrs = {}
    attrs.update(prop_attrs)
    attrs.update(PortSpec.attrs)

    prop_attrs.update(PortSpec.prop_attrs)

class OutputPortSpec(PortSpec):
    xml_name = "outputPortSpec"

class ModuleSpec(object):
    """ Represents specification of a module
        This mirrors how the module will look in the vistrails registry
    """
    xml_name = 'moduleSpec'
    InputSpecType = InputPortSpec
    OutputSpecType = OutputPortSpec

    # From Modulesettings. See core.modules.config._documentation
    ms_attrs = {
        'name':               None,
        'configure_widget':   (None, False, True),
        'constant_widget':    (None, False, True),
        'constant_widgets':   (None, False, True),
        'signature':          (None, False, True),
        'constant_signature': (None, False, True),
        'color':              (None, False, True),
        'fringe':             (None, False, True),
        'left_fringe':        (None, False, True),
        'right_fringe':       (None, False, True),
        'abstract':           (None, False, True),
        'namespace':          (None, False, True),
        'package_version':    (None, False, True),
        'hide_descriptor':    (None, False, True)}
    attrs = {
        # basic attributes
        'module_name': '', # Name of module (can be overridden by modulesettings)
        'superklass': '',  # class to inherit from
        'code_ref': '',    # reference to wrapped class/method
        'docstring': ('', True),   # module __doc__
        'cacheable': (False, False, True),   # should this module be cached
        # special attributes
        'callback': None,    # name of attribute for progress callback
        'tempfile': None    # attribute name for temporary file creation method
    }
    attrs.update(ms_attrs)

    def __init__(self, input_port_specs=None, output_port_specs=None,
                 **kwargs):
        if input_port_specs is None:
            input_port_specs = []
        if output_port_specs is None:
            output_port_specs = []

        self.input_port_specs = input_port_specs
        self.output_port_specs = output_port_specs

        for attr, props in self.attrs.iteritems():
            default_val, is_subelt, run_eval = parse_props(props)
            setattr(self, attr, kwargs.get(attr, default_val))

    def to_xml(self, elt=None):
        if elt is None:
            elt = ET.Element(self.xml_name)
        for attr, props in self.attrs.iteritems():
            value = getattr(self, attr)
            default_val, is_subelt, run_eval = parse_props(props)
            if value != default_val:
                if is_subelt:
                    subelt = ET.Element(attr)
                    subelt.text = unicode(value)
                    elt.append(subelt)
                else:
                    if run_eval:
                        value = repr(value)
                    elt.set(attr, value)
        for port_spec in self.input_port_specs:
            subelt = port_spec.to_xml()
            elt.append(subelt)
        for port_spec in self.output_port_specs:
            subelt = port_spec.to_xml()
            elt.append(subelt)
        return elt

    @staticmethod
    def from_xml(elt, klass=None):
        if klass is None:
            klass = ModuleSpec
        # Process attributes
        kwargs = {}
        for attr, props in klass.attrs.iteritems():
            default_val, is_subelt, run_eval = parse_props(props)
            value = elt.get(attr, default_val)
            if run_eval and value != default_val:
                value = ast.literal_eval(value)
            kwargs[attr] = value
        input_port_specs = []
        output_port_specs = []
        for child in elt.getchildren():
            if child.tag == klass.InputSpecType.xml_name:
                input_port_specs.append(klass.InputSpecType.from_xml(child))
            elif child.tag == klass.OutputSpecType.xml_name:
                output_port_specs.append(klass.OutputSpecType.from_xml(child))
            elif child.tag in klass.attrs:
                props = klass.attrs[child.tag]
                default_val, is_subelt, run_eval = parse_props(props)
                if not is_subelt:
                    continue
                value = child.text or default_val
                if run_eval and value != default_val:
                    value = ast.literal_eval(value)
                kwargs[child.tag] = value
        return klass(input_port_specs=input_port_specs,
                     output_port_specs=output_port_specs,
                     **kwargs)

    def get_output_port_spec(self, compute_name):
        for ps in self.output_port_specs:
            if ps.compute_name == compute_name:
                return ps
        return None

    def get_module_settings(self):
        """ Returns modulesettings dict

        """
        attrs = {}
        for attr in self.ms_attrs:
            value = getattr(self, attr)
            if value is not None:
                attrs[attr] = value
        return attrs


######### PYTHON FUNCTION SPEC ###########

class FunctionInputPortSpec(InputPortSpec):
    xml_name = "functionInputPortSpec"
    attrs = {"arg": ""}                  # attribute name
    attrs.update(InputPortSpec.attrs)


class FunctionOutputPortSpec(OutputPortSpec):
    xml_name = "functionOutputPortSpec"


class FunctionSpec(ModuleSpec):
    """ Specification for wrapping a python function
    """
    xml_name = 'functionSpec'
    InputSpecType = FunctionInputPortSpec
    OutputSpecType = FunctionOutputPortSpec

    # output_type tells VisTrails what the function returns
    # None - single data object
    # "list" - ordered list
    # "dict" - dict with attr:value
    attrs = {'output_type': None}
    attrs.update(ModuleSpec.attrs)

    def __init__(self, input_port_specs=None, output_port_specs=None,
                 **kwargs):
        ModuleSpec.__init__(self, input_port_specs, output_port_specs,
                            **kwargs)

    @staticmethod
    def from_xml(elt):
        inst = ModuleSpec.from_xml(elt, FunctionSpec)
        return inst

######### PYTHON CLASS SPEC ###########


class ClassInputPortSpec(InputPortSpec):
    xml_name = "classInputPortSpec"
    attrs = {
        "method_name": "",                   # method name
        "method_type": "",                   # Type like nullary, OnOff or SetXToY
        "prepend_params": (None, True, True) # prepended params like index
        }
    attrs.update(InputPortSpec.attrs)

    def __init__(self, **kwargs):
        InputPortSpec.__init__(self, **kwargs)
        if not self.method_name:
            self.method_name = self.name


class ClassOutputPortSpec(OutputPortSpec):
    xml_name = "classOutputPortSpec"
    attrs = {
        "method_name": "",                   # method/attribute name
        "prepend_params": (None, True, True) # prepended params used with indexed methods
        }
    attrs.update(OutputPortSpec.attrs)

    def __init__(self, **kwargs):
        OutputPortSpec.__init__(self, **kwargs)
        if not self.method_name:
            self.method_name = self.name


class ClassSpec(ModuleSpec):
    """ Specification for wrapping a python class
    """
    xml_name = 'classSpec'
    InputSpecType = ClassInputPortSpec
    OutputSpecType = ClassOutputPortSpec
    attrs = {
        'methods_last': (False, False, True), # If True will compute methods before connections
        'compute': None,       # Function to call after input methods
        'cleanup': None}       # Function to call after output methods
    attrs.update(ModuleSpec.attrs)

    def __init__(self, input_port_specs=None, output_port_specs=None,
                 **kwargs):
        ModuleSpec.__init__(self, input_port_specs, output_port_specs,
                            **kwargs)

    @staticmethod
    def from_xml(elt):
        inst = ModuleSpec.from_xml(elt, ClassSpec)
        return inst

###############################################################################

import unittest

class TestModuleSpec(unittest.TestCase):

    def test_module_spec(self):
        input_spec = InputPortSpec(name='myportname',
                                   port_type='basic:String',
                                   docstring='my port doc',
                                   min_conns=1,
                                   max_conns=3,
                                   show_port=True,
                                   sort_key=5,
                                   depth=1,
                                   entry_type='enum')
        in_attrs = input_spec.get_port_attrs()

        output_spec = OutputPortSpec(name='myportname',
                                   port_type='basic:String',
                                   docstring='my port doc',
                                   min_conns=1,
                                   max_conns=3,
                                   show_port=False,
                                   sort_key=5,
                                   depth=1)
        out_attrs = output_spec.get_port_attrs()

        ms = ModuleSpec(module_name='myclassname',
                        superklass='mysuperclassname',
                        code_ref='theclassname',
                        docstring='my documentation',
                        callback=None,
                        tempfile=None,
                        cacheable=False,
                        input_port_specs=[input_spec],
                        output_port_specs=[output_spec])
        as_string = ET.tostring(ms.to_xml())
        from_string = ET.fromstring(as_string)
        ms2 = ModuleSpec.from_xml(from_string)
        in_attrs2 = ms2.input_port_specs[0].get_port_attrs()
        out_attrs2 = ms2.output_port_specs[0].get_port_attrs()
        self.assertEqual(in_attrs, in_attrs2)
        self.assertEqual(out_attrs, out_attrs2)

    def test_function_spec(self):
        input_spec = FunctionInputPortSpec(name='myportname',
                                   port_type='basic:String',
                                   docstring='my port doc',
                                   min_conns=1,
                                   max_conns=3,
                                   show_port=False,
                                   sort_key=5,
                                   depth=1,
                                   arg='myargname',
                                   )
        in_attrs = input_spec.get_port_attrs()

        output_spec = FunctionOutputPortSpec(name='myportname',
                                   port_type='basic:String',
                                   docstring='my port doc',
                                   min_conns=1,
                                   max_conns=3,
                                   show_port=False,
                                   sort_key=5,
                                   depth=1)
        out_attrs = output_spec.get_port_attrs()

        ms = FunctionSpec(module_name='myclassname',
                        superklass='mysuperclassname',
                        code_ref='theclassname',
                        docstring='my documentation',
                        callback=None,
                        tempfile=None,
                        cacheable=False,
                        input_port_specs=[input_spec],
                        output_port_specs=[output_spec],
                        output_type='list')
        as_string = ET.tostring(ms.to_xml())
        from_string = ET.fromstring(as_string)
        ms2 = FunctionSpec.from_xml(from_string)
        in_attrs2 = ms2.input_port_specs[0].get_port_attrs()
        out_attrs2 = ms2.output_port_specs[0].get_port_attrs()
        self.assertEqual(in_attrs, in_attrs2)
        self.assertEqual(out_attrs, out_attrs2)

    def test_class_spec(self):
        input_spec = ClassInputPortSpec(name='myportname',
                                   port_type='basic:String',
                                   docstring='my port doc',
                                   min_conns=1,
                                   max_conns=3,
                                   show_port=False,
                                   sort_key=5,
                                   depth=1,
                                   method_name='MyClassMethodName',
                                   method_type='SetXToY',
                                   prepend_params=[1])
        in_attrs = input_spec.get_port_attrs()

        output_spec = ClassOutputPortSpec(name='myportname',
                                   port_type='basic:String',
                                   docstring='my port doc',
                                   min_conns=1,
                                   max_conns=3,
                                   show_port=False,
                                   sort_key=5,
                                   depth=1,
                                   method_name='MyClassMethodName',
                                   prepend_params=[1])
        out_attrs = output_spec.get_port_attrs()

        ms = ClassSpec(module_name='myclassname',
                        superklass='mysuperclassname',
                        code_ref='theclassname',
                        docstring='my documentation',
                        callback=None,
                        tempfile=None,
                        cacheable=False,
                        input_port_specs=[input_spec],
                        output_port_specs=[output_spec],
                        methods_last=True,
                        compute='myCompute',
                        cleanup='myCleanup')
        as_string = ET.tostring(ms.to_xml())
        from_string = ET.fromstring(as_string)
        ms2 = ClassSpec.from_xml(from_string)
        in_attrs2 = ms2.input_port_specs[0].get_port_attrs()
        out_attrs2 = ms2.output_port_specs[0].get_port_attrs()
        self.assertEqual(in_attrs, in_attrs2)
        self.assertEqual(out_attrs, out_attrs2)


#def run():
#    specs = SpecList.read_from_xml("mpl_plots_raw.xml")
#    specs.write_to_xml("mpl_plots_raw_out.xml")

#if __name__ == '__main__':
#    run()

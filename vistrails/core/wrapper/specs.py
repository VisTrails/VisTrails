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
import copy
import os.path
import shutil

from redbaron import RedBaron
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

    def __init__(self, module_specs=None, translations=None):
        """
        translations : {type_string: [{input patch}, {output patch}}
            A dict of translations mapping port types to input/output patches


        """
        if module_specs is None:
            module_specs = []
        self.module_specs = module_specs
        if translations is None:
            translations = {}
        self.translations = translations
        self.patches = {}

    def write_to_xml(self, fname, patch_file=None):
        root = ET.Element("specs")
        for spec in self.module_specs:
            root.append(spec.to_xml())
        for port_type, [input_patch, output_patch] in self.translations.iteritems():
            subelt = ET.Element('translation')
            subelt.set('type', port_type)
            subelt.set('input', input_patch)
            subelt.set('output', output_patch)
            root.append(subelt)
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

        if patch_file:
            patch_name = os.path.splitext(fname)[0] + '-patches.py'
            shutil.copyfile(patch_file, patch_name)

    @staticmethod
    def read_from_xml(fname, klass=None):
        if klass is None:
            klass = ModuleSpec
        module_specs = []
        translations = {}
        tree = ET.parse(fname)
        for elt in tree.getroot():
            if elt.tag == klass.xml_name:
                module_specs.append(klass.from_xml(elt))
            if elt.tag == 'translation':
                translations[elt.get('type')] = [elt.get('input'), elt.get('output')]
        retval = SpecList(module_specs, translations)
        # read patch file from same directory if it exists
        patch_name = os.path.splitext(fname)[0] + '-patches.py'
        if os.path.exists(patch_name):
            retval.read_patches(patch_name)
        return retval

    def read_patches(self, fname):
        """ Read patches from a file """
        patches = {}
        with open(fname) as src:
            red = RedBaron(src.read())
        for patch in red.node_list:
            if patch.type != 'def':
                continue
            new_patch = patch.copy()
            # remove trailing lines
            tail = 1000
            for i, line in enumerate(patch.value):
                if line.type == 'endl' and line.indent == '':
                    # The function has ended, the rest is trailing comments
                    tail = i
            while len(new_patch.value) > tail:
                del new_patch.value[tail]

            patch_lines = []
            for line in new_patch.dumps().split('\n'):
                # ignore lines with single newline
                if not line.startswith('    '):
                    continue
                # deindent line
                patch_lines.append(line[4:])
            final_patch = '\n'.join(patch_lines).strip()
            arguments = [a.name.value for a in patch.arguments]
            patches[patch.name] = (arguments, final_patch)
            self.patches = patches


######### BASE MODULE SPEC ###########


class SpecObject(object):

    # Add attributes in subclasses
    # value as string means default value
    # value as tuple means (default value, [is subelement, [run eval]])
    # Subelement: Should be serialized as a subelement (For large texts)
    # eval: serialize as string and use eval to get value back
    attrs = {}

    def __init__(self, **kwargs):
        self.set_defaults(kwargs)

    def set_defaults(self, kwargs):
        for attr, props in self.attrs.iteritems():
            default_val, is_subelt, run_eval = parse_props(props)
            setattr(self, attr, kwargs.pop(attr)
                                if attr in kwargs else default_val)
        if kwargs:
            raise Exception('Unknown argument(s): %s' % kwargs.keys())
        assert kwargs == {}

    def to_xml(self, elt=None):
        if elt is None:
            elt = ET.Element(self.xml_name)
        for attr, props in self.attrs.iteritems():
            value = getattr(self, attr)
            default_val, is_subelt, run_eval = parse_props(props)
            if default_val != value and value is not None:
                if run_eval:
                    value = self.get_raw(attr)
                else:
                    if not isinstance(value, basestring):
                        value = unicode(value)
                    elif not isinstance(value, unicode):
                        value = unicode(value, 'utf-8')
                if is_subelt:
                    subelt = ET.Element(attr)
                    subelt.text = value
                    elt.append(subelt)
                else:
                    elt.set(attr, value)
        return elt

    def set_raw(self, attr, value):
        """ parse the value before setting it
        """
        props = self.attrs[attr]
        run_eval = parse_props(props)[2]
        if run_eval:
            value = ast.literal_eval(value)
        setattr(self, attr, value)

    def get_raw(self, attr):
        """ serialize the value before returning it
        """
        props = self.attrs[attr]
        run_eval = parse_props(props)[2]
        value = getattr(self, attr)
        return repr(value) if run_eval else value

    @classmethod
    def internal_from_xml(cls, elt):
        # Process attributes
        kwargs = {}
        for attr, props in cls.attrs.iteritems():
            default_val, is_subelt, run_eval = parse_props(props)
            value = elt.get(attr, default_val)
            if run_eval and value != default_val:
                value = ast.literal_eval(value)
            kwargs[attr] = value
        children = elt.getchildren()
        for child in children:
            if child.tag in cls.attrs:
                props = cls.attrs[child.tag]
                default_val, is_subelt, run_eval = parse_props(props)
                if not is_subelt:
                    continue
                value = child.text or default_val
                if run_eval and value != default_val:
                    value = ast.literal_eval(value)
                kwargs[child.tag] = value
        return kwargs, children

    @classmethod
    def from_xml(cls, elt):
        kwargs, child_elts = cls.internal_from_xml(elt)
        return cls(**kwargs)

class PortSpec(SpecObject):
    """ Represents specification of a port
    """
    xml_name = "portSpec"

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
        "port_type": 'basic:String'         # type signature in vistrails
    }
    attrs.update(prop_attrs)

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
    alternate_specs = None
    _parent = None

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

    def __init__(self, **kwargs):
        if "alternate_specs" in kwargs:
            self.alternate_specs = kwargs.pop("alternate_specs")
        else:
            self.alternate_specs = []
        PortSpec.__init__(self, **kwargs)
        for spec in self.alternate_specs:
            spec.set_parent(self)

    def has_alternate_versions(self):
        return len(self.alternate_specs) > 0

    def set_parent(self, parent):
        self._parent = parent
        if not self.name:
            if self._parent.name.endswith("Sequence"):
                base_name = self._parent.name[:-8]
            elif self._parent.name.endswith("Scalar"):
                base_name = self._parent.name[:-6]
            else:
                base_name = self._parent.name
            if self.port_type == "basic:List":
                self.name = base_name + "Sequence"
            else:
                self.name = base_name + "Scalar"
        #self.arg = self._parent.arg

    def full(self):
        """ Construct full spec for an alternate spec
        """
        """ Check parent spec first

        """
        if not self._parent:
            # This is not an Alternate PortSpec
            return self
        full_spec = copy.copy(self)
        for k in self.attrs:
            default, _, _ = parse_props(self.attrs[k])
            # never copy port type attributes and name
            type_props = ['name', 'defaults', 'values', 'entry_types', 'port_type']
            if k in type_props:
                continue
            alt_value = getattr(self, k)
            if alt_value == default:
                setattr(full_spec, k, getattr(self._parent, k))
        return full_spec

    def to_xml(self, elt=None):
        elt = PortSpec.to_xml(self, elt)
        for spec in self.alternate_specs:
            # write the spec as alternateSpec
            spec.xml_name = 'alternateSpec'
            subelt = spec.to_xml()
            elt.append(subelt)
        return elt

    @classmethod
    def from_xml(cls, elt):
        kwargs, child_elts = cls.internal_from_xml(elt)

        obj = cls(**kwargs)

        for child_elt in child_elts:
            if "alternateSpec"  == child_elt.tag:
                spec = cls.from_xml(child_elt)
                spec.set_parent(obj)
                obj.alternate_specs.append(spec)

        return obj

    def get_port_attrs(self):
        """ Check parent spec first

        """
        if not self._parent:
            return PortSpec.get_port_attrs(self)

        # This is an Alternate PortSpec
        alt_attrs = PortSpec.get_port_attrs(self)
        par_attrs = self._parent.get_port_attrs()
        for k, v in par_attrs.iteritems():
            # type properties are never copied from parent
            if k == 'defaults' or k == "values" or k == "entry_types":
                continue
            if k not in alt_attrs or alt_attrs[k] is None:
                alt_attrs[k] = v
        return alt_attrs

class OutputPortSpec(PortSpec):
    xml_name = "outputPortSpec"

class ModuleSpec(SpecObject):
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
        'callback': None,    # attribute name for progress callback
        'tempfile': None    # attribute name for temporary file creation method
    }
    attrs.update(ms_attrs)

    def __init__(self, **kwargs):
        if 'input_port_specs' in kwargs:
            self.input_port_specs = kwargs.pop('input_port_specs')
        else:
            self.input_port_specs = []

        if 'output_port_specs' in kwargs:
            self.output_port_specs = kwargs.pop('output_port_specs')
        else:
            self.output_port_specs = []
        SpecObject.__init__(self, **kwargs)

    def to_xml(self, elt=None):
        elt = SpecObject.to_xml(self, elt)
        for port_spec in self.input_port_specs:
            subelt = port_spec.to_xml()
            elt.append(subelt)
        for port_spec in self.output_port_specs:
            subelt = port_spec.to_xml()
            elt.append(subelt)
        return elt

    @classmethod
    def from_xml(cls, elt):
        kwargs, child_elts = cls.internal_from_xml(elt)
        # read port specs
        input_port_specs = []
        output_port_specs = []
        for child in child_elts:
            if child.tag == cls.InputSpecType.xml_name:
                input_port_specs.append(cls.InputSpecType.from_xml(child))
            elif child.tag == cls.OutputSpecType.xml_name:
                output_port_specs.append(cls.OutputSpecType.from_xml(child))
        kwargs['input_port_specs'] = input_port_specs
        kwargs['output_port_specs'] = output_port_specs
        return cls(**kwargs)

    def all_input_port_specs(self):
        """ appends alternate specs as normal specs
        """
        input_specs = list(self.input_port_specs)
        for ispec in self.input_port_specs:
            input_specs.append(ispec)
            for aspec in ispec.alternate_specs:
                input_specs.append(aspec.full())
        return input_specs

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
    attrs = {"arg":     "",                # function argument name
             # arg_pos: argument position
             # -1=kwarg, -2=*argv, -3=*kwarg, -4=self, -5=operation
             # *-types replaces/extends arglist/dict
             "arg_pos": (-1, False, True)}
    attrs.update(InputPortSpec.attrs)

    def __init__(self, arg=None, **kwargs):
        if arg is not None:
            kwargs['arg'] = arg
        if 'name' not in kwargs and 'arg' in kwargs:
            kwargs['name'] = kwargs['arg']

        InputPortSpec.__init__(self, **kwargs)


class FunctionOutputPortSpec(OutputPortSpec):
    attrs = {"arg":     "",                           # output name
            }
    attrs.update(InputPortSpec.attrs)

    def __init__(self, arg=None, **kwargs):
        if arg is not None:
            kwargs['arg'] = arg
        if 'name' not in kwargs and 'arg' in kwargs:
            kwargs['name'] = kwargs['arg']

        OutputPortSpec.__init__(self, **kwargs)

class FunctionSpec(ModuleSpec):
    """ Specification for wrapping a python function
    """
    InputSpecType = FunctionInputPortSpec
    OutputSpecType = FunctionOutputPortSpec

    attrs = {
        # output_type tells VisTrails what the function returns
        # None - single result
        # "none" - no return value
        # "list" - ordered list
        # "dict" - dict with attr:value
        # "self" - instance passthrough for object methods
        'output_type': 'object',
        # method_type deascribes what kind of function this is
        # "function"  - a normal function (not method)
        # "method"    - class method that can have any output but
        #               may also mutate the class
        # "operation" - class method without outputs that is an input
        #               to the class and is executed within the class module
        'method_type': ('function', False, False)}
    attrs.update(ModuleSpec.attrs)


######### PYTHON CLASS SPEC ###########


class ClassInputPortSpec(InputPortSpec):
    attrs = {
        "arg": "",                   # method name
        # method_type can be
        # 'Instance' - class instances (no constructor call)
        # 'argument' - for constructor arguments,
        # 'attribute' - class attribute setter
        # 'method' - class method caller
        # or method type like 'nullary', 'OnOff' or 'SetXToY'
        "method_type": "method",
        # arg_pos: argument position (-1=kwarg, -2=*argv, -3=*kwarg,
        #                             -4=self, -5=operation)
        # *-types replaces/extends arglist/dict
        # attributes only
        "arg_pos": (-1, False, True),        # argument position (-1 means kwarg)
        "prepend_params": (None, True, True) # prepended method params like index
        }
    attrs.update(InputPortSpec.attrs)

    def __init__(self, **kwargs):
        InputPortSpec.__init__(self, **kwargs)
        if not self.arg:
            self.arg = self.name


class ClassOutputPortSpec(OutputPortSpec):
    attrs = {
        "arg": "",              # method/attribute name
        # method_type can be
        # 'Instance' - class instance
        # 'attribute' - class attribute getter
        # 'method' - class method output
        "method_type": "method",
        "prepend_params": (None, True, True) # prepended method params like index
        }
    attrs.update(OutputPortSpec.attrs)

    def __init__(self, **kwargs):
        OutputPortSpec.__init__(self, **kwargs)
        if not self.arg:
            self.arg = self.name


class ClassSpec(ModuleSpec):
    """ Specification for wrapping a python class
    """
    InputSpecType = ClassInputPortSpec
    OutputSpecType = ClassOutputPortSpec
    attrs = {
        'methods_last': (False, False, True), # If True will compute methods before connections
        'initialize': None,       # Function to call before input methods
        'compute': None,       # Function to call after input methods
        'cleanup': None,       # Function to call after output methods
        'patches': (None, True, True)} # dict(key:[patch_key]) with method patches
    attrs.update(ModuleSpec.attrs)

    def add_patch(self, method, patch_name):
        if self.patches == None:
            self.patches = dict()
        if method not in self.patches:
            self.patches[method] = []
        if patch_name not in self.patches[method]:
            self.patches[method].append(patch_name)

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
                                   entry_types=['enum'])
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
                                   arg='MyClassMethodName',
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
                                   arg='MyClassMethodName',
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

    def test_alt_spec(self):

        alt_spec = InputPortSpec(name='myportname',
                                 port_type='basic:Integer',
                                 docstring='my alternative port doc')

        input_spec = InputPortSpec(name='myaltportname',
                                   port_type='basic:String',
                                   docstring='my port doc',
                                   min_conns=1,
                                   max_conns=3,
                                   show_port=True,
                                   sort_key=5,
                                   depth=1,
                                   entry_types=['enum'],
                                   alternate_specs=[alt_spec])
        in_attrs = input_spec.get_port_attrs()

        alt_attrs = alt_spec.get_port_attrs()

        ms = ModuleSpec(module_name='myclassname',
                        superklass='mysuperclassname',
                        code_ref='theclassname',
                        docstring='my documentation',
                        callback=None,
                        tempfile=None,
                        cacheable=False,
                        input_port_specs=[input_spec])
        as_string = ET.tostring(ms.to_xml())
        from_string = ET.fromstring(as_string)
        ms2 = ModuleSpec.from_xml(from_string)
        in_attrs2 = ms2.input_port_specs[0].get_port_attrs()
        alt_attrs2 = ms2.input_port_specs[0].alternate_specs[0].get_port_attrs()
        self.assertEqual(in_attrs, in_attrs2)
        self.assertEqual(alt_attrs, alt_attrs2)


#def run():
#    specs = SpecList.read_from_xml("mpl_plots_raw.xml")
#    specs.write_to_xml("mpl_plots_raw_out.xml")

#if __name__ == '__main__':
#    run()

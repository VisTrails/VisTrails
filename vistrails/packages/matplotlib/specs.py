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

import inspect
import mixins
from xml.etree import ElementTree as ET

def capfirst(s):
    return s[0].upper() + s[1:]

_mixin_classes = None
def load_mixin_classes():
    return dict(inspect.getmembers(mixins, inspect.isclass))

def get_mixin_classes():
    global _mixin_classes
    if _mixin_classes is None:
        _mixin_classes = load_mixin_classes()
    return _mixin_classes

class SpecList(object):
    def __init__(self, module_specs=[], custom_code=""):
        self.module_specs = module_specs
        self.custom_code = custom_code

    def write_to_xml(self, fname):
        root = ET.Element("specs")
        subelt = ET.Element("customCode")
        subelt.text = self.custom_code
        root.append(subelt)
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
    def read_from_xml(fname):
        module_specs = []
        custom_code = ""
        tree = ET.parse(fname)
        for elt in tree.getroot():
            if elt.tag == "moduleSpec":
                module_specs.append(ModuleSpec.from_xml(elt))
            elif elt.tag == "customCode":
                custom_code = elt.text
        retval = SpecList(module_specs, custom_code)
        return retval

class ModuleSpec(object):
    attrs = ["name", "superklass", "docstring", "output_type"]
    def __init__(self, name, superklass, code_ref, docstring="", port_specs=[],
                 output_port_specs=[], output_type=None):
        self.name = name
        self.superklass = superklass
        self.code_ref = code_ref
        self.docstring = docstring
        self.port_specs = port_specs
        self.output_port_specs = output_port_specs
        self.output_type = output_type
        self._mixin_class = None
        self._mixin_functions = None

    def to_xml(self, elt=None):
        if elt is None:
            elt = ET.Element("moduleSpec")
        elt.set("name", self.name)
        elt.set("superclass", self.superklass)
        elt.set("code_ref", self.code_ref)
        if self.output_type is not None:
            elt.set("output_type", self.output_type)
        subelt = ET.Element("docstring")
        subelt.text = str(self.docstring)
        elt.append(subelt)
        for port_spec in self.port_specs:
            subelt = port_spec.to_xml()
            elt.append(subelt)
        for port_spec in self.output_port_specs:
            subelt = port_spec.to_xml()
            elt.append(subelt)
        return elt

    @classmethod
    def from_xml(cls, elt):
        name = elt.get("name", "")
        superklass = elt.get("superclass", "")
        code_ref = elt.get("code_ref", "")
        output_type = elt.get("output_type", None)
        docstring = ""
        port_specs = []
        output_port_specs = []
        for child in elt.getchildren():
            if child.tag == "inputPortSpec":
                port_specs.append(InputPortSpec.from_xml(child))
            elif child.tag == "outputPortSpec":
                output_port_specs.append(OutputPortSpec.from_xml(child))
            elif child.tag == "docstring":
                if child.text:
                    docstring = child.text
        return cls(name, superklass, code_ref, docstring, port_specs,
                   output_port_specs, output_type)

    def get_returned_output_port_specs(self):
        return [ps for ps in self.output_port_specs 
                if ps.property_key is not None]

    def get_input_args(self):
        args = [ps for ps in self.port_specs if ps.in_args]
        args.sort(key=lambda ps: ps.arg_pos)
        if len(args) > 1 and len(args) != (args[-1].arg_pos + 1):
            raise ValueError("Argument positions are numbered incorrectly")
        return args

    def get_output_port_spec(self, compute_name):
        for ps in self.output_port_specs:
            if ps.compute_name == compute_name:
                return ps
        return None

    def get_mixin_name(self):
        return self.name + "Mixin"
        
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

class PortSpec(object):
    xml_name = "portSpec"
    attrs = {"name": "",
             "port_type": None,
             "docstring": ("", True),
             "required": (False, False, True),
             "show_port": (False, False, True),
             "hide": (False, False, True),
             "property_type": "",}

    def __init__(self, arg, **kwargs):
        self.arg = arg
        self.set_defaults(**kwargs)

    def set_defaults(self, **kwargs):
        for attr, props in self.attrs.iteritems():
            if isinstance(props, tuple):
                default_val = props[0]
            else:
                default_val = props
            if attr in kwargs:
                setattr(self, attr, kwargs[attr])
            else:
                setattr(self, attr, default_val)

        if not self.name:
            if self.port_type == "__property__":
                self.name = self.arg + "Properties"
            else:
                self.name = self.arg

    def to_xml(self, elt=None):
        if elt is None:
            elt = ET.Element(self.xml_name)
        elt.set("arg", self.arg)
        for attr, props in self.attrs.iteritems():
            attr_val = getattr(self, attr)
            is_subelt = False
            if isinstance(props, tuple):
                default_val = props[0]
                if len(props) > 1:
                    is_subelt = props[1]
            else:
                default_val = props

            if default_val != attr_val:
                if is_subelt:
                    subelt = ET.Element(attr)
                    subelt.text = str(getattr(self, attr))
                    elt.append(subelt)
                else:
                    elt.set(attr, str(attr_val))
        return elt

    @classmethod
    def internal_from_xml(cls, elt, obj=None):
        arg = elt.get("arg", "")
        if obj is None:
            obj = cls(arg)
        else:
            obj.arg = arg

        child_elts = {}
        for child in elt.getchildren():
            if child.tag not in child_elts:
                child_elts[child.tag] = []
            child_elts[child.tag].append(child)

        kwargs = {}
        for attr, props in obj.attrs.iteritems():
            is_subelt = False
            run_eval = False
            if isinstance(props, tuple):
                if len(props) > 1:
                    is_subelt = props[1]
                if len(props) > 2:
                    run_eval = props[2]
            attr_vals = []
            if is_subelt:
                if attr in child_elts:
                    attr_vals = [c.text for c in child_elts[attr]
                                 if c.text is not None]
                    if attr == "docstring":
                        print "()() docstring attr_vals:", attr_vals
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
                        kwargs[attr] = eval(attr_val)
                    except (NameError, SyntaxError):
                        kwargs[attr] = attr_val                        
                else:
                    kwargs[attr] = attr_val
        obj.set_defaults(**kwargs)
        return obj, child_elts
        
    @classmethod
    def from_xml(cls, elt, obj=None):
        obj, child_elts = cls.internal_from_xml(elt, obj)
        return obj

    @staticmethod
    def create_from_xml(elt):
        if elt.tag == "inputPortSpec":
            return InputPortSpec.from_xml(elt)
        elif elt.tag == "outputPortSpec":
            return OutputPortSpec.from_xml(elt)
        elif elt.tag == "alternateSpec":
            return AlternatePortSpec.from_xml(elt)
        raise TypeError('Cannot create spec from element of type "%s"' %
                        elt.tag)


    def is_property(self):
        return self.port_type == "__property__"

    def get_property_type(self):
        return "Mpl%sProperties" % \
            capfirst(self.property_type.rsplit('.', 1)[1])

    def get_port_type(self):
        if self.port_type is None:
            return "basic:String"
        return self.port_type

class InputPortSpec(PortSpec):
    xml_name = "inputPortSpec"
    attrs = {"entry_types": (None, True, True),
             "values": (None, True, True),
             "defaults": (None, True, True),
             "translations": (None, True, True),
             "in_kwargs": (True, False, True),
             "in_args": (False, False, True),
             "constructor_arg": (False, False, True),
             "not_setp": (False, False, True),
             "arg_pos": (-1, False, True),
             }
    attrs.update(PortSpec.attrs)

    def __init__(self, arg, **kwargs):
        if "alternate_specs" in kwargs and kwargs["alternate_specs"]:
            self.alternate_specs = kwargs.pop("alternate_specs")
        else:
            self.alternate_specs = []
        PortSpec.__init__(self, arg, **kwargs)
        for spec in self.alternate_specs:
            spec.set_parent(self)

    def to_xml(self, elt=None):
        elt = PortSpec.to_xml(self, elt)
        for spec in self.alternate_specs:
            # write the spec
            subelt = spec.to_xml()
            elt.append(subelt)
        return elt

    @classmethod
    def from_xml(cls, elt, obj=None):
        obj, child_elts = cls.internal_from_xml(elt, obj)

        if "alternateSpec" in child_elts:
            for child_elt in child_elts["alternateSpec"]:
                spec = AlternatePortSpec.from_xml(child_elt)
                spec.set_parent(obj)
                obj.alternate_specs.append(spec)
                
        return obj

    def get_port_attr_dict(self):
        attrs = {}
        if self.values:
            attrs["values"] = str(self.values)
        if self.entry_types:
            attrs["entry_types"] = str(self.entry_types)
        if self.defaults:
            attrs["defaults"] = str(self.defaults)
        if self.docstring:
            attrs["docstring"] = self.docstring
        if not self.required and not self.show_port:
            attrs["optional"] = True
        return attrs

    def get_port_attrs(self):
        return str(self.get_port_attr_dict())

    def has_alternate_versions(self):
        return len(self.alternate_specs) > 0

class AlternatePortSpec(InputPortSpec):
    xml_name = "alternateSpec"
    def __init__(self, *args, **kwargs):
        if len(args) < 1:
            args = [""]
        InputPortSpec.__init__(self, *args, **kwargs)
        self._parent = None

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
        self.arg = self._parent.arg

    def get_port_attr_dict(self):
        print "CALLING AlternatePortSpec.get_port_attr_dict", self.arg
        my_attrs = InputPortSpec.get_port_attr_dict(self)
        print "=> my_attrs:", my_attrs
        par_attrs = self._parent.get_port_attr_dict()
        print "=> par_attrs:", par_attrs
        for k, v in par_attrs.iteritems():
            if k == 'defaults' or k == "values" or k == "entry_types" or \
                    k == "translations":
                continue
            if k not in my_attrs or my_attrs[k] is None:
                my_attrs[k] = v
        print my_attrs
        return my_attrs

class OutputPortSpec(PortSpec):
    xml_name = "outputPortSpec"
    attrs = {"compute_name": "",
             "property_key": None,
             "plural": (False, False, True),
             "compute_parent": "",
             }
    attrs.update(PortSpec.attrs)
    
    def set_defaults(self, **kwargs):
        PortSpec.set_defaults(self, **kwargs)
        if self.compute_name == "":
            if self.plural and self.is_property():
                self.compute_name = self.arg + 's'
            else:
                self.compute_name = self.arg

    @classmethod
    def from_xml(cls, elt, obj=None):
        obj, child_elts = cls.internal_from_xml(elt, obj)

        output_type = elt.get("output_type")
        if output_type is not None:
            obj.port_type = output_type
        return obj

    def get_port_attrs(self):
        attrs = {}
        if self.docstring:
            attrs["docstring"] = self.docstring
        return str(attrs)
             

# class OutputPortSpec(object):
#     attrs = ["name", "compute_name", "output_type", "docstring",
#              "property_type", "property_key", "plural", "compute_parent"]
#     def __init__(self, arg, name, compute_name, output_type, docstring="",
#                  property_type="", property_key=None, plural=False, 
#                  compute_parent=""):
#         self.arg = arg
#         self.name = name
#         self.compute_name = compute_name
#         self.output_type = output_type
#         self.docstring = docstring
#         self.property_type = property_type
#         self.property_key = property_key
#         self.plural = plural
#         self.compute_parent = compute_parent

#         self._property_name = None

#     def to_xml(self, elt=None):
#         if elt is None:
#             elt = ET.Element("outputPortSpec")
#         elt.set("arg", self.arg)
#         elt.set("name", self.name)
#         elt.set("compute_name", self.compute_name)
#         if self.output_type is not None:
#             elt.set("output_type", self.output_type)
#         else:
#             elt.set("output_type", "__unknown__")
#         elt.set("property_type", self.property_type)
#         if self.property_key is None:
#             elt.set("property_key", "__none__")
#         else:
#             elt.set("property_key", str(self.property_key))
#         elt.set("plural", str(self.plural))
#         elt.set("compute_parent", self.compute_parent)
                
#         subelt = ET.Element("docstring")
#         subelt.text = str(self.docstring)
#         elt.append(subelt)
#         return elt

#     @classmethod
#     def from_xml(cls, elt):
#         arg = elt.get("arg", "")
#         output_type = elt.get("output_type", "")
#         if output_type == "__unknown__":
#             output_type = None
#         plural = eval(elt.get("plural", "False"))
        
#         if output_type.lower() == "__property__":
#             name = elt.get("name", arg + "Properties")
#             compute_name = elt.get("compute_name", arg + 
#                                    ("s" if plural else ""))
#         else:
#             name = elt.get("name", arg)
#             compute_name = elt.get("name", arg)
#         property_type = elt.get("property_type", "")
#         property_key = elt.get("property_key", None)
#         if property_key is not None:
#             if property_key == "__none__":
#                 property_key = None
#             else:
#                 try:
#                     property_key = int(property_key)
#                 except ValueError:
#                     pass
#         compute_parent = elt.get("compute_parent", "")
#         docstring = ""
#         for child in elt.getchildren():
#             if child.tag == "docstring" and child.text:
#                 docstring = child.text
#         return cls(arg, name, compute_name, output_type, docstring,
#                    property_type, property_key, plural, compute_parent)

#     def is_property_output(self):
#         return self.output_type.lower() == "__property__"

#     def get_property_type(self):
#         return "Mpl%sProperties" % \
#             capfirst(self.property_type.rsplit('.', 1)[1])

#     def get_port_type(self):
#         if self.output_type is None:
#             return "basic:String"
#         return self.output_type

# class InputPortSpec(PortSpec):
#     def __init__(self, arg="", name="", port_type=None, docstring="", 
#                  required=False, show_port=False, hide=False, property_type="",
#                  entry_types=None, values=None, defaults=None,
#                  translations=None, alternate_specs=None, in_kwargs=True,
#                  in_args=False, constructor_arg=False):
#         PortSpec.__init__(self, arg, name, port_type, docstring, required,
#                           show_port, hide, property_type)
#         self.entry_types = entry_types
#         self.values = values
#         self.defaults = defaults
#         self.translations = translations
#         self.in_kwargs = in_kwargs
#         self.in_args = in_args
#         self.constructor_arg = constructor_arg
#         if alternate_specs is None:
#             self.alternate_specs = []
#         else:
#             self.alternate_specs = alternate_specs
#         for spec in self.alternate_specs:
#             spec.set_parent(self)

#     def to_xml(self, elt=None):
#         if elt is None:
#             elt = ET.Element("inputPortSpec")
#         PortSpec.to_xml(self, elt)
#         elt.set("in_kwargs", str(self.in_kwargs))
#         elt.set("in_args", str(self.in_args))
#         elt.set("constructor_arg", str(self.constructor_arg))
#         if self.entry_types is not None:
#             subelt = ET.Element("entry_types")
#             subelt.text = str(self.entry_types)
#             elt.append(subelt)
#         if self.values is not None:
#             subelt = ET.Element("values")
#             subelt.text = str(self.values)
#             elt.append(subelt)
#         if self.translations is not None:
#             subelt = ET.Element("translations")
#             subelt.text = str(self.translations)
#             elt.append(subelt)
#         if self.defaults is not None:
#             subelt = ET.Element("defaults")
#             subelt.text = str(self.defaults)
#             elt.append(subelt)
#         for spec in self.alternate_specs:
#             # print "FOUND ALT:", spec.name, spec.alternate_specs, spec
#             subelt = ET.Element("alternateSpec")
#             spec.to_xml(subelt)
#             elt.append(subelt)
#         # if self.entry_types is not None and self.values is not None and \
#         #         self.defaults is not None and self.translations is not None:
#         #     for entry_type, value, default, translation in \
#         #             izip(self.entry_types, self.values, self.defaults,
#         #                  self.translations):
#         #         subelt = ET.Element("entry")
#         #         subelt.set("type", str(entry_type))
#         #         valueselt = ET.Element("values")
#         #         valueselt.text = str(value)
#         #         subelt.append(valueselt)
#         #         transelt = ET.Element("translation")
#         #         transelt.text = str(translation)
#         #         subelt.append(transelt)
#         #         defaultelt = ET.Element("default")
#         #         if isinstance(default, basestring):
#         #             defaultelt.text = "'%s'" % default
#         #         else:
#         #             defaultelt.text = str(default)
#         #         subelt.append(defaultelt)
#         #         elt.append(subelt)
#         docelt = ET.Element("docstring")
#         docelt.text = self.docstring
#         elt.append(docelt)
#         return elt

#     @classmethod
#     def from_xml(cls, elt):
#         arg = elt.get("arg", "")
#         port_type = elt.get("port_type", "")
#         if port_type == "__unknown__":
#             port_type = None
#         required = eval(elt.get("required", "False"))
#         hide = eval(elt.get("hide", "False"))
#         in_kwargs = eval(elt.get("in_kwargs", "True"))
#         property_type = elt.get("property_type", "")
#         constructor_arg = eval(elt.get("constructor_arg", "False"))
#         if port_type is not None and port_type.lower() == "__property__":
#             name = elt.get("name", arg + "Properties")
#         else:
#             name = elt.get("name", arg)
#         entry_types = None
#         values = None
#         defaults = None
#         translations = None
#         docstring = ""
#         alternate_specs = []
#         for child in elt.getchildren():
#             if child.tag == "entry_types":
#                 entry_types = eval(child.text)
#             elif child.tag == "values":
#                 try:
#                     values = eval(child.text)
#                 except SyntaxError:
#                     values = [[child.text[2:-2]]]
#             elif child.tag == "translations":
#                 try:
#                     translations = eval(child.text)
#                 except NameError:
#                     translations = child.text
#             elif child.tag == "defaults":
#                 if child.text:
#                     defaults = eval(child.text)
#             elif child.tag == "docstring":
#                 if child.text:
#                     docstring = child.text
#             elif child.tag == "alternateSpec":
#                 alternate_specs.append(AlternatePortSpec.from_xml(child))

#             # if child.tag == "entry":
#             #     if entry_types is None:
#             #         entry_types = []
#             #         values = []
#             #         defaults = []
#             #         translations = []
#             #     entry_types.append(child.get("type", None))
#             #     for subchild in child.getchildren():
#             #         if subchild.tag == "values":
#             #             values.append(eval(subchild.text))
#             #         elif subchild.tag == "translation":
#             #             try:
#             #                 translation = eval(subchild.text)
#             #             except NameError:
#             #                 translation = subchild.text
#             #             translations.append(translation)
#             #         elif subchild.tag == "default":
#             #             defaults.append(eval(subchild.text))
#             # elif child.tag == "docstring":
#             #     docstring = child.text

#         return cls(arg, name, port_type, docstring, required, hide, 
#                    entry_types, values, defaults, translations, 
#                    alternate_specs, in_kwargs, property_type, constructor_arg)


#     # def has_scalar_version(self):
#     #     return self.scalar_type and self.scalar_type != self.port_type

#     # def get_scalar_name(self):
#     #     return self.name + "Scalar"

#     # def has_sequence_version(self):
#     #     return self.sequence_type and self.sequence_type != self.port_type

#     # def get_sequence_name(self):
#     #     return self.name + "Sequence"

#     # def has_other_version(self):
#     #     return self.has_scalar_version() or self.has_sequence_version()

#     # def get_other_name(self):
#     #     if self.has_scalar_version():
#     #         return self.get_scalar_name()
#     #     elif self.has_sequence_version():
#     #         return self.get_sequence_name()
#     #     return None

#     # def get_other_type(self):
#     #     if self.has_scalar_version():
#     #         return self.scalar_type
#     #     elif self.has_sequence_version():
#     #         return self.sequence_type
#     #     return None

def run():
    specs = SpecList.read_from_xml("mpl_plots_raw.xml")
    specs.write_to_xml("mpl_plots_raw_out.xml")

if __name__ == '__main__':
    run()

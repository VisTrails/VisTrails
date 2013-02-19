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
        # for spec in retval.module_specs:
        #     print "==", spec.name, "=="
        #     for ps in spec.port_specs:
        #         print " ", ps.arg, ps.name
        #         for alt_ps in ps.alternate_specs:
        #             print "  !!!", ps.arg, ps.name, alt_ps.name
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
            if child.tag == "portSpec":
                port_specs.append(PortSpec.from_xml(child))
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
    # FIXME add optional
    attrs = ["name", "port_type", "docstring", "required", "hide", 
             "entry_types", "values", "defaults", "translations", "in_kwargs"]
    def __init__(self, arg="", name="", port_type=None, docstring="", 
                 required=False,
                 hide=False, entry_types=None, values=None, defaults=None,
                 translations=None, alternate_specs=None, in_kwargs=True):
        self.arg = arg
        self.name = name
        self.port_type = port_type
        self.docstring = docstring
        self.required = required
        self.hide = hide
        self.in_kwargs = in_kwargs
        self.entry_types = entry_types
        self.values = values
        self.defaults = defaults
        self.translations = translations
        if alternate_specs is None:
            self.alternate_specs = []
        else:
            self.alternate_specs = alternate_specs
        for spec in self.alternate_specs:
            spec.set_parent(self)

    def to_xml(self, elt=None):
        if elt is None:
            elt = ET.Element("portSpec")
        elt.set("arg", self.arg)
        elt.set("name", self.name)
        if self.port_type is not None:
            elt.set("port_type", self.port_type)
        else:
            elt.set("port_type", "__unknown__")
        elt.set("required", str(self.required))
        elt.set("hide", str(self.hide))
        elt.set("in_kwargs", str(self.in_kwargs))
        if self.entry_types is not None:
            subelt = ET.Element("entry_types")
            subelt.text = str(self.entry_types)
            elt.append(subelt)
        if self.values is not None:
            subelt = ET.Element("values")
            subelt.text = str(self.values)
            elt.append(subelt)
        if self.translations is not None:
            subelt = ET.Element("translations")
            subelt.text = str(self.translations)
            elt.append(subelt)
        if self.defaults is not None:
            subelt = ET.Element("defaults")
            subelt.text = str(self.defaults)
            elt.append(subelt)
        for spec in self.alternate_specs:
            # print "FOUND ALT:", spec.name, spec.alternate_specs, spec
            subelt = ET.Element("alternateSpec")
            spec.to_xml(subelt)
            elt.append(subelt)
        # if self.entry_types is not None and self.values is not None and \
        #         self.defaults is not None and self.translations is not None:
        #     for entry_type, value, default, translation in \
        #             izip(self.entry_types, self.values, self.defaults,
        #                  self.translations):
        #         subelt = ET.Element("entry")
        #         subelt.set("type", str(entry_type))
        #         valueselt = ET.Element("values")
        #         valueselt.text = str(value)
        #         subelt.append(valueselt)
        #         transelt = ET.Element("translation")
        #         transelt.text = str(translation)
        #         subelt.append(transelt)
        #         defaultelt = ET.Element("default")
        #         if isinstance(default, basestring):
        #             defaultelt.text = "'%s'" % default
        #         else:
        #             defaultelt.text = str(default)
        #         subelt.append(defaultelt)
        #         elt.append(subelt)
        docelt = ET.Element("docstring")
        docelt.text = self.docstring
        elt.append(docelt)
        return elt

    @classmethod
    def from_xml(cls, elt):
        arg = elt.get("arg", "")
        name = elt.get("name", "")
        port_type = elt.get("port_type", "")
        if port_type == "__unknown__":
            port_type = None
        required = eval(elt.get("required", "False"))
        hide = eval(elt.get("hide", "False"))
        in_kwargs = eval(elt.get("in_kwargs", "True"))
        entry_types = None
        values = None
        defaults = None
        translations = None
        docstring = ""
        alternate_specs = []
        for child in elt.getchildren():
            if child.tag == "entry_types":
                entry_types = eval(child.text)
            elif child.tag == "values":
                try:
                    values = eval(child.text)
                except SyntaxError:
                    values = [[child.text[2:-2]]]
            elif child.tag == "translations":
                try:
                    translations = eval(child.text)
                except NameError:
                    translations = child.text
            elif child.tag == "defaults":
                if child.text:
                    defaults = eval(child.text)
            elif child.tag == "docstring":
                if child.text:
                    docstring = child.text
            elif child.tag == "alternateSpec":
                alternate_specs.append(AlternatePortSpec.from_xml(child))

            # if child.tag == "entry":
            #     if entry_types is None:
            #         entry_types = []
            #         values = []
            #         defaults = []
            #         translations = []
            #     entry_types.append(child.get("type", None))
            #     for subchild in child.getchildren():
            #         if subchild.tag == "values":
            #             values.append(eval(subchild.text))
            #         elif subchild.tag == "translation":
            #             try:
            #                 translation = eval(subchild.text)
            #             except NameError:
            #                 translation = subchild.text
            #             translations.append(translation)
            #         elif subchild.tag == "default":
            #             defaults.append(eval(subchild.text))
            # elif child.tag == "docstring":
            #     docstring = child.text
        return cls(arg, name, port_type, docstring, required, hide, 
                   entry_types, values, defaults, translations, 
                   alternate_specs, in_kwargs)

    def get_port_type(self):
        if self.port_type is None:
            return "basic:String"
        return self.port_type

    def get_port_attr_dict(self):
        attrs = {}
        if self.hide:
            attrs["optional"] = True
        if self.values:
            attrs["values"] = str(self.values)
        if self.entry_types:
            attrs["entry_types"] = str(self.entry_types)
        if self.defaults:
            attrs["defaults"] = str(self.defaults)
        if self.docstring:
            attrs["docstring"] = self.docstring
        if not self.required:
            attrs["optional"] = True
        return attrs

    def get_port_attrs(self):
        return str(self.get_port_attr_dict())

    # def has_scalar_version(self):
    #     return self.scalar_type and self.scalar_type != self.port_type

    # def get_scalar_name(self):
    #     return self.name + "Scalar"

    # def has_sequence_version(self):
    #     return self.sequence_type and self.sequence_type != self.port_type

    # def get_sequence_name(self):
    #     return self.name + "Sequence"

    # def has_other_version(self):
    #     return self.has_scalar_version() or self.has_sequence_version()

    # def get_other_name(self):
    #     if self.has_scalar_version():
    #         return self.get_scalar_name()
    #     elif self.has_sequence_version():
    #         return self.get_sequence_name()
    #     return None

    # def get_other_type(self):
    #     if self.has_scalar_version():
    #         return self.scalar_type
    #     elif self.has_sequence_version():
    #         return self.sequence_type
    #     return None

    def has_alternate_versions(self):
        return len(self.alternate_specs) > 0

class AlternatePortSpec(PortSpec):
    attrs = ["name", "port_type", "docstring", "required", "hide", 
             "entry_types", "values", "defaults", "translations"]

    def __init__(self, *args, **kwargs):
        PortSpec.__init__(self, *args, **kwargs)
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
            
    def to_xml(self, elt=None):
        if elt is None:
            elt = ET.Element("alternateSpec")
        return PortSpec.to_xml(self, elt)

    def get_port_attr_dict(self):
        attrs = PortSpec.get_port_attr_dict(self)
        par_attrs = self._parent.get_port_attr_dict()
        for k, v in par_attrs.iteritems():
            if k not in attrs:
                attrs[k] = v
        return str(attrs)

class OutputPortSpec(object):
    attrs = ["name", "compute_name", "output_type", "docstring",
             "property_type", "property_key", "plural", "compute_parent"]
    def __init__(self, arg, name, compute_name, output_type, docstring="",
                 property_type="", property_key=None, plural=False, 
                 compute_parent=""):
        self.arg = arg
        self.name = name
        self.compute_name = compute_name
        self.output_type = output_type
        self.docstring = docstring
        self.property_type = property_type
        self.property_key = property_key
        self.plural = plural
        self.compute_parent = compute_parent

        self._property_name = None

    def to_xml(self, elt=None):
        if elt is None:
            elt = ET.Element("outputPortSpec")
        elt.set("arg", self.arg)
        elt.set("name", self.name)
        elt.set("compute_name", self.compute_name)
        if self.output_type is not None:
            elt.set("output_type", self.output_type)
        else:
            elt.set("output_type", "__unknown__")
        elt.set("property_type", self.property_type)
        if self.property_key is None:
            elt.set("property_key", "__none__")
        else:
            elt.set("property_key", str(self.property_key))
        elt.set("plural", str(self.plural))
        elt.set("compute_parent", self.compute_parent)
                
        subelt = ET.Element("docstring")
        subelt.text = str(self.docstring)
        elt.append(subelt)
        return elt

    @classmethod
    def from_xml(cls, elt):
        arg = elt.get("arg", "")
        output_type = elt.get("output_type", "")
        if output_type == "__unknown__":
            output_type = None
        plural = eval(elt.get("plural", "False"))
        
        if output_type.lower() == "__property__":
            name = elt.get("name", arg + "Properties")
            compute_name = elt.get("compute_name", arg + 
                                   ("s" if plural else ""))
        else:
            name = elt.get("name", arg)
            compute_name = elt.get("name", arg)
        property_type = elt.get("property_type", "")
        property_key = elt.get("property_key", None)
        if property_key is not None:
            if property_key == "__none__":
                property_key = None
            else:
                try:
                    property_key = int(property_key)
                except ValueError:
                    pass
        compute_parent = elt.get("compute_parent", "")
        docstring = ""
        for child in elt.getchildren():
            if child.tag == "docstring" and child.text:
                docstring = child.text
        return cls(arg, name, compute_name, output_type, docstring,
                   property_type, property_key, plural, compute_parent)

    def is_property_output(self):
        return self.output_type.lower() == "__property__"

    def get_property_type(self):
        return "Mpl%sProperties" % \
            capfirst(self.property_type.rsplit('.', 1)[1])

    def get_port_attrs(self):
        attrs = {}
        if self.docstring:
            attrs["docstring"] = self.docstring
        return str(attrs)

    def get_port_type(self):
        if self.output_type is None:
            return "basic:String"
        return self.output_type

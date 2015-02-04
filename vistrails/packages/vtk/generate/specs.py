
import ast
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
    """ A class with module specifications and custom code
        This describes how the wrapped methods/classes will
        maps to modules in vistrails
    """

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
        return retval

class ModuleSpec(object):
    """ Represents specification of a module
        This mirrors how the module will look in the vistrails registry
    """

    attrs = ["name", "superklass", "docstring", "cacheable"]
    def __init__(self, name, superklass, docstring="", port_specs=None,
                 output_port_specs=None, cacheable=True):
        if port_specs is None:
            port_specs = []
        if output_port_specs is None:
            output_port_specs = []
        self.name = name
        self.superklass = superklass # parent module to subclass from
        self.docstring = docstring
        self.port_specs = port_specs
        self.output_port_specs = output_port_specs
        self.cacheable = cacheable
        self._mixin_class = None
        self._mixin_functions = None

    def to_xml(self, elt=None):
        if elt is None:
            elt = ET.Element("moduleSpec")
        elt.set("name", self.name)
        elt.set("superclass", self.superklass)
        if self.cacheable is False:
            elt.set("cacheable", unicode(self.cacheable))
        subelt = ET.Element("docstring")
        subelt.text = unicode(self.docstring)
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
        cacheable = ast.literal_eval(elt.get("cacheable", "True"))
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
        return cls(name, superklass, docstring, port_specs,
                   output_port_specs, cacheable)

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

class VTKModuleSpec(ModuleSpec):
    """ Represents specification of a vtk module

        Adds attribute is_algorithm
    """

    attrs = ["superklass"]
    attrs.update(ModuleSpec.attrs)

    def __init__(self, name, superklass, code_ref, docstring="", port_specs=None,
                 output_port_specs=None, cacheable=True,
                 is_algorithm=False):
        ModuleSpec.__init__(self, name, superklass, code_ref, docstring,
                            port_specs, output_port_specs,
                            cacheable)
        self.is_algorithm = is_algorithm

    def to_xml(self, elt=None):
        elt = ModuleSpec.to_xml(self, elt)
        if self.is_algorithm is True:
            elt.set("is_algorithm", unicode(self.is_algorithm))
        return elt

    @classmethod
    def from_xml(cls, elt):
        inst = ModuleSpec.from_xml(cls, elt)
        inst.is_algorithm = ast.literal_eval(elt.get("is_algorithm", "False"))
        return inst


class PortSpec(object):
    """ Represents specification of a port
    """
    xml_name = "portSpec"
    # attrs tuple means (default value, [is subelement, [run eval]])
    # FIXME: subelement/eval not needed if using json
    attrs = {"name": "",                         # port name
             "method_name": "",                  # method/attribute name
             "port_type": None,                  # type class in vistrails
             "docstring": ("", True),            # documentation
             "min_conn": (0, False, True),       # set min_conn (1=required)
             "max_conn": (-1, False, True),      # Set max_conn (default -1)
             "show_port": (False, False, True),  # Set not optional (use connection)
             "hide": (False, False, True),       # hides/disables port (is this needed?)
             "other_params": (None, True, True)} # prepended params used with indexed methods

    def __init__(self, arg, **kwargs):
        self.arg = arg
        self.set_defaults(**kwargs)
        self.port_types = []

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
            self.name = self.arg

        if not self.method_name:
            self.method_name = self.name

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
                    subelt.text = unicode(getattr(self, attr))
                    elt.append(subelt)
                else:
                    elt.set(attr, unicode(attr_val))
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
            # if child.tag not in obj.attrs:
            #     raise RuntimeError('Cannot deal with tag "%s"' % child.tag)
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

    @staticmethod
    def create_from_xml(elt):
        if elt.tag == "inputPortSpec":
            return InputPortSpec.from_xml(elt)
        elif elt.tag == "outputPortSpec":
            return OutputPortSpec.from_xml(elt)
        raise TypeError('Cannot create spec from element of type "%s"' %
                        elt.tag)

    def get_port_type(self):
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
        
    def get_port_shape(self):
        """ TODO: Is this needed for vtk?
        """

        if self.port_type is not None:
            try:
                port_types = ast.literal_eval(self.port_type)
                def build_shape(t):
                    if not isinstance(t, list):
                        raise Exception("Expected a list for " + str(t))
                    shape = []
                    count = 0
                    for elt in t:
                        if isinstance(elt, list):
                            if count > 0:
                                shape.append(count)
                            shape.append(build_shape(elt))
                        else:
                            count += 1
                    if count > 0:
                        shape.append(count)
                    return shape
                return build_shape(port_types)
            except (SyntaxError, ValueError):
                pass
        return None

    def get_other_params(self):
        if self.other_params is None:
            return []
        return self.other_params

class InputPortSpec(PortSpec):
    xml_name = "inputPortSpec"
    attrs = {"entry_types": (None, True, True),# custom entry type (like enum)
             "values": (None, True, True),     # values for enums
             "defaults": (None, True, True),   # default value list
             "translations": (None, True, True), # value translating method specified in the mako
             }
    attrs.update(PortSpec.attrs)

    def __init__(self, arg, **kwargs):
        PortSpec.__init__(self, arg, **kwargs)

    def get_port_attr_dict(self):
        attrs = {}
        if self.values:
            attrs["values"] = unicode(self.values)
        if self.entry_types:
            attrs["entry_types"] = unicode(self.entry_types)
        if self.defaults:
            attrs["defaults"] = unicode(self.defaults)
        if self.docstring:
            attrs["docstring"] = self.docstring
        if self.min_conn:
            attrs["min_conn"] = self.min_conn
        if self.max_conn:
            attrs["max_conn"] = self.max_conn
        if not self.show_port:
            attrs["optional"] = True
        return attrs

    def get_port_attrs(self):
        return unicode(self.get_port_attr_dict())

class OutputPortSpec(PortSpec):
    xml_name = "outputPortSpec"
    attrs = {"compute_name": "",
             "compute_parent": "",
             }
    attrs.update(PortSpec.attrs)
    
    def set_defaults(self, **kwargs):
        PortSpec.set_defaults(self, **kwargs)
        if self.compute_name == "":
            self.compute_name = self.arg

    @classmethod
    def from_xml(cls, elt, obj=None):
        obj, child_elts = cls.internal_from_xml(elt, obj)
        return obj

    def get_port_attrs(self):
        attrs = {}
        if self.docstring:
            attrs["docstring"] = self.docstring
        if self.min_conn:
            attrs["min_conn"] = self.min_conn
        if self.max_conn:
            attrs["max_conn"] = self.max_conn
        if not self.show_port:
            attrs["optional"] = True
        return unicode(attrs)

#def run():
#    specs = SpecList.read_from_xml("mpl_plots_raw.xml")
#    specs.write_to_xml("mpl_plots_raw_out.xml")

#if __name__ == '__main__':
#    run()

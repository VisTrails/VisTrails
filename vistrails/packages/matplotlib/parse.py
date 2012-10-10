from xml.etree import ElementTree as ET
from itertools import izip
import inspect
import matplotlib
matplotlib.use('Qt4Agg')
import matplotlib.pyplot
import sys
import re

sys.path.append('/vistrails/src/git/vistrails')
from core.modules.utils import expand_port_spec_string

plot_types = ['acorr', 'bar', 'barbs', 'barh', 'boxplot', 'broken_barh', 'cohere', 'contour', 'contourf', 'csd', 'errorbar', 'hexbin', 'hist', 'loglog', 'pcolor', 'pcolormesh', 'pie', 'plot', 'plot_date', 'pie', 'polar', 'psd', 'quiver', 'scatter', 'semilogx', 'semilogy', 'specgram', 'spy', 'stem', 'tricontour', 'tricontourf', 'tripcolor', 'triplot', 'xcorr']

plot_types = ['bar', 'boxplot', 'contour', 'hist', 'plot', 'scatter', 'legend']

class SpecList(object):
    def __init__(self, module_specs=[]):
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
    def read_from_xml(fname):
        module_specs = []
        tree = ET.parse(fname)
        for elt in tree.getroot():
            module_specs.append(ModuleSpec.from_xml(elt))
        return SpecList(module_specs)

class ModuleSpec(object):
    def __init__(self, name, superklass, plot_type, port_specs=[]):
        self.name = name
        self.superklass = superklass
        self.plot_type = plot_type
        self.port_specs = port_specs

    def to_xml(self):
        elt = ET.Element("moduleSpec")
        elt.set("name", self.name)
        elt.set("superclass", self.superklass)
        elt.set("plot_type", self.plot_type)
        for port_spec in self.port_specs:
            subelt = port_spec.to_xml()
            elt.append(subelt)
        return elt

    @staticmethod
    def from_xml(elt):
        name = elt.get("name", "")
        superklass = elt.get("superclass", "")
        plot_type = elt.get("plot_type", "")
        port_specs = []
        for child in elt.getchildren():
            port_specs.append(PortSpec.from_xml(child))
        return ModuleSpec(name, superklass, plot_type, port_specs)


class PortSpec(object):
    # FIXME add optional
    def __init__(self, name, port_type, docstring, hide=False,
                 entry_types=None, values=None, defaults=None,
                 translations=None):
        self.name = name
        self.port_type = port_type
        self.docstring = docstring
        self.hide = hide
        self.entry_types = entry_types
        self.values = values
        self.defaults = defaults
        self.translations = translations

    def to_xml(self):
        elt = ET.Element("portSpec")
        elt.set("name", self.name)
        elt.set("port_type", self.port_type)
        elt.set("hide", str(self.hide))
        if self.entry_types is not None and self.values is not None and \
                self.defaults is not None and self.translations is not None:
            for entry_type, value, default, translation in \
                    izip(self.entry_types, self.values, self.defaults,
                         self.translations):
                subelt = ET.Element("entry")
                subelt.set("type", str(entry_type))
                valueselt = ET.Element("values")
                valueselt.text = str(value)
                subelt.append(valueselt)
                transelt = ET.Element("translation")
                transelt.text = str(translation)
                subelt.append(transelt)
                defaultelt = ET.Element("default")
                if isinstance(default, basestring):
                    defaultelt.text = "'%s'" % default
                else:
                    defaultelt.text = str(default)
                subelt.append(defaultelt)
                elt.append(subelt)
        docelt = ET.Element("docstring")
        docelt.text = self.docstring
        elt.append(docelt)
        return elt

    @staticmethod
    def from_xml(elt):
        name = elt.get("name", "")
        port_type = elt.get("port_type", "")
        hide = eval(elt.get("hide", "False"))
        entry_types = None
        values = None
        defaults = None
        translations = None
        docstring = ""
        for child in elt.getchildren():
            if child.tag == "entry":
                if entry_types is None:
                    entry_types = []
                    values = []
                    defaults = []
                    translations = []
                entry_types.append(child.get("type", None))
                for subchild in child.getchildren():
                    if subchild.tag == "values":
                        values.append(eval(subchild.text))
                    elif subchild.tag == "translation":
                        try:
                            translation = eval(subchild.text)
                        except NameError:
                            translation = subchild.text
                        translations.append(translation)
                    elif subchild.tag == "default":
                        defaults.append(eval(subchild.text))
            elif child.tag == "docstring":
                docstring = child.text
        return PortSpec(name, port_type, docstring, hide, entry_types, values,
                        defaults, translations)

def get_translate_dict(klass, attr, docstring):
    attr = "set_%s" % attr
    # print "== %s.%s ==" % (klass.__name__, attr)
    line_iter = docstring.split('\n').__iter__()
    table_dict = {}
    for line in line_iter:
        table_start = ''.join(line.strip().split())
        if len(table_start) > 0 and table_start == '=' * len(table_start):
            header_line = line_iter.next()
            header_line2 = line_iter.next()
            # print header_line2.strip().split()
            lengths = [len(x) for x in header_line2.strip().split()]
            starts = [sum(lengths[:i]) for i in xrange(len(lengths))]
            for line in line_iter:
                table_end = ''.join(line.strip().split())
                if len(table_end) > 0 and table_end == '=' * len(table_end):
                    break
                # line = line.strip().replace('``','')
                # # for col in line.split():
                # (arg, desc) = line.split(None, 1)
                # print "+%s+%s+" % (arg.strip(), desc.strip())
                # table_dict[desc.strip()] = arg.strip()[1:-1]
                line = line.strip()
                fields = []
                for i in xrange(len(starts)):
                    if i < len(starts)-1:
                        fields.append(line[starts[i]:starts[i]+lengths[i]])
                    else:
                        fields.append(line[starts[i]:].strip())
                # print "fields:", fields
                arg = fields[0].strip().replace('``','')
                if arg[0] == arg[-1] == "'":
                    arg = arg[1:-1]
                else:
                    try:
                        arg = getattr(sys.modules[klass.__module__], arg)
                    except AttributeError:
                        try:
                            arg = eval(arg)
                        except SyntaxError:
                            pass
                desc = fields[1].strip()
                table_dict[desc] = arg
    return table_dict

def parse_table(line_iter, line):
    if line.replace(' ', '=') != '=' * len(line):
        raise Exception("Not the start of a table")
    col_lens = [len(x) for x in line.split()]
    col_spaces = [len(x) for x in re.split("=+", line) if len(x) > 0]
    # print col_lens, col_spaces
    col_idxs = [sum(col_lens[:i]) + sum(col_spaces[:i]) for i in xrange(len(col_lens)+1)]
    header_line = line_iter.next().strip()
    headers = [header_line[col_idxs[i]:col_idxs[i+1]].strip() 
               for i in xrange(len(col_lens))]
    # print "HEADERS:", headers
    line = line_iter.next()
    rows = []
    for line in line_iter:
        line = line.strip()
        if line.replace(' ', '=') == '=' * len(line):
            break
        rows.append([line[col_idxs[i]:col_idxs[i+1]].strip() 
                     for i in xrange(len(col_lens))])
    # print "COLS:", cols
    return rows, headers

def process_accepts(value_lines):
    line = ' '.join(x.strip() for x in value_lines)
    vals = [v.strip() for v in line[line.find('[')+1:line.find(']')].split('|')]
    clean_vals = []
    for v in vals:
        if v.startswith("'") and v.endswith("'"):
            clean_vals.append(v[1:-1])
        else:
            clean_vals.append(v)
    # print "$$$$ VALUES:", clean_vals
    return clean_vals

def parse_desc(port_desc):
    option_strs = []
    port_types = []
    if port_desc.startswith('['):
        # have a list of possible
        options = port_desc[1:-1].split('|')
        allows_none = False
        for option in options:
            option = option.strip()
            if option.startswith("'") or option.startswith('"'):
                option_strs.append(option[1:-1])
                port_types.append("String")
            elif option.lower() == 'string':
                port_types.append("String")
            elif option.lower() == 'integer':
                port_types.append("Integer")
            elif option.lower() == 'sequence':
                port_types.append("List")
            elif option.lower() == 'float':
                port_types.append("Float")
            elif option.lower() == 'true':
                port_types.append("Boolean")
            elif option.lower() == 'false':
                port_types.append("Boolean")
            elif option.lower() == 'none':
                allows_none = True
            # print "OPTIONS:", options
        print "PORT TYPES:", port_types
        print "OPTION STRS:", option_strs
        print "ALLOWS NONE:", allows_none
    else:
        print "UNKNOWN:", port_desc
    return port_types, option_strs

def get_type_from_val(val):
    if type(val) == float:
        return "Float"
    elif type(val) == int:
        return "Integer"
    elif isinstance(val, basestring):
        return "String"
    elif type(val) == bool:
        return "Boolean"
    elif type(val) == list:
        return "List"
    return "UNKNOWN"

def parse_plots():
    module_specs = []
    for plot in plot_types:
        port_specs = {}
        print "========================================"
        print plot
        print "========================================"
        plot_obj = getattr(matplotlib.pyplot, plot)
        argspec = inspect.getargspec(plot_obj)
        print argspec
        if argspec.defaults is None:
            start_defaults = len(argspec.args) + 1
        else:
            start_defaults = len(argspec.args) - len(argspec.defaults)
        for i, arg in enumerate(argspec.args):
            port_specs[arg] = PortSpec(arg, "UNKNOWN", "")
            if i >= start_defaults:
                default_val = argspec.defaults[i-start_defaults]
                port_specs[arg].defaults = [default_val]
                if default_val is not None:
                    print "GOT DEFAULT_VAL:", default_val
                    port_specs[arg].port_type = get_type_from_val(default_val)
                port_specs[arg].entry_types = [None,]
                port_specs[arg].values = [[]]
                port_specs[arg].translations = [None,]
        # print "ARGS:", argspec.args
        # print "ARG_DEFAULTS:", arg_defaults
        print "========================================"
        docstring = plot_obj.__doc__
        line_iter = iter(docstring.split('\n'))
        in_table = False
        for line in line_iter:
            if line.startswith("  *"):
                # print line
                port_name = line[3:line.index('*',3)]
                port_values_str = ""
                if in_table:
                    # docstring here
                    first_line = line[line.index('*',3)+1:].strip()
                    if first_line.startswith('['):
                        port_values_str = first_line[:first_line.index(']')+1]
                        port_docs = []
                    else:
                        port_docs = [first_line]
                else:
                    port_values_str = line[line.index('*',3)+2:].strip()
                    port_docs = []

                    print "%%%", port_name, ":", port_values_str
                if port_name not in port_specs:
                    port_specs[port_name] = \
                        PortSpec(port_name, "UNKNOWN", "")
                if port_values_str:
                    (port_types, option_strs) = parse_desc(port_values_str)
                    port_type_set = set(port_types)
                    print port_name, "PORT_TYPES:", port_type_set
                    if len(port_type_set) == 1:
                        port_specs[port_name].port_type = port_types[0]
                    if len(option_strs) > 0:
                        port_specs[port_name].entry_types = ['enum']
                        port_specs[port_name].values = [option_strs]
                spec = port_specs[port_name]
                line = line_iter.next()
                while line.startswith("   "):
                    port_docs.append(line.strip())
                    line = line_iter.next()
                # print "DOC:", ' '.join(port_docs)
                port_specs[port_name].docstring = ' '.join(port_docs)
            elif len(line.strip()) > 1 and line.strip().replace(" ", "=") == "=" * len(line.strip()):
                if not in_table:
                    in_table = True
                    # skip headers
                    line = line_iter.next()
                    line = line_iter.next()
                else:
                    in_table = False


        print "========================================"
        module_specs.append(ModuleSpec("Mpl%s" % plot.capitalize(), "object",
                                       plot, 
                                       port_specs.values()))
    my_specs = SpecList(module_specs)
    return my_specs
        

def parse_bases():
    from matplotlib.artist import Artist
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch

    tables = [(Line2D, "linestyle"), (Line2D, "marker")]
    for klass in [Artist, Line2D, Patch]:
        # print "========================================"
        # print "== %s ==" % klass.__name__
        # print "========================================"
        if klass.__bases__[0].__name__ != "object":
            superklass = "Mpl%s" % klass.__bases__[0].__name__
        else:
            superklass = "object"
        print "class Mpl%s(%s):" % (klass.__name__, superklass)
        print "    _input_ports = ["
        translations = {}
        for attr in sorted(klass.__dict__):
            if attr.startswith("set_"):
                attr_no_set = attr[4:]
                # print "== %s ==" % attr
                # print getattr(klass, attr).__doc__
                docstring = getattr(klass, attr).__doc__
                cleaned_docstrings = []
                if docstring.startswith("alias"):
                    continue
                line_iter = docstring.split('\n').__iter__()
                in_value_str = False
                value_lines = []
                values = None
                port_type = "String"
                for line in line_iter:
                    line = line.strip()
                    if line:
                        cleaned_docstrings.append(line)
                    if in_value_str:
                        value_lines.append(line)
                    elif line.startswith("ACCEPTS:") and line.find('[') >= 0:
                        in_value_str = True
                        value_lines.append(line)
                    elif line.startswith("ACCEPTS:"):
                        if "array" in line:
                            port_type = "List"
                        elif "color" in line:
                            port_type = "Color"
                            translations[attr_no_set] = "translate_color"
                        elif "float" in line or "number" in line:
                            port_type = "Float"
                        elif "integer" in line:
                            port_type = "Integer"
                    if in_value_str and line.find(']') >= 0:
                        values = process_accepts(value_lines)
                        value_lines = []
                        in_value_str = False
                if (klass, attr_no_set) in tables:
                    translations[attr_no_set] = \
                        get_translate_dict(klass, attr_no_set, docstring)
                    values = translations[attr_no_set].keys()
                    values.sort()
                if values:
                    if 'True' not in values:
                        values_str = ',\n "entry_types": ["enum"],\n ' + \
                            '"values": [%s]' % str(values)
                    else:
                        values_str = ""
                        port_type = "Boolean"
                else:
                    values_str = ""
                print '("%s", "(%s)",\n {"optional": True,\n ' \
                    '"docstring": "%s"%s}),' % \
                    (attr_no_set, 
                     'edu.utah.sci.vistrails.basic:%s' % port_type, 
                     '\\n'.join(cleaned_docstrings), values_str)
                # print docstring
        print "    ]"
        print "    _mpl_translations = {%s}" % \
            ', '.join("'%s': %s" % (x[0], str(x[1])) \
                          # if isinstance(x[1], dict) else (x[0], x[1] \
                          for x in translations.iteritems())

def write_specs(fname, f=sys.stdout):
    spec_list = SpecList.read_from_xml(fname)
    for spec in spec_list.module_specs:
        print >>f, "class %s(%s):" % (spec.name, spec.superklass)
        print >>f, "    _input_ports = ["
        translations = {}
        for port_spec in spec.port_specs:
            if port_spec.translations:
                for t in port_spec.translations:
                    if t is not None:
                        translations[port_spec.name] = t
            spec_str = expand_port_spec_string(port_spec.port_type,
                                               "edu.utah.sci.vistrails.basic")
            values_str = ''
            if port_spec.values:
                values_str = ',\n "entry_types": %s,\n "values": %s' % \
                    (str(port_spec.entry_types), str(port_spec.values))
            should_print_defaults = False
            defaults_str = ""
            if port_spec.defaults:
                for d in port_spec.defaults:
                    if d is not None:
                        should_print_defaults = True
                        break
            if should_print_defaults:
                defaults_str = ',\n "defaults": %s' % str(port_spec.defaults)
            print >>f, '("%s", "%s",\n {"optional": True,\n ' \
                '"docstring": "%s"%s%s}),' % (port_spec.name, spec_str,
                                              port_spec.docstring, values_str,
                                              defaults_str)
        print >>f, "    ]"
        print >>f, "    _mpl_translations = {%s}" % \
            ', '.join("'%s': %s" % (x[0], str(x[1])) \
                          # if isinstance(x[1], dict) else (x[0], x[1] \
                          for x in translations.iteritems())

def test_xml():
    port_spec = PortSpec("bins", "Integer", "Some documentation", True)
    spec = ModuleSpec("MplHistogram", "object", "hist", [port_spec])
    specs_list = SpecList([spec])
    specs_list.write_to_xml("test.xml")


def test_table():
    table1 = "  ===============   =============\n  Location String   Location Code\n  ===============   =============\n  \'best\'            0\n  \'upper right\'     1\n  \'upper left\'      2\n  \'lower left\'      3\n  \'lower right\'     4\n  \'right\'           5\n  \'center left\'     6\n  \'center right\'    7\n  \'lower center\'    8\n  \'upper center\'    9\n  \'center\'          10\n  ===============   =============\n"
    table2 = "================   ==================================================================\nKeyword            Description\n================   ==================================================================\nborderpad          the fractional whitespace inside the legend border\nlabelspacing       the vertical space between the legend entries\nhandlelength       the length of the legend handles\nhandletextpad      the pad between the legend handle and text\nborderaxespad      the pad between the axes and legend border\ncolumnspacing      the spacing between columns\n================   ==================================================================\n\n"
    line_iter = table2.split('\n').__iter__()
    line = line_iter.next().strip()
    rows, headers = parse_table(line_iter, line)
    print "ROWS:", rows
    print "HEADERS:", headers
    

def run():
    # test_xml()
    # parse_bases()
    # specs = parse_plots()
    # specs.write_to_xml("test.xml")
    # write_specs("test.xml")
    # write_specs("mpl.xml")
    test_table()

    
if __name__ == '__main__':
    run()

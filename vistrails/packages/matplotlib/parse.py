import ast
import re
import sys
from xml.etree import ElementTree as ET
import docutils.core
import docutils.nodes
from itertools import izip
import inspect
import matplotlib
matplotlib.use('Qt4Agg')
import matplotlib.docstring
def new_call(self, func):
    # print "!!!CALLING NEW CALL!!!"
    return func
# print id(matplotlib.docstring.interpd.__call__)

matplotlib.docstring.Substitution.__call__ = new_call

# def test_func():
#     """this is something cool %(Line2D)s"""
#     pass
# # matplotlib.docstring.interpd(test_func)
# print "docstring:", test_func.__doc__
# print id(matplotlib.docstring.interpd.__call__), id(new_call)


import matplotlib.pyplot
from matplotlib.artist import Artist, ArtistInspector
import matplotlib.cbook
# want to get lowercase accepts too
ArtistInspector._get_valid_values_regex = re.compile(
    r"\n\s*ACCEPTS:\s*((?:.|\n)*?)(?:$|(?:\n\n))", re.IGNORECASE)

from specs import SpecList, ModuleSpec, InputPortSpec, OutputPortSpec, \
    AlternatePortSpec

sys.path.append('/vistrails/src/git')
from vistrails.core.modules.utils import expand_port_spec_string

##############################################################################
# docutils parsing code
##############################################################################

def parse_docutils_thead(elt):
    header = []
    for child in elt.children:
        if child.__class__ == docutils.nodes.row:
            if len(header) > 0:
                raise Exception("More than one row in header")
            for subchild in child.children:
                if subchild.__class__ == docutils.nodes.entry:
                    header.append(parse_docutils_elt(subchild)[0].strip())
    return header

def parse_docutils_tbody(elt):
    rows = []
    for child in elt.children:
        if child.__class__ == docutils.nodes.row:
            row = []
            for subchild in child.children:
                if subchild.__class__ == docutils.nodes.entry:
                    row.append(parse_docutils_elt(subchild)[0].strip())
            rows.append(row)
    return rows

def parse_docutils_table(elt):
    header = []
    rows = []
    for child in elt.children:
        if child.__class__ == docutils.nodes.tgroup:
            for subchild in child.children:
                if subchild.__class__ == docutils.nodes.thead:
                    header = parse_docutils_thead(subchild)
                elif subchild.__class__ == docutils.nodes.tbody:
                    rows = parse_docutils_tbody(subchild)
    print "== TABLE =="
    print "HEADER:", header
    print "ROWS:", '\n'.join(str(r) for r in rows)
    return (header, rows)

def parse_docutils_term(elt):
    # term = ""
    terms = []
    accepts = ""
    for child in elt.children:
        if child.__class__ == docutils.nodes.emphasis:
            term = parse_docutils_elt(child)[0].strip()
            if term in ('True', 'False'):
                accepts += term
            elif term != "None":
                terms.append(term)
        elif child.__class__ == docutils.nodes.Text:
            accepts += str(child)
        else:
            accepts += parse_docutils_elt(child)[0]
    accepts = accepts.strip()
    if accepts.startswith(':'):
        accepts = accepts[1:].strip()
    return terms, accepts

def parse_docutils_deflist(elt):
    print "GOT DEFLIST!"
    args = []
    term = None
    definition = None
    for child in elt.children:
        if child.__class__ != docutils.nodes.definition_list_item:
            raise Exception("NO DEF LIST ITEM!")
        else:
            for subchild in child.children:
                if subchild.__class__ == docutils.nodes.term:
                    terms, accepts = parse_docutils_term(subchild)
                    print "TERMS:", terms
                    if accepts:
                        print "ACCEPTS:", accepts
                elif subchild.__class__ == docutils.nodes.definition:
                    definition = parse_docutils_elt(subchild)[0].rstrip()
                    print "DEFINITION:", definition
                    for term in terms:
                        args.append((term, accepts, definition))
    return args

def parse_docutils_elt(elt, last_text=""):
    def get_last_block(cur_text):
        num_newlines = 1
        end_idx = len(cur_text)
        while cur_text.endswith("\n\n" * num_newlines):
            num_newlines += 1
            end_idx -= 2
        idx = cur_text.rfind("\n\n",0,end_idx)
        if idx < 0:
            idx = 0
        else:
            idx += 2
        return cur_text[idx:].strip()

    text = ""
    args = []
    tables = []
    call_signatures = []
    for child in elt.children:
        if child.__class__ == docutils.nodes.Text:
            # cur_block.extend(s.strip() for s in str(child).split('\n'))
            ntext = ' '.join(s for s in str(child).split('\n'))
            text += ntext
        elif child.__class__ == docutils.nodes.system_message:
            pass
        elif child.__class__ == docutils.nodes.definition_list:
            # print "DEFLIST BLOCK:", text[-20:]
            # print get_last_block(last_text + text)
            args.append((get_last_block(last_text + text), 
                         parse_docutils_deflist(child)))
        elif child.__class__ == docutils.nodes.table:
            # print "TABLE BLOCK:", text[-20:]
            # print get_last_block(last_text + text)
            tables.append((get_last_block(last_text + text),) + \
                              parse_docutils_table(child))
        elif isinstance(child, docutils.nodes.Inline):
            (ntext, nargs, ntables, ncall_sigs) = \
                parse_docutils_elt(child, last_text + text)
            text += ntext
            args += nargs
            tables += ntables
            call_signatures += ncall_sigs
        else:
            (ntext, nargs, ntables, ncall_sigs) = \
                parse_docutils_elt(child, last_text + text)
            if child.__class__ == docutils.nodes.literal_block:
                check_str = (last_text + text).lower().strip()
                if check_str.endswith("\ncall signature:") or \
                        check_str.endswith("\ncall signatures:"):
                    call_signatures.append(ntext)
            text += ntext.strip() + "\n\n"
            args += nargs
            tables += ntables
            call_signatures += ncall_sigs
    return (text.rstrip(), args, tables, call_signatures)
            
def parse_docutils_str(docstring, should_print=False):
    root = docutils.core.publish_doctree(docstring)
    if should_print:
        print root
    # for child in root.children:
    #     print "CHILD:", child.__class__, child
    #     for subchild in child.children:
    #         print "SUBCHILD:", subchild.__class__, subchild
    return parse_docutils_elt(root)
    
##############################################################################
# util methods
##############################################################################

def capfirst(s):
    return s[0].upper() + s[1:]

def pretty_name(s):
    cap = True
    new_s = ""
    for i, c in enumerate(s):
        if cap:
            c = c.upper()
            cap = False
        if c != '_' or i == 0:
            new_s += c
        else:
            cap = True
    return new_s

def get_value_and_type(s):
    try:
        val = eval(s)
        if isinstance(val, type):
            return (None, None)
    except:
        val = s
    port_type = get_type_from_val(val)
    return (val, port_type)

def get_type_from_val(val):
    if type(val) == float:
        return "basic:Float"
    elif type(val) == int:
        return "basic:Integer"
    elif isinstance(val, basestring):
        return "basic:String"
    elif type(val) == bool:
        return "basic:Boolean"
    elif type(val) == list:
        return "basic:List"
    return None        

def resolve_port_type(port_types, port_spec):
    port_types_set = set(p for p in port_types if p is not None)
    was_set = False
    if port_spec.port_type is not None:
        port_types_set.add(port_spec.port_type)
    if len(port_types_set) == 1:
        port_spec.port_type = next(iter(port_types_set))
        was_set = True
    elif len(port_types_set) == 2:
        if 'basic:Float' in port_types_set and \
                'basic:Integer' in port_types_set:
            port_spec.port_type = 'basic:Float'
            was_set = True
        elif 'basic:List' in port_types_set:
            port_spec.port_type = 'basic:List'
            base_name = port_spec.name
            port_spec.name = base_name + "Sequence"
            port_types_set.discard('basic:List')
            alternate_spec = \
                AlternatePortSpec(name=base_name + "Scalar",
                                  port_type=next(iter(port_types_set)))
            port_spec.alternate_specs.append(alternate_spec)
            was_set = True
    if not was_set:
        if "color" in port_spec.name:
            port_spec.port_type = "basic:Color"
            port_spec.translations = "translate_color"
        elif port_spec.name == "x":
            port_spec.port_type = "basic:List"
        elif port_spec.name == "y":
            port_spec.port_type = "basic:List"
        else:
            port_spec.port_type = None

    # # FIXME
    # # what to do with scalar/sequence-type args
    # elif len(port_types_set) == 2 and 'basic:List' in port_types_set:
    #     port_type = 'basic:List'
    # else:
    #     port_type = None
    # return port_type

def parse_description(desc):
    key_to_type = {'string': 'basic:String',
                   'integer': 'basic:Integer',
                   'sequence': 'basic:List',
                   'float': 'basic:Float',
                   'boolean': 'basic:Boolean',
                   'scalar': 'basic:Float',
                   'vector': 'basic:List',
                   'list': 'basic:List'}
    port_types = []
    option_strs = []
    default_val = None
    allows_none = False
    default_paren_re = re.compile(r"((\S*)\s+)?\(default:?(\s+(\S*))?\)", 
                                  re.IGNORECASE)
    default_is_re = re.compile(r"default\s+is\s+(\S*)", re.IGNORECASE)

    if '|' in desc:
        m = re.search("\[([\s\S]*?)\]", desc)
        if m:
            opt_str = m.group(1)
        else:
            opt_str = desc
        opts = opt_str.split('|')
        for opt in opts:
            opt = opt.strip()
            m = default_paren_re.search(opt)
            if m:
                (_, before_res, _, after_res) = m.groups()
                if after_res:
                    if default_val is not None:
                        raise Exception('Multiple defaults: "%s" "%s"' % \
                                            (default_val, after_res))
                    default_val = after_res
                    opt = after_res
                elif before_res:
                    if default_val is not None:
                        raise Exception('Multiple defaults: "%s" "%s"' % \
                                            (default_val, after_res))
                    default_val = before_res
                    opt = before_res
            found_type = False
            opt_lower = opt.lower()
            if opt_lower == "none":
                found_type = True
                allows_none = True
            elif opt_lower == "true" or opt_lower == "false":
                found_type = True
                port_types.append("basic:Boolean")
            else:
                for key in key_to_type:
                    if key in opt_lower:
                        found_type = True
                        port_types.append(key_to_type[key])

            if not found_type:
                (val, port_type) = get_value_and_type(opt)
                option_strs.append(val)
                if port_type is not None:
                    port_types.append(port_type)
                    found_type = True
                # option_strs.append(opt)
                # if opt.startswith("'") or opt.startswith('"'):
                #     port_types.append("basic:String")
                #     found_type = True
                    
    if default_val is None:
        m = default_paren_re.search(desc)
        if m:
            (_, before_res, _, after_res) = m.groups()
            if after_res:
                default_val = after_res
            elif before_res:
                default_val = before_res
        else:
            m = default_is_re.search(desc)
            if m:
                (default_val,) = m.groups()
                if default_val.endswith('.') or default_val.endswith(','):
                    default_val = default_val[:-1]

    if default_val:
        (default_val, port_type) = get_value_and_type(default_val)
        if port_type is not None:
            port_types.append(port_type)

    should_print = False
    if len(port_types) == 0:
        for key, port_type in key_to_type.iteritems():
            if key in desc:
                port_types.append(port_type)

    # port_type = resolve_port_type(port_types)
        
    return (port_types, option_strs, default_val, allows_none)

def parse_translation(rows, should_reverse=True):
    t = {}
    port_types = []
    values = []
    for row in rows:
        (val1, port_type1) = get_value_and_type(row[0])
        (val2, port_type2) = get_value_and_type(row[1])
        if should_reverse:
            if val2 != None:
                port_types.append(port_type2)
                values.append(val2)
                t[val2] = val1
        else:
            if val1 != None:
                port_types.append(port_type1)
                values.append(val1)
                t[val1] = val2

    # port_type = resolve_port_type(port_types)
    return (t, port_types, values)

def do_translation_override(port_specs, names, rows, opts):
    if 'name' in opts:
        names = opts['name']
    if names is None:
        raise Exception("Must specify name of port to use translation for")
    if isinstance(names, basestring) or not matplotlib.cbook.iterable(names):
        names = [names]
    should_reverse = opts.get('reverse', True)
    values_only = opts.get('values_only', False)
    (t, port_type, values) = \
        parse_translation(rows, should_reverse)
    for name in names:
        print "TRANSLATING", name
        if name not in port_specs:
            port_specs[name] = InputPortSpec(name) 
        port_specs[name].entry_types = ['enum']
        port_specs[name].values = [values]
        if not values_only:
            port_specs[name].translations = t

def get_names(obj, default_module_base, default_super_base, 
              prefix="Mpl", suffix=""):
    module_name = None
    super_name = None
    if type(obj) == tuple:
        if len(obj) > 2:
            super_name = obj[2]
        if len(obj) < 2:
            raise Exception("Need to specify 2- or 3-tuple")
        (obj, module_name) = obj[:2]
    if module_name is None:
        module_name = "%s%s%s" % (prefix, 
                                  pretty_name(default_module_base(obj)), 
                                  suffix)
    if super_name is None:
        super_name = "%s%s%s" % (prefix, 
                                 pretty_name(default_super_base(obj)), 
                                 suffix)

    return (obj, module_name, super_name)

##############################################################################
# main methods
##############################################################################

def parse_argspec(obj_or_str):
    if isinstance(obj_or_str, basestring):
        obj_or_str = obj_or_str.strip()
        if not obj_or_str.endswith(":"):
            obj_or_str += ":"
        if not obj_or_str.startswith("def "):
            obj_or_str = "def " + obj_or_str
        try:
            tree = ast.parse(obj_or_str + "\n  pass")
        except SyntaxError:
            # cannot parse the argspec
            print "*** CANNOT PARSE", obj_or_str
            return []
        argspec_name = tree.body[0].name
        argspec_args = [a.id for a in tree.body[0].args.args]
        print tree.body[0].args.defaults
        argspec_defaults = []
        for i, d in enumerate(tree.body[0].args.defaults):
            try:
                d_val = ast.literal_eval(d)
            except ValueError:
                d_val = None
            argspec_defaults.append(d_val)
        # argspec_defaults = \
        #     [ast.literal_eval(d) for d in tree.body[0].args.defaults]
    else:
        argspec = inspect.getargspec(obj_or_str)
        argspec_args = argspec.args
        argspec_defaults = argspec.defaults

    # print argspec
    if not argspec_defaults:
        start_defaults = len(argspec_args) + 1
    else:
        start_defaults = len(argspec_args) - len(argspec_defaults)
    port_specs_list = []
    has_self = False
    for i, arg in enumerate(argspec_args):
        if i == 0 and arg == "self":
            has_self = True
            continue
        port_spec = InputPortSpec(arg)
        port_spec.arg_pos = (i-1) if has_self else i
        if i >= start_defaults:
            port_spec.required = False
            default_val = argspec_defaults[i-start_defaults]
            if default_val is not None:
                port_spec.defaults = [str(default_val)]
                port_type = get_type_from_val(default_val)
                if port_type is not None:
                    port_spec.port_type = port_type
        else:
            port_spec.required = True
            # port_specs[arg].entry_types = [None,]
            # port_specs[arg].values = [[]]
            # port_specs[arg].translations = [None,]
        port_specs_list.append(port_spec)
    return port_specs_list

def process_docstring(docstring, port_specs, parent, table_overrides):
    (cleaned_docstring, args, tables, call_sigs) = \
        parse_docutils_str(docstring)

    if len(call_sigs) > 0:
        for call_sig in call_sigs:
            port_specs_list = parse_argspec(call_sig)
            for port_spec in port_specs_list:
                if port_spec.arg in port_specs:
                    # have to reconcile the two
                    old_port_spec = port_specs[port_spec.arg]
                    resolve_port_type([port_spec.port_type], old_port_spec)
                    if old_port_spec.defaults is None:
                        old_port_spec.defaults = port_spec.defaults
                    elif old_port_spec.defaults != port_spec.defaults:
                        # keep it as the old spec is
                        print "*** Different defaults!" + \
                            str(old_port_spec.defaults) + \
                            " : " + str(port_spec.defaults)
                        # raise Exception("Different defaults!" + \
                        #                     str(old_port_spec.defaults) + \
                        #                     " : " + str(port_spec.defaults))
                else:
                    port_specs[port_spec.arg] = port_spec

    output_port_specs = []
    for (deflist_intro, deflist) in args:
        print "PROCESSING DEFLIST", deflist_intro
        if re.search("return value", deflist_intro, re.IGNORECASE):
            print "  -> RETURN VALUE"
            for (name, accepts, port_doc) in deflist:
                (port_types, option_strs, default_val, allows_none) = \
                    parse_description(accepts)
                (pt2, _, dv2, _) = parse_description(port_doc)
                port_types.extend(pt2)
                if default_val is None:
                    default_val = dv2
                oport = OutputPortSpec(name, docstring=port_doc)
                resolve_port_type(port_types, oport)
                output_port_specs.append(oport)
        elif (re.search("argument", deflist_intro, re.IGNORECASE) or
              re.search("kwarg", deflist_intro, re.IGNORECASE)):
            print "  -> ARGUMENTS"
            for (name, accepts, port_doc) in deflist:
                if name not in port_specs:
                    port_specs[name] = InputPortSpec(name, docstring=port_doc)
                else:
                    port_specs[name].docstring = port_doc
                (port_types, option_strs, default_val, allows_none) = \
                    parse_description(accepts)
                (pt2, _, dv2, _) = parse_description(port_doc)
                port_types.extend(pt2)
                if default_val is None:
                    default_val = dv2
                resolve_port_type(port_types, port_specs[name])
                if len(option_strs) > 0:
                    port_specs[name].entry_types = ['enum']
                    port_specs[name].values = [option_strs]
                if default_val is not None:
                    port_specs[name].defaults = [str(default_val)]

    for (table_intro, header, rows) in tables:
        print "GOT TABLE", table_intro, rows[0]
        table_key = parent + (table_intro,)
        if table_key in table_overrides:
            (override_type, opts) = table_overrides[table_key]
            if override_type == "translation":
                do_translation_override(port_specs, None, rows, opts)
                continue
            elif override_type == "ports":
                table_intro = "kwarg"
            elif override_type == "skip":
                continue

        if re.search("return value", table_intro, re.IGNORECASE):
            print "  -> RETURN"
            if len(rows[0]) != 2:
                raise Exception("row that has more/less than 2 columns!")
            for (name, port_doc) in rows:
                (port_types, option_strs, default_val, allows_none) = \
                    parse_description(port_doc)
                # (port_types, option_strs) = parse_desc(port_doc)
                # port_type_set = set(port_types)
                # # print port_name, "PORT_TYPES:", port_type_set
                # port_type = "UNKNOWN"
                # if len(port_type_set) == 1:
                #     port_type = port_types[0]
                oport = OutputPortSpec(name, docstring=port_doc)
                resolve_port_type(oport, port_types)
                output_port_specs.append(oport)
        elif (re.search("argument", table_intro, re.IGNORECASE) or
              re.search("kwarg", table_intro, re.IGNORECASE)):
            print "  -> ARGUMENT"
            if len(rows[0]) != 2:
                raise Exception("row that has more/less than 2 columns!")
            for (name, port_doc) in rows:
                if name not in port_specs:
                    port_specs[name] = InputPortSpec(name, docstring=port_doc)
                else:
                    port_specs[name].docstring = port_doc
                (port_types, option_strs, default_val, allows_none) = \
                    parse_description(port_doc)
                # (port_types, option_strs) = parse_desc(port_doc)
                # port_type_set = set(port_types)
                # # print port_name, "PORT_TYPES:", port_type_set
                # port_type = "UNKNOWN"
                # if len(port_type_set) == 1:
                #     port_specs[name].port_type = port_types[0]
                resolve_port_type(port_types, port_specs[name])
                if len(option_strs) > 0:
                    port_specs[name].entry_types = ['enum']
                    port_specs[name].values = [option_strs]
                if default_val is not None:
                    port_specs[name].defaults = [str(default_val)]
        else:
            raise Exception("Unknown table: %s\n  %s %s" % \
                                (parent, table_intro, str(header)))
            # print "HIT SPEC:", name
            # if name not in port_specs:
            #     port_specs[name] = PortSpec(name, name, "UNKNOWN", "")
            # port_specs[name].translations = dict(reversed(r) for r in rows)
    return cleaned_docstring, output_port_specs

def parse_plots(plot_types, table_overrides):
    def get_module_base(n):
        return n
    def get_super_base(n):
        return "plot"

    module_specs = []
    for plot in plot_types:
        port_specs = {}
        print "========================================"
        print plot
        print "========================================"
        
        (plot, module_name, super_name) = \
            get_names(plot, get_module_base, get_super_base, "Mpl", "")

        try:
            plot_obj = getattr(matplotlib.pyplot, plot)
        except AttributeError:
            print '*** CANNOT ADD PLOT "%s";' \
                'IT DOES NOT EXIST IN THIS MPL VERSION ***' % plot
            continue
        # argspec = inspect.getargspec(plot_obj)
        # print argspec
        # if argspec.defaults is None:
        #     start_defaults = len(argspec.args) + 1
        # else:
        #     start_defaults = len(argspec.args) - len(argspec.defaults)
        # for i, arg in enumerate(argspec.args):
        #     port_specs[arg] = PortSpec(arg, arg)
        #     if i >= start_defaults:
        #         port_specs[arg].required = False
        #         default_val = argspec.defaults[i-start_defaults]
        #         if default_val is not None:
        #             port_specs[arg].defaults = [str(default_val)]
        #             port_type = get_type_from_val(default_val)
        #             if port_type is not None:
        #                 port_specs[arg].port_type = port_type
        #     else:
        #         port_specs[arg].required = True
        #         # port_specs[arg].entry_types = [None,]
        #         # port_specs[arg].values = [[]]
        #         # port_specs[arg].translations = [None,]
        
        port_specs_list = parse_argspec(plot_obj)
        for port_spec in port_specs_list:
            port_specs[port_spec.arg] = port_spec

        docstring = plot_obj.__doc__
        if plot == 'contour':
            # want to change the double newline to single newline...
            print "&*&* FINDING:", \
                docstring.find("*extent*: [ *None* | (x0,x1,y0,y1) ]\n\n")
            docstring = docstring.replace("*extent*: [ *None* | (x0,x1,y0,y1) ]\n\n", 
                              "*extent*: [ *None* | (x0,x1,y0,y1) ]\n")
        if plot == 'annotate':
            docstring = docstring % dict((k,v) for k, v in matplotlib.docstring.interpd.params.iteritems() if k == 'Annotation')
        elif plot == 'barbs':
            docstring = docstring % dict((k,v) for k,v in matplotlib.docstring.interpd.params.iteritems() if k == 'barbs_doc')

        cleaned_docstring, output_port_specs = \
            process_docstring(docstring, port_specs, ('pyplot', plot),
                              table_overrides)

        module_specs.append(ModuleSpec(module_name, super_name,
                                       "matplotlib.pyplot.%s" % plot, 
                                       cleaned_docstring, port_specs.values(),
                                       output_port_specs))
    my_specs = SpecList(module_specs)
    return my_specs
        
_get_accepts_regex = re.compile(
    r"([\s\S]*)\n\s*ACCEPTS:\s*((?:.|\n)*?)(?:$|(?:\n\n))([\s\S]*)",
    re.IGNORECASE)

def parse_artists(artist_types, table_overrides={}):
    def get_module_name(obj):
        return obj.__name__
    def get_super_name(obj):
        for base in obj.__bases__:
            if issubclass(base, Artist):
                return base.__name__
        return ""
        # if obj.__bases__[0].__name__ != 'object':
        #     return obj.__bases__[0].__name__
        # else:
        #     return ""

    module_specs = []
    for klass in artist_types:
        (klass, module_name, super_name) = \
            get_names(klass, get_module_name, get_super_name, "Mpl", 
                      "Properties")

        port_specs = {}
        insp = ArtistInspector(klass)
        klass_name = klass.__name__
        klass_qualname = klass.__module__ + "." + klass_name
        for (s, t) in insp._get_setters_and_targets():
            print "** %s **" % s
            if t.rsplit('.',1)[0] != klass_qualname:
                # let inheritance work
                continue

            if s in port_specs:
                raise Exception('duplicate port "%s"' % s)
            port_spec = InputPortSpec(s)
            port_specs[s] = port_spec

            accepts_raw = insp.get_valid_values(s)
            (accepts, deflists, tables, call_sigs) = \
                parse_docutils_str(accepts_raw)
            if len(deflists) + len(tables) > 0:
                raise Exception("accepts has deflists and/or tables")
            (port_types, option_strs, default_val, allows_none) = \
                parse_description(accepts)
            # port_spec.port_type = port_type
            if default_val is not None:
                port_spec.default_val = default_val
            if len(option_strs) > 0:
                port_spec.entry_types = ['enum']
                port_spec.values = [option_strs]
            port_spec.hide = False

            docstring = getattr(insp.o, 'set_' + s).__doc__
            if docstring is None:
                docstring = ""
            else:
                docstring = docstring % matplotlib.docstring.interpd.params
            match = _get_accepts_regex.search(docstring)
            if match is not None:
                print "STARTING DOCSTRING:", docstring
                groups = match.groups()
                if len(groups) > 2 and groups[2]:
                    # raise Exception("GOT LAST" + str(docstring) + str(groups))
                    docstring = groups[0] + groups[2]
                else:
                    docstring = groups[0]
                print "FIXED DOCSTRING:", docstring
            
            (cleaned_docstring, args, tables, call_sigs) = \
                parse_docutils_str(docstring)
            port_spec.docstring = cleaned_docstring

            translations = None
            for (table_intro, header, rows) in tables:
                print "TABLE:", table_intro
                if (klass.__name__, s, table_intro) in table_overrides:
                    (override_type, opts) = \
                        table_overrides[(klass.__name__, s, table_intro)]
                    if override_type == "translation":
                        do_translation_override(port_specs, s, rows, opts)
                        continue
                    elif override_type == "ports":
                        table_intro = "kwarg"
                    elif override_type == "skip":
                        continue
                if len(header) != 2:
                    raise Exception("Table not two columns!")
                if translations is not None:
                    raise Exception("Two translations in one attr")
                (translations, pt2, values) = parse_translation(rows)
                port_spec.translations = translations
                port_spec.values = [values]
                port_types.extend(pt2)  
            resolve_port_type(port_types, port_spec)

        constructor_port_specs = {}
        port_specs_list = parse_argspec(klass.__init__)
        for port_spec in port_specs_list:
            constructor_port_specs[port_spec.arg] = port_spec
        constructor_docstring = klass.__init__.__doc__
        if constructor_docstring is not None:
            _, output_port_specs = process_docstring(constructor_docstring, 
                                                     constructor_port_specs,
                                                     (klass.__name__, 
                                                      '__init__'),
                                                     table_overrides)
        for arg, ps in constructor_port_specs.iteritems():
            if arg not in port_specs:
                ps.constructor_arg = True
                ps.required = False
                port_specs[arg] = ps            

        module_spec = ModuleSpec(module_name, super_name, klass_qualname,
                                 klass.__doc__, port_specs.values())
        module_specs.append(module_spec)

    my_specs = SpecList(module_specs)
    return my_specs

def run_artists():
    import matplotlib.axes
    import matplotlib.axis
    import matplotlib.collections
    import matplotlib.figure
    import matplotlib.image
    import matplotlib.lines
    import matplotlib.patches
    import matplotlib.text
    
    artist_py_modules = [matplotlib.axes,
                         matplotlib.axis,
                         matplotlib.collections,
                         matplotlib.figure,
                         matplotlib.image,
                         matplotlib.lines,
                         matplotlib.patches,
                         matplotlib.text,
                         ]

    exclude = set([])

    artist_types = set() # (Artist, None, "MplProperties")]
    for py_module in artist_py_modules:
        for cls_name, cls in inspect.getmembers(py_module, inspect.isclass):
            if cls_name in exclude:
                continue
            if issubclass(cls, Artist) and cls != Artist:
                artist_types.add(cls)

    print "ARTIST TYPES:", artist_types
    artist_types = [(Artist, None, "MplProperties")] + \
        list(sorted(artist_types, key=lambda x: list(reversed(x.mro()))))
    print "SORTED ARTIST TYPES:", artist_types

    # from matplotlib.collections import Collection, PathCollection, \
    #     LineCollection
    # from matplotlib.lines import Line2D
    # from matplotlib.patches import Patch, Rectangle, PathPatch, Wedge, \
    #     FancyArrowPatch, YAArrow
    # from matplotlib.text import Text, Annotation
    # from matplotlib.axes import Axes
    # from matplotlib.figure import Figure

    # artist_types = [(Artist, None, "MplProperties"), 
    #                 Line2D, Patch, Rectangle, Axes, Figure, PathPatch, Wedge, 
    #                 Collection, PathCollection, LineCollection, Text, 
    #                 Annotation, FancyArrowPatch, YAArrow]

    # FIXME want this to be indexed by artist name, too...
    artist_overrides = {('Axes', 'aspect', 'aspect'):
                            ('translation', {'reverse': False,
                                             'values_only': True}),
                        # FIXME may want documentation from adjustable?
                        ('Axes', 'aspect', 'adjustable'):
                            ('skip', {}),
                        # FIXME may want documentation from anchor?
                        ('Axes', 'aspect', 'anchor'):
                            ('skip', {}),
                        ('ConnectionPatch', '__init__', "Valid keys are"):
                            ('ports', {}),
                        ('ConnectionPatch', '__init__', "coordsA and coordsB are strings that indicate the coordinates of xyA and xyB."):
                            ('translation', {'name': ['coordsA', 'coordsB'],
                                             'reverse': False,
                                             'values_only': True}),
                        ('Annotation', '__init__', "If the dictionary has a key arrowstyle, a FancyArrowPatch instance is created with the given dictionary and is drawn. Otherwise, a YAArow patch instance is created and drawn. Valid keys for YAArow are"):
                            ('skip', {}),
                        ('Annotation', '__init__', "Valid keys for FancyArrowPatch are"):
                            ('skip', {}),
                        ('Annotation', '__init__', "xycoords and textcoords are strings that indicate the coordinates of xy and xytext."):
                            ('translation', {'name': ['xycoords', 'textcoords'],
                                             'reverse': False,
                                             'values_only': True}),
                        }

    # test_xml()
    specs = parse_artists(artist_types, artist_overrides)
    specs.write_to_xml("mpl_artists_raw.xml")


def run_plots():
    # from matplotlib's boilerplate.py
    plot_types = ['acorr',
                  'arrow',
                  'axhline',
                  'axhspan',
                  'axvline',
                  'axvspan',
                  'bar',
                  'barh',
                  'broken_barh',
                  'boxplot',
                  'cohere',
                  'clabel',
                  'contour',
                  'contourf',
                  'csd',
                  'errorbar',
                  'fill',
                  'fill_between',
                  'fill_betweenx',
                  'hexbin',
                  'hist',
                  'hist2d',
                  'hlines',
                  'imshow',
                  'loglog',
                  'pcolor',
                  'pcolormesh',
                  'pie',
                  # add plot later
                  # 'plot',
                  'plot_date',
                  'psd',
                  'quiver',
                  'quiverkey',
                  'scatter',
                  'semilogx',
                  'semilogy',
                  'specgram',
                  'stackplot',
                  'stem',
                  'step',
                  'streamplot',
                  'tricontour',
                  'tricontourf',
                  'tripcolor',
                  'triplot',
                  'vlines',
                  'xcorr',
                  'barbs',
                  ]

    plot_types += ['spy',
                   'polar',
                   ]

    # FIXME added to keep existing code happy for now
    plot_types += ['legend',
                   'annotate',
                   ('plot', 'MplLinePlot')]

    # others = ['plotfile', 'legend', 'matshow',]

    # plot_types = ['acorr', 'bar', 'barbs', 'barh', 'boxplot', 'broken_barh', 'cohere', 'contour', 'contourf', 'csd', 'errorbar', 'hexbin', 'hist', 'loglog', 'pcolor', 'pcolormesh', 'pie', 'plot', 'plot_date', 'pie', 'polar', 'psd', 'quiver', 'scatter', 'semilogx', 'semilogy', 'specgram', 'spy', 'stem', 'tricontour', 'tricontourf', 'tripcolor', 'triplot', 'xcorr']

    # plot_types = ['bar', 'boxplot', 'contour', 'hist', ('plot', "MplLinePlot"), 
    #               'scatter', 'pie', 'legend', 'annotate', 'hlines', 
    #               'axvline', 'axhline', 'errorbar']

    table_overrides = {('pyplot', 'plot', 'The following format string characters are accepted to control the line style or marker:'):
                           ('translation', {'name': 'marker'}),
                       ('pyplot', 'plot', 'The following color abbreviations are supported:'):
                           ('skip', {}),
                       ('pyplot', 'legend', 'The location codes are'):
                           ('translation', {'name': 'loc',
                                            'reverse': False}),
                       ('pyplot', 'legend', 'Padding and spacing between various elements use following keywords parameters. These values are measure in font-size units. E.g., a fontsize of 10 points and a handlelength=5 implies a handlelength of 50 points.  Values from rcParams will be used if None.'):
                           ('ports', {}),
                       ('pyplot', 'annotate', "If the dictionary has a key arrowstyle, a FancyArrowPatch instance is created with the given dictionary and is drawn. Otherwise, a YAArow patch instance is created and drawn. Valid keys for YAArow are"):
                           ('skip', {}),
                       ('pyplot', 'annotate', "Valid keys for FancyArrowPatch are"):
                           ('skip', {}),
                       ('pyplot', 'annotate', "xycoords and textcoords are strings that indicate the coordinates of xy and xytext."):
                           ('translation', {'name': ['xycoords', 'textcoords'],
                                            'reverse': False,
                                            'values_only': True}),
                       }



    specs = parse_plots(plot_types, table_overrides)
    specs.write_to_xml("mpl_plots_raw.xml")
    

def run(which="all"):
    if which == "all" or which == "artists":
        run_artists()
    if which == "all" or which == "plots":
        run_plots()

    # write_specs("test.xml")
    # write_specs("mpl.xml")
    # test_table()

def get_docutils(plot):
    import matplotlib.pyplot
    plot_obj = getattr(matplotlib.pyplot, plot)
    (_, _, _, call_sigs) = parse_docutils_str(plot_obj.__doc__, True)
    print call_sigs
    
if __name__ == '__main__':
    if len(sys.argv) <= 1:
        run()
    elif len(sys.argv) == 2:
        run(sys.argv[1])
    else:
        raise TypeError("usage: python parse.py [all|artists|plots]")
    # get_docutils("axhline")

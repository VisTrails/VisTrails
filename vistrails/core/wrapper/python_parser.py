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
"""
methods for parsing a function signature and generating a partial
module specification
"""

import ast
from ast import literal_eval
import inspect
import re
import pydoc
import importlib

from types import BuiltinFunctionType

from specs import ClassSpec, FunctionSpec


def get_value_and_type(s):
    if '`' in s:
        # unknown type
        return (None, None)
    try:
        val = eval(s)
        if isinstance(val, type) or isinstance(val, BuiltinFunctionType):
            return (None, None)
    except Exception:
        val = s
    port_type = get_type_from_val(val)
    return (val, port_type)


def get_type_from_val(val):
    """ Parse basic types
    """
    if isinstance(val, float):
        return "basic:Float"
    elif isinstance(val, bool):
        return "basic:Boolean"
    elif isinstance(val, (int, long)):
        return "basic:Integer"
    elif isinstance(val, basestring):
        return "basic:String"
    elif isinstance(val, list) or isinstance(val, tuple):
        return "basic:List"
    return None


# list of common type strings in order of relevance
default_key_to_type = [['array_like', 'basic:List'],
                       ['ndarray', 'basic:List'],
                       ['array', 'basic:List'],
                       ['sequence', 'basic:List'],
                       ['object', 'basic:List'],
                       ['vector', 'basic:List'],
                       ['list', 'basic:List'],
                       ['tuple', 'basic:List'],
                       ['float', 'basic:Float'],
                       ['scalar', 'basic:Float'],
                       ['double', 'basic:Float'],
                       ['integer', 'basic:Integer'],
                       ['boolean', 'basic:Boolean'],
                       ['bool', 'basic:Boolean'],
                       ['dict', 'basic:Dictionary'],
                       ['string', 'basic:String'],
                       ['int', 'basic:Integer'],
                       ['str', 'basic:String']]


# List types used to convert from List to depth-1 types
default_list_types = [['int', 'basic:Integer'],
                      ['float', 'basic:Float'],
                      ['bool', 'basic:Boolean'],
                      ['str', 'basic:String']]


# Name for alternate ports (what to do with multiple scalars?)
default_alt_suffixes = {'basic:Integer': 'Scalar',
                        'basic:Float': 'Scalar',
                        'basic:String': 'Scalar',
                        'basic:Boolean': 'Bool',
                        'basic:List': 'Sequence'}


def clean_sections(signature, _arguments, _attributes, _methods, _returns):

    def clean(_descs):
        """
        * Fixes multi-arg descriptions
        * Discards invalid args
        * Joins docstrings
        """
        descs = []
        arg_list = []
        for args, typestring, fdocstring in _descs:
            # args can specify multiple descs
            for arg in args.split(','):
                arg = arg.strip()
                if arg.startswith('(') or ' ' in arg or '*' in arg:
                    # Ignore comments argv, and kwarg
                    continue
                if isinstance(fdocstring, list):
                    fdocstring = '\n'.join(fdocstring)
                # avoid duplicates
                if arg not in arg_list:
                    descs.append((arg, typestring, fdocstring))
                    arg_list.append(arg)
        return descs

    arguments = clean(_arguments)
    attributes = clean(_attributes)
    methods = clean(_methods)
    returns = clean(_returns)

    return signature, arguments, attributes, methods, returns


def parse_numpydoc(f):
    """ Parse parameters and attributes from numpy docstring

    """
    docstring = pydoc.getdoc(f)
    from numpydoc.docscrape import NumpyDocString
    root = NumpyDocString(docstring)
    # list of (arg, typestring, docstring)
    signature = root['Signature']
    if not signature and root['Summary']:
        signature = root['Summary'][:1][0]
    if signature:
        m = re.search(r"\w+\((.*?)\)", signature, re.IGNORECASE)
        if m:
            signature = m.group(0)
        else:
            signature = ''

    parameters = root['Parameters'] + root['Other Parameters']
    attributes = root['Attributes']
    methods = root['Methods']
    returns = root['Returns']
    if not returns:
        # try to extract return value from first line of summary
        summary = root['Summary'][:1]
        if summary:
            m = re.search(r"\w+\((.*?)\) \-\> (\w+)", summary[0], re.IGNORECASE)
            if m:
                returns.append((m.group(2), '', ''))

    return signature, parameters, attributes, methods, returns


def parse_googledoc(f):
    """ Parse parameters and attributes from numpy docstring

    """
    docstring = pydoc.getdoc(f)
    # signature is not parsed by googledoc
    signature = docstring.split('\n')[0]
    if signature:
        m = re.search(r"\w+\((.*?)\)", signature, re.IGNORECASE)
        if m:
            signature = m.group(0)
        else:
            signature = ''
    from googledocstring import GoogleDocstring
    g = GoogleDocstring(docstring)

    if not g.returns:
        returns = []
        # try to extract return value from first line of docstring
        summary = docstring.split('\n')[0]
        if summary:
            m = re.search(r"\w+\((.*?)\) \-\> (\w+)", summary[0], re.IGNORECASE)
            if m:
                returns.append((m.group(2), '', ''))
        g.returns = returns

    return signature, g.arguments, g.attributes, g.methods, g.returns


def parse_type_string(desc, conf):
    """ parse_type_string(desc: string) ->
            {(port_type, depth): (option_strs, default_val)}

        Parses an argument description string.

        port_type: vistrail type
        option_strs: list of values (for enums)
        default_val: default value
        depth: port depth
    """
    # type priority table [[keyword, type]]
    # desc is searched for keywords until a match is found
    # this usually need to be updated for specific libraries

    # multiple types may be supported
    port_types = {}
    def add_port_type(port_type):
        if port_type not in port_types:
            # (type, depth) : (option list, default)
            port_types[port_type] = [[], None]
    default_val = None
    # Finds: "(default: X)"
    default_paren_re = re.compile(r"((\S*)\s+)?\(default:?(\s+((\[[^\]]*\])|([^\s\[]*)))?\)",
                                  re.IGNORECASE)
    # Finds: "default [value] id: X"
    default_is_re = re.compile(r"default\s+(value\s+)?is\s+((\[[^\]]*\])|([^\s\[]*))", re.IGNORECASE)

    def parse_desc(opt):
        # search for type keywords
        for key, value in conf.key_to_type:
            if key in opt:
                add_port_type((value, 0))
                if conf.typed_lists and value == 'basic:List':
                    for key, listtype in conf.list_types:
                        if key in opt:
                            # Convert list to type of depth 1
                            del port_types[(value, 0)]
                            add_port_type((listtype, 1))
                            break

                return True
        return False

    def parse_opts(opts, default_val):
        for opt in opts:
            opt = opt.strip()
            m = default_paren_re.search(opt)
            if m:
                # it is a default value
                _, before_res, _, after_res, _, _= m.groups()
                if after_res:
                    #assert default_val is None, ('Multiple defaults: '
                    #        '"%s" "%s"' % (default_val, after_res))
                    default_val = after_res
                    opt = after_res
                elif before_res:
                    #assert default_val is None, ('Multiple defaults: '
                    #        '"%s" "%s"' % (default_val, before_res))
                    default_val = before_res
                    opt = before_res
            found_type = False
            opt_lower = opt.lower()
            if opt_lower == "none":
                # Ignores None types
                found_type = True
            elif opt_lower == "true" or opt_lower == "false":
                found_type = True
                add_port_type(("basic:Boolean", 0))
            else:
                # search for type keywords
                found_type = found_type or parse_desc(opt_lower)

            if not found_type:
                (val, port_type) = get_value_and_type(opt)
                if port_type is not None:
                    add_port_type((port_type, 0))
                    if val is not None and (not isinstance(val, basestring)
                                      or (',' not in val and ' ' not in val)):
                        port_types[(port_type, 0)][0].append(val)

        return default_val

    if '|' in desc:
        # assume multiple types or enum values
        m = re.search("\[([\s\S]*?)\]", desc)
        if m:
            opt_str = m.group(1)
        else:
            opt_str = desc
        opts = opt_str.split('|')
        default_val = parse_opts(opts, default_val)

    if '{' in desc:
        # assume enum values separated by comma
        m = re.search("\{([\s\S]*?)\}", desc)
        if m:
            opt_str = m.group(1)
        else:
            opt_str = desc
        if '(' not in opt_str: # cannot handle weird nesting
            opts = opt_str.split(',')
            default_val = parse_opts(opts, default_val)

    if ' or ' in desc:
        # assume multiple types or enum values
        opts = desc.split(' or ')
        default_val = parse_opts(opts, default_val)

    # search for default value
    if default_val is None:
        m = default_paren_re.search(desc)
        if m:
            _, before_res, _, after_res, _, _= m.groups()
            if after_res:
                default_val = after_res
            elif before_res:
                default_val = before_res
        else:
            m = default_is_re.search(desc)
            if m:
                _, default_val, _, _ = m.groups()
                if default_val.endswith('.') or default_val.endswith(','):
                    default_val = default_val[:-1]

    if default_val is not None:
        (default_val, port_type) = get_value_and_type(default_val)
        if port_type is not None:
            add_port_type((port_type, 0))
            port_types[((port_type, 0))][1] = default_val

    if len(port_types) == 0:
        # only check first line
        line1 = desc.split('\n')[0]
        parse_desc(line1.lower())

    return port_types


class PythonParser(object):
    """
    Class that can turn python functions and classes into module specifications

    """
    def __init__(self, **kwargs):
        """
        Parameters
        ----------
        default_type : string
          Default vistrail type when it cannot be determined
        instance_type : string
          Default vistrail type for class instances
        typed_lists : bool
          whether to use type lists of depth 1 when possible
        key_to_type : list
          Defines the types that will be parsed
          See default_key_to_type
        list_types : list
          types that can be converted from list to depth 1 type
          See default_list_types
        alt_suffixes : list
          Defines name suffixes for alternate port types
          See default_alt_suffixes
        parsers : list of functions
          List of parser methods to use in order (default is numpydoc)
        type_string_parser : function
          custom type string parser function
          Default is parse_type_string
        class_spec : class
          Class specification. Default is ClassSpec
        function_spec : class
          Function specification. Default is FunctionSpec
        """
        self.default_type = kwargs.pop('default_type', 'basic:Variant')
        self.instance_type = kwargs.pop('instance_type', None)
        self.typed_lists = kwargs.pop('typed_lists', True)
        self.key_to_type = kwargs.pop('key_to_type', default_key_to_type)
        self.list_types = kwargs.pop('list_types', default_list_types)
        self.alt_suffixes = kwargs.pop('alt_suffixes', default_alt_suffixes)
        self.parsers = kwargs.pop('parsers', parse_numpydoc)
        if not isinstance(self.parsers, list):
            self.parsers = [self.parsers]
        self.type_string_parser = kwargs.pop('type_string_parser',
                                             parse_type_string)
        self.class_spec = kwargs.pop('class_spec', ClassSpec)
        self.function_spec = kwargs.pop('function_spec', FunctionSpec)

    def parse(self, object):
        # Extract port information from object using self.parsers

        sections =  '', [], [], [], []
        if not self.parsers:
            return sections
        for parser in self.parsers:
            new_sec = parser(object)
            if new_sec[0] and not sections[0]:
                sections[0] = new_sec[0]
            for s1, s2 in zip(sections[1:], new_sec[1:]):
                s1.extend(s2)
        return clean_sections(*sections)

    def parse_argspec(self, obj_or_str):
        """ parse method signature and extract types using default values

            returns {arg:(arg_pos, default)}
        """
        if isinstance(obj_or_str, basestring):
            obj_or_str = obj_or_str.strip()
            if '[,' in obj_or_str or ',[' in obj_or_str:
                # brackets may be used around optional args
                # but we cannot parse those yet
                obj_or_str = obj_or_str.replace('[', '').replace(']', '')
            if not obj_or_str.endswith(":"):
                obj_or_str += ":"
            if not obj_or_str.startswith("def "):
                obj_or_str = "def " + obj_or_str
            try:
                tree = ast.parse(obj_or_str + "\n  pass")
            except SyntaxError:
                # cannot parse the argspec
                print "*** CANNOT PARSE", obj_or_str
                return {}
            argspec_name = tree.body[0].name
            argspec_args = [a.id for a in tree.body[0].args.args]
            argspec_defaults = []
            for i, d in enumerate(tree.body[0].args.defaults):
                try:
                    d_val = ast.literal_eval(d)
                except ValueError:
                    d_val = None
                argspec_defaults.append(d_val)
        else:
            argspec = None
            if hasattr(obj_or_str, '__init__'):
                try:
                    argspec = inspect.getargspec(obj_or_str.__init__)
                except:
                    pass
            if argspec is None:
                try:
                    argspec = inspect.getargspec(obj_or_str)
                except:
                    return {}
            argspec_args = argspec.args
            argspec_defaults = argspec.defaults

        if not argspec_defaults:
            start_defaults = len(argspec_args) + 1
        else:
            start_defaults = len(argspec_args) - len(argspec_defaults)
        port_specs = {}
        has_self = False
        for i, arg in enumerate(argspec_args):
            if i == 0 and arg == "self":
                has_self = True
                continue
            default = None
            if i >= start_defaults:
                arg_pos = -1
                default = argspec_defaults[i-start_defaults]
                try:
                    literal_eval(repr(default))
                except:
                    # not reversible
                    default = None
            else:
                arg_pos = (i-1) if has_self else i
            port_specs[arg] = (arg_pos, default)
        return port_specs

    def parse_arguments(self, sig_dict, arguments, klass=False, method=None, is_operation=False, output_type=None):
        """ parsing arguments using signature and documentation
            returns list of parsed input ports
        """
        Spec = self.class_spec if klass else self.function_spec
        input_specs = []
        for arg, typestring, fdocstring in arguments:
            port_types = self.type_string_parser(typestring, self)
            sig_arg = sig_dict.get(arg, None)
            # Add type from sig if there is no other default
            if sig_arg and sig_arg[1] is not None and not [v[1] for v in port_types.itervalues() if v[1] is not None]:
                sig_type = get_type_from_val(sig_arg[1]), 0
                if sig_type not in port_types:
                    port_types[sig_type] = [0, sig_arg[1]]
            method_name = arg
            optional = 'optional' in typestring
            alt_specs = []
            if ('basic:Float', 0) in port_types and \
               ('basic:Integer', 0) in port_types:
                del port_types[('basic:Integer', 0)]

            ports = port_types.keys()
            if not ports:
                port_type, option_strs, default_val, depth = \
                    self.default_type, [], None, 0
            elif len(ports) == 1:
                (port_type, depth), (option_strs, default_val) = port_types.items()[0]
            else:
                # put port with default value first
                option_strs, default_val = port_types[ports[0]]

                # search other port defaults
                if default_val is None:
                    for i, port in enumerate(ports):
                        if port_types[port][1] is not None:
                            # move port first
                            tmp = ports[0]
                            ports[0] = ports[i]
                            ports[i] = tmp
                            option_strs, default_val = port_types[ports[0]]
                            break

                port_type, depth = ports[0]

            # search signature defaults
            if default_val is None:
                if arg in sig_dict and sig_dict[arg][1] is not None:
                     default_val = sig_dict[arg][1]

            arg_pos, sig_default = sig_dict.get(arg, (-1, None))
            if sig_default is not None and port_type == self.default_type:
                port_type = get_type_from_val(default_val)
            if sig_default is not None and default_val is None:
                default_val = sig_default

            if default_val is None:
                # try to parse fdocstring
                default_types = self.type_string_parser(fdocstring, self)
                for default_port, p in default_types.items():
                    if p[1] is not None:
                        # find port with this type
                        for i, port in enumerate(ports):
                            if default_port == port:
                                # move port first
                                tmp = ports[0]
                                ports[0] = ports[i]
                                ports[i] = tmp
                                option_strs, default_val = p
                                break
                        break

            if len(port_types) > 1:
                # create alternate specs
                port_type, depth = ports[0]
                if depth > 0:
                    method_name = arg + self.alt_suffixes['basic:List']
                else:
                    # an unknown port will get default name
                    method_name = arg + self.alt_suffixes.get(port_type, '')

                used_names = [method_name]
                for port in ports[1:]:
                    port_type2, depth2 = port
                    option_strs2, default_val2 = port_types[port]
                    if depth2 > 0:
                        method_name2 = arg + self.alt_suffixes['basic:List']
                    else:
                        method_name2 = arg + self.alt_suffixes.get(port_type2, '')
                    if method_name2 in used_names:
                        print "WARNING: Skipping alt port with existing name '%s'" % method_name2
                        if len(port_types) == 2:
                            # reset method_name
                            method_name = arg
                        continue
                    used_names.append(method_name2)
                    alt_spec = Spec.InputSpecType(
                        name=method_name2,
                        arg=arg,
                        port_type=port_type2,
                        depth=depth2)
                    if klass:
                        alt_spec.method_type = 'argument'

                    if option_strs2 and len(option_strs2) > 1:
                        alt_spec.entry_types = ['enum']
                        alt_spec.values = [option_strs2]
                    if default_val2 is not None:
                        alt_spec.defaults = [default_val2]
                    alt_specs.append(alt_spec)

            if default_val is not None:
                # add as kwarg
                arg_pos = -1
                show_port = False
            else:
                # never auto-add as argv
                arg_pos = -1
                # we still hide it if it is optional
                show_port = not optional
            input_spec = Spec.InputSpecType(
                name=method_name,
                arg=arg,
                port_type=port_type,
                arg_pos=arg_pos,
                defaults=[default_val] if default_val is not None else None,
                show_port=show_port,
                sort_key=arg_pos,
                depth=depth,
                docstring=fdocstring,
                alternate_specs=alt_specs)
            if klass:
                input_spec.method_type = 'argument'

            if option_strs and len(option_strs) > 1:
                input_spec.entry_types = ['enum']
                input_spec.values = [option_strs]

            input_specs.append(input_spec)
            # remove added arg
            if arg in sig_dict:
                del sig_dict[arg]
        # add args not in docstring
        for arg, (i, default_val) in sig_dict.iteritems():
            port_type = get_type_from_val(default_val)

            if default_val:
                # add as kwarg
                arg_pos = -1
                show_port = False
            else:
                # never auto-add as argv
                arg_pos = -1
                show_port = True

            input_spec = Spec.InputSpecType(
                name=arg,
                arg=arg,
                port_type=port_type or self.default_type,
                arg_pos=arg_pos,
                defaults=[default_val] if default_val else None,
                show_port=show_port,
                sort_key=arg_pos)
            if klass:
                input_spec.method_type = 'argument'
            input_specs.append(input_spec)

        if is_operation:
            # Add op port
            input_spec = Spec.InputSpecType(
                name='operation',
                port_type=output_type or method,
                depth=1,
                arg_pos=-5,
                show_port=True,
                sort_key=-1000,
                docstring='Chained operations')
            input_specs.append(input_spec)
        elif method:
            # Add self port
            input_spec = Spec.InputSpecType(
                name='Instance',
                port_type=method,
                arg_pos=-4,
                min_conns=1,
                max_conns=1,
                show_port=True,
                sort_key=-1000,
                docstring='The class instance to use')
            input_specs.append(input_spec)
        return input_specs

    def parse_function_returns(self, returns, output_type=None):
        """ parsing arguments using signature and documentation
            returns list of parsed input ports
        """
        input_specs = []
        for i, (arg, typestring, fdocstring) in enumerate(returns):
            if arg.lower() == "none":
                return []
            if not typestring:
                # No-name return value
                typestring = arg
                arg = 'value'

            port_types = self.type_string_parser(typestring, self)
            if ('basic:Float', 0) in port_types and ('basic:Integer', 0) in port_types:
                del port_types[('basic:Integer', 0)]

            if not port_types:
                port_type, depth = output_type or self.default_type, 0
            else:
                port_type, depth = port_types.keys()[0]

            input_spec = self.function_spec.OutputSpecType(
                name=arg,
                arg=arg,
                port_type=port_type,
                show_port=True,
                sort_key=i,
                depth=depth,
                docstring=fdocstring)

            input_specs.append(input_spec)

        return input_specs

    def parse_attributes(self, c, attributes, parse_arguments=True):
        """ Create port specs from attribute descriptions
         c - class
         attributes - [(name, typestring, docstring)]
        """
        input_specs = []
        output_specs = []
        # instance attributes are by default input/output (setter/getter)
        sort_key = 1000 # put attrs after args
        for attr, typestring, docstring in attributes:
            if parse_arguments:
                port_name = '.' + attr
            else:
                port_name = attr
            port_types = self.type_string_parser(typestring, self)
            if not port_types:
                port_type, depth = self.default_type, 0
            else:
                port_type, depth = port_types.keys()[0]

            # get type from typestring and docstring from attribute or fdocstring
            try:
                attribute = getattr(c, attr)
                adocstring = pydoc.getdoc(attribute)
            except:
                adocstring = ''
            # keep longest docstring
            if len(adocstring) > len(docstring):
                docstring = adocstring

            # setter
            input_spec = self.class_spec.InputSpecType(
                name=port_name,
                arg=attr,
                method_type='attribute',
                port_type=port_type,
                depth=depth,
                sort_key=sort_key,
                show_port=False,
                docstring=docstring)
            input_specs.append(input_spec)

            # getter
            output_spec = self.class_spec.OutputSpecType(
                name=port_name,
                arg=attr,
                method_type='attribute',
                port_type=port_type,
                depth=depth,
                sort_key=sort_key,
                show_port=False,
                docstring=docstring)
            output_specs.append(output_spec)
            sort_key += 1

        return input_specs, output_specs

    def parse_methods(self, c, methods):
        """ generate port specs from a class method
        """
        # a method to automatically get methods
        # but usually we only want the documented ones
        #method_sigs = [q for q in inspect.getmembers(c)
        #           if q[0][0]!='_' and q[1].__class__.__name__ == 'method_descriptor']
        input_specs = []
        output_specs = []

        for arg, typestring, fdocstring in methods:
            # Assume input if it has parameters, output if it has return value, skip otherwise
            # TODO: It cannot tell nullaries apart from missing docstrings
            # If it has both, call input and then fetch result for output
            # use method docstring since it is the only one with parseable types
            # loop through arg sigs and add one alt port for each additional arg with default
            try:
                argument = getattr(c,arg)
                arg_dict = self.parse_argspec(argument)
                _, parameters, _, _, returns = self.parse(argument)
            except:
                continue
            required_args = max([i[0] for i in arg_dict.values()]) + 1 if arg_dict else 0
            if not parameters and not returns:
                continue

            #port_types = self.type_string_parser(typestring, self)
            if parameters:
                name_list = []
                type_list = []
                default_list = []
                for argname, typestring, fdocstring in parameters:
                    port_types = self.type_string_parser(typestring, self)
                    if not port_types:
                        port_type, depth, default_val = self.default_type, 0, None
                    else:
                        (port_type, depth), (_, default_val) = port_types.items()[0]
                    if depth > 0:
                        port_type, depth = 'basic:List', 0
                    if default_val is None and argname in arg_dict and arg_dict[argname][1] is not None:
                        default_val = arg_dict[argname][1]
                    if default_val is not None:
                        default_type = get_type_from_val(default_val)
                        if port_type != default_val:
                            port_type = default_type
                    name_list.append(argname)
                    type_list.append(port_type)
                    default_list.append(default_val)

                # TODO: Remove alts and just add blanks

                method_type = 'method'
                port_name = ','.join(name_list)
                port_type = ','.join(type_list)
                if not port_type:
                    # We add empty methods as booleans
                    method_type = 'nullary'
                    port_type = 'basic:Boolean'
                input_spec = self.class_spec.InputSpecType(
                    name='%s(%s)' % (arg, port_name),
                    arg=arg,
                    method_type=method_type,
                    port_type=port_type,
                    show_port=False,
                    defaults=default_list,
                    docstring=pydoc.getdoc(argument) or fdocstring)
                input_specs.append(input_spec)

            if returns:
                type_list = []
                for _, typestring, fdocstring in returns:
                    port_types = self.type_string_parser(typestring, self)
                    if not port_types:
                        port_type, depth = self.default_type, 0
                    else:
                        port_type, depth = port_types.keys()[0]
                    if depth > 0:
                        port_type, depth = 'basic:List', 0
                    type_list.append(port_type)

                output_spec = self.class_spec.OutputSpecType(
                    name=arg + '(...)',
                    arg=arg,
                    port_type=','.join(type_list),
                    show_port=False,
                    docstring=pydoc.getdoc(argument) or fdocstring)
                output_specs.append(output_spec)
        return input_specs, output_specs

    def parse_class(self, c, name=None, code_ref=None, namespace=None,
                    argument_parsing=True, attribute_parsing=True,
                    method_parsing=False):
        """
        generate port specs for parameters, attributes, and methods

        Parameters
        ----------
        c : class
            class to parse
        name : string
            name of class
        code_ref : string
            class import string
        namespace : string
            module namespace
        argument_parsing : bool
            Should we parse arguments?
        attribute_parsing : bool
            Should we parse attributes?
        method_parsing : bool
            Should we parse methods?

        """
        if isinstance(c, basestring):
            if name is None:
                name = c.rsplit('.', 1)[-1]
            if code_ref is None:
                code_ref = c
            m, n = c.rsplit('.', 1)
            c = getattr(importlib.import_module(m), n)
        else:
            if name is None:
                name = c.__name__
            if code_ref is None:
                code_ref = c.__module__ + '.' + c.__name__

        # parse documentation
        signature, parameters, attributes, methods, _ = self.parse(c)

        input_specs = []
        output_specs = []

        # Add input/output Instance
        if self.instance_type:
            port_type = self.instance_type
        else:
            port_type = (namespace + '|' if namespace else '') + name
        if attribute_parsing or method_parsing:
            # it can be used with existing instance
            input_spec = self.class_spec.InputSpecType(
                name='Instance',
                method_type='Instance',
                port_type=port_type,
                # show input Instance if args are skipped (inspector mode)
                show_port=not argument_parsing,
                sort_key=-1000,
                docstring='The class instance to use')
            if not argument_parsing:
                input_spec.min_conns = 1
                input_spec.max_conns = 1
            input_specs.append(input_spec)
        output_spec = self.class_spec.OutputSpecType(
            name='Instance',
            method_type='Instance',
            port_type=port_type,
            show_port=True,
            sort_key=-1000,
            docstring='The class instance')
        output_specs.append(output_spec)

        # compute arguments
        if argument_parsing:
            # parse signature
            if signature:
                arg_dict = self.parse_argspec(signature)
            else:
                arg_dict = self.parse_argspec(c)
            input_specs.extend(self.parse_arguments(arg_dict, parameters, klass=True))

        if attribute_parsing:
            inputs, outputs = self.parse_attributes(c, attributes, argument_parsing)
            input_specs.extend(inputs)
            output_specs.extend(outputs)

        if method_parsing:
            method_inputs, method_outputs = self.parse_methods(c, methods)
            input_specs.extend(method_inputs)
            output_specs.extend(method_outputs)

        spec = self.class_spec(module_name=name,
                               code_ref=code_ref,
                               docstring=pydoc.getdoc(c) or '',
                               namespace=namespace,
                               input_port_specs=input_specs,
                               output_port_specs=output_specs)
        return spec

    def parse_class_methods(self, c, classname=None, namespace=None, operation=False):
        """
        Create a module for each class method

        Parameters
        ----------
        c : class
          class to parse
        classname : string
          class type signature
        namespace : string
          module namespace
        operation: string or boolean
          Create as operations that is input to class
          Can be a type string

        """
        if isinstance(c, basestring):
            m, n = c.rsplit('.', 1)
            c = getattr(importlib.import_module(m), n)

        # get documented methods
        _, _, _, methods, _ = self.parse(c)
        specs = []
        for arg, _, _ in methods:
            specs.append(self.parse_function(getattr(c, arg),
                                             namespace=namespace,
                                             method=classname or self.instance_type,
                                             is_operation=operation))
        return specs

    def parse_function(self, f, name=None, code_ref=None, namespace=None,
                       method=None, is_empty=False, output_type=None,
                       is_operation=False, operations={}):
        """
        Parmeters
        ---------
        f : function or string
            Function to parse
        name : string
            module name
        code_ref : string
        method : string or None
            If set the function will be parsed as a class method
        is_empty : bool
            Ignore return values (Methods returns instance)
        is_operation : string or bool
            Ignore return values (Methods returns itself as operation)
            Can contain operation type

        """
        if isinstance(is_operation, bool):
            custom_output_type = output_type
        else:
            custom_output_type = is_operation
        if method is True:
            method = self.instance_type
        if isinstance(f, basestring):
            if name is None:
                if method:
                    name = '.'.join(f.rsplit('.', 2)[-2:])
                else:
                    name = f.rsplit('.', 1)[-1]
            if code_ref is None:
                code_ref = f
            if method:
                m, c, n = f.rsplit('.', 2)
                f = getattr(getattr(importlib.import_module(m), c), n)
            else:
                m, n = f.rsplit('.', 1)
                f = getattr(importlib.import_module(m), n)
        else:
            if name is None:
                if method:
                    klass = f.im_class
                    name =  klass.__name__ + '.' + f.__name__
                else:
                    name = f.__name__
            if code_ref is None:
                if method:
                    klass = f.im_class
                    code_ref =  klass.__module__ + '.' + klass.__name__ + '.' + f.__name__
                else:
                    code_ref = f.__module__ + '.' + f.__name__

        signature, parameters, _, _, returns = self.parse(f)

        # parse signature
        arg_dict = self.parse_argspec(f)
        if not arg_dict and signature:
            arg_dict = self.parse_argspec(signature)
        input_specs = self.parse_arguments(arg_dict, parameters, method=method,
                                           is_operation=is_operation,
                                           output_type=custom_output_type)

        if is_operation:
            # add base type input port for chaining operations
            input_specs.append(self.function_spec.InputSpecType(
                name='operation',
                arg='operation',
                arg_pos=-5, # is operation type
                port_type=custom_output_type or self.default_type,
                depth=1,
                show_port=True))

        for op_name, op_type in operations.items():
            # operations that will be applied to the result of this function
            input_specs.append(self.function_spec.InputSpecType(
                name=op_name,
                arg=op_name,
                arg_pos=-5, # is operation type
                port_type=op_type,
                depth=1,
                show_port=True))

        output_specs = []
        if not is_empty:
            output_specs = self.parse_function_returns(returns, custom_output_type)
            if not output_specs:
                # Add default port
                output_specs.append(self.function_spec.OutputSpecType(
                    name='value',
                    arg='value',
                    port_type=custom_output_type or self.default_type,
                    show_port=True))

        depth = 1 if is_operation else 0
        if not output_specs and method:
            # Methods without return value returns instance
            output_type = 'self'
            output_specs.append(self.function_spec.OutputSpecType(
                name='Instance',
                arg='Instance',
                port_type=custom_output_type or method,
                depth=depth,
                show_port=True))
        elif not output_specs:
            output_type = 'none'
        elif len(output_specs) == 1:
            output_type = 'object'
        else:
            output_type = 'list'

        if is_operation:
            method_type = 'operation'
        elif method:
            method_type = 'method'
        else:
            method_type = 'function'

        spec = self.function_spec(module_name=name,
                                  code_ref=code_ref,
                                  docstring=pydoc.getdoc(f) or '',
                                  namespace=namespace,
                                  method_type=method_type,
                                  output_type=output_type,
                                  input_port_specs=input_specs,
                                  output_port_specs=output_specs)
        return spec

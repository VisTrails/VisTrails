import itertools
import sys

import vistrails.core.application
from vistrails.core.api import Package
from vistrails.core.modules.module_registry import get_module_registry

heading_order = ['*', '=', '^', '-', '"', '+', '#']

def trim_docstring(docstring):
    """Copied from PEP 257: http://www.python.org/dev/peps/pep-0257/"""
    if not docstring:
        return ''
    # Convert tabs to spaces (following the normal Python rules)
    # and split into a list of lines:
    lines = docstring.expandtabs().splitlines()
    # Determine minimum indentation (first line doesn't count):
    indent = sys.maxint
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent < sys.maxint:
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())
    # Strip off trailing and leading blank lines:
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)
    # Return a single string:
    return '\n'.join(trimmed)

def indent_docstring(docstring, indent=0):
    new_docstring = ""
    for line in docstring.splitlines():
        new_docstring += (" " * indent) + line + "\n"
    return new_docstring

def format_docstring(docstring, indent=0):
    return indent_docstring(trim_docstring(docstring), indent)

def get_examples(desc):
    return []

def generate_module_doc(desc, f=None, depth=1, inherited=True):
    reg = get_module_registry()
    print >>f, desc.name
    print >>f, heading_order[depth] * len(desc.name)
    print >>f, ""
    print >>f, ".. py:class:: %s" % desc.name
    print >>f, ""
    if desc.module.__doc__:
        print >>f, format_docstring(desc.module.__doc__, 2)
        print >>f, ""

    if inherited:
        input_ports = reg.module_destination_ports_from_descriptor(True, desc)
        output_ports = reg.module_source_ports_from_descriptor(True, desc)
    else:
        input_ports = reg.module_ports('input', desc).values()
        input_ports.sort(key=lambda x: (x.sort_key, x.id))
        output_ports = reg.module_ports('output', desc).values()
        output_ports.sort(key=lambda x: (x.sort_key, x.id))
        
    if len(input_ports) > 0:
        print >>f, "  *Input Ports*"
        for port in input_ports:
            sigstring = port.sigstring.replace(':', '.')[1:-1]
            print >>f, "    .. py:attribute:: %s" % port.name
            print >>f, ""            
            print >>f, "      | *Signature*: :py:class:`%s`" % sigstring
            if port.docstring():
                print >>f, "      | *Description*: %s" % format_docstring(port.docstring(), 9)
            print >>f, ""
    if len(output_ports) > 0:
        print >>f, "  *Output Ports*"
        for port in output_ports:
            sigstring = port.sigstring.replace(':', '.')[1:-1]
            print >>f, "    .. py:attribute:: %s" % port.name
            print >>f, ""            
            print >>f, "      | *Signature*: :py:class:`%s`" % sigstring
            if port.docstring():
                print >>f, "      | *Description*: %s" % format_docstring(port.docstring(), 9)
            print >>f, ""

    examples = get_examples(desc)
    if len(examples) > 0:
        print >>f, "  *Examples*"
        for example in examples:
            print >>f, "   * %s" % example
        print >>f, ""

def generate_docs(pkg, namespace=None, f=None):
    print >>f, pkg._package.name
    print >>f, heading_order[0] * len(pkg._package.name)
    print >>f, ""
    print >>f, ".. py:module:: %s\n" % pkg._package.identifier
    print >>f, '| *Identifier*: %s' % pkg._package.identifier
    print >>f, '| *Version*: %s\n' % pkg._package.version
    print >>f, format_docstring(pkg._package.description, 0)
    print >>f, ""
    
    if namespace == '':
        for desc in pkg._namespaces[1]:
            generate_module_doc(desc, f, 1)
    else:
        if namespace is None:
            namespace = ''
            for desc in pkg._namespaces[1]:
                generate_module_doc(desc, f)
            namespaces = sorted(item + (1,) for item in 
                                pkg._namespaces[0].iteritems())
        else:
            namespace_dict = pkg._namespaces[0]
            descs = pkg._namespaces[1]
            split_ns = namespace.split('|')
            for i, ns in enumerate(split_ns):
                print >>f, ns
                print >>f, heading_order[i+1] * len(ns)
                print >>f, ""
                (namespace_dict, descs) = namespace_dict[ns]
            namespaces = [(namespace, (namespace_dict, descs), len(split_ns))]
        
        for (ns, (child_namespaces, descs), depth) in namespaces:
            print >>f, ns
            print >>f, heading_order[depth] * len(ns)
            print >>f, ""
            for desc in descs:
                generate_module_doc(desc, f, depth+1)
            namespaces = \
                itertools.chain([(ns + '|' + c[0], c[1]) 
                                 for c in child_namespaces.iteritems()],
                                namespaces, depth+1)

def run():
    vistrails.core.application.init()
    pkg = Package("org.vistrails.vistrails.basic")
    # pkg = Package("org.vistrails.vistrails.matplotlib")
    generate_docs(pkg)

if __name__ == '__main__':
    run()

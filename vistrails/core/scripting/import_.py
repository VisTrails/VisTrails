"""Python to pipeline importing logic.

This contains read_workflow_from_python(), which imports a standalone Python
script as a VisTrails pipeline a standalone Python script.
"""

from __future__ import division, unicode_literals

import ast
import re
import redbaron
import urllib2

from vistrails.core import debug
from vistrails.core.db.action import create_action
from vistrails.core.modules.module_registry import get_module_registry, \
    ModuleRegistryException
from vistrails.core.modules.utils import parse_descriptor_string
from vistrails.core.vistrail.port_spec import PortSpec


NUMBER_LITERALS = (redbaron.IntNode, redbaron.FloatNode, redbaron.LongNode,
                   redbaron.OctaNode, redbaron.HexaNode)


def eval_int_literal(node):
    """Takes one of the number literal nodes and returns its value.
    """
    if not isinstance(node, NUMBER_LITERALS):
        raise ValueError
    if isinstance(node, redbaron.IntNode):
        # FIXME: This branch probably shouldn't be required, filed as
        # https://github.com/Psycojoker/redbaron/issues/65
        return node.value
    else:
        return ast.literal_eval(node.value)


def line_number(node):
    """Gets the number of the first line of a node.
    """
    return node.absolute_bounding_box.top_left.line


class EndOfInput(Exception):
    """Unexpected end of input script.
    """


def next_node(script, pos):
    """Go to the next non-empty line of the script.
    """
    script_len = len(script)
    while True:
        if pos >= script_len:
            raise EndOfInput
        node = script[pos]
        print "node: %s" % node.dumps()
        pos += 1
        if not isinstance(node, redbaron.EndlNode):
            print "returning %s" % node.dumps()
            return pos, node


def re_multi(regexps, s):
    """Tests multiple regular expressions against one string.
    """
    for r in regexps:
        match = r.match(s)
        if match is not None:
            return r, match
    return None, None


MODULE_ANNOTATION = re.compile(
        r'^# MODULE ([0-9]+) ([\'A-Za-z0-9_:|]+)$')
FUNCTION_ANNOTATION = re.compile(
        r'^# FUNCTION ([A-Za-z0-9_]+) ([A-Za-z0-9_]+)$')
CONNECTION_ANNOTATION = re.compile(
        r'^# CONNECTION ([A-Za-z0-9_]+) ([A-Za-z0-9_]+)$')


def read_workflow_from_python(controller, filename):
    """Imports a Python script as a workflow on the given controller.
    """
    registry = get_module_registry()

    # FIXME: Unicode support?
    with open(filename, 'rb') as f:
        script = redbaron.RedBaron(f.read())
    print "Got %d-line Python script" % len(script)

    # Previous modules
    pipeline = controller.current_pipeline
    prev_modules = set((mod.id, mod.name)
                       for mod in pipeline.module_list)
    seen_modules = set()

    # Output port <-> variable name mapping
    oport_to_var = {}  # (mod_id, port_name): var_name
    var_to_oport = {}  # var_name: (mod, port_name)

    ops = []

    # Read the script
    pos = 0
    len_script = len(script)
    module_desc, module_id = None, None
    iports = {}
    functions = []
    while True:
        try:
            pos, node = next_node(script, pos)
        except EndOfInput:
            break

        print "% 4d - - -\n%s\n     -----" % (line_number(node), node.dumps())

        # Try to read an annotation
        if isinstance(script, redbaron.CommentNode):
            r, m = re_multi((MODULE_ANNOTATION, FUNCTION_ANNOTATION,
                             CONNECTION_ANNOTATION), node.value)
            if r is MODULE_ANNOTATION:
                if module_desc is not None:
                    debug.warning("Unexpected MODULE annotations line %d" %
                                  line_number(node))
                module_id = int(m.group(1))
                sigstring = ast.literal_eval(m.group(2))
                iports = {}
                print "next block is module %r, id=%d" % (sigstring, module_id)
                info = parse_descriptor_string(sigstring)
                try:
                    module_desc = registry.get_descriptor_by_name(*info)
                except ModuleRegistryException as e:
                    debug.warning("Couldn't find module from annotation %r: " %
                                  sigstring, e)
            elif r is FUNCTION_ANNOTATION:
                if module_desc is None:
                    debug.warning("Unexpected FUNCTION annotation without a "
                                  "previous MODULE line %d" %
                                  line_number(node))
                else:
                    try:
                        nextpos, node = next_node(script, pos)
                    except EndOfInput:
                        debug.warning("Script ends in FUNCTION annotation")
                        break
                    port, var = m.group(1), m.group(2)
                    if (isinstance(node, redbaron.AssignmentNode) and
                            isinstance(node.target, redbaron.NameNode) and
                            node.target.value == var):
                        value = node.value.value
                        iports[port] = var
                        functions.append((m.group(1), value))
                        pos = nextpos
                        print "function: port=%r, var=%r, value=%r" % (
                                port, var, value)
                    else:
                        debug.warning("Invalid function line %d" %
                                      line_number(node))
                        # Don't advance to nextpos: the (broken) assignment
                        # line (if present) will be handled as unexpected code
            elif r is CONNECTION_ANNOTATION:
                if module_desc is None:
                    debug.warning("Unexpected CONNECTION annotation without a "
                                  "previous MODULE line %d" %
                                  line_number(node))
                else:
                    port, var = m.group(1), m.group(2)
                    if var in var_to_oport:
                        iports[port] = var
                        print "input connection: port=%r, var=%r" % (
                                port, var)
                    else:
                        debug.warning("Input CONNECTION annotation mentions "
                                      "unknown variable %s line %d" % (
                                          var, line_number(node)))
            else:
                assert r is None

        # Read code
        else:
            print "reading module line %d" % line_number(node)
            newops, pos = read_module(script, pos, controller, registry,
                                      var_to_oport, oport_to_var,
                                      module_desc, module_id, iports)
            ops.extend(newops)

            module_id = None
            module_desc = None
            functions = []
            iports = {}

    # Remove unseen modules
    ops.extend(controller.delete_module_list_ops(
            pipeline,
            set(mod.id for mod in pipeline.module_list) - seen_modules))

    action = create_action(ops)
    controller.add_new_action(action, "Imported Python script")
    controller.perform_action(action)
    controller.change_selected_version(action.id)
    return True


def read_module(script, pos, controller, registry, var_to_oport, oport_to_var,
                module_desc, module_id, iports):
    """Reads a single module from the script.

    This gets the module's code and all the info from the annotations (module
    descriptor and ID, input port mapping). It will try to read the module, or
    fallback to PythonSource, and update the workflow.
    """
    # Call the module so it can try to parse itself
    if module_desc is not None:
        try:
            print "calling from_python_script for module %s" % module_desc.name
            ret = module_desc.module.from_python_script(script, pos,
                                                        iports)
            if ret is not None:
                pos, mod_info = ret
                print "read successful, updating module in pipeline"
                # Update the workflow with the module from from_python_script()
                ops = update_module(controller, registry,
                                    var_to_oport, oport_to_var,
                                    module_desc, module_id, mod_info)
                return ops, pos
        except Exception as e:
            debug.critical("Got error while reading module into workflow!")
            debug.unexpected_exception(e)
            raise

        # The module from the annotation failed to recognize the code block
        debug.warning("Module %s could not be read back from Python "
                      "script" % module_desc.name)

    # Failed to recognize a module -- make a PythonSource
    # Stop at the next MODULE annotation or two blank lines
    print "falling back to PythonSource"
    endpos = pos + 1
    len_script = len(script)
    blank = 0
    while endpos < len_script:
        node = script[endpos]
        if (isinstance(node, redbaron.CommentNode) and
                MODULE_ANNOTATION.match(node.value) is not None):
            break
        elif isinstance(node, redbaron.EndlNode):
            blank += 1
            if blank == 2:
                break
        else:
            blank = 0
        endpos += 1

    source = script[pos:endpos]
    ops = add_pythonsource(controller, registry, var_to_oport, oport_to_var,
                           source)
    return ops, endpos


def update_module(controller, registry, var_to_oport, oport_to_var,
                  module_id, mod_info):
    """Updates the module in the workflow.

    This gets the information returned from from_python_script() and updates
    the workflow, either changing functions and connections on the module with
    the given ID, or making a new module.
    """
    new_module, new_inputs, new_outputs = mod_info[:3]
    if len(mod_info) >= 4:
        port_specs = mod_info[3]
    else:
        port_specs = None
    if isinstance(new_module, basestring):
        new_module = parse_descriptor_string(new_module)
        new_module = registry.get_descriptor_by_name(*new_module)
    else:
        new_module = registry.get_descriptor(new_module)

    # Make the module
    # TODO : update existing module module_id
    newmod = controller.create_module_from_descriptor(new_module)
    ops = [('add', newmod)]

    # Add port specs
    for i, (inout, name, sig) in enumerate(port_specs):
        newmod.add_port_spec(PortSpec(id=i,
                                      name=name,
                                      type=inout,
                                      sigstring=sig,
                                      sort_key=-1))

    # Connect inputs
    for iport, i in new_inputs.iteritems():
        print "input port %s: %r" % (iport, i)
        # Input is a variable
        if i[0] == 'var':
            varname = i[1]
            # Make connection
            omod, oport = var_to_oport[varname]
            print "connecting to mod %s %d, port %s" % (
                    omod.module_descriptor.name, omod.id, oport)
            conn = controller.create_connection(omod, oport, newmod, iport)
            ops.append(('add', conn))
        # Input is a constant
        elif i[0] == 'const':
            value = i[1]
            # Make a function
            f = controller.create_function(newmod, iport, [value])
            newmod.add_function(f)
        # That's all we accept for now
        else:
            raise ValueError("Invalid input for new module")

    # Record output
    for oport, o in new_outputs.iteritems():
        print "output port %s: %r" % (oport, o)
        # Output is a variable
        if o[0] == 'var':
            varname = o[1]
            print "associating variable %s to mod %s %d, port %s" % (
                    varname, newmod.module_descriptor.name, newmod.id, oport)
            var_to_oport[varname] = newmod, oport
            oport_to_var[(newmod.id, oport)] = varname
        # That's all we accept for now
        else:
            raise ValueError("Invalid output for new module")

    return ops


def add_pythonsource(controller, registry, var_to_oport, oport_to_var,
                     source):
    """Creates a PythonSource module from a Python block.
    """
    outputs = set()
    for node in source.find_all('AssignmentNode'):
        if node.target.NameNode:
            outputs.add(node.target.value)
    inputs = set()
    for node in source.find_all('NameNode'):
        v = node.value
        if v not in outputs and v in var_to_oport:
            inputs.add(v)

    input_map = {'source': (
        'const',
        urllib2.quote('\n'.join(s.dumps() for s in source).encode('utf-8')))}
    input_map.update((iport, ('var', iport)) for iport in inputs)
    output_map = dict((oport, ('var', oport)) for oport in outputs)
    port_specs = [('input', iport, 'org.vistrails.vistrails.basic:Variant')
                  for iport in inputs]
    return update_module(controller, registry, var_to_oport, oport_to_var,
                         None,
                         ('org.vistrails.vistrails.basic:PythonSource',
                          input_map, output_map, port_specs))


###############################################################################

import unittest


class TestImport(unittest.TestCase):
    def test_int_literals(self):
        script = redbaron.RedBaron(
                '1\n'
                '2.0\n'
                '3L\n'
                'def foo(): pass\n'
                '04\n'
                '2+2\n'
                '0x5')
        values = []
        for statement in script:
            if isinstance(statement, NUMBER_LITERALS):
                values.append(eval_int_literal(statement))
            else:
                values.append('skipped')

        self.assertEqual(values, [1, 2.0, 3, 'skipped', 4, 'skipped', 5])

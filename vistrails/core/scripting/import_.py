"""Python to pipeline importing logic.

This contains read_workflow_from_python(), which imports a standalone Python
script as a VisTrails pipeline a standalone Python script.

read_workflow_from_python() processes a full Python script, reading it from top
to bottom. It parses annotations, and calls read_module() when code for a
module is encountered.

read_module() gets a starting position in the script and the info known from
the annotations and previous module additions. It tries to read that module
using a package-supplied from_python_script(), or fallbacks on PythonSource
(using add_pythonsource()). Then update_module() is called either way.

update_module() gets in the module's info, and tries to update that module if a
module exists in the pipeline with that ID (and is the expected type), else
creates a new module. It also connects to previous module's output ports and
updates the output port mapping for future modules.
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
    # FIXME : -1 because we add a blank line before the script to workaround
    # a baron bug: https://github.com/Psycojoker/redbaron/issues/67
    return node.absolute_bounding_box.top_left.line - 1


class EndOfInput(Exception):
    """Unexpected end of input script.
    """


def next_node(script, pos):
    """Go to the next non-empty line of the script.
    """
    script_len = len(script)
    while True:
        pos += 1
        if pos >= script_len:
            raise EndOfInput
        node = script[pos]
        if not isinstance(node, redbaron.EndlNode):
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
        r'^# MODULE ([0-9]+) ([A-Za-z0-9_:.|]+)$')
FUNCTION_ANNOTATION = re.compile(
        r'^# FUNCTION ([A-Za-z0-9_]+) ([A-Za-z0-9_]+)$')
CONNECTION_ANNOTATION = re.compile(
        r'^# CONNECTION ([A-Za-z0-9_]+) ([A-Za-z0-9_]+)$')


class PythonReader(object):
    def __init__(self, controller):
        self.controller = controller
        self.registry = get_module_registry()

        # Previous modules
        self.pipeline = self.controller.current_pipeline
        self.prev_modules = set((mod.id, mod.name)
                                for mod in self.pipeline.module_list)
        self.seen_modules = set()

        # Output port mapping, used to connect modules to previous module's
        # output
        self.oport_to_var = {}  # (mod_id, port_name): var_name
        self.var_to_oport = {}  # var_name: (mod, port_name)

        self.next_module()

    def next_module(self):
        """Resets annotation state after the module has been emitted.
        """
        # What annotations tell us the next module will be
        self.module_desc, self.module_id = None, None

        # Input port mapping, from CONNECTION or FUNCTION annotation
        self.iport_to_var = {}
        self.var_to_iport = {}

        # Functions for next module, from FUNCTION annotation + assignment
        self.functions = []

    def read_file(self, filename):
        """Imports a Python script as a workflow on the given controller.

        This reads the file from top to bottom, reading annotations, and calls
        read_module() when module code is encountered.
        """
        # FIXME: Unicode support?
        with open(filename, 'rb') as f:
            # FIXME: adds '\n' to work around a bug in baron:
            # https://github.com/Psycojoker/redbaron/issues/67
            script = redbaron.RedBaron(b'\n' + f.read())
        print "Got %d-line Python script" % len(script)

        ops = []

        # Read the script
        pos = 0
        while True:
            try:
                pos, node = next_node(script, pos)
            except EndOfInput:
                break

            print "% 4d - - -\n%s\n     -----" % (line_number(node),
                                                  node.dumps())

            # Try to read an annotation
            if isinstance(node, redbaron.CommentNode):
                print "It's a comment, checking for annotation..."
                pos = self.read_annotation(script, pos)
            # Read code
            else:
                print "reading module line %d" % line_number(node)
                newops, pos = self.read_module(script, pos)
                ops.extend(newops)

                self.next_module()

        # Remove unseen modules
        ops.extend(self.controller.delete_module_list_ops(
                self.pipeline,
                [mod.id for mod in self.pipeline.module_list
                 if mod.id not in self.seen_modules]))

        action = create_action(ops)
        self.controller.add_new_action(action, "Imported Python script")
        self.controller.perform_action(action)
        self.controller.change_selected_version(action.id)

    def read_annotation(self, script, pos):
        """Handle a comment, storing info if it is a recognized annotation.
        """
        node = script[pos]
        r, m = re_multi((MODULE_ANNOTATION, FUNCTION_ANNOTATION,
                         CONNECTION_ANNOTATION), node.value)
        if r is MODULE_ANNOTATION:
            if self.module_desc is not None:
                debug.warning("Unexpected MODULE annotations line %d" %
                              line_number(node))
                self.next_module()
            module_id = int(m.group(1))
            sigstring = m.group(2)
            print "next block is module %r, id=%d" % (sigstring,
                                                      module_id)
            try:
                self.module_desc = self.registry.get_descriptor_by_name(
                        *parse_descriptor_string(sigstring))
            except ModuleRegistryException as e:
                debug.warning("Couldn't find module from annotation "
                              "%r: " % sigstring,
                              e)
        elif r is FUNCTION_ANNOTATION:
            if self.module_desc is None:
                debug.warning("Unexpected FUNCTION annotation without "
                              "a previous MODULE line %d" %
                              line_number(node))
            else:
                try:
                    nextpos, node = next_node(script, pos)
                except EndOfInput:
                    debug.warning("Script ends in FUNCTION annotation")
                    return pos
                port, var = m.group(1), m.group(2)
                if (isinstance(node, redbaron.AssignmentNode) and
                        isinstance(node.target, redbaron.NameNode) and
                        node.target.value == var):
                    value = node.value.dumps()
                    self.iport_to_var[port] = var
                    self.var_to_iport[var] = port
                    self.functions.append((port, value))
                    pos = nextpos
                    print "function: port=%r, var=%r, value=%r" % (
                            port, var, value)
                else:
                    debug.warning("Invalid function line %d" %
                                  line_number(node))
                    # Don't advance to nextpos: the (broken) assignment
                    # line (if present) will be handled as unexpected
                    # code
        elif r is CONNECTION_ANNOTATION:
            if self.module_desc is None:
                debug.warning("Unexpected CONNECTION annotation "
                              "without a previous MODULE line %d" %
                              line_number(node))
            else:
                port, var = m.group(1), m.group(2)
                if var in self.var_to_oport:
                    self.iport_to_var[port] = var
                    self.var_to_iport[var] = port
                    print "input connection: port=%r, var=%r" % (
                            port, var)
                else:
                    debug.warning("Input CONNECTION annotation "
                                  "mentions unknown variable %s line "
                                  "%d" % (var, line_number(node)))
        else:
            print "Not a recognized annotation"
            assert r is None

        return pos

    def read_module(self, script, pos):
        """Reads a single module from the script.

        This gets the module's code and all the info from the annotations
        (module descriptor and ID, input port mapping). It will try to read the
        module, or fallback to PythonSource, and update the workflow.
        """
        # Call the module so it can try to parse itself
        if self.module_desc is None:
            print "We don't know what module this is..."
        elif not hasattr(self.module_desc.module, 'from_python_script'):
            print "%s doesn't have from_python_script()" % (
                self.module_desc.module)
        else:
            try:
                print "calling from_python_script for %s" % (
                    self.module_desc.name)
                ret = self.module_desc.module.from_python_script(script, pos)

                if ret is not None:
                    pos, mod_info = ret
                    print "read successful, updating module in pipeline"
                    # Update the workflow with the module's
                    # from_python_script()
                    ops = self.update_module(mod_info)
                    return ops, pos
            except Exception as e:
                debug.critical("Got error while reading module into workflow!")
                debug.unexpected_exception(e)
                raise

            # The module from the annotation failed to recognize the code block
            debug.warning("Module %s could not be read back from Python "
                          "script" % self.module_desc.name)

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
        print "PythonSource block: %d:%d:\n%s" % (
                pos, endpos,
                '\n'.join(s.dumps() for s in source))
        ops = self.add_pythonsource(source)
        return ops, endpos

    def update_module(self, mod_info):
        """Updates the module in the workflow.

        This gets the information returned from from_python_script() and
        updates the workflow, either changing functions and connections on the
        module with the given ID, or making a new module.
        """
        new_module, new_inputs, new_outputs = mod_info[:3]
        if len(mod_info) >= 4:
            port_specs = mod_info[3]
        else:
            port_specs = None
        if isinstance(new_module, basestring):
            new_module = parse_descriptor_string(new_module)
            new_module = self.registry.get_descriptor_by_name(*new_module)
        else:
            new_module = self.registry.get_descriptor(new_module)

        print ("update_module: module %s, inputs %s, outputs %s, "
               "portspecs %s" % (new_module.name, new_inputs, new_outputs,
                                 port_specs))

        # Make the module
        # TODO : update existing module module_id
        newmod = self.controller.create_module_from_descriptor(new_module)
        ops = [('add', newmod)]

        # Add port specs
        for i, (inout, name, sig) in enumerate(port_specs):
            print "adding portspec: %s, %s, %s" % (inout, name, sig)
            ps = self.controller.create_port_spec(newmod, inout, name, sig)
            newmod.add_port_spec(ps)

        # Add functions
        for name, value in self.functions:
            func = self.controller.create_function(newmod, name, [value])
            newmod.add_function(func)

        # Connect inputs
        for iport, i in new_inputs.iteritems():
            print "input port %s: %r" % (iport, i)
            # Input is a variable
            if i[0] == 'var':
                varname = i[1]
                # Make connection
                omod, oport = self.var_to_oport[varname]
                print "connecting to mod %s %d, port %s" % (
                    omod.module_descriptor.name, omod.id, oport)
                conn = self.controller.create_connection(omod, oport,
                                                         newmod, iport)
                ops.append(('add', conn))
            # Input is a constant
            elif i[0] == 'const':
                value = i[1]
                # Make a function
                f = self.controller.create_function(newmod, iport, [value])
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
                self.var_to_oport[varname] = newmod, oport
                self.oport_to_var[(newmod.id, oport)] = varname
            # That's all we accept for now
            else:
                raise ValueError("Invalid output for new module")

        return ops

    def add_pythonsource(self, source):
        """Creates a PythonSource module from a Python block.
        """
        outputs = set()
        for node in source.find_all('AssignmentNode'):
            if node.target.NameNode:
                outputs.add(node.target.value)
        inputs = set()
        for node in source.find_all('NameNode'):
            v = node.value
            if v not in outputs:
                inputs.add(v)
        inputs.update(self.var_to_iport)

        # For PythonSource, the port names must match the associated variable
        # names, so rename the ports now
        self.iport_to_var = self.var_to_iport = dict(
                (v, v) for v in self.var_to_iport)

        # source code
        input_map = {'source': (
            'const',
            urllib2.quote('\n'.join(s.dumps() for s in source).encode('utf-8')))}
        # input ports
        input_map.update((iport, ('var', iport)) for iport in inputs)
        # output ports
        output_map = dict((oport, ('var', oport)) for oport in outputs)
        port_specs = [('input', iport, 'org.vistrails.vistrails.basic:Variant')
                      for iport in inputs]
        port_specs.extend(('output', oport, 'org.vistrails.vistrails.basic:Variant')
                          for oport in outputs)
        return self.update_module(('org.vistrails.vistrails.basic:PythonSource',
                                   input_map, output_map, port_specs))


def read_workflow_from_python(controller, filename):
    """Imports a Python script as a workflow on the given controller.

    This will create a new version *based on the current pipeline*, updating
    the modules if possible, else replacing them.
    """
    reader = PythonReader(controller)
    reader.read_file(filename)


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

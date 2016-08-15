"""This module contains utilities for manipulating Python scripts.
"""

from __future__ import division, unicode_literals

import __builtin__
import keyword

from vistrails.core.bundles import py_import
from vistrails.core.scripting.utils import utf8

reserved = list(set(keyword.kwlist + dir(__builtin__)))

redbaron = None

def get_redbaron():
    """Imports redbaron.

    Not done at top-level so that we can trigger the bundle install if/when
    needed.
    """
    global redbaron
    redbaron = py_import('redbaron', {'pip': 'redbaron'})
    return redbaron

def rename_variables(source, renames):
    """ Rename NameNodes in the code, skipping those that are not variables

    """
    get_redbaron()
    counts = {}
    for node in source.find_all('NameNode'):
        v = node.value
        if v in renames:
            # Skip if it is an attribute (followed by dot)
            if isinstance(node.previous, redbaron.DotNode):
                continue
            # Skif if this is a call argument name
            if isinstance(node.parent, redbaron.CallArgumentNode) and node.parent.target == node:
                continue
            node.value = renames[v]
            counts[v] = counts.get(v, 0) + 1
    return counts

def make_unique(name, all_vars, more_vars=set()):
    """Makes a variable name unique.

    :param all_vars: Variables in the scope, to which the one will be added
    once renamed
    :type all_vars: set
    :param more_vars: Additional identifier names to avoid
    """
    i = 1
    n = name
    while n in all_vars or n in more_vars or n in reserved:
        i += 1
        n = '%s_%d' % (name, i)
    all_vars.add(n)
    return n


class BaseScript(object):
    """A piece of Python code.
    """
    def __init__(self, source):
        get_redbaron()
        if isinstance(source, redbaron.RedBaron):
            self.source = source
        else:
            self.source = redbaron.RedBaron(utf8(source))
        # Removes empty lines
        while self.source and isinstance(self.source[0], redbaron.EndlNode):
            del self.source[0]
        while self.source and isinstance(self.source[-1], redbaron.EndlNode):
            del self.source[-1]

    def rename(self, renames):
        counts = rename_variables(self.source, renames)
        if not counts:
            print("rename():\n    no renames")
        else:
            print("rename():")
            for v, c in counts.iteritems():
                print("    %s: %d" % (v, c))

    def __unicode__(self):
        return self.source.dumps().strip()


class Prelude(BaseScript):
    """A piece of code that should be inserted at the beginning.
    """
    # Defined variables are the symbols that are created by this prelude code
    # The scripts that use this prelude will want to use these
    # We rename them if they clash with other preludes; in that case we rename
    # in the same way in each script that uses the prelude
    defined_vars = None
    # Imported packages are symbols that are created by importing a package of
    # the same name (top-level only)
    # For example, 'import vistrails.api' creates a symbol 'vistrails'
    # We don't rename these and it doesn't matter if they collide
    imported_pkgs = None

    def __init__(self, source, prelude_id=None):
        BaseScript.__init__(self, source)
        if prelude_id is None:
            self.prelude_id = id(source)
        else:
            self.prelude_id = prelude_id

        self.defined_vars = set()
        self.imported_pkgs = set()
        # Variable assignments
        for assign in self.source.find_all('AssignmentNode'):
            # a = 2 -> 'a' is a defined variable
            if assign.target:
                self.defined_vars.add(assign.target.value)
        # Imports
        for imp in self.source.find_all('ImportNode'):
            for v in imp.value:
                if not v.dotted_as_name:
                    continue
                # import a.b as c -> 'c' is a defined variable
                if v.target:
                    self.defined_vars.add(v.target)
                # import a.b -> 'b' is an imported package
                else:
                    self.imported_pkgs.add(v.value.value[0])
        for imp in self.source.find_all('FromImportNode'):
            for v in imp.targets:
                # from a import b as c -> 'c' is a defined variable
                if v.target:
                    self.defined_vars.add(v.target)
                # from a import b -> 'b' is a defined variable
                else:
                    self.defined_vars.add(v.value)

    def avoid_collisions(self, all_vars):
        """Renames the variables to avoid collisions.
        """
        renames = {}
        for name in self.defined_vars:
            if name in all_vars:
                # Collision!
                nname = make_unique(name, all_vars, self.defined_vars)
                renames[name] = nname
                self.defined_vars.discard(name)
                self.defined_vars.add(nname)
            else:
                all_vars.add(name)
        self.rename(renames)
        return renames

    def __hash__(self):
        return hash(self.prelude_id)

    def __eq__(self, other):
        return (isinstance(other, Prelude) and
                self.prelude_id == other.prelude_id)

    def __ne__(self, other):
        return not self.__eq__(other)


class Script(BaseScript):
    """Wrapper for a piece of Python script.

    This holds a piece of code (BaseScript) plus information on how the
    inputs/outputs and variables are represented.

    `inputs` and `outputs` can be:
      * 'variables': they are variables of the same name in the source
      * 'calls': they are calls to self.get_input, self.set_output, ...
      * a dict mapping the name of the port to the symbol in the source
    """

    used_inputs = None
    unset_inputs = None
    internal_vars = None

    def __init__(self, source, inputs, outputs, skip_functions=False):
        BaseScript.__init__(self, source)
        self.inputs = inputs
        self.outputs = outputs
        # Set skip_functions=True if the script adds the functions itself
        self.skip_functions = skip_functions

    def normalize(self, input_vars, output_vars, all_vars):
        # At this point, the script has variables that might clash with other
        # symbols already in all_vars
        # If input_vars or output_vars is 'variables', this is fine and these
        # collisions are wanted; else, we need to do some renaming
        # Renaming happens in one pass so that exchanges can happen without any
        # issue

        # Sets self.inputs -- what inputs currently are in self.source
        if self.inputs == 'variables':
            self.inputs = dict((n, utf8(n)) for n in input_vars)
        #elif self.inputs == 'calls': # TODO
        elif isinstance(self.inputs, dict):
            pass
        else:
            raise ValueError("Script was constructed with unexpected 'inputs' "
                             "parameter %r" % self.inputs)

        # Sets self.outputs -- what outputs currently are in self.source
        if self.outputs == 'variables':
            self.outputs = dict((n, utf8(n)) for n in output_vars)
        #elif self.outputs == 'calls': # TODO
        elif isinstance(self.outputs, dict):
            pass
        else:
            raise ValueError("Script was constructed with unexpected "
                             "'outputs' parameter %r" % self.outputs)

        renames = {}

        # Finds collisions in internal variables
        # When renaming, we also need to avoid port variables, which are not
        # yet in all_vars
        port_vars = set(self.inputs.itervalues())
        port_vars.update(self.outputs.itervalues())
        self.internal_vars = set()
        for node in self.source.find_all('AssignmentNode'):
            if node.target:
                v = node.target.value
                if v in self.internal_vars:
                    continue
                print("Found internal var %s" % v)
                if v in all_vars:
                    # Make sure not to collide with ports either
                    renames[v] = nname = make_unique(v, all_vars, port_vars)
                    self.internal_vars.add(nname)
                    print("Internal var collides (%s -> %s)" % (v, nname))
                else:
                    all_vars.add(v)
                    self.internal_vars.add(v)

        # We might have renamed an input or output port -- update mappings
        for port, var in list(self.inputs.iteritems()):
            if var in renames:
                self.inputs[port] = renames[var]
                # If there is an output with the same name, update that too
                if renames[var] in self.outputs.values():
                    self.outputs[port] = renames[var]
        for port, var in list(self.outputs.iteritems()):
            if var in renames:
                self.outputs[port] = renames[var]

        inputs_back = dict((var, port)
                           for port, var in self.inputs.iteritems())
        for port, var in list(self.outputs.iteritems()):
            if var in all_vars and var not in self.internal_vars:
                self.outputs[port] = renames[var] = make_unique(var, all_vars)
                print("Output port %s collides (%s -> %s)" % (port, var,
                                                              renames[var]))
            else:
                all_vars.add(var)

        # No need to find collisions in input port names: these variables are
        # temporary and will all get set via set_input() before generation

        # Fills in used_inputs
        self.used_inputs = set()
        for node in self.source.find_all('NameNode'):
            v = node.value
            if v in inputs_back:
                self.used_inputs.add(inputs_back[v])
        self.unset_inputs = set(self.inputs.iterkeys())

        self.rename(renames)

    def set_input(self, port, varname):
        if self.inputs[port] in self.outputs.values():
            # it is used as output as well so update the output name
            inverse_output = dict([(v, k) for k, v in self.outputs.iteritems()])
            self.set_output(inverse_output[self.inputs[port]], varname)
        self.rename({self.inputs[port]: varname})
        self.inputs[port] = varname
        self.unset_inputs.discard(port)

    def set_output(self, port, varname):
        self.rename({self.outputs[port]: varname})
        self.outputs[port] = varname

    def get_output(self, port):
        return self.outputs[port]

    def __repr__(self):
        return "Script('''\n%s\n''',\ninputs: %r,\noutputs: %r\n)" % (
                self.source.dumps(),
                self.inputs, self.outputs)

from __future__ import division, unicode_literals

import io
import redbaron

from vistrails.core import debug
from vistrails.core.modules.module_registry import get_module_registry


def gen_unique_vars(names):
    d = {}
    for n in names:
        gen_unique_vars.count += 1
        d[n] = '%s_INTERNAL_YOU_WONT_SEE_THIS_%d' % (n, gen_unique_vars.count)
    return d
gen_unique_vars.count = 0


def gen_unique_var(name):
    gen_unique_vars.count += 1
    return '%s_INTERNAL_YOU_WONT_SEE_THIS_%d' % (name, gen_unique_vars.count)


def is_generated_var(name):
    return '_INTERNAL_YOU_WONT_SEE_THIS_' in name


def make_unique(name, all_vars, more_vars=set()):
    i = 1
    n = name
    while n in all_vars or n in more_vars:
        i += 1
        n = '%s_%d' % (name, i)
    all_vars.add(n)
    return n


def utf8(s):
    if isinstance(s, unicode):
        return s
    elif isinstance(s, str):
        return s.decode('utf-8')
    else:
        raise TypeError("Got %r instead of str or unicode" % type(s))


def write_workflow_to_python(pipeline, filename):
    """Writes a pipeline to a Python source file.
    """
    # The set of all currently bound symbols in the resulting script's global
    # scope
    # These are either variables from translated modules (internal or output
    # ports) or imported names
    all_vars = set()

    # The parts of the final generated script
    text = []

    # The modules that have been translated, maps from the module's id to a
    # Script object
    modules = dict()

    # The preludes that have been collected
    # A "prelude" is a piece of code that is supposed to go at the top of the
    # file, and that shouldn't be repeated; things like import statements,
    # function/class definition, and constants
    preludes = []

    reg = get_module_registry()

    # ########################################
    # Walk through the pipeline to get all the codes
    #
    for module_id in pipeline.graph.vertices_topological_sort():
        module = pipeline.modules[module_id]
        print("Processing module %s %d" % (module.name, module_id))

        desc = module.module_descriptor
        module_class = desc.module

        # Gets the code
        code_preludes = []
        if not hasattr(module_class, 'to_python_script'):
            debug.critical("Module %s cannot be converted to Python")
            code = ("# <Missing code>\n"
                    "# %s doesn't define a function to_python_script()\n"
                    "# VisTrails cannot currently export such modules\n" %
                    module.name)
            input_ports = output_ports = set()
            input_vars = output_vars = dict()
        else:
            # We generate unique names for inputs and outputs
            input_ports = set(p[1] for p in reg.module_ports('input', desc))
            input_ports.update(module.input_port_specs)
            input_vars = gen_unique_vars(utf8(p.name) for p in input_ports)
            output_ports = set(p[1] for p in reg.module_ports('output', desc))
            output_ports.update(module.output_port_specs)
            output_vars = gen_unique_vars(utf8(p.name) for p in output_ports)
            # Call the module to get the base code
            code = module_class.to_python_script(module,
                                                 input_vars, output_vars)
            if isinstance(code, tuple):
                code, code_preludes = code
            print("Got code:\n%r" % (code,))

        modules[module_id] = code
        preludes.extend(code_preludes)

    # ########################################
    # Processes the preludes and writes the beginning of the file
    #
    print("Writing preludes")
    # TODO : remove duplicated import statements
    # Adds all imported modules to the list of symbols
    for prelude in preludes:
        all_vars.update(prelude.imported_pkgs)
    # Removes collisions
    prelude_renames = {}
    for prelude in preludes:
        prelude_renames.update(prelude.avoid_collisions(all_vars))
    # Writes the preludes
    for prelude in preludes:
        text.append('# Prelude')
        text.append(unicode(prelude))
        text.append('')

    # ########################################
    # Walk through the pipeline a second time to generate the full script
    #
    for module_id in pipeline.graph.vertices_topological_sort():
        module = pipeline.modules[module_id]
        print("Writing module %s %d" % (module.name, module_id))

        # Annotation, used to rebuild the pipeline
        text.append("# MODULE name=%r, id=%s" % (module.name, module_id))

        code = modules[module_id]

        # Changes symbol names in this piece of code to prevent collisions
        # with already-encountered code
        old_all_vars = set(all_vars)
        if isinstance(code, basestring):
            code = Script(utf8(code), inputs={}, outputs={})
        else:
            code.normalize(input_vars, output_vars, all_vars)
        # Now, code knows what its inputs and outputs are
        print("Normalized code:\n%r" % (code,))
        print("New vars in all_vars: %r" % (all_vars - old_all_vars,))
        print("used_inputs: %r" % (code.used_inputs,))

        # Adds functions
        for function in pipeline.modules[module_id].functions:
            port = utf8(function.name)
            if port not in code.used_inputs:
                print("NOT adding function %s (not used in script)" % port)
                continue

            # Creates a variable with the value
            name = make_unique(port, all_vars)
            if len(function.params) == 1:
                value = function.params[0].value()
            else:
                value = [repr(p.value()) for p in function.params]
            print("Function %s: var %s, value %r" % (port,
                                                     name, value))
            text.append("# FUNCTION %s %s" % (port, name))
            text.append('%s = %r' % (name, value))
            # Tells the code what that variable is
            code.set_input(port, name)

        # Sets input connections
        for _, conn_id in pipeline.graph.edges_to(module_id):
            conn = pipeline.connections[conn_id]
            dst = conn.destination
            if utf8(dst.name) not in code.used_inputs:
                print("NOT connecting port %s (not used in script)" % dst.name)
                continue
            src = conn.source

            # Tells the code what the variable was
            src_mod = modules[src.moduleId]
            name = src_mod.get_output(utf8(src.name))
            print("Input %s: var %s" % (utf8(dst.name), name))
            text.append("# CONNECTION %s %s" % (dst.name, name))
            code.set_input(utf8(dst.name), name)

        # Sets default values
        if code.unset_inputs:
            print("unset_inputs: %r" % (code.unset_inputs,))
            iports = dict((p.name, p) for p in input_ports)
            for port in set(code.unset_inputs):
                if port not in code.used_inputs:
                    continue
                # Creates a variable with the value
                name = make_unique(port, all_vars)
                default = iports[port].defaults
                if len(default) == 1:
                    default = default[0]
                print("Default: %s: var %s, value %r" % (
                      port, name, default))
                text.append("# DEFAULT %s %s" % (port, name))
                text.append('%s = %r' % (name, default))
                code.set_input(port, name)

        # Ok, add the module's code
        print("Rendering code")
        text.append(unicode(code))
        print("Total new vars: %r" % (all_vars - old_all_vars,))

    print("Writing to file")
    f = io.open(filename, 'w', encoding='utf-8')
    f.write('\n'.join(text))
    f.write('\n')
    f.close()


class BaseScript(object):
    def __init__(self, source):
        if isinstance(source, redbaron.RedBaron):
            self.source = source
        else:
            self.source = redbaron.RedBaron(utf8(source))
        # Removes empty lines
        while self.source and self.source[0].Endl:
            del self.source[0]
        while self.source and self.source[-1].Endl:
            del self.source[-1]

    def rename(self, renames):
        counts = {}
        for node in self.source.find_all('NameNode'):
            v = node.value
            if v in renames:
                node.value = renames[v]
                counts[v] = counts.get(v, 0) + 1
        if not counts:
            print("rename():\n    no renames")
        else:
            print("rename():")
            for v, c in counts.iteritems():
                print("    %s: %d" % (v, c))

    def __unicode__(self):
        return self.source.dumps()


class Prelude(BaseScript):
    """A piece of code that should be inserted at the beginning.
    """
    # Defined variables are the symbols that are created by this prelude code
    # The scripts that use this prelude will want to use these
    # We rename them if they clash with other preludes; in that case we rename
    # in the same way in each script that use the prelude
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
            if assign.target.NameNode:
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

    This holds a piece of code plus information on how the inputs/outputs
    and variables are represented.

    `inputs` and `outputs` can be:
      * 'variables': they are variables of the same name in the source
      * 'calls': they are calls to self.get_input, self.set_output, ...
      * a dict mapping the name of the port to the symbol in the source
    """

    used_inputs = None
    unset_inputs = None
    internal_vars = None

    def __init__(self, source, inputs, outputs):
        BaseScript.__init__(self, source)
        self.inputs = inputs
        self.outputs = outputs

    def normalize(self, input_vars, output_vars, all_vars):
        # At this point, the script has variables that might clash with other
        # symbols already in all_vars
        # If input_vars or output_vars is 'variables', this is fine and these
        # collisions are wanted; else, we need to do some renaming
        # Renaming happens in one pass so that exchanges can happen without any
        # issue

        # Sets self.inputs -- what inputs currently are in self.source
        if self.inputs == 'variables':
            self.inputs = dict((n, n) for n in input_vars.iterkeys())
        #elif self.inputs == 'calls': # TODO
        elif isinstance(self.inputs, dict):
            pass
        else:
            raise ValueError("Script was constructed with unexpected 'inputs' "
                             "parameter %r" % self.inputs)

        # Sets self.outputs -- what outputs currently are in self.source
        if self.outputs == 'variables':
            self.outputs = dict((n, n) for n in output_vars.iterkeys())
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
            if node.target.NameNode:
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
        for port, var in list(self.outputs.iteritems()):
            if var in renames:
                self.outputs[port] = renames[var]

        inputs_back = dict((var, port)
                           for port, var in self.inputs.iteritems())
        for port, var in list(self.outputs.iteritems()):
            # Renames output variables if they were autogenerated
            if is_generated_var(var):
                self.outputs[port] = nname = make_unique(var, all_vars)
                renames[var] = nname
                print("Variable for output port %s autogenerated "
                      "(%s -> %s)" % (port, var, nname))
                # If it collides with input variable, rename that instead
                if nname in inputs_back:
                    iport = inputs_back[nname]
                    self.inputs[iport] = var = gen_unique_var(iport)
                    del inputs_back[nname]
                    inputs_back[var] = iport
                    print("New output name collides with input port %s "
                          "(%s -> %s)" % (iport, nname, var))
            elif var in all_vars and var not in self.internal_vars:
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
        self.rename({self.inputs[port]: varname})
        self.inputs[port] = varname
        self.unset_inputs.discard(port)

    def get_output(self, port):
        return self.outputs[port]

    def __repr__(self):
        return "Script('''\n%s\n''',\ninputs: %r,\noutputs: %r\n)" % (
                self.source.dumps(),
                self.inputs, self.outputs)

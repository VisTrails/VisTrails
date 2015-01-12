"""Pipeline to Python exporting logic.

This contains write_workflow_to_python(), which exports a VisTrails pipeline as
a standalone Python script.
"""

from __future__ import division, unicode_literals

import io

from vistrails.core import debug
from vistrails.core.modules.module_registry import get_module_registry
from vistrails.core.scripting.scripts import make_unique, Script
from vistrails.core.scripting.utils import utf8


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
    preludes = set()

    reg = get_module_registry()

    # ########################################
    # Walk through the pipeline to get all the codes
    #
    for module_id in pipeline.graph.vertices_topological_sort():
        module = pipeline.modules[module_id]
        print("Processing module %s %d" % (module.name, module_id))

        module_class = module.module_descriptor.module

        # Gets the code
        code_preludes = []
        if (not hasattr(module_class, 'to_python_script') or
                module_class.to_python_script is None):
            debug.critical("Module %s cannot be converted to Python")
            code = ("# <Missing code>\n"
                    "# %s doesn't define a function to_python_script()\n"
                    "# VisTrails cannot currently export such modules\n" %
                    module.name)
        else:
            # Call the module to get the base code
            code = module_class.to_python_script(module)
            if isinstance(code, tuple):
                code, code_preludes = code
            print("Got code:\n%r" % (code,))
            assert isinstance(code, Script)

        modules[module_id] = code
        preludes.update(code_preludes)

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
        desc = module.module_descriptor
        print("Writing module %s %d" % (module.name, module_id))

        # Annotation, used to rebuild the pipeline
        text.append("# MODULE name=%r, id=%s" % (module.name, module_id))

        code = modules[module_id]

        # Gets all the module's input and output port names
        input_ports = set(p[1] for p in reg.module_ports('input', desc))
        input_ports.update(module.input_port_specs)
        input_port_names = set(p.name for p in input_ports)
        output_ports = set(p[1] for p in reg.module_ports('output', desc))
        output_ports.update(module.output_port_specs)
        output_port_names = set(p.name for p in output_ports)

        # Changes symbol names in this piece of code to prevent collisions
        # with already-encountered code
        old_all_vars = set(all_vars)
        code.normalize(input_port_names, output_port_names, all_vars)
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

from __future__ import division

import io
from redbaron import RedBaron

from vistrails.core import debug
from vistrails.core.modules.module_registry import get_module_registry


def gen_unique_vars(names):
    d = {}
    for n in names:
        d[n] = '%s_INTERNAL_YOU_WONT_SEE_THIS_%d' % (n, gen_unique_vars.count)
        gen_unique_vars.count += 1
    return d
gen_unique_vars.count = 0


def make_unique(name, all_vars):
    i = 1
    n = name
    while n in all_vars:
        i += 1
        n = '%s_%d' % (name, i)
    all_vars.add(n)
    return n


def write_workflow_to_python(pipeline, filename):
    """Writes a pipeline to a Python source file.
    """
    text = []
    all_vars = set()
    modules = dict()

    reg = get_module_registry()

    # Walk through the pipeline
    for module_id in pipeline.graph.vertices_topological_sort():
        module = pipeline.modules[module_id]

        # Annotation, used to rebuild the pipeline
        text += "# MODULE name=%r, id=%s\n" % (module.name, module_id)

        desc = module.module_descriptor
        module_class = desc.module

        # Gets the code
        if not hasattr(module_class, 'to_python_script'):
            debug.critical("Module %s cannot be converted to Python")
            code = ("# <Missing code>\n"
                    "# %s doesn't define a function to_python_script()\n"
                    "# VisTrails cannot currently export such modules\n")
        else:
            # We generate unique names for inputs and outputs
            input_ports = reg.module_ports('input', desc)
            input_vars = gen_unique_vars(p[0] for p in input_ports)
            output_ports = reg.module_ports('output', desc)
            output_vars = gen_unique_vars(p[0] for p in output_ports)

            # Call the module to get the base code
            code = module_class.to_python_script(module,
                                                 input_vars, output_vars)

        if isinstance(code, basestring):
            code = Script(code, inputs={}, outputs={})
        else:
            code.normalize(input_vars, output_vars, all_vars)
        # Now, code knows what its inputs and outputs are

        # Adds functions
        for function in pipeline.modules[module_id].functions:
            if function.name not in code.used_inputs:
                continue

            # Creates a variable with the value
            name = make_unique(function.name, all_vars)
            text.append('%s = %r' % (name, function.params))
            # Tells the code what that variable is
            code.set_input(function.name, name)

        # Sets input connections
        for _, conn_id in pipeline.graph.edges_to(module_id):
            conn = pipeline.connections[conn_id]
            dst = conn.destination
            if dst.name not in code.used_inputs:
                continue
            src = conn.source

            # Tells the code what the variable was
            src_mod = modules[src.moduleId]
            code.set_input(dst.name, src_mod.get_output(src.name))

        # Sets default values
        unset_inputs = code.unset_inputs()
        if unset_inputs:
            iports = dict(input_ports)
            for port in unset_inputs:
                # Creates a variable with the value
                name = make_unique(port, all_vars)
                text.append('%s = %r' % (name, iports[port].defaults))
                code.set_input(port, name)

        # Ok, add the module's code
        text.append(unicode(code))

        # Stores this for connections to downstream modules
        modules[module_id] = code

    f = io.open(filename, 'w', encoding='utf-8')
    f.write(u'\n'.join(text))
    f.close()


class Script(object):
    """Wrapper for a piece of Python script.

    This holds a piece of code plus information on how the inputs/outputs
    and variables are represented.

    `inputs` and `outputs` can be:
      * 'variables': they are variables of the same name in the source
      * 'calls': they are calls to self.get_input, self.set_output, ...
      * a dict mapping the name of the port to the symbol in the source
    """

    used_inputs = None

    def __init__(self, source, inputs, outputs):
        self.source = RedBaron(source)
        self.inputs = inputs
        self.outputs = outputs

    def normalize(self, input_vars, output_vars, all_vars):
        pass

    def set_input(self, port, varname):
        pass # TODO

    def get_output(self, port):
        pass # TODO

    def __unicode__(self):
        return "code" # TODO

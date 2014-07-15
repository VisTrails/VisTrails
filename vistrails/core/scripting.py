from __future__ import division

from redbaron import RedBaron

from vistrails.core import debug
from vistrails.core.modules.basic_modules import PythonSource


def write_workflow_to_python(pipeline, filename):
    """Writes a pipeline to a Python source file.
    """
    text = ""

    # Walk through the pipeline
    for module_id in pipeline.graph.vertices_topological_sort():
        module = pipeline.modules[module_id]

        # Annotation, used to rebuild the pipeline
        text += "# MODULE name=%r, id=%s\n" % (module.name, module_id)

        module_class = module.module_descriptor.module

        # Gets the code
        if not hasattr(module_class, 'to_python_script'):
            debug.critical("Module %s cannot be converted to Python")
            code = ("# <Missing code>\n"
                    "# %s doesn't define a function to_python_script()\n"
                    "# VisTrails cannot currently export such modules\n")
        else:
            code = module_class.to_python_script(module)

        # Adds functions
        for function in pipeline.modules[module_id].functions:
            # skip pythonsource src ports
            if issubclass(module_class,
                          PythonSource) and function.name == 'source':
                continue
            value = [repr(param.value()) for param in function.params]
            if len(function.params) == 1:
                value = value[0]
            else:
                value = tuple(value)
            text += "%s = %s" % (function.name, value) + '\n'
        # set input connections
        for _, conn_id in pipeline.graph.edges_to(module_id):
            conn = pipeline.connections[conn_id]
            src = conn.source
            dst = conn.destination
            srcName = "%s%s" % (src.name, src.moduleId)
            text += "%s = %s" % (dst.name, srcName) + '\n'
        # compute
        if not hasattr(module_class, "to_python_script"):
            debug.critical("%s cannot be exported to Python" % module.name)
        text += module_class.to_python_script(module) + '\n'
        # set output connections
        # appends module id to port name to make it unique
        for _, conn_id in pipeline.graph.edges_from(module_id):
            conn = pipeline.connections[conn_id]
            src = conn.source
            srcName = "%s%s" % (src.name, src.moduleId)
            text += "%s = %s" % (srcName, src.name) + '\n'
    f = open(filename, 'w')
    f.write(text)
    f.close()


class Script(object):
    """Wrapper for a piece of Python script.

    This holds a piece of code plus information on how the inputs/outputs
    and variables are represented.

    `inputs` and `outputs` can be:
      * 'variables': they are variables of the same name in the source
      * a dict mapping the name of the port to the symbol in the source
    """

    def __init__(self, source, inputs, outputs):
        self.source = RedBaron(source)
        self.inputs = inputs
        self.outputs = outputs

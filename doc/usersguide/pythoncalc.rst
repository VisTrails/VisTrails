.. % NB: Please don't break any of the long lines - Verbatim is picky about line breaks

.. index::
   pair: Module registry; ``addModule``
   pair: packages; ``initialize``
   pair: Module registry; ``addInputPort``
   pair: Module registry; ``addOutputPort``
   pair: modules; ``ModuleError``

.. role:: red

.. code-block:: python
   :linenos:

   import core.modules.module_registry
   from core.modules.vistrails_module import Module, ModuleError

   version = "0.9.0"
   name = "PythonCalc"
   identifier = "edu.utah.sci.vistrails.pythoncalc"

   class PythonCalc(Module):
       """PythonCalc is a module that performs simple arithmetic operations on its inputs."""

       def compute(self):
           v1 = self.getInputFromPort("value1")
           v2 = self.getInputFromPort("value2")
           result = self.op(v1, v2)
           self.setResult("value", result)

       def op(self, v1, v2):
           op = self.getInputFromPort("op")
           if op == '+': return v1 + v2
           elif op == '-': return v1 - v2
           elif op == '*': return v1 * v2
           elif op == '/': return v1 / v2
           else: raise ModuleError(self, "unrecognized operation: '%s'" % op)

   ###############################################################################

   def initialize(*args, **keywords):

       # We'll first create a local alias for the module registry so that
       # we can refer to it in a shorter way.
       reg = core.modules.module_registry.registry

       reg.add_module(PythonCalc)
       reg.add_input_port(PythonCalc, "value1", 
                          (core.modules.basic_modules.Float, 'the first argument'))
       reg.add_input_port(PythonCalc, "value2",
                          (core.modules.basic_modules.Float, 'the second argument'))
       reg.add_input_port(PythonCalc, "op",
                          (core.modules.basic_modules.String, 'the operation'))
       reg.add_output_port(PythonCalc, "value",
                          (core.modules.basic_modules.Float, 'the result'))


.. .. parsed-literal::

   import core.modules.module_registry
   from core.modules.vistrails_module import Module, ModuleError

   :red:`version = "0.9.0"`
   :red:`name = "PythonCalc"`
   :red:`identifier = "edu.utah.sci.vistrails.pythoncalc"`

   .. _package-defineclass:

   class :red:`PythonCalc`\ (:red:`Module`)
       """PythonCalc is a module that performs simple arithmetic operations on its inputs."""

   .. _package-compute:
       :red:`def compute(self):`
   .. _package-getinputfromport:
           v1 = :red:`self.getInputFromPort("value1")`
           v2 = :red:`self.getInputFromPort("value2")`
           result = self.op(v1, v2)
   .. _package-setresult:
           :red:`self.setResult("value", result)`

   .. _package-extramethods:
       :red:`def op(self, v1, v2):`
           op = self.getInputFromPort("op")
           if op == '+': return v1 + v2
           elif op == '-': return v1 - v2
           elif op == '*': return v1 * v2
           elif op == '/': return v1 / v2
   .. _package-moduleerrror:
           else: raise :red:`ModuleError(self, "unrecognized operation: '%s'" % op)`

   ###############################################################################

   .. _package-initialize:
   :red:`def initialize(*args, **keywords):`

       # We'll first create a local alias for the module registry so that
       # we can refer to it in a shorter way.
       reg = core.modules.module_registry.registry

   .. _package-addmodule:
       :red:`reg.add_module(PythonCalc)`
   .. _package-addinputport:
       reg.\ :red:`add_input_port`\ (PythonCalc, "value1", 
   .. _package-float:
                        (:red:`core.modules.basic_modules.Float`, 'the first argument'))
       reg.add_input_port(PythonCalc, "value2",
                        (core.modules.basic_modules.Float, 'the second argument'))
       reg.add_input_port(PythonCalc, "op",
                        (core.modules.basic_modules.String, 'the operation'))
   .. _package-addoutputport:
       reg.\ :red:`add_output_port`\ (PythonCalc, "value",
                         (core.modules.basic_modules.Float, 'the result'))



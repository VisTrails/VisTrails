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

.. .. code-block:: python
   :linenos:

   ############################################################################
   ##
   ## Copyright (C) 2006-2007 University of Utah. All rights reserved.
   ##
   ## This file is part of VisTrails.
   ##
   ## This file may be used under the terms of the GNU General Public
   ## License version 2.0 as published by the Free Software Foundation
   ## and appearing in the file LICENSE.GPL included in the packaging of
   ## this file.  Please review the following to ensure GNU General Public
   ## Licensing requirements will be met:
   ## http://www.opensource.org/licenses/gpl-license.php
   ##
   ## If you are unsure which license is appropriate for your use (for
   ## instance, you are interested in developing a commercial derivative
   ## of VisTrails), please contact us at vistrails@sci.utah.edu.
   ##
   ## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
   ## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
   ##
   ############################################################################
   """This package implements a very simple VisTrails module called
   PythonCalc. This is intended as a simple example that can be referred
   to by users to create their own packages and modules later.

   If you're interested in developing new modules for VisTrails, you
   should also consult the documentation in
   core/modules/vistrails_module.py.
   """

   import core.modules
   import core.modules.module_registry
   from core.modules.vistrails_module import Module, ModuleError

   ###############################################################################
   # PythonCalc
   #
   # A VisTrails package is simply a Python class that subclasses from
   # Module.  For this class to be executable, it must define a method
   # compute(self) that will perform the appropriate computations and set
   # the results.
   #
   # Extra helper methods can be defined, as usual. In this case, we're
   # using a helper method op(self, v1, v2) that performs the right
   # operations.

   class PythonCalc(Module):
       """PythonCalc is a module that performs simple arithmetic operations
       on its inputs."""

       # This constructor is strictly unnecessary. However, some modules
       # might want to initialize per-object data. When implementing your
       # own constructor, remember that it must not take any extra
       # parameters.
       def __init__(self):
           Module.__init__(self)

       # This is the method you should implement in every module that
       # will be executed directly. VisTrails does not use the return
       # value of this method.
       def compute(self):
           # getInputFromPort is a method defined in Module that returns
           # the value stored at an input port. If there's no value
           # stored on the port, the method will return None.
           v1 = self.getInputFromPort("value1")
           v2 = self.getInputFromPort("value2")

           # You should call setResult to store the appropriate results
           # on the ports.  In this case, we are only storing a
           # floating-point result, so we can use the number types
           # directly. For more complicated data, you should
           # return an instance of a VisTrails Module. This will be made
           # clear in further examples that use these more complicated data.
           self.setResult("value", self.op(v1, v2))

       def op(self, v1, v2):
           op = self.getInputFromPort("op")
           if op == '+':
               return v1 + v2
           elif op == '-':
               return v1 - v2
           elif op == '*':
               return v1 * v2
           elif op == '/':
               return v1 / v2
           # If a module wants to report an error to VisTrails, it should raise
           # ModuleError with a descriptive error. This allows the interpreter
           # to capture the error and report it to the caller of the evaluation
           # function.
           raise ModuleError(self, "unrecognized operation: '%s'" % op)

   ###############################################################################
   # the function initialize is called for each package, after all
   # packages have been loaded. It it used to register the module with
   # the VisTrails runtime.

   def initialize(*args, **keywords):

       # We'll first create a local alias for the module_registry so that
       # we can refer to it in a shorter way.
       reg = core.modules.module_registry

       # VisTrails cannot currently automatically detect your derived
       # classes, and the ports that they support as input and
       # output. Because of this, you as a module developer need to let
       # VisTrails know that you created a new module. This is done by calling
       # function addModule:
       reg.addModule(PythonCalc)

       # In a similar way, you need to report the ports the module wants
       # to make available. This is done by calling addInputPort and
       # addOutputPort appropriately. These calls only show how to set up
       # one-parameter ports. We'll see in later tutorials how to set up
       # multiple-parameter plots.
       reg.addInputPort(PythonCalc, "value1",
                        (core.modules.basic_modules.Float, 'the first argument'))
       reg.addInputPort(PythonCalc, "value2",
                        (core.modules.basic_modules.Float, 'the second argument'))
       reg.addInputPort(PythonCalc, "op",
                        (core.modules.basic_modules.String, 'the operation'))
       reg.addOutputPort(PythonCalc, "value",
                         (core.modules.basic_modules.Float, 'the result'))
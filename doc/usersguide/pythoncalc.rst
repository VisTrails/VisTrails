.. % NB: Please don't break any of the long lines - Verbatim is picky about line breaks

.. index::
   pair: packages; ``_modules``
   pair: modules; ``_input_ports``
   pair: modules; ``_output_ports``
   pair: modules; ``ModuleError``

.. role:: red

.. code-block:: python
    :linenos:

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

    from vistrails.core.modules.vistrails_module import Module, ModuleError
    from vistrails.core.modules.config import IPort, OPort

    class PythonCalc(Module):
        """PythonCalc is a module that performs simple arithmetic operations
    on its inputs."""

        # You need to report the ports the module wants to make
        # available. This is done by creating _input_ports and
        # _output_ports lists composed of InputPort (IPort) and OutputPort
        # (OPort) objects. These are simple ports that take only one
        # value. We'll see in later tutorials how to create compound ports
        # which can take a tuple of values.  Each port must specify its
        # name and signature.  The signature specifies the package
        # (e.g. "basic" which is shorthand for
        # "org.vistrails.vistrails.basic") and module (e.g. "Float").
        # Note that the third input port (op) has two other arguments.
        # The "enum" entry_type specifies that there are a set of options
        # the user should choose from, and the values then specifies those
        # options.
        _input_ports = [IPort(name="value1", signature="basic:Float"),
                        IPort(name="value2", signature="basic:Float"),
                        IPort(name="op", signature="basic:String",
                              entry_type="enum", values=["+", "-", "*", "/"])]
        _output_ports = [OPort(name="value", signature="basic:Float")]

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

    # VisTrails will only load the modules specified in the _modules list.
    # This list contains all of the modules a package defines.
    _modules = [PythonCalc,]

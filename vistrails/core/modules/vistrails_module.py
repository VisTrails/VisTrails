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
class NeedsInputPort(Exception):
    def __init__(self, obj, port):
        self.obj = obj
        self.port = port
    def __str__(self):
        return "Module %s needs port %s" % (self.obj, self.port)


class IncompleteImplementation(Exception):
    def __str__(self):
        return "Module has incomplete implementation"


class MissingModule(Exception):
    pass


class ModuleError(Exception):

    """Exception representing a VisTrails module runtime error. This
exception is recognized by the interpreter and allows meaningful error
reporting to the user and to the logging mechanism."""
    
    def __init__(self, module, errormsg):
        """ModuleError should be passed the module that signaled the
error and the error message as a string."""
        Exception.__init__(self, errormsg)
        self.module = module
        self.msg = errormsg

################################################################################

class Module(object):

    """Module is the base module from which all module functionality
is derived from in VisTrails. It defines a set of basic interfaces to
deal with data input/output (through ports, as will be explained
later), as well as a basic mechanism for dataflow based updates.

Execution Model

  VisTrails assumes fundamentally that a pipeline is a dataflow. This
  means that pipeline cycles are disallowed, and that modules are
  supposed to be free of side-effects. This is obviously not possible
  in general, particularly for modules whose sole purpose is to
  interact with operating system resources. In these cases, designing
  a module is harder -- the side effects should ideally not be exposed
  to the module interface.  VisTrails provides some support for making
  this easier, as will be discussed later.

  VisTrails caches intermediate results to increase efficiency in
  exploration. It does so by reusing pieces of pipelines in later
  executions.
  
Terminology

  Module Interface: The module interface is the set of input and
  output ports a module exposes.

Designing New Modules

  Designing new modules is essentially a matter of subclassing this
  module class and overriding the compute() method. There is a
  fully-documented example of this on the default package
  'pythonCalc', available on the 'packages/pythonCalc' directory.

  Caching

    Caching affects the design of a new module. Most importantly,
    users have to account for compute() being called more than
    once. Even though compute() is only called once per individual
    execution, new connections might mean that previously uncomputed
    output must be made available.

    Also, operating system side-effects must be carefully accounted
    for. Some operations are fundamentally side-effectful (creating OS
    output like uploading a file on the WWW or writing a file to a
    local hard drive). These modules should probably not be cached at
    all. VisTrails provides an easy way for modules to report that
    they should not be cached: simply subclass from the NotCacheable
    mixin provided in this python module. (NB: In order for the mixin
    to work appropriately, NotCacheable must appear *BEFORE* any other
    subclass in the class hierarchy declarations). These modules (and
    anything that depends on their results) will then never be reused.


  Intermediate Files

    Many modules communicate through intermediate files. VisTrails
    provides automatic filename and handle management to alleviate the
    burden of determining tricky things (e.g. longevity) of these
    files. Modules can request temporary file names through the file pool,
    currently accessible through

    self.interpreter.filePool

    The FilePool class is available in core/modules/module_utils.py -
    consult its documentation for usage. Notably, using the file pool
    will make temporary files work correctly with caching, and will
    make sure the temporaries are correctly removed.



"""

    def __init__(self):
        self.inputPorts = {}
        self.outputPorts = {}
        self.outputRequestTable = {}
        self.upToDate = False
        self.setResult("self", self) # every object can return itself

    def clear(self):
        """clear(self) -> None. Removes all references, prepares for
deletion."""
        for connector_list in self.inputPorts.itervalues():
            for connector in connector_list:
                print type(connector)
                connector.clear()
        self.inputPorts = {}
        self.outputPorts = {}
        self.outputRequestTable = {}
        if hasattr(self, "logging"):
            del self.logging

    def is_cacheable(self):
        """is_cacheable() -> bool. A Module should return whether it
can be reused across executions. It is safe for a Module to return
different values in different occasions. In other words, it is
possible for modules to be cacheable depending on their execution
context."""
        return True

    def update(self):
        if self.upToDate:
            return
        if not hasattr(self, "logging"):
            for connectorList in self.inputPorts.itervalues():
                for connector in connectorList:
                    connector.obj.update()
            self.compute()
            self.upToDate = True
        else:
            # Updates upstream modules
            self.logging.beginUpdate(self)
            for connectorList in self.inputPorts.itervalues():
                for connector in connectorList:
                    connector.obj.update()
            self.logging.beginCompute(self)
            self.compute()
            self.upToDate = True
            self.logging.endUpdate(self)
            self.logging.signalSuccess(self)

    def checkInputPort(self, name):
        """checkInputPort(name) -> None.
Makes sure input port 'name' is filled."""
        if not self.hasInputFromPort(name):
            raise ModuleError(self, "'%s' is a mandatory port" % name)

    def compute(self):
        pass

    def addRequestPort(self, port, f):
        self.outputRequestTable[port] = f

    def requestOutputFromPort(self, port):
        if not self.outputRequestTable.has_key(port):
            raise ModuleError(("On-demand request port %s not present in table" %
                               port))
        else:
            v = self.outputRequestTable[port]()
            return v

    def setResult(self, port, value):
        self.outputPorts[port] = value

    def getOutput(self, port):
        if self.outputPorts.has_key(port) or not self.outputPorts[port]:
            return self.outputPorts[port]
        return self.requestOutputFromPort(port)

    def getInputFromPort(self, inputPort):
        if not self.inputPorts.has_key(inputPort):
            raise ModuleError(self, "Missing value from port %s" % inputPort)
        return self.inputPorts[inputPort][0]()

    def hasInputFromPort(self, inputPort):
        return self.inputPorts.has_key(inputPort)

    def __str__(self):
        return "<<%s>>" % str(self.__class__)

    def annotate(self, d):
        self.logging.annotate(self, d)

    def forceGetInputFromPort(self, inputPort, defaultValue=None):
        if self.hasInputFromPort(inputPort):
            return self.getInputFromPort(inputPort)
        else:
            return defaultValue

    def setInputPort(self, inputPort, conn):
        if self.inputPorts.has_key(inputPort):
            self.inputPorts[inputPort].append(conn)
        else:
            self.inputPorts[inputPort] = [conn]

    def getInputListFromPort(self, inputPort):
        if not self.inputPorts.has_key(inputPort):
            raise ModuleError(self, "Missing value from port %s" % inputPort)
        return [connector() for connector in self.inputPorts[inputPort]]

    def forceGetInputListFromPort(self, inputPort):
        if not self.inputPorts.has_key(inputPort):
            return []
        return [connector() for connector in self.inputPorts[inputPort]]

    ### Set an output port before hand that it is neccesary for the computation
    def enableOutputPort(self, outputPort):
        # Don't reset existing values, it screws up the caching.
        if not self.outputPorts.has_key(outputPort):
            self.setResult(outputPort, None)


################################################################################

class NotCacheable(object):

    def is_cacheable(self):
        return False

################################################################################

class ModuleConnector(object):
    
    def __init__(self, obj, port):
        self.obj = obj
        self.port = port

    def clear(self):
        """clear() -> None. Removes references, prepares for deletion."""
        self.obj = None
        self.port = None
    
    def __call__(self):
        return self.obj.getOutput(self.port)

def newModule(baseModule, name, dict={}):
    assert issubclass(baseModule, Module)
    return type(name, (baseModule, ), dict)

# This is the gist of how type() works. The example is run from a python
# toplevel

# >>> class X(object):
# ...     def f(self): return 3
# ... 
# >>> a = X()
# >>> a.f()
# 3
# >>> Y = type('Y', (X, ), {'g': lambda x : 4})
# >>> b = Y()
# >>> b.f()
# 3
# >>> b.g()
# 4
# >>> Z = type('Z', (X, ), {'f': lambda x : 4} )
# >>> c = Z()
# >>> c.f()
# 4

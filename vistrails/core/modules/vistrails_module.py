###############################################################################
##
## Copyright (C) 2006-2011, University of Utah. 
## All rights reserved.
## Contact: contact@vistrails.org
##
## This file is part of VisTrails.
##
## "Redistribution and use in source and binary forms, with or without 
## modification, are permitted provided that the following conditions are met:
##
##  - Redistributions of source code must retain the above copyright notice, 
##    this list of conditions and the following disclaimer.
##  - Redistributions in binary form must reproduce the above copyright 
##    notice, this list of conditions and the following disclaimer in the 
##    documentation and/or other materials provided with the distribution.
##  - Neither the name of the University of Utah nor the names of its 
##    contributors may be used to endorse or promote products derived from 
##    this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
## AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
## THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR 
## PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR 
## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; 
## OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
## WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR 
## OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF 
## ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
###############################################################################

import copy
from core.data_structures.bijectivedict import Bidict
from core.utils import VistrailsInternalError

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

class ModuleBreakpoint(Exception):
    def __init__(self, module):
        self.module = module
        self.msg = "Hit breakpoint"
        self.errorTrace = ''

    def __str__(self):
        retstr = "Encoutered breakpoint at Module %s:\n" % (self.module)
        for k in self.module.__dict__.keys():
            retstr += "\t%s = %s\n" % (k, self.module.__dict__[k])

        inputs = self.examine_inputs()
        retstr += "\nModule has inputs:\n"
        
        for i in inputs.keys():
            retstr += "\t%s = %s\n" % (i, inputs[i])

        return retstr

    def examine_inputs(self):
        in_ports = self.module.__dict__["inputPorts"]
        inputs = {}
        for p in in_ports:
            inputs[p] = self.module.getInputListFromPort(p)

        return inputs
        
class ModuleError(Exception):

    """Exception representing a VisTrails module runtime error. This
exception is recognized by the interpreter and allows meaningful error
reporting to the user and to the logging mechanism."""
    
    def __init__(self, module, errormsg):
        """ModuleError should be passed the module instance that signaled the
error and the error message as a string."""
        Exception.__init__(self, errormsg)
        self.module = module
        self.msg = errormsg
        import traceback
        self.errorTrace = traceback.format_exc()

class ModuleSuspended(ModuleError):

    """Exception representing a VisTrails module being suspended. Raising 
    ModuleSuspended flags that the module is not ready to finish yet and
    that the workflow should be executed later.  A suspended module does
    not execute the modules downstream but all modules upstream will be
    executed. This is useful when executing external jobs where you do not
    want to block vistrails while waiting for the execution to finish.  """
    
    def __init__(self, module, errormsg):
        ModuleError.__init__(self, module, errormsg)

class ModuleErrors(Exception):
    """Exception representing a list of VisTrails module runtime errors.
    This exception is recognized by the interpreter and allows meaningful
    error reporting to the user and to the logging mechanism."""
    def __init__(self, module_errors):
        """ModuleErrors should be passed a list of ModuleError objects"""
        Exception.__init__(self, str(tuple(me.msg for me in module_errors)))
        self.module_errors = module_errors

class _InvalidOutput(object):
    """ Specify an invalid result
    """
    pass

InvalidOutput = _InvalidOutput

################################################################################
# DummyModuleLogging

class DummyModuleLogging(object):
    def end_update(*args, **kwargs): pass
    def begin_update(*args, **kwargs): pass
    def begin_compute(*args, **kwargs): pass
    def update_cached(*args, **kwargs): pass
    def signalSuccess(*args, **kwargs): pass
    def annotate(*args, **kwargs): pass

_dummy_logging = DummyModuleLogging()

################################################################################
# Module

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
        self.upToDate = False
        self.setResult("self", self) # every object can return itself
        self.logging = _dummy_logging

        # isMethod stores whether a certain input port is a method.
        # If so, isMethod maps the port to the order in which it is
        # stored. This is so that modules that need to know about the
        # method order can work correctly
        self.is_method = Bidict()
        self._latest_method_order = 0
        
        # Pipeline info that a module should know about This is useful
        # for a spreadsheet cell to know where it is from. It will be
        # also used for talking back and forth between the spreadsheet
        # and the builder besides Parameter Exploration.
        self.moduleInfo = {
            'locator': None,
            'vistrailName': 'Unknown',
            'version': -1,
            'pipeline': None,
            'moduleId': -1,
            'reason': 'Pipeline Execution',
            'actions': []
            }

        self.is_breakpoint = False

        # is_fold_operator stores wether the module is a part of a fold
        self.is_fold_operator = False

        # is_fold_module stores whether the module is a fold module
        self.is_fold_module = False

        # computed stores wether the module was computed
        # used for the logging stuff
        self.computed = False
        
        self.suspended = False

        self.signature = None

    def clear(self):
        """clear(self) -> None. Removes all references, prepares for
deletion."""
        for connector_list in self.inputPorts.itervalues():
            for connector in connector_list:
                connector.clear()
        self.inputPorts = {}
        self.outputPorts = {}
        self.logging = _dummy_logging
        self.is_method = Bidict()
        self._latest_method_order = 0

    def is_cacheable(self):
        """is_cacheable() -> bool. A Module should return whether it
can be reused across executions. It is safe for a Module to return
different values in different occasions. In other words, it is
possible for modules to be cacheable depending on their execution
context."""
        return True

    def updateUpstreamPort(self, port):
        # update single port
        if port in self.inputPorts:
            for connector in self.inputPorts[port]:
                connector.obj.update()
                if hasattr(connector.obj, 'suspended') and \
                   connector.obj.suspended:
                    self.suspended = connector.obj.suspended
            for connector in copy.copy(self.inputPorts[port]):
                if connector.obj.get_output(connector.port) is InvalidOutput:
                    self.removeInputConnector(port, connector)

    def updateUpstream(self):
        """ updateUpstream() -> None        
        Go upstream from the current module, then update its upstream
        modules and check input connection based on upstream modules
        results
        
        """
        for connectorList in self.inputPorts.itervalues():
            for connector in connectorList:
                connector.obj.update()
                if hasattr(connector.obj, 'suspended') and \
                   connector.obj.suspended:
                    self.suspended = connector.obj.suspended
        for iport, connectorList in copy.copy(self.inputPorts.items()):
            for connector in connectorList:
                if connector.obj.get_output(connector.port) is InvalidOutput:
                    self.removeInputConnector(iport, connector)
                    
    def update(self):
        """ update() -> None        
        Check if the module is up-to-date then update the
        modules. Report to the logger if available
        
        """
        self.logging.begin_update(self)
        self.updateUpstream()
        if self.suspended:
            return
        if self.upToDate:
            if not self.computed:
                self.logging.update_cached(self)
                self.computed = True
            return
        self.logging.begin_compute(self)
        try:
            if self.is_breakpoint:
                raise ModuleBreakpoint(self)
            self.compute()
            self.computed = True
        except ModuleSuspended, e:
            self.suspended = e.msg
            self.logging.end_update(self, e.msg, was_suspended=True)
            self.logging.signalSuspended(self)
            return
        except ModuleError, me:
            if hasattr(me.module, 'interpreter'):
                raise
            else:
                msg = "A dynamic module raised an exception: '%s'"
                msg %= str(me)
                raise ModuleError(self, msg)
        except ModuleErrors:
            raise
        except KeyboardInterrupt, e:
            raise ModuleError(self, 'Interrupted by user')
        except ModuleBreakpoint:
            raise
        except Exception, e: 
            import traceback
            traceback.print_exc()
            raise ModuleError(self, 'Uncaught exception: "%s"' % str(e))
        self.upToDate = True
        self.logging.end_update(self)
        self.logging.signalSuccess(self)

    def checkInputPort(self, name):
        """checkInputPort(name) -> None.
Makes sure input port 'name' is filled."""
        if not self.hasInputFromPort(name):
            raise ModuleError(self, "'%s' is a mandatory port" % name)

    def compute(self):
        pass

    def setResult(self, port, value):
        self.outputPorts[port] = value

    def get_output(self, port):
        # if self.outputPorts.has_key(port) or not self.outputPorts[port]: 
        if port not in self.outputPorts:
            raise ModuleError(self, "output port '%s' not found" % port)
        return self.outputPorts[port]

    def getInputConnector(self, inputPort):
        if not self.inputPorts.has_key(inputPort):
            raise ModuleError(self, "Missing value from port %s" % inputPort)
        return self.inputPorts[inputPort][0]

    def getInputFromPort(self, inputPort):
        if not self.inputPorts.has_key(inputPort):
            raise ModuleError(self, "Missing value from port %s" % inputPort)
        # Cannot resolve circular reference here, need to be fixed later
        from core.modules.sub_module import InputPort
        for conn in self.inputPorts[inputPort]:
            if type(conn.obj)==InputPort:
                return conn()
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

    def set_input_port(self, inputPort, conn, is_method=False):
        if self.inputPorts.has_key(inputPort):
            self.inputPorts[inputPort].append(conn)
        else:
            self.inputPorts[inputPort] = [conn]
        if is_method:
            self.is_method[conn] = (self._latest_method_order, inputPort)
            self._latest_method_order += 1

    def getInputListFromPort(self, inputPort):
        if not self.inputPorts.has_key(inputPort):
            raise ModuleError(self, "Missing value from port %s" % inputPort)
        # Cannot resolve circular reference here, need to be fixed later
        from core.modules.sub_module import InputPort
        fromInputPortModule = [connector()
                               for connector in self.inputPorts[inputPort]
                               if type(connector.obj)==InputPort]
        if len(fromInputPortModule)>0:
            return fromInputPortModule
        return [connector() for connector in self.inputPorts[inputPort]]

    def forceGetInputListFromPort(self, inputPort):
        if not self.inputPorts.has_key(inputPort):
            return []
        return self.getInputListFromPort(inputPort)

    def enableOutputPort(self, outputPort):
        """ enableOutputPort(outputPort: str) -> None
        Set an output port to be active to store result of computation
        
        """
        # Don't reset existing values, it screws up the caching.
        if not self.outputPorts.has_key(outputPort):
            self.setResult(outputPort, None)
            
    def removeInputConnector(self, inputPort, connector):
        """ removeInputConnector(inputPort: str,
                                 connector: ModuleConnector) -> None
        Remove a connector from the connection list of an input port
        
        """
        if self.inputPorts.has_key(inputPort):
            conList = self.inputPorts[inputPort]
            if connector in conList:
                conList.remove(connector)
            if conList==[]:
                del self.inputPorts[inputPort]

    def create_instance_of_type(self, ident, name, ns=''):
        """ Create a vistrails module from the module registry.  This creates an instance of the module
        for use in creating the object output by a Module.
        """
        # FIXME (DAK): I don't get this, shouldn't we import module_registry?
        import core.modules.vistrails_module
        try:
            reg = core.modules.module_registry.get_module_registry()
            m = reg.get_module_by_name(ident, name, ns)
            return m()
        except:
            msg = "Cannot get module named " + str(name) + " with identifier " + str(ident) + " and namespace " + ns
            raise ModuleError(self, msg)

    @classmethod
    def provide_input_port_documentation(cls, port_name):
        return None

    @classmethod
    def provide_output_port_documentation(cls, port_name):
        return None

################################################################################

class NotCacheable(object):

    def is_cacheable(self):
        return False

################################################################################

class ModuleConnector(object):
    def __init__(self, obj, port, spec=None):
        self.obj = obj
        self.port = port

    def clear(self):
        """clear() -> None. Removes references, prepares for deletion."""
        self.obj = None
        self.port = None
    
    def __call__(self):
        return self.obj.get_output(self.port)

def new_module(baseModule, name, dict={}, docstring=None):
    """new_module(baseModule or [baseModule list],
                  name,
                  dict={},
                  docstring=None

    Creates a new VisTrails module dynamically. Exactly one of the
    elements of the baseModule list (or baseModule itself, in the case
    it's a single class) should be a subclass of Module.
    """
    if type(baseModule) == type:
        assert issubclass(baseModule, Module)
        superclasses = (baseModule, )
    elif type(baseModule) == list:
        assert len([x for x in baseModule
                    if issubclass(x, Module)]) == 1
        superclasses = tuple(baseModule)
    d = copy.copy(dict)
    if docstring:
        d['__doc__'] = docstring
    return type(name, superclasses, d)
    
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

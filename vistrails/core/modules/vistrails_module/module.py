###############################################################################
##
## Copyright (C) 2011-2013, NYU-Poly.
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

from vistrails.core.data_structures.bijectivedict import Bidict
from vistrails.core.task_system import Task

from .errors import InvalidOutput, ModuleBreakpoint, \
    ModuleError, ModuleErrors, ModuleSuspended


###############################################################################
# DummyModuleLogging

class DummyModuleLogging(object):
    def end_update(self, *args, **kwargs): pass
    def begin_update(self, *args, **kwargs): pass
    def begin_compute(self, *args, **kwargs): pass
    def update_cached(self, *args, **kwargs): pass
    def signalSuccess(self, *args, **kwargs): pass
    def annotate(self, *args, **kwargs): pass

_dummy_logging = DummyModuleLogging()


###############################################################################
# Serializable

class Serializable(object):
    """
    Serializable is a mixin class used to define methods to serialize and
    deserialize modules.
    """

    def serialize(self):
        """
        Method used to serialize a module.
        """
        raise Exception('The serialize method is not defined for this module.')

    def deserialize(self):
        """
        Method used to deserialize a module.
        """
        raise Exception('The deserialize method is not defined for this module.')


###############################################################################
# Module

class Module(Task, Serializable):

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

    # Task priorities - remember, lowest goes first

    # Typical priority for "update upstream ports" tasks
    # These should run first so that upstream module can add their background
    # tasks as soon as possible
    UPDATE_UPSTREAM_PRIORITY = 10
    # Typical priority for "start compute thread" tasks
    # These run before regular compute tasks so that they run at the same time
    # as the later
    COMPUTE_BACKGROUND_PRIORITY = 50
    # Typical priority for "regular compute" tasks, i.e. long
    # non-parallelizable routines
    COMPUTE_PRIORITY = 100

    def __init__(self):
        Task.__init__(self)
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
            'controller': None,
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

        # stores whether the output of the module should be annotated in the
        # execution log
        self.annotate_output = False

    def __copy__(self):
        s = super(Module, self)
        if hasattr(s, '__copy__'):
            clone = s.__copy__()
        else:
            clone = object.__new__(self.__class__)
            clone.__dict__ = self.__dict__.copy()
        clone.inputPorts = copy.copy(self.inputPorts)
        clone.outputPorts = copy.copy(self.outputPorts)
        clone.outputPorts['self'] = clone
        return clone

    def run(self):
        """Entry point of the Task, simply runs update().
        """
        self.update()

    def done(self):
        """Indicate that the Module has finished executing.

        This allows other Tasks waiting on this Module to begin.
        """
        self.computed = True
        super(Module, self).done()

    def run_upstream_module(self, callback, *modules, **kwargs):
        """Adds upstream modules to the task system.

        Registers the given modules as tasks to be run. The callback task will
        be added once these are done.
        The callback will have priority COMPUTE_PRIORITY if none is specified.
        """
        priority = kwargs.pop('priority', self.COMPUTE_PRIORITY)
        if kwargs:
            raise TypeError
        if priority is None:
            priority = self.COMPUTE_PRIORITY
        modules = [m.obj if isinstance(m, ModuleConnector) else m
                   for m in modules]
        self._runner.add(*modules, callback=lambda r: callback(),
                         priority=self.UPDATE_UPSTREAM_PRIORITY,
                         cb_priority=priority)

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

    def updateUpstream(self, callback=None, targets=None, priority=None):
        """ updateUpstream(targets: list) -> None
        Called from update() to update the upstream modules, so as to make
        their results available on this Module's input ports.
        Just schedules the Modules to be run, asking the TaskRunner to get back
        to us when they have completed.

        You can call this method from subclasses with a list of port names or
        connectors to only update some upstream modules:
            self.updateUpstream(targets=['portA', 'portB'])
            self.updateUpstream(callback=self.color_ready, targets=['color'])
        """
        if targets is None:
            connectors = []
            for connectorList in self.inputPorts.itervalues():
                connectors.extend(connectorList)
        elif not isinstance(targets, (tuple, list)):
            raise TypeError("updateUpstream(): targets should be None or the "
                            "list of wanted ports")
        elif all(isinstance(e, ModuleConnector) for e in targets):
            connectors = targets
        elif all(isinstance(e, basestring) for e in targets):
            connectors = []
            for port in targets:
                try:
                    connectors.extend(self.inputPorts[port])
                except KeyError:
                    pass
        else:
            raise TypeError("updateUpstream(): the targets list should either "
                            "contain ModuleConnector objects or port names")

        if priority is None:
            priority = self.COMPUTE_PRIORITY
        if callback is None:
            callback = self.on_upstream_ready

        self.run_upstream_module(
                lambda: callback(connectors),
                *connectors,
                priority=priority)

    def update(self):
        """ update() -> None
        This is the entry point for a Module's execution. It is called either
        by the interpreter (for a sink) or by a downstream Module that needs
        this Module's output.
        """
        self.logging.begin_update(self)
        self.updateUpstream()

    def on_upstream_ready(self, connectors):
        """ on_upstream_ready([connector: ModuleConnector]) -> None
        Callback for the TaskRunner, triggered when all upstream modules have
        completed.
        """
        for connector in connectors:
            if (hasattr(connector.obj, 'suspended') and
                    connector.obj.suspended):
                self.suspended = connector.obj.suspended
        for iport, connectorList in copy.copy(self.inputPorts.items()):
            for connector in connectorList:
                if connector.obj.get_output(connector.port) is InvalidOutput:
                    self.removeInputConnector(iport, connector)

        if self.suspended:
            self.done()
            return
        if self.upToDate:
            if not self.computed:
                self.logging.update_cached(self)
                self.computed = True
            self.done()
            return

        self.logging.begin_compute(self)
        if self.is_breakpoint:
            raise ModuleBreakpoint(self)
        if hasattr(self, 'remote_execution'):
            self.remote_execution.do_compute(self)
        else:
            self.do_compute()

    def do_compute(self, compute=None):
        """ do_compute() -> None
        Actually compute the result of this module now that the upstream
        modules have finished, optionally using several tasks. Call done() when
        finished.

        It also calls the appropriate methods on self.logging to report
        progress to the application.

        The base implementation calls 'compute' if present or compute() and
        catches error classes to set status.
        """
        self.done()
        try:
            if compute is not None:
                compute()
            else:
                self.compute()
            self.computed = True
        except ModuleSuspended, e:
            self.suspended = e.msg
            self._module_suspended = e
            self.logging.end_update(self, e, was_suspended=True)
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
        except Exception, e:
            import traceback
            traceback.print_exc()
            raise ModuleError(self, 'Uncaught exception: "%s"' % str(e))
        if self.annotate_output:
            self.annotate_output_values()
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

    def annotate_output_values(self):
        output_values = []
        for port in self.outputPorts:
            output_values.append((port, self.outputPorts[port]))
        self.logging.annotate(self, {'output': output_values})

    def get_output(self, port):
        # if self.outputPorts.has_key(port) or not self.outputPorts[port]:
        if port not in self.outputPorts:
            raise ModuleError(self, "output port '%s' not found" % port)
        return self.outputPorts[port]

    def getInputConnector(self, inputPort):
        if not self.inputPorts.has_key(inputPort):
            raise ModuleError(self, "Missing value from port %s" % inputPort)
        return self.inputPorts[inputPort][0]

    def getDefaultValue(self, inputPort):
        reg = self.registry

        d = None
        try:
            d = reg.get_descriptor(self.__class__)
        except:
            pass
        if not d:
            return None

        ps = None
        try:
            ps = reg.get_port_spec_from_descriptor(d, inputPort, 'input')
        except:
            pass
        if not ps:
            return None

        if len(ps.port_spec_items) == 1:
            psi = ps.port_spec_items[0]
            if psi.default is not None:
                m_klass = psi.descriptor.module
                return m_klass.translate_to_python(psi.default)
        else:
            default_val = []
            default_valid = True
            for psi in ps.port_spec_items:
                if psi.default is None:
                    default_valid = False
                    break
                m_klass = psi.descriptor.module
                default_val.append(
                    m_klass.translate_to_python(psi.default))
            if default_valid:
                return tuple(default_val)

        return None

    def getInputFromPort(self, inputPort, allowDefault=True):
        if inputPort not in self.inputPorts:
            if allowDefault and self.registry:
                defaultValue = self.getDefaultValue(inputPort)
                if defaultValue is not None:
                    return defaultValue
            raise ModuleError(self, "Missing value from port %s" % inputPort)
        # Cannot resolve circular reference here, need to be fixed later
        from vistrails.core.modules.sub_module import InputPort
        for conn in self.inputPorts[inputPort]:
            if isinstance(conn.obj, InputPort):
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
        from vistrails.core.modules.sub_module import InputPort
        fromInputPortModule = [connector()
                               for connector in self.inputPorts[inputPort]
                               if isinstance(connector.obj, InputPort)]
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

    @classmethod
    def provide_input_port_documentation(cls, port_name):
        return None

    @classmethod
    def provide_output_port_documentation(cls, port_name):
        return None


###############################################################################

class ModuleConnector(object):
    def __init__(self, obj, port, spec=None, typecheck=None):
        # typecheck is a list of booleans indicating which descriptors to
        # typecheck
        self.obj = obj
        self.port = port
        self.spec = spec
        self.typecheck = typecheck

    def clear(self):
        """clear() -> None. Removes references, prepares for deletion."""
        self.obj = None
        self.port = None

    def __call__(self):
        result = self.obj.get_output(self.port)
        if self.spec is not None and self.typecheck is not None:
            descs = self.spec.descriptors()
            typecheck = self.typecheck
            if len(descs) == 1:
                if not typecheck[0]:
                    return result
                mod = descs[0].module
                if hasattr(mod, 'validate') and not mod.validate(result):
                    raise ModuleError(self.obj, "Type passed on Variant port "
                                      "%s does not match destination type "
                                      "%s" % (self.port, descs[0].name))
            else:
                if len(typecheck) == 1:
                    if typecheck[0]:
                        typecheck = [True] * len(descs)
                    else:
                        return result
                if not isinstance(result, tuple):
                    raise ModuleError(self.obj, "Type passed on Variant port "
                                      "%s is not a tuple" % self.port)
                elif len(result) != len(descs):
                    raise ModuleError(self.obj, "Object passed on Variant "
                                      "port %s does not have the correct "
                                      "length (%d, expected %d)" % (
                                      self.port, len(result), len(descs)))
                for i, desc in enumerate(descs):
                    if not typecheck[i]:
                        continue
                    mod = desc.module
                    if hasattr(mod, 'validate'):
                        if not mod.validate(result[i]):
                            raise ModuleError(
                                    self.obj,
                                    "Element %d of tuple passed on Variant "
                                    "port %s does not match the destination "
                                    "type %s" % (i, self.port, desc.name))
        return result


###############################################################################

def new_module(baseModule, name, dict={}, docstring=None):
    """new_module(baseModule or [baseModule list],
                  name,
                  dict={},
                  docstring=None

    Creates a new VisTrails module dynamically. Exactly one of the
    elements of the baseModule list (or baseModule itself, in the case
    it's a single class) should be a subclass of Module.
    """
    if isinstance(baseModule, type):
        assert issubclass(baseModule, Module)
        superclasses = (baseModule, )
    elif isinstance(baseModule, list):
        assert len([x for x in baseModule
                    if issubclass(x, Module)]) == 1
        superclasses = tuple(baseModule)
    d = copy.copy(dict)
    if docstring:
        d['__doc__'] = docstring
    return type(name, superclasses, d)

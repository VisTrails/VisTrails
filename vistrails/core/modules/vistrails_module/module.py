###############################################################################
##
## Copyright (C) 2011-2014, NYU-Poly.
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
from vistrails.core import debug
from vistrails.core.modules.config import ModuleSettings, OPort
from vistrails.core.task_system import Task
from vistrails.core.utils import deprecated

from .errors import InvalidOutput, ModuleBreakpoint, \
    ModuleError, ModuleErrors


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
        raise NotImplementedError('The serialize method is not defined for this module.')

    def deserialize(self):
        """
        Method used to deserialize a module.
        """
        raise NotImplementedError('The deserialize method is not defined for this module.')


###############################################################################
# Module

class Module(Task, Serializable):
    """Module is the base module from which all module functionality
    is derived from in VisTrails. It defines a set of basic interfaces to
    deal with data input/output (through ports, as will be explained
    later), as well as a basic mechanism for dataflow based updates.

    *Execution Model*

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
    
    *Terminology*
    
    Module Interface: The module interface is the set of input and
    output ports a module exposes.
    
    *Designing New Modules*
    
    Designing new modules is essentially a matter of subclassing this
    module class and overriding the compute() method. There is a
    fully-documented example of this on the default package
    'pythonCalc', available on the 'packages/pythonCalc' directory.
    
    *Caching*
    
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
    
    *Intermediate Files*
    
    Many modules communicate through intermediate files. VisTrails
    provides automatic filename and handle management to alleviate the
    burden of determining tricky things (e.g. longevity) of these
    files. Modules can request temporary file names through the file pool,
    currently accessible through ``self.interpreter.filePool``.
    
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

    _settings = ModuleSettings(is_root=True, abstract=True)
    _output_ports = [OPort("self", "Module", optional=True)]

    def __init__(self):
        Task.__init__(self)
        self.inputPorts = {}
        self.outputPorts = {}
        self.upToDate = False
        self.set_output("self", self) # every object can return itself
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

        # computed stores wether the module was computed
        # used for the logging stuff
        self.computed = False

        self.signature = None

        # stores whether the output of the module should be annotated in the
        # execution log
        self.annotate_output = False

    def __copy__(self):
        """Makes a copy of the input/output ports on shallow copy.
        """
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
        self._runner.add(*modules, callback=callback,
                         priority=self.UPDATE_UPSTREAM_PRIORITY,
                         cb_priority=priority)

    def clear(self):
        """clear(self) -> None.
        Removes all references, prepares for deletion.

        """
        for connector_list in self.inputPorts.itervalues():
            for connector in connector_list:
                connector.clear()
        self.inputPorts = {}
        self.outputPorts = {}
        self.logging = _dummy_logging
        self.is_method = Bidict()
        self._latest_method_order = 0

    def is_cacheable(self):
        """is_cacheable() -> bool.
        A Module should return whether it can be
        reused across executions. It is safe for a Module to return
        different values in different occasions. In other words, it is
        possible for modules to be cacheable depending on their
        execution context.

        """
        return True

    def update_upstream(self, callback=None, targets=None, priority=None):
        """ update_upstream(targets: list) -> None
        Called from update() to update the upstream modules, so as to make
        their results available on this Module's input ports.
        Just schedules the Modules to be run, asking the TaskRunner to get back
        to us when they have completed.

        You can call this method from subclasses with a list of port names or
        connectors to only update some upstream modules:
            self.update_upstream(targets=['portA', 'portB'])
            self.update_upstream(callback=self.color_ready, targets=['color'])
        """
        if targets is None:
            connectors = []
            for connectorList in self.inputPorts.itervalues():
                connectors.extend(connectorList)
        elif not isinstance(targets, (tuple, list)):
            raise TypeError("update_upstream(): targets should be None or the "
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
            raise TypeError("update_upstream(): the targets list should "
                            "either contain ModuleConnector objects or port "
                            "names")

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
        self.update_upstream()

    def on_upstream_ready(self, connectors):
        """ on_upstream_ready([connector: ModuleConnector]) -> None
        Callback for the TaskRunner, triggered when all upstream modules have
        completed.
        """
        for iport, connectorList in copy.copy(self.inputPorts.items()):
            for connector in connectorList:
                if connector.obj.get_output(connector.port) is InvalidOutput:
                    self.remove_input_connector(iport, connector)

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
        try:
            if compute is not None:
                compute()
            else:
                self.compute()
            self.computed = True
            self.done()
        except ModuleError, me:
            if hasattr(me.module, 'interpreter'):
                raise
            else:
                msg = "A dynamic module raised an exception: '%s'" % me
                raise ModuleError(self, msg)
        except ModuleErrors:
            raise
        except KeyboardInterrupt, e:
            raise ModuleError(self, 'Interrupted by user')
        except Exception, e:
            import traceback
            raise ModuleError(
                    self,
                    "Uncaught exception: %s\n%s" % (
                    debug.format_exception(e),
                    traceback.format_exc()))
        if self.annotate_output:
            self.annotate_output_values()
        self.upToDate = True
        self.logging.end_update(self)
        self.logging.signalSuccess(self)

    def compute(self):
        """This method should be overridden in order to perform the module's
        computation.

        """
        pass

    def get_input(self, port_name, allow_default=True):
        """Returns the value coming in on the input port named **port_name**.

        :param port_name: the name of the input port being queried
        :type port_name: String
        :param allow_default: whether to return the default value if it exists
        :type allow_default: Boolean
        :returns: the value being passed in on the input port
        :raises: ``ModuleError`` if there is no value on the port (and no default value if allow_default is True)

        """
        if port_name not in self.inputPorts:
            if allow_default and self.registry:
                defaultValue = self.get_default_value(port_name)
                if defaultValue is not None:
                    return defaultValue
            raise ModuleError(self, "Missing value from port %s" % port_name)
        # Cannot resolve circular reference here, need to be fixed later
        from vistrails.core.modules.sub_module import InputPort
        for conn in self.inputPorts[port_name]:
            if isinstance(conn.obj, InputPort):
                return conn()
        return self.inputPorts[port_name][0]()

    def get_input_list(self, port_name):
        """Returns the value(s) coming in on the input port named
        **port_name**.  When a port can accept more than one input,
        this method obtains all the values being passed in.

        :param port_name: the name of the input port being queried
        :type port_name: String 
        :returns: a list of all the values being passed in on the input port
        :raises: ``ModuleError`` if there is no value on the port
        """

        if port_name not in self.inputPorts:
            raise ModuleError(self, "Missing value from port %s" % port_name)
        # Cannot resolve circular reference here, need to be fixed later
        from vistrails.core.modules.sub_module import InputPort
        fromInputPortModule = [connector()
                               for connector in self.inputPorts[port_name]
                               if isinstance(connector.obj, InputPort)]
        if len(fromInputPortModule)>0:
            return fromInputPortModule
        return [connector() for connector in self.inputPorts[port_name]]

    def set_output(self, port_name, value):
        """This method is used to set a value on an output port.

        :param port_name: the name of the output port to be set
        :type port_name: String
        :param value: the value to be assigned to the port

        """
        self.outputPorts[port_name] = value

    def check_input(self, port_name):
        """check_input(port_name) -> None.  
        Raises an exception if the input port named *port_name* is not set.

        :param port_name: the name of the input port being checked
        :type port_name: String
        :raises: ``ModuleError`` if there is no value on the port
        """
        if not self.has_input(port_name):
            raise ModuleError(self, "'%s' is a mandatory port" % port_name)
        
    def has_input(self, port_name):
        """Returns a boolean indicating whether there is a value coming in on
        the input port named **port_name**.
        
        :param port_name: the name of the input port being queried
        :type port_name: String 
        :rtype: Boolean

        """
        return port_name in self.inputPorts

    def force_get_input(self, port_name, default_value=None):
        """Like :py:meth:`.get_input` except that if no value exists, it
        returns a user-specified default_value or None.

        :param port_name: the name of the input port being queried
        :type port_name: String 
        :param default_value: the default value to be used if there is \
        no value on the input port
        :returns: the value being passed in on the input port or the default

        """

        if self.has_input(port_name):
            return self.get_input(port_name)
        else:
            return default_value

    def force_get_input_list(self, port_name):
        """Like :py:meth:`.get_input_list` except that if no values
        exist, it returns an empty list

        :param port_name: the name of the input port being queried
        :type port_name: String
        :returns: a list of all the values being passed in on the input port

        """
        if port_name not in self.inputPorts:
            return []
        return self.get_input_list(port_name)

    def annotate_output_values(self):
        output_values = []
        for port in self.outputPorts:
            output_values.append((port, self.outputPorts[port]))
        self.logging.annotate(self, {'output': output_values})

    def get_output(self, port_name):
        if port_name not in self.outputPorts:
            raise ModuleError(self, "output port '%s' not found" % port_name)
        return self.outputPorts[port_name]

    def get_input_connector(self, port_name):
        if port_name not in self.inputPorts:
            raise ModuleError(self, "Missing value from port %s" % port_name)
        return self.inputPorts[port_name][0]

    def get_default_value(self, port_name):
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
            ps = reg.get_port_spec_from_descriptor(d, port_name, 'input')
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

    def __str__(self):
        return "<<%s>>" % str(self.__class__)

    def annotate(self, d):

        """Manually add provenance information to the module's execution
        trace.  For example, a module that generates random numbers
        might add the seed that was used to initialize the generator.
        
        :param d: a dictionary where both the keys and values are strings
        :type d: Dictionary
        
        """

        self.logging.annotate(self, d)

    def set_input_port(self, port_name, conn, is_method=False):
        if port_name in self.inputPorts:
            self.inputPorts[port_name].append(conn)
        else:
            self.inputPorts[port_name] = [conn]
        if is_method:
            self.is_method[conn] = (self._latest_method_order, port_name)
            self._latest_method_order += 1

    def enable_output_port(self, port_name):

        """ enable_output_port(port_name: str) -> None
        Set an output port to be active to store result of computation
        
        """
        # Don't reset existing values, it screws up the caching.
        if port_name not in self.outputPorts:
            self.set_output(port_name, None)
            
    def remove_input_connector(self, port_name, connector):
        """ remove_input_connector(port_name: str,
                                 connector: ModuleConnector) -> None
        Remove a connector from the connection list of an input port
        
        """
        if port_name in self.inputPorts:
            conList = self.inputPorts[port_name]
            if connector in conList:
                conList.remove(connector)
            if conList==[]:
                del self.inputPorts[port_name]

    @classmethod
    def provide_input_port_documentation(cls, port_name):
        return None

    @classmethod
    def provide_output_port_documentation(cls, port_name):
        return None

    ####################################################################
    # Deprecated methods

    @deprecated("get_input")
    def getInputFromPort(self, *args, **kwargs):
        return self.get_input(*args, **kwargs)

    @deprecated("get_input_list")
    def getInputListFromPort(self, *args, **kwargs):
        return self.get_input_list(*args, **kwargs)

    @deprecated("force_get_input")
    def forceGetInputFromPort(self, *args, **kwargs):
        return self.force_get_input(*args, **kwargs)

    @deprecated("force_get_input_list")
    def forceGetInputListFromPort(self, *args, **kwargs):
        return self.force_get_input_list(*args, **kwargs)

    @deprecated("has_input")
    def hasInputFromPort(self, *args, **kwargs):
        return self.has_input(*args, **kwargs)

    @deprecated("check_input")
    def checkInputPort(self, *args, **kwargs):
        return self.check_input(*args, **kwargs)

    @deprecated("set_output")
    def setResult(self, *args, **kwargs):
        return self.set_output(*args, **kwargs)

    @deprecated("get_input_connector")
    def getInputConnector(self, *args, **kwargs):
        return self.get_input_connector(*args, **kwargs)

    @deprecated("get_default_value")
    def getDefaultValue(self, *args, **kwargs):
        return self.get_default_value(*args, **kwargs)

    @deprecated("enable_output_port")
    def enableOutputPort(self, *args, **kwargs):
        return self.enable_output_port(*args, **kwargs)

    @deprecated("remove_input_connector")
    def removeInputConnector(self, *args, **kwargs):
        return self.remove_input_connector(*args, **kwargs)

    @deprecated("update_upstream")
    def updateUpstream(self, *args, **kwargs):
        return self.update_upstream(*args, **kwargs)


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

def new_module(base_module, name, dict={}, docstring=None):
    """new_module(base_module or [base_module list],
                  name,
                  dict={},
                  docstring=None

    Creates a new VisTrails module dynamically. Exactly one of the
    elements of the base_module list (or base_module itself, in the case
    it's a single class) should be a subclass of Module.
    """
    if isinstance(base_module, type):
        assert issubclass(base_module, Module)
        superclasses = (base_module, )
    elif isinstance(base_module, list):
        assert sum(1 for x in base_module if issubclass(x, Module)) == 1
        superclasses = tuple(base_module)
    d = copy.copy(dict)
    if docstring:
        d['__doc__'] = docstring
    return type(name, superclasses, d)

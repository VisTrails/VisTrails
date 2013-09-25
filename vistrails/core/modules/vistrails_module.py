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
from vistrails.core.modules.config import ModuleSettings, IPort, OPort
from vistrails.core.utils import VistrailsInternalError, deprecated

class NeedsInputPort(Exception):
    def __init__(self, obj, port):
        self.obj = obj
        self.port = port
    def __str__(self):
        return "Module %s needs port %s" % (self.obj, self.port)


class IncompleteImplementation(Exception):
    def __str__(self):
        return "Module has incomplete implementation"

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
            inputs[p] = self.module.get_input_list(p)

        return inputs

class ModuleHadError(Exception):
    """Exception occurring when a module that failed gets updated again.

    It is caught by the interpreter that doesn't log it.
    """

    pass

class ModuleError(Exception):
    """Exception representing a VisTrails module runtime error. This
    exception is recognized by the interpreter and allows meaningful error
    reporting to the user and to the logging mechanism.

    """

    def __init__(self, module, errormsg, abort=False):
        """ModuleError should be passed the module instance that signaled the
        error and the error message as a string.

        """
        Exception.__init__(self, errormsg)
        self.abort = abort # force abort even if stopOnError is False
        self.module = module
        self.msg = errormsg
        import traceback
        self.errorTrace = traceback.format_exc()

class ModuleSuspended(ModuleError):
    """Exception representing a VisTrails module being suspended. Raising 
    ModuleSuspended flags that the module is not ready to finish yet and
    that the workflow should be executed later.  A suspended module does
    not execute the modules downstream but all other branches will be
    executed. This is useful when executing external jobs where you do not
    want to block vistrails while waiting for the execution to finish.

    'queue' is a class instance that should provide a finished() method for
    checking if the job has finished

    'children' is a list of ModuleSuspended instances that is used for nested
    modules
    
    """
    
    def __init__(self, module, errormsg, queue=None, children=None):
        self.queue = queue
        self.children = children
        ModuleError.__init__(self, module, errormsg)

class ModuleErrors(Exception):
    """Exception representing a list of VisTrails module runtime errors.
    This exception is recognized by the interpreter and allows meaningful
    error reporting to the user and to the logging mechanism.

    """
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

################################################################################
# Module

class Module(Serializable):
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

    _settings = ModuleSettings(is_root=True, abstract=True)
    _output_ports = [OPort("self", "Module", optional=True)]

    def __init__(self):
        self.inputPorts = {}
        self.outputPorts = {}
        self.upToDate = False
        self.ran = False
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

        # is_looping stores wether the module is a part of a loop
        self.is_looping = False

        # is_looping_module stores whether the module is a looping module
        self.is_looping_module = False

        # computed stores wether the module was computed
        # used for the logging stuff
        self.computed = False
        
        self.suspended = False

        self.signature = None
        
        # stores whether the output of the module should be annotated in the
        # execution log
        self.annotate_output = False

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

    def update_upstream_port(self, port_name):
        """Updates upstream of a single port instead of all ports."""

        if port_name in self.inputPorts:
            for connector in self.inputPorts[port_name]:
                connector.obj.update()
                if hasattr(connector.obj, 'suspended') and \
                   connector.obj.suspended:
                    self.suspended = connector.obj.suspended
            for connector in copy.copy(self.inputPorts[port_name]):
                if connector.obj.get_output(connector.port) is InvalidOutput:
                    self.remove_input_connector(port_name, connector)

    def update_upstream(self):
        """ update_upstream() -> None        
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
                    self.remove_input_connector(iport, connector)
                    
    def update(self):
        """ update() -> None        
        Check if the module is up-to-date then update the
        modules. Report to the logger if available
        
        """
        if self.upToDate:
            if not self.computed:
                self.logging.update_cached(self)
                self.computed = True
            return
        if self.ran:
            if self.had_error:
                raise ModuleHadError(self)
            return
        self.ran = True
        self.had_error = True # Unset later in this method
        self.logging.begin_update(self)
        self.update_upstream()
        if self.suspended:
            return
        self.logging.begin_compute(self)
        try:
            if self.is_breakpoint:
                raise ModuleBreakpoint(self)
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
        except ModuleBreakpoint:
            raise
        except Exception, e: 
            import traceback
            traceback.print_exc()
            raise ModuleError(self, 'Uncaught exception: "%s"' % str(e))
        if self.annotate_output:
            self.annotate_output_values()
        self.upToDate = True
        self.had_error = False
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

    def create_instance_of_type(self, ident, name, ns=''):
        """ Create a vistrails module from the module registry.  This creates an instance of the module
        for use in creating the object output by a Module.
        """
        from vistrails.core.modules.module_registry import get_module_registry
        try:
            reg = get_module_registry()
            m = reg.get_module_by_name(ident, name, ns)
            return m()
        except:
            msg = "Cannot get module named " + str(name) + \
                  " with identifier " + str(ident) + " and namespace " + ns
            raise ModuleError(self, msg)

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

    @deprecated("update_upstream_port")
    def updateUpstreamPort(self, *args, **kwargs):
        return self.updateUpstreamPort(*args, **kwargs)

################################################################################

class NotCacheable(object):

    def is_cacheable(self):
        return False

################################################################################

class Converter(Module):
    """Base class for automatic conversion modules.

    Modules that subclass Converter will be inserted automatically when
    connecting incompatible ports, if possible.

    You must override the 'in_value' and 'out_value' ports by providing the
    types your module actually matches.
    """
    _settings = ModuleSettings(abstract=True)
    _input_ports = [IPort('in_value', Module)]
    _output_ports = [OPort('out_value', Module)]

    def compute(self):
        raise NotImplementedError

################################################################################

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

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
from base64 import b16encode, b16decode

import copy
import json
import time
from itertools import izip, product
import warnings

from vistrails.core.data_structures.bijectivedict import Bidict
from vistrails.core import debug
from vistrails.core.configuration import get_vistrails_configuration
from vistrails.core.modules.config import ModuleSettings, IPort, OPort
from vistrails.core.vistrail.module_control_param import ModuleControlParam
from vistrails.core.utils import VistrailsDeprecation, deprecated, \
                                 xor, long2bytes
try:
    import hashlib
    sha1_hash = hashlib.sha1
except ImportError:
    import sha
    sha1_hash = sha.new

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
    def __init__(self, module):
        self.module = module

class ModuleWasSuspended(ModuleHadError):
    """Exception occurring when a module that was suspended gets updated again.
    """

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
    """Exception representing a VisTrails module being suspended.

    Raising ModuleSuspended flags that the module is not ready to finish yet
    and that the workflow should be executed later.
    This is useful when executing external jobs where you do not want to block
    vistrails while waiting for the execution to finish.

    'monitor' is a class instance that should provide a finished() method for
    checking if the job has finished

    'children' is a list of ModuleSuspended instances that is used for nested
    modules
    """

    def __init__(self, module, errormsg, monitor=None, children=None, job_id=None, queue=None):
        self.monitor = monitor
        if monitor is None and queue is not None:
            warnings.warn("Use of deprecated argument 'queue' replaced by "
                          "'monitor'",
                          category=VistrailsDeprecation,
                          stacklevel=2)
            self.monitor = queue
        self.children = children
        self.signature = job_id
        self.name = None
        ModuleError.__init__(self, module, errormsg)

    @property
    def queue(self):
        return self.monitor

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
    def end_update(self, *args, **kwargs): pass
    def begin_update(self, *args, **kwargs): pass
    def begin_compute(self, *args, **kwargs): pass
    def update_cached(self, *args, **kwargs): pass
    def signalSuccess(self, *args, **kwargs): pass
    def annotate(self, *args, **kwargs): pass

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
        self.had_error = False
        self.was_suspended = False
        self.is_while = False
        self.list_depth = 0
        self.logging = _dummy_logging

        # isMethod stores whether a certain input port is a method.
        # If so, isMethod maps the port to the order in which it is
        # stored. This is so that modules that need to know about the
        # method order can work correctly
        self.is_method = Bidict()
        self._latest_method_order = 0
        self.control_params = {}
        self.input_specs = {}
        self.output_specs = {}
        self.input_specs_order = []
        self.output_specs_order = []
        self.iterated_ports = []
        self.streamed_ports = {}
        self.in_pipeline = False
        self.set_output("self", self) # every object can return itself

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

    def transfer_attrs(self, module):
        if module.cache != 1:
            self.is_cacheable = lambda *args: False
        self.list_depth = module.list_depth
        self.is_breakpoint = module.is_breakpoint

        for cp in module.control_parameters:
            self.control_params[cp.name] = cp.value

        self.input_specs = dict((p.name, p) for p in module.destinationPorts())
        self.output_specs = dict((p.name, p) for p in module.sourcePorts())
        self.input_specs_order = [p.name for p in module.destinationPorts()]
        self.output_specs_order = [p.name for p in module.sourcePorts()]

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
        clone.control_params = self.control_params.copy()
        clone.input_specs = self.input_specs
        clone.output_specs = self.output_specs
        clone.input_specs_order = self.input_specs_order
        clone.output_specs_order = self.output_specs_order

        return clone

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
                connector.obj.update() # Might raise
            for connector in copy.copy(self.inputPorts[port_name]):
                if connector.obj.get_output(connector.port) is InvalidOutput:
                    self.remove_input_connector(port_name, connector)

    def update_upstream(self):
        """ update_upstream() -> None
        Go upstream from the current module, then update its upstream
        modules and check input connection based on upstream modules
        results

        """
        suspended = []
        was_suspended = None
        for connectorList in self.inputPorts.itervalues():
            for connector in connectorList:
                try:
                    connector.obj.update()
                except ModuleWasSuspended, e:
                    was_suspended = e
                except ModuleSuspended, e:
                    suspended.append(e)
                # Here we keep going even if one of the module suspended, but
                # we'll stop right after the loop
        if len(suspended) == 1:
            raise suspended[0]
        elif suspended:
            raise ModuleSuspended(
                    self,
                    "multiple suspended upstream modules",
                    children=suspended)
        elif was_suspended is not None:
            raise was_suspended
        for iport, connectorList in copy.copy(self.inputPorts.items()):
            for connector in connectorList:
                if connector.obj.get_output(connector.port) is InvalidOutput:
                    self.remove_input_connector(iport, connector)

    def set_iterated_ports(self):
        """ set_iterated_ports() -> None
        Calculates which inputs needs to be iterated over
        """
        iports = {}
        from vistrails.core.modules.basic_modules import List, Variant
        for port_name, connectorList in self.inputPorts.iteritems():
            for connector in connectorList:

                src_depth = connector.depth()
                if not self.input_specs:
                    # cannot do depth wrapping
                    continue
                # Give List an additional depth
                dest_descs = self.input_specs[port_name].descriptors()
                dest_depth = self.input_specs[port_name].depth
                if len(dest_descs) == 1 and dest_descs[0].module == List:
                    dest_depth += 1
                if connector.spec:
                    src_descs = connector.spec.descriptors()
                    if len(src_descs) == 1 and src_descs[0].module == List and \
                       len(dest_descs) == 1 and dest_descs[0].module == Variant:
                        # special case - Treat Variant as list
                        src_depth -= 1
                    if len(src_descs) == 1 and src_descs[0].module == Variant and \
                       len(dest_descs) == 1 and dest_descs[0].module == List:
                        # special case - Treat Variant as list
                        dest_depth -= 1

                # store connector with greatest depth
                # if value depth > port depth
                depth = src_depth - dest_depth
                if depth > 0 and (port_name not in iports or
                                  iports[port_name][1] < depth):
                    # keep largest
                    # raw connector only use by streaming and then use only
                    # one connector
                    iports[port_name] = (port_name, depth, connector.get_raw())
        self.iterated_ports = [iports[p] for p in self.input_specs_order
                               if p in iports]

    def set_streamed_ports(self):
        """ set_streamed_ports() -> None
        Calculates which inputs will be streamed

        """
        self.streamed_ports = {}
        from vistrails.core.modules.basic_modules import Generator
        for iport, connectorList in self.inputPorts.items():
            for connector in connectorList:
                value = connector.get_raw()
                if isinstance(value, Generator):
                    self.streamed_ports[iport] = value

    def update(self):
        """ update() -> None
        Check if the module is up-to-date then update the
        modules. Report to the logger if available

        """
        if self.had_error:
            raise ModuleHadError(self)
        elif self.was_suspended:
            raise ModuleWasSuspended(self)
        elif self.computed:
            return
        self.logging.begin_update(self)
        self.update_upstream()
        if self.upToDate:
            if not self.computed:
                self.logging.update_cached(self)
                self.computed = True
            return
        self.had_error = True # Unset later in this method
        self.logging.begin_compute(self)
        try:
            if self.is_breakpoint:
                raise ModuleBreakpoint(self)
            self.set_iterated_ports()
            self.set_streamed_ports()
            if self.streamed_ports:
                self.build_stream()
            elif self.list_depth > 0:
                self.compute_all()
            elif (self.in_pipeline and
                  not self.is_while and
                  (ModuleControlParam.WHILE_COND_KEY in self.control_params or
                   ModuleControlParam.WHILE_MAX_KEY in self.control_params)):
                self.is_while = True
                self.compute_while()
            else:
                self.compute()
            self.computed = True
        except ModuleSuspended, e:
            self.had_error, self.was_suspended = False, True
            raise
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
        except ModuleBreakpoint:
            raise
        except Exception, e:
            debug.unexpected_exception(e)
            import traceback
            raise ModuleError(
                    self,
                    "Uncaught exception: %s\n%s" % (
                    debug.format_exception(e),
                    traceback.format_exc()))
        if self.annotate_output:
            self.annotate_output_values()
        self.upToDate = True
        self.had_error = False
        self.logging.end_update(self)
        self.logging.signalSuccess(self)

    def do_combine(self, combine_type, inputs, port_name_order):
        values = []
        port_names = []
        for port_name in port_name_order:
            # this is how the (brittle) recursion is accomplished
            if not isinstance(port_name, basestring):
                sub_combine_type = port_name[0]
                sub_port_names = port_name[1:]
                sub_values, sub_port_names = self.do_combine(sub_combine_type,
                                                             inputs,
                                                             sub_port_names)
                values.append(sub_values)
                port_names.extend(sub_port_names)
            else:
                values.append((e,) for e in inputs[port_name])
                port_names.append(port_name)
        if combine_type == "pairwise":
            elements = [tuple(e for t in t_list for e in t)
                        for t_list in izip(*values)]
        elif combine_type == "cartesian":
            elements = [tuple(e for t in t_list for e in t)
                        for t_list in product(*values)]
        else:
            raise ValueError('Unknown combine type "%s"' % combine_type)
        return elements, port_names

    def get_combine_type(self, default="cartesian"):
        if ModuleControlParam.LOOP_KEY in self.control_params:
            return self.control_params[ModuleControlParam.LOOP_KEY]
        return default

    def compute_all(self):
        """This method executes the module once for each input.
           Similarly to controlflow's fold.

        """
        from vistrails.core.modules.sub_module import InputPort
        if isinstance(self, InputPort):
            return self.compute()
        if self.list_depth < 1:
            raise ModuleError(self, "List compute has wrong depth: %s" %
                                    self.list_depth)
        combine_type = self.get_combine_type('cartesian')
        suspended = []

        inputs = {} # dict of port_name: value
        port_names = []
        for port_name, depth, _ in self.iterated_ports:
            # only iterate max depth and leave the others for the
            # next iteration
            if depth != self.list_depth:
                continue
            inputs[port_name] = self.get_input(port_name)
            port_names.append(port_name)

        if combine_type not in ['pairwise', 'cartesian']:
            custom_order = json.loads(combine_type)
            combine_type = custom_order[0]
            port_names = custom_order[1:]

        elements, port_names = self.do_combine(combine_type, inputs, port_names)
        num_inputs = len(elements)
        loop = self.logging.begin_loop_execution(self, num_inputs)
        ## Update everything for each value inside the list
        outputs = {}
        module = copy.copy(self)
        module.list_depth = self.list_depth - 1
        for i in xrange(num_inputs):
            self.logging.update_progress(self, float(i)/num_inputs)
            module.had_error = False

            if not self.upToDate: # pragma: no partial
                ## Type checking if first iteration and last iteration level
                if i == 0 and self.list_depth == 1:
                    module.typeChecking(module, port_names, elements)

                module.upToDate = False
                module.computed = False

                module.setInputValues(module, port_names, elements[i], i)

            loop.begin_iteration(module, i)

            try:
                module.update()
            except ModuleSuspended, e:
                e.loop_iteration = i
                suspended.append(e)
                loop.end_iteration(module)
                continue

            loop.end_iteration(module)

            ## Getting the result from the output port
            for nameOutput in module.outputPorts:
                if nameOutput not in outputs:
                    outputs[nameOutput] = []
                output = module.get_output(nameOutput)
                outputs[nameOutput].append(output)

            self.logging.update_progress(self, i * 1.0 / num_inputs)

        if suspended:
            raise ModuleSuspended(
                    self,
                    "function module suspended in %d/%d iterations" % (
                            len(suspended), num_inputs),
                    children=suspended)
        # set final outputs
        for nameOutput in outputs:
            self.set_output(nameOutput, outputs[nameOutput])
        loop.end_loop_execution()

    def build_stream(self):
        """Determines and builds correct generator type.

        """
        from vistrails.core.modules.basic_modules import PythonSource
        if True in [g.accumulated for g in self.streamed_ports.values()]:
            # the module can only compute once the streaming is finished
            self.compute_after_streaming()
        elif self.list_depth > 0:
            # iterate the module for each value in the stream
            self.compute_streaming()
        elif isinstance(self, Streaming) or\
             (isinstance(self, PythonSource) and
              '%23%20pragma%3A%20streaming' in self.get_input('source')):
            # Magic tag: "# pragma: streaming"

            # the module creates its own generator object
            self.compute()
        else:
            # the module cannot handle generator so we accumulate the stream
            self.compute_accumulate()

    def compute_streaming(self):
        """This method creates a generator object and sets the outputs as
        generators.

        """
        from vistrails.core.modules.basic_modules import Generator
        type = self.control_params.get(ModuleControlParam.LOOP_KEY, 'pairwise')
        if type == 'cartesian':
            raise ModuleError(self,
                              'Cannot use cartesian product while streaming!')
        suspended = []

        # only iterate the max depth and leave others for the next iteration
        ports = [port for port, depth, value in self.iterated_ports
                 if depth == self.list_depth]
        num_inputs = self.iterated_ports[0][2].size
        # the generator will read next from each iterated input port and
        # compute the module again
        module = copy.copy(self)
        module.list_depth = self.list_depth - 1
        if num_inputs:
            milestones = [i*num_inputs/10 for i in xrange(1,11)]
        def generator(self):
            self.logging.begin_compute(module)
            i = 0
            while 1:
                iter_dict = dict([(port, (depth, value))
                                  for port, depth, value in
                                  self.iterated_ports])

                elements = [iter_dict[port][1].next() for port in ports]
                if None in elements:
                    for name_output in module.outputPorts:
                        module.set_output(name_output, None)
                    if suspended:
                        raise ModuleSuspended(
                                self,
                                ("function module suspended after streaming "
                                 "%d/%d iterations") % (
                                        len(suspended), num_inputs),
                                children=suspended)
                    self.logging.update_progress(module, 1.0)
                    self.logging.end_update(module)
                    yield None
                if num_inputs:
                    if i in milestones:
                        self.logging.update_progress(module,float(i)/num_inputs)
                else:
                    self.logging.update_progress(module, 0.5)
                module.had_error = False
                ## Type checking
                if i == 0:
                    module.typeChecking(module, ports, [elements])

                module.upToDate = False
                module.computed = False

                module.setInputValues(module, ports, elements, i)

                try:
                    module.compute()
                except ModuleSuspended, e:
                    e.loop_iteration = i
                    suspended.append(e)
                except Exception, e:
                    raise ModuleError(module, str(e))
                i += 1
                yield True

        _generator = generator(self)
        # set streaming outputs
        for name_output in self.outputPorts:
            iterator = Generator(size=num_inputs,
                                 module=module,
                                 generator=_generator,
                                 port=name_output)
            self.set_output(name_output, iterator)

    def compute_accumulate(self):
        """This method creates a generator object that converts all
        streaming inputs to list inputs for modules that does not explicitly
        support streaming.

        """
        from vistrails.core.modules.basic_modules import Generator
        suspended = []
        # max depth should be one
        ports = self.streamed_ports.keys()
        num_inputs = self.streamed_ports[ports[0]].size
        # the generator will read next from each iterated input port and
        # compute the module again
        module = copy.copy(self)
        module.had_error = False
        module.upToDate = False
        module.computed = False

        inputs = dict([(port, []) for port in ports])
        def generator(self):
            self.logging.begin_update(module)
            i = 0
            while 1:
                elements = [self.streamed_ports[port].next() for port in ports]
                if None in elements:
                    self.logging.begin_compute(module)
                    # assembled all inputs so do the actual computation
                    elements = [inputs[port] for port in ports]
                    ## Type checking
                    module.typeChecking(module, ports, zip(*elements))
                    module.setInputValues(module, ports, elements, i)
                    try:
                        module.compute()
                    except Exception, e:
                        raise ModuleError(module, str(e))
                    if suspended:
                        raise ModuleSuspended(
                                self,
                                ("function module suspended after streaming "
                                 "%d/%d iterations") % (
                                        len(suspended), num_inputs),
                                children=suspended)
                    self.logging.end_update(module)
                    yield None

                for port, value in zip(ports, elements):
                    inputs[port].append(value)
                for name_output in module.outputPorts:
                    module.set_output(name_output, None)
                i += 1
                yield True

        _generator = generator(self)
        # set streaming outputs
        for name_output in self.outputPorts:
            iterator = Generator(size=num_inputs,
                                 module=module,
                                 generator=_generator,
                                 port=name_output,
                                 accumulated=True)
            self.set_output(name_output, iterator)

    def compute_after_streaming(self):
        """This method creates a generator object that computes when the
        streaming is finished.

        """
        from vistrails.core.modules.basic_modules import Generator
        suspended = []

        # max depth should be one
        # max depth should be one
        ports = self.streamed_ports.keys()
        num_inputs = self.streamed_ports[ports[0]].size
        # the generator will read next from each iterated input port and
        # compute the module again
        module = copy.copy(self)
        module.had_error = False
        module.upToDate = False
        module.computed = False

        def generator(self):
            self.logging.begin_update(module)
            i = 0
            for name_output in module.outputPorts:
                module.set_output(name_output, None)
            while 1:
                elements = [self.streamed_ports[port].next() for port in ports]
                if None not in elements:
                    self.logging.begin_compute(module)
                    ## Type checking
                    module.typeChecking(module, ports, [elements])
                    module.setInputValues(module, ports, elements, i)
                    try:
                        module.compute()
                    except Exception, e:
                        raise ModuleError(module, str(e))
                    if suspended:
                        raise ModuleSuspended(
                                self,
                                ("function module suspended after streaming "
                                 "%d/%d iterations") % (
                                 len(suspended), num_inputs),
                                children=suspended)
                    self.logging.update_progress(self, 1.0)
                    self.logging.end_update(module)
                    yield None
                i += 1
                yield True

        _generator = generator(self)
        # set streaming outputs
        for name_output in self.outputPorts:
            iterator = Generator(size=num_inputs,
                                 module=module,
                                 generator=_generator,
                                 port=name_output,
                                 accumulated=True)
            self.set_output(name_output, iterator)

    def compute_while(self):
        """This method executes the module once for each module.
           Similarly to fold.

        """
        name_condition = self.control_params.get(
            ModuleControlParam.WHILE_COND_KEY, None)
        max_iterations = int(self.control_params.get(
            ModuleControlParam.WHILE_MAX_KEY, 20))
        delay = float(self.control_params.get(
            ModuleControlParam.WHILE_DELAY_KEY, 0.0))
        # todo only one state port supported right now
        name_state_input = self.control_params.get(
            ModuleControlParam.WHILE_INPUT_KEY, None)
        name_state_input = [name_state_input] if name_state_input else None
        name_state_output = self.control_params.get(
            ModuleControlParam.WHILE_OUTPUT_KEY, None)
        name_state_output = [name_state_output] if name_state_output else None

        from vistrails.core.modules.basic_modules import create_constant

        if name_state_input or name_state_output:
            if not name_state_input or not name_state_output:
                raise ModuleError(self,
                                  "Passing state between iterations requires "
                                  "BOTH StateInputPorts and StateOutputPorts "
                                  "to be set")
            if len(name_state_input) != len(name_state_output):
                raise ModuleError(self,
                                  "StateInputPorts and StateOutputPorts need "
                                  "to have the same number of ports "
                                  "(got %d and %d)" %(len(name_state_input),
                                                      len(name_state_output)))

        module = copy.copy(self)
        module.had_error = False
        module.is_while = True
        state = None

        loop = self.logging.begin_loop_execution(self, max_iterations)
        for i in xrange(max_iterations):
            if not self.upToDate:
                module.upToDate = False
                module.computed = False

                # Set state on input ports
                if i > 0 and name_state_input:
                    for value, input_port, output_port \
                     in izip(state, name_state_input, name_state_output):
                        if input_port in module.inputPorts:
                            del module.inputPorts[input_port]
                        new_connector = ModuleConnector(
                                create_constant(value), 'value',
                                module.output_specs.get(output_port, None))
                        module.set_input_port(input_port, new_connector)

            loop.begin_iteration(module, i)

            try:
                module.update() # might raise ModuleError, ModuleSuspended,
                                # ModuleHadError, ModuleWasSuspended
            except ModuleSuspended, e:
                e.loop_iteration = i
                raise

            loop.end_iteration(module)

            if name_condition is not None:
                if name_condition not in module.outputPorts:
                    raise ModuleError(
                            module,
                            "Invalid output port: %s" % name_condition)
                if not module.get_output(name_condition):
                    break

            if delay and i+1 != max_iterations:
                time.sleep(delay)

            # Get state on output ports
            if name_state_output:
                state = [module.get_output(port) for port in name_state_output]

            self.logging.update_progress(self, i * 1.0 / max_iterations)

        loop.end_loop_execution()

        for name_output in self.outputPorts:
            self.set_output(name_output, module.get_output(name_output))

    def setInputValues(self, module, inputPorts, elementList, iteration):
        """
        Function used to set a value inside 'module', given the input port(s).
        """
        from vistrails.core.modules.basic_modules import create_constant
        for element, inputPort in izip(elementList, inputPorts):
            ## Cleaning the previous connector...
            if inputPort in module.inputPorts:
                del module.inputPorts[inputPort]
            spec = None
            if inputPort in self.input_specs:
                spec = self.input_specs[inputPort].__copy__()
                spec.depth += module.list_depth
            new_connector = ModuleConnector(create_constant(element), 'value',
                                            spec)
            module.set_input_port(inputPort, new_connector)
            # Affix a fake signature on the module
            # Ultimately, we might want to give it the signature it would have
            # with its current functions if it had a connection to the upstream
            # of our InputList port through a Getter module?
            # This structure with the Getter is unlikely to actually happen
            # anywhere though...
            # The fake signature is
            # XOR(signature(loop module), iteration, hash(inputPort))
            inputPort_hash = sha1_hash()
            inputPort_hash.update(inputPort)
            module.signature = b16encode(xor(
                    b16decode(self.signature.upper()),
                    long2bytes(iteration, 20),
                    inputPort_hash.digest()))

    Variant_desc = None
    InputPort_desc = None

    @staticmethod
    def load_type_check_descs():
        from vistrails.core.modules.module_registry import get_module_registry
        reg = get_module_registry()
        Module.Variant_desc = reg.get_descriptor_by_name(
            'org.vistrails.vistrails.basic', 'Variant')
        Module.InputPort_desc = reg.get_descriptor_by_name(
            'org.vistrails.vistrails.basic', 'InputPort')

    @staticmethod
    def get_type_checks(source_spec):
        if Module.Variant_desc is None:
            Module.load_type_check_descs()
        conf = get_vistrails_configuration()
        error_on_others = getattr(conf, 'showConnectionErrors')
        error_on_variant = (error_on_others or
                            getattr(conf, 'showVariantErrors'))
        errors = [error_on_others, error_on_variant]
        return [errors[desc is Module.Variant_desc]
                for desc in source_spec.descriptors()]

    def typeChecking(self, module, inputPorts, inputList):
        """
        Function used to check if the types of the input list element and of the
        inputPort of 'module' match.
        """
        from vistrails.core.modules.basic_modules import Generator
        from vistrails.core.modules.basic_modules import get_module
        if not module.input_specs:
            return
        for elementList in inputList:
            if len(elementList) != len(inputPorts):
                raise ModuleError(self,
                                  'The number of input values and input ports '
                                  'are not the same.')
            for element, inputPort in izip(elementList, inputPorts):
                if isinstance(element, Generator):
                    raise ModuleError(self, "Generator is not allowed here")
                port_spec = module.input_specs[inputPort]
                # typecheck only if all params should be type-checked
                if False in self.get_type_checks(port_spec):
                    break
                v_module = get_module(element, port_spec.signature)
                if v_module is not None:
                    if not self.compare(port_spec, v_module, inputPort):
                        raise ModuleError(self,
                                          'The type of a list element does '
                                          'not match with the type of the '
                                          'port %s.' % inputPort)
                    del v_module
                else:
                    break

    def createSignature(self, v_module):
        """
    `   Function used to create a signature, given v_module, for a port spec.
        """
        if isinstance(v_module, tuple):
            v_module_class = []
            for module_ in v_module:
                v_module_class.append(self.createSignature(module_))
            return v_module_class
        else:
            return v_module

    def compare(self, port_spec, v_module, port):
        """
        Function used to compare two port specs.
        """
        port_spec1 = port_spec

        from vistrails.core.modules.module_registry import get_module_registry
        from vistrails.core.vistrail.port_spec import PortSpec
        reg = get_module_registry()

        v_module = self.createSignature(v_module)
        port_spec2 = PortSpec(**{'signature': v_module})
        matched = reg.are_specs_matched(port_spec2, port_spec1)

        return matched

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

        # Check for generator
        from vistrails.core.modules.basic_modules import Generator
        raw = self.inputPorts[port_name][0].get_raw()
        if isinstance(raw, Generator):
            return raw

        if self.input_specs:
            # join connections for depth > 0 and List
            list_desc = self.registry.get_descriptor_by_name(
                    'org.vistrails.vistrails.basic', 'List')

            if (self.input_specs[port_name].depth + self.list_depth > 0) or \
                self.input_specs[port_name].descriptors() == [list_desc]:
                return [j for i in self.get_input_list(port_name) for j in i]

        # else return first connector item
        value = self.inputPorts[port_name][0]()
        return value

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
        ports = []
        for connector in self.inputPorts[port_name]:
            from vistrails.core.modules.basic_modules import List, Variant
            value = connector()
            src_depth = connector.depth()
            if not self.input_specs:
                # cannot do depth wrapping
                ports.append(value)
                continue
            # Give List an additional depth
            dest_descs = self.input_specs[port_name].descriptors()
            dest_depth = self.input_specs[port_name].depth + self.list_depth
            if len(dest_descs) == 1 and dest_descs[0].module == List:
                dest_depth += 1
            if connector.spec:
                src_descs = connector.spec.descriptors()
                if len(src_descs) == 1 and src_descs[0].module == List and \
                   len(dest_descs) == 1 and dest_descs[0].module == Variant:
                    # special case - Treat Variant as list
                    src_depth -= 1
                if len(src_descs) == 1 and src_descs[0].module == Variant and \
                   len(dest_descs) == 1 and dest_descs[0].module == List:
                    # special case - Treat Variant as list
                    dest_depth -= 1
            # wrap depths that are too shallow
            while (src_depth - dest_depth) < 0:
                value = [value]
                src_depth += 1
            # type check list of lists
            root = value
            for i in xrange(1, src_depth):
                try:
                    # flatten
                    root = [item for sublist in root for item in sublist]
                except TypeError:
                    raise ModuleError(self, "List on port %s has wrong"
                                            " depth %s, expected %s." %
                                            (port_name, i-1, src_depth))

            if src_depth and root is not None:
                self.typeChecking(self, [port_name],
                                  [[r] for r in root] if src_depth else [[root]])
            ports.append(value)
        return ports

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
        except Exception:
            pass
        if not d:
            return None

        ps = None
        try:
            ps = reg.get_port_spec_from_descriptor(d, port_name, 'input')
        except Exception:
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
        """ Create a vistrails module from the module registry.  This creates
        an instance of the module for use in creating the object output by a
        Module.
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

    def set_streaming(self, UserGenerator):
        """creates a generator object that computes when the next input is received.
        """
        # use the below tag if calling from a PythonSource
        # pragma: streaming - This tag is magic, do not change.
        from vistrails.core.modules.basic_modules import Generator

        ports = self.streamed_ports.keys()
        specs = []
        num_inputs = self.streamed_ports[ports[0]].size
        module = copy.copy(self)
        module.list_depth = self.list_depth - 1
        module.had_error = False
        module.upToDate = False
        module.computed = False

        if num_inputs:
            milestones = [i*num_inputs/10 for i in xrange(1,11)]

        def _Generator(self):
            self.logging.begin_compute(module)
            i = 0
            # <initialize here>
            #intsum = 0
            userGenerator = UserGenerator(module)
            while 1:
                elements = [self.streamed_ports[port].next() for port in ports]
                if None in elements:
                    self.logging.update_progress(self, 1.0)
                    self.logging.end_update(module)
                    for name_output in module.outputPorts:
                        module.set_output(name_output, None)
                    yield None
                ## Type checking
                module.typeChecking(module, ports, [elements])
                module.setInputValues(module, ports, elements, i)

                userGenerator.next()
                # <compute here>
                #intsum += dict(zip(ports, elements))['integerStream']
                #print "Sum so far:", intsum

                # <set output here if any>
                #module.set_output(name_output, intsum)
                if num_inputs:
                    if i in milestones:
                        self.logging.update_progress(self,float(i)/num_inputs)
                else:
                    self.logging.update_progress(self, 0.5)
                i += 1
                yield True

        generator = _Generator(self)
        # sets streaming outputs for downstream modules
        for name_output in self.outputPorts:
            iterator = Generator(size=num_inputs,
                                 module=module,
                                 generator=generator,
                                 port=name_output)

            self.set_output(name_output, iterator)

    def set_streaming_output(self, port, generator, size=0):
        """This method is used to set a streaming output port.

        :param port: the name of the output port to be set
        :type port: String
        :param generator: An iterator object supporting .next()
        :param size: The number of values if known (default=0)
        :type size: Integer
        """
        from vistrails.core.modules.basic_modules import Generator
        module = copy.copy(self)

        if size:
            milestones = [i*size/10 for i in xrange(1,11)]
        def _Generator():
            i = 0
            while 1:
                try:
                    value = generator.next()
                except StopIteration:
                    module.set_output(port, None)
                    self.logging.update_progress(self, 1.0)
                    yield None
                except Exception, e:
                    me = ModuleError(self, "Error generating value: %s"% str(e),
                                      errorTrace=str(e))
                    raise me
                if value is None:
                    module.set_output(port, None)
                    self.logging.update_progress(self, 1.0)
                    yield None
                module.set_output(port, value)
                if size:
                    if i in milestones:
                        self.logging.update_progress(self,float(i)/size)
                else:
                    self.logging.update_progress(self, 0.5)
                i += 1
                yield True
        _generator = _Generator()
        self.set_output(port, Generator(size=size,
                                        module=module,
                                        generator=_generator,
                                        port=port))

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
        if 'allowDefault' in kwargs:
            kwargs['allow_default'] = kwargs.pop('allowDefault')
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

class Streaming(object):
    """ A mixin indicating support for streamable inputs

    """
    pass

################################################################################

class Converter(Module):
    """Base class for automatic conversion modules.

    Modules that subclass Converter will be inserted automatically when
    connecting incompatible ports, if possible.

    You must override the 'in_value' and 'out_value' ports by providing the
    types your module actually matches.

    Alternatively, you can override the classmethod can_convert() to provide
    a custom condition.
    """
    _settings = ModuleSettings(abstract=True)
    _input_ports = [IPort('in_value', 'Variant')]
    _output_ports = [OPort('out_value', 'Variant')]
    @classmethod
    def can_convert(cls, sub_descs, super_descs):
        from vistrails.core.modules.module_registry import get_module_registry
        from vistrails.core.system import get_vistrails_basic_pkg_id
        reg = get_module_registry()
        basic_pkg = get_vistrails_basic_pkg_id()
        desc = reg.get_descriptor(cls)

        in_port = reg.get_port_spec_from_descriptor(
                desc,
                'in_value', 'input')
        if (len(sub_descs) != len(in_port.descriptors()) or
                not reg.is_descriptor_list_subclass(sub_descs,
                                                    in_port.descriptors())):
            return False
        out_port = reg.get_port_spec_from_descriptor(
                desc,
                'out_value', 'output')
        if (len(out_port.descriptors()) != len(super_descs)
                or not reg.is_descriptor_list_subclass(out_port.descriptors(),
                                                       super_descs)):
            return False

        return True

    def compute(self):
        raise NotImplementedError

################################################################################

class ModuleConnector(object):
    def __init__(self, obj, port, spec=None, typecheck=None):
        # typecheck is a list of booleans indicating which descriptors to
        # typecheck
        self.obj = obj
        self.port = port
        if spec is None:
            # guess type
            from vistrails.core.modules.basic_modules import get_module
            from vistrails.core.vistrail.port_spec import PortSpec
            spec = PortSpec(**{'signature': get_module(self.get_raw())})
        self.spec = spec
        self.typecheck = typecheck

    def clear(self):
        """clear() -> None. Removes references, prepares for deletion."""
        self.obj = None
        self.port = None

    def depth(self, fix_list=True):
        """depth(result) -> int. Returns the list depth of the port value."""
        from vistrails.core.modules.basic_modules import List
        depth = self.obj.list_depth + self.spec.depth
        descs = self.spec.descriptors()
        if fix_list and len(descs) == 1 and descs[0].module == List:
            # lists are Variants of depth 1
            depth += 1
        return depth

    def get_raw(self):
        """get_raw() -> Module. Returns the value or a Generator."""
        return self.obj.get_output(self.port)


    def __call__(self):
        result = self.obj.get_output(self.port)
        if isinstance(result, Module):
            warnings.warn(
                    "A Module instance was used as data: "
                    "module=%s, port=%s, object=%r" % (type(self.obj).__name__,
                                                       self.port, result),
                    UserWarning)
        from vistrails.core.modules.basic_modules import Generator
        value = result
        if isinstance(result, Generator):
            return result
        depth = self.depth(fix_list=False)
        if depth > 0:
            value = result
            # flatten list
            for i in xrange(1, depth):
                try:
                    value = [item for sublist in value for item in sublist]
                except TypeError:
                    raise ModuleError(self.obj, "List on port %s has wrong"
                                      " depth %s, expected %s." %
                                      (self.port, i, depth))
            if depth:
                # Only type-check first value
                value = value[0] if value is not None and len(value) else None

        if self.spec is not None and self.typecheck is not None:
            descs = self.spec.descriptors()
            typecheck = self.typecheck
            if len(descs) == 1:
                if not typecheck[0]:
                    return result
                mod = descs[0].module
                if value is not None and hasattr(mod, 'validate') \
                   and not mod.validate(value):
                    raise ModuleError(self.obj, "Type passed on Variant port "
                                      "%s does not match destination type "
                                      "%s" % (self.port, descs[0].name))
            else:
                if len(typecheck) == 1:
                    if typecheck[0]:
                        typecheck = [True] * len(descs)
                    else:
                        return result
                if not isinstance(value, tuple):
                    raise ModuleError(self.obj, "Type passed on Variant port "
                                      "%s is not a tuple" % self.port)
                elif len(value) != len(descs):
                    raise ModuleError(self.obj, "Object passed on Variant "
                                      "port %s does not have the correct "
                                      "length (%d, expected %d)" % (
                                      self.port, len(result), len(descs)))
                for i, desc in enumerate(descs):
                    if not typecheck[i]:
                        continue
                    mod = desc.module
                    if hasattr(mod, 'validate'):
                        if not mod.validate(value[i]):
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

import unittest

class TestImplicitLooping(unittest.TestCase):
    def run_vt(self, vt_basename):
        from vistrails.core.system import vistrails_root_directory
        from vistrails.core.db.locator import FileLocator
        from vistrails.core.db.io import load_vistrail
        from vistrails.core.console_mode import run
        from vistrails.tests.utils import capture_stdout
        import os
        filename = os.path.join(vistrails_root_directory(), "tests",
                                "resources", vt_basename)
        try:
            errs = []
            locator = FileLocator(os.path.abspath(filename))
            (v, _, _, _) = load_vistrail(locator)
            w_list = []
            for version, _ in v.get_tagMap().iteritems():
                w_list.append((locator,version))
            if len(w_list) > 0:
                with capture_stdout() as c:
                    errs = run(w_list, update_vistrail=False)
                for err in errs:
                    self.fail(str(err))
        except Exception, e:
            self.fail(debug.format_exception(e))

    def test_implicit_while(self):
        self.run_vt("test-implicit-while.vt")

    def test_streaming(self):
        self.run_vt("test-streaming.vt")

    def test_list_custom(self):
        self.run_vt("test-list-custom.vt")

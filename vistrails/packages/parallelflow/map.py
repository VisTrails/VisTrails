###############################################################################
##
## Copyright (C) 2014-2016, New York University.
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
##  - Neither the name of the New York University nor the names of its
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

from __future__ import division

import vistrails.core.db.action
from vistrails.core.db.locator import XMLFileLocator
from vistrails.core.db.io import serialize, unserialize
from vistrails.core import debug
from vistrails.core.interpreter.default import get_default_interpreter
from vistrails.core.log.group_exec import GroupExec
from vistrails.core.log.machine import Machine
from vistrails.core.log.module_exec import ModuleExec
from vistrails.core.modules.basic_modules import Constant
import vistrails.core.modules.module_registry
import vistrails.core.modules.utils
from vistrails.core.modules.vistrails_module import Module, ModuleError, \
    InvalidOutput
from vistrails.core.vistrail.annotation import Annotation
from vistrails.core.vistrail.controller import VistrailController
from vistrails.core.vistrail.group import Group
from vistrails.core.vistrail.module_function import ModuleFunction
from vistrails.core.vistrail.module_param import ModuleParam
from vistrails.core.vistrail.pipeline import Pipeline
from vistrails.core.vistrail.vistrail import Vistrail
from vistrails.db.domain import IdScope
import vistrails.db.versions

import copy
import inspect
from itertools import izip
import os
import re
import sys
import tempfile

from IPython.parallel.error import CompositeError

from .api import get_client

try:
    import hashlib
    sha1_hash = hashlib.sha1
except ImportError:
    import sha
    sha1_hash = sha.new


###############################################################################
# This function is sent to the engines which execute it
#
# It receives the workflow, and the list of targeted output ports
#
# It returns the corresponding computed outputs and the execution log
#
def execute_wf(wf, output_port):
    # Save the workflow in a temporary file
    temp_wf_fd, temp_wf = tempfile.mkstemp()

    try:
        f = open(temp_wf, 'w')
        f.write(wf)
        f.close()
        os.close(temp_wf_fd)

        # Clean the cache
        interpreter = get_default_interpreter()
        interpreter.flush()

        # Load the Pipeline from the temporary file
        vistrail = Vistrail()
        locator = XMLFileLocator(temp_wf)
        workflow = locator.load(Pipeline)

        # Build a Vistrail from this single Pipeline
        action_list = []
        for module in workflow.module_list:
            action_list.append(('add', module))
        for connection in workflow.connection_list:
            action_list.append(('add', connection))
        action = vistrails.core.db.action.create_action(action_list)

        vistrail.add_action(action, 0L)
        vistrail.update_id_scope()
        tag = 'parallel flow'
        vistrail.addTag(tag, action.id)

        # Build a controller and execute
        controller = VistrailController()
        controller.set_vistrail(vistrail, None)
        controller.change_selected_version(vistrail.get_version_number(tag))
        execution = controller.execute_current_workflow(
                custom_aliases=None,
                custom_params=None,
                extra_info=None,
                reason='API Pipeline Execution')

        # Build a list of errors
        errors = []
        pipeline = vistrail.getPipeline(tag)
        execution_errors = execution[0][0].errors
        if execution_errors:
            for key in execution_errors:
                module = pipeline.modules[key]
                msg = '%s: %s' %(module.name, execution_errors[key])
                errors.append(msg)

        # Get the execution log from the controller
        try:
            module_log = controller.log.workflow_execs[0].item_execs[0]
        except IndexError:
            errors.append("Module log not found")
            return dict(errors=errors)
        else:
            machine = controller.log.workflow_execs[0].machines[
                    module_log.machine_id]
            xml_log = serialize(module_log)
            machine_log = serialize(machine)

        # Get the output value
        output = None
        if not execution_errors:
            executed_module, = execution[0][0].executed
            executed_module = execution[0][0].objects[executed_module]
            try:
                output = executed_module.get_output(output_port)
            except ModuleError:
                errors.append("Output port not found: %s" % output_port)
                return dict(errors=errors)
            if isinstance(output, Module):
                raise TypeError("Output value is a Module instance")

        # Return the dictionary, that will be sent back to the client
        return dict(errors=errors,
                    output=output,
                    xml_log=xml_log,
                    machine_log=machine_log)
    finally:
        os.unlink(temp_wf)

###############################################################################

_ansi_code = re.compile(r'%s(?:(?:\[[^A-Za-z]*[A-Za-z])|[^\[])' % '\x1B')

def strip_ansi_codes(s):
    return _ansi_code.sub('', s)

###############################################################################
# Map Operator
#
class Map(Module):
    """The Map Module executes a map operator in parallel on IPython engines.

    The FunctionPort should be connected to the 'self' output of the module you
    want to execute.
    The InputList is the list of values to be scattered on the engines.
    """
    def __init__(self):
        Module.__init__(self)

    def update_upstream(self):
        """A modified version of the update_upstream method."""

        # everything is the same except that we don't update anything
        # upstream of FunctionPort
        for port_name, connector_list in self.inputPorts.iteritems():
            if port_name == 'FunctionPort':
                for connector in connector_list:
                    connector.obj.update_upstream()
            else:
                for connector in connector_list:
                    connector.obj.update()
        for port_name, connectorList in copy.copy(self.inputPorts.items()):
            if port_name != 'FunctionPort':
                for connector in connectorList:
                    if connector.obj.get_output(connector.port) is \
                            InvalidOutput:
                        self.remove_input_connector(port_name, connector)

    @staticmethod
    def print_compositeerror(e):
        sys.stderr.write("Got %d exceptions from IPython engines:\n" %
                         len(e.elist))
        for e_type, e_msg, formatted_tb, infos in e.elist:
            sys.stderr.write("Error from engine %d (%r):\n" % (
                             infos['engine_id'], infos['engine_uuid']))
            sys.stderr.write("%s\n" % strip_ansi_codes(formatted_tb))

    @staticmethod
    def list_exceptions(e):
        return '\n'.join(
                "% 3d: %s: %s" % (infos['engine_id'],
                                  e_type,
                                  e_msg)
                for e_type, e_msg, tb, infos in e.elist)

    def updateFunctionPort(self):
        """
        Function to be used inside the updateUsptream method of the Map module. It
        updates the module connected to the FunctionPort port, executing it in
        parallel.
        """
        nameInput = self.get_input('InputPort')
        nameOutput = self.get_input('OutputPort')
        rawInputList = self.get_input('InputList')

        # Create inputList to always have iterable elements
        # to simplify code
        if len(nameInput) == 1:
            element_is_iter = False
            inputList = [[element] for element in rawInputList]
        else:
            element_is_iter = True
            inputList = rawInputList

        workflows = []
        module = None
        vtType = None

        # iterating through the connectors
        for connector in self.inputPorts.get('FunctionPort'):
            module = connector.obj

            # pipeline
            original_pipeline = connector.obj.moduleInfo['pipeline']

            # module
            module_id = connector.obj.moduleInfo['moduleId']
            vtType = original_pipeline.modules[module_id].vtType

            # serialize the module for each value in the list
            for i, element in enumerate(inputList):
                if element_is_iter:
                    self.element = element
                else:
                    self.element = element[0]

                # checking type and setting input in the module
                self.typeChecking(connector.obj, nameInput, inputList)
                self.setInputValues(connector.obj, nameInput, element, i)

                pipeline_db_module = original_pipeline.modules[module_id].do_copy()

                # transforming a subworkflow in a group
                # TODO: should we also transform inner subworkflows?
                if pipeline_db_module.is_abstraction():
                    group = Group(id=pipeline_db_module.id,
                                  cache=pipeline_db_module.cache,
                                  location=pipeline_db_module.location,
                                  functions=pipeline_db_module.functions,
                                  annotations=pipeline_db_module.annotations)

                    source_port_specs = pipeline_db_module.sourcePorts()
                    dest_port_specs = pipeline_db_module.destinationPorts()
                    for source_port_spec in source_port_specs:
                        group.add_port_spec(source_port_spec)
                    for dest_port_spec in dest_port_specs:
                        group.add_port_spec(dest_port_spec)

                    group.pipeline = pipeline_db_module.pipeline
                    pipeline_db_module = group

                # getting highest id between functions to guarantee unique ids
                # TODO: can get current IdScope here?
                if pipeline_db_module.functions:
                    high_id = max(function.db_id
                                  for function in pipeline_db_module.functions)
                else:
                    high_id = 0

                # adding function and parameter to module in pipeline
                # TODO: 'pos' should not be always 0 here
                id_scope = IdScope(beginId=long(high_id+1))
                for elementValue, inputPort in izip(element, nameInput):

                    p_spec = pipeline_db_module.get_port_spec(inputPort, 'input')
                    descrs = p_spec.descriptors()
                    if len(descrs) != 1:
                        raise ModuleError(
                                self,
                                "Tuple input ports are not supported")
                    if not issubclass(descrs[0].module, Constant):
                        raise ModuleError(
                                self,
                                "Module inputs should be Constant types")
                    type = p_spec.sigstring[1:-1]

                    mod_function = ModuleFunction(id=id_scope.getNewId(ModuleFunction.vtType),
                                                  pos=0,
                                                  name=inputPort)
                    mod_param = ModuleParam(id=0L,
                                            pos=0,
                                            type=type,
                                            val=elementValue)

                    mod_function.add_parameter(mod_param)
                    pipeline_db_module.add_function(mod_function)

                # serializing module
                wf = self.serialize_module(pipeline_db_module)
                workflows.append(wf)

            # getting first connector, ignoring the rest
            break

        # IPython stuff
        try:
            rc = get_client()
        except Exception, error:
            raise ModuleError(self, "Exception while loading IPython: %s" %
                              debug.format_exception(error))
        if rc is None:
            raise ModuleError(self, "Couldn't get an IPython connection")
        engines = rc.ids
        if not engines:
            raise ModuleError(
                    self,
                    "Exception while loading IPython: No IPython engines "
                    "detected!")

        # initializes each engine
        # importing modules and initializing the VisTrails application
        # in the engines *only* in the first execution on this engine
        uninitialized = []
        for eng in engines:
            try:
                rc[eng]['init']
            except Exception:
                uninitialized.append(eng)
        if uninitialized:
            init_view = rc[uninitialized]
            with init_view.sync_imports():
                import tempfile
                import inspect

                # VisTrails API
                import vistrails
                import vistrails.core
                import vistrails.core.db.action
                import vistrails.core.application
                import vistrails.core.modules.module_registry
                from vistrails.core.db.io import serialize
                from vistrails.core.vistrail.vistrail import Vistrail
                from vistrails.core.vistrail.pipeline import Pipeline
                from vistrails.core.db.locator import XMLFileLocator
                from vistrails.core.vistrail.controller import VistrailController
                from vistrails.core.interpreter.default import get_default_interpreter

            # initializing a VisTrails application
            try:
                init_view.execute(
                        'app = vistrails.core.application.init('
                        '        {"spawned": True},'
                        '        args=[])',
                        block=True)
            except CompositeError, e:
                self.print_compositeerror(e)
                raise ModuleError(self, "Error initializing application on "
                                  "IPython engines:\n"
                                  "%s" % self.list_exceptions(e))

            init_view['init'] = True

        # setting computing color
        module.logging.set_computing(module)

        # executing function in engines
        # each map returns a dictionary
        try:
            ldview = rc.load_balanced_view()
            map_result = ldview.map_sync(execute_wf, workflows, [nameOutput]*len(workflows))
        except CompositeError, e:
            self.print_compositeerror(e)
            raise ModuleError(self, "Error from IPython engines:\n"
                              "%s" % self.list_exceptions(e))

        # verifying errors
        errors = []
        for engine in range(len(map_result)):
            if map_result[engine]['errors']:
                msg = "ModuleError in engine %d: '%s'" % (
                        engine,
                        ', '.join(map_result[engine]['errors']))
                errors.append(msg)

        if errors:
            raise ModuleError(self, '\n'.join(errors))

        # setting success color
        module.logging.signalSuccess(module)

        reg = vistrails.core.modules.module_registry.get_module_registry()
        self.result = []
        for map_execution in map_result:
            output = map_execution['output']
            self.result.append(output)

        # including execution logs
        for engine in range(len(map_result)):
            log = map_result[engine]['xml_log']
            exec_ = None
            if (vtType == 'abstraction') or (vtType == 'group'):
                exec_ = unserialize(log, GroupExec)
            elif (vtType == 'module'):
                exec_ = unserialize(log, ModuleExec)
            else:
                # something is wrong...
                continue

            # assigning new ids to existing annotations
            exec_annotations = exec_.annotations
            for i in range(len(exec_annotations)):
                exec_annotations[i].id = self.logging.log.log.id_scope.getNewId(Annotation.vtType)

            parallel_annotation = Annotation(key='parallel_execution', value=True)
            parallel_annotation.id = self.logging.log.log.id_scope.getNewId(Annotation.vtType)
            annotations = [parallel_annotation] + exec_annotations
            exec_.annotations = annotations

            # before adding the execution log, we need to get the machine information
            machine = unserialize(map_result[engine]['machine_log'], Machine)
            machine_id = self.logging.add_machine(machine)

            # recursively add machine information to execution items
            def add_machine_recursive(exec_):
                for item in exec_.item_execs:
                    if hasattr(item, 'machine_id'):
                        item.machine_id = machine_id
                        if item.vtType in ('abstraction', 'group'):
                            add_machine_recursive(item)

            exec_.machine_id = machine_id
            if (vtType == 'abstraction') or (vtType == 'group'):
                add_machine_recursive(exec_)

            self.logging.add_exec(exec_)


    def serialize_module(self, module):
        """
        Serializes a module to be executed in parallel.
        """

        def process_group(group):
            group.pipeline.id = None
            for module in group.pipeline.module_list:
                if module.is_group():
                    process_group(module)

        pipeline = Pipeline(version=vistrails.db.versions.currentVersion)

        if module.is_group():
            process_group(module)

        module = module.do_copy()
        pipeline.add_module(module)

        return serialize(pipeline)

    def compute(self):
        """The compute method for Map."""

        self.result = None
        self.updateFunctionPort()

        self.set_output('Result', self.result)

###############################################################################

class NewConstant(Constant):
    """
    A new Constant module to be used inside the Map module.
    """
    def setValue(self, v):
        self.set_output("value", v)
        self.upToDate = True

def create_constant(value):
    """
    Creates a NewConstant module, to be used for the ModuleConnector.
    """
    constant = NewConstant()
    constant.setValue(value)
    return constant

def get_module(value, signature):
    """
    Creates a module for value, in order to do the type checking.
    """

    from vistrails.core.modules.basic_modules import Boolean, String, Integer, Float, List

    if isinstance(value, Constant):
        return type(value)
    elif isinstance(value, bool):
        return Boolean
    elif isinstance(value, str):
        return String
    elif isinstance(value, int):
        return Integer
    elif isinstance(value, float):
        return Float
    elif isinstance(value, list):
        return List
    elif isinstance(value, tuple):
        v_modules = ()
        for element in xrange(len(value)):
            v_modules += (get_module(value[element], signature[element]))
        return v_modules
    else:
        from vistrails.core import debug
        debug.warning("Could not identify the type of the list element.")
        debug.warning("Type checking is not going to be done inside Map module.")
        return None

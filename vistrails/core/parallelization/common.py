import os
import pickle
import tempfile

import vistrails.core.db.action
import vistrails.core.application
from vistrails.core.application import get_vistrails_application
from vistrails.core.db.io import serialize, unserialize
from vistrails.core.db.locator import XMLFileLocator
from vistrails.core.interpreter.default import get_default_interpreter
from vistrails.core.log.group_exec import GroupExec
from vistrails.core.log.machine import Machine
from vistrails.core.log.module_exec import ModuleExec
from vistrails.core.modules.basic_modules import Unpickle
from vistrails.core.modules.module_registry import get_module_registry
from vistrails.core.modules.sub_module import InputPort
from vistrails.core.modules.vistrails_module import ModuleError
from vistrails.core.modules.vistrails_module.parallel import set_is_subprocess
from vistrails.core.vistrail.annotation import Annotation
from vistrails.core.vistrail.controller import VistrailController
from vistrails.core.vistrail.group import Group
from vistrails.core.vistrail.pipeline import Pipeline
from vistrails.core.vistrail.vistrail import Vistrail
import vistrails.db.versions


def get_pickled_module_inputs(module):
    inputs = {}
    for name, conns in module.inputPorts.iteritems():
        inputlist = []
        for conn in conns:
            if isinstance(conn.obj, InputPort):
                inputlist.insert(0, pickle.dumps(conn()))
            else:
                inputlist.append(pickle.dumps(conn()))
        if inputlist:
            inputs[name] = inputlist
    return inputs


def execute_serialized_pipeline(wf, moduleId, inputs, output_ports):
    if get_vistrails_application() is None:
        vistrails.core.application.init(args=[])

    set_is_subprocess()

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

        # Build a controller
        controller = VistrailController()
        controller.set_vistrail(vistrail, None)
        controller.change_selected_version(vistrail.get_version_number(tag))

        # Create the input modules/connections
        reg = get_module_registry()
        unpickle_desc = reg.get_descriptor(Unpickle)
        for portname, values in inputs.iteritems():
            for value in values:
                m = controller.add_module_from_descriptor(unpickle_desc)
                controller.update_function(m, 'input', [value])
                controller.add_connection(m.id, 'result',
                                          moduleId, portname)

        # Execute
        execution = controller.execute_current_workflow(
                custom_aliases=None,
                custom_params=None,
                extra_info=None,
                reason='API Pipeline Execution')

        # Build a list of errors
        errors = []
        pipeline = controller.current_pipeline
        execution_errors = execution[0][0].errors
        if execution_errors:
            for key in execution_errors:
                module = pipeline.modules[key]
                msg = '%s: %s' %(module.name, execution_errors[key])
                errors.append(msg)

        # Get the execution log from the controller
        module_outputs = []
        for module_log in controller.log.workflow_execs[0].item_execs:
            # Get the requested output values
            annotations = module_log.annotations
            for annotation in annotations:
                if annotation.key == 'output':
                    module_outputs = annotation.value
                    break

            if module_outputs:
                machine = controller.log.machine_list[0]
                xml_log = serialize(module_log)
                machine_log = serialize(machine)
                break

        # Store the output values in the order they were requested
        outputs = {}
        for m_output in module_outputs:
            if m_output[0] in output_ports:
                outputs[m_output[0]] = m_output[1]

        # Return the dictionary, that will be sent back to the client
        return dict(errors=errors,
                    outputs=outputs,
                    xml_log=xml_log,
                    machine_log=machine_log)
    finally:
        os.unlink(temp_wf)


def module_to_serialized_pipeline(module):
    original_pipeline = module.moduleInfo['pipeline']
    module_id = module.moduleInfo['moduleId']

    pipeline_modules = dict((k, m.do_copy())
                            for k, m in original_pipeline.modules.iteritems())

    pipeline_db_module = pipeline_modules[module_id]

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

    # store output data
    annotation = Annotation(key='annotate_output', value=True)
    pipeline_db_module.add_annotation(annotation)

    # serializing module
    wf = _serialize_module(pipeline_db_module)

    # identify outputs
    connected_outputports = set(
            pipeline_db_module.connected_output_ports.iterkeys())

    return wf, module_id, connected_outputports


def _serialize_module(module):
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


def set_results(module, results):
    # verifying errors
    if results['errors']:
        raise ModuleError(module, '\n'.join(results['errors']))

    module.outputPorts.update(results['outputs'])

    orig_pipeline = module.moduleInfo['pipeline']
    moduleId = module.moduleInfo['moduleId']
    vtType = orig_pipeline.modules[moduleId]

    # including execution logs
    log = results['xml_log']
    exec_ = None
    if (vtType == 'abstraction') or (vtType == 'group'):
        exec_ = unserialize(log, GroupExec)
    elif (vtType == 'module'):
        exec_ = unserialize(log, ModuleExec)

    if exec_ is not None:
        # assigning new ids to existing annotations
        exec_annotations = exec_.annotations
        for i in range(len(exec_annotations)):
            exec_annotations[i].id = module.logging.log.log.id_scope.getNewId(Annotation.vtType)

        parallel_annotation = Annotation(key='parallel_execution', value=True)
        parallel_annotation.id = module.logging.log.log.id_scope.getNewId(Annotation.vtType)
        annotations = [parallel_annotation] + exec_annotations
        exec_.annotations = annotations

        # before adding the execution log, we need to get the machine information
        machine = unserialize(results['machine_log'], Machine)
        machine.id = module.logging.log.log.id_scope.getNewId(Machine.vtType) #assigning new id
        module.logging.log.log.add_machine(machine)

        # recursively add machine information to execution items
        def add_machine_recursive(exec_):
            for i in range(len(exec_.item_execs)):
                if hasattr(exec_.item_execs[i], 'machine_id'):
                    exec_.item_execs[i].machine_id = machine.id
                    vt_type = exec_.item_execs[i].vtType
                    if (vt_type == 'abstraction') or (vt_type == 'group'):
                        add_machine_recursive(exec_.item_execs[i])

        exec_.machine_id = machine.id
        if (vtType == 'abstraction') or (vtType == 'group'):
            add_machine_recursive(exec_)

        module.logging.add_exec(exec_)

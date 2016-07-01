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

from ast import literal_eval
import copy
import sys
from vistrails.core.system import get_vistrails_basic_pkg_id
import vistrails.db.services.io
from vistrails.db.domain import DBOpmProcess, DBOpmArtifact, DBOpmUsed, \
    DBOpmWasGeneratedBy, DBOpmProcessIdCause, DBOpmProcessIdEffect, \
    DBOpmArtifactIdCause, DBOpmArtifactIdEffect, DBOpmRole, DBOpmAccountId, \
    DBOpmAccount, DBOpmAccounts, DBOpmGraph, DBOpmArtifacts, \
    DBOpmDependencies, DBOpmProcesses, DBOpmProcessValue, DBOpmArtifactValue, \
    IdScope, DBGroupExec, DBLoopExec, DBModuleExec, DBOpmOverlaps, DBPort, \
    DBConnection, DBGroup, DBPortSpec, DBOpmWasTriggeredBy, DBFunction, \
    DBParameter
from vistrails.db.services.vistrail import materializeWorkflow

def create_process(item_exec, account, id_scope):
    return DBOpmProcess(id='p' + str(id_scope.getNewId(DBOpmProcess.vtType)),
                        value=DBOpmProcessValue(item_exec),
                        accounts=[DBOpmAccountId(id=account.db_id)])

def create_process_manual(p_str, account, id_scope):
    item_exec = DBModuleExec(id=-1,
                             module_name=p_str,
                             module_id=-1,
                             completed=1,
                             )
    return DBOpmProcess(id='p' + str(id_scope.getNewId(DBOpmProcess.vtType)),
                        value=DBOpmProcessValue(item_exec),
                        accounts=[DBOpmAccountId(id=account.db_id)])

def create_artifact_from_filename(filename, account, id_scope):
    parameter = DBParameter(id=-1,
                            pos=0,
                            type='%s:File' % get_vistrails_basic_pkg_id(),
                            val=filename)
    function = DBFunction(id=-1,
                          name="file",
                          pos=0,
                          parameters=[parameter])
    return DBOpmArtifact(id='a' + str(id_scope.getNewId(DBOpmArtifact.vtType)),
                         value=DBOpmArtifactValue(function),
                         accounts=[DBOpmAccountId(id=account.db_id)])

def create_artifact_from_db_tuple(db_tuple, account, id_scope):
    parameters = []
    for db_str in db_tuple:
        parameter = DBParameter(id=-1,
                                pos=0,
                                type='%s:String' % get_vistrails_basic_pkg_id(),
                                val=db_str)
        parameters.append(parameter)
    function = DBFunction(id=-1,
                          name="dbEntry",
                          pos=0,
                          parameters=parameters)
    return DBOpmArtifact(id='a' + str(id_scope.getNewId(DBOpmArtifact.vtType)),
                         value=DBOpmArtifactValue(function),
                         accounts=[DBOpmAccountId(id=account.db_id)])

def create_artifact_from_function(function, account, id_scope):
    return DBOpmArtifact(id='a' + str(id_scope.getNewId(DBOpmArtifact.vtType)),
                         value=DBOpmArtifactValue(function),
                         accounts=[DBOpmAccountId(id=account.db_id)])

def create_artifact_from_port_spec(port_spec, account, id_scope):
    return DBOpmArtifact(id='a' + str(id_scope.getNewId(DBOpmArtifact.vtType)),
                         value=DBOpmArtifactValue(port_spec),
                         accounts=[DBOpmAccountId(id=account.db_id)])

def create_used(process, artifact, account, id_scope):
    return DBOpmUsed(effect=DBOpmProcessIdEffect(id=process.db_id),
                     role=DBOpmRole(value="in"),
                     cause=DBOpmArtifactIdCause(id=artifact.db_id),
                     accounts=[DBOpmAccountId(id=account.db_id)])

def create_was_generated_by(artifact, process, account, id_scope):
    return DBOpmWasGeneratedBy(effect=DBOpmArtifactIdEffect(id=artifact.db_id),
                               role=DBOpmRole(value="out"),
                               cause=DBOpmProcessIdCause(id=process.db_id),
                               accounts=[DBOpmAccountId(id=account.db_id)])

def create_was_triggered_by(process1, process2, account, id_scope):
    return DBOpmWasTriggeredBy(effect=DBOpmProcessIdEffect(id=process1.db_id),
                               role=DBOpmRole(value="control"),
                               cause=DBOpmProcessIdCause(id=process2.db_id),
                               accounts=[DBOpmAccountId(id=account.db_id)])

def create_account(depth, id_scope):
    account_id = id_scope.getNewId(DBOpmAccount.vtType)
    account = DBOpmAccount(id='acct' + str(account_id),
                           value=str(depth))
    return account

def create_opm(workflow, version, log, reg):
    id_scope = IdScope()
    processes = []
    # conn_artifacts = {}
    artifacts = []
    dependencies = []
    accounts = []
    depth_accounts = {}
    file_artifacts = {}
    db_artifacts = {}

    def do_create_process(workflow, item_exec, account, module_processes):
        process = create_process(item_exec, account, id_scope)
        print 'adding process', process.db_id,
        if hasattr(item_exec, 'db_module_name'):
            print item_exec.db_module_name
        elif hasattr(item_exec, 'db_group_name'):
            print item_exec.db_group_name
        processes.append(process)
        module = workflow.db_modules_id_index[item_exec.db_module_id]
        module_processes[module.db_id] = (module, process)

    def get_package(reg, pkg_identifier, pkg_version=''):
        if pkg_version:
            try:
                return reg.db_packages_identifier_index[(pkg_identifier,
                                                         pkg_version)]
            except:
                print (("Warning: Version '%s' package '%s' "
                        "is not in the registry") %
                       (pkg_version, pkg_identifier))
        # spin and get current package
        for pkg in reg.db_packages:
            if pkg.db_identifier == pkg_identifier:
                break
            pkg = None
        return pkg

    def process_exec(item_exec, workflow, account, upstream_lookup,
                     downstream_lookup, depth, conn_artifacts=None,
                     function_artifacts=None, module_processes=None,
                     in_upstream_artifacts={}, in_downstream_artifacts={},
                     add_extras=False):

        print 'in_upstream:', [(n, x.db_id) 
                               for n, x_list in in_upstream_artifacts.iteritems() for x in x_list]
        print 'in_downstream:', [(n, x.db_id)  
                                 for n, x_list in in_downstream_artifacts.iteritems() for x in x_list]
        # FIXME merge conn_artifacts and function_artifacts
        # problem is that a conn_artifact is OUTPUT while function_artifact
        # is INPUT
        if conn_artifacts is None:
            conn_artifacts = {}
        if function_artifacts is None:
            function_artifacts = {}
        if module_processes is None:
            module_processes = {}
#         while item_exec.vtType == DBLoopExec.vtType:
#             item_exec = item_exec.db_item_execs[0]
        (module, process) = module_processes[item_exec.db_module_id]

        def process_connection(conn):
            source = conn.db_ports_type_index['source']
            source_t = (source.db_moduleId, source.db_name)
            in_cache = False
            print '!!! processing', source_t
            if source_t in conn_artifacts:
                artifact = conn_artifacts[source_t]
                in_cache = True
            else:
                # key off source module and port name
                # get descriptor from registry and then port_spec
                # store port_spec as artifact

                if source.db_moduleId < 0:
                    dest = conn.db_ports_type_index['destination']
                    module = source.db_module
                else:
                    module = workflow.db_modules_id_index[source.db_moduleId]
                print module.db_name, module.db_id

                pkg = get_package(reg, module.db_package, module.db_version)

                if not module.db_namespace:
                    module_namespace = ''
                else:
                    module_namespace = module.db_namespace
                module_desc = \
                    pkg.db_module_descriptors_name_index[(module.db_name,
                                                          module_namespace,
                                                          '')]
                # FIXME make work for module port_specs, too
                # for example, a PythonSource with a given port in 
                # module.db_portSpecs
                port_spec = None
                spec_t = (source.db_name, 'output')
                if spec_t in module.db_portSpecs_name_index:
                    port_spec = module.db_portSpecs_name_index[spec_t]
                while port_spec is None and \
                        module_desc.db_id != reg.db_root_descriptor_id:
                    if spec_t in module_desc.db_portSpecs_name_index:
                        port_spec = module_desc.db_portSpecs_name_index[spec_t]
                    base_id = module_desc.db_base_descriptor_id

                   # inefficient spin through db_packages but we do
                   # not have the descriptors_by_id index that exists
                   # on core.module_registry.ModuleRegistry here
                    module_desc = None
                    for pkg in reg.db_packages:
                        if base_id in pkg.db_module_descriptors_id_index:
                            module_desc = \
                                pkg.db_module_descriptors_id_index[base_id]
                            break
                    if module_desc is None:
                        raise KeyError("Cannot find base descriptor id %d" %
                                       base_id)
                    # pkg = get_package(reg, module_desc.db_package,
                    #                   module_desc.db_package_version)
                    # module_desc = pkg.db_module_descriptors_id_index[base_id]
                if port_spec is None:
                    port_spec = module_desc.db_portSpecs_name_index[spec_t]
                print module_desc.db_name
                
                artifact = \
                    create_artifact_from_port_spec(port_spec, account, id_scope)
                artifacts.append(artifact)
                print 'adding conn_artifact', artifact.db_id, source_t, \
                    source.db_moduleName
                conn_artifacts[source_t] = artifact
            return (artifact, in_cache)

        def process_map(module, found_input_ports, found_output_ports):
            print "*** Processing Map"
            if depth+1 in depth_accounts:
                account = depth_accounts[depth+1]
            else:
                account = create_account(depth+1, id_scope)
                accounts.append(account)
                depth_accounts[depth+1] = account

            # need to have process that extracts artifacts for each iteration
            input_list_artifact = found_input_ports['InputList']
            result_artifact = found_output_ports.get('Result', None)
            # if InputPort or OutputPort is a Connection we cannot do anything
            if (found_input_ports['InputPort'].vtType == DBConnection.vtType or
                found_input_ports['OutputPort'].vtType == DBConnection.vtType):
                return
            input_port_list = \
                literal_eval(found_input_ports['InputPort'].db_parameters[0].db_val)
            output_port = \
                found_input_ports['OutputPort'].db_parameters[0].db_val

            s_process = create_process_manual('Split', account, id_scope)
            processes.append(s_process)
            dependencies.append(create_used(s_process,
                                            input_list_artifact,
                                            account,
                                            id_scope))
            # need to have process that condenses artifacts from each iteration
            if result_artifact is not None:
                j_process = create_process_manual('Join', account, id_scope)
                processes.append(j_process)
            for loop_exec in item_exec.db_loop_execs:
                for loop_iteration in loop_exec.db_loop_iterations:
                    loop_up_artifacts = {}
                    loop_down_artifacts = {}
                    for input_name in input_port_list:
                        port_spec = DBPortSpec(id=-1,
                                               name=input_name,
                                               type='output')
                        s_artifact = \
                            create_artifact_from_port_spec(port_spec, account,
                                                           id_scope)
                        artifacts.append(s_artifact)
                        dependencies.append(create_was_generated_by(s_artifact,
                                                                    s_process,
                                                                    account,
                                                                    id_scope))
                        if input_name not in loop_up_artifacts:
                            loop_up_artifacts[input_name] = []
                        loop_up_artifacts[input_name].append(s_artifact)

                    # process output_port
                    if loop_iteration.db_completed == 1:
                        port_spec = DBPortSpec(id=-1,
                                               name=output_port,
                                               type='output')
                        o_artifact = \
                                create_artifact_from_port_spec(port_spec, account,
                                                               id_scope)
                        artifacts.append(o_artifact)
                        if output_port not in loop_down_artifacts:
                            loop_down_artifacts[output_port] = []
                        loop_down_artifacts[output_port].append(o_artifact)

                    if result_artifact is not None:
                        dependencies.append(create_used(j_process, o_artifact,
                                                        account, id_scope))

                    # now process a loop_exec
                    for child_exec in loop_iteration.db_item_execs:
                        do_create_process(workflow, child_exec, account,
                                          module_processes)
                    for child_exec in loop_iteration.db_item_execs:
                        process_exec(child_exec, workflow, account, upstream_lookup,
                                     downstream_lookup, depth+1, conn_artifacts,
                                     function_artifacts, module_processes,
                                     loop_up_artifacts, loop_down_artifacts, True)

            # need to set Return artifact and connect j_process to it
            if result_artifact is not None:
                dependencies.append(create_was_generated_by(result_artifact,
                                                            j_process,
                                                            account,
                                                            id_scope))

        def process_module_loop(module, found_input_ports, found_output_ports):
            print "*** Processing Module with loops"
            if depth+1 in depth_accounts:
                account = depth_accounts[depth+1]
            else:
                account = create_account(depth+1, id_scope)
                accounts.append(account)
                depth_accounts[depth+1] = account

            # need to have process that extracts artifacts for each iteration
            result_artifacts = [a for r in found_output_ports
                                if found_output_ports[r] is not None
                                for a in found_output_ports[r]]
            s_process = create_process_manual('Split', account, id_scope)
            processes.append(s_process)
            for input_port in found_input_ports:
                for input_name in input_port:
                    dependencies.append(create_used(s_process,
                                                    found_input_ports[input_name],
                                                    account,
                                                    id_scope))
            # need to have process that condenses artifacts from each iteration
            if result_artifacts:
                j_process = create_process_manual('Join', account, id_scope)
                processes.append(j_process)
            for loop_exec in item_exec.db_loop_execs:
                for loop_iteration in loop_exec.db_loop_iterations:
                    loop_up_artifacts = {}
                    loop_down_artifacts = {}
                    for input_port in found_input_ports:
                        for input_name in input_port:
                            port_spec = DBPortSpec(id=-1,
                                                   name=input_name,
                                                   type='output')
                            s_artifact = \
                                create_artifact_from_port_spec(port_spec, account,
                                                               id_scope)
                            artifacts.append(s_artifact)
                            dependencies.append(create_was_generated_by(s_artifact,
                                                                        s_process,
                                                                        account,
                                                                        id_scope))
                            if input_name not in loop_up_artifacts:
                                loop_up_artifacts[input_name] = []
                            loop_up_artifacts[input_name].append(s_artifact)

                    # process output_port
                    if loop_iteration.db_completed == 1:
                        for output_name in found_output_ports:
                            port_spec = DBPortSpec(id=-1,
                                                   name=output_name,
                                                   type='output')
                            o_artifact = \
                                    create_artifact_from_port_spec(port_spec, account,
                                                                   id_scope)
                            artifacts.append(o_artifact)
                            if output_name not in loop_down_artifacts:
                                loop_down_artifacts[output_name] = []
                            loop_down_artifacts[output_name].append(o_artifact)

                            if result_artifacts:
                                dependencies.append(create_used(j_process, o_artifact,
                                                                account, id_scope))

                    # now process a loop_exec
                    for child_exec in loop_iteration.db_item_execs:
                        do_create_process(workflow, child_exec, account,
                                          module_processes)
                    for child_exec in loop_iteration.db_item_execs:
                        process_exec(child_exec, workflow, account, upstream_lookup,
                                     downstream_lookup, depth+1, conn_artifacts,
                                     function_artifacts, module_processes,
                                     loop_up_artifacts, loop_down_artifacts, True)

            # need to set Return artifacts and connect j_process to it
            for result_artifact in result_artifacts:
                dependencies.append(create_was_generated_by(result_artifact,
                                                            j_process,
                                                            account,
                                                            id_scope))

        def process_group(module, found_input_ports, found_output_ports):
            # identify depth and create new account if necessary
            # recurse with new account
            # need to link to upstream and downstream correctly
            workflow = module.db_workflow
            # run the whole upstream construction, etc, using this exec
            # and the group's workflow
            if depth+1 in depth_accounts:
                account = depth_accounts[depth+1]
            else:
                account = create_account(depth+1, id_scope)
                accounts.append(account)
                depth_accounts[depth+1] = account
            process_workflow(workflow, item_exec, account, 
                             out_upstream_artifacts,
                             out_downstream_artifacts, depth+1)            

        def process_port_module(module, found_input_ports, found_output_ports):
            port_name = found_input_ports['name'].db_parameters[0].db_val
            if module.db_name == 'InputPort':
                if port_name in in_upstream_artifacts:
                    for artifact in in_upstream_artifacts[port_name]:
                        dependencies.append(create_used(process, artifact,
                                                        account, id_scope))
            elif module.db_name == 'OutputPort':
                if port_name in in_downstream_artifacts:
                    for artifact in in_downstream_artifacts[port_name]:
                        dependencies.append(create_was_generated_by(artifact,
                                                                    process, 
                                                                    account, 
                                                                    id_scope))

        def process_if_module(module, found_input_ports, found_output_ports):
            print 'processing IFFFF'
            # need to decide which path was taken?
            # check which module was executed, then know which branch was
            # taken?
            true_conn = found_input_ports['TruePort']
            false_conn = found_input_ports['FalsePort']
            true_id = true_conn.db_ports_type_index['source'].db_moduleId
            false_id = false_conn.db_ports_type_index['source'].db_moduleId
            print '$$ TRUE ID:', true_id
            print '$$ FALSE ID:', false_id
            for x,y in module_processes.iteritems():
                print x, ':', y
            if true_id in module_processes:
                cond_process = module_processes[true_id][1]
            elif false_id in module_processes:
                cond_process = module_processes[false_id][1]
            else:
                raise RuntimeError("cannot process if")
            # FIXME: assume true for now
            # eventually need to check which module_id was execed for this
            # current item exec
            dependencies.append(create_was_triggered_by(cond_process,
                                                        process,
                                                        account,
                                                        id_scope))

        if add_extras:
            print '***adding extras'
            out_upstream_artifacts = copy.copy(in_upstream_artifacts)
            out_downstream_artifacts = copy.copy(in_downstream_artifacts)
            for port_name, artifact_list in in_upstream_artifacts.iteritems():
                for artifact in artifact_list:
                    dependencies.append(create_used(process, artifact,
                                                    account, id_scope))
            for port_name, artifact_list in in_downstream_artifacts.iteritems():
                for artifact in artifact_list:
                    # conn_artifacts[(port_name, 'output')] = artifact
                    dependencies.append(create_was_generated_by(artifact,
                                                                process,
                                                                account,
                                                                id_scope))
        else:
            out_upstream_artifacts = {}
            out_downstream_artifacts = {}


        ctrl_flow_pkg = 'org.vistrails.vistrails.control_flow'
        basic_pkg = get_vistrails_basic_pkg_id()
        all_special_ports = {'%s:Map' % ctrl_flow_pkg:
                                 [{'InputPort': False, 
                                   'OutputPort': False, 
                                   'InputList': True,
                                   'FunctionPort': False},
                                  {'Result': True},
                                  process_map],
                             '%s:Group' % basic_pkg:
                                 [{},
                                  {},
                                  process_group],
                             '%s:InputPort' % basic_pkg:
                                 [{'name': False,
                                   'spec': False,
                                   'old_name': False},
                                  {},
                                  process_port_module],
                             '%s:OutputPort' % basic_pkg:
                                 [{'name': False,
                                   'spec': False,
                                   'old_name': False},
                                  {},
                                  process_port_module],
                             '%s:If' % ctrl_flow_pkg:
                                 [{'TruePort': False,
                                   'FalsePort': False},
                                  {},
                                  process_if_module],
                             }
        
        module_desc_str = module.db_package + ':' + module.db_name
        special_ports = all_special_ports.get(module_desc_str, [{}, {}, None])
        found_input_ports = {}
        found_output_ports = {}
        
        # process used_files annotations
        # process generated_tables annotations:
        for annotation in item_exec.db_annotations:
            def process_db_tuple(db_tuple):
                db_tuple = (str(db_tuple[0]),) + db_tuple[1:]
                if db_tuple not in db_artifacts:
                    artifact = create_artifact_from_db_tuple(db_tuple,
                                                             account,
                                                             id_scope)
                    artifacts.append(artifact)
                    db_artifacts[db_tuple] = artifact
                else:
                    artifact = db_artifacts[db_tuple]
                    if int(artifact.db_accounts[0].db_id[4:]) > \
                            int(account.db_id[4:]):
                        artifact.db_accounts[0] = account
                return artifact

            if annotation.db_key == 'used_files':
                used_files = literal_eval(annotation.db_value)
                for fname in used_files:
                    if fname not in file_artifacts:
                        artifact = create_artifact_from_filename(fname,
                                                                 account,
                                                                 id_scope)
                        artifacts.append(artifact)
                        file_artifacts[fname] = artifact
                    else:
                        artifact = file_artifacts[fname]
                        if int(artifact.db_accounts[0].db_id[4:]) > \
                                int(account.db_id[4:]):
                            artifact.db_accounts[0] = account
                    dependencies.append(create_used(process, artifact,
                                                    account, id_scope))
            elif annotation.db_key == 'generated_tables':
                generated_tables = literal_eval(annotation.db_value)
                for db_tuple in generated_tables:
                    artifact = process_db_tuple(db_tuple)
                    dependencies.append(create_was_generated_by(artifact,
                                                                process,
                                                                account,
                                                                id_scope))
            elif annotation.db_key == 'used_tables':
                used_tables = literal_eval(annotation.db_value)
                for db_tuple in used_tables:
                    artifact = process_db_tuple(db_tuple)
                    dependencies.append(create_used(process, artifact,
                                                    account, id_scope))

        # process functions
        for function in module.db_functions:
            # FIXME let found_input_ports, found_output_ports store lists?
            if function.db_name in special_ports[0]:
                if not special_ports[0][function.db_name]:
                    found_input_ports[function.db_name] = function
                    continue
            function_t = (module.db_id, function.db_name)
            if function_t in function_artifacts:
                artifact = function_artifacts[function_t]
                if int(artifact.db_accounts[0].db_id[4:]) > \
                        int(account.db_id[4:]):
                    artifact.db_accounts[0] = account
            else:
                artifact = create_artifact_from_function(function, 
                                                         account,
                                                         id_scope)
                print 'adding artifact', artifact.db_id
                artifacts.append(artifact)
                function_artifacts[function_t] = artifact
            if function.db_name in special_ports[0]:
                found_input_ports[function.db_name] = artifact
            if function.db_name not in out_upstream_artifacts:
                out_upstream_artifacts[function.db_name] = []
            out_upstream_artifacts[function.db_name].append(artifact)
            dependencies.append(create_used(process, artifact, account,
                                            id_scope))

        # process connections
        if module.db_id in upstream_lookup:
            for conns in upstream_lookup[module.db_id].itervalues():
                for conn in conns:
                    dest = conn.db_ports_type_index['destination']
                    if dest.db_name in special_ports[0]:
                        if not special_ports[0][dest.db_name]:
                            found_input_ports[dest.db_name] = conn
                            continue
                    (artifact, in_cache) = process_connection(conn)
                    if dest.db_name in special_ports[0]:
                        found_input_ports[dest.db_name] = artifact
                    if dest.db_name not in out_upstream_artifacts:
                        out_upstream_artifacts[dest.db_name] = []
                    out_upstream_artifacts[dest.db_name].append(artifact)
                    print 'adding dependency (pa)', process.db_id, \
                        artifact.db_id
                    dependencies.append(create_used(process, artifact, 
                                                    account, id_scope))

        if item_exec.db_completed == 1:
            if module.db_id in downstream_lookup:
                # check if everything completed successfully for this?
                for conns in downstream_lookup[module.db_id].itervalues():
                    for conn in conns:
                        source = conn.db_ports_type_index['source']
                        if source.db_name in special_ports[1]:
                            if not special_ports[1][source.db_name]:
                                found_output_ports[source.db_name] = conn
                                continue
                        dest = conn.db_ports_type_index['destination']
                        dest_module = \
                            workflow.db_modules_id_index[dest.db_moduleId]
                        dest_desc_str = dest_module.db_package + ':' + \
                            dest_module.db_name
                        dest_special_ports = all_special_ports.get(dest_desc_str,
                                                                   [{}, {}, None])
                        if dest.db_name in dest_special_ports[0] and \
                                not dest_special_ports[0][dest.db_name]:
                            print 'skipping', dest.db_name
                            continue
                        (artifact, in_cache) = process_connection(conn)
                        if not in_cache:
                            if source.db_name in special_ports[1]:
                                found_output_ports[source.db_name] = artifact
                            if source.db_name not in out_downstream_artifacts:
                                out_downstream_artifacts[source.db_name] = []
                            out_downstream_artifacts[source.db_name].append(artifact)
                            print 'adding dependency (ap)', artifact.db_id, \
                                process.db_id
                            dependencies.append(create_was_generated_by(artifact, 
                                                                        process, 
                                                                        account,
                                                                        id_scope))

        if special_ports[2] is not None:
            special_ports[2](module, found_input_ports, found_output_ports)
        elif item_exec.db_loop_execs:
            # A normal module that is looping internally
            # Probably an automatic list loop
            process_module_loop(module, in_upstream_artifacts, out_upstream_artifacts)

    def process_workflow(workflow, parent_exec, account, upstream_artifacts={},
                         downstream_artifacts={}, depth=0, top_version=False):
        # create process for each module_exec
        # for each module, find parameters and upstream connections
        # tie them in
        # each connection's source port is 
        # associated with a transient data item
        # use wasDerivedBy and used relationships to tie things together
        # check run-time annotations?
        print 'processing workflow', parent_exec

        upstream_lookup = {}
        downstream_lookup = {}
        for connection in workflow.db_connections:
            source = connection.db_ports_type_index['source']
            if source.db_moduleId not in downstream_lookup:
                downstream_lookup[source.db_moduleId] = {}
            if source.db_name not in downstream_lookup[source.db_moduleId]:
                downstream_lookup[source.db_moduleId][source.db_name] = []
            downstream_lookup[source.db_moduleId][source.db_name].append(connection)

            dest = connection.db_ports_type_index['destination']
            if dest.db_moduleId not in upstream_lookup:
                upstream_lookup[dest.db_moduleId] = {}
            if dest.db_name not in upstream_lookup[dest.db_moduleId]:
                upstream_lookup[dest.db_moduleId][dest.db_name] = []
            upstream_lookup[dest.db_moduleId][dest.db_name].append(connection)

        conn_artifacts = {}
        function_artifacts = {}
        module_processes = {}
        print '  upstream_lookup:'
        lookup = upstream_lookup
        for id, name_list in lookup.iteritems():
            print '    ', id, ':', name_list.keys()

        print '  downstream_lookup:'
        lookup = downstream_lookup
        for id, name_list in lookup.iteritems():
            print '    ', id, ':', name_list.keys()
            
        # print '  upstream_lookup:', upstream_lookup
        # print '  downstream_lookup:', downstream_lookup
        if top_version:
            for workflow_exec in parent_exec.db_workflow_execs:
                if workflow_exec.db_parent_version != version:
                    continue
                conn_artifacts = {}
                function_artifacts = {}
                module_processes = {}
                upstream_artifacts = {}
                downstream_artifacts = {}
                for item_exec in workflow_exec.db_item_execs:
                    do_create_process(workflow, item_exec, account, 
                                      module_processes)
                for item_exec in workflow_exec.db_item_execs:
                    process_exec(item_exec, workflow, account,
                                 upstream_lookup, downstream_lookup,
                                 depth, conn_artifacts, function_artifacts,
                                 module_processes,
                                 upstream_artifacts, downstream_artifacts)
        else:
            for item_exec in parent_exec.db_item_execs:
                do_create_process(workflow, item_exec, account, 
                                  module_processes)
            for item_exec in parent_exec.db_item_execs:
                process_exec(item_exec, workflow, account, upstream_lookup,
                             downstream_lookup, depth, conn_artifacts,
                             function_artifacts, module_processes,
                             upstream_artifacts, downstream_artifacts)
                
    account_id = id_scope.getNewId(DBOpmAccount.vtType)
    account = DBOpmAccount(id='acct' + str(account_id),
                           value=str(0))
    accounts.append(account)
    depth_accounts[0] = account
    process_workflow(workflow, log, account, {}, {}, 0, True) 

    #print processes
    #print dependencies
    max_depth = max(depth_accounts)
    def add_finer_depths(objs, exclude_groups=False, exclude_deps=False, 
                         p_ids=set()):
        new_p_ids = []
        for obj in objs:
            can_update=True
            if exclude_groups:
                if obj.db_value.db_value.vtType == DBGroupExec.vtType:
                    new_p_ids.append(obj.db_id)
                    can_update = False
                elif obj.db_value.db_value.vtType == DBModuleExec.vtType and \
                        len(obj.db_value.db_value.db_loop_execs) > 0:
                    new_p_ids.append(obj.db_id)
                    can_update = False
                
            if exclude_deps:
                if ((obj.vtType == DBOpmWasGeneratedBy.vtType and
                     obj.db_cause.db_id in p_ids) or 
                    (obj.vtType == DBOpmUsed.vtType and
                     obj.db_effect.db_id in p_ids)):
                    can_update = False
            if can_update:
                min_depth = int(obj.db_accounts[0].db_id[4:])
                for i in xrange(min_depth+1, max_depth+1):
                    obj.db_add_account(DBOpmAccountId(id='acct' + str(i)))
        return new_p_ids

    # FIXME: also exclude group dependencies (used, wasGeneratedBy)...
    p_ids = add_finer_depths(processes, True)
    print p_ids
    add_finer_depths(artifacts)
    add_finer_depths(dependencies, False, True, set(p_ids))

    overlaps = []
    for i in xrange(max_depth+1):
        for j in xrange(i+1, max_depth+1):
            ids = [DBOpmAccountId(id='acct' + str(i)),
                   DBOpmAccountId(id='acct' + str(j))]
            overlaps.append(DBOpmOverlaps(opm_account_ids=ids))

    opm_graph = DBOpmGraph(accounts=DBOpmAccounts(accounts=accounts,
                                                  opm_overlapss=overlaps),
                           processes=DBOpmProcesses(processs=processes),
                           artifacts=\
                               DBOpmArtifacts(artifacts=artifacts),
                           dependencies=\
                               DBOpmDependencies(dependencys=dependencies),
                           )
    return opm_graph

def add_module_descriptor_index(registry):
    registry.db_module_descriptors_id_index = {}
    for package in registry.db_packages:
        for module_descriptor in package.db_module_descriptors:
            registry.db_module_descriptors_id_index[module_descriptor.db_id] =\
                module_descriptor

def add_group_portSpecs_index(workflow):
    basic_pkg = get_vistrails_basic_pkg_id()
    def process_group(group):
        def get_port_name(module):
            port_name = None
            for function in module.db_functions:
                if function.db_name == 'name':
                    port_name = function.db_parameters[0].db_val
            return port_name
        g_workflow = group.db_workflow
        group.db_portSpecs_name_index = {}
        for module in g_workflow.db_modules:
            if module.db_name == 'InputPort' and module.db_package == basic_pkg:
                port_name = get_port_name(module)
                # FIXME add sigstring to DBPortSpec
                group.db_portSpecs_name_index[(port_name, 'input')] = \
                    DBPortSpec(id=-1,
                               name=port_name,
                               type='input')
            elif module.db_name == 'OutputPort' and \
                    module.db_package == basic_package:
                port_name = get_port_name(module)
                # FIXME add sigstring to DBPortSpec
                group.db_portSpecs_name_index[(port_name, 'output')] = \
                    DBPortSpec(id=-1,
                               name=port_name,
                               type='output')
            elif module.db_name == 'Group' and module.db_package == basic_pkg:
                process_group(module)

    for module in workflow.db_modules:
        if module.vtType == DBGroup.vtType:
            process_group(module)

def create_opm_from_vistrail(vistrail, version, log, registry):
    workflow = materializeWorkflow(vistrail, version)
    add_group_portSpecs_index(workflow)
    add_module_descriptor_index(registry)
    return create_opm(workflow, version, log, registry)

def run(vistrail_xml, version, log_xml, registry_xml, output_fname):
    from vistrails.db.persistence import DAOList

    vistrail = vistrails.db.services.io.open_vistrail_from_xml(vistrail_xml)
    log = vistrails.db.services.io.open_log_from_xml(log_xml)
    registry = vistrails.db.services.io.open_registry_from_xml(registry_xml)
    opm_graph = create_opm_from_vistrail(vistrail, int(version), log, registry)
    dao_list = DAOList()
    dao_list.save_to_xml(opm_graph, output_fname, {})

if __name__ == '__main__':
    if len(sys.argv) < 5:
        print "Usage: python %s <vt_xml> <version> <log_xml> <registry_xml> <out_xml>" % sys.argv[0]
        sys.exit(1)
    run(*sys.argv[1:])
                    

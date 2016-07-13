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

import copy
import sys
import os
import vistrails.db.services.io
from vistrails.db.domain import DBProvDocument, DBProvEntity, DBProvActivity, \
    DBProvAgent, DBProvGeneration, DBProvUsage, DBProvAssociation, \
    DBVtConnection, DBRefProvEntity, DBRefProvPlan, DBRefProvActivity, \
    DBRefProvAgent, DBIsPartOf, IdScope, DBGroupExec, DBLoopExec, DBLoopIteration, \
    DBModuleExec, DBWorkflowExec, DBFunction, DBParameter, DBGroup, DBAbstraction
from vistrails.db.services.vistrail import materializeWorkflow

def create_prov_document(entities, activities, agents, connections, usages,
                         generations, associations):
    return DBProvDocument(prov_entitys=entities,
                          prov_activitys=activities,
                          prov_agents=agents,
                          vt_connections=connections,
                          prov_usages=usages,
                          prov_generations=generations,
                          prov_associations=associations)

def create_prov_entity_from_workflow(id_scope, workflow):
    return DBProvEntity(id='e' + str(id_scope.getNewId(DBProvEntity.vtType)),
                        vt_id=workflow.db_id,
                        prov_type='prov:Plan',
                        prov_label=workflow._db_name,
                        prov_value=None,
                        vt_type='vt:workflow',
                        vt_desc=None,
                        vt_package=None,
                        vt_version=workflow._db_version,
                        vt_cache=None,
                        vt_location_x=None,
                        vt_location_y=None,
                        is_part_of=None)

def create_prov_entity_from_module(id_scope, module, is_part_of):

    # getting module label defined by the user
    desc = None
    for db_annotation in module.db_annotations:
        if db_annotation._db_key == '__desc__':
            desc = db_annotation._db_value
            break
    
    return DBProvEntity(id='e' + str(id_scope.getNewId(DBProvEntity.vtType)),
                        vt_id=module._db_id,
                        prov_type='prov:Plan',
                        prov_label=module.db_name,
                        prov_value=None,
                        vt_type='vt:module',
                        vt_desc=desc,
                        vt_package=module.db_package,
                        vt_version=module.db_version,
                        vt_cache=module.db_cache,
                        vt_location_x=module.db_location._db_x,
                        vt_location_y=module.db_location._db_y,
                        is_part_of=is_part_of)
    
def create_is_part_of(prov_object):
    return DBIsPartOf(prov_ref=prov_object._db_id)
    
def create_prov_entity_from_group(id_scope, group, is_part_of):

    # getting group label defined by the user
    desc = None
    for db_annotation in group.db_annotations:
        if db_annotation._db_key == '__desc__':
            desc = db_annotation._db_value
            break
    
    return DBProvEntity(id='e' + str(id_scope.getNewId(DBProvEntity.vtType)),
                        vt_id=group.db_id,
                        prov_type='prov:Plan',
                        prov_label=group.db_name,
                        prov_value=None,
                        vt_type='vt:group',
                        vt_desc=desc,
                        vt_package=None,
                        vt_version=None,
                        vt_cache=group.db_cache,
                        vt_location_x=group.db_location._db_x,
                        vt_location_y=group.db_location._db_y,
                        is_part_of=is_part_of)
    
def create_prov_entity_from_abstraction(id_scope, abstraction, is_part_of):

    # getting abstraction label defined by the user
    desc = None
    for db_annotation in abstraction.db_annotations:
        if db_annotation._db_key == '__desc__':
            desc = db_annotation._db_value
            break
    
    return DBProvEntity(id='e' + str(id_scope.getNewId(DBProvEntity.vtType)),
                        vt_id=abstraction.db_id,
                        prov_type='prov:Plan',
                        prov_label=abstraction.db_name,
                        prov_value=None,
                        vt_type='vt:subworkflow',
                        vt_desc=desc,
                        vt_package=None,
                        vt_version=None,
                        vt_cache=abstraction.db_cache,
                        vt_location_x=abstraction.db_location._db_x,
                        vt_location_y=abstraction.db_location._db_y,
                        is_part_of=is_part_of)
    
def create_prov_entity_from_function(id_scope, function):
    values = []
    types = []
    aliases = []
    for parameter in function._db_parameters:
        values.append(str(parameter._db_val))
        types.append(str(parameter._db_type))
        if parameter._db_alias:
            aliases.append(parameter._db_alias)
        else:
            aliases.append('None')
        
    value = ''
    type = ''
    alias = None
    if len(values) == 1:
        value = values[0]
        type = types[0]
        alias = aliases[0]
    elif len(values) > 1:
        value = '(' + ','.join(values) + ')'
        type = '(' + ','.join(types) + ')'
        alias = '(' + ','.join(aliases) + ')'
    
    return DBProvEntity(id='e' + str(id_scope.getNewId(DBProvEntity.vtType)),
                        vt_id=function.db_id,
                        prov_type='vt:data',
                        prov_label=function.db_name,
                        prov_value=value,
                        vt_type=type,
                        vt_desc=alias,
                        vt_package=None,
                        vt_version=None,
                        vt_cache=None,
                        vt_location_x=None,
                        vt_location_y=None,
                        is_part_of=None)
    
def create_prov_entity_for_data(id_scope, conn):
    return DBProvEntity(id='e' + str(id_scope.getNewId(DBProvEntity.vtType)),
                        vt_id=conn.db_id,
                        prov_type='vt:data',
                        prov_label=None,
                        prov_value=None,
                        vt_type=None,
                        vt_desc=None,
                        vt_package=None,
                        vt_version=None,
                        vt_cache=None,
                        vt_location_x=None,
                        vt_location_y=None,
                        is_part_of=None)
    
def create_vt_connection(id_scope, source, dest, mapping):
    return DBVtConnection(id='c' + str(id_scope.getNewId(DBVtConnection.vtType)),
                          vt_source=mapping[source._db_moduleId]._db_id,
                          vt_dest=mapping[dest._db_moduleId]._db_id,
                          vt_source_port=source.db_name,
                          vt_dest_port=dest.db_name,
                          vt_source_signature=source._db_signature,
                          vt_dest_signature=dest._db_signature)
    
def create_prov_agent_from_user(id_scope, user):
    return DBProvAgent(id='ag' + str(id_scope.getNewId(DBProvAgent.vtType)),
                       vt_id=None,
                       prov_type='prov:Person',
                       prov_label=user,
                       vt_machine_os=None,
                       vt_machine_architecture=None,
                       vt_machine_processor=None,
                       vt_machine_ram=None)
    
def create_prov_agent_from_machine(id_scope, machine):
    return DBProvAgent(id='ag' + str(id_scope.getNewId(DBProvAgent.vtType)),
                       vt_id=machine.db_id,
                       prov_type='vt:machine',
                       prov_label=machine.db_name,
                       vt_machine_os=machine._db_os,
                       vt_machine_architecture=machine._db_architecture,
                       vt_machine_processor=machine._db_processor,
                       vt_machine_ram=machine._db_ram)
    
def create_prov_association(prov_activity, prov_agent, prov_entity):
    ref_prov_activity = DBRefProvActivity(prov_ref=prov_activity._db_id)
    ref_prov_agent = DBRefProvAgent(prov_ref=prov_agent._db_id)
    ref_prov_entity = DBRefProvPlan(prov_ref=prov_entity._db_id)
    
    return DBProvAssociation(prov_activity=ref_prov_activity,
                             prov_agent=ref_prov_agent,
                             prov_plan=ref_prov_entity,
                             prov_role=None)
    
def create_prov_activity_from_wf_exec(id_scope, wf_exec):
    return DBProvActivity(id='a' + str(id_scope.getNewId(DBProvActivity.vtType)),
                          vt_id=wf_exec._db_id,
                          startTime=wf_exec._db_ts_start,
                          endTime=wf_exec._db_ts_end,
                          vt_type='vt:wf_exec',
                          vt_cached=None,
                          vt_completed=wf_exec._db_completed,
                          vt_machine_id=None,
                          vt_error=None,
                          is_part_of=None)
    
def create_prov_activity_from_exec(id_scope, module_exec, machine_id, is_part_of):
    type = ''
    if module_exec.vtType == DBModuleExec.vtType:
        type = 'vt:module_exec'
        cached = module_exec._db_cached
    elif module_exec.vtType == DBGroupExec.vtType:
        type = 'vt:group_exec'
        cached = module_exec._db_cached
    elif module_exec.vtType == DBLoopIteration.vtType:
        type = 'vt:loop_iteration'
        cached = 0
    else:
        # something is wrong...
        raise Exception('Unknown exec type: %s' % module_exec.vtType)
    return DBProvActivity(id='a' + str(id_scope.getNewId(DBProvActivity.vtType)),
                          vt_id=module_exec._db_id,
                          startTime=module_exec._db_ts_start,
                          endTime=module_exec._db_ts_end,
                          vt_type=type,
                          vt_cached=cached,
                          vt_completed=module_exec._db_completed,
                          vt_machine_id=machine_id,
                          vt_error=module_exec._db_error,
                          is_part_of=is_part_of)
    
def create_prov_usage(prov_activity, prov_entity):
    ref_prov_activity = DBRefProvActivity(prov_ref=prov_activity._db_id)
    ref_prov_entity = DBRefProvEntity(prov_ref=prov_entity._db_id)
    
    return DBProvUsage(prov_activity=ref_prov_activity,
                       prov_entity=ref_prov_entity,
                       prov_role=None)
    
def create_prov_generation(prov_entity, prov_activity):
    ref_prov_entity = DBRefProvEntity(prov_ref=prov_entity._db_id)
    ref_prov_activity = DBRefProvActivity(prov_ref=prov_activity._db_id)
    
    return DBProvGeneration(prov_entity=ref_prov_entity,
                            prov_activity=ref_prov_activity,
                            prov_role=None)

def create_prov(workflow, version, log):
    id_scope = IdScope()
    entities = []
    activities = []
    agents = []
    connections = []
    usages = []
    generations = []
    associations = []
    
    # mapping between VT ids and PROV objects
    entities_map = {}
    agents_map = {}
    
    # mapping between module ids and their functions
    module_functions = {}
    
    # mapping between module ids and module objects
    module_list = {}
    
    # mapping between module ids and source connections
    source_conn = {}
    
    # mapping between module ids and destination connections
    dest_conn = {}
    
    # mapping between connection ids and PROV entities for data
    prov_data_conn = {}
    
    # mapping between function ids and their PROV entities
    prov_functions = {}
    
    # mapping of machine ids to corresponding PROV agents
    machines = {}
    
    ############################################################################
    def get_modules_and_conn(prov_workflow, workflow):
        
        # modules
        for module in workflow._db_modules:
#            print "Entity name:", module.name
#            print module.id

            module_list[module._db_id] = module
            
            # group
            if module.vtType == DBGroup.vtType:
                vt_part = create_is_part_of(prov_workflow)
                prov_group = create_prov_entity_from_group(id_scope=id_scope,
                                                           group=module,
                                                           is_part_of=vt_part)
                entities_map[module._db_id] = prov_group
                entities.append(prov_group)
                get_modules_and_conn(prov_group, module.db_workflow)
            
            # abstraction (subworkflow)
            elif module.vtType == DBAbstraction.vtType:
                vt_part = create_is_part_of(prov_workflow)
                prov_abstraction = create_prov_entity_from_abstraction(id_scope=id_scope,
                                                                       abstraction=module,
                                                                       is_part_of=vt_part)
                entities_map[module._db_id] = prov_abstraction
                entities.append(prov_abstraction)
                #get_modules_and_conn(prov_abstraction, module.db_workflow)
            
            # module
            else:
                vt_part = create_is_part_of(prov_workflow)
                prov_module = create_prov_entity_from_module(id_scope=id_scope,
                                                             module=module,
                                                             is_part_of=vt_part)
                entities_map[module._db_id] = prov_module
                entities.append(prov_module)

            module_functions[module._db_id] = module._db_functions
            for function in module._db_functions:
                prov_data = create_prov_entity_from_function(id_scope, function)
                prov_functions[function.db_id] = prov_data
        
        # connections
        for conn in workflow._db_connections:
            # storing information about connections
            # used to create entities for input and output data
            source = conn.db_ports_type_index['source']
            dest = conn.db_ports_type_index['destination']
            if not source_conn.has_key(source._db_moduleId):
                source_conn[source._db_moduleId] = []
            if not dest_conn.has_key(dest._db_moduleId):
                dest_conn[dest._db_moduleId] = []
            source_conn[source._db_moduleId].append(conn)
            dest_conn[dest._db_moduleId].append(conn)
            
            prov_data = create_prov_entity_for_data(id_scope, conn)
            prov_data_conn[conn.db_id] = [prov_data, False]
            
            vt_connection = create_vt_connection(id_scope, source, dest, entities_map)
            connections.append(vt_connection)
            
        return True
    ############################################################################

    def get_execs(exec_, parent_exec, prov_agent):

        # module or group execution
        if exec_.vtType != DBLoopExec.vtType:
            
#            print "Exec name:", exec_.module_name
#            print exec_.module_id

            # machine (PROV agent)
            machine_id = None
#            prov_machine = machines[exec_.machine_id][0]
#            machine_id = prov_machine._db_id
#            if not machines[exec_.machine_id][1]:
#                agents.append(prov_machine)
#                machines[exec_.machine_id][1] = True
            
            # PROV activity
            vt_part = create_is_part_of(parent_exec)
            prov_activity = create_prov_activity_from_exec(id_scope,
                                                           exec_,
                                                           machine_id,
                                                           vt_part)
            
            activities.append(prov_activity)

            if exec_.vtType != DBLoopIteration.vtType:
                try:
                    functions = module_functions[exec_._db_module_id]
                except Exception:
                    return True

                for function in functions:
                    prov_data = prov_functions[function.db_id]

                    prov_usage = create_prov_usage(prov_activity, prov_data)
                    usages.append(prov_usage)

                if dest_conn.has_key(exec_._db_module_id):
                    connections = dest_conn[exec_._db_module_id]
                    for connection in connections:
                        prov_input_data, inserted = prov_data_conn[connection.db_id]
                        if not inserted:
                            entities.append(prov_input_data)
                            prov_data_conn[connection.db_id][1] = True

                        prov_usage = create_prov_usage(prov_activity, prov_input_data)
                        usages.append(prov_usage)

                if (prov_activity._db_vt_error is None) or (prov_activity._db_vt_error == ''):
                    if source_conn.has_key(exec_._db_module_id):
                        connections = source_conn[exec_._db_module_id]
                        for connection in connections:
                            prov_output_data, inserted = prov_data_conn[connection.db_id]
                            if not inserted:
                                entities.append(prov_output_data)
                                prov_data_conn[connection.db_id][1] = True

                            prov_generation = create_prov_generation(prov_output_data, prov_activity)
                            generations.append(prov_generation)

                # PROV entity associated
                prov_module_entity = entities_map[exec_._db_module_id]
                prov_association = create_prov_association(prov_activity, prov_agent, prov_module_entity)
                associations.append(prov_association)
            
            if exec_.vtType == DBModuleExec.vtType:
                for loop_exec in exec_.loop_execs:
                    get_execs(loop_exec, prov_activity, prov_agent)
            elif exec_.vtType in [DBGroupExec.vtType, DBLoopIteration.vtType]:
                for item in exec_.item_execs:
                    get_execs(item, prov_activity, prov_agent)
            else:
                # something is wrong...
                pass
            
        # loop execution
        elif exec_.vtType == DBLoopExec.vtType:
            # here, the parent execution is related to the ControlFlow:Map module
            # TODO: should get the input values from Map, and create Function +
            # Parameter?
            for iter_exec in exec_.loop_iterations:
                get_execs(iter_exec, parent_exec, prov_agent)

        else:
            # something is wrong...
            pass
        
        return True
    ############################################################################
    
    # workflow
    prov_workflow = create_prov_entity_from_workflow(id_scope, workflow)
    entities_map[workflow.db_id] = prov_workflow
    entities.append(prov_workflow)
    
    # getting modules and connections 
    get_modules_and_conn(prov_workflow, workflow)
    
    # storing input data
    for id in prov_functions:
        entities.append(prov_functions[id])

    # executions
    for exec_ in log._db_workflow_execs:
        if exec_._db_parent_version != version:
            continue
        prov_agent = None
        if exec_._db_user not in agents_map:
            prov_agent = create_prov_agent_from_user(id_scope, exec_._db_user)
            agents_map[exec_._db_user] = prov_agent
            agents.append(prov_agent)
        else:
            prov_agent = agents_map[exec_._db_user]
        
        # machines
        for machine in exec_.machine_list:
            if machine.db_id not in machines:
                machines[machine.db_id] = (create_prov_agent_from_machine(id_scope, machine), False)

        # creating PROV activity
        prov_activity = create_prov_activity_from_wf_exec(id_scope, exec_)
        activities.append(prov_activity)
        
        # creating association with PROV entity
        prov_association = create_prov_association(prov_activity, prov_agent, prov_workflow)
        
        for item in exec_._db_item_execs:
            get_execs(item, prov_activity, prov_agent)
    
    # PROV Document
    return create_prov_document(entities=entities,
                                activities=activities,
                                agents=agents,
                                connections=connections,
                                usages=usages,
                                generations=generations,
                                associations=associations)
    
def add_group_portSpecs_index(workflow):
    basic_pkg = get_vistrails_basic_pkg_id()
    def process_group(group):
        def get_port_name(module):
            port_name = None
            for function in module._db_functions:
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
                    module.db_package == basic_pkg:
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
    
def create_prov_from_vistrail(vistrail, version, log):
    workflow = materializeWorkflow(vistrail, version)
    add_group_portSpecs_index(workflow)
    return create_prov(workflow, version, log)
    
def run(vistrail_xml, version, log_xml, output_fname):
    from vistrails.db.persistence import DAOList
    from vistrails.core.vistrail.vistrail import Vistrail
    import vistrails.db.services.io
    
    vistrail = vistrails.db.services.io.open_vistrail_from_xml(vistrail_xml)
    log = vistrails.db.services.io.open_log_from_xml(log_xml, was_appended=True)
    version_id = vistrail.db_get_actionAnnotation_by_key((Vistrail.TAG_ANNOTATION, version)).db_action_id
    prov_document = create_prov_from_vistrail(vistrail, int(version_id), log)
    dao_list = DAOList()
    tags = {'xmlns:prov': 'http://www.w3.org/ns/prov#',
            'xmlns:dcterms': 'http://purl.org/dc/terms/',
            'xmlns:vt': 'http://www.vistrails.org/registry.xsd',
            }
    dao_list.save_to_xml(prov_document, output_fname, tags)

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print "Usage: python %s <vt_xml> <version> <log_xml> <out_xml>" % sys.argv[0]
        sys.exit(1)
    run(*sys.argv[1:])


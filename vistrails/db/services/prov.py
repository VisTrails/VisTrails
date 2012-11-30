###############################################################################
##
## Copyright (C) 2011-2012, NYU-Poly.
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
import db.services.io
from db.domain import DBProvDocument, DBProvEntity, DBProvActivity, \
    DBProvAgent, DBProvGeneration, DBProvUsage, DBProvAssociation, \
    DBVtConnection, DBRefProvEntity, DBRefProvPlan, DBRefProvActivity, \
    DBRefProvAgent, DBIsPartOf, IdScope, DBGroupExec, DBLoopExec, DBModuleExec, \
    DBWorkflowExec, DBFunction, DBParameter
from db.services.vistrail import materializeWorkflow

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
                        vt_id=workflow.id,
                        prov_type='prov:Plan',
                        prov_label=workflow.name,
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
    for db_annotation in module.annotations:
        if db_annotation._db_key == '__desc__':
            desc = db_annotation._db_value
            break
    
    return DBProvEntity(id='e' + str(id_scope.getNewId(DBProvEntity.vtType)),
                        vt_id=module.id,
                        prov_type='prov:Plan',
                        prov_label=module.name,
                        prov_value=None,
                        vt_type='vt:module',
                        vt_desc=desc,
                        vt_package=module.package,
                        vt_version=module.version,
                        vt_cache=module.cache,
                        vt_location_x=module.location._db_x,
                        vt_location_y=module.location._db_y,
                        is_part_of=is_part_of)
    
def create_is_part_of(prov_object):
    return DBIsPartOf(prov_ref=prov_object._db_id)
    
def create_prov_entity_from_group(id_scope, group, is_part_of):

    # getting group label defined by the user
    desc = None
    for db_annotation in group.annotations:
        if db_annotation._db_key == '__desc__':
            desc = db_annotation._db_value
            break
    
    return DBProvEntity(id='e' + str(id_scope.getNewId(DBProvEntity.vtType)),
                        vt_id=group.id,
                        prov_type='prov:Plan',
                        prov_label=group.name,
                        prov_value=None,
                        vt_type='vt:group',
                        vt_desc=desc,
                        vt_package=None,
                        vt_version=None,
                        vt_cache=group.cache,
                        vt_location_x=group.location._db_x,
                        vt_location_y=group.location._db_y,
                        is_part_of=is_part_of)
    
def create_prov_entity_from_abstraction(id_scope, abstraction, is_part_of):

    # getting abstraction label defined by the user
    desc = None
    for db_annotation in abstraction.annotations:
        if db_annotation._db_key == '__desc__':
            desc = db_annotation._db_value
            break
    
    return DBProvEntity(id='e' + str(id_scope.getNewId(DBProvEntity.vtType)),
                        vt_id=abstraction.id,
                        prov_type='prov:Plan',
                        prov_label=abstraction.name,
                        prov_value=None,
                        vt_type='vt:subworkflow',
                        vt_desc=desc,
                        vt_package=None,
                        vt_version=None,
                        vt_cache=abstraction.cache,
                        vt_location_x=abstraction.location._db_x,
                        vt_location_y=abstraction.location._db_y,
                        is_part_of=is_part_of)
    
def create_prov_entity_from_function(id_scope, function):
    values = []
    types = []
    aliases = []
    for parameter in function.parameters:
        values.append(parameter.strValue)
        types.append(parameter.typeStr)
        if parameter.alias:
            aliases.append(parameter.alias)
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
                        vt_id=function.id,
                        prov_type='vt:input_data',
                        prov_label=function.name,
                        prov_value=value,
                        vt_type=type,
                        vt_desc=alias,
                        vt_package=None,
                        vt_version=None,
                        vt_cache=None,
                        vt_location_x=None,
                        vt_location_y=None,
                        is_part_of=None)
    
def create_vt_connection(id_scope, source, dest, mapping):
    return DBVtConnection(id='c' + str(id_scope.getNewId(DBVtConnection.vtType)),
                          vt_source=mapping[source.moduleId]._db_id,
                          vt_dest=mapping[dest.moduleId]._db_id,
                          vt_source_port=source.name,
                          vt_dest_port=dest.name,
                          vt_source_signature=source.sigstring,
                          vt_dest_signature=dest.sigstring)
    
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
                       vt_id=machine.id,
                       prov_type='vt:machine',
                       prov_label=machine.name,
                       vt_machine_os=machine.os,
                       vt_machine_architecture=machine.architecture,
                       vt_machine_processor=machine.processor,
                       vt_machine_ram=machine.ram)
    
def create_prov_association(prov_activity, prov_agent, prov_entity):
    ref_prov_activity = DBRefProvActivity(prov_ref=prov_activity._db_id)
    ref_prov_agent = DBRefProvAgent(prov_ref=prov_agent._db_id)
    ref_prov_entity = DBRefProvPlan(prov_ref=prov_entity._db_id)
    
    return DBProvAssociation(prov_activity=ref_prov_activity,
                             prov_agent=ref_prov_agent,
                             prov_plan=ref_prov_entity,
                             prov_role='executor')
    
def create_prov_activity_from_wf_exec(id_scope, wf_exec):
    return DBProvActivity(id='a' + str(id_scope.getNewId(DBProvActivity.vtType)),
                          vt_id=wf_exec.id,
                          startTime=wf_exec.ts_start,
                          endTime=wf_exec.ts_end,
                          vt_type='vt:wf_exec',
                          vt_cached=None,
                          vt_completed=wf_exec.completed,
                          vt_machine_id=None,
                          vt_error=None,
                          is_part_of=None)
    
def create_prov_activity_from_exec(id_scope, module_exec, machine_id, is_part_of):
    type = ''
    if module_exec.vtType == DBModuleExec.vtType:
        type = 'vt:module_exec'
    elif module_exec.vtType == DBGroupExec.vtType:
        type = 'vt:group_exec'
    else:
        # something is wrong...
        pass
    return DBProvActivity(id='a' + str(id_scope.getNewId(DBProvActivity.vtType)),
                          vt_id=module_exec.id,
                          startTime=module_exec.ts_start,
                          endTime=module_exec.ts_end,
                          vt_type=type,
                          vt_cached=module_exec.cached,
                          vt_completed=module_exec.completed,
                          vt_machine_id=machine_id,
                          vt_error=module_exec.error,
                          is_part_of=is_part_of)
    
def create_prov_usage(prov_activity, prov_entity):
    ref_prov_activity = DBRefProvActivity(prov_ref=prov_activity._db_id)
    ref_prov_entity = DBRefProvEntity(prov_ref=prov_entity._db_id)
    
    return DBProvUsage(prov_activity=ref_prov_activity,
                       prov_entity=ref_prov_entity,
                       prov_role='consumer')

def create_prov(workflow, version, log, reg):
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
    
    # mapping between function ids and their PROV entities
    prov_functions = {}
    
    # mapping of machine ids to corresponding PROV agents
    machines = {}
    
    ############################################################################
    def get_modules_and_conn(prov_workflow, workflow):
        
        # modules
        for module in workflow.module_list:
#            print "Entity name:", module.name
#            print module.id
            
            # group
            if module.is_group():
                vt_part = create_is_part_of(prov_workflow)
                prov_group = create_prov_entity_from_group(id_scope=id_scope,
                                                           group=module,
                                                           is_part_of=vt_part)
                entities_map[module.id] = prov_group
                entities.append(prov_group)
                get_modules_and_conn(prov_group, module.workflow)
            
            # abstraction (subworkflow)
            elif module.is_abstraction():
                vt_part = create_is_part_of(prov_workflow)
                prov_abstraction = create_prov_entity_from_abstraction(id_scope=id_scope,
                                                                       abstraction=module,
                                                                       is_part_of=vt_part)
                entities_map[module.id] = prov_abstraction
                entities.append(prov_abstraction)
                get_modules_and_conn(prov_abstraction, module.pipeline)
            
            # module
            else:
                vt_part = create_is_part_of(prov_workflow)
                prov_module = create_prov_entity_from_module(id_scope=id_scope,
                                                             module=module,
                                                             is_part_of=vt_part)
                entities_map[module.id] = prov_module
                entities.append(prov_module)
                
            module_functions[module.id] = module.functions
            for function in module.functions:
                prov_data = create_prov_entity_from_function(id_scope, function)
                prov_functions[function.id] = prov_data
        
        # connections
        for conn in workflow.connection_list:
            vt_connection = create_vt_connection(id_scope, conn.source, conn.dest, entities_map)
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
            
            functions = module_functions[exec_.module_id]
            for function in functions:
                prov_data = prov_functions[function.id]
                
                prov_usage = create_prov_usage(prov_activity, prov_data)
                usages.append(prov_usage)
            
            activities.append(prov_activity)
            
            # PROV entity associated
            prov_module_entity = entities_map[exec_.module_id]
            prov_association = create_prov_association(prov_activity, prov_agent, prov_module_entity)
            associations.append(prov_association)
            
            if exec_.vtType == DBModuleExec.vtType:
                for loop_exec in exec_.loop_execs:
                    get_execs(loop_exec, prov_activity, prov_agent)
            elif exec_.vtType == DBGroupExec.vtType:
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
            
            # there must be only one item exec per loop exec - otherwise, something
            # is wrong
            item_exec = exec_.item_execs[0]
            get_execs(item_exec, parent_exec, prov_agent)
        
        else:
            # something is wrong...
            pass
        
        return True
    ############################################################################
    
    # workflow
    prov_workflow = create_prov_entity_from_workflow(id_scope, workflow)
    entities_map[workflow.id] = prov_workflow
    entities.append(prov_workflow)
    
    # getting modules and connections 
    get_modules_and_conn(prov_workflow, workflow)
    
    # storing input data
    for id in prov_functions:
        entities.append(prov_functions[id])
    
    # machines
    for machine in log.machine_list:
        machines[machine.id] = (create_prov_agent_from_machine(id_scope, machine), False)
    
    # executions
    for exec_ in log.workflow_execs:
        if exec_.parent_version != version:
            continue
        prov_agent = None
        if exec_.user not in agents_map:
            prov_agent = create_prov_agent_from_user(id_scope, exec_.user)
            agents_map[exec_.user] = prov_agent
            agents.append(prov_agent)
        else:
            prov_agent = agents_map[exec_.user]
        
        # creating PROV activity
        prov_activity = create_prov_activity_from_wf_exec(id_scope, exec_)
        activities.append(prov_activity)
        
        # creating association with PROV entity
        prov_association = create_prov_association(prov_activity, prov_agent, prov_workflow)
        
        for item in exec_.item_execs:
            get_execs(item, prov_activity, prov_agent)
    
    # PROV Document
    return create_prov_document(entities=entities,
                                activities=activities,
                                agents=agents,
                                connections=connections,
                                usages=usages,
                                generations=generations,
                                associations=associations)


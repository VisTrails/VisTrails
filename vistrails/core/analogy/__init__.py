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

from vistrails.core.data_structures.bijectivedict import Bidict
from itertools import imap, chain
from vistrails.core.modules.module_registry import get_module_registry, \
    ModuleRegistryException
import vistrails.core.db.io
from vistrails.core.requirements import MissingRequirement
from vistrails.core.vistrail.module import Module
from vistrails.core.vistrail.module_function import ModuleFunction
from vistrails.core.vistrail.port_spec import PortSpec, PortEndPoint
import copy
from vistrails.core.vistrail.pipeline import Pipeline

from eigen import *

##########################################################################


_debug = False

def perform_analogy_on_vistrail(vistrail, version_a, version_b, version_c, 
                                pipeline_a=None, pipeline_c=None, alpha=0.15):
    """perform_analogy(vistrail, version_a, version_b, version_c,
                       pipeline_a=None, pipeline_c=None, alpha=0.15): action
    Creates a new action version_d to the vistrail such that the difference
    between a and b is the same as between c and d, and returns this
    action."""

    ############################################################################
    # STEP 1: find mapping from a to c

    #     pipeline_c = Pipeline(vistrail.actionChain(version_c))
    #     pipeline_a = Pipeline(vistrail.actionChain(version_a))

    if _debug:
        print 'version_a:', version_a
        print 'version_b:', version_b
        print 'version_c:', version_c

    if pipeline_a is None:
        pipeline_a = vistrails.core.db.io.get_workflow(vistrail, version_a)
        pipeline_a.validate()
    if pipeline_c is None:
        pipeline_c = vistrails.core.db.io.get_workflow(vistrail, version_c)
        pipeline_c.validate()
    
    e = EigenPipelineSimilarity2(pipeline_a, pipeline_c, alpha=alpha)
    e._debug = _debug

    (input_module_remap,
     output_module_remap,
     combined_module_remap) = e.solve()

    if _debug:
        print 'Input remap'
        print input_module_remap
        print 'Output remap'
        print output_module_remap
        print 'Combined remap'
        print combined_module_remap

    module_remap = combined_module_remap
    if _debug:
        print "Computing names..."
        
    def name_remap(d):
        return dict([(from_id,
                      pipeline_c.modules[to_id].name)
                     for (from_id, to_id)
                     in d.iteritems()])

    module_name_remap = name_remap(module_remap)
    input_module_name_remap = name_remap(input_module_remap)
    output_module_name_remap = name_remap(output_module_remap)

    if _debug:
        print 'Name remap'
        print module_name_remap

    # find connection remap
    connection_remap = {}
    for a_connect in pipeline_a.connections.itervalues():
        # FIXME assumes that all connections have both source and dest
        a_source = a_connect.source.moduleId
        a_dest = a_connect.destination.moduleId
        match = None
        for c_connect in pipeline_c.connections.itervalues():
            if (output_module_remap[a_source] == c_connect.source.moduleId and 
                input_module_remap[a_dest] == c_connect.destination.moduleId):
                match = c_connect
                if (a_connect.source.spec == c_connect.source.spec and 
                    a_connect.destination.spec == c_connect.destination.spec):
                    break
        if match is not None:
            connection_remap[a_connect.id] = match.id
        elif _debug:
            print "failed to find connection match", a_connect.id, a_source, \
                a_dest

    # find function remap

    # construct total remap
    id_remap = {}
    sum_ax = 0.0
    sum_ay = 0.0
    sum_cx = 0.0
    sum_cy = 0.0
    for (a_id, c_id) in module_remap.iteritems():
        id_remap[('module', a_id)] = c_id
        module_a = pipeline_a.modules[a_id]
        sum_ax += module_a.location.x
        sum_ay += module_a.location.y
        module_c = pipeline_c.modules[c_id]
        sum_cx += module_c.location.x
        sum_cy += module_c.location.y
        
    if len(module_remap) != 0:
        avg_ax = sum_ax / len(module_remap)
        avg_ay = sum_ay / len(module_remap)
        avg_cx = sum_cx / len(module_remap)
        avg_cy = sum_cy / len(module_remap)
    else:
        avg_ax = 0.0
        avg_ay = 0.0
        avg_cx = 0.0
        avg_cy = 0.0
        
#    avg_ax = sum_ax / len(module_remap) if len(module_remap) != 0 else 0.0
#    avg_ay = sum_ay / len(module_remap) if len(module_remap) != 0 else 0.0
#    avg_cx = sum_cx / len(module_remap) if len(module_remap) != 0 else 0.0
#    avg_cy = sum_cy / len(module_remap) if len(module_remap) != 0 else 0.0
        
    for (a_id, c_id) in connection_remap.iteritems():
        id_remap[('connection', a_id)] = c_id
    ############################################################################
    # STEP 2: find actions to be remapped (b-a)

    # this creates a new action with new operations
    baAction = vistrails.core.db.io.getPathAsAction(vistrail, version_a, version_b, True)

#     for operation in baAction.operations:
#         print "ba_op0:", operation.id,  operation.vtType, operation.what, 
#         print operation.old_obj_id, "to", operation.parentObjType,
#         print operation.parentObjId

    ############################################################################
    # STEP 3: remap (b-a) using mapping in STEP 1 so it can be applied to c

    # for all module references, update the module ids according to the remap
    # need to consider modules, parent_obj_ids, ports
    # if things don't make sense, they're cut out in STEP 4, not here

    reg = get_module_registry()
    ops = []

    # NOTE !!! delete ops are before any add ops so this is ok !!!
    # if this changes, this may break
    c_modules = set(pipeline_c.modules)
    c_connections = set(pipeline_c.connections)
    c_locations = dict((m_id, m.location) 
                       for (m_id, m) in pipeline_c.modules.iteritems())
    c_annotations = dict(((m_id, a.key), a) for m_id, m in \
                             pipeline_c.modules.iteritems()
                         for a in m.annotations)
    c_parameters = dict(((f.real_id, p.pos), p) 
                        for m in pipeline_c.modules.itervalues() 
                        for f in m.functions 
                        for p in f.parameters)
    conns_to_delete = set()

    for op in baAction.operations:
        if op.vtType == 'delete':
            parent_obj_type = op.parentObjType
            if parent_obj_type == 'abstraction' or parent_obj_type == 'group':
                parent_obj_type = 'module'
            if (op.what == 'module' or 
                op.what == 'abstraction' or 
                op.what == 'group'):
                if module_remap.has_key(op.old_obj_id):
                    remap_id = module_remap[op.old_obj_id]
                    module = pipeline_c.modules[remap_id]
                    graph = pipeline_c.graph
                    for _, c_id in graph.edges_from(remap_id):
                        conn = pipeline_c.connections[c_id]
                        ops.extend(vistrails.core.db.io.create_delete_op_chain(conn))
                    for _, c_id in graph.edges_to(remap_id):
                        conn = pipeline_c.connections[c_id]
                        ops.extend(vistrails.core.db.io.create_delete_op_chain(conn))
                    ops.extend(vistrails.core.db.io.create_delete_op_chain(module))
                    c_modules.discard(remap_id)
                else:
                    ops.append(op)
                    c_modules.discard(op.old_obj_id)
            elif op.what == 'connection':
                if connection_remap.has_key(op.old_obj_id):
                    conn = pipeline_c.connections[connection_remap[ \
                            op.old_obj_id]]
                    ops.extend(vistrails.core.db.io.create_delete_op_chain(conn))
                    c_connections.discard(conn.id)
                else:
                    ops.append(op)
                    c_connections.discard(op.old_obj_id)
            elif (parent_obj_type, op.parentObjId) not in id_remap:
                if op.what == 'location':
                    c_locations.pop(op.parentObjId, None)
                if op.what == 'annotation':
                    for (m_id, key), a in c_annotations.iteritems():
                        if a.id == op.old_obj_id:
                            c_annotations.pop((m_id, key), None)
                            break
                if op.what == 'parameter':
                    for (f_id, pos), p in c_parameters.iteritems():
                        if p.real_id == op.old_obj_id:
                            c_parameters.pop((f_id, pos), None)
                            break
                    
                ops.append(op)
        elif op.vtType == 'add' or op.vtType == 'change':
            old_id = op.new_obj_id
            new_id = vistrail.idScope.getNewId(op.what)
            op.new_obj_id = new_id
            op.data.db_id = new_id
            op_what = op.what
            if op_what == 'abstraction' or op_what == 'group':
                op_what = 'module'
            id_remap[(op_what, old_id)] = new_id
            if (op.what == 'module' or 
                op.what == 'abstraction' or 
                op.what == 'group'):
                module_name_remap[old_id] = op.data.name
                c_modules.add(new_id)
            elif op.what == 'connection':
                c_connections.add(new_id)

            parent_obj_type = op.parentObjType
            if parent_obj_type == 'abstraction' or parent_obj_type == 'group':
                parent_obj_type = 'module'
            if op.parentObjId is not None and \
                    id_remap.has_key((parent_obj_type, op.parentObjId)):
                op.parentObjId = id_remap[(parent_obj_type, op.parentObjId)]
            if op.what == 'location':
                # need to make this a 'change' if it's an 'add' and
                # the module already exists
                if op.vtType == 'add':
                    if op.parentObjId in c_locations:
                        new_op_list = vistrails.core.db.io.create_change_op_chain(
                            c_locations[op.parentObjId], op.data,
                            (op.parentObjType, op.parentObjId))
                        op = new_op_list[0]
                    c_locations[op.parentObjId] = op.data
                elif op.vtType == 'change':
                    c_locations[op.parentObjId] = op.data
            elif op.what == 'annotation':
                if op.vtType == 'add':
                    if (op.parentObjId, op.data.key) in c_annotations:
                        new_op_list = vistrails.core.db.io.create_change_op_chain(
                            c_annotations[(op.parentObjId, op.data.key)],
                            op.data,
                            (Module.vtType, op.parentObjId))
                        op = new_op_list[0]
                    c_annotations[(op.parentObjId, op.data.key)] = op.data
                elif op.vtType == 'change':
                    c_annotations[(op.parentObjId, op.data.key)] = op.data
            elif op.what == 'parameter':
                if op.vtType == 'add':
                    if (op.parentObjId, op.data.pos) in c_parameters:
                        new_op_list = vistrails.core.db.io.create_change_op_chain(
                            c_parameters[(op.parentObjId, op.data.pos)],
                            op.data,
                            (ModuleFunction.vtType, op.parentObjId))
                        op = new_op_list[0]
                    c_parameters[(op.parentObjId, op.data.pos)] = op.data
                elif op.vtType == 'change':
                    c_parameters[(op.parentObjId, op.data.pos)] = op.data
            elif op.what == 'port':
                port = op.data
                # check the input/output module remaps since that is
                # what we use to modify the ids
                if port.type == 'source' and \
                        port.moduleId in output_module_remap:
                    temp_id = output_module_remap[port.moduleId]
                elif port.type == 'destination' and \
                        port.moduleId in input_module_remap:
                    temp_id = input_module_remap[port.moduleId]
                else:
                    temp_id = port.moduleId
                if ('module', temp_id) in id_remap:
                    temp_id = id_remap[('module', temp_id)]
                if temp_id in c_modules:
                    if port.type == 'source':
                        try:
                            port.moduleName = output_module_name_remap[port.moduleId]
                            port.moduleId = output_module_remap[port.moduleId]
                            m = pipeline_c.modules[port.moduleId]
                            d = m.module_descriptor
                            def remap():
                                port_type = \
                                    PortSpec.port_type_map.inverse[port.type]
                                try:
                                    pspec = reg.get_port_spec(m.package, m.name,
                                                              m.namespace,
                                                              port.name, 
                                                              port_type)
                                except ModuleRegistryException:
                                    return False
                                all_ports = reg.all_source_ports(d)
                                # print "pspec", pspec
                                # First try to find a perfect match
                                for (klass_name, ports) in all_ports:
                                    for candidate_port in ports:
                                        if (candidate_port.type_equals(pspec) and
                                            candidate_port.name == port.name):
                                            #print "found perfect match"
                                            port.spec = candidate_port
                                            return True
                                # Now try to find an imperfect one
                                for (klass_name, ports) in all_ports:
                                    for candidate_port in ports:
                                        print candidate_port
                                        if candidate_port.type_equals(pspec):
                                            #print "found imperfect match"
                                            port.name = candidate_port.name
                                            port.spec = candidate_port
                                            return True
                                return False
                            if not remap():
                                print "COULD NOT FIND source MATCH!!!"
                        except KeyError:
                            # This happens when the module was added as part of the analogy
                            port.moduleName = module_name_remap[port.moduleId]
                            port.moduleId = id_remap[('module', port.moduleId)]
                    elif port.type == 'destination':
                        try:
                            port.moduleName = input_module_name_remap[port.moduleId]
                            port.moduleId = input_module_remap[port.moduleId]
                            m = pipeline_c.modules[port.moduleId]
                            d = m.module_descriptor
                            def remap():
                                port_type = \
                                    PortSpec.port_type_map.inverse[port.type]
                                try:
                                    pspec = reg.get_port_spec(m.package, m.name,
                                                              m.namespace,
                                                              port.name, 
                                                              port_type)
                                    # print "This is the spec", port.spec, \
                                    #     port.db_spec
                                except ModuleRegistryException:
                                    return False
                                all_ports = reg.all_destination_ports(d)
                                # First try to find a perfect match
                                for (klass_name, ports) in all_ports:
                                    for candidate_port in ports:
                                        if (candidate_port.type_equals(pspec) and
                                            candidate_port.name == port.name):
                                            # print "found perfect match"
                                            port.spec = candidate_port
                                            return True
                                # Now try to find an imperfect one
                                for (klass_name, ports) in all_ports:
                                    for candidate_port in ports:
                                        if candidate_port.type_equals(pspec):
                                            # print "found imperfect match"
                                            port.name = candidate_port.name
                                            port.spec = candidate_port
                                            return True
                                return False
                            if not remap():
                                print "COULD NOT FIND destination MATCH!!!"
                            remap()
                        except KeyError:
                            # This happens when the module was added as part of the analogy
                            port.moduleName = module_name_remap[port.moduleId]
                            port.moduleId = id_remap[('module', port.moduleId)]
                else:
                    # delete the connection since it won't work
                    conns_to_delete.add(op.parentObjId)
                    continue
            ops.append(op)

    baAction.operations = []
    for op in ops:
        if op.what == 'connection' and op.new_obj_id in conns_to_delete:
            pass
        elif op.what == 'port' and op.parentObjId in conns_to_delete:
            pass
        else:
            baAction.operations.append(op)

    # baAction.operations = ops
    
    # baAction should now have remapped everything

    ############################################################################
    # STEP 4: apply remapped (b-a) to c

    # some actions cannot be applied because they reference stuff that
    # isn't in c.  need to no-op for them
    
    # want to take the pipeline for c and simply apply (b-a), but return
    # False for operations that don't make sense.
    
    # get operationDict for c, do update with baAction but discard ops
    # that don't make sense

#     for operation in baAction.operations:
#         print "ba_op1:", operation.id, operation.vtType, operation.what, 
#         print operation.old_obj_id, "to", operation.parentObjType,
#         print operation.parentObjId

    baAction.prevId = version_c
    vistrails.core.db.io.fixActions(vistrail, version_c, [baAction])
    for operation in baAction.operations:
        if operation.what == 'location' and (operation.vtType == 'add' or
                                             operation.vtType == 'change'):
            operation.data.x -= avg_ax - avg_cx
            operation.data.y -= avg_ay - avg_cy
#         print "ba_op2:", operation.id, operation.vtType, operation.what, 
#         print operation.old_obj_id, "to", operation.parentObjType,
#         print operation.parentObjId
    # this will be taken care by the controller
    #vistrail.add_action(baAction, version_c)
    return baAction

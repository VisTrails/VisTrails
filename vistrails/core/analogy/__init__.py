############################################################################
##
## Copyright (C) 2006-2007 University of Utah. All rights reserved.
##
## This file is part of VisTrails.
##
## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following to ensure GNU General Public
## Licensing requirements will be met:
## http://www.opensource.org/licenses/gpl-license.php
##
## If you are unsure which license is appropriate for your use (for
## instance, you are interested in developing a commercial derivative
## of VisTrails), please contact us at vistrails@sci.utah.edu.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################

from core.utils import iter_with_index
from core.data_structures.bijectivedict import Bidict
import scipy
from itertools import imap, chain
import core.modules.module_registry
from core.vistrail.port import PortEndPoint
from core.vistrail.module import Module
import copy
from core.vistrail.action import (Action,
                                  MoveModuleAction,
                                  AddModuleAction,
                                  DeleteModuleAction,
                                  ChangeParameterAction,
                                  AddConnectionAction,
                                  DeleteConnectionAction,
                                  AddModulePortAction,
                                  DeleteModulePortAction)
from core.vistrail.pipeline import Pipeline
reg = core.modules.module_registry.registry

##########################################################################

from eigen import *

_debug = True

def perform_analogy_on_vistrail(vistrail,
                                version_a, version_b,
                                version_c, alpha=0.85):
    """perform_analogy(controller, version_a, version_b, version_c,
                       alpha=0.15): version_d
    Adds a new version d to the controller such that the difference
    between a and b is the same as between c and d, and returns the
    number of this version."""

    def get_context_info(version_from, version_to):
        diff = vistrail.get_pipeline_diff_with_connections(version_from,
                                                           version_to)
        if _debug:
            print "DIFF:",
            print diff

        # The right way to do this in the future is to check
        # which action set is smaller
        (actions,
         module_id_remap,
         connection_id_remap) = vistrail.make_actions_from_diff(diff)
#         actions = vistrail.general_action_chain(version_from, version_to)

        # We don't care about move actions or annotations, so remove
        # them all
        actions = [a for a in actions if a.relevant_for_analogy()]

        if _debug:
            print "actions:"
            print version_from, version_to, actions
            print "transpositions: "
            print module_id_remap
            print connection_id_remap

        # Find new modules by trying to perform the action in an empty
        # pipeline.  If it fails, it's because the action references the
        # "outside world"

        context = []
    
        p = Pipeline()
        for action in actions:
            try:
                action.perform(p)
            except Action.MissingModule, e:
                context.append((action, e))
            except Action.MissingConnection, e:
                context.append((action, e))
            except ChangeParameterAction.ParameterInconsistency, e:
                raise Exception("Can't currently handle parameter inconsistencies")

        intrinsics = [a for a in actions if a not in
                      [x[0] for x in context]]

        conn_ids = {}

        # note to self: the exceptions are holding the effective context
        # for multiple deletions

        for (action, e) in context:
            if type(action) == AddConnectionAction:
                conn_ids[action.connection.id] = (action, e)
            elif type(action) == DeleteConnectionAction:
                removed = []
                for c_id in e.connection_ids:
                    if conn_ids.has_key(c_id):
#                         print context
#                         print conn_ids[c_id]
                        context.remove(conn_ids[c_id])
                        removed.append(c_id)
                for r in removed:
                    e.connection_ids.remove(r)

        return (context, intrinsics, module_id_remap, connection_id_remap)


    pipeline_c = Pipeline(vistrail.actionChain(version_c))
    pipeline_a = Pipeline(vistrail.actionChain(version_a))
    
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

    (ab_context, ab_intrinsics,
     ab_module_remap,
     ab_connection_remap) = get_context_info(version_a, version_b)

    # Get version_a - version_c
    (ca_context, ca_intrinsics,
     ca_module_remap,
     ca_connection_remap) = get_context_info(version_c, version_a)

    # ca_intrinsics are the "dangerous stuff" - they are the ones
    # that exist in a but not in c. So any ids that these introduce
    # will have to be soft-matched

    ca_introduced_ids = [ca_module_remap[a.module.id] for a in ca_intrinsics
                         if type(a) == AddModuleAction]
    if _debug:
        print "modules that will have to be soft matched: ",
        print ca_introduced_ids
    ca_introduced_ids = set(ca_introduced_ids)

    if _debug:
        for i in ca_introduced_ids:
            print pipeline_a.modules[i].name
        print "Culling hardmatches..."


#     def keep_introduced_ids(d):
#         items = d.items()
#         new_items = [(k, ((k in ca_introduced_ids) and v) or k)
#                      for (k,v) in items]
#         return dict(new_items)
    def keep_introduced_ids(d):
        return d

    # if in ca_introduced_ids, keep it. otherwise, map back to self
    input_module_remap = keep_introduced_ids(input_module_remap)
    output_module_remap = keep_introduced_ids(output_module_remap)
    combined_module_remap = keep_introduced_ids(combined_module_remap)

#     print 'Input remap'
#     print input_module_remap
#     print 'Output remap'
#     print output_module_remap
#     print 'Combined remap'
#     print combined_module_remap

    if _debug:
        print "Computing names..."

    def name_remap(d):
        return dict([(from_id,
                      pipeline_c.modules[to_id].name)
                     for (from_id, to_id)
                     in d.iteritems()])

    input_module_name_remap = name_remap(input_module_remap)
    output_module_name_remap = name_remap(output_module_remap)
    combined_module_name_remap = name_remap(combined_module_remap)

    class PipelinePortInfo(object):
        pass
    def mk_tuple(m):
        result = PipelinePortInfo()
        (iports, oports) = e.get_ports(m, True)
        iportmap = e.create_type_portmap(iports)
        oportmap = e.create_type_portmap(oports)
        result.iports = iports
        result.oports = oports
        result.iportmap = iportmap
        result.oportmap = oportmap
        return result
    def get_pipeline_ports(pipeline):
        return dict([(m.id, mk_tuple(m))
                     for m in pipeline.modules.itervalues()])

#     a_ports = get_pipeline_ports(pipeline_a)
    c_ports = get_pipeline_ports(pipeline_c)
    if _debug:
        print c_ports
        print 'Input remap'
        print input_module_remap
        print input_module_name_remap
        print 'Output remap'
        print output_module_remap
        print output_module_name_remap
        print 'Combined remap'
        print combined_module_remap
        print combined_module_name_remap

    module_remap = combined_module_remap
    module_name_remap = combined_module_name_remap

    connection_remap = {}

    # Now, for the easy part. Perform the translation by applying
    # transformed actions on "version c" (as in the running example
    # d-c = b-a)
    
    remapped_last_parent = [version_c] # Ugly lack of real closures, yuck

    def remap_port(port):
        def remove_spec_description(spec):
            if type(spec) == list:
                return [remove_spec_description(s) for s in spec]
            elif type(spec) == tuple:
                return spec[0].__name__
        def make_string_spec(spec):
            assert type(spec) == list
            return tuple([x[0].__name__ for x in spec])
        def make_string_spec_list(spec):
            return [make_string_spec(s) for s in spec]
        p = copy.copy(port)
        if p.endPoint == PortEndPoint.Source:
            module_remap = output_module_remap
            module_name_remap = output_module_name_remap
            ports = c_ports[module_remap[port.moduleId]].oports
            portmap = c_ports[module_remap[port.moduleId]].oportmap
            module_ports = Module.sourcePorts
        else:
            assert p.endPoint == PortEndPoint.Destination
            module_remap = input_module_remap
            module_name_remap = input_module_name_remap
            ports = c_ports[module_remap[port.moduleId]].iports
            portmap = c_ports[module_remap[port.moduleId]].iportmap
            module_ports = Module.destinationPorts

        p.moduleId = module_remap[port.moduleId]
        p.moduleName = module_name_remap[port.moduleId]
        if (port.name in ports and
            ports[port.name] == remove_spec_description(port.spec)):
            # perfect match
            if _debug: print "perfect match"
            return p
        sspec = make_string_spec(port.spec[0])
        if sspec in portmap:
#             print sspec
#             print module_ports(pipeline_c.modules[p.moduleId])
#             print portmap[sspec]
            p.name = portmap[sspec][0]
#             print "------------------------------"
#             print p.name
#             for a in module_ports(pipeline_c.modules[p.moduleId]):
#                 print a.name
#                 print a.spec
#                 print make_string_spec_list(a.spec)
            softspec = [a for a
                        in module_ports(pipeline_c.modules[p.moduleId])
                        if sspec in make_string_spec_list(a.spec)]
            assert len(softspec) > 0
            softspec = softspec[0].spec

            # We'll pick the first one. In the future, it should be
            # the best one
            for single_spec in softspec:
                if make_string_spec(single_spec) == sspec:
                    p.spec = [copy.deepcopy(single_spec)]
                    if _debug: print "soft match"
                    return p
        if _debug:
            print p
            print port
            print sspec
            print portmap
            print port.spec
        raise Exception("Couldn't find soft match")


    def translate_action(action, e=None):
        def translate_single_action(action):
            if type(action) == AddModuleAction:
                new_action = AddModuleAction()
                new_action.module = copy.copy(action.module)
                new_id = pipeline_c.fresh_module_id()
                old_id = new_action.module.id
                input_module_remap[old_id] = new_id
                input_module_name_remap[old_id] = new_action.module.name
                output_module_remap[old_id] = new_id
                output_module_name_remap[old_id] = new_action.module.name
                combined_module_remap[old_id] = new_id
                combined_module_name_remap[old_id] = new_action.module.name
                new_action.module.id = new_id
                c_ports[new_id] = mk_tuple(new_action.module)
            elif type(action) == ChangeParameterAction:
                new_action = ChangeParameterAction()
                new_action.parameters = copy.deepcopy(action.parameters)
                # Function id will not change for intrinsics
                # For soft matches, it'll be a mess - we'll assume no change for now
                for p in new_action.parameters:
                    p[0] = combined_module_remap[p[0]]
            elif type(action) == AddConnectionAction:
                new_action = AddConnectionAction()
                new_action.connection = copy.copy(action.connection)
                new_id = pipeline_c.fresh_connection_id()
                old_id = new_action.connection.id
                connection_remap[old_id] = new_id
                new_action.connection.id = new_id
                old_c = action.connection
                c = new_action.connection
                c.source = remap_port(c.source)
                c.destination = remap_port(c.destination)
#                 c.sourceId = output_module_remap[old_c.sourceId]
#                 c.destinationId = output_module_remap[old_c.destinationId]
#                 c.source.moduleName = input_module_name_remap[old_c.sourceId]
#                 c.destination.moduleName = input_module_name_remap[old_c.destinationId]
            elif type(action) == DeleteConnectionAction:
                new_action = DeleteConnectionAction()
                if e: # for context matches
                    lst = e.connection_ids
                else:
                    lst = action.ids
                for conn_id in lst:
                    repeats = set()
                    old_connection = pipeline_a.connections[conn_id]
                    new_source = old_connection.sourceId
                    new_source = output_module_remap[new_source]
                    new_dest = old_connection.destinationId
                    new_dest = input_module_remap[new_dest]
                    if (new_source, new_dest) in repeats:
                        continue
                    repeats.add((new_source, new_dest))
                    new_connection_id = pipeline_c.graph.get_edge(new_source,
                                                                  new_dest)
                    if new_connection_id != None:
                        connection_remap[conn_id] = new_connection_id
                        new_action.ids.append(new_connection_id)
                    else:
                        if _debug:
                            print "Warning, ignoring inexisting match:",
                            print new_source, new_dest
            elif type(action) == AddModulePortAction:
                new_action = AddModulePortAction()
                new_action.portType = action.portType
                new_action.portName = action.portName
                new_action.portSpec = action.portSpec
                new_action.moduleId = combined_module_remap[action.moduleId]
            elif type(action) == DeleteModulePortAction:
                new_action = DeleteModulePortAction()
                new_action.moduleId = combined_module_remap[action.moduleId]
            elif type(action) == DeleteModuleAction:
                new_action = DeleteModuleAction()
                repeats = set()
                if e:
                    lst = e.module_ids
                else:
                    lst = action.ids
                if _debug: print "start"
                for m_id in lst:
                    new_id = combined_module_remap[m_id]
                    if new_id in repeats:
                        continue
                    repeats.add(new_id)
                    if _debug: print "appending ", new_id
                    new_action.ids.append(new_id)
                    del c_ports[new_id]
                if _debug: print "done"
            elif type(action) == CompositeAction:
                new_action = CompositeAction()
                new_action._action_list = [translate_single_action(a)
                                           for a in action._action_list]
            else:
                raise Exception("Can't handle '%s'" % str(type(action)))
            return new_action
        new_action = translate_single_action(action)
        new_action.parent = remapped_last_parent[0]
        new_action.timestep = vistrail.getFreshTimestep()
        new_action.date = vistrail.getDate()
        new_action.user = vistrail.getUser()
        vistrail.addVersion(new_action)
        remapped_last_parent[0] = new_action.timestep
        new_action.perform(pipeline_c)

    for action in ab_intrinsics:
        if _debug: print "\n\n\nWill remap ",type(action), action
        translate_action(action)

    for (action, e) in ab_context:
        if _debug: print "\n\n\nWill remap ",type(action), action
        translate_action(action, e)

    return remapped_last_parent[0]

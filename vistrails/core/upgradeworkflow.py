###############################################################################
##
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

"""This file contains code to handle InvalidPipeline exceptions that contain
upgrade requests."""

from core import debug
import core.db.action
from core.modules.module_registry import get_module_registry, \
     ModuleDescriptor, MissingModule, MissingPort
from core.packagemanager import get_package_manager
from core.vistrail.annotation import Annotation
from core.vistrail.connection import Connection
from core.vistrail.port import Port
from core.vistrail.port_spec import PortSpec
from core.utils import versions_increasing
import copy

##############################################################################

class UpgradeWorkflowError(Exception):

    def __init__(self, msg, module=None, port_name=None, port_type=None):
        Exception.__init__(self, msg)
        self._msg = msg
        self._module = module
        self._port_name = port_name
        self._port_type = port_type.lower() if port_type else None
        
    def __str__(self):
        return "Upgrading workflow failed.\n" + self._msg

class UpgradeWorkflowHandler(object):

    @staticmethod
    def dispatch_request(controller, module_id, current_pipeline):
        reg = get_module_registry()
        pm = get_package_manager()
        if module_id not in current_pipeline.modules:
            # It is possible that some other upgrade request has
            # already removed the invalid module of this request. In
            # that case, disregard the request.
            debug.log("module %s already handled. skipping" % module_id)
            return []
        invalid_module = current_pipeline.modules[module_id]
        pkg = pm.get_package_by_identifier(invalid_module.package)
        if hasattr(pkg.module, 'handle_module_upgrade_request'):
            f = pkg.module.handle_module_upgrade_request
            return f(controller, module_id, current_pipeline)
        else:
            debug.log('Package "%s" cannot handle upgrade request. '
                      'VisTrails will attempt automatic upgrade.' % \
                          pkg.identifier)
            auto_upgrade = UpgradeWorkflowHandler.attempt_automatic_upgrade
            return auto_upgrade(controller, current_pipeline, module_id)

    @staticmethod
    def check_port_spec(module, port_name, port_type, descriptor=None, 
                        sigstring=None):
        from core.modules.basic_modules import identifier as basic_pkg

        reg = get_module_registry()
        found = False
        try:
            if descriptor is not None:
                s = reg.get_port_spec_from_descriptor(descriptor, port_name,
                                                      port_type)
                found = True
                sigstring = reg.expand_port_spec_string(sigstring, basic_pkg)
                if s.sigstring != sigstring:
                    msg = ('%s port "%s" of module "%s" exists, but '
                           'signatures differ "%s" != "%s"') % \
                           (port_type.capitalize(), port_name, module.name,
                            s.sigstring, sigstring)
                    raise UpgradeWorkflowError(msg, module, port_name, port_type)
        except MissingPort:
            pass

        if not found and \
                not module.has_portSpec_with_name((port_name, port_type)):
            msg = '%s port "%s" of module "%s" does not exist.' % \
                (port_type.capitalize(), port_name, module.name)
            raise UpgradeWorkflowError(msg, module, port_name, port_type)

    @staticmethod
    def find_descriptor(controller, pipeline, module_id, desired_version=''):
        from core.modules.abstraction \
            import identifier as local_abstraction_pkg
        reg = get_module_registry()

        get_descriptor = reg.get_descriptor_by_name
        pm = get_package_manager()
        invalid_module = pipeline.modules[module_id]
        mpkg, mname, mnamespace, mid = (invalid_module.package,
                                        invalid_module.name,
                                        invalid_module.namespace,
                                        invalid_module.id)
        pkg = pm.get_package_by_identifier(mpkg)
        desired_version = ''
        d = None
        # don't check for abstraction/subworkflow since the old module
        # could be a subworkflow
        if reg.has_abs_upgrade(*invalid_module.descriptor_info):
            return reg.get_abs_upgrade(*invalid_module.descriptor_info)

        try:
            try:
                d = get_descriptor(mpkg, mname, mnamespace, '', desired_version)
            except MissingModule, e:
                r = None
                if pkg.can_handle_missing_modules():
                    r = pkg.handle_missing_module(controller, module_id, 
                                                  pipeline)
                    d = get_descriptor(mpkg, mname, mnamespace, '', 
                                       desired_version)
                if not r:
                    raise e
        except MissingModule, e:
            return None
        assert isinstance(d, ModuleDescriptor)
        return d

    @staticmethod
    def check_upgrade(pipeline, module_id, d, function_remap={},
                      src_port_remap={}, dst_port_remap={}):
        invalid_module = pipeline.modules[module_id]
        def check_connection_port(port):
            port_type = PortSpec.port_type_map.inverse[port.type]
            UpgradeWorkflowHandler.check_port_spec(invalid_module,
                                                   port.name, port_type,
                                                   d, port.sigstring)
            
        # check if connections are still valid
        for _, conn_id in pipeline.graph.edges_from(module_id):
            port = pipeline.connections[conn_id].source
            if port.name not in src_port_remap:
                check_connection_port(port)
        for _, conn_id in pipeline.graph.edges_to(module_id):
            port = pipeline.connections[conn_id].destination
            if port.name not in dst_port_remap:
                check_connection_port(port)

        # check if function values are still valid
        for function in invalid_module.functions:
            # function_spec = function.get_spec('input')
            if function.name not in function_remap:
                UpgradeWorkflowHandler.check_port_spec(invalid_module,
                                                       function.name, 
                                                       'input', d,
                                                       function.sigstring)

    @staticmethod
    def attempt_automatic_upgrade(controller, pipeline, module_id,
                                  function_remap={}, src_port_remap={}, 
                                  dst_port_remap={}, annotation_remap={}):
        """attempt_automatic_upgrade(module_id, pipeline): [Action]

        Attempts to automatically upgrade module by simply adding a
        new module with the current package version, and recreating
        all connections and functions. If any of the ports used are
        not available, raise an exception that will trigger the
        failure of the entire upgrade.

        attempt_automatic_upgrade returns a list of actions if 
        successful.
        """

        invalid_module = pipeline.modules[module_id]
        mpkg, mname, mnamespace, mid = (invalid_module.package,
                                        invalid_module.name,
                                        invalid_module.namespace,
                                        invalid_module.id)
        d = UpgradeWorkflowHandler.find_descriptor(controller, pipeline, 
                                                   module_id)
        if not d:
            if mnamespace:
                nss = mnamespace + '|' + mname
            else:
                nss = mname
            msg = ("Could not upgrade module %s from package %s.\n" %
                    (mname, mpkg))
            raise UpgradeWorkflowError(msg)

        UpgradeWorkflowHandler.check_upgrade(pipeline, module_id, d, 
                                             function_remap, 
                                             src_port_remap, dst_port_remap)

        # If we passed all of these checks, then we consider module to
        # be automatically upgradeable. Now create actions that will
        # delete functions, module, and connections, and add new
        # module with corresponding functions and connections.

        return UpgradeWorkflowHandler.replace_module(controller, pipeline, 
                                                     module_id, d, 
                                                     function_remap,
                                                     src_port_remap, 
                                                     dst_port_remap,
                                                     annotation_remap)

    @staticmethod
    def create_new_connection(controller, src_module, src_port, 
                              dst_module, dst_port):
        # spec -> name, type, signature
        output_port_id = controller.id_scope.getNewId(Port.vtType)
        if type(src_port) == type(""):
            output_port_spec = src_module.get_port_spec(src_port, 'output')
            output_port = Port(id=output_port_id,
                               spec=output_port_spec,
                               moduleId=src_module.id,
                               moduleName=src_module.name)
        else:
            output_port = Port(id=output_port_id,
                               name=src_port.name,
                               type=src_port.type,
                               signature=src_port.signature,
                               moduleId=src_module.id,
                               moduleName=src_module.name)

        input_port_id = controller.id_scope.getNewId(Port.vtType)
        if type(dst_port) == type(""):
            input_port_spec = dst_module.get_port_spec(dst_port, 'input')
            input_port = Port(id=input_port_id,
                              spec=input_port_spec,
                              moduleId=dst_module.id,
                              moduleName=dst_module.name)
        else:
            input_port = Port(id=input_port_id,
                              name=dst_port.name,
                              type=dst_port.type,
                              signature=dst_port.signature,
                              moduleId=dst_module.id,
                              moduleName=dst_module.name)
        conn_id = controller.id_scope.getNewId(Connection.vtType)
        connection = Connection(id=conn_id,
                                ports=[input_port, output_port])
        return connection



    @staticmethod
    def replace_generic(controller, pipeline, old_module, new_module,
                        function_remap={}, src_port_remap={}, 
                        dst_port_remap={}, annotation_remap={}):
        ops = []
        ops.extend(controller.delete_module_list_ops(pipeline, [old_module.id]))
        
        for annotation in old_module.annotations:
            if annotation.key not in annotation_remap:
                annotation_key = annotation.key
            else:
                remap = annotation_remap[annotation.key]
                if remap is None:
                    # don't add the annotation back in
                    continue
                elif type(remap) != type(""):
                    ops.extend(remap(annotation))
                    continue
                else:
                    annotation_key = remap

            new_annotation = \
                Annotation(id=controller.id_scope.getNewId(Annotation.vtType),
                           key=annotation_key,
                           value=annotation.value)
            new_module.add_annotation(new_annotation)

        if not old_module.is_group() and not old_module.is_abstraction():
            for port_spec in old_module.port_spec_list:
                if port_spec.type == 'input':
                    if port_spec.name not in dst_port_remap:
                        spec_name = port_spec.name
                    else:
                        remap = dst_port_remap[port_spec.name]
                        if remap is None:
                            continue
                        elif type(remap) != type(""):
                            ops.extend(remap(port_spec))
                            continue
                        else:
                            spec_name = remap
                elif port_spec.type == 'output':
                    if port_spec.name not in src_port_remap:
                        spec_name = port_spec.name
                    else:
                        remap = src_port_remap[port_spec.name]
                        if remap is None:
                            continue
                        elif type(remap) != type(""):
                            ops.extend(remap(port_spec))
                            continue
                        else:
                            spec_name = remap                
                new_spec = port_spec.do_copy(True, controller.id_scope, {})
                new_spec.name = spec_name
                new_module.add_port_spec(new_spec)

        for function in old_module.functions:
            if function.name not in function_remap:
                function_name = function.name
            else:
                remap = function_remap[function.name]
                if remap is None:
                    # don't add the function back in
                    continue                    
                elif type(remap) != type(""):
                    ops.extend(remap(function, new_module))
                    continue
                else:
                    function_name = remap

            if len(function.parameters) > 0:
                new_param_vals, aliases = zip(*[(p.strValue, p.alias) 
                                                for p in function.parameters])
            else:
                new_param_vals = []
                aliases = []
            new_function = controller.create_function(new_module, 
                                                      function_name,
                                                      new_param_vals,
                                                      aliases)
            new_module.add_function(new_function)

        # add the new module
        ops.append(('add', new_module))

        create_new_connection = UpgradeWorkflowHandler.create_new_connection

        for _, conn_id in pipeline.graph.edges_from(old_module.id):
            old_conn = pipeline.connections[conn_id]
            if old_conn.source.name not in src_port_remap:
                source_name = old_conn.source.name
            else:
                remap = src_port_remap[old_conn.source.name]
                if remap is None:
                    # don't add this connection back in
                    continue
                elif type(remap) != type(""):
                    ops.extend(remap(old_conn, new_module))
                    continue
                else:
                    source_name = remap
                    
            old_dst_module = pipeline.modules[old_conn.destination.moduleId]

            new_conn = create_new_connection(controller,
                                             new_module,
                                             source_name,
                                             old_dst_module,
                                             old_conn.destination)
            ops.append(('add', new_conn))
            
        for _, conn_id in pipeline.graph.edges_to(old_module.id):
            old_conn = pipeline.connections[conn_id]
            if old_conn.destination.name not in dst_port_remap:
                destination_name = old_conn.destination.name
            else:
                remap = dst_port_remap[old_conn.destination.name]
                if remap is None:
                    # don't add this connection back in
                    continue
                elif type(remap) != type(""):
                    ops.extend(remap(old_conn, new_module))
                    continue
                else:
                    destination_name = remap
                    
            old_src_module = pipeline.modules[old_conn.source.moduleId]
            new_conn = create_new_connection(controller,
                                             old_src_module,
                                             old_conn.source,
                                             new_module,
                                             destination_name)
            ops.append(('add', new_conn))
        
        return [core.db.action.create_action(ops)]

    @staticmethod
    def replace_group(controller, pipeline, module_id, new_subpipeline):
        old_group = pipeline.modules[module_id]
        new_group = controller.create_module('edu.utah.sci.vistrails.basic', 
                                             'Group', '', 
                                             old_group.location.x, 
                                             old_group.location.y)
        new_group.pipeline = new_subpipeline
        return UpgradeWorkflowHandler.replace_generic(controller, pipeline, 
                                                      old_group, new_group)

    @staticmethod
    def replace_module(controller, pipeline, module_id, new_descriptor,
                       function_remap={}, src_port_remap={}, dst_port_remap={},
                       annotation_remap={}):
        old_module = pipeline.modules[module_id]
        internal_version = -1
        # try to determine whether new module is an abstraction
        if (hasattr(new_descriptor, 'module') and
            hasattr(new_descriptor.module, "vistrail") and 
            hasattr(new_descriptor.module, "internal_version")):
            internal_version = new_descriptor.version
        new_module = \
            controller.create_module_from_descriptor(new_descriptor,
                                                     old_module.location.x,
                                                     old_module.location.y,
                                                     internal_version)

        return UpgradeWorkflowHandler.replace_generic(controller, pipeline, 
                                                      old_module, new_module,
                                                      function_remap, 
                                                      src_port_remap, 
                                                      dst_port_remap,
                                                      annotation_remap)

    @staticmethod
    def remap_module(controller, module_id, pipeline, module_remap):

        """remap_module offers a method to shortcut the
        specification of upgrades.  It is useful when just changing
        the names of ports or modules, but can also be used to add
        intermediate modules or change the format of parameters.  It
        is usually called from handle_module_upgrade_request, and the
        first three arguments are passed from the arguments to that
        method.

        module_remap specifies all of the changes and is of the format
        {<old_module_name>: [(<start_version>, <end_version>, 
                             <new_module_klass> | <new_module_id> | None, 
                             <remap_dictionary>)]}
        where new_module_klass is the class and new_module_id
        is a string of the format 
            <package_name>:[<namespace> | ]<module_name>
        passing None keeps the original name,
        and remap_dictionary is {<remap_type>:
        <name_changes>} and <name_changes> is a map from <old_name> to
        <new_name> or <remap_function>
        The remap functions are passed the old object and the new
        module and should return a list of operations with elements of
        the form ('add', <obj>).

        For example:

        def outputName_remap(old_conn, new_module):
            ops = []
            ...
            return ops
        module_remap = {'FileSink': [(None, '1.5.1', FileSink,
                                     {'dst_port_remap':
                                          {'overrideFile': 'overwrite',
                                           'outputName': outputName_remap},
                                      'function_remap':
                                          {'overrideFile': 'overwrite',
                                           'outputName': 'outputPath'}}),
                        }
        """

        reg = get_module_registry()

        old_module = pipeline.modules[module_id]
        old_desc_str = reg.create_descriptor_string(old_module.package,
                                                    old_module.name,
                                                    old_module.namespace,
                                                    False)
        # print 'running module_upgrade_request', old_module.name
        if old_desc_str in module_remap:
            for upgrade_tuple in module_remap[old_desc_str]:
                (start_version, end_version, new_module_type, remap) = \
                    upgrade_tuple
                old_version = old_module.version
                if ((start_version is None or 
                     not versions_increasing(old_version, start_version)) and
                    (end_version is None or
                     versions_increasing(old_version, end_version))):
                    # do upgrade
                    
                    if new_module_type is None:
                        try:
                            new_module_desc = \
                                reg.get_descriptor_by_name(old_module.package, 
                                                           old_module.name, 
                                                           old_module.namespace)
                        except MissingModule, e:
                            # if the replacement is an abstraction,
                            # and it has been upgraded, we use that
                            if reg.has_abs_upgrade(old_module.package,
                                                   old_module.name,
                                                   old_module.namespace):
                                new_module_desc = \
                                    reg.get_abs_upgrade(old_module.package,
                                                        old_module.name,
                                                        old_module.namespace)
                            else:
                                raise e
                    elif type(new_module_type) == type(""):
                        d_tuple = \
                            reg.expand_descriptor_string(new_module_type, \
                                                             old_module.package)
                        try:
                            new_module_desc = \
                                reg.get_descriptor_by_name(*d_tuple)
                        except MissingModule, e:
                            # if the replacement is an abstraction,
                            # and it has been upgraded, we use that
                            if reg.has_abs_upgrade(*d_tuple):
                                new_module_desc = reg.get_abs_upgrade(*d_tuple)
                            else:
                                raise e
                    else: # we have a klass for get_descriptor
                        new_module_desc = reg.get_descriptor(new_module_type)
                   
                    src_port_remap = remap.get('src_port_remap', {})
                    dst_port_remap = remap.get('dst_port_remap', {})
                    # !!! we're going to let dst_port_remap serve as a
                    # base for function_remap but the developer is
                    # responsible for knowing that anything beyond name
                    # remaps requires different functions
                    function_remap = copy.copy(dst_port_remap)
                    function_remap.update(remap.get('function_remap', {}))
                    annotation_remap = remap.get('annotation_remap', {})
                    action_list = \
                        UpgradeWorkflowHandler.replace_module(controller, 
                                                              pipeline,
                                                              module_id, 
                                                              new_module_desc,
                                                              function_remap,
                                                              src_port_remap,
                                                              dst_port_remap,
                                                              annotation_remap)
                    return action_list

        # otherwise, just try to automatic upgrade
        # attempt_automatic_upgrade
        return UpgradeWorkflowHandler.attempt_automatic_upgrade(controller, 
                                                                pipeline,
                                                                module_id)
    

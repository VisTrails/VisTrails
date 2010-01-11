############################################################################
##
## Copyright (C) 2006-2010 University of Utah. All rights reserved.
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

"""This file contains code to handle InvalidPipeline exceptions that contain
upgrade requests."""

from core import debug
import core.db.action
from core.modules.module_registry import get_module_registry, \
     PackageMustUpgradeModule, ModuleDescriptor
from core.packagemanager import get_package_manager
import copy

##############################################################################

class UpgradeWorkflowError(Exception):

    def __init__(self, msg):
        Exception.__init__(self, msg)
        self._msg = msg
        
    def __str__(self):
        return "Upgrading workflow failed.\n" + self._msg

class UpgradeWorkflowHandler(object):

    def __init__(self, controller, exception_set, pipeline):
        self._controller = controller
        self._exception_set = exception_set
        self._pipeline = copy.copy(pipeline)

    def handle_all_requests(self):
        current_pipeline = copy.copy(self._pipeline)
        all_actions = []
        for request in self._exception_set:
            print "New request: ", request
            new_actions = self.dispatch_request(request, current_pipeline)
            for action in new_actions:
                current_pipeline.perform_action(action)
            all_actions.extend(new_actions)
        return all_actions

    def dispatch_request(self, request, current_pipeline):
        reg = get_module_registry()
        pm = get_package_manager()
        if request._module_id not in current_pipeline.modules:
            # It is possible that some other upgrade request has
            # already removed the invalid module of this request. In
            # that case, disregard the request.
            print "module %s already handled. skipping" % request._module_id
            print current_pipeline.modules
            return []
        invalid_module = self._pipeline.modules[request._module_id]
        pkg = pm.get_package_by_identifier(invalid_module.package)
        if hasattr(pkg.module, 'handle_module_upgrade_request'):
            f = pkg.module.handle_module_upgrade_request
            return f(self._controller, request._module_id,
                     current_pipeline)
        else:
            debug.critical('Package cannot handle upgrade request. ' +
                           'VisTrails will attempt automatic upgrade.')
            return self.attempt_automatic_upgrade(request._module_id,
                                                  current_pipeline)

    def attempt_automatic_upgrade(self, module_id, pipeline):
        """attempt_automatic_upgrade(module_id, pipeline): [Action]

        Attempts to automatically upgrade module by simply adding a
        new module with the current package version, and recreating
        all connections and functions. If any of the ports used are
        not available, raise an exception that will trigger the
        failure of the entire upgrade.

        attempt_automatic_upgrade returns a list of actions if
        successful.
        """
        reg = get_module_registry()
        get_descriptor = reg.get_descriptor_by_name
        pm = get_package_manager()
        invalid_module = self._pipeline.modules[module_id]
        mpkg, mname, mnamespace, mid = (invalid_module.package,
                                        invalid_module.name,
                                        invalid_module.namespace,
                                        invalid_module.id)
        pkg = pm.get_package_by_identifier(mpkg)
        try:
            try:
                d = get_descriptor(mpkg, mname, mnamespace)
            except MissingModule, e:
                r = pkg.report_missing_module(mname, mnamespace)
                if not r:
                    raise e
                d = get_descriptor(mpkg, mname, mnamespace)
        except MissingModule, e:
            if mnamespace:
                nss = mnamespace + '|' + mname
            else:
                nss = mname
            msg = ("Could not upgrade module %s from package %s.\n" %
                    (mname, mpkg))
            raise UpgradeWorkflowError(msg)
        assert isinstance(d, ModuleDescriptor)
        
        def check_connection_port(port):
            try:
                s = d.get_port_spec(port.name, port.type)
                if s <> port.spec:
                    msg = ("%s connection to port %s has mismatched type" %
                           (port.type, port.name))
                    raise UpgradeWorkflowError(msg)
            except Exception:
                msg = ("%s connection to port %s does not exist." %
                       (port.type, port.name))
                raise UpgradeWorkflowError(msg)
            
        # check if connections are still valid
        for conn_id in pipeline.graph.edges_from(module_id):
            port = pipeline.connections[conn_id].source
            check_connection_port(port)
        for conn_id in pipeline.graph.edges_to(module_id):
            conn = pipeline.connections[conn_id].destination
            check_connection_port(port)

        # check if function values are still valid
        for function in invalid_module.functions:
            function_spec = function.get_spec('input')
            registry_spec = d.get_port_spec(port.name, port.type)
            if function_spec <> registry_spec:
                msg = ("mismatch on function %s." % function.name)
                raise UpgradeWorkflowError(msg)

        # If we passed all of these checks, then we consider module to
        # be automatically upgradeable. Now create actions that will delete
        # functions, module, and connections, and add new module with corresponding
        # functions and connections.

        ctrl = self._controller
        delete_action = ctrl.create_module_list_deletion_action(pipeline, [mid])
        
        addition_op_list = []
        new_module = ctrl.create_module_from_descriptor(
            d,
            invalid_module.location.x,
            invalid_module.location.y)
        addition_op_list.append(('add', new_module))
        for function in invalid_module.functions:
            new_function = ctrl.create_function(new_module, function.name)
            addition_action_list.append(('add', new_function,
                                         new_module.vtType, new_module.id))
            pvalues = []
            for param in function.params:
                pvalues.append(param.value)
            addition_op_list.extend(ctrl.update_function_ops(new_module,
                                                             [(function.name,
                                                               pvalues,
                                                               -1, True)]))
        for conn_id in pipeline.graph.edges_from(module_id):
            old_conn = pipeline.connections[conn_id]
            new_conn = ctrl.create_connection_from_ids(new_module.id,
                                                       old_conn.source.spec,
                                                       old_conn.destination.id,
                                                       old_conn.destination.spec)
            addition_op_list.append(('add', new_conn))
            
        for conn_id in pipeline.graph.edges_to(module_id):
            old_conn = pipeline.connections[conn_id]
            new_conn = ctrl.create_connection_from_ids(old_conn.source.id,
                                                       old_conn.source.spec,
                                                       new_module.id,
                                                       old_conn.destination.spec)
            addition_op_list.append(('add', new_conn))
        print addition_op_list
        add_action = core.db.action.create_action(addition_op_list)
        return [delete_action, add_action]

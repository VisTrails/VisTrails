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

"""This file contains code to handle InvalidPipeline exceptions that contain
upgrade requests."""
from vistrails.core import debug
import vistrails.core.db.action
from vistrails.core.modules.module_registry import get_module_registry, \
     ModuleDescriptor, MissingModule, MissingPort, MissingPackage
from vistrails.core.modules.utils import parse_descriptor_string, \
    create_descriptor_string, parse_port_spec_string, create_port_spec_string
from vistrails.core.packagemanager import get_package_manager
from vistrails.core.system import get_vistrails_basic_pkg_id
from vistrails.core.vistrail.annotation import Annotation
from vistrails.core.vistrail.module_control_param import ModuleControlParam
from vistrails.core.vistrail.connection import Connection
from vistrails.core.vistrail.port import Port
from vistrails.core.vistrail.port_spec import PortSpec
from vistrails.core.vistrail.port_spec_item import PortSpecItem
from vistrails.core.utils import versions_increasing
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

class UpgradeModuleRemap(object):
    def __init__(self, start_version, end_version, 
                 output_version, new_module=None,
                 dst_port_remap=None, src_port_remap=None,
                 function_remap=None, annotation_remap=None,
                 control_param_remap=None, module_name=None):
        self.module_name = module_name
        self.start_version = start_version
        self.end_version = end_version
        self.output_version = output_version
        self.new_module = new_module

        if dst_port_remap is None:
            self._dst_port_remap = {}
        else:
            self._dst_port_remap = dst_port_remap
        if src_port_remap is None:
            self._src_port_remap = {}
        else:
            self._src_port_remap = src_port_remap
        if function_remap is None:
            self._function_remap = {}
        else:
            self._function_remap = function_remap
        if annotation_remap is None:
            self._annotation_remap = {}
        else:
            self._annotation_remap = annotation_remap
        if control_param_remap is None:
            self._control_param_remap = {}
        else:
            self._control_param_remap = control_param_remap

    @classmethod
    def from_tuple(cls, module_name, t):
        if len(t) == 3:
            obj = cls(t[0], t[1], None, t[2], module_name=module_name)
            remap = None
        elif len(t) == 4:
            obj = cls(t[0], t[1], None, t[2], module_name=module_name)
            remap = t[3]
        elif len(t) == 5:
            obj = cls(t[0], t[1], t[2], t[3], module_name=module_name)
            remap = t[4]
        else:
            raise TypeError("UpgradeModuleRemap.from_tuple() got a tuple of "
                            "length %d" % len(t))
        if remap is not None:
            for remap_type, remap_dict in remap.iteritems():
                for remap_name, remap_change in remap_dict.iteritems():
                    obj.add_remap(remap_type, remap_name, remap_change)
        return obj

    def _get_dst_port_remap(self):
        return self._dst_port_remap
    dst_port_remap = property(_get_dst_port_remap)

    def _get_src_port_remap(self):
        return self._src_port_remap
    src_port_remap = property(_get_src_port_remap)
    
    def _get_function_remap(self):
        # !!! we're going to let dst_port_remap serve as a
        # base for function_remap but the developer is
        # responsible for knowing that anything beyond name
        # remaps requires different functions
        d = copy.copy(self._dst_port_remap)
        d.update(self._function_remap)
        return d
    function_remap = property(_get_function_remap)
    
    def _get_annotation_remap(self):
        return self._annotation_remap
    annotation_remap = property(_get_annotation_remap)    

    def _get_control_param_remap(self):
        return self._control_param_remap
    control_param_remap = property(_get_control_param_remap)    

    def add_remap(self, remap_type, remap_name, remap_change):
        if not hasattr(self, '_%s' % remap_type):
            raise ValueError('remap_type "%s" not allowed' % remap_type)
        d = getattr(self, '_%s' % remap_type)
        d[remap_name] = remap_change
            
        # if remap_type not in self.allowed_remaps:
        #     raise ValueError("remap_type must be one of %s" % allowed_remaps)
        # self.remap[remap_type][remap_name] = remap_change
        
    def get_remap(self, remap_type):
        if not hasattr(self, '_%s' % remap_type):
            raise ValueError('remap_type "%s" not allowed' % remap_type)
        d = getattr(self, '_%s' % remap_type)
        return d

        # if remap_type not in self.allowed_remaps:
        #     raise ValueError("remap_type must be one of %s" % allowed_remaps)
        # return self.remap[remap_type]

    def get_output_version(self):
        return self.output_version

class UpgradePackageRemap(object):
    def __init__(self):
        self.remaps = {}

    @classmethod
    def from_dict(cls, d):
        pkg_remap = cls()
        for module_name, remap_list in d.iteritems():
            for remap in remap_list:
                pkg_remap.add_module_remap(remap, module_name)
        return pkg_remap

    def add_module_remap(self, module_remap, module_name=None):
        if isinstance(module_remap, tuple):
            if module_name is None:
                raise ValueError("module_name must be specified if "
                                 "module_remap is a tuple")
            module_remap = UpgradeModuleRemap.from_tuple(module_name, 
                                                         module_remap)
        else:
            if module_name is not None:
                # assume user wants to override name
                module_remap.module_name = module_name
        if module_remap.module_name not in self.remaps:
            self.remaps[module_remap.module_name] = []
        self.remaps[module_remap.module_name].append(module_remap)

    def get_module_remaps(self, module_name):
        if module_name in self.remaps:
            return self.remaps[module_name]
        return []

    def has_module_remaps(self, module_name):
        return module_name in self.remaps

    def get_module_upgrade(self, module_name, old_version):
        for module_remap in self.get_module_remaps(module_name):
            if ((module_remap.start_version is None or 
                 not versions_increasing(old_version, 
                                         module_remap.start_version)) and
                (module_remap.end_version is None or
                 versions_increasing(old_version, 
                                     module_remap.end_version))):
                return module_remap
        return None

class UpgradeWorkflowHandler(object):

    @staticmethod
    def dispatch_request(controller, module_id, current_pipeline):
        pm = get_package_manager()
        if module_id not in current_pipeline.modules:
            # It is possible that some other upgrade request has
            # already removed the invalid module of this request. In
            # that case, disregard the request.
            debug.log("module %s already handled. skipping" % module_id)
            return []
        invalid_module = current_pipeline.modules[module_id]
        pkg = pm.get_package(invalid_module.package)
        if hasattr(pkg.module, 'handle_module_upgrade_request'):
            f = pkg.module.handle_module_upgrade_request
            return f(controller, module_id, current_pipeline)
        elif hasattr(pkg.module, '_upgrades'):
            return UpgradeWorkflowHandler.remap_module(controller, module_id, 
                                                       current_pipeline,
                                                       pkg.module._upgrades)
        else:
            debug.log('Package "%s" cannot handle upgrade request. '
                      'VisTrails will attempt automatic upgrade.' % \
                          pkg.identifier)
            auto_upgrade = UpgradeWorkflowHandler.attempt_automatic_upgrade
            return auto_upgrade(controller, current_pipeline, module_id)

    @staticmethod
    def check_port_spec(module, port_name, port_type, descriptor=None, 
                        sigstring=None):
        basic_pkg = get_vistrails_basic_pkg_id()

        reg = get_module_registry()
        found = False
        try:
            if descriptor is not None:
                s = reg.get_port_spec_from_descriptor(descriptor, port_name,
                                                      port_type)
                found = True

                spec_tuples = parse_port_spec_string(sigstring, basic_pkg)
                for i in xrange(len(spec_tuples)):
                    spec_tuple = spec_tuples[i]
                    port_pkg = reg.get_package_by_name(spec_tuple[0])
                    if port_pkg.identifier != spec_tuple[0]:
                        # we have an old identifier
                        spec_tuples[i] = (port_pkg.identifier,) + spec_tuple[1:]
                sigstring = create_port_spec_string(spec_tuples)
                # sigstring = expand_port_spec_string(sigstring, basic_pkg)
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
        reg = get_module_registry()

        get_descriptor = reg.get_descriptor_by_name
        pm = get_package_manager()
        invalid_module = pipeline.modules[module_id]
        mpkg, mname, mnamespace, mid = (invalid_module.package,
                                        invalid_module.name,
                                        invalid_module.namespace,
                                        invalid_module.id)
        pkg = pm.get_package(mpkg)
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
    def check_upgrade(pipeline, module_id, d, function_remap=None,
                      src_port_remap=None, dst_port_remap=None):
        if function_remap is None:
            function_remap = {}
        if src_port_remap is None:
            src_port_remap = {}
        if dst_port_remap is None:
            dst_port_remap = {}
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
                                  function_remap=None, src_port_remap=None, 
                                  dst_port_remap=None, annotation_remap=None,
                                  control_param_remap=None):
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
                    (nss, mpkg))
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
                                                     annotation_remap,
                                                     control_param_remap)

    @staticmethod
    def create_new_connection(controller, src_module, src_port, 
                              dst_module, dst_port):
        # spec -> name, type, signature
        output_port_id = controller.id_scope.getNewId(Port.vtType)
        if isinstance(src_port, basestring):
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
        if isinstance(dst_port, basestring):
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
                        function_remap=None, src_port_remap=None, 
                        dst_port_remap=None, annotation_remap=None,
                        control_param_remap=None, use_registry=True):
        if function_remap is None:
            function_remap = {}
        if src_port_remap is None:
            src_port_remap = {}
        if dst_port_remap is None:
            dst_port_remap = {}
        if annotation_remap is None:
            annotation_remap = {}
        if control_param_remap is None:
            control_param_remap = {}

        basic_pkg = get_vistrails_basic_pkg_id()

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
                elif not isinstance(remap, basestring):
                    ops.extend(remap(annotation))
                    continue
                else:
                    annotation_key = remap

            new_annotation = \
                Annotation(id=controller.id_scope.getNewId(Annotation.vtType),
                           key=annotation_key,
                           value=annotation.value)
            new_module.add_annotation(new_annotation)

        for control_param in old_module.control_parameters:
            if control_param.name not in control_param_remap:
                control_param_name = control_param.name
            else:
                remap = control_param_remap[control_param.name]
                if remap is None:
                    # don't add the control param back in
                    continue
                elif not isinstance(remap, basestring):
                    ops.extend(remap(control_param))
                    continue
                else:
                    control_param_name = remap

            new_control_param = \
                ModuleControlParam(id=controller.id_scope.getNewId(
                                                   ModuleControlParam.vtType),
                                   name=control_param_name,
                                   value=control_param.value)
            new_module.add_control_parameter(new_control_param)

        if not old_module.is_group() and not old_module.is_abstraction():
            for port_spec in old_module.port_spec_list:
                if port_spec.type == 'input':
                    if port_spec.name not in dst_port_remap:
                        spec_name = port_spec.name
                    else:
                        remap = dst_port_remap[port_spec.name]
                        if remap is None:
                            continue
                        elif not isinstance(remap, basestring):
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
                        elif not isinstance(remap, basestring):
                            ops.extend(remap(port_spec))
                            continue
                        else:
                            spec_name = remap                
                new_spec = port_spec.do_copy(True, controller.id_scope, {})
                new_spec.name = spec_name
                new_module.add_port_spec(new_spec)

        function_ops = []
        for function in old_module.functions:
            if function.name not in function_remap:
                function_name = function.name
            else:
                remap = function_remap[function.name]
                if remap is None:
                    # don't add the function back in
                    continue                    
                elif not isinstance(remap, basestring):
                    function_ops.extend(remap(function, new_module))
                    continue
                else:
                    function_name = remap

            if len(function.parameters) > 0:
                new_param_vals, aliases = zip(*[(p.strValue, p.alias) 
                                                for p in function.parameters])
            else:
                new_param_vals = []
                aliases = []
            if use_registry:
                function_port_spec = function_name
            else:
                def mk_psi(pos):
                    psi = PortSpecItem(module="Module", package=basic_pkg,
                                       namespace="", pos=pos)
                    return psi
                n_items = len(new_param_vals)
                function_port_spec = PortSpec(name=function_name,
                                              items=[mk_psi(i) 
                                                     for i in xrange(n_items)])
            new_function = controller.create_function(new_module, 
                                                      function_port_spec,
                                                      new_param_vals,
                                                      aliases)
            new_module.add_function(new_function)

        if None in function_remap:
            # used to add new functions
            remap = function_remap[None]
            function_ops.extend(remap(None, new_module))

        # add the new module
        ops.append(('add', new_module))
        ops.extend(function_ops)

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
                elif not isinstance(remap, basestring):
                    ops.extend(remap(old_conn, new_module))
                    continue
                else:
                    source_name = remap
                    
            old_dst_module = pipeline.modules[old_conn.destination.moduleId]
            if use_registry:
                source_port = source_name
            else:
                source_port = Port(name=source_name,
                                   type='source',
                                   signature=create_port_spec_string(
                                       [(basic_pkg, 'Variant', '')]))

            new_conn = create_new_connection(controller,
                                             new_module,
                                             source_port,
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
                elif not isinstance(remap, basestring):
                    ops.extend(remap(old_conn, new_module))
                    continue
                else:
                    destination_name = remap
                    
            old_src_module = pipeline.modules[old_conn.source.moduleId]
            if use_registry:
                destination_port = destination_name
            else:
                destination_port = Port(name=destination_name,
                                        type='destination',
                                        signature=create_port_spec_string(
                                            [(basic_pkg, 'Variant', '')]))

            new_conn = create_new_connection(controller,
                                             old_src_module,
                                             old_conn.source,
                                             new_module,
                                             destination_port)
            ops.append(('add', new_conn))
        
        return [vistrails.core.db.action.create_action(ops)]

    @staticmethod
    def replace_group(controller, pipeline, module_id, new_subpipeline):
        basic_pkg = get_vistrails_basic_pkg_id()
        old_group = pipeline.modules[module_id]
        new_group = controller.create_module(basic_pkg, 'Group', '', 
                                             old_group.location.x, 
                                             old_group.location.y)
        new_group.pipeline = new_subpipeline
        return UpgradeWorkflowHandler.replace_generic(controller, pipeline, 
                                                      old_group, new_group)

    @staticmethod
    def replace_module(controller, pipeline, module_id, new_descriptor,
                       function_remap=None, src_port_remap=None,
                       dst_port_remap=None, annotation_remap=None,
                       control_param_remap=None, use_registry=True):
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
                                                     internal_version,
                                                     not use_registry)

        return UpgradeWorkflowHandler.replace_generic(controller, pipeline, 
                                                      old_module, new_module,
                                                      function_remap, 
                                                      src_port_remap, 
                                                      dst_port_remap,
                                                      annotation_remap,
                                                      control_param_remap,
                                                      use_registry)

    @staticmethod
    def remap_module(controller, module_id, pipeline, pkg_remap):

        """remap_module offers a method to shortcut the
        specification of upgrades.  It is useful when just changing
        the names of ports or modules, but can also be used to add
        intermediate modules or change the format of parameters.  It
        is usually called from handle_module_upgrade_request, and the
        first three arguments are passed from the arguments to that
        method.

        pkg_remap specifies all of the changes and is of the format
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
        pkg_remap = {'FileSink': [(None, '1.5.1', FileSink,
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
        old_version = old_module.version
        old_desc_str = create_descriptor_string(old_module.package,
                                                old_module.name,
                                                old_module.namespace,
                                                False)
        # print 'running module_upgrade_request', old_module.name
        if not isinstance(pkg_remap, UpgradePackageRemap):
            pkg_remap = UpgradePackageRemap.from_dict(pkg_remap)
        

        action_list = []

        old_module_t = \
            (old_module.package, old_module.name, old_module.namespace)
        module_remap = pkg_remap.get_module_upgrade(old_desc_str, old_version)
        tmp_pipeline = copy.copy(pipeline)
        while module_remap is not None:
            new_module_type = module_remap.new_module
            if new_module_type is None:
                new_module_t = old_module_t
            elif isinstance(new_module_type, basestring):
                new_module_t = parse_descriptor_string(new_module_type,
                                                       old_module_t[0])
            else:
                new_module_desc = reg.get_descriptor(new_module_type)
                new_module_t = new_module_desc.spec_tuple

            new_pkg_version = module_remap.output_version
            if (new_pkg_version is None or
                  reg.get_package_by_name(new_module_t[0]).version == new_pkg_version):
                # upgrading to the current version
                try:
                    new_module_desc = reg.get_descriptor_by_name(*new_module_t)
                except MissingModule, e:
                    # if the replacement is an abstraction,
                    # and it has been upgraded, we use that
                    if reg.has_abs_upgrade(*new_module_t):
                        new_module_desc = reg.get_abs_upgrade(*new_module_t)
                    else:
                        raise e
                use_registry = True
                next_module_remap = None
            else:
                new_module_desc = ModuleDescriptor(package=new_module_t[0],
                                                   name=new_module_t[1],
                                                   namespace=new_module_t[2],
                                                   version=new_pkg_version)
                use_registry = False

                # need to try more upgrades since this one isn't current
                old_desc_str = create_descriptor_string(new_module_t[0],
                                                        new_module_t[1],
                                                        new_module_t[2],
                                                        False)
                old_version = new_pkg_version
                next_module_remap = pkg_remap.get_module_upgrade(old_desc_str,
                                                            old_version)
                old_module_t = new_module_t
            replace_module = UpgradeWorkflowHandler.replace_module
            actions = replace_module(controller, 
                                     tmp_pipeline,
                                     module_id, 
                                     new_module_desc,
                                     module_remap.function_remap,
                                     module_remap.src_port_remap,
                                     module_remap.dst_port_remap,
                                     module_remap.annotation_remap,
                                     module_remap.control_param_remap,
                                     use_registry)

            for a in actions:
                for op in a.operations:
                    # Update the id of the module being updated
                    if op.vtType == 'add' and op.what == 'module':
                        module_id = op.objectId
                tmp_pipeline.perform_action(a)

            action_list.extend(actions)
            module_remap = next_module_remap
        if len(action_list) > 0:
            return action_list

        # otherwise, just try to automatic upgrade
        # attempt_automatic_upgrade
        return UpgradeWorkflowHandler.attempt_automatic_upgrade(controller, 
                                                                pipeline,
                                                                module_id)
    
import unittest

class TestUpgradePackageRemap(unittest.TestCase):
    def test_from_dict(self):
        def outputName_remap(old_conn, new_module):
            ops = []
            return ops
        pkg_remap_d = {'FileSink': [(None, '1.5.1', None,
                                     {'dst_port_remap':
                                      {'overrideFile': 'overwrite',
                                       'outputName': outputName_remap},
                                      'function_remap':
                                      {'overrideFile': 'overwrite',
                                       'outputName': 'outputPath'}})]}
        pkg_remap = UpgradePackageRemap.from_dict(pkg_remap_d)

    def create_workflow(self, c):
        upgrade_test_pkg = 'org.vistrails.vistrails.tests.upgrade'

        d1 = ModuleDescriptor(package=upgrade_test_pkg,
                              name='TestUpgradeA',
                              namespace='',
                              package_version='0.8')
        m1 = c.create_module_from_descriptor(d1, use_desc_pkg_version=True)
        m1.is_valid = False
        c.add_module_action(m1)

        d2 = ModuleDescriptor(package=upgrade_test_pkg,
                              name='TestUpgradeB',
                              namespace='',
                              package_version = '0.8')
        m2 = c.create_module_from_descriptor(d2, use_desc_pkg_version=True)
        m2.is_valid = False
        c.add_module_action(m2)

        basic_pkg = get_vistrails_basic_pkg_id()
        psi = PortSpecItem(module="Float", package=basic_pkg,
                           namespace="", pos=0)
        function_port_spec = PortSpec(name="a", type="input", items=[psi])
        f = c.create_function(m1, function_port_spec, [12])
        c.add_function_action(m1, f)

        conn_out_psi = PortSpecItem(module="Integer", package=basic_pkg,
                                    namespace="", pos=0)
        conn_out_spec = PortSpec(name="z", type="output",
                                 items=[conn_out_psi])
        conn_in_psi = PortSpecItem(module="Integer", package=basic_pkg,
                                   namespace="", pos=0)
        conn_in_spec = PortSpec(name="b", type="input",
                                items=[conn_in_psi])
        conn = c.create_connection(m1, conn_out_spec, m2, conn_in_spec)
        c.add_connection_action(conn)
        return c.current_version

    def run_multi_upgrade_test(self, pkg_remap):
        from vistrails.core.application import get_vistrails_application

        app = get_vistrails_application()
        created_vistrail = False
        try:
            pm = get_package_manager()
            pm.late_enable_package('upgrades',
                                   {'upgrades':
                                    'vistrails.tests.resources.'})
            app.new_vistrail()
            created_vistrail = True
            c = app.get_controller()
            self.create_workflow(c)
        
            p = c.current_pipeline
            actions = UpgradeWorkflowHandler.remap_module(c, 0, p, pkg_remap)
        finally:
            if created_vistrail:
                app.close_vistrail()
            try:
                pm.late_disable_package('upgrades')
            except MissingPackage:
                pass

    def test_multi_upgrade_obj(self):
        module_remap_1 = UpgradeModuleRemap('0.8', '0.9', '0.9', None,
                                            module_name="TestUpgradeA")
        module_remap_1.add_remap('function_remap', 'a', 'aa')
        module_remap_1.add_remap('src_port_remap', 'z', 'zz')
        module_remap_2 = UpgradeModuleRemap('0.9', '1.0', '1.0', None,
                                            module_name="TestUpgradeA")
        module_remap_2.add_remap('function_remap', 'aa', 'aaa')
        module_remap_2.add_remap('src_port_remap', 'zz', 'zzz')
        pkg_remap = UpgradePackageRemap()
        pkg_remap.add_module_remap(module_remap_1)
        pkg_remap.add_module_remap(module_remap_2)
        self.run_multi_upgrade_test(pkg_remap)

    def test_multi_upgrade_dict(self):
        pkg_remap = {"TestUpgradeA": 
                     [UpgradeModuleRemap('0.8', '0.9', '0.9', None,
                                         function_remap={'a': 'aa'},
                                         src_port_remap={'z': 'zz'}),
                      UpgradeModuleRemap('0.9', '1.0', '1.0', None,
                                         function_remap={'aa': 'aaa'},
                                         src_port_remap={'zz': 'zzz'})]}
        self.run_multi_upgrade_test(pkg_remap)

    def test_multi_upgrade_legacy(self):
        # note that remap specifies the 0.8 -> 1.0 upgrade directly as
        # must be the case for legacy upgrades
        pkg_remap = {"TestUpgradeA": [('0.8', '1.0', None,
                                       {"function_remap": {'a': 'aaa'},
                                        "src_port_remap": {'z': 'zzz'}}),
                                      ('0.9', '1.0', None,
                                       {"function_remap": {'aa': 'aaa'},
                                        "src_port_remap": {'zz': 'zzz'}})]}
        self.run_multi_upgrade_test(pkg_remap)

    def test_multi_upgrade_rename(self):
        pkg_remap = {"TestUpgradeA": 
                     [UpgradeModuleRemap('0.8', '0.9', '0.9', "TestUpgradeB",
                                         dst_port_remap={'a': 'b'},
                                         src_port_remap={'z': 'zz'})],
                     "TestUpgradeB":
                     [UpgradeModuleRemap('0.9', '1.0', '1.0', None,
                                         src_port_remap={'zz': None})]}
        self.run_multi_upgrade_test(pkg_remap)

    def test_external_upgrade(self):
        from vistrails.core.application import get_vistrails_application

        app = get_vistrails_application()
        default_upgrades = app.temp_configuration.upgrades
        default_upgrade_delay = app.temp_configuration.upgradeDelay
        app.temp_configuration.upgrades = True
        app.temp_configuration.upgradeDelay = False

        created_vistrail = False
        try:
            pm = get_package_manager()
            pm.late_enable_package('upgrades',
                                   {'upgrades':
                                    'vistrails.tests.resources.'})
            app.new_vistrail()
            created_vistrail = True
            c = app.get_controller()
            current_version = self.create_workflow(c)
            for m in c.current_pipeline.modules.itervalues():
                self.assertEqual(m.version, '0.8')

            c.change_selected_version(current_version, from_root=True)
            
            self.assertEqual(len(c.current_pipeline.modules), 2)
            for m in c.current_pipeline.modules.itervalues():
                self.assertEqual(m.version, '1.0')
                if m.name == "TestUpgradeA":
                    self.assertEqual(m.functions[0].name, 'aaa')
            self.assertEqual(len(c.current_pipeline.connections), 1)
            conn = c.current_pipeline.connections.values()[0]
            self.assertEqual(conn.source.name, 'zzz')
            self.assertEqual(conn.destination.name, 'b')
                
        finally:
            if created_vistrail:
                app.close_vistrail()
            try:
                pm.late_disable_package('upgrades')
            except MissingPackage:
                pass
            app.temp_configuration.upgrades = default_upgrades
            app.temp_configuration.upgradeDelay = default_upgrade_delay

if __name__ == '__main__':
    import vistrails.core.application

    vistrails.core.application.init()
    unittest.main()

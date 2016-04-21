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
from itertools import izip
import os
import uuid
import re
import shutil
import tempfile

from vistrails.core.configuration import get_vistrails_configuration
import vistrails.core.db.action
import vistrails.core.db.io
import vistrails.core.db.locator
from vistrails.core import debug
from vistrails.core.data_structures.graph import Graph
from vistrails.core.interpreter.default import get_default_interpreter
from vistrails.core.vistrail.job import JobMonitor
from vistrails.core.layout.workflow_layout import WorkflowLayout, \
    Pipeline as LayoutPipeline, Defaults as LayoutDefaults
from vistrails.core.log.controller import LogController, DummyLogController
from vistrails.core.log.log import Log
from vistrails.core.modules.abstraction import identifier as abstraction_pkg, \
    version as abstraction_ver
from vistrails.core.modules.basic_modules import identifier as basic_pkg
from vistrails.core.modules.module_descriptor import ModuleDescriptor
import vistrails.core.modules.module_registry
from vistrails.core.modules.module_registry import ModuleRegistryException, \
    MissingModuleVersion, MissingModule, MissingPackageVersion, MissingPort, \
    MissingPackage, PortsIncompatible
from vistrails.core.modules.package import Package
from vistrails.core.modules.sub_module import new_abstraction, read_vistrail, \
    get_all_abs_namespaces, get_cur_abs_namespace, get_next_abs_annotation_key, save_abstraction, parse_abstraction_name
from vistrails.core.packagemanager import get_package_manager
import vistrails.core.packagerepository
from vistrails.core.thumbnails import ThumbnailCache
from vistrails.core.upgradeworkflow import UpgradeWorkflowHandler, UpgradeWorkflowError
from vistrails.core.utils import VistrailsInternalError, PortAlreadyExists, DummyView, \
    InvalidPipeline
from vistrails.core.system import vistrails_default_file_type, \
    get_vistrails_directory
from vistrails.core.vistrail.abstraction import Abstraction
from vistrails.core.vistrail.action import Action
from vistrails.core.vistrail.annotation import Annotation
from vistrails.core.vistrail.connection import Connection
from vistrails.core.vistrail.group import Group
from vistrails.core.vistrail.location import Location
from vistrails.core.vistrail.module import Module
from vistrails.core.vistrail.module_control_param import ModuleControlParam
from vistrails.core.vistrail.module_function import ModuleFunction
from vistrails.core.vistrail.module_param import ModuleParam
from vistrails.core.vistrail.pipeline import Pipeline
from vistrails.core.vistrail.port import Port
from vistrails.core.vistrail.port_spec import PortSpec
from vistrails.core.vistrail.port_spec_item import PortSpecItem
from vistrails.core.vistrail.vistrail import Vistrail
from vistrails.core.theme import DefaultCoreTheme
from vistrails.db import VistrailsDBException
from vistrails.db.domain import IdScope, DBWorkflowExec
from vistrails.db.services.io import create_temp_folder, remove_temp_folder
from vistrails.db.services.io import SaveBundle, open_vt_log_from_db
from vistrails.db.services.vistrail import getSharedRoot
from vistrails.core.utils import any


def vt_action(description_or_f=None):
    def get_f(f, description=None):
        def new_f(self, *args, **kwargs):
            self.flush_delayed_actions()
            action = f(self, *args, **kwargs)
            if action is not None:
                self.add_new_action(action, description)
                self.perform_action(action)
            return action
        return new_f

    if isinstance(description_or_f, basestring):
        d = description_or_f
        def wrap(f):
            return get_f(f, d)
        return wrap
    else:
        return get_f(description_or_f)

class CompareThumbnailsError(Exception):

    def __init__(self, msg, first=None, second=None):
        Exception.__init__(self, msg)
        self._msg = msg
        self._first = first
        self._second = second
        
    def __str__(self):
        return "Comparing thumbnails failed.\n%s\n%s\n%s" % \
            (self._msg, self._first, self._second)

def dot_escape(s):
    return '"%s"' % s.replace('\\', '\\\\').replace('"', '\\"')

custom_color_key = '__color__'

custom_color_fmt = re.compile(r'^([0-9]+) *, *([0-9]+) *, *([0-9]+)$')

def parse_custom_color(color):
    m = custom_color_fmt.match(color)
    if not m:
        raise ValueError("Color annotation doesn't match format")
    return tuple(int(m.group(i)) for i in xrange(1, 4))

class VistrailController(object):
    def __init__(self, vistrail=None, locator=None, abstractions=None, 
                 thumbnails=None, mashups=None, id_scope=None, 
                 set_log_on_vt=True, auto_save=True):
        self.vistrail = None
        self.locator = None
        self._auto_save = auto_save
        self.name = ''
        self.file_name = ''
        self.is_abstraction = False
        self.changed = False
        self._upgrade_rev_map = None

        # if _cache_pipelines is True, cache pipelines to speed up
        # version switching
        self._cache_pipelines = True
        self.flush_pipeline_cache()
        self._current_full_graph = None
        self._current_terse_graph = None
        self.show_upgrades = False
        # if delayed_update is True, version tree and 'changed' status
        # needs to be updated
        self.delayed_update = False
        self.num_versions_always_shown = 1

        # if self.search is True, vistrail is currently being searched
        self.search = None
        self.search_str = None
        # If self.refine is True, search mismatches are hidden instead
        # of ghosted
        self.refine = False
        self.full_tree = False

        self._asked_packages = set()
        self._delayed_actions = []
        self._delayed_paramexps = []
        self._delayed_mashups = []
        self._loaded_abstractions = {}
        
        # This will just store the mashups in memory and send them to SaveBundle
        # when writing the vistrail
        self._mashups = []

        # the redo stack stores the undone action ids 
        # (undo is automatic with us, through the version tree)
        self.redo_stack = []

        # this is a reference to the current parameter exploration
        self.current_parameter_exploration = None
        
        # theme used to estimate module size for layout
        self.layoutTheme = DefaultCoreTheme()
        
        self.set_vistrail(vistrail, locator,
                          abstractions=abstractions, 
                          thumbnails=thumbnails,
                          mashups=mashups,
                          id_scope=id_scope, 
                          set_log_on_vt=set_log_on_vt)

    # allow gui.vistrail_controller to reference individual views
    def _get_current_version(self):
        return self._current_version
    def _set_current_version(self, version):
        self._current_version = version
    current_version = property(_get_current_version, _set_current_version)

    def _get_current_base_version(self):
        version = self.current_version
        if self._upgrade_rev_map:
            return self._upgrade_rev_map.get(version, version)
        else:
            return version
    current_base_version = property(_get_current_base_version)

    def _get_current_pipeline(self):
        return self._current_pipeline
    def _set_current_pipeline(self, pipeline):
        self._current_pipeline = pipeline
    current_pipeline = property(_get_current_pipeline, _set_current_pipeline)

    def flush_pipeline_cache(self):
        self._pipelines = {0: Pipeline()}

    def logging_on(self):
        return get_vistrails_configuration().check('executionLog')
            
    def get_logger(self):
        if self.logging_on():
            return LogController(self.log)
        else:
            return DummyLogController
        
    def get_locator(self):
        return self.locator
    
    def set_vistrail(self, vistrail, locator, abstractions=None, 
                     thumbnails=None, mashups=None, id_scope=None,
                     set_log_on_vt=True):
        self.vistrail = vistrail
        self.id_scope = id_scope
        self.current_session = -1
        self.log = Log()
        self.flush_pipeline_cache()
        self.clear_delayed_actions()
        if self.vistrail is not None:
            self.id_scope = self.vistrail.idScope
            self.current_session = self.vistrail.idScope.getNewId("session")
            self.vistrail.current_session = self.current_session
            if set_log_on_vt:
                self.vistrail.log = self.log
            if abstractions is not None:
                self.ensure_abstractions_loaded(self.vistrail, abstractions)
            if thumbnails is not None:
                ThumbnailCache.getInstance().add_entries_from_files(thumbnails)
            if mashups is not None:
                self._mashups = mashups
            job_annotation = vistrail.get_annotation('__jobs__')
            self.jobMonitor = JobMonitor(job_annotation and job_annotation.value)
        else:
            self.jobMonitor = JobMonitor()

        self.current_version = -1
        self.current_pipeline = Pipeline()
        if self.locator != locator and self.locator is not None:
            self.locator.clean_temporaries()
        self.locator = locator
        if self.locator is not None:
            self.set_file_name(locator.name)
        else:
            self.set_file_name('')
        if self.locator and self.locator.has_temporaries():
            self.set_changed(True)
        if self.vistrail is not None:
            self.recompute_terse_graph()

    def close_vistrail(self, locator):
        if not self.vistrail.is_abstraction:
            self.unload_abstractions()
        if locator is not None:
            locator.clean_temporaries()
            locator.close()

    def cleanup(self):
        pass

    def set_id_scope(self, id_scope):
        self.id_scope = id_scope

    def set_changed(self, changed):
        """ set_changed(changed: bool) -> None
        Set the current state of changed and emit signal accordingly
        
        """
        if changed!=self.changed:
            self.changed = changed
        
    def set_file_name(self, file_name):
        """ set_file_name(file_name: str) -> None
        Change the controller file name
        
        """
        if file_name is None:
            file_name = ''
        if self.file_name!=file_name:
            self.file_name = file_name
            self.name = os.path.split(file_name)[1]
            if self.name=='':
                self.name = 'untitled%s'%vistrails_default_file_type()
                
    def check_alias(self, name):
        """check_alias(alias) -> Boolean 
        Returns True if current pipeline has an alias named name """
        # FIXME Why isn't this call on the pipeline?
        return self.current_pipeline.has_alias(name)
    
    def check_vistrail_variable(self, name):
        """check_vistrail_variable(var) -> Boolean
        Returns True if vistrail has a variable named name """
        if self.vistrail:
            return self.vistrail.has_vistrail_var(name)
        return False
    
    def set_vistrail_variable(self, name, value=None, set_changed=True):
        """set_vistrail_variable(var) -> Boolean
        Returns True if vistrail variable was changed """
        if self.vistrail:
            changed = self.vistrail.set_vistrail_var(name, value)
            if changed and set_changed:
                self.set_changed(changed)
            return changed
        return False

    def get_vistrail_variable(self, name):
        if self.vistrail:
            return self.vistrail.get_vistrail_var(name)
        return None

    def has_vistrail_variable_with_uuid(self, uuid):
        if self.vistrail:
            return self.vistrail.db_has_vistrailVariable_with_uuid(uuid)
        return None

    def get_vistrail_variable_by_uuid(self, uuid):
        if self.vistrail:
            return self.vistrail.db_get_vistrailVariable_by_uuid(uuid)
        return None
 
    def get_vistrail_variables(self):
        """get_vistrail_variables() -> list
        Returns the list of vistrail variables """
        if self.vistrail:
            return self.vistrail.vistrail_vars
        return []
    
    def find_vistrail_var_module(self, var_uuid):
        for m in self.current_pipeline.modules.itervalues():
            if m.is_vistrail_var() and m.get_vistrail_var() == var_uuid:
                return m
        return None

    def get_vistrail_var_pairs(self, to_module, port_name, var_uuid=None):
        connections = self.get_connections_to(self.current_pipeline, 
                                              [to_module.id], port_name)
        pipeline = self.current_pipeline
        v_pairs = {}
        for connection in connections:
            m = pipeline.modules[connection.source.moduleId]
            if m.is_vistrail_var():
                if var_uuid is None or m.get_vistrail_var() == var_uuid:
                    if m.id not in v_pairs:
                        v_pairs[m.id] = []
                    v_pairs[m.id].append(connection)
        return v_pairs

    def create_vistrail_var_module(self, descriptor, x, y, var_uuid):
        m = self.create_module_from_descriptor(descriptor, x, y)
        a = Annotation(id=self.id_scope.getNewId(Annotation.vtType),
                       key=Module.VISTRAIL_VAR_ANNOTATION,
                       value=var_uuid)
        m.add_annotation(a)
        f = self.create_function(m, "value")
        m.add_function(f)
        return m

    def check_vistrail_var_connected(self, v_module, to_module, to_port):
        connections = self.get_connections_to(self.current_pipeline, 
                                              [to_module.id], to_port)
        for connection in connections:
            if connection.source.moduleId == v_module.id:
                return True
        return False

    def check_has_vistrail_var_connected(self, to_module, port_name):
        connections = self.get_connections_to(self.current_pipeline, 
                                              [to_module.id], port_name)
        pipeline = self.current_pipeline
        for connection in connections:
            if pipeline.modules[connection.source.moduleId].is_vistrail_var():
                return True
        return False

    @vt_action("Connected vistrail variable")
    def connect_vistrail_var_action(self, connection, module=None):
        ops = []
        if module is not None:
            ops.append(('add', module))
        ops.append(('add', connection))
        action = vistrails.core.db.action.create_action(ops)
        return action
        
    def connect_vistrail_var(self, descriptor, var_uuid,
                             to_module, to_port, x, y):
        ops = []
        new_module = None
        v_module = self.find_vistrail_var_module(var_uuid)
        if v_module is None:
            v_module = self.create_vistrail_var_module(descriptor, x, y, 
                                                       var_uuid)
            new_module = v_module
        elif self.check_vistrail_var_connected(v_module, to_module, to_port):
            return (None, None)

        c = self.create_connection(v_module, "value", to_module, to_port)
        action = self.connect_vistrail_var_action(c, new_module)
        return (c, new_module)

    def delete_modules_and_connections(self, modules, connections):
        ops = []
        ops.extend([('delete', c) for c in connections])
        ops.extend([('delete', m) for m in modules])
        if len(ops) > 0:
            action = vistrails.core.db.action.create_action(ops)
            return action
        return None

    @vt_action("Disconnected vistrail variable")
    def disconnect_vistrail_vars(self, modules, connections):
        return self.delete_modules_and_connections(modules, connections)

    def get_disconnect_vistrail_vars(self, to_module, to_port, 
                                     to_var_uuid=None):
        to_delete_modules = []
        to_delete_conns = []
        v_pairs = self.get_vistrail_var_pairs(to_module, to_port, to_var_uuid)
        for (v_module_id, v_conns) in v_pairs.iteritems():
            to_delete_conns.extend(v_conns)
            total_conns = self.get_connections_from(self.current_pipeline,
                                                    [v_module_id])
            # remove v_module if it isn't connected to others
            if (len(total_conns) - len(v_conns)) < 1:
                to_delete_modules.append(
                    self.current_pipeline.modules[v_module_id])

        # action = self.delete_modules_and_connections(to_delete_modules,
        #                                              to_delete_conns)
        # if action:
        #     self.vistrail.change_description("Disconnected Vistrail Variables",
        #                                      action.id)
        return (to_delete_modules, to_delete_conns)

    def get_connected_vistrail_vars(self, module_ids, to_delete=False):
        """get_connected_vistrail_vars(module_ids: list, to_delete: bool)->list

        Returns the vistrail variables connected to the specified module_id:s
        If to_delete is true we exclude modules that have connections to
        modules not in the module_ids list

        """
        vv_modules = {}
        connections = self.get_connections_to(self.current_pipeline, 
                                              module_ids)
        pipeline = self.current_pipeline
        final_connections = []
        for connection in connections:
            m = pipeline.modules[connection.source.moduleId]
            if m.is_vistrail_var():
                if m.id not in vv_modules:
                    vv_modules[m.id] = []
                vv_modules[m.id].append(connection)
                final_connections.append(connection.id)
        if to_delete:
            for module_id, connections in vv_modules.items():
                total_conns = self.get_connections_from(self.current_pipeline,
                                                        [module_id])
                if len(total_conns) != len(connections):
                    # there are connections to other modules so don't delete
                    del vv_modules[module_id]
        return vv_modules.keys(), final_connections

    def getParameterExplorationById(self, id):
        """ getParameterExplorationById(self, id) -> ParameterExploration
        Returns a ParameterExploration given its id
        """
        if self.vistrail and \
           self.vistrail.db_has_parameter_exploration_with_id(id):
            return  self.vistrail.db_get_parameter_exploration_by_id(id)
        return None

    def getLatestParameterExplorationByVersion(self, id):
        """ getLatestParameterExplorationByVersion(self, version) ->
                                                        ParameterExploration
        Returns a parameter exploration given its action_id and
        that it has not been named
        """
        for i in xrange(len(self.vistrail.db_parameter_explorations)):
            pe = self.vistrail.db_parameter_explorations[i]
            if pe.action_id == id and not pe.name:
                return pe
        return None

    def invalidate_version_tree(self, *args, **kwargs):
        """ invalidate_version_tree(self, *args, **kwargs) -> None
        Does nothing, gui/vistrail_controller.py does, though
        """
        pass

    ##########################################################################
    # Actions, etc

    def has_move_actions(self):
        return False
    
    def flush_move_actions(self):
        return False

    def migrate_tags(self, from_version, to_version, vistrail=None):
        if vistrail is None:
            vistrail = self.vistrail
        tag = vistrail.get_tag(from_version)
        if tag:
            vistrail.set_tag(from_version, "")
            vistrail.set_tag(to_version, tag)
        notes = vistrail.get_notes(from_version)
        if notes:
            vistrail.set_notes(from_version, "")
            vistrail.set_notes(to_version, notes)

    def flush_delayed_actions(self, delay_update=False):
        start_version = self.current_version
        desc_key = Action.ANNOTATION_DESCRIPTION
        added_upgrade = False
        should_migrate_tags = get_vistrails_configuration().check("migrateTags")
        for action in self._delayed_actions:
            self.vistrail.add_action(action, start_version,
                                     self.current_session)
            # HACK to populate upgrade information
            if (action.has_annotation_with_key(desc_key) and
                action.get_annotation_by_key(desc_key).value == 'Upgrade'):
                self.vistrail.set_upgrade(start_version, str(action.id))
            if should_migrate_tags:
                self.migrate_tags(start_version, action.id)
            self.current_version = action.id
            start_version = action.id
            added_upgrade = True
        for pe in self._delayed_paramexps:
            pe.action_id = self.current_version
            self.vistrail.db_add_parameter_exploration(pe)
        for mashup in self._delayed_mashups:
            # mashup is a mashuptrail.
            # We need to update all action id references.
            mashup.vtVersion = self.current_version
            for action in mashup.actions:
                action.mashup.version = self.current_version
            self._mashups.append(mashup)

            #self.vistrail.db_add_parameter_exploration(pe)
        # We have to do moves after the delayed actions because the pipeline
        # may have been updated
        added_moves = self.flush_move_actions()
        self.clear_delayed_actions()
        if added_upgrade or added_moves:
            if delay_update:
                self.delayed_update = True
            else:
                self.recompute_terse_graph()
                self.invalidate_version_tree(False)

    def clear_delayed_actions(self):
        self._delayed_actions = []
        self._delayed_paramexps = []
        self._delayed_mashups = []


    def perform_action(self, action, do_validate=True, raise_exception=False):
        """ performAction(action: Action) -> timestep

        Performs given action on current pipeline.

        By default, the resulting pipeline will get validated, but no exception
        will be raised if it is invalid. However you will get these on your
        next call to change_selected_version().
        """
        if action is not None:
            self.current_pipeline.perform_action(action)
            self.current_version = action.db_id
            if do_validate:
                self.validate(self.current_pipeline, raise_exception)
            return action.db_id
        return None

    def add_new_action(self, action, description=None):
        """add_new_action(action) -> None

        Call this function to add a new action to the vistrail being
        controlled by the vistrailcontroller.

        FIXME: In the future, this function should watch the vistrail
        and get notified of the change.

        """
        if action is not None:
            if self.current_version == -1:
                self.change_selected_version(0)
            self.vistrail.add_action(action, self.current_version, 
                                     self.current_session)
            if description is not None:
                self.vistrail.change_description(description, action.id)
            self.current_version = action.db_id
            self.set_changed(True)
            self.recompute_terse_graph()
            
    def create_module_from_descriptor(self, *args, **kwargs):
        return self.create_module_from_descriptor_static(self.id_scope,
                                                         *args, **kwargs)

    @staticmethod
    def create_module_from_descriptor_static(id_scope, descriptor, 
                                             x=0.0, y=0.0, 
                                             internal_version=-1,
                                             use_desc_pkg_version=False):
        reg = vistrails.core.modules.module_registry.get_module_registry()
        if not use_desc_pkg_version:
            package = reg.get_package_by_name(descriptor.identifier)
            pkg_version = package.version
        else:
            pkg_version = descriptor.package_version
        loc_id = id_scope.getNewId(Location.vtType)
        location = Location(id=loc_id,
                            x=x, 
                            y=y,
                            )
        if internal_version > -1:
            # only get the current namespace if this is a local subworkflow
            if descriptor.identifier == abstraction_pkg:
                namespace = get_cur_abs_namespace(descriptor.module.vistrail)
            else:
                namespace = descriptor.namespace
            abstraction_id = id_scope.getNewId(Abstraction.vtType)
            module = Abstraction(id=abstraction_id,
                                 name=descriptor.name,
                                 package=descriptor.identifier,
                                 namespace=namespace,
                                 version=pkg_version,
                                 location=location,
                                 internal_version=internal_version,
                                 )
        elif descriptor.identifier == basic_pkg and \
                descriptor.name == 'Group':
            group_id = id_scope.getNewId(Group.vtType)
            module = Group(id=group_id,
                           name=descriptor.name,
                           package=descriptor.identifier,
                           namespace=descriptor.namespace,
                           version=pkg_version,
                           location=location,
                           )
        else:
            module_id = id_scope.getNewId(Module.vtType)
            module = Module(id=module_id,
                            name=descriptor.name,
                            package=descriptor.identifier,
                            namespace=descriptor.namespace,
                            version=pkg_version,
                            location=location,
                            )
        module.is_valid = True
        return module

    def create_module(self, *args, **kwargs):
        return self.create_module_static(self.id_scope, *args, **kwargs)

    @staticmethod
    def create_module_static(id_scope, identifier, name, namespace='', 
                             x=0.0, y=0.0, internal_version=-1):
        reg = vistrails.core.modules.module_registry.get_module_registry()
        d = reg.get_descriptor_by_name(identifier, name, namespace)
        static_call = VistrailController.create_module_from_descriptor_static
        return static_call(id_scope, d, x, y, internal_version)

    def create_old_module(self, *args, **kwargs):
        return self.create_old_module_static(self.id_scope, *args, **kwargs)

    @staticmethod
    def create_old_module_static(id_scope, identifier, name, namespace='', 
                                 version='', x=0.0, y=0.0, internal_version=-1):
        dummy_d = ModuleDescriptor(name=name, 
                                   package=identifier, 
                                   namespace=namespace, 
                                   package_version=version, 
                                   internal_version=internal_version)
        return VistrailController.create_module_from_descriptor_static(
            id_scope, dummy_d, x, y, internal_version, True)

    def create_connection_from_ids(self, output_id, output_port_spec,
                                       input_id, input_port_spec):
        output_module = self.current_pipeline.modules[output_id]
        input_module = self.current_pipeline.modules[input_id]
        return self.create_connection(output_module, output_port_spec, 
                                      input_module, input_port_spec)

    def create_connection(self, *args, **kwargs):
        return self.create_connection_static(self.id_scope, *args, **kwargs)

    @staticmethod
    def create_connection_static(id_scope, output_module, output_port_spec,
                                 input_module, input_port_spec):     
        if isinstance(output_port_spec, basestring):
            output_port_spec = \
                output_module.get_port_spec(output_port_spec, 'output')
        if isinstance(input_port_spec, basestring):
            input_port_spec = \
                input_module.get_port_spec(input_port_spec, 'input')            
        if output_port_spec is None:
            raise VistrailsInternalError("output port spec is None")
        if input_port_spec is None:
            raise VistrailsInternalError("input port spec is None")
        reg = vistrails.core.modules.module_registry.get_module_registry()
        if not reg.ports_can_connect(output_port_spec, input_port_spec):
            raise PortsIncompatible(output_module.package,
                                    output_module.name,
                                    output_module.namespace,
                                    output_port_spec.name,
                                    input_module.package,
                                    input_module.name,
                                    input_module.namespace,
                                    input_port_spec.name)
        output_port_id = id_scope.getNewId(Port.vtType)
        output_port = Port(id=output_port_id,
                           spec=output_port_spec,
                           moduleId=output_module.id,
                           moduleName=output_module.name)
        input_port_id = id_scope.getNewId(Port.vtType)
        input_port = Port(id=input_port_id,
                           spec=input_port_spec,
                           moduleId=input_module.id,
                           moduleName=input_module.name)
        conn_id = id_scope.getNewId(Connection.vtType)
        connection = Connection(id=conn_id,
                                ports=[input_port, output_port])
        return connection

    def create_param(self, *args, **kwargs):
        return self.create_param_static(self.id_scope, *args, **kwargs)

    @staticmethod
    def create_param_static(id_scope, port_spec, pos, value, alias='', 
                            query_method=None):
        param_id = id_scope.getNewId(ModuleParam.vtType)
        descriptor = port_spec.descriptors()[pos]
        param_type = descriptor.sigstring
        # FIXME add/remove description
        # FIXME make ModuleParam constructor accept port_spec
        new_param = ModuleParam(id=param_id,
                                pos=pos,
                                name='<no description>',
                                alias=alias,
                                val=value,
                                type=param_type,
                                )

        # FIXME probably should put this in the ModuleParam constructor
        new_param.queryMethod = query_method
        return new_param

    def create_params(self, *args, **kwargs):
        return self.create_params_static(self.id_scope, *args, **kwargs)

    @staticmethod
    def create_params_static(id_scope, port_spec, values, aliases=[], 
                             query_methods=[]):
        params = []
        for i in xrange(len(port_spec.descriptors())):
            if i < len(values) and values[i] is not None:
                value = str(values[i])
            else:
                value = None
            if i < len(aliases):
                alias = str(aliases[i])
            else:
                alias = ''
            if i < len(query_methods):
                query_method = query_methods[i]
            else:
                query_method = None
            param = VistrailController.create_param_static(id_scope, port_spec,
                                                           i, value, alias,
                                                           query_method)
            params.append(param)
        return params

    def create_function(self, *args, **kwargs):
        return self.create_function_static(self.id_scope, *args, **kwargs)

    @staticmethod
    def create_function_static(id_scope, module, port_spec,
                               param_values=[], aliases=[], query_methods=[]):
        if isinstance(port_spec, basestring):
            port_spec = module.get_port_spec(port_spec, 'input')
        if (len(param_values) <= 0 and port_spec.defaults is not None and
            any(d is not None for d in port_spec.defaults)):
            param_values = port_spec.defaults

        f_id = id_scope.getNewId(ModuleFunction.vtType)
        new_function = ModuleFunction(id=f_id,
                                      pos=module.getNumFunctions(),
                                      name=port_spec.name,
                                      )
        new_function.is_valid = True
        new_params = \
            VistrailController.create_params_static(id_scope, port_spec, 
                                                    param_values, aliases,
                                                    query_methods)
        new_function.add_parameters(new_params)        
        return new_function

    def create_functions(self, *args, **kwargs):
        return self.create_functions_static(self.id_scope, *args, **kwargs)

    @staticmethod
    def create_functions_static(id_scope, module, functions):
        """create_functions(module: Module,
                            functions: [function_name: str,
                                        param_values: [str]]) 
            -> [ModuleFunction]
        
        """
        static_call = VistrailController.create_function_static
        return [static_call(id_scope, module, *f) for f in functions]

    def create_port_spec(self, *args, **kwargs):
        return self.create_port_spec_static(self.id_scope, *args, **kwargs)
    
    @staticmethod
    def create_port_spec_static(id_scope, module, port_type, port_name, 
                                port_sigstring, port_sort_key=-1,
                                port_depth=0):
        p_id = id_scope.getNewId(PortSpec.vtType)
        port_spec = PortSpec(id=p_id,
                             type=port_type,
                             name=port_name,
                             sigstring=port_sigstring,
                             sort_key=port_sort_key,
                             depth=port_depth
                             )
        # don't know how many port spec items are created until after...
        for psi in port_spec.port_spec_items:
            psi.id = id_scope.getNewId(PortSpecItem.vtType)
        return port_spec

    def get_module_connection_ids(self, module_ids, graph):
        connection_ids = set()
        for module_id in module_ids:
            for v, id in graph.edges_from(module_id):
                connection_ids.add(id)
            for v, id in graph.edges_to(module_id):
                connection_ids.add(id)
        return connection_ids

    def delete_module_list_ops(self, pipeline, module_ids):
        graph = pipeline.graph
        connect_ids = self.get_module_connection_ids(module_ids, graph)
        ops = []
        for c_id in connect_ids:
            ops.append(('delete', pipeline.connections[c_id]))
        for m_id in module_ids:
            ops.append(('delete', pipeline.modules[m_id]))
        return ops

    def update_port_spec_ops(self, module, deleted_ports, added_ports):
        op_list = []
        deleted_port_info = set()
        changed_port_info = set()
        for p in deleted_ports:
            port_info = (p[1], p[0])
            if module.has_portSpec_with_name(port_info):
                port = module.get_portSpec_by_name(port_info)
                deleted_port_info.add(port_info + (port.sigstring,))
        for p in added_ports:
            port_info = (p[1], p[0], p[2])
            if port_info in deleted_port_info:
                changed_port_info.add(port_info[:2])
            
        # Remove any connections related to deleted ports
        for c in self.current_pipeline.connections.itervalues():
            if ((c.sourceId == module.id and
                 any(c.source.name == p[1] for p in deleted_ports
                     if (p[1], p[0]) not in changed_port_info)) or
                (c.destinationId == module.id and
                 any(c.destination.name == p[1] for p in deleted_ports
                     if (p[1], p[0]) not in changed_port_info))):
                op_list.append(('delete', c))

        # Remove any functions related to deleted ports
        for p in deleted_ports:
            if (p[1], p[0]) not in changed_port_info:
                for function in module.functions:
                    if function.name == p[1]:
                        op_list.append(('delete', function, 
                                        Module.vtType, module.id))

        # Remove all deleted ports
        # !! Reset delted_port_info to not store sigstring
        deleted_port_info = set()
        for p in deleted_ports:
            port_info = (p[1], p[0])
            if module.has_portSpec_with_name(port_info):
                port_spec = module.get_portSpec_by_name(port_info)
                op_list.append(('delete', port_spec, Module.vtType, module.id))
                deleted_port_info.add(port_info)

        # Add all added ports
        for p in added_ports:
            if (p[1], p[0]) not in deleted_port_info and \
                    module.has_port_spec(p[1], p[0]):
                raise PortAlreadyExists(module.package, module.name, p[0], p[1])
            port_spec = self.create_port_spec(module, *p)
            op_list.append(('add', port_spec, Module.vtType, module.id))
        return op_list

    def update_function_ops(self, module, function_name, param_values=[],
                            old_id=-1L, should_replace=True, aliases=[],
                            query_methods=[]):
        """NOTE: aliases will be removed in the future!"""
        op_list = []
        port_spec = module.get_port_spec(function_name, 'input')

        if should_replace and old_id < 0:
            for old_function in module.functions:
                if old_function.name == function_name:
                    old_id = old_function.real_id

        # ensure that replacements don't happen for functions that
        # shouldn't be replaced
        if should_replace and old_id >= 0:
            function = module.function_idx[old_id]
            if param_values is None:
                op_list.append(('delete', function, module.vtType, module.id))
            else:
                for i, new_param_value in enumerate(param_values):
                    old_param = function.params[i]
                    if ((len(aliases) > i and old_param.alias != aliases[i]) or
                        (len(query_methods) > i and 
                         old_param.queryMethod != query_methods[i]) or
                        (old_param.strValue != new_param_value)):
                        if len(aliases) > i:
                            alias = aliases[i]
                        else:
                            alias = ''
                        if len(query_methods) > i:
                            query_method = query_methods[i]
                        else:
                            query_method = None
                        new_param = self.create_param(port_spec, i, 
                                                      new_param_value, alias,
                                                      query_method)
                        op_list.append(('change', old_param, new_param,
                                        function.vtType, function.real_id))
        elif param_values is not None:
            if len(param_values) < 1:
                new_function = self.create_function(module, function_name,
                                                    param_values, aliases,
                                                    query_methods)
                op_list.append(('add', new_function,
                                module.vtType, module.id))        
            else:
                psis = port_spec.port_spec_items
                found = False
                for param_value, psi in izip(param_values, psis):
                    if param_value != psi.default:
                        found = True
                        break
                if found:
                    new_function = self.create_function(module, function_name,
                                                        param_values, aliases,
                                                        query_methods)
                    op_list.append(('add', new_function,
                                    module.vtType, module.id))
        return op_list

    def update_functions_ops(self, module, functions):
        """update_functions_ops(module: Module, 
                                functions: [function_name: str,
                                            param_values: [str],
                                            old_id: long (-1)
                                            should_replace: bool (True)])
            -> [Op]
        Returns a list of operations that will create and update the
        functions of the specified module with new values.

        """
        op_list = []
        for f in functions:
            op_list.extend(self.update_function_ops(module, *f))
        return op_list

    def create_updated_parameter(self, old_param, new_value):
        """update_parameter(old_param: ModuleParam, new_value: str)
              -> ModuleParam
        Generates a change parameter action if the value is different

        """
        if old_param.strValue == new_value:
            return None

        param_id = self.id_scope.getNewId(ModuleParam.vtType)
        new_param = ModuleParam(id=param_id,
                                pos=old_param.pos,
                                name=old_param.name,
                                alias=old_param.alias,
                                val=new_value,
                                type=old_param.typeStr,
                                )
        return new_param

    def update_annotation_ops(self, module, annotations):
        """update_annotation_ops(module: Module, annotations: [(str, str)])
              -> [operation_list]
        
        """
        op_list = []
        for (key, value) in annotations:
            a_id = self.id_scope.getNewId(Annotation.vtType)
            annotation = Annotation(id=a_id,
                                    key=key, 
                                    value=value,
                                    )
            if module.has_annotation_with_key(key):
                old_annotation = module.get_annotation_by_key(key)
                op_list.append(('change', old_annotation, annotation,
                                module.vtType, module.id))
            else:
                op_list.append(('add', annotation, module.vtType, module.id))
        return op_list

    def check_subworkflow_versions(self, changed_subworkflow_desc):
        if self.current_pipeline is not None:
            self.current_pipeline.check_subworkflow_versions()

    @vt_action
    def add_module_action(self, module):
        action = vistrails.core.db.action.create_action([('add', module)])
        return action

    def add_module_from_descriptor(self, descriptor, x=0.0, y=0.0, 
                                   internal_version=-1):
        module = self.create_module_from_descriptor(descriptor, x, y, 
                                                    internal_version)
        action = self.add_module_action(module)
        return module


    def add_module(self, identifier, name, namespace='', x=0.0, y=0.0, 
                   internal_version=-1):
        """ addModule(x: int, y: int, identifier, name: str, namespace='') 
               -> Module
        Add a new module into the current pipeline
        
        """
        module = self.create_module(identifier, name, namespace, x, y,
                                    internal_version)
        action = self.add_module_action(module)
        return module
            
    def delete_module(self, module_id):
        """ delete_module(module_id: int) -> version id
        Delete a module from the current pipeline
        
        """
        return self.delete_module_list([module_id])

    def create_module_list_deletion_action(self, pipeline, module_ids):
        """ create_module_list_deletion_action(
               pipeline: Pipeline,
               module_ids: [int]) -> Action
        Create action that will delete multiple modules from the given pipeline.

        """
        ops = self.delete_module_list_ops(pipeline, module_ids)
        return vistrails.core.db.action.create_action(ops)

    @vt_action
    def delete_module_list(self, module_ids):
        """ delete_module_list(module_ids: [int]) -> [version id]
        Delete multiple modules from the current pipeline
        
        """
        action = self.create_module_list_deletion_action(self.current_pipeline,
                                                         module_ids)
        return action
    
    def move_modules_ops(self, move_list):
        """ move_module_list(move_list: [(id,x,y)]) -> [operations]        
        Returns the operations that will move each module to its 
        specified location
        
        """
        operations = []
        for (id, x, y) in move_list:
            module = self.current_pipeline.get_module_by_id(id)
            if module.location:
                if module.location.x == x and module.location.y == y:
                    continue
            loc_id = self.vistrail.idScope.getNewId(Location.vtType)
            location = Location(id=loc_id, x=x, y=y)
            if module.location and module.location.id != -1:
                old_location = module.location
                operations.append(('change', old_location, location,
                                    module.vtType, module.id))
            else:
                #should probably be an error
                operations.append(('add', location, module.vtType, module.id))
        return operations

    def move_module_list(self, move_list):
        """ move_module_list(move_list: [(id,x,y)]) -> [version id]        
        Move all modules to a new location. No flushMoveActions is
        allowed to to emit to avoid recursive actions
        
        """
        action_list = self.move_modules_ops(move_list)
        action = vistrails.core.db.action.create_action(action_list)
        self.add_new_action(action)
        return self.perform_action(action)

    @vt_action
    def add_connection_action(self, connection):
        action = vistrails.core.db.action.create_action([('add', connection)])
        return action

    def add_connection(self, output_id, output_port_spec, 
                       input_id, input_port_spec):
        """ add_connection(output_id: long,
                           output_port_spec: PortSpec | str,
                           input_id: long,
                           input_port_spec: PortSpec | str) -> Connection
        Add a new connection into Vistrail
        
        """
        connection = \
            self.create_connection_from_ids(output_id, output_port_spec, 
                                            input_id, input_port_spec)
        action = self.add_connection_action(connection)
        return connection
    
    def delete_connection(self, id):
        """ delete_connection(id: int) -> version id
        Delete a connection with id 'id'
        
        """
        return self.delete_connection_list([id])

    @vt_action
    def delete_connection_list(self, connect_ids):
        """ delete_connection_list(connect_ids: list) -> version id
        Delete a list of connections
        
        """
        action_list = []
        for c_id in connect_ids:
            action_list.append(('delete', 
                                self.current_pipeline.connections[c_id]))
        action = vistrails.core.db.action.create_action(action_list)
        return action

    @vt_action
    def add_function_action(self, module, function):
        action = vistrails.core.db.action.create_action([('add', function, 
                                                module.vtType, module.id)])
        return action

    def add_function(self, module, function_name):
        function = self.create_function(module, function_name)
        action = self.add_function_action(module, function)
        return function

    @vt_action
    def update_function(self, module, function_name, param_values, old_id=-1L,
                        aliases=[], query_methods=[], should_replace=True):
        op_list = self.update_function_ops(module, function_name, param_values,
                                           old_id, aliases=aliases,
                                           query_methods=query_methods,
                                           should_replace=should_replace)
        if len(op_list) > 0:
            action = vistrails.core.db.action.create_action(op_list)
            return action
        return None

    @vt_action
    def update_parameter(self, function, old_param_id, new_value):
        old_param = function.parameter_idx[old_param_id]
        new_param = self.create_updated_parameter(old_param, new_value)
        if new_param is None:
            return None
        op = ('change', old_param, new_param, 
              function.vtType, function.real_id)
        action = vistrails.core.db.action.create_action([op])
        return action

    @vt_action
    def delete_method(self, function_pos, module_id):
        """ delete_method(function_pos: int, module_id: int) -> version id
        Delete a method with function_pos from module module_id

        """

        module = self.current_pipeline.get_module_by_id(module_id)
        function = module.functions[function_pos]
        action = vistrails.core.db.action.create_action([('delete', function,
                                                module.vtType, module.id)])
        return action

    @vt_action
    def delete_function(self, real_id, module_id):
        module = self.current_pipeline.get_module_by_id(module_id)
        function = module.get_function_by_real_id(real_id)
        action = vistrails.core.db.action.create_action([('delete', function,
                                                module.vtType, module.id)])
        return action

    @vt_action
    def delete_annotation(self, key, module_id):
        """ delete_annotation(key: str, module_id: long) -> version_id
        Deletes an annotation from a module
        
        """
        module = self.current_pipeline.get_module_by_id(module_id)
        annotation = module.get_annotation_by_key(key)
        action = vistrails.core.db.action.create_action([('delete', annotation,
                                                module.vtType, module.id)])
        return action

    @vt_action
    def add_annotation(self, pair, module_id):
        """ add_annotation(pair: (str, str), moduleId: int)        
        Add/Update a key/value pair annotation into the module of
        moduleId
        
        """
        assert isinstance(pair[0], basestring)
        assert isinstance(pair[1], basestring)
        if pair[0].strip()=='':
            return

        module = self.current_pipeline.get_module_by_id(module_id)
        a_id = self.vistrail.idScope.getNewId(Annotation.vtType)
        annotation = Annotation(id=a_id,
                                key=pair[0], 
                                value=pair[1],
                                )
        if module.has_annotation_with_key(pair[0]):
            old_annotation = module.get_annotation_by_key(pair[0])
            action = \
                vistrails.core.db.action.create_action([('change', old_annotation,
                                                   annotation,
                                                   module.vtType, module.id)])
        else:
            action = vistrails.core.db.action.create_action([('add', annotation,
                                                        module.vtType, 
                                                        module.id)])
        return action

    @vt_action
    def delete_control_parameter(self, name, module_id):
        """ delete_control_parameter(name: str, module_id: long) -> version_id
        Deletes an control_parameter from a module

        """
        module = self.current_pipeline.get_module_by_id(module_id)
        control_parameter = module.get_control_parameter_by_name(name)
        action = vistrails.core.db.action.create_action([('delete', control_parameter,
                                                module.vtType, module.id)])
        return action

    @vt_action
    def add_control_parameter(self, pair, module_id):
        """ add_control_parameter(pair: (str, str), moduleId: int)
        Add/Update a name/value pair control_parameter into the module of
        moduleId

        """
        assert isinstance(pair[0], basestring)
        assert isinstance(pair[1], basestring)
        if pair[0].strip()=='':
            return

        module = self.current_pipeline.get_module_by_id(module_id)
        a_id = self.vistrail.idScope.getNewId(ModuleControlParam.vtType)
        control_parameter = ModuleControlParam(id=a_id,
                                name=pair[0],
                                value=pair[1],
                                )
        if module.has_control_parameter_with_name(pair[0]):
            old_control_parameter = module.get_control_parameter_by_name(pair[0])
            action = \
                vistrails.core.db.action.create_action([('change', old_control_parameter,
                                                   control_parameter,
                                                   module.vtType, module.id)])
        else:
            action = vistrails.core.db.action.create_action([('add', control_parameter,
                                                        module.vtType,
                                                        module.id)])
        return action

    def update_functions_ops_from_ids(self, module_id, functions):
        module = self.current_pipeline.modules[module_id]
        return self.update_functions_ops(module, functions)

    def update_port_spec_ops_from_ids(self, module_id, deleted_ports, 
                                      added_ports):
        module = self.current_pipeline.modules[module_id]
        return self.update_port_spec_ops(module, deleted_ports, added_ports)

    @vt_action
    def update_functions(self, module, functions):
        op_list = self.update_functions_ops(module, functions)
        if len(op_list) > 0:
            action = vistrails.core.db.action.create_action(op_list)
        else:
            action = None
        return action

    @vt_action
    def update_ports_and_functions(self, module_id, deleted_ports, added_ports,
                                   functions):
        op_list = self.update_port_spec_ops_from_ids(module_id, deleted_ports, 
                                                     added_ports)
        op_list.extend(self.update_functions_ops_from_ids(module_id, functions))
        action = vistrails.core.db.action.create_action(op_list)
        return action

    @vt_action
    def update_ports(self, module_id, deleted_ports, added_ports):
        op_list = self.update_port_spec_ops_from_ids(module_id, deleted_ports, 
                                                     added_ports)
        action = vistrails.core.db.action.create_action(op_list)
        return action

    def has_module_port(self, module_id, port_tuple):
        """ has_module_port(module_id: int, port_tuple: (str, str)): bool
        Parameters
        ----------
        
        - module_id : 'int'        
        - port_tuple : (portType, portName)

        Returns true if there exists a module port in this module with given params

        """
        (type, name) = port_tuple
        module = self.current_pipeline.get_module_by_id(module_id)
        return len([x for x in module.db_portSpecs
                    if x.name == name and x.type == type]) > 0

    @vt_action
    def add_module_port(self, module_id, port_tuple):
        """ add_module_port(module_id: int, port_tuple: (str, str, list)
        Parameters
        ----------
        
        - module_id : 'int'        
        - port_tuple : (portType, portName, portSpec)
        
        """
        module = self.current_pipeline.get_module_by_id(module_id)
        p_id = self.vistrail.idScope.getNewId(PortSpec.vtType)
        port_spec = PortSpec(id=p_id,
                             type=port_tuple[0],
                             name=port_tuple[1],
                             sigstring=port_tuple[2],
                             )
        # don't know how many port spec items are created until after...
        for psi in port_spec.port_spec_items:
            psi.id = self.vistrail.idScope.getNewId(PortSpecItem.vtType)
        action = vistrails.core.db.action.create_action([('add', port_spec,
                                                module.vtType, module.id)])
        return action

    @vt_action
    def delete_module_port(self, module_id, port_tuple):
        """
        Parameters
        ----------
        
        - module_id : 'int'
        - port_tuple : (portType, portName, portSpec)
        
        """
        spec_id = -1
        module = self.current_pipeline.get_module_by_id(module_id)
        port_spec = module.get_portSpec_by_name((port_tuple[1], port_tuple[0]))
        action_list = [('delete', port_spec, module.vtType, module.id)]
        for function in module.functions:
            if function.name == port_spec.name:
                action_list.append(('delete', function, 
                                    module.vtType, module.id))
        action = vistrails.core.db.action.create_action(action_list)
        return action

    def create_group(self, module_ids, connection_ids):
        self.flush_delayed_actions()
        (group, connections) = \
            self.build_group(self.current_pipeline, 
                             module_ids, connection_ids)
        op_list = []
        op_list.extend(('delete', self.current_pipeline.connections[c_id])
                       for c_id in connection_ids)
        op_list.extend(('delete', self.current_pipeline.modules[m_id]) 
                       for m_id in module_ids)
        op_list.append(('add', group))
        op_list.extend(('add', c) for c in connections)
        action = vistrails.core.db.action.create_action(op_list)
        self.set_action_annotation(action, Action.ANNOTATION_DESCRIPTION,
                                   "Grouped modules")
        self.add_new_action(action)
#         for op in action.operations:
#             print op.vtType, op.what, op.old_obj_id, op.new_obj_id
        result = self.perform_action(action)
        return group
    
    def create_abstraction(self, module_ids, connection_ids, name):
        self.flush_delayed_actions()
        (abstraction, connections) = \
            self.build_abstraction(self.current_pipeline, 
                                   module_ids, connection_ids, name)
        op_list = []
        op_list.extend(('delete', self.current_pipeline.connections[c_id])
                       for c_id in connection_ids)
        op_list.extend(('delete', self.current_pipeline.modules[m_id]) 
                       for m_id in module_ids)
        op_list.append(('add', abstraction))
        op_list.extend(('add', c) for c in connections)
        action = vistrails.core.db.action.create_action(op_list)
        self.add_new_action(action)
        result = self.perform_action(action)
        return abstraction

    def ungroup_set(self, module_ids):
        self.flush_delayed_actions()
        for m_id in module_ids:
            self.create_ungroup(m_id)

    def create_ungroup(self, module_id):
        (modules, connections) = \
            self.build_ungroup(self.current_pipeline, module_id)
        pipeline = self.current_pipeline
        old_conn_ids = self.get_module_connection_ids([module_id], 
                                                      pipeline.graph)
        op_list = []
        op_list.extend(('delete', pipeline.connections[c_id]) 
                       for c_id in old_conn_ids)
        op_list.append(('delete', pipeline.modules[module_id]))
        op_list.extend(('add', m) for m in modules)
        op_list.extend(('add', c) for c in connections)
        action = vistrails.core.db.action.create_action(op_list)
        self.set_action_annotation(action, Action.ANNOTATION_DESCRIPTION,
                                   "Ungrouped modules")
        self.add_new_action(action)
        res = self.perform_action(action)
        self.validate(self.current_pipeline, False)
        return res



    ##########################################################################
    # Methods to access/find pipeline information
    
    def get_connections_to(self, pipeline, module_ids, port_name=None):
        connection_ids = set()
        graph = pipeline.graph
        for m_id in module_ids:
            for _, id in graph.edges_to(m_id):
                connection_ids.add(id)
        return [pipeline.connections[c_id] for c_id in connection_ids
                if port_name is None or \
                    pipeline.connections[c_id].destination.name == port_name]

    def get_connections_from(self, pipeline, module_ids, port_name=None):
        connection_ids = set()
        graph = pipeline.graph
        for m_id in module_ids:
            for _, id in graph.edges_from(m_id):
                connection_ids.add(id)
        return [pipeline.connections[c_id] for c_id in connection_ids
                if port_name is None or \
                    pipeline.connections[c_id].source.name == port_name]

    def get_connections_to_and_from(self, pipeline, module_ids):
        connection_ids = set()
        graph = pipeline.graph
        for m_id in module_ids:
            for _, id in graph.edges_from(m_id):
                connection_ids.add(id)
            for _, id in graph.edges_to(m_id):
                connection_ids.add(id)
        return [pipeline.connections[c_id] for c_id in connection_ids]
        
    ##########################################################################
    # Grouping/abstraction

    def get_avg_location(self, modules):
        if len(modules) < 1:
            return (0.0, 0.0)

        sum_x = 0.0
        sum_y = 0.0
        for module in modules:
            sum_x += module.location.x
            sum_y += module.location.y
        return (sum_x / len(modules), sum_y / len(modules))

    def translate_modules(self, modules, x, y):
        for module in modules:
            module.location.x -= x
            module.location.y -= y

    def center_modules(self, modules):
        (avg_x, avg_y) = self.get_avg_location(modules)
        self.translate_modules(modules, avg_x, avg_y)

    @staticmethod
    def get_neighbors(pipeline, module, upstream=True):
#         for i, m in pipeline.modules.iteritems():
#             print i, m.name
#         for j, c in pipeline.connections.iteritems():
#             print j, c.source.moduleId, c.destination.moduleId

        neighbors = []
        if upstream:
            get_edges = pipeline.graph.edges_to
            get_port_name = \
                lambda x: pipeline.connections[x].source.name
        else:
            get_edges = pipeline.graph.edges_from
            get_port_name = \
                lambda x: pipeline.connections[x].destination.name
        for (m_id, conn_id) in get_edges(module.id):
            neighbors.append((pipeline.modules[m_id], get_port_name(conn_id)))
        return neighbors

    @staticmethod
    def get_upstream_neighbors(pipeline, module):
        return VistrailController.get_neighbors(pipeline, module, True)
    @staticmethod
    def get_downstream_neighbors(pipeline, module):
        return VistrailController.get_neighbors(pipeline, module, False)

    def check_subpipeline_port_names(self):
        def create_name(base_name, names):
            if base_name in names:
                port_name = base_name + '_' + str(names[base_name])
                names[base_name] += 1
            else:
                port_name = base_name
                names[base_name] = 2
            return port_name

        in_names = {}
        out_names = {}
        in_cur_names = []
        out_cur_names = []
        in_process_list = []
        out_process_list = []
        pipeline = self.current_pipeline
        for m in pipeline.module_list:
            if m.package == basic_pkg and (m.name == 'InputPort' or
                                           m.name == 'OutputPort'):
                if m.name == 'InputPort':
                    neighbors = self.get_downstream_neighbors(pipeline, m)
                    names = in_names
                    cur_names = in_cur_names
                    process_list = in_process_list
                else:  # m.name == 'OutputPort'
                    neighbors = self.get_upstream_neighbors(pipeline, m)
                    names = out_names
                    cur_names = out_cur_names
                    process_list = out_process_list
                    
                if len(neighbors) < 1:
                    # print "not adding, no neighbors"
                    # don't add it!
                    continue

                name_function = None
                base_name = None
                for function in m.functions:
                    if function.name == 'name':
                        name_function = function
                        if len(function.params) > 0:
                            base_name = function.params[0].strValue
                if base_name is not None:
                    cur_names.append(base_name)
                else:
                    base_name = neighbors[0][1]
                    if base_name == 'self':
                        base_name = neighbors[0][0].name
                    process_list.append((m, base_name))

        op_list = []
        for (port_type, names, cur_names, process_list) in \
                [("input", in_names, in_cur_names, in_process_list), \
                     ("output", out_names, out_cur_names, out_process_list)]:
            cur_names.sort()
            last_name = None
            for name in cur_names:
                if name == last_name:
                    msg = 'Cannot assign the name "%s" to more ' \
                        'than one %s port' % (name, port_type)
                    raise RuntimeError(msg)
                last_name = name
                idx = name.rfind("_")
                if idx < 0:
                    names[name] = 2
                else:
                    base_name = None
                    try:
                        val = int(name[idx+1:])
                        base_name = name[:idx]
                    except ValueError:
                        pass
                    if base_name is not None and base_name in names:
                        cur_val = names[base_name]
                        if val >= cur_val:
                            names[base_name] = val + 1
                    else:
                        names[name] = 2

            for (m, base_name) in process_list:
                port_name = create_name(base_name, names)
                # FIXME use update_function when it is moved to
                # core (see core_no_gui branch)
                ops = self.update_function_ops(m, 'name', 
                                               [port_name])
                op_list.extend(ops)
        self.flush_delayed_actions()
        action = vistrails.core.db.action.create_action(op_list)
        if action is not None:
            self.add_new_action(action)
            self.perform_action(action)
        return action

    def create_subpipeline(self, full_pipeline, module_ids, connection_ids, 
                           id_remap, id_scope=None):
        if not id_scope:
            id_scope = IdScope(1, {Group.vtType: Module.vtType,
                                   Abstraction.vtType: Module.vtType})
        old_id_scope = self.id_scope
        self.set_id_scope(id_scope)
        
        connections = [full_pipeline.connections[c_id] 
                       for c_id in connection_ids]

        pipeline = Pipeline()
        pipeline.id = None # get rid of id so that sql saves correctly

        in_names = {}
        out_names = {}
        def create_name(base_name, names):
            if base_name in names:
                port_name = base_name + '_' + str(names[base_name])
                names[base_name] += 1
            else:
                port_name = base_name
                names[base_name] = 2
            return port_name

        for m in full_pipeline.module_list:
            if m.id not in module_ids:
                continue
            if m.package == basic_pkg and (m.name == 'InputPort' or
                                           m.name == 'OutputPort'):
                if m.name == 'InputPort':
                    neighbors = self.get_downstream_neighbors(full_pipeline, m)
                    names = in_names
                else:  # m.name == 'OutputPort'
                    neighbors = self.get_upstream_neighbors(full_pipeline, m)
                    names = out_names
                if len(neighbors) < 1:
                    # print "not adding, no neighbors"
                    # don't add it!
                    continue

                m = m.do_copy(True, id_scope, id_remap)
                name_function = None
                for function in m.functions:
                    if function.name == 'name':
                        name_function = function
                        base_name = function.params[0].strValue
                if name_function is None:
                    base_name = neighbors[0][1]
                if base_name == 'self':
                    base_name = neighbors[0][0].name
                port_name = create_name(base_name, names)
                if name_function is not None:
                    name_function.params[0].strValue = port_name
                else:
                    functions = [('name', [port_name])]
                    for f in self.create_functions(m, functions):
                        m.add_function(f)
                pipeline.add_module(m)
            else:
                pipeline.add_module(m.do_copy(True, id_scope, id_remap))

        # translate group to center
        (avg_x, avg_y) = self.get_avg_location(pipeline.module_list)
        self.translate_modules(pipeline.module_list, avg_x, avg_y)
        module_index = dict([(m.id, m) for m in pipeline.module_list])

        def create_port(port_type, other_port, other_module, old_module, names):
            x = old_module.location.x
            y = old_module.location.y
            module_name = port_type.capitalize() + 'Port'
            base_name = other_port.name
            if base_name == 'self':
                base_name = other_module.name
            port_name = create_name(base_name, names)
            module = self.create_module(basic_pkg, module_name, '', 
                                        x - avg_x, y - avg_y)
            functions = [('name', [port_name])]
            for f in self.create_functions(module, functions):
                module.add_function(f)
            
            return (module, 'InternalPipe', port_name)

        def add_to_pipeline(port_type, port, other_port, names):
            old_module = full_pipeline.modules[port.moduleId]
            old_port_name = port.name
            port_name = other_port.name
            module_id = id_remap[(Module.vtType, other_port.moduleId)]
            module = module_index[module_id]
            key = (module_id, port_name, port_type)
            if key in existing_ports:
                (new_module, new_port, new_name) = existing_ports[key]
            else:
                (new_module, new_port, new_name) = \
                    create_port(port_type, other_port, module, 
                                old_module, names)
                existing_ports[key] = (new_module, new_port, new_name)
                pipeline.add_module(new_module)
                if port_type == 'input':
                    # print "output:", new_module.name, new_module.id, new_name
                    # print "input:", module.name, module.id, port_name
                    new_conn = self.create_connection(new_module, new_port,
                                                      module, port_name)
                elif port_type == 'output':
                    # print "output:", module.name, module.id, port_name  
                    # print "input:", new_module.name, new_module.id, new_name
                    new_conn = self.create_connection(module, port_name,
                                                      new_module, new_port)
                else:
                    raise VistrailsInternalError("port_type incorrect")
                pipeline.add_connection(new_conn)
            return (old_module, old_port_name, new_name)
            

        outside_connections = []
        existing_ports = {}
        for connection in connections:
            all_inside = True
            all_outside = True
            for port in connection.ports:
                if not (Module.vtType, port.moduleId) in id_remap:
                    all_inside = False
                else:
                    all_outside = False

            # if a connection has an "external" connection, we need to
            # create an input port or output port module
            if all_inside:
                pipeline.add_connection(connection.do_copy(True, id_scope,
                                                           id_remap))
            else:
                old_in_module = None
                old_out_module = None
                if (Module.vtType, connection.source.moduleId) not in id_remap:
                    (old_out_module, old_out_port, old_in_port) = \
                        add_to_pipeline('input', connection.source, 
                                        connection.destination, in_names)
                elif (Module.vtType, connection.destination.moduleId) \
                        not in id_remap:
                    (old_in_module, old_in_port, old_out_port) = \
                        add_to_pipeline('output', connection.destination, 
                                        connection.source, out_names)
                outside_connections.append((old_out_module, old_out_port,
                                            old_in_module, old_in_port))

        self.set_id_scope(old_id_scope)
        return (pipeline, outside_connections)

    def get_connections_to_subpipeline(self, module, partial_connections):
        connections = []
        for (out_module, out_port, in_module, in_port) in partial_connections:
            if out_module is None:
                out_module = module
            if in_module is None:
                in_module = module
            connections.append(self.create_connection(out_module, out_port,
                                                      in_module, in_port))
        return connections

    def build_group(self, full_pipeline, module_ids, connection_ids):
        id_remap = {}
        (pipeline, outside_connections) = \
            self.create_subpipeline(full_pipeline, module_ids, connection_ids,
                                    id_remap)

        # now group to vistrail
        (avg_x, avg_y) = self.get_avg_location([full_pipeline.modules[m_id]
                                                for m_id in module_ids])
        group = self.create_module(basic_pkg, 'Group', '', avg_x, avg_y)
        group.pipeline = pipeline

        connections = \
            self.get_connections_to_subpipeline(group, outside_connections)

        return (group, connections)

    def build_abstraction(self, full_pipeline, module_ids, 
                          connection_ids, name):
        id_remap = {}
        (pipeline, outside_connections) = \
            self.create_subpipeline(full_pipeline, module_ids, connection_ids, 
                                    id_remap)
        
        # save vistrail
        abs_vistrail = self.create_vistrail_from_pipeline(pipeline)
        abs_vistrail.name = name
        abs_vistrail.change_description("Copied from pipeline", 1L)
        abs_fname = self.save_abstraction(abs_vistrail)

        # need to late enable stuff on the abstraction_pkg package
        self.add_abstraction_to_registry(abs_vistrail, abs_fname, name, 
                                         None, "1")
        namespace = get_cur_abs_namespace(abs_vistrail)
        (avg_x, avg_y) = self.get_avg_location([full_pipeline.modules[m_id]
                                                for m_id in module_ids])
        abstraction = self.create_module(abstraction_pkg, name, namespace, 
                                         avg_x, avg_y, 1L)
        connections = self.get_connections_to_subpipeline(abstraction, 
                                                          outside_connections)
        return (abstraction, connections)

    def build_abstraction_from_group(self, full_pipeline, group_id, name):
        if name is None:
            return
        group = self.current_pipeline.modules[group_id]
        abs_vistrail = self.create_vistrail_from_pipeline(group.pipeline)
        abs_vistrail.name = name
        abs_vistrail.change_description("Created from group", 1L)
        abs_fname = self.save_abstraction(abs_vistrail)

        group_connections = self.get_connections_to_and_from(full_pipeline,
                                                             [group_id])
        outside_connections = []
        for c in group_connections:
            out_module = full_pipeline.modules[c.source.moduleId]
            out_port = c.source.name
            in_module = full_pipeline.modules[c.destination.moduleId]
            in_port = c.destination.name
            if c.source.moduleId == group_id:
                out_module = None
            if c.destination.moduleId == group.id:
                in_module = None
            outside_connections.append((out_module, out_port, 
                                        in_module, in_port))

        # need to late enable stuff on the 'local.abstractions' package
        self.add_abstraction_to_registry(abs_vistrail, abs_fname, name,
                                         None, "1")
        namespace = get_cur_abs_namespace(abs_vistrail)
        abstraction = self.create_module(abstraction_pkg, name, namespace, 
                                         group.location.x, group.location.y, 
                                         1L)
        connections = self.get_connections_to_subpipeline(abstraction, 
                                                          outside_connections)
        return (abstraction, connections)

    def create_vistrail_from_pipeline(self, pipeline):
        abs_vistrail = Vistrail()
        
        id_remap = {}
        action = vistrails.core.db.action.create_paste_action(pipeline, 
                                                    abs_vistrail.idScope,
                                                    id_remap)
        abs_vistrail.add_action(action, 0L, 0)
        return abs_vistrail
        
    def get_abstraction_dir(self):
        conf = get_vistrails_configuration()
        abstraction_dir = get_vistrails_directory("subworkflowsDir")
        if abstraction_dir is None:
            raise VistrailsInternalError("'subworkflowsDir' not"
                                         " specified in configuration")
        elif not os.path.exists(abstraction_dir):
            raise VistrailsInternalError("Cannot find %s" % abstraction_dir)
        return abstraction_dir

    def get_abstraction_desc(self, package, name, namespace, module_version=None):
        reg = vistrails.core.modules.module_registry.get_module_registry()
        if reg.has_descriptor_with_name(package, name, namespace,
                                        None, module_version):
            return reg.get_descriptor_by_name(package, name,
                                              namespace, None, module_version)
        return None

    def add_abstraction_to_registry(self, abs_vistrail, abs_fname, name, 
                                    namespace=None, module_version=None,
                                    is_global=True, avail_fnames=[]):
        reg = vistrails.core.modules.module_registry.get_module_registry()
        cur_namespace = get_cur_abs_namespace(abs_vistrail)
        if namespace is None:
            namespace = cur_namespace
        if module_version is None:
            module_version = -1L

        self.ensure_abstractions_loaded(abs_vistrail, avail_fnames)
        try:
            abstraction = new_abstraction(name, abs_vistrail, abs_fname,
                                          long(module_version))
        except InvalidPipeline, e:
            # handle_invalid_pipeline will raise it's own InvalidPipeline
            # exception if it fails
            
            # use a new controller that is tied to the abstraction
            # vistrail to process exceptions, also force upgrades to
            # be immediately incorporated, use self.__class_ to create
            # controller so user is prompted if in GUI mode
            abs_controller = self.__class__(abs_vistrail, auto_save=False)
            (new_version, new_pipeline) = \
                abs_controller.handle_invalid_pipeline(e, long(module_version),
                                                       force_no_delay=True) 
            try:
                abstraction = new_abstraction(name, abs_vistrail, abs_fname,
                                              new_version)
            except InvalidPipeline, e:
                # we need to process a second InvalidPipeline exception
                # because the first may be simply for a missing package,
                # then we hit upgrades with the second one

                (new_version, new_pipeline) = \
                    abs_controller.handle_invalid_pipeline(e, new_version,
                                                           force_no_delay=True)
            del abs_controller

            save_abstraction(abs_vistrail, abs_fname)
            self.set_changed(True)
            abstraction = new_abstraction(name, abs_vistrail, abs_fname,
                                          new_version, new_pipeline)
            module_version = str(new_version)

        all_namespaces = get_all_abs_namespaces(abs_vistrail)

        old_desc = None
        for ns in all_namespaces:
            try:
                desc = reg.get_similar_descriptor(abstraction_pkg,
                                                  name,
                                                  ns)
                if not desc.is_hidden:
                    old_desc = desc
                    # print "found old_desc", old_desc.name, old_desc.version
                    break
            except ModuleRegistryException, e:
                pass
            
        global_hide = not is_global or old_desc is not None
        newest_desc = None
        requested_desc = None
        for ns in all_namespaces:
            hide_descriptor = (ns != cur_namespace) or global_hide
            # print '()()() adding abstraction', namespace
            if reg.has_descriptor_with_name(abstraction_pkg, 
                                            name, 
                                            ns,
                                            abstraction_ver, 
                                            str(module_version)):
                # don't add something twice
                continue
            new_desc = reg.auto_add_module((abstraction, 
                                            {'package': abstraction_pkg,
                                             'package_version': abstraction_ver,
                                             'namespace': ns,
                                             'version': str(module_version),
                                             'hide_namespace': True,
                                             'hide_descriptor': hide_descriptor,
                                             }))
            if ns == cur_namespace:
                newest_desc = new_desc
            if ns == namespace:
                requested_desc = new_desc
            reg.auto_add_ports(abstraction)
        if old_desc is not None:
            # print '$$$ calling update_module'
            reg.update_module(old_desc, newest_desc)
        return requested_desc

#         package = reg.get_package_by_name(abstraction_pkg)
#         for desc in package.descriptor_versions.itervalues():
#             print desc.package, desc.name, desc.namespace, desc.version

    def abstraction_exists(self, name):
        # FIXME need to check directory in case abstraction was not
        # loaded due to dependencies.
        # FIXME, also need to check this for groups, probably
        abstraction_dir = self.get_abstraction_dir()
        vt_fname = os.path.join(abstraction_dir, name + '.xml')
        return os.path.exists(vt_fname)

    def load_abstraction(self, abs_fname, is_global=True, abs_name=None,
                         module_version=None, avail_fnames=[]):
        if abs_name is None:
            abs_name = parse_abstraction_name(abs_fname)
        if abs_fname in self._loaded_abstractions:
            abs_vistrail = self._loaded_abstractions[abs_fname]
        else:
            abs_vistrail = read_vistrail(abs_fname)
            self._loaded_abstractions[abs_fname] = abs_vistrail
        
        # print "LOAD_VT NAMESPACES:", get_all_abs_namespaces(abs_vistrail)

        abstraction_uuid = get_cur_abs_namespace(abs_vistrail)
        if abstraction_uuid is None:
            # No current uuid exists - generate one
            abstraction_uuid = str(uuid.uuid1())
            abs_vistrail.set_annotation('__abstraction_uuid__', abstraction_uuid)
        origin_uuid = abs_vistrail.get_annotation('__abstraction_origin_uuid__')
        if origin_uuid is None:
            # No origin uuid exists - set to current uuid (for backwards compatibility)
            origin_uuid = abstraction_uuid
            abs_vistrail.set_annotation('__abstraction_origin_uuid__', origin_uuid)
        else:
            origin_uuid = origin_uuid.value
            
        if module_version is None:
            module_version = str(abs_vistrail.get_latest_version())
        elif isinstance(module_version, (int, long)):
            module_version = str(module_version)
        # If an upgraded version has already been created, we want to use that rather than loading the old version.
        # This step also avoid duplication of abstraction upgrades.  Otherwise, when we try to add the old version
        # to the registry, it raises an InvalidPipeline exception and automatically tries to handle it by creating
        # another upgrade for the old version.
        upgrade_version = abs_vistrail.get_upgrade(long(module_version))
        if upgrade_version is not None:
            old_version = module_version
            module_version = str(upgrade_version)
        
        desc = self.get_abstraction_desc(abstraction_pkg, abs_name, 
                                         abstraction_uuid, module_version)
        if desc is None:
            #print "adding version", module_version, "of", abs_name, "(namespace: %s)"%abstraction_uuid, "to registry"
            desc = self.add_abstraction_to_registry(abs_vistrail, abs_fname, 
                                                    abs_name, None, 
                                                    module_version, 
                                                    is_global, avail_fnames)
        return desc
    
    def unload_abstractions(self):
        reg = vistrails.core.modules.module_registry.get_module_registry()
        for abs_fname, abs_vistrail in self._loaded_abstractions.iteritems():
            abs_name = parse_abstraction_name(abs_fname)
            # FIXME? do we need to remove all versions (call
            # delete_module over and over?)
            for namespace in get_all_abs_namespaces(abs_vistrail):
                try:
                    reg.delete_module(abstraction_pkg, abs_name, namespace)
                except Exception:
                    pass
        self._loaded_abstractions.clear()

    def manage_package_names(self, vistrail, package):
        vistrail = copy.copy(vistrail)
        dependencies = []
        for action in vistrail.actions:
            for operation in action.operations:
                if (operation.vtType == 'add' or 
                    operation.vtType == 'change'):
                    if (operation.what == 'abstraction' and 
                        operation.data.package == abstraction_pkg):
                        operation.data.package = package
                    elif (operation.what == 'abstraction' or
                          operation.what == 'module' or
                          operation.what == 'group'):
                        dependencies.append(operation.data.package)
                    
        return (vistrail, dependencies)

    def save_abstraction(self, vistrail, name=None, package=None, 
                         save_dir=None, overwrite=False):
        if (package is None) != (save_dir is None):
            raise VistrailsInternalError("Must set both package and "
                                         "save_dir or neither")
        if name is None:
            name = vistrail.name

        if package is None and self.abstraction_exists(name):
            raise VistrailsInternalError("Abstraction with name '%s' already "
                                         "exists" % name)
        
        # Set uuid's (this is somewhat tricky because of backwards
        # compatibility - there was originally only
        # '__abstraction_uuid__' and no origin, so we have to handle
        # cases where a uuid is set, but hasn't been set as the origin
        # yet).
        new_uuid = str(uuid.uuid1())
        if vistrail.get_annotation('__abstraction_origin_uuid__') is None:
            # No origin uuid exists
            current_uuid = vistrail.get_annotation('__abstraction_uuid__')
            if current_uuid is None:
                # No current uuid exists - generate one and use it as
                # origin and current uuid
                vistrail.set_annotation('__abstraction_origin_uuid__', new_uuid)
                # vistrail.set_annotation('__abstraction_uuid__', new_uuid)
            else:
                # A current uuid exists - set it as origin and
                # generate a new current uuid
                vistrail.set_annotation('__abstraction_origin_uuid__', 
                                        current_uuid.value)
                # vistrail.set_annotation('__abstraction_uuid__', str(uuid.uuid1()))
        # else:
        #     # Origin uuid exists - just generate a new current uuid
        #     vistrail.set_annotation('__abstraction_uuid__', str(uuid.uuid1()))
        annotation_key = get_next_abs_annotation_key(vistrail)
        vistrail.set_annotation(annotation_key, new_uuid)

        if save_dir is None:
            save_dir = self.get_abstraction_dir()
        vt_fname = os.path.join(save_dir, name + '.xml')
        if not overwrite and os.path.exists(vt_fname):
            raise VistrailsInternalError("'%s' already exists" % \
                                             vt_fname)
        vistrails.core.db.io.save_vistrail_to_xml(vistrail, vt_fname)
        return vt_fname

    def upgrade_abstraction_module(self, module_id, test_only=False):
        """upgrade_abstraction_module(module_id, test_only) -> None or
        (preserved: bool, missing_ports: list)

        If test_only is False, attempts to automatically upgrade an
        abstraction by adding a new abstraction with the current package
        version, and recreates all connections and functions.  If any
        of the ports/functions used are not available, they are not
        reconnected/readded to the new abstraction.
        
        If test_only is True, (preserved: bool, missing_ports: list)
        is returned, where 'preserved' is a boolean that is True
        if the abstraction can be replaced with all functions and
        connections preserved.  If 'preserved' is True, then
        'missing_ports' is an empty list, otherwise it contains a
        list of tuples (port_type: str, port_name: str) of all
        ports that have been removed.
        
        """
        # get the new descriptor first
        invalid_module = self.current_pipeline.modules[module_id]
        # make sure that we don't get an obselete descriptor
        invalid_module._module_descriptor = None
        abs_fname = invalid_module.module_descriptor.module.vt_fname
        #print "&&& abs_fname", abs_fname
        (path, prefix, abs_name, abs_namespace, suffix) = \
            parse_abstraction_name(abs_fname, True)
        # abs_vistrail = invalid_module.vistrail
        abs_vistrail = read_vistrail(abs_fname)
        abs_namespace = get_cur_abs_namespace(abs_vistrail)
        lookup = {(abs_name, abs_namespace): abs_fname}
        descriptor_info = invalid_module.descriptor_info
        newest_version = str(abs_vistrail.get_latest_version())
        #print '&&& check_abstraction', abs_namespace, newest_version
        d = self.check_abstraction((descriptor_info[0],
                                    descriptor_info[1],
                                    abs_namespace,
                                    descriptor_info[3],
                                    newest_version),
                                   lookup)

        failed = True
        src_ports_gone = {}
        dst_ports_gone = {}
        fns_gone = {}
        missing_ports = []
        check_upgrade = UpgradeWorkflowHandler.check_upgrade
        while failed:
            try:
                check_upgrade(self.current_pipeline, module_id, d, 
                              function_remap=fns_gone, 
                              src_port_remap=src_ports_gone, 
                              dst_port_remap=dst_ports_gone)
                if test_only:
                    return (len(missing_ports) == 0, missing_ports)
                failed = False
            except UpgradeWorkflowError, e:
                if test_only:
                    missing_ports.append((e._port_type, e._port_name))
                if e._module is None or e._port_type is None or \
                        e._port_name is None:
                    raise e
                # Remove the offending connection/function by remapping to None
                if e._port_type == 'output':
                    src_ports_gone[e._port_name] = None
                elif e._port_type == 'input':
                    dst_ports_gone[e._port_name] = None
                    fns_gone[e._port_name] = None
                else:
                    raise e
        upgrade_action = \
            UpgradeWorkflowHandler.replace_module(self, self.current_pipeline,
                                                  module_id, d, 
                                                  fns_gone,
                                                  src_ports_gone,
                                                  dst_ports_gone)[0]
        self.flush_delayed_actions()
        self.add_new_action(upgrade_action)
        self.perform_action(upgrade_action)
        self.vistrail.change_description("Upgrade Subworkflow", 
                                         self.current_version)

    def get_abstraction_descriptor(self, name, namespace=None):
        reg = vistrails.core.modules.module_registry.get_module_registry()
        return reg.get_descriptor_by_name(abstraction_pkg, name, namespace)

#     def load_abstraction(self, abs_fname, abs_name=None):
#         if abs_name is None:
#             abs_name = os.path.basename(abs_fname)[12:-4]
#         abs_vistrail = read_vistrail(abs_fname)
#         abstraction_uuid = \
#             abs_vistrail.get_annotation('__abstraction_uuid__').value
#         if self.abstraction_exists(abs_name):
#             descriptor = self.get_abstraction_descriptor(abs_name)
#             if descriptor.module.uuid == abstraction_uuid:
#                 return
#         if self.abstraction_exists(abs_name, abstraction_uuid):
#             descriptor = \
#                 self.get_abstraction_descriptor(abs_name, abstraction_uuid)
#             descriptor._abstraction_refs += 1
#             # print 'load ref_count:', descriptor.abstraction_refs
#             return
            
#         self.add_abstraction(abs_vistrail, abs_fname, abs_name, 
#                              abstraction_uuid)
            
#    def unload_abstraction(self, name, namespace):
#        if self.abstraction_exists(name):
#            descriptor = self.get_abstraction_descriptor(name, namespace)
#            descriptor._abstraction_refs -= 1
#            # print 'unload ref_count:', descriptor.abstraction_refs
#            if descriptor._abstraction_refs < 1:
#                # unload abstraction
#                print "deleting module:", name, namespace
#                reg = core.modules.module_registry.get_module_registry()
#                reg.delete_module(abstraction_pkg, name, namespace)

    def import_abstraction(self, new_name, package, name, namespace, 
                           module_version=None):
        # copy from a local namespace to local.abstractions
        reg = vistrails.core.modules.module_registry.get_module_registry()
        descriptor = self.get_abstraction_desc(package, name, namespace, str(module_version))
        if descriptor is None:
            # if not self.abstraction_exists(name):
            raise VistrailsInternalError("Abstraction %s|%s (package: %s) not on registry" %\
                                             (name, namespace, package))
        # FIXME have save_abstraction take abs_fname as argument and do
        # shutil copy
        # abs_fname = descriptor.module.vt_fname
        abs_vistrail = descriptor.module.vistrail
        # Strip the descriptor info annotation before saving so the imported version will be editable
        abs_desc_info = abs_vistrail.get_annotation('__abstraction_descriptor_info__')
        if abs_desc_info is not None:
            abs_vistrail.set_annotation('__abstraction_descriptor_info__', None)
        abs_fname = self.save_abstraction(abs_vistrail, new_name)
        # Duplicate the vistrail and set the uuid and descriptor annotation back on the original vistrail
        imported_vistrail = read_vistrail(abs_fname)
        annotation_key = get_next_abs_annotation_key(abs_vistrail)
        abs_vistrail.set_annotation(annotation_key, namespace)
        if abs_desc_info is not None:
            abs_vistrail.set_annotation('__abstraction_descriptor_info__', abs_desc_info.value)
        #if new_name == name and package == abstraction_pkg:
        #    reg.show_module(descriptor)
        #    descriptor.module.vt_fname = abs_fname
        #else:
        new_desc = self.add_abstraction_to_registry(imported_vistrail, abs_fname, new_name,
                                                    None, str(module_version))
        reg.show_module(new_desc)

    def export_abstraction(self, new_name, pkg_name, dir, package, name, namespace, 
                           module_version):
        descriptor = self.get_abstraction_desc(package, name, namespace, module_version)
        if descriptor is None:
            raise VistrailsInternalError("Abstraction %s|%s (package: %s) not on registry" %\
                                             (name, namespace, package))
        
        abs_vistrail = descriptor.module.vistrail
        (abs_vistrail, dependencies) = self.manage_package_names(abs_vistrail, 
                                                                 pkg_name)
        abs_fname = self.save_abstraction(abs_vistrail, new_name, pkg_name,
                                          dir)
        return (os.path.basename(abs_fname), dependencies)
    
    def find_abstractions(self, vistrail, recurse=False):
        abstractions = {}
        for action in vistrail.actions:
            for operation in action.operations:
                if operation.vtType == 'add' or \
                        operation.vtType == 'change':
                    if operation.data is not None and operation.data.vtType == Abstraction.vtType:
                        abstraction = operation.data
                        if abstraction.package == abstraction_pkg:
                            key = abstraction.descriptor_info
                            if key not in abstractions:
                                abstractions[key] = []
                            abstractions[key].append(abstraction)
        if recurse:
            for abstraction_list in abstractions.values():
                for abstraction in abstraction_list[:]:
                    try:
                        vistrail = abstraction.vistrail
                    except MissingPackageVersion, e:
                        try:
                            reg = vistrails.core.modules.module_registry.get_module_registry()
                            abstraction._module_descriptor = \
                                reg.get_similar_descriptor(
                                                 *abstraction.descriptor_info)
                            vistrail = abstraction.vistrail
                        except Exception, e:
                            # ignore because there will be a load attempt later 
                            continue
                    except Exception, e:
                        # ignore because there will be a load attempt later 
                        continue
                    r_abstractions = self.find_abstractions(vistrail, recurse)
                    for k,v in r_abstractions.iteritems():
                        if k not in abstractions:
                            abstractions[k] = []
                        abstractions[k].extend(v)
        return abstractions

    def check_abstraction(self, descriptor_tuple, lookup):
        reg = vistrails.core.modules.module_registry.get_module_registry()
        try:
            descriptor = reg.get_descriptor_by_name(*descriptor_tuple)
            if not os.path.exists(descriptor.module.vt_fname):
                # print "abstraction path doesn't exist"
                reg.delete_descriptor(descriptor)
                raise MissingModule(descriptor_tuple[0],
                                    descriptor_tuple[1],
                                    descriptor_tuple[2],
                                    descriptor_tuple[4])
            return descriptor
        except MissingPackageVersion, e:
            if descriptor_tuple[3] != '':
                new_desc = (descriptor_tuple[0],
                            descriptor_tuple[1],
                            descriptor_tuple[2],
                            '',
                            descriptor_tuple[4])
                return self.check_abstraction(new_desc, lookup)
            else:
                raise
        except MissingModuleVersion, e:
            if descriptor_tuple[4] != '':
                other_desc = reg.get_descriptor_by_name(descriptor_tuple[0],
                                                        descriptor_tuple[1],
                                                        descriptor_tuple[2],
                                                        descriptor_tuple[3],
                                                        '')
                new_desc = \
                    self.load_abstraction(other_desc.module.vt_fname, 
                                          False, descriptor_tuple[1],
                                          descriptor_tuple[4])
                descriptor_tuple = (new_desc.package, new_desc.name, 
                                    new_desc.namespace, new_desc.package_version,
                                    str(new_desc.version))
                return self.check_abstraction(descriptor_tuple, lookup)
            else:
                raise
        except MissingModule, e:
            if (descriptor_tuple[1], descriptor_tuple[2]) not in lookup:
                if (descriptor_tuple[1], None) not in lookup:
                    raise
                abs_fnames = lookup[(descriptor_tuple[1], None)]
            else:
                abs_fnames = [lookup[(descriptor_tuple[1], descriptor_tuple[2])]]
            for abs_fname in abs_fnames:
                new_desc = \
                    self.load_abstraction(abs_fname, False, 
                                          descriptor_tuple[1],
                                          descriptor_tuple[4],
                                          [v for k, v in lookup.iteritems()
                                           if k[1] is not None])
                descriptor_tuple = (new_desc.package, new_desc.name, 
                                    new_desc.namespace, new_desc.package_version,
                                    str(new_desc.version))
            return self.check_abstraction(descriptor_tuple, lookup)
        
    def ensure_abstractions_loaded(self, vistrail, abs_fnames):
        lookup = {}
        for abs_fname in abs_fnames:
            path, prefix, abs_name, abs_namespace, suffix = parse_abstraction_name(abs_fname, True)
            # abs_name = os.path.basename(abs_fname)[12:-4]
            lookup[(abs_name, abs_namespace)] = abs_fname
            if (abs_name, None) not in lookup:
                lookup[(abs_name, None)] = []
            lookup[(abs_name, None)].append(abs_fname)
            
        # we're going to recurse manually (see
        # add_abstraction_to_regsitry) because we can't call
        # abstraction.vistrail until the module is loaded.
        abstractions = self.find_abstractions(vistrail)
        for descriptor_info, abstraction_list in abstractions.iteritems():
            # print 'checking for abstraction "' + str(abstraction.name) + '"'
            try:
                descriptor = self.check_abstraction(descriptor_info,
                                                    lookup)
                for abstraction in abstraction_list:
                    abstraction.module_descriptor = descriptor
            except InvalidPipeline, e:
                debug.critical("Error loading abstraction '%s'" %
                               descriptor_info[1], e)

    def build_ungroup(self, full_pipeline, module_id):
        group = full_pipeline.modules[module_id]
        if group.vtType == Group.vtType:
            pipeline = group.pipeline
        elif group.vtType == Abstraction.vtType:
            pipeline = group.summon().pipeline
        else:
            print 'not a group or abstraction?'
            return

        pipeline.ensure_connection_specs()

        # First, we copy all the modules from inside the group pipeline to the
        # outer pipeline.
        # We skip the InputPort and OutputPort modules, which we add to
        # port_modules instead.
        port_modules = set()
        modules = []
        connections = []
        id_remap = {}
        for module in pipeline.module_list:
            if module.package == basic_pkg and (module.name == 'InputPort' or
                                                module.name == 'OutputPort'):
                if module.name == 'InputPort':
                    port_modules.add((module, 'input'))
                else:
                    port_modules.add((module, 'output'))
            else:
                modules.append(module.do_copy(True, self.id_scope, id_remap))
        module_index = dict([(m.id, m) for m in modules])

        # If the connection was to/from an OutputPort/InputPort module, we
        # store the association in open_ports so we can reconnect these to the
        # outside later.
        # We also add them to the unconnected_port_modules dictionary.
        open_ports = {}
        unconnected_port_modules = {}
        for port_module, port_type in port_modules:
            (port_name, _, _, _, neighbors) = \
                group.get_port_spec_info(port_module)
            new_neighbors = \
                [(module_index[id_remap[(Module.vtType, m.id)]], n)
                 for (m, n) in neighbors
                 if (Module.vtType, m.id) in id_remap]
            open_ports[(port_name, port_type)] = new_neighbors
            unconnected_port_modules[(port_name, port_type)] = port_module

        # Now iterate over the outer connections
        # If the connection was between the outside and the group module, we
        # connect to the actual destination instead, using the open_ports dict.
        # We also remove the corresponding port from unconnected_port_modules.
        for connection in full_pipeline.connection_list:
            if connection.source.moduleId == group.id:
                key = (connection.source.name, 'output')
                try:
                    del unconnected_port_modules[key]
                except KeyError:
                    pass
                if key not in open_ports:
                    continue
                neighbors = open_ports[key]
                input_module = \
                    full_pipeline.modules[connection.destination.moduleId]
                input_port = connection.destination.name
                for (output_module, output_port) in neighbors:
                    connections.append(self.create_connection(output_module,
                                                              output_port,
                                                              input_module,
                                                              input_port))
            elif connection.destination.moduleId == group.id:
                key = (connection.destination.name, 'input')
                try:
                    del unconnected_port_modules[key]
                except KeyError:
                    pass
                if key not in open_ports:
                    continue
                neighbors = open_ports[key]
                output_module = \
                    full_pipeline.modules[connection.source.moduleId]
                output_port = connection.source.name
                for (input_module, input_port) in neighbors:
                    connections.append(self.create_connection(output_module, 
                                                              output_port,
                                                              input_module, 
                                                              input_port))

        # We are now left with unconnected_port_modules, a dictionary of
        # InputPort and OutputPort modules for ports that are not connected
        # to anything.
        # We copy these modules over so that re-grouping will keep these ports.
        for key, port_module in unconnected_port_modules.iteritems():
            modules.append(port_module.do_copy(True, self.id_scope, id_remap))

        # Center the group's modules on the old group's location
        self.translate_modules(modules, -group.location.x, -group.location.y)

        # Now copy the inner connections
        # If the connection is between two modules that come from the group
        # (all_inside is True), we copy it.
        for connection in pipeline.connection_list:
            all_inside = all((Module.vtType, port.moduleId) in id_remap
                             for port in connection.ports)
            if all_inside:
                connections.append(connection.do_copy(True, self.id_scope,
                                                      id_remap))

        return (modules, connections)

    def find_thumbnails(self, tags_only=True):
        thumbnails = []
        thumb_cache = ThumbnailCache.getInstance()
        for action in self.vistrail.actions:
            if self.vistrail.has_thumbnail(action.id):
                thumbnail = self.vistrail.get_thumbnail(action.id)
                if tags_only and not self.vistrail.has_tag(action.timestep):
                    thumb_cache.remove(thumbnail)
                    self.vistrail.set_thumbnail(action.timestep, "")
                else:
                    abs_fname = thumb_cache.get_abs_name_entry(thumbnail)
                    if abs_fname is not None:
                        thumbnails.append(abs_fname)
                    else:
                        self.vistrail.set_thumbnail(action.timestep, "")
        return thumbnails
    
    def add_parameter_changes_from_execution(self, pipeline, version,
                                             parameter_changes):
        """add_parameter_changes_from_execution(pipeline, version,
        parameter_changes) -> int.

        Adds new versions to the current vistrail as a result of an
        execution. Returns the version number of the new version."""

        current_pipeline = self.current_pipeline
        current_version = self.current_version

        self.current_pipeline = pipeline
        self.current_version = version

        op_list = []
        for (m_id, function_name, param_values) in parameter_changes:
            try:
                param_values_len = len(param_values)
            except TypeError:
                param_values = [param_values]
            # FIXME should use registry to determine parameter types
            # and then call the translate_to_string method on each
            # parameter
            param_values = [str(x) for x in param_values]
            module = self.current_pipeline.modules[m_id]
            # FIXME remove this code when aliases move
            old_id = -1
            for old_function in module.functions:
                if old_function.name == function_name:
                    old_id = old_function.real_id

            # ensure that replacements don't happen for functions that
            # shouldn't be replaced
            aliases = []
            if old_id >= 0:
                function = module.function_idx[old_id]
                for i in xrange(len(param_values)):
                    aliases.append(function.params[i].alias)
                    
            op_list.extend(self.update_function_ops(module, function_name, 
                                                    param_values,
                                                    should_replace=True, 
                                                    aliases=aliases))

        action = vistrails.core.db.action.create_action(op_list)
        self.add_new_action(action)

        self.current_pipeline = current_pipeline
        self.current_version = current_version
        
        return action.id
    
    ##########################################################################
    # Workflow Execution
    
    def execute_workflow_list(self, vistrails):
        """execute_workflow_list(vistrails: list) -> (results, bool)"""

        stop_on_error = getattr(get_vistrails_configuration(),
                                'stopOnError')
        interpreter = get_default_interpreter()
        changed = False
        results = []
        for vis in vistrails:
            error = None
            (locator, version, pipeline, view, aliases, params, reason, sinks, extra_info) = vis
            temp_folder_used = False
            if (not extra_info or not extra_info.has_key('pathDumpCells') or 
                not extra_info['pathDumpCells']):
                if extra_info is None:
                    extra_info = {}
                extra_info['pathDumpCells'] = create_temp_folder(prefix='vt_thumb')
                temp_folder_used = True

            kwargs = {'locator': locator,
                      'current_version': version,
                      'view': view if view is not None else DummyView(),
                      'logger': self.get_logger(),
                      'controller': self,
                      'aliases': aliases,
                      'params': params,
                      'reason': reason,
                      'sinks': sinks,
                      'extra_info': extra_info,
                      'stop_on_error': stop_on_error,
                      }    
            if self.get_vistrail_variables():
                kwargs['vistrail_variables'] = \
                    self.get_vistrail_variable_by_uuid
            result = interpreter.execute(pipeline, **kwargs)
            
            thumb_cache = ThumbnailCache.getInstance()
            
            if len(result.errors) == 0 and \
            (thumb_cache.conf.autoSave or 'compare_thumbnails' in extra_info):
                old_thumb_name = self.vistrail.get_thumbnail(version)
                if 'compare_thumbnails' in extra_info:
                    old_thumb_name = None
                fname = thumb_cache.add_entry_from_cell_dump(
                                        extra_info['pathDumpCells'],
                                        old_thumb_name)
                if 'compare_thumbnails' in extra_info:
                    # check thumbnail difference
                    prev = None
                    thumb_version = version
                    # the thumb can be in a previous upgrade
                    while not self.vistrail.has_thumbnail(thumb_version) and \
                        thumb_version in self.vistrail.actionMap and \
                        self.vistrail.has_upgrade(self.vistrail.actionMap[thumb_version].parent):
                        thumb_version = self.vistrail.actionMap[thumb_version].parent
                    if self.vistrail.has_thumbnail(thumb_version):
                        prev = thumb_cache.get_abs_name_entry(self.vistrail.get_thumbnail(thumb_version))
                    else:
                        error = CompareThumbnailsError("No thumbnail exist for version %s" % thumb_version)
                    if prev:
                        if not prev:
                            error = CompareThumbnailsError("No thumbnail file exist for version %s" % thumb_version)
                        elif not fname:
                            raise CompareThumbnailsError("No thumbnail generated")
                        else:
                            next = thumb_cache.get_abs_name_entry(fname)
                            if not next:
                                raise CompareThumbnailsError("No thumbnail file generated for version %s" % thumb_version)
                            else:
                                min_err = extra_info['compare_thumbnails'](prev, next)
                                treshold = 0.1
                                if min_err > treshold:
                                    raise CompareThumbnailsError("Thumbnails are different with value %s" % min_err, prev, next)

                if fname is not None:
                    self.vistrail.set_thumbnail(version, fname)
                    changed = True
              
            if temp_folder_used:
                remove_temp_folder(extra_info['pathDumpCells'])
            
            if result.parameter_changes:
                l = result.parameter_changes
                self.add_parameter_changes_from_execution(pipeline, version, l)
                changed = True
            
            results.append(result)
            if error:
                result.errors[version] = error
                return ([result], False)
        if self.logging_on():
            self.set_changed(True)
            
        if interpreter.debugger:
            interpreter.debugger.update_values()
        return (results,changed)
    
    def execute_current_workflow(self, custom_aliases=None, custom_params=None,
                                 extra_info=None, reason='Pipeline Execution',
                                 sinks=None):
        """ execute_current_workflow(custom_aliases: dict, 
                                     custom_params: list,
                                     extra_info: dict) -> (list, bool)
        Execute the current workflow (if exists)
        custom_params is a list of tuples (vttype, oId, newval) with new values
        for parameters
        extra_info is a dictionary containing extra information for execution.
        As we want to make the executions thread safe, we will pass information
        specific to each pipeline through extra_info
        As, an example, this will be useful for telling the spreadsheet where
        to dump the images.
        """
        self.flush_delayed_actions()
        if self.current_pipeline:
            locator = self.get_locator()
            if locator:
                locator.clean_temporaries()
                if self._auto_save:
                    locator.save_temporary(self.vistrail)
            try:
                return self.execute_workflow_list([(self.locator,
                                                    self.current_version,
                                                    self.current_pipeline,
                                                    None,
                                                    custom_aliases,
                                                    custom_params,
                                                    reason,
                                                    sinks,
                                                    extra_info)])
            except Exception, e:
                debug.unexpected_exception(e)
                raise

    def prune_versions(self, versions):
        """ prune_versions(versions: list of version numbers) -> None
        Prune all versions in 'versions' out of the view

        """
        # We need to go up-stream to the highest invisible node
        current = self._current_terse_graph
        if not current:
            self.recompute_terse_graph()
            current, full = self._current_terse_graph, self._current_full_graph
        else:
            full = self._current_full_graph
        changed = False
        new_current_version = None
        for v in versions:
            if v!=0: # not root
                highest = v
                while True:
                    p = full.parent(highest)
                    if p==-1:
                        break
                    if p in current.vertices:
                        break
                    highest = p
                if highest!=0:
                    changed = True
                    if highest == self.current_version:
                        new_current_version = full.parent(highest)
                self.vistrail.pruneVersion(highest)
        if changed:
            self.set_changed(True)
        if new_current_version is not None:
            self.change_selected_version(new_current_version)
        self.recompute_terse_graph()
        self.invalidate_version_tree(False)

    def hide_versions_below(self, v=None):
        """ hide_versions_below(v: int) -> None
        Hide all versions including and below v

        """
        if v is None:
            v = self.current_base_version
        full = self.vistrail.getVersionGraph()
        x = [v]

        am = self.vistrail.actionMap

        changed = False

        while 1:
            try:
                current=x.pop()
            except IndexError:
                break

            children = [to for (to, _) in full.adjacency_list[current]
                        if (to in am) and \
                            not self.vistrail.is_pruned(to)]
            self.vistrail.hideVersion(current)
            changed = True

            for child in children:
                x.append(child)

        if changed:
            self.set_changed(True)
        self.recompute_terse_graph()
        self.invalidate_version_tree(False, False)

    def show_all_versions(self):
        """ show_all_versions() -> None
        Unprune (graft?) all pruned versions

        """
        am = self.vistrail.actionMap
        for a in am.iterkeys():
            self.vistrail.showVersion(a)
        self.set_changed(True)
        self.recompute_terse_graph()
        self.invalidate_version_tree(False, False)

    def expand_versions(self, v1, v2):
        """ expand_versions(v1: int, v2: int) -> None
        Expand all versions between v1 and v2

        """
        full = self.vistrail.getVersionGraph()
        p = full.parent(v2)
        while p > v1:
            self.vistrail.expandVersion(p)
            p = full.parent(p)
        self.recompute_terse_graph()
        self.invalidate_version_tree(False, True)

    def collapse_versions(self, v):
        """ collapse_versions(v: int) -> None
        Collapse all versions including and under version v until the next tag or branch

        """
        full = self.vistrail.getVersionGraph()
        x = [v]

        am = self.vistrail.actionMap
        tm = self.vistrail.get_tagMap()

        upgrades = set()
        for ann in self.vistrail.action_annotations:
            if ann.key != Vistrail.UPGRADE_ANNOTATION:
                continue
            # The target is an upgrade
            upgrades.add(int(ann.value))

        while x:
            current = x.pop()

            all_children = [to for to, _ in full.adjacency_list[current]
                            if to in am]
            children = []
            while all_children:
                child = all_children.pop()
                # Pruned: drop it
                if self.vistrail.is_pruned(child):
                    pass
                # An upgrade: get its children directly
                # (unless it is tagged, and that tag couldn't be moved)
                elif (not self.show_upgrades and child in upgrades and
                        child not in tm):
                    all_children.extend(
                        to for to, _ in full.adjacency_list[child]
                        if to in am)
                else:
                    children.append(child)
            if len(children) > 1:
                break
            self.vistrail.collapseVersion(current)

            for child in children:
                if (not child in tm and  # has no Tag
                    child != self.current_base_version): # not selected
                    x.append(child)

        self.recompute_terse_graph()
        self.invalidate_version_tree(False, True)

    def expand_or_collapse_all_versions_below(self, v=None, expand=True):
        """ expand_or_collapse_all_versions_below(v: int) -> None
        Expand/Collapse all versions including and under version v

        """
        if v is None:
            v = self.current_base_version

        full = self.vistrail.getVersionGraph()
        x = [v]

        am = self.vistrail.actionMap

        while 1:
            try:
                current=x.pop()
            except IndexError:
                break

            children = [to for (to, _) in full.adjacency_list[current]
                        if (to in am) and not self.vistrail.is_pruned(to)]
            if expand:
                self.vistrail.expandVersion(current)
            else:
                self.vistrail.collapseVersion(current)

            for child in children:
                x.append(child)
        self.recompute_terse_graph()
        self.invalidate_version_tree(False, True)

    def expand_all_versions_below(self, v=None):
        self.expand_or_collapse_all_versions_below(v, True)

    def collapse_all_versions_below(self, v=None):
        self.expand_or_collapse_all_versions_below(v, False)

    def collapse_all_versions(self):
        """ collapse_all_versions() -> None
        Collapse all expanded versions

        """
        am = self.vistrail.actionMap
        for a in am.iterkeys():
            self.vistrail.collapseVersion(a)
        self.recompute_terse_graph()
        self.invalidate_version_tree(False, True)

    def recompute_terse_graph(self, show_upgrades=None):
        if show_upgrades is None:
            show_upgrades = not getattr(get_vistrails_configuration(),
                                        'hideUpgrades', True)
        self.show_upgrades = show_upgrades

        # get full version tree (including pruned nodes) this tree is
        # kept updated all the time. This data is read only and should
        # not be updated!
        fullVersionTree = self.vistrail.tree.getVersionTree()

        # create tersed tree
        open_list = [(0, None, False, False)]  # Elements to be handled
        tersedVersionTree = Graph()

        # cache actionMap and tagMap because they're properties, sort
        # of slow
        am = self.vistrail.actionMap
        tm = self.vistrail.get_tagMap()
        last_n = self.vistrail.getLastActions(self.num_versions_always_shown)

        upgrades = set()
        upgrade_rev_map = {}
        current_version = self.current_version
        def rev_map(v):
            return upgrade_rev_map.get(v, v)

        if not self.show_upgrades:
            # process upgrade annotations
            for ann in self.vistrail.action_annotations:
                if ann.key != Vistrail.UPGRADE_ANNOTATION:
                    continue
                # The target is an upgrade
                upgrades.add(int(ann.value))
                # Map from upgraded version to original
                upgrade_rev_map[int(ann.value)] = ann.action_id

            # Map current version
            current_version = rev_map(current_version)

            # Map tags
            tm, orig_tm = {}, tm
            for version, name in sorted(orig_tm.iteritems(),
                                        key=lambda p: p[0]):
                v = version
                while v in upgrade_rev_map:
                    v = upgrade_rev_map[v]
                    if v in orig_tm:
                        # Found another tag in upgrade chain, don't move tag
                        v = version
                        break
                tm[v] = name
            del orig_tm

            # Transitively flatten upgrade_rev_map
            for k, v in upgrade_rev_map.iteritems():
                while v in upgrade_rev_map:
                    v = upgrade_rev_map[v]
                upgrade_rev_map[k] = v

        while open_list:
            current, parent, expandable, collapsible = open_list.pop()

            # mount children list
            all_children = [
                to for to, _ in fullVersionTree.adjacency_list[current]
                if to in am]
            children = []
            while all_children:
                child = all_children.pop()
                # Pruned: drop it
                if self.vistrail.is_pruned(child):
                    pass
                # An upgrade: get its children directly
                # (unless it is tagged, and that tag couldn't be moved)
                elif (not self.show_upgrades and
                      (child in upgrades or
                       am[child].description == 'Upgrade') and
                      child not in tm):
                    all_children.extend(
                        to for to, _ in fullVersionTree.adjacency_list[child]
                        if to in am)
                else:
                    children.append(child)

            display = (self.full_tree or
                       current == 0 or                 # is root
                       current in tm or                # hasTag:
                       current in last_n or            # show latest
                       current == current_version or   # isCurrentVersion
                       len(children) != 1)             # leaf or branch

            if (display or am[current].expand):        # forced expansion

                # yes it will!  this needs to be here because if we
                # are refining version view receives the graph without
                # the non matching elements
                if (not self.refine or
                        (self.refine and not self.search) or
                        current == 0 or
                        (self.refine and self.search and
                         self.search.match(self.vistrail, am[current])) or
                        current == current_version):
                    # add vertex...
                    tersedVersionTree.add_vertex(current, tm.get(current))

                    # ...and the parent
                    if parent is not None:
                        collapse_here = not collapsible and not display
                        tersedVersionTree.add_edge(parent, current,
                                                   (expandable, collapse_here))
                        collapsible = collapsible or collapse_here

                    # update the parent info that will be used by the
                    # children of this node
                    parentToChildren = current
                    expandable = False
                else:
                    parentToChildren = parent
                    expandable = True
            else:
                parentToChildren = parent
                expandable = True

            if collapsible and len(children) > 1:
                collapsible = False
            for child in children:
                open_list.append((child, parentToChildren,
                                  expandable, collapsible))

        self._current_terse_graph = tersedVersionTree
        self._current_full_graph = self.vistrail.tree.getVersionTree()
        self._upgrade_rev_map = upgrade_rev_map

    def save_version_graph(self, filename, tersed=True, highlight=None):
        if tersed:
            graph = copy.copy(self._current_terse_graph)
        else:
            graph = copy.copy(self._current_full_graph)
        tm = self.vistrail.get_tagMap()
        vs = graph.vertices.keys()
        vs.sort()
        al = [(vfrom, vto, edgeid)
              for vfrom, lto in graph.adjacency_list.iteritems()
              for vto, edgeid in lto]
        al.sort()

        configuration = get_vistrails_configuration()
        use_custom_colors = configuration.check('customVersionColors')

        if isinstance(filename, basestring):
            fp = open(filename, 'wb')
            cleanup = lambda: fp.close()
        else:
            fp = filename
            cleanup = lambda: None
        try:
            fp.write('digraph G {\n')
            for v in vs:
                descr = tm.get(v, None) or self.vistrail.get_description(v)
                if use_custom_colors:
                    color = self.vistrail.get_action_annotation(
                            v,
                            custom_color_key)
                else:
                    color = None
                if color:
                    color = '#%s%s%s' % tuple(
                            '%02x' % c
                            for c in parse_custom_color(color.value))
                    fp.write('    %s [label=%s, '
                             'style=filled, fillcolor="%s", color="%s"];\n' % (
                             v, dot_escape(descr), color,
                             'red' if v == highlight else 'black'))
                else:
                    fp.write('    %s [label=%s, color="%s"];\n' % (
                             v, dot_escape(descr),
                             'red' if v == highlight else 'black'))
            fp.write('\n')
            for s in al:
                vfrom, vto, vdata = s
                fp.write('    %s -> %s;\n' % (vfrom, vto))
            fp.write('}\n')
        finally:
            cleanup()

    def get_latest_version_in_graph(self):
        if not self._current_terse_graph:
            # DAK do we want refine_graph here?
            # (current, full, layout) = self.refine_graph()
            self.recompute_terse_graph()
        if self._current_terse_graph:
            return max(self._current_terse_graph.iter_vertices())
        return max(self.actions)

    def select_latest_version(self):
        """ select_latest_version() -> None
        Try to select the latest visible version on the tree
        
        """
        self.change_selected_version(self.get_latest_version_in_graph())

    def enable_missing_package(self, identifier, deps):
        """callback for try_to_enable_package"""
        return True

    def install_missing_package(self, identifier):
        """callback for try_to_enable_package"""
        return True
       
    def try_to_enable_package(self, identifier, confirmed=False):
        """try_to_enable_package(identifier: str,
                                 dep_graph: Graph,
                                 confirmed: boolean)
        Returns True if changes have been made to the registry, which
        means reloading a pipeline that previously failed with missing
        packages might work now.  dep_graph will enable any
        dependencies.  Setting confirmed to True will bypass prompts
        for later enables.
        """

        pm = get_package_manager()
        pkg = pm.identifier_is_available(identifier)
        if pkg is None or pm.has_package(pkg.identifier):
            return False

        dep_graph = pm.build_dependency_graph([identifier])
        deps = pm.get_ordered_dependencies(dep_graph)
        other_deps = filter(lambda i: i != identifier, deps)
        if pkg.identifier in self._asked_packages:
            return False
        if not confirmed and \
                not self.enable_missing_package(pkg.identifier, other_deps):
            self._asked_packages.add(pkg.identifier)
            return False
        # Ok, user wants to late-enable it. Let's give it a shot
        for pkg_id in deps:
            if not self.do_enable_package(pkg_id):
                return False

        return True

    def do_enable_package(self, identifier):
        pm = get_package_manager()
        pkg = pm.identifier_is_available(identifier)
        if pkg and not pm.has_package(pkg.identifier):
            try:
                pm.late_enable_package(pkg.codepath)
                pkg = pm.get_package_by_codepath(pkg.codepath)
                if pkg.identifier != identifier:
                    # pkg is probably a parent of the "identifier" package
                    # try to load it
                    if hasattr(pkg.module, "can_handle_identifier") and \
                        pkg.module.can_handle_identifier(identifier):
                        pkg.init_module.load_from_identifier(identifier)
            except pkg.MissingDependency, e:
                for dependency in e.dependencies:
                    print 'MISSING DEPENDENCY:', dependency
                return False
            except pkg.InitializationFailed:
                self._asked_packages.add(pkg.identifier)
                raise
            # there's a new package in the system, so we retry
            # changing the version by recursing, since other
            # packages/modules might still be needed.
            self._asked_packages.add(pkg.identifier)
            return True
        # identifier may refer to a subpackage
        if pkg and pkg.identifier != identifier and \
           hasattr(pkg.module, "can_handle_identifier") and \
           pkg.module.can_handle_identifier(identifier) and \
           hasattr(pkg.init_module, "load_from_identifier"):
            pkg.init_module.load_from_identifier(identifier)
            return True
        # Package is not available, let's try to fetch it
        rep = vistrails.core.packagerepository.get_repository()
        if rep:
            codepath = rep.find_package(identifier)
            if codepath and self.install_missing_package(identifier):
                rep.install_package(codepath)
                return self.try_to_enable_package(identifier, True)
        self._asked_packages.add(identifier)
        return False

    def set_action_annotation(self, action, key, value, id_scope=None):
        if id_scope is None:
            id_scope = self.id_scope
        if action.has_annotation_with_key(key):
            old_annotation = action.get_annotation_by_key(key)
            if old_annotation.value == value:
                return False
            action.delete_annotation(old_annotation)
        if value.strip() != '':
            annotation = \
                Annotation(id=id_scope.getNewId(Annotation.vtType),
                           key=key,
                           value=value,
                           )
            action.add_annotation(annotation)

    def get_upgrade_module_remap(self, actions):
        """Try to get a module remap when possible.  This uses the fact that
        most generic actions will have a single delete module action
        and a single add module action.

        """
        is_full_remap = True
        remap = {}
        for action in actions:
            d_module_ids = []
            a_module_ids = []
            for op in action.operations:
                if op.vtType == 'delete' and op.what == 'module':
                    d_module_ids.append(op.db_objectId)
                if op.vtType == 'add' and op.what == 'module':
                    a_module_ids.append(op.db_objectId)
            if len(d_module_ids) == 1 and len(a_module_ids) == 1:
                remap[(Module.vtType, d_module_ids[0])] = a_module_ids[0]
            elif len(d_module_ids) + len(a_module_ids) > 0:
                is_full_remap = False
        return (remap, is_full_remap)

    def get_simple_upgrade_remap(self, actions):
        """Try to get module/function/parameter remaps when possible.  This
        uses the fact that most remaps only changes names and number of
        deletes/adds are the same and adds are done in the reverse order of
        deletes.
        """
        is_full_remap = True
        remap = {}
        for action in actions:
            delete_ops = []
            add_ops = []
            for op in action.operations:
                if op.vtType == 'delete':
                    delete_ops.append(op)
                if op.vtType == 'add':
                    add_ops.append(op)
            if len(delete_ops) != len(add_ops):
                return (remap, False)
            add_ops.reverse()
            for deleted, added in zip(delete_ops, add_ops):
                if deleted.what != added.what:
                    return (remap, False)
                if added.what == 'module':
                    remap[(Module.vtType, deleted.db_objectId)] = added.db_objectId
                if added.what == 'function':
                    if len(delete_ops) != len(add_ops):
                        return (remap, False)
                    remap[(ModuleFunction.vtType, deleted.db_objectId)] = added.db_objectId
                if added.what == 'parameter':
                    if len(delete_ops) != len(add_ops):
                        return (remap, False)
                    remap[(ModuleParam.vtType, deleted.db_objectId)] = added.db_objectId
        return (remap, is_full_remap)
                            
    def create_upgrade_action(self, actions):
        new_action = vistrails.core.db.action.merge_actions(actions)
        self.set_action_annotation(new_action, Action.ANNOTATION_DESCRIPTION, 
                                   "Upgrade")
        return new_action

    def check_delayed_update(self):
        if self.delayed_update:
            self.delayed_update = False
            self.set_changed(True)
            self.recompute_terse_graph()
            self.invalidate_version_tree(False)

    def handle_invalid_pipeline(self, e, new_version=-1, vistrail=None,
                                report_all_errors=False, force_no_delay=False,
                                delay_update=False, level=0, pipeline_only=False):
        debug.debug('Running handle_invalid_pipeline on %d' % new_version)
        if delay_update:
            force_no_delay = True
        def check_exceptions(exception_set):
            unhandled_exceptions = []
            for err in exception_set:
                if isinstance(err, InvalidPipeline):
                    sub_exceptions = check_exceptions(err.get_exception_set())
                    if len(sub_exceptions) > 0:
                        new_err = InvalidPipeline(sub_exceptions,
                                                  err._pipeline,
                                                  err._version)
                        unhandled_exceptions.append(new_err)
                else:
                    if not err._was_handled:
                        unhandled_exceptions.append(err)
            return unhandled_exceptions

        load_other_versions = False
        if vistrail is None:
            vistrail = self.vistrail
        pm = get_package_manager()
        root_exceptions = e.get_exception_set()
        missing_packages = {}
        def process_missing_packages(exception_set):
            for err in exception_set:
                err._was_handled = False
                # FIXME need to get module_id from these exceptions
                # when possible!  need to integrate
                # report_missing_module and handle_module_upgrade
                if isinstance(err, InvalidPipeline):
                    process_missing_packages(err.get_exception_set())
                elif isinstance(err, MissingPackage):
                    # check if the package was already installed before
                    # (because it was in the dependency list of a previous
                    # package)
                    if err._identifier not in missing_packages:
                        missing_packages[err._identifier] = []
                    missing_packages[err._identifier].append(err)

        process_missing_packages(root_exceptions)
        new_exceptions = []

        # Full dependency graph from all the packages detected as missing
        dep_graph = pm.build_dependency_graph(missing_packages.keys())
        deps = pm.get_ordered_dependencies(dep_graph)
        missing = set(missing_packages.iterkeys())
        # This orders the list of packages detected as missing according to
        # the order in which they'll be enabled
        # This is so that if pkgA is a dependency of pkgB and both are in
        # missing_packages.keys(), we enable pkgB before (since that will
        # enable pkgA)
        # This is to minimize the number of user prompts
        enable_pkgs = reversed([pkg_id
                                for pkg_id in deps
                                if pkg_id in missing])

        for identifier in enable_pkgs:
            if not pm.has_package(identifier):
                try:
                    if self.try_to_enable_package(identifier):
                        for err in missing_packages[identifier]:
                            err._was_handled = True
                except Exception, new_e:
                    debug.unexpected_exception(new_e)
                    new_exceptions.append(new_e)
                    if not report_all_errors:
                        raise new_e
            else:
                if identifier in missing_packages.iterkeys():
                    for err in missing_packages[identifier]:
                        err._was_handled = True
                # else assume the package was already enabled

        if len(new_exceptions) > 0:
            raise InvalidPipeline(check_exceptions(root_exceptions) + new_exceptions,
                                  e._pipeline, new_version)

        def process_package_versions(exception_set):
            for err in exception_set:
                if err._was_handled:
                    continue
                if isinstance(err, InvalidPipeline):
                    process_package_versions(err.get_exception_set())
                if isinstance(err, MissingPackageVersion):
                    # try and load other version of package?
                    err._was_handled = True
                    pass

        # instead of upgrading, may wish to load the old version of
        # the package if possible
        if load_other_versions:
            process_package_versions(root_exceptions)

        def process_package_exceptions(exception_set, pipeline):
            new_actions = []
            package_errs = {}
            for err in exception_set:
                if err._was_handled:
                    continue
                if isinstance(err, InvalidPipeline):
                    # handle invalid group/abstraction
                    id_scope = IdScope(1, {Group.vtType: Module.vtType,
                                           Abstraction.vtType: Module.vtType})
                    id_remap = {}
                    new_pipeline = err._pipeline.do_copy(True, id_scope,
                                                         id_remap)
                    new_exception_set = []
                    for sub_err in err.get_exception_set():
                        key = (Module.vtType, sub_err._module_id)
                        if key in id_remap:
                            sub_err._module_id = id_remap[key]
                            new_exception_set.append(sub_err)
                        else:
                            new_exception_set.append(sub_err)

                    # set id to None so db saves correctly
                    new_pipeline.id = None
                    # FIXME: We should not temporarily replace id_scope
                    old_id_scope = self.id_scope
                    self.id_scope = id_scope

                    # run handle_invalid_pipeline to fix multi-step upgrades
                    try:
                        _, new_pipeline = \
                            self.handle_invalid_pipeline(err,
                                                    report_all_errors=True,
                                                    pipeline_only=True)
                    except InvalidPipeline, e:
                        # Group cannot be fixed
                        # we just keep the old invalid group
                        debug.unexpected_exception(e)
                        raise e
                    finally:
                        self.id_scope = old_id_scope
                    if new_pipeline != err._pipeline:
                        # create action that recreates group/subworkflow
                        old_module = pipeline.modules[err._module_id]
                        if old_module.is_group():
                            my_actions = \
                                UpgradeWorkflowHandler.replace_group(
                                self, pipeline, old_module.id, new_pipeline)
                            for action in my_actions:
                                pipeline.perform_action(action)
                            new_actions.extend(my_actions)

                elif (isinstance(err, MissingModule) or
                      isinstance(err, MissingPackageVersion) or
                      isinstance(err, MissingModuleVersion)):
                    if err._identifier not in package_errs:
                        package_errs[err._identifier] = []
                    package_errs[err._identifier].append(err)

            for identifier, err_list in package_errs.iteritems():
                try:
                    pkg = pm.get_package(identifier)
                except MissingPackage:
                    # cannot get the package we need
                    continue
                details = '\n'.join(debug.format_exception(e)
                                    for e in err_list)
                debug.debug('Processing upgrades in package "%s"' %
                          identifier, details)
                if pkg.can_handle_all_errors():
                    try:
                        actions = pkg.handle_all_errors(self, err_list,
                                                        pipeline)
                        if actions is not None:
                            for action in actions:
                                pipeline.perform_action(action)
                            new_actions.extend(actions)
                            for err in err_list:
                                err._was_handled = True
                    except Exception, new_e:
                        debug.unexpected_exception(new_e)
                        new_exceptions.append(new_e)
                        if not report_all_errors:
                            return new_actions
                else:
                    # process default upgrades
                    # handler = UpgradeWorkflowHandler(self, pipeline)
                    for err in err_list:
                        try:
                            actions = UpgradeWorkflowHandler.dispatch_request(
                                self, err._module_id, pipeline)
                            if actions is not None:
                                for action in actions:
                                    pipeline.perform_action(action)
                                new_actions.extend(actions)
                                err._was_handled = True
                        except Exception, new_e:
                            debug.unexpected_exception(new_e)
                            new_exceptions.append(new_e)

                if pkg.can_handle_missing_modules():
                    for err in err_list + new_exceptions:
                        if hasattr(err, '_was_handled') and err._was_handled:
                            continue
                        if isinstance(err, MissingModule):
                            try:
                                res = pkg.handle_missing_module(self,
                                                                err._module_id,
                                                                pipeline)
                                # need backward compatibility
                                if res is True:
                                    err._was_handled = True
                                elif res is False:
                                    pass
                                else:
                                    actions = res
                                    if actions is not None:
                                        for action in actions:
                                            pipeline.perform_action(action)
                                        new_actions.extend(actions)
                                        err._was_handled = True
                            except Exception, new_e:
                                debug.unexpected_exception(new_e)
                                new_exceptions.append(new_e)
                                if not report_all_errors:
                                    return new_actions
            return new_actions

        if get_vistrails_configuration().check('upgrades'):
            cur_pipeline = copy.copy(e._pipeline)
            # note that cur_pipeline is modified to be the result of
            # applying the actions in new_actions
            new_actions = process_package_exceptions(root_exceptions,
                                                     cur_pipeline)
        else:
            new_actions = []
            cur_pipeline = e._pipeline

        if not pipeline_only and len(new_actions) > 0:
            upgrade_action = self.create_upgrade_action(new_actions)
            # check if we should use pending param_exps
            if (get_vistrails_configuration().check('upgradeDelay') and not force_no_delay
                and self._delayed_paramexps):
                param_exps = self._delayed_paramexps
                self._delayed_paramexps = []
            else:
                param_exps = self.vistrail.get_paramexps(new_version)
            new_param_exps = []
            if len(param_exps) > 0:
                (module_remap, is_complete) = \
                                    self.get_upgrade_module_remap(new_actions)
                if is_complete:
                    for pe in param_exps:
                        old_pe = None
                        # loop because we may have multi-step upgrades
                        while old_pe != pe:
                            old_pe = pe
                            pe = pe.do_copy(True, self.id_scope, module_remap)
                        new_param_exps.append(pe)
                else:
                    debug.warning("Cannot translate old parameter "
                                  "explorations through upgrade.")
            mashup = None
            if hasattr(self, "_mashups"):
                for mashuptrail in self._mashups:
                    if mashuptrail.vtVersion == new_version:
                        mashup = mashuptrail
            new_mashups = []
            if mashup:
                # mashups are not delayable
                force_no_delay = True
                (mfp_remap, is_complete) = \
                                self.get_simple_upgrade_remap(new_actions)
                if is_complete:
                    # FIXME: we should move the remapping to the db layer
                    # But we need to fix the schema by making functions/params
                    # foreign keys

                    #mashup = mashup.do_copy(True, self.id_scope, mfp_remap)
                    #mashup.id = uuid.uuid1()
                    # we move it to the new version so that references still work
                    self._mashups.remove(mashup)

                    for action in mashup.actions:
                        for alias in action.mashup.aliases:
                            c = alias.component
                            while (Module.vtType, c.vtmid) in mfp_remap:
                                c.vtmid = mfp_remap[(Module.vtType, c.vtmid)]
                            while (ModuleFunction.vtType,
                                c.vtparent_id) in mfp_remap:
                                c.vtparent_id=mfp_remap[(ModuleFunction.vtType,
                                                         c.vtparent_id)]
                            while (ModuleParam.vtType, c.vtid) in mfp_remap:
                                c.vtid = mfp_remap[(ModuleParam.vtType,
                                                     c.vtid)]
                    mashup.currentVersion = mashup.getLatestVersion()

                    new_mashups.append(mashup)
                else:
                    debug.warning("Cannot translate old mashup "
                                  "through upgrade.")

            if get_vistrails_configuration().check('upgradeDelay') and not force_no_delay:
                self._delayed_actions.append(upgrade_action)
                self._delayed_paramexps.extend(new_param_exps)
                self._delayed_mashups.extend(new_mashups)
            else:
                vistrail.add_action(upgrade_action, new_version,
                                    self.current_session)
                vistrail.set_upgrade(new_version, str(upgrade_action.id))
                if get_vistrails_configuration().check("migrateTags"):
                    self.migrate_tags(new_version, upgrade_action.id, vistrail)
                new_version = upgrade_action.id
                for pe in new_param_exps:
                    pe.action_id = new_version
                    self.vistrail.db_add_parameter_exploration(pe)
                for mashup in new_mashups:
                    mashup.vtVersion = new_version
                    for action in mashup.actions:
                        action.mashup.version = new_version
                    self._mashups.append(mashup)

                if delay_update:
                    self.delayed_update = True
                else:
                    self.set_changed(True)
                    self.recompute_terse_graph()

        left_exceptions = check_exceptions(root_exceptions)
        # If exceptions unchanged, fail.
        debug.debug(('handle_invalid_pipeline finished with %d fixed, %d left, '
                     'and %d new exceptions') % ((len(root_exceptions) -
                                                  len(left_exceptions)),
                                                 len(left_exceptions),
                                                 len(new_exceptions)))
        if (len(left_exceptions) == len(root_exceptions) and
            len(new_exceptions) == 0):
            debug.debug('handle_invalid_pipeline failed to validate version '
                        '%d: %d errors left.' % (new_version,
                                               len(root_exceptions)))
            raise InvalidPipeline(left_exceptions + new_exceptions,
                                  cur_pipeline, new_version)
        new_err = None
        # do we have new exceptions or did we reduce the existing ones?
        if len(left_exceptions) > 0 or len(new_exceptions) > 0:
            new_err = InvalidPipeline(left_exceptions + new_exceptions,
                                      cur_pipeline, new_version)
        else:
            # All handled, check if validating generates further exceptions.
            try:
                self.validate(cur_pipeline)
            except InvalidPipeline, e:
                e._version = new_version
                new_err = e

        if new_err is not None:
            # There are still unresolved exceptions (old or new), try to
            # run handle_invalid_pipeline again.
            # each level creates a new upgrade
            level += 1
            max_loops = getattr(get_vistrails_configuration(),
                                'maxPipelineFixAttempts', 50)
            if level >= max_loops:
                debug.critical(
                        "Pipeline-fixing loop doesn't seem to "
                        "be finishing, giving up after %d "
                        "iterations. You may have circular "
                        "upgrade paths!" % level)
            else:
                debug.debug('Recursing handle_invalid_pipeline on '
                            'version %d to level %d' % (new_version, level))
                return self.handle_invalid_pipeline(new_err,
                                                    new_version,
                                                    vistrail,
                                                    report_all_errors,
                                                    force_no_delay,
                                                    delay_update,
                                                    level,
                                                    pipeline_only)
            raise new_err
        return new_version, cur_pipeline

    def validate(self, pipeline, raise_exception=True):
        vistrail_vars = self.get_vistrail_variables()
        pipeline.validate(raise_exception, vistrail_vars)

    def version_switch_cost(self, descendant, ancestor):
        """ Version switch cost as action distance

        """
        cost = 0
        am = self.vistrail.actionMap
        if descendant == -1:
            descendant = 0
        while descendant != ancestor:
            descendant = am[descendant].parent
            cost += 1
        return cost

    def do_version_switch(self, new_version, report_all_errors=False,
                          do_validate=True, from_root=False):
        """ do_version_switch(new_version: int,
                              resolve_all_errors: boolean) -> None
        Change the current vistrail version into new_version, reporting
        either the first error or all errors.

        """
        new_error = None
        try:
            self.current_pipeline = self.get_pipeline(new_version,
                                                      do_validate=do_validate,
                                                      from_root=from_root,
                                                      use_current=True)
            self.current_version = new_version
        except InvalidPipeline, e:
            try:
                self.current_version, self.current_pipeline = \
                    self.validate_version(new_version,
                                          report_all_errors,
                                          from_root)
            except InvalidPipeline, e:
                # just do the version switch anyway, but alert the
                # user to the remaining issues
                self.current_pipeline = e._pipeline
                self.current_version = e._version
                new_error = e

        if new_version != self.current_version:
            self.invalidate_version_tree(False)
        if new_error is not None:
            raise new_error

    def validate_version(self, version, report_all_errors=False,
                         from_root=False, delay_update=False, use_current=True):
        """ validates a pipeline version and returns the updated version

        version: the version to validate
        report_all_errors: Do not stop at first error
        from_root: do not try to use an existing pipeline
        delay_update: Delay version tree update
        use_current: Use current pipeline when searching for closest pipeline

        Returns the valid (version, pipeline) or raises an InvalidPipeline exception
        """

        # This is tricky code, so watch carefully before you change
        # it.  The biggest problem is that we want to perform state
        # changes only after all exceptions have been handled, but
        # creating a pipeline every time is too slow. The solution
        # then is to mutate the pipeline, and in case exceptions
        # are thrown, we roll back by rebuilding the pipeline from
        # scratch as the first thing on the exception handler, so to
        # the rest of the exception handling code, things look
        # stateless.

        def _validate_version(version):
            """ Validates without looking at upgrades
                returns (version, pipeline) or throws InvalidPipeline
            """
            try:
                pipeline = self.get_pipeline(version, from_root=from_root,
                                             use_current=use_current)
            except InvalidPipeline, e:
                try:
                    version, pipeline = \
                        self.handle_invalid_pipeline(e, version,
                                                     self.vistrail,
                                                     report_all_errors,
                                                     delay_update=delay_update)
                except InvalidPipeline, e:
                    debug.unexpected_exception(e)
                    raise e
            return version, pipeline
        # end _validate_version

        try:
            # first try without upgrading
            pipeline = self.get_pipeline(version, from_root=from_root,
                                         use_current=use_current)
        except InvalidPipeline:
            # Try latest upgrade first, then try previous upgrades.
            # If all fail, return latest upgrade exception.
            upgrade_chain = self.vistrail.get_upgrade_chain(version, True)
            # remove missing and pruned versions
            upgrade_chain = [v for v in upgrade_chain
                             if v in self.vistrail.actionMap and
                             not self.vistrail.is_pruned(v)]
            try:
                return _validate_version(upgrade_chain.pop())
            except InvalidPipeline, e:
                while upgrade_chain:
                    try:
                        return _validate_version(upgrade_chain.pop())
                    except InvalidPipeline:
                        # Failed, so try previous.
                        pass
                # We failed, so raise exception for latest upgrade.
                raise e
        return version, pipeline

    def change_selected_version(self, new_version, report_all_errors=True,
                                do_validate=True, from_root=False):
        try:
            self.do_version_switch(new_version, report_all_errors, 
                                   do_validate, from_root)
        except InvalidPipeline, e:
            # FIXME: do error handling through central switch that produces gui
            # or core.debug messages as specified
            def process_err(err):
                if isinstance(err, Package.InitializationFailed):
                    msg = ('Package "%s" failed during initialization. '
                           'Please contact the developer of that package '
                           'and report a bug.' % err.package.name)
                    debug.critical(msg)
                elif isinstance(err, MissingPackage):
                    msg = ('Cannot find package "%s" in '
                           'list of available packages. '
                           'Please install it first.' % err._identifier)
                    debug.critical(msg)
                elif issubclass(err.__class__, MissingPort):
                    msg = ('Cannot find %s port "%s" for module "%s" '
                           'in loaded package "%s". A different package '
                           'version might be necessary.') % \
                           (err._port_type, err._port_name, 
                            err._module_name, err._package_name)
                    debug.critical(msg)
                else:
                    debug.critical(str(err))                

            if report_all_errors:
                for err in e._exception_set:
                    process_err(err)
            elif len(e._exception_set) > 0:
                process_err(e._exception_set.__iter__().next())
        except Exception, e:
            debug.critical("Unhandled exception", debug.format_exc())

    def write_temporary(self):
        if self.vistrail and self.changed:
            locator = self.get_locator()
            if locator:
                locator.save_temporary(self.vistrail)

    def write_abstractions(self, locator, save_bundle, abstractions, 
                           abs_save_dir):
        def make_abstraction_path_unique(abs_fname, namespace):
            # Constructs the abstraction name using the namespace to
            # prevent conflicts and copies the abstraction to the new
            # path so save_bundle has a valid file
            path, prefix, absname, old_ns, suffix = \
                parse_abstraction_name(abs_fname, True)
            new_abs_fname = os.path.join(abs_save_dir, 
                                         '%s%s(%s)%s' % (prefix, absname, 
                                                         namespace, suffix))
            # print " $@$@$ new_abs_fname:", new_abs_fname
            shutil.copy(abs_fname, new_abs_fname)
            return new_abs_fname

        included_abstractions = {}
        for abstraction_list in abstractions.itervalues():
            for abstraction in abstraction_list:
                abs_module = abstraction.module_descriptor.module
                namespaces = set(get_all_abs_namespaces(abstraction.vistrail))
                if abs_module is not None:
                    abs_fname = abs_module.vt_fname
                    path, prefix, abs_name, old_ns, suffix = \
                        parse_abstraction_name(abs_fname, True)
                    # do our indexing by abstraction name
                    # we know that abstractions with different names
                    # cannot overlap, but those that have the same
                    # name may or may not
                    if abs_name not in included_abstractions:
                        included_abstractions[abs_name] = [(abstraction, 
                                                            namespaces)]
                    else:
                        # only keep abstractions that don't repeat what
                        # others already cover
                        new_list = []
                        found = False
                        for (i_abs, i_namespaces) in \
                                included_abstractions[abs_name]:
                            if not (i_namespaces < namespaces):
                                new_list.append((i_abs, i_namespaces))
                            if i_namespaces >= namespaces:
                                found = True
                        # only add new one once
                        if not found:
                            new_list.append((abstraction, namespaces))
                        included_abstractions[abs_name] = new_list

        for abs_name, abstraction_list in included_abstractions.iteritems():
            for (abstraction, _) in abstraction_list:
                abs_module = abstraction.module_descriptor.module
                if abs_module is None:
                    continue
                abs_fname = abs_module.vt_fname
                if not os.path.exists(abs_fname):
                    # Write vistrail to disk if the file no longer
                    # exists (if temp file was deleted)
                    abs_fname = os.path.join(abs_save_dir, 
                                             abstraction.name + '.xml')
                    save_abstraction(abstraction.vistrail, abs_fname)
                namespace = get_cur_abs_namespace(abstraction.vistrail)
                abs_unique_name = make_abstraction_path_unique(abs_fname,
                                                               namespace)
                save_bundle.abstractions.append(abs_unique_name)
                                
    def write_vistrail(self, locator, version=None, export=False):
        """write_vistrail(locator,version) -> Boolean
        It will return a boolean that tells if the tree needs to be 
        invalidated
        export=True means you should not update the current controller"""
        result = False 
        if self.vistrail and (self.changed or self.locator != locator):
            # Save jobs as annotation
            if self.jobMonitor.workflows:
                self.vistrail.set_annotation('__jobs__',
                                             self.jobMonitor.serialize())
            else:
                self.vistrail.set_annotation('__jobs__', '')
            # FIXME create this on-demand?
            abs_save_dir = tempfile.mkdtemp(prefix='vt_abs')
            is_abstraction = self.vistrail.is_abstraction
            if is_abstraction and self.changed:
                # first update any names if necessary
                self.check_subpipeline_port_names()
                new_namespace = str(uuid.uuid1())
                annotation_key = get_next_abs_annotation_key(self.vistrail)
                self.vistrail.set_annotation(annotation_key, new_namespace)
            save_bundle = SaveBundle(self.vistrail.vtType)
            if export:
                save_bundle.vistrail = self.vistrail.do_copy()
                if isinstance(locator, vistrails.core.db.locator.DBLocator):
                    save_bundle.vistrail.db_log_filename = None
            else:
                save_bundle.vistrail = self.vistrail
            if self.log and len(self.log.workflow_execs) > 0:
                save_bundle.log = self.log
            abstractions = self.find_abstractions(self.vistrail, True)
            self.write_abstractions(locator, save_bundle, abstractions, 
                                    abs_save_dir)
            thumb_cache = ThumbnailCache.getInstance()
            if thumb_cache.conf.autoSave:
                save_bundle.thumbnails = self.find_thumbnails(
                                           tags_only=thumb_cache.conf.tagsOnly)
            
            #mashups
            save_bundle.mashups = self._mashups
            # FIXME hack to use db_currentVersion for convenience
            # it's not an actual field
            self.vistrail.db_currentVersion = self.current_version
            if self.locator != locator:
                # check for db log
                log = Log()
                if isinstance(self.locator, vistrails.core.db.locator.DBLocator):
                    connection = self.locator.get_connection()
                    db_log = open_vt_log_from_db(connection, 
                                                 self.vistrail.db_id)
                    Log.convert(db_log)
                    for workflow_exec in db_log.workflow_execs:
                        workflow_exec.db_id = \
                            log.id_scope.getNewId(DBWorkflowExec.vtType)
                        log.db_add_workflow_exec(workflow_exec)
                # add recent log entries
                if self.log and len(self.log.workflow_execs) > 0:
                    for workflow_exec in self.log.db_workflow_execs:
                        workflow_exec = copy.copy(workflow_exec)
                        workflow_exec.db_id = \
                            log.id_scope.getNewId(DBWorkflowExec.vtType)
                        log.db_add_workflow_exec(workflow_exec)
                if len(log.workflow_execs) > 0:
                    save_bundle.log = log
                old_locator = self.get_locator()
                if not export:
                    self.locator = locator
                save_bundle = locator.save_as(save_bundle, version)
                new_vistrail = save_bundle.vistrail
                if isinstance(locator, vistrails.core.db.locator.DBLocator):
                    new_vistrail.db_log_filename = None
                    locator.kwargs['obj_id'] = new_vistrail.db_id
                if not export:
                    # DAK don't think is necessary since we have a new
                    # namespace for an abstraction on each save
                    # Unload abstractions from old namespace
                    # self.unload_abstractions() 
                    # Load all abstractions from new namespaces
                    self.ensure_abstractions_loaded(new_vistrail, 
                                                    save_bundle.abstractions) 
                    self.set_file_name(locator.name)
                    if old_locator and not export:
                        old_locator.clean_temporaries()
                        old_locator.close()
                    self.flush_pipeline_cache()
                    self.change_selected_version(new_vistrail.db_currentVersion, 
                                                 from_root=True)
            else:
                save_bundle = self.locator.save(save_bundle)
                new_vistrail = save_bundle.vistrail
                # Load any abstractions that were given new namespaces
                self.ensure_abstractions_loaded(new_vistrail, 
                                                save_bundle.abstractions)
            # FIXME abstractions only work with FileLocators right now
            if is_abstraction:
                new_vistrail.is_abstraction = True
                if isinstance(self.locator, (
                        vistrails.core.db.locator.XMLFileLocator,
                        vistrails.core.db.locator.ZIPFileLocator)):
                    filename = self.locator.name
                    if filename in self._loaded_abstractions:
                        del self._loaded_abstractions[filename]
                    # we don't know if the subworkflow should be shown
                    # if it doesn't currently exist, we don't want to add it
                    # if it does, we will replace it via upgrade module
                    # so it is not global
                    self.load_abstraction(filename, False)
                    
                    # reg = core.modules.module_registry.get_module_registry()
                    # for desc in reg.get_package_by_name('local.abstractions').descriptor_list:
                    #     print desc.name, desc.namespace, desc.version
            if not export:
                if id(self.vistrail) != id(new_vistrail):
                    new_version = new_vistrail.db_currentVersion
                    # FIXME have to figure out what to do here !!!
                    self.set_vistrail(new_vistrail, locator)
                    self.change_selected_version(new_version)
                    result = True
                if self.log:
                    self.log.delete_all_workflow_execs()
                self.set_changed(False)
                locator.clean_temporaries()

            # delete any temporary subworkflows
                try:
                    for root, _, files in os.walk(abs_save_dir, topdown=False):
                        for name in files:
                            os.remove(os.path.join(root, name))
                    os.rmdir(abs_save_dir)
                except OSError, e:
                    raise VistrailsDBException("Can't remove %s: %s" % (
                                               abs_save_dir,
                                               debug.format_exception(e)))
            return result


    def write_workflow(self, locator, version=None):
        if self.current_pipeline:
            pipeline = Pipeline()
            # pipeline.set_abstraction_map(self.vistrail.abstractionMap)
            for module in self.current_pipeline.modules.itervalues():
                # if module.vtType == AbstractionModule.vtType:
                #     abstraction = \
                #         pipeline.abstraction_map[module.abstraction_id]
                #     pipeline.add_abstraction(abstraction)
                pipeline.add_module(module)
            for connection in self.current_pipeline.connections.itervalues():
                pipeline.add_connection(connection)
            save_bundle = SaveBundle(pipeline.vtType,workflow=pipeline)
            locator.save_as(save_bundle, version)

    def write_log(self, locator):
        if self.log:
            if self.vistrail.db_log_filename is not None:
                log = vistrails.core.db.io.merge_logs(self.log, 
                                            self.vistrail.db_log_filename)
            else:
                log = self.log
            #print log
            save_bundle = SaveBundle(log.vtType,log=log)
            locator.save_as(save_bundle)

    def read_log(self):
        """ Returns the saved log from zip or DB
        
        """
        return self.vistrail.get_persisted_log()
 
    def write_registry(self, locator):
        registry = vistrails.core.modules.module_registry.get_module_registry()
        save_bundle = SaveBundle(registry.vtType, registry=registry)
        locator.save_as(save_bundle)

    def update_checkout_version(self, app=''):
        self.vistrail.update_checkout_version(app)

    def reset_redo_stack(self):
        self.redo_stack = []

    def undo(self):
        """Performs one undo step, moving up the version tree."""
        action_map = self.vistrail.actionMap
        old_action = action_map.get(self.current_version, None)
        self.redo_stack.append(self.current_version)
        self.show_parent_version()
        new_action = action_map.get(self.current_version, None)
        return (old_action, new_action)
        # self.set_pipeline_selection(old_action, new_action, 'undo')
        # return self.current_version

    def redo(self):
        """Performs one redo step if possible, moving down the version tree."""
        action_map = self.vistrail.actionMap
        old_action = action_map.get(self.current_version, None)
        if len(self.redo_stack) < 1:
            debug.critical("Redo on an empty redo stack. Ignoring.")
            return
        next_version = self.redo_stack[-1]
        self.redo_stack = self.redo_stack[:-1]
        self.show_child_version(next_version)
        new_action = action_map[self.current_version]
        return (old_action, new_action)
        # self.set_pipeline_selection(old_action, new_action, 'redo')
        # return next_version

    def can_redo(self):
        return (len(self.redo_stack) > 0)

    def can_undo(self):
        return self.current_version > 0

    def layout_modules(self, old_modules=[], preserve_order=False, 
               new_modules=[], new_connections=[], module_size_func=None, no_gaps=False):
        """Lays out modules and returns the new version.
        
        If old_modules are not specified, all modules in current pipeline are used.
        If preserve_order is True, modules in each row will be ordered based on
            their current x value
        new_modules ignore preserve_order, and don't need exist yet in the pipeline
        new_connections associated with new_modules
        module_size_func is used to determine size of a module. It takes a
            vistrails.core.layout.workflow_layout.Module object and returns a (width, height)
            tuple.
        If no_gaps is True, all connected modules will be at most 1 layer above or
            below their child or parent respectively
        """
        
        #fixes issue when opening old vistrails that needs upgrade
        self.flush_delayed_actions()
        
        action_list = self.layout_modules_ops(old_modules, preserve_order, 
                                      new_modules, new_connections, module_size_func, no_gaps)
        if(len(action_list) > 0):
            action = vistrails.core.db.action.create_action(action_list)
            self.add_new_action(action)
            version = self.perform_action(action)
            self.change_selected_version(version)
            return version
        return self.current_version

    def layout_modules_ops(self, old_modules=[], preserve_order=False, 
               new_modules=[], new_connections=[], module_size_func=None, no_gaps=False):
        """Returns operations needed to layout the modules.
        
        If old_modules are not specified, all modules in current pipeline are used.
        If preserve_order is True, modules in each row will be ordered based on
            their current x value
        new_modules ignore preserve_order, and don't need exist yet in the pipeline
        new_connections associated with new_modules
        module_size_func is used to determine size of a module. It takes a
            vistrails.core.layout.workflow_layout.Module object and returns a (width, height)
            tuple.
        If no_gaps is True, all connected modules will be at most 1 layer above or
            below their child or parent respectively
        """

        connected_input_ports = set(
                c.destination.spec for c in self.current_pipeline.connection_list)
        connected_input_ports.update(
                c.destination.spec for c in new_connections)
        connected_output_ports = set(
                c.source.spec for c in self.current_pipeline.connection_list)
        connected_output_ports.update(
                c.source.spec for c in new_connections)
        connected_ports = connected_input_ports | connected_output_ports

        def get_visible_port_names(port_list, visible_ports):
            output_list = []
            visible_list = []
            for i, p in enumerate(port_list):
                if not p.optional:
                    output_list.append(p.name)
                elif p.name in visible_ports or p in connected_ports:
                    visible_list.append(p.name)
            output_list.extend(visible_list)
            return output_list
        
        if not old_modules or len(old_modules) == 0:
            old_modules = self.current_pipeline.modules.values()
        
        #create layout objects
        layoutPipeline = LayoutPipeline()

        module_info = {} # {id: (module, layoutModule, in_port_names=[], out_port_names=[])}
        
        #add modules to layout, and find their visible ports
        def _add_layout_module(module, prev_x):
            in_ports = get_visible_port_names(module.destinationPorts(), 
                                         module.visible_input_ports)
            out_ports = get_visible_port_names(module.sourcePorts(),
                                          module.visible_output_ports)
            
            layoutModule = layoutPipeline.createModule(module.id, 
                                        module.name,
                                        len(in_ports),
                                        len(out_ports),
                                        prev_x)
            
            module_info[module.id] = (module, layoutModule, in_ports, out_ports)
        
        for module in old_modules:
            _add_layout_module(module, module.location.x)
            
        for module in new_modules:
            _add_layout_module(module, None)
        
        #add connections to layout
        old_ids = [module.id for module in old_modules]
        old_conns = self.get_connections_to(self.current_pipeline, old_ids)
        for conn in old_conns + new_connections:
            if conn.source.moduleId in module_info:
                layoutPipeline.createConnection(
                        module_info[conn.source.moduleId][1],
                        module_info[conn.source.moduleId][3].index(conn.source.name),
                        module_info[conn.destination.moduleId][1],
                        module_info[conn.destination.moduleId][2].index(conn.destination.name))
            
        #set default module size function if needed
        paddedPortWidth = self.layoutTheme.PORT_WIDTH + self.layoutTheme.MODULE_PORT_SPACE
        def estimate_module_size(module):
            width = max(len(module.name)*6 + self.layoutTheme.MODULE_LABEL_MARGIN[0] + self.layoutTheme.MODULE_LABEL_MARGIN[1],
                        len(module_info[module.shortname][2]) * paddedPortWidth + self.layoutTheme.MODULE_PORT_PADDED_SPACE,
                        len(module_info[module.shortname][3]) * paddedPortWidth + self.layoutTheme.MODULE_PORT_PADDED_SPACE)
            height = LayoutDefaults.u * 5 #todo, fix these sizes
            return (width, height)
        if module_size_func is None:
            module_size_func = estimate_module_size
            
        workflowLayout = WorkflowLayout(layoutPipeline,
                                        module_size_func,
                                        self.layoutTheme.MODULE_PORT_MARGIN, 
                                        (self.layoutTheme.PORT_WIDTH, self.layoutTheme.PORT_HEIGHT), 
                                        self.layoutTheme.MODULE_PORT_SPACE)
    
        #do layout with layer x and y separation of 50
        workflowLayout.run_all(50,50,preserve_order,no_gaps)
                
        #maintain center
        center_x, center_y = self.get_avg_location([item[0] for item in module_info.values()])
        new_center_x = sum([m.layout_pos.x for m in layoutPipeline.modules]) / len(layoutPipeline.modules)
        new_center_y = -sum([m.layout_pos.y for m in layoutPipeline.modules]) / len(layoutPipeline.modules)
        offset_x = center_x - new_center_x
        offset_y = center_y - new_center_y
        
        #generate module move list
        moves = []
        for (module, layoutModule, _, _) in module_info.values():
            new_x = layoutModule.layout_pos.x+offset_x
            new_y = -layoutModule.layout_pos.y+offset_y
            if module.id in self.current_pipeline.modules:
                moves.append((module.id, new_x, new_y))
            else:
                #module doesn't exist in pipeline yet, just change x,y
                module.location.x = new_x
                module.location.y = new_y
                
        #return module move operations
        return self.move_modules_ops(moves)

    def get_pipeline(self, version, allow_fail=False, use_current=False,
                     do_validate=True, from_root=False):
        """ Tries to construct the pipeline for a version in the fastest way
            possible using cached pipelines and version distances, and
            optionally current_pipeline.
        """
        if use_current and self.current_version != -1 and not self.current_pipeline:
            debug.warning("current_version is not -1 and "
                          "current_pipeline is None")
        if use_current and version != self.current_version:
            # clear delayed actions
            # FIXME: invert the delayed actions and integrate them into
            # the general_action_chain?
            if len(self._delayed_actions) > 0:
                self.clear_delayed_actions()
                self.current_pipeline = Pipeline()
                self.current_version = 0
        if version == -1:
            return None

        # now we reuse some existing pipeline, even if it's the
        # empty one for version zero
        #
        # The available pipelines are in self._pipelines, plus
        # the current pipeline.
        # Fast check: do we have to change anything?
        if from_root:
            result = self.vistrail.getPipeline(version)
        elif use_current and version == self.current_version:
            # Changing to current pipeline
            # We only need to run validation if it was previously invalid
            # (or didn't get validated)
            result = self.current_pipeline
            if self.current_pipeline.is_valid:
                return result
        # Fast check: if target is cached, copy it and we're done.
        elif version in self._pipelines:
            result = copy.copy(self._pipelines[version])
        else:
            # Find the closest upstream pipeline to the current one
            cv = self._current_full_graph.inverse_immutable().closest_vertex
            closest = cv(version, self._pipelines)
            if use_current:
                cost_to_closest_version = self.version_switch_cost(version,
                                                                   closest)
                # Now we have to decide between the closest pipeline
                # to version and the current pipeline
                shared_parent = getSharedRoot(self.vistrail,
                                              [self.current_version,
                                               version])
                cost_common_to_old = self.version_switch_cost(
                    self.current_version, shared_parent)
                cost_common_to_new = self.version_switch_cost(version,
                                                              shared_parent)
                cost_to_current_version = cost_common_to_old + \
                    cost_common_to_new
            else:
                cost_to_closest_version = 0
                cost_to_current_version = 1
            # FIXME I'm assuming copying the pipeline has zero cost.
            # Formulate a better cost model
            if cost_to_closest_version < cost_to_current_version:
                if closest == 0:
                    result = self.vistrail.getPipeline(version)
                else:
                    result = copy.copy(self._pipelines[closest])
                    action = self.vistrail.general_action_chain(closest,
                                                                version)
                    result.perform_action(action)
            else:
                action = \
                    self.vistrail.general_action_chain(self.current_version,
                                                       version)
                if self.current_version == -1 or self.current_version == 0:
                    result = Pipeline()
                else:
                    result = copy.copy(self.current_pipeline)
                result.perform_action(action)

            if self._cache_pipelines and self.get_tag(long(version)):
                # stash a copy for future use for tagged (and upgraded) pipelines
                if do_validate:
                    try:
                        self.validate(result)
                    except InvalidPipeline:
                        if not allow_fail:
                            raise
                    else:
                        self._pipelines[version] = copy.copy(result)
                else:
                    self._pipelines[version] = copy.copy(result)
        if do_validate:
            try:
                self.validate(result)
            except InvalidPipeline:
                if not allow_fail:
                    raise
        return result

    def get_tag(self, version_number):
        # Follow upgrades forward to find tag
        if not getattr(get_vistrails_configuration(),
                                        'hideUpgrades', True):
            return self.vistrail.getVersionName(version_number)
        tag = self.vistrail.search_upgrade_versions(
                version_number,
                lambda vt, v, bv: vt.getVersionName(v) or None) or ''
        return tag

    def get_tagged_version(self, version_number):
        # Follow upgrades forward to find tagged version
        if not getattr(get_vistrails_configuration(),
                                        'hideUpgrades', True):
            return version_number
        def is_tagged(vt, v):
            return v if vt.getVersionName(v) else None
        tagged_version = self.vistrail.search_upgrade_versions(
                version_number,
                lambda vt, v, bv: is_tagged(vt, v)) or version_number
        return tagged_version

    def get_notes(self, version_number):
        if not getattr(get_vistrails_configuration(),
                                        'hideUpgrades', True):
            return self.vistrail.get_notes(version_number)
        notes = self.vistrail.search_upgrade_versions(
            version_number,
            lambda vt, v, bv: vt.get_notes(v) or None)
        return notes

    def create_upgrade(self, version, delay_update=False):
        """Upgrade a version if needed

         Does not change current version, but will create a new upgrade if it
         does not exist.

        delay_update - set self.update_delayed and do not call set_changed in
                       handle_invalid_pipeline

        """
        try:
            self.get_pipeline(version)
        except InvalidPipeline as e:
            if version == self.current_version:
                # The upgrade is probably already done
                self.flush_delayed_actions(delay_update=delay_update)

            try:
                version, _ = self.validate_version(version,
                                                   delay_update=delay_update,
                                                   use_current=False)
            except InvalidPipeline as e:
                debug.unexpected_exception(e)
                # Get the version anyway
                version = e._version
        return version


import unittest

class TestTerseGraph(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pm = vistrails.core.packagemanager.get_package_manager()
        if pm.has_package('org.vistrails.test.upgrades_layout'):
            return

        d = {'test_upgrades_layout': 'vistrails.tests.resources.'}
        pm.late_enable_package('test_upgrades_layout', d)
        cls.maxDiff = None

    @classmethod
    def tearDownClass(cls):
        manager = vistrails.core.packagemanager.get_package_manager()
        if manager.has_package('org.vistrails.test.upgrades_layout'):
            manager.late_disable_package('test_upgrades_layout')

    def get_workflow(self, name):
        from vistrails.core.db.locator import XMLFileLocator
        from vistrails.core.system import vistrails_root_directory

        locator = XMLFileLocator(vistrails_root_directory() +
                                 '/tests/resources/' + name)
        vistrail = locator.load()
        return VistrailController(vistrail, locator)

    def test_workflow1_upgrades(self):
        """Computes the tersed version tree, with upgrades"""
        controller = self.get_workflow('upgrades1.xml')
        controller.recompute_terse_graph(True)
        self.assertEqual(controller._current_terse_graph.adjacency_list, {
            0: [(1L, (False, False)), (5L, (False, False)), (16L, (True, False))],
            1L: [(3L, (True, False))],
            3L: [(4L, (False, False))],
            5L: [(8L, (True, False)), (10L, (True, False))],
            10L: [(11L, (False, False)), (13L, (True, False))],
            4L: [], 8L: [], 11L: [], 13L: [], 16L: [],
        })
        controller.expand_all_versions_below(0)
        controller.recompute_terse_graph(True)
        self.assertEqual(controller._current_terse_graph.adjacency_list, {
            0: [(1L, (False, False)), (5L, (False, False)), (14L, (False, True))],
            1L: [(2L, (False, True))],
            2L: [(3L, (False, False))],
            3L: [(4L, (False, False))],
            5L: [(6L, (False, True)), (9L, (False, True))],
            6L: [(7L, (False, False))],
            7L: [(8L, (False, False))],
            9L: [(10L, (False, False))],
            10L: [(11L, (False, False)), (12L, (False, True))],
            12L: [(13L, (False, False))],
            14L: [(15L, (False, False))],
            15L: [(16L, (False, False))],
            4L: [], 8L: [], 11L: [], 13L: [], 16L: [],
        })

    def test_workflow1_no_upgrades(self):
        """Computes the tersed version tree, without upgrades"""
        controller = self.get_workflow('upgrades1.xml')
        controller.recompute_terse_graph(False)
        self.assertEqual(controller._current_terse_graph.adjacency_list, {
            0: [(1L, (False, False)), (5L, (False, False)), (14L, (False, False))],
            1L: [(3L, (False, False))],
            3L: [(4L, (False, False))],
            5L: [(8L, (False, False)), (9L, (False, False))],
            9L: [(11L, (False, False)), (13L, (False, False))],
            4L: [], 8L: [], 11L: [], 13L: [], 14L: [],
        })
        controller.expand_all_versions_below(0)
        controller.recompute_terse_graph(False)
        self.assertEqual(controller._current_terse_graph.adjacency_list, {
            0: [(1L, (False, False)), (5L, (False, False)), (14L, (False, False))],
            1L: [(3L, (False, False))],
            3L: [(4L, (False, False))],
            5L: [(8L, (False, False)), (9L, (False, False))],
            9L: [(11L, (False, False)), (13L, (False, False))],
            4L: [], 8L: [], 11L: [], 13L: [], 14L: [],
        })

    def test_workflow2_upgrades(self):
        """Computes the tersed version tree, with upgrades"""
        controller = self.get_workflow('upgrades2.xml')
        controller.recompute_terse_graph(True)
        self.assertEqual(controller._current_terse_graph.adjacency_list, {
            0: [(3L, (True, False)), (9L, (True, False)), (12L, (False, False))],
            3L: [(7L, (True, False)), (6L, (True, False))],
            9L: [(10L, (False, False)), (11L, (False, False))],
            12L: [(13L, (False, False)), (15L, (False, False))],
            13L: [(14L, (False, False)), (17L, (True, False))],
            7L: [], 6L: [], 10L: [], 11L: [], 14L: [], 15L: [], 17L: [],
        })
        controller.expand_all_versions_below(0)
        controller.recompute_terse_graph(True)
        self.assertEqual(controller._current_terse_graph.adjacency_list, {
            0: [(1L, (False, True)), (8L, (False, True)), (12L, ((False, False)))],
            1L: [(2L, (False, False))],
            2L: [(3L, (False, False))],
            3L: [(4L, (False, True)), (5L, (False, True))],
            4L: [(7L, (False, False))],
            5L: [(6L, (False, False))],
            8L: [(9L, (False, False))],
            9L: [(10L, (False, False)), (11L, (False, False))],
            12L: [(13L, (False, False)), (15L, (False, False))],
            13L: [(14L, (False, False)), (16L, (False, True))],
            16L: [(17L, (False, False))],
            7L: [], 6L: [], 10L: [], 11L: [], 14L: [], 15L: [], 17L: [],
        })

    def test_workflow2_no_upgrades(self):
        """Computes the tersed version tree, without upgrades"""
        controller = self.get_workflow('upgrades2.xml')
        controller.recompute_terse_graph(False)
        self.assertEqual(controller._current_terse_graph.adjacency_list, {
            0: [(2L, (True, False)), (9L, (True, False)), (13L, (True, False))],
            2L: [(4L, (False, False)), (6L, (True, False))],
            9L: [(10L, (False, False))],
            13L: [(14L, (False, False)), (17L, (False, False))],
            4L: [], 6L: [], 10L: [], 14L: [], 17L: [],
        })
        controller.expand_all_versions_below(0)
        controller.recompute_terse_graph(False)
        self.assertEqual(controller._current_terse_graph.adjacency_list, {
            0: [(1L, (False, True)), (8L, (False, True)), (12L, ((False, True)))],
            1L: [(2L, (False, False))],
            2L: [(4L, (False, False)), (5L, (False, True))],
            5L: [(6L, (False, False))],
            8L: [(9L, (False, False))],
            9L: [(10L, (False, False))],
            12L: [(13L, (False, False))],
            13L: [(14L, (False, False)), (17L, (False, False))],
            4L: [], 6L: [], 10L: [], 14L: [], 17L: [],
        })

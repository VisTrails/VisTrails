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
from PyQt4 import QtCore, QtGui
from core.common import *
from core.configuration import get_vistrails_configuration
import core.db.action
import core.db.locator
import core.modules.module_registry
import core.modules.vistrails_module
from core.data_structures.graph import Graph
from core.data_structures.point import Point
from core.utils import VistrailsInternalError, ModuleAlreadyExists
from core.log.controller import LogController, DummyLogController
from core.log.log import Log
from core.modules import module_registry
from core.modules.module_registry import ModuleRegistry
from core.modules.basic_modules import Variant
from core.modules.sub_module import InputPort, OutputPort, new_abstraction, \
    read_vistrail
from core.packagemanager import get_package_manager
from core.vistrail.action import Action
from core.query.version import TrueSearch
from core.query.visual import VisualQuery
from core.system import vistrails_default_file_type
from core.vistrail.abstraction import Abstraction
from core.vistrail.annotation import Annotation
from core.vistrail.connection import Connection
from core.vistrail.group import Group
from core.vistrail.location import Location
from core.vistrail.module import Module
from core.vistrail.module_function import ModuleFunction
from core.vistrail.module_param import ModuleParam
from core.vistrail.pipeline import Pipeline
from core.vistrail.port import Port, PortEndPoint
from core.vistrail.port_spec import PortSpec
from core.vistrail.vistrail import Vistrail, TagExists
from core.vistrails_tree_layout_lw import VistrailsTreeLayoutLW
from core.interpreter.default import get_default_interpreter
from core.inspector import PipelineInspector
from db.domain import IdScope
from db.services.vistrail import getSharedRoot
from gui.utils import show_warning, show_question, YES_BUTTON, NO_BUTTON
# Broken right now
# from core.modules.sub_module import addSubModule, DupplicateSubModule
import core.analogy
import copy
import os.path
import math
import uuid

################################################################################

class VistrailController(QtCore.QObject):
    """
    VistrailController is the class handling all action control in
    VisTrails. It updates pipeline, vistrail and emit signals to
    update the view

    Signals emitted:

    vistrailChanged(): emitted when the version tree needs to be
    recreated (for example, a node was added/deleted or the layout
    changed).

    flushMoveActions(): emitted as a request to commit move actions to
    the vistrail, typically prior to adding other actions to the
    vistrail.

    versionWasChanged(): emitted when the current version (the one
    being displayed by the pipeline view) has changed.

    searchChanged(): emitted when the search statement from the
    version view has changed.

    stateChanged(): stateChanged is called when a vistrail goes from
    unsaved to saved or vice-versa.
    
    notesChanged(): notesChanged is called when the version notes have
    been updated

    """

    def __init__(self, vis=None, auto_save=True, name=''):
        """ VistrailController(vis: Vistrail, name: str) -> VistrailController
        Create a controller for a vistrail.

        """
        QtCore.QObject.__init__(self)
        self.name = ''
        self.file_name = None
        self.set_file_name(name)
        self.vistrail = vis
        self.log = Log()
        self.current_session = -1
        if vis is not None:
            self.current_session = vis.idScope.getNewId('session')
            vis.current_session = self.current_session
            vis.log = self.log
        self.current_pipeline = None
        # FIXME: self.current_pipeline_view currently stores the SCENE, not the VIEW
        self.current_pipeline_view = None
        self.vistrail_view = None
        self.reset_pipeline_view = False
        self.reset_version_view = True
        self.quiet = False
        # if self.search is True, vistrail is currently being searched
        self.search = None
        self.search_str = None
        # If self.refine is True, search mismatches are hidden instead
        # of ghosted
        self.refine = False
        self.changed = False
        self.full_tree = False
        self.analogy = {}
        self.locator = None
        # if self._auto_save is True, an auto_saving timer will save a temporary
        # file every 2 minutes
        self._auto_save = auto_save
        self.timer = QtCore.QTimer(self)
        self.connect(self.timer, QtCore.SIGNAL("timeout()"), self.write_temporary)
        self.timer.start(1000 * 60 * 2) # Save every two minutes
        # if _cache_pipelines is True, cache pipelines to speed up
        # version switching
        self._cache_pipelines = True
        self._pipelines = {0: Pipeline()}

        self._current_terse_graph = None
        self._current_full_graph = None
        self._previous_graph_layout = None
        self._current_graph_layout = VistrailsTreeLayoutLW()
        self.animate_layout = False
        self.num_versions_always_shown = 5

    ##########################################################################
    # Signal vistrail relayout / redraw

    def replace_unnamed_node_in_version_tree(self, old_version, new_version):
        """method analogous to invalidate_version_tree but when only
        a single unnamed node and links need to be updated. Much faster."""
        self.reset_version_view = False
        try:
            self.emit(QtCore.SIGNAL('invalidateSingleNodeInVersionTree'),
                                    old_version, new_version)
        finally:
            self.reset_version_view = True

    def invalidate_version_tree(self, reset_version_view=True, animate_layout=False):
        """ invalidate_version_tree(reset_version_tree: bool, animate_layout: bool) -> None
        
        """
        self.reset_version_view = reset_version_view
        self.animate_layout = animate_layout
        #FIXME: in the future, rename the signal
        try:
            self.emit(QtCore.SIGNAL('vistrailChanged()'))
        finally:
            self.reset_version_view = True

    ##########################################################################
    # Autosave

    def enable_autosave(self):
        self._auto_save = True

    def disable_autosave(self):
        self._auto_save = False

    def get_logger(self):
        from gui.application import VistrailsApplication
        if VistrailsApplication.configuration.check('nologger'):
            return DummyLogController()
        else:
            return LogController(self.log)

    def get_locator(self):
        from gui.application import VistrailsApplication
        if (self._auto_save and 
            VistrailsApplication.configuration.check('autosave')):
            return self.locator or core.db.locator.untitled_locator()
        else:
            return None

    def cleanup(self):
        locator = self.get_locator()
        if locator:
            locator.clean_temporaries()
        self.disconnect(self.timer, QtCore.SIGNAL("timeout()"), self.write_temporary)
        self.timer.stop()

    def set_vistrail(self, vistrail, locator, abstractions=None):
        """ set_vistrail(vistrail: Vistrail, locator: VistrailLocator) -> None
        Start controlling a vistrail
        
        """
        self.vistrail = vistrail
        if self.vistrail is not None:
            self.current_session = self.vistrail.idScope.getNewId("session")
            self.vistrail.current_session = self.current_session
            self.vistrail.log = self.log
        if abstractions is not None:
            for abstraction_file in abstractions:
                self.load_abstraction(abstraction_file)
        self.current_version = -1
        self.current_pipeline = None
        if self.locator != locator and self.locator is not None:
            self.locator.clean_temporaries()
        self.locator = locator
        if locator != None:
            self.set_file_name(locator.name)
        else:
            self.set_file_name('')
        if locator and locator.has_temporaries():
            self.set_changed(True)
        self.recompute_terse_graph()

    def close_vistrail(self, locator):
        def process_abstractions(controller, vistrail):
            abstractions = []
            for action in vistrail.actions:
                for operation in action.operations:
                    if operation.vtType == 'add' or \
                            operation.vtType == 'change':
                        if operation.data.vtType == Abstraction.vtType:
                            abstraction = operation.data
                            if abstraction.package == 'local.abstractions' and \
                                    abstraction.namespace is not None:
                                controller.unload_abstraction( \
                                    abstraction.name,
                                    abstraction.namespace)
        process_abstractions(self, self.vistrail)
        if locator is not None:
            locator.close()

    ##########################################################################
    # Actions, etc
    
    def perform_action(self, action, quiet=None):
        """ performAction(action: Action, quiet=None) -> timestep

        performs given action on current pipeline.

        quiet and self.quiet control invalidation of version
        tree. If quiet is set to any value, it overrides the field
        value self.quiet.

        If the value is True, then no invalidation happens (gui is not
        updated.)
        
        """
        self.current_pipeline.perform_action(action)
        self.current_version = action.db_id
        
        if quiet is None:
            if not self.quiet:
                self.invalidate_version_tree(False)
        else:
            if not quiet:
                self.invalidate_version_tree(False)
        return action.db_id

    def add_new_action(self, action):
        """add_new_action(action) -> None

        Call this function to add a new action to the vistrail being
        controlled by the vistrailcontroller.

        FIXME: In the future, this function should watch the vistrail
        and get notified of the change.

        """
        self.vistrail.add_action(action, self.current_version, 
                                 self.current_session)
        self.set_changed(True)
        self.emit(QtCore.SIGNAL("new_action"), action)
        self.current_version = action.db_id
        self.recompute_terse_graph()

    ##########################################################################

    def add_module(self, x, y, identifier, name, namespace='', 
                   internal_version=-1):
        """ addModule(x: int, y: int, identifier, name: str, namespace='') 
               -> Module
        Add a new module into the current pipeline
        
        """
        self.emit(QtCore.SIGNAL("flushMoveActions()"))

        if not self.current_pipeline:
            raise Exception("No version is selected")
        
        loc_id = self.vistrail.idScope.getNewId(Location.vtType)
        location = Location(id=loc_id,
                            x=x, 
                            y=y,
                            )
        if internal_version > -1:
            abstraction_id = self.vistrail.idScope.getNewId(Abstraction.vtType)
            module = Abstraction(id=abstraction_id,
                                 name=name,
                                 package=identifier,
                                 location=location,
                                 namespace=namespace,
                                 internal_version=internal_version,
                                 )
        else:
            module_id = self.vistrail.idScope.getNewId(Module.vtType)
            module = Module(id=module_id,
                            name=name,
                            package=identifier,
                            location=location,
                            namespace=namespace,
                            )
        action = core.db.action.create_action([('add', module)])
        self.add_new_action(action)
        self.perform_action(action)
        return module
            
    def get_module_connection_ids(self, module_ids, graph):
        # FIXME should probably use a Set here
        connection_ids = {}
        for module_id in module_ids:
            for v, id in graph.edges_from(module_id):
                connection_ids[id] = 1
            for v, id in graph.edges_to(module_id):
                connection_ids[id] = 1
        return connection_ids.keys()

    def delete_module(self, module_id):
        """ delete_module(module_id: int) -> version id
        Delete a module from the current pipeline
        
        """
        return self.delete_module_list([module_id])

    def delete_module_list(self, module_ids):
        """ delete_module_list(module_ids: [int]) -> [version id]
        Delete multiple modules from the current pipeline
        
        """
        self.emit(QtCore.SIGNAL("flushMoveActions()"))

        graph = self.current_pipeline.graph
        connect_ids = self.get_module_connection_ids(module_ids, graph)
        action_list = []
        for c_id in connect_ids:
            action_list.append(('delete', 
                                self.current_pipeline.connections[c_id]))
        for m_id in module_ids:
            action_list.append(('delete',
                                self.current_pipeline.modules[m_id]))
        action = core.db.action.create_action(action_list)
        self.add_new_action(action)
        return self.perform_action(action)

    def move_module_list(self, move_list):
        """ move_module_list(move_list: [(id,x,y)]) -> [version id]        
        Move all modules to a new location. No flushMoveActions is
        allowed to to emit to avoid recursive actions
        
        """
        action_list = []
        for (id, x, y) in move_list:
            module = self.current_pipeline.get_module_by_id(id)
            loc_id = self.vistrail.idScope.getNewId(Location.vtType)
            location = Location(id=loc_id,
                                x=x, 
                                y=y,
                                )
            if module.location and module.location.id != -1:
                old_location = module.location
                action_list.append(('change', old_location, location,
                                    module.vtType, module.id))
            else:
                # probably should be an error
                action_list.append(('add', location, module.vtType, module.id))
        action = core.db.action.create_action(action_list)
        self.add_new_action(action)
        return self.perform_action(action)
            
    def add_connection(self, connection):
        """ add_connection(connection: Connection) -> version id
        Add a new connection 'connection' into Vistrail
        
        """
        self.emit(QtCore.SIGNAL("flushMoveActions()"))
        conn_id = self.vistrail.idScope.getNewId(Connection.vtType)
        connection.id = conn_id
        for port in connection.ports:
            port_id = self.vistrail.idScope.getNewId(Port.vtType)
            port.id = port_id
        action = core.db.action.create_action([('add', connection)])
        self.add_new_action(action)
        result = self.perform_action(action)
        self.current_pipeline.ensure_connection_specs([connection.id])
        return result
    
    def delete_connection(self, id):
        """ delete_connection(id: int) -> version id
        Delete a connection with id 'id'
        
        """
        return self.delete_connection_list([id])

    def delete_connection_list(self, connect_ids):
        """ delete_connection_list(connect_ids: list) -> version id
        Delete a list of connections
        
        """
        self.emit(QtCore.SIGNAL("flushMoveActions()"))
        
        action_list = []
        for c_id in connect_ids:
            action_list.append(('delete', 
                                self.current_pipeline.connections[c_id]))
        action = core.db.action.create_action(action_list)
        self.add_new_action(action)
        return self.perform_action(action)

    def delete_method(self, function_pos, module_id):
        """ delete_method(function_pos: int, module_id: int) -> version id
        Delete a method with function_pos from module module_id

        """
        self.emit(QtCore.SIGNAL("flushMoveActions()"))

        module = self.current_pipeline.get_module_by_id(module_id)
        function = module.functions[function_pos]
        action = core.db.action.create_action([('delete', function,
                                                    module.vtType, module.id)])
        self.add_new_action(action)
        return self.perform_action(action)

    def add_method(self, module_id, function):
        """ add_method(module_id: int, function: ModuleFunction) -> version_id
        Add a new method into the module's function list
        
        """
        self.emit(QtCore.SIGNAL("flushMoveActions()"))

        module = self.current_pipeline.get_module_by_id(module_id)
        function_id = self.vistrail.idScope.getNewId(ModuleFunction.vtType)
        function.real_id = function_id
        
        # We can only touch the parameters property once during this loop.
        # Otherwise, ModuleFunction._get_params will sort the list from
        # under us and change all the indices.
        params = function.parameters[:]
        
        for i in xrange(len(params)):
            param = params[i]
            param_id = self.vistrail.idScope.getNewId(ModuleParam.vtType)
            param.real_id = param_id
            param.pos = i
        action = core.db.action.create_action([('add', function,
                                                    Module.vtType, module.id)])
        self.add_new_action(action)
        return self.perform_action(action)
        
    def replace_method(self, module, function_pos, param_list):
        """ replace_method(module: Module, function_pos: int, param_list: list)
               -> version_id or None, if new parameter was equal to old one.
        Replaces parameters for a given function
        """
        self.emit(QtCore.SIGNAL("flushMoveActions()"))

        action_list = []
        must_change = False
        for i in xrange(len(param_list)):
            (p_val, p_type, p_namespace, p_identifier, p_alias) = param_list[i]
            function = module.functions[function_pos]
            old_param = function.params[i]
            param_id = self.vistrail.idScope.getNewId(ModuleParam.vtType)
            new_param = ModuleParam(id=param_id,
                                    pos=i,
                                    name='<no description>',
                                    alias=p_alias,
                                    val=p_val,
                                    type=p_type,
                                    identifier=p_identifier,
                                    namespace=p_namespace,
                                    )
            must_change |= (new_param != old_param)
            action_list.append(('change', old_param, new_param, 
                                function.vtType, function.real_id))
        if must_change:
            action = core.db.action.create_action(action_list)
            self.add_new_action(action)
            return self.perform_action(action)
        else:
            return None

    def delete_annotation(self, key, module_id):
        """ delete_annotation(key: str, module_id: long) -> version_id
        Deletes an annotation from a module
        
        """
        self.emit(QtCore.SIGNAL("flushMoveActions()"))

        module = self.current_pipeline.get_module_by_id(module_id)
        annotation = module.get_annotation_by_key(key)
        action = core.db.action.create_action([('delete', annotation,
                                                module.vtType, module.id)])
        self.add_new_action(action)
        return self.perform_action(action)

    def add_annotation(self, pair, module_id):
        """ add_annotation(pair: (str, str), moduleId: int)        
        Add/Update a key/value pair annotation into the module of
        moduleId
        
        """
        self.emit(QtCore.SIGNAL("flushMoveActions()"))

        assert type(pair[0]) == type('')
        assert type(pair[1]) == type('')
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
                core.db.action.create_action([('change', old_annotation,
                                                   annotation,
                                                   module.vtType, module.id)])
        else:
            action = core.db.action.create_action([('add', annotation,
                                                        module.vtType, 
                                                        module.id)])
        self.add_new_action(action)
        
        return self.perform_action(action)

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

    def add_module_port(self, module_id, port_tuple):
        """ add_module_port(module_id: int, port_tuple: (str, str, list)
        Parameters
        ----------
        
        - module_id : 'int'        
        - port_tuple : (portType, portName, portSpec)
        
        """
        self.emit(QtCore.SIGNAL("flushMoveActions()"))
        
        module = self.current_pipeline.get_module_by_id(module_id)
        p_id = self.vistrail.idScope.getNewId(PortSpec.vtType)
        port_spec = PortSpec(id=p_id,
                             type=port_tuple[0],
                             name=port_tuple[1],
                             spec=port_tuple[2],
                             )
        action = core.db.action.create_action([('add', port_spec,
                                                module.vtType, module.id)])
        
        self.add_new_action(action)
        return self.perform_action(action)

    def delete_module_port(self, module_id, port_tuple):
        """
        Parameters
        ----------
        
        - module_id : 'int'
        - port_tuple : (portType, portName, portSpec)
        
        """
        self.emit(QtCore.SIGNAL("flushMoveActions()"))

        spec_id = -1
        module = self.current_pipeline.get_module_by_id(module_id)
        port_spec = module.get_portSpec_by_name((port_tuple[1], port_tuple[0]))
        action_list = [('delete', port_spec, module.vtType, module.id)]
        for function in module.functions:
            if function.name == port_spec.name:
                action_list.append(('delete', function, 
                                    module.vtType, module.id))
        action = core.db.action.create_action(action_list)
        self.add_new_action(action)
        return self.perform_action(action)

    def update_notes(self, notes):
        """
        Parameters
        ----------

        - notes : 'QtCore.QString'
        
        """
        self.emit(QtCore.SIGNAL("flushMoveActions()"))
        
        if self.vistrail.change_notes(str(notes),self.current_version):
            self.set_changed(True)
            self.emit(QtCore.SIGNAL('notesChanged()'))

    def add_parameter_changes_from_execution(self, pipeline, version,
                                             parameter_changes):
        """add_parameter_changes_from_execution(pipeline, version,
        parameter_changes) -> int.

        Adds new versions to the current vistrail as a result of an
        execution. Returns the version number of the new version."""

        type_map = {float: 'Float',
                    int: 'Integer',
                    str: 'String',
                    bool: 'Boolean'}

        def convert_function_parameters(params):
            if (type(function_values) == tuple or
                type(function_values) == list):
                result = []
                for v in params:
                    result.extend(convert_function_parameters(v))
                return result
            else:
                t = type(function_values)
                assert t in type_map
                return [ModuleParam(type=type_map[t],
                                    val=str(function_values))]

        def add_aliases(m_id, f_index, params):
            function = pipeline.modules[m_id].functions[f_index]
            result = []
            for (index, param) in enumerate(params):
                result.append((param.strValue, param.type,
                               function.params[index].alias))
            return result

        for (m_id, function_name, function_values) in parameter_changes:
            params = convert_function_parameters(function_values)

            f_index = pipeline.find_method(m_id, function_name)
            if f_index == -1:
                new_method = ModuleFunction(name=function_name,
                                            parameters=params)
                self.add_method(m_id, new_method)
            else:
                params = add_aliases(m_id, f_index, params)
                self.replace_method(pipeline.modules[m_id],
                                    f_index,
                                    params)

    def execute_workflow_list(self, vistrails):
        if self.current_pipeline:
            locator = self.get_locator()
            if locator:
                locator.clean_temporaries()
                locator.save_temporary(self.vistrail)
        interpreter = get_default_interpreter()
        changed = False
        old_quiet = self.quiet
        self.quiet = True
        for vis in vistrails:
            (locator, version, pipeline, view) = vis
            kwargs = {'locator': locator,
                      'current_version': version,
                      'view': view,
                      'logger': self.get_logger(),
                      'controller': self,
                      }
            result = interpreter.execute(pipeline, **kwargs)
            if result.parameter_changes:
                l = result.parameter_changes
                self.add_parameter_changes_from_execution(pipeline,
                                                          version, l)
                changed = True
        self.quiet = old_quiet
        if changed:
            self.invalidate_version_tree(False)

    def execute_current_workflow(self):
        """ execute_current_workflow() -> None
        Execute the current workflow (if exists)
        
        """
        if self.current_pipeline:
            self.execute_workflow_list([(self.locator,
                                         self.current_version,
                                         self.current_pipeline,
                                         self.current_pipeline_view)])

    def change_selected_version(self, new_version):
        """ change_selected_version(new_version: int) -> None        
        Change the current vistrail version into new_version and emit a
        notification signal
        
        """

        # This is tricky code, so watch carefully before you change
        # it.  The biggest problem is that we want to perform state
        # changes only after all exceptions have been handled, but
        # creating a pipeline every time is too slow. The solution
        # then is to mutate currentPipeline, and in case exceptions
        # are thrown, we roll back by rebuilding the pipeline from
        # scratch as the first thing on the exception handler, so to
        # the rest of the exception handling code, things look
        # stateless.

        def get_cost(descendant, ancestor):
            cost = 0
            am = self.vistrail.actionMap
            while descendant <> ancestor:
                descendant = am[descendant].parent
                cost += 1
            return cost
        
        def switch_version():
            if not self.current_pipeline:
                result = self.vistrail.getPipeline(new_version)
            # now we reuse some existing pipeline, even if it's the
            # empty one for version zero
            #
            # The available pipelines are in self._pipelines, plus
            # the current pipeline.
            # Fast check: do we have to change anything?
            elif new_version == self.current_version:
                # we don't even need to check connection specs or
                # registry
                return self.current_pipeline
            # Fast check: if target is cached, copy it and we're done.
            elif new_version in self._pipelines:
                result = copy.copy(self._pipelines[new_version])
            else:
                # Find the closest upstream pipeline to the current one
                cv = self._current_full_graph.inverse_immutable().closest_vertex
                closest = cv(new_version,
                             self._pipelines)
                cost_closest_to_new_version = get_cost(new_version, closest)
                # Now we have to decide between the closest pipeline
                # to new_version and the current pipeline
                shared_parent = getSharedRoot(self.vistrail, [self.current_version,
                                                              new_version])
                cost_common_to_old = get_cost(self.current_version, shared_parent)
                cost_common_to_new_version = get_cost(new_version, shared_parent)
                # FIXME I'm assuming copying the pipeline has zero cost.
                # Formulate a better cost model
                if (cost_common_to_old + cost_common_to_new_version >
                    cost_closest_to_new_version):
                    if new_version == 0:
                        result = self.vistrail.getPipeline(new_version)
                    else:
                        result = copy.copy(self._pipelines[closest])
                        action = self.vistrail.general_action_chain(closest, new_version)
                        result.perform_action(action)
                else:
                    action = self.vistrail.general_action_chain(self.current_version,
                                                                new_version)
                    self.current_pipeline.perform_action(action)
                    result = self.current_pipeline
                if self._cache_pipelines and long(new_version) in self.vistrail.tagMap:
                    # stash a copy for future use
                    result.ensure_connection_specs()
                    self._pipelines[new_version] = copy.copy(result)
            result.ensure_connection_specs()
            result.ensure_modules_are_on_registry()
            return result
        
        # We assign to temporaries to avoid partial state changes
        # being hosed by an exception
        
        if new_version == -1:
            new_pipeline = None
        else:
            try:
                new_pipeline = switch_version()
            except ModuleRegistry.MissingModulePackage, e:
                # we need to rollback the current pipeline. This is
                # sort of slow, but we're going to present a dialog to
                # the user anyway, so we can get away with this
                
                # currentVersion might be -1 and so currentPipeline
                # will be None. We can't call getPipeline with -1
                if self.current_version != -1:
                    self.current_pipeline = self.vistrail.getPipeline(self.current_version)
                else:
                    assert self.current_pipeline is None
                
                from gui.application import VistrailsApplication
                # if package is present, then we first let the package know
                # that the module is missing - this might trigger
                # some new modules.
                pm = get_package_manager()
                try:
                    pkg = pm.get_package_by_identifier(e._identifier)
                    res = pkg.report_missing_module(e._name, e._namespace)
                    if not res:
                        msg = (('Cannot find module "%s" in\n' % e._name) +
                               ('loaded package "%s". A different package version\n' %
                                pkg.name) +
                               'might be necessary.')

                        QtGui.QMessageBox.critical(VistrailsApplication.builderWindow,
                                                   'Missing module in package',
                                                   msg)
                        return
                    else:
                        # package reported success in handling missing
                        # module, so we retry changing the version by
                        # recursing, since other packages/modules
                        # might still be needed.
                        return self.change_selected_version(new_version)
                except pm.MissingPackage:
                    pass

                # Ok, package is missing - let's see if user wants to
                # late-enable it.
                pkg = pm.identifier_is_available(e._identifier)
                if pkg:
                    res = show_question('Enable package?',
                                        "This pipeline contains a module in package '%s'."
                                        " Do you want to enable that package?"  % e._identifier,
                                        [YES_BUTTON, NO_BUTTON], YES_BUTTON)
                    if res == NO_BUTTON:
                        return
                    # Ok, user wants to late-enable it. Let's give it a shot
                    try:
                        pm.late_enable_package(pkg.codepath)
                    except pkg.InitializationFailed:
                        QtGui.QMessageBox.critical(VistrailsApplication.builderWindow,
                                                   'Package load failed',
                                                   'Package "%s" failed during initialization.'
                                                   ' Please contact the developer of that package'
                                                   ' and report a bug' % pkg.name)
                        return
                    except Exception, e:
                        msg = "Weird - this exception '%s' shouldn't have happened" % str(e)
                        raise VistrailsInternalError()
                        
                    # there's a new package in the system, so we retry
                    # changing the version by recursing, since other
                    # packages/modules might still be needed.
                    return self.change_selected_version(new_version)
                else:
                    QtGui.QMessageBox.critical(VistrailsApplication.builderWindow,
                                               'Unavailable package',
                                               'Cannot find package "%s" in\n'
                                               'list of available packages. \n'
                                               'Please install it first.' % e._identifier)
                    return
        # If execution arrives here, we handled all exceptions, so
        # assign values
        self.current_pipeline = new_pipeline
        self.current_version = new_version
        self.emit(QtCore.SIGNAL('versionWasChanged'), new_version)

    def set_search(self, search, text=''):
        """ set_search(search: SearchStmt, text: str) -> None
        Change the currrent version tree search statement
        
        """
        if self.search != search or self.search_str != text:
            self.search = search
            self.search_str = text
            if self.search:
                self.search.run(self.vistrail, '')
            if self.refine:
                # need to recompute the graph because the refined items might
                # have changed since last time
                self.recompute_terse_graph()
                self.invalidate_version_tree(True)
            else:
                self.invalidate_version_tree(False)
            
            self.emit(QtCore.SIGNAL('searchChanged'))

    def set_refine(self, refine):
        """ set_refine(refine: bool) -> None
        Set the refine state to True or False
        
        """
        if self.refine!=refine:
            self.refine = refine
            # need to recompute the graph because the refined items might
            # have changed since last time
            self.recompute_terse_graph()
            self.invalidate_version_tree(True)

    def set_full_tree(self, full):
        """ set_full_tree(full: bool) -> None        
        Set if Vistrails should show a complete version tree or just a
        terse tree
        
        """
        if full != self.full_tree:
            self.full_tree = full
            self.invalidate_version_tree(True)

    def recompute_terse_graph(self):
        # get full version tree (including pruned nodes)
        # this tree is kept updated all the time. This
        # data is read only and should not be updated!
        fullVersionTree = self.vistrail.tree.getVersionTree()

        # create tersed tree
        x = [(0,None)]
        tersedVersionTree = Graph()

        # cache actionMap and tagMap because they're properties, sort of slow
        am = self.vistrail.actionMap
        tm = self.vistrail.tagMap
        last_n = self.vistrail.getLastActions(self.num_versions_always_shown)

        while 1:
            try:
                (current,parent)=x.pop()
            except IndexError:
                break

            # mount childs list
            children = [to for (to, _) in fullVersionTree.adjacency_list[current]
                        if (to in am) and not am[to].prune]

            if (self.full_tree or 
                (current == 0) or  # is root
                (current in tm) or # hasTag:
                (len(children) <> 1) or # not oneChild:
                (current == self.current_version) or # isCurrentVersion
                (am[current].expand) or  # forced expansion
                (current in last_n)): # show latest
                # yes it will!
                # this needs to be here because if we are refining
                # version view receives the graph without the non
                # matching elements
                if( (not self.refine) or
                    (self.refine and not self.search) or
                    (current == 0) or
                    (self.refine and self.search and 
                     self.search.match(self.vistrail,am[current]) or
                     current == self.current_version)):
                    # add vertex...
                    tersedVersionTree.add_vertex(current)
                
                    # ...and the parent
                    if parent is not None:
                        tersedVersionTree.add_edge(parent,current,0)

                    # update the parent info that will 
                    # be used by the childs of this node
                    parentToChildren = current
                else:
                    parentToChildren = parent
            else:
                parentToChildren = parent

            for child in reversed(children):
                x.append((child, parentToChildren))

        self._current_terse_graph = tersedVersionTree
        self._current_full_graph = self.vistrail.tree.getVersionTree()
        self._previous_graph_layout = copy.deepcopy(self._current_graph_layout)
        self._current_graph_layout.layout_from(self.vistrail, 
                                               self._current_terse_graph)

    def refine_graph(self, step=1.0):
        """ refine_graph(step: float in [0,1]) -> (Graph, Graph)        
        Refine the graph of the current vistrail based the search
        status of the controller. It also return the full graph as a
        reference
        
        """
        if not self.animate_layout:
            return (self._current_terse_graph, self._current_full_graph,
                    self._current_graph_layout)

        graph_layout = copy.deepcopy(self._current_graph_layout)
        terse_graph = copy.deepcopy(self._current_terse_graph)
        am = self.vistrail.actionMap
        step = 1.0/(1.0+math.exp(-(step*12-6))) # use a logistic sigmoid function
        
        # Adding nodes to tree
        for (c_id, c_node) in self._current_graph_layout.nodes.iteritems():
            if self._previous_graph_layout.nodes.has_key(c_id):
                p_node = self._previous_graph_layout.nodes[c_id]
            else: 
                p_id = c_id
                # Find closest child of contained in both graphs
                while not self._previous_graph_layout.nodes.has_key(p_id):
                    # Should always have exactly one child
                    p_id = [to for (to, _) in self._current_full_graph.adjacency_list[p_id]
                            if (to in am) and not am[to].prune][0]
                p_node = self._previous_graph_layout.nodes[p_id]

            # Interpolate position
            x = p_node.p.x - c_node.p.x
            y = p_node.p.y - c_node.p.y
            graph_layout.move_node(c_id, x*(1.0-step), y*(1.0-step))
            
        # Removing nodes from tree
        for (p_id, p_node) in self._previous_graph_layout.nodes.iteritems():
            if not self._current_graph_layout.nodes.has_key(p_id):
                # Find closest parent contained in both graphs
                shared_parent = p_id
                while shared_parent > 0 and not self._current_graph_layout.nodes.has_key(shared_parent):
                    shared_parent = self._current_full_graph.parent(shared_parent)

                # Find closest child contained in both graphs
                c_id = p_id
                while not self._current_graph_layout.nodes.has_key(c_id):
                    # Should always have exactly one child
                    c_id = [to for (to, _) in self._current_full_graph.adjacency_list[c_id]
                        if (to in am) and not am[to].prune][0]

                # Don't show edge that skips the disappearing nodes
                if terse_graph.has_edge(shared_parent, c_id):
                    terse_graph.delete_edge(shared_parent, c_id)

                # Add the disappearing node to the graph and layout
                c_node = copy.deepcopy(self._current_graph_layout.nodes[c_id])
                c_node.id = p_id
                graph_layout.add_node(p_id, c_node)
                terse_graph.add_vertex(p_id)
                p_parent = self._current_full_graph.parent(p_id)
                if not terse_graph.has_edge(p_id, p_parent):
                    terse_graph.add_edge(p_parent, p_id)
                p_child = [to for (to, _) in self._current_full_graph.adjacency_list[p_id]
                           if (to in am) and not am[to].prune][0]
                if not terse_graph.has_edge(p_id, p_child):
                    terse_graph.add_edge(p_id, p_child)

                # Interpolate position
                x = p_node.p.x - c_node.p.x
                y = p_node.p.y - c_node.p.y
                graph_layout.move_node(p_id, x*(1.0-step), y*(1.0-step))

        return (terse_graph, self._current_full_graph,
                graph_layout)

    ##########################################################################
    # undo/redo navigation

    def _change_version_short_hop(self, new_version):
        """_change_version_short_hop is used internally to
        change versions when we're moving exactly one action up or down.
        This allows a few optimizations that improve interactivity."""
        
        if self.current_version <> new_version:
            # Instead of recomputing the terse graph, simply update it

            # There are two variables in play:
            # a) whether or not the destination node is currently on the
            # terse tree (it will certainly be after the move)
            # b) whether or not the current node will be visible (it
            # certainly is now, since it's the current one)

            dest_node_in_terse_tree = new_version in self._current_terse_graph.vertices
            
            current = self.current_version
            tree = self.vistrail.tree.getVersionTree()
            # same logic as recompute_terse_graph except for current
            children_count = len([x for (x, _) in tree.adjacency_list[current]
                                  if (x in self.vistrail.actionMap and
                                      not self.vistrail.actionMap[x].prune)])
            current_node_will_be_visible = \
                (self.full_tree or
                 (self.current_version in self.vistrail.tagMap) or
                 children_count <> 1)

            self.change_selected_version(new_version)
            # case 1:
            if not dest_node_in_terse_tree and not current_node_will_be_visible:
                # we're going from one boring node to another,
                # so just rename the node on the terse graph
                self._current_terse_graph.rename_vertex(current, new_version)
                self.replace_unnamed_node_in_version_tree(current, new_version)
            else:
                # bail, for now
                self.recompute_terse_graph()
                self.invalidate_version_tree(False)
        

    def show_parent_version(self):
        """ show_parent_version() -> None
        Go back one from the current version and display it

        """
        # NOTE cscheid: Slight change in the logic under refined views:
        # before r1185, undo would back up more than one action in the
        # presence of non-matching refined nodes. That seems wrong. Undo
        # should always move one step only.         

        prev = None
        try:
            prev = self._current_full_graph.parent(self.current_version)
        except full.CalledParentOnSourceVertex:
            prev = 0

        self._change_version_short_hop(prev)

    def show_child_version(self, which_child):
        """ show_child_version(which_child: int) -> None
        Go forward one version and display it. This is used in redo.

        ONLY CALL THIS FUNCTION IF which_child IS A CHILD OF self.current_version

        """
        self._change_version_short_hop(which_child)
        

    def prune_versions(self, versions):
        """ prune_versions(versions: list of version numbers) -> None
        Prune all versions in 'versions' out of the view
        
        """
        # We need to go up-stream to the highest invisible node
        current = self.vistrail.currentGraph
        if not current:
            (current, full, layout) = self.refine_graph()
        else:
            full = self.vistrail.getVersionGraph()
        changed = False
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
                self.vistrail.pruneVersion(highest)
        if changed:
            self.set_changed(True)
        self.recompute_terse_graph()
        self.invalidate_version_tree(False)

    def hide_versions_below(self, v):
        """ hide_versions_below(v: int) -> None
        Hide all versions including and below v
        
        """
        full = self.vistrail.getVersionGraph()
        x = [v]

        am = self.vistrail.actionMap
        tm = self.vistrail.tagMap

        changed = False

        while 1:
            try:
                current=x.pop()
            except IndexError:
                break

            children = [to for (to, _) in full.adjacency_list[current]
                        if (to in am) and not am[to].prune]
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
        full = self.vistrail.getVersionGraph()
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
        changed = False
        p = full.parent(v2)
        while p>v1:
            self.vistrail.expandVersion(p)
            changed = True
            p = full.parent(p)
        if changed:
            self.set_changed(True)
        self.recompute_terse_graph()
        self.invalidate_version_tree(False, True)

    def collapse_versions(self, v):
        """ collapse_versions(v: int) -> None
        Collapse all versions including and under version v until the next tag or branch
        
        """
        full = self.vistrail.getVersionGraph()
        x = [v]

        am = self.vistrail.actionMap
        tm = self.vistrail.tagMap

        changed = False

        while 1:
            try:
                current=x.pop()
            except IndexError:
                break

            children = [to for (to, _) in full.adjacency_list[current]
                        if (to in am) and not am[to].prune]
            if len(children) > 1:
                break;
            self.vistrail.collapseVersion(current)
            changed = True

            for child in children:
                if (not child in tm and  # has no Tag
                    child != self.current_version): # not selected
                    x.append(child)

        if changed:
            self.set_changed(True)
        self.recompute_terse_graph()
        self.invalidate_version_tree(False, True) 

    def expand_or_collapse_all_versions_below(self, v, expand=True):
        """ expand_or_collapse_all_versions_below(v: int) -> None
        Expand/Collapse all versions including and under version v
        
        """
        full = self.vistrail.getVersionGraph()
        x = [v]
        
        am = self.vistrail.actionMap
        tm = self.vistrail.tagMap

        changed = False

        while 1:
            try:
                current=x.pop()
            except IndexError:
                break

            children = [to for (to, _) in full.adjacency_list[current]
                        if (to in am) and not am[to].prune]
            if expand:
                self.vistrail.expandVersion(current)
            else:
                self.vistrail.collapseVersion(current)
            changed = True

            for child in children:
                x.append(child)

        if changed:
            self.set_changed(True)
        self.recompute_terse_graph()
        self.invalidate_version_tree(False, True) 

    def collapse_all_versions(self):
        """ collapse_all_versions() -> None
        Collapse all expanded versions

        """
        am = self.vistrail.actionMap
        for a in am.iterkeys():
            self.vistrail.collapseVersion(a)
        self.set_changed(True)
        self.recompute_terse_graph()
        self.invalidate_version_tree(False, True)

    def set_num_versions_always_shown(self, num):
        """ set_num_versions_always_shown(num: int) -> None

        """
        if num <> self.num_versions_always_shown:
            self.num_versions_always_shown = num
            self.set_changed(True)
            self.recompute_terse_graph()
            self.invalidate_version_tree(False)

    def select_latest_version(self):
        """ select_latest_version() -> None
        Try to select the latest visible version on the tree
        
        """
        current = self.vistrail.currentGraph
        if not current:
            (current, full, layout) = self.refine_graph()        
        self.change_selected_version(max(current.iter_vertices()))

    def setSavedQueries(self, queries):
        """ setSavedQueries(queries: list of (str, str, str)) -> None
        Set the saved queries of a vistail
        
        """
        self.vistrail.setSavedQueries(queries)
        self.set_changed(True)
        

    def update_module_tag(self, module, tag):
        """ update_module_tag(module: Module, tag: str) -> None
        Updates the current module's tag
        
        """
        self.emit(QtCore.SIGNAL("flushMoveActions()"))
        if module.vtType == 'module':
            self.vistrail.update_object(module, db_tag=tag)
        elif module.vtType == 'abstraction':
            self.vistrail.update_object(module, db_name=tag)
        
    def update_current_tag(self,tag):
        """ update_current_tag(tag: str) -> Bool
        Update the current vistrail tag and return success predicate
        
        """
        self.emit(QtCore.SIGNAL("flushMoveActions()"))
        try:
            if self.vistrail.hasTag(self.current_version):
                self.vistrail.changeTag(tag, self.current_version)
            else:
                self.vistrail.addTag(tag, self.current_version)
        except TagExists:
            show_warning('Name Exists',
                         "There is already another version named '%s'.\n"
                         "Please enter a different one." % tag)
            return False
        self.set_changed(True)
        self.recompute_terse_graph()
        self.invalidate_version_tree(False)
        return True

    def perform_param_changes(self, actions):
        """perform_param_changes(actions) -> None

        Performs a series of parameter change actions to the current version.

        FIXME: this function seems to be called from a single place in
        the spreadsheet cell code. Do we need it?
        """
        if len(actions) == 0:
            return
        for action in actions:
            for operation in action.operations:
                if operation.vtType == 'add' or operation.vtType == 'change':
                    if operation.new_obj_id < 0:
                        data = operation.data
                        new_id = self.vistrail.idScope.getNewId(data.vtType)
                        data.real_id = new_id
                        operation.new_obj_id = new_id
            self.add_new_action(action)
            self.perform_action(action, quiet=True)
        self.set_changed(True)
        self.invalidate_version_tree(False)

    ################################################################################
    # Clipboard, copy/paste

    def copy_modules_and_connections(self, module_ids, connection_ids):
        """copy_modules_and_connections(module_ids: [long],
                                     connection_ids: [long]) -> str
        Serializes a list of modules and connections
        """
        self.emit(QtCore.SIGNAL("flushMoveActions()"))

        pipeline = Pipeline()
        sum_x = 0.0
        sum_y = 0.0
        for module_id in module_ids:
            module = self.current_pipeline.modules[module_id]
            sum_x += module.location.x
            sum_y += module.location.y
        center_x = sum_x / len(module_ids)
        center_y = sum_y / len(module_ids)
        for module_id in module_ids:
            module = self.current_pipeline.modules[module_id]
            module = module.do_copy()
            module.location.x -= center_x
            module.location.y -= center_y
            pipeline.add_module(module)
        for connection_id in connection_ids:
            connection = self.current_pipeline.connections[connection_id]
            pipeline.add_connection(connection)
        return core.db.io.serialize(pipeline)
        
    def paste_modules_and_connections(self, str, center):
        """ paste_modules_and_connections(str,
                                          center: (float, float)) -> [id list]
        Paste a list of modules and connections into the current pipeline.

        Returns the list of module ids of added modules

        """
        self.emit(QtCore.SIGNAL("flushMoveActions()"))

        pipeline = core.db.io.unserialize(str, Pipeline)
        modules = []
        connections = []
        if pipeline:
            for module in pipeline.module_list:
                module.location.x += center[0]
                module.location.y += center[1]
            id_remap = {}
            action = core.db.action.create_paste_action(pipeline, 
                                                        self.vistrail.idScope,
                                                        id_remap)

            modules = [op.objectId
                       for op in action.operations
                       if (op.what == 'module' or 
                           op.what == 'abstraction' or
                           op.what == 'group')]
            connections = [op.objectId
                           for op in action.operations
                           if op.what == 'connection']
                
            self.add_new_action(action)
            self.vistrail.change_description("Paste", action.id)
            self.perform_action(action)
            self.current_pipeline.ensure_connection_specs(connections)
        return modules

    ##########################################################################
    # Grouping/abstraction

    def create_subpipeline(self, module_ids, connection_ids, id_remap,
                           id_scope=None):
        if not id_scope:
            id_scope = IdScope(1, {Group.vtType: Module.vtType,
                                   Abstraction.vtType: Module.vtType})
        
        pipeline = Pipeline()
        pipeline.id = None # get rid of id so that sql saves correctly

        sum_x = 0.0
        sum_y = 0.0
        
        abs_modules = []
        abs_connections = []
        changed_ports = []

        del_action_list = []
        for module_id in module_ids:
            module = self.current_pipeline.modules[module_id]
            del_action_list.append(('delete', module))
            sum_x += module.location.x
            sum_y += module.location.y
            tmp_remap = {}
            new_module = module.do_copy(True, id_scope, tmp_remap)

            # hack to make sure that we don't adds ids from group.pipeline
            if module.vtType == Group.vtType or \
                    module.vtType == Abstraction.vtType:
                id_remap[(Module.vtType, module_id)] = new_module.id
            else:
                id_remap.update(tmp_remap)
            pipeline.add_module(new_module)

        # set
        avg_x = sum_x / len(module_ids)
        avg_y = sum_y / len(module_ids)
        for module in pipeline.module_list:
            module.location.x -= avg_x
            module.location.y -= avg_y

        in_names = {}
        out_names = {}
        name_remap = {}
        for connection_id in connection_ids:
            connection = self.current_pipeline.connections[connection_id]
            all_inside = True
            all_outside = True
            for port in connection.ports:
                if not (Module.vtType, port.moduleId) in id_remap:
                    all_inside = False
                else:
                    all_outside = False

            # if a connection has an "external" connection, we need to
            # create an input port or output port module
            new_ports = []
            if not all_inside and not all_outside:
                for port in connection.ports:
                    if not (Module.vtType, port.moduleId) in id_remap:
                        loc_id = id_scope.getNewId(Location.vtType)
                        # FIXME get better location
                        # should use location of current attached module
                        location = Location(id=loc_id,
                                            x=0.0,
                                            y=0.0,
                                            )
                        if port.endPoint == PortEndPoint.Source:
                            port_klass = Variant
                            port_type = InputPort.__name__
                            port_specStr = connection.destination.specStr
                            base_name = connection.destination.name
                            names = in_names
                        elif port.endPoint == PortEndPoint.Destination:
                            port_klass = core.modules.vistrails_module.Module
                            port_type = OutputPort.__name__
                            port_specStr = connection.source.specStr
                            base_name = connection.source.name
                            names = out_names
                        if base_name in names:
                            port_name = base_name + '_' + str(names[base_name])
                            names[base_name] += 1
                        else:
                            port_name = base_name
                            names[base_name] = 2
                        name_remap[connection.id] = port_name

                        param_id = id_scope.getNewId(ModuleParam.vtType)
                        param = ModuleParam(id=param_id,
                                            pos=0,
                                            type='String',
                                            val=port_name)
                        function_id = id_scope.getNewId(ModuleFunction.vtType)
                        function_1 = ModuleFunction(id=function_id,
                                                  name='name',
                                                  parameters=[param])

                        param_id = id_scope.getNewId(ModuleParam.vtType)
                        param = ModuleParam(id=param_id,
                                            pos=0,
                                            type='String',
                                            val=port_specStr)

                        function_id = id_scope.getNewId(ModuleFunction.vtType)
                        function_2 = ModuleFunction(id=function_id,
                                                  name='spec',
                                                  parameters=[param])

                        param_id = id_scope.getNewId(ModuleParam.vtType)
                        param = ModuleParam(id=param_id,
                                            pos=0,
                                            type='String',
                                            val=base_name)

                        function_id = id_scope.getNewId(ModuleFunction.vtType)
                        function_3 = ModuleFunction(id=function_id,
                                                  name='old_name',
                                                  parameters=[param])

                        functions = [function_1, function_2, function_3]
                        # if port.endPoint == PortEndPoint.Source:
                        #     functions.append(function_3)

                        # FIXME package name should not be hard-coded
                        new_id = id_scope.getNewId(Module.vtType)
                        module = Module(id=new_id,
                                        name=port_type,
                                        package='edu.utah.sci.vistrails.basic',
                                        location=location,
                                        functions=functions
                                        )

#                         module = self.create_submodule(port, name_remap, 
#                                                        in_names, out_names)  
                        pipeline.add_module(module, id_remap)
                        spec_str = '(edu.sci.utah.vistrails.basic:%s)' % \
                            port_type
                        port_id = id_scope.getNewId(Port.vtType)
                        new_port = Port(id=port_id,
                                        type=port.type,
                                        moduleId=module.id,
                                        moduleName=port_type,
                                        name='InternalPipe')
                        new_port.spec = \
                            core.modules.module_registry.PortSpec(port_klass)
                        new_ports.append(new_port)  
                    else:
                        changed_ports.append((port, connection))
            new_connection = connection.do_copy(True, id_scope, id_remap)

            for port in new_ports:
                if port.endPoint == PortEndPoint.Source:
                    new_connection.source = port
                elif port.endPoint == PortEndPoint.Destination:
                    new_connection.destination = port
            # action_list.append(('add', new_connection))
            pipeline.add_connection(new_connection)

            # assume that we don't have len(new_ports) >= 2
            if len(new_ports) <= 1:
                # connection inside abstraction
                del_action_list.append(('delete', connection))                
            # else a change port -- done later
        return (pipeline, del_action_list, changed_ports, name_remap,
                (avg_x, avg_y))

    def update_connections_to_subpipeline(self, changed_ports, module_id,
                                          module_name, id_remap, name_remap):
        add_action_list = []
        for (old_port, connection) in changed_ports:
            new_connection = connection.do_copy(True, self.vistrail.idScope, 
                                                id_remap)
            port_id = self.vistrail.idScope.getNewId(Port.vtType)
            changed_port = Port(id=port_id,
                                type=old_port.type,
                                moduleId=module_id,
                                moduleName=module_name,
                                name=name_remap[connection.id])
            changed_port.specStr = old_port.specStr
            changed_port.spec = old_port.spec

            if old_port.type == 'source':
                new_connection.source = changed_port
            else:
                new_connection.destination = changed_port
            add_action_list.append(('add', new_connection))
        return add_action_list

    def create_group(self, module_ids, connection_ids):
        self.emit(QtCore.SIGNAL("flushMoveActions()"))

        id_remap = {}
        (pipeline, del_action_list, changed_ports, name_remap, loc) = \
            self.create_subpipeline(module_ids, connection_ids, id_remap)

        # now group to vistrail
        loc_id = self.vistrail.idScope.getNewId(Location.vtType)
        location = Location(id=loc_id,
                            x=loc[0],
                            y=loc[1],
                            )
        group_id = self.vistrail.idScope.getNewId(Group.vtType)
        group = Group(id=group_id, 
                      name='Group', 
                      package='edu.utah.sci.vistrails.basic', 
                      location=location, 
                      pipeline=pipeline)

        del_action_list.reverse()
        add_action_list = []
        add_action_list.append(('add', group))
        
        more_actions = self.update_connections_to_subpipeline(changed_ports,
                                                              group.id,
                                                              group.name,
                                                              id_remap,
                                                              name_remap)
        add_action_list.extend(more_actions)
        # print 'add_actions:'
        # for a in add_action_list:
        #     print a
        # print 'del actions:'
        # for a in del_action_list:
        #     print a
        action = core.db.action.create_action(add_action_list + del_action_list)
        # Commenting out this as old_obj_id does not exist anymore
        #for op in action.db_operations:
            #print op.vtType, op.what, op.old_obj_id, op.new_obj_id
        self.add_new_action(action)
        self.perform_action(action)

        # FIXME we shouldn't have to return a module
        # we don't do it for any other type
        # doesn't match documentation either
        return group

    def create_abstraction_with_prompt(self, module_ids, connection_ids, 
                                       name=""):
        name = self.get_abstraction_name(name)
        if name is None:
            return
        return self.create_abstraction(module_ids, connection_ids, name)

    def create_abstraction(self, module_ids, connection_ids, name):
        self.emit(QtCore.SIGNAL("flushMoveActions()"))

        if self.abstraction_exists(name):
            raise VistrailsInternalError("Abstraction '%s' already exists" % \
                                             name)
        id_remap = {}
        (pipeline, del_action_list, changed_ports, name_remap, loc) = \
            self.create_subpipeline(module_ids, connection_ids, id_remap)
        
        # save vistrail
        abs_vistrail = self.create_vistrail_from_pipeline(pipeline)
        abs_vistrail.name = name
        abs_vistrail.change_description("Copied from pipeline", 1L)
        abs_fname = self.save_abstraction(abs_vistrail)

        # need to late enable stuff on the 'local.abstractions' package
        self.add_abstraction(abs_vistrail, abs_fname, name)

        # now group to vistrail
        loc_id = self.vistrail.idScope.getNewId(Location.vtType)
        location = Location(id=loc_id,
                            x=loc[0],
                            y=loc[1],
                            )
        abstraction_id = self.vistrail.idScope.getNewId(Abstraction.vtType)
        abstraction = Abstraction(id=abstraction_id,
                                  name=name, 
                                  package='local.abstractions',
                                  internal_version=1L,
                                  location=location,
                                  )
            
        del_action_list.reverse()
        add_action_list = [('add', abstraction)]
        more_actions = self.update_connections_to_subpipeline(changed_ports,
                                                              abstraction.id,
                                                              abstraction.name,
                                                              id_remap,
                                                              name_remap)
        add_action_list.extend(more_actions)
#         for action in add_action_list:
#             print action
        action = core.db.action.create_action(add_action_list + del_action_list)
        self.add_new_action(action)
        self.perform_action(action)
        return abstraction

    def ungroup_set(self, module_ids):
        for m_id in module_ids:
            self.ungroup(m_id)

    def ungroup(self, module_id):
        self.emit(QtCore.SIGNAL("flushMoveActions()"))

        group = self.current_pipeline.modules[module_id]
        if group.vtType == Group.vtType:
            pipeline = group.pipeline
        elif group.vtType == Abstraction.vtType:
            pipeline = group.summon().pipeline
        else:
            print 'not a group or abstraction?'
            return
      
        pipeline.ensure_connection_specs()

        id_remap = {}
        add_action_list = []
        del_action_list = []
        for module in pipeline.module_list:
            if module.name != InputPort.__name__ and \
                    module.name != OutputPort.__name__:
                new_module = module.do_copy(True, self.vistrail.idScope, 
                                            id_remap)
                new_module.location.x += group.location.x
                new_module.location.y += group.location.y
                add_action_list.append(('add', new_module))

        in_conns = {}
        out_conns = {}
        for connection in pipeline.connection_list:
            all_inside = True
            all_outside = True
            for port in connection.ports:
                if (Module.vtType, port.moduleId) not in id_remap:
                    all_inside = False
                else:
                    all_outside = False
            
            if not all_inside and not all_outside:
                source = connection.source
                dest = connection.destination
                def get_port_info(m_id):
                    module = pipeline.modules[m_id]
                    for function in module.functions:
                        port_old_name = None
                        if function.name == 'name':
                            port_name = function.params[0].strValue
                        elif function.name == 'spec':
                            port_spec = function.params[0].strValue
                        elif function.name == 'old_name':
                            port_old_name = function.params[0].strValue
                    return (port_name, port_spec, port_old_name)

                if (Module.vtType, source.moduleId) not in id_remap:
                    (port_name, port_spec, port_old_name) = \
                        get_port_info(source.moduleId)
                    in_conns[(port_name, port_spec)] = connection

                    for function in group.functions:
                        if function.name == port_name:
                            target_module = pipeline.modules[dest.moduleId]
                            new_function = \
                                function.do_copy(True, self.vistrail.idScope, 
                                                 id_remap)
                            if port_old_name is None:
                                print "ERROR old_name is None"
                            new_function.name = port_old_name
                            target_module.add_function(new_function)

                elif (Module.vtType, dest.moduleId) not in id_remap:
                    (port_name, port_spec, port_old_name) = \
                        get_port_info(dest.moduleId)
                    out_conns[(port_name, port_spec)] = connection
            else:
                new_connection = connection.do_copy(True, 
                                                    self.vistrail.idScope, 
                                                    id_remap)
                add_action_list.append(('add', new_connection))
                
        
        for connection in self.current_pipeline.connection_list:
            source = connection.source
            dest = connection.dest
            rewire = False
            for port in connection.ports:
                if port.moduleId == group.id:
                    # need to rewire
                    rewire = True
                    if port.endPoint == PortEndPoint.Source:
                        key = (source.name, source.specStr)
                        if key not in out_conns:
                            print "ERROR: key not in out_conns"
                        old_connection = out_conns[key]
                        source = old_connection.source
                        source = source.do_copy(True, self.vistrail.idScope, 
                                                id_remap)
                        d_map = {}
                        dest = dest.do_copy(True, self.vistrail.idScope, d_map)
                    elif port.endPoint == PortEndPoint.Destination:
                        key = (dest.name, dest.specStr)
                        if key not in in_conns:
                            print "ERROR: key not in in_conns"
                        old_connection = in_conns[key]
                        dest = old_connection.destination
                        dest = dest.do_copy(True, self.vistrail.idScope,
                                            id_remap)
                        s_map = {}
                        source = \
                            source.do_copy(True, self.vistrail.idScope, s_map)
            if rewire:
                new_id = self.vistrail.idScope.getNewId(Connection.vtType)
                new_connection = Connection(id=new_id,
                                            ports=[source, dest])
                add_action_list.append(('add', new_connection))
                del_action_list.append(('delete', connection))
                          
        del_action_list.append(('delete', group))
        action = core.db.action.create_action(add_action_list + del_action_list)
        # Commenting out this as old_obj_id does not exist anymore
#         for op in action.db_operations:
#             print op.vtType, op.what, op.old_obj_id, op.new_obj_id
        self.add_new_action(action)
        self.perform_action(action)

    def abstraction_exists(self, name, namespace=None):
        reg = core.modules.module_registry.registry
        return reg.has_descriptor_with_name('local.abstractions', name,
                                            namespace)
#         conf = get_vistrails_configuration()
#         if conf.check('userPackageDirectory'):
#             abstraction_dir = os.path.join(conf.userPackageDirectory,
#                                            'abstractions')
#             if not os.path.exists(abstraction_dir):
#                 raise VistrailsInternalError("Cannot find %s" % \
#                                                  abstraction_dir)
#             vt_fname = os.path.join(abstraction_dir, fname + '.vt')
#             if os.path.exists(vt_fname):
#                 return True
#         else:
#             raise VistrailsInternalError("Cannot find userPackageDirectory")
#         return False

    def save_abstraction(self, vistrail, name=None):
        #FIXME use a core call to save this instead of db.services.io?
        import db.services.io
            
        if name is None:
            name = vistrail.name
        if self.abstraction_exists(name):
            raise VistrailsInternalError("Abstraction with name '%s' already "
                                         "exists" % name)
        if vistrail.get_annotation('__abstraction_uuid__') is None:            
            abstraction_uuid = uuid.uuid1()
            vistrail.set_annotation('__abstraction_uuid__', abstraction_uuid)

        conf = get_vistrails_configuration()
        if conf.check('userPackageDirectory'):
            abstraction_dir = os.path.join(conf.userPackageDirectory,
                                           'abstractions')
            if not os.path.exists(abstraction_dir):
                raise VistrailsInternalError("Cannot find %s" % \
                                                 abstraction_dir)
            vt_fname = os.path.join(abstraction_dir, name + '.xml')
            if os.path.exists(vt_fname):
                raise VistrailsInternalError("'%s' already exists" % \
                                                 vt_fname)
            db.services.io.save_vistrail_to_xml(vistrail, vt_fname)
            return vt_fname
        return None

    def get_abstraction_descriptor(self, name, namespace=None):
        reg = core.modules.module_registry.registry
        return reg.get_descriptor_by_name('local.abstractions', name, namespace)

    def load_abstraction(self, abs_fname, abs_name=None):
        if abs_name is None:
            abs_name = os.path.basename(abs_fname)[12:-4]
        abs_vistrail = read_vistrail(abs_fname)
        abstraction_uuid = \
            abs_vistrail.get_annotation('__abstraction_uuid__').value
        if self.abstraction_exists(abs_name):
            descriptor = self.get_abstraction_descriptor(abs_name)
            if descriptor.module.uuid == abstraction_uuid:
                return
        if self.abstraction_exists(abs_name, abstraction_uuid):
            descriptor = \
                self.get_abstraction_descriptor(abs_name, abstraction_uuid)
            descriptor.abstraction_refs += 1
            # print 'load ref_count:', descriptor.abstraction_refs
            return
            
        self.add_abstraction(abs_vistrail, abs_fname, abs_name, 
                             abstraction_uuid)
            
    def unload_abstraction(self, name, namespace):
        if self.abstraction_exists(name, namespace):
            descriptor = self.get_abstraction_descriptor(name, namespace)
            descriptor.abstraction_refs -= 1
            # print 'unload ref_count:', descriptor.abstraction_refs
            if descriptor.abstraction_refs < 1:
                # unload abstraction
                print "deleting module:", name, namespace
                reg = core.modules.module_registry.registry
                reg.delete_module('local.abstractions', name, namespace)

    def add_abstraction(self, abs_vistrail, abs_fname, name, 
                        namespace=None): 
        reg = core.modules.module_registry.registry
        abstraction = new_abstraction(name, abs_vistrail, reg, abs_fname)
        reg.auto_add_module((abstraction, {'package': 'local.abstractions',
                                           'namespace': namespace,
                                           }))

    def import_abstractions(self, abstraction_ids):
        for abstraction_id in abstraction_ids:
            abstraction = self.current_pipeline.modules[abstraction_id]
            self.import_abstraction(abstraction.name, abstraction.namespace)
        
    def import_abstraction(self, name, namespace):
        # copy from a local namespace to local.abstractions
        reg = core.modules.module_registry.registry
        if namespace is None:
            # can't import an abstraction that already lives in 
            # local.abstractions
            return
        new_name = self.get_abstraction_name(name)
        if new_name is None:
            return
        if not self.abstraction_exists(name, namespace):
            raise VistrailsInternalError("Abstraction %s|%s not on registry" %\
                                             (name, namespace))
        descriptor = self.get_abstraction_descriptor(name, namespace)
        abs_fname = descriptor.module.vt_fname
        abs_vistrail = descriptor.module.vistrail
        abs_fname = self.save_abstraction(abs_vistrail, new_name)
        self.add_abstraction(abs_vistrail, abs_fname, new_name)
        
    def get_abstraction_name(self, name=""):
        name = self.do_abstraction_prompt(name)
        if name is None:
            return None
        while name == "" or self.abstraction_exists(name):
            name = self.do_abstraction_prompt(name, True)
            if name is None:
                return None
        return name

    def do_abstraction_prompt(self, name="", exists=False):
        if exists:
            prompt = "'%s' already exists.  Enter a new abstraction name" % \
                name
        else:
            prompt = 'Enter abstraction name'
            
        (text, ok) = QtGui.QInputDialog.getText(None, 
                                                'Set Abstraction Name',
                                                prompt,
                                                QtGui.QLineEdit.Normal,
                                                name)
        if ok and not text.isEmpty():
            return str(text).strip().rstrip()
        if not ok:
            return None
        return ""

    def create_vistrail_from_pipeline(self, pipeline):
        abs_vistrail = Vistrail()
        
        id_remap = {}
        action = core.db.action.create_paste_action(pipeline, 
                                                    abs_vistrail.idScope,
                                                    id_remap)
        abs_vistrail.add_action(action, 0L, 0)
        return abs_vistrail

    def create_abstractions_from_groups(self, group_ids):
        for group_id in group_ids:
            self.create_abstraction_from_group(group_id)

    def create_abstraction_from_group(self, group_id, name=""):
        name = self.get_abstraction_name(name)
        if name is None:
            return
        group = self.current_pipeline.modules[group_id]
        abs_vistrail = self.create_vistrail_from_pipeline(group.pipeline)
        abs_vistrail.name = name
        abs_vistrail.change_description("Created from group", 1L)
        abs_fname = self.save_abstraction(abs_vistrail)

        # need to late enable stuff on the 'local.abstractions' package
        self.add_abstraction(abs_vistrail, abs_fname, name)
        
        a_remap = {}
        new_location = group.location.do_copy(True, self.vistrail.idScope,
                                              a_remap)

        abstraction_id = self.vistrail.idScope.getNewId(Abstraction.vtType)
        abstraction = Abstraction(id=abstraction_id,
                                  name=name, 
                                  package='local.abstractions',
                                  internal_version=1L,
                                  location=new_location,
                                  )

        action_list = [('add', abstraction)]
        a_remap = {(Module.vtType, group_id): abstraction_id}
        graph = self.current_pipeline.graph
        connect_ids = self.get_module_connection_ids([group_id], graph)
        for c_id in connect_ids:
            connection = self.current_pipeline.connections[c_id]
            action_list.append(('delete', connection))
            new_ports = []
            for port in connection.ports:
                port = port.do_copy(True, self.vistrail.idScope, 
                                    a_remap)
#                 if port.moduleId == group_id:
#                     port.moduleId = abstraction.id
                new_ports.append(port)
            connection_id = self.vistrail.idScope.getNewId(Connection.vtType)
            action_list.append(('add', Connection(id=connection_id,
                                                  ports=new_ports)))
        action_list.append(('delete', group))
            
        action = core.db.action.create_action(action_list)
        self.add_new_action(action)
        self.perform_action(action)
        return abstraction

    def set_changed(self, changed):
        """ set_changed(changed: bool) -> None
        Set the current state of changed and emit signal accordingly
        
        """
        if changed!=self.changed:
            self.changed = changed
        # FIXME: emit different signal in the future
        self.emit(QtCore.SIGNAL('stateChanged'))

    def set_file_name(self, file_name):
        """ set_file_name(file_name: str) -> None
        Change the controller file name
        
        """
        if file_name == None:
            file_name = ''
        if self.file_name!=file_name:
            self.file_name = file_name
            self.name = os.path.split(file_name)[1]
            if self.name=='':
                self.name = 'untitled%s'%vistrails_default_file_type()
            self.emit(QtCore.SIGNAL('stateChanged'))

    def check_alias(self, name):
        """check_alias(alias) -> Boolean 
        Returns True if current pipeline has an alias named name """
        # FIXME Why isn't this call on the pipeline?
        return self.current_pipeline.has_alias(name)

    def write_temporary(self):
        if self.vistrail and self.changed:
            locator = self.get_locator()
            if locator:
                locator.save_temporary(self.vistrail)

    def write_vistrail(self, locator):
        def process_abstractions(vistrail):
            reg = core.modules.module_registry.registry
            abstractions = []
            for action in vistrail.actions:
                for operation in action.operations:
                    if operation.vtType == 'add' or \
                            operation.vtType == 'change':
                        if operation.data.vtType == Abstraction.vtType:
                            abstraction = operation.data
                            if abstraction.package == 'local.abstractions':
                                getter = reg.get_descriptor_by_name
                                descriptor = getter(abstraction.package,
                                                    abstraction.name)
                                abstraction.namespace = \
                                    descriptor.module.uuid
                                abs_fname = descriptor.module.vt_fname
                                abstractions.append(abs_fname)
            return abstractions

        if self.vistrail and (self.changed or self.locator != locator):
            # FIXME make all locators work with lists of objects
            objs = [(Vistrail.vtType, self.vistrail)]
            if self.log and len(self.log.workflow_execs) > 0:
                objs.append((Log.vtType, self.log))
            abstractions = process_abstractions(self.vistrail)
            for abs_fname in abstractions:
                objs.append(('__file__', abs_fname))
            # FIXME hack to use db_currentVersion for convenience
            # it's not an actual field
            self.vistrail.db_currentVersion = self.current_version
            if self.locator != locator:
                old_locator = self.get_locator()
                self.locator = locator
                # new_vistrail = self.locator.save_as(self.vistrail)
                objs = self.locator.save_as(objs)
                new_vistrail = objs[0][1]
                self.set_file_name(locator.name)
                if old_locator:
                    old_locator.clean_temporaries()
            else:
                # new_vistrail = self.locator.save(self.vistrail)
                objs = self.locator.save(objs)
                new_vistrail = objs[0][1]
            if id(self.vistrail) != id(new_vistrail):
                new_version = new_vistrail.db_currentVersion
                self.set_vistrail(new_vistrail, locator)
                self.change_selected_version(new_version)
                self.invalidate_version_tree(False)
            self.set_changed(False)

    def write_workflow(self, locator):
        if self.current_pipeline:
            pipeline = Pipeline()
            pipeline.set_abstraction_map(self.vistrail.abstractionMap)
            for module in self.current_pipeline.modules.itervalues():
                if module.vtType == AbstractionModule.vtType:
                    abstraction = \
                        pipeline.abstraction_map[module.abstraction_id]
                    pipeline.add_abstraction(abstraction)
                pipeline.add_module(module)
            for connection in self.current_pipeline.connections.itervalues():
                pipeline.add_connection(connection)            
            locator.save_as(pipeline)

    def write_expanded_workflow(self, locator):
        if self.current_pipeline:
            (workflow, _) = core.db.io.expand_workflow(self.vistrail, 
                                                       self.current_pipeline)
            locator.save_as(workflow)
        
    
    def write_log(self, locator):
        if self.log:
            locator.save_as(self.log)

    def query_by_example(self, pipeline):
        """ query_by_example(pipeline: Pipeline) -> None
        Perform visual query on the current vistrail
        
        """
        if len(pipeline.modules)==0:
            search = TrueSearch()
        else:
            search = VisualQuery(pipeline)

        self.set_search(search, '') # pipeline.dump_to_string())

    def addSubModule(self, moduleName, packageName, vistrail,
                     fileName, version, inspector):
        """ addSubModule(moduleName: str,
                         packageName: str,
                         vistrail: Vistrail,
                         fileName: str,
                         version: int,
                         inspector: PipelineInspector) -> SubModule
        Wrap sub_module.addSubModule to show GUI dialogs
        
        """
        raise VistrailsInternalError("Currently broken")
        # try:
        #     return addSubModule(moduleName, packageName, vistrail, fileName,
        #                         version, inspector)
        # except ModuleAlreadyExists:
        #     show_warning('Module Exists',
        #                  "Failed to registered '%s' as a module "
        #                  "because there is already another module with "
        #                  "the same name. Please change the version name "
        #                  "and manually add it later." % moduleName)
        # except DupplicateSubModule:
        #     show_warning('Module Exists',
        #                  "Failed to registered '%s' as a module "
        #                  "because it is already registered." % moduleName)

    def inspectAndImportModules(self):
        """ inspectAndImportModules() -> None        
        Go through all named pipelines and ask user to import them
        
        """

        # Currently broken
        pass
        # importModule = False
        # inspector = PipelineInspector()
        # for version in sorted(self.vistrail.inverseTagMap.keys()):
        #     tag = self.vistrail.inverseTagMap[version]
        #     if tag!='':
        #         pipeline = self.vistrail.getPipeline(version)
        #         inspector.inspect(pipeline)
        #         if inspector.is_sub_module():
        #             if importModule==False:
        #                 res = show_question('Import Modules',
        #                                     "'%s' contains importable modules. "
        #                                     "Do you want to import all of them?"
        #                                     % self.name,
        #                                     [YES_BUTTON, NO_BUTTON], YES_BUTTON)
        #                 if res==YES_BUTTON:
        #                     importModule = True
        #                 else:
        #                     return
        #             if importModule:
        #                 self.addSubModule(tag, self.name, self.vistrail,
        #                                   self.fileName, version,
        #                                   inspector)

    # def create_abstraction(self, subgraph):
    #     self.vistrail.create_abstraction(self.current_version,
    #                                      subgraph,
    #                                      'FOOBAR')

    ##########################################################################
    # analogies

    def add_analogy(self, analogy_name, version_from, version_to):
        assert type(analogy_name) == str
        assert type(version_from) == int or type(version_from) == long
        assert type(version_to) == int or type(version_to) == long
        if analogy_name in self.analogy:
            raise VistrailsInternalError("duplicated analogy name '%s'" %
                                         analogy_name)
        self.analogy[analogy_name] = (version_from, version_to)

    def remove_analogy(self, analogy_name):
        if analogy_name not in self.analogy:
            raise VistrailsInternalError("missing analogy '%s'" %
                                         analogy_name)
        del self.analogy[analogy_name]

    def perform_analogy(self, analogy_name, analogy_target):
        if analogy_name not in self.analogy:
            raise VistrailsInternalError("missing analogy '%s'" %
                                         analogy_name)
        (a, b) = self.analogy[analogy_name]
        c = analogy_target
        action = core.analogy.perform_analogy_on_vistrail(self.vistrail,
                                                          a, b, c)
        self.add_new_action(action)
        self.vistrail.change_description("Analogy", action.id)
        self.vistrail.change_analogy_info("(%s -> %s)(%s)" % (a, b, c), 
                                          action.id)
        self.perform_action(action)
        
        # this is not necessary anymore
        #self.set_changed(True)
        #if invalidate:
            #self.invalidate_version_tree(False)

################################################################################
# Testing

import unittest
import gui.utils
import api
import os

class TestVistrailController(gui.utils.TestVisTrailsGUI):

    # def test_add_module(self):
    #     v = api.new_vistrail()
       

    def test_abstraction_create(self):
        from core.db.locator import XMLFileLocator
        import core.db.io
        from core.configuration import get_vistrails_configuration
        v = XMLFileLocator(core.system.vistrails_root_directory() +
                           '/tests/resources/test_abstraction.xml').load()

        controller = VistrailController(v, False)
        pipeline = v.getPipeline(9L)
        controller.current_pipeline = pipeline
        controller.current_version = 9L
        
        module_ids = [1, 2, 3]
        connection_ids = [1, 2, 3]
        
        controller.create_abstraction(module_ids, connection_ids, 
                                      '__TestFloatList')
        config = get_vistrails_configuration()
        os.remove(os.path.join(config.abstractionsDirectory, 
                               '__TestFloatList.xml'))
 

        

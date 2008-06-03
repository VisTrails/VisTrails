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
import core.db.action
import core.db.locator
import core.modules.module_registry
import core.modules.vistrails_module
from core.data_structures.point import Point
from core.utils import VistrailsInternalError, ModuleAlreadyExists
from core.log.controller import LogController, DummyLogController
from core.log.log import Log
from core.modules import module_registry
from core.modules.module_registry import ModuleRegistry
from core.modules.basic_modules import Variant
from core.modules.sub_module import InputPort, OutputPort
from core.vistrail.action import Action
from core.query.version import TrueSearch
from core.query.visual import VisualQuery
from core.system import vistrails_default_file_type
from core.vistrail.abstraction import Abstraction
from core.vistrail.abstraction_module import AbstractionModule
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
from core.vistrail.vistrail import TagExists
from core.interpreter.default import get_default_interpreter
from core.inspector import PipelineInspector
from db.domain import IdScope
from gui.utils import show_warning, show_question, YES_BUTTON, NO_BUTTON
# Broken right now
# from core.modules.sub_module import addSubModule, DupplicateSubModule
import core.analogy
import copy
import os.path

################################################################################

class VistrailController(QtCore.QObject):
    """
    VistrailController is the class handling all action control in
    VisTrails. It updates pipeline, vistrail and emit signals to
    update the view
    
    """

    def __init__(self, vis=None, auto_save=True, name=''):
        """ VistrailController(vis: Vistrail, name: str) -> VistrailController
        Create a controller from vis

        """
        QtCore.QObject.__init__(self)
        self.name = ''
        self.fileName = None
        self.setFileName(name)
        self.vistrail = vis
        self.log = Log()
        self.currentVersion = -1
        self.currentPipeline = None
        self.currentPipelineView = None
        self.vistrailView = None
        self.resetPipelineView = False
        self.resetVersionView = True
        self.quiet = False
        self.search = None
        self.searchStr = None
        self.refine = False
        self.changed = False
        self.fullTree = False
        self.analogy = {}
        self._auto_save = auto_save
        self.locator = None
        self.timer = QtCore.QTimer(self)
        self.connect(self.timer, QtCore.SIGNAL("timeout()"), self.write_temporary)
        self.timer.start(1000 * 60 * 2) # Save every two minutes

    def invalidate_version_tree(self):
        #FIXME: in the future, rename the signal
        self.emit(QtCore.SIGNAL('vistrailChanged()'))

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

    def setVistrail(self, vistrail, locator):
        """ setVistrail(vistrail: Vistrail, locator: VistrailLocator) -> None
        Start controlling a vistrail
        
        """
        self.vistrail = vistrail
        self.currentVersion = -1
        self.currentPipeline = None
        if self.locator != locator and self.locator is not None:
            self.locator.clean_temporaries()
        self.locator = locator
        if locator != None:
            self.setFileName(locator.name)
        else:
            self.setFileName('')
        if locator and locator.has_temporaries():
            self.setChanged(True)
            
    def perform_action(self, action, quiet=None):
        """ performAction(action: Action, quiet=None) -> timestep
        Add version to vistrail, updates the current pipeline, and the
        rest of the UI know a new pipeline is selected.

        quiet and self.quiet controlds invalidation of version
        tree. If quiet is set to any value, it overrides the field
        value self.quiet.

        If the value is True, then no invalidation happens (gui is not
        updated.)
        
        """
        self.currentPipeline.perform_action(action)
        self.currentVersion = action.db_id
        self.setChanged(True)
        
        if quiet is None:
            if not self.quiet:
                self.invalidate_version_tree()
        else:
            if not quiet:
                self.invalidate_version_tree()
        return action.db_id

    def add_module(self, identifier, name, x, y, namespace=''):
        """ addModule(identifier, name: str, x: int, y: int, namespace='') -> version id
        Add a new module into the current pipeline
        
        """
        self.emit(QtCore.SIGNAL("flushMoveActions()"))

        if self.currentPipeline:
            loc_id = self.vistrail.idScope.getNewId(Location.vtType)
            location = Location(id=loc_id,
                                x=x, 
                                y=y,
                                )
            module_id = self.vistrail.idScope.getNewId(Module.vtType)
            module = Module(id=module_id,
                            name=name,
                            package=identifier,
                            location=location,
                            namespace=namespace,
                            )
            action = core.db.action.create_action([('add', module)])
            self.vistrail.add_action(action, self.currentVersion)
            self.perform_action(action)

            # FIXME we shouldn't have to return a module
            # we don't do it for any other type
            # doesn't match documentation either
            return module
        else:
            return None
            
    def get_module_connection_ids(self, module_ids, graph):
        # FIXME should probably use a Set here
        connection_ids = {}
        for module_id in module_ids:
            for v, id in graph.edges_from(module_id):
                connection_ids[id] = 1
            for v, id in graph.edges_to(module_id):
                connection_ids[id] = 1
        return connection_ids.keys()

    def deleteModule(self, module_id):
        """ deleteModule(module_id: int) -> version id
        Delete a module from the current pipeline
        
        """
        return self.deleteModuleList([module_id])

    def deleteModuleList(self, module_ids):
        """ deleteModule(module_ids: [int]) -> [version id]
        Delete multiple modules from the current pipeline
        
        """
        self.emit(QtCore.SIGNAL("flushMoveActions()"))

        graph = self.currentPipeline.graph
        connect_ids = self.get_module_connection_ids(module_ids, graph)
        action_list = []
        for c_id in connect_ids:
            action_list.append(('delete', 
                                self.currentPipeline.connections[c_id]))
        for m_id in module_ids:
            action_list.append(('delete',
                                self.currentPipeline.modules[m_id]))
        action = core.db.action.create_action(action_list)
        self.vistrail.add_action(action, self.currentVersion)
        return self.perform_action(action)

    def moveModuleList(self, move_list):
        """ moveModuleList(move_list: [(id,x,y)]) -> [version id]        
        Move all modules to a new location. No flushMoveActions is
        allowed to to emit to avoid recursive actions
        
        """
        action_list = []
        for (id, x, y) in move_list:
            module = self.currentPipeline.get_module_by_id(id)
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
        self.vistrail.add_action(action, self.currentVersion)
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
        self.vistrail.add_action(action, self.currentVersion)
        result = self.perform_action(action)
        self.currentPipeline.ensure_connection_specs([connection.id])
        return result
    
    def deleteConnection(self, id):
        """ deleteConnection(id: int) -> version id
        Delete a connection with id 'id'
        
        """
        return self.deleteConnectionList([id])

    def deleteConnectionList(self, connect_ids):
        """ deleteConnections(connect_ids: list) -> version id
        Delete a list of connections
        
        """
        self.emit(QtCore.SIGNAL("flushMoveActions()"))
        
        action_list = []
        for c_id in connect_ids:
            action_list.append(('delete', 
                                self.currentPipeline.connections[c_id]))
        action = core.db.action.create_action(action_list)
        self.vistrail.add_action(action, self.currentVersion)
        return self.perform_action(action)

    def deleteMethod(self, function_pos, module_id):
        """ deleteMethod(function_pos: int, module_id: int) -> version id
        Delete a method with function_pos from module module_id

        """
        self.emit(QtCore.SIGNAL("flushMoveActions()"))

        module = self.currentPipeline.get_module_by_id(module_id)
        function = module.functions[function_pos]
        action = core.db.action.create_action([('delete', function,
                                                    module.vtType, module.id)])
        self.vistrail.add_action(action, self.currentVersion)
        return self.perform_action(action)

    def addMethod(self, module_id, function):
        """ addMethod(module_id: int, function: ModuleFunction) -> version_id
        Add a new method into the module's function list
        
        """
        self.emit(QtCore.SIGNAL("flushMoveActions()"))

        module = self.currentPipeline.get_module_by_id(module_id)
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
        self.vistrail.add_action(action, self.currentVersion)
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
            self.vistrail.add_action(action, self.currentVersion)
            return self.perform_action(action)
        else:
            return None

    def deleteAnnotation(self, key, module_id):
        """ deleteAnnotation(key: str, module_id: long) -> version_id
        Deletes an annotation from a module
        
        """
        self.emit(QtCore.SIGNAL("flushMoveActions()"))

        module = self.currentPipeline.get_module_by_id(module_id)
        annotation = module.get_annotation_by_key(key)
        action = core.db.action.create_action([('delete', annotation,
                                                module.vtType, module.id)])
        self.vistrail.add_action(action, self.currentVersion)
        return self.perform_action(action)

    def addAnnotation(self, pair, module_id):
        """ addAnnotation(pair: (str, str), moduleId: int)        
        Add/Update a key/value pair annotation into the module of
        moduleId
        
        """
        self.emit(QtCore.SIGNAL("flushMoveActions()"))

        assert type(pair[0]) == type('')
        assert type(pair[1]) == type('')
        if pair[0].strip()=='':
            return

        module = self.currentPipeline.get_module_by_id(module_id)
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
        self.vistrail.add_action(action, self.currentVersion)
        
        return self.perform_action(action)

    def hasModulePort(self, module_id, port_tuple):
        """ hasModulePort(module_id: int, port_tuple: (str, str)): bool
        Parameters
        ----------
        
        - module_id : 'int'        
        - port_tuple : (portType, portName)

        Returns true if there exists a module port in this module with given params

        """
        (type, name) = port_tuple
        module = self.currentPipeline.get_module_by_id(module_id)
        return len([x for x in module.db_portSpecs
                    if x.name == name and x.type == type]) > 0

    def addModulePort(self, module_id, port_tuple):
        """ addModulePort(module_id: int, port_tuple: (str, str, list)
        Parameters
        ----------
        
        - module_id : 'int'        
        - port_tuple : (portType, portName, portSpec)
        
        """
        self.emit(QtCore.SIGNAL("flushMoveActions()"))
        
        module = self.currentPipeline.get_module_by_id(module_id)
        p_id = self.vistrail.idScope.getNewId(PortSpec.vtType)
        port_spec = PortSpec(id=p_id,
                             type=port_tuple[0],
                             name=port_tuple[1],
                             spec=port_tuple[2],
                             )
        action = core.db.action.create_action([('add', port_spec,
                                                module.vtType, module.id)])
        
        self.vistrail.add_action(action, self.currentVersion)
        return self.perform_action(action)

    def deleteModulePort(self, module_id, port_tuple):
        """
        Parameters
        ----------
        
        - module_id : 'int'
        - port_tuple : (portType, portName, portSpec)
        
        """
        self.emit(QtCore.SIGNAL("flushMoveActions()"))

        spec_id = -1
        module = self.currentPipeline.get_module_by_id(module_id)
        port_spec = module.get_portSpec_by_name((port_tuple[1], port_tuple[0]))
        action_list = [('delete', port_spec, module.vtType, module.id)]
        for function in module.functions:
            if function.name == port_spec.name:
                action_list.append(('delete', function, 
                                    module.vtType, module.id))
        action = core.db.action.create_action(action_list)
        self.vistrail.add_action(action, self.currentVersion)
        return self.perform_action(action)

    def updateNotes(self,notes):
        """
        Parameters
        ----------

        - notes : 'QtCore.QString'
        
        """
        self.emit(QtCore.SIGNAL("flushMoveActions()"))
        
        if self.vistrail.change_notes(str(notes),self.currentVersion):
            self.setChanged(True)

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
                self.addMethod(m_id, new_method)
            else:
                params = add_aliases(m_id, f_index, params)
                self.replace_method(pipeline.modules[m_id],
                                    f_index,
                                    params)

    def executeWorkflowList(self, vistrails):
        if self.currentPipeline:
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
            result = interpreter.execute(self, pipeline, locator, version, view,
                                         logger=self.get_logger())
            if result.parameter_changes:
                l = result.parameter_changes
                self.add_parameter_changes_from_execution(pipeline,
                                                          version, l)
                changed = True
        self.quiet = old_quiet
        if changed:
            self.invalidate_version_tree()

    def executeCurrentWorkflow(self):
        """ executeCurrentWorkflow() -> None
        Execute the current workflow (if exists)
        
        """
        if self.currentPipeline:
            self.executeWorkflowList([(self.locator,
                                       self.currentVersion,
                                       self.currentPipeline,
                                       self.currentPipelineView)])

    def changeSelectedVersion(self, newVersion):
        """ changeSelectedVersion(newVersion: int) -> None        
        Change the current vistrail version into newVersion and emit a
        notification signal
        
        """
        self.currentVersion = newVersion
        if newVersion>=0:
            try:
                self.currentPipeline = self.vistrail.getPipeline(newVersion)
                self.currentPipeline.ensure_connection_specs()
            except ModuleRegistry.MissingModulePackage, e:
                from gui.application import VistrailsApplication
                QtGui.QMessageBox.critical(VistrailsApplication.builderWindow,
                                           'Missing package',
                                           (('Cannot find module "%s" in \n' % e._name) +
                                             ('package "%s". Make sure package is \n' % e._identifier) +
                                             'enabled in the Preferences dialog.'))
                self.currentPipeline = None
                self.currentVersion = 0
        else:
            self.currentPipeline = None
        self.emit(QtCore.SIGNAL('versionWasChanged'), newVersion)
            
    def resendVersionWasChanged(self):
        """ resendVersionWasChanged() -> None
        Resubmit the notification signal of the current vistrail version
        
        """
        self.emit(QtCore.SIGNAL("flushMoveActions()"))
        self.resetPipelineView = False
        self.emit(QtCore.SIGNAL('versionWasChanged'), self.currentVersion)

    def setSearch(self, search, text=''):
        """ setSearch(search: SearchStmt, text: str) -> None
        Change the currrent version tree search statement
        
        """
        if self.search != search or self.searchStr != text:
            self.search = search
            self.searchStr = text
            if self.search:
                self.search.run(self.vistrail, '')
            self.invalidate_version_tree()
            self.emit(QtCore.SIGNAL('searchChanged'))

    def setRefine(self, refine):
        """ setRefine(refine: bool) -> None
        Set the refine state to True or False
        
        """
        if self.refine!=refine:
            self.refine = refine
            if self.refine:
                self.selectLatestVersion()
            self.invalidate_version_tree()

    def setFullTree(self, full):
        """ setFullTree(full: bool) -> None        
        Set if Vistrails should show a complete version tree or just a
        terse tree
        
        """
        self.fullTree = full
        self.invalidate_version_tree()

    def refineGraph(self):
        """ refineGraph(controller: VistrailController) -> (Graph, Graph)        
        Refine the graph of the current vistrail based the search
        status of the controller. It also return the full graph as a
        reference
        
        """
        # get full version tree (including pruned nodes)
        # this tree is kept updated all the time. This
        # data is read only and should not be updated!
        fullVersionTree = self.vistrail.tree.getVersionTree()

        # create tersed tree
        x = [(0,None)]
        from core.data_structures.graph import Graph
        tersedVersionTree = Graph()
        while len(x):
            (current,parent)=x.pop()

            # print "processing %d"  % (current)
            
            # is root
            isRoot = (current == 0)

            # mount childs list
            childs = []
            for (to,froom) in fullVersionTree.edges_from(current):

                # if it is not a pruned child add it 
                # to be childs list
                if self.vistrail.actionMap.has_key(to) and not self.vistrail.actionMap[to].prune:
                    # print "add child %5d -> %5d" % (current, to)
                    childs.append(to)

            # some properties of the current node
            hasTag = not isRoot and self.vistrail.tagMap.has_key(current)
            oneChild = len(childs) == 1
            isCurrentVersion = (current == self.currentVersion)
            
            # include this node in the tersed tree?
            include = False
            if self.fullTree:
                include = True
            elif isRoot:
                include = True
            elif hasTag:
                include = True
            elif not oneChild:
                include = True # include leaves and branch nodes
            elif isCurrentVersion:
                include = True

            if include:
                # yes it will!

                # add vertex...
                tersedVersionTree.add_vertex(current)
                
                # ...and the parent
                if parent != None:
                    tersedVersionTree.add_edge(parent,current,0)

            # update the parent info that will 
            # be used by the childs of this node
            parentToChilds = parent
            if include:
                parentToChilds = current

            # add childs to the processing list
            for i in xrange(len(childs)-1,-1,-1): #child in childs:
                child = childs[i]
                x.append((child,parentToChilds))

        return (tersedVersionTree, self.vistrail.tree.getVersionTree())

    # FIXME: remove this function (left here only for transition)
    def refineGraphOld(self):
        """ refineGraph(controller: VistrailController) -> (Graph, Graph)        
        Refine the graph of the current vistrail based the search
        status of the controller. It also return the full graph as a
        reference
        
        """
        if self.fullTree:
            terse = copy.copy(self.vistrail.getVersionGraph())
        else:
            terse = copy.copy(self.vistrail.getTerseGraph())
        full = self.vistrail.getVersionGraph()
        if (not self.refine) or (not self.search):
            return self.ensureCurrentVersion(terse, full)
        am = self.vistrail.actionMap
        
        x=[0]
        while len(x):
            current=x.pop()
            efrom = []
            eto = []
            for f in terse.edges_from(current):
                efrom.append(f)
            for t in terse.edges_to(current):
                eto.append(t)
            for (e1,e2) in efrom:
                x.append(e1)
            if (current !=0 and
                not self.search.match(self.vistrail, am[current]) and
                terse.vertices.__contains__(current)):
                to_me = eto[0][0]
                if terse.vertices.__contains__(to_me):
                    terse.delete_edge(to_me, current, None)
                for from_me in efrom:
                    f_me = from_me[0]
                    if terse.vertices.__contains__(f_me):
                        annotated = -1
                        if full.parent(f_me)==to_me:
                            annotated=0
                        terse.delete_edge(current, f_me, None)
                        terse.add_edge(to_me, f_me, annotated)
                terse.delete_vertex(current)
        self.vistrail.setCurrentGraph(terse)
        return self.ensureCurrentVersion(terse, full)


    # FIXME: remove this function (left here only for transition)
    def ensureCurrentVersion(self, terse, full):
        """ ensureCurrentVersion(terse: Graph, full: Graph) -> (terse, full)
        Make sure the current version is in the terse graph
        
        """
        prev = self.currentVersion
        if prev>=0 and (not terse.vertices.has_key(prev)):
            if not full.vertices.has_key(prev):
                self.changeSelectedVersion(-1)
                return (terse, full)
            terse = copy.copy(terse)
            # Up-Stream
            parent = prev
            while parent!=-1:
                parent = full.parent(parent)
                if terse.vertices.has_key(parent):
                    terse.add_edge(parent, prev)
                    break

            # Down-Stream
            child = prev
            while True:
                edges = full.edges_from(child)
                assert len(edges)<=1
                if len(edges)==0:
                    break
                child = edges[0][0]
                if terse.vertices.has_key(child):
                    terse.add_edge(prev, child)
                    terse.delete_edge(parent, child)
                    break
        return (terse, full)

    def showPreviousVersion(self):
        """ showPreviousVersion() -> None
        Go back one from the current version and display it
        
        """
        full = self.vistrail.getVersionGraph()
        prev = None
        v = self.currentVersion
        am = self.vistrail.actionMap
        while True:
            parent = full.parent(v)
            if parent==-1:
                prev = 0
                break
            if (self.refine and self.search and
                (not self.search.match(self.vistrail, am[parent]))):
                v = prev
            else:
                prev = parent
                break
        if prev!=None:
            self.changeSelectedVersion(prev)
            self.resetVersionView = False
            self.invalidate_version_tree()
            self.resetVersionView = True

    def pruneVersions(self, versions):
        """ pruneVersions(versions: list of version numbers) -> None
        Prune all versions in 'versions' out of the view
        
        """
        # We need to go up-stream to the highest invisible node
        current = self.vistrail.currentGraph
        if not current:
            (current, full) = self.refineGraph()
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
                    if current.vertices.has_key(p):
                        break
                    highest = p
                if highest!=0:
                    changed = True
                self.vistrail.pruneVersion(highest)
        if changed:
            self.setChanged(True)
        self.invalidate_version_tree()

    def selectLatestVersion(self):
        """ selectLatestVersion() -> None
        Try to select the latest visible version on the tree
        
        """
        current = self.vistrail.currentGraph
        if not current:
            (current, full) = self.refineGraph()        
        self.changeSelectedVersion(max(current.iter_vertices()))

    def setSavedQueries(self, queries):
        """ setSavedQueries(queries: list of (str, str, str)) -> None
        Set the saved queries of a vistail
        
        """
        self.vistrail.setSavedQueries(queries)
        self.setChanged(True)
        

    def update_module_tag(self, module, tag):
        """ update_module_tag(module: Module, tag: str) -> None
        Updates the current module's tag
        
        """
        self.emit(QtCore.SIGNAL("flushMoveActions()"))
        
        if module.vtType == 'module':
            self.vistrail.update_object(module, db_tag=tag)
        elif module.vtType == 'abstractionRef':
            self.vistrail.update_object(module, db_name=tag)
        
    def updateCurrentTag(self,tag):
        """ updateCurrentTag(tag: str) -> None
        Update the current vistrail tag
        
        """
        self.emit(QtCore.SIGNAL("flushMoveActions()"))

        try:
            if self.vistrail.hasTag(self.currentVersion):
                self.vistrail.changeTag(tag, self.currentVersion)
            else:
                self.vistrail.addTag(tag, self.currentVersion)
        except TagExists:
            show_warning('Name Exists',
                         "There is already another version named '%s'.\n"
                         "Please enter a different one." % tag)
            return

        self.setChanged(True)

        self.resetVersionView = False
        self.invalidate_version_tree()
        self.resetVersionView = True
        
    def perform_param_changes(self, actions):
        new_timestep = -1
        for action in actions:
            for operation in action.operations:
                if operation.vtType == 'add' or operation.vtType == 'change':
                    if operation.new_obj_id < 0:
                        data = operation.data
                        new_id = self.vistrail.idScope.getNewId(data.vtType)
                        data.real_id = new_id
                        operation.new_obj_id = new_id
            self.vistrail.add_action(action, self.currentVersion)
            self.currentPipeline.perform_action(action)
            self.currentVersion = action.db_id
            new_timestep = self.currentVersion
        
        if new_timestep != -1:
            self.setChanged(True)
            self.invalidate_version_tree()
        return new_timestep

    def performBulkActions(self, actions):
        """performBulkAction(actions: [Action]) -> timestep        
        Add version to vistrail, updates the current pipeline, and the
        rest of the UI know a new pipeline is selected only after all
        actions are performed
        
        """
        newTimestep = -1
        for action in actions:
            self.vistrail.add_action(action, self.currentVersion)
            self.currentPipeline.perform_action(action)
            newTimestep = action.db_id
            self.currentVersion = action.db_id

        if newTimestep != -1 and not self.quiet:
            self.setChanged(True)
            self.invalidate_version_tree()
        
        return newTimestep

    def copyModulesAndConnections(self, module_ids, connection_ids):
        """copyModulesAndConnections(module_ids: [long],
                                     connection_ids: [long]) -> str
        Serializes a list of modules and connections
        """
        self.emit(QtCore.SIGNAL("flushMoveActions()"))

        pipeline = Pipeline()
        pipeline.set_abstraction_map(self.vistrail.abstractionMap)
        for module_id in module_ids:
            module = self.currentPipeline.modules[module_id]
            if module.vtType == AbstractionModule.vtType:
                abstraction = pipeline.abstraction_map[module.abstraction_id]
                pipeline.add_abstraction(abstraction)
            pipeline.add_module(module)
        for connection_id in connection_ids:
            connection = self.currentPipeline.connections[connection_id]
            pipeline.add_connection(connection)
        return core.db.io.serialize(pipeline)
        
    def pasteModulesAndConnections(self, str):
        """ pasteModulesAndConnections(str) -> [id list]
        Paste a list of modules and connections into the current pipeline.

        Returns the list of module ids of added modules

        """
        self.emit(QtCore.SIGNAL("flushMoveActions()"))

        pipeline = core.db.io.unserialize(str, Pipeline)
        modules = []
        connections = []
        if pipeline:
            def compare_abstractions(a1, a2):
                if a1.name != a2.name:
                    return False
                if len(a1.action_list) != len(a2.action_list):
                    return False
                if a1.action_list[0].user != a2.action_list[0].user:
                    return False
                if a1.action_list[0].date != a2.action_list[0].date:
                    return False
                return True

            id_remap = {}
            for new_abstraction in pipeline.get_abstractions():
                # don't want to duplicate an existing abstraction...
                # FIXME going to use a heuristic for this
                new_id = -1
                
                for abstraction in self.vistrail.abstractions:
                    if compare_abstractions(new_abstraction, abstraction):
                        new_id = abstraction.id
                        break

                # force a new id if new_id is -1
                if new_id == -1:
                    new_id = \
                        self.vistrail.idScope.getNewId(Abstraction.vtType)
                    new_abstraction.id = new_id
                    self.vistrail.add_abstraction(new_abstraction)
                id_remap[('abstraction', new_abstraction.id)] = new_id

            action = core.db.action.create_paste_action(pipeline, 
                                                        self.vistrail.idScope,
                                                        id_remap)
            modules = [op.objectId
                       for op in action.operations
                       if (op.what == 'module' or 
                           op.what == 'abstractionRef')]
            connections = [op.objectId
                           for op in action.operations
                           if op.what == 'connection']
                
            self.vistrail.add_action(action, self.currentVersion)
            self.perform_action(action)
            self.currentPipeline.ensure_connection_specs(connections)
        return modules

    def create_group(self, module_ids, connection_ids, name):
        self.emit(QtCore.SIGNAL("flushMoveActions()"))

        id_remap = {}
        pipeline = Pipeline()
        id_scope = IdScope(1, {Group.vtType: Module.vtType})

        avg_x = 0.0
        avg_y = 0.0
        
        abs_modules = []
        abs_connections = []
        changed_ports = []

        del_action_list = []
        for module_id in module_ids:
            module = self.currentPipeline.modules[module_id]
            del_action_list.append(('delete', module))
            avg_x += module.location.x
            avg_y += module.location.y
            tmp_remap = {}
            new_module = module.do_copy(True, id_scope, tmp_remap)

            # hack to make sure that we don't adds ids from group.pipeline
            if module.vtType == Group.vtType:
                id_remap[(Module.vtType, module_id)] = new_module.id
            else:
                id_remap.update(tmp_remap)
            pipeline.add_module(new_module)

        print '**** id_remap:', id_remap

        in_names = {}
        out_names = {}
        name_remap = {}
        for connection_id in connection_ids:
            connection = self.currentPipeline.connections[connection_id]
            all_inside = True
            all_outside = True
            for port in connection.ports:
                if not id_remap.has_key((Module.vtType, port.moduleId)):
                    all_inside = False
                else:
                    all_outside = False

            # if a connection has an "external" connection, we need to
            # create an input port or output port module
            new_ports = []
            if not all_inside and not all_outside:
                for port in connection.ports:
                    if not id_remap.has_key((Module.vtType, port.moduleId)):

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
                        if names.has_key(base_name):
                            port_name = base_name + '_' + str(names[base_name])
                            names[base_name] += 1
                        else:
                            port_name = base_name
                            names[base_name] = 2
                        name_remap[connection.id] = port_name

                        param_id = \
                            id_scope.getNewId(ModuleParam.vtType)
                        param = ModuleParam(id=param_id,
                                            pos=0,
                                            type='String',
                                            val=port_name)
                        function_id = \
                            id_scope.getNewId(ModuleFunction.vtType)
                        function_1 = ModuleFunction(id=function_id,
                                                  name='name',
                                                  parameters=[param])

                        param_id = \
                            id_scope.getNewId(ModuleParam.vtType)
                        param = ModuleParam(id=param_id,
                                            pos=0,
                                            type='String',
                                            val=port_specStr)

                        function_id = \
                            id_scope.getNewId(ModuleFunction.vtType)
                        function_2 = ModuleFunction(id=function_id,
                                                  name='spec',
                                                  parameters=[param])

                        param_id = \
                            id_scope.getNewId(ModuleParam.vtType)
                        param = ModuleParam(id=param_id,
                                            pos=0,
                                            type='String',
                                            val=base_name)

                        function_id = \
                            id_scope.getNewId(ModuleFunction.vtType)
                        function_3 = ModuleFunction(id=function_id,
                                                  name='old_name',
                                                  parameters=[param])

                        functions = [function_1, function_2, function_3]
#                         if port.endPoint == PortEndPoint.Source:
#                             functions.append(function_3)

                        # FIXME package name should not be hard-coded
                        new_id = id_scope.getNewId(Module.vtType)
                        module = Module(id=new_id,
                                        name=port_type,
                                        package='edu.utah.sci.vistrails.basic',
                                        location=location,
                                        functions=functions
                                        )
                        pipeline.add_module(module, id_remap)
                        # action_list.append(('add', module))
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

#         action = core.db.action.create_action(action_list)
#         action.date = self.vistrail.getDate()
#         action.user = self.vistrail.getUser()

#         abstraction.add_action(action, 0)
#         self.vistrail.add_abstraction(abstraction)

        # now group to vistrail
        loc_id = self.vistrail.idScope.getNewId(Location.vtType)
        location = Location(id=loc_id,
                            x=avg_x/len(module_ids), 
                            y=avg_y/len(module_ids),
                            )
        group_id = self.vistrail.idScope.getNewId(Group.vtType)
        group = Group(id=group_id, 
                      name=name, 
                      package='edu.utah.sci.vistrails.basic', 
                      location=location, 
                      pipeline=pipeline)

#         module_id = self.vistrail.idScope.getNewId(AbstractionModule.vtType)
#         module = AbstractionModule(id=module_id,
#                                    abstraction_id=abstraction.id,
#                                    version=1,
#                                    name=name, 
#                                    location=location,
#                                    cache=0,
#                                    )
        # need to delete connections before modules
        del_action_list.reverse()
        add_action_list = []
        add_action_list.append(('add', group))
        
        for (old_port, connection) in changed_ports:
            new_connection = connection.do_copy(True, self.vistrail.idScope, 
                                                id_remap)
            port_id = self.vistrail.idScope.getNewId(Port.vtType)
            changed_port = Port(id=port_id,
                                type=old_port.type,
                                moduleId=group.id,
                                moduleName=group.name,
                                name=name_remap[connection.id])
            changed_port.specStr = old_port.specStr
            changed_port.spec = old_port.spec

            if old_port.type == 'source':
                new_connection.source = changed_port
            else:
                new_connection.destination = changed_port
            add_action_list.append(('add', new_connection))
#         print 'add_actions:'
#         for a in add_action_list:
#             print a
#         print 'del actions:'
#         for a in del_action_list:
#             print a
        action = core.db.action.create_action(add_action_list + del_action_list)
        for op in action.db_operations:
            print op.vtType, op.what, op.old_obj_id, op.new_obj_id
        self.vistrail.add_action(action, self.currentVersion)
        self.perform_action(action)

        # FIXME we shouldn't have to return a module
        # we don't do it for any other type
        # doesn't match documentation either
        return group

    def ungroup_set(self, module_ids):
        for m_id in module_ids:
            self.ungroup(m_id)

    def ungroup(self, module_id):

        group = self.currentPipeline.modules[module_id]
        if group.vtType != Group.vtType:
            return
        pipeline = group.pipeline
        pipeline.ensure_connection_specs()

        id_remap = {}
        add_action_list = []
        del_action_list = []
        for module in pipeline.module_list:
            if module.name != InputPort.__name__ and \
                    module.name != OutputPort.__name__:
                new_module = module.do_copy(True, self.vistrail.idScope, 
                                            id_remap)
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
                
        
        for connection in self.currentPipeline.connection_list:
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
        for op in action.db_operations:
            print op.vtType, op.what, op.old_obj_id, op.new_obj_id
        self.vistrail.add_action(action, self.currentVersion)
        self.perform_action(action)

    def create_abstraction(self, module_ids, connection_ids, name):
        """ create_abstraction (module_ids : list[long], 
                                connection_ids : list[long],
                                name : str) -> AbstractionModule

        """
        self.emit(QtCore.SIGNAL("flushMoveActions()"))

        abstraction = Abstraction(id=-1, name=name)

        id_remap = {}
        avg_x = 0.0
        avg_y = 0.0
        
        abs_modules = []
        abs_connections = []
        changed_ports = []

        action_list = []
        del_action_list = []
        for module_id in module_ids:
            module = self.currentPipeline.modules[module_id]
            del_action_list.append(('delete', module))
            avg_x += module.location.x
            avg_y += module.location.y
            new_module  = module.do_copy(True, abstraction.idScope, 
                                         id_remap)
            action_list.append(('add', new_module))

        in_names = {}
        out_names = {}
        name_remap = {}
        for connection_id in connection_ids:
            connection = self.currentPipeline.connections[connection_id]
            all_inside = True
            all_outside = True
            for port in connection.ports:
                if not id_remap.has_key((Module.vtType, port.moduleId)):
                    all_inside = False
                else:
                    all_outside = False

            # if a connection has an "external" connection, we need to
            # create an input port or output port module
            new_ports = []
            if not all_inside and not all_outside:
                for port in connection.ports:
                    if not id_remap.has_key((Module.vtType, port.moduleId)):

                        loc_id = abstraction.idScope.getNewId(Location.vtType)
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
                        if names.has_key(base_name):
                            port_name = base_name + '_' + str(names[base_name])
                            names[base_name] += 1
                        else:
                            port_name = base_name
                            names[base_name] = 2
                        name_remap[connection.id] = port_name

                        param_id = \
                            abstraction.idScope.getNewId(ModuleParam.vtType)
                        param = ModuleParam(id=param_id,
                                            pos=0,
                                            type='String',
                                            val=port_name)
                        function_id = \
                            abstraction.idScope.getNewId(ModuleFunction.vtType)
                        function_1 = ModuleFunction(id=function_id,
                                                  name='name',
                                                  parameters=[param])

                        param_id = \
                            abstraction.idScope.getNewId(ModuleParam.vtType)
                        param = ModuleParam(id=param_id,
                                            pos=0,
                                            type='String',
                                            val=port_specStr)

                        function_id = \
                            abstraction.idScope.getNewId(ModuleFunction.vtType)
                        function_2 = ModuleFunction(id=function_id,
                                                  name='spec',
                                                  parameters=[param])

                        param_id = \
                            abstraction.idScope.getNewId(ModuleParam.vtType)
                        param = ModuleParam(id=param_id,
                                            pos=0,
                                            type='String',
                                            val=base_name)

                        function_id = \
                            abstraction.idScope.getNewId(ModuleFunction.vtType)
                        function_3 = ModuleFunction(id=function_id,
                                                  name='old_name',
                                                  parameters=[param])

                        functions = [function_1, function_2]
                        if port.endPoint == PortEndPoint.Source:
                            functions.append(function_3)

                        new_id = abstraction.idScope.getNewId(Module.vtType)
                        # FIXME package name should not be hard-coded
                        module = Module(id=new_id,
                                        name=port_type,
                                        package='edu.utah.sci.vistrails.basic',
                                        location=location,
                                        functions=functions
                                        )
                        action_list.append(('add', module))
                        spec_str = '(edu.sci.utah.vistrails.basic:%s)' % \
                            port_type
                        port_id = abstraction.idScope.getNewId(Port.vtType)
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
            new_connection = connection.do_copy(True, abstraction.idScope,
                                                id_remap)
            for port in new_ports:
                if port.endPoint == PortEndPoint.Source:
                    new_connection.source = port
                elif port.endPoint == PortEndPoint.Destination:
                    new_connection.destination = port
            action_list.append(('add', new_connection))

            # assume that we don't have len(new_ports) >= 2
            if len(new_ports) <= 1:
                # connection inside abstraction
                del_action_list.append(('delete', connection))                
            # else a change port -- done later

        action = core.db.action.create_action(action_list)
        action.date = self.vistrail.getDate()
        action.user = self.vistrail.getUser()

        abstraction.add_action(action, 0)
        self.vistrail.add_abstraction(abstraction)

        # now add module encoding abstraction reference to vistrail
        loc_id = self.vistrail.idScope.getNewId(Location.vtType)
        location = Location(id=loc_id,
                            x=avg_x/len(module_ids), 
                            y=avg_y/len(module_ids),
                            )
        module_id = self.vistrail.idScope.getNewId(AbstractionModule.vtType)
        module = AbstractionModule(id=module_id,
                                   abstraction_id=abstraction.id,
                                   version=1,
                                   name=name, 
                                   location=location,
                                   cache=0,
                                   )
        # need to delete connections before modules
        del_action_list.reverse()
        add_action_list = []
        add_action_list.append(('add', module))
        
        for (old_port, connection) in changed_ports:
            other_remap = {}
            new_connection = connection.do_copy(True, self.vistrail.idScope,
                                                other_remap)
            port_id = self.vistrail.idScope.getNewId(Port.vtType)
            changed_port = Port(id=port_id,
                                type=old_port.type,
                                moduleId=module.id,
                                moduleName=module.name,
                                name=name_remap[connection.id])
            changed_port.specStr = old_port.specStr
            changed_port.spec = old_port.spec

            if old_port.type == 'source':
                new_connection.source = changed_port
            else:
                new_connection.destination = changed_port
            add_action_list.append(('add', new_connection))
        action = core.db.action.create_action(add_action_list + del_action_list)
#         for op in action.db_operations:
#             print op.vtType, op.what, op.old_obj_id, op.new_obj_id
        self.vistrail.add_action(action, self.currentVersion)
        self.perform_action(action)
        self.currentPipeline.set_abstraction_map(self.vistrail.abstractionMap)

        # FIXME we shouldn't have to return a module
        # we don't do it for any other type
        # doesn't match documentation either
        return module

    def setVersion(self, newVersion):
        """ setVersion(newVersion: int) -> None
        Change the controller to newVersion

        """
        if not self.vistrail.hasVersion(newVersion):
            raise VistrailsInternalError("Can't change VistrailController "
                                         "to a non-existant version")
        self.currentVersion = newVersion

        self.emit(QtCore.SIGNAL("versionWasChanged"), newVersion)

    def setChanged(self, changed):
        """ setChanged(changed: bool) -> None
        Set the current state of changed and emit signal accordingly
        
        """
        if changed!=self.changed:
            self.changed = changed
            self.emit(QtCore.SIGNAL('stateChanged'))

    def setFileName(self, fileName):
        """ setFileName(fileName: str) -> None
        Change the controller file name
        
        """
        if fileName == None:
            fileName = ''
        if self.fileName!=fileName:
            self.fileName = fileName
            self.name = os.path.split(fileName)[1]
            if self.name=='':
                self.name = 'untitled%s'%vistrails_default_file_type()
            self.emit(QtCore.SIGNAL('stateChanged'))

    def checkAlias(self, name):
        """checkAlias(alias) -> Boolean 
        Returns True if current pipeline has an alias named name """
        return self.currentPipeline.has_alias(name)

    def write_temporary(self):
        if self.vistrail and self.changed:
            locator = self.get_locator()
            if locator:
                locator.save_temporary(self.vistrail)

    def write_vistrail(self, locator):
        if self.vistrail and (self.changed or self.locator != locator):
            # FIXME hack to use db_currentVersion for convenience
            # it's not an actual field
            self.vistrail.db_currentVersion = self.currentVersion
            if self.locator != locator:
                old_locator = self.get_locator()
                self.locator = locator
                new_vistrail = self.locator.save_as(self.vistrail)
                self.setFileName(locator.name)
                if old_locator:
                    old_locator.clean_temporaries()
            else:
                new_vistrail = self.locator.save(self.vistrail)
            if id(self.vistrail) != id(new_vistrail):
                new_version = new_vistrail.db_currentVersion
                self.setVistrail(new_vistrail, locator)
                self.changeSelectedVersion(new_version)
                self.invalidate_version_tree()
            self.setChanged(False)

    def write_workflow(self, locator):
        if self.currentPipeline:
            pipeline = Pipeline()
            pipeline.set_abstraction_map(self.vistrail.abstractionMap)
            for module in self.currentPipeline.modules.itervalues():
                if module.vtType == AbstractionModule.vtType:
                    abstraction = \
                        pipeline.abstraction_map[module.abstraction_id]
                    pipeline.add_abstraction(abstraction)
                pipeline.add_module(module)
            for connection in self.currentPipeline.connections.itervalues():
                pipeline.add_connection(connection)            
            locator.save_as(pipeline)

    def write_expanded_workflow(self, locator):
        if self.currentPipeline:
            (workflow, _) = core.db.io.expand_workflow(self.vistrail, 
                                                       self.currentPipeline)
            locator.save_as(workflow)
        
    
    def write_log(self, locator):
        if self.log:
            locator.save_as(self.log)

    def queryByExample(self, pipeline):
        """ queryByExample(pipeline: Pipeline) -> None
        Perform visual query on the current vistrail
        
        """
        if len(pipeline.modules)==0:
            search = TrueSearch()
        else:
            search = VisualQuery(pipeline)

        self.setSearch(search, '') # pipeline.dump_to_string())

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
#         try:
#             return addSubModule(moduleName, packageName, vistrail, fileName,
#                                 version, inspector)
#         except ModuleAlreadyExists:
#             show_warning('Module Exists',
#                          "Failed to registered '%s' as a module "
#                          "because there is already another module with "
#                          "the same name. Please change the version name "
#                          "and manually add it later." % moduleName)
#         except DupplicateSubModule:
#             show_warning('Module Exists',
#                          "Failed to registered '%s' as a module "
#                          "because it is already registered." % moduleName)

    def inspectAndImportModules(self):
        """ inspectAndImportModules() -> None        
        Go through all named pipelines and ask user to import them
        
        """

        # Currently broken
        pass
#         importModule = False
#         inspector = PipelineInspector()
#         for version in sorted(self.vistrail.inverseTagMap.keys()):
#             tag = self.vistrail.inverseTagMap[version]
#             if tag!='':
#                 pipeline = self.vistrail.getPipeline(version)
#                 inspector.inspect(pipeline)
#                 if inspector.is_sub_module():
#                     if importModule==False:
#                         res = show_question('Import Modules',
#                                             "'%s' contains importable modules. "
#                                             "Do you want to import all of them?"
#                                             % self.name,
#                                             [YES_BUTTON, NO_BUTTON], YES_BUTTON)
#                         if res==YES_BUTTON:
#                             importModule = True
#                         else:
#                             return
#                     if importModule:
#                         self.addSubModule(tag, self.name, self.vistrail,
#                                           self.fileName, version,
#                                           inspector)

#     def create_abstraction(self, subgraph):
#         self.vistrail.create_abstraction(self.currentVersion,
#                                          subgraph,
#                                          'FOOBAR')

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

    def perform_analogy(self, analogy_name, analogy_target, invalidate=True):
        if analogy_name not in self.analogy:
            raise VistrailsInternalError("missing analogy '%s'" %
                                         analogy_name)
        (a, b) = self.analogy[analogy_name]
        c = analogy_target
        core.analogy.perform_analogy_on_vistrail(self.vistrail,
                                                 a, b, c)
        self.setChanged(True)
        if invalidate:
            self.invalidate_version_tree()

################################################################################
# Testing

import unittest

class TestVistrailController(unittest.TestCase):

    def test_abstraction_create(self):
        from core.db.locator import XMLFileLocator
        import core.db.io
        v = XMLFileLocator(core.system.vistrails_root_directory() +
                           '/tests/resources/test_abstraction.xml').load()

        controller = VistrailController(v, False)
        pipeline = v.getPipeline(9L)
        controller.currentPipeline = pipeline
        controller.currentVersion = 9L
        
        module_ids = [1, 2, 3]
        connection_ids = [1, 2, 3]
        
        controller.create_abstraction(module_ids, connection_ids, 'FloatList')
        
#         from core.vistrail.module import Module
#         from core.vistrail.module_function import ModuleFunction
#         from core.vistrail.module_param import ModuleParam
#         from core.vistrail.abstraction_module import AbstractionModule
#         from core.vistrial.operation import AddOp, ChangeOp, DeleteOp
#         from db.domain import IdScope
        
#         id_scope = IdScope(remap={AddOp.vtType: 'operation',
#                                   ChangeOp.vtType: 'operation',
#                                   DeleteOp.vtType: 'operation',
#                                   AbstractionModule.vtType: Module.vtType})

#         p1 = ModuleParam(id=id_scope.getNewId(ModuleParam.vtType),
#                          type='Float',
#                          val='1.123')
#         f1 = ModuleFunction(id=id_scope.getNewId(ModuleFunction.vtType),
#                             name='value',
#                             parameters=[p1])
#         m1 = Module(id=id_scope.getNewId(Module.vtType),
#                     name='Float',
#                     package='edu.utah.sci.vistrails.basic',
#                     functions=[f1])

#         p2 = ModuleParam(id=id_scope.getNewId(ModuleParam.vtType),
#                          type='Float',
#                          val='4.456')
#         f2 = ModuleFunction(id=id_scope.getNewId(ModuleFunction.vtType),
#                             name='value',
#                             parameters=[p2])
#         m2 = Module(id=id_scope.getNewId(Module.vtType),
#                     name='Float',
#                     package='edu.utah.sci.vistrails.basic',
#                     functions=[f2])

#         m3 = Module(id=id_scope.getNewId(Module.vtType),
#                     name='List',
#                     package='edu.utah.sci.vistrails.basic',
#                     functions=[])
                    
#         m4 = Module(id=id_scope.getNewId(Module.vtType),
#                     name='List',
#                     package='edu.utah.sci.vistrails.basic',
#                     functions=[])
        
#         s1 = Port(id=id_scope.getNewId(Port.vtType),
#                   type='source',
#                   moduleId=m1.id,
#                   moduleName='Float',
#                   name='self')
#         d1 = Port(id=id_scope.getNewId(Port.vtType),
#                   type='destination',
#                   moduleId=m3.id,
#                   moduleName='List',
#                   name='self')
#         c1 = Connection(id=id_scope.getNewId(Connection.vtType),
#                         ports=[s1, d1])

#         s2 = Port(id=id_scope.getNewId(Port.vtType),
#                   type='source',
#                   moduleId=m2.id,
#                   moduleName='Float',
#                   name='self')
#         d2 = Port(id=id_scope.getNewId(Port.vtType),
#                   type='destination',
#                   moduleId=m4.id,
#                   moduleName='List',
#                   name='self')
#         c2 = Connection(id=id_scope.getNewId(Connection.vtType),
#                         ports=[s2, d2])
                
#         s3 = Port(id=id_scope.getNewId(Port.vtType),
#                   type='source',
#                   moduleId=m3.id,
#                   moduleName='List',
#                   name='self')
#         d3 = Port(id=id_scope.getNewId(Port.vtType),
#                   type='destination',
#                   moduleId=m4.id,
#                   moduleName='List',
#                   name='self')
#         c3 = Connection(id=id_scope.getNewId(Connection.vtType),
#                         ports=[s3, d3])

        

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
from core.utils import VistrailsInternalError, ModuleAlreadyExists
from core.modules import module_registry
from core.vistrail.action import Action, AddModuleAction, DeleteModuleAction, \
    ChangeParameterAction, AddConnectionAction, DeleteConnectionAction, \
    DeleteFunctionAction, ChangeAnnotationAction, DeleteAnnotationAction,\
    AddModulePortAction, DeleteModulePortAction, MoveModuleAction
from core.query.version import TrueSearch
from core.query.visual import VisualQuery
from core.vistrail.module import Module
from core.vistrail.pipeline import Pipeline
from core.vistrail.module_param import VistrailModuleType
from core.vistrail.vistrail import TagExists
from core.interpreter.default import default_interpreter
from core.inspector import PipelineInspector
from gui.utils import show_warning, show_question, YES_BUTTON, NO_BUTTON
from core.modules.sub_module import addSubModule, DupplicateSubModule
import core.startup
import copy
import os.path

################################################################################

class VistrailController(QtCore.QObject):
    """
    VistrailController is the class handling all action control in
    VisTrails. It updates pipeline, vistrail and emit signals to
    update the view
    
    """

    def __init__(self, vis=None, name=''):
        """ VistrailController(vis: Vistrail, name: str) -> VistrailController
        Create a controller from vis

        """
        QtCore.QObject.__init__(self)
        self.name = ''
        self.fileName = ''
        self.setFileName(name)
        self.vistrail = vis
        self.currentVersion = -1
        self.currentPipeline = None
        self.currentPipelineView = None
        self.previousModuleIds = []
        self.resetPipelineView = False
        self.resetVersionView = True
        self.quiet = False
        self.logger = core.startup.logger
        self.search = None
        self.refine = False
        self.changed = False
        self.fullTree = False

    def cleanup(self):
        pass

    def setVistrail(self, vistrail, name):
        """ setVistrail(vistrail: Vistrail, name: str) -> None
        Start controlling a vistrail
        
        """
        self.vistrail = vistrail
        self.currentVersion = -1
        self.currentPipeline = None
        self.setFileName(name)
        
    def addModule(self, name, x, y):
        """ addModule(name: str, x: int, y: int) -> version id
        Add a new module into the current pipeline
        
        """
        self.emit(QtCore.SIGNAL("flushMoveActions()"))

        if self.currentPipeline:
            newModule = Module()
            newModule.id = self.currentPipeline.fresh_module_id()
            newModule.center.reset(x,y)
            newModule.name = str(name)
            newModule.cache = 0
            newAction = AddModuleAction()
            newAction.module = newModule
            self.performAction(newAction)
            return newModule
        else:
            return None

    def deleteModule(self, moduleId):
        """ deleteModule(moduleId: int) -> version id
        Delete a module from the current pipeline
        
        """
        self.emit(QtCore.SIGNAL("flushMoveActions()"))
        graph = self.currentPipeline.graph

        action = DeleteConnectionAction()

        for v, id in graph.edgesFrom(module_id):
            action.addId(id)

        for v, id in graph.edgesTo(module_id):
            action.addId(id)

        self.performAction(action)

        action2 = DeleteModuleAction()
        action2.addId(module_id)
        return self.performAction(action2)


    def deleteModuleList(self, mList):
        """ deleteModule(mList: [int]) -> [version id]
        Delete multiple modules from the current pipeline
        
        """
        self.emit(QtCore.SIGNAL("flushMoveActions()"))
        graph = self.currentPipeline.graph

        action = DeleteConnectionAction()
        action2 = DeleteModuleAction()

        for module_id in mList:
            for v, id in graph.edgesFrom(module_id):
                if id not in action.ids:
                    action.addId(id)

            for v, id in graph.edgesTo(module_id):
                if id not in action.ids:
                    action.addId(id)
            
            action2.addId(module_id)
        l = [action, action2]
        return self.performBulkActions(l)

    def moveModuleList(self, mList):
        """ moveModuleList(mList: [(id,dx,dy)]) -> [version id]        
        Move all modules to a new location. No flushMoveActions is
        allowed to to emit to avoid recursive actions
        
        """
        action = MoveModuleAction()
        action.moves = copy.copy(mList)
        return self.performAction(action)
            
    def addConnection(self, conn):
        """ addConnection(conn: Connection) -> version id
        Add a new connection 'conn' into Vistrail
        
        """
        self.emit(QtCore.SIGNAL("flushMoveActions()"))
        action = AddConnectionAction()
        action.connection = conn
        return self.performAction(action)
    
    def deleteConnection(self, id):
        """ deleteConnection(id: int) -> version id
        Delete a connection with id 'id'
        
        """
        self.emit(QtCore.SIGNAL("flushMoveActions()"))
        action = DeleteConnectionAction()
        action.addId(id)

        return self.performAction(action)

    def deleteConnectionList(self, cList):
        """ deleteConnections(cList: list) -> version id
        Delete a list of connections
        
        """
        self.emit(QtCore.SIGNAL("flushMoveActions()"))
        action = DeleteConnectionAction()
        for id in cList:
            action.addId(id)

        self.performAction(action)

    def executeWorkflowList(self, vistrails):
        interpreter = default_interpreter.get()
        for vis in vistrails:
            (name, version, pipeline, view, logger) = vis
            (objs, errors, executed) = interpreter.execute(pipeline, name, version, view, logger)

    def executeCurrentWorkflow(self):
        """ executeCurrentWorkflow() -> None
        Execute the current workflow (if exists)
        
        """
        if self.currentPipeline:
            self.executeWorkflowList([(self.fileName,
                                       self.currentVersion,
                                       self.currentPipeline,
                                       self.currentPipelineView,
                                       self.logger)])

    def changeSelectedVersion(self, newVersion):
        """ changeSelectedVersion(newVersion: int) -> None        
        Change the current vistrail version into newVersion and emit a
        notification signal
        
        """
        self.currentVersion = newVersion
        if newVersion>=0:
            self.currentPipeline = self.vistrail.getPipeline(newVersion)
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

    def setSearch(self, search, refine = False):
        """ setSearch(search: SearchStmt, refine: bool) -> None
        Change the currrent version tree search statement
        
        """
        self.search = search
        self.refine = refine
        self.emit(QtCore.SIGNAL('vistrailChanged()'))

    def setFullTree(self, full):
        """ setFullTree(full: bool) -> None        
        Set if Vistrails should show a complete version tree or just a
        terse tree
        
        """
        self.fullTree = full
        self.emit(QtCore.SIGNAL('vistrailChanged()'))

    def refineGraph(self):
        """ refineGraph(controller: VistrailController) -> (Graph, Graph)        
        Refine the graph of the current vistrail based the search
        status of the controller. It also return the full graph as a
        reference
        
        """
        if self.fullTree:
            terse = self.vistrail.getVersionGraph().__copy__()
        else:
            terse = self.vistrail.getTerseGraph().__copy__()
        full = self.vistrail.getVersionGraph()
        if (not self.refine) or (not self.search): return (terse, full)
        am = self.vistrail.actionMap
        
        x=[0]
        while len(x):
            current=x.pop()
            efrom = []
            eto = []
            for f in terse.edgesFrom(current):
                efrom.append(f)
            for t in terse.edgesTo(current):
                eto.append(t)
            for (e1,e2) in efrom:
                x.append(e1)
            if (current !=0 and
                not self.search.match(am[current]) and
                terse.vertices.__contains__(current)):
                to_me = eto[0][0]
                if terse.vertices.__contains__(to_me):
                    terse.deleteEdge(to_me, current, None)
                for from_me in efrom:
                    f_me = from_me[0]
                    if terse.vertices.__contains__(f_me):
                        annotated = -1
                        if full.parent(f_me)==to_me:
                            annotated=0
                        terse.deleteEdge(current, f_me, None)
                        terse.addEdge(to_me, f_me, annotated)
                terse.deleteVertex(current)
        self.vistrail.setCurrentGraph(terse)
        return (terse, full)

    def updateCurrentTag(self,tag):
        """ updateCurrentTag(tag: str) -> None
        Update the current vistrail tag
        
        """
        self.emit(QtCore.SIGNAL("flushMoveActions()"))

        pInspector = PipelineInspector()
        if self.currentPipeline:
            pInspector.inspectInputOutputPorts(self.currentPipeline)
            
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

        if pInspector.isSubModule() and tag!='':
            ans = show_question("Add Sub-Module",
                                "'%s' can be used as a module in VisTrails. "
                                "Do you want to add it to VisTrails Modules?"
                                % tag,
                                [YES_BUTTON, NO_BUTTON], YES_BUTTON)
            if ans==YES_BUTTON:
                self.addSubModule(tag, self.name, self.vistrail, self.fileName,
                                  self.currentVersion, pInspector)
        self.setChanged(True)

        self.resetVersionView = False
        self.emit(QtCore.SIGNAL('vistrailChanged()'))
        self.resetVersionView = True

    def updateNotes(self,notes):
        """
        Parameters
        ----------

        - notes : 'QtCore.QString'
        
        """
        self.emit(QtCore.SIGNAL("flushMoveActions()"))
        
        self.vistrail.changenotes(str(notes),self.currentVersion)

        self.setChanged(True)
      
    def deleteMethod(self, function_id, module_id):
        """ deleteMethod(function_id: int, module_id: int) -> version id
        Delete a method with function_id from module module_id

        """
        self.emit(QtCore.SIGNAL("flushMoveActions()"))

        action = DeleteFunctionAction()
        action.functionId = function_id
        action.moduleId = module_id
        self.performAction(action)

    def addMethod(self, moduleId, f):
        """ addMethod(moduleId: int, function: ModuleFunction) -> None
        Add a new method into the module's function list
        
        """
        self.emit(QtCore.SIGNAL("flushMoveActions()"))

        m = self.currentPipeline.modules[moduleId]

        action = ChangeParameterAction()
        if f.getNumParams() == 0:
            action.addParameter(moduleId, m.getNumFunctions(), -1,
                                f.name,"", "","", "")
        else:
            for i in range(f.getNumParams()):
                p = f.params[i]
                action.addParameter(moduleId, m.getNumFunctions(),i,
                                    f.name, p.name, p.value(), p.type, "")
        self.performAction(action)
                   
    def deleteAnnotation(self, key, module_id):
        """
        Parameters
        ----------

        - key : 'string'

        - module_id : 'int'

        """
        self.emit(QtCore.SIGNAL("flushMoveActions()"))

        action = DeleteAnnotationAction()
        action.key = key
        action.moduleId = module_id
        self.performAction(action)

    def addAnnotation(self, pair, moduleId):
        """ addAnnotation(pair: (str, str), moduleId: int)        
        Add/Update a key/value pair annotation into the module of
        moduleId
        
        """
        self.emit(QtCore.SIGNAL("flushMoveActions()"))
        assert type(pair[0]) == type('')
        assert type(pair[1]) == type('')        
        action = ChangeAnnotationAction()
        action.addAnnotation(moduleId, pair[0], pair[1])
        self.performAction(action)
        
    def addModulePort(self, module_id, port):
        """
        Parameters
        ----------
        
        - module_id : 'int'
        
        - port : (portType, portName, portSpec)
        
        """
        self.emit(QtCore.SIGNAL("flushMoveActions()"))
        
        action = AddModulePortAction()
        action.addModulePort(module_id, port[0], port[1], port[2])
        self.performAction(action)
        
    def deleteModulePort(self, module_id, port):
        """
        Parameters
        ----------
        
        - module_id : 'int'
        
        - port : (portType, portName, portSpec)
        
        """
        self.emit(QtCore.SIGNAL("flushMoveActions()"))
        
        action = DeleteModulePortAction()
        action.moduleId = module_id
        action.portType = port[0]
        action.portName = port[1]
        self.performAction(action)
        
    def performAction(self, action):
        """ performAction(action: Action) -> timestep
        Add version to vistrail, updates the current pipeline, and the
        rest of the UI know a new pipeline is selected.
        
        """
        newTimestep = self.vistrail.getFreshTimestep()
        action.timestep = newTimestep
        action.parent = self.currentVersion
        action.date = self.vistrail.getDate()
        action.user = self.vistrail.getUser()
        self.vistrail.addVersion(action)

        action.perform(self.currentPipeline)
        self.currentVersion = newTimestep
        
        self.setChanged(True)
        
        if not self.quiet:
            self.emit(QtCore.SIGNAL('vistrailChanged()'))
        return newTimestep

    def performBulkActions(self, actions):
        """performBulkAction(actions: [Action]) -> timestep        
        Add version to vistrail, updates the current pipeline, and the
        rest of the UI know a new pipeline is selected only after all
        actions are performed
        
        """
        res = []
        newTimestep = -1;
        for action in actions:
            newTimestep = self.vistrail.getFreshTimestep()
            action.timestep = newTimestep
            action.parent = self.currentVersion
            action.date = self.vistrail.getDate()
            action.user = self.vistrail.getUser()
            self.vistrail.addVersion(action)

            action.perform(self.currentPipeline)
            self.currentVersion = newTimestep
            res.append(newTimestep)

        self.setChanged(True)
            
        if newTimestep != -1 and (not self.quiet):
            self.emit(QtCore.SIGNAL("vistrailChanged()"))
        
        return newTimestep

    def pasteModulesAndConnections(self, modules, connections):
        """ pasteModulesAndConnections(modules: [Module],
                                       connections: [Connection]) -> version id
        Paste a list of modules and connections into the current pipeline

        """
        self.quiet = True
        modulesMap ={}
        modulesToSelect = []
        actions = []
        self.previousModuleIds = []
        for module in modules:
            name = module.name
            x = module.center.x + 10.0
            y = module.center.y + 10.0
            t = self.addModule(name,x,y)
            newId = self.vistrail.actionMap[self.currentVersion].module.id
            self.previousModuleIds.append(newId)
            modulesMap[module.id]=newId
            modulesToSelect.append(newId)
            for fi in range(len(module.functions)):
                f = module.functions[fi]
                action = ChangeParameterAction()
                if f.getNumParams() == 0:
                    action.addParameter(newId, fi, -1, f.name, "",
                                        "","", "")
                for i in range(f.getNumParams()):
                    p = f.params[i]
                    action.addParameter(newId, fi, i, f.name, p.name,
                                        p.strValue, p.type, p.alias)
                actions.append(action)
            for (key,value) in module.annotations.items():
                action = ChangeAnnotationAction()
                action.addAnnotation(newId,key,value)
                actions.append(action)
            if module.registry:
                desc = module.registry.getDescriptorByName(module.name)
                for (name, spec) in desc.inputPorts.iteritems():
                    d = module_registry.registry.getDescriptor(spec[0][0][0])
                    print d.name
                    action = AddModulePortAction()
                    action.addModulePort(newId, 'input', name, '('+d.name+')')
                    actions.append(action)
                for (name, spec) in desc.outputPorts.iteritems():
                    d = module_registry.registry.getDescriptor(spec[0][0][0])
                    action = AddModulePortAction()
                    action.addModulePort(newId, 'output', name, '('+d.name+')')
                    actions.append(action)

        currentAction = self.performBulkActions(actions)
        
        for c in connections:
            conn = copy.copy(c)
            conn.id = self.currentPipeline.fresh_connection_id()
            conn.sourceId = modulesMap[conn.sourceId]
            conn.destinationId = modulesMap[conn.destinationId]
            currentAction = self.addConnection(conn)            
        self.quiet = False

        self.currentVersion = currentAction
        self.emit(QtCore.SIGNAL("vistrailChanged()"))

    def replaceFunction(self, module, functionId, paramList):
        self.emit(QtCore.SIGNAL("flushMoveActions()"))
        functionName= module.functions[functionId].name
        action = ChangeParameterAction()        
        for pId in range(len(paramList)):
            (pValue, pType, pAlias) = paramList[pId]
            action.addParameter(module.id,
                                functionId,
                                pId,
                                functionName,
                                '<no description>',
                                pValue,
                                pType,
                                pAlias)
        self.performAction(action)
        
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
        if self.fileName!=fileName:
            self.fileName = fileName
            self.name = os.path.split(fileName)[1]
            if self.name=='':
                self.name = 'Untitled.xml'
            self.emit(QtCore.SIGNAL('stateChanged'))

    def writeVistrail(self, fileName):
        """ writeVistrail(fileName: str) -> None
        Write vistrail to file and emit changed signal
        
        """
        if self.vistrail and (self.changed or fileName!=self.fileName):
            self.vistrail.serialize(fileName)
            self.changed = False
            self.fileName = fileName
            self.name = os.path.split(fileName)[1]
            self.emit(QtCore.SIGNAL('stateChanged'))

    def queryByExample(self, pipeline):
        """ queryByExample(pipeline: Pipeline) -> None
        Perform visual query on the current vistrail
        
        """
        if len(pipeline.modules)==0:
            search = TrueSearch()
        else:
            search = VisualQuery(pipeline)

        search.run(self.vistrail, '')
            
        self.setSearch(search)


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
        try:
            return addSubModule(moduleName, packageName, vistrail, fileName,
                                version, inspector)
        except ModuleAlreadyExists:
            show_warning('Module Exists',
                         "Failed to registered '%s' as a module "
                         "because there is already another module with "
                         "the same name. Please change the version name "
                         "and manually add it later." % moduleName)
        except DupplicateSubModule:
            show_warning('Module Exists',
                         "Failed to registered '%s' as a module "
                         "because it is already registered." % moduleName)

    def inspectAndImportModules(self):
        """ inspectAndImportModules() -> None        
        Go through all named pipelines and ask user to import them
        
        """
        importModule = False
        inspector = PipelineInspector()
        for tag, version in self.vistrail.tagMap.iteritems():
            if tag!='':
                pipeline = self.vistrail.getPipeline(version)
                inspector.inspect(pipeline)
                if inspector.isSubModule():
                    if importModule==False:
                        res = show_question('Import Modules',
                                            "'%s' contains importable modules. "
                                            "Do you want to import all of them?"
                                            % self.name,
                                            [YES_BUTTON, NO_BUTTON], YES_BUTTON)
                        if res==YES_BUTTON:
                            importModule = True
                        else:
                            return
                    if importModule:
                        self.addSubModule(tag, self.name, self.vistrail,
                                          self.fileName, version,
                                          inspector)

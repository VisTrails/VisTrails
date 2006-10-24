from PyQt4 import QtCore, QtGui
from common import VistrailsInternalError, InstanceObject, appendToDictOfLists
from vis_object import VisModule
from vis_pipeline import VisPipeline
from vis_types import VistrailModuleType
from vis_action import *
from modules import module_registry
from vis_macro import *
from debug import DebugPrint
import thread
import copy
import weakref
import version_tree_search
import copy
import query


################################################################################

class VisualQuery(query.Query):

    def __init__(self, pipeline):
        self.queryPipeline = copy.copy(pipeline)

    def heuristicDAGIsomorphism(self,
                                target, template,
                                target_ids, template_ids):
        resultIds = set()
        while 1:
            print "round starting", target, template, target_ids, template_ids
            templateNames = set([(i, template.modules[i].name)
                                 for i in template_ids])
            targetNames = {}
            for i in target_ids:
                appendToDictOfLists(targetNames, target.modules[i].name, i)

            nextTargetIds = set()
            nextTemplateIds = set()

            for (i, templateName) in templateNames:
                if templateName not in targetNames:
                    print "Template",templateName,"is not in",targetNames
                    return (False, resultIds)
                else:
                    resultIds.update(targetNames[templateName])
                    for matchedTargetId in targetNames[templateName]:
                        nextTargetIds.update([moduleId for
                                              (moduleId, edgeId) in
                                              target.graph.edgesFrom(matchedTargetId)])
                    nextTemplateIds.update([moduleId for
                                            (moduleId, edgeId) in
                                            template.graph.edgesFrom(i)])

            if not len(nextTemplateIds):
                print "No more templates to be matched, ok!"
                return (True, resultIds)

            target_ids = nextTargetIds
            template_ids = nextTemplateIds

    def run(self, vistrail, name):
        result = []
        self.tupleLength = 2
        versions = vistrail.tagMap.values()
        for version in versions:
            p = vistrail.getPipeline(version)
            matches = set()
            queryModuleNameIndex = {}
            for moduleId, module in p.modules.iteritems():
                appendToDictOfLists(queryModuleNameIndex, module.name, moduleId)
            for querySourceId in self.queryPipeline.graph.sources():
                querySourceName = self.queryPipeline.modules[querySourceId].name
                if not queryModuleNameIndex.has_key(querySourceName):
                    continue
                candidates = queryModuleNameIndex[querySourceName]
                for candidateSourceId in candidates:
                    print querySourceName
                    print p.modules[candidateSourceId].name
                    (match, targetIds) = self.heuristicDAGIsomorphism \
                                             (template = self.queryPipeline, 
                                              target = p,
                                              template_ids = [querySourceId],
                                              target_ids = [candidateSourceId])
                    if match:
                        matches.update(targetIds)
                        print matches
            for m in matches:
                result.append((version, m))
        self.queryResult = result
        print result
        self.computeIndices()
        return result
                
    def __call__(self):
        """Returns a copy of itself. This needs to be implemented so that
        a visualquery object looks like a class that can be instantiated
        once per vistrail."""
        return VisualQuery(self.queryPipeline)

class BaseController(QtCore.QObject, object):

    def addModule(self, name, x, y, quiet=False):
        """

        Parameters
        ----------

        - name : 'QtCore.QString'
          The name of the module

        - x: 'int'
          x coordinate
        - y: 'int'
          y coordinate

       Returns
       -------
       - timestep : 'int'
        The timestep of the corresponding action

        """
        self.emit(QtCore.SIGNAL("flushPendingActions()"))

        if self.currentPipeline:
            newModule = VisModule()
            newModule.id = self.currentPipeline.freshModuleId()
            newModule.center.reset(x,y)
            newModule.name = str(name)
            newModule.cache = 0

            newAction = AddModuleAction()
            newAction.module = newModule

            return self.performAction(newAction,False,quiet)


    def deleteModule(self, module_id):
        """
        Parameters
        ----------

        - module_id : 'int'

        """
        self.emit(QtCore.SIGNAL("flushPendingActions()"))
        graph = self.currentPipeline.graph

        action = DeleteConnectionAction()

        for v, id in graph.edgesFrom(module_id):
            action.addId(id)

        for v, id in graph.edgesTo(module_id):
            action.addId(id)

        self.performAction(action)

        action2 = DeleteModuleAction()
        action2.addId(module_id)
        self.performAction(action2)


    def deleteModuleList(self, mList):
        """
        Parameters
        ----------

        - mList : 'list'
          List of module_ids

        """
        self.emit(QtCore.SIGNAL("flushPendingActions()"))
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
        self.performBulkActions(l)

            
    def addConnection(self, conn, quiet=False):
        """
        Parameters
        ----------
        -conn : 'VisConnection'
        
        """
        self.emit(QtCore.SIGNAL("flushPendingActions()"))
        action = AddConnectionAction()
        action.connection = conn

        return self.performAction(action, False, quiet)
    
    def deleteConnection(self, id):
        """
        Parameters
        ----------

        - id : 'int'
        
        """
        self.emit(QtCore.SIGNAL("flushPendingActions()"))
        action = DeleteConnectionAction()
        action.addId(id)

        self.performAction(action)

    def deleteConnectionList(self, cList):
        """
        Parameters
        ----------

        - cList : 'list'
          List of connection_ids
        """
        self.emit(QtCore.SIGNAL("flushPendingActions()"))
        action = DeleteConnectionAction()
        for id in cList:
            action.addId(id)

        self.performAction(action)


    def createQueryObject(self):
        """Returns a Query object that corresponds to the query pipeline."""
        

class QueryController(BaseController):
    """ An intermediate class between the interface and the query builder. It
    makes sure interface signals become a query."""
    def __init__(self,builder):
        QtCore.QObject.__init__(self)
        self.currentPipeline = VisPipeline()
        self.queryView = None
        self.builder = weakref.proxy(builder)

        # Ugly effing hack
        self.versionTree = InstanceObject(search = version_tree_search.TrueSearch())

    def setQueryView(self, view):
        self.queryView = weakref.proxy(view)

    def performQuery(self):
        if not len(self.currentPipeline.modules):
            queryTemplate = version_tree_search.TrueSearch
        else:
            queryTemplate = VisualQuery(self.currentPipeline)
        self.builder.newQuery(queryTemplate)

    def pasteModulesAndConnections(self, modules, connections):
        self.queryView.updateVistrail()
        modulesMap ={}
        modulesToSelect = []
        actions = []
        freshId = self.currentPipeline.freshModuleId()
        for module in modules:
            name = module.name
            x = module.center.x + 10.0
            y = module.center.y + 10.0
            t = self.addModule(name,x,y,True)
            newId = freshId
            freshId += 1
            modulesMap[module.id]=newId
            modulesToSelect.append(newId)
#           for fi in range(len(module.functions)):
#               f = module.functions[fi]
#               action = ChangeParameterAction()
#               for i in range(f.getNumParams()):
#                   p = f.params[i]
#                   action.addParameter(newId, fi, i, f.name, p.name,
#                                       p.strValue, p.type, p.alias)
                   
#               actions.append(action)
#           for (key,value) in module.annotations.items():
#               action = ChangeAnnotationAction()
#               action.addAnnotation(newId,key,value)
#               actions.append(action)
            
#       self.performBulkActions(actions)
                    
        for c in connections:
            conn = copy.copy(c)
            conn.id = self.currentPipeline.freshConnectionId()
            conn.sourceId = modulesMap[conn.sourceId]
            conn.destinationId = modulesMap[conn.destinationId]
            self.addConnection(conn,True)
        
        self.currentPipelineView.invalidateLayout()
        self.currentPipelineView.shapeEngine.selectShapes(modulesToSelect)

    def performAction(self, action, isImplicit = False, quiet = False):
        action.perform(self.currentPipeline)
        self.queryView.setPipeline(self.currentPipeline)
        self.queryView.invalidateLayout()

    def performBulkActions(self, actionList):
        for action in actionList:
            action.perform(self.currentPipeline)
        self.queryView.setPipeline(self.currentPipeline)
        self.queryView.invalidateLayout()


class VistrailController(BaseController):
    """ Intermediate class between the interface and the vistrails. It
    links with signals and slots in the interface """ 
    def __init__(self, vis, name=''):
        """ VistrailController Constructor.

        Parameters
        ----------

        - vis : Vistrail


        """
        BaseController.__init__(self)
        if not vis:
            raise VistrailsInternalError("VistrailController needs a real Vistrail")
        self.name = name
        self.vistrail = vis
        self.currentVersion = 0
        self.currentPipeline = None
        self.currentPipelineView = None
        self.recMacro = False
        self.currentMacro = None
        app = QtCore.QCoreApplication.instance()
        self.logger = app.logger

    def _setName(self, name):
        self.__controllerName = name

    def _getName(self):
        return self.__controllerName
    name = property(_getName, _setName)


    def executeWorkflow(self, vistrails):
        for vis in vistrails:
            (name, version, pipeline, view, logger) = vis
            import interpreter
            if self.logger:
                self.logger.startWorkflowExecution(name, version)
            pipeline.resolveAliases()
            (objs, errors, executed) = interpreter.Interpreter().execute(pipeline, name, version, view, logger)
            for obj in objs.itervalues():
                i = obj.id
                if errors.has_key(i):
                    view.setModuleError(i, errors[i])
                elif executed.has_key(i):
                    view.setModuleSuccess(i)
                else:
                    view.setModuleNotExecuted(i)
            if self.logger:
                self.logger.finishWorkflowExecution(name, version)        

    def sendToSpreadsheet(self):
        thread.start_new_thread(self.executeWorkflow,
                                (((self.name,
                                   self.currentVersion,
                                   self.currentPipeline,
                                   self.currentPipelineView,
                                   self.logger),),))
                                
#         for id, obj in result.iteritems():
#             print "id:",id,"obj:",obj
#             print obj.outputPorts
#         self.spreadsheet.setVistrail(self, self.vistrail, self.currentVersion,
#                                      self.currentPipeline,
#                                      self.spreadsheet.getCurrentSheet().SelectedCells)

    def changeSelectedVersion(self, new_version):
        """
        Parameters
        ----------

        - new_version : 'int'

        """
        self.currentVersion = new_version
        self.currentPipeline = self.vistrail.getPipeline(self.currentVersion)
        self.emit(QtCore.SIGNAL("versionWasChanged"),new_version, False)

    def updateCurrentTag(self,tag):
        """
        Parameters
        ----------

        - tag : 'QtCore.QString'
        
        """
        self.emit(QtCore.SIGNAL("flushPendingActions()"))
      
        if tag == QtCore.QString("") and self.vistrail.hasTag(self.currentVersion):
            raise VistrailsInternalError("Tags cannot be erased.")
        else:
            if self.vistrail.hasTag(self.currentVersion):
                changed = self.vistrail.changeTag(str(tag),self.currentVersion)
            else:
                changed = self.vistrail.addTag(str(tag), self.currentVersion)
      
        self.emit(QtCore.SIGNAL("tagChanged(int,QString)"),self.currentVersion,
                                self.tr(self.vistrail.inverseTagMap[self.currentVersion]))

        self.emit(QtCore.SIGNAL("vistrailChanged()"))

    def updateNotes(self,notes):
        """
        Parameters
        ----------

        - notes : 'QtCore.QString'
        
        """
        self.emit(QtCore.SIGNAL("flushPendingActions()"))
        
        self.vistrail.changenotes(str(notes),self.currentVersion)
      
        #self.emit(QtCore.SIGNAL("vistrailChanged()"))

    def deleteMethod(self, function_id, module_id):
        """
        Parameters
        ----------

        - function_id : 'int'

        - module_id : 'int'

        """
        self.emit(QtCore.SIGNAL("flushPendingActions()"))

        action = DeleteFunctionAction()
        action.functionId = function_id
        action.moduleId = module_id
        self.performAction(action)

    def addMethod(self, newMethod, module_id):
        """
        Parameters
        ----------

        - newMethod : (str, str, str)

        - module_id : 'int'

        """
        self.emit(QtCore.SIGNAL("flushPendingActions()"))

        (className, methodName, sig) = newMethod

        m = self.currentPipeline.getModuleById(module_id)

        functions = module_registry.registry.userSetMethods(className)
        if m.registry:
            localFunctions = m.registry.userSetMethods(className)
            for klass in localFunctions:
                if functions.has_key(klass):
                    functions[klass].update(localFunctions[klass])
                else:
                    functions[klass] = localFunctions[klass]
        fs = functions[className][methodName]
        f = fs[0]
        for i in fs:
            isig = i.getSignature()
            isig = isig[isig.find('('):]
            if sig==isig:
                f = i
                break
        action = ChangeParameterAction()
        if f.getNumParams() == 0:
            action.addParameter(module_id, m.getNumFunctions(), -1,
                                f.name,"", "","", "")
        else:
            for i in range(f.getNumParams()):
                p = f.params[i]
                action.addParameter(module_id, m.getNumFunctions(),i,
                                    f.name, p.name, p.value(), p.type, "")
        self.performAction(action)
                   
    def deleteAnnotation(self, key, module_id):
        """
        Parameters
        ----------

        - key : 'string'

        - module_id : 'int'

        """
        self.emit(QtCore.SIGNAL("flushPendingActions()"))

        action = DeleteAnnotationAction()
        action.key = key
        action.moduleId = module_id
        self.performAction(action)

    def addAnnotation(self, newKey, module_id):
        """
        Parameters
        ----------
        
        - newKey : (str, str)
        
        - module_id : 'int'
        
        """
        self.emit(QtCore.SIGNAL("flushPendingActions()"))
        assert type(newKey[0]) == type('')
        assert type(newKey[1]) == type('')
        
        action = ChangeAnnotationAction()
        action.addAnnotation(module_id, newKey[0], newKey[1])
        self.performAction(action)
        
    def addModulePort(self, module_id, port):
        """
        Parameters
        ----------
        
        - module_id : 'int'
        
        - port : (portType, portName, portSpec)
        
        """
        self.emit(QtCore.SIGNAL("flushPendingActions()"))
        
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
        self.emit(QtCore.SIGNAL("flushPendingActions()"))
        
        action = DeleteModulePortAction()
        action.moduleId = module_id
        action.portType = port[0]
        action.portName = port[1]
        self.performAction(action)
        
    def performAction(self, action, isImplicit=False, quiet=False):
        """performAction(action) -> timestep - Add version to vistrail, updates the current
        pipeline, and the rest of the UI know a new pipeline is selected.
        isImplicit is flag that says if the user generated this action (isImplicit==False)
        or if the system (isImplicit==True). For example, when the user deletes a module, a lot of connections
        will also be deleted automatically. And when recording a macro, we don't want
        to record those actions because they will be performed automatically when applying the macro.
        """
        newTimestep = self.vistrail.getFreshTimestep()
        action.timestep = newTimestep
        action.parent = self.currentVersion
        action.date = self.vistrail.getDate()
        action.user = self.vistrail.getUser()
        self.vistrail.addVersion(action)

        action.perform(self.currentPipeline)
        self.currentVersion = newTimestep

        #Recording macro
        if self.recMacro:
            if not isImplicit:
                self.currentMacro.addAction(newTimestep)
                self.emit(QtCore.SIGNAL("updateMacro"),self.currentMacro.name)
        if not quiet:
            self.emit(QtCore.SIGNAL("vistrailChanged()"))
        self.emit(QtCore.SIGNAL("versionWasChanged"),newTimestep, quiet)
        return newTimestep

    def performBulkActions(self, actions):
        """performBulkAction(actions) -> list(newtimesteps) - Add version to vistrail, updates the current
        pipeline, and the rest of the UI know a new pipeline is selected only after all actions are performed..
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
            #Recording macro
            if self.recMacro:
                if not isImplicit:
                    self.currentMacro.addAction(newTimestep)
                    self.emit(QtCore.SIGNAL("updateMacro"),self.currentMacro.name)
            
        if newTimestep != -1:
            self.emit(QtCore.SIGNAL("vistrailChanged()"))
            self.emit(QtCore.SIGNAL("versionWasChanged"),newTimestep,False)
        
        return res


    def pasteModulesAndConnections(self, modules, connections):
        self.currentPipelineView.updateVistrail()
        modulesMap ={}
        modulesToSelect = []
        actions = []
        for module in modules:
            name = module.name
            x = module.center.x + 10.0
            y = module.center.y + 10.0
            t = self.addModule(name,x,y,True)
            newId = self.vistrail.actionMap[t].module.id
            modulesMap[module.id]=newId
            modulesToSelect.append(newId)
            for fi in range(len(module.functions)):
                f = module.functions[fi]
                action = ChangeParameterAction()
                for i in range(f.getNumParams()):
                    p = f.params[i]
                    action.addParameter(newId, fi, i, f.name, p.name,
                                        p.strValue, p.type, p.alias)
                   
                actions.append(action)
            for (key,value) in module.annotations.items():
                action = ChangeAnnotationAction()
                action.addAnnotation(newId,key,value)
                actions.append(action)
            
        self.performBulkActions(actions)
                    
        currentAction = -1
        for c in connections:
            conn = copy.copy(c)
            conn.id = self.currentPipeline.freshConnectionId()
            conn.sourceId = modulesMap[conn.sourceId]
            conn.destinationId = modulesMap[conn.destinationId]
            currentAction = self.addConnection(conn,True)

        if currentAction != -1:
            self.emit(QtCore.SIGNAL("vistrailChanged()"))
            self.emit(QtCore.SIGNAL("versionWasChanged"),currentAction,False)
        
        self.currentPipelineView.invalidateLayout()
        self.currentPipelineView.shapeEngine.selectShapes(modulesToSelect)

    def replaceModuleParams(self, module, functionName, paramList):
        self.emit(QtCore.SIGNAL("flushPendingActions()"))
        for fid in reversed(range(len(module.functions))):
            if module.functions[fid].name==functionName:
                action = DeleteFunctionAction()
                action.functionId = fid
                action.moduleId = module.id
                self.performAction(action)
        typeConverter = {int:'Integer', float:'Float', str:'String'}
        for param in paramList:
            action = ChangeParameterAction()
            for i in range(len(param)):
                action.addParameter(module.id,
                                    module.getNumFunctions(),
                                    i,
                                    functionName,
                                    '<no description>',
                                    str(param[i]),
                                    typeConverter[type(param[i])],
                                    '')
            self.performAction(action)
            
    def consolidatePendingActions(self):
        self.emit(QtCore.SIGNAL("flushPendingActions()"))
         
    def createMacro(self, name='', desc=''):
        """ Creates a macro with a given name, start and end timesteps

        Parameters
        ----------

        - name : 'str'

        - desc : 'str'

    

        Returns
        -------

        - 'VisMacro'
        
        """
        macro = VisMacro(self.vistrail)
        macro.name = name
        macro.description = desc
        self.vistrail.addMacro(macro)
        self.currentMacro = macro
        return macro
        
    def setVersion(self, new_version):
        """
        Parameters
        ----------

        - new_version : 'int'

        """
        if not self.vistrail.hasVersion(new_version):
            raise VistrailsInternalError("Can't change VistrailController to a non-existant version")
        self.currentVersion = new_version

        self.emit(QtCore.SIGNAL("versionWasChanged"), new_version,False)

    def getMacroNames(self):
        """ Returns a list of the macros available in this vistrail

        Returns
        -------

        - 'list'of 'str'
        
        """
        result = []
        for m in self.vistrail.macroMap.keys():
            result.append(m)
        return result

    def getMacro(self, name):
        """ Returns the macro object of name 'name'

        Returns
        -------

        - 'VisMacro'

        """
        macro = self.vistrail.macroMap[name]
        return macro

    def macroChanged(self,oldname):
        self.vistrail.changeMacroName(oldname)

    def recordMacro(self, record):
        self.recMacro = record
        

        
        

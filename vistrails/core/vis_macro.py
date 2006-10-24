import copy
from common import unimplemented, abstract, VistrailsInternalError
from vis_connection import VisConnection
from enum import enum
from data_structures import Point
from vis_types import *
from vis_action import *
from PyQt4 import QtCore, QtGui
class VisMacro(object):
    """ Class that represents a Vis Macro.
    
    Member Description
    ------------------
    
        self.modules is a dictionary of modules referenced by the macro
        and it is in the form:
                macroModuleId -> externalModuleId
                
             Notice that when the macro contains an action addModule, macroModuleId
             and externalModuleId will be the same

        self.connections is a dictionary of
                macroConnectionId -> externalConnectionId

        self.extModules is a list of ModuleIds that point to external pre-existent
        modules in the pipeline (outside the macro).

        self.extConnections is a list of ConnectionIds that point to external
        pre-existent connections in the pipeline (outside the macro).
        
    """
    __fields__ = ['id','startTime', 'name', 'description', 'actions',
                  'modules', 'extModules', 'connections',
                  'extConnections','pipeline', 'vistrail', 'actionList',
                  'startPos']
    def __init__(self, vis):
        """ VisMacro Constructor.

        Parameters
        ----------

        - vis : 'Vistrail'
          Vistrail object

        - startTime : 'int'
          Timestep of the first action in the macro

        - endTime : 'int'
          Timestep of the last action in the macro
          
        - loadActions : 'boolean'
          If True, the macro will load all actions between the timesteps
          
        """
        self.vistrail = vis
        self.name = ''
        self.description = ''
        self.id = -1
        self.actionList = []
        self.clear()
        self.pipeline = None

    def _set_endTime(self,time):
        self.__endTime = time
        if time != 0:
            self.loadActions()

    def _get_endTime(self):
        return self.__endTime
    endTime = property(_get_endTime, _set_endTime)

    def clear(self):
        self.actions = {}
        self.modules = {}
        self.extModules = []
        self.connections = {}
        self.extConnections = []
        
    def loadActions(self):
        if self.vistrail:
            self.clear()
            if len(self.actionList) > 0:
                #the last action on actionList will contain the endTime
                endTime = self.actionList[-1]
                self.pipeline = self.getPipeline(endTime)
                self.buildActionChain()
        else:
            raise VistrailsInternalError("vistrail object is null")

    def getPipeline(self, timestep):
        return self.vistrail.getPipeline(timestep)
        
    def addAction(self, timestep):
        """ Adds an action to the macro during recording time.

        Parameters
        ----------

        - timestep : 'int'
          The timestep
        
        """
        self.actionList.append(timestep)

    def removeAction(self,timestep):
        pass
        
    def buildActionChain(self):
        """ Builds the action chain which will compose the macro according 
        to self.actionList.
        
        """
        st = self.actionList[0]
        et = self.actionList[-1]
        list = []
        self.actions = {}
        for a in self.actionList:
            self.actions[a] = VisMacroAction.create(self.vistrail.actionMap[a],self)


    def applyMacro(self, viscontrol, pipeline, force=True):
        """ Applies the macro to pipeline. When applying a macro, the
        external modules must have been mapped or we get an errorr. We
        need to call checkExternals before. The actions to be performed
        will also be added to the vistrail history, through the vistrail
        controller object.

        Parameters
        ----------

        - viscontrol : 'VistrailController'
        
        - pipeline : 'VisPipeline'
          
        """
        if self.checkExternals():
            if self.checkDependencies(force):
                if len(self.extModules) > 0:
                    for i in range(len(self.extModules)):
                        m_id = self.modules[self.extModules[i]]
                        if m_id:
                            m = pipeline.getModuleById(m_id)
                            self.startPos = Point(m.center.x, m.center.y)
                            break
                for a in self.actionList:
                    action = self.actions[a]
                    if action.enabled: 
                        action.generate(pipeline)
                        if action.endAction.type == "DeleteModule":
                            #the connections to that module will be deleted by
                            #VisController when this action is performed
                            for id in action.endAction.ids:
                                viscontrol.deleteModule(id)
                        else:
                            viscontrol.performAction(copy.copy(action.endAction))
            else:
                raise InvalidActionFound() 
        else:
            raise ExternalModuleNotSet()

    def checkExternals(self):
        """ Return True if all external modules are set """
        result = True
        for ext in self.extModules:
            if self.modules[ext] == None:
                for a in self.actions.values():
                    if a.moduleReferenced(ext) and a.enabled:
                        result = False
                        break
        for ext in self.extConnections:
            if self.connections[ext] == None:
                for a in self.actions.values():
                    if a.connReferenced(ext) and a.enabled:
                        if not self.moduleToBeDeletedIn(ext):
                            result = False
                            break
        return result
    
    def checkExternalModule(self,id):
        if self.modules[id] == None:
            return False
        else:
            return True

    def checkExternalConnection(self,id):
        result = True
        if self.connections[id] == None:
            if not self.moduleToBeDeletedIn(id):
                result = False
        return result

    def getAction(self, type, id, source):
        """ Returns the first enabled action id (timestep) of type 'type' 
            starting from source and following the action chain that 
            references 'id'.
            This is used when source wants to know if its dependencies are enabled
            Parameters
            ----------
             - type : 'str'
               type of action to be found
             - id : 'list' or 'int'
             - source : VisMacroAction
    
        """
        a = source.baseAction.parent
        while a in self.actionList:
            action = self.actions[a]
            if action.enabled:
                if action.baseAction.type == type:
                    ids = action.getId()
                    for i in ids:
                        if i == id:
                            return a
            a = action.baseAction.parent
        return -1 #failure

    def checkDependencies(self, force=True):
        """ Checks for all enabled actions if all required dependent actions
            are also enabled.
            If force is True, it will disable invalid actions. 
        
            Dependencies are considered in the following way: 
            For each action a, if a is a:
                 * AddModule -> no dependecies required
                 * ChangeParameter -> AddModule
                 * DeleteModule -> AddModule
                 * DeleteFunction -> ChangeParameter -> AddModule
                 * MoveModule -> AddModule
                 * AddConnection -> AddModule, AddModule
                 * DeleteConnection -> AddConnection -> AddModule, AddModule 
        """
        verified = {}
        for t in self.actionList:
            action = self.actions[t]
            if action.enabled:
                if not verified.has_key(t):
                    res = action.checkDependencies(verified,force)
                    if not res:
                        return False
        return True

    def moduleToBeDeletedIn(self,id):
        """ Returns True if the connection identified by id connects a module that
        will be deleted by the macro

        Parameters
        ----------

        - id : 'int'
          connection id

        Returns
        -------

        - 'boolean'
        
        """
        result = False

        a = self.actions[self.startTime]
        t = a.baseAction.parent
        pipeline = self.getPipeline(t)

        if pipeline:
            c = pipeline.getConnectionById(id)
            m1 = c.sourceId
            m2 = c.destinationId
            for a in self.actions.values():
                if a.endAction.type == 'DeleteModule' and a.enabled:
                    if a.sourceId in [m1,m2]:
                        if self.checkExternalModule(a.sourceId):
                            result = True
                            break
        return result
            

    def serialize(self, dom, element):
        """ Adds itself to an XML parent element

        Parameters
        ----------

        - dom : 'XML Document'

        - element : 'XML Element'

        
        """
        m = dom.createElement('macro')
        m.setAttribute('id',str(self.id))
        m.setAttribute('name',str(self.name))
        m.setAttribute('desc', str(self.description))
        for a in self.actionList:
            child = dom.createElement('action')
            child.setAttribute('time',str(a))
            m.appendChild(child)
    
        element.appendChild(m)

    @staticmethod
    def createFromXML(vis, element):
        """
        
        Parameters
        ----------

        - vis : 'Vistrail'
        - element : 'XML Element'

        """
        newMacro = VisMacro(vis)
        newMacro.id = int(element.getAttribute('id'))
        newMacro.name = str(element.getAttribute('name'))
        newMacro.description = str(element.getAttribute('desc'))

        newMacro.actionList = [int(m.getAttribute('time'))
                               for m in named_elements(element, 'action')]
        newMacro.loadActions()
        return newMacro
    
    def __str__(self):
        """ Returns a string representation of a VisMacro object
    
        Returns
        -------

        - 'str'
        
        """
        s = '<VisMacro name=%s desc=%s id=%s>\n' % \
               (self.name, self.description, self.id)
        tmp = ''
        for a in self.actionList:
            tmp += tmp + '<action time=%s/>\n' % a
        s += s + tmp
        s += '</Vismacro>'
            
VisMacroActionElement = enum('VisMacroActionElement',
                       ['Undefined', 'Internal', 'External'])            

class VisMacroAction(QtCore.QObject, object):
    createDispatch = {}
    __fields__ = [ 'baseAction', 'macro', 'endAction', 
                   'sourceName', 'sourceType', 'sourceId']
    def _set_enabled(self, value):
        if value != self.__enabled:
            self.__enabled = value
            self.emit(QtCore.SIGNAL("enabledChanged"), self.baseAction.timestep, value)
    
    def _get_enabled(self):
        return self.__enabled
    
    enabled = property(_get_enabled, _set_enabled)

    def setEnabled(self, value):
        """ Does not generate signal to avoid a loop"""
        self.__enabled = value

    @staticmethod
    def create(action, macro):
        if action.type is 'AddModule':
            return VisMacroActionAddModule(action,macro)
        elif action.type is 'AddConnection':
            return VisMacroActionAddConnection(action,macro)
        elif action.type is 'ChangeParameter':
            return VisMacroActionChangeParameter(action,macro)
        elif action.type is 'DeleteModule':
            return VisMacroActionDeleteModule(action,macro)
        elif action.type is 'DeleteConnection':
            return VisMacroActionDeleteConnection(action,macro)
        elif action.type is  'MoveModule':
            return VisMacroActionMoveModule(action,macro)
        elif action.type is 'DeleteFunction':
            return VisMacroActionDeleteFunction(action,macro)
    
    def __init__(self, action, macro):
        QtCore.QObject.__init__(self)
        self.baseAction = action
        self.macro = macro
        self.endAction = None
        self.__enabled = True
        self.sourceName = ''
        self.sourceType = VisMacroActionElement.Undefined
        self.sourceId = -1
        
    def generate(self, pipeline):
        abstract()

    def info(self):
        abstract()
        
    def verifyNumModules(self):
        abstract()

    def moduleReferenced(self,id):
        abstract()

    def connReferenced(self,id):
        abstract()

    def checkDependencies(self, dict, force=True):
        """ Check its dependecies and insert itself in dict 
            dict[timestep] = result (True or False)
            If force == True, and result is false, the correspondent 
            action is marked disabled
        """
        abstract()

    def getId(self):
        """ Returns a list of related module/connection ids
            For example, AddModule -> [moduleId], AddConnection -> [connection.id]
        """
        abstract()

class VisMacroActionImportVistrail(VisMacroAction):
    def __init__(self, action, macro):
        VisMacroAction.__init__(self, action, macro)
        self.endAction = ImportVistrailAction()
        self.endAction.modules = copy.deepcopy(action.modules)
        self.endAction.connections = copy.deepcopy(action.connections)

    def connReferenced(self,id):
        return False
        
    def generate(self, pipeline):
        pass

    def info(self):
        return [self.endAction.type]

    def moduleReferenced(self,id):
        return False
    
    def verifyNumModules(self):
        return True
    
    def checkDependencies(self, dict):
        dict[self.baseAction.timestep] = True #no dependencies
        return True
    
    def getId(self):
        return []
    
class VisMacroActionAddModule(VisMacroAction):
    def __init__(self, action, macro):
        VisMacroAction.__init__(self, action, macro)
        self.endAction = AddModuleAction()
        import copy
        self.endAction.module = copy.copy(action.module)
        self.macro.modules[self.endAction.module.id] = None
        self.sourceId = self.endAction.module.id
        self.sourceName = self.baseAction.module.name
        self.sourceType = VisMacroActionElement.Internal

    def connReferenced(self,id):
        return False

    def generate(self, pipeline):
        newId = pipeline.freshModuleId()
        self.macro.modules[self.endAction.module.id] = newId
        self.endAction.module.id = newId
        self.endAction.module.center = self.macro.startPos + Point(-20,-100)
        self.macro.startPos = self.endAction.module.center

    def info(self):
        return [self.endAction.type, self.sourceName]

    def moduleReferenced(self,id):
        if self.sourceId == id:
            return True
        else:
            return False

    def verifyNumModules(self):
        return True

    def checkDependencies(self, dict, force=True):
        dict[self.baseAction.timestep] = True #no dependencies
        return True

    def getId(self):
        return [self.sourceId]

class VisMacroActionAddConnection(VisMacroAction):
    __fields__ = [ 'destName', 'destType', 'destId']
    def __init__(self, action, macro):
        VisMacroAction.__init__(self, action, macro)
        self.endAction = AddConnectionAction()
        import copy
        self.endAction.connection = copy.copy(action.connection)
        self.macro.connections[self.endAction.connection.id] = None
        self.sourceId = self.endAction.connection.sourceId
        self.destId = self.endAction.connection.destinationId
        if not self.macro.modules.has_key(self.sourceId):
            self.macro.modules[self.sourceId] = None
            self.macro.extModules.append(self.sourceId)
                
        if not self.macro.modules.has_key(self.destId):
            self.macro.modules[self.destId] = None
            self.macro.extModules.append(self.destId)
                 
        #getting information about the modules involved in the connection
        if self.macro.pipeline:
            m1  = self.macro.pipeline.getModuleById(self.sourceId)
            m2  = self.macro.pipeline.getModuleById(self.destId)
            self.sourceName = m1.name
            self.destName = m2.name
            if m1.id in self.macro.extModules:
                self.sourceType = VisMacroActionElement.External
            else:
                self.sourceType = VisMacroActionElement.Internal

            if m2.id in self.macro.extModules:
                self.destType = VisMacroActionElement.External
            else:
                self.destType = VisMacroActionElement.Internal

    def connReferenced(self,id):
        return False
           
    def generate(self, pipeline):
        newCId = pipeline.freshConnectionId()
        self.macro.connections[self.endAction.connection.id] = newCId
        self.endAction.connection.id = newCId

        oldSourceId = self.endAction.connection.sourceId
        oldDestId = self.endAction.connection.destinationId
        self.endAction.connection.sourceId = self.macro.modules[oldSourceId]
        self.endAction.connection.destinationId = self.macro.modules[oldDestId]
        if self.endAction.connection.type == VistrailModuleType.Object:
            self.endAction.connection.objectType = pipeline.getModuleById(self.endAction.connection.sourceId).name

    def info(self):
        return [self.endAction.type, self.sourceName, self.destName]

    def moduleReferenced(self,id):
        if id in [self.sourceId, self.destId]:
            return True
        else:
            return False
    
    def verifyNumModules(self):
        return True

    def checkDependencies(self, dict, force=True):
        if self.sourceType == VisMacroActionElement.Internal:
            a1 = self.macro.getAction('AddModule', self.sourceId, self)
            if a1 != -1:
                if dict.has_key(a1):
                    d1 = dict[a1]
                else:
                    d1 = self.macro.actions[a1].checkDependencies(dict, force)
            else:
                if force:
                    self.enabled = False
                    return True
                else:
                    dict[self.baseAction.timestep] = False
                return False
        else:
            d1 = True #considering external actions valid

        if self.destType == VisMacroActionElement.Internal:
            a2 = self.macro.getAction('AddModule', self.destId, self)
            if a2 != -1:
                if dict.has_key(a2):
                    d2 = dict[a2]
                else:
                    d2 = self.macro.actions[a2].checkDependencies(dict, force)
            else:
                if force:
                    self.enabled = False
                    return True
                else:
                    dict[self.baseAction.timestep] = False
                return False
        else:
            d2 = True #considering external actions valid

        if force:
            if not (d1 and d2):
                self.enabled = False
                return True
        dict[self.baseAction.timestep] = d1 and d2
        return d1 and d2

    def getId(self):
        return [self.endAction.connection.id]
 
class VisMacroActionChangeParameter(VisMacroAction):
    __fields__ = ['functions']
    def __init__(self, action, macro):
        VisMacroAction.__init__(self, action, macro)
        self.endAction = ChangeParameterAction()
        self.endAction.parameters = copy.deepcopy(action.parameters)
        self.functions = []
        for p in self.endAction.parameters:
            if not self.macro.modules.has_key(p[0]):
                self.macro.modules[p[0]] = None
                self.macro.extModules.append(p[0])
            if self.macro.pipeline:
                m = self.macro.pipeline.getModuleById(p[0])
                self.sourceId = p[0]
                self.sourceName = m.name
                if m.id in self.macro.extModules:
                    self.sourceType = VisMacroActionElement.External
                else:
                    self.sourceType = VisMacroActionElement.Internal
                if not p[2] in self.functions:
                    self.functions.append(p[2])

    def connReferenced(self,id):
        return False
                        
    def generate(self, pipeline):
        for p in self.endAction.parameters:
            p[0] = self.macro.modules[p[0]]

    def info(self):
        return [self.endAction.type, self.sourceName]

    def moduleReferenced(self,id):
        if self.sourceId == id:
            return True
        else:
            return False
    
    def verifyNumModules(self):
        modules = []
        for p in self.endAction.parameters:
            if not p[0] in modules and len(modules) == 0:
                modules.append(p[0])
            elif not p[0] in modules and len(modules) > 0:
                return False
        return True

    def checkDependencies(self, dict, force=True):
        if self.sourceType == VisMacroActionElement.Internal:
            modules = {}
            for p in self.endAction.parameters:
                if not modules.has_key(p[0]):
                    a = self.macro.getAction('AddModule', p[0], self)
                    if a != -1:
                        if dict.has_key(a):
                            modules[p[0]] = dict[a]
                        else:
                            modules[p[0]] = self.macro.actions[a].checkDependencies(dict, force)
                        if modules[p[0]] == False:
                            if force:
                                self.enabled = False
                                return True
                            else:
                                dict[self.baseAction.timestep] = False
                            return False
                    else:
                        if force:
                            self.enabled = False
                            return True
                        else:
                            dict[self.baseAction.timestep] = False
                        return False
            #if we get here all modules were found
            dict[self.baseAction.timestep] = True
            return True
        else:
            #not checking external actions
            dict[self.baseAction.timestep] = True
            return True

    def getId(self):
        result = []
        for p in self.endAction.parameters:
            result.append([p[0],p[1]])
        return result

class VisMacroActionDeleteModule(VisMacroAction):
    def __init__(self, action, macro):
        VisMacroAction.__init__(self, action, macro)
        self.endAction = DeleteModuleAction()
        self.endAction.ids = copy.deepcopy(action.ids)

        #The module is already deleted in the current pipeline
        #We need to get the pipeline just before deletion
        pipeline = self.macro.getPipeline(action.parent)

        for id in self.endAction.ids: 
            if pipeline:
                m = pipeline.getModuleById(id)
                self.sourceName = m.name
                self.sourceId = id
            if not self.macro.modules.has_key(id):
                self.macro.modules[id] = None
                self.macro.extModules.append(id)

            if id in self.macro.extModules:
                self.sourceType = VisMacroActionElement.External
            else:
                self.sourceType = VisMacroActionElement.Internal
            
    def connReferenced(self,id):
        return False
    
    def generate(self, pipeline):
        for id in self.endAction.ids:
            id = self.macro.modules[id]

    def info(self):
        return [self.endAction.type, self.sourceName]

    def moduleReferenced(self,id):
        if id in self.endAction.ids:
            return True
        else:
            return False

    def verifyNumModules(self):
        if len(self.endAction.ids) > 1:
            return False
        else:
            return True

    def checkDependencies(self, dict, force=True):
        if self.sourceType == VisMacroActionElement.Internal:
            modules = {}
            for m in self.endAction.ids:
                if not modules.has_key(m):
                    a = self.macro.getAction('AddModule', m, self)
                    if a != -1:
                        if dict.has_key(a):
                            modules[m] = dict[a]
                        else:
                            modules[m] = self.macro.actions[a].checkDependencies(dict, force)
                        if modules[m] == False:
                            if force:
                                self.enabled = False
                                return True
                            else:
                                dict[self.baseAction.timestep] = False
                            return False
                    else:
                        if force:
                            self.enabled = False
                            return True
                        else:
                            dict[self.baseAction.timestep] = False
                        return False
            #if we get here all modules were found
            dict[self.baseAction.timestep] = True
            return True
        else:
            #not checking external actions
            dict[self.baseAction.timestep] = True
            return True

    def getId(self):
        return self.ids

class VisMacroActionDeleteConnection(VisMacroAction):
    def __init__(self, action, macro):
        VisMacroAction.__init__(self, action, macro)
        self.endAction = DeleteConnectionAction()
        
        self.endAction.ids = copy.deepcopy(action.ids)

        #The connection is already deleted in the current pipeline
        #We need to get the pipeline just before deletion
        pipeline = self.macro.getPipeline(action.parent)
  
        for id in self.endAction.ids:
            self.id = id
            if pipeline:
                c = pipeline.getConnectionById(id)
                self.sourceId = c.sourceId
                self.destId = c.destinationId
                
                #getting information about the modules involved in the connection
                m1  = pipeline.getModuleById(self.sourceId)
                m2  = pipeline.getModuleById(self.destId)
                self.sourceName = m1.name
                self.destName = m2.name
            
            if not self.macro.connections.has_key(id):
                self.macro.connections[id] = None
                self.macro.extConnections.append(id)

            if id in self.macro.extConnections:
                self.sourceType = VisMacroActionElement.External
            else:
                self.sourceType = VisMacroActionElement.Internal

    def connReferenced(self,id):
        if id in self.endAction.ids:
            return True
        else:
            return False
                    
    def generate(self, pipeline):
        for id in self.endAction.ids:
            id = self.macro.connections[id]

    def info(self):
        return [self.endAction.type, self.sourceName, self.destName]

    def moduleReferenced(self,id):
          return False
    
    def verifyNumModules(self):
        if len(self.endAction.ids) > 1:
            return False
        else:
            return True
    
    def checkDependencies(self, dict, force=True):
        if self.sourceType == VisMacroActionElement.Internal:
            conns = {}
            for id in self.endAction.ids:
                if not conns.has_key(id):
                    a = self.macro.getAction('AddConnection', id, self)
                    if a != -1:
                        if dict.has_key(a):
                            conns[id] = dict[a]
                        else:
                            conns[id] = self.macro.actions[a].checkDependencies(dict, force)
                        if conns[id] == False:
                            if force:
                                self.enabled = False
                                return True
                            else:
                                dict[self.baseAction.timestep] = False
                            return False
                    else:
                        if force:
                            self.enabled = False
                            return True
                        else:
                            dict[self.baseAction.timestep] = False
                        return False
            #if we get here all modules were found
            dict[self.baseAction.timestep] = True
            return True
        else:
            #not checking external actions
            dict[self.baseAction.timestep] = True
            return True

    def getId(self):
        return self.endAction.ids

class VisMacroActionMoveModule(VisMacroAction):
    def __init__(self, action, macro):
        VisMacroAction.__init__(self, action, macro)
        self.endAction = MoveModuleAction()
        self.endAction.moves = copy.deepcopy(action.moves)
        for move in self.endAction.moves:
            self.sourceId = move[0]
            if self.macro.pipeline:
                m = self.macro.pipeline.getModuleById(move[0])
                self.sourceName = m.name
            if not self.macro.modules.has_key(move[0]):
               self.macro.modules[move[0]] = None
               self.macro.extModules.append(move[0])

            if move[0] in self.macro.extModules:
                self.sourceType = VisMacroActionElement.External
            else:
                self.sourceType = VisMacroActionElement.Internal

    def connReferenced(self,id):
        return False

    def generate(self, pipeline):
        for i in range(len(self.endAction.moves)):
            (id,x,y) = self.endAction.moves[i]
            self.endAction.moves.pop(i)
            id = self.macro.modules[id]
            self.endAction.moves.insert(i,(id,x,y))

    def info(self):
        return [self.endAction.type, self.sourceName]

    def moduleReferenced(self,id):
        for move in self.endAction.moves:
            if id == move[0]:
                return True
        return False

    def verifyNumModules(self):
        modules = []
        for move in self.endAction.moves:
            if not move[0] in modules and len(modules) == 0:
                modules.append(move[0])
            elif not move[0] in modules and len(modules) > 0:
                return False
        return True

    def checkDependencies(self, dict, force=True):
        if self.sourceType == VisMacroActionElement.Internal:
            modules = {}
            for m in self.endAction.moves:
                if not modules.has_key(m[0]):
                    a = self.macro.getAction('AddModule', m[0], self)
                    if a != -1:
                        if dict.has_key(a):
                            modules[m[0]] = dict[a]
                        else:
                            modules[m[0]] = self.macro.actions[a].checkDependencies(dict, force)
                        if modules[m[0]] == False:
                            if force:
                                self.enabled = False
                                return True
                            else:
                                dict[self.baseAction.timestep] = False
                            return False
                    else:
                        if force:
                            self.enabled = False
                            return True
                        else:
                            dict[self.baseAction.timestep] = False
                        return False
            #if we get here all modules were found
            dict[self.baseAction.timestep] = True
            return True
        else:
            #not checking external actions
            dict[self.baseAction.timestep] = True
            return True

    def getId(self):
        result = []
        for move in self.endAction.moves:
            result.append(move[0])
        return result
                                           
class VisMacroActionDeleteFunction(VisMacroAction):
    def __init__(self, action, macro):
        VisMacroAction.__init__(self, action, macro)
        self.endAction = DeleteFunctionAction()
        self.endAction.moduleId = action.moduleId
        self.endAction.functionId = action.functionId
        self.sourceId = self.endAction.moduleId
        if not self.macro.modules.has_key(self.endAction.moduleId):
            self.macro.modules[self.endAction.moduleId] = None
            self.macro.extModules.append(self.endAction.moduleId)
                
        if self.macro.pipeline:
            m = self.macro.pipeline.getModulebyId(self.endAction.moduleId)
            self.sourceName = m.name + '.' + m.functions[self.endAction.functionId].name

            if m.id in self.macro.extModules:
                self.sourceType = VisMacroActionElement.External
            else:
                self.sourceType = VisMacroActionElement.Internal

    def connReferenced(self,id):
        return False

    def generate(self, pipeline):
        self.endAction.moduleId = self.macro.modules[self.endAction.moduleId]

    def info(self):
        return [self.endAction.type, self.sourceName]

    def moduleReferenced(self,id):
        if id == self.sourceId:
            return True
        else:
            return False

    def verifyNumModules(self):
        return True

    def checkDependencies(self, dict, force=True):
        if self.sourceType == VisMacroActionElement.Internal:
            a = self.macro.getAction('ChangeParameter', 
                                     [self.sourceId, self.endAction.functionId], self)
            if a != -1:
                if dict.has_key(a):
                    modules[p[0]] = dict[a]
                else:
                    modules[p[0]] = self.macro.actions[a].checkDependencies(dict, force)
                    if modules[p[0]] == False:
                        if force:
                            self.enabled = False
                            return True
                        else:
                            dict[self.baseAction.timestep] = False
                        return False
            else:
                if force:
                    self.enabled = False
                    return True
                else:
                    dict[self.baseAction.timestep] = False
                return False
            #if we get here all modules were found
            dict[self.baseAction.timestep] = True
            return True
        else:
            #not checking external actions
            dict[self.baseAction.timestep] = True
            return True

    def getId(self):
        result = [[self.sourceId, self.endAction.functionId]]

############################################################################
### Exception Classes
        
class ExternalModuleNotSet(Exception):
    def __str__(self):
        return "You need to set all the external references inside the macro before applying it."
    pass

class InvalidActionFound(Exception):
    def __str__(self):
        return "This macro has actions which depend on actions that won't be played. \
                Please disable these actions or include the other required actions."  
    pass
        
#############################################################################

import unittest

class TestVisMacro(unittest.TestCase):
    def test1(self):
        import vistrail
        import xml_parser
        parser = xml_parser.XMLParser()
        parser.openVistrail('tests/mounthood.xml')
        v = parser.getVistrail()
        parser.closeVistrail()
        v.serialize('tests/mounthood_out.xml')

    def testDependencies(self):
        import vistrail
        import xml_parser
        parser = xml_parser.XMLParser()
        parser.openVistrail('test_files/head_macro.xml')
        v = parser.getVistrail()
        parser.closeVistrail()

if __name__ == '__main__':
    unittest.main()

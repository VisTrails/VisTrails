""" This module defines the following classes:
 - MacroAction
 - MacroActionAddModule
 - MacroActionElement

"""
import copy
from PyQt4 import QtCore, QtGui
from core.utils import enum

###############################################################################

MacroActionElement = enum('MacroActionElement',
                       ['Undefined', 'Internal', 'External'])            

class MacroAction(QtCore.QObject, object):
    """ Abstract class that defines an interface to a Macro Action.
    It encapsulates a Vistrail Action adding new behavior. """

    createDispatch = {}
    __fields__ = [ 'baseAction', 'macro', 'endAction', 
                   'sourceName', 'sourceType', 'sourceId']
    
    def _set_enabled(self, value):
        """ _set_enabled(value:boolean) -> None
        if value is True, this action is going to be used when macro is applied
        This method will emit a signal, so the GUI can update the status of 
        this action immediately. Instead of calling this method directly, use
        the enabled property.

        Do not call this from the GUI, setEnabled should be used so as to 
        avoid a loop of signals.
        
        """
        if value != self.__enabled:
            self.__enabled = value
            self.emit(QtCore.SIGNAL("enabledChanged"), 
                      self.baseAction.timestep, value)
    
    def _get_enabled(self):
        return self.__enabled
    
    enabled = property(_get_enabled, _set_enabled)
     
    def setEnabled(self, value):
        """ setEnabled(value:boolean) -> None 
        Same as _set_enabled but does not generate a signal.
        
        """
        self.__enabled = value

    @staticmethod
    def create(action, macro):
        """ create(action, macro) -> MacroAction 
        Static method that creates a MacroAction according to 
        action.type 

        """
        if action.type is 'AddModule':
            return MacroActionAddModule(action,macro)
        elif action.type is 'AddConnection':
            return MacroActionAddConnection(action,macro)
        elif action.type is 'ChangeParameter':
            return MacroActionChangeParameter(action,macro)
        elif action.type is 'DeleteModule':
            return MacroActionDeleteModule(action,macro)
        elif action.type is 'DeleteConnection':
            return MacroActionDeleteConnection(action,macro)
        elif action.type is  'MoveModule':
            return MacroActionMoveModule(action,macro)
        elif action.type is 'DeleteFunction':
            return MacroActionDeleteFunction(action,macro)
    
    def __init__(self, action, macro):
        """ __init__(action,macro) -> MacroAction 
        MacroAction constructor. """
        QtCore.QObject.__init__(self)
        self.baseAction = action
        self.macro = macro
        self.endAction = None
        self.__enabled = True
        self.sourceName = ''
        self.sourceType = MacroActionElement.Undefined
        self.sourceId = -1
        
    def generate(self, pipeline):
        """  generate(pipeline) -> None
        Abstract method that generates a corresponding Vistrail Action 
        obtaining the required information from pipeline. 
         
        """
        abstract()

    def info(self):
        """ info() -> list 
        Abstract method that returns information about an action 
        
        """
        abstract()
        
    def verifyNumModules(self):
        """ verifyNumModules() -> boolean
        Abstract method that returns True if the action refers to only one 
        module. This is because there are actions that can delete many modules
        at once, for example and the interface can not handle that. 
        
        """
        abstract()

    def moduleReferenced(self,id):
        """ moduleReferenced(id) -> boolean 
        Abstract method that returns True if module id is being referenced 
        inside this action. 
         
        """
        abstract()

    def connReferenced(self,id):
        """ connReferenced(id) -> boolean 
        Abstract method that checks if connection id is being referenced 
        by the action.

        """
        abstract()
        
    def checkDependencies(self, dict, force=True):
        """ checkDependencies(dict, force=True) -> boolean 
        Abstract method that check action dependecies and insert itself in dict
        dict[timestep] = result (True or False)
        If force == True, and result is false, the correspondent 
        action is marked disabled.
         
        """
        abstract()

    def getId(self):
        """ getId() -> list 
        Abstract method that returns a list of related module/connection ids
        For example, AddModule -> [moduleId], 
        AddConnection -> [connection.id]

        """
        abstract()

###############################################################################

class MacroActionAddModule(MacroAction):
    """ Class that wraps AddModuleAction """
    def __init__(self, action, macro):
        MacroAction.__init__(self, action, macro)
        self.endAction = AddModuleAction()
        self.endAction.module = copy.copy(action.module)
        self.macro.modules[self.endAction.module.id] = None
        self.sourceId = self.endAction.module.id
        self.sourceName = self.baseAction.module.name
        self.sourceType = MacroActionElement.Internal

    def connReferenced(self,id):
        """ connReferenced(id) -> False 
        Checks if connection id is being referenced by the action. As this is
        an MacroActionAddModule, it will always return False.

        """
        return False

    def generate(self, pipeline):
        """  generate(pipeline) -> None
        Generates a corresponding Vistrail AddModuleAction needing the 
        pipeline to obtain a fresh Module id. 
         
        """
        newId = pipeline.freshModuleId()
        self.macro.modules[self.endAction.module.id] = newId
        self.endAction.module.id = newId
        self.endAction.module.center = self.macro.startPos + Point(-20,-100)
        self.macro.startPos = self.endAction.module.center

    def info(self):
        """ info() -> [Action.type:str, name:str]
        Method that returns a list containing the action type and the name 
        of the module it refers to.
        
        """
        return [self.endAction.type, self.sourceName]

    def moduleReferenced(self,id):
        """ moduleReferenced(id) -> boolean 
        Returns True if module id is being referenced inside this action. 

        """ 
        if self.sourceId == id:
            return True
        else:
            return False

    def verifyNumModules(self):
        """ verifyNumModules() -> boolean
        Returns True if the action refers to only one module. As we can add 
        only one module at a time, it will always return True. 
        
        """
        return True

    def checkDependencies(self, dict, force=True):
        """ checkDependencies(dict, force=True) -> boolean 
        Check action dependecies and insert itself in dict
        dict[timestep] = result (True or False)
        If force == True, and result is false, the correspondent 
        action is marked disabled.
         
        """
        dict[self.baseAction.timestep] = True #no dependencies
        return True

    def getId(self):
        """ getId() -> list 
        Abstract method that returns a list of related module/connection ids
        For example, AddModule -> [moduleId], 
        AddConnection -> [connection.id]

        """
        Return [self.sourceId]

################################################################################

class MacroActionAddConnection(MacroAction):
    """ Class that wraps AddConnectionAction """
    __fields__ = [ 'destName', 'destType', 'destId']
    def __init__(self, action, macro):
        MacroAction.__init__(self, action, macro)
        self.endAction = AddConnectionAction()
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
                self.sourceType = MacroActionElement.External
            else:
                self.sourceType = MacroActionElement.Internal

            if m2.id in self.macro.extModules:
                self.destType = MacroActionElement.External
            else:
                self.destType = MacroActionElement.Internal

    def connReferenced(self,id):
        """ connReferenced(id) -> False 
        Checks if connection id is being referenced by the action. As this will
        always generate a new connection id, it will always return False.

        """
        return False
           
    def generate(self, pipeline):
        """  generate(pipeline) -> None
        Generates a corresponding Vistrail AddConnectionAction needing the 
        pipeline to obtain a fresh connection id.

        """
        newCId = pipeline.freshConnectionId()
        self.macro.connections[self.endAction.connection.id] = newCId
        self.endAction.connection.id = newCId

        oldSourceId = self.endAction.connection.sourceId
        oldDestId = self.endAction.connection.destinationId
        conn = self.endAction.connection
        conn.sourceId = self.macro.modules[oldSourceId]
        conn.destinationId = self.macro.modules[oldDestId]
        if conn.type == VistrailModuleType.Object:
            conn.objectType = pipeline.getModuleById(conn.sourceId).name

    def info(self):
        """ info() -> [Action.type: str, sourcename:str, destname: str ] 
        Returns a list containing the action type, the name of the source 
        module and the name of the destination module.
        
        """
        return [self.endAction.type, self.sourceName, self.destName]

    def moduleReferenced(self,id):
        """ moduleReferenced(id) -> boolean 
        Returns True if module id is being referenced inside this action. 

        """
        if id in [self.sourceId, self.destId]:
            return True
        else:
            return False
    
    def verifyNumModules(self):
        """ verifyNumModules() -> boolean
        Returns True if the action refers to only one module. As we can add 
        only one connection at a time, it will always return True. 
        
        """
        return True

    def checkDependencies(self, dict, force=True):
        """ checkDependencies(dict, force=True) -> boolean 
        Check action dependecies and insert itself in dict
        dict[timestep] = result (True or False)
        If force == True, and result is false, the correspondent 
        action is marked disabled.
        The dependencies for an AddConnectionAction are the two
        AddModuleActions of source and destination.
        
        """
        if self.sourceType == MacroActionElement.Internal:
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

        if self.destType == MacroActionElement.Internal:
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
        """ getId() -> list 
        Method that returns a list of related module/connection ids
        For example, AddModule -> [moduleId], 
        AddConnection -> [connection.id]

        """
        return [self.endAction.connection.id]

###############################################################################
 
class MacroActionChangeParameter(MacroAction):
    """ Class that wraps ChangeParameterAction """
    __fields__ = ['functions']
    def __init__(self, action, macro):
        MacroAction.__init__(self, action, macro)
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
                    self.sourceType = MacroActionElement.External
                else:
                    self.sourceType = MacroActionElement.Internal
                if not p[2] in self.functions:
                    self.functions.append(p[2])

    def connReferenced(self,id):
        """ connReferenced(id) -> False 
        Checks if connection id is being referenced by the action. As this is
        an MacroActionChangeParameter, it will always return False.

        """
        return False
                        
    def generate(self, pipeline):
        """  generate(pipeline) -> None
        Generates a corresponding Vistrail ChangeParameterAction. 

        """

        for p in self.endAction.parameters:
            p[0] = self.macro.modules[p[0]]

    def info(self):
        """ info() -> [Action.type:str, name:str]
        Method that returns a list containing the action type and the name 
        of the module it refers to.
        We consider that ChangeParameter refrerences to one single module.

        """
        return [self.endAction.type, self.sourceName]

    def moduleReferenced(self,id):
        """ moduleReferenced(id) -> boolean 
        Returns True if module id is being referenced inside this action. 

        """
        if self.sourceId == id:
            return True
        else:
            return False
    
    def verifyNumModules(self):
        """ verifyNumModules() -> boolean
        Returns True if the action refers to only one module.  
        
        """
        modules = []
        for p in self.endAction.parameters:
            if not p[0] in modules and len(modules) == 0:
                modules.append(p[0])
            elif not p[0] in modules and len(modules) > 0:
                return False
        return True

    def checkDependencies(self, dict, force=True):
        """ checkDependencies(dict, force=True) -> boolean 
        Abstract method that check action dependecies and insert itself in dict
        dict[timestep] = result (True or False)
        If force == True, and result is false, the correspondent 
        action is marked disabled.
        The dependency for a ChangeParameterAction is AddModule for each
        parameter.

        """
        if self.sourceType == MacroActionElement.Internal:
            modules = {}
            for p in self.endAction.parameters:
                m = p[0]
                if not modules.has_key(m):
                    a = self.macro.getAction('AddModule', m, self)
                    if a != -1:
                        if dict.has_key(a):
                            modules[m] = dict[a]
                        else:
                            action = self.macro.actions[a]
                            modules[m] = action.checkDependencies(dict, force)
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
        """ getId() -> [module_id : int, function_id : int]  
        Returns a list of related module and function ids
        
        """
        result = []
        for p in self.endAction.parameters:
            result.append([p[0],p[1]])
        return result

################################################################################

class MacroActionDeleteModule(MacroAction):
     """ Class that wraps DeleteModuleAction """
     def __init__(self, action, macro):
         MacroAction.__init__(self, action, macro)
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
                 self.sourceType = MacroActionElement.External
             else:
                 self.sourceType = MacroActionElement.Internal
            
     def connReferenced(self,id):
         """ connReferenced(id) -> False 
         Checks if connection id is being referenced by the action. As this is
         an MacroActionDeleteModule, it will always return False.

         """
         return False
    
     def generate(self, pipeline):
         """  generate(pipeline) -> None
         Generates a corresponding Vistrail DeleteModuleAction. 

         """       
         for id in self.endAction.ids:
             id = self.macro.modules[id]

     def info(self):
         """ info() -> [Action.type:str, name:str]
         Method that returns a list containing the action type and the name 
         of the module it refers to.
         We consider only the first module in the list.

         """
         return [self.endAction.type, self.sourceName]

     def moduleReferenced(self,id):
         """ moduleReferenced(id) -> boolean 
         Returns True if module id is being referenced inside this action. 

         """
         if id in self.endAction.ids:
             return True
         else:
             return False

     def verifyNumModules(self):
         """ verifyNumModules() -> boolean
         Returns True if the action refers to only one module.  
         
         """
         if len(self.endAction.ids) > 1:
             return False
         else:
             return True

     def checkDependencies(self, dict, force=True):
         """ checkDependencies(dict, force=True) -> boolean 
         Abstract method that check action dependecies and insert itself in dict
         dict[timestep] = result (True or False)
         If force == True, and result is false, the correspondent 
         action is marked disabled.
         The dependency for a ChangeParameterAction is AddModule for each
         module id in its list.

         """
         if self.sourceType == MacroActionElement.Internal:
             modules = {}
             for m in self.endAction.ids:
                 if not modules.has_key(m):
                     a = self.macro.getAction('AddModule', m, self)
                     if a != -1:
                         if dict.has_key(a):
                             modules[m] = dict[a]
                         else:
                             act = self.macro.actions[a]
                             modules[m] = act.checkDependencies(dict, force)
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
         """ getId() -> [module_id : int]  
         Returns a list of related module ids
        
         """
         return self.ids

################################################################################

class MacroActionDeleteConnection(MacroAction):
    def __init__(self, action, macro):
        MacroAction.__init__(self, action, macro)
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
                self.sourceType = MacroActionElement.External
            else:
                self.sourceType = MacroActionElement.Internal

    def connReferenced(self,id):
        """ connReferenced(id) -> boolean 
        Checks if connection id is being referenced by the action.

        """
        if id in self.endAction.ids:
            return True
        else:
            return False
                    
    def generate(self, pipeline):
        """  generate(pipeline) -> None
        Generates a corresponding Vistrail DeleteConnectionAction.

        """
        for id in self.endAction.ids:
            id = self.macro.connections[id]

    def info(self):
        """ info() -> [Action.type: str, sourcename:str, destname: str ] 
        Returns a list containing the action type, the name of the source 
        module and the name of the destination module.
        
        """
        return [self.endAction.type, self.sourceName, self.destName]

    def moduleReferenced(self,id):
        """ moduleReferenced(id) -> boolean 
        Returns True if module id is being referenced inside this action. 

        """
        return False
    
    def verifyNumModules(self):
        """ verifyNumModules() -> boolean
        Returns True if the action refers to only one module.  
        
        """
        if len(self.endAction.ids) > 1:
            return False
        else:
            return True
    
    def checkDependencies(self, dict, force=True):
        """ checkDependencies(dict, force=True) -> boolean 
        Abstract method that check action dependecies and insert itself in dict
        dict[timestep] = result (True or False)
        If force == True, and result is false, the correspondent 
        action is marked disabled.
        The dependency for a DeleteConnectionAction is AddConnection for each
        id in its list.

        """
        if self.sourceType == MacroActionElement.Internal:
            conns = {}
            for id in self.endAction.ids:
                if not conns.has_key(id):
                    a = self.macro.getAction('AddConnection', id, self)
                    if a != -1:
                        if dict.has_key(a):
                            conns[id] = dict[a]
                        else:
                            act = self.macro.actions[a]
                            conns[id] = act.checkDependencies(dict, force)
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
        """ getId() -> [connection_id : int]  
        Returns a list of related connection ids
        
        """
        return self.endAction.ids

################################################################################

class MacroActionMoveModule(MacroAction):
    def __init__(self, action, macro):
        MacroAction.__init__(self, action, macro)
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
                self.sourceType = MacroActionElement.External
            else:
                self.sourceType = MacroActionElement.Internal

    def connReferenced(self,id):
        """ connReferenced(id) -> False 
        Checks if connection id is being referenced by the action. As this is
        an MacroActionMoveModule, it will always return False.

        """
        return False

    def generate(self, pipeline):
        """  generate(pipeline) -> None
        Generates a corresponding Vistrail MoveModuleAction.

        """
        for i in range(len(self.endAction.moves)):
            (id,x,y) = self.endAction.moves[i]
            self.endAction.moves.pop(i)
            id = self.macro.modules[id]
            self.endAction.moves.insert(i,(id,x,y))

    def info(self):
        """ info() -> [Action.type:str, name:str]
        Method that returns a list containing the action type and the name 
        of the module it refers to.
        We consider only the first moduleof the list.

        """
        return [self.endAction.type, self.sourceName]

    def moduleReferenced(self,id):
        """ moduleReferenced(id) -> boolean 
        Returns True if module id is being referenced inside this action. 

        """
        for move in self.endAction.moves:
            if id == move[0]:
                return True
        return False

    def verifyNumModules(self):
        """ verifyNumModules() -> boolean
        Returns True if the action refers to only one module.  
        
        """
        modules = []
        for move in self.endAction.moves:
            if not move[0] in modules and len(modules) == 0:
                modules.append(move[0])
            elif not move[0] in modules and len(modules) > 0:
                return False
        return True

    def checkDependencies(self, dict, force=True):
        """ checkDependencies(dict, force=True) -> boolean 
        Abstract method that check action dependecies and insert itself in dict
        dict[timestep] = result (True or False)
        If force == True, and result is false, the correspondent 
        action is marked disabled.
        The dependency for a MoveModuleAction is AddModule for each module
        id.

        """
        if self.sourceType == MacroActionElement.Internal:
            modules = {}
            for m in self.endAction.moves:
                if not modules.has_key(m[0]):
                    a = self.macro.getAction('AddModule', m[0], self)
                    if a != -1:
                        if dict.has_key(a):
                            modules[m[0]] = dict[a]
                        else:
                            act = self.macro.actions[a]
                            modules[m[0]] = act.checkDependencies(dict, force)
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

################################################################################

class MacroActionDeleteFunction(MacroAction):
    """ Class that wraps DeleteFunctionAction """
    def __init__(self, action, macro):
        MacroAction.__init__(self, action, macro)
        self.endAction = DeleteFunctionAction()
        self.endAction.moduleId = action.moduleId
        self.endAction.functionId = action.functionId
        self.sourceId = self.endAction.moduleId
        if not self.macro.modules.has_key(self.endAction.moduleId):
            self.macro.modules[self.endAction.moduleId] = None
            self.macro.extModules.append(self.endAction.moduleId)
                
        if self.macro.pipeline:
            eAct = self.endAction
            m = self.macro.pipeline.getModulebyId(eAct.moduleId)
            self.sourceName = m.name + '.' + m.functions[eAct.functionId].name

            if m.id in self.macro.extModules:
                self.sourceType = MacroActionElement.External
            else:
                self.sourceType = MacroActionElement.Internal

    def connReferenced(self,id):
        """ connReferenced(id) -> False 
        Checks if connection id is being referenced by the action. As this is
        an MacroActionDeleteFunction, it will always return False.

        """
        return False

    def generate(self, pipeline):
        """  generate(pipeline) -> None
        Generates a corresponding Vistrail DeleteFunctionAction. 

        """
        self.endAction.moduleId = self.macro.modules[self.endAction.moduleId]

    def info(self):
        """ info() -> [Action.type:str, name:str]
        Method that returns a list containing the action type and the name 
        of the module it refers to.
        
        """
        return [self.endAction.type, self.sourceName]

    def moduleReferenced(self,id):
        """ moduleReferenced(id) -> boolean 
        Returns True if module id is being referenced inside this action. 

        """
        if id == self.sourceId:
            return True
        else:
            return False

    def verifyNumModules(self):
        """ verifyNumModules() -> boolean
        Returns True if the action refers to only one module. As we can add 
        only one connection at a time, it will always return True. 
        
        """
        return True

    def checkDependencies(self, dict, force=True):
        """ checkDependencies(dict, force=True) -> boolean 
        Check action dependecies and insert itself in dict
        dict[timestep] = result (True or False)
        If force == True, and result is false, the correspondent 
        action is marked disabled.
        The dependency for a DeleteFunctionAction is one ChangeParameterAction.
        
        """
        if self.sourceType == MacroActionElement.Internal:
            a = self.macro.getAction('ChangeParameter', 
                                     [self.sourceId, 
                                      self.endAction.functionId], self)
            if a != -1:
                if dict.has_key(a):
                    modules[p[0]] = dict[a]
                else:
                    act = self.macro.actions[a]
                    modules[p[0]] = act.checkDependencies(dict, force)
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
        """ getId() -> [module_id : int, function_id : int]  
        Returns a list of related module and function ids
        
        """
        result = [[self.sourceId, self.endAction.functionId]]

###############################################################################

#TODO Add Test Cases

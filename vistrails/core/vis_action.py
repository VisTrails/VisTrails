from core.common import abstract, VistrailsInternalError
from core.xml_utils import *
from core.vis_object import VisModule
from core.vis_connection import VisConnection
from core.vis_types import *
from core.data_structures import Point
from core.modules.module_registry import registry, ModuleRegistry
import copy

################################################################################

class VisAction(object):
    """ Base class for a Vis Action.

    A Vistrail action needs to know three things, behavior-wise: 

   - how to perform (that is, how to change a certain pipeline) 

   - how to serialize (that is, given an XML parent element,
     how to add itself to it)

   - how to parse (that is, given an XML parent element, how to
     extract the action information
     
     """
    createFromXMLDispatch = {}
    
    def __init__(self,timestep=0,parent=0,date=None,user=None,notes=None):
        self.timestep = timestep
        self.parent = parent
	self.date = date
	self.user = user
        self.notes = notes

    def perform(self, pipeline):
        abstract()

    def serialize(self,dom,element):
        abstract()

    def writeToDB(self):
	abstract()

    def __str__(self):
        return "<<timestep='%s' parent='%s' date='%s' user='%s' notes='%s'>>" % (self.timestep,
                                                                      self.parent,
                                                                      self.date,
                                                                      self.user,
								      self.notes)

    @staticmethod
    def createFromXML(action, version=None):
        att = action.getAttribute('what')
        return VisAction.createFromXMLDispatch[att](action,version)
       
    @staticmethod
    def getParameter(element):
        p = ModuleParam()
        p.name = element.getAttribute('name')
        p.type = str(named_elements(element, 'type').next().firstChild.nodeValue)
        p.strValue = str(named_elements(element, 'val').next().firstChild.nodeValue)
        return p
    
    @staticmethod
    def getFunction(element):
        f = ModuleFunction()
        (f.name, f.returnType) = [str(element.getAttribute(x))
                            for x in ['name', 'returnType']]
        f.params = [VisAction.getParameter(param) for
                    param in named_elements(element, 'param')]
        return f

    @staticmethod
    def getModule(element):
        m = VisModule()
        (m.name, cache, id, x, y) = [str(element.getAttribute(x))
                                     for x in ['name', 'cache', 'id',
                                               'x', 'y']]
        m.cache = int(cache)
        m.id = int(id)
        m.center.x = float(x)
        m.center.y = float(y)
        m.functions = [VisAction.getFunction(f) for
                       f in named_elements(element, 'function')]
        m.annotations = {}
        for a in named_elements(element, 'annotation'):
            m.annotation[str(a.getAttribute('key'))] = str(a.getAttribute('value'))
        return m

    @staticmethod
    def getConnection(connection):
        c = VisConnection()
        sourceModule = connection.getAttribute('sourceModule')
        destinationModule = connection.getAttribute('destinationModule')
        sourcePort = connection.getAttribute('sourcePort')
        destinationPort = connection.getAttribute('destinationPort')
        # Leaving this to performing actions to get modules registry
        c.source = registry.portFromRepresentation(sourceModule,
                                                  sourcePort,
                                                  VisPortEndPoint.Source,
                                                  None, True)
        c.destination = registry.portFromRepresentation(destinationModule,
                                                       destinationPort,
                                                       VisPortEndPoint.Destination,
                                                       None, True)
        c.sourceInfo = (sourceModule, sourcePort)
        c.destinationInfo = (destinationModule, destinationPort)
        c.id = int(connection.getAttribute('id'))
        c.type = VistrailModuleType.Module
        c.sourceId = int(connection.getAttribute('sourceId'))
        c.destinationId = int(connection.getAttribute('destinationId'))
        return c
    
    @staticmethod
    def getConnection0_1_0(connection):
        cId = int(connection.getAttribute('id'))
        for f in named_elements(connection, 'filterInput'):
	    c = VisConnection()
	    c.source = VisPort()
	    c.destination = VisPort()
	   	
	    c.source.endPoint = VisPortEndPoint.Source
	    c.destination.endPoint = VisPortEndPoint.Destination
	    
            (c.sourceId,
             c.destinationId,
             sourcePort,
             destinationPort) = [int(f.getAttribute(x))
                             for x in ['sourceId', 'destId',
                                       'sourcePort', 'destPort']]
	    c.source.moduleId = c.sourceId
	    c.source.name = "GetOutputPort" + str(sourcePort)

	    c.destination.moduleId = c.destinationId
	    c.destination.name = "SetInputConnection" + str(destinationPort)
	    
	    c.id = cId
	    
            return c

        for o in named_elements(connection, 'objectInput'):
            c = VisConnection()
	    c.source = VisPort()
	    c.destination = VisPort()
	   	
	    c.source.endPoint = VisPortEndPoint.Source
	    c.destination.endPoint = VisPortEndPoint.Destination

            (moduleId,
             destId,
             name) = [str(o.getAttribute(x))
                                   for x in ['sourceId', 'destId',
                                             'name']]
	    
	    
	    c.source.moduleId = int(moduleId)
	    c.source.name = 'self'
	    c.destination.moduleId = int(destId)

	    c.destination.name = str(name) 
            c.id = cId
	    c.sourceId = int(moduleId)
            c.destinationId = int(destId)
            return c
        
	raise VistrailsInternalError("element is neither filter nor object")
    
class ImportVistrailAction(VisAction):
    def __init__(self,timestep=0,parent=0,date=None,user=None,notes=None):
        VisAction.__init__(self,timestep,parent,date,user,notes)
        self.modules = []
        self.connections = []
        self.type = 'ImportVistrail'
        
    @staticmethod
    def parse(element, version=None):
	notes = None
	#backwards compatibility
	notes = str(element.getAttribute('notes'))

	for n in element.childNodes:
	    if n.localName == "notes":
		notes = str(n.firstChild.nodeValue)
		break

        newAction = ImportVistrailAction(int(element.getAttribute('time')),
                                         int(element.getAttribute('parent')),
					 str(element.getAttribute('date')),
					 str(element.getAttribute('user')),
                                         notes)
        
        newAction.modules = [VisAction.getModule(obj)
                             for obj in named_elements(element, 'object')]
        newAction.connections = [VisAction.getConnection0_1_0(conn)
                                 for conn in named_elements(element, 'connect')]
        return newAction
      
    def serialize(self, dom, element):
        element.setAttribute('what', 'import')
        for module in self.modules:
            module.serialize(dom, element)
        for conn in self.connections:
            conn.serialize(dom, element)

    def writeToDB(self):
	source = """<action date=\"""" + str(self.date) + """\" parent=\"""" + str(self.parent) + """\" time=\"""" + str(self.timestep) + """\" user=\"""" + str(self.user) + """\" what="import"> <note>""" + str(self.notes) + """</note>"""
	for module in self.modules:
            source = source + module.writeToDB()
        for conn in self.connections:
            source = source + conn.writeToDB()
	    
	source = source + """</action>"""
	return source

    def perform(self, pipeline):
        for module in self.modules:
            pipeline.addModule(copy.copy(module))
        for conn in self.connections:
            pipeline.addConnection(copy.copy(conn))

VisAction.createFromXMLDispatch['import'] = ImportVistrailAction.parse

class AddModuleAction(VisAction):
    def __init__(self, timestep=0,parent=0,date=None,user=None,notes=None):
        VisAction.__init__(self,timestep,parent,date,user,notes)
        self.module = None
        self.type = 'AddModule'
        
    def serialize(self, dom, element):
        element.setAttribute('what', 'addModule')
        self.module.serialize(dom, element)

    def writeToDB(self):
	source = """<action date=\"""" + str(self.date) + """\" parent=\"""" + str(self.parent) + """\" time=\"""" + str(self.timestep) + """\" user=\"""" + str(self.user) + """\" what="addModule"> <note>""" + str(self.notes) + """</note>""" + self.module.writeToDB() + """</action>"""
	#print source
	return source

    @staticmethod
    def parse(element, version=None):
	notes = None
	#backwards compatibility
	notes = str(element.getAttribute('notes'))
	
	for n in element.childNodes:
	    if n.localName == "notes":
		notes = str(n.firstChild.nodeValue)
		break
	    
        newAction = AddModuleAction(int(element.getAttribute('time')),
                                    int(element.getAttribute('parent')),
				    str(element.getAttribute('date')),
				    str(element.getAttribute('user')),
                                    notes)
        for o in named_elements(element, 'object'):
            newAction.module = VisAction.getModule(o)
            return newAction
        raise VistrailsInternalError("No objects in addModule action")
    
    def perform(self, pipeline):
        pipeline.addModule(copy.copy(self.module))

VisAction.createFromXMLDispatch['addModule'] = AddModuleAction.parse

class AddConnectionAction(VisAction):
    def __init__(self,timestep=0,parent=0,date=None,user=None,notes=None):
        VisAction.__init__(self, timestep, parent, date, user,notes)
        self.connection = None
        self.type = 'AddConnection'
        
    def serialize(self, dom, element):
        element.setAttribute('what', 'addConnection')
        self.connection.serialize(dom, element)

    def writeToDB(self):
	source = """<action date=\"""" + str(self.date) + """\" parent=\"""" + str(self.parent) + """\" time=\"""" + str(self.timestep) + """\" user=\"""" + str(self.user) + """\" what="addConnection"> <note>""" + str(self.notes) + """</note>""" + self.connection.writeToDB() + """</action>"""
	return source

    @staticmethod
    def parse(element, version=None):
	notes = None
	#backwards compatibility
	notes = str(element.getAttribute('notes'))

	for n in element.childNodes:
	    if n.localName == "notes":
		notes = str(n.firstChild.nodeValue)
		break

	newAction = AddConnectionAction(int(element.getAttribute('time')),
					int(element.getAttribute('parent')),
					str(element.getAttribute('date')),
					str(element.getAttribute('user')),
					notes)
	for c in named_elements(element, 'connect'):
	    if version == '0.1.0':
		newAction.connection = VisAction.getConnection0_1_0(c)
	    else:
		newAction.connection = VisAction.getConnection(c)
	    return newAction
	raise VistrailsInternalError("No connections in addConnection action")
     
    def perform(self, pipeline):
        if hasattr(self.connection, 'sourceInfo'):
            (si, di, cid) = (self.connection.sourceId,
                             self.connection.destinationId,
                             self.connection.id)
            (sourceModuleName, sourcePort) = self.connection.sourceInfo
            (destinationModuleName, destinationPort) = self.connection.destinationInfo
            sourceModule = pipeline.getModuleById(si)
            destinationModule = pipeline.getModuleById(di)
            self.connection.source = registry.portFromRepresentation(sourceModuleName,
                                                                    sourcePort,
                                                                    VisPortEndPoint.Source,
                                                                    sourceModule.registry,
                                                                    False)
            self.connection.destination = registry.portFromRepresentation(destinationModuleName,
                                                                         destinationPort,
                                                                         VisPortEndPoint.Destination,
                                                                         destinationModule.registry,
                                                                         False)
            (self.connection.sourceId,
             self.connection.destinationId,
             self.connection.id) = (si, di, cid)
        pipeline.addConnection(copy.copy(self.connection))

VisAction.createFromXMLDispatch['addConnection'] = AddConnectionAction.parse

class ChangeParameterAction(VisAction):
    attributes = ['moduleId', 'functionId', 'function', 'parameterId',
                  'parameter', 'value', 'type', 'alias']
    conversions = [int, int, str, int, str, str, str, str]

    def __init__(self, timestep=0,parent=0,date=None,user=None,notes=None):
        VisAction.__init__(self, timestep,parent,date,user,notes)
        self.parameters = []
        self.type = 'ChangeParameter'

    def addParameter(self, moduleId, functionId, paramId,
                     function, param, value, type, alias):
        """ Add a new parameter to the action
        Parameters
        ----------

        - moduleId : 'int'

        - functionId : 'int'

        - paramId: 'int'

        - function: 'str'

        - param : 'str'

        - value : 'str'

        - type : 'str'

        """
        p = [moduleId, functionId,function, paramId, param, value, type, alias]
        self.parameters.append(p)

    def writeToDB(self):
	
	temp = ""
	for parameter in self.parameters:
            temp = temp + """<set"""
            for a, v in zip(ChangeParameterAction.attributes, parameter):
                temp = temp + """ """ + a + """=\"""" + str(v) + """\""""
	    temp = temp + """/>"""
	
	source = """<action date=\"""" + str(self.date) + """\" parent=\"""" + str(self.parent) + """\" time=\"""" + str(self.timestep) + """\" user=\"""" + str(self.user) + """\" what="changeParameter"> <note>""" + str(self.notes) + """</note>""" + temp + """</action>"""
	#print source
	return source
     
    def serialize(self, dom, element):
        element.setAttribute('what', 'changeParameter')
        for parameter in self.parameters:
            child = dom.createElement('set')
            for a, v in zip(ChangeParameterAction.attributes, parameter):
                child.setAttribute(a,str(v))
            element.appendChild(child)

    @staticmethod
    def parse(element, version=None):
	notes = None
	#backwards compatibility
	notes = str(element.getAttribute('notes'))

	for n in element.childNodes:
	    if n.localName == "notes":
		notes = str(n.firstChild.nodeValue)
		break

	newAction = ChangeParameterAction(int(element.getAttribute('time')),
                                          int(element.getAttribute('parent')),
					  str(element.getAttribute('date')),
					  str(element.getAttribute('user')),
                                          notes)
	if version == '0.1.0':
	    p = [[conv(set.getAttribute(key))
              for conv,key in zip([int, int, str, int, str, str, str],
                                  ['moduleId', 'functionId', 'function', 'parameterId',
				   'parameter', 'value', 'type'])]
             for set in named_elements(element, 'set')]
	    
	    for par in p:
		if par[6] in ['double','float']:
		    par[6] = 'Float'
		elif par[6] == 'int':
		    par[6] = 'Integer'
		elif par[6] in ['const char *', 'const char*', 'string']:
		    par[6] = 'String'
		par.append("") #alias
	else:
	    p = [[conv(set.getAttribute(key))
		  for conv,key in zip(ChangeParameterAction.conversions,
				      ChangeParameterAction.attributes)]
		 for set in named_elements(element, 'set')]
        
	newAction.parameters = p
        return newAction
      
    def perform(self, pipeline):
        for p in self.parameters:
            m = pipeline.getModuleById(p[0])
            if p[1] >= len(m.functions):
                f = ModuleFunction()
                f.name = p[2]
                m.functions.append(f)
                if len(m.functions)-1 != p[1]:
                    raise VistrailsInternalError("Pipeline function id is inconsistent")
            f = m.functions[p[1]]
            if f.name != p[2]:
                raise VistrailsInternalError("Pipeline function name is inconsistent")
            if p[3] == -1:
                continue
            if p[3] >= len(f.params):
                param = ModuleParam()
                param.name = p[4]
                f.params.append(param)
                if len(f.params)-1 != p[3]:
                    raise VistrailsInternalError("Pipeline parameter id is inconsistent")
            param = f.params[p[3]]
            param.name = p[4]
#            if param.name != p[4]:
#                raise VistrailsInternalError("Pipeline parameter name is inconsistent")
            param.strValue = p[5]
            param.type = p[6]
            if param.type.find('char')>-1 or param.type=='str':
                param.type = 'string'
            param.alias = p[7]

VisAction.createFromXMLDispatch['changeParameter'] = ChangeParameterAction.parse

class DeleteModuleAction(VisAction):
    def __init__(self, timestep=0,parent=0,date=None,user=None,notes=None):
        VisAction.__init__(self, timestep,parent,date,user,notes)
        self.ids = []
        self.type = 'DeleteModule'

    def addId(self, id):
        """  Adds a id module to the list of modules to be deleted
        Parameters
        ----------

        - id : 'int'

        """
        self.ids.append(id)

    def writeToDB(self):
	
	temp = ""
	for id in self.ids:
	    temp = temp + """<module moduleId=\"""" + str(id) + """\"/>"""

	source = """<action date=\"""" + str(self.date) + """\" parent=\"""" + str(self.parent) + """\" time=\"""" + str(self.timestep) + """\" user=\"""" + str(self.user) + """\" what="deleteModule"> <note>""" + str(self.notes) + """</note>""" + temp  + """</action>"""
	return source
        
    def serialize(self, dom, element):
        element.setAttribute('what','deleteModule')
        for id in self.ids:
            child = dom.createElement('module')
            child.setAttribute('moduleId', str(id))
            element.appendChild(child)

    @staticmethod
    def parse(element, version=None):
	notes = None
	#backwards compatibility
	notes = str(element.getAttribute('notes'))
	for n in element.childNodes:
	    if n.localName == "notes":
		notes = str(n.firstChild.nodeValue)
		break

        newAction = DeleteModuleAction(int(element.getAttribute('time')),
                                       int(element.getAttribute('parent')),
				       str(element.getAttribute('date')),
				       str(element.getAttribute('user')),
                                       notes)
        newAction.ids = [int(m.getAttribute('moduleId'))
                    for m in named_elements(element, 'module')]
        return newAction
      
    def perform(self, pipeline):
        for id in self.ids:
            pipeline.deleteModule(id)

VisAction.createFromXMLDispatch['deleteModule'] = DeleteModuleAction.parse

class DeleteConnectionAction(VisAction):
    def __init__(self, timestep=0,parent=0,date=None,user=None,notes=None):
        VisAction.__init__(self, timestep,parent,date,user,notes)
        self.ids = []
        self.type = 'DeleteConnection'
        
    def addId(self, id):
        self.ids.append(id)

    def writeToDB(self):
	
	temp = ""
	for id in self.ids:
	    temp = temp + """<connection connectionId=\"""" + str(id) + """\" />"""

	source = """<action date=\"""" + str(self.date) + """\" parent=\"""" + str(self.parent) + """\" time=\"""" + str(self.timestep) + """\" user=\"""" + str(self.user) + """\" what="deleteConnection"> <note>""" + str(self.notes) + """</note>""" + temp  + """</action>"""
	return source

    def serialize(self, dom, element):
        element.setAttribute('what','deleteConnection')
        for id in self.ids:
            child = dom.createElement('connection')
            child.setAttribute('connectionId', str(id))
            element.appendChild(child)

    @staticmethod
    def parse(element, version=None):
	notes = None
	#backwards compatibility
	notes = str(element.getAttribute('notes'))
	for n in element.childNodes:
	    if n.localName == "notes":
		notes = str(n.firstChild.nodeValue)
		break
	
        newAction = DeleteConnectionAction(int(element.getAttribute('time')),
                                           int(element.getAttribute('parent')),
					   str(element.getAttribute('date')),
					   str(element.getAttribute('user')),
                                           notes)
        newAction.ids = [int(m.getAttribute('connectionId'))
                         for m in named_elements(element, 'connection')]
        return newAction
       
    def perform(self, pipeline):
        for id in self.ids:
            pipeline.deleteConnection(id)

VisAction.createFromXMLDispatch['deleteConnection'] = DeleteConnectionAction.parse

class MoveModuleAction(VisAction):
    def __init__(self, timestep=0,parent=0,date=None,user=None,notes=None):
        VisAction.__init__(self, timestep,parent,date,user,notes)
        self.moves = []
        self.type = 'MoveModule'

    @staticmethod
    def parse(element, version=None):
	notes = None
	#backwards compatibility
	notes = str(element.getAttribute('notes'))

	for n in element.childNodes:
	    if n.localName == "notes":
		notes = str(n.firstChild.nodeValue)
		break

        newAction = MoveModuleAction(int(element.getAttribute('time')),
                                     int(element.getAttribute('parent')),
				     str(element.getAttribute('date')),
				     str(element.getAttribute('user')),
                                     notes)
        newAction.moves = [(int(m.getAttribute('id')),
                            float(m.getAttribute('dx')),
                            float(m.getAttribute('dy')))
                           for m in named_elements(element, 'move')]
        return newAction
  
    def addMove(self, id, dx, dy):
        """ Adds a item to the moves
        
        Parameters
        ----------

        - id : 'int'
        - dx : 'float'
        - dy : 'float'
        
        """
        self.moves.append((id, dx, dy))
        
    def perform(self, pipeline):
        for move in self.moves:
            m = pipeline.getModuleById(move[0])
            m.center.x = m.center.x + move[1]
            m.center.y = m.center.y + move[2]

    def writeToDB(self):
	
	temp = ""
	for move in self.moves:
	    temp = temp + """<move id=\"""" + str(move[0]) + """\" dx=\"""" + str(move[1]) + """\" dy=\"""" + str(move[2]) + """\" />"""

	source = """<action date=\"""" + str(self.date) + """\" parent=\"""" + str(self.parent) + """\" time=\"""" + str(self.timestep) + """\" user=\"""" + str(self.user) + """\" what="moveModule"> <note>""" + str(self.notes) + """</note>""" + temp  + """</action>"""
	return source

    def serialize(self, dom, element):
        element.setAttribute('what', 'moveModule')
        for move in self.moves:
            child = dom.createElement('move')
            child.setAttribute('id', str(move[0]))
            child.setAttribute('dx', str(move[1]))
            child.setAttribute('dy', str(move[2]))
            element.appendChild(child)

VisAction.createFromXMLDispatch['moveModule'] = MoveModuleAction.parse

class DeleteFunctionAction(VisAction):
    def __init__(self, timestep=0,parent=0,date=None,user=None,notes=None):
        VisAction.__init__(self,timestep,parent,date,user,notes)
        self.functionId = -1
        self.moduleId = -1
        self.type = 'DeleteFunction'
        
    def perform(self, pipeline):
        pipeline.getModuleById(self.moduleId).deleteFunction(self.functionId)

    def writeToDB(self):
	source = """<action date=\"""" + str(self.date) + """\" parent=\"""" + str(self.parent) + """\" time=\"""" + str(self.timestep) + """\" user=\"""" + str(self.user) + """\" what="deleteFunction"> <note>""" + str(self.notes) + """</note> <function functionId=\"""" + str(self.functionId) + """\" moduleId=\"""" + str(self.moduleId)  + """\" /> </action>"""
	return source

    def serialize(self, dom, element):
        element.setAttribute('what', 'deleteFunction')
        child = dom.createElement('function')
        child.setAttribute('functionId', str(self.functionId))
        child.setAttribute('moduleId',   str(self.moduleId))
        element.appendChild(child)

    @staticmethod
    def parse(element, version=None):
	notes = None
	#backwards compatibility
	notes = str(element.getAttribute('notes'))
	
	for n in element.childNodes:
	    if n.localName == "notes":
		notes = str(n.firstChild.nodeValue)
		break

	newAction = DeleteFunctionAction(int(element.getAttribute('time')),
                                         int(element.getAttribute('parent')),
					 str(element.getAttribute('date')),
					 str(element.getAttribute('user')),
                                         notes)
        for el in named_elements(element, 'function'):
            newAction.moduleId = int(el.getAttribute('moduleId'))
            newAction.functionId = int(el.getAttribute('functionId'))
            return newAction
 
VisAction.createFromXMLDispatch['deleteFunction'] = DeleteFunctionAction.parse

class ChangeAnnotationAction(VisAction):
    attributes = ['moduleId', 'key', 'value']
    conversions = [int, str, str]

    def __init__(self, timestep=0,parent=0,date=None,user=None,notes=None):
        VisAction.__init__(self, timestep,parent,date,user,notes)
        self.moduleId = -1
        self.type = 'ChangeAnnotation'

    def addAnnotation(self, moduleId, key, value):
        """ Add a new annotation to the action
        Parameters
        ----------

        - moduleId : 'int'

        - key : 'string'

        - value : 'str'

        """
        self.moduleId = moduleId
        self.key = key
        self.value = value

    def writeToDB(self):
	
        temp = ""
        temp = temp + """<set"""
        for a, v in zip(ChangeAnnotationAction.attributes, [self.moduleId, self.key, self.value]):
            temp = temp + """ """ + a + """=\"""" + str(v) + """\""""
        temp = temp + """/>"""
        source =""
        
        source = """<action date=\"""" + str(self.date) + """\" parent=\"""" + str(self.parent) + """\" time=\"""" + str(self.timestep) + """\" user=\"""" + str(self.user) + """\" what="changeAnnotation"> <note>""" + str(self.notes) + """</note>""" + temp + """</action>"""
        return source
     
    def serialize(self, dom, element):
        element.setAttribute('what', 'changeAnnotation')
        child = dom.createElement('set')
        for a, v in zip(ChangeAnnotationAction.attributes, [self.moduleId, self.key, self.value]):
            child.setAttribute(a,str(v))
        element.appendChild(child)

    @staticmethod
    def parse(element, version=None):
	notes = None
	#backwards compatibility
	notes = str(element.getAttribute('notes'))

	for n in element.childNodes:
	    if n.localName == "notes":
		notes = str(n.firstChild.nodeValue)
		break

	newAction = ChangeAnnotationAction(int(element.getAttribute('time')),
                                          int(element.getAttribute('parent')),
					  str(element.getAttribute('date')),
					  str(element.getAttribute('user')),
                                          notes)
        p = [[conv(set.getAttribute(key))
              for conv,key in zip(ChangeAnnotationAction.conversions,
                                  ChangeAnnotationAction.attributes)]
             for set in named_elements(element, 'set')]
        [[newAction.moduleId, newAction.key, newAction.value]] = p
        return newAction
      
    def perform(self, pipeline):
        m = pipeline.getModuleById(self.moduleId)
        m.annotations[self.key] = self.value

VisAction.createFromXMLDispatch['changeAnnotation'] = ChangeAnnotationAction.parse

class DeleteAnnotationAction(VisAction):
    def __init__(self, timestep=0,parent=0,date=None,user=None,notes=None):
        VisAction.__init__(self,timestep,parent,date,user,notes)
        self.key = None
        self.moduleId = -1
        self.type = 'DeleteAnnotation'
        
    def perform(self, pipeline):
        pipeline.getModuleById(self.moduleId).deleteAnnotation(self.key)

    def writeToDB(self):
	source = """<action date=\"""" + str(self.date) + """\" parent=\"""" + str(self.parent) + """\" time=\"""" + str(self.timestep) + """\" user=\"""" + str(self.user) + """\" what="deleteAnnotation"> <note>""" + str(self.notes) + """</note> <annotation key=\"""" + str(self.key) + """\" moduleId=\"""" + str(self.moduleId)  + """\" /> </action>"""
	return source

    def serialize(self, dom, element):
        element.setAttribute('what', 'deleteAnnotation')
        child = dom.createElement('annotation')
        child.setAttribute('key', self.key)
        child.setAttribute('moduleId',   str(self.moduleId))
        element.appendChild(child)

    @staticmethod
    def parse(element, version = None):
	notes = None
	#backwards compatibility
	notes = str(element.getAttribute('notes'))
	
	for n in element.childNodes:
	    if n.localName == "notes":
		notes = str(n.firstChild.nodeValue)
		break

	newAction = DeleteAnnotationAction(int(element.getAttribute('time')),
                                         int(element.getAttribute('parent')),
					 str(element.getAttribute('date')),
					 str(element.getAttribute('user')),
                                         notes)
        for el in named_elements(element, 'annotation'):
            newAction.moduleId = int(el.getAttribute('moduleId'))
            newAction.key = str(el.getAttribute('key'))
            return newAction
 
VisAction.createFromXMLDispatch['deleteAnnotation'] = DeleteAnnotationAction.parse

class AddModulePortAction(VisAction):
    attributes = ['moduleId', 'portType', 'portName', 'portSpec']
    conversions = [int, str, str, str]

    def __init__(self, timestep=0,parent=0,date=None,user=None,notes=None):
        VisAction.__init__(self, timestep,parent,date,user,notes)
        self.moduleId = -1
        self.type = 'AddModulePort'

    def addModulePort(self, moduleId, portType, portName, portSpec):
        """ Add a new port to the module
        Parameters
        ----------

        - moduleId : 'int'

        - portType : 'string'

        - portName : 'string'

        - portSpec : 'string'

        """
        self.moduleId = moduleId
        self.portType = portType
        self.portName = portName
        self.portSpec = portSpec

    def writeToDB(self):
	
        temp = ""
        temp = temp + """<addPort"""
        for a, v in zip(AddModulePortAction.attributes,
                        [self.moduleId, self.portType, self.portName, self.portSpec]):
            temp = temp + """ """ + a + """=\"""" + str(v) + """\""""
        temp = temp + """/>"""
        source =""
        
        source = """<action date=\"""" + str(self.date) + """\" parent=\"""" + str(self.parent) + """\" time=\"""" + str(self.timestep) + """\" user=\"""" + str(self.user) + """\" what="addModulePort"> <note>""" + str(self.notes) + """</note>""" + temp + """</action>"""
        return source
     
    def serialize(self, dom, element):
        element.setAttribute('what', 'addModulePort')
        child = dom.createElement('addPort')
        for a, v in zip(AddModulePortAction.attributes,
                        [self.moduleId, self.portType, self.portName, self.portSpec]):
            child.setAttribute(a,str(v))
        element.appendChild(child)

    @staticmethod
    def parse(element, version=None):
        notes = None
        #backwards compatibility
        notes = str(element.getAttribute('notes'))

        for n in element.childNodes:
            if n.localName == "notes":
                notes = str(n.firstChild.nodeValue)
                break

        newAction = AddModulePortAction(int(element.getAttribute('time')),
                                        int(element.getAttribute('parent')),
                                        str(element.getAttribute('date')),
                                        str(element.getAttribute('user')),
                                        notes)
        p = [[conv(set.getAttribute(key))
              for conv,key in zip(AddModulePortAction.conversions,
                                  AddModulePortAction.attributes)]
             for set in named_elements(element, 'addPort')]
        [[newAction.moduleId, newAction.portType, newAction.portName, newAction.portSpec]] = p
        return newAction
      
    def perform(self, pipeline):
        m = pipeline.getModuleById(self.moduleId)
        moduleThing = registry.getDescriptorByName(m.name).module
        if m.registry==None:
            m.registry = ModuleRegistry()
            m.registry.addModule(moduleThing)
        if self.portType=='input':
            des = m.registry.getDescriptorByThing(moduleThing)
            m.registry.addInputPort(moduleThing,
                                    self.portName,
                                    [registry.getDescriptorByName(spec).module
                                     for spec in self.portSpec[1:-1].split(',')])
        else:
            m.registry.addOutputPort(moduleThing,
                                     self.portName,
                                     [registry.getDescriptorByName(spec).module
                                      for spec in self.portSpec[1:-1].split(',')])

VisAction.createFromXMLDispatch['addModulePort'] = AddModulePortAction.parse

class DeleteModulePortAction(VisAction):
    def __init__(self,timestep=0,parent=0,date=None,user=None,notes=None):
        VisAction.__init__(self,timestep,parent,date,user,notes)
        self.moduleId = -1
        self.type = 'DeleteModulePort'
        
    def perform(self, pipeline):
        m = pipeline.getModuleById(self.moduleId)
        moduleThing = registry.getDescriptorByName(m.name).module
        if self.portType=='input':
            m.registry.deleteInputPort(moduleThing, self.portName)
        else:
            m.registry.deleteOutputPort(moduleThing, self.portName)

    def writeToDB(self):
	source = """<action date=\"""" + str(self.date) + """\" parent=\"""" + str(self.parent) + """\" time=\"""" + str(self.timestep) + """\" user=\"""" + str(self.user) + """\" what="deleteModulePort"> <note>""" + str(self.notes) + """</note> <annotation key=\"""" + str(self.key) + """\" moduleId=\"""" + str(self.moduleId)  + """\" /> </action>"""
	return source

    def serialize(self, dom, element):
        element.setAttribute('what', 'deleteModulePort')
        child = dom.createElement('deletePort')
        child.setAttribute('moduleId',   str(self.moduleId))
        child.setAttribute('portType', self.portType)
        child.setAttribute('portName', self.portName)
        element.appendChild(child)

    @staticmethod
    def parse(element, version=None):
        notes = None
        #backwards compatibility
        notes = str(element.getAttribute('notes'))
        
        for n in element.childNodes:
            if n.localName == "notes":
                notes = str(n.firstChild.nodeValue)
                break

        newAction = DeleteModulePortAction(int(element.getAttribute('time')),
                                           int(element.getAttribute('parent')),
                                           str(element.getAttribute('date')),
                                           str(element.getAttribute('user')),
                                           notes)
        for el in named_elements(element, 'deletePort'):
            newAction.moduleId = int(el.getAttribute('moduleId'))
            newAction.portType = str(el.getAttribute('portType'))
            newAction.portName = str(el.getAttribute('portName'))
            return newAction
 
VisAction.createFromXMLDispatch['deleteModulePort'] = DeleteModulePortAction.parse

################################################################################

import unittest

class TestVisAction(unittest.TestCase):
    def test1(self):
        import vistrail
        import xml_parser
        parser = xml_parser.XMLParser()
        parser.openVistrail('test_files/vistrail.xml')
        v = parser.getVistrail()
        parser.closeVistrail()
        p1 = v.getPipeline('Nice layout')
        p2 = v.getPipeline('Nice layout')
        self.assertEquals(len(p1.modules), len(p2.modules))
        for k in p1.modules.keys():
            if p1.modules[k] is p2.modules[k]:
                self.fail("didn't expect aliases in two different pipelines")
    def test2(self):
        import vistrail
        import xml_parser
        parser = xml_parser.XMLParser()
        parser.openVistrail('test_files/vtk_book_3rd_p189.xml')
        v = parser.getVistrail()
        parser.closeVistrail()
        p1 = v.getPipeline('final')
        v.getPipeline('quadric')
        p2 = v.getPipeline('final')
        
        m1s = p1.modules.items()
        m2s = p2.modules.items()
        m1s.sort()
        m2s.sort()
        for ((i1,m1),(i2,m2)) in zip(m1s, m2s):
            self.assertEquals(m1.center.x, m2.center.x)
            self.assertEquals(m1.center.y, m2.center.y)

if __name__ == '__main__':
    unittest.main()

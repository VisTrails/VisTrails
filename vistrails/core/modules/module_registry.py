from PyQt4 import QtCore

import core.modules
import core.modules.vistrails_module

import __builtin__

from core.common import VistrailsInternalError, memo_method, all
import core.vis_types
import copy

################################################################################
# ModuleDescriptor

class ModuleDescriptor(object):

    def __init__(self, module, name = None):
        if not name:
            name = module.__name__
        self.module = module
        if (len(self.module.__bases__) > 0 and
            self.module.__bases__[0] != object):
            self.baseDescriptor = registry.getDescriptor(self.module.__bases__[0])
        else:
            self.baseDescriptor = None
        self.name = name
        self.inputPorts = {}
        self.outputPorts = {}
        self.inputPortsOptional = {}
        self.outputPortsOptional = {}
        self.inputPortsConfigureWidgetType = {}
    
    def appendToPortList(self, port, optionals, name, spec, optional):
        def canonicalize(specItem):
            if type(specItem) == __builtin__.type:
                return (specItem, '<no description>')
            elif type(specItem) == __builtin__.tuple:
                assert len(specItem) == 2
                assert type(specItem[0]) == __builtin__.type
                assert type(specItem[1]) == __builtin__.str                
                return specItem
        if type(spec) == __builtin__.list:
            newSpec = []
            for s in spec:
                if type(s)==__builtin__.list:
                    newSpec = newSpec + s
                else:
                    newSpec.append(s)
            spec = [canonicalize(s) for s in newSpec]
        else:
            spec = [canonicalize(spec)]
        if not port.has_key(name):
            port[name] = []
            optionals[name] = optional
        if not spec in port[name]:
            optionals[name] = optional and optionals[name]
            port[name].append(spec)

    def addInputPort(self, name, spec, optional, configureWidgetType):
        self.appendToPortList(self.inputPorts, self.inputPortsOptional, name, spec, optional)
        self.inputPortsConfigureWidgetType[name] = configureWidgetType

    def deleteInputPort(self, name):
        if self.inputPorts.has_key(name):
            del self.inputPorts[name]
            del self.inputPortsOptional[name]

    def addOutputPort(self, name, spec, optional):
        self.appendToPortList(self.outputPorts, self.outputPortsOptional, name, spec, optional)

    def deleteOutputPort(self, name):
        if self.outputPorts.has_key(name):
            del self.outputPorts[name]
            del self.outputPortsOptional[name]

################################################################################
# ModuleRegistry

class ModuleRegistry(QtCore.QObject):
    """ModuleRegistry serves as a global registry of all VisTrails modules.

(To compare with the previous implementation, it is both VTKRTTI and PluginRTTI
put together, with the ability to extend it at runtime)"""

    def __init__(self):
        QtCore.QObject.__init__(self)
        # newModuleSignal is emitted with name of new module
        self.newModuleSignal = QtCore.SIGNAL("newModule")
        # newInputPortSignal is emitted with name of module, new port and spec
        self.newInputPortSignal = QtCore.SIGNAL("newInputPortSignal")
        # newOutputPortSignal is emitted with name of module, new port and spec
        self.newOutputPortSignal = QtCore.SIGNAL("newOutputPortSignal")
        n = Tree(core.modules.vistrails_module.Module)
        self.classTree = n
        self.moduleName = { core.modules.vistrails_module.Module: "Module" }
        self.moduleTree = { "Module": n }
        self.moduleWidget = { "Module": None }

    def hasModule(self, name):
        return self.moduleTree.has_key(name)

    def getDescriptorByName(self, name):
        """getDescriptorByName(name: string) -> ModuleDescriptor

Returns the module descriptor of the class with a given name"""
        assert self.moduleTree.has_key(name)
        return self.moduleTree[name].descriptor

    def getDescriptor(self, module):
        """getDescriptor(module: class) -> ModuleDescriptor

Returns the ModuleDescriptor of a given vistrails module (a class that
subclasses from modules.vistrails_module.Module)"""
        assert self.moduleName.has_key(module)
        name = self.moduleName[module]
        return self.getDescriptorByName(name)

    def addModule(self, module, name = None, configureWidgetType = None):
        """addModule(module: class, optional name: string) -> Tree

Registers a new module with VisTrails. Receives the class itself and an optional
name that will be the name of the module (if not given, uses module.__name__).
This module will be available for use in pipelines."""
        if not name:
            name = module.__name__
        assert not self.moduleTree.has_key(name)
        assert len(module.__bases__) == 1
        baseClass = module.__bases__[0]
        assert self.moduleName.has_key(baseClass), ("Missing base class %s" % baseClass.__name__)
        baseName = self.moduleName[baseClass]
        baseNode = self.moduleTree[baseName]
        moduleNode = baseNode.addModule(module)
        self.moduleTree[name] = moduleNode
        self.moduleName[module] = name
        self.moduleWidget[name] = configureWidgetType
        
        # self requires object magic, it's an open type! I want OCaml :(
        # self.addOutputPort(module, 'self', (module, 'self'))
        self.emit(QtCore.SIGNAL("newModule"), name)
        return moduleNode

    def addInputPort(self, module, portName, portSpec, optional=False, configureWidgetType=None):
        """addInputPort(module: class, portName: string, portSpec) -> None

Registers a new input port with VisTrails. Receives the module that will
now have a certain port, a string representing the name, and a specification
of the port, with the following format:

Module (the real module, not a string with the module name): The port takes
a module of class Module.

(Module, str): The port takes a module of class Module. str
contains a description of the input

list of formats: the port takes more than a single input. Each of the list
elements is of either of the above formats."""
        descriptor = self.getDescriptor(module)
        descriptor.addInputPort(portName, portSpec, optional, configureWidgetType)
        self.emit(self.newInputPortSignal,
                  descriptor.name, portName, portSpec)

    def addOutputPort(self, module, portName, portSpec, optional=False):
        """addInputPort(module: class, portName: string, portSpec) -> None

Registers a new input port with VisTrails. Receives the module that will
now have a certain port, a string representing the name, and a specification
of the port, with one of the following formats:

Module (the real module, not a string with the module name): The port produces
a module of class Module.

(Module, str): The port produces a module of class Module. str
contains a description of the output

list of formats: the port produces more than a single output. Each of the list
elements is of either of the above formats."""
        descriptor = self.getDescriptor(module)
        descriptor.addOutputPort(portName, portSpec, optional)
        self.emit(self.newOutputPortSignal,
                  descriptor.name, portName, portSpec)

    def deleteInputPort(self, module, portName):
        """ Just remove a name input port with all of its specs """
        descriptor = self.getDescriptor(module)
        descriptor.deleteInputPort(portName)

    def deleteOutputPort(self, module, portName):
        """ Just remove a name output port with all of its specs """
        descriptor = self.getDescriptor(module)
        descriptor.deleteOutputPort(portName)

#    @memo_method
    def sourcePortsFromDescriptor(self, descriptor):
        def visPortFromSpec(spec, optional):
            result = core.vis_types.VisPort()
            result.name = spec[0]
            result.spec = spec[1]
            result.optional = optional
            result.moduleName = descriptor.name
            result.endPoint = core.vis_types.VisPortEndPoint.Source
            return result
        v = descriptor.outputPorts.items()
        v.sort(lambda (n1, v1), (n2, v2): cmp(n1,n2))
        return [visPortFromSpec(x, descriptor.outputPortsOptional[x[0]]) for x in v]

#    @memo_method
    def destinationPortsFromDescriptor(self, descriptor):
        def visPortFromSpec(spec, optional):
            result = core.vis_types.VisPort()
            result.name = spec[0]
            result.spec = spec[1]
            result.optional = optional
            result.moduleName = descriptor.name
            result.endPoint = core.vis_types.VisPortEndPoint.Destination
            return result        
        v = descriptor.inputPorts.items()
        v.sort(lambda (n1, v1), (n2, v2): cmp(n1,n2))
        return [visPortFromSpec(x, descriptor.inputPortsOptional[x[0]]) for x in v]

    getDescriptorByThingDispatch = {
        __builtin__.str: getDescriptorByName,
        __builtin__.type: getDescriptor,
        ModuleDescriptor: lambda self, x: x}
    
    def getDescriptorByThing(self, thing):
        return self.getDescriptorByThingDispatch[type(thing)](self, thing)

    def sourcePorts(self, thing):
        """Returns source ports for all hierarchy leading to given module"""
        return [(klass.__name__,
                 self.sourcePortsFromDescriptor(self.getDescriptor(klass)))
                for klass in self.getModuleHierarchy(thing)]

    def destinationPorts(self, thing):
        """Returns destination ports for all hierarchy leading to given module"""
        return [(klass.__name__,
                 self.destinationPortsFromDescriptor(self.getDescriptor(klass)))
                for klass in self.getModuleHierarchy(thing)]

#    @memo_method
    def methodPorts(self, module):
        """methodPorts(module: class or string) -> list of VisPort

Returns the list of ports that can also be interpreted as method
calls. These are the ones whose spec contains only subclasses of
Constant."""
        def specWithConstantOnly(port):
#            print '>>>>>', port.name
#            for spec in port.spec:
#                print spec
            return [spec
                    for spec
                    in port.spec
                    if all(spec, lambda x: issubclass(x[0], core.modules.basic_modules.Constant))]
        lst = self.destinationPortsFromDescriptor(self.getDescriptorByThing(module))
        result = []
        for port in lst:
            constantOnly = specWithConstantOnly(port)
            if len(constantOnly):
                cp = copy.copy(port)
                cp.spec = constantOnly
                result.append(cp)
        return result

#    @memo_method
    def userSetMethods(self, module):
        """userSetMethods(module: class or string) -> dict(classname,
dict(functionName, list of ModuleFunction)).

Returns all methods that can be set by the user in a given class
(including parent classes)"""
        
        def userSetMethodsClass(klass):
            # klass -> dict(functionName, list of ModuleMunction)
            ports = self.methodPorts(klass)
            result = {}
            for port in ports:
                if not result.has_key(port.name):
                    result[port.name] = []
                specs = port.spec
                for spec in specs:
                    result[port.name].append(core.vis_types.ModuleFunction.fromSpec(port, spec))
            return result

        hierarchy = self.getModuleHierarchy(module)
        methods = [(klass.__name__, userSetMethodsClass(klass))
                   for klass in hierarchy]
        return dict(methods)

    def portsCanConnect(self, sourceModulePort, destinationModulePort):
        """portsCanConnectVTKRTTI().portsCanConnect(sourceModulePort, destinationModulePort) -> Boolean
returns true if there could exist a connection connecting these two ports."""
        if sourceModulePort.endPoint == destinationModulePort.endPoint:
            return False
        if sourceModulePort.type != destinationModulePort.type:
            return False

        def getTypes(port, specId=0):
            spec = port.spec[specId]
            return [description[0] for description in spec]

        for j in range(len(sourceModulePort.spec)):
            sourceTypes = getTypes(sourceModulePort, j)
            for i in range(len(destinationModulePort.spec)):
                destTypes = getTypes(destinationModulePort, i)
                if len(sourceTypes) != len(destTypes):
                    continue
                ok = True
                for (st, dt) in zip(sourceTypes, destTypes):
                    sourceDescriptor = self.getDescriptorByThing(st)
                    destinationDescriptor = self.getDescriptorByThing(dt)
                    if not issubclass(sourceDescriptor.module, destinationDescriptor.module):
                        ok = False
                        break
                if ok:
                    return True
        return False


    def isPortSubType(self, super, sub):
        def getTypes(port, specId=0):
            spec = port.spec[specId]
            return [description[0] for description in spec]

        if super.endPoint != sub.endPoint:
            return False
        if super.type != sub.type:
            return False
        if super.name != sub.name:
            return False

        for j in range(len(super.spec)):
            superTypes = getTypes(super, j)
            for i in range(len(sub.spec)):
                subTypes = getTypes(sub, i)
                if len(superTypes) != len(subTypes):
                    continue
                ok = True
                for (superType, subType) in zip(superTypes, subTypes):
                    superModule = self.getDescriptorByThing(superType).module
                    subModule = self.getDescriptorByThing(subType).module
                    if not issubclass(subModule, superModule):
                        ok = False
                        break
                if ok:
                    return True
        return False


    def getModuleHierarchy(self, thing):
        descriptor = self.getDescriptorByThing(thing)
        return descriptor.module.mro()[:-1]

    def getPortConfigureWidgetType(self, moduleName, portName):
        moduleDescriptor = self.getDescriptorByName(moduleName)
        if moduleDescriptor.inputPortsConfigureWidgetType.has_key(portName):
            return moduleDescriptor.inputPortsConfigureWidgetType[portName]
        else:
            return None

    def makeSpec(self, port, specStr, localRegistry=None, loose=True):
        """Parses a string representation of a port spec and returns the spec. Uses
own type to decide between source and destination ports."""
        if specStr[0] != '(' or specStr[-1] != ')':
            raise VistrailsInternalError("invalid port spec")
        specStr = specStr[1:-1]
        descriptor = self.getDescriptorByName(port.moduleName)
        if localRegistry:
            localDescriptor = localRegistry.getDescriptorByName(port.moduleName)
        else:
            localDescriptor = None
        if port.endPoint == core.vis_types.VisPortEndPoint.Source:
            ports = copy.copy(descriptor.outputPorts)
            if localDescriptor:
                ports.update(localDescriptor.outputPorts)
        elif port.endPoint == core.vis_types.VisPortEndPoint.Destination:
            ports = copy.copy(descriptor.inputPorts)
            if localDescriptor:
                ports.update(localDescriptor.inputPorts)
        else:
            raise VistrailsInternalError("Invalid port endpoint: %s" % port.endPoint)
        values = specStr.split(", ")
        if not ports.has_key(port.name):            
            if loose:
                return [[(self.getDescriptorByName(v).module,
                         '<no description>')
                        for v in values]]
            else:
                raise VistrailsInternalError("Port name is inexistent in ModuleDescriptor")
        specs = ports[port.name]
        for spec in specs:
            if all(zip(spec, values),
                   lambda ((klass, descr), name): issubclass(self.getDescriptorByName(name).module, klass)):
                return [copy.copy(spec)]
        raise VistrailsInternalError("No port spec matches the given string")

    @staticmethod
    def portFromRepresentation(moduleName, portStr, endPoint, localRegistry=None, loose=False):
        x = portStr.find('(')
        assert x != -1
        portName = portStr[:x]
        portSpec = portStr[x:]
        port = core.vis_types.VisPort()
        port.name = portName
        port.moduleName = moduleName
        port.endPoint = endPoint
        port.spec = registry.makeSpec(port, portSpec, localRegistry, loose)
        return port

################################################################################

class Tree(object):
    """Tree implements an n-ary tree of module descriptors. """
    def __init__(self, *args):
        self.descriptor = ModuleDescriptor(*args)
        self.children = []
        self.parent = None

    def addModule(self, submodule):
        assert submodule.__bases__[0] == self.descriptor.module
        result = Tree(submodule)
        result.parent = self
        self.children.append(result)
        return result

################################################################################

import gui.qt
gui.qt.askForQObjectCreation()

registry = ModuleRegistry()

addModule     = registry.addModule
addInputPort  = registry.addInputPort
addOutputPort = registry.addOutputPort

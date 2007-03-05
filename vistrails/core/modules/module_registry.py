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
from PyQt4 import QtCore

from core.utils import VistrailsInternalError, memo_method, all, \
     InvalidModuleClass, ModuleAlreadyExists
import __builtin__
import copy
import core.debug
import core.modules
import core.modules.vistrails_module

from core.vistrail.port import Port, PortEndPoint
from core.vistrail.module_function import ModuleFunction
import core.cache.hasher

###############################################################################
# ModuleDescriptor

class ModuleDescriptor(object):

    def __init__(self, module, name = None):
        if not name:
            name = module.__name__
        self.module = module
        candidates = ModuleRegistry.get_subclass_candidates(self.module)
        if len(candidates) > 0:
            base = candidates[0]
            self.baseDescriptor = registry.getDescriptor(base)
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
        self.appendToPortList(self.inputPorts,
                              self.inputPortsOptional, name, spec, optional)
        self.inputPortsConfigureWidgetType[name] = configureWidgetType

    def deleteInputPort(self, name):
        if self.inputPorts.has_key(name):
            del self.inputPorts[name]
            del self.inputPortsOptional[name]

    def addOutputPort(self, name, spec, optional):
        self.appendToPortList(self.outputPorts,
                              self.outputPortsOptional, name, spec, optional)

    def deleteOutputPort(self, name):
        if self.outputPorts.has_key(name):
            del self.outputPorts[name]
            del self.outputPortsOptional[name]

###############################################################################
# ModuleRegistry

class ModuleRegistry(QtCore.QObject):
    """ModuleRegistry serves as a global registry of all VisTrails modules.

(To compare with the previous implementation, it is both VTKRTTI and
PluginRTTI put together, with the ability to extend it at runtime)"""

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
        self._hasher_callable = {}
        self._module_color = {}
        self._module_fringe = {}
        self.currentPackageName = 'Basic Modules'
        self.modulePackage = {"Module": 'Basic Modules'}
        self.packageModules = {'Basic Modules': ["Module"]}

    def module_signature(self, module):
        """Returns signature of a given core.vistrail.Module, possibly
using user-defined hasher."""
        if self._hasher_callable.has_key(module.name):
            return self._hasher_callable[module.name](module)
        else:
            return core.cache.hasher.Hasher.module_signature(module)

    def hasModule(self, name):
        return self.moduleTree.has_key(name)

    def get_module_color(self, name):
        if self._module_color.has_key(name):
            return self._module_color[name]
        else:
            return None

    def get_module_fringe(self, name):
        if self._module_fringe.has_key(name):
            return self._module_fringe[name]
        else:
            return None

    def getDescriptorByName(self, name):
        """getDescriptorByName(name: string) -> ModuleDescriptor

Returns the module descriptor of the class with a given name"""
        if not self.moduleTree.has_key(name):            
            msg = (("Cannot find module %s" % name) +
                   ": a required package might be missing")            
            core.debug.critical(msg)
            return None
        else:
            return self.moduleTree[name].descriptor

    def getDescriptor(self, module):
        """getDescriptor(module: class) -> ModuleDescriptor

Returns the ModuleDescriptor of a given vistrails module (a class that
subclasses from modules.vistrails_module.Module)"""
        assert self.moduleName.has_key(module)
        name = self.moduleName[module]
        return self.getDescriptorByName(name)

    def addModule(self, module,
                  name=None,
                  configureWidgetType=None,
                  cacheCallable=None,
                  moduleColor=None,
                  moduleFringe=None,
                  moduleLeftFringe=None,
                  moduleRightFringe=None):
        """addModule(module: class,
        name=None, configureWidgetType=None,
        cacheCallable=None, moduleColor=None,
        moduleFringe=None,
        moduleLeftFringe=None, moduleRightFringe=None) -> Tree

Registers a new module with VisTrails. Receives the class itself and
an optional name that will be the name of the module (if not given,
uses module.__name__).  This module will be available for use in
pipelines.

If moduleColor is not None, then registry stores it so that the gui
can use it correctly. moduleColor must be a tuple of three floats
between 0 and 1.

if moduleFringe is not None, then registry stores it so that the gui
can use it correctly. moduleFringe must be a list of pairs of floating
points.  The first point must be (0.0, 0.0), and the last must be
(0.0, 1.0). This will be used to generate custom lateral fringes for
module boxes. It must be the case that all x values must be positive, and
all y values must be between 0.0 and 1.0. Alternatively, the user can
set moduleLeftFringe and moduleRightFringe to set two different fringes.

"""
        if not name:
            name = module.__name__
        if self.moduleTree.has_key(name):
            raise ModuleAlreadyExists(name)
        # try to eliminate mixins
        candidates = self.get_subclass_candidates(module)
        if len(candidates) != 1:
            raise InvalidModuleClass(module)
        baseClass = candidates[0]
        assert (self.moduleName.has_key(baseClass),
                ("Missing base class %s" % baseClass.__name__))
        baseName = self.moduleName[baseClass]
        baseNode = self.moduleTree[baseName]
        moduleNode = baseNode.addModule(module, name)
        self.moduleTree[name] = moduleNode
        self.moduleName[module] = name
        self.moduleWidget[name] = configureWidgetType
        self.modulePackage[name] = self.currentPackageName
        if self.packageModules.has_key(self.currentPackageName):
            self.packageModules[self.currentPackageName].append(name)
        else:
            self.packageModules[self.currentPackageName] = [name]
        
        if cacheCallable:
            raise VistrailsInternalError("Unimplemented!")
            self._hasher_callable[name] = cacheCallable

        if moduleColor:
            assert type(moduleColor) == tuple
            assert len(moduleColor) == 3
            for i in 0,1,2:
                assert type(moduleColor[i]) == float
            self._module_color[name] = moduleColor

        def checkFringe(fringe):
            assert type(fringe) == list
            assert len(fringe) >= 1
            for v in fringe:
                assert type(v) == tuple
                assert len(v) == 2
                assert type(v[0]) == float
                assert type(v[1]) == float

        if moduleFringe:
            checkFringe(moduleFringe)
            leftFringe = list(reversed([(-x, 1.0-y) for (x, y) in moduleFringe]))
            print leftFringe
            print moduleFringe
            self._module_fringe[name] = (leftFringe, moduleFringe)
        elif moduleLeftFringe and moduleRightFringe:
            checkFringe(moduleLeftFringe)
            checkFringe(moduleRightFringe)
            self._module_fringe[name] = (moduleLeftFringe, moduleRightFringe)
            
            

        # self requires object magic, it's an open type! I want OCaml :(
        # self.addOutputPort(module, 'self', (module, 'self'))
        self.emit(QtCore.SIGNAL("newModule"), name)
        return moduleNode

    def addInputPort(self, module, portName, portSpec, optional=False,
                     configureWidgetType=None):
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
        descriptor.addInputPort(portName, portSpec, optional,
                                configureWidgetType)
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
    def sourcePortsFromDescriptor(self, descriptor, sorted=True):
        def visPortFromSpec(spec, optional):
            result = Port()
            result.name = spec[0]
            result.spec = spec[1]
            result.optional = optional
            result.moduleName = descriptor.name
            result.endPoint = PortEndPoint.Source
            return result
        v = descriptor.outputPorts.items()
        if sorted:
            v.sort(lambda (n1, v1), (n2, v2): cmp(n1,n2))
        return [visPortFromSpec(x, descriptor.outputPortsOptional[x[0]])
                for x in v]

#    @memo_method
    def destinationPortsFromDescriptor(self, descriptor, sorted=True):
        def visPortFromSpec(spec, optional):
            result = Port()
            result.name = spec[0]
            result.spec = spec[1]
            result.optional = optional
            result.moduleName = descriptor.name
            result.endPoint = PortEndPoint.Destination
            return result        
        v = descriptor.inputPorts.items()
        if sorted:
            v.sort(lambda (n1, v1), (n2, v2): cmp(n1,n2))
        return [visPortFromSpec(x, descriptor.inputPortsOptional[x[0]])
                for x in v]

    getDescriptorByThingDispatch = {
        __builtin__.str: getDescriptorByName,
        __builtin__.type: getDescriptor,
        ModuleDescriptor: lambda self, x: x}
    
    def getDescriptorByThing(self, thing):
        return self.getDescriptorByThingDispatch[type(thing)](self, thing)

    def sourcePorts(self, thing, sorted=True):
        """Returns source ports for all hierarchy leading to given module"""
        return [(klass.__name__,
                 self.sourcePortsFromDescriptor(self.getDescriptor(klass),
                                                sorted))
                for klass in self.getModuleHierarchy(thing)]

    def destinationPorts(self, thing, sorted=True):
        """Returns destination ports for all hierarchy leading to
        given module"""
        getter = self.destinationPortsFromDescriptor
        return [(klass.__name__, getter(self.getDescriptor(klass),
                                        sorted))
                for klass in self.getModuleHierarchy(thing)]

#    @memo_method
    def methodPorts(self, module):
        """methodPorts(module: class or string) -> list of VisPort

Returns the list of ports that can also be interpreted as method
calls. These are the ones whose spec contains only subclasses of
Constant."""
        def specWithConstantOnly(port):
            allConstant = (lambda x:
                           issubclass(x[0],
                                      core.modules.basic_modules.Constant))
            return [spec
                    for spec
                    in port.spec
                    if all(spec, allConstant)]
        module_descriptor = self.getDescriptorByThing(module)
        lst = self.destinationPortsFromDescriptor(module_descriptor)
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
                    fun = ModuleFunction.fromSpec(port, spec)
                    result[port.name].append(fun)
            return result

        hierarchy = self.getModuleHierarchy(module)
        methods = [(klass.__name__, userSetMethodsClass(klass))
                   for klass in hierarchy]
        return dict(methods)

    def portsCanConnect(self, sourceModulePort, destinationModulePort):
        """portsCanConnectVTKRTTI().portsCanConnect(sourceModulePort,
destinationModulePort) -> Boolean returns true if there could exist a
connection connecting these two ports."""
        if sourceModulePort.endPoint == destinationModulePort.endPoint:
            return False
        if sourceModulePort.type != destinationModulePort.type:
            return False
        return self.isSpecsMatched(sourceModulePort, destinationModulePort)

    def isPortSubType(self, super, sub):
        """ isPortSubType(super: Port, sub: Port) -> bool        
        Check if port super and sub are similar or not. These ports
        must have exact name and type as well as position
        
        """
        if super.endPoint != sub.endPoint:
            return False
        if super.type != sub.type:
            return False
        if super.name != sub.name:
            return False
        return self.isSpecsMatched(super, sub)

    def isSpecsMatched(self, super, sub):
        """ isSpecsMatched(super: Port, sub: Port) -> bool        
        Check if specs of super and sub port are matched or not
        
        """
        def getTypes(port, specId=0):
            spec = port.spec[specId]
            return [description[0] for description in spec]

        variantType = core.modules.basic_modules.Variant

        for j in range(len(super.spec)):
            superTypes = getTypes(super, j)
            if superTypes==[variantType]:
                return True
            for i in range(len(sub.spec)):
                subTypes = getTypes(sub, i)
                if subTypes==[variantType]:
                    return True
                if len(superTypes) != len(subTypes):
                    continue
                ok = True
                for (superType, subType) in zip(superTypes, subTypes):
                    if (superType==variantType or subType==variantType):
                        continue
                    superModule = self.getDescriptorByThing(superType).module
                    subModule = self.getDescriptorByThing(subType).module
                    if not issubclass(superModule, subModule):
                        ok = False
                        break
                if ok:
                    return True
        return False

    def getModuleHierarchy(self, thing):
        descriptor = self.getDescriptorByThing(thing)
        return [klass
                for klass in descriptor.module.mro()
                if issubclass(klass, core.modules.vistrails_module.Module)]

    def getPortConfigureWidgetType(self, moduleName, portName):
        moduleDescriptor = self.getDescriptorByName(moduleName)
        if moduleDescriptor.inputPortsConfigureWidgetType.has_key(portName):
            return moduleDescriptor.inputPortsConfigureWidgetType[portName]
        else:
            return None

    def makeSpec(self, port, specStr, localRegistry=None, loose=True):
        """Parses a string representation of a port spec and returns
the spec. Uses own type to decide between source and destination
ports."""
        if specStr[0] != '(' or specStr[-1] != ')':
            raise VistrailsInternalError("invalid port spec")
        specStr = specStr[1:-1]
        if self.hasModule(port.moduleName):            
            descriptor = self.getDescriptorByName(port.moduleName)
        else:
            descriptor = None
        if localRegistry:
            name = port.moduleName
            localDescriptor = localRegistry.getDescriptorByName(name)
        else:
            localDescriptor = None
        if port.endPoint == PortEndPoint.Source:
            if loose and descriptor==None:
                ports = {}
            else:
                ports = copy.copy(descriptor.outputPorts)
            if localDescriptor:
                ports.update(localDescriptor.outputPorts)
        elif port.endPoint == PortEndPoint.Destination:
            if loose and descriptor==None:
                ports = {}
            else:
                ports = copy.copy(descriptor.inputPorts)
            if localDescriptor:
                ports.update(localDescriptor.inputPorts)
        else:
            raise VistrailsInternalError("Invalid port endpoint: %s" %
                                         port.endPoint)
        values = specStr.split(",")
        values = [v.strip() for v in values]
        if not ports.has_key(port.name):
            if loose:
                return [[(self.getDescriptorByName(v).module,
                         '<no description>')
                        for v in values]]
            else:
                msg = "Port name is inexistent in ModuleDescriptor"
                raise VistrailsInternalError(msg)
        specs = ports[port.name]
        fun = lambda ((klass, descr), name): \
                      issubclass(self.getDescriptorByName(name).module, klass)
        for spec in specs:
            if all(zip(spec, values), fun):
                return [copy.copy(spec)]
        raise VistrailsInternalError("No port spec matches the given string")

    @staticmethod
    def portFromRepresentation(moduleName, portStr, endPoint,
                               localRegistry=None, loose=False):
        x = portStr.find('(')
        assert x != -1
        portName = portStr[:x]
        portSpec = portStr[x:]
        port = Port()
        port.name = portName
        port.moduleName = moduleName
        port.endPoint = endPoint
        port.spec = registry.makeSpec(port, portSpec, localRegistry, loose)
        return port

    def getInputPortSpec(self, module, portName):
        """ getInputPortSpec(module: Module, portName: str) -> spec-tuple        
        Return the spec for an input port of a module given the module
        and port name
        
        """
        moduleHierarchy = self.getModuleHierarchy(module.name)
        if module.registry:
            moduleHierarchy = module.registry.getModuleHierarchy(module.name)
            for baseModule in moduleHierarchy:
                des = module.registry.getDescriptorByThing(baseModule)
                if des.inputPorts.has_key(portName):
                    return des.inputPorts[portName]
        for baseModule in moduleHierarchy:
            des = self.getDescriptorByThing(baseModule)
            if des.inputPorts.has_key(portName):
                return des.inputPorts[portName]
        return None

    def getOutputPortSpec(self, module, portName):
        """ getOutputPortSpec(module: Module, portName: str) -> spec-tuple        
        Return the spec for an output port of a module given the module
        and port name
        
        """
        moduleHierarchy = self.getModuleHierarchy(module.name)
        if module.registry:
            moduleHierarchy = module.registry.getModuleHierarchy(module.name)
            for baseModule in moduleHierarchy:
                des = module.registry.getDescriptorByThing(baseModule)
                if des.outputPorts.has_key(portName):
                    return des.outputPorts[portName]
        for baseModule in moduleHierarchy:
            des = self.getDescriptorByThing(baseModule)
            if des.outputPorts.has_key(portName):
                return des.outputPorts[portName]
        # Also check local registry
        return None

    @staticmethod
    def get_subclass_candidates(module):
        """get_subclass_candidates(module) -> [class]

Tries to eliminate irrelevant mixins for the hierarchy. Returns all
base classes that subclass from Module."""
        return [klass
                for klass in module.__bases__
                if issubclass(klass,
                              core.modules.vistrails_module.Module)]

    def setCurrentPackageName(self, pName):
        """ setCurrentPackageName(pName: str) -> None        
        Set the current package name for all addModule operations to
        name. This means that all modules added after this call will
        be assigned to a package name: pName. Set pName to None to
        indicate that VisTrails default package should be used instead
        
        """
        if pName==None:
            pName = 'Basic Modules'
        self.currentPackageName = pName

    def getModulePackage(self, moduleName):
        """ getModulePackage(moduleName: str) -> str
        Return the name associate of a module
        
        """
        if self.modulePackage.has_key(moduleName):
            return self.modulePackage[moduleName]
        else:
            return None

###############################################################################

class Tree(object):
    """Tree implements an n-ary tree of module descriptors. """
    def __init__(self, *args):
        self.descriptor = ModuleDescriptor(*args)
        self.children = []
        self.parent = None

    def addModule(self, submodule, name=None):
        assert self.descriptor.module in submodule.__bases__
        result = Tree(submodule, name)
        result.parent = self
        self.children.append(result)
        return result

###############################################################################

registry = ModuleRegistry()

addModule     = registry.addModule
addInputPort  = registry.addInputPort
addOutputPort = registry.addOutputPort
setCurrentPackageName = registry.setCurrentPackageName

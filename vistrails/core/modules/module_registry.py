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
from itertools import izip

from core.vistrail.port import Port, PortEndPoint
from core.vistrail.module_function import ModuleFunction
import core.cache.hasher

##############################################################################

def _check_fringe(fringe):
    assert type(fringe) == list
    assert len(fringe) >= 1
    for v in fringe:
        assert type(v) == tuple
        assert len(v) == 2
        assert type(v[0]) == float
        assert type(v[1]) == float

###############################################################################
# ModuleDescriptor

class ModuleDescriptor(object):
    """ModuleDescriptor is a class that holds information about
    modules in the registry.

    """

    ##########################################################################

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
        self.portOrder = {}
        self.outputPorts = {}
        self.inputPortsOptional = {}
        self.outputPortsOptional = {}
        self.inputPortsConfigureWidgetType = {}
        
        self._is_abstract = False
        self._configuration_widget = None
        self._left_fringe = None # Fringes are lists of pairs of floats
        self._right_fringe = None
        self._module_color = None
        self._module_package = None
        self._hasher_callable = None
        
    def __copy__(self):
        result = ModuleDescriptor(self.module, self.name)
        result.baseDescriptor = self.baseDescriptor
        result.inputPorts = copy.deepcopy(self.inputPorts)
        result.portOrder = copy.deepcopy(self.portOrder)
        result.outputPorts = copy.deepcopy(self.outputPorts)
        result.inputPortsOptional = copy.deepcopy(self.inputPortsOptional)
        result.outputPortsOptional = copy.deepcopy(self.outputPortsOptional)
        result.inputPortsConfigureWidgetType = copy.deepcopy(self.inputPortsConfigureWidgetType)
        
        result._is_abstract = self._is_abstract
        result._configuration_widget = self._configuration_widget
        result._left_fringe = copy.copy(self._left_fringe)
        result._right_fringe = copy.copy(self._right_fringe)
        result._module_color = self._module_color
        result._module_package = self._module_package
        result._hasher_callable = self._hasher_callable
        return result

    ##########################################################################
    
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
            self.portOrder[name] = len(port)
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

    def set_abstract(self, v):
        self._is_abtract = v

    def abstract(self):
        return self._is_abtract

    def set_configuration_widget(self, configuration_widget_type):
        self._configuration_widget = configuration_widget_type

    def configuration_widget(self):
        return self._configuration_widget

    def set_module_color(self, color):
        if color:
            assert type(color) == tuple
            assert len(color) == 3
            for i in 0,1,2:
                assert type(color[i]) == float
        self._module_color = color

    def module_color(self):
        return self._module_color

    def set_module_fringe(self, left_fringe, right_fringe):
        if left_fringe is None:
            assert right_fringe is None
            self._left_fringe = None
            self._right_fringe = None
        else:
            _check_fringe(left_fringe, right_fringe)
            self._left_fringe = left_fringe
            self._right_fringe = right_fringe

    def module_fringe(self):
        if self._left_fringe is None and self._right_fringe is None:
            return None
        return (self._left_fringe, self._right_fringe)

    def set_module_package(self, package_name):
        self._module_package = package_name

    def module_package(self):
        return self._module_package

    def set_hasher_callable(self, callable_):
        self._hasher_callable = callable_

    def hasher_callable(self):
        return self._hasher_callable

###############################################################################
# ModuleRegistry

class ModuleRegistry(QtCore.QObject):
    """ModuleRegistry serves as a registry of VisTrails modules.
    """

    ##########################################################################
    # Constructor and copy

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
        self.currentPackageName = 'Basic Modules'
        n.descriptor.set_module_package(self.currentPackageName)
        self.packageModules = {'Basic Modules': ["Module"]}

    def __copy__(self):
        result = ModuleRegistry()
        result.classTree = copy.copy(self.classTree)
        result.moduleName = copy.copy(self.moduleName)
        result.moduleTree = result.classTree.make_dictionary()
        result.currentPackageName = copy.copy(self.currentPackageName)
        result.packageModules = copy.copy(self.packageModules)
        return result
        
    ##########################################################################

    def module_signature(self, module):
        """Returns signature of a given core.vistrail.Module, possibly
using user-defined hasher."""
        descriptor = self.getDescriptorByName(module.name)
        if not descriptor:
            return core.cache.hasher.Hasher.module_signature(module)
        c = descriptor.hasher_callable()
        if c:
            return c(module)
        else:
            return core.cache.hasher.Hasher.module_signature(module)

    def hasModule(self, name):
        """hasModule(name) -> Boolean. True if 'name' is registered
        as a module."""
        return self.moduleTree.has_key(name)

    def get_module_color(self, name):
        return self.getDescriptorByName(name).module_color()

    def get_module_fringe(self, name):
        return self.getDescriptorByName(name).module_fringe()

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

    def addModule(self, module, name=None, **kwargs):
        """addModule(module: class, name=None, **kwargs) -> Tree

        kwargs:
          configureWidgetType=None,
          cacheCallable=None,
          moduleColor=None,
          moduleFringe=None,
          moduleLeftFringe=None,
          moduleRightFringe=None,
          abstract=None

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

Notice: in the future, more named parameters might be added to this
method, and the order is not specified.

"""
        # Setup named arguments. We don't use passed parameters so
        # that positional parameter calls fail earlier
        def fetch(name, default):
            r = kwargs.get(name, default)
            try:
                del kwargs[name]
            except KeyError:
                pass
            return r
        name = fetch('name', module.__name__)
        configureWidgetType = fetch('configureWidgetType', None)
        cacheCallable = fetch('cacheCallable', None)
        moduleColor = fetch('moduleColor', None)
        moduleFringe = fetch('moduleFringe', None)
        moduleLeftFringe = fetch('moduleLeftFringe', None) 
        moduleRightFringe = fetch('moduleRightFringe', None)
        is_abstract = fetch('abstract', False)
        
        if len(kwargs) > 0:
            raise VistrailsInternalError('Wrong parameters passed to addModule: %s' % kwargs)
        
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

        descriptor = moduleNode.descriptor
        descriptor.set_abstract(is_abstract)
        descriptor.set_configuration_widget(configureWidgetType)
        descriptor.set_module_package(self.currentPackageName)

        if cacheCallable:
            raise VistrailsInternalError("Unimplemented!")
        descriptor.set_hasher_callable(cacheCallable)
        descriptor.set_module_color(moduleColor)

        if moduleFringe:
            _check_fringe(moduleFringe)
            leftFringe = list(reversed([(-x, 1.0-y) for (x, y) in moduleFringe]))
            descriptor.set_module_fringe(leftFringe, moduleFringe)
        elif moduleLeftFringe and moduleRightFringe:
            checkFringe(moduleLeftFringe)
            checkFringe(moduleRightFringe)
            descriptor.set_module_fringe(moduleLeftFringe, moduleRightFringe)

        if self.packageModules.has_key(self.currentPackageName):
            self.packageModules[self.currentPackageName].append(name)
        else:
            self.packageModules[self.currentPackageName] = [name]

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
            result.sort_key = descriptor.portOrder[spec[0]]
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
        return self.isSpecsMatched(sourceModulePort, destinationModulePort)

    def isPortSubType(self, super, sub):
        """ isPortSubType(super: Port, sub: Port) -> bool        
        Check if port super and sub are similar or not. These ports
        must have exact name as well as position
        
        """
        if super.endPoint != sub.endPoint:
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
        """getModuleHierarchy(thing) -> [klass].
        Returns the module hierarchy all the way to Module, excluding
        any mixins."""
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
        the spec. Uses port type to decide between source and destination
        ports.

        if 'loose' is true, makeSpec will try to succeed even if the
        information is missing in the registry. This is useful for loading
        vistrails when packages are missing."""

        def get_descriptor(reg, name):
            if reg and reg.hasModule(name):
                return reg.getDescriptorByName(name)
            else:
                return None

        ports = {}
        def update_ports_from_descriptor(descriptor):
            """updates 'ports' corresponding to the passed port type
            (source->outputs, destination->inputs). If descriptor is
            not present, do nothing"""
            endpoint = port.endPoint
            if descriptor == None:
                return
            if endpoint == PortEndPoint.Source:
                ports.update(descriptor.outputPorts)
            elif endpoint == PortEndPoint.Destination:
                ports.update(descriptor.inputPorts)
            else:
                raise VistrailsInternalError("Invalid port endpoint: %s" %
                                             endpoint)

        descriptor      = get_descriptor(self,          port.moduleName)
        localDescriptor = get_descriptor(localRegistry, port.moduleName)

        update_ports_from_descriptor(descriptor)
        update_ports_from_descriptor(localDescriptor)

        if specStr[0] != '(' or specStr[-1] != ')':
            raise VistrailsInternalError("invalid port spec")
        values = [v.strip() for v in specStr[1:-1].split(",")]

        if ports.has_key(port.name): 
            specs = ports[port.name]

            def param_type_matches(((klass, _), name)):
                return issubclass(self.getDescriptorByName(name).module,
                                  klass)

            for spec in specs:
                if all(izip(spec, values), param_type_matches):
                    return [copy.copy(spec)]

            msg = "No port spec matches the given string '%s'" % specStr
            raise VistrailsInternalError(msg)

        if loose:
            # Attempt to reconstruct the spec without information
            return [[(self.getDescriptorByName(v).module,
                      '<no description>')
                     for v in values]]

        msg = "Port '%s' is inexistent in ModuleDescriptor" % port.name
        raise VistrailsInternalError(msg)

        

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

    def get_module_package(self, moduleName):
        """ get_module_package(moduleName: str) -> str
        Return the name of the package where the module is registered.
        
        """
        descriptor = self.getDescriptorByName(moduleName)
        return descriptor.module_package()

    def get_configuration_widget(self, moduleName):
        descriptor = self.getDescriptorByName(moduleName)
        return descriptor.configuration_widget()
        

###############################################################################

class Tree(object):
    """Tree implements an n-ary tree of module descriptors. """

    ##########################################################################
    # Constructor and copy
    def __init__(self, *args):
        self.descriptor = ModuleDescriptor(*args)
        self.children = []
        self.parent = None

    def __copy__(self):
        cp = Tree(self.descriptor.module, self.descriptor.name)
        cp.descriptor = copy.copy(self.descriptor)
        cp.children = [copy.copy(child)
                       for child in self.children]
        for child in cp.children:
            child.parent = cp
        return cp

    ##########################################################################

    def addModule(self, submodule, name=None):
        assert self.descriptor.module in submodule.__bases__
        result = Tree(submodule, name)
        result.parent = self
        self.children.append(result)
        return result

    def make_dictionary(self):
        """make_dictionary(): recreate ModuleRegistry dictionary
for copying module registries around"""
        # This is inefficient
        result = {self.descriptor.name: self}
        for child in self.children:
            result.update(child.make_dictionary())
        return result
        

###############################################################################

registry = ModuleRegistry()

addModule     = registry.addModule
addInputPort  = registry.addInputPort
addOutputPort = registry.addOutputPort
setCurrentPackageName = registry.setCurrentPackageName


##############################################################################

import unittest


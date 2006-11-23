################################################################################
# VTK Package for VisTrails
################################################################################
import vtk
from core.debug import log
from core.modules.basic_modules import Integer, Float, String
from core.modules.module_registry import (registry, addModule,
                                          addInputPort, addOutputPort)
from core.modules.vistrails_module import newModule
from base_module import vtkBaseModule
from class_tree import ClassTree
from vtk_parser import VTKMethodParser

################################################################################

parser = VTKMethodParser()


typeMapDict = {'int': Integer,
               'float': Float,
               'char*': String,
               'char *': String,
               'string': String,
               'char': String,
               'const char*': String,
               'const char *': String}

def typeMap(name):
    """ typeMap(name: str) -> Module
    Convert from C/C++ types into VisTrails Module type
    
    """
    if type(name) == tuple:
        return [typeMap(x) for x in name]
    if typeMapDict.has_key(name):
        return typeMapDict[name]
    else:
        if registry.hasModule(name):
            return registry.getDescriptorByName(name).module
        else:
            return None

def addAlgorithmPorts(module):
    """ addAlgorithmPorts(module: Module) -> None
    If module is a subclass of vtkAlgorithm, this function will add all
    SetInputConnection([id],[port]) and GetOutputPort([id]) as
    SetInputConnection{id}([port]) and GetOutputPort{id}.

    """
    if issubclass(module.vtkClass, vtk.vtkAlgorithm):
        if module.vtkClass!=vtk.vtkStructuredPointsGeometryFilter:
            # We try to instantiate the class here to get the number of
            # ports and to avoid abstract classes
            try:
                instance = module.vtkClass()
                for i in range(0,instance.GetNumberOfInputPorts()):
                    des = registry.getDescriptorByName('vtkAlgorithmOutput')
                    addInputPort(module, 'SetInputConnection%d'%i, des.module)
                for i in range(0,instance.GetNumberOfOutputPorts()):
                    des = registry.getDescriptorByName('vtkAlgorithmOutput')
                    addOutputPort(module, 'GetOutputPort%d'%i, des.module)
                del instance
            except:
                pass

def addSetGetPorts(module, get_set_dict):
    """ addSetGetPorts(module: Module, get_set_dict: dict) -> None
    Convert all Setxxx methods of module into input ports and all Getxxx
    methods of module into output ports

    Keyword arguments:
    module       --- Module
    get_set_dict --- the Set/Get method signatures returned by vtk_parser

    """
    for name in get_set_dict.iterkeys():
        if name in ['InputConnection', 'OutputPort']: continue
        getterMethod = getattr(module.vtkClass, 'Get%s'%name)
        setterMethod = getattr(module.vtkClass, 'Set%s'%name)
        getterSig = parser.get_method_signature(getterMethod)
        setterSig = parser.get_method_signature(setterMethod)
        for getter, order in zip(getterSig, range(1, len(getterSig)+1)):
            if getter[1]:
                log("Can't handle getter %s (%s) of class %s: Needs input to "
                    "get output" % (order, name, module.vtkClass))
                continue
            if len(getter[0]) != 1:
                log("Can't handle getter %s (%s) of class %s: More than a "
                    "single output" % (order, name, module.vtkClass))
                continue
            addOutputPort(module, 'Get'+name, typeMap(getter[0][0]), True)
        for setter, order in zip(setterSig, range(1, len(setterSig)+1)):
            try:
                if len(setter[1])==1:                    
                    addInputPort(module, 'Set'+name,
                                 typeMap(setter[1][0]),
                                 setter[1][0] in typeMapDict)
                else:
                    addInputPort(module, 'Set'+name,
                                 [typeMap(i) for i in setter[1]],
                                 True)
            except IndexError, e:
                print "module", module, "name", name, setter
                raise

def addTogglePorts(module, toggle_dict):
    """ addTogglePorts(module: Module, toggle_dict: dict) -> None
    Convert all xxxOn/Off methods of module into input ports

    Keyword arguments:
    module      --- Module
    toggle_dict --- the Toggle method signatures returned by vtk_parser

    """
    for name in toggle_dict.iterkeys():
        addInputPort(module, name+'On', [], True)
        addInputPort(module, name+'Off', [], True)
    
def addStatePorts(module, state_dict):
    """ addStatePorts(module: Module, state_dict: dict) -> None
    Convert all SetxxxToyyy methods of module into input ports

    Keyword arguments:
    module     --- Module
    state_dict --- the State method signatures returned by vtk_parser

    """
    for name in state_dict.iterkeys():
        for mode in state_dict[name]:
            addInputPort(module, 'Set'+name+'To'+mode[0], [], True)
    
def addOtherPorts(module, other_list):
    """ addOtherPorts(module: Module, other_list: list) -> None
    Convert all other ports such as Insert/Add.... into input/output

    Keyword arguments:
    module     --- Module
    other_dict --- any other method signatures that is not
                   Algorithm/SetGet/Toggle/State type

    """
    for name in other_list:
        if name[:3]=='Add' or name[:6]=='Insert':
            method = getattr(module.vtkClass, name)
            addSignature = parser.get_method_signature(method)
            for sig in addSignature:
                ([result], params) = sig
                types = []
                if params:
                    for p in params:
                        t = typeMap(p)
                        if not t: types = None
                        else: types.append(t)
                else:
                    types = [[]]
                if types:
                    if len(types)<=1:
                        addInputPort(module, name, types[0],
                                     types[0] in typeMapDict.itervalues())
                    else:
                        addInputPort(module, name, types, True)
        else:
            method = getattr(module.vtkClass, name)
            signatures = parser.get_method_signature(method)
            for sig in signatures:
                ([result], params) = sig
                if params:
                    types = [typeMap(p) for p in params]
                else:
                    types = []
                if len(types)==0 or (result==None):
                    addInputPort(module, name, types, True)
    
def addPorts(module):
    """ addPorts(module: VTK module inherited from Module) -> None
    Search all metamethods of module and add appropriate ports

    """
    addOutputPort(module, 'self', module)
    parser.parse(module.vtkClass)
    addAlgorithmPorts(module)
    addSetGetPorts(module, parser.get_get_set_methods())
    addTogglePorts(module, parser.get_toggle_methods())
    addStatePorts(module, parser.get_state_methods())
    addOtherPorts(module, parser.get_other_methods())

def setAllPorts(treeNode):
    """ setAllPorts(treeNode: TreeNode) -> None
    Traverse treeNode and all of its children/grand-children to add all ports

    """
    addPorts(treeNode.descriptor.module)
    for child in treeNode.children:
        setAllPorts(child)

def createModule(baseModule, node):
    """ createModule(baseModule: a Module subclass, node: TreeNode) -> None
    Construct a module inherits baseModule with specification from node
    
    """
    module = newModule(baseModule, node.name)
    # This is sitting on the class
    module.vtkClass = node.klass
    addModule(module)
    for child in node.children:
        createModule(module, child)

def createAllModules(g):
    """ createAllModules(g: ClassTree) -> None
    Traverse the VTK class tree and add all modules into the module registry
    
    """
    assert len(g.tree[0]) == 1
    base = g.tree[0][0]
    assert base.name == 'vtkObjectBase'
    vtkObjectBase = newModule(vtkBaseModule, 'vtkObjectBase')
    vtkObjectBase.vtkClass = vtk.vtkObjectBase
    addModule(vtkObjectBase)
    for children in base.children:
        createModule(vtkObjectBase, children)

################################################################################
def initialize():
    """ initialize() -> None
    Package-entry to initialize the package
    
    """
    inheritanceGraph = ClassTree(vtk)
    inheritanceGraph.create()
    addModule(vtkBaseModule)
    createAllModules(inheritanceGraph)
    setAllPorts(registry.moduleTree['vtkObjectBase'])

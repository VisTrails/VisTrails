# VTK Package for VisTrails
################################################################################

# TODO:

# Investigate how to setup "get by reference"

################################################################################
# Package version

version = '0.1'

try:
    import vtk
except ImportError:
    raise PackageError("This package requires VTK.")

import __builtin__
import vtk_parser
import inspect

from core.modules.module_registry import addModule, addInputPort, addOutputPort, registry
from core.modules.vistrails_module import newModule
import core.modules.vistrails_module
import core.modules.basic_modules as basic
from core.debug import critical, warning, log
from base_module import vtkBaseModule

parser = vtk_parser.VTKMethodParser()

################################################################################
# initialize

def addPorts(module):
    typeMapDict = {'int': basic.Integer,
                   'float': basic.Float,
                   'char*': basic.String,
                   'char *': basic.String,
                   'string': basic.String,
                   'char': basic.String,
                   'const char*': basic.String,
                   'const char *': basic.String}
    def typeMap(name):
        if type(name) == __builtin__.tuple:
            return [typeMap(x) for x in name]
        if typeMapDict.has_key(name):
            return typeMapDict[name]
        else:
            try:
                return registry.getDescriptorByName(name).module
            except:
                return None

    addOutputPort(module, 'self', module)

    ### Add special vtkAlgorithm ports
    if issubclass(module.vtkClass, vtk.vtkAlgorithm):
        if module.vtkClass!=vtk.vtkStructuredPointsGeometryFilter:
            try:
                instance = module.vtkClass()
                for i in range(0,instance.GetNumberOfInputPorts()):
                    addInputPort(module, 'SetInputConnection%d'%i,
                                 registry.getDescriptorByName('vtkAlgorithmOutput').module)
                for i in range(0,instance.GetNumberOfOutputPorts()):
                    addOutputPort(module, 'GetOutputPort%d'%i,                                      
                                  registry.getDescriptorByName('vtkAlgorithmOutput').module)
                del instance
            except:
                pass

    parser.parse(module.vtkClass)
    get_set_dict = parser.get_get_set_methods()
    toggle_dict = parser.get_toggle_methods()
    state_dict = parser.get_state_methods()
    other_list = parser.get_other_methods()    
    
    for name in get_set_dict.iterkeys():
        if name in ['InputConnection', 'OutputPort']: continue
        getterMethod = getattr(module.vtkClass, 'Get%s'%name)
        setterMethod = getattr(module.vtkClass, 'Set%s'%name)
        getterSignature = parser.get_method_signature(getterMethod)
        setterSignature = parser.get_method_signature(setterMethod)
        for getter, order in zip(getterSignature, range(1, len(getterSignature)+1)):
            if getter[1]:
                log("Can't handle getter %s (%s) of class %s: Needs input to get output" % (order, name, module.vtkClass))
                continue
            if len(getter[0]) != 1:
                log("Can't handle getter %s (%s) of class %s: More than a single output" % (order, name, module.vtkClass))
                continue
            addOutputPort(module, 'Get'+name, typeMap(getter[0][0]), True)
        for setter, order in zip(setterSignature, range(1, len(setterSignature)+1)):
            try:
                if len(setter[1])==1:                    
                    addInputPort(module, 'Set'+name, typeMap(setter[1][0]), setter[1][0] in typeMapDict)
                else:
                    addInputPort(module, 'Set'+name, [typeMap(i) for i in setter[1]], True)
            except IndexError, e:
                print "module",module,"name",name
                print setter
                raise

    for name in toggle_dict.iterkeys():
        addInputPort(module, name+'On', [], True)
        addInputPort(module, name+'Off', [], True)

    for name in state_dict.iterkeys():
        for mode in state_dict[name]:
            addInputPort(module, 'Set'+name+'To'+mode[0], [], True)

    for name in other_list:
        if name[:3]=='Add' or name[:6]=='Insert':
            addSignature = parser.get_method_signature(getattr(module.vtkClass, name))
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
                        addInputPort(module, name, types[0], types[0] in typeMapDict.itervalues())
                    else:
                        addInputPort(module, name, types, True)
        else:
            signatures = parser.get_method_signature(getattr(module.vtkClass, name))
            for sig in signatures:
                ([result], params) = sig
                if params:
                    types = [typeMap(p) for p in params]
                else:
                    types = []
                if len(types)==0 or (result==None):
                    addInputPort(module, name, types, True)

def setAllPorts(treeNode):
    addPorts(treeNode.descriptor.module)
    for child in treeNode.children:
        setAllPorts(child)

def createModule(baseModule, node):
    module = newModule(baseModule, node.name)
    # This is sitting on the class
    module.vtkClass = node.klass
    addModule(module)
    for child in node.children:
        createModule(module, child)

def createAllModules(g):
    assert len(g.tree[0]) == 1
    base = g.tree[0][0]
    assert base.name == 'vtkObjectBase'
    vtkObjectBase = newModule(vtkBaseModule, 'vtkObjectBase')
    vtkObjectBase.vtkClass = vtk.vtkObjectBase
    addModule(vtkObjectBase)
    for children in base.children:
        createModule(vtkObjectBase, children)

def initialize():
    import class_tree
    inheritanceGraph = class_tree.ClassTree(vtk)
    inheritanceGraph.create()
    addModule(vtkBaseModule)
    createAllModules(inheritanceGraph)
    setAllPorts(registry.moduleTree['vtkObjectBase'])

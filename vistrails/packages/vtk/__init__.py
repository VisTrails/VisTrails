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
import re

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
typeMapDictValues = [Integer, Float, String]

def typeMap(name):
    """ typeMap(name: str) -> Module
    Convert from C/C++ types into VisTrails Module type
    
    """
    if type(name) == tuple:
        return [typeMap(x) for x in name]
    if name in typeMapDict:
        return typeMapDict[name]
    else:
        node = registry.moduleTree.get(name, None)
        if node:
            return node.descriptor.module
        else:
            return None

def get_method_signature(method):
    """ get_method_signature(method: vtkmethod) -> [ret, arg]
    Re-wrap Prabu's method to increase performance
    
    """
    doc = method.__doc__
    tmp = doc.split('\n')
    sig = []        
    pat = re.compile(r'\b')

    # Remove all the C++ function signatures and V.<method_name> field
    offset = 2+len(method.__name__)
    for i in range(len(tmp)):
        s = tmp[i]
        if s=='': break
        if i%2==0:
            x = s.split('->')
            arg = x[0].strip()[offset:]
            if len(x) == 1: # No return value
                ret = None
            else:
                ret = x[1].strip()

            # Remove leading and trailing parens for arguments.
            arg = arg[1:-1]
            if not arg:
                arg = None
            if arg and arg[-1] == ')':
                arg = arg + ','

            # Now quote the args and eval them.  Easy!
            if ret and ret[:3]!='vtk':
                ret = eval(pat.sub('\"', ret))
            if arg:
                if arg.find('(')!=-1:
                    arg = eval(pat.sub('\"', arg))
                else:
                    arg = arg.split(', ')
                    if len(arg)>1:
                        arg = tuple(arg)
                    else:
                        arg = arg[0]
                if type(arg) == str:
                    arg = [arg]

            sig.append(([ret], arg))
    return sig    

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
        getterSig = get_method_signature(getterMethod)
        setterSig = get_method_signature(setterMethod)
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
        if name[:3] in ['Add','Set'] or name[:6]=='Insert':
            method = getattr(module.vtkClass, name)
            signatures = get_method_signature(method)
            for sig in signatures:
                ([result], params) = sig
                types = []
                if params:
                    for p in params:
                        t = typeMap(p)
                        if not t:
                            types = None
                            break
                        else: types.append(t)
                else:
                    types = [[]]
                if types:
                    if len(types)<=1:
                        addInputPort(module, name, types[0],
                                     types[0] in typeMapDictValues)
                    else:
                        addInputPort(module, name, types, True)
#         else:
#             method = getattr(module.vtkClass, name)
#             signatures = get_method_signature(method)
#             for sig in signatures:
#                 ([result], params) = sig
#                 types = []
#                 if params:
#                     types = [typeMap(p) for p in params]
#                 else:
#                     types = []
#                 if types==[] or (result==None):
#                     addInputPort(module, name, types, True)
    
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
    registry.setCurrentPackageName('VTK')
    # Check VTK version
    v = vtk.vtkVersion()
    version = [v.GetVTKMajorVersion(),
               v.GetVTKMinorVersion(),
               v.GetVTKBuildVersion()]
    if version < [5, 0, 0]:
        raise Exception("You need to upgrade your VTK install to version \
        > >= 5.0.0")
    inheritanceGraph = ClassTree(vtk)
    inheritanceGraph.create()
    addModule(vtkBaseModule)
    createAllModules(inheritanceGraph)
    setAllPorts(registry.moduleTree['vtkObjectBase'])

    # Register the VTKCell type if the spreadsheet is up
    if registry.hasModule('SpreadsheetCell'):
        from vtkcell import VTKCell
        from packages.spreadsheet.basic_widgets import CellLocation
        addModule(VTKCell)
        addInputPort(VTKCell, "Location", CellLocation)
        addInputPort(VTKCell, "AddRenderer",
                     registry.getDescriptorByName('vtkRenderer').module)

def package_dependencies():
    import core.packagemanager
    manager = core.packagemanager.get_package_manager()
    if manager.has_package('spreadsheet'):
        return ['spreadsheet']
    else:
        return []

def package_requirements():
    import core.requirements
    if not core.requirements.python_module_exists('vtk'):
        raise core.requirements.MissingRequirement('vtk')
    if not core.requirements.python_module_exists('PyQt4'):
        print 'PyQt4 is not available. There will be no interaction',
        print 'between VTK and the spreadsheet.'
    import vtk

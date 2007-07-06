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

from core.bundles import py_import

vtk = py_import('vtk', {'linux-ubuntu': 'python-vtk'})

from core.utils import all
from core.debug import log
from core.modules.basic_modules import Integer, Float, String, File
from core.modules.module_registry import (registry, addModule,
                                          addInputPort, addOutputPort)
from core.modules.vistrails_module import newModule, ModuleError
from base_module import vtkBaseModule
from class_tree import ClassTree
from vtk_parser import VTKMethodParser
import re
import os.path

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

disallowed_classes = set(
    [
    'vtkCriticalSection',
    'vtkDataArraySelection',
    'vtkDebugLeaks',
    'vtkDirectory',
    'vtkDynamicLoader',
    'vtkFunctionParser',
    'vtkGarbageCollector',
    'vtkHeap',
    'vtkInformationKey',
    'vtkInstantiator',
    'vtkMath',
    'vtkModelMetadata',
    'vtkMultiProcessController',
    'vtkMutexLock',
    'vtkOutputWindow',
    'vtkPriorityQueue',
    'vtkReferenceCount',
    'vtkRenderWindowInteractor',
    'vtkTesting',
    'vtkWindow',
     ])

def is_class_allowed(module):
    if module is None:
        return False
    try:
        name = module.__name__
        return not (name in disallowed_classes)
    except AttributeError:
        return True

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

disallowed_set_get_ports = set(['ReferenceCount',
                                'InputConnection',
                                'OutputPort',
                                'Progress',
                                'ProgressText',
                                'InputArrayToProcess',
                                ])
def addSetGetPorts(module, get_set_dict):
    """ addSetGetPorts(module: Module, get_set_dict: dict) -> None
    Convert all Setxxx methods of module into input ports and all Getxxx
    methods of module into output ports

    Keyword arguments:
    module       --- Module
    get_set_dict --- the Set/Get method signatures returned by vtk_parser

    """
    for name in get_set_dict.iterkeys():
        if name in disallowed_set_get_ports: continue
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
                    "single output" % (order, name, str(module.vtkClass)))
                continue
            class_ = typeMap(getter[0][0])
            if is_class_allowed(class_):
                addOutputPort(module, 'Get'+name, class_, True)
        for setter, order in zip(setterSig, range(1, len(setterSig)+1)):
            try:
                if len(setter[1]) == 1 and is_class_allowed(typeMap(setter[1][0])):
                    addInputPort(module, 'Set'+name,
                                 typeMap(setter[1][0]),
                                 setter[1][0] in typeMapDict)
                else:
                    classes = [typeMap(i) for i in setter[1]]
                    if all(classes, is_class_allowed):
                        addInputPort(module, 'Set'+name, classes, True)
                # Wrap SetFileNames for VisTrails file access
                if name == 'FileName':
                    addInputPort(module, 'SetFile', (File, 'input file'),
                                 False)
            except IndexError, e:
                print "module", module, "name", name, setter
                raise

disallowed_toggle_ports = set(['GlobalWarningDisplay',
                               'Debug',
                               ])
def addTogglePorts(module, toggle_dict):
    """ addTogglePorts(module: Module, toggle_dict: dict) -> None
    Convert all xxxOn/Off methods of module into input ports

    Keyword arguments:
    module      --- Module
    toggle_dict --- the Toggle method signatures returned by vtk_parser

    """
    for name in toggle_dict.iterkeys():
        if name in disallowed_toggle_ports:
            continue
        addInputPort(module, name+'On', [], True)
        addInputPort(module, name+'Off', [], True)

disallowed_state_ports = set(['SetInputArrayToProcess'])
def addStatePorts(module, state_dict):
    """ addStatePorts(module: Module, state_dict: dict) -> None
    Convert all SetxxxToyyy methods of module into input ports

    Keyword arguments:
    module     --- Module
    state_dict --- the State method signatures returned by vtk_parser

    """
    for name in state_dict.iterkeys():
        for mode in state_dict[name]:
            field = 'Set'+name+'To'+mode[0]
            if field in disallowed_state_ports:
                continue
            addInputPort(module, field, [], True)

disallowed_other_ports = set(
    ['DeepCopy',
     'IsA',
     'NewInstance',
     'ShallowCopy',
     'SafeDownCast',
     'BreakOnError',
     'FastDelete',
     'PrintRevisions',
     'Modified',
     'RemoveObserver',
     'RemoveObservers',
     'INPUT_IS_OPTIONAL',
     'INPUT_IS_REPEATABLE',
     'INPUT_REQUIRED_FIELDS',
     'HasExecutive',
     'INPUT_REQUIRED_DATA_TYPE',
     'INPUT_ARRAYS_TO_PROCESS',
     'INPUT_CONNECTION',
     'INPUT_PORT',
     'RemoveAllInputs',
     'Update',
     'UpdateProgress',
     'UpdateInformation',
     'UpdateWholeExtent',
     'SetInputArrayToProcess'
     ])

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
            if name in disallowed_other_ports:
                continue
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
                    if not all(types, is_class_allowed):
                        continue
                    if len(types)<=1:
                        addInputPort(module, name, types[0],
                                     types[0] in typeMapDictValues)
                    else:
                        addInputPort(module, name, types, True)
        else:
            if name in disallowed_other_ports:
                continue
#             print "other: %s %s" % (module.vtkClass.__name__, name)
            method = getattr(module.vtkClass, name)
            signatures = get_method_signature(method)
            for sig in signatures:
                ([result], params) = sig
                types = []
                if params:
                    types = [typeMap(p) for p in params]
                else:
                    types = []
                if not all(types, is_class_allowed):
                    continue
                if types==[] or (result==None):
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
    # CVS version of VTK doesn't support AddInputConnect(vtkAlgorithmOutput)
    if module.vtkClass==vtk.vtkAlgorithm:
        addInputPort(module, 'AddInputConnection',
                     typeMap('vtkAlgorithmOutput'))
    # Somehow vtkProbeFilter.GetOutput cannot be found in any port list
    if module.vtkClass==vtk.vtkProbeFilter:
        addOutputPort(module, 'GetOutput',
                      typeMap('vtkPolyData'), True)

def setAllPorts(treeNode):
    """ setAllPorts(treeNode: TreeNode) -> None
    Traverse treeNode and all of its children/grand-children to add all ports

    """
    addPorts(treeNode.descriptor.module)
    for child in treeNode.children:
        setAllPorts(child)

def class_dict(base_module, node):
    """class_dict(base_module, node) -> dict
    Returns the class dictionary for the module represented by node and
    with base class base_module"""

    class_dict_ = {}
    def update_dict(name, callable_):
        if class_dict_.has_key(name):
            class_dict_[name] = callable_(class_dict_[name])
        elif hasattr(base_module, name):
            class_dict_[name] = callable_(getattr(base_module, name))
        else:
            class_dict_[name] = callable_(None)

    def guarded_SetFileName_wrap_compute(old_compute):
        def compute(self):
            if self.hasInputFromPort('SetFileName'):
                name = self.getInputFromPort('SetFileName')
            elif self.hasInputFromPort('SetFile'):
                name = self.getInputFromPort('SetFile').name
            else:
                raise ModuleError(self, 'Missing filename')
            if not os.path.isfile(name):
                raise ModuleError(self, 'File does not exist')
            old_compute(self)
        return compute

    def compute_SetFile(old_compute_SetFile):
        if old_compute_SetFile != None:
            return old_compute_SetFile
        def call_SetFile(self, file_obj):
            self.vtkInstance.SetFileName(file_obj.name)
        return call_SetFile

    if hasattr(node.klass, 'SetFileName'):
        update_dict('compute', guarded_SetFileName_wrap_compute)
        update_dict('_special_input_function_SetFile', compute_SetFile)

    return class_dict_

def createModule(baseModule, node):
    """ createModule(baseModule: a Module subclass, node: TreeNode) -> None
    Construct a module inherits baseModule with specification from node
    
    """
    def obsolete_class_list():
        lst = []
        items = ['vtkInteractorStyleTrackball',
                 'vtkStructuredPointsGeometryFilter',
                 'vtkConstrainedPointHandleRepresentation']
        def try_to_add_item(item):
            try:
                lst.append(getattr(vtk, item))
            except AttributeError:
                pass
        for item in items:
            try_to_add_item(item)
        return lst

    obsolete_list = obsolete_class_list()
    
    def is_abstract():
        """is_abstract tries to instantiate the class. If it's
        abstract, this will raise."""
        # Consider obsolete classes abstract        
        if node.klass in obsolete_list:
            return True
        try:
            getattr(vtk, node.name)()
        except TypeError: # VTK raises type error on abstract classes
            return True
        return False
    module = newModule(baseModule, node.name,
                       class_dict(baseModule, node))
    # This is sitting on the class
    module.vtkClass = node.klass
    addModule(module, abstract=is_abstract())
    for child in node.children:
        if child.name in disallowed_classes:
            continue
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
    for child in base.children:
        if child.name in disallowed_classes:
            continue
        createModule(vtkObjectBase, child)

##############################################################################
# Convenience methods

def extract_vtk_instance(vistrails_obj):
    """extract_vtk_instance(vistrails_obj) -> vtk_object

    takes an instance of a VisTrails module that is a subclass
    of the vtkObjectBase module and returns the corresponding
    instance."""
    vtkObjectBase = registry.getDescriptorByName('vtkObjectBase').module
    assert isinstance(vistrails_obj, vtkObjectBase)
    return vistrails_obj.vtkInstance

def wrap_vtk_instance(vtk_obj):
    """wrap_vtk_instance(vtk_object) -> VisTrails module

    takes a vtk instance and returns a corresponding
    wrapped instance of a VisTrails module"""
    assert isinstance(vtk_obj, vtk.vtkObjectBase)
    m = registry.getDescriptorByName(vtk_obj.GetClassName())
    result = m.module()
    result.vtkInstance = vtk_obj
    return result

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
        import vtkhandler
        import vtkcell
        vtkhandler.registerSelf()
        vtkcell.registerSelf()

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

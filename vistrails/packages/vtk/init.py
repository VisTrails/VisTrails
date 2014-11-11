###############################################################################
##
## Copyright (C) 2011-2014, NYU-Poly.
## Copyright (C) 2006-2011, University of Utah. 
## All rights reserved.
## Contact: contact@vistrails.org
##
## This file is part of VisTrails.
##
## "Redistribution and use in source and binary forms, with or without 
## modification, are permitted provided that the following conditions are met:
##
##  - Redistributions of source code must retain the above copyright notice, 
##    this list of conditions and the following disclaimer.
##  - Redistributions in binary form must reproduce the above copyright 
##    notice, this list of conditions and the following disclaimer in the 
##    documentation and/or other materials provided with the distribution.
##  - Neither the name of the University of Utah nor the names of its 
##    contributors may be used to endorse or promote products derived from 
##    this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
## AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
## THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR 
## PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR 
## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; 
## OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
## WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR 
## OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF 
## ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
###############################################################################
################################################################################
# VTK Package for VisTrails
################################################################################

from vistrails.core.debug import debug, warning, unexpected_exception
from vistrails.core.modules.basic_modules import Integer, Float, String, File, \
     Color, PathObject, identifier as basic_pkg
from vistrails.core.modules.module_registry import get_module_registry
from vistrails.core.modules.vistrails_module import new_module, ModuleError
from vistrails.core.system import get_vistrails_default_pkg_prefix
from identifiers import identifier as vtk_pkg_identifier
from vistrails.core.upgradeworkflow import UpgradeWorkflowHandler
from vistrails.core.utils import all, any, InstanceObject
from vistrails.core.vistrail.connection import Connection

from ast import literal_eval
from hasher import vtk_hasher
from itertools import izip
import os.path
import re
import warnings

import vtk

from base_module import vtkBaseModule, vtkRendererOutput
from class_tree import ClassTree
import fix_classes
import inspectors
import offscreen
import tf_widget
from vtk_parser import VTKMethodParser


#TODO: Change the Core > Module > Registry > Add Input : To support vector as type.

################################################################################

# filter some deprecation warnings coming from the fact that vtk calls
# range() with float parameters

warnings.filterwarnings("ignore",
                        message="integer argument expected, got float")

################################################################################
v = vtk.vtkVersion()
version = [v.GetVTKMajorVersion(),
           v.GetVTKMinorVersion(),
           v.GetVTKBuildVersion()]
if version < [5, 0, 4]:
    def get_description_class(klass):
        """Because sometimes we need to patch VTK classes, the klass that
        has the methods is different than the klass we want to
        instantiate. get_description_class makes sure that for patched
        classes we get the correct one."""
        try:
            return fix_classes.description[klass]
        except KeyError:
            return klass
else:
    # On VTK 5.0.4, we use the id of the class to hash, because it
    # seems that VTK hasn't implemented hash() correctly for their
    # classes.
    def get_description_class(klass):
        """Because sometimes we need to patch VTK classes, the klass that
        has the methods is different than the klass we want to
        instantiate. get_description_class makes sure that for patched
        classes we get the correct one."""
        try:
            return fix_classes.description[id(klass)]
        except KeyError:
            return klass

parser = VTKMethodParser()

typeMapDict = {'int': Integer,
               'long': Integer,
               'float': Float,
               'char*': String,
               'char *': String,
               'string': String,
               'char': String,
               'const char*': String,
               'const char *': String,
               '[float': Float,         
               'float]': Float,
               '[int': Integer,
               'int]': Integer}
typeMapDictValues = [Integer, Float, String]

file_name_pattern = re.compile('.*FileName$')
set_file_name_pattern = re.compile('Set.*FileName$')

_upgrade_self_to_instance_modules = set()

def resolve_overloaded_name(name, ix, signatures):
    # VTK supports static overloading, VisTrails does not. The
    # solution is to check whether the current function has
    # overloads and change the names appropriately.
    if len(signatures) == 1:
        return name
    else:
        return name + '_' + str(ix+1)

def typeMap(name, package=None):
    """ typeMap(name: str) -> Module
    Convert from C/C++ types into VisTrails Module type
    
    """
    if package is None:
        package = identifier
    if isinstance(name, tuple):
        return [typeMap(x, package) for x in name]
    if name in typeMapDict:
        return typeMapDict[name]
    else:
        registry = get_module_registry()
        if not registry.has_descriptor_with_name(package, name):
            return None
        else:
            return registry.get_descriptor_by_name(package,
                                                   name).module

def get_method_signature(method, docum='', name=''):
    """ get_method_signature(method: vtkmethod) -> [ret, arg]
    Re-wrap Prabu's method to increase performance

    """
    doc = method.__doc__ if docum=='' else docum
    tmptmp = doc.split('\n')
    tmp = []
    for l in tmptmp:
        l = l.strip('\n \t')
        if l.startswith('V.') or l.startswith('C++:'):
            tmp.append(l)
        else:
            if (len(tmp) != 0):       
                tmp[-1] = tmp[-1] + ' ' + l
    tmp.append('')
    sig = []        
    pat = re.compile(r'\b')

    # Remove all the C++ function signatures and V.<method_name> field  
    name = method.__name__ if name == '' else name
    offset = 2+len(name)
    for i in xrange(len(tmp)):
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
                try:
                    ret = literal_eval(pat.sub('\"', ret))
                except Exception:
                    continue
            if arg:
                if arg.find('(')!=-1:
                    try:
                        arg = literal_eval(pat.sub('\"', arg))
                    except Exception:
                        continue
                else:
                    arg = arg.split(', ')
                    if len(arg)>1:
                        arg = tuple(arg)
                    else:
                        arg = arg[0]
                if isinstance(arg, str):
                    arg = [arg]

            sig.append(([ret], arg))
    return sig    

def prune_signatures(module, name, signatures, output=False):
    """prune_signatures tries to remove redundant signatures to reduce
    overloading. It _mutates_ the given parameter.

    It does this by performing several operations:

    1) It compares a 'flattened' version of the types
    against the other 'flattened' signatures. If any of them match, we
    keep only the 'flatter' ones.

    A 'flattened' signature is one where parameters are not inside a
    tuple.

    2) We explicitly forbid a few signatures based on modules and names

    """
    # yeah, this is Omega(n^2) on the number of overloads. Who cares?

    def flatten(type_):
        if type_ is None:
            return []
        def convert(entry):
            if isinstance(entry, tuple):
                return list(entry)
            elif isinstance(entry, str):
                return [entry]
            else:
                result = []
                first = True
                lastList = True
                for e in entry:
                    if (isinstance(e, list)):
                        if lastList == False: result[len(result)] = result[len(result)] + ']'  
                        aux = e
                        aux.reverse()
                        aux[0] = '[' + aux[0]
                        aux[-1] = aux[-1] + ']'
                        result.extend(aux)
                        lastList = True
                    else:
                        if first: e = '[' + e
                        result.append(e)
                        lastList = False
                        first = False
                return result
        result = []
        for entry in type_:
            result.extend(convert(entry))
        return result
    flattened_entries = [flatten(sig[1]) for
                         sig in signatures]
    def hit_count(entry):
        result = 0
        for entry in flattened_entries:
            if entry in flattened_entries:
                result += 1
        return result
    hits = [hit_count(entry) for entry in flattened_entries]

    def forbidden(flattened, hit_count, original):
        if (issubclass(get_description_class(module.vtkClass), vtk.vtk3DWidget) and
            name == 'PlaceWidget' and
            flattened == []):
            return True
        # We forbid this because addPorts hardcodes this but
        # SetInputArrayToProcess is an exception for the InfoVis
        # package
        if (get_description_class(module.vtkClass) == vtk.vtkAlgorithm and
            name!='SetInputArrayToProcess'):
            return True
        return False

    # This is messy: a signature is only allowed if there's no
    # explicit disallowing of it. Then, if it's not overloaded,
    # it is also allowed. If it is overloaded and not the flattened
    # version, it is pruned. If these are output ports, there can be
    # no parameters.

    def passes(flattened, hit_count, original):
        if forbidden(flattened, hit_count, original):
            return False
        if hit_count == 1:
            return True
        if original[1] is None:
            return True
        if output and len(original[1]) > 0:
            return False
        if hit_count > 1 and len(original[1]) == len(flattened):
            return True
        return False
    
    signatures[:] = [original for (flattened, hit_count, original)
                     in izip(flattened_entries,
                             hits,
                             signatures)
                     if passes(flattened, hit_count, original)]
    
    #then we remove the duplicates, if necessary
    unique_signatures = []
    
    #Remove the arrays and tuples inside the signature
    #  in order to transform it in a single array
    #Also remove the '[]' from the Strings
    def removeBracts(signatures):
        result = []
        stack = list(signatures)
        while (len(stack) != 0):
            curr = stack.pop(0)
            if (isinstance(curr, (String, str))):
                c = curr.replace('[', '')
                c = c.replace(']', '')
                result.append(c)
            elif (curr == None):
                result.append(curr)
            elif (isinstance(curr, list)):
                curr.reverse()
                for c in curr: stack.insert(0, c)
            elif (isinstance(curr, tuple)):
                cc = list(curr)
                cc.reverse()
                for c in cc: stack.insert(0, c)
            else:
                result.append(curr)
        return result

    unique2 = []
    for s in signatures:
        aux = removeBracts(s)
        if not unique2.count(aux): 
            unique_signatures.append(s)
            unique2.append(aux)
    signatures[:] = unique_signatures
    
disallowed_classes = set(
    [
    'simplewrapper', # ticket 464: VTK 5.10 on OpenSuSE needs this
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
    'vtkLogLookupTable', # VTK: use vtkLookupTable.SetScaleToLog10() instead
    'vtkMath',
    'vtkModelMetadata',
    'vtkMultiProcessController',
    'vtkMutexLock',
    'vtkOutputWindow',
    'vtkPriorityQueue',
    'vtkQtInitialization',
    'vtkReferenceCount',
    'vtkRenderWindowCollection',
    'vtkRenderWindowInteractor',
    'vtkTesting',
    'vtkWindow',
    'vtkContext2D',       #Not working for VTK 5.7.0
    'vtkPLYWriter',       #Not working for VTK 5.7.0. 
    'vtkBooleanTexture',  #Not working for VTK 5.7.0
    'vtkImageMaskBits',   #Not working for VTK 5.7.0
    'vtkHardwareSelector',#Not working for VTK 5.7.0
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
    if issubclass(get_description_class(module.vtkClass), vtk.vtkAlgorithm):
        if get_description_class(module.vtkClass)!=vtk.vtkStructuredPointsGeometryFilter:
            # We try to instantiate the class here to get the number of
            # ports and to avoid abstract classes
            try:
                instance = module.vtkClass()
            except TypeError:
                pass
            else:
                reg = get_module_registry()
                des = reg.get_descriptor_by_name(vtk_pkg_identifier,
                                                      'vtkAlgorithmOutput')
                for i in xrange(0,instance.GetNumberOfInputPorts()):
                    reg.add_input_port(module, 'SetInputConnection%d'%i,
                                       des.module, 
                                       docstring=\
                                           module.get_doc('SetInputConnection'))
                for i in xrange(0,instance.GetNumberOfOutputPorts()):
                    reg.add_output_port(module, 'GetOutputPort%d'%i, 
                                        des.module, 
                                        docstring=\
                                            module.get_doc('GetOutputPort'))

disallowed_set_get_ports = set(['ReferenceCount',
                                'InputConnection',
                                'OutputPort',
                                'Progress',
                                'ProgressText',
                                'InputArrayToProcess',
                                ])
def addSetGetPorts(module, get_set_dict, delayed):
    """ addSetGetPorts(module: Module, get_set_dict: dict) -> None
    Convert all Setxxx methods of module into input ports and all Getxxx
    methods of module into output ports

    Keyword arguments:
    module       --- Module
    get_set_dict --- the Set/Get method signatures returned by vtk_parser

    """

    klass = get_description_class(module.vtkClass)
    registry = get_module_registry()
    for name in get_set_dict.iterkeys():
        if name in disallowed_set_get_ports: continue
        getterMethod = getattr(klass, 'Get%s'%name)
        setterMethod = getattr(klass, 'Set%s'%name)
        getterSig = get_method_signature(getterMethod)
        setterSig = get_method_signature(setterMethod)
        if len(getterSig) > 1:
            prune_signatures(module, 'Get%s'%name, getterSig, output=True)
        for order, getter in enumerate(getterSig):
            if getter[1]:
                debug("Can't handle getter %s (%s) of class %s: Needs input to "
                    "get output" % (order+1, name, klass))
                continue
            if len(getter[0]) != 1:
                debug("Can't handle getter %s (%s) of class %s: More than a "
                    "single output" % (order+1, name, str(klass)))
                continue
            class_ = typeMap(getter[0][0])
            if is_class_allowed(class_):
                port_name = 'Get'+name
                registry.add_output_port(module, port_name, class_, True,
                                         docstring=module.get_doc(port_name))
        if len(setterSig) > 1:
            prune_signatures(module, 'Set%s'%name, setterSig)
        for ix, setter in enumerate(setterSig):
            if setter[1]==None: continue
            n = resolve_overloaded_name('Set' + name, ix, setterSig)
            if len(setter[1]) == 1 and is_class_allowed(typeMap(setter[1][0])):
                registry.add_input_port(module, n,
                                        typeMap(setter[1][0]),
                                        setter[1][0] in typeMapDict,
                                        docstring=module.get_doc(n))
            else:
                classes = [typeMap(i) for i in setter[1]]

                if all(is_class_allowed(x) for x in classes):
                    registry.add_input_port(module, n, classes, True, 
                                            docstring=module.get_doc(n))


            # Wrap SetFileNames for VisTrails file access
            if file_name_pattern.match(name):
                # FIXME add documentation...
                registry.add_input_port(module, 'Set' + name[:-4], 
                                        (File, 'input file'), False)
            # Wrap SetRenderWindow for exporters
            elif name == 'RenderWindow':
                # cscheid 2008-07-11 This is messy: VTKCell isn't
                # registered yet, so we can't use it as a port
                # However, we can't register VTKCell before these either,
                # because VTKCell requires vtkRenderer. The "right" way would
                # be to add all modules first, then all ports. However, that would
                # be too slow.
                # Workaround: delay the addition of the port by storing
                # the information in a list
                if registry.has_module('%s.spreadsheet' % \
                                       get_vistrails_default_pkg_prefix(),
                                       'SpreadsheetCell'):
                    from vtkcell import VTKCell
                    # FIXME add documentation
                    delayed.add_input_port.append((module, 'SetVTKCell', VTKCell, False))
            # Wrap color methods for VisTrails GUI facilities
            # FIXME add documentation for all of these!
            elif name == 'DiffuseColor':
                registry.add_input_port(module, 'SetDiffuseColorWidget',
                                        (Color, 'color'), True)
            elif name == 'Color':
                registry.add_input_port(module, 'SetColorWidget', 
                                        (Color, 'color'), True)
            elif name == 'AmbientColor':
                registry.add_input_port(module, 'SetAmbientColorWidget',
                                        (Color, 'color'), True)
            elif name == 'SpecularColor':
                registry.add_input_port(module, 'SetSpecularColorWidget',
                                        (Color, 'color'), True)
            elif name == 'EdgeColor':
                registry.add_input_port(module, 'SetEdgeColorWidget',
                                        (Color, 'color'), True)
            elif name == 'Background' :
                registry.add_input_port(module, 'SetBackgroundWidget', 
                                        (Color, 'color'), True)
            elif name == 'Background2' :
                registry.add_input_port(module, 'SetBackground2Widget', 
                                        (Color, 'color'), True)

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
    registry = get_module_registry()
    for name in toggle_dict.iterkeys():
        if name in disallowed_toggle_ports:
            continue
        port_name = name+'On'
        registry.add_input_port(module, port_name, [], True,
                                docstring=module.get_doc(port_name))
        port_name = name+'Off'
        registry.add_input_port(module, port_name, [], True,
                                docstring=module.get_doc(port_name))

disallowed_state_ports = set(['SetInputArrayToProcess'])
def addStatePorts(module, state_dict):
    """ addStatePorts(module: Module, state_dict: dict) -> None
    Convert all SetxxxToyyy methods of module into input ports

    Keyword arguments:
    module     --- Module
    state_dict --- the State method signatures returned by vtk_parser

    """
    klass = get_description_class(module.vtkClass)
    registry = get_module_registry()
    for name in state_dict.iterkeys():
        for mode in state_dict[name]:
            # Creates the port Set foo to bar
            field = 'Set'+name+'To'+mode[0]
            if field in disallowed_state_ports:
                continue
            if not registry.has_input_port(module, field):
                registry.add_input_port(module, field, [], True,
                                        docstring=module.get_doc(field))

        # Now create the port Set foo with parameter
        if hasattr(klass, 'Set%s'%name):
            setterMethod = getattr(klass, 'Set%s'%name)
            setterSig = get_method_signature(setterMethod)
            # if the signature looks like an enum, we'll skip it, it shouldn't
            # be necessary
            if len(setterSig) > 1:
                prune_signatures(module, 'Set%s'%name, setterSig)
            for ix, setter in enumerate(setterSig):
                n = resolve_overloaded_name('Set' + name, ix, setterSig)
                tm = typeMap(setter[1][0])
                if len(setter[1]) == 1 and is_class_allowed(tm):
                    registry.add_input_port(module, n, tm,
                                            setter[1][0] in typeMapDict,
                                            docstring=module.get_doc(n))
                else:
                    classes = [typeMap(i) for i in setter[1]]
                    if all(is_class_allowed(x) for x in classes):
                        registry.add_input_port(module, n, classes, True,
                                                docstring=module.get_doc(n))

disallowed_other_ports = set(
    [
     'BreakOnError',
     'DeepCopy',
     'FastDelete',
     'HasObserver',
     'HasExecutive',
     'InvokeEvent',
     'IsA',
     'Modified',
     'NewInstance',
     'PrintRevisions',
     'RemoveAllInputs',
     'RemoveObserver',
     'RemoveObservers',
     'SafeDownCast',
#     'SetInputArrayToProcess',
     'ShallowCopy',
     'Update',
     'UpdateInformation',
     'UpdateProgress',
     'UpdateWholeExtent',
     # DAK: These are taken care of by s.upper() == s test
     # 'GUI_HIDE',
     # 'INPUT_ARRAYS_TO_PROCESS',
     # 'INPUT_CONNECTION',
     # 'INPUT_IS_OPTIONAL',
     # 'INPUT_IS_REPEATABLE',
     # 'INPUT_PORT',
     # 'INPUT_REQUIRED_DATA_TYPE',
     # 'INPUT_REQUIRED_FIELDS',
     # 'IS_INTERNAL_VOLUME',
     # 'IS_EXTERNAL_SURFACE',
     # 'MANAGES_METAINFORMATION',
     # 'POINT_DATA',
     # 'POINTS',
     # 'PRESERVES_ATTRIBUTES',
     # 'PRESERVES_BOUNDS',
     # 'PRESERVES_DATASET',
     # 'PRESERVES_GEOMETRY',
     # 'PRESERVES_RANGES',
     # 'PRESERVES_TOPOLOGY',
     ])



force_not_optional_port = set(
    ['ApplyViewTheme',
     ])


def addOtherPorts(module, other_list):
    """ addOtherPorts(module: Module, other_list: list) -> None
    Convert all other ports such as Insert/Add.... into input/output

    Keyword arguments:
    module     --- Module
    other_dict --- any other method signatures that is not
                   Algorithm/SetGet/Toggle/State type

    """
    klass = get_description_class(module.vtkClass)
    registry = get_module_registry()
    for name in other_list:
        if name=='CopyImportVoidPointer':
            # FIXME add documentation
            registry.add_input_port(module, 'CopyImportVoidString', (String, 'value'), False)
        if name[:3] in ['Add','Set'] or name[:6]=='Insert':
            if name in disallowed_other_ports:
                continue
            method = getattr(klass, name)
            signatures = ""
            if not isinstance(method, int):
                signatures = get_method_signature(method)

            if len(signatures) > 1:
                prune_signatures(module, name, signatures)
            for (ix, sig) in enumerate(signatures):
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
                    if not all(is_class_allowed(x) for x in types):
                        continue
                    n = resolve_overloaded_name(name, ix, signatures)
                    if len(types)<=1:
                        registry.add_input_port(module, n, types[0],
                                                types[0] in typeMapDictValues,
                                                docstring=module.get_doc(n))
                    else:
                        registry.add_input_port(module, n, types, True,
                                                docstring=module.get_doc(n))
        else:
            # DAK: check for static methods as name.upper() == name
            if name in disallowed_other_ports or name.upper() == name:
                continue
            method = getattr(klass, name)
            signatures = ""
            if not isinstance(method, int):
                signatures = get_method_signature(method)

            if len(signatures) > 1:
                prune_signatures(module, name, signatures)
            for (ix, sig) in enumerate(signatures):
                ([result], params) = sig
                types = []
                if params:
                    paramsList = list(params)
                    while (len(paramsList) != 0):
                        p = paramsList.pop(0)
                        if isinstance(p, list): 
                            for aux in p: paramsList.insert(0, aux)
                        else:
                            types.append(typeMap(p))
                else:
                    types = []
                if not all(is_class_allowed(x) for x in types):
                    continue
                if types==[] or (result==None):
                    n = resolve_overloaded_name(name, ix, signatures)
                    # print module.vtkClass.__name__, n
                    try:
                        doc = module.get_doc(n)
                    except Exception, e:
                        unexpected_exception(e)
                        warning("Error with %s" % module.vtkClass.__name, e)
                    else:
                        registry.add_input_port(module, n, types,
                                                not (n in force_not_optional_port),
                                                docstring=doc)

disallowed_get_ports = set([
    'GetClassName',
    'GetErrorCode',
    'GetNumberOfInputPorts',
    'GetNumberOfOutputPorts',
    'GetOutputPortInformation',
    'GetTotalNumberOfInputConnections',
    ])

def addGetPorts(module, get_list):
    klass = get_description_class(module.vtkClass)
    registry = get_module_registry()
    for name in get_list:
        if name in disallowed_get_ports:
            continue
        method = getattr(klass, name)
        signatures = get_method_signature(method)
        if len(signatures) > 1:
            prune_signatures(module, name, signatures, output=True)
        for ix, getter in enumerate(signatures):
            if getter[1] or len(getter[0]) > 1:
                continue
            class_ = typeMap(getter[0][0])
            if is_class_allowed(class_):
                if len(signatures) > 1:
                    n = name + "_" + str(ix+1)
                else:
                    n = name
                registry.add_output_port(module, n, class_, True,
                                         docstring=module.get_doc(n))
    
def addPorts(module, delayed):
    """ addPorts(module: VTK module inherited from Module,
                 delayed: object with add_input_port slot
    ) -> None
    
    Search all metamethods of module and add appropriate ports

    ports that cannot be added immediately should be appended to
    the delayed object that is passed. see the SetRenderWindow cases.

    """
    klass = get_description_class(module.vtkClass)
    registry = get_module_registry()
    registry.add_output_port(module, 'Instance', module)
    _upgrade_self_to_instance_modules.add(module)
    parser.parse(klass)
    addAlgorithmPorts(module)
    addGetPorts(module, parser.get_get_methods())
    addSetGetPorts(module, parser.get_get_set_methods(), delayed) 
    addTogglePorts(module, parser.get_toggle_methods())
    addStatePorts(module, parser.get_state_methods())
    addOtherPorts(module, parser.get_other_methods())             
    # CVS version of VTK doesn't support AddInputConnect(vtkAlgorithmOutput)
    # FIXME Add documentation
    basic_pkg = '%s.basic' % get_vistrails_default_pkg_prefix()
    if klass==vtk.vtkAlgorithm:
        registry.add_input_port(module, 'AddInputConnection',
                                typeMap('vtkAlgorithmOutput'))
    # vtkWriters have a custom File port
    elif klass==vtk.vtkWriter:
        registry.add_output_port(module, 'file', typeMap('File', basic_pkg))
    elif klass==vtk.vtkImageWriter:
        registry.add_output_port(module, 'file', typeMap('File', basic_pkg))
    elif klass==vtk.vtkVolumeProperty:
        registry.add_input_port(module, 'SetTransferFunction',
                                typeMap('TransferFunction'))
    elif klass==vtk.vtkDataSet:
        registry.add_input_port(module, 'SetPointData', typeMap('vtkPointData'))
        registry.add_input_port(module, 'SetCellData', typeMap('vtkCellData'))
    elif klass==vtk.vtkCell:
        registry.add_input_port(module, 'SetPointIds', typeMap('vtkIdList'))

def setAllPorts(descriptor, delayed):
    """ setAllPorts(descriptor: ModuleDescriptor) -> None
    Traverse descriptor and all of its children/grand-children to add all ports

    """
    addPorts(descriptor.module, delayed)
    for child in descriptor.children:
        setAllPorts(child, delayed)

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

    def guarded_SimpleScalarTree_wrap_compute(old_compute):
        # This builds the scalar tree and makes it cacheable

        def compute(self):
            self.is_cacheable = lambda *args, **kwargs: True
            old_compute(self)
            self.vtkInstance.BuildTree()
        return compute

    def guarded_SetFileName_wrap_compute(old_compute):
        # This checks for the presence of file in VTK readers
        def compute(self):

            # Skips the check if it's a vtkImageReader or vtkPLOT3DReader, because
            # it has other ways of specifying files, like SetFilePrefix for
            # multiple files
            skip = [vtk.vtkBYUReader,
                    vtk.vtkImageReader,
                    vtk.vtkDICOMImageReader,
                    vtk.vtkTIFFReader]

            # vtkPLOT3DReader does not exist from version 6.0.0
            v = vtk.vtkVersion()
            version = [v.GetVTKMajorVersion(),
                       v.GetVTKMinorVersion(),
                       v.GetVTKBuildVersion()]
            if version < [6, 0, 0]:
                skip.append(vtk.vtkPLOT3DReader)
            if any(issubclass(self.vtkClass, x) for x in skip):
                old_compute(self)
                return
            if self.has_input('SetFileName'):
                name = self.get_input('SetFileName')
            elif self.has_input('SetFile'):
                name = self.get_input('SetFile').name
            else:
                raise ModuleError(self, 'Missing filename')
            if not os.path.isfile(name):
                raise ModuleError(self, 'File does not exist')
            old_compute(self)
        return compute

    def compute_SetDiffuseColorWidget(old_compute):
        if old_compute != None:
            return old_compute
        def call_SetDiffuseColorWidget(self, color):
            self.vtkInstance.SetDiffuseColor(color.tuple)
        return call_SetDiffuseColorWidget

    def compute_SetAmbientColorWidget(old_compute):
        if old_compute != None:
            return old_compute
        def call_SetAmbientColorWidget(self, color):
            self.vtkInstance.SetAmbientColor(color.tuple)
        return call_SetAmbientColorWidget

    def compute_SetSpecularColorWidget(old_compute):
        if old_compute != None:
            return old_compute
        def call_SetSpecularColorWidget(self, color):
            self.vtkInstance.SetSpecularColor(color.tuple)
        return call_SetSpecularColorWidget

    def compute_SetColorWidget(old_compute):
        if old_compute != None:
            return old_compute
        def call_SetColorWidget(self, color):
            self.vtkInstance.SetColor(color.tuple)
        return call_SetColorWidget

    def compute_SetEdgeColorWidget(old_compute):
        if old_compute != None:
            return old_compute
        def call_SetEdgeColorWidget(self, color):
            self.vtkInstance.SetEdgeColor(color.tuple)
        return call_SetEdgeColorWidget
    
    def compute_SetBackgroundWidget(old_compute):
        if old_compute != None:
            return old_compute
        def call_SetBackgroundWidget(self, color):
            self.vtkInstance.SetBackground(color.tuple)
        return call_SetBackgroundWidget
    
    def compute_SetBackground2Widget(old_compute):
        if old_compute != None:
            return old_compute
        def call_SetBackground2Widget(self, color):
            self.vtkInstance.SetBackground2(color.tuple)
        return call_SetBackground2Widget
    
    def compute_SetVTKCell(old_compute):
        if old_compute != None:
            return old_compute
        def call_SetRenderWindow(self, cellObj):
            if cellObj.cellWidget:
                self.vtkInstance.SetRenderWindow(cellObj.cellWidget.mRenWin)
        return call_SetRenderWindow
    
    def compute_SetTransferFunction(old_compute):
        # This sets the transfer function
        if old_compute != None:
            return old_compute
        def call_SetTransferFunction(self, tf):
            tf.set_on_vtk_volume_property(self.vtkInstance)
        return call_SetTransferFunction

    def compute_SetPointData(old_compute):
        if old_compute != None:
            return old_compute
        def call_SetPointData(self, pd):
            self.vtkInstance.GetPointData().ShallowCopy(pd)
        return call_SetPointData

    def compute_SetCellData(old_compute):
        if old_compute != None:
            return old_compute
        def call_SetCellData(self, cd):
            self.vtkInstance.GetCellData().ShallowCopy(cd)
        return call_SetCellData            

    def compute_SetPointIds(old_compute):
        if old_compute != None:
            return old_compute
        def call_SetPointIds(self, point_ids):
            self.vtkInstance.GetPointIds().SetNumberOfIds(point_ids.GetNumberOfIds())
            for i in xrange(point_ids.GetNumberOfIds()):
                self.vtkInstance.GetPointIds().SetId(i, point_ids.GetId(i))
        return call_SetPointIds

    def compute_CopyImportString(old_compute):
        if old_compute != None:
            return old_compute
        def call_CopyImportVoidPointer(self, pointer):
            self.vtkInstance.CopyImportVoidPointer(pointer, len(pointer))
        return call_CopyImportVoidPointer

    def guarded_Writer_wrap_compute(old_compute):
        # The behavior for vtkWriter subclasses is to call Write()
        # If the user sets a name, we will create a file with that name
        # If not, we will create a temporary file from the file pool
        def compute(self):
            old_compute(self)
            fn = self.vtkInstance.GetFileName()
            if not fn:
                o = self.interpreter.filePool.create_file(suffix='.vtk')
                self.vtkInstance.SetFileName(o.name)
            else:
                o = PathObject(fn)
            self.vtkInstance.Write()
            self.set_output('file', o)
        return compute

    for var in dir(node.klass):
        # Everyone that has a Set.*FileName should have a Set.*File port too
        if set_file_name_pattern.match(var):
            def get_compute_SetFile(method_name):
                def compute_SetFile(old_compute):
                    if old_compute != None:
                        return old_compute
                    def call_SetFile(self, file_obj):
                        getattr(self.vtkInstance, method_name)(file_obj.name)
                    return call_SetFile
                return compute_SetFile
            update_dict('_special_input_function_' + var[:-4], 
                        get_compute_SetFile(var))

    if hasattr(node.klass, 'SetFileName'):
        # ... BUT we only want to check existence of filenames on
        # readers. VTK is nice enough to be consistent with names, but
        # this is brittle..
        if node.klass.__name__.endswith('Reader'):
            if not node.klass.__name__.endswith('TiffReader'):
                update_dict('compute', guarded_SetFileName_wrap_compute)
    if hasattr(node.klass, 'SetRenderWindow'):
        update_dict('_special_input_function_SetVTKCell',
                    compute_SetVTKCell)
    #color gui wrapping
    if hasattr(node.klass, 'SetDiffuseColor'):
        update_dict('_special_input_function_SetDiffuseColorWidget',
                    compute_SetDiffuseColorWidget)
    if hasattr(node.klass, 'SetAmbientColor'):
        update_dict('_special_input_function_SetAmbientColorWidget',
                    compute_SetAmbientColorWidget)
    if hasattr(node.klass, 'SetSpecularColor'):
        update_dict('_special_input_function_SetSpecularColorWidget',
                    compute_SetSpecularColorWidget)
    if hasattr(node.klass, 'SetEdgeColor'):
        update_dict('_special_input_function_SetEdgeColorWidget',
                    compute_SetEdgeColorWidget)
    if hasattr(node.klass, 'SetColor'):
        update_dict('_special_input_function_SetColorWidget',
                    compute_SetColorWidget)
    if (issubclass(node.klass, vtk.vtkRenderer) and 
        hasattr(node.klass, 'SetBackground')):
        update_dict('_special_input_function_SetBackgroundWidget',
                    compute_SetBackgroundWidget)
    if (issubclass(node.klass, vtk.vtkRenderer) and 
        hasattr(node.klass, 'SetBackground2')):
        update_dict('_special_input_function_SetBackground2Widget',
                    compute_SetBackground2Widget)    
    if issubclass(node.klass, vtk.vtkWriter):
        update_dict('compute', guarded_Writer_wrap_compute)

    if issubclass(node.klass, vtk.vtkScalarTree):
        update_dict('compute', guarded_SimpleScalarTree_wrap_compute)

    if issubclass(node.klass, vtk.vtkVolumeProperty):
        update_dict('_special_input_function_SetTransferFunction',
                    compute_SetTransferFunction)
    if issubclass(node.klass, vtk.vtkDataSet):
        update_dict('_special_input_function_SetPointData',
                    compute_SetPointData)
        update_dict('_special_input_function_SetCellData',
                    compute_SetCellData)
    if issubclass(node.klass, vtk.vtkCell):
        update_dict('_special_input_function_SetPointIds',
                    compute_SetPointIds)
    if issubclass(node.klass, vtk.vtkImageImport):
        update_dict('_special_input_function_CopyImportString',
                    compute_CopyImportString)
    return class_dict_

disallowed_modules = set([
        'vtkGeoAlignedImageCache',
        'vtkGeoTerrainCache',
        'vtkMPIGroup'
        ])
def createModule(baseModule, node):
    """ createModule(baseModule: a Module subclass, node: TreeNode) -> None
    Construct a module inherits baseModule with specification from node
    
    """
    if node.name in disallowed_modules: return
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
        except (TypeError, NotImplementedError): # VTK raises type error on abstract classes
            return True
        return False
    module = new_module(baseModule, node.name,
                       class_dict(baseModule, node),
                       docstring=getattr(vtk, node.name).__doc__
                       )

    # This is sitting on the class
    if hasattr(fix_classes, node.klass.__name__ + '_fixed'):
        module.vtkClass = getattr(fix_classes, node.klass.__name__ + '_fixed')
    else:
        module.vtkClass = node.klass
    registry = get_module_registry()
    registry.add_module(module, abstract=is_abstract(), 
                        signatureCallable=vtk_hasher)
    for child in node.children:
        if child.name in disallowed_classes:
            continue
        createModule(module, child)

def createAllModules(g):
    """ createAllModules(g: ClassTree) -> None
    Traverse the VTK class tree and add all modules into the module registry
    
    """
    v = vtk.vtkVersion()
    version = [v.GetVTKMajorVersion(),
               v.GetVTKMinorVersion(),
               v.GetVTKBuildVersion()]
    if version < [5, 7, 0]:
        assert len(g.tree[0]) == 1
        base = g.tree[0][0]
        assert base.name == 'vtkObjectBase'

    vtkObjectBase = new_module(vtkBaseModule, 'vtkObjectBase')
    vtkObjectBase.vtkClass = vtk.vtkObjectBase
    registry = get_module_registry()
    registry.add_module(vtkObjectBase)
    if version < [5, 7, 0]:
        for child in base.children:
            if child.name in disallowed_classes:
                continue
            createModule(vtkObjectBase, child)
    else:
        for base in g.tree[0]:
            for child in base.children:
                if child.name in disallowed_classes:
                    continue
                createModule(vtkObjectBase, child)


################################################################################

def initialize():
    """ initialize() -> None
    Package-entry to initialize the package
    
    """
    # Check VTK version
    v = vtk.vtkVersion()
    version = [v.GetVTKMajorVersion(),
               v.GetVTKMinorVersion(),
               v.GetVTKBuildVersion()]
    if version < [5, 0, 0]:
        raise RuntimeError("You need to upgrade your VTK install to version "
                           ">= 5.0.0")
    inheritanceGraph = ClassTree(vtk)
    inheritanceGraph.create()

    # Transfer Function constant
    tf_widget.initialize()

    delayed = InstanceObject(add_input_port=[])
    # Add VTK modules
    registry = get_module_registry()
    registry.add_module(vtkBaseModule)
    registry.add_module(vtkRendererOutput)
    createAllModules(inheritanceGraph)
    setAllPorts(registry.get_descriptor_by_name(identifier,
                                                'vtkObjectBase'),
                delayed)

    # Register the VTKCell and VTKHandler type if the spreadsheet is up
    if registry.has_module('%s.spreadsheet' % \
                           get_vistrails_default_pkg_prefix(),
                           'SpreadsheetCell'):
        import vtkhandler
        import vtkcell
        import vtkviewcell
        vtkhandler.registerSelf()
        vtkcell.registerSelf()
        vtkviewcell.registerSelf()

    # register offscreen rendering module
    offscreen.register_self()

    # Now add all "delayed" ports - see comment on addSetGetPorts
    for args in delayed.add_input_port:
        
        registry.add_input_port(*args)

    # register Transfer Function adjustment
    # This can't be reordered -- TransferFunction needs to go before
    # vtkVolumeProperty, but vtkScaledTransferFunction needs
    # to go after vtkAlgorithmOutput
    getter = registry.get_descriptor_by_name
    registry.add_module(tf_widget.vtkScaledTransferFunction)
    # FIXME Add documentation
    registry.add_input_port(tf_widget.vtkScaledTransferFunction,
                            'Input', getter(vtk_pkg_identifier,
                                            'vtkAlgorithmOutput').module)
    registry.add_input_port(tf_widget.vtkScaledTransferFunction,
                            'Dataset', getter (vtk_pkg_identifier,
                                               'vtkDataObject').module)
    registry.add_input_port(tf_widget.vtkScaledTransferFunction,
                            'Range', [Float, Float])
    registry.add_input_port(tf_widget.vtkScaledTransferFunction,
                            'TransferFunction',
                            tf_widget.TransferFunctionConstant)
    registry.add_output_port(tf_widget.vtkScaledTransferFunction,
                             'TransferFunction',
                             tf_widget.TransferFunctionConstant)
    registry.add_output_port(tf_widget.vtkScaledTransferFunction,
                             'vtkPiecewiseFunction',
                             getter(vtk_pkg_identifier, 
                                    'vtkPiecewiseFunction').module)
    registry.add_output_port(tf_widget.vtkScaledTransferFunction,
                             'vtkColorTransferFunction',
                             getter(vtk_pkg_identifier, 
                                    'vtkColorTransferFunction').module)

    inspectors.initialize()

################################################################################

_remap = None
_controller = None
_pipeline = None

def _get_controller():
    global _controller
    return _controller

def _get_pipeline():
    global _pipeline
    return _pipeline

def build_remap(module_name=None):
    global _remap, _controller

    reg = get_module_registry()
    uscore_num = re.compile(r"(.+)_(\d+)$")
    
    def get_port_specs(descriptor, port_type):
        ports = {}
        for desc in reversed(reg.get_module_hierarchy(descriptor)):
            ports.update(reg.module_ports(port_type, desc))
        return ports

    def build_remap_method(desc, port_prefix, port_num, port_type):
        # for connection, need to differentiate between src and dst
        if port_type == 'input':
            conn_lookup = Connection._get_destination
            get_port_spec = reg.get_input_port_spec
            idx = 1
        else:
            conn_lookup = Connection._get_source
            get_port_spec = reg.get_output_port_spec
            idx = 0

        def remap(old_conn, new_module):
            create_new_connection = UpgradeWorkflowHandler.create_new_connection
            port = conn_lookup(old_conn)
            pipeline = _get_pipeline()
            modules = [pipeline.modules[old_conn.source.moduleId],
                       pipeline.modules[old_conn.destination.moduleId]]
            modules[idx] = new_module
            ports = [old_conn.source, old_conn.destination]
            for i in xrange(1, port_num):
                port_name = "%s_%d" % (port_prefix, i)
                port_spec = get_port_spec(modules[idx], port_name)
                if port_spec.sigstring == port.signature:
                    ports[idx] = port_name
                    new_conn = create_new_connection(_get_controller(),
                                                     modules[0],
                                                     ports[0],
                                                     modules[1],
                                                     ports[1])
                    return [('add', new_conn)]
                                                                  
            # if get here, just try to use _1 version?
            ports[idx] = "%s_%d" % (port_prefix, 1)
            new_conn = create_new_connection(_get_controller(),
                                             modules[0],
                                             ports[0],
                                             modules[1],
                                             ports[1])
            return [('add', new_conn)]
        return remap

    def build_function_remap_method(desc, port_prefix, port_num):
        f_map = {"vtkCellArray": {"InsertNextCell": 3}}
        def build_function(old_function, new_function_name, new_module):
            controller = _get_controller()
            if len(old_function.parameters) > 0:
                new_param_vals, aliases = \
                    zip(*[(p.strValue, p.alias) 
                          for p in old_function.parameters])
            else:
                new_param_vals = []
                aliases = []
            new_function = controller.create_function(new_module, 
                                                      new_function_name,
                                                      new_param_vals,
                                                      aliases)
            return new_function
            
        def remap(old_function, new_module):
            for i in xrange(1, port_num):
                port_name = "%s_%d" % (port_prefix, i)
                port_spec = reg.get_input_port_spec(new_module, port_name)
                old_sigstring = \
                    reg.expand_port_spec_string(old_function.sigstring,
                                                basic_pkg)
                if port_spec.sigstring == old_sigstring:
                    new_function = build_function(old_function, port_name,
                                                  new_module)
                    new_module.add_function(new_function)
                    return []
            port_idx = 1
            if desc.name in f_map:
                if port_prefix in f_map[desc.name]:
                    port_idx =  f_map[desc.name][port_prefix]
            port_name = "%s_%d" % (port_prefix, port_idx)
            new_function = build_function(old_function, port_name, new_module)
            new_module.add_function(new_function)
            return []

        return remap
                    
    def process_ports(desc, port_type):
        if port_type == 'input':
            remap_dict_key = 'dst_port_remap'
        else:
            remap_dict_key = 'src_port_remap'
        ports = get_port_specs(desc, port_type)
        port_nums = {}
        for port_name, port_spec in ports.iteritems():
            # FIXME just start at 1 and go until don't find port (no
            # need to track max)?
            search_res = uscore_num.search(port_name)
            if search_res:
                port_prefix = search_res.group(1)
                port_num = int(search_res.group(2))
                if port_prefix not in port_nums:
                    port_nums[port_prefix] = port_num
                elif port_num > port_nums[port_prefix]:
                    port_nums[port_prefix] = port_num
        if desc.name not in _remap:
            _remap[desc.name] = [(None, '0.9.3', None, dict())]
        my_remap_dict = _remap[desc.name][0][3]
        for port_prefix, port_num in port_nums.iteritems():
            remap = build_remap_method(desc, port_prefix, port_num, port_type)
            my_remap_dict.setdefault(remap_dict_key, {})[port_prefix] = remap
            if port_type == 'input':
                remap = build_function_remap_method(desc, port_prefix, port_num)
                if 'function_remap' not in my_remap_dict:
                    my_remap_dict['function_remap'] = {}
                my_remap_dict['function_remap'][port_prefix] = remap
        if port_type == 'output' and issubclass(desc.module, vtkBaseModule):
            my_remap_dict.setdefault('src_port_remap', {})['self'] = 'Instance'

    pkg = reg.get_package_by_name(identifier)
    if module_name is not None:
        # print 'building remap for', module_name
        desc = reg.get_descriptor_by_name(identifier, module_name)
        process_ports(desc, 'input')
        process_ports(desc, 'output')
        if issubclass(desc.module, vtkBaseModule):
            _remap.setdefault(desc.name, []).append(('0.9.3', '0.9.5', None, {
                    'src_port_remap': {
                        'self': 'Instance',
                    }
                }))
    else:
        # print 'building entire remap'
        # FIXME do this by descriptor first, then build the hierarchies for each
        # module after that...
        for desc in pkg.descriptor_list:
            process_ports(desc, 'input')
            process_ports(desc, 'output')
            if issubclass(desc.module, vtkBaseModule):
                _remap.setdefault(desc.name, []).append(('0.9.3', '0.9.5', None, {
                        'src_port_remap': {
                            'self': 'Instance',
                        }
                    }))

def handle_module_upgrade_request(controller, module_id, pipeline):
    global _remap, _controller, _pipeline
    if _remap is None:
        _remap = {'vtkInteractionHandler': [(None, '0.9.5', None, {})]}
    
    _controller = controller
    _pipeline = pipeline
    module_name = pipeline.modules[module_id].name
    if module_name not in _remap:
        build_remap(module_name)
    return UpgradeWorkflowHandler.remap_module(controller, module_id, pipeline,
                                              _remap)

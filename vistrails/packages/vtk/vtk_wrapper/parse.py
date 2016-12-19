###############################################################################
##
## Copyright (C) 2014-2016, New York University.
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
##  - Neither the name of the New York University nor the names of its
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

from __future__ import division

from itertools import izip, chain
import re

import vtk

from .class_tree import ClassTree
from .specs import ClassSpec, SpecList, \
                   ClassInputPortSpec as InputPortSpec, \
                   ClassOutputPortSpec as OutputPortSpec
from .vtk_parser import VTKMethodParser

parser = VTKMethodParser()

disallowed_classes = set(
    [
        'simplewrapper', # ticket 464: VTK 5.10 on OpenSuSE needs this
        'vtkEventQtSlotConnect', # VTK 5.10.1 OpenSuSE (uses QObject)
        'vtkQtView', # VTK 5.10.1 OpenSuSE (uses QWidget)
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
        'vtkLogLookupTable', # use vtkLookupTable.SetScaleToLog10() instead
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
        'vtkOpenGLExtensionManager',

        # these show up with new parse
        'vtkAbstractContextBufferId',
        'vtkAbstractElectronicData',
        'vtkCallbackCommand',
        'vtkImageComplex',
        'vtkInformationDataObjectKey',
        'vtkInformationDoubleKey',
        'vtkInformationDoubleVectorKey',
        'vtkInformationIdTypeKey',
        'vtkInformationInformationKey',
        'vtkInformationInformationVectorKey',
        'vtkInformationIntegerKey',
        'vtkInformationIntegerPointerKey',
        'vtkInformationIntegerVectorKey',
        'vtkInformationKeyVectorKey',
        'vtkInformationObjectBaseKey',
        'vtkInformationRequestKey',
        'vtkInformationStringKey',
        'vtkInformationStringVectorKey',
        'vtkInformationUnsignedLongKey',
        'vtkRenderWindow',
        'vtkShaderProgram2',
        'vtkShadowMapBakerPassLightCameras',
        'vtkShadowMapBakerPassTextures',
        'vtkTDxMotionEventInfo',
        'vtkVolumeRayCastDynamicInfo',
        'vtkVolumeRayCastStaticInfo',
        # For VTK 5.8
        'vtkMPICommunicatorOpaqueComm',
        # For VTK 6
        'vtkBlueObeliskData',
        'vtkSocketController',
        'vtkMPIController',
        'vtkInformationVariantVectorKey',
        'vtkInformationVariantKey',
        'QImage',
        'vtkPLOT3DReader',
        # For VTK 6.2
        'QuantileDefinitionType'
    ])

disallowed_modules = set(
    [
        'vtkGeoAlignedImageCache',
        'vtkGeoTerrainCache',
        'vtkMPIGroup'
    ])

def create_module(base_cls_name, node):
    """create_module(base_cls_name: String, node: TreeNode) -> [ModuleSpec]

    Construct a module spec that inherits from base_cls_name with
    specification from node.

    """
    if node.name in disallowed_modules: return []
    if node.name == 'int': return [] #enum
    def obsolete_class_list():
        lst = []
        items = ['vtkInteractorStyleTrackball',
                 'vtkStructuredPointsGeometryFilter',
                 'vtkConstrainedPointHandleRepresentation',
                 'vtkRenderViewBase',
                 'vtkRenderView']
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

    try:
        node.klass.__doc__.decode('latin-1')
    except UnicodeDecodeError:
        print "ERROR decoding docstring", node.name
        raise

    input_ports, output_ports = get_ports(node.klass)
    output_ports = list(output_ports) # drop generator

    cacheable = (issubclass(node.klass, vtk.vtkAlgorithm) and
                 (not issubclass(node.klass, vtk.vtkAbstractMapper))) or \
                issubclass(node.klass, vtk.vtkScalarTree)

    is_algorithm = issubclass(node.klass, vtk.vtkAlgorithm)
    tempfile = '_set_tempfile' if issubclass(node.klass, vtk.vtkWriter) else None
    callback = '_set_callback' if is_algorithm else None
    methods_last = hasattr(node.klass, 'SetRenderWindow')

    module_spec = ClassSpec(node.name, base_cls_name, node.name,
                            node.klass.__doc__.decode('latin-1'), callback,
                            tempfile, cacheable, input_ports, output_ports,
                            compute='Update', cleanup='_cleanup',
                            methods_last=methods_last, abstract=is_abstract())

    module_specs = [module_spec]
    for child in node.children:
        if child.name in disallowed_classes:
            continue
        module_specs.extend(create_module(node.name, child))

    return module_specs

def get_doc(cls, port_name):
    f = re.match(r"(.*)_\d+$", port_name)
    if f:
        name = f.group(1)
    else:
        name = port_name

    doc = getattr(cls, name).__doc__
    # Remove all the C++ function signatures.
    idx = doc.find('\n\n')
    if idx > 0:
        doc = doc[idx+2:]
    return doc

def prune_signatures(cls, name, signatures, output=False):
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
        if (issubclass(cls, vtk.vtk3DWidget) and
            name == 'PlaceWidget' and
            flattened == []):
            return True
        # We forbid this because addPorts hardcodes this but
        # SetInputArrayToProcess is an exception for the InfoVis
        # package
        if (cls == vtk.vtkAlgorithm and
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
            if (isinstance(curr, str)):
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

file_name_pattern = re.compile('.*FileName$')
set_file_name_pattern = re.compile('Set.*FileName$')

def resolve_overloaded_name(name, ix, signatures):
    # VTK supports static overloading, VisTrails does not. The
    # solution is to check whether the current function has
    # overloads and change the names appropriately.
    if len(signatures) == 1:
        return name
    else:
        return name + '_' + str(ix+1)

type_map_dict = {'int': "basic:Integer",
                 'long': "basic:Integer",
                 'float': "basic:Float",
                 'char*': "basic:String",
                 'char *': "basic:String",
                 'string': "basic:String",
                 'char': "basic:String",
                 'const char*': "basic:String",
                 'const char *': "basic:String",
                 '[float': "basic:Float",
                 'float]': "basic:Float",
                 '[int': "basic:Integer",
                 'int]': "basic:Integer",
                 'bool': "basic:Boolean",
                 'unicode': 'basic:String'}

type_map_values = set(type_map_dict.itervalues())
# ["basic:Integer", "basic:Float", "basic:String", "basic:Boolean"]

def get_port_types(name):
    """ get_port_types(name: str) -> str
    Convert from C/C++ types into VisTrails port type

    """
    if isinstance(name, tuple) or isinstance(name, list):
        return [get_port_types(x) for x in name]
    if name in type_map_dict:
        return type_map_dict[name]
    else:
        if name is not None and name.strip():
            #if not name.startswith("vtk"):
            #    print "RETURNING RAW TYPE:", name
            return name
    return None

def is_type_allowed(t):
    if isinstance(t, list):
        return all(is_type_allowed(sub_t) for sub_t in t)
    if t is None:
        return False
    if t == "tuple" or t == "function":
        return False
    return t not in disallowed_classes

def get_algorithm_ports(cls):
    """ get_algorithm_ports(cls: class) -> None
    If module is a subclass of vtkAlgorithm, this function will add all
    SetInputConnection([id],[port]) and GetOutputPort([id]) as
    SetInputConnection{id}([port]) and GetOutputPort{id}.

    """
    input_ports = []
    output_ports = []

    if issubclass(cls, vtk.vtkAlgorithm):
        # We try to instantiate the class here to get the number of
        # ports and to avoid abstract classes
        try:
            instance = cls()
        except TypeError:
            pass
        else:
            for i in xrange(instance.GetNumberOfInputPorts()):
                port_name = "SetInputConnection%d" % i
                port_spec = InputPortSpec(name=port_name,
                                          method_name="SetInputConnection",
                                          port_type="vtkAlgorithmOutput",
                                          docstring=get_doc(cls,
                                                        "SetInputConnection"),
                                          show_port=True,
                                          prepend_params=[i])
                input_ports.append(port_spec)
            for i in xrange(instance.GetNumberOfOutputPorts()):
                port_name = "GetOutputPort%d" % i
                port_spec = OutputPortSpec(name=port_name,
                                           method_name="GetOutputPort",
                                           port_type="vtkAlgorithmOutput",
                                           docstring=get_doc(cls,
                                                             "GetOutputPort"),
                                           show_port=True)
                output_ports.append(port_spec)

    return input_ports, output_ports

disallowed_get_ports = set([
    'GetClassName',
    'GetErrorCode',
    'GetNumberOfInputPorts',
    'GetNumberOfOutputPorts',
    'GetOutputPortInformation',
    'GetTotalNumberOfInputConnections',
    ])

def get_get_ports(cls, get_list):
    output_ports = []
    for name in get_list:
        if name in disallowed_get_ports:
            continue
        method = getattr(cls, name)
        signatures = parser.get_method_signature(method)
        if len(signatures) > 1:
            prune_signatures(cls, name, signatures, output=True)
        for ix, getter in enumerate(signatures):
            if getter[1]:
                #print ("Can't handle getter %s (%s) of class %s: Needs input "
                #       "to get output" % (ix+1, name, cls.__name__))
                continue
            if len(getter[0]) != 1:
                #print ("Can't handle getter %s (%s) of class %s: More than a "
                #       "single output" % (ix+1, name, cls.__name__))
                continue
            port_type = get_port_types(getter[0][0])
            if is_type_allowed(port_type):
                n = resolve_overloaded_name(name[3:], ix, signatures)
                port_spec = OutputPortSpec(name=n,
                                           method_name=name,
                                           port_type=port_type,
                                           show_port=False,
                                           docstring=get_doc(cls, name))
                output_ports.append(port_spec)
    return [], output_ports

disallowed_get_set_ports = set(['ReferenceCount',
                                'InputConnection',
                                'OutputPort',
                                'Progress',
                                'ProgressText',
                                'InputArrayToProcess',
                                ])

color_ports = set(["DiffuseColor", "Color", "AmbientColor", "SpecularColor",
                   "EdgeColor", "Background", "Background2"])

to_vtk6_names = {'AddInput':  'AddInputData',
                 'SetInput':  'SetInputData',
                'AddSource': 'AddSourceData',
                'SetSource': 'SetSourceData'}
def get_vtk6_name(cls, name):
    # Return SetInputData for SetInput etc.
    if name == 'AddInput' and cls == vtk.vtkXYPlotActor:
        return 'AddDataSetInput'
    return to_vtk6_names.get(name, name)

# FIXME use defaults and ranges!
def get_get_set_ports(cls, get_set_dict):
    """get_get_set_ports(cls: class, get_set_dict: dict) -> None
    Convert all Setxxx methods of cls into input ports and all Getxxx
    methods of module into output ports

    Keyword arguments:
    cls          --- class
    get_set_dict --- the Set/Get method signatures returned by vtk_parser

    """

    input_ports = []
    output_ports = []
    for name in get_set_dict:
        if name in disallowed_get_set_ports:
            continue
        getter_name = 'Get%s' % name
        setter_name = 'Set%s' % name
        getter_method = getattr(cls, getter_name)
        setter_method = getattr(cls, setter_name)
        getter_sig = parser.get_method_signature(getter_method)
        setter_sig = parser.get_method_signature(setter_method)
        if len(getter_sig) > 1:
            prune_signatures(cls, getter_name, getter_sig, output=True)
        for order, getter in enumerate(getter_sig):
            if getter[1]:
                #print ("Can't handle getter %s (%s) of class %s: Needs input "
                #       "to get output" % (order+1, name, cls.__name__))
                continue
            if len(getter[0]) != 1:
                #print ("Can't handle getter %s (%s) of class %s: More than a "
                #       "single output" % (order+1, name, cls.__name__))
                continue
            port_type = get_port_types(getter[0][0])
            if is_type_allowed(port_type):
                if name in color_ports:
                    ps = OutputPortSpec(name=name,
                                        method_name=getter_name,
                                        port_type="basic:Color",
                                        show_port=False,
                                        docstring=get_doc(cls, getter_name))
                    input_ports.append(ps)
                else:
                    ps = OutputPortSpec(name=name,
                                        method_name=getter_name,
                                        port_type=port_type,
                                        show_port=False,
                                        docstring=get_doc(cls, getter_name))
                    output_ports.append(ps)

        if len(setter_sig) > 1:
            prune_signatures(cls, setter_name, setter_sig)
        docstring = get_doc(cls, setter_name)
        v = vtk.vtkVersion()
        version = [v.GetVTKMajorVersion(),
                   v.GetVTKMinorVersion(),
                   v.GetVTKBuildVersion()]
        if version < [6, 0, 0]:
            # Always use VTK6-style names for InputData-style types
            setter_name = get_vtk6_name(cls, setter_name)
            name = setter_name[3:]
        for ix, setter in enumerate(setter_sig):
            if setter[1] is None:
                continue

            # Wrap SetFileNames for VisTrails file access
            # FIXME add documentation
            if file_name_pattern.match(name):
                ps = InputPortSpec(name=name[:-4],
                                   method_name=setter_name,
                                   port_type="basic:File",
                                   show_port=True)
                input_ports.append(ps)
            # Wrap color methods for VisTrails GUI facilities
            # FIXME add documentation
            elif name in color_ports:
                ps = InputPortSpec(name=name,
                                   method_name=setter_name,
                                   port_type="basic:Color",
                                   show_port=False)
                input_ports.append(ps)
            # Wrap SetRenderWindow for exporters
            # FIXME Add documentation
            elif name == 'RenderWindow' and cls == vtk.vtkExporter:
                ps = InputPortSpec(name="vtkRenderer",
                                   port_type="vtkRenderer",
                                   show_port=True)
                input_ports.append(ps)
            else:
                n = resolve_overloaded_name(name, ix, setter_sig)
                port_types = get_port_types(setter[1])
                if is_type_allowed(port_types):
                    if len(setter[1]) == 1:
                        show_port = True
                        try:
                            show_port = port_types[0] not in type_map_values
                        except TypeError: # hash error
                            pass
                        port_types = port_types[0]
                    else:
                        show_port = False
                    ps = InputPortSpec(name=n,
                                       method_name=setter_name,
                                       port_type=port_types,
                                       show_port=show_port,
                                       docstring=docstring,
                                       depth=1)
                    input_ports.append(ps)

    return input_ports, output_ports

disallowed_toggle_ports = set(['GlobalWarningDisplay',
                               'Debug',
                               ])
def get_toggle_ports(cls, toggle_dict):
    """ get_toggle_ports(cls: class, toggle_dict: dict) -> None
    Convert all xxxOn/Off methods of module into boolean input ports

    Keyword arguments:
    module      --- Module
    toggle_dict --- the Toggle method signatures returned by vtk_parser

    """

    input_ports = []
    for name, default_val in toggle_dict.iteritems():
        if name in disallowed_toggle_ports:
            continue
        ps = InputPortSpec(name=name,
                           method_name=name, # With On/Off appended
                           method_type='OnOff',
                           port_type="basic:Boolean",
                           show_port=False,
                           defaults=[bool(default_val)],
                           docstring=get_doc(cls, name + "On"))
        input_ports.append(ps)
    return input_ports, []

disallowed_state_ports = set([('InputArray', 'Process')])
def get_state_ports(cls, state_dict):
    """ get_state_ports(cls: class, state_dict: dict) -> None
    Convert all SetxxxToyyy methods of module into input ports

    Keyword arguments:
    module     --- Module
    state_dict --- the State method signatures returned by vtk_parser

    """
    input_ports = []
    for name in state_dict:
        enum_values = []
        translations = {}
        method_name = "Set%sTo%s" % (name, state_dict[name][0][0])
        method_name_short = "Set%sTo" % name
        for mode in state_dict[name]:
            if (name, mode[0]) in disallowed_state_ports:
                continue
            if mode[0] in translations:
                if translations[mode[0]] != mode[1]:
                    raise Exception("Duplicate entry with different value")
                continue
            translations[mode[0]] = mode[1]
            enum_values.append(mode[0])

        ps = InputPortSpec(name=name,
                           method_name=method_name_short,
                           method_type='SetXToY',
                           port_type="basic:String",
                           entry_types=['enum'],
                           values=[enum_values],
                           show_port=False,
                           docstring=get_doc(cls, method_name))
        input_ports.append(ps)

    return input_ports, []


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
     # for VTK 6
     'SetMaterialProperties',
     ])


# FIXME deal with this in diff...
force_not_optional_port = set(
    ['ApplyViewTheme',
     ])

def get_other_ports(cls, other_list):
    """ addOtherPorts(cls: Module, other_list: list) -> None
    Convert all other ports such as Insert/Add.... into input/output

    Keyword arguments:
    cls        --- class
    other_dict --- any other method signatures that is not
                   Algorithm/SetGet/Toggle/State type

    """
    input_ports = []
    for name in other_list:
        # DAK: check for static methods as name.upper() == name
        if name in disallowed_other_ports or name.upper() == name:
            continue
        elif name=='CopyImportVoidPointer':
            # FIXME add documentation
            ps = InputPortSpec(name='CopyImportVoidString',
                               method_name='CopyImportVoidPointer',
                               port_type='basic:String',
                               show_port=True)

        # elif name[:3] in ['Add','Set'] or name[:6]=='Insert':
        else:
            method = getattr(cls, name)
            signatures = ""
            if not isinstance(method, int):
                signatures = parser.get_method_signature(method)
            if len(signatures) > 1:
                prune_signatures(cls, name, signatures)
            docstring = get_doc(cls, name)
            v = vtk.vtkVersion()
            version = [v.GetVTKMajorVersion(),
                       v.GetVTKMinorVersion(),
                       v.GetVTKBuildVersion()]
            if version < [6, 0, 0]:
                # Always use VTK6-style names for InputData-style types
                name = get_vtk6_name(cls, name)
            for (ix, sig) in enumerate(signatures):
                ([result], params) = sig
                port_types = get_port_types(params)
                if not (name[:3] in ['Add','Set'] or
                        name[:6]=='Insert' or
                        (port_types is not None and len(port_types) == 0) or
                        result is None):
                    continue
                if is_type_allowed(port_types):
                    n = resolve_overloaded_name(name, ix, signatures)
                    if n.startswith('Set'):
                        n = n[3:]
                    show_port = False
                    if len(port_types) < 1:
                        raise Exception("Shouldn't have empty input")
                    elif len(port_types) == 1:
                        if name[:3] in ['Add','Set'] or name[:6]=='Insert':
                            try:
                                show_port = port_types[0] not in type_map_values
                            except TypeError:
                                pass
                        port_types = port_types[0]
                    ps = InputPortSpec(name=n,
                                       method_name=name,
                                       port_type=port_types,
                                       show_port=show_port,
                                       docstring=docstring,
                                       depth=1)
                    input_ports.append(ps)
                elif result == None or port_types == []:
                    n = resolve_overloaded_name(name, ix, signatures)
                    ps = InputPortSpec(name=n,
                                       method_name=name,
                                       port_type='basic:Boolean',
                                       method_type='nullary',
                                       docstring=get_doc(cls, name),
                                       depth=1)
                    input_ports.append(ps)
    return input_ports, []

def get_custom_ports(cls):
    """ get_custom_ports(cls: Module) -> None
    Patch other ports needed to get a good wrapping

    Keyword arguments:
    cls        --- class

    """
    input_ports = []
    output_ports = []

    if cls == vtk.vtkAlgorithm:
        ps = InputPortSpec(name='AddInputConnection',
                           port_type='vtkAlgorithmOutput',
                           show_port=True,
                           docstring='Adds an input connection',
                           depth=1)
        input_ports.append(ps)
    # vtkWriters have a custom File port
    if cls in [vtk.vtkWriter, vtk.vtkImageWriter]:
        ps = OutputPortSpec(name='file',
                            port_type='basic:File',
                            show_port=True,
                            docstring='The written file')
        output_ports.append(ps)
    elif cls == vtk.vtkVolumeProperty:
        ps = InputPortSpec(name='TransferFunction',
                           method_name='SetTransferFunction',
                           port_type='TransferFunction',
                           docstring='Sets the transfer function to use')
        input_ports.append(ps)
    elif cls == vtk.vtkDataSet:
        ps = InputPortSpec(name='SetPointData',
                           method_name='PointData',
                           port_type='vtkPointData',
                           show_port=True,
                           docstring='Sets the point data')
        input_ports.append(ps)
        ps = InputPortSpec(name='SetCellData',
                           method_name='CellData',
                           port_type='vtkCellData',
                           show_port=True,
                           docstring='Sets the cell data')
        input_ports.append(ps)
    elif cls==vtk.vtkCell:
        ps = InputPortSpec(name='SetPointIds',
                           method_name='PointIds',
                           port_type='vtkIdList',
                           show_port=True,
                           docstring='Sets the point id list')
        input_ports.append(ps)
    elif cls==vtk.vtkMultiBlockPLOT3DReader:
        ps = OutputPortSpec(name='StructuredGrid',
                            method_name='FirstBlock',
                            port_type='vtkStructuredGrid',
                            show_port=True,
                            docstring='Returns .GetOutput().GetBlock(0)')
        output_ports.append(ps)

    return input_ports, output_ports


def get_ports(cls):
    """get_ports(cls: vtk class) -> None

    Search all metamethods of module and add appropriate ports

    """

    parser.parse(cls)
    ports_tuples = []
    ports_tuples.append(get_algorithm_ports(cls))
    ports_tuples.append(get_get_ports(cls, parser.get_get_methods()))
    ports_tuples.append(get_get_set_ports(cls, parser.get_get_set_methods()))
    ports_tuples.append(get_toggle_ports(cls, parser.get_toggle_methods()))
    ports_tuples.append(get_state_ports(cls, parser.get_state_methods()))
    ports_tuples.append(get_other_ports(cls, parser.get_other_methods()))
    ports_tuples.append(get_custom_ports(cls))

    zipped_ports = izip(*ports_tuples)
    input_ports = chain(*zipped_ports.next())
    output_ports = chain(*zipped_ports.next())
    return input_ports, output_ports

def parse(filename="vtk_raw.xml"):
    inheritance_graph = ClassTree(vtk)
    inheritance_graph.create()

    v = vtk.vtkVersion()
    version = [v.GetVTKMajorVersion(),
               v.GetVTKMinorVersion(),
               v.GetVTKBuildVersion()]
    if version < [5, 7, 0]:
        assert len(inheritance_graph.tree[0]) == 1
        base = inheritance_graph.tree[0][0]
        assert base.name == 'vtkObjectBase'

    specs_list = []
    if version < [5, 7, 0]:
        for child in base.children:
            if child.name in disallowed_classes:
                continue
            specs_list.extend(create_module("vtkObjectBase", child))
    else:
        for base in inheritance_graph.tree[0]:
            for child in base.children:
                if child.name in disallowed_classes:
                    continue
                specs_list.extend(create_module("vtkObjectBase", child))

    specs = SpecList(specs_list)
    specs.write_to_xml(filename)


if __name__ == '__main__':
    parse()

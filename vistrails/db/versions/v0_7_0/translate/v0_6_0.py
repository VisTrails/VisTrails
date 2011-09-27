###############################################################################
##
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

import copy
from db.versions.v0_7_0.domain import DBVistrail, DBAction, DBTag, DBModule, \
    DBConnection, DBPortSpec, DBFunction, DBParameter, DBLocation, DBAdd, \
    DBChange, DBDelete, DBAnnotation, DBPort

def translateVistrail(_vistrail):
    vistrail = DBVistrail()

    for _action in _vistrail.db_actions.itervalues():
        ops = []
        for op in _action.db_operations:
            if op.vtType == 'add':
                data = convert_data(op.db_data, op.db_parentObjType,
                                    op.db_parentObjId)
                ops.append(DBAdd(id=op.db_id,
                                 what=op.db_what, 
                                 objectId=op.db_objectId, 
                                 parentObjId=op.db_parentObjId, 
                                 parentObjType=op.db_parentObjType, 
                                 data=data))
            elif op.vtType == 'change':
                data = convert_data(op.db_data, op.db_parentObjType,
                                    op.db_parentObjId)
                ops.append(DBChange(id=op.db_id,
                                    what=op.db_what, 
                                    oldObjId=op.db_oldObjId, 
                                    newObjId=op.db_newObjId,
                                    parentObjId=op.db_parentObjId, 
                                    parentObjType=op.db_parentObjType, 
                                    data=data))
            elif op.vtType == 'delete':
                ops.append(DBDelete(id=op.db_id,
                                    what=op.db_what, 
                                    objectId=op.db_objectId, 
                                    parentObjId=op.db_parentObjId, 
                                    parentObjType=op.db_parentObjType))
        action = DBAction(id=_action.db_id,
                          prevId=_action.db_prevId, 
                          date=_action.db_date, 
                          user=_action.db_user, 
                          operations=ops,
                          annotations=_action.db_annotations.values())
        vistrail.db_add_action(action)

    for _tag in _vistrail.db_tags.itervalues():
        tag = DBTag(id=_tag.db_id,
                    name=_tag.db_name)
        vistrail.db_add_tag(tag)

    vistrail.db_version = '0.7.0'
    return vistrail

module_map = {}
translate_ports = {'SetInputConnection': {None: 'SetInputConnection0'},
                   'GetOutputPort': {None: 'GetOutputPort0'},
                   'SetRenderWindow': {None: 'SetVTKCell'},
                   'SetInteractorStyle': {None: 'InteractorStyle'},
                   'ResetCamera': {None: 'ResetCamera'},
                   'AddPoint': {None: 'AddPoint_1'},
                   'AddRGBPoint': {None: 'AddRGBPoint_1'},
                   'AddHSVPoint': {None: 'AddHSVPoint_1'},
                   'AddInput': {None: 'AddInput',
                                'vtkXYPlotActor': 'AddInput_2'},
                   'SetInput': {None: 'SetInput',
                                'vtkPolyDataNormals': 'SetInput_1',
                                'vtkGlyph3D': 'SetInput_1',
                                'vtkDelaunay2D': 'SetInput_1',
                                'vtkDelaunay3D': 'SetInput_1',
                                'vtkWarpVector': 'SetInput_1',
                                'vtkContourFilter': 'SetInput_1',
                                'vtkTubeFilter': 'SetInput_1',
                                'vtkThresholdPoints': 'SetInput_1',
                                'vtkProbeFilter': 'SetInput_1',
                                'vtkTriangleFilter': 'SetInput_1',
                                'vtkBandedPolyDataContourFilter': \
                                    'SetInput_1',
                                'vtkWarpScalar': 'SetInput_1'},
                   'SetSourceConnection': {None: 'SetSourceConnection',
                                           'vtkGlyph3D': \
                                               'SetSourceConnection_2'},
                   'AddFunction': {None: 'AddFunction',
                                   ('vtkImplicitSum', 'vtkPlane'): \
                                       'AddFunction_2',
                                   ('vtkImplicitSum', 'Tuple'): \
                                       'AddFunction_1'},
                   'SetColor': {None: 'SetColor',
                                ('vtkVolumeProperty', 
                                 'vtkColorTransferFunction'): \
                                    'SetColor_4',
                                ('vtkVolumeProperty', 
                                 'vtkPiecewiseFunction'): \
                                    'SetColor_2'},
                   'SetScalarOpacity': {None: 'SetScalarOpacity',
                                        'vtkVolumeProperty': \
                                            'SetScalarOpacity_2'},
                   'SetGradientOpacity': {None: 'SetGradientOpacity',
                                          'vtkVolumeProperty':
                                              'SetGradientOpacity_2'},
                   'SetSource': {None: 'SetSource',
                                 'vtkGlyph3D': 'SetSource_1'},
                   }

def translate_vtk(module_id, port_name, specs=None):
    global module_map
    if port_name in translate_ports:
        if module_id in module_map:
            (module_name, module_pkg) = module_map[module_id]
            if module_pkg != 'edu.utah.sci.vistrails.vtk':
                return port_name
        if module_name in translate_ports[port_name]:
            port_name = translate_ports[port_name][module_name]
        elif (module_name, specs) in translate_ports[port_name]:
            port_name = translate_ports[port_name][(module_name, specs)]
        else:
            port_name = translate_ports[port_name][None]  
    return port_name

def convert_data(child, parent_type, parent_id):
    from core.vistrail.port_spec import PortSpec
    from core.modules.module_registry import get_module_registry
    global module_map, translate_ports

    registry = get_module_registry()
    if child.vtType == 'module':
        descriptor = registry.get_descriptor_from_name_only(child.db_name)
        package = descriptor.identifier
        module_map[child.db_id] = (child.db_name, package)
        return DBModule(id=child.db_id,
                        cache=child.db_cache, 
                        abstraction=0, 
                        name=child.db_name,
                        package=package)
    elif child.vtType == 'connection':
        return DBConnection(id=child.db_id)
    elif child.vtType == 'portSpec':
        return DBPortSpec(id=child.db_id,
                          name=child.db_name, 
                          type=child.db_type, 
                          spec=child.db_spec)
    elif child.vtType == 'function':
        if parent_type == 'module':
            name = translate_vtk(parent_id, child.db_name)
        else:
            name = child.db_name
        return DBFunction(id=child.db_id,
                          pos=child.db_pos, 
                          name=name)
    elif child.vtType == 'parameter':
        return DBParameter(id=child.db_id,
                           pos=child.db_pos,
                           name=child.db_name, 
                           type=child.db_type, 
                           val=child.db_val, 
                           alias=child.db_alias)
    elif child.vtType == 'location':
        return DBLocation(id=child.db_id,
                          x=child.db_x,
                          y=child.db_y)
    elif child.vtType == 'annotation':
        return DBAnnotation(id=child.db_id,
                            key=child.db_key,
                            value=child.db_value)
    elif child.vtType == 'port':
        sig = child.db_sig
        if '(' in sig and ')' in sig:
            name = sig[:sig.find('(')]
            specs = sig[sig.find('(')+1:sig.find(')')]
            name = translate_vtk(child.db_moduleId, name, specs)

            new_specs = []
            for spec_name in specs.split(','):
                descriptor = registry.get_descriptor_from_name_only(spec_name)
                spec_str = descriptor.identifier + ':' + spec_name
                new_specs.append(spec_str)
            spec = '(' + ','.join(new_specs) + ')'
        else:
            name = sig
            spec = ''
        return DBPort(id=child.db_id,
                      type=child.db_type, 
                      moduleId=child.db_moduleId, 
                      moduleName=child.db_moduleName, 
                      name=name,
                      spec=spec)

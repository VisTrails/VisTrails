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

import sys
sys.path.append('/vistrails/src/trunk/vistrails')
import os
os.environ['EXECUTABLEPATH'] = ""
import copy
import datetime
import re
import urllib

from db.domain import DBModule, DBConnection, DBPort, DBFunction, \
    DBParameter, DBLocation, DBPortSpec, DBTag, DBAnnotation, DBVistrail, \
    DBRegistry
import db.services.io
from db.services.io import SaveBundle
from vtk_imposter import vtk_module, vtk_function

class VTK2VT(object):
    vtk_data_url = 'http://www.vtk.org/files/release/5.0/vtkdata-5.0.4.zip'
    package_name = 'edu.utah.sci.vistrails.vtk'
    basic_name = 'edu.utah.sci.vistrails.basic'
    pythoncalc_name = 'edu.utah.sci.vistrails.pythoncalc'
    http_name = 'edu.utah.sci.vistrails.http'
    variant_sigstring ='(edu.utah.sci.vistrails.basic:Tuple)'
    unused_functions = set(['Update', 
                            'Read', 
                            'Write', 
                            'Start', 
                            'Initialize',
                            'Render', 
                            'PlaceWidget', 
                            'AddObserver',
                            'SetSize',
                            ])
    translate_ports = {'SetInputConnection': {None: 'SetInputConnection0'},
                       'GetOutputPort': {None: 'GetOutputPort0'},
                       'SetRenderWindow': {None: 'SetVTKCell'},
                       'SetInteractorStyle': {None: 'InteractorStyle'},
                       'ResetCamera': {None: 'ResetCamera'},
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
                       'SetSource': {None: 'SetSource',
                                     'vtkGlyph3D': 'SetSource_1'},
                       }

    inspector_functions = {'GetScalarRange': 'vtkDataSetInspector',
                           'GetCenter': 'vtkDataSetInspector',
                           'GetNumberOfCells': 'vtkDataSetInspector',
                           'GetNumberOfPoints': 'vtkDataSetInspector',
                           'GetLength': 'vtkDataSetInspector',
                           'GetBounds': 'vtkDataSetInspector',
                           'GetPointData': 'vtkDataSetInspector',
                           'GetCellData': 'vtkDataSetInspector',
                           'GetVerts': 'vtkPolyDataInspector',
                           'GetPoints': 'vtkPolyDataInspector',
                           'GetLines': 'vtkPolyDataInspector',
                           'GetStrips': 'vtkPolyDataInspector',
                           'GetPoints': 'vtkPolyDataInspector',
                           'GetNumberOfVerts': 'vtkPolyDataInspector',
                           'GetNumberOfPoints': 'vtkPolyDataInspector',
                           'GetNumberOfPolys': 'vtkPolyDataInspector',
                           'GetNumberOfStrips': 'vtkPolyDataInspector',
                           'GetScalars': 'vtkDataSetAttributesInspector',
                           'GetVectors': 'vtkDataSetAttributesInspector',
                           'GetNormals': 'vtkDataSetAttributesInspector',
                           'GetTCoords': 'vtkDataSetAttributesInspector',
                           'GetTensors': 'vtkDataSetAttributesInspector',
                           'GetGlobalIds': 'vtkDataSetAttributesInspector',
                           'GetPedigreeIds': 'vtkDataSetAttributesInspector',
                           'GetMaxNorm': 'vtkDataArrayInspector',
                           'GetRange': 'vtkDataArrayInspector',
                           }
                           
    getters = {'GetProperty': {None: ('SetProperty', 'vtkProperty', None),
                               'vtkXYPlotActor': ('SetProperty',
                                                  'vtkProperty2D', None)}, 
               'GetActiveCamera': {None: ('SetActiveCamera', 
                                          'vtkCamera', None)},
               'GetTitleTextProperty':{None: ('SetTitleTextProperty', 
                                              'vtkTextProperty',
                                              [('BoldOn',),
                                               ('ItalicOn',),
                                               ('ShadowOn',),
                                               ('SetFontFamilyToArial',)])},
               'GetTextProperty': {None: ('SetTextProperty', 
                                          'vtkTextProperty', None)},
               'GetPointData': {None: ('SetPointData', 'vtkPointData', None)},
               'GetCellData': {None: ('SetCellData', 'vtkCellData', None)},
               'GetPointIds': {None: ('SetPointIds', 'vtkIdList', None),
                               'vtkVoxel': ('SetPointIds', 'vtkIdList',
                                            [('SetNumberOfIds', 8)]),
                               'vtkHexahedron': ('SetPointIds', 'vtkIdList',
                                                 [('SetNumberOfIds', 8)]),
                               'vtkTetra': ('SetPointIds', 'vtkIdList',
                                            [('SetNumberOfIds', 4)]),
                               'vtkWedge': ('SetPointIds', 'vtkIdList',
                                            [('SetNumberOfIds', 6)]),
                               'vtkPyramid': ('SetPointIds', 'vtkIdList',
                                              [('SetNumberOfIds', 5)]),
                               'vtkPixel': ('SetPointIds', 'vtkIdList',
                                            [('SetNumberOfIds', 4)]), 
                               'vtkQuad': ('SetPointIds', 'vtkIdList',
                                           [('SetNumberOfIds', 4)]), 
                               'vtkTriangle': ('SetPointIds', 'vtkIdList',
                                               [('SetNumberOfIds', 3)]), 
                               'vtkLine': ('SetPointIds', 'vtkIdList',
                                           [('SetNumberOfIds', 2)]), 
                               'vtkVertex': ('SetPointIds', 'vtkIdList',
                                             [('SetNumberOfIds', 1)]), 
                               },
               'GetRenderWindow': {None: ('SetVTKCell', 'VTKCell', None)},
               }

    set_file_name_pattern = re.compile('Set.*FileName$')

    def __init__(self):
        self.created_modules = {}
        self.modules = {}
        self.vt_modules = {}
        self.vtk_modules = {}
        self.connections = {}
        self.vt_f_connections = {}
        self.vt_b_connections = {}
        self.max_module_id = 0
        self.max_location_id = 0
        self.max_function_id = 0
        self.max_parameter_id = 0
        self.max_connection_id = 0
        self.max_port_id = 0
        self.max_port_spec_id = 0
        self.http_module = None

        r_file = '/vistrails/registry.xml'
        self.registry = db.services.io.open_registry_from_xml(r_file)
        self.registry_desc_idx = {}
        for package in self.registry.db_packages:
            for desc in package.db_module_descriptors:
                self.registry_desc_idx[desc.db_id] = desc

    def create_module(self, module):
        # print 'creating module', module._name, id(module)
        module_name = module._name
        package_name = self.package_name
        if module_name == 'vtkRenderWindow':
            module_name = 'VTKCell'
        elif module_name == 'vtkRenderWindowInteractor':
            return
        elif module_name == 'Tuple' or module_name == 'Unzip':
            package_name = self.basic_name
        elif module_name == 'PythonCalc':
            package_name = self.pythoncalc_name
        elif module_name == 'HTTPFile':
            package_name = self.http_name
        db_module = DBModule(id=self.max_module_id,
                             name=module_name,
                             package=package_name,
                             location=DBLocation(id=self.max_location_id, 
                                                 x=0.0, y=0.0),
                             )
        self.max_module_id += 1
        self.max_location_id += 1
        self.modules[id(module)] = db_module
        self.vt_modules[db_module.db_id] = db_module
        self.vtk_modules[id(module)] = module
        # self.vt_f_connections[db_module.db_id] = []
        # self.vt_b_connections[db_module.db_id] = []

    def save_modules(self):
        self.saved_functions = {}
        for k, module in self.vtk_modules.iteritems():
            self.saved_functions[k] = module.functions
            module.functions = []
            
    def restore_modules(self):
        for k, module in self.vtk_modules.iteritems():
            module.functions = self.saved_functions[k]
    
    def do_layout(self):
        queue = []
        # sinks = []
        vt_b_connections = self.vt_f_connections
        vt_f_connections = self.vt_b_connections
        b_connections = copy.deepcopy(vt_b_connections)
        f_connections = copy.deepcopy(vt_f_connections)
        for m_id, module in self.vt_modules.iteritems():
            if m_id not in b_connections:
                queue.append((module, 0))
            # if module.db_id not in f_connections:
            #     sinks.append([set([module])])

        # print >>sys.stderr, 'queue:', queue
        # topological sort
        t_sort = []
        for module, level in queue:
            t_sort.append((module, level))
            if module.db_id in f_connections:
                for (next_id, _) in f_connections[module.db_id]:
                    next_module = self.vt_modules[next_id]
                    if next_module.db_id in b_connections:
                        if len(b_connections[next_module.db_id]) == 0:
                            continue
                        remaining_list = b_connections[next_module.db_id][:]
                        for t in remaining_list:
                            if t[0] == module.db_id:
                                b_connections[next_module.db_id].remove(t)
                        if len(b_connections[next_module.db_id]) == 0:
                            queue.append((next_module, level+1))
        
        # print >>sys.stderr, [(m.db_name, ell) for (m, ell) in t_sort]
        levels = {}
        module_levels = {}
        for (m, ell) in t_sort:
            if ell not in levels:
                levels[ell] = []
            levels[ell].append(m)
            module_levels[m.db_id] = ell

        for level, m_list in sorted(levels.iteritems()):
            for i, m in enumerate(m_list):
                if i >= len(m_list) - 1:
                    continue

                m_next = m_list[i+1]
                m_idxs = []
                m_next_idxs = []
                if m.db_id not in vt_b_connections:
                    continue
                if m_next.db_id not in vt_b_connections:
                    continue
                for (n_id, _) in vt_b_connections[m.db_id]:
                    n = self.vt_modules[n_id]
                    n_idx = levels[module_levels[n_id]].index(n)
                    m_idxs.append(n_idx)
                for (n_id, _) in vt_b_connections[m_next.db_id]:
                    n = self.vt_modules[n_id]
                    n_idx = levels[module_levels[n_id]].index(n)
                    m_next_idxs.append(n_idx)
                num_overlaps_f = 0
                num_overlaps_b = 0
                for m_idx in m_idxs:
                    for m_next_idx in m_next_idxs:
                        if m_idx == m_next_idx:
                            continue
                        elif m_idx < m_next_idx:
                            num_overlaps_b += 1
                        else:
                            num_overlaps_f += 1
                if num_overlaps_f > num_overlaps_b:
                    # swap
                    swap = m_list[i]
                    m_list[i] = m_list[i+1]
                    m_list[i+1] = swap
                                
        dx = 250.0
        dy = 100.0
        current_y = 0.0
        for level, m_list in levels.iteritems():
            current_x = - (len(m_list) * dx) / 2.0
            for m in m_list:
                m.db_location.db_x = current_x
                m.db_location.db_y = current_y
                current_x += dx
            current_y += dy
                   
    def get_vtk_cell(self, interactor):
        found_vtk_cell = False
        if interactor._name == 'vtkRenderWindowInteractor':
            found_vtk_cell = False
            for function in interactor.functions:
                if function._name == 'SetRenderWindow' and \
                        len(function._args) == 1 and \
                        type(function._args[0]) == vtk_module:
                    # use VTKCell to translate calls
                    function_list = interactor.functions
                    module = function._args[0]
                    found_vtk_cell = True
                    break
        if found_vtk_cell:
            return (module, function_list)
        else:
            print >>sys.stderr, "ERROR: cannot find VTKCell for Interactor"
        return (None, None)
    
    def create_functions(self, module, function_list=None, f_pos=0):
        # print >>sys.stderr, 'creating functions:', module._name
#         import traceback
#         traceback.print_stack(file=sys.stderr)
        if module._name == 'vtkRenderWindowInteractor':
            (module, new_function_list) = self.get_vtk_cell(module)
            if not module:
                # punt on it in this case
                return
            else:
                function_list = []
                for function in new_function_list[:]:
                    if type(function.parent) == vtk_module:
                        function.parent = module
                    if function._name != 'SetRenderWindow':
                        function_list.append(function)
        if function_list is None:
            function_list = module.functions
        for function in function_list:
            # print >>sys.stderr, '  creating:', function._name
            db_function = self.create_function(function, f_pos)
            if db_function:
                self.modules[id(module)].db_add_function(db_function)
                f_pos += 1
        return f_pos

    def find_or_create_module(self, function, allow_sub=True):
#         print >>sys.stderr, 'find_or_create:', function._name, \
#             function.parent._name, id(function)
        parent_name = function.parent._name

#                    'GetPositionCoordinate': {None: ('SetPosition',
#                                                     'vtkCoordinate')},
#                    'GetPosition2Coordinate': {None: ('SetPosition2',
#                                                      'vtkCoordinate')}
#                    }
        
        # if we have a getter, than check this stuff
        if function._name.startswith('Get') and len(function._args) == 0 and \
                len(function.sub_functions) == 1 and \
                function.sub_functions[0]._name in self.inspector_functions:
            # print >>sys.stderr, ">> found inspector function"
            # print >>sys.stderr, "  ", function._name, function.parent._name
            inspector_name = \
                self.inspector_functions[function.sub_functions[0]._name]
            key = (id(function.parent), function._name)
            # print >>sys.stderr, '  ', key

            out_function = function.sub_functions[0]
            if key in self.created_modules:
                inspector_module = self.created_modules[key]
            else:
                inspector_module = vtk_module(inspector_name)
                self.create_module(inspector_module)
                self.created_modules[key] = inspector_module

                # need to attach first piece of call to inspector input
                in_function = vtk_function('SetInput')
                in_function.parent = inspector_module
                function.sub_functions = []
                in_function._args = [function]
                inspector_module.functions.append(in_function)
                self.create_functions(inspector_module, [in_function])
            # need to attach rest to inspector output
            found = False
            out_function.parent = inspector_module
            for old_function in inspector_module.functions:
                if old_function._name == out_function._name and \
                        (len(old_function.sub_functions) == 0 or
                         len(out_function.sub_functions) == 0 or
                         old_function.sub_functions[0]._name == \
                             old_function.sub_functions[0]._name):
                    found = True
                    break
            if not found:
                inspector_module.functions.append(out_function)
                self.create_functions(inspector_module, [out_function])
            return (inspector_module, True)
        elif function._name in self.getters and \
                (function._name not in self.inspector_functions or
                 self.inspector_functions[function._name] != \
                     function.parent._name):
#             and len(function.sub_functions) == 1 \
#                 and function.sub_functions[0]._name not in \
#                 self.inspector_functions:
            # print >>sys.stderr, '>>', function._name, 'found in getters'
            if not allow_sub:
                print >>sys.stderr, "ERROR: sub function has getter"
            key = (id(function.parent), function._name)
            if key in self.created_modules:
                p_module = self.created_modules[key]
#                 print >>sys.stderr, "found in created_modules:", \
#                     p_module._name
                return (p_module, False)
            if parent_name in self.getters[function._name]:
                (setter, module_name, function_list) = \
                    self.getters[function._name][parent_name]
            else:
                (setter, module_name, function_list) = \
                    self.getters[function._name][None]
#             print >>sys.stderr, 'self.getters:', self.getters[function._name]
            found_setter = False
            for p_function in function.parent.functions:
                if p_function._name == setter:
                    found_setter = True
                    for arg in p_function._args:
                        if type(arg) == vtk_module:
                            p_module = arg
                        else:
                            if arg == function:
                                found_setter = False
                            else:
                                p_module = arg.parent
                    if found_setter and type(p_module) != vtk_module:
                        print >>sys.stderr, "ERROR: type of p_module incorrect"
                        found_setter = False
                    if found_setter:
                        # print >>sys.stderr, "found", module_name, p_module._name
                        self.create_functions(p_module, function.sub_functions)
                        return (p_module, False)
            if not found_setter:
                # print >>sys.stderr, "doing create for", module_name
                p_module = \
                    self.create_module_for_get(function, setter, module_name,
                                               function_list)
                # print >>sys.stderr, id(p_module)
            return (p_module, False)
        return (None, False)

    def create_module_for_get(self, function, setter, module_name, 
                              function_list=None):
        # create new vtkProperty module
        # add connection to parent module on SetProperty call
        # for sub_function in function.sub_functions:
            # add each sub_function to the vtkProperty module
        src_module = None
        # if len(function.sub_functions) > 0:

        db_module = DBModule(id=self.max_module_id,
                     name=module_name,
                     package=self.package_name,
                     location=DBLocation(id=self.max_location_id, 
                                         x=0.0, y=0.0),
                     )
        self.max_module_id += 1
        self.max_location_id += 1
        src_module = vtk_module(module_name)                
        self.modules[id(src_module)] = db_module
        self.vt_modules[db_module.db_id] = db_module
        self.vtk_modules[id(src_module)] = src_module
        if function_list:
            src_functions = []
            for f in function_list:
                # doesn't work for functions with args yet
                src_function = vtk_function(f[0])
                if len(f) > 1:
                    src_function._args = list(f[1:])
                src_function.parent = src_module
                src_functions.append(src_function)
                # print >>sys.stderr, '**', src_function._name
            # src_module.functions = src_functions
            self.create_functions(src_module, src_functions)
            # print >>sys.stderr, "** done with create"

        # self.vt_f_connections[db_module.db_id] = []
        # self.vt_b_connections[db_module.db_id] = []
        self.created_modules[(id(function.parent), function._name)] = \
            src_module
        dst_function = vtk_function(setter)
        dst_function.parent = function.parent
        self.create_connection(src_module, dst_function)

        return src_module

    def create_tuple(self, function):
        tuple_module = vtk_module('Tuple')
        tuple_module.blah()
        self.create_module(tuple_module)
        db_tuple_module = self.modules[id(tuple_module)]
        tuple_f_pos = 0
        final_sigs = []
        for i, arg in enumerate(function._args):
            port_spec = DBPortSpec(id=self.max_port_spec_id,
                                   name='arg' + str(i),
                                   type='input',
                                   sigstring=self.variant_sigstring)
            db_tuple_module.db_add_portSpec(port_spec)
            self.max_port_spec_id += 1
            if type(arg) == vtk_module or \
                    type(arg) == vtk_function:
                # connection
                tuple_function = vtk_function('arg' + str(i))
                tuple_function.parent = tuple_module
                conn = self.create_connection(arg, tuple_function)
                port_spec.db_sigstring = \
                    conn.db_ports_type_index['source'].db_signature
                conn.db_ports_type_index['destination'].db_signature = \
                    port_spec.db_sigstring
                final_sigs.append(port_spec.db_sigstring[1:-1])
            else:
                db_parameters = self.get_parameters([arg])
                db_function = DBFunction(id=self.max_function_id,
                                         name='arg' + str(i),
                                         pos=tuple_f_pos,
                                         parameters=db_parameters,
                                         )
                self.max_function_id += 1
                tuple_f_pos += 1
                db_tuple_module.db_add_function(db_function)
                port_spec.db_sigstring = \
                    "(" + ','.join(p.db_type for p in db_parameters) + ")"
                final_sigs.extend(p.db_type for p in db_parameters)
        final_sigstring = "(" + ",".join(final_sigs) + ")"
        port_spec = DBPortSpec(id=self.max_port_spec_id,
                               name='value',
                               type='output',
                               sigstring=final_sigstring)
        db_tuple_module.db_add_portSpec(port_spec)
        self.max_port_spec_id += 1
        tuple_output = vtk_function('value')
        tuple_output.parent = tuple_module
        self.create_connection(tuple_output, function)
        return tuple_module

    def get_parameters(self, params):
        def get_type(arg):
            python_types = {int: 'edu.utah.sci.vistrails.basic:Integer', 
                            str: 'edu.utah.sci.vistrails.basic:String', 
                            float: 'edu.utah.sci.vistrails.basic:Float',
                            bool: 'edu.utah.sci.vistrails.basic:Boolean'}
            if type(arg) not in python_types:
                return None
            return python_types[type(arg)]
        # end get_type

        def create_param(arg, position):
            p_type = get_type(arg)
            if p_type:
                p = DBParameter(id=self.max_parameter_id,
                            type=p_type,
                            val=arg,
                            pos=position,
                            )
                db_parameters.append(p)
                self.max_parameter_id += 1
                position += 1
            return position
        # end create_param

        db_parameters = []
        pos = 0
        for arg in params:
            if type(arg) == tuple:
                for tuple_arg in arg:
                    pos = create_param(tuple_arg, pos)
            else:
                pos = create_param(arg, pos)
        return db_parameters
    # end get_parameters
        

    def create_function(self, function, f_pos, allow_sub=True):

        # print >>sys.stderr, 'type(function.parent):', type(function.parent)
        db_function = None
        (p_module, _) = self.find_or_create_module(function, allow_sub)
        if p_module:
            # print >>sys.stderr, 'found p_module', p_module._name, 'for', function._name
            add_functions = []
            for sub_function in function.sub_functions:
                if not sub_function._name.startswith('Get'):
                    # print >>sys.stderr, 'adding function:', sub_function._name
                    add_functions.append(sub_function)
            self.create_functions(p_module, add_functions, 
                                  len(self.modules[id(p_module)].db_functions))
#             self.create_functions(p_module, function.sub_functions,
#                                   len(self.modules[id(p_module)].db_functions))
            db_function = None
        else:
            if function._name in self.unused_functions:
                return None
            parameters = []
            connections = []
            for arg in function._args:
                if type(arg) == vtk_module or \
                        type(arg) == vtk_function:                    
                    connections.append(arg)
                else:
                    parameters.append(arg)

            if len(function._args) == 0 and \
                    len(function.sub_functions) == 0 and \
                    not function._name.startswith('Get'):
                parameters.append(None)
            elif function._name.startswith('Get'):
                parameters = []
                connections = []
#             if function._name == 'SetScalarRange' and \
#                     len(function._args) == 1:
#                 # use a vtkDataSetInspector to get scalar range
#                 arg = function._args[0]
#                 if type(arg) == vtk_function and \
#                         type(arg.parent) == vtk_function and \
#                         arg._name == 'GetScalarRange' and \
#                         arg.parent._name == 'GetOutput':
#                     inspector_module = vtk_module('vtkDataSetInspector')
#                     inspector_module.SetInputConnection(
#                         arg.parent.parent.GetOutputPort())
#                     self.create_module(inspector_module)
#                     self.create_functions(inspector_module)

#                     function._args = (inspector_module.GetScalarRange(),)
#                     connections = [function._args[0]]
#             elif function._name == 'GenerateValues' and \
#                     len(function._args) == 2:
#                 # use a vtkDataSetInspector to get scalar range
#                 arg = function._args[0]
#                 if type(arg) != int:
#                     print >>sys.stderr, \
#                         "ERROR: GenerateValues first arg type is incorrect"
#                     return None
#                 arg = function._args[1]
#                 if type(arg) == vtk_function and \
#                         type(arg.parent) == vtk_function and \
#                         arg._name == 'GetScalarRange' and \
#                         arg.parent._name == 'GetOutput':
#                     inspector_module = vtk_module('vtkDataSetInspector')
#                     inspector_module.SetInputConnection(
#                         arg.parent.parent.GetOutputPort())
#                     self.create_module(inspector_module)
#                     self.create_functions(inspector_module)

#                     function._args = (function._args[0], 
#                                       inspector_module.GetScalarRange())
#                     connections = [function._args[1]]
#                     parameters = [function._args[0]]   
            if self.set_file_name_pattern.match(function._name) and \
                    type(function.parent) == vtk_module and \
                    len(function._args) == 1 and \
                    type(function._args[0]) == str:
                # replace SetFileName with a HTTPFile -> Unzip -> SetFile
                if not self.http_module:
                    self.http_module = vtk_module('HTTPFile')
                    self.http_module.url(self.vtk_data_url)
                    self.create_module(self.http_module)
                    self.create_functions(self.http_module)
                unzip_module = vtk_module('Unzip')
                self.create_module(unzip_module)
                unzip_module.filename_in_archive(function._args[0][1:])
                unzip_module.archive_file(self.http_module.file())
                self.create_functions(unzip_module)
                set_file_function = vtk_function(function._name[:-4])
                set_file_function.parent = function.parent
                set_file_function._args = [unzip_module.file()]
                self.create_functions(function.parent, [set_file_function])
                return None
            if function._name == 'SetInteractor' and \
                    len(function._args) == 1 and \
                    type(function._args[0]) == vtk_module and \
                    type(function.parent) == vtk_module:
                observer_module = function.parent
                for a_function in observer_module.functions:
                    # right way to do this is to make SharedData a Tuple
                    if a_function._name == 'AddObserver' and \
                            len(a_function._args) == 2: 
                        (vtk_cell, _) = self.get_vtk_cell(function._args[0])
                        handler_module = vtk_module('vtkInteractionHandler')
                        handler_module.Observer(function.parent)
                        self.create_module(handler_module)
                        vtk_cell.InteractionHandler(handler_module)
                        for b_index, b_function in \
                                enumerate(vtk_cell.functions):
                            if b_function._name == 'InteractionHandler':
                                break
                        # probably need to make this position right...
                        self.create_functions(vtk_cell, [b_function],
                                              len(self.modules[id(vtk_cell)].db_functions))
                        del vtk_cell.functions[b_index]
                     
                        # print >>sys.stderr, a_function._args
                        (event_type, python_function) = a_function._args
                        # print >>sys.stderr, 'AddObserver', event_type, \
                        #     'executing'
                        self.save_modules()
                        python_function(observer_module, None)
                        f = event_type[0].lower() + event_type[1:]
                        f = f.replace('Event', 'Handler')
                        handler_code = 'def %s(observer, shareddata):\n' % f
                        # probably need to order the function calls here
                        # ideally, this would be an abstraction of some sort
                        shared_data = set()
                        for s_module in self.vtk_modules.itervalues():
                            if len(s_module.functions) > 0:
                                if not s_module._name == 'vtkRenderWindow':
                                    shared_data.add(s_module)
                                    # print >>sys.stderr, s_module._name
                                    for s_function in s_module.functions:
                                        for s_arg in s_function._args:
                                            while type(s_arg) == vtk_function:
                                                s_arg = s_arg.parent
                                            if type(s_arg) == vtk_module:
                                                shared_data.add(s_arg)
                                                #print >>sys.stderr, s_arg._name

                        s_codelines = []
                        s_arg_map = {}
                        s_arg_idx = 1

                        if len(shared_data) < 1 or (len(shared_data) == 1 and \
                                                        observer_module in \
                                                        shared_data):
                            handler_code += '    pass\n'
                        else:
                            if len(shared_data) > 2:
                                handler_code += '    ('
                                comma = ','
                            else:
                                handler_code += '    '
                                comma = ''
                            for s_module in shared_data:
                                if s_module != observer_module:
                                    handler_code += 'arg' + str(s_arg_idx) + \
                                        comma
                                    s_arg_map[id(s_module)] = s_arg_idx
                                    loop_arg_idx = s_arg_idx
                                    s_arg_idx += 1
                                else:
                                    loop_arg_idx = 0
                                for s_function in s_module.functions:
                                    s_line = (s_function.id, loop_arg_idx, 
                                              s_function)
                                    # print >>sys.stderr, "s_line:", s_line
                                    s_codelines.append(s_line)
                            if len(shared_data) > 2:
                                handler_code += ') = shareddata\n'
                            else:
                                handler_code += ' = shareddata\n'
                            # need to assign input module names, then write code
                            s_codelines.sort()

                            # need to check to see if an arg...
                            for (_, m_idx, s_function) in s_codelines:
                                s_module_name = 'observer' if m_idx == 0 else \
                                    'arg%d.vtkInstance' % m_idx
                                s_function_str = s_function._name
                                while len(s_function.sub_functions) > 0:
                                    if len(s_function.sub_functions) > 1:
                                        print >> sys.stderr, \
                                            "ERROR: too many subfunctions"
                                    # FIXME need to do args here, too
                                    s_function_str += '().' + \
                                        s_function.sub_functions[0]._name
                                    s_function = s_function.sub_functions[0]
                                handler_code += '    %s.%s(' % \
                                    (s_module_name, s_function_str)

                                s_arg_str = ''
                                for arg in s_function._args:
                                    if type(arg) == vtk_module:
                                        s_module = arg
                                    elif type(arg) == vtk_function:
                                        s_module = arg.parent
                                    else:
                                        s_arg_str += arg + ', '
                                        continue
                                    m_idx = s_arg_map[id(s_module)]
                                    s_module_name = 'observer' if m_idx == 0 \
                                        else 'arg%d.vtkInstance' % m_idx
                                    if type(arg) == vtk_module:
                                        s_arg_str += s_module_name
                                    else:
                                        s_arg_str += s_module_name + \
                                            arg._name + '()'
                                handler_code += s_arg_str + ')\n'
                                    
                                    
                        self.restore_modules()                        
                        # print >>sys.stderr, handler_code
#                         s_data_function = vtk_function('SharedData')
#                         s_data_function.parent = handler_module
#                         s_data_function._args = list(shared_data)
                        shared_data.discard(observer_module)
                        shared_data.discard(handler_module)
                        handler_module.SharedData(*shared_data)
                        handler_module.Handler(urllib.quote(handler_code))
                        # print >> sys.stderr, "shared_data", shared_data
                        # functions.append(s_data_function)
                        self.create_functions(handler_module)

                return None
            elif len(function.sub_functions) == 1:
                sub_function = function.sub_functions[0]
                if function._name == 'GetPositionCoordinate' and \
                        sub_function._name == 'SetValue':
                    # print >>sys.stderr, 'sub_function:', sub_function._args[:2]
                    new_function = vtk_function('SetPosition')
                    new_function._args = sub_function._args[:2]
                    new_function._kwargs = sub_function._kwargs
                    new_function.parent = function.parent
                    function = new_function
                    parameters.extend(new_function._args)
                elif function._name == 'GetPosition2Coordinate' and \
                        sub_function._name == 'SetValue':
                    # print >>sys.stderr, 'sub_function:', sub_function._args[:2]
                    new_function = vtk_function('SetPosition2')
                    new_function._args = sub_function._args[:2]
                    new_function._kwargs = sub_function._kwargs
                    new_function.parent = function.parent
                    function = new_function
                    parameters.extend(new_function._args)
                    
#                 # we need to use a Tuple module
#                 tuple_module = vtk_module('Tuple')
#                 self.create_module(tuple_module)
#                 new_arg_list = []
#                 for arg in function._args:
#                     if type(arg) == vtk_module or \
#                             type(arg) == vtk_function:
#                         self.create_connection(arg, tuple_module)
#                     else:
#                         new_arg_list.append(arg)
#                 tuple_function = vtk_function(
#                 function._args = 

            if len(connections) > 0:
                if len(connections) > 1 or len(parameters) > 0:
                    # need tuple
                    tuple_module = self.create_tuple(function)
                    db_function = None
                else:
                    if allow_sub:
                        for arg in connections:
                            self.create_connection(arg, function)
                    else:
                        print >>sys.stderr, \
                            "ERROR: sub function has connections"
            elif len(parameters) > 0:
                db_parameters = self.get_parameters(parameters)
                db_function = DBFunction(id=self.max_function_id,
                                         name=function._name,
                                         pos=f_pos,
                                         parameters=db_parameters,
                                         )
                self.max_function_id += 1
        return db_function
        
    def create_connection(self, src, dst):
        convert_type_map = {'input': 'destination', 'output': 'source'}
        def create_port(vtk_module, type, name, other_vtk_module):
            # print >>sys.stderr, 'creating port:', vtk_module._name, name
            if id(vtk_module) not in self.modules:
                print >>sys.stderr, 'ERROR: cannot create port', \
                    vtk_module._name, type, name
                import traceback
                traceback.print_stack()
                return (None, None)

            db_module = self.modules[id(vtk_module)]
            db_package = \
                self.registry.db_packages_identifier_index[db_module.db_package]
            if db_module.db_namespace is None:
                db_module.db_namespace = ''
            d_key = (db_module.db_name, db_module.db_namespace)
            db_module_desc = db_package.db_module_descriptors_name_index[d_key]

            if name in self.translate_ports:
                if db_module.db_name in self.translate_ports[name]:
                    name = self.translate_ports[name][db_module.db_name]
                elif (db_module.db_name, 
                      other_vtk_module._name) in self.translate_ports[name]:
                    name = self.translate_ports[name][(db_module.db_name,
                                                       other_vtk_module._name)]
                else:
                    name = self.translate_ports[name][None]

            ps_key = (name, type)
            if ps_key in db_module.db_portSpecs_name_index:
                db_module_desc = db_module
            while ps_key not in db_module_desc.db_portSpecs_name_index:
                base_id = db_module_desc.db_base_descriptor_id
                if base_id < 0:
                    print >>sys.stderr, 'ERROR: cannot create port', \
                        vtk_module._name, type, name
                    import traceback
                    traceback.print_stack()
                    return (None, None)
                db_module_desc = self.registry_desc_idx[base_id]

            db_port_spec = db_module_desc.db_portSpecs_name_index[ps_key]
            db_signature = db_port_spec.db_sigstring

            new_port = DBPort(id=self.max_port_id,
                              type=convert_type_map[type],
                              moduleId=db_module.db_id,
                              moduleName=db_module.db_name,
                              name=name,
                              signature=db_signature,
                              )
            self.max_port_id += 1
            return (db_module, new_port)
        # end create_port
        
        def find_port_info(entity):
            if type(entity) == vtk_module:
                if entity._name == 'vtkRenderWindowInteractor':
                    (entity, _) = self.get_vtk_cell(entity)
                found_module = entity
                port_name = 'self'
            elif type(entity) == vtk_function and \
                    type(entity.parent) == vtk_module:
                (found_module, inspector) = self.find_or_create_module(entity)
                if found_module:
                    if inspector:
                        port_name = entity._name
                    else:
                        port_name = 'self'
                else:
                    found_module = entity.parent
                    port_name = entity._name
            elif type(entity) == vtk_function and  \
                    type(entity.parent) == vtk_function:
                (found_module, _) = self.find_or_create_module(entity.parent)
                port_name = entity._name
                if not found_module:
                    print >>sys.stderr, \
                        "ERROR: cannot convert function", entity._name
                    
#             elif type(entity) == vtk_function:
#                 found_module = self.find_or_create_module(entity)
#                 if found_module:
#                     port_name = 'self'
#                 else:
#                     if type(entity.parent) == vtk_function:
#                         found_module = self.find_or_create_module(entity.parent)
#                         port_name = entity._name
#                         if not found_module:
#                             print >>sys.stderr, \
#                                 "ERROR: cannot convert function", entity._name
#                     else:
#                         found_module = entity.parent
#                         port_name = entity._name
            else:
                print >>sys.stderr, 'ERROR: cannot deal with type "' + \
                    str(type(entity))
                found_module = None
                port_name = None
            return (found_module, port_name)
        # end find_port_info

        src_port = None
        src_module = None
        dst_port = None
        dst_module = None

        # print >> sys.stderr, "creating connection:", src._name, dst._name

        (src_vtk_module, src_port_name) = find_port_info(src)
        (dst_vtk_module, dst_port_name) = find_port_info(dst)
        if src_vtk_module and dst_vtk_module:
            (src_module, src_port) = create_port(src_vtk_module, 'output',
                                                 src_port_name, dst_vtk_module)
            (dst_module, dst_port) = create_port(dst_vtk_module, 'input',
                                                 dst_port_name, src_vtk_module)

#         if type(src) == vtk_module:
#             src_vtk_module = src
#             (src_module, src_port) = create_port(src, 'source', 'self', 
#                                                  dst.parent)
#         elif type(src) == vtk_function:
#             # print >>sys.stderr, 'src:', src._name, src.parent._name
#             src_vtk_module = self.find_or_create_module(src)
#             if src_vtk_module:
#                 print >>sys.stderr, '** found early "%s"' % src._name, src_vtk_module._name
#                 print >>sys.stderr, 'src_vtk_module:', src_vtk_module._name
#                 src_name = 'self'
#             if not src_vtk_module:
#                 if type(src.parent) == vtk_function:
#                     src_vtk_module = self.find_or_create_module(src.parent)
#                     src_name = src._name
#                     print >>sys.stderr, 'found src_vtk_module', src_vtk_module._name, 'for', src.parent._name, src_name

#                     # print >>sys.stderr, "src_vtk_module:", id(src_vtk_module)
#                     if not src_vtk_module:
#                         print >>sys.stderr, \
#                             "ERROR: cannot convert function", src._name
#                 else:
#                     src_vtk_module = src.parent
#                     src_name = src._name
#             if src_vtk_module:
#                 (src_module, src_port) = create_port(src_vtk_module, 'source', 
#                                                      src_name, dst.parent)
#         else:
#             print >>sys.stderr, 'ERROR: cannot deal with type "' + \
#                 str(type(src)) + '"'

#         if type(dst) == vtk_function:
#             (dst_module, dst_port) = create_port(dst.parent, 'destination',
#                                                  dst._name, src_vtk_module)
#         else:
#             print >>sys.stderr, 'ERROR: cannot deal with type "' + \
#                 str(type(dst)) + '"'

        if not src_module or not dst_module:
            print >>sys.stderr, 'ERROR: cannot create connection', \
                src._name, dst._name
            return None
#         print >>sys.stderr, 'creating connection:', \
#             src_module.db_name, dst_module.db_name
        connection = DBConnection(id=self.max_connection_id,
                                  ports=[src_port, dst_port],
                                  )
        self.max_connection_id += 1
        key = (id(src_module), id(dst_module))
        if key not in self.connections:
            self.connections[key] = []
        self.connections[key].append(connection)
        if src_module.db_id not in self.vt_f_connections:
            self.vt_f_connections[src_module.db_id] = []
        self.vt_f_connections[src_module.db_id].append((dst_module.db_id, 
                                                        connection))
        if dst_module.db_id not in self.vt_b_connections:
            self.vt_b_connections[dst_module.db_id] = []
        self.vt_b_connections[dst_module.db_id].append((src_module.db_id,
                                                        connection))
        return connection

    def print_vt(self, filename=None):
        import db.services.io
        import db.services.action

        action_list = []
        for module in self.modules.itervalues():
            # print 'module:', module._name, id(module)
            action_list.append(('add', module))
        for connection_list in self.connections.itervalues():
            for connection in connection_list:
                # print 'connection:', connection._name, id(connection)
                action_list.append(('add', connection))
        self.do_layout()
        action = db.services.action.create_action(action_list)
        action.db_id = 1
        action.db_prevId = 0
        action.db_user = 'dakoop'
        action.db_date = datetime.datetime.now()

        tag = DBTag(name='Auto-Translated', id=1L)
            
        op_id = 0
        for op in action.db_operations:
            op.db_id = op_id
            op_id += 1
        vistrail = DBVistrail(actions=[action], tags=[tag], version='0.9.0')
        if filename: 
            # f = file(filename, 'w')
            script_name = os.path.splitext(filename)[0] + '.py'

            # total hack to make this a capital E
            script_name = 'E' + script_name[3:]
            annotation = DBAnnotation(id=1,
                                      key='notes',
                                      value="This workflow was automatically generated from a modified version of the vtk python example script '%s' from the vtk 5.0.4 distribution.  In most cases, running this workflow will generate a visualization that is identical to the result from the example script." % script_name)
            action.db_add_annotation(annotation)

            db.services.io.save_bundle_to_zip_xml(SaveBundle(DBVistrail.vtType, vistrail), filename)
        else:
            f = None
            print >>f, db.services.io.serialize(vistrail)
            

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

# This file was generated using vistrail_converter.py 


import core.modules
import core.modules.module_registry
from core.modules.vistrails_module import Module, ModuleError
from core.modules.basic_modules import Constant

import sr_py
import os
import time

version = "0.9.0"
identifier = "edu.utah.sci.vistrails.scirun"
name = "SCIRun"
class scirun_WriteBundle(Module) :
  def compute(self) :
    p_filetype = 'Binary'
    if self.hasInputFromPort('p_filetype') :
      p_filetype = self.getInputFromPort('p_filetype')
    p_confirm = '0'
    if self.hasInputFromPort('p_confirm') :
      p_confirm = self.getInputFromPort('p_confirm')
    p_confirm_once = '0'
    if self.hasInputFromPort('p_confirm_once') :
      p_confirm_once = self.getInputFromPort('p_confirm_once')
    bundle = 0
    if self.hasInputFromPort('bundle') :
      bundle = self.getInputFromPort('bundle')
    Filename = ''
    if self.hasInputFromPort('Filename') :
      Filename = self.getInputFromPort('Filename')
    results = sr_py.WriteBundle(bundle,Filename,p_filetype,p_confirm,p_confirm_once)

class scirun_JoinFields(Module) :
  def compute(self) :
    p_tolerance = 0.0001
    if self.hasInputFromPort('p_tolerance') :
      p_tolerance = self.getInputFromPort('p_tolerance')
    p_force_nodemerge = 1
    if self.hasInputFromPort('p_force_nodemerge') :
      p_force_nodemerge = self.getInputFromPort('p_force_nodemerge')
    p_force_pointcloud = 0
    if self.hasInputFromPort('p_force_pointcloud') :
      p_force_pointcloud = self.getInputFromPort('p_force_pointcloud')
    p_matchval = 0
    if self.hasInputFromPort('p_matchval') :
      p_matchval = self.getInputFromPort('p_matchval')
    p_meshonly = 0
    if self.hasInputFromPort('p_meshonly') :
      p_meshonly = self.getInputFromPort('p_meshonly')
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    results = sr_py.JoinFields(Field,p_tolerance,p_force_nodemerge,p_force_pointcloud,p_matchval,p_meshonly)
    self.setResult('Output Field', results)

class scirun_ApplyMappingMatrix(Module) :
  def compute(self) :
    Source = 0
    if self.hasInputFromPort('Source') :
      Source = self.getInputFromPort('Source')
    Destination = 0
    if self.hasInputFromPort('Destination') :
      Destination = self.getInputFromPort('Destination')
    Mapping = 0
    if self.hasInputFromPort('Mapping') :
      Mapping = self.getInputFromPort('Mapping')
    results = sr_py.ApplyMappingMatrix(Source,Destination,Mapping)
    self.setResult('Output', results)

class scirun_TransformPlanarMesh(Module) :
  def compute(self) :
    p_axis = 2
    if self.hasInputFromPort('p_axis') :
      p_axis = self.getInputFromPort('p_axis')
    p_invert = 0
    if self.hasInputFromPort('p_invert') :
      p_invert = self.getInputFromPort('p_invert')
    p_trans_x = 0
    if self.hasInputFromPort('p_trans_x') :
      p_trans_x = self.getInputFromPort('p_trans_x')
    p_trans_y = 0
    if self.hasInputFromPort('p_trans_y') :
      p_trans_y = self.getInputFromPort('p_trans_y')
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    Index_Matrix = 0
    if self.hasInputFromPort('Index Matrix') :
      Index_Matrix = self.getInputFromPort('Index Matrix')
    results = sr_py.TransformPlanarMesh(Input_Field,Index_Matrix,p_axis,p_invert,p_trans_x,p_trans_y)
    self.setResult('Transformed Field', results)

class scirun_MaskLatVolWithTriSurf(Module) :
  def compute(self) :
    LatVolField = 0
    if self.hasInputFromPort('LatVolField') :
      LatVolField = self.getInputFromPort('LatVolField')
    TriSurfField = 0
    if self.hasInputFromPort('TriSurfField') :
      TriSurfField = self.getInputFromPort('TriSurfField')
    results = sr_py.MaskLatVolWithTriSurf(LatVolField,TriSurfField)
    self.setResult('LatVol Mask', results)

class scirun_RefineMeshByIsovalue(Module) :
  def compute(self) :
    p_isoval = 0.0
    if self.hasInputFromPort('p_isoval') :
      p_isoval = self.getInputFromPort('p_isoval')
    p_lte = 1
    if self.hasInputFromPort('p_lte') :
      p_lte = self.getInputFromPort('p_lte')
    Input = 0
    if self.hasInputFromPort('Input') :
      Input = self.getInputFromPort('Input')
    Optional_Isovalue = 0
    if self.hasInputFromPort('Optional Isovalue') :
      Optional_Isovalue = self.getInputFromPort('Optional Isovalue')
    results = sr_py.RefineMeshByIsovalue(Input,Optional_Isovalue,p_isoval,p_lte)
    self.setResult('Refined', results[0])
    self.setResult('Mapping', results[1])

class scirun_ViewScene(Module) :
  def compute(self) :
    Geometry = 0
    if self.hasInputFromPort('Geometry') :
      Geometry = self.getInputFromPort('Geometry')
    results = sr_py.ViewScene(Geometry)

class scirun_ReportColumnMatrixMisfit(Module) :
  def compute(self) :
    p_have_ui = 0
    if self.hasInputFromPort('p_have_ui') :
      p_have_ui = self.getInputFromPort('p_have_ui')
    p_methodTCL = 'CCinv'
    if self.hasInputFromPort('p_methodTCL') :
      p_methodTCL = self.getInputFromPort('p_methodTCL')
    p_pTCL = '2'
    if self.hasInputFromPort('p_pTCL') :
      p_pTCL = self.getInputFromPort('p_pTCL')
    Vec1 = 0
    if self.hasInputFromPort('Vec1') :
      Vec1 = self.getInputFromPort('Vec1')
    Vec2 = 0
    if self.hasInputFromPort('Vec2') :
      Vec2 = self.getInputFromPort('Vec2')
    results = sr_py.ReportColumnMatrixMisfit(Vec1,Vec2,p_have_ui,p_methodTCL,p_pTCL)
    self.setResult('Error Out', results)

class scirun_EvaluateLinAlgGeneral(Module) :
  def compute(self) :
    p_function = 'o1 = i1 * 12;'
    if self.hasInputFromPort('p_function') :
      p_function = self.getInputFromPort('p_function')
    i1 = 0
    if self.hasInputFromPort('i1') :
      i1 = self.getInputFromPort('i1')
    i2 = 0
    if self.hasInputFromPort('i2') :
      i2 = self.getInputFromPort('i2')
    i3 = 0
    if self.hasInputFromPort('i3') :
      i3 = self.getInputFromPort('i3')
    i4 = 0
    if self.hasInputFromPort('i4') :
      i4 = self.getInputFromPort('i4')
    i5 = 0
    if self.hasInputFromPort('i5') :
      i5 = self.getInputFromPort('i5')
    results = sr_py.EvaluateLinAlgGeneral(i1,i2,i3,i4,i5,p_function)
    self.setResult('o1', results[0])
    self.setResult('o2', results[1])
    self.setResult('o3', results[2])
    self.setResult('o4', results[3])
    self.setResult('o5', results[4])

class scirun_AppendMatrix(Module) :
  def compute(self) :
    p_row_or_column = 'row'
    if self.hasInputFromPort('p_row_or_column') :
      p_row_or_column = self.getInputFromPort('p_row_or_column')
    BaseMatrix = 0
    if self.hasInputFromPort('BaseMatrix') :
      BaseMatrix = self.getInputFromPort('BaseMatrix')
    AppendMatrix = 0
    if self.hasInputFromPort('AppendMatrix') :
      AppendMatrix = self.getInputFromPort('AppendMatrix')
    results = sr_py.AppendMatrix(BaseMatrix,AppendMatrix,p_row_or_column)
    self.setResult('Matrix', results)

class scirun_CreateDataArray(Module) :
  def compute(self) :
    p_function = 'RESULT = abs(A);'
    if self.hasInputFromPort('p_function') :
      p_function = self.getInputFromPort('p_function')
    p_format = 'Scalar'
    if self.hasInputFromPort('p_format') :
      p_format = self.getInputFromPort('p_format')
    Size = 0
    if self.hasInputFromPort('Size') :
      Size = self.getInputFromPort('Size')
    Function = ''
    if self.hasInputFromPort('Function') :
      Function = self.getInputFromPort('Function')
    Array = 0
    if self.hasInputFromPort('Array') :
      Array = self.getInputFromPort('Array')
    results = sr_py.CreateDataArray(Size,Function,Array,p_function,p_format)
    self.setResult('DataArray', results)

class scirun_FairMesh(Module) :
  def compute(self) :
    p_iterations = 50
    if self.hasInputFromPort('p_iterations') :
      p_iterations = self.getInputFromPort('p_iterations')
    p_method = 'fast'
    if self.hasInputFromPort('p_method') :
      p_method = self.getInputFromPort('p_method')
    Input_Mesh = 0
    if self.hasInputFromPort('Input Mesh') :
      Input_Mesh = self.getInputFromPort('Input Mesh')
    results = sr_py.FairMesh(Input_Mesh,p_iterations,p_method)
    self.setResult('Faired Mesh', results)

class scirun_EvaluateLinAlgBinary(Module) :
  def compute(self) :
    p_op = 'Mult'
    if self.hasInputFromPort('p_op') :
      p_op = self.getInputFromPort('p_op')
    p_function = 'x+y'
    if self.hasInputFromPort('p_function') :
      p_function = self.getInputFromPort('p_function')
    A = 0
    if self.hasInputFromPort('A') :
      A = self.getInputFromPort('A')
    B = 0
    if self.hasInputFromPort('B') :
      B = self.getInputFromPort('B')
    results = sr_py.EvaluateLinAlgBinary(A,B,p_op,p_function)
    self.setResult('Output', results)

class scirun_PrintMatrixIntoString(Module) :
  def compute(self) :
    p_formatstring = 'time: %5.4f ms'
    if self.hasInputFromPort('p_formatstring') :
      p_formatstring = self.getInputFromPort('p_formatstring')
    Format = ''
    if self.hasInputFromPort('Format') :
      Format = self.getInputFromPort('Format')
    Input = 0
    if self.hasInputFromPort('Input') :
      Input = self.getInputFromPort('Input')
    results = sr_py.PrintMatrixIntoString(Format,Input,p_formatstring)
    self.setResult('Output', results)

class scirun_SetFieldProperty(Module) :
  def compute(self) :
    p_num_entries = '0'
    if self.hasInputFromPort('p_num_entries') :
      p_num_entries = self.getInputFromPort('p_num_entries')
    p_property = ''
    if self.hasInputFromPort('p_property') :
      p_property = self.getInputFromPort('p_property')
    p_type = 'unknown'
    if self.hasInputFromPort('p_type') :
      p_type = self.getInputFromPort('p_type')
    p_value = ''
    if self.hasInputFromPort('p_value') :
      p_value = self.getInputFromPort('p_value')
    p_readonly = '0'
    if self.hasInputFromPort('p_readonly') :
      p_readonly = self.getInputFromPort('p_readonly')
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    results = sr_py.SetFieldProperty(Field,p_num_entries,p_property,p_type,p_value,p_readonly)
    self.setResult('Field', results)

class scirun_ConvertFieldBasis(Module) :
  def compute(self) :
    p_output_basis = 'Linear'
    if self.hasInputFromPort('p_output_basis') :
      p_output_basis = self.getInputFromPort('p_output_basis')
    Input = 0
    if self.hasInputFromPort('Input') :
      Input = self.getInputFromPort('Input')
    results = sr_py.ConvertFieldBasis(Input,p_output_basis)
    self.setResult('Output', results[0])
    self.setResult('Mapping', results[1])

class scirun_ReportMeshQualityMeasures(Module) :
  def compute(self) :
    Input = 0
    if self.hasInputFromPort('Input') :
      Input = self.getInputFromPort('Input')
    results = sr_py.ReportMeshQualityMeasures(Input)
    self.setResult('Checked', results)

class scirun_SelectAndSetFieldData(Module) :
  def compute(self) :
    p_selection1 = 'DATA < A'
    if self.hasInputFromPort('p_selection1') :
      p_selection1 = self.getInputFromPort('p_selection1')
    p_function1 = 'abs(DATA)'
    if self.hasInputFromPort('p_function1') :
      p_function1 = self.getInputFromPort('p_function1')
    p_selection2 = 'DATA > A'
    if self.hasInputFromPort('p_selection2') :
      p_selection2 = self.getInputFromPort('p_selection2')
    p_function2 = '-abs(DATA)'
    if self.hasInputFromPort('p_function2') :
      p_function2 = self.getInputFromPort('p_function2')
    p_selection3 = ''
    if self.hasInputFromPort('p_selection3') :
      p_selection3 = self.getInputFromPort('p_selection3')
    p_function3 = ''
    if self.hasInputFromPort('p_function3') :
      p_function3 = self.getInputFromPort('p_function3')
    p_selection4 = ''
    if self.hasInputFromPort('p_selection4') :
      p_selection4 = self.getInputFromPort('p_selection4')
    p_function4 = ''
    if self.hasInputFromPort('p_function4') :
      p_function4 = self.getInputFromPort('p_function4')
    p_functiondef = '0'
    if self.hasInputFromPort('p_functiondef') :
      p_functiondef = self.getInputFromPort('p_functiondef')
    p_format = 'Scalar'
    if self.hasInputFromPort('p_format') :
      p_format = self.getInputFromPort('p_format')
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    Array = 0
    if self.hasInputFromPort('Array') :
      Array = self.getInputFromPort('Array')
    results = sr_py.SelectAndSetFieldData(Field,Array,p_selection1,p_function1,p_selection2,p_function2,p_selection3,p_function3,p_selection4,p_function4,p_functiondef,p_format)
    self.setResult('Field', results)

class scirun_GetColorMapsFromBundle(Module) :
  def compute(self) :
    p_colormap1_name = 'colormap1'
    if self.hasInputFromPort('p_colormap1_name') :
      p_colormap1_name = self.getInputFromPort('p_colormap1_name')
    p_colormap2_name = 'colormap2'
    if self.hasInputFromPort('p_colormap2_name') :
      p_colormap2_name = self.getInputFromPort('p_colormap2_name')
    p_colormap3_name = 'colormap3'
    if self.hasInputFromPort('p_colormap3_name') :
      p_colormap3_name = self.getInputFromPort('p_colormap3_name')
    p_colormap4_name = 'colormap4'
    if self.hasInputFromPort('p_colormap4_name') :
      p_colormap4_name = self.getInputFromPort('p_colormap4_name')
    p_colormap5_name = 'colormap5'
    if self.hasInputFromPort('p_colormap5_name') :
      p_colormap5_name = self.getInputFromPort('p_colormap5_name')
    p_colormap6_name = 'colormap6'
    if self.hasInputFromPort('p_colormap6_name') :
      p_colormap6_name = self.getInputFromPort('p_colormap6_name')
    p_colormap_selection = ''
    if self.hasInputFromPort('p_colormap_selection') :
      p_colormap_selection = self.getInputFromPort('p_colormap_selection')
    bundle = 0
    if self.hasInputFromPort('bundle') :
      bundle = self.getInputFromPort('bundle')
    results = sr_py.GetColorMapsFromBundle(bundle,p_colormap1_name,p_colormap2_name,p_colormap3_name,p_colormap4_name,p_colormap5_name,p_colormap6_name,p_colormap_selection)
    self.setResult('bundle', results[0])
    self.setResult('colormap1', results[1])
    self.setResult('colormap2', results[2])
    self.setResult('colormap3', results[3])
    self.setResult('colormap4', results[4])
    self.setResult('colormap5', results[5])
    self.setResult('colormap6', results[6])

class scirun_CreateStructHex(Module) :
  def compute(self) :
    p_sizex = 16
    if self.hasInputFromPort('p_sizex') :
      p_sizex = self.getInputFromPort('p_sizex')
    p_sizey = 16
    if self.hasInputFromPort('p_sizey') :
      p_sizey = self.getInputFromPort('p_sizey')
    p_sizez = 16
    if self.hasInputFromPort('p_sizez') :
      p_sizez = self.getInputFromPort('p_sizez')
    p_padpercent = 0.0
    if self.hasInputFromPort('p_padpercent') :
      p_padpercent = self.getInputFromPort('p_padpercent')
    p_data_at = 'Nodes'
    if self.hasInputFromPort('p_data_at') :
      p_data_at = self.getInputFromPort('p_data_at')
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    results = sr_py.CreateStructHex(Input_Field,p_sizex,p_sizey,p_sizez,p_padpercent,p_data_at)
    self.setResult('Output Sample Field', results)

class scirun_ShowColorMap(Module) :
  def compute(self) :
    p_length = 'half2'
    if self.hasInputFromPort('p_length') :
      p_length = self.getInputFromPort('p_length')
    p_side = 'left'
    if self.hasInputFromPort('p_side') :
      p_side = self.getInputFromPort('p_side')
    p_numlabels = 5
    if self.hasInputFromPort('p_numlabels') :
      p_numlabels = self.getInputFromPort('p_numlabels')
    p_scale = 1.0
    if self.hasInputFromPort('p_scale') :
      p_scale = self.getInputFromPort('p_scale')
    p_numsigdigits = 2
    if self.hasInputFromPort('p_numsigdigits') :
      p_numsigdigits = self.getInputFromPort('p_numsigdigits')
    p_units = ''
    if self.hasInputFromPort('p_units') :
      p_units = self.getInputFromPort('p_units')
    p_color_r = 1.0
    if self.hasInputFromPort('p_color_r') :
      p_color_r = self.getInputFromPort('p_color_r')
    p_color_g = 1.0
    if self.hasInputFromPort('p_color_g') :
      p_color_g = self.getInputFromPort('p_color_g')
    p_color_b = 1.0
    if self.hasInputFromPort('p_color_b') :
      p_color_b = self.getInputFromPort('p_color_b')
    p_text_fontsize = 2
    if self.hasInputFromPort('p_text_fontsize') :
      p_text_fontsize = self.getInputFromPort('p_text_fontsize')
    p_extra_padding = 0
    if self.hasInputFromPort('p_extra_padding') :
      p_extra_padding = self.getInputFromPort('p_extra_padding')
    ColorMap = 0
    if self.hasInputFromPort('ColorMap') :
      ColorMap = self.getInputFromPort('ColorMap')
    results = sr_py.ShowColorMap(ColorMap,p_length,p_side,p_numlabels,p_scale,p_numsigdigits,p_units,p_color_r,p_color_g,p_color_b,p_text_fontsize,p_extra_padding)
    self.setResult('Geometry', results)

class scirun_CalculateFieldData3(Module) :
  def compute(self) :
    p_function = 'RESULT = abs(DATA1);'
    if self.hasInputFromPort('p_function') :
      p_function = self.getInputFromPort('p_function')
    p_format = 'Scalar'
    if self.hasInputFromPort('p_format') :
      p_format = self.getInputFromPort('p_format')
    Field1 = 0
    if self.hasInputFromPort('Field1') :
      Field1 = self.getInputFromPort('Field1')
    Field2 = 0
    if self.hasInputFromPort('Field2') :
      Field2 = self.getInputFromPort('Field2')
    Field3 = 0
    if self.hasInputFromPort('Field3') :
      Field3 = self.getInputFromPort('Field3')
    Function = ''
    if self.hasInputFromPort('Function') :
      Function = self.getInputFromPort('Function')
    Array = 0
    if self.hasInputFromPort('Array') :
      Array = self.getInputFromPort('Array')
    results = sr_py.CalculateFieldData3(Field1,Field2,Field3,Function,Array,p_function,p_format)
    self.setResult('Field', results)

class scirun_InsertFieldsIntoBundle(Module) :
  def compute(self) :
    p_field1_name = 'field1'
    if self.hasInputFromPort('p_field1_name') :
      p_field1_name = self.getInputFromPort('p_field1_name')
    p_field2_name = 'field2'
    if self.hasInputFromPort('p_field2_name') :
      p_field2_name = self.getInputFromPort('p_field2_name')
    p_field3_name = 'field3'
    if self.hasInputFromPort('p_field3_name') :
      p_field3_name = self.getInputFromPort('p_field3_name')
    p_field4_name = 'field4'
    if self.hasInputFromPort('p_field4_name') :
      p_field4_name = self.getInputFromPort('p_field4_name')
    p_field5_name = 'field5'
    if self.hasInputFromPort('p_field5_name') :
      p_field5_name = self.getInputFromPort('p_field5_name')
    p_field6_name = 'field6'
    if self.hasInputFromPort('p_field6_name') :
      p_field6_name = self.getInputFromPort('p_field6_name')
    p_replace1 = 1
    if self.hasInputFromPort('p_replace1') :
      p_replace1 = self.getInputFromPort('p_replace1')
    p_replace2 = 1
    if self.hasInputFromPort('p_replace2') :
      p_replace2 = self.getInputFromPort('p_replace2')
    p_replace3 = 1
    if self.hasInputFromPort('p_replace3') :
      p_replace3 = self.getInputFromPort('p_replace3')
    p_replace4 = 1
    if self.hasInputFromPort('p_replace4') :
      p_replace4 = self.getInputFromPort('p_replace4')
    p_replace5 = 1
    if self.hasInputFromPort('p_replace5') :
      p_replace5 = self.getInputFromPort('p_replace5')
    p_replace6 = 1
    if self.hasInputFromPort('p_replace6') :
      p_replace6 = self.getInputFromPort('p_replace6')
    p_bundlename = ''
    if self.hasInputFromPort('p_bundlename') :
      p_bundlename = self.getInputFromPort('p_bundlename')
    bundle = 0
    if self.hasInputFromPort('bundle') :
      bundle = self.getInputFromPort('bundle')
    field1 = 0
    if self.hasInputFromPort('field1') :
      field1 = self.getInputFromPort('field1')
    field2 = 0
    if self.hasInputFromPort('field2') :
      field2 = self.getInputFromPort('field2')
    field3 = 0
    if self.hasInputFromPort('field3') :
      field3 = self.getInputFromPort('field3')
    field4 = 0
    if self.hasInputFromPort('field4') :
      field4 = self.getInputFromPort('field4')
    field5 = 0
    if self.hasInputFromPort('field5') :
      field5 = self.getInputFromPort('field5')
    field6 = 0
    if self.hasInputFromPort('field6') :
      field6 = self.getInputFromPort('field6')
    results = sr_py.InsertFieldsIntoBundle(bundle,field1,field2,field3,field4,field5,field6,p_field1_name,p_field2_name,p_field3_name,p_field4_name,p_field5_name,p_field6_name,p_replace1,p_replace2,p_replace3,p_replace4,p_replace5,p_replace6,p_bundlename)
    self.setResult('bundle', results)

class scirun_CreateAndEditColorMap2D(Module) :
  def compute(self) :
    p_histo = 0.5
    if self.hasInputFromPort('p_histo') :
      p_histo = self.getInputFromPort('p_histo')
    p_selected_widget = -1
    if self.hasInputFromPort('p_selected_widget') :
      p_selected_widget = self.getInputFromPort('p_selected_widget')
    p_selected_object = -1
    if self.hasInputFromPort('p_selected_object') :
      p_selected_object = self.getInputFromPort('p_selected_object')
    p_num_entries = 0
    if self.hasInputFromPort('p_num_entries') :
      p_num_entries = self.getInputFromPort('p_num_entries')
    p_marker = 'end'
    if self.hasInputFromPort('p_marker') :
      p_marker = self.getInputFromPort('p_marker')
    Input_Colormap = 0
    if self.hasInputFromPort('Input Colormap') :
      Input_Colormap = self.getInputFromPort('Input Colormap')
    Histogram = 0
    if self.hasInputFromPort('Histogram') :
      Histogram = self.getInputFromPort('Histogram')
    results = sr_py.CreateAndEditColorMap2D(Input_Colormap,Histogram,p_histo,p_selected_widget,p_selected_object,p_num_entries,p_marker)
    self.setResult('Output Colormap', results)

class scirun_CreateDataArrayFromIndices(Module) :
  def compute(self) :
    Indices = 0
    if self.hasInputFromPort('Indices') :
      Indices = self.getInputFromPort('Indices')
    Template = 0
    if self.hasInputFromPort('Template') :
      Template = self.getInputFromPort('Template')
    results = sr_py.CreateDataArrayFromIndices(Indices,Template)
    self.setResult('DataArray', results)

class scirun_ReportDataArrayInfo(Module) :
  def compute(self) :
    DataArray = 0
    if self.hasInputFromPort('DataArray') :
      DataArray = self.getInputFromPort('DataArray')
    results = sr_py.ReportDataArrayInfo(DataArray)
    self.setResult('NumElements', results)

class scirun_ConvertMaskVectorToMappingMatrix(Module) :
  def compute(self) :
    MaskVector = 0
    if self.hasInputFromPort('MaskVector') :
      MaskVector = self.getInputFromPort('MaskVector')
    results = sr_py.ConvertMaskVectorToMappingMatrix(MaskVector)
    self.setResult('MappingMatrix', results)

class scirun_GetFieldsFromBundle(Module) :
  def compute(self) :
    p_field1_name = 'field1'
    if self.hasInputFromPort('p_field1_name') :
      p_field1_name = self.getInputFromPort('p_field1_name')
    p_field2_name = 'field2'
    if self.hasInputFromPort('p_field2_name') :
      p_field2_name = self.getInputFromPort('p_field2_name')
    p_field3_name = 'field3'
    if self.hasInputFromPort('p_field3_name') :
      p_field3_name = self.getInputFromPort('p_field3_name')
    p_field4_name = 'field4'
    if self.hasInputFromPort('p_field4_name') :
      p_field4_name = self.getInputFromPort('p_field4_name')
    p_field5_name = 'field5'
    if self.hasInputFromPort('p_field5_name') :
      p_field5_name = self.getInputFromPort('p_field5_name')
    p_field6_name = 'field6'
    if self.hasInputFromPort('p_field6_name') :
      p_field6_name = self.getInputFromPort('p_field6_name')
    p_field_selection = ''
    if self.hasInputFromPort('p_field_selection') :
      p_field_selection = self.getInputFromPort('p_field_selection')
    bundle = 0
    if self.hasInputFromPort('bundle') :
      bundle = self.getInputFromPort('bundle')
    results = sr_py.GetFieldsFromBundle(bundle,p_field1_name,p_field2_name,p_field3_name,p_field4_name,p_field5_name,p_field6_name,p_field_selection)
    self.setResult('bundle', results[0])
    self.setResult('field1', results[1])
    self.setResult('field2', results[2])
    self.setResult('field3', results[3])
    self.setResult('field4', results[4])
    self.setResult('field5', results[5])
    self.setResult('field6', results[6])

class scirun_ReportScalarFieldStats(Module) :
  def compute(self) :
    p_min = 0.0
    if self.hasInputFromPort('p_min') :
      p_min = self.getInputFromPort('p_min')
    p_max = 0.0
    if self.hasInputFromPort('p_max') :
      p_max = self.getInputFromPort('p_max')
    p_mean = 0.0
    if self.hasInputFromPort('p_mean') :
      p_mean = self.getInputFromPort('p_mean')
    p_median = 0.0
    if self.hasInputFromPort('p_median') :
      p_median = self.getInputFromPort('p_median')
    p_sigma = 0.0
    if self.hasInputFromPort('p_sigma') :
      p_sigma = self.getInputFromPort('p_sigma')
    p_is_fixed = 0
    if self.hasInputFromPort('p_is_fixed') :
      p_is_fixed = self.getInputFromPort('p_is_fixed')
    p_nbuckets = 256
    if self.hasInputFromPort('p_nbuckets') :
      p_nbuckets = self.getInputFromPort('p_nbuckets')
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    results = sr_py.ReportScalarFieldStats(Input_Field,p_min,p_max,p_mean,p_median,p_sigma,p_is_fixed,p_nbuckets)

class scirun_ShowField(Module) :
  def compute(self) :
    p_nodes_on = 1
    if self.hasInputFromPort('p_nodes_on') :
      p_nodes_on = self.getInputFromPort('p_nodes_on')
    p_nodes_transparency = 0
    if self.hasInputFromPort('p_nodes_transparency') :
      p_nodes_transparency = self.getInputFromPort('p_nodes_transparency')
    p_nodes_color_type = 1
    if self.hasInputFromPort('p_nodes_color_type') :
      p_nodes_color_type = self.getInputFromPort('p_nodes_color_type')
    p_nodes_display_type = 'Points'
    if self.hasInputFromPort('p_nodes_display_type') :
      p_nodes_display_type = self.getInputFromPort('p_nodes_display_type')
    p_edges_on = 1
    if self.hasInputFromPort('p_edges_on') :
      p_edges_on = self.getInputFromPort('p_edges_on')
    p_edges_transparency = 0
    if self.hasInputFromPort('p_edges_transparency') :
      p_edges_transparency = self.getInputFromPort('p_edges_transparency')
    p_edges_color_type = 1
    if self.hasInputFromPort('p_edges_color_type') :
      p_edges_color_type = self.getInputFromPort('p_edges_color_type')
    p_edges_display_type = 'Lines'
    if self.hasInputFromPort('p_edges_display_type') :
      p_edges_display_type = self.getInputFromPort('p_edges_display_type')
    p_faces_on = 1
    if self.hasInputFromPort('p_faces_on') :
      p_faces_on = self.getInputFromPort('p_faces_on')
    p_faces_transparency = 0
    if self.hasInputFromPort('p_faces_transparency') :
      p_faces_transparency = self.getInputFromPort('p_faces_transparency')
    p_faces_color_type = 1
    if self.hasInputFromPort('p_faces_color_type') :
      p_faces_color_type = self.getInputFromPort('p_faces_color_type')
    p_faces_normals = 0
    if self.hasInputFromPort('p_faces_normals') :
      p_faces_normals = self.getInputFromPort('p_faces_normals')
    p_faces_usetexture = 0
    if self.hasInputFromPort('p_faces_usetexture') :
      p_faces_usetexture = self.getInputFromPort('p_faces_usetexture')
    p_text_on = 0
    if self.hasInputFromPort('p_text_on') :
      p_text_on = self.getInputFromPort('p_text_on')
    p_text_color_type = 0
    if self.hasInputFromPort('p_text_color_type') :
      p_text_color_type = self.getInputFromPort('p_text_color_type')
    p_text_color_r = 1.0
    if self.hasInputFromPort('p_text_color_r') :
      p_text_color_r = self.getInputFromPort('p_text_color_r')
    p_text_color_g = 1.0
    if self.hasInputFromPort('p_text_color_g') :
      p_text_color_g = self.getInputFromPort('p_text_color_g')
    p_text_color_b = 1.0
    if self.hasInputFromPort('p_text_color_b') :
      p_text_color_b = self.getInputFromPort('p_text_color_b')
    p_text_backface_cull = 0
    if self.hasInputFromPort('p_text_backface_cull') :
      p_text_backface_cull = self.getInputFromPort('p_text_backface_cull')
    p_text_always_visible = 0
    if self.hasInputFromPort('p_text_always_visible') :
      p_text_always_visible = self.getInputFromPort('p_text_always_visible')
    p_text_fontsize = 1
    if self.hasInputFromPort('p_text_fontsize') :
      p_text_fontsize = self.getInputFromPort('p_text_fontsize')
    p_text_precision = 3
    if self.hasInputFromPort('p_text_precision') :
      p_text_precision = self.getInputFromPort('p_text_precision')
    p_text_render_locations = 0
    if self.hasInputFromPort('p_text_render_locations') :
      p_text_render_locations = self.getInputFromPort('p_text_render_locations')
    p_text_show_data = 1
    if self.hasInputFromPort('p_text_show_data') :
      p_text_show_data = self.getInputFromPort('p_text_show_data')
    p_text_show_nodes = 0
    if self.hasInputFromPort('p_text_show_nodes') :
      p_text_show_nodes = self.getInputFromPort('p_text_show_nodes')
    p_text_show_edges = 0
    if self.hasInputFromPort('p_text_show_edges') :
      p_text_show_edges = self.getInputFromPort('p_text_show_edges')
    p_text_show_faces = 0
    if self.hasInputFromPort('p_text_show_faces') :
      p_text_show_faces = self.getInputFromPort('p_text_show_faces')
    p_text_show_cells = 0
    if self.hasInputFromPort('p_text_show_cells') :
      p_text_show_cells = self.getInputFromPort('p_text_show_cells')
    p_def_color_r = 0.5
    if self.hasInputFromPort('p_def_color_r') :
      p_def_color_r = self.getInputFromPort('p_def_color_r')
    p_def_color_g = 0.5
    if self.hasInputFromPort('p_def_color_g') :
      p_def_color_g = self.getInputFromPort('p_def_color_g')
    p_def_color_b = 0.5
    if self.hasInputFromPort('p_def_color_b') :
      p_def_color_b = self.getInputFromPort('p_def_color_b')
    p_def_color_a = 1.0
    if self.hasInputFromPort('p_def_color_a') :
      p_def_color_a = self.getInputFromPort('p_def_color_a')
    p_nodes_scale = 0.03
    if self.hasInputFromPort('p_nodes_scale') :
      p_nodes_scale = self.getInputFromPort('p_nodes_scale')
    p_nodes_scaleNV = 0.03
    if self.hasInputFromPort('p_nodes_scaleNV') :
      p_nodes_scaleNV = self.getInputFromPort('p_nodes_scaleNV')
    p_edges_scale = 0.15
    if self.hasInputFromPort('p_edges_scale') :
      p_edges_scale = self.getInputFromPort('p_edges_scale')
    p_edges_scaleNV = 0.15
    if self.hasInputFromPort('p_edges_scaleNV') :
      p_edges_scaleNV = self.getInputFromPort('p_edges_scaleNV')
    p_active_tab = 'Nodes'
    if self.hasInputFromPort('p_active_tab') :
      p_active_tab = self.getInputFromPort('p_active_tab')
    p_interactive_mode = 'Interactive'
    if self.hasInputFromPort('p_interactive_mode') :
      p_interactive_mode = self.getInputFromPort('p_interactive_mode')
    p_show_progress = 0
    if self.hasInputFromPort('p_show_progress') :
      p_show_progress = self.getInputFromPort('p_show_progress')
    p_field_name = ''
    if self.hasInputFromPort('p_field_name') :
      p_field_name = self.getInputFromPort('p_field_name')
    p_field_name_override = 0
    if self.hasInputFromPort('p_field_name_override') :
      p_field_name_override = self.getInputFromPort('p_field_name_override')
    p_nodes_resolution = 6
    if self.hasInputFromPort('p_nodes_resolution') :
      p_nodes_resolution = self.getInputFromPort('p_nodes_resolution')
    p_edges_resolution = 6
    if self.hasInputFromPort('p_edges_resolution') :
      p_edges_resolution = self.getInputFromPort('p_edges_resolution')
    p_approx_div = 1
    if self.hasInputFromPort('p_approx_div') :
      p_approx_div = self.getInputFromPort('p_approx_div')
    p_use_default_size = 0
    if self.hasInputFromPort('p_use_default_size') :
      p_use_default_size = self.getInputFromPort('p_use_default_size')
    Mesh = 0
    if self.hasInputFromPort('Mesh') :
      Mesh = self.getInputFromPort('Mesh')
    ColorMap = 0
    if self.hasInputFromPort('ColorMap') :
      ColorMap = self.getInputFromPort('ColorMap')
    results = sr_py.ShowField(Mesh,ColorMap,p_nodes_on,p_nodes_transparency,p_nodes_color_type,p_nodes_display_type,p_edges_on,p_edges_transparency,p_edges_color_type,p_edges_display_type,p_faces_on,p_faces_transparency,p_faces_color_type,p_faces_normals,p_faces_usetexture,p_text_on,p_text_color_type,p_text_color_r,p_text_color_g,p_text_color_b,p_text_backface_cull,p_text_always_visible,p_text_fontsize,p_text_precision,p_text_render_locations,p_text_show_data,p_text_show_nodes,p_text_show_edges,p_text_show_faces,p_text_show_cells,p_def_color_r,p_def_color_g,p_def_color_b,p_def_color_a,p_nodes_scale,p_nodes_scaleNV,p_edges_scale,p_edges_scaleNV,p_active_tab,p_interactive_mode,p_show_progress,p_field_name,p_field_name_override,p_nodes_resolution,p_edges_resolution,p_approx_div,p_use_default_size)
    self.setResult('Scene Graph', results)

class scirun_CreateVectorArray(Module) :
  def compute(self) :
    X = 0
    if self.hasInputFromPort('X') :
      X = self.getInputFromPort('X')
    Y = 0
    if self.hasInputFromPort('Y') :
      Y = self.getInputFromPort('Y')
    Z = 0
    if self.hasInputFromPort('Z') :
      Z = self.getInputFromPort('Z')
    results = sr_py.CreateVectorArray(X,Y,Z)
    self.setResult('Vector', results)

class scirun_SynchronizeGeometry(Module) :
  def compute(self) :
    p_enforce = 1
    if self.hasInputFromPort('p_enforce') :
      p_enforce = self.getInputFromPort('p_enforce')
    Input_Geometry = 0
    if self.hasInputFromPort('Input Geometry') :
      Input_Geometry = self.getInputFromPort('Input Geometry')
    results = sr_py.SynchronizeGeometry(Input_Geometry,p_enforce)
    self.setResult('Output Geometry', results)

class scirun_SolveLinearSystem(Module) :
  def compute(self) :
    p_target_error = 0.001
    if self.hasInputFromPort('p_target_error') :
      p_target_error = self.getInputFromPort('p_target_error')
    p_flops = 0.0
    if self.hasInputFromPort('p_flops') :
      p_flops = self.getInputFromPort('p_flops')
    p_floprate = 0.0
    if self.hasInputFromPort('p_floprate') :
      p_floprate = self.getInputFromPort('p_floprate')
    p_memrefs = 0.0
    if self.hasInputFromPort('p_memrefs') :
      p_memrefs = self.getInputFromPort('p_memrefs')
    p_memrate = 0.0
    if self.hasInputFromPort('p_memrate') :
      p_memrate = self.getInputFromPort('p_memrate')
    p_orig_error = 0.0
    if self.hasInputFromPort('p_orig_error') :
      p_orig_error = self.getInputFromPort('p_orig_error')
    p_current_error = ''
    if self.hasInputFromPort('p_current_error') :
      p_current_error = self.getInputFromPort('p_current_error')
    p_method = 'Conjugate Gradient & Precond. (SCI)'
    if self.hasInputFromPort('p_method') :
      p_method = self.getInputFromPort('p_method')
    p_precond = 'jacobi'
    if self.hasInputFromPort('p_precond') :
      p_precond = self.getInputFromPort('p_precond')
    p_iteration = 0
    if self.hasInputFromPort('p_iteration') :
      p_iteration = self.getInputFromPort('p_iteration')
    p_maxiter = 200
    if self.hasInputFromPort('p_maxiter') :
      p_maxiter = self.getInputFromPort('p_maxiter')
    p_use_previous_soln = 1
    if self.hasInputFromPort('p_use_previous_soln') :
      p_use_previous_soln = self.getInputFromPort('p_use_previous_soln')
    p_emit_partial = 1
    if self.hasInputFromPort('p_emit_partial') :
      p_emit_partial = self.getInputFromPort('p_emit_partial')
    p_emit_iter = 50
    if self.hasInputFromPort('p_emit_iter') :
      p_emit_iter = self.getInputFromPort('p_emit_iter')
    p_status = ''
    if self.hasInputFromPort('p_status') :
      p_status = self.getInputFromPort('p_status')
    p_np = 4
    if self.hasInputFromPort('p_np') :
      p_np = self.getInputFromPort('p_np')
    Matrix = 0
    if self.hasInputFromPort('Matrix') :
      Matrix = self.getInputFromPort('Matrix')
    RHS = 0
    if self.hasInputFromPort('RHS') :
      RHS = self.getInputFromPort('RHS')
    results = sr_py.SolveLinearSystem(Matrix,RHS,p_target_error,p_flops,p_floprate,p_memrefs,p_memrate,p_orig_error,p_current_error,p_method,p_precond,p_iteration,p_maxiter,p_use_previous_soln,p_emit_partial,p_emit_iter,p_status,p_np)
    self.setResult('Solution', results)

class scirun_SetFieldData(Module) :
  def compute(self) :
    p_keepscalartype = 0
    if self.hasInputFromPort('p_keepscalartype') :
      p_keepscalartype = self.getInputFromPort('p_keepscalartype')
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    Matrix_Data = 0
    if self.hasInputFromPort('Matrix Data') :
      Matrix_Data = self.getInputFromPort('Matrix Data')
    Nrrd_Data = 0
    if self.hasInputFromPort('Nrrd Data') :
      Nrrd_Data = self.getInputFromPort('Nrrd Data')
    results = sr_py.SetFieldData(Field,Matrix_Data,Nrrd_Data,p_keepscalartype)
    self.setResult('Field', results)

class scirun_InsertColorMap2sIntoBundle(Module) :
  def compute(self) :
    p_colormap21_name = 'colormap21'
    if self.hasInputFromPort('p_colormap21_name') :
      p_colormap21_name = self.getInputFromPort('p_colormap21_name')
    p_colormap22_name = 'colormap22'
    if self.hasInputFromPort('p_colormap22_name') :
      p_colormap22_name = self.getInputFromPort('p_colormap22_name')
    p_colormap23_name = 'colormap23'
    if self.hasInputFromPort('p_colormap23_name') :
      p_colormap23_name = self.getInputFromPort('p_colormap23_name')
    p_colormap24_name = 'colormap24'
    if self.hasInputFromPort('p_colormap24_name') :
      p_colormap24_name = self.getInputFromPort('p_colormap24_name')
    p_colormap25_name = 'colormap25'
    if self.hasInputFromPort('p_colormap25_name') :
      p_colormap25_name = self.getInputFromPort('p_colormap25_name')
    p_colormap26_name = 'colormap26'
    if self.hasInputFromPort('p_colormap26_name') :
      p_colormap26_name = self.getInputFromPort('p_colormap26_name')
    p_replace1 = 1
    if self.hasInputFromPort('p_replace1') :
      p_replace1 = self.getInputFromPort('p_replace1')
    p_replace2 = 1
    if self.hasInputFromPort('p_replace2') :
      p_replace2 = self.getInputFromPort('p_replace2')
    p_replace3 = 1
    if self.hasInputFromPort('p_replace3') :
      p_replace3 = self.getInputFromPort('p_replace3')
    p_replace4 = 1
    if self.hasInputFromPort('p_replace4') :
      p_replace4 = self.getInputFromPort('p_replace4')
    p_replace5 = 1
    if self.hasInputFromPort('p_replace5') :
      p_replace5 = self.getInputFromPort('p_replace5')
    p_replace6 = 1
    if self.hasInputFromPort('p_replace6') :
      p_replace6 = self.getInputFromPort('p_replace6')
    p_bundlename = ''
    if self.hasInputFromPort('p_bundlename') :
      p_bundlename = self.getInputFromPort('p_bundlename')
    bundle = 0
    if self.hasInputFromPort('bundle') :
      bundle = self.getInputFromPort('bundle')
    colormap21 = 0
    if self.hasInputFromPort('colormap21') :
      colormap21 = self.getInputFromPort('colormap21')
    colormap22 = 0
    if self.hasInputFromPort('colormap22') :
      colormap22 = self.getInputFromPort('colormap22')
    colormap23 = 0
    if self.hasInputFromPort('colormap23') :
      colormap23 = self.getInputFromPort('colormap23')
    colormap24 = 0
    if self.hasInputFromPort('colormap24') :
      colormap24 = self.getInputFromPort('colormap24')
    colormap25 = 0
    if self.hasInputFromPort('colormap25') :
      colormap25 = self.getInputFromPort('colormap25')
    colormap26 = 0
    if self.hasInputFromPort('colormap26') :
      colormap26 = self.getInputFromPort('colormap26')
    results = sr_py.InsertColorMap2sIntoBundle(bundle,colormap21,colormap22,colormap23,colormap24,colormap25,colormap26,p_colormap21_name,p_colormap22_name,p_colormap23_name,p_colormap24_name,p_colormap25_name,p_colormap26_name,p_replace1,p_replace2,p_replace3,p_replace4,p_replace5,p_replace6,p_bundlename)
    self.setResult('bundle', results)

class scirun_ExtractIsosurface(Module) :
  def compute(self) :
    p_isoval_min = 0.0
    if self.hasInputFromPort('p_isoval_min') :
      p_isoval_min = self.getInputFromPort('p_isoval_min')
    p_isoval_max = 99.0
    if self.hasInputFromPort('p_isoval_max') :
      p_isoval_max = self.getInputFromPort('p_isoval_max')
    p_isoval = 0.0
    if self.hasInputFromPort('p_isoval') :
      p_isoval = self.getInputFromPort('p_isoval')
    p_isoval_typed = 0.0
    if self.hasInputFromPort('p_isoval_typed') :
      p_isoval_typed = self.getInputFromPort('p_isoval_typed')
    p_isoval_quantity = 1
    if self.hasInputFromPort('p_isoval_quantity') :
      p_isoval_quantity = self.getInputFromPort('p_isoval_quantity')
    p_quantity_range = 'field'
    if self.hasInputFromPort('p_quantity_range') :
      p_quantity_range = self.getInputFromPort('p_quantity_range')
    p_quantity_clusive = 'exclusive'
    if self.hasInputFromPort('p_quantity_clusive') :
      p_quantity_clusive = self.getInputFromPort('p_quantity_clusive')
    p_quantity_min = 0.0
    if self.hasInputFromPort('p_quantity_min') :
      p_quantity_min = self.getInputFromPort('p_quantity_min')
    p_quantity_max = 100.0
    if self.hasInputFromPort('p_quantity_max') :
      p_quantity_max = self.getInputFromPort('p_quantity_max')
    p_quantity_list = ''
    if self.hasInputFromPort('p_quantity_list') :
      p_quantity_list = self.getInputFromPort('p_quantity_list')
    p_isoval_list = 'No values present.'
    if self.hasInputFromPort('p_isoval_list') :
      p_isoval_list = self.getInputFromPort('p_isoval_list')
    p_matrix_list = 'No matrix present - execution needed.'
    if self.hasInputFromPort('p_matrix_list') :
      p_matrix_list = self.getInputFromPort('p_matrix_list')
    p_algorithm = 0
    if self.hasInputFromPort('p_algorithm') :
      p_algorithm = self.getInputFromPort('p_algorithm')
    p_build_trisurf = 1
    if self.hasInputFromPort('p_build_trisurf') :
      p_build_trisurf = self.getInputFromPort('p_build_trisurf')
    p_build_geom = 1
    if self.hasInputFromPort('p_build_geom') :
      p_build_geom = self.getInputFromPort('p_build_geom')
    p_np = 1
    if self.hasInputFromPort('p_np') :
      p_np = self.getInputFromPort('p_np')
    p_active_isoval_selection_tab = '0'
    if self.hasInputFromPort('p_active_isoval_selection_tab') :
      p_active_isoval_selection_tab = self.getInputFromPort('p_active_isoval_selection_tab')
    p_active_tab = '0'
    if self.hasInputFromPort('p_active_tab') :
      p_active_tab = self.getInputFromPort('p_active_tab')
    p_update_type = 'On Release'
    if self.hasInputFromPort('p_update_type') :
      p_update_type = self.getInputFromPort('p_update_type')
    p_color_r = 0.4
    if self.hasInputFromPort('p_color_r') :
      p_color_r = self.getInputFromPort('p_color_r')
    p_color_g = 0.2
    if self.hasInputFromPort('p_color_g') :
      p_color_g = self.getInputFromPort('p_color_g')
    p_color_b = 0.9
    if self.hasInputFromPort('p_color_b') :
      p_color_b = self.getInputFromPort('p_color_b')
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    Optional_Color_Map = 0
    if self.hasInputFromPort('Optional Color Map') :
      Optional_Color_Map = self.getInputFromPort('Optional Color Map')
    Optional_Isovalues = 0
    if self.hasInputFromPort('Optional Isovalues') :
      Optional_Isovalues = self.getInputFromPort('Optional Isovalues')
    results = sr_py.ExtractIsosurface(Field,Optional_Color_Map,Optional_Isovalues,p_isoval_min,p_isoval_max,p_isoval,p_isoval_typed,p_isoval_quantity,p_quantity_range,p_quantity_clusive,p_quantity_min,p_quantity_max,p_quantity_list,p_isoval_list,p_matrix_list,p_algorithm,p_build_trisurf,p_build_geom,p_np,p_active_isoval_selection_tab,p_active_tab,p_update_type,p_color_r,p_color_g,p_color_b)
    self.setResult('Surface', results[0])
    self.setResult('Geometry', results[1])
    self.setResult('Mapping', results[2])

class scirun_ConvertMatrixToString(Module) :
  def compute(self) :
    Matrix = 0
    if self.hasInputFromPort('Matrix') :
      Matrix = self.getInputFromPort('Matrix')
    results = sr_py.ConvertMatrixToString(Matrix)
    self.setResult('String', results)

class scirun_ReportMatrixColumnMeasure(Module) :
  def compute(self) :
    p_method = 'Sum'
    if self.hasInputFromPort('p_method') :
      p_method = self.getInputFromPort('p_method')
    Matrix = 0
    if self.hasInputFromPort('Matrix') :
      Matrix = self.getInputFromPort('Matrix')
    results = sr_py.ReportMatrixColumnMeasure(Matrix,p_method)
    self.setResult('Vector', results)

class scirun_ReplicateDataArray(Module) :
  def compute(self) :
    p_size = 1
    if self.hasInputFromPort('p_size') :
      p_size = self.getInputFromPort('p_size')
    DataArray = 0
    if self.hasInputFromPort('DataArray') :
      DataArray = self.getInputFromPort('DataArray')
    Size = 0
    if self.hasInputFromPort('Size') :
      Size = self.getInputFromPort('Size')
    results = sr_py.ReplicateDataArray(DataArray,Size,p_size)
    self.setResult('DataArray', results)

class scirun_SortMatrix(Module) :
  def compute(self) :
    p_row_or_col = 'row'
    if self.hasInputFromPort('p_row_or_col') :
      p_row_or_col = self.getInputFromPort('p_row_or_col')
    Matrix = 0
    if self.hasInputFromPort('Matrix') :
      Matrix = self.getInputFromPort('Matrix')
    results = sr_py.SortMatrix(Matrix,p_row_or_col)
    self.setResult('Matrix', results)

class scirun_ConvertMeshToUnstructuredMesh(Module) :
  def compute(self) :
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    results = sr_py.ConvertMeshToUnstructuredMesh(Input_Field)
    self.setResult('Output Field', results)

class scirun_CreateViewerAxes(Module) :
  def compute(self) :
    p_precision = '3'
    if self.hasInputFromPort('p_precision') :
      p_precision = self.getInputFromPort('p_precision')
    p_squash = '0.7'
    if self.hasInputFromPort('p_squash') :
      p_squash = self.getInputFromPort('p_squash')
    p_valuerez = '72'
    if self.hasInputFromPort('p_valuerez') :
      p_valuerez = self.getInputFromPort('p_valuerez')
    p_labelrez = '72'
    if self.hasInputFromPort('p_labelrez') :
      p_labelrez = self.getInputFromPort('p_labelrez')
    p_Plane_01_0_Axis_absolute = ''
    if self.hasInputFromPort('p_Plane_01_0_Axis_absolute') :
      p_Plane_01_0_Axis_absolute = self.getInputFromPort('p_Plane_01_0_Axis_absolute')
    p_Plane_01_0_Axis_divisions = '10'
    if self.hasInputFromPort('p_Plane_01_0_Axis_divisions') :
      p_Plane_01_0_Axis_divisions = self.getInputFromPort('p_Plane_01_0_Axis_divisions')
    p_Plane_01_0_Axis_offset = '1'
    if self.hasInputFromPort('p_Plane_01_0_Axis_offset') :
      p_Plane_01_0_Axis_offset = self.getInputFromPort('p_Plane_01_0_Axis_offset')
    p_Plane_01_0_Axis_range_first = '0.0'
    if self.hasInputFromPort('p_Plane_01_0_Axis_range_first') :
      p_Plane_01_0_Axis_range_first = self.getInputFromPort('p_Plane_01_0_Axis_range_first')
    p_Plane_01_0_Axis_range_second = '1.0'
    if self.hasInputFromPort('p_Plane_01_0_Axis_range_second') :
      p_Plane_01_0_Axis_range_second = self.getInputFromPort('p_Plane_01_0_Axis_range_second')
    p_Plane_01_0_Axis_min_absolute = '0.0'
    if self.hasInputFromPort('p_Plane_01_0_Axis_min_absolute') :
      p_Plane_01_0_Axis_min_absolute = self.getInputFromPort('p_Plane_01_0_Axis_min_absolute')
    p_Plane_01_0_Axis_max_absolute = '1.0'
    if self.hasInputFromPort('p_Plane_01_0_Axis_max_absolute') :
      p_Plane_01_0_Axis_max_absolute = self.getInputFromPort('p_Plane_01_0_Axis_max_absolute')
    p_Plane_01_0_Axis_minplane = '2'
    if self.hasInputFromPort('p_Plane_01_0_Axis_minplane') :
      p_Plane_01_0_Axis_minplane = self.getInputFromPort('p_Plane_01_0_Axis_minplane')
    p_Plane_01_0_Axis_maxplane = '2'
    if self.hasInputFromPort('p_Plane_01_0_Axis_maxplane') :
      p_Plane_01_0_Axis_maxplane = self.getInputFromPort('p_Plane_01_0_Axis_maxplane')
    p_Plane_01_0_Axis_lines = '2'
    if self.hasInputFromPort('p_Plane_01_0_Axis_lines') :
      p_Plane_01_0_Axis_lines = self.getInputFromPort('p_Plane_01_0_Axis_lines')
    p_Plane_01_0_Axis_minticks = '2'
    if self.hasInputFromPort('p_Plane_01_0_Axis_minticks') :
      p_Plane_01_0_Axis_minticks = self.getInputFromPort('p_Plane_01_0_Axis_minticks')
    p_Plane_01_0_Axis_maxticks = '2'
    if self.hasInputFromPort('p_Plane_01_0_Axis_maxticks') :
      p_Plane_01_0_Axis_maxticks = self.getInputFromPort('p_Plane_01_0_Axis_maxticks')
    p_Plane_01_0_Axis_minlabel = '2'
    if self.hasInputFromPort('p_Plane_01_0_Axis_minlabel') :
      p_Plane_01_0_Axis_minlabel = self.getInputFromPort('p_Plane_01_0_Axis_minlabel')
    p_Plane_01_0_Axis_maxlabel = '2'
    if self.hasInputFromPort('p_Plane_01_0_Axis_maxlabel') :
      p_Plane_01_0_Axis_maxlabel = self.getInputFromPort('p_Plane_01_0_Axis_maxlabel')
    p_Plane_01_0_Axis_minvalue = '2'
    if self.hasInputFromPort('p_Plane_01_0_Axis_minvalue') :
      p_Plane_01_0_Axis_minvalue = self.getInputFromPort('p_Plane_01_0_Axis_minvalue')
    p_Plane_01_0_Axis_maxvalue = '2'
    if self.hasInputFromPort('p_Plane_01_0_Axis_maxvalue') :
      p_Plane_01_0_Axis_maxvalue = self.getInputFromPort('p_Plane_01_0_Axis_maxvalue')
    p_Plane_01_0_Axis_width = '1'
    if self.hasInputFromPort('p_Plane_01_0_Axis_width') :
      p_Plane_01_0_Axis_width = self.getInputFromPort('p_Plane_01_0_Axis_width')
    p_Plane_01_0_Axis_tickangle = '0'
    if self.hasInputFromPort('p_Plane_01_0_Axis_tickangle') :
      p_Plane_01_0_Axis_tickangle = self.getInputFromPort('p_Plane_01_0_Axis_tickangle')
    p_Plane_01_0_Axis_ticktilt = '0'
    if self.hasInputFromPort('p_Plane_01_0_Axis_ticktilt') :
      p_Plane_01_0_Axis_ticktilt = self.getInputFromPort('p_Plane_01_0_Axis_ticktilt')
    p_Plane_01_0_Axis_ticksize = '5'
    if self.hasInputFromPort('p_Plane_01_0_Axis_ticksize') :
      p_Plane_01_0_Axis_ticksize = self.getInputFromPort('p_Plane_01_0_Axis_ticksize')
    p_Plane_01_0_Axis_labelangle = '0'
    if self.hasInputFromPort('p_Plane_01_0_Axis_labelangle') :
      p_Plane_01_0_Axis_labelangle = self.getInputFromPort('p_Plane_01_0_Axis_labelangle')
    p_Plane_01_0_Axis_labelheight = '6'
    if self.hasInputFromPort('p_Plane_01_0_Axis_labelheight') :
      p_Plane_01_0_Axis_labelheight = self.getInputFromPort('p_Plane_01_0_Axis_labelheight')
    p_Plane_01_0_Axis_valuesize = '3'
    if self.hasInputFromPort('p_Plane_01_0_Axis_valuesize') :
      p_Plane_01_0_Axis_valuesize = self.getInputFromPort('p_Plane_01_0_Axis_valuesize')
    p_Plane_01_0_Axis_valuesquash = '1.0'
    if self.hasInputFromPort('p_Plane_01_0_Axis_valuesquash') :
      p_Plane_01_0_Axis_valuesquash = self.getInputFromPort('p_Plane_01_0_Axis_valuesquash')
    p_Plane_01_1_Axis_absolute = ''
    if self.hasInputFromPort('p_Plane_01_1_Axis_absolute') :
      p_Plane_01_1_Axis_absolute = self.getInputFromPort('p_Plane_01_1_Axis_absolute')
    p_Plane_01_1_Axis_divisions = '10'
    if self.hasInputFromPort('p_Plane_01_1_Axis_divisions') :
      p_Plane_01_1_Axis_divisions = self.getInputFromPort('p_Plane_01_1_Axis_divisions')
    p_Plane_01_1_Axis_offset = '1'
    if self.hasInputFromPort('p_Plane_01_1_Axis_offset') :
      p_Plane_01_1_Axis_offset = self.getInputFromPort('p_Plane_01_1_Axis_offset')
    p_Plane_01_1_Axis_range_first = '0.0'
    if self.hasInputFromPort('p_Plane_01_1_Axis_range_first') :
      p_Plane_01_1_Axis_range_first = self.getInputFromPort('p_Plane_01_1_Axis_range_first')
    p_Plane_01_1_Axis_range_second = '1.0'
    if self.hasInputFromPort('p_Plane_01_1_Axis_range_second') :
      p_Plane_01_1_Axis_range_second = self.getInputFromPort('p_Plane_01_1_Axis_range_second')
    p_Plane_01_1_Axis_min_absolute = '0.0'
    if self.hasInputFromPort('p_Plane_01_1_Axis_min_absolute') :
      p_Plane_01_1_Axis_min_absolute = self.getInputFromPort('p_Plane_01_1_Axis_min_absolute')
    p_Plane_01_1_Axis_max_absolute = '1.0'
    if self.hasInputFromPort('p_Plane_01_1_Axis_max_absolute') :
      p_Plane_01_1_Axis_max_absolute = self.getInputFromPort('p_Plane_01_1_Axis_max_absolute')
    p_Plane_01_1_Axis_minplane = '2'
    if self.hasInputFromPort('p_Plane_01_1_Axis_minplane') :
      p_Plane_01_1_Axis_minplane = self.getInputFromPort('p_Plane_01_1_Axis_minplane')
    p_Plane_01_1_Axis_maxplane = '2'
    if self.hasInputFromPort('p_Plane_01_1_Axis_maxplane') :
      p_Plane_01_1_Axis_maxplane = self.getInputFromPort('p_Plane_01_1_Axis_maxplane')
    p_Plane_01_1_Axis_lines = '2'
    if self.hasInputFromPort('p_Plane_01_1_Axis_lines') :
      p_Plane_01_1_Axis_lines = self.getInputFromPort('p_Plane_01_1_Axis_lines')
    p_Plane_01_1_Axis_minticks = '2'
    if self.hasInputFromPort('p_Plane_01_1_Axis_minticks') :
      p_Plane_01_1_Axis_minticks = self.getInputFromPort('p_Plane_01_1_Axis_minticks')
    p_Plane_01_1_Axis_maxticks = '2'
    if self.hasInputFromPort('p_Plane_01_1_Axis_maxticks') :
      p_Plane_01_1_Axis_maxticks = self.getInputFromPort('p_Plane_01_1_Axis_maxticks')
    p_Plane_01_1_Axis_minlabel = '2'
    if self.hasInputFromPort('p_Plane_01_1_Axis_minlabel') :
      p_Plane_01_1_Axis_minlabel = self.getInputFromPort('p_Plane_01_1_Axis_minlabel')
    p_Plane_01_1_Axis_maxlabel = '2'
    if self.hasInputFromPort('p_Plane_01_1_Axis_maxlabel') :
      p_Plane_01_1_Axis_maxlabel = self.getInputFromPort('p_Plane_01_1_Axis_maxlabel')
    p_Plane_01_1_Axis_minvalue = '2'
    if self.hasInputFromPort('p_Plane_01_1_Axis_minvalue') :
      p_Plane_01_1_Axis_minvalue = self.getInputFromPort('p_Plane_01_1_Axis_minvalue')
    p_Plane_01_1_Axis_maxvalue = '2'
    if self.hasInputFromPort('p_Plane_01_1_Axis_maxvalue') :
      p_Plane_01_1_Axis_maxvalue = self.getInputFromPort('p_Plane_01_1_Axis_maxvalue')
    p_Plane_01_1_Axis_width = '1'
    if self.hasInputFromPort('p_Plane_01_1_Axis_width') :
      p_Plane_01_1_Axis_width = self.getInputFromPort('p_Plane_01_1_Axis_width')
    p_Plane_01_1_Axis_tickangle = '0'
    if self.hasInputFromPort('p_Plane_01_1_Axis_tickangle') :
      p_Plane_01_1_Axis_tickangle = self.getInputFromPort('p_Plane_01_1_Axis_tickangle')
    p_Plane_01_1_Axis_ticktilt = '0'
    if self.hasInputFromPort('p_Plane_01_1_Axis_ticktilt') :
      p_Plane_01_1_Axis_ticktilt = self.getInputFromPort('p_Plane_01_1_Axis_ticktilt')
    p_Plane_01_1_Axis_ticksize = '5'
    if self.hasInputFromPort('p_Plane_01_1_Axis_ticksize') :
      p_Plane_01_1_Axis_ticksize = self.getInputFromPort('p_Plane_01_1_Axis_ticksize')
    p_Plane_01_1_Axis_labelangle = '0'
    if self.hasInputFromPort('p_Plane_01_1_Axis_labelangle') :
      p_Plane_01_1_Axis_labelangle = self.getInputFromPort('p_Plane_01_1_Axis_labelangle')
    p_Plane_01_1_Axis_labelheight = '6'
    if self.hasInputFromPort('p_Plane_01_1_Axis_labelheight') :
      p_Plane_01_1_Axis_labelheight = self.getInputFromPort('p_Plane_01_1_Axis_labelheight')
    p_Plane_01_1_Axis_valuesize = '3'
    if self.hasInputFromPort('p_Plane_01_1_Axis_valuesize') :
      p_Plane_01_1_Axis_valuesize = self.getInputFromPort('p_Plane_01_1_Axis_valuesize')
    p_Plane_01_1_Axis_valuesquash = '1.0'
    if self.hasInputFromPort('p_Plane_01_1_Axis_valuesquash') :
      p_Plane_01_1_Axis_valuesquash = self.getInputFromPort('p_Plane_01_1_Axis_valuesquash')
    p_Plane_02_0_Axis_absolute = ''
    if self.hasInputFromPort('p_Plane_02_0_Axis_absolute') :
      p_Plane_02_0_Axis_absolute = self.getInputFromPort('p_Plane_02_0_Axis_absolute')
    p_Plane_02_0_Axis_divisions = '10'
    if self.hasInputFromPort('p_Plane_02_0_Axis_divisions') :
      p_Plane_02_0_Axis_divisions = self.getInputFromPort('p_Plane_02_0_Axis_divisions')
    p_Plane_02_0_Axis_offset = '1'
    if self.hasInputFromPort('p_Plane_02_0_Axis_offset') :
      p_Plane_02_0_Axis_offset = self.getInputFromPort('p_Plane_02_0_Axis_offset')
    p_Plane_02_0_Axis_range_first = '0.0'
    if self.hasInputFromPort('p_Plane_02_0_Axis_range_first') :
      p_Plane_02_0_Axis_range_first = self.getInputFromPort('p_Plane_02_0_Axis_range_first')
    p_Plane_02_0_Axis_range_second = '1.0'
    if self.hasInputFromPort('p_Plane_02_0_Axis_range_second') :
      p_Plane_02_0_Axis_range_second = self.getInputFromPort('p_Plane_02_0_Axis_range_second')
    p_Plane_02_0_Axis_min_absolute = '0.0'
    if self.hasInputFromPort('p_Plane_02_0_Axis_min_absolute') :
      p_Plane_02_0_Axis_min_absolute = self.getInputFromPort('p_Plane_02_0_Axis_min_absolute')
    p_Plane_02_0_Axis_max_absolute = '1.0'
    if self.hasInputFromPort('p_Plane_02_0_Axis_max_absolute') :
      p_Plane_02_0_Axis_max_absolute = self.getInputFromPort('p_Plane_02_0_Axis_max_absolute')
    p_Plane_02_0_Axis_minplane = '2'
    if self.hasInputFromPort('p_Plane_02_0_Axis_minplane') :
      p_Plane_02_0_Axis_minplane = self.getInputFromPort('p_Plane_02_0_Axis_minplane')
    p_Plane_02_0_Axis_maxplane = '2'
    if self.hasInputFromPort('p_Plane_02_0_Axis_maxplane') :
      p_Plane_02_0_Axis_maxplane = self.getInputFromPort('p_Plane_02_0_Axis_maxplane')
    p_Plane_02_0_Axis_lines = '2'
    if self.hasInputFromPort('p_Plane_02_0_Axis_lines') :
      p_Plane_02_0_Axis_lines = self.getInputFromPort('p_Plane_02_0_Axis_lines')
    p_Plane_02_0_Axis_minticks = '2'
    if self.hasInputFromPort('p_Plane_02_0_Axis_minticks') :
      p_Plane_02_0_Axis_minticks = self.getInputFromPort('p_Plane_02_0_Axis_minticks')
    p_Plane_02_0_Axis_maxticks = '2'
    if self.hasInputFromPort('p_Plane_02_0_Axis_maxticks') :
      p_Plane_02_0_Axis_maxticks = self.getInputFromPort('p_Plane_02_0_Axis_maxticks')
    p_Plane_02_0_Axis_minlabel = '2'
    if self.hasInputFromPort('p_Plane_02_0_Axis_minlabel') :
      p_Plane_02_0_Axis_minlabel = self.getInputFromPort('p_Plane_02_0_Axis_minlabel')
    p_Plane_02_0_Axis_maxlabel = '2'
    if self.hasInputFromPort('p_Plane_02_0_Axis_maxlabel') :
      p_Plane_02_0_Axis_maxlabel = self.getInputFromPort('p_Plane_02_0_Axis_maxlabel')
    p_Plane_02_0_Axis_minvalue = '2'
    if self.hasInputFromPort('p_Plane_02_0_Axis_minvalue') :
      p_Plane_02_0_Axis_minvalue = self.getInputFromPort('p_Plane_02_0_Axis_minvalue')
    p_Plane_02_0_Axis_maxvalue = '2'
    if self.hasInputFromPort('p_Plane_02_0_Axis_maxvalue') :
      p_Plane_02_0_Axis_maxvalue = self.getInputFromPort('p_Plane_02_0_Axis_maxvalue')
    p_Plane_02_0_Axis_width = '1'
    if self.hasInputFromPort('p_Plane_02_0_Axis_width') :
      p_Plane_02_0_Axis_width = self.getInputFromPort('p_Plane_02_0_Axis_width')
    p_Plane_02_0_Axis_tickangle = '0'
    if self.hasInputFromPort('p_Plane_02_0_Axis_tickangle') :
      p_Plane_02_0_Axis_tickangle = self.getInputFromPort('p_Plane_02_0_Axis_tickangle')
    p_Plane_02_0_Axis_ticktilt = '0'
    if self.hasInputFromPort('p_Plane_02_0_Axis_ticktilt') :
      p_Plane_02_0_Axis_ticktilt = self.getInputFromPort('p_Plane_02_0_Axis_ticktilt')
    p_Plane_02_0_Axis_ticksize = '5'
    if self.hasInputFromPort('p_Plane_02_0_Axis_ticksize') :
      p_Plane_02_0_Axis_ticksize = self.getInputFromPort('p_Plane_02_0_Axis_ticksize')
    p_Plane_02_0_Axis_labelangle = '0'
    if self.hasInputFromPort('p_Plane_02_0_Axis_labelangle') :
      p_Plane_02_0_Axis_labelangle = self.getInputFromPort('p_Plane_02_0_Axis_labelangle')
    p_Plane_02_0_Axis_labelheight = '6'
    if self.hasInputFromPort('p_Plane_02_0_Axis_labelheight') :
      p_Plane_02_0_Axis_labelheight = self.getInputFromPort('p_Plane_02_0_Axis_labelheight')
    p_Plane_02_0_Axis_valuesize = '3'
    if self.hasInputFromPort('p_Plane_02_0_Axis_valuesize') :
      p_Plane_02_0_Axis_valuesize = self.getInputFromPort('p_Plane_02_0_Axis_valuesize')
    p_Plane_02_0_Axis_valuesquash = '1.0'
    if self.hasInputFromPort('p_Plane_02_0_Axis_valuesquash') :
      p_Plane_02_0_Axis_valuesquash = self.getInputFromPort('p_Plane_02_0_Axis_valuesquash')
    p_Plane_02_2_Axis_absolute = ''
    if self.hasInputFromPort('p_Plane_02_2_Axis_absolute') :
      p_Plane_02_2_Axis_absolute = self.getInputFromPort('p_Plane_02_2_Axis_absolute')
    p_Plane_02_2_Axis_divisions = '10'
    if self.hasInputFromPort('p_Plane_02_2_Axis_divisions') :
      p_Plane_02_2_Axis_divisions = self.getInputFromPort('p_Plane_02_2_Axis_divisions')
    p_Plane_02_2_Axis_offset = '1'
    if self.hasInputFromPort('p_Plane_02_2_Axis_offset') :
      p_Plane_02_2_Axis_offset = self.getInputFromPort('p_Plane_02_2_Axis_offset')
    p_Plane_02_2_Axis_range_first = '0.0'
    if self.hasInputFromPort('p_Plane_02_2_Axis_range_first') :
      p_Plane_02_2_Axis_range_first = self.getInputFromPort('p_Plane_02_2_Axis_range_first')
    p_Plane_02_2_Axis_range_second = '1.0'
    if self.hasInputFromPort('p_Plane_02_2_Axis_range_second') :
      p_Plane_02_2_Axis_range_second = self.getInputFromPort('p_Plane_02_2_Axis_range_second')
    p_Plane_02_2_Axis_min_absolute = '0.0'
    if self.hasInputFromPort('p_Plane_02_2_Axis_min_absolute') :
      p_Plane_02_2_Axis_min_absolute = self.getInputFromPort('p_Plane_02_2_Axis_min_absolute')
    p_Plane_02_2_Axis_max_absolute = '1.0'
    if self.hasInputFromPort('p_Plane_02_2_Axis_max_absolute') :
      p_Plane_02_2_Axis_max_absolute = self.getInputFromPort('p_Plane_02_2_Axis_max_absolute')
    p_Plane_02_2_Axis_minplane = '2'
    if self.hasInputFromPort('p_Plane_02_2_Axis_minplane') :
      p_Plane_02_2_Axis_minplane = self.getInputFromPort('p_Plane_02_2_Axis_minplane')
    p_Plane_02_2_Axis_maxplane = '2'
    if self.hasInputFromPort('p_Plane_02_2_Axis_maxplane') :
      p_Plane_02_2_Axis_maxplane = self.getInputFromPort('p_Plane_02_2_Axis_maxplane')
    p_Plane_02_2_Axis_lines = '2'
    if self.hasInputFromPort('p_Plane_02_2_Axis_lines') :
      p_Plane_02_2_Axis_lines = self.getInputFromPort('p_Plane_02_2_Axis_lines')
    p_Plane_02_2_Axis_minticks = '2'
    if self.hasInputFromPort('p_Plane_02_2_Axis_minticks') :
      p_Plane_02_2_Axis_minticks = self.getInputFromPort('p_Plane_02_2_Axis_minticks')
    p_Plane_02_2_Axis_maxticks = '2'
    if self.hasInputFromPort('p_Plane_02_2_Axis_maxticks') :
      p_Plane_02_2_Axis_maxticks = self.getInputFromPort('p_Plane_02_2_Axis_maxticks')
    p_Plane_02_2_Axis_minlabel = '2'
    if self.hasInputFromPort('p_Plane_02_2_Axis_minlabel') :
      p_Plane_02_2_Axis_minlabel = self.getInputFromPort('p_Plane_02_2_Axis_minlabel')
    p_Plane_02_2_Axis_maxlabel = '2'
    if self.hasInputFromPort('p_Plane_02_2_Axis_maxlabel') :
      p_Plane_02_2_Axis_maxlabel = self.getInputFromPort('p_Plane_02_2_Axis_maxlabel')
    p_Plane_02_2_Axis_minvalue = '2'
    if self.hasInputFromPort('p_Plane_02_2_Axis_minvalue') :
      p_Plane_02_2_Axis_minvalue = self.getInputFromPort('p_Plane_02_2_Axis_minvalue')
    p_Plane_02_2_Axis_maxvalue = '2'
    if self.hasInputFromPort('p_Plane_02_2_Axis_maxvalue') :
      p_Plane_02_2_Axis_maxvalue = self.getInputFromPort('p_Plane_02_2_Axis_maxvalue')
    p_Plane_02_2_Axis_width = '1'
    if self.hasInputFromPort('p_Plane_02_2_Axis_width') :
      p_Plane_02_2_Axis_width = self.getInputFromPort('p_Plane_02_2_Axis_width')
    p_Plane_02_2_Axis_tickangle = '0'
    if self.hasInputFromPort('p_Plane_02_2_Axis_tickangle') :
      p_Plane_02_2_Axis_tickangle = self.getInputFromPort('p_Plane_02_2_Axis_tickangle')
    p_Plane_02_2_Axis_ticktilt = '0'
    if self.hasInputFromPort('p_Plane_02_2_Axis_ticktilt') :
      p_Plane_02_2_Axis_ticktilt = self.getInputFromPort('p_Plane_02_2_Axis_ticktilt')
    p_Plane_02_2_Axis_ticksize = '5'
    if self.hasInputFromPort('p_Plane_02_2_Axis_ticksize') :
      p_Plane_02_2_Axis_ticksize = self.getInputFromPort('p_Plane_02_2_Axis_ticksize')
    p_Plane_02_2_Axis_labelangle = '0'
    if self.hasInputFromPort('p_Plane_02_2_Axis_labelangle') :
      p_Plane_02_2_Axis_labelangle = self.getInputFromPort('p_Plane_02_2_Axis_labelangle')
    p_Plane_02_2_Axis_labelheight = '6'
    if self.hasInputFromPort('p_Plane_02_2_Axis_labelheight') :
      p_Plane_02_2_Axis_labelheight = self.getInputFromPort('p_Plane_02_2_Axis_labelheight')
    p_Plane_02_2_Axis_valuesize = '3'
    if self.hasInputFromPort('p_Plane_02_2_Axis_valuesize') :
      p_Plane_02_2_Axis_valuesize = self.getInputFromPort('p_Plane_02_2_Axis_valuesize')
    p_Plane_02_2_Axis_valuesquash = '1.0'
    if self.hasInputFromPort('p_Plane_02_2_Axis_valuesquash') :
      p_Plane_02_2_Axis_valuesquash = self.getInputFromPort('p_Plane_02_2_Axis_valuesquash')
    p_Plane_12_1_Axis_absolute = ''
    if self.hasInputFromPort('p_Plane_12_1_Axis_absolute') :
      p_Plane_12_1_Axis_absolute = self.getInputFromPort('p_Plane_12_1_Axis_absolute')
    p_Plane_12_1_Axis_divisions = '10'
    if self.hasInputFromPort('p_Plane_12_1_Axis_divisions') :
      p_Plane_12_1_Axis_divisions = self.getInputFromPort('p_Plane_12_1_Axis_divisions')
    p_Plane_12_1_Axis_offset = '1'
    if self.hasInputFromPort('p_Plane_12_1_Axis_offset') :
      p_Plane_12_1_Axis_offset = self.getInputFromPort('p_Plane_12_1_Axis_offset')
    p_Plane_12_1_Axis_range_first = '0.0'
    if self.hasInputFromPort('p_Plane_12_1_Axis_range_first') :
      p_Plane_12_1_Axis_range_first = self.getInputFromPort('p_Plane_12_1_Axis_range_first')
    p_Plane_12_1_Axis_range_second = '1.0'
    if self.hasInputFromPort('p_Plane_12_1_Axis_range_second') :
      p_Plane_12_1_Axis_range_second = self.getInputFromPort('p_Plane_12_1_Axis_range_second')
    p_Plane_12_1_Axis_min_absolute = '0.0'
    if self.hasInputFromPort('p_Plane_12_1_Axis_min_absolute') :
      p_Plane_12_1_Axis_min_absolute = self.getInputFromPort('p_Plane_12_1_Axis_min_absolute')
    p_Plane_12_1_Axis_max_absolute = '1.0'
    if self.hasInputFromPort('p_Plane_12_1_Axis_max_absolute') :
      p_Plane_12_1_Axis_max_absolute = self.getInputFromPort('p_Plane_12_1_Axis_max_absolute')
    p_Plane_12_1_Axis_minplane = '2'
    if self.hasInputFromPort('p_Plane_12_1_Axis_minplane') :
      p_Plane_12_1_Axis_minplane = self.getInputFromPort('p_Plane_12_1_Axis_minplane')
    p_Plane_12_1_Axis_maxplane = '2'
    if self.hasInputFromPort('p_Plane_12_1_Axis_maxplane') :
      p_Plane_12_1_Axis_maxplane = self.getInputFromPort('p_Plane_12_1_Axis_maxplane')
    p_Plane_12_1_Axis_lines = '2'
    if self.hasInputFromPort('p_Plane_12_1_Axis_lines') :
      p_Plane_12_1_Axis_lines = self.getInputFromPort('p_Plane_12_1_Axis_lines')
    p_Plane_12_1_Axis_minticks = '2'
    if self.hasInputFromPort('p_Plane_12_1_Axis_minticks') :
      p_Plane_12_1_Axis_minticks = self.getInputFromPort('p_Plane_12_1_Axis_minticks')
    p_Plane_12_1_Axis_maxticks = '2'
    if self.hasInputFromPort('p_Plane_12_1_Axis_maxticks') :
      p_Plane_12_1_Axis_maxticks = self.getInputFromPort('p_Plane_12_1_Axis_maxticks')
    p_Plane_12_1_Axis_minlabel = '2'
    if self.hasInputFromPort('p_Plane_12_1_Axis_minlabel') :
      p_Plane_12_1_Axis_minlabel = self.getInputFromPort('p_Plane_12_1_Axis_minlabel')
    p_Plane_12_1_Axis_maxlabel = '2'
    if self.hasInputFromPort('p_Plane_12_1_Axis_maxlabel') :
      p_Plane_12_1_Axis_maxlabel = self.getInputFromPort('p_Plane_12_1_Axis_maxlabel')
    p_Plane_12_1_Axis_minvalue = '2'
    if self.hasInputFromPort('p_Plane_12_1_Axis_minvalue') :
      p_Plane_12_1_Axis_minvalue = self.getInputFromPort('p_Plane_12_1_Axis_minvalue')
    p_Plane_12_1_Axis_maxvalue = '2'
    if self.hasInputFromPort('p_Plane_12_1_Axis_maxvalue') :
      p_Plane_12_1_Axis_maxvalue = self.getInputFromPort('p_Plane_12_1_Axis_maxvalue')
    p_Plane_12_1_Axis_width = '1'
    if self.hasInputFromPort('p_Plane_12_1_Axis_width') :
      p_Plane_12_1_Axis_width = self.getInputFromPort('p_Plane_12_1_Axis_width')
    p_Plane_12_1_Axis_tickangle = '0'
    if self.hasInputFromPort('p_Plane_12_1_Axis_tickangle') :
      p_Plane_12_1_Axis_tickangle = self.getInputFromPort('p_Plane_12_1_Axis_tickangle')
    p_Plane_12_1_Axis_ticktilt = '0'
    if self.hasInputFromPort('p_Plane_12_1_Axis_ticktilt') :
      p_Plane_12_1_Axis_ticktilt = self.getInputFromPort('p_Plane_12_1_Axis_ticktilt')
    p_Plane_12_1_Axis_ticksize = '5'
    if self.hasInputFromPort('p_Plane_12_1_Axis_ticksize') :
      p_Plane_12_1_Axis_ticksize = self.getInputFromPort('p_Plane_12_1_Axis_ticksize')
    p_Plane_12_1_Axis_labelangle = '0'
    if self.hasInputFromPort('p_Plane_12_1_Axis_labelangle') :
      p_Plane_12_1_Axis_labelangle = self.getInputFromPort('p_Plane_12_1_Axis_labelangle')
    p_Plane_12_1_Axis_labelheight = '6'
    if self.hasInputFromPort('p_Plane_12_1_Axis_labelheight') :
      p_Plane_12_1_Axis_labelheight = self.getInputFromPort('p_Plane_12_1_Axis_labelheight')
    p_Plane_12_1_Axis_valuesize = '3'
    if self.hasInputFromPort('p_Plane_12_1_Axis_valuesize') :
      p_Plane_12_1_Axis_valuesize = self.getInputFromPort('p_Plane_12_1_Axis_valuesize')
    p_Plane_12_1_Axis_valuesquash = '1.0'
    if self.hasInputFromPort('p_Plane_12_1_Axis_valuesquash') :
      p_Plane_12_1_Axis_valuesquash = self.getInputFromPort('p_Plane_12_1_Axis_valuesquash')
    p_Plane_12_2_Axis_absolute = ''
    if self.hasInputFromPort('p_Plane_12_2_Axis_absolute') :
      p_Plane_12_2_Axis_absolute = self.getInputFromPort('p_Plane_12_2_Axis_absolute')
    p_Plane_12_2_Axis_divisions = '10'
    if self.hasInputFromPort('p_Plane_12_2_Axis_divisions') :
      p_Plane_12_2_Axis_divisions = self.getInputFromPort('p_Plane_12_2_Axis_divisions')
    p_Plane_12_2_Axis_offset = '1'
    if self.hasInputFromPort('p_Plane_12_2_Axis_offset') :
      p_Plane_12_2_Axis_offset = self.getInputFromPort('p_Plane_12_2_Axis_offset')
    p_Plane_12_2_Axis_range_first = '0.0'
    if self.hasInputFromPort('p_Plane_12_2_Axis_range_first') :
      p_Plane_12_2_Axis_range_first = self.getInputFromPort('p_Plane_12_2_Axis_range_first')
    p_Plane_12_2_Axis_range_second = '1.0'
    if self.hasInputFromPort('p_Plane_12_2_Axis_range_second') :
      p_Plane_12_2_Axis_range_second = self.getInputFromPort('p_Plane_12_2_Axis_range_second')
    p_Plane_12_2_Axis_min_absolute = '0.0'
    if self.hasInputFromPort('p_Plane_12_2_Axis_min_absolute') :
      p_Plane_12_2_Axis_min_absolute = self.getInputFromPort('p_Plane_12_2_Axis_min_absolute')
    p_Plane_12_2_Axis_max_absolute = '1.0'
    if self.hasInputFromPort('p_Plane_12_2_Axis_max_absolute') :
      p_Plane_12_2_Axis_max_absolute = self.getInputFromPort('p_Plane_12_2_Axis_max_absolute')
    p_Plane_12_2_Axis_minplane = '2'
    if self.hasInputFromPort('p_Plane_12_2_Axis_minplane') :
      p_Plane_12_2_Axis_minplane = self.getInputFromPort('p_Plane_12_2_Axis_minplane')
    p_Plane_12_2_Axis_maxplane = '2'
    if self.hasInputFromPort('p_Plane_12_2_Axis_maxplane') :
      p_Plane_12_2_Axis_maxplane = self.getInputFromPort('p_Plane_12_2_Axis_maxplane')
    p_Plane_12_2_Axis_lines = '2'
    if self.hasInputFromPort('p_Plane_12_2_Axis_lines') :
      p_Plane_12_2_Axis_lines = self.getInputFromPort('p_Plane_12_2_Axis_lines')
    p_Plane_12_2_Axis_minticks = '2'
    if self.hasInputFromPort('p_Plane_12_2_Axis_minticks') :
      p_Plane_12_2_Axis_minticks = self.getInputFromPort('p_Plane_12_2_Axis_minticks')
    p_Plane_12_2_Axis_maxticks = '2'
    if self.hasInputFromPort('p_Plane_12_2_Axis_maxticks') :
      p_Plane_12_2_Axis_maxticks = self.getInputFromPort('p_Plane_12_2_Axis_maxticks')
    p_Plane_12_2_Axis_minlabel = '2'
    if self.hasInputFromPort('p_Plane_12_2_Axis_minlabel') :
      p_Plane_12_2_Axis_minlabel = self.getInputFromPort('p_Plane_12_2_Axis_minlabel')
    p_Plane_12_2_Axis_maxlabel = '2'
    if self.hasInputFromPort('p_Plane_12_2_Axis_maxlabel') :
      p_Plane_12_2_Axis_maxlabel = self.getInputFromPort('p_Plane_12_2_Axis_maxlabel')
    p_Plane_12_2_Axis_minvalue = '2'
    if self.hasInputFromPort('p_Plane_12_2_Axis_minvalue') :
      p_Plane_12_2_Axis_minvalue = self.getInputFromPort('p_Plane_12_2_Axis_minvalue')
    p_Plane_12_2_Axis_maxvalue = '2'
    if self.hasInputFromPort('p_Plane_12_2_Axis_maxvalue') :
      p_Plane_12_2_Axis_maxvalue = self.getInputFromPort('p_Plane_12_2_Axis_maxvalue')
    p_Plane_12_2_Axis_width = '1'
    if self.hasInputFromPort('p_Plane_12_2_Axis_width') :
      p_Plane_12_2_Axis_width = self.getInputFromPort('p_Plane_12_2_Axis_width')
    p_Plane_12_2_Axis_tickangle = '0'
    if self.hasInputFromPort('p_Plane_12_2_Axis_tickangle') :
      p_Plane_12_2_Axis_tickangle = self.getInputFromPort('p_Plane_12_2_Axis_tickangle')
    p_Plane_12_2_Axis_ticktilt = '0'
    if self.hasInputFromPort('p_Plane_12_2_Axis_ticktilt') :
      p_Plane_12_2_Axis_ticktilt = self.getInputFromPort('p_Plane_12_2_Axis_ticktilt')
    p_Plane_12_2_Axis_ticksize = '5'
    if self.hasInputFromPort('p_Plane_12_2_Axis_ticksize') :
      p_Plane_12_2_Axis_ticksize = self.getInputFromPort('p_Plane_12_2_Axis_ticksize')
    p_Plane_12_2_Axis_labelangle = '0'
    if self.hasInputFromPort('p_Plane_12_2_Axis_labelangle') :
      p_Plane_12_2_Axis_labelangle = self.getInputFromPort('p_Plane_12_2_Axis_labelangle')
    p_Plane_12_2_Axis_labelheight = '6'
    if self.hasInputFromPort('p_Plane_12_2_Axis_labelheight') :
      p_Plane_12_2_Axis_labelheight = self.getInputFromPort('p_Plane_12_2_Axis_labelheight')
    p_Plane_12_2_Axis_valuesize = '3'
    if self.hasInputFromPort('p_Plane_12_2_Axis_valuesize') :
      p_Plane_12_2_Axis_valuesize = self.getInputFromPort('p_Plane_12_2_Axis_valuesize')
    p_Plane_12_2_Axis_valuesquash = '1.0'
    if self.hasInputFromPort('p_Plane_12_2_Axis_valuesquash') :
      p_Plane_12_2_Axis_valuesquash = self.getInputFromPort('p_Plane_12_2_Axis_valuesquash')
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    results = sr_py.CreateViewerAxes(Field,p_precision,p_squash,p_valuerez,p_labelrez,p_Plane_01_0_Axis_absolute,p_Plane_01_0_Axis_divisions,p_Plane_01_0_Axis_offset,p_Plane_01_0_Axis_range_first,p_Plane_01_0_Axis_range_second,p_Plane_01_0_Axis_min_absolute,p_Plane_01_0_Axis_max_absolute,p_Plane_01_0_Axis_minplane,p_Plane_01_0_Axis_maxplane,p_Plane_01_0_Axis_lines,p_Plane_01_0_Axis_minticks,p_Plane_01_0_Axis_maxticks,p_Plane_01_0_Axis_minlabel,p_Plane_01_0_Axis_maxlabel,p_Plane_01_0_Axis_minvalue,p_Plane_01_0_Axis_maxvalue,p_Plane_01_0_Axis_width,p_Plane_01_0_Axis_tickangle,p_Plane_01_0_Axis_ticktilt,p_Plane_01_0_Axis_ticksize,p_Plane_01_0_Axis_labelangle,p_Plane_01_0_Axis_labelheight,p_Plane_01_0_Axis_valuesize,p_Plane_01_0_Axis_valuesquash,p_Plane_01_1_Axis_absolute,p_Plane_01_1_Axis_divisions,p_Plane_01_1_Axis_offset,p_Plane_01_1_Axis_range_first,p_Plane_01_1_Axis_range_second,p_Plane_01_1_Axis_min_absolute,p_Plane_01_1_Axis_max_absolute,p_Plane_01_1_Axis_minplane,p_Plane_01_1_Axis_maxplane,p_Plane_01_1_Axis_lines,p_Plane_01_1_Axis_minticks,p_Plane_01_1_Axis_maxticks,p_Plane_01_1_Axis_minlabel,p_Plane_01_1_Axis_maxlabel,p_Plane_01_1_Axis_minvalue,p_Plane_01_1_Axis_maxvalue,p_Plane_01_1_Axis_width,p_Plane_01_1_Axis_tickangle,p_Plane_01_1_Axis_ticktilt,p_Plane_01_1_Axis_ticksize,p_Plane_01_1_Axis_labelangle,p_Plane_01_1_Axis_labelheight,p_Plane_01_1_Axis_valuesize,p_Plane_01_1_Axis_valuesquash,p_Plane_02_0_Axis_absolute,p_Plane_02_0_Axis_divisions,p_Plane_02_0_Axis_offset,p_Plane_02_0_Axis_range_first,p_Plane_02_0_Axis_range_second,p_Plane_02_0_Axis_min_absolute,p_Plane_02_0_Axis_max_absolute,p_Plane_02_0_Axis_minplane,p_Plane_02_0_Axis_maxplane,p_Plane_02_0_Axis_lines,p_Plane_02_0_Axis_minticks,p_Plane_02_0_Axis_maxticks,p_Plane_02_0_Axis_minlabel,p_Plane_02_0_Axis_maxlabel,p_Plane_02_0_Axis_minvalue,p_Plane_02_0_Axis_maxvalue,p_Plane_02_0_Axis_width,p_Plane_02_0_Axis_tickangle,p_Plane_02_0_Axis_ticktilt,p_Plane_02_0_Axis_ticksize,p_Plane_02_0_Axis_labelangle,p_Plane_02_0_Axis_labelheight,p_Plane_02_0_Axis_valuesize,p_Plane_02_0_Axis_valuesquash,p_Plane_02_2_Axis_absolute,p_Plane_02_2_Axis_divisions,p_Plane_02_2_Axis_offset,p_Plane_02_2_Axis_range_first,p_Plane_02_2_Axis_range_second,p_Plane_02_2_Axis_min_absolute,p_Plane_02_2_Axis_max_absolute,p_Plane_02_2_Axis_minplane,p_Plane_02_2_Axis_maxplane,p_Plane_02_2_Axis_lines,p_Plane_02_2_Axis_minticks,p_Plane_02_2_Axis_maxticks,p_Plane_02_2_Axis_minlabel,p_Plane_02_2_Axis_maxlabel,p_Plane_02_2_Axis_minvalue,p_Plane_02_2_Axis_maxvalue,p_Plane_02_2_Axis_width,p_Plane_02_2_Axis_tickangle,p_Plane_02_2_Axis_ticktilt,p_Plane_02_2_Axis_ticksize,p_Plane_02_2_Axis_labelangle,p_Plane_02_2_Axis_labelheight,p_Plane_02_2_Axis_valuesize,p_Plane_02_2_Axis_valuesquash,p_Plane_12_1_Axis_absolute,p_Plane_12_1_Axis_divisions,p_Plane_12_1_Axis_offset,p_Plane_12_1_Axis_range_first,p_Plane_12_1_Axis_range_second,p_Plane_12_1_Axis_min_absolute,p_Plane_12_1_Axis_max_absolute,p_Plane_12_1_Axis_minplane,p_Plane_12_1_Axis_maxplane,p_Plane_12_1_Axis_lines,p_Plane_12_1_Axis_minticks,p_Plane_12_1_Axis_maxticks,p_Plane_12_1_Axis_minlabel,p_Plane_12_1_Axis_maxlabel,p_Plane_12_1_Axis_minvalue,p_Plane_12_1_Axis_maxvalue,p_Plane_12_1_Axis_width,p_Plane_12_1_Axis_tickangle,p_Plane_12_1_Axis_ticktilt,p_Plane_12_1_Axis_ticksize,p_Plane_12_1_Axis_labelangle,p_Plane_12_1_Axis_labelheight,p_Plane_12_1_Axis_valuesize,p_Plane_12_1_Axis_valuesquash,p_Plane_12_2_Axis_absolute,p_Plane_12_2_Axis_divisions,p_Plane_12_2_Axis_offset,p_Plane_12_2_Axis_range_first,p_Plane_12_2_Axis_range_second,p_Plane_12_2_Axis_min_absolute,p_Plane_12_2_Axis_max_absolute,p_Plane_12_2_Axis_minplane,p_Plane_12_2_Axis_maxplane,p_Plane_12_2_Axis_lines,p_Plane_12_2_Axis_minticks,p_Plane_12_2_Axis_maxticks,p_Plane_12_2_Axis_minlabel,p_Plane_12_2_Axis_maxlabel,p_Plane_12_2_Axis_minvalue,p_Plane_12_2_Axis_maxvalue,p_Plane_12_2_Axis_width,p_Plane_12_2_Axis_tickangle,p_Plane_12_2_Axis_ticktilt,p_Plane_12_2_Axis_ticksize,p_Plane_12_2_Axis_labelangle,p_Plane_12_2_Axis_labelheight,p_Plane_12_2_Axis_valuesize,p_Plane_12_2_Axis_valuesquash)
    self.setResult('Axes', results)

class scirun_SelectFieldROIWithBoxWidget(Module) :
  def compute(self) :
    p_stampvalue = 100
    if self.hasInputFromPort('p_stampvalue') :
      p_stampvalue = self.getInputFromPort('p_stampvalue')
    p_runmode = 0
    if self.hasInputFromPort('p_runmode') :
      p_runmode = self.getInputFromPort('p_runmode')
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    results = sr_py.SelectFieldROIWithBoxWidget(Input_Field,p_stampvalue,p_runmode)
    self.setResult('Selection Widget', results[0])
    self.setResult('Output Field', results[1])

class scirun_SetTetVolFieldDataValues(Module) :
  def compute(self) :
    p_newval = 1.0
    if self.hasInputFromPort('p_newval') :
      p_newval = self.getInputFromPort('p_newval')
    InField = 0
    if self.hasInputFromPort('InField') :
      InField = self.getInputFromPort('InField')
    results = sr_py.SetTetVolFieldDataValues(InField,p_newval)
    self.setResult('OutField', results)

class scirun_WritePath(Module) :
  def compute(self) :
    p_filetype = 'Binary'
    if self.hasInputFromPort('p_filetype') :
      p_filetype = self.getInputFromPort('p_filetype')
    p_confirm = '0'
    if self.hasInputFromPort('p_confirm') :
      p_confirm = self.getInputFromPort('p_confirm')
    p_confirm_once = '0'
    if self.hasInputFromPort('p_confirm_once') :
      p_confirm_once = self.getInputFromPort('p_confirm_once')
    Input_Data = 0
    if self.hasInputFromPort('Input Data') :
      Input_Data = self.getInputFromPort('Input Data')
    Filename = ''
    if self.hasInputFromPort('Filename') :
      Filename = self.getInputFromPort('Filename')
    results = sr_py.WritePath(Input_Data,Filename,p_filetype,p_confirm,p_confirm_once)

class scirun_ClipLatVolByIndicesOrWidget(Module) :
  def compute(self) :
    p_use_text_bbox = 0
    if self.hasInputFromPort('p_use_text_bbox') :
      p_use_text_bbox = self.getInputFromPort('p_use_text_bbox')
    p_text_min_x = 0.0
    if self.hasInputFromPort('p_text_min_x') :
      p_text_min_x = self.getInputFromPort('p_text_min_x')
    p_text_min_y = 0.0
    if self.hasInputFromPort('p_text_min_y') :
      p_text_min_y = self.getInputFromPort('p_text_min_y')
    p_text_min_z = 0.0
    if self.hasInputFromPort('p_text_min_z') :
      p_text_min_z = self.getInputFromPort('p_text_min_z')
    p_text_max_x = 1.0
    if self.hasInputFromPort('p_text_max_x') :
      p_text_max_x = self.getInputFromPort('p_text_max_x')
    p_text_max_y = 1.0
    if self.hasInputFromPort('p_text_max_y') :
      p_text_max_y = self.getInputFromPort('p_text_max_y')
    p_text_max_z = 1.0
    if self.hasInputFromPort('p_text_max_z') :
      p_text_max_z = self.getInputFromPort('p_text_max_z')
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    results = sr_py.ClipLatVolByIndicesOrWidget(Input_Field,p_use_text_bbox,p_text_min_x,p_text_min_y,p_text_min_z,p_text_max_x,p_text_max_y,p_text_max_z)
    self.setResult('Selection Widget', results[0])
    self.setResult('Output Field', results[1])
    self.setResult('MaskVector', results[2])

class scirun_GetBundlesFromBundle(Module) :
  def compute(self) :
    p_bundle1_name = 'bundle1'
    if self.hasInputFromPort('p_bundle1_name') :
      p_bundle1_name = self.getInputFromPort('p_bundle1_name')
    p_bundle2_name = 'bundle2'
    if self.hasInputFromPort('p_bundle2_name') :
      p_bundle2_name = self.getInputFromPort('p_bundle2_name')
    p_bundle3_name = 'bundle3'
    if self.hasInputFromPort('p_bundle3_name') :
      p_bundle3_name = self.getInputFromPort('p_bundle3_name')
    p_bundle4_name = 'bundle4'
    if self.hasInputFromPort('p_bundle4_name') :
      p_bundle4_name = self.getInputFromPort('p_bundle4_name')
    p_bundle5_name = 'bundle5'
    if self.hasInputFromPort('p_bundle5_name') :
      p_bundle5_name = self.getInputFromPort('p_bundle5_name')
    p_bundle6_name = 'bundle6'
    if self.hasInputFromPort('p_bundle6_name') :
      p_bundle6_name = self.getInputFromPort('p_bundle6_name')
    p_bundle_selection = ''
    if self.hasInputFromPort('p_bundle_selection') :
      p_bundle_selection = self.getInputFromPort('p_bundle_selection')
    bundle = 0
    if self.hasInputFromPort('bundle') :
      bundle = self.getInputFromPort('bundle')
    results = sr_py.GetBundlesFromBundle(bundle,p_bundle1_name,p_bundle2_name,p_bundle3_name,p_bundle4_name,p_bundle5_name,p_bundle6_name,p_bundle_selection)
    self.setResult('bundle', results[0])
    self.setResult('bundle1', results[1])
    self.setResult('bundle2', results[2])
    self.setResult('bundle3', results[3])
    self.setResult('bundle4', results[4])
    self.setResult('bundle5', results[5])
    self.setResult('bundle6', results[6])

class scirun_RescaleColorMap(Module) :
  def compute(self) :
    p_main_frame = ''
    if self.hasInputFromPort('p_main_frame') :
      p_main_frame = self.getInputFromPort('p_main_frame')
    p_isFixed = 0
    if self.hasInputFromPort('p_isFixed') :
      p_isFixed = self.getInputFromPort('p_isFixed')
    p_min = 0.0
    if self.hasInputFromPort('p_min') :
      p_min = self.getInputFromPort('p_min')
    p_max = 1.0
    if self.hasInputFromPort('p_max') :
      p_max = self.getInputFromPort('p_max')
    p_makeSymmetric = 0
    if self.hasInputFromPort('p_makeSymmetric') :
      p_makeSymmetric = self.getInputFromPort('p_makeSymmetric')
    ColorMap = 0
    if self.hasInputFromPort('ColorMap') :
      ColorMap = self.getInputFromPort('ColorMap')
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    results = sr_py.RescaleColorMap(ColorMap,Field,p_main_frame,p_isFixed,p_min,p_max,p_makeSymmetric)
    self.setResult('ColorMap', results)

class scirun_ConvertNrrdsToTexture(Module) :
  def compute(self) :
    p_vmin = 0.0
    if self.hasInputFromPort('p_vmin') :
      p_vmin = self.getInputFromPort('p_vmin')
    p_vmax = 1.0
    if self.hasInputFromPort('p_vmax') :
      p_vmax = self.getInputFromPort('p_vmax')
    p_gmin = 0.0
    if self.hasInputFromPort('p_gmin') :
      p_gmin = self.getInputFromPort('p_gmin')
    p_gmax = 1.0
    if self.hasInputFromPort('p_gmax') :
      p_gmax = self.getInputFromPort('p_gmax')
    p_mmin = 0.0
    if self.hasInputFromPort('p_mmin') :
      p_mmin = self.getInputFromPort('p_mmin')
    p_mmax = 1.0
    if self.hasInputFromPort('p_mmax') :
      p_mmax = self.getInputFromPort('p_mmax')
    p_is_fixed = 0
    if self.hasInputFromPort('p_is_fixed') :
      p_is_fixed = self.getInputFromPort('p_is_fixed')
    p_card_mem = 16
    if self.hasInputFromPort('p_card_mem') :
      p_card_mem = self.getInputFromPort('p_card_mem')
    p_card_mem_auto = 1
    if self.hasInputFromPort('p_card_mem_auto') :
      p_card_mem_auto = self.getInputFromPort('p_card_mem_auto')
    p_is_uchar = 1
    if self.hasInputFromPort('p_is_uchar') :
      p_is_uchar = self.getInputFromPort('p_is_uchar')
    p_histogram = 1
    if self.hasInputFromPort('p_histogram') :
      p_histogram = self.getInputFromPort('p_histogram')
    p_gamma = 0.5
    if self.hasInputFromPort('p_gamma') :
      p_gamma = self.getInputFromPort('p_gamma')
    Value_Nrrd = 0
    if self.hasInputFromPort('Value Nrrd') :
      Value_Nrrd = self.getInputFromPort('Value Nrrd')
    Gradient_Magnitude_Nrrd = 0
    if self.hasInputFromPort('Gradient Magnitude Nrrd') :
      Gradient_Magnitude_Nrrd = self.getInputFromPort('Gradient Magnitude Nrrd')
    results = sr_py.ConvertNrrdsToTexture(Value_Nrrd,Gradient_Magnitude_Nrrd,p_vmin,p_vmax,p_gmin,p_gmax,p_mmin,p_mmax,p_is_fixed,p_card_mem,p_card_mem_auto,p_is_uchar,p_histogram,p_gamma)
    self.setResult('Texture', results[0])
    self.setResult('JointHistoGram', results[1])

class scirun_ConvertQuadSurfToTriSurf(Module) :
  def compute(self) :
    QuadSurf = 0
    if self.hasInputFromPort('QuadSurf') :
      QuadSurf = self.getInputFromPort('QuadSurf')
    results = sr_py.ConvertQuadSurfToTriSurf(QuadSurf)
    self.setResult('TriSurf', results)

class scirun_WriteColorMap2D(Module) :
  def compute(self) :
    p_filetype = 'Binary'
    if self.hasInputFromPort('p_filetype') :
      p_filetype = self.getInputFromPort('p_filetype')
    p_confirm = '0'
    if self.hasInputFromPort('p_confirm') :
      p_confirm = self.getInputFromPort('p_confirm')
    p_confirm_once = '0'
    if self.hasInputFromPort('p_confirm_once') :
      p_confirm_once = self.getInputFromPort('p_confirm_once')
    p_exporttype = ''
    if self.hasInputFromPort('p_exporttype') :
      p_exporttype = self.getInputFromPort('p_exporttype')
    Input_Data = 0
    if self.hasInputFromPort('Input Data') :
      Input_Data = self.getInputFromPort('Input Data')
    Filename = ''
    if self.hasInputFromPort('Filename') :
      Filename = self.getInputFromPort('Filename')
    results = sr_py.WriteColorMap2D(Input_Data,Filename,p_filetype,p_confirm,p_confirm_once,p_exporttype)

class scirun_BuildMatrixOfSurfaceNormals(Module) :
  def compute(self) :
    Surface_Field = 0
    if self.hasInputFromPort('Surface Field') :
      Surface_Field = self.getInputFromPort('Surface Field')
    results = sr_py.BuildMatrixOfSurfaceNormals(Surface_Field)
    self.setResult('Nodal Surface Normals', results)

class scirun_ReadHDF5File(Module) :
  def compute(self) :
    p_have_HDF5 = 0
    if self.hasInputFromPort('p_have_HDF5') :
      p_have_HDF5 = self.getInputFromPort('p_have_HDF5')
    p_power_app = 0
    if self.hasInputFromPort('p_power_app') :
      p_power_app = self.getInputFromPort('p_power_app')
    p_datasets = ''
    if self.hasInputFromPort('p_datasets') :
      p_datasets = self.getInputFromPort('p_datasets')
    p_dumpname = ''
    if self.hasInputFromPort('p_dumpname') :
      p_dumpname = self.getInputFromPort('p_dumpname')
    p_ports = ''
    if self.hasInputFromPort('p_ports') :
      p_ports = self.getInputFromPort('p_ports')
    p_ndims = 0
    if self.hasInputFromPort('p_ndims') :
      p_ndims = self.getInputFromPort('p_ndims')
    p_mergeData = 1
    if self.hasInputFromPort('p_mergeData') :
      p_mergeData = self.getInputFromPort('p_mergeData')
    p_assumeSVT = 1
    if self.hasInputFromPort('p_assumeSVT') :
      p_assumeSVT = self.getInputFromPort('p_assumeSVT')
    p_animate = 0
    if self.hasInputFromPort('p_animate') :
      p_animate = self.getInputFromPort('p_animate')
    p_animate_tab = ''
    if self.hasInputFromPort('p_animate_tab') :
      p_animate_tab = self.getInputFromPort('p_animate_tab')
    p_basic_tab = ''
    if self.hasInputFromPort('p_basic_tab') :
      p_basic_tab = self.getInputFromPort('p_basic_tab')
    p_extended_tab = ''
    if self.hasInputFromPort('p_extended_tab') :
      p_extended_tab = self.getInputFromPort('p_extended_tab')
    p_playmode_tab = ''
    if self.hasInputFromPort('p_playmode_tab') :
      p_playmode_tab = self.getInputFromPort('p_playmode_tab')
    p_selectable_min = 0
    if self.hasInputFromPort('p_selectable_min') :
      p_selectable_min = self.getInputFromPort('p_selectable_min')
    p_selectable_max = 100
    if self.hasInputFromPort('p_selectable_max') :
      p_selectable_max = self.getInputFromPort('p_selectable_max')
    p_selectable_inc = 1
    if self.hasInputFromPort('p_selectable_inc') :
      p_selectable_inc = self.getInputFromPort('p_selectable_inc')
    p_range_min = 0
    if self.hasInputFromPort('p_range_min') :
      p_range_min = self.getInputFromPort('p_range_min')
    p_range_max = 0
    if self.hasInputFromPort('p_range_max') :
      p_range_max = self.getInputFromPort('p_range_max')
    p_playmode = 'once'
    if self.hasInputFromPort('p_playmode') :
      p_playmode = self.getInputFromPort('p_playmode')
    p_current = 0
    if self.hasInputFromPort('p_current') :
      p_current = self.getInputFromPort('p_current')
    p_execmode = 'init'
    if self.hasInputFromPort('p_execmode') :
      p_execmode = self.getInputFromPort('p_execmode')
    p_delay = 0
    if self.hasInputFromPort('p_delay') :
      p_delay = self.getInputFromPort('p_delay')
    p_inc_amount = 1
    if self.hasInputFromPort('p_inc_amount') :
      p_inc_amount = self.getInputFromPort('p_inc_amount')
    p_update_type = 'On Release'
    if self.hasInputFromPort('p_update_type') :
      p_update_type = self.getInputFromPort('p_update_type')
    p_have_group = 0
    if self.hasInputFromPort('p_have_group') :
      p_have_group = self.getInputFromPort('p_have_group')
    p_have_attributes = 0
    if self.hasInputFromPort('p_have_attributes') :
      p_have_attributes = self.getInputFromPort('p_have_attributes')
    p_have_datasets = 0
    if self.hasInputFromPort('p_have_datasets') :
      p_have_datasets = self.getInputFromPort('p_have_datasets')
    p_continuous = 0
    if self.hasInputFromPort('p_continuous') :
      p_continuous = self.getInputFromPort('p_continuous')
    p_selectionString = ''
    if self.hasInputFromPort('p_selectionString') :
      p_selectionString = self.getInputFromPort('p_selectionString')
    p_regexp = 0
    if self.hasInputFromPort('p_regexp') :
      p_regexp = self.getInputFromPort('p_regexp')
    p_allow_selection = 'true'
    if self.hasInputFromPort('p_allow_selection') :
      p_allow_selection = self.getInputFromPort('p_allow_selection')
    p_read_error = 0
    if self.hasInputFromPort('p_read_error') :
      p_read_error = self.getInputFromPort('p_read_error')
    p_max_dims = 6
    if self.hasInputFromPort('p_max_dims') :
      p_max_dims = self.getInputFromPort('p_max_dims')
    p_0_dim = '2'
    if self.hasInputFromPort('p_0_dim') :
      p_0_dim = self.getInputFromPort('p_0_dim')
    p_0_start = '0'
    if self.hasInputFromPort('p_0_start') :
      p_0_start = self.getInputFromPort('p_0_start')
    p_0_start2 = '0'
    if self.hasInputFromPort('p_0_start2') :
      p_0_start2 = self.getInputFromPort('p_0_start2')
    p_0_count = '1'
    if self.hasInputFromPort('p_0_count') :
      p_0_count = self.getInputFromPort('p_0_count')
    p_0_count2 = '1'
    if self.hasInputFromPort('p_0_count2') :
      p_0_count2 = self.getInputFromPort('p_0_count2')
    p_0_stride = '1'
    if self.hasInputFromPort('p_0_stride') :
      p_0_stride = self.getInputFromPort('p_0_stride')
    p_0_stride2 = '1'
    if self.hasInputFromPort('p_0_stride2') :
      p_0_stride2 = self.getInputFromPort('p_0_stride2')
    p_1_dim = '2'
    if self.hasInputFromPort('p_1_dim') :
      p_1_dim = self.getInputFromPort('p_1_dim')
    p_1_start = '0'
    if self.hasInputFromPort('p_1_start') :
      p_1_start = self.getInputFromPort('p_1_start')
    p_1_start2 = '0'
    if self.hasInputFromPort('p_1_start2') :
      p_1_start2 = self.getInputFromPort('p_1_start2')
    p_1_count = '1'
    if self.hasInputFromPort('p_1_count') :
      p_1_count = self.getInputFromPort('p_1_count')
    p_1_count2 = '1'
    if self.hasInputFromPort('p_1_count2') :
      p_1_count2 = self.getInputFromPort('p_1_count2')
    p_1_stride = '1'
    if self.hasInputFromPort('p_1_stride') :
      p_1_stride = self.getInputFromPort('p_1_stride')
    p_1_stride2 = '1'
    if self.hasInputFromPort('p_1_stride2') :
      p_1_stride2 = self.getInputFromPort('p_1_stride2')
    p_2_dim = '2'
    if self.hasInputFromPort('p_2_dim') :
      p_2_dim = self.getInputFromPort('p_2_dim')
    p_2_start = '0'
    if self.hasInputFromPort('p_2_start') :
      p_2_start = self.getInputFromPort('p_2_start')
    p_2_start2 = '0'
    if self.hasInputFromPort('p_2_start2') :
      p_2_start2 = self.getInputFromPort('p_2_start2')
    p_2_count = '1'
    if self.hasInputFromPort('p_2_count') :
      p_2_count = self.getInputFromPort('p_2_count')
    p_2_count2 = '1'
    if self.hasInputFromPort('p_2_count2') :
      p_2_count2 = self.getInputFromPort('p_2_count2')
    p_2_stride = '1'
    if self.hasInputFromPort('p_2_stride') :
      p_2_stride = self.getInputFromPort('p_2_stride')
    p_2_stride2 = '1'
    if self.hasInputFromPort('p_2_stride2') :
      p_2_stride2 = self.getInputFromPort('p_2_stride2')
    p_3_dim = '2'
    if self.hasInputFromPort('p_3_dim') :
      p_3_dim = self.getInputFromPort('p_3_dim')
    p_3_start = '0'
    if self.hasInputFromPort('p_3_start') :
      p_3_start = self.getInputFromPort('p_3_start')
    p_3_start2 = '0'
    if self.hasInputFromPort('p_3_start2') :
      p_3_start2 = self.getInputFromPort('p_3_start2')
    p_3_count = '1'
    if self.hasInputFromPort('p_3_count') :
      p_3_count = self.getInputFromPort('p_3_count')
    p_3_count2 = '1'
    if self.hasInputFromPort('p_3_count2') :
      p_3_count2 = self.getInputFromPort('p_3_count2')
    p_3_stride = '1'
    if self.hasInputFromPort('p_3_stride') :
      p_3_stride = self.getInputFromPort('p_3_stride')
    p_3_stride2 = '1'
    if self.hasInputFromPort('p_3_stride2') :
      p_3_stride2 = self.getInputFromPort('p_3_stride2')
    p_4_dim = '2'
    if self.hasInputFromPort('p_4_dim') :
      p_4_dim = self.getInputFromPort('p_4_dim')
    p_4_start = '0'
    if self.hasInputFromPort('p_4_start') :
      p_4_start = self.getInputFromPort('p_4_start')
    p_4_start2 = '0'
    if self.hasInputFromPort('p_4_start2') :
      p_4_start2 = self.getInputFromPort('p_4_start2')
    p_4_count = '1'
    if self.hasInputFromPort('p_4_count') :
      p_4_count = self.getInputFromPort('p_4_count')
    p_4_count2 = '1'
    if self.hasInputFromPort('p_4_count2') :
      p_4_count2 = self.getInputFromPort('p_4_count2')
    p_4_stride = '1'
    if self.hasInputFromPort('p_4_stride') :
      p_4_stride = self.getInputFromPort('p_4_stride')
    p_4_stride2 = '1'
    if self.hasInputFromPort('p_4_stride2') :
      p_4_stride2 = self.getInputFromPort('p_4_stride2')
    p_5_dim = '2'
    if self.hasInputFromPort('p_5_dim') :
      p_5_dim = self.getInputFromPort('p_5_dim')
    p_5_start = '0'
    if self.hasInputFromPort('p_5_start') :
      p_5_start = self.getInputFromPort('p_5_start')
    p_5_start2 = '0'
    if self.hasInputFromPort('p_5_start2') :
      p_5_start2 = self.getInputFromPort('p_5_start2')
    p_5_count = '1'
    if self.hasInputFromPort('p_5_count') :
      p_5_count = self.getInputFromPort('p_5_count')
    p_5_count2 = '1'
    if self.hasInputFromPort('p_5_count2') :
      p_5_count2 = self.getInputFromPort('p_5_count2')
    p_5_stride = '1'
    if self.hasInputFromPort('p_5_stride') :
      p_5_stride = self.getInputFromPort('p_5_stride')
    p_5_stride2 = '1'
    if self.hasInputFromPort('p_5_stride2') :
      p_5_stride2 = self.getInputFromPort('p_5_stride2')
    Full_filename = ''
    if self.hasInputFromPort('Full filename') :
      Full_filename = self.getInputFromPort('Full filename')
    Current_Index = 0
    if self.hasInputFromPort('Current Index') :
      Current_Index = self.getInputFromPort('Current Index')
    results = sr_py.ReadHDF5File(Full_filename,Current_Index,p_have_HDF5,p_power_app,p_datasets,p_dumpname,p_ports,p_ndims,p_mergeData,p_assumeSVT,p_animate,p_animate_tab,p_basic_tab,p_extended_tab,p_playmode_tab,p_selectable_min,p_selectable_max,p_selectable_inc,p_range_min,p_range_max,p_playmode,p_current,p_execmode,p_delay,p_inc_amount,p_update_type,p_have_group,p_have_attributes,p_have_datasets,p_continuous,p_selectionString,p_regexp,p_allow_selection,p_read_error,p_max_dims,p_0_dim,p_0_start,p_0_start2,p_0_count,p_0_count2,p_0_stride,p_0_stride2,p_1_dim,p_1_start,p_1_start2,p_1_count,p_1_count2,p_1_stride,p_1_stride2,p_2_dim,p_2_start,p_2_start2,p_2_count,p_2_count2,p_2_stride,p_2_stride2,p_3_dim,p_3_start,p_3_start2,p_3_count,p_3_count2,p_3_stride,p_3_stride2,p_4_dim,p_4_start,p_4_start2,p_4_count,p_4_count2,p_4_stride,p_4_stride2,p_5_dim,p_5_start,p_5_start2,p_5_count,p_5_count2,p_5_stride,p_5_stride2)
    self.setResult('Output 0 Nrrd', results[0])
    self.setResult('Output 1 Nrrd', results[1])
    self.setResult('Output 2 Nrrd', results[2])
    self.setResult('Output 3 Nrrd', results[3])
    self.setResult('Output 4 Nrrd', results[4])
    self.setResult('Output 5 Nrrd', results[5])
    self.setResult('Output 6 Nrrd', results[6])
    self.setResult('Output 7 Nrrd', results[7])
    self.setResult('Selected Index', results[8])

class scirun_SwapFieldDataWithMatrixEntries(Module) :
  def compute(self) :
    p_preserve_scalar_type = 0
    if self.hasInputFromPort('p_preserve_scalar_type') :
      p_preserve_scalar_type = self.getInputFromPort('p_preserve_scalar_type')
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    Input_Matrix = 0
    if self.hasInputFromPort('Input Matrix') :
      Input_Matrix = self.getInputFromPort('Input Matrix')
    results = sr_py.SwapFieldDataWithMatrixEntries(Input_Field,Input_Matrix,p_preserve_scalar_type)
    self.setResult('Output Field', results[0])
    self.setResult('Output Matrix', results[1])

class scirun_GetFieldBoundary(Module) :
  def compute(self) :
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    results = sr_py.GetFieldBoundary(Field)
    self.setResult('BoundaryField', results[0])
    self.setResult('Mapping', results[1])

class scirun_ConvertMatricesToMesh(Module) :
  def compute(self) :
    p_fieldname = 'Created Field'
    if self.hasInputFromPort('p_fieldname') :
      p_fieldname = self.getInputFromPort('p_fieldname')
    p_meshname = 'Created Mesh'
    if self.hasInputFromPort('p_meshname') :
      p_meshname = self.getInputFromPort('p_meshname')
    p_fieldbasetype = 'TetVolField'
    if self.hasInputFromPort('p_fieldbasetype') :
      p_fieldbasetype = self.getInputFromPort('p_fieldbasetype')
    p_datatype = 'double'
    if self.hasInputFromPort('p_datatype') :
      p_datatype = self.getInputFromPort('p_datatype')
    Mesh_Elements = 0
    if self.hasInputFromPort('Mesh Elements') :
      Mesh_Elements = self.getInputFromPort('Mesh Elements')
    Mesh_Positions = 0
    if self.hasInputFromPort('Mesh Positions') :
      Mesh_Positions = self.getInputFromPort('Mesh Positions')
    Mesh_Normals = 0
    if self.hasInputFromPort('Mesh Normals') :
      Mesh_Normals = self.getInputFromPort('Mesh Normals')
    results = sr_py.ConvertMatricesToMesh(Mesh_Elements,Mesh_Positions,Mesh_Normals,p_fieldname,p_meshname,p_fieldbasetype,p_datatype)
    self.setResult('Output Field', results)

class scirun_TransformMeshWithFunction(Module) :
  def compute(self) :
    p_function = 'result = (Point) (Vector(x,y,z) * Vector(1.0, 2.0, 3.0));'
    if self.hasInputFromPort('p_function') :
      p_function = self.getInputFromPort('p_function')
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    results = sr_py.TransformMeshWithFunction(Input_Field,p_function)
    self.setResult('Output Field', results)

class scirun_PrintHelloWorldToScreen(Module) :
  def compute(self) :
    results = sr_py.PrintHelloWorldToScreen()

class scirun_ReportFieldInfo(Module) :
  def compute(self) :
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    results = sr_py.ReportFieldInfo(Input_Field)
    self.setResult('NumNodes', results[0])
    self.setResult('NumElements', results[1])
    self.setResult('NumData', results[2])
    self.setResult('DataMin', results[3])
    self.setResult('DataMax', results[4])
    self.setResult('FieldSize', results[5])
    self.setResult('FieldCenter', results[6])
    self.setResult('Dimensions', results[7])

class scirun_ConvertLatVolDataFromElemToNode(Module) :
  def compute(self) :
    Elem_Field = 0
    if self.hasInputFromPort('Elem Field') :
      Elem_Field = self.getInputFromPort('Elem Field')
    results = sr_py.ConvertLatVolDataFromElemToNode(Elem_Field)
    self.setResult('Node Field', results)

class scirun_GetPathsFromBundle(Module) :
  def compute(self) :
    p_path1_name = 'path1'
    if self.hasInputFromPort('p_path1_name') :
      p_path1_name = self.getInputFromPort('p_path1_name')
    p_path2_name = 'path2'
    if self.hasInputFromPort('p_path2_name') :
      p_path2_name = self.getInputFromPort('p_path2_name')
    p_path3_name = 'path3'
    if self.hasInputFromPort('p_path3_name') :
      p_path3_name = self.getInputFromPort('p_path3_name')
    p_path4_name = 'path4'
    if self.hasInputFromPort('p_path4_name') :
      p_path4_name = self.getInputFromPort('p_path4_name')
    p_path5_name = 'path5'
    if self.hasInputFromPort('p_path5_name') :
      p_path5_name = self.getInputFromPort('p_path5_name')
    p_path6_name = 'path6'
    if self.hasInputFromPort('p_path6_name') :
      p_path6_name = self.getInputFromPort('p_path6_name')
    p_path_selection = ''
    if self.hasInputFromPort('p_path_selection') :
      p_path_selection = self.getInputFromPort('p_path_selection')
    bundle = 0
    if self.hasInputFromPort('bundle') :
      bundle = self.getInputFromPort('bundle')
    results = sr_py.GetPathsFromBundle(bundle,p_path1_name,p_path2_name,p_path3_name,p_path4_name,p_path5_name,p_path6_name,p_path_selection)
    self.setResult('bundle', results[0])
    self.setResult('path1', results[1])
    self.setResult('path2', results[2])
    self.setResult('path3', results[3])
    self.setResult('path4', results[4])
    self.setResult('path5', results[5])
    self.setResult('path6', results[6])

class scirun_CreateGeometricTransform(Module) :
  def compute(self) :
    p_rotate_x = 0
    if self.hasInputFromPort('p_rotate_x') :
      p_rotate_x = self.getInputFromPort('p_rotate_x')
    p_rotate_y = 0
    if self.hasInputFromPort('p_rotate_y') :
      p_rotate_y = self.getInputFromPort('p_rotate_y')
    p_rotate_z = 1
    if self.hasInputFromPort('p_rotate_z') :
      p_rotate_z = self.getInputFromPort('p_rotate_z')
    p_rotate_theta = 0
    if self.hasInputFromPort('p_rotate_theta') :
      p_rotate_theta = self.getInputFromPort('p_rotate_theta')
    p_translate_x = 0
    if self.hasInputFromPort('p_translate_x') :
      p_translate_x = self.getInputFromPort('p_translate_x')
    p_translate_y = 0
    if self.hasInputFromPort('p_translate_y') :
      p_translate_y = self.getInputFromPort('p_translate_y')
    p_translate_z = 0
    if self.hasInputFromPort('p_translate_z') :
      p_translate_z = self.getInputFromPort('p_translate_z')
    p_scale_uniform = 0
    if self.hasInputFromPort('p_scale_uniform') :
      p_scale_uniform = self.getInputFromPort('p_scale_uniform')
    p_scale_x = 0
    if self.hasInputFromPort('p_scale_x') :
      p_scale_x = self.getInputFromPort('p_scale_x')
    p_scale_y = 0
    if self.hasInputFromPort('p_scale_y') :
      p_scale_y = self.getInputFromPort('p_scale_y')
    p_scale_z = 0
    if self.hasInputFromPort('p_scale_z') :
      p_scale_z = self.getInputFromPort('p_scale_z')
    p_shear_plane_a = 0
    if self.hasInputFromPort('p_shear_plane_a') :
      p_shear_plane_a = self.getInputFromPort('p_shear_plane_a')
    p_shear_plane_b = 0
    if self.hasInputFromPort('p_shear_plane_b') :
      p_shear_plane_b = self.getInputFromPort('p_shear_plane_b')
    p_shear_plane_c = 1
    if self.hasInputFromPort('p_shear_plane_c') :
      p_shear_plane_c = self.getInputFromPort('p_shear_plane_c')
    p_widget_resizable = 1
    if self.hasInputFromPort('p_widget_resizable') :
      p_widget_resizable = self.getInputFromPort('p_widget_resizable')
    p_permute_x = 1
    if self.hasInputFromPort('p_permute_x') :
      p_permute_x = self.getInputFromPort('p_permute_x')
    p_permute_y = 2
    if self.hasInputFromPort('p_permute_y') :
      p_permute_y = self.getInputFromPort('p_permute_y')
    p_permute_z = 3
    if self.hasInputFromPort('p_permute_z') :
      p_permute_z = self.getInputFromPort('p_permute_z')
    p_pre_transform = 1
    if self.hasInputFromPort('p_pre_transform') :
      p_pre_transform = self.getInputFromPort('p_pre_transform')
    p_which_transform = 'translate'
    if self.hasInputFromPort('p_which_transform') :
      p_which_transform = self.getInputFromPort('p_which_transform')
    p_widget_scale = 1
    if self.hasInputFromPort('p_widget_scale') :
      p_widget_scale = self.getInputFromPort('p_widget_scale')
    p_ignoring_widget_changes = 1
    if self.hasInputFromPort('p_ignoring_widget_changes') :
      p_ignoring_widget_changes = self.getInputFromPort('p_ignoring_widget_changes')
    Matrix = 0
    if self.hasInputFromPort('Matrix') :
      Matrix = self.getInputFromPort('Matrix')
    results = sr_py.CreateGeometricTransform(Matrix,p_rotate_x,p_rotate_y,p_rotate_z,p_rotate_theta,p_translate_x,p_translate_y,p_translate_z,p_scale_uniform,p_scale_x,p_scale_y,p_scale_z,p_shear_plane_a,p_shear_plane_b,p_shear_plane_c,p_widget_resizable,p_permute_x,p_permute_y,p_permute_z,p_pre_transform,p_which_transform,p_widget_scale,p_ignoring_widget_changes)
    self.setResult('Matrix', results[0])
    self.setResult('Geometry', results[1])

class scirun_CalculateNodeNormals(Module) :
  def compute(self) :
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    Input_Point = 0
    if self.hasInputFromPort('Input Point') :
      Input_Point = self.getInputFromPort('Input Point')
    results = sr_py.CalculateNodeNormals(Input_Field,Input_Point)
    self.setResult('Output Field', results)

class scirun_ReportFieldGeometryMeasures(Module) :
  def compute(self) :
    p_simplexString = 'Node'
    if self.hasInputFromPort('p_simplexString') :
      p_simplexString = self.getInputFromPort('p_simplexString')
    p_xFlag = 1
    if self.hasInputFromPort('p_xFlag') :
      p_xFlag = self.getInputFromPort('p_xFlag')
    p_yFlag = 1
    if self.hasInputFromPort('p_yFlag') :
      p_yFlag = self.getInputFromPort('p_yFlag')
    p_zFlag = 1
    if self.hasInputFromPort('p_zFlag') :
      p_zFlag = self.getInputFromPort('p_zFlag')
    p_idxFlag = 0
    if self.hasInputFromPort('p_idxFlag') :
      p_idxFlag = self.getInputFromPort('p_idxFlag')
    p_sizeFlag = 0
    if self.hasInputFromPort('p_sizeFlag') :
      p_sizeFlag = self.getInputFromPort('p_sizeFlag')
    p_normalsFlag = 0
    if self.hasInputFromPort('p_normalsFlag') :
      p_normalsFlag = self.getInputFromPort('p_normalsFlag')
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    results = sr_py.ReportFieldGeometryMeasures(Input_Field,p_simplexString,p_xFlag,p_yFlag,p_zFlag,p_idxFlag,p_sizeFlag,p_normalsFlag)
    self.setResult('Output Measures Matrix', results)

class scirun_CalculateVectorMagnitudes(Module) :
  def compute(self) :
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    results = sr_py.CalculateVectorMagnitudes(Input_Field)
    self.setResult('Output CalculateVectorMagnitudes', results)

class scirun_GetInputField(Module) :
  def compute(self) :
    InField = 0
    if self.hasInputFromPort('InField') :
      InField = self.getInputFromPort('InField')
    results = sr_py.GetInputField(InField)

class scirun_ChooseMatrix(Module) :
  def compute(self) :
    p_use_first_valid = '1'
    if self.hasInputFromPort('p_use_first_valid') :
      p_use_first_valid = self.getInputFromPort('p_use_first_valid')
    p_port_valid_index = '0'
    if self.hasInputFromPort('p_port_valid_index') :
      p_port_valid_index = self.getInputFromPort('p_port_valid_index')
    p_port_selected_index = '0'
    if self.hasInputFromPort('p_port_selected_index') :
      p_port_selected_index = self.getInputFromPort('p_port_selected_index')
    Matrix = 0
    if self.hasInputFromPort('Matrix') :
      Matrix = self.getInputFromPort('Matrix')
    results = sr_py.ChooseMatrix(Matrix,p_use_first_valid,p_port_valid_index,p_port_selected_index)
    self.setResult('Matrix', results)

class scirun_ClipFieldToFieldOrWidget(Module) :
  def compute(self) :
    p_clip_location = 'cell'
    if self.hasInputFromPort('p_clip_location') :
      p_clip_location = self.getInputFromPort('p_clip_location')
    p_clipmode = 'replace'
    if self.hasInputFromPort('p_clipmode') :
      p_clipmode = self.getInputFromPort('p_clipmode')
    p_autoexecute = 0
    if self.hasInputFromPort('p_autoexecute') :
      p_autoexecute = self.getInputFromPort('p_autoexecute')
    p_autoinvert = 0
    if self.hasInputFromPort('p_autoinvert') :
      p_autoinvert = self.getInputFromPort('p_autoinvert')
    p_execmode = '0'
    if self.hasInputFromPort('p_execmode') :
      p_execmode = self.getInputFromPort('p_execmode')
    p_center_x = -1.0
    if self.hasInputFromPort('p_center_x') :
      p_center_x = self.getInputFromPort('p_center_x')
    p_center_y = -1.0
    if self.hasInputFromPort('p_center_y') :
      p_center_y = self.getInputFromPort('p_center_y')
    p_center_z = -1.0
    if self.hasInputFromPort('p_center_z') :
      p_center_z = self.getInputFromPort('p_center_z')
    p_right_x = -1.0
    if self.hasInputFromPort('p_right_x') :
      p_right_x = self.getInputFromPort('p_right_x')
    p_right_y = -1.0
    if self.hasInputFromPort('p_right_y') :
      p_right_y = self.getInputFromPort('p_right_y')
    p_right_z = -1.0
    if self.hasInputFromPort('p_right_z') :
      p_right_z = self.getInputFromPort('p_right_z')
    p_down_x = -1.0
    if self.hasInputFromPort('p_down_x') :
      p_down_x = self.getInputFromPort('p_down_x')
    p_down_y = -1.0
    if self.hasInputFromPort('p_down_y') :
      p_down_y = self.getInputFromPort('p_down_y')
    p_down_z = -1.0
    if self.hasInputFromPort('p_down_z') :
      p_down_z = self.getInputFromPort('p_down_z')
    p_in_x = -1.0
    if self.hasInputFromPort('p_in_x') :
      p_in_x = self.getInputFromPort('p_in_x')
    p_in_y = -1.0
    if self.hasInputFromPort('p_in_y') :
      p_in_y = self.getInputFromPort('p_in_y')
    p_in_z = -1.0
    if self.hasInputFromPort('p_in_z') :
      p_in_z = self.getInputFromPort('p_in_z')
    p_scale = -1.0
    if self.hasInputFromPort('p_scale') :
      p_scale = self.getInputFromPort('p_scale')
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    Clip_Field = 0
    if self.hasInputFromPort('Clip Field') :
      Clip_Field = self.getInputFromPort('Clip Field')
    results = sr_py.ClipFieldToFieldOrWidget(Input_Field,Clip_Field,p_clip_location,p_clipmode,p_autoexecute,p_autoinvert,p_execmode,p_center_x,p_center_y,p_center_z,p_right_x,p_right_y,p_right_z,p_down_x,p_down_y,p_down_z,p_in_x,p_in_y,p_in_z,p_scale)
    self.setResult('Selection Widget', results[0])
    self.setResult('Output Field', results[1])

class scirun_ConvertHexVolToTetVol(Module) :
  def compute(self) :
    HexVol = 0
    if self.hasInputFromPort('HexVol') :
      HexVol = self.getInputFromPort('HexVol')
    results = sr_py.ConvertHexVolToTetVol(HexVol)
    self.setResult('TetVol', results)

class scirun_SetFieldOrMeshStringProperty(Module) :
  def compute(self) :
    p_prop = 'units'
    if self.hasInputFromPort('p_prop') :
      p_prop = self.getInputFromPort('p_prop')
    p_val = 'cm'
    if self.hasInputFromPort('p_val') :
      p_val = self.getInputFromPort('p_val')
    p_meshprop = 1
    if self.hasInputFromPort('p_meshprop') :
      p_meshprop = self.getInputFromPort('p_meshprop')
    Input = 0
    if self.hasInputFromPort('Input') :
      Input = self.getInputFromPort('Input')
    results = sr_py.SetFieldOrMeshStringProperty(Input,p_prop,p_val,p_meshprop)
    self.setResult('Output', results)

class scirun_ConvertMeshCoordinateSystem(Module) :
  def compute(self) :
    p_oldsystem = 'Cartesian'
    if self.hasInputFromPort('p_oldsystem') :
      p_oldsystem = self.getInputFromPort('p_oldsystem')
    p_newsystem = 'Spherical'
    if self.hasInputFromPort('p_newsystem') :
      p_newsystem = self.getInputFromPort('p_newsystem')
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    results = sr_py.ConvertMeshCoordinateSystem(Input_Field,p_oldsystem,p_newsystem)
    self.setResult('Output Field', results)

class scirun_RefineMeshByIsovalue2(Module) :
  def compute(self) :
    p_isoval = 0.0
    if self.hasInputFromPort('p_isoval') :
      p_isoval = self.getInputFromPort('p_isoval')
    p_lte = 1
    if self.hasInputFromPort('p_lte') :
      p_lte = self.getInputFromPort('p_lte')
    Input = 0
    if self.hasInputFromPort('Input') :
      Input = self.getInputFromPort('Input')
    Optional_Isovalue = 0
    if self.hasInputFromPort('Optional Isovalue') :
      Optional_Isovalue = self.getInputFromPort('Optional Isovalue')
    results = sr_py.RefineMeshByIsovalue2(Input,Optional_Isovalue,p_isoval,p_lte)
    self.setResult('Refined', results[0])
    self.setResult('Mapping', results[1])

class scirun_SetTetVolFieldDataValuesToZero(Module) :
  def compute(self) :
    InField = 0
    if self.hasInputFromPort('InField') :
      InField = self.getInputFromPort('InField')
    results = sr_py.SetTetVolFieldDataValuesToZero(InField)
    self.setResult('OutField', results)

class scirun_ViewSlices(Module) :
  def compute(self) :
    p_clut_ww = '1.0'
    if self.hasInputFromPort('p_clut_ww') :
      p_clut_ww = self.getInputFromPort('p_clut_ww')
    p_clut_wl = '0.0'
    if self.hasInputFromPort('p_clut_wl') :
      p_clut_wl = self.getInputFromPort('p_clut_wl')
    p_probe = '0'
    if self.hasInputFromPort('p_probe') :
      p_probe = self.getInputFromPort('p_probe')
    p_show_colormap2 = '0'
    if self.hasInputFromPort('p_show_colormap2') :
      p_show_colormap2 = self.getInputFromPort('p_show_colormap2')
    p_painting = '0'
    if self.hasInputFromPort('p_painting') :
      p_painting = self.getInputFromPort('p_painting')
    p_crop = '0'
    if self.hasInputFromPort('p_crop') :
      p_crop = self.getInputFromPort('p_crop')
    p_crop_minAxis0 = '0'
    if self.hasInputFromPort('p_crop_minAxis0') :
      p_crop_minAxis0 = self.getInputFromPort('p_crop_minAxis0')
    p_crop_minAxis1 = '0'
    if self.hasInputFromPort('p_crop_minAxis1') :
      p_crop_minAxis1 = self.getInputFromPort('p_crop_minAxis1')
    p_crop_minAxis2 = '0'
    if self.hasInputFromPort('p_crop_minAxis2') :
      p_crop_minAxis2 = self.getInputFromPort('p_crop_minAxis2')
    p_crop_maxAxis0 = '0'
    if self.hasInputFromPort('p_crop_maxAxis0') :
      p_crop_maxAxis0 = self.getInputFromPort('p_crop_maxAxis0')
    p_crop_maxAxis1 = '0'
    if self.hasInputFromPort('p_crop_maxAxis1') :
      p_crop_maxAxis1 = self.getInputFromPort('p_crop_maxAxis1')
    p_crop_maxAxis2 = '0'
    if self.hasInputFromPort('p_crop_maxAxis2') :
      p_crop_maxAxis2 = self.getInputFromPort('p_crop_maxAxis2')
    p_crop_minPadAxis0 = '0'
    if self.hasInputFromPort('p_crop_minPadAxis0') :
      p_crop_minPadAxis0 = self.getInputFromPort('p_crop_minPadAxis0')
    p_crop_minPadAxis1 = '0'
    if self.hasInputFromPort('p_crop_minPadAxis1') :
      p_crop_minPadAxis1 = self.getInputFromPort('p_crop_minPadAxis1')
    p_crop_minPadAxis2 = '0'
    if self.hasInputFromPort('p_crop_minPadAxis2') :
      p_crop_minPadAxis2 = self.getInputFromPort('p_crop_minPadAxis2')
    p_crop_maxPadAxis0 = '0'
    if self.hasInputFromPort('p_crop_maxPadAxis0') :
      p_crop_maxPadAxis0 = self.getInputFromPort('p_crop_maxPadAxis0')
    p_crop_maxPadAxis1 = '0'
    if self.hasInputFromPort('p_crop_maxPadAxis1') :
      p_crop_maxPadAxis1 = self.getInputFromPort('p_crop_maxPadAxis1')
    p_crop_maxPadAxis2 = '0'
    if self.hasInputFromPort('p_crop_maxPadAxis2') :
      p_crop_maxPadAxis2 = self.getInputFromPort('p_crop_maxPadAxis2')
    p_texture_filter = '1'
    if self.hasInputFromPort('p_texture_filter') :
      p_texture_filter = self.getInputFromPort('p_texture_filter')
    p_anatomical_coordinates = '1'
    if self.hasInputFromPort('p_anatomical_coordinates') :
      p_anatomical_coordinates = self.getInputFromPort('p_anatomical_coordinates')
    p_show_text = '1'
    if self.hasInputFromPort('p_show_text') :
      p_show_text = self.getInputFromPort('p_show_text')
    p_color_font_r = '1.0'
    if self.hasInputFromPort('p_color_font_r') :
      p_color_font_r = self.getInputFromPort('p_color_font_r')
    p_color_font_g = '1.0'
    if self.hasInputFromPort('p_color_font_g') :
      p_color_font_g = self.getInputFromPort('p_color_font_g')
    p_color_font_b = '1.0'
    if self.hasInputFromPort('p_color_font_b') :
      p_color_font_b = self.getInputFromPort('p_color_font_b')
    p_color_font_a = '1.0'
    if self.hasInputFromPort('p_color_font_a') :
      p_color_font_a = self.getInputFromPort('p_color_font_a')
    p_min = '-1.0'
    if self.hasInputFromPort('p_min') :
      p_min = self.getInputFromPort('p_min')
    p_max = '-1.0'
    if self.hasInputFromPort('p_max') :
      p_max = self.getInputFromPort('p_max')
    p_dim0 = '0'
    if self.hasInputFromPort('p_dim0') :
      p_dim0 = self.getInputFromPort('p_dim0')
    p_dim1 = '0'
    if self.hasInputFromPort('p_dim1') :
      p_dim1 = self.getInputFromPort('p_dim1')
    p_dim2 = '0'
    if self.hasInputFromPort('p_dim2') :
      p_dim2 = self.getInputFromPort('p_dim2')
    p_geom_flushed = '0'
    if self.hasInputFromPort('p_geom_flushed') :
      p_geom_flushed = self.getInputFromPort('p_geom_flushed')
    p_background_threshold = '0.0'
    if self.hasInputFromPort('p_background_threshold') :
      p_background_threshold = self.getInputFromPort('p_background_threshold')
    p_gradient_threshold = '0.0'
    if self.hasInputFromPort('p_gradient_threshold') :
      p_gradient_threshold = self.getInputFromPort('p_gradient_threshold')
    p_font_size = '15.0'
    if self.hasInputFromPort('p_font_size') :
      p_font_size = self.getInputFromPort('p_font_size')
    Nrrd1 = 0
    if self.hasInputFromPort('Nrrd1') :
      Nrrd1 = self.getInputFromPort('Nrrd1')
    Nrrd2 = 0
    if self.hasInputFromPort('Nrrd2') :
      Nrrd2 = self.getInputFromPort('Nrrd2')
    Nrrd1ColorMap = 0
    if self.hasInputFromPort('Nrrd1ColorMap') :
      Nrrd1ColorMap = self.getInputFromPort('Nrrd1ColorMap')
    Nrrd2ColorMap = 0
    if self.hasInputFromPort('Nrrd2ColorMap') :
      Nrrd2ColorMap = self.getInputFromPort('Nrrd2ColorMap')
    InputColorMap2 = 0
    if self.hasInputFromPort('InputColorMap2') :
      InputColorMap2 = self.getInputFromPort('InputColorMap2')
    NrrdGradient = 0
    if self.hasInputFromPort('NrrdGradient') :
      NrrdGradient = self.getInputFromPort('NrrdGradient')
    results = sr_py.ViewSlices(Nrrd1,Nrrd2,Nrrd1ColorMap,Nrrd2ColorMap,InputColorMap2,NrrdGradient,p_clut_ww,p_clut_wl,p_probe,p_show_colormap2,p_painting,p_crop,p_crop_minAxis0,p_crop_minAxis1,p_crop_minAxis2,p_crop_maxAxis0,p_crop_maxAxis1,p_crop_maxAxis2,p_crop_minPadAxis0,p_crop_minPadAxis1,p_crop_minPadAxis2,p_crop_maxPadAxis0,p_crop_maxPadAxis1,p_crop_maxPadAxis2,p_texture_filter,p_anatomical_coordinates,p_show_text,p_color_font_r,p_color_font_g,p_color_font_b,p_color_font_a,p_min,p_max,p_dim0,p_dim1,p_dim2,p_geom_flushed,p_background_threshold,p_gradient_threshold,p_font_size)
    self.setResult('Geometry', results[0])
    self.setResult('ColorMap2', results[1])

class scirun_SplitVectorArrayInXYZ(Module) :
  def compute(self) :
    VectorArray = 0
    if self.hasInputFromPort('VectorArray') :
      VectorArray = self.getInputFromPort('VectorArray')
    results = sr_py.SplitVectorArrayInXYZ(VectorArray)
    self.setResult('X', results[0])
    self.setResult('Y', results[1])
    self.setResult('Z', results[2])

class scirun_ConvertIndicesToFieldData(Module) :
  def compute(self) :
    p_outputtype = 'double'
    if self.hasInputFromPort('p_outputtype') :
      p_outputtype = self.getInputFromPort('p_outputtype')
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    Data = 0
    if self.hasInputFromPort('Data') :
      Data = self.getInputFromPort('Data')
    results = sr_py.ConvertIndicesToFieldData(Field,Data,p_outputtype)
    self.setResult('Field', results)

class scirun_CalculateDistanceToFieldBoundary(Module) :
  def compute(self) :
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    results = sr_py.CalculateDistanceToFieldBoundary(Field)
    self.setResult('DistanceField', results)

class scirun_ConvertMappingMatrixToMaskVector(Module) :
  def compute(self) :
    MappingMatrix = 0
    if self.hasInputFromPort('MappingMatrix') :
      MappingMatrix = self.getInputFromPort('MappingMatrix')
    results = sr_py.ConvertMappingMatrixToMaskVector(MappingMatrix)
    self.setResult('MaskVector', results)

class scirun_MapFieldDataFromSourceToDestination(Module) :
  def compute(self) :
    p_interpolation_basis = 'linear'
    if self.hasInputFromPort('p_interpolation_basis') :
      p_interpolation_basis = self.getInputFromPort('p_interpolation_basis')
    p_map_source_to_single_dest = 0
    if self.hasInputFromPort('p_map_source_to_single_dest') :
      p_map_source_to_single_dest = self.getInputFromPort('p_map_source_to_single_dest')
    p_exhaustive_search = 0
    if self.hasInputFromPort('p_exhaustive_search') :
      p_exhaustive_search = self.getInputFromPort('p_exhaustive_search')
    p_exhaustive_search_max_dist = -1.0
    if self.hasInputFromPort('p_exhaustive_search_max_dist') :
      p_exhaustive_search_max_dist = self.getInputFromPort('p_exhaustive_search_max_dist')
    p_np = 1
    if self.hasInputFromPort('p_np') :
      p_np = self.getInputFromPort('p_np')
    Source = 0
    if self.hasInputFromPort('Source') :
      Source = self.getInputFromPort('Source')
    Destination = 0
    if self.hasInputFromPort('Destination') :
      Destination = self.getInputFromPort('Destination')
    results = sr_py.MapFieldDataFromSourceToDestination(Source,Destination,p_interpolation_basis,p_map_source_to_single_dest,p_exhaustive_search,p_exhaustive_search_max_dist,p_np)
    self.setResult('Remapped Destination', results)

class scirun_CreateLatVol(Module) :
  def compute(self) :
    p_sizex = 16
    if self.hasInputFromPort('p_sizex') :
      p_sizex = self.getInputFromPort('p_sizex')
    p_sizey = 16
    if self.hasInputFromPort('p_sizey') :
      p_sizey = self.getInputFromPort('p_sizey')
    p_sizez = 16
    if self.hasInputFromPort('p_sizez') :
      p_sizez = self.getInputFromPort('p_sizez')
    p_padpercent = 0.0
    if self.hasInputFromPort('p_padpercent') :
      p_padpercent = self.getInputFromPort('p_padpercent')
    p_data_at = 'Nodes'
    if self.hasInputFromPort('p_data_at') :
      p_data_at = self.getInputFromPort('p_data_at')
    p_element_size = 'Mesh'
    if self.hasInputFromPort('p_element_size') :
      p_element_size = self.getInputFromPort('p_element_size')
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    LatVol_Size = 0
    if self.hasInputFromPort('LatVol Size') :
      LatVol_Size = self.getInputFromPort('LatVol Size')
    results = sr_py.CreateLatVol(Input_Field,LatVol_Size,p_sizex,p_sizey,p_sizez,p_padpercent,p_data_at,p_element_size)
    self.setResult('Output Sample Field', results)

class scirun_ResizeMatrix(Module) :
  def compute(self) :
    p_dim_m = 1
    if self.hasInputFromPort('p_dim_m') :
      p_dim_m = self.getInputFromPort('p_dim_m')
    p_dim_n = 1
    if self.hasInputFromPort('p_dim_n') :
      p_dim_n = self.getInputFromPort('p_dim_n')
    Matrix = 0
    if self.hasInputFromPort('Matrix') :
      Matrix = self.getInputFromPort('Matrix')
    M = 0
    if self.hasInputFromPort('M') :
      M = self.getInputFromPort('M')
    N = 0
    if self.hasInputFromPort('N') :
      N = self.getInputFromPort('N')
    results = sr_py.ResizeMatrix(Matrix,M,N,p_dim_m,p_dim_n)
    self.setResult('Matrix', results)

class scirun_ShowAndEditCameraWidget(Module) :
  def compute(self) :
    p_frame = 1
    if self.hasInputFromPort('p_frame') :
      p_frame = self.getInputFromPort('p_frame')
    p_num_frames = 100
    if self.hasInputFromPort('p_num_frames') :
      p_num_frames = self.getInputFromPort('p_num_frames')
    p_time = 0
    if self.hasInputFromPort('p_time') :
      p_time = self.getInputFromPort('p_time')
    p_playmode = 'once'
    if self.hasInputFromPort('p_playmode') :
      p_playmode = self.getInputFromPort('p_playmode')
    p_execmode = 'init'
    if self.hasInputFromPort('p_execmode') :
      p_execmode = self.getInputFromPort('p_execmode')
    p_track = 1
    if self.hasInputFromPort('p_track') :
      p_track = self.getInputFromPort('p_track')
    p_B = 1.0
    if self.hasInputFromPort('p_B') :
      p_B = self.getInputFromPort('p_B')
    p_C = 0.0
    if self.hasInputFromPort('p_C') :
      p_C = self.getInputFromPort('p_C')
    results = sr_py.ShowAndEditCameraWidget(p_frame,p_num_frames,p_time,p_playmode,p_execmode,p_track,p_B,p_C)
    self.setResult('Geometry', results)

class scirun_InterfaceWithCamal(Module) :
  def compute(self) :
    TriSurf = 0
    if self.hasInputFromPort('TriSurf') :
      TriSurf = self.getInputFromPort('TriSurf')
    results = sr_py.InterfaceWithCamal(TriSurf)
    self.setResult('TetVol', results)

class scirun_SelectAndSetFieldData3(Module) :
  def compute(self) :
    p_selection1 = 'DATA < A'
    if self.hasInputFromPort('p_selection1') :
      p_selection1 = self.getInputFromPort('p_selection1')
    p_function1 = 'abs(DATA)'
    if self.hasInputFromPort('p_function1') :
      p_function1 = self.getInputFromPort('p_function1')
    p_selection2 = 'DATA > A'
    if self.hasInputFromPort('p_selection2') :
      p_selection2 = self.getInputFromPort('p_selection2')
    p_function2 = '-abs(DATA)'
    if self.hasInputFromPort('p_function2') :
      p_function2 = self.getInputFromPort('p_function2')
    p_selection3 = ''
    if self.hasInputFromPort('p_selection3') :
      p_selection3 = self.getInputFromPort('p_selection3')
    p_function3 = ''
    if self.hasInputFromPort('p_function3') :
      p_function3 = self.getInputFromPort('p_function3')
    p_selection4 = ''
    if self.hasInputFromPort('p_selection4') :
      p_selection4 = self.getInputFromPort('p_selection4')
    p_function4 = ''
    if self.hasInputFromPort('p_function4') :
      p_function4 = self.getInputFromPort('p_function4')
    p_functiondef = '0'
    if self.hasInputFromPort('p_functiondef') :
      p_functiondef = self.getInputFromPort('p_functiondef')
    p_format = 'Scalar'
    if self.hasInputFromPort('p_format') :
      p_format = self.getInputFromPort('p_format')
    Field1 = 0
    if self.hasInputFromPort('Field1') :
      Field1 = self.getInputFromPort('Field1')
    Field2 = 0
    if self.hasInputFromPort('Field2') :
      Field2 = self.getInputFromPort('Field2')
    Field3 = 0
    if self.hasInputFromPort('Field3') :
      Field3 = self.getInputFromPort('Field3')
    Array = 0
    if self.hasInputFromPort('Array') :
      Array = self.getInputFromPort('Array')
    results = sr_py.SelectAndSetFieldData3(Field1,Field2,Field3,Array,p_selection1,p_function1,p_selection2,p_function2,p_selection3,p_function3,p_selection4,p_function4,p_functiondef,p_format)
    self.setResult('Field', results)

class scirun_ConvertMeshToPointCloud(Module) :
  def compute(self) :
    p_datalocation = 0
    if self.hasInputFromPort('p_datalocation') :
      p_datalocation = self.getInputFromPort('p_datalocation')
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    results = sr_py.ConvertMeshToPointCloud(Field,p_datalocation)
    self.setResult('Field', results)

class scirun_CreateFieldData(Module) :
  def compute(self) :
    p_function = 'RESULT = 1;'
    if self.hasInputFromPort('p_function') :
      p_function = self.getInputFromPort('p_function')
    p_format = 'Scalar'
    if self.hasInputFromPort('p_format') :
      p_format = self.getInputFromPort('p_format')
    p_basis = 'Linear'
    if self.hasInputFromPort('p_basis') :
      p_basis = self.getInputFromPort('p_basis')
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    Function = ''
    if self.hasInputFromPort('Function') :
      Function = self.getInputFromPort('Function')
    DataArray = 0
    if self.hasInputFromPort('DataArray') :
      DataArray = self.getInputFromPort('DataArray')
    results = sr_py.CreateFieldData(Field,Function,DataArray,p_function,p_format,p_basis)
    self.setResult('Field', results)

class scirun_InsertStringsIntoBundle(Module) :
  def compute(self) :
    p_string1_name = 'string1'
    if self.hasInputFromPort('p_string1_name') :
      p_string1_name = self.getInputFromPort('p_string1_name')
    p_string2_name = 'string2'
    if self.hasInputFromPort('p_string2_name') :
      p_string2_name = self.getInputFromPort('p_string2_name')
    p_string3_name = 'string3'
    if self.hasInputFromPort('p_string3_name') :
      p_string3_name = self.getInputFromPort('p_string3_name')
    p_string4_name = 'string4'
    if self.hasInputFromPort('p_string4_name') :
      p_string4_name = self.getInputFromPort('p_string4_name')
    p_string5_name = 'string5'
    if self.hasInputFromPort('p_string5_name') :
      p_string5_name = self.getInputFromPort('p_string5_name')
    p_string6_name = 'string6'
    if self.hasInputFromPort('p_string6_name') :
      p_string6_name = self.getInputFromPort('p_string6_name')
    p_replace1 = 1
    if self.hasInputFromPort('p_replace1') :
      p_replace1 = self.getInputFromPort('p_replace1')
    p_replace2 = 1
    if self.hasInputFromPort('p_replace2') :
      p_replace2 = self.getInputFromPort('p_replace2')
    p_replace3 = 1
    if self.hasInputFromPort('p_replace3') :
      p_replace3 = self.getInputFromPort('p_replace3')
    p_replace4 = 1
    if self.hasInputFromPort('p_replace4') :
      p_replace4 = self.getInputFromPort('p_replace4')
    p_replace5 = 1
    if self.hasInputFromPort('p_replace5') :
      p_replace5 = self.getInputFromPort('p_replace5')
    p_replace6 = 1
    if self.hasInputFromPort('p_replace6') :
      p_replace6 = self.getInputFromPort('p_replace6')
    bundle = 0
    if self.hasInputFromPort('bundle') :
      bundle = self.getInputFromPort('bundle')
    string1 = ''
    if self.hasInputFromPort('string1') :
      string1 = self.getInputFromPort('string1')
    string2 = ''
    if self.hasInputFromPort('string2') :
      string2 = self.getInputFromPort('string2')
    string3 = ''
    if self.hasInputFromPort('string3') :
      string3 = self.getInputFromPort('string3')
    string4 = ''
    if self.hasInputFromPort('string4') :
      string4 = self.getInputFromPort('string4')
    string5 = ''
    if self.hasInputFromPort('string5') :
      string5 = self.getInputFromPort('string5')
    string6 = ''
    if self.hasInputFromPort('string6') :
      string6 = self.getInputFromPort('string6')
    results = sr_py.InsertStringsIntoBundle(bundle,string1,string2,string3,string4,string5,string6,p_string1_name,p_string2_name,p_string3_name,p_string4_name,p_string5_name,p_string6_name,p_replace1,p_replace2,p_replace3,p_replace4,p_replace5,p_replace6)
    self.setResult('bundle', results)

class scirun_GetInputFieldAndSendAsOutput(Module) :
  def compute(self) :
    InField = 0
    if self.hasInputFromPort('InField') :
      InField = self.getInputFromPort('InField')
    results = sr_py.GetInputFieldAndSendAsOutput(InField)
    self.setResult('OutField', results)

class scirun_GetNrrdsFromBundle(Module) :
  def compute(self) :
    p_nrrd1_name = 'nrrd1'
    if self.hasInputFromPort('p_nrrd1_name') :
      p_nrrd1_name = self.getInputFromPort('p_nrrd1_name')
    p_nrrd2_name = 'nrrd2'
    if self.hasInputFromPort('p_nrrd2_name') :
      p_nrrd2_name = self.getInputFromPort('p_nrrd2_name')
    p_nrrd3_name = 'nrrd3'
    if self.hasInputFromPort('p_nrrd3_name') :
      p_nrrd3_name = self.getInputFromPort('p_nrrd3_name')
    p_nrrd4_name = 'nrrd4'
    if self.hasInputFromPort('p_nrrd4_name') :
      p_nrrd4_name = self.getInputFromPort('p_nrrd4_name')
    p_nrrd5_name = 'nrrd5'
    if self.hasInputFromPort('p_nrrd5_name') :
      p_nrrd5_name = self.getInputFromPort('p_nrrd5_name')
    p_nrrd6_name = 'nrrd6'
    if self.hasInputFromPort('p_nrrd6_name') :
      p_nrrd6_name = self.getInputFromPort('p_nrrd6_name')
    p_transposenrrd1 = 0
    if self.hasInputFromPort('p_transposenrrd1') :
      p_transposenrrd1 = self.getInputFromPort('p_transposenrrd1')
    p_transposenrrd2 = 0
    if self.hasInputFromPort('p_transposenrrd2') :
      p_transposenrrd2 = self.getInputFromPort('p_transposenrrd2')
    p_transposenrrd3 = 0
    if self.hasInputFromPort('p_transposenrrd3') :
      p_transposenrrd3 = self.getInputFromPort('p_transposenrrd3')
    p_transposenrrd4 = 0
    if self.hasInputFromPort('p_transposenrrd4') :
      p_transposenrrd4 = self.getInputFromPort('p_transposenrrd4')
    p_transposenrrd5 = 0
    if self.hasInputFromPort('p_transposenrrd5') :
      p_transposenrrd5 = self.getInputFromPort('p_transposenrrd5')
    p_transposenrrd6 = 0
    if self.hasInputFromPort('p_transposenrrd6') :
      p_transposenrrd6 = self.getInputFromPort('p_transposenrrd6')
    p_nrrd_selection = ''
    if self.hasInputFromPort('p_nrrd_selection') :
      p_nrrd_selection = self.getInputFromPort('p_nrrd_selection')
    bundle = 0
    if self.hasInputFromPort('bundle') :
      bundle = self.getInputFromPort('bundle')
    results = sr_py.GetNrrdsFromBundle(bundle,p_nrrd1_name,p_nrrd2_name,p_nrrd3_name,p_nrrd4_name,p_nrrd5_name,p_nrrd6_name,p_transposenrrd1,p_transposenrrd2,p_transposenrrd3,p_transposenrrd4,p_transposenrrd5,p_transposenrrd6,p_nrrd_selection)
    self.setResult('bundle', results[0])
    self.setResult('nrrd1', results[1])
    self.setResult('nrrd2', results[2])
    self.setResult('nrrd3', results[3])
    self.setResult('nrrd4', results[4])
    self.setResult('nrrd5', results[5])
    self.setResult('nrrd6', results[6])

class scirun_ManageFieldSeries(Module) :
  def compute(self) :
    p_num_ports = '2'
    if self.hasInputFromPort('p_num_ports') :
      p_num_ports = self.getInputFromPort('p_num_ports')
    Input = 0
    if self.hasInputFromPort('Input') :
      Input = self.getInputFromPort('Input')
    results = sr_py.ManageFieldSeries(Input,p_num_ports)
    self.setResult('Output 0', results[0])
    self.setResult('Output 1', results[1])
    self.setResult('Output 2', results[2])
    self.setResult('Output 3', results[3])

class scirun_ConvertMatrixToField(Module) :
  def compute(self) :
    p_datalocation = 'Node'
    if self.hasInputFromPort('p_datalocation') :
      p_datalocation = self.getInputFromPort('p_datalocation')
    Matrix = 0
    if self.hasInputFromPort('Matrix') :
      Matrix = self.getInputFromPort('Matrix')
    results = sr_py.ConvertMatrixToField(Matrix,p_datalocation)
    self.setResult('Field', results)

class scirun_CollectMatrices(Module) :
  def compute(self) :
    p_append = 0
    if self.hasInputFromPort('p_append') :
      p_append = self.getInputFromPort('p_append')
    p_row = 0
    if self.hasInputFromPort('p_row') :
      p_row = self.getInputFromPort('p_row')
    p_front = 0
    if self.hasInputFromPort('p_front') :
      p_front = self.getInputFromPort('p_front')
    Optional_BaseMatrix = 0
    if self.hasInputFromPort('Optional BaseMatrix') :
      Optional_BaseMatrix = self.getInputFromPort('Optional BaseMatrix')
    SubMatrix = 0
    if self.hasInputFromPort('SubMatrix') :
      SubMatrix = self.getInputFromPort('SubMatrix')
    results = sr_py.CollectMatrices(Optional_BaseMatrix,SubMatrix,p_append,p_row,p_front)
    self.setResult('CompositeMatrix', results)

class scirun_ChooseColorMap(Module) :
  def compute(self) :
    p_use_first_valid = '1'
    if self.hasInputFromPort('p_use_first_valid') :
      p_use_first_valid = self.getInputFromPort('p_use_first_valid')
    p_port_valid_index = '0'
    if self.hasInputFromPort('p_port_valid_index') :
      p_port_valid_index = self.getInputFromPort('p_port_valid_index')
    p_port_selected_index = '0'
    if self.hasInputFromPort('p_port_selected_index') :
      p_port_selected_index = self.getInputFromPort('p_port_selected_index')
    ColorMap = 0
    if self.hasInputFromPort('ColorMap') :
      ColorMap = self.getInputFromPort('ColorMap')
    results = sr_py.ChooseColorMap(ColorMap,p_use_first_valid,p_port_valid_index,p_port_selected_index)
    self.setResult('ColorMap', results)

class scirun_ReadField(Module) :
  def compute(self) :
    p_from_env = ''
    if self.hasInputFromPort('p_from_env') :
      p_from_env = self.getInputFromPort('p_from_env')
    Filename = ''
    if self.hasInputFromPort('Filename') :
      Filename = self.getInputFromPort('Filename')
    results = sr_py.ReadField(Filename,p_from_env)
    self.setResult('Output Data', results[0])
    self.setResult('Filename', results[1])

class scirun_GetFileName(Module) :
  def compute(self) :
    p_filename_base = ''
    if self.hasInputFromPort('p_filename_base') :
      p_filename_base = self.getInputFromPort('p_filename_base')
    p_delay = 0
    if self.hasInputFromPort('p_delay') :
      p_delay = self.getInputFromPort('p_delay')
    p_pinned = 0
    if self.hasInputFromPort('p_pinned') :
      p_pinned = self.getInputFromPort('p_pinned')
    results = sr_py.GetFileName(p_filename_base,p_delay,p_pinned)
    self.setResult('Full Filename', results)

class scirun_DecomposeTensorArrayIntoEigenVectors(Module) :
  def compute(self) :
    TensorArray = 0
    if self.hasInputFromPort('TensorArray') :
      TensorArray = self.getInputFromPort('TensorArray')
    results = sr_py.DecomposeTensorArrayIntoEigenVectors(TensorArray)
    self.setResult('EigenVector1', results[0])
    self.setResult('EigenVector2', results[1])
    self.setResult('EigenVector3', results[2])
    self.setResult('EigenValue1', results[3])
    self.setResult('EigenValue2', results[4])
    self.setResult('EigenValue3', results[5])

class scirun_TransformMeshWithTransform(Module) :
  def compute(self) :
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    Transform_Matrix = 0
    if self.hasInputFromPort('Transform Matrix') :
      Transform_Matrix = self.getInputFromPort('Transform Matrix')
    results = sr_py.TransformMeshWithTransform(Input_Field,Transform_Matrix)
    self.setResult('Transformed Field', results)

class scirun_ClipVolumeByIsovalue(Module) :
  def compute(self) :
    p_isoval_min = 0.0
    if self.hasInputFromPort('p_isoval_min') :
      p_isoval_min = self.getInputFromPort('p_isoval_min')
    p_isoval_max = 99.0
    if self.hasInputFromPort('p_isoval_max') :
      p_isoval_max = self.getInputFromPort('p_isoval_max')
    p_isoval = 0.0
    if self.hasInputFromPort('p_isoval') :
      p_isoval = self.getInputFromPort('p_isoval')
    p_lte = 1
    if self.hasInputFromPort('p_lte') :
      p_lte = self.getInputFromPort('p_lte')
    p_update_type = 'On Release'
    if self.hasInputFromPort('p_update_type') :
      p_update_type = self.getInputFromPort('p_update_type')
    Input = 0
    if self.hasInputFromPort('Input') :
      Input = self.getInputFromPort('Input')
    Optional_Isovalue = 0
    if self.hasInputFromPort('Optional Isovalue') :
      Optional_Isovalue = self.getInputFromPort('Optional Isovalue')
    results = sr_py.ClipVolumeByIsovalue(Input,Optional_Isovalue,p_isoval_min,p_isoval_max,p_isoval,p_lte,p_update_type)
    self.setResult('Clipped', results[0])
    self.setResult('Mapping', results[1])

class scirun_ReportSearchGridInfo(Module) :
  def compute(self) :
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    results = sr_py.ReportSearchGridInfo(Input_Field)
    self.setResult('Output Sample Field', results)

class scirun_ChooseField(Module) :
  def compute(self) :
    p_use_first_valid = '1'
    if self.hasInputFromPort('p_use_first_valid') :
      p_use_first_valid = self.getInputFromPort('p_use_first_valid')
    p_port_valid_index = '0'
    if self.hasInputFromPort('p_port_valid_index') :
      p_port_valid_index = self.getInputFromPort('p_port_valid_index')
    p_port_selected_index = '0'
    if self.hasInputFromPort('p_port_selected_index') :
      p_port_selected_index = self.getInputFromPort('p_port_selected_index')
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    results = sr_py.ChooseField(Field,p_use_first_valid,p_port_valid_index,p_port_selected_index)
    self.setResult('Field', results)

class scirun_ConvertRegularMeshToStructuredMesh(Module) :
  def compute(self) :
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    results = sr_py.ConvertRegularMeshToStructuredMesh(Input_Field)
    self.setResult('Output Field', results)

class scirun_CreateLightForViewer(Module) :
  def compute(self) :
    p_control_pos_saved = 0
    if self.hasInputFromPort('p_control_pos_saved') :
      p_control_pos_saved = self.getInputFromPort('p_control_pos_saved')
    p_control_x = 0.0
    if self.hasInputFromPort('p_control_x') :
      p_control_x = self.getInputFromPort('p_control_x')
    p_control_y = 0.0
    if self.hasInputFromPort('p_control_y') :
      p_control_y = self.getInputFromPort('p_control_y')
    p_control_z = 0.0
    if self.hasInputFromPort('p_control_z') :
      p_control_z = self.getInputFromPort('p_control_z')
    p_at_x = 0.0
    if self.hasInputFromPort('p_at_x') :
      p_at_x = self.getInputFromPort('p_at_x')
    p_at_y = 0.0
    if self.hasInputFromPort('p_at_y') :
      p_at_y = self.getInputFromPort('p_at_y')
    p_at_z = 1.0
    if self.hasInputFromPort('p_at_z') :
      p_at_z = self.getInputFromPort('p_at_z')
    p_type = 0
    if self.hasInputFromPort('p_type') :
      p_type = self.getInputFromPort('p_type')
    p_on = 1
    if self.hasInputFromPort('p_on') :
      p_on = self.getInputFromPort('p_on')
    results = sr_py.CreateLightForViewer(p_control_pos_saved,p_control_x,p_control_y,p_control_z,p_at_x,p_at_y,p_at_z,p_type,p_on)
    self.setResult('Geometry', results)

class scirun_GetMatricesFromBundle(Module) :
  def compute(self) :
    p_matrix1_name = 'matrix1'
    if self.hasInputFromPort('p_matrix1_name') :
      p_matrix1_name = self.getInputFromPort('p_matrix1_name')
    p_matrix2_name = 'matrix2'
    if self.hasInputFromPort('p_matrix2_name') :
      p_matrix2_name = self.getInputFromPort('p_matrix2_name')
    p_matrix3_name = 'matrix3'
    if self.hasInputFromPort('p_matrix3_name') :
      p_matrix3_name = self.getInputFromPort('p_matrix3_name')
    p_matrix4_name = 'matrix4'
    if self.hasInputFromPort('p_matrix4_name') :
      p_matrix4_name = self.getInputFromPort('p_matrix4_name')
    p_matrix5_name = 'matrix5'
    if self.hasInputFromPort('p_matrix5_name') :
      p_matrix5_name = self.getInputFromPort('p_matrix5_name')
    p_matrix6_name = 'matrix6'
    if self.hasInputFromPort('p_matrix6_name') :
      p_matrix6_name = self.getInputFromPort('p_matrix6_name')
    p_transposenrrd1 = 0
    if self.hasInputFromPort('p_transposenrrd1') :
      p_transposenrrd1 = self.getInputFromPort('p_transposenrrd1')
    p_transposenrrd2 = 0
    if self.hasInputFromPort('p_transposenrrd2') :
      p_transposenrrd2 = self.getInputFromPort('p_transposenrrd2')
    p_transposenrrd3 = 0
    if self.hasInputFromPort('p_transposenrrd3') :
      p_transposenrrd3 = self.getInputFromPort('p_transposenrrd3')
    p_transposenrrd4 = 0
    if self.hasInputFromPort('p_transposenrrd4') :
      p_transposenrrd4 = self.getInputFromPort('p_transposenrrd4')
    p_transposenrrd5 = 0
    if self.hasInputFromPort('p_transposenrrd5') :
      p_transposenrrd5 = self.getInputFromPort('p_transposenrrd5')
    p_transposenrrd6 = 0
    if self.hasInputFromPort('p_transposenrrd6') :
      p_transposenrrd6 = self.getInputFromPort('p_transposenrrd6')
    p_matrix_selection = ''
    if self.hasInputFromPort('p_matrix_selection') :
      p_matrix_selection = self.getInputFromPort('p_matrix_selection')
    bundle = 0
    if self.hasInputFromPort('bundle') :
      bundle = self.getInputFromPort('bundle')
    results = sr_py.GetMatricesFromBundle(bundle,p_matrix1_name,p_matrix2_name,p_matrix3_name,p_matrix4_name,p_matrix5_name,p_matrix6_name,p_transposenrrd1,p_transposenrrd2,p_transposenrrd3,p_transposenrrd4,p_transposenrrd5,p_transposenrrd6,p_matrix_selection)
    self.setResult('bundle', results[0])
    self.setResult('matrix1', results[1])
    self.setResult('matrix2', results[2])
    self.setResult('matrix3', results[3])
    self.setResult('matrix4', results[4])
    self.setResult('matrix5', results[5])
    self.setResult('matrix6', results[6])

class scirun_RefineMesh(Module) :
  def compute(self) :
    p_select = 'all'
    if self.hasInputFromPort('p_select') :
      p_select = self.getInputFromPort('p_select')
    p_method = 'default'
    if self.hasInputFromPort('p_method') :
      p_method = self.getInputFromPort('p_method')
    p_isoval = 0.0
    if self.hasInputFromPort('p_isoval') :
      p_isoval = self.getInputFromPort('p_isoval')
    Mesh = 0
    if self.hasInputFromPort('Mesh') :
      Mesh = self.getInputFromPort('Mesh')
    Isovalue = 0
    if self.hasInputFromPort('Isovalue') :
      Isovalue = self.getInputFromPort('Isovalue')
    results = sr_py.RefineMesh(Mesh,Isovalue,p_select,p_method,p_isoval)
    self.setResult('RefinedMesh', results[0])
    self.setResult('Mapping', results[1])

class scirun_MergeFields(Module) :
  def compute(self) :
    Container_Mesh = 0
    if self.hasInputFromPort('Container Mesh') :
      Container_Mesh = self.getInputFromPort('Container Mesh')
    Insert_Field = 0
    if self.hasInputFromPort('Insert Field') :
      Insert_Field = self.getInputFromPort('Insert Field')
    results = sr_py.MergeFields(Container_Mesh,Insert_Field)
    self.setResult('Combined Field', results[0])
    self.setResult('Extended Insert Field', results[1])
    self.setResult('Combined To Extended Mapping', results[2])

class scirun_BuildPointCloudToLatVolMappingMatrix(Module) :
  def compute(self) :
    p_epsilon = '0.0'
    if self.hasInputFromPort('p_epsilon') :
      p_epsilon = self.getInputFromPort('p_epsilon')
    PointCloudField = 0
    if self.hasInputFromPort('PointCloudField') :
      PointCloudField = self.getInputFromPort('PointCloudField')
    LatVolField = 0
    if self.hasInputFromPort('LatVolField') :
      LatVolField = self.getInputFromPort('LatVolField')
    results = sr_py.BuildPointCloudToLatVolMappingMatrix(PointCloudField,LatVolField,p_epsilon)
    self.setResult('MappingMatrix', results)

class scirun_CalculateDataArray(Module) :
  def compute(self) :
    p_function = 'RESULT = abs(DATA);'
    if self.hasInputFromPort('p_function') :
      p_function = self.getInputFromPort('p_function')
    p_format = 'Scalar'
    if self.hasInputFromPort('p_format') :
      p_format = self.getInputFromPort('p_format')
    DataArray = 0
    if self.hasInputFromPort('DataArray') :
      DataArray = self.getInputFromPort('DataArray')
    Function = ''
    if self.hasInputFromPort('Function') :
      Function = self.getInputFromPort('Function')
    Array = 0
    if self.hasInputFromPort('Array') :
      Array = self.getInputFromPort('Array')
    results = sr_py.CalculateDataArray(DataArray,Function,Array,p_function,p_format)
    self.setResult('DataArray', results)

class scirun_WriteColorMap(Module) :
  def compute(self) :
    p_filetype = 'Binary'
    if self.hasInputFromPort('p_filetype') :
      p_filetype = self.getInputFromPort('p_filetype')
    p_confirm = '0'
    if self.hasInputFromPort('p_confirm') :
      p_confirm = self.getInputFromPort('p_confirm')
    p_confirm_once = '0'
    if self.hasInputFromPort('p_confirm_once') :
      p_confirm_once = self.getInputFromPort('p_confirm_once')
    p_exporttype = ''
    if self.hasInputFromPort('p_exporttype') :
      p_exporttype = self.getInputFromPort('p_exporttype')
    Input_Data = 0
    if self.hasInputFromPort('Input Data') :
      Input_Data = self.getInputFromPort('Input Data')
    Filename = ''
    if self.hasInputFromPort('Filename') :
      Filename = self.getInputFromPort('Filename')
    results = sr_py.WriteColorMap(Input_Data,Filename,p_filetype,p_confirm,p_confirm_once,p_exporttype)

class scirun_ShowTextureVolume(Module) :
  def compute(self) :
    p_sampling_rate_hi = 4.0
    if self.hasInputFromPort('p_sampling_rate_hi') :
      p_sampling_rate_hi = self.getInputFromPort('p_sampling_rate_hi')
    p_sampling_rate_lo = 1.0
    if self.hasInputFromPort('p_sampling_rate_lo') :
      p_sampling_rate_lo = self.getInputFromPort('p_sampling_rate_lo')
    p_gradient_min = 0.0
    if self.hasInputFromPort('p_gradient_min') :
      p_gradient_min = self.getInputFromPort('p_gradient_min')
    p_gradient_max = 0.0
    if self.hasInputFromPort('p_gradient_max') :
      p_gradient_max = self.getInputFromPort('p_gradient_max')
    p_adaptive = 1
    if self.hasInputFromPort('p_adaptive') :
      p_adaptive = self.getInputFromPort('p_adaptive')
    p_cmap_size = 8
    if self.hasInputFromPort('p_cmap_size') :
      p_cmap_size = self.getInputFromPort('p_cmap_size')
    p_sw_raster = 0
    if self.hasInputFromPort('p_sw_raster') :
      p_sw_raster = self.getInputFromPort('p_sw_raster')
    p_render_style = 0
    if self.hasInputFromPort('p_render_style') :
      p_render_style = self.getInputFromPort('p_render_style')
    p_alpha_scale = 0.0
    if self.hasInputFromPort('p_alpha_scale') :
      p_alpha_scale = self.getInputFromPort('p_alpha_scale')
    p_interp_mode = 1
    if self.hasInputFromPort('p_interp_mode') :
      p_interp_mode = self.getInputFromPort('p_interp_mode')
    p_shading = 0
    if self.hasInputFromPort('p_shading') :
      p_shading = self.getInputFromPort('p_shading')
    p_ambient = 0.5
    if self.hasInputFromPort('p_ambient') :
      p_ambient = self.getInputFromPort('p_ambient')
    p_diffuse = 0.5
    if self.hasInputFromPort('p_diffuse') :
      p_diffuse = self.getInputFromPort('p_diffuse')
    p_specular = 0.0
    if self.hasInputFromPort('p_specular') :
      p_specular = self.getInputFromPort('p_specular')
    p_shine = 30.0
    if self.hasInputFromPort('p_shine') :
      p_shine = self.getInputFromPort('p_shine')
    p_light = 0
    if self.hasInputFromPort('p_light') :
      p_light = self.getInputFromPort('p_light')
    p_blend_res = 8
    if self.hasInputFromPort('p_blend_res') :
      p_blend_res = self.getInputFromPort('p_blend_res')
    p_multi_level = 1
    if self.hasInputFromPort('p_multi_level') :
      p_multi_level = self.getInputFromPort('p_multi_level')
    p_use_stencil = 0
    if self.hasInputFromPort('p_use_stencil') :
      p_use_stencil = self.getInputFromPort('p_use_stencil')
    p_invert_opacity = 0
    if self.hasInputFromPort('p_invert_opacity') :
      p_invert_opacity = self.getInputFromPort('p_invert_opacity')
    p_num_clipping_planes = 0
    if self.hasInputFromPort('p_num_clipping_planes') :
      p_num_clipping_planes = self.getInputFromPort('p_num_clipping_planes')
    p_show_clipping_widgets = 1
    if self.hasInputFromPort('p_show_clipping_widgets') :
      p_show_clipping_widgets = self.getInputFromPort('p_show_clipping_widgets')
    p_level_on = ''
    if self.hasInputFromPort('p_level_on') :
      p_level_on = self.getInputFromPort('p_level_on')
    p_level_vals = ''
    if self.hasInputFromPort('p_level_vals') :
      p_level_vals = self.getInputFromPort('p_level_vals')
    Texture = 0
    if self.hasInputFromPort('Texture') :
      Texture = self.getInputFromPort('Texture')
    ColorMap = 0
    if self.hasInputFromPort('ColorMap') :
      ColorMap = self.getInputFromPort('ColorMap')
    ColorMap2 = 0
    if self.hasInputFromPort('ColorMap2') :
      ColorMap2 = self.getInputFromPort('ColorMap2')
    results = sr_py.ShowTextureVolume(Texture,ColorMap,ColorMap2,p_sampling_rate_hi,p_sampling_rate_lo,p_gradient_min,p_gradient_max,p_adaptive,p_cmap_size,p_sw_raster,p_render_style,p_alpha_scale,p_interp_mode,p_shading,p_ambient,p_diffuse,p_specular,p_shine,p_light,p_blend_res,p_multi_level,p_use_stencil,p_invert_opacity,p_num_clipping_planes,p_show_clipping_widgets,p_level_on,p_level_vals)
    self.setResult('Geometry', results[0])
    self.setResult('ColorMap', results[1])

class scirun_GetCentroidsFromMesh(Module) :
  def compute(self) :
    TetVolField = 0
    if self.hasInputFromPort('TetVolField') :
      TetVolField = self.getInputFromPort('TetVolField')
    results = sr_py.GetCentroidsFromMesh(TetVolField)
    self.setResult('PointCloudField', results)

class scirun_ConvertLatVolDataFromNodeToElem(Module) :
  def compute(self) :
    Node_Field = 0
    if self.hasInputFromPort('Node Field') :
      Node_Field = self.getInputFromPort('Node Field')
    results = sr_py.ConvertLatVolDataFromNodeToElem(Node_Field)
    self.setResult('Elem Field', results)

class scirun_ReadColorMap2D(Module) :
  def compute(self) :
    p_from_env = ''
    if self.hasInputFromPort('p_from_env') :
      p_from_env = self.getInputFromPort('p_from_env')
    Filename = ''
    if self.hasInputFromPort('Filename') :
      Filename = self.getInputFromPort('Filename')
    results = sr_py.ReadColorMap2D(Filename,p_from_env)
    self.setResult('Output Data', results[0])
    self.setResult('Filename', results[1])

class scirun_GetColumnOrRowFromMatrix(Module) :
  def compute(self) :
    p_row_or_col = 'row'
    if self.hasInputFromPort('p_row_or_col') :
      p_row_or_col = self.getInputFromPort('p_row_or_col')
    p_selectable_min = 0
    if self.hasInputFromPort('p_selectable_min') :
      p_selectable_min = self.getInputFromPort('p_selectable_min')
    p_selectable_max = 100
    if self.hasInputFromPort('p_selectable_max') :
      p_selectable_max = self.getInputFromPort('p_selectable_max')
    p_selectable_inc = 1
    if self.hasInputFromPort('p_selectable_inc') :
      p_selectable_inc = self.getInputFromPort('p_selectable_inc')
    p_selectable_units = ''
    if self.hasInputFromPort('p_selectable_units') :
      p_selectable_units = self.getInputFromPort('p_selectable_units')
    p_range_min = 0
    if self.hasInputFromPort('p_range_min') :
      p_range_min = self.getInputFromPort('p_range_min')
    p_range_max = 100
    if self.hasInputFromPort('p_range_max') :
      p_range_max = self.getInputFromPort('p_range_max')
    p_playmode = 'once'
    if self.hasInputFromPort('p_playmode') :
      p_playmode = self.getInputFromPort('p_playmode')
    p_current = 0
    if self.hasInputFromPort('p_current') :
      p_current = self.getInputFromPort('p_current')
    p_execmode = 'init'
    if self.hasInputFromPort('p_execmode') :
      p_execmode = self.getInputFromPort('p_execmode')
    p_delay = 0
    if self.hasInputFromPort('p_delay') :
      p_delay = self.getInputFromPort('p_delay')
    p_inc_amount = 1
    if self.hasInputFromPort('p_inc_amount') :
      p_inc_amount = self.getInputFromPort('p_inc_amount')
    p_send_amount = 1
    if self.hasInputFromPort('p_send_amount') :
      p_send_amount = self.getInputFromPort('p_send_amount')
    p_data_series_done = 0
    if self.hasInputFromPort('p_data_series_done') :
      p_data_series_done = self.getInputFromPort('p_data_series_done')
    Matrix = 0
    if self.hasInputFromPort('Matrix') :
      Matrix = self.getInputFromPort('Matrix')
    Weight_Vector = 0
    if self.hasInputFromPort('Weight Vector') :
      Weight_Vector = self.getInputFromPort('Weight Vector')
    Current_Index = 0
    if self.hasInputFromPort('Current Index') :
      Current_Index = self.getInputFromPort('Current Index')
    results = sr_py.GetColumnOrRowFromMatrix(Matrix,Weight_Vector,Current_Index,p_row_or_col,p_selectable_min,p_selectable_max,p_selectable_inc,p_selectable_units,p_range_min,p_range_max,p_playmode,p_current,p_execmode,p_delay,p_inc_amount,p_send_amount,p_data_series_done)
    self.setResult('Vector', results[0])
    self.setResult('Selected Index', results[1])

class scirun_ExtractIsosurfaceByFunction(Module) :
  def compute(self) :
    p_function = 'result = sqrt(x*x + y*y);'
    if self.hasInputFromPort('p_function') :
      p_function = self.getInputFromPort('p_function')
    p_zero_checks = 0
    if self.hasInputFromPort('p_zero_checks') :
      p_zero_checks = self.getInputFromPort('p_zero_checks')
    p_slice_value_min = 0.0
    if self.hasInputFromPort('p_slice_value_min') :
      p_slice_value_min = self.getInputFromPort('p_slice_value_min')
    p_slice_value_max = 99.0
    if self.hasInputFromPort('p_slice_value_max') :
      p_slice_value_max = self.getInputFromPort('p_slice_value_max')
    p_slice_value = 0.0
    if self.hasInputFromPort('p_slice_value') :
      p_slice_value = self.getInputFromPort('p_slice_value')
    p_slice_value_typed = 0.0
    if self.hasInputFromPort('p_slice_value_typed') :
      p_slice_value_typed = self.getInputFromPort('p_slice_value_typed')
    p_slice_value_quantity = 1
    if self.hasInputFromPort('p_slice_value_quantity') :
      p_slice_value_quantity = self.getInputFromPort('p_slice_value_quantity')
    p_quantity_range = 'field'
    if self.hasInputFromPort('p_quantity_range') :
      p_quantity_range = self.getInputFromPort('p_quantity_range')
    p_quantity_clusive = 'exclusive'
    if self.hasInputFromPort('p_quantity_clusive') :
      p_quantity_clusive = self.getInputFromPort('p_quantity_clusive')
    p_quantity_min = 0.0
    if self.hasInputFromPort('p_quantity_min') :
      p_quantity_min = self.getInputFromPort('p_quantity_min')
    p_quantity_max = 100.0
    if self.hasInputFromPort('p_quantity_max') :
      p_quantity_max = self.getInputFromPort('p_quantity_max')
    p_quantity_list = ''
    if self.hasInputFromPort('p_quantity_list') :
      p_quantity_list = self.getInputFromPort('p_quantity_list')
    p_slice_value_list = 'No values present.'
    if self.hasInputFromPort('p_slice_value_list') :
      p_slice_value_list = self.getInputFromPort('p_slice_value_list')
    p_matrix_list = 'No matrix present - execution needed.'
    if self.hasInputFromPort('p_matrix_list') :
      p_matrix_list = self.getInputFromPort('p_matrix_list')
    p_algorithm = 0
    if self.hasInputFromPort('p_algorithm') :
      p_algorithm = self.getInputFromPort('p_algorithm')
    p_build_trisurf = 1
    if self.hasInputFromPort('p_build_trisurf') :
      p_build_trisurf = self.getInputFromPort('p_build_trisurf')
    p_build_geom = 1
    if self.hasInputFromPort('p_build_geom') :
      p_build_geom = self.getInputFromPort('p_build_geom')
    p_active_slice_value_selection_tab = '0'
    if self.hasInputFromPort('p_active_slice_value_selection_tab') :
      p_active_slice_value_selection_tab = self.getInputFromPort('p_active_slice_value_selection_tab')
    p_active_tab = '0'
    if self.hasInputFromPort('p_active_tab') :
      p_active_tab = self.getInputFromPort('p_active_tab')
    p_update_type = 'On Release'
    if self.hasInputFromPort('p_update_type') :
      p_update_type = self.getInputFromPort('p_update_type')
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    Optional_Slice_values = 0
    if self.hasInputFromPort('Optional Slice values') :
      Optional_Slice_values = self.getInputFromPort('Optional Slice values')
    results = sr_py.ExtractIsosurfaceByFunction(Input_Field,Optional_Slice_values,p_function,p_zero_checks,p_slice_value_min,p_slice_value_max,p_slice_value,p_slice_value_typed,p_slice_value_quantity,p_quantity_range,p_quantity_clusive,p_quantity_min,p_quantity_max,p_quantity_list,p_slice_value_list,p_matrix_list,p_algorithm,p_build_trisurf,p_build_geom,p_active_slice_value_selection_tab,p_active_tab,p_update_type)
    self.setResult('Output Field', results)

class scirun_BuildNoiseColumnMatrix(Module) :
  def compute(self) :
    p_snr = 10.0
    if self.hasInputFromPort('p_snr') :
      p_snr = self.getInputFromPort('p_snr')
    Signal = 0
    if self.hasInputFromPort('Signal') :
      Signal = self.getInputFromPort('Signal')
    results = sr_py.BuildNoiseColumnMatrix(Signal,p_snr)
    self.setResult('Noise', results)

class scirun_MergeTriSurfs(Module) :
  def compute(self) :
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    results = sr_py.MergeTriSurfs(Input_Field)
    self.setResult('Output Field', results)

class scirun_ReadString(Module) :
  def compute(self) :
    p_from_env = ''
    if self.hasInputFromPort('p_from_env') :
      p_from_env = self.getInputFromPort('p_from_env')
    Filename = ''
    if self.hasInputFromPort('Filename') :
      Filename = self.getInputFromPort('Filename')
    results = sr_py.ReadString(Filename,p_from_env)
    self.setResult('Output Data', results[0])
    self.setResult('Filename', results[1])

class scirun_InterfaceWithTetGen(Module) :
  def compute(self) :
    p_switch = 'pqYAz'
    if self.hasInputFromPort('p_switch') :
      p_switch = self.getInputFromPort('p_switch')
    Main = 0
    if self.hasInputFromPort('Main') :
      Main = self.getInputFromPort('Main')
    Points = 0
    if self.hasInputFromPort('Points') :
      Points = self.getInputFromPort('Points')
    Region_Attribs = 0
    if self.hasInputFromPort('Region Attribs') :
      Region_Attribs = self.getInputFromPort('Region Attribs')
    Regions = 0
    if self.hasInputFromPort('Regions') :
      Regions = self.getInputFromPort('Regions')
    results = sr_py.InterfaceWithTetGen(Main,Points,Region_Attribs,Regions,p_switch)
    self.setResult('TetVol', results)

class scirun_CalculateMeshNodes(Module) :
  def compute(self) :
    p_function = 'NEWPOS = 3*POS;'
    if self.hasInputFromPort('p_function') :
      p_function = self.getInputFromPort('p_function')
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    Function = ''
    if self.hasInputFromPort('Function') :
      Function = self.getInputFromPort('Function')
    Array = 0
    if self.hasInputFromPort('Array') :
      Array = self.getInputFromPort('Array')
    results = sr_py.CalculateMeshNodes(Field,Function,Array,p_function)
    self.setResult('Field', results)

class scirun_CreateImage(Module) :
  def compute(self) :
    p_sizex = 20
    if self.hasInputFromPort('p_sizex') :
      p_sizex = self.getInputFromPort('p_sizex')
    p_sizey = 20
    if self.hasInputFromPort('p_sizey') :
      p_sizey = self.getInputFromPort('p_sizey')
    p_sizez = 2
    if self.hasInputFromPort('p_sizez') :
      p_sizez = self.getInputFromPort('p_sizez')
    p_z_value = 0
    if self.hasInputFromPort('p_z_value') :
      p_z_value = self.getInputFromPort('p_z_value')
    p_auto_size = 0
    if self.hasInputFromPort('p_auto_size') :
      p_auto_size = self.getInputFromPort('p_auto_size')
    p_axis = 0
    if self.hasInputFromPort('p_axis') :
      p_axis = self.getInputFromPort('p_axis')
    p_padpercent = 0.0
    if self.hasInputFromPort('p_padpercent') :
      p_padpercent = self.getInputFromPort('p_padpercent')
    p_pos = 0.0
    if self.hasInputFromPort('p_pos') :
      p_pos = self.getInputFromPort('p_pos')
    p_data_at = 'Nodes'
    if self.hasInputFromPort('p_data_at') :
      p_data_at = self.getInputFromPort('p_data_at')
    p_update_type = 'On Release'
    if self.hasInputFromPort('p_update_type') :
      p_update_type = self.getInputFromPort('p_update_type')
    p_corigin_x = '0.0'
    if self.hasInputFromPort('p_corigin_x') :
      p_corigin_x = self.getInputFromPort('p_corigin_x')
    p_corigin_y = '0.0'
    if self.hasInputFromPort('p_corigin_y') :
      p_corigin_y = self.getInputFromPort('p_corigin_y')
    p_corigin_z = '0.0'
    if self.hasInputFromPort('p_corigin_z') :
      p_corigin_z = self.getInputFromPort('p_corigin_z')
    p_cnormal_x = '1.0'
    if self.hasInputFromPort('p_cnormal_x') :
      p_cnormal_x = self.getInputFromPort('p_cnormal_x')
    p_cnormal_y = '1.0'
    if self.hasInputFromPort('p_cnormal_y') :
      p_cnormal_y = self.getInputFromPort('p_cnormal_y')
    p_cnormal_z = '1.0'
    if self.hasInputFromPort('p_cnormal_z') :
      p_cnormal_z = self.getInputFromPort('p_cnormal_z')
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    results = sr_py.CreateImage(Input_Field,p_sizex,p_sizey,p_sizez,p_z_value,p_auto_size,p_axis,p_padpercent,p_pos,p_data_at,p_update_type,p_corigin_x,p_corigin_y,p_corigin_z,p_cnormal_x,p_cnormal_y,p_cnormal_z)
    self.setResult('Output Sample Field', results)

class scirun_CalculateFieldDataCompiled(Module) :
  def compute(self) :
    p_outputdatatype = 'port 0 input'
    if self.hasInputFromPort('p_outputdatatype') :
      p_outputdatatype = self.getInputFromPort('p_outputdatatype')
    p_function = 'result = v0 + v1 + v2;'
    if self.hasInputFromPort('p_function') :
      p_function = self.getInputFromPort('p_function')
    p_cache = 0
    if self.hasInputFromPort('p_cache') :
      p_cache = self.getInputFromPort('p_cache')
    Function = ''
    if self.hasInputFromPort('Function') :
      Function = self.getInputFromPort('Function')
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    results = sr_py.CalculateFieldDataCompiled(Function,Input_Field,p_outputdatatype,p_function,p_cache)
    self.setResult('Output Field', results)

class scirun_ReadColorMap(Module) :
  def compute(self) :
    p_from_env = ''
    if self.hasInputFromPort('p_from_env') :
      p_from_env = self.getInputFromPort('p_from_env')
    Filename = ''
    if self.hasInputFromPort('Filename') :
      Filename = self.getInputFromPort('Filename')
    results = sr_py.ReadColorMap(Filename,p_from_env)
    self.setResult('Output Data', results[0])
    self.setResult('Filename', results[1])

class scirun_MapFieldDataFromElemToNode(Module) :
  def compute(self) :
    p_method = 'Interpolate'
    if self.hasInputFromPort('p_method') :
      p_method = self.getInputFromPort('p_method')
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    results = sr_py.MapFieldDataFromElemToNode(Field,p_method)
    self.setResult('Field', results)

class scirun_ShowFieldGlyphs(Module) :
  def compute(self) :
    p_scalars_has_data = 0
    if self.hasInputFromPort('p_scalars_has_data') :
      p_scalars_has_data = self.getInputFromPort('p_scalars_has_data')
    p_scalars_on = 0
    if self.hasInputFromPort('p_scalars_on') :
      p_scalars_on = self.getInputFromPort('p_scalars_on')
    p_scalars_display_type = 'Spheres'
    if self.hasInputFromPort('p_scalars_display_type') :
      p_scalars_display_type = self.getInputFromPort('p_scalars_display_type')
    p_scalars_transparency = 0
    if self.hasInputFromPort('p_scalars_transparency') :
      p_scalars_transparency = self.getInputFromPort('p_scalars_transparency')
    p_scalars_normalize = 0
    if self.hasInputFromPort('p_scalars_normalize') :
      p_scalars_normalize = self.getInputFromPort('p_scalars_normalize')
    p_scalars_color_type = 1
    if self.hasInputFromPort('p_scalars_color_type') :
      p_scalars_color_type = self.getInputFromPort('p_scalars_color_type')
    p_scalars_resolution = 6
    if self.hasInputFromPort('p_scalars_resolution') :
      p_scalars_resolution = self.getInputFromPort('p_scalars_resolution')
    p_vectors_has_data = 0
    if self.hasInputFromPort('p_vectors_has_data') :
      p_vectors_has_data = self.getInputFromPort('p_vectors_has_data')
    p_vectors_on = 0
    if self.hasInputFromPort('p_vectors_on') :
      p_vectors_on = self.getInputFromPort('p_vectors_on')
    p_vectors_display_type = 'Arrows'
    if self.hasInputFromPort('p_vectors_display_type') :
      p_vectors_display_type = self.getInputFromPort('p_vectors_display_type')
    p_vectors_transparency = 0
    if self.hasInputFromPort('p_vectors_transparency') :
      p_vectors_transparency = self.getInputFromPort('p_vectors_transparency')
    p_vectors_normalize = 0
    if self.hasInputFromPort('p_vectors_normalize') :
      p_vectors_normalize = self.getInputFromPort('p_vectors_normalize')
    p_vectors_bidirectional = 0
    if self.hasInputFromPort('p_vectors_bidirectional') :
      p_vectors_bidirectional = self.getInputFromPort('p_vectors_bidirectional')
    p_vectors_color_type = 1
    if self.hasInputFromPort('p_vectors_color_type') :
      p_vectors_color_type = self.getInputFromPort('p_vectors_color_type')
    p_vectors_resolution = 6
    if self.hasInputFromPort('p_vectors_resolution') :
      p_vectors_resolution = self.getInputFromPort('p_vectors_resolution')
    p_tensors_has_data = 0
    if self.hasInputFromPort('p_tensors_has_data') :
      p_tensors_has_data = self.getInputFromPort('p_tensors_has_data')
    p_tensors_on = 0
    if self.hasInputFromPort('p_tensors_on') :
      p_tensors_on = self.getInputFromPort('p_tensors_on')
    p_tensors_display_type = 'Colored Boxes'
    if self.hasInputFromPort('p_tensors_display_type') :
      p_tensors_display_type = self.getInputFromPort('p_tensors_display_type')
    p_tensors_transparency = 0
    if self.hasInputFromPort('p_tensors_transparency') :
      p_tensors_transparency = self.getInputFromPort('p_tensors_transparency')
    p_tensors_normalize = 0
    if self.hasInputFromPort('p_tensors_normalize') :
      p_tensors_normalize = self.getInputFromPort('p_tensors_normalize')
    p_tensors_color_type = 1
    if self.hasInputFromPort('p_tensors_color_type') :
      p_tensors_color_type = self.getInputFromPort('p_tensors_color_type')
    p_tensors_resolution = 6
    if self.hasInputFromPort('p_tensors_resolution') :
      p_tensors_resolution = self.getInputFromPort('p_tensors_resolution')
    p_tensors_emphasis = 0.825
    if self.hasInputFromPort('p_tensors_emphasis') :
      p_tensors_emphasis = self.getInputFromPort('p_tensors_emphasis')
    p_secondary_has_data = 0
    if self.hasInputFromPort('p_secondary_has_data') :
      p_secondary_has_data = self.getInputFromPort('p_secondary_has_data')
    p_secondary_on = 0
    if self.hasInputFromPort('p_secondary_on') :
      p_secondary_on = self.getInputFromPort('p_secondary_on')
    p_secondary_display_type = 'Major Radius'
    if self.hasInputFromPort('p_secondary_display_type') :
      p_secondary_display_type = self.getInputFromPort('p_secondary_display_type')
    p_secondary_color_type = 0
    if self.hasInputFromPort('p_secondary_color_type') :
      p_secondary_color_type = self.getInputFromPort('p_secondary_color_type')
    p_secondary_alpha = 0
    if self.hasInputFromPort('p_secondary_alpha') :
      p_secondary_alpha = self.getInputFromPort('p_secondary_alpha')
    p_secondary_value = 1
    if self.hasInputFromPort('p_secondary_value') :
      p_secondary_value = self.getInputFromPort('p_secondary_value')
    p_tertiary_has_data = 0
    if self.hasInputFromPort('p_tertiary_has_data') :
      p_tertiary_has_data = self.getInputFromPort('p_tertiary_has_data')
    p_tertiary_on = 0
    if self.hasInputFromPort('p_tertiary_on') :
      p_tertiary_on = self.getInputFromPort('p_tertiary_on')
    p_tertiary_display_type = 'Minor Radius'
    if self.hasInputFromPort('p_tertiary_display_type') :
      p_tertiary_display_type = self.getInputFromPort('p_tertiary_display_type')
    p_tertiary_color_type = 0
    if self.hasInputFromPort('p_tertiary_color_type') :
      p_tertiary_color_type = self.getInputFromPort('p_tertiary_color_type')
    p_tertiary_alpha = 0
    if self.hasInputFromPort('p_tertiary_alpha') :
      p_tertiary_alpha = self.getInputFromPort('p_tertiary_alpha')
    p_tertiary_value = 1
    if self.hasInputFromPort('p_tertiary_value') :
      p_tertiary_value = self.getInputFromPort('p_tertiary_value')
    p_text_on = 0
    if self.hasInputFromPort('p_text_on') :
      p_text_on = self.getInputFromPort('p_text_on')
    p_text_color_type = 0
    if self.hasInputFromPort('p_text_color_type') :
      p_text_color_type = self.getInputFromPort('p_text_color_type')
    p_text_color_r = 1.0
    if self.hasInputFromPort('p_text_color_r') :
      p_text_color_r = self.getInputFromPort('p_text_color_r')
    p_text_color_g = 1.0
    if self.hasInputFromPort('p_text_color_g') :
      p_text_color_g = self.getInputFromPort('p_text_color_g')
    p_text_color_b = 1.0
    if self.hasInputFromPort('p_text_color_b') :
      p_text_color_b = self.getInputFromPort('p_text_color_b')
    p_text_backface_cull = 0
    if self.hasInputFromPort('p_text_backface_cull') :
      p_text_backface_cull = self.getInputFromPort('p_text_backface_cull')
    p_text_always_visible = 0
    if self.hasInputFromPort('p_text_always_visible') :
      p_text_always_visible = self.getInputFromPort('p_text_always_visible')
    p_text_fontsize = 0
    if self.hasInputFromPort('p_text_fontsize') :
      p_text_fontsize = self.getInputFromPort('p_text_fontsize')
    p_text_precision = 3
    if self.hasInputFromPort('p_text_precision') :
      p_text_precision = self.getInputFromPort('p_text_precision')
    p_text_render_locations = 0
    if self.hasInputFromPort('p_text_render_locations') :
      p_text_render_locations = self.getInputFromPort('p_text_render_locations')
    p_text_show_data = 1
    if self.hasInputFromPort('p_text_show_data') :
      p_text_show_data = self.getInputFromPort('p_text_show_data')
    p_text_show_nodes = 0
    if self.hasInputFromPort('p_text_show_nodes') :
      p_text_show_nodes = self.getInputFromPort('p_text_show_nodes')
    p_text_show_edges = 0
    if self.hasInputFromPort('p_text_show_edges') :
      p_text_show_edges = self.getInputFromPort('p_text_show_edges')
    p_text_show_faces = 0
    if self.hasInputFromPort('p_text_show_faces') :
      p_text_show_faces = self.getInputFromPort('p_text_show_faces')
    p_text_show_cells = 0
    if self.hasInputFromPort('p_text_show_cells') :
      p_text_show_cells = self.getInputFromPort('p_text_show_cells')
    p_def_color_r = 0.5
    if self.hasInputFromPort('p_def_color_r') :
      p_def_color_r = self.getInputFromPort('p_def_color_r')
    p_def_color_g = 0.5
    if self.hasInputFromPort('p_def_color_g') :
      p_def_color_g = self.getInputFromPort('p_def_color_g')
    p_def_color_b = 0.5
    if self.hasInputFromPort('p_def_color_b') :
      p_def_color_b = self.getInputFromPort('p_def_color_b')
    p_def_color_a = 0.75
    if self.hasInputFromPort('p_def_color_a') :
      p_def_color_a = self.getInputFromPort('p_def_color_a')
    p_active_tab = 'Scalars'
    if self.hasInputFromPort('p_active_tab') :
      p_active_tab = self.getInputFromPort('p_active_tab')
    p_interactive_mode = 'Interactive'
    if self.hasInputFromPort('p_interactive_mode') :
      p_interactive_mode = self.getInputFromPort('p_interactive_mode')
    p_show_progress = 0
    if self.hasInputFromPort('p_show_progress') :
      p_show_progress = self.getInputFromPort('p_show_progress')
    p_field_name = ''
    if self.hasInputFromPort('p_field_name') :
      p_field_name = self.getInputFromPort('p_field_name')
    p_field_name_override = 0
    if self.hasInputFromPort('p_field_name_override') :
      p_field_name_override = self.getInputFromPort('p_field_name_override')
    p_approx_div = 1
    if self.hasInputFromPort('p_approx_div') :
      p_approx_div = self.getInputFromPort('p_approx_div')
    p_use_default_size = 0
    if self.hasInputFromPort('p_use_default_size') :
      p_use_default_size = self.getInputFromPort('p_use_default_size')
    Primary_Data = 0
    if self.hasInputFromPort('Primary Data') :
      Primary_Data = self.getInputFromPort('Primary Data')
    Primary_ColorMap = 0
    if self.hasInputFromPort('Primary ColorMap') :
      Primary_ColorMap = self.getInputFromPort('Primary ColorMap')
    Secondary_Data = 0
    if self.hasInputFromPort('Secondary Data') :
      Secondary_Data = self.getInputFromPort('Secondary Data')
    Secondary_ColorMap = 0
    if self.hasInputFromPort('Secondary ColorMap') :
      Secondary_ColorMap = self.getInputFromPort('Secondary ColorMap')
    Tertiary_Data = 0
    if self.hasInputFromPort('Tertiary Data') :
      Tertiary_Data = self.getInputFromPort('Tertiary Data')
    Tertiary_ColorMap = 0
    if self.hasInputFromPort('Tertiary ColorMap') :
      Tertiary_ColorMap = self.getInputFromPort('Tertiary ColorMap')
    results = sr_py.ShowFieldGlyphs(Primary_Data,Primary_ColorMap,Secondary_Data,Secondary_ColorMap,Tertiary_Data,Tertiary_ColorMap,p_scalars_has_data,p_scalars_on,p_scalars_display_type,p_scalars_transparency,p_scalars_normalize,p_scalars_color_type,p_scalars_resolution,p_vectors_has_data,p_vectors_on,p_vectors_display_type,p_vectors_transparency,p_vectors_normalize,p_vectors_bidirectional,p_vectors_color_type,p_vectors_resolution,p_tensors_has_data,p_tensors_on,p_tensors_display_type,p_tensors_transparency,p_tensors_normalize,p_tensors_color_type,p_tensors_resolution,p_tensors_emphasis,p_secondary_has_data,p_secondary_on,p_secondary_display_type,p_secondary_color_type,p_secondary_alpha,p_secondary_value,p_tertiary_has_data,p_tertiary_on,p_tertiary_display_type,p_tertiary_color_type,p_tertiary_alpha,p_tertiary_value,p_text_on,p_text_color_type,p_text_color_r,p_text_color_g,p_text_color_b,p_text_backface_cull,p_text_always_visible,p_text_fontsize,p_text_precision,p_text_render_locations,p_text_show_data,p_text_show_nodes,p_text_show_edges,p_text_show_faces,p_text_show_cells,p_def_color_r,p_def_color_g,p_def_color_b,p_def_color_a,p_active_tab,p_interactive_mode,p_show_progress,p_field_name,p_field_name_override,p_approx_div,p_use_default_size)
    self.setResult('Scene Graph', results)

class scirun_JoinBundles(Module) :
  def compute(self) :
    bundle = 0
    if self.hasInputFromPort('bundle') :
      bundle = self.getInputFromPort('bundle')
    results = sr_py.JoinBundles(bundle)
    self.setResult('bundle', results)

class scirun_ApplyFilterToFieldData(Module) :
  def compute(self) :
    p_method = 'erodedilate'
    if self.hasInputFromPort('p_method') :
      p_method = self.getInputFromPort('p_method')
    p_ed_method = 'erode'
    if self.hasInputFromPort('p_ed_method') :
      p_ed_method = self.getInputFromPort('p_ed_method')
    p_ed_iterations = 3
    if self.hasInputFromPort('p_ed_iterations') :
      p_ed_iterations = self.getInputFromPort('p_ed_iterations')
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    results = sr_py.ApplyFilterToFieldData(Field,p_method,p_ed_method,p_ed_iterations)
    self.setResult('Field', results)

class scirun_InsertHexVolSheetAlongSurface(Module) :
  def compute(self) :
    p_side = 'side1'
    if self.hasInputFromPort('p_side') :
      p_side = self.getInputFromPort('p_side')
    p_addlayer = 'On'
    if self.hasInputFromPort('p_addlayer') :
      p_addlayer = self.getInputFromPort('p_addlayer')
    HexField = 0
    if self.hasInputFromPort('HexField') :
      HexField = self.getInputFromPort('HexField')
    TriField = 0
    if self.hasInputFromPort('TriField') :
      TriField = self.getInputFromPort('TriField')
    results = sr_py.InsertHexVolSheetAlongSurface(HexField,TriField,p_side,p_addlayer)
    self.setResult('Side1Field', results[0])
    self.setResult('Side2Field', results[1])

class scirun_GetFieldData(Module) :
  def compute(self) :
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    results = sr_py.GetFieldData(Field)
    self.setResult('Data', results)

class scirun_CalculateFieldData2(Module) :
  def compute(self) :
    p_function = 'RESULT = abs(DATA1);'
    if self.hasInputFromPort('p_function') :
      p_function = self.getInputFromPort('p_function')
    p_format = 'Scalar'
    if self.hasInputFromPort('p_format') :
      p_format = self.getInputFromPort('p_format')
    Field1 = 0
    if self.hasInputFromPort('Field1') :
      Field1 = self.getInputFromPort('Field1')
    Field2 = 0
    if self.hasInputFromPort('Field2') :
      Field2 = self.getInputFromPort('Field2')
    Function = ''
    if self.hasInputFromPort('Function') :
      Function = self.getInputFromPort('Function')
    Array = 0
    if self.hasInputFromPort('Array') :
      Array = self.getInputFromPort('Array')
    results = sr_py.CalculateFieldData2(Field1,Field2,Function,Array,p_function,p_format)
    self.setResult('Field', results)

class scirun_ReportBundleInfo(Module) :
  def compute(self) :
    p_tclinfostring = ''
    if self.hasInputFromPort('p_tclinfostring') :
      p_tclinfostring = self.getInputFromPort('p_tclinfostring')
    bundle = 0
    if self.hasInputFromPort('bundle') :
      bundle = self.getInputFromPort('bundle')
    results = sr_py.ReportBundleInfo(bundle,p_tclinfostring)

class scirun_GenerateSinglePointProbeFromField(Module) :
  def compute(self) :
    p_main_frame = ''
    if self.hasInputFromPort('p_main_frame') :
      p_main_frame = self.getInputFromPort('p_main_frame')
    p_locx = 0.0
    if self.hasInputFromPort('p_locx') :
      p_locx = self.getInputFromPort('p_locx')
    p_locy = 0.0
    if self.hasInputFromPort('p_locy') :
      p_locy = self.getInputFromPort('p_locy')
    p_locz = 0.0
    if self.hasInputFromPort('p_locz') :
      p_locz = self.getInputFromPort('p_locz')
    p_value = ''
    if self.hasInputFromPort('p_value') :
      p_value = self.getInputFromPort('p_value')
    p_node = ''
    if self.hasInputFromPort('p_node') :
      p_node = self.getInputFromPort('p_node')
    p_edge = ''
    if self.hasInputFromPort('p_edge') :
      p_edge = self.getInputFromPort('p_edge')
    p_face = ''
    if self.hasInputFromPort('p_face') :
      p_face = self.getInputFromPort('p_face')
    p_cell = ''
    if self.hasInputFromPort('p_cell') :
      p_cell = self.getInputFromPort('p_cell')
    p_show_value = 1
    if self.hasInputFromPort('p_show_value') :
      p_show_value = self.getInputFromPort('p_show_value')
    p_show_node = 1
    if self.hasInputFromPort('p_show_node') :
      p_show_node = self.getInputFromPort('p_show_node')
    p_show_edge = 0
    if self.hasInputFromPort('p_show_edge') :
      p_show_edge = self.getInputFromPort('p_show_edge')
    p_show_face = 0
    if self.hasInputFromPort('p_show_face') :
      p_show_face = self.getInputFromPort('p_show_face')
    p_show_cell = 1
    if self.hasInputFromPort('p_show_cell') :
      p_show_cell = self.getInputFromPort('p_show_cell')
    p_probe_scale = 5.0
    if self.hasInputFromPort('p_probe_scale') :
      p_probe_scale = self.getInputFromPort('p_probe_scale')
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    results = sr_py.GenerateSinglePointProbeFromField(Input_Field,p_main_frame,p_locx,p_locy,p_locz,p_value,p_node,p_edge,p_face,p_cell,p_show_value,p_show_node,p_show_edge,p_show_face,p_show_cell,p_probe_scale)
    self.setResult('GenerateSinglePointProbeFromField Widget', results[0])
    self.setResult('GenerateSinglePointProbeFromField Point', results[1])
    self.setResult('Element Index', results[2])

class scirun_ReportDataArrayMeasure(Module) :
  def compute(self) :
    p_measure = 'Sum'
    if self.hasInputFromPort('p_measure') :
      p_measure = self.getInputFromPort('p_measure')
    Array = 0
    if self.hasInputFromPort('Array') :
      Array = self.getInputFromPort('Array')
    results = sr_py.ReportDataArrayMeasure(Array,p_measure)
    self.setResult('Measure', results)

class scirun_SmoothMesh(Module) :
  def compute(self) :
    Input = 0
    if self.hasInputFromPort('Input') :
      Input = self.getInputFromPort('Input')
    IsoValue = 0
    if self.hasInputFromPort('IsoValue') :
      IsoValue = self.getInputFromPort('IsoValue')
    results = sr_py.SmoothMesh(Input,IsoValue)
    self.setResult('Smoothed', results)

class scirun_InsertPathsIntoBundle(Module) :
  def compute(self) :
    p_path1_name = 'path1'
    if self.hasInputFromPort('p_path1_name') :
      p_path1_name = self.getInputFromPort('p_path1_name')
    p_path2_name = 'path2'
    if self.hasInputFromPort('p_path2_name') :
      p_path2_name = self.getInputFromPort('p_path2_name')
    p_path3_name = 'path3'
    if self.hasInputFromPort('p_path3_name') :
      p_path3_name = self.getInputFromPort('p_path3_name')
    p_path4_name = 'path4'
    if self.hasInputFromPort('p_path4_name') :
      p_path4_name = self.getInputFromPort('p_path4_name')
    p_path5_name = 'path5'
    if self.hasInputFromPort('p_path5_name') :
      p_path5_name = self.getInputFromPort('p_path5_name')
    p_path6_name = 'path6'
    if self.hasInputFromPort('p_path6_name') :
      p_path6_name = self.getInputFromPort('p_path6_name')
    p_replace1 = 1
    if self.hasInputFromPort('p_replace1') :
      p_replace1 = self.getInputFromPort('p_replace1')
    p_replace2 = 1
    if self.hasInputFromPort('p_replace2') :
      p_replace2 = self.getInputFromPort('p_replace2')
    p_replace3 = 1
    if self.hasInputFromPort('p_replace3') :
      p_replace3 = self.getInputFromPort('p_replace3')
    p_replace4 = 1
    if self.hasInputFromPort('p_replace4') :
      p_replace4 = self.getInputFromPort('p_replace4')
    p_replace5 = 1
    if self.hasInputFromPort('p_replace5') :
      p_replace5 = self.getInputFromPort('p_replace5')
    p_replace6 = 1
    if self.hasInputFromPort('p_replace6') :
      p_replace6 = self.getInputFromPort('p_replace6')
    p_bundlename = ''
    if self.hasInputFromPort('p_bundlename') :
      p_bundlename = self.getInputFromPort('p_bundlename')
    bundle = 0
    if self.hasInputFromPort('bundle') :
      bundle = self.getInputFromPort('bundle')
    path1 = 0
    if self.hasInputFromPort('path1') :
      path1 = self.getInputFromPort('path1')
    path2 = 0
    if self.hasInputFromPort('path2') :
      path2 = self.getInputFromPort('path2')
    path3 = 0
    if self.hasInputFromPort('path3') :
      path3 = self.getInputFromPort('path3')
    path4 = 0
    if self.hasInputFromPort('path4') :
      path4 = self.getInputFromPort('path4')
    path5 = 0
    if self.hasInputFromPort('path5') :
      path5 = self.getInputFromPort('path5')
    path6 = 0
    if self.hasInputFromPort('path6') :
      path6 = self.getInputFromPort('path6')
    results = sr_py.InsertPathsIntoBundle(bundle,path1,path2,path3,path4,path5,path6,p_path1_name,p_path2_name,p_path3_name,p_path4_name,p_path5_name,p_path6_name,p_replace1,p_replace2,p_replace3,p_replace4,p_replace5,p_replace6,p_bundlename)
    self.setResult('bundle', results)

class scirun_SplitFileName(Module) :
  def compute(self) :
    Filename = ''
    if self.hasInputFromPort('Filename') :
      Filename = self.getInputFromPort('Filename')
    results = sr_py.SplitFileName(Filename)
    self.setResult('Pathname', results[0])
    self.setResult('Filename Base', results[1])
    self.setResult('Extension', results[2])
    self.setResult('Filename', results[3])

class scirun_CalculateLatVolGradientsAtNodes(Module) :
  def compute(self) :
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    results = sr_py.CalculateLatVolGradientsAtNodes(Input_Field)
    self.setResult('Output Gradient', results)

class scirun_CalculateGradients(Module) :
  def compute(self) :
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    results = sr_py.CalculateGradients(Input_Field)
    self.setResult('Output CalculateGradients', results)

class scirun_GetColorMap2sFromBundle(Module) :
  def compute(self) :
    p_colormap21_name = 'colormap21'
    if self.hasInputFromPort('p_colormap21_name') :
      p_colormap21_name = self.getInputFromPort('p_colormap21_name')
    p_colormap22_name = 'colormap22'
    if self.hasInputFromPort('p_colormap22_name') :
      p_colormap22_name = self.getInputFromPort('p_colormap22_name')
    p_colormap23_name = 'colormap23'
    if self.hasInputFromPort('p_colormap23_name') :
      p_colormap23_name = self.getInputFromPort('p_colormap23_name')
    p_colormap24_name = 'colormap24'
    if self.hasInputFromPort('p_colormap24_name') :
      p_colormap24_name = self.getInputFromPort('p_colormap24_name')
    p_colormap25_name = 'colormap25'
    if self.hasInputFromPort('p_colormap25_name') :
      p_colormap25_name = self.getInputFromPort('p_colormap25_name')
    p_colormap26_name = 'colormap26'
    if self.hasInputFromPort('p_colormap26_name') :
      p_colormap26_name = self.getInputFromPort('p_colormap26_name')
    p_colormap2_selection = ''
    if self.hasInputFromPort('p_colormap2_selection') :
      p_colormap2_selection = self.getInputFromPort('p_colormap2_selection')
    bundle = 0
    if self.hasInputFromPort('bundle') :
      bundle = self.getInputFromPort('bundle')
    results = sr_py.GetColorMap2sFromBundle(bundle,p_colormap21_name,p_colormap22_name,p_colormap23_name,p_colormap24_name,p_colormap25_name,p_colormap26_name,p_colormap2_selection)
    self.setResult('bundle', results[0])
    self.setResult('colormap21', results[1])
    self.setResult('colormap22', results[2])
    self.setResult('colormap23', results[3])
    self.setResult('colormap24', results[4])
    self.setResult('colormap25', results[5])
    self.setResult('colormap26', results[6])

class scirun_ReadMatrix(Module) :
  def compute(self) :
    p_from_env = ''
    if self.hasInputFromPort('p_from_env') :
      p_from_env = self.getInputFromPort('p_from_env')
    Filename = ''
    if self.hasInputFromPort('Filename') :
      Filename = self.getInputFromPort('Filename')
    results = sr_py.ReadMatrix(Filename,p_from_env)
    self.setResult('Output Data', results[0])
    self.setResult('Filename', results[1])

class scirun_GenerateStreamLines(Module) :
  def compute(self) :
    p_stepsize = 0.01
    if self.hasInputFromPort('p_stepsize') :
      p_stepsize = self.getInputFromPort('p_stepsize')
    p_tolerance = 0.0001
    if self.hasInputFromPort('p_tolerance') :
      p_tolerance = self.getInputFromPort('p_tolerance')
    p_maxsteps = 2000
    if self.hasInputFromPort('p_maxsteps') :
      p_maxsteps = self.getInputFromPort('p_maxsteps')
    p_direction = 1
    if self.hasInputFromPort('p_direction') :
      p_direction = self.getInputFromPort('p_direction')
    p_value = 1
    if self.hasInputFromPort('p_value') :
      p_value = self.getInputFromPort('p_value')
    p_remove_colinear_pts = 1
    if self.hasInputFromPort('p_remove_colinear_pts') :
      p_remove_colinear_pts = self.getInputFromPort('p_remove_colinear_pts')
    p_method = 4
    if self.hasInputFromPort('p_method') :
      p_method = self.getInputFromPort('p_method')
    p_nthreads = 1
    if self.hasInputFromPort('p_nthreads') :
      p_nthreads = self.getInputFromPort('p_nthreads')
    p_auto_parameterize = 0
    if self.hasInputFromPort('p_auto_parameterize') :
      p_auto_parameterize = self.getInputFromPort('p_auto_parameterize')
    Vector_Field = 0
    if self.hasInputFromPort('Vector Field') :
      Vector_Field = self.getInputFromPort('Vector Field')
    Seed_Points = 0
    if self.hasInputFromPort('Seed Points') :
      Seed_Points = self.getInputFromPort('Seed Points')
    results = sr_py.GenerateStreamLines(Vector_Field,Seed_Points,p_stepsize,p_tolerance,p_maxsteps,p_direction,p_value,p_remove_colinear_pts,p_method,p_nthreads,p_auto_parameterize)
    self.setResult('Streamlines', results)

class scirun_EditMeshBoundingBox(Module) :
  def compute(self) :
    p_outputcenterx = 0.0
    if self.hasInputFromPort('p_outputcenterx') :
      p_outputcenterx = self.getInputFromPort('p_outputcenterx')
    p_outputcentery = 0.0
    if self.hasInputFromPort('p_outputcentery') :
      p_outputcentery = self.getInputFromPort('p_outputcentery')
    p_outputcenterz = 0.0
    if self.hasInputFromPort('p_outputcenterz') :
      p_outputcenterz = self.getInputFromPort('p_outputcenterz')
    p_outputsizex = 0.0
    if self.hasInputFromPort('p_outputsizex') :
      p_outputsizex = self.getInputFromPort('p_outputsizex')
    p_outputsizey = 0.0
    if self.hasInputFromPort('p_outputsizey') :
      p_outputsizey = self.getInputFromPort('p_outputsizey')
    p_outputsizez = 0.0
    if self.hasInputFromPort('p_outputsizez') :
      p_outputsizez = self.getInputFromPort('p_outputsizez')
    p_useoutputcenter = 0
    if self.hasInputFromPort('p_useoutputcenter') :
      p_useoutputcenter = self.getInputFromPort('p_useoutputcenter')
    p_useoutputsize = 0
    if self.hasInputFromPort('p_useoutputsize') :
      p_useoutputsize = self.getInputFromPort('p_useoutputsize')
    p_box_scale = -1.0
    if self.hasInputFromPort('p_box_scale') :
      p_box_scale = self.getInputFromPort('p_box_scale')
    p_box_mode = 0
    if self.hasInputFromPort('p_box_mode') :
      p_box_mode = self.getInputFromPort('p_box_mode')
    p_box_real_scale = -1.0
    if self.hasInputFromPort('p_box_real_scale') :
      p_box_real_scale = self.getInputFromPort('p_box_real_scale')
    p_box_center_x = '0.0'
    if self.hasInputFromPort('p_box_center_x') :
      p_box_center_x = self.getInputFromPort('p_box_center_x')
    p_box_center_y = '0.0'
    if self.hasInputFromPort('p_box_center_y') :
      p_box_center_y = self.getInputFromPort('p_box_center_y')
    p_box_center_z = '0.0'
    if self.hasInputFromPort('p_box_center_z') :
      p_box_center_z = self.getInputFromPort('p_box_center_z')
    p_box_right_x = '0.0'
    if self.hasInputFromPort('p_box_right_x') :
      p_box_right_x = self.getInputFromPort('p_box_right_x')
    p_box_right_y = '0.0'
    if self.hasInputFromPort('p_box_right_y') :
      p_box_right_y = self.getInputFromPort('p_box_right_y')
    p_box_right_z = '0.0'
    if self.hasInputFromPort('p_box_right_z') :
      p_box_right_z = self.getInputFromPort('p_box_right_z')
    p_box_down_x = '0.0'
    if self.hasInputFromPort('p_box_down_x') :
      p_box_down_x = self.getInputFromPort('p_box_down_x')
    p_box_down_y = '0.0'
    if self.hasInputFromPort('p_box_down_y') :
      p_box_down_y = self.getInputFromPort('p_box_down_y')
    p_box_down_z = '0.0'
    if self.hasInputFromPort('p_box_down_z') :
      p_box_down_z = self.getInputFromPort('p_box_down_z')
    p_box_in_x = '0.0'
    if self.hasInputFromPort('p_box_in_x') :
      p_box_in_x = self.getInputFromPort('p_box_in_x')
    p_box_in_y = '0.0'
    if self.hasInputFromPort('p_box_in_y') :
      p_box_in_y = self.getInputFromPort('p_box_in_y')
    p_box_in_z = '0.0'
    if self.hasInputFromPort('p_box_in_z') :
      p_box_in_z = self.getInputFromPort('p_box_in_z')
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    results = sr_py.EditMeshBoundingBox(Input_Field,p_outputcenterx,p_outputcentery,p_outputcenterz,p_outputsizex,p_outputsizey,p_outputsizez,p_useoutputcenter,p_useoutputsize,p_box_scale,p_box_mode,p_box_real_scale,p_box_center_x,p_box_center_y,p_box_center_z,p_box_right_x,p_box_right_y,p_box_right_z,p_box_down_x,p_box_down_y,p_box_down_z,p_box_in_x,p_box_in_y,p_box_in_z)
    self.setResult('Output Field', results[0])
    self.setResult('Transformation Widget', results[1])
    self.setResult('Transformation Matrix', results[2])

class scirun_PrintStringIntoString(Module) :
  def compute(self) :
    p_formatstring = 'my string: %s'
    if self.hasInputFromPort('p_formatstring') :
      p_formatstring = self.getInputFromPort('p_formatstring')
    Format = ''
    if self.hasInputFromPort('Format') :
      Format = self.getInputFromPort('Format')
    Input = ''
    if self.hasInputFromPort('Input') :
      Input = self.getInputFromPort('Input')
    results = sr_py.PrintStringIntoString(Format,Input,p_formatstring)
    self.setResult('Output', results)

class scirun_GenerateStreamLinesWithPlacementHeuristic(Module) :
  def compute(self) :
    p_numsl = 10
    if self.hasInputFromPort('p_numsl') :
      p_numsl = self.getInputFromPort('p_numsl')
    p_numpts = 10
    if self.hasInputFromPort('p_numpts') :
      p_numpts = self.getInputFromPort('p_numpts')
    p_minper = 0
    if self.hasInputFromPort('p_minper') :
      p_minper = self.getInputFromPort('p_minper')
    p_maxper = 1
    if self.hasInputFromPort('p_maxper') :
      p_maxper = self.getInputFromPort('p_maxper')
    p_ming = 0
    if self.hasInputFromPort('p_ming') :
      p_ming = self.getInputFromPort('p_ming')
    p_maxg = 1
    if self.hasInputFromPort('p_maxg') :
      p_maxg = self.getInputFromPort('p_maxg')
    p_numsamples = 3
    if self.hasInputFromPort('p_numsamples') :
      p_numsamples = self.getInputFromPort('p_numsamples')
    p_method = 0
    if self.hasInputFromPort('p_method') :
      p_method = self.getInputFromPort('p_method')
    p_stepsize = 0.01
    if self.hasInputFromPort('p_stepsize') :
      p_stepsize = self.getInputFromPort('p_stepsize')
    p_stepout = 100
    if self.hasInputFromPort('p_stepout') :
      p_stepout = self.getInputFromPort('p_stepout')
    p_maxsteps = 10000
    if self.hasInputFromPort('p_maxsteps') :
      p_maxsteps = self.getInputFromPort('p_maxsteps')
    p_minmag = 1e-07
    if self.hasInputFromPort('p_minmag') :
      p_minmag = self.getInputFromPort('p_minmag')
    p_direction = 1
    if self.hasInputFromPort('p_direction') :
      p_direction = self.getInputFromPort('p_direction')
    Source = 0
    if self.hasInputFromPort('Source') :
      Source = self.getInputFromPort('Source')
    Weighting = 0
    if self.hasInputFromPort('Weighting') :
      Weighting = self.getInputFromPort('Weighting')
    Flow = 0
    if self.hasInputFromPort('Flow') :
      Flow = self.getInputFromPort('Flow')
    Compare = 0
    if self.hasInputFromPort('Compare') :
      Compare = self.getInputFromPort('Compare')
    Seed_points = 0
    if self.hasInputFromPort('Seed points') :
      Seed_points = self.getInputFromPort('Seed points')
    results = sr_py.GenerateStreamLinesWithPlacementHeuristic(Source,Weighting,Flow,Compare,Seed_points,p_numsl,p_numpts,p_minper,p_maxper,p_ming,p_maxg,p_numsamples,p_method,p_stepsize,p_stepout,p_maxsteps,p_minmag,p_direction)
    self.setResult('Streamlines', results[0])
    self.setResult('Render', results[1])

class scirun_CalculateSignedDistanceToField(Module) :
  def compute(self) :
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    ObjectField = 0
    if self.hasInputFromPort('ObjectField') :
      ObjectField = self.getInputFromPort('ObjectField')
    results = sr_py.CalculateSignedDistanceToField(Field,ObjectField)
    self.setResult('SignedDistanceField', results)

class scirun_SetFieldDataValues(Module) :
  def compute(self) :
    p_newval = 1.0
    if self.hasInputFromPort('p_newval') :
      p_newval = self.getInputFromPort('p_newval')
    InField = 0
    if self.hasInputFromPort('InField') :
      InField = self.getInputFromPort('InField')
    results = sr_py.SetFieldDataValues(InField,p_newval)
    self.setResult('OutField', results)

class scirun_EvaluateLinAlgUnary(Module) :
  def compute(self) :
    p_op = 'Function'
    if self.hasInputFromPort('p_op') :
      p_op = self.getInputFromPort('p_op')
    p_function = 'x+10'
    if self.hasInputFromPort('p_function') :
      p_function = self.getInputFromPort('p_function')
    Input = 0
    if self.hasInputFromPort('Input') :
      Input = self.getInputFromPort('Input')
    results = sr_py.EvaluateLinAlgUnary(Input,p_op,p_function)
    self.setResult('Output', results)

class scirun_GetSubmatrix(Module) :
  def compute(self) :
    p_mincol = '---'
    if self.hasInputFromPort('p_mincol') :
      p_mincol = self.getInputFromPort('p_mincol')
    p_maxcol = '---'
    if self.hasInputFromPort('p_maxcol') :
      p_maxcol = self.getInputFromPort('p_maxcol')
    p_minrow = '---'
    if self.hasInputFromPort('p_minrow') :
      p_minrow = self.getInputFromPort('p_minrow')
    p_maxrow = '---'
    if self.hasInputFromPort('p_maxrow') :
      p_maxrow = self.getInputFromPort('p_maxrow')
    p_nrow = '??'
    if self.hasInputFromPort('p_nrow') :
      p_nrow = self.getInputFromPort('p_nrow')
    p_ncol = '??'
    if self.hasInputFromPort('p_ncol') :
      p_ncol = self.getInputFromPort('p_ncol')
    Input_Matrix = 0
    if self.hasInputFromPort('Input Matrix') :
      Input_Matrix = self.getInputFromPort('Input Matrix')
    Optional_Range_Bounds = 0
    if self.hasInputFromPort('Optional Range Bounds') :
      Optional_Range_Bounds = self.getInputFromPort('Optional Range Bounds')
    results = sr_py.GetSubmatrix(Input_Matrix,Optional_Range_Bounds,p_mincol,p_maxcol,p_minrow,p_maxrow,p_nrow,p_ncol)
    self.setResult('Output Matrix', results)

class scirun_InsertMatricesIntoBundle(Module) :
  def compute(self) :
    p_matrix1_name = 'matrix1'
    if self.hasInputFromPort('p_matrix1_name') :
      p_matrix1_name = self.getInputFromPort('p_matrix1_name')
    p_matrix2_name = 'matrix2'
    if self.hasInputFromPort('p_matrix2_name') :
      p_matrix2_name = self.getInputFromPort('p_matrix2_name')
    p_matrix3_name = 'matrix3'
    if self.hasInputFromPort('p_matrix3_name') :
      p_matrix3_name = self.getInputFromPort('p_matrix3_name')
    p_matrix4_name = 'matrix4'
    if self.hasInputFromPort('p_matrix4_name') :
      p_matrix4_name = self.getInputFromPort('p_matrix4_name')
    p_matrix5_name = 'matrix5'
    if self.hasInputFromPort('p_matrix5_name') :
      p_matrix5_name = self.getInputFromPort('p_matrix5_name')
    p_matrix6_name = 'matrix6'
    if self.hasInputFromPort('p_matrix6_name') :
      p_matrix6_name = self.getInputFromPort('p_matrix6_name')
    p_replace1 = 1
    if self.hasInputFromPort('p_replace1') :
      p_replace1 = self.getInputFromPort('p_replace1')
    p_replace2 = 1
    if self.hasInputFromPort('p_replace2') :
      p_replace2 = self.getInputFromPort('p_replace2')
    p_replace3 = 1
    if self.hasInputFromPort('p_replace3') :
      p_replace3 = self.getInputFromPort('p_replace3')
    p_replace4 = 1
    if self.hasInputFromPort('p_replace4') :
      p_replace4 = self.getInputFromPort('p_replace4')
    p_replace5 = 1
    if self.hasInputFromPort('p_replace5') :
      p_replace5 = self.getInputFromPort('p_replace5')
    p_replace6 = 1
    if self.hasInputFromPort('p_replace6') :
      p_replace6 = self.getInputFromPort('p_replace6')
    p_bundlename = ''
    if self.hasInputFromPort('p_bundlename') :
      p_bundlename = self.getInputFromPort('p_bundlename')
    bundle = 0
    if self.hasInputFromPort('bundle') :
      bundle = self.getInputFromPort('bundle')
    matrix1 = 0
    if self.hasInputFromPort('matrix1') :
      matrix1 = self.getInputFromPort('matrix1')
    matrix2 = 0
    if self.hasInputFromPort('matrix2') :
      matrix2 = self.getInputFromPort('matrix2')
    matrix3 = 0
    if self.hasInputFromPort('matrix3') :
      matrix3 = self.getInputFromPort('matrix3')
    matrix4 = 0
    if self.hasInputFromPort('matrix4') :
      matrix4 = self.getInputFromPort('matrix4')
    matrix5 = 0
    if self.hasInputFromPort('matrix5') :
      matrix5 = self.getInputFromPort('matrix5')
    matrix6 = 0
    if self.hasInputFromPort('matrix6') :
      matrix6 = self.getInputFromPort('matrix6')
    results = sr_py.InsertMatricesIntoBundle(bundle,matrix1,matrix2,matrix3,matrix4,matrix5,matrix6,p_matrix1_name,p_matrix2_name,p_matrix3_name,p_matrix4_name,p_matrix5_name,p_matrix6_name,p_replace1,p_replace2,p_replace3,p_replace4,p_replace5,p_replace6,p_bundlename)
    self.setResult('bundle', results)

class scirun_CalculateInsideWhichField(Module) :
  def compute(self) :
    p_outputbasis = 'same as input'
    if self.hasInputFromPort('p_outputbasis') :
      p_outputbasis = self.getInputFromPort('p_outputbasis')
    p_outputtype = 'double'
    if self.hasInputFromPort('p_outputtype') :
      p_outputtype = self.getInputFromPort('p_outputtype')
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    Object = 0
    if self.hasInputFromPort('Object') :
      Object = self.getInputFromPort('Object')
    results = sr_py.CalculateInsideWhichField(Field,Object,p_outputbasis,p_outputtype)
    self.setResult('Field', results)

class scirun_WriteString(Module) :
  def compute(self) :
    p_filetype = 'Binary'
    if self.hasInputFromPort('p_filetype') :
      p_filetype = self.getInputFromPort('p_filetype')
    p_confirm = '0'
    if self.hasInputFromPort('p_confirm') :
      p_confirm = self.getInputFromPort('p_confirm')
    p_confirm_once = '0'
    if self.hasInputFromPort('p_confirm_once') :
      p_confirm_once = self.getInputFromPort('p_confirm_once')
    String = ''
    if self.hasInputFromPort('String') :
      String = self.getInputFromPort('String')
    Filename = ''
    if self.hasInputFromPort('Filename') :
      Filename = self.getInputFromPort('Filename')
    results = sr_py.WriteString(String,Filename,p_filetype,p_confirm,p_confirm_once)

class scirun_TimeControls(Module) :
  def compute(self) :
    p_execmode = 'init'
    if self.hasInputFromPort('p_execmode') :
      p_execmode = self.getInputFromPort('p_execmode')
    p_scale_factor = 1.0
    if self.hasInputFromPort('p_scale_factor') :
      p_scale_factor = self.getInputFromPort('p_scale_factor')
    results = sr_py.TimeControls(p_execmode,p_scale_factor)
    self.setResult('time', results)

class scirun_InterfaceWithCubit(Module) :
  def compute(self) :
    p_cubitdir = '.'
    if self.hasInputFromPort('p_cubitdir') :
      p_cubitdir = self.getInputFromPort('p_cubitdir')
    p_ncdump = 'ncdump'
    if self.hasInputFromPort('p_ncdump') :
      p_ncdump = self.getInputFromPort('p_ncdump')
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    PointCloudField = 0
    if self.hasInputFromPort('PointCloudField') :
      PointCloudField = self.getInputFromPort('PointCloudField')
    results = sr_py.InterfaceWithCubit(Field,PointCloudField,p_cubitdir,p_ncdump)
    self.setResult('Field', results)

class scirun_AppendDataArrays(Module) :
  def compute(self) :
    Array = 0
    if self.hasInputFromPort('Array') :
      Array = self.getInputFromPort('Array')
    results = sr_py.AppendDataArrays(Array)
    self.setResult('Array', results)

class scirun_ReadPath(Module) :
  def compute(self) :
    p_from_env = ''
    if self.hasInputFromPort('p_from_env') :
      p_from_env = self.getInputFromPort('p_from_env')
    Filename = ''
    if self.hasInputFromPort('Filename') :
      Filename = self.getInputFromPort('Filename')
    results = sr_py.ReadPath(Filename,p_from_env)
    self.setResult('Output Data', results[0])
    self.setResult('Filename', results[1])

class scirun_CreateString(Module) :
  def compute(self) :
    p_inputstring = ''
    if self.hasInputFromPort('p_inputstring') :
      p_inputstring = self.getInputFromPort('p_inputstring')
    results = sr_py.CreateString(p_inputstring)
    self.setResult('Output', results)

class scirun_ClipFieldByFunction(Module) :
  def compute(self) :
    p_mode = 'allnodes'
    if self.hasInputFromPort('p_mode') :
      p_mode = self.getInputFromPort('p_mode')
    p_function = 'return (x < 0);'
    if self.hasInputFromPort('p_function') :
      p_function = self.getInputFromPort('p_function')
    Function = ''
    if self.hasInputFromPort('Function') :
      Function = self.getInputFromPort('Function')
    Input = 0
    if self.hasInputFromPort('Input') :
      Input = self.getInputFromPort('Input')
    results = sr_py.ClipFieldByFunction(Function,Input,p_mode,p_function)
    self.setResult('Clipped', results[0])
    self.setResult('Mapping', results[1])
    self.setResult('MaskVector', results[2])

class scirun_CreateTensorArray(Module) :
  def compute(self) :
    EigenVector1 = 0
    if self.hasInputFromPort('EigenVector1') :
      EigenVector1 = self.getInputFromPort('EigenVector1')
    EigenVector2 = 0
    if self.hasInputFromPort('EigenVector2') :
      EigenVector2 = self.getInputFromPort('EigenVector2')
    EigenValue1 = 0
    if self.hasInputFromPort('EigenValue1') :
      EigenValue1 = self.getInputFromPort('EigenValue1')
    EigenValue2 = 0
    if self.hasInputFromPort('EigenValue2') :
      EigenValue2 = self.getInputFromPort('EigenValue2')
    EigenValue3 = 0
    if self.hasInputFromPort('EigenValue3') :
      EigenValue3 = self.getInputFromPort('EigenValue3')
    results = sr_py.CreateTensorArray(EigenVector1,EigenVector2,EigenValue1,EigenValue2,EigenValue3)
    self.setResult('TensorArray', results)

class scirun_WriteField(Module) :
  def compute(self) :
    p_filetype = 'Binary'
    if self.hasInputFromPort('p_filetype') :
      p_filetype = self.getInputFromPort('p_filetype')
    p_confirm = '0'
    if self.hasInputFromPort('p_confirm') :
      p_confirm = self.getInputFromPort('p_confirm')
    p_confirm_once = '0'
    if self.hasInputFromPort('p_confirm_once') :
      p_confirm_once = self.getInputFromPort('p_confirm_once')
    p_exporttype = ''
    if self.hasInputFromPort('p_exporttype') :
      p_exporttype = self.getInputFromPort('p_exporttype')
    p_increment = 0
    if self.hasInputFromPort('p_increment') :
      p_increment = self.getInputFromPort('p_increment')
    p_current = 0
    if self.hasInputFromPort('p_current') :
      p_current = self.getInputFromPort('p_current')
    Input_Data = 0
    if self.hasInputFromPort('Input Data') :
      Input_Data = self.getInputFromPort('Input Data')
    Filename = ''
    if self.hasInputFromPort('Filename') :
      Filename = self.getInputFromPort('Filename')
    results = sr_py.WriteField(Input_Data,Filename,p_filetype,p_confirm,p_confirm_once,p_exporttype,p_increment,p_current)

class scirun_BuildMappingMatrix(Module) :
  def compute(self) :
    p_interpolation_basis = 'linear'
    if self.hasInputFromPort('p_interpolation_basis') :
      p_interpolation_basis = self.getInputFromPort('p_interpolation_basis')
    p_map_source_to_single_dest = 0
    if self.hasInputFromPort('p_map_source_to_single_dest') :
      p_map_source_to_single_dest = self.getInputFromPort('p_map_source_to_single_dest')
    p_exhaustive_search = 0
    if self.hasInputFromPort('p_exhaustive_search') :
      p_exhaustive_search = self.getInputFromPort('p_exhaustive_search')
    p_exhaustive_search_max_dist = -1.0
    if self.hasInputFromPort('p_exhaustive_search_max_dist') :
      p_exhaustive_search_max_dist = self.getInputFromPort('p_exhaustive_search_max_dist')
    p_np = 1
    if self.hasInputFromPort('p_np') :
      p_np = self.getInputFromPort('p_np')
    Source = 0
    if self.hasInputFromPort('Source') :
      Source = self.getInputFromPort('Source')
    Destination = 0
    if self.hasInputFromPort('Destination') :
      Destination = self.getInputFromPort('Destination')
    results = sr_py.BuildMappingMatrix(Source,Destination,p_interpolation_basis,p_map_source_to_single_dest,p_exhaustive_search,p_exhaustive_search_max_dist,p_np)
    self.setResult('Mapping', results)

class scirun_InsertNrrdsIntoBundle(Module) :
  def compute(self) :
    p_nrrd1_name = 'nrrd1'
    if self.hasInputFromPort('p_nrrd1_name') :
      p_nrrd1_name = self.getInputFromPort('p_nrrd1_name')
    p_nrrd2_name = 'nrrd2'
    if self.hasInputFromPort('p_nrrd2_name') :
      p_nrrd2_name = self.getInputFromPort('p_nrrd2_name')
    p_nrrd3_name = 'nrrd3'
    if self.hasInputFromPort('p_nrrd3_name') :
      p_nrrd3_name = self.getInputFromPort('p_nrrd3_name')
    p_nrrd4_name = 'nrrd4'
    if self.hasInputFromPort('p_nrrd4_name') :
      p_nrrd4_name = self.getInputFromPort('p_nrrd4_name')
    p_nrrd5_name = 'nrrd5'
    if self.hasInputFromPort('p_nrrd5_name') :
      p_nrrd5_name = self.getInputFromPort('p_nrrd5_name')
    p_nrrd6_name = 'nrrd6'
    if self.hasInputFromPort('p_nrrd6_name') :
      p_nrrd6_name = self.getInputFromPort('p_nrrd6_name')
    p_replace1 = 1
    if self.hasInputFromPort('p_replace1') :
      p_replace1 = self.getInputFromPort('p_replace1')
    p_replace2 = 1
    if self.hasInputFromPort('p_replace2') :
      p_replace2 = self.getInputFromPort('p_replace2')
    p_replace3 = 1
    if self.hasInputFromPort('p_replace3') :
      p_replace3 = self.getInputFromPort('p_replace3')
    p_replace4 = 1
    if self.hasInputFromPort('p_replace4') :
      p_replace4 = self.getInputFromPort('p_replace4')
    p_replace5 = 1
    if self.hasInputFromPort('p_replace5') :
      p_replace5 = self.getInputFromPort('p_replace5')
    p_replace6 = 1
    if self.hasInputFromPort('p_replace6') :
      p_replace6 = self.getInputFromPort('p_replace6')
    p_bundlename = ''
    if self.hasInputFromPort('p_bundlename') :
      p_bundlename = self.getInputFromPort('p_bundlename')
    bundle = 0
    if self.hasInputFromPort('bundle') :
      bundle = self.getInputFromPort('bundle')
    nrrd1 = 0
    if self.hasInputFromPort('nrrd1') :
      nrrd1 = self.getInputFromPort('nrrd1')
    nrrd2 = 0
    if self.hasInputFromPort('nrrd2') :
      nrrd2 = self.getInputFromPort('nrrd2')
    nrrd3 = 0
    if self.hasInputFromPort('nrrd3') :
      nrrd3 = self.getInputFromPort('nrrd3')
    nrrd4 = 0
    if self.hasInputFromPort('nrrd4') :
      nrrd4 = self.getInputFromPort('nrrd4')
    nrrd5 = 0
    if self.hasInputFromPort('nrrd5') :
      nrrd5 = self.getInputFromPort('nrrd5')
    nrrd6 = 0
    if self.hasInputFromPort('nrrd6') :
      nrrd6 = self.getInputFromPort('nrrd6')
    results = sr_py.InsertNrrdsIntoBundle(bundle,nrrd1,nrrd2,nrrd3,nrrd4,nrrd5,nrrd6,p_nrrd1_name,p_nrrd2_name,p_nrrd3_name,p_nrrd4_name,p_nrrd5_name,p_nrrd6_name,p_replace1,p_replace2,p_replace3,p_replace4,p_replace5,p_replace6,p_bundlename)
    self.setResult('bundle', results)

class scirun_InsertBundlesIntoBundle(Module) :
  def compute(self) :
    p_bundle1_name = 'bundle1'
    if self.hasInputFromPort('p_bundle1_name') :
      p_bundle1_name = self.getInputFromPort('p_bundle1_name')
    p_bundle2_name = 'bundle2'
    if self.hasInputFromPort('p_bundle2_name') :
      p_bundle2_name = self.getInputFromPort('p_bundle2_name')
    p_bundle3_name = 'bundle3'
    if self.hasInputFromPort('p_bundle3_name') :
      p_bundle3_name = self.getInputFromPort('p_bundle3_name')
    p_bundle4_name = 'bundle4'
    if self.hasInputFromPort('p_bundle4_name') :
      p_bundle4_name = self.getInputFromPort('p_bundle4_name')
    p_bundle5_name = 'bundle5'
    if self.hasInputFromPort('p_bundle5_name') :
      p_bundle5_name = self.getInputFromPort('p_bundle5_name')
    p_bundle6_name = 'bundle6'
    if self.hasInputFromPort('p_bundle6_name') :
      p_bundle6_name = self.getInputFromPort('p_bundle6_name')
    p_replace1 = 1
    if self.hasInputFromPort('p_replace1') :
      p_replace1 = self.getInputFromPort('p_replace1')
    p_replace2 = 1
    if self.hasInputFromPort('p_replace2') :
      p_replace2 = self.getInputFromPort('p_replace2')
    p_replace3 = 1
    if self.hasInputFromPort('p_replace3') :
      p_replace3 = self.getInputFromPort('p_replace3')
    p_replace4 = 1
    if self.hasInputFromPort('p_replace4') :
      p_replace4 = self.getInputFromPort('p_replace4')
    p_replace5 = 1
    if self.hasInputFromPort('p_replace5') :
      p_replace5 = self.getInputFromPort('p_replace5')
    p_replace6 = 1
    if self.hasInputFromPort('p_replace6') :
      p_replace6 = self.getInputFromPort('p_replace6')
    p_bundlename = ''
    if self.hasInputFromPort('p_bundlename') :
      p_bundlename = self.getInputFromPort('p_bundlename')
    bundle = 0
    if self.hasInputFromPort('bundle') :
      bundle = self.getInputFromPort('bundle')
    bundle1 = 0
    if self.hasInputFromPort('bundle1') :
      bundle1 = self.getInputFromPort('bundle1')
    bundle2 = 0
    if self.hasInputFromPort('bundle2') :
      bundle2 = self.getInputFromPort('bundle2')
    bundle3 = 0
    if self.hasInputFromPort('bundle3') :
      bundle3 = self.getInputFromPort('bundle3')
    bundle4 = 0
    if self.hasInputFromPort('bundle4') :
      bundle4 = self.getInputFromPort('bundle4')
    bundle5 = 0
    if self.hasInputFromPort('bundle5') :
      bundle5 = self.getInputFromPort('bundle5')
    bundle6 = 0
    if self.hasInputFromPort('bundle6') :
      bundle6 = self.getInputFromPort('bundle6')
    results = sr_py.InsertBundlesIntoBundle(bundle,bundle1,bundle2,bundle3,bundle4,bundle5,bundle6,p_bundle1_name,p_bundle2_name,p_bundle3_name,p_bundle4_name,p_bundle5_name,p_bundle6_name,p_replace1,p_replace2,p_replace3,p_replace4,p_replace5,p_replace6,p_bundlename)
    self.setResult('bundle', results)

class scirun_ReadBundle(Module) :
  def compute(self) :
    p_from_env = ''
    if self.hasInputFromPort('p_from_env') :
      p_from_env = self.getInputFromPort('p_from_env')
    p_types = 'SCIRun Bundle File} {.bdl} } {{SCIRun Bundle Any} {.*} } '
    if self.hasInputFromPort('p_types') :
      p_types = self.getInputFromPort('p_types')
    Filename = ''
    if self.hasInputFromPort('Filename') :
      Filename = self.getInputFromPort('Filename')
    results = sr_py.ReadBundle(Filename,p_from_env,p_types)
    self.setResult('bundle', results[0])
    self.setResult('Filename', results[1])

class scirun_GetStringsFromBundle(Module) :
  def compute(self) :
    p_string1_name = 'string1'
    if self.hasInputFromPort('p_string1_name') :
      p_string1_name = self.getInputFromPort('p_string1_name')
    p_string2_name = 'string2'
    if self.hasInputFromPort('p_string2_name') :
      p_string2_name = self.getInputFromPort('p_string2_name')
    p_string3_name = 'string3'
    if self.hasInputFromPort('p_string3_name') :
      p_string3_name = self.getInputFromPort('p_string3_name')
    p_string4_name = 'string4'
    if self.hasInputFromPort('p_string4_name') :
      p_string4_name = self.getInputFromPort('p_string4_name')
    p_string5_name = 'string5'
    if self.hasInputFromPort('p_string5_name') :
      p_string5_name = self.getInputFromPort('p_string5_name')
    p_string6_name = 'string6'
    if self.hasInputFromPort('p_string6_name') :
      p_string6_name = self.getInputFromPort('p_string6_name')
    p_string_selection = ''
    if self.hasInputFromPort('p_string_selection') :
      p_string_selection = self.getInputFromPort('p_string_selection')
    bundle = 0
    if self.hasInputFromPort('bundle') :
      bundle = self.getInputFromPort('bundle')
    results = sr_py.GetStringsFromBundle(bundle,p_string1_name,p_string2_name,p_string3_name,p_string4_name,p_string5_name,p_string6_name,p_string_selection)
    self.setResult('bundle', results[0])
    self.setResult('string1', results[1])
    self.setResult('string2', results[2])
    self.setResult('string3', results[3])
    self.setResult('string4', results[4])
    self.setResult('string5', results[5])
    self.setResult('string6', results[6])

class scirun_ShowString(Module) :
  def compute(self) :
    p_bbox = 1
    if self.hasInputFromPort('p_bbox') :
      p_bbox = self.getInputFromPort('p_bbox')
    p_size = 1
    if self.hasInputFromPort('p_size') :
      p_size = self.getInputFromPort('p_size')
    p_location_x = -0.96875
    if self.hasInputFromPort('p_location_x') :
      p_location_x = self.getInputFromPort('p_location_x')
    p_location_y = 0.96875
    if self.hasInputFromPort('p_location_y') :
      p_location_y = self.getInputFromPort('p_location_y')
    p_color_r = 1.0
    if self.hasInputFromPort('p_color_r') :
      p_color_r = self.getInputFromPort('p_color_r')
    p_color_g = 1.0
    if self.hasInputFromPort('p_color_g') :
      p_color_g = self.getInputFromPort('p_color_g')
    p_color_b = 1.0
    if self.hasInputFromPort('p_color_b') :
      p_color_b = self.getInputFromPort('p_color_b')
    Format_String = ''
    if self.hasInputFromPort('Format String') :
      Format_String = self.getInputFromPort('Format String')
    results = sr_py.ShowString(Format_String,p_bbox,p_size,p_location_x,p_location_y,p_color_r,p_color_g,p_color_b)
    self.setResult('Title', results)

class scirun_SwapNodeLocationsWithMatrixEntries(Module) :
  def compute(self) :
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    Input_Matrix = 0
    if self.hasInputFromPort('Input Matrix') :
      Input_Matrix = self.getInputFromPort('Input Matrix')
    results = sr_py.SwapNodeLocationsWithMatrixEntries(Input_Field,Input_Matrix)
    self.setResult('Output Field', results[0])
    self.setResult('Output Matrix', results[1])

class scirun_ReorderMatrixByReverseCuthillMcKee(Module) :
  def compute(self) :
    Matrix = 0
    if self.hasInputFromPort('Matrix') :
      Matrix = self.getInputFromPort('Matrix')
    results = sr_py.ReorderMatrixByReverseCuthillMcKee(Matrix)
    self.setResult('Matrix', results[0])
    self.setResult('Mapping', results[1])
    self.setResult('InverseMapping', results[2])

class scirun_MapFieldDataFromNodeToElem(Module) :
  def compute(self) :
    p_method = 'Interpolate'
    if self.hasInputFromPort('p_method') :
      p_method = self.getInputFromPort('p_method')
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    results = sr_py.MapFieldDataFromNodeToElem(Field,p_method)
    self.setResult('Field', results)

class scirun_GetDomainBoundary(Module) :
  def compute(self) :
    p_userange = 0
    if self.hasInputFromPort('p_userange') :
      p_userange = self.getInputFromPort('p_userange')
    p_minrange = 0.0
    if self.hasInputFromPort('p_minrange') :
      p_minrange = self.getInputFromPort('p_minrange')
    p_maxrange = 255.0
    if self.hasInputFromPort('p_maxrange') :
      p_maxrange = self.getInputFromPort('p_maxrange')
    p_usevalue = 0
    if self.hasInputFromPort('p_usevalue') :
      p_usevalue = self.getInputFromPort('p_usevalue')
    p_value = 1.0
    if self.hasInputFromPort('p_value') :
      p_value = self.getInputFromPort('p_value')
    p_includeouterboundary = 1
    if self.hasInputFromPort('p_includeouterboundary') :
      p_includeouterboundary = self.getInputFromPort('p_includeouterboundary')
    p_innerboundaryonly = 0
    if self.hasInputFromPort('p_innerboundaryonly') :
      p_innerboundaryonly = self.getInputFromPort('p_innerboundaryonly')
    p_noinnerboundary = 0
    if self.hasInputFromPort('p_noinnerboundary') :
      p_noinnerboundary = self.getInputFromPort('p_noinnerboundary')
    p_disconnect = 1
    if self.hasInputFromPort('p_disconnect') :
      p_disconnect = self.getInputFromPort('p_disconnect')
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    MinValueValue = 0
    if self.hasInputFromPort('MinValueValue') :
      MinValueValue = self.getInputFromPort('MinValueValue')
    MaxValue = 0
    if self.hasInputFromPort('MaxValue') :
      MaxValue = self.getInputFromPort('MaxValue')
    results = sr_py.GetDomainBoundary(Field,MinValueValue,MaxValue,p_userange,p_minrange,p_maxrange,p_usevalue,p_value,p_includeouterboundary,p_innerboundaryonly,p_noinnerboundary,p_disconnect)
    self.setResult('Field', results)

class scirun_CollectFields(Module) :
  def compute(self) :
    p_buffersize = 20
    if self.hasInputFromPort('p_buffersize') :
      p_buffersize = self.getInputFromPort('p_buffersize')
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    BufferSize = 0
    if self.hasInputFromPort('BufferSize') :
      BufferSize = self.getInputFromPort('BufferSize')
    results = sr_py.CollectFields(Field,BufferSize,p_buffersize)
    self.setResult('Fields', results)

class scirun_ReportStringInfo(Module) :
  def compute(self) :
    p_inputstring = ''
    if self.hasInputFromPort('p_inputstring') :
      p_inputstring = self.getInputFromPort('p_inputstring')
    Input = ''
    if self.hasInputFromPort('Input') :
      Input = self.getInputFromPort('Input')
    results = sr_py.ReportStringInfo(Input,p_inputstring)

class scirun_StreamMatrixFromDisk(Module) :
  def compute(self) :
    p_row_or_col = 'column'
    if self.hasInputFromPort('p_row_or_col') :
      p_row_or_col = self.getInputFromPort('p_row_or_col')
    p_slider_min = 0
    if self.hasInputFromPort('p_slider_min') :
      p_slider_min = self.getInputFromPort('p_slider_min')
    p_slider_max = 100
    if self.hasInputFromPort('p_slider_max') :
      p_slider_max = self.getInputFromPort('p_slider_max')
    p_range_min = 0
    if self.hasInputFromPort('p_range_min') :
      p_range_min = self.getInputFromPort('p_range_min')
    p_range_max = 100
    if self.hasInputFromPort('p_range_max') :
      p_range_max = self.getInputFromPort('p_range_max')
    p_playmode = 'once'
    if self.hasInputFromPort('p_playmode') :
      p_playmode = self.getInputFromPort('p_playmode')
    p_current = 0
    if self.hasInputFromPort('p_current') :
      p_current = self.getInputFromPort('p_current')
    p_execmode = 'init'
    if self.hasInputFromPort('p_execmode') :
      p_execmode = self.getInputFromPort('p_execmode')
    p_delay = 0
    if self.hasInputFromPort('p_delay') :
      p_delay = self.getInputFromPort('p_delay')
    p_inc_amount = 1
    if self.hasInputFromPort('p_inc_amount') :
      p_inc_amount = self.getInputFromPort('p_inc_amount')
    p_send_amount = 1
    if self.hasInputFromPort('p_send_amount') :
      p_send_amount = self.getInputFromPort('p_send_amount')
    Indices = 0
    if self.hasInputFromPort('Indices') :
      Indices = self.getInputFromPort('Indices')
    Weights = 0
    if self.hasInputFromPort('Weights') :
      Weights = self.getInputFromPort('Weights')
    Filename = ''
    if self.hasInputFromPort('Filename') :
      Filename = self.getInputFromPort('Filename')
    results = sr_py.StreamMatrixFromDisk(Indices,Weights,Filename,p_row_or_col,p_slider_min,p_slider_max,p_range_min,p_range_max,p_playmode,p_current,p_execmode,p_delay,p_inc_amount,p_send_amount)
    self.setResult('DataVector', results[0])
    self.setResult('Index', results[1])
    self.setResult('Scaled Index', results[2])
    self.setResult('Filename', results[3])

class scirun_WriteMatrix(Module) :
  def compute(self) :
    p_filetype = 'Binary'
    if self.hasInputFromPort('p_filetype') :
      p_filetype = self.getInputFromPort('p_filetype')
    p_confirm = '0'
    if self.hasInputFromPort('p_confirm') :
      p_confirm = self.getInputFromPort('p_confirm')
    p_confirm_once = '0'
    if self.hasInputFromPort('p_confirm_once') :
      p_confirm_once = self.getInputFromPort('p_confirm_once')
    p_exporttype = ''
    if self.hasInputFromPort('p_exporttype') :
      p_exporttype = self.getInputFromPort('p_exporttype')
    p_split = 0
    if self.hasInputFromPort('p_split') :
      p_split = self.getInputFromPort('p_split')
    Input_Data = 0
    if self.hasInputFromPort('Input Data') :
      Input_Data = self.getInputFromPort('Input Data')
    Filename = ''
    if self.hasInputFromPort('Filename') :
      Filename = self.getInputFromPort('Filename')
    results = sr_py.WriteMatrix(Input_Data,Filename,p_filetype,p_confirm,p_confirm_once,p_exporttype,p_split)

class scirun_ConvertFieldDataType(Module) :
  def compute(self) :
    p_outputdatatype = 'double'
    if self.hasInputFromPort('p_outputdatatype') :
      p_outputdatatype = self.getInputFromPort('p_outputdatatype')
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    results = sr_py.ConvertFieldDataType(Input_Field,p_outputdatatype)
    self.setResult('Output Field', results)

class scirun_GeneratePointSamplesFromField(Module) :
  def compute(self) :
    p_num_seeds = 1
    if self.hasInputFromPort('p_num_seeds') :
      p_num_seeds = self.getInputFromPort('p_num_seeds')
    p_probe_scale = 5.0
    if self.hasInputFromPort('p_probe_scale') :
      p_probe_scale = self.getInputFromPort('p_probe_scale')
    p_send = 0
    if self.hasInputFromPort('p_send') :
      p_send = self.getInputFromPort('p_send')
    p_widget = 0
    if self.hasInputFromPort('p_widget') :
      p_widget = self.getInputFromPort('p_widget')
    p_red = 0.5
    if self.hasInputFromPort('p_red') :
      p_red = self.getInputFromPort('p_red')
    p_green = 0.5
    if self.hasInputFromPort('p_green') :
      p_green = self.getInputFromPort('p_green')
    p_blue = 0.5
    if self.hasInputFromPort('p_blue') :
      p_blue = self.getInputFromPort('p_blue')
    p_auto_execute = 1
    if self.hasInputFromPort('p_auto_execute') :
      p_auto_execute = self.getInputFromPort('p_auto_execute')
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    results = sr_py.GeneratePointSamplesFromField(Input_Field,p_num_seeds,p_probe_scale,p_send,p_widget,p_red,p_green,p_blue,p_auto_execute)
    self.setResult('GeneratePointSamplesFromField Widget', results[0])
    self.setResult('GeneratePointSamplesFromField Point', results[1])

class scirun_GeneratePointSamplesFromFieldOrWidget(Module) :
  def compute(self) :
    p_wtype = 'rake'
    if self.hasInputFromPort('p_wtype') :
      p_wtype = self.getInputFromPort('p_wtype')
    p_endpoints = 0
    if self.hasInputFromPort('p_endpoints') :
      p_endpoints = self.getInputFromPort('p_endpoints')
    p_maxseeds = 15.0
    if self.hasInputFromPort('p_maxseeds') :
      p_maxseeds = self.getInputFromPort('p_maxseeds')
    p_numseeds = 10
    if self.hasInputFromPort('p_numseeds') :
      p_numseeds = self.getInputFromPort('p_numseeds')
    p_rngseed = 1
    if self.hasInputFromPort('p_rngseed') :
      p_rngseed = self.getInputFromPort('p_rngseed')
    p_rnginc = 1
    if self.hasInputFromPort('p_rnginc') :
      p_rnginc = self.getInputFromPort('p_rnginc')
    p_clamp = 0
    if self.hasInputFromPort('p_clamp') :
      p_clamp = self.getInputFromPort('p_clamp')
    p_autoexecute = 1
    if self.hasInputFromPort('p_autoexecute') :
      p_autoexecute = self.getInputFromPort('p_autoexecute')
    p_dist = 'uniuni'
    if self.hasInputFromPort('p_dist') :
      p_dist = self.getInputFromPort('p_dist')
    p_whichtab = 'Widget'
    if self.hasInputFromPort('p_whichtab') :
      p_whichtab = self.getInputFromPort('p_whichtab')
    Field_to_Sample = 0
    if self.hasInputFromPort('Field to Sample') :
      Field_to_Sample = self.getInputFromPort('Field to Sample')
    results = sr_py.GeneratePointSamplesFromFieldOrWidget(Field_to_Sample,p_wtype,p_endpoints,p_maxseeds,p_numseeds,p_rngseed,p_rnginc,p_clamp,p_autoexecute,p_dist,p_whichtab)
    self.setResult('Samples', results[0])
    self.setResult('Sampling Widget', results[1])

class scirun_CreateMatrix(Module) :
  def compute(self) :
    p_rows = 1
    if self.hasInputFromPort('p_rows') :
      p_rows = self.getInputFromPort('p_rows')
    p_cols = 1
    if self.hasInputFromPort('p_cols') :
      p_cols = self.getInputFromPort('p_cols')
    p_data = '0.0'
    if self.hasInputFromPort('p_data') :
      p_data = self.getInputFromPort('p_data')
    p_clabel = '0'
    if self.hasInputFromPort('p_clabel') :
      p_clabel = self.getInputFromPort('p_clabel')
    p_rlabel = '0'
    if self.hasInputFromPort('p_rlabel') :
      p_rlabel = self.getInputFromPort('p_rlabel')
    results = sr_py.CreateMatrix(p_rows,p_cols,p_data,p_clabel,p_rlabel)
    self.setResult('matrix', results)

class scirun_CalculateIsInsideField(Module) :
  def compute(self) :
    p_outputbasis = 'same as input'
    if self.hasInputFromPort('p_outputbasis') :
      p_outputbasis = self.getInputFromPort('p_outputbasis')
    p_outputtype = 'double'
    if self.hasInputFromPort('p_outputtype') :
      p_outputtype = self.getInputFromPort('p_outputtype')
    p_outval = 0
    if self.hasInputFromPort('p_outval') :
      p_outval = self.getInputFromPort('p_outval')
    p_inval = 1
    if self.hasInputFromPort('p_inval') :
      p_inval = self.getInputFromPort('p_inval')
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    ObjectField = 0
    if self.hasInputFromPort('ObjectField') :
      ObjectField = self.getInputFromPort('ObjectField')
    results = sr_py.CalculateIsInsideField(Field,ObjectField,p_outputbasis,p_outputtype,p_outval,p_inval)
    self.setResult('Field', results)

class scirun_CreateAndEditColorMap(Module) :
  def compute(self) :
    p_rgbhsv = 1
    if self.hasInputFromPort('p_rgbhsv') :
      p_rgbhsv = self.getInputFromPort('p_rgbhsv')
    p_rgb_points = '0 0.05 0.1 0 1 0.95 0.9 1 '
    if self.hasInputFromPort('p_rgb_points') :
      p_rgb_points = self.getInputFromPort('p_rgb_points')
    p_alpha_points = '0 0 0 0.25 0.5 0.5 0.8 0.75 0.8 1 '
    if self.hasInputFromPort('p_alpha_points') :
      p_alpha_points = self.getInputFromPort('p_alpha_points')
    p_resolution = 256
    if self.hasInputFromPort('p_resolution') :
      p_resolution = self.getInputFromPort('p_resolution')
    ColorMap = 0
    if self.hasInputFromPort('ColorMap') :
      ColorMap = self.getInputFromPort('ColorMap')
    results = sr_py.CreateAndEditColorMap(ColorMap,p_rgbhsv,p_rgb_points,p_alpha_points,p_resolution)
    self.setResult('ColorMap', results[0])
    self.setResult('Geometry', results[1])

class scirun_DecimateTriSurf(Module) :
  def compute(self) :
    TriSurf = 0
    if self.hasInputFromPort('TriSurf') :
      TriSurf = self.getInputFromPort('TriSurf')
    results = sr_py.DecimateTriSurf(TriSurf)
    self.setResult('Decimated', results)

class scirun_CoregisterPointClouds(Module) :
  def compute(self) :
    p_allowScale = 1
    if self.hasInputFromPort('p_allowScale') :
      p_allowScale = self.getInputFromPort('p_allowScale')
    p_allowRotate = 1
    if self.hasInputFromPort('p_allowRotate') :
      p_allowRotate = self.getInputFromPort('p_allowRotate')
    p_allowTranslate = 1
    if self.hasInputFromPort('p_allowTranslate') :
      p_allowTranslate = self.getInputFromPort('p_allowTranslate')
    p_seed = 1
    if self.hasInputFromPort('p_seed') :
      p_seed = self.getInputFromPort('p_seed')
    p_iters = 1000
    if self.hasInputFromPort('p_iters') :
      p_iters = self.getInputFromPort('p_iters')
    p_misfitTol = 0.001
    if self.hasInputFromPort('p_misfitTol') :
      p_misfitTol = self.getInputFromPort('p_misfitTol')
    p_method = 'Analytic'
    if self.hasInputFromPort('p_method') :
      p_method = self.getInputFromPort('p_method')
    Fixed_PointCloudField = 0
    if self.hasInputFromPort('Fixed PointCloudField') :
      Fixed_PointCloudField = self.getInputFromPort('Fixed PointCloudField')
    Mobile_PointCloudField = 0
    if self.hasInputFromPort('Mobile PointCloudField') :
      Mobile_PointCloudField = self.getInputFromPort('Mobile PointCloudField')
    DistanceField_From_Fixed = 0
    if self.hasInputFromPort('DistanceField From Fixed') :
      DistanceField_From_Fixed = self.getInputFromPort('DistanceField From Fixed')
    results = sr_py.CoregisterPointClouds(Fixed_PointCloudField,Mobile_PointCloudField,DistanceField_From_Fixed,p_allowScale,p_allowRotate,p_allowTranslate,p_seed,p_iters,p_misfitTol,p_method)
    self.setResult('Transform', results)

class scirun_SolveMinNormLeastSqSystem(Module) :
  def compute(self) :
    BasisVec1 = 0
    if self.hasInputFromPort('BasisVec1') :
      BasisVec1 = self.getInputFromPort('BasisVec1')
    BasisVec2 = 0
    if self.hasInputFromPort('BasisVec2') :
      BasisVec2 = self.getInputFromPort('BasisVec2')
    BasisVec3 = 0
    if self.hasInputFromPort('BasisVec3') :
      BasisVec3 = self.getInputFromPort('BasisVec3')
    TargetVec = 0
    if self.hasInputFromPort('TargetVec') :
      TargetVec = self.getInputFromPort('TargetVec')
    results = sr_py.SolveMinNormLeastSqSystem(BasisVec1,BasisVec2,BasisVec3,TargetVec)
    self.setResult('WeightVec(Col)', results[0])
    self.setResult('ResultVec(Col)', results[1])

class scirun_CalculateFieldData(Module) :
  def compute(self) :
    p_function = 'RESULT = abs(DATA);'
    if self.hasInputFromPort('p_function') :
      p_function = self.getInputFromPort('p_function')
    p_format = 'Scalar'
    if self.hasInputFromPort('p_format') :
      p_format = self.getInputFromPort('p_format')
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    Function = ''
    if self.hasInputFromPort('Function') :
      Function = self.getInputFromPort('Function')
    Array = 0
    if self.hasInputFromPort('Array') :
      Array = self.getInputFromPort('Array')
    results = sr_py.CalculateFieldData(Field,Function,Array,p_function,p_format)
    self.setResult('Field', results)

class scirun_MapFieldDataToNodeCoordinate(Module) :
  def compute(self) :
    p_coord = 2
    if self.hasInputFromPort('p_coord') :
      p_coord = self.getInputFromPort('p_coord')
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    results = sr_py.MapFieldDataToNodeCoordinate(Input_Field,p_coord)
    self.setResult('Output Field', results)

class scirun_ShowMeshBoundingBox(Module) :
  def compute(self) :
    p_sizex = 10
    if self.hasInputFromPort('p_sizex') :
      p_sizex = self.getInputFromPort('p_sizex')
    p_sizey = 10
    if self.hasInputFromPort('p_sizey') :
      p_sizey = self.getInputFromPort('p_sizey')
    p_sizez = 10
    if self.hasInputFromPort('p_sizez') :
      p_sizez = self.getInputFromPort('p_sizez')
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    results = sr_py.ShowMeshBoundingBox(Field,p_sizex,p_sizey,p_sizez)
    self.setResult('Scene Graph', results)

class scirun_ViewGraph(Module) :
  def compute(self) :
    Title = ''
    if self.hasInputFromPort('Title') :
      Title = self.getInputFromPort('Title')
    Input = 0
    if self.hasInputFromPort('Input') :
      Input = self.getInputFromPort('Input')
    results = sr_py.ViewGraph(Title,Input)

class scirun_CreateStandardColorMaps(Module) :
  def compute(self) :
    p_mapName = 'Rainbow'
    if self.hasInputFromPort('p_mapName') :
      p_mapName = self.getInputFromPort('p_mapName')
    p_gamma = 0.0
    if self.hasInputFromPort('p_gamma') :
      p_gamma = self.getInputFromPort('p_gamma')
    p_resolution = 256
    if self.hasInputFromPort('p_resolution') :
      p_resolution = self.getInputFromPort('p_resolution')
    p_reverse = 0
    if self.hasInputFromPort('p_reverse') :
      p_reverse = self.getInputFromPort('p_reverse')
    p_faux = 0
    if self.hasInputFromPort('p_faux') :
      p_faux = self.getInputFromPort('p_faux')
    p_positionList = ''
    if self.hasInputFromPort('p_positionList') :
      p_positionList = self.getInputFromPort('p_positionList')
    p_nodeList = ''
    if self.hasInputFromPort('p_nodeList') :
      p_nodeList = self.getInputFromPort('p_nodeList')
    p_width = 1
    if self.hasInputFromPort('p_width') :
      p_width = self.getInputFromPort('p_width')
    p_height = 1
    if self.hasInputFromPort('p_height') :
      p_height = self.getInputFromPort('p_height')
    results = sr_py.CreateStandardColorMaps(p_mapName,p_gamma,p_resolution,p_reverse,p_faux,p_positionList,p_nodeList,p_width,p_height)
    self.setResult('ColorMap', results)

class scirun_ShowTextureSlices(Module) :
  def compute(self) :
    p_control_pos_saved = 0
    if self.hasInputFromPort('p_control_pos_saved') :
      p_control_pos_saved = self.getInputFromPort('p_control_pos_saved')
    p_drawX = 0
    if self.hasInputFromPort('p_drawX') :
      p_drawX = self.getInputFromPort('p_drawX')
    p_drawY = 0
    if self.hasInputFromPort('p_drawY') :
      p_drawY = self.getInputFromPort('p_drawY')
    p_drawZ = 0
    if self.hasInputFromPort('p_drawZ') :
      p_drawZ = self.getInputFromPort('p_drawZ')
    p_drawView = 0
    if self.hasInputFromPort('p_drawView') :
      p_drawView = self.getInputFromPort('p_drawView')
    p_interp_mode = 1
    if self.hasInputFromPort('p_interp_mode') :
      p_interp_mode = self.getInputFromPort('p_interp_mode')
    p_draw_phi_0 = 0
    if self.hasInputFromPort('p_draw_phi_0') :
      p_draw_phi_0 = self.getInputFromPort('p_draw_phi_0')
    p_draw_phi_1 = 0
    if self.hasInputFromPort('p_draw_phi_1') :
      p_draw_phi_1 = self.getInputFromPort('p_draw_phi_1')
    p_phi_0 = 30.0
    if self.hasInputFromPort('p_phi_0') :
      p_phi_0 = self.getInputFromPort('p_phi_0')
    p_phi_1 = 60.0
    if self.hasInputFromPort('p_phi_1') :
      p_phi_1 = self.getInputFromPort('p_phi_1')
    p_multi_level = 1
    if self.hasInputFromPort('p_multi_level') :
      p_multi_level = self.getInputFromPort('p_multi_level')
    p_color_changed = 1
    if self.hasInputFromPort('p_color_changed') :
      p_color_changed = self.getInputFromPort('p_color_changed')
    p_colors = ''
    if self.hasInputFromPort('p_colors') :
      p_colors = self.getInputFromPort('p_colors')
    p_level_on = ''
    if self.hasInputFromPort('p_level_on') :
      p_level_on = self.getInputFromPort('p_level_on')
    p_outline_levels = 0
    if self.hasInputFromPort('p_outline_levels') :
      p_outline_levels = self.getInputFromPort('p_outline_levels')
    p_use_stencil = 0
    if self.hasInputFromPort('p_use_stencil') :
      p_use_stencil = self.getInputFromPort('p_use_stencil')
    Texture = 0
    if self.hasInputFromPort('Texture') :
      Texture = self.getInputFromPort('Texture')
    ColorMap = 0
    if self.hasInputFromPort('ColorMap') :
      ColorMap = self.getInputFromPort('ColorMap')
    ColorMap2 = 0
    if self.hasInputFromPort('ColorMap2') :
      ColorMap2 = self.getInputFromPort('ColorMap2')
    results = sr_py.ShowTextureSlices(Texture,ColorMap,ColorMap2,p_control_pos_saved,p_drawX,p_drawY,p_drawZ,p_drawView,p_interp_mode,p_draw_phi_0,p_draw_phi_1,p_phi_0,p_phi_1,p_multi_level,p_color_changed,p_colors,p_level_on,p_outline_levels,p_use_stencil)
    self.setResult('Geometry', results[0])
    self.setResult('ColorMap', results[1])

class scirun_ShowMatrix(Module) :
  def compute(self) :
    p_xpos = 0.0
    if self.hasInputFromPort('p_xpos') :
      p_xpos = self.getInputFromPort('p_xpos')
    p_ypos = 0.0
    if self.hasInputFromPort('p_ypos') :
      p_ypos = self.getInputFromPort('p_ypos')
    p_xscale = 1.0
    if self.hasInputFromPort('p_xscale') :
      p_xscale = self.getInputFromPort('p_xscale')
    p_yscale = 2.0
    if self.hasInputFromPort('p_yscale') :
      p_yscale = self.getInputFromPort('p_yscale')
    p_3d_mode = 1
    if self.hasInputFromPort('p_3d_mode') :
      p_3d_mode = self.getInputFromPort('p_3d_mode')
    p_gmode = 1
    if self.hasInputFromPort('p_gmode') :
      p_gmode = self.getInputFromPort('p_gmode')
    p_showtext = 0
    if self.hasInputFromPort('p_showtext') :
      p_showtext = self.getInputFromPort('p_showtext')
    p_row_begin = 0
    if self.hasInputFromPort('p_row_begin') :
      p_row_begin = self.getInputFromPort('p_row_begin')
    p_rows = 10000
    if self.hasInputFromPort('p_rows') :
      p_rows = self.getInputFromPort('p_rows')
    p_col_begin = 0
    if self.hasInputFromPort('p_col_begin') :
      p_col_begin = self.getInputFromPort('p_col_begin')
    p_cols = 10000
    if self.hasInputFromPort('p_cols') :
      p_cols = self.getInputFromPort('p_cols')
    p_colormapmode = 0
    if self.hasInputFromPort('p_colormapmode') :
      p_colormapmode = self.getInputFromPort('p_colormapmode')
    ColorMap = 0
    if self.hasInputFromPort('ColorMap') :
      ColorMap = self.getInputFromPort('ColorMap')
    Matrix = 0
    if self.hasInputFromPort('Matrix') :
      Matrix = self.getInputFromPort('Matrix')
    results = sr_py.ShowMatrix(ColorMap,Matrix,p_xpos,p_ypos,p_xscale,p_yscale,p_3d_mode,p_gmode,p_showtext,p_row_begin,p_rows,p_col_begin,p_cols,p_colormapmode)
    self.setResult('Geometry', results)

class scirun_GetSliceFromStructuredFieldByIndices(Module) :
  def compute(self) :
    p_axis = 2
    if self.hasInputFromPort('p_axis') :
      p_axis = self.getInputFromPort('p_axis')
    p_dims = 3
    if self.hasInputFromPort('p_dims') :
      p_dims = self.getInputFromPort('p_dims')
    p_dim_i = 1
    if self.hasInputFromPort('p_dim_i') :
      p_dim_i = self.getInputFromPort('p_dim_i')
    p_dim_j = 1
    if self.hasInputFromPort('p_dim_j') :
      p_dim_j = self.getInputFromPort('p_dim_j')
    p_dim_k = 1
    if self.hasInputFromPort('p_dim_k') :
      p_dim_k = self.getInputFromPort('p_dim_k')
    p_index_i = 1
    if self.hasInputFromPort('p_index_i') :
      p_index_i = self.getInputFromPort('p_index_i')
    p_index_j = 1
    if self.hasInputFromPort('p_index_j') :
      p_index_j = self.getInputFromPort('p_index_j')
    p_index_k = 1
    if self.hasInputFromPort('p_index_k') :
      p_index_k = self.getInputFromPort('p_index_k')
    p_update_type = 'Manual'
    if self.hasInputFromPort('p_update_type') :
      p_update_type = self.getInputFromPort('p_update_type')
    p_continuous = 0
    if self.hasInputFromPort('p_continuous') :
      p_continuous = self.getInputFromPort('p_continuous')
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    Input_Matrix = 0
    if self.hasInputFromPort('Input Matrix') :
      Input_Matrix = self.getInputFromPort('Input Matrix')
    results = sr_py.GetSliceFromStructuredFieldByIndices(Input_Field,Input_Matrix,p_axis,p_dims,p_dim_i,p_dim_j,p_dim_k,p_index_i,p_index_j,p_index_k,p_update_type,p_continuous)
    self.setResult('Output Field', results[0])
    self.setResult('Output Matrix', results[1])

class scirun_ConvertMatrixType(Module) :
  def compute(self) :
    p_oldtype = 'Same'
    if self.hasInputFromPort('p_oldtype') :
      p_oldtype = self.getInputFromPort('p_oldtype')
    p_newtype = 'Unknown'
    if self.hasInputFromPort('p_newtype') :
      p_newtype = self.getInputFromPort('p_newtype')
    p_nrow = '??'
    if self.hasInputFromPort('p_nrow') :
      p_nrow = self.getInputFromPort('p_nrow')
    p_ncol = '??'
    if self.hasInputFromPort('p_ncol') :
      p_ncol = self.getInputFromPort('p_ncol')
    Input = 0
    if self.hasInputFromPort('Input') :
      Input = self.getInputFromPort('Input')
    results = sr_py.ConvertMatrixType(Input,p_oldtype,p_newtype,p_nrow,p_ncol)
    self.setResult('Output', results)

class scirun_InsertColorMapsIntoBundle(Module) :
  def compute(self) :
    p_colormap1_name = 'colormap1'
    if self.hasInputFromPort('p_colormap1_name') :
      p_colormap1_name = self.getInputFromPort('p_colormap1_name')
    p_colormap2_name = 'colormap2'
    if self.hasInputFromPort('p_colormap2_name') :
      p_colormap2_name = self.getInputFromPort('p_colormap2_name')
    p_colormap3_name = 'colormap3'
    if self.hasInputFromPort('p_colormap3_name') :
      p_colormap3_name = self.getInputFromPort('p_colormap3_name')
    p_colormap4_name = 'colormap4'
    if self.hasInputFromPort('p_colormap4_name') :
      p_colormap4_name = self.getInputFromPort('p_colormap4_name')
    p_colormap5_name = 'colormap5'
    if self.hasInputFromPort('p_colormap5_name') :
      p_colormap5_name = self.getInputFromPort('p_colormap5_name')
    p_colormap6_name = 'colormap6'
    if self.hasInputFromPort('p_colormap6_name') :
      p_colormap6_name = self.getInputFromPort('p_colormap6_name')
    p_replace1 = 1
    if self.hasInputFromPort('p_replace1') :
      p_replace1 = self.getInputFromPort('p_replace1')
    p_replace2 = 1
    if self.hasInputFromPort('p_replace2') :
      p_replace2 = self.getInputFromPort('p_replace2')
    p_replace3 = 1
    if self.hasInputFromPort('p_replace3') :
      p_replace3 = self.getInputFromPort('p_replace3')
    p_replace4 = 1
    if self.hasInputFromPort('p_replace4') :
      p_replace4 = self.getInputFromPort('p_replace4')
    p_replace5 = 1
    if self.hasInputFromPort('p_replace5') :
      p_replace5 = self.getInputFromPort('p_replace5')
    p_replace6 = 1
    if self.hasInputFromPort('p_replace6') :
      p_replace6 = self.getInputFromPort('p_replace6')
    p_bundlename = ''
    if self.hasInputFromPort('p_bundlename') :
      p_bundlename = self.getInputFromPort('p_bundlename')
    bundle = 0
    if self.hasInputFromPort('bundle') :
      bundle = self.getInputFromPort('bundle')
    colormap1 = 0
    if self.hasInputFromPort('colormap1') :
      colormap1 = self.getInputFromPort('colormap1')
    colormap2 = 0
    if self.hasInputFromPort('colormap2') :
      colormap2 = self.getInputFromPort('colormap2')
    colormap3 = 0
    if self.hasInputFromPort('colormap3') :
      colormap3 = self.getInputFromPort('colormap3')
    colormap4 = 0
    if self.hasInputFromPort('colormap4') :
      colormap4 = self.getInputFromPort('colormap4')
    colormap5 = 0
    if self.hasInputFromPort('colormap5') :
      colormap5 = self.getInputFromPort('colormap5')
    colormap6 = 0
    if self.hasInputFromPort('colormap6') :
      colormap6 = self.getInputFromPort('colormap6')
    results = sr_py.InsertColorMapsIntoBundle(bundle,colormap1,colormap2,colormap3,colormap4,colormap5,colormap6,p_colormap1_name,p_colormap2_name,p_colormap3_name,p_colormap4_name,p_colormap5_name,p_colormap6_name,p_replace1,p_replace2,p_replace3,p_replace4,p_replace5,p_replace6,p_bundlename)
    self.setResult('bundle', results)

class scirun_JoinStrings(Module) :
  def compute(self) :
    input = ''
    if self.hasInputFromPort('input') :
      input = self.getInputFromPort('input')
    results = sr_py.JoinStrings(input)
    self.setResult('Output', results)

class scirun_CreateViewerClockIcon(Module) :
  def compute(self) :
    p_type = 0
    if self.hasInputFromPort('p_type') :
      p_type = self.getInputFromPort('p_type')
    p_bbox = 1
    if self.hasInputFromPort('p_bbox') :
      p_bbox = self.getInputFromPort('p_bbox')
    p_format = '%8.3f seconds'
    if self.hasInputFromPort('p_format') :
      p_format = self.getInputFromPort('p_format')
    p_min = 0.0
    if self.hasInputFromPort('p_min') :
      p_min = self.getInputFromPort('p_min')
    p_max = 1.0
    if self.hasInputFromPort('p_max') :
      p_max = self.getInputFromPort('p_max')
    p_current = '0'
    if self.hasInputFromPort('p_current') :
      p_current = self.getInputFromPort('p_current')
    p_size = 100
    if self.hasInputFromPort('p_size') :
      p_size = self.getInputFromPort('p_size')
    p_location_x = -0.96875
    if self.hasInputFromPort('p_location_x') :
      p_location_x = self.getInputFromPort('p_location_x')
    p_location_y = 0.96875
    if self.hasInputFromPort('p_location_y') :
      p_location_y = self.getInputFromPort('p_location_y')
    p_color_r = 1.0
    if self.hasInputFromPort('p_color_r') :
      p_color_r = self.getInputFromPort('p_color_r')
    p_color_g = 1.0
    if self.hasInputFromPort('p_color_g') :
      p_color_g = self.getInputFromPort('p_color_g')
    p_color_b = 1.0
    if self.hasInputFromPort('p_color_b') :
      p_color_b = self.getInputFromPort('p_color_b')
    Time_Matrix = 0
    if self.hasInputFromPort('Time Matrix') :
      Time_Matrix = self.getInputFromPort('Time Matrix')
    Time_Nrrd = 0
    if self.hasInputFromPort('Time Nrrd') :
      Time_Nrrd = self.getInputFromPort('Time Nrrd')
    results = sr_py.CreateViewerClockIcon(Time_Matrix,Time_Nrrd,p_type,p_bbox,p_format,p_min,p_max,p_current,p_size,p_location_x,p_location_y,p_color_r,p_color_g,p_color_b)
    self.setResult('Clock', results)

class scirun_ReportMatrixRowMeasure(Module) :
  def compute(self) :
    p_method = 'Sum'
    if self.hasInputFromPort('p_method') :
      p_method = self.getInputFromPort('p_method')
    Matrix = 0
    if self.hasInputFromPort('Matrix') :
      Matrix = self.getInputFromPort('Matrix')
    results = sr_py.ReportMatrixRowMeasure(Matrix,p_method)
    self.setResult('Vector', results)

class scirun_RemoveHexVolSheet(Module) :
  def compute(self) :
    p_edge_list = 'No values present.'
    if self.hasInputFromPort('p_edge_list') :
      p_edge_list = self.getInputFromPort('p_edge_list')
    HexField = 0
    if self.hasInputFromPort('HexField') :
      HexField = self.getInputFromPort('HexField')
    results = sr_py.RemoveHexVolSheet(HexField,p_edge_list)
    self.setResult('NewHexField', results[0])
    self.setResult('ExtractedHexes', results[1])

class scirun_ReorderMatrixByCuthillMcKee(Module) :
  def compute(self) :
    Matrix = 0
    if self.hasInputFromPort('Matrix') :
      Matrix = self.getInputFromPort('Matrix')
    results = sr_py.ReorderMatrixByCuthillMcKee(Matrix)
    self.setResult('Matrix', results[0])
    self.setResult('Mapping', results[1])
    self.setResult('InverseMapping', results[2])

class scirun_ReportMatrixInfo(Module) :
  def compute(self) :
    Input = 0
    if self.hasInputFromPort('Input') :
      Input = self.getInputFromPort('Input')
    results = sr_py.ReportMatrixInfo(Input)
    self.setResult('NumRows', results[0])
    self.setResult('NumCols', results[1])
    self.setResult('NumElements', results[2])

class scirun_SubsampleStructuredFieldByIndices(Module) :
  def compute(self) :
    p_power_app = 0
    if self.hasInputFromPort('p_power_app') :
      p_power_app = self.getInputFromPort('p_power_app')
    p_wrap = 0
    if self.hasInputFromPort('p_wrap') :
      p_wrap = self.getInputFromPort('p_wrap')
    p_dims = 3
    if self.hasInputFromPort('p_dims') :
      p_dims = self.getInputFromPort('p_dims')
    p_dim_i = 2
    if self.hasInputFromPort('p_dim_i') :
      p_dim_i = self.getInputFromPort('p_dim_i')
    p_dim_j = 2
    if self.hasInputFromPort('p_dim_j') :
      p_dim_j = self.getInputFromPort('p_dim_j')
    p_dim_k = 2
    if self.hasInputFromPort('p_dim_k') :
      p_dim_k = self.getInputFromPort('p_dim_k')
    p_start_i = 0
    if self.hasInputFromPort('p_start_i') :
      p_start_i = self.getInputFromPort('p_start_i')
    p_start_j = 0
    if self.hasInputFromPort('p_start_j') :
      p_start_j = self.getInputFromPort('p_start_j')
    p_start_k = 0
    if self.hasInputFromPort('p_start_k') :
      p_start_k = self.getInputFromPort('p_start_k')
    p_stop_i = 1
    if self.hasInputFromPort('p_stop_i') :
      p_stop_i = self.getInputFromPort('p_stop_i')
    p_stop_j = 1
    if self.hasInputFromPort('p_stop_j') :
      p_stop_j = self.getInputFromPort('p_stop_j')
    p_stop_k = 1
    if self.hasInputFromPort('p_stop_k') :
      p_stop_k = self.getInputFromPort('p_stop_k')
    p_stride_i = 1
    if self.hasInputFromPort('p_stride_i') :
      p_stride_i = self.getInputFromPort('p_stride_i')
    p_stride_j = 1
    if self.hasInputFromPort('p_stride_j') :
      p_stride_j = self.getInputFromPort('p_stride_j')
    p_stride_k = 1
    if self.hasInputFromPort('p_stride_k') :
      p_stride_k = self.getInputFromPort('p_stride_k')
    p_wrap_i = 0
    if self.hasInputFromPort('p_wrap_i') :
      p_wrap_i = self.getInputFromPort('p_wrap_i')
    p_wrap_j = 0
    if self.hasInputFromPort('p_wrap_j') :
      p_wrap_j = self.getInputFromPort('p_wrap_j')
    p_wrap_k = 0
    if self.hasInputFromPort('p_wrap_k') :
      p_wrap_k = self.getInputFromPort('p_wrap_k')
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    Input_Matrix = 0
    if self.hasInputFromPort('Input Matrix') :
      Input_Matrix = self.getInputFromPort('Input Matrix')
    results = sr_py.SubsampleStructuredFieldByIndices(Input_Field,Input_Matrix,p_power_app,p_wrap,p_dims,p_dim_i,p_dim_j,p_dim_k,p_start_i,p_start_j,p_start_k,p_stop_i,p_stop_j,p_stop_k,p_stride_i,p_stride_j,p_stride_k,p_wrap_i,p_wrap_j,p_wrap_k)
    self.setResult('Output Field', results[0])
    self.setResult('Output Matrix', results[1])

class scirun_CalculateDistanceToField(Module) :
  def compute(self) :
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    ObjectField = 0
    if self.hasInputFromPort('ObjectField') :
      ObjectField = self.getInputFromPort('ObjectField')
    results = sr_py.CalculateDistanceToField(Field,ObjectField)
    self.setResult('DistanceField', results)

class scirun_GetAllSegmentationBoundaries(Module) :
  def compute(self) :
    Segmentations = 0
    if self.hasInputFromPort('Segmentations') :
      Segmentations = self.getInputFromPort('Segmentations')
    results = sr_py.GetAllSegmentationBoundaries(Segmentations)
    self.setResult('Boundaries', results)

class scirun_ClipFieldWithSeed(Module) :
  def compute(self) :
    p_mode = 'allnodes'
    if self.hasInputFromPort('p_mode') :
      p_mode = self.getInputFromPort('p_mode')
    p_function = 'return (fx < 0);'
    if self.hasInputFromPort('p_function') :
      p_function = self.getInputFromPort('p_function')
    Function = ''
    if self.hasInputFromPort('Function') :
      Function = self.getInputFromPort('Function')
    Input = 0
    if self.hasInputFromPort('Input') :
      Input = self.getInputFromPort('Input')
    Seeds = 0
    if self.hasInputFromPort('Seeds') :
      Seeds = self.getInputFromPort('Seeds')
    results = sr_py.ClipFieldWithSeed(Function,Input,Seeds,p_mode,p_function)
    self.setResult('Clipped', results[0])
    self.setResult('Mapping', results[1])
    self.setResult('MaskVector', results[2])

class scirun_CreateParameterBundle(Module) :
  def compute(self) :
    p_data = '0 "example field" string "example" ""} {0 "example scalar" scalar 1.0 ""} '
    if self.hasInputFromPort('p_data') :
      p_data = self.getInputFromPort('p_data')
    p_new_field_count = 1
    if self.hasInputFromPort('p_new_field_count') :
      p_new_field_count = self.getInputFromPort('p_new_field_count')
    p_update_all = '::SCIRun_Bundle_CreateParameterBundle_0 update_all_data'
    if self.hasInputFromPort('p_update_all') :
      p_update_all = self.getInputFromPort('p_update_all')
    results = sr_py.CreateParameterBundle(p_data,p_new_field_count,p_update_all)
    self.setResult('ParameterList', results)

class scirun_CollectPointClouds(Module) :
  def compute(self) :
    p_num_fields = 1
    if self.hasInputFromPort('p_num_fields') :
      p_num_fields = self.getInputFromPort('p_num_fields')
    Point_Cloud = 0
    if self.hasInputFromPort('Point Cloud') :
      Point_Cloud = self.getInputFromPort('Point Cloud')
    results = sr_py.CollectPointClouds(Point_Cloud,p_num_fields)
    self.setResult('Curve', results)

class scirun_InsertEnvironmentIntoBundle(Module) :
  def compute(self) :
    results = sr_py.InsertEnvironmentIntoBundle()
    self.setResult('Environment', results)

class scirun_ScaleFieldMeshAndData(Module) :
  def compute(self) :
    p_datascale = 1
    if self.hasInputFromPort('p_datascale') :
      p_datascale = self.getInputFromPort('p_datascale')
    p_geomscale = 1
    if self.hasInputFromPort('p_geomscale') :
      p_geomscale = self.getInputFromPort('p_geomscale')
    p_usegeomcenter = 1
    if self.hasInputFromPort('p_usegeomcenter') :
      p_usegeomcenter = self.getInputFromPort('p_usegeomcenter')
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    GeomScaleFactor = 0
    if self.hasInputFromPort('GeomScaleFactor') :
      GeomScaleFactor = self.getInputFromPort('GeomScaleFactor')
    DataScaleFactor = 0
    if self.hasInputFromPort('DataScaleFactor') :
      DataScaleFactor = self.getInputFromPort('DataScaleFactor')
    results = sr_py.ScaleFieldMeshAndData(Field,GeomScaleFactor,DataScaleFactor,p_datascale,p_geomscale,p_usegeomcenter)
    self.setResult('Field', results)

class scirun_ConvertFieldsToTexture(Module) :
  def compute(self) :
    p_vmin = 0.0
    if self.hasInputFromPort('p_vmin') :
      p_vmin = self.getInputFromPort('p_vmin')
    p_vmax = 1.0
    if self.hasInputFromPort('p_vmax') :
      p_vmax = self.getInputFromPort('p_vmax')
    p_gmin = 0.0
    if self.hasInputFromPort('p_gmin') :
      p_gmin = self.getInputFromPort('p_gmin')
    p_gmax = 1.0
    if self.hasInputFromPort('p_gmax') :
      p_gmax = self.getInputFromPort('p_gmax')
    p_is_fixed = 0
    if self.hasInputFromPort('p_is_fixed') :
      p_is_fixed = self.getInputFromPort('p_is_fixed')
    p_card_mem = 16
    if self.hasInputFromPort('p_card_mem') :
      p_card_mem = self.getInputFromPort('p_card_mem')
    p_card_mem_auto = 1
    if self.hasInputFromPort('p_card_mem_auto') :
      p_card_mem_auto = self.getInputFromPort('p_card_mem_auto')
    p_histogram = 1
    if self.hasInputFromPort('p_histogram') :
      p_histogram = self.getInputFromPort('p_histogram')
    p_gamma = 0.5
    if self.hasInputFromPort('p_gamma') :
      p_gamma = self.getInputFromPort('p_gamma')
    Value_Field = 0
    if self.hasInputFromPort('Value Field') :
      Value_Field = self.getInputFromPort('Value Field')
    Gradient_Magnitude_Field = 0
    if self.hasInputFromPort('Gradient Magnitude Field') :
      Gradient_Magnitude_Field = self.getInputFromPort('Gradient Magnitude Field')
    results = sr_py.ConvertFieldsToTexture(Value_Field,Gradient_Magnitude_Field,p_vmin,p_vmax,p_gmin,p_gmax,p_is_fixed,p_card_mem,p_card_mem_auto,p_histogram,p_gamma)
    self.setResult('Texture', results[0])
    self.setResult('JointHistoGram', results[1])

class scirun_SplitNodesByDomain(Module) :
  def compute(self) :
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    results = sr_py.SplitNodesByDomain(Field)
    self.setResult('SplitField', results)

class scirun_RemoveZerosFromMatrix(Module) :
  def compute(self) :
    p_row_or_col = 'row'
    if self.hasInputFromPort('p_row_or_col') :
      p_row_or_col = self.getInputFromPort('p_row_or_col')
    Matrix = 0
    if self.hasInputFromPort('Matrix') :
      Matrix = self.getInputFromPort('Matrix')
    results = sr_py.RemoveZerosFromMatrix(Matrix,p_row_or_col)
    self.setResult('Matrix', results)

class scirun_GetNetworkFileName(Module) :
  def compute(self) :
    results = sr_py.GetNetworkFileName()
    self.setResult('String', results)

class scirun_RemoveZeroRowsAndColumns(Module) :
  def compute(self) :
    Matrix = 0
    if self.hasInputFromPort('Matrix') :
      Matrix = self.getInputFromPort('Matrix')
    results = sr_py.RemoveZeroRowsAndColumns(Matrix)
    self.setResult('ReducedMatrix', results[0])
    self.setResult('LeftMapping', results[1])
    self.setResult('RightMapping', results[2])

class scirun_ColorMap2DSemantics(Module) :
  def compute(self) :
    Input_Colormap = 0
    if self.hasInputFromPort('Input Colormap') :
      Input_Colormap = self.getInputFromPort('Input Colormap')
    results = sr_py.ColorMap2DSemantics(Input_Colormap)
    self.setResult('Output Colormap', results)

class SCIRun_Bundle(Constant):
  def compute(self): 
    pass
class SCIRun_Field(Constant):
  def compute(self): 
    pass
class SCIRun_Matrix(Constant):
  def compute(self): 
    pass
class SCIRun_Geometry(Constant):
  def compute(self): 
    pass
class SCIRun_Nrrd(Constant):
  def compute(self): 
    pass
class SCIRun_ColorMap(Constant):
  def compute(self): 
    pass
class SCIRun_ColorMap2(Constant):
  def compute(self): 
    pass
class SCIRun_Path(Constant):
  def compute(self): 
    pass
class SCIRun_Texture(Constant):
  def compute(self): 
    pass
class SCIRun_Time(Constant):
  def compute(self): 
    pass

def initialize(*args, **keywords):

  env = []
  for k in os.environ.keys() :
    estr = "%s=%s" % (k, os.environ[k])
    env.append(estr)
  sr_py.init_sr_py(env)

  reg = core.modules.module_registry

  reg.add_module(SCIRun_Time)

  reg.add_module(SCIRun_Texture)

  reg.add_module(SCIRun_Path)

  reg.add_module(SCIRun_ColorMap2)

  reg.add_module(SCIRun_ColorMap)

  reg.add_module(SCIRun_Nrrd)

  reg.add_module(SCIRun_Geometry)

  reg.add_module(SCIRun_Matrix)

  reg.add_module(SCIRun_Field)

  reg.add_module(SCIRun_Bundle)

  reg.add_module(scirun_WriteBundle)
  reg.add_input_port(scirun_WriteBundle, 'p_filetype',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_WriteBundle, 'p_confirm',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_WriteBundle, 'p_confirm_once',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_WriteBundle, 'bundle',
                   (SCIRun_Bundle, "SCIRun_Bundle"))
  reg.add_input_port(scirun_WriteBundle, 'Filename',
                   (core.modules.basic_modules.String, 'tip'))

  reg.add_module(scirun_JoinFields)
  reg.add_input_port(scirun_JoinFields, 'p_tolerance',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_JoinFields, 'p_force_nodemerge',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_JoinFields, 'p_force_pointcloud',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_JoinFields, 'p_matchval',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_JoinFields, 'p_meshonly',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_JoinFields, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_JoinFields, 'Output Field', 
                    (SCIRun_Field, 'Output Field'))

  reg.add_module(scirun_ApplyMappingMatrix)
  reg.add_input_port(scirun_ApplyMappingMatrix, 'Source',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_ApplyMappingMatrix, 'Destination',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_ApplyMappingMatrix, 'Mapping',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_ApplyMappingMatrix, 'Output', 
                    (SCIRun_Field, 'Output'))

  reg.add_module(scirun_TransformPlanarMesh)
  reg.add_input_port(scirun_TransformPlanarMesh, 'p_axis',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_TransformPlanarMesh, 'p_invert',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_TransformPlanarMesh, 'p_trans_x',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_TransformPlanarMesh, 'p_trans_y',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_TransformPlanarMesh, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_TransformPlanarMesh, 'Index Matrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_TransformPlanarMesh, 'Transformed Field', 
                    (SCIRun_Field, 'Transformed Field'))

  reg.add_module(scirun_MaskLatVolWithTriSurf)
  reg.add_input_port(scirun_MaskLatVolWithTriSurf, 'LatVolField',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_MaskLatVolWithTriSurf, 'TriSurfField',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_MaskLatVolWithTriSurf, 'LatVol Mask', 
                    (SCIRun_Field, 'LatVol Mask'))

  reg.add_module(scirun_RefineMeshByIsovalue)
  reg.add_input_port(scirun_RefineMeshByIsovalue, 'p_isoval',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_RefineMeshByIsovalue, 'p_lte',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_RefineMeshByIsovalue, 'Input',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_RefineMeshByIsovalue, 'Optional Isovalue',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_RefineMeshByIsovalue, 'Refined', 
                    (SCIRun_Field, 'Refined'))
  reg.add_output_port(scirun_RefineMeshByIsovalue, 'Mapping', 
                    (SCIRun_Matrix, 'Mapping'))

  reg.add_module(scirun_ViewScene)
  reg.add_input_port(scirun_ViewScene, 'Geometry',
                   (SCIRun_Geometry, "SCIRun_Geometry"))

  reg.add_module(scirun_ReportColumnMatrixMisfit)
  reg.add_input_port(scirun_ReportColumnMatrixMisfit, 'p_have_ui',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ReportColumnMatrixMisfit, 'p_methodTCL',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReportColumnMatrixMisfit, 'p_pTCL',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReportColumnMatrixMisfit, 'Vec1',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(scirun_ReportColumnMatrixMisfit, 'Vec2',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_ReportColumnMatrixMisfit, 'Error Out', 
                    (SCIRun_Matrix, 'Error Out'))

  reg.add_module(scirun_EvaluateLinAlgGeneral)
  reg.add_input_port(scirun_EvaluateLinAlgGeneral, 'p_function',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_EvaluateLinAlgGeneral, 'i1',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(scirun_EvaluateLinAlgGeneral, 'i2',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(scirun_EvaluateLinAlgGeneral, 'i3',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(scirun_EvaluateLinAlgGeneral, 'i4',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(scirun_EvaluateLinAlgGeneral, 'i5',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_EvaluateLinAlgGeneral, 'o1', 
                    (SCIRun_Matrix, 'o1'))
  reg.add_output_port(scirun_EvaluateLinAlgGeneral, 'o2', 
                    (SCIRun_Matrix, 'o2'))
  reg.add_output_port(scirun_EvaluateLinAlgGeneral, 'o3', 
                    (SCIRun_Matrix, 'o3'))
  reg.add_output_port(scirun_EvaluateLinAlgGeneral, 'o4', 
                    (SCIRun_Matrix, 'o4'))
  reg.add_output_port(scirun_EvaluateLinAlgGeneral, 'o5', 
                    (SCIRun_Matrix, 'o5'))

  reg.add_module(scirun_AppendMatrix)
  reg.add_input_port(scirun_AppendMatrix, 'p_row_or_column',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_AppendMatrix, 'BaseMatrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(scirun_AppendMatrix, 'AppendMatrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_AppendMatrix, 'Matrix', 
                    (SCIRun_Matrix, 'Matrix'))

  reg.add_module(scirun_CreateDataArray)
  reg.add_input_port(scirun_CreateDataArray, 'p_function',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateDataArray, 'p_format',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateDataArray, 'Size',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(scirun_CreateDataArray, 'Function',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_input_port(scirun_CreateDataArray, 'Array',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_CreateDataArray, 'DataArray', 
                    (SCIRun_Matrix, 'DataArray'))

  reg.add_module(scirun_FairMesh)
  reg.add_input_port(scirun_FairMesh, 'p_iterations',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_FairMesh, 'p_method',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_FairMesh, 'Input Mesh',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_FairMesh, 'Faired Mesh', 
                    (SCIRun_Field, 'Faired Mesh'))

  reg.add_module(scirun_EvaluateLinAlgBinary)
  reg.add_input_port(scirun_EvaluateLinAlgBinary, 'p_op',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_EvaluateLinAlgBinary, 'p_function',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_EvaluateLinAlgBinary, 'A',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(scirun_EvaluateLinAlgBinary, 'B',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_EvaluateLinAlgBinary, 'Output', 
                    (SCIRun_Matrix, 'Output'))

  reg.add_module(scirun_PrintMatrixIntoString)
  reg.add_input_port(scirun_PrintMatrixIntoString, 'p_formatstring',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_PrintMatrixIntoString, 'Format',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_input_port(scirun_PrintMatrixIntoString, 'Input',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_PrintMatrixIntoString, 'Output', 
                    (core.modules.basic_modules.String, 'Output'))

  reg.add_module(scirun_SetFieldProperty)
  reg.add_input_port(scirun_SetFieldProperty, 'p_num_entries',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_SetFieldProperty, 'p_property',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_SetFieldProperty, 'p_type',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_SetFieldProperty, 'p_value',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_SetFieldProperty, 'p_readonly',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_SetFieldProperty, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_SetFieldProperty, 'Field', 
                    (SCIRun_Field, 'Field'))

  reg.add_module(scirun_ConvertFieldBasis)
  reg.add_input_port(scirun_ConvertFieldBasis, 'p_output_basis',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ConvertFieldBasis, 'Input',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_ConvertFieldBasis, 'Output', 
                    (SCIRun_Field, 'Output'))
  reg.add_output_port(scirun_ConvertFieldBasis, 'Mapping', 
                    (SCIRun_Matrix, 'Mapping'))

  reg.add_module(scirun_ReportMeshQualityMeasures)
  reg.add_input_port(scirun_ReportMeshQualityMeasures, 'Input',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_ReportMeshQualityMeasures, 'Checked', 
                    (SCIRun_Nrrd, 'Checked'))

  reg.add_module(scirun_SelectAndSetFieldData)
  reg.add_input_port(scirun_SelectAndSetFieldData, 'p_selection1',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_SelectAndSetFieldData, 'p_function1',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_SelectAndSetFieldData, 'p_selection2',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_SelectAndSetFieldData, 'p_function2',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_SelectAndSetFieldData, 'p_selection3',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_SelectAndSetFieldData, 'p_function3',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_SelectAndSetFieldData, 'p_selection4',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_SelectAndSetFieldData, 'p_function4',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_SelectAndSetFieldData, 'p_functiondef',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_SelectAndSetFieldData, 'p_format',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_SelectAndSetFieldData, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_SelectAndSetFieldData, 'Array',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_SelectAndSetFieldData, 'Field', 
                    (SCIRun_Field, 'Field'))

  reg.add_module(scirun_GetColorMapsFromBundle)
  reg.add_input_port(scirun_GetColorMapsFromBundle, 'p_colormap1_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetColorMapsFromBundle, 'p_colormap2_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetColorMapsFromBundle, 'p_colormap3_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetColorMapsFromBundle, 'p_colormap4_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetColorMapsFromBundle, 'p_colormap5_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetColorMapsFromBundle, 'p_colormap6_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetColorMapsFromBundle, 'p_colormap_selection',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetColorMapsFromBundle, 'bundle',
                   (SCIRun_Bundle, "SCIRun_Bundle"))
  reg.add_output_port(scirun_GetColorMapsFromBundle, 'bundle', 
                    (SCIRun_Bundle, 'bundle'))
  reg.add_output_port(scirun_GetColorMapsFromBundle, 'colormap1', 
                    (SCIRun_ColorMap, 'colormap1'))
  reg.add_output_port(scirun_GetColorMapsFromBundle, 'colormap2', 
                    (SCIRun_ColorMap, 'colormap2'))
  reg.add_output_port(scirun_GetColorMapsFromBundle, 'colormap3', 
                    (SCIRun_ColorMap, 'colormap3'))
  reg.add_output_port(scirun_GetColorMapsFromBundle, 'colormap4', 
                    (SCIRun_ColorMap, 'colormap4'))
  reg.add_output_port(scirun_GetColorMapsFromBundle, 'colormap5', 
                    (SCIRun_ColorMap, 'colormap5'))
  reg.add_output_port(scirun_GetColorMapsFromBundle, 'colormap6', 
                    (SCIRun_ColorMap, 'colormap6'))

  reg.add_module(scirun_CreateStructHex)
  reg.add_input_port(scirun_CreateStructHex, 'p_sizex',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_CreateStructHex, 'p_sizey',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_CreateStructHex, 'p_sizez',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_CreateStructHex, 'p_padpercent',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_CreateStructHex, 'p_data_at',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateStructHex, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_CreateStructHex, 'Output Sample Field', 
                    (SCIRun_Field, 'Output Sample Field'))

  reg.add_module(scirun_ShowColorMap)
  reg.add_input_port(scirun_ShowColorMap, 'p_length',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ShowColorMap, 'p_side',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ShowColorMap, 'p_numlabels',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowColorMap, 'p_scale',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ShowColorMap, 'p_numsigdigits',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowColorMap, 'p_units',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ShowColorMap, 'p_color_r',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ShowColorMap, 'p_color_g',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ShowColorMap, 'p_color_b',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ShowColorMap, 'p_text_fontsize',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowColorMap, 'p_extra_padding',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowColorMap, 'ColorMap',
                   (SCIRun_ColorMap, "SCIRun_ColorMap"))
  reg.add_output_port(scirun_ShowColorMap, 'Geometry', 
                    (SCIRun_Geometry, 'Geometry'))

  reg.add_module(scirun_CalculateFieldData3)
  reg.add_input_port(scirun_CalculateFieldData3, 'p_function',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CalculateFieldData3, 'p_format',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CalculateFieldData3, 'Field1',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_CalculateFieldData3, 'Field2',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_CalculateFieldData3, 'Field3',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_CalculateFieldData3, 'Function',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_input_port(scirun_CalculateFieldData3, 'Array',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_CalculateFieldData3, 'Field', 
                    (SCIRun_Field, 'Field'))

  reg.add_module(scirun_InsertFieldsIntoBundle)
  reg.add_input_port(scirun_InsertFieldsIntoBundle, 'p_field1_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertFieldsIntoBundle, 'p_field2_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertFieldsIntoBundle, 'p_field3_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertFieldsIntoBundle, 'p_field4_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertFieldsIntoBundle, 'p_field5_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertFieldsIntoBundle, 'p_field6_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertFieldsIntoBundle, 'p_replace1',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_InsertFieldsIntoBundle, 'p_replace2',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_InsertFieldsIntoBundle, 'p_replace3',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_InsertFieldsIntoBundle, 'p_replace4',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_InsertFieldsIntoBundle, 'p_replace5',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_InsertFieldsIntoBundle, 'p_replace6',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_InsertFieldsIntoBundle, 'p_bundlename',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertFieldsIntoBundle, 'bundle',
                   (SCIRun_Bundle, "SCIRun_Bundle"))
  reg.add_input_port(scirun_InsertFieldsIntoBundle, 'field1',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_InsertFieldsIntoBundle, 'field2',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_InsertFieldsIntoBundle, 'field3',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_InsertFieldsIntoBundle, 'field4',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_InsertFieldsIntoBundle, 'field5',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_InsertFieldsIntoBundle, 'field6',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_InsertFieldsIntoBundle, 'bundle', 
                    (SCIRun_Bundle, 'bundle'))

  reg.add_module(scirun_CreateAndEditColorMap2D)
  reg.add_input_port(scirun_CreateAndEditColorMap2D, 'p_histo',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_CreateAndEditColorMap2D, 'p_selected_widget',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_CreateAndEditColorMap2D, 'p_selected_object',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_CreateAndEditColorMap2D, 'p_num_entries',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_CreateAndEditColorMap2D, 'p_marker',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateAndEditColorMap2D, 'Input Colormap',
                   (SCIRun_ColorMap2, "SCIRun_ColorMap2"))
  reg.add_input_port(scirun_CreateAndEditColorMap2D, 'Histogram',
                   (SCIRun_Nrrd, "SCIRun_Nrrd"))
  reg.add_output_port(scirun_CreateAndEditColorMap2D, 'Output Colormap', 
                    (SCIRun_ColorMap2, 'Output Colormap'))

  reg.add_module(scirun_CreateDataArrayFromIndices)
  reg.add_input_port(scirun_CreateDataArrayFromIndices, 'Indices',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(scirun_CreateDataArrayFromIndices, 'Template',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_CreateDataArrayFromIndices, 'DataArray', 
                    (SCIRun_Matrix, 'DataArray'))

  reg.add_module(scirun_ReportDataArrayInfo)
  reg.add_input_port(scirun_ReportDataArrayInfo, 'DataArray',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_ReportDataArrayInfo, 'NumElements', 
                    (SCIRun_Matrix, 'NumElements'))

  reg.add_module(scirun_ConvertMaskVectorToMappingMatrix)
  reg.add_input_port(scirun_ConvertMaskVectorToMappingMatrix, 'MaskVector',
                   (SCIRun_Nrrd, "SCIRun_Nrrd"))
  reg.add_output_port(scirun_ConvertMaskVectorToMappingMatrix, 'MappingMatrix', 
                    (SCIRun_Matrix, 'MappingMatrix'))

  reg.add_module(scirun_GetFieldsFromBundle)
  reg.add_input_port(scirun_GetFieldsFromBundle, 'p_field1_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetFieldsFromBundle, 'p_field2_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetFieldsFromBundle, 'p_field3_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetFieldsFromBundle, 'p_field4_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetFieldsFromBundle, 'p_field5_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetFieldsFromBundle, 'p_field6_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetFieldsFromBundle, 'p_field_selection',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetFieldsFromBundle, 'bundle',
                   (SCIRun_Bundle, "SCIRun_Bundle"))
  reg.add_output_port(scirun_GetFieldsFromBundle, 'bundle', 
                    (SCIRun_Bundle, 'bundle'))
  reg.add_output_port(scirun_GetFieldsFromBundle, 'field1', 
                    (SCIRun_Field, 'field1'))
  reg.add_output_port(scirun_GetFieldsFromBundle, 'field2', 
                    (SCIRun_Field, 'field2'))
  reg.add_output_port(scirun_GetFieldsFromBundle, 'field3', 
                    (SCIRun_Field, 'field3'))
  reg.add_output_port(scirun_GetFieldsFromBundle, 'field4', 
                    (SCIRun_Field, 'field4'))
  reg.add_output_port(scirun_GetFieldsFromBundle, 'field5', 
                    (SCIRun_Field, 'field5'))
  reg.add_output_port(scirun_GetFieldsFromBundle, 'field6', 
                    (SCIRun_Field, 'field6'))

  reg.add_module(scirun_ReportScalarFieldStats)
  reg.add_input_port(scirun_ReportScalarFieldStats, 'p_min',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ReportScalarFieldStats, 'p_max',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ReportScalarFieldStats, 'p_mean',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ReportScalarFieldStats, 'p_median',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ReportScalarFieldStats, 'p_sigma',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ReportScalarFieldStats, 'p_is_fixed',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ReportScalarFieldStats, 'p_nbuckets',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ReportScalarFieldStats, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))

  reg.add_module(scirun_ShowField)
  reg.add_input_port(scirun_ShowField, 'p_nodes_on',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowField, 'p_nodes_transparency',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowField, 'p_nodes_color_type',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowField, 'p_nodes_display_type',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ShowField, 'p_edges_on',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowField, 'p_edges_transparency',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowField, 'p_edges_color_type',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowField, 'p_edges_display_type',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ShowField, 'p_faces_on',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowField, 'p_faces_transparency',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowField, 'p_faces_color_type',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowField, 'p_faces_normals',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowField, 'p_faces_usetexture',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowField, 'p_text_on',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowField, 'p_text_color_type',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowField, 'p_text_color_r',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ShowField, 'p_text_color_g',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ShowField, 'p_text_color_b',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ShowField, 'p_text_backface_cull',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowField, 'p_text_always_visible',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowField, 'p_text_fontsize',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowField, 'p_text_precision',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowField, 'p_text_render_locations',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowField, 'p_text_show_data',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowField, 'p_text_show_nodes',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowField, 'p_text_show_edges',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowField, 'p_text_show_faces',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowField, 'p_text_show_cells',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowField, 'p_def_color_r',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ShowField, 'p_def_color_g',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ShowField, 'p_def_color_b',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ShowField, 'p_def_color_a',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ShowField, 'p_nodes_scale',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ShowField, 'p_nodes_scaleNV',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ShowField, 'p_edges_scale',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ShowField, 'p_edges_scaleNV',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ShowField, 'p_active_tab',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ShowField, 'p_interactive_mode',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ShowField, 'p_show_progress',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowField, 'p_field_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ShowField, 'p_field_name_override',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowField, 'p_nodes_resolution',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowField, 'p_edges_resolution',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowField, 'p_approx_div',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowField, 'p_use_default_size',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowField, 'Mesh',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_ShowField, 'ColorMap',
                   (SCIRun_ColorMap, "SCIRun_ColorMap"))
  reg.add_output_port(scirun_ShowField, 'Scene Graph', 
                    (SCIRun_Geometry, 'Scene Graph'))

  reg.add_module(scirun_CreateVectorArray)
  reg.add_input_port(scirun_CreateVectorArray, 'X',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(scirun_CreateVectorArray, 'Y',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(scirun_CreateVectorArray, 'Z',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_CreateVectorArray, 'Vector', 
                    (SCIRun_Matrix, 'Vector'))

  reg.add_module(scirun_SynchronizeGeometry)
  reg.add_input_port(scirun_SynchronizeGeometry, 'p_enforce',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_SynchronizeGeometry, 'Input Geometry',
                   (SCIRun_Geometry, "SCIRun_Geometry"))
  reg.add_output_port(scirun_SynchronizeGeometry, 'Output Geometry', 
                    (SCIRun_Geometry, 'Output Geometry'))

  reg.add_module(scirun_SolveLinearSystem)
  reg.add_input_port(scirun_SolveLinearSystem, 'p_target_error',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_SolveLinearSystem, 'p_flops',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_SolveLinearSystem, 'p_floprate',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_SolveLinearSystem, 'p_memrefs',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_SolveLinearSystem, 'p_memrate',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_SolveLinearSystem, 'p_orig_error',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_SolveLinearSystem, 'p_current_error',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_SolveLinearSystem, 'p_method',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_SolveLinearSystem, 'p_precond',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_SolveLinearSystem, 'p_iteration',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_SolveLinearSystem, 'p_maxiter',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_SolveLinearSystem, 'p_use_previous_soln',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_SolveLinearSystem, 'p_emit_partial',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_SolveLinearSystem, 'p_emit_iter',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_SolveLinearSystem, 'p_status',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_SolveLinearSystem, 'p_np',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_SolveLinearSystem, 'Matrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(scirun_SolveLinearSystem, 'RHS',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_SolveLinearSystem, 'Solution', 
                    (SCIRun_Matrix, 'Solution'))

  reg.add_module(scirun_SetFieldData)
  reg.add_input_port(scirun_SetFieldData, 'p_keepscalartype',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_SetFieldData, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_SetFieldData, 'Matrix Data',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(scirun_SetFieldData, 'Nrrd Data',
                   (SCIRun_Nrrd, "SCIRun_Nrrd"))
  reg.add_output_port(scirun_SetFieldData, 'Field', 
                    (SCIRun_Field, 'Field'))

  reg.add_module(scirun_InsertColorMap2sIntoBundle)
  reg.add_input_port(scirun_InsertColorMap2sIntoBundle, 'p_colormap21_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertColorMap2sIntoBundle, 'p_colormap22_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertColorMap2sIntoBundle, 'p_colormap23_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertColorMap2sIntoBundle, 'p_colormap24_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertColorMap2sIntoBundle, 'p_colormap25_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertColorMap2sIntoBundle, 'p_colormap26_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertColorMap2sIntoBundle, 'p_replace1',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_InsertColorMap2sIntoBundle, 'p_replace2',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_InsertColorMap2sIntoBundle, 'p_replace3',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_InsertColorMap2sIntoBundle, 'p_replace4',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_InsertColorMap2sIntoBundle, 'p_replace5',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_InsertColorMap2sIntoBundle, 'p_replace6',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_InsertColorMap2sIntoBundle, 'p_bundlename',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertColorMap2sIntoBundle, 'bundle',
                   (SCIRun_Bundle, "SCIRun_Bundle"))
  reg.add_input_port(scirun_InsertColorMap2sIntoBundle, 'colormap21',
                   (SCIRun_ColorMap2, "SCIRun_ColorMap2"))
  reg.add_input_port(scirun_InsertColorMap2sIntoBundle, 'colormap22',
                   (SCIRun_ColorMap2, "SCIRun_ColorMap2"))
  reg.add_input_port(scirun_InsertColorMap2sIntoBundle, 'colormap23',
                   (SCIRun_ColorMap2, "SCIRun_ColorMap2"))
  reg.add_input_port(scirun_InsertColorMap2sIntoBundle, 'colormap24',
                   (SCIRun_ColorMap2, "SCIRun_ColorMap2"))
  reg.add_input_port(scirun_InsertColorMap2sIntoBundle, 'colormap25',
                   (SCIRun_ColorMap2, "SCIRun_ColorMap2"))
  reg.add_input_port(scirun_InsertColorMap2sIntoBundle, 'colormap26',
                   (SCIRun_ColorMap2, "SCIRun_ColorMap2"))
  reg.add_output_port(scirun_InsertColorMap2sIntoBundle, 'bundle', 
                    (SCIRun_Bundle, 'bundle'))

  reg.add_module(scirun_ExtractIsosurface)
  reg.add_input_port(scirun_ExtractIsosurface, 'p_isoval_min',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ExtractIsosurface, 'p_isoval_max',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ExtractIsosurface, 'p_isoval',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ExtractIsosurface, 'p_isoval_typed',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ExtractIsosurface, 'p_isoval_quantity',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ExtractIsosurface, 'p_quantity_range',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ExtractIsosurface, 'p_quantity_clusive',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ExtractIsosurface, 'p_quantity_min',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ExtractIsosurface, 'p_quantity_max',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ExtractIsosurface, 'p_quantity_list',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ExtractIsosurface, 'p_isoval_list',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ExtractIsosurface, 'p_matrix_list',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ExtractIsosurface, 'p_algorithm',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ExtractIsosurface, 'p_build_trisurf',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ExtractIsosurface, 'p_build_geom',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ExtractIsosurface, 'p_np',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ExtractIsosurface, 'p_active_isoval_selection_tab',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ExtractIsosurface, 'p_active_tab',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ExtractIsosurface, 'p_update_type',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ExtractIsosurface, 'p_color_r',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ExtractIsosurface, 'p_color_g',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ExtractIsosurface, 'p_color_b',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ExtractIsosurface, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_ExtractIsosurface, 'Optional Color Map',
                   (SCIRun_ColorMap, "SCIRun_ColorMap"))
  reg.add_input_port(scirun_ExtractIsosurface, 'Optional Isovalues',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_ExtractIsosurface, 'Surface', 
                    (SCIRun_Field, 'Surface'))
  reg.add_output_port(scirun_ExtractIsosurface, 'Geometry', 
                    (SCIRun_Geometry, 'Geometry'))
  reg.add_output_port(scirun_ExtractIsosurface, 'Mapping', 
                    (SCIRun_Matrix, 'Mapping'))

  reg.add_module(scirun_ConvertMatrixToString)
  reg.add_input_port(scirun_ConvertMatrixToString, 'Matrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_ConvertMatrixToString, 'String', 
                    (core.modules.basic_modules.String, 'String'))

  reg.add_module(scirun_ReportMatrixColumnMeasure)
  reg.add_input_port(scirun_ReportMatrixColumnMeasure, 'p_method',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReportMatrixColumnMeasure, 'Matrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_ReportMatrixColumnMeasure, 'Vector', 
                    (SCIRun_Matrix, 'Vector'))

  reg.add_module(scirun_ReplicateDataArray)
  reg.add_input_port(scirun_ReplicateDataArray, 'p_size',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ReplicateDataArray, 'DataArray',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(scirun_ReplicateDataArray, 'Size',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_ReplicateDataArray, 'DataArray', 
                    (SCIRun_Matrix, 'DataArray'))

  reg.add_module(scirun_SortMatrix)
  reg.add_input_port(scirun_SortMatrix, 'p_row_or_col',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_SortMatrix, 'Matrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_SortMatrix, 'Matrix', 
                    (SCIRun_Matrix, 'Matrix'))

  reg.add_module(scirun_ConvertMeshToUnstructuredMesh)
  reg.add_input_port(scirun_ConvertMeshToUnstructuredMesh, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_ConvertMeshToUnstructuredMesh, 'Output Field', 
                    (SCIRun_Field, 'Output Field'))

  reg.add_module(scirun_CreateViewerAxes)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_precision',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_squash',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_valuerez',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_labelrez',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_01_0_Axis_absolute',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_01_0_Axis_divisions',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_01_0_Axis_offset',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_01_0_Axis_range_first',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_01_0_Axis_range_second',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_01_0_Axis_min_absolute',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_01_0_Axis_max_absolute',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_01_0_Axis_minplane',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_01_0_Axis_maxplane',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_01_0_Axis_lines',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_01_0_Axis_minticks',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_01_0_Axis_maxticks',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_01_0_Axis_minlabel',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_01_0_Axis_maxlabel',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_01_0_Axis_minvalue',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_01_0_Axis_maxvalue',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_01_0_Axis_width',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_01_0_Axis_tickangle',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_01_0_Axis_ticktilt',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_01_0_Axis_ticksize',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_01_0_Axis_labelangle',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_01_0_Axis_labelheight',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_01_0_Axis_valuesize',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_01_0_Axis_valuesquash',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_01_1_Axis_absolute',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_01_1_Axis_divisions',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_01_1_Axis_offset',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_01_1_Axis_range_first',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_01_1_Axis_range_second',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_01_1_Axis_min_absolute',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_01_1_Axis_max_absolute',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_01_1_Axis_minplane',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_01_1_Axis_maxplane',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_01_1_Axis_lines',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_01_1_Axis_minticks',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_01_1_Axis_maxticks',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_01_1_Axis_minlabel',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_01_1_Axis_maxlabel',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_01_1_Axis_minvalue',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_01_1_Axis_maxvalue',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_01_1_Axis_width',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_01_1_Axis_tickangle',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_01_1_Axis_ticktilt',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_01_1_Axis_ticksize',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_01_1_Axis_labelangle',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_01_1_Axis_labelheight',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_01_1_Axis_valuesize',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_01_1_Axis_valuesquash',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_02_0_Axis_absolute',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_02_0_Axis_divisions',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_02_0_Axis_offset',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_02_0_Axis_range_first',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_02_0_Axis_range_second',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_02_0_Axis_min_absolute',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_02_0_Axis_max_absolute',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_02_0_Axis_minplane',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_02_0_Axis_maxplane',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_02_0_Axis_lines',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_02_0_Axis_minticks',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_02_0_Axis_maxticks',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_02_0_Axis_minlabel',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_02_0_Axis_maxlabel',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_02_0_Axis_minvalue',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_02_0_Axis_maxvalue',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_02_0_Axis_width',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_02_0_Axis_tickangle',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_02_0_Axis_ticktilt',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_02_0_Axis_ticksize',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_02_0_Axis_labelangle',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_02_0_Axis_labelheight',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_02_0_Axis_valuesize',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_02_0_Axis_valuesquash',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_02_2_Axis_absolute',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_02_2_Axis_divisions',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_02_2_Axis_offset',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_02_2_Axis_range_first',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_02_2_Axis_range_second',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_02_2_Axis_min_absolute',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_02_2_Axis_max_absolute',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_02_2_Axis_minplane',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_02_2_Axis_maxplane',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_02_2_Axis_lines',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_02_2_Axis_minticks',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_02_2_Axis_maxticks',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_02_2_Axis_minlabel',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_02_2_Axis_maxlabel',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_02_2_Axis_minvalue',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_02_2_Axis_maxvalue',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_02_2_Axis_width',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_02_2_Axis_tickangle',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_02_2_Axis_ticktilt',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_02_2_Axis_ticksize',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_02_2_Axis_labelangle',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_02_2_Axis_labelheight',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_02_2_Axis_valuesize',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_02_2_Axis_valuesquash',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_12_1_Axis_absolute',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_12_1_Axis_divisions',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_12_1_Axis_offset',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_12_1_Axis_range_first',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_12_1_Axis_range_second',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_12_1_Axis_min_absolute',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_12_1_Axis_max_absolute',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_12_1_Axis_minplane',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_12_1_Axis_maxplane',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_12_1_Axis_lines',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_12_1_Axis_minticks',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_12_1_Axis_maxticks',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_12_1_Axis_minlabel',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_12_1_Axis_maxlabel',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_12_1_Axis_minvalue',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_12_1_Axis_maxvalue',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_12_1_Axis_width',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_12_1_Axis_tickangle',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_12_1_Axis_ticktilt',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_12_1_Axis_ticksize',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_12_1_Axis_labelangle',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_12_1_Axis_labelheight',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_12_1_Axis_valuesize',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_12_1_Axis_valuesquash',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_12_2_Axis_absolute',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_12_2_Axis_divisions',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_12_2_Axis_offset',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_12_2_Axis_range_first',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_12_2_Axis_range_second',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_12_2_Axis_min_absolute',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_12_2_Axis_max_absolute',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_12_2_Axis_minplane',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_12_2_Axis_maxplane',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_12_2_Axis_lines',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_12_2_Axis_minticks',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_12_2_Axis_maxticks',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_12_2_Axis_minlabel',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_12_2_Axis_maxlabel',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_12_2_Axis_minvalue',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_12_2_Axis_maxvalue',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_12_2_Axis_width',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_12_2_Axis_tickangle',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_12_2_Axis_ticktilt',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_12_2_Axis_ticksize',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_12_2_Axis_labelangle',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_12_2_Axis_labelheight',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_12_2_Axis_valuesize',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'p_Plane_12_2_Axis_valuesquash',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerAxes, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_CreateViewerAxes, 'Axes', 
                    (SCIRun_Geometry, 'Axes'))

  reg.add_module(scirun_SelectFieldROIWithBoxWidget)
  reg.add_input_port(scirun_SelectFieldROIWithBoxWidget, 'p_stampvalue',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_SelectFieldROIWithBoxWidget, 'p_runmode',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_SelectFieldROIWithBoxWidget, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_SelectFieldROIWithBoxWidget, 'Selection Widget', 
                    (SCIRun_Geometry, 'Selection Widget'))
  reg.add_output_port(scirun_SelectFieldROIWithBoxWidget, 'Output Field', 
                    (SCIRun_Field, 'Output Field'))

  reg.add_module(scirun_SetTetVolFieldDataValues)
  reg.add_input_port(scirun_SetTetVolFieldDataValues, 'p_newval',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_SetTetVolFieldDataValues, 'InField',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_SetTetVolFieldDataValues, 'OutField', 
                    (SCIRun_Field, 'OutField'))

  reg.add_module(scirun_WritePath)
  reg.add_input_port(scirun_WritePath, 'p_filetype',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_WritePath, 'p_confirm',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_WritePath, 'p_confirm_once',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_WritePath, 'Input Data',
                   (SCIRun_Path, "SCIRun_Path"))
  reg.add_input_port(scirun_WritePath, 'Filename',
                   (core.modules.basic_modules.String, 'tip'))

  reg.add_module(scirun_ClipLatVolByIndicesOrWidget)
  reg.add_input_port(scirun_ClipLatVolByIndicesOrWidget, 'p_use_text_bbox',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ClipLatVolByIndicesOrWidget, 'p_text_min_x',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ClipLatVolByIndicesOrWidget, 'p_text_min_y',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ClipLatVolByIndicesOrWidget, 'p_text_min_z',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ClipLatVolByIndicesOrWidget, 'p_text_max_x',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ClipLatVolByIndicesOrWidget, 'p_text_max_y',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ClipLatVolByIndicesOrWidget, 'p_text_max_z',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ClipLatVolByIndicesOrWidget, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_ClipLatVolByIndicesOrWidget, 'Selection Widget', 
                    (SCIRun_Geometry, 'Selection Widget'))
  reg.add_output_port(scirun_ClipLatVolByIndicesOrWidget, 'Output Field', 
                    (SCIRun_Field, 'Output Field'))
  reg.add_output_port(scirun_ClipLatVolByIndicesOrWidget, 'MaskVector', 
                    (SCIRun_Nrrd, 'MaskVector'))

  reg.add_module(scirun_GetBundlesFromBundle)
  reg.add_input_port(scirun_GetBundlesFromBundle, 'p_bundle1_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetBundlesFromBundle, 'p_bundle2_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetBundlesFromBundle, 'p_bundle3_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetBundlesFromBundle, 'p_bundle4_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetBundlesFromBundle, 'p_bundle5_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetBundlesFromBundle, 'p_bundle6_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetBundlesFromBundle, 'p_bundle_selection',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetBundlesFromBundle, 'bundle',
                   (SCIRun_Bundle, "SCIRun_Bundle"))
  reg.add_output_port(scirun_GetBundlesFromBundle, 'bundle', 
                    (SCIRun_Bundle, 'bundle'))
  reg.add_output_port(scirun_GetBundlesFromBundle, 'bundle1', 
                    (SCIRun_Bundle, 'bundle1'))
  reg.add_output_port(scirun_GetBundlesFromBundle, 'bundle2', 
                    (SCIRun_Bundle, 'bundle2'))
  reg.add_output_port(scirun_GetBundlesFromBundle, 'bundle3', 
                    (SCIRun_Bundle, 'bundle3'))
  reg.add_output_port(scirun_GetBundlesFromBundle, 'bundle4', 
                    (SCIRun_Bundle, 'bundle4'))
  reg.add_output_port(scirun_GetBundlesFromBundle, 'bundle5', 
                    (SCIRun_Bundle, 'bundle5'))
  reg.add_output_port(scirun_GetBundlesFromBundle, 'bundle6', 
                    (SCIRun_Bundle, 'bundle6'))

  reg.add_module(scirun_RescaleColorMap)
  reg.add_input_port(scirun_RescaleColorMap, 'p_main_frame',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_RescaleColorMap, 'p_isFixed',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_RescaleColorMap, 'p_min',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_RescaleColorMap, 'p_max',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_RescaleColorMap, 'p_makeSymmetric',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_RescaleColorMap, 'ColorMap',
                   (SCIRun_ColorMap, "SCIRun_ColorMap"))
  reg.add_input_port(scirun_RescaleColorMap, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_RescaleColorMap, 'ColorMap', 
                    (SCIRun_ColorMap, 'ColorMap'))

  reg.add_module(scirun_ConvertNrrdsToTexture)
  reg.add_input_port(scirun_ConvertNrrdsToTexture, 'p_vmin',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ConvertNrrdsToTexture, 'p_vmax',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ConvertNrrdsToTexture, 'p_gmin',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ConvertNrrdsToTexture, 'p_gmax',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ConvertNrrdsToTexture, 'p_mmin',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ConvertNrrdsToTexture, 'p_mmax',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ConvertNrrdsToTexture, 'p_is_fixed',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ConvertNrrdsToTexture, 'p_card_mem',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ConvertNrrdsToTexture, 'p_card_mem_auto',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ConvertNrrdsToTexture, 'p_is_uchar',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ConvertNrrdsToTexture, 'p_histogram',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ConvertNrrdsToTexture, 'p_gamma',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ConvertNrrdsToTexture, 'Value Nrrd',
                   (SCIRun_Nrrd, "SCIRun_Nrrd"))
  reg.add_input_port(scirun_ConvertNrrdsToTexture, 'Gradient Magnitude Nrrd',
                   (SCIRun_Nrrd, "SCIRun_Nrrd"))
  reg.add_output_port(scirun_ConvertNrrdsToTexture, 'Texture', 
                    (SCIRun_Texture, 'Texture'))
  reg.add_output_port(scirun_ConvertNrrdsToTexture, 'JointHistoGram', 
                    (SCIRun_Nrrd, 'JointHistoGram'))

  reg.add_module(scirun_ConvertQuadSurfToTriSurf)
  reg.add_input_port(scirun_ConvertQuadSurfToTriSurf, 'QuadSurf',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_ConvertQuadSurfToTriSurf, 'TriSurf', 
                    (SCIRun_Field, 'TriSurf'))

  reg.add_module(scirun_WriteColorMap2D)
  reg.add_input_port(scirun_WriteColorMap2D, 'p_filetype',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_WriteColorMap2D, 'p_confirm',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_WriteColorMap2D, 'p_confirm_once',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_WriteColorMap2D, 'p_exporttype',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_WriteColorMap2D, 'Input Data',
                   (SCIRun_ColorMap2, "SCIRun_ColorMap2"))
  reg.add_input_port(scirun_WriteColorMap2D, 'Filename',
                   (core.modules.basic_modules.String, 'tip'))

  reg.add_module(scirun_BuildMatrixOfSurfaceNormals)
  reg.add_input_port(scirun_BuildMatrixOfSurfaceNormals, 'Surface Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_BuildMatrixOfSurfaceNormals, 'Nodal Surface Normals', 
                    (SCIRun_Matrix, 'Nodal Surface Normals'))

  reg.add_module(scirun_ReadHDF5File)
  reg.add_input_port(scirun_ReadHDF5File, 'p_have_HDF5',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_power_app',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_datasets',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_dumpname',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_ports',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_ndims',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_mergeData',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_assumeSVT',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_animate',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_animate_tab',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_basic_tab',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_extended_tab',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_playmode_tab',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_selectable_min',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_selectable_max',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_selectable_inc',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_range_min',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_range_max',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_playmode',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_current',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_execmode',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_delay',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_inc_amount',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_update_type',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_have_group',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_have_attributes',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_have_datasets',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_continuous',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_selectionString',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_regexp',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_allow_selection',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_read_error',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_max_dims',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_0_dim',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_0_start',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_0_start2',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_0_count',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_0_count2',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_0_stride',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_0_stride2',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_1_dim',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_1_start',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_1_start2',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_1_count',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_1_count2',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_1_stride',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_1_stride2',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_2_dim',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_2_start',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_2_start2',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_2_count',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_2_count2',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_2_stride',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_2_stride2',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_3_dim',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_3_start',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_3_start2',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_3_count',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_3_count2',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_3_stride',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_3_stride2',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_4_dim',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_4_start',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_4_start2',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_4_count',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_4_count2',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_4_stride',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_4_stride2',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_5_dim',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_5_start',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_5_start2',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_5_count',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_5_count2',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_5_stride',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'p_5_stride2',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadHDF5File, 'Full filename',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_input_port(scirun_ReadHDF5File, 'Current Index',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_ReadHDF5File, 'Output 0 Nrrd', 
                    (SCIRun_Nrrd, 'Output 0 Nrrd'))
  reg.add_output_port(scirun_ReadHDF5File, 'Output 1 Nrrd', 
                    (SCIRun_Nrrd, 'Output 1 Nrrd'))
  reg.add_output_port(scirun_ReadHDF5File, 'Output 2 Nrrd', 
                    (SCIRun_Nrrd, 'Output 2 Nrrd'))
  reg.add_output_port(scirun_ReadHDF5File, 'Output 3 Nrrd', 
                    (SCIRun_Nrrd, 'Output 3 Nrrd'))
  reg.add_output_port(scirun_ReadHDF5File, 'Output 4 Nrrd', 
                    (SCIRun_Nrrd, 'Output 4 Nrrd'))
  reg.add_output_port(scirun_ReadHDF5File, 'Output 5 Nrrd', 
                    (SCIRun_Nrrd, 'Output 5 Nrrd'))
  reg.add_output_port(scirun_ReadHDF5File, 'Output 6 Nrrd', 
                    (SCIRun_Nrrd, 'Output 6 Nrrd'))
  reg.add_output_port(scirun_ReadHDF5File, 'Output 7 Nrrd', 
                    (SCIRun_Nrrd, 'Output 7 Nrrd'))
  reg.add_output_port(scirun_ReadHDF5File, 'Selected Index', 
                    (SCIRun_Matrix, 'Selected Index'))

  reg.add_module(scirun_SwapFieldDataWithMatrixEntries)
  reg.add_input_port(scirun_SwapFieldDataWithMatrixEntries, 'p_preserve_scalar_type',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_SwapFieldDataWithMatrixEntries, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_SwapFieldDataWithMatrixEntries, 'Input Matrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_SwapFieldDataWithMatrixEntries, 'Output Field', 
                    (SCIRun_Field, 'Output Field'))
  reg.add_output_port(scirun_SwapFieldDataWithMatrixEntries, 'Output Matrix', 
                    (SCIRun_Matrix, 'Output Matrix'))

  reg.add_module(scirun_GetFieldBoundary)
  reg.add_input_port(scirun_GetFieldBoundary, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_GetFieldBoundary, 'BoundaryField', 
                    (SCIRun_Field, 'BoundaryField'))
  reg.add_output_port(scirun_GetFieldBoundary, 'Mapping', 
                    (SCIRun_Matrix, 'Mapping'))

  reg.add_module(scirun_ConvertMatricesToMesh)
  reg.add_input_port(scirun_ConvertMatricesToMesh, 'p_fieldname',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ConvertMatricesToMesh, 'p_meshname',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ConvertMatricesToMesh, 'p_fieldbasetype',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ConvertMatricesToMesh, 'p_datatype',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ConvertMatricesToMesh, 'Mesh Elements',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(scirun_ConvertMatricesToMesh, 'Mesh Positions',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(scirun_ConvertMatricesToMesh, 'Mesh Normals',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_ConvertMatricesToMesh, 'Output Field', 
                    (SCIRun_Field, 'Output Field'))

  reg.add_module(scirun_TransformMeshWithFunction)
  reg.add_input_port(scirun_TransformMeshWithFunction, 'p_function',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_TransformMeshWithFunction, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_TransformMeshWithFunction, 'Output Field', 
                    (SCIRun_Field, 'Output Field'))

  reg.add_module(scirun_PrintHelloWorldToScreen)

  reg.add_module(scirun_ReportFieldInfo)
  reg.add_input_port(scirun_ReportFieldInfo, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_ReportFieldInfo, 'NumNodes', 
                    (SCIRun_Matrix, 'NumNodes'))
  reg.add_output_port(scirun_ReportFieldInfo, 'NumElements', 
                    (SCIRun_Matrix, 'NumElements'))
  reg.add_output_port(scirun_ReportFieldInfo, 'NumData', 
                    (SCIRun_Matrix, 'NumData'))
  reg.add_output_port(scirun_ReportFieldInfo, 'DataMin', 
                    (SCIRun_Matrix, 'DataMin'))
  reg.add_output_port(scirun_ReportFieldInfo, 'DataMax', 
                    (SCIRun_Matrix, 'DataMax'))
  reg.add_output_port(scirun_ReportFieldInfo, 'FieldSize', 
                    (SCIRun_Matrix, 'FieldSize'))
  reg.add_output_port(scirun_ReportFieldInfo, 'FieldCenter', 
                    (SCIRun_Matrix, 'FieldCenter'))
  reg.add_output_port(scirun_ReportFieldInfo, 'Dimensions', 
                    (SCIRun_Matrix, 'Dimensions'))

  reg.add_module(scirun_ConvertLatVolDataFromElemToNode)
  reg.add_input_port(scirun_ConvertLatVolDataFromElemToNode, 'Elem Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_ConvertLatVolDataFromElemToNode, 'Node Field', 
                    (SCIRun_Field, 'Node Field'))

  reg.add_module(scirun_GetPathsFromBundle)
  reg.add_input_port(scirun_GetPathsFromBundle, 'p_path1_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetPathsFromBundle, 'p_path2_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetPathsFromBundle, 'p_path3_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetPathsFromBundle, 'p_path4_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetPathsFromBundle, 'p_path5_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetPathsFromBundle, 'p_path6_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetPathsFromBundle, 'p_path_selection',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetPathsFromBundle, 'bundle',
                   (SCIRun_Bundle, "SCIRun_Bundle"))
  reg.add_output_port(scirun_GetPathsFromBundle, 'bundle', 
                    (SCIRun_Bundle, 'bundle'))
  reg.add_output_port(scirun_GetPathsFromBundle, 'path1', 
                    (SCIRun_Path, 'path1'))
  reg.add_output_port(scirun_GetPathsFromBundle, 'path2', 
                    (SCIRun_Path, 'path2'))
  reg.add_output_port(scirun_GetPathsFromBundle, 'path3', 
                    (SCIRun_Path, 'path3'))
  reg.add_output_port(scirun_GetPathsFromBundle, 'path4', 
                    (SCIRun_Path, 'path4'))
  reg.add_output_port(scirun_GetPathsFromBundle, 'path5', 
                    (SCIRun_Path, 'path5'))
  reg.add_output_port(scirun_GetPathsFromBundle, 'path6', 
                    (SCIRun_Path, 'path6'))

  reg.add_module(scirun_CreateGeometricTransform)
  reg.add_input_port(scirun_CreateGeometricTransform, 'p_rotate_x',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_CreateGeometricTransform, 'p_rotate_y',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_CreateGeometricTransform, 'p_rotate_z',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_CreateGeometricTransform, 'p_rotate_theta',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_CreateGeometricTransform, 'p_translate_x',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_CreateGeometricTransform, 'p_translate_y',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_CreateGeometricTransform, 'p_translate_z',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_CreateGeometricTransform, 'p_scale_uniform',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_CreateGeometricTransform, 'p_scale_x',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_CreateGeometricTransform, 'p_scale_y',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_CreateGeometricTransform, 'p_scale_z',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_CreateGeometricTransform, 'p_shear_plane_a',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_CreateGeometricTransform, 'p_shear_plane_b',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_CreateGeometricTransform, 'p_shear_plane_c',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_CreateGeometricTransform, 'p_widget_resizable',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_CreateGeometricTransform, 'p_permute_x',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_CreateGeometricTransform, 'p_permute_y',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_CreateGeometricTransform, 'p_permute_z',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_CreateGeometricTransform, 'p_pre_transform',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_CreateGeometricTransform, 'p_which_transform',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateGeometricTransform, 'p_widget_scale',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_CreateGeometricTransform, 'p_ignoring_widget_changes',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_CreateGeometricTransform, 'Matrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_CreateGeometricTransform, 'Matrix', 
                    (SCIRun_Matrix, 'Matrix'))
  reg.add_output_port(scirun_CreateGeometricTransform, 'Geometry', 
                    (SCIRun_Geometry, 'Geometry'))

  reg.add_module(scirun_CalculateNodeNormals)
  reg.add_input_port(scirun_CalculateNodeNormals, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_CalculateNodeNormals, 'Input Point',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_CalculateNodeNormals, 'Output Field', 
                    (SCIRun_Field, 'Output Field'))

  reg.add_module(scirun_ReportFieldGeometryMeasures)
  reg.add_input_port(scirun_ReportFieldGeometryMeasures, 'p_simplexString',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReportFieldGeometryMeasures, 'p_xFlag',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ReportFieldGeometryMeasures, 'p_yFlag',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ReportFieldGeometryMeasures, 'p_zFlag',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ReportFieldGeometryMeasures, 'p_idxFlag',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ReportFieldGeometryMeasures, 'p_sizeFlag',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ReportFieldGeometryMeasures, 'p_normalsFlag',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ReportFieldGeometryMeasures, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_ReportFieldGeometryMeasures, 'Output Measures Matrix', 
                    (SCIRun_Matrix, 'Output Measures Matrix'))

  reg.add_module(scirun_CalculateVectorMagnitudes)
  reg.add_input_port(scirun_CalculateVectorMagnitudes, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_CalculateVectorMagnitudes, 'Output CalculateVectorMagnitudes', 
                    (SCIRun_Field, 'Output CalculateVectorMagnitudes'))

  reg.add_module(scirun_GetInputField)
  reg.add_input_port(scirun_GetInputField, 'InField',
                   (SCIRun_Field, "SCIRun_Field"))

  reg.add_module(scirun_ChooseMatrix)
  reg.add_input_port(scirun_ChooseMatrix, 'p_use_first_valid',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ChooseMatrix, 'p_port_valid_index',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ChooseMatrix, 'p_port_selected_index',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ChooseMatrix, 'Matrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_ChooseMatrix, 'Matrix', 
                    (SCIRun_Matrix, 'Matrix'))

  reg.add_module(scirun_ClipFieldToFieldOrWidget)
  reg.add_input_port(scirun_ClipFieldToFieldOrWidget, 'p_clip_location',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ClipFieldToFieldOrWidget, 'p_clipmode',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ClipFieldToFieldOrWidget, 'p_autoexecute',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ClipFieldToFieldOrWidget, 'p_autoinvert',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ClipFieldToFieldOrWidget, 'p_execmode',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ClipFieldToFieldOrWidget, 'p_center_x',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ClipFieldToFieldOrWidget, 'p_center_y',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ClipFieldToFieldOrWidget, 'p_center_z',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ClipFieldToFieldOrWidget, 'p_right_x',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ClipFieldToFieldOrWidget, 'p_right_y',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ClipFieldToFieldOrWidget, 'p_right_z',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ClipFieldToFieldOrWidget, 'p_down_x',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ClipFieldToFieldOrWidget, 'p_down_y',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ClipFieldToFieldOrWidget, 'p_down_z',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ClipFieldToFieldOrWidget, 'p_in_x',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ClipFieldToFieldOrWidget, 'p_in_y',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ClipFieldToFieldOrWidget, 'p_in_z',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ClipFieldToFieldOrWidget, 'p_scale',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ClipFieldToFieldOrWidget, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_ClipFieldToFieldOrWidget, 'Clip Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_ClipFieldToFieldOrWidget, 'Selection Widget', 
                    (SCIRun_Geometry, 'Selection Widget'))
  reg.add_output_port(scirun_ClipFieldToFieldOrWidget, 'Output Field', 
                    (SCIRun_Field, 'Output Field'))

  reg.add_module(scirun_ConvertHexVolToTetVol)
  reg.add_input_port(scirun_ConvertHexVolToTetVol, 'HexVol',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_ConvertHexVolToTetVol, 'TetVol', 
                    (SCIRun_Field, 'TetVol'))

  reg.add_module(scirun_SetFieldOrMeshStringProperty)
  reg.add_input_port(scirun_SetFieldOrMeshStringProperty, 'p_prop',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_SetFieldOrMeshStringProperty, 'p_val',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_SetFieldOrMeshStringProperty, 'p_meshprop',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_SetFieldOrMeshStringProperty, 'Input',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_SetFieldOrMeshStringProperty, 'Output', 
                    (SCIRun_Field, 'Output'))

  reg.add_module(scirun_ConvertMeshCoordinateSystem)
  reg.add_input_port(scirun_ConvertMeshCoordinateSystem, 'p_oldsystem',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ConvertMeshCoordinateSystem, 'p_newsystem',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ConvertMeshCoordinateSystem, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_ConvertMeshCoordinateSystem, 'Output Field', 
                    (SCIRun_Field, 'Output Field'))

  reg.add_module(scirun_RefineMeshByIsovalue2)
  reg.add_input_port(scirun_RefineMeshByIsovalue2, 'p_isoval',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_RefineMeshByIsovalue2, 'p_lte',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_RefineMeshByIsovalue2, 'Input',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_RefineMeshByIsovalue2, 'Optional Isovalue',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_RefineMeshByIsovalue2, 'Refined', 
                    (SCIRun_Field, 'Refined'))
  reg.add_output_port(scirun_RefineMeshByIsovalue2, 'Mapping', 
                    (SCIRun_Matrix, 'Mapping'))

  reg.add_module(scirun_SetTetVolFieldDataValuesToZero)
  reg.add_input_port(scirun_SetTetVolFieldDataValuesToZero, 'InField',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_SetTetVolFieldDataValuesToZero, 'OutField', 
                    (SCIRun_Field, 'OutField'))

  reg.add_module(scirun_ViewSlices)
  reg.add_input_port(scirun_ViewSlices, 'p_clut_ww',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ViewSlices, 'p_clut_wl',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ViewSlices, 'p_probe',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ViewSlices, 'p_show_colormap2',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ViewSlices, 'p_painting',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ViewSlices, 'p_crop',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ViewSlices, 'p_crop_minAxis0',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ViewSlices, 'p_crop_minAxis1',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ViewSlices, 'p_crop_minAxis2',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ViewSlices, 'p_crop_maxAxis0',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ViewSlices, 'p_crop_maxAxis1',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ViewSlices, 'p_crop_maxAxis2',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ViewSlices, 'p_crop_minPadAxis0',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ViewSlices, 'p_crop_minPadAxis1',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ViewSlices, 'p_crop_minPadAxis2',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ViewSlices, 'p_crop_maxPadAxis0',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ViewSlices, 'p_crop_maxPadAxis1',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ViewSlices, 'p_crop_maxPadAxis2',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ViewSlices, 'p_texture_filter',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ViewSlices, 'p_anatomical_coordinates',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ViewSlices, 'p_show_text',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ViewSlices, 'p_color_font_r',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ViewSlices, 'p_color_font_g',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ViewSlices, 'p_color_font_b',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ViewSlices, 'p_color_font_a',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ViewSlices, 'p_min',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ViewSlices, 'p_max',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ViewSlices, 'p_dim0',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ViewSlices, 'p_dim1',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ViewSlices, 'p_dim2',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ViewSlices, 'p_geom_flushed',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ViewSlices, 'p_background_threshold',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ViewSlices, 'p_gradient_threshold',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ViewSlices, 'p_font_size',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ViewSlices, 'Nrrd1',
                   (SCIRun_Nrrd, "SCIRun_Nrrd"))
  reg.add_input_port(scirun_ViewSlices, 'Nrrd2',
                   (SCIRun_Nrrd, "SCIRun_Nrrd"))
  reg.add_input_port(scirun_ViewSlices, 'Nrrd1ColorMap',
                   (SCIRun_ColorMap, "SCIRun_ColorMap"))
  reg.add_input_port(scirun_ViewSlices, 'Nrrd2ColorMap',
                   (SCIRun_ColorMap, "SCIRun_ColorMap"))
  reg.add_input_port(scirun_ViewSlices, 'InputColorMap2',
                   (SCIRun_ColorMap2, "SCIRun_ColorMap2"))
  reg.add_input_port(scirun_ViewSlices, 'NrrdGradient',
                   (SCIRun_Nrrd, "SCIRun_Nrrd"))
  reg.add_output_port(scirun_ViewSlices, 'Geometry', 
                    (SCIRun_Geometry, 'Geometry'))
  reg.add_output_port(scirun_ViewSlices, 'ColorMap2', 
                    (SCIRun_ColorMap2, 'ColorMap2'))

  reg.add_module(scirun_SplitVectorArrayInXYZ)
  reg.add_input_port(scirun_SplitVectorArrayInXYZ, 'VectorArray',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_SplitVectorArrayInXYZ, 'X', 
                    (SCIRun_Matrix, 'X'))
  reg.add_output_port(scirun_SplitVectorArrayInXYZ, 'Y', 
                    (SCIRun_Matrix, 'Y'))
  reg.add_output_port(scirun_SplitVectorArrayInXYZ, 'Z', 
                    (SCIRun_Matrix, 'Z'))

  reg.add_module(scirun_ConvertIndicesToFieldData)
  reg.add_input_port(scirun_ConvertIndicesToFieldData, 'p_outputtype',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ConvertIndicesToFieldData, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_ConvertIndicesToFieldData, 'Data',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_ConvertIndicesToFieldData, 'Field', 
                    (SCIRun_Field, 'Field'))

  reg.add_module(scirun_CalculateDistanceToFieldBoundary)
  reg.add_input_port(scirun_CalculateDistanceToFieldBoundary, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_CalculateDistanceToFieldBoundary, 'DistanceField', 
                    (SCIRun_Field, 'DistanceField'))

  reg.add_module(scirun_ConvertMappingMatrixToMaskVector)
  reg.add_input_port(scirun_ConvertMappingMatrixToMaskVector, 'MappingMatrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_ConvertMappingMatrixToMaskVector, 'MaskVector', 
                    (SCIRun_Nrrd, 'MaskVector'))

  reg.add_module(scirun_MapFieldDataFromSourceToDestination)
  reg.add_input_port(scirun_MapFieldDataFromSourceToDestination, 'p_interpolation_basis',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_MapFieldDataFromSourceToDestination, 'p_map_source_to_single_dest',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_MapFieldDataFromSourceToDestination, 'p_exhaustive_search',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_MapFieldDataFromSourceToDestination, 'p_exhaustive_search_max_dist',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_MapFieldDataFromSourceToDestination, 'p_np',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_MapFieldDataFromSourceToDestination, 'Source',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_MapFieldDataFromSourceToDestination, 'Destination',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_MapFieldDataFromSourceToDestination, 'Remapped Destination', 
                    (SCIRun_Field, 'Remapped Destination'))

  reg.add_module(scirun_CreateLatVol)
  reg.add_input_port(scirun_CreateLatVol, 'p_sizex',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_CreateLatVol, 'p_sizey',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_CreateLatVol, 'p_sizez',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_CreateLatVol, 'p_padpercent',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_CreateLatVol, 'p_data_at',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateLatVol, 'p_element_size',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateLatVol, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_CreateLatVol, 'LatVol Size',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_CreateLatVol, 'Output Sample Field', 
                    (SCIRun_Field, 'Output Sample Field'))

  reg.add_module(scirun_ResizeMatrix)
  reg.add_input_port(scirun_ResizeMatrix, 'p_dim_m',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ResizeMatrix, 'p_dim_n',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ResizeMatrix, 'Matrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(scirun_ResizeMatrix, 'M',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(scirun_ResizeMatrix, 'N',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_ResizeMatrix, 'Matrix', 
                    (SCIRun_Matrix, 'Matrix'))

  reg.add_module(scirun_ShowAndEditCameraWidget)
  reg.add_input_port(scirun_ShowAndEditCameraWidget, 'p_frame',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowAndEditCameraWidget, 'p_num_frames',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowAndEditCameraWidget, 'p_time',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ShowAndEditCameraWidget, 'p_playmode',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ShowAndEditCameraWidget, 'p_execmode',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ShowAndEditCameraWidget, 'p_track',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowAndEditCameraWidget, 'p_B',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ShowAndEditCameraWidget, 'p_C',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_output_port(scirun_ShowAndEditCameraWidget, 'Geometry', 
                    (SCIRun_Geometry, 'Geometry'))

  reg.add_module(scirun_InterfaceWithCamal)
  reg.add_input_port(scirun_InterfaceWithCamal, 'TriSurf',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_InterfaceWithCamal, 'TetVol', 
                    (SCIRun_Field, 'TetVol'))

  reg.add_module(scirun_SelectAndSetFieldData3)
  reg.add_input_port(scirun_SelectAndSetFieldData3, 'p_selection1',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_SelectAndSetFieldData3, 'p_function1',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_SelectAndSetFieldData3, 'p_selection2',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_SelectAndSetFieldData3, 'p_function2',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_SelectAndSetFieldData3, 'p_selection3',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_SelectAndSetFieldData3, 'p_function3',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_SelectAndSetFieldData3, 'p_selection4',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_SelectAndSetFieldData3, 'p_function4',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_SelectAndSetFieldData3, 'p_functiondef',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_SelectAndSetFieldData3, 'p_format',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_SelectAndSetFieldData3, 'Field1',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_SelectAndSetFieldData3, 'Field2',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_SelectAndSetFieldData3, 'Field3',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_SelectAndSetFieldData3, 'Array',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_SelectAndSetFieldData3, 'Field', 
                    (SCIRun_Field, 'Field'))

  reg.add_module(scirun_ConvertMeshToPointCloud)
  reg.add_input_port(scirun_ConvertMeshToPointCloud, 'p_datalocation',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ConvertMeshToPointCloud, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_ConvertMeshToPointCloud, 'Field', 
                    (SCIRun_Field, 'Field'))

  reg.add_module(scirun_CreateFieldData)
  reg.add_input_port(scirun_CreateFieldData, 'p_function',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateFieldData, 'p_format',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateFieldData, 'p_basis',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateFieldData, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_CreateFieldData, 'Function',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_input_port(scirun_CreateFieldData, 'DataArray',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_CreateFieldData, 'Field', 
                    (SCIRun_Field, 'Field'))

  reg.add_module(scirun_InsertStringsIntoBundle)
  reg.add_input_port(scirun_InsertStringsIntoBundle, 'p_string1_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertStringsIntoBundle, 'p_string2_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertStringsIntoBundle, 'p_string3_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertStringsIntoBundle, 'p_string4_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertStringsIntoBundle, 'p_string5_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertStringsIntoBundle, 'p_string6_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertStringsIntoBundle, 'p_replace1',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_InsertStringsIntoBundle, 'p_replace2',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_InsertStringsIntoBundle, 'p_replace3',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_InsertStringsIntoBundle, 'p_replace4',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_InsertStringsIntoBundle, 'p_replace5',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_InsertStringsIntoBundle, 'p_replace6',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_InsertStringsIntoBundle, 'bundle',
                   (SCIRun_Bundle, "SCIRun_Bundle"))
  reg.add_input_port(scirun_InsertStringsIntoBundle, 'string1',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_input_port(scirun_InsertStringsIntoBundle, 'string2',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_input_port(scirun_InsertStringsIntoBundle, 'string3',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_input_port(scirun_InsertStringsIntoBundle, 'string4',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_input_port(scirun_InsertStringsIntoBundle, 'string5',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_input_port(scirun_InsertStringsIntoBundle, 'string6',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_output_port(scirun_InsertStringsIntoBundle, 'bundle', 
                    (SCIRun_Bundle, 'bundle'))

  reg.add_module(scirun_GetInputFieldAndSendAsOutput)
  reg.add_input_port(scirun_GetInputFieldAndSendAsOutput, 'InField',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_GetInputFieldAndSendAsOutput, 'OutField', 
                    (SCIRun_Field, 'OutField'))

  reg.add_module(scirun_GetNrrdsFromBundle)
  reg.add_input_port(scirun_GetNrrdsFromBundle, 'p_nrrd1_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetNrrdsFromBundle, 'p_nrrd2_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetNrrdsFromBundle, 'p_nrrd3_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetNrrdsFromBundle, 'p_nrrd4_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetNrrdsFromBundle, 'p_nrrd5_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetNrrdsFromBundle, 'p_nrrd6_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetNrrdsFromBundle, 'p_transposenrrd1',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GetNrrdsFromBundle, 'p_transposenrrd2',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GetNrrdsFromBundle, 'p_transposenrrd3',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GetNrrdsFromBundle, 'p_transposenrrd4',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GetNrrdsFromBundle, 'p_transposenrrd5',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GetNrrdsFromBundle, 'p_transposenrrd6',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GetNrrdsFromBundle, 'p_nrrd_selection',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetNrrdsFromBundle, 'bundle',
                   (SCIRun_Bundle, "SCIRun_Bundle"))
  reg.add_output_port(scirun_GetNrrdsFromBundle, 'bundle', 
                    (SCIRun_Bundle, 'bundle'))
  reg.add_output_port(scirun_GetNrrdsFromBundle, 'nrrd1', 
                    (SCIRun_Nrrd, 'nrrd1'))
  reg.add_output_port(scirun_GetNrrdsFromBundle, 'nrrd2', 
                    (SCIRun_Nrrd, 'nrrd2'))
  reg.add_output_port(scirun_GetNrrdsFromBundle, 'nrrd3', 
                    (SCIRun_Nrrd, 'nrrd3'))
  reg.add_output_port(scirun_GetNrrdsFromBundle, 'nrrd4', 
                    (SCIRun_Nrrd, 'nrrd4'))
  reg.add_output_port(scirun_GetNrrdsFromBundle, 'nrrd5', 
                    (SCIRun_Nrrd, 'nrrd5'))
  reg.add_output_port(scirun_GetNrrdsFromBundle, 'nrrd6', 
                    (SCIRun_Nrrd, 'nrrd6'))

  reg.add_module(scirun_ManageFieldSeries)
  reg.add_input_port(scirun_ManageFieldSeries, 'p_num_ports',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ManageFieldSeries, 'Input',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_ManageFieldSeries, 'Output 0', 
                    (SCIRun_Field, 'Output 0'))
  reg.add_output_port(scirun_ManageFieldSeries, 'Output 1', 
                    (SCIRun_Field, 'Output 1'))
  reg.add_output_port(scirun_ManageFieldSeries, 'Output 2', 
                    (SCIRun_Field, 'Output 2'))
  reg.add_output_port(scirun_ManageFieldSeries, 'Output 3', 
                    (SCIRun_Field, 'Output 3'))

  reg.add_module(scirun_ConvertMatrixToField)
  reg.add_input_port(scirun_ConvertMatrixToField, 'p_datalocation',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ConvertMatrixToField, 'Matrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_ConvertMatrixToField, 'Field', 
                    (SCIRun_Field, 'Field'))

  reg.add_module(scirun_CollectMatrices)
  reg.add_input_port(scirun_CollectMatrices, 'p_append',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_CollectMatrices, 'p_row',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_CollectMatrices, 'p_front',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_CollectMatrices, 'Optional BaseMatrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(scirun_CollectMatrices, 'SubMatrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_CollectMatrices, 'CompositeMatrix', 
                    (SCIRun_Matrix, 'CompositeMatrix'))

  reg.add_module(scirun_ChooseColorMap)
  reg.add_input_port(scirun_ChooseColorMap, 'p_use_first_valid',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ChooseColorMap, 'p_port_valid_index',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ChooseColorMap, 'p_port_selected_index',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ChooseColorMap, 'ColorMap',
                   (SCIRun_ColorMap, "SCIRun_ColorMap"))
  reg.add_output_port(scirun_ChooseColorMap, 'ColorMap', 
                    (SCIRun_ColorMap, 'ColorMap'))

  reg.add_module(scirun_ReadField)
  reg.add_input_port(scirun_ReadField, 'p_from_env',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadField, 'Filename',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_output_port(scirun_ReadField, 'Output Data', 
                    (SCIRun_Field, 'Output Data'))
  reg.add_output_port(scirun_ReadField, 'Filename', 
                    (core.modules.basic_modules.String, 'Filename'))

  reg.add_module(scirun_GetFileName)
  reg.add_input_port(scirun_GetFileName, 'p_filename_base',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetFileName, 'p_delay',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GetFileName, 'p_pinned',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_output_port(scirun_GetFileName, 'Full Filename', 
                    (core.modules.basic_modules.String, 'Full Filename'))

  reg.add_module(scirun_DecomposeTensorArrayIntoEigenVectors)
  reg.add_input_port(scirun_DecomposeTensorArrayIntoEigenVectors, 'TensorArray',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_DecomposeTensorArrayIntoEigenVectors, 'EigenVector1', 
                    (SCIRun_Matrix, 'EigenVector1'))
  reg.add_output_port(scirun_DecomposeTensorArrayIntoEigenVectors, 'EigenVector2', 
                    (SCIRun_Matrix, 'EigenVector2'))
  reg.add_output_port(scirun_DecomposeTensorArrayIntoEigenVectors, 'EigenVector3', 
                    (SCIRun_Matrix, 'EigenVector3'))
  reg.add_output_port(scirun_DecomposeTensorArrayIntoEigenVectors, 'EigenValue1', 
                    (SCIRun_Matrix, 'EigenValue1'))
  reg.add_output_port(scirun_DecomposeTensorArrayIntoEigenVectors, 'EigenValue2', 
                    (SCIRun_Matrix, 'EigenValue2'))
  reg.add_output_port(scirun_DecomposeTensorArrayIntoEigenVectors, 'EigenValue3', 
                    (SCIRun_Matrix, 'EigenValue3'))

  reg.add_module(scirun_TransformMeshWithTransform)
  reg.add_input_port(scirun_TransformMeshWithTransform, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_TransformMeshWithTransform, 'Transform Matrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_TransformMeshWithTransform, 'Transformed Field', 
                    (SCIRun_Field, 'Transformed Field'))

  reg.add_module(scirun_ClipVolumeByIsovalue)
  reg.add_input_port(scirun_ClipVolumeByIsovalue, 'p_isoval_min',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ClipVolumeByIsovalue, 'p_isoval_max',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ClipVolumeByIsovalue, 'p_isoval',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ClipVolumeByIsovalue, 'p_lte',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ClipVolumeByIsovalue, 'p_update_type',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ClipVolumeByIsovalue, 'Input',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_ClipVolumeByIsovalue, 'Optional Isovalue',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_ClipVolumeByIsovalue, 'Clipped', 
                    (SCIRun_Field, 'Clipped'))
  reg.add_output_port(scirun_ClipVolumeByIsovalue, 'Mapping', 
                    (SCIRun_Matrix, 'Mapping'))

  reg.add_module(scirun_ReportSearchGridInfo)
  reg.add_input_port(scirun_ReportSearchGridInfo, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_ReportSearchGridInfo, 'Output Sample Field', 
                    (SCIRun_Field, 'Output Sample Field'))

  reg.add_module(scirun_ChooseField)
  reg.add_input_port(scirun_ChooseField, 'p_use_first_valid',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ChooseField, 'p_port_valid_index',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ChooseField, 'p_port_selected_index',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ChooseField, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_ChooseField, 'Field', 
                    (SCIRun_Field, 'Field'))

  reg.add_module(scirun_ConvertRegularMeshToStructuredMesh)
  reg.add_input_port(scirun_ConvertRegularMeshToStructuredMesh, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_ConvertRegularMeshToStructuredMesh, 'Output Field', 
                    (SCIRun_Field, 'Output Field'))

  reg.add_module(scirun_CreateLightForViewer)
  reg.add_input_port(scirun_CreateLightForViewer, 'p_control_pos_saved',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_CreateLightForViewer, 'p_control_x',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_CreateLightForViewer, 'p_control_y',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_CreateLightForViewer, 'p_control_z',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_CreateLightForViewer, 'p_at_x',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_CreateLightForViewer, 'p_at_y',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_CreateLightForViewer, 'p_at_z',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_CreateLightForViewer, 'p_type',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_CreateLightForViewer, 'p_on',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_output_port(scirun_CreateLightForViewer, 'Geometry', 
                    (SCIRun_Geometry, 'Geometry'))

  reg.add_module(scirun_GetMatricesFromBundle)
  reg.add_input_port(scirun_GetMatricesFromBundle, 'p_matrix1_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetMatricesFromBundle, 'p_matrix2_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetMatricesFromBundle, 'p_matrix3_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetMatricesFromBundle, 'p_matrix4_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetMatricesFromBundle, 'p_matrix5_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetMatricesFromBundle, 'p_matrix6_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetMatricesFromBundle, 'p_transposenrrd1',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GetMatricesFromBundle, 'p_transposenrrd2',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GetMatricesFromBundle, 'p_transposenrrd3',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GetMatricesFromBundle, 'p_transposenrrd4',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GetMatricesFromBundle, 'p_transposenrrd5',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GetMatricesFromBundle, 'p_transposenrrd6',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GetMatricesFromBundle, 'p_matrix_selection',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetMatricesFromBundle, 'bundle',
                   (SCIRun_Bundle, "SCIRun_Bundle"))
  reg.add_output_port(scirun_GetMatricesFromBundle, 'bundle', 
                    (SCIRun_Bundle, 'bundle'))
  reg.add_output_port(scirun_GetMatricesFromBundle, 'matrix1', 
                    (SCIRun_Matrix, 'matrix1'))
  reg.add_output_port(scirun_GetMatricesFromBundle, 'matrix2', 
                    (SCIRun_Matrix, 'matrix2'))
  reg.add_output_port(scirun_GetMatricesFromBundle, 'matrix3', 
                    (SCIRun_Matrix, 'matrix3'))
  reg.add_output_port(scirun_GetMatricesFromBundle, 'matrix4', 
                    (SCIRun_Matrix, 'matrix4'))
  reg.add_output_port(scirun_GetMatricesFromBundle, 'matrix5', 
                    (SCIRun_Matrix, 'matrix5'))
  reg.add_output_port(scirun_GetMatricesFromBundle, 'matrix6', 
                    (SCIRun_Matrix, 'matrix6'))

  reg.add_module(scirun_RefineMesh)
  reg.add_input_port(scirun_RefineMesh, 'p_select',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_RefineMesh, 'p_method',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_RefineMesh, 'p_isoval',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_RefineMesh, 'Mesh',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_RefineMesh, 'Isovalue',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_RefineMesh, 'RefinedMesh', 
                    (SCIRun_Field, 'RefinedMesh'))
  reg.add_output_port(scirun_RefineMesh, 'Mapping', 
                    (SCIRun_Matrix, 'Mapping'))

  reg.add_module(scirun_MergeFields)
  reg.add_input_port(scirun_MergeFields, 'Container Mesh',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_MergeFields, 'Insert Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_MergeFields, 'Combined Field', 
                    (SCIRun_Field, 'Combined Field'))
  reg.add_output_port(scirun_MergeFields, 'Extended Insert Field', 
                    (SCIRun_Field, 'Extended Insert Field'))
  reg.add_output_port(scirun_MergeFields, 'Combined To Extended Mapping', 
                    (SCIRun_Matrix, 'Combined To Extended Mapping'))

  reg.add_module(scirun_BuildPointCloudToLatVolMappingMatrix)
  reg.add_input_port(scirun_BuildPointCloudToLatVolMappingMatrix, 'p_epsilon',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_BuildPointCloudToLatVolMappingMatrix, 'PointCloudField',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_BuildPointCloudToLatVolMappingMatrix, 'LatVolField',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_BuildPointCloudToLatVolMappingMatrix, 'MappingMatrix', 
                    (SCIRun_Matrix, 'MappingMatrix'))

  reg.add_module(scirun_CalculateDataArray)
  reg.add_input_port(scirun_CalculateDataArray, 'p_function',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CalculateDataArray, 'p_format',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CalculateDataArray, 'DataArray',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(scirun_CalculateDataArray, 'Function',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_input_port(scirun_CalculateDataArray, 'Array',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_CalculateDataArray, 'DataArray', 
                    (SCIRun_Matrix, 'DataArray'))

  reg.add_module(scirun_WriteColorMap)
  reg.add_input_port(scirun_WriteColorMap, 'p_filetype',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_WriteColorMap, 'p_confirm',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_WriteColorMap, 'p_confirm_once',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_WriteColorMap, 'p_exporttype',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_WriteColorMap, 'Input Data',
                   (SCIRun_ColorMap, "SCIRun_ColorMap"))
  reg.add_input_port(scirun_WriteColorMap, 'Filename',
                   (core.modules.basic_modules.String, 'tip'))

  reg.add_module(scirun_ShowTextureVolume)
  reg.add_input_port(scirun_ShowTextureVolume, 'p_sampling_rate_hi',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ShowTextureVolume, 'p_sampling_rate_lo',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ShowTextureVolume, 'p_gradient_min',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ShowTextureVolume, 'p_gradient_max',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ShowTextureVolume, 'p_adaptive',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowTextureVolume, 'p_cmap_size',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowTextureVolume, 'p_sw_raster',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowTextureVolume, 'p_render_style',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowTextureVolume, 'p_alpha_scale',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ShowTextureVolume, 'p_interp_mode',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowTextureVolume, 'p_shading',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowTextureVolume, 'p_ambient',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ShowTextureVolume, 'p_diffuse',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ShowTextureVolume, 'p_specular',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ShowTextureVolume, 'p_shine',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ShowTextureVolume, 'p_light',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowTextureVolume, 'p_blend_res',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowTextureVolume, 'p_multi_level',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowTextureVolume, 'p_use_stencil',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowTextureVolume, 'p_invert_opacity',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowTextureVolume, 'p_num_clipping_planes',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowTextureVolume, 'p_show_clipping_widgets',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowTextureVolume, 'p_level_on',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ShowTextureVolume, 'p_level_vals',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ShowTextureVolume, 'Texture',
                   (SCIRun_Texture, "SCIRun_Texture"))
  reg.add_input_port(scirun_ShowTextureVolume, 'ColorMap',
                   (SCIRun_ColorMap, "SCIRun_ColorMap"))
  reg.add_input_port(scirun_ShowTextureVolume, 'ColorMap2',
                   (SCIRun_ColorMap2, "SCIRun_ColorMap2"))
  reg.add_output_port(scirun_ShowTextureVolume, 'Geometry', 
                    (SCIRun_Geometry, 'Geometry'))
  reg.add_output_port(scirun_ShowTextureVolume, 'ColorMap', 
                    (SCIRun_ColorMap, 'ColorMap'))

  reg.add_module(scirun_GetCentroidsFromMesh)
  reg.add_input_port(scirun_GetCentroidsFromMesh, 'TetVolField',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_GetCentroidsFromMesh, 'PointCloudField', 
                    (SCIRun_Field, 'PointCloudField'))

  reg.add_module(scirun_ConvertLatVolDataFromNodeToElem)
  reg.add_input_port(scirun_ConvertLatVolDataFromNodeToElem, 'Node Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_ConvertLatVolDataFromNodeToElem, 'Elem Field', 
                    (SCIRun_Field, 'Elem Field'))

  reg.add_module(scirun_ReadColorMap2D)
  reg.add_input_port(scirun_ReadColorMap2D, 'p_from_env',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadColorMap2D, 'Filename',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_output_port(scirun_ReadColorMap2D, 'Output Data', 
                    (SCIRun_ColorMap2, 'Output Data'))
  reg.add_output_port(scirun_ReadColorMap2D, 'Filename', 
                    (core.modules.basic_modules.String, 'Filename'))

  reg.add_module(scirun_GetColumnOrRowFromMatrix)
  reg.add_input_port(scirun_GetColumnOrRowFromMatrix, 'p_row_or_col',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetColumnOrRowFromMatrix, 'p_selectable_min',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_GetColumnOrRowFromMatrix, 'p_selectable_max',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_GetColumnOrRowFromMatrix, 'p_selectable_inc',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GetColumnOrRowFromMatrix, 'p_selectable_units',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetColumnOrRowFromMatrix, 'p_range_min',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GetColumnOrRowFromMatrix, 'p_range_max',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GetColumnOrRowFromMatrix, 'p_playmode',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetColumnOrRowFromMatrix, 'p_current',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GetColumnOrRowFromMatrix, 'p_execmode',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetColumnOrRowFromMatrix, 'p_delay',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GetColumnOrRowFromMatrix, 'p_inc_amount',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GetColumnOrRowFromMatrix, 'p_send_amount',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GetColumnOrRowFromMatrix, 'p_data_series_done',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GetColumnOrRowFromMatrix, 'Matrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(scirun_GetColumnOrRowFromMatrix, 'Weight Vector',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(scirun_GetColumnOrRowFromMatrix, 'Current Index',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_GetColumnOrRowFromMatrix, 'Vector', 
                    (SCIRun_Matrix, 'Vector'))
  reg.add_output_port(scirun_GetColumnOrRowFromMatrix, 'Selected Index', 
                    (SCIRun_Matrix, 'Selected Index'))

  reg.add_module(scirun_ExtractIsosurfaceByFunction)
  reg.add_input_port(scirun_ExtractIsosurfaceByFunction, 'p_function',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ExtractIsosurfaceByFunction, 'p_zero_checks',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ExtractIsosurfaceByFunction, 'p_slice_value_min',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ExtractIsosurfaceByFunction, 'p_slice_value_max',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ExtractIsosurfaceByFunction, 'p_slice_value',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ExtractIsosurfaceByFunction, 'p_slice_value_typed',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ExtractIsosurfaceByFunction, 'p_slice_value_quantity',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ExtractIsosurfaceByFunction, 'p_quantity_range',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ExtractIsosurfaceByFunction, 'p_quantity_clusive',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ExtractIsosurfaceByFunction, 'p_quantity_min',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ExtractIsosurfaceByFunction, 'p_quantity_max',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ExtractIsosurfaceByFunction, 'p_quantity_list',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ExtractIsosurfaceByFunction, 'p_slice_value_list',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ExtractIsosurfaceByFunction, 'p_matrix_list',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ExtractIsosurfaceByFunction, 'p_algorithm',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ExtractIsosurfaceByFunction, 'p_build_trisurf',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ExtractIsosurfaceByFunction, 'p_build_geom',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ExtractIsosurfaceByFunction, 'p_active_slice_value_selection_tab',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ExtractIsosurfaceByFunction, 'p_active_tab',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ExtractIsosurfaceByFunction, 'p_update_type',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ExtractIsosurfaceByFunction, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_ExtractIsosurfaceByFunction, 'Optional Slice values',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_ExtractIsosurfaceByFunction, 'Output Field', 
                    (SCIRun_Field, 'Output Field'))

  reg.add_module(scirun_BuildNoiseColumnMatrix)
  reg.add_input_port(scirun_BuildNoiseColumnMatrix, 'p_snr',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_BuildNoiseColumnMatrix, 'Signal',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_BuildNoiseColumnMatrix, 'Noise', 
                    (SCIRun_Matrix, 'Noise'))

  reg.add_module(scirun_MergeTriSurfs)
  reg.add_input_port(scirun_MergeTriSurfs, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_MergeTriSurfs, 'Output Field', 
                    (SCIRun_Field, 'Output Field'))

  reg.add_module(scirun_ReadString)
  reg.add_input_port(scirun_ReadString, 'p_from_env',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadString, 'Filename',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_output_port(scirun_ReadString, 'Output Data', 
                    (core.modules.basic_modules.String, 'Output Data'))
  reg.add_output_port(scirun_ReadString, 'Filename', 
                    (core.modules.basic_modules.String, 'Filename'))

  reg.add_module(scirun_InterfaceWithTetGen)
  reg.add_input_port(scirun_InterfaceWithTetGen, 'p_switch',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InterfaceWithTetGen, 'Main',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_InterfaceWithTetGen, 'Points',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_InterfaceWithTetGen, 'Region Attribs',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_InterfaceWithTetGen, 'Regions',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_InterfaceWithTetGen, 'TetVol', 
                    (SCIRun_Field, 'TetVol'))

  reg.add_module(scirun_CalculateMeshNodes)
  reg.add_input_port(scirun_CalculateMeshNodes, 'p_function',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CalculateMeshNodes, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_CalculateMeshNodes, 'Function',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_input_port(scirun_CalculateMeshNodes, 'Array',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_CalculateMeshNodes, 'Field', 
                    (SCIRun_Field, 'Field'))

  reg.add_module(scirun_CreateImage)
  reg.add_input_port(scirun_CreateImage, 'p_sizex',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_CreateImage, 'p_sizey',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_CreateImage, 'p_sizez',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_CreateImage, 'p_z_value',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_CreateImage, 'p_auto_size',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_CreateImage, 'p_axis',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_CreateImage, 'p_padpercent',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_CreateImage, 'p_pos',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_CreateImage, 'p_data_at',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateImage, 'p_update_type',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateImage, 'p_corigin_x',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateImage, 'p_corigin_y',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateImage, 'p_corigin_z',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateImage, 'p_cnormal_x',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateImage, 'p_cnormal_y',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateImage, 'p_cnormal_z',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateImage, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_CreateImage, 'Output Sample Field', 
                    (SCIRun_Field, 'Output Sample Field'))

  reg.add_module(scirun_CalculateFieldDataCompiled)
  reg.add_input_port(scirun_CalculateFieldDataCompiled, 'p_outputdatatype',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CalculateFieldDataCompiled, 'p_function',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CalculateFieldDataCompiled, 'p_cache',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_CalculateFieldDataCompiled, 'Function',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_input_port(scirun_CalculateFieldDataCompiled, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_CalculateFieldDataCompiled, 'Output Field', 
                    (SCIRun_Field, 'Output Field'))

  reg.add_module(scirun_ReadColorMap)
  reg.add_input_port(scirun_ReadColorMap, 'p_from_env',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadColorMap, 'Filename',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_output_port(scirun_ReadColorMap, 'Output Data', 
                    (SCIRun_ColorMap, 'Output Data'))
  reg.add_output_port(scirun_ReadColorMap, 'Filename', 
                    (core.modules.basic_modules.String, 'Filename'))

  reg.add_module(scirun_MapFieldDataFromElemToNode)
  reg.add_input_port(scirun_MapFieldDataFromElemToNode, 'p_method',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_MapFieldDataFromElemToNode, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_MapFieldDataFromElemToNode, 'Field', 
                    (SCIRun_Field, 'Field'))

  reg.add_module(scirun_ShowFieldGlyphs)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_scalars_has_data',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_scalars_on',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_scalars_display_type',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_scalars_transparency',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_scalars_normalize',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_scalars_color_type',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_scalars_resolution',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_vectors_has_data',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_vectors_on',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_vectors_display_type',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_vectors_transparency',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_vectors_normalize',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_vectors_bidirectional',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_vectors_color_type',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_vectors_resolution',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_tensors_has_data',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_tensors_on',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_tensors_display_type',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_tensors_transparency',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_tensors_normalize',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_tensors_color_type',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_tensors_resolution',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_tensors_emphasis',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_secondary_has_data',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_secondary_on',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_secondary_display_type',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_secondary_color_type',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_secondary_alpha',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_secondary_value',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_tertiary_has_data',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_tertiary_on',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_tertiary_display_type',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_tertiary_color_type',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_tertiary_alpha',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_tertiary_value',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_text_on',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_text_color_type',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_text_color_r',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_text_color_g',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_text_color_b',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_text_backface_cull',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_text_always_visible',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_text_fontsize',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_text_precision',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_text_render_locations',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_text_show_data',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_text_show_nodes',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_text_show_edges',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_text_show_faces',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_text_show_cells',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_def_color_r',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_def_color_g',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_def_color_b',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_def_color_a',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_active_tab',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_interactive_mode',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_show_progress',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_field_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_field_name_override',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_approx_div',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'p_use_default_size',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowFieldGlyphs, 'Primary Data',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_ShowFieldGlyphs, 'Primary ColorMap',
                   (SCIRun_ColorMap, "SCIRun_ColorMap"))
  reg.add_input_port(scirun_ShowFieldGlyphs, 'Secondary Data',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_ShowFieldGlyphs, 'Secondary ColorMap',
                   (SCIRun_ColorMap, "SCIRun_ColorMap"))
  reg.add_input_port(scirun_ShowFieldGlyphs, 'Tertiary Data',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_ShowFieldGlyphs, 'Tertiary ColorMap',
                   (SCIRun_ColorMap, "SCIRun_ColorMap"))
  reg.add_output_port(scirun_ShowFieldGlyphs, 'Scene Graph', 
                    (SCIRun_Geometry, 'Scene Graph'))

  reg.add_module(scirun_JoinBundles)
  reg.add_input_port(scirun_JoinBundles, 'bundle',
                   (SCIRun_Bundle, "SCIRun_Bundle"))
  reg.add_output_port(scirun_JoinBundles, 'bundle', 
                    (SCIRun_Bundle, 'bundle'))

  reg.add_module(scirun_ApplyFilterToFieldData)
  reg.add_input_port(scirun_ApplyFilterToFieldData, 'p_method',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ApplyFilterToFieldData, 'p_ed_method',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ApplyFilterToFieldData, 'p_ed_iterations',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ApplyFilterToFieldData, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_ApplyFilterToFieldData, 'Field', 
                    (SCIRun_Field, 'Field'))

  reg.add_module(scirun_InsertHexVolSheetAlongSurface)
  reg.add_input_port(scirun_InsertHexVolSheetAlongSurface, 'p_side',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertHexVolSheetAlongSurface, 'p_addlayer',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertHexVolSheetAlongSurface, 'HexField',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_InsertHexVolSheetAlongSurface, 'TriField',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_InsertHexVolSheetAlongSurface, 'Side1Field', 
                    (SCIRun_Field, 'Side1Field'))
  reg.add_output_port(scirun_InsertHexVolSheetAlongSurface, 'Side2Field', 
                    (SCIRun_Field, 'Side2Field'))

  reg.add_module(scirun_GetFieldData)
  reg.add_input_port(scirun_GetFieldData, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_GetFieldData, 'Data', 
                    (SCIRun_Matrix, 'Data'))

  reg.add_module(scirun_CalculateFieldData2)
  reg.add_input_port(scirun_CalculateFieldData2, 'p_function',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CalculateFieldData2, 'p_format',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CalculateFieldData2, 'Field1',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_CalculateFieldData2, 'Field2',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_CalculateFieldData2, 'Function',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_input_port(scirun_CalculateFieldData2, 'Array',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_CalculateFieldData2, 'Field', 
                    (SCIRun_Field, 'Field'))

  reg.add_module(scirun_ReportBundleInfo)
  reg.add_input_port(scirun_ReportBundleInfo, 'p_tclinfostring',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReportBundleInfo, 'bundle',
                   (SCIRun_Bundle, "SCIRun_Bundle"))

  reg.add_module(scirun_GenerateSinglePointProbeFromField)
  reg.add_input_port(scirun_GenerateSinglePointProbeFromField, 'p_main_frame',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GenerateSinglePointProbeFromField, 'p_locx',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_GenerateSinglePointProbeFromField, 'p_locy',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_GenerateSinglePointProbeFromField, 'p_locz',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_GenerateSinglePointProbeFromField, 'p_value',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GenerateSinglePointProbeFromField, 'p_node',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GenerateSinglePointProbeFromField, 'p_edge',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GenerateSinglePointProbeFromField, 'p_face',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GenerateSinglePointProbeFromField, 'p_cell',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GenerateSinglePointProbeFromField, 'p_show_value',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GenerateSinglePointProbeFromField, 'p_show_node',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GenerateSinglePointProbeFromField, 'p_show_edge',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GenerateSinglePointProbeFromField, 'p_show_face',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GenerateSinglePointProbeFromField, 'p_show_cell',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GenerateSinglePointProbeFromField, 'p_probe_scale',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_GenerateSinglePointProbeFromField, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_GenerateSinglePointProbeFromField, 'GenerateSinglePointProbeFromField Widget', 
                    (SCIRun_Geometry, 'GenerateSinglePointProbeFromField Widget'))
  reg.add_output_port(scirun_GenerateSinglePointProbeFromField, 'GenerateSinglePointProbeFromField Point', 
                    (SCIRun_Field, 'GenerateSinglePointProbeFromField Point'))
  reg.add_output_port(scirun_GenerateSinglePointProbeFromField, 'Element Index', 
                    (SCIRun_Matrix, 'Element Index'))

  reg.add_module(scirun_ReportDataArrayMeasure)
  reg.add_input_port(scirun_ReportDataArrayMeasure, 'p_measure',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReportDataArrayMeasure, 'Array',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_ReportDataArrayMeasure, 'Measure', 
                    (SCIRun_Matrix, 'Measure'))

  reg.add_module(scirun_SmoothMesh)
  reg.add_input_port(scirun_SmoothMesh, 'Input',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_SmoothMesh, 'IsoValue',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_SmoothMesh, 'Smoothed', 
                    (SCIRun_Field, 'Smoothed'))

  reg.add_module(scirun_InsertPathsIntoBundle)
  reg.add_input_port(scirun_InsertPathsIntoBundle, 'p_path1_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertPathsIntoBundle, 'p_path2_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertPathsIntoBundle, 'p_path3_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertPathsIntoBundle, 'p_path4_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertPathsIntoBundle, 'p_path5_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertPathsIntoBundle, 'p_path6_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertPathsIntoBundle, 'p_replace1',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_InsertPathsIntoBundle, 'p_replace2',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_InsertPathsIntoBundle, 'p_replace3',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_InsertPathsIntoBundle, 'p_replace4',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_InsertPathsIntoBundle, 'p_replace5',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_InsertPathsIntoBundle, 'p_replace6',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_InsertPathsIntoBundle, 'p_bundlename',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertPathsIntoBundle, 'bundle',
                   (SCIRun_Bundle, "SCIRun_Bundle"))
  reg.add_input_port(scirun_InsertPathsIntoBundle, 'path1',
                   (SCIRun_Path, "SCIRun_Path"))
  reg.add_input_port(scirun_InsertPathsIntoBundle, 'path2',
                   (SCIRun_Path, "SCIRun_Path"))
  reg.add_input_port(scirun_InsertPathsIntoBundle, 'path3',
                   (SCIRun_Path, "SCIRun_Path"))
  reg.add_input_port(scirun_InsertPathsIntoBundle, 'path4',
                   (SCIRun_Path, "SCIRun_Path"))
  reg.add_input_port(scirun_InsertPathsIntoBundle, 'path5',
                   (SCIRun_Path, "SCIRun_Path"))
  reg.add_input_port(scirun_InsertPathsIntoBundle, 'path6',
                   (SCIRun_Path, "SCIRun_Path"))
  reg.add_output_port(scirun_InsertPathsIntoBundle, 'bundle', 
                    (SCIRun_Bundle, 'bundle'))

  reg.add_module(scirun_SplitFileName)
  reg.add_input_port(scirun_SplitFileName, 'Filename',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_output_port(scirun_SplitFileName, 'Pathname', 
                    (core.modules.basic_modules.String, 'Pathname'))
  reg.add_output_port(scirun_SplitFileName, 'Filename Base', 
                    (core.modules.basic_modules.String, 'Filename Base'))
  reg.add_output_port(scirun_SplitFileName, 'Extension', 
                    (core.modules.basic_modules.String, 'Extension'))
  reg.add_output_port(scirun_SplitFileName, 'Filename', 
                    (core.modules.basic_modules.String, 'Filename'))

  reg.add_module(scirun_CalculateLatVolGradientsAtNodes)
  reg.add_input_port(scirun_CalculateLatVolGradientsAtNodes, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_CalculateLatVolGradientsAtNodes, 'Output Gradient', 
                    (SCIRun_Field, 'Output Gradient'))

  reg.add_module(scirun_CalculateGradients)
  reg.add_input_port(scirun_CalculateGradients, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_CalculateGradients, 'Output CalculateGradients', 
                    (SCIRun_Field, 'Output CalculateGradients'))

  reg.add_module(scirun_GetColorMap2sFromBundle)
  reg.add_input_port(scirun_GetColorMap2sFromBundle, 'p_colormap21_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetColorMap2sFromBundle, 'p_colormap22_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetColorMap2sFromBundle, 'p_colormap23_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetColorMap2sFromBundle, 'p_colormap24_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetColorMap2sFromBundle, 'p_colormap25_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetColorMap2sFromBundle, 'p_colormap26_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetColorMap2sFromBundle, 'p_colormap2_selection',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetColorMap2sFromBundle, 'bundle',
                   (SCIRun_Bundle, "SCIRun_Bundle"))
  reg.add_output_port(scirun_GetColorMap2sFromBundle, 'bundle', 
                    (SCIRun_Bundle, 'bundle'))
  reg.add_output_port(scirun_GetColorMap2sFromBundle, 'colormap21', 
                    (SCIRun_ColorMap2, 'colormap21'))
  reg.add_output_port(scirun_GetColorMap2sFromBundle, 'colormap22', 
                    (SCIRun_ColorMap2, 'colormap22'))
  reg.add_output_port(scirun_GetColorMap2sFromBundle, 'colormap23', 
                    (SCIRun_ColorMap2, 'colormap23'))
  reg.add_output_port(scirun_GetColorMap2sFromBundle, 'colormap24', 
                    (SCIRun_ColorMap2, 'colormap24'))
  reg.add_output_port(scirun_GetColorMap2sFromBundle, 'colormap25', 
                    (SCIRun_ColorMap2, 'colormap25'))
  reg.add_output_port(scirun_GetColorMap2sFromBundle, 'colormap26', 
                    (SCIRun_ColorMap2, 'colormap26'))

  reg.add_module(scirun_ReadMatrix)
  reg.add_input_port(scirun_ReadMatrix, 'p_from_env',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadMatrix, 'Filename',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_output_port(scirun_ReadMatrix, 'Output Data', 
                    (SCIRun_Matrix, 'Output Data'))
  reg.add_output_port(scirun_ReadMatrix, 'Filename', 
                    (core.modules.basic_modules.String, 'Filename'))

  reg.add_module(scirun_GenerateStreamLines)
  reg.add_input_port(scirun_GenerateStreamLines, 'p_stepsize',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_GenerateStreamLines, 'p_tolerance',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_GenerateStreamLines, 'p_maxsteps',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GenerateStreamLines, 'p_direction',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GenerateStreamLines, 'p_value',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GenerateStreamLines, 'p_remove_colinear_pts',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GenerateStreamLines, 'p_method',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GenerateStreamLines, 'p_nthreads',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GenerateStreamLines, 'p_auto_parameterize',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GenerateStreamLines, 'Vector Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_GenerateStreamLines, 'Seed Points',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_GenerateStreamLines, 'Streamlines', 
                    (SCIRun_Field, 'Streamlines'))

  reg.add_module(scirun_EditMeshBoundingBox)
  reg.add_input_port(scirun_EditMeshBoundingBox, 'p_outputcenterx',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_EditMeshBoundingBox, 'p_outputcentery',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_EditMeshBoundingBox, 'p_outputcenterz',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_EditMeshBoundingBox, 'p_outputsizex',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_EditMeshBoundingBox, 'p_outputsizey',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_EditMeshBoundingBox, 'p_outputsizez',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_EditMeshBoundingBox, 'p_useoutputcenter',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_EditMeshBoundingBox, 'p_useoutputsize',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_EditMeshBoundingBox, 'p_box_scale',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_EditMeshBoundingBox, 'p_box_mode',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_EditMeshBoundingBox, 'p_box_real_scale',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_EditMeshBoundingBox, 'p_box_center_x',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_EditMeshBoundingBox, 'p_box_center_y',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_EditMeshBoundingBox, 'p_box_center_z',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_EditMeshBoundingBox, 'p_box_right_x',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_EditMeshBoundingBox, 'p_box_right_y',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_EditMeshBoundingBox, 'p_box_right_z',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_EditMeshBoundingBox, 'p_box_down_x',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_EditMeshBoundingBox, 'p_box_down_y',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_EditMeshBoundingBox, 'p_box_down_z',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_EditMeshBoundingBox, 'p_box_in_x',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_EditMeshBoundingBox, 'p_box_in_y',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_EditMeshBoundingBox, 'p_box_in_z',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_EditMeshBoundingBox, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_EditMeshBoundingBox, 'Output Field', 
                    (SCIRun_Field, 'Output Field'))
  reg.add_output_port(scirun_EditMeshBoundingBox, 'Transformation Widget', 
                    (SCIRun_Geometry, 'Transformation Widget'))
  reg.add_output_port(scirun_EditMeshBoundingBox, 'Transformation Matrix', 
                    (SCIRun_Matrix, 'Transformation Matrix'))

  reg.add_module(scirun_PrintStringIntoString)
  reg.add_input_port(scirun_PrintStringIntoString, 'p_formatstring',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_PrintStringIntoString, 'Format',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_input_port(scirun_PrintStringIntoString, 'Input',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_output_port(scirun_PrintStringIntoString, 'Output', 
                    (core.modules.basic_modules.String, 'Output'))

  reg.add_module(scirun_GenerateStreamLinesWithPlacementHeuristic)
  reg.add_input_port(scirun_GenerateStreamLinesWithPlacementHeuristic, 'p_numsl',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GenerateStreamLinesWithPlacementHeuristic, 'p_numpts',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GenerateStreamLinesWithPlacementHeuristic, 'p_minper',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_GenerateStreamLinesWithPlacementHeuristic, 'p_maxper',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_GenerateStreamLinesWithPlacementHeuristic, 'p_ming',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_GenerateStreamLinesWithPlacementHeuristic, 'p_maxg',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_GenerateStreamLinesWithPlacementHeuristic, 'p_numsamples',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GenerateStreamLinesWithPlacementHeuristic, 'p_method',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GenerateStreamLinesWithPlacementHeuristic, 'p_stepsize',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_GenerateStreamLinesWithPlacementHeuristic, 'p_stepout',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GenerateStreamLinesWithPlacementHeuristic, 'p_maxsteps',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GenerateStreamLinesWithPlacementHeuristic, 'p_minmag',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_GenerateStreamLinesWithPlacementHeuristic, 'p_direction',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GenerateStreamLinesWithPlacementHeuristic, 'Source',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_GenerateStreamLinesWithPlacementHeuristic, 'Weighting',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_GenerateStreamLinesWithPlacementHeuristic, 'Flow',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_GenerateStreamLinesWithPlacementHeuristic, 'Compare',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_GenerateStreamLinesWithPlacementHeuristic, 'Seed points',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_GenerateStreamLinesWithPlacementHeuristic, 'Streamlines', 
                    (SCIRun_Field, 'Streamlines'))
  reg.add_output_port(scirun_GenerateStreamLinesWithPlacementHeuristic, 'Render', 
                    (SCIRun_Field, 'Render'))

  reg.add_module(scirun_CalculateSignedDistanceToField)
  reg.add_input_port(scirun_CalculateSignedDistanceToField, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_CalculateSignedDistanceToField, 'ObjectField',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_CalculateSignedDistanceToField, 'SignedDistanceField', 
                    (SCIRun_Field, 'SignedDistanceField'))

  reg.add_module(scirun_SetFieldDataValues)
  reg.add_input_port(scirun_SetFieldDataValues, 'p_newval',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_SetFieldDataValues, 'InField',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_SetFieldDataValues, 'OutField', 
                    (SCIRun_Field, 'OutField'))

  reg.add_module(scirun_EvaluateLinAlgUnary)
  reg.add_input_port(scirun_EvaluateLinAlgUnary, 'p_op',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_EvaluateLinAlgUnary, 'p_function',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_EvaluateLinAlgUnary, 'Input',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_EvaluateLinAlgUnary, 'Output', 
                    (SCIRun_Matrix, 'Output'))

  reg.add_module(scirun_GetSubmatrix)
  reg.add_input_port(scirun_GetSubmatrix, 'p_mincol',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetSubmatrix, 'p_maxcol',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetSubmatrix, 'p_minrow',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetSubmatrix, 'p_maxrow',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetSubmatrix, 'p_nrow',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetSubmatrix, 'p_ncol',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetSubmatrix, 'Input Matrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(scirun_GetSubmatrix, 'Optional Range Bounds',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_GetSubmatrix, 'Output Matrix', 
                    (SCIRun_Matrix, 'Output Matrix'))

  reg.add_module(scirun_InsertMatricesIntoBundle)
  reg.add_input_port(scirun_InsertMatricesIntoBundle, 'p_matrix1_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertMatricesIntoBundle, 'p_matrix2_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertMatricesIntoBundle, 'p_matrix3_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertMatricesIntoBundle, 'p_matrix4_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertMatricesIntoBundle, 'p_matrix5_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertMatricesIntoBundle, 'p_matrix6_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertMatricesIntoBundle, 'p_replace1',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_InsertMatricesIntoBundle, 'p_replace2',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_InsertMatricesIntoBundle, 'p_replace3',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_InsertMatricesIntoBundle, 'p_replace4',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_InsertMatricesIntoBundle, 'p_replace5',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_InsertMatricesIntoBundle, 'p_replace6',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_InsertMatricesIntoBundle, 'p_bundlename',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertMatricesIntoBundle, 'bundle',
                   (SCIRun_Bundle, "SCIRun_Bundle"))
  reg.add_input_port(scirun_InsertMatricesIntoBundle, 'matrix1',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(scirun_InsertMatricesIntoBundle, 'matrix2',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(scirun_InsertMatricesIntoBundle, 'matrix3',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(scirun_InsertMatricesIntoBundle, 'matrix4',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(scirun_InsertMatricesIntoBundle, 'matrix5',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(scirun_InsertMatricesIntoBundle, 'matrix6',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_InsertMatricesIntoBundle, 'bundle', 
                    (SCIRun_Bundle, 'bundle'))

  reg.add_module(scirun_CalculateInsideWhichField)
  reg.add_input_port(scirun_CalculateInsideWhichField, 'p_outputbasis',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CalculateInsideWhichField, 'p_outputtype',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CalculateInsideWhichField, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_CalculateInsideWhichField, 'Object',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_CalculateInsideWhichField, 'Field', 
                    (SCIRun_Field, 'Field'))

  reg.add_module(scirun_WriteString)
  reg.add_input_port(scirun_WriteString, 'p_filetype',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_WriteString, 'p_confirm',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_WriteString, 'p_confirm_once',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_WriteString, 'String',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_input_port(scirun_WriteString, 'Filename',
                   (core.modules.basic_modules.String, 'tip'))

  reg.add_module(scirun_TimeControls)
  reg.add_input_port(scirun_TimeControls, 'p_execmode',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_TimeControls, 'p_scale_factor',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_output_port(scirun_TimeControls, 'time', 
                    (SCIRun_Time, 'time'))

  reg.add_module(scirun_InterfaceWithCubit)
  reg.add_input_port(scirun_InterfaceWithCubit, 'p_cubitdir',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InterfaceWithCubit, 'p_ncdump',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InterfaceWithCubit, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_InterfaceWithCubit, 'PointCloudField',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_InterfaceWithCubit, 'Field', 
                    (SCIRun_Field, 'Field'))

  reg.add_module(scirun_AppendDataArrays)
  reg.add_input_port(scirun_AppendDataArrays, 'Array',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_AppendDataArrays, 'Array', 
                    (SCIRun_Matrix, 'Array'))

  reg.add_module(scirun_ReadPath)
  reg.add_input_port(scirun_ReadPath, 'p_from_env',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadPath, 'Filename',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_output_port(scirun_ReadPath, 'Output Data', 
                    (SCIRun_Path, 'Output Data'))
  reg.add_output_port(scirun_ReadPath, 'Filename', 
                    (core.modules.basic_modules.String, 'Filename'))

  reg.add_module(scirun_CreateString)
  reg.add_input_port(scirun_CreateString, 'p_inputstring',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_output_port(scirun_CreateString, 'Output', 
                    (core.modules.basic_modules.String, 'Output'))

  reg.add_module(scirun_ClipFieldByFunction)
  reg.add_input_port(scirun_ClipFieldByFunction, 'p_mode',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ClipFieldByFunction, 'p_function',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ClipFieldByFunction, 'Function',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_input_port(scirun_ClipFieldByFunction, 'Input',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_ClipFieldByFunction, 'Clipped', 
                    (SCIRun_Field, 'Clipped'))
  reg.add_output_port(scirun_ClipFieldByFunction, 'Mapping', 
                    (SCIRun_Matrix, 'Mapping'))
  reg.add_output_port(scirun_ClipFieldByFunction, 'MaskVector', 
                    (SCIRun_Nrrd, 'MaskVector'))

  reg.add_module(scirun_CreateTensorArray)
  reg.add_input_port(scirun_CreateTensorArray, 'EigenVector1',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(scirun_CreateTensorArray, 'EigenVector2',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(scirun_CreateTensorArray, 'EigenValue1',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(scirun_CreateTensorArray, 'EigenValue2',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(scirun_CreateTensorArray, 'EigenValue3',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_CreateTensorArray, 'TensorArray', 
                    (SCIRun_Matrix, 'TensorArray'))

  reg.add_module(scirun_WriteField)
  reg.add_input_port(scirun_WriteField, 'p_filetype',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_WriteField, 'p_confirm',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_WriteField, 'p_confirm_once',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_WriteField, 'p_exporttype',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_WriteField, 'p_increment',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_WriteField, 'p_current',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_WriteField, 'Input Data',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_WriteField, 'Filename',
                   (core.modules.basic_modules.String, 'tip'))

  reg.add_module(scirun_BuildMappingMatrix)
  reg.add_input_port(scirun_BuildMappingMatrix, 'p_interpolation_basis',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_BuildMappingMatrix, 'p_map_source_to_single_dest',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_BuildMappingMatrix, 'p_exhaustive_search',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_BuildMappingMatrix, 'p_exhaustive_search_max_dist',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_BuildMappingMatrix, 'p_np',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_BuildMappingMatrix, 'Source',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_BuildMappingMatrix, 'Destination',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_BuildMappingMatrix, 'Mapping', 
                    (SCIRun_Matrix, 'Mapping'))

  reg.add_module(scirun_InsertNrrdsIntoBundle)
  reg.add_input_port(scirun_InsertNrrdsIntoBundle, 'p_nrrd1_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertNrrdsIntoBundle, 'p_nrrd2_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertNrrdsIntoBundle, 'p_nrrd3_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertNrrdsIntoBundle, 'p_nrrd4_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertNrrdsIntoBundle, 'p_nrrd5_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertNrrdsIntoBundle, 'p_nrrd6_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertNrrdsIntoBundle, 'p_replace1',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_InsertNrrdsIntoBundle, 'p_replace2',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_InsertNrrdsIntoBundle, 'p_replace3',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_InsertNrrdsIntoBundle, 'p_replace4',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_InsertNrrdsIntoBundle, 'p_replace5',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_InsertNrrdsIntoBundle, 'p_replace6',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_InsertNrrdsIntoBundle, 'p_bundlename',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertNrrdsIntoBundle, 'bundle',
                   (SCIRun_Bundle, "SCIRun_Bundle"))
  reg.add_input_port(scirun_InsertNrrdsIntoBundle, 'nrrd1',
                   (SCIRun_Nrrd, "SCIRun_Nrrd"))
  reg.add_input_port(scirun_InsertNrrdsIntoBundle, 'nrrd2',
                   (SCIRun_Nrrd, "SCIRun_Nrrd"))
  reg.add_input_port(scirun_InsertNrrdsIntoBundle, 'nrrd3',
                   (SCIRun_Nrrd, "SCIRun_Nrrd"))
  reg.add_input_port(scirun_InsertNrrdsIntoBundle, 'nrrd4',
                   (SCIRun_Nrrd, "SCIRun_Nrrd"))
  reg.add_input_port(scirun_InsertNrrdsIntoBundle, 'nrrd5',
                   (SCIRun_Nrrd, "SCIRun_Nrrd"))
  reg.add_input_port(scirun_InsertNrrdsIntoBundle, 'nrrd6',
                   (SCIRun_Nrrd, "SCIRun_Nrrd"))
  reg.add_output_port(scirun_InsertNrrdsIntoBundle, 'bundle', 
                    (SCIRun_Bundle, 'bundle'))

  reg.add_module(scirun_InsertBundlesIntoBundle)
  reg.add_input_port(scirun_InsertBundlesIntoBundle, 'p_bundle1_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertBundlesIntoBundle, 'p_bundle2_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertBundlesIntoBundle, 'p_bundle3_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertBundlesIntoBundle, 'p_bundle4_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertBundlesIntoBundle, 'p_bundle5_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertBundlesIntoBundle, 'p_bundle6_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertBundlesIntoBundle, 'p_replace1',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_InsertBundlesIntoBundle, 'p_replace2',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_InsertBundlesIntoBundle, 'p_replace3',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_InsertBundlesIntoBundle, 'p_replace4',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_InsertBundlesIntoBundle, 'p_replace5',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_InsertBundlesIntoBundle, 'p_replace6',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_InsertBundlesIntoBundle, 'p_bundlename',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertBundlesIntoBundle, 'bundle',
                   (SCIRun_Bundle, "SCIRun_Bundle"))
  reg.add_input_port(scirun_InsertBundlesIntoBundle, 'bundle1',
                   (SCIRun_Bundle, "SCIRun_Bundle"))
  reg.add_input_port(scirun_InsertBundlesIntoBundle, 'bundle2',
                   (SCIRun_Bundle, "SCIRun_Bundle"))
  reg.add_input_port(scirun_InsertBundlesIntoBundle, 'bundle3',
                   (SCIRun_Bundle, "SCIRun_Bundle"))
  reg.add_input_port(scirun_InsertBundlesIntoBundle, 'bundle4',
                   (SCIRun_Bundle, "SCIRun_Bundle"))
  reg.add_input_port(scirun_InsertBundlesIntoBundle, 'bundle5',
                   (SCIRun_Bundle, "SCIRun_Bundle"))
  reg.add_input_port(scirun_InsertBundlesIntoBundle, 'bundle6',
                   (SCIRun_Bundle, "SCIRun_Bundle"))
  reg.add_output_port(scirun_InsertBundlesIntoBundle, 'bundle', 
                    (SCIRun_Bundle, 'bundle'))

  reg.add_module(scirun_ReadBundle)
  reg.add_input_port(scirun_ReadBundle, 'p_from_env',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadBundle, 'p_types',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReadBundle, 'Filename',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_output_port(scirun_ReadBundle, 'bundle', 
                    (SCIRun_Bundle, 'bundle'))
  reg.add_output_port(scirun_ReadBundle, 'Filename', 
                    (core.modules.basic_modules.String, 'Filename'))

  reg.add_module(scirun_GetStringsFromBundle)
  reg.add_input_port(scirun_GetStringsFromBundle, 'p_string1_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetStringsFromBundle, 'p_string2_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetStringsFromBundle, 'p_string3_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetStringsFromBundle, 'p_string4_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetStringsFromBundle, 'p_string5_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetStringsFromBundle, 'p_string6_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetStringsFromBundle, 'p_string_selection',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetStringsFromBundle, 'bundle',
                   (SCIRun_Bundle, "SCIRun_Bundle"))
  reg.add_output_port(scirun_GetStringsFromBundle, 'bundle', 
                    (SCIRun_Bundle, 'bundle'))
  reg.add_output_port(scirun_GetStringsFromBundle, 'string1', 
                    (core.modules.basic_modules.String, 'string1'))
  reg.add_output_port(scirun_GetStringsFromBundle, 'string2', 
                    (core.modules.basic_modules.String, 'string2'))
  reg.add_output_port(scirun_GetStringsFromBundle, 'string3', 
                    (core.modules.basic_modules.String, 'string3'))
  reg.add_output_port(scirun_GetStringsFromBundle, 'string4', 
                    (core.modules.basic_modules.String, 'string4'))
  reg.add_output_port(scirun_GetStringsFromBundle, 'string5', 
                    (core.modules.basic_modules.String, 'string5'))
  reg.add_output_port(scirun_GetStringsFromBundle, 'string6', 
                    (core.modules.basic_modules.String, 'string6'))

  reg.add_module(scirun_ShowString)
  reg.add_input_port(scirun_ShowString, 'p_bbox',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowString, 'p_size',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowString, 'p_location_x',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ShowString, 'p_location_y',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ShowString, 'p_color_r',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ShowString, 'p_color_g',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ShowString, 'p_color_b',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ShowString, 'Format String',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_output_port(scirun_ShowString, 'Title', 
                    (SCIRun_Geometry, 'Title'))

  reg.add_module(scirun_SwapNodeLocationsWithMatrixEntries)
  reg.add_input_port(scirun_SwapNodeLocationsWithMatrixEntries, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_SwapNodeLocationsWithMatrixEntries, 'Input Matrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_SwapNodeLocationsWithMatrixEntries, 'Output Field', 
                    (SCIRun_Field, 'Output Field'))
  reg.add_output_port(scirun_SwapNodeLocationsWithMatrixEntries, 'Output Matrix', 
                    (SCIRun_Matrix, 'Output Matrix'))

  reg.add_module(scirun_ReorderMatrixByReverseCuthillMcKee)
  reg.add_input_port(scirun_ReorderMatrixByReverseCuthillMcKee, 'Matrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_ReorderMatrixByReverseCuthillMcKee, 'Matrix', 
                    (SCIRun_Matrix, 'Matrix'))
  reg.add_output_port(scirun_ReorderMatrixByReverseCuthillMcKee, 'Mapping', 
                    (SCIRun_Matrix, 'Mapping'))
  reg.add_output_port(scirun_ReorderMatrixByReverseCuthillMcKee, 'InverseMapping', 
                    (SCIRun_Matrix, 'InverseMapping'))

  reg.add_module(scirun_MapFieldDataFromNodeToElem)
  reg.add_input_port(scirun_MapFieldDataFromNodeToElem, 'p_method',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_MapFieldDataFromNodeToElem, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_MapFieldDataFromNodeToElem, 'Field', 
                    (SCIRun_Field, 'Field'))

  reg.add_module(scirun_GetDomainBoundary)
  reg.add_input_port(scirun_GetDomainBoundary, 'p_userange',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GetDomainBoundary, 'p_minrange',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_GetDomainBoundary, 'p_maxrange',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_GetDomainBoundary, 'p_usevalue',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GetDomainBoundary, 'p_value',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_GetDomainBoundary, 'p_includeouterboundary',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GetDomainBoundary, 'p_innerboundaryonly',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GetDomainBoundary, 'p_noinnerboundary',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GetDomainBoundary, 'p_disconnect',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GetDomainBoundary, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_GetDomainBoundary, 'MinValueValue',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(scirun_GetDomainBoundary, 'MaxValue',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_GetDomainBoundary, 'Field', 
                    (SCIRun_Field, 'Field'))

  reg.add_module(scirun_CollectFields)
  reg.add_input_port(scirun_CollectFields, 'p_buffersize',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_CollectFields, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_CollectFields, 'BufferSize',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_CollectFields, 'Fields', 
                    (SCIRun_Field, 'Fields'))

  reg.add_module(scirun_ReportStringInfo)
  reg.add_input_port(scirun_ReportStringInfo, 'p_inputstring',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReportStringInfo, 'Input',
                   (core.modules.basic_modules.String, 'tip'))

  reg.add_module(scirun_StreamMatrixFromDisk)
  reg.add_input_port(scirun_StreamMatrixFromDisk, 'p_row_or_col',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_StreamMatrixFromDisk, 'p_slider_min',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_StreamMatrixFromDisk, 'p_slider_max',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_StreamMatrixFromDisk, 'p_range_min',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_StreamMatrixFromDisk, 'p_range_max',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_StreamMatrixFromDisk, 'p_playmode',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_StreamMatrixFromDisk, 'p_current',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_StreamMatrixFromDisk, 'p_execmode',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_StreamMatrixFromDisk, 'p_delay',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_StreamMatrixFromDisk, 'p_inc_amount',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_StreamMatrixFromDisk, 'p_send_amount',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_StreamMatrixFromDisk, 'Indices',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(scirun_StreamMatrixFromDisk, 'Weights',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(scirun_StreamMatrixFromDisk, 'Filename',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_output_port(scirun_StreamMatrixFromDisk, 'DataVector', 
                    (SCIRun_Matrix, 'DataVector'))
  reg.add_output_port(scirun_StreamMatrixFromDisk, 'Index', 
                    (SCIRun_Matrix, 'Index'))
  reg.add_output_port(scirun_StreamMatrixFromDisk, 'Scaled Index', 
                    (SCIRun_Matrix, 'Scaled Index'))
  reg.add_output_port(scirun_StreamMatrixFromDisk, 'Filename', 
                    (core.modules.basic_modules.String, 'Filename'))

  reg.add_module(scirun_WriteMatrix)
  reg.add_input_port(scirun_WriteMatrix, 'p_filetype',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_WriteMatrix, 'p_confirm',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_WriteMatrix, 'p_confirm_once',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_WriteMatrix, 'p_exporttype',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_WriteMatrix, 'p_split',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_WriteMatrix, 'Input Data',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(scirun_WriteMatrix, 'Filename',
                   (core.modules.basic_modules.String, 'tip'))

  reg.add_module(scirun_ConvertFieldDataType)
  reg.add_input_port(scirun_ConvertFieldDataType, 'p_outputdatatype',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ConvertFieldDataType, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_ConvertFieldDataType, 'Output Field', 
                    (SCIRun_Field, 'Output Field'))

  reg.add_module(scirun_GeneratePointSamplesFromField)
  reg.add_input_port(scirun_GeneratePointSamplesFromField, 'p_num_seeds',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GeneratePointSamplesFromField, 'p_probe_scale',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_GeneratePointSamplesFromField, 'p_send',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GeneratePointSamplesFromField, 'p_widget',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GeneratePointSamplesFromField, 'p_red',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_GeneratePointSamplesFromField, 'p_green',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_GeneratePointSamplesFromField, 'p_blue',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_GeneratePointSamplesFromField, 'p_auto_execute',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GeneratePointSamplesFromField, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_GeneratePointSamplesFromField, 'GeneratePointSamplesFromField Widget', 
                    (SCIRun_Geometry, 'GeneratePointSamplesFromField Widget'))
  reg.add_output_port(scirun_GeneratePointSamplesFromField, 'GeneratePointSamplesFromField Point', 
                    (SCIRun_Field, 'GeneratePointSamplesFromField Point'))

  reg.add_module(scirun_GeneratePointSamplesFromFieldOrWidget)
  reg.add_input_port(scirun_GeneratePointSamplesFromFieldOrWidget, 'p_wtype',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GeneratePointSamplesFromFieldOrWidget, 'p_endpoints',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GeneratePointSamplesFromFieldOrWidget, 'p_maxseeds',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_GeneratePointSamplesFromFieldOrWidget, 'p_numseeds',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GeneratePointSamplesFromFieldOrWidget, 'p_rngseed',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GeneratePointSamplesFromFieldOrWidget, 'p_rnginc',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GeneratePointSamplesFromFieldOrWidget, 'p_clamp',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GeneratePointSamplesFromFieldOrWidget, 'p_autoexecute',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GeneratePointSamplesFromFieldOrWidget, 'p_dist',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GeneratePointSamplesFromFieldOrWidget, 'p_whichtab',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GeneratePointSamplesFromFieldOrWidget, 'Field to Sample',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_GeneratePointSamplesFromFieldOrWidget, 'Samples', 
                    (SCIRun_Field, 'Samples'))
  reg.add_output_port(scirun_GeneratePointSamplesFromFieldOrWidget, 'Sampling Widget', 
                    (SCIRun_Geometry, 'Sampling Widget'))

  reg.add_module(scirun_CreateMatrix)
  reg.add_input_port(scirun_CreateMatrix, 'p_rows',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_CreateMatrix, 'p_cols',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_CreateMatrix, 'p_data',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateMatrix, 'p_clabel',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateMatrix, 'p_rlabel',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_output_port(scirun_CreateMatrix, 'matrix', 
                    (SCIRun_Matrix, 'matrix'))

  reg.add_module(scirun_CalculateIsInsideField)
  reg.add_input_port(scirun_CalculateIsInsideField, 'p_outputbasis',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CalculateIsInsideField, 'p_outputtype',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CalculateIsInsideField, 'p_outval',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_CalculateIsInsideField, 'p_inval',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_CalculateIsInsideField, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_CalculateIsInsideField, 'ObjectField',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_CalculateIsInsideField, 'Field', 
                    (SCIRun_Field, 'Field'))

  reg.add_module(scirun_CreateAndEditColorMap)
  reg.add_input_port(scirun_CreateAndEditColorMap, 'p_rgbhsv',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_CreateAndEditColorMap, 'p_rgb_points',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateAndEditColorMap, 'p_alpha_points',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateAndEditColorMap, 'p_resolution',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_CreateAndEditColorMap, 'ColorMap',
                   (SCIRun_ColorMap, "SCIRun_ColorMap"))
  reg.add_output_port(scirun_CreateAndEditColorMap, 'ColorMap', 
                    (SCIRun_ColorMap, 'ColorMap'))
  reg.add_output_port(scirun_CreateAndEditColorMap, 'Geometry', 
                    (SCIRun_Geometry, 'Geometry'))

  reg.add_module(scirun_DecimateTriSurf)
  reg.add_input_port(scirun_DecimateTriSurf, 'TriSurf',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_DecimateTriSurf, 'Decimated', 
                    (SCIRun_Field, 'Decimated'))

  reg.add_module(scirun_CoregisterPointClouds)
  reg.add_input_port(scirun_CoregisterPointClouds, 'p_allowScale',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_CoregisterPointClouds, 'p_allowRotate',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_CoregisterPointClouds, 'p_allowTranslate',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_CoregisterPointClouds, 'p_seed',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_CoregisterPointClouds, 'p_iters',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_CoregisterPointClouds, 'p_misfitTol',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_CoregisterPointClouds, 'p_method',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CoregisterPointClouds, 'Fixed PointCloudField',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_CoregisterPointClouds, 'Mobile PointCloudField',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_CoregisterPointClouds, 'DistanceField From Fixed',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_CoregisterPointClouds, 'Transform', 
                    (SCIRun_Matrix, 'Transform'))

  reg.add_module(scirun_SolveMinNormLeastSqSystem)
  reg.add_input_port(scirun_SolveMinNormLeastSqSystem, 'BasisVec1',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(scirun_SolveMinNormLeastSqSystem, 'BasisVec2',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(scirun_SolveMinNormLeastSqSystem, 'BasisVec3',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(scirun_SolveMinNormLeastSqSystem, 'TargetVec',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_SolveMinNormLeastSqSystem, 'WeightVec(Col)', 
                    (SCIRun_Matrix, 'WeightVec(Col)'))
  reg.add_output_port(scirun_SolveMinNormLeastSqSystem, 'ResultVec(Col)', 
                    (SCIRun_Matrix, 'ResultVec(Col)'))

  reg.add_module(scirun_CalculateFieldData)
  reg.add_input_port(scirun_CalculateFieldData, 'p_function',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CalculateFieldData, 'p_format',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CalculateFieldData, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_CalculateFieldData, 'Function',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_input_port(scirun_CalculateFieldData, 'Array',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_CalculateFieldData, 'Field', 
                    (SCIRun_Field, 'Field'))

  reg.add_module(scirun_MapFieldDataToNodeCoordinate)
  reg.add_input_port(scirun_MapFieldDataToNodeCoordinate, 'p_coord',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_MapFieldDataToNodeCoordinate, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_MapFieldDataToNodeCoordinate, 'Output Field', 
                    (SCIRun_Field, 'Output Field'))

  reg.add_module(scirun_ShowMeshBoundingBox)
  reg.add_input_port(scirun_ShowMeshBoundingBox, 'p_sizex',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowMeshBoundingBox, 'p_sizey',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowMeshBoundingBox, 'p_sizez',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowMeshBoundingBox, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_ShowMeshBoundingBox, 'Scene Graph', 
                    (SCIRun_Geometry, 'Scene Graph'))

  reg.add_module(scirun_ViewGraph)
  reg.add_input_port(scirun_ViewGraph, 'Title',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_input_port(scirun_ViewGraph, 'Input',
                   (SCIRun_Matrix, "SCIRun_Matrix"))

  reg.add_module(scirun_CreateStandardColorMaps)
  reg.add_input_port(scirun_CreateStandardColorMaps, 'p_mapName',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateStandardColorMaps, 'p_gamma',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_CreateStandardColorMaps, 'p_resolution',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_CreateStandardColorMaps, 'p_reverse',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_CreateStandardColorMaps, 'p_faux',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_CreateStandardColorMaps, 'p_positionList',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateStandardColorMaps, 'p_nodeList',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateStandardColorMaps, 'p_width',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_CreateStandardColorMaps, 'p_height',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_output_port(scirun_CreateStandardColorMaps, 'ColorMap', 
                    (SCIRun_ColorMap, 'ColorMap'))

  reg.add_module(scirun_ShowTextureSlices)
  reg.add_input_port(scirun_ShowTextureSlices, 'p_control_pos_saved',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowTextureSlices, 'p_drawX',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowTextureSlices, 'p_drawY',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowTextureSlices, 'p_drawZ',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowTextureSlices, 'p_drawView',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowTextureSlices, 'p_interp_mode',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowTextureSlices, 'p_draw_phi_0',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowTextureSlices, 'p_draw_phi_1',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowTextureSlices, 'p_phi_0',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ShowTextureSlices, 'p_phi_1',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ShowTextureSlices, 'p_multi_level',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowTextureSlices, 'p_color_changed',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowTextureSlices, 'p_colors',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ShowTextureSlices, 'p_level_on',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ShowTextureSlices, 'p_outline_levels',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowTextureSlices, 'p_use_stencil',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowTextureSlices, 'Texture',
                   (SCIRun_Texture, "SCIRun_Texture"))
  reg.add_input_port(scirun_ShowTextureSlices, 'ColorMap',
                   (SCIRun_ColorMap, "SCIRun_ColorMap"))
  reg.add_input_port(scirun_ShowTextureSlices, 'ColorMap2',
                   (SCIRun_ColorMap2, "SCIRun_ColorMap2"))
  reg.add_output_port(scirun_ShowTextureSlices, 'Geometry', 
                    (SCIRun_Geometry, 'Geometry'))
  reg.add_output_port(scirun_ShowTextureSlices, 'ColorMap', 
                    (SCIRun_ColorMap, 'ColorMap'))

  reg.add_module(scirun_ShowMatrix)
  reg.add_input_port(scirun_ShowMatrix, 'p_xpos',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ShowMatrix, 'p_ypos',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ShowMatrix, 'p_xscale',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ShowMatrix, 'p_yscale',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ShowMatrix, 'p_3d_mode',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowMatrix, 'p_gmode',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowMatrix, 'p_showtext',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowMatrix, 'p_row_begin',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowMatrix, 'p_rows',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowMatrix, 'p_col_begin',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowMatrix, 'p_cols',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowMatrix, 'p_colormapmode',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ShowMatrix, 'ColorMap',
                   (SCIRun_ColorMap, "SCIRun_ColorMap"))
  reg.add_input_port(scirun_ShowMatrix, 'Matrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_ShowMatrix, 'Geometry', 
                    (SCIRun_Geometry, 'Geometry'))

  reg.add_module(scirun_GetSliceFromStructuredFieldByIndices)
  reg.add_input_port(scirun_GetSliceFromStructuredFieldByIndices, 'p_axis',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GetSliceFromStructuredFieldByIndices, 'p_dims',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GetSliceFromStructuredFieldByIndices, 'p_dim_i',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GetSliceFromStructuredFieldByIndices, 'p_dim_j',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GetSliceFromStructuredFieldByIndices, 'p_dim_k',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GetSliceFromStructuredFieldByIndices, 'p_index_i',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GetSliceFromStructuredFieldByIndices, 'p_index_j',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GetSliceFromStructuredFieldByIndices, 'p_index_k',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GetSliceFromStructuredFieldByIndices, 'p_update_type',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_GetSliceFromStructuredFieldByIndices, 'p_continuous',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_GetSliceFromStructuredFieldByIndices, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_GetSliceFromStructuredFieldByIndices, 'Input Matrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_GetSliceFromStructuredFieldByIndices, 'Output Field', 
                    (SCIRun_Field, 'Output Field'))
  reg.add_output_port(scirun_GetSliceFromStructuredFieldByIndices, 'Output Matrix', 
                    (SCIRun_Matrix, 'Output Matrix'))

  reg.add_module(scirun_ConvertMatrixType)
  reg.add_input_port(scirun_ConvertMatrixType, 'p_oldtype',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ConvertMatrixType, 'p_newtype',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ConvertMatrixType, 'p_nrow',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ConvertMatrixType, 'p_ncol',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ConvertMatrixType, 'Input',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_ConvertMatrixType, 'Output', 
                    (SCIRun_Matrix, 'Output'))

  reg.add_module(scirun_InsertColorMapsIntoBundle)
  reg.add_input_port(scirun_InsertColorMapsIntoBundle, 'p_colormap1_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertColorMapsIntoBundle, 'p_colormap2_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertColorMapsIntoBundle, 'p_colormap3_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertColorMapsIntoBundle, 'p_colormap4_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertColorMapsIntoBundle, 'p_colormap5_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertColorMapsIntoBundle, 'p_colormap6_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertColorMapsIntoBundle, 'p_replace1',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_InsertColorMapsIntoBundle, 'p_replace2',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_InsertColorMapsIntoBundle, 'p_replace3',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_InsertColorMapsIntoBundle, 'p_replace4',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_InsertColorMapsIntoBundle, 'p_replace5',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_InsertColorMapsIntoBundle, 'p_replace6',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_InsertColorMapsIntoBundle, 'p_bundlename',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_InsertColorMapsIntoBundle, 'bundle',
                   (SCIRun_Bundle, "SCIRun_Bundle"))
  reg.add_input_port(scirun_InsertColorMapsIntoBundle, 'colormap1',
                   (SCIRun_ColorMap, "SCIRun_ColorMap"))
  reg.add_input_port(scirun_InsertColorMapsIntoBundle, 'colormap2',
                   (SCIRun_ColorMap, "SCIRun_ColorMap"))
  reg.add_input_port(scirun_InsertColorMapsIntoBundle, 'colormap3',
                   (SCIRun_ColorMap, "SCIRun_ColorMap"))
  reg.add_input_port(scirun_InsertColorMapsIntoBundle, 'colormap4',
                   (SCIRun_ColorMap, "SCIRun_ColorMap"))
  reg.add_input_port(scirun_InsertColorMapsIntoBundle, 'colormap5',
                   (SCIRun_ColorMap, "SCIRun_ColorMap"))
  reg.add_input_port(scirun_InsertColorMapsIntoBundle, 'colormap6',
                   (SCIRun_ColorMap, "SCIRun_ColorMap"))
  reg.add_output_port(scirun_InsertColorMapsIntoBundle, 'bundle', 
                    (SCIRun_Bundle, 'bundle'))

  reg.add_module(scirun_JoinStrings)
  reg.add_input_port(scirun_JoinStrings, 'input',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_output_port(scirun_JoinStrings, 'Output', 
                    (core.modules.basic_modules.String, 'Output'))

  reg.add_module(scirun_CreateViewerClockIcon)
  reg.add_input_port(scirun_CreateViewerClockIcon, 'p_type',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerClockIcon, 'p_bbox',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerClockIcon, 'p_format',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerClockIcon, 'p_min',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerClockIcon, 'p_max',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerClockIcon, 'p_current',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerClockIcon, 'p_size',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerClockIcon, 'p_location_x',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerClockIcon, 'p_location_y',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerClockIcon, 'p_color_r',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerClockIcon, 'p_color_g',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerClockIcon, 'p_color_b',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_CreateViewerClockIcon, 'Time Matrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(scirun_CreateViewerClockIcon, 'Time Nrrd',
                   (SCIRun_Nrrd, "SCIRun_Nrrd"))
  reg.add_output_port(scirun_CreateViewerClockIcon, 'Clock', 
                    (SCIRun_Geometry, 'Clock'))

  reg.add_module(scirun_ReportMatrixRowMeasure)
  reg.add_input_port(scirun_ReportMatrixRowMeasure, 'p_method',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ReportMatrixRowMeasure, 'Matrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_ReportMatrixRowMeasure, 'Vector', 
                    (SCIRun_Matrix, 'Vector'))

  reg.add_module(scirun_RemoveHexVolSheet)
  reg.add_input_port(scirun_RemoveHexVolSheet, 'p_edge_list',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_RemoveHexVolSheet, 'HexField',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_RemoveHexVolSheet, 'NewHexField', 
                    (SCIRun_Field, 'NewHexField'))
  reg.add_output_port(scirun_RemoveHexVolSheet, 'ExtractedHexes', 
                    (SCIRun_Field, 'ExtractedHexes'))

  reg.add_module(scirun_ReorderMatrixByCuthillMcKee)
  reg.add_input_port(scirun_ReorderMatrixByCuthillMcKee, 'Matrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_ReorderMatrixByCuthillMcKee, 'Matrix', 
                    (SCIRun_Matrix, 'Matrix'))
  reg.add_output_port(scirun_ReorderMatrixByCuthillMcKee, 'Mapping', 
                    (SCIRun_Matrix, 'Mapping'))
  reg.add_output_port(scirun_ReorderMatrixByCuthillMcKee, 'InverseMapping', 
                    (SCIRun_Matrix, 'InverseMapping'))

  reg.add_module(scirun_ReportMatrixInfo)
  reg.add_input_port(scirun_ReportMatrixInfo, 'Input',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_ReportMatrixInfo, 'NumRows', 
                    (SCIRun_Matrix, 'NumRows'))
  reg.add_output_port(scirun_ReportMatrixInfo, 'NumCols', 
                    (SCIRun_Matrix, 'NumCols'))
  reg.add_output_port(scirun_ReportMatrixInfo, 'NumElements', 
                    (SCIRun_Matrix, 'NumElements'))

  reg.add_module(scirun_SubsampleStructuredFieldByIndices)
  reg.add_input_port(scirun_SubsampleStructuredFieldByIndices, 'p_power_app',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_SubsampleStructuredFieldByIndices, 'p_wrap',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_SubsampleStructuredFieldByIndices, 'p_dims',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_SubsampleStructuredFieldByIndices, 'p_dim_i',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_SubsampleStructuredFieldByIndices, 'p_dim_j',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_SubsampleStructuredFieldByIndices, 'p_dim_k',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_SubsampleStructuredFieldByIndices, 'p_start_i',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_SubsampleStructuredFieldByIndices, 'p_start_j',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_SubsampleStructuredFieldByIndices, 'p_start_k',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_SubsampleStructuredFieldByIndices, 'p_stop_i',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_SubsampleStructuredFieldByIndices, 'p_stop_j',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_SubsampleStructuredFieldByIndices, 'p_stop_k',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_SubsampleStructuredFieldByIndices, 'p_stride_i',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_SubsampleStructuredFieldByIndices, 'p_stride_j',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_SubsampleStructuredFieldByIndices, 'p_stride_k',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_SubsampleStructuredFieldByIndices, 'p_wrap_i',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_SubsampleStructuredFieldByIndices, 'p_wrap_j',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_SubsampleStructuredFieldByIndices, 'p_wrap_k',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_SubsampleStructuredFieldByIndices, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_SubsampleStructuredFieldByIndices, 'Input Matrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_SubsampleStructuredFieldByIndices, 'Output Field', 
                    (SCIRun_Field, 'Output Field'))
  reg.add_output_port(scirun_SubsampleStructuredFieldByIndices, 'Output Matrix', 
                    (SCIRun_Matrix, 'Output Matrix'))

  reg.add_module(scirun_CalculateDistanceToField)
  reg.add_input_port(scirun_CalculateDistanceToField, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_CalculateDistanceToField, 'ObjectField',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_CalculateDistanceToField, 'DistanceField', 
                    (SCIRun_Field, 'DistanceField'))

  reg.add_module(scirun_GetAllSegmentationBoundaries)
  reg.add_input_port(scirun_GetAllSegmentationBoundaries, 'Segmentations',
                   (SCIRun_Nrrd, "SCIRun_Nrrd"))
  reg.add_output_port(scirun_GetAllSegmentationBoundaries, 'Boundaries', 
                    (SCIRun_Field, 'Boundaries'))

  reg.add_module(scirun_ClipFieldWithSeed)
  reg.add_input_port(scirun_ClipFieldWithSeed, 'p_mode',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ClipFieldWithSeed, 'p_function',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_ClipFieldWithSeed, 'Function',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_input_port(scirun_ClipFieldWithSeed, 'Input',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_ClipFieldWithSeed, 'Seeds',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_ClipFieldWithSeed, 'Clipped', 
                    (SCIRun_Field, 'Clipped'))
  reg.add_output_port(scirun_ClipFieldWithSeed, 'Mapping', 
                    (SCIRun_Matrix, 'Mapping'))
  reg.add_output_port(scirun_ClipFieldWithSeed, 'MaskVector', 
                    (SCIRun_Nrrd, 'MaskVector'))

  reg.add_module(scirun_CreateParameterBundle)
  reg.add_input_port(scirun_CreateParameterBundle, 'p_data',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_CreateParameterBundle, 'p_new_field_count',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_CreateParameterBundle, 'p_update_all',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_output_port(scirun_CreateParameterBundle, 'ParameterList', 
                    (SCIRun_Bundle, 'ParameterList'))

  reg.add_module(scirun_CollectPointClouds)
  reg.add_input_port(scirun_CollectPointClouds, 'p_num_fields',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_CollectPointClouds, 'Point Cloud',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_CollectPointClouds, 'Curve', 
                    (SCIRun_Field, 'Curve'))

  reg.add_module(scirun_InsertEnvironmentIntoBundle)
  reg.add_output_port(scirun_InsertEnvironmentIntoBundle, 'Environment', 
                    (SCIRun_Bundle, 'Environment'))

  reg.add_module(scirun_ScaleFieldMeshAndData)
  reg.add_input_port(scirun_ScaleFieldMeshAndData, 'p_datascale',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ScaleFieldMeshAndData, 'p_geomscale',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ScaleFieldMeshAndData, 'p_usegeomcenter',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ScaleFieldMeshAndData, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_ScaleFieldMeshAndData, 'GeomScaleFactor',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(scirun_ScaleFieldMeshAndData, 'DataScaleFactor',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_ScaleFieldMeshAndData, 'Field', 
                    (SCIRun_Field, 'Field'))

  reg.add_module(scirun_ConvertFieldsToTexture)
  reg.add_input_port(scirun_ConvertFieldsToTexture, 'p_vmin',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ConvertFieldsToTexture, 'p_vmax',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ConvertFieldsToTexture, 'p_gmin',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ConvertFieldsToTexture, 'p_gmax',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ConvertFieldsToTexture, 'p_is_fixed',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ConvertFieldsToTexture, 'p_card_mem',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ConvertFieldsToTexture, 'p_card_mem_auto',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ConvertFieldsToTexture, 'p_histogram',
                   (core.modules.basic_modules.Integer, 'tip'), True)
  reg.add_input_port(scirun_ConvertFieldsToTexture, 'p_gamma',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(scirun_ConvertFieldsToTexture, 'Value Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(scirun_ConvertFieldsToTexture, 'Gradient Magnitude Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_ConvertFieldsToTexture, 'Texture', 
                    (SCIRun_Texture, 'Texture'))
  reg.add_output_port(scirun_ConvertFieldsToTexture, 'JointHistoGram', 
                    (SCIRun_Nrrd, 'JointHistoGram'))

  reg.add_module(scirun_SplitNodesByDomain)
  reg.add_input_port(scirun_SplitNodesByDomain, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(scirun_SplitNodesByDomain, 'SplitField', 
                    (SCIRun_Field, 'SplitField'))

  reg.add_module(scirun_RemoveZerosFromMatrix)
  reg.add_input_port(scirun_RemoveZerosFromMatrix, 'p_row_or_col',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(scirun_RemoveZerosFromMatrix, 'Matrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_RemoveZerosFromMatrix, 'Matrix', 
                    (SCIRun_Matrix, 'Matrix'))

  reg.add_module(scirun_GetNetworkFileName)
  reg.add_output_port(scirun_GetNetworkFileName, 'String', 
                    (core.modules.basic_modules.String, 'String'))

  reg.add_module(scirun_RemoveZeroRowsAndColumns)
  reg.add_input_port(scirun_RemoveZeroRowsAndColumns, 'Matrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(scirun_RemoveZeroRowsAndColumns, 'ReducedMatrix', 
                    (SCIRun_Matrix, 'ReducedMatrix'))
  reg.add_output_port(scirun_RemoveZeroRowsAndColumns, 'LeftMapping', 
                    (SCIRun_Matrix, 'LeftMapping'))
  reg.add_output_port(scirun_RemoveZeroRowsAndColumns, 'RightMapping', 
                    (SCIRun_Matrix, 'RightMapping'))

  reg.add_module(scirun_ColorMap2DSemantics)
  reg.add_input_port(scirun_ColorMap2DSemantics, 'Input Colormap',
                   (SCIRun_ColorMap2, "SCIRun_ColorMap2"))
  reg.add_output_port(scirun_ColorMap2DSemantics, 'Output Colormap', 
                    (SCIRun_ColorMap2, 'Output Colormap'))



  import viewercell
  viewercell.registerSelf()


def package_dependencies():
  return ['edu.utah.sci.vistrails.spreadsheet']


def finalize():
  sr_py.terminate()
  time.sleep(.5)

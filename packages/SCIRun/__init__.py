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
class SCIRun_CreateDataArray(Module) :
  def compute(self) :
    function = 'RESULT = abs(A);'
    if self.hasInputFromPort('function') :
      function = self.getInputFromPort('function')
    format = 'Scalar'
    if self.hasInputFromPort('format') :
      format = self.getInputFromPort('format')
    Size = 0
    if self.hasInputFromPort('Size') :
      Size = self.getInputFromPort('Size')
    Function = 0
    if self.hasInputFromPort('Function') :
      Function = self.getInputFromPort('Function')
    Array = 0
    if self.hasInputFromPort('Array') :
      Array = self.getInputFromPort('Array')
    results = sr_py.CreateDataArray(Size,Function,Array,function,format)
    self.setResult('DataArray', results)

class SCIRun_WriteBundle(Module) :
  def compute(self) :
    filetype = 'Binary'
    if self.hasInputFromPort('filetype') :
      filetype = self.getInputFromPort('filetype')
    confirm = 0
    if self.hasInputFromPort('confirm') :
      confirm = self.getInputFromPort('confirm')
    confirm_once = 0
    if self.hasInputFromPort('confirm_once') :
      confirm_once = self.getInputFromPort('confirm_once')
    bundle = 0
    if self.hasInputFromPort('bundle') :
      bundle = self.getInputFromPort('bundle')
    Filename = 0
    if self.hasInputFromPort('Filename') :
      Filename = self.getInputFromPort('Filename')
    results = sr_py.WriteBundle(bundle,Filename,filetype,confirm,confirm_once)

class SCIRun_JoinFields(Module) :
  def compute(self) :
    accumulating = 0
    if self.hasInputFromPort('accumulating') :
      accumulating = self.getInputFromPort('accumulating')
    tolerance = 0.0001
    if self.hasInputFromPort('tolerance') :
      tolerance = self.getInputFromPort('tolerance')
    force_nodemerge = 1
    if self.hasInputFromPort('force_nodemerge') :
      force_nodemerge = self.getInputFromPort('force_nodemerge')
    force_pointcloud = 0
    if self.hasInputFromPort('force_pointcloud') :
      force_pointcloud = self.getInputFromPort('force_pointcloud')
    matchval = 0
    if self.hasInputFromPort('matchval') :
      matchval = self.getInputFromPort('matchval')
    meshonly = 0
    if self.hasInputFromPort('meshonly') :
      meshonly = self.getInputFromPort('meshonly')
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    results = sr_py.JoinFields(Field,accumulating,tolerance,force_nodemerge,force_pointcloud,matchval,meshonly)
    self.setResult('Output Field', results)

class SCIRun_MaskLatVolWithTriSurf(Module) :
  def compute(self) :
    LatVolField = 0
    if self.hasInputFromPort('LatVolField') :
      LatVolField = self.getInputFromPort('LatVolField')
    TriSurfField = 0
    if self.hasInputFromPort('TriSurfField') :
      TriSurfField = self.getInputFromPort('TriSurfField')
    results = sr_py.MaskLatVolWithTriSurf(LatVolField,TriSurfField)
    self.setResult('LatVol Mask', results)

class SCIRun_ApplyMappingMatrix(Module) :
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

class SCIRun_TransformPlanarMesh(Module) :
  def compute(self) :
    axis = 2
    if self.hasInputFromPort('axis') :
      axis = self.getInputFromPort('axis')
    invert = 0
    if self.hasInputFromPort('invert') :
      invert = self.getInputFromPort('invert')
    trans_x = 0
    if self.hasInputFromPort('trans_x') :
      trans_x = self.getInputFromPort('trans_x')
    trans_y = 0
    if self.hasInputFromPort('trans_y') :
      trans_y = self.getInputFromPort('trans_y')
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    Index_Matrix = 0
    if self.hasInputFromPort('Index Matrix') :
      Index_Matrix = self.getInputFromPort('Index Matrix')
    results = sr_py.TransformPlanarMesh(Input_Field,Index_Matrix,axis,invert,trans_x,trans_y)
    self.setResult('Transformed Field', results)

class SCIRun_ViewScene(Module) :
  def compute(self) :
    Geometry = 0
    if self.hasInputFromPort('Geometry') :
      Geometry = self.getInputFromPort('Geometry')
    results = sr_py.ViewScene(Geometry)

class SCIRun_RefineMeshByIsovalue(Module) :
  def compute(self) :
    isoval = 0.0
    if self.hasInputFromPort('isoval') :
      isoval = self.getInputFromPort('isoval')
    lte = 1
    if self.hasInputFromPort('lte') :
      lte = self.getInputFromPort('lte')
    Input = 0
    if self.hasInputFromPort('Input') :
      Input = self.getInputFromPort('Input')
    Optional_Isovalue = 0
    if self.hasInputFromPort('Optional Isovalue') :
      Optional_Isovalue = self.getInputFromPort('Optional Isovalue')
    results = sr_py.RefineMeshByIsovalue(Input,Optional_Isovalue,isoval,lte)
    self.setResult('Refined', sr_py.read_at_index(results,0))
    self.setResult('Mapping', sr_py.read_at_index(results,1))

class SCIRun_AppendMatrix(Module) :
  def compute(self) :
    row_or_column = 'row'
    if self.hasInputFromPort('row_or_column') :
      row_or_column = self.getInputFromPort('row_or_column')
    BaseMatrix = 0
    if self.hasInputFromPort('BaseMatrix') :
      BaseMatrix = self.getInputFromPort('BaseMatrix')
    AppendMatrix = 0
    if self.hasInputFromPort('AppendMatrix') :
      AppendMatrix = self.getInputFromPort('AppendMatrix')
    results = sr_py.AppendMatrix(BaseMatrix,AppendMatrix,row_or_column)
    self.setResult('Matrix', results)

class SCIRun_ReportColumnMatrixMisfit(Module) :
  def compute(self) :
    have_ui = 0
    if self.hasInputFromPort('have_ui') :
      have_ui = self.getInputFromPort('have_ui')
    methodTCL = 'CCinv'
    if self.hasInputFromPort('methodTCL') :
      methodTCL = self.getInputFromPort('methodTCL')
    pTCL = 2
    if self.hasInputFromPort('pTCL') :
      pTCL = self.getInputFromPort('pTCL')
    Vec1 = 0
    if self.hasInputFromPort('Vec1') :
      Vec1 = self.getInputFromPort('Vec1')
    Vec2 = 0
    if self.hasInputFromPort('Vec2') :
      Vec2 = self.getInputFromPort('Vec2')
    results = sr_py.ReportColumnMatrixMisfit(Vec1,Vec2,have_ui,methodTCL,pTCL)
    self.setResult('Error Out', results)

class SCIRun_EvaluateLinAlgGeneral(Module) :
  def compute(self) :
    function = 'o1 = i1 * 12;'
    if self.hasInputFromPort('function') :
      function = self.getInputFromPort('function')
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
    results = sr_py.EvaluateLinAlgGeneral(i1,i2,i3,i4,i5,function)
    self.setResult('o1', sr_py.read_at_index(results,0))
    self.setResult('o2', sr_py.read_at_index(results,1))
    self.setResult('o3', sr_py.read_at_index(results,2))
    self.setResult('o4', sr_py.read_at_index(results,3))
    self.setResult('o5', sr_py.read_at_index(results,4))

class SCIRun_ReportMeshQualityMeasures(Module) :
  def compute(self) :
    Input = 0
    if self.hasInputFromPort('Input') :
      Input = self.getInputFromPort('Input')
    results = sr_py.ReportMeshQualityMeasures(Input)
    self.setResult('Checked', results)

class SCIRun_ApplyFilterToFieldData(Module) :
  def compute(self) :
    method = 'erode/dilate'
    if self.hasInputFromPort('method') :
      method = self.getInputFromPort('method')
    ed_method = 'erode'
    if self.hasInputFromPort('ed_method') :
      ed_method = self.getInputFromPort('ed_method')
    ed_iterations = 3
    if self.hasInputFromPort('ed_iterations') :
      ed_iterations = self.getInputFromPort('ed_iterations')
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    results = sr_py.ApplyFilterToFieldData(Field,method,ed_method,ed_iterations)
    self.setResult('Field', results)

class SCIRun_FairMesh(Module) :
  def compute(self) :
    iterations = 50
    if self.hasInputFromPort('iterations') :
      iterations = self.getInputFromPort('iterations')
    method = 'fast'
    if self.hasInputFromPort('method') :
      method = self.getInputFromPort('method')
    Input_Mesh = 0
    if self.hasInputFromPort('Input Mesh') :
      Input_Mesh = self.getInputFromPort('Input Mesh')
    results = sr_py.FairMesh(Input_Mesh,iterations,method)
    self.setResult('Faired Mesh', results)

class SCIRun_EvaluateLinAlgBinary(Module) :
  def compute(self) :
    op = 'Mult'
    if self.hasInputFromPort('op') :
      op = self.getInputFromPort('op')
    function = 'x+y'
    if self.hasInputFromPort('function') :
      function = self.getInputFromPort('function')
    A = 0
    if self.hasInputFromPort('A') :
      A = self.getInputFromPort('A')
    B = 0
    if self.hasInputFromPort('B') :
      B = self.getInputFromPort('B')
    results = sr_py.EvaluateLinAlgBinary(A,B,op,function)
    self.setResult('Output', results)

class SCIRun_PrintMatrixIntoString(Module) :
  def compute(self) :
    formatstring = 'time: %5.4f ms'
    if self.hasInputFromPort('formatstring') :
      formatstring = self.getInputFromPort('formatstring')
    Format = 0
    if self.hasInputFromPort('Format') :
      Format = self.getInputFromPort('Format')
    Input = 0
    if self.hasInputFromPort('Input') :
      Input = self.getInputFromPort('Input')
    results = sr_py.PrintMatrixIntoString(Format,Input,formatstring)
    self.setResult('Output', results)

class SCIRun_SetFieldProperty(Module) :
  def compute(self) :
    num_entries = 0
    if self.hasInputFromPort('num_entries') :
      num_entries = self.getInputFromPort('num_entries')
    property = ''
    if self.hasInputFromPort('property') :
      property = self.getInputFromPort('property')
    type = 'unknown'
    if self.hasInputFromPort('type') :
      type = self.getInputFromPort('type')
    value = ''
    if self.hasInputFromPort('value') :
      value = self.getInputFromPort('value')
    readonly = 0
    if self.hasInputFromPort('readonly') :
      readonly = self.getInputFromPort('readonly')
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    results = sr_py.SetFieldProperty(Field,num_entries,property,type,value,readonly)
    self.setResult('Field', results)

class SCIRun_ConvertFieldBasis(Module) :
  def compute(self) :
    output_basis = 'Linear'
    if self.hasInputFromPort('output_basis') :
      output_basis = self.getInputFromPort('output_basis')
    Input = 0
    if self.hasInputFromPort('Input') :
      Input = self.getInputFromPort('Input')
    results = sr_py.ConvertFieldBasis(Input,output_basis)
    self.setResult('Output', sr_py.read_at_index(results,0))
    self.setResult('Mapping', sr_py.read_at_index(results,1))

class SCIRun_CreateDataArrayFromIndices(Module) :
  def compute(self) :
    Indices = 0
    if self.hasInputFromPort('Indices') :
      Indices = self.getInputFromPort('Indices')
    Template = 0
    if self.hasInputFromPort('Template') :
      Template = self.getInputFromPort('Template')
    results = sr_py.CreateDataArrayFromIndices(Indices,Template)
    self.setResult('DataArray', results)

class SCIRun_SelectAndSetFieldData(Module) :
  def compute(self) :
    selection1 = 'DATA < A'
    if self.hasInputFromPort('selection1') :
      selection1 = self.getInputFromPort('selection1')
    function1 = 'abs(DATA)'
    if self.hasInputFromPort('function1') :
      function1 = self.getInputFromPort('function1')
    selection2 = 'DATA > A'
    if self.hasInputFromPort('selection2') :
      selection2 = self.getInputFromPort('selection2')
    function2 = '-abs(DATA)'
    if self.hasInputFromPort('function2') :
      function2 = self.getInputFromPort('function2')
    selection3 = ''
    if self.hasInputFromPort('selection3') :
      selection3 = self.getInputFromPort('selection3')
    function3 = ''
    if self.hasInputFromPort('function3') :
      function3 = self.getInputFromPort('function3')
    selection4 = ''
    if self.hasInputFromPort('selection4') :
      selection4 = self.getInputFromPort('selection4')
    function4 = ''
    if self.hasInputFromPort('function4') :
      function4 = self.getInputFromPort('function4')
    functiondef = 0
    if self.hasInputFromPort('functiondef') :
      functiondef = self.getInputFromPort('functiondef')
    format = 'Scalar'
    if self.hasInputFromPort('format') :
      format = self.getInputFromPort('format')
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    Array = 0
    if self.hasInputFromPort('Array') :
      Array = self.getInputFromPort('Array')
    results = sr_py.SelectAndSetFieldData(Field,Array,selection1,function1,selection2,function2,selection3,function3,selection4,function4,functiondef,format)
    self.setResult('Field', results)

class SCIRun_GetColorMapsFromBundle(Module) :
  def compute(self) :
    colormap1_name = 'colormap1'
    if self.hasInputFromPort('colormap1_name') :
      colormap1_name = self.getInputFromPort('colormap1_name')
    colormap2_name = 'colormap2'
    if self.hasInputFromPort('colormap2_name') :
      colormap2_name = self.getInputFromPort('colormap2_name')
    colormap3_name = 'colormap3'
    if self.hasInputFromPort('colormap3_name') :
      colormap3_name = self.getInputFromPort('colormap3_name')
    colormap4_name = 'colormap4'
    if self.hasInputFromPort('colormap4_name') :
      colormap4_name = self.getInputFromPort('colormap4_name')
    colormap5_name = 'colormap5'
    if self.hasInputFromPort('colormap5_name') :
      colormap5_name = self.getInputFromPort('colormap5_name')
    colormap6_name = 'colormap6'
    if self.hasInputFromPort('colormap6_name') :
      colormap6_name = self.getInputFromPort('colormap6_name')
    colormap_selection = ''
    if self.hasInputFromPort('colormap_selection') :
      colormap_selection = self.getInputFromPort('colormap_selection')
    bundle = 0
    if self.hasInputFromPort('bundle') :
      bundle = self.getInputFromPort('bundle')
    results = sr_py.GetColorMapsFromBundle(bundle,colormap1_name,colormap2_name,colormap3_name,colormap4_name,colormap5_name,colormap6_name,colormap_selection)
    self.setResult('bundle', sr_py.read_at_index(results,0))
    self.setResult('colormap1', sr_py.read_at_index(results,1))
    self.setResult('colormap2', sr_py.read_at_index(results,2))
    self.setResult('colormap3', sr_py.read_at_index(results,3))
    self.setResult('colormap4', sr_py.read_at_index(results,4))
    self.setResult('colormap5', sr_py.read_at_index(results,5))
    self.setResult('colormap6', sr_py.read_at_index(results,6))

class SCIRun_CreateStructHex(Module) :
  def compute(self) :
    sizex = 16
    if self.hasInputFromPort('sizex') :
      sizex = self.getInputFromPort('sizex')
    sizey = 16
    if self.hasInputFromPort('sizey') :
      sizey = self.getInputFromPort('sizey')
    sizez = 16
    if self.hasInputFromPort('sizez') :
      sizez = self.getInputFromPort('sizez')
    padpercent = 0.0
    if self.hasInputFromPort('padpercent') :
      padpercent = self.getInputFromPort('padpercent')
    data_at = 'Nodes'
    if self.hasInputFromPort('data_at') :
      data_at = self.getInputFromPort('data_at')
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    results = sr_py.CreateStructHex(Input_Field,sizex,sizey,sizez,padpercent,data_at)
    self.setResult('Output Sample Field', results)

class SCIRun_ShowColorMap(Module) :
  def compute(self) :
    length = 'half2'
    if self.hasInputFromPort('length') :
      length = self.getInputFromPort('length')
    side = 'left'
    if self.hasInputFromPort('side') :
      side = self.getInputFromPort('side')
    numlabels = 5
    if self.hasInputFromPort('numlabels') :
      numlabels = self.getInputFromPort('numlabels')
    scale = 1.0
    if self.hasInputFromPort('scale') :
      scale = self.getInputFromPort('scale')
    numsigdigits = 2
    if self.hasInputFromPort('numsigdigits') :
      numsigdigits = self.getInputFromPort('numsigdigits')
    units = ''
    if self.hasInputFromPort('units') :
      units = self.getInputFromPort('units')
    color_r = 1.0
    if self.hasInputFromPort('color_r') :
      color_r = self.getInputFromPort('color_r')
    color_g = 1.0
    if self.hasInputFromPort('color_g') :
      color_g = self.getInputFromPort('color_g')
    color_b = 1.0
    if self.hasInputFromPort('color_b') :
      color_b = self.getInputFromPort('color_b')
    text_fontsize = 2
    if self.hasInputFromPort('text_fontsize') :
      text_fontsize = self.getInputFromPort('text_fontsize')
    extra_padding = 0
    if self.hasInputFromPort('extra_padding') :
      extra_padding = self.getInputFromPort('extra_padding')
    ColorMap = 0
    if self.hasInputFromPort('ColorMap') :
      ColorMap = self.getInputFromPort('ColorMap')
    results = sr_py.ShowColorMap(ColorMap,length,side,numlabels,scale,numsigdigits,units,color_r,color_g,color_b,text_fontsize,extra_padding)
    self.setResult('Geometry', results)

class SCIRun_CalculateFieldData3(Module) :
  def compute(self) :
    function = 'RESULT = abs(DATA1);'
    if self.hasInputFromPort('function') :
      function = self.getInputFromPort('function')
    format = 'Scalar'
    if self.hasInputFromPort('format') :
      format = self.getInputFromPort('format')
    Field1 = 0
    if self.hasInputFromPort('Field1') :
      Field1 = self.getInputFromPort('Field1')
    Field2 = 0
    if self.hasInputFromPort('Field2') :
      Field2 = self.getInputFromPort('Field2')
    Field3 = 0
    if self.hasInputFromPort('Field3') :
      Field3 = self.getInputFromPort('Field3')
    Function = 0
    if self.hasInputFromPort('Function') :
      Function = self.getInputFromPort('Function')
    Array = 0
    if self.hasInputFromPort('Array') :
      Array = self.getInputFromPort('Array')
    results = sr_py.CalculateFieldData3(Field1,Field2,Field3,Function,Array,function,format)
    self.setResult('Field', results)

class SCIRun_InsertFieldsIntoBundle(Module) :
  def compute(self) :
    field1_name = 'field1'
    if self.hasInputFromPort('field1_name') :
      field1_name = self.getInputFromPort('field1_name')
    field2_name = 'field2'
    if self.hasInputFromPort('field2_name') :
      field2_name = self.getInputFromPort('field2_name')
    field3_name = 'field3'
    if self.hasInputFromPort('field3_name') :
      field3_name = self.getInputFromPort('field3_name')
    field4_name = 'field4'
    if self.hasInputFromPort('field4_name') :
      field4_name = self.getInputFromPort('field4_name')
    field5_name = 'field5'
    if self.hasInputFromPort('field5_name') :
      field5_name = self.getInputFromPort('field5_name')
    field6_name = 'field6'
    if self.hasInputFromPort('field6_name') :
      field6_name = self.getInputFromPort('field6_name')
    replace1 = 1
    if self.hasInputFromPort('replace1') :
      replace1 = self.getInputFromPort('replace1')
    replace2 = 1
    if self.hasInputFromPort('replace2') :
      replace2 = self.getInputFromPort('replace2')
    replace3 = 1
    if self.hasInputFromPort('replace3') :
      replace3 = self.getInputFromPort('replace3')
    replace4 = 1
    if self.hasInputFromPort('replace4') :
      replace4 = self.getInputFromPort('replace4')
    replace5 = 1
    if self.hasInputFromPort('replace5') :
      replace5 = self.getInputFromPort('replace5')
    replace6 = 1
    if self.hasInputFromPort('replace6') :
      replace6 = self.getInputFromPort('replace6')
    bundlename = ''
    if self.hasInputFromPort('bundlename') :
      bundlename = self.getInputFromPort('bundlename')
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
    results = sr_py.InsertFieldsIntoBundle(bundle,field1,field2,field3,field4,field5,field6,field1_name,field2_name,field3_name,field4_name,field5_name,field6_name,replace1,replace2,replace3,replace4,replace5,replace6,bundlename)
    self.setResult('bundle', results)

class SCIRun_CreateAndEditColorMap2D(Module) :
  def compute(self) :
    panx = 0.0
    if self.hasInputFromPort('panx') :
      panx = self.getInputFromPort('panx')
    pany = 0.0
    if self.hasInputFromPort('pany') :
      pany = self.getInputFromPort('pany')
    scale_factor = 1.0
    if self.hasInputFromPort('scale_factor') :
      scale_factor = self.getInputFromPort('scale_factor')
    histo = 0.5
    if self.hasInputFromPort('histo') :
      histo = self.getInputFromPort('histo')
    selected_widget = 1
    if self.hasInputFromPort('selected_widget') :
      selected_widget = self.getInputFromPort('selected_widget')
    selected_object = -1
    if self.hasInputFromPort('selected_object') :
      selected_object = self.getInputFromPort('selected_object')
    num_entries = 2
    if self.hasInputFromPort('num_entries') :
      num_entries = self.getInputFromPort('num_entries')
    faux = 0
    if self.hasInputFromPort('faux') :
      faux = self.getInputFromPort('faux')
    name_0 = 'Rectangle'
    if self.hasInputFromPort('name_0') :
      name_0 = self.getInputFromPort('name_0')
    a0_color_r = 0.12009425537
    if self.hasInputFromPort('a0_color_r') :
      a0_color_r = self.getInputFromPort('a0_color_r')
    a0_color_g = 0.122522867934
    if self.hasInputFromPort('a0_color_g') :
      a0_color_g = self.getInputFromPort('a0_color_g')
    a0_color_b = 0.859472894936
    if self.hasInputFromPort('a0_color_b') :
      a0_color_b = self.getInputFromPort('a0_color_b')
    a0_color_a = 0.800000011921
    if self.hasInputFromPort('a0_color_a') :
      a0_color_a = self.getInputFromPort('a0_color_a')
    state_0 = 'r 0 0.478865 0.73946 0.340307 0.218051 0.584851'
    if self.hasInputFromPort('state_0') :
      state_0 = self.getInputFromPort('state_0')
    shadeType_0 = 0
    if self.hasInputFromPort('shadeType_0') :
      shadeType_0 = self.getInputFromPort('shadeType_0')
    on_0 = 1
    if self.hasInputFromPort('on_0') :
      on_0 = self.getInputFromPort('on_0')
    name_1 = 'Rectangle'
    if self.hasInputFromPort('name_1') :
      name_1 = self.getInputFromPort('name_1')
    a1_color_r = 0.381380394093
    if self.hasInputFromPort('a1_color_r') :
      a1_color_r = self.getInputFromPort('a1_color_r')
    a1_color_g = 0.0419620992568
    if self.hasInputFromPort('a1_color_g') :
      a1_color_g = self.getInputFromPort('a1_color_g')
    a1_color_b = 0.605304105914
    if self.hasInputFromPort('a1_color_b') :
      a1_color_b = self.getInputFromPort('a1_color_b')
    a1_color_a = 0.800000011921
    if self.hasInputFromPort('a1_color_a') :
      a1_color_a = self.getInputFromPort('a1_color_a')
    state_1 = 'r 0 0.510807 0.737528 0.452638 0.226319 0.461235'
    if self.hasInputFromPort('state_1') :
      state_1 = self.getInputFromPort('state_1')
    shadeType_1 = 0
    if self.hasInputFromPort('shadeType_1') :
      shadeType_1 = self.getInputFromPort('shadeType_1')
    on_1 = 1
    if self.hasInputFromPort('on_1') :
      on_1 = self.getInputFromPort('on_1')
    marker = 'end'
    if self.hasInputFromPort('marker') :
      marker = self.getInputFromPort('marker')
    Input_Colormap = 0
    if self.hasInputFromPort('Input Colormap') :
      Input_Colormap = self.getInputFromPort('Input Colormap')
    Histogram = 0
    if self.hasInputFromPort('Histogram') :
      Histogram = self.getInputFromPort('Histogram')
    Colormap = 0
    if self.hasInputFromPort('Colormap') :
      Colormap = self.getInputFromPort('Colormap')
    results = sr_py.CreateAndEditColorMap2D(Input_Colormap,Histogram,Colormap,panx,pany,scale_factor,histo,selected_widget,selected_object,num_entries,faux,name_0,a0_color_r,a0_color_g,a0_color_b,a0_color_a,state_0,shadeType_0,on_0,name_1,a1_color_r,a1_color_g,a1_color_b,a1_color_a,state_1,shadeType_1,on_1,marker)
    self.setResult('Output Colormap', results)

class SCIRun_ReportScalarFieldStats(Module) :
  def compute(self) :
    min = '?'
    if self.hasInputFromPort('min') :
      min = self.getInputFromPort('min')
    max = '?'
    if self.hasInputFromPort('max') :
      max = self.getInputFromPort('max')
    mean = '?'
    if self.hasInputFromPort('mean') :
      mean = self.getInputFromPort('mean')
    median = '?'
    if self.hasInputFromPort('median') :
      median = self.getInputFromPort('median')
    sigma = '?'
    if self.hasInputFromPort('sigma') :
      sigma = self.getInputFromPort('sigma')
    is_fixed = 0
    if self.hasInputFromPort('is_fixed') :
      is_fixed = self.getInputFromPort('is_fixed')
    nbuckets = 256
    if self.hasInputFromPort('nbuckets') :
      nbuckets = self.getInputFromPort('nbuckets')
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    results = sr_py.ReportScalarFieldStats(Input_Field,min,max,mean,median,sigma,is_fixed,nbuckets)

class SCIRun_ReportDataArrayInfo(Module) :
  def compute(self) :
    DataArray = 0
    if self.hasInputFromPort('DataArray') :
      DataArray = self.getInputFromPort('DataArray')
    results = sr_py.ReportDataArrayInfo(DataArray)
    self.setResult('NumElements', results)

class SCIRun_GetFieldsFromBundle(Module) :
  def compute(self) :
    field1_name = 'field1'
    if self.hasInputFromPort('field1_name') :
      field1_name = self.getInputFromPort('field1_name')
    field2_name = 'field2'
    if self.hasInputFromPort('field2_name') :
      field2_name = self.getInputFromPort('field2_name')
    field3_name = 'field3'
    if self.hasInputFromPort('field3_name') :
      field3_name = self.getInputFromPort('field3_name')
    field4_name = 'field4'
    if self.hasInputFromPort('field4_name') :
      field4_name = self.getInputFromPort('field4_name')
    field5_name = 'field5'
    if self.hasInputFromPort('field5_name') :
      field5_name = self.getInputFromPort('field5_name')
    field6_name = 'field6'
    if self.hasInputFromPort('field6_name') :
      field6_name = self.getInputFromPort('field6_name')
    field_selection = ''
    if self.hasInputFromPort('field_selection') :
      field_selection = self.getInputFromPort('field_selection')
    bundle = 0
    if self.hasInputFromPort('bundle') :
      bundle = self.getInputFromPort('bundle')
    results = sr_py.GetFieldsFromBundle(bundle,field1_name,field2_name,field3_name,field4_name,field5_name,field6_name,field_selection)
    self.setResult('bundle', sr_py.read_at_index(results,0))
    self.setResult('field1', sr_py.read_at_index(results,1))
    self.setResult('field2', sr_py.read_at_index(results,2))
    self.setResult('field3', sr_py.read_at_index(results,3))
    self.setResult('field4', sr_py.read_at_index(results,4))
    self.setResult('field5', sr_py.read_at_index(results,5))
    self.setResult('field6', sr_py.read_at_index(results,6))

class SCIRun_ConvertMaskVectorToMappingMatrix(Module) :
  def compute(self) :
    MaskVector = 0
    if self.hasInputFromPort('MaskVector') :
      MaskVector = self.getInputFromPort('MaskVector')
    results = sr_py.ConvertMaskVectorToMappingMatrix(MaskVector)
    self.setResult('MappingMatrix', results)

class SCIRun_CreateViewerAxes(Module) :
  def compute(self) :
    precision = 3
    if self.hasInputFromPort('precision') :
      precision = self.getInputFromPort('precision')
    squash = 0.7
    if self.hasInputFromPort('squash') :
      squash = self.getInputFromPort('squash')
    valuerez = 72
    if self.hasInputFromPort('valuerez') :
      valuerez = self.getInputFromPort('valuerez')
    labelrez = 72
    if self.hasInputFromPort('labelrez') :
      labelrez = self.getInputFromPort('labelrez')
    Plane_01_0_Axis_absolute = ''
    if self.hasInputFromPort('Plane_01_0_Axis_absolute') :
      Plane_01_0_Axis_absolute = self.getInputFromPort('Plane_01_0_Axis_absolute')
    Plane_01_0_Axis_divisions = 10
    if self.hasInputFromPort('Plane_01_0_Axis_divisions') :
      Plane_01_0_Axis_divisions = self.getInputFromPort('Plane_01_0_Axis_divisions')
    Plane_01_0_Axis_offset = 1
    if self.hasInputFromPort('Plane_01_0_Axis_offset') :
      Plane_01_0_Axis_offset = self.getInputFromPort('Plane_01_0_Axis_offset')
    Plane_01_0_Axis_range_first = 0.0
    if self.hasInputFromPort('Plane_01_0_Axis_range_first') :
      Plane_01_0_Axis_range_first = self.getInputFromPort('Plane_01_0_Axis_range_first')
    Plane_01_0_Axis_range_second = 1.0
    if self.hasInputFromPort('Plane_01_0_Axis_range_second') :
      Plane_01_0_Axis_range_second = self.getInputFromPort('Plane_01_0_Axis_range_second')
    Plane_01_0_Axis_min_absolute = 0.0
    if self.hasInputFromPort('Plane_01_0_Axis_min_absolute') :
      Plane_01_0_Axis_min_absolute = self.getInputFromPort('Plane_01_0_Axis_min_absolute')
    Plane_01_0_Axis_max_absolute = 1.0
    if self.hasInputFromPort('Plane_01_0_Axis_max_absolute') :
      Plane_01_0_Axis_max_absolute = self.getInputFromPort('Plane_01_0_Axis_max_absolute')
    Plane_01_0_Axis_minplane = 2
    if self.hasInputFromPort('Plane_01_0_Axis_minplane') :
      Plane_01_0_Axis_minplane = self.getInputFromPort('Plane_01_0_Axis_minplane')
    Plane_01_0_Axis_maxplane = 2
    if self.hasInputFromPort('Plane_01_0_Axis_maxplane') :
      Plane_01_0_Axis_maxplane = self.getInputFromPort('Plane_01_0_Axis_maxplane')
    Plane_01_0_Axis_lines = 2
    if self.hasInputFromPort('Plane_01_0_Axis_lines') :
      Plane_01_0_Axis_lines = self.getInputFromPort('Plane_01_0_Axis_lines')
    Plane_01_0_Axis_minticks = 2
    if self.hasInputFromPort('Plane_01_0_Axis_minticks') :
      Plane_01_0_Axis_minticks = self.getInputFromPort('Plane_01_0_Axis_minticks')
    Plane_01_0_Axis_maxticks = 2
    if self.hasInputFromPort('Plane_01_0_Axis_maxticks') :
      Plane_01_0_Axis_maxticks = self.getInputFromPort('Plane_01_0_Axis_maxticks')
    Plane_01_0_Axis_minlabel = 2
    if self.hasInputFromPort('Plane_01_0_Axis_minlabel') :
      Plane_01_0_Axis_minlabel = self.getInputFromPort('Plane_01_0_Axis_minlabel')
    Plane_01_0_Axis_maxlabel = 2
    if self.hasInputFromPort('Plane_01_0_Axis_maxlabel') :
      Plane_01_0_Axis_maxlabel = self.getInputFromPort('Plane_01_0_Axis_maxlabel')
    Plane_01_0_Axis_minvalue = 2
    if self.hasInputFromPort('Plane_01_0_Axis_minvalue') :
      Plane_01_0_Axis_minvalue = self.getInputFromPort('Plane_01_0_Axis_minvalue')
    Plane_01_0_Axis_maxvalue = 2
    if self.hasInputFromPort('Plane_01_0_Axis_maxvalue') :
      Plane_01_0_Axis_maxvalue = self.getInputFromPort('Plane_01_0_Axis_maxvalue')
    Plane_01_0_Axis_width = 1
    if self.hasInputFromPort('Plane_01_0_Axis_width') :
      Plane_01_0_Axis_width = self.getInputFromPort('Plane_01_0_Axis_width')
    Plane_01_0_Axis_tickangle = 0
    if self.hasInputFromPort('Plane_01_0_Axis_tickangle') :
      Plane_01_0_Axis_tickangle = self.getInputFromPort('Plane_01_0_Axis_tickangle')
    Plane_01_0_Axis_ticktilt = 0
    if self.hasInputFromPort('Plane_01_0_Axis_ticktilt') :
      Plane_01_0_Axis_ticktilt = self.getInputFromPort('Plane_01_0_Axis_ticktilt')
    Plane_01_0_Axis_ticksize = 5
    if self.hasInputFromPort('Plane_01_0_Axis_ticksize') :
      Plane_01_0_Axis_ticksize = self.getInputFromPort('Plane_01_0_Axis_ticksize')
    Plane_01_0_Axis_labelangle = 0
    if self.hasInputFromPort('Plane_01_0_Axis_labelangle') :
      Plane_01_0_Axis_labelangle = self.getInputFromPort('Plane_01_0_Axis_labelangle')
    Plane_01_0_Axis_labelheight = 6
    if self.hasInputFromPort('Plane_01_0_Axis_labelheight') :
      Plane_01_0_Axis_labelheight = self.getInputFromPort('Plane_01_0_Axis_labelheight')
    Plane_01_0_Axis_valuesize = 3
    if self.hasInputFromPort('Plane_01_0_Axis_valuesize') :
      Plane_01_0_Axis_valuesize = self.getInputFromPort('Plane_01_0_Axis_valuesize')
    Plane_01_0_Axis_valuesquash = 1.0
    if self.hasInputFromPort('Plane_01_0_Axis_valuesquash') :
      Plane_01_0_Axis_valuesquash = self.getInputFromPort('Plane_01_0_Axis_valuesquash')
    Plane_01_1_Axis_absolute = ''
    if self.hasInputFromPort('Plane_01_1_Axis_absolute') :
      Plane_01_1_Axis_absolute = self.getInputFromPort('Plane_01_1_Axis_absolute')
    Plane_01_1_Axis_divisions = 10
    if self.hasInputFromPort('Plane_01_1_Axis_divisions') :
      Plane_01_1_Axis_divisions = self.getInputFromPort('Plane_01_1_Axis_divisions')
    Plane_01_1_Axis_offset = 1
    if self.hasInputFromPort('Plane_01_1_Axis_offset') :
      Plane_01_1_Axis_offset = self.getInputFromPort('Plane_01_1_Axis_offset')
    Plane_01_1_Axis_range_first = 0.0
    if self.hasInputFromPort('Plane_01_1_Axis_range_first') :
      Plane_01_1_Axis_range_first = self.getInputFromPort('Plane_01_1_Axis_range_first')
    Plane_01_1_Axis_range_second = 1.0
    if self.hasInputFromPort('Plane_01_1_Axis_range_second') :
      Plane_01_1_Axis_range_second = self.getInputFromPort('Plane_01_1_Axis_range_second')
    Plane_01_1_Axis_min_absolute = 0.0
    if self.hasInputFromPort('Plane_01_1_Axis_min_absolute') :
      Plane_01_1_Axis_min_absolute = self.getInputFromPort('Plane_01_1_Axis_min_absolute')
    Plane_01_1_Axis_max_absolute = 1.0
    if self.hasInputFromPort('Plane_01_1_Axis_max_absolute') :
      Plane_01_1_Axis_max_absolute = self.getInputFromPort('Plane_01_1_Axis_max_absolute')
    Plane_01_1_Axis_minplane = 2
    if self.hasInputFromPort('Plane_01_1_Axis_minplane') :
      Plane_01_1_Axis_minplane = self.getInputFromPort('Plane_01_1_Axis_minplane')
    Plane_01_1_Axis_maxplane = 2
    if self.hasInputFromPort('Plane_01_1_Axis_maxplane') :
      Plane_01_1_Axis_maxplane = self.getInputFromPort('Plane_01_1_Axis_maxplane')
    Plane_01_1_Axis_lines = 2
    if self.hasInputFromPort('Plane_01_1_Axis_lines') :
      Plane_01_1_Axis_lines = self.getInputFromPort('Plane_01_1_Axis_lines')
    Plane_01_1_Axis_minticks = 2
    if self.hasInputFromPort('Plane_01_1_Axis_minticks') :
      Plane_01_1_Axis_minticks = self.getInputFromPort('Plane_01_1_Axis_minticks')
    Plane_01_1_Axis_maxticks = 2
    if self.hasInputFromPort('Plane_01_1_Axis_maxticks') :
      Plane_01_1_Axis_maxticks = self.getInputFromPort('Plane_01_1_Axis_maxticks')
    Plane_01_1_Axis_minlabel = 2
    if self.hasInputFromPort('Plane_01_1_Axis_minlabel') :
      Plane_01_1_Axis_minlabel = self.getInputFromPort('Plane_01_1_Axis_minlabel')
    Plane_01_1_Axis_maxlabel = 2
    if self.hasInputFromPort('Plane_01_1_Axis_maxlabel') :
      Plane_01_1_Axis_maxlabel = self.getInputFromPort('Plane_01_1_Axis_maxlabel')
    Plane_01_1_Axis_minvalue = 2
    if self.hasInputFromPort('Plane_01_1_Axis_minvalue') :
      Plane_01_1_Axis_minvalue = self.getInputFromPort('Plane_01_1_Axis_minvalue')
    Plane_01_1_Axis_maxvalue = 2
    if self.hasInputFromPort('Plane_01_1_Axis_maxvalue') :
      Plane_01_1_Axis_maxvalue = self.getInputFromPort('Plane_01_1_Axis_maxvalue')
    Plane_01_1_Axis_width = 1
    if self.hasInputFromPort('Plane_01_1_Axis_width') :
      Plane_01_1_Axis_width = self.getInputFromPort('Plane_01_1_Axis_width')
    Plane_01_1_Axis_tickangle = 0
    if self.hasInputFromPort('Plane_01_1_Axis_tickangle') :
      Plane_01_1_Axis_tickangle = self.getInputFromPort('Plane_01_1_Axis_tickangle')
    Plane_01_1_Axis_ticktilt = 0
    if self.hasInputFromPort('Plane_01_1_Axis_ticktilt') :
      Plane_01_1_Axis_ticktilt = self.getInputFromPort('Plane_01_1_Axis_ticktilt')
    Plane_01_1_Axis_ticksize = 5
    if self.hasInputFromPort('Plane_01_1_Axis_ticksize') :
      Plane_01_1_Axis_ticksize = self.getInputFromPort('Plane_01_1_Axis_ticksize')
    Plane_01_1_Axis_labelangle = 0
    if self.hasInputFromPort('Plane_01_1_Axis_labelangle') :
      Plane_01_1_Axis_labelangle = self.getInputFromPort('Plane_01_1_Axis_labelangle')
    Plane_01_1_Axis_labelheight = 6
    if self.hasInputFromPort('Plane_01_1_Axis_labelheight') :
      Plane_01_1_Axis_labelheight = self.getInputFromPort('Plane_01_1_Axis_labelheight')
    Plane_01_1_Axis_valuesize = 3
    if self.hasInputFromPort('Plane_01_1_Axis_valuesize') :
      Plane_01_1_Axis_valuesize = self.getInputFromPort('Plane_01_1_Axis_valuesize')
    Plane_01_1_Axis_valuesquash = 1.0
    if self.hasInputFromPort('Plane_01_1_Axis_valuesquash') :
      Plane_01_1_Axis_valuesquash = self.getInputFromPort('Plane_01_1_Axis_valuesquash')
    Plane_02_0_Axis_absolute = ''
    if self.hasInputFromPort('Plane_02_0_Axis_absolute') :
      Plane_02_0_Axis_absolute = self.getInputFromPort('Plane_02_0_Axis_absolute')
    Plane_02_0_Axis_divisions = 10
    if self.hasInputFromPort('Plane_02_0_Axis_divisions') :
      Plane_02_0_Axis_divisions = self.getInputFromPort('Plane_02_0_Axis_divisions')
    Plane_02_0_Axis_offset = 1
    if self.hasInputFromPort('Plane_02_0_Axis_offset') :
      Plane_02_0_Axis_offset = self.getInputFromPort('Plane_02_0_Axis_offset')
    Plane_02_0_Axis_range_first = 0.0
    if self.hasInputFromPort('Plane_02_0_Axis_range_first') :
      Plane_02_0_Axis_range_first = self.getInputFromPort('Plane_02_0_Axis_range_first')
    Plane_02_0_Axis_range_second = 1.0
    if self.hasInputFromPort('Plane_02_0_Axis_range_second') :
      Plane_02_0_Axis_range_second = self.getInputFromPort('Plane_02_0_Axis_range_second')
    Plane_02_0_Axis_min_absolute = 0.0
    if self.hasInputFromPort('Plane_02_0_Axis_min_absolute') :
      Plane_02_0_Axis_min_absolute = self.getInputFromPort('Plane_02_0_Axis_min_absolute')
    Plane_02_0_Axis_max_absolute = 1.0
    if self.hasInputFromPort('Plane_02_0_Axis_max_absolute') :
      Plane_02_0_Axis_max_absolute = self.getInputFromPort('Plane_02_0_Axis_max_absolute')
    Plane_02_0_Axis_minplane = 2
    if self.hasInputFromPort('Plane_02_0_Axis_minplane') :
      Plane_02_0_Axis_minplane = self.getInputFromPort('Plane_02_0_Axis_minplane')
    Plane_02_0_Axis_maxplane = 2
    if self.hasInputFromPort('Plane_02_0_Axis_maxplane') :
      Plane_02_0_Axis_maxplane = self.getInputFromPort('Plane_02_0_Axis_maxplane')
    Plane_02_0_Axis_lines = 2
    if self.hasInputFromPort('Plane_02_0_Axis_lines') :
      Plane_02_0_Axis_lines = self.getInputFromPort('Plane_02_0_Axis_lines')
    Plane_02_0_Axis_minticks = 2
    if self.hasInputFromPort('Plane_02_0_Axis_minticks') :
      Plane_02_0_Axis_minticks = self.getInputFromPort('Plane_02_0_Axis_minticks')
    Plane_02_0_Axis_maxticks = 2
    if self.hasInputFromPort('Plane_02_0_Axis_maxticks') :
      Plane_02_0_Axis_maxticks = self.getInputFromPort('Plane_02_0_Axis_maxticks')
    Plane_02_0_Axis_minlabel = 2
    if self.hasInputFromPort('Plane_02_0_Axis_minlabel') :
      Plane_02_0_Axis_minlabel = self.getInputFromPort('Plane_02_0_Axis_minlabel')
    Plane_02_0_Axis_maxlabel = 2
    if self.hasInputFromPort('Plane_02_0_Axis_maxlabel') :
      Plane_02_0_Axis_maxlabel = self.getInputFromPort('Plane_02_0_Axis_maxlabel')
    Plane_02_0_Axis_minvalue = 2
    if self.hasInputFromPort('Plane_02_0_Axis_minvalue') :
      Plane_02_0_Axis_minvalue = self.getInputFromPort('Plane_02_0_Axis_minvalue')
    Plane_02_0_Axis_maxvalue = 2
    if self.hasInputFromPort('Plane_02_0_Axis_maxvalue') :
      Plane_02_0_Axis_maxvalue = self.getInputFromPort('Plane_02_0_Axis_maxvalue')
    Plane_02_0_Axis_width = 1
    if self.hasInputFromPort('Plane_02_0_Axis_width') :
      Plane_02_0_Axis_width = self.getInputFromPort('Plane_02_0_Axis_width')
    Plane_02_0_Axis_tickangle = 0
    if self.hasInputFromPort('Plane_02_0_Axis_tickangle') :
      Plane_02_0_Axis_tickangle = self.getInputFromPort('Plane_02_0_Axis_tickangle')
    Plane_02_0_Axis_ticktilt = 0
    if self.hasInputFromPort('Plane_02_0_Axis_ticktilt') :
      Plane_02_0_Axis_ticktilt = self.getInputFromPort('Plane_02_0_Axis_ticktilt')
    Plane_02_0_Axis_ticksize = 5
    if self.hasInputFromPort('Plane_02_0_Axis_ticksize') :
      Plane_02_0_Axis_ticksize = self.getInputFromPort('Plane_02_0_Axis_ticksize')
    Plane_02_0_Axis_labelangle = 0
    if self.hasInputFromPort('Plane_02_0_Axis_labelangle') :
      Plane_02_0_Axis_labelangle = self.getInputFromPort('Plane_02_0_Axis_labelangle')
    Plane_02_0_Axis_labelheight = 6
    if self.hasInputFromPort('Plane_02_0_Axis_labelheight') :
      Plane_02_0_Axis_labelheight = self.getInputFromPort('Plane_02_0_Axis_labelheight')
    Plane_02_0_Axis_valuesize = 3
    if self.hasInputFromPort('Plane_02_0_Axis_valuesize') :
      Plane_02_0_Axis_valuesize = self.getInputFromPort('Plane_02_0_Axis_valuesize')
    Plane_02_0_Axis_valuesquash = 1.0
    if self.hasInputFromPort('Plane_02_0_Axis_valuesquash') :
      Plane_02_0_Axis_valuesquash = self.getInputFromPort('Plane_02_0_Axis_valuesquash')
    Plane_02_2_Axis_absolute = ''
    if self.hasInputFromPort('Plane_02_2_Axis_absolute') :
      Plane_02_2_Axis_absolute = self.getInputFromPort('Plane_02_2_Axis_absolute')
    Plane_02_2_Axis_divisions = 10
    if self.hasInputFromPort('Plane_02_2_Axis_divisions') :
      Plane_02_2_Axis_divisions = self.getInputFromPort('Plane_02_2_Axis_divisions')
    Plane_02_2_Axis_offset = 1
    if self.hasInputFromPort('Plane_02_2_Axis_offset') :
      Plane_02_2_Axis_offset = self.getInputFromPort('Plane_02_2_Axis_offset')
    Plane_02_2_Axis_range_first = 0.0
    if self.hasInputFromPort('Plane_02_2_Axis_range_first') :
      Plane_02_2_Axis_range_first = self.getInputFromPort('Plane_02_2_Axis_range_first')
    Plane_02_2_Axis_range_second = 1.0
    if self.hasInputFromPort('Plane_02_2_Axis_range_second') :
      Plane_02_2_Axis_range_second = self.getInputFromPort('Plane_02_2_Axis_range_second')
    Plane_02_2_Axis_min_absolute = 0.0
    if self.hasInputFromPort('Plane_02_2_Axis_min_absolute') :
      Plane_02_2_Axis_min_absolute = self.getInputFromPort('Plane_02_2_Axis_min_absolute')
    Plane_02_2_Axis_max_absolute = 1.0
    if self.hasInputFromPort('Plane_02_2_Axis_max_absolute') :
      Plane_02_2_Axis_max_absolute = self.getInputFromPort('Plane_02_2_Axis_max_absolute')
    Plane_02_2_Axis_minplane = 2
    if self.hasInputFromPort('Plane_02_2_Axis_minplane') :
      Plane_02_2_Axis_minplane = self.getInputFromPort('Plane_02_2_Axis_minplane')
    Plane_02_2_Axis_maxplane = 2
    if self.hasInputFromPort('Plane_02_2_Axis_maxplane') :
      Plane_02_2_Axis_maxplane = self.getInputFromPort('Plane_02_2_Axis_maxplane')
    Plane_02_2_Axis_lines = 2
    if self.hasInputFromPort('Plane_02_2_Axis_lines') :
      Plane_02_2_Axis_lines = self.getInputFromPort('Plane_02_2_Axis_lines')
    Plane_02_2_Axis_minticks = 2
    if self.hasInputFromPort('Plane_02_2_Axis_minticks') :
      Plane_02_2_Axis_minticks = self.getInputFromPort('Plane_02_2_Axis_minticks')
    Plane_02_2_Axis_maxticks = 2
    if self.hasInputFromPort('Plane_02_2_Axis_maxticks') :
      Plane_02_2_Axis_maxticks = self.getInputFromPort('Plane_02_2_Axis_maxticks')
    Plane_02_2_Axis_minlabel = 2
    if self.hasInputFromPort('Plane_02_2_Axis_minlabel') :
      Plane_02_2_Axis_minlabel = self.getInputFromPort('Plane_02_2_Axis_minlabel')
    Plane_02_2_Axis_maxlabel = 2
    if self.hasInputFromPort('Plane_02_2_Axis_maxlabel') :
      Plane_02_2_Axis_maxlabel = self.getInputFromPort('Plane_02_2_Axis_maxlabel')
    Plane_02_2_Axis_minvalue = 2
    if self.hasInputFromPort('Plane_02_2_Axis_minvalue') :
      Plane_02_2_Axis_minvalue = self.getInputFromPort('Plane_02_2_Axis_minvalue')
    Plane_02_2_Axis_maxvalue = 2
    if self.hasInputFromPort('Plane_02_2_Axis_maxvalue') :
      Plane_02_2_Axis_maxvalue = self.getInputFromPort('Plane_02_2_Axis_maxvalue')
    Plane_02_2_Axis_width = 1
    if self.hasInputFromPort('Plane_02_2_Axis_width') :
      Plane_02_2_Axis_width = self.getInputFromPort('Plane_02_2_Axis_width')
    Plane_02_2_Axis_tickangle = 0
    if self.hasInputFromPort('Plane_02_2_Axis_tickangle') :
      Plane_02_2_Axis_tickangle = self.getInputFromPort('Plane_02_2_Axis_tickangle')
    Plane_02_2_Axis_ticktilt = 0
    if self.hasInputFromPort('Plane_02_2_Axis_ticktilt') :
      Plane_02_2_Axis_ticktilt = self.getInputFromPort('Plane_02_2_Axis_ticktilt')
    Plane_02_2_Axis_ticksize = 5
    if self.hasInputFromPort('Plane_02_2_Axis_ticksize') :
      Plane_02_2_Axis_ticksize = self.getInputFromPort('Plane_02_2_Axis_ticksize')
    Plane_02_2_Axis_labelangle = 0
    if self.hasInputFromPort('Plane_02_2_Axis_labelangle') :
      Plane_02_2_Axis_labelangle = self.getInputFromPort('Plane_02_2_Axis_labelangle')
    Plane_02_2_Axis_labelheight = 6
    if self.hasInputFromPort('Plane_02_2_Axis_labelheight') :
      Plane_02_2_Axis_labelheight = self.getInputFromPort('Plane_02_2_Axis_labelheight')
    Plane_02_2_Axis_valuesize = 3
    if self.hasInputFromPort('Plane_02_2_Axis_valuesize') :
      Plane_02_2_Axis_valuesize = self.getInputFromPort('Plane_02_2_Axis_valuesize')
    Plane_02_2_Axis_valuesquash = 1.0
    if self.hasInputFromPort('Plane_02_2_Axis_valuesquash') :
      Plane_02_2_Axis_valuesquash = self.getInputFromPort('Plane_02_2_Axis_valuesquash')
    Plane_12_1_Axis_absolute = ''
    if self.hasInputFromPort('Plane_12_1_Axis_absolute') :
      Plane_12_1_Axis_absolute = self.getInputFromPort('Plane_12_1_Axis_absolute')
    Plane_12_1_Axis_divisions = 10
    if self.hasInputFromPort('Plane_12_1_Axis_divisions') :
      Plane_12_1_Axis_divisions = self.getInputFromPort('Plane_12_1_Axis_divisions')
    Plane_12_1_Axis_offset = 1
    if self.hasInputFromPort('Plane_12_1_Axis_offset') :
      Plane_12_1_Axis_offset = self.getInputFromPort('Plane_12_1_Axis_offset')
    Plane_12_1_Axis_range_first = 0.0
    if self.hasInputFromPort('Plane_12_1_Axis_range_first') :
      Plane_12_1_Axis_range_first = self.getInputFromPort('Plane_12_1_Axis_range_first')
    Plane_12_1_Axis_range_second = 1.0
    if self.hasInputFromPort('Plane_12_1_Axis_range_second') :
      Plane_12_1_Axis_range_second = self.getInputFromPort('Plane_12_1_Axis_range_second')
    Plane_12_1_Axis_min_absolute = 0.0
    if self.hasInputFromPort('Plane_12_1_Axis_min_absolute') :
      Plane_12_1_Axis_min_absolute = self.getInputFromPort('Plane_12_1_Axis_min_absolute')
    Plane_12_1_Axis_max_absolute = 1.0
    if self.hasInputFromPort('Plane_12_1_Axis_max_absolute') :
      Plane_12_1_Axis_max_absolute = self.getInputFromPort('Plane_12_1_Axis_max_absolute')
    Plane_12_1_Axis_minplane = 2
    if self.hasInputFromPort('Plane_12_1_Axis_minplane') :
      Plane_12_1_Axis_minplane = self.getInputFromPort('Plane_12_1_Axis_minplane')
    Plane_12_1_Axis_maxplane = 2
    if self.hasInputFromPort('Plane_12_1_Axis_maxplane') :
      Plane_12_1_Axis_maxplane = self.getInputFromPort('Plane_12_1_Axis_maxplane')
    Plane_12_1_Axis_lines = 2
    if self.hasInputFromPort('Plane_12_1_Axis_lines') :
      Plane_12_1_Axis_lines = self.getInputFromPort('Plane_12_1_Axis_lines')
    Plane_12_1_Axis_minticks = 2
    if self.hasInputFromPort('Plane_12_1_Axis_minticks') :
      Plane_12_1_Axis_minticks = self.getInputFromPort('Plane_12_1_Axis_minticks')
    Plane_12_1_Axis_maxticks = 2
    if self.hasInputFromPort('Plane_12_1_Axis_maxticks') :
      Plane_12_1_Axis_maxticks = self.getInputFromPort('Plane_12_1_Axis_maxticks')
    Plane_12_1_Axis_minlabel = 2
    if self.hasInputFromPort('Plane_12_1_Axis_minlabel') :
      Plane_12_1_Axis_minlabel = self.getInputFromPort('Plane_12_1_Axis_minlabel')
    Plane_12_1_Axis_maxlabel = 2
    if self.hasInputFromPort('Plane_12_1_Axis_maxlabel') :
      Plane_12_1_Axis_maxlabel = self.getInputFromPort('Plane_12_1_Axis_maxlabel')
    Plane_12_1_Axis_minvalue = 2
    if self.hasInputFromPort('Plane_12_1_Axis_minvalue') :
      Plane_12_1_Axis_minvalue = self.getInputFromPort('Plane_12_1_Axis_minvalue')
    Plane_12_1_Axis_maxvalue = 2
    if self.hasInputFromPort('Plane_12_1_Axis_maxvalue') :
      Plane_12_1_Axis_maxvalue = self.getInputFromPort('Plane_12_1_Axis_maxvalue')
    Plane_12_1_Axis_width = 1
    if self.hasInputFromPort('Plane_12_1_Axis_width') :
      Plane_12_1_Axis_width = self.getInputFromPort('Plane_12_1_Axis_width')
    Plane_12_1_Axis_tickangle = 0
    if self.hasInputFromPort('Plane_12_1_Axis_tickangle') :
      Plane_12_1_Axis_tickangle = self.getInputFromPort('Plane_12_1_Axis_tickangle')
    Plane_12_1_Axis_ticktilt = 0
    if self.hasInputFromPort('Plane_12_1_Axis_ticktilt') :
      Plane_12_1_Axis_ticktilt = self.getInputFromPort('Plane_12_1_Axis_ticktilt')
    Plane_12_1_Axis_ticksize = 5
    if self.hasInputFromPort('Plane_12_1_Axis_ticksize') :
      Plane_12_1_Axis_ticksize = self.getInputFromPort('Plane_12_1_Axis_ticksize')
    Plane_12_1_Axis_labelangle = 0
    if self.hasInputFromPort('Plane_12_1_Axis_labelangle') :
      Plane_12_1_Axis_labelangle = self.getInputFromPort('Plane_12_1_Axis_labelangle')
    Plane_12_1_Axis_labelheight = 6
    if self.hasInputFromPort('Plane_12_1_Axis_labelheight') :
      Plane_12_1_Axis_labelheight = self.getInputFromPort('Plane_12_1_Axis_labelheight')
    Plane_12_1_Axis_valuesize = 3
    if self.hasInputFromPort('Plane_12_1_Axis_valuesize') :
      Plane_12_1_Axis_valuesize = self.getInputFromPort('Plane_12_1_Axis_valuesize')
    Plane_12_1_Axis_valuesquash = 1.0
    if self.hasInputFromPort('Plane_12_1_Axis_valuesquash') :
      Plane_12_1_Axis_valuesquash = self.getInputFromPort('Plane_12_1_Axis_valuesquash')
    Plane_12_2_Axis_absolute = ''
    if self.hasInputFromPort('Plane_12_2_Axis_absolute') :
      Plane_12_2_Axis_absolute = self.getInputFromPort('Plane_12_2_Axis_absolute')
    Plane_12_2_Axis_divisions = 10
    if self.hasInputFromPort('Plane_12_2_Axis_divisions') :
      Plane_12_2_Axis_divisions = self.getInputFromPort('Plane_12_2_Axis_divisions')
    Plane_12_2_Axis_offset = 1
    if self.hasInputFromPort('Plane_12_2_Axis_offset') :
      Plane_12_2_Axis_offset = self.getInputFromPort('Plane_12_2_Axis_offset')
    Plane_12_2_Axis_range_first = 0.0
    if self.hasInputFromPort('Plane_12_2_Axis_range_first') :
      Plane_12_2_Axis_range_first = self.getInputFromPort('Plane_12_2_Axis_range_first')
    Plane_12_2_Axis_range_second = 1.0
    if self.hasInputFromPort('Plane_12_2_Axis_range_second') :
      Plane_12_2_Axis_range_second = self.getInputFromPort('Plane_12_2_Axis_range_second')
    Plane_12_2_Axis_min_absolute = 0.0
    if self.hasInputFromPort('Plane_12_2_Axis_min_absolute') :
      Plane_12_2_Axis_min_absolute = self.getInputFromPort('Plane_12_2_Axis_min_absolute')
    Plane_12_2_Axis_max_absolute = 1.0
    if self.hasInputFromPort('Plane_12_2_Axis_max_absolute') :
      Plane_12_2_Axis_max_absolute = self.getInputFromPort('Plane_12_2_Axis_max_absolute')
    Plane_12_2_Axis_minplane = 2
    if self.hasInputFromPort('Plane_12_2_Axis_minplane') :
      Plane_12_2_Axis_minplane = self.getInputFromPort('Plane_12_2_Axis_minplane')
    Plane_12_2_Axis_maxplane = 2
    if self.hasInputFromPort('Plane_12_2_Axis_maxplane') :
      Plane_12_2_Axis_maxplane = self.getInputFromPort('Plane_12_2_Axis_maxplane')
    Plane_12_2_Axis_lines = 2
    if self.hasInputFromPort('Plane_12_2_Axis_lines') :
      Plane_12_2_Axis_lines = self.getInputFromPort('Plane_12_2_Axis_lines')
    Plane_12_2_Axis_minticks = 2
    if self.hasInputFromPort('Plane_12_2_Axis_minticks') :
      Plane_12_2_Axis_minticks = self.getInputFromPort('Plane_12_2_Axis_minticks')
    Plane_12_2_Axis_maxticks = 2
    if self.hasInputFromPort('Plane_12_2_Axis_maxticks') :
      Plane_12_2_Axis_maxticks = self.getInputFromPort('Plane_12_2_Axis_maxticks')
    Plane_12_2_Axis_minlabel = 2
    if self.hasInputFromPort('Plane_12_2_Axis_minlabel') :
      Plane_12_2_Axis_minlabel = self.getInputFromPort('Plane_12_2_Axis_minlabel')
    Plane_12_2_Axis_maxlabel = 2
    if self.hasInputFromPort('Plane_12_2_Axis_maxlabel') :
      Plane_12_2_Axis_maxlabel = self.getInputFromPort('Plane_12_2_Axis_maxlabel')
    Plane_12_2_Axis_minvalue = 2
    if self.hasInputFromPort('Plane_12_2_Axis_minvalue') :
      Plane_12_2_Axis_minvalue = self.getInputFromPort('Plane_12_2_Axis_minvalue')
    Plane_12_2_Axis_maxvalue = 2
    if self.hasInputFromPort('Plane_12_2_Axis_maxvalue') :
      Plane_12_2_Axis_maxvalue = self.getInputFromPort('Plane_12_2_Axis_maxvalue')
    Plane_12_2_Axis_width = 1
    if self.hasInputFromPort('Plane_12_2_Axis_width') :
      Plane_12_2_Axis_width = self.getInputFromPort('Plane_12_2_Axis_width')
    Plane_12_2_Axis_tickangle = 0
    if self.hasInputFromPort('Plane_12_2_Axis_tickangle') :
      Plane_12_2_Axis_tickangle = self.getInputFromPort('Plane_12_2_Axis_tickangle')
    Plane_12_2_Axis_ticktilt = 0
    if self.hasInputFromPort('Plane_12_2_Axis_ticktilt') :
      Plane_12_2_Axis_ticktilt = self.getInputFromPort('Plane_12_2_Axis_ticktilt')
    Plane_12_2_Axis_ticksize = 5
    if self.hasInputFromPort('Plane_12_2_Axis_ticksize') :
      Plane_12_2_Axis_ticksize = self.getInputFromPort('Plane_12_2_Axis_ticksize')
    Plane_12_2_Axis_labelangle = 0
    if self.hasInputFromPort('Plane_12_2_Axis_labelangle') :
      Plane_12_2_Axis_labelangle = self.getInputFromPort('Plane_12_2_Axis_labelangle')
    Plane_12_2_Axis_labelheight = 6
    if self.hasInputFromPort('Plane_12_2_Axis_labelheight') :
      Plane_12_2_Axis_labelheight = self.getInputFromPort('Plane_12_2_Axis_labelheight')
    Plane_12_2_Axis_valuesize = 3
    if self.hasInputFromPort('Plane_12_2_Axis_valuesize') :
      Plane_12_2_Axis_valuesize = self.getInputFromPort('Plane_12_2_Axis_valuesize')
    Plane_12_2_Axis_valuesquash = 1.0
    if self.hasInputFromPort('Plane_12_2_Axis_valuesquash') :
      Plane_12_2_Axis_valuesquash = self.getInputFromPort('Plane_12_2_Axis_valuesquash')
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    results = sr_py.CreateViewerAxes(Field,precision,squash,valuerez,labelrez,Plane_01_0_Axis_absolute,Plane_01_0_Axis_divisions,Plane_01_0_Axis_offset,Plane_01_0_Axis_range_first,Plane_01_0_Axis_range_second,Plane_01_0_Axis_min_absolute,Plane_01_0_Axis_max_absolute,Plane_01_0_Axis_minplane,Plane_01_0_Axis_maxplane,Plane_01_0_Axis_lines,Plane_01_0_Axis_minticks,Plane_01_0_Axis_maxticks,Plane_01_0_Axis_minlabel,Plane_01_0_Axis_maxlabel,Plane_01_0_Axis_minvalue,Plane_01_0_Axis_maxvalue,Plane_01_0_Axis_width,Plane_01_0_Axis_tickangle,Plane_01_0_Axis_ticktilt,Plane_01_0_Axis_ticksize,Plane_01_0_Axis_labelangle,Plane_01_0_Axis_labelheight,Plane_01_0_Axis_valuesize,Plane_01_0_Axis_valuesquash,Plane_01_1_Axis_absolute,Plane_01_1_Axis_divisions,Plane_01_1_Axis_offset,Plane_01_1_Axis_range_first,Plane_01_1_Axis_range_second,Plane_01_1_Axis_min_absolute,Plane_01_1_Axis_max_absolute,Plane_01_1_Axis_minplane,Plane_01_1_Axis_maxplane,Plane_01_1_Axis_lines,Plane_01_1_Axis_minticks,Plane_01_1_Axis_maxticks,Plane_01_1_Axis_minlabel,Plane_01_1_Axis_maxlabel,Plane_01_1_Axis_minvalue,Plane_01_1_Axis_maxvalue,Plane_01_1_Axis_width,Plane_01_1_Axis_tickangle,Plane_01_1_Axis_ticktilt,Plane_01_1_Axis_ticksize,Plane_01_1_Axis_labelangle,Plane_01_1_Axis_labelheight,Plane_01_1_Axis_valuesize,Plane_01_1_Axis_valuesquash,Plane_02_0_Axis_absolute,Plane_02_0_Axis_divisions,Plane_02_0_Axis_offset,Plane_02_0_Axis_range_first,Plane_02_0_Axis_range_second,Plane_02_0_Axis_min_absolute,Plane_02_0_Axis_max_absolute,Plane_02_0_Axis_minplane,Plane_02_0_Axis_maxplane,Plane_02_0_Axis_lines,Plane_02_0_Axis_minticks,Plane_02_0_Axis_maxticks,Plane_02_0_Axis_minlabel,Plane_02_0_Axis_maxlabel,Plane_02_0_Axis_minvalue,Plane_02_0_Axis_maxvalue,Plane_02_0_Axis_width,Plane_02_0_Axis_tickangle,Plane_02_0_Axis_ticktilt,Plane_02_0_Axis_ticksize,Plane_02_0_Axis_labelangle,Plane_02_0_Axis_labelheight,Plane_02_0_Axis_valuesize,Plane_02_0_Axis_valuesquash,Plane_02_2_Axis_absolute,Plane_02_2_Axis_divisions,Plane_02_2_Axis_offset,Plane_02_2_Axis_range_first,Plane_02_2_Axis_range_second,Plane_02_2_Axis_min_absolute,Plane_02_2_Axis_max_absolute,Plane_02_2_Axis_minplane,Plane_02_2_Axis_maxplane,Plane_02_2_Axis_lines,Plane_02_2_Axis_minticks,Plane_02_2_Axis_maxticks,Plane_02_2_Axis_minlabel,Plane_02_2_Axis_maxlabel,Plane_02_2_Axis_minvalue,Plane_02_2_Axis_maxvalue,Plane_02_2_Axis_width,Plane_02_2_Axis_tickangle,Plane_02_2_Axis_ticktilt,Plane_02_2_Axis_ticksize,Plane_02_2_Axis_labelangle,Plane_02_2_Axis_labelheight,Plane_02_2_Axis_valuesize,Plane_02_2_Axis_valuesquash,Plane_12_1_Axis_absolute,Plane_12_1_Axis_divisions,Plane_12_1_Axis_offset,Plane_12_1_Axis_range_first,Plane_12_1_Axis_range_second,Plane_12_1_Axis_min_absolute,Plane_12_1_Axis_max_absolute,Plane_12_1_Axis_minplane,Plane_12_1_Axis_maxplane,Plane_12_1_Axis_lines,Plane_12_1_Axis_minticks,Plane_12_1_Axis_maxticks,Plane_12_1_Axis_minlabel,Plane_12_1_Axis_maxlabel,Plane_12_1_Axis_minvalue,Plane_12_1_Axis_maxvalue,Plane_12_1_Axis_width,Plane_12_1_Axis_tickangle,Plane_12_1_Axis_ticktilt,Plane_12_1_Axis_ticksize,Plane_12_1_Axis_labelangle,Plane_12_1_Axis_labelheight,Plane_12_1_Axis_valuesize,Plane_12_1_Axis_valuesquash,Plane_12_2_Axis_absolute,Plane_12_2_Axis_divisions,Plane_12_2_Axis_offset,Plane_12_2_Axis_range_first,Plane_12_2_Axis_range_second,Plane_12_2_Axis_min_absolute,Plane_12_2_Axis_max_absolute,Plane_12_2_Axis_minplane,Plane_12_2_Axis_maxplane,Plane_12_2_Axis_lines,Plane_12_2_Axis_minticks,Plane_12_2_Axis_maxticks,Plane_12_2_Axis_minlabel,Plane_12_2_Axis_maxlabel,Plane_12_2_Axis_minvalue,Plane_12_2_Axis_maxvalue,Plane_12_2_Axis_width,Plane_12_2_Axis_tickangle,Plane_12_2_Axis_ticktilt,Plane_12_2_Axis_ticksize,Plane_12_2_Axis_labelangle,Plane_12_2_Axis_labelheight,Plane_12_2_Axis_valuesize,Plane_12_2_Axis_valuesquash)
    self.setResult('Axes', results)

class SCIRun_ShowField(Module) :
  def compute(self) :
    nodes_on = 1
    if self.hasInputFromPort('nodes_on') :
      nodes_on = self.getInputFromPort('nodes_on')
    nodes_transparency = 0
    if self.hasInputFromPort('nodes_transparency') :
      nodes_transparency = self.getInputFromPort('nodes_transparency')
    nodes_color_type = 0
    if self.hasInputFromPort('nodes_color_type') :
      nodes_color_type = self.getInputFromPort('nodes_color_type')
    nodes_display_type = 'Points'
    if self.hasInputFromPort('nodes_display_type') :
      nodes_display_type = self.getInputFromPort('nodes_display_type')
    edges_on = 1
    if self.hasInputFromPort('edges_on') :
      edges_on = self.getInputFromPort('edges_on')
    edges_transparency = 0
    if self.hasInputFromPort('edges_transparency') :
      edges_transparency = self.getInputFromPort('edges_transparency')
    edges_color_type = 0
    if self.hasInputFromPort('edges_color_type') :
      edges_color_type = self.getInputFromPort('edges_color_type')
    edges_display_type = 'Lines'
    if self.hasInputFromPort('edges_display_type') :
      edges_display_type = self.getInputFromPort('edges_display_type')
    faces_on = 1
    if self.hasInputFromPort('faces_on') :
      faces_on = self.getInputFromPort('faces_on')
    faces_transparency = 0
    if self.hasInputFromPort('faces_transparency') :
      faces_transparency = self.getInputFromPort('faces_transparency')
    faces_color_type = 0
    if self.hasInputFromPort('faces_color_type') :
      faces_color_type = self.getInputFromPort('faces_color_type')
    faces_normals = 0
    if self.hasInputFromPort('faces_normals') :
      faces_normals = self.getInputFromPort('faces_normals')
    faces_usetexture = 0
    if self.hasInputFromPort('faces_usetexture') :
      faces_usetexture = self.getInputFromPort('faces_usetexture')
    text_on = 0
    if self.hasInputFromPort('text_on') :
      text_on = self.getInputFromPort('text_on')
    text_color_type = 0
    if self.hasInputFromPort('text_color_type') :
      text_color_type = self.getInputFromPort('text_color_type')
    text_color_r = 1.0
    if self.hasInputFromPort('text_color_r') :
      text_color_r = self.getInputFromPort('text_color_r')
    text_color_g = 1.0
    if self.hasInputFromPort('text_color_g') :
      text_color_g = self.getInputFromPort('text_color_g')
    text_color_b = 1.0
    if self.hasInputFromPort('text_color_b') :
      text_color_b = self.getInputFromPort('text_color_b')
    text_backface_cull = 0
    if self.hasInputFromPort('text_backface_cull') :
      text_backface_cull = self.getInputFromPort('text_backface_cull')
    text_always_visible = 0
    if self.hasInputFromPort('text_always_visible') :
      text_always_visible = self.getInputFromPort('text_always_visible')
    text_fontsize = 1
    if self.hasInputFromPort('text_fontsize') :
      text_fontsize = self.getInputFromPort('text_fontsize')
    text_precision = 3
    if self.hasInputFromPort('text_precision') :
      text_precision = self.getInputFromPort('text_precision')
    text_render_locations = 0
    if self.hasInputFromPort('text_render_locations') :
      text_render_locations = self.getInputFromPort('text_render_locations')
    text_show_data = 1
    if self.hasInputFromPort('text_show_data') :
      text_show_data = self.getInputFromPort('text_show_data')
    text_show_nodes = 0
    if self.hasInputFromPort('text_show_nodes') :
      text_show_nodes = self.getInputFromPort('text_show_nodes')
    text_show_edges = 0
    if self.hasInputFromPort('text_show_edges') :
      text_show_edges = self.getInputFromPort('text_show_edges')
    text_show_faces = 0
    if self.hasInputFromPort('text_show_faces') :
      text_show_faces = self.getInputFromPort('text_show_faces')
    text_show_cells = 0
    if self.hasInputFromPort('text_show_cells') :
      text_show_cells = self.getInputFromPort('text_show_cells')
    def_color_r = 0.5
    if self.hasInputFromPort('def_color_r') :
      def_color_r = self.getInputFromPort('def_color_r')
    def_color_g = 0.5
    if self.hasInputFromPort('def_color_g') :
      def_color_g = self.getInputFromPort('def_color_g')
    def_color_b = 0.5
    if self.hasInputFromPort('def_color_b') :
      def_color_b = self.getInputFromPort('def_color_b')
    def_color_a = 0.75
    if self.hasInputFromPort('def_color_a') :
      def_color_a = self.getInputFromPort('def_color_a')
    nodes_scale = 0.03
    if self.hasInputFromPort('nodes_scale') :
      nodes_scale = self.getInputFromPort('nodes_scale')
    nodes_scaleNV = -0.0
    if self.hasInputFromPort('nodes_scaleNV') :
      nodes_scaleNV = self.getInputFromPort('nodes_scaleNV')
    edges_scale = 0.15
    if self.hasInputFromPort('edges_scale') :
      edges_scale = self.getInputFromPort('edges_scale')
    edges_scaleNV = -0.0
    if self.hasInputFromPort('edges_scaleNV') :
      edges_scaleNV = self.getInputFromPort('edges_scaleNV')
    active_tab = 'Nodes'
    if self.hasInputFromPort('active_tab') :
      active_tab = self.getInputFromPort('active_tab')
    interactive_mode = 'Interactive'
    if self.hasInputFromPort('interactive_mode') :
      interactive_mode = self.getInputFromPort('interactive_mode')
    show_progress = 0
    if self.hasInputFromPort('show_progress') :
      show_progress = self.getInputFromPort('show_progress')
    field_name = ''
    if self.hasInputFromPort('field_name') :
      field_name = self.getInputFromPort('field_name')
    field_name_override = 0
    if self.hasInputFromPort('field_name_override') :
      field_name_override = self.getInputFromPort('field_name_override')
    nodes_resolution = 6
    if self.hasInputFromPort('nodes_resolution') :
      nodes_resolution = self.getInputFromPort('nodes_resolution')
    edges_resolution = 6
    if self.hasInputFromPort('edges_resolution') :
      edges_resolution = self.getInputFromPort('edges_resolution')
    approx_div = 1
    if self.hasInputFromPort('approx_div') :
      approx_div = self.getInputFromPort('approx_div')
    use_default_size = 0
    if self.hasInputFromPort('use_default_size') :
      use_default_size = self.getInputFromPort('use_default_size')
    Mesh = 0
    if self.hasInputFromPort('Mesh') :
      Mesh = self.getInputFromPort('Mesh')
    ColorMap = 0
    if self.hasInputFromPort('ColorMap') :
      ColorMap = self.getInputFromPort('ColorMap')
    results = sr_py.ShowField(Mesh,ColorMap,nodes_on,nodes_transparency,nodes_color_type,nodes_display_type,edges_on,edges_transparency,edges_color_type,edges_display_type,faces_on,faces_transparency,faces_color_type,faces_normals,faces_usetexture,text_on,text_color_type,text_color_r,text_color_g,text_color_b,text_backface_cull,text_always_visible,text_fontsize,text_precision,text_render_locations,text_show_data,text_show_nodes,text_show_edges,text_show_faces,text_show_cells,def_color_r,def_color_g,def_color_b,def_color_a,nodes_scale,nodes_scaleNV,edges_scale,edges_scaleNV,active_tab,interactive_mode,show_progress,field_name,field_name_override,nodes_resolution,edges_resolution,approx_div,use_default_size)
    self.setResult('Scene Graph', results)

class SCIRun_SetFieldData(Module) :
  def compute(self) :
    keepscalartype = 0
    if self.hasInputFromPort('keepscalartype') :
      keepscalartype = self.getInputFromPort('keepscalartype')
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    Matrix_Data = 0
    if self.hasInputFromPort('Matrix Data') :
      Matrix_Data = self.getInputFromPort('Matrix Data')
    Nrrd_Data = 0
    if self.hasInputFromPort('Nrrd Data') :
      Nrrd_Data = self.getInputFromPort('Nrrd Data')
    results = sr_py.SetFieldData(Field,Matrix_Data,Nrrd_Data,keepscalartype)
    self.setResult('Field', results)

class SCIRun_CreateVectorArray(Module) :
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

class SCIRun_SynchronizeGeometry(Module) :
  def compute(self) :
    enforce = 1
    if self.hasInputFromPort('enforce') :
      enforce = self.getInputFromPort('enforce')
    Input_Geometry = 0
    if self.hasInputFromPort('Input Geometry') :
      Input_Geometry = self.getInputFromPort('Input Geometry')
    results = sr_py.SynchronizeGeometry(Input_Geometry,enforce)
    self.setResult('Output Geometry', results)

class SCIRun_ClipFieldWithSeed(Module) :
  def compute(self) :
    mode = 'allnodes'
    if self.hasInputFromPort('mode') :
      mode = self.getInputFromPort('mode')
    function = 'return (fx < 0);'
    if self.hasInputFromPort('function') :
      function = self.getInputFromPort('function')
    Function = 0
    if self.hasInputFromPort('Function') :
      Function = self.getInputFromPort('Function')
    Input = 0
    if self.hasInputFromPort('Input') :
      Input = self.getInputFromPort('Input')
    Seeds = 0
    if self.hasInputFromPort('Seeds') :
      Seeds = self.getInputFromPort('Seeds')
    results = sr_py.ClipFieldWithSeed(Function,Input,Seeds,mode,function)
    self.setResult('Clipped', sr_py.read_at_index(results,0))
    self.setResult('Mapping', sr_py.read_at_index(results,1))
    self.setResult('MaskVector', sr_py.read_at_index(results,2))

class SCIRun_SolveLinearSystem(Module) :
  def compute(self) :
    target_error = 0.001
    if self.hasInputFromPort('target_error') :
      target_error = self.getInputFromPort('target_error')
    flops = 0.0
    if self.hasInputFromPort('flops') :
      flops = self.getInputFromPort('flops')
    floprate = 0.0
    if self.hasInputFromPort('floprate') :
      floprate = self.getInputFromPort('floprate')
    memrefs = 0.0
    if self.hasInputFromPort('memrefs') :
      memrefs = self.getInputFromPort('memrefs')
    memrate = 0.0
    if self.hasInputFromPort('memrate') :
      memrate = self.getInputFromPort('memrate')
    orig_error = 0.0
    if self.hasInputFromPort('orig_error') :
      orig_error = self.getInputFromPort('orig_error')
    current_error = ''
    if self.hasInputFromPort('current_error') :
      current_error = self.getInputFromPort('current_error')
    method = 'Conjugate Gradient & Precond. (SCI)'
    if self.hasInputFromPort('method') :
      method = self.getInputFromPort('method')
    precond = 'jacobi'
    if self.hasInputFromPort('precond') :
      precond = self.getInputFromPort('precond')
    iteration = 0
    if self.hasInputFromPort('iteration') :
      iteration = self.getInputFromPort('iteration')
    maxiter = 200
    if self.hasInputFromPort('maxiter') :
      maxiter = self.getInputFromPort('maxiter')
    use_previous_soln = 1
    if self.hasInputFromPort('use_previous_soln') :
      use_previous_soln = self.getInputFromPort('use_previous_soln')
    emit_partial = 1
    if self.hasInputFromPort('emit_partial') :
      emit_partial = self.getInputFromPort('emit_partial')
    emit_iter = 50
    if self.hasInputFromPort('emit_iter') :
      emit_iter = self.getInputFromPort('emit_iter')
    status = ''
    if self.hasInputFromPort('status') :
      status = self.getInputFromPort('status')
    np = 4
    if self.hasInputFromPort('np') :
      np = self.getInputFromPort('np')
    Matrix = 0
    if self.hasInputFromPort('Matrix') :
      Matrix = self.getInputFromPort('Matrix')
    RHS = 0
    if self.hasInputFromPort('RHS') :
      RHS = self.getInputFromPort('RHS')
    results = sr_py.SolveLinearSystem(Matrix,RHS,target_error,flops,floprate,memrefs,memrate,orig_error,current_error,method,precond,iteration,maxiter,use_previous_soln,emit_partial,emit_iter,status,np)
    self.setResult('Solution', results)

class SCIRun_ShowFieldV1(Module) :
  def compute(self) :
    nodes_on = 1
    if self.hasInputFromPort('nodes_on') :
      nodes_on = self.getInputFromPort('nodes_on')
    nodes_transparency = 0
    if self.hasInputFromPort('nodes_transparency') :
      nodes_transparency = self.getInputFromPort('nodes_transparency')
    nodes_as_disks = 0
    if self.hasInputFromPort('nodes_as_disks') :
      nodes_as_disks = self.getInputFromPort('nodes_as_disks')
    nodes_usedefcolor = 0
    if self.hasInputFromPort('nodes_usedefcolor') :
      nodes_usedefcolor = self.getInputFromPort('nodes_usedefcolor')
    edges_on = 1
    if self.hasInputFromPort('edges_on') :
      edges_on = self.getInputFromPort('edges_on')
    edges_transparency = 0
    if self.hasInputFromPort('edges_transparency') :
      edges_transparency = self.getInputFromPort('edges_transparency')
    edges_usedefcolor = 0
    if self.hasInputFromPort('edges_usedefcolor') :
      edges_usedefcolor = self.getInputFromPort('edges_usedefcolor')
    faces_on = 1
    if self.hasInputFromPort('faces_on') :
      faces_on = self.getInputFromPort('faces_on')
    use_normals = 0
    if self.hasInputFromPort('use_normals') :
      use_normals = self.getInputFromPort('use_normals')
    use_transparency = 0
    if self.hasInputFromPort('use_transparency') :
      use_transparency = self.getInputFromPort('use_transparency')
    faces_usedefcolor = 0
    if self.hasInputFromPort('faces_usedefcolor') :
      faces_usedefcolor = self.getInputFromPort('faces_usedefcolor')
    faces_usetexture = 0
    if self.hasInputFromPort('faces_usetexture') :
      faces_usetexture = self.getInputFromPort('faces_usetexture')
    scalars_on = 0
    if self.hasInputFromPort('scalars_on') :
      scalars_on = self.getInputFromPort('scalars_on')
    scalars_transparency = 0
    if self.hasInputFromPort('scalars_transparency') :
      scalars_transparency = self.getInputFromPort('scalars_transparency')
    normalize_scalars = 0
    if self.hasInputFromPort('normalize_scalars') :
      normalize_scalars = self.getInputFromPort('normalize_scalars')
    scalars_usedefcolor = 0
    if self.hasInputFromPort('scalars_usedefcolor') :
      scalars_usedefcolor = self.getInputFromPort('scalars_usedefcolor')
    has_scalar_data = 0
    if self.hasInputFromPort('has_scalar_data') :
      has_scalar_data = self.getInputFromPort('has_scalar_data')
    vectors_on = 0
    if self.hasInputFromPort('vectors_on') :
      vectors_on = self.getInputFromPort('vectors_on')
    vectors_transparency = 0
    if self.hasInputFromPort('vectors_transparency') :
      vectors_transparency = self.getInputFromPort('vectors_transparency')
    normalize_vectors = 0
    if self.hasInputFromPort('normalize_vectors') :
      normalize_vectors = self.getInputFromPort('normalize_vectors')
    has_vector_data = 0
    if self.hasInputFromPort('has_vector_data') :
      has_vector_data = self.getInputFromPort('has_vector_data')
    bidirectional = 0
    if self.hasInputFromPort('bidirectional') :
      bidirectional = self.getInputFromPort('bidirectional')
    vectors_usedefcolor = 0
    if self.hasInputFromPort('vectors_usedefcolor') :
      vectors_usedefcolor = self.getInputFromPort('vectors_usedefcolor')
    tensors_on = 0
    if self.hasInputFromPort('tensors_on') :
      tensors_on = self.getInputFromPort('tensors_on')
    tensors_transparency = 0
    if self.hasInputFromPort('tensors_transparency') :
      tensors_transparency = self.getInputFromPort('tensors_transparency')
    normalize_tensors = 0
    if self.hasInputFromPort('normalize_tensors') :
      normalize_tensors = self.getInputFromPort('normalize_tensors')
    has_tensor_data = 0
    if self.hasInputFromPort('has_tensor_data') :
      has_tensor_data = self.getInputFromPort('has_tensor_data')
    tensors_usedefcolor = 0
    if self.hasInputFromPort('tensors_usedefcolor') :
      tensors_usedefcolor = self.getInputFromPort('tensors_usedefcolor')
    tensors_emphasis = 0.825
    if self.hasInputFromPort('tensors_emphasis') :
      tensors_emphasis = self.getInputFromPort('tensors_emphasis')
    text_on = 0
    if self.hasInputFromPort('text_on') :
      text_on = self.getInputFromPort('text_on')
    text_use_default_color = 1
    if self.hasInputFromPort('text_use_default_color') :
      text_use_default_color = self.getInputFromPort('text_use_default_color')
    text_color_r = 1.0
    if self.hasInputFromPort('text_color_r') :
      text_color_r = self.getInputFromPort('text_color_r')
    text_color_g = 1.0
    if self.hasInputFromPort('text_color_g') :
      text_color_g = self.getInputFromPort('text_color_g')
    text_color_b = 1.0
    if self.hasInputFromPort('text_color_b') :
      text_color_b = self.getInputFromPort('text_color_b')
    text_backface_cull = 0
    if self.hasInputFromPort('text_backface_cull') :
      text_backface_cull = self.getInputFromPort('text_backface_cull')
    text_always_visible = 0
    if self.hasInputFromPort('text_always_visible') :
      text_always_visible = self.getInputFromPort('text_always_visible')
    text_fontsize = 1
    if self.hasInputFromPort('text_fontsize') :
      text_fontsize = self.getInputFromPort('text_fontsize')
    text_precision = 2
    if self.hasInputFromPort('text_precision') :
      text_precision = self.getInputFromPort('text_precision')
    text_render_locations = 0
    if self.hasInputFromPort('text_render_locations') :
      text_render_locations = self.getInputFromPort('text_render_locations')
    text_show_data = 1
    if self.hasInputFromPort('text_show_data') :
      text_show_data = self.getInputFromPort('text_show_data')
    text_show_nodes = 0
    if self.hasInputFromPort('text_show_nodes') :
      text_show_nodes = self.getInputFromPort('text_show_nodes')
    text_show_edges = 0
    if self.hasInputFromPort('text_show_edges') :
      text_show_edges = self.getInputFromPort('text_show_edges')
    text_show_faces = 0
    if self.hasInputFromPort('text_show_faces') :
      text_show_faces = self.getInputFromPort('text_show_faces')
    text_show_cells = 0
    if self.hasInputFromPort('text_show_cells') :
      text_show_cells = self.getInputFromPort('text_show_cells')
    def_color_r = 0.5
    if self.hasInputFromPort('def_color_r') :
      def_color_r = self.getInputFromPort('def_color_r')
    def_color_g = 0.5
    if self.hasInputFromPort('def_color_g') :
      def_color_g = self.getInputFromPort('def_color_g')
    def_color_b = 0.5
    if self.hasInputFromPort('def_color_b') :
      def_color_b = self.getInputFromPort('def_color_b')
    def_color_a = 0.5
    if self.hasInputFromPort('def_color_a') :
      def_color_a = self.getInputFromPort('def_color_a')
    node_display_type = 'Points'
    if self.hasInputFromPort('node_display_type') :
      node_display_type = self.getInputFromPort('node_display_type')
    edge_display_type = 'Lines'
    if self.hasInputFromPort('edge_display_type') :
      edge_display_type = self.getInputFromPort('edge_display_type')
    data_display_type = 'Arrows'
    if self.hasInputFromPort('data_display_type') :
      data_display_type = self.getInputFromPort('data_display_type')
    tensor_display_type = 'Boxes'
    if self.hasInputFromPort('tensor_display_type') :
      tensor_display_type = self.getInputFromPort('tensor_display_type')
    scalar_display_type = 'Points'
    if self.hasInputFromPort('scalar_display_type') :
      scalar_display_type = self.getInputFromPort('scalar_display_type')
    active_tab = 'Nodes'
    if self.hasInputFromPort('active_tab') :
      active_tab = self.getInputFromPort('active_tab')
    node_scale = 0.03
    if self.hasInputFromPort('node_scale') :
      node_scale = self.getInputFromPort('node_scale')
    node_scaleNV = -0.0
    if self.hasInputFromPort('node_scaleNV') :
      node_scaleNV = self.getInputFromPort('node_scaleNV')
    edge_scale = 0.015
    if self.hasInputFromPort('edge_scale') :
      edge_scale = self.getInputFromPort('edge_scale')
    edge_scaleNV = -0.0
    if self.hasInputFromPort('edge_scaleNV') :
      edge_scaleNV = self.getInputFromPort('edge_scaleNV')
    vectors_scale = 0.3
    if self.hasInputFromPort('vectors_scale') :
      vectors_scale = self.getInputFromPort('vectors_scale')
    vectors_scaleNV = -0.0
    if self.hasInputFromPort('vectors_scaleNV') :
      vectors_scaleNV = self.getInputFromPort('vectors_scaleNV')
    tensors_scale = 0.3
    if self.hasInputFromPort('tensors_scale') :
      tensors_scale = self.getInputFromPort('tensors_scale')
    tensors_scaleNV = -0.0
    if self.hasInputFromPort('tensors_scaleNV') :
      tensors_scaleNV = self.getInputFromPort('tensors_scaleNV')
    scalars_scale = 0.3
    if self.hasInputFromPort('scalars_scale') :
      scalars_scale = self.getInputFromPort('scalars_scale')
    scalars_scaleNV = -0.0
    if self.hasInputFromPort('scalars_scaleNV') :
      scalars_scaleNV = self.getInputFromPort('scalars_scaleNV')
    interactive_mode = 'Interactive'
    if self.hasInputFromPort('interactive_mode') :
      interactive_mode = self.getInputFromPort('interactive_mode')
    field_name = ''
    if self.hasInputFromPort('field_name') :
      field_name = self.getInputFromPort('field_name')
    field_name_override = 0
    if self.hasInputFromPort('field_name_override') :
      field_name_override = self.getInputFromPort('field_name_override')
    field_name_update = 1
    if self.hasInputFromPort('field_name_update') :
      field_name_update = self.getInputFromPort('field_name_update')
    node_resolution = 6
    if self.hasInputFromPort('node_resolution') :
      node_resolution = self.getInputFromPort('node_resolution')
    edge_resolution = 6
    if self.hasInputFromPort('edge_resolution') :
      edge_resolution = self.getInputFromPort('edge_resolution')
    data_resolution = 6
    if self.hasInputFromPort('data_resolution') :
      data_resolution = self.getInputFromPort('data_resolution')
    approx_div = 1
    if self.hasInputFromPort('approx_div') :
      approx_div = self.getInputFromPort('approx_div')
    use_default_size = 1
    if self.hasInputFromPort('use_default_size') :
      use_default_size = self.getInputFromPort('use_default_size')
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    ColorMap = 0
    if self.hasInputFromPort('ColorMap') :
      ColorMap = self.getInputFromPort('ColorMap')
    Orientation_Field = 0
    if self.hasInputFromPort('Orientation Field') :
      Orientation_Field = self.getInputFromPort('Orientation Field')
    results = sr_py.ShowFieldV1(Field,ColorMap,Orientation_Field,nodes_on,nodes_transparency,nodes_as_disks,nodes_usedefcolor,edges_on,edges_transparency,edges_usedefcolor,faces_on,use_normals,use_transparency,faces_usedefcolor,faces_usetexture,scalars_on,scalars_transparency,normalize_scalars,scalars_usedefcolor,has_scalar_data,vectors_on,vectors_transparency,normalize_vectors,has_vector_data,bidirectional,vectors_usedefcolor,tensors_on,tensors_transparency,normalize_tensors,has_tensor_data,tensors_usedefcolor,tensors_emphasis,text_on,text_use_default_color,text_color_r,text_color_g,text_color_b,text_backface_cull,text_always_visible,text_fontsize,text_precision,text_render_locations,text_show_data,text_show_nodes,text_show_edges,text_show_faces,text_show_cells,def_color_r,def_color_g,def_color_b,def_color_a,node_display_type,edge_display_type,data_display_type,tensor_display_type,scalar_display_type,active_tab,node_scale,node_scaleNV,edge_scale,edge_scaleNV,vectors_scale,vectors_scaleNV,tensors_scale,tensors_scaleNV,scalars_scale,scalars_scaleNV,interactive_mode,field_name,field_name_override,field_name_update,node_resolution,edge_resolution,data_resolution,approx_div,use_default_size)
    self.setResult('Scene Graph', results)

class SCIRun_ReadPath(Module) :
  def compute(self) :
    from_env = ''
    if self.hasInputFromPort('from_env') :
      from_env = self.getInputFromPort('from_env')
    Filename = 0
    if self.hasInputFromPort('Filename') :
      Filename = self.getInputFromPort('Filename')
    results = sr_py.ReadPath(Filename,from_env)
    self.setResult('Output Data', sr_py.read_at_index(results,0))
    self.setResult('Filename', sr_py.read_at_index(results,1))

class SCIRun_InsertColorMap2sIntoBundle(Module) :
  def compute(self) :
    colormap21_name = 'colormap21'
    if self.hasInputFromPort('colormap21_name') :
      colormap21_name = self.getInputFromPort('colormap21_name')
    colormap22_name = 'colormap22'
    if self.hasInputFromPort('colormap22_name') :
      colormap22_name = self.getInputFromPort('colormap22_name')
    colormap23_name = 'colormap23'
    if self.hasInputFromPort('colormap23_name') :
      colormap23_name = self.getInputFromPort('colormap23_name')
    colormap24_name = 'colormap24'
    if self.hasInputFromPort('colormap24_name') :
      colormap24_name = self.getInputFromPort('colormap24_name')
    colormap25_name = 'colormap25'
    if self.hasInputFromPort('colormap25_name') :
      colormap25_name = self.getInputFromPort('colormap25_name')
    colormap26_name = 'colormap26'
    if self.hasInputFromPort('colormap26_name') :
      colormap26_name = self.getInputFromPort('colormap26_name')
    replace1 = 1
    if self.hasInputFromPort('replace1') :
      replace1 = self.getInputFromPort('replace1')
    replace2 = 1
    if self.hasInputFromPort('replace2') :
      replace2 = self.getInputFromPort('replace2')
    replace3 = 1
    if self.hasInputFromPort('replace3') :
      replace3 = self.getInputFromPort('replace3')
    replace4 = 1
    if self.hasInputFromPort('replace4') :
      replace4 = self.getInputFromPort('replace4')
    replace5 = 1
    if self.hasInputFromPort('replace5') :
      replace5 = self.getInputFromPort('replace5')
    replace6 = 1
    if self.hasInputFromPort('replace6') :
      replace6 = self.getInputFromPort('replace6')
    bundlename = ''
    if self.hasInputFromPort('bundlename') :
      bundlename = self.getInputFromPort('bundlename')
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
    results = sr_py.InsertColorMap2sIntoBundle(bundle,colormap21,colormap22,colormap23,colormap24,colormap25,colormap26,colormap21_name,colormap22_name,colormap23_name,colormap24_name,colormap25_name,colormap26_name,replace1,replace2,replace3,replace4,replace5,replace6,bundlename)
    self.setResult('bundle', results)

class SCIRun_ConvertMatrixToString(Module) :
  def compute(self) :
    Matrix = 0
    if self.hasInputFromPort('Matrix') :
      Matrix = self.getInputFromPort('Matrix')
    results = sr_py.ConvertMatrixToString(Matrix)
    self.setResult('String', results)

class SCIRun_ExtractIsosurface(Module) :
  def compute(self) :
    isoval_min = 0.0
    if self.hasInputFromPort('isoval_min') :
      isoval_min = self.getInputFromPort('isoval_min')
    isoval_max = 99.0
    if self.hasInputFromPort('isoval_max') :
      isoval_max = self.getInputFromPort('isoval_max')
    isoval = 0.0
    if self.hasInputFromPort('isoval') :
      isoval = self.getInputFromPort('isoval')
    isoval_typed = 0.0
    if self.hasInputFromPort('isoval_typed') :
      isoval_typed = self.getInputFromPort('isoval_typed')
    isoval_quantity = 1
    if self.hasInputFromPort('isoval_quantity') :
      isoval_quantity = self.getInputFromPort('isoval_quantity')
    quantity_range = 'field'
    if self.hasInputFromPort('quantity_range') :
      quantity_range = self.getInputFromPort('quantity_range')
    quantity_clusive = 'exclusive'
    if self.hasInputFromPort('quantity_clusive') :
      quantity_clusive = self.getInputFromPort('quantity_clusive')
    quantity_min = 0.0
    if self.hasInputFromPort('quantity_min') :
      quantity_min = self.getInputFromPort('quantity_min')
    quantity_max = 100.0
    if self.hasInputFromPort('quantity_max') :
      quantity_max = self.getInputFromPort('quantity_max')
    quantity_list = ''
    if self.hasInputFromPort('quantity_list') :
      quantity_list = self.getInputFromPort('quantity_list')
    isoval_list = 'No values present.'
    if self.hasInputFromPort('isoval_list') :
      isoval_list = self.getInputFromPort('isoval_list')
    matrix_list = 'No matrix present - execution needed.'
    if self.hasInputFromPort('matrix_list') :
      matrix_list = self.getInputFromPort('matrix_list')
    extract_from_new_field = 1
    if self.hasInputFromPort('extract_from_new_field') :
      extract_from_new_field = self.getInputFromPort('extract_from_new_field')
    algorithm = 0
    if self.hasInputFromPort('algorithm') :
      algorithm = self.getInputFromPort('algorithm')
    build_trisurf = 1
    if self.hasInputFromPort('build_trisurf') :
      build_trisurf = self.getInputFromPort('build_trisurf')
    build_geom = 1
    if self.hasInputFromPort('build_geom') :
      build_geom = self.getInputFromPort('build_geom')
    np = 1
    if self.hasInputFromPort('np') :
      np = self.getInputFromPort('np')
    active_isoval_selection_tab = 0
    if self.hasInputFromPort('active_isoval_selection_tab') :
      active_isoval_selection_tab = self.getInputFromPort('active_isoval_selection_tab')
    active_tab = 0
    if self.hasInputFromPort('active_tab') :
      active_tab = self.getInputFromPort('active_tab')
    update_type = 'On Release'
    if self.hasInputFromPort('update_type') :
      update_type = self.getInputFromPort('update_type')
    color_r = 0.4
    if self.hasInputFromPort('color_r') :
      color_r = self.getInputFromPort('color_r')
    color_g = 0.2
    if self.hasInputFromPort('color_g') :
      color_g = self.getInputFromPort('color_g')
    color_b = 0.9
    if self.hasInputFromPort('color_b') :
      color_b = self.getInputFromPort('color_b')
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    Optional_Color_Map = 0
    if self.hasInputFromPort('Optional Color Map') :
      Optional_Color_Map = self.getInputFromPort('Optional Color Map')
    Optional_Isovalues = 0
    if self.hasInputFromPort('Optional Isovalues') :
      Optional_Isovalues = self.getInputFromPort('Optional Isovalues')
    results = sr_py.ExtractIsosurface(Field,Optional_Color_Map,Optional_Isovalues,isoval_min,isoval_max,isoval,isoval_typed,isoval_quantity,quantity_range,quantity_clusive,quantity_min,quantity_max,quantity_list,isoval_list,matrix_list,extract_from_new_field,algorithm,build_trisurf,build_geom,np,active_isoval_selection_tab,active_tab,update_type,color_r,color_g,color_b)
    self.setResult('Surface', sr_py.read_at_index(results,0))
    self.setResult('Geometry', sr_py.read_at_index(results,1))
    self.setResult('Mapping', sr_py.read_at_index(results,2))

class SCIRun_ConvertMeshToUnstructuredMesh(Module) :
  def compute(self) :
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    results = sr_py.ConvertMeshToUnstructuredMesh(Input_Field)
    self.setResult('Output Field', results)

class SCIRun_ReportMatrixColumnMeasure(Module) :
  def compute(self) :
    method = 'Sum'
    if self.hasInputFromPort('method') :
      method = self.getInputFromPort('method')
    Matrix = 0
    if self.hasInputFromPort('Matrix') :
      Matrix = self.getInputFromPort('Matrix')
    results = sr_py.ReportMatrixColumnMeasure(Matrix,method)
    self.setResult('Vector', results)

class SCIRun_ReplicateDataArray(Module) :
  def compute(self) :
    size = 1
    if self.hasInputFromPort('size') :
      size = self.getInputFromPort('size')
    DataArray = 0
    if self.hasInputFromPort('DataArray') :
      DataArray = self.getInputFromPort('DataArray')
    Size = 0
    if self.hasInputFromPort('Size') :
      Size = self.getInputFromPort('Size')
    results = sr_py.ReplicateDataArray(DataArray,Size,size)
    self.setResult('DataArray', results)

class SCIRun_SwapFieldDataWithMatrixEntries(Module) :
  def compute(self) :
    preserve_scalar_type = 0
    if self.hasInputFromPort('preserve_scalar_type') :
      preserve_scalar_type = self.getInputFromPort('preserve_scalar_type')
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    Input_Matrix = 0
    if self.hasInputFromPort('Input Matrix') :
      Input_Matrix = self.getInputFromPort('Input Matrix')
    results = sr_py.SwapFieldDataWithMatrixEntries(Input_Field,Input_Matrix,preserve_scalar_type)
    self.setResult('Output Field', sr_py.read_at_index(results,0))
    self.setResult('Output Matrix', sr_py.read_at_index(results,1))

class SCIRun_SelectFieldROIWithBoxWidget(Module) :
  def compute(self) :
    stampvalue = 100
    if self.hasInputFromPort('stampvalue') :
      stampvalue = self.getInputFromPort('stampvalue')
    runmode = 0
    if self.hasInputFromPort('runmode') :
      runmode = self.getInputFromPort('runmode')
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    results = sr_py.SelectFieldROIWithBoxWidget(Input_Field,stampvalue,runmode)
    self.setResult('Selection Widget', sr_py.read_at_index(results,0))
    self.setResult('Output Field', sr_py.read_at_index(results,1))

class SCIRun_SetTetVolFieldDataValues(Module) :
  def compute(self) :
    newval = 1.0
    if self.hasInputFromPort('newval') :
      newval = self.getInputFromPort('newval')
    InField = 0
    if self.hasInputFromPort('InField') :
      InField = self.getInputFromPort('InField')
    results = sr_py.SetTetVolFieldDataValues(InField,newval)
    self.setResult('OutField', results)

class SCIRun_WritePath(Module) :
  def compute(self) :
    filetype = 'Binary'
    if self.hasInputFromPort('filetype') :
      filetype = self.getInputFromPort('filetype')
    confirm = 0
    if self.hasInputFromPort('confirm') :
      confirm = self.getInputFromPort('confirm')
    confirm_once = 0
    if self.hasInputFromPort('confirm_once') :
      confirm_once = self.getInputFromPort('confirm_once')
    Input_Data = 0
    if self.hasInputFromPort('Input Data') :
      Input_Data = self.getInputFromPort('Input Data')
    Filename = 0
    if self.hasInputFromPort('Filename') :
      Filename = self.getInputFromPort('Filename')
    results = sr_py.WritePath(Input_Data,Filename,filetype,confirm,confirm_once)

class SCIRun_ClipLatVolByIndicesOrWidget(Module) :
  def compute(self) :
    use_text_bbox = 0
    if self.hasInputFromPort('use_text_bbox') :
      use_text_bbox = self.getInputFromPort('use_text_bbox')
    text_min_x = 0.0
    if self.hasInputFromPort('text_min_x') :
      text_min_x = self.getInputFromPort('text_min_x')
    text_min_y = 0.0
    if self.hasInputFromPort('text_min_y') :
      text_min_y = self.getInputFromPort('text_min_y')
    text_min_z = 0.0
    if self.hasInputFromPort('text_min_z') :
      text_min_z = self.getInputFromPort('text_min_z')
    text_max_x = 1.0
    if self.hasInputFromPort('text_max_x') :
      text_max_x = self.getInputFromPort('text_max_x')
    text_max_y = 1.0
    if self.hasInputFromPort('text_max_y') :
      text_max_y = self.getInputFromPort('text_max_y')
    text_max_z = 1.0
    if self.hasInputFromPort('text_max_z') :
      text_max_z = self.getInputFromPort('text_max_z')
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    results = sr_py.ClipLatVolByIndicesOrWidget(Input_Field,use_text_bbox,text_min_x,text_min_y,text_min_z,text_max_x,text_max_y,text_max_z)
    self.setResult('Selection Widget', sr_py.read_at_index(results,0))
    self.setResult('Output Field', sr_py.read_at_index(results,1))
    self.setResult('MaskVector', sr_py.read_at_index(results,2))

class SCIRun_GetBundlesFromBundle(Module) :
  def compute(self) :
    bundle1_name = 'bundle1'
    if self.hasInputFromPort('bundle1_name') :
      bundle1_name = self.getInputFromPort('bundle1_name')
    bundle2_name = 'bundle2'
    if self.hasInputFromPort('bundle2_name') :
      bundle2_name = self.getInputFromPort('bundle2_name')
    bundle3_name = 'bundle3'
    if self.hasInputFromPort('bundle3_name') :
      bundle3_name = self.getInputFromPort('bundle3_name')
    bundle4_name = 'bundle4'
    if self.hasInputFromPort('bundle4_name') :
      bundle4_name = self.getInputFromPort('bundle4_name')
    bundle5_name = 'bundle5'
    if self.hasInputFromPort('bundle5_name') :
      bundle5_name = self.getInputFromPort('bundle5_name')
    bundle6_name = 'bundle6'
    if self.hasInputFromPort('bundle6_name') :
      bundle6_name = self.getInputFromPort('bundle6_name')
    bundle_selection = ''
    if self.hasInputFromPort('bundle_selection') :
      bundle_selection = self.getInputFromPort('bundle_selection')
    bundle = 0
    if self.hasInputFromPort('bundle') :
      bundle = self.getInputFromPort('bundle')
    results = sr_py.GetBundlesFromBundle(bundle,bundle1_name,bundle2_name,bundle3_name,bundle4_name,bundle5_name,bundle6_name,bundle_selection)
    self.setResult('bundle', sr_py.read_at_index(results,0))
    self.setResult('bundle1', sr_py.read_at_index(results,1))
    self.setResult('bundle2', sr_py.read_at_index(results,2))
    self.setResult('bundle3', sr_py.read_at_index(results,3))
    self.setResult('bundle4', sr_py.read_at_index(results,4))
    self.setResult('bundle5', sr_py.read_at_index(results,5))
    self.setResult('bundle6', sr_py.read_at_index(results,6))

class SCIRun_RescaleColorMap(Module) :
  def compute(self) :
    main_frame = ''
    if self.hasInputFromPort('main_frame') :
      main_frame = self.getInputFromPort('main_frame')
    isFixed = 0
    if self.hasInputFromPort('isFixed') :
      isFixed = self.getInputFromPort('isFixed')
    min = 0.0
    if self.hasInputFromPort('min') :
      min = self.getInputFromPort('min')
    max = 1.0
    if self.hasInputFromPort('max') :
      max = self.getInputFromPort('max')
    makeSymmetric = 0
    if self.hasInputFromPort('makeSymmetric') :
      makeSymmetric = self.getInputFromPort('makeSymmetric')
    ColorMap = 0
    if self.hasInputFromPort('ColorMap') :
      ColorMap = self.getInputFromPort('ColorMap')
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    results = sr_py.RescaleColorMap(ColorMap,Field,main_frame,isFixed,min,max,makeSymmetric)
    self.setResult('ColorMap', results)

class SCIRun_ConvertNrrdsToTexture(Module) :
  def compute(self) :
    vmin = 0.0
    if self.hasInputFromPort('vmin') :
      vmin = self.getInputFromPort('vmin')
    vmax = 1.0
    if self.hasInputFromPort('vmax') :
      vmax = self.getInputFromPort('vmax')
    gmin = 0.0
    if self.hasInputFromPort('gmin') :
      gmin = self.getInputFromPort('gmin')
    gmax = 1.0
    if self.hasInputFromPort('gmax') :
      gmax = self.getInputFromPort('gmax')
    mmin = 0.0
    if self.hasInputFromPort('mmin') :
      mmin = self.getInputFromPort('mmin')
    mmax = 1.0
    if self.hasInputFromPort('mmax') :
      mmax = self.getInputFromPort('mmax')
    is_fixed = 0
    if self.hasInputFromPort('is_fixed') :
      is_fixed = self.getInputFromPort('is_fixed')
    card_mem = 16
    if self.hasInputFromPort('card_mem') :
      card_mem = self.getInputFromPort('card_mem')
    card_mem_auto = 1
    if self.hasInputFromPort('card_mem_auto') :
      card_mem_auto = self.getInputFromPort('card_mem_auto')
    is_uchar = 1
    if self.hasInputFromPort('is_uchar') :
      is_uchar = self.getInputFromPort('is_uchar')
    histogram = 1
    if self.hasInputFromPort('histogram') :
      histogram = self.getInputFromPort('histogram')
    gamma = 0.5
    if self.hasInputFromPort('gamma') :
      gamma = self.getInputFromPort('gamma')
    Value_Nrrd = 0
    if self.hasInputFromPort('Value Nrrd') :
      Value_Nrrd = self.getInputFromPort('Value Nrrd')
    Gradient_Magnitude_Nrrd = 0
    if self.hasInputFromPort('Gradient Magnitude Nrrd') :
      Gradient_Magnitude_Nrrd = self.getInputFromPort('Gradient Magnitude Nrrd')
    results = sr_py.ConvertNrrdsToTexture(Value_Nrrd,Gradient_Magnitude_Nrrd,vmin,vmax,gmin,gmax,mmin,mmax,is_fixed,card_mem,card_mem_auto,is_uchar,histogram,gamma)
    self.setResult('Texture', sr_py.read_at_index(results,0))
    self.setResult('JointHistoGram', sr_py.read_at_index(results,1))

class SCIRun_ConvertQuadSurfToTriSurf(Module) :
  def compute(self) :
    QuadSurf = 0
    if self.hasInputFromPort('QuadSurf') :
      QuadSurf = self.getInputFromPort('QuadSurf')
    results = sr_py.ConvertQuadSurfToTriSurf(QuadSurf)
    self.setResult('TriSurf', results)

class SCIRun_WriteColorMap2D(Module) :
  def compute(self) :
    filetype = 'Binary'
    if self.hasInputFromPort('filetype') :
      filetype = self.getInputFromPort('filetype')
    confirm = 0
    if self.hasInputFromPort('confirm') :
      confirm = self.getInputFromPort('confirm')
    confirm_once = 0
    if self.hasInputFromPort('confirm_once') :
      confirm_once = self.getInputFromPort('confirm_once')
    exporttype = ''
    if self.hasInputFromPort('exporttype') :
      exporttype = self.getInputFromPort('exporttype')
    Input_Data = 0
    if self.hasInputFromPort('Input Data') :
      Input_Data = self.getInputFromPort('Input Data')
    Filename = 0
    if self.hasInputFromPort('Filename') :
      Filename = self.getInputFromPort('Filename')
    results = sr_py.WriteColorMap2D(Input_Data,Filename,filetype,confirm,confirm_once,exporttype)

class SCIRun_BuildMatrixOfSurfaceNormals(Module) :
  def compute(self) :
    Surface_Field = 0
    if self.hasInputFromPort('Surface Field') :
      Surface_Field = self.getInputFromPort('Surface Field')
    results = sr_py.BuildMatrixOfSurfaceNormals(Surface_Field)
    self.setResult('Nodal Surface Normals', results)

class SCIRun_ReadHDF5File(Module) :
  def compute(self) :
    have_HDF5 = 0
    if self.hasInputFromPort('have_HDF5') :
      have_HDF5 = self.getInputFromPort('have_HDF5')
    power_app = 0
    if self.hasInputFromPort('power_app') :
      power_app = self.getInputFromPort('power_app')
    datasets = ''
    if self.hasInputFromPort('datasets') :
      datasets = self.getInputFromPort('datasets')
    dumpname = ''
    if self.hasInputFromPort('dumpname') :
      dumpname = self.getInputFromPort('dumpname')
    ports = ''
    if self.hasInputFromPort('ports') :
      ports = self.getInputFromPort('ports')
    ndims = 0
    if self.hasInputFromPort('ndims') :
      ndims = self.getInputFromPort('ndims')
    mergeData = 1
    if self.hasInputFromPort('mergeData') :
      mergeData = self.getInputFromPort('mergeData')
    assumeSVT = 1
    if self.hasInputFromPort('assumeSVT') :
      assumeSVT = self.getInputFromPort('assumeSVT')
    animate = 0
    if self.hasInputFromPort('animate') :
      animate = self.getInputFromPort('animate')
    animate_tab = ''
    if self.hasInputFromPort('animate_tab') :
      animate_tab = self.getInputFromPort('animate_tab')
    basic_tab = ''
    if self.hasInputFromPort('basic_tab') :
      basic_tab = self.getInputFromPort('basic_tab')
    extended_tab = ''
    if self.hasInputFromPort('extended_tab') :
      extended_tab = self.getInputFromPort('extended_tab')
    playmode_tab = ''
    if self.hasInputFromPort('playmode_tab') :
      playmode_tab = self.getInputFromPort('playmode_tab')
    selectable_min = 0
    if self.hasInputFromPort('selectable_min') :
      selectable_min = self.getInputFromPort('selectable_min')
    selectable_max = 100
    if self.hasInputFromPort('selectable_max') :
      selectable_max = self.getInputFromPort('selectable_max')
    selectable_inc = 1
    if self.hasInputFromPort('selectable_inc') :
      selectable_inc = self.getInputFromPort('selectable_inc')
    range_min = 0
    if self.hasInputFromPort('range_min') :
      range_min = self.getInputFromPort('range_min')
    range_max = 0
    if self.hasInputFromPort('range_max') :
      range_max = self.getInputFromPort('range_max')
    playmode = 'once'
    if self.hasInputFromPort('playmode') :
      playmode = self.getInputFromPort('playmode')
    current = 0
    if self.hasInputFromPort('current') :
      current = self.getInputFromPort('current')
    execmode = 'init'
    if self.hasInputFromPort('execmode') :
      execmode = self.getInputFromPort('execmode')
    delay = 0
    if self.hasInputFromPort('delay') :
      delay = self.getInputFromPort('delay')
    inc_amount = 1
    if self.hasInputFromPort('inc_amount') :
      inc_amount = self.getInputFromPort('inc_amount')
    update_type = 'On Release'
    if self.hasInputFromPort('update_type') :
      update_type = self.getInputFromPort('update_type')
    have_group = 0
    if self.hasInputFromPort('have_group') :
      have_group = self.getInputFromPort('have_group')
    have_attributes = 0
    if self.hasInputFromPort('have_attributes') :
      have_attributes = self.getInputFromPort('have_attributes')
    have_datasets = 0
    if self.hasInputFromPort('have_datasets') :
      have_datasets = self.getInputFromPort('have_datasets')
    continuous = 0
    if self.hasInputFromPort('continuous') :
      continuous = self.getInputFromPort('continuous')
    selectionString = ''
    if self.hasInputFromPort('selectionString') :
      selectionString = self.getInputFromPort('selectionString')
    regexp = 0
    if self.hasInputFromPort('regexp') :
      regexp = self.getInputFromPort('regexp')
    allow_selection = 'true'
    if self.hasInputFromPort('allow_selection') :
      allow_selection = self.getInputFromPort('allow_selection')
    read_error = 0
    if self.hasInputFromPort('read_error') :
      read_error = self.getInputFromPort('read_error')
    max_dims = 6
    if self.hasInputFromPort('max_dims') :
      max_dims = self.getInputFromPort('max_dims')
    a0_dim = 2
    if self.hasInputFromPort('a0_dim') :
      a0_dim = self.getInputFromPort('a0_dim')
    a0_start = 0
    if self.hasInputFromPort('a0_start') :
      a0_start = self.getInputFromPort('a0_start')
    a0_start2 = 0
    if self.hasInputFromPort('a0_start2') :
      a0_start2 = self.getInputFromPort('a0_start2')
    a0_count = 1
    if self.hasInputFromPort('a0_count') :
      a0_count = self.getInputFromPort('a0_count')
    a0_count2 = 1
    if self.hasInputFromPort('a0_count2') :
      a0_count2 = self.getInputFromPort('a0_count2')
    a0_stride = 1
    if self.hasInputFromPort('a0_stride') :
      a0_stride = self.getInputFromPort('a0_stride')
    a0_stride2 = 1
    if self.hasInputFromPort('a0_stride2') :
      a0_stride2 = self.getInputFromPort('a0_stride2')
    a1_dim = 2
    if self.hasInputFromPort('a1_dim') :
      a1_dim = self.getInputFromPort('a1_dim')
    a1_start = 0
    if self.hasInputFromPort('a1_start') :
      a1_start = self.getInputFromPort('a1_start')
    a1_start2 = 0
    if self.hasInputFromPort('a1_start2') :
      a1_start2 = self.getInputFromPort('a1_start2')
    a1_count = 1
    if self.hasInputFromPort('a1_count') :
      a1_count = self.getInputFromPort('a1_count')
    a1_count2 = 1
    if self.hasInputFromPort('a1_count2') :
      a1_count2 = self.getInputFromPort('a1_count2')
    a1_stride = 1
    if self.hasInputFromPort('a1_stride') :
      a1_stride = self.getInputFromPort('a1_stride')
    a1_stride2 = 1
    if self.hasInputFromPort('a1_stride2') :
      a1_stride2 = self.getInputFromPort('a1_stride2')
    a2_dim = 2
    if self.hasInputFromPort('a2_dim') :
      a2_dim = self.getInputFromPort('a2_dim')
    a2_start = 0
    if self.hasInputFromPort('a2_start') :
      a2_start = self.getInputFromPort('a2_start')
    a2_start2 = 0
    if self.hasInputFromPort('a2_start2') :
      a2_start2 = self.getInputFromPort('a2_start2')
    a2_count = 1
    if self.hasInputFromPort('a2_count') :
      a2_count = self.getInputFromPort('a2_count')
    a2_count2 = 1
    if self.hasInputFromPort('a2_count2') :
      a2_count2 = self.getInputFromPort('a2_count2')
    a2_stride = 1
    if self.hasInputFromPort('a2_stride') :
      a2_stride = self.getInputFromPort('a2_stride')
    a2_stride2 = 1
    if self.hasInputFromPort('a2_stride2') :
      a2_stride2 = self.getInputFromPort('a2_stride2')
    a3_dim = 2
    if self.hasInputFromPort('a3_dim') :
      a3_dim = self.getInputFromPort('a3_dim')
    a3_start = 0
    if self.hasInputFromPort('a3_start') :
      a3_start = self.getInputFromPort('a3_start')
    a3_start2 = 0
    if self.hasInputFromPort('a3_start2') :
      a3_start2 = self.getInputFromPort('a3_start2')
    a3_count = 1
    if self.hasInputFromPort('a3_count') :
      a3_count = self.getInputFromPort('a3_count')
    a3_count2 = 1
    if self.hasInputFromPort('a3_count2') :
      a3_count2 = self.getInputFromPort('a3_count2')
    a3_stride = 1
    if self.hasInputFromPort('a3_stride') :
      a3_stride = self.getInputFromPort('a3_stride')
    a3_stride2 = 1
    if self.hasInputFromPort('a3_stride2') :
      a3_stride2 = self.getInputFromPort('a3_stride2')
    a4_dim = 2
    if self.hasInputFromPort('a4_dim') :
      a4_dim = self.getInputFromPort('a4_dim')
    a4_start = 0
    if self.hasInputFromPort('a4_start') :
      a4_start = self.getInputFromPort('a4_start')
    a4_start2 = 0
    if self.hasInputFromPort('a4_start2') :
      a4_start2 = self.getInputFromPort('a4_start2')
    a4_count = 1
    if self.hasInputFromPort('a4_count') :
      a4_count = self.getInputFromPort('a4_count')
    a4_count2 = 1
    if self.hasInputFromPort('a4_count2') :
      a4_count2 = self.getInputFromPort('a4_count2')
    a4_stride = 1
    if self.hasInputFromPort('a4_stride') :
      a4_stride = self.getInputFromPort('a4_stride')
    a4_stride2 = 1
    if self.hasInputFromPort('a4_stride2') :
      a4_stride2 = self.getInputFromPort('a4_stride2')
    a5_dim = 2
    if self.hasInputFromPort('a5_dim') :
      a5_dim = self.getInputFromPort('a5_dim')
    a5_start = 0
    if self.hasInputFromPort('a5_start') :
      a5_start = self.getInputFromPort('a5_start')
    a5_start2 = 0
    if self.hasInputFromPort('a5_start2') :
      a5_start2 = self.getInputFromPort('a5_start2')
    a5_count = 1
    if self.hasInputFromPort('a5_count') :
      a5_count = self.getInputFromPort('a5_count')
    a5_count2 = 1
    if self.hasInputFromPort('a5_count2') :
      a5_count2 = self.getInputFromPort('a5_count2')
    a5_stride = 1
    if self.hasInputFromPort('a5_stride') :
      a5_stride = self.getInputFromPort('a5_stride')
    a5_stride2 = 1
    if self.hasInputFromPort('a5_stride2') :
      a5_stride2 = self.getInputFromPort('a5_stride2')
    Full_filename = 0
    if self.hasInputFromPort('Full filename') :
      Full_filename = self.getInputFromPort('Full filename')
    Current_Index = 0
    if self.hasInputFromPort('Current Index') :
      Current_Index = self.getInputFromPort('Current Index')
    results = sr_py.ReadHDF5File(Full_filename,Current_Index,have_HDF5,power_app,datasets,dumpname,ports,ndims,mergeData,assumeSVT,animate,animate_tab,basic_tab,extended_tab,playmode_tab,selectable_min,selectable_max,selectable_inc,range_min,range_max,playmode,current,execmode,delay,inc_amount,update_type,have_group,have_attributes,have_datasets,continuous,selectionString,regexp,allow_selection,read_error,max_dims,a0_dim,a0_start,a0_start2,a0_count,a0_count2,a0_stride,a0_stride2,a1_dim,a1_start,a1_start2,a1_count,a1_count2,a1_stride,a1_stride2,a2_dim,a2_start,a2_start2,a2_count,a2_count2,a2_stride,a2_stride2,a3_dim,a3_start,a3_start2,a3_count,a3_count2,a3_stride,a3_stride2,a4_dim,a4_start,a4_start2,a4_count,a4_count2,a4_stride,a4_stride2,a5_dim,a5_start,a5_start2,a5_count,a5_count2,a5_stride,a5_stride2)
    self.setResult('Output 0 Nrrd', sr_py.read_at_index(results,0))
    self.setResult('Output 1 Nrrd', sr_py.read_at_index(results,1))
    self.setResult('Output 2 Nrrd', sr_py.read_at_index(results,2))
    self.setResult('Output 3 Nrrd', sr_py.read_at_index(results,3))
    self.setResult('Output 4 Nrrd', sr_py.read_at_index(results,4))
    self.setResult('Output 5 Nrrd', sr_py.read_at_index(results,5))
    self.setResult('Output 6 Nrrd', sr_py.read_at_index(results,6))
    self.setResult('Output 7 Nrrd', sr_py.read_at_index(results,7))
    self.setResult('Selected Index', sr_py.read_at_index(results,8))

class SCIRun_GetPathsFromBundle(Module) :
  def compute(self) :
    path1_name = 'path1'
    if self.hasInputFromPort('path1_name') :
      path1_name = self.getInputFromPort('path1_name')
    path2_name = 'path2'
    if self.hasInputFromPort('path2_name') :
      path2_name = self.getInputFromPort('path2_name')
    path3_name = 'path3'
    if self.hasInputFromPort('path3_name') :
      path3_name = self.getInputFromPort('path3_name')
    path4_name = 'path4'
    if self.hasInputFromPort('path4_name') :
      path4_name = self.getInputFromPort('path4_name')
    path5_name = 'path5'
    if self.hasInputFromPort('path5_name') :
      path5_name = self.getInputFromPort('path5_name')
    path6_name = 'path6'
    if self.hasInputFromPort('path6_name') :
      path6_name = self.getInputFromPort('path6_name')
    path_selection = ''
    if self.hasInputFromPort('path_selection') :
      path_selection = self.getInputFromPort('path_selection')
    bundle = 0
    if self.hasInputFromPort('bundle') :
      bundle = self.getInputFromPort('bundle')
    results = sr_py.GetPathsFromBundle(bundle,path1_name,path2_name,path3_name,path4_name,path5_name,path6_name,path_selection)
    self.setResult('bundle', sr_py.read_at_index(results,0))
    self.setResult('path1', sr_py.read_at_index(results,1))
    self.setResult('path2', sr_py.read_at_index(results,2))
    self.setResult('path3', sr_py.read_at_index(results,3))
    self.setResult('path4', sr_py.read_at_index(results,4))
    self.setResult('path5', sr_py.read_at_index(results,5))
    self.setResult('path6', sr_py.read_at_index(results,6))

class SCIRun_GetFieldBoundary(Module) :
  def compute(self) :
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    results = sr_py.GetFieldBoundary(Field)
    self.setResult('BoundaryField', sr_py.read_at_index(results,0))
    self.setResult('Mapping', sr_py.read_at_index(results,1))

class SCIRun_TransformMeshWithFunction(Module) :
  def compute(self) :
    function = 'result = Vector(x,y,z) * Vector(1.0, 2.0, 3.0);'
    if self.hasInputFromPort('function') :
      function = self.getInputFromPort('function')
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    results = sr_py.TransformMeshWithFunction(Input_Field,function)
    self.setResult('Output Field', results)

class SCIRun_ConvertMatricesToMesh(Module) :
  def compute(self) :
    fieldname = 'Created Field'
    if self.hasInputFromPort('fieldname') :
      fieldname = self.getInputFromPort('fieldname')
    meshname = 'Created Mesh'
    if self.hasInputFromPort('meshname') :
      meshname = self.getInputFromPort('meshname')
    fieldbasetype = 'TetVolField'
    if self.hasInputFromPort('fieldbasetype') :
      fieldbasetype = self.getInputFromPort('fieldbasetype')
    datatype = 'double'
    if self.hasInputFromPort('datatype') :
      datatype = self.getInputFromPort('datatype')
    Mesh_Elements = 0
    if self.hasInputFromPort('Mesh Elements') :
      Mesh_Elements = self.getInputFromPort('Mesh Elements')
    Mesh_Positions = 0
    if self.hasInputFromPort('Mesh Positions') :
      Mesh_Positions = self.getInputFromPort('Mesh Positions')
    Mesh_Normals = 0
    if self.hasInputFromPort('Mesh Normals') :
      Mesh_Normals = self.getInputFromPort('Mesh Normals')
    results = sr_py.ConvertMatricesToMesh(Mesh_Elements,Mesh_Positions,Mesh_Normals,fieldname,meshname,fieldbasetype,datatype)
    self.setResult('Output Field', results)

class SCIRun_ReportFieldInfo(Module) :
  def compute(self) :
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    results = sr_py.ReportFieldInfo(Input_Field)
    self.setResult('NumNodes', sr_py.read_at_index(results,0))
    self.setResult('NumElements', sr_py.read_at_index(results,1))
    self.setResult('NumData', sr_py.read_at_index(results,2))
    self.setResult('DataMin', sr_py.read_at_index(results,3))
    self.setResult('DataMax', sr_py.read_at_index(results,4))
    self.setResult('FieldSize', sr_py.read_at_index(results,5))
    self.setResult('FieldCenter', sr_py.read_at_index(results,6))
    self.setResult('Dimensions', sr_py.read_at_index(results,7))

class SCIRun_ConvertFieldsToTexture(Module) :
  def compute(self) :
    vmin = 0.0
    if self.hasInputFromPort('vmin') :
      vmin = self.getInputFromPort('vmin')
    vmax = 1.0
    if self.hasInputFromPort('vmax') :
      vmax = self.getInputFromPort('vmax')
    gmin = 0.0
    if self.hasInputFromPort('gmin') :
      gmin = self.getInputFromPort('gmin')
    gmax = 1.0
    if self.hasInputFromPort('gmax') :
      gmax = self.getInputFromPort('gmax')
    is_fixed = 0
    if self.hasInputFromPort('is_fixed') :
      is_fixed = self.getInputFromPort('is_fixed')
    card_mem = 16
    if self.hasInputFromPort('card_mem') :
      card_mem = self.getInputFromPort('card_mem')
    card_mem_auto = 1
    if self.hasInputFromPort('card_mem_auto') :
      card_mem_auto = self.getInputFromPort('card_mem_auto')
    histogram = 1
    if self.hasInputFromPort('histogram') :
      histogram = self.getInputFromPort('histogram')
    gamma = 0.5
    if self.hasInputFromPort('gamma') :
      gamma = self.getInputFromPort('gamma')
    Value_Field = 0
    if self.hasInputFromPort('Value Field') :
      Value_Field = self.getInputFromPort('Value Field')
    Gradient_Magnitude_Field = 0
    if self.hasInputFromPort('Gradient Magnitude Field') :
      Gradient_Magnitude_Field = self.getInputFromPort('Gradient Magnitude Field')
    results = sr_py.ConvertFieldsToTexture(Value_Field,Gradient_Magnitude_Field,vmin,vmax,gmin,gmax,is_fixed,card_mem,card_mem_auto,histogram,gamma)
    self.setResult('Texture', sr_py.read_at_index(results,0))
    self.setResult('JointHistoGram', sr_py.read_at_index(results,1))

class SCIRun_PrintHelloWorldToScreen(Module) :
  def compute(self) :
    results = sr_py.PrintHelloWorldToScreen()

class SCIRun_MapFieldDataFromSourceToDestination(Module) :
  def compute(self) :
    interpolation_basis = 'linear'
    if self.hasInputFromPort('interpolation_basis') :
      interpolation_basis = self.getInputFromPort('interpolation_basis')
    map_source_to_single_dest = 0
    if self.hasInputFromPort('map_source_to_single_dest') :
      map_source_to_single_dest = self.getInputFromPort('map_source_to_single_dest')
    exhaustive_search = 0
    if self.hasInputFromPort('exhaustive_search') :
      exhaustive_search = self.getInputFromPort('exhaustive_search')
    exhaustive_search_max_dist = -1.0
    if self.hasInputFromPort('exhaustive_search_max_dist') :
      exhaustive_search_max_dist = self.getInputFromPort('exhaustive_search_max_dist')
    np = 1
    if self.hasInputFromPort('np') :
      np = self.getInputFromPort('np')
    Source = 0
    if self.hasInputFromPort('Source') :
      Source = self.getInputFromPort('Source')
    Destination = 0
    if self.hasInputFromPort('Destination') :
      Destination = self.getInputFromPort('Destination')
    results = sr_py.MapFieldDataFromSourceToDestination(Source,Destination,interpolation_basis,map_source_to_single_dest,exhaustive_search,exhaustive_search_max_dist,np)
    self.setResult('Remapped Destination', results)

class SCIRun_ConvertLatVolDataFromElemToNode(Module) :
  def compute(self) :
    Elem_Field = 0
    if self.hasInputFromPort('Elem Field') :
      Elem_Field = self.getInputFromPort('Elem Field')
    results = sr_py.ConvertLatVolDataFromElemToNode(Elem_Field)
    self.setResult('Node Field', results)

class SCIRun_CreateGeometricTransform(Module) :
  def compute(self) :
    rotate_x = 0
    if self.hasInputFromPort('rotate_x') :
      rotate_x = self.getInputFromPort('rotate_x')
    rotate_y = 0
    if self.hasInputFromPort('rotate_y') :
      rotate_y = self.getInputFromPort('rotate_y')
    rotate_z = 1
    if self.hasInputFromPort('rotate_z') :
      rotate_z = self.getInputFromPort('rotate_z')
    rotate_theta = 0
    if self.hasInputFromPort('rotate_theta') :
      rotate_theta = self.getInputFromPort('rotate_theta')
    translate_x = 0
    if self.hasInputFromPort('translate_x') :
      translate_x = self.getInputFromPort('translate_x')
    translate_y = 0
    if self.hasInputFromPort('translate_y') :
      translate_y = self.getInputFromPort('translate_y')
    translate_z = 0
    if self.hasInputFromPort('translate_z') :
      translate_z = self.getInputFromPort('translate_z')
    scale_uniform = 0
    if self.hasInputFromPort('scale_uniform') :
      scale_uniform = self.getInputFromPort('scale_uniform')
    scale_x = 0
    if self.hasInputFromPort('scale_x') :
      scale_x = self.getInputFromPort('scale_x')
    scale_y = 0
    if self.hasInputFromPort('scale_y') :
      scale_y = self.getInputFromPort('scale_y')
    scale_z = 0
    if self.hasInputFromPort('scale_z') :
      scale_z = self.getInputFromPort('scale_z')
    shear_plane_a = 0
    if self.hasInputFromPort('shear_plane_a') :
      shear_plane_a = self.getInputFromPort('shear_plane_a')
    shear_plane_b = 0
    if self.hasInputFromPort('shear_plane_b') :
      shear_plane_b = self.getInputFromPort('shear_plane_b')
    shear_plane_c = 1
    if self.hasInputFromPort('shear_plane_c') :
      shear_plane_c = self.getInputFromPort('shear_plane_c')
    widget_resizable = 1
    if self.hasInputFromPort('widget_resizable') :
      widget_resizable = self.getInputFromPort('widget_resizable')
    permute_x = 1
    if self.hasInputFromPort('permute_x') :
      permute_x = self.getInputFromPort('permute_x')
    permute_y = 2
    if self.hasInputFromPort('permute_y') :
      permute_y = self.getInputFromPort('permute_y')
    permute_z = 3
    if self.hasInputFromPort('permute_z') :
      permute_z = self.getInputFromPort('permute_z')
    pre_transform = 1
    if self.hasInputFromPort('pre_transform') :
      pre_transform = self.getInputFromPort('pre_transform')
    which_transform = 'translate'
    if self.hasInputFromPort('which_transform') :
      which_transform = self.getInputFromPort('which_transform')
    widget_scale = 1
    if self.hasInputFromPort('widget_scale') :
      widget_scale = self.getInputFromPort('widget_scale')
    ignoring_widget_changes = 1
    if self.hasInputFromPort('ignoring_widget_changes') :
      ignoring_widget_changes = self.getInputFromPort('ignoring_widget_changes')
    Matrix = 0
    if self.hasInputFromPort('Matrix') :
      Matrix = self.getInputFromPort('Matrix')
    results = sr_py.CreateGeometricTransform(Matrix,rotate_x,rotate_y,rotate_z,rotate_theta,translate_x,translate_y,translate_z,scale_uniform,scale_x,scale_y,scale_z,shear_plane_a,shear_plane_b,shear_plane_c,widget_resizable,permute_x,permute_y,permute_z,pre_transform,which_transform,widget_scale,ignoring_widget_changes)
    self.setResult('Matrix', sr_py.read_at_index(results,0))
    self.setResult('Geometry', sr_py.read_at_index(results,1))

class SCIRun_CalculateNodeNormals(Module) :
  def compute(self) :
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    Input_Point = 0
    if self.hasInputFromPort('Input Point') :
      Input_Point = self.getInputFromPort('Input Point')
    results = sr_py.CalculateNodeNormals(Input_Field,Input_Point)
    self.setResult('Output Field', results)

class SCIRun_ReportFieldGeometryMeasures(Module) :
  def compute(self) :
    simplexString = 'Node'
    if self.hasInputFromPort('simplexString') :
      simplexString = self.getInputFromPort('simplexString')
    xFlag = 1
    if self.hasInputFromPort('xFlag') :
      xFlag = self.getInputFromPort('xFlag')
    yFlag = 1
    if self.hasInputFromPort('yFlag') :
      yFlag = self.getInputFromPort('yFlag')
    zFlag = 1
    if self.hasInputFromPort('zFlag') :
      zFlag = self.getInputFromPort('zFlag')
    idxFlag = 0
    if self.hasInputFromPort('idxFlag') :
      idxFlag = self.getInputFromPort('idxFlag')
    sizeFlag = 0
    if self.hasInputFromPort('sizeFlag') :
      sizeFlag = self.getInputFromPort('sizeFlag')
    normalsFlag = 0
    if self.hasInputFromPort('normalsFlag') :
      normalsFlag = self.getInputFromPort('normalsFlag')
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    results = sr_py.ReportFieldGeometryMeasures(Input_Field,simplexString,xFlag,yFlag,zFlag,idxFlag,sizeFlag,normalsFlag)
    self.setResult('Output Measures Matrix', results)

class SCIRun_CalculateVectorMagnitudes(Module) :
  def compute(self) :
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    results = sr_py.CalculateVectorMagnitudes(Input_Field)
    self.setResult('Output CalculateVectorMagnitudes', results)

class SCIRun_GetInputField(Module) :
  def compute(self) :
    InField = 0
    if self.hasInputFromPort('InField') :
      InField = self.getInputFromPort('InField')
    results = sr_py.GetInputField(InField)

class SCIRun_ChooseMatrix(Module) :
  def compute(self) :
    use_first_valid = 1
    if self.hasInputFromPort('use_first_valid') :
      use_first_valid = self.getInputFromPort('use_first_valid')
    port_valid_index = 0
    if self.hasInputFromPort('port_valid_index') :
      port_valid_index = self.getInputFromPort('port_valid_index')
    port_selected_index = 0
    if self.hasInputFromPort('port_selected_index') :
      port_selected_index = self.getInputFromPort('port_selected_index')
    Matrix = 0
    if self.hasInputFromPort('Matrix') :
      Matrix = self.getInputFromPort('Matrix')
    results = sr_py.ChooseMatrix(Matrix,use_first_valid,port_valid_index,port_selected_index)
    self.setResult('Matrix', results)

class SCIRun_ClipFieldToFieldOrWidget(Module) :
  def compute(self) :
    clip_location = 'cell'
    if self.hasInputFromPort('clip_location') :
      clip_location = self.getInputFromPort('clip_location')
    clipmode = 'replace'
    if self.hasInputFromPort('clipmode') :
      clipmode = self.getInputFromPort('clipmode')
    autoexecute = 0
    if self.hasInputFromPort('autoexecute') :
      autoexecute = self.getInputFromPort('autoexecute')
    autoinvert = 0
    if self.hasInputFromPort('autoinvert') :
      autoinvert = self.getInputFromPort('autoinvert')
    execmode = 0
    if self.hasInputFromPort('execmode') :
      execmode = self.getInputFromPort('execmode')
    center_x = -1.0
    if self.hasInputFromPort('center_x') :
      center_x = self.getInputFromPort('center_x')
    center_y = -1.0
    if self.hasInputFromPort('center_y') :
      center_y = self.getInputFromPort('center_y')
    center_z = -1.0
    if self.hasInputFromPort('center_z') :
      center_z = self.getInputFromPort('center_z')
    right_x = -1.0
    if self.hasInputFromPort('right_x') :
      right_x = self.getInputFromPort('right_x')
    right_y = -1.0
    if self.hasInputFromPort('right_y') :
      right_y = self.getInputFromPort('right_y')
    right_z = -1.0
    if self.hasInputFromPort('right_z') :
      right_z = self.getInputFromPort('right_z')
    down_x = -1.0
    if self.hasInputFromPort('down_x') :
      down_x = self.getInputFromPort('down_x')
    down_y = -1.0
    if self.hasInputFromPort('down_y') :
      down_y = self.getInputFromPort('down_y')
    down_z = -1.0
    if self.hasInputFromPort('down_z') :
      down_z = self.getInputFromPort('down_z')
    in_x = -1.0
    if self.hasInputFromPort('in_x') :
      in_x = self.getInputFromPort('in_x')
    in_y = -1.0
    if self.hasInputFromPort('in_y') :
      in_y = self.getInputFromPort('in_y')
    in_z = -1.0
    if self.hasInputFromPort('in_z') :
      in_z = self.getInputFromPort('in_z')
    scale = -1.0
    if self.hasInputFromPort('scale') :
      scale = self.getInputFromPort('scale')
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    Clip_Field = 0
    if self.hasInputFromPort('Clip Field') :
      Clip_Field = self.getInputFromPort('Clip Field')
    results = sr_py.ClipFieldToFieldOrWidget(Input_Field,Clip_Field,clip_location,clipmode,autoexecute,autoinvert,execmode,center_x,center_y,center_z,right_x,right_y,right_z,down_x,down_y,down_z,in_x,in_y,in_z,scale)
    self.setResult('Selection Widget', sr_py.read_at_index(results,0))
    self.setResult('Output Field', sr_py.read_at_index(results,1))

class SCIRun_ConvertHexVolToTetVol(Module) :
  def compute(self) :
    HexVol = 0
    if self.hasInputFromPort('HexVol') :
      HexVol = self.getInputFromPort('HexVol')
    results = sr_py.ConvertHexVolToTetVol(HexVol)
    self.setResult('TetVol', results)

class SCIRun_SetFieldOrMeshStringProperty(Module) :
  def compute(self) :
    prop = 'units'
    if self.hasInputFromPort('prop') :
      prop = self.getInputFromPort('prop')
    val = 'cm'
    if self.hasInputFromPort('val') :
      val = self.getInputFromPort('val')
    meshprop = 1
    if self.hasInputFromPort('meshprop') :
      meshprop = self.getInputFromPort('meshprop')
    Input = 0
    if self.hasInputFromPort('Input') :
      Input = self.getInputFromPort('Input')
    results = sr_py.SetFieldOrMeshStringProperty(Input,prop,val,meshprop)
    self.setResult('Output', results)

class SCIRun_ConvertMeshCoordinateSystem(Module) :
  def compute(self) :
    oldsystem = 'Cartesian'
    if self.hasInputFromPort('oldsystem') :
      oldsystem = self.getInputFromPort('oldsystem')
    newsystem = 'Spherical'
    if self.hasInputFromPort('newsystem') :
      newsystem = self.getInputFromPort('newsystem')
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    results = sr_py.ConvertMeshCoordinateSystem(Input_Field,oldsystem,newsystem)
    self.setResult('Output Field', results)

class SCIRun_RefineMeshByIsovalue2(Module) :
  def compute(self) :
    isoval = 0.0
    if self.hasInputFromPort('isoval') :
      isoval = self.getInputFromPort('isoval')
    lte = 1
    if self.hasInputFromPort('lte') :
      lte = self.getInputFromPort('lte')
    Input = 0
    if self.hasInputFromPort('Input') :
      Input = self.getInputFromPort('Input')
    Optional_Isovalue = 0
    if self.hasInputFromPort('Optional Isovalue') :
      Optional_Isovalue = self.getInputFromPort('Optional Isovalue')
    results = sr_py.RefineMeshByIsovalue2(Input,Optional_Isovalue,isoval,lte)
    self.setResult('Refined', sr_py.read_at_index(results,0))
    self.setResult('Mapping', sr_py.read_at_index(results,1))

class SCIRun_SetTetVolFieldDataValuesToZero(Module) :
  def compute(self) :
    InField = 0
    if self.hasInputFromPort('InField') :
      InField = self.getInputFromPort('InField')
    results = sr_py.SetTetVolFieldDataValuesToZero(InField)
    self.setResult('OutField', results)

class SCIRun_ViewSlices(Module) :
  def compute(self) :
    clut_ww = 1.0
    if self.hasInputFromPort('clut_ww') :
      clut_ww = self.getInputFromPort('clut_ww')
    clut_wl = 0.0
    if self.hasInputFromPort('clut_wl') :
      clut_wl = self.getInputFromPort('clut_wl')
    probe = 0
    if self.hasInputFromPort('probe') :
      probe = self.getInputFromPort('probe')
    show_colormap2 = 0
    if self.hasInputFromPort('show_colormap2') :
      show_colormap2 = self.getInputFromPort('show_colormap2')
    painting = 0
    if self.hasInputFromPort('painting') :
      painting = self.getInputFromPort('painting')
    crop = 0
    if self.hasInputFromPort('crop') :
      crop = self.getInputFromPort('crop')
    crop_minAxis0 = 0
    if self.hasInputFromPort('crop_minAxis0') :
      crop_minAxis0 = self.getInputFromPort('crop_minAxis0')
    crop_minAxis1 = 0
    if self.hasInputFromPort('crop_minAxis1') :
      crop_minAxis1 = self.getInputFromPort('crop_minAxis1')
    crop_minAxis2 = 0
    if self.hasInputFromPort('crop_minAxis2') :
      crop_minAxis2 = self.getInputFromPort('crop_minAxis2')
    crop_maxAxis0 = 0
    if self.hasInputFromPort('crop_maxAxis0') :
      crop_maxAxis0 = self.getInputFromPort('crop_maxAxis0')
    crop_maxAxis1 = 0
    if self.hasInputFromPort('crop_maxAxis1') :
      crop_maxAxis1 = self.getInputFromPort('crop_maxAxis1')
    crop_maxAxis2 = 0
    if self.hasInputFromPort('crop_maxAxis2') :
      crop_maxAxis2 = self.getInputFromPort('crop_maxAxis2')
    crop_minPadAxis0 = 0
    if self.hasInputFromPort('crop_minPadAxis0') :
      crop_minPadAxis0 = self.getInputFromPort('crop_minPadAxis0')
    crop_minPadAxis1 = 0
    if self.hasInputFromPort('crop_minPadAxis1') :
      crop_minPadAxis1 = self.getInputFromPort('crop_minPadAxis1')
    crop_minPadAxis2 = 0
    if self.hasInputFromPort('crop_minPadAxis2') :
      crop_minPadAxis2 = self.getInputFromPort('crop_minPadAxis2')
    crop_maxPadAxis0 = 0
    if self.hasInputFromPort('crop_maxPadAxis0') :
      crop_maxPadAxis0 = self.getInputFromPort('crop_maxPadAxis0')
    crop_maxPadAxis1 = 0
    if self.hasInputFromPort('crop_maxPadAxis1') :
      crop_maxPadAxis1 = self.getInputFromPort('crop_maxPadAxis1')
    crop_maxPadAxis2 = 0
    if self.hasInputFromPort('crop_maxPadAxis2') :
      crop_maxPadAxis2 = self.getInputFromPort('crop_maxPadAxis2')
    texture_filter = 1
    if self.hasInputFromPort('texture_filter') :
      texture_filter = self.getInputFromPort('texture_filter')
    anatomical_coordinates = 1
    if self.hasInputFromPort('anatomical_coordinates') :
      anatomical_coordinates = self.getInputFromPort('anatomical_coordinates')
    show_text = 1
    if self.hasInputFromPort('show_text') :
      show_text = self.getInputFromPort('show_text')
    color_font_r = 1.0
    if self.hasInputFromPort('color_font_r') :
      color_font_r = self.getInputFromPort('color_font_r')
    color_font_g = 1.0
    if self.hasInputFromPort('color_font_g') :
      color_font_g = self.getInputFromPort('color_font_g')
    color_font_b = 1.0
    if self.hasInputFromPort('color_font_b') :
      color_font_b = self.getInputFromPort('color_font_b')
    color_font_a = 1.0
    if self.hasInputFromPort('color_font_a') :
      color_font_a = self.getInputFromPort('color_font_a')
    min = -1.0
    if self.hasInputFromPort('min') :
      min = self.getInputFromPort('min')
    max = -1.0
    if self.hasInputFromPort('max') :
      max = self.getInputFromPort('max')
    dim0 = 0
    if self.hasInputFromPort('dim0') :
      dim0 = self.getInputFromPort('dim0')
    dim1 = 0
    if self.hasInputFromPort('dim1') :
      dim1 = self.getInputFromPort('dim1')
    dim2 = 0
    if self.hasInputFromPort('dim2') :
      dim2 = self.getInputFromPort('dim2')
    geom_flushed = 0
    if self.hasInputFromPort('geom_flushed') :
      geom_flushed = self.getInputFromPort('geom_flushed')
    background_threshold = 0.0
    if self.hasInputFromPort('background_threshold') :
      background_threshold = self.getInputFromPort('background_threshold')
    gradient_threshold = 0.0
    if self.hasInputFromPort('gradient_threshold') :
      gradient_threshold = self.getInputFromPort('gradient_threshold')
    font_size = 15.0
    if self.hasInputFromPort('font_size') :
      font_size = self.getInputFromPort('font_size')
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
    results = sr_py.ViewSlices(Nrrd1,Nrrd2,Nrrd1ColorMap,Nrrd2ColorMap,InputColorMap2,NrrdGradient,clut_ww,clut_wl,probe,show_colormap2,painting,crop,crop_minAxis0,crop_minAxis1,crop_minAxis2,crop_maxAxis0,crop_maxAxis1,crop_maxAxis2,crop_minPadAxis0,crop_minPadAxis1,crop_minPadAxis2,crop_maxPadAxis0,crop_maxPadAxis1,crop_maxPadAxis2,texture_filter,anatomical_coordinates,show_text,color_font_r,color_font_g,color_font_b,color_font_a,min,max,dim0,dim1,dim2,geom_flushed,background_threshold,gradient_threshold,font_size)
    self.setResult('Geometry', sr_py.read_at_index(results,0))
    self.setResult('ColorMap2', sr_py.read_at_index(results,1))

class SCIRun_SplitVectorArrayInXYZ(Module) :
  def compute(self) :
    VectorArray = 0
    if self.hasInputFromPort('VectorArray') :
      VectorArray = self.getInputFromPort('VectorArray')
    results = sr_py.SplitVectorArrayInXYZ(VectorArray)
    self.setResult('X', sr_py.read_at_index(results,0))
    self.setResult('Y', sr_py.read_at_index(results,1))
    self.setResult('Z', sr_py.read_at_index(results,2))

class SCIRun_ConvertIndicesToFieldData(Module) :
  def compute(self) :
    outputtype = 'double'
    if self.hasInputFromPort('outputtype') :
      outputtype = self.getInputFromPort('outputtype')
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    Data = 0
    if self.hasInputFromPort('Data') :
      Data = self.getInputFromPort('Data')
    results = sr_py.ConvertIndicesToFieldData(Field,Data,outputtype)
    self.setResult('Field', results)

class SCIRun_CreateAndEditCameraPath(Module) :
  def compute(self) :
    Path = 0
    if self.hasInputFromPort('Path') :
      Path = self.getInputFromPort('Path')
    results = sr_py.CreateAndEditCameraPath(Path)
    self.setResult('Path', sr_py.read_at_index(results,0))
    self.setResult('Geometry', sr_py.read_at_index(results,1))
    self.setResult('Camera View', sr_py.read_at_index(results,2))

class SCIRun_CalculateDistanceToFieldBoundary(Module) :
  def compute(self) :
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    results = sr_py.CalculateDistanceToFieldBoundary(Field)
    self.setResult('DistanceField', results)

class SCIRun_ConvertMappingMatrixToMaskVector(Module) :
  def compute(self) :
    MappingMatrix = 0
    if self.hasInputFromPort('MappingMatrix') :
      MappingMatrix = self.getInputFromPort('MappingMatrix')
    results = sr_py.ConvertMappingMatrixToMaskVector(MappingMatrix)
    self.setResult('MaskVector', results)

class SCIRun_CreateFieldData(Module) :
  def compute(self) :
    function = 'RESULT = 1;'
    if self.hasInputFromPort('function') :
      function = self.getInputFromPort('function')
    format = 'Scalar'
    if self.hasInputFromPort('format') :
      format = self.getInputFromPort('format')
    basis = 'Linear'
    if self.hasInputFromPort('basis') :
      basis = self.getInputFromPort('basis')
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    Function = 0
    if self.hasInputFromPort('Function') :
      Function = self.getInputFromPort('Function')
    DataArray = 0
    if self.hasInputFromPort('DataArray') :
      DataArray = self.getInputFromPort('DataArray')
    results = sr_py.CreateFieldData(Field,Function,DataArray,function,format,basis)
    self.setResult('Field', results)

class SCIRun_CreateLatVol(Module) :
  def compute(self) :
    sizex = 16
    if self.hasInputFromPort('sizex') :
      sizex = self.getInputFromPort('sizex')
    sizey = 16
    if self.hasInputFromPort('sizey') :
      sizey = self.getInputFromPort('sizey')
    sizez = 16
    if self.hasInputFromPort('sizez') :
      sizez = self.getInputFromPort('sizez')
    padpercent = 0.0
    if self.hasInputFromPort('padpercent') :
      padpercent = self.getInputFromPort('padpercent')
    data_at = 'Nodes'
    if self.hasInputFromPort('data_at') :
      data_at = self.getInputFromPort('data_at')
    element_size = 'Mesh'
    if self.hasInputFromPort('element_size') :
      element_size = self.getInputFromPort('element_size')
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    LatVol_Size = 0
    if self.hasInputFromPort('LatVol Size') :
      LatVol_Size = self.getInputFromPort('LatVol Size')
    results = sr_py.CreateLatVol(Input_Field,LatVol_Size,sizex,sizey,sizez,padpercent,data_at,element_size)
    self.setResult('Output Sample Field', results)

class SCIRun_ResizeMatrix(Module) :
  def compute(self) :
    dim_m = 1
    if self.hasInputFromPort('dim_m') :
      dim_m = self.getInputFromPort('dim_m')
    dim_n = 1
    if self.hasInputFromPort('dim_n') :
      dim_n = self.getInputFromPort('dim_n')
    Matrix = 0
    if self.hasInputFromPort('Matrix') :
      Matrix = self.getInputFromPort('Matrix')
    M = 0
    if self.hasInputFromPort('M') :
      M = self.getInputFromPort('M')
    N = 0
    if self.hasInputFromPort('N') :
      N = self.getInputFromPort('N')
    results = sr_py.ResizeMatrix(Matrix,M,N,dim_m,dim_n)
    self.setResult('Matrix', results)

class SCIRun_GetInputFieldAndSendAsOutput(Module) :
  def compute(self) :
    InField = 0
    if self.hasInputFromPort('InField') :
      InField = self.getInputFromPort('InField')
    results = sr_py.GetInputFieldAndSendAsOutput(InField)
    self.setResult('OutField', results)

class SCIRun_ShowAndEditCameraWidget(Module) :
  def compute(self) :
    frame = 1
    if self.hasInputFromPort('frame') :
      frame = self.getInputFromPort('frame')
    num_frames = 100
    if self.hasInputFromPort('num_frames') :
      num_frames = self.getInputFromPort('num_frames')
    time = 0
    if self.hasInputFromPort('time') :
      time = self.getInputFromPort('time')
    playmode = 'once'
    if self.hasInputFromPort('playmode') :
      playmode = self.getInputFromPort('playmode')
    execmode = 'init'
    if self.hasInputFromPort('execmode') :
      execmode = self.getInputFromPort('execmode')
    track = 1
    if self.hasInputFromPort('track') :
      track = self.getInputFromPort('track')
    B = 1.0
    if self.hasInputFromPort('B') :
      B = self.getInputFromPort('B')
    C = 0.0
    if self.hasInputFromPort('C') :
      C = self.getInputFromPort('C')
    results = sr_py.ShowAndEditCameraWidget(frame,num_frames,time,playmode,execmode,track,B,C)
    self.setResult('Geometry', results)

class SCIRun_InterfaceWithCamal(Module) :
  def compute(self) :
    TriSurf = 0
    if self.hasInputFromPort('TriSurf') :
      TriSurf = self.getInputFromPort('TriSurf')
    results = sr_py.InterfaceWithCamal(TriSurf)
    self.setResult('TetVol', results)

class SCIRun_CreateParameterBundle(Module) :
  def compute(self) :
    data = '0 "example field" string "example" ""} {0 "example scalar" scalar 1.0 ""} '
    if self.hasInputFromPort('data') :
      data = self.getInputFromPort('data')
    new_field_count = 1
    if self.hasInputFromPort('new_field_count') :
      new_field_count = self.getInputFromPort('new_field_count')
    update_all = '::SCIRun_Bundle_CreateParameterBundle_0 update_all_data'
    if self.hasInputFromPort('update_all') :
      update_all = self.getInputFromPort('update_all')
    results = sr_py.CreateParameterBundle(data,new_field_count,update_all)
    self.setResult('ParameterList', results)

class SCIRun_SelectAndSetFieldData3(Module) :
  def compute(self) :
    selection1 = 'DATA < A'
    if self.hasInputFromPort('selection1') :
      selection1 = self.getInputFromPort('selection1')
    function1 = 'abs(DATA)'
    if self.hasInputFromPort('function1') :
      function1 = self.getInputFromPort('function1')
    selection2 = 'DATA > A'
    if self.hasInputFromPort('selection2') :
      selection2 = self.getInputFromPort('selection2')
    function2 = '-abs(DATA)'
    if self.hasInputFromPort('function2') :
      function2 = self.getInputFromPort('function2')
    selection3 = ''
    if self.hasInputFromPort('selection3') :
      selection3 = self.getInputFromPort('selection3')
    function3 = ''
    if self.hasInputFromPort('function3') :
      function3 = self.getInputFromPort('function3')
    selection4 = ''
    if self.hasInputFromPort('selection4') :
      selection4 = self.getInputFromPort('selection4')
    function4 = ''
    if self.hasInputFromPort('function4') :
      function4 = self.getInputFromPort('function4')
    functiondef = 0
    if self.hasInputFromPort('functiondef') :
      functiondef = self.getInputFromPort('functiondef')
    format = 'Scalar'
    if self.hasInputFromPort('format') :
      format = self.getInputFromPort('format')
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
    results = sr_py.SelectAndSetFieldData3(Field1,Field2,Field3,Array,selection1,function1,selection2,function2,selection3,function3,selection4,function4,functiondef,format)
    self.setResult('Field', results)

class SCIRun_ConvertMeshToPointCloud(Module) :
  def compute(self) :
    datalocation = 0
    if self.hasInputFromPort('datalocation') :
      datalocation = self.getInputFromPort('datalocation')
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    results = sr_py.ConvertMeshToPointCloud(Field,datalocation)
    self.setResult('Field', results)

class SCIRun_InsertStringsIntoBundle(Module) :
  def compute(self) :
    string1_name = 'string1'
    if self.hasInputFromPort('string1_name') :
      string1_name = self.getInputFromPort('string1_name')
    string2_name = 'string2'
    if self.hasInputFromPort('string2_name') :
      string2_name = self.getInputFromPort('string2_name')
    string3_name = 'string3'
    if self.hasInputFromPort('string3_name') :
      string3_name = self.getInputFromPort('string3_name')
    string4_name = 'string4'
    if self.hasInputFromPort('string4_name') :
      string4_name = self.getInputFromPort('string4_name')
    string5_name = 'string5'
    if self.hasInputFromPort('string5_name') :
      string5_name = self.getInputFromPort('string5_name')
    string6_name = 'string6'
    if self.hasInputFromPort('string6_name') :
      string6_name = self.getInputFromPort('string6_name')
    replace1 = 1
    if self.hasInputFromPort('replace1') :
      replace1 = self.getInputFromPort('replace1')
    replace2 = 1
    if self.hasInputFromPort('replace2') :
      replace2 = self.getInputFromPort('replace2')
    replace3 = 1
    if self.hasInputFromPort('replace3') :
      replace3 = self.getInputFromPort('replace3')
    replace4 = 1
    if self.hasInputFromPort('replace4') :
      replace4 = self.getInputFromPort('replace4')
    replace5 = 1
    if self.hasInputFromPort('replace5') :
      replace5 = self.getInputFromPort('replace5')
    replace6 = 1
    if self.hasInputFromPort('replace6') :
      replace6 = self.getInputFromPort('replace6')
    bundle = 0
    if self.hasInputFromPort('bundle') :
      bundle = self.getInputFromPort('bundle')
    string1 = 0
    if self.hasInputFromPort('string1') :
      string1 = self.getInputFromPort('string1')
    string2 = 0
    if self.hasInputFromPort('string2') :
      string2 = self.getInputFromPort('string2')
    string3 = 0
    if self.hasInputFromPort('string3') :
      string3 = self.getInputFromPort('string3')
    string4 = 0
    if self.hasInputFromPort('string4') :
      string4 = self.getInputFromPort('string4')
    string5 = 0
    if self.hasInputFromPort('string5') :
      string5 = self.getInputFromPort('string5')
    string6 = 0
    if self.hasInputFromPort('string6') :
      string6 = self.getInputFromPort('string6')
    results = sr_py.InsertStringsIntoBundle(bundle,string1,string2,string3,string4,string5,string6,string1_name,string2_name,string3_name,string4_name,string5_name,string6_name,replace1,replace2,replace3,replace4,replace5,replace6)
    self.setResult('bundle', results)

class SCIRun_GetMatricesFromBundle(Module) :
  def compute(self) :
    matrix1_name = 'matrix1'
    if self.hasInputFromPort('matrix1_name') :
      matrix1_name = self.getInputFromPort('matrix1_name')
    matrix2_name = 'matrix2'
    if self.hasInputFromPort('matrix2_name') :
      matrix2_name = self.getInputFromPort('matrix2_name')
    matrix3_name = 'matrix3'
    if self.hasInputFromPort('matrix3_name') :
      matrix3_name = self.getInputFromPort('matrix3_name')
    matrix4_name = 'matrix4'
    if self.hasInputFromPort('matrix4_name') :
      matrix4_name = self.getInputFromPort('matrix4_name')
    matrix5_name = 'matrix5'
    if self.hasInputFromPort('matrix5_name') :
      matrix5_name = self.getInputFromPort('matrix5_name')
    matrix6_name = 'matrix6'
    if self.hasInputFromPort('matrix6_name') :
      matrix6_name = self.getInputFromPort('matrix6_name')
    transposenrrd1 = 0
    if self.hasInputFromPort('transposenrrd1') :
      transposenrrd1 = self.getInputFromPort('transposenrrd1')
    transposenrrd2 = 0
    if self.hasInputFromPort('transposenrrd2') :
      transposenrrd2 = self.getInputFromPort('transposenrrd2')
    transposenrrd3 = 0
    if self.hasInputFromPort('transposenrrd3') :
      transposenrrd3 = self.getInputFromPort('transposenrrd3')
    transposenrrd4 = 0
    if self.hasInputFromPort('transposenrrd4') :
      transposenrrd4 = self.getInputFromPort('transposenrrd4')
    transposenrrd5 = 0
    if self.hasInputFromPort('transposenrrd5') :
      transposenrrd5 = self.getInputFromPort('transposenrrd5')
    transposenrrd6 = 0
    if self.hasInputFromPort('transposenrrd6') :
      transposenrrd6 = self.getInputFromPort('transposenrrd6')
    matrix_selection = ''
    if self.hasInputFromPort('matrix_selection') :
      matrix_selection = self.getInputFromPort('matrix_selection')
    bundle = 0
    if self.hasInputFromPort('bundle') :
      bundle = self.getInputFromPort('bundle')
    results = sr_py.GetMatricesFromBundle(bundle,matrix1_name,matrix2_name,matrix3_name,matrix4_name,matrix5_name,matrix6_name,transposenrrd1,transposenrrd2,transposenrrd3,transposenrrd4,transposenrrd5,transposenrrd6,matrix_selection)
    self.setResult('bundle', sr_py.read_at_index(results,0))
    self.setResult('matrix1', sr_py.read_at_index(results,1))
    self.setResult('matrix2', sr_py.read_at_index(results,2))
    self.setResult('matrix3', sr_py.read_at_index(results,3))
    self.setResult('matrix4', sr_py.read_at_index(results,4))
    self.setResult('matrix5', sr_py.read_at_index(results,5))
    self.setResult('matrix6', sr_py.read_at_index(results,6))

class SCIRun_GetNrrdsFromBundle(Module) :
  def compute(self) :
    nrrd1_name = 'nrrd1'
    if self.hasInputFromPort('nrrd1_name') :
      nrrd1_name = self.getInputFromPort('nrrd1_name')
    nrrd2_name = 'nrrd2'
    if self.hasInputFromPort('nrrd2_name') :
      nrrd2_name = self.getInputFromPort('nrrd2_name')
    nrrd3_name = 'nrrd3'
    if self.hasInputFromPort('nrrd3_name') :
      nrrd3_name = self.getInputFromPort('nrrd3_name')
    nrrd4_name = 'nrrd4'
    if self.hasInputFromPort('nrrd4_name') :
      nrrd4_name = self.getInputFromPort('nrrd4_name')
    nrrd5_name = 'nrrd5'
    if self.hasInputFromPort('nrrd5_name') :
      nrrd5_name = self.getInputFromPort('nrrd5_name')
    nrrd6_name = 'nrrd6'
    if self.hasInputFromPort('nrrd6_name') :
      nrrd6_name = self.getInputFromPort('nrrd6_name')
    transposenrrd1 = 0
    if self.hasInputFromPort('transposenrrd1') :
      transposenrrd1 = self.getInputFromPort('transposenrrd1')
    transposenrrd2 = 0
    if self.hasInputFromPort('transposenrrd2') :
      transposenrrd2 = self.getInputFromPort('transposenrrd2')
    transposenrrd3 = 0
    if self.hasInputFromPort('transposenrrd3') :
      transposenrrd3 = self.getInputFromPort('transposenrrd3')
    transposenrrd4 = 0
    if self.hasInputFromPort('transposenrrd4') :
      transposenrrd4 = self.getInputFromPort('transposenrrd4')
    transposenrrd5 = 0
    if self.hasInputFromPort('transposenrrd5') :
      transposenrrd5 = self.getInputFromPort('transposenrrd5')
    transposenrrd6 = 0
    if self.hasInputFromPort('transposenrrd6') :
      transposenrrd6 = self.getInputFromPort('transposenrrd6')
    nrrd_selection = ''
    if self.hasInputFromPort('nrrd_selection') :
      nrrd_selection = self.getInputFromPort('nrrd_selection')
    bundle = 0
    if self.hasInputFromPort('bundle') :
      bundle = self.getInputFromPort('bundle')
    results = sr_py.GetNrrdsFromBundle(bundle,nrrd1_name,nrrd2_name,nrrd3_name,nrrd4_name,nrrd5_name,nrrd6_name,transposenrrd1,transposenrrd2,transposenrrd3,transposenrrd4,transposenrrd5,transposenrrd6,nrrd_selection)
    self.setResult('bundle', sr_py.read_at_index(results,0))
    self.setResult('nrrd1', sr_py.read_at_index(results,1))
    self.setResult('nrrd2', sr_py.read_at_index(results,2))
    self.setResult('nrrd3', sr_py.read_at_index(results,3))
    self.setResult('nrrd4', sr_py.read_at_index(results,4))
    self.setResult('nrrd5', sr_py.read_at_index(results,5))
    self.setResult('nrrd6', sr_py.read_at_index(results,6))

class SCIRun_ManageFieldSeries(Module) :
  def compute(self) :
    num_ports = 2
    if self.hasInputFromPort('num_ports') :
      num_ports = self.getInputFromPort('num_ports')
    Input = 0
    if self.hasInputFromPort('Input') :
      Input = self.getInputFromPort('Input')
    results = sr_py.ManageFieldSeries(Input,num_ports)
    self.setResult('Output 0', sr_py.read_at_index(results,0))
    self.setResult('Output 1', sr_py.read_at_index(results,1))
    self.setResult('Output 2', sr_py.read_at_index(results,2))
    self.setResult('Output 3', sr_py.read_at_index(results,3))

class SCIRun_ConvertMatrixToField(Module) :
  def compute(self) :
    datalocation = 'Node'
    if self.hasInputFromPort('datalocation') :
      datalocation = self.getInputFromPort('datalocation')
    Matrix = 0
    if self.hasInputFromPort('Matrix') :
      Matrix = self.getInputFromPort('Matrix')
    results = sr_py.ConvertMatrixToField(Matrix,datalocation)
    self.setResult('Field', results)

class SCIRun_ChooseColorMap(Module) :
  def compute(self) :
    use_first_valid = 1
    if self.hasInputFromPort('use_first_valid') :
      use_first_valid = self.getInputFromPort('use_first_valid')
    port_valid_index = 0
    if self.hasInputFromPort('port_valid_index') :
      port_valid_index = self.getInputFromPort('port_valid_index')
    port_selected_index = 0
    if self.hasInputFromPort('port_selected_index') :
      port_selected_index = self.getInputFromPort('port_selected_index')
    ColorMap = 0
    if self.hasInputFromPort('ColorMap') :
      ColorMap = self.getInputFromPort('ColorMap')
    results = sr_py.ChooseColorMap(ColorMap,use_first_valid,port_valid_index,port_selected_index)
    self.setResult('ColorMap', results)

class SCIRun_CollectMatrices(Module) :
  def compute(self) :
    append = 0
    if self.hasInputFromPort('append') :
      append = self.getInputFromPort('append')
    row = 0
    if self.hasInputFromPort('row') :
      row = self.getInputFromPort('row')
    front = 0
    if self.hasInputFromPort('front') :
      front = self.getInputFromPort('front')
    Optional_BaseMatrix = 0
    if self.hasInputFromPort('Optional BaseMatrix') :
      Optional_BaseMatrix = self.getInputFromPort('Optional BaseMatrix')
    SubMatrix = 0
    if self.hasInputFromPort('SubMatrix') :
      SubMatrix = self.getInputFromPort('SubMatrix')
    results = sr_py.CollectMatrices(Optional_BaseMatrix,SubMatrix,append,row,front)
    self.setResult('CompositeMatrix', results)

class SCIRun_ReadField(Module) :
  def compute(self) :
    from_env = ''
    if self.hasInputFromPort('from_env') :
      from_env = self.getInputFromPort('from_env')
    Filename = 0
    if self.hasInputFromPort('Filename') :
      Filename = self.getInputFromPort('Filename')
    results = sr_py.ReadField(Filename,from_env)
    self.setResult('Output Data', sr_py.read_at_index(results,0))
    self.setResult('Filename', sr_py.read_at_index(results,1))

class SCIRun_GetFileName(Module) :
  def compute(self) :
    filename_base = ''
    if self.hasInputFromPort('filename_base') :
      filename_base = self.getInputFromPort('filename_base')
    delay = 0
    if self.hasInputFromPort('delay') :
      delay = self.getInputFromPort('delay')
    pinned = 0
    if self.hasInputFromPort('pinned') :
      pinned = self.getInputFromPort('pinned')
    results = sr_py.GetFileName(filename_base,delay,pinned)
    self.setResult('Full Filename', results)

class SCIRun_ClipVolumeByIsovalue(Module) :
  def compute(self) :
    isoval_min = 0.0
    if self.hasInputFromPort('isoval_min') :
      isoval_min = self.getInputFromPort('isoval_min')
    isoval_max = 99.0
    if self.hasInputFromPort('isoval_max') :
      isoval_max = self.getInputFromPort('isoval_max')
    isoval = 0.0
    if self.hasInputFromPort('isoval') :
      isoval = self.getInputFromPort('isoval')
    lte = 1
    if self.hasInputFromPort('lte') :
      lte = self.getInputFromPort('lte')
    update_type = 'On Release'
    if self.hasInputFromPort('update_type') :
      update_type = self.getInputFromPort('update_type')
    Input = 0
    if self.hasInputFromPort('Input') :
      Input = self.getInputFromPort('Input')
    Optional_Isovalue = 0
    if self.hasInputFromPort('Optional Isovalue') :
      Optional_Isovalue = self.getInputFromPort('Optional Isovalue')
    results = sr_py.ClipVolumeByIsovalue(Input,Optional_Isovalue,isoval_min,isoval_max,isoval,lte,update_type)
    self.setResult('Clipped', sr_py.read_at_index(results,0))
    self.setResult('Mapping', sr_py.read_at_index(results,1))

class SCIRun_DecomposeTensorArrayIntoEigenVectors(Module) :
  def compute(self) :
    TensorArray = 0
    if self.hasInputFromPort('TensorArray') :
      TensorArray = self.getInputFromPort('TensorArray')
    results = sr_py.DecomposeTensorArrayIntoEigenVectors(TensorArray)
    self.setResult('EigenVector1', sr_py.read_at_index(results,0))
    self.setResult('EigenVector2', sr_py.read_at_index(results,1))
    self.setResult('EigenVector3', sr_py.read_at_index(results,2))
    self.setResult('EigenValue1', sr_py.read_at_index(results,3))
    self.setResult('EigenValue2', sr_py.read_at_index(results,4))
    self.setResult('EigenValue3', sr_py.read_at_index(results,5))

class SCIRun_TransformMeshWithTransform(Module) :
  def compute(self) :
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    Transform_Matrix = 0
    if self.hasInputFromPort('Transform Matrix') :
      Transform_Matrix = self.getInputFromPort('Transform Matrix')
    results = sr_py.TransformMeshWithTransform(Input_Field,Transform_Matrix)
    self.setResult('Transformed Field', results)

class SCIRun_ReportSearchGridInfo(Module) :
  def compute(self) :
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    results = sr_py.ReportSearchGridInfo(Input_Field)
    self.setResult('Output Sample Field', results)

class SCIRun_ChooseField(Module) :
  def compute(self) :
    use_first_valid = 1
    if self.hasInputFromPort('use_first_valid') :
      use_first_valid = self.getInputFromPort('use_first_valid')
    port_valid_index = 0
    if self.hasInputFromPort('port_valid_index') :
      port_valid_index = self.getInputFromPort('port_valid_index')
    port_selected_index = 0
    if self.hasInputFromPort('port_selected_index') :
      port_selected_index = self.getInputFromPort('port_selected_index')
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    results = sr_py.ChooseField(Field,use_first_valid,port_valid_index,port_selected_index)
    self.setResult('Field', results)

class SCIRun_CreateLightForViewer(Module) :
  def compute(self) :
    control_pos_saved = 0
    if self.hasInputFromPort('control_pos_saved') :
      control_pos_saved = self.getInputFromPort('control_pos_saved')
    control_x = 0.0
    if self.hasInputFromPort('control_x') :
      control_x = self.getInputFromPort('control_x')
    control_y = 0.0
    if self.hasInputFromPort('control_y') :
      control_y = self.getInputFromPort('control_y')
    control_z = 0.0
    if self.hasInputFromPort('control_z') :
      control_z = self.getInputFromPort('control_z')
    at_x = 0.0
    if self.hasInputFromPort('at_x') :
      at_x = self.getInputFromPort('at_x')
    at_y = 0.0
    if self.hasInputFromPort('at_y') :
      at_y = self.getInputFromPort('at_y')
    at_z = 1.0
    if self.hasInputFromPort('at_z') :
      at_z = self.getInputFromPort('at_z')
    type = 0
    if self.hasInputFromPort('type') :
      type = self.getInputFromPort('type')
    on = 1
    if self.hasInputFromPort('on') :
      on = self.getInputFromPort('on')
    results = sr_py.CreateLightForViewer(control_pos_saved,control_x,control_y,control_z,at_x,at_y,at_z,type,on)
    self.setResult('Geometry', results)

class SCIRun_ConvertRegularMeshToStructuredMesh(Module) :
  def compute(self) :
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    results = sr_py.ConvertRegularMeshToStructuredMesh(Input_Field)
    self.setResult('Output Field', results)

class SCIRun_WriteColorMap(Module) :
  def compute(self) :
    filetype = 'Binary'
    if self.hasInputFromPort('filetype') :
      filetype = self.getInputFromPort('filetype')
    confirm = 0
    if self.hasInputFromPort('confirm') :
      confirm = self.getInputFromPort('confirm')
    confirm_once = 0
    if self.hasInputFromPort('confirm_once') :
      confirm_once = self.getInputFromPort('confirm_once')
    exporttype = ''
    if self.hasInputFromPort('exporttype') :
      exporttype = self.getInputFromPort('exporttype')
    Input_Data = 0
    if self.hasInputFromPort('Input Data') :
      Input_Data = self.getInputFromPort('Input Data')
    Filename = 0
    if self.hasInputFromPort('Filename') :
      Filename = self.getInputFromPort('Filename')
    results = sr_py.WriteColorMap(Input_Data,Filename,filetype,confirm,confirm_once,exporttype)

class SCIRun_MergeFields(Module) :
  def compute(self) :
    Container_Mesh = 0
    if self.hasInputFromPort('Container Mesh') :
      Container_Mesh = self.getInputFromPort('Container Mesh')
    Insert_Field = 0
    if self.hasInputFromPort('Insert Field') :
      Insert_Field = self.getInputFromPort('Insert Field')
    results = sr_py.MergeFields(Container_Mesh,Insert_Field)
    self.setResult('Combined Field', sr_py.read_at_index(results,0))
    self.setResult('Extended Insert Field', sr_py.read_at_index(results,1))
    self.setResult('Combined To Extended Mapping', sr_py.read_at_index(results,2))

class SCIRun_BuildPointCloudToLatVolMappingMatrix(Module) :
  def compute(self) :
    epsilon = 0.0
    if self.hasInputFromPort('epsilon') :
      epsilon = self.getInputFromPort('epsilon')
    PointCloudField = 0
    if self.hasInputFromPort('PointCloudField') :
      PointCloudField = self.getInputFromPort('PointCloudField')
    LatVolField = 0
    if self.hasInputFromPort('LatVolField') :
      LatVolField = self.getInputFromPort('LatVolField')
    results = sr_py.BuildPointCloudToLatVolMappingMatrix(PointCloudField,LatVolField,epsilon)
    self.setResult('MappingMatrix', results)

class SCIRun_CalculateDataArray(Module) :
  def compute(self) :
    function = 'RESULT = abs(DATA);'
    if self.hasInputFromPort('function') :
      function = self.getInputFromPort('function')
    format = 'Scalar'
    if self.hasInputFromPort('format') :
      format = self.getInputFromPort('format')
    DataArray = 0
    if self.hasInputFromPort('DataArray') :
      DataArray = self.getInputFromPort('DataArray')
    Function = 0
    if self.hasInputFromPort('Function') :
      Function = self.getInputFromPort('Function')
    Array = 0
    if self.hasInputFromPort('Array') :
      Array = self.getInputFromPort('Array')
    results = sr_py.CalculateDataArray(DataArray,Function,Array,function,format)
    self.setResult('DataArray', results)

class SCIRun_GetColumnOrRowFromMatrix(Module) :
  def compute(self) :
    row_or_col = 'row'
    if self.hasInputFromPort('row_or_col') :
      row_or_col = self.getInputFromPort('row_or_col')
    selectable_min = 0
    if self.hasInputFromPort('selectable_min') :
      selectable_min = self.getInputFromPort('selectable_min')
    selectable_max = 100
    if self.hasInputFromPort('selectable_max') :
      selectable_max = self.getInputFromPort('selectable_max')
    selectable_inc = 1
    if self.hasInputFromPort('selectable_inc') :
      selectable_inc = self.getInputFromPort('selectable_inc')
    selectable_units = ''
    if self.hasInputFromPort('selectable_units') :
      selectable_units = self.getInputFromPort('selectable_units')
    range_min = 0
    if self.hasInputFromPort('range_min') :
      range_min = self.getInputFromPort('range_min')
    range_max = 100
    if self.hasInputFromPort('range_max') :
      range_max = self.getInputFromPort('range_max')
    playmode = 'once'
    if self.hasInputFromPort('playmode') :
      playmode = self.getInputFromPort('playmode')
    current = 0
    if self.hasInputFromPort('current') :
      current = self.getInputFromPort('current')
    execmode = 'init'
    if self.hasInputFromPort('execmode') :
      execmode = self.getInputFromPort('execmode')
    delay = 0
    if self.hasInputFromPort('delay') :
      delay = self.getInputFromPort('delay')
    inc_amount = 1
    if self.hasInputFromPort('inc_amount') :
      inc_amount = self.getInputFromPort('inc_amount')
    send_amount = 1
    if self.hasInputFromPort('send_amount') :
      send_amount = self.getInputFromPort('send_amount')
    data_series_done = 0
    if self.hasInputFromPort('data_series_done') :
      data_series_done = self.getInputFromPort('data_series_done')
    Matrix = 0
    if self.hasInputFromPort('Matrix') :
      Matrix = self.getInputFromPort('Matrix')
    Weight_Vector = 0
    if self.hasInputFromPort('Weight Vector') :
      Weight_Vector = self.getInputFromPort('Weight Vector')
    Current_Index = 0
    if self.hasInputFromPort('Current Index') :
      Current_Index = self.getInputFromPort('Current Index')
    results = sr_py.GetColumnOrRowFromMatrix(Matrix,Weight_Vector,Current_Index,row_or_col,selectable_min,selectable_max,selectable_inc,selectable_units,range_min,range_max,playmode,current,execmode,delay,inc_amount,send_amount,data_series_done)
    self.setResult('Vector', sr_py.read_at_index(results,0))
    self.setResult('Selected Index', sr_py.read_at_index(results,1))

class SCIRun_ShowTextureVolume(Module) :
  def compute(self) :
    sampling_rate_hi = 4.0
    if self.hasInputFromPort('sampling_rate_hi') :
      sampling_rate_hi = self.getInputFromPort('sampling_rate_hi')
    sampling_rate_lo = 1.0
    if self.hasInputFromPort('sampling_rate_lo') :
      sampling_rate_lo = self.getInputFromPort('sampling_rate_lo')
    gradient_min = 0.0
    if self.hasInputFromPort('gradient_min') :
      gradient_min = self.getInputFromPort('gradient_min')
    gradient_max = 0.0
    if self.hasInputFromPort('gradient_max') :
      gradient_max = self.getInputFromPort('gradient_max')
    adaptive = 1
    if self.hasInputFromPort('adaptive') :
      adaptive = self.getInputFromPort('adaptive')
    cmap_size = 8
    if self.hasInputFromPort('cmap_size') :
      cmap_size = self.getInputFromPort('cmap_size')
    sw_raster = 0
    if self.hasInputFromPort('sw_raster') :
      sw_raster = self.getInputFromPort('sw_raster')
    render_style = 0
    if self.hasInputFromPort('render_style') :
      render_style = self.getInputFromPort('render_style')
    alpha_scale = 0.0
    if self.hasInputFromPort('alpha_scale') :
      alpha_scale = self.getInputFromPort('alpha_scale')
    interp_mode = 1
    if self.hasInputFromPort('interp_mode') :
      interp_mode = self.getInputFromPort('interp_mode')
    shading = 0
    if self.hasInputFromPort('shading') :
      shading = self.getInputFromPort('shading')
    ambient = 0.5
    if self.hasInputFromPort('ambient') :
      ambient = self.getInputFromPort('ambient')
    diffuse = 0.5
    if self.hasInputFromPort('diffuse') :
      diffuse = self.getInputFromPort('diffuse')
    specular = 0.0
    if self.hasInputFromPort('specular') :
      specular = self.getInputFromPort('specular')
    shine = 30.0
    if self.hasInputFromPort('shine') :
      shine = self.getInputFromPort('shine')
    light = 0
    if self.hasInputFromPort('light') :
      light = self.getInputFromPort('light')
    blend_res = 8
    if self.hasInputFromPort('blend_res') :
      blend_res = self.getInputFromPort('blend_res')
    multi_level = 1
    if self.hasInputFromPort('multi_level') :
      multi_level = self.getInputFromPort('multi_level')
    use_stencil = 0
    if self.hasInputFromPort('use_stencil') :
      use_stencil = self.getInputFromPort('use_stencil')
    invert_opacity = 0
    if self.hasInputFromPort('invert_opacity') :
      invert_opacity = self.getInputFromPort('invert_opacity')
    num_clipping_planes = 2
    if self.hasInputFromPort('num_clipping_planes') :
      num_clipping_planes = self.getInputFromPort('num_clipping_planes')
    show_clipping_widgets = 1
    if self.hasInputFromPort('show_clipping_widgets') :
      show_clipping_widgets = self.getInputFromPort('show_clipping_widgets')
    level_on = ''
    if self.hasInputFromPort('level_on') :
      level_on = self.getInputFromPort('level_on')
    level_vals = ''
    if self.hasInputFromPort('level_vals') :
      level_vals = self.getInputFromPort('level_vals')
    Texture = 0
    if self.hasInputFromPort('Texture') :
      Texture = self.getInputFromPort('Texture')
    ColorMap = 0
    if self.hasInputFromPort('ColorMap') :
      ColorMap = self.getInputFromPort('ColorMap')
    ColorMap2 = 0
    if self.hasInputFromPort('ColorMap2') :
      ColorMap2 = self.getInputFromPort('ColorMap2')
    results = sr_py.ShowTextureVolume(Texture,ColorMap,ColorMap2,sampling_rate_hi,sampling_rate_lo,gradient_min,gradient_max,adaptive,cmap_size,sw_raster,render_style,alpha_scale,interp_mode,shading,ambient,diffuse,specular,shine,light,blend_res,multi_level,use_stencil,invert_opacity,num_clipping_planes,show_clipping_widgets,level_on,level_vals)
    self.setResult('Geometry', sr_py.read_at_index(results,0))
    self.setResult('ColorMap', sr_py.read_at_index(results,1))

class SCIRun_GetCentroidsFromMesh(Module) :
  def compute(self) :
    TetVolField = 0
    if self.hasInputFromPort('TetVolField') :
      TetVolField = self.getInputFromPort('TetVolField')
    results = sr_py.GetCentroidsFromMesh(TetVolField)
    self.setResult('PointCloudField', results)

class SCIRun_ReadColorMap2D(Module) :
  def compute(self) :
    from_env = ''
    if self.hasInputFromPort('from_env') :
      from_env = self.getInputFromPort('from_env')
    Filename = 0
    if self.hasInputFromPort('Filename') :
      Filename = self.getInputFromPort('Filename')
    results = sr_py.ReadColorMap2D(Filename,from_env)
    self.setResult('Output Data', sr_py.read_at_index(results,0))
    self.setResult('Filename', sr_py.read_at_index(results,1))

class SCIRun_ConvertLatVolDataFromNodeToElem(Module) :
  def compute(self) :
    Node_Field = 0
    if self.hasInputFromPort('Node Field') :
      Node_Field = self.getInputFromPort('Node Field')
    results = sr_py.ConvertLatVolDataFromNodeToElem(Node_Field)
    self.setResult('Elem Field', results)

class SCIRun_InsertHexVolSheetAlongSurface(Module) :
  def compute(self) :
    side = 'side1'
    if self.hasInputFromPort('side') :
      side = self.getInputFromPort('side')
    addlayer = 'On'
    if self.hasInputFromPort('addlayer') :
      addlayer = self.getInputFromPort('addlayer')
    HexField = 0
    if self.hasInputFromPort('HexField') :
      HexField = self.getInputFromPort('HexField')
    TriField = 0
    if self.hasInputFromPort('TriField') :
      TriField = self.getInputFromPort('TriField')
    results = sr_py.InsertHexVolSheetAlongSurface(HexField,TriField,side,addlayer)
    self.setResult('Side1Field', sr_py.read_at_index(results,0))
    self.setResult('Side2Field', sr_py.read_at_index(results,1))

class SCIRun_ExtractIsosurfaceByFunction(Module) :
  def compute(self) :
    function = 'result = sqrt(x*x + y*y);'
    if self.hasInputFromPort('function') :
      function = self.getInputFromPort('function')
    zero_checks = 0
    if self.hasInputFromPort('zero_checks') :
      zero_checks = self.getInputFromPort('zero_checks')
    slice_value_min = 0.0
    if self.hasInputFromPort('slice_value_min') :
      slice_value_min = self.getInputFromPort('slice_value_min')
    slice_value_max = 99.0
    if self.hasInputFromPort('slice_value_max') :
      slice_value_max = self.getInputFromPort('slice_value_max')
    slice_value = 0.0
    if self.hasInputFromPort('slice_value') :
      slice_value = self.getInputFromPort('slice_value')
    slice_value_typed = 0.0
    if self.hasInputFromPort('slice_value_typed') :
      slice_value_typed = self.getInputFromPort('slice_value_typed')
    slice_value_quantity = 1
    if self.hasInputFromPort('slice_value_quantity') :
      slice_value_quantity = self.getInputFromPort('slice_value_quantity')
    quantity_range = 'field'
    if self.hasInputFromPort('quantity_range') :
      quantity_range = self.getInputFromPort('quantity_range')
    quantity_clusive = 'exclusive'
    if self.hasInputFromPort('quantity_clusive') :
      quantity_clusive = self.getInputFromPort('quantity_clusive')
    quantity_min = 0.0
    if self.hasInputFromPort('quantity_min') :
      quantity_min = self.getInputFromPort('quantity_min')
    quantity_max = 100.0
    if self.hasInputFromPort('quantity_max') :
      quantity_max = self.getInputFromPort('quantity_max')
    quantity_list = ''
    if self.hasInputFromPort('quantity_list') :
      quantity_list = self.getInputFromPort('quantity_list')
    slice_value_list = 'No values present.'
    if self.hasInputFromPort('slice_value_list') :
      slice_value_list = self.getInputFromPort('slice_value_list')
    matrix_list = 'No matrix present - execution needed.'
    if self.hasInputFromPort('matrix_list') :
      matrix_list = self.getInputFromPort('matrix_list')
    extract_from_new_field = 1
    if self.hasInputFromPort('extract_from_new_field') :
      extract_from_new_field = self.getInputFromPort('extract_from_new_field')
    algorithm = 0
    if self.hasInputFromPort('algorithm') :
      algorithm = self.getInputFromPort('algorithm')
    build_trisurf = 1
    if self.hasInputFromPort('build_trisurf') :
      build_trisurf = self.getInputFromPort('build_trisurf')
    build_geom = 1
    if self.hasInputFromPort('build_geom') :
      build_geom = self.getInputFromPort('build_geom')
    active_slice_value_selection_tab = 0
    if self.hasInputFromPort('active_slice_value_selection_tab') :
      active_slice_value_selection_tab = self.getInputFromPort('active_slice_value_selection_tab')
    active_tab = 0
    if self.hasInputFromPort('active_tab') :
      active_tab = self.getInputFromPort('active_tab')
    update_type = 'On Release'
    if self.hasInputFromPort('update_type') :
      update_type = self.getInputFromPort('update_type')
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    Optional_Slice_values = 0
    if self.hasInputFromPort('Optional Slice values') :
      Optional_Slice_values = self.getInputFromPort('Optional Slice values')
    results = sr_py.ExtractIsosurfaceByFunction(Input_Field,Optional_Slice_values,function,zero_checks,slice_value_min,slice_value_max,slice_value,slice_value_typed,slice_value_quantity,quantity_range,quantity_clusive,quantity_min,quantity_max,quantity_list,slice_value_list,matrix_list,extract_from_new_field,algorithm,build_trisurf,build_geom,active_slice_value_selection_tab,active_tab,update_type)
    self.setResult('Output Field', results)

class SCIRun_BuildNoiseColumnMatrix(Module) :
  def compute(self) :
    snr = 10.0
    if self.hasInputFromPort('snr') :
      snr = self.getInputFromPort('snr')
    Signal = 0
    if self.hasInputFromPort('Signal') :
      Signal = self.getInputFromPort('Signal')
    results = sr_py.BuildNoiseColumnMatrix(Signal,snr)
    self.setResult('Noise', results)

class SCIRun_MergeTriSurfs(Module) :
  def compute(self) :
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    results = sr_py.MergeTriSurfs(Input_Field)
    self.setResult('Output Field', results)

class SCIRun_ReadString(Module) :
  def compute(self) :
    from_env = ''
    if self.hasInputFromPort('from_env') :
      from_env = self.getInputFromPort('from_env')
    Filename = 0
    if self.hasInputFromPort('Filename') :
      Filename = self.getInputFromPort('Filename')
    results = sr_py.ReadString(Filename,from_env)
    self.setResult('Output Data', sr_py.read_at_index(results,0))
    self.setResult('Filename', sr_py.read_at_index(results,1))

class SCIRun_InterfaceWithTetGen(Module) :
  def compute(self) :
    switch = 'pqYAz'
    if self.hasInputFromPort('switch') :
      switch = self.getInputFromPort('switch')
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
    results = sr_py.InterfaceWithTetGen(Main,Points,Region_Attribs,Regions,switch)
    self.setResult('TetVol', results)

class SCIRun_CalculateMeshNodes(Module) :
  def compute(self) :
    function = 'NEWPOS = 3*POS;'
    if self.hasInputFromPort('function') :
      function = self.getInputFromPort('function')
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    Function = 0
    if self.hasInputFromPort('Function') :
      Function = self.getInputFromPort('Function')
    Array = 0
    if self.hasInputFromPort('Array') :
      Array = self.getInputFromPort('Array')
    results = sr_py.CalculateMeshNodes(Field,Function,Array,function)
    self.setResult('Field', results)

class SCIRun_CreateImage(Module) :
  def compute(self) :
    sizex = 20
    if self.hasInputFromPort('sizex') :
      sizex = self.getInputFromPort('sizex')
    sizey = 20
    if self.hasInputFromPort('sizey') :
      sizey = self.getInputFromPort('sizey')
    sizez = 2
    if self.hasInputFromPort('sizez') :
      sizez = self.getInputFromPort('sizez')
    z_value = 0
    if self.hasInputFromPort('z_value') :
      z_value = self.getInputFromPort('z_value')
    auto_size = 0
    if self.hasInputFromPort('auto_size') :
      auto_size = self.getInputFromPort('auto_size')
    axis = 0
    if self.hasInputFromPort('axis') :
      axis = self.getInputFromPort('axis')
    padpercent = 0.0
    if self.hasInputFromPort('padpercent') :
      padpercent = self.getInputFromPort('padpercent')
    pos = 0.0
    if self.hasInputFromPort('pos') :
      pos = self.getInputFromPort('pos')
    data_at = 'Nodes'
    if self.hasInputFromPort('data_at') :
      data_at = self.getInputFromPort('data_at')
    update_type = 'On Release'
    if self.hasInputFromPort('update_type') :
      update_type = self.getInputFromPort('update_type')
    corigin_x = 0.0
    if self.hasInputFromPort('corigin_x') :
      corigin_x = self.getInputFromPort('corigin_x')
    corigin_y = 0.0
    if self.hasInputFromPort('corigin_y') :
      corigin_y = self.getInputFromPort('corigin_y')
    corigin_z = 0.0
    if self.hasInputFromPort('corigin_z') :
      corigin_z = self.getInputFromPort('corigin_z')
    cnormal_x = 1.0
    if self.hasInputFromPort('cnormal_x') :
      cnormal_x = self.getInputFromPort('cnormal_x')
    cnormal_y = 1.0
    if self.hasInputFromPort('cnormal_y') :
      cnormal_y = self.getInputFromPort('cnormal_y')
    cnormal_z = 1.0
    if self.hasInputFromPort('cnormal_z') :
      cnormal_z = self.getInputFromPort('cnormal_z')
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    results = sr_py.CreateImage(Input_Field,sizex,sizey,sizez,z_value,auto_size,axis,padpercent,pos,data_at,update_type,corigin_x,corigin_y,corigin_z,cnormal_x,cnormal_y,cnormal_z)
    self.setResult('Output Sample Field', results)

class SCIRun_SplitNodesByDomain(Module) :
  def compute(self) :
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    results = sr_py.SplitNodesByDomain(Field)
    self.setResult('SplitField', results)

class SCIRun_CalculateFieldDataCompiled(Module) :
  def compute(self) :
    outputdatatype = 'port 0 input'
    if self.hasInputFromPort('outputdatatype') :
      outputdatatype = self.getInputFromPort('outputdatatype')
    function = 'result = v0 + v1 + v2;'
    if self.hasInputFromPort('function') :
      function = self.getInputFromPort('function')
    cache = 0
    if self.hasInputFromPort('cache') :
      cache = self.getInputFromPort('cache')
    Function = 0
    if self.hasInputFromPort('Function') :
      Function = self.getInputFromPort('Function')
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    results = sr_py.CalculateFieldDataCompiled(Function,Input_Field,outputdatatype,function,cache)
    self.setResult('Output Field', results)

class SCIRun_ReadColorMap(Module) :
  def compute(self) :
    from_env = ''
    if self.hasInputFromPort('from_env') :
      from_env = self.getInputFromPort('from_env')
    Filename = 0
    if self.hasInputFromPort('Filename') :
      Filename = self.getInputFromPort('Filename')
    results = sr_py.ReadColorMap(Filename,from_env)
    self.setResult('Output Data', sr_py.read_at_index(results,0))
    self.setResult('Filename', sr_py.read_at_index(results,1))

class SCIRun_MapFieldDataFromElemToNode(Module) :
  def compute(self) :
    method = 'Interpolate'
    if self.hasInputFromPort('method') :
      method = self.getInputFromPort('method')
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    results = sr_py.MapFieldDataFromElemToNode(Field,method)
    self.setResult('Field', results)

class SCIRun_ShowFieldGlyphs(Module) :
  def compute(self) :
    scalars_has_data = 0
    if self.hasInputFromPort('scalars_has_data') :
      scalars_has_data = self.getInputFromPort('scalars_has_data')
    scalars_on = 0
    if self.hasInputFromPort('scalars_on') :
      scalars_on = self.getInputFromPort('scalars_on')
    scalars_display_type = 'Spheres'
    if self.hasInputFromPort('scalars_display_type') :
      scalars_display_type = self.getInputFromPort('scalars_display_type')
    scalars_transparency = 0
    if self.hasInputFromPort('scalars_transparency') :
      scalars_transparency = self.getInputFromPort('scalars_transparency')
    scalars_normalize = 0
    if self.hasInputFromPort('scalars_normalize') :
      scalars_normalize = self.getInputFromPort('scalars_normalize')
    scalars_color_type = 0
    if self.hasInputFromPort('scalars_color_type') :
      scalars_color_type = self.getInputFromPort('scalars_color_type')
    scalars_resolution = 6
    if self.hasInputFromPort('scalars_resolution') :
      scalars_resolution = self.getInputFromPort('scalars_resolution')
    vectors_has_data = 0
    if self.hasInputFromPort('vectors_has_data') :
      vectors_has_data = self.getInputFromPort('vectors_has_data')
    vectors_on = 0
    if self.hasInputFromPort('vectors_on') :
      vectors_on = self.getInputFromPort('vectors_on')
    vectors_display_type = 'Arrows'
    if self.hasInputFromPort('vectors_display_type') :
      vectors_display_type = self.getInputFromPort('vectors_display_type')
    vectors_transparency = 0
    if self.hasInputFromPort('vectors_transparency') :
      vectors_transparency = self.getInputFromPort('vectors_transparency')
    vectors_normalize = 0
    if self.hasInputFromPort('vectors_normalize') :
      vectors_normalize = self.getInputFromPort('vectors_normalize')
    vectors_bidirectional = 0
    if self.hasInputFromPort('vectors_bidirectional') :
      vectors_bidirectional = self.getInputFromPort('vectors_bidirectional')
    vectors_color_type = 0
    if self.hasInputFromPort('vectors_color_type') :
      vectors_color_type = self.getInputFromPort('vectors_color_type')
    vectors_resolution = 6
    if self.hasInputFromPort('vectors_resolution') :
      vectors_resolution = self.getInputFromPort('vectors_resolution')
    tensors_has_data = 0
    if self.hasInputFromPort('tensors_has_data') :
      tensors_has_data = self.getInputFromPort('tensors_has_data')
    tensors_on = 0
    if self.hasInputFromPort('tensors_on') :
      tensors_on = self.getInputFromPort('tensors_on')
    tensors_display_type = 'Colored Boxes'
    if self.hasInputFromPort('tensors_display_type') :
      tensors_display_type = self.getInputFromPort('tensors_display_type')
    tensors_transparency = 0
    if self.hasInputFromPort('tensors_transparency') :
      tensors_transparency = self.getInputFromPort('tensors_transparency')
    tensors_normalize = 0
    if self.hasInputFromPort('tensors_normalize') :
      tensors_normalize = self.getInputFromPort('tensors_normalize')
    tensors_color_type = 0
    if self.hasInputFromPort('tensors_color_type') :
      tensors_color_type = self.getInputFromPort('tensors_color_type')
    tensors_resolution = 6
    if self.hasInputFromPort('tensors_resolution') :
      tensors_resolution = self.getInputFromPort('tensors_resolution')
    tensors_emphasis = 0.825
    if self.hasInputFromPort('tensors_emphasis') :
      tensors_emphasis = self.getInputFromPort('tensors_emphasis')
    secondary_has_data = 0
    if self.hasInputFromPort('secondary_has_data') :
      secondary_has_data = self.getInputFromPort('secondary_has_data')
    secondary_on = 0
    if self.hasInputFromPort('secondary_on') :
      secondary_on = self.getInputFromPort('secondary_on')
    secondary_display_type = 'Major Radius'
    if self.hasInputFromPort('secondary_display_type') :
      secondary_display_type = self.getInputFromPort('secondary_display_type')
    secondary_color_type = 0
    if self.hasInputFromPort('secondary_color_type') :
      secondary_color_type = self.getInputFromPort('secondary_color_type')
    secondary_alpha = 0
    if self.hasInputFromPort('secondary_alpha') :
      secondary_alpha = self.getInputFromPort('secondary_alpha')
    secondary_value = 1
    if self.hasInputFromPort('secondary_value') :
      secondary_value = self.getInputFromPort('secondary_value')
    tertiary_has_data = 0
    if self.hasInputFromPort('tertiary_has_data') :
      tertiary_has_data = self.getInputFromPort('tertiary_has_data')
    tertiary_on = 0
    if self.hasInputFromPort('tertiary_on') :
      tertiary_on = self.getInputFromPort('tertiary_on')
    tertiary_display_type = 'Minor Radius'
    if self.hasInputFromPort('tertiary_display_type') :
      tertiary_display_type = self.getInputFromPort('tertiary_display_type')
    tertiary_color_type = 0
    if self.hasInputFromPort('tertiary_color_type') :
      tertiary_color_type = self.getInputFromPort('tertiary_color_type')
    tertiary_alpha = 0
    if self.hasInputFromPort('tertiary_alpha') :
      tertiary_alpha = self.getInputFromPort('tertiary_alpha')
    tertiary_value = 1
    if self.hasInputFromPort('tertiary_value') :
      tertiary_value = self.getInputFromPort('tertiary_value')
    text_on = 0
    if self.hasInputFromPort('text_on') :
      text_on = self.getInputFromPort('text_on')
    text_color_type = 0
    if self.hasInputFromPort('text_color_type') :
      text_color_type = self.getInputFromPort('text_color_type')
    text_color_r = 1.0
    if self.hasInputFromPort('text_color_r') :
      text_color_r = self.getInputFromPort('text_color_r')
    text_color_g = 1.0
    if self.hasInputFromPort('text_color_g') :
      text_color_g = self.getInputFromPort('text_color_g')
    text_color_b = 1.0
    if self.hasInputFromPort('text_color_b') :
      text_color_b = self.getInputFromPort('text_color_b')
    text_backface_cull = 0
    if self.hasInputFromPort('text_backface_cull') :
      text_backface_cull = self.getInputFromPort('text_backface_cull')
    text_always_visible = 0
    if self.hasInputFromPort('text_always_visible') :
      text_always_visible = self.getInputFromPort('text_always_visible')
    text_fontsize = 0
    if self.hasInputFromPort('text_fontsize') :
      text_fontsize = self.getInputFromPort('text_fontsize')
    text_precision = 3
    if self.hasInputFromPort('text_precision') :
      text_precision = self.getInputFromPort('text_precision')
    text_render_locations = 0
    if self.hasInputFromPort('text_render_locations') :
      text_render_locations = self.getInputFromPort('text_render_locations')
    text_show_data = 1
    if self.hasInputFromPort('text_show_data') :
      text_show_data = self.getInputFromPort('text_show_data')
    text_show_nodes = 0
    if self.hasInputFromPort('text_show_nodes') :
      text_show_nodes = self.getInputFromPort('text_show_nodes')
    text_show_edges = 0
    if self.hasInputFromPort('text_show_edges') :
      text_show_edges = self.getInputFromPort('text_show_edges')
    text_show_faces = 0
    if self.hasInputFromPort('text_show_faces') :
      text_show_faces = self.getInputFromPort('text_show_faces')
    text_show_cells = 0
    if self.hasInputFromPort('text_show_cells') :
      text_show_cells = self.getInputFromPort('text_show_cells')
    def_color_r = 0.5
    if self.hasInputFromPort('def_color_r') :
      def_color_r = self.getInputFromPort('def_color_r')
    def_color_g = 0.5
    if self.hasInputFromPort('def_color_g') :
      def_color_g = self.getInputFromPort('def_color_g')
    def_color_b = 0.5
    if self.hasInputFromPort('def_color_b') :
      def_color_b = self.getInputFromPort('def_color_b')
    def_color_a = 0.75
    if self.hasInputFromPort('def_color_a') :
      def_color_a = self.getInputFromPort('def_color_a')
    active_tab = 'Scalars'
    if self.hasInputFromPort('active_tab') :
      active_tab = self.getInputFromPort('active_tab')
    interactive_mode = 'Interactive'
    if self.hasInputFromPort('interactive_mode') :
      interactive_mode = self.getInputFromPort('interactive_mode')
    show_progress = 0
    if self.hasInputFromPort('show_progress') :
      show_progress = self.getInputFromPort('show_progress')
    field_name = ''
    if self.hasInputFromPort('field_name') :
      field_name = self.getInputFromPort('field_name')
    field_name_override = 0
    if self.hasInputFromPort('field_name_override') :
      field_name_override = self.getInputFromPort('field_name_override')
    approx_div = 1
    if self.hasInputFromPort('approx_div') :
      approx_div = self.getInputFromPort('approx_div')
    use_default_size = 0
    if self.hasInputFromPort('use_default_size') :
      use_default_size = self.getInputFromPort('use_default_size')
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
    results = sr_py.ShowFieldGlyphs(Primary_Data,Primary_ColorMap,Secondary_Data,Secondary_ColorMap,Tertiary_Data,Tertiary_ColorMap,scalars_has_data,scalars_on,scalars_display_type,scalars_transparency,scalars_normalize,scalars_color_type,scalars_resolution,vectors_has_data,vectors_on,vectors_display_type,vectors_transparency,vectors_normalize,vectors_bidirectional,vectors_color_type,vectors_resolution,tensors_has_data,tensors_on,tensors_display_type,tensors_transparency,tensors_normalize,tensors_color_type,tensors_resolution,tensors_emphasis,secondary_has_data,secondary_on,secondary_display_type,secondary_color_type,secondary_alpha,secondary_value,tertiary_has_data,tertiary_on,tertiary_display_type,tertiary_color_type,tertiary_alpha,tertiary_value,text_on,text_color_type,text_color_r,text_color_g,text_color_b,text_backface_cull,text_always_visible,text_fontsize,text_precision,text_render_locations,text_show_data,text_show_nodes,text_show_edges,text_show_faces,text_show_cells,def_color_r,def_color_g,def_color_b,def_color_a,active_tab,interactive_mode,show_progress,field_name,field_name_override,approx_div,use_default_size)
    self.setResult('Scene Graph', results)

class SCIRun_JoinBundles(Module) :
  def compute(self) :
    bundle = 0
    if self.hasInputFromPort('bundle') :
      bundle = self.getInputFromPort('bundle')
    results = sr_py.JoinBundles(bundle)
    self.setResult('bundle', results)

class SCIRun_ReportBundleInfo(Module) :
  def compute(self) :
    tclinfostring = ''
    if self.hasInputFromPort('tclinfostring') :
      tclinfostring = self.getInputFromPort('tclinfostring')
    bundle = 0
    if self.hasInputFromPort('bundle') :
      bundle = self.getInputFromPort('bundle')
    results = sr_py.ReportBundleInfo(bundle,tclinfostring)

class SCIRun_GetFieldData(Module) :
  def compute(self) :
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    results = sr_py.GetFieldData(Field)
    self.setResult('Data', results)

class SCIRun_ReportDataArrayMeasure(Module) :
  def compute(self) :
    measure = 'Sum'
    if self.hasInputFromPort('measure') :
      measure = self.getInputFromPort('measure')
    Array = 0
    if self.hasInputFromPort('Array') :
      Array = self.getInputFromPort('Array')
    results = sr_py.ReportDataArrayMeasure(Array,measure)
    self.setResult('Measure', results)

class SCIRun_CalculateFieldData2(Module) :
  def compute(self) :
    function = 'RESULT = abs(DATA1);'
    if self.hasInputFromPort('function') :
      function = self.getInputFromPort('function')
    format = 'Scalar'
    if self.hasInputFromPort('format') :
      format = self.getInputFromPort('format')
    Field1 = 0
    if self.hasInputFromPort('Field1') :
      Field1 = self.getInputFromPort('Field1')
    Field2 = 0
    if self.hasInputFromPort('Field2') :
      Field2 = self.getInputFromPort('Field2')
    Function = 0
    if self.hasInputFromPort('Function') :
      Function = self.getInputFromPort('Function')
    Array = 0
    if self.hasInputFromPort('Array') :
      Array = self.getInputFromPort('Array')
    results = sr_py.CalculateFieldData2(Field1,Field2,Function,Array,function,format)
    self.setResult('Field', results)

class SCIRun_SplitFileName(Module) :
  def compute(self) :
    Filename = 0
    if self.hasInputFromPort('Filename') :
      Filename = self.getInputFromPort('Filename')
    results = sr_py.SplitFileName(Filename)
    self.setResult('Pathname', sr_py.read_at_index(results,0))
    self.setResult('Filename Base', sr_py.read_at_index(results,1))
    self.setResult('Extension', sr_py.read_at_index(results,2))
    self.setResult('Filename', sr_py.read_at_index(results,3))

class SCIRun_SmoothMesh(Module) :
  def compute(self) :
    Input = 0
    if self.hasInputFromPort('Input') :
      Input = self.getInputFromPort('Input')
    IsoValue = 0
    if self.hasInputFromPort('IsoValue') :
      IsoValue = self.getInputFromPort('IsoValue')
    results = sr_py.SmoothMesh(Input,IsoValue)
    self.setResult('Smoothed', results)

class SCIRun_GenerateSinglePointProbeFromField(Module) :
  def compute(self) :
    main_frame = ''
    if self.hasInputFromPort('main_frame') :
      main_frame = self.getInputFromPort('main_frame')
    locx = 0.0
    if self.hasInputFromPort('locx') :
      locx = self.getInputFromPort('locx')
    locy = 0.0
    if self.hasInputFromPort('locy') :
      locy = self.getInputFromPort('locy')
    locz = 0.0
    if self.hasInputFromPort('locz') :
      locz = self.getInputFromPort('locz')
    value = ''
    if self.hasInputFromPort('value') :
      value = self.getInputFromPort('value')
    node = ''
    if self.hasInputFromPort('node') :
      node = self.getInputFromPort('node')
    edge = ''
    if self.hasInputFromPort('edge') :
      edge = self.getInputFromPort('edge')
    face = ''
    if self.hasInputFromPort('face') :
      face = self.getInputFromPort('face')
    cell = ''
    if self.hasInputFromPort('cell') :
      cell = self.getInputFromPort('cell')
    show_value = 1
    if self.hasInputFromPort('show_value') :
      show_value = self.getInputFromPort('show_value')
    show_node = 1
    if self.hasInputFromPort('show_node') :
      show_node = self.getInputFromPort('show_node')
    show_edge = 0
    if self.hasInputFromPort('show_edge') :
      show_edge = self.getInputFromPort('show_edge')
    show_face = 0
    if self.hasInputFromPort('show_face') :
      show_face = self.getInputFromPort('show_face')
    show_cell = 1
    if self.hasInputFromPort('show_cell') :
      show_cell = self.getInputFromPort('show_cell')
    probe_scale = 5.0
    if self.hasInputFromPort('probe_scale') :
      probe_scale = self.getInputFromPort('probe_scale')
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    results = sr_py.GenerateSinglePointProbeFromField(Input_Field,main_frame,locx,locy,locz,value,node,edge,face,cell,show_value,show_node,show_edge,show_face,show_cell,probe_scale)
    self.setResult('GenerateSinglePointProbeFromField Widget', sr_py.read_at_index(results,0))
    self.setResult('GenerateSinglePointProbeFromField Point', sr_py.read_at_index(results,1))
    self.setResult('Element Index', sr_py.read_at_index(results,2))

class SCIRun_CalculateInsideWhichField(Module) :
  def compute(self) :
    outputbasis = 'same as input'
    if self.hasInputFromPort('outputbasis') :
      outputbasis = self.getInputFromPort('outputbasis')
    outputtype = 'double'
    if self.hasInputFromPort('outputtype') :
      outputtype = self.getInputFromPort('outputtype')
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    Object = 0
    if self.hasInputFromPort('Object') :
      Object = self.getInputFromPort('Object')
    results = sr_py.CalculateInsideWhichField(Field,Object,outputbasis,outputtype)
    self.setResult('Field', results)

class SCIRun_InsertPathsIntoBundle(Module) :
  def compute(self) :
    path1_name = 'path1'
    if self.hasInputFromPort('path1_name') :
      path1_name = self.getInputFromPort('path1_name')
    path2_name = 'path2'
    if self.hasInputFromPort('path2_name') :
      path2_name = self.getInputFromPort('path2_name')
    path3_name = 'path3'
    if self.hasInputFromPort('path3_name') :
      path3_name = self.getInputFromPort('path3_name')
    path4_name = 'path4'
    if self.hasInputFromPort('path4_name') :
      path4_name = self.getInputFromPort('path4_name')
    path5_name = 'path5'
    if self.hasInputFromPort('path5_name') :
      path5_name = self.getInputFromPort('path5_name')
    path6_name = 'path6'
    if self.hasInputFromPort('path6_name') :
      path6_name = self.getInputFromPort('path6_name')
    replace1 = 1
    if self.hasInputFromPort('replace1') :
      replace1 = self.getInputFromPort('replace1')
    replace2 = 1
    if self.hasInputFromPort('replace2') :
      replace2 = self.getInputFromPort('replace2')
    replace3 = 1
    if self.hasInputFromPort('replace3') :
      replace3 = self.getInputFromPort('replace3')
    replace4 = 1
    if self.hasInputFromPort('replace4') :
      replace4 = self.getInputFromPort('replace4')
    replace5 = 1
    if self.hasInputFromPort('replace5') :
      replace5 = self.getInputFromPort('replace5')
    replace6 = 1
    if self.hasInputFromPort('replace6') :
      replace6 = self.getInputFromPort('replace6')
    bundlename = ''
    if self.hasInputFromPort('bundlename') :
      bundlename = self.getInputFromPort('bundlename')
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
    results = sr_py.InsertPathsIntoBundle(bundle,path1,path2,path3,path4,path5,path6,path1_name,path2_name,path3_name,path4_name,path5_name,path6_name,replace1,replace2,replace3,replace4,replace5,replace6,bundlename)
    self.setResult('bundle', results)

class SCIRun_RemoveZerosFromMatrix(Module) :
  def compute(self) :
    row_or_col = 'row'
    if self.hasInputFromPort('row_or_col') :
      row_or_col = self.getInputFromPort('row_or_col')
    Matrix = 0
    if self.hasInputFromPort('Matrix') :
      Matrix = self.getInputFromPort('Matrix')
    results = sr_py.RemoveZerosFromMatrix(Matrix,row_or_col)
    self.setResult('Matrix', results)

class SCIRun_GetNetworkFileName(Module) :
  def compute(self) :
    results = sr_py.GetNetworkFileName()
    self.setResult('String', results)

class SCIRun_RemoveZeroRowsAndColumns(Module) :
  def compute(self) :
    Matrix = 0
    if self.hasInputFromPort('Matrix') :
      Matrix = self.getInputFromPort('Matrix')
    results = sr_py.RemoveZeroRowsAndColumns(Matrix)
    self.setResult('ReducedMatrix', sr_py.read_at_index(results,0))
    self.setResult('LeftMapping', sr_py.read_at_index(results,1))
    self.setResult('RightMapping', sr_py.read_at_index(results,2))

class SCIRun_CalculateGradients(Module) :
  def compute(self) :
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    results = sr_py.CalculateGradients(Input_Field)
    self.setResult('Output CalculateGradients', results)

class SCIRun_CalculateLatVolGradientsAtNodes(Module) :
  def compute(self) :
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    results = sr_py.CalculateLatVolGradientsAtNodes(Input_Field)
    self.setResult('Output Gradient', results)

class SCIRun_GetColorMap2sFromBundle(Module) :
  def compute(self) :
    colormap21_name = 'colormap21'
    if self.hasInputFromPort('colormap21_name') :
      colormap21_name = self.getInputFromPort('colormap21_name')
    colormap22_name = 'colormap22'
    if self.hasInputFromPort('colormap22_name') :
      colormap22_name = self.getInputFromPort('colormap22_name')
    colormap23_name = 'colormap23'
    if self.hasInputFromPort('colormap23_name') :
      colormap23_name = self.getInputFromPort('colormap23_name')
    colormap24_name = 'colormap24'
    if self.hasInputFromPort('colormap24_name') :
      colormap24_name = self.getInputFromPort('colormap24_name')
    colormap25_name = 'colormap25'
    if self.hasInputFromPort('colormap25_name') :
      colormap25_name = self.getInputFromPort('colormap25_name')
    colormap26_name = 'colormap26'
    if self.hasInputFromPort('colormap26_name') :
      colormap26_name = self.getInputFromPort('colormap26_name')
    colormap2_selection = ''
    if self.hasInputFromPort('colormap2_selection') :
      colormap2_selection = self.getInputFromPort('colormap2_selection')
    bundle = 0
    if self.hasInputFromPort('bundle') :
      bundle = self.getInputFromPort('bundle')
    results = sr_py.GetColorMap2sFromBundle(bundle,colormap21_name,colormap22_name,colormap23_name,colormap24_name,colormap25_name,colormap26_name,colormap2_selection)
    self.setResult('bundle', sr_py.read_at_index(results,0))
    self.setResult('colormap21', sr_py.read_at_index(results,1))
    self.setResult('colormap22', sr_py.read_at_index(results,2))
    self.setResult('colormap23', sr_py.read_at_index(results,3))
    self.setResult('colormap24', sr_py.read_at_index(results,4))
    self.setResult('colormap25', sr_py.read_at_index(results,5))
    self.setResult('colormap26', sr_py.read_at_index(results,6))

class SCIRun_ReadMatrix(Module) :
  def compute(self) :
    from_env = ''
    if self.hasInputFromPort('from_env') :
      from_env = self.getInputFromPort('from_env')
    Filename = 0
    if self.hasInputFromPort('Filename') :
      Filename = self.getInputFromPort('Filename')
    results = sr_py.ReadMatrix(Filename,from_env)
    self.setResult('Output Data', sr_py.read_at_index(results,0))
    self.setResult('Filename', sr_py.read_at_index(results,1))

class SCIRun_GenerateStreamLines(Module) :
  def compute(self) :
    stepsize = 0.01
    if self.hasInputFromPort('stepsize') :
      stepsize = self.getInputFromPort('stepsize')
    tolerance = 0.0001
    if self.hasInputFromPort('tolerance') :
      tolerance = self.getInputFromPort('tolerance')
    maxsteps = 2000
    if self.hasInputFromPort('maxsteps') :
      maxsteps = self.getInputFromPort('maxsteps')
    direction = 1
    if self.hasInputFromPort('direction') :
      direction = self.getInputFromPort('direction')
    value = 1
    if self.hasInputFromPort('value') :
      value = self.getInputFromPort('value')
    remove_colinear_pts = 1
    if self.hasInputFromPort('remove_colinear_pts') :
      remove_colinear_pts = self.getInputFromPort('remove_colinear_pts')
    method = 4
    if self.hasInputFromPort('method') :
      method = self.getInputFromPort('method')
    nthreads = 1
    if self.hasInputFromPort('nthreads') :
      nthreads = self.getInputFromPort('nthreads')
    auto_parameterize = 0
    if self.hasInputFromPort('auto_parameterize') :
      auto_parameterize = self.getInputFromPort('auto_parameterize')
    Vector_Field = 0
    if self.hasInputFromPort('Vector Field') :
      Vector_Field = self.getInputFromPort('Vector Field')
    Seed_Points = 0
    if self.hasInputFromPort('Seed Points') :
      Seed_Points = self.getInputFromPort('Seed Points')
    results = sr_py.GenerateStreamLines(Vector_Field,Seed_Points,stepsize,tolerance,maxsteps,direction,value,remove_colinear_pts,method,nthreads,auto_parameterize)
    self.setResult('Streamlines', results)

class SCIRun_EditMeshBoundingBox(Module) :
  def compute(self) :
    outputcenterx = 0.0
    if self.hasInputFromPort('outputcenterx') :
      outputcenterx = self.getInputFromPort('outputcenterx')
    outputcentery = 0.0
    if self.hasInputFromPort('outputcentery') :
      outputcentery = self.getInputFromPort('outputcentery')
    outputcenterz = 0.0
    if self.hasInputFromPort('outputcenterz') :
      outputcenterz = self.getInputFromPort('outputcenterz')
    outputsizex = 0.0
    if self.hasInputFromPort('outputsizex') :
      outputsizex = self.getInputFromPort('outputsizex')
    outputsizey = 0.0
    if self.hasInputFromPort('outputsizey') :
      outputsizey = self.getInputFromPort('outputsizey')
    outputsizez = 0.0
    if self.hasInputFromPort('outputsizez') :
      outputsizez = self.getInputFromPort('outputsizez')
    useoutputcenter = 0
    if self.hasInputFromPort('useoutputcenter') :
      useoutputcenter = self.getInputFromPort('useoutputcenter')
    useoutputsize = 0
    if self.hasInputFromPort('useoutputsize') :
      useoutputsize = self.getInputFromPort('useoutputsize')
    box_scale = -1.0
    if self.hasInputFromPort('box_scale') :
      box_scale = self.getInputFromPort('box_scale')
    box_mode = 0
    if self.hasInputFromPort('box_mode') :
      box_mode = self.getInputFromPort('box_mode')
    box_real_scale = -1.0
    if self.hasInputFromPort('box_real_scale') :
      box_real_scale = self.getInputFromPort('box_real_scale')
    box_center_x = 0.0
    if self.hasInputFromPort('box_center_x') :
      box_center_x = self.getInputFromPort('box_center_x')
    box_center_y = 0.0
    if self.hasInputFromPort('box_center_y') :
      box_center_y = self.getInputFromPort('box_center_y')
    box_center_z = 0.0
    if self.hasInputFromPort('box_center_z') :
      box_center_z = self.getInputFromPort('box_center_z')
    box_right_x = 0.0
    if self.hasInputFromPort('box_right_x') :
      box_right_x = self.getInputFromPort('box_right_x')
    box_right_y = 0.0
    if self.hasInputFromPort('box_right_y') :
      box_right_y = self.getInputFromPort('box_right_y')
    box_right_z = 0.0
    if self.hasInputFromPort('box_right_z') :
      box_right_z = self.getInputFromPort('box_right_z')
    box_down_x = 0.0
    if self.hasInputFromPort('box_down_x') :
      box_down_x = self.getInputFromPort('box_down_x')
    box_down_y = 0.0
    if self.hasInputFromPort('box_down_y') :
      box_down_y = self.getInputFromPort('box_down_y')
    box_down_z = 0.0
    if self.hasInputFromPort('box_down_z') :
      box_down_z = self.getInputFromPort('box_down_z')
    box_in_x = 0.0
    if self.hasInputFromPort('box_in_x') :
      box_in_x = self.getInputFromPort('box_in_x')
    box_in_y = 0.0
    if self.hasInputFromPort('box_in_y') :
      box_in_y = self.getInputFromPort('box_in_y')
    box_in_z = 0.0
    if self.hasInputFromPort('box_in_z') :
      box_in_z = self.getInputFromPort('box_in_z')
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    results = sr_py.EditMeshBoundingBox(Input_Field,outputcenterx,outputcentery,outputcenterz,outputsizex,outputsizey,outputsizez,useoutputcenter,useoutputsize,box_scale,box_mode,box_real_scale,box_center_x,box_center_y,box_center_z,box_right_x,box_right_y,box_right_z,box_down_x,box_down_y,box_down_z,box_in_x,box_in_y,box_in_z)
    self.setResult('Output Field', sr_py.read_at_index(results,0))
    self.setResult('Transformation Widget', sr_py.read_at_index(results,1))
    self.setResult('Transformation Matrix', sr_py.read_at_index(results,2))

class SCIRun_PrintStringIntoString(Module) :
  def compute(self) :
    formatstring = 'my string: %s'
    if self.hasInputFromPort('formatstring') :
      formatstring = self.getInputFromPort('formatstring')
    Format = 0
    if self.hasInputFromPort('Format') :
      Format = self.getInputFromPort('Format')
    Input = 0
    if self.hasInputFromPort('Input') :
      Input = self.getInputFromPort('Input')
    results = sr_py.PrintStringIntoString(Format,Input,formatstring)
    self.setResult('Output', results)

class SCIRun_SetFieldDataValues(Module) :
  def compute(self) :
    newval = 1.0
    if self.hasInputFromPort('newval') :
      newval = self.getInputFromPort('newval')
    InField = 0
    if self.hasInputFromPort('InField') :
      InField = self.getInputFromPort('InField')
    results = sr_py.SetFieldDataValues(InField,newval)
    self.setResult('OutField', results)

class SCIRun_GetSubmatrix(Module) :
  def compute(self) :
    mincol = '---'
    if self.hasInputFromPort('mincol') :
      mincol = self.getInputFromPort('mincol')
    maxcol = '---'
    if self.hasInputFromPort('maxcol') :
      maxcol = self.getInputFromPort('maxcol')
    minrow = '---'
    if self.hasInputFromPort('minrow') :
      minrow = self.getInputFromPort('minrow')
    maxrow = '---'
    if self.hasInputFromPort('maxrow') :
      maxrow = self.getInputFromPort('maxrow')
    nrow = '??'
    if self.hasInputFromPort('nrow') :
      nrow = self.getInputFromPort('nrow')
    ncol = '??'
    if self.hasInputFromPort('ncol') :
      ncol = self.getInputFromPort('ncol')
    Input_Matrix = 0
    if self.hasInputFromPort('Input Matrix') :
      Input_Matrix = self.getInputFromPort('Input Matrix')
    Optional_Range_Bounds = 0
    if self.hasInputFromPort('Optional Range Bounds') :
      Optional_Range_Bounds = self.getInputFromPort('Optional Range Bounds')
    results = sr_py.GetSubmatrix(Input_Matrix,Optional_Range_Bounds,mincol,maxcol,minrow,maxrow,nrow,ncol)
    self.setResult('Output Matrix', results)

class SCIRun_GenerateStreamLinesWithPlacementHeuristic(Module) :
  def compute(self) :
    numsl = 10
    if self.hasInputFromPort('numsl') :
      numsl = self.getInputFromPort('numsl')
    numpts = 10
    if self.hasInputFromPort('numpts') :
      numpts = self.getInputFromPort('numpts')
    minper = 0
    if self.hasInputFromPort('minper') :
      minper = self.getInputFromPort('minper')
    maxper = 1
    if self.hasInputFromPort('maxper') :
      maxper = self.getInputFromPort('maxper')
    ming = 0
    if self.hasInputFromPort('ming') :
      ming = self.getInputFromPort('ming')
    maxg = 1
    if self.hasInputFromPort('maxg') :
      maxg = self.getInputFromPort('maxg')
    numsamples = 3
    if self.hasInputFromPort('numsamples') :
      numsamples = self.getInputFromPort('numsamples')
    method = 0
    if self.hasInputFromPort('method') :
      method = self.getInputFromPort('method')
    stepsize = 0.01
    if self.hasInputFromPort('stepsize') :
      stepsize = self.getInputFromPort('stepsize')
    stepout = 100
    if self.hasInputFromPort('stepout') :
      stepout = self.getInputFromPort('stepout')
    maxsteps = 10000
    if self.hasInputFromPort('maxsteps') :
      maxsteps = self.getInputFromPort('maxsteps')
    minmag = '1e-07'
    if self.hasInputFromPort('minmag') :
      minmag = self.getInputFromPort('minmag')
    direction = 1
    if self.hasInputFromPort('direction') :
      direction = self.getInputFromPort('direction')
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
    results = sr_py.GenerateStreamLinesWithPlacementHeuristic(Source,Weighting,Flow,Compare,Seed_points,numsl,numpts,minper,maxper,ming,maxg,numsamples,method,stepsize,stepout,maxsteps,minmag,direction)
    self.setResult('Streamlines', sr_py.read_at_index(results,0))
    self.setResult('Render', sr_py.read_at_index(results,1))

class SCIRun_CalculateSignedDistanceToField(Module) :
  def compute(self) :
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    ObjectField = 0
    if self.hasInputFromPort('ObjectField') :
      ObjectField = self.getInputFromPort('ObjectField')
    results = sr_py.CalculateSignedDistanceToField(Field,ObjectField)
    self.setResult('SignedDistanceField', results)

class SCIRun_EvaluateLinAlgUnary(Module) :
  def compute(self) :
    op = 'Function'
    if self.hasInputFromPort('op') :
      op = self.getInputFromPort('op')
    function = 'x+10'
    if self.hasInputFromPort('function') :
      function = self.getInputFromPort('function')
    Input = 0
    if self.hasInputFromPort('Input') :
      Input = self.getInputFromPort('Input')
    results = sr_py.EvaluateLinAlgUnary(Input,op,function)
    self.setResult('Output', results)

class SCIRun_InsertMatricesIntoBundle(Module) :
  def compute(self) :
    matrix1_name = 'matrix1'
    if self.hasInputFromPort('matrix1_name') :
      matrix1_name = self.getInputFromPort('matrix1_name')
    matrix2_name = 'matrix2'
    if self.hasInputFromPort('matrix2_name') :
      matrix2_name = self.getInputFromPort('matrix2_name')
    matrix3_name = 'matrix3'
    if self.hasInputFromPort('matrix3_name') :
      matrix3_name = self.getInputFromPort('matrix3_name')
    matrix4_name = 'matrix4'
    if self.hasInputFromPort('matrix4_name') :
      matrix4_name = self.getInputFromPort('matrix4_name')
    matrix5_name = 'matrix5'
    if self.hasInputFromPort('matrix5_name') :
      matrix5_name = self.getInputFromPort('matrix5_name')
    matrix6_name = 'matrix6'
    if self.hasInputFromPort('matrix6_name') :
      matrix6_name = self.getInputFromPort('matrix6_name')
    replace1 = 1
    if self.hasInputFromPort('replace1') :
      replace1 = self.getInputFromPort('replace1')
    replace2 = 1
    if self.hasInputFromPort('replace2') :
      replace2 = self.getInputFromPort('replace2')
    replace3 = 1
    if self.hasInputFromPort('replace3') :
      replace3 = self.getInputFromPort('replace3')
    replace4 = 1
    if self.hasInputFromPort('replace4') :
      replace4 = self.getInputFromPort('replace4')
    replace5 = 1
    if self.hasInputFromPort('replace5') :
      replace5 = self.getInputFromPort('replace5')
    replace6 = 1
    if self.hasInputFromPort('replace6') :
      replace6 = self.getInputFromPort('replace6')
    bundlename = ''
    if self.hasInputFromPort('bundlename') :
      bundlename = self.getInputFromPort('bundlename')
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
    results = sr_py.InsertMatricesIntoBundle(bundle,matrix1,matrix2,matrix3,matrix4,matrix5,matrix6,matrix1_name,matrix2_name,matrix3_name,matrix4_name,matrix5_name,matrix6_name,replace1,replace2,replace3,replace4,replace5,replace6,bundlename)
    self.setResult('bundle', results)

class SCIRun_AppendDataArrays(Module) :
  def compute(self) :
    Array = 0
    if self.hasInputFromPort('Array') :
      Array = self.getInputFromPort('Array')
    results = sr_py.AppendDataArrays(Array)
    self.setResult('Array', results)

class SCIRun_WriteString(Module) :
  def compute(self) :
    filetype = 'Binary'
    if self.hasInputFromPort('filetype') :
      filetype = self.getInputFromPort('filetype')
    confirm = 0
    if self.hasInputFromPort('confirm') :
      confirm = self.getInputFromPort('confirm')
    confirm_once = 0
    if self.hasInputFromPort('confirm_once') :
      confirm_once = self.getInputFromPort('confirm_once')
    String = 0
    if self.hasInputFromPort('String') :
      String = self.getInputFromPort('String')
    Filename = 0
    if self.hasInputFromPort('Filename') :
      Filename = self.getInputFromPort('Filename')
    results = sr_py.WriteString(String,Filename,filetype,confirm,confirm_once)

class SCIRun_TimeControls(Module) :
  def compute(self) :
    results = sr_py.TimeControls()
    self.setResult('time', results)

class SCIRun_InsertNrrdsIntoBundle(Module) :
  def compute(self) :
    nrrd1_name = 'nrrd1'
    if self.hasInputFromPort('nrrd1_name') :
      nrrd1_name = self.getInputFromPort('nrrd1_name')
    nrrd2_name = 'nrrd2'
    if self.hasInputFromPort('nrrd2_name') :
      nrrd2_name = self.getInputFromPort('nrrd2_name')
    nrrd3_name = 'nrrd3'
    if self.hasInputFromPort('nrrd3_name') :
      nrrd3_name = self.getInputFromPort('nrrd3_name')
    nrrd4_name = 'nrrd4'
    if self.hasInputFromPort('nrrd4_name') :
      nrrd4_name = self.getInputFromPort('nrrd4_name')
    nrrd5_name = 'nrrd5'
    if self.hasInputFromPort('nrrd5_name') :
      nrrd5_name = self.getInputFromPort('nrrd5_name')
    nrrd6_name = 'nrrd6'
    if self.hasInputFromPort('nrrd6_name') :
      nrrd6_name = self.getInputFromPort('nrrd6_name')
    replace1 = 1
    if self.hasInputFromPort('replace1') :
      replace1 = self.getInputFromPort('replace1')
    replace2 = 1
    if self.hasInputFromPort('replace2') :
      replace2 = self.getInputFromPort('replace2')
    replace3 = 1
    if self.hasInputFromPort('replace3') :
      replace3 = self.getInputFromPort('replace3')
    replace4 = 1
    if self.hasInputFromPort('replace4') :
      replace4 = self.getInputFromPort('replace4')
    replace5 = 1
    if self.hasInputFromPort('replace5') :
      replace5 = self.getInputFromPort('replace5')
    replace6 = 1
    if self.hasInputFromPort('replace6') :
      replace6 = self.getInputFromPort('replace6')
    bundlename = ''
    if self.hasInputFromPort('bundlename') :
      bundlename = self.getInputFromPort('bundlename')
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
    results = sr_py.InsertNrrdsIntoBundle(bundle,nrrd1,nrrd2,nrrd3,nrrd4,nrrd5,nrrd6,nrrd1_name,nrrd2_name,nrrd3_name,nrrd4_name,nrrd5_name,nrrd6_name,replace1,replace2,replace3,replace4,replace5,replace6,bundlename)
    self.setResult('bundle', results)

class SCIRun_InterfaceWithCubit(Module) :
  def compute(self) :
    cubitdir = '.'
    if self.hasInputFromPort('cubitdir') :
      cubitdir = self.getInputFromPort('cubitdir')
    ncdump = 'ncdump'
    if self.hasInputFromPort('ncdump') :
      ncdump = self.getInputFromPort('ncdump')
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    PointCloudField = 0
    if self.hasInputFromPort('PointCloudField') :
      PointCloudField = self.getInputFromPort('PointCloudField')
    results = sr_py.InterfaceWithCubit(Field,PointCloudField,cubitdir,ncdump)
    self.setResult('Field', results)

class SCIRun_CreateString(Module) :
  def compute(self) :
    inputstring = ''
    if self.hasInputFromPort('inputstring') :
      inputstring = self.getInputFromPort('inputstring')
    results = sr_py.CreateString(inputstring)
    self.setResult('Output', results)

class SCIRun_ClipFieldByFunction(Module) :
  def compute(self) :
    mode = 'allnodes'
    if self.hasInputFromPort('mode') :
      mode = self.getInputFromPort('mode')
    function = 'return (x < 0);'
    if self.hasInputFromPort('function') :
      function = self.getInputFromPort('function')
    Function = 0
    if self.hasInputFromPort('Function') :
      Function = self.getInputFromPort('Function')
    Input = 0
    if self.hasInputFromPort('Input') :
      Input = self.getInputFromPort('Input')
    results = sr_py.ClipFieldByFunction(Function,Input,mode,function)
    self.setResult('Clipped', sr_py.read_at_index(results,0))
    self.setResult('Mapping', sr_py.read_at_index(results,1))
    self.setResult('MaskVector', sr_py.read_at_index(results,2))

class SCIRun_CreateTensorArray(Module) :
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

class SCIRun_WriteField(Module) :
  def compute(self) :
    filetype = 'Binary'
    if self.hasInputFromPort('filetype') :
      filetype = self.getInputFromPort('filetype')
    confirm = 0
    if self.hasInputFromPort('confirm') :
      confirm = self.getInputFromPort('confirm')
    confirm_once = 0
    if self.hasInputFromPort('confirm_once') :
      confirm_once = self.getInputFromPort('confirm_once')
    exporttype = ''
    if self.hasInputFromPort('exporttype') :
      exporttype = self.getInputFromPort('exporttype')
    increment = 0
    if self.hasInputFromPort('increment') :
      increment = self.getInputFromPort('increment')
    current = 0
    if self.hasInputFromPort('current') :
      current = self.getInputFromPort('current')
    Input_Data = 0
    if self.hasInputFromPort('Input Data') :
      Input_Data = self.getInputFromPort('Input Data')
    Filename = 0
    if self.hasInputFromPort('Filename') :
      Filename = self.getInputFromPort('Filename')
    results = sr_py.WriteField(Input_Data,Filename,filetype,confirm,confirm_once,exporttype,increment,current)

class SCIRun_BuildMappingMatrix(Module) :
  def compute(self) :
    interpolation_basis = 'linear'
    if self.hasInputFromPort('interpolation_basis') :
      interpolation_basis = self.getInputFromPort('interpolation_basis')
    map_source_to_single_dest = 0
    if self.hasInputFromPort('map_source_to_single_dest') :
      map_source_to_single_dest = self.getInputFromPort('map_source_to_single_dest')
    exhaustive_search = 0
    if self.hasInputFromPort('exhaustive_search') :
      exhaustive_search = self.getInputFromPort('exhaustive_search')
    exhaustive_search_max_dist = -1.0
    if self.hasInputFromPort('exhaustive_search_max_dist') :
      exhaustive_search_max_dist = self.getInputFromPort('exhaustive_search_max_dist')
    np = 1
    if self.hasInputFromPort('np') :
      np = self.getInputFromPort('np')
    Source = 0
    if self.hasInputFromPort('Source') :
      Source = self.getInputFromPort('Source')
    Destination = 0
    if self.hasInputFromPort('Destination') :
      Destination = self.getInputFromPort('Destination')
    results = sr_py.BuildMappingMatrix(Source,Destination,interpolation_basis,map_source_to_single_dest,exhaustive_search,exhaustive_search_max_dist,np)
    self.setResult('Mapping', results)

class SCIRun_MapFieldDataFromNodeToElem(Module) :
  def compute(self) :
    method = 'Interpolate'
    if self.hasInputFromPort('method') :
      method = self.getInputFromPort('method')
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    results = sr_py.MapFieldDataFromNodeToElem(Field,method)
    self.setResult('Field', results)

class SCIRun_InsertBundlesIntoBundle(Module) :
  def compute(self) :
    bundle1_name = 'bundle1'
    if self.hasInputFromPort('bundle1_name') :
      bundle1_name = self.getInputFromPort('bundle1_name')
    bundle2_name = 'bundle2'
    if self.hasInputFromPort('bundle2_name') :
      bundle2_name = self.getInputFromPort('bundle2_name')
    bundle3_name = 'bundle3'
    if self.hasInputFromPort('bundle3_name') :
      bundle3_name = self.getInputFromPort('bundle3_name')
    bundle4_name = 'bundle4'
    if self.hasInputFromPort('bundle4_name') :
      bundle4_name = self.getInputFromPort('bundle4_name')
    bundle5_name = 'bundle5'
    if self.hasInputFromPort('bundle5_name') :
      bundle5_name = self.getInputFromPort('bundle5_name')
    bundle6_name = 'bundle6'
    if self.hasInputFromPort('bundle6_name') :
      bundle6_name = self.getInputFromPort('bundle6_name')
    replace1 = 1
    if self.hasInputFromPort('replace1') :
      replace1 = self.getInputFromPort('replace1')
    replace2 = 1
    if self.hasInputFromPort('replace2') :
      replace2 = self.getInputFromPort('replace2')
    replace3 = 1
    if self.hasInputFromPort('replace3') :
      replace3 = self.getInputFromPort('replace3')
    replace4 = 1
    if self.hasInputFromPort('replace4') :
      replace4 = self.getInputFromPort('replace4')
    replace5 = 1
    if self.hasInputFromPort('replace5') :
      replace5 = self.getInputFromPort('replace5')
    replace6 = 1
    if self.hasInputFromPort('replace6') :
      replace6 = self.getInputFromPort('replace6')
    bundlename = ''
    if self.hasInputFromPort('bundlename') :
      bundlename = self.getInputFromPort('bundlename')
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
    results = sr_py.InsertBundlesIntoBundle(bundle,bundle1,bundle2,bundle3,bundle4,bundle5,bundle6,bundle1_name,bundle2_name,bundle3_name,bundle4_name,bundle5_name,bundle6_name,replace1,replace2,replace3,replace4,replace5,replace6,bundlename)
    self.setResult('bundle', results)

class SCIRun_ReadBundle(Module) :
  def compute(self) :
    from_env = ''
    if self.hasInputFromPort('from_env') :
      from_env = self.getInputFromPort('from_env')
    types = 'SCIRun Bundle File} {.bdl} } {{SCIRun Bundle Any} {.*} } '
    if self.hasInputFromPort('types') :
      types = self.getInputFromPort('types')
    Filename = 0
    if self.hasInputFromPort('Filename') :
      Filename = self.getInputFromPort('Filename')
    results = sr_py.ReadBundle(Filename,from_env,types)
    self.setResult('bundle', sr_py.read_at_index(results,0))
    self.setResult('Filename', sr_py.read_at_index(results,1))

class SCIRun_GetStringsFromBundle(Module) :
  def compute(self) :
    string1_name = 'string1'
    if self.hasInputFromPort('string1_name') :
      string1_name = self.getInputFromPort('string1_name')
    string2_name = 'string2'
    if self.hasInputFromPort('string2_name') :
      string2_name = self.getInputFromPort('string2_name')
    string3_name = 'string3'
    if self.hasInputFromPort('string3_name') :
      string3_name = self.getInputFromPort('string3_name')
    string4_name = 'string4'
    if self.hasInputFromPort('string4_name') :
      string4_name = self.getInputFromPort('string4_name')
    string5_name = 'string5'
    if self.hasInputFromPort('string5_name') :
      string5_name = self.getInputFromPort('string5_name')
    string6_name = 'string6'
    if self.hasInputFromPort('string6_name') :
      string6_name = self.getInputFromPort('string6_name')
    string_selection = ''
    if self.hasInputFromPort('string_selection') :
      string_selection = self.getInputFromPort('string_selection')
    bundle = 0
    if self.hasInputFromPort('bundle') :
      bundle = self.getInputFromPort('bundle')
    results = sr_py.GetStringsFromBundle(bundle,string1_name,string2_name,string3_name,string4_name,string5_name,string6_name,string_selection)
    self.setResult('bundle', sr_py.read_at_index(results,0))
    self.setResult('string1', sr_py.read_at_index(results,1))
    self.setResult('string2', sr_py.read_at_index(results,2))
    self.setResult('string3', sr_py.read_at_index(results,3))
    self.setResult('string4', sr_py.read_at_index(results,4))
    self.setResult('string5', sr_py.read_at_index(results,5))
    self.setResult('string6', sr_py.read_at_index(results,6))

class SCIRun_ShowString(Module) :
  def compute(self) :
    bbox = 1
    if self.hasInputFromPort('bbox') :
      bbox = self.getInputFromPort('bbox')
    size = 1
    if self.hasInputFromPort('size') :
      size = self.getInputFromPort('size')
    location_x = -0.96875
    if self.hasInputFromPort('location_x') :
      location_x = self.getInputFromPort('location_x')
    location_y = 0.96875
    if self.hasInputFromPort('location_y') :
      location_y = self.getInputFromPort('location_y')
    color_r = 1.0
    if self.hasInputFromPort('color_r') :
      color_r = self.getInputFromPort('color_r')
    color_g = 1.0
    if self.hasInputFromPort('color_g') :
      color_g = self.getInputFromPort('color_g')
    color_b = 1.0
    if self.hasInputFromPort('color_b') :
      color_b = self.getInputFromPort('color_b')
    Format_String = 0
    if self.hasInputFromPort('Format String') :
      Format_String = self.getInputFromPort('Format String')
    results = sr_py.ShowString(Format_String,bbox,size,location_x,location_y,color_r,color_g,color_b)
    self.setResult('Title', results)

class SCIRun_ReportStringInfo(Module) :
  def compute(self) :
    inputstring = ''
    if self.hasInputFromPort('inputstring') :
      inputstring = self.getInputFromPort('inputstring')
    Input = 0
    if self.hasInputFromPort('Input') :
      Input = self.getInputFromPort('Input')
    results = sr_py.ReportStringInfo(Input,inputstring)

class SCIRun_SortMatrix(Module) :
  def compute(self) :
    row_or_col = 'row'
    if self.hasInputFromPort('row_or_col') :
      row_or_col = self.getInputFromPort('row_or_col')
    Matrix = 0
    if self.hasInputFromPort('Matrix') :
      Matrix = self.getInputFromPort('Matrix')
    results = sr_py.SortMatrix(Matrix,row_or_col)
    self.setResult('Matrix', results)

class SCIRun_SwapNodeLocationsWithMatrixEntries(Module) :
  def compute(self) :
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    Input_Matrix = 0
    if self.hasInputFromPort('Input Matrix') :
      Input_Matrix = self.getInputFromPort('Input Matrix')
    results = sr_py.SwapNodeLocationsWithMatrixEntries(Input_Field,Input_Matrix)
    self.setResult('Output Field', sr_py.read_at_index(results,0))
    self.setResult('Output Matrix', sr_py.read_at_index(results,1))

class SCIRun_ReorderMatrixByReverseCuthillMcKee(Module) :
  def compute(self) :
    Matrix = 0
    if self.hasInputFromPort('Matrix') :
      Matrix = self.getInputFromPort('Matrix')
    results = sr_py.ReorderMatrixByReverseCuthillMcKee(Matrix)
    self.setResult('Matrix', sr_py.read_at_index(results,0))
    self.setResult('Mapping', sr_py.read_at_index(results,1))
    self.setResult('InverseMapping', sr_py.read_at_index(results,2))

class SCIRun_GetDomainBoundary(Module) :
  def compute(self) :
    userange = 0
    if self.hasInputFromPort('userange') :
      userange = self.getInputFromPort('userange')
    minrange = 0.0
    if self.hasInputFromPort('minrange') :
      minrange = self.getInputFromPort('minrange')
    maxrange = 255.0
    if self.hasInputFromPort('maxrange') :
      maxrange = self.getInputFromPort('maxrange')
    usevalue = 0
    if self.hasInputFromPort('usevalue') :
      usevalue = self.getInputFromPort('usevalue')
    value = 1.0
    if self.hasInputFromPort('value') :
      value = self.getInputFromPort('value')
    includeouterboundary = 1
    if self.hasInputFromPort('includeouterboundary') :
      includeouterboundary = self.getInputFromPort('includeouterboundary')
    innerboundaryonly = 0
    if self.hasInputFromPort('innerboundaryonly') :
      innerboundaryonly = self.getInputFromPort('innerboundaryonly')
    noinnerboundary = 0
    if self.hasInputFromPort('noinnerboundary') :
      noinnerboundary = self.getInputFromPort('noinnerboundary')
    disconnect = 1
    if self.hasInputFromPort('disconnect') :
      disconnect = self.getInputFromPort('disconnect')
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    MinValueValue = 0
    if self.hasInputFromPort('MinValueValue') :
      MinValueValue = self.getInputFromPort('MinValueValue')
    MaxValue = 0
    if self.hasInputFromPort('MaxValue') :
      MaxValue = self.getInputFromPort('MaxValue')
    results = sr_py.GetDomainBoundary(Field,MinValueValue,MaxValue,userange,minrange,maxrange,usevalue,value,includeouterboundary,innerboundaryonly,noinnerboundary,disconnect)
    self.setResult('Field', results)

class SCIRun_CollectFields(Module) :
  def compute(self) :
    buffersize = 20
    if self.hasInputFromPort('buffersize') :
      buffersize = self.getInputFromPort('buffersize')
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    BufferSize = 0
    if self.hasInputFromPort('BufferSize') :
      BufferSize = self.getInputFromPort('BufferSize')
    results = sr_py.CollectFields(Field,BufferSize,buffersize)
    self.setResult('Fields', results)

class SCIRun_ScaleFieldMeshAndData(Module) :
  def compute(self) :
    datascale = 1
    if self.hasInputFromPort('datascale') :
      datascale = self.getInputFromPort('datascale')
    geomscale = 1
    if self.hasInputFromPort('geomscale') :
      geomscale = self.getInputFromPort('geomscale')
    usegeomcenter = 1
    if self.hasInputFromPort('usegeomcenter') :
      usegeomcenter = self.getInputFromPort('usegeomcenter')
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    GeomScaleFactor = 0
    if self.hasInputFromPort('GeomScaleFactor') :
      GeomScaleFactor = self.getInputFromPort('GeomScaleFactor')
    DataScaleFactor = 0
    if self.hasInputFromPort('DataScaleFactor') :
      DataScaleFactor = self.getInputFromPort('DataScaleFactor')
    results = sr_py.ScaleFieldMeshAndData(Field,GeomScaleFactor,DataScaleFactor,datascale,geomscale,usegeomcenter)
    self.setResult('Field', results)

class SCIRun_StreamMatrixFromDisk(Module) :
  def compute(self) :
    row_or_col = 'column'
    if self.hasInputFromPort('row_or_col') :
      row_or_col = self.getInputFromPort('row_or_col')
    slider_min = 0
    if self.hasInputFromPort('slider_min') :
      slider_min = self.getInputFromPort('slider_min')
    slider_max = 100
    if self.hasInputFromPort('slider_max') :
      slider_max = self.getInputFromPort('slider_max')
    range_min = 0
    if self.hasInputFromPort('range_min') :
      range_min = self.getInputFromPort('range_min')
    range_max = 100
    if self.hasInputFromPort('range_max') :
      range_max = self.getInputFromPort('range_max')
    playmode = 'once'
    if self.hasInputFromPort('playmode') :
      playmode = self.getInputFromPort('playmode')
    current = 0
    if self.hasInputFromPort('current') :
      current = self.getInputFromPort('current')
    execmode = 'init'
    if self.hasInputFromPort('execmode') :
      execmode = self.getInputFromPort('execmode')
    delay = 0
    if self.hasInputFromPort('delay') :
      delay = self.getInputFromPort('delay')
    inc_amount = 1
    if self.hasInputFromPort('inc_amount') :
      inc_amount = self.getInputFromPort('inc_amount')
    send_amount = 1
    if self.hasInputFromPort('send_amount') :
      send_amount = self.getInputFromPort('send_amount')
    Indices = 0
    if self.hasInputFromPort('Indices') :
      Indices = self.getInputFromPort('Indices')
    Weights = 0
    if self.hasInputFromPort('Weights') :
      Weights = self.getInputFromPort('Weights')
    Filename = 0
    if self.hasInputFromPort('Filename') :
      Filename = self.getInputFromPort('Filename')
    results = sr_py.StreamMatrixFromDisk(Indices,Weights,Filename,row_or_col,slider_min,slider_max,range_min,range_max,playmode,current,execmode,delay,inc_amount,send_amount)
    self.setResult('DataVector', sr_py.read_at_index(results,0))
    self.setResult('Index', sr_py.read_at_index(results,1))
    self.setResult('Scaled Index', sr_py.read_at_index(results,2))
    self.setResult('Filename', sr_py.read_at_index(results,3))

class SCIRun_WriteMatrix(Module) :
  def compute(self) :
    filetype = 'Binary'
    if self.hasInputFromPort('filetype') :
      filetype = self.getInputFromPort('filetype')
    confirm = 0
    if self.hasInputFromPort('confirm') :
      confirm = self.getInputFromPort('confirm')
    confirm_once = 0
    if self.hasInputFromPort('confirm_once') :
      confirm_once = self.getInputFromPort('confirm_once')
    exporttype = ''
    if self.hasInputFromPort('exporttype') :
      exporttype = self.getInputFromPort('exporttype')
    split = 0
    if self.hasInputFromPort('split') :
      split = self.getInputFromPort('split')
    Input_Data = 0
    if self.hasInputFromPort('Input Data') :
      Input_Data = self.getInputFromPort('Input Data')
    Filename = 0
    if self.hasInputFromPort('Filename') :
      Filename = self.getInputFromPort('Filename')
    results = sr_py.WriteMatrix(Input_Data,Filename,filetype,confirm,confirm_once,exporttype,split)

class SCIRun_ConvertFieldDataType(Module) :
  def compute(self) :
    outputdatatype = 'double'
    if self.hasInputFromPort('outputdatatype') :
      outputdatatype = self.getInputFromPort('outputdatatype')
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    results = sr_py.ConvertFieldDataType(Input_Field,outputdatatype)
    self.setResult('Output Field', results)

class SCIRun_GetSliceFromStructuredFieldByIndices(Module) :
  def compute(self) :
    axis = 2
    if self.hasInputFromPort('axis') :
      axis = self.getInputFromPort('axis')
    dims = 3
    if self.hasInputFromPort('dims') :
      dims = self.getInputFromPort('dims')
    dim_i = 1
    if self.hasInputFromPort('dim_i') :
      dim_i = self.getInputFromPort('dim_i')
    dim_j = 1
    if self.hasInputFromPort('dim_j') :
      dim_j = self.getInputFromPort('dim_j')
    dim_k = 1
    if self.hasInputFromPort('dim_k') :
      dim_k = self.getInputFromPort('dim_k')
    index_i = 1
    if self.hasInputFromPort('index_i') :
      index_i = self.getInputFromPort('index_i')
    index_j = 1
    if self.hasInputFromPort('index_j') :
      index_j = self.getInputFromPort('index_j')
    index_k = 1
    if self.hasInputFromPort('index_k') :
      index_k = self.getInputFromPort('index_k')
    update_type = 'Manual'
    if self.hasInputFromPort('update_type') :
      update_type = self.getInputFromPort('update_type')
    continuous = 0
    if self.hasInputFromPort('continuous') :
      continuous = self.getInputFromPort('continuous')
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    Input_Matrix = 0
    if self.hasInputFromPort('Input Matrix') :
      Input_Matrix = self.getInputFromPort('Input Matrix')
    results = sr_py.GetSliceFromStructuredFieldByIndices(Input_Field,Input_Matrix,axis,dims,dim_i,dim_j,dim_k,index_i,index_j,index_k,update_type,continuous)
    self.setResult('Output Field', sr_py.read_at_index(results,0))
    self.setResult('Output Matrix', sr_py.read_at_index(results,1))

class SCIRun_GeneratePointSamplesFromField(Module) :
  def compute(self) :
    num_seeds = 1
    if self.hasInputFromPort('num_seeds') :
      num_seeds = self.getInputFromPort('num_seeds')
    probe_scale = 5.0
    if self.hasInputFromPort('probe_scale') :
      probe_scale = self.getInputFromPort('probe_scale')
    send = 0
    if self.hasInputFromPort('send') :
      send = self.getInputFromPort('send')
    widget = 0
    if self.hasInputFromPort('widget') :
      widget = self.getInputFromPort('widget')
    red = 0.5
    if self.hasInputFromPort('red') :
      red = self.getInputFromPort('red')
    green = 0.5
    if self.hasInputFromPort('green') :
      green = self.getInputFromPort('green')
    blue = 0.5
    if self.hasInputFromPort('blue') :
      blue = self.getInputFromPort('blue')
    auto_execute = 1
    if self.hasInputFromPort('auto_execute') :
      auto_execute = self.getInputFromPort('auto_execute')
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    results = sr_py.GeneratePointSamplesFromField(Input_Field,num_seeds,probe_scale,send,widget,red,green,blue,auto_execute)
    self.setResult('GeneratePointSamplesFromField Widget', sr_py.read_at_index(results,0))
    self.setResult('GeneratePointSamplesFromField Point', sr_py.read_at_index(results,1))

class SCIRun_CreateMatrix(Module) :
  def compute(self) :
    rows = 1
    if self.hasInputFromPort('rows') :
      rows = self.getInputFromPort('rows')
    cols = 1
    if self.hasInputFromPort('cols') :
      cols = self.getInputFromPort('cols')
    data = 0.0
    if self.hasInputFromPort('data') :
      data = self.getInputFromPort('data')
    clabel = 0
    if self.hasInputFromPort('clabel') :
      clabel = self.getInputFromPort('clabel')
    rlabel = 0
    if self.hasInputFromPort('rlabel') :
      rlabel = self.getInputFromPort('rlabel')
    results = sr_py.CreateMatrix(rows,cols,data,clabel,rlabel)
    self.setResult('matrix', results)

class SCIRun_DecimateTriSurf(Module) :
  def compute(self) :
    TriSurf = 0
    if self.hasInputFromPort('TriSurf') :
      TriSurf = self.getInputFromPort('TriSurf')
    results = sr_py.DecimateTriSurf(TriSurf)
    self.setResult('Decimated', results)

class SCIRun_GeneratePointSamplesFromFieldOrWidget(Module) :
  def compute(self) :
    wtype = 'rake'
    if self.hasInputFromPort('wtype') :
      wtype = self.getInputFromPort('wtype')
    endpoints = 0
    if self.hasInputFromPort('endpoints') :
      endpoints = self.getInputFromPort('endpoints')
    maxseeds = 15.0
    if self.hasInputFromPort('maxseeds') :
      maxseeds = self.getInputFromPort('maxseeds')
    numseeds = 10
    if self.hasInputFromPort('numseeds') :
      numseeds = self.getInputFromPort('numseeds')
    rngseed = 1
    if self.hasInputFromPort('rngseed') :
      rngseed = self.getInputFromPort('rngseed')
    rnginc = 1
    if self.hasInputFromPort('rnginc') :
      rnginc = self.getInputFromPort('rnginc')
    clamp = 0
    if self.hasInputFromPort('clamp') :
      clamp = self.getInputFromPort('clamp')
    autoexecute = 1
    if self.hasInputFromPort('autoexecute') :
      autoexecute = self.getInputFromPort('autoexecute')
    dist = 'uniuni'
    if self.hasInputFromPort('dist') :
      dist = self.getInputFromPort('dist')
    whichtab = 'Widget'
    if self.hasInputFromPort('whichtab') :
      whichtab = self.getInputFromPort('whichtab')
    Field_to_Sample = 0
    if self.hasInputFromPort('Field to Sample') :
      Field_to_Sample = self.getInputFromPort('Field to Sample')
    results = sr_py.GeneratePointSamplesFromFieldOrWidget(Field_to_Sample,wtype,endpoints,maxseeds,numseeds,rngseed,rnginc,clamp,autoexecute,dist,whichtab)
    self.setResult('Samples', sr_py.read_at_index(results,0))
    self.setResult('Sampling Widget', sr_py.read_at_index(results,1))

class SCIRun_CalculateIsInsideField(Module) :
  def compute(self) :
    outputbasis = 'same as input'
    if self.hasInputFromPort('outputbasis') :
      outputbasis = self.getInputFromPort('outputbasis')
    outputtype = 'double'
    if self.hasInputFromPort('outputtype') :
      outputtype = self.getInputFromPort('outputtype')
    outval = 0
    if self.hasInputFromPort('outval') :
      outval = self.getInputFromPort('outval')
    inval = 1
    if self.hasInputFromPort('inval') :
      inval = self.getInputFromPort('inval')
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    ObjectField = 0
    if self.hasInputFromPort('ObjectField') :
      ObjectField = self.getInputFromPort('ObjectField')
    results = sr_py.CalculateIsInsideField(Field,ObjectField,outputbasis,outputtype,outval,inval)
    self.setResult('Field', results)

class SCIRun_CreateAndEditColorMap(Module) :
  def compute(self) :
    rgbhsv = 1
    if self.hasInputFromPort('rgbhsv') :
      rgbhsv = self.getInputFromPort('rgbhsv')
    rgb_points = '0 0.05 0.1 0 1 0.95 0.9 1 '
    if self.hasInputFromPort('rgb_points') :
      rgb_points = self.getInputFromPort('rgb_points')
    alpha_points = '0 0 0 0.25 0.5 0.5 0.8 0.75 0.8 1 '
    if self.hasInputFromPort('alpha_points') :
      alpha_points = self.getInputFromPort('alpha_points')
    resolution = 256
    if self.hasInputFromPort('resolution') :
      resolution = self.getInputFromPort('resolution')
    ColorMap = 0
    if self.hasInputFromPort('ColorMap') :
      ColorMap = self.getInputFromPort('ColorMap')
    results = sr_py.CreateAndEditColorMap(ColorMap,rgbhsv,rgb_points,alpha_points,resolution)
    self.setResult('ColorMap', sr_py.read_at_index(results,0))
    self.setResult('Geometry', sr_py.read_at_index(results,1))

class SCIRun_CoregisterPointClouds(Module) :
  def compute(self) :
    allowScale = 1
    if self.hasInputFromPort('allowScale') :
      allowScale = self.getInputFromPort('allowScale')
    allowRotate = 1
    if self.hasInputFromPort('allowRotate') :
      allowRotate = self.getInputFromPort('allowRotate')
    allowTranslate = 1
    if self.hasInputFromPort('allowTranslate') :
      allowTranslate = self.getInputFromPort('allowTranslate')
    seed = 1
    if self.hasInputFromPort('seed') :
      seed = self.getInputFromPort('seed')
    iters = 1000
    if self.hasInputFromPort('iters') :
      iters = self.getInputFromPort('iters')
    misfitTol = 0.001
    if self.hasInputFromPort('misfitTol') :
      misfitTol = self.getInputFromPort('misfitTol')
    method = 'Analytic'
    if self.hasInputFromPort('method') :
      method = self.getInputFromPort('method')
    Fixed_PointCloudField = 0
    if self.hasInputFromPort('Fixed PointCloudField') :
      Fixed_PointCloudField = self.getInputFromPort('Fixed PointCloudField')
    Mobile_PointCloudField = 0
    if self.hasInputFromPort('Mobile PointCloudField') :
      Mobile_PointCloudField = self.getInputFromPort('Mobile PointCloudField')
    DistanceField_From_Fixed = 0
    if self.hasInputFromPort('DistanceField From Fixed') :
      DistanceField_From_Fixed = self.getInputFromPort('DistanceField From Fixed')
    results = sr_py.CoregisterPointClouds(Fixed_PointCloudField,Mobile_PointCloudField,DistanceField_From_Fixed,allowScale,allowRotate,allowTranslate,seed,iters,misfitTol,method)
    self.setResult('Transform', results)

class SCIRun_SolveMinNormLeastSqSystem(Module) :
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
    self.setResult('WeightVec(Col)', sr_py.read_at_index(results,0))
    self.setResult('ResultVec(Col)', sr_py.read_at_index(results,1))

class SCIRun_CalculateFieldData(Module) :
  def compute(self) :
    function = 'RESULT = abs(DATA);'
    if self.hasInputFromPort('function') :
      function = self.getInputFromPort('function')
    format = 'Scalar'
    if self.hasInputFromPort('format') :
      format = self.getInputFromPort('format')
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    Function = 0
    if self.hasInputFromPort('Function') :
      Function = self.getInputFromPort('Function')
    Array = 0
    if self.hasInputFromPort('Array') :
      Array = self.getInputFromPort('Array')
    results = sr_py.CalculateFieldData(Field,Function,Array,function,format)
    self.setResult('Field', results)

class SCIRun_MapFieldDataToNodeCoordinate(Module) :
  def compute(self) :
    coord = 2
    if self.hasInputFromPort('coord') :
      coord = self.getInputFromPort('coord')
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    results = sr_py.MapFieldDataToNodeCoordinate(Input_Field,coord)
    self.setResult('Output Field', results)

class SCIRun_ShowMeshBoundingBox(Module) :
  def compute(self) :
    sizex = 10
    if self.hasInputFromPort('sizex') :
      sizex = self.getInputFromPort('sizex')
    sizey = 10
    if self.hasInputFromPort('sizey') :
      sizey = self.getInputFromPort('sizey')
    sizez = 10
    if self.hasInputFromPort('sizez') :
      sizez = self.getInputFromPort('sizez')
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    results = sr_py.ShowMeshBoundingBox(Field,sizex,sizey,sizez)
    self.setResult('Scene Graph', results)

class SCIRun_ViewGraph(Module) :
  def compute(self) :
    Title = 0
    if self.hasInputFromPort('Title') :
      Title = self.getInputFromPort('Title')
    Input = 0
    if self.hasInputFromPort('Input') :
      Input = self.getInputFromPort('Input')
    results = sr_py.ViewGraph(Title,Input)

class SCIRun_GetAllSegmentationBoundaries(Module) :
  def compute(self) :
    Segmentations = 0
    if self.hasInputFromPort('Segmentations') :
      Segmentations = self.getInputFromPort('Segmentations')
    results = sr_py.GetAllSegmentationBoundaries(Segmentations)
    self.setResult('Boundaries', results)

class SCIRun_CreateStandardColorMaps(Module) :
  def compute(self) :
    mapName = 'Rainbow'
    if self.hasInputFromPort('mapName') :
      mapName = self.getInputFromPort('mapName')
    gamma = 0.0
    if self.hasInputFromPort('gamma') :
      gamma = self.getInputFromPort('gamma')
    resolution = 256
    if self.hasInputFromPort('resolution') :
      resolution = self.getInputFromPort('resolution')
    reverse = 0
    if self.hasInputFromPort('reverse') :
      reverse = self.getInputFromPort('reverse')
    faux = 0
    if self.hasInputFromPort('faux') :
      faux = self.getInputFromPort('faux')
    positionList = ''
    if self.hasInputFromPort('positionList') :
      positionList = self.getInputFromPort('positionList')
    nodeList = ''
    if self.hasInputFromPort('nodeList') :
      nodeList = self.getInputFromPort('nodeList')
    width = 1
    if self.hasInputFromPort('width') :
      width = self.getInputFromPort('width')
    height = 1
    if self.hasInputFromPort('height') :
      height = self.getInputFromPort('height')
    results = sr_py.CreateStandardColorMaps(mapName,gamma,resolution,reverse,faux,positionList,nodeList,width,height)
    self.setResult('ColorMap', results)

class SCIRun_ShowTextureSlices(Module) :
  def compute(self) :
    control_pos_saved = 0
    if self.hasInputFromPort('control_pos_saved') :
      control_pos_saved = self.getInputFromPort('control_pos_saved')
    drawX = 0
    if self.hasInputFromPort('drawX') :
      drawX = self.getInputFromPort('drawX')
    drawY = 0
    if self.hasInputFromPort('drawY') :
      drawY = self.getInputFromPort('drawY')
    drawZ = 0
    if self.hasInputFromPort('drawZ') :
      drawZ = self.getInputFromPort('drawZ')
    drawView = 0
    if self.hasInputFromPort('drawView') :
      drawView = self.getInputFromPort('drawView')
    interp_mode = 1
    if self.hasInputFromPort('interp_mode') :
      interp_mode = self.getInputFromPort('interp_mode')
    draw_phi_0 = 0
    if self.hasInputFromPort('draw_phi_0') :
      draw_phi_0 = self.getInputFromPort('draw_phi_0')
    draw_phi_1 = 0
    if self.hasInputFromPort('draw_phi_1') :
      draw_phi_1 = self.getInputFromPort('draw_phi_1')
    phi_0 = 30.0
    if self.hasInputFromPort('phi_0') :
      phi_0 = self.getInputFromPort('phi_0')
    phi_1 = 60.0
    if self.hasInputFromPort('phi_1') :
      phi_1 = self.getInputFromPort('phi_1')
    multi_level = 1
    if self.hasInputFromPort('multi_level') :
      multi_level = self.getInputFromPort('multi_level')
    color_changed = 1
    if self.hasInputFromPort('color_changed') :
      color_changed = self.getInputFromPort('color_changed')
    colors = ''
    if self.hasInputFromPort('colors') :
      colors = self.getInputFromPort('colors')
    level_on = ''
    if self.hasInputFromPort('level_on') :
      level_on = self.getInputFromPort('level_on')
    outline_levels = 0
    if self.hasInputFromPort('outline_levels') :
      outline_levels = self.getInputFromPort('outline_levels')
    use_stencil = 0
    if self.hasInputFromPort('use_stencil') :
      use_stencil = self.getInputFromPort('use_stencil')
    Texture = 0
    if self.hasInputFromPort('Texture') :
      Texture = self.getInputFromPort('Texture')
    ColorMap = 0
    if self.hasInputFromPort('ColorMap') :
      ColorMap = self.getInputFromPort('ColorMap')
    ColorMap2 = 0
    if self.hasInputFromPort('ColorMap2') :
      ColorMap2 = self.getInputFromPort('ColorMap2')
    results = sr_py.ShowTextureSlices(Texture,ColorMap,ColorMap2,control_pos_saved,drawX,drawY,drawZ,drawView,interp_mode,draw_phi_0,draw_phi_1,phi_0,phi_1,multi_level,color_changed,colors,level_on,outline_levels,use_stencil)
    self.setResult('Geometry', sr_py.read_at_index(results,0))
    self.setResult('ColorMap', sr_py.read_at_index(results,1))

class SCIRun_ShowMatrix(Module) :
  def compute(self) :
    xpos = 0.0
    if self.hasInputFromPort('xpos') :
      xpos = self.getInputFromPort('xpos')
    ypos = 0.0
    if self.hasInputFromPort('ypos') :
      ypos = self.getInputFromPort('ypos')
    xscale = 1.0
    if self.hasInputFromPort('xscale') :
      xscale = self.getInputFromPort('xscale')
    yscale = 2.0
    if self.hasInputFromPort('yscale') :
      yscale = self.getInputFromPort('yscale')
    a3d_mode = 1
    if self.hasInputFromPort('a3d_mode') :
      a3d_mode = self.getInputFromPort('a3d_mode')
    gmode = 1
    if self.hasInputFromPort('gmode') :
      gmode = self.getInputFromPort('gmode')
    showtext = 0
    if self.hasInputFromPort('showtext') :
      showtext = self.getInputFromPort('showtext')
    row_begin = 0
    if self.hasInputFromPort('row_begin') :
      row_begin = self.getInputFromPort('row_begin')
    rows = 10000
    if self.hasInputFromPort('rows') :
      rows = self.getInputFromPort('rows')
    col_begin = 0
    if self.hasInputFromPort('col_begin') :
      col_begin = self.getInputFromPort('col_begin')
    cols = 10000
    if self.hasInputFromPort('cols') :
      cols = self.getInputFromPort('cols')
    colormapmode = 0
    if self.hasInputFromPort('colormapmode') :
      colormapmode = self.getInputFromPort('colormapmode')
    ColorMap = 0
    if self.hasInputFromPort('ColorMap') :
      ColorMap = self.getInputFromPort('ColorMap')
    Matrix = 0
    if self.hasInputFromPort('Matrix') :
      Matrix = self.getInputFromPort('Matrix')
    results = sr_py.ShowMatrix(ColorMap,Matrix,xpos,ypos,xscale,yscale,a3d_mode,gmode,showtext,row_begin,rows,col_begin,cols,colormapmode)
    self.setResult('Geometry', results)

class SCIRun_CreateViewerClockIcon(Module) :
  def compute(self) :
    type = 0
    if self.hasInputFromPort('type') :
      type = self.getInputFromPort('type')
    bbox = 1
    if self.hasInputFromPort('bbox') :
      bbox = self.getInputFromPort('bbox')
    format = '%8.3f seconds'
    if self.hasInputFromPort('format') :
      format = self.getInputFromPort('format')
    min = 0.0
    if self.hasInputFromPort('min') :
      min = self.getInputFromPort('min')
    max = 1.0
    if self.hasInputFromPort('max') :
      max = self.getInputFromPort('max')
    current = 0
    if self.hasInputFromPort('current') :
      current = self.getInputFromPort('current')
    size = 100
    if self.hasInputFromPort('size') :
      size = self.getInputFromPort('size')
    location_x = -0.96875
    if self.hasInputFromPort('location_x') :
      location_x = self.getInputFromPort('location_x')
    location_y = 0.96875
    if self.hasInputFromPort('location_y') :
      location_y = self.getInputFromPort('location_y')
    color_r = 1.0
    if self.hasInputFromPort('color_r') :
      color_r = self.getInputFromPort('color_r')
    color_g = 1.0
    if self.hasInputFromPort('color_g') :
      color_g = self.getInputFromPort('color_g')
    color_b = 1.0
    if self.hasInputFromPort('color_b') :
      color_b = self.getInputFromPort('color_b')
    Time_Matrix = 0
    if self.hasInputFromPort('Time Matrix') :
      Time_Matrix = self.getInputFromPort('Time Matrix')
    Time_Nrrd = 0
    if self.hasInputFromPort('Time Nrrd') :
      Time_Nrrd = self.getInputFromPort('Time Nrrd')
    results = sr_py.CreateViewerClockIcon(Time_Matrix,Time_Nrrd,type,bbox,format,min,max,current,size,location_x,location_y,color_r,color_g,color_b)
    self.setResult('Clock', results)

class SCIRun_ConvertMatrixType(Module) :
  def compute(self) :
    oldtype = 'Same'
    if self.hasInputFromPort('oldtype') :
      oldtype = self.getInputFromPort('oldtype')
    newtype = 'Unknown'
    if self.hasInputFromPort('newtype') :
      newtype = self.getInputFromPort('newtype')
    nrow = '??'
    if self.hasInputFromPort('nrow') :
      nrow = self.getInputFromPort('nrow')
    ncol = '??'
    if self.hasInputFromPort('ncol') :
      ncol = self.getInputFromPort('ncol')
    Input = 0
    if self.hasInputFromPort('Input') :
      Input = self.getInputFromPort('Input')
    results = sr_py.ConvertMatrixType(Input,oldtype,newtype,nrow,ncol)
    self.setResult('Output', results)

class SCIRun_JoinStrings(Module) :
  def compute(self) :
    input = 0
    if self.hasInputFromPort('input') :
      input = self.getInputFromPort('input')
    results = sr_py.JoinStrings(input)
    self.setResult('Output', results)

class SCIRun_InsertColorMapsIntoBundle(Module) :
  def compute(self) :
    colormap1_name = 'colormap1'
    if self.hasInputFromPort('colormap1_name') :
      colormap1_name = self.getInputFromPort('colormap1_name')
    colormap2_name = 'colormap2'
    if self.hasInputFromPort('colormap2_name') :
      colormap2_name = self.getInputFromPort('colormap2_name')
    colormap3_name = 'colormap3'
    if self.hasInputFromPort('colormap3_name') :
      colormap3_name = self.getInputFromPort('colormap3_name')
    colormap4_name = 'colormap4'
    if self.hasInputFromPort('colormap4_name') :
      colormap4_name = self.getInputFromPort('colormap4_name')
    colormap5_name = 'colormap5'
    if self.hasInputFromPort('colormap5_name') :
      colormap5_name = self.getInputFromPort('colormap5_name')
    colormap6_name = 'colormap6'
    if self.hasInputFromPort('colormap6_name') :
      colormap6_name = self.getInputFromPort('colormap6_name')
    replace1 = 1
    if self.hasInputFromPort('replace1') :
      replace1 = self.getInputFromPort('replace1')
    replace2 = 1
    if self.hasInputFromPort('replace2') :
      replace2 = self.getInputFromPort('replace2')
    replace3 = 1
    if self.hasInputFromPort('replace3') :
      replace3 = self.getInputFromPort('replace3')
    replace4 = 1
    if self.hasInputFromPort('replace4') :
      replace4 = self.getInputFromPort('replace4')
    replace5 = 1
    if self.hasInputFromPort('replace5') :
      replace5 = self.getInputFromPort('replace5')
    replace6 = 1
    if self.hasInputFromPort('replace6') :
      replace6 = self.getInputFromPort('replace6')
    bundlename = ''
    if self.hasInputFromPort('bundlename') :
      bundlename = self.getInputFromPort('bundlename')
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
    results = sr_py.InsertColorMapsIntoBundle(bundle,colormap1,colormap2,colormap3,colormap4,colormap5,colormap6,colormap1_name,colormap2_name,colormap3_name,colormap4_name,colormap5_name,colormap6_name,replace1,replace2,replace3,replace4,replace5,replace6,bundlename)
    self.setResult('bundle', results)

class SCIRun_CollectPointClouds(Module) :
  def compute(self) :
    num_fields = 1
    if self.hasInputFromPort('num_fields') :
      num_fields = self.getInputFromPort('num_fields')
    Point_Cloud = 0
    if self.hasInputFromPort('Point Cloud') :
      Point_Cloud = self.getInputFromPort('Point Cloud')
    results = sr_py.CollectPointClouds(Point_Cloud,num_fields)
    self.setResult('Curve', results)

class SCIRun_ReorderMatrixByCuthillMcKee(Module) :
  def compute(self) :
    Matrix = 0
    if self.hasInputFromPort('Matrix') :
      Matrix = self.getInputFromPort('Matrix')
    results = sr_py.ReorderMatrixByCuthillMcKee(Matrix)
    self.setResult('Matrix', sr_py.read_at_index(results,0))
    self.setResult('Mapping', sr_py.read_at_index(results,1))
    self.setResult('InverseMapping', sr_py.read_at_index(results,2))

class SCIRun_ReportMatrixRowMeasure(Module) :
  def compute(self) :
    method = 'Sum'
    if self.hasInputFromPort('method') :
      method = self.getInputFromPort('method')
    Matrix = 0
    if self.hasInputFromPort('Matrix') :
      Matrix = self.getInputFromPort('Matrix')
    results = sr_py.ReportMatrixRowMeasure(Matrix,method)
    self.setResult('Vector', results)

class SCIRun_RemoveHexVolSheet(Module) :
  def compute(self) :
    edge_list = 'No values present.'
    if self.hasInputFromPort('edge_list') :
      edge_list = self.getInputFromPort('edge_list')
    HexField = 0
    if self.hasInputFromPort('HexField') :
      HexField = self.getInputFromPort('HexField')
    results = sr_py.RemoveHexVolSheet(HexField,edge_list)
    self.setResult('NewHexField', sr_py.read_at_index(results,0))
    self.setResult('ExtractedHexes', sr_py.read_at_index(results,1))

class SCIRun_ColorMap2DSemantics(Module) :
  def compute(self) :
    Input_Colormap = 0
    if self.hasInputFromPort('Input Colormap') :
      Input_Colormap = self.getInputFromPort('Input Colormap')
    results = sr_py.ColorMap2DSemantics(Input_Colormap)
    self.setResult('Output Colormap', results)

class SCIRun_ReportMatrixInfo(Module) :
  def compute(self) :
    Input = 0
    if self.hasInputFromPort('Input') :
      Input = self.getInputFromPort('Input')
    results = sr_py.ReportMatrixInfo(Input)
    self.setResult('NumRows', sr_py.read_at_index(results,0))
    self.setResult('NumCols', sr_py.read_at_index(results,1))
    self.setResult('NumElements', sr_py.read_at_index(results,2))

class SCIRun_RefineMesh(Module) :
  def compute(self) :
    Mesh = 0
    if self.hasInputFromPort('Mesh') :
      Mesh = self.getInputFromPort('Mesh')
    Isovalue = 0
    if self.hasInputFromPort('Isovalue') :
      Isovalue = self.getInputFromPort('Isovalue')
    results = sr_py.RefineMesh(Mesh,Isovalue)
    self.setResult('RefinedMesh', sr_py.read_at_index(results,0))
    self.setResult('Mapping', sr_py.read_at_index(results,1))

class SCIRun_InsertEnvironmentIntoBundle(Module) :
  def compute(self) :
    results = sr_py.InsertEnvironmentIntoBundle()
    self.setResult('Environment', results)

class SCIRun_CalculateDistanceToField(Module) :
  def compute(self) :
    Field = 0
    if self.hasInputFromPort('Field') :
      Field = self.getInputFromPort('Field')
    ObjectField = 0
    if self.hasInputFromPort('ObjectField') :
      ObjectField = self.getInputFromPort('ObjectField')
    results = sr_py.CalculateDistanceToField(Field,ObjectField)
    self.setResult('DistanceField', results)

class SCIRun_SubsampleStructuredFieldByIndices(Module) :
  def compute(self) :
    power_app = 0
    if self.hasInputFromPort('power_app') :
      power_app = self.getInputFromPort('power_app')
    wrap = 0
    if self.hasInputFromPort('wrap') :
      wrap = self.getInputFromPort('wrap')
    dims = 3
    if self.hasInputFromPort('dims') :
      dims = self.getInputFromPort('dims')
    dim_i = 2
    if self.hasInputFromPort('dim_i') :
      dim_i = self.getInputFromPort('dim_i')
    dim_j = 2
    if self.hasInputFromPort('dim_j') :
      dim_j = self.getInputFromPort('dim_j')
    dim_k = 2
    if self.hasInputFromPort('dim_k') :
      dim_k = self.getInputFromPort('dim_k')
    start_i = 0
    if self.hasInputFromPort('start_i') :
      start_i = self.getInputFromPort('start_i')
    start_j = 0
    if self.hasInputFromPort('start_j') :
      start_j = self.getInputFromPort('start_j')
    start_k = 0
    if self.hasInputFromPort('start_k') :
      start_k = self.getInputFromPort('start_k')
    stop_i = 1
    if self.hasInputFromPort('stop_i') :
      stop_i = self.getInputFromPort('stop_i')
    stop_j = 1
    if self.hasInputFromPort('stop_j') :
      stop_j = self.getInputFromPort('stop_j')
    stop_k = 1
    if self.hasInputFromPort('stop_k') :
      stop_k = self.getInputFromPort('stop_k')
    stride_i = 1
    if self.hasInputFromPort('stride_i') :
      stride_i = self.getInputFromPort('stride_i')
    stride_j = 1
    if self.hasInputFromPort('stride_j') :
      stride_j = self.getInputFromPort('stride_j')
    stride_k = 1
    if self.hasInputFromPort('stride_k') :
      stride_k = self.getInputFromPort('stride_k')
    wrap_i = 0
    if self.hasInputFromPort('wrap_i') :
      wrap_i = self.getInputFromPort('wrap_i')
    wrap_j = 0
    if self.hasInputFromPort('wrap_j') :
      wrap_j = self.getInputFromPort('wrap_j')
    wrap_k = 0
    if self.hasInputFromPort('wrap_k') :
      wrap_k = self.getInputFromPort('wrap_k')
    Input_Field = 0
    if self.hasInputFromPort('Input Field') :
      Input_Field = self.getInputFromPort('Input Field')
    Input_Matrix = 0
    if self.hasInputFromPort('Input Matrix') :
      Input_Matrix = self.getInputFromPort('Input Matrix')
    results = sr_py.SubsampleStructuredFieldByIndices(Input_Field,Input_Matrix,power_app,wrap,dims,dim_i,dim_j,dim_k,start_i,start_j,start_k,stop_i,stop_j,stop_k,stride_i,stride_j,stride_k,wrap_i,wrap_j,wrap_k)
    self.setResult('Output Field', sr_py.read_at_index(results,0))
    self.setResult('Output Matrix', sr_py.read_at_index(results,1))

class SCIRun_Matrix(Constant):
  def compute(self): 
    pass
class SCIRun_Bundle(Constant):
  def compute(self): 
    pass
class SCIRun_Field(Constant):
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

  import viewercell
  viewercell.registerSelf()

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

  reg.add_module(SCIRun_Field)

  reg.add_module(SCIRun_Bundle)

  reg.add_module(SCIRun_Matrix)

  reg.add_module(SCIRun_CreateDataArray)
  reg.add_input_port(SCIRun_CreateDataArray, 'function',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_CreateDataArray, 'format',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_CreateDataArray, 'Size',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(SCIRun_CreateDataArray, 'Function',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_input_port(SCIRun_CreateDataArray, 'Array',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_CreateDataArray, 'DataArray', 
                    (SCIRun_Matrix, 'DataArray'))

  reg.add_module(SCIRun_WriteBundle)
  reg.add_input_port(SCIRun_WriteBundle, 'filetype',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_WriteBundle, 'confirm',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_WriteBundle, 'confirm_once',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_WriteBundle, 'bundle',
                   (SCIRun_Bundle, "SCIRun_Bundle"))
  reg.add_input_port(SCIRun_WriteBundle, 'Filename',
                   (core.modules.basic_modules.String, 'tip'))

  reg.add_module(SCIRun_JoinFields)
  reg.add_input_port(SCIRun_JoinFields, 'accumulating',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_JoinFields, 'tolerance',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_JoinFields, 'force_nodemerge',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_JoinFields, 'force_pointcloud',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_JoinFields, 'matchval',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_JoinFields, 'meshonly',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_JoinFields, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_JoinFields, 'Output Field', 
                    (SCIRun_Field, 'Output Field'))

  reg.add_module(SCIRun_MaskLatVolWithTriSurf)
  reg.add_input_port(SCIRun_MaskLatVolWithTriSurf, 'LatVolField',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_MaskLatVolWithTriSurf, 'TriSurfField',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_MaskLatVolWithTriSurf, 'LatVol Mask', 
                    (SCIRun_Field, 'LatVol Mask'))

  reg.add_module(SCIRun_ApplyMappingMatrix)
  reg.add_input_port(SCIRun_ApplyMappingMatrix, 'Source',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_ApplyMappingMatrix, 'Destination',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_ApplyMappingMatrix, 'Mapping',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_ApplyMappingMatrix, 'Output', 
                    (SCIRun_Field, 'Output'))

  reg.add_module(SCIRun_TransformPlanarMesh)
  reg.add_input_port(SCIRun_TransformPlanarMesh, 'axis',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_TransformPlanarMesh, 'invert',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_TransformPlanarMesh, 'trans_x',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_TransformPlanarMesh, 'trans_y',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_TransformPlanarMesh, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_TransformPlanarMesh, 'Index Matrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_TransformPlanarMesh, 'Transformed Field', 
                    (SCIRun_Field, 'Transformed Field'))

  reg.add_module(SCIRun_ViewScene)
  reg.add_input_port(SCIRun_ViewScene, 'Geometry',
                   (SCIRun_Geometry, "SCIRun_Geometry"))

  reg.add_module(SCIRun_RefineMeshByIsovalue)
  reg.add_input_port(SCIRun_RefineMeshByIsovalue, 'isoval',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_RefineMeshByIsovalue, 'lte',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_RefineMeshByIsovalue, 'Input',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_RefineMeshByIsovalue, 'Optional Isovalue',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_RefineMeshByIsovalue, 'Refined', 
                    (SCIRun_Field, 'Refined'))
  reg.add_output_port(SCIRun_RefineMeshByIsovalue, 'Mapping', 
                    (SCIRun_Matrix, 'Mapping'))

  reg.add_module(SCIRun_AppendMatrix)
  reg.add_input_port(SCIRun_AppendMatrix, 'row_or_column',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_AppendMatrix, 'BaseMatrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(SCIRun_AppendMatrix, 'AppendMatrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_AppendMatrix, 'Matrix', 
                    (SCIRun_Matrix, 'Matrix'))

  reg.add_module(SCIRun_ReportColumnMatrixMisfit)
  reg.add_input_port(SCIRun_ReportColumnMatrixMisfit, 'have_ui',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReportColumnMatrixMisfit, 'methodTCL',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ReportColumnMatrixMisfit, 'pTCL',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReportColumnMatrixMisfit, 'Vec1',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(SCIRun_ReportColumnMatrixMisfit, 'Vec2',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_ReportColumnMatrixMisfit, 'Error Out', 
                    (SCIRun_Matrix, 'Error Out'))

  reg.add_module(SCIRun_EvaluateLinAlgGeneral)
  reg.add_input_port(SCIRun_EvaluateLinAlgGeneral, 'function',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_EvaluateLinAlgGeneral, 'i1',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(SCIRun_EvaluateLinAlgGeneral, 'i2',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(SCIRun_EvaluateLinAlgGeneral, 'i3',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(SCIRun_EvaluateLinAlgGeneral, 'i4',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(SCIRun_EvaluateLinAlgGeneral, 'i5',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_EvaluateLinAlgGeneral, 'o1', 
                    (SCIRun_Matrix, 'o1'))
  reg.add_output_port(SCIRun_EvaluateLinAlgGeneral, 'o2', 
                    (SCIRun_Matrix, 'o2'))
  reg.add_output_port(SCIRun_EvaluateLinAlgGeneral, 'o3', 
                    (SCIRun_Matrix, 'o3'))
  reg.add_output_port(SCIRun_EvaluateLinAlgGeneral, 'o4', 
                    (SCIRun_Matrix, 'o4'))
  reg.add_output_port(SCIRun_EvaluateLinAlgGeneral, 'o5', 
                    (SCIRun_Matrix, 'o5'))

  reg.add_module(SCIRun_ReportMeshQualityMeasures)
  reg.add_input_port(SCIRun_ReportMeshQualityMeasures, 'Input',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_ReportMeshQualityMeasures, 'Checked', 
                    (SCIRun_Nrrd, 'Checked'))

  reg.add_module(SCIRun_ApplyFilterToFieldData)
  reg.add_input_port(SCIRun_ApplyFilterToFieldData, 'method',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ApplyFilterToFieldData, 'ed_method',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ApplyFilterToFieldData, 'ed_iterations',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ApplyFilterToFieldData, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_ApplyFilterToFieldData, 'Field', 
                    (SCIRun_Field, 'Field'))

  reg.add_module(SCIRun_FairMesh)
  reg.add_input_port(SCIRun_FairMesh, 'iterations',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_FairMesh, 'method',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_FairMesh, 'Input Mesh',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_FairMesh, 'Faired Mesh', 
                    (SCIRun_Field, 'Faired Mesh'))

  reg.add_module(SCIRun_EvaluateLinAlgBinary)
  reg.add_input_port(SCIRun_EvaluateLinAlgBinary, 'op',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_EvaluateLinAlgBinary, 'function',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_EvaluateLinAlgBinary, 'A',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(SCIRun_EvaluateLinAlgBinary, 'B',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_EvaluateLinAlgBinary, 'Output', 
                    (SCIRun_Matrix, 'Output'))

  reg.add_module(SCIRun_PrintMatrixIntoString)
  reg.add_input_port(SCIRun_PrintMatrixIntoString, 'formatstring',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_PrintMatrixIntoString, 'Format',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_input_port(SCIRun_PrintMatrixIntoString, 'Input',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_PrintMatrixIntoString, 'Output', 
                    (core.modules.basic_modules.String, 'Output'))

  reg.add_module(SCIRun_SetFieldProperty)
  reg.add_input_port(SCIRun_SetFieldProperty, 'num_entries',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_SetFieldProperty, 'property',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_SetFieldProperty, 'type',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_SetFieldProperty, 'value',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_SetFieldProperty, 'readonly',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_SetFieldProperty, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_SetFieldProperty, 'Field', 
                    (SCIRun_Field, 'Field'))

  reg.add_module(SCIRun_ConvertFieldBasis)
  reg.add_input_port(SCIRun_ConvertFieldBasis, 'output_basis',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ConvertFieldBasis, 'Input',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_ConvertFieldBasis, 'Output', 
                    (SCIRun_Field, 'Output'))
  reg.add_output_port(SCIRun_ConvertFieldBasis, 'Mapping', 
                    (SCIRun_Matrix, 'Mapping'))

  reg.add_module(SCIRun_CreateDataArrayFromIndices)
  reg.add_input_port(SCIRun_CreateDataArrayFromIndices, 'Indices',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(SCIRun_CreateDataArrayFromIndices, 'Template',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_CreateDataArrayFromIndices, 'DataArray', 
                    (SCIRun_Matrix, 'DataArray'))

  reg.add_module(SCIRun_SelectAndSetFieldData)
  reg.add_input_port(SCIRun_SelectAndSetFieldData, 'selection1',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_SelectAndSetFieldData, 'function1',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_SelectAndSetFieldData, 'selection2',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_SelectAndSetFieldData, 'function2',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_SelectAndSetFieldData, 'selection3',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_SelectAndSetFieldData, 'function3',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_SelectAndSetFieldData, 'selection4',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_SelectAndSetFieldData, 'function4',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_SelectAndSetFieldData, 'functiondef',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_SelectAndSetFieldData, 'format',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_SelectAndSetFieldData, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_SelectAndSetFieldData, 'Array',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_SelectAndSetFieldData, 'Field', 
                    (SCIRun_Field, 'Field'))

  reg.add_module(SCIRun_GetColorMapsFromBundle)
  reg.add_input_port(SCIRun_GetColorMapsFromBundle, 'colormap1_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetColorMapsFromBundle, 'colormap2_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetColorMapsFromBundle, 'colormap3_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetColorMapsFromBundle, 'colormap4_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetColorMapsFromBundle, 'colormap5_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetColorMapsFromBundle, 'colormap6_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetColorMapsFromBundle, 'colormap_selection',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetColorMapsFromBundle, 'bundle',
                   (SCIRun_Bundle, "SCIRun_Bundle"))
  reg.add_output_port(SCIRun_GetColorMapsFromBundle, 'bundle', 
                    (SCIRun_Bundle, 'bundle'))
  reg.add_output_port(SCIRun_GetColorMapsFromBundle, 'colormap1', 
                    (SCIRun_ColorMap, 'colormap1'))
  reg.add_output_port(SCIRun_GetColorMapsFromBundle, 'colormap2', 
                    (SCIRun_ColorMap, 'colormap2'))
  reg.add_output_port(SCIRun_GetColorMapsFromBundle, 'colormap3', 
                    (SCIRun_ColorMap, 'colormap3'))
  reg.add_output_port(SCIRun_GetColorMapsFromBundle, 'colormap4', 
                    (SCIRun_ColorMap, 'colormap4'))
  reg.add_output_port(SCIRun_GetColorMapsFromBundle, 'colormap5', 
                    (SCIRun_ColorMap, 'colormap5'))
  reg.add_output_port(SCIRun_GetColorMapsFromBundle, 'colormap6', 
                    (SCIRun_ColorMap, 'colormap6'))

  reg.add_module(SCIRun_CreateStructHex)
  reg.add_input_port(SCIRun_CreateStructHex, 'sizex',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateStructHex, 'sizey',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateStructHex, 'sizez',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateStructHex, 'padpercent',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateStructHex, 'data_at',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_CreateStructHex, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_CreateStructHex, 'Output Sample Field', 
                    (SCIRun_Field, 'Output Sample Field'))

  reg.add_module(SCIRun_ShowColorMap)
  reg.add_input_port(SCIRun_ShowColorMap, 'length',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ShowColorMap, 'side',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ShowColorMap, 'numlabels',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowColorMap, 'scale',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowColorMap, 'numsigdigits',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowColorMap, 'units',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ShowColorMap, 'color_r',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowColorMap, 'color_g',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowColorMap, 'color_b',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowColorMap, 'text_fontsize',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowColorMap, 'extra_padding',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowColorMap, 'ColorMap',
                   (SCIRun_ColorMap, "SCIRun_ColorMap"))
  reg.add_output_port(SCIRun_ShowColorMap, 'Geometry', 
                    (SCIRun_Geometry, 'Geometry'))

  reg.add_module(SCIRun_CalculateFieldData3)
  reg.add_input_port(SCIRun_CalculateFieldData3, 'function',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_CalculateFieldData3, 'format',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_CalculateFieldData3, 'Field1',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_CalculateFieldData3, 'Field2',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_CalculateFieldData3, 'Field3',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_CalculateFieldData3, 'Function',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_input_port(SCIRun_CalculateFieldData3, 'Array',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_CalculateFieldData3, 'Field', 
                    (SCIRun_Field, 'Field'))

  reg.add_module(SCIRun_InsertFieldsIntoBundle)
  reg.add_input_port(SCIRun_InsertFieldsIntoBundle, 'field1_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertFieldsIntoBundle, 'field2_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertFieldsIntoBundle, 'field3_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertFieldsIntoBundle, 'field4_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertFieldsIntoBundle, 'field5_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertFieldsIntoBundle, 'field6_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertFieldsIntoBundle, 'replace1',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_InsertFieldsIntoBundle, 'replace2',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_InsertFieldsIntoBundle, 'replace3',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_InsertFieldsIntoBundle, 'replace4',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_InsertFieldsIntoBundle, 'replace5',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_InsertFieldsIntoBundle, 'replace6',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_InsertFieldsIntoBundle, 'bundlename',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertFieldsIntoBundle, 'bundle',
                   (SCIRun_Bundle, "SCIRun_Bundle"))
  reg.add_input_port(SCIRun_InsertFieldsIntoBundle, 'field1',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_InsertFieldsIntoBundle, 'field2',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_InsertFieldsIntoBundle, 'field3',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_InsertFieldsIntoBundle, 'field4',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_InsertFieldsIntoBundle, 'field5',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_InsertFieldsIntoBundle, 'field6',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_InsertFieldsIntoBundle, 'bundle', 
                    (SCIRun_Bundle, 'bundle'))

  reg.add_module(SCIRun_CreateAndEditColorMap2D)
  reg.add_input_port(SCIRun_CreateAndEditColorMap2D, 'panx',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateAndEditColorMap2D, 'pany',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateAndEditColorMap2D, 'scale_factor',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateAndEditColorMap2D, 'histo',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateAndEditColorMap2D, 'selected_widget',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateAndEditColorMap2D, 'selected_object',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateAndEditColorMap2D, 'num_entries',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateAndEditColorMap2D, 'faux',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateAndEditColorMap2D, 'name_0',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_CreateAndEditColorMap2D, 'a0_color_r',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateAndEditColorMap2D, 'a0_color_g',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateAndEditColorMap2D, 'a0_color_b',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateAndEditColorMap2D, 'a0_color_a',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateAndEditColorMap2D, 'state_0',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_CreateAndEditColorMap2D, 'shadeType_0',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateAndEditColorMap2D, 'on_0',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateAndEditColorMap2D, 'name_1',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_CreateAndEditColorMap2D, 'a1_color_r',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateAndEditColorMap2D, 'a1_color_g',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateAndEditColorMap2D, 'a1_color_b',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateAndEditColorMap2D, 'a1_color_a',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateAndEditColorMap2D, 'state_1',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_CreateAndEditColorMap2D, 'shadeType_1',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateAndEditColorMap2D, 'on_1',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateAndEditColorMap2D, 'marker',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_CreateAndEditColorMap2D, 'Input Colormap',
                   (SCIRun_ColorMap2, "SCIRun_ColorMap2"))
  reg.add_input_port(SCIRun_CreateAndEditColorMap2D, 'Histogram',
                   (SCIRun_Nrrd, "SCIRun_Nrrd"))
  reg.add_input_port(SCIRun_CreateAndEditColorMap2D, 'Colormap',
                   (SCIRun_ColorMap, "SCIRun_ColorMap"))
  reg.add_output_port(SCIRun_CreateAndEditColorMap2D, 'Output Colormap', 
                    (SCIRun_ColorMap2, 'Output Colormap'))

  reg.add_module(SCIRun_ReportScalarFieldStats)
  reg.add_input_port(SCIRun_ReportScalarFieldStats, 'min',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ReportScalarFieldStats, 'max',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ReportScalarFieldStats, 'mean',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ReportScalarFieldStats, 'median',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ReportScalarFieldStats, 'sigma',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ReportScalarFieldStats, 'is_fixed',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReportScalarFieldStats, 'nbuckets',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReportScalarFieldStats, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))

  reg.add_module(SCIRun_ReportDataArrayInfo)
  reg.add_input_port(SCIRun_ReportDataArrayInfo, 'DataArray',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_ReportDataArrayInfo, 'NumElements', 
                    (SCIRun_Matrix, 'NumElements'))

  reg.add_module(SCIRun_GetFieldsFromBundle)
  reg.add_input_port(SCIRun_GetFieldsFromBundle, 'field1_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetFieldsFromBundle, 'field2_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetFieldsFromBundle, 'field3_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetFieldsFromBundle, 'field4_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetFieldsFromBundle, 'field5_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetFieldsFromBundle, 'field6_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetFieldsFromBundle, 'field_selection',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetFieldsFromBundle, 'bundle',
                   (SCIRun_Bundle, "SCIRun_Bundle"))
  reg.add_output_port(SCIRun_GetFieldsFromBundle, 'bundle', 
                    (SCIRun_Bundle, 'bundle'))
  reg.add_output_port(SCIRun_GetFieldsFromBundle, 'field1', 
                    (SCIRun_Field, 'field1'))
  reg.add_output_port(SCIRun_GetFieldsFromBundle, 'field2', 
                    (SCIRun_Field, 'field2'))
  reg.add_output_port(SCIRun_GetFieldsFromBundle, 'field3', 
                    (SCIRun_Field, 'field3'))
  reg.add_output_port(SCIRun_GetFieldsFromBundle, 'field4', 
                    (SCIRun_Field, 'field4'))
  reg.add_output_port(SCIRun_GetFieldsFromBundle, 'field5', 
                    (SCIRun_Field, 'field5'))
  reg.add_output_port(SCIRun_GetFieldsFromBundle, 'field6', 
                    (SCIRun_Field, 'field6'))

  reg.add_module(SCIRun_ConvertMaskVectorToMappingMatrix)
  reg.add_input_port(SCIRun_ConvertMaskVectorToMappingMatrix, 'MaskVector',
                   (SCIRun_Nrrd, "SCIRun_Nrrd"))
  reg.add_output_port(SCIRun_ConvertMaskVectorToMappingMatrix, 'MappingMatrix', 
                    (SCIRun_Matrix, 'MappingMatrix'))

  reg.add_module(SCIRun_CreateViewerAxes)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'precision',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'squash',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'valuerez',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'labelrez',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_01_0_Axis_absolute',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_01_0_Axis_divisions',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_01_0_Axis_offset',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_01_0_Axis_range_first',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_01_0_Axis_range_second',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_01_0_Axis_min_absolute',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_01_0_Axis_max_absolute',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_01_0_Axis_minplane',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_01_0_Axis_maxplane',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_01_0_Axis_lines',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_01_0_Axis_minticks',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_01_0_Axis_maxticks',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_01_0_Axis_minlabel',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_01_0_Axis_maxlabel',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_01_0_Axis_minvalue',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_01_0_Axis_maxvalue',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_01_0_Axis_width',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_01_0_Axis_tickangle',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_01_0_Axis_ticktilt',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_01_0_Axis_ticksize',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_01_0_Axis_labelangle',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_01_0_Axis_labelheight',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_01_0_Axis_valuesize',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_01_0_Axis_valuesquash',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_01_1_Axis_absolute',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_01_1_Axis_divisions',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_01_1_Axis_offset',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_01_1_Axis_range_first',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_01_1_Axis_range_second',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_01_1_Axis_min_absolute',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_01_1_Axis_max_absolute',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_01_1_Axis_minplane',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_01_1_Axis_maxplane',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_01_1_Axis_lines',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_01_1_Axis_minticks',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_01_1_Axis_maxticks',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_01_1_Axis_minlabel',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_01_1_Axis_maxlabel',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_01_1_Axis_minvalue',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_01_1_Axis_maxvalue',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_01_1_Axis_width',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_01_1_Axis_tickangle',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_01_1_Axis_ticktilt',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_01_1_Axis_ticksize',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_01_1_Axis_labelangle',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_01_1_Axis_labelheight',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_01_1_Axis_valuesize',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_01_1_Axis_valuesquash',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_02_0_Axis_absolute',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_02_0_Axis_divisions',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_02_0_Axis_offset',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_02_0_Axis_range_first',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_02_0_Axis_range_second',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_02_0_Axis_min_absolute',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_02_0_Axis_max_absolute',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_02_0_Axis_minplane',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_02_0_Axis_maxplane',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_02_0_Axis_lines',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_02_0_Axis_minticks',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_02_0_Axis_maxticks',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_02_0_Axis_minlabel',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_02_0_Axis_maxlabel',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_02_0_Axis_minvalue',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_02_0_Axis_maxvalue',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_02_0_Axis_width',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_02_0_Axis_tickangle',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_02_0_Axis_ticktilt',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_02_0_Axis_ticksize',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_02_0_Axis_labelangle',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_02_0_Axis_labelheight',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_02_0_Axis_valuesize',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_02_0_Axis_valuesquash',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_02_2_Axis_absolute',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_02_2_Axis_divisions',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_02_2_Axis_offset',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_02_2_Axis_range_first',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_02_2_Axis_range_second',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_02_2_Axis_min_absolute',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_02_2_Axis_max_absolute',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_02_2_Axis_minplane',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_02_2_Axis_maxplane',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_02_2_Axis_lines',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_02_2_Axis_minticks',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_02_2_Axis_maxticks',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_02_2_Axis_minlabel',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_02_2_Axis_maxlabel',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_02_2_Axis_minvalue',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_02_2_Axis_maxvalue',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_02_2_Axis_width',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_02_2_Axis_tickangle',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_02_2_Axis_ticktilt',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_02_2_Axis_ticksize',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_02_2_Axis_labelangle',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_02_2_Axis_labelheight',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_02_2_Axis_valuesize',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_02_2_Axis_valuesquash',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_12_1_Axis_absolute',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_12_1_Axis_divisions',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_12_1_Axis_offset',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_12_1_Axis_range_first',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_12_1_Axis_range_second',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_12_1_Axis_min_absolute',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_12_1_Axis_max_absolute',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_12_1_Axis_minplane',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_12_1_Axis_maxplane',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_12_1_Axis_lines',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_12_1_Axis_minticks',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_12_1_Axis_maxticks',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_12_1_Axis_minlabel',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_12_1_Axis_maxlabel',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_12_1_Axis_minvalue',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_12_1_Axis_maxvalue',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_12_1_Axis_width',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_12_1_Axis_tickangle',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_12_1_Axis_ticktilt',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_12_1_Axis_ticksize',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_12_1_Axis_labelangle',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_12_1_Axis_labelheight',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_12_1_Axis_valuesize',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_12_1_Axis_valuesquash',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_12_2_Axis_absolute',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_12_2_Axis_divisions',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_12_2_Axis_offset',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_12_2_Axis_range_first',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_12_2_Axis_range_second',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_12_2_Axis_min_absolute',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_12_2_Axis_max_absolute',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_12_2_Axis_minplane',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_12_2_Axis_maxplane',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_12_2_Axis_lines',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_12_2_Axis_minticks',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_12_2_Axis_maxticks',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_12_2_Axis_minlabel',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_12_2_Axis_maxlabel',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_12_2_Axis_minvalue',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_12_2_Axis_maxvalue',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_12_2_Axis_width',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_12_2_Axis_tickangle',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_12_2_Axis_ticktilt',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_12_2_Axis_ticksize',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_12_2_Axis_labelangle',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_12_2_Axis_labelheight',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_12_2_Axis_valuesize',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Plane_12_2_Axis_valuesquash',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerAxes, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_CreateViewerAxes, 'Axes', 
                    (SCIRun_Geometry, 'Axes'))

  reg.add_module(SCIRun_ShowField)
  reg.add_input_port(SCIRun_ShowField, 'nodes_on',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowField, 'nodes_transparency',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowField, 'nodes_color_type',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowField, 'nodes_display_type',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ShowField, 'edges_on',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowField, 'edges_transparency',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowField, 'edges_color_type',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowField, 'edges_display_type',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ShowField, 'faces_on',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowField, 'faces_transparency',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowField, 'faces_color_type',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowField, 'faces_normals',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowField, 'faces_usetexture',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowField, 'text_on',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowField, 'text_color_type',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowField, 'text_color_r',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowField, 'text_color_g',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowField, 'text_color_b',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowField, 'text_backface_cull',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowField, 'text_always_visible',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowField, 'text_fontsize',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowField, 'text_precision',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowField, 'text_render_locations',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowField, 'text_show_data',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowField, 'text_show_nodes',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowField, 'text_show_edges',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowField, 'text_show_faces',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowField, 'text_show_cells',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowField, 'def_color_r',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowField, 'def_color_g',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowField, 'def_color_b',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowField, 'def_color_a',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowField, 'nodes_scale',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowField, 'nodes_scaleNV',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowField, 'edges_scale',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowField, 'edges_scaleNV',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowField, 'active_tab',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ShowField, 'interactive_mode',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ShowField, 'show_progress',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowField, 'field_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ShowField, 'field_name_override',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowField, 'nodes_resolution',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowField, 'edges_resolution',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowField, 'approx_div',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowField, 'use_default_size',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowField, 'Mesh',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_ShowField, 'ColorMap',
                   (SCIRun_ColorMap, "SCIRun_ColorMap"))
  reg.add_output_port(SCIRun_ShowField, 'Scene Graph', 
                    (SCIRun_Geometry, 'Scene Graph'))

  reg.add_module(SCIRun_SetFieldData)
  reg.add_input_port(SCIRun_SetFieldData, 'keepscalartype',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_SetFieldData, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_SetFieldData, 'Matrix Data',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(SCIRun_SetFieldData, 'Nrrd Data',
                   (SCIRun_Nrrd, "SCIRun_Nrrd"))
  reg.add_output_port(SCIRun_SetFieldData, 'Field', 
                    (SCIRun_Field, 'Field'))

  reg.add_module(SCIRun_CreateVectorArray)
  reg.add_input_port(SCIRun_CreateVectorArray, 'X',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(SCIRun_CreateVectorArray, 'Y',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(SCIRun_CreateVectorArray, 'Z',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_CreateVectorArray, 'Vector', 
                    (SCIRun_Matrix, 'Vector'))

  reg.add_module(SCIRun_SynchronizeGeometry)
  reg.add_input_port(SCIRun_SynchronizeGeometry, 'enforce',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_SynchronizeGeometry, 'Input Geometry',
                   (SCIRun_Geometry, "SCIRun_Geometry"))
  reg.add_output_port(SCIRun_SynchronizeGeometry, 'Output Geometry', 
                    (SCIRun_Geometry, 'Output Geometry'))

  reg.add_module(SCIRun_ClipFieldWithSeed)
  reg.add_input_port(SCIRun_ClipFieldWithSeed, 'mode',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ClipFieldWithSeed, 'function',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ClipFieldWithSeed, 'Function',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_input_port(SCIRun_ClipFieldWithSeed, 'Input',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_ClipFieldWithSeed, 'Seeds',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_ClipFieldWithSeed, 'Clipped', 
                    (SCIRun_Field, 'Clipped'))
  reg.add_output_port(SCIRun_ClipFieldWithSeed, 'Mapping', 
                    (SCIRun_Matrix, 'Mapping'))
  reg.add_output_port(SCIRun_ClipFieldWithSeed, 'MaskVector', 
                    (SCIRun_Nrrd, 'MaskVector'))

  reg.add_module(SCIRun_SolveLinearSystem)
  reg.add_input_port(SCIRun_SolveLinearSystem, 'target_error',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_SolveLinearSystem, 'flops',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_SolveLinearSystem, 'floprate',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_SolveLinearSystem, 'memrefs',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_SolveLinearSystem, 'memrate',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_SolveLinearSystem, 'orig_error',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_SolveLinearSystem, 'current_error',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_SolveLinearSystem, 'method',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_SolveLinearSystem, 'precond',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_SolveLinearSystem, 'iteration',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_SolveLinearSystem, 'maxiter',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_SolveLinearSystem, 'use_previous_soln',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_SolveLinearSystem, 'emit_partial',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_SolveLinearSystem, 'emit_iter',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_SolveLinearSystem, 'status',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_SolveLinearSystem, 'np',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_SolveLinearSystem, 'Matrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(SCIRun_SolveLinearSystem, 'RHS',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_SolveLinearSystem, 'Solution', 
                    (SCIRun_Matrix, 'Solution'))

  reg.add_module(SCIRun_ShowFieldV1)
  reg.add_input_port(SCIRun_ShowFieldV1, 'nodes_on',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'nodes_transparency',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'nodes_as_disks',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'nodes_usedefcolor',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'edges_on',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'edges_transparency',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'edges_usedefcolor',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'faces_on',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'use_normals',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'use_transparency',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'faces_usedefcolor',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'faces_usetexture',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'scalars_on',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'scalars_transparency',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'normalize_scalars',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'scalars_usedefcolor',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'has_scalar_data',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'vectors_on',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'vectors_transparency',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'normalize_vectors',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'has_vector_data',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'bidirectional',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'vectors_usedefcolor',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'tensors_on',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'tensors_transparency',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'normalize_tensors',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'has_tensor_data',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'tensors_usedefcolor',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'tensors_emphasis',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'text_on',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'text_use_default_color',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'text_color_r',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'text_color_g',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'text_color_b',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'text_backface_cull',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'text_always_visible',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'text_fontsize',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'text_precision',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'text_render_locations',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'text_show_data',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'text_show_nodes',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'text_show_edges',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'text_show_faces',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'text_show_cells',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'def_color_r',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'def_color_g',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'def_color_b',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'def_color_a',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'node_display_type',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'edge_display_type',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'data_display_type',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'tensor_display_type',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'scalar_display_type',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'active_tab',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'node_scale',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'node_scaleNV',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'edge_scale',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'edge_scaleNV',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'vectors_scale',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'vectors_scaleNV',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'tensors_scale',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'tensors_scaleNV',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'scalars_scale',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'scalars_scaleNV',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'interactive_mode',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'field_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'field_name_override',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'field_name_update',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'node_resolution',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'edge_resolution',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'data_resolution',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'approx_div',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'use_default_size',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldV1, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_ShowFieldV1, 'ColorMap',
                   (SCIRun_ColorMap, "SCIRun_ColorMap"))
  reg.add_input_port(SCIRun_ShowFieldV1, 'Orientation Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_ShowFieldV1, 'Scene Graph', 
                    (SCIRun_Geometry, 'Scene Graph'))

  reg.add_module(SCIRun_ReadPath)
  reg.add_input_port(SCIRun_ReadPath, 'from_env',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ReadPath, 'Filename',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_output_port(SCIRun_ReadPath, 'Output Data', 
                    (SCIRun_Path, 'Output Data'))
  reg.add_output_port(SCIRun_ReadPath, 'Filename', 
                    (core.modules.basic_modules.String, 'Filename'))

  reg.add_module(SCIRun_InsertColorMap2sIntoBundle)
  reg.add_input_port(SCIRun_InsertColorMap2sIntoBundle, 'colormap21_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertColorMap2sIntoBundle, 'colormap22_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertColorMap2sIntoBundle, 'colormap23_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertColorMap2sIntoBundle, 'colormap24_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertColorMap2sIntoBundle, 'colormap25_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertColorMap2sIntoBundle, 'colormap26_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertColorMap2sIntoBundle, 'replace1',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_InsertColorMap2sIntoBundle, 'replace2',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_InsertColorMap2sIntoBundle, 'replace3',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_InsertColorMap2sIntoBundle, 'replace4',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_InsertColorMap2sIntoBundle, 'replace5',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_InsertColorMap2sIntoBundle, 'replace6',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_InsertColorMap2sIntoBundle, 'bundlename',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertColorMap2sIntoBundle, 'bundle',
                   (SCIRun_Bundle, "SCIRun_Bundle"))
  reg.add_input_port(SCIRun_InsertColorMap2sIntoBundle, 'colormap21',
                   (SCIRun_ColorMap2, "SCIRun_ColorMap2"))
  reg.add_input_port(SCIRun_InsertColorMap2sIntoBundle, 'colormap22',
                   (SCIRun_ColorMap2, "SCIRun_ColorMap2"))
  reg.add_input_port(SCIRun_InsertColorMap2sIntoBundle, 'colormap23',
                   (SCIRun_ColorMap2, "SCIRun_ColorMap2"))
  reg.add_input_port(SCIRun_InsertColorMap2sIntoBundle, 'colormap24',
                   (SCIRun_ColorMap2, "SCIRun_ColorMap2"))
  reg.add_input_port(SCIRun_InsertColorMap2sIntoBundle, 'colormap25',
                   (SCIRun_ColorMap2, "SCIRun_ColorMap2"))
  reg.add_input_port(SCIRun_InsertColorMap2sIntoBundle, 'colormap26',
                   (SCIRun_ColorMap2, "SCIRun_ColorMap2"))
  reg.add_output_port(SCIRun_InsertColorMap2sIntoBundle, 'bundle', 
                    (SCIRun_Bundle, 'bundle'))

  reg.add_module(SCIRun_ConvertMatrixToString)
  reg.add_input_port(SCIRun_ConvertMatrixToString, 'Matrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_ConvertMatrixToString, 'String', 
                    (core.modules.basic_modules.String, 'String'))

  reg.add_module(SCIRun_ExtractIsosurface)
  reg.add_input_port(SCIRun_ExtractIsosurface, 'isoval_min',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ExtractIsosurface, 'isoval_max',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ExtractIsosurface, 'isoval',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ExtractIsosurface, 'isoval_typed',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ExtractIsosurface, 'isoval_quantity',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ExtractIsosurface, 'quantity_range',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ExtractIsosurface, 'quantity_clusive',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ExtractIsosurface, 'quantity_min',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ExtractIsosurface, 'quantity_max',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ExtractIsosurface, 'quantity_list',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ExtractIsosurface, 'isoval_list',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ExtractIsosurface, 'matrix_list',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ExtractIsosurface, 'extract_from_new_field',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ExtractIsosurface, 'algorithm',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ExtractIsosurface, 'build_trisurf',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ExtractIsosurface, 'build_geom',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ExtractIsosurface, 'np',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ExtractIsosurface, 'active_isoval_selection_tab',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ExtractIsosurface, 'active_tab',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ExtractIsosurface, 'update_type',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ExtractIsosurface, 'color_r',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ExtractIsosurface, 'color_g',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ExtractIsosurface, 'color_b',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ExtractIsosurface, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_ExtractIsosurface, 'Optional Color Map',
                   (SCIRun_ColorMap, "SCIRun_ColorMap"))
  reg.add_input_port(SCIRun_ExtractIsosurface, 'Optional Isovalues',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_ExtractIsosurface, 'Surface', 
                    (SCIRun_Field, 'Surface'))
  reg.add_output_port(SCIRun_ExtractIsosurface, 'Geometry', 
                    (SCIRun_Geometry, 'Geometry'))
  reg.add_output_port(SCIRun_ExtractIsosurface, 'Mapping', 
                    (SCIRun_Matrix, 'Mapping'))

  reg.add_module(SCIRun_ConvertMeshToUnstructuredMesh)
  reg.add_input_port(SCIRun_ConvertMeshToUnstructuredMesh, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_ConvertMeshToUnstructuredMesh, 'Output Field', 
                    (SCIRun_Field, 'Output Field'))

  reg.add_module(SCIRun_ReportMatrixColumnMeasure)
  reg.add_input_port(SCIRun_ReportMatrixColumnMeasure, 'method',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ReportMatrixColumnMeasure, 'Matrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_ReportMatrixColumnMeasure, 'Vector', 
                    (SCIRun_Matrix, 'Vector'))

  reg.add_module(SCIRun_ReplicateDataArray)
  reg.add_input_port(SCIRun_ReplicateDataArray, 'size',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReplicateDataArray, 'DataArray',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(SCIRun_ReplicateDataArray, 'Size',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_ReplicateDataArray, 'DataArray', 
                    (SCIRun_Matrix, 'DataArray'))

  reg.add_module(SCIRun_SwapFieldDataWithMatrixEntries)
  reg.add_input_port(SCIRun_SwapFieldDataWithMatrixEntries, 'preserve_scalar_type',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_SwapFieldDataWithMatrixEntries, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_SwapFieldDataWithMatrixEntries, 'Input Matrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_SwapFieldDataWithMatrixEntries, 'Output Field', 
                    (SCIRun_Field, 'Output Field'))
  reg.add_output_port(SCIRun_SwapFieldDataWithMatrixEntries, 'Output Matrix', 
                    (SCIRun_Matrix, 'Output Matrix'))

  reg.add_module(SCIRun_SelectFieldROIWithBoxWidget)
  reg.add_input_port(SCIRun_SelectFieldROIWithBoxWidget, 'stampvalue',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_SelectFieldROIWithBoxWidget, 'runmode',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_SelectFieldROIWithBoxWidget, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_SelectFieldROIWithBoxWidget, 'Selection Widget', 
                    (SCIRun_Geometry, 'Selection Widget'))
  reg.add_output_port(SCIRun_SelectFieldROIWithBoxWidget, 'Output Field', 
                    (SCIRun_Field, 'Output Field'))

  reg.add_module(SCIRun_SetTetVolFieldDataValues)
  reg.add_input_port(SCIRun_SetTetVolFieldDataValues, 'newval',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_SetTetVolFieldDataValues, 'InField',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_SetTetVolFieldDataValues, 'OutField', 
                    (SCIRun_Field, 'OutField'))

  reg.add_module(SCIRun_WritePath)
  reg.add_input_port(SCIRun_WritePath, 'filetype',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_WritePath, 'confirm',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_WritePath, 'confirm_once',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_WritePath, 'Input Data',
                   (SCIRun_Path, "SCIRun_Path"))
  reg.add_input_port(SCIRun_WritePath, 'Filename',
                   (core.modules.basic_modules.String, 'tip'))

  reg.add_module(SCIRun_ClipLatVolByIndicesOrWidget)
  reg.add_input_port(SCIRun_ClipLatVolByIndicesOrWidget, 'use_text_bbox',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ClipLatVolByIndicesOrWidget, 'text_min_x',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ClipLatVolByIndicesOrWidget, 'text_min_y',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ClipLatVolByIndicesOrWidget, 'text_min_z',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ClipLatVolByIndicesOrWidget, 'text_max_x',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ClipLatVolByIndicesOrWidget, 'text_max_y',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ClipLatVolByIndicesOrWidget, 'text_max_z',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ClipLatVolByIndicesOrWidget, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_ClipLatVolByIndicesOrWidget, 'Selection Widget', 
                    (SCIRun_Geometry, 'Selection Widget'))
  reg.add_output_port(SCIRun_ClipLatVolByIndicesOrWidget, 'Output Field', 
                    (SCIRun_Field, 'Output Field'))
  reg.add_output_port(SCIRun_ClipLatVolByIndicesOrWidget, 'MaskVector', 
                    (SCIRun_Nrrd, 'MaskVector'))

  reg.add_module(SCIRun_GetBundlesFromBundle)
  reg.add_input_port(SCIRun_GetBundlesFromBundle, 'bundle1_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetBundlesFromBundle, 'bundle2_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetBundlesFromBundle, 'bundle3_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetBundlesFromBundle, 'bundle4_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetBundlesFromBundle, 'bundle5_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetBundlesFromBundle, 'bundle6_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetBundlesFromBundle, 'bundle_selection',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetBundlesFromBundle, 'bundle',
                   (SCIRun_Bundle, "SCIRun_Bundle"))
  reg.add_output_port(SCIRun_GetBundlesFromBundle, 'bundle', 
                    (SCIRun_Bundle, 'bundle'))
  reg.add_output_port(SCIRun_GetBundlesFromBundle, 'bundle1', 
                    (SCIRun_Bundle, 'bundle1'))
  reg.add_output_port(SCIRun_GetBundlesFromBundle, 'bundle2', 
                    (SCIRun_Bundle, 'bundle2'))
  reg.add_output_port(SCIRun_GetBundlesFromBundle, 'bundle3', 
                    (SCIRun_Bundle, 'bundle3'))
  reg.add_output_port(SCIRun_GetBundlesFromBundle, 'bundle4', 
                    (SCIRun_Bundle, 'bundle4'))
  reg.add_output_port(SCIRun_GetBundlesFromBundle, 'bundle5', 
                    (SCIRun_Bundle, 'bundle5'))
  reg.add_output_port(SCIRun_GetBundlesFromBundle, 'bundle6', 
                    (SCIRun_Bundle, 'bundle6'))

  reg.add_module(SCIRun_RescaleColorMap)
  reg.add_input_port(SCIRun_RescaleColorMap, 'main_frame',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_RescaleColorMap, 'isFixed',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_RescaleColorMap, 'min',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_RescaleColorMap, 'max',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_RescaleColorMap, 'makeSymmetric',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_RescaleColorMap, 'ColorMap',
                   (SCIRun_ColorMap, "SCIRun_ColorMap"))
  reg.add_input_port(SCIRun_RescaleColorMap, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_RescaleColorMap, 'ColorMap', 
                    (SCIRun_ColorMap, 'ColorMap'))

  reg.add_module(SCIRun_ConvertNrrdsToTexture)
  reg.add_input_port(SCIRun_ConvertNrrdsToTexture, 'vmin',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ConvertNrrdsToTexture, 'vmax',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ConvertNrrdsToTexture, 'gmin',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ConvertNrrdsToTexture, 'gmax',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ConvertNrrdsToTexture, 'mmin',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ConvertNrrdsToTexture, 'mmax',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ConvertNrrdsToTexture, 'is_fixed',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ConvertNrrdsToTexture, 'card_mem',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ConvertNrrdsToTexture, 'card_mem_auto',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ConvertNrrdsToTexture, 'is_uchar',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ConvertNrrdsToTexture, 'histogram',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ConvertNrrdsToTexture, 'gamma',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ConvertNrrdsToTexture, 'Value Nrrd',
                   (SCIRun_Nrrd, "SCIRun_Nrrd"))
  reg.add_input_port(SCIRun_ConvertNrrdsToTexture, 'Gradient Magnitude Nrrd',
                   (SCIRun_Nrrd, "SCIRun_Nrrd"))
  reg.add_output_port(SCIRun_ConvertNrrdsToTexture, 'Texture', 
                    (SCIRun_Texture, 'Texture'))
  reg.add_output_port(SCIRun_ConvertNrrdsToTexture, 'JointHistoGram', 
                    (SCIRun_Nrrd, 'JointHistoGram'))

  reg.add_module(SCIRun_ConvertQuadSurfToTriSurf)
  reg.add_input_port(SCIRun_ConvertQuadSurfToTriSurf, 'QuadSurf',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_ConvertQuadSurfToTriSurf, 'TriSurf', 
                    (SCIRun_Field, 'TriSurf'))

  reg.add_module(SCIRun_WriteColorMap2D)
  reg.add_input_port(SCIRun_WriteColorMap2D, 'filetype',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_WriteColorMap2D, 'confirm',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_WriteColorMap2D, 'confirm_once',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_WriteColorMap2D, 'exporttype',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_WriteColorMap2D, 'Input Data',
                   (SCIRun_ColorMap2, "SCIRun_ColorMap2"))
  reg.add_input_port(SCIRun_WriteColorMap2D, 'Filename',
                   (core.modules.basic_modules.String, 'tip'))

  reg.add_module(SCIRun_BuildMatrixOfSurfaceNormals)
  reg.add_input_port(SCIRun_BuildMatrixOfSurfaceNormals, 'Surface Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_BuildMatrixOfSurfaceNormals, 'Nodal Surface Normals', 
                    (SCIRun_Matrix, 'Nodal Surface Normals'))

  reg.add_module(SCIRun_ReadHDF5File)
  reg.add_input_port(SCIRun_ReadHDF5File, 'have_HDF5',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'power_app',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'datasets',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'dumpname',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'ports',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'ndims',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'mergeData',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'assumeSVT',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'animate',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'animate_tab',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'basic_tab',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'extended_tab',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'playmode_tab',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'selectable_min',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'selectable_max',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'selectable_inc',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'range_min',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'range_max',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'playmode',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'current',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'execmode',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'delay',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'inc_amount',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'update_type',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'have_group',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'have_attributes',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'have_datasets',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'continuous',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'selectionString',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'regexp',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'allow_selection',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'read_error',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'max_dims',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'a0_dim',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'a0_start',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'a0_start2',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'a0_count',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'a0_count2',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'a0_stride',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'a0_stride2',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'a1_dim',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'a1_start',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'a1_start2',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'a1_count',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'a1_count2',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'a1_stride',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'a1_stride2',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'a2_dim',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'a2_start',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'a2_start2',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'a2_count',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'a2_count2',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'a2_stride',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'a2_stride2',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'a3_dim',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'a3_start',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'a3_start2',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'a3_count',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'a3_count2',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'a3_stride',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'a3_stride2',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'a4_dim',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'a4_start',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'a4_start2',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'a4_count',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'a4_count2',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'a4_stride',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'a4_stride2',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'a5_dim',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'a5_start',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'a5_start2',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'a5_count',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'a5_count2',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'a5_stride',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'a5_stride2',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReadHDF5File, 'Full filename',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_input_port(SCIRun_ReadHDF5File, 'Current Index',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_ReadHDF5File, 'Output 0 Nrrd', 
                    (SCIRun_Nrrd, 'Output 0 Nrrd'))
  reg.add_output_port(SCIRun_ReadHDF5File, 'Output 1 Nrrd', 
                    (SCIRun_Nrrd, 'Output 1 Nrrd'))
  reg.add_output_port(SCIRun_ReadHDF5File, 'Output 2 Nrrd', 
                    (SCIRun_Nrrd, 'Output 2 Nrrd'))
  reg.add_output_port(SCIRun_ReadHDF5File, 'Output 3 Nrrd', 
                    (SCIRun_Nrrd, 'Output 3 Nrrd'))
  reg.add_output_port(SCIRun_ReadHDF5File, 'Output 4 Nrrd', 
                    (SCIRun_Nrrd, 'Output 4 Nrrd'))
  reg.add_output_port(SCIRun_ReadHDF5File, 'Output 5 Nrrd', 
                    (SCIRun_Nrrd, 'Output 5 Nrrd'))
  reg.add_output_port(SCIRun_ReadHDF5File, 'Output 6 Nrrd', 
                    (SCIRun_Nrrd, 'Output 6 Nrrd'))
  reg.add_output_port(SCIRun_ReadHDF5File, 'Output 7 Nrrd', 
                    (SCIRun_Nrrd, 'Output 7 Nrrd'))
  reg.add_output_port(SCIRun_ReadHDF5File, 'Selected Index', 
                    (SCIRun_Matrix, 'Selected Index'))

  reg.add_module(SCIRun_GetPathsFromBundle)
  reg.add_input_port(SCIRun_GetPathsFromBundle, 'path1_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetPathsFromBundle, 'path2_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetPathsFromBundle, 'path3_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetPathsFromBundle, 'path4_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetPathsFromBundle, 'path5_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetPathsFromBundle, 'path6_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetPathsFromBundle, 'path_selection',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetPathsFromBundle, 'bundle',
                   (SCIRun_Bundle, "SCIRun_Bundle"))
  reg.add_output_port(SCIRun_GetPathsFromBundle, 'bundle', 
                    (SCIRun_Bundle, 'bundle'))
  reg.add_output_port(SCIRun_GetPathsFromBundle, 'path1', 
                    (SCIRun_Path, 'path1'))
  reg.add_output_port(SCIRun_GetPathsFromBundle, 'path2', 
                    (SCIRun_Path, 'path2'))
  reg.add_output_port(SCIRun_GetPathsFromBundle, 'path3', 
                    (SCIRun_Path, 'path3'))
  reg.add_output_port(SCIRun_GetPathsFromBundle, 'path4', 
                    (SCIRun_Path, 'path4'))
  reg.add_output_port(SCIRun_GetPathsFromBundle, 'path5', 
                    (SCIRun_Path, 'path5'))
  reg.add_output_port(SCIRun_GetPathsFromBundle, 'path6', 
                    (SCIRun_Path, 'path6'))

  reg.add_module(SCIRun_GetFieldBoundary)
  reg.add_input_port(SCIRun_GetFieldBoundary, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_GetFieldBoundary, 'BoundaryField', 
                    (SCIRun_Field, 'BoundaryField'))
  reg.add_output_port(SCIRun_GetFieldBoundary, 'Mapping', 
                    (SCIRun_Matrix, 'Mapping'))

  reg.add_module(SCIRun_TransformMeshWithFunction)
  reg.add_input_port(SCIRun_TransformMeshWithFunction, 'function',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_TransformMeshWithFunction, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_TransformMeshWithFunction, 'Output Field', 
                    (SCIRun_Field, 'Output Field'))

  reg.add_module(SCIRun_ConvertMatricesToMesh)
  reg.add_input_port(SCIRun_ConvertMatricesToMesh, 'fieldname',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ConvertMatricesToMesh, 'meshname',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ConvertMatricesToMesh, 'fieldbasetype',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ConvertMatricesToMesh, 'datatype',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ConvertMatricesToMesh, 'Mesh Elements',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(SCIRun_ConvertMatricesToMesh, 'Mesh Positions',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(SCIRun_ConvertMatricesToMesh, 'Mesh Normals',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_ConvertMatricesToMesh, 'Output Field', 
                    (SCIRun_Field, 'Output Field'))

  reg.add_module(SCIRun_ReportFieldInfo)
  reg.add_input_port(SCIRun_ReportFieldInfo, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_ReportFieldInfo, 'NumNodes', 
                    (SCIRun_Matrix, 'NumNodes'))
  reg.add_output_port(SCIRun_ReportFieldInfo, 'NumElements', 
                    (SCIRun_Matrix, 'NumElements'))
  reg.add_output_port(SCIRun_ReportFieldInfo, 'NumData', 
                    (SCIRun_Matrix, 'NumData'))
  reg.add_output_port(SCIRun_ReportFieldInfo, 'DataMin', 
                    (SCIRun_Matrix, 'DataMin'))
  reg.add_output_port(SCIRun_ReportFieldInfo, 'DataMax', 
                    (SCIRun_Matrix, 'DataMax'))
  reg.add_output_port(SCIRun_ReportFieldInfo, 'FieldSize', 
                    (SCIRun_Matrix, 'FieldSize'))
  reg.add_output_port(SCIRun_ReportFieldInfo, 'FieldCenter', 
                    (SCIRun_Matrix, 'FieldCenter'))
  reg.add_output_port(SCIRun_ReportFieldInfo, 'Dimensions', 
                    (SCIRun_Matrix, 'Dimensions'))

  reg.add_module(SCIRun_ConvertFieldsToTexture)
  reg.add_input_port(SCIRun_ConvertFieldsToTexture, 'vmin',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ConvertFieldsToTexture, 'vmax',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ConvertFieldsToTexture, 'gmin',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ConvertFieldsToTexture, 'gmax',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ConvertFieldsToTexture, 'is_fixed',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ConvertFieldsToTexture, 'card_mem',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ConvertFieldsToTexture, 'card_mem_auto',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ConvertFieldsToTexture, 'histogram',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ConvertFieldsToTexture, 'gamma',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ConvertFieldsToTexture, 'Value Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_ConvertFieldsToTexture, 'Gradient Magnitude Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_ConvertFieldsToTexture, 'Texture', 
                    (SCIRun_Texture, 'Texture'))
  reg.add_output_port(SCIRun_ConvertFieldsToTexture, 'JointHistoGram', 
                    (SCIRun_Nrrd, 'JointHistoGram'))

  reg.add_module(SCIRun_PrintHelloWorldToScreen)

  reg.add_module(SCIRun_MapFieldDataFromSourceToDestination)
  reg.add_input_port(SCIRun_MapFieldDataFromSourceToDestination, 'interpolation_basis',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_MapFieldDataFromSourceToDestination, 'map_source_to_single_dest',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_MapFieldDataFromSourceToDestination, 'exhaustive_search',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_MapFieldDataFromSourceToDestination, 'exhaustive_search_max_dist',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_MapFieldDataFromSourceToDestination, 'np',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_MapFieldDataFromSourceToDestination, 'Source',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_MapFieldDataFromSourceToDestination, 'Destination',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_MapFieldDataFromSourceToDestination, 'Remapped Destination', 
                    (SCIRun_Field, 'Remapped Destination'))

  reg.add_module(SCIRun_ConvertLatVolDataFromElemToNode)
  reg.add_input_port(SCIRun_ConvertLatVolDataFromElemToNode, 'Elem Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_ConvertLatVolDataFromElemToNode, 'Node Field', 
                    (SCIRun_Field, 'Node Field'))

  reg.add_module(SCIRun_CreateGeometricTransform)
  reg.add_input_port(SCIRun_CreateGeometricTransform, 'rotate_x',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateGeometricTransform, 'rotate_y',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateGeometricTransform, 'rotate_z',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateGeometricTransform, 'rotate_theta',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateGeometricTransform, 'translate_x',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateGeometricTransform, 'translate_y',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateGeometricTransform, 'translate_z',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateGeometricTransform, 'scale_uniform',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateGeometricTransform, 'scale_x',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateGeometricTransform, 'scale_y',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateGeometricTransform, 'scale_z',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateGeometricTransform, 'shear_plane_a',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateGeometricTransform, 'shear_plane_b',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateGeometricTransform, 'shear_plane_c',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateGeometricTransform, 'widget_resizable',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateGeometricTransform, 'permute_x',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateGeometricTransform, 'permute_y',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateGeometricTransform, 'permute_z',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateGeometricTransform, 'pre_transform',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateGeometricTransform, 'which_transform',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_CreateGeometricTransform, 'widget_scale',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateGeometricTransform, 'ignoring_widget_changes',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateGeometricTransform, 'Matrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_CreateGeometricTransform, 'Matrix', 
                    (SCIRun_Matrix, 'Matrix'))
  reg.add_output_port(SCIRun_CreateGeometricTransform, 'Geometry', 
                    (SCIRun_Geometry, 'Geometry'))

  reg.add_module(SCIRun_CalculateNodeNormals)
  reg.add_input_port(SCIRun_CalculateNodeNormals, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_CalculateNodeNormals, 'Input Point',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_CalculateNodeNormals, 'Output Field', 
                    (SCIRun_Field, 'Output Field'))

  reg.add_module(SCIRun_ReportFieldGeometryMeasures)
  reg.add_input_port(SCIRun_ReportFieldGeometryMeasures, 'simplexString',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ReportFieldGeometryMeasures, 'xFlag',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReportFieldGeometryMeasures, 'yFlag',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReportFieldGeometryMeasures, 'zFlag',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReportFieldGeometryMeasures, 'idxFlag',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReportFieldGeometryMeasures, 'sizeFlag',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReportFieldGeometryMeasures, 'normalsFlag',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ReportFieldGeometryMeasures, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_ReportFieldGeometryMeasures, 'Output Measures Matrix', 
                    (SCIRun_Matrix, 'Output Measures Matrix'))

  reg.add_module(SCIRun_CalculateVectorMagnitudes)
  reg.add_input_port(SCIRun_CalculateVectorMagnitudes, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_CalculateVectorMagnitudes, 'Output CalculateVectorMagnitudes', 
                    (SCIRun_Field, 'Output CalculateVectorMagnitudes'))

  reg.add_module(SCIRun_GetInputField)
  reg.add_input_port(SCIRun_GetInputField, 'InField',
                   (SCIRun_Field, "SCIRun_Field"))

  reg.add_module(SCIRun_ChooseMatrix)
  reg.add_input_port(SCIRun_ChooseMatrix, 'use_first_valid',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ChooseMatrix, 'port_valid_index',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ChooseMatrix, 'port_selected_index',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ChooseMatrix, 'Matrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_ChooseMatrix, 'Matrix', 
                    (SCIRun_Matrix, 'Matrix'))

  reg.add_module(SCIRun_ClipFieldToFieldOrWidget)
  reg.add_input_port(SCIRun_ClipFieldToFieldOrWidget, 'clip_location',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ClipFieldToFieldOrWidget, 'clipmode',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ClipFieldToFieldOrWidget, 'autoexecute',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ClipFieldToFieldOrWidget, 'autoinvert',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ClipFieldToFieldOrWidget, 'execmode',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ClipFieldToFieldOrWidget, 'center_x',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ClipFieldToFieldOrWidget, 'center_y',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ClipFieldToFieldOrWidget, 'center_z',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ClipFieldToFieldOrWidget, 'right_x',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ClipFieldToFieldOrWidget, 'right_y',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ClipFieldToFieldOrWidget, 'right_z',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ClipFieldToFieldOrWidget, 'down_x',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ClipFieldToFieldOrWidget, 'down_y',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ClipFieldToFieldOrWidget, 'down_z',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ClipFieldToFieldOrWidget, 'in_x',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ClipFieldToFieldOrWidget, 'in_y',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ClipFieldToFieldOrWidget, 'in_z',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ClipFieldToFieldOrWidget, 'scale',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ClipFieldToFieldOrWidget, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_ClipFieldToFieldOrWidget, 'Clip Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_ClipFieldToFieldOrWidget, 'Selection Widget', 
                    (SCIRun_Geometry, 'Selection Widget'))
  reg.add_output_port(SCIRun_ClipFieldToFieldOrWidget, 'Output Field', 
                    (SCIRun_Field, 'Output Field'))

  reg.add_module(SCIRun_ConvertHexVolToTetVol)
  reg.add_input_port(SCIRun_ConvertHexVolToTetVol, 'HexVol',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_ConvertHexVolToTetVol, 'TetVol', 
                    (SCIRun_Field, 'TetVol'))

  reg.add_module(SCIRun_SetFieldOrMeshStringProperty)
  reg.add_input_port(SCIRun_SetFieldOrMeshStringProperty, 'prop',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_SetFieldOrMeshStringProperty, 'val',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_SetFieldOrMeshStringProperty, 'meshprop',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_SetFieldOrMeshStringProperty, 'Input',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_SetFieldOrMeshStringProperty, 'Output', 
                    (SCIRun_Field, 'Output'))

  reg.add_module(SCIRun_ConvertMeshCoordinateSystem)
  reg.add_input_port(SCIRun_ConvertMeshCoordinateSystem, 'oldsystem',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ConvertMeshCoordinateSystem, 'newsystem',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ConvertMeshCoordinateSystem, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_ConvertMeshCoordinateSystem, 'Output Field', 
                    (SCIRun_Field, 'Output Field'))

  reg.add_module(SCIRun_RefineMeshByIsovalue2)
  reg.add_input_port(SCIRun_RefineMeshByIsovalue2, 'isoval',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_RefineMeshByIsovalue2, 'lte',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_RefineMeshByIsovalue2, 'Input',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_RefineMeshByIsovalue2, 'Optional Isovalue',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_RefineMeshByIsovalue2, 'Refined', 
                    (SCIRun_Field, 'Refined'))
  reg.add_output_port(SCIRun_RefineMeshByIsovalue2, 'Mapping', 
                    (SCIRun_Matrix, 'Mapping'))

  reg.add_module(SCIRun_SetTetVolFieldDataValuesToZero)
  reg.add_input_port(SCIRun_SetTetVolFieldDataValuesToZero, 'InField',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_SetTetVolFieldDataValuesToZero, 'OutField', 
                    (SCIRun_Field, 'OutField'))

  reg.add_module(SCIRun_ViewSlices)
  reg.add_input_port(SCIRun_ViewSlices, 'clut_ww',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ViewSlices, 'clut_wl',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ViewSlices, 'probe',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ViewSlices, 'show_colormap2',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ViewSlices, 'painting',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ViewSlices, 'crop',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ViewSlices, 'crop_minAxis0',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ViewSlices, 'crop_minAxis1',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ViewSlices, 'crop_minAxis2',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ViewSlices, 'crop_maxAxis0',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ViewSlices, 'crop_maxAxis1',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ViewSlices, 'crop_maxAxis2',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ViewSlices, 'crop_minPadAxis0',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ViewSlices, 'crop_minPadAxis1',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ViewSlices, 'crop_minPadAxis2',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ViewSlices, 'crop_maxPadAxis0',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ViewSlices, 'crop_maxPadAxis1',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ViewSlices, 'crop_maxPadAxis2',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ViewSlices, 'texture_filter',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ViewSlices, 'anatomical_coordinates',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ViewSlices, 'show_text',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ViewSlices, 'color_font_r',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ViewSlices, 'color_font_g',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ViewSlices, 'color_font_b',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ViewSlices, 'color_font_a',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ViewSlices, 'min',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ViewSlices, 'max',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ViewSlices, 'dim0',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ViewSlices, 'dim1',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ViewSlices, 'dim2',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ViewSlices, 'geom_flushed',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ViewSlices, 'background_threshold',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ViewSlices, 'gradient_threshold',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ViewSlices, 'font_size',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ViewSlices, 'Nrrd1',
                   (SCIRun_Nrrd, "SCIRun_Nrrd"))
  reg.add_input_port(SCIRun_ViewSlices, 'Nrrd2',
                   (SCIRun_Nrrd, "SCIRun_Nrrd"))
  reg.add_input_port(SCIRun_ViewSlices, 'Nrrd1ColorMap',
                   (SCIRun_ColorMap, "SCIRun_ColorMap"))
  reg.add_input_port(SCIRun_ViewSlices, 'Nrrd2ColorMap',
                   (SCIRun_ColorMap, "SCIRun_ColorMap"))
  reg.add_input_port(SCIRun_ViewSlices, 'InputColorMap2',
                   (SCIRun_ColorMap2, "SCIRun_ColorMap2"))
  reg.add_input_port(SCIRun_ViewSlices, 'NrrdGradient',
                   (SCIRun_Nrrd, "SCIRun_Nrrd"))
  reg.add_output_port(SCIRun_ViewSlices, 'Geometry', 
                    (SCIRun_Geometry, 'Geometry'))
  reg.add_output_port(SCIRun_ViewSlices, 'ColorMap2', 
                    (SCIRun_ColorMap2, 'ColorMap2'))

  reg.add_module(SCIRun_SplitVectorArrayInXYZ)
  reg.add_input_port(SCIRun_SplitVectorArrayInXYZ, 'VectorArray',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_SplitVectorArrayInXYZ, 'X', 
                    (SCIRun_Matrix, 'X'))
  reg.add_output_port(SCIRun_SplitVectorArrayInXYZ, 'Y', 
                    (SCIRun_Matrix, 'Y'))
  reg.add_output_port(SCIRun_SplitVectorArrayInXYZ, 'Z', 
                    (SCIRun_Matrix, 'Z'))

  reg.add_module(SCIRun_ConvertIndicesToFieldData)
  reg.add_input_port(SCIRun_ConvertIndicesToFieldData, 'outputtype',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ConvertIndicesToFieldData, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_ConvertIndicesToFieldData, 'Data',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_ConvertIndicesToFieldData, 'Field', 
                    (SCIRun_Field, 'Field'))

  reg.add_module(SCIRun_CreateAndEditCameraPath)
  reg.add_input_port(SCIRun_CreateAndEditCameraPath, 'Path',
                   (SCIRun_Path, "SCIRun_Path"))
  reg.add_output_port(SCIRun_CreateAndEditCameraPath, 'Path', 
                    (SCIRun_Path, 'Path'))
  reg.add_output_port(SCIRun_CreateAndEditCameraPath, 'Geometry', 
                    (SCIRun_Geometry, 'Geometry'))
  reg.add_output_port(SCIRun_CreateAndEditCameraPath, 'Camera View', 
                    (SCIRun_Path, 'Camera View'))

  reg.add_module(SCIRun_CalculateDistanceToFieldBoundary)
  reg.add_input_port(SCIRun_CalculateDistanceToFieldBoundary, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_CalculateDistanceToFieldBoundary, 'DistanceField', 
                    (SCIRun_Field, 'DistanceField'))

  reg.add_module(SCIRun_ConvertMappingMatrixToMaskVector)
  reg.add_input_port(SCIRun_ConvertMappingMatrixToMaskVector, 'MappingMatrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_ConvertMappingMatrixToMaskVector, 'MaskVector', 
                    (SCIRun_Nrrd, 'MaskVector'))

  reg.add_module(SCIRun_CreateFieldData)
  reg.add_input_port(SCIRun_CreateFieldData, 'function',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_CreateFieldData, 'format',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_CreateFieldData, 'basis',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_CreateFieldData, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_CreateFieldData, 'Function',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_input_port(SCIRun_CreateFieldData, 'DataArray',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_CreateFieldData, 'Field', 
                    (SCIRun_Field, 'Field'))

  reg.add_module(SCIRun_CreateLatVol)
  reg.add_input_port(SCIRun_CreateLatVol, 'sizex',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateLatVol, 'sizey',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateLatVol, 'sizez',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateLatVol, 'padpercent',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateLatVol, 'data_at',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_CreateLatVol, 'element_size',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_CreateLatVol, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_CreateLatVol, 'LatVol Size',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_CreateLatVol, 'Output Sample Field', 
                    (SCIRun_Field, 'Output Sample Field'))

  reg.add_module(SCIRun_ResizeMatrix)
  reg.add_input_port(SCIRun_ResizeMatrix, 'dim_m',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ResizeMatrix, 'dim_n',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ResizeMatrix, 'Matrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(SCIRun_ResizeMatrix, 'M',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(SCIRun_ResizeMatrix, 'N',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_ResizeMatrix, 'Matrix', 
                    (SCIRun_Matrix, 'Matrix'))

  reg.add_module(SCIRun_GetInputFieldAndSendAsOutput)
  reg.add_input_port(SCIRun_GetInputFieldAndSendAsOutput, 'InField',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_GetInputFieldAndSendAsOutput, 'OutField', 
                    (SCIRun_Field, 'OutField'))

  reg.add_module(SCIRun_ShowAndEditCameraWidget)
  reg.add_input_port(SCIRun_ShowAndEditCameraWidget, 'frame',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowAndEditCameraWidget, 'num_frames',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowAndEditCameraWidget, 'time',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowAndEditCameraWidget, 'playmode',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ShowAndEditCameraWidget, 'execmode',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ShowAndEditCameraWidget, 'track',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowAndEditCameraWidget, 'B',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowAndEditCameraWidget, 'C',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_output_port(SCIRun_ShowAndEditCameraWidget, 'Geometry', 
                    (SCIRun_Geometry, 'Geometry'))

  reg.add_module(SCIRun_InterfaceWithCamal)
  reg.add_input_port(SCIRun_InterfaceWithCamal, 'TriSurf',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_InterfaceWithCamal, 'TetVol', 
                    (SCIRun_Field, 'TetVol'))

  reg.add_module(SCIRun_CreateParameterBundle)
  reg.add_input_port(SCIRun_CreateParameterBundle, 'data',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_CreateParameterBundle, 'new_field_count',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateParameterBundle, 'update_all',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_output_port(SCIRun_CreateParameterBundle, 'ParameterList', 
                    (SCIRun_Bundle, 'ParameterList'))

  reg.add_module(SCIRun_SelectAndSetFieldData3)
  reg.add_input_port(SCIRun_SelectAndSetFieldData3, 'selection1',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_SelectAndSetFieldData3, 'function1',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_SelectAndSetFieldData3, 'selection2',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_SelectAndSetFieldData3, 'function2',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_SelectAndSetFieldData3, 'selection3',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_SelectAndSetFieldData3, 'function3',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_SelectAndSetFieldData3, 'selection4',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_SelectAndSetFieldData3, 'function4',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_SelectAndSetFieldData3, 'functiondef',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_SelectAndSetFieldData3, 'format',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_SelectAndSetFieldData3, 'Field1',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_SelectAndSetFieldData3, 'Field2',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_SelectAndSetFieldData3, 'Field3',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_SelectAndSetFieldData3, 'Array',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_SelectAndSetFieldData3, 'Field', 
                    (SCIRun_Field, 'Field'))

  reg.add_module(SCIRun_ConvertMeshToPointCloud)
  reg.add_input_port(SCIRun_ConvertMeshToPointCloud, 'datalocation',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ConvertMeshToPointCloud, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_ConvertMeshToPointCloud, 'Field', 
                    (SCIRun_Field, 'Field'))

  reg.add_module(SCIRun_InsertStringsIntoBundle)
  reg.add_input_port(SCIRun_InsertStringsIntoBundle, 'string1_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertStringsIntoBundle, 'string2_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertStringsIntoBundle, 'string3_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertStringsIntoBundle, 'string4_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertStringsIntoBundle, 'string5_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertStringsIntoBundle, 'string6_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertStringsIntoBundle, 'replace1',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_InsertStringsIntoBundle, 'replace2',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_InsertStringsIntoBundle, 'replace3',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_InsertStringsIntoBundle, 'replace4',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_InsertStringsIntoBundle, 'replace5',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_InsertStringsIntoBundle, 'replace6',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_InsertStringsIntoBundle, 'bundle',
                   (SCIRun_Bundle, "SCIRun_Bundle"))
  reg.add_input_port(SCIRun_InsertStringsIntoBundle, 'string1',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_input_port(SCIRun_InsertStringsIntoBundle, 'string2',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_input_port(SCIRun_InsertStringsIntoBundle, 'string3',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_input_port(SCIRun_InsertStringsIntoBundle, 'string4',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_input_port(SCIRun_InsertStringsIntoBundle, 'string5',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_input_port(SCIRun_InsertStringsIntoBundle, 'string6',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_output_port(SCIRun_InsertStringsIntoBundle, 'bundle', 
                    (SCIRun_Bundle, 'bundle'))

  reg.add_module(SCIRun_GetMatricesFromBundle)
  reg.add_input_port(SCIRun_GetMatricesFromBundle, 'matrix1_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetMatricesFromBundle, 'matrix2_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetMatricesFromBundle, 'matrix3_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetMatricesFromBundle, 'matrix4_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetMatricesFromBundle, 'matrix5_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetMatricesFromBundle, 'matrix6_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetMatricesFromBundle, 'transposenrrd1',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GetMatricesFromBundle, 'transposenrrd2',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GetMatricesFromBundle, 'transposenrrd3',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GetMatricesFromBundle, 'transposenrrd4',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GetMatricesFromBundle, 'transposenrrd5',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GetMatricesFromBundle, 'transposenrrd6',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GetMatricesFromBundle, 'matrix_selection',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetMatricesFromBundle, 'bundle',
                   (SCIRun_Bundle, "SCIRun_Bundle"))
  reg.add_output_port(SCIRun_GetMatricesFromBundle, 'bundle', 
                    (SCIRun_Bundle, 'bundle'))
  reg.add_output_port(SCIRun_GetMatricesFromBundle, 'matrix1', 
                    (SCIRun_Matrix, 'matrix1'))
  reg.add_output_port(SCIRun_GetMatricesFromBundle, 'matrix2', 
                    (SCIRun_Matrix, 'matrix2'))
  reg.add_output_port(SCIRun_GetMatricesFromBundle, 'matrix3', 
                    (SCIRun_Matrix, 'matrix3'))
  reg.add_output_port(SCIRun_GetMatricesFromBundle, 'matrix4', 
                    (SCIRun_Matrix, 'matrix4'))
  reg.add_output_port(SCIRun_GetMatricesFromBundle, 'matrix5', 
                    (SCIRun_Matrix, 'matrix5'))
  reg.add_output_port(SCIRun_GetMatricesFromBundle, 'matrix6', 
                    (SCIRun_Matrix, 'matrix6'))

  reg.add_module(SCIRun_GetNrrdsFromBundle)
  reg.add_input_port(SCIRun_GetNrrdsFromBundle, 'nrrd1_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetNrrdsFromBundle, 'nrrd2_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetNrrdsFromBundle, 'nrrd3_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetNrrdsFromBundle, 'nrrd4_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetNrrdsFromBundle, 'nrrd5_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetNrrdsFromBundle, 'nrrd6_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetNrrdsFromBundle, 'transposenrrd1',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GetNrrdsFromBundle, 'transposenrrd2',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GetNrrdsFromBundle, 'transposenrrd3',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GetNrrdsFromBundle, 'transposenrrd4',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GetNrrdsFromBundle, 'transposenrrd5',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GetNrrdsFromBundle, 'transposenrrd6',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GetNrrdsFromBundle, 'nrrd_selection',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetNrrdsFromBundle, 'bundle',
                   (SCIRun_Bundle, "SCIRun_Bundle"))
  reg.add_output_port(SCIRun_GetNrrdsFromBundle, 'bundle', 
                    (SCIRun_Bundle, 'bundle'))
  reg.add_output_port(SCIRun_GetNrrdsFromBundle, 'nrrd1', 
                    (SCIRun_Nrrd, 'nrrd1'))
  reg.add_output_port(SCIRun_GetNrrdsFromBundle, 'nrrd2', 
                    (SCIRun_Nrrd, 'nrrd2'))
  reg.add_output_port(SCIRun_GetNrrdsFromBundle, 'nrrd3', 
                    (SCIRun_Nrrd, 'nrrd3'))
  reg.add_output_port(SCIRun_GetNrrdsFromBundle, 'nrrd4', 
                    (SCIRun_Nrrd, 'nrrd4'))
  reg.add_output_port(SCIRun_GetNrrdsFromBundle, 'nrrd5', 
                    (SCIRun_Nrrd, 'nrrd5'))
  reg.add_output_port(SCIRun_GetNrrdsFromBundle, 'nrrd6', 
                    (SCIRun_Nrrd, 'nrrd6'))

  reg.add_module(SCIRun_ManageFieldSeries)
  reg.add_input_port(SCIRun_ManageFieldSeries, 'num_ports',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ManageFieldSeries, 'Input',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_ManageFieldSeries, 'Output 0', 
                    (SCIRun_Field, 'Output 0'))
  reg.add_output_port(SCIRun_ManageFieldSeries, 'Output 1', 
                    (SCIRun_Field, 'Output 1'))
  reg.add_output_port(SCIRun_ManageFieldSeries, 'Output 2', 
                    (SCIRun_Field, 'Output 2'))
  reg.add_output_port(SCIRun_ManageFieldSeries, 'Output 3', 
                    (SCIRun_Field, 'Output 3'))

  reg.add_module(SCIRun_ConvertMatrixToField)
  reg.add_input_port(SCIRun_ConvertMatrixToField, 'datalocation',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ConvertMatrixToField, 'Matrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_ConvertMatrixToField, 'Field', 
                    (SCIRun_Field, 'Field'))

  reg.add_module(SCIRun_ChooseColorMap)
  reg.add_input_port(SCIRun_ChooseColorMap, 'use_first_valid',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ChooseColorMap, 'port_valid_index',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ChooseColorMap, 'port_selected_index',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ChooseColorMap, 'ColorMap',
                   (SCIRun_ColorMap, "SCIRun_ColorMap"))
  reg.add_output_port(SCIRun_ChooseColorMap, 'ColorMap', 
                    (SCIRun_ColorMap, 'ColorMap'))

  reg.add_module(SCIRun_CollectMatrices)
  reg.add_input_port(SCIRun_CollectMatrices, 'append',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CollectMatrices, 'row',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CollectMatrices, 'front',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CollectMatrices, 'Optional BaseMatrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(SCIRun_CollectMatrices, 'SubMatrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_CollectMatrices, 'CompositeMatrix', 
                    (SCIRun_Matrix, 'CompositeMatrix'))

  reg.add_module(SCIRun_ReadField)
  reg.add_input_port(SCIRun_ReadField, 'from_env',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ReadField, 'Filename',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_output_port(SCIRun_ReadField, 'Output Data', 
                    (SCIRun_Field, 'Output Data'))
  reg.add_output_port(SCIRun_ReadField, 'Filename', 
                    (core.modules.basic_modules.String, 'Filename'))

  reg.add_module(SCIRun_GetFileName)
  reg.add_input_port(SCIRun_GetFileName, 'filename_base',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetFileName, 'delay',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GetFileName, 'pinned',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_output_port(SCIRun_GetFileName, 'Full Filename', 
                    (core.modules.basic_modules.String, 'Full Filename'))

  reg.add_module(SCIRun_ClipVolumeByIsovalue)
  reg.add_input_port(SCIRun_ClipVolumeByIsovalue, 'isoval_min',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ClipVolumeByIsovalue, 'isoval_max',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ClipVolumeByIsovalue, 'isoval',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ClipVolumeByIsovalue, 'lte',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ClipVolumeByIsovalue, 'update_type',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ClipVolumeByIsovalue, 'Input',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_ClipVolumeByIsovalue, 'Optional Isovalue',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_ClipVolumeByIsovalue, 'Clipped', 
                    (SCIRun_Field, 'Clipped'))
  reg.add_output_port(SCIRun_ClipVolumeByIsovalue, 'Mapping', 
                    (SCIRun_Matrix, 'Mapping'))

  reg.add_module(SCIRun_DecomposeTensorArrayIntoEigenVectors)
  reg.add_input_port(SCIRun_DecomposeTensorArrayIntoEigenVectors, 'TensorArray',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_DecomposeTensorArrayIntoEigenVectors, 'EigenVector1', 
                    (SCIRun_Matrix, 'EigenVector1'))
  reg.add_output_port(SCIRun_DecomposeTensorArrayIntoEigenVectors, 'EigenVector2', 
                    (SCIRun_Matrix, 'EigenVector2'))
  reg.add_output_port(SCIRun_DecomposeTensorArrayIntoEigenVectors, 'EigenVector3', 
                    (SCIRun_Matrix, 'EigenVector3'))
  reg.add_output_port(SCIRun_DecomposeTensorArrayIntoEigenVectors, 'EigenValue1', 
                    (SCIRun_Matrix, 'EigenValue1'))
  reg.add_output_port(SCIRun_DecomposeTensorArrayIntoEigenVectors, 'EigenValue2', 
                    (SCIRun_Matrix, 'EigenValue2'))
  reg.add_output_port(SCIRun_DecomposeTensorArrayIntoEigenVectors, 'EigenValue3', 
                    (SCIRun_Matrix, 'EigenValue3'))

  reg.add_module(SCIRun_TransformMeshWithTransform)
  reg.add_input_port(SCIRun_TransformMeshWithTransform, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_TransformMeshWithTransform, 'Transform Matrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_TransformMeshWithTransform, 'Transformed Field', 
                    (SCIRun_Field, 'Transformed Field'))

  reg.add_module(SCIRun_ReportSearchGridInfo)
  reg.add_input_port(SCIRun_ReportSearchGridInfo, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_ReportSearchGridInfo, 'Output Sample Field', 
                    (SCIRun_Field, 'Output Sample Field'))

  reg.add_module(SCIRun_ChooseField)
  reg.add_input_port(SCIRun_ChooseField, 'use_first_valid',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ChooseField, 'port_valid_index',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ChooseField, 'port_selected_index',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ChooseField, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_ChooseField, 'Field', 
                    (SCIRun_Field, 'Field'))

  reg.add_module(SCIRun_CreateLightForViewer)
  reg.add_input_port(SCIRun_CreateLightForViewer, 'control_pos_saved',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateLightForViewer, 'control_x',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateLightForViewer, 'control_y',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateLightForViewer, 'control_z',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateLightForViewer, 'at_x',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateLightForViewer, 'at_y',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateLightForViewer, 'at_z',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateLightForViewer, 'type',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateLightForViewer, 'on',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_output_port(SCIRun_CreateLightForViewer, 'Geometry', 
                    (SCIRun_Geometry, 'Geometry'))

  reg.add_module(SCIRun_ConvertRegularMeshToStructuredMesh)
  reg.add_input_port(SCIRun_ConvertRegularMeshToStructuredMesh, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_ConvertRegularMeshToStructuredMesh, 'Output Field', 
                    (SCIRun_Field, 'Output Field'))

  reg.add_module(SCIRun_WriteColorMap)
  reg.add_input_port(SCIRun_WriteColorMap, 'filetype',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_WriteColorMap, 'confirm',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_WriteColorMap, 'confirm_once',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_WriteColorMap, 'exporttype',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_WriteColorMap, 'Input Data',
                   (SCIRun_ColorMap, "SCIRun_ColorMap"))
  reg.add_input_port(SCIRun_WriteColorMap, 'Filename',
                   (core.modules.basic_modules.String, 'tip'))

  reg.add_module(SCIRun_MergeFields)
  reg.add_input_port(SCIRun_MergeFields, 'Container Mesh',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_MergeFields, 'Insert Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_MergeFields, 'Combined Field', 
                    (SCIRun_Field, 'Combined Field'))
  reg.add_output_port(SCIRun_MergeFields, 'Extended Insert Field', 
                    (SCIRun_Field, 'Extended Insert Field'))
  reg.add_output_port(SCIRun_MergeFields, 'Combined To Extended Mapping', 
                    (SCIRun_Matrix, 'Combined To Extended Mapping'))

  reg.add_module(SCIRun_BuildPointCloudToLatVolMappingMatrix)
  reg.add_input_port(SCIRun_BuildPointCloudToLatVolMappingMatrix, 'epsilon',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_BuildPointCloudToLatVolMappingMatrix, 'PointCloudField',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_BuildPointCloudToLatVolMappingMatrix, 'LatVolField',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_BuildPointCloudToLatVolMappingMatrix, 'MappingMatrix', 
                    (SCIRun_Matrix, 'MappingMatrix'))

  reg.add_module(SCIRun_CalculateDataArray)
  reg.add_input_port(SCIRun_CalculateDataArray, 'function',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_CalculateDataArray, 'format',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_CalculateDataArray, 'DataArray',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(SCIRun_CalculateDataArray, 'Function',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_input_port(SCIRun_CalculateDataArray, 'Array',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_CalculateDataArray, 'DataArray', 
                    (SCIRun_Matrix, 'DataArray'))

  reg.add_module(SCIRun_GetColumnOrRowFromMatrix)
  reg.add_input_port(SCIRun_GetColumnOrRowFromMatrix, 'row_or_col',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetColumnOrRowFromMatrix, 'selectable_min',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GetColumnOrRowFromMatrix, 'selectable_max',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GetColumnOrRowFromMatrix, 'selectable_inc',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GetColumnOrRowFromMatrix, 'selectable_units',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetColumnOrRowFromMatrix, 'range_min',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GetColumnOrRowFromMatrix, 'range_max',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GetColumnOrRowFromMatrix, 'playmode',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetColumnOrRowFromMatrix, 'current',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GetColumnOrRowFromMatrix, 'execmode',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetColumnOrRowFromMatrix, 'delay',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GetColumnOrRowFromMatrix, 'inc_amount',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GetColumnOrRowFromMatrix, 'send_amount',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GetColumnOrRowFromMatrix, 'data_series_done',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GetColumnOrRowFromMatrix, 'Matrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(SCIRun_GetColumnOrRowFromMatrix, 'Weight Vector',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(SCIRun_GetColumnOrRowFromMatrix, 'Current Index',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_GetColumnOrRowFromMatrix, 'Vector', 
                    (SCIRun_Matrix, 'Vector'))
  reg.add_output_port(SCIRun_GetColumnOrRowFromMatrix, 'Selected Index', 
                    (SCIRun_Matrix, 'Selected Index'))

  reg.add_module(SCIRun_ShowTextureVolume)
  reg.add_input_port(SCIRun_ShowTextureVolume, 'sampling_rate_hi',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowTextureVolume, 'sampling_rate_lo',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowTextureVolume, 'gradient_min',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowTextureVolume, 'gradient_max',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowTextureVolume, 'adaptive',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowTextureVolume, 'cmap_size',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowTextureVolume, 'sw_raster',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowTextureVolume, 'render_style',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowTextureVolume, 'alpha_scale',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowTextureVolume, 'interp_mode',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowTextureVolume, 'shading',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowTextureVolume, 'ambient',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowTextureVolume, 'diffuse',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowTextureVolume, 'specular',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowTextureVolume, 'shine',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowTextureVolume, 'light',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowTextureVolume, 'blend_res',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowTextureVolume, 'multi_level',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowTextureVolume, 'use_stencil',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowTextureVolume, 'invert_opacity',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowTextureVolume, 'num_clipping_planes',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowTextureVolume, 'show_clipping_widgets',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowTextureVolume, 'level_on',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ShowTextureVolume, 'level_vals',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ShowTextureVolume, 'Texture',
                   (SCIRun_Texture, "SCIRun_Texture"))
  reg.add_input_port(SCIRun_ShowTextureVolume, 'ColorMap',
                   (SCIRun_ColorMap, "SCIRun_ColorMap"))
  reg.add_input_port(SCIRun_ShowTextureVolume, 'ColorMap2',
                   (SCIRun_ColorMap2, "SCIRun_ColorMap2"))
  reg.add_output_port(SCIRun_ShowTextureVolume, 'Geometry', 
                    (SCIRun_Geometry, 'Geometry'))
  reg.add_output_port(SCIRun_ShowTextureVolume, 'ColorMap', 
                    (SCIRun_ColorMap, 'ColorMap'))

  reg.add_module(SCIRun_GetCentroidsFromMesh)
  reg.add_input_port(SCIRun_GetCentroidsFromMesh, 'TetVolField',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_GetCentroidsFromMesh, 'PointCloudField', 
                    (SCIRun_Field, 'PointCloudField'))

  reg.add_module(SCIRun_ReadColorMap2D)
  reg.add_input_port(SCIRun_ReadColorMap2D, 'from_env',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ReadColorMap2D, 'Filename',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_output_port(SCIRun_ReadColorMap2D, 'Output Data', 
                    (SCIRun_ColorMap2, 'Output Data'))
  reg.add_output_port(SCIRun_ReadColorMap2D, 'Filename', 
                    (core.modules.basic_modules.String, 'Filename'))

  reg.add_module(SCIRun_ConvertLatVolDataFromNodeToElem)
  reg.add_input_port(SCIRun_ConvertLatVolDataFromNodeToElem, 'Node Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_ConvertLatVolDataFromNodeToElem, 'Elem Field', 
                    (SCIRun_Field, 'Elem Field'))

  reg.add_module(SCIRun_InsertHexVolSheetAlongSurface)
  reg.add_input_port(SCIRun_InsertHexVolSheetAlongSurface, 'side',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertHexVolSheetAlongSurface, 'addlayer',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertHexVolSheetAlongSurface, 'HexField',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_InsertHexVolSheetAlongSurface, 'TriField',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_InsertHexVolSheetAlongSurface, 'Side1Field', 
                    (SCIRun_Field, 'Side1Field'))
  reg.add_output_port(SCIRun_InsertHexVolSheetAlongSurface, 'Side2Field', 
                    (SCIRun_Field, 'Side2Field'))

  reg.add_module(SCIRun_ExtractIsosurfaceByFunction)
  reg.add_input_port(SCIRun_ExtractIsosurfaceByFunction, 'function',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ExtractIsosurfaceByFunction, 'zero_checks',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ExtractIsosurfaceByFunction, 'slice_value_min',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ExtractIsosurfaceByFunction, 'slice_value_max',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ExtractIsosurfaceByFunction, 'slice_value',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ExtractIsosurfaceByFunction, 'slice_value_typed',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ExtractIsosurfaceByFunction, 'slice_value_quantity',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ExtractIsosurfaceByFunction, 'quantity_range',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ExtractIsosurfaceByFunction, 'quantity_clusive',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ExtractIsosurfaceByFunction, 'quantity_min',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ExtractIsosurfaceByFunction, 'quantity_max',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ExtractIsosurfaceByFunction, 'quantity_list',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ExtractIsosurfaceByFunction, 'slice_value_list',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ExtractIsosurfaceByFunction, 'matrix_list',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ExtractIsosurfaceByFunction, 'extract_from_new_field',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ExtractIsosurfaceByFunction, 'algorithm',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ExtractIsosurfaceByFunction, 'build_trisurf',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ExtractIsosurfaceByFunction, 'build_geom',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ExtractIsosurfaceByFunction, 'active_slice_value_selection_tab',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ExtractIsosurfaceByFunction, 'active_tab',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ExtractIsosurfaceByFunction, 'update_type',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ExtractIsosurfaceByFunction, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_ExtractIsosurfaceByFunction, 'Optional Slice values',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_ExtractIsosurfaceByFunction, 'Output Field', 
                    (SCIRun_Field, 'Output Field'))

  reg.add_module(SCIRun_BuildNoiseColumnMatrix)
  reg.add_input_port(SCIRun_BuildNoiseColumnMatrix, 'snr',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_BuildNoiseColumnMatrix, 'Signal',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_BuildNoiseColumnMatrix, 'Noise', 
                    (SCIRun_Matrix, 'Noise'))

  reg.add_module(SCIRun_MergeTriSurfs)
  reg.add_input_port(SCIRun_MergeTriSurfs, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_MergeTriSurfs, 'Output Field', 
                    (SCIRun_Field, 'Output Field'))

  reg.add_module(SCIRun_ReadString)
  reg.add_input_port(SCIRun_ReadString, 'from_env',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ReadString, 'Filename',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_output_port(SCIRun_ReadString, 'Output Data', 
                    (core.modules.basic_modules.String, 'Output Data'))
  reg.add_output_port(SCIRun_ReadString, 'Filename', 
                    (core.modules.basic_modules.String, 'Filename'))

  reg.add_module(SCIRun_InterfaceWithTetGen)
  reg.add_input_port(SCIRun_InterfaceWithTetGen, 'switch',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InterfaceWithTetGen, 'Main',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_InterfaceWithTetGen, 'Points',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_InterfaceWithTetGen, 'Region Attribs',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_InterfaceWithTetGen, 'Regions',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_InterfaceWithTetGen, 'TetVol', 
                    (SCIRun_Field, 'TetVol'))

  reg.add_module(SCIRun_CalculateMeshNodes)
  reg.add_input_port(SCIRun_CalculateMeshNodes, 'function',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_CalculateMeshNodes, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_CalculateMeshNodes, 'Function',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_input_port(SCIRun_CalculateMeshNodes, 'Array',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_CalculateMeshNodes, 'Field', 
                    (SCIRun_Field, 'Field'))

  reg.add_module(SCIRun_CreateImage)
  reg.add_input_port(SCIRun_CreateImage, 'sizex',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateImage, 'sizey',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateImage, 'sizez',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateImage, 'z_value',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateImage, 'auto_size',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateImage, 'axis',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateImage, 'padpercent',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateImage, 'pos',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateImage, 'data_at',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_CreateImage, 'update_type',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_CreateImage, 'corigin_x',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateImage, 'corigin_y',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateImage, 'corigin_z',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateImage, 'cnormal_x',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateImage, 'cnormal_y',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateImage, 'cnormal_z',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateImage, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_CreateImage, 'Output Sample Field', 
                    (SCIRun_Field, 'Output Sample Field'))

  reg.add_module(SCIRun_SplitNodesByDomain)
  reg.add_input_port(SCIRun_SplitNodesByDomain, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_SplitNodesByDomain, 'SplitField', 
                    (SCIRun_Field, 'SplitField'))

  reg.add_module(SCIRun_CalculateFieldDataCompiled)
  reg.add_input_port(SCIRun_CalculateFieldDataCompiled, 'outputdatatype',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_CalculateFieldDataCompiled, 'function',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_CalculateFieldDataCompiled, 'cache',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CalculateFieldDataCompiled, 'Function',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_input_port(SCIRun_CalculateFieldDataCompiled, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_CalculateFieldDataCompiled, 'Output Field', 
                    (SCIRun_Field, 'Output Field'))

  reg.add_module(SCIRun_ReadColorMap)
  reg.add_input_port(SCIRun_ReadColorMap, 'from_env',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ReadColorMap, 'Filename',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_output_port(SCIRun_ReadColorMap, 'Output Data', 
                    (SCIRun_ColorMap, 'Output Data'))
  reg.add_output_port(SCIRun_ReadColorMap, 'Filename', 
                    (core.modules.basic_modules.String, 'Filename'))

  reg.add_module(SCIRun_MapFieldDataFromElemToNode)
  reg.add_input_port(SCIRun_MapFieldDataFromElemToNode, 'method',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_MapFieldDataFromElemToNode, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_MapFieldDataFromElemToNode, 'Field', 
                    (SCIRun_Field, 'Field'))

  reg.add_module(SCIRun_ShowFieldGlyphs)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'scalars_has_data',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'scalars_on',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'scalars_display_type',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'scalars_transparency',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'scalars_normalize',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'scalars_color_type',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'scalars_resolution',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'vectors_has_data',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'vectors_on',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'vectors_display_type',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'vectors_transparency',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'vectors_normalize',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'vectors_bidirectional',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'vectors_color_type',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'vectors_resolution',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'tensors_has_data',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'tensors_on',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'tensors_display_type',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'tensors_transparency',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'tensors_normalize',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'tensors_color_type',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'tensors_resolution',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'tensors_emphasis',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'secondary_has_data',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'secondary_on',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'secondary_display_type',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'secondary_color_type',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'secondary_alpha',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'secondary_value',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'tertiary_has_data',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'tertiary_on',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'tertiary_display_type',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'tertiary_color_type',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'tertiary_alpha',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'tertiary_value',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'text_on',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'text_color_type',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'text_color_r',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'text_color_g',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'text_color_b',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'text_backface_cull',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'text_always_visible',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'text_fontsize',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'text_precision',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'text_render_locations',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'text_show_data',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'text_show_nodes',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'text_show_edges',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'text_show_faces',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'text_show_cells',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'def_color_r',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'def_color_g',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'def_color_b',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'def_color_a',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'active_tab',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'interactive_mode',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'show_progress',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'field_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'field_name_override',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'approx_div',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'use_default_size',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'Primary Data',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'Primary ColorMap',
                   (SCIRun_ColorMap, "SCIRun_ColorMap"))
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'Secondary Data',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'Secondary ColorMap',
                   (SCIRun_ColorMap, "SCIRun_ColorMap"))
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'Tertiary Data',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_ShowFieldGlyphs, 'Tertiary ColorMap',
                   (SCIRun_ColorMap, "SCIRun_ColorMap"))
  reg.add_output_port(SCIRun_ShowFieldGlyphs, 'Scene Graph', 
                    (SCIRun_Geometry, 'Scene Graph'))

  reg.add_module(SCIRun_JoinBundles)
  reg.add_input_port(SCIRun_JoinBundles, 'bundle',
                   (SCIRun_Bundle, "SCIRun_Bundle"))
  reg.add_output_port(SCIRun_JoinBundles, 'bundle', 
                    (SCIRun_Bundle, 'bundle'))

  reg.add_module(SCIRun_ReportBundleInfo)
  reg.add_input_port(SCIRun_ReportBundleInfo, 'tclinfostring',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ReportBundleInfo, 'bundle',
                   (SCIRun_Bundle, "SCIRun_Bundle"))

  reg.add_module(SCIRun_GetFieldData)
  reg.add_input_port(SCIRun_GetFieldData, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_GetFieldData, 'Data', 
                    (SCIRun_Matrix, 'Data'))

  reg.add_module(SCIRun_ReportDataArrayMeasure)
  reg.add_input_port(SCIRun_ReportDataArrayMeasure, 'measure',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ReportDataArrayMeasure, 'Array',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_ReportDataArrayMeasure, 'Measure', 
                    (SCIRun_Matrix, 'Measure'))

  reg.add_module(SCIRun_CalculateFieldData2)
  reg.add_input_port(SCIRun_CalculateFieldData2, 'function',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_CalculateFieldData2, 'format',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_CalculateFieldData2, 'Field1',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_CalculateFieldData2, 'Field2',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_CalculateFieldData2, 'Function',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_input_port(SCIRun_CalculateFieldData2, 'Array',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_CalculateFieldData2, 'Field', 
                    (SCIRun_Field, 'Field'))

  reg.add_module(SCIRun_SplitFileName)
  reg.add_input_port(SCIRun_SplitFileName, 'Filename',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_output_port(SCIRun_SplitFileName, 'Pathname', 
                    (core.modules.basic_modules.String, 'Pathname'))
  reg.add_output_port(SCIRun_SplitFileName, 'Filename Base', 
                    (core.modules.basic_modules.String, 'Filename Base'))
  reg.add_output_port(SCIRun_SplitFileName, 'Extension', 
                    (core.modules.basic_modules.String, 'Extension'))
  reg.add_output_port(SCIRun_SplitFileName, 'Filename', 
                    (core.modules.basic_modules.String, 'Filename'))

  reg.add_module(SCIRun_SmoothMesh)
  reg.add_input_port(SCIRun_SmoothMesh, 'Input',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_SmoothMesh, 'IsoValue',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_SmoothMesh, 'Smoothed', 
                    (SCIRun_Field, 'Smoothed'))

  reg.add_module(SCIRun_GenerateSinglePointProbeFromField)
  reg.add_input_port(SCIRun_GenerateSinglePointProbeFromField, 'main_frame',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GenerateSinglePointProbeFromField, 'locx',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GenerateSinglePointProbeFromField, 'locy',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GenerateSinglePointProbeFromField, 'locz',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GenerateSinglePointProbeFromField, 'value',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GenerateSinglePointProbeFromField, 'node',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GenerateSinglePointProbeFromField, 'edge',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GenerateSinglePointProbeFromField, 'face',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GenerateSinglePointProbeFromField, 'cell',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GenerateSinglePointProbeFromField, 'show_value',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GenerateSinglePointProbeFromField, 'show_node',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GenerateSinglePointProbeFromField, 'show_edge',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GenerateSinglePointProbeFromField, 'show_face',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GenerateSinglePointProbeFromField, 'show_cell',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GenerateSinglePointProbeFromField, 'probe_scale',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GenerateSinglePointProbeFromField, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_GenerateSinglePointProbeFromField, 'GenerateSinglePointProbeFromField Widget', 
                    (SCIRun_Geometry, 'GenerateSinglePointProbeFromField Widget'))
  reg.add_output_port(SCIRun_GenerateSinglePointProbeFromField, 'GenerateSinglePointProbeFromField Point', 
                    (SCIRun_Field, 'GenerateSinglePointProbeFromField Point'))
  reg.add_output_port(SCIRun_GenerateSinglePointProbeFromField, 'Element Index', 
                    (SCIRun_Matrix, 'Element Index'))

  reg.add_module(SCIRun_CalculateInsideWhichField)
  reg.add_input_port(SCIRun_CalculateInsideWhichField, 'outputbasis',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_CalculateInsideWhichField, 'outputtype',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_CalculateInsideWhichField, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_CalculateInsideWhichField, 'Object',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_CalculateInsideWhichField, 'Field', 
                    (SCIRun_Field, 'Field'))

  reg.add_module(SCIRun_InsertPathsIntoBundle)
  reg.add_input_port(SCIRun_InsertPathsIntoBundle, 'path1_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertPathsIntoBundle, 'path2_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertPathsIntoBundle, 'path3_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertPathsIntoBundle, 'path4_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertPathsIntoBundle, 'path5_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertPathsIntoBundle, 'path6_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertPathsIntoBundle, 'replace1',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_InsertPathsIntoBundle, 'replace2',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_InsertPathsIntoBundle, 'replace3',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_InsertPathsIntoBundle, 'replace4',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_InsertPathsIntoBundle, 'replace5',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_InsertPathsIntoBundle, 'replace6',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_InsertPathsIntoBundle, 'bundlename',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertPathsIntoBundle, 'bundle',
                   (SCIRun_Bundle, "SCIRun_Bundle"))
  reg.add_input_port(SCIRun_InsertPathsIntoBundle, 'path1',
                   (SCIRun_Path, "SCIRun_Path"))
  reg.add_input_port(SCIRun_InsertPathsIntoBundle, 'path2',
                   (SCIRun_Path, "SCIRun_Path"))
  reg.add_input_port(SCIRun_InsertPathsIntoBundle, 'path3',
                   (SCIRun_Path, "SCIRun_Path"))
  reg.add_input_port(SCIRun_InsertPathsIntoBundle, 'path4',
                   (SCIRun_Path, "SCIRun_Path"))
  reg.add_input_port(SCIRun_InsertPathsIntoBundle, 'path5',
                   (SCIRun_Path, "SCIRun_Path"))
  reg.add_input_port(SCIRun_InsertPathsIntoBundle, 'path6',
                   (SCIRun_Path, "SCIRun_Path"))
  reg.add_output_port(SCIRun_InsertPathsIntoBundle, 'bundle', 
                    (SCIRun_Bundle, 'bundle'))

  reg.add_module(SCIRun_RemoveZerosFromMatrix)
  reg.add_input_port(SCIRun_RemoveZerosFromMatrix, 'row_or_col',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_RemoveZerosFromMatrix, 'Matrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_RemoveZerosFromMatrix, 'Matrix', 
                    (SCIRun_Matrix, 'Matrix'))

  reg.add_module(SCIRun_GetNetworkFileName)
  reg.add_output_port(SCIRun_GetNetworkFileName, 'String', 
                    (core.modules.basic_modules.String, 'String'))

  reg.add_module(SCIRun_RemoveZeroRowsAndColumns)
  reg.add_input_port(SCIRun_RemoveZeroRowsAndColumns, 'Matrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_RemoveZeroRowsAndColumns, 'ReducedMatrix', 
                    (SCIRun_Matrix, 'ReducedMatrix'))
  reg.add_output_port(SCIRun_RemoveZeroRowsAndColumns, 'LeftMapping', 
                    (SCIRun_Matrix, 'LeftMapping'))
  reg.add_output_port(SCIRun_RemoveZeroRowsAndColumns, 'RightMapping', 
                    (SCIRun_Matrix, 'RightMapping'))

  reg.add_module(SCIRun_CalculateGradients)
  reg.add_input_port(SCIRun_CalculateGradients, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_CalculateGradients, 'Output CalculateGradients', 
                    (SCIRun_Field, 'Output CalculateGradients'))

  reg.add_module(SCIRun_CalculateLatVolGradientsAtNodes)
  reg.add_input_port(SCIRun_CalculateLatVolGradientsAtNodes, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_CalculateLatVolGradientsAtNodes, 'Output Gradient', 
                    (SCIRun_Field, 'Output Gradient'))

  reg.add_module(SCIRun_GetColorMap2sFromBundle)
  reg.add_input_port(SCIRun_GetColorMap2sFromBundle, 'colormap21_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetColorMap2sFromBundle, 'colormap22_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetColorMap2sFromBundle, 'colormap23_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetColorMap2sFromBundle, 'colormap24_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetColorMap2sFromBundle, 'colormap25_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetColorMap2sFromBundle, 'colormap26_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetColorMap2sFromBundle, 'colormap2_selection',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetColorMap2sFromBundle, 'bundle',
                   (SCIRun_Bundle, "SCIRun_Bundle"))
  reg.add_output_port(SCIRun_GetColorMap2sFromBundle, 'bundle', 
                    (SCIRun_Bundle, 'bundle'))
  reg.add_output_port(SCIRun_GetColorMap2sFromBundle, 'colormap21', 
                    (SCIRun_ColorMap2, 'colormap21'))
  reg.add_output_port(SCIRun_GetColorMap2sFromBundle, 'colormap22', 
                    (SCIRun_ColorMap2, 'colormap22'))
  reg.add_output_port(SCIRun_GetColorMap2sFromBundle, 'colormap23', 
                    (SCIRun_ColorMap2, 'colormap23'))
  reg.add_output_port(SCIRun_GetColorMap2sFromBundle, 'colormap24', 
                    (SCIRun_ColorMap2, 'colormap24'))
  reg.add_output_port(SCIRun_GetColorMap2sFromBundle, 'colormap25', 
                    (SCIRun_ColorMap2, 'colormap25'))
  reg.add_output_port(SCIRun_GetColorMap2sFromBundle, 'colormap26', 
                    (SCIRun_ColorMap2, 'colormap26'))

  reg.add_module(SCIRun_ReadMatrix)
  reg.add_input_port(SCIRun_ReadMatrix, 'from_env',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ReadMatrix, 'Filename',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_output_port(SCIRun_ReadMatrix, 'Output Data', 
                    (SCIRun_Matrix, 'Output Data'))
  reg.add_output_port(SCIRun_ReadMatrix, 'Filename', 
                    (core.modules.basic_modules.String, 'Filename'))

  reg.add_module(SCIRun_GenerateStreamLines)
  reg.add_input_port(SCIRun_GenerateStreamLines, 'stepsize',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GenerateStreamLines, 'tolerance',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GenerateStreamLines, 'maxsteps',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GenerateStreamLines, 'direction',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GenerateStreamLines, 'value',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GenerateStreamLines, 'remove_colinear_pts',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GenerateStreamLines, 'method',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GenerateStreamLines, 'nthreads',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GenerateStreamLines, 'auto_parameterize',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GenerateStreamLines, 'Vector Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_GenerateStreamLines, 'Seed Points',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_GenerateStreamLines, 'Streamlines', 
                    (SCIRun_Field, 'Streamlines'))

  reg.add_module(SCIRun_EditMeshBoundingBox)
  reg.add_input_port(SCIRun_EditMeshBoundingBox, 'outputcenterx',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_EditMeshBoundingBox, 'outputcentery',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_EditMeshBoundingBox, 'outputcenterz',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_EditMeshBoundingBox, 'outputsizex',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_EditMeshBoundingBox, 'outputsizey',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_EditMeshBoundingBox, 'outputsizez',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_EditMeshBoundingBox, 'useoutputcenter',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_EditMeshBoundingBox, 'useoutputsize',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_EditMeshBoundingBox, 'box_scale',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_EditMeshBoundingBox, 'box_mode',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_EditMeshBoundingBox, 'box_real_scale',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_EditMeshBoundingBox, 'box_center_x',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_EditMeshBoundingBox, 'box_center_y',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_EditMeshBoundingBox, 'box_center_z',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_EditMeshBoundingBox, 'box_right_x',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_EditMeshBoundingBox, 'box_right_y',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_EditMeshBoundingBox, 'box_right_z',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_EditMeshBoundingBox, 'box_down_x',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_EditMeshBoundingBox, 'box_down_y',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_EditMeshBoundingBox, 'box_down_z',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_EditMeshBoundingBox, 'box_in_x',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_EditMeshBoundingBox, 'box_in_y',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_EditMeshBoundingBox, 'box_in_z',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_EditMeshBoundingBox, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_EditMeshBoundingBox, 'Output Field', 
                    (SCIRun_Field, 'Output Field'))
  reg.add_output_port(SCIRun_EditMeshBoundingBox, 'Transformation Widget', 
                    (SCIRun_Geometry, 'Transformation Widget'))
  reg.add_output_port(SCIRun_EditMeshBoundingBox, 'Transformation Matrix', 
                    (SCIRun_Matrix, 'Transformation Matrix'))

  reg.add_module(SCIRun_PrintStringIntoString)
  reg.add_input_port(SCIRun_PrintStringIntoString, 'formatstring',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_PrintStringIntoString, 'Format',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_input_port(SCIRun_PrintStringIntoString, 'Input',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_output_port(SCIRun_PrintStringIntoString, 'Output', 
                    (core.modules.basic_modules.String, 'Output'))

  reg.add_module(SCIRun_SetFieldDataValues)
  reg.add_input_port(SCIRun_SetFieldDataValues, 'newval',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_SetFieldDataValues, 'InField',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_SetFieldDataValues, 'OutField', 
                    (SCIRun_Field, 'OutField'))

  reg.add_module(SCIRun_GetSubmatrix)
  reg.add_input_port(SCIRun_GetSubmatrix, 'mincol',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetSubmatrix, 'maxcol',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetSubmatrix, 'minrow',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetSubmatrix, 'maxrow',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetSubmatrix, 'nrow',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetSubmatrix, 'ncol',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetSubmatrix, 'Input Matrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(SCIRun_GetSubmatrix, 'Optional Range Bounds',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_GetSubmatrix, 'Output Matrix', 
                    (SCIRun_Matrix, 'Output Matrix'))

  reg.add_module(SCIRun_GenerateStreamLinesWithPlacementHeuristic)
  reg.add_input_port(SCIRun_GenerateStreamLinesWithPlacementHeuristic, 'numsl',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GenerateStreamLinesWithPlacementHeuristic, 'numpts',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GenerateStreamLinesWithPlacementHeuristic, 'minper',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GenerateStreamLinesWithPlacementHeuristic, 'maxper',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GenerateStreamLinesWithPlacementHeuristic, 'ming',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GenerateStreamLinesWithPlacementHeuristic, 'maxg',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GenerateStreamLinesWithPlacementHeuristic, 'numsamples',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GenerateStreamLinesWithPlacementHeuristic, 'method',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GenerateStreamLinesWithPlacementHeuristic, 'stepsize',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GenerateStreamLinesWithPlacementHeuristic, 'stepout',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GenerateStreamLinesWithPlacementHeuristic, 'maxsteps',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GenerateStreamLinesWithPlacementHeuristic, 'minmag',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GenerateStreamLinesWithPlacementHeuristic, 'direction',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GenerateStreamLinesWithPlacementHeuristic, 'Source',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_GenerateStreamLinesWithPlacementHeuristic, 'Weighting',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_GenerateStreamLinesWithPlacementHeuristic, 'Flow',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_GenerateStreamLinesWithPlacementHeuristic, 'Compare',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_GenerateStreamLinesWithPlacementHeuristic, 'Seed points',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_GenerateStreamLinesWithPlacementHeuristic, 'Streamlines', 
                    (SCIRun_Field, 'Streamlines'))
  reg.add_output_port(SCIRun_GenerateStreamLinesWithPlacementHeuristic, 'Render', 
                    (SCIRun_Field, 'Render'))

  reg.add_module(SCIRun_CalculateSignedDistanceToField)
  reg.add_input_port(SCIRun_CalculateSignedDistanceToField, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_CalculateSignedDistanceToField, 'ObjectField',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_CalculateSignedDistanceToField, 'SignedDistanceField', 
                    (SCIRun_Field, 'SignedDistanceField'))

  reg.add_module(SCIRun_EvaluateLinAlgUnary)
  reg.add_input_port(SCIRun_EvaluateLinAlgUnary, 'op',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_EvaluateLinAlgUnary, 'function',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_EvaluateLinAlgUnary, 'Input',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_EvaluateLinAlgUnary, 'Output', 
                    (SCIRun_Matrix, 'Output'))

  reg.add_module(SCIRun_InsertMatricesIntoBundle)
  reg.add_input_port(SCIRun_InsertMatricesIntoBundle, 'matrix1_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertMatricesIntoBundle, 'matrix2_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertMatricesIntoBundle, 'matrix3_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertMatricesIntoBundle, 'matrix4_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertMatricesIntoBundle, 'matrix5_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertMatricesIntoBundle, 'matrix6_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertMatricesIntoBundle, 'replace1',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_InsertMatricesIntoBundle, 'replace2',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_InsertMatricesIntoBundle, 'replace3',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_InsertMatricesIntoBundle, 'replace4',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_InsertMatricesIntoBundle, 'replace5',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_InsertMatricesIntoBundle, 'replace6',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_InsertMatricesIntoBundle, 'bundlename',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertMatricesIntoBundle, 'bundle',
                   (SCIRun_Bundle, "SCIRun_Bundle"))
  reg.add_input_port(SCIRun_InsertMatricesIntoBundle, 'matrix1',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(SCIRun_InsertMatricesIntoBundle, 'matrix2',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(SCIRun_InsertMatricesIntoBundle, 'matrix3',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(SCIRun_InsertMatricesIntoBundle, 'matrix4',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(SCIRun_InsertMatricesIntoBundle, 'matrix5',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(SCIRun_InsertMatricesIntoBundle, 'matrix6',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_InsertMatricesIntoBundle, 'bundle', 
                    (SCIRun_Bundle, 'bundle'))

  reg.add_module(SCIRun_AppendDataArrays)
  reg.add_input_port(SCIRun_AppendDataArrays, 'Array',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_AppendDataArrays, 'Array', 
                    (SCIRun_Matrix, 'Array'))

  reg.add_module(SCIRun_WriteString)
  reg.add_input_port(SCIRun_WriteString, 'filetype',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_WriteString, 'confirm',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_WriteString, 'confirm_once',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_WriteString, 'String',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_input_port(SCIRun_WriteString, 'Filename',
                   (core.modules.basic_modules.String, 'tip'))

  reg.add_module(SCIRun_TimeControls)
  reg.add_output_port(SCIRun_TimeControls, 'time', 
                    (SCIRun_Time, 'time'))

  reg.add_module(SCIRun_InsertNrrdsIntoBundle)
  reg.add_input_port(SCIRun_InsertNrrdsIntoBundle, 'nrrd1_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertNrrdsIntoBundle, 'nrrd2_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertNrrdsIntoBundle, 'nrrd3_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertNrrdsIntoBundle, 'nrrd4_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertNrrdsIntoBundle, 'nrrd5_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertNrrdsIntoBundle, 'nrrd6_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertNrrdsIntoBundle, 'replace1',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_InsertNrrdsIntoBundle, 'replace2',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_InsertNrrdsIntoBundle, 'replace3',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_InsertNrrdsIntoBundle, 'replace4',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_InsertNrrdsIntoBundle, 'replace5',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_InsertNrrdsIntoBundle, 'replace6',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_InsertNrrdsIntoBundle, 'bundlename',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertNrrdsIntoBundle, 'bundle',
                   (SCIRun_Bundle, "SCIRun_Bundle"))
  reg.add_input_port(SCIRun_InsertNrrdsIntoBundle, 'nrrd1',
                   (SCIRun_Nrrd, "SCIRun_Nrrd"))
  reg.add_input_port(SCIRun_InsertNrrdsIntoBundle, 'nrrd2',
                   (SCIRun_Nrrd, "SCIRun_Nrrd"))
  reg.add_input_port(SCIRun_InsertNrrdsIntoBundle, 'nrrd3',
                   (SCIRun_Nrrd, "SCIRun_Nrrd"))
  reg.add_input_port(SCIRun_InsertNrrdsIntoBundle, 'nrrd4',
                   (SCIRun_Nrrd, "SCIRun_Nrrd"))
  reg.add_input_port(SCIRun_InsertNrrdsIntoBundle, 'nrrd5',
                   (SCIRun_Nrrd, "SCIRun_Nrrd"))
  reg.add_input_port(SCIRun_InsertNrrdsIntoBundle, 'nrrd6',
                   (SCIRun_Nrrd, "SCIRun_Nrrd"))
  reg.add_output_port(SCIRun_InsertNrrdsIntoBundle, 'bundle', 
                    (SCIRun_Bundle, 'bundle'))

  reg.add_module(SCIRun_InterfaceWithCubit)
  reg.add_input_port(SCIRun_InterfaceWithCubit, 'cubitdir',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InterfaceWithCubit, 'ncdump',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InterfaceWithCubit, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_InterfaceWithCubit, 'PointCloudField',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_InterfaceWithCubit, 'Field', 
                    (SCIRun_Field, 'Field'))

  reg.add_module(SCIRun_CreateString)
  reg.add_input_port(SCIRun_CreateString, 'inputstring',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_output_port(SCIRun_CreateString, 'Output', 
                    (core.modules.basic_modules.String, 'Output'))

  reg.add_module(SCIRun_ClipFieldByFunction)
  reg.add_input_port(SCIRun_ClipFieldByFunction, 'mode',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ClipFieldByFunction, 'function',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ClipFieldByFunction, 'Function',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_input_port(SCIRun_ClipFieldByFunction, 'Input',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_ClipFieldByFunction, 'Clipped', 
                    (SCIRun_Field, 'Clipped'))
  reg.add_output_port(SCIRun_ClipFieldByFunction, 'Mapping', 
                    (SCIRun_Matrix, 'Mapping'))
  reg.add_output_port(SCIRun_ClipFieldByFunction, 'MaskVector', 
                    (SCIRun_Nrrd, 'MaskVector'))

  reg.add_module(SCIRun_CreateTensorArray)
  reg.add_input_port(SCIRun_CreateTensorArray, 'EigenVector1',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(SCIRun_CreateTensorArray, 'EigenVector2',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(SCIRun_CreateTensorArray, 'EigenValue1',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(SCIRun_CreateTensorArray, 'EigenValue2',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(SCIRun_CreateTensorArray, 'EigenValue3',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_CreateTensorArray, 'TensorArray', 
                    (SCIRun_Matrix, 'TensorArray'))

  reg.add_module(SCIRun_WriteField)
  reg.add_input_port(SCIRun_WriteField, 'filetype',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_WriteField, 'confirm',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_WriteField, 'confirm_once',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_WriteField, 'exporttype',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_WriteField, 'increment',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_WriteField, 'current',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_WriteField, 'Input Data',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_WriteField, 'Filename',
                   (core.modules.basic_modules.String, 'tip'))

  reg.add_module(SCIRun_BuildMappingMatrix)
  reg.add_input_port(SCIRun_BuildMappingMatrix, 'interpolation_basis',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_BuildMappingMatrix, 'map_source_to_single_dest',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_BuildMappingMatrix, 'exhaustive_search',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_BuildMappingMatrix, 'exhaustive_search_max_dist',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_BuildMappingMatrix, 'np',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_BuildMappingMatrix, 'Source',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_BuildMappingMatrix, 'Destination',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_BuildMappingMatrix, 'Mapping', 
                    (SCIRun_Matrix, 'Mapping'))

  reg.add_module(SCIRun_MapFieldDataFromNodeToElem)
  reg.add_input_port(SCIRun_MapFieldDataFromNodeToElem, 'method',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_MapFieldDataFromNodeToElem, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_MapFieldDataFromNodeToElem, 'Field', 
                    (SCIRun_Field, 'Field'))

  reg.add_module(SCIRun_InsertBundlesIntoBundle)
  reg.add_input_port(SCIRun_InsertBundlesIntoBundle, 'bundle1_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertBundlesIntoBundle, 'bundle2_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertBundlesIntoBundle, 'bundle3_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertBundlesIntoBundle, 'bundle4_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertBundlesIntoBundle, 'bundle5_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertBundlesIntoBundle, 'bundle6_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertBundlesIntoBundle, 'replace1',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_InsertBundlesIntoBundle, 'replace2',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_InsertBundlesIntoBundle, 'replace3',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_InsertBundlesIntoBundle, 'replace4',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_InsertBundlesIntoBundle, 'replace5',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_InsertBundlesIntoBundle, 'replace6',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_InsertBundlesIntoBundle, 'bundlename',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertBundlesIntoBundle, 'bundle',
                   (SCIRun_Bundle, "SCIRun_Bundle"))
  reg.add_input_port(SCIRun_InsertBundlesIntoBundle, 'bundle1',
                   (SCIRun_Bundle, "SCIRun_Bundle"))
  reg.add_input_port(SCIRun_InsertBundlesIntoBundle, 'bundle2',
                   (SCIRun_Bundle, "SCIRun_Bundle"))
  reg.add_input_port(SCIRun_InsertBundlesIntoBundle, 'bundle3',
                   (SCIRun_Bundle, "SCIRun_Bundle"))
  reg.add_input_port(SCIRun_InsertBundlesIntoBundle, 'bundle4',
                   (SCIRun_Bundle, "SCIRun_Bundle"))
  reg.add_input_port(SCIRun_InsertBundlesIntoBundle, 'bundle5',
                   (SCIRun_Bundle, "SCIRun_Bundle"))
  reg.add_input_port(SCIRun_InsertBundlesIntoBundle, 'bundle6',
                   (SCIRun_Bundle, "SCIRun_Bundle"))
  reg.add_output_port(SCIRun_InsertBundlesIntoBundle, 'bundle', 
                    (SCIRun_Bundle, 'bundle'))

  reg.add_module(SCIRun_ReadBundle)
  reg.add_input_port(SCIRun_ReadBundle, 'from_env',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ReadBundle, 'types',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ReadBundle, 'Filename',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_output_port(SCIRun_ReadBundle, 'bundle', 
                    (SCIRun_Bundle, 'bundle'))
  reg.add_output_port(SCIRun_ReadBundle, 'Filename', 
                    (core.modules.basic_modules.String, 'Filename'))

  reg.add_module(SCIRun_GetStringsFromBundle)
  reg.add_input_port(SCIRun_GetStringsFromBundle, 'string1_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetStringsFromBundle, 'string2_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetStringsFromBundle, 'string3_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetStringsFromBundle, 'string4_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetStringsFromBundle, 'string5_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetStringsFromBundle, 'string6_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetStringsFromBundle, 'string_selection',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetStringsFromBundle, 'bundle',
                   (SCIRun_Bundle, "SCIRun_Bundle"))
  reg.add_output_port(SCIRun_GetStringsFromBundle, 'bundle', 
                    (SCIRun_Bundle, 'bundle'))
  reg.add_output_port(SCIRun_GetStringsFromBundle, 'string1', 
                    (core.modules.basic_modules.String, 'string1'))
  reg.add_output_port(SCIRun_GetStringsFromBundle, 'string2', 
                    (core.modules.basic_modules.String, 'string2'))
  reg.add_output_port(SCIRun_GetStringsFromBundle, 'string3', 
                    (core.modules.basic_modules.String, 'string3'))
  reg.add_output_port(SCIRun_GetStringsFromBundle, 'string4', 
                    (core.modules.basic_modules.String, 'string4'))
  reg.add_output_port(SCIRun_GetStringsFromBundle, 'string5', 
                    (core.modules.basic_modules.String, 'string5'))
  reg.add_output_port(SCIRun_GetStringsFromBundle, 'string6', 
                    (core.modules.basic_modules.String, 'string6'))

  reg.add_module(SCIRun_ShowString)
  reg.add_input_port(SCIRun_ShowString, 'bbox',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowString, 'size',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowString, 'location_x',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowString, 'location_y',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowString, 'color_r',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowString, 'color_g',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowString, 'color_b',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowString, 'Format String',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_output_port(SCIRun_ShowString, 'Title', 
                    (SCIRun_Geometry, 'Title'))

  reg.add_module(SCIRun_ReportStringInfo)
  reg.add_input_port(SCIRun_ReportStringInfo, 'inputstring',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ReportStringInfo, 'Input',
                   (core.modules.basic_modules.String, 'tip'))

  reg.add_module(SCIRun_SortMatrix)
  reg.add_input_port(SCIRun_SortMatrix, 'row_or_col',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_SortMatrix, 'Matrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_SortMatrix, 'Matrix', 
                    (SCIRun_Matrix, 'Matrix'))

  reg.add_module(SCIRun_SwapNodeLocationsWithMatrixEntries)
  reg.add_input_port(SCIRun_SwapNodeLocationsWithMatrixEntries, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_SwapNodeLocationsWithMatrixEntries, 'Input Matrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_SwapNodeLocationsWithMatrixEntries, 'Output Field', 
                    (SCIRun_Field, 'Output Field'))
  reg.add_output_port(SCIRun_SwapNodeLocationsWithMatrixEntries, 'Output Matrix', 
                    (SCIRun_Matrix, 'Output Matrix'))

  reg.add_module(SCIRun_ReorderMatrixByReverseCuthillMcKee)
  reg.add_input_port(SCIRun_ReorderMatrixByReverseCuthillMcKee, 'Matrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_ReorderMatrixByReverseCuthillMcKee, 'Matrix', 
                    (SCIRun_Matrix, 'Matrix'))
  reg.add_output_port(SCIRun_ReorderMatrixByReverseCuthillMcKee, 'Mapping', 
                    (SCIRun_Matrix, 'Mapping'))
  reg.add_output_port(SCIRun_ReorderMatrixByReverseCuthillMcKee, 'InverseMapping', 
                    (SCIRun_Matrix, 'InverseMapping'))

  reg.add_module(SCIRun_GetDomainBoundary)
  reg.add_input_port(SCIRun_GetDomainBoundary, 'userange',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GetDomainBoundary, 'minrange',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GetDomainBoundary, 'maxrange',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GetDomainBoundary, 'usevalue',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GetDomainBoundary, 'value',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GetDomainBoundary, 'includeouterboundary',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GetDomainBoundary, 'innerboundaryonly',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GetDomainBoundary, 'noinnerboundary',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GetDomainBoundary, 'disconnect',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GetDomainBoundary, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_GetDomainBoundary, 'MinValueValue',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(SCIRun_GetDomainBoundary, 'MaxValue',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_GetDomainBoundary, 'Field', 
                    (SCIRun_Field, 'Field'))

  reg.add_module(SCIRun_CollectFields)
  reg.add_input_port(SCIRun_CollectFields, 'buffersize',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CollectFields, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_CollectFields, 'BufferSize',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_CollectFields, 'Fields', 
                    (SCIRun_Field, 'Fields'))

  reg.add_module(SCIRun_ScaleFieldMeshAndData)
  reg.add_input_port(SCIRun_ScaleFieldMeshAndData, 'datascale',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ScaleFieldMeshAndData, 'geomscale',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ScaleFieldMeshAndData, 'usegeomcenter',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ScaleFieldMeshAndData, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_ScaleFieldMeshAndData, 'GeomScaleFactor',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(SCIRun_ScaleFieldMeshAndData, 'DataScaleFactor',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_ScaleFieldMeshAndData, 'Field', 
                    (SCIRun_Field, 'Field'))

  reg.add_module(SCIRun_StreamMatrixFromDisk)
  reg.add_input_port(SCIRun_StreamMatrixFromDisk, 'row_or_col',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_StreamMatrixFromDisk, 'slider_min',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_StreamMatrixFromDisk, 'slider_max',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_StreamMatrixFromDisk, 'range_min',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_StreamMatrixFromDisk, 'range_max',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_StreamMatrixFromDisk, 'playmode',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_StreamMatrixFromDisk, 'current',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_StreamMatrixFromDisk, 'execmode',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_StreamMatrixFromDisk, 'delay',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_StreamMatrixFromDisk, 'inc_amount',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_StreamMatrixFromDisk, 'send_amount',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_StreamMatrixFromDisk, 'Indices',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(SCIRun_StreamMatrixFromDisk, 'Weights',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(SCIRun_StreamMatrixFromDisk, 'Filename',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_output_port(SCIRun_StreamMatrixFromDisk, 'DataVector', 
                    (SCIRun_Matrix, 'DataVector'))
  reg.add_output_port(SCIRun_StreamMatrixFromDisk, 'Index', 
                    (SCIRun_Matrix, 'Index'))
  reg.add_output_port(SCIRun_StreamMatrixFromDisk, 'Scaled Index', 
                    (SCIRun_Matrix, 'Scaled Index'))
  reg.add_output_port(SCIRun_StreamMatrixFromDisk, 'Filename', 
                    (core.modules.basic_modules.String, 'Filename'))

  reg.add_module(SCIRun_WriteMatrix)
  reg.add_input_port(SCIRun_WriteMatrix, 'filetype',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_WriteMatrix, 'confirm',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_WriteMatrix, 'confirm_once',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_WriteMatrix, 'exporttype',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_WriteMatrix, 'split',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_WriteMatrix, 'Input Data',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(SCIRun_WriteMatrix, 'Filename',
                   (core.modules.basic_modules.String, 'tip'))

  reg.add_module(SCIRun_ConvertFieldDataType)
  reg.add_input_port(SCIRun_ConvertFieldDataType, 'outputdatatype',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ConvertFieldDataType, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_ConvertFieldDataType, 'Output Field', 
                    (SCIRun_Field, 'Output Field'))

  reg.add_module(SCIRun_GetSliceFromStructuredFieldByIndices)
  reg.add_input_port(SCIRun_GetSliceFromStructuredFieldByIndices, 'axis',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GetSliceFromStructuredFieldByIndices, 'dims',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GetSliceFromStructuredFieldByIndices, 'dim_i',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GetSliceFromStructuredFieldByIndices, 'dim_j',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GetSliceFromStructuredFieldByIndices, 'dim_k',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GetSliceFromStructuredFieldByIndices, 'index_i',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GetSliceFromStructuredFieldByIndices, 'index_j',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GetSliceFromStructuredFieldByIndices, 'index_k',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GetSliceFromStructuredFieldByIndices, 'update_type',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GetSliceFromStructuredFieldByIndices, 'continuous',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GetSliceFromStructuredFieldByIndices, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_GetSliceFromStructuredFieldByIndices, 'Input Matrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_GetSliceFromStructuredFieldByIndices, 'Output Field', 
                    (SCIRun_Field, 'Output Field'))
  reg.add_output_port(SCIRun_GetSliceFromStructuredFieldByIndices, 'Output Matrix', 
                    (SCIRun_Matrix, 'Output Matrix'))

  reg.add_module(SCIRun_GeneratePointSamplesFromField)
  reg.add_input_port(SCIRun_GeneratePointSamplesFromField, 'num_seeds',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GeneratePointSamplesFromField, 'probe_scale',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GeneratePointSamplesFromField, 'send',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GeneratePointSamplesFromField, 'widget',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GeneratePointSamplesFromField, 'red',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GeneratePointSamplesFromField, 'green',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GeneratePointSamplesFromField, 'blue',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GeneratePointSamplesFromField, 'auto_execute',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GeneratePointSamplesFromField, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_GeneratePointSamplesFromField, 'GeneratePointSamplesFromField Widget', 
                    (SCIRun_Geometry, 'GeneratePointSamplesFromField Widget'))
  reg.add_output_port(SCIRun_GeneratePointSamplesFromField, 'GeneratePointSamplesFromField Point', 
                    (SCIRun_Field, 'GeneratePointSamplesFromField Point'))

  reg.add_module(SCIRun_CreateMatrix)
  reg.add_input_port(SCIRun_CreateMatrix, 'rows',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateMatrix, 'cols',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateMatrix, 'data',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateMatrix, 'clabel',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateMatrix, 'rlabel',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_output_port(SCIRun_CreateMatrix, 'matrix', 
                    (SCIRun_Matrix, 'matrix'))

  reg.add_module(SCIRun_DecimateTriSurf)
  reg.add_input_port(SCIRun_DecimateTriSurf, 'TriSurf',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_DecimateTriSurf, 'Decimated', 
                    (SCIRun_Field, 'Decimated'))

  reg.add_module(SCIRun_GeneratePointSamplesFromFieldOrWidget)
  reg.add_input_port(SCIRun_GeneratePointSamplesFromFieldOrWidget, 'wtype',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GeneratePointSamplesFromFieldOrWidget, 'endpoints',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GeneratePointSamplesFromFieldOrWidget, 'maxseeds',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GeneratePointSamplesFromFieldOrWidget, 'numseeds',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GeneratePointSamplesFromFieldOrWidget, 'rngseed',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GeneratePointSamplesFromFieldOrWidget, 'rnginc',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GeneratePointSamplesFromFieldOrWidget, 'clamp',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GeneratePointSamplesFromFieldOrWidget, 'autoexecute',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_GeneratePointSamplesFromFieldOrWidget, 'dist',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GeneratePointSamplesFromFieldOrWidget, 'whichtab',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_GeneratePointSamplesFromFieldOrWidget, 'Field to Sample',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_GeneratePointSamplesFromFieldOrWidget, 'Samples', 
                    (SCIRun_Field, 'Samples'))
  reg.add_output_port(SCIRun_GeneratePointSamplesFromFieldOrWidget, 'Sampling Widget', 
                    (SCIRun_Geometry, 'Sampling Widget'))

  reg.add_module(SCIRun_CalculateIsInsideField)
  reg.add_input_port(SCIRun_CalculateIsInsideField, 'outputbasis',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_CalculateIsInsideField, 'outputtype',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_CalculateIsInsideField, 'outval',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CalculateIsInsideField, 'inval',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CalculateIsInsideField, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_CalculateIsInsideField, 'ObjectField',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_CalculateIsInsideField, 'Field', 
                    (SCIRun_Field, 'Field'))

  reg.add_module(SCIRun_CreateAndEditColorMap)
  reg.add_input_port(SCIRun_CreateAndEditColorMap, 'rgbhsv',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateAndEditColorMap, 'rgb_points',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_CreateAndEditColorMap, 'alpha_points',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_CreateAndEditColorMap, 'resolution',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateAndEditColorMap, 'ColorMap',
                   (SCIRun_ColorMap, "SCIRun_ColorMap"))
  reg.add_output_port(SCIRun_CreateAndEditColorMap, 'ColorMap', 
                    (SCIRun_ColorMap, 'ColorMap'))
  reg.add_output_port(SCIRun_CreateAndEditColorMap, 'Geometry', 
                    (SCIRun_Geometry, 'Geometry'))

  reg.add_module(SCIRun_CoregisterPointClouds)
  reg.add_input_port(SCIRun_CoregisterPointClouds, 'allowScale',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CoregisterPointClouds, 'allowRotate',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CoregisterPointClouds, 'allowTranslate',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CoregisterPointClouds, 'seed',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CoregisterPointClouds, 'iters',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CoregisterPointClouds, 'misfitTol',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CoregisterPointClouds, 'method',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_CoregisterPointClouds, 'Fixed PointCloudField',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_CoregisterPointClouds, 'Mobile PointCloudField',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_CoregisterPointClouds, 'DistanceField From Fixed',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_CoregisterPointClouds, 'Transform', 
                    (SCIRun_Matrix, 'Transform'))

  reg.add_module(SCIRun_SolveMinNormLeastSqSystem)
  reg.add_input_port(SCIRun_SolveMinNormLeastSqSystem, 'BasisVec1',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(SCIRun_SolveMinNormLeastSqSystem, 'BasisVec2',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(SCIRun_SolveMinNormLeastSqSystem, 'BasisVec3',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(SCIRun_SolveMinNormLeastSqSystem, 'TargetVec',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_SolveMinNormLeastSqSystem, 'WeightVec(Col)', 
                    (SCIRun_Matrix, 'WeightVec(Col)'))
  reg.add_output_port(SCIRun_SolveMinNormLeastSqSystem, 'ResultVec(Col)', 
                    (SCIRun_Matrix, 'ResultVec(Col)'))

  reg.add_module(SCIRun_CalculateFieldData)
  reg.add_input_port(SCIRun_CalculateFieldData, 'function',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_CalculateFieldData, 'format',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_CalculateFieldData, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_CalculateFieldData, 'Function',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_input_port(SCIRun_CalculateFieldData, 'Array',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_CalculateFieldData, 'Field', 
                    (SCIRun_Field, 'Field'))

  reg.add_module(SCIRun_MapFieldDataToNodeCoordinate)
  reg.add_input_port(SCIRun_MapFieldDataToNodeCoordinate, 'coord',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_MapFieldDataToNodeCoordinate, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_MapFieldDataToNodeCoordinate, 'Output Field', 
                    (SCIRun_Field, 'Output Field'))

  reg.add_module(SCIRun_ShowMeshBoundingBox)
  reg.add_input_port(SCIRun_ShowMeshBoundingBox, 'sizex',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowMeshBoundingBox, 'sizey',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowMeshBoundingBox, 'sizez',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowMeshBoundingBox, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_ShowMeshBoundingBox, 'Scene Graph', 
                    (SCIRun_Geometry, 'Scene Graph'))

  reg.add_module(SCIRun_ViewGraph)
  reg.add_input_port(SCIRun_ViewGraph, 'Title',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_input_port(SCIRun_ViewGraph, 'Input',
                   (SCIRun_Matrix, "SCIRun_Matrix"))

  reg.add_module(SCIRun_GetAllSegmentationBoundaries)
  reg.add_input_port(SCIRun_GetAllSegmentationBoundaries, 'Segmentations',
                   (SCIRun_Nrrd, "SCIRun_Nrrd"))
  reg.add_output_port(SCIRun_GetAllSegmentationBoundaries, 'Boundaries', 
                    (SCIRun_Field, 'Boundaries'))

  reg.add_module(SCIRun_CreateStandardColorMaps)
  reg.add_input_port(SCIRun_CreateStandardColorMaps, 'mapName',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_CreateStandardColorMaps, 'gamma',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateStandardColorMaps, 'resolution',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateStandardColorMaps, 'reverse',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateStandardColorMaps, 'faux',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateStandardColorMaps, 'positionList',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_CreateStandardColorMaps, 'nodeList',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_CreateStandardColorMaps, 'width',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateStandardColorMaps, 'height',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_output_port(SCIRun_CreateStandardColorMaps, 'ColorMap', 
                    (SCIRun_ColorMap, 'ColorMap'))

  reg.add_module(SCIRun_ShowTextureSlices)
  reg.add_input_port(SCIRun_ShowTextureSlices, 'control_pos_saved',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowTextureSlices, 'drawX',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowTextureSlices, 'drawY',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowTextureSlices, 'drawZ',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowTextureSlices, 'drawView',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowTextureSlices, 'interp_mode',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowTextureSlices, 'draw_phi_0',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowTextureSlices, 'draw_phi_1',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowTextureSlices, 'phi_0',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowTextureSlices, 'phi_1',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowTextureSlices, 'multi_level',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowTextureSlices, 'color_changed',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowTextureSlices, 'colors',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ShowTextureSlices, 'level_on',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ShowTextureSlices, 'outline_levels',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowTextureSlices, 'use_stencil',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowTextureSlices, 'Texture',
                   (SCIRun_Texture, "SCIRun_Texture"))
  reg.add_input_port(SCIRun_ShowTextureSlices, 'ColorMap',
                   (SCIRun_ColorMap, "SCIRun_ColorMap"))
  reg.add_input_port(SCIRun_ShowTextureSlices, 'ColorMap2',
                   (SCIRun_ColorMap2, "SCIRun_ColorMap2"))
  reg.add_output_port(SCIRun_ShowTextureSlices, 'Geometry', 
                    (SCIRun_Geometry, 'Geometry'))
  reg.add_output_port(SCIRun_ShowTextureSlices, 'ColorMap', 
                    (SCIRun_ColorMap, 'ColorMap'))

  reg.add_module(SCIRun_ShowMatrix)
  reg.add_input_port(SCIRun_ShowMatrix, 'xpos',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowMatrix, 'ypos',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowMatrix, 'xscale',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowMatrix, 'yscale',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowMatrix, 'a3d_mode',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowMatrix, 'gmode',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowMatrix, 'showtext',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowMatrix, 'row_begin',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowMatrix, 'rows',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowMatrix, 'col_begin',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowMatrix, 'cols',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowMatrix, 'colormapmode',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_ShowMatrix, 'ColorMap',
                   (SCIRun_ColorMap, "SCIRun_ColorMap"))
  reg.add_input_port(SCIRun_ShowMatrix, 'Matrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_ShowMatrix, 'Geometry', 
                    (SCIRun_Geometry, 'Geometry'))

  reg.add_module(SCIRun_CreateViewerClockIcon)
  reg.add_input_port(SCIRun_CreateViewerClockIcon, 'type',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerClockIcon, 'bbox',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerClockIcon, 'format',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerClockIcon, 'min',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerClockIcon, 'max',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerClockIcon, 'current',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerClockIcon, 'size',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerClockIcon, 'location_x',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerClockIcon, 'location_y',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerClockIcon, 'color_r',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerClockIcon, 'color_g',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerClockIcon, 'color_b',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CreateViewerClockIcon, 'Time Matrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_input_port(SCIRun_CreateViewerClockIcon, 'Time Nrrd',
                   (SCIRun_Nrrd, "SCIRun_Nrrd"))
  reg.add_output_port(SCIRun_CreateViewerClockIcon, 'Clock', 
                    (SCIRun_Geometry, 'Clock'))

  reg.add_module(SCIRun_ConvertMatrixType)
  reg.add_input_port(SCIRun_ConvertMatrixType, 'oldtype',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ConvertMatrixType, 'newtype',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ConvertMatrixType, 'nrow',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ConvertMatrixType, 'ncol',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ConvertMatrixType, 'Input',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_ConvertMatrixType, 'Output', 
                    (SCIRun_Matrix, 'Output'))

  reg.add_module(SCIRun_JoinStrings)
  reg.add_input_port(SCIRun_JoinStrings, 'input',
                   (core.modules.basic_modules.String, 'tip'))
  reg.add_output_port(SCIRun_JoinStrings, 'Output', 
                    (core.modules.basic_modules.String, 'Output'))

  reg.add_module(SCIRun_InsertColorMapsIntoBundle)
  reg.add_input_port(SCIRun_InsertColorMapsIntoBundle, 'colormap1_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertColorMapsIntoBundle, 'colormap2_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertColorMapsIntoBundle, 'colormap3_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertColorMapsIntoBundle, 'colormap4_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertColorMapsIntoBundle, 'colormap5_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertColorMapsIntoBundle, 'colormap6_name',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertColorMapsIntoBundle, 'replace1',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_InsertColorMapsIntoBundle, 'replace2',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_InsertColorMapsIntoBundle, 'replace3',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_InsertColorMapsIntoBundle, 'replace4',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_InsertColorMapsIntoBundle, 'replace5',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_InsertColorMapsIntoBundle, 'replace6',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_InsertColorMapsIntoBundle, 'bundlename',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_InsertColorMapsIntoBundle, 'bundle',
                   (SCIRun_Bundle, "SCIRun_Bundle"))
  reg.add_input_port(SCIRun_InsertColorMapsIntoBundle, 'colormap1',
                   (SCIRun_ColorMap, "SCIRun_ColorMap"))
  reg.add_input_port(SCIRun_InsertColorMapsIntoBundle, 'colormap2',
                   (SCIRun_ColorMap, "SCIRun_ColorMap"))
  reg.add_input_port(SCIRun_InsertColorMapsIntoBundle, 'colormap3',
                   (SCIRun_ColorMap, "SCIRun_ColorMap"))
  reg.add_input_port(SCIRun_InsertColorMapsIntoBundle, 'colormap4',
                   (SCIRun_ColorMap, "SCIRun_ColorMap"))
  reg.add_input_port(SCIRun_InsertColorMapsIntoBundle, 'colormap5',
                   (SCIRun_ColorMap, "SCIRun_ColorMap"))
  reg.add_input_port(SCIRun_InsertColorMapsIntoBundle, 'colormap6',
                   (SCIRun_ColorMap, "SCIRun_ColorMap"))
  reg.add_output_port(SCIRun_InsertColorMapsIntoBundle, 'bundle', 
                    (SCIRun_Bundle, 'bundle'))

  reg.add_module(SCIRun_CollectPointClouds)
  reg.add_input_port(SCIRun_CollectPointClouds, 'num_fields',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_CollectPointClouds, 'Point Cloud',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_CollectPointClouds, 'Curve', 
                    (SCIRun_Field, 'Curve'))

  reg.add_module(SCIRun_ReorderMatrixByCuthillMcKee)
  reg.add_input_port(SCIRun_ReorderMatrixByCuthillMcKee, 'Matrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_ReorderMatrixByCuthillMcKee, 'Matrix', 
                    (SCIRun_Matrix, 'Matrix'))
  reg.add_output_port(SCIRun_ReorderMatrixByCuthillMcKee, 'Mapping', 
                    (SCIRun_Matrix, 'Mapping'))
  reg.add_output_port(SCIRun_ReorderMatrixByCuthillMcKee, 'InverseMapping', 
                    (SCIRun_Matrix, 'InverseMapping'))

  reg.add_module(SCIRun_ReportMatrixRowMeasure)
  reg.add_input_port(SCIRun_ReportMatrixRowMeasure, 'method',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_ReportMatrixRowMeasure, 'Matrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_ReportMatrixRowMeasure, 'Vector', 
                    (SCIRun_Matrix, 'Vector'))

  reg.add_module(SCIRun_RemoveHexVolSheet)
  reg.add_input_port(SCIRun_RemoveHexVolSheet, 'edge_list',
                   (core.modules.basic_modules.String, 'tip'), True)
  reg.add_input_port(SCIRun_RemoveHexVolSheet, 'HexField',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_RemoveHexVolSheet, 'NewHexField', 
                    (SCIRun_Field, 'NewHexField'))
  reg.add_output_port(SCIRun_RemoveHexVolSheet, 'ExtractedHexes', 
                    (SCIRun_Field, 'ExtractedHexes'))

  reg.add_module(SCIRun_ColorMap2DSemantics)
  reg.add_input_port(SCIRun_ColorMap2DSemantics, 'Input Colormap',
                   (SCIRun_ColorMap2, "SCIRun_ColorMap2"))
  reg.add_output_port(SCIRun_ColorMap2DSemantics, 'Output Colormap', 
                    (SCIRun_ColorMap2, 'Output Colormap'))

  reg.add_module(SCIRun_ReportMatrixInfo)
  reg.add_input_port(SCIRun_ReportMatrixInfo, 'Input',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_ReportMatrixInfo, 'NumRows', 
                    (SCIRun_Matrix, 'NumRows'))
  reg.add_output_port(SCIRun_ReportMatrixInfo, 'NumCols', 
                    (SCIRun_Matrix, 'NumCols'))
  reg.add_output_port(SCIRun_ReportMatrixInfo, 'NumElements', 
                    (SCIRun_Matrix, 'NumElements'))

  reg.add_module(SCIRun_RefineMesh)
  reg.add_input_port(SCIRun_RefineMesh, 'Mesh',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_RefineMesh, 'Isovalue',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_RefineMesh, 'RefinedMesh', 
                    (SCIRun_Field, 'RefinedMesh'))
  reg.add_output_port(SCIRun_RefineMesh, 'Mapping', 
                    (SCIRun_Matrix, 'Mapping'))

  reg.add_module(SCIRun_InsertEnvironmentIntoBundle)
  reg.add_output_port(SCIRun_InsertEnvironmentIntoBundle, 'Environment', 
                    (SCIRun_Bundle, 'Environment'))

  reg.add_module(SCIRun_CalculateDistanceToField)
  reg.add_input_port(SCIRun_CalculateDistanceToField, 'Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_CalculateDistanceToField, 'ObjectField',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_output_port(SCIRun_CalculateDistanceToField, 'DistanceField', 
                    (SCIRun_Field, 'DistanceField'))

  reg.add_module(SCIRun_SubsampleStructuredFieldByIndices)
  reg.add_input_port(SCIRun_SubsampleStructuredFieldByIndices, 'power_app',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_SubsampleStructuredFieldByIndices, 'wrap',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_SubsampleStructuredFieldByIndices, 'dims',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_SubsampleStructuredFieldByIndices, 'dim_i',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_SubsampleStructuredFieldByIndices, 'dim_j',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_SubsampleStructuredFieldByIndices, 'dim_k',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_SubsampleStructuredFieldByIndices, 'start_i',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_SubsampleStructuredFieldByIndices, 'start_j',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_SubsampleStructuredFieldByIndices, 'start_k',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_SubsampleStructuredFieldByIndices, 'stop_i',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_SubsampleStructuredFieldByIndices, 'stop_j',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_SubsampleStructuredFieldByIndices, 'stop_k',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_SubsampleStructuredFieldByIndices, 'stride_i',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_SubsampleStructuredFieldByIndices, 'stride_j',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_SubsampleStructuredFieldByIndices, 'stride_k',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_SubsampleStructuredFieldByIndices, 'wrap_i',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_SubsampleStructuredFieldByIndices, 'wrap_j',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_SubsampleStructuredFieldByIndices, 'wrap_k',
                   (core.modules.basic_modules.Float, 'tip'), True)
  reg.add_input_port(SCIRun_SubsampleStructuredFieldByIndices, 'Input Field',
                   (SCIRun_Field, "SCIRun_Field"))
  reg.add_input_port(SCIRun_SubsampleStructuredFieldByIndices, 'Input Matrix',
                   (SCIRun_Matrix, "SCIRun_Matrix"))
  reg.add_output_port(SCIRun_SubsampleStructuredFieldByIndices, 'Output Field', 
                    (SCIRun_Field, 'Output Field'))
  reg.add_output_port(SCIRun_SubsampleStructuredFieldByIndices, 'Output Matrix', 
                    (SCIRun_Matrix, 'Output Matrix'))

def package_dependencies():
  return ['edu.utah.sci.vistrails.spreadsheet']

def finalize():
  sr_py.terminate()
  time.sleep(.5)
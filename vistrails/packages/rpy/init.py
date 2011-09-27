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
import os
import sys
import tempfile
import urllib

# FIXME when rpy2 is installed on the path, we won't need this
old_sys_path = sys.path
sys.path.append(os.path.dirname(__file__))
import rpy2.robjects as robjects
sys.path = old_sys_path

from core.modules.basic_modules import File, Constant, \
    new_constant, list_compute
    # new_constant as _new_constant

from core.modules.vistrails_module import Module, ModuleError, \
    ModuleConnector, NotCacheable
from core.modules.basic_modules import new_constant
import core.modules.module_registry
from widgets import RSourceConfigurationWidget, RFigureConfigurationWidget

r_temp_files = []

# # bckward compatibility
# from core.modules.constant_configuration import StandardConstantWidget

# def new_constant(name, py_conversion, default_value, validation,
#                  widget_type=StandardConstantWidget, str_conversion=None,
#                  base_class=Constant, compute=None):
#     m = _new_constant(name, py_conversion, default_value, validation,
#                       widget_type)
#     m.__bases__  = (base_class,)
#     m.translate_to_string = str_conversion
#     m.compute = compute
#     m._input_ports = []
#     m._output_ports = []
#     return m

class TypeException(Exception):
    pass

def create_vector(v_list, desired_type=None):
    is_bool = True
    is_int = True
    is_float = True
    is_str = True
    for elt in v_list:
        if type(elt) == str:
            is_bool = False
            is_int = False
            is_float = False
        elif type(elt) == float:
            is_bool = False
            is_int = False
        elif type(elt) == int:
            is_bool = False
        else:
            is_bool = False
            is_int = False
            is_float = False
            is_str = False
            break
 
    if is_bool and (desired_type is None or desired_type == bool):
        return robjects.BoolVector(v_list)
    elif is_int and (desired_type is None or desired_type == int):
        res = [int(elt) for elt in v_list]
        return robjects.IntVector(res)
    elif is_float and (desired_type is None or desired_type == float):
        res = [float(elt) for elt in v_list]
        return robjects.FloatVector(res)
    elif is_str and (desired_type is None or desired_type == str):
        res = [str(elt) for elt in v_list]
        return robjects.StrVector(res)
    
    if desired_type is not None:
        raise TypeException("Cannot coerce vector to type '%s'" % desired_type)
    return robjects.RVector(v_list)

def vector_conv(v, desired_type=None):
    v_list = eval(v)
    return create_vector(v_list, desired_type)

RVector = new_constant('RVector', staticmethod(vector_conv),
                       robjects.RVector([]),
                       staticmethod(lambda x: isinstance(x, robjects.RVector)))

def bool_vector_conv(v):
    return vector_conv(v, bool)

RBoolVector = new_constant('RBoolVector' , staticmethod(bool_vector_conv), 
                            robjects.BoolVector([]),
                            staticmethod(lambda x: isinstance(x, robjects.RVector)),
                            base_class=RVector)
                       
def int_vector_conv(v):
    return vector_conv(v, int)

RIntVector = new_constant('RIntVector' , staticmethod(int_vector_conv), 
                            robjects.IntVector([]),
                            staticmethod(lambda x: isinstance(x, robjects.RVector)),
                            base_class=RVector)

def float_vector_conv(v):
    return vector_conv(v, float)

RFloatVector = new_constant('RFloatVector' , staticmethod(float_vector_conv), 
                            robjects.FloatVector([]),
                            staticmethod(lambda x: isinstance(x, robjects.RVector)),
                            base_class=RVector)
                       
def str_vector_conv(v):
    return vector_conv(v, str)

RStrVector = new_constant('RStrVector' , staticmethod(str_vector_conv), 
                            robjects.StrVector([]),
                            staticmethod(lambda x: isinstance(x, robjects.RVector)),
                            base_class=RVector)

def array_conv(v):
    return robjects.r.array(vector_conv(v))

RArray = new_constant('RArray', staticmethod(array_conv),
                      robjects.r.array(),
                      staticmethod(lambda x: isinstance(x, robjects.RArray)),
                      base_class=RVector)

def create_matrix(v_list):
    vec_list = []
    nrow = 0
    ncol = -1
    for v_sublist in v_list:
        if ncol == -1:
            ncol = len(v_sublist)
        elif ncol != len(v_sublist):
            raise TypeException("Matrix must be rectangular")
        nrow += 1
        vec_list.extend(v_sublist)
    vec = create_vector(vec_list)
    return robjects.r.matrix(vec, nrow=nrow)
    
def matrix_conv(v):
    # should be a double list
    v_list = eval(v)
    create_matrix(v_list)

def matrix_compute(self):
    if self.hasInputFromPort('rvector'):
        rvector = self.getInputFromPort('rvector')
        nrows = self.getInputFromPort('nrows')
        self.setResult('value', robjects.r.matrix(rvector, nrow=nrows))
    else:
        RArray.compute(self)

RMatrix = new_constant('RMatrix', staticmethod(matrix_conv),
                       robjects.r.matrix(),
                       staticmethod(lambda x: isinstance(x, robjects.RArray)),
                       base_class=RArray,
                       compute=matrix_compute)
RMatrix._input_ports.extend([('rvector', 
                              '(edu.utah.sci.vistrails.rpy:RVector:Types)'), 
                             ('nrows', 
                              '(edu.utah.sci.vistrails.basic:Integer)')])

def create_list(v_dict):
    data_dict = {}
    for k,v in v_dict.iteritems():
        if type(v) == list:
            data_dict[k] = create_vector(v)
        elif type(v) == dict:
            data_dict[k] = create_list(v)
        else:
            data_dict[k] = v
    return robjects.r['list'](**data_dict)

def list_conv(v):
    v_dict = eval(v)
    return create_list(v_dict)

RList = new_constant('RList', staticmethod(list_conv),
                     robjects.r.list(),
                     staticmethod(lambda x: isinstance(x, robjects.RVector)),
                     base_class=RVector,
                     compute=list_compute)

def create_data_frame(v_dict):
    data_dict = {}
    for k,v in v_dict.iteritems():
        if type(v) == list:
            data_dict[k] = create_vector(v)
        elif type(v) == dict:
            data_dict[k] = create_data_frame(v)
        else:
            data_dict[k] = v
    return robjects.r['data.frame'](**data_dict)

def data_frame_conv(v):
    v_dict = eval(v)
    return create_data_frame(v_dict)

RDataFrame = new_constant('RDataFrame', staticmethod(data_frame_conv),
                          robjects.r['data.frame'](),
                          staticmethod(lambda x: \
                                           isinstance(x, robjects.RDataFrame)))
                          
class RVectorFromList(Module):
    _input_ports = [('list', '(edu.utah.sci.vistrails.basic:List)')]
    _output_ports = [('rvector', '(edu.utah.sci.vistrails.rpy:RVector:Types)')]

    def compute(self):
        ilist = self.getInputFromPort('list')
        rvector = create_vector(ilist)
        self.setResult('rvector', rvector)

class ListFromRVector(Module):
    _input_ports = [('rvector', '(edu.utah.sci.vistrails.rpy:RVector:Types)')]
    _output_ports = [('list', '(edu.utah.sci.vistrails.basic:List)')]

    def compute(self):
        rvector = self.getInputFromPort('rvector')
        olist = list(rvector)
        self.setResult('list', olist)

class RMatrixFromNestedList(Module):
    _input_ports = [('list', '(edu.utah.sci.vistrails.basic:List)')]
    _output_ports = [('rmatrix', '(edu.utah.sci.vistrails.rpy:RMatrix:Types)')]

    def compute(self):
        ilist = self.getInputFromPort('list')
        rmatrix = create_matrix(ilist)
        self.setResult('rmatrix', rmatrix)

class NestedListFromRMatrix(Module):
    _input_ports = [('rmatrix', '(edu.utah.sci.vistrails.rpy:RMatrix:Types)')]
    _output_ports = [('list', '(edu.utah.sci.vistrails.basic:List)')]
    
    def compute(self):
        rmatrix = self.getInputFromPort('rmatrix')
        mlist = list(rmatrix)
        nrows = rmatrix.nrow
        ncols = len(mlist) / nrows
        olist = [] 
        for row in xrange(nrows):
            olist.append(mlist[row*ncols:(row+1)*ncols])
        self.setResult('list', olist)

class RDataFrameFromDict(Module):
    _input_ports = [('dict', '(edu.utah.sci.vistrails.basic:Dictionary)')]
    _output_ports = [('rdataframe', 
                      '(edu.utah.sci.vistrails.rpy:RDataFrame:Types)')]
    
    def compute(self):
        idict = self.getInputFromPort('dict')
        rdataframe = create_data_frame(idict)
        self.setResult('rdataframe', rdataframe)

class DictFromRDataFrame(Module):
    _input_ports = [('rdataframe', 
                     '(edu.utah.sci.vistrails.rpy:RDataFrame:Types)')]
    _output_ports = [('dict', '(edu.utah.sci.vistrails.basic:Dictionary)')]

    def compute(self):
        rdataframe = self.getInputFromPort('rdataframe')
        colnames = list(rdataframe.colnames())
        odict = {}
        for i in xrange(len(rdataframe)):
            # FIXME !!! just assume that each row can be converted to a list!!!
            odict[colnames[i]] = list(rdataframe[i])
        self.setResult('dict', odict)

class RListFromDict(Module):
    # _input_ports = [('dict', '(edu.utah.sci.vistrails.basic:Dictionary)')]
    _input_ports = [('dict', '(edu.utah.sci.vistrails.basic:Module)')]
    _output_ports = [('rlist', '(edu.utah.sci.vistrails.rpy:RList:Types)')]
    
    def compute(self):
        idict = self.getInputFromPort('dict')
        rlist = create_list(idict)
        self.setResult('rlist', rlist)

class DictFromRList(Module):
    _input_ports = [('rlist', '(edu.utah.sci.vistrails.rpy:RList:Types)')]
    # _output_ports = [('dict', '(edu.utah.sci.vistrails.basic:Dictionary)')]
    _output_ports = [('dict', '(edu.utah.sci.vistrails.basic:Module)')]

    def compute(self):
        rlist = self.getInputFromPort('rlist')
        colnames = list(rlist.names)
        odict = {}
        for i in xrange(len(rlist)):
            # FIXME !!! just assume that each row can be converted to a list!!!
            # FIXME this may need to be a list of lists
            odict[colnames[i]] = list(rlist[i])
        self.setResult('dict', odict)

class RRead(Module):
    _input_ports = [('file', '(edu.utah.sci.vistrails.basic:File)'),
                    ('header', '(edu.utah.sci.vistrails.basic:Boolean)', True),
                    ('sep', '(edu.utah.sci.vistrails.basic:String)', True),
                    ('commentChar', 
                     '(edu.utah.sci.vistrails.basic:String)', True),
                    ('quote', '(edu.utah.sci.vistrails.basic:String)', True),
                    ('dec', '(edu.utah.sci.vistrails.basic:String)', True),
                    ('fill', '(edu.utah.sci.vistrails.basic:Boolean)', True)]
    _output_ports = [('rdataframe',
                      '(edu.utah.sci.vistrails.rpy:RDataFrame:Types)')]

    def do_read(self, read_cmd):
        fname = self.getInputFromPort('file').name
        options_dict = {}
        for port in RRead._input_ports:
            if port[0] != 'file' and self.hasInputFromPort(port):
                options_dict[port] = self.getInputFromPort(port)
        rdataframe = robjects.r[read_cmd](fname, **options_dict)
        self.setResult('rdataframe', rdataframe)

class RReadTable(RRead):
    def compute(self):
        self.do_read('read.table')

class RReadCSV(RRead):
    def compute(self):
        self.do_read('read.csv')

class RReadCSV2(RRead):
    def compute(self):
        self.do_read('read.csv2')
    
class RReadDelim(RRead):
    def compute(self):
        self.do_read('read.delim')

class RReadDelim2(RRead):
    def compute(self):
        self.do_read('read.delim2')

# class RSource(NotCacheable, Module):
class RSource(Module):
    _input_ports = [('source', '(edu.utah.sci.vistrails.basic:String)', True)]
    def run_code(self, code_str,
                 use_input=False,
                 use_output=False,
                 excluded_inputs=set(),
                 excluded_outputs=set()):
        """run_code runs a piece of code as a VisTrails module.
        use_input and use_output control whether to use the inputport
        and output port dictionary as local variables inside the
        execution."""
        import core.packagemanager
        def fail(msg):
            raise ModuleError(self, msg)
        def cache_this():
            self.is_cacheable = lambda *args, **kwargs: True
        if use_input:
            inputDict = dict([(k, self.getInputFromPort(k))
                              for k in self.inputPorts
                              if k not in excluded_inputs])
            for k,v in inputDict.iteritems():
                robjects.globalEnv[k] = v
        robjects.r(code_str)
        if use_output:
            for k in self.outputPorts:
                if k not in excluded_outputs and k in robjects.globalEnv:
                    self.setResult(k, robjects.globalEnv[k])

    def run_file(self, fname, excluded_inputs=set(['source']), 
                 excluded_outputs=set()):
        f = open(fname, 'rU')
        code_str = f.readlines()
        f.close()
        self.run_code(code_str, use_input=True, use_output=True,
                      excluded_inputs=excluded_inputs,
                      excluded_outputs=excluded_outputs)

    def set_variable(self, name, value):
        robjects.globalEnv[name] = value

    def get_variable(self, name):
        # return robjects.globalEnv[name]
        return robjects.r(name)

    def chdir(self, dir):
        robjects.r('setwd("%s")' % dir)

    def compute(self):
        code_str = urllib.unquote(str(self.forceGetInputFromPort('source', '')))
        self.run_code(code_str, use_input=True, use_output=True,
                      excluded_inputs=set(['source']))

class RFigure(RSource):
    _output_ports = [('imageFile', '(edu.utah.sci.vistrails.basic:File)')]
    def run_figure(self, code_str, graphics_dev, width, height, 
                   excluded_inputs=set(['source'])):
        f, fname = tempfile.mkstemp(prefix='vtr', suffix='.' + graphics_dev)
        r_temp_files.append(fname)
        os.close(f)
        robjects.r[graphics_dev](file=fname, width=width, height=height)
        self.run_code(code_str, use_input=True, 
                      excluded_inputs=excluded_inputs)
        robjects.r['dev.off']()
        image_file = File()
        image_file.name = fname
        image_file.upToDate = True
        self.setResult('imageFile', image_file)

    def run_figure_file(self, fname, graphics_dev, width, height, 
                        excluded_inputs=set(['source'])):
        f = open(fname)
        code_str = f.readlines()
        f.close()
        self.run_figure(code_str, graphics_dev, width, height, excluded_inputs)

class RSVGFigure(RFigure):
    def compute(self):
        code_str = \
            urllib.unquote(str(self.forceGetInputFromPort('source', '')))
        RFigure.run_figure(self, code_str, 'svg', 4, 3)

class RPNGFigure(RFigure):
    def compute(self):
        code_str = \
            urllib.unquote(str(self.forceGetInputFromPort('source', '')))
        RFigure.run_figure(self, code_str, 'png', 640, 480)

class RPDFFigure(RFigure):
    def compute(self):
        code_str = \
            urllib.unquote(str(self.forceGetInputFromPort('source', '')))
        RFigure.run_figure(self, code_str, 'pdf', 4, 3)

class RFactor(Module):
    pass

_modules = {None: [(RSource, 
                    {'configureWidgetType': RSourceConfigurationWidget})],
            'Types': [RVector, 
                      RBoolVector,
                      RIntVector,
                      RFloatVector,
                      RStrVector,
                      RArray,
                      RMatrix,
                      RDataFrame,
                      RList,
                      RFactor],
            'Readers': [(RRead, {'abstract': True}),
                         RReadTable,
                         RReadCSV,
                         RReadCSV2,
                         RReadDelim,
                         RReadDelim2],
            'Converters': [RVectorFromList,
                           ListFromRVector,
                           RMatrixFromNestedList,
                           NestedListFromRMatrix,
                           RDataFrameFromDict,
                           DictFromRDataFrame,
                           RListFromDict,
                           DictFromRList],
            'Figures': [(RFigure, {'abstract': True}),
                        (RSVGFigure, {'configureWidgetType': \
                                          RFigureConfigurationWidget}),
                        (RPNGFigure, {'configureWidgetType': \
                                          RFigureConfigurationWidget}),
                        (RPDFFigure, {'configureWidgetType': \
                                          RFigureConfigurationWidget})]
            }

def finalize():
    for file in r_temp_files:
        os.remove(file)

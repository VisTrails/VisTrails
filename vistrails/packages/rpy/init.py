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

from ast import literal_eval
import os
import sys
import urllib
import rpy2.robjects as robjects

from vistrails.core.modules.basic_modules import PathObject, new_constant
from vistrails.core.modules.vistrails_module import Module, ModuleError
from .widgets import RSourceConfigurationWidget, RFigureConfigurationWidget


# FIXME when rpy2 is installed on the path, we won't need this
old_sys_path = sys.path
sys.path.append(os.path.dirname(__file__))
sys.path = old_sys_path

r_temp_files = []

class TypeException(Exception):
    pass

def create_vector(v_list, desired_type=None):
    is_bool = True
    is_int = True
    is_float = True
    is_str = True
    for elt in v_list:
        if isinstance(elt, basestring):
            is_bool = False
            is_int = False
            is_float = False
        elif isinstance(elt, float):
            is_bool = False
            is_int = False
        elif isinstance(elt, (int, long)):
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
    v_list = literal_eval(v)
    return create_vector(v_list, desired_type)

RVector = new_constant('RVector', staticmethod(vector_conv),
                       robjects.Vector([]),
                       staticmethod(lambda x: isinstance(x, robjects.Vector)))

def bool_vector_conv(v):
    return vector_conv(v, bool)

RBoolVector = new_constant('RBoolVector' , staticmethod(bool_vector_conv), 
                            robjects.BoolVector([]),
                            staticmethod(lambda x: isinstance(x, robjects.Vector)),
                            base_class=RVector)
                       
def int_vector_conv(v):
    return vector_conv(v, int)

RIntVector = new_constant('RIntVector' , staticmethod(int_vector_conv), 
                            robjects.IntVector([]),
                            staticmethod(lambda x: isinstance(x, robjects.Vector)),
                            base_class=RVector)

def float_vector_conv(v):
    return vector_conv(v, float)

RFloatVector = new_constant('RFloatVector' , staticmethod(float_vector_conv), 
                            robjects.FloatVector([]),
                            staticmethod(lambda x: isinstance(x, robjects.Vector)),
                            base_class=RVector)
                       
def str_vector_conv(v):
    return vector_conv(v, str)

RStrVector = new_constant('RStrVector' , staticmethod(str_vector_conv), 
                            robjects.StrVector([]),
                            staticmethod(lambda x: isinstance(x, robjects.Vector)),
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
    v_list = literal_eval(v)
    create_matrix(v_list)

def matrix_compute(self):
    if self.has_input('rvector'):
        rvector = self.get_input('rvector')
        nrows = self.get_input('nrows')
        self.set_output('value', robjects.r.matrix(rvector, nrow=nrows))
    else:
        RArray.compute(self)

RMatrix = new_constant('RMatrix', staticmethod(matrix_conv),
                       robjects.r.matrix(),
                       staticmethod(lambda x: isinstance(x, robjects.RArray)),
                       base_class=RArray,
                       compute=matrix_compute)
RMatrix._input_ports.extend([('rvector', '(Types|RVector)'), 
                             ('nrows', '(basic:Integer)')])

def create_list(v_dict):
    data_dict = {}
    for k,v in v_dict.iteritems():
        if isinstance(v, list):
            data_dict[k] = create_vector(v)
        elif isinstance(v, dict):
            data_dict[k] = create_list(v)
        else:
            data_dict[k] = v
    return robjects.r['list'](**data_dict)

def list_conv(v):
    v_dict = literal_eval(v)
    return create_list(v_dict)

RList = new_constant('RList', staticmethod(list_conv),
                     robjects.r.list(),
                     staticmethod(lambda x: isinstance(x, robjects.Vector)),
                     base_class=RVector)
# compute=list_compute)

def create_data_frame(v_dict):
    data_dict = {}
    for k,v in v_dict.iteritems():
        if isinstance(v, list):
            data_dict[k] = create_vector(v)
        elif isinstance(v, dict):
            data_dict[k] = create_data_frame(v)
        else:
            data_dict[k] = v
    return robjects.r['data.frame'](**data_dict)

def data_frame_conv(v):
    v_dict = literal_eval(v)
    return create_data_frame(v_dict)

RDataFrame = new_constant('RDataFrame', staticmethod(data_frame_conv),
                          robjects.r['data.frame'](),
                          staticmethod(lambda x: \
                                           isinstance(x, robjects.RDataFrame)))
                          
class RVectorFromList(Module):
    _input_ports = [('list', '(basic:List)')]
    _output_ports = [('rvector', '(Types|RVector)')]

    def compute(self):
        ilist = self.get_input('list')
        rvector = create_vector(ilist)
        self.set_output('rvector', rvector)

class ListFromRVector(Module):
    _input_ports = [('rvector', '(Types|RVector)')]
    _output_ports = [('list', '(basic:List)')]

    def compute(self):
        rvector = self.get_input('rvector')
        olist = list(rvector)
        self.set_output('list', olist)

class RMatrixFromNestedList(Module):
    _input_ports = [('list', '(basic:List)')]
    _output_ports = [('rmatrix', '(Types|RMatrix)')]

    def compute(self):
        ilist = self.get_input('list')
        rmatrix = create_matrix(ilist)
        self.set_output('rmatrix', rmatrix)

class NestedListFromRMatrix(Module):
    _input_ports = [('rmatrix', '(Types|RMatrix)')]
    _output_ports = [('list', '(basic:List)')]
    
    def compute(self):
        rmatrix = self.get_input('rmatrix')
        mlist = list(rmatrix)
        nrows = rmatrix.nrow
        ncols = len(mlist) // nrows
        olist = [] 
        for row in xrange(nrows):
            olist.append(mlist[row*ncols:(row+1)*ncols])
        self.set_output('list', olist)

class RDataFrameFromDict(Module):
    _input_ports = [('dict', '(basic:Dictionary)')]
    _output_ports = [('rdataframe', '(Types|RDataFrame)')]
    
    def compute(self):
        idict = self.get_input('dict')
        rdataframe = create_data_frame(idict)
        self.set_output('rdataframe', rdataframe)

class DictFromRDataFrame(Module):
    _input_ports = [('rdataframe','(Types|RDataFrame)')]
    _output_ports = [('dict', '(basic:Dictionary)')]

    def compute(self):
        rdataframe = self.get_input('rdataframe')
        colnames = list(rdataframe.colnames())
        odict = {}
        for i in xrange(len(rdataframe)):
            # FIXME !!! just assume that each row can be converted to a list!!!
            odict[colnames[i]] = list(rdataframe[i])
        self.set_output('dict', odict)

class RListFromDict(Module):
    # _input_ports = [('dict', '(basic:Dictionary)')]
    _input_ports = [('dict', '(basic:Module)')]
    _output_ports = [('rlist', '(Types|RList)')]
    
    def compute(self):
        idict = self.get_input('dict')
        rlist = create_list(idict)
        self.set_output('rlist', rlist)

class DictFromRList(Module):
    _input_ports = [('rlist', '(Types|RList)')]
    # _output_ports = [('dict', '(basic:Dictionary)')]
    _output_ports = [('dict', '(basic:Module)')]

    def compute(self):
        rlist = self.get_input('rlist')
        colnames = list(rlist.names)
        odict = {}
        for i in xrange(len(rlist)):
            # FIXME !!! just assume that each row can be converted to a list!!!
            # FIXME this may need to be a list of lists
            odict[colnames[i]] = list(rlist[i])
        self.set_output('dict', odict)

class RRead(Module):
    _input_ports = [('file', '(basic:File)'),
                    ('header', '(basic:Boolean)', True),
                    ('sep', '(basic:String)', True),
                    ('commentChar', '(basic:String)', True),
                    ('quote', '(basic:String)', True),
                    ('dec', '(basic:String)', True),
                    ('fill', '(basic:Boolean)', True)]
    _output_ports = [('rdataframe', '(Types|RDataFrame)')]

    def do_read(self, read_cmd):
        fname = self.get_input('file').name
        options_dict = {}
        for port in RRead._input_ports:
            if port[0] != 'file' and self.has_input(port):
                options_dict[port] = self.get_input(port)
        rdataframe = robjects.r[read_cmd](fname, **options_dict)
        self.set_output('rdataframe', rdataframe)

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
    _input_ports = [('source', '(basic:String)', True)]
    def run_code(self, code_str,
                 use_input=False,
                 use_output=False,
                 excluded_inputs=set(),
                 excluded_outputs=set()):
        """run_code runs a piece of code as a VisTrails module.
        use_input and use_output control whether to use the inputport
        and output port dictionary as local variables inside the
        execution."""
        import vistrails.core.packagemanager
        def fail(msg):
            raise ModuleError(self, msg)
        def cache_this():
            self.is_cacheable = lambda *args, **kwargs: True
        if use_input:
            inputDict = dict([(k, self.get_input(k))
                              for k in self.inputPorts
                              if k not in excluded_inputs])
            for k,v in inputDict.iteritems():
                robjects.globalEnv[k] = v
        robjects.r(code_str)
        if use_output:
            for k in self.outputPorts:
                if k not in excluded_outputs and k in robjects.globalEnv:
                    self.set_output(k, robjects.globalEnv[k])

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
        code_str = urllib.unquote(str(self.force_get_input('source', '')))
        self.run_code(code_str, use_input=True, use_output=True,
                      excluded_inputs=set(['source']))

class RFigure(RSource):
    _output_ports = [('imageFile', '(basic:File)')]
    def run_figure(self, code_str, graphics_dev, width, height, 
                   excluded_inputs=set(['source'])):
        fname = self.interpreter.filePool.create_file(prefix='vtr', suffix='.' + graphics_dev)
        r_temp_files.append(fname)
        robjects.r[graphics_dev](file=fname, width=width, height=height)
        self.run_code(code_str, use_input=True, 
                      excluded_inputs=excluded_inputs)
        robjects.r['dev.off']()
        image_file = PathObject(fname)
        self.set_output('imageFile', image_file)

    def run_figure_file(self, fname, graphics_dev, width, height, 
                        excluded_inputs=set(['source'])):
        f = open(fname)
        code_str = f.readlines()
        f.close()
        self.run_figure(code_str, graphics_dev, width, height, excluded_inputs)

class RSVGFigure(RFigure):
    def compute(self):
        code_str = \
            urllib.unquote(str(self.force_get_input('source', '')))
        RFigure.run_figure(self, code_str, 'svg', 4, 3)

class RPNGFigure(RFigure):
    def compute(self):
        code_str = \
            urllib.unquote(str(self.force_get_input('source', '')))
        RFigure.run_figure(self, code_str, 'png', 640, 480)

class RPDFFigure(RFigure):
    def compute(self):
        code_str = \
            urllib.unquote(str(self.force_get_input('source', '')))
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

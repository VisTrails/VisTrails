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
"""basic_modules defines basic VisTrails Modules that are used in most
pipelines."""

import core.cache.hasher
from core.modules.module_registry import get_module_registry
from core.modules import vistrails_module
from core.modules.vistrails_module import Module, new_module, \
     NotCacheable, ModuleError
from core.system import vistrails_version
from core.utils import InstanceObject
from core import debug


import core.system
from itertools import izip
import re
import os
import os.path
import shutil
try:
    import hashlib
    sha_hash = hashlib.sha1
except ImportError:
    import sha
    sha_hash = sha.new
import zipfile
import urllib

###############################################################################

version = '1.6'
name = 'Basic Modules'
identifier = 'edu.utah.sci.vistrails.basic'

class Constant(Module):
    """Base class for all Modules that represent a constant value of
    some type.
    
    When implementing your own constant, You have to adhere to the
    following interface:

    Implement the following methods:
    
       translate_to_python(x): Given a string, translate_to_python
       must return a python value that will be the value seen by the
       execution modules.

       For example, translate_to_python called on a float parameter
       with value '3.15' will return float('3.15').
       
       translate_to_string(): Return a string representation of the
       current constant, which will eventually be passed to
       translate_to_python.

       validate(v): return True if given python value is a plausible
       value for the constant. It should be implemented such that
       validate(translate_to_python(x)) == True for all valid x

    A constant must also expose its default value, through the field
    default_value.

    There are fields you are not allowed to use in your constant classes.
    These are: 'id', 'interpreter', 'logging' and 'change_parameter'

    You can also define the constant's own GUI widget.
    See core/modules/constant_configuration.py for details.
    
    """
    def __init__(self):
        Module.__init__(self)
        
    def compute(self):
        """Constant.compute() only checks validity (and presence) of
        input value."""
        v = self.getInputFromPort("value")
        b = self.validate(v)
        if not b:
            raise ModuleError(self, "Internal Error: Constant failed validation")
        self.setResult("value", v)
        self.setResult("value_as_string", self.translate_to_string(v))

    def setValue(self, v):
        self.setResult("value", self.translate_to_python(v))
        self.upToDate = True

    @staticmethod
    def translate_to_string(v):
        return str(v)

    @staticmethod
    def get_widget_class():
        # return StandardConstantWidget
        return None

    @staticmethod
    def get_query_widget_class():
        return None

    @staticmethod
    def get_param_explore_widget_list():
        return []

    @staticmethod
    def query_compute(value_a, value_b, query_method):
        if query_method == '==' or query_method is None:
            return (value_a == value_b)
        elif query_method == '!=':
            return (value_a != value_b)
        return False

def new_constant(name, py_conversion, default_value, validation,
                 widget_type=None,
                 str_conversion=None, base_class=Constant,
                 compute=None, query_widget_type=None,
                 query_compute=None,
                 param_explore_widget_list=None):
    """new_constant(name: str, 
                    py_conversion: callable,
                    default_value: python_type,
                    validation: callable,
                    widget_type: (path, name) tuple or QWidget type,
                    str_conversion: callable,
                    base_class: class,
                    compute: callable,
                    query_widget_type: (path, name) tuple or QWidget type,
                    query_compute: static callable,
                    param_explore_widget_list: 
                        list((path, name) tuple or QWidget type)) -> Module

    new_constant dynamically creates a new Module derived from
    Constant with given py_conversion and str_conversion functions, a
    corresponding python type and a widget type. py_conversion is a
    python callable that takes a string and returns a python value of
    the type that the class should hold. str_conversion does the reverse.

    This is the quickest way to create new Constant Modules."""
    
    def create_init(base_class):
        def __init__(self):
            base_class.__init__(self)
        return __init__

    d = {'__init__': create_init(base_class),
         'validate': validation,
         'translate_to_python': py_conversion,
         'default_value': default_value,
         }
    if str_conversion is not None:
        d['translate_to_string'] = str_conversion
    if compute is not None:
        d['compute'] = compute
    if query_compute is not None:
        d['query_compute'] = query_compute
    if widget_type is not None:
        @staticmethod
        def get_widget_class():
            return widget_type
        d['get_widget_class'] = get_widget_class
    if query_widget_type is not None:
        @staticmethod
        def get_query_widget_class():
            return query_widget_type
        d['get_query_widget_class'] = get_query_widget_class
    if param_explore_widget_list is not None:
        @staticmethod
        def get_param_explore_widget_list():
            return param_explore_widget_list
        d['get_param_explore_widget_list'] = get_param_explore_widget_list

    m = new_module(base_class, name, d)
    m._input_ports = [('value', m)]
    m._output_ports = [('value', m)]
    return m

def bool_conv(x):
    s = str(x).upper()
    if s == 'TRUE':
        return True
    if s == 'FALSE':
        return False
    raise ValueError('Boolean from String in VisTrails should be either \
"true" or "false", got "%s" instead' % x)

def int_conv(x):
    if x.startswith('0x'):
        return int(x, 16)
    else:
        return int(x)

@staticmethod
def numeric_compare(value_a, value_b, query_method):
    value_a = float(value_a)
    value_b = float(value_b)
    if query_method == '==' or query_method is None:
        return (value_a == value_b)
    elif query_method == '<':
        return (value_a < value_b)
    elif query_method == '>':
        return (value_a > value_b)
    elif query_method == '<=':
        return (value_a <= value_b)
    elif query_method == '>=':
        return (value_a >= value_b)

@staticmethod
def string_compare(value_a, value_b, query_method):
    if query_method == '*[]*' or query_method is None:
        return (value_b in value_a)
    elif query_method == '==':
        return (value_a == value_b)
    elif query_method == '=~':
        try:
            m = re.match(value_b, value_a)
            if m is not None:
                return (m.end() ==len(value_a))
        except:
            pass
    return False

Boolean = new_constant('Boolean' , staticmethod(bool_conv),
                       False, staticmethod(lambda x: type(x) == bool),
                       widget_type=('gui.modules.constant_configuration', 
                                    'BooleanWidget'))
Float   = new_constant('Float'   , staticmethod(float), 0.0, 
                       staticmethod(lambda x: type(x) == float),
                       query_widget_type=('gui.modules.query_configuration',
                                          'NumericQueryWidget'),
                       query_compute=numeric_compare,
                       param_explore_widget_list=[('gui.modules.paramexplore',
                                                   'FloatExploreWidget')])
Integer = new_constant('Integer' , staticmethod(int_conv), 0, 
                       staticmethod(lambda x: type(x) == int),
                       query_widget_type=('gui.modules.query_configuration',
                                          'NumericQueryWidget'),
                       query_compute=numeric_compare,
                       param_explore_widget_list=[('gui.modules.paramexplore',
                                                   'IntegerExploreWidget')])
String  = new_constant('String'  , staticmethod(str), "", 
                       staticmethod(lambda x: type(x) == str),
                       query_widget_type=('gui.modules.query_configuration',
                                          'StringQueryWidget'),
                       query_compute=string_compare)

##############################################################################

class Path(Constant):
    def __init__(self):
        Constant.__init__(self)
        self.name = ""
    
    @staticmethod
    def translate_to_python(x):
        result = Path()
        result.name = x
        result.setResult("value", result)
        return result

    @staticmethod
    def translate_to_string(x):
        return str(x.name)

    @staticmethod
    def validate(v):
        #print 'validating', v
        #print 'isinstance', isinstance(v, Path)
        return isinstance(v, Path)

    def get_name(self):
        n = None
        if self.hasInputFromPort("value"):
            n = self.getInputFromPort("value").name
        if n is None:
            self.checkInputPort("name")
            n = self.getInputFromPort("name")
        return n
        
    def set_results(self, n):
        self.name = n
        self.setResult("value", self)
        self.setResult("value_as_string", self.translate_to_string(self))

    def compute(self):
        n = self.get_name()
        self.set_results(n)
#         self.setResult("exists", os.path.exists(n))
#         self.setResult("isfile", os.path.isfile(n))
#         self.setResult("isdir", os.path.isdir(n))
        
    @staticmethod
    def get_widget_class():
        return ("gui.modules.constant_configuration", "PathChooserWidget")

Path.default_value = Path()

class File(Path):
    """File is a VisTrails Module that represents a file stored on a
    file system local to the machine where VisTrails is running."""
    def __init__(self):
        Path.__init__(self)
        
    @staticmethod
    def translate_to_python(x):
        result = File()
        result.name = x
        result.setResult("value", result)
        return result

    def compute(self):
        n = self.get_name()
        if (self.hasInputFromPort("create_file") and
            self.getInputFromPort("create_file")):
            core.system.touch(n)
        if not os.path.isfile(n):
            raise ModuleError(self, 'File "%s" does not exist' % n)
        self.set_results(n)
        self.setResult("local_filename", n)
        self.setResult("self", self)

    @staticmethod
    def get_widget_class():
        return ("gui.modules.constant_configuration", "FileChooserWidget")

File.default_value = File()
    
class Directory(Path):
    def __init__(self):
        Path.__init__(self)
        Directory.default_value = self
        
    @staticmethod
    def translate_to_python(x):
        result = Directory()
        result.name = x
        result.setResult("value", result)
        return result

    def compute(self):
        n = self.get_name()
        if (self.hasInputFromPort("create_directory") and
            self.getInputFromPort("create_directory")):
            try:
                core.system.mkdir(n)
            except Exception, e:
                raise ModuleError(self, 'mkdir: ' + str(e))
        if not os.path.isdir(n):
            raise ModuleError(self, 'Directory "%s" does not exist' % n)
        self.set_results(n)
        
        dir_list = os.listdir(n)
        output_list = []
        for item in dir_list:
            full_path = os.path.join(n, item)
            if os.path.isfile(full_path):
                file_item = File()
                file_item.name = full_path
                file_item.upToDate = True
                output_list.append(file_item)
            elif os.path.isdir(full_path):
                dir_item = Directory()
                dir_item.name = full_path
                dir_item.upToDate = True
                output_list.append(dir_item)
        self.setResult('itemList', output_list)
            
    @staticmethod
    def get_widget_class():
        return ("gui.modules.constant_configuration", "DirectoryChooserWidget")

Directory.default_value = Directory()

def path_parameter_hasher(p):
    def get_mtime(path):
        v_list = [int(os.path.getmtime(path))]
        if os.path.isdir(path):
            for subpath in os.listdir(path):
                subpath = os.path.join(path, subpath)
                if os.path.isdir(subpath):
                    v_list.extend(get_mtime(subpath))
        return v_list

    h = core.cache.hasher.Hasher.parameter_signature(p)
    hasher = sha_hash()
    try:
        # FIXME: This will break with aliases - I don't really care that much
        v_list = get_mtime(p.strValue)
    except OSError:
        return h
    hasher = sha_hash()
    hasher.update(h)
    for v in v_list:
        hasher.update(str(v))
    return hasher.digest()

##############################################################################

class OutputPath(Path):
    def get_name(self):
        n = None
        if self.hasInputFromPort("value"):
            n = self.getInputFromPort("value").name
        if n is None:
            self.checkInputPort("name")
            n = self.getInputFromPort("name")
        return n
        
    def set_results(self, n):
        self.name = n
        self.setResult("value", self)
        self.setResult("value_as_string", self.translate_to_string(self))

    def compute(self):
        n = self.get_name()
        self.set_results(n)
        
    @staticmethod
    def get_widget_class():
        return ("gui.modules.constant_configuration", "OutputPathChooserWidget")

OutputPath.default_value = OutputPath()

class FileSink(NotCacheable, Module):
    """FileSink takes a file and writes it to a user-specified
    location in the file system.  The file is stored at location
    specified by the outputPath.  The overwrite flag allows users to
    specify whether an existing path should be overwritten."""

    def compute(self):
        input_file = self.getInputFromPort("file")
        output_path = self.getInputFromPort("outputPath")
        full_path = output_path.name

        try:
            core.system.link_or_copy(input_file.name, full_path)
        except OSError, e:
            if self.hasInputFromPort("overwrite") and \
                    self.getInputFromPort("overwrite"):
                try:
                    os.unlink(full_path)
                    core.system.link_or_copy(input_file.name, full_path)
                except OSError:
                    msg = "(override true) Could not create file '%s'" % \
                        full_path
                    raise ModuleError(self, msg)
            else:
                msg = "Could not create file '%s': %s" % (full_path, e)
                raise ModuleError(self, msg)
            
        if (self.hasInputFromPort("publishFile") and
            self.getInputFromPort("publishFile") or 
            not self.hasInputFromPort("publishFile")):
            if self.moduleInfo.has_key('extra_info'):
                if self.moduleInfo['extra_info'].has_key('pathDumpCells'):
                    folder = self.moduleInfo['extra_info']['pathDumpCells']
                    base_fname = os.path.basename(full_path)
                    (base_fname, file_extension) = os.path.splitext(base_fname)
                    base_fname = os.path.join(folder, base_fname)
                    # make a unique filename
                    filename = base_fname + file_extension
                    counter = 2
                    while os.path.exists(filename):
                        filename = base_fname + "_%d%s" % (counter,
                                                           file_extension)
                        counter += 1
                    try:
                        core.system.link_or_copy(input_file.name, filename)
                    except OSError:
                        msg = "Could not publish file '%s' \n   on  '%s': %s" % \
                               (full_path, filename, e)
                        # I am not sure whether we should raise an error
                        # I will just print a warning for now (Emanuele)
                        debug.warning("%s" % msg)

class DirectorySink(NotCacheable, Module):
    """DirectorySink takes a directory and writes it to a
    user-specified location in the file system.  The directory is
    stored at location specified by the outputPath.  The overwrite
    flag allows users to specify whether an existing path should be
    overwritten."""

    def compute(self):
        input_dir = self.getInputFromPort("dir")
        output_path = self.getInputFromPort("outputPath")
        full_path = output_path.name

        if os.path.exists(full_path):
            if (self.hasInputFromPort("overwrite") and 
                self.getInputFromPort("overwrite")):
                try:
                    if os.path.isfile(full_path):
                        os.remove(full_path)
                    else:
                        shutil.rmtree(full_path)
                except OSError, e:
                    msg = ('Could not delete existing path "%s" '
                           '(overwrite on)' % full_path)
                    raise ModuleError(self, msg + '\n' + str(e))
            else:
                msg = ('Could not write to existing path "%s" '
                       '(overwrite off)' % full_path)
                raise ModuleError(self, msg)
            
        try:
            shutil.copytree(input_dir.name, full_path)
        except OSError, e:
            msg = 'Could not copy path from "%s" to "%s"' % \
                (input_dir.name, full_path)
            raise ModuleError(self, msg + '\n' + str(e))


        
##############################################################################

class Color(Constant):
    # We set the value of a color object to be an InstanceObject that
    # contains a tuple because a tuple would be interpreted as a
    # type(tuple) which messes with the interpreter

    def __init__(self):
        Constant.__init__(self)
    
    default_value = InstanceObject(tuple=(1,1,1))
        
    @staticmethod
    def translate_to_python(x):
        return InstanceObject(
            tuple=tuple([float(a) for a in x.split(',')]))

    @staticmethod
    def translate_to_string(v):
        return str(v.tuple)[1:-1]

    @staticmethod
    def validate(x):
        return type(x) == InstanceObject and hasattr(x, 'tuple')

    @staticmethod
    def to_string(r, g, b):
        return "%s,%s,%s" % (r,g,b)

    @staticmethod
    def get_widget_class():
        return ("gui.modules.constant_configuration", "ColorWidget")
        
    @staticmethod
    def get_query_widget_class():
        return ("gui.modules.query_configuration", "ColorQueryWidget")

    @staticmethod
    def get_param_explore_widget_list():
        return [('gui.modules.paramexplore', 'RGBExploreWidget'),
                ('gui.modules.paramexplore', 'HSVExploreWidget')]

    @staticmethod
    def query_compute(value_a, value_b, query_method):
        # SOURCE: http://www.easyrgb.com/index.php?X=MATH
        def rgb_to_xyz(r, g, b):
            # r,g,b \in [0,1]

            if r > 0.04045: 
                r = ( ( r + 0.055 ) / 1.055 ) ** 2.4
            else:
                r = r / 12.92
            if g > 0.04045:
                g = ( ( g + 0.055 ) / 1.055 ) ** 2.4
            else:
                g = g / 12.92
            if b > 0.04045: 
                b = ( ( b + 0.055 ) / 1.055 ) ** 2.4
            else:
                b = b / 12.92

            r *= 100
            g *= 100
            b *= 100

            # Observer. = 2 deg, Illuminant = D65
            x = r * 0.4124 + g * 0.3576 + b * 0.1805
            y = r * 0.2126 + g * 0.7152 + b * 0.0722
            z = r * 0.0193 + g * 0.1192 + b * 0.9505
            return (x,y,z)

        def xyz_to_cielab(x,y,z):
            # Observer= 2 deg, Illuminant= D65
            ref_x, ref_y, ref_z = (95.047, 100.000, 108.883)
            x /= ref_x
            y /= ref_y
            z /= ref_z

            if x > 0.008856:
                x = x ** ( 1/3.0 )
            else:                    
                x = ( 7.787 * x ) + ( 16 / 116.0 )
            if y > 0.008856:
                y = y ** ( 1/3.0 )
            else:
                y = ( 7.787 * y ) + ( 16 / 116.0 )
            if z > 0.008856: 
                z = z ** ( 1/3.0 )
            else:
                z = ( 7.787 * z ) + ( 16 / 116.0 )

            L = ( 116 * y ) - 16
            a = 500 * ( x - y )
            b = 200 * ( y - z )
            return (L, a, b)

        def rgb_to_cielab(r,g,b):
            return xyz_to_cielab(*rgb_to_xyz(r,g,b))
        
        value_a_rgb = (float(a) for a in value_a.split(','))
        value_b_rgb = (float(b) for b in value_b.split(','))
        value_a_lab = rgb_to_cielab(*value_a_rgb)
        value_b_lab = rgb_to_cielab(*value_b_rgb)
        
        # cie76 difference
        diff = sum((v_1 - v_2) ** 2 
                   for v_1, v_2 in izip(value_a_lab, value_b_lab)) ** (0.5)

        # print "CIE 76 DIFFERENCE:", diff
        if query_method is None:
            query_method = '2.3'
        return diff < float(query_method)

##############################################################################

# class OutputWindow(Module):
    
#     def compute(self):
#         v = self.getInputFromPort("value")
#         from PyQt4 import QtCore, QtGui
#         QtGui.QMessageBox.information(None,
#                                       "VisTrails",
#                                       str(v))

#Removing Output Window because it does not work with current threading
#reg.add_module(OutputWindow)
#reg.add_input_port(OutputWindow, "value",
#                               Module)

##############################################################################

class StandardOutput(NotCacheable, Module):
    """StandardOutput is a VisTrails Module that simply prints the
    value connected on its port to standard output. It is intended
    mostly as a debugging device."""
    
    def compute(self):
        v = self.getInputFromPort("value")
        print v

##############################################################################

# Tuple will be reasonably magic right now. We'll integrate it better
# with vistrails later.
# TODO: Check Tuple class, test, integrate.
class Tuple(Module):
    """Tuple represents a tuple of values. Tuple might not be well
    integrated with the rest of VisTrails, so don't use it unless
    you know what you're doing."""

    def __init__(self):
        Module.__init__(self)
        self.input_ports_order = []
        self.values = tuple()

    def compute(self):
        values = tuple([self.getInputFromPort(p)
                        for p in self.input_ports_order])
        self.values = values
        self.setResult("value", values)
        
class TestTuple(Module):
    def compute(self):
        pair = self.getInputFromPort('tuple')
        print pair
        
class Untuple(Module):
    """Untuple takes a tuple and returns the individual values.  It
    reverses the actions of Tuple.

    """
    def __init__(self):
        Module.__init__(self)
        self.output_ports_order = []

    def compute(self):
        if self.hasInputFromPort("tuple"):
            tuple = self.getInputFromPort("tuple")
            values = tuple.values
        else:
            values = self.getInputFromPort("value")
        for p, value in izip(self.output_ports_order, values):
            self.setResult(p, value)

##############################################################################

# TODO: Create a better Module for ConcatenateString.
class ConcatenateString(Module):
    """ConcatenateString takes many strings as input and produces the
    concatenation as output. Useful for constructing filenames, for
    example.

    This class will probably be replaced with a better API in the
    future."""

    fieldCount = 4

    def compute(self):
        result = ""
        for i in xrange(self.fieldCount):
            v = i+1
            port = "str%s" % v
            if self.hasInputFromPort(port):
                inp = self.getInputFromPort(port)
                result += inp
        self.setResult("value", result)

##############################################################################
# List

def list_conv(v):
    v_list = eval(v)
    return v_list

def list_compute(self):
    if (not self.hasInputFromPort("value") and 
        not self.hasInputFromPort("tail") and
        not self.hasInputFromPort("head")):
        # fail at getting the value port
        self.getInputFromPort("value")
            
    head, middle, tail = [], [], []
    if self.hasInputFromPort("value"):
        # run the regular compute here
        Constant.compute(self)
        middle = self.outputPorts['value']
    if self.hasInputFromPort("head"):
        head = [self.getInputFromPort("head")]
    if self.hasInputFromPort("tail"):
        tail = self.getInputFromPort("tail")
    self.setResult("value", head + middle + tail)

List = new_constant('List' , staticmethod(list_conv),
                    [], staticmethod(lambda x: type(x) == list),
                    compute=list_compute)

##############################################################################
# Dictionary
                    
def dict_conv(v):
    v_dict = eval(v)
    return v_dict

def dict_compute(self):
    d = {}
    if self.hasInputFromPort('value'):
        Constant.compute(self)
        d.update(self.outputPorts['value'])
    if self.hasInputFromPort('addPair'):
        pairs_list = self.getInputListFromPort('addPair')
        d.update(pairs_list)
    if self.hasInputFromPort('addPairs'):
        d.update(self.getInputFromPort('addPairs'))
        
    self.setResult("value", d)
        
Dictionary = new_constant('Dictionary', staticmethod(dict_conv),
                          {}, staticmethod(lambda x: type(x) == dict),
                          compute=dict_compute)

##############################################################################

# TODO: Null should be a subclass of Constant?
class Null(Module):
    """Null is the class of None values."""
    
    def compute(self):
        self.setResult("value", None)

##############################################################################

class PythonSource(NotCacheable, Module):
    """PythonSource is a Module that executes an arbitrary piece of
    Python code.
    
    It is especially useful for one-off pieces of 'glue' in a
    pipeline.

    If you want a PythonSource execution to fail, call
    fail(error_message).

    If you want a PythonSource execution to be cached, call
    cache_this().
    """

    def run_code(self, code_str,
                 use_input=False,
                 use_output=False):
        """run_code runs a piece of code as a VisTrails module.
        use_input and use_output control whether to use the inputport
        and output port dictionary as local variables inside the
        execution."""
        import core.packagemanager
        def fail(msg):
            raise ModuleError(self, msg)
        def cache_this():
            self.is_cacheable = lambda *args, **kwargs: True
        locals_ = locals()
        if use_input:
            inputDict = dict([(k, self.getInputFromPort(k))
                              for k in self.inputPorts])
            locals_.update(inputDict)
        if use_output:
            outputDict = dict([(k, None)
                               for k in self.outputPorts])
            locals_.update(outputDict)
        _m = core.packagemanager.get_package_manager()
        reg = get_module_registry()
        locals_.update({'fail': fail,
                        'package_manager': _m,
                        'cache_this': cache_this,
                        'registry': reg,
                        'self': self})
        del locals_['source']
        exec code_str in locals_, locals_
        if use_output:
            for k in outputDict.iterkeys():
                if locals_[k] != None:
                    self.setResult(k, locals_[k])

    def compute(self):
        s = urllib.unquote(str(self.forceGetInputFromPort('source', '')))
        self.run_code(s, use_input=True, use_output=True)

##############################################################################

class SmartSource(NotCacheable, Module):

    def run_code(self, code_str,
                 use_input=False,
                 use_output=False):
        import core.packagemanager
        def fail(msg):
            raise ModuleError(self, msg)
        def cache_this():
            self.is_cacheable = lambda *args, **kwargs: True
        locals_ = locals()

        def smart_input_entry(k):
            v = self.getInputFromPort(k)
            if isinstance(v, Module) and hasattr(v, 'get_source'):
                v = v.get_source()
            return (k, v)

        def get_mro(v):
            # Tries to get the mro from strange class hierarchies like VTK's
            try:
                return v.mro()
            except AttributeError:
                def yield_all(v):
                    b = v.__bases__
                    yield v
                    for base in b:
                        g = yield_all(base)
                        while 1: yield g.next()
                return [x for x in yield_all(v)]
            
        if use_input:
            inputDict = dict([smart_input_entry(k)
                              for k in self.inputPorts])
            locals_.update(inputDict)
        if use_output:
            outputDict = dict([(k, None)
                               for k in self.outputPorts])
            locals_.update(outputDict)
        _m = core.packagemanager.get_package_manager()
        locals_.update({'fail': fail,
                        'package_manager': _m,
                        'cache_this': cache_this,
                        'self': self})
        del locals_['source']
        exec code_str in locals_, locals_
        if use_output:
            oports = self.registry.get_descriptor(SmartSource).output_ports
            for k in outputDict.iterkeys():
                if locals_[k] != None:
                    v = locals_[k]
                    spec = oports.get(k, None)
                    
                    if spec:
                        # See explanation of algo in doc/smart_source_resolution_algo.txt
                        port_vistrail_base_class = spec.types()[0]
                        mro = get_mro(type(v))
                        source_types = self.registry.python_source_types
                        found = False
                        for python_class in mro:
                            if python_class in source_types:
                                vistrail_classes = [x for x in source_types[python_class]
                                                    if issubclass(x, port_vistrail_base_class)]
                                if len(vistrail_classes) == 0:
                                    # FIXME better error handling
                                    raise ModuleError(self, "Module Registry inconsistent")
                                vt_class = vistrail_classes[0]
                                found = True
                                break
                        if found:
                            vt_instance = vt_class()
                            vt_instance.set_source(v)
                            v = vt_instance
                    self.setResult(k, v)

    def compute(self):
        s = urllib.unquote(str(self.forceGetInputFromPort('source', '')))
        self.run_code(s, use_input=True, use_output=True)

##############################################################################

class _ZIPDecompressor(object):

    """_ZIPDecompressor extracts a file from a .zip file. On Win32, uses
the zipfile library from python. On Linux/Macs, uses command line, because
it avoids moving the entire file contents to/from memory."""

    # TODO: Figure out a way of doing this right on Win32

    def __init__(self, archive, filename_in_archive, output_filename):
        self._archive = archive
        self._filename_in_archive = filename_in_archive
        self._output_filename = output_filename

    if core.system.systemType in ['Windows', 'Microsoft']:
        def extract(self):
            os.system('unzip -p "%s" "%s" > "%s"' %
                      (self._archive,
                       self._filename_in_archive,
                       self._output_filename))
# zipfile cannot handle big files
#            import zipfile
#             output_file = file(self._output_filename, 'w')
#             zip_file = zipfile.ZipFile(self._archive)
#             contents = zip_file.read(self._filename_in_archive)
#             output_file.write(contents)
#             output_file.close()
    else:
        def extract(self):
            os.system("unzip -p %s %s > %s" %
                      (self._archive,
                       self._filename_in_archive,
                       self._output_filename))
            

class Unzip(Module):
    """Unzip extracts a file from a ZIP archive."""

    def compute(self):
        self.checkInputPort("archive_file")
        self.checkInputPort("filename_in_archive")
        filename_in_archive = self.getInputFromPort("filename_in_archive")
        archive_file = self.getInputFromPort("archive_file")
        suffix = self.interpreter.filePool.guess_suffix(filename_in_archive)
        output = self.interpreter.filePool.create_file(suffix=suffix)
        dc = _ZIPDecompressor(archive_file.name,
                              filename_in_archive,
                              output.name)
        dc.extract()
        self.setResult("file", output)

##############################################################################
    
class Variant(Module):
    """
    Variant is tracked internally for outputing a variant type on
    output port. For input port, Module type should be used
    
    """
    pass

def init_constant(m):
    reg = get_module_registry()

    reg.add_module(m)
    reg.add_input_port(m, "value", m)
    reg.add_output_port(m, "value", m)
    
def initialize(*args, **kwargs):
    reg = get_module_registry()

    # !!! is_root should only be set for Module !!!
    reg.add_module(Module, is_root=True)
    reg.add_output_port(Module, "self", Module, optional=True)

    reg.add_module(Constant)

    reg.add_module(Boolean)
    reg.add_module(Float)
    reg.add_module(Integer)
    reg.add_module(String)
    
    reg.add_output_port(Constant, "value_as_string", String)
    reg.add_output_port(String, "value_as_string", String, True)

    reg.add_module(List)
    reg.add_input_port(List, "head", Module)
    reg.add_input_port(List, "tail", List)

    reg.add_module(Path)
    reg.add_input_port(Path, "value", Path)
    reg.add_output_port(Path, "value", Path)
    reg.add_input_port(Path, "name", String, True)

    reg.add_module(File, constantSignatureCallable=path_parameter_hasher)
    reg.add_input_port(File, "value", File)
    reg.add_output_port(File, "value", File)
    reg.add_output_port(File, "self", File, True)
    reg.add_input_port(File, "create_file", Boolean, True)
    reg.add_output_port(File, "local_filename", String, True)

    reg.add_module(Directory, constantSignatureCallable=path_parameter_hasher)
    reg.add_input_port(Directory, "value", Directory)
    reg.add_output_port(Directory, "value", Directory)
    reg.add_output_port(Directory, "itemList", List)
    reg.add_input_port(Directory, "create_directory", Boolean, True)

    reg.add_module(OutputPath)
    reg.add_output_port(OutputPath, "value", OutputPath)

    reg.add_module(FileSink)
    reg.add_input_port(FileSink, "file", File)
    reg.add_input_port(FileSink, "outputPath", OutputPath)
    reg.add_input_port(FileSink, "overwrite", Boolean, True, 
                       defaults="(True,)")
    reg.add_input_port(FileSink,  "publishFile", Boolean, True)
    
    reg.add_module(DirectorySink)
    reg.add_input_port(DirectorySink, "dir", Directory)
    reg.add_input_port(DirectorySink, "outputPath", OutputPath)
    reg.add_input_port(DirectorySink, "overwrite", Boolean, True, 
                       defaults="(True,)")

    reg.add_module(Color)
    reg.add_input_port(Color, "value", Color)
    reg.add_output_port(Color, "value", Color)

    reg.add_module(StandardOutput)
    reg.add_input_port(StandardOutput, "value", Module)

    reg.add_module(Tuple, 
                   configureWidgetType=("gui.modules.tuple_configuration",
                                        "TupleConfigurationWidget"))
    reg.add_output_port(Tuple, 'self', Tuple)

    reg.add_module(TestTuple)
    reg.add_input_port(TestTuple, 'tuple', [Integer, String])

    reg.add_module(Untuple, 
                   configureWidgetType=("gui.modules.tuple_configuration",
                                        "UntupleConfigurationWidget"))
    reg.add_input_port(Untuple, 'tuple', Tuple)

    reg.add_module(ConcatenateString)
    for i in xrange(ConcatenateString.fieldCount):
        j = i+1
        port = "str%s" % j
        reg.add_input_port(ConcatenateString, port, String)
    reg.add_output_port(ConcatenateString, "value", String)

    reg.add_module(Dictionary)
    reg.add_input_port(Dictionary, "addPair", [Module, Module])
    reg.add_input_port(Dictionary, "addPairs", List)

    reg.add_module(Null)

    reg.add_module(PythonSource,
                   configureWidgetType=("gui.modules.python_source_configure",
                                        "PythonSourceConfigurationWidget"))
    reg.add_input_port(PythonSource, 'source', String, True)
    reg.add_output_port(PythonSource, 'self', Module)

    reg.add_module(SmartSource,
                   configureWidgetType=("gui.modules.python_source_configure",
                                        "PythonSourceConfigurationWidget"))
    reg.add_input_port(SmartSource, 'source', String, True)

    reg.add_module(Unzip)
    reg.add_input_port(Unzip, 'archive_file', File)
    reg.add_input_port(Unzip, 'filename_in_archive', String)
    reg.add_output_port(Unzip, 'file', File)

    reg.add_module(Variant)

    # initialize the sub_module modules, too
    import core.modules.sub_module
    core.modules.sub_module.initialize(*args, **kwargs)


def handle_module_upgrade_request(controller, module_id, pipeline):
   from core.upgradeworkflow import UpgradeWorkflowHandler
   reg = get_module_registry()

   def outputName_remap(old_conn, new_module):
       ops = []
       old_src_module = pipeline.modules[old_conn.source.moduleId]
       op_desc = reg.get_descriptor(OutputPath)
       new_x = (old_src_module.location.x + new_module.location.x) / 2.0
       new_y = (old_src_module.location.y + new_module.location.y) / 2.0
       op_module = \
           controller.create_module_from_descriptor(op_desc, new_x, new_y)
       ops.append(('add', op_module))
       create_new_connection = UpgradeWorkflowHandler.create_new_connection
       new_conn_1 = create_new_connection(controller,
                                          old_src_module,
                                          old_conn.source,
                                          op_module,
                                          "name")
       ops.append(('add', new_conn_1))
       new_conn_2 = create_new_connection(controller,
                                          op_module,
                                          "value",
                                          new_module,
                                          "outputPath")
       ops.append(('add', new_conn_2))
       return ops

   module_remap = {'FileSink':
                       [(None, '1.6', None,
                         {'dst_port_remap':
                              {'overrideFile': 'overwrite',
                               'outputName': outputName_remap},
                          'function_remap':
                              {'overrideFile': 'overwrite',
                               'outputName': 'outputPath'}})],
                   'GetItemsFromDirectory':
                       [(None, '1.6', 'Directory',
                         {'dst_port_remap':
                              {'dir': 'value'},
                          'src_port_remap':
                              {'itemlist': 'itemList'},
                          })],
                   'InputPort':
                       [(None, '1.6', None,
                         {'dst_port_remap': {'old_name': None}})],
                   'OutputPort':
                       [(None, '1.6', None,
                         {'dst_port_remap': {'old_name': None}})],
                   'PythonSource':
                       [(None, '1.6', None, {})],
                   }

   return UpgradeWorkflowHandler.remap_module(controller, module_id, pipeline,
                                              module_remap)

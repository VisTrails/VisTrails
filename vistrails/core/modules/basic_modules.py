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
"""basic_modules defines basic VisTrails Modules that are used in most
pipelines."""

import core.cache.hasher
from core.modules import module_configure
from core.modules.module_registry import get_module_registry
from core.modules import port_configure
from core.modules import vistrails_module
from core.modules.vistrails_module import Module, new_module, \
     NotCacheable, ModuleError
from core.modules.python_source_configure import PythonSourceConfigurationWidget
from core.modules.tuple_configuration import TupleConfigurationWidget, \
    UntupleConfigurationWidget
from core.modules.constant_configuration import StandardConstantWidget, \
     FileChooserWidget, ColorWidget, ColorChooserButton, BooleanWidget
from core.system import vistrails_version
from core.utils import InstanceObject
from core.modules.paramexplore import make_interpolator, \
     QFloatLineEdit, QIntegerLineEdit, FloatLinearInterpolator, \
     IntegerLinearInterpolator
from PyQt4 import QtGui

import core.packagemanager
import core.system
from itertools import izip
import os
import os.path
import sha
import zipfile
import urllib

###############################################################################

version = vistrails_version()
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
        return StandardConstantWidget

def new_constant(name, conversion, default_value,
                 validation,
                 widget_type=StandardConstantWidget):
    """new_constant(name: str, conversion: callable,
                    default_value: python_type,
                    validation: callable
                    widget_type: QWidget type) -> Module

    new_constant dynamically creates a new Module derived from Constant
    with a given conversion function, a corresponding python type and a
    widget type. conversion is a python callable that takes a string and
    returns a python value of the type that the class should hold.

    This is the quickest way to create new Constant Modules."""
    
    def __init__(self):
        Constant.__init__(self)

    @staticmethod
    def get_widget_class():
        return widget_type
    
    m = new_module(Constant, name, {'__init__': __init__,
                                    'validate': validation,
                                    'translate_to_python': conversion,
                                    'get_widget_class': get_widget_class,
                                    'default_value': default_value})
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

Boolean = new_constant('Boolean' , staticmethod(bool_conv),
                       False, staticmethod(lambda x: type(x) == bool),
                       BooleanWidget)
Float   = new_constant('Float'   , staticmethod(float), 0.0, 
                       staticmethod(lambda x: type(x) == float))
Integer = new_constant('Integer' , staticmethod(int_conv), 0, 
                       staticmethod(lambda x: type(x) == int))
String  = new_constant('String'  , staticmethod(str), "", 
                       staticmethod(lambda x: type(x) == str))

Float.parameter_exploration_widgets   = [
    make_interpolator(QFloatLineEdit,
                      FloatLinearInterpolator,
                      'Linear Interpolation')]
Integer.parameter_exploration_widgets = [
    make_interpolator(QIntegerLineEdit,
                      IntegerLinearInterpolator,
                      'Linear Interpolation')]

##############################################################################

class File(Constant):
    """File is a VisTrails Module that represents a file stored on a
    file system local to the machine where VisTrails is running."""

    def __init__(self):
        Constant.__init__(self)
        self.name = ""
        File.default_value = self

    @staticmethod
    def translate_to_python(x):
        result = File()
        result.name = x
        result.setResult("value", result)
        return result

    @staticmethod
    def translate_to_string(x):
        return str(x.name)
    
    def compute(self):
        n = None
        if self.hasInputFromPort("value"):
            n = self.getInputFromPort("value").name
        if n is None:
            self.checkInputPort("name")
            n = self.getInputFromPort("name")

        if (self.hasInputFromPort("create_file") and
            self.getInputFromPort("create_file")):
            core.system.touch(n)
        self.name = n
        if not os.path.isfile(n):
            raise ModuleError(self, "File '%s' not existent" % n)
        self.setResult("local_filename", self.name)
        self.setResult("self", self)
        self.setResult("value", self)
        self.setResult("value_as_string", self.translate_to_string(self))

    @staticmethod
    def get_widget_class():
        return FileChooserWidget

def file_parameter_hasher(p):
    h = core.cache.hasher.Hasher.parameter_signature(p)
    try:
        # FIXME: This will break with aliases - I don't really care that much
        v = int(os.path.getmtime(p.strValue))
    except OSError:
        return h
    hasher = sha.new()
    u = hasher.update
    u(h)
    u(str(v))
    return hasher.digest()

##############################################################################

class FileSink(NotCacheable, Module):
    """FileSink is a VisTrails Module that takes a file and writes it
    in a user-specified location in the file system."""

    def compute(self):
        self.checkInputPort("file")
        self.checkInputPort("outputName")
        v1 = self.getInputFromPort("file")
        v2 = self.getInputFromPort("outputName")
        try:
            core.system.link_or_copy(v1.name, v2)
        except OSError, e:
            if (self.hasInputFromPort("overrideFile") and
                self.getInputFromPort("overrideFile")):
                try:
                    os.unlink(v2)
                    core.system.link_or_copy(v1.name, v2)
                except OSError:
                    msg = "(override true) Could not create file '%s'" % v2
                    raise ModuleError(self, v2)
            else:
                msg = "Could not create file '%s': %s" % (v2, e)
                raise ModuleError(self, msg)

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
        return ColorWidget
        
class BaseColorInterpolator(object):

    def __init__(self, ifunc, begin, end, size):
        self._ifunc = ifunc
        self.begin = begin
        self.end = end
        self.size = size

    def get_values(self):
        if self.size <= 1:
            return [self.begin]
        result = [self._ifunc(self.begin, self.end, self.size, i)
                  for i in xrange(self.size)]
        return result

class RGBColorInterpolator(BaseColorInterpolator):

    def __init__(self, begin, end, size):
        def fun(b, e, s, i):
            b = [float(x) for x in b.split(',')]
            e = [float(x) for x in e.split(',')]
            u = float(i) / (float(s) - 1.0)
            [r,g,b] = [b[i] + u * (e[i] - b[i]) for i in [0,1,2]]
            return Color.to_string(r, g, b)
        BaseColorInterpolator.__init__(self, fun, begin, end, size)

class HSVColorInterpolator(BaseColorInterpolator):
    def __init__(self, begin, end, size):
        def fun(b, e, s, i):
            b = [float(x) for x in b.split(',')]
            e = [float(x) for x in e.split(',')]
            u = float(i) / (float(s) - 1.0)

            # Use QtGui.QColor as easy converter between rgb and hsv
            color_b = QtGui.QColor(int(b[0] * 255),
                                   int(b[1] * 255),
                                   int(b[2] * 255))
            color_e = QtGui.QColor(int(e[0] * 255),
                                   int(e[1] * 255),
                                   int(e[2] * 255))

            b_hsv = [color_b.hueF(), color_b.saturationF(), color_b.valueF()]
            e_hsv = [color_e.hueF(), color_e.saturationF(), color_e.valueF()]

            [new_h, new_s, new_v] = [b_hsv[i] + u * (e_hsv[i] - b_hsv[i])
                                     for i in [0,1,2]]
            new_color = QtGui.QColor()
            new_color.setHsvF(new_h, new_s, new_v)
            return Color.to_string(new_color.redF(),
                                   new_color.greenF(),
                                   new_color.blueF())
        BaseColorInterpolator.__init__(self, fun, begin, end, size)
    

class PEColorChooserButton(ColorChooserButton):

    def __init__(self, param_info, parent=None):
        ColorChooserButton.__init__(self, parent)
        r,g,b = [int(float(i) * 255) for i in param_info.value.split(',')]
        
        self.setColor(QtGui.QColor(r,g,b))
        self.setFixedHeight(22)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding,
                           QtGui.QSizePolicy.Fixed)

    def get_value(self):
        return Color.to_string(self.qcolor.redF(),
                               self.qcolor.greenF(),
                               self.qcolor.blueF())

Color.parameter_exploration_widgets = [
    make_interpolator(PEColorChooserButton,
                      RGBColorInterpolator,
                      'RGB Interpolation'),
    make_interpolator(PEColorChooserButton,
                      HSVColorInterpolator,
                      'HSV Interpolation')]

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

# TODO: Create a better Module for List.
class List(Module):
    """List represents a single cons cell of a linked list.

    This class will probably be replaced with a better API in the
    future."""

    def compute(self):

        if self.hasInputFromPort("head"):
            head = [self.getInputFromPort("head")]
        else:
            head = []

        if self.hasInputFromPort("tail"):
            tail = self.getInputFromPort("tail")
        else:
            tail = []

        self.setResult("value", head + tail)

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

    init_constant(Boolean)
    init_constant(Float)
    init_constant(Integer)
    init_constant(String)
    
    reg.add_output_port(Constant, "value_as_string", String)

    reg.add_module(File, constantSignatureCallable=file_parameter_hasher)
    reg.add_input_port(File, "value", File)
    reg.add_output_port(File, "value", File)
    reg.add_input_port(File, "name", String, True)
    reg.add_output_port(File, "self", File, True)
    reg.add_input_port(File, "create_file", Boolean, True)
    reg.add_output_port(File, "local_filename", String, True)

    reg.add_module(FileSink)
    reg.add_input_port(FileSink,  "file", File)
    reg.add_input_port(FileSink,  "outputName", String)
    reg.add_input_port(FileSink,  "overrideFile", Boolean)

    reg.add_module(Color)
    reg.add_input_port(Color, "value", Color)
    reg.add_output_port(Color, "value", Color)    

    reg.add_module(StandardOutput)
    reg.add_input_port(StandardOutput, "value", Module)

    reg.add_module(Tuple, configureWidgetType=TupleConfigurationWidget)
    reg.add_output_port(Tuple, 'self', Tuple)

    reg.add_module(TestTuple)
    reg.add_input_port(TestTuple, 'tuple', [Integer, String])

    reg.add_module(Untuple, configureWidgetType=UntupleConfigurationWidget)
    reg.add_input_port(Untuple, 'tuple', Tuple)

    reg.add_module(ConcatenateString)
    for i in xrange(ConcatenateString.fieldCount):
        j = i+1
        port = "str%s" % j
        reg.add_input_port(ConcatenateString, port, String)
    reg.add_output_port(ConcatenateString, "value", String)

    reg.add_module(List)

    reg.add_input_port(List, "head", Module)
    reg.add_input_port(List, "tail", List)
    reg.add_output_port(List, "value", List)

    reg.add_module(Null)

    reg.add_module(PythonSource,
                    configureWidgetType=PythonSourceConfigurationWidget)
    reg.add_input_port(PythonSource, 'source', String, True)
    reg.add_output_port(PythonSource, 'self', Module)

    reg.add_module(SmartSource,
                    configureWidgetType=PythonSourceConfigurationWidget)
    reg.add_input_port(SmartSource, 'source', String, True)

    reg.add_module(Unzip)
    reg.add_input_port(Unzip, 'archive_file', File)
    reg.add_input_port(Unzip, 'filename_in_archive', String)
    reg.add_output_port(Unzip, 'file', File)

    reg.add_module(Variant)

    # initialize the sub_module modules, too
    import core.modules.sub_module
    core.modules.sub_module.initialize(*args, **kwargs)

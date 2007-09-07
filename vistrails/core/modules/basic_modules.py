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

from core.modules import module_configure
from core.modules import module_registry
from core.modules import port_configure
from core.modules import vistrails_module
from core.modules.vistrails_module import Module, new_module, \
     NotCacheable, ModuleError
from core.modules.tuple_configuration import TupleConfigurationWidget
import core.packagemanager
import core.system
import os
import zipfile
import urllib

_reg = module_registry.registry

###############################################################################

class Constant(Module):
    """Base class for all Modules that represent a constant value of
    some type."""
    
    def __init__(self):
        Module.__init__(self)
        self.value = None
        self.addRequestPort("value_as_string", self.valueAsString)

    def compute(self):
        """Constant.compute() only checks validity (and presence) of
        input value."""
        if self.hasInputFromPort("value"):
            v = self.getInputFromPort("value")
        else:
            v = self.value

        # TODO: This is a bogus check ('except: pass' is bad). Fix it.
        try:
            b = isinstance(v, self.convert)
        except:
            pass
        else:
            if not b:
                raise Exception("Value should be a %s" % self.convert.__name__)
        self.setResult("value", v)

    def setValue(self, v):
        self.value = self.convert(v)
    
#     def __str__(self):
#         if not self.upToDate:
#             return str(self.value)
#         else:
#             return str(self.get_output("value"))

    def valueAsString(self):
        return str(self.value)

_reg.add_module(Constant)


def new_constant(name, conversion):
    """new_constant(conversion) -> Module

    new_constant dynamically creates a new Module derived from Constant
    that with a given conversion function. conversion is a python
    callable that takes a string and returns a python value of the type
    that the class should hold.

    This is the quickest way to create new Constant Modules."""
    
    def __init__(self):
        Constant.__init__(self)
        self.convert = conversion
    
    m = new_module(Constant, name, {'__init__': __init__})
    module_registry.registry.add_module(m)
    module_registry.registry.add_input_port(m, "value", m)
    module_registry.registry.add_output_port(m, "value", m)
    return m

def bool_conv(x):
    s = str(x).upper()
    if s == 'TRUE':
        return True
    if s == 'FALSE':
        return False
    raise ValueError('Boolean from String in VisTrails should be either \
"true" or "false"')

def int_conv(x):
    if x.startswith('0x'):
        return int(x, 16)
    else:
        return int(x)

Boolean = new_constant('Boolean' , bool_conv)
Float   = new_constant('Float'   , float)
Integer = new_constant('Integer' , int_conv)
String  = new_constant('String'  , str)
_reg.add_output_port(Constant, "value_as_string", String)

##############################################################################

class File(Module):
    """File is a VisTrails Module that represents a file stored on a
    file system local to the machine where VisTrails is running."""

    def compute(self):
        self.checkInputPort("name")
        n = self.getInputFromPort("name")
        if (self.hasInputFromPort("create_file") and
            self.getInputFromPort("create_file")):
            core.system.touch(n)
        self.name = n
        if not os.path.isfile(n):
            raise ModuleError(self, "File '%s' not existent" % n)
        self.setResult("local_filename", self.name)

_reg.add_module(File)
_reg.add_input_port(File, "name", String)
_reg.add_output_port(File, "self", File)
_reg.add_input_port(File, "create_file", Boolean)
_reg.add_output_port(File, "local_filename", String, True)

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

_reg.add_module(FileSink)
_reg.add_input_port(FileSink,  "file", File)
_reg.add_input_port(FileSink,  "outputName", String)
_reg.add_input_port(FileSink,  "overrideFile", Boolean)

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

_reg.add_module(StandardOutput)
_reg.add_input_port(StandardOutput, "value", Module)

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
        self.srcPortsOrder = []

    def compute(self):
        values = tuple([self.getInputFromPort(p)
                        for p in self.srcPortsOrder])
        self.setResult("value", values)
        
_reg.add_module(Tuple, configureWidgetType=TupleConfigurationWidget)
_reg.add_output_port(Tuple, 'self', Tuple)

class TestTuple(Module):
    def compute(self):
        pair = self.getInputFromPort('tuple')
        print pair
        
_reg.add_module(TestTuple)
_reg.add_input_port(TestTuple, 'tuple', [Integer, String])


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
_reg.add_module(ConcatenateString)
for i in xrange(ConcatenateString.fieldCount):
    j = i+1
    port = "str%s" % j
    _reg.add_input_port(ConcatenateString, port, String)
_reg.add_output_port(ConcatenateString, "value", String)

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

_reg.add_module(List)

_reg.add_input_port(List, "head", Module)
_reg.add_input_port(List, "tail", List)
_reg.add_output_port(List, "value", List)

##############################################################################

# TODO: Null should be a subclass of Constant?
class Null(Module):
    """Null is the class of None values."""
    
    def compute(self):
        self.setResult("value", None)

_reg.add_module(Null)

##############################################################################

class PythonSource(NotCacheable, Module):
    """PythonSource is a Module that executes an arbitrary piece of
    Python code.
    
    It is especially useful for one-off pieces of 'glue' in a
    pipeline."""

    def run_code(self, code_str,
                 use_input=False,
                 use_output=False):
        """run_code runs a piece of code as a VisTrails module.
        use_input and use_output control whether to use the inputport
        and output port dictionary as local variables inside the
        execution."""
        
        def fail(msg):
            raise ModuleError(self, msg)
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
        locals_.update({'fail': fail,
                        'package_manager': _m,
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

_reg.add_module(PythonSource,
                configureWidgetType=module_configure.PythonSourceConfigurationWidget)
_reg.add_input_port(PythonSource, 'source', String, True)

##############################################################################

class TestPortConfig(Module):
    
    def compute(self):
        pass
    
_reg.add_module(TestPortConfig)
_reg.add_input_port(TestPortConfig,
                 'ColorPort', [Float,Float,Float],
                 False, port_configure.ColorConfigurationWidget)
_reg.add_input_port(TestPortConfig, 'IntegerPort', Integer)

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

_reg.add_module(Unzip)
_reg.add_input_port(Unzip, 'archive_file', File)
_reg.add_input_port(Unzip, 'filename_in_archive', String)
_reg.add_output_port(Unzip, 'file', File)

##############################################################################
    
class Variant(Module):
    """
    Variant is tracked internally for outputing a variant type on
    output port. For input port, Module type should be used
    
    """
    pass
    
_reg.add_module(Variant)

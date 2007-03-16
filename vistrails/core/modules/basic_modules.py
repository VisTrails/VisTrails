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
from core.modules.vistrails_module import Module, newModule, \
     NotCacheable, ModuleError
from core.modules.tuple_configuration import TupleConfigurationWidget
import core.packagemanager
import core.system
import os
import zipfile

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
#             return str(self.getOutput("value"))

    def valueAsString(self):
        return str(self.value)

_reg.addModule(Constant)


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
    
    m = newModule(Constant, name, {'__init__': __init__})
    module_registry.registry.addModule(m)
    module_registry.registry.addInputPort(m, "value", m)
    module_registry.registry.addOutputPort(m, "value", m)
    return m

def bool_conv(x):
    s = str(x).upper()
    if s == 'TRUE':
        return True
    if s == 'FALSE':
        return False
    raise ValueError('Boolean from String in VisTrails should be either \
"true" or "false"')

Boolean = new_constant('Boolean' , bool_conv)
Float   = new_constant('Float'   , float)
Integer = new_constant('Integer' , int)
String  = new_constant('String'  , str)
_reg.addOutputPort(Constant, "value_as_string", String)

##############################################################################

class File(Module):
    """File is a VisTrails Module that represents a file stored on a
    file system local to the machine where VisTrails is running."""

    def compute(self):
        self.checkInputPort("name")
        n = self.getInputFromPort("name")
        self.name = n
        self.setResult("local_filename", self.name)

_reg.addModule(File)
_reg.addInputPort(File, "name", String)
_reg.addOutputPort(File, "self", File)
_reg.addOutputPort(File, "local_filename", String)

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

_reg.addModule(FileSink)
_reg.addInputPort(FileSink,  "file", File)
_reg.addInputPort(FileSink,  "outputName", String)
_reg.addInputPort(FileSink,  "overrideFile", Boolean)

##############################################################################

# class OutputWindow(Module):
    
#     def compute(self):
#         v = self.getInputFromPort("value")
#         from PyQt4 import QtCore, QtGui
#         QtGui.QMessageBox.information(None,
#                                       "VisTrails",
#                                       str(v))

#Removing Output Window because it does not work with current threading
#reg.addModule(OutputWindow)
#reg.addInputPort(OutputWindow, "value",
#                               Module)

##############################################################################

class StandardOutput(NotCacheable, Module):
    """StandardOutput is a VisTrails Module that simply prints the
    value connected on its port to standard output. It is intended
    mostly as a debugging device."""
    
    def compute(self):
        v = self.getInputFromPort("value")
        print v

_reg.addModule(StandardOutput)
_reg.addInputPort(StandardOutput, "value", Module)

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
        
_reg.addModule(Tuple, None, TupleConfigurationWidget)
_reg.addOutputPort(Tuple, 'self', Tuple)

class TestTuple(Module):
    def compute(self):
        pair = self.getInputFromPort('tuple')
        print pair
        
_reg.addModule(TestTuple)
_reg.addInputPort(TestTuple, 'tuple', [Integer, String])


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
        for i in range(self.fieldCount):
            v = i+1
            port = "str%s" % v
            if self.hasInputFromPort(port):
                inp = self.getInputFromPort(port)
                result += inp
        self.setResult("value", result)
_reg.addModule(ConcatenateString)
for i in range(ConcatenateString.fieldCount):
    j = i+1
    port = "str%s" % j
    _reg.addInputPort(ConcatenateString, port, String)
_reg.addOutputPort(ConcatenateString, "value", String)

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

_reg.addModule(List)

_reg.addInputPort(List, "head", Module)
_reg.addInputPort(List, "tail", List)
_reg.addOutputPort(List, "value", List)

##############################################################################

# TODO: Null should be a subclass of Constant?
class Null(Module):
    """Null is the class of None values."""
    
    def compute(self):
        self.setResult("value", None)

_reg.addModule(Null)

##############################################################################

class PythonSource(NotCacheable, Module):
    """PythonSource is a Module that executes an arbitrary piece of
    Python code.
    
    It is especially useful for one-off pieces of 'glue' in a
    pipeline."""
    
    def compute(self):
        def fail(msg):
            raise ModuleError(self, msg)
        import urllib
        s = urllib.unquote(str(self.forceGetInputFromPort('source', '')))
        inputDict = dict([(k, self.getInputFromPort(k))
                          for k in self.inputPorts])
        outputDict = dict([(k, None)
                           for k in self.outputPorts])
        locals_ = locals()
        locals_.update(inputDict)
        locals_.update(outputDict)
        _m = core.packagemanager.get_package_manager()
        locals_.update({'fail': fail,
                        'package_manager': _m,
                        'self': self})
        del locals_['source']
        exec s in globals(), locals_
        for k in outputDict.iterkeys():
            if locals_[k] != None:
                self.setResult(k, locals_[k])

_reg.addModule(PythonSource,
              None, module_configure.PythonSourceConfigurationWidget)
_reg.addInputPort(PythonSource, 'source', String, True)

##############################################################################

class TestPortConfig(Module):
    
    def compute(self):
        pass
    
_reg.addModule(TestPortConfig)
_reg.addInputPort(TestPortConfig,
                 'ColorPort', [Float,Float,Float],
                 False, port_configure.ColorConfigurationWidget)
_reg.addInputPort(TestPortConfig, 'IntegerPort', Integer)

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

_reg.addModule(Unzip)
_reg.addInputPort(Unzip, 'archive_file', File)
_reg.addInputPort(Unzip, 'filename_in_archive', String)
_reg.addOutputPort(Unzip, 'file', File)

##############################################################################
    
class Variant(Module):
    """
    Variant is tracked internally for outputing a variant type on
    output port. For input port, Module type should be used
    
    """
    pass
    
_reg.addModule(Variant)

"""basic_modules defines basic VisTrails Modules that are used in most
pipelines."""

from core.modules import module_configure
from core.modules import module_registry
from core.modules import module_utils
from core.modules import port_configure
from core.modules import vistrails_module
import core.system
import os

###############################################################################

class Constant(vistrails_module.Module):
    """Base class for all Modules that represent a constant value of
    some type."""
    
    def __init__(self):
        vistrails_module.Module.__init__(self)
        self.value = None
        self.addRequestPort("value_as_string", self.valueAsString)

    def compute(self):
        """Constant.compute() only checks validity (and presence) of
        input value."""
        if self.hasInputFromPort("value"):
            v = self.getInputFromPort("value")
        else:
            v = self.value
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
    
    def __str__(self):
        if not self.upToDate:
            return str(self.value)
        else:
            return str(self.getOutput("value"))

    def valueAsString(self):
        return str(self)

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
    
    m = vistrails_module.newModule(Constant, name, {'__init__': __init__})
    module_registry.registry.addModule(m)
    module_registry.registry.addInputPort(m, "value", m)
    module_registry.registry.addOutputPort(m, "value", m)
    return m


class File(vistrails_module.Module):
    """File is a VisTrails Module that represents a file stored on a
    file system local to the machine where VisTrails is running."""

    def compute(self):
        n = self.getInputFromPort("name")
        self.name = n

    def __str__(self):
        return "file"

class FileSink(vistrails_module.Module):
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
                    raise vistrails_module.ModuleError(self, v2)
            else:
                msg = "Could not create file '%s': %s" % (v2, e)
                raise vistrails_module.ModuleError(self, msg)


# class OutputWindow(vistrails_module.Module):
    
#     def compute(self):
#         v = self.getInputFromPort("value")
#         from PyQt4 import QtCore, QtGui
#         QtGui.QMessageBox.information(None,
#                                       "VisTrails",
#                                       str(v))


class StandardOutput(vistrails_module.Module):
    """StandardOutput is a VisTrails Module that simply prints the
    value connected on its port to standard output. It is intended
    mostly as a debugging device."""
    
    def compute(self):
        v = self.getInputFromPort("value")
        print v

# Tuple will be reasonably magic right now. We'll integrate it better
# with vistrails later.
# TODO: Check Tuple class, test, integrate.
class Tuple(vistrails_module.Module):
    """Tuple represents a tuple of values. Tuple might not be well
    integrated with the rest of VisTrails, so don't use it unless
    you know what you're doing."""

    def compute(self):
        values = tuple([self.getInputFromPort(i) for i in range(self.length)])
        self.setResult("value", values)

# TODO: Create a better Module for ConcatenateString.
class ConcatenateString(vistrails_module.Module):
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
                print inp
                result += inp
        self.setResult("value", result)


# TODO: Create a better Module for List.
class List(vistrails_module.Module):
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

# TODO: Null should be a subclass of Constant?
class Null(vistrails_module.Module):
    """Null is the class of None values."""
    
    def compute(self):
        self.setResult("value", None)

class PythonSource(vistrails_module.Module):
    """PythonSource is a Module that executes an arbitrary piece of
    Python code.
    
    It is especially useful for one-off pieces of 'glue' in a
    pipeline."""
    
    def compute(self):
        import urllib
        exec urllib.unquote(str(self.forceGetInputFromPort('source', '')))

class TestPortConfig(vistrails_module.Module):
    
    def compute(self):
        pass
    
###############################################################################

reg = module_registry.registry

reg.addModule(Constant)

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

reg.addOutputPort(Constant, "value_as_string", String)

reg.addModule(Null)

reg.addModule(File)
reg.addInputPort(File, "name", String)
reg.addOutputPort(File, "self", File)

reg.addModule(FileSink)
reg.addInputPort(FileSink,  "file", File)
reg.addInputPort(FileSink,  "outputName", String)
reg.addInputPort(FileSink,  "overrideFile", Boolean)

#Removing Output Window because it does not work with current threading
#reg.addModule(OutputWindow)
#reg.addInputPort(OutputWindow, "value",
#                               vistrails_module.Module)

reg.addModule(StandardOutput)
reg.addInputPort(StandardOutput, "value", vistrails_module.Module)

reg.addModule(PythonSource,
              None, module_configure.PythonSourceConfigurationWidget)
reg.addInputPort(PythonSource, 'source', String, True)

reg.addModule(TestPortConfig)
reg.addInputPort(TestPortConfig,
                 'ColorPort', [Float,Float,Float],
                 False, port_configure.ColorConfigurationWidget)
reg.addInputPort(TestPortConfig, 'IntegerPort', Integer)

reg.addModule(Tuple)
reg.addModule(ConcatenateString)
for i in range(ConcatenateString.fieldCount):
    j = i+1
    port = "str%s" % j
    reg.addInputPort(ConcatenateString, port, String)
reg.addOutputPort(ConcatenateString, "value", String)

reg.addModule(List)
reg.addInputPort(List, "head", vistrails_module.Module)
reg.addInputPort(List, "tail", List)
reg.addOutputPort(List, "value", List)

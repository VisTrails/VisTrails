# from modules

from core.modules import module_registry
from core.modules import vistrails_module
from core.modules import module_utils
from core.modules import module_configure
from core.modules import port_configure
import os
import core.system

################################################################################

class Constant(vistrails_module.Module):
    
    def __init__(self):
        vistrails_module.Module.__init__(self)
        self.value = None
        self.addRequestPort("value_as_string", self.valueAsString)

    def compute(self):
        """Constant.compute() only checks validity (and presence) of input value."""
        if self.hasInputFromPort("value"):
            v = self.getInputFromPort("value")
        else:
            v = self.value
        if not isinstance(v, self.convert):
            raise Exception("Value should be a %s" % self.convert.__name__)
        self.setResult("value", v)

    def setValue(self, v):
        self.value = self.convert(v)
    
    def __str__(self):
        return str(self.getOutput("value"))

    def valueAsString(self):
        return str(self)

def newConstant(name, conversion):
    def __init__(self):
        Constant.__init__(self)
        self.convert = conversion
    m = vistrails_module.newModule(Constant, name, {'__init__': __init__})
    module_registry.registry.addModule(m)
    module_registry.registry.addInputPort(m, "value", m)
    module_registry.registry.addOutputPort(m, "value", m)
    return m


class File(vistrails_module.Module):

    def compute(self):
        n = self.getInputFromPort("name")
        self.name = n

    def __str__(self):
        return "file"

import shutil

class FileSink(vistrails_module.Module):

    def compute(self):
        v1 = self.getInputFromPort("file")
        v2 = self.getInputFromPort("outputName")
        try:
            system.link_or_copy(v1.name, v2)
        except OSError, e:
            if (self.hasInputFromPort("overrideFile") and
                self.getInputFromPort("overrideFile")):
                try:
                    os.unlink(v2)
                    system.link_or_copy(v1.name, v2)
                except OSError:
                    raise vistrails_module.ModuleError(self, "(override true) Could not create file '%s'" % v2)
            else:
                raise vistrails_module.ModuleError(self, "Could not create file '%s': %s" % (v2, e))


class OutputWindow(vistrails_module.Module):
    
    def compute(self):
        v = self.getInputFromPort("value")
        from PyQt4 import QtCore, QtGui
        QtGui.QMessageBox.information(None,
                                      "VisTrails",
                                      str(v))


class StandardOutput(vistrails_module.Module):
    def compute(self):
        v = self.getInputFromPort("value")
        print v
# Tuple will be reasonably magic right now. We'll integrate it better
# with vistrails later.
class Tuple(vistrails_module.Module):

    def compute(self):
        values = tuple([self.getInputFromPort(i) for i in range(self.length)])
        self.setResult("value", values)

class ConcatenateString(vistrails_module.Module):

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


class List(vistrails_module.Module):

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

class Null(vistrails_module.Module):
    def compute(self):
        self.setResult("value", None)

class PythonSource(vistrails_module.Module):
    
    def compute(self):
        import urllib
        exec urllib.unquote(str(self.forceGetInputFromPort('source', '')))

class TestPortConfig(vistrails_module.Module):
    
    def compute(self):
        pass
    
################################################################################

module_registry.registry.addModule(Constant)

Boolean = newConstant('Boolean' , bool)
Float   = newConstant('Float'   , float)
Integer = newConstant('Integer' , int)
String  = newConstant('String'  , str)

module_registry.registry.addOutputPort(Constant, "value_as_string", String)

module_registry.registry.addModule(Null)

module_registry.registry.addModule(File)
module_registry.registry.addInputPort(File, "name", String)
module_registry.registry.addOutputPort(File, "self", File)

module_registry.registry.addModule(FileSink)
module_registry.registry.addInputPort(FileSink,  "file", File)
module_registry.registry.addInputPort(FileSink,  "outputName", String)
module_registry.registry.addInputPort(FileSink,  "overrideFile", Boolean)

module_registry.registry.addModule(OutputWindow)
module_registry.registry.addInputPort(OutputWindow, "value", vistrails_module.Module)

module_registry.registry.addModule(StandardOutput)
module_registry.registry.addInputPort(StandardOutput, "value", vistrails_module.Module)

module_registry.registry.addModule(PythonSource,
                                   None,
                                   module_configure.PythonSourceConfigurationWidget)
module_registry.registry.addInputPort(PythonSource, 'source', String, True)

module_registry.registry.addModule(TestPortConfig)
module_registry.registry.addInputPort(TestPortConfig,
                                      'ColorPort',
                                      [Float,Float,Float],
                                      False,
                                      port_configure.ColorConfigurationWidget)
module_registry.registry.addInputPort(TestPortConfig,
                                      'IntegerPort',
                                      Integer)

module_registry.registry.addModule(Tuple)
module_registry.registry.addModule(ConcatenateString)
for i in range(ConcatenateString.fieldCount):
    j = i+1
    port = "str%s" % j
    module_registry.registry.addInputPort(ConcatenateString, port, String)
module_registry.registry.addOutputPort(ConcatenateString, "value", String)

module_registry.registry.addModule(List)
module_registry.registry.addInputPort(List, "head", vistrails_module.Module)
module_registry.registry.addInputPort(List, "tail", List)
module_registry.registry.addOutputPort(List, "value", List)

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
class NeedsInputPort(Exception):
    def __init__(self, obj, port):
        self.obj = obj
        self.port = port
    def __str__(self):
        return "Module %s needs port %s" % (self.obj, self.port)


class IncompleteImplementation(Exception):
    def __str__(self):
        return "Module has incomplete implementation"


class MissingModule(Exception):
    pass


class ModuleError(Exception):
    
    def __init__(self, module, errormsg):
        Exception.__init__(self, errormsg)
        self.module = module
        self.msg = errormsg

################################################################################

class Module(object):

    def __init__(self):
        self.inputPorts = {}
        self.outputPorts = {}
        self.outputRequestTable = {}
        self.upToDate = False
        self.setResult("self", self) # every object can return itself

    def update(self):
        if self.upToDate:
            return
        if not hasattr(self, "logging"):
            for connectorList in self.inputPorts.itervalues():
                for connector in connectorList:
                    connector.obj.update()
            self.compute()
            self.upToDate = True
        else:
            # Updates upstream modules
            self.logging.beginUpdate(self)
            for connectorList in self.inputPorts.itervalues():
                for connector in connectorList:
                    connector.obj.update()
            self.logging.beginCompute(self)
            self.compute()
            self.upToDate = True
            self.logging.endUpdate(self)
            self.logging.signalSuccess(self)

    def checkInputPort(self, name):
        """checkInputPort(name) -> None.
Makes sure input port 'name' is filled."""
        if not self.hasInputFromPort(name):
            raise ModuleError(self, "'%s' is a mandatory port" % name)

    def compute(self):
        pass

    def addRequestPort(self, port, f):
        self.outputRequestTable[port] = f

    def requestOutputFromPort(self, port):
        if not self.outputRequestTable.has_key(port):
            raise ModuleError(("On-demand request port %s not present in table" %
                               port))
        else:
            v = self.outputRequestTable[port]()
            return v

    def setResult(self, port, value):
        self.outputPorts[port] = value

    def getOutput(self, port):
        if self.outputPorts.has_key(port) or not self.outputPorts[port]:
            return self.outputPorts[port]
        return self.requestOutputFromPort(port)

    def getInputFromPort(self, inputPort):
        if not self.inputPorts.has_key(inputPort):
            raise Exception("Missing value from port %s" % inputPort)
        return self.inputPorts[inputPort][0]()

    def hasInputFromPort(self, inputPort):
        return self.inputPorts.has_key(inputPort)

    def __str__(self):
        return "VisTrails_Module"

    def annotate(self, d):
        self.logging.annotate(self, d)

    def forceGetInputFromPort(self, inputPort, defaultValue=None):
        if self.hasInputFromPort(inputPort):
            return self.getInputFromPort(inputPort)
        else:
            return defaultValue

    def setInputPort(self, inputPort, conn):
        if self.inputPorts.has_key(inputPort):
            self.inputPorts[inputPort].append(conn)
        else:
            self.inputPorts[inputPort] = [conn]

    def getInputListFromPort(self, inputPort):
        if not self.inputPorts.has_key(inputPort):
            raise Exception("Missing value from port %s" % inputPort)
        return [connector() for connector in self.inputPorts[inputPort]]

    def forceGetInputListFromPort(self, inputPort):
        if not self.inputPorts.has_key(inputPort):
            return []
        return [connector() for connector in self.inputPorts[inputPort]]

    ### Set an output port before hand that it is neccesary for the computation
    def enableOutputPort(self, outputPort):
        if outputPort!='self':
            self.setResult(outputPort, None)

################################################################################

class ModuleConnector(object):
    def __init__(self, obj, port):
        self.obj = obj
        self.port = port
    def __call__(self):
        return self.obj.getOutput(self.port)

def newModule(baseModule, name, dict={}):
    assert issubclass(baseModule, Module)
    return type(name, (baseModule, ), dict)

# This is the gist of how type() works. The example is run from a python
# toplevel

# >>> class X(object):
# ...     def f(self): return 3
# ... 
# >>> a = X()
# >>> a.f()
# 3
# >>> Y = type('Y', (X, ), {'g': lambda x : 4})
# >>> b = Y()
# >>> b.f()
# 3
# >>> b.g()
# 4
# >>> Z = type('Z', (X, ), {'f': lambda x : 4} )
# >>> c = Z()
# >>> c.f()
# 4

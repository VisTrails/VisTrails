""" This is the core classes for the general workflow model

The structures can hold a description of a workflow and lists of operations.

This file implements:
 Annotation
 Parameter
 Module
 Connection
 Pipeline
 Port
 Operation
 Service
"""

class Annotation:
    """
    annotation
    """
    def __init__(self, key='', value=''):
        self.key = key
        self.value = value
        self.annotations = [] # list of annotations
    def __eq__(self, other):
        """ equal if keys are equal """
        return self.key == other.key

class Parameter:
    """
    module parameter
    """
    def __init__(self, name, value='', type=''):
        self.name = name      # parameter name
        self.value = value    # value
        self.type = type      # value type type/class (actually redundant)
        self.annotations = [] # list of annotations

class Module:
    """
    workflow module
    """
    def __init__(self, name = 'New', package = '',
                 version = '', type = 'Module'):
        self.name = name       # module name
        self.package = package # package that the 'type' is in
        self.version = version # version of the package
        self.type = type       # module type
        self.annotations = []  # list of annotations
        self.parameters = []   # list of parameters
        self.up = []           # input  modules (redundant)
        self.down = []         # output modules (redundant)

class Connection:
    """
    A connection between modules
    """
    def __init__(self, startModule=None, endModule=None, \
                       startPort='', endPort=''):
            self.startModule = startModule # reference to startmodule
            self.endModule = endModule     # reference to endmodule
            self.startPort = startPort
            self.endPort = endPort
            self.annotations = []           # list of annotations

class Pipeline:
    """
    A representation of a pipeline 
    """
    def __init__(self, name='', type='', version='', source=''):
        self.name        = name       # textual representation of pipeline
        self.source      = source     # location of source
        self.type        = type       # source format 
        self.version     = version    # version of source format
        self.modules     = []         # list of modules
        self.connections = []         # list of connections
        self.annotations = []         # list of annotations

outPort = False
inPort = True
class Port:
    """
    module port
    """
    def __init__(self, name, type=None, kind=inPort):
        self.name = name      # port name
        self.type = type      # port type/class
        self.kind = kind      # inPort/outPort
        self.annotations = [] # list of annotations

class Operation:
    """
    An operation
    """
    def __init__(self, name):
        self.name = name      # operation name
        self.ports = []       # list of ports
        self.annotations = [] # list of annotations

class Service:
    """
    A service representation
    """
    def __init__(self, name='', source='', type='', version=''):
        self.name        = name       # textual representation of pipeline
        self.source      = source     # location of source
        self.type        = type       # source format (namespace)
        self.version     = version    # version of source format
        self.operations  = []         # list of operations
        self.annotations = []         # list of annotations

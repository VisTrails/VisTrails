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

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

from db.domain import DBOpmGraph

class OpmGraph(DBOpmGraph):
    """ Class that stores info for generating OPM Provenance. """

    def __init__(self, *args, **kwargs):
        if 'log' in kwargs:
            self.log = kwargs['log']
            del kwargs['log']
        else:
            self.log = None
        if 'workflow' in kwargs:
            self.workflow = kwargs['workflow']
            del kwargs['workflow']
        elif 'pipeline' in kwargs:
            self.workflow = kwargs['pipeline']
            del kwargs['pipeline']
        else:
            self.workflow = None
        if 'registry' in kwargs:
            self.registry = kwargs['registry']
            del kwargs['registry']
        else:
            self.registry = None
        if 'version' in kwargs:
            self.version = kwargs['version']
            del kwargs['version']
        else:
            self.version = None
        DBOpmGraph.__init__(self, *args, **kwargs)

    def __copy__(self):
        return self.do_copy()

    def do_copy(self):
        cp = DBOpmGraph.__copy__(self)
        cp.__class__ = OpmGraph
        cp.log = self.log
        cp.workflow = self.workflow
        cp.version = self.version
        cp.registry = self.registry
        return cp

    @staticmethod
    def convert(_graph):
        if _graph.__class__ == OpmGraph:
            return
        _graph.__class__ = OpmGraph

    ##########################################################################
    # Properties

    # No need to do properties right now...


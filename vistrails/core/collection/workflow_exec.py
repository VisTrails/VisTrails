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
from entity import Entity

class WorkflowExecEntity(Entity):
    type_id = 3

    def __init__(self, workflow_exec=None):
        Entity.__init__(self)
        self.id = None
        self.update(workflow_exec)

    @staticmethod
    def load(*args):
        entity = WorkflowExecEntity()
        Entity.load(entity, *args)
        return entity

    def update(self, workflow_exec):
        self.workflow_exec = workflow_exec
        if self.workflow_exec is not None:
            self.name = "%s" % self.workflow_exec.db_ts_start
            self.user = self.workflow_exec.user
            self.mod_time = \
                self.workflow_exec.ts_end.strftime('%d %b %Y %H:%M:%S') \
                if self.workflow_exec.ts_end else '1 Jan 0000 00:00:00'
            self.create_time = \
                self.workflow_exec.ts_start.strftime('%d %b %Y %H:%M:%S') \
                if self.workflow_exec.ts_start else '1 Jan 0000 00:00:00'
            self.size = len(self.workflow_exec.item_execs)
            self.description = ""
            self.url = 'test'
            self.was_updated = True
        
    # returns boolean, True if search input is satisfied else False
    def match(self, search):
        raise Exception("Not implemented")


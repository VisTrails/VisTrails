############################################################################
##
## Copyright (C) 2006-2010 University of Utah. All rights reserved.
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


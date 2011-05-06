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

class WorkflowEntity(Entity):
    type_id = 2

    def __init__(self, workflow=None):
        Entity.__init__(self)
        self.id = None
        self.update(workflow)

    @staticmethod
    def load(*args):
        entity = WorkflowEntity()
        Entity.load(entity, *args)
        return entity

    def update(self, workflow):
        self.workflow = workflow
        if self.workflow is not None:
            self.name = workflow.name \
            if workflow.name else "Version #" + str(workflow.id)
            self.user = 'testing'
            self.mod_time = 'test'
            self.create_time = 'test'
            self.size = len(self.workflow.modules)
            self.description = ""
            self.url = 'test'
            self.was_updated = True

#             self.name = self.workflow.name
#             self.user = self.workflow.user
#             self.mod_time = self.workflow.py_date
#             self.create_time = self.workflow.py_date
#             self.size = len(self.workflow.modules)
#             self.description = self.workflow.notes
#             self.was_updated = True
        
#     # returns string
#     def get_name(self):
#         raise Exception("Method is abstract")

#     # returns datetime
#     def get_mod_time(self):
#         raise Exception("Method is abstract")

#     # returns datetime
#     def get_create_time(self):
#         raise Exception("Method is abstract")        
    
#     # returns string
#     # FIXME: perhaps this should be a User object at some point
#     def get_user(self):
#         raise Exception("Method is abstract")
    
#     # returns tuple (<entity_type>, <entity_id>)
#     def get_id(self):
#         raise Exception("Method is abstract")

#     # returns integer
#     def get_size(self):
#         raise Exception("Method is abstract")
    
#     # returns possibly empty list of Entity objects
#     def get_children(self):
#         raise Exception("Method is abstract")

#     # returns list of strings representing paths
#     # FIXME: should this be uris for database access?
#     def get_image_fnames(self):
#         raise Exception("Method is abstract")
    
    # returns boolean, True if search input is satisfied else False
    def match(self, search):
        raise Exception("Not implemented")


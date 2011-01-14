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


from core.db.locator import BaseLocator

class Entity(object):
    def __init__(self):
        self.parent = None
        self.children = []
        self.image_fnames = []
        self.was_updated = False

    def load(self, *args):
        (self.id, 
         _, 
         self.name, 
         self.user,
         self.mod_time, 
         self.create_time,
         self.size,
         self.description,
         self.url) = args

    def save(self):
        return (self.id,
                self.type_id,
                self.name,
                self.user,
                self.mod_time,
                self.create_time,
                self.size,
                self.description,
                self.url)

    def _get_start_date(self):
        return self.create_time
    start_date = property(_get_start_date)

    def _get_end_date(self):
        return self.mod_time
    end_date = property(_get_end_date)

#     # returns string
#     def get_name(self):
#         return self.name

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

#     def get_description(self):
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
        raise Exception("Method is abstract")

    def locator(self):
        return BaseLocator.from_url(self.url)


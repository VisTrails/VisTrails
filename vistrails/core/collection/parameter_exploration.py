###############################################################################
##
## Copyright (C) 2011-2014, NYU-Poly.
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

class ParameterExplorationEntity(Entity):
    type_id = 6

    def __init__(self, pe=None):
        Entity.__init__(self)
        self.id = None
        self.update(pe)

    @staticmethod
    def create(*args):
        entity = ParameterExplorationEntity()
        entity.load(*args)
        return entity

    def update(self, pe):
        self.pe = pe
        if self.pe is not None:
            self.name = pe.name
            self.user = pe.user
            self.mod_time = pe.date if pe.date else self.now()
            self.create_time = pe.date if pe.date else self.now()
            self.size = len(pe.functions)
            self.description = ""
            self.url = 'test'
            self.was_updated = True
        
#     # returns string
#     def get_name(self):
#         raise RuntimeError("Method is abstract")

#     # returns datetime
#     def get_mod_time(self):
#         raise RuntimeError("Method is abstract")

#     # returns datetime
#     def get_create_time(self):
#         raise RuntimeError("Method is abstract")
    
#     # returns string
#     # FIXME: perhaps this should be a User object at some point
#     def get_user(self):
#         raise RuntimeError("Method is abstract")
    
#     # returns tuple (<entity_type>, <entity_id>)
#     def get_id(self):
#         raise RuntimeError("Method is abstract")

#     # returns integer
#     def get_size(self):
#         raise RuntimeError("Method is abstract")
    
#     # returns possibly empty list of Entity objects
#     def get_children(self):
#         raise RuntimeError("Method is abstract")

#     # returns list of strings representing paths
#     # FIXME: should this be uris for database access?
#     def get_image_fnames(self):
#         raise RuntimeError("Method is abstract")
    
    # returns boolean, True if search input is satisfied else False
    def match(self, search):
        raise RuntimeError("Not implemented")
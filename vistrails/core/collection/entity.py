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
from core.db.locator import BaseLocator

class Entity(object):
    def __init__(self):
        self.parent = None
        self.children = []
        self.image_fnames = []
        self.was_updated = False
        self.is_open = False

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
        locator = BaseLocator.from_url(self.url)
        return locator


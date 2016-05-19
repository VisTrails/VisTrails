###############################################################################
##
## Copyright (C) 2014-2016, New York University.
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
##  - Neither the name of the New York University nor the names of its
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
from __future__ import division

from vistrails.core.db.locator import BaseLocator
from vistrails.core.system import strftime
from datetime import datetime

class Entity(object):
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S.%f'

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
        self.mod_time = self.timeval(self.mod_time)
        self.create_time = self.timeval(self.create_time)


    def save(self):
        return (self.id,
                self.type_id,
                self.name,
                self.user,
                strftime(self.mod_time, self.DATE_FORMAT),
                strftime(self.create_time, self.DATE_FORMAT),
                self.size,
                self.description,
                self.url)

    def _get_start_date(self):
        return self.create_time
    start_date = property(_get_start_date)

    def _get_end_date(self):
        return self.mod_time
    end_date = property(_get_end_date)

    def now(self):
        return datetime.now()

    def timeval(self, time):
        try:
            return datetime.strptime(time, self.DATE_FORMAT)
        except ValueError:
            # try old format
            try:
                return datetime.strptime(time, '%d %b %Y %H:%M:%S')
            except ValueError:
                # locale or other error
                return self.now()

#     # returns string
#     def get_name(self):
#         return self.name

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

#     def get_description(self):
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
        raise RuntimeError("Method is abstract")

    def locator(self):
        locator = BaseLocator.from_url(self.url)
        return locator


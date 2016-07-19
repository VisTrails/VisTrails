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

from vistrails.core.query import Query
from combined import CombinedSearch

class MultipleSearch(Query):
    # vistrails_to_check { Vistrail: set(version_ids) }
    def __init__(self, search_str=None, pipeline=None, entities_to_check={},
                 use_regex=False):
        self.entities_to_check = entities_to_check
        self.queryPipeline = pipeline
        self.search_str = search_str
        self.use_regex = use_regex
        self.queries = {}
        self.queries_by_vistrail = {}
        self.cur_controller = None

    def setCurrentController(self, controller):
        self.cur_controller = controller

    def run(self):
        for entity, versions_to_check in self.entities_to_check.iteritems():
            query = CombinedSearch(self.search_str, self.queryPipeline, 
                                   versions_to_check, self.use_regex)
            query.run(entity._window.controller, '')
            self.queries[entity] = query
            self.queries_by_vistrail[entity.vistrail] = query

    def match(self, controller, action):
        self.setCurrentController(controller)
        query = self.queries_by_vistrail[controller.vistrail]
        return query.match(controller, action)

    def matchModule(self, version_id, module):
        query = self.queries_by_vistrail[self.cur_controller.vistrail]
        return query.matchModule(version_id, module)
    
    def getResultEntities(self):
        result_entities = []
        for entity, query in self.queries.iteritems():
            versions_to_check = self.entities_to_check[entity]
            result_entity = query.getResultEntity(entity._window.controller,
                                                  versions_to_check)
            if result_entity is not None:
                # needed for workspace results that are temporary...
                result_entity._window = entity._window
                result_entities.append(result_entity)
        return result_entities

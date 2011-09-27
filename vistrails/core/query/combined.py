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

from version import SearchCompiler
from visual import VisualQuery

class CombinedSearch(VisualQuery):
    def __init__(self, search_str=None, pipeline=None, versions_to_check=None):
        VisualQuery.__init__(self, pipeline, versions_to_check)
        self.search_str = search_str

    def run(self, vistrail, name):
        VisualQuery.run(self, vistrail, name)
        self.search_stmt = SearchCompiler(self.search_str).searchStmt

    def match(self, vistrail, action):
        if self.queryPipeline is not None and \
                len(self.queryPipeline.modules) > 0:
            if action.timestep in self.versionDict:
                return self.search_stmt.match(vistrail, action)
            return False
        else:
            return self.search_stmt.match(vistrail, action)

    def matchModule(self, version_id, module):
        if self.queryPipeline is not None and \
                len(self.queryPipeline.modules) > 0:
            return VisualQuery.matchModule(self, version_id, module)
        return True
    
    def getResultEntity(self, vistrail, versions_to_check):
        from core.collection.vistrail import VistrailEntity

        locators = []
        vistrail_entity = None
        for version in versions_to_check:
            if version in vistrail.actionMap:
                action = vistrail.actionMap[version]
                if self.match(vistrail, action):
                    # have a match, get vistrail entity
                    if vistrail_entity is None:
                        vistrail_entity = VistrailEntity()
                        # don't want to add all workflows, executions
                        vistrail_entity.set_vistrail(vistrail)
                    vistrail_entity.add_workflow_entity(version)
                    # FIXME this is not done at the low level but in
                    # Collection class, probably should be reworked
                    vistrail_entity.wf_entity_map[version].parent = \
                        vistrail_entity
        return vistrail_entity


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

from vistrails.core import reportusage

from version import SearchCompiler
from visual import VisualQuery

from vistrails.core.configuration import get_vistrails_configuration

class CombinedSearch(VisualQuery):
    def __init__(self, search_str=None, pipeline=None, versions_to_check=None,
                 use_regex=False):
        VisualQuery.__init__(self, pipeline, versions_to_check)
        self.search_str = search_str
        self.use_regex = use_regex

    def run(self, controller, name):
        if self.search_str:
            reportusage.record_feature('query', controller)
        if self.queryPipeline is not None and \
            len(self.queryPipeline.modules) > 0:
            VisualQuery.run(self, controller, name)
        compiler = SearchCompiler(self.search_str, self.use_regex)
        self.search_stmt = compiler.searchStmt

    def match(self, controller, action):
        if self.queryPipeline is not None and \
                len(self.queryPipeline.modules) > 0:
            if action.timestep in self.versionDict:
                return self.search_stmt.match(controller, action)
            return False
        else:
            return self.search_stmt.match(controller, action)

    def matchModule(self, version_id, module):
        if self.queryPipeline is not None and \
                len(self.queryPipeline.modules) > 0:
            if VisualQuery.matchModule(self, version_id, module):
                return self.search_stmt.matchModule(version_id, module)
            return False
        else:
            return self.search_stmt.matchModule(version_id, module)

    def getResultEntity(self, controller, versions_to_check):
        from vistrails.core.collection.vistrail import VistrailEntity

        vistrail_entity = None
        for version in versions_to_check:
            if version in controller.vistrail.actionMap:
                action = controller.vistrail.actionMap[version]
                if getattr(get_vistrails_configuration(), 'hideUpgrades',
                           True):
                    # Use upgraded version to match
                    action = controller.vistrail.actionMap[
                            controller.vistrail.get_upgrade(action.id, False)]
                if self.match(controller, action):
                    # have a match, get vistrail entity
                    if vistrail_entity is None:
                        vistrail_entity = VistrailEntity()
                        # don't want to add all workflows, executions
                        vistrail_entity.set_vistrail(controller.vistrail)
                    # only tagged versions should be displayed in the workspace
                    tagged_version = controller.get_tagged_version(version)
                    vistrail_entity.add_workflow_entity(tagged_version)
                    # FIXME this is not done at the low level but in
                    # Collection class, probably should be reworked
                    vistrail_entity.wf_entity_map[tagged_version].parent = \
                        vistrail_entity
        return vistrail_entity

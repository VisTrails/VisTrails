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

import copy
import os.path
from vistrails.core.system import current_user, current_time
from vistrails.core.mashup.alias import Alias
from vistrails.core.mashup.component import Component
from vistrails.core.mashup.mashup import Mashup

class MashupController(object):
    def __init__(self, originalController, vt_controller, vt_version, mshptrail=None):
        self.vtController = vt_controller
        self.originalController = originalController
        self.vtVersion = vt_version
        self.vtPipeline = self.vtController.vistrail.getPipeline(self.vtVersion)
        self.vtPipeline.validate()
        self.mshptrail = mshptrail
        self.id_scope = mshptrail.id_scope
        self.currentVersion = -1
        self.currentMashup = None
        self._changed = False

    def setChanged(self, on):
        self._changed = on
        self.originalController.set_changed(True)
        
    def setCurrentVersion(self, version):
        self.currentVersion = version
        self.vtPipeline = self.vtController.vistrail.getPipeline(self.vtVersion)
        if version > -1:
            self.currentMashup = self.mshptrail.getMashup(version)
            self.updatePipelineAliasesFromCurrentMashup()
            
    def getVistrailParam(self, alias):
        if self.vtPipeline:
            return self.vtPipeline.db_get_object(alias.component.vttype,
                                                  alias.component.vtid)
        return None
    
    def execute(self, params):
        if self.vtPipeline and self.vtController:
            mashup_id = self.mshptrail.id
            mashup_version = self.currentVersion
            reason = "mashup::%s::%s"%(str(mashup_id), mashup_version)
            result = self.vtController.execute_current_workflow(custom_params=params,
                                                              reason=reason)
            self.originalController.set_changed(True)
            return result
        return ([], False)
            
    def updateCurrentTag(self, name):
        if self.mshptrail.changeTag(self.currentVersion, name, current_user(),
                                 current_time()):
            self.setChanged(True)
            return True
        else:
            return False
    
    def moveTag(self, from_version, to_version, name):
        tag = self.mshptrail.getTagForActionId(from_version)
        if tag:
            self.mshptrail.removeTagByActionId(from_version)
            self.mshptrail.addTag(to_version, tag, user=current_user(),
                                  date=current_time())
            
    def getCurrentTag(self):
        return self.mshptrail.getTagForActionId(self.currentVersion)
    
    def versionHasTag(self, version):
        return self.mshptrail.hasTagForActionId(version)
    
    def hasTagWithName(self, name):
        return self.mshptrail.hasTagWithName(name)
    
    def getVistrailName(self):
        name = ''
        locator = self.currentMashup.vtid
        if locator is not None:
            if locator.name is None:
                name = ''
            else:
                name = os.path.split(locator.name)[1]
            if name == '':
                name = self.controller.vtController.name
        return name
        
    def resetVistrailPipeline(self):
        self.vtController.change_selected_version(self.vtVersion)
    
    def getVistrailWorkflowTag(self):
        return self.vtController.get_pipeline_name(self.vtVersion)
    
    def reorderAliases(self, new_order):
        if self.currentMashup:
            new_aliases = []
            pos = 0
            for old_pos in new_order:
                alias = self.currentMashup.alias_list[old_pos].do_copy(
                               new_ids=True, id_scope=self.mshptrail.id_scope,
                               id_remap={})
                alias.component.pos = pos
                new_aliases.append(alias)
                pos += 1
            return self.createMashupVersion(new_aliases, quiet=False)
                
    def updateAlias(self, alias):
        """updateAlias(alias)-> long
        This will create a version with an alias change (can't be a position
        change). Position changes are taken care in reorderAliases method. 
        
        """
        #print " controller updateAlias ", alias
        new_aliases = []

        if self.currentMashup:
            for a in self.currentMashup.alias_list:
                if a.id != alias.id:
                    calias = a.do_copy(new_ids=True,
                                       id_scope=self.mshptrail.id_scope,
                                       id_remap={})
                else:
                    #print "found alias: ", a
                    calias = alias.do_copy(new_ids=True,
                                           id_scope=self.mshptrail.id_scope,
                                           id_remap={})
                new_aliases.append(calias)
        return self.createMashupVersion(new_aliases, quiet=False)
        
    def updateAliasFromParam(self, param):
        add_alias = True
        new_aliases = []
        pos = 0
        for alias in self.currentMashup.alias_list:
            if alias.component.vtid != param.id:
                calias = alias.do_copy(new_ids=True,
                                       id_scope=self.mshptrail.id_scope,
                                       id_remap={})
                calias.component.pos = pos
                new_aliases.append(calias)
                pos += 1
            else:
                #print "found alias: ", alias
                add_alias = False
                if param.alias != '':
                    new_alias = alias.do_copy(new_ids=True,
                                              id_scope=self.mshptrail.id_scope,
                                              id_remap={})
                    new_alias.name = param.alias
                    new_aliases.append(new_alias)
                    pos += 1
        if add_alias:
            parameter = self.vtPipeline.db_get_object(param.dbtype, param.id)
            cid = self.id_scope.getNewId('mashup_component')
            aid = self.id_scope.getNewId('mashup_alias')
            component = Component(cid, parameter.vtType, 
                                  parameter.real_id, param.parent_dbtype, 
                                  param.parent_id,
                                  param.mId, parameter.type, 
                                  parameter.strValue, parameter.pos, 
                                  pos, "")
            alias = Alias(aid, param.alias, component) 
            new_aliases.append(alias)
            self.vtPipeline.add_alias(param.alias, param.type, param.id,
                                      param.parent_dbtype, param.parent_id,
                                      param.mId)
        else:
            self.vtPipeline.change_alias(param.alias, param.type, param.id,
                                         param.parent_dbtype, param.parent_id,
                                         param.mId)
        
        return self.createMashupVersion(new_aliases, quiet=False)
        
    def updateAliasesFromPipeline(self, pipeline):
        """updateAliasesFromPipeline(self, pipeline) -> long
        This will generate a new mashup by updating the aliases of the current 
        mashup according to the aliases in a pipeline. This assumes that the 
        mashup's current aliases are different from pipeline aliases by at most 
        one change (eg., an alias rename, an alias addition, an alias removal)
        
        """
        pip_aliases = pipeline.aliases.keys()
        mashup_aliases = [a.name for a in self.currentMashup.alias_list]
        new_aliases = []
        if len(pip_aliases) == len(mashup_aliases):
            #an alias probably changed its name or its value    
            old_a = None
            new_a = None
            for a in self.currentMashup.alias_list:
                if a.name not in pip_aliases:
                    old_a = a.do_copy(new_ids=True,
                                      id_scope=self.mshptrail.id_scope,
                                      id_remap={})
                    new_aliases.append(old_a)
                else:
                    new_aliases.append(a)
            for a in pip_aliases:
                if a not in mashup_aliases:
                    new_a = (a, pipeline.aliases[a])
            if old_a is not None and new_a is not None:
                (a, info) = new_a
                parameter = pipeline.db_get_object(info[0],info[1])
                old_a.name = a
                old_a.component.vttype = parameter.vtType 
                old_a.component.vtid = parameter.real_id
                old_a.component.vtparent_type = info[2]
                old_a.component.vt_parent_id = info[3]
                old_a.component.mid = info[4]
                old_a.component.type = parameter.type
                old_a.component.val = parameter.strValue
                old_a.component.vtpos = parameter.pos
            
        elif len(pip_aliases) < len(mashup_aliases):
            # an alias was removed
            pos = 0
            for a in self.currentMashup.alias_list:
                if a.name in pip_aliases:
                    alias = a.do_copy(new_ids=True,
                                      id_scope=self.mshptrail.id_scope,
                                      id_remap={})
                    alias.component.pos = pos
                    new_aliases.append(alias)
                    pos += 1
        else:
            #an alias was added
            pos = len(mashup_aliases)
            new_aliases = [a for a in self.currentMashup.alias_list]
            for a in pip_aliases:
                if a not in mashup_aliases:
                    info = pipeline.aliases[a]
                    parameter = pipeline.db_get_object(info[0],info[1])
                    cid = self.id_scope.getNewId('mashup_component')
                    aid = self.id_scope.getNewId('mashup_alias')
                    component = Component(cid, parameter.vtType, 
                                          parameter.real_id, info[2], info[3],
                                          info[4], parameter.type, 
                                          parameter.strValue, parameter.pos, 
                                          pos, "")
                    alias = Alias(aid, a, component) 
                    new_aliases.append(alias)
                    pos += 1
        
        return self.createMashupVersion(new_aliases, quiet=False)
        
    def updatePipelineAliasesFromCurrentMashup(self):
        self.resetVistrailPipeline()
        self.vtPipeline = copy.copy(self.vtController.current_pipeline)
        #first we clear all aliases in pipeline
        to_remove = self.vtPipeline.aliases.values()
        for (type, oId, parentType, parentId, mid) in to_remove:
            self.vtPipeline.remove_alias(type, oId, parentType, parentId, mid)
            parameter = self.vtPipeline.db_get_object(type,oId)
            parameter.alias = ''
            
        #now we populate the pipeline according to the aliases in the mashup 
        for alias in self.currentMashup.alias_list:
            self.vtPipeline.add_alias(alias.name, alias.component.vttype, 
                                      alias.component.vtid,
                                      alias.component.vtparent_type, 
                                      alias.component.vtparent_id,
                                      alias.component.vtmid)
            parameter = self.vtPipeline.db_get_object(alias.component.vttype,
                                                      alias.component.vtid)
            parameter.alias = alias.name
        
    def getMashupName(self, version=-1):
        action_map = self.mshptrail.actionMap
        if version == -1:
            version = self.currentVersion
        count = 0
        while True:
            hasTag = self.mshptrail.hasTagForActionId(version)
            if hasTag or version <= 1:
                if hasTag:
                    name = self.mshptrail.getTagForActionId(version)
                else:
                    name = "ROOT"
                count_str = ""
                if count > 0:
                    count_str = " + " + str(count)
                return name + count_str
            version = action_map[version].parent_id
            count += 1
            
    def findFirstTaggedParent(self, version):
        action_map = self.mshptrail.actionMap
        version = action_map[version].parent_id
        while True:
            hasTag = self.mshptrail.hasTagForActionId(version)
            if hasTag or version <= 1:
                name = ""
                if hasTag:
                    name = self.mshptrail.getTagForActionId(version)
                return (version, name)
            version = action_map[version].parent_id
            
    def removeAlias(self, name):
        """removeAlias(name: str) -> long
        This will create a new version of the mashup without alias name, add it
        to the trail and set the version as the current version. It will return 
        the version number 
        """
        new_aliases = []
        if self.currentMashup:
            pos = 0
            for alias in self.currentMashup.alias_list:
                if alias.name != name:
                    calias = alias.do_copy(new_ids=True,
                                           id_scope=self.mshptrail.id_scope,
                                           id_remap={})
                    calias.component.pos = pos
                    new_aliases.append(calias)
                    pos += 1
            return self.createMashupVersion(alias_list=new_aliases, quiet=False)
            
    def createMashupVersion(self, alias_list, quiet=False):
        id = self.id_scope.getNewId('mashup')
        mashup = Mashup(id=id, name="mashup%s"%id, 
                        vtid=self.currentMashup.vtid, 
                        version=self.currentMashup.version, 
                        alias_list=alias_list)
        currVersion = self.mshptrail.addVersion(parent_id=self.currentVersion,
                                                mashup=mashup, 
                                                user=current_user(),
                                                date=current_time())
        self.mshptrail.currentVersion = currVersion
        self.currentMashup = mashup
        #print "created new mashup ", currVersion
        self.setCurrentVersion(currVersion, quiet)
        self.setChanged(True)
        return currVersion

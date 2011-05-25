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
import copy
import os.path
from core.system import current_user, current_time
from core.mashup.alias import Alias
from core.mashup.component import Component
from core.mashup.mashup import Mashup

class MashupController(object):
    def __init__(self, vt_controller, vt_version, mshptrail=None):
        self.vtController = vt_controller
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
        
    def setCurrentVersion(self, version):
        self.currentVersion = version
        if version > -1:
            self.currentMashup = self.mshptrail.getMashup(version)
            
    def getVistrailParam(self, alias):
        if self.vtPipeline:
            return self.vtPipeline.db_get_object(alias.component.vttype,
                                                  alias.component.vtid)
        return None
    
    def executeCurrentMashup(self, params):
        if self.vtPipeline and self.vtController:
            return self.vtController.execute_current_workflow(custom_params=params)
        return ([], False)
    
    def updateCurrentTag(self, name):
        self.mshptrail.changeTag(self.currentVersion, name, current_user(),
                                 current_time())
        self.setChanged(True)
    
    def getCurrentTag(self):
        return self.mshptrail.getTagForActionId(self.currentVersion)
    
    def versionHasTag(self, version):
        return self.mshptrail.hasTagForActionId(version)
    
    def getVistrailName(self):
        name = ''
        locator = self.currentMashup.vtid
        if locator != None:
            if locator.name == None:
                name = ''
            else:
                name = os.path.split(locator.name)[1]
            if name == '':
                name = self.controller.vtController.name
        return name
        
    def resetVistrailPipeline(self):
        self.vtController.change_selected_version(self.vtVersion)
    
    def getVistrailWorkflowTag(self):
        return self.vtController.vistrail.getVersionName(self.vtVersion)
    
    def reorderAliases(self, new_order):
        if self.currentMashup:
            new_aliases = []
            pos = 0
            for old_pos in new_order:
                alias = copy.copy(self.currentMashup.alias_list[old_pos])
                alias.component.pos = pos
                new_aliases.append(alias)
                pos += 1
            return self.createMashupVersion(new_aliases, quiet=False)
                
    def updateAlias(self, alias):
        """updateAlias(alias)-> long
        This will create a version with an alias change (can't be a position
        change). Position changes are taken care in reorderAliases method. 
        
        """
        print " controller updateAlias ", alias
        new_aliases = []

        if self.currentMashup:
            for a in self.currentMashup.alias_list:
                if a.id != alias.id:
                    calias = copy.copy(a)
                else:
                    print "found alias: ", a
                    calias = copy.copy(alias)
                new_aliases.append(calias)
        return self.createMashupVersion(new_aliases, quiet=False)
        
    def updateAliasFromParam(self, param):
        add_alias = True
        new_aliases = []
        pos = 0
        for alias in self.currentMashup.alias_list:
            if alias.component.vtid != param.id:
                calias = copy.copy(alias)
                calias.component.pos = pos
                new_aliases.append(calias)
                pos += 1
            else:
                print "found alias: ", alias
                add_alias = False
                if param.alias != '':
                    new_alias = copy.copy(alias)
                    new_alias.name = param.alias
                    new_aliases.append(new_alias)
                    pos += 1
        if add_alias:
            parameter = self.vtPipeline.db_get_object(param.dbtype, param.id)
            cid = self.id_scope.getNewId('component')
            aid = self.id_scope.getNewId('alias')
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
        pip_aliases = pipeline.aliases.keys()
        mashup_aliases = [a.name for a in self.currentMashup.alias_list]
        new_aliases = []
        if len(pip_aliases) == len(mashup_aliases):
            #an alias probably changed its name or its value    
            old_a = None
            new_a = None
            for a in self.currentMashup.alias_list:
                if a.name not in pip_aliases:
                    old_a = copy.copy(a)
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
                    alias = copy.copy(a)
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
                    cid = self.id_scope.getNewId('component')
                    aid = self.id_scope.getNewId('alias')
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
        self.vtPipeline = self.vtController.current_pipeline
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
        
    def getMashupName(self):
        tag_map = self.mshptrail.getTagMap()
        action_map = self.mshptrail.actionMap
        version = self.currentVersion
        count = 0
        while True:
            if version in tag_map or version <= 1:
                if version in tag_map:
                    name = tag_map[version]
                else:
                    name = "ROOT"
                count_str = ""
                if count > 0:
                    count_str = " + " + str(count)
                return name + count_str
            version = action_map[version].parent_id
            count += 1
            
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
                    calias = copy.copy(alias)
                    calias.component.pos = pos
                    new_aliases.append(calias)
                    pos += 1
            return self.createMashupVersion(alias_list=new_aliases, quiet=False)
            
    def createMashupVersion(self, alias_list, quiet=True):
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
        print "created new mashup ", currVersion
        self.setCurrentVersion(currVersion, quiet=False)
        return currVersion
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

import urlparse
import copy

from core.thumbnails import ThumbnailCache
from core import debug
from core.query import extract_text
import core.system

from entity import Entity
from workflow import WorkflowEntity
from workflow_exec import WorkflowExecEntity
from thumbnail import ThumbnailEntity
from mashup import MashupEntity

class VistrailEntity(Entity):
    type_id = 1

    def __init__(self, vistrail=None):
        Entity.__init__(self)
        self.id = None
        self.wf_entity_map = {}
        self.mshp_entity_map = {}
        self.wf_exec_entity_map = {}
        self._vt_tag_map = {}
        self._mshp_tag_map = {}
        # self._last_wf_exec_id = None
        self.reload(vistrail)

    @staticmethod
    def load(*args):
        entity = VistrailEntity()
        Entity.load(entity, *args)
        return entity
    
    def create_workflow_entity(self, workflow, action):
        entity = WorkflowEntity(workflow)
        self.children.append(entity)
        entity.parent = self
        if self.vistrail.has_notes(action.id):
            plain_notes = extract_text(self.vistrail.get_notes(action.id))
            entity.description = plain_notes
        else:
            entity.description = ''
        entity.user = action.user
        entity.mod_time = action.date
        entity.create_time = action.date
        scheme, rest = self.url.split('://', 1)
        url = 'http://' + rest
        url_tuple = urlparse.urlsplit(url)
        query_str = url_tuple[3]
        if query_str == '':
            query_str = 'workflow=%s' % action.id
        else:
            query_str += '&workflow=%s' % action.id
        url_tuple = (scheme, url_tuple[1], url_tuple[2], query_str,
                     url_tuple[4])
        entity.url = urlparse.urlunsplit(url_tuple)
        # entity.url = self.url + '?workflow_id=%s' % action.id
        return entity
    
    def create_mashup_entity(self, trail_id, mashup, action):
        entity = MashupEntity(mashup)
        self.children.append(entity)
        entity.parent = self
        vt_version = mashup.version
        if self.vistrail.has_notes(vt_version):
            plain_notes = extract_text(self.vistrail.get_notes(vt_version))
            entity.description = plain_notes
        else:
            entity.description = ''
        entity.user = action.user
        entity.mod_time = action.date
        entity.create_time = action.date
        scheme, rest = self.url.split('://', 1)
        url = 'http://' + rest
        url_tuple = urlparse.urlsplit(url)
        query_str = url_tuple[3]
        if query_str == '':
            query_str = 'mashuptrail=%s&mashup=%s' %(trail_id, action.id)
        else:
            query_str += '&mashuptrail=%s&mashup=%s' %(trail_id, action.id)
        url_tuple = (scheme, url_tuple[1], url_tuple[2], query_str,
                     url_tuple[4])
        entity.url = urlparse.urlunsplit(url_tuple)
        # entity.url = self.url + '?workflow_id=%s' % action.id
        return entity

    def create_wf_exec_entity(self, wf_exec, wf_entity):
        entity = WorkflowExecEntity(wf_exec)
        wf_entity.children.append(entity)
        entity.parent = wf_entity
        scheme, rest = self.url.split('://', 1)
        url = 'http://' + rest
        url_tuple = urlparse.urlsplit(url)
        query_str = url_tuple[3]
        if query_str == '':
            query_str = 'workflow_exec=%s' % entity.name
        else:
            query_str += '&workflow_exec=%s' % entity.name
        url_tuple = (scheme, url_tuple[1], url_tuple[2], query_str,
                     url_tuple[4])
        entity.url = urlparse.urlunsplit(url_tuple)
        return entity

    def get_vistrail_info(self, vistrail=None):
        if vistrail is None:
            vistrail = self.vistrail
        name = None
        if vistrail.locator:
            name = vistrail.locator.short_name
        if name is None:
            if vistrail.db_name:
                name = vistrail.db_name
            else:
                name = "untitled"
            
        size = vistrail.get_version_count()
        if size < 1:
            # empty vistrail
            user = core.system.current_user()
            mod_time = core.system.current_time()
            create_time = core.system.current_time()
        else:
            latestVersionId = vistrail.get_latest_version()
            latestVersion = vistrail.actionMap[latestVersionId]
            user = latestVersion.user
            mod_time = latestVersion.date
            # FIXME: relies on 1 being the first version...
            firstVersion = vistrail.actionMap[1] \
                if 1 in vistrail.actionMap else latestVersion
            create_time = firstVersion.date
        url = vistrail.locator.to_url() \
            if vistrail.locator else 'file://untitled'
        return (name, size, user, mod_time, create_time, url)

    def set_vistrail(self, vistrail):
        self.vistrail = vistrail

        (self.name, self.size, self.user, self.mod_time, self.create_time, \
             self.url) = self.get_vistrail_info()
        self.description = ""
        self.was_updated = True

    def add_workflow_entity(self, version_id):
        if version_id not in self.vistrail.actionMap:
            return
        action = self.vistrail.actionMap[version_id]
        tag = None
        if self.vistrail.has_tag(version_id):
            tag = self.vistrail.get_tag(version_id)
        try:
            workflow = self.vistrail.getPipeline(version_id)
        except:
            import traceback
            debug.critical("Failed to construct pipeline '%s'" % 
                               (tag if tag else version_id),
                           traceback.format_exc())
            workflow = self.vistrail.getPipeline(0)
        if tag:
            workflow.name = tag
        # if workflow already exists, we want to update it...
        # spin through self.children and look for matching
        # workflow entity?
        # self.children.append(WorkflowEntity(workflow))
        self.wf_entity_map[version_id] = \
            self.create_workflow_entity(workflow, action)

        # get thumbnail
        thumbnail = self.vistrail.get_thumbnail(version_id)
        if thumbnail is not None:
            cache = ThumbnailCache.getInstance()
            path = cache.get_abs_name_entry(thumbnail)
            if path:
                entity = ThumbnailEntity(path)
                self.wf_entity_map[action.id].children.append(entity)
                entity.parent = self.wf_entity_map[action.id]
        return self.wf_entity_map[version_id]

    def add_mashup_entity(self, mashuptrail, version_id, tag=None):
        if not hasattr(self.vistrail, 'mashups'):
            return
        if mashuptrail not in self.vistrail.mashups:
            return
        action = mashuptrail.actionMap[version_id]
        mashup = mashuptrail.getMashup(version_id)
        if tag:
            mashup.name = tag
        mashup.id = action.id
        entity_key = (mashuptrail.id,version_id)
        self.mshp_entity_map[entity_key] = \
                   self.create_mashup_entity(mashuptrail.id, mashup, action)
        # get thumbnail for the workflow it points
        thumb_version = mashuptrail.vtVersion
        thumbnail = self.vistrail.get_thumbnail(thumb_version)
        if thumbnail is not None:
            cache = ThumbnailCache.getInstance()
            path = cache.get_abs_name_entry(thumbnail)
            if path:
                entity = ThumbnailEntity(path)
                mshp_entity = self.mshp_entity_map[entity_key]
                mshp_entity.children.append(entity)
                entity.parent = mshp_entity
        return self.mshp_entity_map[entity_key]
       
    def add_wf_exec_entity(self, wf_exec, add_to_map=False):
        version_id = wf_exec.parent_version
        is_new = False
        if version_id not in self.wf_entity_map:
            is_new = True
            # FIXME add new workflow entity for this version
            if version_id not in self.vistrail.actionMap:
                raise Exception("Version %d does not occur in vistrail." % \
                                    version_id)
            action = self.vistrail.actionMap[version_id]
            try:
                workflow = self.vistrail.getPipeline(version_id)
            except:
                import traceback
                if self.vistrail.has_tag(version_id):
                    tag_str = self.vistrail.get_tag(version_id)
                else:
                    tag_str = str(version_id)
                debug.critical("Failed to construct pipeline '%s'" % tag_str,
                               traceback.format_exc())
                workflow = self.vistrail.getPipeline(0)
            wf_entity = self.create_workflow_entity(workflow, action)
            self.wf_entity_map[version_id] = wf_entity
        else:
            wf_entity = self.wf_entity_map[version_id]

        entity = self.create_wf_exec_entity(wf_exec, wf_entity)
        if add_to_map:
            self.wf_exec_entity_map[wf_exec.id] = entity
        if is_new:
            return (entity, wf_entity)
        return (entity, None)
                        
    def add_mashup_entities_from_mashuptrail(self, mashuptrail):
        added_entry_keys = set()
        inv_tag_map = {}
        tagMap = mashuptrail.getTagMap()
        tags = tagMap.keys()
        if len(tags) > 0:
            tags.sort()
            for tag in tags:
                version_id = tagMap[tag]
                inv_tag_map[version_id] = tag
                action = mashuptrail.actionMap[version_id]
                mashup = mashuptrail.getMashup(version_id)
                mashup.name = tag
                #make sure we identify a mashup by its version
                mashup.id = action.id
                entity_key = (mashuptrail.id,version_id)
                self.mshp_entity_map[entity_key] = \
                   self.create_mashup_entity(mashuptrail.id, mashup, action)
                added_entry_keys.add(entity_key)
                # get thumbnail for the workflow it points
                thumb_version = mashuptrail.vtVersion
                thumbnail = self.vistrail.get_thumbnail(thumb_version)
                if thumbnail is not None:
                    cache = ThumbnailCache.getInstance()
                    path = cache.get_abs_name_entry(thumbnail)
                    if path:
                        entity = ThumbnailEntity(path)
                        mshp_entity = self.mshp_entity_map[entity_key]
                        mshp_entity.children.append(entity)
                        entity.parent = mshp_entity
        return inv_tag_map

    def reload(self, vistrail):
        if vistrail is not None:
            self.set_vistrail(vistrail)

            for version_id in self.vistrail.get_tagMap():
                self.add_workflow_entity(version_id)
            
            #mashups
            if hasattr(self.vistrail, 'mashups'):
                self._mshp_tag_map = {}
                for mashuptrail in self.vistrail.mashups:
                    self._mshp_tag_map[mashuptrail.id] = \
                         self.add_mashup_entities_from_mashuptrail(mashuptrail)
                
            # read persisted log entries
            try:
                log = vistrail.get_persisted_log()
            except:
                import traceback
                debug.critical("Failed to read log", traceback.format_exc())
                
            if log is not None:
                for wf_exec in log.workflow_execs:
                    self.add_wf_exec_entity(wf_exec, False)

            # read unpersisted log entries
            if vistrail.log is not None:
                for wf_exec in self.vistrail.log.workflow_execs:
                    self.add_wf_exec_entity(wf_exec, True)

            self._vt_tag_map = copy.copy(self.vistrail.get_tagMap())
                      
    def update_vistrail(self, vistrail):
        # like set_vistrail but checks everything!

        (name, size, user, mod_time, create_time, url) = \
            self.get_vistrail_info(vistrail)

        was_updated = False
        new_entity = False
        if name != self.name:
            # self.name = name
            new_entity = True
        if size != self.size:
            self.size = size
            was_updated = True
        if user != self.user:
            self.user = user
            was_updated = True
        if mod_time != self.mod_time:
            self.mod_time = mod_time
            was_updated = True
        if create_time != self.create_time:
            self.create_time = create_time
            was_updated = True
        if url != self.url:
            # self.url = url
            new_entity = True

        # if we need a new entity, just return, don't update old one
        if new_entity:
            return (True, was_updated)
 
        self.vistrail = vistrail
        self.vistrail.was_updated = was_updated
        return (False, was_updated)

    def update_workflows(self):
        # here we just need to check for changes in tags
        added_tags = []
        deleted_tags = []
        for version_id, tag in self.vistrail.get_tagMap().iteritems():
            if version_id not in self._vt_tag_map:
                added_tags.append(self.add_workflow_entity(version_id))
            elif tag != self._vt_tag_map[version_id]:
                deleted_tags.append(self.wf_entity_map[version_id])
                added_tags.append(self.add_workflow_entity(version_id))
        for version_id, tag in self._vt_tag_map.iteritems():
            if version_id not in self.vistrail.get_tagMap():
                deleted_tags.append(self.wf_entity_map[version_id])
                del self.wf_entity_map[version_id]
        self._vt_tag_map = copy.copy(self.vistrail.get_tagMap())
        return (added_tags, deleted_tags)

    def update_log(self):
        # only need to check non-persisted wf_execs since log is immutable
        # if vistrail.log.get_last_workflow_exec_id() == self._last_wf_exec_id:
        #     return []
        added_workflows = []
        added_wf_execs = []
        for wf_exec in self.vistrail.log.workflow_execs:
            if wf_exec.id not in self.wf_exec_entity_map:
                (exec_entity, wf_entity) = \
                    self.add_wf_exec_entity(wf_exec, True)
                if wf_entity is not None:
                    added_workflows.append(wf_entity)
                added_wf_execs.append(exec_entity)
        return (added_workflows, added_wf_execs)

    def update_mashups(self):
        added_mashups = []
        deleted_mashups = []
        if hasattr(self.vistrail, 'mashups'):
            for mashuptrail in self.vistrail.mashups:
                if mashuptrail.id not in self._mshp_tag_map:
                    self._mshp_tag_map[mashuptrail.id] = {}
                mashup_tag_map = self._mshp_tag_map[mashuptrail.id]
                tagMap = mashuptrail.getTagMap()
                #mashups tag map is inverted map[tag] -> version
                new_mshp_map = {}
                for tag, version_id in tagMap.iteritems():
                    new_mshp_map[version_id] = tag
                    if version_id not in mashup_tag_map:
                        added_mashups.append(self.add_mashup_entity(mashuptrail, version_id, tag))
                    elif tag != mashup_tag_map[version_id]:
                        deleted_mashups.append(self.mshp_entity_map[(mashuptrail.id,
                                                                     version_id)])
                        added_mashups.append(self.add_mashup_entity(mashuptrail, version_id, tag))
                for version_id, tag in mashup_tag_map.iteritems():
                    if version_id not in tagMap.values():
                        deleted_mashups.append(self.mshp_entity_map[(mashuptrail.id,
                                                                     version_id)])
                        del self.mshp_entity_map[(mashuptrail.id, version_id)]
                self._mshp_tag_map[mashuptrail.id] = new_mshp_map
        return (added_mashups, deleted_mashups)
                
#        for key, mashup in self.mshp_entity_map.iteritems():
#            deleted_mashups.append(mashup)
#        self.mshp_entity_map = {}
#
#        if hasattr(self.vistrail, 'mashups'):
#            for mashuptrail in self.vistrail.mashups:
#                self.mshp_entity_map.update(
#                    self.add_mashup_entities_from_mashuptrail(mashuptrail))
#        for key, mashup in self.mshp_entity_map.iteritems():
#            added_mashups.append(mashup)
#        return (added_mashups, deleted_mashups)
                
#     # returns string
#     def get_name(self):
#         return self.vistrail.name
    
#     # returns datetime
#     def get_mod_time(self):
#         return self.vistrail.get_most_recent_action().py_date

#     # returns datetime
#     def get_create_time(self):
#         return self.vistrail.get_first_action().py_date
    
#     # returns string
#     # FIXME: perhaps this should be a User object at some point
#     def get_user(self):
#         return self.vistrail.get_most_recent_action().py_date
    
#     # returns tuple (<entity_type>, <entity_id>)
#     def get_id(self):
#         return (self.vistrail.vtType, self.vistrail.id)

#     # returns integer
#     def get_size(self):
#         return len(self.vistrail.actionMap)
    
#     # returns possibly empty list of Entity objects
#     def get_children(self):
#         return len(self.vistrail.tagMap)

#     # returns list of strings representing paths
#     # FIXME: should this be urls for database access?
#     def get_image_fnames(self):
#         return []
    
    # returns boolean, True if search input is satisfied else False
    def match(self, search):
        # try match on self
        

        # if no match on self, check for a match on all children
        for child in self.get_children():
            if child.match(search):
                return True

    def open(self):
        locator = BaseLocator.from_url(self.url)
        locator._name = self.name
        core.open_locator(locator)

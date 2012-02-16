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
from core.thumbnails import ThumbnailCache
from core import debug
from core.query import extract_text
import core.system
import urlparse

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
        self.update(vistrail)

    @staticmethod
    def load(*args):
        entity = VistrailEntity()
        Entity.load(entity, *args)
        return entity
    
    def create_workflow_entity(self, workflow, action):
        entity = WorkflowEntity(workflow)
        self.children.append(entity)
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

    def set_vistrail(self, vistrail):
        self.vistrail = vistrail

        self.name = self.vistrail.locator.short_name \
            if self.vistrail.locator else 'untitled'
        if not self.name or self.name == 'None':
            self.name = self.vistrail.db_name
        self.size = len(self.vistrail.actionMap)
        if self.size:
            latestVersion = self.vistrail.actionMap[
                                self.vistrail.get_latest_version()]
            self.user = latestVersion.user
            self.mod_time = latestVersion.date
            firstVersion = self.vistrail.actionMap[1] \
                if 1 in self.vistrail.actionMap else latestVersion
            self.create_time = firstVersion.date
        else:
            # empty vistrail
            self.user = core.system.current_user()
            self.mod_time = core.system.current_time()
            self.create_time = core.system.current_time()
        self.description = ""
        self.url = self.vistrail.locator.to_url() \
            if self.vistrail.locator else 'file://untitled'
        self.was_updated = True        

    def add_workflow_entity(self, version_id):
        if version_id not in self.vistrail.actionMap:
            return
        action = self.vistrail.actionMap[version_id]
        tag = self.vistrail.get_action_annotation(version_id, "__tag__")
        try:
            workflow = self.vistrail.getPipeline(version_id)
        except:
            import traceback
            debug.critical("Failed to construct pipeline '%s'" % 
                               (tag.value if tag else version_id),
                           traceback.format_exc())
            workflow = self.vistrail.getPipeline(0)
        if tag:
            workflow.name = tag.value
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

    def add_mashup_entities_from_mashuptrail(self, mashuptrail):
        tagMap = mashuptrail.getTagMap()
        tags = tagMap.keys()
        if len(tags) > 0:
            tags.sort()
            for tag in tags:
                version_id = tagMap[tag]
                action = mashuptrail.actionMap[version_id]
                mashup = mashuptrail.getMashup(version_id)
                mashup.name = tag
                #make sure we identify a mashup by its version
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
                        
    def update(self, vistrail):
        if vistrail is not None:
            self.set_vistrail(vistrail)

            for version_id in self.vistrail.get_tagMap():
                self.add_workflow_entity(version_id)
            
            #mashups
            if hasattr(self.vistrail, 'mashups'):
                for mashuptrail in self.vistrail.mashups:
                    self.add_mashup_entities_from_mashuptrail(mashuptrail)
                
            try:
                log = vistrail.get_log()
            except:
                import traceback
                debug.critical("Failed to read log", traceback.format_exc())
                
            if log is not None:
                for wf_exec in log.workflow_execs:
                    version_id = wf_exec.parent_version
                    if version_id not in self.wf_entity_map:

                        # FIXME add new workflow entity for this version
                        if version_id not in self.vistrail.actionMap:
                            continue
                        action = self.vistrail.actionMap[version_id]
                        try:
                            workflow = self.vistrail.getPipeline(version_id)
                        except:
                            import traceback
                            tag = self.vistrail.get_action_annotation(
                                                     version_id, "__tag__")
                            debug.critical("Failed to construct pipeline '%s'" %
                                             (tag.value if tag else version_id),
                                           traceback.format_exc())
                            workflow = self.vistrail.getPipeline(0)
                        wf_entity = \
                            self.create_workflow_entity(workflow, action)

                        self.wf_entity_map[version_id] = wf_entity
                    else:
                        wf_entity = self.wf_entity_map[version_id]
                    entity = WorkflowExecEntity(wf_exec)

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
                    wf_entity.children.append(entity)
                      
            # moved this code to add_workflow_entity
            # for action in self.vistrail.actionMap.itervalues():
            #     thumbnail = self.vistrail.get_thumbnail(action.id)
            #     if thumbnail is not None:
            #         cache = ThumbnailCache.getInstance()
            #         path = cache.get_abs_name_entry(thumbnail)
            #         if not path:
            #             continue
            #         entity = ThumbnailEntity(path)

            #         if action.id in self.wf_entity_map:
            #             self.wf_entity_map[action.id].children.append(entity)
            #         else:
            #             # there is a thumbnail but the action is not important
            #             #print "No such action:", action.id                    
            #             pass

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

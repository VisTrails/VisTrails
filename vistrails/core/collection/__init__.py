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

import glob
import os
import sqlite3
from itertools import chain

from entity import Entity
from vistrail import VistrailEntity
from workflow import WorkflowEntity
from workflow_exec import WorkflowExecEntity
from thumbnail import ThumbnailEntity
from mashup import MashupEntity
from parameter_exploration import ParameterExplorationEntity

from vistrails.core.db.locator import FileLocator, BaseLocator
from vistrails.core.db.io import load_vistrail
import vistrails.core.system
import vistrails.db.services.io
from vistrails.core import debug

schema = ["create table entity(id integer primary key, type integer, "
          "name text, user integer, mod_time text, create_time text, "
          "size integer, description text, url text)",
          "create table entity_children(parent integer, child integer)",
          "create table entity_workspace(entity integer, workspace text)",
          "create table workspaces(id text primary key)",
          "insert into workspaces values ('Default')"]

class Collection(object):
    entity_types = dict((x.type_id, x)
                        for x in [VistrailEntity, WorkflowEntity, 
                                  WorkflowExecEntity, ThumbnailEntity,
                                  MashupEntity, ParameterExplorationEntity])
    def __init__(self, database=None):
        if database is None:
            self.database = ':memory:'
        else:
            self.database = database

        self.entities = {}
        self.deleted_entities = {}
        self.temp_entities = {}
        self.workspaces = {}
        self.currentWorkspace = 'Default'
        self.listeners = [] # listens for entity creation removal
        self.max_id = 0
        
        if not os.path.exists(self.database):
            debug.log("'%s' does not exist. Trying to create" % self.database)
            self.conn = sqlite3.connect(self.database)
            try:
                cur = self.conn.cursor()
                for s in schema:
                    cur.execute(s)
                self.conn.commit()
            except Exception, e:
                debug.critical("Could not create vistrail index schema", e)
        else:
            self.conn = sqlite3.connect(self.database)
        self.load_entities()

    #Singleton technique
    _instance = None

    @staticmethod
    def getInstance():
        if Collection._instance is False:
            debug.critical("Collection.getInstance() called but the "
                           "Collection has been deleted!")
            raise RuntimeError("Collection has been deleted!")
        elif Collection._instance is None:
            dotVistrails = vistrails.core.system.current_dot_vistrails()

            path = os.path.join(dotVistrails, "index.db")
            obj = Collection(path)
            Collection._instance = obj
        return Collection._instance

    @staticmethod
    def clearInstance():
        if Collection._instance:
            Collection._instance.conn.close()
        Collection._instance = False

    def add_listener(self, c):
        """ Add objects that listen to entity creation/removal
            Object may implement the following method
             updated(self)
        """
        self.listeners.append(c)

    def clear(self):
        cur = self.conn.cursor()
        cur.execute('delete from entity;')
        cur.execute('delete from entity_children;')
        cur.execute('delete from workspaces;')
        cur.execute('delete from entity_workspace;')

    def get_current_entities(self):
        """NOTE: returns an iterator"""
        return chain(self.entities.itervalues(), 
                     self.temp_entities.itervalues())

    def load_entities(self):
        cur = self.conn.cursor()
        cur.execute("select max(id) from entity;")
        for row in cur.fetchall():
            n = row[0]
            self.max_id = n if n is not None else 0
        
        cur.execute("select * from entity;")
        for row in cur.fetchall():
            entity = self.load_entity(*row)
            if entity is not None:
                self.entities[entity.id] = entity

        # now need to map children to correct places
        cur.execute("select * from entity_children;")
        for row in cur.fetchall():
            if row[0] in self.entities and row[1] in self.entities:
                self.entities[row[0]].children.append(self.entities[row[1]])
                self.entities[row[1]].parent = self.entities[row[0]]

        cur.execute("select * from workspaces;")
        for row in cur.fetchall():
            self.workspaces[row[0]] = []

        cur.execute("select * from entity_workspace;")
        for row in cur.fetchall():
            e_id, workspace = row
            if e_id in self.entities:
                if workspace not in self.workspaces:
                    self.workspaces[workspace] = []
                self.workspaces[workspace].append(self.entities[e_id])

    def save_entities(self):
        # TODO delete entities with no workspace
        for entity in self.deleted_entities.itervalues():
            self.db_delete_entity(entity)
        self.deleted_entities = {}
        
        for entity in self.entities.itervalues():
            if entity.was_updated:
                self.save_entity(entity)
                
        cur = self.conn.cursor()
        cur.execute('delete from workspaces;')
        cur.executemany("insert into workspaces values (?)", 
                        [(i,) for i in self.workspaces])

        cur.execute('delete from entity_workspace;')
        cur.executemany("insert into entity_workspace values (?, ?)", 
            ((k.id, i) for i,j in self.workspaces.iteritems() for k in j))

    def load_entity(self, *args):
        if args[1] in Collection.entity_types:
            entity = Collection.entity_types[args[1]].create(*args)
            return entity
        else:
            debug.critical("Cannot find entity type '%s'" % args[1])
        return None

    def add_entity(self, entity):
        """ Adds entities to memory recursively """
        if entity.id is None:
            self.max_id += 1
            entity.id = self.max_id
        entity.was_updated = True
        self.entities[entity.id] = entity
        for child in entity.children:
            child.parent = entity
            self.add_entity(child)
        
    def add_temp_entity(self, entity):
        """Add an entity to memory only.  Used for vistrails that have
        not been saved."""
        self.max_id += 1
        entity.id = self.max_id
        self.temp_entities[entity.id] = entity
        for child in entity.children:
            child.parent = entity
            self.add_temp_entity(child)

    def is_temp_entity(self, entity):
        return entity.id in self.temp_entities
            
    def save_entity(self, entity):
        """ saves entities to disk """
        cur = self.conn.cursor()
        entity_tuple = entity.save()
        cur.execute("insert or replace into entity values(%s)" % \
                    ','.join(('?',) * len(entity_tuple)), entity_tuple)
        entity.was_updated = False
        cur.execute('delete from entity_children where parent=?', (entity.id,))
        cur.executemany("insert into entity_children values (?, ?)",
                        ((entity.id, child.id) for child in entity.children))

    def commit(self):
        self.save_entities()
        self.conn.commit()
        for o in self.listeners:
            if hasattr(o, "updated"):
                o.updated()

    def delete_entity(self, entity):
        """ Delete entity from memory recursively """
        if entity.id in self.temp_entities:
            del self.temp_entities[entity.id]
        else:
            self.deleted_entities[entity.id] = entity
            if entity.id in self.entities:
                del self.entities[entity.id]
        for child in entity.children:
            self.delete_entity(child)

    def add_workspace(self, workspace):
        if workspace not in self.workspaces:
            self.workspaces[workspace] = []

    def add_to_workspace(self, entity, workspace=None):
        if not entity:
            return
        if not workspace:
            workspace = self.currentWorkspace
        self.add_workspace(workspace)
        if entity not in self.workspaces[workspace]:
            self.workspaces[workspace].append(entity)
        
    def del_from_workspace(self, entity, workspace=None):
        if not workspace:
            workspace = self.currentWorkspace
        if workspace in self.workspaces:
            if entity in self.workspaces[workspace]:
                self.workspaces[workspace].remove(entity)

    def delete_workspace(self, workspace):
        if workspace in self.workspaces:
            del self.workspaces[workspace]

    def db_delete_entity(self, entity):
        """ Delete entity from database """
        cur = self.conn.cursor()
        if entity.id is not None:
            cur.execute("delete from entity where id=?", (entity.id,))
            cur.execute("delete from entity_children where parent=?", (entity.id,))
            cur.execute("delete from entity_children where child=?", (entity.id,))

    def create_workflow_entity(self, workflow):
        entity = WorkflowEntity(workflow)
        self.add_entity(entity)
        return entity

    def create_vistrail_entity(self, vistrail):
        entity = VistrailEntity(vistrail)
        self.add_entity(entity)
        return entity

    def update_from_directory(self, directory):
        filenames = glob.glob(os.path.join(directory, '*.vt'))
        for filename in filenames:
            locator = FileLocator(filename)
            url = locator.to_url()
            self.updateVistrail(url)

    def fromUrl(self, url):
        """ Check if entity with this url exist in index and return it """
        for e in self.entities.itervalues():
            if e.url == url:
                return e
        return None

    def urlExists(self, url):
        """ Check if entity with this url exist """
        locator = BaseLocator.from_url(url)
        if locator.is_valid():
            return True
        return False

    def updateVistrail(self, url, vistrail=None):
        """ updateVistrail(self, string:url, Vistrail:vistrail)
        Update the specified entity url. Delete or reload as necessary.
        Need to make sure workspaces are updated if the entity is changed.
        """
        entities = [e for e in self.entities.itervalues() if e.url == url]
        entity = entities[0] if len(entities) else None
        while entity and entity.parent:
            entity = entity.parent 
            url = entity.url
        workspaces = [p for p in self.workspaces if entity in self.workspaces[p]]
        if entity:
            for p in workspaces:
                self.del_from_workspace(entity, p)
            self.delete_entity(entity)

        locator = BaseLocator.from_url(url)
        if locator.is_valid():
            if not vistrail:
                (vistrail, abstractions, thumbnails, mashups) = load_vistrail(locator)
                vistrail.abstractions = abstractions
                vistrail.thumbnails = thumbnails
                vistrail.mashups = mashups
            entity = self.create_vistrail_entity(vistrail)
            for p in workspaces:
                self.add_to_workspace(entity, p)
            return entity
        else:
            # probably an unsaved vistrail
            pass
#            debug.critical("Locator is not valid!")

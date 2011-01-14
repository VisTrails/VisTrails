import glob
import os
import sqlite3

from entity import Entity
from vistrail import VistrailEntity
from workflow import WorkflowEntity
from workflow_exec import WorkflowExecEntity
from thumbnail import ThumbnailEntity

from core.db.locator import ZIPFileLocator, DBLocator, FileLocator, BaseLocator
from core.db.io import load_vistrail
import core.system
import db.services.io
from core.configuration import get_vistrails_configuration
from core import debug

schema = ["create table entity(id integer primary key, type integer, "
          "name text, user integer, mod_time text, create_time text, "
          "size integer, description text, url text)",
          "create table entity_children(parent integer, child integer)"]

class Collection(object):
    entity_types = dict((x.type_id, x) 
                        for x in [VistrailEntity, WorkflowEntity, 
                                  WorkflowExecEntity, ThumbnailEntity])

    def __init__(self, database=None):
        if database is None:
            self.database = ':memory:'
        else:
            self.database = database

        self.entities = {}
        self.deleted_entities = {}
        self.listeners = [] # listens for entity creation removal
        self.max_id = 0
        
        if not os.path.exists(self.database):
            debug.log("'%s' does not exist. Trying to create" % self.database)
            self.conn = sqlite3.connect(self.database)
            try:
                cur = self.conn.cursor()
                [cur.execute(s) for s in schema]
                self.conn.commit()
            except Exception, e:
                debug.critical("Could not create vistrail index schema",
                               str(e))
        else:
            self.conn = sqlite3.connect(self.database)
                
            
        self.load_entities()

    #Singleton technique
    _instance = None
    class CollectionSingleton():
        def __call__(self, *args, **kw):
            if Collection._instance is None:
                config = get_vistrails_configuration()
                if config:
                    self.dotVistrails = config.dotVistrails
                else:
                    self.dotVistrails = core.system.default_dot_vistrails()

                config = get_vistrails_configuration()
                path = os.path.join(self.dotVistrails, "index.db")
                obj = Collection(path)
                Collection._instance = obj
            return Collection._instance
        
    getInstance = CollectionSingleton()

    def add_listener(self, c):
        """ Add objects that listen to entity creation/removal
            Object may implement the following methods
             entityCreated(self, entity)
             entityDeleted(self, entity)
        """
        self.listeners.append(c)

    def clear(self):
        cur = self.conn.cursor()
        cur.execute('delete from entity;')
        cur.execute('delete from entity_children;')
        self.conn.commit()

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

    def save_entities(self):
        for entity in self.deleted_entities.itervalues():
            self.db_delete_entity(entity)
        self.deleted_entities = {}
        
        for entity in self.entities.itervalues():
            if entity.was_updated:
                self.save_entity(entity)
            
    def load_entity(self, *args):
        if args[1] in Collection.entity_types:
            entity = Collection.entity_types[args[1]].load(*args)
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
        for o in self.listeners:
            if hasattr(o, "entityCreated"):
                o.entityCreated(entity)
        
        cur = self.conn.cursor()
        entity_tuple = entity.save()
        cur.execute("insert or replace into entity values(%s)" % \
                    ','.join(('?',) * len(entity_tuple)), entity_tuple)
        entity.was_updated = False
        # self.conn.commit()
        cur.execute('delete from entity_children where parent=?', (entity.id,))
        cur.executemany("insert into entity_children values (?, ?)", 
                        ((entity.id, child.id) for child in entity.children))

    def commit(self):
        self.save_entities()
        self.conn.commit()

    def delete_entity(self, entity):
        """ Delete entity from memory recursively"""
        self.deleted_entities[entity.id] = entity
        del self.entities[entity.id]
        for child in entity.children:
            self.delete_entity(child)
        for o in self.listeners:
            if hasattr(o, "entityDeleted"):
                o.entityCreated(entity)

    def db_delete_entity(self, entity):
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

    def update_from_database(self, db_locator):
        # db_conn = db_locator.get_connection()
        config = (('host', db_locator._host),
                  ('port', int(db_locator._port)),
                  ('db', db_locator._db),
                  ('user', db_locator._user),
                  ('passwd', db_locator._passwd))
        rows = db.services.io.get_db_object_list(dict(config), 'vistrail')
        for row in rows:
            if row[0] in [1,]:
                continue
            kwargs = {'obj_type': 'vistrail', 'obj_id': row[0]}
            locator = DBLocator(*[x[1] for x in config], **kwargs)
            (vistrail, abstractions, thumbnails) = load_vistrail(locator)
            vistrail.abstractions = abstractions
            vistrail.thumbnails = thumbnails

            entity = self.create_vistrail_entity(vistrail)

    def update_from_directory(self, directory):
        filenames = glob.glob(os.path.join(directory, '*.vt'))
        for filename in filenames:
            print 'processing ', filename
            locator = FileLocator(filename)
            url = locator.to_url()
            self.updateVistrail(url)
        self.commit()

    def hasUrl(self, url):
        """ Check if entity with this url exist in index """
        for e in self.entities.itervalues():
            if e.url == url:
                return True
        return False

    def urlExists(self, url):
        """ Check if entity with this url exist """
        locator = BaseLocator.from_url(url)
        if locator.is_valid():
                return True
        return False

    def updateVistrail(self, url, vistrail = None):
        """ Update the specified url. Delete or reload as necessary. """
        locator = BaseLocator.from_url(url)
        entities = [e for e in self.entities.itervalues() if e.url == url]
        entity = entities[0] if len(entities) else None
        if entity:
                self.delete_entity(entity)
        if locator.is_valid():
            if not vistrail:
                (vistrail, abstractions, thumbnails) = load_vistrail(locator)
                vistrail.abstractions = abstractions
                vistrail.thumbnails = thumbnails
            entity = self.create_vistrail_entity(vistrail)
            self.add_entity(entity)

def main():
    from db.services.locator import BaseLocator
    import sys
    sys.path.append('/home/tommy/git/vistrails/vistrails')

    # vistrail = load_vistrail(ZIPFileLocator('/vistrails/examples/spx.vt'))[0]
#    db_locator = DBLocator('vistrails.sci.utah.edu', 3306,
#                           'vistrails', 'vistrails', '8edLj4',
#                           obj_id=9, obj_type='vistrail')
    # vistrail = load_vistrail(db_locator)[0]
    c = Collection('/home/tommy/git/vistrails/vistrails/core/collection/test.db')
    c.clear()
    c.update_from_directory('/home/tommy/git/vistrails/examples')
#    c.update_from_database(db_locator)

    # entity = c.create_vistrail_entity(vistrail)
    c.entities = {}
    c.load_entities()
#    print c.entities[2].url
#    locator = BaseLocator.from_url(c.entities[2].url)
#    c.entities[1].description = 'blah blah blah'
#    c.save_entity(c.entities[1])
#    print locator.to_url()
    # c.load_entities()

#    print BaseLocator.from_url('/vistrails/examples/spx.xml').to_url()

if __name__ == '__main__':
    main()
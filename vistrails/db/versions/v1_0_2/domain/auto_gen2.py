from auto_gen import DBTag, DBAnnotation, DBAction, DBActionAnnotation, \
    DBWorkflowExec, DBFunction, DBPortSpec, DBModuleExec, DBLoopExec, \
    DBGroupExec

class DBVistrail(object):

    vtType = 'vistrail'

    def __init__(self, id=None, entity_type=None, version=None, name=None, last_modified=None, actions=None, tags=None, annotations=None, actionAnnotations=None):
        self._db_id = id
        self._db_entity_type = entity_type
        self._db_version = version
        self._db_name = name
        self._db_last_modified = last_modified
        self.db_deleted_actions = []
        self.db_actions_id_index = {}
        if actions is None:
            self._db_actions = []
        else:
            self._db_actions = actions
            for v in self._db_actions:
                self.db_actions_id_index[v.db_id] = v
        self.db_deleted_tags = []
        self.db_tags_id_index = {}
        self.db_tags_name_index = {}
        if tags is None:
            self._db_tags = []
        else:
            self._db_tags = tags
            for v in self._db_tags:
                self.db_tags_id_index[v.db_id] = v
                self.db_tags_name_index[v.db_name] = v
        self.db_deleted_annotations = []
        self.db_annotations_id_index = {}
        self.db_annotations_key_index = {}
        if annotations is None:
            self._db_annotations = []
        else:
            self._db_annotations = annotations
            for v in self._db_annotations:
                self.db_annotations_id_index[v.db_id] = v
                self.db_annotations_key_index[v.db_key] = v
        self.db_deleted_actionAnnotations = []
        self.db_actionAnnotations_id_index = {}
        self.db_actionAnnotations_action_id_index = {}
        self.db_actionAnnotations_key_index = {}
        if actionAnnotations is None:
            self._db_actionAnnotations = []
        else:
            self._db_actionAnnotations = actionAnnotations
            for v in self._db_actionAnnotations:
                self.db_actionAnnotations_id_index[v.db_id] = v
                self.db_actionAnnotations_action_id_index[(v.db_action_id,v.db_key)] = v
                self.db_actionAnnotations_key_index[(v.db_key,v.db_value)] = v
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBVistrail.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBVistrail(id=self._db_id,
                        entity_type=self._db_entity_type,
                        version=self._db_version,
                        name=self._db_name,
                        last_modified=self._db_last_modified)
        if self._db_actions is None:
            cp._db_actions = []
        else:
            cp._db_actions = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_actions]
        if self._db_tags is None:
            cp._db_tags = []
        else:
            cp._db_tags = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_tags]
        if self._db_annotations is None:
            cp._db_annotations = []
        else:
            cp._db_annotations = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_annotations]
        if self._db_actionAnnotations is None:
            cp._db_actionAnnotations = []
        else:
            cp._db_actionAnnotations = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_actionAnnotations]
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
        
        # recreate indices and set flags
        cp.db_actions_id_index = dict((v.db_id, v) for v in cp._db_actions)
        cp.db_tags_id_index = dict((v.db_id, v) for v in cp._db_tags)
        cp.db_tags_name_index = dict((v.db_name, v) for v in cp._db_tags)
        cp.db_annotations_id_index = dict((v.db_id, v) for v in cp._db_annotations)
        cp.db_annotations_key_index = dict((v.db_key, v) for v in cp._db_annotations)
        cp.db_actionAnnotations_id_index = dict((v.db_id, v) for v in cp._db_actionAnnotations)
        cp.db_actionAnnotations_action_id_index = dict(((v.db_action_id,v.db_key), v) for v in cp._db_actionAnnotations)
        cp.db_actionAnnotations_key_index = dict(((v.db_key,v.db_value), v) for v in cp._db_actionAnnotations)
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBVistrail()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'entity_type' in class_dict:
            res = class_dict['entity_type'](old_obj, trans_dict)
            new_obj.db_entity_type = res
        elif hasattr(old_obj, 'db_entity_type') and old_obj.db_entity_type is not None:
            new_obj.db_entity_type = old_obj.db_entity_type
        if 'version' in class_dict:
            res = class_dict['version'](old_obj, trans_dict)
            new_obj.db_version = res
        elif hasattr(old_obj, 'db_version') and old_obj.db_version is not None:
            new_obj.db_version = old_obj.db_version
        if 'name' in class_dict:
            res = class_dict['name'](old_obj, trans_dict)
            new_obj.db_name = res
        elif hasattr(old_obj, 'db_name') and old_obj.db_name is not None:
            new_obj.db_name = old_obj.db_name
        if 'last_modified' in class_dict:
            res = class_dict['last_modified'](old_obj, trans_dict)
            new_obj.db_last_modified = res
        elif hasattr(old_obj, 'db_last_modified') and old_obj.db_last_modified is not None:
            new_obj.db_last_modified = old_obj.db_last_modified
        if 'actions' in class_dict:
            res = class_dict['actions'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_action(obj)
        elif hasattr(old_obj, 'db_actions') and old_obj.db_actions is not None:
            for obj in old_obj.db_actions:
                new_obj.db_add_action(DBAction.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_actions') and hasattr(new_obj, 'db_deleted_actions'):
            for obj in old_obj.db_deleted_actions:
                n_obj = DBAction.update_version(obj, trans_dict)
                new_obj.db_deleted_actions.append(n_obj)
        if 'tags' in class_dict:
            res = class_dict['tags'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_tag(obj)
        elif hasattr(old_obj, 'db_tags') and old_obj.db_tags is not None:
            for obj in old_obj.db_tags:
                new_obj.db_add_tag(DBTag.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_tags') and hasattr(new_obj, 'db_deleted_tags'):
            for obj in old_obj.db_deleted_tags:
                n_obj = DBTag.update_version(obj, trans_dict)
                new_obj.db_deleted_tags.append(n_obj)
        if 'annotations' in class_dict:
            res = class_dict['annotations'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_annotation(obj)
        elif hasattr(old_obj, 'db_annotations') and old_obj.db_annotations is not None:
            for obj in old_obj.db_annotations:
                new_obj.db_add_annotation(DBAnnotation.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_annotations') and hasattr(new_obj, 'db_deleted_annotations'):
            for obj in old_obj.db_deleted_annotations:
                n_obj = DBAnnotation.update_version(obj, trans_dict)
                new_obj.db_deleted_annotations.append(n_obj)
        if 'actionAnnotations' in class_dict:
            res = class_dict['actionAnnotations'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_actionAnnotation(obj)
        elif hasattr(old_obj, 'db_actionAnnotations') and old_obj.db_actionAnnotations is not None:
            for obj in old_obj.db_actionAnnotations:
                new_obj.db_add_actionAnnotation(DBActionAnnotation.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_actionAnnotations') and hasattr(new_obj, 'db_deleted_actionAnnotations'):
            for obj in old_obj.db_deleted_actionAnnotations:
                n_obj = DBActionAnnotation.update_version(obj, trans_dict)
                new_obj.db_deleted_actionAnnotations.append(n_obj)
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False):
        children = []
        to_del = []
        for child in self.db_actions:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_action(child)
        to_del = []
        for child in self.db_tags:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_tag(child)
        to_del = []
        for child in self.db_annotations:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_annotation(child)
        to_del = []
        for child in self.db_actionAnnotations:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_actionAnnotation(child)
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_actions)
        children.extend(self.db_deleted_tags)
        children.extend(self.db_deleted_annotations)
        children.extend(self.db_deleted_actionAnnotations)
        if remove:
            self.db_deleted_actions = []
            self.db_deleted_tags = []
            self.db_deleted_annotations = []
            self.db_deleted_actionAnnotations = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        for child in self._db_actions:
            if child.has_changes():
                return True
        for child in self._db_tags:
            if child.has_changes():
                return True
        for child in self._db_annotations:
            if child.has_changes():
                return True
        for child in self._db_actionAnnotations:
            if child.has_changes():
                return True
        return False
    def __get_db_id(self):
        return self._db_id
    def __set_db_id(self, id):
        self._db_id = id
        self.is_dirty = True
    db_id = property(__get_db_id, __set_db_id)
    def db_add_id(self, id):
        self._db_id = id
    def db_change_id(self, id):
        self._db_id = id
    def db_delete_id(self, id):
        self._db_id = None
    
    def __get_db_entity_type(self):
        return self._db_entity_type
    def __set_db_entity_type(self, entity_type):
        self._db_entity_type = entity_type
        self.is_dirty = True
    db_entity_type = property(__get_db_entity_type, __set_db_entity_type)
    def db_add_entity_type(self, entity_type):
        self._db_entity_type = entity_type
    def db_change_entity_type(self, entity_type):
        self._db_entity_type = entity_type
    def db_delete_entity_type(self, entity_type):
        self._db_entity_type = None
    
    def __get_db_version(self):
        return self._db_version
    def __set_db_version(self, version):
        self._db_version = version
        self.is_dirty = True
    db_version = property(__get_db_version, __set_db_version)
    def db_add_version(self, version):
        self._db_version = version
    def db_change_version(self, version):
        self._db_version = version
    def db_delete_version(self, version):
        self._db_version = None
    
    def __get_db_name(self):
        return self._db_name
    def __set_db_name(self, name):
        self._db_name = name
        self.is_dirty = True
    db_name = property(__get_db_name, __set_db_name)
    def db_add_name(self, name):
        self._db_name = name
    def db_change_name(self, name):
        self._db_name = name
    def db_delete_name(self, name):
        self._db_name = None
    
    def __get_db_last_modified(self):
        return self._db_last_modified
    def __set_db_last_modified(self, last_modified):
        self._db_last_modified = last_modified
        self.is_dirty = True
    db_last_modified = property(__get_db_last_modified, __set_db_last_modified)
    def db_add_last_modified(self, last_modified):
        self._db_last_modified = last_modified
    def db_change_last_modified(self, last_modified):
        self._db_last_modified = last_modified
    def db_delete_last_modified(self, last_modified):
        self._db_last_modified = None
    
    def __get_db_actions(self):
        return self._db_actions
    def __set_db_actions(self, actions):
        self._db_actions = actions
        self.is_dirty = True
    db_actions = property(__get_db_actions, __set_db_actions)
    def db_get_actions(self):
        return self._db_actions
    def db_add_action(self, action):
        self.is_dirty = True
        self._db_actions.append(action)
        self.db_actions_id_index[action.db_id] = action
    def db_change_action(self, action):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_actions)):
            if self._db_actions[i].db_id == action.db_id:
                self._db_actions[i] = action
                found = True
                break
        if not found:
            self._db_actions.append(action)
        self.db_actions_id_index[action.db_id] = action
    def db_delete_action(self, action):
        self.is_dirty = True
        for i in xrange(len(self._db_actions)):
            if self._db_actions[i].db_id == action.db_id:
                if not self._db_actions[i].is_new:
                    self.db_deleted_actions.append(self._db_actions[i])
                del self._db_actions[i]
                break
        del self.db_actions_id_index[action.db_id]
    def db_get_action(self, key):
        for i in xrange(len(self._db_actions)):
            if self._db_actions[i].db_id == key:
                return self._db_actions[i]
        return None
    def db_get_action_by_id(self, key):
        return self.db_actions_id_index[key]
    def db_has_action_with_id(self, key):
        return key in self.db_actions_id_index
    
    def __get_db_tags(self):
        return self._db_tags
    def __set_db_tags(self, tags):
        self._db_tags = tags
        self.is_dirty = True
    db_tags = property(__get_db_tags, __set_db_tags)
    def db_get_tags(self):
        return self._db_tags
    def db_add_tag(self, tag):
        self.is_dirty = True
        self._db_tags.append(tag)
        self.db_tags_id_index[tag.db_id] = tag
        self.db_tags_name_index[tag.db_name] = tag
    def db_change_tag(self, tag):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_tags)):
            if self._db_tags[i].db_id == tag.db_id:
                self._db_tags[i] = tag
                found = True
                break
        if not found:
            self._db_tags.append(tag)
        self.db_tags_id_index[tag.db_id] = tag
        self.db_tags_name_index[tag.db_name] = tag
    def db_delete_tag(self, tag):
        self.is_dirty = True
        for i in xrange(len(self._db_tags)):
            if self._db_tags[i].db_id == tag.db_id:
                if not self._db_tags[i].is_new:
                    self.db_deleted_tags.append(self._db_tags[i])
                del self._db_tags[i]
                break
        del self.db_tags_id_index[tag.db_id]
        del self.db_tags_name_index[tag.db_name]
    def db_get_tag(self, key):
        for i in xrange(len(self._db_tags)):
            if self._db_tags[i].db_id == key:
                return self._db_tags[i]
        return None
    def db_get_tag_by_id(self, key):
        return self.db_tags_id_index[key]
    def db_has_tag_with_id(self, key):
        return key in self.db_tags_id_index
    def db_get_tag_by_name(self, key):
        return self.db_tags_name_index[key]
    def db_has_tag_with_name(self, key):
        return key in self.db_tags_name_index
    
    def __get_db_annotations(self):
        return self._db_annotations
    def __set_db_annotations(self, annotations):
        self._db_annotations = annotations
        self.is_dirty = True
    db_annotations = property(__get_db_annotations, __set_db_annotations)
    def db_get_annotations(self):
        return self._db_annotations
    def db_add_annotation(self, annotation):
        self.is_dirty = True
        self._db_annotations.append(annotation)
        self.db_annotations_id_index[annotation.db_id] = annotation
        self.db_annotations_key_index[annotation.db_key] = annotation
    def db_change_annotation(self, annotation):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_annotations)):
            if self._db_annotations[i].db_id == annotation.db_id:
                self._db_annotations[i] = annotation
                found = True
                break
        if not found:
            self._db_annotations.append(annotation)
        self.db_annotations_id_index[annotation.db_id] = annotation
        self.db_annotations_key_index[annotation.db_key] = annotation
    def db_delete_annotation(self, annotation):
        self.is_dirty = True
        for i in xrange(len(self._db_annotations)):
            if self._db_annotations[i].db_id == annotation.db_id:
                if not self._db_annotations[i].is_new:
                    self.db_deleted_annotations.append(self._db_annotations[i])
                del self._db_annotations[i]
                break
        del self.db_annotations_id_index[annotation.db_id]
        del self.db_annotations_key_index[annotation.db_key]
    def db_get_annotation(self, key):
        for i in xrange(len(self._db_annotations)):
            if self._db_annotations[i].db_id == key:
                return self._db_annotations[i]
        return None
    def db_get_annotation_by_id(self, key):
        return self.db_annotations_id_index[key]
    def db_has_annotation_with_id(self, key):
        return key in self.db_annotations_id_index
    def db_get_annotation_by_key(self, key):
        return self.db_annotations_key_index[key]
    def db_has_annotation_with_key(self, key):
        return key in self.db_annotations_key_index
    
    def __get_db_actionAnnotations(self):
        return self._db_actionAnnotations
    def __set_db_actionAnnotations(self, actionAnnotations):
        self._db_actionAnnotations = actionAnnotations
        self.is_dirty = True
    db_actionAnnotations = property(__get_db_actionAnnotations, __set_db_actionAnnotations)
    def db_get_actionAnnotations(self):
        return self._db_actionAnnotations
    def db_add_actionAnnotation(self, actionAnnotation):
        self.is_dirty = True
        self._db_actionAnnotations.append(actionAnnotation)
        self.db_actionAnnotations_id_index[actionAnnotation.db_id] = actionAnnotation
        self.db_actionAnnotations_action_id_index[(actionAnnotation.db_action_id,actionAnnotation.db_key)] = actionAnnotation
        self.db_actionAnnotations_key_index[(actionAnnotation.db_key,actionAnnotation.db_value)] = actionAnnotation
    def db_change_actionAnnotation(self, actionAnnotation):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_actionAnnotations)):
            if self._db_actionAnnotations[i].db_id == actionAnnotation.db_id:
                self._db_actionAnnotations[i] = actionAnnotation
                found = True
                break
        if not found:
            self._db_actionAnnotations.append(actionAnnotation)
        self.db_actionAnnotations_id_index[actionAnnotation.db_id] = actionAnnotation
        self.db_actionAnnotations_action_id_index[(actionAnnotation.db_action_id,actionAnnotation.db_key)] = actionAnnotation
        self.db_actionAnnotations_key_index[(actionAnnotation.db_key,actionAnnotation.db_value)] = actionAnnotation
    def db_delete_actionAnnotation(self, actionAnnotation):
        self.is_dirty = True
        for i in xrange(len(self._db_actionAnnotations)):
            if self._db_actionAnnotations[i].db_id == actionAnnotation.db_id:
                if not self._db_actionAnnotations[i].is_new:
                    self.db_deleted_actionAnnotations.append(self._db_actionAnnotations[i])
                del self._db_actionAnnotations[i]
                break
        del self.db_actionAnnotations_id_index[actionAnnotation.db_id]
        del self.db_actionAnnotations_action_id_index[(actionAnnotation.db_action_id,actionAnnotation.db_key)]
        try:
            del self.db_actionAnnotations_key_index[(actionAnnotation.db_key,actionAnnotation.db_value)]
        except KeyError:
            pass
    def db_get_actionAnnotation(self, key):
        for i in xrange(len(self._db_actionAnnotations)):
            if self._db_actionAnnotations[i].db_id == key:
                return self._db_actionAnnotations[i]
        return None
    def db_get_actionAnnotation_by_id(self, key):
        return self.db_actionAnnotations_id_index[key]
    def db_has_actionAnnotation_with_id(self, key):
        return key in self.db_actionAnnotations_id_index
    def db_get_actionAnnotation_by_action_id(self, key):
        return self.db_actionAnnotations_action_id_index[key]
    def db_has_actionAnnotation_with_action_id(self, key):
        return key in self.db_actionAnnotations_action_id_index
    def db_get_actionAnnotation_by_key(self, key):
        return self.db_actionAnnotations_key_index[key]
    def db_has_actionAnnotation_with_key(self, key):
        return key in self.db_actionAnnotations_key_index
    
    def getPrimaryKey(self):
        return self._db_id

class DBLog(object):

    vtType = 'log'

    def __init__(self, id=None, entity_type=None, version=None, name=None, last_modified=None, workflow_execs=None, machines=None, vistrail_id=None):
        self._db_id = id
        self._db_entity_type = entity_type
        self._db_version = version
        self._db_name = name
        self._db_last_modified = last_modified
        self.db_deleted_workflow_execs = []
        self.db_workflow_execs_id_index = {}
        if workflow_execs is None:
            self._db_workflow_execs = []
        else:
            self._db_workflow_execs = workflow_execs
            for v in self._db_workflow_execs:
                self.db_workflow_execs_id_index[v.db_id] = v
        self.db_deleted_machines = []
        self.db_machines_id_index = {}
        if machines is None:
            self._db_machines = []
        else:
            self._db_machines = machines
            for v in self._db_machines:
                self.db_machines_id_index[v.db_id] = v
        self._db_vistrail_id = vistrail_id
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBLog.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBLog(id=self._db_id,
                   entity_type=self._db_entity_type,
                   version=self._db_version,
                   name=self._db_name,
                   last_modified=self._db_last_modified,
                   vistrail_id=self._db_vistrail_id)
        if self._db_workflow_execs is None:
            cp._db_workflow_execs = []
        else:
            cp._db_workflow_execs = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_workflow_execs]
        if self._db_machines is None:
            cp._db_machines = []
        else:
            cp._db_machines = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_machines]
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
            if hasattr(self, 'db_vistrail_id') and ('vistrail', self._db_vistrail_id) in id_remap:
                cp._db_vistrail_id = id_remap[('vistrail', self._db_vistrail_id)]
        
        # recreate indices and set flags
        cp.db_workflow_execs_id_index = dict((v.db_id, v) for v in cp._db_workflow_execs)
        cp.db_machines_id_index = dict((v.db_id, v) for v in cp._db_machines)
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBLog()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'entity_type' in class_dict:
            res = class_dict['entity_type'](old_obj, trans_dict)
            new_obj.db_entity_type = res
        elif hasattr(old_obj, 'db_entity_type') and old_obj.db_entity_type is not None:
            new_obj.db_entity_type = old_obj.db_entity_type
        if 'version' in class_dict:
            res = class_dict['version'](old_obj, trans_dict)
            new_obj.db_version = res
        elif hasattr(old_obj, 'db_version') and old_obj.db_version is not None:
            new_obj.db_version = old_obj.db_version
        if 'name' in class_dict:
            res = class_dict['name'](old_obj, trans_dict)
            new_obj.db_name = res
        elif hasattr(old_obj, 'db_name') and old_obj.db_name is not None:
            new_obj.db_name = old_obj.db_name
        if 'last_modified' in class_dict:
            res = class_dict['last_modified'](old_obj, trans_dict)
            new_obj.db_last_modified = res
        elif hasattr(old_obj, 'db_last_modified') and old_obj.db_last_modified is not None:
            new_obj.db_last_modified = old_obj.db_last_modified
        if 'workflow_execs' in class_dict:
            res = class_dict['workflow_execs'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_workflow_exec(obj)
        elif hasattr(old_obj, 'db_workflow_execs') and old_obj.db_workflow_execs is not None:
            for obj in old_obj.db_workflow_execs:
                new_obj.db_add_workflow_exec(DBWorkflowExec.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_workflow_execs') and hasattr(new_obj, 'db_deleted_workflow_execs'):
            for obj in old_obj.db_deleted_workflow_execs:
                n_obj = DBWorkflowExec.update_version(obj, trans_dict)
                new_obj.db_deleted_workflow_execs.append(n_obj)
        if 'machines' in class_dict:
            res = class_dict['machines'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_machine(obj)
        elif hasattr(old_obj, 'db_machines') and old_obj.db_machines is not None:
            for obj in old_obj.db_machines:
                new_obj.db_add_machine(DBMachine.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_machines') and hasattr(new_obj, 'db_deleted_machines'):
            for obj in old_obj.db_deleted_machines:
                n_obj = DBMachine.update_version(obj, trans_dict)
                new_obj.db_deleted_machines.append(n_obj)
        if 'vistrail_id' in class_dict:
            res = class_dict['vistrail_id'](old_obj, trans_dict)
            new_obj.db_vistrail_id = res
        elif hasattr(old_obj, 'db_vistrail_id') and old_obj.db_vistrail_id is not None:
            new_obj.db_vistrail_id = old_obj.db_vistrail_id
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False):
        children = []
        to_del = []
        for child in self.db_workflow_execs:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_workflow_exec(child)
        to_del = []
        for child in self.db_machines:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_machine(child)
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_workflow_execs)
        children.extend(self.db_deleted_machines)
        if remove:
            self.db_deleted_workflow_execs = []
            self.db_deleted_machines = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        for child in self._db_workflow_execs:
            if child.has_changes():
                return True
        for child in self._db_machines:
            if child.has_changes():
                return True
        return False
    def __get_db_id(self):
        return self._db_id
    def __set_db_id(self, id):
        self._db_id = id
        self.is_dirty = True
    db_id = property(__get_db_id, __set_db_id)
    def db_add_id(self, id):
        self._db_id = id
    def db_change_id(self, id):
        self._db_id = id
    def db_delete_id(self, id):
        self._db_id = None
    
    def __get_db_entity_type(self):
        return self._db_entity_type
    def __set_db_entity_type(self, entity_type):
        self._db_entity_type = entity_type
        self.is_dirty = True
    db_entity_type = property(__get_db_entity_type, __set_db_entity_type)
    def db_add_entity_type(self, entity_type):
        self._db_entity_type = entity_type
    def db_change_entity_type(self, entity_type):
        self._db_entity_type = entity_type
    def db_delete_entity_type(self, entity_type):
        self._db_entity_type = None
    
    def __get_db_version(self):
        return self._db_version
    def __set_db_version(self, version):
        self._db_version = version
        self.is_dirty = True
    db_version = property(__get_db_version, __set_db_version)
    def db_add_version(self, version):
        self._db_version = version
    def db_change_version(self, version):
        self._db_version = version
    def db_delete_version(self, version):
        self._db_version = None
    
    def __get_db_name(self):
        return self._db_name
    def __set_db_name(self, name):
        self._db_name = name
        self.is_dirty = True
    db_name = property(__get_db_name, __set_db_name)
    def db_add_name(self, name):
        self._db_name = name
    def db_change_name(self, name):
        self._db_name = name
    def db_delete_name(self, name):
        self._db_name = None
    
    def __get_db_last_modified(self):
        return self._db_last_modified
    def __set_db_last_modified(self, last_modified):
        self._db_last_modified = last_modified
        self.is_dirty = True
    db_last_modified = property(__get_db_last_modified, __set_db_last_modified)
    def db_add_last_modified(self, last_modified):
        self._db_last_modified = last_modified
    def db_change_last_modified(self, last_modified):
        self._db_last_modified = last_modified
    def db_delete_last_modified(self, last_modified):
        self._db_last_modified = None
    
    def __get_db_workflow_execs(self):
        return self._db_workflow_execs
    def __set_db_workflow_execs(self, workflow_execs):
        self._db_workflow_execs = workflow_execs
        self.is_dirty = True
    db_workflow_execs = property(__get_db_workflow_execs, __set_db_workflow_execs)
    def db_get_workflow_execs(self):
        return self._db_workflow_execs
    def db_add_workflow_exec(self, workflow_exec):
        self.is_dirty = True
        self._db_workflow_execs.append(workflow_exec)
        self.db_workflow_execs_id_index[workflow_exec.db_id] = workflow_exec
    def db_change_workflow_exec(self, workflow_exec):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_workflow_execs)):
            if self._db_workflow_execs[i].db_id == workflow_exec.db_id:
                self._db_workflow_execs[i] = workflow_exec
                found = True
                break
        if not found:
            self._db_workflow_execs.append(workflow_exec)
        self.db_workflow_execs_id_index[workflow_exec.db_id] = workflow_exec
    def db_delete_workflow_exec(self, workflow_exec):
        print "delwfexecid=", workflow_exec.db_id
        print "wfexecids=", [i.db_id for i in self._db_workflow_execs]
        print "wfexecidindex=", self.db_workflow_execs_id_index
        self.is_dirty = True
        for i in xrange(len(self._db_workflow_execs)):
            if self._db_workflow_execs[i].db_id == workflow_exec.db_id:
                if not self._db_workflow_execs[i].is_new:
                    self.db_deleted_workflow_execs.append(self._db_workflow_execs[i])
                del self._db_workflow_execs[i]
                break
        del self.db_workflow_execs_id_index[workflow_exec.db_id]
    def db_get_workflow_exec(self, key):
        for i in xrange(len(self._db_workflow_execs)):
            if self._db_workflow_execs[i].db_id == key:
                return self._db_workflow_execs[i]
        return None
    def db_get_workflow_exec_by_id(self, key):
        return self.db_workflow_execs_id_index[key]
    def db_has_workflow_exec_with_id(self, key):
        return key in self.db_workflow_execs_id_index
    
    def __get_db_machines(self):
        return self._db_machines
    def __set_db_machines(self, machines):
        self._db_machines = machines
        self.is_dirty = True
    db_machines = property(__get_db_machines, __set_db_machines)
    def db_get_machines(self):
        return self._db_machines
    def db_add_machine(self, machine):
        self.is_dirty = True
        self._db_machines.append(machine)
        self.db_machines_id_index[machine.db_id] = machine
    def db_change_machine(self, machine):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_machines)):
            if self._db_machines[i].db_id == machine.db_id:
                self._db_machines[i] = machine
                found = True
                break
        if not found:
            self._db_machines.append(machine)
        self.db_machines_id_index[machine.db_id] = machine
    def db_delete_machine(self, machine):
        self.is_dirty = True
        for i in xrange(len(self._db_machines)):
            if self._db_machines[i].db_id == machine.db_id:
                if not self._db_machines[i].is_new:
                    self.db_deleted_machines.append(self._db_machines[i])
                del self._db_machines[i]
                break
        del self.db_machines_id_index[machine.db_id]
    def db_get_machine(self, key):
        for i in xrange(len(self._db_machines)):
            if self._db_machines[i].db_id == key:
                return self._db_machines[i]
        return None
    def db_get_machine_by_id(self, key):
        return self.db_machines_id_index[key]
    def db_has_machine_with_id(self, key):
        return key in self.db_machines_id_index
    
    def __get_db_vistrail_id(self):
        return self._db_vistrail_id
    def __set_db_vistrail_id(self, vistrail_id):
        self._db_vistrail_id = vistrail_id
        self.is_dirty = True
    db_vistrail_id = property(__get_db_vistrail_id, __set_db_vistrail_id)
    def db_add_vistrail_id(self, vistrail_id):
        self._db_vistrail_id = vistrail_id
    def db_change_vistrail_id(self, vistrail_id):
        self._db_vistrail_id = vistrail_id
    def db_delete_vistrail_id(self, vistrail_id):
        self._db_vistrail_id = None
    
    def getPrimaryKey(self):
        return self._db_id
    
class DBMachine(object):

    vtType = 'machine'

    def __init__(self, id=None, name=None, os=None, architecture=None, processor=None, ram=None):
        self._db_id = id
        self._db_name = name
        self._db_os = os
        self._db_architecture = architecture
        self._db_processor = processor
        self._db_ram = ram
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBMachine.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBMachine(id=self._db_id,
                       name=self._db_name,
                       os=self._db_os,
                       architecture=self._db_architecture,
                       processor=self._db_processor,
                       ram=self._db_ram)
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
            if hasattr(self, 'db_vistrailId') and ('vistrail', self._db_vistrailId) in id_remap:
                cp._db_vistrailId = id_remap[('vistrail', self._db_vistrailId)]
        
        # recreate indices and set flags
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBMachine()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'name' in class_dict:
            res = class_dict['name'](old_obj, trans_dict)
            new_obj.db_name = res
        elif hasattr(old_obj, 'db_name') and old_obj.db_name is not None:
            new_obj.db_name = old_obj.db_name
        if 'os' in class_dict:
            res = class_dict['os'](old_obj, trans_dict)
            new_obj.db_os = res
        elif hasattr(old_obj, 'db_os') and old_obj.db_os is not None:
            new_obj.db_os = old_obj.db_os
        if 'architecture' in class_dict:
            res = class_dict['architecture'](old_obj, trans_dict)
            new_obj.db_architecture = res
        elif hasattr(old_obj, 'db_architecture') and old_obj.db_architecture is not None:
            new_obj.db_architecture = old_obj.db_architecture
        if 'processor' in class_dict:
            res = class_dict['processor'](old_obj, trans_dict)
            new_obj.db_processor = res
        elif hasattr(old_obj, 'db_processor') and old_obj.db_processor is not None:
            new_obj.db_processor = old_obj.db_processor
        if 'ram' in class_dict:
            res = class_dict['ram'](old_obj, trans_dict)
            new_obj.db_ram = res
        elif hasattr(old_obj, 'db_ram') and old_obj.db_ram is not None:
            new_obj.db_ram = old_obj.db_ram
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False):
        return [(self, parent[0], parent[1])]
    def db_deleted_children(self, remove=False):
        children = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        return False
    def __get_db_id(self):
        return self._db_id
    def __set_db_id(self, id):
        self._db_id = id
        self.is_dirty = True
    db_id = property(__get_db_id, __set_db_id)
    def db_add_id(self, id):
        self._db_id = id
    def db_change_id(self, id):
        self._db_id = id
    def db_delete_id(self, id):
        self._db_id = None
    
    def __get_db_name(self):
        return self._db_name
    def __set_db_name(self, name):
        self._db_name = name
        self.is_dirty = True
    db_name = property(__get_db_name, __set_db_name)
    def db_add_name(self, name):
        self._db_name = name
    def db_change_name(self, name):
        self._db_name = name
    def db_delete_name(self, name):
        self._db_name = None
    
    def __get_db_os(self):
        return self._db_os
    def __set_db_os(self, os):
        self._db_os = os
        self.is_dirty = True
    db_os = property(__get_db_os, __set_db_os)
    def db_add_os(self, os):
        self._db_os = os
    def db_change_os(self, os):
        self._db_os = os
    def db_delete_os(self, os):
        self._db_os = None
    
    def __get_db_architecture(self):
        return self._db_architecture
    def __set_db_architecture(self, architecture):
        self._db_architecture = architecture
        self.is_dirty = True
    db_architecture = property(__get_db_architecture, __set_db_architecture)
    def db_add_architecture(self, architecture):
        self._db_architecture = architecture
    def db_change_architecture(self, architecture):
        self._db_architecture = architecture
    def db_delete_architecture(self, architecture):
        self._db_architecture = None
    
    def __get_db_processor(self):
        return self._db_processor
    def __set_db_processor(self, processor):
        self._db_processor = processor
        self.is_dirty = True
    db_processor = property(__get_db_processor, __set_db_processor)
    def db_add_processor(self, processor):
        self._db_processor = processor
    def db_change_processor(self, processor):
        self._db_processor = processor
    def db_delete_processor(self, processor):
        self._db_processor = None
    
    def __get_db_ram(self):
        return self._db_ram
    def __set_db_ram(self, ram):
        self._db_ram = ram
        self.is_dirty = True
    db_ram = property(__get_db_ram, __set_db_ram)
    def db_add_ram(self, ram):
        self._db_ram = ram
    def db_change_ram(self, ram):
        self._db_ram = ram
    def db_delete_ram(self, ram):
        self._db_ram = None
    
    def getPrimaryKey(self):
        return self._db_id

class DBOpmGraph(object):

    vtType = 'opm_graph'

    def __init__(self, accounts=None, processes=None, artifacts=None, agents=None, dependencies=None):
        self.db_deleted_accounts = []
        self._db_accounts = accounts
        self.db_deleted_processes = []
        self._db_processes = processes
        self.db_deleted_artifacts = []
        self._db_artifacts = artifacts
        self.db_deleted_agents = []
        self._db_agents = agents
        self.db_deleted_dependencies = []
        self._db_dependencies = dependencies
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBOpmGraph.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBOpmGraph()
        if self._db_accounts is not None:
            cp._db_accounts = self._db_accounts.do_copy(new_ids, id_scope, id_remap)
        if self._db_processes is not None:
            cp._db_processes = self._db_processes.do_copy(new_ids, id_scope, id_remap)
        if self._db_artifacts is not None:
            cp._db_artifacts = self._db_artifacts.do_copy(new_ids, id_scope, id_remap)
        if self._db_agents is not None:
            cp._db_agents = self._db_agents.do_copy(new_ids, id_scope, id_remap)
        if self._db_dependencies is not None:
            cp._db_dependencies = self._db_dependencies.do_copy(new_ids, id_scope, id_remap)
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
        
        # recreate indices and set flags
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBOpmGraph()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'accounts' in class_dict:
            res = class_dict['accounts'](old_obj, trans_dict)
            new_obj.db_accounts = res
        elif hasattr(old_obj, 'db_accounts') and old_obj.db_accounts is not None:
            obj = old_obj.db_accounts
            new_obj.db_add_accounts(DBOpmAccounts.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_accounts') and hasattr(new_obj, 'db_deleted_accounts'):
            for obj in old_obj.db_deleted_accounts:
                n_obj = DBOpmAccounts.update_version(obj, trans_dict)
                new_obj.db_deleted_accounts.append(n_obj)
        if 'processes' in class_dict:
            res = class_dict['processes'](old_obj, trans_dict)
            new_obj.db_processes = res
        elif hasattr(old_obj, 'db_processes') and old_obj.db_processes is not None:
            obj = old_obj.db_processes
            new_obj.db_add_processes(DBOpmProcesses.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_processes') and hasattr(new_obj, 'db_deleted_processes'):
            for obj in old_obj.db_deleted_processes:
                n_obj = DBOpmProcesses.update_version(obj, trans_dict)
                new_obj.db_deleted_processes.append(n_obj)
        if 'artifacts' in class_dict:
            res = class_dict['artifacts'](old_obj, trans_dict)
            new_obj.db_artifacts = res
        elif hasattr(old_obj, 'db_artifacts') and old_obj.db_artifacts is not None:
            obj = old_obj.db_artifacts
            new_obj.db_add_artifacts(DBOpmArtifacts.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_artifacts') and hasattr(new_obj, 'db_deleted_artifacts'):
            for obj in old_obj.db_deleted_artifacts:
                n_obj = DBOpmArtifacts.update_version(obj, trans_dict)
                new_obj.db_deleted_artifacts.append(n_obj)
        if 'agents' in class_dict:
            res = class_dict['agents'](old_obj, trans_dict)
            new_obj.db_agents = res
        elif hasattr(old_obj, 'db_agents') and old_obj.db_agents is not None:
            obj = old_obj.db_agents
            new_obj.db_add_agents(DBOpmAgents.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_agents') and hasattr(new_obj, 'db_deleted_agents'):
            for obj in old_obj.db_deleted_agents:
                n_obj = DBOpmAgents.update_version(obj, trans_dict)
                new_obj.db_deleted_agents.append(n_obj)
        if 'dependencies' in class_dict:
            res = class_dict['dependencies'](old_obj, trans_dict)
            new_obj.db_dependencies = res
        elif hasattr(old_obj, 'db_dependencies') and old_obj.db_dependencies is not None:
            obj = old_obj.db_dependencies
            new_obj.db_add_dependencies(DBOpmDependencies.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_dependencies') and hasattr(new_obj, 'db_deleted_dependencies'):
            for obj in old_obj.db_deleted_dependencies:
                n_obj = DBOpmDependencies.update_version(obj, trans_dict)
                new_obj.db_deleted_dependencies.append(n_obj)
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False):
        children = []
        if self._db_accounts is not None:
            children.extend(self._db_accounts.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                self._db_accounts = None
        if self._db_processes is not None:
            children.extend(self._db_processes.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                self._db_processes = None
        if self._db_artifacts is not None:
            children.extend(self._db_artifacts.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                self._db_artifacts = None
        if self._db_agents is not None:
            children.extend(self._db_agents.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                self._db_agents = None
        if self._db_dependencies is not None:
            children.extend(self._db_dependencies.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                self._db_dependencies = None
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_accounts)
        children.extend(self.db_deleted_processes)
        children.extend(self.db_deleted_artifacts)
        children.extend(self.db_deleted_agents)
        children.extend(self.db_deleted_dependencies)
        if remove:
            self.db_deleted_accounts = []
            self.db_deleted_processes = []
            self.db_deleted_artifacts = []
            self.db_deleted_agents = []
            self.db_deleted_dependencies = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        if self._db_accounts is not None and self._db_accounts.has_changes():
            return True
        if self._db_processes is not None and self._db_processes.has_changes():
            return True
        if self._db_artifacts is not None and self._db_artifacts.has_changes():
            return True
        if self._db_agents is not None and self._db_agents.has_changes():
            return True
        if self._db_dependencies is not None and self._db_dependencies.has_changes():
            return True
        return False
    def __get_db_accounts(self):
        return self._db_accounts
    def __set_db_accounts(self, accounts):
        self._db_accounts = accounts
        self.is_dirty = True
    db_accounts = property(__get_db_accounts, __set_db_accounts)
    def db_add_accounts(self, accounts):
        self._db_accounts = accounts
    def db_change_accounts(self, accounts):
        self._db_accounts = accounts
    def db_delete_accounts(self, accounts):
        if not self.is_new:
            self.db_deleted_accounts.append(self._db_accounts)
        self._db_accounts = None
    
    def __get_db_processes(self):
        return self._db_processes
    def __set_db_processes(self, processes):
        self._db_processes = processes
        self.is_dirty = True
    db_processes = property(__get_db_processes, __set_db_processes)
    def db_add_processes(self, processes):
        self._db_processes = processes
    def db_change_processes(self, processes):
        self._db_processes = processes
    def db_delete_processes(self, processes):
        if not self.is_new:
            self.db_deleted_processes.append(self._db_processes)
        self._db_processes = None
    
    def __get_db_artifacts(self):
        return self._db_artifacts
    def __set_db_artifacts(self, artifacts):
        self._db_artifacts = artifacts
        self.is_dirty = True
    db_artifacts = property(__get_db_artifacts, __set_db_artifacts)
    def db_add_artifacts(self, artifacts):
        self._db_artifacts = artifacts
    def db_change_artifacts(self, artifacts):
        self._db_artifacts = artifacts
    def db_delete_artifacts(self, artifacts):
        if not self.is_new:
            self.db_deleted_artifacts.append(self._db_artifacts)
        self._db_artifacts = None
    
    def __get_db_agents(self):
        return self._db_agents
    def __set_db_agents(self, agents):
        self._db_agents = agents
        self.is_dirty = True
    db_agents = property(__get_db_agents, __set_db_agents)
    def db_add_agents(self, agents):
        self._db_agents = agents
    def db_change_agents(self, agents):
        self._db_agents = agents
    def db_delete_agents(self, agents):
        if not self.is_new:
            self.db_deleted_agents.append(self._db_agents)
        self._db_agents = None
    
    def __get_db_dependencies(self):
        return self._db_dependencies
    def __set_db_dependencies(self, dependencies):
        self._db_dependencies = dependencies
        self.is_dirty = True
    db_dependencies = property(__get_db_dependencies, __set_db_dependencies)
    def db_add_dependencies(self, dependencies):
        self._db_dependencies = dependencies
    def db_change_dependencies(self, dependencies):
        self._db_dependencies = dependencies
    def db_delete_dependencies(self, dependencies):
        if not self.is_new:
            self.db_deleted_dependencies.append(self._db_dependencies)
        self._db_dependencies = None
        
class DBOpmDependencies(object):

    vtType = 'opm_dependencies'

    def __init__(self, dependencys=None):
        self.db_deleted_dependencys = []
        if dependencys is None:
            self._db_dependencys = []
        else:
            self._db_dependencys = dependencys
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBOpmDependencies.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBOpmDependencies()
        if self._db_dependencys is None:
            cp._db_dependencys = []
        else:
            cp._db_dependencys = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_dependencys]
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
        
        # recreate indices and set flags
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBOpmDependencies()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'dependencys' in class_dict:
            res = class_dict['dependencys'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_dependency(obj)
        elif hasattr(old_obj, 'db_dependencys') and old_obj.db_dependencys is not None:
            for obj in old_obj.db_dependencys:
                if obj.vtType == 'opm_used':
                    new_obj.db_add_dependency(DBOpmUsed.update_version(obj, trans_dict))
                elif obj.vtType == 'opm_was_generated_by':
                    new_obj.db_add_dependency(DBOpmWasGeneratedBy.update_version(obj, trans_dict))
                elif obj.vtType == 'opm_was_triggered_by':
                    new_obj.db_add_dependency(DBOpmWasTriggeredBy.update_version(obj, trans_dict))
                elif obj.vtType == 'opm_was_derived_from':
                    new_obj.db_add_dependency(DBOpmWasDerivedFrom.update_version(obj, trans_dict))
                elif obj.vtType == 'opm_was_controlled_by':
                    new_obj.db_add_dependency(DBOpmWasControlledBy.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_dependencys') and hasattr(new_obj, 'db_deleted_dependencys'):
            for obj in old_obj.db_deleted_dependencys:
                if obj.vtType == 'opm_used':
                    n_obj = DBOpmUsed.update_version(obj, trans_dict)
                    new_obj.db_deleted_dependencys.append(n_obj)
                elif obj.vtType == 'opm_was_generated_by':
                    n_obj = DBOpmWasGeneratedBy.update_version(obj, trans_dict)
                    new_obj.db_deleted_dependencys.append(n_obj)
                elif obj.vtType == 'opm_was_triggered_by':
                    n_obj = DBOpmWasTriggeredBy.update_version(obj, trans_dict)
                    new_obj.db_deleted_dependencys.append(n_obj)
                elif obj.vtType == 'opm_was_derived_from':
                    n_obj = DBOpmWasDerivedFrom.update_version(obj, trans_dict)
                    new_obj.db_deleted_dependencys.append(n_obj)
                elif obj.vtType == 'opm_was_controlled_by':
                    n_obj = DBOpmWasControlledBy.update_version(obj, trans_dict)
                    new_obj.db_deleted_dependencys.append(n_obj)
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False):
        children = []
        to_del = []
        for child in self.db_dependencys:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_dependency(child)
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_dependencys)
        if remove:
            self.db_deleted_dependencys = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        for child in self._db_dependencys:
            if child.has_changes():
                return True
        return False
    def __get_db_dependencys(self):
        return self._db_dependencys
    def __set_db_dependencys(self, dependencys):
        self._db_dependencys = dependencys
        self.is_dirty = True
    db_dependencys = property(__get_db_dependencys, __set_db_dependencys)
    def db_get_dependencys(self):
        return self._db_dependencys
    def db_add_dependency(self, dependency):
        self.is_dirty = True
        self._db_dependencys.append(dependency)
    def db_change_dependency(self, dependency):
        self.is_dirty = True
        self._db_dependencys.append(dependency)
    def db_delete_dependency(self, dependency):
        self.is_dirty = True
        raise Exception('Cannot delete a non-keyed object')
    def db_get_dependency(self, key):
        return None
    
class DBOpmAgents(object):

    vtType = 'opm_agents'

    def __init__(self, agents=None):
        self.db_deleted_agents = []
        self.db_agents_id_index = {}
        if agents is None:
            self._db_agents = []
        else:
            self._db_agents = agents
            for v in self._db_agents:
                self.db_agents_id_index[v.db_id] = v
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBOpmAgents.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBOpmAgents()
        if self._db_agents is None:
            cp._db_agents = []
        else:
            cp._db_agents = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_agents]
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
        
        # recreate indices and set flags
        cp.db_agents_id_index = dict((v.db_id, v) for v in cp._db_agents)
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBOpmAgents()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'agents' in class_dict:
            res = class_dict['agents'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_agent(obj)
        elif hasattr(old_obj, 'db_agents') and old_obj.db_agents is not None:
            for obj in old_obj.db_agents:
                new_obj.db_add_agent(DBOpmAgent.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_agents') and hasattr(new_obj, 'db_deleted_agents'):
            for obj in old_obj.db_deleted_agents:
                n_obj = DBOpmAgent.update_version(obj, trans_dict)
                new_obj.db_deleted_agents.append(n_obj)
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False):
        children = []
        to_del = []
        for child in self.db_agents:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_agent(child)
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_agents)
        if remove:
            self.db_deleted_agents = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        for child in self._db_agents:
            if child.has_changes():
                return True
        return False
    def __get_db_agents(self):
        return self._db_agents
    def __set_db_agents(self, agents):
        self._db_agents = agents
        self.is_dirty = True
    db_agents = property(__get_db_agents, __set_db_agents)
    def db_get_agents(self):
        return self._db_agents
    def db_add_agent(self, agent):
        self.is_dirty = True
        self._db_agents.append(agent)
        self.db_agents_id_index[agent.db_id] = agent
    def db_change_agent(self, agent):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_agents)):
            if self._db_agents[i].db_id == agent.db_id:
                self._db_agents[i] = agent
                found = True
                break
        if not found:
            self._db_agents.append(agent)
        self.db_agents_id_index[agent.db_id] = agent
    def db_delete_agent(self, agent):
        self.is_dirty = True
        for i in xrange(len(self._db_agents)):
            if self._db_agents[i].db_id == agent.db_id:
                if not self._db_agents[i].is_new:
                    self.db_deleted_agents.append(self._db_agents[i])
                del self._db_agents[i]
                break
        del self.db_agents_id_index[agent.db_id]
    def db_get_agent(self, key):
        for i in xrange(len(self._db_agents)):
            if self._db_agents[i].db_id == key:
                return self._db_agents[i]
        return None
    def db_get_agent_by_id(self, key):
        return self.db_agents_id_index[key]
    def db_has_agent_with_id(self, key):
        return key in self.db_agents_id_index

class DBOpmProcesses(object):

    vtType = 'opm_processes'

    def __init__(self, processs=None):
        self.db_deleted_processs = []
        self.db_processs_id_index = {}
        if processs is None:
            self._db_processs = []
        else:
            self._db_processs = processs
            for v in self._db_processs:
                self.db_processs_id_index[v.db_id] = v
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBOpmProcesses.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBOpmProcesses()
        if self._db_processs is None:
            cp._db_processs = []
        else:
            cp._db_processs = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_processs]
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
        
        # recreate indices and set flags
        cp.db_processs_id_index = dict((v.db_id, v) for v in cp._db_processs)
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBOpmProcesses()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'processs' in class_dict:
            res = class_dict['processs'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_process(obj)
        elif hasattr(old_obj, 'db_processs') and old_obj.db_processs is not None:
            for obj in old_obj.db_processs:
                new_obj.db_add_process(DBOpmProcess.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_processs') and hasattr(new_obj, 'db_deleted_processs'):
            for obj in old_obj.db_deleted_processs:
                n_obj = DBOpmProcess.update_version(obj, trans_dict)
                new_obj.db_deleted_processs.append(n_obj)
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False):
        children = []
        to_del = []
        for child in self.db_processs:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_process(child)
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_processs)
        if remove:
            self.db_deleted_processs = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        for child in self._db_processs:
            if child.has_changes():
                return True
        return False
    def __get_db_processs(self):
        return self._db_processs
    def __set_db_processs(self, processs):
        self._db_processs = processs
        self.is_dirty = True
    db_processs = property(__get_db_processs, __set_db_processs)
    def db_get_processs(self):
        return self._db_processs
    def db_add_process(self, process):
        self.is_dirty = True
        self._db_processs.append(process)
        self.db_processs_id_index[process.db_id] = process
    def db_change_process(self, process):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_processs)):
            if self._db_processs[i].db_id == process.db_id:
                self._db_processs[i] = process
                found = True
                break
        if not found:
            self._db_processs.append(process)
        self.db_processs_id_index[process.db_id] = process
    def db_delete_process(self, process):
        self.is_dirty = True
        for i in xrange(len(self._db_processs)):
            if self._db_processs[i].db_id == process.db_id:
                if not self._db_processs[i].is_new:
                    self.db_deleted_processs.append(self._db_processs[i])
                del self._db_processs[i]
                break
        del self.db_processs_id_index[process.db_id]
    def db_get_process(self, key):
        for i in xrange(len(self._db_processs)):
            if self._db_processs[i].db_id == key:
                return self._db_processs[i]
        return None
    def db_get_process_by_id(self, key):
        return self.db_processs_id_index[key]
    def db_has_process_with_id(self, key):
        return key in self.db_processs_id_index
    
class DBOpmAccounts(object):

    vtType = 'opm_accounts'

    def __init__(self, accounts=None, opm_overlapss=None):
        self.db_deleted_accounts = []
        self.db_accounts_id_index = {}
        if accounts is None:
            self._db_accounts = []
        else:
            self._db_accounts = accounts
            for v in self._db_accounts:
                self.db_accounts_id_index[v.db_id] = v
        self.db_deleted_opm_overlapss = []
        if opm_overlapss is None:
            self._db_opm_overlapss = []
        else:
            self._db_opm_overlapss = opm_overlapss
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBOpmAccounts.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBOpmAccounts()
        if self._db_accounts is None:
            cp._db_accounts = []
        else:
            cp._db_accounts = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_accounts]
        if self._db_opm_overlapss is None:
            cp._db_opm_overlapss = []
        else:
            cp._db_opm_overlapss = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_opm_overlapss]
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
        
        # recreate indices and set flags
        cp.db_accounts_id_index = dict((v.db_id, v) for v in cp._db_accounts)
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBOpmAccounts()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'accounts' in class_dict:
            res = class_dict['accounts'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_account(obj)
        elif hasattr(old_obj, 'db_accounts') and old_obj.db_accounts is not None:
            for obj in old_obj.db_accounts:
                new_obj.db_add_account(DBOpmAccount.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_accounts') and hasattr(new_obj, 'db_deleted_accounts'):
            for obj in old_obj.db_deleted_accounts:
                n_obj = DBOpmAccount.update_version(obj, trans_dict)
                new_obj.db_deleted_accounts.append(n_obj)
        if 'opm_overlapss' in class_dict:
            res = class_dict['opm_overlapss'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_opm_overlaps(obj)
        elif hasattr(old_obj, 'db_opm_overlapss') and old_obj.db_opm_overlapss is not None:
            for obj in old_obj.db_opm_overlapss:
                new_obj.db_add_opm_overlaps(DBOpmOverlaps.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_opm_overlapss') and hasattr(new_obj, 'db_deleted_opm_overlapss'):
            for obj in old_obj.db_deleted_opm_overlapss:
                n_obj = DBOpmOverlaps.update_version(obj, trans_dict)
                new_obj.db_deleted_opm_overlapss.append(n_obj)
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False):
        children = []
        to_del = []
        for child in self.db_accounts:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_account(child)
        to_del = []
        for child in self.db_opm_overlapss:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_opm_overlaps(child)
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_accounts)
        children.extend(self.db_deleted_opm_overlapss)
        if remove:
            self.db_deleted_accounts = []
            self.db_deleted_opm_overlapss = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        for child in self._db_accounts:
            if child.has_changes():
                return True
        for child in self._db_opm_overlapss:
            if child.has_changes():
                return True
        return False
    def __get_db_accounts(self):
        return self._db_accounts
    def __set_db_accounts(self, accounts):
        self._db_accounts = accounts
        self.is_dirty = True
    db_accounts = property(__get_db_accounts, __set_db_accounts)
    def db_get_accounts(self):
        return self._db_accounts
    def db_add_account(self, account):
        self.is_dirty = True
        self._db_accounts.append(account)
        self.db_accounts_id_index[account.db_id] = account
    def db_change_account(self, account):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_accounts)):
            if self._db_accounts[i].db_id == account.db_id:
                self._db_accounts[i] = account
                found = True
                break
        if not found:
            self._db_accounts.append(account)
        self.db_accounts_id_index[account.db_id] = account
    def db_delete_account(self, account):
        self.is_dirty = True
        for i in xrange(len(self._db_accounts)):
            if self._db_accounts[i].db_id == account.db_id:
                if not self._db_accounts[i].is_new:
                    self.db_deleted_accounts.append(self._db_accounts[i])
                del self._db_accounts[i]
                break
        del self.db_accounts_id_index[account.db_id]
    def db_get_account(self, key):
        for i in xrange(len(self._db_accounts)):
            if self._db_accounts[i].db_id == key:
                return self._db_accounts[i]
        return None
    def db_get_account_by_id(self, key):
        return self.db_accounts_id_index[key]
    def db_has_account_with_id(self, key):
        return key in self.db_accounts_id_index
    
    def __get_db_opm_overlapss(self):
        return self._db_opm_overlapss
    def __set_db_opm_overlapss(self, opm_overlapss):
        self._db_opm_overlapss = opm_overlapss
        self.is_dirty = True
    db_opm_overlapss = property(__get_db_opm_overlapss, __set_db_opm_overlapss)
    def db_get_opm_overlapss(self):
        return self._db_opm_overlapss
    def db_add_opm_overlaps(self, opm_overlaps):
        self.is_dirty = True
        self._db_opm_overlapss.append(opm_overlaps)
    def db_change_opm_overlaps(self, opm_overlaps):
        self.is_dirty = True
        self._db_opm_overlapss.append(opm_overlaps)
    def db_delete_opm_overlaps(self, opm_overlaps):
        self.is_dirty = True
        raise Exception('Cannot delete a non-keyed object')
    def db_get_opm_overlaps(self, key):
        return None

class DBOpmArtifacts(object):

    vtType = 'opm_artifacts'

    def __init__(self, artifacts=None):
        self.db_deleted_artifacts = []
        self.db_artifacts_id_index = {}
        if artifacts is None:
            self._db_artifacts = []
        else:
            self._db_artifacts = artifacts
            for v in self._db_artifacts:
                self.db_artifacts_id_index[v.db_id] = v
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBOpmArtifacts.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBOpmArtifacts()
        if self._db_artifacts is None:
            cp._db_artifacts = []
        else:
            cp._db_artifacts = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_artifacts]
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
        
        # recreate indices and set flags
        cp.db_artifacts_id_index = dict((v.db_id, v) for v in cp._db_artifacts)
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBOpmArtifacts()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'artifacts' in class_dict:
            res = class_dict['artifacts'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_artifact(obj)
        elif hasattr(old_obj, 'db_artifacts') and old_obj.db_artifacts is not None:
            for obj in old_obj.db_artifacts:
                new_obj.db_add_artifact(DBOpmArtifact.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_artifacts') and hasattr(new_obj, 'db_deleted_artifacts'):
            for obj in old_obj.db_deleted_artifacts:
                n_obj = DBOpmArtifact.update_version(obj, trans_dict)
                new_obj.db_deleted_artifacts.append(n_obj)
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False):
        children = []
        to_del = []
        for child in self.db_artifacts:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_artifact(child)
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_artifacts)
        if remove:
            self.db_deleted_artifacts = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        for child in self._db_artifacts:
            if child.has_changes():
                return True
        return False
    def __get_db_artifacts(self):
        return self._db_artifacts
    def __set_db_artifacts(self, artifacts):
        self._db_artifacts = artifacts
        self.is_dirty = True
    db_artifacts = property(__get_db_artifacts, __set_db_artifacts)
    def db_get_artifacts(self):
        return self._db_artifacts
    def db_add_artifact(self, artifact):
        self.is_dirty = True
        self._db_artifacts.append(artifact)
        self.db_artifacts_id_index[artifact.db_id] = artifact
    def db_change_artifact(self, artifact):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_artifacts)):
            if self._db_artifacts[i].db_id == artifact.db_id:
                self._db_artifacts[i] = artifact
                found = True
                break
        if not found:
            self._db_artifacts.append(artifact)
        self.db_artifacts_id_index[artifact.db_id] = artifact
    def db_delete_artifact(self, artifact):
        self.is_dirty = True
        for i in xrange(len(self._db_artifacts)):
            if self._db_artifacts[i].db_id == artifact.db_id:
                if not self._db_artifacts[i].is_new:
                    self.db_deleted_artifacts.append(self._db_artifacts[i])
                del self._db_artifacts[i]
                break
        del self.db_artifacts_id_index[artifact.db_id]
    def db_get_artifact(self, key):
        for i in xrange(len(self._db_artifacts)):
            if self._db_artifacts[i].db_id == key:
                return self._db_artifacts[i]
        return None
    def db_get_artifact_by_id(self, key):
        return self.db_artifacts_id_index[key]
    def db_has_artifact_with_id(self, key):
        return key in self.db_artifacts_id_index
    
class DBOpmArtifact(object):

    vtType = 'opm_artifact'

    def __init__(self, id=None, value=None, accounts=None):
        self._db_id = id
        self.db_deleted_value = []
        self._db_value = value
        self.db_deleted_accounts = []
        if accounts is None:
            self._db_accounts = []
        else:
            self._db_accounts = accounts
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBOpmArtifact.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBOpmArtifact(id=self._db_id)
        if self._db_value is not None:
            cp._db_value = self._db_value.do_copy(new_ids, id_scope, id_remap)
        if self._db_accounts is None:
            cp._db_accounts = []
        else:
            cp._db_accounts = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_accounts]
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
        
        # recreate indices and set flags
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBOpmArtifact()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'value' in class_dict:
            res = class_dict['value'](old_obj, trans_dict)
            new_obj.db_value = res
        elif hasattr(old_obj, 'db_value') and old_obj.db_value is not None:
            obj = old_obj.db_value
            new_obj.db_add_value(DBOpmArtifactValue.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_value') and hasattr(new_obj, 'db_deleted_value'):
            for obj in old_obj.db_deleted_value:
                n_obj = DBOpmArtifactValue.update_version(obj, trans_dict)
                new_obj.db_deleted_value.append(n_obj)
        if 'accounts' in class_dict:
            res = class_dict['accounts'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_account(obj)
        elif hasattr(old_obj, 'db_accounts') and old_obj.db_accounts is not None:
            for obj in old_obj.db_accounts:
                new_obj.db_add_account(DBOpmAccountId.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_accounts') and hasattr(new_obj, 'db_deleted_accounts'):
            for obj in old_obj.db_deleted_accounts:
                n_obj = DBOpmAccountId.update_version(obj, trans_dict)
                new_obj.db_deleted_accounts.append(n_obj)
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False):
        children = []
        if self._db_value is not None:
            children.extend(self._db_value.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                self._db_value = None
        to_del = []
        for child in self.db_accounts:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_account(child)
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_value)
        children.extend(self.db_deleted_accounts)
        if remove:
            self.db_deleted_value = []
            self.db_deleted_accounts = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        if self._db_value is not None and self._db_value.has_changes():
            return True
        for child in self._db_accounts:
            if child.has_changes():
                return True
        return False
    def __get_db_id(self):
        return self._db_id
    def __set_db_id(self, id):
        self._db_id = id
        self.is_dirty = True
    db_id = property(__get_db_id, __set_db_id)
    def db_add_id(self, id):
        self._db_id = id
    def db_change_id(self, id):
        self._db_id = id
    def db_delete_id(self, id):
        self._db_id = None
    
    def __get_db_value(self):
        return self._db_value
    def __set_db_value(self, value):
        self._db_value = value
        self.is_dirty = True
    db_value = property(__get_db_value, __set_db_value)
    def db_add_value(self, value):
        self._db_value = value
    def db_change_value(self, value):
        self._db_value = value
    def db_delete_value(self, value):
        if not self.is_new:
            self.db_deleted_value.append(self._db_value)
        self._db_value = None
    
    def __get_db_accounts(self):
        return self._db_accounts
    def __set_db_accounts(self, accounts):
        self._db_accounts = accounts
        self.is_dirty = True
    db_accounts = property(__get_db_accounts, __set_db_accounts)
    def db_get_accounts(self):
        return self._db_accounts
    def db_add_account(self, account):
        self.is_dirty = True
        self._db_accounts.append(account)
    def db_change_account(self, account):
        self.is_dirty = True
        self._db_accounts.append(account)
    def db_delete_account(self, account):
        self.is_dirty = True
        raise Exception('Cannot delete a non-keyed object')
    def db_get_account(self, key):
        return None
    
    def getPrimaryKey(self):
        return self._db_id
    
class DBOpmUsed(object):

    vtType = 'opm_used'

    def __init__(self, effect=None, role=None, cause=None, accounts=None, opm_times=None):
        self.db_deleted_effect = []
        self._db_effect = effect
        self.db_deleted_role = []
        self._db_role = role
        self.db_deleted_cause = []
        self._db_cause = cause
        self.db_deleted_accounts = []
        if accounts is None:
            self._db_accounts = []
        else:
            self._db_accounts = accounts
        self.db_deleted_opm_times = []
        if opm_times is None:
            self._db_opm_times = []
        else:
            self._db_opm_times = opm_times
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBOpmUsed.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBOpmUsed()
        if self._db_effect is not None:
            cp._db_effect = self._db_effect.do_copy(new_ids, id_scope, id_remap)
        if self._db_role is not None:
            cp._db_role = self._db_role.do_copy(new_ids, id_scope, id_remap)
        if self._db_cause is not None:
            cp._db_cause = self._db_cause.do_copy(new_ids, id_scope, id_remap)
        if self._db_accounts is None:
            cp._db_accounts = []
        else:
            cp._db_accounts = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_accounts]
        if self._db_opm_times is None:
            cp._db_opm_times = []
        else:
            cp._db_opm_times = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_opm_times]
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
        
        # recreate indices and set flags
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBOpmUsed()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'effect' in class_dict:
            res = class_dict['effect'](old_obj, trans_dict)
            new_obj.db_effect = res
        elif hasattr(old_obj, 'db_effect') and old_obj.db_effect is not None:
            obj = old_obj.db_effect
            new_obj.db_add_effect(DBOpmProcessIdEffect.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_effect') and hasattr(new_obj, 'db_deleted_effect'):
            for obj in old_obj.db_deleted_effect:
                n_obj = DBOpmProcessIdEffect.update_version(obj, trans_dict)
                new_obj.db_deleted_effect.append(n_obj)
        if 'role' in class_dict:
            res = class_dict['role'](old_obj, trans_dict)
            new_obj.db_role = res
        elif hasattr(old_obj, 'db_role') and old_obj.db_role is not None:
            obj = old_obj.db_role
            new_obj.db_add_role(DBOpmRole.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_role') and hasattr(new_obj, 'db_deleted_role'):
            for obj in old_obj.db_deleted_role:
                n_obj = DBOpmRole.update_version(obj, trans_dict)
                new_obj.db_deleted_role.append(n_obj)
        if 'cause' in class_dict:
            res = class_dict['cause'](old_obj, trans_dict)
            new_obj.db_cause = res
        elif hasattr(old_obj, 'db_cause') and old_obj.db_cause is not None:
            obj = old_obj.db_cause
            new_obj.db_add_cause(DBOpmArtifactIdCause.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_cause') and hasattr(new_obj, 'db_deleted_cause'):
            for obj in old_obj.db_deleted_cause:
                n_obj = DBOpmArtifactIdCause.update_version(obj, trans_dict)
                new_obj.db_deleted_cause.append(n_obj)
        if 'accounts' in class_dict:
            res = class_dict['accounts'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_account(obj)
        elif hasattr(old_obj, 'db_accounts') and old_obj.db_accounts is not None:
            for obj in old_obj.db_accounts:
                new_obj.db_add_account(DBOpmAccountId.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_accounts') and hasattr(new_obj, 'db_deleted_accounts'):
            for obj in old_obj.db_deleted_accounts:
                n_obj = DBOpmAccountId.update_version(obj, trans_dict)
                new_obj.db_deleted_accounts.append(n_obj)
        if 'opm_times' in class_dict:
            res = class_dict['opm_times'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_opm_time(obj)
        elif hasattr(old_obj, 'db_opm_times') and old_obj.db_opm_times is not None:
            for obj in old_obj.db_opm_times:
                new_obj.db_add_opm_time(DBOpmTime.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_opm_times') and hasattr(new_obj, 'db_deleted_opm_times'):
            for obj in old_obj.db_deleted_opm_times:
                n_obj = DBOpmTime.update_version(obj, trans_dict)
                new_obj.db_deleted_opm_times.append(n_obj)
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False):
        children = []
        if self._db_effect is not None:
            children.extend(self._db_effect.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                self._db_effect = None
        if self._db_role is not None:
            children.extend(self._db_role.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                self._db_role = None
        if self._db_cause is not None:
            children.extend(self._db_cause.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                self._db_cause = None
        to_del = []
        for child in self.db_accounts:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_account(child)
        to_del = []
        for child in self.db_opm_times:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_opm_time(child)
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_effect)
        children.extend(self.db_deleted_role)
        children.extend(self.db_deleted_cause)
        children.extend(self.db_deleted_accounts)
        children.extend(self.db_deleted_opm_times)
        if remove:
            self.db_deleted_effect = []
            self.db_deleted_role = []
            self.db_deleted_cause = []
            self.db_deleted_accounts = []
            self.db_deleted_opm_times = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        if self._db_effect is not None and self._db_effect.has_changes():
            return True
        if self._db_role is not None and self._db_role.has_changes():
            return True
        if self._db_cause is not None and self._db_cause.has_changes():
            return True
        for child in self._db_accounts:
            if child.has_changes():
                return True
        for child in self._db_opm_times:
            if child.has_changes():
                return True
        return False
    def __get_db_effect(self):
        return self._db_effect
    def __set_db_effect(self, effect):
        self._db_effect = effect
        self.is_dirty = True
    db_effect = property(__get_db_effect, __set_db_effect)
    def db_add_effect(self, effect):
        self._db_effect = effect
    def db_change_effect(self, effect):
        self._db_effect = effect
    def db_delete_effect(self, effect):
        if not self.is_new:
            self.db_deleted_effect.append(self._db_effect)
        self._db_effect = None
    
    def __get_db_role(self):
        return self._db_role
    def __set_db_role(self, role):
        self._db_role = role
        self.is_dirty = True
    db_role = property(__get_db_role, __set_db_role)
    def db_add_role(self, role):
        self._db_role = role
    def db_change_role(self, role):
        self._db_role = role
    def db_delete_role(self, role):
        if not self.is_new:
            self.db_deleted_role.append(self._db_role)
        self._db_role = None
    
    def __get_db_cause(self):
        return self._db_cause
    def __set_db_cause(self, cause):
        self._db_cause = cause
        self.is_dirty = True
    db_cause = property(__get_db_cause, __set_db_cause)
    def db_add_cause(self, cause):
        self._db_cause = cause
    def db_change_cause(self, cause):
        self._db_cause = cause
    def db_delete_cause(self, cause):
        if not self.is_new:
            self.db_deleted_cause.append(self._db_cause)
        self._db_cause = None
    
    def __get_db_accounts(self):
        return self._db_accounts
    def __set_db_accounts(self, accounts):
        self._db_accounts = accounts
        self.is_dirty = True
    db_accounts = property(__get_db_accounts, __set_db_accounts)
    def db_get_accounts(self):
        return self._db_accounts
    def db_add_account(self, account):
        self.is_dirty = True
        self._db_accounts.append(account)
    def db_change_account(self, account):
        self.is_dirty = True
        self._db_accounts.append(account)
    def db_delete_account(self, account):
        self.is_dirty = True
        raise Exception('Cannot delete a non-keyed object')
    def db_get_account(self, key):
        return None
    
    def __get_db_opm_times(self):
        return self._db_opm_times
    def __set_db_opm_times(self, opm_times):
        self._db_opm_times = opm_times
        self.is_dirty = True
    db_opm_times = property(__get_db_opm_times, __set_db_opm_times)
    def db_get_opm_times(self):
        return self._db_opm_times
    def db_add_opm_time(self, opm_time):
        self.is_dirty = True
        self._db_opm_times.append(opm_time)
    def db_change_opm_time(self, opm_time):
        self.is_dirty = True
        self._db_opm_times.append(opm_time)
    def db_delete_opm_time(self, opm_time):
        self.is_dirty = True
        raise Exception('Cannot delete a non-keyed object')
    def db_get_opm_time(self, key):
        return None
    
class DBOpmAccountId(object):

    vtType = 'opm_account_id'

    def __init__(self, id=None):
        self._db_id = id
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBOpmAccountId.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBOpmAccountId(id=self._db_id)
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
            if hasattr(self, 'db_id') and ('opm_account', self._db_id) in id_remap:
                cp._db_id = id_remap[('opm_account', self._db_id)]
        
        # recreate indices and set flags
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBOpmAccountId()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False):
        return [(self, parent[0], parent[1])]
    def db_deleted_children(self, remove=False):
        children = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        return False
    def __get_db_id(self):
        return self._db_id
    def __set_db_id(self, id):
        self._db_id = id
        self.is_dirty = True
    db_id = property(__get_db_id, __set_db_id)
    def db_add_id(self, id):
        self._db_id = id
    def db_change_id(self, id):
        self._db_id = id
    def db_delete_id(self, id):
        self._db_id = None
        
class DBOpmWasGeneratedBy(object):

    vtType = 'opm_was_generated_by'

    def __init__(self, effect=None, role=None, cause=None, accounts=None, opm_times=None):
        self.db_deleted_effect = []
        self._db_effect = effect
        self.db_deleted_role = []
        self._db_role = role
        self.db_deleted_cause = []
        self._db_cause = cause
        self.db_deleted_accounts = []
        if accounts is None:
            self._db_accounts = []
        else:
            self._db_accounts = accounts
        self.db_deleted_opm_times = []
        if opm_times is None:
            self._db_opm_times = []
        else:
            self._db_opm_times = opm_times
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBOpmWasGeneratedBy.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBOpmWasGeneratedBy()
        if self._db_effect is not None:
            cp._db_effect = self._db_effect.do_copy(new_ids, id_scope, id_remap)
        if self._db_role is not None:
            cp._db_role = self._db_role.do_copy(new_ids, id_scope, id_remap)
        if self._db_cause is not None:
            cp._db_cause = self._db_cause.do_copy(new_ids, id_scope, id_remap)
        if self._db_accounts is None:
            cp._db_accounts = []
        else:
            cp._db_accounts = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_accounts]
        if self._db_opm_times is None:
            cp._db_opm_times = []
        else:
            cp._db_opm_times = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_opm_times]
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
        
        # recreate indices and set flags
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBOpmWasGeneratedBy()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'effect' in class_dict:
            res = class_dict['effect'](old_obj, trans_dict)
            new_obj.db_effect = res
        elif hasattr(old_obj, 'db_effect') and old_obj.db_effect is not None:
            obj = old_obj.db_effect
            new_obj.db_add_effect(DBOpmArtifactIdEffect.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_effect') and hasattr(new_obj, 'db_deleted_effect'):
            for obj in old_obj.db_deleted_effect:
                n_obj = DBOpmArtifactIdEffect.update_version(obj, trans_dict)
                new_obj.db_deleted_effect.append(n_obj)
        if 'role' in class_dict:
            res = class_dict['role'](old_obj, trans_dict)
            new_obj.db_role = res
        elif hasattr(old_obj, 'db_role') and old_obj.db_role is not None:
            obj = old_obj.db_role
            new_obj.db_add_role(DBOpmRole.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_role') and hasattr(new_obj, 'db_deleted_role'):
            for obj in old_obj.db_deleted_role:
                n_obj = DBOpmRole.update_version(obj, trans_dict)
                new_obj.db_deleted_role.append(n_obj)
        if 'cause' in class_dict:
            res = class_dict['cause'](old_obj, trans_dict)
            new_obj.db_cause = res
        elif hasattr(old_obj, 'db_cause') and old_obj.db_cause is not None:
            obj = old_obj.db_cause
            new_obj.db_add_cause(DBOpmProcessIdCause.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_cause') and hasattr(new_obj, 'db_deleted_cause'):
            for obj in old_obj.db_deleted_cause:
                n_obj = DBOpmProcessIdCause.update_version(obj, trans_dict)
                new_obj.db_deleted_cause.append(n_obj)
        if 'accounts' in class_dict:
            res = class_dict['accounts'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_account(obj)
        elif hasattr(old_obj, 'db_accounts') and old_obj.db_accounts is not None:
            for obj in old_obj.db_accounts:
                new_obj.db_add_account(DBOpmAccountId.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_accounts') and hasattr(new_obj, 'db_deleted_accounts'):
            for obj in old_obj.db_deleted_accounts:
                n_obj = DBOpmAccountId.update_version(obj, trans_dict)
                new_obj.db_deleted_accounts.append(n_obj)
        if 'opm_times' in class_dict:
            res = class_dict['opm_times'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_opm_time(obj)
        elif hasattr(old_obj, 'db_opm_times') and old_obj.db_opm_times is not None:
            for obj in old_obj.db_opm_times:
                new_obj.db_add_opm_time(DBOpmTime.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_opm_times') and hasattr(new_obj, 'db_deleted_opm_times'):
            for obj in old_obj.db_deleted_opm_times:
                n_obj = DBOpmTime.update_version(obj, trans_dict)
                new_obj.db_deleted_opm_times.append(n_obj)
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False):
        children = []
        if self._db_effect is not None:
            children.extend(self._db_effect.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                self._db_effect = None
        if self._db_role is not None:
            children.extend(self._db_role.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                self._db_role = None
        if self._db_cause is not None:
            children.extend(self._db_cause.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                self._db_cause = None
        to_del = []
        for child in self.db_accounts:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_account(child)
        to_del = []
        for child in self.db_opm_times:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_opm_time(child)
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_effect)
        children.extend(self.db_deleted_role)
        children.extend(self.db_deleted_cause)
        children.extend(self.db_deleted_accounts)
        children.extend(self.db_deleted_opm_times)
        if remove:
            self.db_deleted_effect = []
            self.db_deleted_role = []
            self.db_deleted_cause = []
            self.db_deleted_accounts = []
            self.db_deleted_opm_times = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        if self._db_effect is not None and self._db_effect.has_changes():
            return True
        if self._db_role is not None and self._db_role.has_changes():
            return True
        if self._db_cause is not None and self._db_cause.has_changes():
            return True
        for child in self._db_accounts:
            if child.has_changes():
                return True
        for child in self._db_opm_times:
            if child.has_changes():
                return True
        return False
    def __get_db_effect(self):
        return self._db_effect
    def __set_db_effect(self, effect):
        self._db_effect = effect
        self.is_dirty = True
    db_effect = property(__get_db_effect, __set_db_effect)
    def db_add_effect(self, effect):
        self._db_effect = effect
    def db_change_effect(self, effect):
        self._db_effect = effect
    def db_delete_effect(self, effect):
        if not self.is_new:
            self.db_deleted_effect.append(self._db_effect)
        self._db_effect = None
    
    def __get_db_role(self):
        return self._db_role
    def __set_db_role(self, role):
        self._db_role = role
        self.is_dirty = True
    db_role = property(__get_db_role, __set_db_role)
    def db_add_role(self, role):
        self._db_role = role
    def db_change_role(self, role):
        self._db_role = role
    def db_delete_role(self, role):
        if not self.is_new:
            self.db_deleted_role.append(self._db_role)
        self._db_role = None
    
    def __get_db_cause(self):
        return self._db_cause
    def __set_db_cause(self, cause):
        self._db_cause = cause
        self.is_dirty = True
    db_cause = property(__get_db_cause, __set_db_cause)
    def db_add_cause(self, cause):
        self._db_cause = cause
    def db_change_cause(self, cause):
        self._db_cause = cause
    def db_delete_cause(self, cause):
        if not self.is_new:
            self.db_deleted_cause.append(self._db_cause)
        self._db_cause = None
    
    def __get_db_accounts(self):
        return self._db_accounts
    def __set_db_accounts(self, accounts):
        self._db_accounts = accounts
        self.is_dirty = True
    db_accounts = property(__get_db_accounts, __set_db_accounts)
    def db_get_accounts(self):
        return self._db_accounts
    def db_add_account(self, account):
        self.is_dirty = True
        self._db_accounts.append(account)
    def db_change_account(self, account):
        self.is_dirty = True
        self._db_accounts.append(account)
    def db_delete_account(self, account):
        self.is_dirty = True
        raise Exception('Cannot delete a non-keyed object')
    def db_get_account(self, key):
        return None
    
    def __get_db_opm_times(self):
        return self._db_opm_times
    def __set_db_opm_times(self, opm_times):
        self._db_opm_times = opm_times
        self.is_dirty = True
    db_opm_times = property(__get_db_opm_times, __set_db_opm_times)
    def db_get_opm_times(self):
        return self._db_opm_times
    def db_add_opm_time(self, opm_time):
        self.is_dirty = True
        self._db_opm_times.append(opm_time)
    def db_change_opm_time(self, opm_time):
        self.is_dirty = True
        self._db_opm_times.append(opm_time)
    def db_delete_opm_time(self, opm_time):
        self.is_dirty = True
        raise Exception('Cannot delete a non-keyed object')
    def db_get_opm_time(self, key):
        return None
    
class DBOpmWasDerivedFrom(object):

    vtType = 'opm_was_derived_from'

    def __init__(self, effect=None, role=None, cause=None, accounts=None, opm_times=None):
        self.db_deleted_effect = []
        self._db_effect = effect
        self.db_deleted_role = []
        self._db_role = role
        self.db_deleted_cause = []
        self._db_cause = cause
        self.db_deleted_accounts = []
        if accounts is None:
            self._db_accounts = []
        else:
            self._db_accounts = accounts
        self.db_deleted_opm_times = []
        if opm_times is None:
            self._db_opm_times = []
        else:
            self._db_opm_times = opm_times
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBOpmWasDerivedFrom.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBOpmWasDerivedFrom()
        if self._db_effect is not None:
            cp._db_effect = self._db_effect.do_copy(new_ids, id_scope, id_remap)
        if self._db_role is not None:
            cp._db_role = self._db_role.do_copy(new_ids, id_scope, id_remap)
        if self._db_cause is not None:
            cp._db_cause = self._db_cause.do_copy(new_ids, id_scope, id_remap)
        if self._db_accounts is None:
            cp._db_accounts = []
        else:
            cp._db_accounts = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_accounts]
        if self._db_opm_times is None:
            cp._db_opm_times = []
        else:
            cp._db_opm_times = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_opm_times]
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
        
        # recreate indices and set flags
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBOpmWasDerivedFrom()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'effect' in class_dict:
            res = class_dict['effect'](old_obj, trans_dict)
            new_obj.db_effect = res
        elif hasattr(old_obj, 'db_effect') and old_obj.db_effect is not None:
            obj = old_obj.db_effect
            new_obj.db_add_effect(DBOpmArtifactIdEffect.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_effect') and hasattr(new_obj, 'db_deleted_effect'):
            for obj in old_obj.db_deleted_effect:
                n_obj = DBOpmArtifactIdEffect.update_version(obj, trans_dict)
                new_obj.db_deleted_effect.append(n_obj)
        if 'role' in class_dict:
            res = class_dict['role'](old_obj, trans_dict)
            new_obj.db_role = res
        elif hasattr(old_obj, 'db_role') and old_obj.db_role is not None:
            obj = old_obj.db_role
            new_obj.db_add_role(DBOpmRole.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_role') and hasattr(new_obj, 'db_deleted_role'):
            for obj in old_obj.db_deleted_role:
                n_obj = DBOpmRole.update_version(obj, trans_dict)
                new_obj.db_deleted_role.append(n_obj)
        if 'cause' in class_dict:
            res = class_dict['cause'](old_obj, trans_dict)
            new_obj.db_cause = res
        elif hasattr(old_obj, 'db_cause') and old_obj.db_cause is not None:
            obj = old_obj.db_cause
            new_obj.db_add_cause(DBOpmArtifactIdCause.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_cause') and hasattr(new_obj, 'db_deleted_cause'):
            for obj in old_obj.db_deleted_cause:
                n_obj = DBOpmArtifactIdCause.update_version(obj, trans_dict)
                new_obj.db_deleted_cause.append(n_obj)
        if 'accounts' in class_dict:
            res = class_dict['accounts'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_account(obj)
        elif hasattr(old_obj, 'db_accounts') and old_obj.db_accounts is not None:
            for obj in old_obj.db_accounts:
                new_obj.db_add_account(DBOpmAccountId.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_accounts') and hasattr(new_obj, 'db_deleted_accounts'):
            for obj in old_obj.db_deleted_accounts:
                n_obj = DBOpmAccountId.update_version(obj, trans_dict)
                new_obj.db_deleted_accounts.append(n_obj)
        if 'opm_times' in class_dict:
            res = class_dict['opm_times'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_opm_time(obj)
        elif hasattr(old_obj, 'db_opm_times') and old_obj.db_opm_times is not None:
            for obj in old_obj.db_opm_times:
                new_obj.db_add_opm_time(DBOpmTime.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_opm_times') and hasattr(new_obj, 'db_deleted_opm_times'):
            for obj in old_obj.db_deleted_opm_times:
                n_obj = DBOpmTime.update_version(obj, trans_dict)
                new_obj.db_deleted_opm_times.append(n_obj)
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False):
        children = []
        if self._db_effect is not None:
            children.extend(self._db_effect.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                self._db_effect = None
        if self._db_role is not None:
            children.extend(self._db_role.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                self._db_role = None
        if self._db_cause is not None:
            children.extend(self._db_cause.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                self._db_cause = None
        to_del = []
        for child in self.db_accounts:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_account(child)
        to_del = []
        for child in self.db_opm_times:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_opm_time(child)
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_effect)
        children.extend(self.db_deleted_role)
        children.extend(self.db_deleted_cause)
        children.extend(self.db_deleted_accounts)
        children.extend(self.db_deleted_opm_times)
        if remove:
            self.db_deleted_effect = []
            self.db_deleted_role = []
            self.db_deleted_cause = []
            self.db_deleted_accounts = []
            self.db_deleted_opm_times = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        if self._db_effect is not None and self._db_effect.has_changes():
            return True
        if self._db_role is not None and self._db_role.has_changes():
            return True
        if self._db_cause is not None and self._db_cause.has_changes():
            return True
        for child in self._db_accounts:
            if child.has_changes():
                return True
        for child in self._db_opm_times:
            if child.has_changes():
                return True
        return False
    def __get_db_effect(self):
        return self._db_effect
    def __set_db_effect(self, effect):
        self._db_effect = effect
        self.is_dirty = True
    db_effect = property(__get_db_effect, __set_db_effect)
    def db_add_effect(self, effect):
        self._db_effect = effect
    def db_change_effect(self, effect):
        self._db_effect = effect
    def db_delete_effect(self, effect):
        if not self.is_new:
            self.db_deleted_effect.append(self._db_effect)
        self._db_effect = None
    
    def __get_db_role(self):
        return self._db_role
    def __set_db_role(self, role):
        self._db_role = role
        self.is_dirty = True
    db_role = property(__get_db_role, __set_db_role)
    def db_add_role(self, role):
        self._db_role = role
    def db_change_role(self, role):
        self._db_role = role
    def db_delete_role(self, role):
        if not self.is_new:
            self.db_deleted_role.append(self._db_role)
        self._db_role = None
    
    def __get_db_cause(self):
        return self._db_cause
    def __set_db_cause(self, cause):
        self._db_cause = cause
        self.is_dirty = True
    db_cause = property(__get_db_cause, __set_db_cause)
    def db_add_cause(self, cause):
        self._db_cause = cause
    def db_change_cause(self, cause):
        self._db_cause = cause
    def db_delete_cause(self, cause):
        if not self.is_new:
            self.db_deleted_cause.append(self._db_cause)
        self._db_cause = None
    
    def __get_db_accounts(self):
        return self._db_accounts
    def __set_db_accounts(self, accounts):
        self._db_accounts = accounts
        self.is_dirty = True
    db_accounts = property(__get_db_accounts, __set_db_accounts)
    def db_get_accounts(self):
        return self._db_accounts
    def db_add_account(self, account):
        self.is_dirty = True
        self._db_accounts.append(account)
    def db_change_account(self, account):
        self.is_dirty = True
        self._db_accounts.append(account)
    def db_delete_account(self, account):
        self.is_dirty = True
        raise Exception('Cannot delete a non-keyed object')
    def db_get_account(self, key):
        return None
    
    def __get_db_opm_times(self):
        return self._db_opm_times
    def __set_db_opm_times(self, opm_times):
        self._db_opm_times = opm_times
        self.is_dirty = True
    db_opm_times = property(__get_db_opm_times, __set_db_opm_times)
    def db_get_opm_times(self):
        return self._db_opm_times
    def db_add_opm_time(self, opm_time):
        self.is_dirty = True
        self._db_opm_times.append(opm_time)
    def db_change_opm_time(self, opm_time):
        self.is_dirty = True
        self._db_opm_times.append(opm_time)
    def db_delete_opm_time(self, opm_time):
        self.is_dirty = True
        raise Exception('Cannot delete a non-keyed object')
    def db_get_opm_time(self, key):
        return None

class DBOpmWasControlledBy(object):

    vtType = 'opm_was_controlled_by'

    def __init__(self, effect=None, role=None, cause=None, accounts=None, starts=None, ends=None):
        self.db_deleted_effect = []
        self._db_effect = effect
        self.db_deleted_role = []
        self._db_role = role
        self.db_deleted_cause = []
        self._db_cause = cause
        self.db_deleted_accounts = []
        if accounts is None:
            self._db_accounts = []
        else:
            self._db_accounts = accounts
        self.db_deleted_starts = []
        if starts is None:
            self._db_starts = []
        else:
            self._db_starts = starts
        self.db_deleted_ends = []
        if ends is None:
            self._db_ends = []
        else:
            self._db_ends = ends
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBOpmWasControlledBy.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBOpmWasControlledBy()
        if self._db_effect is not None:
            cp._db_effect = self._db_effect.do_copy(new_ids, id_scope, id_remap)
        if self._db_role is not None:
            cp._db_role = self._db_role.do_copy(new_ids, id_scope, id_remap)
        if self._db_cause is not None:
            cp._db_cause = self._db_cause.do_copy(new_ids, id_scope, id_remap)
        if self._db_accounts is None:
            cp._db_accounts = []
        else:
            cp._db_accounts = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_accounts]
        if self._db_starts is None:
            cp._db_starts = []
        else:
            cp._db_starts = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_starts]
        if self._db_ends is None:
            cp._db_ends = []
        else:
            cp._db_ends = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_ends]
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
        
        # recreate indices and set flags
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBOpmWasControlledBy()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'effect' in class_dict:
            res = class_dict['effect'](old_obj, trans_dict)
            new_obj.db_effect = res
        elif hasattr(old_obj, 'db_effect') and old_obj.db_effect is not None:
            obj = old_obj.db_effect
            new_obj.db_add_effect(DBOpmProcessIdEffect.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_effect') and hasattr(new_obj, 'db_deleted_effect'):
            for obj in old_obj.db_deleted_effect:
                n_obj = DBOpmProcessIdEffect.update_version(obj, trans_dict)
                new_obj.db_deleted_effect.append(n_obj)
        if 'role' in class_dict:
            res = class_dict['role'](old_obj, trans_dict)
            new_obj.db_role = res
        elif hasattr(old_obj, 'db_role') and old_obj.db_role is not None:
            obj = old_obj.db_role
            new_obj.db_add_role(DBOpmRole.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_role') and hasattr(new_obj, 'db_deleted_role'):
            for obj in old_obj.db_deleted_role:
                n_obj = DBOpmRole.update_version(obj, trans_dict)
                new_obj.db_deleted_role.append(n_obj)
        if 'cause' in class_dict:
            res = class_dict['cause'](old_obj, trans_dict)
            new_obj.db_cause = res
        elif hasattr(old_obj, 'db_cause') and old_obj.db_cause is not None:
            obj = old_obj.db_cause
            new_obj.db_add_cause(DBOpmAgentId.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_cause') and hasattr(new_obj, 'db_deleted_cause'):
            for obj in old_obj.db_deleted_cause:
                n_obj = DBOpmAgentId.update_version(obj, trans_dict)
                new_obj.db_deleted_cause.append(n_obj)
        if 'accounts' in class_dict:
            res = class_dict['accounts'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_account(obj)
        elif hasattr(old_obj, 'db_accounts') and old_obj.db_accounts is not None:
            for obj in old_obj.db_accounts:
                new_obj.db_add_account(DBOpmAccountId.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_accounts') and hasattr(new_obj, 'db_deleted_accounts'):
            for obj in old_obj.db_deleted_accounts:
                n_obj = DBOpmAccountId.update_version(obj, trans_dict)
                new_obj.db_deleted_accounts.append(n_obj)
        if 'starts' in class_dict:
            res = class_dict['starts'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_start(obj)
        elif hasattr(old_obj, 'db_starts') and old_obj.db_starts is not None:
            for obj in old_obj.db_starts:
                new_obj.db_add_start(DBOpmTime.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_starts') and hasattr(new_obj, 'db_deleted_starts'):
            for obj in old_obj.db_deleted_starts:
                n_obj = DBOpmTime.update_version(obj, trans_dict)
                new_obj.db_deleted_starts.append(n_obj)
        if 'ends' in class_dict:
            res = class_dict['ends'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_end(obj)
        elif hasattr(old_obj, 'db_ends') and old_obj.db_ends is not None:
            for obj in old_obj.db_ends:
                new_obj.db_add_end(DBOpmTime.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_ends') and hasattr(new_obj, 'db_deleted_ends'):
            for obj in old_obj.db_deleted_ends:
                n_obj = DBOpmTime.update_version(obj, trans_dict)
                new_obj.db_deleted_ends.append(n_obj)
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False):
        children = []
        if self._db_effect is not None:
            children.extend(self._db_effect.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                self._db_effect = None
        if self._db_role is not None:
            children.extend(self._db_role.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                self._db_role = None
        if self._db_cause is not None:
            children.extend(self._db_cause.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                self._db_cause = None
        to_del = []
        for child in self.db_accounts:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_account(child)
        to_del = []
        for child in self.db_starts:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_start(child)
        to_del = []
        for child in self.db_ends:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_end(child)
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_effect)
        children.extend(self.db_deleted_role)
        children.extend(self.db_deleted_cause)
        children.extend(self.db_deleted_accounts)
        children.extend(self.db_deleted_starts)
        children.extend(self.db_deleted_ends)
        if remove:
            self.db_deleted_effect = []
            self.db_deleted_role = []
            self.db_deleted_cause = []
            self.db_deleted_accounts = []
            self.db_deleted_starts = []
            self.db_deleted_ends = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        if self._db_effect is not None and self._db_effect.has_changes():
            return True
        if self._db_role is not None and self._db_role.has_changes():
            return True
        if self._db_cause is not None and self._db_cause.has_changes():
            return True
        for child in self._db_accounts:
            if child.has_changes():
                return True
        for child in self._db_starts:
            if child.has_changes():
                return True
        for child in self._db_ends:
            if child.has_changes():
                return True
        return False
    def __get_db_effect(self):
        return self._db_effect
    def __set_db_effect(self, effect):
        self._db_effect = effect
        self.is_dirty = True
    db_effect = property(__get_db_effect, __set_db_effect)
    def db_add_effect(self, effect):
        self._db_effect = effect
    def db_change_effect(self, effect):
        self._db_effect = effect
    def db_delete_effect(self, effect):
        if not self.is_new:
            self.db_deleted_effect.append(self._db_effect)
        self._db_effect = None
    
    def __get_db_role(self):
        return self._db_role
    def __set_db_role(self, role):
        self._db_role = role
        self.is_dirty = True
    db_role = property(__get_db_role, __set_db_role)
    def db_add_role(self, role):
        self._db_role = role
    def db_change_role(self, role):
        self._db_role = role
    def db_delete_role(self, role):
        if not self.is_new:
            self.db_deleted_role.append(self._db_role)
        self._db_role = None
    
    def __get_db_cause(self):
        return self._db_cause
    def __set_db_cause(self, cause):
        self._db_cause = cause
        self.is_dirty = True
    db_cause = property(__get_db_cause, __set_db_cause)
    def db_add_cause(self, cause):
        self._db_cause = cause
    def db_change_cause(self, cause):
        self._db_cause = cause
    def db_delete_cause(self, cause):
        if not self.is_new:
            self.db_deleted_cause.append(self._db_cause)
        self._db_cause = None
    
    def __get_db_accounts(self):
        return self._db_accounts
    def __set_db_accounts(self, accounts):
        self._db_accounts = accounts
        self.is_dirty = True
    db_accounts = property(__get_db_accounts, __set_db_accounts)
    def db_get_accounts(self):
        return self._db_accounts
    def db_add_account(self, account):
        self.is_dirty = True
        self._db_accounts.append(account)
    def db_change_account(self, account):
        self.is_dirty = True
        self._db_accounts.append(account)
    def db_delete_account(self, account):
        self.is_dirty = True
        raise Exception('Cannot delete a non-keyed object')
    def db_get_account(self, key):
        return None
    
    def __get_db_starts(self):
        return self._db_starts
    def __set_db_starts(self, starts):
        self._db_starts = starts
        self.is_dirty = True
    db_starts = property(__get_db_starts, __set_db_starts)
    def db_get_starts(self):
        return self._db_starts
    def db_add_start(self, start):
        self.is_dirty = True
        self._db_starts.append(start)
    def db_change_start(self, start):
        self.is_dirty = True
        self._db_starts.append(start)
    def db_delete_start(self, start):
        self.is_dirty = True
        raise Exception('Cannot delete a non-keyed object')
    def db_get_start(self, key):
        return None
    
    def __get_db_ends(self):
        return self._db_ends
    def __set_db_ends(self, ends):
        self._db_ends = ends
        self.is_dirty = True
    db_ends = property(__get_db_ends, __set_db_ends)
    def db_get_ends(self):
        return self._db_ends
    def db_add_end(self, end):
        self.is_dirty = True
        self._db_ends.append(end)
    def db_change_end(self, end):
        self.is_dirty = True
        self._db_ends.append(end)
    def db_delete_end(self, end):
        self.is_dirty = True
        raise Exception('Cannot delete a non-keyed object')
    def db_get_end(self, key):
        return None

class DBOpmWasTriggeredBy(object):

    vtType = 'opm_was_triggered_by'

    def __init__(self, effect=None, role=None, cause=None, accounts=None, opm_times=None):
        self.db_deleted_effect = []
        self._db_effect = effect
        self.db_deleted_role = []
        self._db_role = role
        self.db_deleted_cause = []
        self._db_cause = cause
        self.db_deleted_accounts = []
        if accounts is None:
            self._db_accounts = []
        else:
            self._db_accounts = accounts
        self.db_deleted_opm_times = []
        if opm_times is None:
            self._db_opm_times = []
        else:
            self._db_opm_times = opm_times
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBOpmWasTriggeredBy.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBOpmWasTriggeredBy()
        if self._db_effect is not None:
            cp._db_effect = self._db_effect.do_copy(new_ids, id_scope, id_remap)
        if self._db_role is not None:
            cp._db_role = self._db_role.do_copy(new_ids, id_scope, id_remap)
        if self._db_cause is not None:
            cp._db_cause = self._db_cause.do_copy(new_ids, id_scope, id_remap)
        if self._db_accounts is None:
            cp._db_accounts = []
        else:
            cp._db_accounts = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_accounts]
        if self._db_opm_times is None:
            cp._db_opm_times = []
        else:
            cp._db_opm_times = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_opm_times]
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
        
        # recreate indices and set flags
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBOpmWasTriggeredBy()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'effect' in class_dict:
            res = class_dict['effect'](old_obj, trans_dict)
            new_obj.db_effect = res
        elif hasattr(old_obj, 'db_effect') and old_obj.db_effect is not None:
            obj = old_obj.db_effect
            new_obj.db_add_effect(DBOpmProcessIdEffect.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_effect') and hasattr(new_obj, 'db_deleted_effect'):
            for obj in old_obj.db_deleted_effect:
                n_obj = DBOpmProcessIdEffect.update_version(obj, trans_dict)
                new_obj.db_deleted_effect.append(n_obj)
        if 'role' in class_dict:
            res = class_dict['role'](old_obj, trans_dict)
            new_obj.db_role = res
        elif hasattr(old_obj, 'db_role') and old_obj.db_role is not None:
            obj = old_obj.db_role
            new_obj.db_add_role(DBOpmRole.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_role') and hasattr(new_obj, 'db_deleted_role'):
            for obj in old_obj.db_deleted_role:
                n_obj = DBOpmRole.update_version(obj, trans_dict)
                new_obj.db_deleted_role.append(n_obj)
        if 'cause' in class_dict:
            res = class_dict['cause'](old_obj, trans_dict)
            new_obj.db_cause = res
        elif hasattr(old_obj, 'db_cause') and old_obj.db_cause is not None:
            obj = old_obj.db_cause
            new_obj.db_add_cause(DBOpmProcessIdCause.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_cause') and hasattr(new_obj, 'db_deleted_cause'):
            for obj in old_obj.db_deleted_cause:
                n_obj = DBOpmProcessIdCause.update_version(obj, trans_dict)
                new_obj.db_deleted_cause.append(n_obj)
        if 'accounts' in class_dict:
            res = class_dict['accounts'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_account(obj)
        elif hasattr(old_obj, 'db_accounts') and old_obj.db_accounts is not None:
            for obj in old_obj.db_accounts:
                new_obj.db_add_account(DBOpmAccountId.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_accounts') and hasattr(new_obj, 'db_deleted_accounts'):
            for obj in old_obj.db_deleted_accounts:
                n_obj = DBOpmAccountId.update_version(obj, trans_dict)
                new_obj.db_deleted_accounts.append(n_obj)
        if 'opm_times' in class_dict:
            res = class_dict['opm_times'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_opm_time(obj)
        elif hasattr(old_obj, 'db_opm_times') and old_obj.db_opm_times is not None:
            for obj in old_obj.db_opm_times:
                new_obj.db_add_opm_time(DBOpmTime.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_opm_times') and hasattr(new_obj, 'db_deleted_opm_times'):
            for obj in old_obj.db_deleted_opm_times:
                n_obj = DBOpmTime.update_version(obj, trans_dict)
                new_obj.db_deleted_opm_times.append(n_obj)
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False):
        children = []
        if self._db_effect is not None:
            children.extend(self._db_effect.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                self._db_effect = None
        if self._db_role is not None:
            children.extend(self._db_role.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                self._db_role = None
        if self._db_cause is not None:
            children.extend(self._db_cause.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                self._db_cause = None
        to_del = []
        for child in self.db_accounts:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_account(child)
        to_del = []
        for child in self.db_opm_times:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_opm_time(child)
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_effect)
        children.extend(self.db_deleted_role)
        children.extend(self.db_deleted_cause)
        children.extend(self.db_deleted_accounts)
        children.extend(self.db_deleted_opm_times)
        if remove:
            self.db_deleted_effect = []
            self.db_deleted_role = []
            self.db_deleted_cause = []
            self.db_deleted_accounts = []
            self.db_deleted_opm_times = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        if self._db_effect is not None and self._db_effect.has_changes():
            return True
        if self._db_role is not None and self._db_role.has_changes():
            return True
        if self._db_cause is not None and self._db_cause.has_changes():
            return True
        for child in self._db_accounts:
            if child.has_changes():
                return True
        for child in self._db_opm_times:
            if child.has_changes():
                return True
        return False
    def __get_db_effect(self):
        return self._db_effect
    def __set_db_effect(self, effect):
        self._db_effect = effect
        self.is_dirty = True
    db_effect = property(__get_db_effect, __set_db_effect)
    def db_add_effect(self, effect):
        self._db_effect = effect
    def db_change_effect(self, effect):
        self._db_effect = effect
    def db_delete_effect(self, effect):
        if not self.is_new:
            self.db_deleted_effect.append(self._db_effect)
        self._db_effect = None
    
    def __get_db_role(self):
        return self._db_role
    def __set_db_role(self, role):
        self._db_role = role
        self.is_dirty = True
    db_role = property(__get_db_role, __set_db_role)
    def db_add_role(self, role):
        self._db_role = role
    def db_change_role(self, role):
        self._db_role = role
    def db_delete_role(self, role):
        if not self.is_new:
            self.db_deleted_role.append(self._db_role)
        self._db_role = None
    
    def __get_db_cause(self):
        return self._db_cause
    def __set_db_cause(self, cause):
        self._db_cause = cause
        self.is_dirty = True
    db_cause = property(__get_db_cause, __set_db_cause)
    def db_add_cause(self, cause):
        self._db_cause = cause
    def db_change_cause(self, cause):
        self._db_cause = cause
    def db_delete_cause(self, cause):
        if not self.is_new:
            self.db_deleted_cause.append(self._db_cause)
        self._db_cause = None
    
    def __get_db_accounts(self):
        return self._db_accounts
    def __set_db_accounts(self, accounts):
        self._db_accounts = accounts
        self.is_dirty = True
    db_accounts = property(__get_db_accounts, __set_db_accounts)
    def db_get_accounts(self):
        return self._db_accounts
    def db_add_account(self, account):
        self.is_dirty = True
        self._db_accounts.append(account)
    def db_change_account(self, account):
        self.is_dirty = True
        self._db_accounts.append(account)
    def db_delete_account(self, account):
        self.is_dirty = True
        raise Exception('Cannot delete a non-keyed object')
    def db_get_account(self, key):
        return None
    
    def __get_db_opm_times(self):
        return self._db_opm_times
    def __set_db_opm_times(self, opm_times):
        self._db_opm_times = opm_times
        self.is_dirty = True
    db_opm_times = property(__get_db_opm_times, __set_db_opm_times)
    def db_get_opm_times(self):
        return self._db_opm_times
    def db_add_opm_time(self, opm_time):
        self.is_dirty = True
        self._db_opm_times.append(opm_time)
    def db_change_opm_time(self, opm_time):
        self.is_dirty = True
        self._db_opm_times.append(opm_time)
    def db_delete_opm_time(self, opm_time):
        self.is_dirty = True
        raise Exception('Cannot delete a non-keyed object')
    def db_get_opm_time(self, key):
        return None
    
class DBOpmAgent(object):

    vtType = 'opm_agent'

    def __init__(self, id=None, value=None, accounts=None):
        self._db_id = id
        self._db_value = value
        self.db_deleted_accounts = []
        if accounts is None:
            self._db_accounts = []
        else:
            self._db_accounts = accounts
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBOpmAgent.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBOpmAgent(id=self._db_id,
                        value=self._db_value)
        if self._db_accounts is None:
            cp._db_accounts = []
        else:
            cp._db_accounts = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_accounts]
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
        
        # recreate indices and set flags
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBOpmAgent()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'value' in class_dict:
            res = class_dict['value'](old_obj, trans_dict)
            new_obj.db_value = res
        elif hasattr(old_obj, 'db_value') and old_obj.db_value is not None:
            new_obj.db_value = old_obj.db_value
        if 'accounts' in class_dict:
            res = class_dict['accounts'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_account(obj)
        elif hasattr(old_obj, 'db_accounts') and old_obj.db_accounts is not None:
            for obj in old_obj.db_accounts:
                new_obj.db_add_account(DBOpmAccountId.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_accounts') and hasattr(new_obj, 'db_deleted_accounts'):
            for obj in old_obj.db_deleted_accounts:
                n_obj = DBOpmAccountId.update_version(obj, trans_dict)
                new_obj.db_deleted_accounts.append(n_obj)
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False):
        children = []
        to_del = []
        for child in self.db_accounts:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_account(child)
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_accounts)
        if remove:
            self.db_deleted_accounts = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        for child in self._db_accounts:
            if child.has_changes():
                return True
        return False
    def __get_db_id(self):
        return self._db_id
    def __set_db_id(self, id):
        self._db_id = id
        self.is_dirty = True
    db_id = property(__get_db_id, __set_db_id)
    def db_add_id(self, id):
        self._db_id = id
    def db_change_id(self, id):
        self._db_id = id
    def db_delete_id(self, id):
        self._db_id = None
    
    def __get_db_value(self):
        return self._db_value
    def __set_db_value(self, value):
        self._db_value = value
        self.is_dirty = True
    db_value = property(__get_db_value, __set_db_value)
    def db_add_value(self, value):
        self._db_value = value
    def db_change_value(self, value):
        self._db_value = value
    def db_delete_value(self, value):
        self._db_value = None
    
    def __get_db_accounts(self):
        return self._db_accounts
    def __set_db_accounts(self, accounts):
        self._db_accounts = accounts
        self.is_dirty = True
    db_accounts = property(__get_db_accounts, __set_db_accounts)
    def db_get_accounts(self):
        return self._db_accounts
    def db_add_account(self, account):
        self.is_dirty = True
        self._db_accounts.append(account)
    def db_change_account(self, account):
        self.is_dirty = True
        self._db_accounts.append(account)
    def db_delete_account(self, account):
        self.is_dirty = True
        raise Exception('Cannot delete a non-keyed object')
    def db_get_account(self, key):
        return None
    
    def getPrimaryKey(self):
        return self._db_id
    
class DBOpmProcess(object):

    vtType = 'opm_process'

    def __init__(self, id=None, value=None, accounts=None):
        self._db_id = id
        self.db_deleted_value = []
        self._db_value = value
        self.db_deleted_accounts = []
        if accounts is None:
            self._db_accounts = []
        else:
            self._db_accounts = accounts
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBOpmProcess.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBOpmProcess(id=self._db_id)
        if self._db_value is not None:
            cp._db_value = self._db_value.do_copy(new_ids, id_scope, id_remap)
        if self._db_accounts is None:
            cp._db_accounts = []
        else:
            cp._db_accounts = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_accounts]
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
        
        # recreate indices and set flags
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBOpmProcess()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'value' in class_dict:
            res = class_dict['value'](old_obj, trans_dict)
            new_obj.db_value = res
        elif hasattr(old_obj, 'db_value') and old_obj.db_value is not None:
            obj = old_obj.db_value
            new_obj.db_add_value(DBOpmProcessValue.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_value') and hasattr(new_obj, 'db_deleted_value'):
            for obj in old_obj.db_deleted_value:
                n_obj = DBOpmProcessValue.update_version(obj, trans_dict)
                new_obj.db_deleted_value.append(n_obj)
        if 'accounts' in class_dict:
            res = class_dict['accounts'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_account(obj)
        elif hasattr(old_obj, 'db_accounts') and old_obj.db_accounts is not None:
            for obj in old_obj.db_accounts:
                new_obj.db_add_account(DBOpmAccountId.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_accounts') and hasattr(new_obj, 'db_deleted_accounts'):
            for obj in old_obj.db_deleted_accounts:
                n_obj = DBOpmAccountId.update_version(obj, trans_dict)
                new_obj.db_deleted_accounts.append(n_obj)
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False):
        children = []
        if self._db_value is not None:
            children.extend(self._db_value.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                self._db_value = None
        to_del = []
        for child in self.db_accounts:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_account(child)
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_value)
        children.extend(self.db_deleted_accounts)
        if remove:
            self.db_deleted_value = []
            self.db_deleted_accounts = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        if self._db_value is not None and self._db_value.has_changes():
            return True
        for child in self._db_accounts:
            if child.has_changes():
                return True
        return False
    def __get_db_id(self):
        return self._db_id
    def __set_db_id(self, id):
        self._db_id = id
        self.is_dirty = True
    db_id = property(__get_db_id, __set_db_id)
    def db_add_id(self, id):
        self._db_id = id
    def db_change_id(self, id):
        self._db_id = id
    def db_delete_id(self, id):
        self._db_id = None
    
    def __get_db_value(self):
        return self._db_value
    def __set_db_value(self, value):
        self._db_value = value
        self.is_dirty = True
    db_value = property(__get_db_value, __set_db_value)
    def db_add_value(self, value):
        self._db_value = value
    def db_change_value(self, value):
        self._db_value = value
    def db_delete_value(self, value):
        if not self.is_new:
            self.db_deleted_value.append(self._db_value)
        self._db_value = None
    
    def __get_db_accounts(self):
        return self._db_accounts
    def __set_db_accounts(self, accounts):
        self._db_accounts = accounts
        self.is_dirty = True
    db_accounts = property(__get_db_accounts, __set_db_accounts)
    def db_get_accounts(self):
        return self._db_accounts
    def db_add_account(self, account):
        self.is_dirty = True
        self._db_accounts.append(account)
    def db_change_account(self, account):
        self.is_dirty = True
        self._db_accounts.append(account)
    def db_delete_account(self, account):
        self.is_dirty = True
        raise Exception('Cannot delete a non-keyed object')
    def db_get_account(self, key):
        return None
    
    def getPrimaryKey(self):
        return self._db_id
    
class DBOpmAccount(object):

    vtType = 'opm_account'

    def __init__(self, id=None, value=None):
        self._db_id = id
        self._db_value = value
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBOpmAccount.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBOpmAccount(id=self._db_id,
                          value=self._db_value)
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
        
        # recreate indices and set flags
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBOpmAccount()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'value' in class_dict:
            res = class_dict['value'](old_obj, trans_dict)
            new_obj.db_value = res
        elif hasattr(old_obj, 'db_value') and old_obj.db_value is not None:
            new_obj.db_value = old_obj.db_value
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False):
        return [(self, parent[0], parent[1])]
    def db_deleted_children(self, remove=False):
        children = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        return False
    def __get_db_id(self):
        return self._db_id
    def __set_db_id(self, id):
        self._db_id = id
        self.is_dirty = True
    db_id = property(__get_db_id, __set_db_id)
    def db_add_id(self, id):
        self._db_id = id
    def db_change_id(self, id):
        self._db_id = id
    def db_delete_id(self, id):
        self._db_id = None
    
    def __get_db_value(self):
        return self._db_value
    def __set_db_value(self, value):
        self._db_value = value
        self.is_dirty = True
    db_value = property(__get_db_value, __set_db_value)
    def db_add_value(self, value):
        self._db_value = value
    def db_change_value(self, value):
        self._db_value = value
    def db_delete_value(self, value):
        self._db_value = None
    
    def getPrimaryKey(self):
        return self._db_id
    
class DBOpmOverlaps(object):

    vtType = 'opm_overlaps'

    def __init__(self, opm_account_ids=None):
        self.db_deleted_opm_account_ids = []
        if opm_account_ids is None:
            self._db_opm_account_ids = []
        else:
            self._db_opm_account_ids = opm_account_ids
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBOpmOverlaps.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBOpmOverlaps()
        if self._db_opm_account_ids is None:
            cp._db_opm_account_ids = []
        else:
            cp._db_opm_account_ids = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_opm_account_ids]
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
        
        # recreate indices and set flags
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBOpmOverlaps()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'opm_account_ids' in class_dict:
            res = class_dict['opm_account_ids'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_opm_account_id(obj)
        elif hasattr(old_obj, 'db_opm_account_ids') and old_obj.db_opm_account_ids is not None:
            for obj in old_obj.db_opm_account_ids:
                new_obj.db_add_opm_account_id(DBOpmAccountId.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_opm_account_ids') and hasattr(new_obj, 'db_deleted_opm_account_ids'):
            for obj in old_obj.db_deleted_opm_account_ids:
                n_obj = DBOpmAccountId.update_version(obj, trans_dict)
                new_obj.db_deleted_opm_account_ids.append(n_obj)
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False):
        children = []
        to_del = []
        for child in self.db_opm_account_ids:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_opm_account_id(child)
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_opm_account_ids)
        if remove:
            self.db_deleted_opm_account_ids = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        for child in self._db_opm_account_ids:
            if child.has_changes():
                return True
        return False
    def __get_db_opm_account_ids(self):
        return self._db_opm_account_ids
    def __set_db_opm_account_ids(self, opm_account_ids):
        self._db_opm_account_ids = opm_account_ids
        self.is_dirty = True
    db_opm_account_ids = property(__get_db_opm_account_ids, __set_db_opm_account_ids)
    def db_get_opm_account_ids(self):
        return self._db_opm_account_ids
    def db_add_opm_account_id(self, opm_account_id):
        self.is_dirty = True
        self._db_opm_account_ids.append(opm_account_id)
    def db_change_opm_account_id(self, opm_account_id):
        self.is_dirty = True
        self._db_opm_account_ids.append(opm_account_id)
    def db_delete_opm_account_id(self, opm_account_id):
        self.is_dirty = True
        raise Exception('Cannot delete a non-keyed object')
    def db_get_opm_account_id(self, key):
        return None
    
class DBOpmArtifactValue(object):

    vtType = 'opm_artifact_value'

    def __init__(self, value=None):
        self.db_deleted_value = []
        self._db_value = value
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBOpmArtifactValue.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBOpmArtifactValue()
        if self._db_value is not None:
            cp._db_value = self._db_value.do_copy(new_ids, id_scope, id_remap)
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
        
        # recreate indices and set flags
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBOpmArtifactValue()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'value' in class_dict:
            res = class_dict['value'](old_obj, trans_dict)
            new_obj.db_value = res
        elif hasattr(old_obj, 'db_value') and old_obj.db_value is not None:
            obj = old_obj.db_value
            if obj.vtType == 'portSpec':
                new_obj.db_add_value(DBPortSpec.update_version(obj, trans_dict))
            elif obj.vtType == 'function':
                new_obj.db_add_value(DBFunction.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_value') and hasattr(new_obj, 'db_deleted_value'):
            for obj in old_obj.db_deleted_value:
                if obj.vtType == 'portSpec':
                    n_obj = DBPortSpec.update_version(obj, trans_dict)
                    new_obj.db_deleted_value.append(n_obj)
                elif obj.vtType == 'function':
                    n_obj = DBFunction.update_version(obj, trans_dict)
                    new_obj.db_deleted_value.append(n_obj)
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False):
        children = []
        if self._db_value is not None:
            children.extend(self._db_value.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                self._db_value = None
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_value)
        if remove:
            self.db_deleted_value = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        if self._db_value is not None and self._db_value.has_changes():
            return True
        return False
    def __get_db_value(self):
        return self._db_value
    def __set_db_value(self, value):
        self._db_value = value
        self.is_dirty = True
    db_value = property(__get_db_value, __set_db_value)
    def db_add_value(self, value):
        self._db_value = value
    def db_change_value(self, value):
        self._db_value = value
    def db_delete_value(self, value):
        if not self.is_new:
            self.db_deleted_value.append(self._db_value)
        self._db_value = None

class DBOpmTime(object):

    vtType = 'opm_time'

    def __init__(self, no_later_than=None, no_earlier_than=None, clock_id=None):
        self._db_no_later_than = no_later_than
        self._db_no_earlier_than = no_earlier_than
        self._db_clock_id = clock_id
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBOpmTime.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBOpmTime(no_later_than=self._db_no_later_than,
                       no_earlier_than=self._db_no_earlier_than,
                       clock_id=self._db_clock_id)
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
        
        # recreate indices and set flags
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBOpmTime()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'no_later_than' in class_dict:
            res = class_dict['no_later_than'](old_obj, trans_dict)
            new_obj.db_no_later_than = res
        elif hasattr(old_obj, 'db_no_later_than') and old_obj.db_no_later_than is not None:
            new_obj.db_no_later_than = old_obj.db_no_later_than
        if 'no_earlier_than' in class_dict:
            res = class_dict['no_earlier_than'](old_obj, trans_dict)
            new_obj.db_no_earlier_than = res
        elif hasattr(old_obj, 'db_no_earlier_than') and old_obj.db_no_earlier_than is not None:
            new_obj.db_no_earlier_than = old_obj.db_no_earlier_than
        if 'clock_id' in class_dict:
            res = class_dict['clock_id'](old_obj, trans_dict)
            new_obj.db_clock_id = res
        elif hasattr(old_obj, 'db_clock_id') and old_obj.db_clock_id is not None:
            new_obj.db_clock_id = old_obj.db_clock_id
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False):
        return [(self, parent[0], parent[1])]
    def db_deleted_children(self, remove=False):
        children = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        return False
    def __get_db_no_later_than(self):
        return self._db_no_later_than
    def __set_db_no_later_than(self, no_later_than):
        self._db_no_later_than = no_later_than
        self.is_dirty = True
    db_no_later_than = property(__get_db_no_later_than, __set_db_no_later_than)
    def db_add_no_later_than(self, no_later_than):
        self._db_no_later_than = no_later_than
    def db_change_no_later_than(self, no_later_than):
        self._db_no_later_than = no_later_than
    def db_delete_no_later_than(self, no_later_than):
        self._db_no_later_than = None
    
    def __get_db_no_earlier_than(self):
        return self._db_no_earlier_than
    def __set_db_no_earlier_than(self, no_earlier_than):
        self._db_no_earlier_than = no_earlier_than
        self.is_dirty = True
    db_no_earlier_than = property(__get_db_no_earlier_than, __set_db_no_earlier_than)
    def db_add_no_earlier_than(self, no_earlier_than):
        self._db_no_earlier_than = no_earlier_than
    def db_change_no_earlier_than(self, no_earlier_than):
        self._db_no_earlier_than = no_earlier_than
    def db_delete_no_earlier_than(self, no_earlier_than):
        self._db_no_earlier_than = None
    
    def __get_db_clock_id(self):
        return self._db_clock_id
    def __set_db_clock_id(self, clock_id):
        self._db_clock_id = clock_id
        self.is_dirty = True
    db_clock_id = property(__get_db_clock_id, __set_db_clock_id)
    def db_add_clock_id(self, clock_id):
        self._db_clock_id = clock_id
    def db_change_clock_id(self, clock_id):
        self._db_clock_id = clock_id
    def db_delete_clock_id(self, clock_id):
        self._db_clock_id = None
        
class DBOpmArtifactIdCause(object):

    vtType = 'opm_artifact_id_cause'

    def __init__(self, id=None):
        self._db_id = id
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBOpmArtifactIdCause.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBOpmArtifactIdCause(id=self._db_id)
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
            if hasattr(self, 'db_id') and ('opm_artifact', self._db_id) in id_remap:
                cp._db_id = id_remap[('opm_artifact', self._db_id)]
        
        # recreate indices and set flags
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBOpmArtifactIdCause()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False):
        return [(self, parent[0], parent[1])]
    def db_deleted_children(self, remove=False):
        children = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        return False
    def __get_db_id(self):
        return self._db_id
    def __set_db_id(self, id):
        self._db_id = id
        self.is_dirty = True
    db_id = property(__get_db_id, __set_db_id)
    def db_add_id(self, id):
        self._db_id = id
    def db_change_id(self, id):
        self._db_id = id
    def db_delete_id(self, id):
        self._db_id = None
        
class DBOpmProcessIdEffect(object):

    vtType = 'opm_process_id_effect'

    def __init__(self, id=None):
        self._db_id = id
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBOpmProcessIdEffect.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBOpmProcessIdEffect(id=self._db_id)
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
            if hasattr(self, 'db_id') and ('opm_process', self._db_id) in id_remap:
                cp._db_id = id_remap[('opm_process', self._db_id)]
        
        # recreate indices and set flags
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBOpmProcessIdEffect()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False):
        return [(self, parent[0], parent[1])]
    def db_deleted_children(self, remove=False):
        children = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        return False
    def __get_db_id(self):
        return self._db_id
    def __set_db_id(self, id):
        self._db_id = id
        self.is_dirty = True
    db_id = property(__get_db_id, __set_db_id)
    def db_add_id(self, id):
        self._db_id = id
    def db_change_id(self, id):
        self._db_id = id
    def db_delete_id(self, id):
        self._db_id = None
    
class DBOpmRole(object):

    vtType = 'opm_role'

    def __init__(self, value=None):
        self._db_value = value
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBOpmRole.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBOpmRole(value=self._db_value)
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
        
        # recreate indices and set flags
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBOpmRole()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'value' in class_dict:
            res = class_dict['value'](old_obj, trans_dict)
            new_obj.db_value = res
        elif hasattr(old_obj, 'db_value') and old_obj.db_value is not None:
            new_obj.db_value = old_obj.db_value
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False):
        return [(self, parent[0], parent[1])]
    def db_deleted_children(self, remove=False):
        children = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        return False
    def __get_db_value(self):
        return self._db_value
    def __set_db_value(self, value):
        self._db_value = value
        self.is_dirty = True
    db_value = property(__get_db_value, __set_db_value)
    def db_add_value(self, value):
        self._db_value = value
    def db_change_value(self, value):
        self._db_value = value
    def db_delete_value(self, value):
        self._db_value = None
        
class DBOpmProcessIdCause(object):

    vtType = 'opm_process_id_cause'

    def __init__(self, id=None):
        self._db_id = id
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBOpmProcessIdCause.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBOpmProcessIdCause(id=self._db_id)
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
            if hasattr(self, 'db_id') and ('opm_process', self._db_id) in id_remap:
                cp._db_id = id_remap[('opm_process', self._db_id)]
        
        # recreate indices and set flags
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBOpmProcessIdCause()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False):
        return [(self, parent[0], parent[1])]
    def db_deleted_children(self, remove=False):
        children = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        return False
    def __get_db_id(self):
        return self._db_id
    def __set_db_id(self, id):
        self._db_id = id
        self.is_dirty = True
    db_id = property(__get_db_id, __set_db_id)
    def db_add_id(self, id):
        self._db_id = id
    def db_change_id(self, id):
        self._db_id = id
    def db_delete_id(self, id):
        self._db_id = None
    
class DBOpmArtifactIdEffect(object):

    vtType = 'opm_artifact_id_effect'

    def __init__(self, id=None):
        self._db_id = id
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBOpmArtifactIdEffect.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBOpmArtifactIdEffect(id=self._db_id)
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
            if hasattr(self, 'db_id') and ('opm_artifact', self._db_id) in id_remap:
                cp._db_id = id_remap[('opm_artifact', self._db_id)]
        
        # recreate indices and set flags
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBOpmArtifactIdEffect()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False):
        return [(self, parent[0], parent[1])]
    def db_deleted_children(self, remove=False):
        children = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        return False
    def __get_db_id(self):
        return self._db_id
    def __set_db_id(self, id):
        self._db_id = id
        self.is_dirty = True
    db_id = property(__get_db_id, __set_db_id)
    def db_add_id(self, id):
        self._db_id = id
    def db_change_id(self, id):
        self._db_id = id
    def db_delete_id(self, id):
        self._db_id = None
        
class DBOpmAgentId(object):

    vtType = 'opm_agent_id'

    def __init__(self, id=None):
        self._db_id = id
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBOpmAgentId.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBOpmAgentId(id=self._db_id)
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
            if hasattr(self, 'db_id') and ('opm_agent', self._db_id) in id_remap:
                cp._db_id = id_remap[('opm_agent', self._db_id)]
        
        # recreate indices and set flags
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBOpmAgentId()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False):
        return [(self, parent[0], parent[1])]
    def db_deleted_children(self, remove=False):
        children = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        return False
    def __get_db_id(self):
        return self._db_id
    def __set_db_id(self, id):
        self._db_id = id
        self.is_dirty = True
    db_id = property(__get_db_id, __set_db_id)
    def db_add_id(self, id):
        self._db_id = id
    def db_change_id(self, id):
        self._db_id = id
    def db_delete_id(self, id):
        self._db_id = None

class DBOpmProcessValue(object):

    vtType = 'opm_process_value'

    def __init__(self, value=None):
        self.db_deleted_value = []
        self._db_value = value
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBOpmProcessValue.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBOpmProcessValue()
        if self._db_value is not None:
            cp._db_value = self._db_value.do_copy(new_ids, id_scope, id_remap)
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
        
        # recreate indices and set flags
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBOpmProcessValue()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'value' in class_dict:
            res = class_dict['value'](old_obj, trans_dict)
            new_obj.db_value = res
        elif hasattr(old_obj, 'db_value') and old_obj.db_value is not None:
            obj = old_obj.db_value
            if obj.vtType == 'module_exec':
                new_obj.db_add_value(DBModuleExec.update_version(obj, trans_dict))
            elif obj.vtType == 'group_exec':
                new_obj.db_add_value(DBGroupExec.update_version(obj, trans_dict))
            elif obj.vtType == 'loop_exec':
                new_obj.db_add_value(DBLoopExec.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_value') and hasattr(new_obj, 'db_deleted_value'):
            for obj in old_obj.db_deleted_value:
                if obj.vtType == 'module_exec':
                    n_obj = DBModuleExec.update_version(obj, trans_dict)
                    new_obj.db_deleted_value.append(n_obj)
                elif obj.vtType == 'group_exec':
                    n_obj = DBGroupExec.update_version(obj, trans_dict)
                    new_obj.db_deleted_value.append(n_obj)
                elif obj.vtType == 'loop_exec':
                    n_obj = DBLoopExec.update_version(obj, trans_dict)
                    new_obj.db_deleted_value.append(n_obj)
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False):
        children = []
        if self._db_value is not None:
            children.extend(self._db_value.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                self._db_value = None
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_value)
        if remove:
            self.db_deleted_value = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        if self._db_value is not None and self._db_value.has_changes():
            return True
        return False
    def __get_db_value(self):
        return self._db_value
    def __set_db_value(self, value):
        self._db_value = value
        self.is_dirty = True
    db_value = property(__get_db_value, __set_db_value)
    def db_add_value(self, value):
        self._db_value = value
    def db_change_value(self, value):
        self._db_value = value
    def db_delete_value(self, value):
        if not self.is_new:
            self.db_deleted_value.append(self._db_value)
        self._db_value = None
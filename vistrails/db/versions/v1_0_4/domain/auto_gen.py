###############################################################################
##
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

"""generated automatically by auto_dao.py"""

import copy

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

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        children = []
        if self._db_effect is not None:
            children.extend(self._db_effect.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                self._db_effect = None
        if self._db_role is not None:
            children.extend(self._db_role.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                self._db_role = None
        if self._db_cause is not None:
            children.extend(self._db_cause.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                self._db_cause = None
        to_del = []
        for child in self.db_accounts:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_account(child)
        to_del = []
        for child in self.db_opm_times:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
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
    


class DBConfigKey(object):

    vtType = 'config_key'

    def __init__(self, value=None, name=None):
        self.db_deleted_value = []
        self._db_value = value
        self._db_name = name
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBConfigKey.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBConfigKey(name=self._db_name)
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
            new_obj = DBConfigKey()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'value' in class_dict:
            res = class_dict['value'](old_obj, trans_dict)
            new_obj.db_value = res
        elif hasattr(old_obj, 'db_value') and old_obj.db_value is not None:
            obj = old_obj.db_value
            if obj.vtType == 'config_str':
                new_obj.db_add_value(DBConfigStr.update_version(obj, trans_dict))
            elif obj.vtType == 'config_int':
                new_obj.db_add_value(DBConfigInt.update_version(obj, trans_dict))
            elif obj.vtType == 'config_float':
                new_obj.db_add_value(DBConfigFloat.update_version(obj, trans_dict))
            elif obj.vtType == 'config_bool':
                new_obj.db_add_value(DBConfigBool.update_version(obj, trans_dict))
            elif obj.vtType == 'configuration':
                new_obj.db_add_value(DBConfiguration.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_value') and hasattr(new_obj, 'db_deleted_value'):
            for obj in old_obj.db_deleted_value:
                if obj.vtType == 'config_str':
                    n_obj = DBConfigStr.update_version(obj, trans_dict)
                    new_obj.db_deleted_value.append(n_obj)
                elif obj.vtType == 'config_int':
                    n_obj = DBConfigInt.update_version(obj, trans_dict)
                    new_obj.db_deleted_value.append(n_obj)
                elif obj.vtType == 'config_float':
                    n_obj = DBConfigFloat.update_version(obj, trans_dict)
                    new_obj.db_deleted_value.append(n_obj)
                elif obj.vtType == 'config_bool':
                    n_obj = DBConfigBool.update_version(obj, trans_dict)
                    new_obj.db_deleted_value.append(n_obj)
                elif obj.vtType == 'configuration':
                    n_obj = DBConfiguration.update_version(obj, trans_dict)
                    new_obj.db_deleted_value.append(n_obj)
        if 'name' in class_dict:
            res = class_dict['name'](old_obj, trans_dict)
            new_obj.db_name = res
        elif hasattr(old_obj, 'db_name') and old_obj.db_name is not None:
            new_obj.db_name = old_obj.db_name
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        children = []
        if self._db_value is not None:
            children.extend(self._db_value.db_children((self.vtType, self.db_id), orphan, for_action))
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
    
    def getPrimaryKey(self):
        return self._db_name

class DBMashupAlias(object):

    vtType = 'mashup_alias'

    def __init__(self, id=None, name=None, component=None):
        self._db_id = id
        self._db_name = name
        self.db_deleted_component = []
        self._db_component = component
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBMashupAlias.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBMashupAlias(id=self._db_id,
                           name=self._db_name)
        if self._db_component is not None:
            cp._db_component = self._db_component.do_copy(new_ids, id_scope, id_remap)
        
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
            new_obj = DBMashupAlias()
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
        if 'component' in class_dict:
            res = class_dict['component'](old_obj, trans_dict)
            new_obj.db_component = res
        elif hasattr(old_obj, 'db_component') and old_obj.db_component is not None:
            obj = old_obj.db_component
            new_obj.db_add_component(DBMashupComponent.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_component') and hasattr(new_obj, 'db_deleted_component'):
            for obj in old_obj.db_deleted_component:
                n_obj = DBMashupComponent.update_version(obj, trans_dict)
                new_obj.db_deleted_component.append(n_obj)
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        children = []
        if self._db_component is not None:
            children.extend(self._db_component.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                self._db_component = None
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_component)
        if remove:
            self.db_deleted_component = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        if self._db_component is not None and self._db_component.has_changes():
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
    
    def __get_db_component(self):
        return self._db_component
    def __set_db_component(self, component):
        self._db_component = component
        self.is_dirty = True
    db_component = property(__get_db_component, __set_db_component)
    def db_add_component(self, component):
        self._db_component = component
    def db_change_component(self, component):
        self._db_component = component
    def db_delete_component(self, component):
        if not self.is_new:
            self.db_deleted_component.append(self._db_component)
        self._db_component = None
    
    def getPrimaryKey(self):
        return self._db_id

class DBGroup(object):

    vtType = 'group'

    def __init__(self, id=None, workflow=None, cache=None, name=None, namespace=None, package=None, version=None, location=None, functions=None, annotations=None, controlParameters=None):
        self._db_id = id
        self.db_deleted_workflow = []
        self._db_workflow = workflow
        self._db_cache = cache
        self._db_name = name
        self._db_namespace = namespace
        self._db_package = package
        self._db_version = version
        self.db_deleted_location = []
        self._db_location = location
        self.db_deleted_functions = []
        self.db_functions_id_index = {}
        if functions is None:
            self._db_functions = []
        else:
            self._db_functions = functions
            for v in self._db_functions:
                self.db_functions_id_index[v.db_id] = v
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
        self.db_deleted_controlParameters = []
        self.db_controlParameters_id_index = {}
        self.db_controlParameters_name_index = {}
        if controlParameters is None:
            self._db_controlParameters = []
        else:
            self._db_controlParameters = controlParameters
            for v in self._db_controlParameters:
                self.db_controlParameters_id_index[v.db_id] = v
                self.db_controlParameters_name_index[v.db_name] = v
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBGroup.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBGroup(id=self._db_id,
                     cache=self._db_cache,
                     name=self._db_name,
                     namespace=self._db_namespace,
                     package=self._db_package,
                     version=self._db_version)
        if self._db_workflow is not None:
            cp._db_workflow = self._db_workflow.do_copy()
        if self._db_location is not None:
            cp._db_location = self._db_location.do_copy(new_ids, id_scope, id_remap)
        if self._db_functions is None:
            cp._db_functions = []
        else:
            cp._db_functions = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_functions]
        if self._db_annotations is None:
            cp._db_annotations = []
        else:
            cp._db_annotations = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_annotations]
        if self._db_controlParameters is None:
            cp._db_controlParameters = []
        else:
            cp._db_controlParameters = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_controlParameters]
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
        
        # recreate indices and set flags
        cp.db_functions_id_index = dict((v.db_id, v) for v in cp._db_functions)
        cp.db_annotations_id_index = dict((v.db_id, v) for v in cp._db_annotations)
        cp.db_annotations_key_index = dict((v.db_key, v) for v in cp._db_annotations)
        cp.db_controlParameters_id_index = dict((v.db_id, v) for v in cp._db_controlParameters)
        cp.db_controlParameters_name_index = dict((v.db_name, v) for v in cp._db_controlParameters)
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBGroup()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'workflow' in class_dict:
            res = class_dict['workflow'](old_obj, trans_dict)
            new_obj.db_workflow = res
        elif hasattr(old_obj, 'db_workflow') and old_obj.db_workflow is not None:
            obj = old_obj.db_workflow
            new_obj.db_add_workflow(DBWorkflow.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_workflow') and hasattr(new_obj, 'db_deleted_workflow'):
            for obj in old_obj.db_deleted_workflow:
                n_obj = DBWorkflow.update_version(obj, trans_dict)
                new_obj.db_deleted_workflow.append(n_obj)
        if 'cache' in class_dict:
            res = class_dict['cache'](old_obj, trans_dict)
            new_obj.db_cache = res
        elif hasattr(old_obj, 'db_cache') and old_obj.db_cache is not None:
            new_obj.db_cache = old_obj.db_cache
        if 'name' in class_dict:
            res = class_dict['name'](old_obj, trans_dict)
            new_obj.db_name = res
        elif hasattr(old_obj, 'db_name') and old_obj.db_name is not None:
            new_obj.db_name = old_obj.db_name
        if 'namespace' in class_dict:
            res = class_dict['namespace'](old_obj, trans_dict)
            new_obj.db_namespace = res
        elif hasattr(old_obj, 'db_namespace') and old_obj.db_namespace is not None:
            new_obj.db_namespace = old_obj.db_namespace
        if 'package' in class_dict:
            res = class_dict['package'](old_obj, trans_dict)
            new_obj.db_package = res
        elif hasattr(old_obj, 'db_package') and old_obj.db_package is not None:
            new_obj.db_package = old_obj.db_package
        if 'version' in class_dict:
            res = class_dict['version'](old_obj, trans_dict)
            new_obj.db_version = res
        elif hasattr(old_obj, 'db_version') and old_obj.db_version is not None:
            new_obj.db_version = old_obj.db_version
        if 'location' in class_dict:
            res = class_dict['location'](old_obj, trans_dict)
            new_obj.db_location = res
        elif hasattr(old_obj, 'db_location') and old_obj.db_location is not None:
            obj = old_obj.db_location
            new_obj.db_add_location(DBLocation.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_location') and hasattr(new_obj, 'db_deleted_location'):
            for obj in old_obj.db_deleted_location:
                n_obj = DBLocation.update_version(obj, trans_dict)
                new_obj.db_deleted_location.append(n_obj)
        if 'functions' in class_dict:
            res = class_dict['functions'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_function(obj)
        elif hasattr(old_obj, 'db_functions') and old_obj.db_functions is not None:
            for obj in old_obj.db_functions:
                new_obj.db_add_function(DBFunction.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_functions') and hasattr(new_obj, 'db_deleted_functions'):
            for obj in old_obj.db_deleted_functions:
                n_obj = DBFunction.update_version(obj, trans_dict)
                new_obj.db_deleted_functions.append(n_obj)
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
        if 'controlParameters' in class_dict:
            res = class_dict['controlParameters'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_controlParameter(obj)
        elif hasattr(old_obj, 'db_controlParameters') and old_obj.db_controlParameters is not None:
            for obj in old_obj.db_controlParameters:
                new_obj.db_add_controlParameter(DBControlParameter.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_controlParameters') and hasattr(new_obj, 'db_deleted_controlParameters'):
            for obj in old_obj.db_deleted_controlParameters:
                n_obj = DBControlParameter.update_version(obj, trans_dict)
                new_obj.db_deleted_controlParameters.append(n_obj)
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        children = []
        if self._db_location is not None:
            children.extend(self._db_location.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                self._db_location = None
        to_del = []
        for child in self.db_functions:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_function(child)
        to_del = []
        for child in self.db_annotations:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_annotation(child)
        to_del = []
        for child in self.db_controlParameters:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_controlParameter(child)
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_workflow)
        children.extend(self.db_deleted_location)
        children.extend(self.db_deleted_functions)
        children.extend(self.db_deleted_annotations)
        children.extend(self.db_deleted_controlParameters)
        if remove:
            self.db_deleted_workflow = []
            self.db_deleted_location = []
            self.db_deleted_functions = []
            self.db_deleted_annotations = []
            self.db_deleted_controlParameters = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        if self._db_workflow is not None and self._db_workflow.has_changes():
            return True
        if self._db_location is not None and self._db_location.has_changes():
            return True
        for child in self._db_functions:
            if child.has_changes():
                return True
        for child in self._db_annotations:
            if child.has_changes():
                return True
        for child in self._db_controlParameters:
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
    
    def __get_db_workflow(self):
        return self._db_workflow
    def __set_db_workflow(self, workflow):
        self._db_workflow = workflow
        self.is_dirty = True
    db_workflow = property(__get_db_workflow, __set_db_workflow)
    def db_add_workflow(self, workflow):
        self._db_workflow = workflow
    def db_change_workflow(self, workflow):
        self._db_workflow = workflow
    def db_delete_workflow(self, workflow):
        if not self.is_new:
            self.db_deleted_workflow.append(self._db_workflow)
        self._db_workflow = None
    
    def __get_db_cache(self):
        return self._db_cache
    def __set_db_cache(self, cache):
        self._db_cache = cache
        self.is_dirty = True
    db_cache = property(__get_db_cache, __set_db_cache)
    def db_add_cache(self, cache):
        self._db_cache = cache
    def db_change_cache(self, cache):
        self._db_cache = cache
    def db_delete_cache(self, cache):
        self._db_cache = None
    
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
    
    def __get_db_namespace(self):
        return self._db_namespace
    def __set_db_namespace(self, namespace):
        self._db_namespace = namespace
        self.is_dirty = True
    db_namespace = property(__get_db_namespace, __set_db_namespace)
    def db_add_namespace(self, namespace):
        self._db_namespace = namespace
    def db_change_namespace(self, namespace):
        self._db_namespace = namespace
    def db_delete_namespace(self, namespace):
        self._db_namespace = None
    
    def __get_db_package(self):
        return self._db_package
    def __set_db_package(self, package):
        self._db_package = package
        self.is_dirty = True
    db_package = property(__get_db_package, __set_db_package)
    def db_add_package(self, package):
        self._db_package = package
    def db_change_package(self, package):
        self._db_package = package
    def db_delete_package(self, package):
        self._db_package = None
    
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
    
    def __get_db_location(self):
        return self._db_location
    def __set_db_location(self, location):
        self._db_location = location
        self.is_dirty = True
    db_location = property(__get_db_location, __set_db_location)
    def db_add_location(self, location):
        self._db_location = location
    def db_change_location(self, location):
        self._db_location = location
    def db_delete_location(self, location):
        if not self.is_new:
            self.db_deleted_location.append(self._db_location)
        self._db_location = None
    
    def __get_db_functions(self):
        return self._db_functions
    def __set_db_functions(self, functions):
        self._db_functions = functions
        self.is_dirty = True
    db_functions = property(__get_db_functions, __set_db_functions)
    def db_get_functions(self):
        return self._db_functions
    def db_add_function(self, function):
        self.is_dirty = True
        self._db_functions.append(function)
        self.db_functions_id_index[function.db_id] = function
    def db_change_function(self, function):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_functions)):
            if self._db_functions[i].db_id == function.db_id:
                self._db_functions[i] = function
                found = True
                break
        if not found:
            self._db_functions.append(function)
        self.db_functions_id_index[function.db_id] = function
    def db_delete_function(self, function):
        self.is_dirty = True
        for i in xrange(len(self._db_functions)):
            if self._db_functions[i].db_id == function.db_id:
                if not self._db_functions[i].is_new:
                    self.db_deleted_functions.append(self._db_functions[i])
                del self._db_functions[i]
                break
        del self.db_functions_id_index[function.db_id]
    def db_get_function(self, key):
        for i in xrange(len(self._db_functions)):
            if self._db_functions[i].db_id == key:
                return self._db_functions[i]
        return None
    def db_get_function_by_id(self, key):
        return self.db_functions_id_index[key]
    def db_has_function_with_id(self, key):
        return key in self.db_functions_id_index
    
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
    
    def __get_db_controlParameters(self):
        return self._db_controlParameters
    def __set_db_controlParameters(self, controlParameters):
        self._db_controlParameters = controlParameters
        self.is_dirty = True
    db_controlParameters = property(__get_db_controlParameters, __set_db_controlParameters)
    def db_get_controlParameters(self):
        return self._db_controlParameters
    def db_add_controlParameter(self, controlParameter):
        self.is_dirty = True
        self._db_controlParameters.append(controlParameter)
        self.db_controlParameters_id_index[controlParameter.db_id] = controlParameter
        self.db_controlParameters_name_index[controlParameter.db_name] = controlParameter
    def db_change_controlParameter(self, controlParameter):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_controlParameters)):
            if self._db_controlParameters[i].db_id == controlParameter.db_id:
                self._db_controlParameters[i] = controlParameter
                found = True
                break
        if not found:
            self._db_controlParameters.append(controlParameter)
        self.db_controlParameters_id_index[controlParameter.db_id] = controlParameter
        self.db_controlParameters_name_index[controlParameter.db_name] = controlParameter
    def db_delete_controlParameter(self, controlParameter):
        self.is_dirty = True
        for i in xrange(len(self._db_controlParameters)):
            if self._db_controlParameters[i].db_id == controlParameter.db_id:
                if not self._db_controlParameters[i].is_new:
                    self.db_deleted_controlParameters.append(self._db_controlParameters[i])
                del self._db_controlParameters[i]
                break
        del self.db_controlParameters_id_index[controlParameter.db_id]
        del self.db_controlParameters_name_index[controlParameter.db_name]
    def db_get_controlParameter(self, key):
        for i in xrange(len(self._db_controlParameters)):
            if self._db_controlParameters[i].db_id == key:
                return self._db_controlParameters[i]
        return None
    def db_get_controlParameter_by_id(self, key):
        return self.db_controlParameters_id_index[key]
    def db_has_controlParameter_with_id(self, key):
        return key in self.db_controlParameters_id_index
    def db_get_controlParameter_by_name(self, key):
        return self.db_controlParameters_name_index[key]
    def db_has_controlParameter_with_name(self, key):
        return key in self.db_controlParameters_name_index
    
    def getPrimaryKey(self):
        return self._db_id

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

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        children = []
        if self._db_effect is not None:
            children.extend(self._db_effect.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                self._db_effect = None
        if self._db_role is not None:
            children.extend(self._db_role.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                self._db_role = None
        if self._db_cause is not None:
            children.extend(self._db_cause.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                self._db_cause = None
        to_del = []
        for child in self.db_accounts:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_account(child)
        to_del = []
        for child in self.db_starts:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_start(child)
        to_del = []
        for child in self.db_ends:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
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
    


class DBAdd(object):

    vtType = 'add'

    def __init__(self, data=None, id=None, what=None, objectId=None, parentObjId=None, parentObjType=None):
        self.db_deleted_data = []
        self._db_data = data
        self._db_id = id
        self._db_what = what
        self._db_objectId = objectId
        self._db_parentObjId = parentObjId
        self._db_parentObjType = parentObjType
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBAdd.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBAdd(id=self._db_id,
                   what=self._db_what,
                   objectId=self._db_objectId,
                   parentObjId=self._db_parentObjId,
                   parentObjType=self._db_parentObjType)
        if self._db_data is not None:
            cp._db_data = self._db_data.do_copy(new_ids, id_scope, id_remap)
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
            if hasattr(self, 'db_objectId') and (self._db_what, self._db_objectId) in id_remap:
                cp._db_objectId = id_remap[(self._db_what, self._db_objectId)]
            if hasattr(self, 'db_parentObjId') and (self._db_parentObjType, self._db_parentObjId) in id_remap:
                cp._db_parentObjId = id_remap[(self._db_parentObjType, self._db_parentObjId)]
        
        # recreate indices and set flags
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBAdd()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'data' in class_dict:
            res = class_dict['data'](old_obj, trans_dict)
            new_obj.db_data = res
        elif hasattr(old_obj, 'db_data') and old_obj.db_data is not None:
            obj = old_obj.db_data
            if obj.vtType == 'module':
                new_obj.db_add_data(DBModule.update_version(obj, trans_dict))
            elif obj.vtType == 'location':
                new_obj.db_add_data(DBLocation.update_version(obj, trans_dict))
            elif obj.vtType == 'annotation':
                new_obj.db_add_data(DBAnnotation.update_version(obj, trans_dict))
            elif obj.vtType == 'controlParameter':
                new_obj.db_add_data(DBControlParameter.update_version(obj, trans_dict))
            elif obj.vtType == 'function':
                new_obj.db_add_data(DBFunction.update_version(obj, trans_dict))
            elif obj.vtType == 'connection':
                new_obj.db_add_data(DBConnection.update_version(obj, trans_dict))
            elif obj.vtType == 'port':
                new_obj.db_add_data(DBPort.update_version(obj, trans_dict))
            elif obj.vtType == 'parameter':
                new_obj.db_add_data(DBParameter.update_version(obj, trans_dict))
            elif obj.vtType == 'portSpec':
                new_obj.db_add_data(DBPortSpec.update_version(obj, trans_dict))
            elif obj.vtType == 'abstraction':
                new_obj.db_add_data(DBAbstraction.update_version(obj, trans_dict))
            elif obj.vtType == 'group':
                new_obj.db_add_data(DBGroup.update_version(obj, trans_dict))
            elif obj.vtType == 'other':
                new_obj.db_add_data(DBOther.update_version(obj, trans_dict))
            elif obj.vtType == 'plugin_data':
                new_obj.db_add_data(DBPluginData.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_data') and hasattr(new_obj, 'db_deleted_data'):
            for obj in old_obj.db_deleted_data:
                if obj.vtType == 'module':
                    n_obj = DBModule.update_version(obj, trans_dict)
                    new_obj.db_deleted_data.append(n_obj)
                elif obj.vtType == 'location':
                    n_obj = DBLocation.update_version(obj, trans_dict)
                    new_obj.db_deleted_data.append(n_obj)
                elif obj.vtType == 'annotation':
                    n_obj = DBAnnotation.update_version(obj, trans_dict)
                    new_obj.db_deleted_data.append(n_obj)
                elif obj.vtType == 'controlParameter':
                    n_obj = DBControlParameter.update_version(obj, trans_dict)
                    new_obj.db_deleted_data.append(n_obj)
                elif obj.vtType == 'function':
                    n_obj = DBFunction.update_version(obj, trans_dict)
                    new_obj.db_deleted_data.append(n_obj)
                elif obj.vtType == 'connection':
                    n_obj = DBConnection.update_version(obj, trans_dict)
                    new_obj.db_deleted_data.append(n_obj)
                elif obj.vtType == 'port':
                    n_obj = DBPort.update_version(obj, trans_dict)
                    new_obj.db_deleted_data.append(n_obj)
                elif obj.vtType == 'parameter':
                    n_obj = DBParameter.update_version(obj, trans_dict)
                    new_obj.db_deleted_data.append(n_obj)
                elif obj.vtType == 'portSpec':
                    n_obj = DBPortSpec.update_version(obj, trans_dict)
                    new_obj.db_deleted_data.append(n_obj)
                elif obj.vtType == 'abstraction':
                    n_obj = DBAbstraction.update_version(obj, trans_dict)
                    new_obj.db_deleted_data.append(n_obj)
                elif obj.vtType == 'group':
                    n_obj = DBGroup.update_version(obj, trans_dict)
                    new_obj.db_deleted_data.append(n_obj)
                elif obj.vtType == 'other':
                    n_obj = DBOther.update_version(obj, trans_dict)
                    new_obj.db_deleted_data.append(n_obj)
                elif obj.vtType == 'plugin_data':
                    n_obj = DBPluginData.update_version(obj, trans_dict)
                    new_obj.db_deleted_data.append(n_obj)
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'what' in class_dict:
            res = class_dict['what'](old_obj, trans_dict)
            new_obj.db_what = res
        elif hasattr(old_obj, 'db_what') and old_obj.db_what is not None:
            new_obj.db_what = old_obj.db_what
        if 'objectId' in class_dict:
            res = class_dict['objectId'](old_obj, trans_dict)
            new_obj.db_objectId = res
        elif hasattr(old_obj, 'db_objectId') and old_obj.db_objectId is not None:
            new_obj.db_objectId = old_obj.db_objectId
        if 'parentObjId' in class_dict:
            res = class_dict['parentObjId'](old_obj, trans_dict)
            new_obj.db_parentObjId = res
        elif hasattr(old_obj, 'db_parentObjId') and old_obj.db_parentObjId is not None:
            new_obj.db_parentObjId = old_obj.db_parentObjId
        if 'parentObjType' in class_dict:
            res = class_dict['parentObjType'](old_obj, trans_dict)
            new_obj.db_parentObjType = res
        elif hasattr(old_obj, 'db_parentObjType') and old_obj.db_parentObjType is not None:
            new_obj.db_parentObjType = old_obj.db_parentObjType
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        children = []
        if self._db_data is not None:
            children.extend(self._db_data.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                self._db_data = None
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_data)
        if remove:
            self.db_deleted_data = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        if self._db_data is not None and self._db_data.has_changes():
            return True
        return False
    def __get_db_data(self):
        return self._db_data
    def __set_db_data(self, data):
        self._db_data = data
        self.is_dirty = True
    db_data = property(__get_db_data, __set_db_data)
    def db_add_data(self, data):
        self._db_data = data
    def db_change_data(self, data):
        self._db_data = data
    def db_delete_data(self, data):
        if not self.is_new:
            self.db_deleted_data.append(self._db_data)
        self._db_data = None
    
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
    
    def __get_db_what(self):
        return self._db_what
    def __set_db_what(self, what):
        self._db_what = what
        self.is_dirty = True
    db_what = property(__get_db_what, __set_db_what)
    def db_add_what(self, what):
        self._db_what = what
    def db_change_what(self, what):
        self._db_what = what
    def db_delete_what(self, what):
        self._db_what = None
    
    def __get_db_objectId(self):
        return self._db_objectId
    def __set_db_objectId(self, objectId):
        self._db_objectId = objectId
        self.is_dirty = True
    db_objectId = property(__get_db_objectId, __set_db_objectId)
    def db_add_objectId(self, objectId):
        self._db_objectId = objectId
    def db_change_objectId(self, objectId):
        self._db_objectId = objectId
    def db_delete_objectId(self, objectId):
        self._db_objectId = None
    
    def __get_db_parentObjId(self):
        return self._db_parentObjId
    def __set_db_parentObjId(self, parentObjId):
        self._db_parentObjId = parentObjId
        self.is_dirty = True
    db_parentObjId = property(__get_db_parentObjId, __set_db_parentObjId)
    def db_add_parentObjId(self, parentObjId):
        self._db_parentObjId = parentObjId
    def db_change_parentObjId(self, parentObjId):
        self._db_parentObjId = parentObjId
    def db_delete_parentObjId(self, parentObjId):
        self._db_parentObjId = None
    
    def __get_db_parentObjType(self):
        return self._db_parentObjType
    def __set_db_parentObjType(self, parentObjType):
        self._db_parentObjType = parentObjType
        self.is_dirty = True
    db_parentObjType = property(__get_db_parentObjType, __set_db_parentObjType)
    def db_add_parentObjType(self, parentObjType):
        self._db_parentObjType = parentObjType
    def db_change_parentObjType(self, parentObjType):
        self._db_parentObjType = parentObjType
    def db_delete_parentObjType(self, parentObjType):
        self._db_parentObjType = None
    
    def getPrimaryKey(self):
        return self._db_id

class DBProvGeneration(object):

    vtType = 'prov_generation'

    def __init__(self, prov_entity=None, prov_activity=None, prov_role=None):
        self.db_deleted_prov_entity = []
        self._db_prov_entity = prov_entity
        self.db_deleted_prov_activity = []
        self._db_prov_activity = prov_activity
        self._db_prov_role = prov_role
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBProvGeneration.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBProvGeneration(prov_role=self._db_prov_role)
        if self._db_prov_entity is not None:
            cp._db_prov_entity = self._db_prov_entity.do_copy(new_ids, id_scope, id_remap)
        if self._db_prov_activity is not None:
            cp._db_prov_activity = self._db_prov_activity.do_copy(new_ids, id_scope, id_remap)
        
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
            new_obj = DBProvGeneration()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'prov_entity' in class_dict:
            res = class_dict['prov_entity'](old_obj, trans_dict)
            new_obj.db_prov_entity = res
        elif hasattr(old_obj, 'db_prov_entity') and old_obj.db_prov_entity is not None:
            obj = old_obj.db_prov_entity
            new_obj.db_add_prov_entity(DBRefProvEntity.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_prov_entity') and hasattr(new_obj, 'db_deleted_prov_entity'):
            for obj in old_obj.db_deleted_prov_entity:
                n_obj = DBRefProvEntity.update_version(obj, trans_dict)
                new_obj.db_deleted_prov_entity.append(n_obj)
        if 'prov_activity' in class_dict:
            res = class_dict['prov_activity'](old_obj, trans_dict)
            new_obj.db_prov_activity = res
        elif hasattr(old_obj, 'db_prov_activity') and old_obj.db_prov_activity is not None:
            obj = old_obj.db_prov_activity
            new_obj.db_add_prov_activity(DBRefProvActivity.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_prov_activity') and hasattr(new_obj, 'db_deleted_prov_activity'):
            for obj in old_obj.db_deleted_prov_activity:
                n_obj = DBRefProvActivity.update_version(obj, trans_dict)
                new_obj.db_deleted_prov_activity.append(n_obj)
        if 'prov_role' in class_dict:
            res = class_dict['prov_role'](old_obj, trans_dict)
            new_obj.db_prov_role = res
        elif hasattr(old_obj, 'db_prov_role') and old_obj.db_prov_role is not None:
            new_obj.db_prov_role = old_obj.db_prov_role
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        children = []
        if self._db_prov_entity is not None:
            children.extend(self._db_prov_entity.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                self._db_prov_entity = None
        if self._db_prov_activity is not None:
            children.extend(self._db_prov_activity.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                self._db_prov_activity = None
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_prov_entity)
        children.extend(self.db_deleted_prov_activity)
        if remove:
            self.db_deleted_prov_entity = []
            self.db_deleted_prov_activity = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        if self._db_prov_entity is not None and self._db_prov_entity.has_changes():
            return True
        if self._db_prov_activity is not None and self._db_prov_activity.has_changes():
            return True
        return False
    def __get_db_prov_entity(self):
        return self._db_prov_entity
    def __set_db_prov_entity(self, prov_entity):
        self._db_prov_entity = prov_entity
        self.is_dirty = True
    db_prov_entity = property(__get_db_prov_entity, __set_db_prov_entity)
    def db_add_prov_entity(self, prov_entity):
        self._db_prov_entity = prov_entity
    def db_change_prov_entity(self, prov_entity):
        self._db_prov_entity = prov_entity
    def db_delete_prov_entity(self, prov_entity):
        if not self.is_new:
            self.db_deleted_prov_entity.append(self._db_prov_entity)
        self._db_prov_entity = None
    
    def __get_db_prov_activity(self):
        return self._db_prov_activity
    def __set_db_prov_activity(self, prov_activity):
        self._db_prov_activity = prov_activity
        self.is_dirty = True
    db_prov_activity = property(__get_db_prov_activity, __set_db_prov_activity)
    def db_add_prov_activity(self, prov_activity):
        self._db_prov_activity = prov_activity
    def db_change_prov_activity(self, prov_activity):
        self._db_prov_activity = prov_activity
    def db_delete_prov_activity(self, prov_activity):
        if not self.is_new:
            self.db_deleted_prov_activity.append(self._db_prov_activity)
        self._db_prov_activity = None
    
    def __get_db_prov_role(self):
        return self._db_prov_role
    def __set_db_prov_role(self, prov_role):
        self._db_prov_role = prov_role
        self.is_dirty = True
    db_prov_role = property(__get_db_prov_role, __set_db_prov_role)
    def db_add_prov_role(self, prov_role):
        self._db_prov_role = prov_role
    def db_change_prov_role(self, prov_role):
        self._db_prov_role = prov_role
    def db_delete_prov_role(self, prov_role):
        self._db_prov_role = None
    


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

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        children = []
        if self._db_effect is not None:
            children.extend(self._db_effect.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                self._db_effect = None
        if self._db_role is not None:
            children.extend(self._db_role.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                self._db_role = None
        if self._db_cause is not None:
            children.extend(self._db_cause.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                self._db_cause = None
        to_del = []
        for child in self.db_accounts:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_account(child)
        to_del = []
        for child in self.db_opm_times:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
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

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
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
    


class DBRefProvEntity(object):

    vtType = 'ref_prov_entity'

    def __init__(self, prov_ref=None):
        self._db_prov_ref = prov_ref
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBRefProvEntity.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBRefProvEntity(prov_ref=self._db_prov_ref)
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
            if hasattr(self, 'db_prov_ref') and ('prov_entity', self._db_prov_ref) in id_remap:
                cp._db_prov_ref = id_remap[('prov_entity', self._db_prov_ref)]
        
        # recreate indices and set flags
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBRefProvEntity()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'prov_ref' in class_dict:
            res = class_dict['prov_ref'](old_obj, trans_dict)
            new_obj.db_prov_ref = res
        elif hasattr(old_obj, 'db_prov_ref') and old_obj.db_prov_ref is not None:
            new_obj.db_prov_ref = old_obj.db_prov_ref
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        return [(self, parent[0], parent[1])]
    def db_deleted_children(self, remove=False):
        children = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        return False
    def __get_db_prov_ref(self):
        return self._db_prov_ref
    def __set_db_prov_ref(self, prov_ref):
        self._db_prov_ref = prov_ref
        self.is_dirty = True
    db_prov_ref = property(__get_db_prov_ref, __set_db_prov_ref)
    def db_add_prov_ref(self, prov_ref):
        self._db_prov_ref = prov_ref
    def db_change_prov_ref(self, prov_ref):
        self._db_prov_ref = prov_ref
    def db_delete_prov_ref(self, prov_ref):
        self._db_prov_ref = None
    


class DBVtConnection(object):

    vtType = 'vt_connection'

    def __init__(self, id=None, vt_source=None, vt_dest=None, vt_source_port=None, vt_dest_port=None, vt_source_signature=None, vt_dest_signature=None):
        self._db_id = id
        self._db_vt_source = vt_source
        self._db_vt_dest = vt_dest
        self._db_vt_source_port = vt_source_port
        self._db_vt_dest_port = vt_dest_port
        self._db_vt_source_signature = vt_source_signature
        self._db_vt_dest_signature = vt_dest_signature
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBVtConnection.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBVtConnection(id=self._db_id,
                            vt_source=self._db_vt_source,
                            vt_dest=self._db_vt_dest,
                            vt_source_port=self._db_vt_source_port,
                            vt_dest_port=self._db_vt_dest_port,
                            vt_source_signature=self._db_vt_source_signature,
                            vt_dest_signature=self._db_vt_dest_signature)
        
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
            new_obj = DBVtConnection()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'vt_source' in class_dict:
            res = class_dict['vt_source'](old_obj, trans_dict)
            new_obj.db_vt_source = res
        elif hasattr(old_obj, 'db_vt_source') and old_obj.db_vt_source is not None:
            new_obj.db_vt_source = old_obj.db_vt_source
        if 'vt_dest' in class_dict:
            res = class_dict['vt_dest'](old_obj, trans_dict)
            new_obj.db_vt_dest = res
        elif hasattr(old_obj, 'db_vt_dest') and old_obj.db_vt_dest is not None:
            new_obj.db_vt_dest = old_obj.db_vt_dest
        if 'vt_source_port' in class_dict:
            res = class_dict['vt_source_port'](old_obj, trans_dict)
            new_obj.db_vt_source_port = res
        elif hasattr(old_obj, 'db_vt_source_port') and old_obj.db_vt_source_port is not None:
            new_obj.db_vt_source_port = old_obj.db_vt_source_port
        if 'vt_dest_port' in class_dict:
            res = class_dict['vt_dest_port'](old_obj, trans_dict)
            new_obj.db_vt_dest_port = res
        elif hasattr(old_obj, 'db_vt_dest_port') and old_obj.db_vt_dest_port is not None:
            new_obj.db_vt_dest_port = old_obj.db_vt_dest_port
        if 'vt_source_signature' in class_dict:
            res = class_dict['vt_source_signature'](old_obj, trans_dict)
            new_obj.db_vt_source_signature = res
        elif hasattr(old_obj, 'db_vt_source_signature') and old_obj.db_vt_source_signature is not None:
            new_obj.db_vt_source_signature = old_obj.db_vt_source_signature
        if 'vt_dest_signature' in class_dict:
            res = class_dict['vt_dest_signature'](old_obj, trans_dict)
            new_obj.db_vt_dest_signature = res
        elif hasattr(old_obj, 'db_vt_dest_signature') and old_obj.db_vt_dest_signature is not None:
            new_obj.db_vt_dest_signature = old_obj.db_vt_dest_signature
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
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
    
    def __get_db_vt_source(self):
        return self._db_vt_source
    def __set_db_vt_source(self, vt_source):
        self._db_vt_source = vt_source
        self.is_dirty = True
    db_vt_source = property(__get_db_vt_source, __set_db_vt_source)
    def db_add_vt_source(self, vt_source):
        self._db_vt_source = vt_source
    def db_change_vt_source(self, vt_source):
        self._db_vt_source = vt_source
    def db_delete_vt_source(self, vt_source):
        self._db_vt_source = None
    
    def __get_db_vt_dest(self):
        return self._db_vt_dest
    def __set_db_vt_dest(self, vt_dest):
        self._db_vt_dest = vt_dest
        self.is_dirty = True
    db_vt_dest = property(__get_db_vt_dest, __set_db_vt_dest)
    def db_add_vt_dest(self, vt_dest):
        self._db_vt_dest = vt_dest
    def db_change_vt_dest(self, vt_dest):
        self._db_vt_dest = vt_dest
    def db_delete_vt_dest(self, vt_dest):
        self._db_vt_dest = None
    
    def __get_db_vt_source_port(self):
        return self._db_vt_source_port
    def __set_db_vt_source_port(self, vt_source_port):
        self._db_vt_source_port = vt_source_port
        self.is_dirty = True
    db_vt_source_port = property(__get_db_vt_source_port, __set_db_vt_source_port)
    def db_add_vt_source_port(self, vt_source_port):
        self._db_vt_source_port = vt_source_port
    def db_change_vt_source_port(self, vt_source_port):
        self._db_vt_source_port = vt_source_port
    def db_delete_vt_source_port(self, vt_source_port):
        self._db_vt_source_port = None
    
    def __get_db_vt_dest_port(self):
        return self._db_vt_dest_port
    def __set_db_vt_dest_port(self, vt_dest_port):
        self._db_vt_dest_port = vt_dest_port
        self.is_dirty = True
    db_vt_dest_port = property(__get_db_vt_dest_port, __set_db_vt_dest_port)
    def db_add_vt_dest_port(self, vt_dest_port):
        self._db_vt_dest_port = vt_dest_port
    def db_change_vt_dest_port(self, vt_dest_port):
        self._db_vt_dest_port = vt_dest_port
    def db_delete_vt_dest_port(self, vt_dest_port):
        self._db_vt_dest_port = None
    
    def __get_db_vt_source_signature(self):
        return self._db_vt_source_signature
    def __set_db_vt_source_signature(self, vt_source_signature):
        self._db_vt_source_signature = vt_source_signature
        self.is_dirty = True
    db_vt_source_signature = property(__get_db_vt_source_signature, __set_db_vt_source_signature)
    def db_add_vt_source_signature(self, vt_source_signature):
        self._db_vt_source_signature = vt_source_signature
    def db_change_vt_source_signature(self, vt_source_signature):
        self._db_vt_source_signature = vt_source_signature
    def db_delete_vt_source_signature(self, vt_source_signature):
        self._db_vt_source_signature = None
    
    def __get_db_vt_dest_signature(self):
        return self._db_vt_dest_signature
    def __set_db_vt_dest_signature(self, vt_dest_signature):
        self._db_vt_dest_signature = vt_dest_signature
        self.is_dirty = True
    db_vt_dest_signature = property(__get_db_vt_dest_signature, __set_db_vt_dest_signature)
    def db_add_vt_dest_signature(self, vt_dest_signature):
        self._db_vt_dest_signature = vt_dest_signature
    def db_change_vt_dest_signature(self, vt_dest_signature):
        self._db_vt_dest_signature = vt_dest_signature
    def db_delete_vt_dest_signature(self, vt_dest_signature):
        self._db_vt_dest_signature = None
    
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

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
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

class DBGroupExec(object):

    vtType = 'group_exec'

    def __init__(self, item_execs=None, id=None, ts_start=None, ts_end=None, cached=None, module_id=None, group_name=None, group_type=None, completed=None, error=None, machine_id=None, annotations=None):
        self.db_deleted_item_execs = []
        self.db_item_execs_id_index = {}
        if item_execs is None:
            self._db_item_execs = []
        else:
            self._db_item_execs = item_execs
            for v in self._db_item_execs:
                self.db_item_execs_id_index[v.db_id] = v
        self._db_id = id
        self._db_ts_start = ts_start
        self._db_ts_end = ts_end
        self._db_cached = cached
        self._db_module_id = module_id
        self._db_group_name = group_name
        self._db_group_type = group_type
        self._db_completed = completed
        self._db_error = error
        self._db_machine_id = machine_id
        self.db_deleted_annotations = []
        self.db_annotations_id_index = {}
        if annotations is None:
            self._db_annotations = []
        else:
            self._db_annotations = annotations
            for v in self._db_annotations:
                self.db_annotations_id_index[v.db_id] = v
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBGroupExec.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBGroupExec(id=self._db_id,
                         ts_start=self._db_ts_start,
                         ts_end=self._db_ts_end,
                         cached=self._db_cached,
                         module_id=self._db_module_id,
                         group_name=self._db_group_name,
                         group_type=self._db_group_type,
                         completed=self._db_completed,
                         error=self._db_error,
                         machine_id=self._db_machine_id)
        if self._db_item_execs is None:
            cp._db_item_execs = []
        else:
            cp._db_item_execs = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_item_execs]
        if self._db_annotations is None:
            cp._db_annotations = []
        else:
            cp._db_annotations = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_annotations]
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
            if hasattr(self, 'db_module_id') and ('module', self._db_module_id) in id_remap:
                cp._db_module_id = id_remap[('module', self._db_module_id)]
            if hasattr(self, 'db_machine_id') and ('machine', self._db_machine_id) in id_remap:
                cp._db_machine_id = id_remap[('machine', self._db_machine_id)]
        
        # recreate indices and set flags
        cp.db_item_execs_id_index = dict((v.db_id, v) for v in cp._db_item_execs)
        cp.db_annotations_id_index = dict((v.db_id, v) for v in cp._db_annotations)
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBGroupExec()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'item_execs' in class_dict:
            res = class_dict['item_execs'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_item_exec(obj)
        elif hasattr(old_obj, 'db_item_execs') and old_obj.db_item_execs is not None:
            for obj in old_obj.db_item_execs:
                if obj.vtType == 'module_exec':
                    new_obj.db_add_item_exec(DBModuleExec.update_version(obj, trans_dict))
                elif obj.vtType == 'group_exec':
                    new_obj.db_add_item_exec(DBGroupExec.update_version(obj, trans_dict))
                elif obj.vtType == 'loop_exec':
                    new_obj.db_add_item_exec(DBLoopExec.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_item_execs') and hasattr(new_obj, 'db_deleted_item_execs'):
            for obj in old_obj.db_deleted_item_execs:
                if obj.vtType == 'module_exec':
                    n_obj = DBModuleExec.update_version(obj, trans_dict)
                    new_obj.db_deleted_item_execs.append(n_obj)
                elif obj.vtType == 'group_exec':
                    n_obj = DBGroupExec.update_version(obj, trans_dict)
                    new_obj.db_deleted_item_execs.append(n_obj)
                elif obj.vtType == 'loop_exec':
                    n_obj = DBLoopExec.update_version(obj, trans_dict)
                    new_obj.db_deleted_item_execs.append(n_obj)
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'ts_start' in class_dict:
            res = class_dict['ts_start'](old_obj, trans_dict)
            new_obj.db_ts_start = res
        elif hasattr(old_obj, 'db_ts_start') and old_obj.db_ts_start is not None:
            new_obj.db_ts_start = old_obj.db_ts_start
        if 'ts_end' in class_dict:
            res = class_dict['ts_end'](old_obj, trans_dict)
            new_obj.db_ts_end = res
        elif hasattr(old_obj, 'db_ts_end') and old_obj.db_ts_end is not None:
            new_obj.db_ts_end = old_obj.db_ts_end
        if 'cached' in class_dict:
            res = class_dict['cached'](old_obj, trans_dict)
            new_obj.db_cached = res
        elif hasattr(old_obj, 'db_cached') and old_obj.db_cached is not None:
            new_obj.db_cached = old_obj.db_cached
        if 'module_id' in class_dict:
            res = class_dict['module_id'](old_obj, trans_dict)
            new_obj.db_module_id = res
        elif hasattr(old_obj, 'db_module_id') and old_obj.db_module_id is not None:
            new_obj.db_module_id = old_obj.db_module_id
        if 'group_name' in class_dict:
            res = class_dict['group_name'](old_obj, trans_dict)
            new_obj.db_group_name = res
        elif hasattr(old_obj, 'db_group_name') and old_obj.db_group_name is not None:
            new_obj.db_group_name = old_obj.db_group_name
        if 'group_type' in class_dict:
            res = class_dict['group_type'](old_obj, trans_dict)
            new_obj.db_group_type = res
        elif hasattr(old_obj, 'db_group_type') and old_obj.db_group_type is not None:
            new_obj.db_group_type = old_obj.db_group_type
        if 'completed' in class_dict:
            res = class_dict['completed'](old_obj, trans_dict)
            new_obj.db_completed = res
        elif hasattr(old_obj, 'db_completed') and old_obj.db_completed is not None:
            new_obj.db_completed = old_obj.db_completed
        if 'error' in class_dict:
            res = class_dict['error'](old_obj, trans_dict)
            new_obj.db_error = res
        elif hasattr(old_obj, 'db_error') and old_obj.db_error is not None:
            new_obj.db_error = old_obj.db_error
        if 'machine_id' in class_dict:
            res = class_dict['machine_id'](old_obj, trans_dict)
            new_obj.db_machine_id = res
        elif hasattr(old_obj, 'db_machine_id') and old_obj.db_machine_id is not None:
            new_obj.db_machine_id = old_obj.db_machine_id
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
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        children = []
        to_del = []
        for child in self.db_annotations:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_annotation(child)
        to_del = []
        for child in self.db_item_execs:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_item_exec(child)
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_annotations)
        children.extend(self.db_deleted_item_execs)
        if remove:
            self.db_deleted_annotations = []
            self.db_deleted_item_execs = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        for child in self._db_annotations:
            if child.has_changes():
                return True
        for child in self._db_item_execs:
            if child.has_changes():
                return True
        return False
    def __get_db_item_execs(self):
        return self._db_item_execs
    def __set_db_item_execs(self, item_execs):
        self._db_item_execs = item_execs
        self.is_dirty = True
    db_item_execs = property(__get_db_item_execs, __set_db_item_execs)
    def db_get_item_execs(self):
        return self._db_item_execs
    def db_add_item_exec(self, item_exec):
        self.is_dirty = True
        self._db_item_execs.append(item_exec)
        self.db_item_execs_id_index[item_exec.db_id] = item_exec
    def db_change_item_exec(self, item_exec):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_item_execs)):
            if self._db_item_execs[i].db_id == item_exec.db_id:
                self._db_item_execs[i] = item_exec
                found = True
                break
        if not found:
            self._db_item_execs.append(item_exec)
        self.db_item_execs_id_index[item_exec.db_id] = item_exec
    def db_delete_item_exec(self, item_exec):
        self.is_dirty = True
        for i in xrange(len(self._db_item_execs)):
            if self._db_item_execs[i].db_id == item_exec.db_id:
                if not self._db_item_execs[i].is_new:
                    self.db_deleted_item_execs.append(self._db_item_execs[i])
                del self._db_item_execs[i]
                break
        del self.db_item_execs_id_index[item_exec.db_id]
    def db_get_item_exec(self, key):
        for i in xrange(len(self._db_item_execs)):
            if self._db_item_execs[i].db_id == key:
                return self._db_item_execs[i]
        return None
    def db_get_item_exec_by_id(self, key):
        return self.db_item_execs_id_index[key]
    def db_has_item_exec_with_id(self, key):
        return key in self.db_item_execs_id_index
    
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
    
    def __get_db_ts_start(self):
        return self._db_ts_start
    def __set_db_ts_start(self, ts_start):
        self._db_ts_start = ts_start
        self.is_dirty = True
    db_ts_start = property(__get_db_ts_start, __set_db_ts_start)
    def db_add_ts_start(self, ts_start):
        self._db_ts_start = ts_start
    def db_change_ts_start(self, ts_start):
        self._db_ts_start = ts_start
    def db_delete_ts_start(self, ts_start):
        self._db_ts_start = None
    
    def __get_db_ts_end(self):
        return self._db_ts_end
    def __set_db_ts_end(self, ts_end):
        self._db_ts_end = ts_end
        self.is_dirty = True
    db_ts_end = property(__get_db_ts_end, __set_db_ts_end)
    def db_add_ts_end(self, ts_end):
        self._db_ts_end = ts_end
    def db_change_ts_end(self, ts_end):
        self._db_ts_end = ts_end
    def db_delete_ts_end(self, ts_end):
        self._db_ts_end = None
    
    def __get_db_cached(self):
        return self._db_cached
    def __set_db_cached(self, cached):
        self._db_cached = cached
        self.is_dirty = True
    db_cached = property(__get_db_cached, __set_db_cached)
    def db_add_cached(self, cached):
        self._db_cached = cached
    def db_change_cached(self, cached):
        self._db_cached = cached
    def db_delete_cached(self, cached):
        self._db_cached = None
    
    def __get_db_module_id(self):
        return self._db_module_id
    def __set_db_module_id(self, module_id):
        self._db_module_id = module_id
        self.is_dirty = True
    db_module_id = property(__get_db_module_id, __set_db_module_id)
    def db_add_module_id(self, module_id):
        self._db_module_id = module_id
    def db_change_module_id(self, module_id):
        self._db_module_id = module_id
    def db_delete_module_id(self, module_id):
        self._db_module_id = None
    
    def __get_db_group_name(self):
        return self._db_group_name
    def __set_db_group_name(self, group_name):
        self._db_group_name = group_name
        self.is_dirty = True
    db_group_name = property(__get_db_group_name, __set_db_group_name)
    def db_add_group_name(self, group_name):
        self._db_group_name = group_name
    def db_change_group_name(self, group_name):
        self._db_group_name = group_name
    def db_delete_group_name(self, group_name):
        self._db_group_name = None
    
    def __get_db_group_type(self):
        return self._db_group_type
    def __set_db_group_type(self, group_type):
        self._db_group_type = group_type
        self.is_dirty = True
    db_group_type = property(__get_db_group_type, __set_db_group_type)
    def db_add_group_type(self, group_type):
        self._db_group_type = group_type
    def db_change_group_type(self, group_type):
        self._db_group_type = group_type
    def db_delete_group_type(self, group_type):
        self._db_group_type = None
    
    def __get_db_completed(self):
        return self._db_completed
    def __set_db_completed(self, completed):
        self._db_completed = completed
        self.is_dirty = True
    db_completed = property(__get_db_completed, __set_db_completed)
    def db_add_completed(self, completed):
        self._db_completed = completed
    def db_change_completed(self, completed):
        self._db_completed = completed
    def db_delete_completed(self, completed):
        self._db_completed = None
    
    def __get_db_error(self):
        return self._db_error
    def __set_db_error(self, error):
        self._db_error = error
        self.is_dirty = True
    db_error = property(__get_db_error, __set_db_error)
    def db_add_error(self, error):
        self._db_error = error
    def db_change_error(self, error):
        self._db_error = error
    def db_delete_error(self, error):
        self._db_error = None
    
    def __get_db_machine_id(self):
        return self._db_machine_id
    def __set_db_machine_id(self, machine_id):
        self._db_machine_id = machine_id
        self.is_dirty = True
    db_machine_id = property(__get_db_machine_id, __set_db_machine_id)
    def db_add_machine_id(self, machine_id):
        self._db_machine_id = machine_id
    def db_change_machine_id(self, machine_id):
        self._db_machine_id = machine_id
    def db_delete_machine_id(self, machine_id):
        self._db_machine_id = None
    
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
    def db_delete_annotation(self, annotation):
        self.is_dirty = True
        for i in xrange(len(self._db_annotations)):
            if self._db_annotations[i].db_id == annotation.db_id:
                if not self._db_annotations[i].is_new:
                    self.db_deleted_annotations.append(self._db_annotations[i])
                del self._db_annotations[i]
                break
        del self.db_annotations_id_index[annotation.db_id]
    def db_get_annotation(self, key):
        for i in xrange(len(self._db_annotations)):
            if self._db_annotations[i].db_id == key:
                return self._db_annotations[i]
        return None
    def db_get_annotation_by_id(self, key):
        return self.db_annotations_id_index[key]
    def db_has_annotation_with_id(self, key):
        return key in self.db_annotations_id_index
    
    def getPrimaryKey(self):
        return self._db_id

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

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
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
    


class DBParameter(object):

    vtType = 'parameter'

    def __init__(self, id=None, pos=None, name=None, type=None, val=None, alias=None):
        self._db_id = id
        self._db_pos = pos
        self._db_name = name
        self._db_type = type
        self._db_val = val
        self._db_alias = alias
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBParameter.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBParameter(id=self._db_id,
                         pos=self._db_pos,
                         name=self._db_name,
                         type=self._db_type,
                         val=self._db_val,
                         alias=self._db_alias)
        
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
            new_obj = DBParameter()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'pos' in class_dict:
            res = class_dict['pos'](old_obj, trans_dict)
            new_obj.db_pos = res
        elif hasattr(old_obj, 'db_pos') and old_obj.db_pos is not None:
            new_obj.db_pos = old_obj.db_pos
        if 'name' in class_dict:
            res = class_dict['name'](old_obj, trans_dict)
            new_obj.db_name = res
        elif hasattr(old_obj, 'db_name') and old_obj.db_name is not None:
            new_obj.db_name = old_obj.db_name
        if 'type' in class_dict:
            res = class_dict['type'](old_obj, trans_dict)
            new_obj.db_type = res
        elif hasattr(old_obj, 'db_type') and old_obj.db_type is not None:
            new_obj.db_type = old_obj.db_type
        if 'val' in class_dict:
            res = class_dict['val'](old_obj, trans_dict)
            new_obj.db_val = res
        elif hasattr(old_obj, 'db_val') and old_obj.db_val is not None:
            new_obj.db_val = old_obj.db_val
        if 'alias' in class_dict:
            res = class_dict['alias'](old_obj, trans_dict)
            new_obj.db_alias = res
        elif hasattr(old_obj, 'db_alias') and old_obj.db_alias is not None:
            new_obj.db_alias = old_obj.db_alias
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
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
    
    def __get_db_pos(self):
        return self._db_pos
    def __set_db_pos(self, pos):
        self._db_pos = pos
        self.is_dirty = True
    db_pos = property(__get_db_pos, __set_db_pos)
    def db_add_pos(self, pos):
        self._db_pos = pos
    def db_change_pos(self, pos):
        self._db_pos = pos
    def db_delete_pos(self, pos):
        self._db_pos = None
    
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
    
    def __get_db_type(self):
        return self._db_type
    def __set_db_type(self, type):
        self._db_type = type
        self.is_dirty = True
    db_type = property(__get_db_type, __set_db_type)
    def db_add_type(self, type):
        self._db_type = type
    def db_change_type(self, type):
        self._db_type = type
    def db_delete_type(self, type):
        self._db_type = None
    
    def __get_db_val(self):
        return self._db_val
    def __set_db_val(self, val):
        self._db_val = val
        self.is_dirty = True
    db_val = property(__get_db_val, __set_db_val)
    def db_add_val(self, val):
        self._db_val = val
    def db_change_val(self, val):
        self._db_val = val
    def db_delete_val(self, val):
        self._db_val = None
    
    def __get_db_alias(self):
        return self._db_alias
    def __set_db_alias(self, alias):
        self._db_alias = alias
        self.is_dirty = True
    db_alias = property(__get_db_alias, __set_db_alias)
    def db_add_alias(self, alias):
        self._db_alias = alias
    def db_change_alias(self, alias):
        self._db_alias = alias
    def db_delete_alias(self, alias):
        self._db_alias = None
    
    def getPrimaryKey(self):
        return self._db_id

class DBVistrail(object):

    vtType = 'vistrail'

    def __init__(self, id=None, entity_type=None, version=None, name=None, last_modified=None, actions=None, tags=None, annotations=None, controlParameters=None, vistrailVariables=None, parameter_explorations=None, actionAnnotations=None):
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
        self.db_deleted_controlParameters = []
        self.db_controlParameters_id_index = {}
        self.db_controlParameters_name_index = {}
        if controlParameters is None:
            self._db_controlParameters = []
        else:
            self._db_controlParameters = controlParameters
            for v in self._db_controlParameters:
                self.db_controlParameters_id_index[v.db_id] = v
                self.db_controlParameters_name_index[v.db_name] = v
        self.db_deleted_vistrailVariables = []
        self.db_vistrailVariables_name_index = {}
        self.db_vistrailVariables_uuid_index = {}
        if vistrailVariables is None:
            self._db_vistrailVariables = []
        else:
            self._db_vistrailVariables = vistrailVariables
            for v in self._db_vistrailVariables:
                self.db_vistrailVariables_name_index[v.db_name] = v
                self.db_vistrailVariables_uuid_index[v.db_uuid] = v
        self.db_deleted_parameter_explorations = []
        self.db_parameter_explorations_id_index = {}
        if parameter_explorations is None:
            self._db_parameter_explorations = []
        else:
            self._db_parameter_explorations = parameter_explorations
            for v in self._db_parameter_explorations:
                self.db_parameter_explorations_id_index[v.db_id] = v
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
        if self._db_controlParameters is None:
            cp._db_controlParameters = []
        else:
            cp._db_controlParameters = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_controlParameters]
        if self._db_vistrailVariables is None:
            cp._db_vistrailVariables = []
        else:
            cp._db_vistrailVariables = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_vistrailVariables]
        if self._db_parameter_explorations is None:
            cp._db_parameter_explorations = []
        else:
            cp._db_parameter_explorations = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_parameter_explorations]
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
        cp.db_controlParameters_id_index = dict((v.db_id, v) for v in cp._db_controlParameters)
        cp.db_controlParameters_name_index = dict((v.db_name, v) for v in cp._db_controlParameters)
        cp.db_vistrailVariables_name_index = dict((v.db_name, v) for v in cp._db_vistrailVariables)
        cp.db_vistrailVariables_uuid_index = dict((v.db_uuid, v) for v in cp._db_vistrailVariables)
        cp.db_parameter_explorations_id_index = dict((v.db_id, v) for v in cp._db_parameter_explorations)
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
        if 'controlParameters' in class_dict:
            res = class_dict['controlParameters'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_controlParameter(obj)
        elif hasattr(old_obj, 'db_controlParameters') and old_obj.db_controlParameters is not None:
            for obj in old_obj.db_controlParameters:
                new_obj.db_add_controlParameter(DBControlParameter.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_controlParameters') and hasattr(new_obj, 'db_deleted_controlParameters'):
            for obj in old_obj.db_deleted_controlParameters:
                n_obj = DBControlParameter.update_version(obj, trans_dict)
                new_obj.db_deleted_controlParameters.append(n_obj)
        if 'vistrailVariables' in class_dict:
            res = class_dict['vistrailVariables'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_vistrailVariable(obj)
        elif hasattr(old_obj, 'db_vistrailVariables') and old_obj.db_vistrailVariables is not None:
            for obj in old_obj.db_vistrailVariables:
                new_obj.db_add_vistrailVariable(DBVistrailVariable.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_vistrailVariables') and hasattr(new_obj, 'db_deleted_vistrailVariables'):
            for obj in old_obj.db_deleted_vistrailVariables:
                n_obj = DBVistrailVariable.update_version(obj, trans_dict)
                new_obj.db_deleted_vistrailVariables.append(n_obj)
        if 'parameter_explorations' in class_dict:
            res = class_dict['parameter_explorations'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_parameter_exploration(obj)
        elif hasattr(old_obj, 'db_parameter_explorations') and old_obj.db_parameter_explorations is not None:
            for obj in old_obj.db_parameter_explorations:
                new_obj.db_add_parameter_exploration(DBParameterExploration.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_parameter_explorations') and hasattr(new_obj, 'db_deleted_parameter_explorations'):
            for obj in old_obj.db_deleted_parameter_explorations:
                n_obj = DBParameterExploration.update_version(obj, trans_dict)
                new_obj.db_deleted_parameter_explorations.append(n_obj)
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

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        children = []
        to_del = []
        for child in self.db_actions:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_action(child)
        to_del = []
        for child in self.db_tags:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_tag(child)
        to_del = []
        for child in self.db_annotations:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_annotation(child)
        to_del = []
        for child in self.db_controlParameters:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_controlParameter(child)
        to_del = []
        for child in self.db_vistrailVariables:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_vistrailVariable(child)
        to_del = []
        for child in self.db_parameter_explorations:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_parameter_exploration(child)
        to_del = []
        for child in self.db_actionAnnotations:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
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
        children.extend(self.db_deleted_controlParameters)
        children.extend(self.db_deleted_vistrailVariables)
        children.extend(self.db_deleted_parameter_explorations)
        children.extend(self.db_deleted_actionAnnotations)
        if remove:
            self.db_deleted_actions = []
            self.db_deleted_tags = []
            self.db_deleted_annotations = []
            self.db_deleted_controlParameters = []
            self.db_deleted_vistrailVariables = []
            self.db_deleted_parameter_explorations = []
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
        for child in self._db_controlParameters:
            if child.has_changes():
                return True
        for child in self._db_vistrailVariables:
            if child.has_changes():
                return True
        for child in self._db_parameter_explorations:
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
    
    def __get_db_controlParameters(self):
        return self._db_controlParameters
    def __set_db_controlParameters(self, controlParameters):
        self._db_controlParameters = controlParameters
        self.is_dirty = True
    db_controlParameters = property(__get_db_controlParameters, __set_db_controlParameters)
    def db_get_controlParameters(self):
        return self._db_controlParameters
    def db_add_controlParameter(self, controlParameter):
        self.is_dirty = True
        self._db_controlParameters.append(controlParameter)
        self.db_controlParameters_id_index[controlParameter.db_id] = controlParameter
        self.db_controlParameters_name_index[controlParameter.db_name] = controlParameter
    def db_change_controlParameter(self, controlParameter):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_controlParameters)):
            if self._db_controlParameters[i].db_id == controlParameter.db_id:
                self._db_controlParameters[i] = controlParameter
                found = True
                break
        if not found:
            self._db_controlParameters.append(controlParameter)
        self.db_controlParameters_id_index[controlParameter.db_id] = controlParameter
        self.db_controlParameters_name_index[controlParameter.db_name] = controlParameter
    def db_delete_controlParameter(self, controlParameter):
        self.is_dirty = True
        for i in xrange(len(self._db_controlParameters)):
            if self._db_controlParameters[i].db_id == controlParameter.db_id:
                if not self._db_controlParameters[i].is_new:
                    self.db_deleted_controlParameters.append(self._db_controlParameters[i])
                del self._db_controlParameters[i]
                break
        del self.db_controlParameters_id_index[controlParameter.db_id]
        del self.db_controlParameters_name_index[controlParameter.db_name]
    def db_get_controlParameter(self, key):
        for i in xrange(len(self._db_controlParameters)):
            if self._db_controlParameters[i].db_id == key:
                return self._db_controlParameters[i]
        return None
    def db_get_controlParameter_by_id(self, key):
        return self.db_controlParameters_id_index[key]
    def db_has_controlParameter_with_id(self, key):
        return key in self.db_controlParameters_id_index
    def db_get_controlParameter_by_name(self, key):
        return self.db_controlParameters_name_index[key]
    def db_has_controlParameter_with_name(self, key):
        return key in self.db_controlParameters_name_index
    
    def __get_db_vistrailVariables(self):
        return self._db_vistrailVariables
    def __set_db_vistrailVariables(self, vistrailVariables):
        self._db_vistrailVariables = vistrailVariables
        self.is_dirty = True
    db_vistrailVariables = property(__get_db_vistrailVariables, __set_db_vistrailVariables)
    def db_get_vistrailVariables(self):
        return self._db_vistrailVariables
    def db_add_vistrailVariable(self, vistrailVariable):
        self.is_dirty = True
        self._db_vistrailVariables.append(vistrailVariable)
        self.db_vistrailVariables_name_index[vistrailVariable.db_name] = vistrailVariable
        self.db_vistrailVariables_uuid_index[vistrailVariable.db_uuid] = vistrailVariable
    def db_change_vistrailVariable(self, vistrailVariable):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_vistrailVariables)):
            if self._db_vistrailVariables[i].db_name == vistrailVariable.db_name:
                self._db_vistrailVariables[i] = vistrailVariable
                found = True
                break
        if not found:
            self._db_vistrailVariables.append(vistrailVariable)
        self.db_vistrailVariables_name_index[vistrailVariable.db_name] = vistrailVariable
        self.db_vistrailVariables_uuid_index[vistrailVariable.db_uuid] = vistrailVariable
    def db_delete_vistrailVariable(self, vistrailVariable):
        self.is_dirty = True
        for i in xrange(len(self._db_vistrailVariables)):
            if self._db_vistrailVariables[i].db_name == vistrailVariable.db_name:
                if not self._db_vistrailVariables[i].is_new:
                    self.db_deleted_vistrailVariables.append(self._db_vistrailVariables[i])
                del self._db_vistrailVariables[i]
                break
        del self.db_vistrailVariables_name_index[vistrailVariable.db_name]
        del self.db_vistrailVariables_uuid_index[vistrailVariable.db_uuid]
    def db_get_vistrailVariable(self, key):
        for i in xrange(len(self._db_vistrailVariables)):
            if self._db_vistrailVariables[i].db_name == key:
                return self._db_vistrailVariables[i]
        return None
    def db_get_vistrailVariable_by_name(self, key):
        return self.db_vistrailVariables_name_index[key]
    def db_has_vistrailVariable_with_name(self, key):
        return key in self.db_vistrailVariables_name_index
    def db_get_vistrailVariable_by_uuid(self, key):
        return self.db_vistrailVariables_uuid_index[key]
    def db_has_vistrailVariable_with_uuid(self, key):
        return key in self.db_vistrailVariables_uuid_index
    
    def __get_db_parameter_explorations(self):
        return self._db_parameter_explorations
    def __set_db_parameter_explorations(self, parameter_explorations):
        self._db_parameter_explorations = parameter_explorations
        self.is_dirty = True
    db_parameter_explorations = property(__get_db_parameter_explorations, __set_db_parameter_explorations)
    def db_get_parameter_explorations(self):
        return self._db_parameter_explorations
    def db_add_parameter_exploration(self, parameter_exploration):
        self.is_dirty = True
        self._db_parameter_explorations.append(parameter_exploration)
        self.db_parameter_explorations_id_index[parameter_exploration.db_id] = parameter_exploration
    def db_change_parameter_exploration(self, parameter_exploration):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_parameter_explorations)):
            if self._db_parameter_explorations[i].db_id == parameter_exploration.db_id:
                self._db_parameter_explorations[i] = parameter_exploration
                found = True
                break
        if not found:
            self._db_parameter_explorations.append(parameter_exploration)
        self.db_parameter_explorations_id_index[parameter_exploration.db_id] = parameter_exploration
    def db_delete_parameter_exploration(self, parameter_exploration):
        self.is_dirty = True
        for i in xrange(len(self._db_parameter_explorations)):
            if self._db_parameter_explorations[i].db_id == parameter_exploration.db_id:
                if not self._db_parameter_explorations[i].is_new:
                    self.db_deleted_parameter_explorations.append(self._db_parameter_explorations[i])
                del self._db_parameter_explorations[i]
                break
        del self.db_parameter_explorations_id_index[parameter_exploration.db_id]
    def db_get_parameter_exploration(self, key):
        for i in xrange(len(self._db_parameter_explorations)):
            if self._db_parameter_explorations[i].db_id == key:
                return self._db_parameter_explorations[i]
        return None
    def db_get_parameter_exploration_by_id(self, key):
        return self.db_parameter_explorations_id_index[key]
    def db_has_parameter_exploration_with_id(self, key):
        return key in self.db_parameter_explorations_id_index
    
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

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        children = []
        if self._db_value is not None:
            children.extend(self._db_value.db_children((self.vtType, self.db_id), orphan, for_action))
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
    


class DBConfigStr(object):

    vtType = 'config_str'

    def __init__(self, value=None):
        self._db_value = value
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBConfigStr.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBConfigStr(value=self._db_value)
        
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
            new_obj = DBConfigStr()
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

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
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
    


class DBStartup(object):

    vtType = 'startup'

    def __init__(self, version=None, configuration=None, enabled_packages=None, disabled_packages=None):
        self._db_version = version
        self.db_deleted_configuration = []
        self._db_configuration = configuration
        self.db_deleted_enabled_packages = []
        self._db_enabled_packages = enabled_packages
        self.db_deleted_disabled_packages = []
        self._db_disabled_packages = disabled_packages
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBStartup.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBStartup(version=self._db_version)
        if self._db_configuration is not None:
            cp._db_configuration = self._db_configuration.do_copy(new_ids, id_scope, id_remap)
        if self._db_enabled_packages is not None:
            cp._db_enabled_packages = self._db_enabled_packages.do_copy(new_ids, id_scope, id_remap)
        if self._db_disabled_packages is not None:
            cp._db_disabled_packages = self._db_disabled_packages.do_copy(new_ids, id_scope, id_remap)
        
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
            new_obj = DBStartup()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'version' in class_dict:
            res = class_dict['version'](old_obj, trans_dict)
            new_obj.db_version = res
        elif hasattr(old_obj, 'db_version') and old_obj.db_version is not None:
            new_obj.db_version = old_obj.db_version
        if 'configuration' in class_dict:
            res = class_dict['configuration'](old_obj, trans_dict)
            new_obj.db_configuration = res
        elif hasattr(old_obj, 'db_configuration') and old_obj.db_configuration is not None:
            obj = old_obj.db_configuration
            new_obj.db_add_configuration(DBConfiguration.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_configuration') and hasattr(new_obj, 'db_deleted_configuration'):
            for obj in old_obj.db_deleted_configuration:
                n_obj = DBConfiguration.update_version(obj, trans_dict)
                new_obj.db_deleted_configuration.append(n_obj)
        if 'enabled_packages' in class_dict:
            res = class_dict['enabled_packages'](old_obj, trans_dict)
            new_obj.db_enabled_packages = res
        elif hasattr(old_obj, 'db_enabled_packages') and old_obj.db_enabled_packages is not None:
            obj = old_obj.db_enabled_packages
            new_obj.db_add_enabled_packages(DBEnabledPackages.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_enabled_packages') and hasattr(new_obj, 'db_deleted_enabled_packages'):
            for obj in old_obj.db_deleted_enabled_packages:
                n_obj = DBEnabledPackages.update_version(obj, trans_dict)
                new_obj.db_deleted_enabled_packages.append(n_obj)
        if 'disabled_packages' in class_dict:
            res = class_dict['disabled_packages'](old_obj, trans_dict)
            new_obj.db_disabled_packages = res
        elif hasattr(old_obj, 'db_disabled_packages') and old_obj.db_disabled_packages is not None:
            obj = old_obj.db_disabled_packages
            new_obj.db_add_disabled_packages(DBDisabledPackages.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_disabled_packages') and hasattr(new_obj, 'db_deleted_disabled_packages'):
            for obj in old_obj.db_deleted_disabled_packages:
                n_obj = DBDisabledPackages.update_version(obj, trans_dict)
                new_obj.db_deleted_disabled_packages.append(n_obj)
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        children = []
        if self._db_configuration is not None:
            children.extend(self._db_configuration.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                self._db_configuration = None
        if self._db_enabled_packages is not None:
            children.extend(self._db_enabled_packages.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                self._db_enabled_packages = None
        if self._db_disabled_packages is not None:
            children.extend(self._db_disabled_packages.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                self._db_disabled_packages = None
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_configuration)
        children.extend(self.db_deleted_enabled_packages)
        children.extend(self.db_deleted_disabled_packages)
        if remove:
            self.db_deleted_configuration = []
            self.db_deleted_enabled_packages = []
            self.db_deleted_disabled_packages = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        if self._db_configuration is not None and self._db_configuration.has_changes():
            return True
        if self._db_enabled_packages is not None and self._db_enabled_packages.has_changes():
            return True
        if self._db_disabled_packages is not None and self._db_disabled_packages.has_changes():
            return True
        return False
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
    
    def __get_db_configuration(self):
        return self._db_configuration
    def __set_db_configuration(self, configuration):
        self._db_configuration = configuration
        self.is_dirty = True
    db_configuration = property(__get_db_configuration, __set_db_configuration)
    def db_add_configuration(self, configuration):
        self._db_configuration = configuration
    def db_change_configuration(self, configuration):
        self._db_configuration = configuration
    def db_delete_configuration(self, configuration):
        if not self.is_new:
            self.db_deleted_configuration.append(self._db_configuration)
        self._db_configuration = None
    
    def __get_db_enabled_packages(self):
        return self._db_enabled_packages
    def __set_db_enabled_packages(self, enabled_packages):
        self._db_enabled_packages = enabled_packages
        self.is_dirty = True
    db_enabled_packages = property(__get_db_enabled_packages, __set_db_enabled_packages)
    def db_add_enabled_packages(self, enabled_packages):
        self._db_enabled_packages = enabled_packages
    def db_change_enabled_packages(self, enabled_packages):
        self._db_enabled_packages = enabled_packages
    def db_delete_enabled_packages(self, enabled_packages):
        if not self.is_new:
            self.db_deleted_enabled_packages.append(self._db_enabled_packages)
        self._db_enabled_packages = None
    
    def __get_db_disabled_packages(self):
        return self._db_disabled_packages
    def __set_db_disabled_packages(self, disabled_packages):
        self._db_disabled_packages = disabled_packages
        self.is_dirty = True
    db_disabled_packages = property(__get_db_disabled_packages, __set_db_disabled_packages)
    def db_add_disabled_packages(self, disabled_packages):
        self._db_disabled_packages = disabled_packages
    def db_change_disabled_packages(self, disabled_packages):
        self._db_disabled_packages = disabled_packages
    def db_delete_disabled_packages(self, disabled_packages):
        if not self.is_new:
            self.db_deleted_disabled_packages.append(self._db_disabled_packages)
        self._db_disabled_packages = None
    


class DBModule(object):

    vtType = 'module'

    def __init__(self, id=None, cache=None, name=None, namespace=None, package=None, version=None, location=None, functions=None, annotations=None, controlParameters=None, portSpecs=None):
        self._db_id = id
        self._db_cache = cache
        self._db_name = name
        self._db_namespace = namespace
        self._db_package = package
        self._db_version = version
        self.db_deleted_location = []
        self._db_location = location
        self.db_deleted_functions = []
        self.db_functions_id_index = {}
        if functions is None:
            self._db_functions = []
        else:
            self._db_functions = functions
            for v in self._db_functions:
                self.db_functions_id_index[v.db_id] = v
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
        self.db_deleted_controlParameters = []
        self.db_controlParameters_id_index = {}
        self.db_controlParameters_name_index = {}
        if controlParameters is None:
            self._db_controlParameters = []
        else:
            self._db_controlParameters = controlParameters
            for v in self._db_controlParameters:
                self.db_controlParameters_id_index[v.db_id] = v
                self.db_controlParameters_name_index[v.db_name] = v
        self.db_deleted_portSpecs = []
        self.db_portSpecs_id_index = {}
        self.db_portSpecs_name_index = {}
        if portSpecs is None:
            self._db_portSpecs = []
        else:
            self._db_portSpecs = portSpecs
            for v in self._db_portSpecs:
                self.db_portSpecs_id_index[v.db_id] = v
                self.db_portSpecs_name_index[(v.db_name,v.db_type)] = v
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBModule.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBModule(id=self._db_id,
                      cache=self._db_cache,
                      name=self._db_name,
                      namespace=self._db_namespace,
                      package=self._db_package,
                      version=self._db_version)
        if self._db_location is not None:
            cp._db_location = self._db_location.do_copy(new_ids, id_scope, id_remap)
        if self._db_functions is None:
            cp._db_functions = []
        else:
            cp._db_functions = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_functions]
        if self._db_annotations is None:
            cp._db_annotations = []
        else:
            cp._db_annotations = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_annotations]
        if self._db_controlParameters is None:
            cp._db_controlParameters = []
        else:
            cp._db_controlParameters = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_controlParameters]
        if self._db_portSpecs is None:
            cp._db_portSpecs = []
        else:
            cp._db_portSpecs = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_portSpecs]
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
        
        # recreate indices and set flags
        cp.db_functions_id_index = dict((v.db_id, v) for v in cp._db_functions)
        cp.db_annotations_id_index = dict((v.db_id, v) for v in cp._db_annotations)
        cp.db_annotations_key_index = dict((v.db_key, v) for v in cp._db_annotations)
        cp.db_controlParameters_id_index = dict((v.db_id, v) for v in cp._db_controlParameters)
        cp.db_controlParameters_name_index = dict((v.db_name, v) for v in cp._db_controlParameters)
        cp.db_portSpecs_id_index = dict((v.db_id, v) for v in cp._db_portSpecs)
        cp.db_portSpecs_name_index = dict(((v.db_name,v.db_type), v) for v in cp._db_portSpecs)
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBModule()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'cache' in class_dict:
            res = class_dict['cache'](old_obj, trans_dict)
            new_obj.db_cache = res
        elif hasattr(old_obj, 'db_cache') and old_obj.db_cache is not None:
            new_obj.db_cache = old_obj.db_cache
        if 'name' in class_dict:
            res = class_dict['name'](old_obj, trans_dict)
            new_obj.db_name = res
        elif hasattr(old_obj, 'db_name') and old_obj.db_name is not None:
            new_obj.db_name = old_obj.db_name
        if 'namespace' in class_dict:
            res = class_dict['namespace'](old_obj, trans_dict)
            new_obj.db_namespace = res
        elif hasattr(old_obj, 'db_namespace') and old_obj.db_namespace is not None:
            new_obj.db_namespace = old_obj.db_namespace
        if 'package' in class_dict:
            res = class_dict['package'](old_obj, trans_dict)
            new_obj.db_package = res
        elif hasattr(old_obj, 'db_package') and old_obj.db_package is not None:
            new_obj.db_package = old_obj.db_package
        if 'version' in class_dict:
            res = class_dict['version'](old_obj, trans_dict)
            new_obj.db_version = res
        elif hasattr(old_obj, 'db_version') and old_obj.db_version is not None:
            new_obj.db_version = old_obj.db_version
        if 'location' in class_dict:
            res = class_dict['location'](old_obj, trans_dict)
            new_obj.db_location = res
        elif hasattr(old_obj, 'db_location') and old_obj.db_location is not None:
            obj = old_obj.db_location
            new_obj.db_add_location(DBLocation.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_location') and hasattr(new_obj, 'db_deleted_location'):
            for obj in old_obj.db_deleted_location:
                n_obj = DBLocation.update_version(obj, trans_dict)
                new_obj.db_deleted_location.append(n_obj)
        if 'functions' in class_dict:
            res = class_dict['functions'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_function(obj)
        elif hasattr(old_obj, 'db_functions') and old_obj.db_functions is not None:
            for obj in old_obj.db_functions:
                new_obj.db_add_function(DBFunction.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_functions') and hasattr(new_obj, 'db_deleted_functions'):
            for obj in old_obj.db_deleted_functions:
                n_obj = DBFunction.update_version(obj, trans_dict)
                new_obj.db_deleted_functions.append(n_obj)
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
        if 'controlParameters' in class_dict:
            res = class_dict['controlParameters'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_controlParameter(obj)
        elif hasattr(old_obj, 'db_controlParameters') and old_obj.db_controlParameters is not None:
            for obj in old_obj.db_controlParameters:
                new_obj.db_add_controlParameter(DBControlParameter.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_controlParameters') and hasattr(new_obj, 'db_deleted_controlParameters'):
            for obj in old_obj.db_deleted_controlParameters:
                n_obj = DBControlParameter.update_version(obj, trans_dict)
                new_obj.db_deleted_controlParameters.append(n_obj)
        if 'portSpecs' in class_dict:
            res = class_dict['portSpecs'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_portSpec(obj)
        elif hasattr(old_obj, 'db_portSpecs') and old_obj.db_portSpecs is not None:
            for obj in old_obj.db_portSpecs:
                new_obj.db_add_portSpec(DBPortSpec.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_portSpecs') and hasattr(new_obj, 'db_deleted_portSpecs'):
            for obj in old_obj.db_deleted_portSpecs:
                n_obj = DBPortSpec.update_version(obj, trans_dict)
                new_obj.db_deleted_portSpecs.append(n_obj)
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        children = []
        if self._db_location is not None:
            children.extend(self._db_location.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                self._db_location = None
        to_del = []
        for child in self.db_functions:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_function(child)
        to_del = []
        for child in self.db_annotations:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_annotation(child)
        to_del = []
        for child in self.db_controlParameters:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_controlParameter(child)
        to_del = []
        for child in self.db_portSpecs:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_portSpec(child)
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_location)
        children.extend(self.db_deleted_functions)
        children.extend(self.db_deleted_annotations)
        children.extend(self.db_deleted_controlParameters)
        children.extend(self.db_deleted_portSpecs)
        if remove:
            self.db_deleted_location = []
            self.db_deleted_functions = []
            self.db_deleted_annotations = []
            self.db_deleted_controlParameters = []
            self.db_deleted_portSpecs = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        if self._db_location is not None and self._db_location.has_changes():
            return True
        for child in self._db_functions:
            if child.has_changes():
                return True
        for child in self._db_annotations:
            if child.has_changes():
                return True
        for child in self._db_controlParameters:
            if child.has_changes():
                return True
        for child in self._db_portSpecs:
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
    
    def __get_db_cache(self):
        return self._db_cache
    def __set_db_cache(self, cache):
        self._db_cache = cache
        self.is_dirty = True
    db_cache = property(__get_db_cache, __set_db_cache)
    def db_add_cache(self, cache):
        self._db_cache = cache
    def db_change_cache(self, cache):
        self._db_cache = cache
    def db_delete_cache(self, cache):
        self._db_cache = None
    
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
    
    def __get_db_namespace(self):
        return self._db_namespace
    def __set_db_namespace(self, namespace):
        self._db_namespace = namespace
        self.is_dirty = True
    db_namespace = property(__get_db_namespace, __set_db_namespace)
    def db_add_namespace(self, namespace):
        self._db_namespace = namespace
    def db_change_namespace(self, namespace):
        self._db_namespace = namespace
    def db_delete_namespace(self, namespace):
        self._db_namespace = None
    
    def __get_db_package(self):
        return self._db_package
    def __set_db_package(self, package):
        self._db_package = package
        self.is_dirty = True
    db_package = property(__get_db_package, __set_db_package)
    def db_add_package(self, package):
        self._db_package = package
    def db_change_package(self, package):
        self._db_package = package
    def db_delete_package(self, package):
        self._db_package = None
    
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
    
    def __get_db_location(self):
        return self._db_location
    def __set_db_location(self, location):
        self._db_location = location
        self.is_dirty = True
    db_location = property(__get_db_location, __set_db_location)
    def db_add_location(self, location):
        self._db_location = location
    def db_change_location(self, location):
        self._db_location = location
    def db_delete_location(self, location):
        if not self.is_new:
            self.db_deleted_location.append(self._db_location)
        self._db_location = None
    
    def __get_db_functions(self):
        return self._db_functions
    def __set_db_functions(self, functions):
        self._db_functions = functions
        self.is_dirty = True
    db_functions = property(__get_db_functions, __set_db_functions)
    def db_get_functions(self):
        return self._db_functions
    def db_add_function(self, function):
        self.is_dirty = True
        self._db_functions.append(function)
        self.db_functions_id_index[function.db_id] = function
    def db_change_function(self, function):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_functions)):
            if self._db_functions[i].db_id == function.db_id:
                self._db_functions[i] = function
                found = True
                break
        if not found:
            self._db_functions.append(function)
        self.db_functions_id_index[function.db_id] = function
    def db_delete_function(self, function):
        self.is_dirty = True
        for i in xrange(len(self._db_functions)):
            if self._db_functions[i].db_id == function.db_id:
                if not self._db_functions[i].is_new:
                    self.db_deleted_functions.append(self._db_functions[i])
                del self._db_functions[i]
                break
        del self.db_functions_id_index[function.db_id]
    def db_get_function(self, key):
        for i in xrange(len(self._db_functions)):
            if self._db_functions[i].db_id == key:
                return self._db_functions[i]
        return None
    def db_get_function_by_id(self, key):
        return self.db_functions_id_index[key]
    def db_has_function_with_id(self, key):
        return key in self.db_functions_id_index
    
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
    
    def __get_db_controlParameters(self):
        return self._db_controlParameters
    def __set_db_controlParameters(self, controlParameters):
        self._db_controlParameters = controlParameters
        self.is_dirty = True
    db_controlParameters = property(__get_db_controlParameters, __set_db_controlParameters)
    def db_get_controlParameters(self):
        return self._db_controlParameters
    def db_add_controlParameter(self, controlParameter):
        self.is_dirty = True
        self._db_controlParameters.append(controlParameter)
        self.db_controlParameters_id_index[controlParameter.db_id] = controlParameter
        self.db_controlParameters_name_index[controlParameter.db_name] = controlParameter
    def db_change_controlParameter(self, controlParameter):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_controlParameters)):
            if self._db_controlParameters[i].db_id == controlParameter.db_id:
                self._db_controlParameters[i] = controlParameter
                found = True
                break
        if not found:
            self._db_controlParameters.append(controlParameter)
        self.db_controlParameters_id_index[controlParameter.db_id] = controlParameter
        self.db_controlParameters_name_index[controlParameter.db_name] = controlParameter
    def db_delete_controlParameter(self, controlParameter):
        self.is_dirty = True
        for i in xrange(len(self._db_controlParameters)):
            if self._db_controlParameters[i].db_id == controlParameter.db_id:
                if not self._db_controlParameters[i].is_new:
                    self.db_deleted_controlParameters.append(self._db_controlParameters[i])
                del self._db_controlParameters[i]
                break
        del self.db_controlParameters_id_index[controlParameter.db_id]
        del self.db_controlParameters_name_index[controlParameter.db_name]
    def db_get_controlParameter(self, key):
        for i in xrange(len(self._db_controlParameters)):
            if self._db_controlParameters[i].db_id == key:
                return self._db_controlParameters[i]
        return None
    def db_get_controlParameter_by_id(self, key):
        return self.db_controlParameters_id_index[key]
    def db_has_controlParameter_with_id(self, key):
        return key in self.db_controlParameters_id_index
    def db_get_controlParameter_by_name(self, key):
        return self.db_controlParameters_name_index[key]
    def db_has_controlParameter_with_name(self, key):
        return key in self.db_controlParameters_name_index
    
    def __get_db_portSpecs(self):
        return self._db_portSpecs
    def __set_db_portSpecs(self, portSpecs):
        self._db_portSpecs = portSpecs
        self.is_dirty = True
    db_portSpecs = property(__get_db_portSpecs, __set_db_portSpecs)
    def db_get_portSpecs(self):
        return self._db_portSpecs
    def db_add_portSpec(self, portSpec):
        self.is_dirty = True
        self._db_portSpecs.append(portSpec)
        self.db_portSpecs_id_index[portSpec.db_id] = portSpec
        self.db_portSpecs_name_index[(portSpec.db_name,portSpec.db_type)] = portSpec
    def db_change_portSpec(self, portSpec):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_portSpecs)):
            if self._db_portSpecs[i].db_id == portSpec.db_id:
                self._db_portSpecs[i] = portSpec
                found = True
                break
        if not found:
            self._db_portSpecs.append(portSpec)
        self.db_portSpecs_id_index[portSpec.db_id] = portSpec
        self.db_portSpecs_name_index[(portSpec.db_name,portSpec.db_type)] = portSpec
    def db_delete_portSpec(self, portSpec):
        self.is_dirty = True
        for i in xrange(len(self._db_portSpecs)):
            if self._db_portSpecs[i].db_id == portSpec.db_id:
                if not self._db_portSpecs[i].is_new:
                    self.db_deleted_portSpecs.append(self._db_portSpecs[i])
                del self._db_portSpecs[i]
                break
        del self.db_portSpecs_id_index[portSpec.db_id]
        del self.db_portSpecs_name_index[(portSpec.db_name,portSpec.db_type)]
    def db_get_portSpec(self, key):
        for i in xrange(len(self._db_portSpecs)):
            if self._db_portSpecs[i].db_id == key:
                return self._db_portSpecs[i]
        return None
    def db_get_portSpec_by_id(self, key):
        return self.db_portSpecs_id_index[key]
    def db_has_portSpec_with_id(self, key):
        return key in self.db_portSpecs_id_index
    def db_get_portSpec_by_name(self, key):
        return self.db_portSpecs_name_index[key]
    def db_has_portSpec_with_name(self, key):
        return key in self.db_portSpecs_name_index
    
    def getPrimaryKey(self):
        return self._db_id

class DBPort(object):

    vtType = 'port'

    def __init__(self, id=None, type=None, moduleId=None, moduleName=None, name=None, signature=None):
        self._db_id = id
        self._db_type = type
        self._db_moduleId = moduleId
        self._db_moduleName = moduleName
        self._db_name = name
        self._db_signature = signature
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBPort.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBPort(id=self._db_id,
                    type=self._db_type,
                    moduleId=self._db_moduleId,
                    moduleName=self._db_moduleName,
                    name=self._db_name,
                    signature=self._db_signature)
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
            if hasattr(self, 'db_moduleId') and ('module', self._db_moduleId) in id_remap:
                cp._db_moduleId = id_remap[('module', self._db_moduleId)]
        
        # recreate indices and set flags
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBPort()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'type' in class_dict:
            res = class_dict['type'](old_obj, trans_dict)
            new_obj.db_type = res
        elif hasattr(old_obj, 'db_type') and old_obj.db_type is not None:
            new_obj.db_type = old_obj.db_type
        if 'moduleId' in class_dict:
            res = class_dict['moduleId'](old_obj, trans_dict)
            new_obj.db_moduleId = res
        elif hasattr(old_obj, 'db_moduleId') and old_obj.db_moduleId is not None:
            new_obj.db_moduleId = old_obj.db_moduleId
        if 'moduleName' in class_dict:
            res = class_dict['moduleName'](old_obj, trans_dict)
            new_obj.db_moduleName = res
        elif hasattr(old_obj, 'db_moduleName') and old_obj.db_moduleName is not None:
            new_obj.db_moduleName = old_obj.db_moduleName
        if 'name' in class_dict:
            res = class_dict['name'](old_obj, trans_dict)
            new_obj.db_name = res
        elif hasattr(old_obj, 'db_name') and old_obj.db_name is not None:
            new_obj.db_name = old_obj.db_name
        if 'signature' in class_dict:
            res = class_dict['signature'](old_obj, trans_dict)
            new_obj.db_signature = res
        elif hasattr(old_obj, 'db_signature') and old_obj.db_signature is not None:
            new_obj.db_signature = old_obj.db_signature
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
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
    
    def __get_db_type(self):
        return self._db_type
    def __set_db_type(self, type):
        self._db_type = type
        self.is_dirty = True
    db_type = property(__get_db_type, __set_db_type)
    def db_add_type(self, type):
        self._db_type = type
    def db_change_type(self, type):
        self._db_type = type
    def db_delete_type(self, type):
        self._db_type = None
    
    def __get_db_moduleId(self):
        return self._db_moduleId
    def __set_db_moduleId(self, moduleId):
        self._db_moduleId = moduleId
        self.is_dirty = True
    db_moduleId = property(__get_db_moduleId, __set_db_moduleId)
    def db_add_moduleId(self, moduleId):
        self._db_moduleId = moduleId
    def db_change_moduleId(self, moduleId):
        self._db_moduleId = moduleId
    def db_delete_moduleId(self, moduleId):
        self._db_moduleId = None
    
    def __get_db_moduleName(self):
        return self._db_moduleName
    def __set_db_moduleName(self, moduleName):
        self._db_moduleName = moduleName
        self.is_dirty = True
    db_moduleName = property(__get_db_moduleName, __set_db_moduleName)
    def db_add_moduleName(self, moduleName):
        self._db_moduleName = moduleName
    def db_change_moduleName(self, moduleName):
        self._db_moduleName = moduleName
    def db_delete_moduleName(self, moduleName):
        self._db_moduleName = None
    
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
    
    def __get_db_signature(self):
        return self._db_signature
    def __set_db_signature(self, signature):
        self._db_signature = signature
        self.is_dirty = True
    db_signature = property(__get_db_signature, __set_db_signature)
    def db_add_signature(self, signature):
        self._db_signature = signature
    def db_change_signature(self, signature):
        self._db_signature = signature
    def db_delete_signature(self, signature):
        self._db_signature = None
    
    def getPrimaryKey(self):
        return self._db_id

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

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        children = []
        to_del = []
        for child in self.db_agents:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
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

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        children = []
        to_del = []
        for child in self.db_dependencys:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
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
    


class DBPEFunction(object):

    vtType = 'pe_function'

    def __init__(self, id=None, module_id=None, port_name=None, is_alias=None, parameters=None):
        self._db_id = id
        self._db_module_id = module_id
        self._db_port_name = port_name
        self._db_is_alias = is_alias
        self.db_deleted_parameters = []
        self.db_parameters_id_index = {}
        if parameters is None:
            self._db_parameters = []
        else:
            self._db_parameters = parameters
            for v in self._db_parameters:
                self.db_parameters_id_index[v.db_id] = v
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBPEFunction.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBPEFunction(id=self._db_id,
                          module_id=self._db_module_id,
                          port_name=self._db_port_name,
                          is_alias=self._db_is_alias)
        if self._db_parameters is None:
            cp._db_parameters = []
        else:
            cp._db_parameters = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_parameters]
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
            if hasattr(self, 'db_module_id') and ('module', self._db_module_id) in id_remap:
                cp._db_module_id = id_remap[('module', self._db_module_id)]
        
        # recreate indices and set flags
        cp.db_parameters_id_index = dict((v.db_id, v) for v in cp._db_parameters)
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBPEFunction()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'module_id' in class_dict:
            res = class_dict['module_id'](old_obj, trans_dict)
            new_obj.db_module_id = res
        elif hasattr(old_obj, 'db_module_id') and old_obj.db_module_id is not None:
            new_obj.db_module_id = old_obj.db_module_id
        if 'port_name' in class_dict:
            res = class_dict['port_name'](old_obj, trans_dict)
            new_obj.db_port_name = res
        elif hasattr(old_obj, 'db_port_name') and old_obj.db_port_name is not None:
            new_obj.db_port_name = old_obj.db_port_name
        if 'is_alias' in class_dict:
            res = class_dict['is_alias'](old_obj, trans_dict)
            new_obj.db_is_alias = res
        elif hasattr(old_obj, 'db_is_alias') and old_obj.db_is_alias is not None:
            new_obj.db_is_alias = old_obj.db_is_alias
        if 'parameters' in class_dict:
            res = class_dict['parameters'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_parameter(obj)
        elif hasattr(old_obj, 'db_parameters') and old_obj.db_parameters is not None:
            for obj in old_obj.db_parameters:
                new_obj.db_add_parameter(DBPEParameter.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_parameters') and hasattr(new_obj, 'db_deleted_parameters'):
            for obj in old_obj.db_deleted_parameters:
                n_obj = DBPEParameter.update_version(obj, trans_dict)
                new_obj.db_deleted_parameters.append(n_obj)
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        children = []
        to_del = []
        for child in self.db_parameters:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_parameter(child)
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_parameters)
        if remove:
            self.db_deleted_parameters = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        for child in self._db_parameters:
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
    
    def __get_db_module_id(self):
        return self._db_module_id
    def __set_db_module_id(self, module_id):
        self._db_module_id = module_id
        self.is_dirty = True
    db_module_id = property(__get_db_module_id, __set_db_module_id)
    def db_add_module_id(self, module_id):
        self._db_module_id = module_id
    def db_change_module_id(self, module_id):
        self._db_module_id = module_id
    def db_delete_module_id(self, module_id):
        self._db_module_id = None
    
    def __get_db_port_name(self):
        return self._db_port_name
    def __set_db_port_name(self, port_name):
        self._db_port_name = port_name
        self.is_dirty = True
    db_port_name = property(__get_db_port_name, __set_db_port_name)
    def db_add_port_name(self, port_name):
        self._db_port_name = port_name
    def db_change_port_name(self, port_name):
        self._db_port_name = port_name
    def db_delete_port_name(self, port_name):
        self._db_port_name = None
    
    def __get_db_is_alias(self):
        return self._db_is_alias
    def __set_db_is_alias(self, is_alias):
        self._db_is_alias = is_alias
        self.is_dirty = True
    db_is_alias = property(__get_db_is_alias, __set_db_is_alias)
    def db_add_is_alias(self, is_alias):
        self._db_is_alias = is_alias
    def db_change_is_alias(self, is_alias):
        self._db_is_alias = is_alias
    def db_delete_is_alias(self, is_alias):
        self._db_is_alias = None
    
    def __get_db_parameters(self):
        return self._db_parameters
    def __set_db_parameters(self, parameters):
        self._db_parameters = parameters
        self.is_dirty = True
    db_parameters = property(__get_db_parameters, __set_db_parameters)
    def db_get_parameters(self):
        return self._db_parameters
    def db_add_parameter(self, parameter):
        self.is_dirty = True
        self._db_parameters.append(parameter)
        self.db_parameters_id_index[parameter.db_id] = parameter
    def db_change_parameter(self, parameter):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_parameters)):
            if self._db_parameters[i].db_id == parameter.db_id:
                self._db_parameters[i] = parameter
                found = True
                break
        if not found:
            self._db_parameters.append(parameter)
        self.db_parameters_id_index[parameter.db_id] = parameter
    def db_delete_parameter(self, parameter):
        self.is_dirty = True
        for i in xrange(len(self._db_parameters)):
            if self._db_parameters[i].db_id == parameter.db_id:
                if not self._db_parameters[i].is_new:
                    self.db_deleted_parameters.append(self._db_parameters[i])
                del self._db_parameters[i]
                break
        del self.db_parameters_id_index[parameter.db_id]
    def db_get_parameter(self, key):
        for i in xrange(len(self._db_parameters)):
            if self._db_parameters[i].db_id == key:
                return self._db_parameters[i]
        return None
    def db_get_parameter_by_id(self, key):
        return self.db_parameters_id_index[key]
    def db_has_parameter_with_id(self, key):
        return key in self.db_parameters_id_index
    
    def getPrimaryKey(self):
        return self._db_id

class DBWorkflow(object):

    vtType = 'workflow'

    def __init__(self, modules=None, id=None, entity_type=None, name=None, version=None, last_modified=None, connections=None, annotations=None, plugin_datas=None, others=None, vistrail_id=None):
        self.db_deleted_modules = []
        self.db_modules_id_index = {}
        if modules is None:
            self._db_modules = []
        else:
            self._db_modules = modules
            for v in self._db_modules:
                self.db_modules_id_index[v.db_id] = v
        self._db_id = id
        self._db_entity_type = entity_type
        self._db_name = name
        self._db_version = version
        self._db_last_modified = last_modified
        self.db_deleted_connections = []
        self.db_connections_id_index = {}
        if connections is None:
            self._db_connections = []
        else:
            self._db_connections = connections
            for v in self._db_connections:
                self.db_connections_id_index[v.db_id] = v
        self.db_deleted_annotations = []
        self.db_annotations_id_index = {}
        if annotations is None:
            self._db_annotations = []
        else:
            self._db_annotations = annotations
            for v in self._db_annotations:
                self.db_annotations_id_index[v.db_id] = v
        self.db_deleted_plugin_datas = []
        self.db_plugin_datas_id_index = {}
        if plugin_datas is None:
            self._db_plugin_datas = []
        else:
            self._db_plugin_datas = plugin_datas
            for v in self._db_plugin_datas:
                self.db_plugin_datas_id_index[v.db_id] = v
        self.db_deleted_others = []
        self.db_others_id_index = {}
        if others is None:
            self._db_others = []
        else:
            self._db_others = others
            for v in self._db_others:
                self.db_others_id_index[v.db_id] = v
        self._db_vistrail_id = vistrail_id
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBWorkflow.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBWorkflow(id=self._db_id,
                        entity_type=self._db_entity_type,
                        name=self._db_name,
                        version=self._db_version,
                        last_modified=self._db_last_modified,
                        vistrail_id=self._db_vistrail_id)
        if self._db_modules is None:
            cp._db_modules = []
        else:
            cp._db_modules = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_modules]
        if self._db_connections is None:
            cp._db_connections = []
        else:
            cp._db_connections = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_connections]
        if self._db_annotations is None:
            cp._db_annotations = []
        else:
            cp._db_annotations = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_annotations]
        if self._db_plugin_datas is None:
            cp._db_plugin_datas = []
        else:
            cp._db_plugin_datas = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_plugin_datas]
        if self._db_others is None:
            cp._db_others = []
        else:
            cp._db_others = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_others]
        
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
        cp.db_modules_id_index = dict((v.db_id, v) for v in cp._db_modules)
        cp.db_connections_id_index = dict((v.db_id, v) for v in cp._db_connections)
        cp.db_annotations_id_index = dict((v.db_id, v) for v in cp._db_annotations)
        cp.db_plugin_datas_id_index = dict((v.db_id, v) for v in cp._db_plugin_datas)
        cp.db_others_id_index = dict((v.db_id, v) for v in cp._db_others)
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBWorkflow()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'modules' in class_dict:
            res = class_dict['modules'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_module(obj)
        elif hasattr(old_obj, 'db_modules') and old_obj.db_modules is not None:
            for obj in old_obj.db_modules:
                if obj.vtType == 'module':
                    new_obj.db_add_module(DBModule.update_version(obj, trans_dict))
                elif obj.vtType == 'abstraction':
                    new_obj.db_add_module(DBAbstraction.update_version(obj, trans_dict))
                elif obj.vtType == 'group':
                    new_obj.db_add_module(DBGroup.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_modules') and hasattr(new_obj, 'db_deleted_modules'):
            for obj in old_obj.db_deleted_modules:
                if obj.vtType == 'module':
                    n_obj = DBModule.update_version(obj, trans_dict)
                    new_obj.db_deleted_modules.append(n_obj)
                elif obj.vtType == 'abstraction':
                    n_obj = DBAbstraction.update_version(obj, trans_dict)
                    new_obj.db_deleted_modules.append(n_obj)
                elif obj.vtType == 'group':
                    n_obj = DBGroup.update_version(obj, trans_dict)
                    new_obj.db_deleted_modules.append(n_obj)
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
        if 'name' in class_dict:
            res = class_dict['name'](old_obj, trans_dict)
            new_obj.db_name = res
        elif hasattr(old_obj, 'db_name') and old_obj.db_name is not None:
            new_obj.db_name = old_obj.db_name
        if 'version' in class_dict:
            res = class_dict['version'](old_obj, trans_dict)
            new_obj.db_version = res
        elif hasattr(old_obj, 'db_version') and old_obj.db_version is not None:
            new_obj.db_version = old_obj.db_version
        if 'last_modified' in class_dict:
            res = class_dict['last_modified'](old_obj, trans_dict)
            new_obj.db_last_modified = res
        elif hasattr(old_obj, 'db_last_modified') and old_obj.db_last_modified is not None:
            new_obj.db_last_modified = old_obj.db_last_modified
        if 'connections' in class_dict:
            res = class_dict['connections'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_connection(obj)
        elif hasattr(old_obj, 'db_connections') and old_obj.db_connections is not None:
            for obj in old_obj.db_connections:
                new_obj.db_add_connection(DBConnection.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_connections') and hasattr(new_obj, 'db_deleted_connections'):
            for obj in old_obj.db_deleted_connections:
                n_obj = DBConnection.update_version(obj, trans_dict)
                new_obj.db_deleted_connections.append(n_obj)
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
        if 'plugin_datas' in class_dict:
            res = class_dict['plugin_datas'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_plugin_data(obj)
        elif hasattr(old_obj, 'db_plugin_datas') and old_obj.db_plugin_datas is not None:
            for obj in old_obj.db_plugin_datas:
                new_obj.db_add_plugin_data(DBPluginData.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_plugin_datas') and hasattr(new_obj, 'db_deleted_plugin_datas'):
            for obj in old_obj.db_deleted_plugin_datas:
                n_obj = DBPluginData.update_version(obj, trans_dict)
                new_obj.db_deleted_plugin_datas.append(n_obj)
        if 'others' in class_dict:
            res = class_dict['others'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_other(obj)
        elif hasattr(old_obj, 'db_others') and old_obj.db_others is not None:
            for obj in old_obj.db_others:
                new_obj.db_add_other(DBOther.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_others') and hasattr(new_obj, 'db_deleted_others'):
            for obj in old_obj.db_deleted_others:
                n_obj = DBOther.update_version(obj, trans_dict)
                new_obj.db_deleted_others.append(n_obj)
        if 'vistrail_id' in class_dict:
            res = class_dict['vistrail_id'](old_obj, trans_dict)
            new_obj.db_vistrail_id = res
        elif hasattr(old_obj, 'db_vistrail_id') and old_obj.db_vistrail_id is not None:
            new_obj.db_vistrail_id = old_obj.db_vistrail_id
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        children = []
        to_del = []
        for child in self.db_connections:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_connection(child)
        to_del = []
        for child in self.db_annotations:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_annotation(child)
        to_del = []
        for child in self.db_plugin_datas:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_plugin_data(child)
        to_del = []
        for child in self.db_others:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_other(child)
        to_del = []
        for child in self.db_modules:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_module(child)
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_connections)
        children.extend(self.db_deleted_annotations)
        children.extend(self.db_deleted_plugin_datas)
        children.extend(self.db_deleted_others)
        children.extend(self.db_deleted_modules)
        if remove:
            self.db_deleted_connections = []
            self.db_deleted_annotations = []
            self.db_deleted_plugin_datas = []
            self.db_deleted_others = []
            self.db_deleted_modules = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        for child in self._db_connections:
            if child.has_changes():
                return True
        for child in self._db_annotations:
            if child.has_changes():
                return True
        for child in self._db_plugin_datas:
            if child.has_changes():
                return True
        for child in self._db_others:
            if child.has_changes():
                return True
        for child in self._db_modules:
            if child.has_changes():
                return True
        return False
    def __get_db_modules(self):
        return self._db_modules
    def __set_db_modules(self, modules):
        self._db_modules = modules
        self.is_dirty = True
    db_modules = property(__get_db_modules, __set_db_modules)
    def db_get_modules(self):
        return self._db_modules
    def db_add_module(self, module):
        self.is_dirty = True
        self._db_modules.append(module)
        self.db_modules_id_index[module.db_id] = module
    def db_change_module(self, module):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_modules)):
            if self._db_modules[i].db_id == module.db_id:
                self._db_modules[i] = module
                found = True
                break
        if not found:
            self._db_modules.append(module)
        self.db_modules_id_index[module.db_id] = module
    def db_delete_module(self, module):
        self.is_dirty = True
        for i in xrange(len(self._db_modules)):
            if self._db_modules[i].db_id == module.db_id:
                if not self._db_modules[i].is_new:
                    self.db_deleted_modules.append(self._db_modules[i])
                del self._db_modules[i]
                break
        del self.db_modules_id_index[module.db_id]
    def db_get_module(self, key):
        for i in xrange(len(self._db_modules)):
            if self._db_modules[i].db_id == key:
                return self._db_modules[i]
        return None
    def db_get_module_by_id(self, key):
        return self.db_modules_id_index[key]
    def db_has_module_with_id(self, key):
        return key in self.db_modules_id_index
    
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
    
    def __get_db_connections(self):
        return self._db_connections
    def __set_db_connections(self, connections):
        self._db_connections = connections
        self.is_dirty = True
    db_connections = property(__get_db_connections, __set_db_connections)
    def db_get_connections(self):
        return self._db_connections
    def db_add_connection(self, connection):
        self.is_dirty = True
        self._db_connections.append(connection)
        self.db_connections_id_index[connection.db_id] = connection
    def db_change_connection(self, connection):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_connections)):
            if self._db_connections[i].db_id == connection.db_id:
                self._db_connections[i] = connection
                found = True
                break
        if not found:
            self._db_connections.append(connection)
        self.db_connections_id_index[connection.db_id] = connection
    def db_delete_connection(self, connection):
        self.is_dirty = True
        for i in xrange(len(self._db_connections)):
            if self._db_connections[i].db_id == connection.db_id:
                if not self._db_connections[i].is_new:
                    self.db_deleted_connections.append(self._db_connections[i])
                del self._db_connections[i]
                break
        del self.db_connections_id_index[connection.db_id]
    def db_get_connection(self, key):
        for i in xrange(len(self._db_connections)):
            if self._db_connections[i].db_id == key:
                return self._db_connections[i]
        return None
    def db_get_connection_by_id(self, key):
        return self.db_connections_id_index[key]
    def db_has_connection_with_id(self, key):
        return key in self.db_connections_id_index
    
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
    def db_delete_annotation(self, annotation):
        self.is_dirty = True
        for i in xrange(len(self._db_annotations)):
            if self._db_annotations[i].db_id == annotation.db_id:
                if not self._db_annotations[i].is_new:
                    self.db_deleted_annotations.append(self._db_annotations[i])
                del self._db_annotations[i]
                break
        del self.db_annotations_id_index[annotation.db_id]
    def db_get_annotation(self, key):
        for i in xrange(len(self._db_annotations)):
            if self._db_annotations[i].db_id == key:
                return self._db_annotations[i]
        return None
    def db_get_annotation_by_id(self, key):
        return self.db_annotations_id_index[key]
    def db_has_annotation_with_id(self, key):
        return key in self.db_annotations_id_index
    
    def __get_db_plugin_datas(self):
        return self._db_plugin_datas
    def __set_db_plugin_datas(self, plugin_datas):
        self._db_plugin_datas = plugin_datas
        self.is_dirty = True
    db_plugin_datas = property(__get_db_plugin_datas, __set_db_plugin_datas)
    def db_get_plugin_datas(self):
        return self._db_plugin_datas
    def db_add_plugin_data(self, plugin_data):
        self.is_dirty = True
        self._db_plugin_datas.append(plugin_data)
        self.db_plugin_datas_id_index[plugin_data.db_id] = plugin_data
    def db_change_plugin_data(self, plugin_data):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_plugin_datas)):
            if self._db_plugin_datas[i].db_id == plugin_data.db_id:
                self._db_plugin_datas[i] = plugin_data
                found = True
                break
        if not found:
            self._db_plugin_datas.append(plugin_data)
        self.db_plugin_datas_id_index[plugin_data.db_id] = plugin_data
    def db_delete_plugin_data(self, plugin_data):
        self.is_dirty = True
        for i in xrange(len(self._db_plugin_datas)):
            if self._db_plugin_datas[i].db_id == plugin_data.db_id:
                if not self._db_plugin_datas[i].is_new:
                    self.db_deleted_plugin_datas.append(self._db_plugin_datas[i])
                del self._db_plugin_datas[i]
                break
        del self.db_plugin_datas_id_index[plugin_data.db_id]
    def db_get_plugin_data(self, key):
        for i in xrange(len(self._db_plugin_datas)):
            if self._db_plugin_datas[i].db_id == key:
                return self._db_plugin_datas[i]
        return None
    def db_get_plugin_data_by_id(self, key):
        return self.db_plugin_datas_id_index[key]
    def db_has_plugin_data_with_id(self, key):
        return key in self.db_plugin_datas_id_index
    
    def __get_db_others(self):
        return self._db_others
    def __set_db_others(self, others):
        self._db_others = others
        self.is_dirty = True
    db_others = property(__get_db_others, __set_db_others)
    def db_get_others(self):
        return self._db_others
    def db_add_other(self, other):
        self.is_dirty = True
        self._db_others.append(other)
        self.db_others_id_index[other.db_id] = other
    def db_change_other(self, other):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_others)):
            if self._db_others[i].db_id == other.db_id:
                self._db_others[i] = other
                found = True
                break
        if not found:
            self._db_others.append(other)
        self.db_others_id_index[other.db_id] = other
    def db_delete_other(self, other):
        self.is_dirty = True
        for i in xrange(len(self._db_others)):
            if self._db_others[i].db_id == other.db_id:
                if not self._db_others[i].is_new:
                    self.db_deleted_others.append(self._db_others[i])
                del self._db_others[i]
                break
        del self.db_others_id_index[other.db_id]
    def db_get_other(self, key):
        for i in xrange(len(self._db_others)):
            if self._db_others[i].db_id == key:
                return self._db_others[i]
        return None
    def db_get_other_by_id(self, key):
        return self.db_others_id_index[key]
    def db_has_other_with_id(self, key):
        return key in self.db_others_id_index
    
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

class DBMashupAction(object):

    vtType = 'mashup_action'

    def __init__(self, id=None, prevId=None, date=None, user=None, mashup=None):
        self._db_id = id
        self._db_prevId = prevId
        self._db_date = date
        self._db_user = user
        self.db_deleted_mashup = []
        self._db_mashup = mashup
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBMashupAction.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBMashupAction(id=self._db_id,
                            prevId=self._db_prevId,
                            date=self._db_date,
                            user=self._db_user)
        if self._db_mashup is not None:
            cp._db_mashup = self._db_mashup.do_copy(new_ids, id_scope, id_remap)
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
            if hasattr(self, 'db_prevId') and ('mashup_action', self._db_prevId) in id_remap:
                cp._db_prevId = id_remap[('mashup_action', self._db_prevId)]
        
        # recreate indices and set flags
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBMashupAction()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'prevId' in class_dict:
            res = class_dict['prevId'](old_obj, trans_dict)
            new_obj.db_prevId = res
        elif hasattr(old_obj, 'db_prevId') and old_obj.db_prevId is not None:
            new_obj.db_prevId = old_obj.db_prevId
        if 'date' in class_dict:
            res = class_dict['date'](old_obj, trans_dict)
            new_obj.db_date = res
        elif hasattr(old_obj, 'db_date') and old_obj.db_date is not None:
            new_obj.db_date = old_obj.db_date
        if 'user' in class_dict:
            res = class_dict['user'](old_obj, trans_dict)
            new_obj.db_user = res
        elif hasattr(old_obj, 'db_user') and old_obj.db_user is not None:
            new_obj.db_user = old_obj.db_user
        if 'mashup' in class_dict:
            res = class_dict['mashup'](old_obj, trans_dict)
            new_obj.db_mashup = res
        elif hasattr(old_obj, 'db_mashup') and old_obj.db_mashup is not None:
            obj = old_obj.db_mashup
            new_obj.db_add_mashup(DBMashup.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_mashup') and hasattr(new_obj, 'db_deleted_mashup'):
            for obj in old_obj.db_deleted_mashup:
                n_obj = DBMashup.update_version(obj, trans_dict)
                new_obj.db_deleted_mashup.append(n_obj)
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        children = []
        if self._db_mashup is not None:
            children.extend(self._db_mashup.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                self._db_mashup = None
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_mashup)
        if remove:
            self.db_deleted_mashup = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        if self._db_mashup is not None and self._db_mashup.has_changes():
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
    
    def __get_db_prevId(self):
        return self._db_prevId
    def __set_db_prevId(self, prevId):
        self._db_prevId = prevId
        self.is_dirty = True
    db_prevId = property(__get_db_prevId, __set_db_prevId)
    def db_add_prevId(self, prevId):
        self._db_prevId = prevId
    def db_change_prevId(self, prevId):
        self._db_prevId = prevId
    def db_delete_prevId(self, prevId):
        self._db_prevId = None
    
    def __get_db_date(self):
        return self._db_date
    def __set_db_date(self, date):
        self._db_date = date
        self.is_dirty = True
    db_date = property(__get_db_date, __set_db_date)
    def db_add_date(self, date):
        self._db_date = date
    def db_change_date(self, date):
        self._db_date = date
    def db_delete_date(self, date):
        self._db_date = None
    
    def __get_db_user(self):
        return self._db_user
    def __set_db_user(self, user):
        self._db_user = user
        self.is_dirty = True
    db_user = property(__get_db_user, __set_db_user)
    def db_add_user(self, user):
        self._db_user = user
    def db_change_user(self, user):
        self._db_user = user
    def db_delete_user(self, user):
        self._db_user = None
    
    def __get_db_mashup(self):
        return self._db_mashup
    def __set_db_mashup(self, mashup):
        self._db_mashup = mashup
        self.is_dirty = True
    db_mashup = property(__get_db_mashup, __set_db_mashup)
    def db_add_mashup(self, mashup):
        self._db_mashup = mashup
    def db_change_mashup(self, mashup):
        self._db_mashup = mashup
    def db_delete_mashup(self, mashup):
        if not self.is_new:
            self.db_deleted_mashup.append(self._db_mashup)
        self._db_mashup = None
    
    def getPrimaryKey(self):
        return self._db_id

class DBConfiguration(object):

    vtType = 'configuration'

    def __init__(self, config_keys=None):
        self.db_deleted_config_keys = []
        self.db_config_keys_name_index = {}
        if config_keys is None:
            self._db_config_keys = []
        else:
            self._db_config_keys = config_keys
            for v in self._db_config_keys:
                self.db_config_keys_name_index[v.db_name] = v
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBConfiguration.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBConfiguration()
        if self._db_config_keys is None:
            cp._db_config_keys = []
        else:
            cp._db_config_keys = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_config_keys]
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
        
        # recreate indices and set flags
        cp.db_config_keys_name_index = dict((v.db_name, v) for v in cp._db_config_keys)
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBConfiguration()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'config_keys' in class_dict:
            res = class_dict['config_keys'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_config_key(obj)
        elif hasattr(old_obj, 'db_config_keys') and old_obj.db_config_keys is not None:
            for obj in old_obj.db_config_keys:
                new_obj.db_add_config_key(DBConfigKey.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_config_keys') and hasattr(new_obj, 'db_deleted_config_keys'):
            for obj in old_obj.db_deleted_config_keys:
                n_obj = DBConfigKey.update_version(obj, trans_dict)
                new_obj.db_deleted_config_keys.append(n_obj)
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        children = []
        to_del = []
        for child in self.db_config_keys:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_config_key(child)
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_config_keys)
        if remove:
            self.db_deleted_config_keys = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        for child in self._db_config_keys:
            if child.has_changes():
                return True
        return False
    def __get_db_config_keys(self):
        return self._db_config_keys
    def __set_db_config_keys(self, config_keys):
        self._db_config_keys = config_keys
        self.is_dirty = True
    db_config_keys = property(__get_db_config_keys, __set_db_config_keys)
    def db_get_config_keys(self):
        return self._db_config_keys
    def db_add_config_key(self, config_key):
        self.is_dirty = True
        self._db_config_keys.append(config_key)
        self.db_config_keys_name_index[config_key.db_name] = config_key
    def db_change_config_key(self, config_key):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_config_keys)):
            if self._db_config_keys[i].db_name == config_key.db_name:
                self._db_config_keys[i] = config_key
                found = True
                break
        if not found:
            self._db_config_keys.append(config_key)
        self.db_config_keys_name_index[config_key.db_name] = config_key
    def db_delete_config_key(self, config_key):
        self.is_dirty = True
        for i in xrange(len(self._db_config_keys)):
            if self._db_config_keys[i].db_name == config_key.db_name:
                if not self._db_config_keys[i].is_new:
                    self.db_deleted_config_keys.append(self._db_config_keys[i])
                del self._db_config_keys[i]
                break
        del self.db_config_keys_name_index[config_key.db_name]
    def db_get_config_key(self, key):
        for i in xrange(len(self._db_config_keys)):
            if self._db_config_keys[i].db_name == key:
                return self._db_config_keys[i]
        return None
    def db_get_config_key_by_name(self, key):
        return self.db_config_keys_name_index[key]
    def db_has_config_key_with_name(self, key):
        return key in self.db_config_keys_name_index
    


class DBChange(object):

    vtType = 'change'

    def __init__(self, data=None, id=None, what=None, oldObjId=None, newObjId=None, parentObjId=None, parentObjType=None):
        self.db_deleted_data = []
        self._db_data = data
        self._db_id = id
        self._db_what = what
        self._db_oldObjId = oldObjId
        self._db_newObjId = newObjId
        self._db_parentObjId = parentObjId
        self._db_parentObjType = parentObjType
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBChange.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBChange(id=self._db_id,
                      what=self._db_what,
                      oldObjId=self._db_oldObjId,
                      newObjId=self._db_newObjId,
                      parentObjId=self._db_parentObjId,
                      parentObjType=self._db_parentObjType)
        if self._db_data is not None:
            cp._db_data = self._db_data.do_copy(new_ids, id_scope, id_remap)
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
            if hasattr(self, 'db_oldObjId') and (self._db_what, self._db_oldObjId) in id_remap:
                cp._db_oldObjId = id_remap[(self._db_what, self._db_oldObjId)]
            if hasattr(self, 'db_newObjId') and (self._db_what, self._db_newObjId) in id_remap:
                cp._db_newObjId = id_remap[(self._db_what, self._db_newObjId)]
            if hasattr(self, 'db_parentObjId') and (self._db_parentObjType, self._db_parentObjId) in id_remap:
                cp._db_parentObjId = id_remap[(self._db_parentObjType, self._db_parentObjId)]
        
        # recreate indices and set flags
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBChange()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'data' in class_dict:
            res = class_dict['data'](old_obj, trans_dict)
            new_obj.db_data = res
        elif hasattr(old_obj, 'db_data') and old_obj.db_data is not None:
            obj = old_obj.db_data
            if obj.vtType == 'module':
                new_obj.db_add_data(DBModule.update_version(obj, trans_dict))
            elif obj.vtType == 'location':
                new_obj.db_add_data(DBLocation.update_version(obj, trans_dict))
            elif obj.vtType == 'annotation':
                new_obj.db_add_data(DBAnnotation.update_version(obj, trans_dict))
            elif obj.vtType == 'controlParameter':
                new_obj.db_add_data(DBControlParameter.update_version(obj, trans_dict))
            elif obj.vtType == 'function':
                new_obj.db_add_data(DBFunction.update_version(obj, trans_dict))
            elif obj.vtType == 'connection':
                new_obj.db_add_data(DBConnection.update_version(obj, trans_dict))
            elif obj.vtType == 'port':
                new_obj.db_add_data(DBPort.update_version(obj, trans_dict))
            elif obj.vtType == 'parameter':
                new_obj.db_add_data(DBParameter.update_version(obj, trans_dict))
            elif obj.vtType == 'portSpec':
                new_obj.db_add_data(DBPortSpec.update_version(obj, trans_dict))
            elif obj.vtType == 'abstraction':
                new_obj.db_add_data(DBAbstraction.update_version(obj, trans_dict))
            elif obj.vtType == 'group':
                new_obj.db_add_data(DBGroup.update_version(obj, trans_dict))
            elif obj.vtType == 'other':
                new_obj.db_add_data(DBOther.update_version(obj, trans_dict))
            elif obj.vtType == 'plugin_data':
                new_obj.db_add_data(DBPluginData.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_data') and hasattr(new_obj, 'db_deleted_data'):
            for obj in old_obj.db_deleted_data:
                if obj.vtType == 'module':
                    n_obj = DBModule.update_version(obj, trans_dict)
                    new_obj.db_deleted_data.append(n_obj)
                elif obj.vtType == 'location':
                    n_obj = DBLocation.update_version(obj, trans_dict)
                    new_obj.db_deleted_data.append(n_obj)
                elif obj.vtType == 'annotation':
                    n_obj = DBAnnotation.update_version(obj, trans_dict)
                    new_obj.db_deleted_data.append(n_obj)
                elif obj.vtType == 'controlParameter':
                    n_obj = DBControlParameter.update_version(obj, trans_dict)
                    new_obj.db_deleted_data.append(n_obj)
                elif obj.vtType == 'function':
                    n_obj = DBFunction.update_version(obj, trans_dict)
                    new_obj.db_deleted_data.append(n_obj)
                elif obj.vtType == 'connection':
                    n_obj = DBConnection.update_version(obj, trans_dict)
                    new_obj.db_deleted_data.append(n_obj)
                elif obj.vtType == 'port':
                    n_obj = DBPort.update_version(obj, trans_dict)
                    new_obj.db_deleted_data.append(n_obj)
                elif obj.vtType == 'parameter':
                    n_obj = DBParameter.update_version(obj, trans_dict)
                    new_obj.db_deleted_data.append(n_obj)
                elif obj.vtType == 'portSpec':
                    n_obj = DBPortSpec.update_version(obj, trans_dict)
                    new_obj.db_deleted_data.append(n_obj)
                elif obj.vtType == 'abstraction':
                    n_obj = DBAbstraction.update_version(obj, trans_dict)
                    new_obj.db_deleted_data.append(n_obj)
                elif obj.vtType == 'group':
                    n_obj = DBGroup.update_version(obj, trans_dict)
                    new_obj.db_deleted_data.append(n_obj)
                elif obj.vtType == 'other':
                    n_obj = DBOther.update_version(obj, trans_dict)
                    new_obj.db_deleted_data.append(n_obj)
                elif obj.vtType == 'plugin_data':
                    n_obj = DBPluginData.update_version(obj, trans_dict)
                    new_obj.db_deleted_data.append(n_obj)
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'what' in class_dict:
            res = class_dict['what'](old_obj, trans_dict)
            new_obj.db_what = res
        elif hasattr(old_obj, 'db_what') and old_obj.db_what is not None:
            new_obj.db_what = old_obj.db_what
        if 'oldObjId' in class_dict:
            res = class_dict['oldObjId'](old_obj, trans_dict)
            new_obj.db_oldObjId = res
        elif hasattr(old_obj, 'db_oldObjId') and old_obj.db_oldObjId is not None:
            new_obj.db_oldObjId = old_obj.db_oldObjId
        if 'newObjId' in class_dict:
            res = class_dict['newObjId'](old_obj, trans_dict)
            new_obj.db_newObjId = res
        elif hasattr(old_obj, 'db_newObjId') and old_obj.db_newObjId is not None:
            new_obj.db_newObjId = old_obj.db_newObjId
        if 'parentObjId' in class_dict:
            res = class_dict['parentObjId'](old_obj, trans_dict)
            new_obj.db_parentObjId = res
        elif hasattr(old_obj, 'db_parentObjId') and old_obj.db_parentObjId is not None:
            new_obj.db_parentObjId = old_obj.db_parentObjId
        if 'parentObjType' in class_dict:
            res = class_dict['parentObjType'](old_obj, trans_dict)
            new_obj.db_parentObjType = res
        elif hasattr(old_obj, 'db_parentObjType') and old_obj.db_parentObjType is not None:
            new_obj.db_parentObjType = old_obj.db_parentObjType
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        children = []
        if self._db_data is not None:
            children.extend(self._db_data.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                self._db_data = None
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_data)
        if remove:
            self.db_deleted_data = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        if self._db_data is not None and self._db_data.has_changes():
            return True
        return False
    def __get_db_data(self):
        return self._db_data
    def __set_db_data(self, data):
        self._db_data = data
        self.is_dirty = True
    db_data = property(__get_db_data, __set_db_data)
    def db_add_data(self, data):
        self._db_data = data
    def db_change_data(self, data):
        self._db_data = data
    def db_delete_data(self, data):
        if not self.is_new:
            self.db_deleted_data.append(self._db_data)
        self._db_data = None
    
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
    
    def __get_db_what(self):
        return self._db_what
    def __set_db_what(self, what):
        self._db_what = what
        self.is_dirty = True
    db_what = property(__get_db_what, __set_db_what)
    def db_add_what(self, what):
        self._db_what = what
    def db_change_what(self, what):
        self._db_what = what
    def db_delete_what(self, what):
        self._db_what = None
    
    def __get_db_oldObjId(self):
        return self._db_oldObjId
    def __set_db_oldObjId(self, oldObjId):
        self._db_oldObjId = oldObjId
        self.is_dirty = True
    db_oldObjId = property(__get_db_oldObjId, __set_db_oldObjId)
    def db_add_oldObjId(self, oldObjId):
        self._db_oldObjId = oldObjId
    def db_change_oldObjId(self, oldObjId):
        self._db_oldObjId = oldObjId
    def db_delete_oldObjId(self, oldObjId):
        self._db_oldObjId = None
    
    def __get_db_newObjId(self):
        return self._db_newObjId
    def __set_db_newObjId(self, newObjId):
        self._db_newObjId = newObjId
        self.is_dirty = True
    db_newObjId = property(__get_db_newObjId, __set_db_newObjId)
    def db_add_newObjId(self, newObjId):
        self._db_newObjId = newObjId
    def db_change_newObjId(self, newObjId):
        self._db_newObjId = newObjId
    def db_delete_newObjId(self, newObjId):
        self._db_newObjId = None
    
    def __get_db_parentObjId(self):
        return self._db_parentObjId
    def __set_db_parentObjId(self, parentObjId):
        self._db_parentObjId = parentObjId
        self.is_dirty = True
    db_parentObjId = property(__get_db_parentObjId, __set_db_parentObjId)
    def db_add_parentObjId(self, parentObjId):
        self._db_parentObjId = parentObjId
    def db_change_parentObjId(self, parentObjId):
        self._db_parentObjId = parentObjId
    def db_delete_parentObjId(self, parentObjId):
        self._db_parentObjId = None
    
    def __get_db_parentObjType(self):
        return self._db_parentObjType
    def __set_db_parentObjType(self, parentObjType):
        self._db_parentObjType = parentObjType
        self.is_dirty = True
    db_parentObjType = property(__get_db_parentObjType, __set_db_parentObjType)
    def db_add_parentObjType(self, parentObjType):
        self._db_parentObjType = parentObjType
    def db_change_parentObjType(self, parentObjType):
        self._db_parentObjType = parentObjType
    def db_delete_parentObjType(self, parentObjType):
        self._db_parentObjType = None
    
    def getPrimaryKey(self):
        return self._db_id

class DBPackage(object):

    vtType = 'package'

    def __init__(self, id=None, name=None, identifier=None, codepath=None, load_configuration=None, version=None, description=None, module_descriptors=None):
        self._db_id = id
        self._db_name = name
        self._db_identifier = identifier
        self._db_codepath = codepath
        self._db_load_configuration = load_configuration
        self._db_version = version
        self._db_description = description
        self.db_deleted_module_descriptors = []
        self.db_module_descriptors_id_index = {}
        self.db_module_descriptors_name_index = {}
        if module_descriptors is None:
            self._db_module_descriptors = []
        else:
            self._db_module_descriptors = module_descriptors
            for v in self._db_module_descriptors:
                self.db_module_descriptors_id_index[v.db_id] = v
                self.db_module_descriptors_name_index[(v.db_name,v.db_namespace,v.db_version)] = v
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBPackage.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBPackage(id=self._db_id,
                       name=self._db_name,
                       identifier=self._db_identifier,
                       codepath=self._db_codepath,
                       load_configuration=self._db_load_configuration,
                       version=self._db_version,
                       description=self._db_description)
        if self._db_module_descriptors is None:
            cp._db_module_descriptors = []
        else:
            cp._db_module_descriptors = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_module_descriptors]
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
        
        # recreate indices and set flags
        cp.db_module_descriptors_id_index = dict((v.db_id, v) for v in cp._db_module_descriptors)
        cp.db_module_descriptors_name_index = dict(((v.db_name,v.db_namespace,v.db_version), v) for v in cp._db_module_descriptors)
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBPackage()
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
        if 'identifier' in class_dict:
            res = class_dict['identifier'](old_obj, trans_dict)
            new_obj.db_identifier = res
        elif hasattr(old_obj, 'db_identifier') and old_obj.db_identifier is not None:
            new_obj.db_identifier = old_obj.db_identifier
        if 'codepath' in class_dict:
            res = class_dict['codepath'](old_obj, trans_dict)
            new_obj.db_codepath = res
        elif hasattr(old_obj, 'db_codepath') and old_obj.db_codepath is not None:
            new_obj.db_codepath = old_obj.db_codepath
        if 'load_configuration' in class_dict:
            res = class_dict['load_configuration'](old_obj, trans_dict)
            new_obj.db_load_configuration = res
        elif hasattr(old_obj, 'db_load_configuration') and old_obj.db_load_configuration is not None:
            new_obj.db_load_configuration = old_obj.db_load_configuration
        if 'version' in class_dict:
            res = class_dict['version'](old_obj, trans_dict)
            new_obj.db_version = res
        elif hasattr(old_obj, 'db_version') and old_obj.db_version is not None:
            new_obj.db_version = old_obj.db_version
        if 'description' in class_dict:
            res = class_dict['description'](old_obj, trans_dict)
            new_obj.db_description = res
        elif hasattr(old_obj, 'db_description') and old_obj.db_description is not None:
            new_obj.db_description = old_obj.db_description
        if 'module_descriptors' in class_dict:
            res = class_dict['module_descriptors'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_module_descriptor(obj)
        elif hasattr(old_obj, 'db_module_descriptors') and old_obj.db_module_descriptors is not None:
            for obj in old_obj.db_module_descriptors:
                new_obj.db_add_module_descriptor(DBModuleDescriptor.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_module_descriptors') and hasattr(new_obj, 'db_deleted_module_descriptors'):
            for obj in old_obj.db_deleted_module_descriptors:
                n_obj = DBModuleDescriptor.update_version(obj, trans_dict)
                new_obj.db_deleted_module_descriptors.append(n_obj)
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        children = []
        to_del = []
        for child in self.db_module_descriptors:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_module_descriptor(child)
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_module_descriptors)
        if remove:
            self.db_deleted_module_descriptors = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        for child in self._db_module_descriptors:
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
    
    def __get_db_identifier(self):
        return self._db_identifier
    def __set_db_identifier(self, identifier):
        self._db_identifier = identifier
        self.is_dirty = True
    db_identifier = property(__get_db_identifier, __set_db_identifier)
    def db_add_identifier(self, identifier):
        self._db_identifier = identifier
    def db_change_identifier(self, identifier):
        self._db_identifier = identifier
    def db_delete_identifier(self, identifier):
        self._db_identifier = None
    
    def __get_db_codepath(self):
        return self._db_codepath
    def __set_db_codepath(self, codepath):
        self._db_codepath = codepath
        self.is_dirty = True
    db_codepath = property(__get_db_codepath, __set_db_codepath)
    def db_add_codepath(self, codepath):
        self._db_codepath = codepath
    def db_change_codepath(self, codepath):
        self._db_codepath = codepath
    def db_delete_codepath(self, codepath):
        self._db_codepath = None
    
    def __get_db_load_configuration(self):
        return self._db_load_configuration
    def __set_db_load_configuration(self, load_configuration):
        self._db_load_configuration = load_configuration
        self.is_dirty = True
    db_load_configuration = property(__get_db_load_configuration, __set_db_load_configuration)
    def db_add_load_configuration(self, load_configuration):
        self._db_load_configuration = load_configuration
    def db_change_load_configuration(self, load_configuration):
        self._db_load_configuration = load_configuration
    def db_delete_load_configuration(self, load_configuration):
        self._db_load_configuration = None
    
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
    
    def __get_db_description(self):
        return self._db_description
    def __set_db_description(self, description):
        self._db_description = description
        self.is_dirty = True
    db_description = property(__get_db_description, __set_db_description)
    def db_add_description(self, description):
        self._db_description = description
    def db_change_description(self, description):
        self._db_description = description
    def db_delete_description(self, description):
        self._db_description = None
    
    def __get_db_module_descriptors(self):
        return self._db_module_descriptors
    def __set_db_module_descriptors(self, module_descriptors):
        self._db_module_descriptors = module_descriptors
        self.is_dirty = True
    db_module_descriptors = property(__get_db_module_descriptors, __set_db_module_descriptors)
    def db_get_module_descriptors(self):
        return self._db_module_descriptors
    def db_add_module_descriptor(self, module_descriptor):
        self.is_dirty = True
        self._db_module_descriptors.append(module_descriptor)
        self.db_module_descriptors_id_index[module_descriptor.db_id] = module_descriptor
        self.db_module_descriptors_name_index[(module_descriptor.db_name,module_descriptor.db_namespace,module_descriptor.db_version)] = module_descriptor
    def db_change_module_descriptor(self, module_descriptor):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_module_descriptors)):
            if self._db_module_descriptors[i].db_id == module_descriptor.db_id:
                self._db_module_descriptors[i] = module_descriptor
                found = True
                break
        if not found:
            self._db_module_descriptors.append(module_descriptor)
        self.db_module_descriptors_id_index[module_descriptor.db_id] = module_descriptor
        self.db_module_descriptors_name_index[(module_descriptor.db_name,module_descriptor.db_namespace,module_descriptor.db_version)] = module_descriptor
    def db_delete_module_descriptor(self, module_descriptor):
        self.is_dirty = True
        for i in xrange(len(self._db_module_descriptors)):
            if self._db_module_descriptors[i].db_id == module_descriptor.db_id:
                if not self._db_module_descriptors[i].is_new:
                    self.db_deleted_module_descriptors.append(self._db_module_descriptors[i])
                del self._db_module_descriptors[i]
                break
        del self.db_module_descriptors_id_index[module_descriptor.db_id]
        del self.db_module_descriptors_name_index[(module_descriptor.db_name,module_descriptor.db_namespace,module_descriptor.db_version)]
    def db_get_module_descriptor(self, key):
        for i in xrange(len(self._db_module_descriptors)):
            if self._db_module_descriptors[i].db_id == key:
                return self._db_module_descriptors[i]
        return None
    def db_get_module_descriptor_by_id(self, key):
        return self.db_module_descriptors_id_index[key]
    def db_has_module_descriptor_with_id(self, key):
        return key in self.db_module_descriptors_id_index
    def db_get_module_descriptor_by_name(self, key):
        return self.db_module_descriptors_name_index[key]
    def db_has_module_descriptor_with_name(self, key):
        return key in self.db_module_descriptors_name_index
    
    def getPrimaryKey(self):
        return self._db_id

class DBLoopExec(object):

    vtType = 'loop_exec'

    def __init__(self, id=None, ts_start=None, ts_end=None, loop_iterations=None):
        self._db_id = id
        self._db_ts_start = ts_start
        self._db_ts_end = ts_end
        self.db_deleted_loop_iterations = []
        self.db_loop_iterations_id_index = {}
        if loop_iterations is None:
            self._db_loop_iterations = []
        else:
            self._db_loop_iterations = loop_iterations
            for v in self._db_loop_iterations:
                self.db_loop_iterations_id_index[v.db_id] = v
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBLoopExec.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBLoopExec(id=self._db_id,
                        ts_start=self._db_ts_start,
                        ts_end=self._db_ts_end)
        if self._db_loop_iterations is None:
            cp._db_loop_iterations = []
        else:
            cp._db_loop_iterations = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_loop_iterations]
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
        
        # recreate indices and set flags
        cp.db_loop_iterations_id_index = dict((v.db_id, v) for v in cp._db_loop_iterations)
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBLoopExec()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'ts_start' in class_dict:
            res = class_dict['ts_start'](old_obj, trans_dict)
            new_obj.db_ts_start = res
        elif hasattr(old_obj, 'db_ts_start') and old_obj.db_ts_start is not None:
            new_obj.db_ts_start = old_obj.db_ts_start
        if 'ts_end' in class_dict:
            res = class_dict['ts_end'](old_obj, trans_dict)
            new_obj.db_ts_end = res
        elif hasattr(old_obj, 'db_ts_end') and old_obj.db_ts_end is not None:
            new_obj.db_ts_end = old_obj.db_ts_end
        if 'loop_iterations' in class_dict:
            res = class_dict['loop_iterations'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_loop_iteration(obj)
        elif hasattr(old_obj, 'db_loop_iterations') and old_obj.db_loop_iterations is not None:
            for obj in old_obj.db_loop_iterations:
                new_obj.db_add_loop_iteration(DBLoopIteration.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_loop_iterations') and hasattr(new_obj, 'db_deleted_loop_iterations'):
            for obj in old_obj.db_deleted_loop_iterations:
                n_obj = DBLoopIteration.update_version(obj, trans_dict)
                new_obj.db_deleted_loop_iterations.append(n_obj)
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        children = []
        to_del = []
        for child in self.db_loop_iterations:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_loop_iteration(child)
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_loop_iterations)
        if remove:
            self.db_deleted_loop_iterations = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        for child in self._db_loop_iterations:
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
    
    def __get_db_ts_start(self):
        return self._db_ts_start
    def __set_db_ts_start(self, ts_start):
        self._db_ts_start = ts_start
        self.is_dirty = True
    db_ts_start = property(__get_db_ts_start, __set_db_ts_start)
    def db_add_ts_start(self, ts_start):
        self._db_ts_start = ts_start
    def db_change_ts_start(self, ts_start):
        self._db_ts_start = ts_start
    def db_delete_ts_start(self, ts_start):
        self._db_ts_start = None
    
    def __get_db_ts_end(self):
        return self._db_ts_end
    def __set_db_ts_end(self, ts_end):
        self._db_ts_end = ts_end
        self.is_dirty = True
    db_ts_end = property(__get_db_ts_end, __set_db_ts_end)
    def db_add_ts_end(self, ts_end):
        self._db_ts_end = ts_end
    def db_change_ts_end(self, ts_end):
        self._db_ts_end = ts_end
    def db_delete_ts_end(self, ts_end):
        self._db_ts_end = None
    
    def __get_db_loop_iterations(self):
        return self._db_loop_iterations
    def __set_db_loop_iterations(self, loop_iterations):
        self._db_loop_iterations = loop_iterations
        self.is_dirty = True
    db_loop_iterations = property(__get_db_loop_iterations, __set_db_loop_iterations)
    def db_get_loop_iterations(self):
        return self._db_loop_iterations
    def db_add_loop_iteration(self, loop_iteration):
        self.is_dirty = True
        self._db_loop_iterations.append(loop_iteration)
        self.db_loop_iterations_id_index[loop_iteration.db_id] = loop_iteration
    def db_change_loop_iteration(self, loop_iteration):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_loop_iterations)):
            if self._db_loop_iterations[i].db_id == loop_iteration.db_id:
                self._db_loop_iterations[i] = loop_iteration
                found = True
                break
        if not found:
            self._db_loop_iterations.append(loop_iteration)
        self.db_loop_iterations_id_index[loop_iteration.db_id] = loop_iteration
    def db_delete_loop_iteration(self, loop_iteration):
        self.is_dirty = True
        for i in xrange(len(self._db_loop_iterations)):
            if self._db_loop_iterations[i].db_id == loop_iteration.db_id:
                if not self._db_loop_iterations[i].is_new:
                    self.db_deleted_loop_iterations.append(self._db_loop_iterations[i])
                del self._db_loop_iterations[i]
                break
        del self.db_loop_iterations_id_index[loop_iteration.db_id]
    def db_get_loop_iteration(self, key):
        for i in xrange(len(self._db_loop_iterations)):
            if self._db_loop_iterations[i].db_id == key:
                return self._db_loop_iterations[i]
        return None
    def db_get_loop_iteration_by_id(self, key):
        return self.db_loop_iterations_id_index[key]
    def db_has_loop_iteration_with_id(self, key):
        return key in self.db_loop_iterations_id_index
    
    def getPrimaryKey(self):
        return self._db_id

class DBConnection(object):

    vtType = 'connection'

    def __init__(self, id=None, ports=None):
        self._db_id = id
        self.db_deleted_ports = []
        self.db_ports_id_index = {}
        self.db_ports_type_index = {}
        if ports is None:
            self._db_ports = []
        else:
            self._db_ports = ports
            for v in self._db_ports:
                self.db_ports_id_index[v.db_id] = v
                self.db_ports_type_index[v.db_type] = v
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBConnection.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBConnection(id=self._db_id)
        if self._db_ports is None:
            cp._db_ports = []
        else:
            cp._db_ports = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_ports]
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
        
        # recreate indices and set flags
        cp.db_ports_id_index = dict((v.db_id, v) for v in cp._db_ports)
        cp.db_ports_type_index = dict((v.db_type, v) for v in cp._db_ports)
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBConnection()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'ports' in class_dict:
            res = class_dict['ports'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_port(obj)
        elif hasattr(old_obj, 'db_ports') and old_obj.db_ports is not None:
            for obj in old_obj.db_ports:
                new_obj.db_add_port(DBPort.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_ports') and hasattr(new_obj, 'db_deleted_ports'):
            for obj in old_obj.db_deleted_ports:
                n_obj = DBPort.update_version(obj, trans_dict)
                new_obj.db_deleted_ports.append(n_obj)
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        children = []
        to_del = []
        for child in self.db_ports:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_port(child)
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_ports)
        if remove:
            self.db_deleted_ports = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        for child in self._db_ports:
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
    
    def __get_db_ports(self):
        return self._db_ports
    def __set_db_ports(self, ports):
        self._db_ports = ports
        self.is_dirty = True
    db_ports = property(__get_db_ports, __set_db_ports)
    def db_get_ports(self):
        return self._db_ports
    def db_add_port(self, port):
        self.is_dirty = True
        self._db_ports.append(port)
        self.db_ports_id_index[port.db_id] = port
        self.db_ports_type_index[port.db_type] = port
    def db_change_port(self, port):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_ports)):
            if self._db_ports[i].db_id == port.db_id:
                self._db_ports[i] = port
                found = True
                break
        if not found:
            self._db_ports.append(port)
        self.db_ports_id_index[port.db_id] = port
        self.db_ports_type_index[port.db_type] = port
    def db_delete_port(self, port):
        self.is_dirty = True
        for i in xrange(len(self._db_ports)):
            if self._db_ports[i].db_id == port.db_id:
                if not self._db_ports[i].is_new:
                    self.db_deleted_ports.append(self._db_ports[i])
                del self._db_ports[i]
                break
        del self.db_ports_id_index[port.db_id]
        del self.db_ports_type_index[port.db_type]
    def db_get_port(self, key):
        for i in xrange(len(self._db_ports)):
            if self._db_ports[i].db_id == key:
                return self._db_ports[i]
        return None
    def db_get_port_by_id(self, key):
        return self.db_ports_id_index[key]
    def db_has_port_with_id(self, key):
        return key in self.db_ports_id_index
    def db_get_port_by_type(self, key):
        return self.db_ports_type_index[key]
    def db_has_port_with_type(self, key):
        return key in self.db_ports_type_index
    
    def getPrimaryKey(self):
        return self._db_id

class DBConfigBool(object):

    vtType = 'config_bool'

    def __init__(self, value=None):
        self._db_value = value
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBConfigBool.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBConfigBool(value=self._db_value)
        
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
            new_obj = DBConfigBool()
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

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
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
    


class DBAction(object):

    vtType = 'action'

    def __init__(self, operations=None, id=None, prevId=None, date=None, session=None, user=None, annotations=None):
        self.db_deleted_operations = []
        self.db_operations_id_index = {}
        if operations is None:
            self._db_operations = []
        else:
            self._db_operations = operations
            for v in self._db_operations:
                self.db_operations_id_index[v.db_id] = v
        self._db_id = id
        self._db_prevId = prevId
        self._db_date = date
        self._db_session = session
        self._db_user = user
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
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBAction.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBAction(id=self._db_id,
                      prevId=self._db_prevId,
                      date=self._db_date,
                      session=self._db_session,
                      user=self._db_user)
        if self._db_operations is None:
            cp._db_operations = []
        else:
            cp._db_operations = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_operations]
        if self._db_annotations is None:
            cp._db_annotations = []
        else:
            cp._db_annotations = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_annotations]
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
            if hasattr(self, 'db_prevId') and ('action', self._db_prevId) in id_remap:
                cp._db_prevId = id_remap[('action', self._db_prevId)]
        
        # recreate indices and set flags
        cp.db_operations_id_index = dict((v.db_id, v) for v in cp._db_operations)
        cp.db_annotations_id_index = dict((v.db_id, v) for v in cp._db_annotations)
        cp.db_annotations_key_index = dict((v.db_key, v) for v in cp._db_annotations)
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBAction()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'operations' in class_dict:
            res = class_dict['operations'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_operation(obj)
        elif hasattr(old_obj, 'db_operations') and old_obj.db_operations is not None:
            for obj in old_obj.db_operations:
                if obj.vtType == 'add':
                    new_obj.db_add_operation(DBAdd.update_version(obj, trans_dict))
                elif obj.vtType == 'delete':
                    new_obj.db_add_operation(DBDelete.update_version(obj, trans_dict))
                elif obj.vtType == 'change':
                    new_obj.db_add_operation(DBChange.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_operations') and hasattr(new_obj, 'db_deleted_operations'):
            for obj in old_obj.db_deleted_operations:
                if obj.vtType == 'add':
                    n_obj = DBAdd.update_version(obj, trans_dict)
                    new_obj.db_deleted_operations.append(n_obj)
                elif obj.vtType == 'delete':
                    n_obj = DBDelete.update_version(obj, trans_dict)
                    new_obj.db_deleted_operations.append(n_obj)
                elif obj.vtType == 'change':
                    n_obj = DBChange.update_version(obj, trans_dict)
                    new_obj.db_deleted_operations.append(n_obj)
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'prevId' in class_dict:
            res = class_dict['prevId'](old_obj, trans_dict)
            new_obj.db_prevId = res
        elif hasattr(old_obj, 'db_prevId') and old_obj.db_prevId is not None:
            new_obj.db_prevId = old_obj.db_prevId
        if 'date' in class_dict:
            res = class_dict['date'](old_obj, trans_dict)
            new_obj.db_date = res
        elif hasattr(old_obj, 'db_date') and old_obj.db_date is not None:
            new_obj.db_date = old_obj.db_date
        if 'session' in class_dict:
            res = class_dict['session'](old_obj, trans_dict)
            new_obj.db_session = res
        elif hasattr(old_obj, 'db_session') and old_obj.db_session is not None:
            new_obj.db_session = old_obj.db_session
        if 'user' in class_dict:
            res = class_dict['user'](old_obj, trans_dict)
            new_obj.db_user = res
        elif hasattr(old_obj, 'db_user') and old_obj.db_user is not None:
            new_obj.db_user = old_obj.db_user
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
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        children = []
        to_del = []
        for child in self.db_annotations:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_annotation(child)
        to_del = []
        for child in self.db_operations:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_operation(child)
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_annotations)
        children.extend(self.db_deleted_operations)
        if remove:
            self.db_deleted_annotations = []
            self.db_deleted_operations = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        for child in self._db_annotations:
            if child.has_changes():
                return True
        for child in self._db_operations:
            if child.has_changes():
                return True
        return False
    def __get_db_operations(self):
        return self._db_operations
    def __set_db_operations(self, operations):
        self._db_operations = operations
        self.is_dirty = True
    db_operations = property(__get_db_operations, __set_db_operations)
    def db_get_operations(self):
        return self._db_operations
    def db_add_operation(self, operation):
        self.is_dirty = True
        self._db_operations.append(operation)
        self.db_operations_id_index[operation.db_id] = operation
    def db_change_operation(self, operation):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_operations)):
            if self._db_operations[i].db_id == operation.db_id:
                self._db_operations[i] = operation
                found = True
                break
        if not found:
            self._db_operations.append(operation)
        self.db_operations_id_index[operation.db_id] = operation
    def db_delete_operation(self, operation):
        self.is_dirty = True
        for i in xrange(len(self._db_operations)):
            if self._db_operations[i].db_id == operation.db_id:
                if not self._db_operations[i].is_new:
                    self.db_deleted_operations.append(self._db_operations[i])
                del self._db_operations[i]
                break
        del self.db_operations_id_index[operation.db_id]
    def db_get_operation(self, key):
        for i in xrange(len(self._db_operations)):
            if self._db_operations[i].db_id == key:
                return self._db_operations[i]
        return None
    def db_get_operation_by_id(self, key):
        return self.db_operations_id_index[key]
    def db_has_operation_with_id(self, key):
        return key in self.db_operations_id_index
    
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
    
    def __get_db_prevId(self):
        return self._db_prevId
    def __set_db_prevId(self, prevId):
        self._db_prevId = prevId
        self.is_dirty = True
    db_prevId = property(__get_db_prevId, __set_db_prevId)
    def db_add_prevId(self, prevId):
        self._db_prevId = prevId
    def db_change_prevId(self, prevId):
        self._db_prevId = prevId
    def db_delete_prevId(self, prevId):
        self._db_prevId = None
    
    def __get_db_date(self):
        return self._db_date
    def __set_db_date(self, date):
        self._db_date = date
        self.is_dirty = True
    db_date = property(__get_db_date, __set_db_date)
    def db_add_date(self, date):
        self._db_date = date
    def db_change_date(self, date):
        self._db_date = date
    def db_delete_date(self, date):
        self._db_date = None
    
    def __get_db_session(self):
        return self._db_session
    def __set_db_session(self, session):
        self._db_session = session
        self.is_dirty = True
    db_session = property(__get_db_session, __set_db_session)
    def db_add_session(self, session):
        self._db_session = session
    def db_change_session(self, session):
        self._db_session = session
    def db_delete_session(self, session):
        self._db_session = None
    
    def __get_db_user(self):
        return self._db_user
    def __set_db_user(self, user):
        self._db_user = user
        self.is_dirty = True
    db_user = property(__get_db_user, __set_db_user)
    def db_add_user(self, user):
        self._db_user = user
    def db_change_user(self, user):
        self._db_user = user
    def db_delete_user(self, user):
        self._db_user = None
    
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
    
    def getPrimaryKey(self):
        return self._db_id

class DBStartupPackage(object):

    vtType = 'startup_package'

    def __init__(self, name=None, configuration=None):
        self._db_name = name
        self.db_deleted_configuration = []
        self._db_configuration = configuration
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBStartupPackage.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBStartupPackage(name=self._db_name)
        if self._db_configuration is not None:
            cp._db_configuration = self._db_configuration.do_copy(new_ids, id_scope, id_remap)
        
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
            new_obj = DBStartupPackage()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'name' in class_dict:
            res = class_dict['name'](old_obj, trans_dict)
            new_obj.db_name = res
        elif hasattr(old_obj, 'db_name') and old_obj.db_name is not None:
            new_obj.db_name = old_obj.db_name
        if 'configuration' in class_dict:
            res = class_dict['configuration'](old_obj, trans_dict)
            new_obj.db_configuration = res
        elif hasattr(old_obj, 'db_configuration') and old_obj.db_configuration is not None:
            obj = old_obj.db_configuration
            new_obj.db_add_configuration(DBConfiguration.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_configuration') and hasattr(new_obj, 'db_deleted_configuration'):
            for obj in old_obj.db_deleted_configuration:
                n_obj = DBConfiguration.update_version(obj, trans_dict)
                new_obj.db_deleted_configuration.append(n_obj)
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        children = []
        if self._db_configuration is not None:
            children.extend(self._db_configuration.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                self._db_configuration = None
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_configuration)
        if remove:
            self.db_deleted_configuration = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        if self._db_configuration is not None and self._db_configuration.has_changes():
            return True
        return False
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
    
    def __get_db_configuration(self):
        return self._db_configuration
    def __set_db_configuration(self, configuration):
        self._db_configuration = configuration
        self.is_dirty = True
    db_configuration = property(__get_db_configuration, __set_db_configuration)
    def db_add_configuration(self, configuration):
        self._db_configuration = configuration
    def db_change_configuration(self, configuration):
        self._db_configuration = configuration
    def db_delete_configuration(self, configuration):
        if not self.is_new:
            self.db_deleted_configuration.append(self._db_configuration)
        self._db_configuration = None
    


class DBConfigInt(object):

    vtType = 'config_int'

    def __init__(self, value=None):
        self._db_value = value
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBConfigInt.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBConfigInt(value=self._db_value)
        
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
            new_obj = DBConfigInt()
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

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
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

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
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
    


class DBRefProvPlan(object):

    vtType = 'ref_prov_plan'

    def __init__(self, prov_ref=None):
        self._db_prov_ref = prov_ref
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBRefProvPlan.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBRefProvPlan(prov_ref=self._db_prov_ref)
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
            if hasattr(self, 'db_prov_ref') and ('prov_entity', self._db_prov_ref) in id_remap:
                cp._db_prov_ref = id_remap[('prov_entity', self._db_prov_ref)]
        
        # recreate indices and set flags
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBRefProvPlan()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'prov_ref' in class_dict:
            res = class_dict['prov_ref'](old_obj, trans_dict)
            new_obj.db_prov_ref = res
        elif hasattr(old_obj, 'db_prov_ref') and old_obj.db_prov_ref is not None:
            new_obj.db_prov_ref = old_obj.db_prov_ref
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        return [(self, parent[0], parent[1])]
    def db_deleted_children(self, remove=False):
        children = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        return False
    def __get_db_prov_ref(self):
        return self._db_prov_ref
    def __set_db_prov_ref(self, prov_ref):
        self._db_prov_ref = prov_ref
        self.is_dirty = True
    db_prov_ref = property(__get_db_prov_ref, __set_db_prov_ref)
    def db_add_prov_ref(self, prov_ref):
        self._db_prov_ref = prov_ref
    def db_change_prov_ref(self, prov_ref):
        self._db_prov_ref = prov_ref
    def db_delete_prov_ref(self, prov_ref):
        self._db_prov_ref = None
    


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

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        children = []
        to_del = []
        for child in self.db_accounts:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_account(child)
        to_del = []
        for child in self.db_opm_overlapss:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
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
    


class DBRefProvAgent(object):

    vtType = 'ref_prov_agent'

    def __init__(self, prov_ref=None):
        self._db_prov_ref = prov_ref
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBRefProvAgent.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBRefProvAgent(prov_ref=self._db_prov_ref)
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
            if hasattr(self, 'db_prov_ref') and ('prov_agent', self._db_prov_ref) in id_remap:
                cp._db_prov_ref = id_remap[('prov_agent', self._db_prov_ref)]
        
        # recreate indices and set flags
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBRefProvAgent()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'prov_ref' in class_dict:
            res = class_dict['prov_ref'](old_obj, trans_dict)
            new_obj.db_prov_ref = res
        elif hasattr(old_obj, 'db_prov_ref') and old_obj.db_prov_ref is not None:
            new_obj.db_prov_ref = old_obj.db_prov_ref
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        return [(self, parent[0], parent[1])]
    def db_deleted_children(self, remove=False):
        children = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        return False
    def __get_db_prov_ref(self):
        return self._db_prov_ref
    def __set_db_prov_ref(self, prov_ref):
        self._db_prov_ref = prov_ref
        self.is_dirty = True
    db_prov_ref = property(__get_db_prov_ref, __set_db_prov_ref)
    def db_add_prov_ref(self, prov_ref):
        self._db_prov_ref = prov_ref
    def db_change_prov_ref(self, prov_ref):
        self._db_prov_ref = prov_ref
    def db_delete_prov_ref(self, prov_ref):
        self._db_prov_ref = None
    


class DBPortSpec(object):

    vtType = 'portSpec'

    def __init__(self, id=None, name=None, type=None, optional=None, depth=None, sort_key=None, portSpecItems=None, min_conns=None, max_conns=None):
        self._db_id = id
        self._db_name = name
        self._db_type = type
        self._db_optional = optional
        self._db_depth = depth
        self._db_sort_key = sort_key
        self.db_deleted_portSpecItems = []
        self.db_portSpecItems_id_index = {}
        if portSpecItems is None:
            self._db_portSpecItems = []
        else:
            self._db_portSpecItems = portSpecItems
            for v in self._db_portSpecItems:
                self.db_portSpecItems_id_index[v.db_id] = v
        self._db_min_conns = min_conns
        self._db_max_conns = max_conns
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBPortSpec.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBPortSpec(id=self._db_id,
                        name=self._db_name,
                        type=self._db_type,
                        optional=self._db_optional,
                        depth=self._db_depth,
                        sort_key=self._db_sort_key,
                        min_conns=self._db_min_conns,
                        max_conns=self._db_max_conns)
        if self._db_portSpecItems is None:
            cp._db_portSpecItems = []
        else:
            cp._db_portSpecItems = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_portSpecItems]
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
        
        # recreate indices and set flags
        cp.db_portSpecItems_id_index = dict((v.db_id, v) for v in cp._db_portSpecItems)
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBPortSpec()
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
        if 'type' in class_dict:
            res = class_dict['type'](old_obj, trans_dict)
            new_obj.db_type = res
        elif hasattr(old_obj, 'db_type') and old_obj.db_type is not None:
            new_obj.db_type = old_obj.db_type
        if 'optional' in class_dict:
            res = class_dict['optional'](old_obj, trans_dict)
            new_obj.db_optional = res
        elif hasattr(old_obj, 'db_optional') and old_obj.db_optional is not None:
            new_obj.db_optional = old_obj.db_optional
        if 'depth' in class_dict:
            res = class_dict['depth'](old_obj, trans_dict)
            new_obj.db_depth = res
        elif hasattr(old_obj, 'db_depth') and old_obj.db_depth is not None:
            new_obj.db_depth = old_obj.db_depth
        if 'sort_key' in class_dict:
            res = class_dict['sort_key'](old_obj, trans_dict)
            new_obj.db_sort_key = res
        elif hasattr(old_obj, 'db_sort_key') and old_obj.db_sort_key is not None:
            new_obj.db_sort_key = old_obj.db_sort_key
        if 'portSpecItems' in class_dict:
            res = class_dict['portSpecItems'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_portSpecItem(obj)
        elif hasattr(old_obj, 'db_portSpecItems') and old_obj.db_portSpecItems is not None:
            for obj in old_obj.db_portSpecItems:
                new_obj.db_add_portSpecItem(DBPortSpecItem.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_portSpecItems') and hasattr(new_obj, 'db_deleted_portSpecItems'):
            for obj in old_obj.db_deleted_portSpecItems:
                n_obj = DBPortSpecItem.update_version(obj, trans_dict)
                new_obj.db_deleted_portSpecItems.append(n_obj)
        if 'min_conns' in class_dict:
            res = class_dict['min_conns'](old_obj, trans_dict)
            new_obj.db_min_conns = res
        elif hasattr(old_obj, 'db_min_conns') and old_obj.db_min_conns is not None:
            new_obj.db_min_conns = old_obj.db_min_conns
        if 'max_conns' in class_dict:
            res = class_dict['max_conns'](old_obj, trans_dict)
            new_obj.db_max_conns = res
        elif hasattr(old_obj, 'db_max_conns') and old_obj.db_max_conns is not None:
            new_obj.db_max_conns = old_obj.db_max_conns
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        children = []
        if not for_action:
            for child in self.db_portSpecItems:
                children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_portSpecItems)
        if remove:
            self.db_deleted_portSpecItems = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        for child in self._db_portSpecItems:
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
    
    def __get_db_type(self):
        return self._db_type
    def __set_db_type(self, type):
        self._db_type = type
        self.is_dirty = True
    db_type = property(__get_db_type, __set_db_type)
    def db_add_type(self, type):
        self._db_type = type
    def db_change_type(self, type):
        self._db_type = type
    def db_delete_type(self, type):
        self._db_type = None
    
    def __get_db_optional(self):
        return self._db_optional
    def __set_db_optional(self, optional):
        self._db_optional = optional
        self.is_dirty = True
    db_optional = property(__get_db_optional, __set_db_optional)
    def db_add_optional(self, optional):
        self._db_optional = optional
    def db_change_optional(self, optional):
        self._db_optional = optional
    def db_delete_optional(self, optional):
        self._db_optional = None
    
    def __get_db_depth(self):
        return self._db_depth
    def __set_db_depth(self, depth):
        self._db_depth = depth
        self.is_dirty = True
    db_depth = property(__get_db_depth, __set_db_depth)
    def db_add_depth(self, depth):
        self._db_depth = depth
    def db_change_depth(self, depth):
        self._db_depth = depth
    def db_delete_depth(self, depth):
        self._db_depth = None
    
    def __get_db_sort_key(self):
        return self._db_sort_key
    def __set_db_sort_key(self, sort_key):
        self._db_sort_key = sort_key
        self.is_dirty = True
    db_sort_key = property(__get_db_sort_key, __set_db_sort_key)
    def db_add_sort_key(self, sort_key):
        self._db_sort_key = sort_key
    def db_change_sort_key(self, sort_key):
        self._db_sort_key = sort_key
    def db_delete_sort_key(self, sort_key):
        self._db_sort_key = None
    
    def __get_db_portSpecItems(self):
        return self._db_portSpecItems
    def __set_db_portSpecItems(self, portSpecItems):
        self._db_portSpecItems = portSpecItems
        self.is_dirty = True
    db_portSpecItems = property(__get_db_portSpecItems, __set_db_portSpecItems)
    def db_get_portSpecItems(self):
        return self._db_portSpecItems
    def db_add_portSpecItem(self, portSpecItem):
        self.is_dirty = True
        self._db_portSpecItems.append(portSpecItem)
        self.db_portSpecItems_id_index[portSpecItem.db_id] = portSpecItem
    def db_change_portSpecItem(self, portSpecItem):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_portSpecItems)):
            if self._db_portSpecItems[i].db_id == portSpecItem.db_id:
                self._db_portSpecItems[i] = portSpecItem
                found = True
                break
        if not found:
            self._db_portSpecItems.append(portSpecItem)
        self.db_portSpecItems_id_index[portSpecItem.db_id] = portSpecItem
    def db_delete_portSpecItem(self, portSpecItem):
        self.is_dirty = True
        for i in xrange(len(self._db_portSpecItems)):
            if self._db_portSpecItems[i].db_id == portSpecItem.db_id:
                if not self._db_portSpecItems[i].is_new:
                    self.db_deleted_portSpecItems.append(self._db_portSpecItems[i])
                del self._db_portSpecItems[i]
                break
        del self.db_portSpecItems_id_index[portSpecItem.db_id]
    def db_get_portSpecItem(self, key):
        for i in xrange(len(self._db_portSpecItems)):
            if self._db_portSpecItems[i].db_id == key:
                return self._db_portSpecItems[i]
        return None
    def db_get_portSpecItem_by_id(self, key):
        return self.db_portSpecItems_id_index[key]
    def db_has_portSpecItem_with_id(self, key):
        return key in self.db_portSpecItems_id_index
    
    def __get_db_min_conns(self):
        return self._db_min_conns
    def __set_db_min_conns(self, min_conns):
        self._db_min_conns = min_conns
        self.is_dirty = True
    db_min_conns = property(__get_db_min_conns, __set_db_min_conns)
    def db_add_min_conns(self, min_conns):
        self._db_min_conns = min_conns
    def db_change_min_conns(self, min_conns):
        self._db_min_conns = min_conns
    def db_delete_min_conns(self, min_conns):
        self._db_min_conns = None
    
    def __get_db_max_conns(self):
        return self._db_max_conns
    def __set_db_max_conns(self, max_conns):
        self._db_max_conns = max_conns
        self.is_dirty = True
    db_max_conns = property(__get_db_max_conns, __set_db_max_conns)
    def db_add_max_conns(self, max_conns):
        self._db_max_conns = max_conns
    def db_change_max_conns(self, max_conns):
        self._db_max_conns = max_conns
    def db_delete_max_conns(self, max_conns):
        self._db_max_conns = None
    
    def getPrimaryKey(self):
        return self._db_id

class DBEnabledPackages(object):

    vtType = 'enabled_packages'

    def __init__(self, packages=None):
        self.db_deleted_packages = []
        self.db_packages_name_index = {}
        if packages is None:
            self._db_packages = []
        else:
            self._db_packages = packages
            for v in self._db_packages:
                self.db_packages_name_index[v.db_name] = v
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBEnabledPackages.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBEnabledPackages()
        if self._db_packages is None:
            cp._db_packages = []
        else:
            cp._db_packages = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_packages]
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
        
        # recreate indices and set flags
        cp.db_packages_name_index = dict((v.db_name, v) for v in cp._db_packages)
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBEnabledPackages()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'packages' in class_dict:
            res = class_dict['packages'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_package(obj)
        elif hasattr(old_obj, 'db_packages') and old_obj.db_packages is not None:
            for obj in old_obj.db_packages:
                new_obj.db_add_package(DBStartupPackage.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_packages') and hasattr(new_obj, 'db_deleted_packages'):
            for obj in old_obj.db_deleted_packages:
                n_obj = DBStartupPackage.update_version(obj, trans_dict)
                new_obj.db_deleted_packages.append(n_obj)
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        children = []
        to_del = []
        for child in self.db_packages:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_package(child)
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_packages)
        if remove:
            self.db_deleted_packages = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        for child in self._db_packages:
            if child.has_changes():
                return True
        return False
    def __get_db_packages(self):
        return self._db_packages
    def __set_db_packages(self, packages):
        self._db_packages = packages
        self.is_dirty = True
    db_packages = property(__get_db_packages, __set_db_packages)
    def db_get_packages(self):
        return self._db_packages
    def db_add_package(self, package):
        self.is_dirty = True
        self._db_packages.append(package)
        self.db_packages_name_index[package.db_name] = package
    def db_change_package(self, package):
        self.is_dirty = True
        self._db_packages.append(package)
        self.db_packages_name_index[package.db_name] = package
    def db_delete_package(self, package):
        self.is_dirty = True
        raise Exception('Cannot delete a non-keyed object')
    def db_get_package(self, key):
        return None
    def db_get_package_by_name(self, key):
        return self.db_packages_name_index[key]
    def db_has_package_with_name(self, key):
        return key in self.db_packages_name_index
    


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

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        children = []
        if self._db_value is not None:
            children.extend(self._db_value.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                self._db_value = None
        to_del = []
        for child in self.db_accounts:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
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

class DBLog(object):

    vtType = 'log'

    def __init__(self, id=None, entity_type=None, version=None, name=None, last_modified=None, workflow_execs=None, vistrail_id=None):
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
        if 'vistrail_id' in class_dict:
            res = class_dict['vistrail_id'](old_obj, trans_dict)
            new_obj.db_vistrail_id = res
        elif hasattr(old_obj, 'db_vistrail_id') and old_obj.db_vistrail_id is not None:
            new_obj.db_vistrail_id = old_obj.db_vistrail_id
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        children = []
        to_del = []
        for child in self.db_workflow_execs:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_workflow_exec(child)
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_workflow_execs)
        if remove:
            self.db_deleted_workflow_execs = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        for child in self._db_workflow_execs:
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

class DBLoopIteration(object):

    vtType = 'loop_iteration'

    def __init__(self, item_execs=None, id=None, ts_start=None, ts_end=None, iteration=None, completed=None, error=None):
        self.db_deleted_item_execs = []
        self.db_item_execs_id_index = {}
        if item_execs is None:
            self._db_item_execs = []
        else:
            self._db_item_execs = item_execs
            for v in self._db_item_execs:
                self.db_item_execs_id_index[v.db_id] = v
        self._db_id = id
        self._db_ts_start = ts_start
        self._db_ts_end = ts_end
        self._db_iteration = iteration
        self._db_completed = completed
        self._db_error = error
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBLoopIteration.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBLoopIteration(id=self._db_id,
                             ts_start=self._db_ts_start,
                             ts_end=self._db_ts_end,
                             iteration=self._db_iteration,
                             completed=self._db_completed,
                             error=self._db_error)
        if self._db_item_execs is None:
            cp._db_item_execs = []
        else:
            cp._db_item_execs = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_item_execs]
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
        
        # recreate indices and set flags
        cp.db_item_execs_id_index = dict((v.db_id, v) for v in cp._db_item_execs)
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBLoopIteration()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'item_execs' in class_dict:
            res = class_dict['item_execs'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_item_exec(obj)
        elif hasattr(old_obj, 'db_item_execs') and old_obj.db_item_execs is not None:
            for obj in old_obj.db_item_execs:
                if obj.vtType == 'module_exec':
                    new_obj.db_add_item_exec(DBModuleExec.update_version(obj, trans_dict))
                elif obj.vtType == 'group_exec':
                    new_obj.db_add_item_exec(DBGroupExec.update_version(obj, trans_dict))
                elif obj.vtType == 'loop_exec':
                    new_obj.db_add_item_exec(DBLoopExec.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_item_execs') and hasattr(new_obj, 'db_deleted_item_execs'):
            for obj in old_obj.db_deleted_item_execs:
                if obj.vtType == 'module_exec':
                    n_obj = DBModuleExec.update_version(obj, trans_dict)
                    new_obj.db_deleted_item_execs.append(n_obj)
                elif obj.vtType == 'group_exec':
                    n_obj = DBGroupExec.update_version(obj, trans_dict)
                    new_obj.db_deleted_item_execs.append(n_obj)
                elif obj.vtType == 'loop_exec':
                    n_obj = DBLoopExec.update_version(obj, trans_dict)
                    new_obj.db_deleted_item_execs.append(n_obj)
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'ts_start' in class_dict:
            res = class_dict['ts_start'](old_obj, trans_dict)
            new_obj.db_ts_start = res
        elif hasattr(old_obj, 'db_ts_start') and old_obj.db_ts_start is not None:
            new_obj.db_ts_start = old_obj.db_ts_start
        if 'ts_end' in class_dict:
            res = class_dict['ts_end'](old_obj, trans_dict)
            new_obj.db_ts_end = res
        elif hasattr(old_obj, 'db_ts_end') and old_obj.db_ts_end is not None:
            new_obj.db_ts_end = old_obj.db_ts_end
        if 'iteration' in class_dict:
            res = class_dict['iteration'](old_obj, trans_dict)
            new_obj.db_iteration = res
        elif hasattr(old_obj, 'db_iteration') and old_obj.db_iteration is not None:
            new_obj.db_iteration = old_obj.db_iteration
        if 'completed' in class_dict:
            res = class_dict['completed'](old_obj, trans_dict)
            new_obj.db_completed = res
        elif hasattr(old_obj, 'db_completed') and old_obj.db_completed is not None:
            new_obj.db_completed = old_obj.db_completed
        if 'error' in class_dict:
            res = class_dict['error'](old_obj, trans_dict)
            new_obj.db_error = res
        elif hasattr(old_obj, 'db_error') and old_obj.db_error is not None:
            new_obj.db_error = old_obj.db_error
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        children = []
        to_del = []
        for child in self.db_item_execs:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_item_exec(child)
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_item_execs)
        if remove:
            self.db_deleted_item_execs = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        for child in self._db_item_execs:
            if child.has_changes():
                return True
        return False
    def __get_db_item_execs(self):
        return self._db_item_execs
    def __set_db_item_execs(self, item_execs):
        self._db_item_execs = item_execs
        self.is_dirty = True
    db_item_execs = property(__get_db_item_execs, __set_db_item_execs)
    def db_get_item_execs(self):
        return self._db_item_execs
    def db_add_item_exec(self, item_exec):
        self.is_dirty = True
        self._db_item_execs.append(item_exec)
        self.db_item_execs_id_index[item_exec.db_id] = item_exec
    def db_change_item_exec(self, item_exec):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_item_execs)):
            if self._db_item_execs[i].db_id == item_exec.db_id:
                self._db_item_execs[i] = item_exec
                found = True
                break
        if not found:
            self._db_item_execs.append(item_exec)
        self.db_item_execs_id_index[item_exec.db_id] = item_exec
    def db_delete_item_exec(self, item_exec):
        self.is_dirty = True
        for i in xrange(len(self._db_item_execs)):
            if self._db_item_execs[i].db_id == item_exec.db_id:
                if not self._db_item_execs[i].is_new:
                    self.db_deleted_item_execs.append(self._db_item_execs[i])
                del self._db_item_execs[i]
                break
        del self.db_item_execs_id_index[item_exec.db_id]
    def db_get_item_exec(self, key):
        for i in xrange(len(self._db_item_execs)):
            if self._db_item_execs[i].db_id == key:
                return self._db_item_execs[i]
        return None
    def db_get_item_exec_by_id(self, key):
        return self.db_item_execs_id_index[key]
    def db_has_item_exec_with_id(self, key):
        return key in self.db_item_execs_id_index
    
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
    
    def __get_db_ts_start(self):
        return self._db_ts_start
    def __set_db_ts_start(self, ts_start):
        self._db_ts_start = ts_start
        self.is_dirty = True
    db_ts_start = property(__get_db_ts_start, __set_db_ts_start)
    def db_add_ts_start(self, ts_start):
        self._db_ts_start = ts_start
    def db_change_ts_start(self, ts_start):
        self._db_ts_start = ts_start
    def db_delete_ts_start(self, ts_start):
        self._db_ts_start = None
    
    def __get_db_ts_end(self):
        return self._db_ts_end
    def __set_db_ts_end(self, ts_end):
        self._db_ts_end = ts_end
        self.is_dirty = True
    db_ts_end = property(__get_db_ts_end, __set_db_ts_end)
    def db_add_ts_end(self, ts_end):
        self._db_ts_end = ts_end
    def db_change_ts_end(self, ts_end):
        self._db_ts_end = ts_end
    def db_delete_ts_end(self, ts_end):
        self._db_ts_end = None
    
    def __get_db_iteration(self):
        return self._db_iteration
    def __set_db_iteration(self, iteration):
        self._db_iteration = iteration
        self.is_dirty = True
    db_iteration = property(__get_db_iteration, __set_db_iteration)
    def db_add_iteration(self, iteration):
        self._db_iteration = iteration
    def db_change_iteration(self, iteration):
        self._db_iteration = iteration
    def db_delete_iteration(self, iteration):
        self._db_iteration = None
    
    def __get_db_completed(self):
        return self._db_completed
    def __set_db_completed(self, completed):
        self._db_completed = completed
        self.is_dirty = True
    db_completed = property(__get_db_completed, __set_db_completed)
    def db_add_completed(self, completed):
        self._db_completed = completed
    def db_change_completed(self, completed):
        self._db_completed = completed
    def db_delete_completed(self, completed):
        self._db_completed = None
    
    def __get_db_error(self):
        return self._db_error
    def __set_db_error(self, error):
        self._db_error = error
        self.is_dirty = True
    db_error = property(__get_db_error, __set_db_error)
    def db_add_error(self, error):
        self._db_error = error
    def db_change_error(self, error):
        self._db_error = error
    def db_delete_error(self, error):
        self._db_error = None
    
    def getPrimaryKey(self):
        return self._db_id

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

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
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

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        children = []
        to_del = []
        for child in self.db_artifacts:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
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
    


class DBPEParameter(object):

    vtType = 'pe_parameter'

    def __init__(self, id=None, pos=None, interpolator=None, value=None, dimension=None):
        self._db_id = id
        self._db_pos = pos
        self._db_interpolator = interpolator
        self._db_value = value
        self._db_dimension = dimension
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBPEParameter.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBPEParameter(id=self._db_id,
                           pos=self._db_pos,
                           interpolator=self._db_interpolator,
                           value=self._db_value,
                           dimension=self._db_dimension)
        
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
            new_obj = DBPEParameter()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'pos' in class_dict:
            res = class_dict['pos'](old_obj, trans_dict)
            new_obj.db_pos = res
        elif hasattr(old_obj, 'db_pos') and old_obj.db_pos is not None:
            new_obj.db_pos = old_obj.db_pos
        if 'interpolator' in class_dict:
            res = class_dict['interpolator'](old_obj, trans_dict)
            new_obj.db_interpolator = res
        elif hasattr(old_obj, 'db_interpolator') and old_obj.db_interpolator is not None:
            new_obj.db_interpolator = old_obj.db_interpolator
        if 'value' in class_dict:
            res = class_dict['value'](old_obj, trans_dict)
            new_obj.db_value = res
        elif hasattr(old_obj, 'db_value') and old_obj.db_value is not None:
            new_obj.db_value = old_obj.db_value
        if 'dimension' in class_dict:
            res = class_dict['dimension'](old_obj, trans_dict)
            new_obj.db_dimension = res
        elif hasattr(old_obj, 'db_dimension') and old_obj.db_dimension is not None:
            new_obj.db_dimension = old_obj.db_dimension
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
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
    
    def __get_db_pos(self):
        return self._db_pos
    def __set_db_pos(self, pos):
        self._db_pos = pos
        self.is_dirty = True
    db_pos = property(__get_db_pos, __set_db_pos)
    def db_add_pos(self, pos):
        self._db_pos = pos
    def db_change_pos(self, pos):
        self._db_pos = pos
    def db_delete_pos(self, pos):
        self._db_pos = None
    
    def __get_db_interpolator(self):
        return self._db_interpolator
    def __set_db_interpolator(self, interpolator):
        self._db_interpolator = interpolator
        self.is_dirty = True
    db_interpolator = property(__get_db_interpolator, __set_db_interpolator)
    def db_add_interpolator(self, interpolator):
        self._db_interpolator = interpolator
    def db_change_interpolator(self, interpolator):
        self._db_interpolator = interpolator
    def db_delete_interpolator(self, interpolator):
        self._db_interpolator = None
    
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
    
    def __get_db_dimension(self):
        return self._db_dimension
    def __set_db_dimension(self, dimension):
        self._db_dimension = dimension
        self.is_dirty = True
    db_dimension = property(__get_db_dimension, __set_db_dimension)
    def db_add_dimension(self, dimension):
        self._db_dimension = dimension
    def db_change_dimension(self, dimension):
        self._db_dimension = dimension
    def db_delete_dimension(self, dimension):
        self._db_dimension = None
    
    def getPrimaryKey(self):
        return self._db_id

class DBWorkflowExec(object):

    vtType = 'workflow_exec'

    def __init__(self, item_execs=None, id=None, user=None, ip=None, session=None, vt_version=None, ts_start=None, ts_end=None, parent_id=None, parent_type=None, parent_version=None, completed=None, name=None, annotations=None, machines=None):
        self.db_deleted_item_execs = []
        self.db_item_execs_id_index = {}
        if item_execs is None:
            self._db_item_execs = []
        else:
            self._db_item_execs = item_execs
            for v in self._db_item_execs:
                self.db_item_execs_id_index[v.db_id] = v
        self._db_id = id
        self._db_user = user
        self._db_ip = ip
        self._db_session = session
        self._db_vt_version = vt_version
        self._db_ts_start = ts_start
        self._db_ts_end = ts_end
        self._db_parent_id = parent_id
        self._db_parent_type = parent_type
        self._db_parent_version = parent_version
        self._db_completed = completed
        self._db_name = name
        self.db_deleted_annotations = []
        self.db_annotations_id_index = {}
        if annotations is None:
            self._db_annotations = []
        else:
            self._db_annotations = annotations
            for v in self._db_annotations:
                self.db_annotations_id_index[v.db_id] = v
        self.db_deleted_machines = []
        self.db_machines_id_index = {}
        if machines is None:
            self._db_machines = []
        else:
            self._db_machines = machines
            for v in self._db_machines:
                self.db_machines_id_index[v.db_id] = v
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBWorkflowExec.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBWorkflowExec(id=self._db_id,
                            user=self._db_user,
                            ip=self._db_ip,
                            session=self._db_session,
                            vt_version=self._db_vt_version,
                            ts_start=self._db_ts_start,
                            ts_end=self._db_ts_end,
                            parent_id=self._db_parent_id,
                            parent_type=self._db_parent_type,
                            parent_version=self._db_parent_version,
                            completed=self._db_completed,
                            name=self._db_name)
        if self._db_item_execs is None:
            cp._db_item_execs = []
        else:
            cp._db_item_execs = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_item_execs]
        if self._db_annotations is None:
            cp._db_annotations = []
        else:
            cp._db_annotations = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_annotations]
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
        
        # recreate indices and set flags
        cp.db_item_execs_id_index = dict((v.db_id, v) for v in cp._db_item_execs)
        cp.db_annotations_id_index = dict((v.db_id, v) for v in cp._db_annotations)
        cp.db_machines_id_index = dict((v.db_id, v) for v in cp._db_machines)
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBWorkflowExec()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'item_execs' in class_dict:
            res = class_dict['item_execs'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_item_exec(obj)
        elif hasattr(old_obj, 'db_item_execs') and old_obj.db_item_execs is not None:
            for obj in old_obj.db_item_execs:
                if obj.vtType == 'module_exec':
                    new_obj.db_add_item_exec(DBModuleExec.update_version(obj, trans_dict))
                elif obj.vtType == 'group_exec':
                    new_obj.db_add_item_exec(DBGroupExec.update_version(obj, trans_dict))
                elif obj.vtType == 'loop_exec':
                    new_obj.db_add_item_exec(DBLoopExec.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_item_execs') and hasattr(new_obj, 'db_deleted_item_execs'):
            for obj in old_obj.db_deleted_item_execs:
                if obj.vtType == 'module_exec':
                    n_obj = DBModuleExec.update_version(obj, trans_dict)
                    new_obj.db_deleted_item_execs.append(n_obj)
                elif obj.vtType == 'group_exec':
                    n_obj = DBGroupExec.update_version(obj, trans_dict)
                    new_obj.db_deleted_item_execs.append(n_obj)
                elif obj.vtType == 'loop_exec':
                    n_obj = DBLoopExec.update_version(obj, trans_dict)
                    new_obj.db_deleted_item_execs.append(n_obj)
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'user' in class_dict:
            res = class_dict['user'](old_obj, trans_dict)
            new_obj.db_user = res
        elif hasattr(old_obj, 'db_user') and old_obj.db_user is not None:
            new_obj.db_user = old_obj.db_user
        if 'ip' in class_dict:
            res = class_dict['ip'](old_obj, trans_dict)
            new_obj.db_ip = res
        elif hasattr(old_obj, 'db_ip') and old_obj.db_ip is not None:
            new_obj.db_ip = old_obj.db_ip
        if 'session' in class_dict:
            res = class_dict['session'](old_obj, trans_dict)
            new_obj.db_session = res
        elif hasattr(old_obj, 'db_session') and old_obj.db_session is not None:
            new_obj.db_session = old_obj.db_session
        if 'vt_version' in class_dict:
            res = class_dict['vt_version'](old_obj, trans_dict)
            new_obj.db_vt_version = res
        elif hasattr(old_obj, 'db_vt_version') and old_obj.db_vt_version is not None:
            new_obj.db_vt_version = old_obj.db_vt_version
        if 'ts_start' in class_dict:
            res = class_dict['ts_start'](old_obj, trans_dict)
            new_obj.db_ts_start = res
        elif hasattr(old_obj, 'db_ts_start') and old_obj.db_ts_start is not None:
            new_obj.db_ts_start = old_obj.db_ts_start
        if 'ts_end' in class_dict:
            res = class_dict['ts_end'](old_obj, trans_dict)
            new_obj.db_ts_end = res
        elif hasattr(old_obj, 'db_ts_end') and old_obj.db_ts_end is not None:
            new_obj.db_ts_end = old_obj.db_ts_end
        if 'parent_id' in class_dict:
            res = class_dict['parent_id'](old_obj, trans_dict)
            new_obj.db_parent_id = res
        elif hasattr(old_obj, 'db_parent_id') and old_obj.db_parent_id is not None:
            new_obj.db_parent_id = old_obj.db_parent_id
        if 'parent_type' in class_dict:
            res = class_dict['parent_type'](old_obj, trans_dict)
            new_obj.db_parent_type = res
        elif hasattr(old_obj, 'db_parent_type') and old_obj.db_parent_type is not None:
            new_obj.db_parent_type = old_obj.db_parent_type
        if 'parent_version' in class_dict:
            res = class_dict['parent_version'](old_obj, trans_dict)
            new_obj.db_parent_version = res
        elif hasattr(old_obj, 'db_parent_version') and old_obj.db_parent_version is not None:
            new_obj.db_parent_version = old_obj.db_parent_version
        if 'completed' in class_dict:
            res = class_dict['completed'](old_obj, trans_dict)
            new_obj.db_completed = res
        elif hasattr(old_obj, 'db_completed') and old_obj.db_completed is not None:
            new_obj.db_completed = old_obj.db_completed
        if 'name' in class_dict:
            res = class_dict['name'](old_obj, trans_dict)
            new_obj.db_name = res
        elif hasattr(old_obj, 'db_name') and old_obj.db_name is not None:
            new_obj.db_name = old_obj.db_name
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
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        children = []
        to_del = []
        for child in self.db_annotations:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_annotation(child)
        to_del = []
        for child in self.db_machines:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_machine(child)
        to_del = []
        for child in self.db_item_execs:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_item_exec(child)
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_annotations)
        children.extend(self.db_deleted_machines)
        children.extend(self.db_deleted_item_execs)
        if remove:
            self.db_deleted_annotations = []
            self.db_deleted_machines = []
            self.db_deleted_item_execs = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        for child in self._db_annotations:
            if child.has_changes():
                return True
        for child in self._db_machines:
            if child.has_changes():
                return True
        for child in self._db_item_execs:
            if child.has_changes():
                return True
        return False
    def __get_db_item_execs(self):
        return self._db_item_execs
    def __set_db_item_execs(self, item_execs):
        self._db_item_execs = item_execs
        self.is_dirty = True
    db_item_execs = property(__get_db_item_execs, __set_db_item_execs)
    def db_get_item_execs(self):
        return self._db_item_execs
    def db_add_item_exec(self, item_exec):
        self.is_dirty = True
        self._db_item_execs.append(item_exec)
        self.db_item_execs_id_index[item_exec.db_id] = item_exec
    def db_change_item_exec(self, item_exec):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_item_execs)):
            if self._db_item_execs[i].db_id == item_exec.db_id:
                self._db_item_execs[i] = item_exec
                found = True
                break
        if not found:
            self._db_item_execs.append(item_exec)
        self.db_item_execs_id_index[item_exec.db_id] = item_exec
    def db_delete_item_exec(self, item_exec):
        self.is_dirty = True
        for i in xrange(len(self._db_item_execs)):
            if self._db_item_execs[i].db_id == item_exec.db_id:
                if not self._db_item_execs[i].is_new:
                    self.db_deleted_item_execs.append(self._db_item_execs[i])
                del self._db_item_execs[i]
                break
        del self.db_item_execs_id_index[item_exec.db_id]
    def db_get_item_exec(self, key):
        for i in xrange(len(self._db_item_execs)):
            if self._db_item_execs[i].db_id == key:
                return self._db_item_execs[i]
        return None
    def db_get_item_exec_by_id(self, key):
        return self.db_item_execs_id_index[key]
    def db_has_item_exec_with_id(self, key):
        return key in self.db_item_execs_id_index
    
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
    
    def __get_db_user(self):
        return self._db_user
    def __set_db_user(self, user):
        self._db_user = user
        self.is_dirty = True
    db_user = property(__get_db_user, __set_db_user)
    def db_add_user(self, user):
        self._db_user = user
    def db_change_user(self, user):
        self._db_user = user
    def db_delete_user(self, user):
        self._db_user = None
    
    def __get_db_ip(self):
        return self._db_ip
    def __set_db_ip(self, ip):
        self._db_ip = ip
        self.is_dirty = True
    db_ip = property(__get_db_ip, __set_db_ip)
    def db_add_ip(self, ip):
        self._db_ip = ip
    def db_change_ip(self, ip):
        self._db_ip = ip
    def db_delete_ip(self, ip):
        self._db_ip = None
    
    def __get_db_session(self):
        return self._db_session
    def __set_db_session(self, session):
        self._db_session = session
        self.is_dirty = True
    db_session = property(__get_db_session, __set_db_session)
    def db_add_session(self, session):
        self._db_session = session
    def db_change_session(self, session):
        self._db_session = session
    def db_delete_session(self, session):
        self._db_session = None
    
    def __get_db_vt_version(self):
        return self._db_vt_version
    def __set_db_vt_version(self, vt_version):
        self._db_vt_version = vt_version
        self.is_dirty = True
    db_vt_version = property(__get_db_vt_version, __set_db_vt_version)
    def db_add_vt_version(self, vt_version):
        self._db_vt_version = vt_version
    def db_change_vt_version(self, vt_version):
        self._db_vt_version = vt_version
    def db_delete_vt_version(self, vt_version):
        self._db_vt_version = None
    
    def __get_db_ts_start(self):
        return self._db_ts_start
    def __set_db_ts_start(self, ts_start):
        self._db_ts_start = ts_start
        self.is_dirty = True
    db_ts_start = property(__get_db_ts_start, __set_db_ts_start)
    def db_add_ts_start(self, ts_start):
        self._db_ts_start = ts_start
    def db_change_ts_start(self, ts_start):
        self._db_ts_start = ts_start
    def db_delete_ts_start(self, ts_start):
        self._db_ts_start = None
    
    def __get_db_ts_end(self):
        return self._db_ts_end
    def __set_db_ts_end(self, ts_end):
        self._db_ts_end = ts_end
        self.is_dirty = True
    db_ts_end = property(__get_db_ts_end, __set_db_ts_end)
    def db_add_ts_end(self, ts_end):
        self._db_ts_end = ts_end
    def db_change_ts_end(self, ts_end):
        self._db_ts_end = ts_end
    def db_delete_ts_end(self, ts_end):
        self._db_ts_end = None
    
    def __get_db_parent_id(self):
        return self._db_parent_id
    def __set_db_parent_id(self, parent_id):
        self._db_parent_id = parent_id
        self.is_dirty = True
    db_parent_id = property(__get_db_parent_id, __set_db_parent_id)
    def db_add_parent_id(self, parent_id):
        self._db_parent_id = parent_id
    def db_change_parent_id(self, parent_id):
        self._db_parent_id = parent_id
    def db_delete_parent_id(self, parent_id):
        self._db_parent_id = None
    
    def __get_db_parent_type(self):
        return self._db_parent_type
    def __set_db_parent_type(self, parent_type):
        self._db_parent_type = parent_type
        self.is_dirty = True
    db_parent_type = property(__get_db_parent_type, __set_db_parent_type)
    def db_add_parent_type(self, parent_type):
        self._db_parent_type = parent_type
    def db_change_parent_type(self, parent_type):
        self._db_parent_type = parent_type
    def db_delete_parent_type(self, parent_type):
        self._db_parent_type = None
    
    def __get_db_parent_version(self):
        return self._db_parent_version
    def __set_db_parent_version(self, parent_version):
        self._db_parent_version = parent_version
        self.is_dirty = True
    db_parent_version = property(__get_db_parent_version, __set_db_parent_version)
    def db_add_parent_version(self, parent_version):
        self._db_parent_version = parent_version
    def db_change_parent_version(self, parent_version):
        self._db_parent_version = parent_version
    def db_delete_parent_version(self, parent_version):
        self._db_parent_version = None
    
    def __get_db_completed(self):
        return self._db_completed
    def __set_db_completed(self, completed):
        self._db_completed = completed
        self.is_dirty = True
    db_completed = property(__get_db_completed, __set_db_completed)
    def db_add_completed(self, completed):
        self._db_completed = completed
    def db_change_completed(self, completed):
        self._db_completed = completed
    def db_delete_completed(self, completed):
        self._db_completed = None
    
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
    def db_delete_annotation(self, annotation):
        self.is_dirty = True
        for i in xrange(len(self._db_annotations)):
            if self._db_annotations[i].db_id == annotation.db_id:
                if not self._db_annotations[i].is_new:
                    self.db_deleted_annotations.append(self._db_annotations[i])
                del self._db_annotations[i]
                break
        del self.db_annotations_id_index[annotation.db_id]
    def db_get_annotation(self, key):
        for i in xrange(len(self._db_annotations)):
            if self._db_annotations[i].db_id == key:
                return self._db_annotations[i]
        return None
    def db_get_annotation_by_id(self, key):
        return self.db_annotations_id_index[key]
    def db_has_annotation_with_id(self, key):
        return key in self.db_annotations_id_index
    
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
    
    def getPrimaryKey(self):
        return self._db_id

class DBLocation(object):

    vtType = 'location'

    def __init__(self, id=None, x=None, y=None):
        self._db_id = id
        self._db_x = x
        self._db_y = y
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBLocation.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBLocation(id=self._db_id,
                        x=self._db_x,
                        y=self._db_y)
        
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
            new_obj = DBLocation()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'x' in class_dict:
            res = class_dict['x'](old_obj, trans_dict)
            new_obj.db_x = res
        elif hasattr(old_obj, 'db_x') and old_obj.db_x is not None:
            new_obj.db_x = old_obj.db_x
        if 'y' in class_dict:
            res = class_dict['y'](old_obj, trans_dict)
            new_obj.db_y = res
        elif hasattr(old_obj, 'db_y') and old_obj.db_y is not None:
            new_obj.db_y = old_obj.db_y
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
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
    
    def __get_db_x(self):
        return self._db_x
    def __set_db_x(self, x):
        self._db_x = x
        self.is_dirty = True
    db_x = property(__get_db_x, __set_db_x)
    def db_add_x(self, x):
        self._db_x = x
    def db_change_x(self, x):
        self._db_x = x
    def db_delete_x(self, x):
        self._db_x = None
    
    def __get_db_y(self):
        return self._db_y
    def __set_db_y(self, y):
        self._db_y = y
        self.is_dirty = True
    db_y = property(__get_db_y, __set_db_y)
    def db_add_y(self, y):
        self._db_y = y
    def db_change_y(self, y):
        self._db_y = y
    def db_delete_y(self, y):
        self._db_y = None
    
    def getPrimaryKey(self):
        return self._db_id

class DBFunction(object):

    vtType = 'function'

    def __init__(self, id=None, pos=None, name=None, parameters=None):
        self._db_id = id
        self._db_pos = pos
        self._db_name = name
        self.db_deleted_parameters = []
        self.db_parameters_id_index = {}
        if parameters is None:
            self._db_parameters = []
        else:
            self._db_parameters = parameters
            for v in self._db_parameters:
                self.db_parameters_id_index[v.db_id] = v
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBFunction.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBFunction(id=self._db_id,
                        pos=self._db_pos,
                        name=self._db_name)
        if self._db_parameters is None:
            cp._db_parameters = []
        else:
            cp._db_parameters = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_parameters]
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
        
        # recreate indices and set flags
        cp.db_parameters_id_index = dict((v.db_id, v) for v in cp._db_parameters)
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBFunction()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'pos' in class_dict:
            res = class_dict['pos'](old_obj, trans_dict)
            new_obj.db_pos = res
        elif hasattr(old_obj, 'db_pos') and old_obj.db_pos is not None:
            new_obj.db_pos = old_obj.db_pos
        if 'name' in class_dict:
            res = class_dict['name'](old_obj, trans_dict)
            new_obj.db_name = res
        elif hasattr(old_obj, 'db_name') and old_obj.db_name is not None:
            new_obj.db_name = old_obj.db_name
        if 'parameters' in class_dict:
            res = class_dict['parameters'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_parameter(obj)
        elif hasattr(old_obj, 'db_parameters') and old_obj.db_parameters is not None:
            for obj in old_obj.db_parameters:
                new_obj.db_add_parameter(DBParameter.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_parameters') and hasattr(new_obj, 'db_deleted_parameters'):
            for obj in old_obj.db_deleted_parameters:
                n_obj = DBParameter.update_version(obj, trans_dict)
                new_obj.db_deleted_parameters.append(n_obj)
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        children = []
        to_del = []
        for child in self.db_parameters:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_parameter(child)
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_parameters)
        if remove:
            self.db_deleted_parameters = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        for child in self._db_parameters:
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
    
    def __get_db_pos(self):
        return self._db_pos
    def __set_db_pos(self, pos):
        self._db_pos = pos
        self.is_dirty = True
    db_pos = property(__get_db_pos, __set_db_pos)
    def db_add_pos(self, pos):
        self._db_pos = pos
    def db_change_pos(self, pos):
        self._db_pos = pos
    def db_delete_pos(self, pos):
        self._db_pos = None
    
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
    
    def __get_db_parameters(self):
        return self._db_parameters
    def __set_db_parameters(self, parameters):
        self._db_parameters = parameters
        self.is_dirty = True
    db_parameters = property(__get_db_parameters, __set_db_parameters)
    def db_get_parameters(self):
        return self._db_parameters
    def db_add_parameter(self, parameter):
        self.is_dirty = True
        self._db_parameters.append(parameter)
        self.db_parameters_id_index[parameter.db_id] = parameter
    def db_change_parameter(self, parameter):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_parameters)):
            if self._db_parameters[i].db_id == parameter.db_id:
                self._db_parameters[i] = parameter
                found = True
                break
        if not found:
            self._db_parameters.append(parameter)
        self.db_parameters_id_index[parameter.db_id] = parameter
    def db_delete_parameter(self, parameter):
        self.is_dirty = True
        for i in xrange(len(self._db_parameters)):
            if self._db_parameters[i].db_id == parameter.db_id:
                if not self._db_parameters[i].is_new:
                    self.db_deleted_parameters.append(self._db_parameters[i])
                del self._db_parameters[i]
                break
        del self.db_parameters_id_index[parameter.db_id]
    def db_get_parameter(self, key):
        for i in xrange(len(self._db_parameters)):
            if self._db_parameters[i].db_id == key:
                return self._db_parameters[i]
        return None
    def db_get_parameter_by_id(self, key):
        return self.db_parameters_id_index[key]
    def db_has_parameter_with_id(self, key):
        return key in self.db_parameters_id_index
    
    def getPrimaryKey(self):
        return self._db_id

class DBActionAnnotation(object):

    vtType = 'actionAnnotation'

    def __init__(self, id=None, key=None, value=None, action_id=None, date=None, user=None):
        self._db_id = id
        self._db_key = key
        self._db_value = value
        self._db_action_id = action_id
        self._db_date = date
        self._db_user = user
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBActionAnnotation.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBActionAnnotation(id=self._db_id,
                                key=self._db_key,
                                value=self._db_value,
                                action_id=self._db_action_id,
                                date=self._db_date,
                                user=self._db_user)
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
            if hasattr(self, 'db_action_id') and ('action', self._db_action_id) in id_remap:
                cp._db_action_id = id_remap[('action', self._db_action_id)]
        
        # recreate indices and set flags
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBActionAnnotation()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'key' in class_dict:
            res = class_dict['key'](old_obj, trans_dict)
            new_obj.db_key = res
        elif hasattr(old_obj, 'db_key') and old_obj.db_key is not None:
            new_obj.db_key = old_obj.db_key
        if 'value' in class_dict:
            res = class_dict['value'](old_obj, trans_dict)
            new_obj.db_value = res
        elif hasattr(old_obj, 'db_value') and old_obj.db_value is not None:
            new_obj.db_value = old_obj.db_value
        if 'action_id' in class_dict:
            res = class_dict['action_id'](old_obj, trans_dict)
            new_obj.db_action_id = res
        elif hasattr(old_obj, 'db_action_id') and old_obj.db_action_id is not None:
            new_obj.db_action_id = old_obj.db_action_id
        if 'date' in class_dict:
            res = class_dict['date'](old_obj, trans_dict)
            new_obj.db_date = res
        elif hasattr(old_obj, 'db_date') and old_obj.db_date is not None:
            new_obj.db_date = old_obj.db_date
        if 'user' in class_dict:
            res = class_dict['user'](old_obj, trans_dict)
            new_obj.db_user = res
        elif hasattr(old_obj, 'db_user') and old_obj.db_user is not None:
            new_obj.db_user = old_obj.db_user
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
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
    
    def __get_db_key(self):
        return self._db_key
    def __set_db_key(self, key):
        self._db_key = key
        self.is_dirty = True
    db_key = property(__get_db_key, __set_db_key)
    def db_add_key(self, key):
        self._db_key = key
    def db_change_key(self, key):
        self._db_key = key
    def db_delete_key(self, key):
        self._db_key = None
    
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
    
    def __get_db_action_id(self):
        return self._db_action_id
    def __set_db_action_id(self, action_id):
        self._db_action_id = action_id
        self.is_dirty = True
    db_action_id = property(__get_db_action_id, __set_db_action_id)
    def db_add_action_id(self, action_id):
        self._db_action_id = action_id
    def db_change_action_id(self, action_id):
        self._db_action_id = action_id
    def db_delete_action_id(self, action_id):
        self._db_action_id = None
    
    def __get_db_date(self):
        return self._db_date
    def __set_db_date(self, date):
        self._db_date = date
        self.is_dirty = True
    db_date = property(__get_db_date, __set_db_date)
    def db_add_date(self, date):
        self._db_date = date
    def db_change_date(self, date):
        self._db_date = date
    def db_delete_date(self, date):
        self._db_date = None
    
    def __get_db_user(self):
        return self._db_user
    def __set_db_user(self, user):
        self._db_user = user
        self.is_dirty = True
    db_user = property(__get_db_user, __set_db_user)
    def db_add_user(self, user):
        self._db_user = user
    def db_change_user(self, user):
        self._db_user = user
    def db_delete_user(self, user):
        self._db_user = None
    
    def getPrimaryKey(self):
        return self._db_id

class DBProvActivity(object):

    vtType = 'prov_activity'

    def __init__(self, id=None, startTime=None, endTime=None, vt_id=None, vt_type=None, vt_cached=None, vt_completed=None, vt_machine_id=None, vt_error=None, is_part_of=None):
        self._db_id = id
        self._db_startTime = startTime
        self._db_endTime = endTime
        self._db_vt_id = vt_id
        self._db_vt_type = vt_type
        self._db_vt_cached = vt_cached
        self._db_vt_completed = vt_completed
        self._db_vt_machine_id = vt_machine_id
        self._db_vt_error = vt_error
        self.db_deleted_is_part_of = []
        self._db_is_part_of = is_part_of
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBProvActivity.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBProvActivity(id=self._db_id,
                            startTime=self._db_startTime,
                            endTime=self._db_endTime,
                            vt_id=self._db_vt_id,
                            vt_type=self._db_vt_type,
                            vt_cached=self._db_vt_cached,
                            vt_completed=self._db_vt_completed,
                            vt_machine_id=self._db_vt_machine_id,
                            vt_error=self._db_vt_error)
        if self._db_is_part_of is not None:
            cp._db_is_part_of = self._db_is_part_of.do_copy(new_ids, id_scope, id_remap)
        
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
            new_obj = DBProvActivity()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'startTime' in class_dict:
            res = class_dict['startTime'](old_obj, trans_dict)
            new_obj.db_startTime = res
        elif hasattr(old_obj, 'db_startTime') and old_obj.db_startTime is not None:
            new_obj.db_startTime = old_obj.db_startTime
        if 'endTime' in class_dict:
            res = class_dict['endTime'](old_obj, trans_dict)
            new_obj.db_endTime = res
        elif hasattr(old_obj, 'db_endTime') and old_obj.db_endTime is not None:
            new_obj.db_endTime = old_obj.db_endTime
        if 'vt_id' in class_dict:
            res = class_dict['vt_id'](old_obj, trans_dict)
            new_obj.db_vt_id = res
        elif hasattr(old_obj, 'db_vt_id') and old_obj.db_vt_id is not None:
            new_obj.db_vt_id = old_obj.db_vt_id
        if 'vt_type' in class_dict:
            res = class_dict['vt_type'](old_obj, trans_dict)
            new_obj.db_vt_type = res
        elif hasattr(old_obj, 'db_vt_type') and old_obj.db_vt_type is not None:
            new_obj.db_vt_type = old_obj.db_vt_type
        if 'vt_cached' in class_dict:
            res = class_dict['vt_cached'](old_obj, trans_dict)
            new_obj.db_vt_cached = res
        elif hasattr(old_obj, 'db_vt_cached') and old_obj.db_vt_cached is not None:
            new_obj.db_vt_cached = old_obj.db_vt_cached
        if 'vt_completed' in class_dict:
            res = class_dict['vt_completed'](old_obj, trans_dict)
            new_obj.db_vt_completed = res
        elif hasattr(old_obj, 'db_vt_completed') and old_obj.db_vt_completed is not None:
            new_obj.db_vt_completed = old_obj.db_vt_completed
        if 'vt_machine_id' in class_dict:
            res = class_dict['vt_machine_id'](old_obj, trans_dict)
            new_obj.db_vt_machine_id = res
        elif hasattr(old_obj, 'db_vt_machine_id') and old_obj.db_vt_machine_id is not None:
            new_obj.db_vt_machine_id = old_obj.db_vt_machine_id
        if 'vt_error' in class_dict:
            res = class_dict['vt_error'](old_obj, trans_dict)
            new_obj.db_vt_error = res
        elif hasattr(old_obj, 'db_vt_error') and old_obj.db_vt_error is not None:
            new_obj.db_vt_error = old_obj.db_vt_error
        if 'is_part_of' in class_dict:
            res = class_dict['is_part_of'](old_obj, trans_dict)
            new_obj.db_is_part_of = res
        elif hasattr(old_obj, 'db_is_part_of') and old_obj.db_is_part_of is not None:
            obj = old_obj.db_is_part_of
            new_obj.db_add_is_part_of(DBIsPartOf.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_is_part_of') and hasattr(new_obj, 'db_deleted_is_part_of'):
            for obj in old_obj.db_deleted_is_part_of:
                n_obj = DBIsPartOf.update_version(obj, trans_dict)
                new_obj.db_deleted_is_part_of.append(n_obj)
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        children = []
        if self._db_is_part_of is not None:
            children.extend(self._db_is_part_of.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                self._db_is_part_of = None
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_is_part_of)
        if remove:
            self.db_deleted_is_part_of = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        if self._db_is_part_of is not None and self._db_is_part_of.has_changes():
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
    
    def __get_db_startTime(self):
        return self._db_startTime
    def __set_db_startTime(self, startTime):
        self._db_startTime = startTime
        self.is_dirty = True
    db_startTime = property(__get_db_startTime, __set_db_startTime)
    def db_add_startTime(self, startTime):
        self._db_startTime = startTime
    def db_change_startTime(self, startTime):
        self._db_startTime = startTime
    def db_delete_startTime(self, startTime):
        self._db_startTime = None
    
    def __get_db_endTime(self):
        return self._db_endTime
    def __set_db_endTime(self, endTime):
        self._db_endTime = endTime
        self.is_dirty = True
    db_endTime = property(__get_db_endTime, __set_db_endTime)
    def db_add_endTime(self, endTime):
        self._db_endTime = endTime
    def db_change_endTime(self, endTime):
        self._db_endTime = endTime
    def db_delete_endTime(self, endTime):
        self._db_endTime = None
    
    def __get_db_vt_id(self):
        return self._db_vt_id
    def __set_db_vt_id(self, vt_id):
        self._db_vt_id = vt_id
        self.is_dirty = True
    db_vt_id = property(__get_db_vt_id, __set_db_vt_id)
    def db_add_vt_id(self, vt_id):
        self._db_vt_id = vt_id
    def db_change_vt_id(self, vt_id):
        self._db_vt_id = vt_id
    def db_delete_vt_id(self, vt_id):
        self._db_vt_id = None
    
    def __get_db_vt_type(self):
        return self._db_vt_type
    def __set_db_vt_type(self, vt_type):
        self._db_vt_type = vt_type
        self.is_dirty = True
    db_vt_type = property(__get_db_vt_type, __set_db_vt_type)
    def db_add_vt_type(self, vt_type):
        self._db_vt_type = vt_type
    def db_change_vt_type(self, vt_type):
        self._db_vt_type = vt_type
    def db_delete_vt_type(self, vt_type):
        self._db_vt_type = None
    
    def __get_db_vt_cached(self):
        return self._db_vt_cached
    def __set_db_vt_cached(self, vt_cached):
        self._db_vt_cached = vt_cached
        self.is_dirty = True
    db_vt_cached = property(__get_db_vt_cached, __set_db_vt_cached)
    def db_add_vt_cached(self, vt_cached):
        self._db_vt_cached = vt_cached
    def db_change_vt_cached(self, vt_cached):
        self._db_vt_cached = vt_cached
    def db_delete_vt_cached(self, vt_cached):
        self._db_vt_cached = None
    
    def __get_db_vt_completed(self):
        return self._db_vt_completed
    def __set_db_vt_completed(self, vt_completed):
        self._db_vt_completed = vt_completed
        self.is_dirty = True
    db_vt_completed = property(__get_db_vt_completed, __set_db_vt_completed)
    def db_add_vt_completed(self, vt_completed):
        self._db_vt_completed = vt_completed
    def db_change_vt_completed(self, vt_completed):
        self._db_vt_completed = vt_completed
    def db_delete_vt_completed(self, vt_completed):
        self._db_vt_completed = None
    
    def __get_db_vt_machine_id(self):
        return self._db_vt_machine_id
    def __set_db_vt_machine_id(self, vt_machine_id):
        self._db_vt_machine_id = vt_machine_id
        self.is_dirty = True
    db_vt_machine_id = property(__get_db_vt_machine_id, __set_db_vt_machine_id)
    def db_add_vt_machine_id(self, vt_machine_id):
        self._db_vt_machine_id = vt_machine_id
    def db_change_vt_machine_id(self, vt_machine_id):
        self._db_vt_machine_id = vt_machine_id
    def db_delete_vt_machine_id(self, vt_machine_id):
        self._db_vt_machine_id = None
    
    def __get_db_vt_error(self):
        return self._db_vt_error
    def __set_db_vt_error(self, vt_error):
        self._db_vt_error = vt_error
        self.is_dirty = True
    db_vt_error = property(__get_db_vt_error, __set_db_vt_error)
    def db_add_vt_error(self, vt_error):
        self._db_vt_error = vt_error
    def db_change_vt_error(self, vt_error):
        self._db_vt_error = vt_error
    def db_delete_vt_error(self, vt_error):
        self._db_vt_error = None
    
    def __get_db_is_part_of(self):
        return self._db_is_part_of
    def __set_db_is_part_of(self, is_part_of):
        self._db_is_part_of = is_part_of
        self.is_dirty = True
    db_is_part_of = property(__get_db_is_part_of, __set_db_is_part_of)
    def db_add_is_part_of(self, is_part_of):
        self._db_is_part_of = is_part_of
    def db_change_is_part_of(self, is_part_of):
        self._db_is_part_of = is_part_of
    def db_delete_is_part_of(self, is_part_of):
        if not self.is_new:
            self.db_deleted_is_part_of.append(self._db_is_part_of)
        self._db_is_part_of = None
    
    def getPrimaryKey(self):
        return self._db_id

class DBProvUsage(object):

    vtType = 'prov_usage'

    def __init__(self, prov_activity=None, prov_entity=None, prov_role=None):
        self.db_deleted_prov_activity = []
        self._db_prov_activity = prov_activity
        self.db_deleted_prov_entity = []
        self._db_prov_entity = prov_entity
        self._db_prov_role = prov_role
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBProvUsage.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBProvUsage(prov_role=self._db_prov_role)
        if self._db_prov_activity is not None:
            cp._db_prov_activity = self._db_prov_activity.do_copy(new_ids, id_scope, id_remap)
        if self._db_prov_entity is not None:
            cp._db_prov_entity = self._db_prov_entity.do_copy(new_ids, id_scope, id_remap)
        
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
            new_obj = DBProvUsage()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'prov_activity' in class_dict:
            res = class_dict['prov_activity'](old_obj, trans_dict)
            new_obj.db_prov_activity = res
        elif hasattr(old_obj, 'db_prov_activity') and old_obj.db_prov_activity is not None:
            obj = old_obj.db_prov_activity
            new_obj.db_add_prov_activity(DBRefProvActivity.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_prov_activity') and hasattr(new_obj, 'db_deleted_prov_activity'):
            for obj in old_obj.db_deleted_prov_activity:
                n_obj = DBRefProvActivity.update_version(obj, trans_dict)
                new_obj.db_deleted_prov_activity.append(n_obj)
        if 'prov_entity' in class_dict:
            res = class_dict['prov_entity'](old_obj, trans_dict)
            new_obj.db_prov_entity = res
        elif hasattr(old_obj, 'db_prov_entity') and old_obj.db_prov_entity is not None:
            obj = old_obj.db_prov_entity
            new_obj.db_add_prov_entity(DBRefProvEntity.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_prov_entity') and hasattr(new_obj, 'db_deleted_prov_entity'):
            for obj in old_obj.db_deleted_prov_entity:
                n_obj = DBRefProvEntity.update_version(obj, trans_dict)
                new_obj.db_deleted_prov_entity.append(n_obj)
        if 'prov_role' in class_dict:
            res = class_dict['prov_role'](old_obj, trans_dict)
            new_obj.db_prov_role = res
        elif hasattr(old_obj, 'db_prov_role') and old_obj.db_prov_role is not None:
            new_obj.db_prov_role = old_obj.db_prov_role
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        children = []
        if self._db_prov_activity is not None:
            children.extend(self._db_prov_activity.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                self._db_prov_activity = None
        if self._db_prov_entity is not None:
            children.extend(self._db_prov_entity.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                self._db_prov_entity = None
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_prov_activity)
        children.extend(self.db_deleted_prov_entity)
        if remove:
            self.db_deleted_prov_activity = []
            self.db_deleted_prov_entity = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        if self._db_prov_activity is not None and self._db_prov_activity.has_changes():
            return True
        if self._db_prov_entity is not None and self._db_prov_entity.has_changes():
            return True
        return False
    def __get_db_prov_activity(self):
        return self._db_prov_activity
    def __set_db_prov_activity(self, prov_activity):
        self._db_prov_activity = prov_activity
        self.is_dirty = True
    db_prov_activity = property(__get_db_prov_activity, __set_db_prov_activity)
    def db_add_prov_activity(self, prov_activity):
        self._db_prov_activity = prov_activity
    def db_change_prov_activity(self, prov_activity):
        self._db_prov_activity = prov_activity
    def db_delete_prov_activity(self, prov_activity):
        if not self.is_new:
            self.db_deleted_prov_activity.append(self._db_prov_activity)
        self._db_prov_activity = None
    
    def __get_db_prov_entity(self):
        return self._db_prov_entity
    def __set_db_prov_entity(self, prov_entity):
        self._db_prov_entity = prov_entity
        self.is_dirty = True
    db_prov_entity = property(__get_db_prov_entity, __set_db_prov_entity)
    def db_add_prov_entity(self, prov_entity):
        self._db_prov_entity = prov_entity
    def db_change_prov_entity(self, prov_entity):
        self._db_prov_entity = prov_entity
    def db_delete_prov_entity(self, prov_entity):
        if not self.is_new:
            self.db_deleted_prov_entity.append(self._db_prov_entity)
        self._db_prov_entity = None
    
    def __get_db_prov_role(self):
        return self._db_prov_role
    def __set_db_prov_role(self, prov_role):
        self._db_prov_role = prov_role
        self.is_dirty = True
    db_prov_role = property(__get_db_prov_role, __set_db_prov_role)
    def db_add_prov_role(self, prov_role):
        self._db_prov_role = prov_role
    def db_change_prov_role(self, prov_role):
        self._db_prov_role = prov_role
    def db_delete_prov_role(self, prov_role):
        self._db_prov_role = None
    


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

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
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

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        children = []
        if self._db_accounts is not None:
            children.extend(self._db_accounts.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                self._db_accounts = None
        if self._db_processes is not None:
            children.extend(self._db_processes.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                self._db_processes = None
        if self._db_artifacts is not None:
            children.extend(self._db_artifacts.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                self._db_artifacts = None
        if self._db_agents is not None:
            children.extend(self._db_agents.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                self._db_agents = None
        if self._db_dependencies is not None:
            children.extend(self._db_dependencies.db_children((self.vtType, self.db_id), orphan, for_action))
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
    


class DBIsPartOf(object):

    vtType = 'is_part_of'

    def __init__(self, prov_ref=None):
        self._db_prov_ref = prov_ref
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBIsPartOf.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBIsPartOf(prov_ref=self._db_prov_ref)
        
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
            new_obj = DBIsPartOf()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'prov_ref' in class_dict:
            res = class_dict['prov_ref'](old_obj, trans_dict)
            new_obj.db_prov_ref = res
        elif hasattr(old_obj, 'db_prov_ref') and old_obj.db_prov_ref is not None:
            new_obj.db_prov_ref = old_obj.db_prov_ref
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        return [(self, parent[0], parent[1])]
    def db_deleted_children(self, remove=False):
        children = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        return False
    def __get_db_prov_ref(self):
        return self._db_prov_ref
    def __set_db_prov_ref(self, prov_ref):
        self._db_prov_ref = prov_ref
        self.is_dirty = True
    db_prov_ref = property(__get_db_prov_ref, __set_db_prov_ref)
    def db_add_prov_ref(self, prov_ref):
        self._db_prov_ref = prov_ref
    def db_change_prov_ref(self, prov_ref):
        self._db_prov_ref = prov_ref
    def db_delete_prov_ref(self, prov_ref):
        self._db_prov_ref = None
    


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

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        children = []
        if self._db_effect is not None:
            children.extend(self._db_effect.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                self._db_effect = None
        if self._db_role is not None:
            children.extend(self._db_role.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                self._db_role = None
        if self._db_cause is not None:
            children.extend(self._db_cause.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                self._db_cause = None
        to_del = []
        for child in self.db_accounts:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_account(child)
        to_del = []
        for child in self.db_opm_times:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
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
    


class DBControlParameter(object):

    vtType = 'controlParameter'

    def __init__(self, id=None, name=None, value=None):
        self._db_id = id
        self._db_name = name
        self._db_value = value
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBControlParameter.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBControlParameter(id=self._db_id,
                                name=self._db_name,
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
            new_obj = DBControlParameter()
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
        if 'value' in class_dict:
            res = class_dict['value'](old_obj, trans_dict)
            new_obj.db_value = res
        elif hasattr(old_obj, 'db_value') and old_obj.db_value is not None:
            new_obj.db_value = old_obj.db_value
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
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

class DBPluginData(object):

    vtType = 'plugin_data'

    def __init__(self, id=None, data=None):
        self._db_id = id
        self._db_data = data
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBPluginData.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBPluginData(id=self._db_id,
                          data=self._db_data)
        
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
            new_obj = DBPluginData()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'data' in class_dict:
            res = class_dict['data'](old_obj, trans_dict)
            new_obj.db_data = res
        elif hasattr(old_obj, 'db_data') and old_obj.db_data is not None:
            new_obj.db_data = old_obj.db_data
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
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
    
    def __get_db_data(self):
        return self._db_data
    def __set_db_data(self, data):
        self._db_data = data
        self.is_dirty = True
    db_data = property(__get_db_data, __set_db_data)
    def db_add_data(self, data):
        self._db_data = data
    def db_change_data(self, data):
        self._db_data = data
    def db_delete_data(self, data):
        self._db_data = None
    
    def getPrimaryKey(self):
        return self._db_id

class DBDelete(object):

    vtType = 'delete'

    def __init__(self, id=None, what=None, objectId=None, parentObjId=None, parentObjType=None):
        self._db_id = id
        self._db_what = what
        self._db_objectId = objectId
        self._db_parentObjId = parentObjId
        self._db_parentObjType = parentObjType
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBDelete.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBDelete(id=self._db_id,
                      what=self._db_what,
                      objectId=self._db_objectId,
                      parentObjId=self._db_parentObjId,
                      parentObjType=self._db_parentObjType)
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
            if hasattr(self, 'db_objectId') and (self._db_what, self._db_objectId) in id_remap:
                cp._db_objectId = id_remap[(self._db_what, self._db_objectId)]
            if hasattr(self, 'db_parentObjId') and (self._db_parentObjType, self._db_parentObjId) in id_remap:
                cp._db_parentObjId = id_remap[(self._db_parentObjType, self._db_parentObjId)]
        
        # recreate indices and set flags
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBDelete()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'what' in class_dict:
            res = class_dict['what'](old_obj, trans_dict)
            new_obj.db_what = res
        elif hasattr(old_obj, 'db_what') and old_obj.db_what is not None:
            new_obj.db_what = old_obj.db_what
        if 'objectId' in class_dict:
            res = class_dict['objectId'](old_obj, trans_dict)
            new_obj.db_objectId = res
        elif hasattr(old_obj, 'db_objectId') and old_obj.db_objectId is not None:
            new_obj.db_objectId = old_obj.db_objectId
        if 'parentObjId' in class_dict:
            res = class_dict['parentObjId'](old_obj, trans_dict)
            new_obj.db_parentObjId = res
        elif hasattr(old_obj, 'db_parentObjId') and old_obj.db_parentObjId is not None:
            new_obj.db_parentObjId = old_obj.db_parentObjId
        if 'parentObjType' in class_dict:
            res = class_dict['parentObjType'](old_obj, trans_dict)
            new_obj.db_parentObjType = res
        elif hasattr(old_obj, 'db_parentObjType') and old_obj.db_parentObjType is not None:
            new_obj.db_parentObjType = old_obj.db_parentObjType
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
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
    
    def __get_db_what(self):
        return self._db_what
    def __set_db_what(self, what):
        self._db_what = what
        self.is_dirty = True
    db_what = property(__get_db_what, __set_db_what)
    def db_add_what(self, what):
        self._db_what = what
    def db_change_what(self, what):
        self._db_what = what
    def db_delete_what(self, what):
        self._db_what = None
    
    def __get_db_objectId(self):
        return self._db_objectId
    def __set_db_objectId(self, objectId):
        self._db_objectId = objectId
        self.is_dirty = True
    db_objectId = property(__get_db_objectId, __set_db_objectId)
    def db_add_objectId(self, objectId):
        self._db_objectId = objectId
    def db_change_objectId(self, objectId):
        self._db_objectId = objectId
    def db_delete_objectId(self, objectId):
        self._db_objectId = None
    
    def __get_db_parentObjId(self):
        return self._db_parentObjId
    def __set_db_parentObjId(self, parentObjId):
        self._db_parentObjId = parentObjId
        self.is_dirty = True
    db_parentObjId = property(__get_db_parentObjId, __set_db_parentObjId)
    def db_add_parentObjId(self, parentObjId):
        self._db_parentObjId = parentObjId
    def db_change_parentObjId(self, parentObjId):
        self._db_parentObjId = parentObjId
    def db_delete_parentObjId(self, parentObjId):
        self._db_parentObjId = None
    
    def __get_db_parentObjType(self):
        return self._db_parentObjType
    def __set_db_parentObjType(self, parentObjType):
        self._db_parentObjType = parentObjType
        self.is_dirty = True
    db_parentObjType = property(__get_db_parentObjType, __set_db_parentObjType)
    def db_add_parentObjType(self, parentObjType):
        self._db_parentObjType = parentObjType
    def db_change_parentObjType(self, parentObjType):
        self._db_parentObjType = parentObjType
    def db_delete_parentObjType(self, parentObjType):
        self._db_parentObjType = None
    
    def getPrimaryKey(self):
        return self._db_id

class DBVistrailVariable(object):

    vtType = 'vistrailVariable'

    def __init__(self, name=None, uuid=None, package=None, module=None, namespace=None, value=None):
        self._db_name = name
        self._db_uuid = uuid
        self._db_package = package
        self._db_module = module
        self._db_namespace = namespace
        self._db_value = value
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBVistrailVariable.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBVistrailVariable(name=self._db_name,
                                uuid=self._db_uuid,
                                package=self._db_package,
                                module=self._db_module,
                                namespace=self._db_namespace,
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
            new_obj = DBVistrailVariable()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'name' in class_dict:
            res = class_dict['name'](old_obj, trans_dict)
            new_obj.db_name = res
        elif hasattr(old_obj, 'db_name') and old_obj.db_name is not None:
            new_obj.db_name = old_obj.db_name
        if 'uuid' in class_dict:
            res = class_dict['uuid'](old_obj, trans_dict)
            new_obj.db_uuid = res
        elif hasattr(old_obj, 'db_uuid') and old_obj.db_uuid is not None:
            new_obj.db_uuid = old_obj.db_uuid
        if 'package' in class_dict:
            res = class_dict['package'](old_obj, trans_dict)
            new_obj.db_package = res
        elif hasattr(old_obj, 'db_package') and old_obj.db_package is not None:
            new_obj.db_package = old_obj.db_package
        if 'module' in class_dict:
            res = class_dict['module'](old_obj, trans_dict)
            new_obj.db_module = res
        elif hasattr(old_obj, 'db_module') and old_obj.db_module is not None:
            new_obj.db_module = old_obj.db_module
        if 'namespace' in class_dict:
            res = class_dict['namespace'](old_obj, trans_dict)
            new_obj.db_namespace = res
        elif hasattr(old_obj, 'db_namespace') and old_obj.db_namespace is not None:
            new_obj.db_namespace = old_obj.db_namespace
        if 'value' in class_dict:
            res = class_dict['value'](old_obj, trans_dict)
            new_obj.db_value = res
        elif hasattr(old_obj, 'db_value') and old_obj.db_value is not None:
            new_obj.db_value = old_obj.db_value
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        return [(self, parent[0], parent[1])]
    def db_deleted_children(self, remove=False):
        children = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        return False
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
    
    def __get_db_uuid(self):
        return self._db_uuid
    def __set_db_uuid(self, uuid):
        self._db_uuid = uuid
        self.is_dirty = True
    db_uuid = property(__get_db_uuid, __set_db_uuid)
    def db_add_uuid(self, uuid):
        self._db_uuid = uuid
    def db_change_uuid(self, uuid):
        self._db_uuid = uuid
    def db_delete_uuid(self, uuid):
        self._db_uuid = None
    
    def __get_db_package(self):
        return self._db_package
    def __set_db_package(self, package):
        self._db_package = package
        self.is_dirty = True
    db_package = property(__get_db_package, __set_db_package)
    def db_add_package(self, package):
        self._db_package = package
    def db_change_package(self, package):
        self._db_package = package
    def db_delete_package(self, package):
        self._db_package = None
    
    def __get_db_module(self):
        return self._db_module
    def __set_db_module(self, module):
        self._db_module = module
        self.is_dirty = True
    db_module = property(__get_db_module, __set_db_module)
    def db_add_module(self, module):
        self._db_module = module
    def db_change_module(self, module):
        self._db_module = module
    def db_delete_module(self, module):
        self._db_module = None
    
    def __get_db_namespace(self):
        return self._db_namespace
    def __set_db_namespace(self, namespace):
        self._db_namespace = namespace
        self.is_dirty = True
    db_namespace = property(__get_db_namespace, __set_db_namespace)
    def db_add_namespace(self, namespace):
        self._db_namespace = namespace
    def db_change_namespace(self, namespace):
        self._db_namespace = namespace
    def db_delete_namespace(self, namespace):
        self._db_namespace = None
    
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
        return self._db_name

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

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        children = []
        to_del = []
        for child in self.db_opm_account_ids:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
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

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        children = []
        if self._db_effect is not None:
            children.extend(self._db_effect.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                self._db_effect = None
        if self._db_role is not None:
            children.extend(self._db_role.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                self._db_role = None
        if self._db_cause is not None:
            children.extend(self._db_cause.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                self._db_cause = None
        to_del = []
        for child in self.db_accounts:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_account(child)
        to_del = []
        for child in self.db_opm_times:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
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
    


class DBModuleDescriptor(object):

    vtType = 'module_descriptor'

    def __init__(self, id=None, name=None, package=None, namespace=None, package_version=None, version=None, base_descriptor_id=None, portSpecs=None):
        self._db_id = id
        self._db_name = name
        self._db_package = package
        self._db_namespace = namespace
        self._db_package_version = package_version
        self._db_version = version
        self._db_base_descriptor_id = base_descriptor_id
        self.db_deleted_portSpecs = []
        self.db_portSpecs_id_index = {}
        self.db_portSpecs_name_index = {}
        if portSpecs is None:
            self._db_portSpecs = []
        else:
            self._db_portSpecs = portSpecs
            for v in self._db_portSpecs:
                self.db_portSpecs_id_index[v.db_id] = v
                self.db_portSpecs_name_index[(v.db_name,v.db_type)] = v
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBModuleDescriptor.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBModuleDescriptor(id=self._db_id,
                                name=self._db_name,
                                package=self._db_package,
                                namespace=self._db_namespace,
                                package_version=self._db_package_version,
                                version=self._db_version,
                                base_descriptor_id=self._db_base_descriptor_id)
        if self._db_portSpecs is None:
            cp._db_portSpecs = []
        else:
            cp._db_portSpecs = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_portSpecs]
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
            if hasattr(self, 'db_base_descriptor_id') and ('module_descriptor', self._db_base_descriptor_id) in id_remap:
                cp._db_base_descriptor_id = id_remap[('module_descriptor', self._db_base_descriptor_id)]
        
        # recreate indices and set flags
        cp.db_portSpecs_id_index = dict((v.db_id, v) for v in cp._db_portSpecs)
        cp.db_portSpecs_name_index = dict(((v.db_name,v.db_type), v) for v in cp._db_portSpecs)
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBModuleDescriptor()
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
        if 'package' in class_dict:
            res = class_dict['package'](old_obj, trans_dict)
            new_obj.db_package = res
        elif hasattr(old_obj, 'db_package') and old_obj.db_package is not None:
            new_obj.db_package = old_obj.db_package
        if 'namespace' in class_dict:
            res = class_dict['namespace'](old_obj, trans_dict)
            new_obj.db_namespace = res
        elif hasattr(old_obj, 'db_namespace') and old_obj.db_namespace is not None:
            new_obj.db_namespace = old_obj.db_namespace
        if 'package_version' in class_dict:
            res = class_dict['package_version'](old_obj, trans_dict)
            new_obj.db_package_version = res
        elif hasattr(old_obj, 'db_package_version') and old_obj.db_package_version is not None:
            new_obj.db_package_version = old_obj.db_package_version
        if 'version' in class_dict:
            res = class_dict['version'](old_obj, trans_dict)
            new_obj.db_version = res
        elif hasattr(old_obj, 'db_version') and old_obj.db_version is not None:
            new_obj.db_version = old_obj.db_version
        if 'base_descriptor_id' in class_dict:
            res = class_dict['base_descriptor_id'](old_obj, trans_dict)
            new_obj.db_base_descriptor_id = res
        elif hasattr(old_obj, 'db_base_descriptor_id') and old_obj.db_base_descriptor_id is not None:
            new_obj.db_base_descriptor_id = old_obj.db_base_descriptor_id
        if 'portSpecs' in class_dict:
            res = class_dict['portSpecs'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_portSpec(obj)
        elif hasattr(old_obj, 'db_portSpecs') and old_obj.db_portSpecs is not None:
            for obj in old_obj.db_portSpecs:
                new_obj.db_add_portSpec(DBPortSpec.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_portSpecs') and hasattr(new_obj, 'db_deleted_portSpecs'):
            for obj in old_obj.db_deleted_portSpecs:
                n_obj = DBPortSpec.update_version(obj, trans_dict)
                new_obj.db_deleted_portSpecs.append(n_obj)
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        children = []
        to_del = []
        for child in self.db_portSpecs:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_portSpec(child)
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_portSpecs)
        if remove:
            self.db_deleted_portSpecs = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        for child in self._db_portSpecs:
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
    
    def __get_db_package(self):
        return self._db_package
    def __set_db_package(self, package):
        self._db_package = package
        self.is_dirty = True
    db_package = property(__get_db_package, __set_db_package)
    def db_add_package(self, package):
        self._db_package = package
    def db_change_package(self, package):
        self._db_package = package
    def db_delete_package(self, package):
        self._db_package = None
    
    def __get_db_namespace(self):
        return self._db_namespace
    def __set_db_namespace(self, namespace):
        self._db_namespace = namespace
        self.is_dirty = True
    db_namespace = property(__get_db_namespace, __set_db_namespace)
    def db_add_namespace(self, namespace):
        self._db_namespace = namespace
    def db_change_namespace(self, namespace):
        self._db_namespace = namespace
    def db_delete_namespace(self, namespace):
        self._db_namespace = None
    
    def __get_db_package_version(self):
        return self._db_package_version
    def __set_db_package_version(self, package_version):
        self._db_package_version = package_version
        self.is_dirty = True
    db_package_version = property(__get_db_package_version, __set_db_package_version)
    def db_add_package_version(self, package_version):
        self._db_package_version = package_version
    def db_change_package_version(self, package_version):
        self._db_package_version = package_version
    def db_delete_package_version(self, package_version):
        self._db_package_version = None
    
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
    
    def __get_db_base_descriptor_id(self):
        return self._db_base_descriptor_id
    def __set_db_base_descriptor_id(self, base_descriptor_id):
        self._db_base_descriptor_id = base_descriptor_id
        self.is_dirty = True
    db_base_descriptor_id = property(__get_db_base_descriptor_id, __set_db_base_descriptor_id)
    def db_add_base_descriptor_id(self, base_descriptor_id):
        self._db_base_descriptor_id = base_descriptor_id
    def db_change_base_descriptor_id(self, base_descriptor_id):
        self._db_base_descriptor_id = base_descriptor_id
    def db_delete_base_descriptor_id(self, base_descriptor_id):
        self._db_base_descriptor_id = None
    
    def __get_db_portSpecs(self):
        return self._db_portSpecs
    def __set_db_portSpecs(self, portSpecs):
        self._db_portSpecs = portSpecs
        self.is_dirty = True
    db_portSpecs = property(__get_db_portSpecs, __set_db_portSpecs)
    def db_get_portSpecs(self):
        return self._db_portSpecs
    def db_add_portSpec(self, portSpec):
        self.is_dirty = True
        self._db_portSpecs.append(portSpec)
        self.db_portSpecs_id_index[portSpec.db_id] = portSpec
        self.db_portSpecs_name_index[(portSpec.db_name,portSpec.db_type)] = portSpec
    def db_change_portSpec(self, portSpec):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_portSpecs)):
            if self._db_portSpecs[i].db_id == portSpec.db_id:
                self._db_portSpecs[i] = portSpec
                found = True
                break
        if not found:
            self._db_portSpecs.append(portSpec)
        self.db_portSpecs_id_index[portSpec.db_id] = portSpec
        self.db_portSpecs_name_index[(portSpec.db_name,portSpec.db_type)] = portSpec
    def db_delete_portSpec(self, portSpec):
        self.is_dirty = True
        for i in xrange(len(self._db_portSpecs)):
            if self._db_portSpecs[i].db_id == portSpec.db_id:
                if not self._db_portSpecs[i].is_new:
                    self.db_deleted_portSpecs.append(self._db_portSpecs[i])
                del self._db_portSpecs[i]
                break
        del self.db_portSpecs_id_index[portSpec.db_id]
        del self.db_portSpecs_name_index[(portSpec.db_name,portSpec.db_type)]
    def db_get_portSpec(self, key):
        for i in xrange(len(self._db_portSpecs)):
            if self._db_portSpecs[i].db_id == key:
                return self._db_portSpecs[i]
        return None
    def db_get_portSpec_by_id(self, key):
        return self.db_portSpecs_id_index[key]
    def db_has_portSpec_with_id(self, key):
        return key in self.db_portSpecs_id_index
    def db_get_portSpec_by_name(self, key):
        return self.db_portSpecs_name_index[key]
    def db_has_portSpec_with_name(self, key):
        return key in self.db_portSpecs_name_index
    
    def getPrimaryKey(self):
        return self._db_id

class DBTag(object):

    vtType = 'tag'

    def __init__(self, id=None, name=None):
        self._db_id = id
        self._db_name = name
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBTag.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBTag(id=self._db_id,
                   name=self._db_name)
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
            if hasattr(self, 'db_id') and ('action', self._db_id) in id_remap:
                cp._db_id = id_remap[('action', self._db_id)]
        
        # recreate indices and set flags
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBTag()
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
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
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
    
    def getPrimaryKey(self):
        return self._db_id

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

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
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
    


class DBProvDocument(object):

    vtType = 'prov_document'

    def __init__(self, prov_entitys=None, prov_activitys=None, prov_agents=None, vt_connections=None, prov_usages=None, prov_generations=None, prov_associations=None):
        self.db_deleted_prov_entitys = []
        self.db_prov_entitys_id_index = {}
        if prov_entitys is None:
            self._db_prov_entitys = []
        else:
            self._db_prov_entitys = prov_entitys
            for v in self._db_prov_entitys:
                self.db_prov_entitys_id_index[v.db_id] = v
        self.db_deleted_prov_activitys = []
        self.db_prov_activitys_id_index = {}
        if prov_activitys is None:
            self._db_prov_activitys = []
        else:
            self._db_prov_activitys = prov_activitys
            for v in self._db_prov_activitys:
                self.db_prov_activitys_id_index[v.db_id] = v
        self.db_deleted_prov_agents = []
        self.db_prov_agents_id_index = {}
        if prov_agents is None:
            self._db_prov_agents = []
        else:
            self._db_prov_agents = prov_agents
            for v in self._db_prov_agents:
                self.db_prov_agents_id_index[v.db_id] = v
        self.db_deleted_vt_connections = []
        self.db_vt_connections_id_index = {}
        if vt_connections is None:
            self._db_vt_connections = []
        else:
            self._db_vt_connections = vt_connections
            for v in self._db_vt_connections:
                self.db_vt_connections_id_index[v.db_id] = v
        self.db_deleted_prov_usages = []
        if prov_usages is None:
            self._db_prov_usages = []
        else:
            self._db_prov_usages = prov_usages
        self.db_deleted_prov_generations = []
        if prov_generations is None:
            self._db_prov_generations = []
        else:
            self._db_prov_generations = prov_generations
        self.db_deleted_prov_associations = []
        if prov_associations is None:
            self._db_prov_associations = []
        else:
            self._db_prov_associations = prov_associations
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBProvDocument.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBProvDocument()
        if self._db_prov_entitys is None:
            cp._db_prov_entitys = []
        else:
            cp._db_prov_entitys = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_prov_entitys]
        if self._db_prov_activitys is None:
            cp._db_prov_activitys = []
        else:
            cp._db_prov_activitys = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_prov_activitys]
        if self._db_prov_agents is None:
            cp._db_prov_agents = []
        else:
            cp._db_prov_agents = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_prov_agents]
        if self._db_vt_connections is None:
            cp._db_vt_connections = []
        else:
            cp._db_vt_connections = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_vt_connections]
        if self._db_prov_usages is None:
            cp._db_prov_usages = []
        else:
            cp._db_prov_usages = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_prov_usages]
        if self._db_prov_generations is None:
            cp._db_prov_generations = []
        else:
            cp._db_prov_generations = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_prov_generations]
        if self._db_prov_associations is None:
            cp._db_prov_associations = []
        else:
            cp._db_prov_associations = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_prov_associations]
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
        
        # recreate indices and set flags
        cp.db_prov_entitys_id_index = dict((v.db_id, v) for v in cp._db_prov_entitys)
        cp.db_prov_activitys_id_index = dict((v.db_id, v) for v in cp._db_prov_activitys)
        cp.db_prov_agents_id_index = dict((v.db_id, v) for v in cp._db_prov_agents)
        cp.db_vt_connections_id_index = dict((v.db_id, v) for v in cp._db_vt_connections)
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBProvDocument()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'prov_entitys' in class_dict:
            res = class_dict['prov_entitys'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_prov_entity(obj)
        elif hasattr(old_obj, 'db_prov_entitys') and old_obj.db_prov_entitys is not None:
            for obj in old_obj.db_prov_entitys:
                new_obj.db_add_prov_entity(DBProvEntity.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_prov_entitys') and hasattr(new_obj, 'db_deleted_prov_entitys'):
            for obj in old_obj.db_deleted_prov_entitys:
                n_obj = DBProvEntity.update_version(obj, trans_dict)
                new_obj.db_deleted_prov_entitys.append(n_obj)
        if 'prov_activitys' in class_dict:
            res = class_dict['prov_activitys'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_prov_activity(obj)
        elif hasattr(old_obj, 'db_prov_activitys') and old_obj.db_prov_activitys is not None:
            for obj in old_obj.db_prov_activitys:
                new_obj.db_add_prov_activity(DBProvActivity.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_prov_activitys') and hasattr(new_obj, 'db_deleted_prov_activitys'):
            for obj in old_obj.db_deleted_prov_activitys:
                n_obj = DBProvActivity.update_version(obj, trans_dict)
                new_obj.db_deleted_prov_activitys.append(n_obj)
        if 'prov_agents' in class_dict:
            res = class_dict['prov_agents'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_prov_agent(obj)
        elif hasattr(old_obj, 'db_prov_agents') and old_obj.db_prov_agents is not None:
            for obj in old_obj.db_prov_agents:
                new_obj.db_add_prov_agent(DBProvAgent.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_prov_agents') and hasattr(new_obj, 'db_deleted_prov_agents'):
            for obj in old_obj.db_deleted_prov_agents:
                n_obj = DBProvAgent.update_version(obj, trans_dict)
                new_obj.db_deleted_prov_agents.append(n_obj)
        if 'vt_connections' in class_dict:
            res = class_dict['vt_connections'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_vt_connection(obj)
        elif hasattr(old_obj, 'db_vt_connections') and old_obj.db_vt_connections is not None:
            for obj in old_obj.db_vt_connections:
                new_obj.db_add_vt_connection(DBVtConnection.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_vt_connections') and hasattr(new_obj, 'db_deleted_vt_connections'):
            for obj in old_obj.db_deleted_vt_connections:
                n_obj = DBVtConnection.update_version(obj, trans_dict)
                new_obj.db_deleted_vt_connections.append(n_obj)
        if 'prov_usages' in class_dict:
            res = class_dict['prov_usages'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_prov_usage(obj)
        elif hasattr(old_obj, 'db_prov_usages') and old_obj.db_prov_usages is not None:
            for obj in old_obj.db_prov_usages:
                new_obj.db_add_prov_usage(DBProvUsage.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_prov_usages') and hasattr(new_obj, 'db_deleted_prov_usages'):
            for obj in old_obj.db_deleted_prov_usages:
                n_obj = DBProvUsage.update_version(obj, trans_dict)
                new_obj.db_deleted_prov_usages.append(n_obj)
        if 'prov_generations' in class_dict:
            res = class_dict['prov_generations'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_prov_generation(obj)
        elif hasattr(old_obj, 'db_prov_generations') and old_obj.db_prov_generations is not None:
            for obj in old_obj.db_prov_generations:
                new_obj.db_add_prov_generation(DBProvGeneration.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_prov_generations') and hasattr(new_obj, 'db_deleted_prov_generations'):
            for obj in old_obj.db_deleted_prov_generations:
                n_obj = DBProvGeneration.update_version(obj, trans_dict)
                new_obj.db_deleted_prov_generations.append(n_obj)
        if 'prov_associations' in class_dict:
            res = class_dict['prov_associations'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_prov_association(obj)
        elif hasattr(old_obj, 'db_prov_associations') and old_obj.db_prov_associations is not None:
            for obj in old_obj.db_prov_associations:
                new_obj.db_add_prov_association(DBProvAssociation.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_prov_associations') and hasattr(new_obj, 'db_deleted_prov_associations'):
            for obj in old_obj.db_deleted_prov_associations:
                n_obj = DBProvAssociation.update_version(obj, trans_dict)
                new_obj.db_deleted_prov_associations.append(n_obj)
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        children = []
        to_del = []
        for child in self.db_prov_entitys:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_prov_entity(child)
        to_del = []
        for child in self.db_prov_activitys:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_prov_activity(child)
        to_del = []
        for child in self.db_prov_agents:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_prov_agent(child)
        to_del = []
        for child in self.db_vt_connections:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_vt_connection(child)
        to_del = []
        for child in self.db_prov_usages:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_prov_usage(child)
        to_del = []
        for child in self.db_prov_generations:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_prov_generation(child)
        to_del = []
        for child in self.db_prov_associations:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_prov_association(child)
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_prov_entitys)
        children.extend(self.db_deleted_prov_activitys)
        children.extend(self.db_deleted_prov_agents)
        children.extend(self.db_deleted_vt_connections)
        children.extend(self.db_deleted_prov_usages)
        children.extend(self.db_deleted_prov_generations)
        children.extend(self.db_deleted_prov_associations)
        if remove:
            self.db_deleted_prov_entitys = []
            self.db_deleted_prov_activitys = []
            self.db_deleted_prov_agents = []
            self.db_deleted_vt_connections = []
            self.db_deleted_prov_usages = []
            self.db_deleted_prov_generations = []
            self.db_deleted_prov_associations = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        for child in self._db_prov_entitys:
            if child.has_changes():
                return True
        for child in self._db_prov_activitys:
            if child.has_changes():
                return True
        for child in self._db_prov_agents:
            if child.has_changes():
                return True
        for child in self._db_vt_connections:
            if child.has_changes():
                return True
        for child in self._db_prov_usages:
            if child.has_changes():
                return True
        for child in self._db_prov_generations:
            if child.has_changes():
                return True
        for child in self._db_prov_associations:
            if child.has_changes():
                return True
        return False
    def __get_db_prov_entitys(self):
        return self._db_prov_entitys
    def __set_db_prov_entitys(self, prov_entitys):
        self._db_prov_entitys = prov_entitys
        self.is_dirty = True
    db_prov_entitys = property(__get_db_prov_entitys, __set_db_prov_entitys)
    def db_get_prov_entitys(self):
        return self._db_prov_entitys
    def db_add_prov_entity(self, prov_entity):
        self.is_dirty = True
        self._db_prov_entitys.append(prov_entity)
        self.db_prov_entitys_id_index[prov_entity.db_id] = prov_entity
    def db_change_prov_entity(self, prov_entity):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_prov_entitys)):
            if self._db_prov_entitys[i].db_id == prov_entity.db_id:
                self._db_prov_entitys[i] = prov_entity
                found = True
                break
        if not found:
            self._db_prov_entitys.append(prov_entity)
        self.db_prov_entitys_id_index[prov_entity.db_id] = prov_entity
    def db_delete_prov_entity(self, prov_entity):
        self.is_dirty = True
        for i in xrange(len(self._db_prov_entitys)):
            if self._db_prov_entitys[i].db_id == prov_entity.db_id:
                if not self._db_prov_entitys[i].is_new:
                    self.db_deleted_prov_entitys.append(self._db_prov_entitys[i])
                del self._db_prov_entitys[i]
                break
        del self.db_prov_entitys_id_index[prov_entity.db_id]
    def db_get_prov_entity(self, key):
        for i in xrange(len(self._db_prov_entitys)):
            if self._db_prov_entitys[i].db_id == key:
                return self._db_prov_entitys[i]
        return None
    def db_get_prov_entity_by_id(self, key):
        return self.db_prov_entitys_id_index[key]
    def db_has_prov_entity_with_id(self, key):
        return key in self.db_prov_entitys_id_index
    
    def __get_db_prov_activitys(self):
        return self._db_prov_activitys
    def __set_db_prov_activitys(self, prov_activitys):
        self._db_prov_activitys = prov_activitys
        self.is_dirty = True
    db_prov_activitys = property(__get_db_prov_activitys, __set_db_prov_activitys)
    def db_get_prov_activitys(self):
        return self._db_prov_activitys
    def db_add_prov_activity(self, prov_activity):
        self.is_dirty = True
        self._db_prov_activitys.append(prov_activity)
        self.db_prov_activitys_id_index[prov_activity.db_id] = prov_activity
    def db_change_prov_activity(self, prov_activity):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_prov_activitys)):
            if self._db_prov_activitys[i].db_id == prov_activity.db_id:
                self._db_prov_activitys[i] = prov_activity
                found = True
                break
        if not found:
            self._db_prov_activitys.append(prov_activity)
        self.db_prov_activitys_id_index[prov_activity.db_id] = prov_activity
    def db_delete_prov_activity(self, prov_activity):
        self.is_dirty = True
        for i in xrange(len(self._db_prov_activitys)):
            if self._db_prov_activitys[i].db_id == prov_activity.db_id:
                if not self._db_prov_activitys[i].is_new:
                    self.db_deleted_prov_activitys.append(self._db_prov_activitys[i])
                del self._db_prov_activitys[i]
                break
        del self.db_prov_activitys_id_index[prov_activity.db_id]
    def db_get_prov_activity(self, key):
        for i in xrange(len(self._db_prov_activitys)):
            if self._db_prov_activitys[i].db_id == key:
                return self._db_prov_activitys[i]
        return None
    def db_get_prov_activity_by_id(self, key):
        return self.db_prov_activitys_id_index[key]
    def db_has_prov_activity_with_id(self, key):
        return key in self.db_prov_activitys_id_index
    
    def __get_db_prov_agents(self):
        return self._db_prov_agents
    def __set_db_prov_agents(self, prov_agents):
        self._db_prov_agents = prov_agents
        self.is_dirty = True
    db_prov_agents = property(__get_db_prov_agents, __set_db_prov_agents)
    def db_get_prov_agents(self):
        return self._db_prov_agents
    def db_add_prov_agent(self, prov_agent):
        self.is_dirty = True
        self._db_prov_agents.append(prov_agent)
        self.db_prov_agents_id_index[prov_agent.db_id] = prov_agent
    def db_change_prov_agent(self, prov_agent):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_prov_agents)):
            if self._db_prov_agents[i].db_id == prov_agent.db_id:
                self._db_prov_agents[i] = prov_agent
                found = True
                break
        if not found:
            self._db_prov_agents.append(prov_agent)
        self.db_prov_agents_id_index[prov_agent.db_id] = prov_agent
    def db_delete_prov_agent(self, prov_agent):
        self.is_dirty = True
        for i in xrange(len(self._db_prov_agents)):
            if self._db_prov_agents[i].db_id == prov_agent.db_id:
                if not self._db_prov_agents[i].is_new:
                    self.db_deleted_prov_agents.append(self._db_prov_agents[i])
                del self._db_prov_agents[i]
                break
        del self.db_prov_agents_id_index[prov_agent.db_id]
    def db_get_prov_agent(self, key):
        for i in xrange(len(self._db_prov_agents)):
            if self._db_prov_agents[i].db_id == key:
                return self._db_prov_agents[i]
        return None
    def db_get_prov_agent_by_id(self, key):
        return self.db_prov_agents_id_index[key]
    def db_has_prov_agent_with_id(self, key):
        return key in self.db_prov_agents_id_index
    
    def __get_db_vt_connections(self):
        return self._db_vt_connections
    def __set_db_vt_connections(self, vt_connections):
        self._db_vt_connections = vt_connections
        self.is_dirty = True
    db_vt_connections = property(__get_db_vt_connections, __set_db_vt_connections)
    def db_get_vt_connections(self):
        return self._db_vt_connections
    def db_add_vt_connection(self, vt_connection):
        self.is_dirty = True
        self._db_vt_connections.append(vt_connection)
        self.db_vt_connections_id_index[vt_connection.db_id] = vt_connection
    def db_change_vt_connection(self, vt_connection):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_vt_connections)):
            if self._db_vt_connections[i].db_id == vt_connection.db_id:
                self._db_vt_connections[i] = vt_connection
                found = True
                break
        if not found:
            self._db_vt_connections.append(vt_connection)
        self.db_vt_connections_id_index[vt_connection.db_id] = vt_connection
    def db_delete_vt_connection(self, vt_connection):
        self.is_dirty = True
        for i in xrange(len(self._db_vt_connections)):
            if self._db_vt_connections[i].db_id == vt_connection.db_id:
                if not self._db_vt_connections[i].is_new:
                    self.db_deleted_vt_connections.append(self._db_vt_connections[i])
                del self._db_vt_connections[i]
                break
        del self.db_vt_connections_id_index[vt_connection.db_id]
    def db_get_vt_connection(self, key):
        for i in xrange(len(self._db_vt_connections)):
            if self._db_vt_connections[i].db_id == key:
                return self._db_vt_connections[i]
        return None
    def db_get_vt_connection_by_id(self, key):
        return self.db_vt_connections_id_index[key]
    def db_has_vt_connection_with_id(self, key):
        return key in self.db_vt_connections_id_index
    
    def __get_db_prov_usages(self):
        return self._db_prov_usages
    def __set_db_prov_usages(self, prov_usages):
        self._db_prov_usages = prov_usages
        self.is_dirty = True
    db_prov_usages = property(__get_db_prov_usages, __set_db_prov_usages)
    def db_get_prov_usages(self):
        return self._db_prov_usages
    def db_add_prov_usage(self, prov_usage):
        self.is_dirty = True
        self._db_prov_usages.append(prov_usage)
    def db_change_prov_usage(self, prov_usage):
        self.is_dirty = True
        self._db_prov_usages.append(prov_usage)
    def db_delete_prov_usage(self, prov_usage):
        self.is_dirty = True
        raise Exception('Cannot delete a non-keyed object')
    def db_get_prov_usage(self, key):
        return None
    
    def __get_db_prov_generations(self):
        return self._db_prov_generations
    def __set_db_prov_generations(self, prov_generations):
        self._db_prov_generations = prov_generations
        self.is_dirty = True
    db_prov_generations = property(__get_db_prov_generations, __set_db_prov_generations)
    def db_get_prov_generations(self):
        return self._db_prov_generations
    def db_add_prov_generation(self, prov_generation):
        self.is_dirty = True
        self._db_prov_generations.append(prov_generation)
    def db_change_prov_generation(self, prov_generation):
        self.is_dirty = True
        self._db_prov_generations.append(prov_generation)
    def db_delete_prov_generation(self, prov_generation):
        self.is_dirty = True
        raise Exception('Cannot delete a non-keyed object')
    def db_get_prov_generation(self, key):
        return None
    
    def __get_db_prov_associations(self):
        return self._db_prov_associations
    def __set_db_prov_associations(self, prov_associations):
        self._db_prov_associations = prov_associations
        self.is_dirty = True
    db_prov_associations = property(__get_db_prov_associations, __set_db_prov_associations)
    def db_get_prov_associations(self):
        return self._db_prov_associations
    def db_add_prov_association(self, prov_association):
        self.is_dirty = True
        self._db_prov_associations.append(prov_association)
    def db_change_prov_association(self, prov_association):
        self.is_dirty = True
        self._db_prov_associations.append(prov_association)
    def db_delete_prov_association(self, prov_association):
        self.is_dirty = True
        raise Exception('Cannot delete a non-keyed object')
    def db_get_prov_association(self, key):
        return None
    


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

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        children = []
        to_del = []
        for child in self.db_processs:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
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

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
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
    


class DBPortSpecItem(object):

    vtType = 'portSpecItem'

    def __init__(self, id=None, pos=None, module=None, package=None, namespace=None, label=None, default=None, values=None, entry_type=None):
        self._db_id = id
        self._db_pos = pos
        self._db_module = module
        self._db_package = package
        self._db_namespace = namespace
        self._db_label = label
        self._db_default = default
        self._db_values = values
        self._db_entry_type = entry_type
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBPortSpecItem.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBPortSpecItem(id=self._db_id,
                            pos=self._db_pos,
                            module=self._db_module,
                            package=self._db_package,
                            namespace=self._db_namespace,
                            label=self._db_label,
                            default=self._db_default,
                            values=self._db_values,
                            entry_type=self._db_entry_type)
        
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
            new_obj = DBPortSpecItem()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'pos' in class_dict:
            res = class_dict['pos'](old_obj, trans_dict)
            new_obj.db_pos = res
        elif hasattr(old_obj, 'db_pos') and old_obj.db_pos is not None:
            new_obj.db_pos = old_obj.db_pos
        if 'module' in class_dict:
            res = class_dict['module'](old_obj, trans_dict)
            new_obj.db_module = res
        elif hasattr(old_obj, 'db_module') and old_obj.db_module is not None:
            new_obj.db_module = old_obj.db_module
        if 'package' in class_dict:
            res = class_dict['package'](old_obj, trans_dict)
            new_obj.db_package = res
        elif hasattr(old_obj, 'db_package') and old_obj.db_package is not None:
            new_obj.db_package = old_obj.db_package
        if 'namespace' in class_dict:
            res = class_dict['namespace'](old_obj, trans_dict)
            new_obj.db_namespace = res
        elif hasattr(old_obj, 'db_namespace') and old_obj.db_namespace is not None:
            new_obj.db_namespace = old_obj.db_namespace
        if 'label' in class_dict:
            res = class_dict['label'](old_obj, trans_dict)
            new_obj.db_label = res
        elif hasattr(old_obj, 'db_label') and old_obj.db_label is not None:
            new_obj.db_label = old_obj.db_label
        if 'default' in class_dict:
            res = class_dict['default'](old_obj, trans_dict)
            new_obj.db_default = res
        elif hasattr(old_obj, 'db_default') and old_obj.db_default is not None:
            new_obj.db_default = old_obj.db_default
        if 'values' in class_dict:
            res = class_dict['values'](old_obj, trans_dict)
            new_obj.db_values = res
        elif hasattr(old_obj, 'db_values') and old_obj.db_values is not None:
            new_obj.db_values = old_obj.db_values
        if 'entry_type' in class_dict:
            res = class_dict['entry_type'](old_obj, trans_dict)
            new_obj.db_entry_type = res
        elif hasattr(old_obj, 'db_entry_type') and old_obj.db_entry_type is not None:
            new_obj.db_entry_type = old_obj.db_entry_type
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
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
    
    def __get_db_pos(self):
        return self._db_pos
    def __set_db_pos(self, pos):
        self._db_pos = pos
        self.is_dirty = True
    db_pos = property(__get_db_pos, __set_db_pos)
    def db_add_pos(self, pos):
        self._db_pos = pos
    def db_change_pos(self, pos):
        self._db_pos = pos
    def db_delete_pos(self, pos):
        self._db_pos = None
    
    def __get_db_module(self):
        return self._db_module
    def __set_db_module(self, module):
        self._db_module = module
        self.is_dirty = True
    db_module = property(__get_db_module, __set_db_module)
    def db_add_module(self, module):
        self._db_module = module
    def db_change_module(self, module):
        self._db_module = module
    def db_delete_module(self, module):
        self._db_module = None
    
    def __get_db_package(self):
        return self._db_package
    def __set_db_package(self, package):
        self._db_package = package
        self.is_dirty = True
    db_package = property(__get_db_package, __set_db_package)
    def db_add_package(self, package):
        self._db_package = package
    def db_change_package(self, package):
        self._db_package = package
    def db_delete_package(self, package):
        self._db_package = None
    
    def __get_db_namespace(self):
        return self._db_namespace
    def __set_db_namespace(self, namespace):
        self._db_namespace = namespace
        self.is_dirty = True
    db_namespace = property(__get_db_namespace, __set_db_namespace)
    def db_add_namespace(self, namespace):
        self._db_namespace = namespace
    def db_change_namespace(self, namespace):
        self._db_namespace = namespace
    def db_delete_namespace(self, namespace):
        self._db_namespace = None
    
    def __get_db_label(self):
        return self._db_label
    def __set_db_label(self, label):
        self._db_label = label
        self.is_dirty = True
    db_label = property(__get_db_label, __set_db_label)
    def db_add_label(self, label):
        self._db_label = label
    def db_change_label(self, label):
        self._db_label = label
    def db_delete_label(self, label):
        self._db_label = None
    
    def __get_db_default(self):
        return self._db_default
    def __set_db_default(self, default):
        self._db_default = default
        self.is_dirty = True
    db_default = property(__get_db_default, __set_db_default)
    def db_add_default(self, default):
        self._db_default = default
    def db_change_default(self, default):
        self._db_default = default
    def db_delete_default(self, default):
        self._db_default = None
    
    def __get_db_values(self):
        return self._db_values
    def __set_db_values(self, values):
        self._db_values = values
        self.is_dirty = True
    db_values = property(__get_db_values, __set_db_values)
    def db_add_values(self, values):
        self._db_values = values
    def db_change_values(self, values):
        self._db_values = values
    def db_delete_values(self, values):
        self._db_values = None
    
    def __get_db_entry_type(self):
        return self._db_entry_type
    def __set_db_entry_type(self, entry_type):
        self._db_entry_type = entry_type
        self.is_dirty = True
    db_entry_type = property(__get_db_entry_type, __set_db_entry_type)
    def db_add_entry_type(self, entry_type):
        self._db_entry_type = entry_type
    def db_change_entry_type(self, entry_type):
        self._db_entry_type = entry_type
    def db_delete_entry_type(self, entry_type):
        self._db_entry_type = None
    
    def getPrimaryKey(self):
        return self._db_id

class DBMashupComponent(object):

    vtType = 'mashup_component'

    def __init__(self, id=None, vtid=None, vttype=None, vtparent_type=None, vtparent_id=None, vtpos=None, vtmid=None, pos=None, type=None, val=None, minVal=None, maxVal=None, stepSize=None, strvaluelist=None, widget=None, seq=None, parent=None):
        self._db_id = id
        self._db_vtid = vtid
        self._db_vttype = vttype
        self._db_vtparent_type = vtparent_type
        self._db_vtparent_id = vtparent_id
        self._db_vtpos = vtpos
        self._db_vtmid = vtmid
        self._db_pos = pos
        self._db_type = type
        self._db_val = val
        self._db_minVal = minVal
        self._db_maxVal = maxVal
        self._db_stepSize = stepSize
        self._db_strvaluelist = strvaluelist
        self._db_widget = widget
        self._db_seq = seq
        self._db_parent = parent
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBMashupComponent.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBMashupComponent(id=self._db_id,
                               vtid=self._db_vtid,
                               vttype=self._db_vttype,
                               vtparent_type=self._db_vtparent_type,
                               vtparent_id=self._db_vtparent_id,
                               vtpos=self._db_vtpos,
                               vtmid=self._db_vtmid,
                               pos=self._db_pos,
                               type=self._db_type,
                               val=self._db_val,
                               minVal=self._db_minVal,
                               maxVal=self._db_maxVal,
                               stepSize=self._db_stepSize,
                               strvaluelist=self._db_strvaluelist,
                               widget=self._db_widget,
                               seq=self._db_seq,
                               parent=self._db_parent)
        
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
            new_obj = DBMashupComponent()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'vtid' in class_dict:
            res = class_dict['vtid'](old_obj, trans_dict)
            new_obj.db_vtid = res
        elif hasattr(old_obj, 'db_vtid') and old_obj.db_vtid is not None:
            new_obj.db_vtid = old_obj.db_vtid
        if 'vttype' in class_dict:
            res = class_dict['vttype'](old_obj, trans_dict)
            new_obj.db_vttype = res
        elif hasattr(old_obj, 'db_vttype') and old_obj.db_vttype is not None:
            new_obj.db_vttype = old_obj.db_vttype
        if 'vtparent_type' in class_dict:
            res = class_dict['vtparent_type'](old_obj, trans_dict)
            new_obj.db_vtparent_type = res
        elif hasattr(old_obj, 'db_vtparent_type') and old_obj.db_vtparent_type is not None:
            new_obj.db_vtparent_type = old_obj.db_vtparent_type
        if 'vtparent_id' in class_dict:
            res = class_dict['vtparent_id'](old_obj, trans_dict)
            new_obj.db_vtparent_id = res
        elif hasattr(old_obj, 'db_vtparent_id') and old_obj.db_vtparent_id is not None:
            new_obj.db_vtparent_id = old_obj.db_vtparent_id
        if 'vtpos' in class_dict:
            res = class_dict['vtpos'](old_obj, trans_dict)
            new_obj.db_vtpos = res
        elif hasattr(old_obj, 'db_vtpos') and old_obj.db_vtpos is not None:
            new_obj.db_vtpos = old_obj.db_vtpos
        if 'vtmid' in class_dict:
            res = class_dict['vtmid'](old_obj, trans_dict)
            new_obj.db_vtmid = res
        elif hasattr(old_obj, 'db_vtmid') and old_obj.db_vtmid is not None:
            new_obj.db_vtmid = old_obj.db_vtmid
        if 'pos' in class_dict:
            res = class_dict['pos'](old_obj, trans_dict)
            new_obj.db_pos = res
        elif hasattr(old_obj, 'db_pos') and old_obj.db_pos is not None:
            new_obj.db_pos = old_obj.db_pos
        if 'type' in class_dict:
            res = class_dict['type'](old_obj, trans_dict)
            new_obj.db_type = res
        elif hasattr(old_obj, 'db_type') and old_obj.db_type is not None:
            new_obj.db_type = old_obj.db_type
        if 'val' in class_dict:
            res = class_dict['val'](old_obj, trans_dict)
            new_obj.db_val = res
        elif hasattr(old_obj, 'db_val') and old_obj.db_val is not None:
            new_obj.db_val = old_obj.db_val
        if 'minVal' in class_dict:
            res = class_dict['minVal'](old_obj, trans_dict)
            new_obj.db_minVal = res
        elif hasattr(old_obj, 'db_minVal') and old_obj.db_minVal is not None:
            new_obj.db_minVal = old_obj.db_minVal
        if 'maxVal' in class_dict:
            res = class_dict['maxVal'](old_obj, trans_dict)
            new_obj.db_maxVal = res
        elif hasattr(old_obj, 'db_maxVal') and old_obj.db_maxVal is not None:
            new_obj.db_maxVal = old_obj.db_maxVal
        if 'stepSize' in class_dict:
            res = class_dict['stepSize'](old_obj, trans_dict)
            new_obj.db_stepSize = res
        elif hasattr(old_obj, 'db_stepSize') and old_obj.db_stepSize is not None:
            new_obj.db_stepSize = old_obj.db_stepSize
        if 'strvaluelist' in class_dict:
            res = class_dict['strvaluelist'](old_obj, trans_dict)
            new_obj.db_strvaluelist = res
        elif hasattr(old_obj, 'db_strvaluelist') and old_obj.db_strvaluelist is not None:
            new_obj.db_strvaluelist = old_obj.db_strvaluelist
        if 'widget' in class_dict:
            res = class_dict['widget'](old_obj, trans_dict)
            new_obj.db_widget = res
        elif hasattr(old_obj, 'db_widget') and old_obj.db_widget is not None:
            new_obj.db_widget = old_obj.db_widget
        if 'seq' in class_dict:
            res = class_dict['seq'](old_obj, trans_dict)
            new_obj.db_seq = res
        elif hasattr(old_obj, 'db_seq') and old_obj.db_seq is not None:
            new_obj.db_seq = old_obj.db_seq
        if 'parent' in class_dict:
            res = class_dict['parent'](old_obj, trans_dict)
            new_obj.db_parent = res
        elif hasattr(old_obj, 'db_parent') and old_obj.db_parent is not None:
            new_obj.db_parent = old_obj.db_parent
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
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
    
    def __get_db_vtid(self):
        return self._db_vtid
    def __set_db_vtid(self, vtid):
        self._db_vtid = vtid
        self.is_dirty = True
    db_vtid = property(__get_db_vtid, __set_db_vtid)
    def db_add_vtid(self, vtid):
        self._db_vtid = vtid
    def db_change_vtid(self, vtid):
        self._db_vtid = vtid
    def db_delete_vtid(self, vtid):
        self._db_vtid = None
    
    def __get_db_vttype(self):
        return self._db_vttype
    def __set_db_vttype(self, vttype):
        self._db_vttype = vttype
        self.is_dirty = True
    db_vttype = property(__get_db_vttype, __set_db_vttype)
    def db_add_vttype(self, vttype):
        self._db_vttype = vttype
    def db_change_vttype(self, vttype):
        self._db_vttype = vttype
    def db_delete_vttype(self, vttype):
        self._db_vttype = None
    
    def __get_db_vtparent_type(self):
        return self._db_vtparent_type
    def __set_db_vtparent_type(self, vtparent_type):
        self._db_vtparent_type = vtparent_type
        self.is_dirty = True
    db_vtparent_type = property(__get_db_vtparent_type, __set_db_vtparent_type)
    def db_add_vtparent_type(self, vtparent_type):
        self._db_vtparent_type = vtparent_type
    def db_change_vtparent_type(self, vtparent_type):
        self._db_vtparent_type = vtparent_type
    def db_delete_vtparent_type(self, vtparent_type):
        self._db_vtparent_type = None
    
    def __get_db_vtparent_id(self):
        return self._db_vtparent_id
    def __set_db_vtparent_id(self, vtparent_id):
        self._db_vtparent_id = vtparent_id
        self.is_dirty = True
    db_vtparent_id = property(__get_db_vtparent_id, __set_db_vtparent_id)
    def db_add_vtparent_id(self, vtparent_id):
        self._db_vtparent_id = vtparent_id
    def db_change_vtparent_id(self, vtparent_id):
        self._db_vtparent_id = vtparent_id
    def db_delete_vtparent_id(self, vtparent_id):
        self._db_vtparent_id = None
    
    def __get_db_vtpos(self):
        return self._db_vtpos
    def __set_db_vtpos(self, vtpos):
        self._db_vtpos = vtpos
        self.is_dirty = True
    db_vtpos = property(__get_db_vtpos, __set_db_vtpos)
    def db_add_vtpos(self, vtpos):
        self._db_vtpos = vtpos
    def db_change_vtpos(self, vtpos):
        self._db_vtpos = vtpos
    def db_delete_vtpos(self, vtpos):
        self._db_vtpos = None
    
    def __get_db_vtmid(self):
        return self._db_vtmid
    def __set_db_vtmid(self, vtmid):
        self._db_vtmid = vtmid
        self.is_dirty = True
    db_vtmid = property(__get_db_vtmid, __set_db_vtmid)
    def db_add_vtmid(self, vtmid):
        self._db_vtmid = vtmid
    def db_change_vtmid(self, vtmid):
        self._db_vtmid = vtmid
    def db_delete_vtmid(self, vtmid):
        self._db_vtmid = None
    
    def __get_db_pos(self):
        return self._db_pos
    def __set_db_pos(self, pos):
        self._db_pos = pos
        self.is_dirty = True
    db_pos = property(__get_db_pos, __set_db_pos)
    def db_add_pos(self, pos):
        self._db_pos = pos
    def db_change_pos(self, pos):
        self._db_pos = pos
    def db_delete_pos(self, pos):
        self._db_pos = None
    
    def __get_db_type(self):
        return self._db_type
    def __set_db_type(self, type):
        self._db_type = type
        self.is_dirty = True
    db_type = property(__get_db_type, __set_db_type)
    def db_add_type(self, type):
        self._db_type = type
    def db_change_type(self, type):
        self._db_type = type
    def db_delete_type(self, type):
        self._db_type = None
    
    def __get_db_val(self):
        return self._db_val
    def __set_db_val(self, val):
        self._db_val = val
        self.is_dirty = True
    db_val = property(__get_db_val, __set_db_val)
    def db_add_val(self, val):
        self._db_val = val
    def db_change_val(self, val):
        self._db_val = val
    def db_delete_val(self, val):
        self._db_val = None
    
    def __get_db_minVal(self):
        return self._db_minVal
    def __set_db_minVal(self, minVal):
        self._db_minVal = minVal
        self.is_dirty = True
    db_minVal = property(__get_db_minVal, __set_db_minVal)
    def db_add_minVal(self, minVal):
        self._db_minVal = minVal
    def db_change_minVal(self, minVal):
        self._db_minVal = minVal
    def db_delete_minVal(self, minVal):
        self._db_minVal = None
    
    def __get_db_maxVal(self):
        return self._db_maxVal
    def __set_db_maxVal(self, maxVal):
        self._db_maxVal = maxVal
        self.is_dirty = True
    db_maxVal = property(__get_db_maxVal, __set_db_maxVal)
    def db_add_maxVal(self, maxVal):
        self._db_maxVal = maxVal
    def db_change_maxVal(self, maxVal):
        self._db_maxVal = maxVal
    def db_delete_maxVal(self, maxVal):
        self._db_maxVal = None
    
    def __get_db_stepSize(self):
        return self._db_stepSize
    def __set_db_stepSize(self, stepSize):
        self._db_stepSize = stepSize
        self.is_dirty = True
    db_stepSize = property(__get_db_stepSize, __set_db_stepSize)
    def db_add_stepSize(self, stepSize):
        self._db_stepSize = stepSize
    def db_change_stepSize(self, stepSize):
        self._db_stepSize = stepSize
    def db_delete_stepSize(self, stepSize):
        self._db_stepSize = None
    
    def __get_db_strvaluelist(self):
        return self._db_strvaluelist
    def __set_db_strvaluelist(self, strvaluelist):
        self._db_strvaluelist = strvaluelist
        self.is_dirty = True
    db_strvaluelist = property(__get_db_strvaluelist, __set_db_strvaluelist)
    def db_add_strvaluelist(self, strvaluelist):
        self._db_strvaluelist = strvaluelist
    def db_change_strvaluelist(self, strvaluelist):
        self._db_strvaluelist = strvaluelist
    def db_delete_strvaluelist(self, strvaluelist):
        self._db_strvaluelist = None
    
    def __get_db_widget(self):
        return self._db_widget
    def __set_db_widget(self, widget):
        self._db_widget = widget
        self.is_dirty = True
    db_widget = property(__get_db_widget, __set_db_widget)
    def db_add_widget(self, widget):
        self._db_widget = widget
    def db_change_widget(self, widget):
        self._db_widget = widget
    def db_delete_widget(self, widget):
        self._db_widget = None
    
    def __get_db_seq(self):
        return self._db_seq
    def __set_db_seq(self, seq):
        self._db_seq = seq
        self.is_dirty = True
    db_seq = property(__get_db_seq, __set_db_seq)
    def db_add_seq(self, seq):
        self._db_seq = seq
    def db_change_seq(self, seq):
        self._db_seq = seq
    def db_delete_seq(self, seq):
        self._db_seq = None
    
    def __get_db_parent(self):
        return self._db_parent
    def __set_db_parent(self, parent):
        self._db_parent = parent
        self.is_dirty = True
    db_parent = property(__get_db_parent, __set_db_parent)
    def db_add_parent(self, parent):
        self._db_parent = parent
    def db_change_parent(self, parent):
        self._db_parent = parent
    def db_delete_parent(self, parent):
        self._db_parent = None
    
    def getPrimaryKey(self):
        return self._db_id

class DBMashup(object):

    vtType = 'mashup'

    def __init__(self, id=None, name=None, version=None, aliases=None, type=None, vtid=None, layout=None, geometry=None, has_seq=None):
        self._db_id = id
        self._db_name = name
        self._db_version = version
        self.db_deleted_aliases = []
        self.db_aliases_id_index = {}
        if aliases is None:
            self._db_aliases = []
        else:
            self._db_aliases = aliases
            for v in self._db_aliases:
                self.db_aliases_id_index[v.db_id] = v
        self._db_type = type
        self._db_vtid = vtid
        self._db_layout = layout
        self._db_geometry = geometry
        self._db_has_seq = has_seq
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBMashup.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBMashup(id=self._db_id,
                      name=self._db_name,
                      version=self._db_version,
                      type=self._db_type,
                      vtid=self._db_vtid,
                      layout=self._db_layout,
                      geometry=self._db_geometry,
                      has_seq=self._db_has_seq)
        if self._db_aliases is None:
            cp._db_aliases = []
        else:
            cp._db_aliases = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_aliases]
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
            if hasattr(self, 'db_vtid') and ('vistrail', self._db_vtid) in id_remap:
                cp._db_vtid = id_remap[('vistrail', self._db_vtid)]
        
        # recreate indices and set flags
        cp.db_aliases_id_index = dict((v.db_id, v) for v in cp._db_aliases)
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBMashup()
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
        if 'version' in class_dict:
            res = class_dict['version'](old_obj, trans_dict)
            new_obj.db_version = res
        elif hasattr(old_obj, 'db_version') and old_obj.db_version is not None:
            new_obj.db_version = old_obj.db_version
        if 'aliases' in class_dict:
            res = class_dict['aliases'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_alias(obj)
        elif hasattr(old_obj, 'db_aliases') and old_obj.db_aliases is not None:
            for obj in old_obj.db_aliases:
                new_obj.db_add_alias(DBMashupAlias.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_aliases') and hasattr(new_obj, 'db_deleted_aliases'):
            for obj in old_obj.db_deleted_aliases:
                n_obj = DBMashupAlias.update_version(obj, trans_dict)
                new_obj.db_deleted_aliases.append(n_obj)
        if 'type' in class_dict:
            res = class_dict['type'](old_obj, trans_dict)
            new_obj.db_type = res
        elif hasattr(old_obj, 'db_type') and old_obj.db_type is not None:
            new_obj.db_type = old_obj.db_type
        if 'vtid' in class_dict:
            res = class_dict['vtid'](old_obj, trans_dict)
            new_obj.db_vtid = res
        elif hasattr(old_obj, 'db_vtid') and old_obj.db_vtid is not None:
            new_obj.db_vtid = old_obj.db_vtid
        if 'layout' in class_dict:
            res = class_dict['layout'](old_obj, trans_dict)
            new_obj.db_layout = res
        elif hasattr(old_obj, 'db_layout') and old_obj.db_layout is not None:
            new_obj.db_layout = old_obj.db_layout
        if 'geometry' in class_dict:
            res = class_dict['geometry'](old_obj, trans_dict)
            new_obj.db_geometry = res
        elif hasattr(old_obj, 'db_geometry') and old_obj.db_geometry is not None:
            new_obj.db_geometry = old_obj.db_geometry
        if 'has_seq' in class_dict:
            res = class_dict['has_seq'](old_obj, trans_dict)
            new_obj.db_has_seq = res
        elif hasattr(old_obj, 'db_has_seq') and old_obj.db_has_seq is not None:
            new_obj.db_has_seq = old_obj.db_has_seq
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        children = []
        to_del = []
        for child in self.db_aliases:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_alias(child)
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_aliases)
        if remove:
            self.db_deleted_aliases = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        for child in self._db_aliases:
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
    
    def __get_db_aliases(self):
        return self._db_aliases
    def __set_db_aliases(self, aliases):
        self._db_aliases = aliases
        self.is_dirty = True
    db_aliases = property(__get_db_aliases, __set_db_aliases)
    def db_get_aliases(self):
        return self._db_aliases
    def db_add_alias(self, alias):
        self.is_dirty = True
        self._db_aliases.append(alias)
        self.db_aliases_id_index[alias.db_id] = alias
    def db_change_alias(self, alias):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_aliases)):
            if self._db_aliases[i].db_id == alias.db_id:
                self._db_aliases[i] = alias
                found = True
                break
        if not found:
            self._db_aliases.append(alias)
        self.db_aliases_id_index[alias.db_id] = alias
    def db_delete_alias(self, alias):
        self.is_dirty = True
        for i in xrange(len(self._db_aliases)):
            if self._db_aliases[i].db_id == alias.db_id:
                if not self._db_aliases[i].is_new:
                    self.db_deleted_aliases.append(self._db_aliases[i])
                del self._db_aliases[i]
                break
        del self.db_aliases_id_index[alias.db_id]
    def db_get_alias(self, key):
        for i in xrange(len(self._db_aliases)):
            if self._db_aliases[i].db_id == key:
                return self._db_aliases[i]
        return None
    def db_get_alias_by_id(self, key):
        return self.db_aliases_id_index[key]
    def db_has_alias_with_id(self, key):
        return key in self.db_aliases_id_index
    
    def __get_db_type(self):
        return self._db_type
    def __set_db_type(self, type):
        self._db_type = type
        self.is_dirty = True
    db_type = property(__get_db_type, __set_db_type)
    def db_add_type(self, type):
        self._db_type = type
    def db_change_type(self, type):
        self._db_type = type
    def db_delete_type(self, type):
        self._db_type = None
    
    def __get_db_vtid(self):
        return self._db_vtid
    def __set_db_vtid(self, vtid):
        self._db_vtid = vtid
        self.is_dirty = True
    db_vtid = property(__get_db_vtid, __set_db_vtid)
    def db_add_vtid(self, vtid):
        self._db_vtid = vtid
    def db_change_vtid(self, vtid):
        self._db_vtid = vtid
    def db_delete_vtid(self, vtid):
        self._db_vtid = None
    
    def __get_db_layout(self):
        return self._db_layout
    def __set_db_layout(self, layout):
        self._db_layout = layout
        self.is_dirty = True
    db_layout = property(__get_db_layout, __set_db_layout)
    def db_add_layout(self, layout):
        self._db_layout = layout
    def db_change_layout(self, layout):
        self._db_layout = layout
    def db_delete_layout(self, layout):
        self._db_layout = None
    
    def __get_db_geometry(self):
        return self._db_geometry
    def __set_db_geometry(self, geometry):
        self._db_geometry = geometry
        self.is_dirty = True
    db_geometry = property(__get_db_geometry, __set_db_geometry)
    def db_add_geometry(self, geometry):
        self._db_geometry = geometry
    def db_change_geometry(self, geometry):
        self._db_geometry = geometry
    def db_delete_geometry(self, geometry):
        self._db_geometry = None
    
    def __get_db_has_seq(self):
        return self._db_has_seq
    def __set_db_has_seq(self, has_seq):
        self._db_has_seq = has_seq
        self.is_dirty = True
    db_has_seq = property(__get_db_has_seq, __set_db_has_seq)
    def db_add_has_seq(self, has_seq):
        self._db_has_seq = has_seq
    def db_change_has_seq(self, has_seq):
        self._db_has_seq = has_seq
    def db_delete_has_seq(self, has_seq):
        self._db_has_seq = None
    
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

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
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

class DBConfigFloat(object):

    vtType = 'config_float'

    def __init__(self, value=None):
        self._db_value = value
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBConfigFloat.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBConfigFloat(value=self._db_value)
        
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
            new_obj = DBConfigFloat()
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

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
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
    


class DBOther(object):

    vtType = 'other'

    def __init__(self, id=None, key=None, value=None):
        self._db_id = id
        self._db_key = key
        self._db_value = value
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBOther.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBOther(id=self._db_id,
                     key=self._db_key,
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
            new_obj = DBOther()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'key' in class_dict:
            res = class_dict['key'](old_obj, trans_dict)
            new_obj.db_key = res
        elif hasattr(old_obj, 'db_key') and old_obj.db_key is not None:
            new_obj.db_key = old_obj.db_key
        if 'value' in class_dict:
            res = class_dict['value'](old_obj, trans_dict)
            new_obj.db_value = res
        elif hasattr(old_obj, 'db_value') and old_obj.db_value is not None:
            new_obj.db_value = old_obj.db_value
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
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
    
    def __get_db_key(self):
        return self._db_key
    def __set_db_key(self, key):
        self._db_key = key
        self.is_dirty = True
    db_key = property(__get_db_key, __set_db_key)
    def db_add_key(self, key):
        self._db_key = key
    def db_change_key(self, key):
        self._db_key = key
    def db_delete_key(self, key):
        self._db_key = None
    
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

class DBRefProvActivity(object):

    vtType = 'ref_prov_activity'

    def __init__(self, prov_ref=None):
        self._db_prov_ref = prov_ref
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBRefProvActivity.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBRefProvActivity(prov_ref=self._db_prov_ref)
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
            if hasattr(self, 'db_prov_ref') and ('prov_activity', self._db_prov_ref) in id_remap:
                cp._db_prov_ref = id_remap[('prov_activity', self._db_prov_ref)]
        
        # recreate indices and set flags
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBRefProvActivity()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'prov_ref' in class_dict:
            res = class_dict['prov_ref'](old_obj, trans_dict)
            new_obj.db_prov_ref = res
        elif hasattr(old_obj, 'db_prov_ref') and old_obj.db_prov_ref is not None:
            new_obj.db_prov_ref = old_obj.db_prov_ref
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        return [(self, parent[0], parent[1])]
    def db_deleted_children(self, remove=False):
        children = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        return False
    def __get_db_prov_ref(self):
        return self._db_prov_ref
    def __set_db_prov_ref(self, prov_ref):
        self._db_prov_ref = prov_ref
        self.is_dirty = True
    db_prov_ref = property(__get_db_prov_ref, __set_db_prov_ref)
    def db_add_prov_ref(self, prov_ref):
        self._db_prov_ref = prov_ref
    def db_change_prov_ref(self, prov_ref):
        self._db_prov_ref = prov_ref
    def db_delete_prov_ref(self, prov_ref):
        self._db_prov_ref = None
    


class DBAbstraction(object):

    vtType = 'abstraction'

    def __init__(self, id=None, cache=None, name=None, namespace=None, package=None, version=None, internal_version=None, location=None, functions=None, annotations=None, controlParameters=None):
        self._db_id = id
        self._db_cache = cache
        self._db_name = name
        self._db_namespace = namespace
        self._db_package = package
        self._db_version = version
        self._db_internal_version = internal_version
        self.db_deleted_location = []
        self._db_location = location
        self.db_deleted_functions = []
        self.db_functions_id_index = {}
        if functions is None:
            self._db_functions = []
        else:
            self._db_functions = functions
            for v in self._db_functions:
                self.db_functions_id_index[v.db_id] = v
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
        self.db_deleted_controlParameters = []
        self.db_controlParameters_id_index = {}
        self.db_controlParameters_name_index = {}
        if controlParameters is None:
            self._db_controlParameters = []
        else:
            self._db_controlParameters = controlParameters
            for v in self._db_controlParameters:
                self.db_controlParameters_id_index[v.db_id] = v
                self.db_controlParameters_name_index[v.db_name] = v
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBAbstraction.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBAbstraction(id=self._db_id,
                           cache=self._db_cache,
                           name=self._db_name,
                           namespace=self._db_namespace,
                           package=self._db_package,
                           version=self._db_version,
                           internal_version=self._db_internal_version)
        if self._db_location is not None:
            cp._db_location = self._db_location.do_copy(new_ids, id_scope, id_remap)
        if self._db_functions is None:
            cp._db_functions = []
        else:
            cp._db_functions = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_functions]
        if self._db_annotations is None:
            cp._db_annotations = []
        else:
            cp._db_annotations = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_annotations]
        if self._db_controlParameters is None:
            cp._db_controlParameters = []
        else:
            cp._db_controlParameters = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_controlParameters]
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
        
        # recreate indices and set flags
        cp.db_functions_id_index = dict((v.db_id, v) for v in cp._db_functions)
        cp.db_annotations_id_index = dict((v.db_id, v) for v in cp._db_annotations)
        cp.db_annotations_key_index = dict((v.db_key, v) for v in cp._db_annotations)
        cp.db_controlParameters_id_index = dict((v.db_id, v) for v in cp._db_controlParameters)
        cp.db_controlParameters_name_index = dict((v.db_name, v) for v in cp._db_controlParameters)
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBAbstraction()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'cache' in class_dict:
            res = class_dict['cache'](old_obj, trans_dict)
            new_obj.db_cache = res
        elif hasattr(old_obj, 'db_cache') and old_obj.db_cache is not None:
            new_obj.db_cache = old_obj.db_cache
        if 'name' in class_dict:
            res = class_dict['name'](old_obj, trans_dict)
            new_obj.db_name = res
        elif hasattr(old_obj, 'db_name') and old_obj.db_name is not None:
            new_obj.db_name = old_obj.db_name
        if 'namespace' in class_dict:
            res = class_dict['namespace'](old_obj, trans_dict)
            new_obj.db_namespace = res
        elif hasattr(old_obj, 'db_namespace') and old_obj.db_namespace is not None:
            new_obj.db_namespace = old_obj.db_namespace
        if 'package' in class_dict:
            res = class_dict['package'](old_obj, trans_dict)
            new_obj.db_package = res
        elif hasattr(old_obj, 'db_package') and old_obj.db_package is not None:
            new_obj.db_package = old_obj.db_package
        if 'version' in class_dict:
            res = class_dict['version'](old_obj, trans_dict)
            new_obj.db_version = res
        elif hasattr(old_obj, 'db_version') and old_obj.db_version is not None:
            new_obj.db_version = old_obj.db_version
        if 'internal_version' in class_dict:
            res = class_dict['internal_version'](old_obj, trans_dict)
            new_obj.db_internal_version = res
        elif hasattr(old_obj, 'db_internal_version') and old_obj.db_internal_version is not None:
            new_obj.db_internal_version = old_obj.db_internal_version
        if 'location' in class_dict:
            res = class_dict['location'](old_obj, trans_dict)
            new_obj.db_location = res
        elif hasattr(old_obj, 'db_location') and old_obj.db_location is not None:
            obj = old_obj.db_location
            new_obj.db_add_location(DBLocation.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_location') and hasattr(new_obj, 'db_deleted_location'):
            for obj in old_obj.db_deleted_location:
                n_obj = DBLocation.update_version(obj, trans_dict)
                new_obj.db_deleted_location.append(n_obj)
        if 'functions' in class_dict:
            res = class_dict['functions'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_function(obj)
        elif hasattr(old_obj, 'db_functions') and old_obj.db_functions is not None:
            for obj in old_obj.db_functions:
                new_obj.db_add_function(DBFunction.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_functions') and hasattr(new_obj, 'db_deleted_functions'):
            for obj in old_obj.db_deleted_functions:
                n_obj = DBFunction.update_version(obj, trans_dict)
                new_obj.db_deleted_functions.append(n_obj)
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
        if 'controlParameters' in class_dict:
            res = class_dict['controlParameters'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_controlParameter(obj)
        elif hasattr(old_obj, 'db_controlParameters') and old_obj.db_controlParameters is not None:
            for obj in old_obj.db_controlParameters:
                new_obj.db_add_controlParameter(DBControlParameter.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_controlParameters') and hasattr(new_obj, 'db_deleted_controlParameters'):
            for obj in old_obj.db_deleted_controlParameters:
                n_obj = DBControlParameter.update_version(obj, trans_dict)
                new_obj.db_deleted_controlParameters.append(n_obj)
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        children = []
        if self._db_location is not None:
            children.extend(self._db_location.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                self._db_location = None
        to_del = []
        for child in self.db_functions:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_function(child)
        to_del = []
        for child in self.db_annotations:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_annotation(child)
        to_del = []
        for child in self.db_controlParameters:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_controlParameter(child)
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_location)
        children.extend(self.db_deleted_functions)
        children.extend(self.db_deleted_annotations)
        children.extend(self.db_deleted_controlParameters)
        if remove:
            self.db_deleted_location = []
            self.db_deleted_functions = []
            self.db_deleted_annotations = []
            self.db_deleted_controlParameters = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        if self._db_location is not None and self._db_location.has_changes():
            return True
        for child in self._db_functions:
            if child.has_changes():
                return True
        for child in self._db_annotations:
            if child.has_changes():
                return True
        for child in self._db_controlParameters:
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
    
    def __get_db_cache(self):
        return self._db_cache
    def __set_db_cache(self, cache):
        self._db_cache = cache
        self.is_dirty = True
    db_cache = property(__get_db_cache, __set_db_cache)
    def db_add_cache(self, cache):
        self._db_cache = cache
    def db_change_cache(self, cache):
        self._db_cache = cache
    def db_delete_cache(self, cache):
        self._db_cache = None
    
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
    
    def __get_db_namespace(self):
        return self._db_namespace
    def __set_db_namespace(self, namespace):
        self._db_namespace = namespace
        self.is_dirty = True
    db_namespace = property(__get_db_namespace, __set_db_namespace)
    def db_add_namespace(self, namespace):
        self._db_namespace = namespace
    def db_change_namespace(self, namespace):
        self._db_namespace = namespace
    def db_delete_namespace(self, namespace):
        self._db_namespace = None
    
    def __get_db_package(self):
        return self._db_package
    def __set_db_package(self, package):
        self._db_package = package
        self.is_dirty = True
    db_package = property(__get_db_package, __set_db_package)
    def db_add_package(self, package):
        self._db_package = package
    def db_change_package(self, package):
        self._db_package = package
    def db_delete_package(self, package):
        self._db_package = None
    
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
    
    def __get_db_internal_version(self):
        return self._db_internal_version
    def __set_db_internal_version(self, internal_version):
        self._db_internal_version = internal_version
        self.is_dirty = True
    db_internal_version = property(__get_db_internal_version, __set_db_internal_version)
    def db_add_internal_version(self, internal_version):
        self._db_internal_version = internal_version
    def db_change_internal_version(self, internal_version):
        self._db_internal_version = internal_version
    def db_delete_internal_version(self, internal_version):
        self._db_internal_version = None
    
    def __get_db_location(self):
        return self._db_location
    def __set_db_location(self, location):
        self._db_location = location
        self.is_dirty = True
    db_location = property(__get_db_location, __set_db_location)
    def db_add_location(self, location):
        self._db_location = location
    def db_change_location(self, location):
        self._db_location = location
    def db_delete_location(self, location):
        if not self.is_new:
            self.db_deleted_location.append(self._db_location)
        self._db_location = None
    
    def __get_db_functions(self):
        return self._db_functions
    def __set_db_functions(self, functions):
        self._db_functions = functions
        self.is_dirty = True
    db_functions = property(__get_db_functions, __set_db_functions)
    def db_get_functions(self):
        return self._db_functions
    def db_add_function(self, function):
        self.is_dirty = True
        self._db_functions.append(function)
        self.db_functions_id_index[function.db_id] = function
    def db_change_function(self, function):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_functions)):
            if self._db_functions[i].db_id == function.db_id:
                self._db_functions[i] = function
                found = True
                break
        if not found:
            self._db_functions.append(function)
        self.db_functions_id_index[function.db_id] = function
    def db_delete_function(self, function):
        self.is_dirty = True
        for i in xrange(len(self._db_functions)):
            if self._db_functions[i].db_id == function.db_id:
                if not self._db_functions[i].is_new:
                    self.db_deleted_functions.append(self._db_functions[i])
                del self._db_functions[i]
                break
        del self.db_functions_id_index[function.db_id]
    def db_get_function(self, key):
        for i in xrange(len(self._db_functions)):
            if self._db_functions[i].db_id == key:
                return self._db_functions[i]
        return None
    def db_get_function_by_id(self, key):
        return self.db_functions_id_index[key]
    def db_has_function_with_id(self, key):
        return key in self.db_functions_id_index
    
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
    
    def __get_db_controlParameters(self):
        return self._db_controlParameters
    def __set_db_controlParameters(self, controlParameters):
        self._db_controlParameters = controlParameters
        self.is_dirty = True
    db_controlParameters = property(__get_db_controlParameters, __set_db_controlParameters)
    def db_get_controlParameters(self):
        return self._db_controlParameters
    def db_add_controlParameter(self, controlParameter):
        self.is_dirty = True
        self._db_controlParameters.append(controlParameter)
        self.db_controlParameters_id_index[controlParameter.db_id] = controlParameter
        self.db_controlParameters_name_index[controlParameter.db_name] = controlParameter
    def db_change_controlParameter(self, controlParameter):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_controlParameters)):
            if self._db_controlParameters[i].db_id == controlParameter.db_id:
                self._db_controlParameters[i] = controlParameter
                found = True
                break
        if not found:
            self._db_controlParameters.append(controlParameter)
        self.db_controlParameters_id_index[controlParameter.db_id] = controlParameter
        self.db_controlParameters_name_index[controlParameter.db_name] = controlParameter
    def db_delete_controlParameter(self, controlParameter):
        self.is_dirty = True
        for i in xrange(len(self._db_controlParameters)):
            if self._db_controlParameters[i].db_id == controlParameter.db_id:
                if not self._db_controlParameters[i].is_new:
                    self.db_deleted_controlParameters.append(self._db_controlParameters[i])
                del self._db_controlParameters[i]
                break
        del self.db_controlParameters_id_index[controlParameter.db_id]
        del self.db_controlParameters_name_index[controlParameter.db_name]
    def db_get_controlParameter(self, key):
        for i in xrange(len(self._db_controlParameters)):
            if self._db_controlParameters[i].db_id == key:
                return self._db_controlParameters[i]
        return None
    def db_get_controlParameter_by_id(self, key):
        return self.db_controlParameters_id_index[key]
    def db_has_controlParameter_with_id(self, key):
        return key in self.db_controlParameters_id_index
    def db_get_controlParameter_by_name(self, key):
        return self.db_controlParameters_name_index[key]
    def db_has_controlParameter_with_name(self, key):
        return key in self.db_controlParameters_name_index
    
    def getPrimaryKey(self):
        return self._db_id

class DBProvAgent(object):

    vtType = 'prov_agent'

    def __init__(self, id=None, vt_id=None, prov_type=None, prov_label=None, vt_machine_os=None, vt_machine_architecture=None, vt_machine_processor=None, vt_machine_ram=None):
        self._db_id = id
        self._db_vt_id = vt_id
        self._db_prov_type = prov_type
        self._db_prov_label = prov_label
        self._db_vt_machine_os = vt_machine_os
        self._db_vt_machine_architecture = vt_machine_architecture
        self._db_vt_machine_processor = vt_machine_processor
        self._db_vt_machine_ram = vt_machine_ram
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBProvAgent.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBProvAgent(id=self._db_id,
                         vt_id=self._db_vt_id,
                         prov_type=self._db_prov_type,
                         prov_label=self._db_prov_label,
                         vt_machine_os=self._db_vt_machine_os,
                         vt_machine_architecture=self._db_vt_machine_architecture,
                         vt_machine_processor=self._db_vt_machine_processor,
                         vt_machine_ram=self._db_vt_machine_ram)
        
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
            new_obj = DBProvAgent()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'vt_id' in class_dict:
            res = class_dict['vt_id'](old_obj, trans_dict)
            new_obj.db_vt_id = res
        elif hasattr(old_obj, 'db_vt_id') and old_obj.db_vt_id is not None:
            new_obj.db_vt_id = old_obj.db_vt_id
        if 'prov_type' in class_dict:
            res = class_dict['prov_type'](old_obj, trans_dict)
            new_obj.db_prov_type = res
        elif hasattr(old_obj, 'db_prov_type') and old_obj.db_prov_type is not None:
            new_obj.db_prov_type = old_obj.db_prov_type
        if 'prov_label' in class_dict:
            res = class_dict['prov_label'](old_obj, trans_dict)
            new_obj.db_prov_label = res
        elif hasattr(old_obj, 'db_prov_label') and old_obj.db_prov_label is not None:
            new_obj.db_prov_label = old_obj.db_prov_label
        if 'vt_machine_os' in class_dict:
            res = class_dict['vt_machine_os'](old_obj, trans_dict)
            new_obj.db_vt_machine_os = res
        elif hasattr(old_obj, 'db_vt_machine_os') and old_obj.db_vt_machine_os is not None:
            new_obj.db_vt_machine_os = old_obj.db_vt_machine_os
        if 'vt_machine_architecture' in class_dict:
            res = class_dict['vt_machine_architecture'](old_obj, trans_dict)
            new_obj.db_vt_machine_architecture = res
        elif hasattr(old_obj, 'db_vt_machine_architecture') and old_obj.db_vt_machine_architecture is not None:
            new_obj.db_vt_machine_architecture = old_obj.db_vt_machine_architecture
        if 'vt_machine_processor' in class_dict:
            res = class_dict['vt_machine_processor'](old_obj, trans_dict)
            new_obj.db_vt_machine_processor = res
        elif hasattr(old_obj, 'db_vt_machine_processor') and old_obj.db_vt_machine_processor is not None:
            new_obj.db_vt_machine_processor = old_obj.db_vt_machine_processor
        if 'vt_machine_ram' in class_dict:
            res = class_dict['vt_machine_ram'](old_obj, trans_dict)
            new_obj.db_vt_machine_ram = res
        elif hasattr(old_obj, 'db_vt_machine_ram') and old_obj.db_vt_machine_ram is not None:
            new_obj.db_vt_machine_ram = old_obj.db_vt_machine_ram
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
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
    
    def __get_db_vt_id(self):
        return self._db_vt_id
    def __set_db_vt_id(self, vt_id):
        self._db_vt_id = vt_id
        self.is_dirty = True
    db_vt_id = property(__get_db_vt_id, __set_db_vt_id)
    def db_add_vt_id(self, vt_id):
        self._db_vt_id = vt_id
    def db_change_vt_id(self, vt_id):
        self._db_vt_id = vt_id
    def db_delete_vt_id(self, vt_id):
        self._db_vt_id = None
    
    def __get_db_prov_type(self):
        return self._db_prov_type
    def __set_db_prov_type(self, prov_type):
        self._db_prov_type = prov_type
        self.is_dirty = True
    db_prov_type = property(__get_db_prov_type, __set_db_prov_type)
    def db_add_prov_type(self, prov_type):
        self._db_prov_type = prov_type
    def db_change_prov_type(self, prov_type):
        self._db_prov_type = prov_type
    def db_delete_prov_type(self, prov_type):
        self._db_prov_type = None
    
    def __get_db_prov_label(self):
        return self._db_prov_label
    def __set_db_prov_label(self, prov_label):
        self._db_prov_label = prov_label
        self.is_dirty = True
    db_prov_label = property(__get_db_prov_label, __set_db_prov_label)
    def db_add_prov_label(self, prov_label):
        self._db_prov_label = prov_label
    def db_change_prov_label(self, prov_label):
        self._db_prov_label = prov_label
    def db_delete_prov_label(self, prov_label):
        self._db_prov_label = None
    
    def __get_db_vt_machine_os(self):
        return self._db_vt_machine_os
    def __set_db_vt_machine_os(self, vt_machine_os):
        self._db_vt_machine_os = vt_machine_os
        self.is_dirty = True
    db_vt_machine_os = property(__get_db_vt_machine_os, __set_db_vt_machine_os)
    def db_add_vt_machine_os(self, vt_machine_os):
        self._db_vt_machine_os = vt_machine_os
    def db_change_vt_machine_os(self, vt_machine_os):
        self._db_vt_machine_os = vt_machine_os
    def db_delete_vt_machine_os(self, vt_machine_os):
        self._db_vt_machine_os = None
    
    def __get_db_vt_machine_architecture(self):
        return self._db_vt_machine_architecture
    def __set_db_vt_machine_architecture(self, vt_machine_architecture):
        self._db_vt_machine_architecture = vt_machine_architecture
        self.is_dirty = True
    db_vt_machine_architecture = property(__get_db_vt_machine_architecture, __set_db_vt_machine_architecture)
    def db_add_vt_machine_architecture(self, vt_machine_architecture):
        self._db_vt_machine_architecture = vt_machine_architecture
    def db_change_vt_machine_architecture(self, vt_machine_architecture):
        self._db_vt_machine_architecture = vt_machine_architecture
    def db_delete_vt_machine_architecture(self, vt_machine_architecture):
        self._db_vt_machine_architecture = None
    
    def __get_db_vt_machine_processor(self):
        return self._db_vt_machine_processor
    def __set_db_vt_machine_processor(self, vt_machine_processor):
        self._db_vt_machine_processor = vt_machine_processor
        self.is_dirty = True
    db_vt_machine_processor = property(__get_db_vt_machine_processor, __set_db_vt_machine_processor)
    def db_add_vt_machine_processor(self, vt_machine_processor):
        self._db_vt_machine_processor = vt_machine_processor
    def db_change_vt_machine_processor(self, vt_machine_processor):
        self._db_vt_machine_processor = vt_machine_processor
    def db_delete_vt_machine_processor(self, vt_machine_processor):
        self._db_vt_machine_processor = None
    
    def __get_db_vt_machine_ram(self):
        return self._db_vt_machine_ram
    def __set_db_vt_machine_ram(self, vt_machine_ram):
        self._db_vt_machine_ram = vt_machine_ram
        self.is_dirty = True
    db_vt_machine_ram = property(__get_db_vt_machine_ram, __set_db_vt_machine_ram)
    def db_add_vt_machine_ram(self, vt_machine_ram):
        self._db_vt_machine_ram = vt_machine_ram
    def db_change_vt_machine_ram(self, vt_machine_ram):
        self._db_vt_machine_ram = vt_machine_ram
    def db_delete_vt_machine_ram(self, vt_machine_ram):
        self._db_vt_machine_ram = None
    
    def getPrimaryKey(self):
        return self._db_id

class DBMashuptrail(object):

    vtType = 'mashuptrail'

    def __init__(self, id=None, name=None, version=None, vtVersion=None, last_modified=None, actions=None, annotations=None, actionAnnotations=None):
        self._db_id = id
        self._db_name = name
        self._db_version = version
        self._db_vtVersion = vtVersion
        self._db_last_modified = last_modified
        self.db_deleted_actions = []
        self.db_actions_id_index = {}
        if actions is None:
            self._db_actions = []
        else:
            self._db_actions = actions
            for v in self._db_actions:
                self.db_actions_id_index[v.db_id] = v
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
        return DBMashuptrail.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBMashuptrail(id=self._db_id,
                           name=self._db_name,
                           version=self._db_version,
                           vtVersion=self._db_vtVersion,
                           last_modified=self._db_last_modified)
        if self._db_actions is None:
            cp._db_actions = []
        else:
            cp._db_actions = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_actions]
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
            new_obj = DBMashuptrail()
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
        if 'version' in class_dict:
            res = class_dict['version'](old_obj, trans_dict)
            new_obj.db_version = res
        elif hasattr(old_obj, 'db_version') and old_obj.db_version is not None:
            new_obj.db_version = old_obj.db_version
        if 'vtVersion' in class_dict:
            res = class_dict['vtVersion'](old_obj, trans_dict)
            new_obj.db_vtVersion = res
        elif hasattr(old_obj, 'db_vtVersion') and old_obj.db_vtVersion is not None:
            new_obj.db_vtVersion = old_obj.db_vtVersion
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
                new_obj.db_add_action(DBMashupAction.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_actions') and hasattr(new_obj, 'db_deleted_actions'):
            for obj in old_obj.db_deleted_actions:
                n_obj = DBMashupAction.update_version(obj, trans_dict)
                new_obj.db_deleted_actions.append(n_obj)
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
                new_obj.db_add_actionAnnotation(DBMashupActionAnnotation.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_actionAnnotations') and hasattr(new_obj, 'db_deleted_actionAnnotations'):
            for obj in old_obj.db_deleted_actionAnnotations:
                n_obj = DBMashupActionAnnotation.update_version(obj, trans_dict)
                new_obj.db_deleted_actionAnnotations.append(n_obj)
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        children = []
        to_del = []
        for child in self.db_actions:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_action(child)
        to_del = []
        for child in self.db_annotations:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_annotation(child)
        to_del = []
        for child in self.db_actionAnnotations:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_actionAnnotation(child)
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_actions)
        children.extend(self.db_deleted_annotations)
        children.extend(self.db_deleted_actionAnnotations)
        if remove:
            self.db_deleted_actions = []
            self.db_deleted_annotations = []
            self.db_deleted_actionAnnotations = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        for child in self._db_actions:
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
    
    def __get_db_vtVersion(self):
        return self._db_vtVersion
    def __set_db_vtVersion(self, vtVersion):
        self._db_vtVersion = vtVersion
        self.is_dirty = True
    db_vtVersion = property(__get_db_vtVersion, __set_db_vtVersion)
    def db_add_vtVersion(self, vtVersion):
        self._db_vtVersion = vtVersion
    def db_change_vtVersion(self, vtVersion):
        self._db_vtVersion = vtVersion
    def db_delete_vtVersion(self, vtVersion):
        self._db_vtVersion = None
    
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

class DBRegistry(object):

    vtType = 'registry'

    def __init__(self, id=None, entity_type=None, version=None, root_descriptor_id=None, name=None, last_modified=None, packages=None):
        self._db_id = id
        self._db_entity_type = entity_type
        self._db_version = version
        self._db_root_descriptor_id = root_descriptor_id
        self._db_name = name
        self._db_last_modified = last_modified
        self.db_deleted_packages = []
        self.db_packages_id_index = {}
        self.db_packages_identifier_index = {}
        if packages is None:
            self._db_packages = []
        else:
            self._db_packages = packages
            for v in self._db_packages:
                self.db_packages_id_index[v.db_id] = v
                self.db_packages_identifier_index[(v.db_identifier,v.db_version)] = v
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBRegistry.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBRegistry(id=self._db_id,
                        entity_type=self._db_entity_type,
                        version=self._db_version,
                        root_descriptor_id=self._db_root_descriptor_id,
                        name=self._db_name,
                        last_modified=self._db_last_modified)
        if self._db_packages is None:
            cp._db_packages = []
        else:
            cp._db_packages = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_packages]
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
            if hasattr(self, 'db_root_descriptor_id') and ('module_descriptor', self._db_root_descriptor_id) in id_remap:
                cp._db_root_descriptor_id = id_remap[('module_descriptor', self._db_root_descriptor_id)]
        
        # recreate indices and set flags
        cp.db_packages_id_index = dict((v.db_id, v) for v in cp._db_packages)
        cp.db_packages_identifier_index = dict(((v.db_identifier,v.db_version), v) for v in cp._db_packages)
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBRegistry()
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
        if 'root_descriptor_id' in class_dict:
            res = class_dict['root_descriptor_id'](old_obj, trans_dict)
            new_obj.db_root_descriptor_id = res
        elif hasattr(old_obj, 'db_root_descriptor_id') and old_obj.db_root_descriptor_id is not None:
            new_obj.db_root_descriptor_id = old_obj.db_root_descriptor_id
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
        if 'packages' in class_dict:
            res = class_dict['packages'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_package(obj)
        elif hasattr(old_obj, 'db_packages') and old_obj.db_packages is not None:
            for obj in old_obj.db_packages:
                new_obj.db_add_package(DBPackage.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_packages') and hasattr(new_obj, 'db_deleted_packages'):
            for obj in old_obj.db_deleted_packages:
                n_obj = DBPackage.update_version(obj, trans_dict)
                new_obj.db_deleted_packages.append(n_obj)
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        children = []
        to_del = []
        for child in self.db_packages:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_package(child)
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_packages)
        if remove:
            self.db_deleted_packages = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        for child in self._db_packages:
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
    
    def __get_db_root_descriptor_id(self):
        return self._db_root_descriptor_id
    def __set_db_root_descriptor_id(self, root_descriptor_id):
        self._db_root_descriptor_id = root_descriptor_id
        self.is_dirty = True
    db_root_descriptor_id = property(__get_db_root_descriptor_id, __set_db_root_descriptor_id)
    def db_add_root_descriptor_id(self, root_descriptor_id):
        self._db_root_descriptor_id = root_descriptor_id
    def db_change_root_descriptor_id(self, root_descriptor_id):
        self._db_root_descriptor_id = root_descriptor_id
    def db_delete_root_descriptor_id(self, root_descriptor_id):
        self._db_root_descriptor_id = None
    
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
    
    def __get_db_packages(self):
        return self._db_packages
    def __set_db_packages(self, packages):
        self._db_packages = packages
        self.is_dirty = True
    db_packages = property(__get_db_packages, __set_db_packages)
    def db_get_packages(self):
        return self._db_packages
    def db_add_package(self, package):
        self.is_dirty = True
        self._db_packages.append(package)
        self.db_packages_id_index[package.db_id] = package
        self.db_packages_identifier_index[(package.db_identifier,package.db_version)] = package
    def db_change_package(self, package):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_packages)):
            if self._db_packages[i].db_id == package.db_id:
                self._db_packages[i] = package
                found = True
                break
        if not found:
            self._db_packages.append(package)
        self.db_packages_id_index[package.db_id] = package
        self.db_packages_identifier_index[(package.db_identifier,package.db_version)] = package
    def db_delete_package(self, package):
        self.is_dirty = True
        for i in xrange(len(self._db_packages)):
            if self._db_packages[i].db_id == package.db_id:
                if not self._db_packages[i].is_new:
                    self.db_deleted_packages.append(self._db_packages[i])
                del self._db_packages[i]
                break
        del self.db_packages_id_index[package.db_id]
        del self.db_packages_identifier_index[(package.db_identifier,package.db_version)]
    def db_get_package(self, key):
        for i in xrange(len(self._db_packages)):
            if self._db_packages[i].db_id == key:
                return self._db_packages[i]
        return None
    def db_get_package_by_id(self, key):
        return self.db_packages_id_index[key]
    def db_has_package_with_id(self, key):
        return key in self.db_packages_id_index
    def db_get_package_by_identifier(self, key):
        return self.db_packages_identifier_index[key]
    def db_has_package_with_identifier(self, key):
        return key in self.db_packages_identifier_index
    
    def getPrimaryKey(self):
        return self._db_id

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

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        children = []
        to_del = []
        for child in self.db_accounts:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
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

class DBProvEntity(object):

    vtType = 'prov_entity'

    def __init__(self, id=None, prov_type=None, prov_label=None, prov_value=None, vt_id=None, vt_type=None, vt_desc=None, vt_package=None, vt_version=None, vt_cache=None, vt_location_x=None, vt_location_y=None, is_part_of=None):
        self._db_id = id
        self._db_prov_type = prov_type
        self._db_prov_label = prov_label
        self._db_prov_value = prov_value
        self._db_vt_id = vt_id
        self._db_vt_type = vt_type
        self._db_vt_desc = vt_desc
        self._db_vt_package = vt_package
        self._db_vt_version = vt_version
        self._db_vt_cache = vt_cache
        self._db_vt_location_x = vt_location_x
        self._db_vt_location_y = vt_location_y
        self.db_deleted_is_part_of = []
        self._db_is_part_of = is_part_of
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBProvEntity.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBProvEntity(id=self._db_id,
                          prov_type=self._db_prov_type,
                          prov_label=self._db_prov_label,
                          prov_value=self._db_prov_value,
                          vt_id=self._db_vt_id,
                          vt_type=self._db_vt_type,
                          vt_desc=self._db_vt_desc,
                          vt_package=self._db_vt_package,
                          vt_version=self._db_vt_version,
                          vt_cache=self._db_vt_cache,
                          vt_location_x=self._db_vt_location_x,
                          vt_location_y=self._db_vt_location_y)
        if self._db_is_part_of is not None:
            cp._db_is_part_of = self._db_is_part_of.do_copy(new_ids, id_scope, id_remap)
        
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
            new_obj = DBProvEntity()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'prov_type' in class_dict:
            res = class_dict['prov_type'](old_obj, trans_dict)
            new_obj.db_prov_type = res
        elif hasattr(old_obj, 'db_prov_type') and old_obj.db_prov_type is not None:
            new_obj.db_prov_type = old_obj.db_prov_type
        if 'prov_label' in class_dict:
            res = class_dict['prov_label'](old_obj, trans_dict)
            new_obj.db_prov_label = res
        elif hasattr(old_obj, 'db_prov_label') and old_obj.db_prov_label is not None:
            new_obj.db_prov_label = old_obj.db_prov_label
        if 'prov_value' in class_dict:
            res = class_dict['prov_value'](old_obj, trans_dict)
            new_obj.db_prov_value = res
        elif hasattr(old_obj, 'db_prov_value') and old_obj.db_prov_value is not None:
            new_obj.db_prov_value = old_obj.db_prov_value
        if 'vt_id' in class_dict:
            res = class_dict['vt_id'](old_obj, trans_dict)
            new_obj.db_vt_id = res
        elif hasattr(old_obj, 'db_vt_id') and old_obj.db_vt_id is not None:
            new_obj.db_vt_id = old_obj.db_vt_id
        if 'vt_type' in class_dict:
            res = class_dict['vt_type'](old_obj, trans_dict)
            new_obj.db_vt_type = res
        elif hasattr(old_obj, 'db_vt_type') and old_obj.db_vt_type is not None:
            new_obj.db_vt_type = old_obj.db_vt_type
        if 'vt_desc' in class_dict:
            res = class_dict['vt_desc'](old_obj, trans_dict)
            new_obj.db_vt_desc = res
        elif hasattr(old_obj, 'db_vt_desc') and old_obj.db_vt_desc is not None:
            new_obj.db_vt_desc = old_obj.db_vt_desc
        if 'vt_package' in class_dict:
            res = class_dict['vt_package'](old_obj, trans_dict)
            new_obj.db_vt_package = res
        elif hasattr(old_obj, 'db_vt_package') and old_obj.db_vt_package is not None:
            new_obj.db_vt_package = old_obj.db_vt_package
        if 'vt_version' in class_dict:
            res = class_dict['vt_version'](old_obj, trans_dict)
            new_obj.db_vt_version = res
        elif hasattr(old_obj, 'db_vt_version') and old_obj.db_vt_version is not None:
            new_obj.db_vt_version = old_obj.db_vt_version
        if 'vt_cache' in class_dict:
            res = class_dict['vt_cache'](old_obj, trans_dict)
            new_obj.db_vt_cache = res
        elif hasattr(old_obj, 'db_vt_cache') and old_obj.db_vt_cache is not None:
            new_obj.db_vt_cache = old_obj.db_vt_cache
        if 'vt_location_x' in class_dict:
            res = class_dict['vt_location_x'](old_obj, trans_dict)
            new_obj.db_vt_location_x = res
        elif hasattr(old_obj, 'db_vt_location_x') and old_obj.db_vt_location_x is not None:
            new_obj.db_vt_location_x = old_obj.db_vt_location_x
        if 'vt_location_y' in class_dict:
            res = class_dict['vt_location_y'](old_obj, trans_dict)
            new_obj.db_vt_location_y = res
        elif hasattr(old_obj, 'db_vt_location_y') and old_obj.db_vt_location_y is not None:
            new_obj.db_vt_location_y = old_obj.db_vt_location_y
        if 'is_part_of' in class_dict:
            res = class_dict['is_part_of'](old_obj, trans_dict)
            new_obj.db_is_part_of = res
        elif hasattr(old_obj, 'db_is_part_of') and old_obj.db_is_part_of is not None:
            obj = old_obj.db_is_part_of
            new_obj.db_add_is_part_of(DBIsPartOf.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_is_part_of') and hasattr(new_obj, 'db_deleted_is_part_of'):
            for obj in old_obj.db_deleted_is_part_of:
                n_obj = DBIsPartOf.update_version(obj, trans_dict)
                new_obj.db_deleted_is_part_of.append(n_obj)
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        children = []
        if self._db_is_part_of is not None:
            children.extend(self._db_is_part_of.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                self._db_is_part_of = None
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_is_part_of)
        if remove:
            self.db_deleted_is_part_of = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        if self._db_is_part_of is not None and self._db_is_part_of.has_changes():
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
    
    def __get_db_prov_type(self):
        return self._db_prov_type
    def __set_db_prov_type(self, prov_type):
        self._db_prov_type = prov_type
        self.is_dirty = True
    db_prov_type = property(__get_db_prov_type, __set_db_prov_type)
    def db_add_prov_type(self, prov_type):
        self._db_prov_type = prov_type
    def db_change_prov_type(self, prov_type):
        self._db_prov_type = prov_type
    def db_delete_prov_type(self, prov_type):
        self._db_prov_type = None
    
    def __get_db_prov_label(self):
        return self._db_prov_label
    def __set_db_prov_label(self, prov_label):
        self._db_prov_label = prov_label
        self.is_dirty = True
    db_prov_label = property(__get_db_prov_label, __set_db_prov_label)
    def db_add_prov_label(self, prov_label):
        self._db_prov_label = prov_label
    def db_change_prov_label(self, prov_label):
        self._db_prov_label = prov_label
    def db_delete_prov_label(self, prov_label):
        self._db_prov_label = None
    
    def __get_db_prov_value(self):
        return self._db_prov_value
    def __set_db_prov_value(self, prov_value):
        self._db_prov_value = prov_value
        self.is_dirty = True
    db_prov_value = property(__get_db_prov_value, __set_db_prov_value)
    def db_add_prov_value(self, prov_value):
        self._db_prov_value = prov_value
    def db_change_prov_value(self, prov_value):
        self._db_prov_value = prov_value
    def db_delete_prov_value(self, prov_value):
        self._db_prov_value = None
    
    def __get_db_vt_id(self):
        return self._db_vt_id
    def __set_db_vt_id(self, vt_id):
        self._db_vt_id = vt_id
        self.is_dirty = True
    db_vt_id = property(__get_db_vt_id, __set_db_vt_id)
    def db_add_vt_id(self, vt_id):
        self._db_vt_id = vt_id
    def db_change_vt_id(self, vt_id):
        self._db_vt_id = vt_id
    def db_delete_vt_id(self, vt_id):
        self._db_vt_id = None
    
    def __get_db_vt_type(self):
        return self._db_vt_type
    def __set_db_vt_type(self, vt_type):
        self._db_vt_type = vt_type
        self.is_dirty = True
    db_vt_type = property(__get_db_vt_type, __set_db_vt_type)
    def db_add_vt_type(self, vt_type):
        self._db_vt_type = vt_type
    def db_change_vt_type(self, vt_type):
        self._db_vt_type = vt_type
    def db_delete_vt_type(self, vt_type):
        self._db_vt_type = None
    
    def __get_db_vt_desc(self):
        return self._db_vt_desc
    def __set_db_vt_desc(self, vt_desc):
        self._db_vt_desc = vt_desc
        self.is_dirty = True
    db_vt_desc = property(__get_db_vt_desc, __set_db_vt_desc)
    def db_add_vt_desc(self, vt_desc):
        self._db_vt_desc = vt_desc
    def db_change_vt_desc(self, vt_desc):
        self._db_vt_desc = vt_desc
    def db_delete_vt_desc(self, vt_desc):
        self._db_vt_desc = None
    
    def __get_db_vt_package(self):
        return self._db_vt_package
    def __set_db_vt_package(self, vt_package):
        self._db_vt_package = vt_package
        self.is_dirty = True
    db_vt_package = property(__get_db_vt_package, __set_db_vt_package)
    def db_add_vt_package(self, vt_package):
        self._db_vt_package = vt_package
    def db_change_vt_package(self, vt_package):
        self._db_vt_package = vt_package
    def db_delete_vt_package(self, vt_package):
        self._db_vt_package = None
    
    def __get_db_vt_version(self):
        return self._db_vt_version
    def __set_db_vt_version(self, vt_version):
        self._db_vt_version = vt_version
        self.is_dirty = True
    db_vt_version = property(__get_db_vt_version, __set_db_vt_version)
    def db_add_vt_version(self, vt_version):
        self._db_vt_version = vt_version
    def db_change_vt_version(self, vt_version):
        self._db_vt_version = vt_version
    def db_delete_vt_version(self, vt_version):
        self._db_vt_version = None
    
    def __get_db_vt_cache(self):
        return self._db_vt_cache
    def __set_db_vt_cache(self, vt_cache):
        self._db_vt_cache = vt_cache
        self.is_dirty = True
    db_vt_cache = property(__get_db_vt_cache, __set_db_vt_cache)
    def db_add_vt_cache(self, vt_cache):
        self._db_vt_cache = vt_cache
    def db_change_vt_cache(self, vt_cache):
        self._db_vt_cache = vt_cache
    def db_delete_vt_cache(self, vt_cache):
        self._db_vt_cache = None
    
    def __get_db_vt_location_x(self):
        return self._db_vt_location_x
    def __set_db_vt_location_x(self, vt_location_x):
        self._db_vt_location_x = vt_location_x
        self.is_dirty = True
    db_vt_location_x = property(__get_db_vt_location_x, __set_db_vt_location_x)
    def db_add_vt_location_x(self, vt_location_x):
        self._db_vt_location_x = vt_location_x
    def db_change_vt_location_x(self, vt_location_x):
        self._db_vt_location_x = vt_location_x
    def db_delete_vt_location_x(self, vt_location_x):
        self._db_vt_location_x = None
    
    def __get_db_vt_location_y(self):
        return self._db_vt_location_y
    def __set_db_vt_location_y(self, vt_location_y):
        self._db_vt_location_y = vt_location_y
        self.is_dirty = True
    db_vt_location_y = property(__get_db_vt_location_y, __set_db_vt_location_y)
    def db_add_vt_location_y(self, vt_location_y):
        self._db_vt_location_y = vt_location_y
    def db_change_vt_location_y(self, vt_location_y):
        self._db_vt_location_y = vt_location_y
    def db_delete_vt_location_y(self, vt_location_y):
        self._db_vt_location_y = None
    
    def __get_db_is_part_of(self):
        return self._db_is_part_of
    def __set_db_is_part_of(self, is_part_of):
        self._db_is_part_of = is_part_of
        self.is_dirty = True
    db_is_part_of = property(__get_db_is_part_of, __set_db_is_part_of)
    def db_add_is_part_of(self, is_part_of):
        self._db_is_part_of = is_part_of
    def db_change_is_part_of(self, is_part_of):
        self._db_is_part_of = is_part_of
    def db_delete_is_part_of(self, is_part_of):
        if not self.is_new:
            self.db_deleted_is_part_of.append(self._db_is_part_of)
        self._db_is_part_of = None
    
    def getPrimaryKey(self):
        return self._db_id

class DBAnnotation(object):

    vtType = 'annotation'

    def __init__(self, id=None, key=None, value=None):
        self._db_id = id
        self._db_key = key
        self._db_value = value
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBAnnotation.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBAnnotation(id=self._db_id,
                          key=self._db_key,
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
            new_obj = DBAnnotation()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'key' in class_dict:
            res = class_dict['key'](old_obj, trans_dict)
            new_obj.db_key = res
        elif hasattr(old_obj, 'db_key') and old_obj.db_key is not None:
            new_obj.db_key = old_obj.db_key
        if 'value' in class_dict:
            res = class_dict['value'](old_obj, trans_dict)
            new_obj.db_value = res
        elif hasattr(old_obj, 'db_value') and old_obj.db_value is not None:
            new_obj.db_value = old_obj.db_value
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
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
    
    def __get_db_key(self):
        return self._db_key
    def __set_db_key(self, key):
        self._db_key = key
        self.is_dirty = True
    db_key = property(__get_db_key, __set_db_key)
    def db_add_key(self, key):
        self._db_key = key
    def db_change_key(self, key):
        self._db_key = key
    def db_delete_key(self, key):
        self._db_key = None
    
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

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
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
    


class DBParameterExploration(object):

    vtType = 'parameter_exploration'

    def __init__(self, id=None, action_id=None, name=None, date=None, user=None, dims=None, layout=None, functions=None):
        self._db_id = id
        self._db_action_id = action_id
        self._db_name = name
        self._db_date = date
        self._db_user = user
        self._db_dims = dims
        self._db_layout = layout
        self.db_deleted_functions = []
        self.db_functions_id_index = {}
        if functions is None:
            self._db_functions = []
        else:
            self._db_functions = functions
            for v in self._db_functions:
                self.db_functions_id_index[v.db_id] = v
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBParameterExploration.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBParameterExploration(id=self._db_id,
                                    action_id=self._db_action_id,
                                    name=self._db_name,
                                    date=self._db_date,
                                    user=self._db_user,
                                    dims=self._db_dims,
                                    layout=self._db_layout)
        if self._db_functions is None:
            cp._db_functions = []
        else:
            cp._db_functions = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_functions]
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
            if hasattr(self, 'db_action_id') and ('action', self._db_action_id) in id_remap:
                cp._db_action_id = id_remap[('action', self._db_action_id)]
        
        # recreate indices and set flags
        cp.db_functions_id_index = dict((v.db_id, v) for v in cp._db_functions)
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBParameterExploration()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'action_id' in class_dict:
            res = class_dict['action_id'](old_obj, trans_dict)
            new_obj.db_action_id = res
        elif hasattr(old_obj, 'db_action_id') and old_obj.db_action_id is not None:
            new_obj.db_action_id = old_obj.db_action_id
        if 'name' in class_dict:
            res = class_dict['name'](old_obj, trans_dict)
            new_obj.db_name = res
        elif hasattr(old_obj, 'db_name') and old_obj.db_name is not None:
            new_obj.db_name = old_obj.db_name
        if 'date' in class_dict:
            res = class_dict['date'](old_obj, trans_dict)
            new_obj.db_date = res
        elif hasattr(old_obj, 'db_date') and old_obj.db_date is not None:
            new_obj.db_date = old_obj.db_date
        if 'user' in class_dict:
            res = class_dict['user'](old_obj, trans_dict)
            new_obj.db_user = res
        elif hasattr(old_obj, 'db_user') and old_obj.db_user is not None:
            new_obj.db_user = old_obj.db_user
        if 'dims' in class_dict:
            res = class_dict['dims'](old_obj, trans_dict)
            new_obj.db_dims = res
        elif hasattr(old_obj, 'db_dims') and old_obj.db_dims is not None:
            new_obj.db_dims = old_obj.db_dims
        if 'layout' in class_dict:
            res = class_dict['layout'](old_obj, trans_dict)
            new_obj.db_layout = res
        elif hasattr(old_obj, 'db_layout') and old_obj.db_layout is not None:
            new_obj.db_layout = old_obj.db_layout
        if 'functions' in class_dict:
            res = class_dict['functions'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_function(obj)
        elif hasattr(old_obj, 'db_functions') and old_obj.db_functions is not None:
            for obj in old_obj.db_functions:
                new_obj.db_add_function(DBPEFunction.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_functions') and hasattr(new_obj, 'db_deleted_functions'):
            for obj in old_obj.db_deleted_functions:
                n_obj = DBPEFunction.update_version(obj, trans_dict)
                new_obj.db_deleted_functions.append(n_obj)
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        children = []
        to_del = []
        for child in self.db_functions:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_function(child)
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_functions)
        if remove:
            self.db_deleted_functions = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        for child in self._db_functions:
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
    
    def __get_db_action_id(self):
        return self._db_action_id
    def __set_db_action_id(self, action_id):
        self._db_action_id = action_id
        self.is_dirty = True
    db_action_id = property(__get_db_action_id, __set_db_action_id)
    def db_add_action_id(self, action_id):
        self._db_action_id = action_id
    def db_change_action_id(self, action_id):
        self._db_action_id = action_id
    def db_delete_action_id(self, action_id):
        self._db_action_id = None
    
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
    
    def __get_db_date(self):
        return self._db_date
    def __set_db_date(self, date):
        self._db_date = date
        self.is_dirty = True
    db_date = property(__get_db_date, __set_db_date)
    def db_add_date(self, date):
        self._db_date = date
    def db_change_date(self, date):
        self._db_date = date
    def db_delete_date(self, date):
        self._db_date = None
    
    def __get_db_user(self):
        return self._db_user
    def __set_db_user(self, user):
        self._db_user = user
        self.is_dirty = True
    db_user = property(__get_db_user, __set_db_user)
    def db_add_user(self, user):
        self._db_user = user
    def db_change_user(self, user):
        self._db_user = user
    def db_delete_user(self, user):
        self._db_user = None
    
    def __get_db_dims(self):
        return self._db_dims
    def __set_db_dims(self, dims):
        self._db_dims = dims
        self.is_dirty = True
    db_dims = property(__get_db_dims, __set_db_dims)
    def db_add_dims(self, dims):
        self._db_dims = dims
    def db_change_dims(self, dims):
        self._db_dims = dims
    def db_delete_dims(self, dims):
        self._db_dims = None
    
    def __get_db_layout(self):
        return self._db_layout
    def __set_db_layout(self, layout):
        self._db_layout = layout
        self.is_dirty = True
    db_layout = property(__get_db_layout, __set_db_layout)
    def db_add_layout(self, layout):
        self._db_layout = layout
    def db_change_layout(self, layout):
        self._db_layout = layout
    def db_delete_layout(self, layout):
        self._db_layout = None
    
    def __get_db_functions(self):
        return self._db_functions
    def __set_db_functions(self, functions):
        self._db_functions = functions
        self.is_dirty = True
    db_functions = property(__get_db_functions, __set_db_functions)
    def db_get_functions(self):
        return self._db_functions
    def db_add_function(self, function):
        self.is_dirty = True
        self._db_functions.append(function)
        self.db_functions_id_index[function.db_id] = function
    def db_change_function(self, function):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_functions)):
            if self._db_functions[i].db_id == function.db_id:
                self._db_functions[i] = function
                found = True
                break
        if not found:
            self._db_functions.append(function)
        self.db_functions_id_index[function.db_id] = function
    def db_delete_function(self, function):
        self.is_dirty = True
        for i in xrange(len(self._db_functions)):
            if self._db_functions[i].db_id == function.db_id:
                if not self._db_functions[i].is_new:
                    self.db_deleted_functions.append(self._db_functions[i])
                del self._db_functions[i]
                break
        del self.db_functions_id_index[function.db_id]
    def db_get_function(self, key):
        for i in xrange(len(self._db_functions)):
            if self._db_functions[i].db_id == key:
                return self._db_functions[i]
        return None
    def db_get_function_by_id(self, key):
        return self.db_functions_id_index[key]
    def db_has_function_with_id(self, key):
        return key in self.db_functions_id_index
    
    def getPrimaryKey(self):
        return self._db_id

class DBMashupActionAnnotation(object):

    vtType = 'mashup_actionAnnotation'

    def __init__(self, id=None, key=None, value=None, action_id=None, date=None, user=None):
        self._db_id = id
        self._db_key = key
        self._db_value = value
        self._db_action_id = action_id
        self._db_date = date
        self._db_user = user
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBMashupActionAnnotation.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBMashupActionAnnotation(id=self._db_id,
                                      key=self._db_key,
                                      value=self._db_value,
                                      action_id=self._db_action_id,
                                      date=self._db_date,
                                      user=self._db_user)
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
            if hasattr(self, 'db_action_id') and ('mashup_action', self._db_action_id) in id_remap:
                cp._db_action_id = id_remap[('mashup_action', self._db_action_id)]
        
        # recreate indices and set flags
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBMashupActionAnnotation()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'key' in class_dict:
            res = class_dict['key'](old_obj, trans_dict)
            new_obj.db_key = res
        elif hasattr(old_obj, 'db_key') and old_obj.db_key is not None:
            new_obj.db_key = old_obj.db_key
        if 'value' in class_dict:
            res = class_dict['value'](old_obj, trans_dict)
            new_obj.db_value = res
        elif hasattr(old_obj, 'db_value') and old_obj.db_value is not None:
            new_obj.db_value = old_obj.db_value
        if 'action_id' in class_dict:
            res = class_dict['action_id'](old_obj, trans_dict)
            new_obj.db_action_id = res
        elif hasattr(old_obj, 'db_action_id') and old_obj.db_action_id is not None:
            new_obj.db_action_id = old_obj.db_action_id
        if 'date' in class_dict:
            res = class_dict['date'](old_obj, trans_dict)
            new_obj.db_date = res
        elif hasattr(old_obj, 'db_date') and old_obj.db_date is not None:
            new_obj.db_date = old_obj.db_date
        if 'user' in class_dict:
            res = class_dict['user'](old_obj, trans_dict)
            new_obj.db_user = res
        elif hasattr(old_obj, 'db_user') and old_obj.db_user is not None:
            new_obj.db_user = old_obj.db_user
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
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
    
    def __get_db_key(self):
        return self._db_key
    def __set_db_key(self, key):
        self._db_key = key
        self.is_dirty = True
    db_key = property(__get_db_key, __set_db_key)
    def db_add_key(self, key):
        self._db_key = key
    def db_change_key(self, key):
        self._db_key = key
    def db_delete_key(self, key):
        self._db_key = None
    
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
    
    def __get_db_action_id(self):
        return self._db_action_id
    def __set_db_action_id(self, action_id):
        self._db_action_id = action_id
        self.is_dirty = True
    db_action_id = property(__get_db_action_id, __set_db_action_id)
    def db_add_action_id(self, action_id):
        self._db_action_id = action_id
    def db_change_action_id(self, action_id):
        self._db_action_id = action_id
    def db_delete_action_id(self, action_id):
        self._db_action_id = None
    
    def __get_db_date(self):
        return self._db_date
    def __set_db_date(self, date):
        self._db_date = date
        self.is_dirty = True
    db_date = property(__get_db_date, __set_db_date)
    def db_add_date(self, date):
        self._db_date = date
    def db_change_date(self, date):
        self._db_date = date
    def db_delete_date(self, date):
        self._db_date = None
    
    def __get_db_user(self):
        return self._db_user
    def __set_db_user(self, user):
        self._db_user = user
        self.is_dirty = True
    db_user = property(__get_db_user, __set_db_user)
    def db_add_user(self, user):
        self._db_user = user
    def db_change_user(self, user):
        self._db_user = user
    def db_delete_user(self, user):
        self._db_user = None
    
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

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        children = []
        if self._db_value is not None:
            children.extend(self._db_value.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                self._db_value = None
        to_del = []
        for child in self.db_accounts:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
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

class DBDisabledPackages(object):

    vtType = 'disabled_packages'

    def __init__(self, packages=None):
        self.db_deleted_packages = []
        self.db_packages_name_index = {}
        if packages is None:
            self._db_packages = []
        else:
            self._db_packages = packages
            for v in self._db_packages:
                self.db_packages_name_index[v.db_name] = v
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBDisabledPackages.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBDisabledPackages()
        if self._db_packages is None:
            cp._db_packages = []
        else:
            cp._db_packages = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_packages]
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
        
        # recreate indices and set flags
        cp.db_packages_name_index = dict((v.db_name, v) for v in cp._db_packages)
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBDisabledPackages()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'packages' in class_dict:
            res = class_dict['packages'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_package(obj)
        elif hasattr(old_obj, 'db_packages') and old_obj.db_packages is not None:
            for obj in old_obj.db_packages:
                new_obj.db_add_package(DBStartupPackage.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_packages') and hasattr(new_obj, 'db_deleted_packages'):
            for obj in old_obj.db_deleted_packages:
                n_obj = DBStartupPackage.update_version(obj, trans_dict)
                new_obj.db_deleted_packages.append(n_obj)
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        children = []
        to_del = []
        for child in self.db_packages:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_package(child)
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_packages)
        if remove:
            self.db_deleted_packages = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        for child in self._db_packages:
            if child.has_changes():
                return True
        return False
    def __get_db_packages(self):
        return self._db_packages
    def __set_db_packages(self, packages):
        self._db_packages = packages
        self.is_dirty = True
    db_packages = property(__get_db_packages, __set_db_packages)
    def db_get_packages(self):
        return self._db_packages
    def db_add_package(self, package):
        self.is_dirty = True
        self._db_packages.append(package)
        self.db_packages_name_index[package.db_name] = package
    def db_change_package(self, package):
        self.is_dirty = True
        self._db_packages.append(package)
        self.db_packages_name_index[package.db_name] = package
    def db_delete_package(self, package):
        self.is_dirty = True
        raise Exception('Cannot delete a non-keyed object')
    def db_get_package(self, key):
        return None
    def db_get_package_by_name(self, key):
        return self.db_packages_name_index[key]
    def db_has_package_with_name(self, key):
        return key in self.db_packages_name_index
    


class DBModuleExec(object):

    vtType = 'module_exec'

    def __init__(self, id=None, ts_start=None, ts_end=None, cached=None, module_id=None, module_name=None, completed=None, error=None, machine_id=None, annotations=None, loop_execs=None):
        self._db_id = id
        self._db_ts_start = ts_start
        self._db_ts_end = ts_end
        self._db_cached = cached
        self._db_module_id = module_id
        self._db_module_name = module_name
        self._db_completed = completed
        self._db_error = error
        self._db_machine_id = machine_id
        self.db_deleted_annotations = []
        self.db_annotations_id_index = {}
        if annotations is None:
            self._db_annotations = []
        else:
            self._db_annotations = annotations
            for v in self._db_annotations:
                self.db_annotations_id_index[v.db_id] = v
        self.db_deleted_loop_execs = []
        self.db_loop_execs_id_index = {}
        if loop_execs is None:
            self._db_loop_execs = []
        else:
            self._db_loop_execs = loop_execs
            for v in self._db_loop_execs:
                self.db_loop_execs_id_index[v.db_id] = v
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBModuleExec.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBModuleExec(id=self._db_id,
                          ts_start=self._db_ts_start,
                          ts_end=self._db_ts_end,
                          cached=self._db_cached,
                          module_id=self._db_module_id,
                          module_name=self._db_module_name,
                          completed=self._db_completed,
                          error=self._db_error,
                          machine_id=self._db_machine_id)
        if self._db_annotations is None:
            cp._db_annotations = []
        else:
            cp._db_annotations = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_annotations]
        if self._db_loop_execs is None:
            cp._db_loop_execs = []
        else:
            cp._db_loop_execs = [v.do_copy(new_ids, id_scope, id_remap) for v in self._db_loop_execs]
        
        # set new ids
        if new_ids:
            new_id = id_scope.getNewId(self.vtType)
            if self.vtType in id_scope.remap:
                id_remap[(id_scope.remap[self.vtType], self.db_id)] = new_id
            else:
                id_remap[(self.vtType, self.db_id)] = new_id
            cp.db_id = new_id
            if hasattr(self, 'db_module_id') and ('module', self._db_module_id) in id_remap:
                cp._db_module_id = id_remap[('module', self._db_module_id)]
            if hasattr(self, 'db_machine_id') and ('machine', self._db_machine_id) in id_remap:
                cp._db_machine_id = id_remap[('machine', self._db_machine_id)]
        
        # recreate indices and set flags
        cp.db_annotations_id_index = dict((v.db_id, v) for v in cp._db_annotations)
        cp.db_loop_execs_id_index = dict((v.db_id, v) for v in cp._db_loop_execs)
        if not new_ids:
            cp.is_dirty = self.is_dirty
            cp.is_new = self.is_new
        return cp

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBModuleExec()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'id' in class_dict:
            res = class_dict['id'](old_obj, trans_dict)
            new_obj.db_id = res
        elif hasattr(old_obj, 'db_id') and old_obj.db_id is not None:
            new_obj.db_id = old_obj.db_id
        if 'ts_start' in class_dict:
            res = class_dict['ts_start'](old_obj, trans_dict)
            new_obj.db_ts_start = res
        elif hasattr(old_obj, 'db_ts_start') and old_obj.db_ts_start is not None:
            new_obj.db_ts_start = old_obj.db_ts_start
        if 'ts_end' in class_dict:
            res = class_dict['ts_end'](old_obj, trans_dict)
            new_obj.db_ts_end = res
        elif hasattr(old_obj, 'db_ts_end') and old_obj.db_ts_end is not None:
            new_obj.db_ts_end = old_obj.db_ts_end
        if 'cached' in class_dict:
            res = class_dict['cached'](old_obj, trans_dict)
            new_obj.db_cached = res
        elif hasattr(old_obj, 'db_cached') and old_obj.db_cached is not None:
            new_obj.db_cached = old_obj.db_cached
        if 'module_id' in class_dict:
            res = class_dict['module_id'](old_obj, trans_dict)
            new_obj.db_module_id = res
        elif hasattr(old_obj, 'db_module_id') and old_obj.db_module_id is not None:
            new_obj.db_module_id = old_obj.db_module_id
        if 'module_name' in class_dict:
            res = class_dict['module_name'](old_obj, trans_dict)
            new_obj.db_module_name = res
        elif hasattr(old_obj, 'db_module_name') and old_obj.db_module_name is not None:
            new_obj.db_module_name = old_obj.db_module_name
        if 'completed' in class_dict:
            res = class_dict['completed'](old_obj, trans_dict)
            new_obj.db_completed = res
        elif hasattr(old_obj, 'db_completed') and old_obj.db_completed is not None:
            new_obj.db_completed = old_obj.db_completed
        if 'error' in class_dict:
            res = class_dict['error'](old_obj, trans_dict)
            new_obj.db_error = res
        elif hasattr(old_obj, 'db_error') and old_obj.db_error is not None:
            new_obj.db_error = old_obj.db_error
        if 'machine_id' in class_dict:
            res = class_dict['machine_id'](old_obj, trans_dict)
            new_obj.db_machine_id = res
        elif hasattr(old_obj, 'db_machine_id') and old_obj.db_machine_id is not None:
            new_obj.db_machine_id = old_obj.db_machine_id
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
        if 'loop_execs' in class_dict:
            res = class_dict['loop_execs'](old_obj, trans_dict)
            for obj in res:
                new_obj.db_add_loop_exec(obj)
        elif hasattr(old_obj, 'db_loop_execs') and old_obj.db_loop_execs is not None:
            for obj in old_obj.db_loop_execs:
                new_obj.db_add_loop_exec(DBLoopExec.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_loop_execs') and hasattr(new_obj, 'db_deleted_loop_execs'):
            for obj in old_obj.db_deleted_loop_execs:
                n_obj = DBLoopExec.update_version(obj, trans_dict)
                new_obj.db_deleted_loop_execs.append(n_obj)
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        children = []
        to_del = []
        for child in self.db_annotations:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_annotation(child)
        to_del = []
        for child in self.db_loop_execs:
            children.extend(child.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_loop_exec(child)
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_annotations)
        children.extend(self.db_deleted_loop_execs)
        if remove:
            self.db_deleted_annotations = []
            self.db_deleted_loop_execs = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        for child in self._db_annotations:
            if child.has_changes():
                return True
        for child in self._db_loop_execs:
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
    
    def __get_db_ts_start(self):
        return self._db_ts_start
    def __set_db_ts_start(self, ts_start):
        self._db_ts_start = ts_start
        self.is_dirty = True
    db_ts_start = property(__get_db_ts_start, __set_db_ts_start)
    def db_add_ts_start(self, ts_start):
        self._db_ts_start = ts_start
    def db_change_ts_start(self, ts_start):
        self._db_ts_start = ts_start
    def db_delete_ts_start(self, ts_start):
        self._db_ts_start = None
    
    def __get_db_ts_end(self):
        return self._db_ts_end
    def __set_db_ts_end(self, ts_end):
        self._db_ts_end = ts_end
        self.is_dirty = True
    db_ts_end = property(__get_db_ts_end, __set_db_ts_end)
    def db_add_ts_end(self, ts_end):
        self._db_ts_end = ts_end
    def db_change_ts_end(self, ts_end):
        self._db_ts_end = ts_end
    def db_delete_ts_end(self, ts_end):
        self._db_ts_end = None
    
    def __get_db_cached(self):
        return self._db_cached
    def __set_db_cached(self, cached):
        self._db_cached = cached
        self.is_dirty = True
    db_cached = property(__get_db_cached, __set_db_cached)
    def db_add_cached(self, cached):
        self._db_cached = cached
    def db_change_cached(self, cached):
        self._db_cached = cached
    def db_delete_cached(self, cached):
        self._db_cached = None
    
    def __get_db_module_id(self):
        return self._db_module_id
    def __set_db_module_id(self, module_id):
        self._db_module_id = module_id
        self.is_dirty = True
    db_module_id = property(__get_db_module_id, __set_db_module_id)
    def db_add_module_id(self, module_id):
        self._db_module_id = module_id
    def db_change_module_id(self, module_id):
        self._db_module_id = module_id
    def db_delete_module_id(self, module_id):
        self._db_module_id = None
    
    def __get_db_module_name(self):
        return self._db_module_name
    def __set_db_module_name(self, module_name):
        self._db_module_name = module_name
        self.is_dirty = True
    db_module_name = property(__get_db_module_name, __set_db_module_name)
    def db_add_module_name(self, module_name):
        self._db_module_name = module_name
    def db_change_module_name(self, module_name):
        self._db_module_name = module_name
    def db_delete_module_name(self, module_name):
        self._db_module_name = None
    
    def __get_db_completed(self):
        return self._db_completed
    def __set_db_completed(self, completed):
        self._db_completed = completed
        self.is_dirty = True
    db_completed = property(__get_db_completed, __set_db_completed)
    def db_add_completed(self, completed):
        self._db_completed = completed
    def db_change_completed(self, completed):
        self._db_completed = completed
    def db_delete_completed(self, completed):
        self._db_completed = None
    
    def __get_db_error(self):
        return self._db_error
    def __set_db_error(self, error):
        self._db_error = error
        self.is_dirty = True
    db_error = property(__get_db_error, __set_db_error)
    def db_add_error(self, error):
        self._db_error = error
    def db_change_error(self, error):
        self._db_error = error
    def db_delete_error(self, error):
        self._db_error = None
    
    def __get_db_machine_id(self):
        return self._db_machine_id
    def __set_db_machine_id(self, machine_id):
        self._db_machine_id = machine_id
        self.is_dirty = True
    db_machine_id = property(__get_db_machine_id, __set_db_machine_id)
    def db_add_machine_id(self, machine_id):
        self._db_machine_id = machine_id
    def db_change_machine_id(self, machine_id):
        self._db_machine_id = machine_id
    def db_delete_machine_id(self, machine_id):
        self._db_machine_id = None
    
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
    def db_delete_annotation(self, annotation):
        self.is_dirty = True
        for i in xrange(len(self._db_annotations)):
            if self._db_annotations[i].db_id == annotation.db_id:
                if not self._db_annotations[i].is_new:
                    self.db_deleted_annotations.append(self._db_annotations[i])
                del self._db_annotations[i]
                break
        del self.db_annotations_id_index[annotation.db_id]
    def db_get_annotation(self, key):
        for i in xrange(len(self._db_annotations)):
            if self._db_annotations[i].db_id == key:
                return self._db_annotations[i]
        return None
    def db_get_annotation_by_id(self, key):
        return self.db_annotations_id_index[key]
    def db_has_annotation_with_id(self, key):
        return key in self.db_annotations_id_index
    
    def __get_db_loop_execs(self):
        return self._db_loop_execs
    def __set_db_loop_execs(self, loop_execs):
        self._db_loop_execs = loop_execs
        self.is_dirty = True
    db_loop_execs = property(__get_db_loop_execs, __set_db_loop_execs)
    def db_get_loop_execs(self):
        return self._db_loop_execs
    def db_add_loop_exec(self, loop_exec):
        self.is_dirty = True
        self._db_loop_execs.append(loop_exec)
        self.db_loop_execs_id_index[loop_exec.db_id] = loop_exec
    def db_change_loop_exec(self, loop_exec):
        self.is_dirty = True
        found = False
        for i in xrange(len(self._db_loop_execs)):
            if self._db_loop_execs[i].db_id == loop_exec.db_id:
                self._db_loop_execs[i] = loop_exec
                found = True
                break
        if not found:
            self._db_loop_execs.append(loop_exec)
        self.db_loop_execs_id_index[loop_exec.db_id] = loop_exec
    def db_delete_loop_exec(self, loop_exec):
        self.is_dirty = True
        for i in xrange(len(self._db_loop_execs)):
            if self._db_loop_execs[i].db_id == loop_exec.db_id:
                if not self._db_loop_execs[i].is_new:
                    self.db_deleted_loop_execs.append(self._db_loop_execs[i])
                del self._db_loop_execs[i]
                break
        del self.db_loop_execs_id_index[loop_exec.db_id]
    def db_get_loop_exec(self, key):
        for i in xrange(len(self._db_loop_execs)):
            if self._db_loop_execs[i].db_id == key:
                return self._db_loop_execs[i]
        return None
    def db_get_loop_exec_by_id(self, key):
        return self.db_loop_execs_id_index[key]
    def db_has_loop_exec_with_id(self, key):
        return key in self.db_loop_execs_id_index
    
    def getPrimaryKey(self):
        return self._db_id

class DBProvAssociation(object):

    vtType = 'prov_association'

    def __init__(self, prov_activity=None, prov_agent=None, prov_plan=None, prov_role=None):
        self.db_deleted_prov_activity = []
        self._db_prov_activity = prov_activity
        self.db_deleted_prov_agent = []
        self._db_prov_agent = prov_agent
        self.db_deleted_prov_plan = []
        self._db_prov_plan = prov_plan
        self._db_prov_role = prov_role
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBProvAssociation.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBProvAssociation(prov_role=self._db_prov_role)
        if self._db_prov_activity is not None:
            cp._db_prov_activity = self._db_prov_activity.do_copy(new_ids, id_scope, id_remap)
        if self._db_prov_agent is not None:
            cp._db_prov_agent = self._db_prov_agent.do_copy(new_ids, id_scope, id_remap)
        if self._db_prov_plan is not None:
            cp._db_prov_plan = self._db_prov_plan.do_copy(new_ids, id_scope, id_remap)
        
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
            new_obj = DBProvAssociation()
        class_dict = {}
        if new_obj.__class__.__name__ in trans_dict:
            class_dict = trans_dict[new_obj.__class__.__name__]
        if 'prov_activity' in class_dict:
            res = class_dict['prov_activity'](old_obj, trans_dict)
            new_obj.db_prov_activity = res
        elif hasattr(old_obj, 'db_prov_activity') and old_obj.db_prov_activity is not None:
            obj = old_obj.db_prov_activity
            new_obj.db_add_prov_activity(DBRefProvActivity.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_prov_activity') and hasattr(new_obj, 'db_deleted_prov_activity'):
            for obj in old_obj.db_deleted_prov_activity:
                n_obj = DBRefProvActivity.update_version(obj, trans_dict)
                new_obj.db_deleted_prov_activity.append(n_obj)
        if 'prov_agent' in class_dict:
            res = class_dict['prov_agent'](old_obj, trans_dict)
            new_obj.db_prov_agent = res
        elif hasattr(old_obj, 'db_prov_agent') and old_obj.db_prov_agent is not None:
            obj = old_obj.db_prov_agent
            new_obj.db_add_prov_agent(DBRefProvAgent.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_prov_agent') and hasattr(new_obj, 'db_deleted_prov_agent'):
            for obj in old_obj.db_deleted_prov_agent:
                n_obj = DBRefProvAgent.update_version(obj, trans_dict)
                new_obj.db_deleted_prov_agent.append(n_obj)
        if 'prov_plan' in class_dict:
            res = class_dict['prov_plan'](old_obj, trans_dict)
            new_obj.db_prov_plan = res
        elif hasattr(old_obj, 'db_prov_plan') and old_obj.db_prov_plan is not None:
            obj = old_obj.db_prov_plan
            new_obj.db_add_prov_plan(DBRefProvPlan.update_version(obj, trans_dict))
        if hasattr(old_obj, 'db_deleted_prov_plan') and hasattr(new_obj, 'db_deleted_prov_plan'):
            for obj in old_obj.db_deleted_prov_plan:
                n_obj = DBRefProvPlan.update_version(obj, trans_dict)
                new_obj.db_deleted_prov_plan.append(n_obj)
        if 'prov_role' in class_dict:
            res = class_dict['prov_role'](old_obj, trans_dict)
            new_obj.db_prov_role = res
        elif hasattr(old_obj, 'db_prov_role') and old_obj.db_prov_role is not None:
            new_obj.db_prov_role = old_obj.db_prov_role
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        children = []
        if self._db_prov_activity is not None:
            children.extend(self._db_prov_activity.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                self._db_prov_activity = None
        if self._db_prov_agent is not None:
            children.extend(self._db_prov_agent.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                self._db_prov_agent = None
        if self._db_prov_plan is not None:
            children.extend(self._db_prov_plan.db_children((self.vtType, self.db_id), orphan, for_action))
            if orphan:
                self._db_prov_plan = None
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_prov_activity)
        children.extend(self.db_deleted_prov_agent)
        children.extend(self.db_deleted_prov_plan)
        if remove:
            self.db_deleted_prov_activity = []
            self.db_deleted_prov_agent = []
            self.db_deleted_prov_plan = []
        return children
    def has_changes(self):
        if self.is_dirty:
            return True
        if self._db_prov_activity is not None and self._db_prov_activity.has_changes():
            return True
        if self._db_prov_agent is not None and self._db_prov_agent.has_changes():
            return True
        if self._db_prov_plan is not None and self._db_prov_plan.has_changes():
            return True
        return False
    def __get_db_prov_activity(self):
        return self._db_prov_activity
    def __set_db_prov_activity(self, prov_activity):
        self._db_prov_activity = prov_activity
        self.is_dirty = True
    db_prov_activity = property(__get_db_prov_activity, __set_db_prov_activity)
    def db_add_prov_activity(self, prov_activity):
        self._db_prov_activity = prov_activity
    def db_change_prov_activity(self, prov_activity):
        self._db_prov_activity = prov_activity
    def db_delete_prov_activity(self, prov_activity):
        if not self.is_new:
            self.db_deleted_prov_activity.append(self._db_prov_activity)
        self._db_prov_activity = None
    
    def __get_db_prov_agent(self):
        return self._db_prov_agent
    def __set_db_prov_agent(self, prov_agent):
        self._db_prov_agent = prov_agent
        self.is_dirty = True
    db_prov_agent = property(__get_db_prov_agent, __set_db_prov_agent)
    def db_add_prov_agent(self, prov_agent):
        self._db_prov_agent = prov_agent
    def db_change_prov_agent(self, prov_agent):
        self._db_prov_agent = prov_agent
    def db_delete_prov_agent(self, prov_agent):
        if not self.is_new:
            self.db_deleted_prov_agent.append(self._db_prov_agent)
        self._db_prov_agent = None
    
    def __get_db_prov_plan(self):
        return self._db_prov_plan
    def __set_db_prov_plan(self, prov_plan):
        self._db_prov_plan = prov_plan
        self.is_dirty = True
    db_prov_plan = property(__get_db_prov_plan, __set_db_prov_plan)
    def db_add_prov_plan(self, prov_plan):
        self._db_prov_plan = prov_plan
    def db_change_prov_plan(self, prov_plan):
        self._db_prov_plan = prov_plan
    def db_delete_prov_plan(self, prov_plan):
        if not self.is_new:
            self.db_deleted_prov_plan.append(self._db_prov_plan)
        self._db_prov_plan = None
    
    def __get_db_prov_role(self):
        return self._db_prov_role
    def __set_db_prov_role(self, prov_role):
        self._db_prov_role = prov_role
        self.is_dirty = True
    db_prov_role = property(__get_db_prov_role, __set_db_prov_role)
    def db_add_prov_role(self, prov_role):
        self._db_prov_role = prov_role
    def db_change_prov_role(self, prov_role):
        self._db_prov_role = prov_role
    def db_delete_prov_role(self, prov_role):
        self._db_prov_role = None
    


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

    def db_children(self, parent=(None,None), orphan=False, for_action=False):
        children = []
        if self._db_value is not None:
            children.extend(self._db_value.db_children((self.vtType, self.db_id), orphan, for_action))
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
    



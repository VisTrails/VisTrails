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

    def db_children(self, parent=(None,None), orphan=False):
        children = []
        to_del = []
        for child in self.db_ports:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
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
    


class DBPortSpec(object):

    vtType = 'portSpec'

    def __init__(self, id=None, name=None, type=None, optional=None, sort_key=None, sigstring=None):
        self._db_id = id
        self._db_name = name
        self._db_type = type
        self._db_optional = optional
        self._db_sort_key = sort_key
        self._db_sigstring = sigstring
        self.is_dirty = True
        self.is_new = True
    
    def __copy__(self):
        return DBPortSpec.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBPortSpec(id=self._db_id,
                        name=self._db_name,
                        type=self._db_type,
                        optional=self._db_optional,
                        sort_key=self._db_sort_key,
                        sigstring=self._db_sigstring)
        
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
        if 'sort_key' in class_dict:
            res = class_dict['sort_key'](old_obj, trans_dict)
            new_obj.db_sort_key = res
        elif hasattr(old_obj, 'db_sort_key') and old_obj.db_sort_key is not None:
            new_obj.db_sort_key = old_obj.db_sort_key
        if 'sigstring' in class_dict:
            res = class_dict['sigstring'](old_obj, trans_dict)
            new_obj.db_sigstring = res
        elif hasattr(old_obj, 'db_sigstring') and old_obj.db_sigstring is not None:
            new_obj.db_sigstring = old_obj.db_sigstring
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
    
    def __get_db_sigstring(self):
        return self._db_sigstring
    def __set_db_sigstring(self, sigstring):
        self._db_sigstring = sigstring
        self.is_dirty = True
    db_sigstring = property(__get_db_sigstring, __set_db_sigstring)
    def db_add_sigstring(self, sigstring):
        self._db_sigstring = sigstring
    def db_change_sigstring(self, sigstring):
        self._db_sigstring = sigstring
    def db_delete_sigstring(self, sigstring):
        self._db_sigstring = None
    
    def getPrimaryKey(self):
        return self._db_id

class DBModule(object):

    vtType = 'module'

    def __init__(self, id=None, cache=None, name=None, namespace=None, package=None, version=None, tag=None, location=None, functions=None, annotations=None, portSpecs=None):
        self._db_id = id
        self._db_cache = cache
        self._db_name = name
        self._db_namespace = namespace
        self._db_package = package
        self._db_version = version
        self._db_tag = tag
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
                      version=self._db_version,
                      tag=self._db_tag)
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
        if 'tag' in class_dict:
            res = class_dict['tag'](old_obj, trans_dict)
            new_obj.db_tag = res
        elif hasattr(old_obj, 'db_tag') and old_obj.db_tag is not None:
            new_obj.db_tag = old_obj.db_tag
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

    def db_children(self, parent=(None,None), orphan=False):
        children = []
        if self._db_location is not None:
            children.extend(self._db_location.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                self._db_location = None
        to_del = []
        for child in self.db_functions:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_function(child)
        to_del = []
        for child in self.db_annotations:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_annotation(child)
        to_del = []
        for child in self.db_portSpecs:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
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
        children.extend(self.db_deleted_portSpecs)
        if remove:
            self.db_deleted_location = []
            self.db_deleted_functions = []
            self.db_deleted_annotations = []
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
    
    def __get_db_tag(self):
        return self._db_tag
    def __set_db_tag(self, tag):
        self._db_tag = tag
        self.is_dirty = True
    db_tag = property(__get_db_tag, __set_db_tag)
    def db_add_tag(self, tag):
        self._db_tag = tag
    def db_change_tag(self, tag):
        self._db_tag = tag
    def db_delete_tag(self, tag):
        self._db_tag = None
    
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

class DBModuleDescriptor(object):

    vtType = 'module_descriptor'

    def __init__(self, id=None, name=None, package=None, namespace=None, version=None, base_descriptor_id=None, portSpecs=None):
        self._db_id = id
        self._db_name = name
        self._db_package = package
        self._db_namespace = namespace
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

    def db_children(self, parent=(None,None), orphan=False):
        children = []
        to_del = []
        for child in self.db_portSpecs:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
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

class DBGroup(object):

    vtType = 'group'

    def __init__(self, id=None, workflow=None, cache=None, name=None, namespace=None, package=None, version=None, tag=None, location=None, functions=None, annotations=None):
        self._db_id = id
        self.db_deleted_workflow = []
        self._db_workflow = workflow
        self._db_cache = cache
        self._db_name = name
        self._db_namespace = namespace
        self._db_package = package
        self._db_version = version
        self._db_tag = tag
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
                     version=self._db_version,
                     tag=self._db_tag)
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
        if 'tag' in class_dict:
            res = class_dict['tag'](old_obj, trans_dict)
            new_obj.db_tag = res
        elif hasattr(old_obj, 'db_tag') and old_obj.db_tag is not None:
            new_obj.db_tag = old_obj.db_tag
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
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False):
        children = []
        if self._db_location is not None:
            children.extend(self._db_location.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                self._db_location = None
        to_del = []
        for child in self.db_functions:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_function(child)
        to_del = []
        for child in self.db_annotations:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_annotation(child)
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_workflow)
        children.extend(self.db_deleted_location)
        children.extend(self.db_deleted_functions)
        children.extend(self.db_deleted_annotations)
        if remove:
            self.db_deleted_workflow = []
            self.db_deleted_location = []
            self.db_deleted_functions = []
            self.db_deleted_annotations = []
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
    
    def __get_db_tag(self):
        return self._db_tag
    def __set_db_tag(self, tag):
        self._db_tag = tag
        self.is_dirty = True
    db_tag = property(__get_db_tag, __set_db_tag)
    def db_add_tag(self, tag):
        self._db_tag = tag
    def db_change_tag(self, tag):
        self._db_tag = tag
    def db_delete_tag(self, tag):
        self._db_tag = None
    
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

    def db_children(self, parent=(None,None), orphan=False):
        children = []
        if self._db_data is not None:
            children.extend(self._db_data.db_children((self.vtType, self.db_id), orphan))
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

    def db_children(self, parent=(None,None), orphan=False):
        children = []
        to_del = []
        for child in self.db_parameters:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
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

class DBAbstraction(object):

    vtType = 'abstraction'

    def __init__(self, id=None, cache=None, name=None, namespace=None, package=None, version=None, internal_version=None, tag=None, location=None, functions=None, annotations=None):
        self._db_id = id
        self._db_cache = cache
        self._db_name = name
        self._db_namespace = namespace
        self._db_package = package
        self._db_version = version
        self._db_internal_version = internal_version
        self._db_tag = tag
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
                           internal_version=self._db_internal_version,
                           tag=self._db_tag)
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
        if 'tag' in class_dict:
            res = class_dict['tag'](old_obj, trans_dict)
            new_obj.db_tag = res
        elif hasattr(old_obj, 'db_tag') and old_obj.db_tag is not None:
            new_obj.db_tag = old_obj.db_tag
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
        new_obj.is_new = old_obj.is_new
        new_obj.is_dirty = old_obj.is_dirty
        return new_obj

    def db_children(self, parent=(None,None), orphan=False):
        children = []
        if self._db_location is not None:
            children.extend(self._db_location.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                self._db_location = None
        to_del = []
        for child in self.db_functions:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_function(child)
        to_del = []
        for child in self.db_annotations:
            children.extend(child.db_children((self.vtType, self.db_id), orphan))
            if orphan:
                to_del.append(child)
        for child in to_del:
            self.db_delete_annotation(child)
        children.append((self, parent[0], parent[1]))
        return children
    def db_deleted_children(self, remove=False):
        children = []
        children.extend(self.db_deleted_location)
        children.extend(self.db_deleted_functions)
        children.extend(self.db_deleted_annotations)
        if remove:
            self.db_deleted_location = []
            self.db_deleted_functions = []
            self.db_deleted_annotations = []
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
    
    def __get_db_tag(self):
        return self._db_tag
    def __set_db_tag(self, tag):
        self._db_tag = tag
        self.is_dirty = True
    db_tag = property(__get_db_tag, __set_db_tag)
    def db_add_tag(self, tag):
        self._db_tag = tag
    def db_change_tag(self, tag):
        self._db_tag = tag
    def db_delete_tag(self, tag):
        self._db_tag = None
    
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
    
    def getPrimaryKey(self):
        return self._db_id

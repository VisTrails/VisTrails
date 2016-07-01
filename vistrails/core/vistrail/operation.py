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

from vistrails.db.domain import DBAdd, DBChange, DBDelete
from vistrails.db.domain import DBAnnotation, DBAbstraction, DBConnection, DBGroup, \
    DBLocation, DBModule, DBFunction, DBPluginData, DBParameter, DBPort, \
    DBPortSpec, DBControlParameter

from vistrails.core.vistrail.annotation import Annotation
from vistrails.core.vistrail.abstraction import Abstraction
from vistrails.core.vistrail.connection import Connection
from vistrails.core.vistrail.group import Group
from vistrails.core.vistrail.location import Location
from vistrails.core.vistrail.module import Module
from vistrails.core.vistrail.module_control_param import ModuleControlParam
from vistrails.core.vistrail.module_function import ModuleFunction
from vistrails.core.vistrail.module_param import ModuleParam
from vistrails.core.vistrail.plugin_data import PluginData
from vistrails.core.vistrail.port import Port
from vistrails.core.vistrail.port_spec import PortSpec

import unittest
import copy
from vistrails.db.domain import IdScope
import vistrails.core

def convert_data(_data):
    map = {
        DBAnnotation.vtType: Annotation,
        DBAbstraction.vtType: Abstraction,
        DBConnection.vtType: Connection,
        DBLocation.vtType: Location,
        DBModule.vtType: Module,
        DBFunction.vtType: ModuleFunction,
        DBGroup.vtType: Group,
        DBParameter.vtType: ModuleParam,
        DBPluginData.vtType: PluginData,
        DBPort.vtType: Port,
        DBPortSpec.vtType: PortSpec,
        DBControlParameter.vtType: ModuleControlParam,
        }
    try:
        map[_data.vtType].convert(_data)
    except KeyError:
        raise TypeError('cannot convert data of type %s' % _data.vtType)

class AddOp(DBAdd):

    ##########################################################################
    # Constructors and copy

    def __init__(self, *args, **kwargs):
        DBAdd.__init__(self, *args, **kwargs)
    
    def __copy__(self):
        return AddOp.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBAdd.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = AddOp
        return cp

    @staticmethod
    def convert(_add_op):
        if _add_op.__class__ == AddOp:
            return
        _add_op.__class__ = AddOp
        if _add_op.data is not None:
            convert_data(_add_op.data)
    ##########################################################################
    # Properties

    id = DBAdd.db_id
    what = DBAdd.db_what
    objectId = DBAdd.db_objectId
    old_obj_id = DBAdd.db_objectId
    new_obj_id = DBAdd.db_objectId
    parentObjId = DBAdd.db_parentObjId
    parentObjType = DBAdd.db_parentObjType
    data = DBAdd.db_data

    ##########################################################################
    # Operators
    
    def __str__(self):
        """__str__() -> str - Returns a string representation of an Annotation
        object. 

        """
        
        rep = ("<add id=%s what=%s objectId=%s parentObjId=%s" + \
               " parentObjType=%s>") % (str(self.id), str(self.what), str(self.objectId),
                                        str(self.parentObjId), str(self.parentObjType))
        rep += str(self.data) + "</add>"
        return rep

    # FIXME expand this
    def __eq__(self, other):
        """ __eq__(other: AddOp) -> boolean
        Returns True if self and other have the same attributes. Used by == 
        operator. 
        
        """
        if type(other) != type(self):
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

class ChangeOp(DBChange):

    ##########################################################################
    # Constructors and copy

    def __init__(self, *args, **kwargs):
        DBChange.__init__(self, *args, **kwargs)

    def __copy__(self):
        return ChangeOp.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBChange.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = ChangeOp
        return cp
    
    @staticmethod
    def convert(_change_op):
        if _change_op.__class__ == ChangeOp:
            return
        _change_op.__class__ = ChangeOp
        if _change_op.data is not None:
            convert_data(_change_op.data)

    ##########################################################################
    # Properties
    
    id = DBChange.db_id
    what = DBChange.db_what
    oldObjId = DBChange.db_oldObjId
    old_obj_id = DBChange.db_oldObjId
    newObjId = DBChange.db_newObjId
    new_obj_id = DBChange.db_newObjId
    parentObjId = DBChange.db_parentObjId
    parentObjType = DBChange.db_parentObjType
    data = DBChange.db_data

    # def _get_id(self):
    #     return self.db_id
    # def _set_id(self, id):
    #     self.db_id = id
    # id = property(_get_id, _set_id)

    # def _get_what(self):
    #     return self.db_what
    # def _set_what(self, what):
    #     self.db_what = what
    # what = property(_get_what, _set_what)

    # def _get_oldObjId(self):
    #     return self.db_oldObjId
    # def _set_oldObjId(self, oldObjId):
    #     self.db_oldObjId = oldObjId
    # oldObjId = property(_get_oldObjId, _set_oldObjId)
    # old_obj_id = property(_get_oldObjId, _set_oldObjId)

    # def _get_newObjId(self):
    #     return self.db_newObjId
    # def _set_newObjId(self, newObjId):
    #     self.db_newObjId = newObjId
    # newObjId = property(_get_newObjId, _set_newObjId)
    # new_obj_id = property(_get_newObjId, _set_newObjId)

    # def _get_parentObjId(self):
    #     return self.db_parentObjId
    # def _set_parentObjId(self, parentObjId):
    #     self.db_parentObjId = parentObjId
    # parentObjId = property(_get_parentObjId, _set_parentObjId)

    # def _get_parentObjType(self):
    #     return self.db_parentObjType
    # def _set_parentObjType(self, parentObjType):
    #     self.db_parentObjType = parentObjType
    # parentObjType = property(_get_parentObjType, _set_parentObjType)

    # def _get_data(self):
    #     return self.db_data
    # def _set_data(self, data):
    #     self.db_data = data
    # data = property(_get_data, _set_data)

    ##########################################################################
    # Operators
    
    def __str__(self):
        """__str__() -> str - Returns a string representation of an Annotation
        object. 

        """
        rep = "<change id=%s what=%s oldId=%s newId=%s parentObjId=%s" + \
            " parentObjType=%s>" + str(self.data) + "</change>"
        return rep % (str(self.id), str(self.what), str(self.oldObjId),
                      str(self.newObjId), str(self.parentObjId), 
                      str(self.parentObjType))

    # FIXME expand this
    def __eq__(self, other):
        """ __eq__(other: ChangeOp) -> boolean
        Returns True if self and other have the same attributes. Used by == 
        operator. 
        
        """
        if type(other) != type(self):
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

class DeleteOp(DBDelete):

    ##########################################################################
    # Constructors and copy

    def __init__(self, *args, **kwargs):
        DBDelete.__init__(self, *args, **kwargs)
    
    def __copy__(self):
        return DeleteOp.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBDelete.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = DeleteOp
        return cp

    @staticmethod
    def convert(_delete_op):
        _delete_op.__class__ = DeleteOp

    ##########################################################################
    # Properties

    id = DBDelete.db_id
    what = DBDelete.db_what
    objectId = DBDelete.db_objectId
    old_obj_id = DBDelete.db_objectId
    new_obj_id = DBDelete.db_objectId
    parentObjId = DBDelete.db_parentObjId
    parentObjType = DBDelete.db_parentObjType

    # def _get_id(self):
    #     return self.db_id
    # def _set_id(self, id):
    #     self.db_id = id
    # id = property(_get_id, _set_id)

    # def _get_what(self):
    #     return self.db_what
    # def _set_what(self, what):
    #     self.db_what = what
    # what = property(_get_what, _set_what)

    # def _get_objectId(self):
    #     return self.db_objectId
    # def _set_objectId(self, objectId):
    #     self.db_objectId = objectId
    # objectId = property(_get_objectId, _set_objectId)
    # old_obj_id = property(_get_objectId, _set_objectId)
    # new_obj_id = property(_get_objectId, _set_objectId)

    # def _get_parentObjId(self):
    #     return self.db_parentObjId
    # def _set_parentObjId(self, parentObjId):
    #     self.db_parentObjId = parentObjId
    # parentObjId = property(_get_parentObjId, _set_parentObjId)
    
    # def _get_parentObjType(self):
    #     return self.db_parentObjType
    # def _set_parentObjType(self, parentObjType):
    #     self.db_parentObjType = parentObjType
    # parentObjType = property(_get_parentObjType, _set_parentObjType)

    ##########################################################################
    # Operators
    
    def __str__(self):
        """__str__() -> str - Returns a string representation of an Annotation
        object. 

        """
        rep = "<delete id=%s what=%s objectId=%s parentObjId=%s" + \
            " parentObjType=%s/>"
        return rep % (str(self.id), str(self.what), str(self.objectId),
                      str(self.parentObjId), str(self.parentObjType))

    # FIXME expand this
    def __eq__(self, other):
        """ __eq__(other: DeleteOp) -> boolean
        Returns True if self and other have the same attributes. Used by == 
        operator. 
        
        """
        if type(other) != type(self):
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

################################################################################
# Unit tests


class TestOperation(unittest.TestCase):
    
    def create_ops(self, id_scope=IdScope()):
        from vistrails.core.modules.basic_modules import identifier as basic_pkg
        from vistrails.core.vistrail.module import Module
        from vistrails.core.vistrail.module_function import ModuleFunction
        from vistrails.core.vistrail.module_param import ModuleParam
        from vistrails.core.vistrail.annotation import Annotation
        
        if id_scope is None:
            id_scope = IdScope(remap={AddOp.vtType: 'operation',
                                      ChangeOp.vtType: 'operation',
                                      DeleteOp.vtType: 'operation'})

        m = Module(id=id_scope.getNewId(Module.vtType),
                   name='Float',
                   package=basic_pkg)
        add_op = AddOp(id=id_scope.getNewId(AddOp.vtType),
                       what=Module.vtType,
                       objectId=m.id,
                       data=m)
        function = ModuleFunction(id=id_scope.getNewId(ModuleFunction.vtType),
                                  name='value')
        change_op = ChangeOp(id=id_scope.getNewId(ChangeOp.vtType),
                             what=ModuleFunction.vtType,
                             oldObjId=2,
                             newObjId=function.real_id,
                             parentObjId=m.id,
                             parentObjType=Module.vtType,
                             data=function)
        param = ModuleParam(id=id_scope.getNewId(ModuleParam.vtType),
                            type='Float',
                            val='1.0')
        
        delete_op = DeleteOp(id=id_scope.getNewId(DeleteOp.vtType),
                             what=ModuleParam.vtType,
                             objectId=param.real_id,
                             parentObjId=function.real_id,
                             parentObjType=ModuleFunction.vtType)

        annotation = Annotation(id=id_scope.getNewId(Annotation.vtType),
                                key='foo',
                                value='bar')
        add_annotation = AddOp(id=id_scope.getNewId(AddOp.vtType),
                               what=Annotation.vtType,
                               objectId=m.id,
                               data=annotation)
        cparam = ModuleControlParam(id=id_scope.getNewId(ModuleControlParam.vtType),
                                name='foo',
                                value='bar')
        add_cparam = AddOp(id=id_scope.getNewId(AddOp.vtType),
                               what=ModuleControlParam.vtType,
                               objectId=m.id,
                               data=cparam)
        
        return [add_op, change_op, delete_op, add_annotation]

    def test_copy(self):       
        id_scope = IdScope(remap={AddOp.vtType: 'operation',
                                  ChangeOp.vtType: 'operation',
                                  DeleteOp.vtType: 'operation'})
        for op1 in self.create_ops(id_scope):
            op2 = copy.copy(op1)
            self.assertEquals(op1, op2)
            self.assertEquals(op1.id, op2.id)
            op3 = op1.do_copy(True, id_scope, {})
            self.assertEquals(op1, op3)
            self.assertNotEquals(op1.id, op3.id)
            if hasattr(op1, 'data'):
                self.assertNotEquals(op1.data.db_id, op3.data.db_id)

    def test_serialization(self):
        import vistrails.core.db.io
        for op1 in self.create_ops():
            xml_str = vistrails.core.db.io.serialize(op1)
            op2 = vistrails.core.db.io.unserialize(xml_str, op1.__class__)
            self.assertEquals(op1, op2)
            self.assertEquals(op1.id, op2.id)

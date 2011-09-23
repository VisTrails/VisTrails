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

from db.services.action_chain import simplify_ops
from db.domain import DBAction, DBAdd, DBDelete, DBChange
import copy

def create_delete_op_chain(object, parent=(None, None)):
    opChain = []
    for (obj, parentType, parentId) in object.db_children(parent):
        op = DBDelete(id=-1,
                      what=obj.vtType,
                      objectId=obj.db_id,
                      parentObjType=parentType,
                      parentObjId=parentId,
                      )
        opChain.append(op)
    return opChain

def create_add_op_chain(object, parent=(None, None)):
    opChain = []
    object = copy.copy(object)
    adds = object.db_children(parent, True)
    adds.reverse()
    for (obj, parentType, parentId) in adds:
        op = DBAdd(id=-1,
                   what=obj.vtType,
                   objectId=obj.db_id,
                   parentObjType=parentType,
                   parentObjId=parentId,
                   data=obj,
                   )
        opChain.append(op)
    return opChain

def create_change_op_chain(old_obj, new_obj, parent=(None,None)):
    opChain = []
    new_obj = copy.copy(new_obj)
    deletes = old_obj.db_children(parent)
    deletes.pop()
    for (obj, parentType, parentId) in deletes:
        op = DBDelete(id=-1,
                      what=obj.vtType,
                      objectId=obj.db_id,
                      parentObjType=parentType,
                      parentObjId=parentId,
                      )
        opChain.append(op)

    adds = new_obj.db_children(parent, True)
    (obj, parentType, parentId) = adds.pop()
    op = DBChange(id=-1,
                  what=obj.vtType,
                  oldObjId=old_obj.db_id,
                  newObjId=obj.db_id,
                  parentObjType=parentType,
                  parentObjId=parentId,
                  data=new_obj,
                  )
    opChain.append(op)

    adds.reverse()
    for (obj, parentType, parentId) in adds:
        op = DBAdd(id=-1,
                   what=obj.vtType,
                   objectId=obj.db_id,
                   parentObjType=parentType,
                   parentObjId=parentId,
                   data=obj,
                   )
    return opChain

def create_copy_op_chain(object, parent=(None,None), id_scope=None):
    opChain = []
    id_remap = {}
    object = copy.copy(object)

    adds = object.db_children(parent, True)
    adds.reverse()
    for (obj, parentType, parentId) in adds:
        if parentId is not None:
            parentId = id_remap[(parentType, parentId)]
        new_id = id_scope.getNewId(obj.vtType)
        id_remap[(obj.vtType, obj.db_id)] = new_id
        obj.db_id = new_id
        op = DBAdd(id=-1,
                   what=obj.vtType,
                   objectId=obj.db_id,
                   parentObjType=parentType,
                   parentObjId=parentId,
                   data=obj,
                   )
        opChain.append(op)
    return opChain
    

def create_action(action_list):
    """create_action(action_list: list) -> DBAction
    where action_list is a list of tuples
     (
      type, 
      object, 
      new_obj=None,
      parent_type=None,
      parent_id=None,
    )
    Example: create_action([('add', module1), ('delete', connection2)]

    """
    ops = []
    for tuple in action_list:
        if tuple[0] == 'add' and len(tuple) >= 2:
            if len(tuple) >= 4:
                ops.extend(create_add_op_chain(tuple[1], (tuple[2], tuple[3])))
            else:
                ops.extend(create_add_op_chain(tuple[1]))
        elif tuple[0] == 'delete' and len(tuple) >= 2:
            if len(tuple) >= 4:
                ops.extend(create_delete_op_chain(tuple[1], 
                                                  (tuple[2], tuple[3])))
            else:
                ops.extend(create_delete_op_chain(tuple[1]))
        elif tuple[0] == 'change' and len(tuple) >= 3:
            if len(tuple) >= 5:
                ops.extend(create_change_op_chain(tuple[1], tuple[2],
                                                  (tuple[3], tuple[4])))
            else:
                ops.extend(create_change_op_chain(tuple[1], tuple[2]))
        else:
            msg = "unable to interpret action tuple " + tuple.__str__()
            raise Exception(msg)
    action = DBAction(id=-1,
                      operations=ops)
    return action

def create_action_from_ops(ops, simplify=False):
    if simplify:
        ops = simplify_ops(ops)

    action = DBAction(id=-1,
                      operations=ops)
    return action

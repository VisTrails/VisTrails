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

def getActionChain(obj, version, start=0):
    result = []
    currentId = version
    while currentId > start: #and currentId > 0:
        action = obj.db_get_action_by_id(currentId)
        result.append(action)
        currentId = action.db_prevId
    result.reverse()
    return result

def simplify_ops(ops):
    addDict = {}
    deleteDict = {}
    for op_count, op in enumerate(ops):
        op.db_id = -op_count - 1
        if op.vtType == 'add':
            addDict[(op.db_what, op.db_objectId)] = op
        elif op.vtType == 'delete':
            try:
                del addDict[(op.db_what, op.db_objectId)]
            except KeyError:
                deleteDict[(op.db_what, op.db_objectId)] = op
        elif op.vtType == 'change':
            try:
                k = addDict[(op.db_what, op.db_oldObjId)]
            except KeyError:
                addDict[(op.db_what, op.db_newObjId)] = op
            else:
                old_old_id = getOldObjId(k)
                del addDict[(op.db_what, op.db_oldObjId)]
                addDict[(op.db_what, op.db_newObjId)] = \
                    DBChange(id=opCount,
                             what=op.db_what,
                             oldObjId=old_old_id,
                             newObjId=op.db_newObjId,
                             parentObjId=op.db_parentObjId,
                             parentObjType=op.db_parentObjType,
                             data=op.db_data,
                             )

    deletes = deleteDict.values()
    deletes.sort(key=lambda x: -x.db_id) # faster than sort(lambda x, y: -cmp(x.db_id, y.db_id))
    adds = addDict.values()
    adds.sort(key=lambda x: -x.db_id) # faster than sort(lambda x, y: -cmp(x.db_id, y.db_id))
    return deletes + adds

def getCurrentOperationDict(actions, currentOperations=None):
    if currentOperations is None:
        currentOperations = {}

    # note that this operation assumes unique ids for each operation's data
    # any add adds to the dict, delete removes from the dict, and
    # change replaces the current value in the dict
    for action in actions:
        for operation in action.db_operations:
            operationvtType = operation.vtType
            d = operation.__dict__
            if operationvtType == 'add':
                currentOperations[(d['_db_what'], 
                                   d['_db_objectId'])] = \
                                   operation
            elif operationvtType == 'delete':
                what = d['_db_what']
                objectId = d['_db_objectId']
                t = (what, objectId)
                try:
                    del currentOperations[t]
                except KeyError:
                    msg = "Illegal delete operation: %d" % d['_db_id']
                    raise Exception(msg)
            elif operationvtType == 'change':
                what = d['_db_what']
                objectId = d['_db_oldObjId']
                t = (what, objectId)
                try:
                    del currentOperations[t]
                except KeyError:
                    msg = "Illegal change operation: %d" % d['_db_id']
                    raise Exception(msg)
                currentOperations[(what,
                                   d['_db_newObjId'])] = operation
            else:
                msg = "Unrecognized operation '%s'" % operation.vtType
                raise Exception(msg)

    return currentOperations

def getCurrentOperations(actions):
    # sort the values left in the hash and return the list
    sortedOperations = getCurrentOperationDict(actions).values()
    sortedOperations.sort(key=lambda x: x.db_id)
    return sortedOperations


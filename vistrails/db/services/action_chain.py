############################################################################
##
## Copyright (C) 2006-2007 University of Utah. All rights reserved.
##
## This file is part of VisTrails.
##
## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following to ensure GNU General Public
## Licensing requirements will be met:
## http://www.opensource.org/licenses/gpl-license.php
##
## If you are unsure which license is appropriate for your use (for
## instance, you are interested in developing a commercial derivative
## of VisTrails), please contact us at vistrails@sci.utah.edu.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################

def getActionChain(obj, version, start=0):
    result = []
    currentId = version
    while currentId > start: #and currentId > 0:
        action = obj.db_get_action_by_id(currentId)
        result.append(action)
        currentId = action.db_prevId
    result.reverse()
    return result

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
                currentOperations[(d['_DBAdd__db_what'], 
                                   d['_DBAdd__db_objectId'])] = \
                                   operation
            elif operationvtType == 'delete':
                what = d['_DBDelete__db_what']
                objectId = d['_DBDelete__db_objectId']
                t = (what, objectId)
                try:
                    del currentOperations[t]
                except KeyError:
                    msg = "Illegal delete operation"
                    raise Exception(msg)
            elif operationvtType == 'change':
                what = d['_DBChange__db_what']
                objectId = d['_DBChange__db_oldObjId']
                t = (what, objectId)
                try:
                    del currentOperations[t]
                except KeyError:
                    msg = "Illegal change operation"
                    raise Exception(msg)
                currentOperations[(what,
                                   d['_DBChange__db_newObjId'])] = operation
            else:
                msg = "Unrecognized operation '%s'" % operation.vtType
                raise Exception(msg)

    return currentOperations

def getCurrentOperations(actions):
    # sort the values left in the hash and return the list
    sortedOperations = getCurrentOperationDict(actions).values()
    sortedOperations.sort(key=lambda x: x.db_id)
    return sortedOperations


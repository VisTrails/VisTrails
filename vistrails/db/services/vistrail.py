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

from db.domain import DBWorkflow
import copy

def materializeWorkflow(vistrail, version):
    # construct path up through tree and perform each action
    if vistrail.db_get_action(version) is not None:
        workflow = DBWorkflow()
        #	    for action in getActionChain(vistrail, version):
        #		oldPerformAction(action, workflow)
        performActions(getActionChain(vistrail, version), 
                            workflow)
        workflow.db_id = version
        workflow.db_vistrailId = vistrail.db_id
        return workflow
    elif version == 0:
        return DBWorkflow()

def getActionChain(vistrail, version, start=0):
    result = []
    currentId = version
    while currentId >= start and currentId > 0:
        action = vistrail.db_get_action(currentId)
        result.append(action)
        currentId = action.db_prevId
    result.reverse()
    return result

def getCurrentOperationDict(actions):
    currentOperations = {}

    # note that this operation assumes unique ids for each operation's data
    # any add adds to the dict, delete removes from the dict, and
    # change replaces the current value in the dict

    # ERROR: need to keep track of operations not actions
    for action in actions:
#         print 'action: %d' % action.db_id
        for operation in action.db_operations:
            if operation.vtType == 'add':
#                 print "add: %s %s" % (operation.db_what, 
#                                       operation.db_objectId)
#                 print "    to:  %s %s" % (operation.db_parentObjType, operation.db_parentObjId)
                currentOperations[(operation.db_what, 
                                   operation.db_objectId)] = \
                                   operation
            elif operation.vtType == 'delete':
#                 print "del: %s %s" % (operation.db_what, 
#                                       operation.db_objectId)
#                 print "    from:  %s %s" % (operation.db_parentObjType, operation.db_parentObjId)
                if currentOperations.has_key((operation.db_what,
                                              operation.db_objectId)):
                    del currentOperations[(operation.db_what, 
                                           operation.db_objectId)]
                else:
                    msg = "Illegal delete operation"
                    raise Exception(msg)
            elif operation.vtType == 'change':
#                 print "chg: %s %s %s" % (operation.db_what, 
#                                          operation.db_oldObjId,
#                                          operation.db_newObjId)
#                 print "    at:  %s %s" % (operation.db_parentObjType, operation.db_parentObjId)
                if currentOperations.has_key((operation.db_what,
                                              operation.db_oldObjId)):
                    del currentOperations[(operation.db_what, 
                                           operation.db_oldObjId)]
                else:
                    msg = "Illegal change operation"
                    raise Exception(msg)

                currentOperations[(operation.db_what, 
                                   operation.db_newObjId)] = operation
            else:
                msg = "Unrecognized operation '%s'" % operation.vtType
                raise Exception(msg)

    return currentOperations

def getCurrentOperations(actions):
    # sort the values left in the hash and return the list
    sortedOperations = getCurrentOperationDict(actions).values()
    sortedOperations.sort(lambda x, y: cmp(x.db_id, y.db_id))
    return sortedOperations

def performAction(action, workflow):
    if action.actionType == 'add':
        for operation in action.db_operations:
            workflow.db_add_object(operation.db_data, 
                                   operation.db_parentObjType,
                                   operation.db_parentObjId)
    elif action.actionType == 'change':
        for operation in action.db_operations:
            workflow.db_change_object(operation.db_data,
                                      operation.db_parentObjType,
                                      operation.db_parentObjId)
    elif action.actionType == 'delete':
        for operation in action.operations:
            workflow.db_delete_object(operation.db_objectId,
                                      operation.db_what,
                                      operation.db_parentObjType,
                                      operation.db_parentObjId)
    else:
        msg = "Unrecognized action type '%s'" % action.db_actionType
        raise Exception(msg)

def performActions(actions, workflow):
    # get the current actions and run addObject on the workflow
    # note that delete actions have been removed and
    # a change after an add is effectively an add if the add is discarded
    for operation in getCurrentOperations(actions):
#         print "operation %d: %s %s" % (operation.db_id, operation.vtType,
#                                        operation.db_what)
#         print "    to:  %s %s" % (operation.db_parentObjType, operation.db_parentObjId)
        workflow.db_add_object(operation.db_data,
                               operation.db_parentObjType,
                               operation.db_parentObjId)

def getSharedRoots(vistrail, versions):
    # base case is 0
    current = copy.copy(versions)
    sharedRoots = []
    while 0 not in current:
        maxId = max(current)
        if current.count(maxval) == len(current):
            return maxId
        else:
            newId = vistrail.db_get_action(maxId).db_prevId
            for i, v in enumerate(current):
                if v == maxId:
                    current[i] = newId
    return 0

def updateActionDict(actionDict, actions):
    addDict = {}
    for action in actions:
        if action.db_actionType == 'add':
            for operation in action.db_operations:
                print "add: %s %s" % (operation.db_what, 
                                      operation.db_data.getPrimaryKey())
                addDict[(operation.db_what, 
                         operation.db_data.getPrimaryKey())] = action
        elif action.actionType == 'delete':
            for operation in action.db_operations:
                print "del: %s %s" % (operation.db_what, 
                                      operation.db_objectId)
                if actionDict.has_key((operation.db_what,
                                       operation.db_objectId)):
                    del actionDict[(operation.db_what, 
                                    operation.db_objectId)]
                elif addDict.has_key((operation.db_what,
                                      operation.db_objectId)):
                    del addDict[(operation.db_what,
                                 opeation.db_objectId)]
                else:
                    pass
        elif action.db_actionType == 'change':
            for operation in action.db_operations:
                print "chg: %s %s" % (operation.db_what, 
                                      operation.db_data.getPrimaryKey())
                if actionDict.has_key((operation.db_what,
                                       operation.db_data.getPrimaryKey())):
                    del actionDict[(operation.db_what, 
                                    operation.db_data.getPrimaryKey())]
                addDict[(operation.db_what,
                         operation.db_data.getPrimaryKey())] = action
        else:
            msg = "Unrecognized action type '%s'" % action.db_actionType
            raise Exception(msg)

    return addDict

def getObjects(actions):
    objects = {}
    for action in actions:
        for operation in action.db_operations:
            if not objects.has_key(operation.db_what):
                objects[operation.db_what] = []
            object = copy.copy(operation.db_data)
            objects[operation.db_what].append(object)
    return objects

def getVersionDifferences(vistrail, versions):
    sharedRoot = getSharedRoot(vistrail, versions)
    sharedActionChain = getActionChain(vistrail, sharedRoot)
    sharedActionDict = getCurrentActionDict(sharedActionChain)

    vOnlySorted = []
    for v in versions:
        vActions = getActionChain(vistrail, v, sharedRoot)
        vAdds = updateActionDict(sharedActionDict, vActions)
        vOnlyActions = vAdds.values()
        vOnlyActions.sort(lambda x,y: cmp(x.db_id, y.db_id))
        vOnlySorted.append(vOnlyActions)

    sharedActions = sharedActionDict.values()
    sharedActions.sort(lambda x, y: cmp(x.db_id, y.db_id))

    return (sharedActions, vOnlySorted)

def compareParams(f1, f2):
    badParams = []
    for p1 in f1.getParameters():
        found = False
        for p2 in f2.getParameters():
            if p1.getPrimaryKey() == p2.getPrimaryKey():
                found = True
                break
            elif p1.db_type == p2.db_type and p1.db_val == p2.db_val:
                found = True
                break
        if not found:
            badParams.append(p1)
    return badParams

def compareModules(m1, m2):	
    f2vals = m2.getFunctions()
    f2matched  = [False] * len(f2vals)
    for f1 in m1.getFunctions():
        found = False
        for i,f2 in enumerate(f2vals):
            if matches(f1, f2):
                f2matched[i] = True
                break
        if not found:
            badFunctions.append(f1)
    for i,f2 in enumerate(f2vals):
        if not f2matched[i]:
            found = False
            for f1 in m1.getFunctions():
                if matches(f1, f2):
                    found = True
                    break
            if not found:
                badFunctions.append(f2)

    return badFunctions

def getWorkflowDiff(vistrail, v1, v2):
    (sharedActions, vOnlyActions) = \
        getVersionDifferences(vistrail, [v1, v2])

    sharedWorkflow = Workflow()
    performActions(sharedActions, sharedWorkflow)

    v1Workflow = copy.deepcopy(sharedWorkflow)
    performActions(vOnlyActions[0], v1Workflow)
    v2Workflow = copy.deepcopy(sharedWorkflow)
    performActions(vOnlyActions[1], v2Workflow)

    # 	sharedModules = sharedObjects[Module.vtType]
    # 	sharedFunctions = sharedObjects[Function.vtType]
    # 	sharedParams = sharedObjects[Parameter.vtType]

    # 	v1Modules = vOnlyObjects[0][Module.vtType]
    # 	v1Functions = vOnlyObjects[0][Function.vtType]
    # 	v1Params = vOnlyObjects[0][Parameter.vtType]
    # 	v2Modules = vOnlyObjects[1][Module.vtType]
    # 	v2Functions = vOnlyObjects[1][Function.vtType]
    # 	v2Params = vOnlyObjects[1][Parameter.vtType]

    # want to materialize the modules, then do comparison

    sharedModuleIds = [(m.db_id,m.db_id) 
                       for m in sharedWorkflow.db_get_modules()]
    v1ModuleIds = [m.db_id for m in v1Workflow.db_get_modules()]
    v2ModuleIds = [m.db_id for m in v2Workflow.db_get_modules()]

    # match shared modules by name
    for m1 in v1Workflow.db_get_modules():
        for m2 in v2Workflow.db_get_modules():
            # same if have same name
            if m1.db_name == m2.db_name:
                # spin through functions to make sure they're the same

                sharedModuleIds.append((m1.db_id, m2.db_id))
                v1ModuleIds.remove(m1.db_id)
                v2ModuleIds.remove(m2.db_id)

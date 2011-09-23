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

from db.domain import DBWorkflow, DBAdd, DBDelete, DBAction, DBAbstraction, \
    DBModule, DBConnection, DBPort, DBFunction, DBParameter, DBGroup
from db.services.action_chain import getActionChain, getCurrentOperationDict, \
    getCurrentOperations, simplify_ops
from db import VistrailsDBException

import copy
import datetime
import getpass

def update_id_scope(vistrail):
    if hasattr(vistrail, 'update_id_scope'):
        vistrail.update_id_scope()
    else:
        for action in vistrail.db_actions:
            vistrail.idScope.updateBeginId('action', action.db_id+1)
            if action.db_session is not None:
                vistrail.idScope.updateBeginId('session', action.db_session + 1)
            for operation in action.db_operations:
                vistrail.idScope.updateBeginId('operation', operation.db_id+1)
                if operation.vtType == 'add' or operation.vtType == 'change':
                    # update ids of data
                    vistrail.idScope.updateBeginId(operation.db_what, 
                                                   getNewObjId(operation)+1)
                    if operation.db_data is None:
                        if operation.vtType == 'change':
                            operation.db_objectId = operation.db_oldObjId
                    vistrail.db_add_object(operation.db_data)
            for annotation in action.db_annotations:
                vistrail.idScope.updateBeginId('annotation', annotation.db_id+1)

def materializeWorkflow(vistrail, version):
    # construct path up through tree and perform each action
    if vistrail.db_has_action_with_id(version):
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
    else:
        raise VistrailsDBException("invalid workflow version %s" % version)

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

def performDeletes(deleteOps, workflow):
    for operation in deleteOps:
        workflow.db_delete_object(getOldObjId(operation), operation.db_what,
                                  operation.db_parentObjType,
                                  operation.db_parentObjId)

def performAdds(addOps, workflow):
    for operation in addOps:
#         print "operation %d: %s %s" % (operation.db_id, operation.vtType,
#                                        operation.db_what)
#         print "    to:  %s %s" % (operation.db_parentObjType, 
#                                   operation.db_parentObjId)
        workflow.db_add_object(operation.db_data,
                               operation.db_parentObjType,
                               operation.db_parentObjId)

def performActions(actions, workflow):
    # get the current actions and run addObject on the workflow
    # note that delete actions have been removed and
    # a change after an add is effectively an add if the add is discarded
    performAdds(getCurrentOperations(actions), workflow)

def synchronize(old_vistrail, new_vistrail, current_action_id):
    id_remap = {}
    for action in new_vistrail.db_actions:
        if action.is_new:
            new_action = action.do_copy(True, old_vistrail.idScope, id_remap)
            old_vistrail.db_add_action(new_action)
        else:
            # it must exist in the old vistrail, too
            old_action = old_vistrail.db_actions_id_index[action.db_id]
            # use knowledge that we replace old notes...
            for annotation in action.db_deleted_annotations:
                if old_action.db_has_annotation_with_id(annotation.db_id):
                    old_action.db_delete_annotation(annotation)
                else:
                    # FIXME conflict!
                    # we know that the annotation that was there isn't anymore
                    #print 'possible notes conflict'
                    if old_action.db_has_annotation_with_key('notes'):
                        old_annotation = \
                            old_action.db_get_annotation_by_key('notes')
                        old_action.db_delete_annotation(old_annotation)
                    else:
                        # we don't have to do anything
                        pass
            for annotation in action.db_annotations:
                if annotation.is_new:
                    new_annotation = annotation.do_copy(True, 
                                                        old_vistrail.idScope,
                                                        id_remap)
                    old_action.db_add_annotation(new_annotation)

    for tag in new_vistrail.db_deleted_tags:
        if old_vistrail.db_has_tag_with_id(tag.db_id):
            old_vistrail.db_delete_tag(tag)
        else:
            # FIXME conflict!
            # we know the tag that was there isn't anymore
            #print 'possible tag conflict'
            # we don't have to do anything here, though
            pass

    for tag in new_vistrail.db_tags:
        if tag.is_new:
            new_tag = tag.do_copy(False)
            # remap id
            try:
                new_tag.db_id = id_remap[(DBAction.vtType, new_tag.db_id)]
            except KeyError:
                pass
            try:
                old_tag = old_vistrail.db_tags_name_index[new_tag.db_name]
            except KeyError:
                # FIXME conflict!
                #print "tag conflict--name already used"
                old_vistrail.db_delete_tag(old_tag)
            try:
                old_tag = old_vistrail.db_tags_id_index[new_tag.db_id]
            except KeyError:
                #print 'possible tag conflict -- WILL NOT GET HERE!'
                old_vistrail.db_delete_tag(old_tag)
            old_vistrail.db_add_tag(new_tag)

    new_action_id = \
        id_remap.get((DBAction.vtType, current_action_id), current_action_id)
    old_vistrail.db_currentVersion = new_action_id
    return new_action_id

def merge(sb, next_sb, app='', interactive = False, tmp_dir = '', next_tmp_dir = ''):
    """ def merge(sb: SaveBundle, next_sb: SaveBundle, app: str,
                  interactive: bool, tmp_dir: str, next_tmp_dir: str) -> None
        Merges two save bundles that has been annotated with checkout
        information from a database.
        All changes from next_sb are appended onto sb. The changes in sb can
        then be uploaded to the database and use as the new working copy.
        first sb is the old one from db, last vt is the new one.
        if interactive is gui.merge_gui.MergeGui then the tmp_dir's must be set.
        """
    vt = sb.vistrail
    next_vt = next_sb.vistrail
    merge_gui = interactive
    MergeGUI = merge_gui.MergeGUI if merge_gui else False
    skip = 0

    id_remap = {}

    checkout_key = "__checkout_version_"
    action_key = checkout_key + app
    annotation_key = action_key + '_annotationhash'
    action_annotation_key = action_key + '_actionannotationhash'

    # find the highest common checkin id
    checkinId = 0
    if len(app) and next_vt.db_has_annotation_with_key(action_key):
        co = next_vt.db_get_annotation_by_key(action_key)
        #print "found checkin id annotation"
        checkinId = int(co._db_value)
    else:
        #print "calculating checkin id"
        # create unique identifiers for all actions
        actions = []
        actionDict = {}
        for action in vt.db_actions:
            unique = action._db_user + str(action._db_date)
            copy_no = 0
            while (unique + str(copy_no)) in actionDict:
                copy_no += 1
            unique = unique + str(copy_no)
            actions.append(unique)
            actionDict[unique] = action
        actionNexts = []
        actionDictNext = {}
        for action in next_vt.db_actions:
            unique = action._db_user + str(action._db_date)
            copy_no = 0
            while (unique + str(copy_no)) in actionDictNext:
                copy_no += 1
            unique = unique + str(copy_no)
            actionNexts.append(unique)
            actionDictNext[unique] = action

        # find last checkin action (only works for centralized syncs)
        while checkinId < len(actions) and checkinId < len(actionNexts) and \
            actions[checkinId] == actionNexts[checkinId]:
                checkinId += 1
        if checkinId > 0:
            checkinId = actionDict[actions[checkinId-1]].db_id
    #print "checkinId:", checkinId

    # delete previous checkout annotations in vt
    deletekeys = [action_key,annotation_key,action_annotation_key]
    for key in deletekeys:
        while vt.db_has_annotation_with_key(key):
            a = vt.db_get_annotation_by_key(key)
            vt.db_delete_annotation(a)

    # check if someone else have changed the annotations
    mergeAnnotations = True
    if len(app) and next_vt.db_has_annotation_with_key(annotation_key):
        #print "found annotationhash"
        co = next_vt.db_get_annotation_by_key(annotation_key)
        old_hash = co._db_value
        mergeAnnotations = (old_hash != vt.hashAnnotations())
    #print "merge annotations:", mergeAnnotations

    # check if someone else have changed the action annotations
    mergeActionAnnotations = True
    if len(app) and next_vt.db_has_annotation_with_key(action_annotation_key):
        #print "found actionannotationhash"
        co = next_vt.db_get_annotation_by_key(action_annotation_key)
        old_hash = co._db_value
        mergeActionAnnotations = (old_hash != vt.hashActionAnnotations())
    #print "merge actionannotations:", mergeActionAnnotations

    ################## merge actions ######################
    for action in next_vt.db_actions:
        # check for identical actions
        if action._db_id > checkinId:
            new_action = action.do_copy(True, vt.idScope, id_remap)
            vt.db_add_action(new_action)

    ################## merge annotations ##################
    if not mergeAnnotations:
        # delete removed annotations
        for annotation in [a for a in vt.db_annotations]:
            if not next_vt.db_has_annotation_with_id(annotation.db_id):
                # delete it
                vt.db_delete_annotation(annotation)
        # add new and update changed annotations
        for annotation in next_vt.db_annotations:
            if not vt.db_has_annotation_with_id(annotation.db_id):
                # new annotation
                new_annotation = annotation.do_copy(True, vt.idScope, id_remap)
                vt.db_add_annotation(new_annotation)
            else:
                old_annotation = vt.db_get_annotation_by_id(annotation.db_id)
                if old_annotation.db_key != annotation.db_key:
                    # key changed
                    old_annotation.db_key = annotation.db_key
                if old_annotation.db_value != annotation.db_value:
                    # value changed
                    old_annotation.db_value = annotation.db_value
    else:
        annotations = {}
        # create dict with keys and values
        for annotation in vt.db_annotations:
            if annotation.db_key not in annotations:
                annotations[annotation.db_key] = []
            if annotation.db_value not in annotations[annotation.db_key]:
                annotations[annotation.db_key].append(annotation.db_value)
        # add nonexisting key-value pairs
        for annotation in next_vt.db_annotations:
            if annotation.db_key not in annotations or \
                    annotation.db_value not in annotations[annotation.db_key]:
                new_annotation = annotation.do_copy(True, vt.idScope, id_remap)
                vt.db_add_annotation(new_annotation)

    ################# merge action annotations ############
    if not mergeActionAnnotations:
        # delete removed action annotations
        for annotation in [a for a in vt.db_actionAnnotations]:
            if not next_vt.db_has_actionAnnotation_with_id(annotation.db_id):
                # delete it
                vt.db_delete_actionAnnotation(annotation)
                if annotation.db_key == '__thumb__' and len(sb.thumbnails) > 0:
                    # remove thumb
                    thumb = '/'.join(sb.thumbnails[0].split(
                            '/')[:-1]) + '/' + annotation.db_value
                    if thumb in sb.thumbnails:
                        sb.thumbnails.remove(thumb)

        # add new and update changed annotations
        for annotation in next_vt.db_actionAnnotations:
            if not vt.db_has_actionAnnotation_with_id(annotation.db_id):
                # new actionAnnotation
                annotation = annotation.do_copy(True, vt.idScope, id_remap)
                vt.db_add_actionAnnotation(annotation)
                if annotation.db_key == '__thumb__' and \
                        len(next_sb.thumbnails) > 0:
                    # add thumb
                    thumb = '/'.join(next_sb.thumbnails[0].split(
                            '/')[:-1])+'/'+ annotation.db_value
                    if thumb not in sb.thumbnails:
                        sb.thumbnails.append(thumb)
            else:
                old_annotation = \
                    vt.db_get_actionAnnotation_by_id(annotation.db_id)
                if old_annotation.db_value != annotation.db_value:
                    # value changed
                    if annotation.db_key == '__thumb__' and \
                            len(sb.thumbnails) > 0:
                        # remove thumb
                        thumb = '/'.join(sb.thumbnails[0].split(
                                '/')[:-1]) + '/' + old_annotation.db_value
                        if thumb in sb.thumbnails:
                            sb.thumbnails.remove(thumb)
                    if annotation.db_key == '__thumb__' and \
                            len(next_sb.thumbnails) > 0:
                        # add thumb
                        thumb = '/'.join(next_sb.thumbnails[0].split(
                                '/')[:-1])+'/'+ annotation.db_value
                        if thumb not in sb.thumbnails:
                            sb.thumbnails.append(thumb)
                    old_annotation.db_value = annotation.db_value
                    old_annotation.db_date = annotation.db_date
                    old_annotation.db_user = annotation.db_user
    else:
        # construct old action index (oas)
        oas = {}
        for a in vt.db_actionAnnotations:
            if not a.db_action_id in oas:
                oas[a.db_action_id] = {}
            if not a.db_key in oas[a.db_action_id]:
                oas[a.db_action_id][a.db_key] = []
            oas[a.db_action_id][a.db_key].append(a)
        # merge per action
        for new_annotation in next_vt.db_actionAnnotations:
            # keep both upgrades but update action id in new
            if new_annotation.db_key == '__upgrade__':
                value = int(new_annotation.db_value)
                if ('action', value) in id_remap:
                    new_annotation.db_value = str(id_remap[('action', value)])
                annotation = new_annotation.do_copy(True, vt.idScope, id_remap)
                vt.db_add_actionAnnotation(annotation)
            elif new_annotation.db_action_id <= checkinId and \
                    new_annotation.db_key in oas[new_annotation.db_action_id]:
                old_action = oas[new_annotation.db_action_id]
                # we have a conflict
                # tags should be merged (the user need to resolve)
                if new_annotation.db_key == '__tag__':
                    # there is only one
                    old_annotation = old_action[new_annotation.db_key][0]
                    if old_annotation.db_value != new_annotation.db_value:
                        value = old_annotation.db_value + " or " + \
                            new_annotation.db_value
                        if interactive:
                            if skip == 1:
                                pass
                            elif skip == 2:
                                old_annotation.db_value=new_annotation.db_value
                                old_annotation.db_date = new_annotation.db_date
                                old_annotation.db_user = new_annotation.db_user
                            else:
                                v, value = MergeGUI.resolveTags(
                                    old_annotation, new_annotation, value)
                                if v == merge_gui.CHOICE_OTHER_ALL:
                                    skip = 1
                                elif v == merge_gui.CHOICE_OTHER:
                                    pass
                                elif v == merge_gui.CHOICE_RESOLVED:
                                    #print "Tag resolved:", value
                                    old_annotation.db_value = value
                                    old_annotation.db_date = \
                                        new_annotation.db_date
                                    old_annotation.db_user = \
                                        new_annotation.db_user
                                    pass
                                elif v == merge_gui.CHOICE_OWN:
                                    old_annotation.db_value = \
                                        new_annotation.db_value
                                    old_annotation.db_date = \
                                        new_annotation.db_date
                                    old_annotation.db_user = \
                                        new_annotation.db_user
                                elif v == merge_gui.CHOICE_OWN_ALL:
                                    old_annotation.db_value = \
                                        new_annotation.db_value
                                    old_annotation.db_date = \
                                        new_annotation.db_date
                                    old_annotation.db_user = \
                                        new_annotation.db_user
                                    skip = 2
                        else:
                            old_annotation.db_value = value
                            old_annotation.db_date = new_annotation.db_date
                            old_annotation.db_user = new_annotation.db_user
                # notes should be merged (the user need to resolve)
                elif new_annotation.db_key == '__notes__':
                    # there is only one
                    old_annotation = old_action[new_annotation.db_key][0]
                    if new_annotation.db_value != old_annotation.db_value:
                        value = ("#### conflicting versions! ####<br/>" + 
                                 "## Other version at %s by %s:%s<br/>" +
                                 "## Your version at %s by %s:%s") % \
                          (str(old_annotation.db_date), old_annotation.db_user,
                          old_annotation.db_value, str(new_annotation.db_date),
                          new_annotation.db_user, new_annotation.db_value)
                        if interactive:
                            if skip == 1:
                                pass
                            elif skip == 2:
                                old_annotation.db_value=new_annotation.db_value
                                old_annotation.db_date = new_annotation.db_date
                                old_annotation.db_user = new_annotation.db_user
                            else:
                                v, value = MergeGUI.resolveNotes(
                                    old_annotation, new_annotation, value)
                                if v == merge_gui.CHOICE_OTHER_ALL:
                                    skip = 1
                                elif v == merge_gui.CHOICE_OTHER:
                                    pass
                                elif v == merge_gui.CHOICE_RESOLVED:
                                    #print "Note resolved:", value
                                    old_annotation.db_value = value
                                    old_annotation.db_date = \
                                        new_annotation.db_date
                                    old_annotation.db_user = \
                                        new_annotation.db_user
                                    pass
                                elif v == merge_gui.CHOICE_OWN:
                                    old_annotation.db_value = \
                                        new_annotation.db_value
                                    old_annotation.db_date = \
                                        new_annotation.db_date
                                    old_annotation.db_user = \
                                        new_annotation.db_user
                                elif v == merge_gui.CHOICE_OWN_ALL:
                                    old_annotation.db_value = \
                                        new_annotation.db_value
                                    old_annotation.db_date = \
                                        new_annotation.db_date
                                    old_annotation.db_user = \
                                        new_annotation.db_user
                                    skip = 2
                        else:
                            old_annotation.db_value = value
                            old_annotation.db_date = new_annotation.db_date
                            old_annotation.db_user = new_annotation.db_user

                # thumbs should be updated (we loose the other update)
                elif new_annotation.db_key == '__thumb__': 
                    # there is only one
                    old_annotation = old_action[new_annotation.db_key][0]
                    if new_annotation.db_value != old_annotation.db_value:
                        if interactive:
                            if skip == 1:
                                pass
                            elif skip == 2:
                                thumb = '/'.join(sb.thumbnails[0].split(
                                        '/')[:-1])+'/'+ old_annotation.db_value
                                if thumb in sb.thumbnails:
                                    sb.thumbnails.remove(thumb)
                                old_annotation.db_value=new_annotation.db_value
                                old_annotation.db_date = new_annotation.db_date
                                old_annotation.db_user = new_annotation.db_user
                                thumb = '/'.join(next_sb.thumbnails[0].split(
                                        '/')[:-1])+'/'+ new_annotation.db_value
                                if thumb not in sb.thumbnails:
                                    sb.thumbnails.append(thumb)
                            else:
                                v = MergeGUI.resolveThumbs(old_annotation,
                                         new_annotation, tmp_dir, next_tmp_dir)
                                if v == merge_gui.CHOICE_OTHER_ALL:
                                    skip = 1
                                elif v == merge_gui.CHOICE_OTHER:
                                    pass
                                elif v in (merge_gui.CHOICE_OWN,
                                           merge_gui.CHOICE_OWN_ALL):
                                    thumb = '/'.join(sb.thumbnails[0].split(
                                        '/')[:-1])+'/'+ old_annotation.db_value
                                    if thumb in sb.thumbnails:
                                        sb.thumbnails.remove(thumb)
                                    old_annotation.db_value = \
                                        new_annotation.db_value
                                    old_annotation.db_date = \
                                        new_annotation.db_date
                                    old_annotation.db_user = \
                                        new_annotation.db_user
                                    thumb='/'.join(next_sb.thumbnails[0].split(
                                        '/')[:-1])+'/'+ new_annotation.db_value
                                    if thumb not in sb.thumbnails:
                                        sb.thumbnails.append(thumb)
                                    if v == merge_gui.CHOICE_OWN_ALL:
                                        skip = 2
                        else:
                            thumb = '/'.join(sb.thumbnails[0].split(
                                    '/')[:-1])+'/'+ old_annotation.db_value
                            if thumb in sb.thumbnails:
                                sb.thumbnails.remove(thumb)
                            old_annotation.db_value = new_annotation.db_value
                            old_annotation.db_date = new_annotation.db_date
                            old_annotation.db_user = new_annotation.db_user
                            thumb = '/'.join(next_sb.thumbnails[0].split(
                                    '/')[:-1])+'/'+ new_annotation.db_value
                            if thumb not in sb.thumbnails:
                                sb.thumbnails.append(thumb)
                elif new_annotation.db_key == '__prune__': # keep old
                    pass
                # others should be appended if not already there
                else:
                    values = []
                    for old_annotation in old_action[new_annotation.db_key]:
                            values.append(old_annotation.db_value)
                    if new_annotation.db_value not in values:
                        annotation = new_annotation.do_copy(True, vt.idScope, \
                                                                id_remap)
                        vt.db_add_actionAnnotation(annotation)
            else:
                annotation = new_annotation.do_copy(True, vt.idScope, id_remap)
                vt.db_add_actionAnnotation(annotation)
                if annotation.db_key == '__thumb__':
                    thumb = '/'.join(next_sb.thumbnails[0].split('/')[:-1]) + \
                            '/' + annotation.db_value
                    if thumb not in sb.thumbnails:
                        sb.thumbnails.append(thumb)
    # make this a valid checked out version
    if len(app):
        vt.update_checkout_version(app)

################################################################################
# Analogy methods

def find_data(what, id, op_dict):
    try:
        return op_dict[(what, id)].db_data
    except KeyError:
        msg = 'cannot find data (%s, %s)'  % (what, id)
        raise Exception(msg)

def invertOperations(op_dict, adds, deletes, do_copy=False):
    inverse_ops = []       
    deletes.reverse()
    for op in deletes:
        data = find_data(op.db_what, getOldObjId(op), op_dict)
        if do_copy:
            data = copy.copy(data)
        inv_op = DBAdd(id=-1,
                       what=op.db_what,
                       objectId=getOldObjId(op),
                       parentObjId=op.db_parentObjId,
                       parentObjType=op.db_parentObjType,
                       data=data
                       )
        inverse_ops.append(inv_op)
    adds.reverse()
    for op in adds:
        inv_op = DBDelete(id=-1,
                          what=op.db_what,
                          objectId=getNewObjId(op),
                          parentObjId=op.db_parentObjId,
                          parentObjType=op.db_parentObjType,
                          )
        inverse_ops.append(inv_op)
    return inverse_ops

def normalOperations(adds, deletes, do_copy=False):
    new_ops = []
    for op in deletes:
        new_op = DBDelete(id=-1,
                          what=op.db_what,
                          objectId=getOldObjId(op),
                          parentObjId=op.db_parentObjId,
                          parentObjType=op.db_parentObjType,
                          )
        new_ops.append(new_op)
    for op in adds:
        data = op.db_data
        if do_copy:
            data = copy.copy(op.db_data)
        new_op = DBAdd(id=-1,
                       what=op.db_what,
                       objectId=getNewObjId(op),
                       parentObjId=op.db_parentObjId,
                       parentObjType=op.db_parentObjType,
                       data=data)
        new_ops.append(new_op)
    return new_ops        

def getPathAsAction(vistrail, v1, v2, do_copy=False):
    sharedRoot = getSharedRoot(vistrail, [v1, v2])
    sharedActionChain = getActionChain(vistrail, sharedRoot)
    sharedOperationDict = getCurrentOperationDict(sharedActionChain)
    v1Actions = getActionChain(vistrail, v1, sharedRoot)
    v2Actions = getActionChain(vistrail, v2, sharedRoot)
    (v1AddDict, v1DeleteDict) = getOperationDiff(v1Actions, 
                                                 sharedOperationDict)
    (v2AddDict, v2DeleteDict) = getOperationDiff(v2Actions,
                                                 sharedOperationDict)
    
    # need to invert one of them (v1)
    v1Adds = v1AddDict.values()
    v1Adds.sort(key=lambda x: x.db_id) # faster than sort(lambda x, y: cmp(x.db_id, y.db_id))
    v1Deletes = v1DeleteDict.values()
    v1Deletes.sort(key=lambda x: x.db_id) # faster than sort(lambda x, y: cmp(x.db_id, y.db_id))
    v1InverseOps = \
        invertOperations(sharedOperationDict, v1Adds, v1Deletes, do_copy)
    
    # need to normalize ops of the other (v2)
    v2Adds = v2AddDict.values()
    v2Adds.sort(key=lambda x: x.db_id) # faster than sort(lambda x, y: cmp(x.db_id, y.db_id))
    v2Deletes = v2DeleteDict.values()
    v2Deletes.sort(key=lambda x: x.db_id) # faster than sort(lambda x, y: cmp(x.db_id, y.db_id))
    v2Ops = normalOperations(v2Adds, v2Deletes, do_copy)

    allOps = v1InverseOps + v2Ops
    simplifiedOps = simplify_ops(allOps)
    return DBAction(id=-1, 
                    operations=simplifiedOps,
                    )

def addAndFixActions(startDict, actions):
    curDict = copy.copy(startDict)
    # print curDict
    for action in actions:
#         print "fixing action:", action.db_id
        new_ops = []
        for op in action.db_operations:
#             print "op:", op.vtType, op.db_what, getOldObjId(op)
#             print "   ", op.db_parentObjType, op.db_parentObjId
            if op.vtType == 'add':
                if op.db_parentObjId is None or \
                        curDict.has_key((op.db_parentObjType, 
                                         op.db_parentObjId)):
                    curDict[(op.db_what, op.db_objectId)] = op
                    new_ops.append(op)                    
            elif op.vtType == 'change':
                if curDict.has_key((op.db_what, op.db_oldObjId)) and \
                        (op.db_parentObjId is None or \
                             curDict.has_key((op.db_parentObjType, 
                                              op.db_parentObjId))):
                    del curDict[(op.db_what, op.db_oldObjId)]
                    curDict[(op.db_what, op.db_newObjId)] = op
                    new_ops.append(op)
            elif op.vtType == 'delete':
                if (op.db_parentObjId is None or
                    curDict.has_key((op.db_parentObjType, 
                                     op.db_parentObjId))) and \
                    curDict.has_key((op.db_what, op.db_objectId)):
                    del curDict[(op.db_what, op.db_objectId)]
                    new_ops.append(op)
        action.db_operations = new_ops
    return curDict

def fixActions(vistrail, v, actions):
    startingChain = getActionChain(vistrail, v)
    startingDict = getCurrentOperationDict(startingChain)
    addAndFixActions(startingDict, actions)
    
################################################################################
# Diff methods

def getSharedRoot(vistrail, versions):
    # base case is 0
    current = copy.copy(versions)
    while 0 not in current:
        maxId = max(current)
        if current.count(maxId) == len(current):
            return maxId
        else:
            newId = vistrail.db_get_action_by_id(maxId).db_prevId
            for i, v in enumerate(current):
                if v == maxId:
                    current[i] = newId
    return 0

def getOperationDiff(actions, operationDict):
    addDict = {}
    deleteDict = {}
    for action in actions:
#         print 'action: %d' % action.db_id
        for operation in action.db_operations:
            if operation.vtType == 'add':
#                 print "add: %s %s" % (operation.db_what, 
#                                       operation.db_objectId)
                addDict[(operation.db_what, 
                         operation.db_objectId)] = operation
            elif operation.vtType == 'delete':
#                 print "del: %s %s" % (operation.db_what, 
#                                       operation.db_objectId)
                if operationDict.has_key((operation.db_what,
                                          operation.db_objectId)):
                    deleteDict[(operation.db_what,
                                operation.db_objectId)] = operation
#                     del operationDict[(operation.db_what, 
#                                        operation.db_objectId)]
                elif addDict.has_key((operation.db_what,
                                      operation.db_objectId)):
                    del addDict[(operation.db_what,
                                 operation.db_objectId)]
                else:
                    pass
            elif operation.vtType == 'change':
#                 print "chg: %s %s %s" % (operation.db_what, 
#                                          operation.db_oldObjId,
#                                          operation.db_newObjId)
                if operationDict.has_key((operation.db_what,
                                          operation.db_oldObjId)):
                    deleteDict[(operation.db_what,
                                operation.db_oldObjId)] = operation
#                     del operationDict[(operation.db_what, 
#                                        operation.db_oldObjId)]
                elif addDict.has_key((operation.db_what,
                                      operation.db_oldObjId)):
                    del addDict[(operation.db_what, operation.db_oldObjId)]

                addDict[(operation.db_what,
                         operation.db_newObjId)] = operation
            else:
                msg = "Unrecognized operation '%s'" % operation.vtType
                raise Exception(msg)

    return (addDict, deleteDict)

def updateOperationDict(operationDict, deleteOps, addOps):
    for operation in deleteOps:
        if operationDict.has_key((operation.db_what, getOldObjId(operation))):
            del operationDict[(operation.db_what, getOldObjId(operation))]
        else:
            msg = "Illegal operation: " + operation
    for operation in addOps:
        operationDict[(operation.db_what, getNewObjId(operation))] = operation
    return operationDict

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
    sharedOperationDict = getCurrentOperationDict(sharedActionChain)

    vOnlySorted = []
    for v in versions:
        vActions = getActionChain(vistrail, v, sharedRoot)
        (vAddDict, vDeleteDict) = getOperationDiff(vActions, 
                                                   sharedOperationDict)
        vOnlyAdds = vAddDict.values()
        vOnlyAdds.sort(key=lambda x: x.db_id)
        vOnlyDeletes = vDeleteDict.values()
        vOnlyDeletes.sort(key=lambda x: x.db_id)
        vOpDict = copy.copy(sharedOperationDict)
        updateOperationDict(vOpDict, vOnlyDeletes, vOnlyAdds)
        vOps = vOpDict.values()
        vOps.sort(key=lambda x: x.db_id)
        vOnlySorted.append((vOnlyAdds, vOnlyDeletes, vOps))

    sharedOps = sharedOperationDict.values()
    sharedOps.sort(key=lambda x: x.db_id)

    return (sharedOps, vOnlySorted)

def heuristicModuleMatch(m1, m2):
    """takes two modules and returns 1 if exact match,
    0 if module names match, -1 if no match
    
    """
    if m1.db_name == m2.db_name and m1.db_namespace == m2.db_namespace and \
            m1.db_package == m2.db_package:
        if m1.vtType == 'group':
            # check if we have __desc__ annotation
            m1_desc = None
            m2_desc = None
            if '__desc__' in m1.db_annotations_key_index:
                m1_desc = m1.db_annotations_key_index['__desc__']
            if '__desc__' in m2.db_annotations_key_index:
                m2_desc = m2.db_annotations_key_index['__desc__']
            if not (m1_desc and m2_desc and m1_desc == m2_desc):
                # if desc's don't exactly match, return 0
                # else continue and check functions
                # FIXME: maybe we should check functions here
                return 0
                
        m1_functions = copy.copy(m1.db_get_functions())
        m2_functions = copy.copy(m2.db_get_functions())
        if len(m1_functions) != len(m2_functions):
            return 0
        for f1 in m1_functions[:]:
            match = None
            for f2 in m2_functions:
                isMatch = heuristicFunctionMatch(f1, f2)
                if isMatch == 1:
                    match = f2
                    break
            if match is not None:
                m1_functions.remove(f1)
                m2_functions.remove(f2)
            else:
                return 0
        if len(m1_functions) == len(m2_functions) == 0:
            return 1
        else:
            return 0
    return -1

def heuristicFunctionMatch(f1, f2):
    """takes two functions and returns 1 if exact match,
    0 if function names match, -1 if no match

    """
    if f1.db_name == f2.db_name:
        f1_parameters = copy.copy(f1.db_get_parameters())
        f2_parameters = copy.copy(f2.db_get_parameters())
        if len(f1_parameters) != len(f2_parameters):
            return 0
        for p1 in f1_parameters[:]:
            match = None
            for p2 in f2_parameters:
                isMatch = heuristicParameterMatch(p1, p2)
                if isMatch == 1:
                    match = p2
                    break
            if match is not None:
                f1_parameters.remove(p1)
                f2_parameters.remove(match)
            else:
                return 0
        if len(f1_parameters) == len(f2_parameters) == 0:
            return 1
        else:
            return 0
    return -1

def heuristicParameterMatch(p1, p2):
    """takes two parameters and returns 1 if exact match,
    0 if partial match (types match), -1 if no match

    """
    if p1.db_type == p2.db_type and p1.db_pos == p2.db_pos:
        if p1.db_val == p2.db_val:
            return 1
        else:
            return 0
    return -1

def heuristicConnectionMatch(c1, c2):
    """takes two connections and returns 1 if exact match,
    0 if partial match (currently undefined), -1 if no match

    """
    c1_ports = copy.copy(c1.db_get_ports())
    c2_ports = copy.copy(c2.db_get_ports())
    for p1 in c1_ports[:]:
        match = None
        for p2 in c2_ports:
            isMatch = heuristicPortMatch(p1, p2)
            if isMatch == 1:
                match = p2
                break
            elif isMatch == 0:
                match = p2
        if match is not None:
            c1_ports.remove(p1)
            c2_ports.remove(match)
        else:
            return -1
    if len(c1_ports) == len(c2_ports) == 0:
        return 1
    return -1

def heuristicPortMatch(p1, p2):
    """takes two ports and returns 1 if exact match,
    0 if partial match, -1 if no match
    
    """
    if p1.db_moduleId == p2.db_moduleId:
        return 1
    elif p1.db_type == p2.db_type and \
            p1.db_moduleName == p2.db_moduleName and \
            p1.sig == p2.sig:
        return 0
    return -1

def function_sig(function):
    return (function.db_name,
            [(param.db_type, param.db_val)
             for param in function.db_get_parameters()])

def getParamChanges(m1, m2, same_vt=True, heuristic_match=True):
    paramChanges = []
    # need to check to see if any children of m1 and m2 are affected
    m1_functions = m1.db_get_functions()
    m2_functions = m2.db_get_functions()
    m1_unmatched = []
    m2_unmatched = []
    if same_vt:
        for f1 in m1_functions:
            # see if m2 has f1, too
            f2 = m2.db_get_function(f1.db_id)
            if f2 is None:            
                m1_unmatched.append(f1)
            else:
                # function is same, check if parameters have changed
                if heuristic_match:
                    matchValue = heuristicFunctionMatch(f1, f2)
                    if matchValue != 1:
                        paramChanges.append((function_sig(f1), 
                                             function_sig(f2)))
                else:
                    paramChanges.append((function_sig(f1), function_sig(f2)))
        for f2 in m2_functions:
            # see if m1 has f2, too
            if m1.db_get_function(f2.db_id) is None:
                m2_unmatched.append(f2)
    else:
        m1_unmatched.extend(m1_functions)
        m2_unmatched.extend(m2_functions)

#             functionMatch = True
#             f1_params = f1.db_get_parameters()
#             f2_params = f2.db_get_parameters()
#             for p1 in f1_params:
#                 if f2.db_get_parameter(p1.db_id) is None:
#                     functionMatch = False
#                     m1_unmatched.append(f1)
#                     break
#             for p2 in f2_params:
#                 if f1.db_get_parameter(p2.db_id) is None:
#                     functionMatch = False
#                     m2_unmatched.append(f2)
#                     break
#             if functionMatch:

    if len(m1_unmatched) + len(m2_unmatched) > 0:
        if heuristic_match and len(m1_unmatched) > 0 and len(m2_unmatched) > 0:
            # do heuristic matches
            for f1 in m1_unmatched[:]:
                matched = False
                matchValue = 0
                for f2 in m2_unmatched:
                    matchValue = heuristicFunctionMatch(f1, f2)
                    if matchValue == 1:
                        # best match so quit
                        matched = f1
                        break
                    elif matchValue == 0:
                        # match, but not exact so continue to look
                        matched = f1
                if matched:
                    if matchValue != 1:
                        paramChanges.append((function_sig(f1), 
                                             function_sig(f2)))
                    m1_unmatched.remove(f1)
                    m2_unmatched.remove(f2)

        for f in m1_unmatched:
            paramChanges.append((function_sig(f), (None, None)))
        for f in m2_unmatched:
            paramChanges.append(((None, None), function_sig(f)))
        
    return paramChanges

def getOldObjId(operation):
    if operation.vtType == 'change':
        return operation.db_oldObjId
    return operation.db_objectId

def getNewObjId(operation):
    if operation.vtType == 'change':
        return operation.db_newObjId
    return operation.db_objectId

def setOldObjId(operation, id):
    if operation.vtType == 'change':
        operation.db_oldObjId = id
    else:
        operation.db_objectId = id

def setNewObjId(operation, id):
    if operation.vtType == 'change':
        operation.db_newObjId = id
    else:
        operation.db_objectId = id

def getWorkflowDiffCommon(vistrail, v1, v2, heuristic_match=True):
    (sharedOps, vOnlyOps) = \
        getVersionDifferences(vistrail, [v1, v2])

    sharedWorkflow = DBWorkflow()
    performAdds(sharedOps, sharedWorkflow)

    # FIXME better to do additional ops (and do deletes) or do this?
    v1Workflow = DBWorkflow()
    v1Ops = vOnlyOps[0][2]
    performAdds(v1Ops, v1Workflow)

    v2Workflow = DBWorkflow()
    v2Ops = vOnlyOps[1][2]
    performAdds(v2Ops, v2Workflow)

    # FIXME connections do not check their ports
    sharedModuleIds = []
    sharedConnectionIds = []
    sharedFunctionIds = {}
    for op in sharedOps:
        if op.what == 'module' or op.what == 'abstraction' or \
                op.what == 'group':
            sharedModuleIds.append(getNewObjId(op))
        elif op.what == 'connection':
            sharedConnectionIds.append(getNewObjId(op))
        elif op.what == 'function':
            sharedFunctionIds[getNewObjId(op)] = op.db_parentObjId
    
    vOnlyModules = []
    vOnlyConnections = []
    paramChgModules = {}
    for (vAdds, vDeletes, _) in vOnlyOps:
        moduleDeleteIds = []
        connectionDeleteIds = []
        for op in vDeletes:
            if op.what == 'module' or op.what == 'abstraction' or \
                    op.what == 'group':
                moduleDeleteIds.append(getOldObjId(op))
                if getOldObjId(op) in sharedModuleIds:
                    sharedModuleIds.remove(getOldObjId(op))
                if paramChgModules.has_key(getOldObjId(op)):
                    del paramChgModules[getOldObjId(op)]
            elif op.what == 'function' and \
                    (op.db_parentObjType == 'module' or 
                     op.db_parentObjType == 'abstraction' or 
                     op.db_parentObjType == 'group') and \
                     op.db_parentObjId in sharedModuleIds:
                # have a function change
                paramChgModules[op.db_parentObjId] = None
                sharedModuleIds.remove(op.db_parentObjId)
            elif op.what == 'parameter' and op.db_parentObjType == 'function' \
                    and sharedFunctionIds.has_key(op.db_parentObjId):
                # have a parameter change
                moduleId = sharedFunctionIds[op.db_parentObjId]
                if moduleId in sharedModuleIds:
                    paramChgModules[moduleId] = None
                    sharedModuleIds.remove(moduleId)
            elif op.what == 'connection':
                connectionDeleteIds.append(getOldObjId(op))
                if getOldObjId(op) in sharedConnectionIds:
                    sharedConnectionIds.remove(getOldObjId(op))

        moduleAddIds = []
        connectionAddIds = []
        for op in vAdds:
            if op.what == 'module' or op.what == 'abstraction' or \
                    op.what == 'group':
                moduleAddIds.append(getNewObjId(op))
            elif (op.what == 'function' and
                  (op.db_parentObjType == 'module' or
                   op.db_parentObjType == 'abstraction' or
                   op.db_parentObjType == 'group') and
                  op.db_parentObjId in sharedModuleIds):
                # have a function change
                paramChgModules[op.db_parentObjId] = None
                sharedModuleIds.remove(op.db_parentObjId)
            elif op.what == 'parameter' and op.db_parentObjType == 'function' \
                    and sharedFunctionIds.has_key(op.db_parentObjId):
                # have a parameter change
                moduleId = sharedFunctionIds[op.db_parentObjId]
                if moduleId in sharedModuleIds:
                    paramChgModules[moduleId] = None
                    sharedModuleIds.remove(moduleId)
            elif op.what == 'connection':
                connectionAddIds.append(getOldObjId(op))

        vOnlyModules.append((moduleAddIds, moduleDeleteIds))
        vOnlyConnections.append((connectionAddIds, connectionDeleteIds))

    sharedModulePairs = [(id, id) for id in sharedModuleIds]
    v1Only = vOnlyModules[0][0]
    v2Only = vOnlyModules[1][0]
    for id in vOnlyModules[1][1]:
        if id not in vOnlyModules[0][1]:
            v1Only.append(id)
    for id in vOnlyModules[0][1]:
        if id not in vOnlyModules[1][1]:
            v2Only.append(id)

    sharedConnectionPairs = [(id, id) for id in sharedConnectionIds]
    c1Only = vOnlyConnections[0][0]
    c2Only = vOnlyConnections[1][0]
    for id in vOnlyConnections[1][1]:
        if id not in vOnlyConnections[0][1]:
            c1Only.append(id)
    for id in vOnlyConnections[0][1]:
        if id not in vOnlyConnections[1][1]:
            c2Only.append(id)

    paramChgModulePairs = [(id, id) for id in paramChgModules.keys()]

    # print "^^^^ SHARED MODULE PAIRS:", sharedModulePairs
    if heuristic_match:
        (heuristicModulePairs, heuristicConnectionPairs, v1Only, v2Only, \
             c1Only, c2Only) = do_heuristic_diff(v1Workflow, v2Workflow, \
                                                     v1Only, v2Only, \
                                                     c1Only, c2Only)
        paramChgModulePairs.extend(heuristicModulePairs)

    (heuristicModulePairs, paramChanges) = \
        check_params_diff(v1Workflow, v2Workflow, paramChgModulePairs, 
                          True, heuristic_match)

    return (v1Workflow, v2Workflow, 
            sharedModulePairs, heuristicModulePairs, v1Only, v2Only, 
            paramChanges, sharedConnectionPairs, heuristicConnectionPairs, 
            c1Only, c2Only)

def do_heuristic_diff(v1Workflow, v2Workflow, v1_modules, v2_modules, 
                      v1_connections, v2_connections):    
    # add heuristic matches
    heuristicModulePairs = []
    heuristicConnectionPairs = []
    paramChgModulePairs = []
    
    v1Only = copy.copy(v1_modules)
    v2Only = copy.copy(v2_modules)
    c1Only = copy.copy(v1_connections)
    c2Only = copy.copy(v2_connections)

    # we now check all heuristic pairs for parameter changes
    # match modules
    # for (m1_id, m2_id) in paramChgModulePairs[:]:
    #     m1 = v1Workflow.db_get_module(m1_id)
    #     m2 = v2Workflow.db_get_module(m2_id)
    #     if heuristicModuleMatch(m1, m2) == 1:
    #         # paramChgModulePairs.remove((m1_id, m2_id))
    #         # heuristicModulePairs.append((m1_id, m2_id))
    #         pass

    for m1_id in v1Only[:]:
        m1 = v1Workflow.db_get_module(m1_id)
        match = None
        for m2_id in v2Only:
            m2 = v2Workflow.db_get_module(m2_id)
            isMatch = heuristicModuleMatch(m1, m2)
            if isMatch == 1:
                match = (m1_id, m2_id)
                break
            elif isMatch == 0:
                match = (m1_id, m2_id)
        if match is not None:
            v1Only.remove(match[0])
            v2Only.remove(match[1])
            # we now check all heuristic pairs for parameter changes
            heuristicModulePairs.append(match)
            # paramChgModulePairs.append(match)

    # match connections
    for c1_id in c1Only[:]:
        c1 = v1Workflow.db_get_connection(c1_id)
        match = None
        for c2_id in c2Only:
            c2 = v2Workflow.db_get_connection(c2_id)
            isMatch = heuristicConnectionMatch(c1, c2)
            if isMatch == 1:
                match = (c1_id, c2_id)
                break
            elif isMatch == 0:
                match = (c1_id, c2_id)
        if match is not None:
            # don't have port changes yet
            c1Only.remove(match[0])
            c2Only.remove(match[1])
            heuristicConnectionPairs.append(match)

    return (heuristicModulePairs, heuristicConnectionPairs, v1Only, v2Only,
            c1Only, c2Only)

def check_params_diff(v1Workflow, v2Workflow, paramChgModulePairs, 
                      same_vt=True, heuristic_match=True):
    matched = []
    paramChanges = []
    # print "^^^^ PARAM CHG PAIRS:", paramChgModulePairs
    for (m1_id, m2_id) in paramChgModulePairs:
        m1 = v1Workflow.db_get_module(m1_id)
        m2 = v2Workflow.db_get_module(m2_id)
        moduleParamChanges = getParamChanges(m1, m2, same_vt, heuristic_match)
        if len(moduleParamChanges) > 0:
            paramChanges.append(((m1_id, m2_id), moduleParamChanges))
        else:
            # heuristicModulePairs.append((m1_id, m2_id))
            matched.append((m1_id, m2_id))

    return (matched, paramChanges)    

def getWorkflowDiff(vt_pair_1, vt_pair_2, heuristic_match=True):
    (vistrail_1, v_1) = vt_pair_1
    (vistrail_2, v_2) = vt_pair_2
    
    if vistrail_1 == vistrail_2:
        return getWorkflowDiffCommon(vistrail_1, v_1, v_2, heuristic_match)
    
    workflow_1 = materializeWorkflow(vistrail_1, v_1)
    workflow_2 = materializeWorkflow(vistrail_2, v_2)
    modules_1 = workflow_1.db_modules_id_index.keys()
    modules_2 = workflow_2.db_modules_id_index.keys()
    conns_1 = workflow_1.db_connections_id_index.keys()
    conns_2 = workflow_2.db_connections_id_index.keys()

    if heuristic_match:
        (m_matches, c_matches, modules_1, modules_2, conns_1, conns_2) = \
            do_heuristic_diff(workflow_1, workflow_2, modules_1, modules_2, \
                                  conns_1, conns_2)
        (m_matches, param_changes) = check_params_diff(workflow_1, workflow_2, 
                                                       m_matches, False,
                                                       heuristic_match)
        return (workflow_1, workflow_2, [], m_matches, modules_1, modules_2,
                param_changes, [], c_matches, conns_1, conns_2)

    return (workflow_1, workflow_2, [], [], modules_1, modules_2, [], [], [], 
            conns_1, conns_2)

################################################################################

import unittest
import core.system

class TestDBVistrailService(unittest.TestCase):
    def test_parameter_heuristic(self):
        from core.vistrail.module_param import ModuleParam
        
        param1 = ModuleParam(id=0, pos=0, type='String', val='abc')
        param2 = ModuleParam(id=1, pos=0, type='String', val='abc')
        param3 = ModuleParam(id=2, pos=1, type='Float', val='1.0')
        param4 = ModuleParam(id=3, pos=0, type='String', val='def')
        param5 = ModuleParam(id=4, pos=1, type='String', val='abc')

        # test basic equality
        assert heuristicParameterMatch(param1, param2) == 1
        # test basic inequality
        assert heuristicParameterMatch(param1, param3) == -1
        # test partial match
        assert heuristicParameterMatch(param1, param4) == 0
        # test position inequality
        assert heuristicParameterMatch(param1, param5) == -1

    def test_function_heuristic(self):
        from core.vistrail.module_param import ModuleParam
        from core.vistrail.module_function import ModuleFunction
        
        param1 = ModuleParam(id=0, pos=0, type='String', val='abc')
        param2 = ModuleParam(id=1, pos=1, type='Float', val='1.0')
        param3 = ModuleParam(id=2, pos=0, type='String', val='abc')
        param4 = ModuleParam(id=3, pos=1, type='Float', val='1.0')
        param5 = ModuleParam(id=4, pos=0, type='String', val='abc')
        param6 = ModuleParam(id=5, pos=1, type='Float', val='2.0')

        function1 = ModuleFunction(name='f1', parameters=[param1, param2])
        function2 = ModuleFunction(name='f1', parameters=[param3, param4])
        function3 = ModuleFunction(name='f1', parameters=[param5, param6])
        function4 = ModuleFunction(name='f2', parameters=[param1, param2])
        function5 = ModuleFunction(name='f1', parameters=[param1])

        # test basic equality
        assert heuristicFunctionMatch(function1, function2) == 1
        # test partial match
        assert heuristicFunctionMatch(function1, function3) == 0
        # test basic inequality
        assert heuristicFunctionMatch(function1, function4) == -1
        # test length inequality
        assert heuristicFunctionMatch(function1, function5) == 0

    def test_module_heuristic(self):
        from core.vistrail.module_param import ModuleParam
        from core.vistrail.module_function import ModuleFunction
        from core.vistrail.module import Module

        param1 = ModuleParam(id=0, pos=0, type='String', val='abc')
        param2 = ModuleParam(id=1, pos=1, type='Float', val='1.0')
        param3 = ModuleParam(id=2, pos=0, type='String', val='abc')
        param4 = ModuleParam(id=3, pos=1, type='Float', val='1.0')
        param5 = ModuleParam(id=4, pos=0, type='Integer', val='2')
        param6 = ModuleParam(id=5, pos=0, type='Integer', val='2')

        function1 = ModuleFunction(name='f1', parameters=[param1, param2])
        function2 = ModuleFunction(name='f1', parameters=[param3, param4])
        function3 = ModuleFunction(name='f2', parameters=[param5])
        function4 = ModuleFunction(name='f2', parameters=[param6])
        function5 = ModuleFunction(name='f1', parameters=[param2, param4])
        function6 = ModuleFunction(name='f2', parameters=[param5])

        module1 = Module(name='m1', functions=[function1, function3])
        module2 = Module(name='m1', functions=[function2, function4])
        module3 = Module(name='m2', functions=[function1, function2])
        module4 = Module(name='m1', functions=[function5])
        module5 = Module(name='m1', functions=[function5, function6])

        # test basic equality
        assert heuristicModuleMatch(module1, module2) == 1
        # test basic inequality
        assert heuristicModuleMatch(module1, module3) == -1
        # test length inequality
        assert heuristicModuleMatch(module1, module4) == 0
        # test parameter change inequality
        assert heuristicModuleMatch(module1, module5) == 0

if __name__ == '__main__':
    unittest.main()

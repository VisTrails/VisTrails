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

from core.vistrail.action import Action
from core.log.log import Log
from core.vistrail.operation import AddOp, ChangeOp, DeleteOp
from db.services.io import SaveBundle
import db.services.io
import db.services.vistrail
import db.services.action
from xml.dom.minidom import parse, getDOMImplementation

def get_db_vistrail_list(config):
    return db.services.io.get_db_object_list(config,'vistrail')

def get_workflow(vt, version):
    from core.vistrail.pipeline import Pipeline
    workflow = db.services.vistrail.materializeWorkflow(vt, version)
    Pipeline.convert(workflow)
    return workflow

def open_workflow(filename):
    from core.vistrail.pipeline import Pipeline
    workflow = db.services.io.open_workflow_from_xml(filename)
    Pipeline.convert(workflow)
    return workflow

def save_workflow(workflow, filename):
    db.services.io.save_workflow_to_xml(workflow, filename)

def save_vistrail_to_xml(vistrail, filename):
    db.services.io.save_vistrail_to_xml(vistrail, filename)

def load_vistrail(locator, is_abstraction=False):
    from core.vistrail.vistrail import Vistrail

    abstraction_files = []
    thumbnail_files = []
    mashups = []
    vistrail = None
    if locator is None:
        vistrail = Vistrail()
    else:
        res = locator.load()
        if type(res) == type(SaveBundle(None)):
            vistrail = res.vistrail
            abstraction_files.extend(res.abstractions)
            thumbnail_files.extend(res.thumbnails)
            mashups.extend(res.mashups)
        else:
            vistrail = res
    vistrail.is_abstraction = is_abstraction
    return (vistrail, abstraction_files, thumbnail_files, mashups)
    
def open_registry(filename):
    from core.modules.module_registry import ModuleRegistry
    registry = db.services.io.open_registry_from_xml(filename)
    ModuleRegistry.convert(registry)
    return registry

def unserialize(str, klass):
    """returns VisTrails entity given an XML serialization

    """
    obj = db.services.io.unserialize(str, klass.vtType)
    if obj:
        #maybe we should also put a try except here
        klass.convert(obj)
    return obj

def serialize(object):
    """returns XML serialization for any VisTrails entity

    """
    return db.services.io.serialize(object)

def open_log(fname, was_appended=False):
    log = db.services.io.open_log_from_xml(fname, was_appended)
    Log.convert(log)
    return log


def merge_logs(new_log, log_fname):
    log = db.services.io.merge_logs(new_log, log_fname)
    Log.convert(log)
    return log

def get_workflow_diff(vt_pair_1, vt_pair_2):
    """get_workflow_diff( tuple(Vistrail, id), tuple(Vistrail, id) ) ->
            Pipeline, Pipeline, [tuple(id, id)], [tuple(id, id)], 
            [id], [id], [tuple(id, id, list)]

    Return a difference between two workflows referenced as vistrails.
    """

    from core.vistrail.pipeline import Pipeline
    (v1, v2, pairs, heuristic_pairs, v1_only, v2_only, param_changes, \
         _, _, _, _) = \
         db.services.vistrail.getWorkflowDiff(vt_pair_1, vt_pair_2, True)
    Pipeline.convert(v1)
    Pipeline.convert(v2)
    return (v1, v2, pairs, heuristic_pairs, v1_only, v2_only, param_changes)

def get_workflow_diff_with_connections(vt_pair_1, vt_pair_2):
    """get_workflow_diff_with_connections

    Similar to get_workflow_diff but with connection pairings.
    """

    from core.vistrail.pipeline import Pipeline
    (v1, v2, m_pairs, m_heuristic, v1_only, v2_only, param_changes, \
         c_pairs, c_heuristic, c1_only, c2_only) = \
         db.services.vistrail.getWorkflowDiff(vt_pair_1, vt_pair_2, False)
    Pipeline.convert(v1)
    Pipeline.convert(v2)
    return (v1, v2, m_pairs, m_heustric, v1_only, v2_only, param_changes,
            c_pairs, c_heuristic, c1_only, c2_only)

def getPathAsAction(vt, v1, v2, do_copy=False):
    a = db.services.vistrail.getPathAsAction(vt, v1, v2, do_copy)
    Action.convert(a)
    return a

def fixActions(vt, v, actions):
    return db.services.vistrail.fixActions(vt, v, actions)

def convert_operation_list(ops):
    for op in ops:
        if op.vtType == 'add':
            AddOp.convert(op)
        elif op.vtType == 'change':
            ChangeOp.convert(op)
        elif op.vtType == 'delete':
            DeleteOp.convert(op)
        else:
            raise Exception("Unknown operation type '%s'" % op.vtType)

def create_action(action_list):
    """create_action(action_list: list) -> Action
    where action_list is a list of tuples
     (
      type, 
      object, 
      parent_type=None,
      parent_id=None,
      new_obj=None
     )
    and the method returns a *single* action that accomplishes all 
    of the operations.

    Examples: create_action([('add', module1), ('delete', connection2)]
              create_action([('add', param1, 'function', function1),
                             ('change', old_func, new_func, 'module', m1)])
    Note that create_action([('add', module)]) adds a module and *all* of its
    children.
    """
    action = db.services.action.create_action(action_list)
    Action.convert(action)
    return action
    
def create_add_op_chain(object, parent=(None, None)):
    """create_add_op_chain(object: object, 
                           parent=(type : str, id : long)) -> [op]
    where [op] is a list of operations to add the given object and its
    children to a workflow.
    """
    ops = db.services.action.create_add_op_chain(object, parent)
    convert_operation_list(ops)
    return ops

def create_change_op_chain(old_obj, new_obj, parent=(None,None)):
    """create_change_op_chain(old_obj: object, new_obj: object, 
                              parent=(type : str, id : long)) -> [op]
    where [op] is a list of operations to change the given object and its
    children to the new object in a workflow.
    """
    ops = db.services.action.create_change_op_chain(old_obj, new_obj, parent)
    convert_operation_list(ops)
    return ops

def create_delete_op_chain(object, parent=(None, None)):
    """create_delete_op_chain(object: object, 
                              parent=(type : str, id : long)) -> [op]
    where [op] is a list of operations to delete the given object and its
    children from a workflow.
    """
    ops = db.services.action.create_delete_op_chain(object, parent)
    convert_operation_list(ops)
    return ops

def create_temp_folder(prefix='vt_save'):
    return db.services.io.create_temp_folder(prefix=prefix)

def remove_temp_folder(temp_dir):
    db.services.io.remove_temp_folder(temp_dir)

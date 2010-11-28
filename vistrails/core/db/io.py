############################################################################
##
## Copyright (C) 2006-2010 University of Utah. All rights reserved.
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
    vistrail = None
    if locator is None:
        vistrail = Vistrail()
    else:
        res = locator.load()
        if type(res) == type(SaveBundle(None)):
            vistrail = res.vistrail
            abstraction_files.extend(res.abstractions)
            thumbnail_files.extend(res.thumbnails)
        else:
            vistrail = res
    vistrail.is_abstraction = is_abstraction
    return (vistrail, abstraction_files, thumbnail_files)
    
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

def merge_logs(new_log, log_fname):
    log = db.services.io.merge_logs(new_log, log_fname)
    Log.convert(log)
    return log

def get_workflow_diff(vt, v1, v2):
    from core.vistrail.pipeline import Pipeline
    (v1, v2, pairs, heuristic_pairs, v1_only, v2_only, param_changes, \
         _, _, _, _) = db.services.vistrail.getWorkflowDiff(vt, v1, v2, True)
    Pipeline.convert(v1)
    Pipeline.convert(v2)
    return (v1, v2, pairs, heuristic_pairs, v1_only, v2_only, param_changes)

def get_workflow_diff_with_connections(vt, v1, v2):
    from core.vistrail.pipeline import Pipeline
    (v1, v2, m_pairs, m_heuristic, v1_only, v2_only, param_changes, \
         c_pairs, c_heuristic, c1_only, c2_only) = \
         db.services.vistrail.getWorkflowDiff(vt, v1, v2, False)
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

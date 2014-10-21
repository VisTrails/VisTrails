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
from vistrails.core.vistrail.action import Action
from vistrails.core.log.log import Log
from vistrails.core.vistrail.operation import AddOp, ChangeOp, DeleteOp
from vistrails.db.services.io import SaveBundle
import vistrails.db.services.io
import vistrails.db.services.vistrail
import vistrails.db.services.action
from xml.dom.minidom import parse, getDOMImplementation

def get_db_vistrail_list(config):
    return vistrails.db.services.io.get_db_object_list(config,'vistrail')

def get_workflow(vt, version):
    from vistrails.core.vistrail.pipeline import Pipeline
    workflow = vistrails.db.services.vistrail.materializeWorkflow(vt, version)
    Pipeline.convert(workflow)
    return workflow

def open_workflow(filename):
    from vistrails.core.vistrail.pipeline import Pipeline
    workflow = vistrails.db.services.io.open_workflow_from_xml(filename)
    Pipeline.convert(workflow)
    return workflow

def save_workflow(workflow, filename):
    vistrails.db.services.io.save_workflow_to_xml(workflow, filename)

def save_vistrail_to_xml(vistrail, filename):
    vistrails.db.services.io.save_vistrail_to_xml(vistrail, filename)

def load_vistrail(locator, is_abstraction=False):
    from vistrails.core.vistrail.vistrail import Vistrail

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
    from vistrails.core.modules.module_registry import ModuleRegistry
    registry = vistrails.db.services.io.open_registry_from_xml(filename)
    ModuleRegistry.convert(registry)
    return registry

def unserialize(str, klass):
    """returns VisTrails entity given an XML serialization

    """
    obj = vistrails.db.services.io.unserialize(str, klass.vtType)
    if obj:
        #maybe we should also put a try except here
        klass.convert(obj)
    return obj

def serialize(object):
    """returns XML serialization for any VisTrails entity

    """
    return vistrails.db.services.io.serialize(object)

def open_log(fname, was_appended=False):
    log = vistrails.db.services.io.open_log_from_xml(fname, was_appended)
    Log.convert(log)
    return log


def merge_logs(new_log, log_fname):
    log = vistrails.db.services.io.merge_logs(new_log, log_fname)
    Log.convert(log)
    return log

def get_workflow_diff(vt_pair_1, vt_pair_2):
    """get_workflow_diff( tuple(Vistrail, id), tuple(Vistrail, id) ) ->
            Pipeline, Pipeline, [tuple(id, id)], [tuple(id, id)], 
            [id], [id], [tuple(id, id, list)]

    Return a difference between two workflows referenced as vistrails.
    """

    from vistrails.core.vistrail.pipeline import Pipeline
    (v1, v2, pairs, heuristic_pairs, v1_only, v2_only, param_changes,
     cparam_changes, annot_changes, _, _, _, _) = \
         vistrails.db.services.vistrail.getWorkflowDiff(vt_pair_1, vt_pair_2,
                                                        True)
    Pipeline.convert(v1)
    Pipeline.convert(v2)
    return (v1, v2, pairs, heuristic_pairs, v1_only, v2_only, param_changes,
            cparam_changes, annot_changes)

def get_workflow_diff_with_connections(vt_pair_1, vt_pair_2):
    """get_workflow_diff_with_connections

    Similar to get_workflow_diff but with connection pairings.
    """

    from vistrails.core.vistrail.pipeline import Pipeline
    (v1, v2, m_pairs, m_heuristic, v1_only, v2_only, param_changes,
     cparam_changes, annot_changes, c_pairs, c_heuristic, c1_only, c2_only) =\
         vistrails.db.services.vistrail.getWorkflowDiff(vt_pair_1, vt_pair_2,
                                                        False)
    Pipeline.convert(v1)
    Pipeline.convert(v2)
    return (v1, v2, m_pairs, m_heuristic, v1_only, v2_only, param_changes,
            cparam_changes, annot_changes, c_pairs, c_heuristic, c1_only,
            c2_only)

def getPathAsAction(vt, v1, v2, do_copy=False):
    a = vistrails.db.services.vistrail.getPathAsAction(vt, v1, v2, do_copy)
    Action.convert(a)
    return a

def fixActions(vt, v, actions):
    return vistrails.db.services.vistrail.fixActions(vt, v, actions)

def convert_operation_list(ops):
    for op in ops:
        if op.vtType == 'add':
            AddOp.convert(op)
        elif op.vtType == 'change':
            ChangeOp.convert(op)
        elif op.vtType == 'delete':
            DeleteOp.convert(op)
        else:
            raise TypeError("Unknown operation type '%s'" % op.vtType)

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
    action = vistrails.db.services.action.create_action(action_list)
    Action.convert(action)
    return action
    
def create_add_op_chain(object, parent=(None, None)):
    """create_add_op_chain(object: object, 
                           parent=(type : str, id : long)) -> [op]
    where [op] is a list of operations to add the given object and its
    children to a workflow.
    """
    ops = vistrails.db.services.action.create_add_op_chain(object, parent)
    convert_operation_list(ops)
    return ops

def create_change_op_chain(old_obj, new_obj, parent=(None,None)):
    """create_change_op_chain(old_obj: object, new_obj: object, 
                              parent=(type : str, id : long)) -> [op]
    where [op] is a list of operations to change the given object and its
    children to the new object in a workflow.
    """
    ops = vistrails.db.services.action.create_change_op_chain(old_obj, new_obj, parent)
    convert_operation_list(ops)
    return ops

def create_delete_op_chain(object, parent=(None, None)):
    """create_delete_op_chain(object: object, 
                              parent=(type : str, id : long)) -> [op]
    where [op] is a list of operations to delete the given object and its
    children from a workflow.
    """
    ops = vistrails.db.services.action.create_delete_op_chain(object, parent)
    convert_operation_list(ops)
    return ops

def create_temp_folder(prefix='vt_save'):
    return vistrails.db.services.io.create_temp_folder(prefix=prefix)

def remove_temp_folder(temp_dir):
    vistrails.db.services.io.remove_temp_folder(temp_dir)

def load_startup(startup_fname):
    from vistrails.core.startup import VistrailsStartup
    startup = vistrails.db.services.io.open_startup_from_xml(startup_fname)
    VistrailsStartup.convert(startup)
    return startup

def save_startup(startup, fname):
    startup = vistrails.db.services.io.save_startup_to_xml(startup, fname)
    return startup
    

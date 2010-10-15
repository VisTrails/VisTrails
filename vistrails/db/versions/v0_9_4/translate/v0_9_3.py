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

import copy
from db.versions.v0_9_4.domain import DBVistrail, DBAction, DBTag, DBModule, \
    DBConnection, DBPortSpec, DBFunction, DBParameter, DBLocation, DBAdd, \
    DBChange, DBDelete, DBAnnotation, DBPort, DBGroup, \
    DBWorkflow, DBLog, DBAbstraction

def translateVistrail(_vistrail):
    def update_workflow(old_obj, translate_dict):
        return DBWorkflow.update_version(old_obj.db_workflow, 
                                         translate_dict, DBWorkflow())
    def update_operations(old_obj, trans_dict):
        def update_abstractionRef(old_obj, trans_dict):
            return DBAbstraction.update_version(old_obj.db_data, trans_dict)
        new_ops = []
        for obj in old_obj.db_operations:
            if obj.vtType == 'add':
                if obj.db_what == 'abstractionRef':
                    trans_dict['DBAdd'] = {'data': update_abstractionRef}
                    new_op = DBAdd.update_version(obj, trans_dict)
                    new_op.db_what = 'abstraction'
                    new_ops.append(new_op)
                    del trans_dict['DBAdd']
                else:
                    new_op = DBAdd.update_version(obj, trans_dict)
                    if obj.db_parentObjType == 'abstractionRef':
                        new_op.db_parentObjType = 'abstraction'
                    new_ops.append(new_op)
            elif obj.vtType == 'delete':
                new_ops.append(DBDelete.update_version(obj, trans_dict))
            elif obj.vtType == 'change':
                if obj.db_what == 'abstractionRef':
                    trans_dict['DBChange'] = {'data': update_abstractionRef}
                    new_op = DBChange.update_version(obj, trans_dict)
                    new_op.db_what = 'abstraction'
                    new_ops.append(new_op)
                    del trans_dict['DBChange']
                else:
                    new_op = DBChange.update_version(obj, trans_dict)
                    if obj.db_parentObjType == 'abstractionRef':
                        new_op.db_parentObjType = 'abstraction'
                    new_ops.append(new_op)
        return new_ops

    translate_dict = {'DBGroup': {'workflow': update_workflow},
                      'DBAction': {'operations': update_operations}}
    vistrail = DBVistrail.update_version(_vistrail, translate_dict)
    vistrail.db_version = '0.9.4'
    return vistrail

def translateWorkflow(_workflow):
    def update_workflow(old_obj, translate_dict):
        return DBWorkflow.update_version(old_obj.db_workflow, 
                                         translate_dict, DBWorkflow())
    def update_modules(old_obj, trans_dict):
        new_modules = []
        for obj in old_obj.db_modules:
            if obj.vtType == 'module':
                new_modules.append(DBModule.update_version(obj, trans_dict))
            elif obj.vtType == 'abstractionRef':
                new_modules.append(DBAbstraction.update_version(obj,
                                                                trans_dict))
            elif obj.vtType == 'group':
                new_modules.append(DBGroup.update_version(obj, trans_dict))
        return new_modules

    translate_dict = {'DBGroup': {'workflow': update_workflow},
                      'DBWorkflow': {'modules': update_modules}}
    workflow = DBWorkflow.update_version(_workflow, translate_dict)
    workflow.db_version = '0.9.4'
    return workflow

def translateLog(_log):
    translate_dict = {}
    log = DBLog.update_version(_log, translate_dict)
    log.db_version = '0.9.4'
    return log

############################################################################
##
## Copyright (C) 2006-2009 University of Utah. All rights reserved.
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
from db.versions.v0_9_3.domain import DBVistrail, DBAction, DBTag, DBModule, \
    DBConnection, DBPortSpec, DBFunction, DBParameter, DBLocation, DBAdd, \
    DBChange, DBDelete, DBAnnotation, DBPort, DBAbstractionRef, DBGroup, \
    DBWorkflow, DBLog

def translateVistrail(_vistrail):
    def update_key(old_obj, translate_dict):
        return '__notes__'

    def update_annotation(old_obj, translate_dict):
        new_dict = {'DBAnnotation': {'key': update_key}}
        new_list = []
        for annotation in old_obj.db_annotations:
            if annotation.db_key == 'notes':
                new_list.append(DBAnnotation.update_version(annotation, 
                                                            new_dict))
            else:
                new_list.append(DBAnnotation.update_version(annotation,
                                                            {}))
        return new_list
                
    def update_session(old_obj, translate_dict):
        if not old_obj.db_session:
            session = None
        else:
            session = long(old_obj.db_session)
        return session

    def update_workflow(old_obj, translate_dict):
        return DBWorkflow.update_version(old_obj.db_workflow, translate_dict)

    translate_dict = {'DBAction': {'annotations': update_annotation,
                                   'session': update_session},
                      'DBGroup': {'workflow': update_workflow}}
    # pass DBVistrail because domain contains enriched version of the auto_gen
    vistrail = DBVistrail.update_version(_vistrail, translate_dict)
    vistrail.db_version = '0.9.3'
    return vistrail

def translateWorkflow(_workflow):
    def update_workflow(old_obj, translate_dict):
        return DBWorkflow.update_version(old_obj.db_workflow, translate_dict)
    translate_dict = {'DBGroup': {'workflow': update_workflow}}
    workflow = update_workflow(_workflow, translate_dict)
    workflow.db_version = '0.9.3'
    return workflow

def translateLog(_log):
    log = DBLog.update_version(_log, translate_dict)
    log.db_version = '0.9.3'
    return log

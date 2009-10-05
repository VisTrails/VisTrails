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

from db.versions.v0_9_3.domain import DBVistrail, DBWorkflow, DBLog

def translateVistrail(_vistrail):
    def update_workflow(old_obj, translate_dict):
        return DBWorkflow.update_version(old_obj.db_workflow, 
                                         translate_dict, DBWorkflow())

    translate_dict = {'DBGroup': {'workflow': update_workflow}}
    # pass DBVistrail because domain contains enriched version of the auto_gen
    vistrail = DBVistrail.update_version(_vistrail, translate_dict)
    vistrail.db_version = '0.9.3'
    return vistrail

def translateWorkflow(_workflow):
    def update_workflow(old_obj, translate_dict):
        return DBWorkflow.update_version(old_obj.db_workflow, 
                                         translate_dict, DBWorkflow())

    translate_dict = {'DBGroup': {'workflow': update_workflow}}
    workflow = DBWorkflow.update_version(_workflow, translate_dict)
    workflow.db_version = '0.9.3'
    return workflow

def translateLog(_log):
    translate_dict = {}
    log = DBLog.update_version(_log, translate_dict)
    log.db_version = '0.9.3'
    return log


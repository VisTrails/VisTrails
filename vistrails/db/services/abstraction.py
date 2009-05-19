
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

from db.domain import DBWorkflow
from db.services.action_chain import getActionChain, getCurrentOperationDict, \
    getCurrentOperations

def getNewObjId(operation):
    if operation.vtType == 'change':
        return operation.db_newObjId
    return operation.db_objectId

def update_id_scope(vistrail):
    for action in vistrail.db_actions:
        vistrail.idScope.updateBeginId('action', action.db_id+1)
        for operation in action.db_operations:
            vistrail.idScope.updateBeginId('operation', operation.db_id+1)
            if operation.vtType == 'add' or operation.vtType == 'change':
                # update ids of data
                vistrail.idScope.updateBeginId(operation.db_what, 
                                               getNewObjId(operation)+1)
                if operation.db_data is None:
                    if operation.vtType == 'change':
                        operation.db_objectId = operation.db_oldObjId
        for annotation in action.db_annotations:
            vistrail.idScope.updateBeginId('annotation', annotation.db_id+1)

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

from core.vistrail.location import Location
import db.services.action

def create_action(op_list):
    if len(op_list) > 0:
        from core.vistrail.action import Action
        action = db.services.action.create_action(op_list)
        Action.convert(action)
        return action
    return None

def create_action_from_ops(ops):
    if len(ops) > 0:
        from core.vistrail.action import Action
        action = db.services.action.create_action_from_ops(ops)
        Action.convert(action)
        return action
    return None

def create_paste_action(pipeline, id_scope, id_remap=None):
    action_list = []
    if id_remap is None:
        id_remap = {}
    for module in pipeline.modules.itervalues():
        module = module.do_copy(True, id_scope, id_remap)
        action_list.append(('add', module))
    for connection in pipeline.connections.itervalues():
        connection = connection.do_copy(True, id_scope, id_remap)
        action_list.append(('add', connection))
    action = create_action(action_list)

    # fun stuff to work around bug where pasted entities aren't dirty
    for (child, _, _) in action.db_children():
        child.is_dirty = True
    return action


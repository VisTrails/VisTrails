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
from auto_gen import DBAbstraction as _DBAbstraction
from id_scope import IdScope

class DBAbstraction(_DBAbstraction):
    def __init__(self, *args, **kwargs):
	_DBAbstraction.__init__(self, *args, **kwargs)
        self.idScope = IdScope()
        self.idScope.setBeginId('action', 1)

    def __copy__(self):
        return DBAbstraction.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = _DBAbstraction.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = DBAbstraction
        # need to go through and reset the index to the copied objects
        cp.idScope = copy.copy(self.idScope)
        return cp

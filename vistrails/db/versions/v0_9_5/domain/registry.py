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

from auto_gen import DBRegistry as _DBRegistry
from id_scope import IdScope

class DBRegistry(_DBRegistry):
    def __init__(self, *args, **kwargs):
	_DBRegistry.__init__(self, *args, **kwargs)
        self.idScope = IdScope()

    @staticmethod
    def update_version(old_obj, trans_dict, new_obj=None):
        if new_obj is None:
            new_obj = DBRegistry()
        new_obj = _DBRegistry.update_version(old_obj, trans_dict, new_obj)
        new_obj.update_id_scope()
        return new_obj
    
    def update_id_scope(self):
        for package in self.db_packages:
            self.idScope.updateBeginId(DBPackage.vtType, package.db_id+1)
            for descriptor in package.db_module_descriptors:
                self.idScope.updateBeginId(DBModuleDescriptor.vtType,
                                           descriptor.db_id+1)
                for port_spec in descriptor.db_portSpecs:
                    self.idScope.updateBeginId(DBPortSpec.vtType, 
                                               port_spec.db_id+1)

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

from db.domain import DBPackage, DBModuleDescriptor, DBPortSpec

def update_id_scope(registry):
    if hasattr(registry, 'update_id_scope'):
        registry.update_id_scope()
    else:
        for package in registry.db_packages:
            registry.idScope.updateBeginId(DBPackage.vtType, package.db_id+1)
            for descriptor in package.db_module_descriptors:
                registry.idScope.updateBeginId(DBModuleDescriptor.vtType,
                                               descriptor.db_id+1)
                for port_spec in descriptor.db_portSpecs:
                    registry.idScope.updateBeginId(DBPortSpec.vtType, 
                                                   port_spec.db_id+1)

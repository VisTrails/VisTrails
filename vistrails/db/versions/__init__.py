############################################################################
##
## Copyright (C) 2006-2007 University of Utah. All rights reserved.
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

import os
from core.system import vistrails_root_directory

currentVersion = '0.7.0'

def getVersionDAO(version=None):
    if version is None:
        version = currentVersion
    if version == '0.3.0':
        import db.versions.v0_3_0.persistence
        return db.versions.v0_3_0.persistence.DAOList()
    elif version == '0.3.1':
        import db.versions.v0_3_1.persistence
        return db.versions.v0_3_1.persistence.DAOList()
    elif version == '0.5.0':
        import db.versions.v0_5_0.persistence
        return db.versions.v0_5_0.persistence.DAOList()
    elif version == '0.6.0':
        import db.versions.v0_6_0.persistence
        return db.versions.v0_6_0.persistence.DAOList()
    elif version == '0.7.0':
        import db.versions.v0_7_0.persistence
        return db.versions.v0_7_0.persistence.DAOList()

def translateVistrail(vistrail, version=None):
    if version is None:
        version = vistrail.version
    
    if version == '0.3.0':
        import db.versions.v0_3_1.translate.v0_3_0
        vistrail = \
            db.versions.v0_3_1.translate.v0_3_0.translateVistrail(vistrail)
        version = '0.3.1'
    if version == '0.3.1':
        import db.versions.v0_6_0.translate.v0_3_1
        vistrail = \
            db.versions.v0_6_0.translate.v0_3_1.translateVistrail(vistrail)
        version = '0.6.0'
    if version == '0.5.0':
        import db.versions.v0_6_0.translate.v0_5_0
        vistrail = \
            db.versions.v0_6_0.translate.v0_5_0.translateVistrail(vistrail)
        version = '0.6.0'
    if version == '0.6.0':
        import db.versions.v0_7_0.translate.v0_6_0
        vistrail = \
            db.versions.v0_7_0.translate.v0_6_0.translateVistrail(vistrail)
        version = '0.7.0'
    if version != currentVersion:
        msg = "An error occurred when translating,"
        msg += "only able to translate to version '%s'" % version
        raise Exception(msg)

    return vistrail

def getVersionSchemaDir(version=None):
    if version is None:
        version = currentVersion
    
    versionName = 'v' + version.replace('.', '_')
    schemaDir = vistrails_root_directory()
    schemaDir = os.path.join(vistrails_root_directory(), 'db', 'versions', 
                             versionName, 'schemas', 'sql')
    return schemaDir

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

import copy

def translateVistrail(_vistrail):
    # FIXME should this be a deepcopy?
    vistrail = copy.deepcopy(_vistrail)
    for action in vistrail.db_get_actions():
#        print 'translating action %s' % action.db_time
        if action.db_what == 'addModule':
            if action.db_datas[0].db_cache == 0:
                action.db_datas[0].db_cache = 1
    vistrail.db_version = '0.3.1'
    return vistrail

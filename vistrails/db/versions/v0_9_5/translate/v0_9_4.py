############################################################################
##
## Copyright (C) 2006-2008 University of Utah. All rights reserved.
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
from db.versions.v0_9_5.domain import DBVistrail

def translateVistrail(_vistrail):
    def update_signature(old_obj, translate_dict):
        return old_obj.db_spec
    def update_optional(old_obj, translate_dict):
        return 0
    def update_sort_key(old_obj, translate_dict):
        return -1
    def update_sigstring(old_obj, translate_dict):
        return old_obj.db_spec

    translate_dict = {'DBPortSpec': {'sigstring': update_sigstring,
                                     'optional': update_optional,
                                     'sort_key': update_sort_key},
                      'DBPort': {'signature': update_signature}}

    # pass DBVistrail because domain contains enriched version of the auto_gen
    vistrail = DBVistrail.update_version(_vistrail, translate_dict, 
                                         DBVistrail())
    vistrail.db_version = '0.9.5'
    return vistrail

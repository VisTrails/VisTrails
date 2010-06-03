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

import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(
                os.path.abspath(__file__))), 'vistrails'))
from db.services import io
from db_utils import parse_db_cmd_line

def delete_from_db(config, obj_type, obj_id):
    db_connection = io.open_db_connection(config)
    io.delete_entity_from_db(db_connection, obj_type, obj_id)
    io.close_db_connection(db_connection)

if __name__ == '__main__':
    more_options = {'t:': ('set object type', False, 'obj_type'),
                    'i:': ('set object id', True, 'obj_id'),
                    }
    config, options = parse_db_cmd_line(sys.argv, more_options)
    obj_type = 'vistrail'
    if options['t']:
        obj_type = options['t']
    obj_id = int(options['i'])
    delete_from_db(config, obj_type, obj_id)
                   

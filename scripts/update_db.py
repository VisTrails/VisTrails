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
import tempfile
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(
                os.path.abspath(__file__))), 'vistrails'))
from db.services import io
from db.versions import currentVersion
from db_utils import parse_db_cmd_line

# DO NOT RUN THIS WHILE USERS HAVE ACCESS TO THE DATABASE!
def update_db(config, new_version=None, tmp_dir=None):
    obj_types = {'vistrail': io.open_bundle_from_db,
                 # 'workflow': io.open_from_db, 
                 # 'log': io.open_from_db,
                 # 'registry': io.open_from_db
                 }
    if new_version is None:
        new_version = currentVersion
    if tmp_dir is None:
        tmp_dir = tempfile.mkdtemp(prefix='vt_db')
        print 'creating tmpdir:', tmp_dir

    obj_id_lists = {}
    for obj_type in obj_types:
        obj_id_lists[obj_type] = io.get_db_object_list(config, obj_type)

    # read data out of database
    filenames = []
    thumbnail_dir = os.path.join(tmp_dir, 'thumbs')
    os.mkdir(thumbnail_dir)
    db_connection = io.open_db_connection(config)
    for obj_type, obj_ids in obj_id_lists.iteritems():
        for (obj_id, _, _) in obj_ids:
            old_version = io.get_db_object_version(db_connection, obj_id, 
                                                   'vistrail')

            print 'getting', obj_type, 'id', obj_id
            local_tmp_dir = os.path.join(tmp_dir, str(obj_id))
            vt_name = os.path.join(tmp_dir, str(obj_id) + '.vt')
            filenames.append(vt_name)
            os.mkdir(local_tmp_dir)
            res = obj_types[obj_type](obj_type, db_connection, obj_id,
                                      thumbnail_dir)
            io.save_vistrail_bundle_to_zip_xml(res, vt_name, local_tmp_dir)
    
    # drop the old database
    # recreate with the new version of the specs
    io.setup_db_tables(db_connection, None, old_version)

    # add the new data back
    for filename in filenames:
        (res, _) = io.open_vistrail_bundle_from_zip_xml(filename)
        io.save_vistrail_bundle_to_db(res, db_connection, 'with_ids')
    io.close_db_connection(db_connection)

if __name__ == '__main__':
    more_options = {'v:': ('set new schema version', False, 'version'),
                    }
    config, options = parse_db_cmd_line(sys.argv, more_options)
    new_version = None
    if options['v']:
        new_version = options[v]
    update_db(config, new_version)

###############################################################################
##
## Copyright (C) 2006-2011, University of Utah. 
## All rights reserved.
## Contact: contact@vistrails.org
##
## This file is part of VisTrails.
##
## "Redistribution and use in source and binary forms, with or without 
## modification, are permitted provided that the following conditions are met:
##
##  - Redistributions of source code must retain the above copyright notice, 
##    this list of conditions and the following disclaimer.
##  - Redistributions in binary form must reproduce the above copyright 
##    notice, this list of conditions and the following disclaimer in the 
##    documentation and/or other materials provided with the distribution.
##  - Neither the name of the University of Utah nor the names of its 
##    contributors may be used to endorse or promote products derived from 
##    this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
## AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
## THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR 
## PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR 
## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; 
## OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
## WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR 
## OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF 
## ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
###############################################################################

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

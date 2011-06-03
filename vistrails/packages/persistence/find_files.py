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
import shutil
import sys

vistrails_src = None
if not vistrails_src:
    vistrails_src = os.path.dirname(os.path.dirname(sys.path[0]))
if vistrails_src not in sys.path:
    sys.path.append(vistrails_src)
import db.services.io
    
def find_files(filename, version=None):
    save_bundle, save_dir = \
        db.services.io.open_vistrail_bundle_from_zip_xml(filename)
    vistrail = save_bundle.vistrail
    # FIXME hack for now, should change in the future
    log_fname = vistrail.db_log_filename
    log = db.services.io.open_log_from_xml(log_fname, True)

    if version:
        if type(version) == type(""):
            # need to lookup version number
            if version in vistrail.db_tags_name_index:
                version = vistrail.db_tags_name_index[version].db_id

    persistent_module_ids = set()
    for action in vistrail.db_actions:
        for op in action.db_operations:
            if op.db_what == 'module' and (op.vtType == 'add' or 
                                           op.vtType == 'change'):
                module = op.db_data
                if module.db_package == 'edu.utah.sci.vistrails.persistence':
                    persistent_module_ids.add(module.db_id)
                
    filenames = {}
    tags = {}
    for workflow_exec in log.db_workflow_execs:
        cur_version = workflow_exec.db_parent_version
        if version is not None and cur_version != version:
            continue
        if cur_version in vistrail.db_tags_id_index:
            tags[cur_version] = vistrail.db_tags_id_index[cur_version].db_name
        
        for module_exec in workflow_exec.db_item_execs:
            if module_exec.db_module_id in persistent_module_ids:
                for annotation in module_exec.db_annotations:
                    if annotation.db_key == 'signature':
                        if cur_version not in filenames:
                            filenames[cur_version] = set()
                        val = annotation.db_value.upper()
                        filenames[cur_version].add(os.path.join(val[:2], 
                                                                val[2:]))
    shutil.rmtree(save_dir)
    return filenames, tags
                        
if __name__ == '__main__':
    fname = sys.argv[1]
    version = sys.argv[2] if len(sys.argv) > 2 else None
    if version:
        try:
            version = int(version)
        except ValueError:
            pass
    all_files, tags = find_files(fname, version)
    for version, filenames in all_files.iteritems():
        if version in tags:
            print str(version) + ' (' + tags[version] + '):'
        else:
            print str(version) + ':'
        for fname in filenames:
            print ' ', fname
                    

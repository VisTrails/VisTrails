###############################################################################
##
## Copyright (C) 2014-2016, New York University.
## Copyright (C) 2011-2014, NYU-Poly.
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
##  - Neither the name of the New York University nor the names of its
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
from __future__ import division

import os
import shutil
import sys

vistrails_src = None
if not vistrails_src:
    vistrails_src = os.path.dirname(
        os.path.dirname(os.path.dirname(sys.path[0])))
if vistrails_src not in sys.path:
    sys.path.append(vistrails_src)

import vistrails.db.services.io

from identifiers import identifier as persistence_pkg, \
    old_identifiers as persistence_old_ids
persistence_pkg_ids = set(persistence_old_ids)
persistence_pkg_ids.add(persistence_pkg)
    
def find_files(filename, version=None):
    save_bundle, save_dir = \
        vistrails.db.services.io.open_vistrail_bundle_from_zip_xml(filename)
    vistrail = save_bundle.vistrail
    # FIXME hack for now, should change in the future
    log_fname = vistrail.db_log_filename
    log = vistrails.db.services.io.open_log_from_xml(log_fname, True)

    if version:
        if isinstance(version, basestring):
            # need to lookup version number
            if version in vistrail.db_tags_name_index:
                version = vistrail.db_tags_name_index[version].db_id

    persistent_module_ids = set()
    for action in vistrail.db_actions:
        for op in action.db_operations:
            if op.db_what == 'module' and (op.vtType == 'add' or 
                                           op.vtType == 'change'):
                module = op.db_data
                if module.db_package in persistence_pkg_ids:
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
                    

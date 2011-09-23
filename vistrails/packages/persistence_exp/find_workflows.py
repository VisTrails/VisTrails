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
import shutil
import sys

vistrails_src = None
if not vistrails_src:
    vistrails_src = os.path.dirname(os.path.dirname(sys.path[0]))
if vistrails_src not in sys.path:
    sys.path.append(vistrails_src)
    
import db.services.io
    
from compute_hash import compute_hash

def find_workflows(path_name, vistrail_dir):
    file_hash = compute_hash(path_name)
    vt_files = []
    dir_stack = [vistrail_dir]
    while dir_stack:
        dir = dir_stack.pop()
        for base in os.listdir(dir):
            name = os.path.join(dir, base)
            if os.path.isdir(name):
                dir_stack.append(name)
            elif name.endswith('.vt'):
                vt_files.append(name)

    vt_finds = {}
    for filename in vt_files:
        save_bundle, save_dir = \
            db.services.io.open_vistrail_bundle_from_zip_xml(filename)
        vistrail = save_bundle.vistrail
        log_fname = vistrail.db_log_filename
        log = db.services.io.open_log_from_xml(log_fname, True)
        
        persistent_module_ids = set()
        for action in vistrail.db_actions:
            for op in action.db_operations:
                if op.db_what == 'module' and (op.vtType == 'add' or 
                                               op.vtType == 'change'):
                    module = op.db_data
                    if module.db_package == \
                            'edu.utah.sci.vistrails.persistence':
                        persistent_module_ids.add(module.db_id)

        execs = {}
        tags = {}
        for workflow_exec in log.db_workflow_execs:
            cur_version = workflow_exec.db_parent_version
            if cur_version in vistrail.db_tags_id_index:
                tags[cur_version] = \
                    vistrail.db_tags_id_index[cur_version].db_name

            for module_exec in workflow_exec.db_item_execs:
                if module_exec.db_module_id in persistent_module_ids:
                    found = False
                    for annotation in module_exec.db_annotations:
                        if annotation.db_key == 'sha_hash':
                            if annotation.db_value == file_hash:
                                # found the file/dir
                                # do something
                                found = True
                        if annotation.db_key == 'signature':
                            val = annotation.db_value.upper()
                            cache_fname = os.path.join(val[:2], val[2:])
                    if found:
                        if cur_version not in execs:
                            execs[cur_version] = []
                        execs[cur_version].append((workflow_exec.db_ts_start,
                                                   cache_fname))

        if len(execs) > 0:
            vt_finds[filename] = (execs, tags)

        shutil.rmtree(save_dir)

    return vt_finds

if __name__ == '__main__':
    path_name = sys.argv[1]
    vistrail_dir = sys.argv[2]
    vt_finds = find_workflows(path_name, vistrail_dir)

    for fname, (execs, tags) in vt_finds.iteritems():
        print fname + ':'
        for version, exec_list in execs.iteritems():
            for (exec_time, cache_fname) in exec_list:
                if version in tags:
                    print ' ', str(version) + ' (' + tags[version] + '):', \
                        exec_time
                    print '   ', cache_fname
                else:
                    print ' ', str(version) + ':', exec_time
                    print '   ', cache_fname

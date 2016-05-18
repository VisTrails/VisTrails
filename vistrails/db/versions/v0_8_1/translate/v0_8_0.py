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

from vistrails.db import VistrailsDBException
from vistrails.db.versions.v0_8_0.domain import DBAdd, DBAnnotation, DBChange, DBDelete

# two step process
# 1. remap all the old "notes" so that they exist in the id scope
# 2. remap all the annotations that were numbered correctly
# note that for 2, we don't need to worry about uniqueness -- they are unique
# but step 1 may have taken some of their ids...

def translateVistrail(vistrail):
    id_remap = {}
    for action in vistrail.db_get_actions():
        # don't need to change key idx since none of that changes
        new_action_idx = {}
        for annotation in action.db_get_annotations():
            annotation.db_id = vistrail.idScope.getNewId(DBAnnotation.vtType)
            new_action_idx[annotation.db_id] = annotation
        action.db_annotations_id_index = new_action_idx

        for operation in action.db_get_operations():
            # never have annotations as parent objs so 
            # don't have to worry about those ids
            if operation.db_what == DBAnnotation.vtType:
                if operation.vtType == 'add':
                    new_id = vistrail.idScope.getNewId(DBAnnotation.vtType)
                    old_id = operation.db_objectId
                    operation.db_objectId = new_id
                    operation.db_data.db_id = new_id
                    id_remap[old_id] = new_id
                elif operation.vtType == 'change':
                    changed_id = operation.db_oldObjId
                    if id_remap.has_key(changed_id):
                        operation.db_oldObjId = id_remap[changed_id]
                    else:
                        raise VistrailsDBException('cannot translate')

                    new_id = vistrail.idScope.getNewId(DBAnnotation.vtType)
                    old_id = operation.db_newObjId
                    operation.db_newObjId = new_id
                    operation.db_data.db_id = new_id
                    id_remap[old_id] = new_id
                elif operation.vtType == 'delete':
                    old_id = operation.db_objectId
                    if id_remap.has_key(old_id):
                        operation.db_objectId = id_remap[old_id]
                    else:
                        raise VistrailsDBException('cannot translate')

    vistrail.db_version = '0.8.1'
    return vistrail

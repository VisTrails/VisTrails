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

import copy
from db.versions.v0_9_0.domain import DBVistrail, DBAction, DBTag, DBModule, \
    DBConnection, DBPortSpec, DBFunction, DBParameter, DBLocation, DBAdd, \
    DBChange, DBDelete, DBAnnotation, DBPort, DBAbstractionRef

def translateVistrail(_vistrail):
    vistrail = DBVistrail()

    for _action in _vistrail.db_actions:
        ops = []
        for op in _action.db_operations:
            if op.vtType == 'add':
                data = convert_data(op.db_data)
                ops.append(DBAdd(id=op.db_id,
                                 what=op.db_what,
                                 objectId=op.db_objectId,
                                 parentObjId=op.db_parentObjId,
                                 parentObjType=op.db_parentObjType,
                                 data=data))
            elif op.vtType == 'change':
                data = convert_data(op.db_data)
                ops.append(DBChange(id=op.db_id,
                                    what=op.db_what,
                                    oldObjId=op.db_oldObjId,
                                    newObjId=op.db_newObjId,
                                    parentObjId=op.db_parentObjId,
                                    parentObjType=op.db_parentObjType,
                                    data=data))
            elif op.vtType == 'delete':
                ops.append(DBDelete(id=op.db_id,
                                    what=op.db_what,
                                    objectId=op.db_objectId,
                                    parentObjId=op.db_parentObjId,
                                    parentObjType=op.db_parentObjType))
        annotations = []
        for annotation in _action.db_annotations:
            annotations.append(DBAnnotation(id=annotation.db_id,
                                            key=annotation.db_key,
                                            value=annotation.db_value))
        action = DBAction(id=_action.db_id,
                          prevId=_action.db_prevId,
                          date=_action.db_date,
                          user=_action.db_user,
                          prune=_action.db_prune,
                          operations=ops,
                          annotations=annotations)
        vistrail.db_add_action(action)

    for _tag in _vistrail.db_tags:
        tag = DBTag(id=_tag.db_id,
                    name=_tag.db_name)
        vistrail.db_add_tag(tag)

    vistrail.db_version = '0.9.0'
    return vistrail

def convert_data(child):
    if child.vtType == 'module':
        return DBModule(id=child.db_id,
                        cache=child.db_cache,
                        name=child.db_name,
                        package=child.db_package)
    elif child.vtType == 'abstractionRef':
        return DBAbstractionRef(id=child.db_id,
                                name=child.db_name,
                                cache=child.db_cache,
                                abstraction_id=child.db_abstraction_id,
                                version=child.db_version)
    elif child.vtType == 'connection':
        return DBConnection(id=child.db_id)
    elif child.vtType == 'portSpec':
        return DBPortSpec(id=child.db_id,
                          name=child.db_name,
                          type=child.db_type,
                          spec=child.db_spec)
    elif child.vtType == 'function':
        return DBFunction(id=child.db_id,
                          pos=child.db_pos,
                          name=child.db_name)
    elif child.vtType == 'parameter':
        return DBParameter(id=child.db_id,
                           pos=child.db_pos,
                           name=child.db_name,
                           type=child.db_type,
                           val=child.db_val,
                           alias=child.db_alias)
    elif child.vtType == 'location':
        return DBLocation(id=child.db_id,
                          x=child.db_x,
                          y=child.db_y)
    elif child.vtType == 'annotation':
        return DBAnnotation(id=child.db_id,
                            key=child.db_key,
                            value=child.db_value)
    elif child.vtType == 'port':
        return DBPort(id=child.db_id,
                      type=child.db_type,
                      moduleId=child.db_moduleId,
                      moduleName=child.db_moduleName,
                      name=child.db_name,
                      spec=child.db_spec)

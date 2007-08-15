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
from db.versions.v0_6_0.domain import DBVistrail, DBAction, DBTag, DBModule, \
    DBConnection, DBPortSpec, DBFunction, DBParameter, DBLocation, DBAdd, \
    DBChange, DBDelete, DBAnnotation, DBPort

def translateVistrail(_vistrail):
    # FIXME should this be a deepcopy?
    vistrail = copy.deepcopy(_vistrail)
    vistrail.__class__ = DBVistrail
    vistrail.db_tags_name_index = {}

    for child in vistrail.db_actions.itervalues():
        child.__class__ = DBAction
        child.db_annotations = {}
        child.db_annotations_key_index = {}
        for op in child.db_operations:
            if op.vtType == 'add':
                op.__class__ = DBAdd
                convert_data(op.db_data)
            elif op.vtType == 'change':
                op.__class__ = DBChange
                convert_data(op.db_data)
            elif op.vtType == 'delete':
                op.__class__ = DBDelete
        child.is_new = True

    for child in vistrail.db_tags.itervalues():
        id = child.db_time
        child.__class__ = DBTag
        child.db_id = id
        vistrail.db_tags_name_index[child.db_name] = child
        child.is_new = True

    vistrail.db_abstractions = {}
    vistrail.db_version = '0.6.0'
    return vistrail

def convert_data(child):
    if child.vtType == 'module':
        child.__class__ = DBModule
        child.db_package = None
        child.db_version = None
        child.db_annotations_key_index = {}       
        port_specs_dict = {}
        for port_spec in child.db_portSpecs:
            port_specs_dict[port_spec.id] = port_spec
        child.db_portSpecs = port_specs_dict
        child.db_portSpecs_name_index = {}
    elif child.vtType == 'connection':
        child.__class__ = DBConnection
        child.db_ports_type_index = {}
    elif child.vtType == 'portSpec':
        child.__class__ = DBPortSpec
    elif child.vtType == 'function':
        child.__class__ = DBFunction
    elif child.vtType == 'parameter':
        child.__class__ = DBParameter
    elif child.vtType == 'location':
        child.__class__ = DBLocation
    elif child.vtType == 'add':
        child.__class__ = DBAdd
    elif child.vtType == 'change':
        child.__class__ = DBChange
    elif child.vtType == 'delete':
        child.__class__ = DBDelete
    elif child.vtType == 'annotation':
        child.__class__ = DBAnnotation
    elif child.vtType == 'port':
        child.__class__ = DBPort    
    child.is_new = True

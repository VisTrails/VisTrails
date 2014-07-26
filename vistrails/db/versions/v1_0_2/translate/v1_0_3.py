###############################################################################
##
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
from vistrails.db.versions.v1_0_2.domain import DBVistrail, DBAnnotation, \
                                      DBWorkflow, DBLog, DBRegistry, \
                                      DBPortSpec, DBAdd, DBChange, DBDelete
from vistrails.core import debug
from vistrails.core.system import get_elementtree_library
ElementTree = get_elementtree_library()

import unittest

id_scope = None

def update_portSpec(old_obj, translate_dict):
    global id_scope
    
    sigs = []
    defaults = []
    labels = []
    for psi in sorted(old_obj.db_portSpecItems, key=lambda x: x.db_pos):
        sigs.append((psi.db_package, psi.db_module, psi.db_namespace))
        defaults.append(psi.db_default)
        labels.append(psi.db_label)
    new_obj = DBPortSpec.update_version(old_obj, translate_dict)
    sigstring = '(' + ','.join('%s:%s%s' %
                               (s[0], s[1], ":%s" % s[2] if s[2] else "")
                               for s in sigs) + ')'
    new_obj.db_sigstring = sigstring
    if all(not d for d in defaults):
        new_obj.db_defaults = None
    else:
        new_obj.db_defaults = unicode(defaults)
    if all(not label for label in labels):
        new_obj.db_labels = None
    else:
        new_obj.db_labels = unicode(labels)
        
    return new_obj

def update_portSpecs(old_obj, translate_dict):
    new_port_specs = []
    for port_spec in old_obj.db_portSpecs:
        new_port_specs.append(update_portSpec(port_spec, translate_dict))
    return new_port_specs

def update_portSpec_op(old_obj, translate_dict):
    return update_portSpec(old_obj.db_data, translate_dict)

def translateVistrail(_vistrail):
    """ Translate new DBVistrailVariable based vistrail variables to old
         annotation based type """
    global id_scope
    
    def update_workflow(old_obj, trans_dict):
        return DBWorkflow.update_version(old_obj.db_workflow, 
                                         trans_dict, DBWorkflow())

    def update_operations(old_obj, trans_dict):
        new_ops = []
        for obj in old_obj.db_operations:
            if obj.vtType == 'delete':
                new_ops.append(DBDelete.update_version(obj, trans_dict))
            elif obj.vtType == 'add':
                if obj.db_what == 'portSpec':
                    trans_dict['DBAdd'] = {'data': update_portSpec_op}
                    new_op = DBAdd.update_version(obj, trans_dict)
                    new_ops.append(new_op)
                    del trans_dict['DBAdd']
                else:
                    new_op = DBAdd.update_version(obj, trans_dict)
                    new_ops.append(new_op)
            elif obj.vtType == 'change':
                if obj.db_what == 'portSpec':
                    trans_dict['DBChange'] = {'data': update_portSpec_op}
                    new_op = DBChange.update_version(obj, trans_dict)
                    new_ops.append(new_op)
                    del trans_dict['DBChange']
                else:
                    new_op = DBChange.update_version(obj, trans_dict)
                    new_ops.append(new_op)
        return new_ops

    vistrail = DBVistrail()
    id_scope = vistrail.idScope

    def update_annotations(old_obj, trans_dict):
        new_annotations = []
        for a in old_obj.db_annotations:
            new_annotations.append(DBAnnotation.update_version(a, 
                                                               translate_dict))
            id_scope.updateBeginId(DBAnnotation.vtType, a.db_id)
        vars = {}
        for var in old_obj.db_vistrailVariables:
            descriptor = (var.db_package, var.db_module, var.db_namespace)
            vars[var.db_name] = (var.db_uuid, descriptor, var.db_value)
        if vars:
            new_id = id_scope.getNewId(DBAnnotation.vtType)
            annotation = DBAnnotation(id=new_id, key='__vistrail_vars__', 
                                      value=str(vars))
            new_annotations.append(annotation)

        return new_annotations

    translate_dict = {'DBModule': {'portSpecs': update_portSpecs},
                      'DBModuleDescriptor': {'portSpecs': update_portSpecs},
                      'DBAction': {'operations': update_operations},
                      'DBGroup': {'workflow': update_workflow},
                      'DBVistrail': {'annotations': update_annotations},
                      }

    vistrail = DBVistrail.update_version(_vistrail, translate_dict, vistrail)

    if _vistrail.db_parameter_explorations:
        debug.warning(("Vistrail contains %s parameter explorations that "
                      "cannot be converted") % len(_vistrail.db_parameter_explorations))

    vistrail.db_version = '1.0.2'
    return vistrail

def translateWorkflow(_workflow):
    def update_workflow(old_obj, translate_dict):
        return DBWorkflow.update_version(old_obj.db_workflow, translate_dict)
    translate_dict = {'DBModule': {'portSpecs': update_portSpecs},
                      'DBGroup': {'workflow': update_workflow}}
    workflow = DBWorkflow.update_version(_workflow, translate_dict)

    workflow.db_version = '1.0.2'
    return workflow

def translateLog(_log):
    translate_dict = {}
    log = DBLog.update_version(_log, translate_dict)
    log.db_version = '1.0.2'
    return log

def translateRegistry(_registry):
    global id_scope
    translate_dict = {'DBModuleDescriptor': {'portSpecs': update_portSpecs}}
    registry = DBRegistry()
    id_scope = registry.idScope
    vistrail = DBRegistry.update_version(_registry, translate_dict, registry)
    registry.db_version = '1.0.2'
    return registry

class TestTranslate(unittest.TestCase):
    def testParamexp(self):
        """test translating parameter explorations from 1.0.3 to 1.0.2"""
        from vistrails.db.services.io import open_bundle_from_zip_xml
        from vistrails.core.system import vistrails_root_directory
        import os
        (save_bundle, vt_save_dir) = open_bundle_from_zip_xml(DBVistrail.vtType, \
                        os.path.join(vistrails_root_directory(),
                        'tests/resources/paramexp-1.0.3.vt'))
        vistrail = translateVistrail(save_bundle.vistrail)
        # paramexps cannot be downgraded but should produce a warning
        
    def testVistrailvars(self):
        """test translating vistrail variables from 1.0.3 to 1.0.2"""
        from vistrails.db.services.io import open_bundle_from_zip_xml
        from vistrails.core.system import vistrails_root_directory
        import os
        (save_bundle, vt_save_dir) = open_bundle_from_zip_xml(DBVistrail.vtType, \
                        os.path.join(vistrails_root_directory(),
                        'tests/resources/visvar-1.0.3.vt'))
        vistrail = translateVistrail(save_bundle.vistrail)
        visvars = vistrail.db_annotations_key_index['__vistrail_vars__']
        self.assertTrue(visvars.db_value)

if __name__ == '__main__':
    from vistrails.gui.application import start_application
    v = start_application({'batch': True,
                           'nologger': True,
                           'singleInstance': False,
                           'fixedSpreadsheetCells': True})
    unittest.main()

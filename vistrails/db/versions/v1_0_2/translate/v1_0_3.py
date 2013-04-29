###############################################################################
##
## Copyright (C) 2011-2013, NYU-Poly.
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
                                      DBWorkflow, DBLog, DBRegistry
from vistrails.core import debug

import unittest

def translateVistrail(_vistrail):
    """ Translate new DBVistrailVariable based vistrail variables to old
         annotation based type """
    
    vistrail = DBVistrail.update_version(_vistrail, {})

    key = '__vistrail_vars__'

    id_scope = vistrail.idScope
    id_scope.setBeginId('annotation', _vistrail.idScope.getNewId('annotation'))
    vars = {}
    for var in _vistrail.db_vistrailVariables:
        descriptor =(var.db_package, var.db_module, var.db_namespace)
        vars[var.db_name] = (var.db_uuid, descriptor, var.db_value)

    if vars:
        new_id = id_scope.getNewId(DBAnnotation.vtType)
        annotation = DBAnnotation(id=new_id, key=key, value=str(vars))
        vistrail.db_add_annotation(annotation)

    if _vistrail.db_parameter_explorations:
        debug.warning(("Vistrail contains %s parameter explorations that "
                      "cannot be converted") % len(_vistrail.db_parameter_explorations))

    vistrail.db_version = '1.0.2'
    return vistrail

def translateWorkflow(_workflow):
    def update_workflow(old_obj, translate_dict):
        return DBWorkflow.update_version(old_obj.db_workflow, translate_dict)
    translate_dict = {'DBGroup': {'workflow': update_workflow}}
    workflow = DBWorkflow.update_version(_workflow, translate_dict)

    workflow.db_version = '1.0.2'
    return workflow

def translateLog(_log):
    translate_dict = {}
    log = DBLog.update_version(_log, translate_dict)
    log.db_version = '1.0.2'
    return log

def translateRegistry(_registry):
    translate_dict = {}
    registry = DBRegistry.update_version(_registry, translate_dict)
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
    v = start_application({'interactiveMode': False,
                           'nologger': True,
                           'singleInstance': False,
                           'fixedSpreadsheetCells': True})
    unittest.main()

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
from vistrails.db.versions.v1_0_3.domain import DBVistrail, DBVistrailVariable, \
                                      DBWorkflow, DBLog, DBRegistry, \
                                      DBAdd, DBChange, DBDelete, \
                                      DBPortSpec, DBPortSpecItem, \
                                      DBParameterExploration, \
                                      DBPEParameter, DBPEFunction, \
                                      IdScope, DBAbstraction, \
                                      DBModule, DBGroup, DBAnnotation, \
                                      DBActionAnnotation

from vistrails.db.services.vistrail import materializeWorkflow

import os
from itertools import izip
from ast import literal_eval
import unittest
from xml.dom.minidom import parseString

id_scope = None

def update_portSpec(old_obj, translate_dict):
    global id_scope
    sigstring = old_obj.db_sigstring
    sigs = []
    if sigstring and sigstring != '()':
        for sig in sigstring[1:-1].split(','):
            sigs.append(sig.split(':', 2))
    # not great to use eval...
    defaults = literal_eval(old_obj.db_defaults) if old_obj.db_defaults else []
    if isinstance(defaults, basestring):
        defaults = (defaults,)
    else:
        try:
            it = iter(defaults)
        except TypeError:
            defaults = (defaults,)
    # not great to use eval...
    labels = literal_eval(old_obj.db_labels) if old_obj.db_labels else []
    if isinstance(labels, basestring):
        labels = (labels,)
    else:
        try:
            it = iter(labels)
        except TypeError:
            labels = (labels,)
    new_obj = DBPortSpec.update_version(old_obj, translate_dict)
    total_len = len(sigs)
    if len(defaults) < total_len:
        defaults.extend("" for i in xrange(total_len-len(defaults)))
    if len(labels) < total_len:
        labels.extend("" for i in xrange(total_len-len(labels)))
    for i, (sig, default, label) in enumerate(izip(sigs, defaults, labels)):
        module = None
        package = None
        namespace = ''
        if len(sig) == 1:
            module = sig[0]
        else:
            package = sig[0]
            module = sig[1]
        if len(sig) > 2:
            namespace = sig[2]
        item = DBPortSpecItem(id=id_scope.getNewId(DBPortSpecItem.vtType),
                              pos=i, 
                              module=module, 
                              package=package,
                              namespace=namespace, 
                              label=label, 
                              default=default)
        item.db_values = ''
        item.db_entry_type = ''
        new_obj.db_add_portSpecItem(item)
    return new_obj

def update_portSpecs(old_obj, translate_dict):
    new_port_specs = []
    for port_spec in old_obj.db_portSpecs:
        new_port_specs.append(update_portSpec(port_spec, translate_dict))
    return new_port_specs

def update_portSpec_op(old_obj, translate_dict):
    return update_portSpec(old_obj.db_data, translate_dict)

def createParameterExploration(action_id, xmlString, vistrail):
    if not xmlString:
        return
    # Parse/validate the xml

    try:
        striplen = len("<paramexps>")
        xmlString = xmlString[striplen:-(striplen+1)].strip()
        xmlDoc = parseString(xmlString).documentElement
    except Exception:
        return None
    # we need the pipeline to look up function/paramater id:s
    pipeline = materializeWorkflow(vistrail, action_id)
    # Populate parameter exploration window with stored functions and aliases
    functions = []
    for f in xmlDoc.getElementsByTagName('function'):
        f_id = long(f.attributes['id'].value)
        # we need to convert function id:s to (module_id, port_name)
        module_id = None
        f_name = None
        for m in pipeline.db_modules:
            for _f in m.db_functions:
                if _f.db_id == f_id:
                    module_id = m.db_id
                    f_name = _f.db_name
                    continue
        if not (module_id and f_name):
            break
        parameters = []
        for p in f.getElementsByTagName('param'):
            # we need to convert function id:s to (module_id, port_name)
            p_id = long(p.attributes['id'].value)
            p_pos = None
            for m in pipeline.db_modules:
                for _f in m.db_functions:
                    for _p in _f.db_parameters:
                        if _p.db_id == p_id:
                            p_pos = _p.db_pos
                        continue
            if p_pos is None:
                break
            p_intType = str(p.attributes['interp'].value)
            if p_intType in ['Linear Interpolation']:
                p_min = str(p.attributes['min'].value)
                p_max = str(p.attributes['max'].value)
                value = "[%s, %s]" % (p_min, p_max)
            if p_intType in ['RGB Interpolation', 'HSV Interpolation']:
                p_min = str(p.attributes['min'].value)
                p_max = str(p.attributes['max'].value)
                value = '["%s", "%s"]' % (p_min, p_max)
            elif p_intType == 'List':
                value = str(p.attributes['values'].value)
            elif p_intType == 'User-defined Function':
                # Set function code
                value = str(p.attributes['code'].value)
            param = DBPEParameter(id=vistrail.idScope.getNewId(DBPEParameter.vtType),
                                  pos=p_pos,
                                  interpolator=p_intType,
                                  value=value,
                                  dimension=int(p.attributes['dim'].value))
            parameters.append(param)
        f_is_alias = (str(f.attributes['alias'].value) == 'True')
        function = DBPEFunction(id=vistrail.idScope.getNewId(DBPEFunction.vtType),
                                module_id=module_id,
                                port_name=f_name,
                                is_alias=1 if f_is_alias else 0,
                                parameters=parameters)
        functions.append(function)
    pe = DBParameterExploration(id=vistrail.idScope.getNewId(DBParameterExploration.vtType),
                                action_id=action_id,
                                dims=str(xmlDoc.attributes['dims'].value),
                                layout=str(xmlDoc.attributes['layout'].value),
                                date=str(xmlDoc.attributes['date'].value),
                                functions = functions)
    return pe


def translateVistrail(_vistrail):
    """ Translate old annotation based vistrail variables to new
        DBVistrailVariable class """
    global id_scope

    new_vistrail_vars = []
    new_param_exps = []

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
    
    def update_annotations(old_obj, trans_dict):
        new_annotations = []
        for a in old_obj.db_annotations:
            if a.db_key == '__vistrail_vars__':
                for name, data in dict(literal_eval(a.db_value)).iteritems():
                    uuid, identifier, value = data
                    package, module, namespace = identifier
                    var = DBVistrailVariable(name, uuid, package, module, 
                                             namespace, value)
                    new_vistrail_vars.append(var)
            else:
                new_a = DBAnnotation.update_version(a, trans_dict)
                new_annotations.append(new_a)

        return new_annotations

    def update_actionAnnotations(old_obj, trans_dict):
        new_actionAnnotations = []
        for aa in old_obj.db_actionAnnotations:
            if aa.db_key == '__paramexp__':
                pe = createParameterExploration(aa.db_action_id, aa.db_value, 
                                                vistrail)
                new_param_exps.append(pe)
            else:
                new_aa = DBActionAnnotation.update_version(aa, trans_dict)
                new_actionAnnotations.append(new_aa)
        return new_actionAnnotations

    translate_dict = {'DBModule': {'portSpecs': update_portSpecs},
                      'DBModuleDescriptor': {'portSpecs': update_portSpecs},
                      'DBAction': {'operations': update_operations},
                      'DBGroup': {'workflow': update_workflow},
                      'DBVistrail': {'annotations': update_annotations,
                                     'actionAnnotations': \
                                         update_actionAnnotations}
                      }
    vistrail = DBVistrail()
    id_scope = vistrail.idScope
    vistrail = DBVistrail.update_version(_vistrail, translate_dict, vistrail)
    for v in new_vistrail_vars:
        vistrail.db_add_vistrailVariable(v)
    for pe in new_param_exps:
        vistrail.db_add_parameter_exploration(pe)

    vistrail.db_version = '1.0.3'
    return vistrail

def translateWorkflow(_workflow):
    global id_scope
    def update_workflow(old_obj, translate_dict):
        return DBWorkflow.update_version(old_obj.db_workflow, translate_dict)
    translate_dict = {'DBModule': {'portSpecs': update_portSpecs},
                      'DBGroup': {'workflow': update_workflow}}

    workflow = DBWorkflow()
    id_scope = IdScope(remap={DBAbstraction.vtType: DBModule.vtType, DBGroup.vtType: DBModule.vtType})
    workflow = DBWorkflow.update_version(_workflow, translate_dict, workflow)
    workflow.db_version = '1.0.3'
    return workflow

def translateLog(_log):
    translate_dict = {}
    log = DBLog.update_version(_log, translate_dict)
    log.db_version = '1.0.3'
    return log

def translateRegistry(_registry):
    global id_scope
    translate_dict = {'DBModuleDescriptor': {'portSpecs': update_portSpecs}}
    registry = DBRegistry()
    id_scope = registry.idScope
    registry = DBRegistry.update_version(_registry, translate_dict, registry)
    registry.db_version = '1.0.3'
    return registry

class TestTranslate(unittest.TestCase):
    def testParamexp(self):
        """test translating parameter explorations from 1.0.2 to 1.0.3"""
        from vistrails.db.services.io import open_bundle_from_zip_xml
        from vistrails.core.system import vistrails_root_directory
        import os
        (save_bundle, vt_save_dir) = open_bundle_from_zip_xml(DBVistrail.vtType, \
                        os.path.join(vistrails_root_directory(),
                        'tests/resources/paramexp-1.0.2.vt'))
        vistrail = translateVistrail(save_bundle.vistrail)
        pes = vistrail.db_get_parameter_explorations()
        self.assertEqual(len(pes), 1)
        funs = pes[0].db_functions
        self.assertEqual(set([f.db_port_name for f in funs]),
                         set(['SetCoefficients', 'SetBackgroundWidget']))
        parameters = funs[0].db_parameters
        self.assertEqual(len(parameters), 10)
        
    def testVistrailvars(self):
        """test translating vistrail variables from 1.0.2 to 1.0.3"""
        from vistrails.db.services.io import open_bundle_from_zip_xml
        from vistrails.core.system import vistrails_root_directory
        import os
        (save_bundle, vt_save_dir) = open_bundle_from_zip_xml(DBVistrail.vtType, \
                        os.path.join(vistrails_root_directory(),
                        'tests/resources/visvar-1.0.2.vt'))
        vistrail = translateVistrail(save_bundle.vistrail)
        visvars = vistrail.db_vistrailVariables
        self.assertEqual(len(visvars), 2)
        self.assertNotEqual(visvars[0].db_name, visvars[1].db_name)


if __name__ == '__main__':
    import vistrails.core.application
    vistrails.core.application.init()
    unittest.main()

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

from db.versions.v1_0_3.domain import DBVistrail, DBVistrailVariable, \
                                      DBWorkflow, DBLog, DBRegistry, \
                                      DBAdd, DBChange, DBDelete, \
                                      DBPortSpec, DBPortSpecItem

from itertools import izip

id_scope = None

def update_portSpec(old_obj, translate_dict):
    global id_scope
    sigstring = old_obj.db_sigstring
    sigs = []
    if sigstring != '()':
        for sig in sigstring[1:-1].split(','):
            sigs.append(sig.split(':', 2))
    # not great to use eval...
    defaults = eval(old_obj.db_defaults) if old_obj.db_defaults else []
    if isinstance(defaults, basestring):
        defaults = (defaults,)
    else:
        try:
            it = iter(defaults)
        except TypeError:
            defaults = (defaults,)
    # not great to use eval...
    labels = eval(old_obj.db_labels) if old_obj.db_labels else []
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
        namespace = None
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
                              default=label)
        new_obj.db_add_portSpecItem(item)
    return new_obj

def update_portSpecs(old_obj, translate_dict):
    new_port_specs = []
    for port_spec in old_obj.db_portSpecs:
        new_port_specs.append(update_portSpec(port_spec, translate_dict))
    return new_port_specs

def update_portSpec_op(old_obj, translate_dict):
    return update_portSpec(old_obj.db_data, translate_dict)

def translateVistrail(_vistrail):
    """ Translate old annotation based vistrail variables to new
        DBVistrailVariable class """
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
    
    translate_dict = {'DBModule': {'portSpecs': update_portSpecs},
                      'DBModuleDescriptor': {'portSpecs': update_portSpecs},
                      'DBAction': {'operations': update_operations},
                      'DBGroup': {'workflow': update_workflow},
                      }
    vistrail = DBVistrail()
    id_scope = vistrail.idScope
    vistrail = DBVistrail.update_version(_vistrail, translate_dict, vistrail)
    key = '__vistrail_vars__'
    if vistrail.db_has_annotation_with_key(key):
        s = vistrail.db_get_annotation_by_key(key)
        vistrail.db_delete_annotation(s)
        for name, data in dict(eval(s.db_value)).iteritems():
            uuid, identifier, value = data
            package, module, namespace = identifier
            var = DBVistrailVariable(name, uuid, package, module, namespace, value)
            vistrail.db_add_vistrailVariable(var)

    vistrail.db_version = '1.0.3'
    return vistrail

def translateWorkflow(_workflow):
    global id_scope
    def update_workflow(old_obj, translate_dict):
        return DBWorkflow.update_version(old_obj.db_workflow, translate_dict)
    translate_dict = {'DBModule': {'portSpecs': update_portSpecs},
                      'DBGroup': {'workflow': update_workflow}}

    workflow = DBWorkflow()
    id_scope = workflow.idScope
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

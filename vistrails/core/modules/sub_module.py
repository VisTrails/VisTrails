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

""" Define facilities for setting up SubModule Module in VisTrails """

from itertools import izip
import random
try:
    import hashlib
    sha_hash = hashlib.sha1
except ImportError:
    import sha
    sha_hash = sha.new

from core.modules import module_registry
from core.modules.basic_modules import String, Boolean, Variant, NotCacheable
from core.modules.vistrails_module import Module, InvalidOutput, new_module, \
    ModuleError
from core.utils import ModuleAlreadyExists, DummyView, VistrailsInternalError
import os.path

##############################################################################

class InputPort(Module):
    
    def compute(self):
        exPipe = self.forceGetInputFromPort('ExternalPipe')
        if exPipe:
            self.setResult('InternalPipe', exPipe)
        else:
            self.setResult('InternalPipe', InvalidOutput)

###############################################################################
    
class OutputPort(Module):
    
    def compute(self):
        inPipe = self.getInputFromPort('InternalPipe')
        self.setResult('ExternalPipe', inPipe)
    
###############################################################################

class Group(Module):
    def __init__(self):
        Module.__init__(self)

    def compute(self):
        if not hasattr(self, 'pipeline') or self.pipeline is None:
            raise VistrailsInternalError("%s cannot execute--" % \
                                             self.__class__.__name__ + \
                                         "pipeline doesn't exist")
        elif not hasattr(self, 'input_remap') or self.input_remap is None or \
                not hasattr(self, 'output_remap') or self.output_remap is None:
            raise VistrailsInternalError("%s cannot execute--" % \
                                             self.__class__.__name__ + \
                                         "remap dictionaries don't exist")
            
        res = self.interpreter.setup_pipeline(self.pipeline)
        if len(res[5]) > 0:
            raise ModuleError(self, 'Error(s) inside group:\n' +
                              '\n'.join(me.msg for me in res[5].itervalues()))
        tmp_id_to_module_map = res[0]
        for iport_name, conn in self.inputPorts.iteritems():
            iport_module = self.input_remap[iport_name]
            iport_obj = tmp_id_to_module_map[iport_module.id]
            iport_obj.set_input_port('ExternalPipe', conn[0])
        
        kwargs = {'logger': self.logging.log, 'clean_pipeline': True}
        module_info_args = set(['locator', 'reason', 'extra_info', 'actions'])
        for arg in module_info_args:
            if arg in self.moduleInfo:
                kwargs[arg] = self.moduleInfo[arg]

#         if hasattr(self, 'group_exec'):
#             kwargs['parent_exec'] = self.group_exec

        res = self.interpreter.execute_pipeline(self.pipeline, *(res[:2]), 
                                                **kwargs)
        if len(res[2]) > 0:
            raise ModuleError(self, 'Error(s) inside group:\n' +
                              '\n '.join(me.module.__class__.__name__ + ': ' + \
                                            me.msg for me in res[2].itervalues()))
            
        for oport_name, oport_module in self.output_remap.iteritems():
            if oport_name is not 'self':
                # oport_module = self.output_remap[oport_name]
                oport_obj = tmp_id_to_module_map[oport_module.id]
                self.setResult(oport_name, oport_obj.get_output('ExternalPipe'))
        self.interpreter.finalize_pipeline(self.pipeline, *res[:-1],
                                           **{'reset_computed': False})

    def is_cacheable(self):
        for module in self.pipeline.modules.itervalues():
            if not module.summon().is_cacheable():
                return False
        return True

###############################################################################

def coalesce_port_specs(neighbors, type):
    from core.modules.basic_modules import identifier as basic_pkg
    reg = module_registry.get_module_registry()
    cur_descs = None
    if type == 'input':
        find_common = reg.find_descriptor_subclass
        common_desc = reg.get_descriptor_by_name(basic_pkg, 'Variant')
    elif type == 'output':
        find_common = reg.find_descriptor_superclass
        common_desc = reg.get_descriptor_by_name(basic_pkg, 'Module')
    else:
        raise VistrailsInternalError("Cannot understand type '%s'" % type)

    for (module, port_name) in neighbors:
        if cur_descs is None:
            port_spec = module.get_port_spec(port_name, type)
            cur_descs = port_spec.descriptors()
        else:
            next_port_spec = module.get_port_spec(port_name, type)
            next_descs = next_port_spec.descriptors()
            if len(cur_descs) != len(next_descs):
                raise VistrailsInternalError("Cannot have single port "
                                             "connect to incompatible "
                                             "types")
            descs = []
            for cur_desc, next_desc in izip(cur_descs, next_descs):
                new_desc = find_common(cur_desc, next_desc)
                if new_desc is None:
                    new_desc = common_desc
                descs.append(new_desc)
            cur_descs = descs
    if cur_descs:
        sigstring = '(' + ','.join(d.sigstring for d in cur_descs) + ')'
    else:
        sigstring = None
    return sigstring

def get_port_spec_info(pipeline, module):
    type_map = {'OutputPort': 'output', 'InputPort': 'input'}
    try:
        type = type_map[module.name]
    except KeyError:
        raise VistrailsInternalError("cannot translate type '%s'" % type)
    if type == 'input':
        get_edges = pipeline.graph.edges_from
        get_port_name = \
            lambda x: pipeline.connections[x].destination.name
    elif type == 'output':
        get_edges = pipeline.graph.edges_to
        get_port_name = \
            lambda x: pipeline.connections[x].source.name
    # conns = get_edges(module.id)
#     for i, m in pipeline.modules.iteritems():
#         print i, m.name
#     for j, c in pipeline.connections.iteritems():
#         print j, c.source.moduleId, c.destination.moduleId

    neighbors = [(pipeline.modules[m_id], get_port_name(c_id))
                 for (m_id, c_id) in get_edges(module.id)]
    port_name = neighbors[0][1]
    sigstring = coalesce_port_specs(neighbors, type)
    old_name = port_name
    # sigstring = neighbor.get_port_spec(port_name, type).sigstring

    # FIXME check old registry here?
    port_optional = False
    for function in module.functions:
        if function.name == 'name':
            port_name = function.params[0].strValue
        if function.name == 'optional':
            port_optional = function.params[0].strValue == 'True'
#     print 'psi:', port_name, old_name, sigstring
    return (port_name, sigstring, port_optional, neighbors)

###############################################################################

class Abstraction(Group):
    def __init__(self):
        Group.__init__(self)

    # the compute method is inherited from Group!

def read_vistrail(vt_fname):
    import db.services.io
    from core.vistrail.vistrail import Vistrail
    vistrail = db.services.io.open_vistrail_from_xml(vt_fname)
    Vistrail.convert(vistrail)
    return vistrail

def new_abstraction(name, vistrail, vt_fname=None, internal_version=-1L,
                    pipeline=None):
    """make_abstraction(name: str, 
                        vistrail: (str or Vistrail), 
                        registry: ModuleRegistry,
                        vt_fname: str,
                        internal_version: long,
                        pipeline: Pipeline) -> type

    Creates a new VisTrails module that is a subclass of Abstraction
    according to the vistrail file provided and the version.  The version
    can either be a tag (string) or an id (long)
    """

    if type(vistrail) == type(""):
        vt_fname = vistrail
        vistrail = read_vistrail(vistrail)
    elif vt_fname is None:
        raise VistrailsInternalError("Abstraction must provide "
                                     "vt_fname with vistrail")
    
    if internal_version == -1L:
        internal_version = vistrail.get_latest_version()
    action = vistrail.actionMap[internal_version]
    if pipeline is None:
        pipeline = vistrail.getPipeline(internal_version)
        # try to make the subworkflow work with the package versions we have
        pipeline.validate()
    uuid = vistrail.get_annotation('__abstraction_uuid__').value

    if vistrail.has_notes(action.id):
        docstring = vistrail.get_notes(action.id)
    else:
        docstring = None

    d = {}
    input_modules = []
    output_modules = []
    for module in pipeline.module_list:
        #FIXME make this compare more robust
        if module.name == 'InputPort' and \
                module.package == 'edu.utah.sci.vistrails.basic':
            input_modules.append(module)
        elif module.name == 'OutputPort' and \
                module.package == 'edu.utah.sci.vistrails.basic':
            output_modules.append(module)
    input_ports = []
    output_ports = []
    input_remap = {}
    output_remap = {}
    for module in input_modules:
        (port_name, sigstring, optional, _) = \
            get_port_spec_info(pipeline, module)
        input_ports.append((port_name, sigstring, optional))
        input_remap[port_name] = module
    for module in output_modules:
        (port_name, sigstring, optional, _) = \
            get_port_spec_info(pipeline, module)
        output_ports.append((port_name, sigstring, optional))
        output_remap[port_name] = module

    # necessary for group
    d['_input_ports'] = input_ports
    d['_output_ports'] = output_ports
    d['input_remap'] = input_remap
    d['output_remap'] = output_remap
    d['pipeline'] = pipeline

    # abstraction specific
    d['vt_fname'] = vt_fname
    d['vistrail'] = vistrail
    d['internal_version'] = internal_version
    d['uuid'] = uuid

    # print "input_ports", d['_input_ports']
    # print "output_ports", d['_output_ports']
    return new_module(Abstraction, name, d, docstring)

def get_abstraction_dependencies(vistrail, internal_version=-1L):
    if type(vistrail) == type(""):
        vistrail = read_vistrail(vistrail)
    if internal_version == -1L:
        internal_version = vistrail.get_latest_version()
    # action = vistrail.actionMap[internal_version]
    pipeline = vistrail.getPipeline(internal_version)
    
    packages = {}
    for module in pipeline.module_list:
        if module.package not in packages:
            packages[module.package] = set()
        packages[module.package].add(module.descriptor_info)
    return packages

def find_internal_abstraction_refs(pkg, vistrail, internal_version=-1L):
    if type(vistrail) == type(""):
        vistrail = read_vistrail(os.path.join(pkg.package_dir, vistrail))
    if internal_version == -1L:
        internal_version = vistrail.get_latest_version()
    pipeline = vistrail.getPipeline(internal_version)
    abstractions = []
    for m in pipeline.module_list:
        if m.vtType == 'abstraction' and m.package == pkg.identifier:
            abstractions.append((m.name, m.namespace))
    return abstractions

###############################################################################

def initialize(*args, **kwargs):
    # These are all from sub_module.py!
    reg = module_registry.get_module_registry()

    def random_signature(pipeline, obj, chm):
        hasher = sha_hash()
        hasher.update(str(random.random()))
        return hasher.digest()

    reg.add_module(InputPort, signatureCallable=random_signature)
    reg.add_input_port(InputPort, "name", String, True)
    reg.add_input_port(InputPort, "optional", Boolean, True)
    reg.add_input_port(InputPort, "spec", String)
    reg.add_input_port(InputPort, "ExternalPipe", Variant, True)
    reg.add_output_port(InputPort, "InternalPipe", Variant)

    reg.add_module(OutputPort)
    reg.add_input_port(OutputPort, "name", String, True)
    reg.add_input_port(OutputPort, "optional", Boolean, True)
    reg.add_input_port(OutputPort, "spec", String)
    reg.add_input_port(OutputPort, "InternalPipe", Variant)
    reg.add_output_port(OutputPort, "ExternalPipe", Variant, True)

    reg.add_module(Group)
    reg.add_output_port(Group, "self", Group, True)

    reg.add_module(Abstraction, name="SubWorkflow")

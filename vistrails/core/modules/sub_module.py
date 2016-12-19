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

""" Define facilities for setting up SubModule Module in VisTrails """
from __future__ import division

from itertools import izip
import random
import uuid

from vistrails.core.cache.hasher import Hasher
from vistrails.core.cache.utils import hash_list
from vistrails.core.modules import module_registry
from vistrails.core.modules.basic_modules import identifier as basic_pkg
from vistrails.core.modules.config import ModuleSettings, IPort, OPort
from vistrails.core.modules.vistrails_module import Module, InvalidOutput, new_module, \
    ModuleError, ModuleSuspended, ModuleConnector
from vistrails.core.utils import VistrailsInternalError
import os.path

try:
    import hashlib
    sha_hash = hashlib.sha1
except ImportError:
    import sha
    sha_hash = sha.new

##############################################################################

def random_signature(pipeline, obj, chm):
    hasher = sha_hash()
    hasher.update(str(random.random()))
    return hasher.digest()

def input_port_signature(pipeline, obj, chm):
    if hasattr(obj, '_input_port_signature') and \
            obj._input_port_signature is not None:
        return obj._input_port_signature
    return random_signature(pipeline, obj, chm)

class InputPort(Module):
    _settings = ModuleSettings(signature=input_port_signature)
    _input_ports = [IPort("name", "String", optional=True),
                    IPort("optional", "Boolean", optional=True),
                    IPort("spec", "String"),
                    IPort("ExternalPipe", "Variant", optional=True),
                    IPort("Default", "Variant")]
    _output_ports = [OPort("InternalPipe", "Variant")]
                    
    def compute(self):
        exPipe = self.force_get_input('ExternalPipe')
        if exPipe is not None:
            self.set_output('InternalPipe', exPipe)
        else:
            if self.has_input('Default'):
                self.set_output('InternalPipe',
                               self.get_input('Default'))
            else:
                self.set_output('InternalPipe', InvalidOutput)

###############################################################################
    
class OutputPort(Module):
    _input_ports = [IPort("name", "String", optional=True),
                    IPort("optional", "Boolean", optional=True),
                    IPort("spec", "String"),
                    IPort("InternalPipe", "Variant")]
    _output_ports = [OPort("ExternalPipe", "Variant", optional=True)]
    
    def compute(self):
        inPipe = self.get_input('InternalPipe')
        self.set_output('ExternalPipe', inPipe)
    
###############################################################################

def group_signature(pipeline, module, chm):
    if module._port_specs is None:
        module.make_port_specs()
    input_conns = {}
    input_functions = {}
    for from_module, c_id in pipeline.graph.edges_to(module.id):
        conn = pipeline.connections[c_id]
        if conn.destination.name not in input_conns:
            input_conns[conn.destination.name] = []
        input_conns[conn.destination.name].append((from_module, conn))
    for function in module.functions:
        if function.name not in input_functions:
            input_functions[function.name] = []
        input_functions[function.name].append(function)
    covered_modules = dict((k, False) for k in module._input_remap)
    for input_port_name, conn_list in input_conns.iteritems():
        covered_modules[input_port_name] = True
        input_module = module._input_remap[input_port_name]
        upstream_sigs = [(pipeline.subpipeline_signature(m) +
                          Hasher.connection_signature(c))
                         for (m, c) in conn_list]
        module_sig = Hasher.module_signature(input_module, chm)
        sig = Hasher.subpipeline_signature(module_sig, upstream_sigs)
        if input_port_name in input_functions:
            function_sig = hash_list(input_functions[input_port_name], 
                                     Hasher.function_signature, chm)
            sig = Hasher.compound_signature([sig, function_sig])
        input_module._input_port_signature = sig
    for input_port_name, done in covered_modules.iteritems():
        if done:
            continue
        covered_modules[input_port_name] = True
        input_module = module._input_remap[input_port_name]
        if input_port_name in input_functions:
            module_sig = Hasher.module_signature(input_module, chm)
            function_sig = hash_list(input_functions[input_port_name], 
                                     Hasher.function_signature, chm)
            sig = Hasher.compound_signature([module_sig, function_sig])
        else:
            sig = Hasher.module_signature(input_module, chm)
        input_module._input_port_signature = sig

    module.pipeline.refresh_signatures()

    sig_list = []
    sig_list.append(Hasher.module_signature(module, chm))
    for m_id in module.pipeline.graph.sinks():
        sig_list.append(module.pipeline.subpipeline_signature(m_id))
    return Hasher.compound_signature(sig_list)

class Group(Module):
    _settings = ModuleSettings(signature=group_signature,
                               hide_descriptor=True)
    _output_ports = [OPort("self", "Group", optional=True)]

    def __init__(self):
        Module.__init__(self)
        self.is_group = True
        self.persistent_modules = []

    def compute(self):
        # Check required attributes
        if not hasattr(self, 'pipeline') or self.pipeline is None:
            raise VistrailsInternalError(
                    "%s cannot execute -- pipeline doesn't exist" %
                    self.__class__.__name__)
        elif (not hasattr(self, 'output_remap') or self.output_remap is None or
                not hasattr(self, 'input_remap') or self.input_remap is None):
            raise VistrailsInternalError(
                    "%s cannot execute -- remap dictionaries don't exist" %
                    self.__class__.__name__)

        # Setup pipeline for execution
        res = self.interpreter.setup_pipeline(self.pipeline)
        self.persistent_modules = res[0].values()
        if len(res[5]) > 0:
            raise ModuleError(self, "Error(s) inside group:\n" +
                              "\n".join(me.msg for me in res[5].itervalues()))
        tmp_id_to_module_map = res[0]

        # Connect Group's external input ports to internal InputPort modules
        for iport_name, conn in self.inputPorts.iteritems():
            from vistrails.core.modules.basic_modules import create_constant
            # The type information is lost when passing as Variant,
            # so we need to use the the final normalized value
            value = self.get_input(iport_name)
            temp_conn = ModuleConnector(create_constant(value),
                                        'value', self.input_specs[iport_name])
            iport_module = self.input_remap[iport_name]
            iport_obj = tmp_id_to_module_map[iport_module.id]
            iport_obj.set_input_port('ExternalPipe', temp_conn)

        # Execute pipeline
        kwargs = {'logger': self.logging.log.recursing(self),
                  'clean_pipeline': True,
                  'current_version': self.moduleInfo['version']}
        module_info_args = set(['locator', 'reason', 'extra_info', 'actions', 'job_monitor'])
        for arg in module_info_args:
            if arg in self.moduleInfo:
                kwargs[arg] = self.moduleInfo[arg]

        res = self.interpreter.execute_pipeline(self.pipeline,
                                                *res[:2],
                                                **kwargs)

        # Check and propagate errors
        if len(res[2]) > 0:
            raise ModuleError(self, "Error(s) inside group:\n" +
                              "\n".join("%s: %s" % (
                                      me.module.__class__.__name__, me.msg)
                              for me in res[2].itervalues()))

        # Check and propagate ModuleSuspended exceptions
        if res[4]:
            message = "\n".join([ms.msg for ms in res[4].itervalues()])
            children = list(res[4].values())
            raise ModuleSuspended(self, message, children=children)

        # Connect internal OutputPort modules to Group's external output ports
        for oport_name, oport_module in self.output_remap.iteritems():
            if oport_name is not 'self':
                oport_obj = tmp_id_to_module_map[oport_module.id]
                self.set_output(oport_name,
                                oport_obj.get_output('ExternalPipe'))

        self.interpreter.finalize_pipeline(self.pipeline, *res[:-1],
                                           reset_computed=False)

    def is_cacheable(self):
        return all(m.is_cacheable() for m in self.persistent_modules)

    def transfer_attrs(self, module):
        self.pipeline = module.pipeline
        if module._port_specs is None:
            module.make_port_specs()
        self.input_remap = module._input_remap
        self.output_remap = module._output_remap
        Module.transfer_attrs(self, module)

###############################################################################

def coalesce_port_specs(neighbors, type):
    reg = module_registry.get_module_registry()
    cur_descs = None
    cur_depth = 0
    Variant_desc = reg.get_descriptor_by_name(basic_pkg, 'Variant')
    if type == 'input':
        find_common = reg.find_descriptor_subclass
        common_desc = Variant_desc
    elif type == 'output':
        find_common = reg.find_descriptor_superclass
        common_desc = reg.get_descriptor_by_name(basic_pkg, 'Module')
    else:
        raise VistrailsInternalError("Cannot understand type '%s'" % type)

    for (module, port_name) in neighbors:
        if cur_descs is None:
            port_spec = module.get_port_spec(port_name, type)
            cur_descs = port_spec.descriptors()
            cur_depth = port_spec.depth
        else:
            next_port_spec = module.get_port_spec(port_name, type)
            next_descs = next_port_spec.descriptors()
            next_depth = next_port_spec.depth
            if len(cur_descs) != len(next_descs):
                raise VistrailsInternalError("Cannot have single port "
                                             "connect to incompatible "
                                             "types")
            if 'input' == type and cur_depth > next_depth:
                # use least depth
                cur_depth = next_depth
                cur_descs = next_descs
            if 'output' == type and cur_depth < next_depth:
                # use least depth
                cur_depth = next_depth
                cur_descs = next_descs
            descs = []
            for cur_desc, next_desc in izip(cur_descs, next_descs):
                if cur_desc is Variant_desc:
                    new_desc = next_desc
                elif next_desc is Variant_desc:
                    new_desc = cur_desc
                else:
                    new_desc = find_common(cur_desc, next_desc)
                if new_desc is None:
                    new_desc = common_desc
                descs.append(new_desc)
            cur_descs = descs
            
    if cur_descs:
        sigstring = '(' + ','.join(d.sigstring for d in cur_descs) + ')'
    else:
        sigstring = None
    return (sigstring, cur_depth)

def get_port_spec_info(pipeline, module):
    type_map = {'OutputPort': 'output', 'InputPort': 'input'}
    try:
        type = type_map[module.name]
    except KeyError:
        raise VistrailsInternalError("cannot translate type '%s'" % module.name)
    if type == 'input':
        get_edges = pipeline.graph.edges_from
        get_port_name = \
            lambda x: pipeline.connections[x].destination.name
    else:  # type == 'output'
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
    sigstring, depth = coalesce_port_specs(neighbors, type)
    # sigstring = neighbor.get_port_spec(port_name, type).sigstring

    # FIXME check old registry here?
    port_optional = False
    for function in module.functions:
        if function.name == 'name':
            port_name = function.params[0].strValue
        if function.name == 'optional':
            port_optional = function.params[0].strValue == 'True'
#     print 'psi:', port_name, old_name, sigstring
    return (port_name, sigstring, port_optional, depth, neighbors)

###############################################################################

class Abstraction(Group):
    # We need Abstraction to be a subclass of Group so that the hierarchy of
    # modules is right
    # But the pipeline comes from somewhere else, so skip the transfer_attrs()
    _settings = ModuleSettings(name="SubWorkflow",
                               hide_descriptor=True)

    def transfer_attrs(self, module):
        Module.transfer_attrs(self, module)

    # the compute method is inherited from Group!

def read_vistrail(vt_fname):
    import vistrails.db.services.io
    from vistrails.core.vistrail.vistrail import Vistrail
    vistrail = vistrails.db.services.io.open_vistrail_from_xml(vt_fname)
    Vistrail.convert(vistrail)
    return vistrail

def read_vistrail_from_db(db_connection, abs_id, version):
    import vistrails.db.services.io
    from vistrails.core.vistrail.vistrail import Vistrail
    vistrail = vistrails.db.services.io.open_vistrail_from_db(db_connection, abs_id, version)
    Vistrail.convert(vistrail)
    return vistrail

def get_abs_namespace_info(vistrail):
    annotation_add = None
    annotation_key = '__abstraction_uuid__'
    namespaces = []
    while vistrail.get_annotation(annotation_key) is not None:
        namespaces.append(vistrail.get_annotation(annotation_key).value)
        if annotation_add is None:
            annotation_add = 2
        else:
            annotation_add += 1
        annotation_key = '__abstraction_uuid_%d__' % annotation_add
    return namespaces, annotation_add

def get_all_abs_namespaces(vistrail):
    return get_abs_namespace_info(vistrail)[0]

def get_cur_abs_namespace(vistrail):
    all_namespaces = get_abs_namespace_info(vistrail)[0]
    if len(all_namespaces) > 0:
        return all_namespaces[-1]
    return None

def get_next_abs_annotation_key(vistrail):
    annotation_add = get_abs_namespace_info(vistrail)[1]
    if annotation_add is None:
        return "__abstraction_uuid__"
    return "__abstraction_uuid_%d__" % annotation_add

def get_cur_abs_annotation_key(vistrail):
    annotation_add = get_abs_namespace_info(vistrail)[1]
    if annotation_add is None:
        return None
    elif annotation_add == 2:
        return '__abstraction_uuid__'
    return '__abstraction_uuid_%d__' % (annotation_add - 1)
    
def save_abstraction(vistrail, fname):
    from vistrails.core.db.io import save_vistrail_to_xml

    # check if vistrail is changed before calling this!
    new_namespace = str(uuid.uuid1())
    annotation_key = get_next_abs_annotation_key(vistrail)
    vistrail.set_annotation(annotation_key, new_namespace)
    save_vistrail_to_xml(vistrail, fname)

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

    if isinstance(vistrail, basestring):
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
    uuid = get_cur_abs_namespace(vistrail)

    if vistrail.has_notes(action.id):
        docstring = vistrail.get_notes(action.id)
    else:
        docstring = None

    d = {}
    input_modules = []
    output_modules = []
    for module in pipeline.module_list:
        #FIXME make this compare more robust
        if module.name == 'InputPort' and module.package == basic_pkg:
            input_modules.append(module)
        elif module.name == 'OutputPort' and module.package == basic_pkg:
            output_modules.append(module)
    input_ports = []
    output_ports = []
    input_remap = {}
    output_remap = {}
    for module in input_modules:
        (port_name, sigstring, optional, depth, _) = \
            get_port_spec_info(pipeline, module)
        input_ports.append((port_name, sigstring, optional, depth))
        input_remap[port_name] = module
    for module in output_modules:
        (port_name, sigstring, optional, depth, _) = \
            get_port_spec_info(pipeline, module)
        output_ports.append((port_name, sigstring, optional, depth))
        output_remap[port_name] = module

    # necessary for group
    d['_input_ports'] = [IPort(*p[:3], depth=p[3]) for p in input_ports] 
    d['_output_ports'] = [OPort(*p[:3], depth=p[3]) for p in output_ports] 
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
    if isinstance(vistrail, basestring):
        vistrail = read_vistrail(vistrail)
    if internal_version == -1L:
        internal_version = vistrail.get_latest_version()
    pipeline = vistrail.getPipeline(internal_version)

    packages = {}
    def pipeline_deps(pipeline):
        for module in pipeline.module_list:
            if module.is_group():
                pipeline_deps(module.pipeline)
                continue
            if module.package not in packages:
                packages[module.package] = set()
            packages[module.package].add(module.descriptor_info)
    pipeline_deps(pipeline)
    return packages

def find_internal_abstraction_refs(pkg, vistrail, internal_version=-1L):
    if isinstance(vistrail, basestring):
        vistrail = read_vistrail(os.path.join(pkg.package_dir, vistrail))
    if internal_version == -1L:
        internal_version = vistrail.get_latest_version()
    pipeline = vistrail.getPipeline(internal_version)
    abstractions = []
    for m in pipeline.module_list:
        if m.vtType == 'abstraction' and m.package == pkg.identifier:
            abstractions.append((m.name, m.namespace))
    return abstractions

def parse_abstraction_name(filename, get_all_parts=False):
    # assume only 1 possible prefix or suffix
    import re
    prefixes = ["abstraction_"]
    suffixes = [".vt", ".xml"]
    path, fname = os.path.split(filename)
    hexpat = '[a-fA-F0-9]'
    uuidpat = hexpat + '{8}-' + hexpat + '{4}-' + hexpat + '{4}-' + hexpat + '{4}-' + hexpat + '{12}'
    prepat = '|'.join(prefixes).replace('.','\\.')
    sufpat = '|'.join(suffixes).replace('.','\\.')
    pattern = re.compile("(" + prepat + ")?(.+?)(\(" + uuidpat + "\))?(" + sufpat + ")", re.DOTALL | re.IGNORECASE)
    matchobj = pattern.match(fname)
    prefix, absname, uuid, suffix = [matchobj.group(x) or '' for x in xrange(1,5)]
    if get_all_parts:
        return (path, prefix, absname, uuid[1:-1], suffix)
    return absname


###############################################################################

_modules = [InputPort, OutputPort, Group, Abstraction]

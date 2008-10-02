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

""" Define facilities for setting up SubModule Module in VisTrails """

from itertools import izip

from core.modules import module_registry
from core.modules.basic_modules import String, Variant, NotCacheable
from core.modules.vistrails_module import Module, InvalidOutput, new_module
from core.interpreter.default import noncached_interpreter
from core.inspector import PipelineInspector
from core.utils import ModuleAlreadyExists, DummyView, VistrailsInternalError
import os.path

_reg = module_registry.registry

class InputPort(Module):
    
    def compute(self):
        exPipe = self.forceGetInputFromPort('ExternalPipe')
        if exPipe:
            self.setResult('InternalPipe', exPipe)
        else:
            self.setResult('InternalPipe', InvalidOutput)
            
_reg.add_module(InputPort)
_reg.add_input_port(InputPort, "name", String, True)
_reg.add_input_port(InputPort, "spec", String, True)
_reg.add_input_port(InputPort, "old_name", String, True)
_reg.add_input_port(InputPort, "ExternalPipe", Module, True)
_reg.add_output_port(InputPort, "InternalPipe", Variant)

##############################################################################
    
class OutputPort(Module):
    
    def compute(self):
        inPipe = self.getInputFromPort('InternalPipe')
        self.setResult('ExternalPipe', inPipe)
    
_reg.add_module(OutputPort)
_reg.add_input_port(OutputPort, "name", String, True)
_reg.add_input_port(OutputPort, "spec", String, True)
_reg.add_input_port(OutputPort, "InternalPipe", Module)
_reg.add_output_port(OutputPort, "ExternalPipe", Variant, True)

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
        tmp_id_to_module_map = res[0]
        for iport_name, conn in self.inputPorts.iteritems():
            iport_module = self.input_remap[iport_name]
            iport_obj = tmp_id_to_module_map[iport_module.id]
            iport_obj.set_input_port('ExternalPipe', conn[0])
        kwargs = {'clean_pipeline': True}
        res = self.interpreter.execute_pipeline(self.pipeline, *(res[:2]), 
                                                **kwargs)
        for oport_name in self.outputPorts:
            if oport_name is not 'self':
                oport_module = self.output_remap[oport_name]
                oport_obj = tmp_id_to_module_map[oport_module.id]
                self.setResult(oport_name, oport_obj.get_output('ExternalPipe'))
        self.interpreter.finalize_pipeline(self.pipeline, *res[:-1])

_reg.add_module(Group)

###############################################################################

class Abstraction(Group):
    def __init__(self):
        Group.__init__(self)

    # the compute method is inherited from Group!

_reg.add_module(Abstraction)

def read_vistrail(vt_fname):
    import db.services.io
    from core.vistrail.vistrail import Vistrail
    vistrail = db.services.io.open_vistrail_from_xml(vt_fname)
    Vistrail.convert(vistrail)
    return vistrail

def new_abstraction(name, vistrail, registry, vt_fname=None,
                    internal_version=-1L):
    """make_abstraction(name: str, 
                        vistrail: (str or Vistrail), 
                        registry: ModuleRegistry,
                        vt_fname: str,
                        internal_version: long) -> type

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
    pipeline = vistrail.getPipeline(internal_version)
    uuid = vistrail.get_annotation('__abstraction_uuid__').value

    if action.notes is not None:
        docstring = action.notes
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
        for function in module.functions:
            if function.name == 'name':
                port_name = function.parameters[0].strValue
            elif function.name == 'spec':
                port_spec = function.parameters[0].strValue
            elif function.name == 'old_name':
                port_old_name = function.parameters[0].strValue
        signature = []
        portSpecs = port_spec[1:-1].split(',')
        for s in portSpecs:
            spec = s.split(':', 2)
            try:
                descriptor = registry.get_descriptor_by_name(*spec)
                signature.append(descriptor.module)
            except registry.MissingModulePackage, e:
                return (None, -1)
        input_ports.append((port_name, signature))
        input_remap[port_name] = module
    for module in output_modules:
        for function in module.functions:
            if function.name == 'name':
                port_name = function.parameters[0].strValue
            elif function.name == 'spec':
                port_spec = function.parameters[0].strValue
        signature = []
        portSpecs = port_spec[1:-1].split(',')
        for s in portSpecs:
            spec = s.split(':', 2)
            try:
                descriptor = registry.get_descriptor_by_name(*spec)
                signature.append(descriptor.module)
            except registry.MissingModulePackage, e:
                return (None, -1)
        output_ports.append((port_name, signature))
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

    return new_module(Abstraction, name, d, docstring)

def get_abstraction_dependencies(vistrail, internal_version=-1L):
    if type(vistrail) == type(""):
        vistrail = read_vistrail(vt_fname)
    if internal_version == -1L:
        internal_version = vistrail.get_latest_version()
    # action = vistrail.actionMap[internal_version]
    pipeline = vistrail.getPipeline(internal_version)
    
    packages = set()
    for module in pipeline.module_list:
        packages.add(module.package)
    return packages

    
# class SubModule(NotCacheable, Module):
#     """
#     SubModule is the base class of all SubModule class. Inherited
#     classes should change vistrail locator and version number refering
#     to the sub pipeline it represents
    
#     """
#     # Vistrail object where this sub module is from
#     Vistrail = None
    
#     # XML File containing the Vistrail
#     VistrailLocator = None

#     # Version number, within the locator, that represents the pipeline
#     VersionNumber = 0

#     def __init__(self):
#         """ SubModule() -> SubModule
#         Create an inspector for pipeline
        
#         """
#         NotCacheable.__init__(self)
#         Module.__init__(self)
#         self.inspector = PipelineInspector()

#     def compute(self):
#         """ compute() -> None
#         Connects the sub-pipeline to the rest of the module
#         """
#         pipeline = self.Vistrail.getPipeline(self.VersionNumber)
#         interpreter = noncached_interpreter.get()
#         interpreter.set_done_summon_hook(self.glueInputPorts)
#         interpreter.set_done_update_hook(self.glueOutputPorts)        
#         interpreter.execute(None,
#                             pipeline,
#                             '<<SUBMODULE>>',
#                             None,
#                             useLock=False)
#         interpreter.set_done_summon_hook(None)
#         interpreter.set_done_update_hook(None)

#     def glueInputPorts(self, pipeline, objects):
#         """ glueInputPorts(pipeline: Pipeline, objects: [object]) -> None
#         Added additional input port to sub module
        
#         """
#         # Make sure we the sub modules interpreter point to the
#         # sub_module interpreter for file pool
#         for obj in objects.itervalues():
#             obj.interpreter = self.interpreter
        
#         self.inspector.inspect_input_output_ports(pipeline)
#         for iport, conn in self.inputPorts.iteritems():
#             inputPortId = self.inspector.input_port_by_name[iport]
#             inputPortModule = objects[inputPortId]
#             inputPortModule.set_input_port('ExternalPipe', conn[0])
        
#     def glueOutputPorts(self, pipeline, objects):
#         """ glueOutputPorts(pipeline: Pipeline, objects: [object]) -> None
#         Added additional output port to sub module
        
#         """
#         self.inspector.inspect_input_output_ports(pipeline)
#         for oport in self.outputPorts.keys():
#             if self.inspector.output_port_by_name.has_key(oport):
#                 outputPortId = self.inspector.output_port_by_name[oport]
#                 outputPortModule = objects[outputPortId]
#                 self.setResult(oport,
#                                outputPortModule.get_output('ExternalPipe'))
        
# _reg.add_module(SubModule)

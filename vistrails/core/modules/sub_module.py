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

from core.modules import module_registry
from core.modules.basic_modules import String, Variant, NotCacheable
from core.modules.vistrails_module import Module, InvalidOutput
from core.interpreter.default import (noncached_interpreter, 
                                      default_interpreter)
from core.inspector import PipelineInspector
from core.utils import ModuleAlreadyExists, DummyView
import os.path

_reg = module_registry.registry

class DupplicateSubModule(Exception):
    """DupplicateSubModule is raised when trying to add the same
    sub-module to the module registry."""

    def __init__(self, moduleName):
        self.moduleName = moduleName

    def __str__(self):
        return ("'%s' is already registered with VisTrails." % self.moduleName)

##############################################################################

def addSubModule(moduleName, packageName, vistrail,
                 fileName, version, inspector):
    """ addSubModule(moduleName: str,
        packageName: str,
        vistrail: Vistrail,
        fileName: str,
        version: int,
        inspector: PipelineInspector) -> SubModule
    Add a module containing a sub-pipeline given a package name
    and vistrail information
    
    """
    if _reg.hasModule(moduleName):
        currentDesc = _reg.getDescriptorByName(moduleName)
        if issubclass(currentDesc.module, SubModule):
            # Need a way to check VistrailLocator. Just check package for now
            if (packageName==_reg.modulePackage[moduleName] and
                currentDesc.module.VersionNumber==version):
                raise DupplicateSubModule(moduleName)
        raise ModuleAlreadyExists(moduleName)
    NewSubModuleInfo = {'Vistrail': vistrail,
                        'VistrailLocator': fileName,
                        'VersionNumber': version}
    NewSubModule = type('%s_%d_%s' % (packageName, version, moduleName),
                        (SubModule, ),
                        NewSubModuleInfo)
    module_registry.registry.setCurrentPackageName(packageName)
    module_registry.registry.addModule(NewSubModule, moduleName)
    for (name, spec) in inspector.inputPorts.itervalues():
        module_registry.registry.addInputPort(NewSubModule,
                                              name, spec)
    for (name, spec) in inspector.outputPorts.itervalues():
        module_registry.registry.addOutputPort(NewSubModule,
                                               name, spec)
    module_registry.registry.setCurrentPackageName(None)
    return NewSubModule

##############################################################################

class InputPort(Module):
    
    def compute(self):
        exPipe = self.forceGetInputFromPort('ExternalPipe')
        if exPipe:
            self.setResult('InternalPipe', exPipe)
        else:
            self.setResult('InternalPipe', InvalidOutput)
            
_reg.addModule(InputPort)
_reg.addInputPort(InputPort, "name", String, True)
_reg.addInputPort(InputPort, "ExternalPipe", Module, True)
_reg.addOutputPort(InputPort, "InternalPipe", Variant)

##############################################################################
    
class OutputPort(Module):
    
    def compute(self):
        inPipe = self.getInputFromPort('InternalPipe')
        self.setResult('ExternalPipe', inPipe)
    
_reg.addModule(OutputPort)
_reg.addInputPort(OutputPort, "name", String, True)
_reg.addInputPort(OutputPort, "InternalPipe", Module)
_reg.addOutputPort(OutputPort, "ExternalPipe", Variant, True)

###############################################################################

class SubModule(NotCacheable, Module):
    """
    SubModule is the base class of all SubModule class. Inherited
    classes should change vistrail locator and version number refering
    to the sub pipeline it represents
    
    """
    # Vistrail object where this sub module is from
    Vistrail = None
    
    # XML File containing the Vistrail
    VistrailLocator = None

    # Version number, within the locator, that represents the pipeline
    VersionNumber = 0

    def __init__(self):
        """ SubModule() -> SubModule
        Create an inspector for pipeline
        
        """
        NotCacheable.__init__(self)
        Module.__init__(self)
        self.inspector = PipelineInspector()

    def compute(self):
        """ compute() -> None
        Connects the sub-pipeline to the rest of the module
        """
        pipeline = self.Vistrail.getPipeline(self.VersionNumber)
        interpreter = noncached_interpreter.get()
        interpreter.set_done_summon_hook(self.glueInputPorts)
        interpreter.set_done_update_hook(self.glueOutputPorts)        
        results = interpreter.execute(pipeline,
                                      '<<SUBMODULE>>',
                                      None,
                                      useLock=False)
        interpreter.set_done_summon_hook(None)
        interpreter.set_done_update_hook(None)

    def glueInputPorts(self, pipeline, objects):
        """ glueInputPorts(pipeline: Pipeline, objects: [object]) -> None
        Added additional input port to sub module
        
        """
        # Make sure we the sub modules interpreter point to the
        # sub_module interpreter for file pool
        for obj in objects.itervalues():
            obj.interpreter = self.interpreter
        
        self.inspector.inspectInputOutputPorts(pipeline)
        for iport, conn in self.inputPorts.iteritems():
            inputPortId = self.inspector.inputPortByName[iport]
            inputPortModule = objects[inputPortId]
            inputPortModule.set_input_port('ExternalPipe', conn[0])
        
    def glueOutputPorts(self, pipeline, objects):
        """ glueOutputPorts(pipeline: Pipeline, objects: [object]) -> None
        Added additional output port to sub module
        
        """
        self.inspector.inspectInputOutputPorts(pipeline)
        for oport in self.outputPorts.keys():
            if self.inspector.outputPortByName.has_key(oport):
                outputPortId = self.inspector.outputPortByName[oport]
                outputPortModule = objects[outputPortId]
                self.setResult(oport,
                               outputPortModule.get_output('ExternalPipe'))
        
_reg.addModule(SubModule)


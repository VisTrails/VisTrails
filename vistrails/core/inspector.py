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

"""Helper classes for inspecting vistrails/pipelines at runtime"""

from core.vistrail.pipeline import Pipeline
from core.modules.module_registry import registry

################################################################################

class PipelineInspector(object):
    """
    PipelineInspector inspects a pipeline to get informations such as
    the number of spreadsheet cells or compatibility for sub-modules
    
    """
    def __init__(self):
        """ PipelineInspector() -> None
        Initialize pipeline information
        
        """
        # A dict of input port module ids to its name/type
        self.inputPorts = {}
        self.inputPortByName = {}

        # A dict of output port module ids to its name/type
        self.outputPorts = {}
        self.outputPortByName = {}

        # A list of ids of module of type cell
        self.spreadsheetCells = []        

    def inspect(self, pipeline):
        """ inspect(pipeline: Pipeline) -> None
        Inspect a pipeline and update information
        
        """
        self.inputPorts = {}
        self.inputPortByName = {}
        self.outputPorts = {}
        self.outputPortByName = {}
        self.spreadsheetCells = []

        # First pass to check cells types
        cellType = registry.getDescriptorByName('SpreadsheetCell').module
        for mId, module in pipeline.modules.iteritems():
            desc = registry.getDescriptorByName(module.name)
            if issubclass(desc.module, cellType):
                self.spreadsheetCells.append(mId)

        # Then inspect input and output ports
        for cId, conn in pipeline.connections.iteritems():
            srcModule = pipeline.modules[conn.source.moduleId]
            dstModule = pipeline.modules[conn.destination.moduleId]
            if srcModule.name=='InputPort':
                spec = registry.getInputPortSpec(dstModule,
                                                 conn.destination.name)
                self.inputPorts[srcModule.id] = (conn.destination.name,
                                                 spec[0])
                self.inputPortByName[conn.destination.name] = srcModule.id
            if dstModule.name=='OutputPort':
                spec = registry.getOutputPortSpec(srcModule,
                                                 conn.source.name)
                self.outputPorts[dstModule.id] = (conn.source.name,
                                                  spec[0])
                self.outputPortByName[conn.source.name] = dstModule.id

    def hasInputPorts(self):
        """ hasInputPorts() -> bool
        Check if the inspected pipeline has any input ports
        
        """
        return len(self.inputPorts)>0
    
    def hasOutputPorts(self):
        """ hasOutputPorts() -> bool
        Check if the inspected pipeline has any output ports
        
        """
        return len(self.outputPorts)>0

    def numberOfCells(self):
        """ numberOfCells() -> int
        Return the number of cells that will occupied on the spreadsheet
        
        """
        return len(self.spreadsheetCells)

    def isSubModule(self):
        """ isSubModule() -> bool
        Check whether or not this pipeline is a sub module
        
        """
        return self.hasInputPorts() or self.hasOutputPorts()    

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

"""Helper classes for inspecting vistrails/pipelines at runtime"""

from core.vistrail.pipeline import Pipeline
from core.modules.module_registry import get_module_registry

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
        self.input_ports = {}
        self.input_port_by_name = {}

        # A dict of output port module ids to its name/type
        self.output_ports = {}
        self.output_port_by_name = {}

        # A list of ids of module of type cell
        self.spreadsheet_cells = []

        # A dict of ambiguous modules mapped to their annotated id
        self.annotated_modules = {}

    def inspect(self, pipeline):
        """ inspect(pipeline: Pipeline) -> None
        Inspect a pipeline and update information
        
        """
        self.inspect_input_output_ports(pipeline)
        self.inspect_spreadsheet_cells(pipeline)
        self.inspect_ambiguous_modules(pipeline)

    def has_input_ports(self):
        """ has_input_ports() -> bool
        Check if the inspected pipeline has any input ports
        
        """
        return len(self.input_ports)>0
    
    def has_output_ports(self):
        """ has_output_ports() -> bool
        Check if the inspected pipeline has any output ports
        
        """
        return len(self.output_ports)>0

    def number_of_cells(self):
        """ number_of_cells() -> int
        Return the number of cells that will occupied on the spreadsheet
        
        """
        return len(self.spreadsheet_cells)

    def is_sub_module(self):
        """ is_sub_module() -> bool
        Check whether or not this pipeline is a sub module
        
        """
        return self.has_input_ports() or self.has_output_ports()    

    def inspect_input_output_ports(self, pipeline):
        """ inspect_input_output_ports(pipeline: Pipeline) -> None
        Inspect the pipeline input/output ports, useful for submodule
        
        """
        registry = get_module_registry()
        self.input_ports = {}
        self.input_port_by_name = {}
        self.output_ports = {}
        self.output_port_by_name = {}
        if not pipeline: return        
        for cId, conn in pipeline.connections.iteritems():
            src_module = pipeline.modules[conn.source.moduleId]
            dst_module = pipeline.modules[conn.destination.moduleId]
            if src_module.name=='InputPort':
                spec = registry.getInputPortSpec(dst_module,
                                                 conn.destination.name)
                name = self.get_port_name(src_module)
                if name=='':
                    name = conn.destination.name
                self.input_ports[src_module.id] = (name,
                                                 spec[0])
                self.input_port_by_name[name] = src_module.id
            if dst_module.name=='OutputPort':
                spec = registry.getOutputPortSpec(src_module,
                                                 conn.source.name)
                name = self.get_port_name(dst_module)
                if name=='':
                    name = conn.source.name
                self.output_ports[dst_module.id] = (name,
                                                  spec[0])
                self.output_port_by_name[name] = dst_module.id

    def get_port_name(self, module):
        """ get_port_name(module: InputPort/OutputPort) -> str
        Return the real name of the port module based on 'name' function
        
        """
        for f in module.functions:
            if f.name=='name' and f.params:
                return f.params[0].strValue
        return ''
            
    def inspect_spreadsheet_cells(self, pipeline):
        """ inspect_spreadsheet_cells(pipeline: Pipeline) -> None
        Inspect the pipeline to see how many cells is needed
        
        """
        registry = get_module_registry()
        self.spreadsheet_cells = []
        if not pipeline: return

        def find_spreadsheet_cells(pipeline, root_id=None):
            if root_id is None:
                root_id = []
            # Sometimes we run without the spreadsheet!
            if registry.has_module('edu.utah.sci.vistrails.spreadsheet', 
                                   'SpreadsheetCell'):
                # First pass to check cells types
                cellType = registry.get_descriptor_by_name( \
                    'edu.utah.sci.vistrails.spreadsheet',
                    'SpreadsheetCell').module
                for mId, module in pipeline.modules.iteritems():
                    desc = registry.get_descriptor_by_name(module.package, 
                                                           module.name, 
                                                           module.namespace)
                    if issubclass(desc.module, cellType):
                        self.spreadsheet_cells.append(root_id + [mId])

            for subworkflow_id in self.find_subworkflows(pipeline):
                subworkflow = pipeline.modules[subworkflow_id]
                find_spreadsheet_cells(subworkflow.pipeline, 
                                       root_id + [subworkflow_id])

        find_spreadsheet_cells(pipeline)
    
    def find_subworkflows(self, pipeline):
        if not pipeline: 
            return
        subworkflows = []
        for m_id, module in pipeline.modules.iteritems():
            if module.is_abstraction() or module.is_group():
                subworkflows.append(m_id)
        return subworkflows

    def inspect_ambiguous_modules(self, pipeline):
        """ inspect_ambiguous_modules(pipeline: Pipeline) -> None
        inspect_ambiguous_modules returns a dict of ambiguous modules,
        i.e. cannot determine the exact module by giving just its
        name. Then in each group of dupplicate modules, a set of
        annotated id is generated for them sorted based on their id.
        The annotated_modules dictionary will map actual module id into
        their annotated one (if it is ambiguous)
        
        """
        self.annotated_modules = {}
        if not pipeline: return

        orig_pipeline = pipeline
        count = {}
        module_name = {}
        for moduleId in pipeline.modules.iterkeys():
            module = pipeline.modules[moduleId]
            if module_name.has_key(module.name): # ambiguous
                if count[module.name]==1:
                    self.annotated_modules[module_name[module.name]] = 1
                count[module.name] += 1
                self.annotated_modules[moduleId] = count[module.name]
            else:
                module_name[module.name] = moduleId
                count[module.name] = 1

        for id_list in self.spreadsheet_cells:
            pipeline = orig_pipeline
            # only need to worry about nested cells here
            if len(id_list) >= 2:
                id_iter = iter(id_list)
                m = pipeline.modules[id_iter.next()]
                for m_id in id_iter:
                    pipeline = m.pipeline
                    m = pipeline.modules[m_id]
                if m.name in module_name:
                    if count[m.name] == 1:
                        self.annotated_modules[module_name[m.name]] = 1
                    count[m.name] += 1
                    self.annotated_modules[tuple(id_list)] = count[m.name]
                else:
                    module_name[m.name] = tuple(id_list)
                    count[m.name] = 1


# if __name__ == '__main__':
#     from core.startup import VistrailsStartup
#     from core.xml_parser import XMLParser
#     xmlFile = 'C:/cygwin/home/stew/src/vistrails/trunk/examples/vtk.xml'    
#     vs = VistrailsStartup()
#     vs.init()
#     parser = XMLParser()
#     parser.openVistrail(xmlFile)
#     vistrail = parser.getVistrail()
#     pipeline = vistrail.getPipeline('Single Renderer')
#     print vistrail.latestTime

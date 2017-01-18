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
"""WebGLView provides modules to enable Web Visualizations using WebGL.
It generating WebGL+JavaScript files that can be shared and visualized in
any web browser with WebGL enabled. 
"""

import sys
import os
#import vistrails.core.system
#sys.path.append(os.path.join(vistrails.core.system.home_directory(), '.vistrails/userpackages/vtWebGL/')) 
sys.path.append(os.path.dirname(__file__)) 
from datastructure.octree import Octree
from datastructure.basic import BasicNode, DivideMesh

#import vistrails.core.modules.vistrails_module
from vistrails.core.configuration import ConfigField, ConfigPath
from vistrails.core.modules.output_modules import OutputMode, OutputModeConfig
#import vtk
from webVTKCell import webVTKCell
###############################################################################

# class WebGLView(vistrails.core.modules.vistrails_module.Module):
#     pass

# class VTKWebView(WebGLView):
#     """ Downloads file from URL """

#     def is_cacheable(self):
#         return False
           
#     def compute(self):
#         self.checkInputPort('vtkrenderer')
#         renderer = self.getInputFromPort("vtkrenderer")
#         folder = ""
#         if self.hasInputFromPort('folder'):
#             folder = self.getInputFromPort("folder")
#         rsrc_path = os.path.join(core.system.home_directory(), '.vistrails/userpackages/vtWebGL/')
#         webcell = webVTKCell(renderer.vtkInstance, folder, resource_path=rsrc_path)
    

class WebGLConfig(OutputModeConfig):
    mode_type = "WebGL"
    _fields = [ConfigField('dir', None, ConfigPath),
               ConfigField('width', 640, int),
               ConfigField('height', 480, int)]

class vtkRendererToWebGL(OutputMode):
    mode_type = "WebGL"
    config_cls = WebGLConfig

    @classmethod
    def can_compute(cls):
        return True

    def compute_output(self, output_module, configuration=None):
        old_dir = os.getcwd()
        os.chdir(configuration['dir'])
        webVTKCell(output_module.get_input('value'),
                   configuration['dir'],
                   width=configuration['width'],
                   height=configuration['height'],
                   resource_path=os.path.dirname(os.path.realpath(__file__)), showInfo=True)
        os.chdir(old_dir)

def initialize(*args, **keywords):

    from vistrails.packages.vtk.base_module import vtkRendererOutput
    vtkRendererOutput.register_output_mode(vtkRendererToWebGL)

    #reg = vistrails.core.modules.module_registry.get_module_registry()
    #basic = vistrails.core.modules.basic_modules

    #registry = vistrails.core.modules.module_registry.get_module_registry()
    #reg.add_module(WebGLView, abstract=True)
    #reg.add_module(VTKWebView)

    #vtkrenderer = registry.get_descriptor_by_name('edu.utah.sci.vistrails.vtk', 'vtkRenderer').module
    #reg.add_input_port(VTKWebView, "vtkrenderer", vtkrenderer)
    #reg.add_output_port(VTKWebView, "vtkcell",
    #                    (basic.String, 'VTKCell'), optional=True)

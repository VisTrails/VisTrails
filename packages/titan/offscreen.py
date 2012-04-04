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
## of VisTrails), please contact us at contact@vistrails.org.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################

from core.modules.module_registry import get_module_registry
from core.modules.vistrails_module import Module
from core.modules.basic_modules import File, Integer

class VTKRenderOffscreen(Module):

    def compute(self):
        r = self.getInputFromPort("renderer").vtkInstance
        window = vtk.vtkRenderWindow()
        w = self.forceGetInputFromPort("width", 512)
        h = self.forceGetInputFromPort("height", 512)
        window.OffScreenRenderingOn()
        window.SetSize(w, h)
        # r.ResetCamera()
        window.AddRenderer(r)
        window.Start()
        window.Render()
        win2image = vtk.vtkWindowToImageFilter()
        win2image.SetInput(window)
        win2image.Update()
        writer = vtk.vtkPNGWriter()
        writer.SetInput(win2image.GetOutput())
        output = self.interpreter.filePool.create_file(suffix='.png')
        writer.SetFileName(output.name)
        writer.Write()
        window.Finalize()
        self.setResult("image", output)

def register_self():
    registry = get_module_registry()
    r = registry.get_descriptor_by_name(
        'edu.utah.sci.vistrails.vtk',
# Wendel
        'vtkRenderer').module
    registry.add_module(VTKRenderOffscreen)
    registry.add_input_port(VTKRenderOffscreen, 'renderer', r)
    registry.add_input_port(VTKRenderOffscreen, 'width', Integer)
    registry.add_input_port(VTKRenderOffscreen, 'height', Integer)
    registry.add_output_port(VTKRenderOffscreen, 'image', File)


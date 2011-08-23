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

import vtk
from core.modules.module_registry import get_module_registry
from core.modules.vistrails_module import Module
from core.modules.basic_modules import File, Integer
from core import system

class VTKRenderOffscreen(Module):

    def compute(self):
        r = self.getInputFromPort("renderer").vtkInstance
        window = vtk.vtkRenderWindow()
        w = self.forceGetInputFromPort("width", 512)
        h = self.forceGetInputFromPort("height", 512)
        window.OffScreenRenderingOn()
        window.SetSize(w, h)
        # r.ResetCamera()

        widget = None
        if system.systemType=='Darwin':
            from PyQt4 import QtCore, QtGui
            widget = QtGui.QWidget(None, QtCore.Qt.FramelessWindowHint)
            widget.resize(w, h)
            widget.show()
            window.SetWindowInfo(str(int(widget.winId())))    
       
        window.AddRenderer(r)
#        window.Start()
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
        if widget!=None:
            widget.close()
        self.setResult("image", output)

def register_self():
    registry = get_module_registry()
    r = registry.get_descriptor_by_name(
        'edu.utah.sci.vistrails.vtk',
        'vtkRenderer').module
    registry.add_module(VTKRenderOffscreen)
    registry.add_input_port(VTKRenderOffscreen, 'renderer', r)
    registry.add_input_port(VTKRenderOffscreen, 'width', Integer)
    registry.add_input_port(VTKRenderOffscreen, 'height', Integer)
    registry.add_output_port(VTKRenderOffscreen, 'image', File)


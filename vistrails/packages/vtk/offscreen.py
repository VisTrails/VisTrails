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
from __future__ import division

import vtk
from vistrails.core.modules.vistrails_module import Module
from vistrails.core import system

class VTKRenderOffscreen(Module):
    _input_ports = [('renderer', 'vtkRenderer'),
                    ('width', 'basic:Integer'),
                    ('height', 'basic:Integer')]
    _output_ports = [('image', 'basic:File')]

    def compute(self):
        r = self.get_input("renderer").vtkInstance
        window = vtk.vtkRenderWindow()
        w = self.force_get_input("width", 512)
        h = self.force_get_input("height", 512)
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
        if hasattr(writer, 'SetInput'):
            writer.SetInput(win2image.GetOutput())
        else:
            # VTK 6 uses SetInputData
            writer.SetInputData(win2image.GetOutput())
        output = self.interpreter.filePool.create_file(suffix='.png')
        writer.SetFileName(output.name)
        writer.Write()
        window.Finalize()
        if widget!=None:
            widget.close()
        self.set_output("image", output)

_modules = [VTKRenderOffscreen]

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

################################################################################
# Some fixed classes that solve a few VTK API issues

# This dictionary stores the patched class to vtk class mapping.
# This would be naturally better stored as an attribute directly on the
# patched class. VTK, however, doesn't like class attributes.
description = {}

# http://www.vtk.org/doc/nightly/html/classvtkImagePlaneWidget.html
# SetUserControlledLookupTable needs to be set before calling
# SetLookupTable.  VTK should do it automatically, so let's fix it


# This fix seems to break on VTK versions larger than 5.0.3. It might also
# be because of an interaction with python 2.6, but I haven't checked that.
class vtkImagePlaneWidget_fixed(vtk.vtkImagePlaneWidget):
    def SetLookupTable(self, lookup_table):
        self.UserControlledLookupTableOn()
        vtk.vtkImagePlaneWidget.SetLookupTable(self, lookup_table)
v = vtk.vtkVersion()
version = [v.GetVTKMajorVersion(),
           v.GetVTKMinorVersion(),
           v.GetVTKBuildVersion()]
if version < [5, 0, 4]:
    description[vtkImagePlaneWidget_fixed] = vtk.vtkImagePlaneWidget
else:
    description[id(vtkImagePlaneWidget_fixed)] = vtk.vtkImagePlaneWidget

# Set docstring to wrap it correctly
vtkImagePlaneWidget_fixed.SetLookupTable.__doc__ = vtk.vtkImagePlaneWidget.SetLookupTable.__doc__

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

import vtksnl

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
class vtkImagePlaneWidget_fixed(vtksnl.vtkImagePlaneWidget):
    def SetLookupTable(self, lookup_table):
        self.UserControlledLookupTableOn()
        vtksnl.vtkImagePlaneWidget.SetLookupTable(self, lookup_table)

if tuple(vtksnl.vtkVersion().GetVTKVersion().split('.')) < ('5', '0', '4'):
    description[vtkImagePlaneWidget_fixed] = vtksnl.vtkImagePlaneWidget
else:
    description[id(vtkImagePlaneWidget_fixed)] = vtksnl.vtkImagePlaneWidget

# Set docstring to wrap it correctly
vtkImagePlaneWidget_fixed.SetLookupTable.__doc__ = vtksnl.vtkImagePlaneWidget.SetLookupTable.__doc__

###########################################################################
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
################################################################################
# VTK-SNL Package for VisTrails (Sandia National Laboratories)
################################################################################

"""The Visualization ToolKit (VTK) is an open source, freely available
software system for 3D computer graphics, image processing, and
visualization used by thousands of researchers and developers around
the world. This version of the VTK package requires the Sandia
National Laboratories version of the VTK libraries.

http://www.vtk.org"""

identifier = 'edu.utah.sci.vistrails.vtksnl'
name = 'VTKSNL'
version = '0.9.1'

def package_dependencies():
    import core.packagemanager
    manager = core.packagemanager.get_package_manager()
    if manager.has_package('edu.utah.sci.vistrails.spreadsheet'):
        return ['edu.utah.sci.vistrails.spreadsheet']
    else:
        return []

def package_requirements():
    import core.requirements
    if not core.requirements.python_module_exists('vtksnl'):
        raise core.requirements.MissingRequirement('vtksnl')
    if not core.requirements.python_module_exists('PyQt4'):
        print 'PyQt4 is not available. There will be no interaction',
        print 'between VTK and the spreadsheet.'
    import vtksnl 

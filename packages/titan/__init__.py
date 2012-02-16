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
# Titan Package for VisTrails (Sandia National Laboratories)
################################################################################

"""The Titan Informatics Toolkit is a collaborative effort between 
Sandia National Laboratories and Kitware Inc. It represents a 
significant expansion of the Visualization ToolKit (VTK) to support 
the ingestion, processing, and display of informatics data. By 
leveraging the VTK engine, Titan provides a flexible, component 
based, pipeline architecture for the integration and deployment of 
algorithms in the fields of intelligence, semantic graph and 
information analysis. 

https://www.kitware.com/InfovisWiki/"""

identifier = 'edu.utah.sci.vistrails.titan'
name = 'Titan'
version = '0.1.2'

def package_dependencies():
    import core.packagemanager
    manager = core.packagemanager.get_package_manager()

    ret = []
    #if manager.has_package('edu.utah.sci.vistrails.vtk'):
    ret.append('edu.utah.sci.vistrails.vtk')
    #if manager.has_package('edu.utah.sci.vistrails.spreadsheet'):
    ret.append('edu.utah.sci.vistrails.spreadsheet')
    return ret

def package_requirements():
    import core.requirements
    if not core.requirements.python_module_exists('titan'):
        raise core.requirements.MissingRequirement('titan')
    if not core.requirements.python_module_exists('PyQt4'):
        print 'PyQt4 is not available. There will be no interaction',
        print 'between Titan and the spreadsheet.'
    import titan 

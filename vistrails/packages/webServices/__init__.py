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
""" This package defines a set of methods to deal with web services.
It requires ZSI library to be installed (please use the trunk version as it has
important fixes. Click on configure to add wsdl urls to the package 
(use a ; to separate the urls).

ChangeLog
2010-02-25  (by VisTrails Team)
    * Updated package to version 0.9.3
    * Fixed bug with new package reloading
    * If you see the error ('Error loading configuration file: ',
                             '~/.vistrails/webServices/modules.conf')
      Just remove your ~/.vistrails/webServices and enable the package again
    * Adding http package to package dependencies
2010-01-27  (by VisTrails Team)
    * Updated package to version 0.9.2 
    * Supporting hierarchy of types (not fully tested yet)
    * Changing the default port names of modules to 'self', keeping the old 
      names (as optional ports) for backwards compatibility 
2010-01-25  (by VisTrails Team)
    * Updated package to version 0.9.1 
    * Expanded map of simple types
"""

from core.configuration import ConfigurationObject

identifier = 'edu.utah.sci.vistrails.webservices'
name = 'Web Services'
version = '0.9.3'
configuration = ConfigurationObject(wsdlList=(None, str),
                                    showWarning=True)

def package_dependencies():
    return ['edu.utah.sci.vistrails.http']
    
def package_requirements():
    import core.requirements
    if not core.requirements.python_module_exists('ZSI'):
        raise core.requirements.MissingRequirement('ZSI')
    import ZSI

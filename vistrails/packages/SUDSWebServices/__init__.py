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
It requires suds library to be installed. Click on configure to add wsdl
urls to the package (use a ; to separate the urls).
"""

from core.configuration import ConfigurationObject

identifier = 'edu.utah.sci.vistrails.sudswebservices'
name = 'SUDS Web Services'
version = '0.1.0'
configuration = ConfigurationObject(wsdlList=(None, str),
                                    proxy_http=(None, str),
                                    cache_days=(None, int))

#def package_dependencies():
#    return ['edu.utah.sci.vistrails.http']
    
def package_requirements():
    import core.requirements
    if not core.requirements.python_module_exists('suds'):
        raise core.requirements.MissingRequirement('suds')
    import suds

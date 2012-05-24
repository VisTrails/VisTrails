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
""" This package defines a set of methods to deal with web services.
It requires suds library to be installed. Click on configure to add wsdl
urls to the package (use a ; to separate the urls).
"""

from core.configuration import ConfigurationObject

identifier = 'edu.utah.sci.vistrails.sudswebservices'
name = 'SUDS Web Services'
version = '0.1.1'
configuration = ConfigurationObject(wsdlList=(None, str),
                                    proxy_http=(None, str),
                                    cache_days=(None, int))

def can_handle_identifier(identifier):
    """ This package handles packages where identifier starts with SUDS#
    """
    return identifier.startswith('SUDS#')

def can_handle_vt_file(name):
    """ This package handles file in zipped .vt files that ends with
        "-wsdl-px"
        They are cached web service instances 
    """
    return name.endswith("-wsdl.px")
    
#def package_dependencies():
#    return ['edu.utah.sci.vistrails.http']
    
def package_requirements():
    import core.requirements
    if not core.requirements.python_module_exists('suds'):
        raise core.requirements.MissingRequirement('suds')
    import suds

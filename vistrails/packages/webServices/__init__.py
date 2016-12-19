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
""" This package defines a set of methods to deal with web services.
It requires ZSI library to be installed (please use the trunk version as it has
important fixes. Click on configure to add wsdl urls to the package 
(use a ; to separate the urls).

ChangeLog
2013-04-26  (by VisTrails Team)
    * Updated package to version 0.9.4
    * Updated to new org.vistrails identifiers
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
from __future__ import division

from vistrails.core.configuration import ConfigurationObject
import vistrails.core

identifier = 'org.vistrails.vistrails.webservices'
name = 'Web Services'
version = '0.9.4'
old_identifiers = ['edu.utah.sci.vistrails.webservices']
configuration = ConfigurationObject(wsdlList=(None, str),
                                    showWarning=True)

def package_dependencies():
    return ['org.vistrails.vistrails.http']
    
def package_requirements():
    from vistrails.core.requirements import require_python_module
    require_python_module('ZSI', {
            'pip': 'zsi',
            'linux-debian': 'python-zsi',
            'linux-ubuntu': 'python-zsi',
            'linux-fedora': 'python-ZSI'})

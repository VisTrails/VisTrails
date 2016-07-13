###############################################################################
##
## Copyright (C) 2014-2016, New York University.
## Copyright (C) 2013-2014, NYU-Poly.
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

"""Table data package for VisTrails.

This package contains data extraction and manipulation facilities. It wraps
numpy and csv and allows the use of several file types from VisTrails, with
extraction and conversion routines.

"""

# ChangeLog:
# 2014-05-29 -- 0.1.5
#   * Updates JSON readers
# 2014-02-03 -- 0.1.4
#   * Merges some tabdata functionality (improve CSV)
# 2014-01-14 -- 0.1.3
#   * Adds writer modules
# 2013-12-09 -- 0.1.2
#   * No longer use 'self' ports to output tables
# 2013-10-04 -- 0.1.1
#   * Moves reading modules out of specific namespaces
#     (read|csv|CSVFile -> read|CSVFile)
# 2013-05-16 -- 0.1.0
#   * Package created (for DAT project)

from __future__ import division

from vistrails.core.packagemanager import get_package_manager

from .identifiers import *


def package_dependencies():
    pm = get_package_manager()
    spreadsheet_identifier = 'org.vistrails.vistrails.spreadsheet'
    if pm.has_package(spreadsheet_identifier):
        return [spreadsheet_identifier]
    else: # pragma: no cover
        return []


def package_requirements():
    from vistrails.core.requirements import require_python_module
    require_python_module('csv')

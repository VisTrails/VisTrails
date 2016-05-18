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

"""This file contains the spreadsheet registry: SpreadsheetRegistry
"""

from __future__ import division

class SpreadsheetRegistry(object):
    """
    SpreadsheetRegistry is the class holding information about cell and sheet
    types. Each sheet name will only have one sheet type associated with it

    """
    def __init__(self):
        """ SpreadsheetRegistry() -> SpreadsheetRegistry
        Initialize the registry with no member

        """
        self.packages = {}
        self.sheets = {}

    def registerPackage(self, package, name):
        """ registerPackage(package: python package, name: str) -> None
        Register a package containing spreadsheet widgets to the spreadsheet

        """
        self.packages[package] = name

    def unregisterPackage(self, package):
        """ unregisterPackage(package: python package) -> None
        Unregister a package out of the spreadsheet

        """
        if self.packages.has_key(package):
            del self.packages[package]

    def registerSheet(self, name, sheetType):
        """ registerSheet(name: str, sheetType: type) -> None
        Register a name for a sheet type

        """
        self.sheets[name] = sheetType

    def unregisterSheet(self, name):
        """ unregisterSheet(name: str) -> None
        Unregister a named sheet type

        """
        if self.sheets.has_key(name):
            del self.sheets[name]

    def getSheet(self, name):
        """ getSheet(name: str) -> type
        Return the type of sheet with the corresponding name

        """
        if self.sheets.has_key(name):
            return self.sheets[name]
        else:
            return None

    def getSheetByType(self, type):
        """ getSheetByType(type) -> name
        Return the name of sheet with the corresponding type

        """
        for (n,t) in self.sheets.items():
            if t==type:
                return n
        return None

spreadsheetRegistry = SpreadsheetRegistry()

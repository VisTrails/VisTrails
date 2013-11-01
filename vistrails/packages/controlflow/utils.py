###############################################################################
##
## Copyright (C) 2011-2013, NYU-Poly.
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
from vistrails.core.modules.vistrails_module import ModuleError
from fold import Fold, FoldWithModule

#################################################################################
## Some useful loop structures

class Map(FoldWithModule):
    """A Map module, that just appends the results in a list."""

    def setInitialValue(self):
        """Defining the initial value..."""

        self.initialValue = []

    def operation(self):
        """Defining the operation..."""

        self.partialResult.append(self.elementResult)


class Filter(FoldWithModule):
    """A Filter module, that returns in a list only the results that satisfy a
    condition."""

    def setInitialValue(self):
        """Defining the initial value..."""

        self.initialValue = []

    def operation(self):
        """Defining the operation..."""

        if not isinstance(self.elementResult, bool):
            raise ModuleError(self,'The function applied to the elements of the\
list must return a boolean result.')

        if self.elementResult:
            self.partialResult.append(self.element)


class Sum(Fold):
    """A Sum module, that computes the sum of the elements in a list."""

    def setInitialValue(self):
        """Defining the initial value..."""

        self.initialValue = 0

    def operation(self):
        """Defining the operation..."""

        self.partialResult += self.element


class And(Fold):
    """An And module, that computes the And result among the elements
    in a list."""

    def setInitialValue(self):
        """Defining the initial value..."""

        self.initialValue = True

    def operation(self):
        """Defining the operation..."""

        self.partialResult = self.partialResult and bool(self.element)


class Or(Fold):
    """An Or module, that computes the Or result among the elements
    in a list."""

    def setInitialValue(self):
        """Defining the initial value..."""

        self.initialValue = False

    def operation(self):
        """Defining the operation..."""

        self.partialResult = self.partialResult or self.element

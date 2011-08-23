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
from core.modules.vistrails_module import Module, ModuleError

#################################################################################
## Products

class Dot(Module):
    """This module produces a Dot product between two input ports."""
    
    def compute(self):
        list1 = self.getInputFromPort("List_1")
	list2 = self.getInputFromPort("List_2")
	lenght1 = len(list1)
	lenght2 = len(list2)
	result = []
	if lenght1 != lenght2:
            raise ModuleError(self,'Both lists must have the same size.')
        if self.hasInputFromPort("CombineTuple") and (not self.getInputFromPort\
                                                      ("CombineTuple")):
            for i in xrange(lenght1):
                tuple_ = (list1[i],list2[i])
                result.append(tuple_)
        else:
            for i in xrange(lenght1):
                if type(list1[i])==tuple and type(list2[i])==tuple:
                    tuple_ = list1[i]+list2[i]
                    result.append(tuple_)
                elif type(list1[i])==tuple and type(list2[i])!=tuple:
                    tuple_ = list1[i]+(list2[i],)
                    result.append(tuple_)
                elif type(list1[i])!=tuple and type(list2[i])==tuple:
                    tuple_ = (list1[i],)+list2[i]
                    result.append(tuple_)
                else:
                    tuple_ = (list1[i],list2[i])
                    result.append(tuple_)

        self.setResult("Result", result)


class Cross(Module):
    """This module produces a Cross product between two input ports."""
    
    def compute(self):
        list1 = self.getInputFromPort("List_1")
	list2 = self.getInputFromPort("List_2")
	lenght1 = len(list1)
	lenght2 = len(list2)
	result = []
	if self.hasInputFromPort("CombineTuple") and (not self.getInputFromPort\
                                                      ("CombineTuple")):
            for i in xrange(lenght1):
                for j in xrange(lenght2):
                    tuple_ = (list1[i],list2[j])
                    result.append(tuple_)
        else:
            for i in xrange(lenght1):
                for j in xrange(lenght2):
                    if type(list1[i])==tuple and type(list2[j])==tuple:
                        tuple_ = list1[i]+list2[j]
                        result.append(tuple_)
                    elif type(list1[i])==tuple and type(list2[j])!=tuple:
                        tuple_ = list1[i]+(list2[j],)
                        result.append(tuple_)
                    elif type(list1[i])!=tuple and type(list2[j])==tuple:
                        tuple_ = (list1[i],)+list2[j]
                        result.append(tuple_)
                    else:
                        tuple_ = (list1[i],list2[j])
                        result.append(tuple_)

        self.setResult("Result", result)

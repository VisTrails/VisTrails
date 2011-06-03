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

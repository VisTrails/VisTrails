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
        if self.hasInputFromPort("CombineTuple") and (not self.getInputFromPort("CombineTuple")):
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
	if self.hasInputFromPort("CombineTuple") and (not self.getInputFromPort("CombineTuple")):
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

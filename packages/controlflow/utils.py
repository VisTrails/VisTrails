from fold import Fold

#################################################################################
## Some useful loop structures

class Map(Fold):
    """A Map module, that just appends the results in a list."""

    def setInitialValue(self):
        """Defining the initial value..."""
        
        self.initialValue = []

    def operation(self):
        """Defining the operation..."""

        self.partialResult.append(self.elementResult)


class Filter(Fold):
    """A Filter module, that returns in a list only the results that satisfy a
    condition."""

    def setInitialValue(self):
        """Defining the initial value..."""
        
        self.initialValue = []

    def operation(self):
        """Defining the operation..."""

        if type(self.elementResult)!=bool:
            raise ModuleError(self,'The function applied to the elements of the list must return a boolean result.')

        if self.elementResult:
            self.partialResult.append(self.element)


class AreaFilter(Fold):
    """A Filter module, to be used inside triangle_area.vt; it will discard the
    areas under the value 200000."""

    def setInitialValue(self):
        """Defining the initial value..."""
        
        self.initialValue = []

    def operation(self):
        """Defining the operation..."""

        area = self.elementResult
        
        if area>200000:
            self.partialResult.append(area)


class SimilarityFilter(Fold):
    """A Filter module, to be used inside DDBJ_webService.vt; it will discard the
    species with similarity score under 95.00."""

    def setInitialValue(self):
        """Defining the initial value..."""
        
        self.initialValue = []

    def operation(self):
        """Defining the operation..."""

        similarityScore = float(self.elementResult[1].split('\t')[1])

        if similarityScore>98.00:
            self.partialResult.append(self.elementResult)


##class Sum(Fold):
##    """A Sum module, that computes the sum of the elements in a list."""
##
##    def setInitialValue(self):
##        """Defining the initial value..."""
##        
##        self.initialValue = 0
##        
##    def operation(self):
##        """Defining the operation..."""
##        
##        self.partialResult += self.element
##
##        
##class And(Fold):
##    """An And module, that computes the And result among the elements
##    in a list."""
##
##    def setInitialValue(self):
##        """Defining the initial value..."""
##        
##        self.initialValue = 1
##
##    def operation(self):
##        """Defining the operation..."""
##        
##        self.partialResult = self.partialResult and self.element
##
##        
##class Or(Fold):
##    """An Or module, that computes the Or result among the elements
##    in a list."""
##
##    def setInitialValue(self):
##        """Defining the initial value..."""
##        
##        self.initialValue = 0
##
##    def operation(self):
##        """Defining the operation..."""
##        
##        self.partialResult = self.partialResult or self.element
            

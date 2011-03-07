class AggMethod():

	###################################################################
	# This data member is a static list of aggregation methods.  As
	# AggMethod derivatives are imported, they must add themselves to 
	# this list.
	###################################################################
	theAggMethods = []
	
	###################################################################
	# The constructor must add its instance to the list of AggMethods.
	# Dervied classes must call this in their __init__.
	###################################################################
	def __init__(self):
		self.theAggMethods.append(self)
		
	###################################################################
	# getName
	# This returns  the name of the aggregation method.  Users specify
	# this name to choose the aggregation method from the collection of 
	# aggregation methods.
	###################################################################
	def getName(self): return "Unknown: there is an AggMethod that did not implement getName()"

	###################################################################
	# aggregateKernel
	# This is the implementation of a specific aggregation method.  It
	# applies the method to the kernel, returning a single value.
	###################################################################
	def aggregateKernel(self, kernel): return float('nan')
	
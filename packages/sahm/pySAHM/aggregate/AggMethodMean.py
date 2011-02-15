from AggMethod import *

class AggMethodMean(AggMethod):

	###################################################################
	# The constructor must call the base class constructor to have
	# itself added to the list of aggregation methods.
	###################################################################
	def __init__(self):
		AggMethod.__init__(self)
		
	###################################################################
	# getName
	# This returns  the name of the aggregation method.  Users specify
	# this name to choose the aggregation method from the collection of 
	# aggregation methods.
	###################################################################
	def getName(self): return "Mean"
	
	###################################################################
	# aggregateKernel
	# This is the implementation of a specific aggregation method.  It
	# applies the method to the kernel, returning a single value.
	###################################################################
	def aggregateKernel(self, kernel): 
		pixelValue = sum(kernel) / len(kernel)
		return pixelValue

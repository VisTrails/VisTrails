#!/usr/bin/python

import glob
import math
import os
import struct
import sys

from   optparse import OptionParser

from   osgeo import gdalconst
from   osgeo import gdal
from   osgeo import osr

from AggMethodMean import *
from AggMethod import *

from numpy import *

##############################################
# Aggregate
##############################################
class Aggregate():

	###
	# Aggregate must hold onto aggMethodInstance because it will go out of scope with its AggMethods
	# if Aggregate is used from another class.  Running Aggregate via the main does not need this.
	###
	aggMethodInstance = None

	verbose = False
	
	##############################################
	# main
	##############################################
	def main(self):

		# Process command-line args.  
		usageStmt = "usage:  %prog [options] <input image> <template image> <output file>"
		desc = "This application aggregates pixels from the input file to match the spatial characteristics of the template image using the specified aggregation method."
		
		parser = OptionParser(usage=usageStmt, description=desc)
		parser.add_option("-v", dest="verbose", default=False, action="store_true", help="the verbose flag causes diagnostic output to print")
		parser.add_option("-l", dest="listMethodFlag", default=False, action="store_true", help="print the names of all known aggregation methods")
		parser.add_option("-m", dest="method", default="Mean", help="the method of aggregation to apply")

		(options, args) = parser.parse_args()
		
		if options.listMethodFlag:	
			self.printAggMethods()	
			raise RuntimeError
			
		# Find the AggMethod to used, based on the user's request.
		aggMethod = self.selectAggMethod(options.method)

		# Process the remaining args.
		inImage, templateImage, outFile = self.validateArgs(args, options)
		
		self.verbose = options.verbose
		
		self.aggregateFile(inImage, templateImage, outFile, aggMethod)
		
	##############################################
	# __init__
	##############################################
	def __init__(self):
		self.loadAggMethods()
		
	##############################################
	# selectAggMethod
	##############################################
	def selectAggMethod(self, aggMethName):
		
		if aggMethName == None: aggMethName = "Mean"
		
		aggMethod = None
		
		for method in self.aggMethodInstance.theAggMethods:
			if method.getName() == aggMethName: aggMethod = method
			
		if aggMethod == None:
			print "The aggregation method, " + str(aggMethName) + ", is not implemented."
			raise RuntimeError
			
		return aggMethod
	
	##############################################
	# loadAggMethods
	##############################################
	def loadAggMethods(self):

		# Get the directory in which this class resides.
		path, scriptName = os.path.split(__file__)
		
		# Ensure the directory containing the aggregation methods is in Python's path.
		if sys.path.count(path) == 0: sys.path.append(path)
		
		# Get all other Python modules therein.
		baseAggMethodFileName = path + "/" + "AggMethod.py"
		
		if not os.path.exists(baseAggMethodFileName):
			print "Unable to find the aggregate method modules in " + path
			raise RuntimeError
		
		moduleFiles = glob.glob(path + "/*.py")
		
		###
		# Instantiate them.  When instantiated, they will add themselves to the list of 
		# aggregation methods.
		###
		for moduleFile in moduleFiles:
		
#			if not os.path.samefile(path + "/aggregate.py", moduleFile) and \
#			   not os.path.samefile(path + "/__init__.py",  moduleFile) and \
#			   not os.path.samefile(baseAggMethodFileName,  moduleFile):
			if os.path.abspath(path + "/aggregate.py") != os.path.abspath(moduleFile) and \
			   os.path.abspath(path + "/__init__.py")  != os.path.abspath(moduleFile) and \
			   os.path.abspath(baseAggMethodFileName)  != os.path.abspath(moduleFile):

				path, moduleFileName = os.path.split(moduleFile)
				moduleName, extension = os.path.splitext(moduleFileName)
				m = __import__(moduleName)
				m = getattr(m, moduleName)
				m()
				self.aggMethodInstance = m

	##############################################
	# printAggMethods
	##############################################
	def printAggMethods(self):
		for method in self.aggMethodInstance.theAggMethods:
			print method.getName()

	##############################################
	# setVerbose
	##############################################
	def setVerbose(self):
		self.verbose = True

	##############################################
	# aggregateFile
	##############################################
	def aggregateFile(self, inImage, templateImage, outFile, aggMethod):

		# Open each image once, and pass them around.
		inDataset = gdal.Open(inImage, gdalconst.GA_ReadOnly)
		if inDataset == None: raise RuntimeError("Error:  unable to read " + inImage + ".")
		
		tDataset = gdal.Open(templateImage, gdalconst.GA_Update)
		if tDataset == None: raise RuntimeError("Error:  unable to read " + templateImage + ".")
		
		# Verify the template image has lower resolution the the input image.
		tXSize,  tYSize  = self.getResolution(tDataset)
		inXSize, inYSize = self.getResolution(inDataset)
		
		if self.verbose:
			print inImage       + " pixel dimensions = (" + str(inXSize) + ", " + str(inYSize) + ")"
			print templateImage + " pixel dimensions = (" + str(tXSize)  + ", " + str(tYSize)  + ")"
			print templateImage + " data type        =  " + str(tDataset.GetRasterBand(1).DataType)
			print "GDT_BYTE = " + str(gdalconst.GDT_Byte)
					
		if math.fabs(tXSize) < math.fabs(inXSize) or math.fabs(tYSize) < math.fabs(inYSize):
			raise RuntimeError("The template image must be of lower resolution than the input image.")
		
		# Determine how many input image pixels comprise one template pixel.
		kernelXSize, kernelYSize = self.getKernelDimensions(tXSize, tYSize, inXSize, inYSize)
		
		# Create the output image.
		driver = tDataset.GetDriver()
		#type = tDataset.GetRasterBand(1).DataType  # creates an empty image
		#outDataset = driver.Create(outFile, tDataset.RasterXSize, tDataset.RasterYSize, tDataset.RasterCount, gdalconst.GDT_Float32)
		#gt = tDataset.GetGeoTransform()
		#outDataset.SetGeoTransform(gt)
		#prj = tDataset.GetProjectionRef()
		#outDataset.SetProjection(prj)
		outDataset = driver.CreateCopy(outFile, tDataset, 1) # copies all tDataset values
		tDataset = None
		
		# Ready to aggregate.
		try:
		
			outBand = outDataset.GetRasterBand(1)
			numRows = outDataset.RasterYSize	
			numCols = outDataset.RasterXSize
			
			if self.verbose:
				print "number of columns = " + str(numCols)
				print "number of rows    = " + str(numRows)

			row = 0
			col = 0
			
			while row < numRows:
				while col < numCols:
				
					inImgRow, inImgCol = self.getCorrespondingImageLocationInInput(col, row, inDataset, outDataset)
					
					kernel = self.getKernel(inImgRow, inImgCol, kernelXSize, kernelYSize, inDataset)
					if len(kernel) == 0: raise RuntimeError("Attempted to aggregate an empty kernel.")
					
					outPixelValue = aggMethod.aggregateKernel(kernel)
					
					if self.verbose: print "Writing pixel value " + str(outPixelValue) + " at (sample, line) (" + str(col) + ", " + str(row) + ")" 

					outPack = struct.pack('f', outPixelValue)
					outBand.WriteRaster(col, row, 1, 1, outPack, 1, 1, gdalconst.GDT_Float32)
					#outBand.WriteRaster(col, row, 1, 1, outPack, 1, 1, gdalconst.GDT_Byte)    # min all black
					#outBand.WriteRaster(col, row, 1, 1, outPack, 1, 1, gdalconst.GDT_Float64) # same as float32
					
					col += 1
					
				row += 1
				col  = 0
							
		except:
			
			inDataset  = None
			outDataset = None
			os.remove(outFile)
			raise
			
		# Once we're done, close the datasets
		inDataset  = None
		outDataset = None

	##############################################
	# getCorrespondingImageLocationInInput
	##############################################
	def getCorrespondingImageLocationInInput(self, outCol, outRow, inDataset, outDataset):
	
		if self.verbose: print "in getCorrespondingImageLocationInInput"

		###
		# If output image uses "pixel is area" for the origin, shift the image point to
		# the upper left.
		###
		metadata = outDataset.GetDriver().GetMetadata()
		aop = "AREA_OR_POINT"
		
		if metadata.has_key(aop) and metadata[aop] == 'Area':
			outCol -= 0.5
			outRow -= 0.5
			if self.verbose: print "shifting output pixel by (-0.5, -0.5) because output image uses 'pixel is area'"
	   
		# Output image to ground
		outCoefs = outDataset.GetGeoTransform()
		x = outCoefs[0] + outCol * outCoefs[1] + outRow * outCoefs[2];
		y = outCoefs[3] + outCol * outCoefs[4] + outRow * outCoefs[5];
	
		# Ground to input image
		inCoefs = inDataset.GetGeoTransform()
		xOrigin     = inCoefs[0] 
		yOrigin     = inCoefs[3] 
		pixelWidth  = inCoefs[1] 
		pixelHeight = inCoefs[5] 
		
		inCol = int((x - xOrigin) / pixelWidth) 
		inRow = int((y - yOrigin) / pixelHeight)
		
		if self.verbose:
		
			print "(outCol, outRow) = (" + str(outCol)    + ", " + str(outRow)    + ")"
			print "outCoefs         = "  + str(outCoefs)
			print "(x, y)           = (" + str(x)         + ", " + str(y)         + ")"
			print "inCoefs          = "  + str(inCoefs)
			print "(inCol, inRow)   = (" + str(inCol)     + ", " + str(inRow)     + ")"

		return inRow, inCol
	
	##############################################
	# getKernel
	##############################################
	def getKernel(self, row, col, kernelXSize, kernelYSize, inDataset):

		readKernelXSize = kernelXSize
		readKernelYSize = kernelYSize
		
		xOffset = col + int(kernelXSize / -2.0)
		yOffset = row + int(kernelYSize / -2.0)

		if self.verbose:
			print "Original read parameters:"
			print "(col, row)                         = (" + str(col)         + ", " + str(row)         + ")"
			print "(xOffset, yOffset)                 = (" + str(xOffset)     + ", " + str(yOffset)     + ")"
			print "(kernelXSize, kernelYSize)         = (" + str(kernelXSize) + ", " + str(kernelYSize) + ")"
			print "(readKernelXSize, readKernelYSize) = (" + str(readKernelXSize) + ", " + str(readKernelYSize) + ")"
			
		# Determine if the kernel falls without the input image.
		if xOffset < 0:			
			if self.verbose: print "Kernel outside image, adjusting..."
			readKernelXSize += xOffset
			xOffset = 0
		
		if yOffset < 0:			
			if self.verbose: print "Kernel outside image, adjusting..."
			readKernelYSize += yOffset
			yOffset = 0

		if self.verbose:
			print "Adjusted read parameters:"
			print "(col, row)                         = (" + str(col)             + ", " + str(row)         + ")"
			print "(xOffset, yOffset)                 = (" + str(xOffset)         + ", " + str(yOffset)     + ")"
			print "(kernelXSize, kernelYSize)         = (" + str(kernelXSize)     + ", " + str(kernelYSize) + ")"
			print "(readKernelXSize, readKernelYSize) = (" + str(readKernelXSize) + ", " + str(readKernelYSize) + ")"
			
		scanline = inDataset.ReadRaster(xOffset, 
										yOffset, 
										readKernelXSize, 
										readKernelYSize, 
										readKernelXSize, 
										readKernelYSize, 
										gdalconst.GDT_Float32)

		listOfFloats = list(struct.unpack('f' * readKernelXSize * readKernelYSize, scanline))
		
		if self.verbose: print "kernel = " + str(listOfFloats)
		
		return listOfFloats

	##############################################
	# getKernelDimensions
	##############################################
	def getKernelDimensions(self, tXSize, tYSize, inXSize, inYSize):
	 
		kernelXSize = int(math.ceil(tXSize / inXSize))
		kernelYSize = int(math.ceil(tYSize / inYSize))
		
		# Make them odd, so the target pixel will be in the center.
		#if kernelXSize % 2 == 0: kernelXSize += 1
		#if kernelYSize % 2 == 0: kernelYSize += 1
		
		if self.verbose: print "kernel dimensions = (" + str(kernelXSize) + ", " + str(kernelYSize) + ")"
		
		return kernelXSize, kernelYSize
		
	##############################################
	# getResolution
	##############################################
	def getResolution(self, dataset):

		coefs = dataset.GetGeoTransform()
		xSize = coefs[1]
		ySize = coefs[5]

		return xSize, ySize

	##############################################
	# validateArgs
	##############################################
	def validateArgs(self, args, options):

		if len(args) < 3:
			raise RuntimeError("At least three arguments required.  Please refer to the help.")
			
		inImage  = args[0]
		if not os.path.exists(inImage):
			raise ValueError("Input image, " + inImage + ", does not exist.")

		templateImage = args[1]
		if not os.path.exists(templateImage):
			raise ValueError("Template image, " + templateImage + ", does not exist.")

		outFile = args[2]
		if  os.path.exists(outFile):
			raise ValueError("Output file, " + outFile + ", already exists.")
		
		#methods = ["mean"]
		#methodSet = set(methods)
		#if not options.method in methodSet:
		#	raise ValueError("Method, " + options.method + ", is unknown to this application.")
		
		return inImage, templateImage, outFile
		
##############################################
# Invoke the main
##############################################
if __name__ == "__main__":
	try:
		sys.exit(Aggregate().main())
	except:
		sys.exit(1)
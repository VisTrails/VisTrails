#!/usr/bin/python

import glob
import math
import os
import shutil
import struct
import sys

from optparse import OptionParser

from osgeo import gdalconst
from osgeo import gdal
from osgeo import osr

from numpy import *

path, scriptName = os.path.split(__file__)
if sys.path.count(path) == 0: sys.path.append(path)
from aggregate.aggregate import Aggregate

##############################################
# PARC:  Project, Aggregate, Resample, Clip
##############################################
class PARC:

	aggInstance = None
	aggMethod   = None
	resMethod   = "near"
	
	###
	# imageCoversTemplate computations must be done in geographic coordinates because
	# the UTM zone may be unknown.  Store them once here.
	###
	tGeoUlX     = None
	tGeoUlY     = None
	tGeoLrX     = None
	tGeoLrY     = None
	
	verbose     = False
	
	##############################################
	# main
	##############################################
	def main(self, args_in):
		# Process command-line args.  
		usageStmt = "usage:  %prog [options] <template image> <input dir or list of input files>"
		desc = "This application projects, aggregates, resamples, and clips imagery."
		
		parser = OptionParser(usage=usageStmt, description=desc)
		parser.add_option("-l", dest="listMethodFlag", default=False, action="store_true", help="print the names of all known aggregation methods")
		parser.add_option("-m", dest="method", default="Mean", help="the method of aggregation to apply; no aggregation, if unspecified")
		parser.add_option("-o", dest="outDir", default="./", help="directory in which to put processed images, defaults to current directory")
		parser.add_option("-r", dest="resampleMethod", default="near", help="the method of resampling to apply: 'near', 'bilinear', 'cubic', 'cubicspline', 'lanczos'")
		parser.add_option("-v", dest="verbose", default=False, action="store_true", help="the verbose flag causes diagnostic output to print")

		(options, args) = parser.parse_args(args_in)

		self.verbose = options.verbose

		if options.listMethodFlag:	
			self.aggInstance.printAggMethods()	
			raise RuntimeError
		
		
		
		self.validateArgs(args, options)

		InputFiles = self.getInputFiles(args)
		self.parcFiles(args[0], InputFiles, options.outDir)

	##############################################
	# __init__
	##############################################
	def __init__(self):
		self.aggInstance = Aggregate()

	##############################################
	# parcFiles
	##############################################
	def parcFiles(self, template, sourceImages, outDir):

		# Get the PARC parameters from the template.
		ulx, uly, lrx, lry, destEPSG, xScale, yScale = self.getTemplateParams(template)

		# Clip and reproject each source image. 
		for image in sourceImages:
		
			# Ensure source is different from template.
			if os.path.abspath(template) != os.path.abspath(image):
			
				inPath, inFileName = os.path.split(image)
				outFile = os.path.join(outDir, inFileName)
				
				if os.path.exists(outFile) and \
				   os.path.abspath(image) == os.path.abspath(outFile):
				   
					baseName, extension = os.path.splitext(outFile)
					outFile = baseName + "-PARC.tif"
				
				#print "test"
				self.parcFile(image, outFile, ulx, uly, lrx, lry, destEPSG, xScale, yScale, template)
	
	##############################################
	# getTemplateParams
	##############################################
	def getTemplateParams(self, template):

		# Get the PARC parameters from the template.
		dataset = gdal.Open(template, gdalconst.GA_ReadOnly)
		if dataset is None:
			print "Unable to open " + template
			raise RuntimeError
			
		xform  = dataset.GetGeoTransform()
		xScale = xform[1]
		yScale = xform[5]
		
		# Ensure the template has square pixels.
		if math.fabs(xScale) != math.fabs(yScale):
			print "The template image must have square pixels."
			print "x pixel scale = " + str(xScale)
			print "y pixel scale = " + str(yScale)
			raise RuntimeError
		
		width  = dataset.RasterXSize
		height = dataset.RasterYSize
		
		ulx = xform[0]
		uly = xform[3]	
		lrx = ulx + width  * xScale
		lry = uly + height * yScale

		if self.verbose == True:
			print "upper left = (" + str(ulx) + ", " + str(uly) + ")"
			print "lower right = (" + str(lrx) + ", " + str(lry) + ")"
			
		# Store the extent in geographic coordinates.
		tEPSG = self.getEPSG(dataset)
		
		if tEPSG == 4326:
		
			self.tGeoUlX = ulx
			self.tGeoUlY = uly
			self.tGeoLrX = lrx
			self.tGeoLrY = lry
			
		else:
		
			self.tGeoUlX, self.tGeoUlY, self.tGeoLrX, self.tGeoLrY = self.getExtentInGeog(ulx, uly, lrx, lry, tEPSG)
			
		return ulx, uly, lrx, lry, tEPSG, xScale, yScale
		
	##############################################
	# getExtentInGeog
	##############################################
	def getExtentInGeog(self, ulx, uly, lrx, lry, EPSG):
	
		s_srs = osr.SpatialReference()
		s_srs.ImportFromEPSG(EPSG)
		
		t_srs = osr.SpatialReference()
		t_srs.ImportFromEPSG(4326)
		
		coordXform = osr.CoordinateTransformation(s_srs, t_srs)
		
		result = coordXform.TransformPoint(ulx, uly)
		gulx = result[0]
		guly = result[1]
		
		result = coordXform.TransformPoint(lrx, lry)
		glrx = result[0]
		glry = result[1]		
	
		return gulx, guly, glrx, glry
		
	##############################################
	# getEPSG
	##############################################
	def getEPSG(self, dataset):

		wkt = dataset.GetProjection()
		s_srs = osr.SpatialReference(wkt)
		s_srs.AutoIdentifyEPSG()
		
		epsg = s_srs.GetAuthorityCode("PROJCS")
		if epsg == None: epsg = s_srs.GetAuthorityCode("GEOGCS")
			
		if epsg == None:
			print "Unable to extract the EPSG code from the image."	
			raise RuntimeError
			
		return int(epsg)

	##############################################
	# parcFile
	##############################################
	def parcFile(self, source, dest, ulx, uly, lrx, lry, destEPSG, xScale, yScale, template):

		if self.verbose:
			print "source image = " + source
			print "destination image = " + dest
			
		# Verify the source image falls within the template.
		if not self.imageCoversTemplate(source, ulx, uly, lrx, lry, destEPSG):
			print source + " falls outside the template image, so it will not be processed."
			return
			
		###
		# Clip and reproject.
		###
		print "Clipping and reprojecting..."		
		cmd	= "gdalwarp -te " + str(ulx) + " " + str(lry) + " " + str(lrx) + " " + str(uly) + " -t_srs EPSG:" + str(destEPSG) + " " + source + " " + dest
		if self.verbose:  print "command = " + cmd
		returnValue = os.system(cmd)
		
		# Check for the output file, ensuring gdal_translate succeeded.
		if not os.path.exists(dest):
			print "gdalwarp did not produce output."
			raise RuntimeError
		
		if returnValue != 0: raise RuntimeError
		
		destFile, destExt  = os.path.splitext(dest)
		destTemp = destFile + "-temp" + destExt

		###
		# Aggregate now, if requested.
		###
		if self.aggMethod != None:
			print "Aggregating..."
			shutil.move(dest, destTemp)
			self.aggInstance.aggregateFile(destTemp, template, dest, self.aggMethod)
		
		###
		# Perform the final resampling.
		###
		print "Resampling..."
		shutil.move(dest, destTemp)
		cmd	= "gdalwarp -tr " +	str(xScale) + " " + str(yScale) + " -r " + self.resMethod + " " + destTemp + " " + dest
		if self.verbose:  print "command = " + cmd
		returnValue = os.system(cmd)
		
		if os.path.exists(destTemp): os.remove(destTemp)
			
		# Check for the output file, ensuring gdal_translate succeeded.
		if not os.path.exists(dest):
			print "gdalwarp did not produce output."
			raise RuntimeError
		
		if returnValue != 0: raise RuntimeError
				
	##############################################
	# imageCoversTemplate
	##############################################
	def imageCoversTemplate(self, source, tulx, tuly, tlrx, tlry, tEPSG):
	
		inside = False
		
		# Open the image.
		dataset = gdal.Open(source, gdalconst.GA_ReadOnly)
		if dataset is None:
			print "Unable to open " + source
			raise RuntimeError
			
		# Get its CRS information.
		xform  = dataset.GetGeoTransform()
		xScale = xform[1]
		yScale = xform[5]
		
		width  = dataset.RasterXSize
		height = dataset.RasterYSize
		
		# Get its extent and EPSG.
		sulx = xform[0]
		suly = xform[3]	
		slrx = sulx + width  * xScale
		slry = suly + height * yScale
		
		sEPSG = self.getEPSG(dataset)
		
		# Transform the image's corners to a geographic CRS, if necessary.
		if sEPSG != 4326:

			gulx, guly, glrx, glry = self.getExtentInGeog(sulx, suly, slrx, slry, sEPSG)
		
		else:
		
			gulx = sulx
			guly = suly
			glrx = slrx
			glry = slry
						
		# Compare the corners.
		if gulx <= self.tGeoUlX and guly >= self.tGeoUlY and \
		   glrx >= self.tGeoLrX and glry <= self.tGeoLrY:
				   
			inside = True
			
		else:

			if self.verbose == True:
				print "template upper left  = (" + str(self.tGeoUlX) + ", " + str(self.tGeoUlY) + ")"
				print "template lower right = (" + str(self.tGeoLrX) + ", " + str(self.tGeoLrY) + ")"
				print "image    upper left  = (" + str(gulx) + ", " + str(guly) + ")"
				print "image    lower right = (" + str(glrx) + ", " + str(glry) + ")"
				print "Note: points are given in geographic coordinates."
				
		return inside
		
	##############################################
	# validateArgs
	##############################################
	def validateArgs(self, args, options):
		
		# Aggregate method
		self.aggMethod = self.aggInstance.selectAggMethod(options.method)
		
		# Resample method
		self.resMethod = options.resampleMethod
		
		# Validate template image.
		if len(args) < 2:
			print "A template image and at least one input file or directory must be provided."
			raise RuntimeError

		template = args[0]

		if not os.path.exists(template):
			print "Template file, " + template + ", does not exist."
			raise RuntimeError

		# Validate output directory.
		if not os.path.exists(options.outDir):
			print "Output directory, " + options.outDir + ", does not exist."
			raise RuntimeError
	
		if not os.path.isdir(options.outDir):
			print options.outDir + " is not a directory."
			raise RuntimeError

	##############################################
	# getInputFiles
	##############################################
	def getInputFiles(self, args):
	
		sourceImages = None
		
		# Validate input directory or files.
		if os.path.isdir(args[1]):
			if self.verbose == True:  print "Input directory found..."
			
			if not os.path.exists(args[1]):
				print "Input directory, " + args[1] + ", does not exist."
				raise RuntimeError
				
			sourceImages = glob.glob(args[1] + "/*.tif")
			if len(sourceImages) == 0:
				print "There are no images in " + args[1]
				raise RuntimeError
				
		else:
			sourceImages = args[1:]
			if self.verbose == True:  print "source images: " + str(sourceImages)

		return sourceImages
		
##############################################
# Invoke the main
##############################################
if __name__ == "__main__":
	try:
		sys.exit(PARC().main(sys.argv))
	except:
		sys.exit(1)

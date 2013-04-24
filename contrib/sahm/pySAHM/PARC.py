#!/usr/bin/python

import glob
import math
import os
import shutil
import struct
import sys
import csv
import Queue
import thread
import subprocess

from optparse import OptionParser

from osgeo import gdalconst
from osgeo import gdal
from osgeo import osr


from numpy import *
import numpy as np

import utilities

def main(args_in):
    """
    Process commandline Arguments, 
    Create an instance of PARC with the Variables,
    Kick off the parkFiles function of our PARC instance
    """
    # Process command-line args.  
    usageStmt = "usage:  %prog [options] <template image> <input dir or list of input files>"
    desc = "This application projects, aggregates, resamples, and clips imagery."
    
    parser = OptionParser(usage=usageStmt, description=desc)
    parser.add_option("-l", dest="listMethodFlag", default=False, action="store_true", help="print the names of all known aggregation methods")
    parser.add_option("-o", dest="out_dir", default="./", help="directory in which to put processed images, defaults to current directory")
    parser.add_option("-v", dest="verbose", default=False, action="store_true", help="the verbose flag causes diagnostic output to print")
    parser.add_option("-t", dest="templateRaster", help="The template raster used for projection, origin, cell size and extent")
    parser.add_option("-i", dest="inputs_CSV", help="The CSV containing the list of files to process.  Format is 'FilePath, Categorical, Resampling, Aggreagtion")
    parser.add_option("-m", dest="multicore", default=True, help="'True', 'False' indicating whether to use multiple cores or not") 
    (options, args) = parser.parse_args(args_in)
    
    ourPARC = PARC()
    ourPARC.verbose = options.verbose
    ourPARC.template = options.templateRaster
    ourPARC.out_dir = options.out_dir
    ourPARC.inputs_CSV = options.inputs_CSV
    ourPARC.multicores = options.multicore
    ourPARC.parcFiles()

class PARC:
    '''
     PARC:  Project, Aggregate, Resample, Clip
      The workflow on this beast is as follows:
            For each dataset
            Step 1: RePrject the source raster into a tmp raster using
                the projection info from the template and the method if 
                supplied or the default of nearest if not.
                At this stage the tmp output will have a cell size about
                the same as the input.  We just use the default for this 
                setting.
            Step 2: Aggregate the tmpRaster to have the same origin, 
                cell size and extent as our template.
    '''    
    
    def __init__(self):
        #instance level variables
        self.verbose = False
        self.template = ""
        self.template_params = {}
        self.out_dir = ""
        self.inputs_CSV = ''
        self.inputs = []
        self.agg_methods = ['Min', 'Mean', 'Max', 'Majority']
        self.resample_methods = ['NearestNeighbor', 'Bilinear', 'Cubic', 'CubicSpline', 'Lanczos']
        self.logger = None
        self.multicores = 'False'
        self.module = None

    def parcFiles(self):
        '''
            1: Parse the inputs_CSV into our inputs list
            2: Make sure all of our instance variables are good and proper
            3: Loop through the list of sourceImages and PARC each one.
            4: The outputs will be stored in the output directory
            5: Additionally an output CSV will be produced that lists the 
            inputs, parameters used, and outputs
        '''
        
        self.logger.writetolog("Starting PARC", True, True)
        self.validateArgs()
        self.logger.writetolog("    Arguments validated successfully", True, True)
        if self.multicores.lower() in ['true', 'yes', 't', 'y', '1']:
            self.processFilesMC()
        else:
            self.processFiles()
        
        self.logger.writetolog("Finished PARC", True, True)
        
    def processFiles(self):
        # Clip and reproject each source image.
        for image in self.inputs:
            # Ensure source is different from template.
            #if not os.path.samefile(template, image):
            inPath, inFileName = os.path.split(image[0])
            outFile, ext = os.path.splitext(inFileName) 
            outFile = os.path.join(self.out_dir, outFile + ".tif")
            
            # os.path.samefile(image, outFile):
            if os.path.exists(outFile) and \
               os.path.abspath(image[0]) == os.path.abspath(outFile):

                baseName, extension = os.path.splitext(outFile)
                outFile = baseName + "-PARC.tif"
                
            if os.path.abspath(self.template) != os.path.abspath(image[0]):
                self.parcFile(image, outFile)
            elif os.path.abspath(self.template) == os.path.abspath(image[0]): 
                shutil.copyfile(self.template, outFile)
                
		
        
    def processFilesMC(self):
        '''This function has the same functionality as parcFiles
        with the addition of utilizing multiple cores to do the processing.
        '''
        results= Queue.Queue()
        process_count= 0
        
        for image in self.inputs:
            # Ensure source is different from template.
            #if not os.path.samefile(template, image):
            inPath, inFileName = os.path.split(image[0])
            outFile, ext = os.path.splitext(inFileName) 
            outFile = os.path.join(self.out_dir, outFile + ".tif")
            
            # os.path.samefile(image, outFile):
            if os.path.exists(outFile) and \
               os.path.abspath(image[0]) == os.path.abspath(outFile):

                baseName, extension = os.path.splitext(outFile)
                outFile = baseName + "-PARC.tif"
            
            if os.path.abspath(self.template) != os.path.abspath(image[0]):
                image_short_name = os.path.split(image[0])[1]
                args = '-s ' + '"' + os.path.abspath(image[0]) + '"'
                args += ' -c '  + '"' + image[1] + '"'
                args += ' -d ' + os.path.abspath(outFile)
                args += ' -t ' + os.path.abspath(self.template)
                args += ' -r ' + image[2]
                args += ' -a ' + image[3]
                
                execDir = os.path.split(__file__)[0]
                executable = os.path.join(execDir, 'singlePARC.py')
                
                pyEx = sys.executable
                command = ' '.join([pyEx, executable, args])
                self.logger.writetolog(command, False, False)
                proc = subprocess.Popen( command )
                thread.start_new_thread(utilities.process_waiter,
                        (proc, image_short_name, results))
                process_count+= 1
            
        while process_count > 0:
            description, rc= results.get()
            
            if rc == 0:
                if self.verbose:
                    msg = "    " + description + " finished successfully:  " + \
                        str(len(self.inputs) - process_count + 1)  + " done out of " \
                        + str(len(self.inputs))
                    self.logger.writetolog(msg, True, True)
            else:
                self.logger.writetolog("There was a problem with: " + description , True, True)
            process_count-= 1
                
        
        
        self.logger.writetolog("Finished PARC", True, True)

    def parcFile(self, source, dest):
        """
        Processes a single file
        """
        gdal.UseExceptions()
        
        shortName = os.path.split(os.path.splitext(source[0])[0])[1]
        self.logger.writetolog("    Starting processing of " + source[0])
        sourceParams = self.getRasterParams(source[0])
                
        gdalType = None
        if source[2].lower() == "nearestneighbor":
            gdalType = gdalconst.GRA_NearestNeighbour
        if source[2].lower() == "bilinear":
            gdalType = gdalconst.GRA_Bilinear
        if source[2].lower() == "cubic":
            gdalType = gdalconst.GRA_Cubic
        if source[2].lower() == "cubicspline":
            gdalType = gdalconst.GRA_CubicSpline
        if source[2].lower() == "lanczos":
            gdalType = gdalconst.GRA_Lanczos
        if gdalType == None:
            self.logger.writetolog("   Specified resampling method (" + source[2] + ") not one of 'NearestNeighbor', 'Bilinear', 'Cubic', 'CubicSpline', or 'Lanczos'.  Defaulting to 'NearestNeighbor'")
            gdalType = gdalconst.GRA_NearestNeighbour
        
        #Open dgal dataset of the source to pull some values from
        srcDs = gdal.Open(source[0])
        
        cellRatio = self.getTemplateSRSCellSize(sourceParams)/self.template_params["xScale"]
        msg = "  ratio of source cell size to template cell size = " + str(cellRatio)
        msg += "    template cell size = " + str(self.template_params["xScale"])
        msg += "    " + shortName + " cell size = " + str(self.getTemplateSRSCellSize(sourceParams))
        self.writetolog(msg)
            
        if cellRatio > 0.5:
            #The source cell size is close enough to our template cell size,
            #or smaller so
            #that all we need to do is reproject and resample.
            self.logger.writetolog("  cell ratio > .5: reprojecting and resampling to template parameters only")
            self.reprojectRaster(srcDs, sourceParams, self.template_params, dest, 
                                gdalType, shortName, self.template_params["xScale"])
        else:
            #Our Target cell size is much bigger than our source we need to do 
            #some aggregation to make things work.
            msg = '  cell ratio <= .5: reprojecting and resampling to template parameters'
            msg += '    then aggregating the reprojected raster to match template parameters'
            self.writetolog(msg)   
			    
            targetCellSize, numSourcePerTarget = self.getAggregateTargetCellSize(sourceParams)
            tmpOutput = os.path.join(os.path.dirname(dest), "tmp_" + os.path.basename(dest))
            
            self.reprojectRaster(srcDs, sourceParams, self.template_params,
                                tmpOutput, gdalType,  shortName, targetCellSize)
            self.writetolog("   Starting on Aggregating: " + shortName)
                
            tmpOutput2 = os.path.splitext(tmpOutput)[0] + ".tif"
            self.Aggregate(tmpOutput2, dest, 
                        sourceParams, self.template_params,
                        source[3], numSourcePerTarget)
            
            try:
                os.remove(tmpOutput2)
            except WindowsError:
                pass
            
    
    def getTemplateSRSCellSize(self, sourceParams):
        """
        Calculate what size our source image pixels would be in the template SRS
        """
        #first convert our template origin into the source srs
        tOriginX, tOriginY = self.transformPoint(self.template_params["west"], self.template_params["north"], 
                                        self.template_params["srs"], sourceParams["srs"])
        #next add the source xScale to the converted origin x and convert that back to template srs
        tOriginX1 = self.transformPoint (tOriginX + sourceParams["xScale"], tOriginY, 
                                                sourceParams["srs"], self.template_params["srs"])[0]                        
        
        
#        templateCellXCorner1 = (self.template_params["west"], self.template_params["north"], 
#                                        self.template_params["srs"], sourceParams["srs"])[0]
#        
#        targetCellXCorner1 = (sourceParams["west"], sourceParams["north"], 
#                                                sourceParams["srs"], self.template_params["srs"])[0]
#        targetCellXCorner2 = self.transformPoint(sourceParams["west"] + sourceParams["xScale"], 
#                                                sourceParams["north"], sourceParams["srs"], self.template_params["srs"])[0]
        templateSRSCellSize = abs(abs(tOriginX1) - abs(self.template_params["west"]))
        return templateSRSCellSize

    def getAggregateTargetCellSize(self, sourceParams):
        """
        This function determines the appropriate cell size to
        reproject/resample our source raster into before 
        aggregating.
        This size is the cell size that results in a template 
        cell containing a whole number of cells which are as 
        close as possible to the cell dimension that would 
        result if you reprojected the source cells into the 
        target srs without changing cell size.
        """
        #first determine what cell size we are going to use for the initial reproject/resample 
        #step 1:  Determine the native cell size in the template coordinate system.
        templateSRSCellSize = self.getTemplateSRSCellSize(sourceParams)
        #step 2:  round this up or down to an even fraction of the template cell size
        # for example source = 30, target = 250 resampledSource = 250/round(250/30)
        sourcePixelsPerTarget = round(self.template_params["xScale"]/templateSRSCellSize)
        nearestWholeCellSize = (self.template_params["xScale"] / 
                            sourcePixelsPerTarget)
        return nearestWholeCellSize, sourcePixelsPerTarget
        
        
    def Aggregate(self, inFile, outFile, sourceParams, templateParams, method=None, numSourcePerTarget=10):
        sourceDs = gdal.Open(inFile, gdalconst.GA_ReadOnly)
        sourceBand  = sourceDs.GetRasterBand(1)
        
        tmpOutput = os.path.splitext(outFile)[0] + ".tif"
        tmpOutDataset = self.generateOutputDS(sourceParams, templateParams, tmpOutput)
        outBand = tmpOutDataset.GetRasterBand(1)
        
        rows = int(sourceParams["height"])
        cols = int(sourceParams["width"])

        row = 0
        col = 0
        
        
        pcntDone = 0.0
        if self.verbose:
            print "    % Done:    0.0",
            
        while row < templateParams["width"]:
            while col < templateParams["height"]:
                sourceRow = row * numSourcePerTarget
                sourceCol = col * numSourcePerTarget

                #kernel = self.getKernel(sourceRow, sourceCol, numSourcePerTarget, sourceDs)
                kernel = sourceDs.GetRasterBand(1).ReadAsArray(int(sourceRow), 
                                                    int(sourceCol), 
                                                    int(numSourcePerTarget),
                                                    int(numSourcePerTarget))
                #convert kernel values of our nodata to nan
                ndMask = ma.masked_array(kernel, mask=(kernel==sourceParams["NoData"]))
                #print kernel
                if method == "Min":
                    ans = ndMask.min()
                elif method == "Max":
                    ans = ndMask.max()
                elif method == "Majority":
#                    ndMask = ndMask.flatten()
                    uniques = np.unique(ndMask)
                    curMajority = -3.40282346639e+038
                    for val in uniques:
                        numOccurances = (array(ndMask)==val).sum()
                        if numOccurances > curMajority:
                            ans = val
                            curMajority = numOccurances
                            
#                    histogram = np.histogram(ndMask, uniques)
#                    ans = histogram[1][histogram[0].argmax()]
                else:
                    ans = ndMask.mean()
                
#                print ndMask
#                print ans
                #special case real ugly
                if ans < 0 and sourceParams["signedByte"]:
                    ans = ans + 255
                
                ansArray = empty([1, 1])
                if type(ans) == ma.core.MaskedArray:
                    ansArray[0, 0] = sourceParams["NoData"]
                else:
                    ansArray[0, 0] = ans

                outBand.WriteArray(ansArray, row, col)
                
                col += 1
                
            row += 1
            col  = 0
            if self.verbose:
                if float(row)/templateParams["width"] > float(pcntDone)/100:
                    pcntDone += 2.5
                    if int(pcntDone) % 10 == 0:
                        print str(pcntDone),
                    else:
                        print ".",
        if self.verbose:
            print "Done"
#        if self.verbose:
#            print "Done\nSaving to ASCII format"
#                            
#        driver = gdal.GetDriverByName("AAIGrid")
#        driver.Register()
#        
#        dst_ds = driver.CreateCopy(outFile, tmpOutDataset, 0)
#        if self.verbose:
#            print "    Finished Saving ", self.shortName
        
        dst_ds = None
        tmpOutDataset=None
        
    def getRasterParams(self, rasterFile):
        """
        Extracts properties from a passed raster
        All values are stored in a dictionary which is returned.
        If errors are encountered along the way the error messages will
        be returned as a list in the 'Error' element.
        """
        try:
            #initialize our params dictionary to have None for all parma
            params = {}
            allRasterParams = ["Error", "xScale", "yScale", "width", "height",
                            "east", "north", "west", "south",  
                            "tEast", "tNorth", "tWest", "tSouth",
                            "gEast", "gNorth", "gWest", "gSouth",  
                            "Wkt", "srs", "gt", "prj", "NoData", "PixelType", "file_name"]
            
            for param in allRasterParams:
                params[param] = None
            params["Error"] = []
            params["file_name"] = rasterFile

            
            # Get the PARC parameters from the rasterFile.
            dataset = gdal.Open(rasterFile, gdalconst.GA_ReadOnly)
            if dataset is None:
                params["Error"].append("Unable to open file")
                return params
                
                #print "Unable to open " + rasterFile
                #raise Exception, "Unable to open specifed file " + rasterFile
                
            
            xform  = dataset.GetGeoTransform()
            params["xScale"] = xform[1]
            params["yScale"] = xform[5]
    
            params["width"]  = dataset.RasterXSize
            params["height"] = dataset.RasterYSize
    
            params["west"] = xform[0]
            params["north"] = xform[3]
            params["east"] = params["west"] + params["width"]  * params["xScale"]
            params["south"] = params["north"] + params["height"] * params["yScale"]
    
            try:
                wkt = dataset.GetProjection()
                params["gt"] = dataset.GetGeoTransform()
                params["prj"] = dataset.GetProjectionRef()
                params["srs"] = osr.SpatialReference(wkt)
                if wkt == '':
                    params["Error"].append("Undefined projection")
                else:
                    
                    if rasterFile == self.template:
                        params["tWest"], params["tNorth"] = params["west"], params["north"]
                        params["tEast"], params["tSouth"] = params["east"], params["south"]
                    elif params["srs"].ExportToWkt() == self.template_params["srs"].ExportToWkt():
                        params["tWest"], params["tNorth"] = params["west"], params["north"]
                        params["tEast"], params["tSouth"] = params["east"], params["south"]
                    else:
                        try:
                            params["tWest"], params["tNorth"] = self.transformPoint(params["west"], params["north"], params["srs"], self.template_params["srs"])
                            params["tEast"], params["tSouth"] = self.transformPoint(params["east"], params["south"], params["srs"], self.template_params["srs"])
                        except:
                            params["Error"].append("Could not transform extent coordinates to template spatial reference")
                            #params["Error"] = "We ran into problems converting projected coordinates to template for " +  rasterFile
                    try:
                        geographic = osr.SpatialReference()
                        geographic.ImportFromEPSG(4326)
                        params["gWest"], params["gNorth"] = self.transformPoint(params["west"], params["north"], params["srs"], geographic)
                        params["gEast"], params["gSouth"] = self.transformPoint(params["east"], params["south"], params["srs"], geographic)
                    except:
                        pass
                    
            except:
                #print "We ran into problems getting the projection information for " +  rasterFile
                params["Error"].append("Undefined problems extracting the projection information")
                
            try:
                params["signedByte"] = dataset.GetRasterBand(1).GetMetadata('IMAGE_STRUCTURE')['PIXELTYPE'] == 'SIGNEDBYTE'
            except KeyError:
                params["signedByte"] = False
            
            params["NoData"] = dataset.GetRasterBand(1).GetNoDataValue()
            if params["NoData"] == None:
                if dataset.GetRasterBand(1).DataType == 1:
                    print "Warning:  Could not extract NoData value.  Using assumed nodata value of 255"
                    params["NoData"] = 255
                elif dataset.GetRasterBand(1).DataType == 2:
                    print "Warning:  Could not extract NoData value.  Using assumed nodata value of 65536"
                    params["NoData"] = 65536
                elif dataset.GetRasterBand(1).DataType == 3:
                    print "Warning:  Could not extract NoData value.  Using assumed nodata value of 32767"
                    params["NoData"] = 32767
                elif dataset.GetRasterBand(1).DataType == 4:
                    print "Warning:  Could not extract NoData value.  Using assumed nodata value of 2147483647"
                    params["NoData"] = 2147483647
                elif dataset.GetRasterBand(1).DataType == 5:
                    print "Warning:  Could not extract NoData value.  Using assumed nodata value of 2147483647"
                    params["NoData"] = 2147483647
                elif dataset.GetRasterBand(1).DataType == 6:
                    print "Warning:  Could not extract NoData value.  Using assumed nodata value of -3.40282346639e+038"
                    params["NoData"] = -3.40282346639e+038
                else:
                    params["Error"].append("Could not identify nodata value")
            params["PixelType"] = dataset.GetRasterBand(1).DataType
            if params["PixelType"] == None:
                params["Error"].append("Could not identify pixel type (bit depth)")
            
        except:
            #print "We ran into problems extracting raster parameters from " + rasterFile
            params["Error"].append("Some untrapped error was encountered")
        finally:
            del dataset
            return params

    def transformPoint(self, x, y, from_srs, to_srs):
        """
        Transforms a point from one srs to another
        """
        coordXform = osr.CoordinateTransformation(from_srs, to_srs)
        yRound = round(y, 4)
        xRound = round(x, 4)

        result = coordXform.TransformPoint(xRound, yRound)
        
        gx = result[0]
        gy = result[1]

        return gx, gy
        
    def ImageCoversTemplate(self, sourceParams):
        """
        Checks to see if the template images 
        falls completely inside the source raster
        
        it does this by generating a list of 16 coordinate
        pairs equally distributed across the template,
        including the four absolute corners.  
        These points are in the CRS of the image.
        If all of these points have a valid data or nodata
        value in the image, then the image covers the template.
        (in nearly every case anyway)
        """
        
        n = 5
        xOffset = (self.template_params["east"] - self.template_params["west"]) / (n) - \
                    ((self.template_params["east"] - self.template_params["west"]) / self.template_params["width"] / 1000)
        yOffset = (self.template_params["north"] - self.template_params["south"]) / (n) - \
                    ((self.template_params["north"] - self.template_params["south"]) / self.template_params["height"] / 1000)
        curX = self.template_params["west"]
        curY = self.template_params["north"]
        testPoints =[]
        
        for x in range(n + 1):
            for y in range(n + 1):
                testPoints.append(self.transformPoint(curX, curY, self.template_params["srs"], 
                                                    sourceParams["srs"]))
                curY -= yOffset
                
            curX += xOffset
            curY = self.template_params["north"]  
                
        rasterDS = gdal.Open(sourceParams["file_name"], gdalconst.GA_ReadOnly)
        band = rasterDS.GetRasterBand(1)
        badPoint = False        
        for point in testPoints:
            try:
                xOffset = int((point[0] - sourceParams["west"]) / sourceParams["xScale"])
                yOffset = int((point[1] - sourceParams["north"]) / sourceParams["yScale"])
                data = band.ReadAsArray(xOffset, yOffset, 1, 1)
                value = data[0,0]
            except:
                badPoint = True
        
        #if valid values were returned from each of our points then
        #the template falls entirely within the Source image.
        if badPoint:
            return False
        else:
            return True
        

    def validateArgs(self):
        """
        Make sure the user sent us some stuff we can work with
        """

        if not os.path.exists(self.out_dir):
            raise utilities.TrappedError("Specified Output directory " + self.out_dir + " not found on file system")
        
        if not os.path.isdir(self.out_dir):
            raise utilities.TrappedError("Specified Output directory " + self.out_dir + " is not a directory")
     
        if self.logger is None:
            self.logger = utilities.logger(self.out_dir, self.verbose)
        self.writetolog = self.logger.writetolog

        # Validate template image.
        if self.template is None:
            raise utilities.TrappedError("template raster not provided.")
        
        if not os.path.exists(self.template):
            raise utilities.TrappedError("Template file, " + self.template + ", does not exist on file system")

        self.template_params = self.getRasterParams(self.template)
        if len(self.template_params["Error"]) <> 0:
            raise utilities.TrappedError("There was a problem with the provided template: \n    " + 
                                    "    " + "\n    ".join(self.template_params["Error"]))
        
        # Ensure the template has square pixels.
        if abs(abs(self.template_params["xScale"]) - abs(self.template_params["yScale"])) > 1e-6:
            raise utilities.TrappedError("template image must have square pixels." + 
                            "/n    x pixel scale = " + str(xScale) +
                            "/n    y pixel scale = " + str(yScale))

        
        #Validate input rasters
        if not os.path.exists(self.inputs_CSV):
            raise utilities.TrappedError("Inputs CSV, " + self.inputs_CSV + ", does not exist on file system.")
        
        inputsCSV = csv.reader(open(self.inputs_CSV, 'r'))
        header = inputsCSV.next()
        strInputFileErrors = ""

        outputCSV = os.path.join(self.out_dir, "PARC_Files.csv")
        output = csv.writer(open(outputCSV, "wb"))
        output.writerow(["PARCOutputFile", "Categorical", "Resampling", "Aggregation", "OriginalFile", os.path.abspath(self.template), os.path.abspath(self.out_dir)])
        
        for row in inputsCSV:
            inputFile = row[0]
            sourceParams = self.getRasterParams(inputFile)
            if len(sourceParams["Error"]) > 0:
                strInputFileErrors += ("  " + os.path.split(inputFile)[1] + " had the following errors:\n" + 
                                    "    " + "\n    ".join(sourceParams["Error"])) + "\n"
            else:
                pass
                if not self.ImageCoversTemplate(sourceParams):
                    strInputFileErrors += ("\n  Some part of the template image falls outside of " + os.path.split(inputFile)[1])
                    strInputFileErrors += "\n        template upper left  = (" + str(self.template_params["gWest"]) + ", " + str(self.template_params["gNorth"]) + ")"
                    strInputFileErrors += "\n        template lower right = (" + str(self.template_params["gEast"]) + ", " + str(self.template_params["gSouth"]) + ")"
                    strInputFileErrors += "\n        image    upper left  = (" + str(sourceParams["gWest"]) + ", " + str(sourceParams["gNorth"]) + ")"
                    strInputFileErrors += "\n        image    lower right = (" + str(sourceParams["gEast"]) + ", " + str(sourceParams["gSouth"]) + ")"
#                    strInputFileErrors += "\n        points are given in projected coordinates."
#                    strInputFileErrors += "\n        template upper left  = (" + str(self.template_params["tWest"]) + ", " + str(self.template_params["tNorth"]) + ")"
#                    strInputFileErrors += "\n        template lower right = (" + str(self.template_params["tEast"]) + ", " + str(self.template_params["tSouth"]) + ")"
#                    strInputFileErrors += "\n        image    upper left  = (" + str(sourceParams["tWest"]) + ", " + str(sourceParams["tNorth"]) + ")"
#                    strInputFileErrors += "\n        image    lower right = (" + str(sourceParams["tEast"]) + ", " + str(sourceParams["tSouth"]) + ")"
#                    strInputFileErrors += "\n        Note: points are given in the template coordinates." + "\n"
#            
            if len(row) < 2 or not row[1] in ['0', '1']:
                self.writetolog("  " + os.path.split(inputFile)[1] + " categorical either missing or not 0 or 1:\n   Defaulting to 0 (continuous)")
                if len(row) < 2:
                    row.append('0')
                else:
                    row[1] = '0'
                 
            if len(row) < 3 or not row[2].lower() in [item.lower() for item in self.resample_methods]:
                 self.writetolog("  " + os.path.split(inputFile)[1] + " resample method either missing or not one of " + 
                                        ", ".join(self.resample_methods) + "\n  Defaulting to 'Bilinear'")                  
                 
                 if row[1] == '0':
                     default = 'Bilinear'
                 else:
                     default = 'NearestNeighbor'
                 if len(row) < 3:
                     row.append(default)
                 else:
                     row[2] = default

            if len(row) < 4 or not row[3].lower() in [item.lower() for item in self.agg_methods]:
                 self.writetolog("  " + os.path.split(inputFile)[1] + " aggregation method either missing or not one of " + 
                                        ", ".join(self.agg_methods) + "\n  Defaulting to 'Mean'")
                 if row[1] == '0':
                     default = 'Mean'
                 else:
                     default = 'Majority'
                 if len(row) < 4:
                     row.append(default)
                 else:
                     row[3] = default
                 
            self.inputs.append(row)
            #also write the output row, reconfigured to our output file
            fileName = self.getShortName(row[0])
            fileName = os.path.abspath(os.path.join(self.out_dir, fileName + ".tif"))
            outputrow = [fileName] + row[1:4] + [os.path.abspath(row[0]), os.path.abspath(self.out_dir)]
            output.writerow(outputrow)
        del output
        
        if strInputFileErrors <> "":
            self.writetolog(strInputFileErrors)
            raise utilities.TrappedError("There was one or more problems with your input rasters: \n" + strInputFileErrors)

    def reprojectRaster(self, srcDs, sourceParams, templateParams, 
                    destFile, resamplingType, shortName='', outputCellSize = None):
        """
        Reprojects a raster to match the template_params
        if outputCellSize is not provided defaults to the template cellSize
        """
#        driver = gdal.GetDriverByName("AAIGrid")
#        driver.Register()
        
        tmpOutput = os.path.splitext(destFile)[0] + ".tif"
        
        tmpOutDataset = self.generateOutputDS(sourceParams, templateParams, tmpOutput, outputCellSize)
        
        self.writetolog("    Starting intermediate reprojection of: " + shortName)

        err = gdal.ReprojectImage(srcDs, tmpOutDataset, sourceParams["srs"].ExportToWkt(), 
                                templateParams["srs"].ExportToWkt(), resamplingType)
        
#        dst_ds = driver.CreateCopy(destFile, tmpOutDataset, 0)
        self.writetolog("    Finished reprojection " + shortName)
        dst_ds = None
        tmpOutDataset = None
        
    def generateOutputDS(self, sourceParams, templateParams, 
                        tmpOutput, outputCellSize = None):
        """
        Creates an output dataset (tiff format) that
          has the nodata value of the sourceParams but
          all other attributes from the template_params
        This output is saved to tmpOutput.
        
        The optional cell size will override the cell size 
            specified in the template_params
        """
        tifDriver = gdal.GetDriverByName("GTiff")
        
        if outputCellSize == None:
            width = templateParams["width"]
            height = templateParams["height"]
        else:
            width = templateParams["width"] * int(templateParams["xScale"]/outputCellSize)
            height = templateParams["height"] * int(templateParams["xScale"]/outputCellSize)
        
        if sourceParams["signedByte"]: 
            tmpOutDataset = tifDriver.Create(tmpOutput, 
                                            width,
                                            height,
                                            1, sourceParams["PixelType"], ["PIXELTYPE=SIGNEDBYTE"])
        else:
            tmpOutDataset = tifDriver.Create(tmpOutput, 
                                            width,
                                            height,
                                            1, sourceParams["PixelType"])
        
            
        if outputCellSize == None:
            outputCellSize = templateParams["xScale"]
        gtList = list(templateParams["gt"])
        if templateParams["xScale"] < 0:
            gtList[1] = -1 * outputCellSize
        else:
            gtList[1] = outputCellSize
        if templateParams["yScale"] < 0:
            gtList[5] = -1 * outputCellSize
        else:
            gtList[5] = outputCellSize
        gt = tuple(gtList)
        
        tmpOutDataset.SetGeoTransform(gt)
        tmpOutDataset.SetProjection(templateParams["prj"])
        tmpOutDataset.GetRasterBand(1).SetNoDataValue(sourceParams["NoData"])
        if sourceParams["signedByte"]:
            #tmpOutDataset.GetRasterBand(1).SetMetadataItem('PIXELTYPE', "SIGNEDBYTE")
            tmpOutDataset.GetRasterBand(1).PixelType = "SIGNEDBYTE"
            tmpOutDataset.GetRasterBand(1).SetMetadata({'PIXELTYPE': 'SIGNEDBYTE'}, 'IMAGE_STRUCTURE')
            
#        if self.verbose:
#            print tmpOutput
#            print "noDataValue = ", tmpOutDataset.GetRasterBand(1).GetNoDataValue()
#            print "Pixel type = ", gdal.GetDataTypeName(tmpOutDataset.GetRasterBand(1).DataType)
        return tmpOutDataset

    def getShortName(self, fullPathName):
        if fullPathName.endswith('hdr.adf'):
            shortname = os.path.split(fullPathName)[0]
            shortname = os.path.split(shortname)[1]
        else:
            shortname = os.path.split(fullPathName)[1]
            shortname = os.path.splitext(shortname)[0]
        return shortname
    
if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
#    try:
##        PARC().testing()
#        sys.exit(PARC().main(sys.argv[1:]))
#    except Exception as e:
#        print e
#        sys.exit(1)

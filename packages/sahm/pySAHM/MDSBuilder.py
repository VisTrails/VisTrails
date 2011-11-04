'''
Created on Jan 31, 2011

This module creates a Merged Data Set (MDS)
from an input CSV and directory 
or list of rasters. The MDS consists of three
header lines 1st is a x, y, ResponseBinary, 
{other info fields}, then a list of raster covariates.
The next header line contains ones and zeros for each of the 
raster covariates and indicates if the covariate is to be 
used in subsequent analyses.  The last header line contains
the full network path the raster dataset for that covariate.
After the header lines comes the data which is the 
covariate values pulled from the raster cell 
with those coordinates. 

@author: talbertc

'''

import sys
import csv
import os
import time
import random
import shutil

from osgeo import gdalconst
from osgeo import gdal

from optparse import OptionParser
import utilities
#from Utilities import self.writetolog

class MDSBuilder(object):
    '''Takes a csv with animal location x,y and attributes each with the values 
    extracted from each of the grids (covariates) indicated in the supplied 
    csv list of files
    '''
    def __init__(self):
        #instance level variables
        self.verbose = False
        self.inputsCSV = ''
        self.inputs = []
        self.fieldData = ''
        self.outputMDS  = ''
        self.probsurf = ''
        self.pointcount = 0
        self.NDFlag = -9999
        self.deleteTmp = False
        self.logger = None
    
    def validateArgs(self):
        #check our CSV file for expectations
        if not os.path.exists(self.fieldData):
            raise RuntimeError, "Could not find CSV file of fieldData provided.  Please check input file: " + str(self.fieldData)
         
        if not os.path.exists(self.inputsCSV):
            raise RuntimeError, "Could not find CSV file of inputs provided.  Please check input file: " + str(self.inputsCSV) 
        
        #check the input CSV file of inputs
        reader = csv.reader(open(self.inputsCSV, 'r'))
        header = reader.next()
        missingfiles = []
        for row in reader:
            if not self.isRaster(row[0]):
                missingfiles.append(row[0])
        if not len(missingfiles) ==0:
            msg = "One or more of the files in the input covariate list CSV could not be identified as rasters by GDAL."
            msg += "\n    ".join(missingfiles)
            raise RuntimeError, msg
            
        if self.probsurf <> '':
            if not self.isRaster(self.probsurf):
                raise RuntimeError, "The supplied probability surface, " + self.probsurf + ", does not appear to be a valid raster."
        
        try:
            self.pointcount = int(self.pointcount)
        except:
            raise RuntimeError, "The supplied point count parameter, " + self.pointcount +", does not appear to be an integer"
        
        #make sure the directory the mds file is going into exists:
        outDir = os.path.split(self.outputMDS)[0]
        if not os.path.exists(outDir):
            raise RuntimeError, "The directory of the supplied MDS output file path, " + self.outputMDS +", does not appear to exist on the filesystem"
        
        if self.logger is None:
            self.logger = utilities.logger(outDir, self.verbose)  
        self.writetolog = self.logger.writetolog
            
    def run(self):
        '''
        This routine loops through a set of rasters and creates an MDS file
        '''
        
        self.validateArgs()
        self.writetolog('\nRunning MDSBuilder', True, True)
        # start timing
        startTime = time.time()
        gdal.UseExceptions()
        gdal.AllRegister()
        
        self.constructEmptyMDS()
        
        if self.pointcount <> 0:
            self.addBackgroundPoints()
        
        outputRows = self.readInPoints()
        
        #loop though each of the supplied rasters and add the 
        #extracted values to
        for input in self.inputs:
            inputND = self.getND(input)
            rasterDS = gdal.Open(input, gdalconst.GA_ReadOnly)
            # get image size
            rows = rasterDS.RasterYSize
            cols = rasterDS.RasterXSize
            band = rasterDS.GetRasterBand(1)
            # get georeference info
            transform = rasterDS.GetGeoTransform()
            xOrigin = transform[0]
            yOrigin = transform[3]
            pixelWidth = transform[1]
            pixelHeight = transform[5]
            
            if self.verbose:
                self.writetolog("    Extracting raster values for " + input)
                print "    ",
            
            pcntDone = 0
            i = 1
            badpoints = []
            for row in outputRows:
                x = float(row[0])
                y = float(row[1])
                # compute pixel offset
                xOffset = int((x - xOrigin) / pixelWidth)
                yOffset = int((y - yOrigin) / pixelHeight)
#                try:
                if xOffset < 0 or yOffset < 0:
                    if row[:3] not in badpoints:
                        badpoints.append(row[:3])
                    row.append(str(self.NDFlag))
                else:
                    try:
                        data = band.ReadAsArray(xOffset, yOffset, 1, 1)
                        value = data[0,0]
                        if value <> inputND:
                            row.append(value)
                        else:
                            row.append(str(self.NDFlag))
                    except:
                        badpoints.append(row[:3])
                        row.append(str(self.NDFlag))
                
                if self.verbose:
                    if i/float(len(outputRows)) > float(pcntDone)/100:
                        pcntDone += 10
                        print str(pcntDone) + "...",
                i += 1
            if self.verbose:
                self.writetolog("    Done")
        if len(badpoints) > 0:
                msg =  "\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
                msg += "\n!!!!!!!!!!!!!!!!!!!!!WARNING!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n"
                msg += str(len(badpoints)) + " point fell outside the Covariate coverage."
                msg += "\nThese points were assigned the NoData value of -9999 for all covariates and will"
                msg += "not be included in subsequent models.\n     These points are:"
                for badpoint in badpoints:
                    msg += "     x:" + str(row[0]) + " Y: " + str(row[1]) + " response: " + str(row[2]) 
                self.writetolog(msg)
            
            
        outputMDS = csv.writer(open(self.outputMDS, 'ab'))
        thrownOut = 0
        kept = 0
        for row in outputRows:
            #remove this if when Marian handles the ND   
            if not str(self.NDFlag) in row[3:]:
                outputMDS.writerow(row)
                kept += 1
            else:
                outputMDS.writerow(row)
                thrownOut += 1
        if thrownOut > 0:
            msg =  "\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
            msg += "\n!!!!!!!!!!!!!!!!!!!!!WARNING!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n"
            msg += str(thrownOut) + " points had 'nodata' in at least one of the covariates."
            msg += "\nThese points will not be considered in subsequent Models."
            msg +=  "\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
            msg +=  "\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
            self.writetolog(msg)
        del outputMDS
        
        #convert the mds csv to a shapefile
        output_shp = self.outputMDS.replace(".csv", ".mds")
        utilities.mds_to_shape(self.outputMDS, output_shp)
        
        # figure out how long the script took to run
        endTime = time.time()
        
        if self.deleteTmp:
            #if this flag is trud the field data we're working with is 
            # a temporary copy which we created so that we could add
            # background points.  Delete it to clean up our working file.
            os.remove(self.fieldData)
        
        if self.verbose:
            self.writetolog('Finished running MDSBuilder', True, True)
            self.writetolog('    The process took ' + str(endTime - startTime) + ' seconds')
        
    def constructEmptyMDS(self):
        '''Creates the triple header line format of our output file.
        Also parses the inputs file to append the '_categorical' flag 
        to the covariate names of all categorical inputs.
        '''        
        
        field_data_CSV = csv.reader(open(self.fieldData, "r"))
        orig_header = field_data_CSV.next()
        full_header = ["x", "y"]
        if orig_header[2].lower not in ["responsebinary", "responsecount"]:
            #inputs not conforming to our expected format will be assumed
            #to be binary data
            full_header.append("responseBinary")
        else:
            full_header.append(orig_header[2])
        
        inputs_CSV = csv.reader(open(self.inputsCSV, "r"))
        inputs_header = inputs_CSV.next()
        self.inputs = []

        #each row contains a covariate raster layer
        #item 0 is the full path to the file
        #item 1 is 0/1 indicating categorical
        #Construct our output header by extracting each individual 
        #file (raster) name and appending '_categorical' if the flag is 1
        rasters = {}
        for row in inputs_CSV:
            temp_raster = row[0]
#            self.inputs.append(temp_raster)
            raster_shortname = os.path.split(temp_raster)[1]
            raster_shortname = os.path.splitext(raster_shortname)[0]
            if len(row) > 1 and row[1] == '1':
                raster_shortname += "_categorical"
            rasters[raster_shortname] = temp_raster
            
        keys = rasters.keys()
        keys.sort(key=lambda s: s.lower())
        keys.sort(key=lambda s: s.lower())
        for key in keys:
            self.inputs.append(rasters[key])
            full_header.append(key)

        #Open up and write to an output file
        oFile = open(self.outputMDS, 'wb')
        fOut = csv.writer(oFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        
        #Format and write out our three header lines
        #    the original template, fieldData, and parc folder are 
        #    stored in spots 1,2,3 in the second header line
        if len(orig_header) > 7 and os.path.exists(orig_header[7]):
            #The input is an output from Field data query
            original_field_data = orig_header[7]
            field_data_template = orig_header[8]
        else:
            #The input is a raw field data file
            original_field_data = self.fieldData
            field_data_template = "NA"
        
        if len(inputs_header) > 5:
            parc_template = inputs_header[5]
            parc_workspace = inputs_header[6]
        else:
            parc_template = "Unknown"
            parc_workspace = "Unknown"
        
        secondRow = [original_field_data, field_data_template, ""] + ["1" for elem in self.inputs]
        thirdRow = [parc_template, parc_workspace, ""] + self.inputs
        fOut.writerow(full_header)
        fOut.writerow(secondRow)
        fOut.writerow(thirdRow)
        oFile.close()
        del fOut
    
    def readInPoints(self):
        '''Loop through each row in our field data and add the X, Y, response
        to our in memory list of rows to write to our output MDS file
        '''
        fieldDataCSV = csv.reader(open(self.fieldData, "r"))
        origHeader = fieldDataCSV.next()
        points = []
        for row in fieldDataCSV:
            points.append(row[:3])
            
        del fieldDataCSV
        return points
    
    def addBackgroundPoints(self):
        '''Add pointcount number of points to the supplied field data
        If a probability surface was provided the distribution will 
        follow this otherwise it will be uniform within the extent of the first of our inputs.
        No more than one per pixel is used.
        '''
        #First we'll create a temp copy of the Field Data to work with.
        shutil.copy(self.fieldData, self.fieldData + ".tmp.csv")
        self.fieldData = self.fieldData + ".tmp.csv"
        self.deleteTmp = True
        
        if self.probsurf <> '':
            rasterDS = gdal.Open(self.probsurf, gdalconst.GA_ReadOnly)
            useProbSurf = True
        else:
            print self.inputs[0]
            rasterDS = gdal.Open(self.inputs[0], gdalconst.GA_ReadOnly)
            useProbSurf = False
            
        # get image size
        rows = rasterDS.RasterYSize
        cols = rasterDS.RasterXSize
        band = rasterDS.GetRasterBand(1)
        # get georeference info
        transform = rasterDS.GetGeoTransform()
        xOrigin = transform[0]
        yOrigin = transform[3]
        pixelWidth = transform[1]
        pixelHeight = transform[5]
        xRange = [xOrigin, xOrigin * pixelWidth * cols]
        yRange = [yOrigin, yOrigin * pixelHeight * rows]
        
        #Open up and write to an output file
        oFile = open(self.fieldData, 'ab')
        fOut = csv.writer(oFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        
        
        if self.verbose:
            self.writetolog('    Starting generation of ' + str(self.pointcount) + ' random background points, ')
            if self.probsurf <> '':
                self.writetolog('      using ' + self.probsurf + ' as the probability surface.')
            print "    Percent Done:    ",
        
        foundPoints = 0 # The running count of how many we've found
        pcntDone = 0 #for status bar
        while foundPoints < self.pointcount: #loop until we find enough
            x = random.randint(0, cols - 1) 
            y = random.randint(0, rows - 1)
            #print x, y
            tmpPixel = [x, y, -9999] # a random pixel in the entire image
            if useProbSurf:
                # if they supplied a probability surface ignore the random pixel
                # if a random number between 1 and 100 is > the probability surface value
                pixelProb = int(band.ReadAsArray(tmpPixel[0], tmpPixel[1], 1, 1)[0,0])
                #pixelProb is the extracted probability from the probability surface
                rand = random.randint(1,100)
                #rand is a uniform random integer between 1 and 100 inclusive
                if rand > pixelProb:
                    continue
                    #don't record this pixel in our output file 
                    #because our rand number was lower (or equal) than that pixel's probability
                    
            #convert our outValues for row, col to coordinates
            tmpPixel[0] = xOrigin + tmpPixel[0] * pixelWidth
            tmpPixel[1] = yOrigin + tmpPixel[1] * pixelHeight
            
            fOut.writerow(tmpPixel)
            foundPoints += 1
            if self.verbose:
                if float(foundPoints)/self.pointcount > float(pcntDone)/100:
                    pcntDone += 10
                    print str(pcntDone) + "...",
        print "Done!\n"
        oFile.close()
        del fOut
    
    def getRasters(self, directory):
        #the list of rasters in the given directory
        rasters = []
        dirList = os.listdir(directory)
        for file in [elem for elem in dirList if elem[-4:].lower() == ".tif"]:
            if isRaster(os.path.join(directory, file)):
                rasters.append(os.path.join(directory, file))
        for file in [elem for elem in dirList if elem[-4:].lower() == ".asc"]:
            if isRaster(os.path.join(directory,file)):
                rasters.append(os.path.join(directory, file))
        for folder in [name for name in dirList if os.path.isdir(os.path.join(directory, name)) ]:
            if isRaster(os.path.join(directory, folder)):
                rasters.append(os.path.join(directory, folder))
    
        return rasters
    
    def isRaster(self, filePath):
        '''Verifies that a pased file and path is recognized by
        GDAL as a raster file.
        '''
        try:
            dataset = gdal.Open(filePath, gdalconst.GA_ReadOnly)
            if dataset is None:
                return False
            else:
                return True
                del dataset
        except:
            return False
        
    def getND(self, raster):
        dataset = gdal.Open(raster, gdalconst.GA_ReadOnly)
        ND = dataset.GetRasterBand(1).GetNoDataValue()
        if ND is None:
            if dataset.GetRasterBand(1).DataType == 1:
                print "Warning:  Could not extract NoData value.  Using assumed nodata value of 255"
                return 255
            elif dataset.GetRasterBand(1).DataType == 2:
                print "Warning:  Could not extract NoData value.  Using assumed nodata value of 65536"
                return 65536
            elif dataset.GetRasterBand(1).DataType == 3:
                print "Warning:  Could not extract NoData value.  Using assumed nodata value of 32767"
                return 32767
            elif dataset.GetRasterBand(1).DataType == 4:
                print "Warning:  Could not extract NoData value.  Using assumed nodata value of 2147483647"
                return 2147483647
            elif dataset.GetRasterBand(1).DataType == 5:
                print "Warning:  Could not extract NoData value.  Using assumed nodata value of 2147483647"
                return 2147483647
            elif dataset.GetRasterBand(1).DataType == 6:
                print "Warning:  Could not extract NoData value.  Using assumed nodata value of -3.40282346639e+038"
                return -3.40282346639e+038
            else:
                return None
        else:
            return ND

def main(argv):
    
    usageStmt = "usage:  options: -f --fieldData -i --inCSV -o --output -pc --pointcount -ps --probsurf"
    desc = "Creates a merged dataset file (mds) from a csv of field points and rasters located in a csv listing one raster per line.  Optionally this module adds a number of background points to the output."
    parser = OptionParser(usage=usageStmt, description=desc)
    
    parser.add_option("-v", 
                      dest="verbose", 
                      default=False, 
                      action="store_true", 
                      help="the verbose flag causes diagnostic output to print")
    parser.add_option("-f", "--fieldData", 
                      dest="fieldData", 
                      help="The input CSV of field data points")
    parser.add_option("-i", "--inCSV", 
                      dest="inputsCSV", 
                      help="The input CSV containing a list of our inputs, one per line.")              
    parser.add_option("-o", "--output", 
                      dest="outputMDS", 
                      help="Output MDS file to save to.")
    parser.add_option("-p", "--probsurf", 
                      dest="probsurf",
                      default='', 
                      help="Probability surface to use for generation of background points (optional)")
    parser.add_option("-c", "--pointcount", 
                      dest="pointcount",
                      default=0, 
                      help="Number of random background points to add(optional)")
    
    (options, args) = parser.parse_args(argv)
    
    ourMDS = MDSBuilder()
    ourMDS.verbose = options.verbose
    ourMDS.fieldData = options.fieldData
    ourMDS.inputsCSV = options.inputsCSV
    ourMDS.probsurf = options.probsurf
    ourMDS.pointcount = options.pointcount
    ourMDS.outputMDS = options.outputMDS
    ourMDS.run()
   

if __name__ == '__main__':
    sys.exit(main(sys.argv))
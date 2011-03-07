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

from osgeo import gdalconst
from osgeo import gdal

from optparse import OptionParser

def run(argv):
    usageStmt = "usage:  options: -f --fieldData -d --inDir -r --rasters -o --output"
    desc = "Creates a merged dataset file (mds) from a csv of field points and rasters located in a given directory or set of files."
    parser = OptionParser(usage=usageStmt, description=desc)
    
    parser.add_option("-f", "--fieldData", 
                      dest="fieldData", 
                      help="The input CSV of field data points")
    parser.add_option("-d", "--inDir", 
                      dest="inDir", 
                      help="The folder containing our inputs.")              
    parser.add_option("-r", "--rasters", 
                      dest="rast", 
                      help="Comma separated list of rasters to include.")
    parser.add_option("-o", "--output", 
                      dest="output", 
                      help="Output file to save to.")
    
    (options, args) = parser.parse_args(argv)
    
    validateArgs(args, options)
    
    MDSFile(options.fieldData, 
            options.inDir,
            options.rast,
            options.output)

def validateArgs(args, options):
    #check our CSV file for expectations
    try:
        csvfile = open(options.fieldData, "r")
        reader = csv.reader(csvfile)
        header = reader.next()
        if not header[0].lower() == "x" and \
            header[1].lower() == "y" and \
            len(header) >= 3:
            print "Invalid CSV of fieldData provided.  Please check input file: " + str(options.fieldData)
            raise RuntimeError
        del reader
        csvfile.close()
    except:
        print "Invalid CSV of fieldData provided.  Please check input file: " + str(options.fieldData)
        raise RuntimeError       
        
    #check for a valid indirectory or rast input parameter
    try:
        if options.inDir:
            if not os.path.isdir(options.inDir):
                print "There is a problem with the directory passed.  Please check input directory: " + str(options.inDir)
                raise RuntimeError
        elif options.rast:
            pass #we will assume that the rast variable passed is ok.  This will be fully check during runtime
        else:
            if not options.inDir and not options.rast:
                print "Neither an input directory or list of rasters was provided.  Please check inputs."
                raise RuntimeError
    except:
        print "There is some problem with the directory or raster list passed.  Please check inputs."
        raise RuntimeError   

    
def MDSFile(fieldDataCSV, dir, rasters, output):
    '''
    This routine loops through a set of rasters and creates an MDS file
    '''
    
    # start timing
    startTime = time.time()
    
    csvfile = open(fieldDataCSV, "r")
    reader = csv.reader(csvfile)
    origHeader = reader.next()
    fullHeader = []
    fullHeader = ["x", "y", "ResponseBinary"]
    #fullHeader.extend(origHeader)
    
    inputs = []
    # register all of the drivers
    gdal.AllRegister()
    
    if rasters:
        rasters_tmp = str.split(rasters,",")
        for raster in rasters_tmp:
            if isRaster(raster.rstrip()):
                inputs.append(raster.rstrip())
    if dir:
        rasters_tmp = getRasters(dir)
        for raster in rasters_tmp:
            inputs.append(raster.rstrip())
            rasterShortName = os.path.split(raster)[1]
            rasterShortName = os.path.splitext(rasterShortName)[0]
            fullHeader.append(rasterShortName)

    #Open up and write to an output file
    oFile = open(output, 'wb')
    fOut = csv.writer(oFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    
    #Format and write out our three header lines
    secondRow = ["0" for elem in ["x", "y", "ResponseBinary"]] + ["1" for elem in inputs]
    thirdRow = ["" for elem in ["x", "y", "ResponseBinary"]] + inputs
    fOut.writerow(fullHeader)
    fOut.writerow(secondRow)
    fOut.writerow(thirdRow)

    #loop through each xy in our field data and pull the points from each of our inputs.
    outputRows = []
    for row in reader:
        outputRows.append(row[:3])
    
    for input in inputs:
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
        
        print "Starting on " + input
        
        for row in outputRows:
            #print row[0], row[1]
            # get x,y
            x = float(row[0])
            y = float(row[1])
            # compute pixel offset
            xOffset = int((x - xOrigin) / pixelWidth)
            yOffset = int((y - yOrigin) / pixelHeight)
            data = band.ReadAsArray(xOffset, yOffset, 1, 1)
            

            value = data[0,0]
            row.append(value)
            #print value
        
    for row in outputRows:   
        fOut.writerow(row)
    oFile.close
    # figure out how long the script took to run
    endTime = time.time()
    print 'The script took ' + str(endTime - startTime) + ' seconds'
    print "Done"
    


def getRasters(directory):
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

def isRaster(filePath):
    try:
        dataset = gdal.Open(filePath, gdalconst.GA_ReadOnly)
        if dataset is None:
            return False
        else:
            return True
            del dataset
    except:
        return False
     


if __name__ == '__main__':
    sys.exit(run(sys.argv))
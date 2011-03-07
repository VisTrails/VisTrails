'''
Created on Dec 29, 2010

This module was created to 

@author: talbertc
'''

import sys
import math
import csv

from osgeo import gdalconst
from osgeo import gdal
from osgeo import osr
from math import floor

from optparse import OptionParser


def run(argv):
   
    usageStmt = "usage:  options: -t --template   -f --fieldData -a --aggPixel -y --aggYears -o --output"
    desc = "Aggregates sample points by pixel and/or year."

    parser = OptionParser(usage=usageStmt, description=desc)
    parser.add_option("-t", "--template", 
                      dest="template", 
                      help="The template grid in Tif, ESRI grid, or ASC format")
    parser.add_option("-f", "--fieldData", 
                      dest="csv", 
                      help="The CSV of field data")
    parser.add_option("-o", "--output", 
                      dest="output", 
                      help="The output CSV file with appended frequency and numPresence")
    parser.add_option("-p", "--aggregate", 
                      dest="bAgg", 
                      default=False, 
                      action="store_true", 
                      help="Flag to aggregate by pixel in the template")
    parser.add_option("-y", "--aggregateYears", 
                      dest="bAggYears", 
                      default=False, 
                      action="store_true", 
                      help="Flag to aggregate by years in the template")
    parser.add_option("-v", "--verbose", 
                      dest="verbose", 
                      default=False, 
                      action="store_true",
                      help="the verbose flag causes diagnostic output to print")

    (options, args) = parser.parse_args(argv)

    ulx, uly, lrx, lry, destEPSG, xScale, yScale = getTemplateParams(options.template, options.verbose)
    print ulx, uly, lrx, lry, destEPSG, xScale, yScale
    processCSV(options.csv, options.output, ulx, uly, lrx, lry, destEPSG, xScale, yScale, options.verbose)

def processCSV(fieldDataCSV, output, ulx, uly, lrx, lry, destEPSG, xScale, yScale, verbose):
    csvfile = open(fieldDataCSV, "r")
    #dialect = csv.Sniffer().sniff(csvfile.read(1024))
    reader = csv.reader(csvfile)
    usedPixels = {}
    reader.next()
    header = ["x", "y", "ResponseBinary"]
    
    #Commented this out because it is causing an error
    #to be thrown by the java, uncomment out when the 
    #java has been replaced
    header.append("frequency")
    header.append("numPresence")
    header.append("pixelColumn")
    header.append("pixelRow")

    #loop through each row (observation) and 
    #if that particular pixel hasn't been encountered before
    #add it to a dictionary containing a key of the pixel X,Y
    #and values of each row encountered for that pixel
    for row in reader:
        pixelColumn = int(floor((float(row[0]) - ulx) / xScale))
        pixelRow = int(floor((float(row[1]) - uly) / yScale))
        pixel = "".join(["X:",str(pixelColumn),":Y:",str(pixelRow)])
        #if verbose == True:
        if not pixel in usedPixels:
            usedPixels[pixel] = [row]
            #usedPixels[pixel] = usedPixels[pixel].append(row)
        else:
            curVal = usedPixels[pixel]
            curVal.append(row)
            usedPixels[pixel] = curVal

    #Open up and write to an output file
    oFile = open(output, 'wb')
    fOut = csv.writer(oFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    fOut.writerow(header)

    #Add each used pixel to the output file
    for k in usedPixels:
        v = usedPixels[k]
        outputLine = v[0]

        pixelColumn = int(k.rsplit(':')[1])
        pixelRow = int(k.rsplit(':')[3])
        outPixelX = ulx + (xScale * pixelColumn) + xScale/2
        outPixelY = uly + (yScale * pixelRow) + yScale/2
        frequency = len(v)

        numPresence = 0
        for i in range (frequency):
            if int(float(v[i][2])) == 1:
                numPresence += 1
        
        outputLine[0] = outPixelX
        outputLine[1] = outPixelY
        
        if numPresence == 0:
            outputLine[2] = 0
        else:
            outputLine[2] = 1
            
        outputLine.append(frequency)
        outputLine.append(numPresence)
        outputLine.append(pixelColumn)
        outputLine.append(pixelRow)
        

        fOut.writerow(outputLine)
    oFile.close
    print "Done"

def getTemplateParams(template, verbose):
    # Get the PARC parameters from the template.
    dataset = gdal.Open(template, gdalconst.GA_ReadOnly)
    
    if dataset is None:
        print "Unable to open " + template
        raise RuntimeError
    xform = dataset.GetGeoTransform()
    xScale = xform[1]
    yScale = xform[5]
    # Ensure the template has square pixels.
    if abs(math.fabs(xScale) - math.fabs(yScale)) > 1e-6:
        print "The template image must have square pixels."
        print "x pixel scale = " + str(math.fabs(xScale))
        print "y pixel scale = " + str(math.fabs(yScale))
        raise RuntimeError
    width = dataset.RasterXSize
    height = dataset.RasterYSize
    ulx = xform[0]
    uly = xform[3]
    lrx = ulx + width * xScale
    lry = uly + height * yScale
    if verbose == True:
        print "upper left = (" + str(ulx) + ", " + str(uly) + ")"
        print "lower right = (" + str(lrx) + ", " + str(lry) + ")"
    # Store the extent in geographic coordinates.
    tEPSG = getEPSG(dataset)
    if int(tEPSG) == 4326:
        tGeoUlX = ulx
        tGeoUlY = uly
        tGeoLrX = lrx
        tGeoLrY = lry
    else:
        tGeoUlX, tGeoUlY, tGeoLrX, tGeoLrY = getExtentInGeog(ulx, uly, lrx, lry, tEPSG)
    return ulx, uly, lrx, lry, getEPSG(dataset), xScale, yScale

def getEPSG(dataset):
    #Returns code for the projection/datum used in the layer
    wkt = dataset.GetProjection()
    s_srs = osr.SpatialReference(wkt)
    s_srs.AutoIdentifyEPSG()
    epsg = s_srs.GetAuthorityCode("PROJCS")
    if epsg == None:
        epsg = s_srs.GetAuthorityCode("GEOGCS")
    if epsg == None:
        print "Unable to extract the EPSG code from the image."
        raise RuntimeError
    return epsg

def getExtentInGeog(ulx, uly, lrx, lry, EPSG):
        
        s_srs = osr.SpatialReference()
        s_srs.ImportFromEPSG(int(EPSG))

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

if __name__ == '__main__':
    run(sys.argv)
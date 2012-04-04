#!/usr/bin/python
"""
This script is a wrapper for the
RasterFormatConverter which allows 
the user to run an individual raster through.
It is used by RasterFormatConverter itself
to allow each raster to be spawned off as 
a separate command line to take advantage of 
multiple cores on a machine.

"""


import glob
import math
import os
import shutil
import struct
import sys
import csv

from optparse import OptionParser
from multiprocessing import Process, Queue

from osgeo import gdalconst
from osgeo import gdal
from osgeo import osr

from numpy import *
import numpy as np

import utilities
from RasterFormatConverter import FormatConverter

def main(argv):
    usageStmt = "usage:  options: -m --MDSFile -o --outputDir -f --format -v --verbose"
    desc = "Converts all of the tif files specified in an MDS to ASCII format (or optionally other formats)"
    parser = OptionParser(usage=usageStmt, description=desc)
    
    parser.add_option("-v", 
                      dest="verbose", 
                      default=False, 
                      action="store_true", 
                      help="the verbose flag causes diagnostic output to print.")
    parser.add_option("-i", "--inputfile", 
                      dest="input", 
                      help="")           
    parser.add_option("-o", "--outputDir", 
                      dest="outputDir", 
                      help="Output directory to save files in.")
    parser.add_option("-f", "--format", 
                      dest="format",
                      default='asc', 
                      help="The format to convert into. 'bil', 'img', 'tif', 'jpg', 'bmp', 'asc'")
    
    (options, args) = parser.parse_args(argv)
    
    ourFC = FormatConverter()
    ourFC.verbose = options.verbose
    ourFC.logger = utilities.logger(options.outputDir, ourFC.verbose)
    ourFC.writetolog = ourFC.logger.writetolog
    ourFC.outputDir = options.outputDir
    ourFC.format = options.format
    ourFC.convertEnvironmentalLayers([options.input, ], options.outputDir, options.format)
    
if __name__ == "__main__":
    main(sys.argv[1:])
#    try:
##        PARC().testing()
#        sys.exit(PARC().main(sys.argv[1:]))
#    except Exception as e:
#        print e
#        sys.exit(1)

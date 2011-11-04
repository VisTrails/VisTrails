#!/usr/bin/python
"""
This was an experiment to explore breaking the
individual raster processes into individual
runs that could be either run on separate 
processes on the same computer with a command line
popopen perhaps or sent out individually to our 
Condor distributed computing cluster.

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
from PARC import PARC

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
    parser.add_option("-s", dest="source", help="print the names of all known aggregation methods")
    parser.add_option("-c", dest="categorical")
    parser.add_option("-d", dest="dest", default="./", help="directory in which to put processed images, defaults to current directory")
    parser.add_option("-v", dest="verbose", default=False, action="store_true", help="the verbose flag causes diagnostic output to print")
    parser.add_option("-t", dest="template", help="The template raster used for projection, origin, cell size and extent")
    parser.add_option("-r", dest="resampling", help="The CSV containing the list of files to process.  Format is 'FilePath, Categorical, Resampling, Aggreagtion")
    parser.add_option("-a", dest="aggregation", default=True, help="'True', 'False' indicating whether to use multiple cores or not") 
    (options, args) = parser.parse_args(args_in)
    
    ourPARC = PARC()
    ourPARC.verbose = options.verbose
    ourPARC.template = options.template
    outDir = os.path.split(options.dest)[0]
    ourPARC.outDir = outDir
    ourPARC.logger = utilities.logger(outDir, ourPARC.verbose)
    ourPARC.writetolog = ourPARC.logger.writetolog
    ourPARC.template_params = ourPARC.getRasterParams(options.template)
    ourPARC.parcFile([options.source, options.categorical, options.resampling, options.aggregation], options.dest)
    
if __name__ == "__main__":
    main(sys.argv[1:])
#    try:
##        PARC().testing()
#        sys.exit(PARC().main(sys.argv[1:]))
#    except Exception as e:
#        print e
#        sys.exit(1)

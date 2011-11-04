'''
These are utilites used by the VisTrails 
wrappers of the SAHM command line applications

@author: talbertc
test

'''
import os, sys, shutil
import traceback
import csv
import time
import tempfile
import subprocess

from PyQt4 import QtCore, QtGui

from core.modules.basic_modules import File, Path, Directory, new_constant, Constant
from core.modules.vistrails_module import ModuleError

from osgeo import gdalconst
from osgeo import gdal
from osgeo import osr
import numpy

import packages.sahm.pySAHM.utilities as utilities
import getpass

_roottempdir = ""
_logger = None
config = None

def getrasterminmax(filename):
    dataset = gdal.Open(filename, gdalconst.GA_ReadOnly)
    band = dataset.GetRasterBand(1)
    
    min = band.GetMinimum()
    max = band.GetMaximum()
    
    try:
        #our output rasters have approx nodata values
        #which don't equal the specified nodata.
        #set the specified to equal what is actually used.
        if (abs(band.GetNoDataValue() - band.GetMinimum()) < 1e-9 and 
            band.GetNoDataValue() <> band.GetMinimum()):
            band.SetNoDataValue(band.GetMinimum)
        
        if min is None or max is None:
            (min,max) = band.ComputeRasterMinMax(1)
        
    except:
        pass
    return (min, max)
    dataset = None

def mknextfile(prefix, suffix="", directory=""):
    global _roottempdir
    if directory == "":
        directory = _roottempdir
    files = os.listdir(directory)
    seq = 0
    for f in files:
        if f.startswith(prefix):
            old_seq = f.replace(prefix, '')
            old_seq = old_seq.replace(suffix, '')
            old_seq = old_seq.replace("_", '')
            if old_seq.isdigit():
                if int(old_seq) > seq:
                    seq = int(old_seq)
    seq += 1
    filename = prefix + str(seq) + suffix
    return os.path.join(directory, filename)

def mknextdir(prefix, directory=""):
    global _roottempdir
    if directory == "":
        directory = _roottempdir
    files = os.listdir(directory)
    seq = 0
    for f in files:
        if (f.startswith(prefix) and
            not os.path.isfile(f)):
            f_seq = int(f.replace(prefix, ''))
            if f_seq > seq:
                seq = f_seq
    seq += 1
    dirname = prefix + str(seq)
    os.mkdir(os.path.join(directory, dirname))
    return os.path.join(directory, dirname)

def setrootdir(session_dir):
    global _roottempdir
    _roottempdir = session_dir

def createrootdir(rootWorkspace):
    '''Creates a session Directory which will
    contain all of the output produced in a single
    VisTrails/Sahm session.
    '''
    global _roottempdir
    user_nospace = getpass.getuser().split(' ')[0]
    _roottempdir = os.path.join(rootWorkspace, user_nospace + '_' + time.strftime("%Y%m%dT%H%M%S"))
    if not os.path.exists(_roottempdir):
        os.makedirs(_roottempdir) 

    return _roottempdir

def map_ports(module, port_map):
    args = {}
    for port, (flag, access, required) in port_map.iteritems():
        if required or module.hasInputFromPort(port):
            #breakpoint()
            value = module.forceGetInputListFromPort(port)
            if len(value) > 1:
                raise ModuleError(module, 'Multiple items found from Port ' + 
                    port + '.  Only single entry handled.  Please remove extraneous items.')
            elif len(value)  == 0:
                raise ModuleError(module, 'Multiple items found from Port ' + 
                    port + '.  Only single entry handled.  Please remove extraneous items.')
            value = module.forceGetInputFromPort(port)
            if access is not None:
                value = access(value)
            if isinstance(value, File) or \
                        isinstance(value, Directory) or \
                        isinstance(value, Path):
                value = path_port(module, port)
            args[flag] = value
    return args

def path_port(module, portName):
    value = module.forceGetInputListFromPort(portName)
    if len(value) > 1:
        raise ModuleError(module, 'Multiple items found from Port ' + 
                          portName + '.  Only single entry handled.  Please remove extraneous items.')
    value = value[0]
    path = value.name 
    path.replace("/", os.path.sep)
    if os.path.exists(path):
        return path
    else:
        raise RuntimeError, 'The indicated file or directory, ' + \
            path + ', does not exist on the file system.  Cannot continue!'
    
def PySAHM_instance_params(instance, mappedPorts):
    global _logger
    instance.__dict__['logger'] = _logger
    instance.__dict__['verbose'] = _logger.verbose
    for k, v in mappedPorts.iteritems():
            instance.__dict__[k] = v
    
def R_boolean(value):
    if value:
        return 'TRUE'
    else:
        return 'FALSE'

def dir_path_value(value):
    val = value.name
    sep = os.path.sep
    return val.replace("/", sep)
    
def create_file_module(fname, f=None):
    if f is None:
        f = File()
    f.name = fname
    f.upToDate = True
    return f

def create_dir_module(dname, d=None):
    if d is None:
        d = Directory()
    d.name = dname
    d.upToDate = True
    return d

#No longer used
#def collapse_dictionary(dict):
#    list = []
#    for k,v in dict.items():
#        list.append(k)
#        list.append(v)
#    return list

#def tif_to_color_jpeg(input, output, colorBreaksCSV):
#    writetolog("    running  tif_to_color_jpeg()", True, False)
#    writetolog("        input=" + input, False, False)
#    writetolog("        output=" + output, False, False)
#    writetolog("        colorBreaksCSV=" + colorBreaksCSV, False, False)
#    out_bands = 3
#    #output_tmp = mktempfile(prefix='intermediateJpegPic', suffix='.tif')
#    output_tmp = output + ".tmp.tif"
#    # Print some info
#    #print "Creating %s" % (output)
#    
#    #populate the color breaks dictionary 
#    #  from the colorBreaks CSV
#
#    csvfile = open(colorBreaksCSV, "r")
#    #dialect = csv.Sniffer().sniff(csvfile.read(1024))
#    reader = csv.reader(csvfile)
#    usedPixels = {}
#    header = reader.next() #skip the header
#    
#    color_dict = {}
#    maxVal = -9999
#    for row in reader:
#        color_dict[float(row[1])] = [row[3], row[4], row[5]]
#        if row[2] > maxVal: maxVal = row[2]
#        
#    #print color_dict
#    # Open source file
#    src_ds = gdal.Open( input )
#    src_band = src_ds.GetRasterBand(1)
#    
#    # create destination file
#    dst_driver = gdal.GetDriverByName('GTiff')
#    dst_ds = dst_driver.Create(output_tmp, src_ds.RasterXSize,
#                               src_ds.RasterYSize, out_bands, gdal.GDT_Byte)
#    
#    # create output bands
#    band1 = numpy.zeros([src_ds.RasterYSize, src_ds.RasterXSize])
#    band2 = numpy.zeros([src_ds.RasterYSize, src_ds.RasterXSize])
#    band3 = numpy.zeros([src_ds.RasterYSize, src_ds.RasterXSize])
#    
#    # set the projection and georeferencing info
#    dst_ds.SetProjection( src_ds.GetProjection() )
#    dst_ds.SetGeoTransform( src_ds.GetGeoTransform() )
#    
#    # read the source file
#    #gdal.TermProgress( 0.0 )
#    for iY in range(src_ds.RasterYSize):
#        src_data = src_band.ReadAsArray(0,iY,src_ds.RasterXSize,1)
#        col_values = src_data[0] # array of z_values, one per row in source data
#        for iX in range(src_ds.RasterXSize):
#            z_value = col_values[iX]
#            [R,G,B] = MakeColor(z_value, color_dict, maxVal)
#            band1[iY][iX] = R
#            band2[iY][iX] = G
#            band3[iY][iX] = B
#    #gdal.TermProgress( (iY+1.0) / src_ds.RasterYSize )
#    
#    # write each band out
#    dst_ds.GetRasterBand(1).WriteArray(band1)
#    dst_ds.GetRasterBand(2).WriteArray(band2)
#    dst_ds.GetRasterBand(3).WriteArray(band3)
#
#    # Create jpeg or rename tmp file
#    jpg_driver = gdal.GetDriverByName("JPEG") 
#    jpg_driver.CreateCopy(output, dst_ds, 0 ) 
#    
#    try:
#        os.remove(output_tmp)
#    except:
#        pass
#    
#    try:
#        GDALClose(output_tmp)
#    except:
#        pass
#    
#    try:
#        os.remove(output_tmp)
#    except:
#        pass
#    
#    dst_ds = None
#    writetolog("    finished running  tif_to_color_jpeg()", True, False)
#    return True
#
#def MakeColor(z_value, color_dict, maxVal):
#
#    
#    key_list = color_dict.keys()
#    key_list.sort()
#    while len(key_list) > 0:
#        last_val = key_list[-1]
#        #print "lastVal =   ",last_val
#        #print "ZVal =   ",z_value
#        if z_value >= last_val and z_value <= maxVal:
#            #"print color for ", z_value, " is ", last_val, " = ", color_dict[last_val]
#            return color_dict[last_val]
#            break
#        else:
#            key_list.remove(last_val)
#
#    #if we get here something is wrong return black
#    #print "Value not found defaulting to black"
#    return [255, 255, 255]
    
def MDSresponseCol(MDSFile):
    csvfile = open(MDSFile, "r")
    reader = csv.reader(csvfile)
    header = reader.next() #store the header
    responseCol = header[2]
    return responseCol 
   
def print_exc_plus( ):
    """ Print the usual traceback information, followed by a listing of
        all the local variables in each frame.
        lifted from the Python Cookbook
    """
    msg = ""
    tb = sys.exc_info( )[2]
    while tb.tb_next:
        tb = tb.tb_next
    stack = [  ]
    f = tb.tb_frame
    while f:
        if r'\sahm\\' in f.f_code.co_filename:
            stack.append(f)
        f = f.f_back
    stack.reverse( )
    traceback.print_exc( )
    msg += "\n" + "Locals by frame, innermost last"
    for frame in stack:
        msg += "\n"
        msg += "\n" + "Frame %s in %s at line %s" % (frame.f_code.co_name,
                                             frame.f_code.co_filename,
                                             frame.f_lineno)
        msg += "\n"
        for key, value in frame.f_locals.items( ):
            msg += "\t%20s = " % key
            # we must _absolutely_ avoid propagating exceptions, and str(value)
            # COULD cause any exception, so we MUST catch any...:
            try:
                msg += str(value)
            except:
                msg += "<ERROR WHILE PRINTING VALUE>"
                
    msg += "\n\n" + ' '.join([str(i) for i in sys.exc_info()[:2]])
    
    return msg

def informative_untrapped_error(instance, name):
    errorMsg = "An error occurred running " + name + ", error message below:  "
    errorMsg += "\n    " + ' '.join([str(i) for i in sys.exc_info()[:2]])
    try:
        errorMsg += traceback.format_tb(sys.exc_info()[2], 10)[-2]
    except IndexError:
        pass
    writetolog(print_exc_plus(), False, False)
    raise ModuleError(instance, errorMsg)

def breakpoint():
    ''' open up the python debugger here and poke around
    Very helpful, I should have figured this out ages ago!
    '''
    QtCore.pyqtRemoveInputHook()
    import pdb; pdb.set_trace()

def writetolog(*args, **kwargs):
    '''Uses the SAHM log file writting function
    but appends our known logfile to the kwargs.
    '''
    global _logger
    _logger.writetolog(*args, **kwargs)

def createLogger(outputdir, verbose):
    global _logger
    _logger = utilities.logger(outputdir, verbose)
    
def getLogger():
    global _logger
    return _logger

def getShortName(fullPathName):
    if fullPathName.endswith('hdr.adf'):
        shortname = os.path.split(fullPathName)[0]
        shortname = os.path.split(shortname)[1]
    else:
        shortname = os.path.split(fullPathName)[1]
        shortname = os.path.splitext(shortname)[0]
    return shortname

def getRasterName(fullPathName):
    if fullPathName.endswith('hdr.adf'):
        rastername = os.path.split(fullPathName)[0]
    else:
        rastername = fullPathName
    return rastername

def getModelsPath():
    return os.path.join(os.path.dirname(__file__), "pySAHM", "Resources", "R_Modules")

def runRScript(script, args, module=None):
    global config
    r_path = config.r_path
    program = os.path.join(r_path, "i386", "Rterm.exe") #-q prevents program from running
    scriptFile = os.path.join(getModelsPath(), script)
    
    command = program + " --vanilla -f " + scriptFile + " --args " + args
    
    p = subprocess.Popen(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    writetolog("\nStarting R Processing of " + script, True)
    writetolog("    args: " + args, False, False)
    writetolog("    command: " + command, False, False)
    ret = p.communicate()
    
    if 'Error' in ret[1]:
        msg = "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        msg +="\n  An error was encountered in the R script for this module."
        msg += "\n     The R error message is below: \n"
        msg += ret[1]
        writetolog(msg)
        if module:
            raise ModuleError(module, msg)
        else:
            raise RuntimeError , msg

    if 'Warning' in ret[1]:
        msg = "The R scipt returned the following warning(s).  The R warning message is below - \n"
        msg += ret[1]
        writetolog(msg)

    del(ret)
    writetolog("\nFinished R Processing of " + script, True)

def merge_inputs_csvs(inputCSVs_list, outputFile):
    oFile = open(outputFile, "wb")
    outputCSV = csv.writer(oFile)
    outputCSV.writerow(["PARCOutputFile", "Categorical",
                         "Resampling", "Aggregation", "OriginalFile"])
    for inputCSV in inputCSVs_list:
        iFile = open(inputCSV, "rb")
        inputreader = csv.reader(iFile)
        inputreader.next()
        for row in inputreader:
            outputCSV.writerow(row)
        iFile.close()
    oFile.close()

def applyMDS_selection(oldMDS, newMDS):
    """Takes a selection from a previous MDS and '
        applies it to a new MDS file.
    """
    oldvals = {}
    if os.path.exists(oldMDS):
        iFile = open(oldMDS, 'r')
        previousout = csv.reader(iFile)
        oldheader1 = previousout.next()
        oldheader2 = previousout.next()
        oldvals = dict(zip(oldheader1, oldheader2))
        iFile.close()
        del previousout
        
    tmpnewMDS = newMDS + ".tmp.csv"
    oFile = open(tmpnewMDS, "wb")
    tmpOutCSV = csv.writer(oFile)
    iFile = open(newMDS, "rb")
    outCSV = csv.reader(iFile)
    
    oldHeader1 = outCSV.next()
    oldHeader2 = outCSV.next()
    oldHeader3 = outCSV.next()
    
    selectionline = []
    for i in range(len(oldHeader1)):
        if oldvals.has_key(oldHeader1[i]) and \
        oldvals[oldHeader1[i]] == '0':
            selectionline.append('0')
        else:
            selectionline.append('1')
            
    tmpOutCSV.writerow(oldHeader1)
    tmpOutCSV.writerow(selectionline)    
    tmpOutCSV.writerow(oldHeader3)
    for row in outCSV:
        tmpOutCSV.writerow(row)
    
    iFile.close()
    oFile.close()
    shutil.copyfile(tmpnewMDS, newMDS)
    os.remove(tmpnewMDS)
    


    
    
    

    
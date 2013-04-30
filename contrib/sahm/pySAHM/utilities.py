#!/usr/bin/python

''' These utility functions are shared 
between all of the Python SAHM command line
modules
'''

import os, sys
import time
import csv
import string

from osgeo import gdal
from osgeo import osr
from osgeo import ogr

_logfile = ''
_verbose = False

class logger(object):
    def __init__(self, logfile, verbose):
        self.logfile = logfile
        self.verbose = verbose
        
        #if we mistakenly get a output dir instead of a filename
        if os.path.isdir(logfile):
            self.logfile = os.path.join(logfile, 'sessionLog.txt')
        else:
            self.logfile = logfile
            
        if os.path.exists(self.logfile):
            self.writetolog("\nSession continued\n", True, True)
        else:
            logDir = os.path.split(self.logfile)[0]
            if not os.path.exists(logDir):
                raise RuntimeError('Directory of specified logfile does not exist.')
            f = open(self.logfile, "w")
            del f
            self.writetolog("\nSession started\n", True, False)
            
            
    def writetolog(self, msg, addtime=False, printtoscreen=True):
        '''Opens the log file and writes the passed msg.
    Optionally adds a time slot to the message and
    Prints the msg to the screen.
    If the logfile is not specified tries to use the global variable.
        '''
        f = open(self.logfile, "a")
        if self.verbose and printtoscreen:
            print msg
        if addtime:
            msg = ' at: '.join([msg, time.strftime("%m/%d/%Y %H:%M")])
        msg = "\n" + msg
        f.write(msg)
        del f  

class TrappedError(Exception):
    """Exception class indicating that an anticipated problem
    was encountered in a specific module
    """
    def __init__(self, msg=None):
        Exception.__init__(self)
        self.message = msg

            

#def createsessionlog(roottempdir, verbose):
#    '''Creates a new log file if one doesn't already exist.
#    If one exists then writes that the session has continued.
#    '''
#    global _logfile, _verbose
#    _verbose = verbose
#    
#    logfile = os.path.join(roottempdir, "sessionLog.txt")
#    _logfile = logfile
#    
#    if os.path.exists(logfile):
#        writetolog("\nSession continued\n", True, True, logfile=logfile)
#    else:
#        f = open(os.path.join(roottempdir, "sessionLog.txt"), "w")
#        del f
#    
#    return logfile
#
#def writetolog(msg, addtime=False, printtoscreen=True, logfile=''):
#    '''Opens the log file and writes the passed msg.
#    Optionally adds a time slot to the message and
#    Prints the msg to the screen.
#    If the logfile is not specified tries to use the global variable.
#    '''
#    global _logfile
#    if logfile == '':
#        logfile = _logfile
#    
#    f = open(logfile, "a")
#    if _verbose and printtoscreen:
#        print msg
#    if addtime:
#        msg = ' at: '.join([msg, time.strftime("%m/%d/%Y %H:%M")])
#    msg = "\n" + msg
#    f.write(msg)
#    del f

    
def isMDSFile(MDSFile):
    '''performs a check to see if a supplied file is in 'MDS' format
    This means:
    1 - The file has three header lines
        first: x, y, responseBinary or responseCount, a series of covariate names, and an optional Split
        second: '0', '0', '0', 0 or blanks and 0 or 1 for each covariate indicate use or ignore
        third: '', '', '', the full path and filename of the tiff covariate layer.
    2 - additionally lines contain individual occurance location, response, covariate attributes at that location, and test\train for the Split column
    
        Values of -9999 in the response column indicate a background point.
        covariate names ending in '*_categorical' indicate a categorical variable
        
    The test used in this check are by no means thorough in checking for covariate files
    existing on the file system, missing values in any columns, appropriate values in 
    the response or Split columns, etc.  Instead this function is intended to just give a 
    best guess as to to if this is an MDS.    
    '''
    MDSreader = csv.reader(open(MDSFile, 'r'))
    header1 = MDSreader.next()
    header2 = MDSreader.next()
    header3 = MDSreader.next()

#These no longer apply with the new agg feature.
#    for i in [0, 1, 2]:
#        if not(header2[0] == '' or header2[0] == '0'):
#            return False
    
#    for item in header2[3:-1]:
#        if not item in ['0', '1']:
#            return False
    
    return True
    del MDSreader

def process_waiter(popen, description, que):
    try: 
        popen.wait()     
    finally: 
        que.put( (description, popen.returncode) ) 


def mds_to_shape(MDSFile, outputfolder):
    
    #bit of a hack but currently saving the shape file as 
    #three shape files presence, absence, and background
    #as I'm having trouble getting QGIS to display points
    #with categorical symbology
    
    h, t = os.path.split(MDSFile)
    t_no_ext = os.path.splitext(t)[0]
    outputfiles = {"pres":os.path.join(outputfolder, t_no_ext + "_pres.shp"),
                   "abs":os.path.join(outputfolder, t_no_ext +  "_abs.shp"),
                   "backs":os.path.join(outputfolder, t_no_ext +  "_backs.shp")}

    driver = ogr.GetDriverByName('ESRI Shapefile')
    
    MDSreader = csv.reader(open(MDSFile, 'r'))
    header1 = MDSreader.next()
    header2 = MDSreader.next()
    header3 = MDSreader.next()
    
    h, t = os.path.split(MDSFile)
    t_no_ext = os.path.splitext(t)[0]
#    
    
    for outfile in outputfiles.values():
        h, t = os.path.split(outfile)
        if os.path.exists(outfile):
            os.chdir(h)
            driver.DeleteDataSource(t)
    
    ds = driver.CreateDataSource(h)
    
    preslayer = ds.CreateLayer(t_no_ext + "_pres",
                           geom_type=ogr.wkbPoint)
    abslayer = ds.CreateLayer(t_no_ext + "_abs",
                           geom_type=ogr.wkbPoint)
    backslayer = ds.CreateLayer(t_no_ext + "_backs",
                           geom_type=ogr.wkbPoint)
    
    #cycle through the items in the header and add
    #these to each output shapefile attribute table
    fields = {}
    for field in header1:
        field_name = Normalized_field_name(field, fields)
        fields[field_name] = field
        if field == "Split":
            #this is the test training split field that we add
            fieldDefn = ogr.FieldDefn(field_name, ogr.OFTString)
        else:
            fieldDefn = ogr.FieldDefn(field_name, ogr.OFTReal)
        
        preslayer.CreateField(fieldDefn)
        abslayer.CreateField(fieldDefn)
        backslayer.CreateField(fieldDefn)
        
    featureDefn = preslayer.GetLayerDefn()
    
    #cycle through the rows and add each geometry to the 
    #appropriate shapefile
    for row in MDSreader:
        feature = ogr.Feature(featureDefn)
        point = ogr.Geometry(ogr.wkbPoint)
        
        point.SetPoint_2D(0, float(row[0]), float(row[1]))
        feature.SetGeometry(point)
        
        # for this feature add in each of the attributes from the row
        header_num = 0
        for field in header1:
            short_field = find_key(fields, field)
            if field == "Split":
                feature.SetField(short_field, row[header_num])
            else:
                feature.SetField(short_field, float(row[header_num]))
            header_num += 1
        
        response = float(row[2])
        
        if abs(response - 0) < 1e-9: 
            abslayer.CreateFeature(feature)
        elif response > 0:
            preslayer.CreateFeature(feature)
        elif abs(response - -9999.0) < 1e-9:
            backslayer.CreateFeature(feature)

    # close the data sources
    del MDSreader
    ds.Destroy()

def Normalized_field_name(field_name, previous_fields):
    short_name = field_name[:10]
    
    #remove Non alpha numeric characters
    short_name = ''.join(ch for ch in short_name if ch in (string.ascii_letters + string.digits + '_'))
    
    if previous_fields.has_key(short_name):
        i = 1
        shorter_name = short_name[:8]
        short_name = shorter_name + "_" + str(i)
        while previous_fields.has_key(short_name):
            i += 1
            short_name = shorter_name + "_" + str(i)
    return short_name

def find_key(dic, val):
    """return the key of dictionary dic given the value
    from: http://www.daniweb.com/software-development/python/code/217019"""    
    return [k for k, v in dic.iteritems() if v == val][0]

if __name__ == "__main__":
    
    mds_to_shape(r"I:\VisTrails\WorkingFiles\workspace\talbertc_20110901T175958\CovariateCorrelationOutputMDS_anothertry2.csv", r"I:\VisTrails\WorkingFiles\workspace\talbertc_20110901T175958\CovariateCorrelationOutputMDS_anothertry2.shp")
    print "done"




'''
Created on Nov 18, 2010

@author: talbertc
'''
import os, sys, shutil
import time
import tempfile


from core.modules.basic_modules import File, Directory, new_constant, Constant

from osgeo import gdalconst
from osgeo import gdal
from osgeo import osr
import numpy

_roottempdir = ""
_temp_files = []
_temp_dirs = []

def mktempfile(*args, **kwargs):
    global _temp_files
    global _roottempdir
    kwargs["dir"] = _roottempdir
    (fd, fname) = tempfile.mkstemp(*args, **kwargs)
    os.close(fd)
    _temp_files.append(fname)
    return fname

def mktempdir(*args, **kwargs):
    global _temp_dirs
    global _roottempdir
    kwargs["dir"] = _roottempdir
    dname = tempfile.mkdtemp(*args, **kwargs)
    _temp_dirs.append(dname)
    return dname

def createrootdir():
    global _roottempdir
    _roottempdir = tempfile.mkdtemp(prefix='sahmrun_' + 
                    time.strftime("%Y%m%dT%H%M%S") +"_")
    
    print ("*"*60 + "\n")*2 + ("*"*60 )
    print "temp directory location is " + _roottempdir
    print ("*"*60 + "\n")*3

def cleantemps():
    global _temp_files, _temp_dirs, _roottempdir
    for file in _temp_files:
        os.remove(file)
    for dir in _temp_dirs:
        shutil.rmtree(dir)
    shutil.rmtree(_roottempdir)

def map_ports(module, port_map):
    args = {}
    for port, (flag, access, required) in port_map.iteritems():
        if required or module.hasInputFromPort(port):
            value = module.getInputFromPort(port)
            if access is not None:
                value = access(value)
            args[flag] = value
    return args

def path_value(value):
    return value.name

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

def collapse_dictionary(dict):
    list = []
    for k,v in dict.items():
        list.append(k)
        list.append(v)
    return list

def tif_to_color_jpeg(input, output):
    out_bands = 3
    output_tmp = mktempfile(prefix='intermediateJpegPic', suffix='.tif')
    # Print some info
    print "Creating %s" % (output)
    
    # Open source file
    src_ds = gdal.Open( input )
    src_band = src_ds.GetRasterBand(1)
    
    # create destination file
    dst_driver = gdal.GetDriverByName('GTiff')
    dst_ds = dst_driver.Create(output_tmp, src_ds.RasterXSize,
                               src_ds.RasterYSize, out_bands, gdal.GDT_Byte)
    
    # create output bands
    band1 = numpy.zeros([src_ds.RasterYSize, src_ds.RasterXSize])
    band2 = numpy.zeros([src_ds.RasterYSize, src_ds.RasterXSize])
    band3 = numpy.zeros([src_ds.RasterYSize, src_ds.RasterXSize])
    
    # set the projection and georeferencing info
    dst_ds.SetProjection( src_ds.GetProjection() )
    dst_ds.SetGeoTransform( src_ds.GetGeoTransform() )
    
    # read the source file
    #gdal.TermProgress( 0.0 )
    for iY in range(src_ds.RasterYSize):
        src_data = src_band.ReadAsArray(0,iY,src_ds.RasterXSize,1)
        col_values = src_data[0] # array of z_values, one per row in source data
        for iX in range(src_ds.RasterXSize):
            z_value = col_values[iX]
            #print z_value # uncomment to see what value breaks color ramp
            [R,G,B] = MakeColor(z_value)
            band1[iY][iX] = R
            band2[iY][iX] = G
            band3[iY][iX] = B
    #gdal.TermProgress( (iY+1.0) / src_ds.RasterYSize )
    
    # write each band out
    dst_ds.GetRasterBand(1).WriteArray(band1)
    dst_ds.GetRasterBand(2).WriteArray(band2)
    dst_ds.GetRasterBand(3).WriteArray(band3)

    # Create jpeg or rename tmp file
    
    jpg_driver = gdal.GetDriverByName("JPEG") 
    jpg_driver.CreateCopy(output, dst_ds, 0 ) 
    
    try:
        GDALClose(output_tmp)
        os.remove(output_tmp)
    except:
        pass
    dst_ds = None

    return True

def MakeColor(z_value):
    '''LUT for color ramp. Keys are pixel values, hash values are RGB
    triplets.'''
    color_dict = {
    0:[0,245,0],
    0:[0,245,0],
    0.1:[91,247,0],
    0.2:[140,247,0],
    0.3:[186,247,0],
    0.4:[224,245,0],
    0.5:[245,194,0],
    0.6:[247,223,0],
    0.7:[252,177,0],
    0.8:[252,130,0],
    0.9:[250,79,0],
    1:[245,0,0]}
    
    key_list = color_dict.keys()
    key_list.sort()
    while len(key_list) > 0:
        last_val = key_list[-1]
        if z_value >= last_val:
            return color_dict[last_val]
        else:
            key_list.remove(last_val)



if __name__ == '__main__':
    pass
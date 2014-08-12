###############################################################################
##
## Copyright (C) 2011-2014, NYU-Poly.
## Copyright (C) 2006-2011, University of Utah. 
## All rights reserved.
## Contact: contact@vistrails.org
##
## This file is part of VisTrails.
##
## "Redistribution and use in source and binary forms, with or without 
## modification, are permitted provided that the following conditions are met:
##
##  - Redistributions of source code must retain the above copyright notice, 
##    this list of conditions and the following disclaimer.
##  - Redistributions in binary form must reproduce the above copyright 
##    notice, this list of conditions and the following disclaimer in the 
##    documentation and/or other materials provided with the distribution.
##  - Neither the name of the University of Utah nor the names of its 
##    contributors may be used to endorse or promote products derived from 
##    this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
## AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
## THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR 
## PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR 
## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; 
## OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
## WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR 
## OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF 
## ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
###############################################################################
import itertools

""" Utilities for dealing with the thumbnails """
import os
import os.path
import shutil
import tempfile
import time
import uuid
import mimetypes
# mimetypes are broken by default on windows so use the builtins
# Remove line below when it is fixed here: http://bugs.python.org/issue15207
mimetypes.init(files=[])
from vistrails.core import debug, system
from vistrails.core.configuration import get_vistrails_configuration, \
      get_vistrails_persistent_configuration
from vistrails.core.utils import VistrailsInternalError

############################################################################
class CacheEntry(object):
    def __init__(self, abs_name, name, time, size):
        self.abs_name = abs_name
        self.name = name
        self.time = time
        self.size = size
        
class ThumbnailCache(object):
    _instance = None
    IMAGE_MAX_WIDTH = 200 
    SUPPORTED_TYPES = ['image/png','image/jpeg','image/bmp','image/gif']
    @staticmethod
    def getInstance(*args, **kwargs):
        if ThumbnailCache._instance is None:
            obj = ThumbnailCache(*args, **kwargs)
            ThumbnailCache._instance = obj
        return ThumbnailCache._instance

    @staticmethod
    def clearInstance():
        if ThumbnailCache._instance is not None:
            ThumbnailCache._instance.destroy()

    def __init__(self):
        self._temp_directory = None
        self.elements = {}
        self.vtelements = {}
        self.conf = None
        conf = get_vistrails_configuration()
        if conf.has('thumbs'):
            self.conf = conf.thumbs
        self.init_cache()

    def destroy(self):
        if self._temp_directory is not None:
            print "removing thumbnail directory"
            shutil.rmtree(self._temp_directory)
        
    def get_directory(self):
        thumbnail_dir = system.get_vistrails_directory('thumbs.cacheDir')
        if thumbnail_dir is not None:
            if not os.path.exists(thumbnail_dir):
                raise VistrailsInternalError("Cannot find %s" % thumbnail_dir)
            return thumbnail_dir
        
        # raise VistrailsInternalError("'thumbs.cacheDir' not"
        #                              " specified in configuration")
        if self._temp_directory is None:
            self._temp_directory = tempfile.mkdtemp(prefix='vt_thumbs_')
        return self._temp_directory
    
    def init_cache(self):
        for root,dirs, files in os.walk(self.get_directory()):
            for f in files:
                fname = os.path.join(root,f)
                statinfo = os.stat(fname)
                size = int(statinfo[6])
                time = float(statinfo[8])
                entry = CacheEntry(fname, f, time, size)
                self.elements[f] = entry
                
    def get_abs_name_entry(self,name):
        """get_abs_name_entry(name) -> str 
        It will look for absolute file path of name in self.elements and 
        self.vtelements. It returns None if item was not found.
        
        """
        try:
            return self.elements[name].abs_name
        except KeyError, e:
            try:
                return self.vtelements[name].abs_name
            except KeyError, e:
                return None
        
    def size(self):
        size = 0
        for entry in self.elements.itervalues():
            size += entry.size
        return size

    def move_cache_directory(self, sourcedir, destdir):
        """change_cache_directory(sourcedir: str, dest_dir: str) -> None"
        Moves files from sourcedir to destdir
        
        """
        if os.path.exists(destdir):
            for entry in self.elements.itervalues():
                try:
                    srcname = entry.abs_name
                    dstname = os.path.join(destdir,entry.name)
                    shutil.move(srcname,dstname)
                    entry.abs_name = dstname
                        
                except shutil.Error, e:
                    debug.warning("Could not move thumbnail from %s to %s" % (
                                  sourcedir, destdir),
                                  e)
                    
    def remove_lru(self,n=1):
        elements = self.elements.values()
        elements.sort(key=lambda obj: obj.time)
        num = min(n,len(elements))
        debug.debug("Will remove %s elements from cache..."%num)
        debug.debug("Cache has %s elements and %s bytes"%(len(elements),
                                                             self.size()))
        for elem in itertools.islice(elements, num):
            try:
                del self.elements[elem.name]
                os.unlink(elem.abs_name)
            except os.error, e:
                debug.warning("Could not remove file %s" % elem.abs_name, e)

    def remove(self,key):
        if key in self.elements.keys():
            entry = self.elements[key]
            del self.elements[key]
            os.unlink(entry.abs_name)
        elif key in self.vtelements.keys():
            entry = self.vtelements[key]
            del self.vtelements[key]
            os.unlink(entry.abs_name)
            
    def clear(self):
        self.elements = {}
        self._delete_files(self.get_directory())
        
    def add_entry_from_cell_dump(self, folder, key=None):
        """create_entry_from_cell_dump(folder: str) -> str
        Creates a cache entry from images in folder by merge them in a single 
        image and returns the name of the image in cache.
        If a valid key is provided, it will use it as the name of the 
        image file.
        
        """
        
        image = None
        thumbnail_fnames = self._get_thumbnail_fnames(folder)
        if len(thumbnail_fnames) > 0:
            image = self._merge_thumbnails(thumbnail_fnames)
        fname = None
        if image != None and image.width() > 0 and image.height() > 0:
            fname = "%s.png" % str(uuid.uuid1())
            abs_fname = self._save_thumbnail(image, fname) 
            statinfo = os.stat(abs_fname)
            size = int(statinfo[6])
            time = float(statinfo[8])
            entry = CacheEntry(abs_fname, fname, time, size)
            #remove old element
            if key:
                self.remove(key)
            if self.size() + size > self.conf.cacheSize*1024*1024:
                self.remove_lru(10)
                
            self.elements[fname] = entry
        return fname
        
    def add_entries_from_files(self, absfnames):
        """add_entries_from_files(absfnames: list of str) -> None
        In this case the files already exist somewhere on disk.
        We just keep references to them.
        
        """
        for abs_fname in absfnames:
            fname = os.path.basename(abs_fname)
            statinfo = os.stat(abs_fname)
            size = int(statinfo[6])
            time = float(statinfo[8])
            entry = CacheEntry(abs_fname, fname, time, size)
            self.vtelements[fname] = entry

    @staticmethod
    def _delete_files(dirname):
        """delete_files(dirname: str) -> None
        Deletes all files inside dirname
    
        """
        if dirname is None:
            return
        try:
            for root, dirs, files in os.walk(dirname):
                for fname in files:
                    os.unlink(os.path.join(root,fname))
                    
        except OSError, e:
            debug.warning("Error when removing thumbnails", e)
    
    @staticmethod
    def _get_thumbnail_fnames(folder):
        """Returns the filenames of the images to be composited in the given
        folder.  (folder: str) -> list(str)
        
        """
        fnames = []
        for root, dirs, files in os.walk(folder):
            for f in files:
                ftype = mimetypes.guess_type(f)
                if ftype[0] in ThumbnailCache.SUPPORTED_TYPES:
                    fnames.append(os.path.join(root,f))
        return fnames

    @staticmethod
    def _merge_thumbnails(fnames):
        """_merge_thumbnails(fnames: list(str)) -> QImage 
        Generates a single image formed by all the images in the fnames list.
        
        """
        from PyQt4 import QtCore, QtGui
        height = 0
        width = 0
        pixmaps = []
        # OS may return wrong order so  we need to sort
        fnames.sort()
        for fname in fnames:
            pix = QtGui.QPixmap(fname)
            if pix.height() > 0 and pix.width() > 0:
                pixmaps.append(pix)
                #width += pix.width()
                #height = max(height, pix.height())
                height += pix.height()
                width = max(width,pix.width())            
        if len(pixmaps) > 0 and height > 0 and width > 0:        
            finalImage = QtGui.QImage(width, height, QtGui.QImage.Format_ARGB32)
            painter = QtGui.QPainter(finalImage)
            x = 0
            for pix in pixmaps:
                painter.drawPixmap(0, x, pix)
                x += pix.height()
            painter.end()
            if width > ThumbnailCache.IMAGE_MAX_WIDTH:
                finalImage = finalImage.scaledToWidth(ThumbnailCache.IMAGE_MAX_WIDTH,
                                                      QtCore.Qt.SmoothTransformation)
        else:
            finalImage = None
        return finalImage

    def _save_thumbnail(self, pngimage, fname):
        """_save_thumbnail(pngimage:QImage, fname: str) -> str 
        Returns the absolute path of the saved image
        
        """
        png_fname = os.path.join(self.get_directory(), fname)
        if os.path.exists(png_fname):
            os.unlink(png_fname)
        pngimage.save(png_fname)
        return png_fname

    def _copy_thumbnails(self, thumbnails):
        """_copy_thumbnails(thumbnails: list of str) -> None """
        local_dir = self.get_directory()
        for thumb in thumbnails:
            local_thumb = os.path.join(local_dir, os.path.basename(thumb))
            if os.path.exists(thumb) and not os.path.exists(local_thumb):
                shutil.copyfile(thumb, local_thumb)

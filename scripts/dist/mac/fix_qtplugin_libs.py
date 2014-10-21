#!/usr/bin/env python
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
""" Copy Qt plugin libs to a separate folder, such as "./Input/plugins".
For the VisTrails app we have to copy only the iconengines and imageformats
plugins.

For example:
  $ mkdir Input/plugins
  $ cp -r ~/Qt-4.4.3/plugins/iconengines Input/plugins
  $ cp -r ~/Qt-4.4.3/plugins/imageformats Input/plugins
  $ python fix_qtplugin_libs.py Input/plugins/iconengines
  $ python fix_qtplugin_libs.py Input/plugins/imageformats

"""
import os
import shutil
import popen2
import re
import os.path
import sys

def usage():
    print "Usage: "
    print "   %s path_to_dylibs" % sys.argv[0]
    sys.exit(1)

try:
    path_to_libs = sys.argv[1]
    
except IndexError:
    usage()

print "This will modify the *.dylibs in ", path_to_libs

libnames = re.compile(r'.*\.dylib')
libnames_otool = re.compile(r'(.*\.dylib) (\(.+\))')
pythonlibname = re.compile(r'(.*Python\.framework*[^\)]*/Python) (\(.+\))')

# my qt libraries are in /Users/emanuele/Qt-4.4.3/
# modify this according to your needs
qtlibnames = re.compile(r'(Qt.+) (\(.+\))')

updatenames = re.compile(r'(@executable_path.*[^ ]*) .*')

#we first build the list of everything to change to minimize risk of failing
# after partial changes
def link_or_copy(src, dst):
    """link_or_copy(src:str, dst:str) -> None 
    Tries to create a hard link to a file. If it is not possible, it will
    copy file src to dst 
    
    """
    # Links if possible, but we're across devices, we need to copy.
    try:
        os.link(src, dst)
    except OSError, e:
        if e.errno == 18:
            # Across-device linking is not possible. Let's copy.
            shutil.copyfile(src, dst)
        else:
            raise e
        
def build_cmdline_qt(file_name, original_path, lib_name):
    new_path = '@executable_path/../Frameworks/%s' % (lib_name)
    cmd_line = ('install_name_tool -change %s %s %s' %
                (original_path,
                 new_path,
                 file_name))
    return cmd_line

def build_id_cmdline(file_name, original_path):
    new_id = os.path.basename(original_path)
    cmd_line = ('install_name_tool -id %s %s' %
                (new_id, file_name))
    return cmd_line

for root, dirs, file_names in os.walk(path_to_libs):
    break

files_to_visit = set()
links_to_visit = set()

for f in file_names:
    if libnames.match(f):
        if not os.path.islink(os.path.join(path_to_libs,f)):
            files_to_visit.add(f)
        else:
            links_to_visit.add(f)

if len(files_to_visit) == 0:
    print "looks like you started the script from the wrong directory"
    sys.exit(1)

while len(files_to_visit):
    f = files_to_visit.pop()
    print "Visiting file", f
    src = os.path.join(path_to_libs,f)

    pout, pin = popen2.popen2("otool -L %s" % src)
    #print pout.readlines()
    #changing id
    lines = pout.readlines()
    #print lines[1]
    if lines[1].find(lines[0][:-2]) > 0:
        m = libnames_otool.match(lines[1][:-1].strip())
        if m:
            original_path = m.groups()[0]
            id_cmd_line = build_id_cmdline(lines[0][:-2].strip(), original_path)
            #print "id_cmd_line ", id_cmd_line
            result = os.system(id_cmd_line)
            if result != 0:
                print "Something went wrong with install_name_tool. Ouch."
                sys.exit(1)
    for l in lines[2:]:
        
        for r in [qtlibnames,
                  pythonlibname]:
            m = r.match(l[:-1].strip())
            if m and r == qtlibnames:
                #print "qt  * matched: ", l[:-1].strip()
                #pos = str(m.groups()[0]).find("/Qt-4.4.3/lib/")
                libname = str(m.groups()[0])
                cmd_line = build_cmdline_qt(src, m.groups()[0], libname)
            elif m and r == pythonlibname :
                #print "python  * matched: ", l[:-1].strip()
                #print m.groups()
                libname ='Python.framework/Python' #Python framework in paraview bundle
                cmd_line = build_cmdline_qt(src, m.groups()[0], libname)
                #print "cmdline: ", cmd_line
            if m:
                #print "new file!", f
                result = os.system(cmd_line)
                if result != 0:
                    print "Something went wrong with install_name_tool. Ouch."
                    sys.exit(1)

# creating symbolic links
# cur_dir = os.getcwd()
# os.chdir(destination_libs)
# print "Creating symbolic links in %s " % os.getcwd()
# while len(links_to_visit):
#     f = links_to_visit.pop()
#     src = os.readlink(os.path.join(path_to_libs,f))
#     print "  ", f, " -> " , src
#     os.symlink(src,f)
#os.chdir(cur_dir)


print "Done."

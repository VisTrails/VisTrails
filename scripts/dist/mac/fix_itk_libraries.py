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
import os
import shutil
import popen2
import re
import os.path
import sys

def usage():
    print "Usage: "
    print "   %s path_to_itk_files destination_folder" % sys.argv[0]
    sys.exit(1)

try:
    path_to_libs = os.path.realpath(os.path.join(sys.argv[1],'bin'))
    path_to_python_files = os.path.realpath(os.path.join(sys.argv[1],
                                                         'Wrapping',
                                                         'WrapITK',
                                                         'Python'))
    destination_libs = os.path.realpath(os.path.join(sys.argv[2], 'Frameworks'))
    destination_python_files = os.path.realpath(os.path.join(sys.argv[2],
                                                             'Resources',
                                                             'lib',
                                                             'python2.5'))
    
except IndexError:
    usage()

print "This will copy the *.dylib to", destination_libs, " and *.so and the python files to ", destination_python_files

libnames = re.compile(r'.*\.dylib')
itklibnames = re.compile(r'(.*emanuele*.*\.dylib) .*')
sonames = re.compile(r'.*\.so')
usrlocalnames = re.compile(r'(.*local*.*\.dylib) .*')
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
        
def build_cmdline(file_name, original_path, lib_name):
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
so_to_visit = set()
for f in file_names:
    if libnames.match(f):
        if not os.path.islink(os.path.join(path_to_libs,f)):
            files_to_visit.add(f)
        else:
            links_to_visit.add(f)
    elif sonames.match(f):
        so_to_visit.add(f)
        
if len(files_to_visit) == 0:
    print "looks like you started the script from the wrong directory"
    sys.exit(1)

while len(files_to_visit):
    f = files_to_visit.pop()
    print "Visiting file", f
    src = os.path.join(path_to_libs,f)
    dst = os.path.join(destination_libs,f)
    print "Copyng to destination folder..."
    link_or_copy(src,dst)
    pout, pin = popen2.popen2("otool -L %s" % dst)
    # print pout.readlines()
    #changing id
    lines = pout.readlines()
    m = itklibnames.match(lines[0][:-1].strip())
    if m:
        cmd_line = build_id_cmdline(dst, m.groups()[0])
        result = os.system(cmd_line)
    for l in lines[1:]:
        for r in [itklibnames,
                  usrlocalnames]:
            m = r.match(l[:-1].strip())
            if m:
                #print "  * matched: ", l[:-1].strip()
                libname = os.path.basename(m.groups()[0])
                cmd_line = build_cmdline(dst, m.groups()[0], libname)
                #print "new file!", f
                result = os.system(cmd_line)
                if result != 0:
                    print "Something went wrong with install_name_tool. Ouch."
                    sys.exit(1)

# creating symbolic links
cur_dir = os.getcwd()
os.chdir(destination_libs)
print "Creating symbolic links in %s " % os.getcwd()
while len(links_to_visit):
    f = links_to_visit.pop()
    src = os.readlink(os.path.join(path_to_libs,f))
    print "  ", f, " -> " , src
    os.symlink(src,f)
    
os.chdir(cur_dir)
print "Dealing with *.so files... "
while len(so_to_visit):
    f = so_to_visit.pop()
    print "Visiting file", f
    src = os.path.join(path_to_libs,f)
    dst = os.path.join(destination_python_files,f)
    print "Copyng to destination folder..."
    link_or_copy(src,dst)
    pout, pin = popen2.popen2("otool -L %s" % dst)
    # print pout.readlines()
    #changing id
    lines = pout.readlines()
    m = itklibnames.match(lines[0][:-1].strip())
    if m:
        cmd_line = build_id_cmdline(dst, m.groups()[0])
        result = os.system(cmd_line)
    for l in lines[1:]:
        for r in [itklibnames,
                  usrlocalnames]:
            m = r.match(l[:-1].strip())
            if m:
                #print "  * matched: ", l[:-1].strip()
                libname = os.path.basename(m.groups()[0])
                cmd_line = build_cmdline(dst, m.groups()[0], libname)
                #print "new file!", f
                result = os.system(cmd_line)
                if result != 0:
                    print "Something went wrong with install_name_tool. Ouch."
                    sys.exit(1)
                    
#copying python files
print "copying python files... "
src = os.path.join(path_to_python_files,'*')
os.system("cp -r %s %s" % (src, destination_python_files))    

print "copying  python files in %s..." % path_to_libs
src = os.path.join(path_to_libs,'*.py')
os.system("cp %s %s" % (src, destination_python_files))    

print "copying static libs..." 
src = os.path.join(path_to_libs, "*.a")
os.system("cp %s %s" % (src, destination_libs))

print "Done with ITK."

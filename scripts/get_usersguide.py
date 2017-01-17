#!/usr/bin/env python
###############################################################################
##
## Copyright (C) 2014-2016, New York University.
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
##  - Neither the name of the New York University nor the names of its
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

import os.path
import subprocess
import sys
import urllib2

this_dir = os.path.dirname(os.path.abspath(__file__))

DOWNLOAD_URL = "http://www.vistrails.org/usersguide/dev/html/VisTrails.pdf"
SAVE_TO = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else this_dir

# http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
def which(program):
    import os
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

def download_usersguide():
    print "Downloading usersguide from", DOWNLOAD_URL
    response = urllib2.urlopen(DOWNLOAD_URL)
    filename = os.path.join(SAVE_TO,
                            DOWNLOAD_URL.split('/')[-1])
    f = open(filename, 'wb')
    f.write(response.read())
    f.close()
    
if __name__ == "__main__":
    if which('sphinx-build') is None:
        print "Sphinx is not installed!"
        download_usersguide()
    elif which('pdflatex') is None:
        print "pdflatex is not installed!"
        download_usersguide()
    else:
        cwd = os.getcwd()
        os.chdir(this_dir)
        # Build usersguide
        proc = subprocess.Popen(['./build_usersguide.py', SAVE_TO],
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        proc.wait()
        if proc.returncode != 0:
            print "ERROR: building usersguide failed."
            if proc.stdout:
                print proc.stdout.readlines()        
            sys.exit(1)
        os.chdir(this_dir)


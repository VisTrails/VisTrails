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
""" This will build the html and the pdf version of the user's guide and put
them in where defined. 
Please configure the variables below according to your server's setup

"""
import os
import os.path
import re
import shutil
import subprocess
import sys
import time
### Begin configuration ###

# Should we build the pdf version
BUILD_PDF = True

# Should we build the html version
BUILD_HTML = False

# Folder where vistrails is
PATH_TO_VISTRAILS_GIT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

# Folder where the html files will be placed. This script will build
# the docs in the standard location and move files later
HTML_FOLDER = None

# Complete file path to where copy final pdf file
PDF_FILE = os.path.join(PATH_TO_VISTRAILS_GIT, "scripts", "VisTrails.pdf")

# Should we run a `git pull` before building docs? 
PERFORM_GIT_PULL = False

### End configuration ### 
### The following variables usually don't need to be changed
USERSGUIDE_SUBPATH = ['doc', 'usersguide']
GIT_PULL_CMD = ["git", "pull"]
BUILD_HTML_SUBPATH = ["_build", "html"]
BUILD_LATEX_SUBPATH = ["_build", "latex"]
PDF_BUILD_NAME = "VisTrails.pdf"
if len(sys.argv)>1:
    PDF_FILE = os.path.abspath(sys.argv[1])
    if PDF_FILE[-4:] != '.pdf':
        PDF_FILE = os.path.join(PDF_FILE, PDF_BUILD_NAME)
if __name__ == '__main__':
    if (PATH_TO_VISTRAILS_GIT is not None and
        os.path.exists(PATH_TO_VISTRAILS_GIT)):
        current_folder = os.getcwd()
        if PERFORM_GIT_PULL:
            print "performing git pull in %s..."%PATH_TO_VISTRAILS_GIT
            os.chdir(PATH_TO_VISTRAILS_GIT)
            proc = subprocess.Popen(GIT_PULL_CMD,
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
            proc.wait()
            if proc.returncode != 0:
                print "ERROR: git pull failed."
                if proc.stdout:
                    print proc.stdout.readlines()
        
        # The api needs path to source set
        env = os.environ.copy()
        env['PYTHONPATH'] = PATH_TO_VISTRAILS_GIT

        os.chdir(os.path.join(PATH_TO_VISTRAILS_GIT,
                              *USERSGUIDE_SUBPATH))
        
        print "Going into directory %s"%os.getcwd()
        if BUILD_HTML:
            # now build html documentation    
            print "now building html documentation..."
            proc = subprocess.Popen(["make", "html"],
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    env=env)
            proc.wait()
            if proc.returncode != 0:
                print "ERROR: make html failed."
                if proc.stdout:
                    print proc.stdout.readlines()
            else:
                # now move files to their final place
                if HTML_FOLDER is not None:
                    if os.path.exists(HTML_FOLDER):
                        shutil.rmtree(HTML_FOLDER)
                    html_build = os.path.join(os.getcwd(),
                                              *BUILD_HTML_SUBPATH)
                    shutil.move(html_build, HTML_FOLDER)

        if BUILD_PDF:
            print "Building usersguide to ", PDF_FILE
            #build latex files
            print "now preparing latex files..."
            latex_path = os.path.join(".",
                                  *BUILD_LATEX_SUBPATH)
            if os.path.exists(latex_path):
                print "removing old %s directory..."%latex_path
                proc = subprocess.Popen(["rm", "-rf", latex_path],
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT)
                proc.wait()
            print "building latex files..."
            proc = subprocess.Popen(["make", "latex"],
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    env=env)
            proc.wait()
            if proc.returncode != 0:
                print "ERROR: make latex failed."
                if proc.stdout:
                    print proc.stdout.readlines()
            else:
                #now build pdf
                print "now building pdf file..."
                os.chdir(os.path.join(os.getcwd(),
                         *BUILD_LATEX_SUBPATH))
                proc = subprocess.Popen(["make", "LATEXOPTS=-interaction=nonstopmode -halt-on-error", "all-pdf"],
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    env=env)
                output, error = proc.communicate()
                if proc.returncode != 0:
                    print "ERROR: make all-pdf failed."
                    print output, error
                else:
                    #now move file to its final place
                    if PDF_FILE is not None:
                        if os.path.exists(PDF_FILE):
                            os.unlink(PDF_FILE)
                        pdf_build = os.path.join(os.getcwd(),
                                                 PDF_BUILD_NAME)
                        shutil.move(pdf_build, PDF_FILE)
        os.chdir(current_folder)
        print "Done."
    else:
        print "PATH_TO_VISTRAILS_GIT was not provided. Exiting."

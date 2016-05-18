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
""" This script assumes that VisTrails.command file is located at ../
Run this script after you copied the VisTrails folder and run from where it
is located.

"""
import os, os.path
import sys

if __name__ == "__main__":
    sys.stderr.write("Running the update_vistrails_command.py script is not required anymore.\n"
                     "It will be removed in future releases.\n")
    # TODO : Remove this file after 2.2

    # get VisTrails folder
    vt_folder = os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
    command_file = os.path.join(vt_folder, 'VisTrails.command')

    file_contents = """#This will execute VisTrails in a separate terminal window
#If you get an error saying:
#Found another instance of VisTrails running
#Sending parameters to main instance  []
#Failed:  QLocalSocket::connectToServer: Connection refused
#make sure VisTrails is not already running and simply try to run the script again
#This might indicate that VisTrails did not quit properly

cd "$(dirname "$0")"
DYLD_LIBRARY_PATH= VisTrails.app/Contents/MacOS/vistrails
"""
    f = open(command_file, 'w')
    f.write(file_contents)
    f.close()

###############################################################################
##
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
""" This will create the media_dir directory structure required by vistrails
server when used as a remote server with crowdlabs (www.crowdlabs.org) 

usage: python create_server_media_dir_structure.py /path/to/media_dir

If media_dir does not exist, it will be created.

"""

import sys
import os, os.path

folders = [["wf_execution"],
           ["graphs", "workflows"],
           ["graphs", "vistrails"],
           ["medleys", "images"]]
def path_exists_and_not_empty(path):
    """path_exists_and_not_empty(path:str) -> boolean 
    Returns True if given path exists and it's not empty, otherwise returns 
    False.
    
    """
    if os.path.exists(path):
        for root, dirs, file_names in os.walk(path):
            break
        if len(file_names) > 0 or len(dirs) > 0:
            return True
    return False

if __name__ == "__main__":
    args = sys.argv
    error = False
    if len(args) == 2:
        media_dir = args[1]
    else:
        print "Usage: %s /path/to/media_dir" % args[0]
        sys.exit(0)
    if os.path.exists(media_dir):
        if not os.path.isdir(media_dir):
            print "Error: %s exists and it is not a directory." %media_dir
            error = True
        elif path_exists_and_not_empty(media_dir):
            print "Error: %s exists and it is not empty. "% media_dir
            error = True
    else:
        print "%s does not exist. Trying to create directory..."%media_dir
        try:
            os.mkdir(media_dir)
        except Exception, e:
            print "Error creating %s directory: %s" % (media_dir, str(e))
            error = True
    if not error:
        print "Creating inner structure... "
        for path_list in folders:
            folder = os.path.join(media_dir, os.path.join(*path_list))
            print "   ", folder
            try:
                os.makedirs(folder)
            except Exception, e:
                print "Error creating %s directory: %s" % (folder, str(e))
        print "Done."
    else:
        print "There was an error. Please check the messages above. "
        sys.exit(1)
    
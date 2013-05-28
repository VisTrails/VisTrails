###############################################################################
##
## Copyright (C) 2011-2013, NYU-Poly.
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

# This runs on crowdlabs only!!!
# the input file format should follow this:
#   path=/vistrails/vistrails.py
#   wfid=598
#   buildalways=true
#   other=width=0.45\linewidth 
#
# if path is not provided we will run on crowdlabs
# the buildalways and port lines are optional
# at least a version or a tag must be provided
# please notice that the tag has precedence over version. If a tag is passed
# we will query the database to get the latest version number.

import sys
import os.path
import os
from httplib import HTTP
from urlparse import urlparse
import urllib2
import re
                     
###############################################################################

def usage():
    print "Usage: "
    print "   %s path/to/options_file" % sys.argv[0]
    sys.exit(1)

###############################################################################
    
def bool_conv(x):
    """bool_conv(x: str) -> bool
    Converts a string to boolean.
    
    """
    s = str(x).upper()
    if s == 'TRUE':
        return True
    if s == 'FALSE':
        return False
    
###############################################################################    

def path_exists_and_not_empty(path):
    """path_exists_and_not_empty(path:str) -> boolean 
    Returns True if given path exists and it's not empty, otherwise returns 
    False.
    
    """
    if os.path.exists(path):
        for root, dirs, file_names in os.walk(path):
            break
        if len(file_names) > 0:
            return True
    return False

###############################################################################
 
def build_vistrails_cmd_line(path_to_vistrails, host, db_name, vt_id, version,
                             port, path_to_figures):
    """ build_vistrails_cmd_line(path_to_vistrails: str, host: str,
                                 db_name: str, vt_id: str, version: str,
                                 path_to_figures: str) -> str
        Build the command line to run vistrails with the given parameters.
    """
    cmd_line = 'python "%s" -b -e "%s" -t %s -f %s -r %s -u %s "%s:%s" > \
vistrails.log' % (vt_user,
                  path_to_vistrails,
                  path_to_figures,
                  host,
                  db_name,
                  port,
                  vt_id,
                  version)
    return cmd_line

###############################################################################

def generate_latex(server_url, wfid, path_to_figures, graphics_options):
    """generate_latex(wfid: str, execute: bool,
                      showspreadsheetonly: bool, path_to_figures: str,
                      graphics_options: str)  -> str
        This generates a piece of latex code containing the \href command and
        a \includegraphics command for each image generated.
    """
    url_params = "details/%s/" % wfid
    url_params = url_params.replace("%","\%")
    url = "%s%s"%(server_url,url_params)
    href = "\href{%s}{" % url
    for root, dirs, file_names in os.walk(path_to_figures):
        break
    n = len(file_names)
    s = ''
    
    for f in file_names:
        filename = os.path.join(path_to_figures,f).replace("%","\%")
        if graphics_options:
            s += "\includegraphics[%s]{%s}\n" % (graphics_options, filename)
        else:
            s += "\includegraphics{%s}\n" % filename
    s += "}"
    return href+s

###############################################################################

def generate_latex_error(error_msg):
    """ generate_latex_error(error_msg: str) -> str
        this generates a piece of latex code with an error message.
    """
    s = """\\PackageError{vistrails}{ An error occurred when executing vistrails. \\MessageBreak
%s
}{vistrails}""" % error_msg
    return s
###############################################################################

def run_vistrails_locally(path_to_vistrails, host, db_name, vt_id,
                          version, port, path_to_figures, build_always=False,
                          tag='', execute=False, showspreadsheetonly=False):
    """run_vistrails_locally(path_to_vistrails: str, host: str,
                             db_name: str, vt_id: str, version: str, port: str,
                             path_to_figures: str) -> tuple(bool, str)
        Run vistrails and returns a tuple containing a boolean saying if it was
        successful or not and the latex code.
    """
    cmd_line = build_vistrails_cmd_line(path_to_vistrails, host, db_name, vt_id,
                                        version, port, path_to_figures)
    
    if not os.path.exists(path_to_figures):
        os.makedirs(path_to_figures)
        result = os.system(cmd_line)
        if result != 0:
            os.rmdir(path_to_figures)
            msg = "See vistrails.log for more information."
            return (False, generate_latex_error(msg))
        
    else:
        if build_always or not path_exists_and_not_empty(path_to_figures):
            result = os.system(cmd_line)
            if result != 0:
                os.rmdir(path_to_figures)
                msg = "See vistrails.log for more information."
                return (False, generate_latex_error(msg))

    return (True, generate_latex(host, db_name, vt_id, version, port, tag,
                                 execute, showspreadsheetonly,
                                 path_to_figures, graphics_options))

###############################################################################

def run_vistrails_remotely(path_to_vistrails, wfid, path_to_figures,
                           build_always=False):
    """run_vistrails_remotely(path_to_vistrails: str, host: str,
                              db_name: str, vt_id: str, version: str, port: str,
                              path_to_figures: str, build_always: bool,
                              tag:str, execute: bool, showspreadsheetonly: bool)
                                   -> tuple(bool, str)
        Run vistrails and returns a tuple containing a boolean saying if it was
        successful or not and the latex code.
    """
    def check_url(url):
        try:
            p = urlparse(url)
            h = HTTP(p[1])
            h.putrequest('HEAD', p[2])
            h.endheaders()
            if h.getreply()[0] == 200:
                return True
            else:
                return False
        except:
            return False
        
    def download(url,filename):
        try:
            furl = urllib2.urlopen(url)
            f = file(filename,'wb')
            f.write(furl.read())
            f.close()
            return True
        except:
            return False
        
    def download_as_text(url):
        try:
            furl = urllib2.urlopen(url)
            s = furl.read()
            return s
        except:
            return None
    
    if not path_exists_and_not_empty(path_to_figures) or build_always:
        if not os.path.exists(path_to_figures):
            os.makedirs(path_to_figures)
        
        if check_url(path_to_vistrails):
            website = "://".join(urlparse(path_to_vistrails)[:2])
            request = "generate_visualization_image/%s/"%wfid
            url = path_to_vistrails + request
            #print url
            try:
                page = download_as_text(url)
                # we will look for a list of comma separated in the html
                images = page.split(",")
                if len(images) > 0:
                    failed = False
                    for i in images:
                        msg = ''
                        pngfile = i.strip()
                        if not check_url(pngfile):
                            img = website + pngfile
                        else:
                            img = pngfile
                        if not download(img, os.path.join(path_to_figures,
                                        os.path.basename(img))):
                            msg += "Error when download image: %s. <return>" %\
                                   img
                            failed = True
                    if not failed:
                        return (True, generate_latex(path_to_vistrails, wfid,
                                                     path_to_figures,
                                                     graphics_options))
                    else:
                        return (False, generate_latex_error(msg))
                else:
                    msg = "Web server returned: %s" % page
                    return (False, generate_latex_error(msg))
            
            except Exception, e:
                return (False, generate_latex_error(str(e)))
        else:
            msg = "Invalid url: %s" % path_to_vistrails
            return (False, generate_latex_error(msg))
    else:
        return (True, generate_latex(path_to_vistrails, wfid,
                                     path_to_figures, graphics_options))
    
    
###############################################################################

def check_path(path):
    """check_path(path:str) -> bool
    Checks if it's a valid path.
    If path is valid, we will update it to be a realpath.
    
    """
    result = False
    new_path = os.path.realpath(path)
    if os.path.isfile(new_path):
        path = new_path
        result = True
    else:
        result = False
    return result

###############################################################################

options_file = None
try:
    options_file = open(sys.argv[1])
except IndexError:
    usage()
    
lines = options_file.readlines()
path_to_vistrails = None
wfid = None
graphics_options = None
build_always = False
run_locally = True

for line in lines:
    args = line.split("=")
    if len(args) > 2:
        args[1] = "=".join(args[1:])
    if args[0] == "path":
        path_to_vistrails = args[1].strip(" \n")
    elif args[0] == "wfid":
        wfid = args[1].strip(" \n")
    elif args[0] == "buildalways":
        build_always = bool_conv(args[1].strip(" \n"))
    elif args[0] == "other":
        graphics_options = args[1].strip(" \n")

# then we use the combination wfid to
# create a unique folder. 
# TODO: Maybe we should use a hash of this. For now let's keep it
# legible.

path_to_figures = os.path.join("vistrails_images",
                               "%s" % wfid)

# if the path_to_vistrails point to a file that exists on disk, we will use
# it, else let's assume it's a url (we still check if the url is valid inside
# the run_vistrails_remotely function)

run_locally = check_path(path_to_vistrails)

if run_locally:
    result, latex = run_vistrails_locally(path_to_vistrails, host, db_name,
                                          vt_id, version, port, path_to_figures,
                                          build_always, version_tag, execute,
                                          showspreadsheetonly)
else:
    result, latex = run_vistrails_remotely(path_to_vistrails, wfid,
                                           path_to_figures, build_always)
    
# the printed answer will be included inline by the latex compiler.
print latex
if result == True:
    sys.exit(0)
else:
    sys.exit(1)

#!/usr/bin/env python
############################################################################
## Copyright (C) 2006-2010 University of Utah. All rights reserved.
##
## This file is part of VisTrails.
##
## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following to ensure GNU General Public
## Licensing requirements will be met:
## http://www.opensource.org/licenses/gpl-license.php
##
## If you are unsure which license is appropriate for your use (for
## instance, you are interested in developing a commercial derivative
## of VisTrails), please contact us at vistrails@sci.utah.edu.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################

# the input file format should follow this:
#   path=/Users/emanuele/code/vistrails/branches/v1.2/vistrails/vistrails.py
#   host=vistrails.sci.utah.edu
#   db=vistrails
#   version=598
#   vtid=8
#   port=3306
#   buildalways=true
#   tag=Some text
#   other=width=0.45\linewidth 
#
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
import MySQLdb

vt_user = 'vtserver' # this is the user used to connect to the database.
                     # we use a user with readonly and no password set
                     
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

def generate_latex(host, db_name, vt_id, version, port, tag, execute,
                   showspreadsheetonly, path_to_figures, graphics_options):
    """generate_latex(host: str, db_name:str, vt_id: str, version: str,
                      port:str, tag: str, execute: bool,
                      showspreadsheetonly: bool, path_to_figures: str,
                      graphics_options: str)  -> str
        This generates a piece of latex code containing the \href command and
        a \includegraphics command for each image generated.
    """
    url_params = "getvt=%s&version=%s&db=%s&host=%s&port=%s&tag=%s&\
execute=%s&showspreadsheetonly=%s" % (vt_id,
                                      urllib2.quote(version),
                                      db_name,
                                      host,
                                      port,
                                      urllib2.quote(tag),
                                      execute,
                                      showspreadsheetonly)
    url_params = url_params.replace("%","\%")
    url = "http://www.vistrails.org/extensions/download.php?%s"% url_params
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

def run_vistrails_remotely(path_to_vistrails, host, db_name, vt_id,
                           version, port, path_to_figures, build_always=False,
                           tag='', execute=False, showspreadsheetonly=False,
                           pdf=False):
    """run_vistrails_remotely(path_to_vistrails: str, host: str,
                              db_name: str, vt_id: str, version: str, port: str,
                              path_to_figures: str, build_always: bool,
                              tag:str, execute: bool, showspreadsheetonly: bool,
                              pdf: bool)
                                   -> tuple(bool, str)
        Run vistrails and returns a tuple containing a boolean saying if it was
        successful or not and the latex code.
    """ 
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
            request = "?host=%s&db=%s&vt=%s&version=%s&port=%s&pdf=%s" % (host,
                                                                   db_name,
                                                                   vt_id,
                                                                   urllib2.quote(version),
                                                                   port,
                                                                   pdf)
            url = path_to_vistrails + request
            #print url
            try:
                page = download_as_text(url)
                # we will look for images and other files embedded in the html
                re_imgs = re.compile('<img[^>]*/>')
                re_src = re.compile('(.*src=")([^"]*)"')
                re_a = re.compile('<a[^>]*>[^<]*</a>')
                re_href = re.compile('(.*href=")([^"]*)"')
                images = re_imgs.findall(page)
                files = re_a.findall(page)
                failed = False
                msg = ''
                if len(images) > 0 or len(files) > 0:
                    for i in images:
                        pngfile = re_src.match(i).groups()[1]
                        if not check_url(pngfile):
                            img = website + pngfile
                        else:
                            img = pngfile
                    
                        if not download(img, os.path.join(path_to_figures,
                                         os.path.basename(img))):
                            msg += "Error when downloading image: %s. <return>" %\
                                   img
                            failed = True
                        
                    for f in files:
                        otherfile = re_href.match(f).groups()[1]
                    
                        if not check_url(otherfile):
                            filename = website + otherfile
                        else:
                            filename = otherfile
                    
                        if not download(filename, os.path.join(path_to_figures,
                                        os.path.basename(filename))):
                            msg += "Error when downloading file: %s. <return>" %\
                                    filename
                            failed = True
                        
                    if not failed :
                        return (True, generate_latex(host, db_name, vt_id,
                                                     version, port, tag,
                                                     execute,
                                                     showspreadsheetonly,
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
        return (True, generate_latex(host, db_name, vt_id,
                                     version, port, tag, execute,
                                     showspreadsheetonly,
                                     path_to_figures, graphics_options))
    
    
###############################################################################

def check_path(path):
    """check_path(path:str) -> bool
    Checks if it's a valid system path.
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

###############################################################################

options_file = None
try:
    options_file = open(sys.argv[1])
except IndexError:
    usage()
    
lines = options_file.readlines()
path_to_vistrails = None
host = None
db_name = None
vt_id = None
version = None
graphics_options = None
build_always = False
port = '3306'
version_tag = ''
showspreadsheetonly = False
execute = False
pdf = False

for line in lines:
    args = line.split("=")
    if len(args) > 2:
        args[1] = "=".join(args[1:])
    if args[0] == "path":
        path_to_vistrails = args[1].strip(" \n")
    elif args[0] == "host":
        host = args[1].strip(" \n")
    elif args[0] == "db":
        db_name = args[1].strip(" \n")
    elif args[0] == "vtid":
        vt_id = args[1].strip(" \n")
    elif args[0] == "version":
        version = args[1].strip(" \n")
    elif args[0] == "port":
        port = args[1].strip(" \n")
    elif args[0] == "buildalways":
        build_always = bool_conv(args[1].strip(" \n"))
    elif args[0] == "tag":
        version_tag = args[1].strip(" \n")
    elif args[0] == "execute":
        execute = bool_conv(args[1].strip(" \n"))
    elif args[0] == "showspreadsheetonly":
        showspreadsheetonly = bool_conv(args[1].strip(" \n"))
        if showspreadsheetonly:
            execute = True
    elif args[0] == 'pdf':
        pdf = bool_conv(args[1].strip(" \n"))
    elif args[0] == "other":
        graphics_options = args[1].strip(" \n")

# then we use the combination host_db_name_port_vt_id_version to
# create a unique folder. 
# TODO: Maybe we should use a hash of this. For now let's keep it
# legible.
out_type = "png"
if pdf:
    out_type = 'pdf'
path_to_figures = os.path.join("vistrails_images",
                               "%s_%s_%s_%s_%s_%s" % (host, db_name, port,
                                                   vt_id,
                                                   version,
                                                   out_type))    

# if the path_to_vistrails point to a file that exists on disk, we will use
# it, else let's assume it's a url (we still check if the url is valid inside
# the run_vistrails_remotely function)

if check_path(path_to_vistrails): #run locally
    result, latex = run_vistrails_locally(path_to_vistrails, host, db_name,
                                          vt_id, version, port, path_to_figures,
                                          build_always, version_tag, execute,
                                          showspreadsheetonly,pdf)
elif check_url(path_to_vistrails): #run from the web
    result, latex = run_vistrails_remotely(path_to_vistrails, host, db_name,
                                          vt_id, version, port, path_to_figures,
                                          build_always, version_tag, execute,
                                          showspreadsheetonly,pdf)
else:
    result, latex = (False, 
                     "%s is not a valid url nor a valid path to vistrails.py" %\
                       (path_to_vistrails))
    
# the printed answer will be included inline by the latex compiler.
print latex
if result == True:
    sys.exit(0)
else:
    sys.exit(1)

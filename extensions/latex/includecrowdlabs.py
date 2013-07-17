#!/usr/bin/env python
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
#   url=http://www.crowdlabs.org
#   wfid=598
#   vtid=34
#   pdf=true
#   workflow=true
#   buildalways=true
#   other=width=0.45\linewidth 
#
# buildalways, workflow and pdf are optional
# at least one of wfid or vtid must be provided

import sys
import os.path
import os
from httplib import HTTP
from urlparse import urlparse
import urllib2
import re
import logging

debug = True
logger = None
             
###############################################################################

def log(msg):
    global debug, logger
    if debug:
        logger.debug(msg)
        
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
    log("generate_latex")
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

def download(url,filename):
    try:
        furl = urllib2.urlopen(url)
        f = file(filename,'wb')
        f.write(furl.read())
        f.close()
        return True
    except:
        return False
        
###############################################################################    

def download_as_text(url):
    try:
        furl = urllib2.urlopen(url)
        s = furl.read()
        return s
    except:
        return None

###############################################################################

def download_workflow(url_crowdlabs, wfid, path_to_figures, wgraph=False,
                      pdf=False, build_always=False):
    """download_workflow(url_crowdlabs: str, wfid: str, path_to_figures: str, 
                         wgraph: bool, pdf: bool, build_always: bool)
                                   -> tuple(bool, str)
        Try to download image from url and returns a tuple containing a boolean 
        saying if it was successful or not and the latex code.
    """    
    log("download_workflow")
    if not path_exists_and_not_empty(path_to_figures) or build_always:
        if not os.path.exists(path_to_figures):
            os.makedirs(path_to_figures)
        
        if check_url(url_crowdlabs):
            website = "://".join(urlparse(url_crowdlabs)[:2])
            if not wgraph:
                if not pdf:
                    request = "/vistrails/workflows/generate_visualization_image/%s/"%wfid
                else:
                    request = "/vistrails/workflows/generate_visualization_pdf/%s/"%wfid
            else:
                if not pdf:
                    request = "/vistrails/workflows/generate_pipeline_image/%s/"%wfid
                else:
                    request = "/vistrails/workflows/generate_pipeline_pdf/%s/"%wfid

            url = url_crowdlabs + request
            log("from %s"%url)
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
                        log("success")
                        return (True, generate_latex(url_crowdlabs + "/vistrails/workflows/",
                                                     wfid,
                                                     path_to_figures,
                                                     graphics_options))
                    else:
                        log("failed: %s"%msg)
                        return (False, generate_latex_error(msg))
                else:
                    msg = "Web server returned: %s" % page
                    log("failed: %s"%msg)
                    return (False, generate_latex_error(msg))
            
            except Exception, e:
                log("failed with exception: %s"%str(e))
                return (False, generate_latex_error(str(e)))
        else:
            msg = "Invalid url: %s" % url_crowdlabs
            return (False, generate_latex_error(msg))
    else:
        log("using cached images")
        return (True, generate_latex(url_crowdlabs  + "/vistrails/workflows/", 
                                     wfid,
                                     path_to_figures, 
                                     graphics_options))
    
###############################################################################

def download_tree(url_crowdlabs, vtid, path_to_figures, pdf=False,
                  build_always=False):
    """download_tree(url_crowdlabs: str, vtid: str, path_to_figures: str, 
                     pdf: bool, build_always: bool)
                                   -> tuple(bool, str)
        Try to download tree from url and returns a tuple containing a boolean 
        saying if it was successful or not and the latex code.
    """
    log("download_tree")
    if not path_exists_and_not_empty(path_to_figures) or build_always:
        if not os.path.exists(path_to_figures):
            os.makedirs(path_to_figures)
        
        if check_url(url_crowdlabs):
            website = "://".join(urlparse(url_crowdlabs)[:2])
            if not pdf:
                request = "/vistrails/generate_provenance_image/%s/"%vtid
            else:
                request = "/vistrails/generate_provenance_pdf/%s/"%vtid
            url = url_crowdlabs + request
            log("from %s"%url)
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
                        log("success")
                        return (True, generate_latex(url_crowdlabs + "/vistrails/", vtid,
                                                     path_to_figures,
                                                     graphics_options))
                    else:
                        log("failed: %s"%msg)
                        return (False, generate_latex_error(msg))
                else:
                    msg = "Web server returned: %s" % page
                    log("failed: %s"%msg)
                    return (False, generate_latex_error(msg))
            
            except Exception, e:
                log("failed with exception: %s"%str(e))
                return (False, generate_latex_error(str(e)))
        else:
            msg = "Invalid url: %s" % url_crowdlabs
            log("failed: %s"%msg)
            return (False, generate_latex_error(msg))
    else:
        log("using cached images")
        return (True, generate_latex(url_crowdlabs + "/vistrails/", vtid,
                                     path_to_figures, graphics_options))
    
    
###############################################################################

def check_url(url):
    """check_url(url:str) -> bool
    Check if a URL exists using the url's header.
    """
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

if debug:
    logger = logging.getLogger("crowdLabsLatex")
    handler = logging.FileHandler('crowdlabs.log')
    handler.setFormatter(logging.Formatter('crowdLabsLatex - %(asctime)s %(message)s'))
    handler.setLevel(logging.DEBUG)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    log("***********************************")
    log("********* SESSION START ***********")
        
lines = options_file.readlines()
urlcrowdlabs = None
wfid = None
vtid = None
pdf = False
wgraph = False
tree = False

graphics_options = None
build_always = False
run_locally = True

for line in lines:
    args = line.split("=")
    if len(args) > 2:
        args[1] = "=".join(args[1:])
    if args[0] == "url":
        urlcrowdlabs = args[1].strip(" \n")
    elif args[0] == "wfid":
        wfid = args[1].strip(" \n")
    elif args[0] == "vtid":
        vtid = args[1].strip(" \n")
        tree = True
    elif args[0] == 'pdf':
        pdf = bool_conv(args[1].strip(" \n"))    
    elif args[0] == 'workflow':
        wgraph = bool_conv(args[1].strip(" \n"))
    elif args[0] == "buildalways":
        build_always = bool_conv(args[1].strip(" \n"))
    elif args[0] == "other":
        graphics_options = args[1].strip(" \n")

# then we use the combination wf_wfid or vt_vtid to
# create a unique folder. 
# TODO: Maybe we should use a hash of this. For now let's keep it
# legible.
out_type = "png"
if pdf:
    out_type = 'pdf'

if check_url(urlcrowdlabs):
    
    if wfid is not None:
        folder_suffix = ""
        if wgraph:
            folder_suffix = "_graph"
        path_to_figures = os.path.join("crowdlabs_images",
                                       "wf_%s_%s%s" %(wfid, out_type,folder_suffix))
        log(path_to_figures)
        result, latex = download_workflow(urlcrowdlabs, wfid,
                                          path_to_figures, wgraph, pdf, build_always)        

    elif vtid is not None:
        path_to_figures = os.path.join("crowdlabs_images",
                                       "vt_%s_%s" %(vtid, out_type))
        log(path_to_figures)
        result, latex = download_tree(urlcrowdlabs, vtid,
                                          path_to_figures, pdf, build_always)
        
else:
    result, latex = (False, generate_latex_error("Invalid url %s." % urlcrowdlabs))
    
# the printed answer will be included inline by the latex compiler.
print latex
if result == True:
    log("********** SESSION END ************")
    log("***********************************")
    sys.exit(0)
else:
    log("********** SESSION END ************")
    log("***********************************")
    sys.exit(1)

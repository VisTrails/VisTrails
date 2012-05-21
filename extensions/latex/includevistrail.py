#!/usr/bin/env python
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

# the input file format should follow this:
#   path=/Users/emanuele/code/vistrails/branches/v1.2/vistrails/vistrails.py
#   python=/path/to/python
#   env=DYLD_LIBRARY_PATH= 
#   download=http://url.from.where.download.vt.files
#   host=vistrails.sci.utah.edu
#   user=username
#   db=vistrails
#   filename=path_to_vtfile
#   version=598
#   vtid=8
#   port=3306
#   buildalways=true
#   tag=Some text
#   pdf=false
#   workflow=false
#   tree=false
#   getvtl=false
#   embedworkflow=false
#   includefulltree=false
#   other=width=0.45\linewidth 
#
# the buildalways and port lines are optional
# at least a version or a tag must be provided
# if filename is provided host, db, user and vtid are ignored
# please notice that the tag has precedence over version. If a tag is passed
# we will query the database to get the latest version number.

import sys
import os.path
import os
from httplib import HTTP
from urlparse import urlparse
import urllib2
import re
import logging
import shlex
import shutil
import subprocess
import platform

systemType = platform.system()
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

def vtl_exists_in_folder(path):
    """vtl_exists_in_folder(path:str) -> boolean 
    Returns True if given path contains a *.vtl file, otherwise returns False.
    
    """
    for dirpath, dirname,filenames in os.walk(path):
        for f in filenames:
            ext = os.path.splitext(f)[1]
            if ext == ".vtl":
                return True
    return False

###############################################################################

def build_vtl_file(download_url, filename, version, tag, 
                   execute, showspreadsheetonly, embedWorkflow=False,
                   includeFullTree=False):
    log("build_vtl_file")
    try:
        basename = os.path.splitext(os.path.basename(filename))[0]
        if version != None:
            basename += "_%s_%s_%s_%s"%(version,tag,showspreadsheetonly,execute)
        basename += ".vtl"
        vtl_filename = os.path.join(download_url, basename)
        header = '<vtlink filename="%s" version="%s" execute="%s" showSpreadsheetOnly="%s" \
forceDB="%s" tag="%s"/>'%(filename,#os.path.abspath(filename),
              str(version),
              str(execute),
              str(showspreadsheetonly),
              str(False),
              str(tag))
    except Exception, e:
        log("Error: %s"%str(e))
    log("will open %s"%vtl_filename)
    log("vtlfile contents: %s"%header)
    f = open(vtl_filename, "w")
    f.write(header)
    f.close()
    return "run:"+ os.path.abspath(vtl_filename).replace("\\","/")

###############################################################################

def build_vtl_db(download_url, host, db_name, vt_id, version, port, tag, 
                   execute, showspreadsheetonly, embedWorkflow=False, 
                   includeFullTree=False):
    """build_download_vtl_request(host: str, db_name:str, vt_id: str, version: str,
                      port:str, tag: str, execute: bool,
                      showspreadsheetonly: bool)  -> str  """
    log("build_vtl_db")
    try:
        basename = "%s_%s_%s_%s_%s_%s_%s_%s_%s.vtl"%(host,
                                               db_name,
                                               port,
                                               vt_id,
                                               version,
                                               execute,
                                               embedWorkflow,
                                               includeFullTree,
                                               showspreadsheetonly)
        vtl_filename = os.path.join(download_url, basename)
        header = '<vtlink host="%s" database="%s" port="%s" vtid="%s" \
version="%s" execute="%s" showSpreadsheetOnly="%s" forceDB="%s" />'%(
              host,
              db_name,
              str(port),
              str(vt_id),
              str(version),
              str(execute),
              str(showspreadsheetonly),
              str(True))
    except Exception, e:
        log("Error: %s"%str(e))
    log("will open %s"%vtl_filename)
    log("vtlfile contents: %s"%header)
    f = open(vtl_filename, "w")
    f.write(header)
    f.close()
    return "run:"+ os.path.abspath(vtl_filename)

###############################################################################
def download(url,filename, folder=None):
    """download(url:string, filename: string) -> Boolean
    Downloads a binary file from url to filename and returns True (success)
    or False (failure)
    
    """
    try:
        furl = urllib2.urlopen(url)
        if filename is None and folder is not None:
            info = furl.info()
            re_filename = re.compile('attachment;filename=(.*vtl)')
            attach = info.dict['content-disposition']
            filename = os.path.join(folder,
                                    re_filename.match(attach).groups()[0])
            
        log("downloading file: " + filename)
        f = file(filename,'wb')
        f.write(furl.read())
        f.close()
        return True
    except Exception, e:
        log(str(e))
        return False
    
###############################################################################        

def download_as_text(url):
    """download_as_text(url: string) -> string
    Downloads a url as text. It will return None if it failed.
    
    """
    try:
        furl = urllib2.urlopen(url)
        s = furl.read()
        return s
    except:
        return None

###############################################################################

def build_download_vtl_request(download_url, host, db_name, vt_id, version, port, tag, 
                   execute, showspreadsheetonly, embedWorkflow=False, 
                   includeFullTree=False):
    """build_download_vtl_request(host: str, db_name:str, vt_id: str, version: str,
                      port:str, tag: str, execute: bool,
                      showspreadsheetonly: bool)  -> str
        This generates a piece of latex code containing the \href command and
        a \includegraphics command for each image generated.
    """
    
    url_params = "getvt=%s&db=%s&host=%s&port=%s&tag=%s&\
execute=%s&showspreadsheetonly=%s&embedWorkflow=%s&includeFullTree=%s" % (vt_id,
                                                    db_name,
                                                    host,
                                                    port,
                                                    urllib2.quote(tag),
                                                    execute,
                                                    showspreadsheetonly,
                                                    embedWorkflow,
                                                    includeFullTree)
    if version is not None:
        url_params += "&version=%s"%urllib2.quote(version)
    url_params = url_params.replace("%","\%")
    url = "%s?%s"%(download_url, url_params)
    
    return url    

###############################################################################

def _download_content(url, request, path_to_figures):
    """_download_images(url:string, request:string, path_to_figures:string) -> (Boolean, 
                                                                message)
    Downloads all images and pdf files listed in url and saves them to
    path_to_figures
    
    """ 
    website = url
    url = request
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
                    msg += "Error when downloading image: %s. <return>" %img
                    failed = True
                        
            for f in files:
                otherfile = re_href.match(f).groups()[1]
                    
                if not check_url(otherfile):
                    filename = website + otherfile
                else:
                    filename = otherfile
                    
                if not download(filename, os.path.join(path_to_figures,
                                os.path.basename(filename))):
                    msg += "Error when downloading file: %s. <return>"%filename
                    failed = True
                        
            if not failed :
                return (True, "")
            else:
                return (False, msg)
        else:
            msg = "url: '%s' \n returned: %s" % (url,page.strip())
            return (False, msg)
            
    except Exception, e:
        return (False, str(e))
    
def build_vistrails_cmd_line_db(path_to_vistrails, path_to_python,
                                env_for_vistrails, host, 
                                db_name, db_user, vt_id, version, port, 
                                path_to_figures, pdf=False, wgraph=False, 
                                tree=False):
    """ build_vistrails_cmd_line_db(path_to_vistrails: str, env_for_vistrails: str,
                                     host: str, db_name: str, vt_id: str, 
                                     version: str, path_to_figures: str,
                                     pdf:bool, wgraph:bool, tree: bool) -> list
        Build the command line to run vistrails with the given parameters.
    """
    #dump pdf
    if pdf:
        pdfoption = ["-p"]
    else:
        pdfoption = []
    #user
    if db_user is not None and db_user != "":
        useroption = ['-u', '%s'%db_user]
    else:
        useroption = []
    #dump tree and workflow graph
    if wgraph:
        graphoption = ['-G', '%s'%os.path.abspath(path_to_figures)]
    elif tree:
        graphoption = ['-U' ,'%s'%os.path.abspath(path_to_figures)]
    else:
        graphoption = ['-e', '%s'%os.path.abspath(path_to_figures)]
    #don't select a workflow
    if version is not None:
        voption = ":%s"%version
    else:
        voption = ""
        
    prefix = ['%s'%path_to_vistrails]
    if path_to_vistrails.endswith(".py"):
        prefix = ['%s'%path_to_python,
                  '%s'%path_to_vistrails]
    cmd_line = prefix + ['-b'] + graphoption + ['-t', host, '-f',db_name] + \
             useroption + ['-r', port] + pdfoption + [ '%s%s'%(vt_id, voption)]
    return cmd_line

###############################################################################

def build_vistrails_cmd_line_file(path_to_vistrails, path_to_python,
                                  env_for_vistrails, filename, 
                                  version, path_to_figures, pdf=False, 
                                  wgraph=False, tree=False):
    """ build_vistrails_cmd_line_file(path_to_vistrails: str, 
                                      env_for_vostrails: str, filename: str,
                                      version: str, path_to_figures: str,
                                      pdf:bool, wgraph:bool, tree: bool) -> str
        Build the command line to run vistrails with the given parameters.
    """
    #dump pdf
    if pdf:
        pdfoption = ["-p"]
    else:
        pdfoption = []
    #dump tree and workflow graph
    if wgraph:
        graphoption = ['-G','%s'%os.path.abspath(path_to_figures)]
    elif tree:
        graphoption = ['-U','%s'%os.path.abspath(path_to_figures)]
    else:
        graphoption = ['-e','%s'%os.path.abspath(path_to_figures)]
    #don't select a workflow
    if version is not None:
        voption = ":%s"%version
    else:
        voption = ''
    prefix = ['%s'%path_to_vistrails]
    if path_to_vistrails.endswith(".py"):
        prefix = ['%s'%path_to_python,
                  '%s'%path_to_vistrails]
    cmd_line = prefix + ['-b'] + graphoption + pdfoption + \
               [ "%s%s"%(os.path.abspath(filename),voption)]
                      
    return cmd_line

###############################################################################

def generate_latex_db(is_local, download_url, host, db_name, vt_id, version, port, tag, 
                      execute, showspreadsheetonly, path_to_figures, 
                      graphics_options, embedWorkflow=False, 
                      includeFullTree=False):
    """generate_latex(host: str, db_name:str, vt_id: str, version: str,
                      port:str, tag: str, execute: bool,
                      showspreadsheetonly: bool, path_to_figures: str,
                      graphics_options: str, embedWorkflow: bool, 
                      includeFullTree:bool)  -> str
        This generates a piece of latex code containing the \href command and
        a \includegraphics command for each image generated.
    """
    if not is_local:
        if download_url is not None and download_url != "":
            url = build_download_vtl_request(download_url, host, db_name, vt_id, 
                                             version, port, tag, execute, 
                                             showspreadsheetonly, 
                                             embedWorkflow=embedWorkflow,
                                             includeFullTree=includeFullTree)
            href = "\href{%s}{" % url
    else:
        if download_url is not None and download_url != "":
            url = build_vtl_db(download_url, host, db_name, vt_id, 
                            version, port, tag, execute, 
                            showspreadsheetonly, embedWorkflow=embedWorkflow,
                            includeFullTree=includeFullTree)
            href = "\href{%s}{" % url
    ALLOWED_GRAPHICS = [".png", ".jpg", ".pdf"]
    images = []
    for root, dirs, file_names in os.walk(path_to_figures):
        for f in file_names:
            ext = os.path.splitext(f)[1]
            if ext in ALLOWED_GRAPHICS:
                images.append(f)
        break
    n = len(images)
    s = ''
    
    for f in images:
        filename = os.path.join(path_to_figures,f).replace("%","\%")
        if graphics_options:
            s += "\includegraphics[%s]{%s}\n" % (graphics_options, filename.replace("\\","/"))
        else:
            s += "\includegraphics{%s}\n" % filename.replace("\\","/")
    
    if download_url is not None and download_url != "":
        return href + s + "}"
    else:
        return s

###############################################################################

def generate_latex_file(download_url, vtfile, version, tag, 
                      execute, showspreadsheetonly, path_to_figures, 
                      graphics_options,embedWorkflow=False, 
                      includeFullTree=False):
    """generate_latex(host: str, db_name:str, vt_id: str, version: str,
                      port:str, tag: str, execute: bool,
                      showspreadsheetonly: bool, path_to_figures: str,
                      graphics_options: str)  -> str
        This generates a piece of latex code containing the \href command and
        a \includegraphics command for each image generated.
    """
    log("generate_latex_file")
    if download_url is not None and download_url != "":
        url = build_vtl_file(download_url, vtfile, version, tag, execute, 
                             showspreadsheetonly, embedWorkflow=False)
        href = "\href{%s}{" % url
        log(url)
    ALLOWED_GRAPHICS = [".png", ".jpg", ".pdf"]
    images = []
    for root, dirs, file_names in os.walk(path_to_figures):
        for f in file_names:
            ext = os.path.splitext(f)[1]
            if ext in ALLOWED_GRAPHICS:
                images.append(f)
        break
    n = len(images)
    s = ''
    for f in images:
        filename = os.path.join(path_to_figures,f).replace("%","\%")
        if graphics_options:
            s += "\includegraphics[%s]{%s}\n" % (graphics_options, filename.replace("\\","/"))
        else:
            s += "\includegraphics{%s}\n" % filename.replace("\\","/")
    
    if download_url is not None and download_url != "":
        return href + s + "}"
    else:
        return s

###############################################################################

def generate_latex_error(error_msg):
    """ generate_latex_error(error_msg: str) -> str
        this generates a piece of latex code with an error message.
    """
    error_msg = error_msg.replace("\n", "\\MessageBreak ")
    s = """\\PackageError{vistrails}{ An error occurred when executing vistrails. \\MessageBreak
%s
}{}""" % error_msg
    return s

###############################################################################

def run_vistrails_locally_db(path_to_vistrails, path_to_python, 
                             env_for_vistrails, host, db_name, 
                             db_user, vt_id,
                             version, port, path_to_figures, build_always=False,
                             tag='', execute=False, showspreadsheetonly=False,
                             pdf=False, embedWorkflow=False, 
                             includeFullTree=False):
    """run_vistrails_locally_db(path_to_vistrails: str, host: str,
                             db_name: str, vt_id: str, version: str, port: str,
                             path_to_figures: str) -> tuple(bool, str)
        Run vistrails and returns a tuple containing a boolean saying if it was
        successful or not and the latex code.
    """
    v = version
    if tag != '':
        v = tag
    cmd_line = build_vistrails_cmd_line_db(path_to_vistrails, path_to_python,
                                           env_for_vistrails, 
                                           host, db_name, db_user, vt_id,
                                           v, port, path_to_figures, pdf)
    log("run_vistrails_locally_db")
    log("cmdline: %s"%cmd_line)

    if build_always:
        #force to remove the folder so we avoid stale results
        if os.path.exists(path_to_figures):
            shutil.rmtree(path_to_figures)
            
    if not os.path.exists(path_to_figures):
        os.makedirs(path_to_figures)
        
    if build_always or not path_exists_and_not_empty(path_to_figures):
        my_env = os.environ
        sep = ":"
        if systemType in ["Windows", "Microsoft"]:
            sep = ";"
        if env_for_vistrails != '':
            data = shlex.split(env_for_vistrails)
            for d in data:
                (name,val) = d.split("=")
                pos = val.find("$"+name)
                if pos != -1:
                    if pos == 0:
                        my_env[name] = my_env.get(name,'') + \
                                       val[pos+len(name)+1:]
                    else:
                        if pos + len(name) == len(val) -1:
                            my_env[name] = val[0:pos] + my_env.get(name,'')
                        else:
                            my_env[name] = val[0:pos] + my_env.get(name,'') + \
                                           val[pos+len(name)+1:]
                else:
                    my_env[name] = val
        log("env: %s"%my_env)
        if systemType in ['Windows', 'Microsoft']:
            proc = subprocess.Popen(cmd_line,
                                    env=my_env)
        else:
            proc = subprocess.Popen(cmd_line, shell=False,
                                    env=my_env,
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    close_fds=True)
        proc.wait()
        log("result: %s"%proc.returncode)
        if proc.stdout:
            lines = proc.stdout.readlines()
            log("stdout: %s"%lines)
        if proc.returncode != 0:
            shutil.rmtree(path_to_figures)
            msg = "See vistrails.log for more information."
            return (False, generate_latex_error(msg))
        
    return (True, generate_latex_db(True,os.getcwd(), host, db_name, vt_id, version, port, tag,
                                    execute, showspreadsheetonly, 
                                    path_to_figures, graphics_options, 
                                    embedWorkflow, includeFullTree))

###############################################################################

def run_vistrails_locally_file(path_to_vistrails, path_to_python,
                               env_for_vistrails, filename, 
                               version, path_to_figures, build_always=False,
                               tag='', execute=False, showspreadsheetonly=False,
                               pdf=False, embedWorkflow=False, 
                               includeFullTree=False):
    """run_vistrails_locally_file(path_to_vistrails: str, filename: str,
                                  version: str, path_to_figures: str,
                                  build_always:bool, tag:str, execute:bool,
                                  showspreadsheetonly:bool, pdf:bool) -> 
                                                               tuple(bool, str)
        Run vistrails and returns a tuple containing a boolean saying if it was
        successful or not and the latex code.
    """
    v = version
    if tag != '':
        v = tag
    cmd_line = build_vistrails_cmd_line_file(path_to_vistrails, path_to_python, 
                                             env_for_vistrails,
                                             filename, v, path_to_figures, 
                                             pdf)
    log("run_vistrails_locally_file")
    log("cmdline: %s"%cmd_line)
    if build_always:
        #force to remove the folder so we avoid stale results
        if os.path.exists(path_to_figures):
            shutil.rmtree(path_to_figures)
            
    if not os.path.exists(path_to_figures):
        log("creating image path")
        os.makedirs(path_to_figures)
                
    if build_always or not path_exists_and_not_empty(path_to_figures):
        my_env = os.environ
        sep = ":"
        if systemType in ["Windows", "Microsoft"]:
            sep = ";"
        if env_for_vistrails != '':
            data = shlex.split(env_for_vistrails)
            log("env_for_vistrails: %s"%data)
            for d in data:
                (name,val) = d.split("=")
                pos = val.find("$"+name)
                if pos != -1:
                    if pos == 0:
                        my_env[name] = my_env.get(name,'') + \
                                       val[pos+len(name)+1:]
                    else:
                        if pos + len(name) == len(val) -1:
                            my_env[name] = val[0:pos] + my_env.get(name,'')
                        else:
                            my_env[name] = val[0:pos] + my_env.get(name,'') + \
                                           val[pos+len(name)+1:]
                else:
                    my_env[name] = val
        log("env: %s"%my_env)
        if systemType in ['Windows', 'Microsoft']:
            proc = subprocess.Popen(cmd_line,
                                    env=my_env,
                                    stdout=subprocess.PIPE)
        else:
            proc = subprocess.Popen(cmd_line, shell=False,
                                    env=my_env,
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    close_fds=True)
        proc.wait()
        log("result: %s"%proc.returncode)
        if proc.stdout:
            lines = proc.stdout.readlines()
            log("stdout: %s"%lines)
        if proc.returncode != 0:
            shutil.rmtree(path_to_figures)
            msg = "See vistrails.log for more information."
            return (False, generate_latex_error(msg))
    log("will generate latex")
    try:
        return (True, generate_latex_file(os.path.dirname(os.path.abspath(filename)), 
                                      filename, version, tag,
                                      execute, showspreadsheetonly,
                                      path_to_figures, graphics_options,
                                      embedWorkflow, includeFullTree))
    except Exception, e:
        log("Error: %s"%str(e))
###############################################################################

def get_vt_graph_locally_db(path_to_vistrails, path_to_python,
                            env_for_vistrails, host, db_name,
                            db_user, vt_id, port, path_to_figures, 
                            build_always=False, pdf=False,
                            embedWorkflow=False, includeFullTree=False):
    """get_vt_graph_locally_db(path_to_vistrails: str, host: str,
                             db_name: str, vt_id: str, port: str,
                             path_to_figures: str, build_always: bool,
                             pdf:bool) -> tuple(bool, str)
        Run vistrails for loading a vistrail and dump the tree to a file and 
        returns a tuple containing a boolean saying if it was
        successful or not and the latex code.
    """
    cmd_line = build_vistrails_cmd_line_db(path_to_vistrails, path_to_python,
                                           env_for_vistrails, 
                                           host, db_name, db_user, vt_id,
                                           None, port, path_to_figures, pdf, False,
                                           True)
    log("get_vt_graph_locally_db")
    log("cmdline: %s"%cmd_line)
    if build_always:
        #force to remove the folder so we avoid stale results
        if os.path.exists(path_to_figures):
            shutil.rmtree(path_to_figures)
            
    if not os.path.exists(path_to_figures):
        os.makedirs(path_to_figures)
    
    if build_always or not path_exists_and_not_empty(path_to_figures):
        my_env = os.environ
        sep = ":"
        if systemType in ["Windows", "Microsoft"]:
            sep = ";"
        if env_for_vistrails != '':
            data = shlex.split(env_for_vistrails)
            for d in data:
                (name,val) = d.split("=")
                pos = val.find("$"+name)
                if pos != -1:
                    if pos == 0:
                        my_env[name] = my_env.get(name,'') + \
                                       val[pos+len(name)+1:]
                    else:
                        if pos + len(name) == len(val) -1:
                            my_env[name] = val[0:pos] + my_env.get(name,'')
                        else:
                            my_env[name] = val[0:pos] + my_env.get(name,'') + \
                                           val[pos+len(name)+1:]
                else:
                    my_env[name] = val
        log("env: %s"%my_env)        
        if systemType in ['Windows', 'Microsoft']:
            proc = subprocess.Popen(cmd_line,
                                    env=my_env,
                                    stdout=subprocess.PIPE)
        else:
            proc = subprocess.Popen(cmd_line, shell=False,
                                    env=my_env,
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    close_fds=True)
        proc.wait()
        log("result: %s"%proc.returncode)
        if proc.stdout:
            lines = proc.stdout.readlines()
            log("stdout: %s"%lines)
        if proc.returncode != 0:
            os.rmdir(path_to_figures)
            msg = "See vistrails.log for more information."
            return (False, generate_latex_error(msg))

    return (True, generate_latex_db(True, os.getcwd(), host, db_name, vt_id, None, port, '',
                                 False, False,
                                 path_to_figures, graphics_options,
                                 embedWorkflow, includeFullTree))

###############################################################################

def get_vt_graph_locally_file(path_to_vistrails, path_to_python,
                              env_for_vistrails, filename,
                              path_to_figures, build_always=False, pdf=False,
                              embedWorkflow=False, includeFullTree=False):
    """get_vt_graph_locally_file(path_to_vistrails: str, env_for_vistrails: str,
                                 filename: str, version: str, 
                                 path_to_figures: str,build_always: bool,
                                 pdf:bool) -> tuple(bool, str)
        Run VisTrails to load a workflow and dump the graph to a file and 
        returns a tuple containing a boolean saying whether it was
        successful and the latex code.
    """
    cmd_line = build_vistrails_cmd_line_file(path_to_vistrails, 
                                             path_to_python,
                                             env_for_vistrails, 
                                             filename, None, path_to_figures, 
                                             pdf, False, True)
    log("get_vt_graph_locally_file")
    log("cmdline: %s"%cmd_line)
    
    if build_always:
        #force to remove the folder so we avoid stale results
        if os.path.exists(path_to_figures):
            shutil.rmtree(path_to_figures)
            
    if not os.path.exists(path_to_figures):
        log("  creating images folder")
        os.makedirs(path_to_figures)
        
    if build_always or not path_exists_and_not_empty(path_to_figures):
        log("  folder was empty or forcing execution")
        my_env = os.environ
        sep = ":"
        if systemType in ["Windows", "Microsoft"]:
            sep = ";"
        if env_for_vistrails != '':
            data = shlex.split(env_for_vistrails)
            for d in data:
                (name,val) = d.split("=")
                pos = val.find("$"+name)
                if pos != -1:
                    if pos == 0:
                        my_env[name] = my_env.get(name,'') + \
                                       val[pos+len(name)+1:]
                    else:
                        if pos + len(name) == len(val) -1:
                            my_env[name] = val[0:pos] + my_env.get(name,'')
                        else:
                            my_env[name] = val[0:pos] + my_env.get(name,'') + \
                                           val[pos+len(name)+1:]
                else:
                    my_env[name] = val
        log("env: %s"%my_env)
        if systemType in ['Windows', 'Microsoft']:
            proc = subprocess.Popen(cmd_line,
                                    env=my_env,
                                    stdout=subprocess.PIPE)
        else:
            proc = subprocess.Popen(cmd_line, shell=False,
                                    env=my_env,
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    close_fds=True)
        proc.wait()
        log("result: %s"%proc.returncode)
        if proc.stdout:
            lines = proc.stdout.readlines()
            log("stdout: %s"%lines)
        if proc.returncode != 0:
            os.rmdir(path_to_figures)
            msg = "See vistrails.log and vistrails_run.log for more information."
            return (False, generate_latex_error(msg))
    else:
        log("  found cached images")
        
    return (True, generate_latex_file(os.path.dirname(os.path.abspath(filename)), 
                                      filename, None, '', False, 
                                      False, path_to_figures, 
                                      graphics_options, embedWorkflow, 
                                      includeFullTree))    

###############################################################################    

def get_wf_graph_locally_db(path_to_vistrails, path_to_python,
                            env_for_vistrails, host, db_name,
                            db_user, vt_id, version, port, path_to_figures, 
                            build_always=False, tag='', pdf=False,
                            embedWorkflow=False, includeFullTree=False):
    """get_wf_graph_locally_db(path_to_vistrails: str, host: str,
                             db_name: str, vt_id: str, version: str, port: str,
                             path_to_figures: str,build_always: bool,
                             tag: str, pdf:bool) -> tuple(bool, str)
        Run vistrails for loading a workflow and dump the graph to a file and 
        returns a tuple containing a boolean saying if it was
        successful or not and the latex code.
    """
    v = version
    if tag != '':
        v = tag
    cmd_line = build_vistrails_cmd_line_db(path_to_vistrails, 
                                           path_to_python, env_for_vistrails, 
                                           host, db_name, db_user, vt_id,
                                           v, port, path_to_figures, pdf, 
                                           True, False)
    log("get_wf_graph_locally_db")
    log("cmdline: %s"%cmd_line)
    if build_always:
        #force to remove the folder so we avoid stale results
        if os.path.exists(path_to_figures):
            shutil.rmtree(path_to_figures)
            
    if not os.path.exists(path_to_figures):
        log("  creating images folder")
        os.makedirs(path_to_figures)
        
    if build_always or not path_exists_and_not_empty(path_to_figures):
        log("  folder was empty or forcing execution")
        my_env = os.environ
        sep = ":"
        if systemType in ["Windows", "Microsoft"]:
            sep = ";"
        if env_for_vistrails != '':
            data = shlex.split(env_for_vistrails)
            for d in data:
                (name,val) = d.split("=")
                pos = val.find("$"+name)
                if pos != -1:
                    if pos == 0:
                        my_env[name] = my_env.get(name,'') + \
                                       val[pos+len(name)+1:]
                    else:
                        if pos + len(name) == len(val) -1:
                            my_env[name] = val[0:pos] + my_env.get(name,'')
                        else:
                            my_env[name] = val[0:pos] + my_env.get(name,'') + \
                                           val[pos+len(name)+1:]
                else:
                    my_env[name] = val
        log("env: %s"%my_env)
        if systemType in ['Windows', 'Microsoft']:
            log("env: %s"%my_env)
            proc = subprocess.Popen(cmd_line,
                                    env=my_env,
                                    stdout=subprocess.PIPE)
        else:
            proc = subprocess.Popen(cmd_line, shell=False,
                                    env=my_env,
                                    stdin=subprocess.PIPE,    
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    close_fds=True)
        proc.wait()
        log("result: %s"%proc.returncode)
        if proc.stdout:
            lines = proc.stdout.readlines()
            log("stdout: %s"%lines)
        if proc.returncode != 0:
            os.rmdir(path_to_figures)
            msg = "See vistrails.log for more information."
            return (False, generate_latex_error(msg))
    else:
        log("  found cached images")
        
    return (True, generate_latex_db(True, os.getcwd(), host, db_name, vt_id, version, 
                                    port, tag, execute, showspreadsheetonly,
                                    path_to_figures, graphics_options,
                                    embedWorkflow, includeFullTree))

###############################################################################

def get_wf_graph_locally_file(path_to_vistrails, path_to_python,
                              env_for_vistrails, filename,
                              version, path_to_figures, build_always=False,
                              tag='', pdf=False, embedWorkflow=False, 
                              includeFullTree=False):
    """get_wf_graph_locally_file(path_to_vistrails: str, env_for_vistrails: str,
                                 filename: str, version: str, 
                             path_to_figures: str,build_always: bool,
                             tag: str, pdf:bool) -> tuple(bool, str)
        Run VisTrails to load a workflow and dump the graph to a file and 
        returns a tuple containing a boolean saying whether it was
        successful and the latex code.
    """
    v = version
    if tag != '':
        v = tag
    cmd_line = build_vistrails_cmd_line_file(path_to_vistrails, path_to_python,
                                             env_for_vistrails, 
                                             filename, v, path_to_figures, 
                                             pdf, True, False)
    log("get_wf_graph_locally_file")
    log("cmdline: %s"%cmd_line)
    if build_always:
        #force to remove the folder so we avoid stale results
        if os.path.exists(path_to_figures):
            shutil.rmtree(path_to_figures)
            
    if not os.path.exists(path_to_figures):
        log("  creating images folder")
        os.makedirs(path_to_figures)
        
    if build_always or not path_exists_and_not_empty(path_to_figures):
        log("  folder was empty or forcing execution")
        my_env = os.environ
        sep = ":"
        if systemType in ["Windows", "Microsoft"]:
            sep = ";"
        if env_for_vistrails != '':
            data = shlex.split(env_for_vistrails)
            for d in data:
                (name,val) = d.split("=")
                pos = val.find("$"+name)
                if pos != -1:
                    if pos == 0:
                        my_env[name] = my_env.get(name,'') + \
                                       val[pos+len(name)+1:]
                    else:
                        if pos + len(name) == len(val) -1:
                            my_env[name] = val[0:pos] + my_env.get(name,'')
                        else:
                            my_env[name] = val[0:pos] + my_env.get(name,'') + \
                                           val[pos+len(name)+1:]
                else:
                    my_env[name] = val
        log("env: %s"%my_env)
        if systemType in ['Windows', 'Microsoft']:
            proc = subprocess.Popen(cmd_line,
                                    env=my_env,
                                    stdout=subprocess.PIPE)
        else:
            proc = subprocess.Popen(cmd_line, shell=False,
                                    env=my_env,
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    close_fds=True)
        proc.wait()
        log("result: %s"%proc.returncode)
        if proc.stdout:
            lines = proc.stdout.readlines()
            log("stdout: %s"%lines)
        if proc.returncode != 0:
            os.rmdir(path_to_figures)
            msg = "See vistrails.log for more information."
            return (False, generate_latex_error(msg))
    else:
        log("  found cached images")
    log("   about to return")    
    return (True, generate_latex_file(os.path.dirname(os.path.abspath(filename)), 
                                      filename, version, tag, execute, 
                                      showspreadsheetonly, path_to_figures, 
                                      graphics_options, embedWorkflow, 
                                      includeFullTree))    

###############################################################################

def run_vistrails_remotely(path_to_vistrails, download_url, host, db_name, vt_id,
                           version, port, path_to_figures, build_always=False,
                           tag='', execute=False, showspreadsheetonly=False,
                           pdf=False, embedWorkflow=False, 
                           includeFullTree=False):
    """run_vistrails_remotely(path_to_vistrails: str, download_url: str host: str,
                              db_name: str, vt_id: str, version: str, port: str,
                              path_to_figures: str, build_always: bool,
                              tag:str, execute: bool, showspreadsheetonly: bool,
                              pdf: bool, embedWorkflow:bool, 
                              includeFullTree:bool)
                                   -> tuple(bool, str)
        Call vistrails remotely to execute a workflow and returns a tuple 
        containing a boolean saying whether it was successful and the latex 
        code.
    """ 
    log("run_vistrails_remotely")
    if build_always:
        #force to remove the folder so we avoid stale results
        if os.path.exists(path_to_figures):
            shutil.rmtree(path_to_figures)
            
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
            log("will download from: " + url)
            
            (result, msg) = _download_content(website, url, path_to_figures)
            if result == True:
                log("success")
                return (result, generate_latex_db(False, download_url, host, db_name, vt_id, 
                                               version, port, tag, execute,
                                               showspreadsheetonly,
                                               path_to_figures, 
                                               graphics_options,
                                               embedWorkflow, includeFullTree))
            else:
                log("Error: " + msg)
                return (result, generate_latex_error(msg))
        else:
            msg = "Invalid url: %s" % path_to_vistrails
            log("Error: " + msg)
            return (False, generate_latex_error(msg))
    else:
        log("using cached files")
        return (True, generate_latex_db(False, download_url, host, db_name, vt_id, 
                                     version, port, tag, execute, 
                                     showspreadsheetonly,
                                     path_to_figures, graphics_options,
                                     embedWorkflow, includeFullTree))
                
###############################################################################

def get_vt_graph_remotely(path_to_vistrails, download_url, host, db_name, vt_id,
                          port, path_to_figures, build_always=False, pdf=False,
                          embedWorkflow=False, includeFullTree=False):
    """get_vt_graph_remotely(path_to_vistrails: str, download_url: str, host: str,
                              db_name: str, vt_id: str, port: str,
                              path_to_figures: str, build_always: bool, pdf: bool)
                                   -> tuple(bool, str)
        Get the version tree image of a vistrail and returns a tuple containing 
        a boolean saying whether it was successful and the latex code.
    """    
    log("get_vt_graph_remotely")
    if build_always:
        #force to remove the folder so we avoid stale results
        if os.path.exists(path_to_figures):
            shutil.rmtree(path_to_figures)
            
    if not path_exists_and_not_empty(path_to_figures) or build_always:
        if not os.path.exists(path_to_figures):
            os.makedirs(path_to_figures)
        
        if check_url(path_to_vistrails):
            website = "://".join(urlparse(path_to_vistrails)[:2])
            request = "?host=%s&db=%s&vt=%s&port=%s&pdf=%s&showtree=True" % (host,
                                                                   db_name,
                                                                   vt_id,
                                                                   port,
                                                                   pdf)
            url = path_to_vistrails + request
            log("will download from: " + url)
            
            (result, msg) = _download_content(website, url, path_to_figures)
            if result == True:
                log("success")
                return (result, generate_latex_db(False, download_url, host, db_name, 
                                                  vt_id, None, 
                                                  port, '', False,
                                                  False,
                                                  path_to_figures, 
                                                  graphics_options,
                                                  embedWorkflow, includeFullTree))
            else:
                log("Error: " + msg)
                return (result, generate_latex_error(msg))
        else:
            msg = "Invalid url: %s" % path_to_vistrails
            log("Error: " + msg)
            return (False, generate_latex_error(msg))
    else:
        log("using cached files")
        return (True, generate_latex_db(False, download_url, host, db_name, vt_id, 
                                     None, port, '', 
                                     False, False,
                                     path_to_figures, graphics_options,
                                     embedWorkflow, includeFullTree))
        
###############################################################################

def get_wf_graph_remotely(path_to_vistrails, download_url, host, db_name, vt_id,
                           version, port, path_to_figures, build_always=False, 
                           tag='', pdf=False, embedWorkflow=False, 
                           includeFullTree=False):
    """get_wf_graph_remotely(path_to_vistrails: str, download_url:str, host: str,
                              db_name: str, vt_id: str, version: str, port: str,
                              path_to_figures: str, build_always: bool, 
                              tag:str, pdf: bool) -> tuple(bool, str)
        Get the graph of a workflow and returns a tuple containing a boolean 
        saying whether it was successful and the latex code.
    """
    log("get_wf_graph_remotely") 
    
    if build_always:
        #force to remove the folder so we avoid stale results
        if os.path.exists(path_to_figures):
            shutil.rmtree(path_to_figures)
            
    if not path_exists_and_not_empty(path_to_figures) or build_always:
        if not os.path.exists(path_to_figures):
            os.makedirs(path_to_figures)
        
        if check_url(path_to_vistrails):
            website = "://".join(urlparse(path_to_vistrails)[:2])
            request = "?host=%s&db=%s&vt=%s&version=%s&port=%s&pdf=%s&showworkflow=True" % (host,
                                                                   db_name,
                                                                   vt_id,
                                                                   urllib2.quote(version),
                                                                   port,
                                                                   pdf)
            url = path_to_vistrails + request
            log("will download from: " + url)
            
            (result, msg) = _download_content(website, url, path_to_figures)
            if result == True:
                log("success")
                return (result, generate_latex_db(False, download_url, host, db_name, 
                                               vt_id, version, 
                                               port, tag, False,
                                               False,
                                               path_to_figures, 
                                               graphics_options,
                                               embedWorkflow, includeFullTree))
            else:
                log("Error: " + msg)
                return (result, generate_latex_error(msg))
        else:
            msg = "Invalid url: %s" % path_to_vistrails
            log("Error: " + msg)
            return (False, generate_latex_error(msg))
    else:
        log("using cached files")
        return (True, generate_latex_db(False, download_url, host, db_name, vt_id, 
                                     version, port, tag, 
                                     False, False,
                                     path_to_figures, graphics_options,
                                     embedWorkflow, includeFullTree))
            
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
        except Exception, e:
            log(str(e))
            return False

###############################################################################

options_file = None
try:
    options_file = open(sys.argv[1])
except IndexError:
    usage()
    
if debug:
    logger = logging.getLogger("VisTrailsLatex")
    handler = logging.FileHandler('vistrails.log')
    handler.setFormatter(logging.Formatter('VisTrailsLatex - %(asctime)s %(message)s'))
    handler.setLevel(logging.DEBUG)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    log("***********************************")
    log("********* SESSION START ***********")
    
lines = options_file.readlines()
path_to_vistrails = None
path_to_python = None
download_url = None
env_for_vistrails = None
host = None
db_name = None
db_user = None
vt_id = None
filename = None
version = None
graphics_options = None
build_always = False
port = '3306'
version_tag = ''
showspreadsheetonly = False
execute = False
pdf = False
wgraph = False
tree = False
getvtl = False
embedWorkflow=False
includeFullTree=False
for line in lines:
    args = line.split("=")
    if len(args) > 2:
        args[1] = "=".join(args[1:])
    if args[0] == "path":
        path_to_vistrails = args[1].strip(" \n")
    elif args[0] == "python":
        path_to_python = args[1].strip(" \n")
    elif args[0] == "env":
        env_for_vistrails = args[1].strip(" \n")
    elif args[0] == "download":
        download_url = args[1].strip(" \n")
    elif args[0] == "host":
        host = args[1].strip(" \n")
    elif args[0] == "db":
        db_name = args[1].strip(" \n")
    elif args[0] == "user":
        db_user = args[1].strip(" \n")
    elif args[0] == "vtid":
        vt_id = args[1].strip(" \n")
    elif args[0] == "filename":
        filename = args[1].strip(" \n")
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
    elif args[0] == 'pdf':
        pdf = bool_conv(args[1].strip(" \n"))
    elif args[0] == 'workflow':
        wgraph = bool_conv(args[1].strip(" \n"))
    elif args[0] == 'tree':
        tree = bool_conv(args[1].strip(" \n"))
    elif args[0] == 'getvtl':
        getvtl = bool_conv(args[1].strip(" \n"))
    elif args[0] == 'embedworkflow':
        embedWorkflow = bool_conv(args[1].strip(" \n"))
    elif args[0] == 'includefulltree':
        includeFullTree = bool_conv(args[1].strip(" \n"))
    elif args[0] == "other":
        graphics_options = args[1].strip(" \n")

if showspreadsheetonly:
    execute = True
# then we use the combination host_db_name_port_vt_id_version or
# filename_version to create a unique folder.

# TODO: Maybe we should use a hash of this. For now let's keep it
# legible.
out_type = "png"
if pdf:
    out_type = 'pdf'
if filename is not None:
    path_to_figures = os.path.join("vistrails_images",
                                   "%s_%s_%s" % (filename,
                                                 version,
                                                 out_type))
    if tree:
        #no need to encode version
        path_to_figures = os.path.join("vistrails_images",
                                       "%s_%s" % (filename, out_type))
    elif wgraph:
        path_to_figures = os.path.join("vistrails_images",
                                       "%s_%s_%s_graph" % (filename,
                                                           version,
                                                           out_type)) 
else:
    path_to_figures = os.path.join("vistrails_images",
                               "%s_%s_%s_%s_%s_%s" % (host, db_name, port,
                                                   vt_id,
                                                   version,
                                                   out_type))    
    if tree:
        #no need to encode version
        path_to_figures = os.path.join("vistrails_images",
                                       "%s_%s_%s_%s_%s" % (host, db_name, port,
                                                           vt_id,
                                                           out_type)) 
    elif wgraph:
        path_to_figures = os.path.join("vistrails_images",
                                       "%s_%s_%s_%s_%s_%s_graph" % (host, db_name, port,
                                                                    vt_id,
                                                                    version,
                                                                    out_type))    
# if the path_to_vistrails point to a file that exists on disk, we will use
# it, else let's assume it's a url (we still check if the url is valid inside
# the run_vistrails_remotely function)
log("path_to_figures: %s"%path_to_figures)
if check_path(path_to_vistrails) and filename is None: #run locally
    if tree:
        # we don't need to actually run the workflow, we just get the
        # tree
        log("will run get_vt_graph_locally_db")
        result, latex = get_vt_graph_locally_db(path_to_vistrails,
                                                path_to_python,
                                                env_for_vistrails, host, db_name,
                                                db_user,
                                                vt_id, port, path_to_figures,
                                                build_always, pdf, embedWorkflow,
                                                includeFullTree)
    elif wgraph:
        # we don't need to actually run the workflow, we just get the
        # workflow graph
        log("will run get_wf_graph_locally_db")
        result, latex = get_wf_graph_locally_db(path_to_vistrails,
                                                path_to_python,
                                                env_for_vistrails, host, db_name,
                                                db_user,
                                                vt_id, version, port, path_to_figures,
                                                build_always, version_tag, pdf,
                                                embedWorkflow, includeFullTree)
    else:    
        result, latex = run_vistrails_locally_db(path_to_vistrails,
                                                 path_to_python,
                                                 env_for_vistrails, host, db_name,
                                                 db_user,
                                                 vt_id, version, port, path_to_figures,
                                                 build_always, version_tag, execute,
                                                 showspreadsheetonly, pdf,
                                                 embedWorkflow, includeFullTree)
elif check_path(path_to_vistrails) and filename is not None: #run locally
    if tree:
        # we don't need to actually run the workflow, we just get the
        # tree
        result, latex = get_vt_graph_locally_file(path_to_vistrails,
                                                  path_to_python,
                                                  env_for_vistrails, filename,
                                                  path_to_figures,
                                                  build_always, pdf,
                                                  embedWorkflow, includeFullTree)
    elif wgraph:
        # we don't need to actually run the workflow, we just get the
        # workflow graph
        log("will run get_wf_graph_locally_file")
        result, latex = get_wf_graph_locally_file(path_to_vistrails,
                                                  path_to_python,
                                                  env_for_vistrails, filename,
                                                  version, path_to_figures,
                                                  build_always, version_tag, pdf,
                                                  embedWorkflow, includeFullTree)
    else:    
        result, latex = run_vistrails_locally_file(path_to_vistrails,
                                                   path_to_python,
                                                   env_for_vistrails, filename,
                                                   version, path_to_figures,
                                                   build_always, version_tag, 
                                                   execute, showspreadsheetonly,
                                                   pdf,embedWorkflow, 
                                                   includeFullTree)
elif (not build_always or
      (build_always and check_url(path_to_vistrails))): #run from the web
    if tree:
        result, latex = get_vt_graph_remotely(path_to_vistrails, download_url,
                                              host, db_name,
                                              vt_id, port, path_to_figures,
                                              build_always, pdf, embedWorkflow,
                                              includeFullTree)
    elif wgraph:
        result, latex = get_wf_graph_remotely(path_to_vistrails, download_url,
                                              host, db_name,
                                              vt_id, version, port, path_to_figures,
                                              build_always,version_tag, pdf,
                                              embedWorkflow, includeFullTree)
    else:
        result, latex = run_vistrails_remotely(path_to_vistrails, download_url,
                                               host, db_name,
                                               vt_id, version, port, path_to_figures,
                                               build_always, version_tag, execute,
                                               showspreadsheetonly,pdf,
                                               embedWorkflow, includeFullTree)
    #download vtl file
    if getvtl:
        if (not build_always and not vtl_exists_in_folder(path_to_figures) or
            build_always):
                url = build_download_vtl_request(download_url, host, db_name, 
                                                 vt_id, version, port, version_tag, 
                                                 execute, showspreadsheetonly, 
                                                 embedWorkflow=embedWorkflow, 
                                                 includeFullTree=includeFullTree)
                log("get_vtl %s"%url)
                if download(url, filename=None, folder=path_to_figures) == False:
                    log("Error when downloading vtl to %s"%path_to_figures)
        
                
else:
    result, latex = (False, 
                     generate_latex_error("It is possible that %s is not a valid \
url nor a valid path to vistrails.py or that you don't have an internet connection \
and some workflows have the buildalways option. If you already have cached files, \
try removing the buildalways option from vistrails latex command" %\
                     (path_to_vistrails)))
    
# the printed answer will be included inline by the latex compiler.
print latex
if result == True:
    # we will also create a temporary file that can be used to include the
    # images directly
    if not os.path.isdir('cached'):
        if os.path.exists('cached'):
            print generate_latex_error("cached exists and it is not a folder")
            sys.exit(1)
        else:
            os.mkdir('cached')
    if tree:
        texbasename = "%s_%s_%s_%s_%s.tex" % (host, db_name, port, vt_id,out_type)
    elif wgraph:
        texbasename = "%s_%s_%s_%s_%s_%s_graph.tex" % (host, db_name, port, vt_id,
                                                    version, out_type)
    else:
        texbasename = "%s_%s_%s_%s_%s_%s.tex" % (host, db_name, port, vt_id, 
                                              version, out_type)
    texfilename = os.path.join('cached', texbasename)
    texfile = open(texfilename, 'w')
    texfile.write(latex)
    texfile.close()
    log("********** SESSION END ************")
    log("***********************************")
    sys.exit(0)
else:
    log("********** SESSION END ************")
    log("***********************************")
    sys.exit(1)

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

"""Routines common to Linux and OSX."""
import os
import os.path
import stat
import subprocess
import sys
import core.utils
import re

def executable_is_in_path(filename):
    """executable_is_in_path(filename): string
    Tests if filename corresponds to an executable file on the path. Returns
the filename if true, or an empty string if false."""
    cmdline = ['which','%s' % filename]
    output = []
    result = execute_cmdline(cmdline, output)
    if result == 1:
        return ""
    if result != 0:
        msg = ("'%s' failed. Return code %s. Output: %s" %
               (cmdline, result, output))
        raise core.utils.VistrailsInternalError(msg)
    else:
        output = output[0][:-1]
        return output

def executable_is_in_pythonpath(filename):
    """executable_is_in_pythonpath(filename: str)
    Check if exename can be reached in the PYTHONPATH environment. Return
    the filename if true, or an empty string if false.
    
    """
    pathlist = sys.path
    for dir in pathlist:
        fullpath = os.path.join(dir, filename)
        try:
            st = os.stat(fullpath)
        except os.error:
            continue        
        if stat.S_ISREG(st[stat.ST_MODE]):
            return filename
    return ""

def list2cmdline(lst):
    for el in lst:
        assert type(el) in [str,unicode]
    return subprocess.list2cmdline(lst)

def execute_cmdline(lst, output):
    """execute_cmdline(lst: list of str, output)-> int
    Builds a command line enquoting the arguments properly and executes it
    using subprocess.Popen. It returns the error code and the output is on 'output'.

    cscheid: why don't we return a tuple of int, lst instead of mutating that list?

    """
    process = subprocess.Popen(lst, shell=False,
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT,
                               close_fds=True)
    # cscheid: Should this be busy-waiting? What's going on here?
    result = None
    while result == None:
        result = process.poll()
    output.extend(process.stdout.readlines())
    return result

def get_executable_path(executable_name):
    #FIXME
    return None

def execute_piped_cmdlines(cmd_list_list):
    stdin = subprocess.PIPE
    for cmd_list in cmd_list_list:
        cmd_line = list2cmdline(cmd_list)
        process = subprocess.Popen(cmd_line, shell=True,
                                   stdin=stdin,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   close_fds=True)
        stdin = process.stdout
    (output, errs) = process.communicate()
    result = process.returncode
    return (result, output, errs)

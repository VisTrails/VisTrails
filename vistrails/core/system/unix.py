############################################################################
##
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

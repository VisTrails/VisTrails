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
import os
import shutil
import sys
import stat
import subprocess
import core.system

import java.lang.Runtime
import java.lang.System

# Try to guess the real platform we are executing on
is_windows = "win" in java.lang.System.getProperty("os.name").lower()

##############################################################################
def guess_total_memory():
    """ guess_total_memory() -> int
    Return system memory in megabytes.

    """
    runtime = java.lang.Runtime.getRuntime()
    return runtime.totalMemory()

def temporary_directory():
    """ temporary_directory() -> str
    Returns the path to the system's temporary directory.

    """
    return java.lang.System.getProperty("java.io.tmpdir")

def home_directory():
    """ home_directory() -> str
    Returns user's home directory

    """
    return java.lang.System.getProperty("user.home")

def remote_copy_program():
    if is_windows:
        return "pscp -P"
    else:
        return "scp -p"

def remote_shell_program():
    if is_windows:
        return "plink -P"
    else:
        return "ssh -p"

def graph_viz_dot_command_line():
    """ graph_viz_dot_command_line() -> str
    Returns dot command line

    """
    return 'dot -Tplain -o'

def remove_graph_viz_temporaries():
    pass

def link_or_copy(src, dst):
    """link_or_copy(src:str, dst:str) -> None
    Copies file src to dst

    """
    shutil.copyfile(src, dst)

def executable_is_in_path(filename):
    """ executable_is_in_path(filename: str) -> string
    Check if exename can be reached in the PATH environment. Return
    the filename if true, or an empty string if false.

    """
    pathlist = (os.environ['PATH'].split(os.pathsep) +
                [core.system.vistrails_root_directory(),
                 "."])
    for dir in pathlist:
        # On Windows, paths may be enclosed in ""
        if dir.startswith('"') and dir.endswith('"'):
            dir = dir[1:-1]
        fullpath = os.path.join(dir, filename)
        try:
            st = os.stat(fullpath)
        except os.error:
            try:
                st = os.stat(fullpath+'.exe')
            except:
                continue
        if stat.S_ISREG(st[stat.ST_MODE]):
            return filename
    return ""

def executable_is_in_pythonpath(filename):
    """ executable_is_in_pythonpath(filename: str) -> string
    Check if exename can be reached in the PYTHONPATH environment. Return
    the filename if true, or an empty string if false.

    """
    pathlist = sys.path
    for dir in pathlist:
        fullpath = os.path.join(dir, filename)
        try:
            st = os.stat(fullpath)
        except os.error:
            try:
                st = os.stat(fullpath+'.exe')
            except:
                continue
        if stat.S_ISREG(st[stat.ST_MODE]):
            return filename
    return ""

def list2cmdline(lst):
    for el in lst:
        assert type(el) in [str, unicode]
    return subprocess.list2cmdline(lst)

def execute_cmdline(lst, output):
    """execute_cmdline(lst: list of str)-> int Builds a command line
    enquoting the arguments properly and executes it using popen4. It
    returns the output on output. popen4 doesn't return a code, so it
    will always return 0

    """
    proc = subprocess.Popen(lst, shell=True, stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    proc.wait()
    if proc.stdout:
        output.extend(proc.stdout.readlines())
    return proc.returncode

def get_executable_path(executable_name):
    filename = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../', executable_name))
    if os.path.exists(filename) or os.path.exists(filename+'.exe'):
        return filename
    return None

def execute_piped_cmdlines(cmd_list_list):
    stdin = subprocess.PIPE
    for cmd_list in cmd_list_list:
        cmd_line = list2cmdline(cmd_list)
        process = subprocess.Popen(cmd_line, shell=True,
                                   stdin=stdin,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdin = process.stdout
    (output, errs) = process.communicate()
    result = process.returncode
    return (result, output, errs)

################################################################################

import unittest

class TestJython(unittest.TestCase):
    """ Class to test Jython specific functions """

    def test1(self):
        """ Test if guess_total_memory() is returning an int >= 0"""
        result = guess_total_memory()
        self.assertTrue(type(result) == type(1) or type(result) == type(1L))
        self.assertTrue(result >= 0, "guess_total_memory()=%d" % result)

    def test2(self):
        """ Test if home_directory is not empty """
        result = home_directory()
        self.assertNotEqual(result, "")

    def test3(self):
        """ Test if temporary_directory is not empty """
        result = temporary_directory()
        self.assertNotEqual(result, "")

    def test_executable_file_in_path(self):
        result = executable_is_in_path('ping')
        self.assertNotEqual(result, "")

if __name__ == '__main__':
    unittest.main()

###############################################################################
##
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
import subprocess

try:
    from ctypes import windll, Structure, c_ulong, c_ulonglong, byref, sizeof
    importSuccess = True

    class WIN32MEMORYSTATUSEX(Structure):
        """ Structure that represents memory information returned by
        Windows API

        """
        _fields_ = [
            ('dwLength', c_ulong),
            ('dwMemoryLoad', c_ulong),
            ('dwTotalPhys', c_ulonglong),
            ('dwAvailPhys', c_ulonglong),
            ('dwTotalPageFile', c_ulonglong),
            ('dwAvailPageFile', c_ulonglong),
            ('dwTotalVirtual', c_ulonglong),
            ('dwAvailVirtual', c_ulonglong),
            ('dwAvailExtendedVirtual', c_ulonglong),
            ]

except ImportError:
    importSuccess = False


__all__ = ['guess_total_memory', 'home_directory',
           'list2cmdline', 'remote_copy_program', 'remote_shell_program',
           'graph_viz_dot_command_line', 'remove_graph_viz_temporaries',
           'link_or_copy', 'executable_is_in_path', 'execute_cmdline',
           'get_executable_path', 'execute_piped_cmdlines', 'execute_cmdline2',
           'shell_font_face', 'shell_font_size',
           'TestWindows']


##############################################################################
def parse_meminfo():
    """
    parse_meminfo() -> long
    Calls Windows 32 API GlobalMemoryStatus(Ex) to get memory information
    It requires ctypes module

    """
    try:
        kernel32 = windll.kernel32

        result = WIN32MEMORYSTATUSEX()
        result.dwLength = sizeof(WIN32MEMORYSTATUSEX)
        kernel32.GlobalMemoryStatusEx(byref(result))
    except Exception:
        return -1
    return long(result.dwTotalPhys / 1024)

def guess_total_memory():
    """ guess_total_memory() -> int
    Return system memory in megabytes. If ctypes is not installed it returns -1

    """
    if importSuccess:
        return parse_meminfo()
    else:
        return -1

def home_directory():
    """ home_directory() -> str
    Returns user's home directory using windows environment variables
    $HOMEDRIVE and $HOMEPATH

    """
    if len(os.environ['HOMEPATH']) == 0:
        return '\\'
    else:
        return os.environ['HOMEDRIVE'] + os.environ['HOMEPATH']

def remote_copy_program():
    return "pscp -P"

def remote_shell_program():
    return "plink -P"

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
    """ executable_is_in_path(filename: str) -> bool
    Check if exename can be reached in the PATH environment.
    """
    pathlist = os.environ['PATH'].split(os.pathsep) + ["."]
    exts = os.environ['PATHEXT'].split(os.pathsep)
    for path in pathlist:
        for ext in exts:
            fullpath = os.path.join(path, filename) + ext
            if os.path.isfile(fullpath):
                return True
    return False

def list2cmdline(lst):
    for el in lst:
        assert isinstance(el, basestring)
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
    """get_executable_path(executable_name: str) -> str
    Get the absolute filename of an executable, searching in VisTrails's top
    directory then the PATH.
    """
    exts = os.environ['PATHEXT'].split(os.pathsep)

    # Search in top directory
    filename = os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            '../../..',
            executable_name))
    for ext in exts:
        if os.path.isfile(filename + ext):
            return filename

    # Search in path
    pathlist = os.environ['PATH'].split(os.pathsep) + ["."]
    for path in pathlist:
        for ext in exts:
            fullpath = os.path.join(path, executable_name) + ext
            if os.path.isfile(fullpath):
                return os.path.abspath(fullpath)

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

def execute_cmdline2(cmd_list):
    return execute_piped_cmdlines([cmd_list])

def shell_font_face():
    return 'Courier New'

def shell_font_size():
    return 8

################################################################################

import unittest

class TestWindows(unittest.TestCase):
    """ Class to test Windows specific functions """

    def test1(self):
        """ Test if guess_total_memory() is returning an int >= 0"""
        result = guess_total_memory()
        assert isinstance(result, (int, long))
        assert result >= 0

    def test2(self):
        """ Test if home_directory is not empty """
        result = home_directory()
        assert result != ""

    def test_executable_file_in_path(self):
        self.assertTrue(executable_is_in_path('cmd'))

if __name__ == '__main__':
    unittest.main()

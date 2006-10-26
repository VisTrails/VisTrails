import os
from PyQt4 import QtGui

try:
    from ctypes import *
    importSuccess = True
    
    class WIN32MEMORYSTATUS(Structure):
        """ Structure that represents memoory information returned by Windows API"""
        _fields_ = [
            ('dwLength', c_ulong),
            ('dwMemoryLoad', c_ulong),
            ('dwTotalPhys', c_ulong),
            ('dwAvailPhys', c_ulong),
            ('dwTotalPageFile', c_ulong),
            ('dwAvailPageFile', c_ulong),
            ('dwTotalVirtual', c_ulong),
            ('dwAvailVirtual', c_ulong)
            ]

except ImportError:
    importSuccess = False
    

def parse_meminfo():
    """ 
    parse_meminfo() -> int
    Calls Windows 32 API GlobalMemoryStatus(Ex) to get memory information 
    It requires ctypes module
    
    """ 
    try:
        kernel32 = windll.kernel32

        result = WIN32MEMORYSTATUS()
        result.dwLength = sizeof(WIN32MEMORYSTATUS)
        kernel32.GlobalMemoryStatus(byref(result))
    except:
        return -1
    return result.dwTotalPhys

def guessTotalMemory():
    if importSuccess:
        return parse_meminfo()
    else:
        return -1

def temporaryDirectory():
    if os.environ.has_key('TMP'):
        return os.environ['TMP'] + '\\'
    elif os.environ.has_key('TEMP'):
        return os.environ['TEMP'] + '\\'
    else:
        return 'c:/'

def homeDirectory():
    # FIXME: get the right one
    if len(os.environ['HOMEPATH']) == 0:
	return '\\'
    else:
	return os.environ['HOMEDRIVE'] + os.environ['HOMEPATH']

def remoteCopyProgram():
    return "pscp -P"

def remoteShellProgram():
    return "plink -P"

def graphVizDotCommandLine():
    return 'dot -Tplain -o'

def removeGraphvizTemporaries():
    pass

import shutil

def link_or_copy(fr, to):
    shutil.copyfile(fr, to)


def getClipboard():
   return QtGui.QClipboard.Clipboard


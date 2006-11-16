import os
import shutil
from PyQt4 import QtGui

try:
    from ctypes import windll, Structure, c_ulong
    importSuccess = True
    
    class WIN32MEMORYSTATUS(Structure):
        """ Structure that represents memory information returned by 
        Windows API
        
        """
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
    
##############################################################################
def parseMeminfo():
    """ 
    parseMeminfo() -> int
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
    """ guessTotalMemory() -> int 
    Return system memory in bytes. If ctypes is not installed it returns -1 
    
    """
    if importSuccess:
        return parseMeminfo()
    else:
        return -1

def temporaryDirectory():
    """ temporaryDirectory() -> str 
    Returns the path to the system's temporary directory. Tries to use the $TMP 
    environment variable, if it is present. Else, tries $TEMP, else uses 'c:/' 
    
    """
    if os.environ.has_key('TMP'):
        return os.environ['TMP'] + '\\'
    elif os.environ.has_key('TEMP'):
        return os.environ['TEMP'] + '\\'
    else:
        return 'c:/'

def homeDirectory():
    """ homeDirectory() -> str 
    Returns user's home directory using windows environment variables
    $HOMEDRIVE and $HOMEPATH
    
    """
    if len(os.environ['HOMEPATH']) == 0:
	return '\\'
    else:
	return os.environ['HOMEDRIVE'] + os.environ['HOMEPATH']

def remoteCopyProgram():
    return "pscp -P"

def remoteShellProgram():
    return "plink -P"

def graphVizDotCommandLine():
    """ graphVizDotCommandLine() -> str
    Returns dot command line

    """
    return 'dot -Tplain -o'

def removeGraphvizTemporaries():
    pass

def link_or_copy(src, dst):
    """link_or_copy(src:str, dst:str) -> None 
    Copies file src to dst 
    
    """
    shutil.copyfile(src, dst)

def getClipboard():
    """ getClipboard() -> int  
    Returns which part of system clipboard will be used by QtGui.QClipboard.
    On Windows, the global clipboard should be used.

    """
    return QtGui.QClipboard.Clipboard

################################################################################

import unittest

class TestWindows(unittest.TestCase):
     """ Class to test Windows specific functions """
     
     def test1(self):
         """ Test if guessTotalMemory() is returning an int >= 0"""
         result = guessTotalMemory()
         assert type(result) == type(1)
         assert result >= 0

     def test2(self):
         """ Test if homeDirectory is not empty """
         result = homeDirectory()
         assert result != ""

     def test3(self):
         """ Test if temporaryDirectory is not empty """
         result = temporaryDirectory()
         assert result != ""

if __name__ == '__main__':
    unittest.main()

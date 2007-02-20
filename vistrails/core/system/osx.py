############################################################################
##
## Copyright (C) 2006-2007 University of Utah. All rights reserved.
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
""" Mac OS X specific file """
      
from xml import dom
from xml.dom.xmlbuilder import DOMInputSource, DOMBuilder
import datetime
import time
import os
import shutil
import popen2
import core.utils
from core.system.unix import executable_is_in_path

from PyQt4 import QtGui

###############################################################################
# Extract system detailed information of a Mac system
#
# Using a Python Cookbook recipe available online :
#    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/303063
# and in the Python Coobook, page 418
# Credit: Brian Quinlan
#
# It requires PyXML : 
#   http://sourceforge.net/project/showfiles.php?group_id=6473&package_id=6541
#
# This recipe uses the system_profiler application to retrieve detailed
# information about a Mac OS X system. There are two useful ways to use it:
# the first is to ask for a complete Python datastructure containing
# information about the system (see OSXSystemProfiler.all()) and the 
# other is two ask for particular keys in the system information database.

def group(lst, n):
    """group([0,3,4,10,2,3], 2) => [(0,3), (4,10), (2,3)]
    
    Group a list into consecutive n-tuples. Incomplete tuples are
    discarded e.g.
    
    >>> group(range(10), 3)
    [(0, 1, 2), (3, 4, 5), (6, 7, 8)]
    
    """
    return zip(*[lst[i::n] for i in range(n)]) 

def remove_whilespace_nodes(node, unlink=False):
    """Removes all of the whitespace-only text decendants of a DOM node.
    
    When creating a DOM from an XML source, XML parsers are required to
    consider several conditions when deciding whether to include
    whitespace-only text nodes. This function ignores all of those
    conditions and removes all whitespace-only text decendants of the
    specified node. If the unlink flag is specified, the removed text
    nodes are unlinked so that their storage can be reclaimed. If the
    specified node is a whitespace-only text node then it is left
    unmodified.

    """
    remove_list = []
    for child in node.childNodes:
        if child.nodeType == dom.Node.TEXT_NODE and \
           not child.data.strip():
            remove_list.append(child)
        elif child.hasChildNodes():
            remove_whilespace_nodes(child)
    for node in remove_list:
        node.parentNode.removeChild(node)
        if unlink:
            node.unlink()

class POpenInputSource(DOMInputSource):
    "Use stdout from a system command as a DOMInputSource"
    def __init__(self, command):
        super(DOMInputSource, self).__init__()
        
        self.byteStream = os.popen(command)

class OSXSystemProfiler(object):
    "Provide information from the Mac OS X System Profiler"

    def __init__(self, detail=-1):
        """detail can range from -2 to +1, with larger numbers returning more
        information. Beware of +1, it can take several minutes for
        system_profiler to generate the data."""
        b = DOMBuilder()
        self.document = b.parse(
            POpenInputSource('system_profiler -xml -detailLevel %d' % detail))
        remove_whilespace_nodes(self.document, True)

    def _content(self, node):
        "Get the text node content of an element or an empty string"
        if node.firstChild:
            return node.firstChild.nodeValue
        else:
            return ''
    
    def _convert_value_node(self, node):
        """Convert a 'value' node (i.e. anything but 'key') into a Python data
        structure"""
        if node.tagName == 'string':
            return self._content(node)
        elif node.tagName == 'integer':
            return int(self._content(node))
        elif node.tagName == 'real':
            return float(self._content(node))
        elif node.tagName == 'date': #  <date>2004-07-05T13:29:29Z</date>
            return datetime.datetime(
                *time.strptime(self._content(node), '%Y-%m-%dT%H:%M:%SZ')[:5])
        elif node.tagName == 'array':
            return [self._convert_value_node(n) for n in node.childNodes]
        elif node.tagName == 'dict':
            return dict([(self._content(n), self._convert_value_node(m))
                for n, m in group(node.childNodes, 2)])
        else:
            raise ValueError(node.tagName)
    
    def __getitem__(self, key):
        from xml import xpath
        
        # pyxml xpath does not support /element1[...]/element2
        nodes = xpath.Evaluate(
            '//dict[key=%r]' % key, self.document)
        
        results = []
        for node in nodes:
            v = self._convert_value_node(node)[key]
            if isinstance(v, dict) and v.has_key('_order'):
                # this is just information for display
                pass
            else:
                results.append(v)
        return results
    
    def all(self):
        """Return the complete information from the system profiler
        as a Python data structure"""
        
        return self._convert_value_node(
            self.document.documentElement.firstChild)

###############################################################################

def example():
    from optparse import OptionParser
    from pprint import pprint

    info = OSXSystemProfiler()
    parser = OptionParser()
    parser.add_option("-f", "--field", action="store", dest="field",
                      help="display the value of the specified field")
    
    (options, args) = parser.parse_args()
    if len(args) != 0:
        parser.error("no arguments are allowed")
    
    if options.field is not None:
        pprint(info[options.field])
    else:
        # just print some comment keys known to exist in only one important
        # dictionary
        for k in ['cpu_type', 'current_processor_speed', 'l2_cache_size',
                  'physical_memory', 'user_name', 'os_version', 'ip_address']:
            print '%s: %s' % (k, info[k][0])

###############################################################################

def parseMeminfo():
    """ parseMeminfo() -> int
    Uses the system_profiler application to retrieve detailed information
    about a Mac OS X system.

    """
    try:
        from xml import dom, xpath
     
    except ImportError:
        print '**** Install PyXML to get the max memory information\n ****'
        return -1
        
    result = -1
    info = OSXSystemProfiler()
    mem = info['physical_memory'][0]
    if mem.upper().endswith(' GB'):
        result = int(mem[:-3]) * 1024 * 1024 * 1024
    return result

def guessTotalMemory():
    """ guessTotalMemory() -> int 
    Return system memory in bytes. If PyXML is not installed it returns -1 
    
    """
    return parseMeminfo()

def temporaryDirectory():
    """ temporaryDirectory() -> str 
    Returns the path to the system's temporary directory 
    
    """
    return "/tmp/"

def homeDirectory():
    """ homeDirectory() -> str 
    Returns user's home directory using environment variable $HOME
    
    """
    return os.getenv('HOME')

def remoteCopyProgram():
    return "scp -p"

def remoteShellProgram():
    return "ssh -p"

def graphVizDotCommandLine():
    """ graphVizDotCommandLine() -> str
    Returns dot command line

    """
    return 'dot -Tplain -o '

def removeGraphvizTemporaries():
    """ removeGraphvizTemporaries() -> None 
    Removes temporary files generated by dot 
    
    """
    os.unlink(temporaryDirectory() + "dot_output_vistrails.txt")
    os.unlink(temporaryDirectory() + "dot_tmp_vistrails.txt")

def link_or_copy(src, dst):
    """link_or_copy(src:str, dst:str) -> None 
    Tries to create a hard link to a file. If it is not possible, it will
    copy file src to dst 
    
    """
    # Links if possible, but we're across devices, we need to copy.
    try:
        os.link(src, dst)
    except OSError, e:
        if e.errno == 18:
            # Across-device linking is not possible. Let's copy.
            shutil.copyfile(src, dst)
        else:
            raise e

def getClipboard():
    """ getClipboard() -> int  
    Returns which part of system clipboard will be used by QtGui.QClipboard.
    On Mac OS X, the global clipboard should be used.

    """
    return QtGui.QClipboard.Clipboard

################################################################################

import unittest

class TestMacOSX(unittest.TestCase):
     """ Class to test Mac OS X specific functions """
     
     def test1(self):
         """ Test if guessTotalMemory() is returning an int >= 0"""
         result = guessTotalMemory()
         assert type(result) == type(1) or type(result) == type(1L)
         assert result >= 0

     def test2(self):
         """ Test if homeDirectory is not empty """
         result = homeDirectory()
         assert result != ""

     def test3(self):
         """ Test if temporaryDirectory is not empty """
         result = temporaryDirectory()
         assert result != ""

     def test_executable_file_in_path(self):
         # Should exist in any POSIX shell, which is what we have in OSX
         result = executable_is_in_path('ls')
         assert result == "/bin/ls" # Any UNIX should respect this.

if __name__ == '__main__':
    unittest.main()
             

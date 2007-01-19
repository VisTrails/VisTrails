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
from xml.dom import minidom
import xml.parsers.expat

def named_elements(element, elname):
    """named_elements(element, elname) -> Node 
    Helper function that iterates over the element child Nodes searching
    for node with name elname.

    """
    for node in element.childNodes:
        if node.nodeName == elname:
            yield node

class XMLWrapper(object):
    """Helper to parse a general XML file. It provides functions to open and 
    close files.
    It must be subclassed to parse specifi files. """

    class XMLParseError(Exception):

       
        def __init__(self, line, char, code):
            self._line = line
            self._char = char
            self._code = code
            
        def __str__(self):
            return ("XML Parse error at line %s, col %s: %s" %
                    (self._line,
                     self._char,
                     xml.parsers.expat.ErrorString(self._code)))

    def openFile(self, filename):
        """openFile(filename: str) -> None 
        Parses a XML file.

        """
        self.filename = filename
        try:
            self.dom = minidom.parse(filename)
        except xml.parsers.expat.ExpatError, e:
            raise self.XMLParseError(e.lineno, e.offset, e.code) 
    
    def closeFile(self):
        """closeFile() -> None 
        Removes the association with the XML file loaded by openFile 
        method. 

        """
        if self.dom:
            self.dom.unlink()
        self.filename = None
        self.dom = None
    
    def createDocument(self, nodename):
        """createDocument(nodename: str) -> xml element 
        Creates a documentElement 
        
        """
        impl = minidom.getDOMImplementation()
        dom = impl.createDocument(None, nodename, None)
        return dom

    def writeDocument(self, root, filename):
        """writeDocument(root:xml element, filename: str) -> None
        Save as an XML file 
        
        """
        outputFile = file(filename,'w')
        root.writexml(outputFile, "  ", "  ", '\n')
        outputFile.close()

    def __str__(self):
        """ __str__() -> str 
        Returns the XML that self.dom represents as a string 
        
        """
        return self.dom.toprettyxml()

################################################################################
# Testing

import unittest

class TestXmlUtils(unittest.TestCase):
    def testNamed_elements(self):
        """ Exercises searching for elements """
        xmlStr = """<root> 
                        <child>
                            <grandchild></grandchild>
                            <grandchild></grandchild>
                         </child>
                         <child></child>
                     </root>"""
        dom = minidom.parseString(xmlStr)
        root = dom.documentElement
        childcount = 0
        for node in named_elements(root,'child'):
            childcount += 1
        self.assertEquals(childcount,2)
        
        grandchildcount = 0
        for node in named_elements(root,'grandchild'):
            grandchildcount += 1
        self.assertEquals(grandchildcount,0)

        
if __name__ == "__main__":
    unittest.main()

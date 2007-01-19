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

def named_elements(element, elname):
    """named_elements(element, elname) -> Node 
    Helper function that iterates over the element child Nodes searching
    for node with name elname.

    """
    for node in element.childNodes:
        if node.nodeName == elname:
            yield node

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

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

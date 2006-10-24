from xml.dom import minidom

def named_elements(element, elname):
    for node in element.childNodes:
        if node.nodeName == elname:
            yield node

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
""" RecentVistrailList is a Helper class to manage serialization and
unserialization of a list of locators to XML """

from core.system import get_elementtree_library
from core.db.locator import FileLocator, DBLocator

ElementTree = get_elementtree_library()

class RecentVistrailList(object):
    def __init__(self):
        self.maxlocators = 0
        self.locators = []
        self.locators_map = {}
        
    @staticmethod
    def unserialize(text):
        """ unserialize(text) -> RecentVistrailList """
        root = ElementTree.fromstring(text)
        if root.tag != 'recentVistrails':
            return None
        vtlist = RecentVistrailList()
        for node in root.getchildren():
            loc = FileLocator.from_xml(node)
            if loc is None:
                loc = DBLocator.from_xml(node, include_name=True)
            if loc is not None:
                vtlist.locators.append(loc)
                vtlist.locators_map[loc.name] = loc
        return vtlist
    
    def serialize(self, node=None):
        """serialize(node: ElementTree.Element) -> text
        Convert this object to an XML representation.
        """
        if node is None:
            node = ElementTree.Element('recentVistrails')
        for loc in self.locators:
            childNode = ElementTree.SubElement(node, 'locator')
            if isinstance(loc, DBLocator):
                loc.to_xml(childNode, include_name=True)
            else:
                loc.to_xml(childNode)
        return ElementTree.tostring(node)
    
    def ensure_no_more_than_max(self, max):
        while len(self.locators) > max:
            locator = self.locators.pop()
            del self.locators_map[locator.name]
            
        self.maxlocators = max
        
    def add_locator(self, locator):
        if locator in self.locators:
            self.locators.remove(locator)
        self.locators.insert(0, locator)
        self.locators_map[locator.name] = locator
        
        self.ensure_no_more_than_max(self.maxlocators)
        
    def remove_locator(self, locator):
        if locator in self.locators:
            self.locators.remove(locator)
            del self.locators_map[locator.name]
            
    def length(self):
        return len(self.locators)
    
    def get_locator(self, index):
        try:
            return self.locators[index]
        except IndexError:
            return None
        
    def get_locator_by_name(self, name):
        try:
            return self.locators_map[name]
        except KeyError:
            return None
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
from xml.dom import minidom, Node
from auto_gen_objects import Object, Property, Choice

class AutoGenParser:
    def __init__(self):
	pass

    def parse(self, dir):
	objects = {}
	for file in os.listdir(dir):
	    if file.endswith('.xml'):
		filename = os.path.join(dir, file)
		# print filename
		dom = minidom.parse(filename)
		domObjects = dom.getElementsByTagName('object')
		for node in domObjects:
		    curObject = self.parseObject(node)
		    objects[curObject.getName()] = curObject

        # set the referenced objects here
        for obj in objects.itervalues():
            for prop in obj.properties:
                if prop.getReference():
                    try:
                        prop.setReferencedObject(objects[prop.getReference()])
                    except KeyError:
                        print 'error:', prop.getReference()
            for choice in obj.choices:
                for prop in choice.properties:
                    if prop.getReference():
                        try:
                            prop.setReferencedObject(
                                objects[prop.getReference()])
                        except KeyError:
                            print 'error:', prop.getReference()
                
	return objects.values()

    def parseObject(self, node):
	params = {}
	properties = []
	choices = []
	layouts = None
	for attr in node.attributes.keys():
	    params[attr] = node.attributes.get(attr).value
	for child in node.childNodes:
	    if child.nodeType == Node.ELEMENT_NODE:
		if child.nodeName == 'layout':
		    layouts = self.parseLayouts(child)
		elif child.nodeName == 'property':
		    property = self.parseProperty(child)
		    properties.append(property)
		elif child.nodeName == 'choice':
		    choice = self.parseChoice(child)
		    choices.append(choice)
	return Object(params, properties, layouts, choices)
    
    def parseLayouts(self, node):
	layouts = {}
	for child in node.childNodes:
	    if child.nodeType == Node.ELEMENT_NODE:
		layouts[child.nodeName] = self.parseDataToDict(child)
	return layouts

    def parseProperty(self, node):
	params = {}
	specs = {}
	for attr in node.attributes.keys():
	    params[attr] = node.attributes.get(attr).value
	for child in node.childNodes:
	    if child.nodeType == Node.ELEMENT_NODE:
		specs[child.nodeName] = self.parseDataToDict(child)
	return Property(params, specs)

    def parseChoice(self, node):
	params = {}
	properties = []
	for attr in node.attributes.keys():
	    params[attr] = node.attributes.get(attr).value
	for child in node.childNodes:
	    if child.nodeType == Node.ELEMENT_NODE and \
		    child.nodeName == 'property':
		properties.append(self.parseProperty(child))
	return Choice(params, properties)

    def parseDataToDict(self, node):
	dict = {}
	if node.nodeType == Node.ELEMENT_NODE:
	    for attr in node.attributes.keys():
		dict[attr] = node.attributes.get(attr).value
	    for child in node.childNodes:
		if child.nodeType == Node.ELEMENT_NODE:
		    dict[child.nodeName] = child.childNodes[0].data
	return dict

###############################################################################
##
## Copyright (C) 2014-2016, New York University.
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
##  - Neither the name of the New York University nor the names of its
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
from __future__ import division

import base64
import os
import vistrails.core.db.action
from vistrails.core.modules.basic_modules import File, Boolean, String, Directory
from vistrails.core.modules.vistrails_module import Module, ModuleError, NotCacheable
from vistrails.core.vistrail.vistrail import Vistrail
from vistrails.db.services.locator import DBLocator
from vistrails.core.system import get_elementtree_library
from vistrails.db.services import io
from vistrails.db.versions import currentVersion

ElementTree = get_elementtree_library()

class VtlFileCreator(NotCacheable, Module):
    """This Module creates a vtl file for the workflow where it is
    present.
    By default it generates a string with an <vtlink> </vtlink> XML
    element or it can write the vtl file to disk if filename is
    provided. If directory is provided, the final filename will be
    the concatenation of directory and filename.
    
    Other input ports:
    
    execute: Boolean
        tells VisTrails to execute the workflow when the vtl is open
        
    showSpreadsheetOnly: Boolean
        tells VisTrails to hide the builder window and show only the
        spreadsheet when the vtl is open
    
    embedWorkflow: Boolean
        it will embed a vistrail encoded as base64 containing only 
        the workflow where the module is. It can be loaded by 
        VisTrails.
        
    """
    def __init__(self):
        Module.__init__(self)
        self.locator = None
        self.version = -1
        self.pipeline = None
        self.execute = False
        self.embedWorkflow = False
        self.showSpreadsheetOnly = False
        self.forceDB = False
        
    def get_locator_and_version(self):
        self.locator = self.moduleInfo['locator']
        self.version = self.moduleInfo['version']
        self.pipeline = self.moduleInfo['pipeline']
        
        if self.locator is None:
            raise ModuleError(self, 'could not get the locator for this pipeline')
        if self.version is None:
            raise ModuleError(self, 'could not get the version number of this peline')
    
    @staticmethod
    def generate_vtl(locator,version,pipeline,execute=False,forceDB=False,
                     showSpreadsheetOnly=False,embedWorkflow=False):
        """generate_vtl(locator:DBLocator or XMLLocator,
                        version: str, pipeline:Pipeline, execute:boolean,
                        forceDB:boolean, showspreadsheetOnly:boolean,
                        embedWorkflow: boolean) -> str
           It generates the contents of a .vtl file with the information
           given.
        """
        node = ElementTree.Element('vtlink')
        
        if isinstance(locator, DBLocator):
            node.set('host', str(locator.host))
            node.set('port', str(locator.port))
            node.set('database', str(locator.db))
            node.set('vtid', str(locator.obj_id))
        elif locator is not None:
            node.set('filename', str(locator.name))
            
        node.set('version', str(version))    
        node.set('execute', str(execute))
        node.set('forceDB', str(forceDB))
        node.set('showSpreadsheetOnly', str(showSpreadsheetOnly))
            
        if embedWorkflow == True:
            vistrail = Vistrail()
            action_list = []
            for module in pipeline.module_list:
                action_list.append(('add', module))
            for connection in pipeline.connection_list:
                action_list.append(('add', connection))
            action = vistrails.core.db.action.create_action(action_list)
            vistrail.add_action(action, 0L)
            vistrail.addTag("Imported workflow", action.id)
            if not forceDB:
                node.set('version', str(action.id))
            if not vistrail.db_version:
                vistrail.db_version = currentVersion
            pipxmlstr = io.serialize(vistrail)
            vtcontent = base64.b64encode(pipxmlstr)
            node.set('vtcontent',vtcontent)
            
        return ElementTree.tostring(node)
            
            
    def compute(self):
        self.get_locator_and_version()
        
        if self.has_input('execute'):
            self.execute = self.get_input('execute')
        
        if self.has_input('forceDB'):
            self.forceDB = self.get_input('forceDB')
        
        if self.has_input('showSpreadsheetOnly'):
            self.showSpreadsheetOnly = self.get_input('showSpreadsheetOnly')
            
        if self.has_input('embedWorkflow'):
            self.embedWorkflow = self.get_input('embedWorkflow')
        
        xmlstring = self.generate_vtl(self.locator,self.version,self.pipeline,
                                      self.execute,self.forceDB,
                                      self.showSpreadsheetOnly,self.embedWorkflow)
        
        if self.has_input('filename'):
            filename = self.get_input('filename')
            if self.has_input('directory'):
                directory = self.get_input('directory').name
                filename = os.path.join(directory,filename)
            file_ = open(filename,'w')
            file_.write(xmlstring)
            file_.close()
        
        self.set_output("xmlstring", xmlstring)
        
    _input_ports = [('execute', Boolean, True), 
                    ('showspreadsheetOnly', Boolean, True),
                    ('embedWorkflow', Boolean, True),
                    ('forceDB', Boolean, True), 
                    ('filename', String), 
                    ('directory', Directory)]
    
    _output_ports = [('xmlstring', String)]

_modules = [VtlFileCreator]

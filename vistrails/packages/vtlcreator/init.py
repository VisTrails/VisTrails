############################################################################
##
## Copyright (C) 2006-2010 University of Utah. All rights reserved.
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

import base64
import os
import core.db.action
from core.modules.basic_modules import File, Boolean, String, Directory
from core.modules.vistrails_module import Module, ModuleError, NotCacheable
from core.vistrail.vistrail import Vistrail
from db.services.locator import DBLocator
from core.system import get_elementtree_library
from db.services import io
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
        
    def get_locator_and_version(self):
        self.locator = self.moduleInfo['locator']
        self.version = self.moduleInfo['version']
        self.pipeline = self.moduleInfo['pipeline']
        
        if self.locator is None:
            raise ModuleError(self, 'could not get the locator for this pipeline')
        if self.version is None:
            raise ModuleError(self, 'could not get the version number of this peline')
    
    def compute(self):
        self.get_locator_and_version()
        
        node = ElementTree.Element('vtlink')
        
        if isinstance(self.locator, DBLocator):
            node.set('host', str(self.locator.host))
            node.set('port', str(self.locator.port))
            node.set('database', str(self.locator.db))
            node.set('vtid', str(self.locator.obj_id))
        else:
            node.set('filename', str(self.locator.name))
            
        node.set('version', str(self.version))
        if self.hasInputFromPort('execute'):
            self.execute = self.getInputFromPort('execute')
        node.set('execute', str(self.execute))
        
        if self.hasInputFromPort('showSpreadsheetOnly'):
            self.showSpreadsheetOnly = self.getInputFromPort('showSpreadsheetOnly')
        node.set('showSpreadsheetOnly', str(self.showSpreadsheetOnly))
        if self.hasInputFromPort('embedWorkflow'):
            self.embedWorkflow = self.getInputFromPort('embedWorkflow')
        if self.embedWorkflow == True:
            vistrail = Vistrail()
            action_list = []
            for module in self.pipeline.module_list:
                action_list.append(('add', module))
            for connection in self.pipeline.connection_list:
                action_list.append(('add', connection))
            action = core.db.action.create_action(action_list)
            vistrail.add_action(action, 0L)
            vistrail.addTag("Imported workflow", action.id)
            pipxmlstr = io.serialize(vistrail)
            vtcontent = base64.b64encode(pipxmlstr)
            node.set('vtcontent',vtcontent)
            
        xmlstring = ElementTree.tostring(node)
            
        if self.hasInputFromPort('filename'):
            filename = self.getInputFromPort('filename')
            if self.hasInputFromPort('directory'):
                directory = self.getInputFromPort('directory').name
                filename = os.path.join(directory,filename)
            file_ = open(filename,'w')
            file_.write(xmlstring)
            file_.close()
        
        self.setResult("xmlstring", xmlstring)
        
    _input_ports = [('execute', Boolean, True), ('showspreadsheetOnly', Boolean, True),
                    ('embedWorkflow', Boolean, True), ('filename', String), ('directory', Directory)]
    
    _output_ports = [('xmlstring', String)]

_modules = [VtlFileCreator]

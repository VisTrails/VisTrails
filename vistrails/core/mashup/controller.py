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
import os.path
from core.system import current_user, current_time

class MashupController(object):
    def __init__(self, vt_controller, vt_version, mshptrail=None):
        self.vtController = vt_controller
        self.vtVersion = vt_version
        self.vtPipeline = self.vtController.vistrail.getPipeline(self.vtVersion)
        self.mshptrail = mshptrail
        self.currentVersion = -1
        self.currentMashup = None
        self._changed = False

    def setChanged(self, on):
        self._changed = on
        
    def setCurrentVersion(self, version):
        self.currentVersion = version
        if version > -1:
            self.currentMashup = self.mshptrail.getMashup(version)
            
    def getVistrailParam(self, alias):
        if self.vtPipeline:
            return self.vtPipeline.db_get_object(alias.component.vttype,
                                                  alias.component.vtid)
        return None
    
    def executeCurrentMashup(self, params):
        if self.vtPipeline and self.vtController:
            return self.vtController.execute_current_workflow(custom_params=params)
        return ([], False)
    
    def updateCurrentTag(self, name):
        self.mshptrail.changeTag(self.currentVersion, name, current_user(),
                                 current_time())
        self.setChanged(True)
    
    def getCurrentTag(self):
        return self.mshptrail.getTagForActionId(self.currentVersion)
    
    def getVistrailName(self):
        name = ''
        locator = self.currentMashup.vtid
        if locator != None:
            if locator.name == None:
                name = ''
            else:
                name = os.path.split(locator.name)[1]
            if name == '':
                name = self.controller.vtController.name
        return name
        
    
    def getVistrailWorkflowTag(self):
        return self.vtController.vistrail.getVersionName(self.vtVersion)
        
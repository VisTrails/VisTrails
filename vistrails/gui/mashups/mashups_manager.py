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
import copy
import uuid
from gui.mashups.mashups_window import QMashupsWindow
from gui.vistrail_controller import VistrailController
from gui.mashups.controller import MashupController
from core.mashup.mashup_trail import Mashuptrail
from core.mashup.mashup import Mashup
import core.system
from db.domain import IdScope
############################################################################

class MashupsManager(object):
    _instance = None
    class MashupsManagerSingleton(object):
        def __call__(self, *args, **kw):
            if MashupsManager._instance is None:
                obj = MashupsManager(*args, **kw)
                MashupsManager._instance = obj
            return MashupsManager._instance
    
    getInstance = MashupsManagerSingleton()

    def __init__(self):
        if not MashupsManager._instance:
            self._mainWindow = None
            self._id_scope = IdScope(1L)
            MashupsManager._instance = self
        else:
            raise RuntimeError, 'Only one instance of MashupsManager is allowed'

    def createMashup(self, vt_controller, version):
        if self._mainWindow is None:
            self.createMainWindow()
        #we need to create a new controller so we do not change the state of the
        # vistrails controller when we add aliases.
        
        newvt_controller = VistrailController()
        current_log = vt_controller.log
        vistrail = copy.copy(vt_controller.vistrail)
        newvt_controller.log = current_log
        newvt_controller.set_vistrail(vistrail, None)
        newvt_controller.disable_autosave()
        mashuptrail = Mashuptrail(self.getNewMashuptrailId(), self._id_scope)
        pipeline = newvt_controller.vistrail.getPipeline(version)
        id = self._id_scope.getNewId('mashup')
        mashup = Mashup(id=id, name="mashup%s"%id, vtid=vt_controller.locator, 
                        version=version)
        mashup.loadAliasesFromPipeline(pipeline, self._id_scope)
        currVersion = mashuptrail.addVersion(parent_id=mashuptrail.getLatestVersion(),
                                             mashup=mashup, 
                                             user=core.system.current_user(),
                                             date=core.system.current_time())
    
        mashuptrail.currentVersion = currVersion
        mshpController = MashupController(newvt_controller, version, mashuptrail)
        mshpController.setCurrentVersion(currVersion)
        self._mainWindow.createWindow(mshpController)
    
    def createMainWindow(self):
        self._mainWindow = QMashupsWindow()
    
    def updateController(self, mshpController):
        self._mainWindow.updateController(mshpController)
        
    @staticmethod
    def getNewMashuptrailId():  
        return uuid.uuid1()
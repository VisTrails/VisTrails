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

from gui.vistrail_controller import VistrailController
from gui.mashups.controller import MashupController
from core.mashup.mashup_trail import Mashuptrail
from core.mashup.mashup import Mashup
from core.utils import DummyView
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
            MashupsManager._instance = self
        else:
            raise RuntimeError, 'Only one instance of MashupsManager is allowed'

    def createMashupController(self, vt_controller, version, view=DummyView()):
        #print "Manager creating mashup controller ", vt_controller, version
        newvt_controller = VistrailController()
        current_log = vt_controller.log
        vistrail = vt_controller.vistrail
        newvt_controller.log = current_log
        newvt_controller.current_pipeline_view = view.scene()
        newvt_controller.set_vistrail(vistrail, None)
        newvt_controller.disable_autosave()
        mashuptrail = \
         MashupsManager.getMashuptrailforVersionInVistrailController(vt_controller,
                                                                     version)
        if mashuptrail is None:
            id_scope = IdScope(1L)
            mashuptrail = Mashuptrail(self.getNewMashuptrailId(), version, 
                                      id_scope)
            pipeline = newvt_controller.vistrail.getPipeline(version)
            id = id_scope.getNewId('mashup')
            mashup = Mashup(id=id, name="mashup%s"%id, vtid=vt_controller.locator, 
                        version=version)
            mashup.loadAliasesFromPipeline(pipeline, id_scope)
            currVersion = mashuptrail.addVersion(parent_id=mashuptrail.getLatestVersion(),
                                             mashup=mashup, 
                                             user=core.system.current_user(),
                                             date=core.system.current_time())
    
            mashuptrail.currentVersion = currVersion
            
            MashupsManager.addMashuptrailtoVistrailController(vt_controller,
                                                              mashuptrail)
            mshpController = MashupController(newvt_controller, version, mashuptrail)
            mshpController.setCurrentVersion(mashuptrail.currentVersion)
            if mshpController.currentVersion == 1L:
                mshpController.updateCurrentTag("ROOT")
        else:
            print "----> found mashuptrail ", mashuptrail.currentVersion
            mshpController = MashupController(newvt_controller, version, mashuptrail)
            mshpController.setCurrentVersion(mashuptrail.currentVersion)
            mshpController.updatePipelineAliasesFromCurrentMashup()
        
        return mshpController
            
    @staticmethod
    def getNewMashuptrailId():  
        return uuid.uuid1()
    
    @staticmethod
    def getMashuptrailforVersionInVistrailController(controller, version):
        print version, controller
        res = None
        if hasattr(controller, "_mashups"):
            for mashuptrail in controller._mashups:
                print mashuptrail.vtVersion
                if mashuptrail.vtVersion == version:
                    return mashuptrail
        return res
    
    @staticmethod
    def addMashuptrailtoVistrailController(controller, mashuptrail):
        controller._mashups.append(mashuptrail)
        controller.set_changed(True)    
###############################################################################
##
## Copyright (C) 2006-2011, University of Utah. 
## All rights reserved.
## Contact: vistrails@sci.utah.edu
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
import copy
import uuid

from gui.vistrail_controller import VistrailController
from core.vistrail.controller import VistrailController as BaseVistrailController
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
        newvt_controller = MashupsManager.copyVistrailController(vt_controller,
                                                                view)
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
            mshpController = MashupController(vt_controller,
                                              newvt_controller, 
                                              version, mashuptrail)
            mshpController.setCurrentVersion(mashuptrail.currentVersion)
            if mshpController.currentVersion == 1L:
                mshpController.updateCurrentTag("ROOT")
        else:
            print "----> found mashuptrail ", mashuptrail.currentVersion
            mshpController = MashupController(vt_controller, 
                                              newvt_controller, 
                                              version, mashuptrail)
            mshpController.setCurrentVersion(mashuptrail.currentVersion)
            mshpController.updatePipelineAliasesFromCurrentMashup()
        
        return mshpController
            
    @staticmethod
    def getNewMashuptrailId():  
        return uuid.uuid1()
    
    @staticmethod
    def copyVistrailController(vt_controller, view=DummyView()):
        newvt_controller = VistrailController()
        current_log = vt_controller.log
        vistrail = vt_controller.vistrail
        newvt_controller.log = current_log
        newvt_controller.current_pipeline_view = view.scene()
        newvt_controller.set_vistrail(vistrail, None)
        newvt_controller.disable_autosave()
        return newvt_controller
    
    @staticmethod
    def copyBaseVistrailController(vt_controller):
        newvt_controller = BaseVistrailController()
        current_log = vt_controller.log
        vistrail = vt_controller.vistrail
        newvt_controller.log = current_log
        newvt_controller.set_vistrail(vistrail, None)
        return newvt_controller
    
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
        
    @staticmethod
    def createMashupApp(vtcontroller, mashuptrail, version):
        from gui.mashups.mashup_app import QMashupAppMainWindow
        vtVersion = mashuptrail.vtVersion
        view = DummyView()
        view.scene().current_pipeline = vtcontroller.vistrail.getPipeline(vtVersion)
        view.scene().current_pipeline.validate()
        new_vtcontroller = MashupsManager.copyBaseVistrailController(vtcontroller)
        new_vtcontroller.change_selected_version(vtVersion)
        mshpController = MashupController(vtcontroller,
                                          new_vtcontroller, 
                                          vtVersion, mashuptrail)
        mshpController.setCurrentVersion(version)
        app = QMashupAppMainWindow(parent=None, 
                                   controller=mshpController,
                                   version=version)
        return app
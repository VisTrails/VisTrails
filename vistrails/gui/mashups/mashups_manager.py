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
from PyQt4 import QtCore, QtGui
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
            (p_mashuptrail, p_version) = \
                     MashupsManager.findClosestParentMashuptrail(vt_controller, 
                                                                 version)
            id_scope = IdScope(1L)
            if p_mashuptrail is not None:
                version_name = vt_controller.get_pipeline_name(p_version)
                (res, mshpv) = MashupsManager.showFoundMashupsDialog(p_mashuptrail, 
                                                            version_name)
                if res in ['Copy', 'Move']:
                    pipeline = newvt_controller.vistrail.getPipeline(version)
                    if res == 'Copy':
                        # we will copy the mashup from the parent trail and 
                        # validate it to the current pipeline before adding
                        # to the current mashup trail
                        mashuptrail = Mashuptrail(self.getNewMashuptrailId(), 
                                                  version, id_scope)
                        p_mashup = p_mashuptrail.getMashup(mshpv)
                        mashup = p_mashup.doCopy()
                        mashup.id_scope = id_scope
                        mashup.version = version
                        mashup.validateForPipeline(pipeline)
                        currVersion = mashuptrail.addVersion(
                                      parent_id=mashuptrail.getLatestVersion(),
                                      mashup=mashup, 
                                      user=core.system.current_user(),
                                      date=core.system.current_time())
                        mashuptrail.currentVersion = currVersion
                        mashuptrail.updateIdScope()
                        p_tag = p_mashuptrail.getTagForActionId(mshpv)
                        if p_tag == '':
                            tag = "<latest>"
                        tag = "Copy from %s"%p_tag
                        MashupsManager.addMashuptrailtoVistrailController(vt_controller,
                                                                          mashuptrail)    
                        
                    elif res == 'Move':
                        # we will move the parent trail and validate all mashups
                        # for the current pipeline to make sure they will be 
                        # executable for the current version

                        mashuptrail = p_mashuptrail
                        currVersion = mashuptrail.getLatestVersion()
                        mashuptrail.currentVersion = currVersion
                        mashuptrail.validateMashupsForPipeline(version, pipeline)
                        tag = None
                        
                    mashuptrail.vtVersion = version
                    mshpController = MashupController(vt_controller, 
                                                      newvt_controller, 
                                                      version, mashuptrail)
                    mshpController.setCurrentVersion(mashuptrail.currentVersion)
                    # this is to make sure the pipeline displayed in the mashup
                    # view is consistent with the list of aliases in the central
                    # panel
                    mshpController.updatePipelineAliasesFromCurrentMashup()
                    if tag is not None:
                        mshpController.updateCurrentTag(tag)
                    return mshpController
                
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
        #print version, controller
        res = None
        if hasattr(controller, "_mashups"):
            for mashuptrail in controller._mashups:
                #print mashuptrail.vtVersion
                if mashuptrail.vtVersion == version:
                    return mashuptrail
        return res
    
    @staticmethod
    def findClosestParentMashuptrail(vt_controller, version):
        res = None
        mashuptrails = {}
        if hasattr(vt_controller, "_mashups"):
            for mashuptrail in vt_controller._mashups:
                #print mashuptrail.vtVersion
                mashuptrails[mashuptrail.vtVersion] = mashuptrail
        action_map = vt_controller.vistrail.actionMap
        if version > 0 and len(mashuptrails) > 0:
            v = action_map[version].parent
            while True:
                if v in mashuptrails or v <= 0:
                    if v in mashuptrails:
                        res = mashuptrails[v]
                    else:
                        res = None
                    return (res, v)
                v = action_map[v].parent
        return (res, -1)
    
    @staticmethod
    def showFoundMashupsDialog(mashup_trail, version_name, parent=None):
        class FoundMashupDialog(QtGui.QDialog):
            
            def __init__(self, mashup_trail, version_name, parent=None):
                QtGui.QDialog.__init__(self, parent)
                self.setWindowTitle('VisTrails - Mashup')
                dlgLayout = QtGui.QVBoxLayout()
                str_label = "VisTrails found mashup(s) already created in parent %s."
                label = QtGui.QLabel(str_label%str(version_name))
                label.setWordWrap(True)
                gb = QtGui.QGroupBox("What would you like to do?")
                gblayout = QtGui.QVBoxLayout()
                
                self.btnNew = QtGui.QRadioButton("Create new mashup (starting from current pipeline's aliases)")
                self.btnNew.setChecked(True)
                self.btnCopy = QtGui.QRadioButton("Copy selected mashup (aliases will be merged)")
                self.btnMove = QtGui.QRadioButton("Move all mashups to current pipeline")
                self.mashupsList = QtGui.QListWidget()
                self.mashupsList.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
                self.mashupsList.setMaximumSize(100, 120)
                self.mashupsList.setEnabled(False)
                self.setMashupsList(mashup_trail)
                
                hlayout = QtGui.QHBoxLayout()
                hlayout.setMargin(5)
                hlayout.setSpacing(5)
                hlayout.addWidget(self.mashupsList)
                hlayout.addStretch()
                
                gblayout.addWidget(self.btnNew)
                gblayout.addWidget(self.btnMove)
                gblayout.addWidget(self.btnCopy)
                gblayout.addLayout(hlayout)
                
                gb.setLayout(gblayout)
                btnOk = QtGui.QPushButton("OK")
                btnLayout = QtGui.QHBoxLayout()
                btnLayout.addStretch()
                btnLayout.addWidget(btnOk)
                btnLayout.addStretch()
                self.btnPressed = 0
                self.mashup_version = -1
                
                dlgLayout.addWidget(label)
                dlgLayout.addWidget(gb)
                dlgLayout.addLayout(btnLayout)
                self.setLayout(dlgLayout)
                self.connect(self.btnCopy, QtCore.SIGNAL("toggled(bool)"),
                             self.mashupsList.setEnabled)
                self.connect(btnOk, QtCore.SIGNAL("clicked()"), 
                             self.btnOkPressed)      
                
            def btnOkPressed(self):
                if self.btnNew.isChecked():
                    self.btnPressed = 'New'
                elif self.btnMove.isChecked():
                    self.btnPressed = 'Move'
                elif self.btnCopy.isChecked():
                    self.btnPressed = 'Copy'
                    self.mashup_version = self.getMashupVersion()
                self.accept()
                
            def setMashupsList(self, mshptrail):
                from gui.mashups.mashups_inspector import QMashupListPanelItem
                self.mashupsList.clear()
                tagMap = mshptrail.getTagMap()
                tags = tagMap.keys()
                latestversion = mshptrail.getLatestVersion()
                item_selected = False
                if not mshptrail.hasTagForActionId(latestversion):
                    item = QMashupListPanelItem("<latest>",
                                                latestversion,
                                                self.mashupsList)
                    item.setSelected(True)
                    item_selected = True
                if len(tags) > 0:
                    tags.sort()
                    i = 0
                    for tag in tags:
                        item = QMashupListPanelItem(str(tag),
                                                    tagMap[tag],
                                                    self.mashupsList)
                        if i == 0 and not item_selected:
                            item.setSelected(True)
                        i+=1
                        
            def getMashupVersion(self):
                items = self.mashupsList.selectedItems()
                if len(items) == 1:
                    return items[0].version
            
        dialog = FoundMashupDialog(mashup_trail, version_name, parent)
        if dialog.exec_() == QtGui.QDialog.Accepted:
            return (dialog.btnPressed,dialog.mashup_version) 
        else:
            return ('New', -1)                
    
    @staticmethod
    def addMashuptrailtoVistrailController(controller, mashuptrail):
        controller._mashups.append(mashuptrail)
        controller.set_changed(True)    
        
    @staticmethod
    def createMashupApp(vtcontroller, mashuptrail, version):
        from gui.mashups.mashup_app import QMashupAppMainWindow
        vistrail_view = vtcontroller.vistrail_view
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
                                   vistrail_view=vistrail_view, 
                                   controller=mshpController,
                                   version=version)
        return app
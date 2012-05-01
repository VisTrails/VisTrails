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
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import pyqtSignal

spreadsheet = __import__('packages.spreadsheet', globals(), locals(), 
                            ['spreadsheet_controller'], -1) 
spreadsheetController = spreadsheet.spreadsheet_controller.spreadsheetController

from gui.mashups.mashups_widgets import (QAliasSliderWidget, QDropDownWidget,
                                         QAliasNumericStepperWidget)
from gui.utils import show_warning

class QMashupAppMainWindow(QtGui.QMainWindow):
    #signals
    appWasClosed = pyqtSignal(QtGui.QMainWindow)
    
    def __init__(self, parent=None, vistrail_view=None, dumpcells=False, 
                 controller=None, version=-1):
        """ QMashupAppMainWindow()
        Initialize an app window from a mashup.

        """
        # Constructing the main widget
        QtGui.QMainWindow.__init__(self, parent)
        self.vtkCells = []
        self.setStatusBar(QtGui.QStatusBar(self))
    
        # Central widget
        centralWidget = QtGui.QWidget()
        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.setMargin(0)
        self.mainLayout.setSpacing(5)
        centralWidget.setLayout(self.mainLayout)
        self.setCentralWidget(centralWidget)
        self.numberOfCells = 0
        self.is_executing = False
        #self.resize(100,100)
        self.dumpcells = dumpcells
        self.view = vistrail_view
        if controller:
            self.controller = controller
            self.mshptrail = controller.mshptrail
            if version == -1:
                self.currentMashup = self.controller.currentMashup
            else:
                self.currentMashup = self.mshptrail.getMashup(version)
            self.setWindowTitle('%s Mashup'%self.controller.getMashupName(version))
        else:
            self.setWindowTitle('Mashup')
            
        # Assign "hidden" shortcut
        self.editingModeAct = QtGui.QAction("Chang&e Layout", self, shortcut="Ctrl+E",
               statusTip="Change the layout of the widgets", triggered=self.toggleEditingMode)
        #self.editingModeShortcut = QtGui.QShortcut(QtGui.QKeySequence('Ctrl+E'), self)
        #self.connect(self.editingModeShortcut, QtCore.SIGNAL('activated()'),
        #             self.toggleEditingMode)
        self.editing = False
        # Constructing alias controls
        self.controlDocks = []
        # Show here to make sure XDisplay info is correct (for VTKCell)
        self.show()

        spreadsheetController.setEchoMode(True)        
        #will run to get Spreadsheet Cell events
        (cellEvents, errors) = self.runAndGetCellEvents(useDefaultValues=True)
        if cellEvents:
            self.numberOfCells = len(cellEvents)
            self.initCells(cellEvents)
        if len(errors) > 0:
            show_warning("VisTrails::Mashup Preview", 
                         "There was a problem executing the pipeline: %s."%errors)
        # Construct the controllers for aliases
        self.controlDocks = {}
        self.cellControls = {}
        self.aliasWidgets = {}
        self.initControls()
        
        if self.currentMashup.layout != None:
            self.restoreState(QtCore.QByteArray.fromPercentEncoding(
                                QtCore.QByteArray(self.currentMashup.layout)))
        
        if self.currentMashup.geometry != None:
            self.restoreGeometry(QtCore.QByteArray.fromPercentEncoding(
                                QtCore.QByteArray(self.currentMashup.geometry)))
        else:
            self.resize(self.sizeHint())
                    
        # Constructing buttons
        buttonDock = QCustomDockWidget('Control Buttons', self)
        buttonWidget = QtGui.QWidget(buttonDock)
        buttonWidget.setSizePolicy(QtGui.QSizePolicy.Preferred,
                                   QtGui.QSizePolicy.Preferred)
        buttonLayout = QtGui.QGridLayout()
        buttonWidget.setLayout(buttonLayout)
        buttonLayout.setMargin(5)
        self.cb_auto_update = QtGui.QCheckBox("Turn on auto-update", self.centralWidget())
        self.cb_auto_update.setChecked(False)
        self.cb_keep_camera = QtGui.QCheckBox("Keep camera position", self.centralWidget())
        self.cb_keep_camera.setChecked(True)
        self.connect(self.cb_auto_update,
                     QtCore.SIGNAL("stateChanged(int)"),
                     self.auto_update_changed)
        self.updateButton = QtGui.QPushButton("&Update", self.centralWidget())
        if self.dumpcells:
            self.quitButton = QtGui.QPushButton("&Save", self.centralWidget())
            self.connect(self.quitButton,
                         QtCore.SIGNAL('clicked(bool)'),
                         self.saveAndExport)
        else:
            self.quitButton = QtGui.QPushButton("&Quit", self.centralWidget())
            self.connect(self.quitButton,
                         QtCore.SIGNAL('clicked(bool)'),
                         self.close)
        buttonLayout.setColumnStretch(0, 1)
        buttonLayout.addWidget(self.cb_auto_update, 0, 1, QtCore.Qt.AlignLeft)    
        buttonLayout.addWidget(self.cb_keep_camera, 0, 2, 1, 2, QtCore.Qt.AlignLeft) 
        buttonLayout.addWidget(self.updateButton, 1, 2, QtCore.Qt.AlignRight)
        buttonLayout.addWidget(self.quitButton, 1, 3, QtCore.Qt.AlignRight)
        self.connect(self.updateButton,
                     QtCore.SIGNAL('clicked(bool)'),
                     self.updateButtonClick)
        buttonDock.setWidget(buttonWidget)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, buttonDock)
        self.controlDocks["__buttons__"] = buttonDock
        
        self.saveAllAct = QtGui.QAction("S&ave Combined", self, 
                                        shortcut=QtGui.QKeySequence.SelectAll,
                                        statusTip="Save combined images to disk", 
                                        triggered=self.saveAllEvent)
        self.saveAct = QtGui.QAction("&Save Each", self, 
                                     shortcut=QtGui.QKeySequence.Save,
                                     statusTip="Save separate images to disk", 
                                     triggered=self.saveEventAction)
        self.showBuilderAct = QtGui.QAction("VisTrails Main Window", self,
                                            statusTip="Show VisTrails Main Window",
                                            triggered=self.showBuilderWindow)
        self.createMenus()
        self.lastExportPath = ''
                    
    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.saveAct)
        self.fileMenu.addAction(self.saveAllAct)
        
        self.viewMenu = self.menuBar().addMenu("&View")
        self.viewMenu.addAction(self.editingModeAct)
        
        self.windowMenu = self.menuBar().addMenu("&Window")
        self.windowMenu.addAction(self.showBuilderAct)
        
    def runAndGetCellEvents(self, useDefaultValues=False):
        spreadsheetController.setEchoMode(True)        
        #will run to get Spreadsheet Cell events
        cellEvents = []
        errors = []
        try:
            (res, errors) = self.run(useDefaultValues)
            if res:
                cellEvents = spreadsheetController.getEchoCellEvents()
        except Exception, e:
            import traceback
            print "Executing pipeline failed:", str(e), traceback.format_exc()
        finally:
            spreadsheetController.setEchoMode(False)
            
        return (cellEvents, errors)
    
    def updateCells(self):
        self.is_executing = True
        (cellEvents, errors) = self.runAndGetCellEvents()
        self.is_executing = False
        if len(cellEvents) != self.numberOfCells:
            raise Exception('The number of cells has changed (unexpectedly) (%d vs. %d)!\n \
Pipeline results: %s' % (len(cellEvents), self.numberOfCells, errors))
        #self.SaveCamera()
        for i in xrange(self.numberOfCells):
            camera = []
            if (hasattr(self.cellWidgets[i],"getRendererList") and 
                self.cb_keep_camera.isChecked()):
                for ren in self.cellWidgets[i].getRendererList():
                    camera.append(ren.GetActiveCamera())
                self.cellWidgets[i].updateContents(cellEvents[i].inputPorts, camera)
                #self.cellWidgets[i].updateContents(cellEvents[i].inputPorts)
            else:
                self.cellWidgets[i].updateContents(cellEvents[i].inputPorts)
        
    def updateButtonClick(self):
        self.updateButton.setEnabled(False)
        try:
            self.updateCells()
        finally:
            self.updateButton.setEnabled(True
                                         )
    def toggleEditingMode(self):
        if len(self.controlDocks) > 0:
            for dock in self.controlDocks.itervalues():
                dock.toggleTitleBar()
            self.editing = not self.editing
        if not self.editing:
            self.saveSettings()
               
    def saveSettings(self):
        layout = self.saveState().toPercentEncoding()
        geom = self.saveGeometry().toPercentEncoding()
            
        self.currentMashup.layout = layout
        self.currentMashup.geometry = geom
        
        self.controller.setChanged(True)
        
        #self.controller.writeMashuptrail()
   
    def closeEvent(self, event):
        self.saveSettings()
        self.appWasClosed.emit(self)
        event.accept()
        
    def auto_update_changed(self, state):
        if state == QtCore.Qt.Unchecked:
            self.updateButton.setEnabled(True)
        elif state == QtCore.Qt.Checked:
            self.updateButton.setEnabled(False)
            
    def saveAll(self):
        for w in self.widgets:
            w.saveAll(self.dumpcells)
            
    def saveEach(self):
        for w in self.widgets:
            w.saveEach(self.dumpcells, self.frameNo)
        
    def saveEventAction(self, checked):
        self.saveEvent()
          
    def saveEvent(self, folder=None):
        if folder == None:
            folder = QtGui.QFileDialog.getExistingDirectory(self,
                                                        "Save images to...",
                                                        self.lastExportPath,
                                                        QtGui.QFileDialog.ShowDirsOnly)
        if not folder.isEmpty():
            self.dumpcells = str(folder)
            self.saveEach()
            self.lastExportPath = str(folder)
            
    def saveAllEvent(self, folder=None):
        if folder == None:
            folder = QtGui.QFileDialog.getExistingDirectory(self,
                                                        "Save images to...",
                                                        self.lastExportPath,
                                                        QtGui.QFileDialog.ShowDirsOnly)
        if not folder.isEmpty():
            self.dumpcells = str(folder)
            self.saveAll()
            self.lastExportPath
    
    def saveAndExport(self, clicked=True):
        self.saveAll()
        
    def initCells(self, cellEvents):
        cellLayout = QtGui.QHBoxLayout()
        self.mainLayout.addLayout(cellLayout, self.numberOfCells * 2)
        self.cellWidgets = []
        vtkCells = []
        for event in cellEvents:
            cellWidget = event.cellType(self.centralWidget())
            if event.cellType.__name__ == 'QVTKWidget':
                vtkCells.append(cellWidget)
            cellWidget.updateContents(event.inputPorts)
            cellWidget.show()
            cellWidget.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                      QtGui.QSizePolicy.Expanding)
            cellWidget.setMinimumSize(300, 100)
            cellLayout.addWidget(cellWidget)
            self.cellWidgets.append(cellWidget)
        def getSelectedCellWidgets():
            return vtkCells
        for cellWidget in self.vtkCells:
            cellWidget.getSelectedCellWidgets = getSelectedCellWidgets
      
    def initControls(self):
        if len(self.currentMashup.alias_list) == 0:
            return
        
        #Constructing alias controls
        self.controlDocks = {}
        self.cellControls = {}
        self.toolbuttons = {}
        
        row = 0
        for alias in self.currentMashup.alias_list:
            dock = QCustomDockWidget(alias.name, #"Control for '%s'" % aliasName,
                                      self)
            vtparam = self.controller.getVistrailParam(alias)
            
            if alias.component.widget == 'slider':
                aliasWidget = QAliasSliderWidget(alias, vtparam, dock)
            elif alias.component.widget == 'numericstepper':
                aliasWidget = QAliasNumericStepperWidget(alias, vtparam, dock)
            else:
                aliasWidget = QDropDownWidget(alias, vtparam, dock)
            
            aliasWidget.setSizePolicy(QtGui.QSizePolicy.Preferred,
                                          QtGui.QSizePolicy.Maximum)
            self.connect(aliasWidget,
                             QtCore.SIGNAL("contentsChanged"),
                             self.widget_changed)
                
            dock.setWidget(aliasWidget)
            self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)
            self.controlDocks[alias.name] = dock
            self.cellControls[alias.name] = aliasWidget.value
            row += 1
            self.aliasWidgets[alias.name] = aliasWidget
        
        # Added a stretch space
        stretchDock = QCustomDockWidget('Stretch Space', self)
        stretch = QtGui.QWidget()
        stretch.setLayout(QtGui.QVBoxLayout())
        stretch.layout().addStretch()
        stretchDock.setWidget(stretch)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, stretchDock)
        self.controlDocks["_stretch_"] = stretchDock
            
    def widget_changed(self, info):
        if self.cb_auto_update.isChecked() and not self.is_executing:
            self.updateCells()
        
            
    def run(self, useDefaultValues=False):
        
        # Building the list of parameter values
        params = []
        if useDefaultValues:
            for alias in self.currentMashup.alias_list:
                params.append((alias.component.vttype, alias.component.vtid,
                              alias.component.val))
        else:
            for (aliasName, edit) in self.cellControls.iteritems():
                alias = self.currentMashup.getAliasByName(aliasName)
                if hasattr(edit, 'contents'):
                    val = str(edit.contents())
                else:
                    val =str(edit.text())
                params.append((alias.component.vttype, alias.component.vtid,
                              val))    
        results = self.controller.execute(params)[0]
        result = results[0]
        (objs, errors, executed) = (result.objects, result.errors,
                                                   result.executed)
        if len(errors) > 0:
            print '=== ERROR EXECUTING PIPELINE ==='
            print errors
            return (False, errors)
        return (True, [])
    
    def showBuilderWindow(self):
        from gui.vistrails_window import _app
        _app.show()
            
class QCustomDockWidget(QtGui.QDockWidget):
    def __init__(self, title, parent=None):
        QtGui.QDockWidget.__init__(self, title, parent)
        self.setObjectName(title)
        self.setFeatures(QtGui.QDockWidget.DockWidgetClosable | 
                         QtGui.QDockWidget.DockWidgetMovable)
        self.emptyTitleBar = QtGui.QWidget()
        self.titleBarVisible = True
        self.hideTitleBar()

    def showTitleBar(self):
        self.titleBarVisible = True
        self.setFeatures(QtGui.QDockWidget.DockWidgetClosable | 
                         QtGui.QDockWidget.DockWidgetMovable)
        self.setMaximumHeight(524287)
        self.setTitleBarWidget(None)

    def hideTitleBar(self):
        self.titleBarVisible = False
        self.setFeatures(QtGui.QDockWidget.NoDockWidgetFeatures)
        self.setTitleBarWidget(self.emptyTitleBar)

    def toggleTitleBar(self):
        if self.titleBarVisible:
            self.hideTitleBar()
        else:
            self.showTitleBar()
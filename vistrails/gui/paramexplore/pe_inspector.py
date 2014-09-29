###############################################################################
##
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
from PyQt4 import QtGui, QtCore

from vistrails.gui.paramexplore.virtual_cell import QVirtualCellWindow
from vistrails.gui.vistrails_palette import QVistrailsPaletteInterface
from vistrails.gui.theme import CurrentTheme
from pe_view import QParamExploreView 

import weakref

class QParamExploreInspector(QtGui.QWidget, QVistrailsPaletteInterface):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.set_title("Explore Inspector")

        layout = QtGui.QVBoxLayout()
        layout.setMargin(2)
        layout.setSpacing(3)

        self.controller = None
        self.pe_properties = QParamExpProperties()
        p_prop_group = QtGui.QGroupBox(self.pe_properties.windowTitle())
        g_layout = QtGui.QVBoxLayout()
        g_layout.setMargin(0)
        g_layout.setSpacing(0)
        g_layout.addWidget(self.pe_properties)
        p_prop_group.setLayout(g_layout)
        layout.addWidget(p_prop_group)
        self.virtual_cell = QVirtualCellWindow()
        v_cell_group = QtGui.QGroupBox(self.virtual_cell.windowTitle())
        g_layout = QtGui.QVBoxLayout()
        g_layout.setMargin(0)
        g_layout.setSpacing(0)
        g_layout.addWidget(self.virtual_cell)
        v_cell_group.setLayout(g_layout)
        layout.addWidget(v_cell_group)
        self.setLayout(layout)
        self.addButtonsToToolbar()

    def addButtonsToToolbar(self):
        # Add the back/forward exploration buttons
        self.versionsLabel = QtGui.QLabel('Exploration: 0/0')
        self.toolWindow().toolbar.insertWidget(self.toolWindow().pinAction,
                                               self.versionsLabel)
        self.pe_properties.versionsLabel = weakref.proxy(self.versionsLabel)
        self.backAction = QtGui.QAction(
            QtGui.QIcon(CurrentTheme.LEFT_ARROW_PIXMAP),
            'Go to Previous Exploration', None, triggered=self.backPressed)
        self.toolWindow().toolbar.insertAction(self.toolWindow().pinAction,
                                               self.backAction)
        self.pe_properties.backAction = weakref.proxy(self.backAction)
        self.forwardAction = QtGui.QAction(
            QtGui.QIcon(CurrentTheme.RIGHT_ARROW_PIXMAP),
            'Got to Next Exploration', None, triggered=self.forwardPressed)
        self.toolWindow().toolbar.insertAction(self.toolWindow().pinAction,
                                               self.forwardAction)
        self.pe_properties.forwardAction = weakref.proxy(self.forwardAction)

    def set_controller(self, controller):
        if self.controller == controller:
            return
        self.controller = controller
        self.pe_properties.updateController(controller)
        if self.controller is not None:
            self.set_pipeline(self.controller.current_pipeline)
        else:
            self.set_pipeline(None)

    def set_pipeline(self, pipeline):
        self.pipeline = pipeline
        self.virtual_cell.updateVirtualCell(pipeline)
        self.stateChanged()

    def stateChanged(self):
        self.pe_properties.updateVersion()

    def set_exploration(self, pe = None):
        self.stateChanged()

    def backPressed(self):
        self.pe_properties.goBack()

    def forwardPressed(self):
        self.pe_properties.goForward()
        

class QParamExpProperties(QtGui.QWidget):
    def __init__(self, controller=None, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.controller = controller
        self.versionNumber = -1
        self.versionsLabel = None
        self.backAction = None
        self.forwardAction = None
        vLayout = QtGui.QVBoxLayout()
        self.setLayout(vLayout)
        vLayout.setMargin(3)
        vLayout.setSpacing(3)
        gLayout = QtGui.QGridLayout()
        gLayout.setColumnMinimumWidth(1,5)
        gLayout.setRowMinimumHeight(0,24)
        gLayout.setRowMinimumHeight(1,24)
        gLayout.setRowMinimumHeight(2,24)
        gLayout.setRowMinimumHeight(3,24)        
        vLayout.addLayout(gLayout)
        gLayout.setMargin(3)
        gLayout.setSpacing(3)
        
        #vtVersionLabel = QtGui.QLabel('Workflow:', self)
        #gLayout.addWidget(vtVersionLabel, 0, 0, 1, 1)
        
        #self.vtVersionEdit = QtGui.QLabel('', self)
        #gLayout.addWidget(self.vtVersionEdit, 0, 2, 1, 1)
        
        tagLabel = QtGui.QLabel('Exploration Tag:', self)
        gLayout.addWidget(tagLabel, 0, 0, 1, 1)

        editLayout = QtGui.QHBoxLayout()
        self.tagEdit = QtGui.QLineEdit()
        tagLabel.setBuddy(self.tagEdit)
        editLayout.addWidget(self.tagEdit)
        self.tagEdit.setEnabled(False)

        self.tagReset = QtGui.QToolButton(self)
        self.tagReset.setIcon(QtGui.QIcon(
              self.style().standardPixmap(QtGui.QStyle.SP_DialogCloseButton)))
        self.tagReset.setIconSize(QtCore.QSize(12,12))
        self.tagReset.setAutoRaise(True)
        self.tagReset.setEnabled(False)
        editLayout.addWidget(self.tagReset)

        gLayout.addLayout(editLayout, 0, 2, 1, 1)

        userLabel = QtGui.QLabel('User:', self)
        gLayout.addWidget(userLabel, 1, 0, 1, 1)
        
        self.userEdit = QtGui.QLabel('', self)
        gLayout.addWidget(self.userEdit, 1, 2, 1, 1)

        dateLabel = QtGui.QLabel('Date:', self)
        gLayout.addWidget(dateLabel, 2, 0, 1, 1)

        self.dateEdit = QtGui.QLabel('', self)
        gLayout.addWidget(self.dateEdit, 2, 2, 1, 1)
        
        self.connect(self.tagEdit, QtCore.SIGNAL('editingFinished()'),
                     self.tagFinished)
        self.connect(self.tagEdit, QtCore.SIGNAL('textChanged(QString)'),
                     self.tagChanged)
        self.connect(self.tagReset, QtCore.SIGNAL('clicked()'),
                     self.tagCleared)
        
    def updateController(self, controller):
        self.controller = controller

    def updateVersion(self):
        self.pe = None
        if self.controller:
            # Check if version changed
            version_changed = False
            if self.controller.current_parameter_exploration and \
               self.controller.current_parameter_exploration.action_id !=\
                self.controller.current_version:
                # we need to remove it
                version_changed = True
                self.controller.current_parameter_exploration=None
            
            if not self.controller.current_parameter_exploration and \
                self.controller.vistrail.has_paramexp(
                                             self.controller.current_version):
                version_changed = True
                # load latest version
                self.controller.current_parameter_exploration = \
                            self.controller.vistrail.get_paramexp(
                                              self.controller.current_version)

            if version_changed:
                from vistrails.gui.vistrails_window import _app
                _app.notify('exploration_changed')
                return

            self.pe = self.controller.current_parameter_exploration
        if self.controller and self.pe:
            # get all pe for this action
            self.peDict = dict([(pe.id, pe) for pe in
                            self.controller.vistrail.parameter_explorations
                            if pe.action_id==self.pe.action_id])
            count = len(self.peDict)
            ids = self.peDict.keys()
            ids.sort()
            index = ids.index(self.pe.id) + 1
            
            text = 'Exploration: %s/%s' % (index, count)
            self.versionsLabel.setText(text)
            self.backAction.setEnabled(index>1)
            self.forwardAction.setEnabled(index<count)
            self.tagEdit.setEnabled(True)
            self.tagReset.setEnabled(True)
            self.tagEdit.setText(self.pe.name or "")
            self.userEdit.setText(self.pe.user or "")
            self.dateEdit.setText(self.pe.date.strftime('%Y-%m-%d %H:%M:%S')
                                  if self.pe.date else "")
        else:
            self.versionsLabel.setText('Exploration: 0/0')
            self.backAction.setEnabled(False)
            self.forwardAction.setEnabled(False)
            self.tagEdit.setEnabled(False)
            self.tagReset.setEnabled(False)
            self.tagEdit.setText('')
            self.userEdit.setText('')
            self.dateEdit.setText('')  
            
    def tagFinished(self):
        """ tagFinished() -> None
        Update the new tag to pe
        
        """
        if self.pe:
            currentText = str(self.tagEdit.text())
            if self.pe.name != currentText and \
               not self.controller.vistrail.has_named_paramexp(currentText):
                #print "will update current tag", currentText
                self.pe.name = currentText
                self.controller.set_changed(True)
            else:
                self.tagEdit.setText(self.pe.name)
                
    def tagChanged(self, text):
        """ tagChanged(text: QString) -> None
        Update the button state if there is text

        """
        self.tagReset.setEnabled(text != '')

    def tagCleared(self):
        """ tagCleared() -> None
        Remove the tag
        
        """ 
        self.tagEdit.setText('')
        self.tagFinished()
        
    def goBack(self):
        """ Goes to the previous PE for this pipeline"""
        ids = self.peDict.keys()
        ids.sort()
        index = ids.index(self.pe.id)
        if index>0:
            pe = self.peDict[ids[index-1]]
            self.controller.current_parameter_exploration = pe
            from vistrails.gui.vistrails_window import _app
            _app.notify('exploration_changed')


    def goForward(self):
        """ Goes to the next PE for this pipeline"""
        count = len(self.peDict)
        ids = self.peDict.keys()
        ids.sort()
        index = ids.index(self.pe.id)
        if index<count-1:
            pe = self.peDict[ids[index+1]]
            self.controller.current_parameter_exploration = pe
            from vistrails.gui.vistrails_window import _app
            _app.notify('exploration_changed')

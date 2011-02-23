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
from PyQt4 import QtCore, QtGui
from core.utils import VistrailsInternalError
from core.vistrail.port import PortEndPoint
from gui.utils import show_question, SAVE_BUTTON, DISCARD_BUTTON

class StandardModuleConfigurationWidget(QtGui.QWidget):

    def __init__(self, module, controller, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.module = module
        self.module_descriptor = self.module.module_descriptor
        self.controller = controller
        self.state_changed = False
        
    def activate(self):
        #reimplement this to set the focus to a certain widget when activated
        pass
    
    def askToSaveChanges(self):
        if self.state_changed:
            message = ('Configuration panel contains unsaved changes. '
                      'Do you want to save changes before proceeding?' )
            res = show_question('VisTrails',
                                message,
                                buttons = [SAVE_BUTTON, DISCARD_BUTTON])
            if res == SAVE_BUTTON:
                self.saveTriggered()
                return True
            else:
                self.resetTriggered()
                return False
            
    def saveTriggered(self):
        msg = "Must implement saveTriggered in subclass"
        raise VistrailsInternalError(msg)
    
    def resetTriggered(self):
        msg = "Must implement saveTriggered in subclass"
        raise VistrailsInternalError(msg)
    
class DefaultModuleConfigurationWidget(StandardModuleConfigurationWidget):

    def __init__(self, module, controller, parent=None):
        StandardModuleConfigurationWidget.__init__(self, module, controller, 
                                                   parent)
       
        self.setLayout(QtGui.QVBoxLayout())
        self.layout().setMargin(0)
        self.layout().setSpacing(0)
        self.scrollArea = QtGui.QScrollArea(self)
        self.layout().addWidget(self.scrollArea)
        self.scrollArea.setFrameStyle(QtGui.QFrame.NoFrame)
        self.listContainer = QtGui.QWidget(self.scrollArea)
        self.listContainer.setLayout(QtGui.QGridLayout(self.listContainer))
        self.listContainer.setFocusPolicy(QtCore.Qt.WheelFocus)
        self.inputPorts = self.module.destinationPorts()
        self.inputDict = {}
        self.outputPorts = self.module.sourcePorts()
        self.outputDict = {}
        self.constructList()
        self.buttonLayout = QtGui.QHBoxLayout()
        self.buttonLayout.setMargin(5)
        self.saveButton = QtGui.QPushButton('&Save', self)
        self.saveButton.setFixedWidth(100)
        self.saveButton.setEnabled(False)
        self.buttonLayout.addWidget(self.saveButton)
        self.resetButton = QtGui.QPushButton('&Reset', self)
        self.resetButton.setFixedWidth(100)
        self.resetButton.setEnabled(False)
        self.buttonLayout.addWidget(self.resetButton)
        
        self.layout().addLayout(self.buttonLayout)
        self.connect(self.saveButton, QtCore.SIGNAL('clicked(bool)'), 
                     self.saveTriggered)
        self.connect(self.resetButton, QtCore.SIGNAL('clicked(bool)'), 
                     self.resetTriggered)
        self.setMouseTracking(True)
        self.setFocusPolicy(QtCore.Qt.WheelFocus)
        self.adjustSize()
        self.mouseOver = False
        self.state_changed = False
        
    ###########################################################################
    # Focus event handlers
    # There is something wrong with focus on this widget, because I couldn't
    # get it to work with just self.setFocusPolicy() and reimplementing 
    # focusOutEvent. No focus events were being generated at all
    # I had to force calling setFocus(reason) when something changed
    # and as this was also generating focusOutEvents when it shouldn't. 
    # So I also had to force to emit focusOutEvent only when the mouse is not 
    # over this panel.
    # I already spent a lot of time trying fix and I couldn't.
    # If anybody has the time to fix this, please do it. (Emanuele)     
    def focusOutEvent(self, event):
        if self.mouseOver:
            event.ignore()
        else:
            self.askToSaveChanges()
            QtGui.QWidget.focusOutEvent(self, event)
        
    def enterEvent(self, event):
        self.mouseOver = True
        
    def leaveEvent(self, event):
        self.mouseOver = False
        
    def checkBoxFromPort(self, port, input_=False):
        checkBox = QtGui.QCheckBox(port.name)
        if input_:
            pep = PortEndPoint.Destination
        else:
            pep = PortEndPoint.Source
        if not port.optional or (pep, port.name) in self.module.portVisible:
            checkBox.setCheckState(QtCore.Qt.Checked)
        else:
            checkBox.setCheckState(QtCore.Qt.Unchecked)
        if not port.optional or (input_ and port.sigstring=='()'):
            checkBox.setEnabled(False)
        return checkBox

    def constructList(self):
        label = QtGui.QLabel('Input Ports')
        label.setAlignment(QtCore.Qt.AlignHCenter)
        label.font().setBold(True)
        label.font().setPointSize(12)
        self.listContainer.layout().addWidget(label, 0, 0)
        label = QtGui.QLabel('Output Ports')
        label.setAlignment(QtCore.Qt.AlignHCenter)
        label.font().setBold(True)
        label.font().setPointSize(12)
        self.listContainer.layout().addWidget(label, 0, 1)

        for i in xrange(len(self.inputPorts)):
            port = self.inputPorts[i]
            checkBox = self.checkBoxFromPort(port, True)
            checkBox.setFocusPolicy(QtCore.Qt.StrongFocus)
            self.connect(checkBox, QtCore.SIGNAL("stateChanged(int)"),
                         self.updateState)
            self.inputDict[port.name] = checkBox
            self.listContainer.layout().addWidget(checkBox, i+1, 0)
        
        for i in xrange(len(self.outputPorts)):
            port = self.outputPorts[i]
            checkBox = self.checkBoxFromPort(port)
            checkBox.setFocusPolicy(QtCore.Qt.StrongFocus)
            self.connect(checkBox, QtCore.SIGNAL("stateChanged(int)"),
                         self.updateState)
            self.outputDict[port.name] = checkBox
            self.listContainer.layout().addWidget(checkBox, i+1, 1)
        
        self.listContainer.adjustSize()
        self.listContainer.setFixedHeight(self.listContainer.height())
        self.scrollArea.setWidget(self.listContainer)
        self.scrollArea.setWidgetResizable(True)

    def sizeHint(self):
        return QtCore.QSize(384, 512)
        
    def saveTriggered(self, checked = False):
        for port in self.inputPorts:
            entry = (PortEndPoint.Destination, port.name)
            if (port.optional and
                self.inputDict[port.name].checkState()==QtCore.Qt.Checked):
                self.module.portVisible.add(entry)
            else:
                self.module.portVisible.discard(entry)
            
        for port in self.outputPorts:
            entry = (PortEndPoint.Source, port.name)
            if (port.optional and
                self.outputDict[port.name].checkState()==QtCore.Qt.Checked):
                self.module.portVisible.add(entry)
            else:
                self.module.portVisible.discard(entry)
        self.saveButton.setEnabled(False)
        self.resetButton.setEnabled(False)
        self.state_changed = False
        self.emit(QtCore.SIGNAL("stateChanged"))
        self.emit(QtCore.SIGNAL('doneConfigure'), self.module.id)
        
    def closeEvent(self, event):
        self.askToSaveChanges()
        event.accept()
                
    def resetTriggered(self):
        self.setFocus(QtCore.Qt.MouseFocusReason)
        self.setUpdatesEnabled(False)
        for i in xrange(len(self.inputPorts)):
            port = self.inputPorts[i]
            entry = (PortEndPoint.Destination, port.name)
            checkBox = self.inputDict[port.name]
            if not port.optional or entry in self.module.portVisible:
                checkBox.setCheckState(QtCore.Qt.Checked)
            else:
                checkBox.setCheckState(QtCore.Qt.Unchecked)
            if not port.optional or port.sigstring=='()':
                checkBox.setEnabled(False)
        for i in xrange(len(self.outputPorts)):
            port = self.outputPorts[i]
            entry = (PortEndPoint.Source, port.name)
            checkBox = self.outputDict[port.name]
            if not port.optional or entry in self.module.portVisible:
                checkBox.setCheckState(QtCore.Qt.Checked)
            else:
                checkBox.setCheckState(QtCore.Qt.Unchecked)
            if not port.optional:
                checkBox.setEnabled(False)
        self.setUpdatesEnabled(True)
        self.saveButton.setEnabled(False)
        self.resetButton.setEnabled(False)
        self.state_changed = False
        self.emit(QtCore.SIGNAL("stateChanged"))
        
    def updateState(self, state):
        self.setFocus(QtCore.Qt.MouseFocusReason)
        self.saveButton.setEnabled(True)
        self.resetButton.setEnabled(True)
        if not self.state_changed:
            self.state_changed = True
            self.emit(QtCore.SIGNAL("stateChanged"))
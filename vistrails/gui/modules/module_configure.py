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
from core.utils import VistrailsInternalError
from core.vistrail.port import PortEndPoint
from gui.utils import show_question, SAVE_BUTTON, DISCARD_BUTTON
from gui.common_widgets import QPromptWidget

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
        self.prompt = QPromptWidget()
        self.prompt.setPromptText("Please use the visibility icon (an eye) in" 
                                  " the Module Information panel to show or"
                                  " hide a port.")
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.prompt)
        self.setLayout(layout)
        self.prompt.showPrompt()
        
    def saveTriggered(self):
        pass
    
    def resetTriggered(self):
        pass
    
class _DefaultModuleConfigurationWidget(StandardModuleConfigurationWidget):
    """ This is the Default ModuleConfigurationWidget that shows a list of
        ports to be enabled or disabled """
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
#        self.mouseOver = False
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
    #
    # DAK -- seems to be ok when in the palette window...

#    def focusOutEvent(self, event):
#        #self.askToSaveChanges()
#        QtGui.QWidget.focusOutEvent(self, event)
#        
#    def enterEvent(self, event):
#        self.mouseOver = True
#        
#    def leaveEvent(self, event):
#        self.mouseOver = False
        
    def checkBoxFromPort(self, port, input_=False):
        checkBox = QtGui.QCheckBox(port.name)
        if input_:
            port_visible = port.name in self.module.visible_input_ports
        else:
            port_visible = port.name in self.module.visible_output_ports
        if not port.optional or port_visible:
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
            if (port.optional and
                self.inputDict[port.name].checkState()==QtCore.Qt.Checked):
                self.module.visible_input_ports.add(port.name)
            else:
                self.module.visible_input_ports.discard(port.name)
            
        for port in self.outputPorts:
            if (port.optional and
                self.outputDict[port.name].checkState()==QtCore.Qt.Checked):
                self.module.visible_output_ports.add(port.name)
            else:
                self.module.visible_output_ports.discard(port.name)
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
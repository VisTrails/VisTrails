############################################################################
##
## Copyright (C) 2006-2007 University of Utah. All rights reserved.
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
from core.modules.module_registry import get_module_registry
# from core.vistrail.action import ChangeParameterAction
from core.vistrail.port import PortEndPoint

class StandardModuleConfigurationWidget(QtGui.QDialog):

    def __init__(self, module, controller, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setModal(True)
        self.module = module
        reg = get_module_registry()
        self.module_descriptor = self.module.module_descriptor
        self.controller = controller


class DefaultModuleConfigurationWidget(StandardModuleConfigurationWidget):

    def __init__(self, module, controller, parent=None):
        StandardModuleConfigurationWidget.__init__(self, module, controller, parent)
        self.setWindowTitle('Module Configuration')
        self.setLayout(QtGui.QVBoxLayout())
        self.layout().setMargin(0)
        self.layout().setSpacing(0)
        self.scrollArea = QtGui.QScrollArea(self)
        self.layout().addWidget(self.scrollArea)
        self.scrollArea.setFrameStyle(QtGui.QFrame.NoFrame)
        self.listContainer = QtGui.QWidget(self.scrollArea)
        self.listContainer.setLayout(QtGui.QGridLayout(self.listContainer))
        self.inputPorts = self.module.destinationPorts()
        self.inputDict = {}
        self.outputPorts = self.module.sourcePorts()
        self.outputDict = {}
        self.constructList()
        self.buttonLayout = QtGui.QHBoxLayout()
        self.buttonLayout.setMargin(5)
        self.okButton = QtGui.QPushButton('&OK', self)
        self.okButton.setFixedWidth(100)
        self.buttonLayout.addWidget(self.okButton)
        self.cancelButton = QtGui.QPushButton('&Cancel', self)
        self.cancelButton.setShortcut('Esc')
        self.cancelButton.setFixedWidth(100)
        self.buttonLayout.addWidget(self.cancelButton)
        self.layout().addLayout(self.buttonLayout)
        self.connect(self.okButton, QtCore.SIGNAL('clicked(bool)'), self.okTriggered)
        self.connect(self.cancelButton, QtCore.SIGNAL('clicked(bool)'), self.close)

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
            self.inputDict[port.name] = checkBox
            self.listContainer.layout().addWidget(checkBox, i+1, 0)
        
        for i in xrange(len(self.outputPorts)):
            port = self.outputPorts[i]
            checkBox = self.checkBoxFromPort(port)
            self.outputDict[port.name] = checkBox
            self.listContainer.layout().addWidget(checkBox, i+1, 1)
        
        self.listContainer.adjustSize()
        self.listContainer.setFixedHeight(self.listContainer.height())
        self.scrollArea.setWidget(self.listContainer)
        self.scrollArea.setWidgetResizable(True)

    def sizeHint(self):
        return QtCore.QSize(384, 512)

    def okTriggered(self, checked = False):
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
        self.close()
        

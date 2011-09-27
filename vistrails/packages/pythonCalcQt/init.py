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

import core.modules.module_registry
from core.modules.vistrails_module import Module, ModuleError
from PyQt4 import QtCore, QtGui
import api

class QPythonCalc(QtGui.QWidget):
    """QPythonCalc is a widget used for specifying PythonCalc
    parameters and providing two buttons for compute and add that
    module to the pipeline. """
    
    def __init__(self, parent=None):
        """ init(parent: QWidget) -> None        
        We construct a simple GUI with edit boxes for 2 operands and a
        combo box for the operator. There are also 2 buttons: (1)
        perform the calculation and display the result, (2) create a
        PythonCalc module with the specified parameters and add to the
        current pipeline.

        """
        QtGui.QWidget.__init__(self, parent)
        self.setWindowTitle('PythonCalc GUI')
        gridLayout = QtGui.QGridLayout()
        self.setLayout(gridLayout)
        gridLayout.addWidget(QtGui.QLabel('value1'), 0, 0)
        gridLayout.addWidget(QtGui.QLabel('value2'), 1, 0)
        gridLayout.addWidget(QtGui.QLabel('op'), 2, 0)
        gridLayout.addWidget(QtGui.QLabel('result'), 3, 0)
        
        numberValidator = QtGui.QIntValidator(self)
        self.value1Edit = QtGui.QLineEdit('0')
        self.value2Edit = QtGui.QLineEdit('0')
        self.value1Edit.setValidator(numberValidator)
        self.value2Edit.setValidator(numberValidator)
        gridLayout.addWidget(self.value1Edit, 0, 1)
        gridLayout.addWidget(self.value2Edit, 1, 1)
        
        self.opCombo = QtGui.QComboBox()
        self.opCombo.addItems(['+', '-', '*', '/'])
        gridLayout.addWidget(self.opCombo, 2, 1)

        self.resultLabel = QtGui.QLabel()
        gridLayout.addWidget(self.resultLabel, 3, 1)

        self.calculateButton = QtGui.QPushButton('Calculate')
        gridLayout.addWidget(self.calculateButton, 4, 0)
        self.connect(self.calculateButton, QtCore.SIGNAL('clicked()'),
                     self.calculate)

        self.createModuleButton = QtGui.QPushButton('Create Module')
        gridLayout.addWidget(self.createModuleButton, 4, 1)
        self.connect(self.createModuleButton, QtCore.SIGNAL('clicked()'),
                     self.createModule)

    def calculate(self):
        """ calculate() -> None        
        Perform the calculation based on value1, value2 and op,
        similar to the PythonCalc module, but through the GUI.

        """
        result = eval(str(self.value1Edit.text() +
                          self.opCombo.currentText() +
                          self.value2Edit.text()))
        self.resultLabel.setText(str(result))

    def createModule(self):
        """ createModule() -> None
        Collect parameters, values and operator, and create a
        PythonCalc module to the current pipeline using the API
        provided in vistrails.api.

        """
        pythoncalc = "edu.utah.sci.vistrails.pythoncalc"
        module = api.add_module(0, 0, pythoncalc, 'PythonCalc', '')
        api.get_current_controller().update_function(module, 'value1',
                                                     [str(self.value1Edit.text())])
        api.get_current_controller().update_function(module, 'value2',
                                                     [str(self.value2Edit.text())])
        api.get_current_controller().update_function(module, 'op',
                                                     [str(self.opCombo.currentText())])
        api.switch_to_pipeline_view()

def initialize(*args, **keywords):
    """ initialize() -> None    
    Package-entry to initialize the package. We just create and show
    the main window, a QPythonCalc widget, here.
    
    """
    global mainWindow
    mainWindow = QPythonCalc()
    mainWindow.show()

def menu_items():
    """menu_items() -> tuple of (str,function)
    It returns a list of pairs containing text for the menu and a
    callback function that will be executed when that menu item is
    selected. This will add a 'Create Module' menu item under the
    Packages>PythonCalcQt menu. It has the same functionality as the
    'Create Module' button, which adds a PythonCalc with specified
    parameters module to the current pipeline.
    
    """
    lst = []
    global mainWindow
    lst.append(("Create Module", mainWindow.createModule))
    return tuple(lst)    

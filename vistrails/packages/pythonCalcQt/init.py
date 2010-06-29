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

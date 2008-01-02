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
""" This file describe the plot script module and its configuration
widget

"""
from PyQt4 import QtCore, QtGui
from core.modules.basic_modules import PythonSource
from core.modules.vistrails_module import Module, NotCacheable, ModuleError
from core.modules.module_configure import StandardModuleConfigurationWidget, \
     PythonSourceConfigurationWidget, PythonEditor
import urllib

############################################################################

class MplPlot(PythonSource):
    """
    MplPlot is a module similar to PythonSource. The user can enter
    Matplotlib code into this module. This will then get connected to
    MplFigure to draw the figure. Please note that, codes entered in
    this module should limit to subplot() scope only. Using
    Figure-level commands, e.g. figure() or show(), the result will be
    unknown
    
    """

    def compute(self):
        """ compute() -> None        
        We postpone the computation of the plot script to the
        MplFigure module for a unified execution.
        
        """
        if self.hasInputFromPort('source'):
            if self.outputPorts.has_key('source'):
                source = self.getInputFromPort('source')
                s = ('from pylab import *\n' +
                     'from numpy import *\n' +
                     urllib.unquote(source))
                self.run_code(s, use_input=True, use_output=True)

class MplPlotConfigurationWidget(PythonSourceConfigurationWidget):
    def __init__(self, module, controller, parent=None):
        """ MplPlotConfigurationWidget(module: Module,
                                       controller: VistrailController,
                                       parent: QWidget)
                                       -> MplPlotConfigurationWidget                                       
        Setup the dialog to similar to PythonSource but with a
        different name
        
        """
        PythonSourceConfigurationWidget.__init__(self, module,
                                                 controller, parent)
        self.setWindowTitle('MplPlot Script Editor')
    

class _MplPlotConfigurationWidget(StandardModuleConfigurationWidget):
    """
    MplPlotConfigurationWidget is simialr to PythonSource
    configuration widget except that it doesn't allow add/remove
    ports. In this configuration widget, the user will enter their
    Matplotlib script to pass down to MplFigure module
    
    """
    def __init__(self, module, controller, parent=None):
        """ MplPlotConfigurationWidget(module: Module,
                                       controller: VistrailController,
                                       parent: QWidget)
                                       -> MplPlotConfigurationWidget                                       
        Setup the dialog to have a single python source editor and 2
        buttons
        
        """
        StandardModuleConfigurationWidget.__init__(self, module,
                                                   controller, parent)
        self.setWindowTitle('MplPlot Script Editor')
        self.setLayout(QtGui.QVBoxLayout())
        self.layout().setMargin(0)
        self.layout().setSpacing(0)
        self.createEditor()
        self.createButtonLayout()        
    
    def findSourceFunction(self):
        """ findSourceFunction() -> int
        Return the function id associated with input port 'source'
        
        """
        fid = -1
        for i in xrange(self.module.getNumFunctions()):
            if self.module.functions[i].name=='source':
                fid = i
                break
        return fid

    def createEditor(self):
        """ createEditor() -> None
        Add a python editor into the widget layout
        
        """
        self.codeEditor = PythonEditor(self)
        fid = self.findSourceFunction()
        if fid!=-1:
            f = self.module.functions[fid]
            self.codeEditor.setPlainText(urllib.unquote(f.params[0].strValue))
        self.codeEditor.document().setModified(False)
        self.layout().addWidget(self.codeEditor, 1)
        
    def createButtonLayout(self):
        """ createButtonLayout() -> None
        Construct Ok & Cancel button
        
        """
        self.buttonLayout = QtGui.QHBoxLayout()
        self.buttonLayout.setMargin(5)
        self.okButton = QtGui.QPushButton('&OK', self)
        self.okButton.setAutoDefault(False)
        self.okButton.setFixedWidth(100)
        self.buttonLayout.addWidget(self.okButton)
        self.cancelButton = QtGui.QPushButton('&Cancel', self)
        self.cancelButton.setAutoDefault(False)
        self.cancelButton.setShortcut('Esc')
        self.cancelButton.setFixedWidth(100)
        self.buttonLayout.addWidget(self.cancelButton)
        self.layout().addLayout(self.buttonLayout)
        self.connect(self.okButton, QtCore.SIGNAL('clicked(bool)'), self.okTriggered)
        self.connect(self.cancelButton, QtCore.SIGNAL('clicked(bool)'), self.close)

    def sizeHint(self):
        """ sizeHint() -> QSize
        Return the recommendation size of this widget
        
        """
        return QtCore.QSize(512, 512)

    def updateController(self, controller):
        """ updateController() -> None        
        Based on the input of the python editor, update the vistrail
        controller appropriately
        
        """
        if self.codeEditor.document().isModified():
            code = urllib.quote(str(self.codeEditor.toPlainText()))
            fid = self.findSourceFunction()

            # FIXME make sure that this makes sense
            if fid==-1:
                # do add function
                fid = self.module.getNumFunctions()
                f = ModuleFunction(pos=fid,
                                   name='source')
                param = ModuleParam(type='String',
                                    strValue=code,
                                    alias='',
                                    name='<no description>',
                                    pos=0)
                f.addParameter(param)
                controller.addMethod(self.module.id, f)
            else:
                # do change parameter
                paramList = [(code, 'String', '')]
                controller.replace_method(self.module, fid, paramList)

#             if fid==-1:
#                 fid = self.module.getNumFunctions()
#             action = ChangeParameterAction()
#             action.addParameter(self.module.id, fid, 0, 'source',
#                                 '<no description>',code,'String', '')
#             controller.performAction(action)

    def okTriggered(self, checked = False):
        """ okTriggered(checked: bool) -> None
        Update vistrail controller (if neccesssary) then close the widget
        
        """
        self.updateController(self.controller)
        self.close()

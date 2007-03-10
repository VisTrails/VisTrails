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
"""Modules for handling vtkRenderWindowInteractor events"""
from PyQt4 import QtCore, QtGui
from core.modules.basic_modules import String
from core.modules.vistrails_module import Module, NotCacheable
from core.modules.module_registry import registry
from core.modules.module_configure import StandardModuleConfigurationWidget, \
     PythonEditor
from core.vistrail.action import ChangeParameterAction
import urllib

################################################################################
class vtkInteractionHandler(NotCacheable, Module):
    """
    vtkInteractionHandler allow users to insert callback code for interacting
    with the vtkRenderWindowInteractor InteractionEvent
    
    """
    def compute(self):
        """ compute() -> None
        Actually compute nothing
        """        
        self.observer = self.getInputFromPort('Observer')
        self.handler = self.forceGetInputFromPort('Handler', '')
        self.shareddata = self.forceGetInputListFromPort('SharedData')
        if len(self.shareddata)==1:
            self.shareddata = self.shareddata[0]
        if self.observer:
            self.observer.vtkInstance.AddObserver('InteractionEvent',
                                                  self.interactionEvent)
            self.observer.vtkInstance.AddObserver('EndInteractionEvent',
                                                  self.endInteractionEvent)
            self.observer.vtkInstance.AddObserver('StartInteractionEvent',
                                                  self.startInteractionEvent)
            if hasattr(self.observer.vtkInstance, 'PlaceWidget'):
                self.observer.vtkInstance.PlaceWidget()

    def interactionEvent(self, obj, event):
        """ interactionEvent(obj: vtkObject, event: str) -> None
        Perform handler on interaction event
        
        """
        if self.handler!='':
            source = urllib.unquote(self.handler)
            exec(source + '\nif locals().has_key("interactionHandler"):\n' +
                 '\tinteractionHandler(obj, self.shareddata)')

    def startInteractionEvent(self, obj, event):
        """ startInteractionEvent(obj: vtkObject, event: str) -> None
        Perform handler on starting interaction event
        
        """
        if self.handler!='':
            source = urllib.unquote(self.handler)
            exec(source + '\nif locals().has_key("startInteractionHandler"):\n' +
                 '\tstartInteractionHandler(obj, self.shareddata)')

    def endInteractionEvent(self, obj, event):
        """ endInteractionEvent(obj: vtkObject, event: str) -> None
        Perform handler on ending interaction event
        
        """
        if self.handler!='':
            source = urllib.unquote(self.handler)
            exec(source + '\nif locals().has_key("endInteractionHandler"):\n' +
                 '\tendInteractionHandler(obj, self.shareddata)')

    def clear(self):
        """
        """
        self.observer.vtkInstance.RemoveObservers("InteractionEvent")
        self.observer.vtkInstance.RemoveObservers("StartInteractionEvent")
        self.observer.vtkInstance.RemoveObservers("EndInteractionEvent")
        Module.clear(self)

class HandlerConfigurationWidget(StandardModuleConfigurationWidget):
    """
    HandlerConfigurationWidget is simialr to PythonSource
    configuration widget except that it doesn't allow add/remove
    ports. In this configuration widget, the user will enter their
    python code to handle a specifc event
    
    """
    def __init__(self, module, controller, parent=None):
        """ HandlerConfigurationWidget(module: Module,
                                       controller: VistrailController,
                                       parent: QWidget)
                                       -> HandlerConfigurationWidget
        Setup the dialog to have a single python source editor and 2
        buttons
        
        """
        StandardModuleConfigurationWidget.__init__(self, module,
                                                   controller, parent)
        self.setWindowTitle('Handler Python Script Editor')
        self.setLayout(QtGui.QVBoxLayout())
        self.layout().setMargin(0)
        self.layout().setSpacing(0)
        self.createEditor()
        self.createButtonLayout()        
    
    def findHandlerFunction(self):
        """ findHandlerFunction() -> int
        Return the function id associated with input port 'source'
        
        """
        fid = -1
        for i in range(self.module.getNumFunctions()):
            if self.module.functions[i].name=='Handler':
                fid = i
                break
        return fid

    def createEditor(self):
        """ createEditor() -> None
        Add a python editor into the widget layout
        
        """
        self.codeEditor = PythonEditor(self)
        fid = self.findHandlerFunction()
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
            fid = self.findHandlerFunction()
            if fid==-1:
                fid = self.module.getNumFunctions()
            action = ChangeParameterAction()
            action.addParameter(self.module.id, fid, 0, 'Handler',
                                '<no description>',code,'String', '')
            controller.performAction(action)

    def okTriggered(self, checked = False):
        """ okTriggered(checked: bool) -> None
        Update vistrail controller (if neccesssary) then close the widget
        
        """
        self.updateController(self.controller)
        self.emit(QtCore.SIGNAL('doneConfigure()'))
        self.close()


def registerSelf():
    """ registerSelf() -> None
    Registry module with the registry
    """
    vIO = registry.getDescriptorByName('vtkInteractorObserver').module
    registry.addModule(vtkInteractionHandler, None, HandlerConfigurationWidget)
    registry.addInputPort(vtkInteractionHandler, 'Observer', vIO)
    registry.addInputPort(vtkInteractionHandler, 'Handler', String, True)
    registry.addInputPort(vtkInteractionHandler, 'SharedData', Module)
    registry.addOutputPort(vtkInteractionHandler, 'self',
                           vtkInteractionHandler)

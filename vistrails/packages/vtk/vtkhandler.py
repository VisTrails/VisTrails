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
"""Modules for handling vtkRenderWindowInteractor events"""
from PyQt4 import QtCore, QtGui
from core.modules.basic_modules import String
from core.modules.vistrails_module import Module, NotCacheable
from core.modules.module_registry import get_module_registry
from core.modules.module_configure import StandardModuleConfigurationWidget
from core.modules.python_source_configure import PythonEditor
from core.vistrail.module_function import ModuleFunction, ModuleParam
import urllib

################################################################################
class vtkInteractionHandler(NotCacheable, Module):
    """
    vtkInteractionHandler allow users to insert callback code for interacting
    with the vtkRenderWindowInteractor InteractionEvent
    
    """

    # Since vtkCommand is not wrapped in Python, we need to hardcoded all events
    # string from vtkCommand.h
    vtkEvents = [
        'AnyEvent',
        'DeleteEvent',
        'StartEvent',
        'EndEvent',
        'RenderEvent',
        'ProgressEvent',
        'PickEvent',
        'StartPickEvent',
        'EndPickEvent',
        'AbortCheckEvent',
        'ExitEvent',
        'LeftButtonPressEvent',
        'LeftButtonReleaseEvent',
        'MiddleButtonPressEvent',
        'MiddleButtonReleaseEvent',
        'RightButtonPressEvent',
        'RightButtonReleaseEvent',
        'EnterEvent',
        'LeaveEvent',
        'KeyPressEvent',
        'KeyReleaseEvent',
        'CharEvent',
        'ExposeEvent',
        'ConfigureEvent',
        'TimerEvent',
        'MouseMoveEvent',
        'MouseWheelForwardEvent',
        'MouseWheelBackwardEvent',
        'ResetCameraEvent',
        'ResetCameraClippingRangeEvent',
        'ModifiedEvent',
        'WindowLevelEvent',
        'StartWindowLevelEvent',
        'EndWindowLevelEvent',
        'ResetWindowLevelEvent',
        'SetOutputEvent',
        'ErrorEvent',
        'WarningEvent',
        'StartInteractionEvent',
        'InteractionEvent',
        'EndInteractionEvent',
        'EnableEvent',
        'DisableEvent',
        'CreateTimerEvent',
        'DestroyTimerEvent',
        'PlacePointEvent',
        'PlaceWidgetEvent',
        'CursorChangedEvent',
        'ExecuteInformationEvent',
        'RenderWindowMessageEvent',
        'WrongTagEvent',
        'StartAnimationCueEvent',
        'AnimationCueTickEvent',
        'EndAnimationCueEvent',
        'VolumeMapperRenderEndEvent',
        'VolumeMapperRenderProgressEvent',
        'VolumeMapperRenderStartEvent',
        'VolumeMapperComputeGradientsEndEvent',
        'VolumeMapperComputeGradientsProgressEvent',
        'VolumeMapperComputeGradientsStartEvent',
        'WidgetModifiedEvent',
        'WidgetValueChangedEvent',
        'WidgetActivateEvent',
        'ConnectionCreatedEvent',
        'ConnectionClosedEvent',
        'DomainModifiedEvent',
        'PropertyModifiedEvent',
        'UpdateEvent',
        'RegisterEvent',
        'UnRegisterEvent',
        'UpdateInformationEvent']
    
    def __init__(self):
        Module.__init__(self)
        self.observer = None
        self.handler = None
        self.shareddata = None

    def compute(self):
        """ compute() -> None
        Actually compute nothing
        """        
        self.observer = self.forceGetInputFromPort('Observer')
        self.handler = self.forceGetInputFromPort('Handler', '')
        self.shareddata = self.forceGetInputListFromPort('SharedData')
        if len(self.shareddata)==1:
            self.shareddata = self.shareddata[0]
        if self.observer:
            source = urllib.unquote(self.handler)
            observer = self.observer.vtkInstance
            for e in vtkInteractionHandler.vtkEvents:
                f = e[0].lower() + e[1:]
                f = f.replace('Event', 'Handler')
                source += ('\nif locals().has_key("%s"):\n' % f +
                           '\tobserver.AddObserver("%s", ' % e +
                           'self.eventHandler)\n')
            exec(source)
            if hasattr(self.observer.vtkInstance, 'PlaceWidget'):
                self.observer.vtkInstance.PlaceWidget()

    def eventHandler(self, obj, event):
        """ eventHandler(obj: vtkObject, event: str) -> None
        A proxy for all vtk events to direct to the correct calls
        
        """
        if self.handler!='':
            source = urllib.unquote(self.handler)
            f = event[0].lower() + event[1:]
            f = f.replace('Event', 'Handler')
            myGlobals = globals()
            myGlobals.update({'self':self})
            exec(source + ('\nif locals().has_key("%s"):\n' % f)+
                 ('\t%s(obj, self.shareddata)' % f)) in myGlobals, locals()

    def clear(self):
        """ clear() -> None
        Remove event handler so the object can be freed correctly
        
        """
        # Remove all observers
        if self.observer:
            for e in vtkInteractionHandler.vtkEvents:
                self.observer.vtkInstance.RemoveObservers(e)
        Module.clear(self)

    def repaintCells(self):
        """ repaintCells() -> None
        Redraw all cells on the current sheet
        
        """
        from packages.spreadsheet.spreadsheet_controller \
             import spreadsheetController
        from packages.spreadsheet.spreadsheet_event \
             import RepaintCurrentSheetEvent
        spreadsheetController.postEventToSpreadsheet(RepaintCurrentSheetEvent())

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
        for i in xrange(self.module.getNumFunctions()):
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
        if self.codeEditor.__class__.__name__ != '_PythonEditor':
            self.codeEditor.document().setModified(False)
        else:
            self.codeEditor.setModified(False)
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
            functions = [('Handler', [code])]
            self.controller.update_functions(self.module, functions)

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
    registry = get_module_registry()
    vIO = registry.get_descriptor_by_name(
        'edu.utah.sci.vistrails.vtk',
        'vtkInteractorObserver').module
    registry.add_module(vtkInteractionHandler, configureWidgetType=HandlerConfigurationWidget)
    registry.add_input_port(vtkInteractionHandler, 'Observer', vIO)
    registry.add_input_port(vtkInteractionHandler, 'Handler', String, True)
    registry.add_input_port(vtkInteractionHandler, 'SharedData', Module)
    registry.add_output_port(vtkInteractionHandler, 'self',
                             vtkInteractionHandler)

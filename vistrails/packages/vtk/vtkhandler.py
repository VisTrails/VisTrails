###############################################################################
##
## Copyright (C) 2014-2016, New York University.
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
##  - Neither the name of the New York University nor the names of its
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
from __future__ import division

from vistrails.core.modules.vistrails_module import Module, NotCacheable
from vistrails.gui.modules.source_configure import SourceConfigurationWidget
from vistrails.gui.modules.python_source_configure import PythonEditor
import urllib

################################################################################
class HandlerConfigurationWidget(SourceConfigurationWidget):
    def __init__(self, module, controller, parent=None):
        """ HandlerConfigurationWidget(module: Module,
                                       controller: VistrailController,
                                       parent: QWidget)
                                       -> HandlerConfigurationWidget
        Setup the dialog to similar to PythonSource but with a
        different name

        """
        SourceConfigurationWidget.__init__(self, module, controller,
                                           PythonEditor, False, False, parent,
                                           portName='Handler')



class vtkInteractionHandler(NotCacheable, Module):
    """
    vtkInteractionHandler allow users to insert callback code for interacting
    with the vtkRenderWindowInteractor InteractionEvent
    
    """

    _settings={'configureWidgetType': HandlerConfigurationWidget}

    _input_ports = [('Observer', 'vtkInteractorObserver'),
                    ('Handler', 'basic:String', True),
                    ('SharedData', 'basic:Variant')]

    _output_ports =[('Instance', 'vtkInteractionHandler')]

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
        self.observer = self.force_get_input('Observer')
        self.handler = self.force_get_input('Handler', '')
        self.shareddata = self.force_get_input_list('SharedData')
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
        self.set_output('Instance', self)

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
        from vistrails.packages.spreadsheet.spreadsheet_controller \
             import spreadsheetController
        from vistrails.packages.spreadsheet.spreadsheet_event \
             import RepaintCurrentSheetEvent
        spreadsheetController.postEventToSpreadsheet(RepaintCurrentSheetEvent())


_modules = [vtkInteractionHandler]

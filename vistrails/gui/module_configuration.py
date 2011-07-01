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
""" This file describe the module configuration box that is displayed when
the user selects a module's "Edit Configuration"

"""
from PyQt4 import QtCore, QtGui
from core.modules.module_registry import get_module_registry
from core.modules.module_configure import DefaultModuleConfigurationWidget
from gui.common_widgets import QToolWindowInterface

################################################################################

class QConfigurationWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setLayout(QtGui.QVBoxLayout())
        self.widget = None
        #self.setFocusPolicy(QtCore.Qt.StrongFocus)
        
    def setUpWidget(self, widget):
        self.widget = widget
        self.layout().addWidget(self.widget)
        
    def clear(self):
        """ clear() -> None
        Clear and delete widget in the layout
        
        """
        if self.widget:
            self.widget.setVisible(False)
            self.layout().removeWidget(self.widget)
            self.widget.deleteLater()
        self.widget = None
        
    def askToSaveChanges(self):
        if self.widget:
            return self.widget.askToSaveChanges()
        
    def activate(self):
        if self.widget:
            self.widget.activate()
            
################################################################################
        
class QModuleConfiguration(QtGui.QScrollArea, QToolWindowInterface):
    def __init__(self, parent=None, scene=None):
        """QModuleConfiguration(parent: QWidget) -> QModuleConfiguration
        Initialize widget constraints
        
        """
        QtGui.QScrollArea.__init__(self, parent)
        self.setWindowTitle('Module Configuration')
        self.setWidgetResizable(True)
        self.confWidget = QConfigurationWidget()
        self.setWidget(self.confWidget)
        self.module = None
        self.controller = None
        self.scene = scene
        self.updateLocked = False
        self.hasChanges = False
        
    def updateModule(self, module):
        if self.updateLocked: return
        self.module = module
        self.confWidget.setUpdatesEnabled(False)    
        self.confWidget.setVisible(False)
        self.confWidget.clear()
        if module and self.controller:
            if module.has_annotation_with_key('__desc__'):
                label = module.get_annotation_by_key('__desc__').value.strip()
                title = '%s (%s) Module Configuration'%(label,
                                                        module.name)
            else:
                title = '%s Module Configuration'%module.name
            self.setWindowTitle(title)
            registry = get_module_registry()
            getter = registry.get_configuration_widget
            widgetType = getter(module.package, module.name, module.namespace)
            if not widgetType:
                widgetType = DefaultModuleConfigurationWidget
            widget = widgetType(module, self.controller)
            self.scene.modules[module.id]._old_connection_ids = \
              self.scene.modules[module.id].dependingConnectionItems()
        
            self.confWidget.setUpWidget(widget)
            self.connect(widget, QtCore.SIGNAL("doneConfigure"),
                         self.configureDone)
            self.connect(widget, QtCore.SIGNAL("stateChanged"),
                         self.stateChanged)
        else:
            self.setWindowTitle("Module Configuration")
        self.confWidget.setUpdatesEnabled(True)
        self.confWidget.setVisible(True)
        self.hasChanges = False
    
    def configureDone(self):
        self.emit(QtCore.SIGNAL('doneConfigure'), self.module.id)  
        
    def stateChanged(self):
        # self.setWindowModified seems not to work here
        # self.setWindowModified(self.confWidget.widget.state_changed)
        title = str(self.windowTitle())
        self.hasChanges = self.confWidget.widget.state_changed
        if self.hasChanges:
            if not title.endswith("*"):
                self.setWindowTitle(title + "*")
        else:
            if title.endswith("*"):
                self.setWindowTitle(title[:-1])
        
    def lockUpdate(self):
        """ lockUpdate() -> None
        Do not allow updateModule()
        
        """
        self.updateLocked = True
        
    def unlockUpdate(self):
        """ unlockUpdate() -> None
        Allow updateModule()
        
        """
        self.updateLocked = False
        
    def closeEvent(self, event):
        self.confWidget.askToSaveChanges()
        event.accept()
        
    def activate(self):
        if self.isVisible() == False:
            self.toolWindow().show()
        self.activateWindow()
        self.confWidget.activate()
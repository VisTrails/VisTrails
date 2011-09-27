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
from gui.common_widgets import QToolWindowInterface

class QVistrailsPaletteInterface(QToolWindowInterface):
    def __init__(self):
        QToolWindowInterface.__init__(self)
        self.controller = None
        self.title = None
        self.p_id = None
        self.main_window = None
 
    @classmethod
    def instance(klass):
        if not hasattr(klass, '_instance'):
            klass._instance = klass()
        return klass._instance

    def toolWindow(self):
        tool_window = QToolWindowInterface.toolWindow(self)
        return tool_window

    def set_id(self, p_id):
        self.p_id = p_id

    def get_id(self):
        return self.p_id

    def set_title(self, title):
        self.setWindowTitle(title)

    def get_title(self):
        return str(self.windowTitle())

    def set_action(self, action):
        self.action = action
        self.connect(self.toolWindow(), 
                     QtCore.SIGNAL("visibilityChanged(bool)"),
                     self.visibility_changed)

    def get_action(self):
        return self.action
        # return self.toolWindow().toggleViewAction()

    def get_action_tuple(self):
        return (self.get_title(), self.get_title(), 
                {'checkable': True, 
                 'checked': self.toolWindow().isVisible(),
                 'callback': self.set_visible})

    def set_main_window(self, mw):
        self.main_window = mw

    def set_visible(self, enabled):
        #print "set_visible ", self, enabled
        if hasattr(self, 'main_window') and self.main_window is not None:
            self.main_window.show()
            self.main_window.raise_()

        if enabled:
            self.toolWindow().show()
            self.toolWindow().raise_()
            
    def set_pin_status(self, pin_status):
        self.toolWindow().setPinStatus(pin_status)
    
    def get_pin_status(self):
        return self.toolWindow().pinStatus
    
    def set_controller(self, controller):
        self.controller = controller

    def get_controller(self):
        return self.controller

    def set_module(self, module):
        self.module = module
        
    def get_module(self):
        return self.module

    def set_descriptor(self, descriptor):
        self.descriptor = descriptor

    def get_descriptor(self):
        return self.descriptor

    def visibility_changed(self, visible):
        self.action.setChecked(visible)

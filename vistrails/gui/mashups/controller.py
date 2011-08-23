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
from PyQt4.QtCore import QObject, pyqtSignal, pyqtSlot

from core.mashup.controller import MashupController as BaseController
from core.mashup.alias import Alias
from gui.utils import show_warning

class MashupController(BaseController, QObject):
    #signals
    stateChanged = pyqtSignal()
    versionChanged = pyqtSignal(int)
    
    def __init__(self, originalController, vt_controller, vt_version, mshptrail=None):
        QObject.__init__(self)
        BaseController.__init__(self, originalController, vt_controller, vt_version, mshptrail)
        self.name = ''
        self.currentMashupView = None
        
    def setChanged(self, on):
        BaseController.setChanged(self, on)
        self.stateChanged.emit()
        
    def setCurrentVersion(self, version, quiet=True):
        BaseController.setCurrentVersion(self, version)
        if not quiet:
            self.stateChanged.emit()
            self.versionChanged.emit(version)
            
    def updateCurrentTag(self, name):
        if BaseController.updateCurrentTag(self, name) == False:
            show_warning('Name Exists',
                         "There is already another version named '%s'.\n"
                         "Please enter a different one." % name)
            return False
        else:
            return True
        
    @pyqtSlot(str)
    def removeAlias(self, name):
        BaseController.removeAlias(self, name)
    
    @pyqtSlot(Alias)
    def updateAlias(self, alias):
        BaseController.updateAlias(self, alias)
        
    def moveTag(self, from_version, to_version, name):
        BaseController.moveTag(self, from_version, to_version, name)
        self.stateChanged.emit()
        
    def execute(self, params):
        from gui.vistrails_window import _app
        result = BaseController.execute(self, params)
        _app.notify('execution_updated')
        return result
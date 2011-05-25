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
from PyQt4.QtCore import QObject, pyqtSignal, pyqtSlot

from core.mashup.controller import MashupController as BaseController
from core.mashup.alias import Alias

class MashupController(BaseController, QObject):
    #signals
    stateChanged = pyqtSignal()
    versionChanged = pyqtSignal(int)
    
    def __init__(self, vt_controller, vt_version, mshptrail=None):
        QObject.__init__(self)
        BaseController.__init__(self, vt_controller, vt_version, mshptrail)
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
        
    @pyqtSlot(str)
    def removeAlias(self, name):
        BaseController.removeAlias(self, name)
    
    @pyqtSlot(Alias)
    def updateAlias(self, alias):
        BaseController.updateAlias(self, alias)
        
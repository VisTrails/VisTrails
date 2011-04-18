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

from PyQt4 import QtCore, QtGui
from gui.common_widgets import QToolWindowInterface

class QVistrailsPaletteInterface(QToolWindowInterface):
    def __init__(self):
        QToolWindowInterface.__init__(self)
        self.controller = None

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


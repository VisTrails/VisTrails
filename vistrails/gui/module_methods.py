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
""" This file describe the module methods box that user can drop
methods from method palette into it

"""
from PyQt4 import QtCore, QtGui
from gui.method_dropbox import QMethodDropBox
from gui.common_widgets import QToolWindowInterface

################################################################################

class QModuleMethods(QMethodDropBox, QToolWindowInterface):
    """
    QModuleMethods is showing methods of a single module, it also
    support drop actions of method items from the method palette
    
    """
    def __init__(self, parent=None):
        """ QModuleMethods(parent: QWidget) -> QModuleMethods
        Initialize widget constraints
        
        """
        QMethodDropBox.__init__(self, parent)
        self.setWindowTitle('Set Methods')

    def sizeHint(self):
        """ sizeHint() -> None
        """
        return QtCore.QSize(self.size().width(), 300)

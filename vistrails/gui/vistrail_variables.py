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
""" This file describes the vistrail variables box into which the user can
drop constants from the module palette

"""
from PyQt4 import QtCore, QtGui
from gui.variable_dropbox import QVariableDropBox
from gui.common_widgets import QToolWindowInterface
from gui.vistrails_palette import QVistrailsPaletteInterface

################################################################################

class QVistrailVariables(QVariableDropBox, QVistrailsPaletteInterface):
    """
    QVistrailVariables shows variables associated with a vistrail, and
    supports drag/drop actions of constant items from the module palette
    
    """
    def __init__(self, parent=None):
        """ QVistrailVariables(parent: QWidget) -> QVistrailVariables
        Initialize widget constraints
        
        """
        QVariableDropBox.__init__(self, parent)
        self.setWindowTitle('Vistrail Variables')

    def sizeHint(self):
        """ sizeHint() -> None
        """
        return QtCore.QSize(self.size().width(), 300)


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

from common_widgets import QToolWindowInterface

class PaletteContainer(QtGui.QTabWidget, QToolWindowInterface):
    def __init__(self, parent=None):
        QtGui.QTabWidget.__init__(self, parent)
        self.setDocumentMode(True)
        self.setTabPosition(QtGui.QTabWidget.North)
        self.palettes = {}

    def add_palette(self, palette):
        # palette.setContentsMargins(0,5,0,0)
        self.addTab(palette, palette.windowTitle())
        self.palettes[palette.__class__] = palette
        if len(self.palettes) <= 1:
            self.tabBar().hide()
        else:
            self.tabBar().show()

    def set_top_widget(self, klass):
        self.setCurrentWidget(self.palettes[klass])

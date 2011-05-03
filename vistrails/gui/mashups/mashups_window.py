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
from gui.mashups.alias_list import QAliasListPanel
from gui.mashups.mashup_view import QMashupView

class QMashupsWindow(QtGui.QMainWindow):
    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
        QtGui.QMainWindow.__init__(self, parent, f)
        self.windows = []
        self.windows_map = {}
        self.currentWindow = None
        self.aliasPanel = QAliasListPanel(parent=self)
        self.aliasPanel.toolWindow().setFloating(True)
        self.connect(self.aliasPanel, QtCore.SIGNAL("update_alias"),
                     self.updatePreview)
        self.setWindowTitle("Mashup")
        self.createActions()
        self.createMenu()
        
    def createWindow(self, controller):
        """ createWindow() -> None
        Create a pipeline tab and append it to the list of windows

        """
        window = QMashupView(controller, self)
        self.windows.append(window)
        self.windows_map[controller] = window
        return window
        
    def createActions(self):
        """ createActions() -> None
        Construct all menu actions for mashup window

        """
        pass
    
    def createMenu(self):
        """ createMenu() -> None
        Initialize menu bar of Mashup window

        """
        self.viewMenu = self.menuBar().addMenu('&View')
        self.viewMenu.addAction(self.aliasPanel.toolWindow().toggleViewAction())
        
    def updateController(self, mshpController):
        if mshpController not in self.windows_map.keys():
            window = self.createWindow(mshpController)
        else:
            window = self.windows_map[mshpController]
        self.aliasPanel.updateController(mshpController)
        window.show()
            
    def updatePreview(self, info):
        mshpController = info[0]
        if mshpController in self.windows_map.keys():
            window = self.windows_map[mshpController]
            window.updatePreviewTab(info)
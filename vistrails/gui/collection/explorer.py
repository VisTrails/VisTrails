###########################################################################
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

import glob
import os
from datetime import datetime
from time import strptime
from core import debug
from core.thumbnails import ThumbnailCache
from core.collection import Collection
from core.collection.search import SearchCompiler, SearchParseError
from core.db.locator import FileLocator
from gui.common_widgets import QToolWindowInterface, QToolWindow, QSearchBox
from gui.theme import CurrentTheme

class QExplorerWindow(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.splitter = QtGui.QSplitter(self)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.queryWidget = QtGui.QLabel('Here we will have search operations', parent)
        self.splitter.addWidget(self.queryWidget)
        self.hSplitter = QtGui.QSplitter(self)
        self.sourceView = QtGui.QTreeWidget(parent)
        item = QtGui.QTreeWidgetItem(['Workspaces'])
        self.sourceView.addTopLevelItem(item)
        item2 = QtGui.QTreeWidgetItem(['Default'])
        item.addChild(item2)
        item = QtGui.QTreeWidgetItem(['Directories'])
        self.sourceView.addTopLevelItem(item)
        item = QtGui.QTreeWidgetItem(['Databases'])
        self.sourceView.addTopLevelItem(item)

        self.hSplitter.addWidget(self.sourceView)
        self.itemView = QtGui.QTreeWidget(parent)
        self.hSplitter.addWidget(self.itemView)
        self.splitter.addWidget(self.hSplitter)
        self.layout = QtGui.QVBoxLayout()
        self.layout.addWidget(self.splitter)
        self.setLayout(self.layout)
        self.setWindowTitle('Vistrail Explorer')
        self.resize(QtCore.QSize(800, 600))
        
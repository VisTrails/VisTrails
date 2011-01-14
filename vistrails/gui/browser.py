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
""" The file describes the browser widget used to browse
    collections of vistrails
"""

from PyQt4 import QtCore, QtGui
from gui.collection.browser import QBrowserWidget
from gui.common_widgets import QToolWindowInterface, QToolWindow, QSearchBox
from core.collection import Collection
from core.collection.search import SearchCompiler, SearchParseError

class QBrowserDialog(QToolWindow, QToolWindowInterface):
    def __init__(self, parent=None):
        QToolWindow.__init__(self, parent=parent)

        self.widget = QtGui.QWidget(self)
        self.setWidget(self.widget)
        self.setTitleBarWidget(QtGui.QLabel("Recently used files"))

        layout = QtGui.QVBoxLayout()
#        layout.setMargin(0)
#        layout.setSpacing(5)
        self.search_box = QSearchBox(True, False, self)
        layout.addWidget(self.search_box)

        self.collection = Collection.getInstance()
        self.browser = QBrowserWidget(self.collection)
       
        layout.addWidget(self.browser)
        self.browser.setup_widget()
        self.connect(self.search_box, QtCore.SIGNAL('resetSearch()'),
                     self.reset_search)
        self.connect(self.search_box, QtCore.SIGNAL('executeSearch(QString)'),
                     self.execute_search)
        self.connect(self.search_box, QtCore.SIGNAL('refineMode(bool)'),
                     self.refine_mode)
        self.widget.setLayout(layout)
        import api
        api.b = self
 
    def reset_search(self):
        self.browser.reset_search()

    def set_results(self, results):
        pass

    def execute_search(self, text):
        s = str(text)
        try:
            search = SearchCompiler(s).searchStmt
        except SearchParseError, e:
            debug.warning("Search Parse Error", str(e))
            search = None

        self.browser.run_search(search)

    def refine_mode(self, on):
        pass

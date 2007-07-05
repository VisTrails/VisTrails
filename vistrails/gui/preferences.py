############################################################################
##
## Copyright (C) 2006-2007 University of Utah. All rights reserved.
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

from PyQt4 import QtGui, QtCore
from gui.common_widgets import QSearchTreeWindow, QSearchTreeWidget
from core.configuration import ConfigurationObject

##############################################################################

class QConfigurationTreeWidgetItem(QtGui.QTreeWidgetItem):

    def __init__(self, parent, obj, name):
        lst = QtCore.QStringList(name)
        t = type(obj)
        self._obj_type = t
        if t == ConfigurationObject:
            lst << '' << ''
            QtGui.QTreeWidgetItem.__init__(self, parent, lst)
            self.setFlags(self.flags() & ~(QtCore.Qt.ItemIsDragEnabled |
                                           QtCore.Qt.ItemIsSelectable |
                                           QtCore.Qt.ItemIsEnabled))
        elif t == tuple and obj[0] is None and type(obj[1]) == type:
            self._obj_type = obj[1]
            lst << '' << obj[1].__name__
            QtGui.QTreeWidget.__init__(self, parent, lst)
            self.setFlags(self.flags() & ~QtCore.Qt.ItemIsDragEnabled)
        else:
            lst << str(obj) << type(obj).__name__
            QtGui.QTreeWidgetItem.__init__(self, parent, lst)
            self.setFlags(self.flags() & ~QtCore.Qt.ItemIsDragEnabled)

class QConfigurationTreeWidget(QSearchTreeWidget):

    def __init__(self, parent):
        QSearchTreeWidget.__init__(self, parent)
        self.setColumnCount(3)
        lst = QtCore.QStringList()
        lst << 'Name'
        lst << 'Value'
        lst << 'Type'
        self.setHeaderLabels(lst)
        self.create_tree()

    def create_tree(self):
        def create_item(parent, obj, name):
            item = QConfigurationTreeWidgetItem(parent, obj, name)
            if type(obj) == ConfigurationObject:
                for key in obj.keys():
                    create_item(item, getattr(obj, key), key)
        from gui.application import VistrailsApplication
        c = VistrailsApplication.vistrailsStartup.configuration
        create_item(self, c, 'configuration')
        

class QConfigurationTreeWindow(QSearchTreeWindow):

    def createTreeWidget(self):
        self.setWindowTitle('Configuration')
        return QConfigurationTreeWidget(self)


class QPreferencesDialog(QtGui.QDialog):

    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
#         self._tab_widget = QtGui.QTabWidget(self)
        
        self._configuration_tab = self.create_configuration_tab()
#         self._tab_widget.addTab(self._configuration_tab, 'configuration')

#         self._packages_tab = QtGui.QFrame(self)
#         self._tab_widget.addTab(self._packages_tab, 'packages')

    def create_configuration_tab(self):
        self._tree_widget = QConfigurationTreeWindow(self)
#         return self.
        
        

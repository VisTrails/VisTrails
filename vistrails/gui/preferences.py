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
from gui.configuration import QConfigurationWidget
from core.packagemanager import get_package_manager
import os.path

##############################################################################

class QPackagesWidget(QtGui.QWidget):

    ##########################################################################
    # Initalization

    def __init__(self, parent, status_bar):
        QtGui.QWidget.__init__(self, parent)
        self._status_bar = status_bar

        base_layout = QtGui.QHBoxLayout(self)
        
        left = QtGui.QFrame(self)
        right = QtGui.QFrame(self)

        base_layout.addWidget(left)
        base_layout.addWidget(right, 1)
        
        ######################################################################
        left_layout = QtGui.QVBoxLayout(left)
        left_layout.setMargin(2)
        left_layout.setSpacing(2)
       
        left_layout.addWidget(QtGui.QLabel("Disabled packages:", left))
        self._available_packages_list = QtGui.QListWidget(left)
        left_layout.addWidget(self._available_packages_list)
        left_layout.addWidget(QtGui.QLabel("Enabled packages:", left))
        self._enabled_packages_list = QtGui.QListWidget(left)
        left_layout.addWidget(self._enabled_packages_list)

        self.connect(self._available_packages_list,
                     QtCore.SIGNAL('itemClicked(QListWidgetItem*)'),
                     self.clicked_on_available_list)

        self.connect(self._enabled_packages_list,
                     QtCore.SIGNAL('itemClicked(QListWidgetItem*)'),
                     self.clicked_on_enabled_list)

        sm = QtGui.QAbstractItemView.SingleSelection
        self._available_packages_list.setSelectionMode(sm)
        self._enabled_packages_list.setSelectionMode(sm)


        ######################################################################
        right_layout = QtGui.QVBoxLayout(right)
        info_frame = QtGui.QFrame(right)

        info_layout = QtGui.QVBoxLayout(info_frame)
        grid_frame = QtGui.QFrame(info_frame)
        grid_frame.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                 QtGui.QSizePolicy.Expanding)

        info_layout.addWidget(grid_frame)
        grid_layout = QtGui.QGridLayout(grid_frame)
        l1 = QtGui.QLabel("Package Name:", grid_frame)
        grid_layout.addWidget(l1, 0, 0)
        l2 = QtGui.QLabel("Dependencies:", grid_frame)
        grid_layout.addWidget(l2, 1, 0)
        l3 = QtGui.QLabel("Description:", grid_frame)
        grid_layout.addWidget(l3, 2, 0)

        self._name_label = QtGui.QLabel("", grid_frame)
        grid_layout.addWidget(self._name_label, 0, 1)

        self._dependencies_label = QtGui.QLabel("", grid_frame)
        grid_layout.addWidget(self._dependencies_label, 1, 1)

        self._description_label = QtGui.QLabel("", grid_frame)
        grid_layout.addWidget(self._description_label, 2, 1)

        for lbl in [l1, l2, l3, self._name_label, self._dependencies_label,
                    self._description_label]:
            lbl.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
            lbl.setWordWrap(True)

        grid_layout.setRowStretch(2, 1)
        grid_layout.setColumnStretch(1, 1)

        right_layout.addWidget(info_frame)
        
        self._enable_button = QtGui.QPushButton("Enable...")
        self.connect(self._enable_button,
                     QtCore.SIGNAL("clicked()"),
                     self.enable_current_package)
        self._disable_button = QtGui.QPushButton("Disable...")
        self._configure_button = QtGui.QPushButton("Configure...")
        button_box = QtGui.QDialogButtonBox()
        button_box.addButton(self._enable_button, QtGui.QDialogButtonBox.ActionRole)
        button_box.addButton(self._disable_button, QtGui.QDialogButtonBox.ActionRole)
        button_box.addButton(self._configure_button, QtGui.QDialogButtonBox.ActionRole)
        right_layout.addWidget(button_box)
        
        self.populate_lists()

        self._current_package = None

    def populate_lists(self):
        pkg_manager = get_package_manager()
        enabled_pkgs = sorted(pkg_manager.enabled_package_list())
        enabled_pkg_dict = dict([(pkg.name, pkg) for
                                   pkg in enabled_pkgs])
        for pkg in enabled_pkgs:
            self._enabled_packages_list.addItem(pkg.name)
        available_pkg_names = [pkg for pkg in 
                               sorted(pkg_manager.available_package_names_list())
                               if pkg not in enabled_pkg_dict]
        for pkg in available_pkg_names:
            self._available_packages_list.addItem(pkg)

    ##########################################################################

    def enable_current_package(self):
        av = self._available_packages_list
        inst = self._enabled_packages_list
        item = av.currentItem()
        pos = av.indexFromItem(item).row()
        name = str(item.text())
        pm = get_package_manager()

        dependency_graph = pm.dependency_graph()
        new_deps = self._current_package.dependencies()

        unmet_dep = None

        for dep in new_deps:
            if dep not in dependency_graph.vertices:
                unmet_dep = dep
                break
        if unmet_dep:
            msg = QtGui.QMessageBox(QtGui.QMessageBox.Critical,
                                    "Missing dependency",
                                    ("This package requires package '%s'\n" +
                                     "to be enabled. (Complete dependency list is:\n" +
                                     "%s)") % (dep, new_deps),
                                    QtGui.QMessageBox.Ok, self)
            msg.exec_()
        else:
            pm.late_enable_package(name)
            self._current_package = pm.get_package(name)
            av.takeItem(pos)
            av.setCurrentRow(-1)
            inst.addItem(item)
            inst.sortItems()
            inst.setCurrentItem(item)

    def disable_current_package(self):
        av = self._available_packages_list
        inst = self._enabled_packages_list
        item = av.currentItem()
        pos = inst.indexFromItem(item).row()
        name = str(item.text())
        pm = get_package_manager()

        dependency_graph = pm.dependency_graph()

        if dependency_graph.in_degree(name) > 0:
            rev_deps = dependency_graph.inverse_adjacency_list[name]
            msg = QtGui.QMessageBox(QtGui.QMessageBox.Critical,
                                    "Missing dependency",
                                    ("There are other packages that depend on this:\n %s" +
                                     "Please disable those first.") % rev_deps,
                                    QtGui.QMessageBox.Ok, self)
            msg.exec_()
        else:
            pm.remove_package(name)
            inst.takeItem(pos)
            av.addItem(item)
            av.sortItems()

    def set_buttons_to_enabled_package(self):
        self._enable_button.setEnabled(False)
        self._disable_button.setEnabled(True)
        assert self._current_package
        conf = not (self._current_package.configuration is None)
        self._configure_button.setEnabled(conf)

    def set_buttons_to_available_package(self):
        self._configure_button.setEnabled(False)
        self._disable_button.setEnabled(False)
        self._enable_button.setEnabled(True)

    def set_package_information(self):
        assert self._current_package
        p = self._current_package
        self._name_label.setText(p.name)
        deps = ', '.join(p.dependencies()) or 'No package dependencies.'
        self._dependencies_label.setText(deps)
        self._description_label.setText(' '.join(p.description.split('\n')))
        

    ##########################################################################
    # Signal handling

    def clicked_on_enabled_list(self, item):
        name = str(item.text())
        self._current_package = get_package_manager().get_package(name)
        self._available_packages_list.setCurrentItem(None)
        self.set_buttons_to_enabled_package()
        self.set_package_information()

    def clicked_on_available_list(self, item):
        name = str(item.text())
        self._current_package = get_package_manager().look_at_available_package(name)
        self._enabled_packages_list.setCurrentItem(None)
        self.set_buttons_to_available_package()
        self.set_package_information()



class QPreferencesDialog(QtGui.QDialog):

    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self._status_bar = QtGui.QStatusBar(self)
        self.setWindowTitle('VisTrails Preferences')
        layout = QtGui.QHBoxLayout(self)
        layout.setMargin(0)
        layout.setSpacing(0)
        self.setLayout(layout)

        f = QtGui.QFrame()
        layout.addWidget(f)
        
        l = QtGui.QVBoxLayout(f)
        f.setLayout(l)
        
        self._tab_widget = QtGui.QTabWidget(f)
        l.addWidget(self._tab_widget)
        self._tab_widget.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                       QtGui.QSizePolicy.Expanding)

        self._packages_tab = self.create_packages_tab()
        self._tab_widget.addTab(self._packages_tab, 'Module Packages')
        
        self._configuration_tab = self.create_configuration_tab()
        self._tab_widget.addTab(self._configuration_tab, 'General Configuration')

        self._button_box = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Close,
                                                  QtCore.Qt.Horizontal,
                                                  f)
        l.addWidget(self._button_box)
        l.addWidget(self._status_bar)


    def create_configuration_tab(self):
        return QConfigurationWidget(self, self._status_bar)

    def create_packages_tab(self):
        return QPackagesWidget(self, self._status_bar)

    def sizeHint(self):
        return QtCore.QSize(800, 600)

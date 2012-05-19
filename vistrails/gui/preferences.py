###############################################################################
##
## Copyright (C) 2006-2011, University of Utah. 
## All rights reserved.
## Contact: contact@vistrails.org
##
## This file is part of VisTrails.
##
## "Redistribution and use in source and binary forms, with or without 
## modification, are permitted provided that the following conditions are met:
##
##  - Redistributions of source code must retain the above copyright notice, 
##    this list of conditions and the following disclaimer.
##  - Redistributions in binary form must reproduce the above copyright 
##    notice, this list of conditions and the following disclaimer in the 
##    documentation and/or other materials provided with the distribution.
##  - Neither the name of the University of Utah nor the names of its 
##    contributors may be used to endorse or promote products derived from 
##    this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
## AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
## THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR 
## PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR 
## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; 
## OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
## WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR 
## OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF 
## ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
###############################################################################

from PyQt4 import QtGui, QtCore
from core import get_vistrails_application
from core.packagemanager import get_package_manager
from core.utils import InvalidPipeline
from core.utils.uxml import (named_elements,
                             elements_filter, enter_named_element)
from gui.configuration import (QConfigurationWidget, QGeneralConfiguration,
                               QThumbnailConfiguration)
from gui.module_palette import QModulePalette
from gui.pipeline_view import QPipelineView
from core.configuration import get_vistrails_persistent_configuration, \
    get_vistrails_configuration
from core import debug
import os.path

##############################################################################

class QPackageConfigurationDialog(QtGui.QDialog):

    def __init__(self, parent, package):
        QtGui.QDialog.__init__(self, parent)

        self.setSizePolicy(QtGui.QSizePolicy.Expanding,
                           QtGui.QSizePolicy.Expanding)

        
        self.setWindowTitle('Configuration for package "%s"' % package.name)
        self._package = package
        c = package.configuration
        self._configuration_object = c
        assert c is not None

        layout = QtGui.QVBoxLayout(self)
        self.setLayout(layout)
        self._status_bar = QtGui.QStatusBar(self)

        self._configuration_widget = QConfigurationWidget(self, c, c,
                                                          self._status_bar)
        layout.addWidget(self._configuration_widget)

        btns = (QtGui.QDialogButtonBox.Close |
                QtGui.QDialogButtonBox.RestoreDefaults)
        self._button_box = QtGui.QDialogButtonBox(btns,
                                                  QtCore.Qt.Horizontal,
                                                  self)
        self.connect(self._button_box,
                     QtCore.SIGNAL('clicked(QAbstractButton *)'),
                     self.button_clicked)

        self.connect(self._configuration_widget._tree.treeWidget,
                     QtCore.SIGNAL('configuration_changed'),
                     self.configuration_changed)
                     
        layout.addWidget(self._status_bar)
        layout.addWidget(self._button_box)

    def button_clicked(self, button):
        role = self._button_box.buttonRole(button)
        if role == QtGui.QDialogButtonBox.ResetRole:
            txt = ("This will reset all configuration values of " +
                   "this package to their default values. Do you " +
                   "want to proceed?")
            msg_box = QtGui.QMessageBox(QtGui.QMessageBox.Question,
                                        "Really reset?", txt,
                                        (QtGui.QMessageBox.Yes |
                                         QtGui.QMessageBox.No))
            if msg_box.exec_() == QtGui.QMessageBox.Yes:
                self.reset_configuration()
        else:
            assert role == QtGui.QDialogButtonBox.RejectRole
            self.close_dialog()

    def reset_configuration(self):
        self._package.reset_configuration()
        conf = self._package.configuration
        self._configuration_widget.configuration_changed(conf)

    def close_dialog(self):
        self.done(0)

    def configuration_changed(self, item, new_value):
        self._package.set_persistent_configuration()

##############################################################################

class QPackagesWidget(QtGui.QWidget):

    # Signals that a package should be selected after the event loop updates (to remove old references)
    select_package_after_update_signal = QtCore.SIGNAL("select_package_after_update_signal")

    ##########################################################################
    # Initialization

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
                     QtCore.SIGNAL('itemSelectionChanged()'),
                     self.selected_available_list,
                     QtCore.Qt.QueuedConnection)

        self.connect(self._enabled_packages_list,
                     QtCore.SIGNAL('itemSelectionChanged()'),
                     self.selected_enabled_list,
                     QtCore.Qt.QueuedConnection)

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
        l2 = QtGui.QLabel("Identifier:", grid_frame)
        grid_layout.addWidget(l2, 1, 0)
        l3 = QtGui.QLabel("Version:", grid_frame)
        grid_layout.addWidget(l3, 2, 0)
        l4 = QtGui.QLabel("Dependencies:", grid_frame)
        grid_layout.addWidget(l4, 3, 0)
        l5 = QtGui.QLabel("Reverse Dependencies:", grid_frame)
        grid_layout.addWidget(l5, 4, 0)
        l6 = QtGui.QLabel("Description:", grid_frame)
        grid_layout.addWidget(l6, 5, 0)

        self._name_label = QtGui.QLabel("", grid_frame)
        grid_layout.addWidget(self._name_label, 0, 1)

        self._identifier_label = QtGui.QLabel("", grid_frame)
        grid_layout.addWidget(self._identifier_label, 1, 1)

        self._version_label = QtGui.QLabel("", grid_frame)
        grid_layout.addWidget(self._version_label, 2, 1)

        self._dependencies_label = QtGui.QLabel("", grid_frame)
        grid_layout.addWidget(self._dependencies_label, 3, 1)

        self._reverse_dependencies_label = QtGui.QLabel("", grid_frame)
        grid_layout.addWidget(self._reverse_dependencies_label, 4, 1)

        self._description_label = QtGui.QLabel("", grid_frame)
        grid_layout.addWidget(self._description_label, 5, 1)

        for lbl in [l1, l2, l3, l4, l5, l6,
                    self._name_label,
                    self._version_label,
                    self._dependencies_label,
                    self._identifier_label,
                    self._reverse_dependencies_label,
                    self._description_label]:
            lbl.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
            lbl.setWordWrap(True)

        grid_layout.setRowStretch(4, 1)
        grid_layout.setColumnStretch(1, 1)

        right_layout.addWidget(info_frame)
        
        self._enable_button = QtGui.QPushButton("&Enable")
        self._enable_button.setEnabled(False)
        self.connect(self._enable_button,
                     QtCore.SIGNAL("clicked()"),
                     self.enable_current_package)
        self._disable_button = QtGui.QPushButton("&Disable")
        self._disable_button.setEnabled(False)
        self.connect(self._disable_button,
                     QtCore.SIGNAL("clicked()"),
                     self.disable_current_package)
        self._configure_button = QtGui.QPushButton("&Configure...")
        self._configure_button.setEnabled(False)
        self.connect(self._configure_button,
                     QtCore.SIGNAL("clicked()"),
                     self.configure_current_package)
        self._reload_button = QtGui.QPushButton("&Reload")
        self._reload_button.setEnabled(False)
        self.connect(self._reload_button,
                     QtCore.SIGNAL("clicked()"),
                     self.reload_current_package)
        button_box = QtGui.QDialogButtonBox()
        button_box.addButton(self._enable_button, QtGui.QDialogButtonBox.ActionRole)
        button_box.addButton(self._disable_button, QtGui.QDialogButtonBox.ActionRole)
        button_box.addButton(self._configure_button, QtGui.QDialogButtonBox.ActionRole)
        button_box.addButton(self._reload_button, QtGui.QDialogButtonBox.ActionRole)
        right_layout.addWidget(button_box)

        self.connect(self,
                     self.select_package_after_update_signal,
                     self.select_package_after_update_slot,
                     QtCore.Qt.QueuedConnection)

        # pm = get_package_manager()
        # self.connect(pm,
        #              pm.reloading_package_signal,
        #              self.reload_current_package_finisher,
        #              QtCore.Qt.QueuedConnection)
        app = get_vistrails_application()
        app.register_notification("pm_reloading_package", 
                                  self.reload_current_package_finisher)
        app.register_notification("package_added", self.package_added)
        app.register_notification("package_removed", self.package_removed)
        
        self.populate_lists()

        self._current_package = None
        self.erase_cache = False

    def populate_lists(self):
        pkg_manager = get_package_manager()
        enabled_pkgs = sorted(pkg_manager.enabled_package_list())
        enabled_pkg_dict = dict([(pkg.codepath, pkg) for
                                   pkg in enabled_pkgs])
        self._enabled_packages_list.clear()
        for pkg in enabled_pkgs:
            self._enabled_packages_list.addItem(pkg.codepath)
        self._enabled_packages_list.sortItems()
        available_pkg_names = [pkg for pkg in 
                               sorted(pkg_manager.available_package_names_list())
                               if pkg not in enabled_pkg_dict]
        self._available_packages_list.clear()
        for pkg in available_pkg_names:
            self._available_packages_list.addItem(pkg)
        self._available_packages_list.sortItems()

    ##########################################################################

    def enable_current_package(self):
        av = self._available_packages_list
        inst = self._enabled_packages_list
        item = av.currentItem()
        pos = av.indexFromItem(item).row()
        codepath = str(item.text())
        pm = get_package_manager()

        dependency_graph = pm.dependency_graph()
        new_deps = self._current_package.dependencies()

        from core.modules.basic_modules import identifier as basic_modules_identifier
        if self._current_package.identifier != basic_modules_identifier:
            new_deps.append(basic_modules_identifier)

        try:
            pm.check_dependencies(self._current_package, new_deps)
        except self._current_package.MissingDependency, e:
            debug.critical("Missing dependencies", str(e))
        else:
            palette = QModulePalette.instance()
            palette.setUpdatesEnabled(False)
            try:
                pm.late_enable_package(codepath)
            except self._current_package.InitializationFailed, e:
                debug.critical("Initialization of package '%s' failed" %
                               codepath, str(e))
                raise
            finally:
                palette.setUpdatesEnabled(True)
                palette.treeWidget.expandAll()
            av.takeItem(pos)
            inst.addItem(item)
            inst.sortItems()
            self.erase_cache = True
            self.select_package_after_update(codepath)
            self.invalidate_current_pipeline()

    def disable_current_package(self):
        av = self._available_packages_list
        inst = self._enabled_packages_list
        item = inst.currentItem()
        pos = inst.indexFromItem(item).row()
        codepath = str(item.text())
        pm = get_package_manager()

        dependency_graph = pm.dependency_graph()
        identifier = pm.get_package_by_codepath(codepath).identifier

        if dependency_graph.in_degree(identifier) > 0:
            rev_deps = dependency_graph.inverse_adjacency_list[identifier]
            debug.critical("Missing dependency",
                           ("There are other packages that depend on this:\n %s" +
                            "Please disable those first.") % rev_deps)
        else:
            pm.late_disable_package(codepath)
            inst.takeItem(pos)
            av.addItem(item)
            av.sortItems()
            self.erase_cache = True
            self.select_package_after_update(codepath)
            self.invalidate_current_pipeline()

    def configure_current_package(self):
        dlg = QPackageConfigurationDialog(self, self._current_package)
        dlg.exec_()

    def reload_current_package(self):
        # DISABLES the current package and all reverse dependencies
        inst = self._enabled_packages_list
        item = inst.currentItem()
        pm = get_package_manager()
        codepath = str(item.text())
        
        palette = QModulePalette.instance()
        palette.setUpdatesEnabled(False)
        pm.reload_package_disable(codepath)
        self.erase_cache = True

    def reload_current_package_finisher(self, codepath, reverse_deps, prefix_dictionary):
        # REENABLES the current package and all reverse dependencies
        pm = get_package_manager()
        try:
            pm.reload_package_enable(reverse_deps, prefix_dictionary)
        except self._current_package.InitializationFailed, e:
            debug.critical("Re-initialization of package '%s' failed" % 
                            codepath, str(e))
            raise
        finally:
            self.populate_lists()
            palette = QModulePalette.instance()
            palette.setUpdatesEnabled(True)
            palette.treeWidget.expandAll()
            self.erase_cache = True
            self.select_package_after_update(codepath)
            self.invalidate_current_pipeline()

    def package_added(self, codepath):
        # package was added, we need to update list
        av = self._available_packages_list
        inst = self._enabled_packages_list
        for item in av.findItems(codepath, QtCore.Qt.MatchExactly):
            pos = av.indexFromItem(item).row()
            av.takeItem(pos)
            inst.addItem(item)
            inst.sortItems()
            self.erase_cache = True
            self.select_package_after_update(codepath)

    def package_removed(self, codepath):
        # package was removed, we need to update list
        av = self._available_packages_list
        inst = self._enabled_packages_list
        for item in inst.findItems(codepath, QtCore.Qt.MatchExactly):
            pos = inst.indexFromItem(item).row()
            inst.takeItem(pos)
            av.addItem(item)
            av.sortItems()
            self.erase_cache = True
            self.select_package_after_update(codepath)

    def select_package_after_update(self, codepath):
        # Selecting the package causes self._current_package to be set,
        # which reference prevents the package from being freed, so we
        # queue it to select after the event loop completes.
        self.emit(self.select_package_after_update_signal, codepath)

    def select_package_after_update_slot(self, codepath):
        inst = self._enabled_packages_list
        av = self._available_packages_list
        for item in av.findItems(codepath, QtCore.Qt.MatchExactly):
            av.setCurrentItem(item)
        for item in inst.findItems(codepath, QtCore.Qt.MatchExactly):
            inst.setCurrentItem(item)

    def set_buttons_to_enabled_package(self):
        self._enable_button.setEnabled(False)
        assert self._current_package
        pm = get_package_manager()
        from core.modules.basic_modules import identifier as basic_modules_identifier
        from core.modules.abstraction import identifier as abstraction_identifier
        is_not_basic_modules = (self._current_package.identifier != basic_modules_identifier)
        is_not_abstraction = (self._current_package.identifier != abstraction_identifier)
        can_disable = (pm.can_be_disabled(self._current_package.identifier) and
                       is_not_basic_modules and
                       is_not_abstraction)
        self._disable_button.setEnabled(can_disable)
        if not can_disable and is_not_basic_modules and is_not_abstraction:
            msg = ("Module has reverse dependencies that must\n"+
                   "be first disabled.")
            self._disable_button.setToolTip(msg)
        else:
            self._disable_button.setToolTip("")
        conf = self._current_package.configuration is not None
        self._configure_button.setEnabled(conf)
        self._reload_button.setEnabled(is_not_basic_modules)

    def set_buttons_to_available_package(self):
        self._configure_button.setEnabled(False)
        self._disable_button.setEnabled(False)
        self._enable_button.setEnabled(True)
        self._reload_button.setEnabled(False)

    def set_package_information(self):
        """Looks at current package and sets all labels (name,
        dependencies, etc.) appropriately.

        """
        assert self._current_package
        p = self._current_package
        try:
            p.load()
        except Exception, e:
            msg = 'ERROR: Could not load package.'
            self._name_label.setText(msg)
            self._version_label.setText(msg)
            self._identifier_label.setText(msg)
            self._dependencies_label.setText(msg)
            self._description_label.setText(msg)
            self._reverse_dependencies_label.setText(msg)
            debug.critical('Cannot load package', str(e))
        else:
            self._name_label.setText(p.name)
            deps = ', '.join(str(d) for d in p.dependencies()) or \
                'No package dependencies.'
            try:
                pm = get_package_manager()
                reverse_deps = \
                    (', '.join(pm.reverse_dependencies(p.identifier)) or
                     'No reverse dependencies.')
            except KeyError:
                reverse_deps = ("Reverse dependencies only " +
                                "available for enabled packages.")
            self._identifier_label.setText(p.identifier)
            self._version_label.setText(p.version)
            self._dependencies_label.setText(deps)
            self._description_label.setText(p.description)
            self._reverse_dependencies_label.setText(reverse_deps)


    ##########################################################################
    # Signal handling

    def selected_enabled_list(self):
        item = self._enabled_packages_list.currentItem()
        if item is None:
            return # prevent back and forth looping when clearing selection
        self._available_packages_list.setCurrentItem(None)
        codepath = str(item.text())
        pm = get_package_manager()
        self._current_package = pm.get_package_by_codepath(codepath)
        self.set_buttons_to_enabled_package()
        self.set_package_information()
        self._enabled_packages_list.setFocus()

    def selected_available_list(self):
        item = self._available_packages_list.currentItem()
        if item is None:
            return # prevent back and forth looping when clearing selection
        self._enabled_packages_list.setCurrentItem(None)
        codepath = str(item.text())
        pm = get_package_manager()
        self._current_package = pm.look_at_available_package(codepath)
        self.set_buttons_to_available_package()
        self.set_package_information()
        self._available_packages_list.setFocus()

    def invalidate_current_pipeline(self):
        # Reconstruct the current pipelines from root
        from core.interpreter.cached import CachedInterpreter
        CachedInterpreter.flush()
        def reload_view(view):
            view.version_selected(view.controller.current_version,
                                  True, from_root=True)
        #    def reload_tab(tab):
        #        scene = tab.scene()
        #        if scene.current_pipeline:
        #            scene.current_pipeline.is_valid = False
        #            scene.current_pipeline= \
        #                view.controller.vistrail.getPipeline(
        #                                                scene.current_version)
        #            view.controller.validate(scene.current_pipeline)
        #            scene.setupScene(scene.current_pipeline)
        #
        #    for i in xrange(view.stack.count()):
        #        tab = view.stack.widget(i)
        #        if isinstance(tab, QPipelineView):
        #            reload_tab(tab)
        #    for tab in view.detached_views:
        #        if isinstance(tab, QPipelineView):
        #            reload_tab(tab)

        from gui.vistrails_window import _app
        for i in xrange(_app.stack.count()):
            view = _app.stack.widget(i)
            reload_view(view)
        for view in _app.windows:
            reload_view(view)
        
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

        self._general_tab = self.create_general_tab()
        self._tab_widget.addTab(self._general_tab, 'General Configuration')

        self._thumbs_tab = self.create_thumbs_tab()
        self._tab_widget.addTab(self._thumbs_tab, 'Thumbnails Configuration')
        
        self._packages_tab = self.create_packages_tab()
        self._tab_widget.addTab(self._packages_tab, 'Module Packages')
        
        self._configuration_tab = self.create_configuration_tab()
        self._tab_widget.addTab(self._configuration_tab, 'Expert Configuration')

        self._button_box = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Close,
                                                  QtCore.Qt.Horizontal,
                                                  f)
        self.connect(self._tab_widget,
                     QtCore.SIGNAL('currentChanged(int)'),
                     self.tab_changed)

        self.connect(self._button_box,
                     QtCore.SIGNAL('clicked(QAbstractButton *)'),
                     self.close_dialog)

        self.connect(self._configuration_tab._tree.treeWidget,
                     QtCore.SIGNAL('configuration_changed'),
                     self.configuration_changed)

        self.connect(self._general_tab,
                     QtCore.SIGNAL('configuration_changed'),
                     self.configuration_changed)
        
        self.connect(self._thumbs_tab,
                     QtCore.SIGNAL('configuration_changed'),
                     self.configuration_changed)

        l.addWidget(self._button_box)
        l.addWidget(self._status_bar)

    def close_dialog(self):
        self.done(0)

    def create_general_tab(self):
        """ create_general_tab() -> QGeneralConfiguration
        
        """
        return QGeneralConfiguration(self,
                                     get_vistrails_persistent_configuration(),
                                     get_vistrails_configuration())
        
    def create_thumbs_tab(self):
        """ create_thumbs_tab() -> QThumbnailConfiguration
        
        """
        return QThumbnailConfiguration(self,
                                       get_vistrails_persistent_configuration(),
                                       get_vistrails_configuration())

    def create_configuration_tab(self):
        return QConfigurationWidget(self,
                                    get_vistrails_persistent_configuration(),
                                    get_vistrails_configuration(),
                                    self._status_bar)

    def create_packages_tab(self):
        return QPackagesWidget(self, self._status_bar)

    def sizeHint(self):
        return QtCore.QSize(800, 600)

    def tab_changed(self, index):
        """ tab_changed(index: int) -> None
        Keep general and advanced configurations in sync
        
        """
        self._configuration_tab.configuration_changed(
                                       get_vistrails_persistent_configuration(),
                                       get_vistrails_configuration())
        self._general_tab.update_state(
                                       get_vistrails_persistent_configuration(),
                                       get_vistrails_configuration())
    
    def configuration_changed(self, item, new_value):
        """ configuration_changed(item: QTreeWidgetItem *, 
        new_value: QString) -> None
        Write the current session configuration to startup.xml.
        Note:  This is already happening on close to capture configuration
        items that are not set in preferences.  We are doing this here too, so
        we guarantee the changes were saved before VisTrails crashes.
        
        """
        from PyQt4 import QtCore
        from gui.application import get_vistrails_application
        get_vistrails_application().save_configuration()

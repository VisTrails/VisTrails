###############################################################################
##
## Copyright (C) 2011-2014, NYU-Poly.
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
from PyQt4 import QtCore, QtGui

from vistrails.core.system import systemType
from vistrails.core.utils import versions_increasing
from vistrails.gui.common_widgets import QDockPushButton
from vistrails.gui.module_annotation import QModuleAnnotationTable
from vistrails.gui.ports_pane import PortsList
from vistrails.gui.version_prop import QVersionProp
from vistrails.gui.vistrails_palette import QVistrailsPaletteInterface

class QModuleInfo(QtGui.QWidget, QVistrailsPaletteInterface):
    def __init__(self, parent=None, flags=QtCore.Qt.Widget):
        QtGui.QWidget.__init__(self, parent, flags)
        self.build_widget()
        self.controller = None
        self.module = None
        self.pipeline_view = None # pipeline_view
        self.read_only = False
        self.is_updating = False

    def build_widget(self):
        name_label = QtGui.QLabel("Name:")
        self.name_edit = QtGui.QLineEdit()
        self.connect(self.name_edit, QtCore.SIGNAL('editingFinished()'),
                     self.name_editing_finished)
        self.name_edit.setMinimumSize(50, 22)
        type_label = QtGui.QLabel("Type:")
        self.type_edit = QtGui.QLabel("")
        # self.type_edit.setReadOnly(True)
        package_label = QtGui.QLabel("Package:")
        self.package_edit = QtGui.QLabel("")
        # self.package_edit.setReadOnly(True)
        id = QtGui.QLabel("Id:")
        self.module_id = QtGui.QLabel("")
        # self.module_id.setReadOnly(True)
        self.configure_button = QDockPushButton("Configure")
        self.connect(self.configure_button, QtCore.SIGNAL('clicked()'),
                     self.configure)
        self.doc_button = QDockPushButton("Documentation")
        self.connect(self.doc_button, QtCore.SIGNAL('clicked()'),
                     self.documentation)

        layout = QtGui.QVBoxLayout()
        layout.setMargin(2)
        layout.setSpacing(4)
        def add_line(left, right):
            h_layout = QtGui.QHBoxLayout()
            h_layout.setMargin(2)
            h_layout.setSpacing(2)
            h_layout.setAlignment(QtCore.Qt.AlignLeft)
            h_layout.addWidget(left)
            h_layout.addWidget(right)
            h_widget = QtGui.QWidget()
            h_widget.setLayout(h_layout)
            h_widget.setSizePolicy(QtGui.QSizePolicy.Ignored,
                                   QtGui.QSizePolicy.Preferred)
            layout.addWidget(h_widget)
        add_line(name_label, self.name_edit)
        add_line(type_label, self.type_edit)
        add_line(package_label, self.package_edit)
        add_line(id, self.module_id)
        h_layout = QtGui.QHBoxLayout()
        h_layout.setMargin(2)
        h_layout.setSpacing(5)
        h_layout.setAlignment(QtCore.Qt.AlignCenter)
        h_layout.addWidget(self.configure_button)
        h_layout.addWidget(self.doc_button)
        layout.addLayout(h_layout)
        
        self.tab_widget = QtGui.QTabWidget()
        # keep from overflowing on mac
        if systemType in ['Darwin']:
            self.tab_widget.tabBar().setStyleSheet('font-size: 12pt')
        # this causes a crash when undocking the palette in Mac OS X
        # see https://bugreports.qt-project.org/browse/QTBUG-16851
        # self.tab_widget.setDocumentMode(True)
        self.input_ports_list = PortsList('input')
        self.tab_widget.addTab(self.input_ports_list, 'Inputs')
        self.output_ports_list = PortsList('output')
        self.tab_widget.addTab(self.output_ports_list, 'Outputs')
        self.ports_lists = [self.input_ports_list,
                            self.output_ports_list]
        self.annotations = QModuleAnnotationTable()
        self.tab_widget.addTab(self.annotations, 'Annotations')
        layout.addWidget(self.tab_widget, 1)

        layout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(layout)
        self.setWindowTitle('Module Info')

    def setReadOnly(self, read_only):
        if read_only != self.read_only:
            self.read_only = read_only
            for widget in self.ports_lists + [self.annotations]:
                widget.setReadOnly(read_only)

    def set_controller(self, controller):
        if self.controller == controller:
            return
        self.controller = controller
        for ports_list in self.ports_lists:
            ports_list.set_controller(controller)
        self.annotations.set_controller(controller)

        if self.controller is not None:
            scene = self.controller.current_pipeline_scene
            selected_ids = scene.get_selected_module_ids() 
            modules = [self.controller.current_pipeline.modules[i] 
                       for i in selected_ids]
            if len(modules) == 1:
                self.update_module(modules[0])
            else:
                self.update_module(None)
        else:
            self.update_module()

    def update_module(self, module=None):
        self.module = module
        for ports_list in self.ports_lists:
            ports_list.update_module(module)
        self.annotations.updateModule(module)

        if module is None:
            # We show the version properties tab if both are tabified and
            # self is visible
            if not self.toolWindow().isFloating() and \
               not QVersionProp.instance().toolWindow().isFloating() and \
               not self.toolWindow().visibleRegion().isEmpty():
                QVersionProp.instance().set_visible(True)
            self.name_edit.setText("")
            if not versions_increasing(QtCore.QT_VERSION_STR, '4.7.0'):
                self.name_edit.setPlaceholderText("")
            # self.name_edit.setEnabled(False)
            self.type_edit.setText("")
            # self.type_edit.setEnabled(False)
            self.package_edit.setText("")
            self.module_id.setText("")
        else:
            # We show self  if both are tabified and
            # the version properties tab is visible
            if not self.toolWindow().isFloating() and \
               not QVersionProp.instance().toolWindow().isFloating() and \
               not QVersionProp.instance().toolWindow().visibleRegion().isEmpty():
                self.set_visible(True)
            if module.has_annotation_with_key('__desc__'):
                label = module.get_annotation_by_key('__desc__').value.strip()
            else:
                label = ''
            self.name_edit.setText(label)
            if not label and not versions_increasing(QtCore.QT_VERSION_STR, 
                                                     '4.7.0'):
                self.name_edit.setPlaceholderText(self.module.name)

            # self.name_edit.setEnabled(True)
            self.type_edit.setText(self.module.name)
            # self.type_edit.setEnabled(True)
            self.package_edit.setText(self.module.package)
            # self.package_edit.setEnabled(True)
            self.module_id.setText('%d' % self.module.id)
            # self.module_id.setEnabled(True)

    def name_editing_finished(self):
        # updating module may trigger a second call so we check for that
        if self.is_updating or self.module is None:
            return
        try:
            self.is_updating = True
            old_text = ''
            if self.module.has_annotation_with_key('__desc__'):
                old_text = self.module.get_annotation_by_key('__desc__').value
            new_text = str(self.name_edit.text()).strip()
            if not new_text:
                if old_text:
                    self.controller.delete_annotation('__desc__', 
                                                      self.module.id)
            elif old_text != new_text:
                self.controller.add_annotation(('__desc__', new_text), 
                                               self.module.id)
            scene = self.controller.current_pipeline_scene
            scene.recreate_module(self.controller.current_pipeline, 
                                  self.module.id)
        finally:
            self.is_updating = False
            
    def configure(self):
        from vistrails.gui.vistrails_window import _app
        _app.configure_module()

    def documentation(self):
        from vistrails.gui.vistrails_window import _app
        _app.show_documentation()
        
    def update_entry_klass(self, entry_klass):
        self.input_ports_list.set_entry_klass(entry_klass)
        
    def show_annotations(self):
        if self.module is not None:
            self.tab_widget.setCurrentWidget(self.annotations)
            self.annotations.editNextAvailableCell()

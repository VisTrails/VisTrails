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
from PyQt4 import QtCore, QtGui

from core.utils import versions_increasing
from gui.common_widgets import QDockPushButton
from gui.module_annotation import QModuleAnnotationTable
from gui.ports_pane import PortsList
from gui.vistrails_palette import QVistrailsPaletteInterface

class QModuleInfo(QtGui.QWidget, QVistrailsPaletteInterface):
    def __init__(self, parent=None, flags=QtCore.Qt.Widget):
        QtGui.QWidget.__init__(self, parent, flags)
        self.build_widget()
        self.controller = None
        self.module = None
        self.pipeline_view = None # pipeline_view

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
        self.configure_button = QDockPushButton("Configure")
        self.connect(self.configure_button, QtCore.SIGNAL('clicked()'),
                     self.configure)
        self.doc_button = QDockPushButton("Documentation")
        self.connect(self.doc_button, QtCore.SIGNAL('clicked()'),
                     self.documentation)

        layout = QtGui.QVBoxLayout()
        layout.setMargin(2)
        layout.setSpacing(4)
        h_layout = QtGui.QHBoxLayout()
        h_layout.setMargin(2)
        h_layout.setSpacing(2)
        h_layout.setAlignment(QtCore.Qt.AlignLeft)
        h_layout.addWidget(name_label)
        h_layout.addWidget(self.name_edit)
        layout.addLayout(h_layout)
        h_layout = QtGui.QHBoxLayout()        
        h_layout.setMargin(2)
        h_layout.setSpacing(2)
        h_layout.setAlignment(QtCore.Qt.AlignLeft)
        h_layout.addWidget(type_label)
        h_layout.addWidget(self.type_edit)
        h_widget = QtGui.QWidget()
        h_widget.setLayout(h_layout)
        h_widget.setSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Preferred)
        layout.addWidget(h_widget)
        h_layout = QtGui.QHBoxLayout()        
        h_layout.setMargin(2)
        h_layout.setSpacing(2)
        h_layout.setAlignment(QtCore.Qt.AlignLeft)
        h_layout.addWidget(package_label)
        h_layout.addWidget(self.package_edit)
        h_widget = QtGui.QWidget()
        h_widget.setLayout(h_layout)
        h_widget.setSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Preferred)
        layout.addWidget(h_widget)
        h_layout = QtGui.QHBoxLayout()        
        h_layout.setMargin(2)
        h_layout.setSpacing(5)
        h_layout.setAlignment(QtCore.Qt.AlignCenter)
        h_layout.addWidget(self.configure_button)
        h_layout.addWidget(self.doc_button)
        layout.addLayout(h_layout)
        
        self.tab_widget = QtGui.QTabWidget()
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
        self.setWindowTitle('Module Information')

    def set_controller(self, controller):
        self.controller = controller
        for ports_list in self.ports_lists:
            ports_list.set_controller(controller)
        self.annotations.set_controller(controller)

        scene = self.controller.current_pipeline_view
        selected_ids = scene.get_selected_module_ids() 
        modules = [self.controller.current_pipeline.modules[i] 
                   for i in selected_ids]
        if len(modules) == 1:
            self.update_module(modules[0])
        else:
            self.update_module(None)

    def update_module(self, module=None):
        self.module = module
        for ports_list in self.ports_lists:
            ports_list.update_module(module)
        self.annotations.updateModule(module)

        if module is None:
            self.name_edit.setText("")
            if not versions_increasing(QtCore.QT_VERSION_STR, '4.7.0'):
                self.name_edit.setPlaceholderText("")
            # self.name_edit.setEnabled(False)
            self.type_edit.setText("")
            # self.type_edit.setEnabled(False)
            self.package_edit.setText("")
        else:
            if module.has_annotation_with_key('__desc__'):
                label = module.get_annotation_by_key('__desc__').value.strip()
            else:
                label = ''
            self.name_edit.setText(label)
            if not label and not versions_increasing(QtCore.QT_VERSION_STR, 
                                                     '4.7.0'):
                #print QtCore.QT_VERSION_STR, versions_increasing(QtCore.QT_VERSION_STR, '4.7.0')
                self.name_edit.setPlaceholderText(self.module.name)

            # self.name_edit.setEnabled(True)
            self.type_edit.setText(self.module.name)
            # self.type_edit.setEnabled(True)
            self.package_edit.setText(self.module.package)
            # self.package_edit.setEnabled(True)
            
    def name_editing_finished(self):
        if self.module is not None:
            old_text = ''
            if self.module.has_annotation_with_key('__desc__'):
                old_text = self.module.get_annotation_by_key('__desc__').value
            new_text = str(self.name_edit.text()).strip()
            if not new_text:
                if old_text:
                    #print 'delete annotation'
                    self.controller.delete_annotation('__desc__', 
                                                      self.module.id)
            elif old_text != new_text:
                #print 'add annotation', old_text, new_text
                self.controller.add_annotation(('__desc__', new_text), 
                                               self.module.id)
                

            scene = self.controller.current_pipeline_view
            scene.recreate_module(self.controller.current_pipeline, 
                                  self.module.id)
            
    def configure(self):
        from gui.vistrails_window import _app
        _app.configure_module()

    def documentation(self):
        from gui.vistrails_window import _app
        _app.show_documentation()
        
    def update_entry_klass(self, entry_klass):
        self.input_ports_list.set_entry_klass(entry_klass)
        
    def show_annotations(self):
        if self.module is not None:
            self.tab_widget.setCurrentWidget(self.annotations)
            self.annotations.editNextAvailableCell()

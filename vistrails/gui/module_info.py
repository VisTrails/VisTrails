from PyQt4 import QtCore, QtGui

from core.utils import versions_increasing
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
        type_label = QtGui.QLabel("Type:")
        self.type_edit = QtGui.QLabel("")
        # self.type_edit.setReadOnly(True)
        package_label = QtGui.QLabel("Package:")
        self.package_edit = QtGui.QLabel("")
        # self.package_edit.setReadOnly(True)
        self.configure_button = QtGui.QPushButton("Configure")
        self.configure_button.setMinimumSize(50, 30)
        self.connect(self.configure_button, QtCore.SIGNAL('clicked()'),
                     self.configure)
        self.doc_button = QtGui.QPushButton("Documentation")
        self.doc_button.setMinimumSize(50, 30)
        self.connect(self.doc_button, QtCore.SIGNAL('clicked()'),
                     self.documentation)

        layout = QtGui.QVBoxLayout()
        layout.setMargin(2)
        layout.setSpacing(2)
        h_layout = QtGui.QHBoxLayout()
        h_layout.setMargin(0)
        h_layout.setSpacing(0)
        h_layout.setAlignment(QtCore.Qt.AlignLeft)
        h_layout.addWidget(name_label)
        h_layout.addWidget(self.name_edit)
        layout.addLayout(h_layout)
        h_layout = QtGui.QHBoxLayout()        
        h_layout.setMargin(0)
        h_layout.setSpacing(0)
        h_layout.setAlignment(QtCore.Qt.AlignLeft)
        h_layout.addWidget(type_label)
        h_layout.addWidget(self.type_edit)
        layout.addLayout(h_layout)
        h_layout = QtGui.QHBoxLayout()        
        h_layout.setMargin(0)
        h_layout.setSpacing(0)
        h_layout.setAlignment(QtCore.Qt.AlignLeft)
        h_layout.addWidget(package_label)
        h_layout.addWidget(self.package_edit)
        layout.addLayout(h_layout)
        h_layout = QtGui.QHBoxLayout()        
        h_layout.setMargin(0)
        h_layout.setSpacing(5)
        h_layout.setAlignment(QtCore.Qt.AlignCenter)
        h_layout.addWidget(self.configure_button)
        h_layout.addWidget(self.doc_button)
        layout.addLayout(h_layout)
        
        tab_widget = QtGui.QTabWidget()
        tab_widget.setDocumentMode(True)
        self.input_ports_list = PortsList('input')
        tab_widget.addTab(self.input_ports_list, 'Inputs')
        self.output_ports_list = PortsList('output')
        tab_widget.addTab(self.output_ports_list, 'Outputs')
        self.ports_lists = [self.input_ports_list,
                            self.output_ports_list]
        self.annotations = QModuleAnnotationTable()
        tab_widget.addTab(self.annotations, 'Annotations')
        layout.addWidget(tab_widget, 1)

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
                print QtCore.QT_VERSION_STR, versions_increasing(QtCore.QT_VERSION_STR, '4.7.0')
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
                    print 'delete annotation'
                    self.controller.delete_annotation('__desc__', 
                                                      self.module.id)
            elif old_text != new_text:
                print 'add annotation', old_text, new_text
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
        

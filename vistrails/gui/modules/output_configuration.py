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
"""This file specifies the configuration widget for OutputModule and
its subclasses.

"""

from PyQt4 import QtCore, QtGui

from vistrails.core.configuration import ConfigPath
from vistrails.core.modules.basic_modules import Dictionary
from vistrails.gui.common_widgets import QSearchTreeWindow, QSearchTreeWidget, \
    QFileChooserToolButton, QDirectoryChooserToolButton
from vistrails.gui.modules.module_configure import StandardModuleConfigurationWidget
from vistrails.gui.utils import YES_BUTTON, NO_BUTTON, show_question, show_warning

class OutputModuleConfigurationWidget(StandardModuleConfigurationWidget):
    def __init__(self, module, controller, parent=None):
        StandardModuleConfigurationWidget.__init__(self, module, controller, 
                                                   parent)
        self.update_widget()

    def get_configuration(self):
        config = {}
        for f in self.module.functions:
            if f.name == 'configuration':
                f_config = Dictionary.translate_to_python(f.params[0].strValue)
                config.update(f_config)
        return config

    def set_configuration(self, config):
        self.controller.update_function(self.module, 'configuration', 
                                [Dictionary.translate_to_string(config)])

    def update_widget(self):
        self._changed_config = {}
        self._mode_groups = {}
        layout = QtGui.QVBoxLayout()
        config = self.get_configuration()

        self.found_modes = set()
        for mode in self.module.module_descriptor.module.get_sorted_mode_list():
            mode_config = None
            if mode.mode_type in config:
                mode_config = config[mode.mode_type]
            # create output mode widget passing current config
            fields = self.build_mode_config(layout, mode, mode_config)
            self._mode_groups[mode.mode_type] = fields
            self.found_modes.add(mode.mode_type)
            
        for mode_type, mode_config in config.iteritems():
            if mode_type not in self.found_modes:
                fields = self.build_mode_config(layout, None, mode_config)
                self._mode_groups[mode_type] = fields
                self.found_modes.add(mode_type)
                
        # do we want to add a manual config mode for modes that have
        # neither been set before nor are registered?
        # DK: not now...
        scroll_area = QtGui.QScrollArea()
        inner_widget =  QtGui.QWidget()
        inner_widget.setLayout(layout)
        scroll_area.setWidget(inner_widget)
        scroll_area.setWidgetResizable(True)
        self.setLayout(QtGui.QVBoxLayout())
        self.layout().addWidget(scroll_area, 1)
        self.layout().addLayout(self.create_buttons())
        self.layout().setContentsMargins(0,0,0,0)

    def create_buttons(self):
        """ create_buttons() -> None
        Create and connect signals to Save & Reset button
        
        """
        buttonLayout = QtGui.QHBoxLayout()
        buttonLayout.setMargin(5)
        self.saveButton = QtGui.QPushButton('&Save', self)
        self.saveButton.setFixedWidth(100)
        self.saveButton.setEnabled(False)
        buttonLayout.addWidget(self.saveButton)
        self.resetButton = QtGui.QPushButton('&Reset', self)
        self.resetButton.setFixedWidth(100)
        self.resetButton.setEnabled(False)
        buttonLayout.addWidget(self.resetButton)
        self.connect(self.saveButton, QtCore.SIGNAL('clicked(bool)'),
                     self.save_triggered)
        self.connect(self.resetButton, QtCore.SIGNAL('clicked(bool)'),
                     self.reset_triggered)
        return buttonLayout

    def build_mode_config(self, base_layout, mode, mode_config):
        group_box = QtGui.QGroupBox()
        group_box.setTitle(mode.mode_type)
        group_layout = QtGui.QVBoxLayout()
        group_box.setLayout(group_layout)
        # label = QtGui.QLabel(mode.mode_type)
        # base_layout.addWidget(label)
        base_layout.addWidget(group_box, 1)
        field_layouts = {}
        if mode is None:
            for k, v in mode_config.iteritems():
                print "ADD UNSPECIFIED FIELD:", k
                dummy_field = ConfigField(k, None, str)
                layout = self.add_field(dummy_field, mode_config, k)
                group_layout.addLayout(layout)
                field_layouts[k] = layout
        else:
            for field in mode.config_cls.get_all_fields():
                print "ADD FIELD:", mode.mode_type, field.name
                layout = self.add_field(field, mode_config, mode.mode_type)
                group_layout.addLayout(layout)
                field_layouts[mode.mode_type] = layout
        return field_layouts

    # TODO Unify this with code in gui.configuration!
    def add_field(self, field, mode_config, mode_type, indent=0):
        layout = QtGui.QHBoxLayout()
        layout.setMargin(0)
        layout.setSpacing(5)

        config_key = (mode_type, field.name)
        if mode_config is not None and field.name in mode_config:
            config_val = mode_config[field.name]
        else:
            config_val = field.default_val
        # config_val = mode_config.get_deep_value(config_key)

        # icon = self.style().standardIcon(QtGui.QStyle.SP_MessageBoxWarning)
        # label = QtGui.QLabel()
        # label.setPixmap(icon.pixmap(14,14))
        # label.setToolTip("This option has been changed for this session")
        # layout.addWidget(label, 0, QtCore.Qt.AlignTop)
            
        # space = 0
        # if (not startup_only and
        #     config_val == self._configuration.get_deep_value(config_key)):
        #     space = label.sizeHint().width() + layout.spacing() * (indent + 1)
        #     label.hide()
        # elif indent > 0:
        #     space = layout.spacing() * indent

        # if space > 0:
        #     spacer = QtGui.QSpacerItem(space, label.sizeHint().height())
        #     layout.insertSpacerItem(0, spacer)

        # config_desc = find_simpledoc(config_key)

        config_desc = field.name
        widget_type = field.widget_type
        if widget_type is None:
            if field.val_type == bool:
                widget_type = "checkbox"
            elif field.val_type == ConfigPath:
                widget_type = "pathedit"
            else:
                widget_type = "lineedit"

        if widget_type == "combo":
            self.add_combo(layout, field, config_key, config_desc, config_val)
        elif widget_type == "lineedit":
            self.add_line_edit(layout, field, config_key, config_desc, 
                               config_val)
        elif widget_type == "pathedit":
            self.add_path_edit(layout, field, config_key, config_desc, 
                               config_val)
        else:
            config_val = bool(config_val)
            self.add_checkbox(layout, field, config_key, config_desc, 
                              config_val)
        layout.addStretch(1)
        # base_layout.addLayout(layout)
        return layout

    def add_signals(self, config_key, field):
        def call_field_changed(val):
            self.field_changed(config_key, field, val)
        self.connect(cb, QtCore.SIGNAL("toggled(bool)"),
                     call_field_changed)

    def add_checkbox(self, layout, field, config_key, config_desc, config_val):
        cb = QtGui.QCheckBox(config_desc)
        cb.setChecked(config_val)
        layout.addWidget(cb)

        def call_field_changed(val):
            self.field_changed(config_key, field, val)
        cb.toggled.connect(call_field_changed)

    def add_line_edit(self, layout, field, config_key, config_desc, config_val):
        options = {}
        if field.widget_options is not None:
            options = field.widget_options

        sub_layout = QtGui.QHBoxLayout()
        sub_layout.setMargin(0)
        sub_layout.setSpacing(5)

        if "label" in options:
            label_text = options["label"]
        else:
            label_text = config_desc
        label = QtGui.QLabel(label_text)
        sub_layout.addWidget(label)

        line_edit = QtGui.QLineEdit()
        if config_val is None:
            config_val = ""
        line_edit.setText(unicode(config_val))
        sub_layout.addWidget(line_edit)
        layout.addLayout(sub_layout)

        def call_field_changed(val):
            self.field_changed(config_key, field, val)
        line_edit.textEdited.connect(call_field_changed)

    def add_path_edit(self, layout, field, config_key, config_desc, config_val):
        options = {}
        if field.widget_options is not None:
            options = field.widget_options

        sub_layout = QtGui.QVBoxLayout()
        sub_layout.setMargin(0)
        sub_layout.setSpacing(5)
        
        if "label" in options:
            label_text = options["label"]
        else:
            label_text = config_desc
        label = QtGui.QLabel(label_text)
        sub_layout.addWidget(label)

        path_layout = QtGui.QHBoxLayout()
        path_layout.setMargin(0)
        path_layout.setSpacing(5)
        path_layout.addSpacing(15)
        line_edit = QtGui.QLineEdit()
        line_edit.setMinimumWidth(200)
        if config_val is None:
            config_val = ""
        line_edit.setText(unicode(config_val))
        path_layout.addWidget(line_edit)

        # if field.val_type == ConfigPath:
        #     button_cls = QDirectoryChooserToolButton
        # else:
        button_cls = QDirectoryChooserToolButton
        button = button_cls(self, line_edit)
        # button.pathChanged.connect(self.field_changed)
        path_layout.addWidget(button)
        sub_layout.addLayout(path_layout)
        layout.addLayout(sub_layout)

        def call_field_changed(val):
            self.field_changed(config_key, field, val)
        line_edit.textEdited.connect(call_field_changed)

    def add_combo(self, layout, field, config_key, config_desc, config_val):
        options = {}
        if field.widget_options is not None:
            options = field.widget_options

        sub_layout = QtGui.QHBoxLayout()
        sub_layout.setMargin(0)
        sub_layout.setSpacing(5)
        if "label" in options:
            label_text = options["label"]
        else:
            label_text = config_desc
        label = QtGui.QLabel(label_text)
        sub_layout.addWidget(label)
        combo = QtGui.QComboBox()
        inv_remap = None
        if "allowed_values" in options:
            values = options["allowed_values"]
            if "remap" in options:
                remap = options["remap"]
                inv_remap = dict((v, k) for (k, v) in remap.iteritems())
                entries = [remap[v] for v in values]
                cur_text = remap[config_val]
            else:
                entries = values
                cur_text = config_val
            for entry in entries:
                combo.addItem(entry)
            combo.setCurrentIndex(combo.findText(cur_text))
        sub_layout.addWidget(combo)
        layout.addLayout(sub_layout)

        def call_field_changed(val):
            if inv_remap is not None:
                val = inv_remap[val]
            self.field_changed(config_key, field, val)
        combo.currentIndexChanged[unicode].connect(call_field_changed)

    def field_changed(self, config_key, field, val):
        print "field changed:", config_key, val
        if config_key[0] not in self._changed_config:
            self._changed_config[config_key[0]] = {}
        # TODO support arbitrary nesting?
        val = field.from_string(val)
        self._changed_config[config_key[0]][config_key[1]] = val
        self.saveButton.setEnabled(True)
        self.resetButton.setEnabled(True)
        
        # config_val = self._configuration.get_deep_value(config_key)
        # if config_val != self._temp_configuration.get_deep_value(config_key):
        #     retval = QtGui.QMessageBox.question(
        #         self, 
        #         "Change Setting",
        #         "This configuration value has been temporarily changed. "
        #         "If you change it, it will be changed permanently.  Do you "
        #         "want to continue?", 
        #         QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Ok,
        #         QtGui.QMessageBox.Ok)
        #     if retval != QtGui.QMessageBox.Ok:
        #         return
        #     # need to update hbox to reflect change...
        #     layout = self._field_layouts[config_key]
        #     leading_item = layout.itemAt(0)
        #     if isinstance(leading_item.widget(), QtGui.QLabel):
        #         label = leading_item.widget()
        #         spacer = QtGui.QSpacerItem(label.sizeHint().width() + \
        #                                    layout.spacing(),
        #                                    label.sizeHint().height())
        #         layout.insertSpacerItem(0, spacer)
        #     else:
        #         spacer = leading_item
        #         label = layout.itemAt(1).widget()
        #         spacer.changeSize(spacer.sizeHint().width() + \
        #                           label.sizeHint().width() + layout.spacing(), 
        #                           label.sizeHint().height())
        #     label.hide()
        # # FIXME
        # if False:
        #     QtGui.QMessageBox.information(
        #         self, "Change Setting",
        #         "You must restart VisTrails for this setting to take effect.")

        # setattr(self._temp_configuration, config_key, val)
        # setattr(self._configuration, config_key, val)


    # def get_config_from_widgets(self):
    #     # go through field layouts and set each value in config
    #     for mode, field_layouts in self._mode_groups.iteritems():
    #         for field_name, layout in field_layouts.iteritems():
                
    #     return config

    def save_triggered(self):
        # get values from each widget check if any changed and
        # then dump the whole dictionary back to the configuration
        # function
        config = self.get_configuration()
        config.update(self._changed_config)
        self.set_configuration(config)

    def reset_triggered(self):
        self.clear()
        self.update_Widget()

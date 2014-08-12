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
        layout = QtGui.QVBoxLayout()
        config = self.get_configuration()

        self.mode_widgets = []
        self.found_modes = set()
        mode_layouts = []
        for mode in self.module.module_descriptor.module.get_sorted_mode_list():
            mode_config = None
            if mode.mode_type in config:
                mode_config = config[mode.mode_type]
            # create output mode widget passing current config
            mode_w = self.build_mode_config(layout, mode, mode_config)
            mode_layouts.append(mode_w.layout())
            self.found_modes.add(mode.mode_type)
            
        for mode_type, mode_config in config.iteritems():
            if mode_type not in self.found_modes:
                mode_w = self.build_mode_config(layout, None, mode_config, 
                                                title=mode_type)
                mode_layouts.append(mode_w.layout())
                self.found_modes.add(mode_type)
                
        width = 0
        for mode_layout in mode_layouts:
            for row in xrange(mode_layout.rowCount()):
                item = mode_layout.itemAtPosition(row, 0)
                if item and item.widget():
                    width = max(width, item.widget().sizeHint().width())
        for mode_layout in mode_layouts:
            mode_layout.setColumnMinimumWidth(0, width)

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

    def build_mode_config(self, base_layout, mode, mode_config, title=None):
        mode_widget = OutputModeConfigurationWidget(mode, mode_config, title)
        mode_widget.fieldChanged.connect(self.field_was_changed)
        self.mode_widgets.append(mode_widget)
        base_layout.addWidget(mode_widget, 1)
        return mode_widget

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

    def save_triggered(self):
        # get values from each widget check if any changed and
        # then dump the whole dictionary back to the configuration
        # function
        config = self.get_configuration()
        for mode_widget in self.mode_widgets:
            config.update(mode_widget._changed_config)
        self.set_configuration(config)
        self.saveButton.setEnabled(False)
        self.resetButton.setEnabled(False)

    def reset_triggered(self):
        config = self.get_configuration()
        for mode_widget in self.mode_widgets:
            for config_key, field in mode_widget._changed_fields.iteritems():
                widget = mode_widget.field_widgets[config_key]
                mode_type = config_key[0]
                mode_config = None
                if mode_type in config:
                    mode_config = config[mode_type]
                mode_widget.reset_field(widget, field, mode_config, mode_type)
        self.saveButton.setEnabled(False)
        self.resetButton.setEnabled(False)

    def field_was_changed(self, mode_widget):
        self.saveButton.setEnabled(True)
        self.resetButton.setEnabled(True)

class OutputModeConfigurationWidget(QtGui.QGroupBox):
    fieldChanged = QtCore.pyqtSignal(object)

    def __init__(self, mode, mode_config=None, title=None, parent=None):
        assert(mode is not None or mode_config is not None)

        QtGui.QGroupBox.__init__(self, parent)
        self.field_widgets = {}
        self._changed_config = {}
        self._changed_fields = {}

        if title is not None:
            self.setTitle(title)
        elif mode is not None:
            self.setTitle(mode.mode_type)
        else:
            self.setTitle("unknown")

        group_layout = QtGui.QGridLayout()
        group_layout.setMargin(5)
        group_layout.setSpacing(5)
        group_layout.setColumnStretch(1,1)

        if mode is None:
            for k, v in mode_config.iteritems():
                dummy_field = ConfigField(k, None, str)
                self.add_field(group_layout, dummy_field, mode_config,
                                        k)
        else:
            for field in mode.config_cls.get_all_fields():
                self.add_field(group_layout, field, mode_config, 
                               mode.mode_type)
        self.setLayout(group_layout)

    # TODO Unify this with code in gui.configuration!
    def add_field(self, layout, field, mode_config, mode_type, indent=0):
        config_key = (mode_type, field.name)
        if mode_config is not None and field.name in mode_config:
            config_val = mode_config[field.name]
        else:
            config_val = field.default_val

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
            widget = self.add_combo(layout, field, config_key, config_desc, 
                                    config_val)
        elif widget_type == "lineedit":
            widget = self.add_line_edit(layout, field, config_key, config_desc, 
                               config_val)
        elif widget_type == "pathedit":
            widget = self.add_path_edit(layout, field, config_key, config_desc, 
                                        config_val)
        else:
            config_val = bool(config_val)
            widget = self.add_checkbox(layout, field, config_key, config_desc, 
                                       config_val)
        self.field_widgets[config_key] = widget

    def reset_field(self, widget, field, mode_config, mode_type):
        config_key = (mode_type, field.name)
        if mode_config is not None and field.name in mode_config:
            config_val = mode_config[field.name]
        else:
            config_val = field.default_val

        if field.widget_type == "checkbox":
            config_val = bool(config_val)
        self.set_value(widget, field, config_val)

    def set_value(self, widget, field, val):
        widget_type = field.widget_type
        if widget_type is None:
            if field.val_type == bool:
                widget_type = "checkbox"
            elif field.val_type == ConfigPath:
                widget_type = "pathedit"
            else:
                widget_type = "lineedit"

        if widget_type == "combo":
            self.set_combo_value(widget, val)
        elif widget_type == "lineedit":
            self.set_line_edit_value(widget, val)
        elif widget_type == "pathedit":
            self.set_path_edit_value(widget, val)
        else:
            self.set_checkbox_value(widget, val)

    def add_checkbox(self, layout, field, config_key, config_desc, config_val):
        cb = QtGui.QCheckBox(config_desc)
        self.set_checkbox_value(cb, config_val)
        row = layout.rowCount()
        layout.addWidget(cb, row, 1)

        def call_field_changed(val):
            self.field_changed(config_key, field, val, config_val)
        cb.toggled.connect(call_field_changed)
        return cb

    def set_checkbox_value(self, cb, config_val):
        cb.setChecked(config_val)

    def add_line_edit(self, layout, field, config_key, config_desc, config_val):
        options = {}
        if field.widget_options is not None:
            options = field.widget_options

        if "label" in options:
            label_text = options["label"]
        else:
            label_text = config_desc
        label = QtGui.QLabel(label_text)
        row = layout.rowCount()
        layout.addWidget(label, row, 0, QtCore.Qt.AlignRight)

        line_edit = QtGui.QLineEdit()
        self.set_line_edit_value(line_edit, config_val)
        layout.addWidget(line_edit, row, 1)

        def call_field_changed():
            val = line_edit.text()
            self.field_changed(config_key, field, val, config_val)
        line_edit.editingFinished.connect(call_field_changed)
        return line_edit

    def set_line_edit_value(self, line_edit, config_val):
        if config_val is None:
            config_val = ""
        line_edit.setText(unicode(config_val))

    def add_path_edit(self, layout, field, config_key, config_desc, config_val):
        options = {}
        if field.widget_options is not None:
            options = field.widget_options

        path_edit = QtGui.QWidget()
        if "label" in options:
            label_text = options["label"]
        else:
            label_text = config_desc
        label = QtGui.QLabel(label_text)
        row = layout.rowCount()
        layout.addWidget(label, row, 0, QtCore.Qt.AlignRight)

        sub_layout = QtGui.QHBoxLayout()
        sub_layout.setMargin(0)
        sub_layout.setSpacing(5)
        line_edit = QtGui.QLineEdit()
        if config_val is None:
            config_val = ""
        line_edit.setText(unicode(config_val))
        sub_layout.addWidget(line_edit)
        path_edit.line_edit = line_edit

        # if field.val_type == ConfigPath:
        #     button_cls = QDirectoryChooserToolButton
        # else:
        button_cls = QDirectoryChooserToolButton
        button = button_cls(self, line_edit)
        sub_layout.addWidget(button)
        path_edit.setLayout(sub_layout)
        layout.addWidget(path_edit, row, 1)

        def call_field_changed():
            val = line_edit.text()
            self.field_changed(config_key, field, val, config_val)
        line_edit.editingFinished.connect(call_field_changed)
        return path_edit

    def set_path_edit_value(self, path_edit, config_val):
        if config_val is None:
            config_val = ""
        path_edit.line_edit.setText(unicode(config_val))

    def add_combo(self, layout, field, config_key, config_desc, config_val):
        options = {}
        if field.widget_options is not None:
            options = field.widget_options

        if "label" in options:
            label_text = options["label"]
        else:
            label_text = config_desc
        label = QtGui.QLabel(label_text)
        row = layout.rowCount()
        layout.addWidget(label, row, 0, QtCore.Qt.AlignRight)

        combo = QtGui.QComboBox()
        inv_remap = None
        if "allowed_values" in options:
            values = options["allowed_values"]
            if "remap" in options:
                remap = options["remap"]
                inv_remap = dict((v, k) for (k, v) in remap.iteritems())
                entries = [remap[v] for v in values]
            else:
                entries = values
            for entry in entries:
                combo.addItem(entry)
        self.set_combo_value(combo, config_val)
        laout.addWidget(combo, row, 1)

        def call_field_changed(val):
            if inv_remap is not None:
                val = inv_remap[val]
            self.field_changed(config_key, field, val, config_val)
        combo.currentIndexChanged[unicode].connect(call_field_changed)
        return combo

    def set_combo_value(self, combo, config_val):
        if "allowed_values" in options:
            if "remap" in options:
                remap = options["remap"]
                cur_text = remap[config_val]
            else:
                cur_text = config_val
            combo.setCurrentIndex(combo.findText(cur_text))
        else:
            combo.setCurrentIndex(-1)

    def field_changed(self, config_key, field, val, orig_val):
        # TODO support arbitrary nesting?
        try:
            val = field.from_string(val)
            if config_key[0] not in self._changed_config:
                self._changed_config[config_key[0]] = {}
            self._changed_config[config_key[0]][config_key[1]] = val
            self._changed_fields[config_key] = field
            self.fieldChanged.emit(self)
        except:
            widget = self.field_widgets[config_key]
            self.set_value(widget, field, orig_val)


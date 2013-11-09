###############################################################################
##
## Copyright (C) 2011-2013, NYU-Poly.
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

"""Widgets to display/edit configuration objects."""
import os
import os.path
from PyQt4 import QtGui, QtCore

from vistrails.core import debug
from vistrails.core.configuration import ConfigurationObject, \
    ConfigFieldParent, ConfigPath, ConfigURL, \
    get_vistrails_configuration, find_simpledoc

from vistrails.core.thumbnails import ThumbnailCache
from vistrails.gui.common_widgets import QSearchTreeWindow, QSearchTreeWidget, \
    QFileChooserToolButton, QDirectoryChooserToolButton
from vistrails.gui.utils import YES_BUTTON, NO_BUTTON, show_question, show_warning

import vistrails.core.system

##############################################################################

def bool_conv(st):
    if st == 'True':
        return True
    elif st == 'False':
        return False
    else:
        raise TypeError('Bogus value for bool_conv ' + str(st))

class QConfigurationTreeWidgetItem(QtGui.QTreeWidgetItem):

    def __init__(self, parent, obj, parent_obj, name, temp_obj, temp_parent_obj):
        lst = [name]
        t = type(obj)
        if t == bool:
            self._obj_type = bool_conv
        else:
            self._obj_type = t
        self._parent_obj = parent_obj
        self._temp_parent_obj = temp_parent_obj
        
        self._name = name
        if t == ConfigurationObject:
            lst.extend(['', ''])
            QtGui.QTreeWidgetItem.__init__(self, parent, lst)
            self.setFlags(self.flags() & ~(QtCore.Qt.ItemIsDragEnabled |
                                           QtCore.Qt.ItemIsSelectable ))
        elif t == tuple and obj[0] is None and isinstance(obj[1], type):
            self._obj_type = obj[1]
            lst.extend(['', obj[1].__name__])
            QtGui.QTreeWidgetItem.__init__(self, parent, lst)
            self.setFlags((self.flags() & ~QtCore.Qt.ItemIsDragEnabled) |
                          QtCore.Qt.ItemIsEditable)
        else:
            lst.extend([str(obj), type(obj).__name__])
            QtGui.QTreeWidgetItem.__init__(self, parent, lst)
            self.setFlags((self.flags() & ~QtCore.Qt.ItemIsDragEnabled) |
                          QtCore.Qt.ItemIsEditable)

    def change_value(self, new_value):
        if self._parent_obj:
            setattr(self._parent_obj, self._name, self._obj_type(new_value))
            setattr(self._temp_parent_obj, self._name, self._obj_type(new_value))

    def _get_name(self):
        return self._name
    name = property(_get_name)

class QConfigurationTreeWidgetItemDelegate(QtGui.QItemDelegate):
    """
    QConfigurationTreeWidgetItemDelegate allows a custom editor for
    each column of the QConfigurationTreeWidget    
    """
    
    def createEditor(self, parent, option, index):
        """ createEditor(parent: QWidget,
                         option: QStyleOptionViewItem,
                         index: QModelIndex) -> QWidget
        Return the editing widget depending on columns
        
        """
        # We only allow users to edit the  second column
        if index.column()==1:
            dataType = str(index.sibling(index.row(), 2).data())
            
            # Create the editor based on dataType
            if dataType=='int':
                editor = QtGui.QLineEdit(parent)
                editor.setValidator(QtGui.QIntValidator(parent))
            elif dataType=='bool':
                editor = QtGui.QComboBox(parent)
                editor.addItem('True')
                editor.addItem('False')
            else:
                editor = QtGui.QItemDelegate.createEditor(self, parent,
                                                          option, index)
            return editor            
        return None

    def setEditorData(self, editor, index):
        """ setEditorData(editor: QWidget, index: QModelIndex) -> None
        Set the editor to reflects data at index
        
        """
        if isinstance(editor, QtGui.QComboBox):
            editor.setCurrentIndex(editor.findText(index.data()))
        else:
            QtGui.QItemDelegate.setEditorData(self, editor, index)

    def setModelData(self, editor, model, index):
        """ setModelData(editor: QStringEdit,
                         model: QAbstractItemModel,
                         index: QModelIndex) -> None
        Set the text of the editor back to the item model
        
        """
        if isinstance(editor, QtGui.QComboBox):
            model.setData(index, editor.currentText())
        elif isinstance(editor, QtGui.QLineEdit):
            model.setData(index, editor.text())
        else:
            # Should never get here
            assert False
    

class QConfigurationTreeWidget(QSearchTreeWidget):

    def __init__(self, parent, persistent_config, temp_config):
        QSearchTreeWidget.__init__(self, parent)
        self.setMatchedFlags(QtCore.Qt.ItemIsEditable)
        self.setColumnCount(3)
        lst = ['Name', 'Value', 'Type']
        self.setHeaderLabels(lst)
        self.create_tree(persistent_config, temp_config)

    def create_tree(self, persistent_config, temp_config):
        def create_item(parent, obj, parent_obj, name, temp_obj, temp_parent_obj):
            item = QConfigurationTreeWidgetItem(parent, obj, parent_obj, 
                                                name, temp_obj, temp_parent_obj)
            if isinstance(obj, ConfigurationObject):
                for key in sorted(obj.keys()):
                    create_item(item, getattr(obj, key), obj, key, 
                                getattr(temp_obj, key), temp_obj)

        # disconnect() and clear() are here because create_tree might
        # also be called when an entirely new configuration object is set.

        self.disconnect(self, QtCore.SIGNAL('itemChanged(QTreeWidgetItem *, int)'),
                        self.change_configuration)
        self.clear()
        self._configuration = persistent_config
        self._temp_configuration = temp_config
        create_item(self, self._configuration, None, 'configuration', 
                    self._temp_configuration, None)

        self.expandAll()
        self.resizeColumnToContents(0)
        self.connect(self,
                     QtCore.SIGNAL('itemChanged(QTreeWidgetItem *, int)'),
                     self.change_configuration)

    def change_configuration(self, item, col):
        if item.flags() & QtCore.Qt.ItemIsEditable:
            new_value = self.indexFromItem(item, col).data()
            item.change_value(new_value)
            # option-specific code
            if item._name == 'dbDefault':
                # Update the state of the icons if changing between db and
                # file support
                dbState = getattr(get_vistrails_configuration(), 'dbDefault')
                if new_value != dbState:
                    from vistrails.gui.vistrails_window import _app
                    _app.setDBDefault(dbState)

            self.emit(QtCore.SIGNAL('configuration_changed'),
                      item, new_value)
        
class QConfigurationTreeWindow(QSearchTreeWindow):

    def __init__(self, parent, persistent_config, temp_config):
        self._configuration_object = persistent_config
        self._temp_configuration = temp_config
        QSearchTreeWindow.__init__(self, parent)

    def createTreeWidget(self):
        self.setWindowTitle('Configuration')
        treeWidget = QConfigurationTreeWidget(self, self._configuration_object,
                                              self._temp_configuration)
        
        # The delegate has to be around (self._delegate) to
        # work, else the instance will be clean by Python...
        self._delegate = QConfigurationTreeWidgetItemDelegate()
        treeWidget.setItemDelegate(self._delegate)
        return treeWidget


class QConfigurationWidget(QtGui.QWidget):

    def __init__(self, parent, persistent_config, temp_config):
        QtGui.QWidget.__init__(self, parent)
        layout = QtGui.QVBoxLayout(self)
        self.setLayout(layout)

        self._tree = QConfigurationTreeWindow(self, persistent_config,
                                              temp_config)
        lbl = QtGui.QLabel("Set configuration variables for VisTrails here.", self)
        layout.addWidget(lbl)
        layout.addWidget(self._tree)

    def configuration_changed(self, persistent_config, temp_config):
        self._tree.treeWidget.create_tree(persistent_config, temp_config)

class QConfigurationPane(QtGui.QWidget):
    def __init__(self, parent, persistent_config, temp_config, cat_fields):
        QtGui.QWidget.__init__(self, parent)
        layout = QtGui.QVBoxLayout()
        layout.setMargin(10)
        layout.setSpacing(2)
        self.setLayout(layout)
        self._configuration = persistent_config
        self._temp_configuration = temp_config
        self._temp_configuration.migrateTags = not self._configuration.migrateTags
        self._temp_configuration.dbDefault = not self._configuration.dbDefault

        self._fields = {}
        self._field_layouts = {}

        for category, fields in cat_fields:
            label = QtGui.QLabel(category + ":")
            layout.addWidget(label)
            self.process_fields(layout, fields)

        layout.addStretch(1)
                
        # need to determine different types

    def process_fields(self, layout, fields, parent_fields=[], prev_field=None, 
                       prefix=""):
        for field in fields:
            if isinstance(field, ConfigFieldParent):
                self.process_fields(layout, field.sub_fields, parent_fields, 
                                    prev_field, prefix="%s%s." % \
                                    (prefix, field.name))
            else:
                if field.depends_on is not None:
                    if field.depends_on not in parent_fields:
                        if field.depends_on == prev_field:
                            parent_fields.append(prev_field)
                        else:
                            raise Exception("Dependent field %s should "
                                            "follow parent." % field.name)
                    parent_idx = parent_fields.index(field.depends_on)
                    parent_fields = parent_fields[:parent_idx+1]
                    indent = 4 * len(parent_fields)
                else:
                    parent_fields = []
                    indent = 0
                sub_layout = self.add_field(layout, field, prefix=prefix,
                                            indent=indent)
                prev_field = field.name

    def add_field(self, base_layout, field, startup_only=False, prefix="",
                  indent=0):
        layout = QtGui.QHBoxLayout()
        layout.setMargin(0)
        layout.setSpacing(5)

        config_key = "%s%s" % (prefix, field.name)
        config_val = self._temp_configuration.get_deep_value(config_key)

        icon = self.style().standardIcon(QtGui.QStyle.SP_MessageBoxWarning)
        label = QtGui.QLabel()
        label.setPixmap(icon.pixmap(14,14))
        label.setToolTip("This option has been changed for this session")
        layout.addWidget(label, 0, QtCore.Qt.AlignTop)
            
        space = 0
        if (not startup_only and
            config_val == self._configuration.get_deep_value(config_key)):
            space = label.sizeHint().width() + layout.spacing() * (indent + 1)
            label.hide()
        elif indent > 0:
            space = layout.spacing() * indent

        if space > 0:
            spacer = QtGui.QSpacerItem(space, label.sizeHint().height())
            layout.insertSpacerItem(0, spacer)

        config_desc = find_simpledoc(config_key)
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
        self._field_layouts[config_key] = layout
        base_layout.addLayout(layout)

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
                inv_remap = {v: k for (k,v) in remap.iteritems()}
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
        config_val = self._configuration.get_deep_value(config_key)
        if config_val != self._temp_configuration.get_deep_value(config_key):
            retval = QtGui.QMessageBox.question(
                self, 
                "Change Setting",
                "This configuration value has been temporarily changed. "
                "If you change it, it will be changed permanently.  Do you "
                "want to continue?", 
                QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Ok,
                QtGui.QMessageBox.Ok)
            if retval != QtGui.QMessageBox.Ok:
                return
            # need to update hbox to reflect change...
            layout = self._field_layouts[config_key]
            leading_item = layout.itemAt(0)
            if isinstance(leading_item.widget(), QtGui.QLabel):
                label = leading_item.widget()
                spacer = QtGui.QSpacerItem(label.sizeHint().width() + \
                                           layout.spacing(),
                                           label.sizeHint().height())
                layout.insertSpacerItem(0, spacer)
            else:
                spacer = leading_item
                label = layout.itemAt(1).widget()
                spacer.changeSize(spacer.sizeHint().width() + \
                                  label.sizeHint().width() + layout.spacing(), 
                                  label.sizeHint().height())
            label.hide()
        # FIXME
        if False:
            QtGui.QMessageBox.information(
                self, "Change Setting",
                "You must restart VisTrails for this setting to take effect.")

        setattr(self._temp_configuration, config_key, val)
        setattr(self._configuration, config_key, val)

# TODO: Make sure this functionality (Move and Clear Cache) is preserved

class QThumbnailConfiguration(QtGui.QWidget):
    def thumbs_cache_directory_changed(self):
        """ thumbs_cache_changed(v: int) -> None
        
        """
        value = str(self._thumbs_cache_directory_edt.text())
        old_folder = self._configuration.thumbs.cacheDirectory
        if os.path.exists(value):
            self._configuration.thumbs.cacheDirectory = value
            self._temp_configuration.thumbs.cacheDirectory = value
            self.emit(QtCore.SIGNAL('configuration_changed'),
                      None, value)
            self._cache.move_cache_directory(old_folder,value)
        else:
            show_warning('VisTrails', 'The directory specified does not exist.')
            self._thumbs_cache_directory_edt.setText(old_folder)
                        
    def clear_thumbs_cache_pressed(self):
        """clear_thumbs_cache_pressed() -> None
        Will delete all files in thumbs.cacheDirectory if user clicks yes
        
        """
        res = show_question('VisTrails',
                  "All files in %s will be removed. Are you sure? " % (
                            self._temp_configuration.thumbs.cacheDirectory),
                  buttons = [YES_BUTTON,NO_BUTTON],
                  default = NO_BUTTON)
        if res == YES_BUTTON:
            self._cache.clear()
 

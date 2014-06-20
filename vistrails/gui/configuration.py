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

from vistrails.core import system

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
        # if this is a parent ConfigurationObject, do nothing
        if self._parent_obj and not self._obj_type == ConfigurationObject:
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

class QConfigurationWidgetItem(object):
    def __init__(self, key, field, callback_f):
        self.key = key
        self.field = field
        self.change_callback_f = callback_f
        self._desc = None

    def get_desc(self):
        if self._desc is not None:
            return self._desc

        options = self.get_widget_options()
        if "label" in options:
            return options["label"]
        return ""

    def set_desc(self, desc=None):
        self._desc = desc

    def get_label_text(self):
        return self.get_desc()

    def set_value(self, value, signal=True):
        raise NotImplementedError("Subclass needs to implement this method")

    def value_changed(self, value):
        self.change_callback_f(self, self.key, self.field, value)

    def get_widget_options(self):
        options = {}
        if self.field.widget_options is not None:
            options = self.field.widget_options
        return options

class QConfigurationCheckBox(QtGui.QCheckBox, QConfigurationWidgetItem):
    def __init__(self, key, field, callback_f, parent=None):
        QtGui.QCheckBox.__init__(self, parent)
        QConfigurationWidgetItem.__init__(self, key, field, callback_f)
        self.setText(self.get_desc())
        self.toggled.connect(self.value_changed)

    def set_value(self, value, signal=True):
        if not signal:
            self.toggled.disconnect(self.value_changed)
        self.setChecked(value)
        if not signal:
            self.toggled.connect(self.value_changed)

    def get_label_text(self):
        return ""

class QConfigurationLineEdit(QtGui.QLineEdit, QConfigurationWidgetItem):
    def __init__(self, key, field, callback_f, parent=None):
        QtGui.QLineEdit.__init__(self, parent)
        QConfigurationWidgetItem.__init__(self, key, field, callback_f)
        self.setMinimumWidth(200)
        self.editingFinished.connect(self.value_changed)

    def value_changed(self):
        QConfigurationWidgetItem.value_changed(self, self.text())

    def set_value(self, value, signal=True):
        if value is None:
            value = ""
        if not signal:
            self.editingFinished.disconnect(self.value_changed)
        self.setText(unicode(value))
        if not signal:
            self.editingFinished.connect(self.value_changed)

class QConfigurationLineEditButton(QtGui.QWidget, QConfigurationWidgetItem):
    def __init__(self, key, field, callback_f, button, parent=None):
        QtGui.QWidget.__init__(self, parent)
        QConfigurationWidgetItem.__init__(self, key, field, callback_f)

        layout = QtGui.QHBoxLayout()
        layout.setMargin(0)
        layout.setSpacing(5)

        self.line_edit = QtGui.QLineEdit()
        self.line_edit.setMinimumWidth(200)
        layout.addWidget(self.line_edit)

        if button is not None:
            layout.addWidget(button)
        self.setLayout(layout)

        self.line_edit.editingFinished.connect(self.value_changed)

    def add_button(self, button):
        self.layout().addWidget(button)

    def value_changed(self):
        QConfigurationWidgetItem.value_changed(self, self.line_edit.text())

    def set_value(self, value, signal=True):
        if value is None:
            value = ""
        if not signal:
            self.line_edit.editingFinished.disconnect(self.value_changed)
        self.line_edit.setText(unicode(value))
        if not signal:
            self.line_edit.editingFinished.connect(self.value_changed)

class QConfigurationPathEdit(QConfigurationLineEditButton):
    def __init__(self, key, field, callback_f, 
                 button_cls=QDirectoryChooserToolButton, parent=None):
        QConfigurationLineEditButton.__init__(self, key, field, callback_f,
                                              None, parent)
        button = button_cls(self, self.line_edit)
        self.add_button(button)

class QConfigurationThumbnailCache(QConfigurationLineEditButton):
    def __init__(self, key, field, callback_f, parent=None):
        button = QtGui.QPushButton("Clear...")
        button.setAutoDefault(False)
        button.clicked.connect(self.clear_clicked)
        QConfigurationLineEditButton.__init__(self, key, field, callback_f, 
                                              button, parent)

    def clear_clicked(self, checked=False):
        thumbnail_dir = system.get_vistrails_directory("thumbs.cacheDir")
        res = show_question('VisTrails',
                            ("All files in %s will be removed. "
                             "Are you sure? " % thumbnail_dir),
                            buttons = [YES_BUTTON,NO_BUTTON],
                            default = NO_BUTTON)
        if res == YES_BUTTON:
            ThumbnailCache.getInstance().clear()

class QConfigurationLabelButton(QtGui.QWidget, QConfigurationWidgetItem):
    def __init__(self, key, field, callback_f, label=None, button=None, 
                 parent=None):
        QtGui.QWidget.__init__(self, parent)
        QConfigurationWidgetItem.__init__(self, key, field, callback_f)

        layout = QtGui.QHBoxLayout()
        layout.setMargin(0)
        layout.setSpacing(5)

        if label is not None:
            self.label = label
            layout.addWidget(self.label)

        if button is not None:
            self.button = button
            layout.addWidget(self.button)
        self.setLayout(layout)

    def add_button(self, button):
        self.button = button
        self.layout().addWidget(self.button)

    def add_label(self, label):
        self.label = label
        self.layout().insertWidget(0, self.label)

    def set_value(self, value, signal=True):
        # nothing to do here
        pass

class QConfigurationLinuxHandler(QConfigurationLabelButton):
    def __init__(self, key, field, callback_f, parent=None):
        from vistrails.gui.application import linux_default_application_set
        if linux_default_application_set():
            label = QtGui.QLabel(".vt, .vtl handlers installed")
            button = None
        else:
            label = QtGui.QLabel(".vt, .vtl handlers not installed")
        button = QtGui.QPushButton("Install...")
        button.setAutoDefault(False)
        button.clicked.connect(self.install_clicked)
        QConfigurationLabelButton.__init__(self, key, field, callback_f, 
                                           label, button, parent)

    def install_clicked(self, checked=False):
        from vistrails.core.application import get_vistrails_application
        app = get_vistrails_application()
        if app.ask_update_default_application(False):
            self.label.setText(".vt, .vtl handlers installed")

class QConfigurationComboBox(QtGui.QComboBox, QConfigurationWidgetItem):
    def __init__(self, key, field, callback_f, parent=None):
        QtGui.QComboBox.__init__(self, parent)
        QConfigurationWidgetItem.__init__(self, key, field, callback_f)

        inv_remap = None
        options = self.get_widget_options()
        if "allowed_values" in options:
            values = options["allowed_values"]
            if "remap" in options:
                remap = options["remap"]
                inv_remap = dict((v, k) for (k, v) in remap.iteritems())
                entries = [remap[v] for v in values]
            else:
                entries = values
            for entry in entries:
                self.addItem(entry)

        self.currentIndexChanged[int].connect(self.value_changed)

    def set_value(self, value, signal=True):
        options = self.get_widget_options()
        if not signal:
            self.currentIndexChanged[int].disconnect(self.value_changed)
        if value is not None and "allowed_values" in options:
            if "remap" in options:
                remap = options["remap"]
                cur_text = remap[value]
            else:
                cur_text = value
            self.setCurrentIndex(self.findText(cur_text))
        else:
            self.setCurrentIndex(-1)
        if not signal:
            self.currentIndexChanged[int].connect(self.value_changed)

class QConfigurationPane(QtGui.QWidget):
    def __init__(self, parent, persistent_config, temp_config, cat_fields):
        QtGui.QWidget.__init__(self, parent)
        layout = QtGui.QFormLayout()
        layout.setMargin(10)
        layout.setSpacing(4)
        self.setLayout(layout)
        self._configuration = persistent_config
        self._temp_configuration = temp_config

        self._fields = {}
        self._field_layouts = {}

        for category, fields in cat_fields:
            self.process_fields(layout, fields, category)
            spacer_widget = QtGui.QWidget()
            spacer_layout = QtGui.QVBoxLayout()
            spacer_layout.setMargin(0)
            spacer_layout.addSpacing(15)
            spacer_widget.setLayout(spacer_layout)
            layout.addRow("", spacer_widget)

    def process_fields(self, layout, fields, category, parent_fields=[], 
                       prev_field=None, prefix=""):
        for field in fields:
            if isinstance(field, ConfigFieldParent):
                self.process_fields(layout, field.sub_fields, category,
                                    parent_fields, prev_field,
                                    prefix="%s%s." % (prefix, field.name))
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
                self.add_field(layout, field, category, prefix=prefix, 
                               indent=indent)
                prev_field = field.name
                category = ""

    def add_field(self, base_layout, field, category="", startup_only=False,
                  prefix="", indent=0):
        label_widget = QtGui.QWidget()
        label_layout = QtGui.QHBoxLayout()
        label_layout.setMargin(0)
        label_layout.setSpacing(5)
        label_widget.setLayout(label_layout)

        config_key = "%s%s" % (prefix, field.name)
        if self._temp_configuration.is_unset(config_key):
            config_val = None
        else:
            config_val = self._temp_configuration.get_deep_value(config_key)
        if self._configuration.is_unset(config_key):
            perm_config_val = None
        else:
            perm_config_val = self._configuration.get_deep_value(config_key)

        icon = self.style().standardIcon(QtGui.QStyle.SP_MessageBoxWarning)
        label = QtGui.QLabel()
        label.setPixmap(icon.pixmap(14,14))
        label.setToolTip("This option has been changed for this session")
        label_layout.addWidget(label, 0, QtCore.Qt.AlignCenter)
            
        space = 0
        if not startup_only and config_val == perm_config_val:
            space = (label.sizeHint().width() +
                     label_layout.spacing() * (indent + 1))
            label.hide()
        elif indent > 0:
            space = label_layout.spacing() * indent

        if space > 0:
            spacer = QtGui.QSpacerItem(space, label.sizeHint().height())
            label_layout.insertSpacerItem(0, spacer)

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
            widget = QConfigurationComboBox(config_key, field,
                                            self.field_changed)
        elif widget_type == "lineedit":
            widget = QConfigurationLineEdit(config_key, field,
                                            self.field_changed)
        elif widget_type == "pathedit":
            widget = QConfigurationPathEdit(config_key, field,
                                            self.field_changed)
        elif widget_type == "thumbnailcache":
            widget = QConfigurationThumbnailCache(config_key, field,
                                                  self.field_changed)
        elif widget_type == "linuxext":
            widget = QConfigurationLinuxHandler(config_key, field,
                                                self.field_changed)
        else:
            config_val = bool(config_val)
            widget = QConfigurationCheckBox(config_key, field,
                                            self.field_changed)
        widget.set_value(config_val, False)

        label_text = widget.get_label_text()
        if not label_text and category:
            label_text = category
        if label_text:
            label = QtGui.QLabel(label_text + ":")
            label_layout.addWidget(label)

        base_layout.addRow(label_widget, widget)
        self._field_layouts[config_key] = (base_layout, base_layout.rowCount())

    def field_changed(self, widget, config_key, field, val):
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
                # revert widget's value
                widget.set_value(self._temp_configuration.get_deep_value(
                    config_key))
                return
            # need to update hbox to reflect change...
            form_layout, row = self._field_layouts[config_key]
            label_layout = form_layout.itemAt(row, QtGui.QFormLayout.LabelRole).widget().layout()
            leading_item = label_layout.itemAt(0)
            if isinstance(leading_item.widget(), QtGui.QLabel):
                label = leading_item.widget()
                spacer = QtGui.QSpacerItem(label.sizeHint().width() + \
                                           label_layout.spacing(),
                                           label.sizeHint().height())
                label_layout.insertSpacerItem(0, spacer)
            else:
                spacer = leading_item
                label = label_layout.itemAt(1).widget()
                spacer.changeSize((spacer.sizeHint().width() +
                                   label.sizeHint().width() +
                                   label_layout.spacing()),
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


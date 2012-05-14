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

"""Widgets to display/edit configuration objects."""
import os
import os.path
from PyQt4 import QtGui, QtCore

from core import debug
from core.configuration import ConfigurationObject, \
                               get_vistrails_configuration

from core.thumbnails import ThumbnailCache
from gui.common_widgets import QSearchTreeWindow, QSearchTreeWidget
from gui.utils import YES_BUTTON, NO_BUTTON, show_question, show_warning

import core.system

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
        lst = QtCore.QStringList(name)
        t = type(obj)
        if t == bool:
            self._obj_type = bool_conv
        else:
            self._obj_type = t
        self._parent_obj = parent_obj
        self._temp_parent_obj = temp_parent_obj
        
        self._name = name
        if t == ConfigurationObject:
            lst << '' << ''
            QtGui.QTreeWidgetItem.__init__(self, parent, lst)
            self.setFlags(self.flags() & ~(QtCore.Qt.ItemIsDragEnabled |
                                           QtCore.Qt.ItemIsSelectable ))
        elif t == tuple and obj[0] is None and type(obj[1]) == type:
            self._obj_type = obj[1]
            lst << '' << obj[1].__name__
            QtGui.QTreeWidget.__init__(self, parent, lst)
            self.setFlags((self.flags() & ~QtCore.Qt.ItemIsDragEnabled) |
                          QtCore.Qt.ItemIsEditable)
        else:
            lst << str(obj) << type(obj).__name__
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
            dataType = str(index.sibling(index.row(), 2).data().toString())
            
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
        if type(editor)==QtGui.QComboBox:           
            editor.setCurrentIndex(editor.findText(index.data().toString()))
        else:
            QtGui.QItemDelegate.setEditorData(self, editor, index)

    def setModelData(self, editor, model, index):
        """ setModelData(editor: QStringEdit,
                         model: QAbstractItemModel,
                         index: QModelIndex) -> None
        Set the text of the editor back to the item model
        
        """
        if type(editor)==QtGui.QComboBox:
            model.setData(index, QtCore.QVariant(editor.currentText()))
        elif type(editor) == QtGui.QLineEdit:
            model.setData(index, QtCore.QVariant(editor.text()))
        else:
            # Should never get here
            assert False
    

class QConfigurationTreeWidget(QSearchTreeWidget):

    def __init__(self, parent, persistent_config, temp_config):
        QSearchTreeWidget.__init__(self, parent)
        self.setMatchedFlags(QtCore.Qt.ItemIsEditable)
        self.setColumnCount(3)
        lst = QtCore.QStringList()
        lst << 'Name'
        lst << 'Value'
        lst << 'Type'
        self.setHeaderLabels(lst)
        self.create_tree(persistent_config, temp_config)

    def create_tree(self, persistent_config, temp_config):
        def create_item(parent, obj, parent_obj, name, temp_obj, temp_parent_obj):
            item = QConfigurationTreeWidgetItem(parent, obj, parent_obj, 
                                                name, temp_obj, temp_parent_obj)
            if type(obj) == ConfigurationObject:
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
            new_value = self.indexFromItem(item, col).data().toString()
            item.change_value(new_value)
            # option-specific code
            if item._name == 'dbDefault':
                # Update the state of the icons if changing between db and
                # file support
                print "dbDefault", new_value 
                dbState = getattr(get_vistrails_configuration(), 'dbDefault')
                if new_value != dbState:
                    from gui.vistrails_window import _app
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

    def __init__(self, parent, persistent_config, temp_config, status_bar):
        QtGui.QWidget.__init__(self, parent)
        layout = QtGui.QVBoxLayout(self)
        self.setLayout(layout)
        self._status_bar = status_bar

        self._tree = QConfigurationTreeWindow(self, persistent_config,
                                              temp_config)
        lbl = QtGui.QLabel("Set configuration variables for VisTrails here.", self)
        layout.addWidget(lbl)
        layout.addWidget(self._tree)

    def configuration_changed(self, persistent_config, temp_config):
        self._tree.treeWidget.create_tree(persistent_config, temp_config)

class QGeneralConfiguration(QtGui.QWidget):
    """
    QGeneralConfiguration is a widget for showing a few general preferences
    that can be set with widgets.

    """
    def __init__(self, parent, persistent_config, temp_config):
        """
        QGeneralConfiguration(parent: QWidget, 
        configuration_object: ConfigurationObject) -> None

        """
        QtGui.QWidget.__init__(self, parent)
        layout = QtGui.QVBoxLayout()
        layout.setMargin(10)
        layout.setSpacing(10)
        self.setLayout(layout)
        self._configuration = None
        self._temp_configuration = None
        self.create_default_widgets(self,layout)
        self.create_other_widgets(self,layout)
        self.update_state(persistent_config, temp_config)
        self.connect_default_signals()
        self.connect_other_signals()
        
    def connect_default_signals(self):
        
        # We need to connect only one of the radio buttons signal because
        # only one of them will be checked at a time
        
        #Auto save signals
        self.connect(self._autosave_cb,
                     QtCore.SIGNAL('stateChanged(int)'),
                     self.temp_autosave_changed)
        self.connect(self._autosave_always,
                     QtCore.SIGNAL('toggled(bool)'),
                     self.autosave_changed)
        
        #Read and Write to database signals
        self.connect(self._db_connect_cb,
                     QtCore.SIGNAL('stateChanged(int)'),
                     self.temp_db_connect_changed)
        self.connect(self._db_connect_always,
                     QtCore.SIGNAL('toggled(bool)'),
                     self.db_connect_changed)
        
        #Caching signals
        self.connect(self._use_cache_cb,
                     QtCore.SIGNAL('stateChanged(int)'),
                     self.temp_use_cache_changed)
        self.connect(self._use_cache_always,
                     QtCore.SIGNAL('toggled(bool)'),
                     self.use_cache_changed)
        
        #Other signals
        self.connect(self._splash_cb,
                     QtCore.SIGNAL('stateChanged(int)'),
                     self.splash_changed)
        self.connect(self._maximize_cb,
                     QtCore.SIGNAL('stateChanged(int)'),
                     self.maximize_changed)
        self.connect(self._multi_head_cb,
                     QtCore.SIGNAL('stateChanged(int)'),
                     self.multi_head_changed)

    def connect_other_signals(self):
        if core.system.systemType in ['Darwin']:
            self.connect(self._use_metal_style_cb,
                         QtCore.SIGNAL('stateChanged(int)'),
                         self.metalstyle_changed)
        
    def create_default_widgets(self, parent, layout):
        """create_default_widgets(parent: QWidget, layout: QLayout)-> None
        Creates default widgets in parent
        
        """
        #Auto save
        autosave_gb = QtGui.QGroupBox(parent)
        autosave_gb.setTitle('Automatically save vistrails')
        glayout = QtGui.QHBoxLayout()
        parent._autosave_always = QtGui.QRadioButton("Always")
        parent._autosave_never = QtGui.QRadioButton("Never")
        parent._autosave_cb = QtGui.QCheckBox("Yes (for this session only)")
        glayout.addWidget(parent._autosave_always)
        glayout.addWidget(parent._autosave_never)
        glayout.addWidget(parent._autosave_cb)
        autosave_gb.setLayout(glayout)
        layout.addWidget(autosave_gb)

        #Read and Write to database
        db_connect_gb = QtGui.QGroupBox(parent)
        db_connect_gb.setTitle('Read/Write to database by default')
        glayout = QtGui.QHBoxLayout()
        parent._db_connect_always = QtGui.QRadioButton("Always")
        parent._db_connect_never = QtGui.QRadioButton("Never")
        parent._db_connect_cb = QtGui.QCheckBox("Yes (for this session only)")
        glayout.addWidget(parent._db_connect_always)
        glayout.addWidget(parent._db_connect_never)
        glayout.addWidget(parent._db_connect_cb)
        db_connect_gb.setLayout(glayout)
        layout.addWidget(db_connect_gb)
        
        #Caching
        use_cache_gb = QtGui.QGroupBox(parent)
        use_cache_gb.setTitle('Cache execution results')
        glayout = QtGui.QHBoxLayout()
        parent._use_cache_always = QtGui.QRadioButton("Always")
        parent._use_cache_never = QtGui.QRadioButton("Never")
        parent._use_cache_cb = QtGui.QCheckBox("Yes (for this session only)")
        glayout.addWidget(parent._use_cache_always)
        glayout.addWidget(parent._use_cache_never)
        glayout.addWidget(parent._use_cache_cb)
        use_cache_gb.setLayout(glayout)
        layout.addWidget(use_cache_gb)

        parent._splash_cb = QtGui.QCheckBox(parent)
        parent._splash_cb.setText('Show splash dialog on startup*')
        layout.addWidget(parent._splash_cb)

        parent._maximize_cb = QtGui.QCheckBox(parent)
        parent._maximize_cb.setText('Maximize windows on startup*')
        layout.addWidget(parent._maximize_cb)

        parent._multi_head_cb = QtGui.QCheckBox(parent)
        parent._multi_head_cb.setText('Use multiple displays on startup*')
        layout.addWidget(parent._multi_head_cb)
        

    def create_other_widgets(self, parent, layout):
        """create_other_widgets(parent: QWidget, layout: QLayout)-> None
        Creates system specific widgets in parent
        
        """
        if core.system.systemType in ['Darwin']:
            parent._use_metal_style_cb = QtGui.QCheckBox(parent)
            parent._use_metal_style_cb.setText('Use brushed metal appearance*')
            layout.addWidget(parent._use_metal_style_cb)
        
        layout.addStretch()
        label = QtGui.QLabel("* It requires restarting VisTrails for these \
changes to take effect")
        layout.addWidget(label)
        layout.addStretch()

    def update_state(self, persistent_config, temp_config):
        """ update_state(configuration: VistrailConfiguration) -> None
        
        Update the dialog state based on a new configuration
        """
        
        self._configuration = persistent_config
        self._temp_configuration = temp_config

        #Autosave
        if self._configuration.has('autosave'):
            if self._configuration.autosave == True:
                self._autosave_always.setChecked(True)
                self._autosave_never.setChecked(False)
                self._autosave_cb.setText("No (for this session only)")
                self._autosave_cb.setChecked(
                                     not self._temp_configuration.autosave)
                    
            else:
                self._autosave_always.setChecked(False)
                self._autosave_never.setChecked(True)
                self._autosave_cb.setText("Yes (for this session only)")        
                self._autosave_cb.setChecked(self._temp_configuration.autosave)
        
        #Read/Write from DB by default   
        if self._configuration.has('dbDefault'):
            if self._configuration.dbDefault == True:
                self._db_connect_always.setChecked(True)
                self._db_connect_never.setChecked(False)
                self._db_connect_cb.setText("No (for this session only)")
                self._db_connect_cb.setChecked(
                                        not self._temp_configuration.dbDefault)
                    
            else:
                self._db_connect_always.setChecked(False)
                self._db_connect_never.setChecked(True)
                self._db_connect_cb.setText("Yes (for this session only)")        
                self._db_connect_cb.setChecked(
                                        self._temp_configuration.dbDefault)
        #Caching 
        if self._configuration.has('useCache'):
            if self._configuration.useCache == True:
                self._use_cache_always.setChecked(True)
                self._use_cache_never.setChecked(False)
                self._use_cache_cb.setText("No (for this session only)")
                self._use_cache_cb.setChecked(
                                        not self._temp_configuration.useCache)
                    
            else:
                self._use_cache_always.setChecked(False)
                self._use_cache_never.setChecked(True)
                self._use_cache_cb.setText("Yes (for this session only)")        
                self._use_cache_cb.setChecked(self._temp_configuration.useCache)
        
        if self._configuration.has('showSplash'):
            self._splash_cb.setChecked(self._configuration.showSplash)
        if self._configuration.has('maximizeWindows'):
            self._maximize_cb.setChecked(self._configuration.maximizeWindows)
        if self._configuration.has('multiHeads'):
            self._multi_head_cb.setChecked(self._configuration.multiHeads)
        #other widgets
        self.update_other_state()
        
    def update_other_state(self):
        """ update_state(configuration: VistrailConfiguration) -> None
        
        Update the dialog state based on a new configuration
        """
        if core.system.systemType in ['Darwin']:
            self._use_metal_style_cb.setChecked(
                self._configuration.check('useMacBrushedMetalStyle'))
            
    def autosave_changed(self, on):
        """ autosave_changed(on: bool) -> None
        
        """
        debug.log("auto_save_changed")
        if self._autosave_always.isChecked() == True:
            value = True
            self._autosave_cb.setText("No (for this session only)")
            self._autosave_cb.setChecked(False)
        else:
            value = False
            self._autosave_cb.setText("Yes (for this session only)")
            self._autosave_cb.setChecked(False)
            
        self._configuration.autosave = value
        self._temp_configuration.autosave = value
        self.emit(QtCore.SIGNAL('configuration_changed'),
                  None, bool(on))
        
    def temp_autosave_changed(self, on):
        """ temp_autosave_changed(on: int) -> None
        
        """
        debug.log("temp_auto_save_changed")
        value = bool(on)
        if self._autosave_cb.text() == "No (for this session only)":
            value = not bool(on)
        
        self._temp_configuration.autosave = value

    def db_connect_changed(self, on):
        """ db_connect_changed(on: int) -> None

        """
        if self._db_connect_always.isChecked() == True:
            value = True
            self._db_connect_cb.setText("No (for this session only)")
            self._db_connect_cb.setChecked(False)
        else:
            value = False
            self._db_connect_cb.setText("Yes (for this session only)")
            self._db_connect_cb.setChecked(False)
            
        self._configuration.dbDefault = value
        self._temp_configuration.dbDefault = value
        self.emit(QtCore.SIGNAL('configuration_changed'),
                  None, bool(on))
        
    def temp_db_connect_changed(self, on):
        """ temp_db_connect_changed(on: int) -> None

        """
        debug.log("temp_db_connect_changed")
        value = bool(on)
        if self._db_connect_cb.text() == "No (for this session only)":
            value = not bool(on)
        
        self._temp_configuration.dbDefault = value

    def use_cache_changed(self, on):
        """ use_cache_changed(on: int) -> None

        """
        if self._use_cache_always.isChecked() == True:
            value = True
            self._use_cache_cb.setText("No (for this session only)")
            self._use_cache_cb.setChecked(False)
        else:
            value = False
            self._use_cache_cb.setText("Yes (for this session only)")
            self._use_cache_cb.setChecked(False)
            
        self._configuration.useCache = value
        self._temp_configuration.useCache = value
        self.emit(QtCore.SIGNAL('configuration_changed'),
                  None, bool(on))
        
    def temp_use_cache_changed(self, on):
        """ temp_use_cache_changed(on: int) -> None

        """
        debug.log("temp_use_cache_changed")
        value = bool(on)
        if self._use_cache_cb.text() == "No (for this session only)":
            value = not bool(on)
        
        self._temp_configuration.useCache = value

    def splash_changed(self, on):
        """ splash_changed(on: int) -> None

        """
        self._configuration.showSplash = bool(on)
        self.emit(QtCore.SIGNAL('configuration_changed'),
                  None, bool(on))

    def maximize_changed(self, on):
        """ maximize_changed(on: int) -> None

        """
        self._configuration.maximizeWindows = bool(on)
        self.emit(QtCore.SIGNAL('configuration_changed'),
                  None, bool(on))

    def multi_head_changed(self, on):
        """ multi_head_changed(on: int) -> None

        """
        self._configuration.multiHeads = bool(on)
        self.emit(QtCore.SIGNAL('configuration_changed'),
                  None, bool(on))

    def metalstyle_changed(self, on):
        """ metalstyle_changed(on: int) -> None
        
        """
        self._configuration.useMacBrushedMetalStyle = bool(on)
        self.emit(QtCore.SIGNAL('configuration_changed'),
                  None, bool(on))

class QThumbnailConfiguration(QtGui.QWidget):
    """
    QThumbnailConfiguration is a widget for showing a few thumbnail related 
    preferences that can be set with widgets.

    """
    def __init__(self, parent, persistent_config, temp_config):
        """
        QThumbnailConfiguration(parent: QWidget, 
        configuration_object: ConfigurationObject) -> None

        """
        QtGui.QWidget.__init__(self, parent)
        self._configuration = None
        self._temp_configuration = None
        self._cache = ThumbnailCache.getInstance()
        self.create_widgets()
        self.update_state(persistent_config, temp_config)
        self.connect_signals()
    
    def create_widgets(self):
        """create_widgets()-> None
        Creates widgets
        
        """
        layout = QtGui.QVBoxLayout()
        layout.setMargin(10)
        layout.setSpacing(10)
        self.setLayout(layout)
        
        #Auto save
        autosave_gb = QtGui.QGroupBox(self)
        autosave_gb.setTitle('Automatically save thumbnails in .vt files')
        glayout = QtGui.QHBoxLayout()
        self._autosave_always = QtGui.QRadioButton("Always")
        self._autosave_never = QtGui.QRadioButton("Never")
        self._autosave_cb = QtGui.QCheckBox("Yes (for this session only)")
        glayout.addWidget(self._autosave_always)
        glayout.addWidget(self._autosave_never)
        glayout.addWidget(self._autosave_cb)
        autosave_gb.setLayout(glayout)
        layout.addWidget(autosave_gb)
        
        #Thumbnails for tagged versions only
        tagsonly_gb = QtGui.QGroupBox(self)
        tagsonly_gb.setTitle('Keep thumbnails of tagged versions only')
        glayout = QtGui.QHBoxLayout()
        self._tagsonly_always = QtGui.QRadioButton("Always")
        self._tagsonly_never = QtGui.QRadioButton("Never")
        self._tagsonly_cb = QtGui.QCheckBox("Yes (for this session only)")
        glayout.addWidget(self._tagsonly_always)
        glayout.addWidget(self._tagsonly_never)
        glayout.addWidget(self._tagsonly_cb)
        tagsonly_gb.setLayout(glayout)
        layout.addWidget(tagsonly_gb)
        
        #Show thumbnails on mouser hover events
        mouse_hover_gb = QtGui.QGroupBox(self)
        mouse_hover_gb.setTitle('Show thumbnails as tooltips on mouse \
hovering tree nodes')
        glayout = QtGui.QHBoxLayout()
        self._mouse_hover_always = QtGui.QRadioButton("Always")
        self._mouse_hover_never = QtGui.QRadioButton("Never")
        self._mouse_hover_cb = QtGui.QCheckBox("Yes (for this session only)")
        glayout.addWidget(self._mouse_hover_always)
        glayout.addWidget(self._mouse_hover_never)
        glayout.addWidget(self._mouse_hover_cb)
        mouse_hover_gb.setLayout(glayout)
        layout.addWidget(mouse_hover_gb)
        
        hlayout = QtGui.QHBoxLayout()
        cache_label = QtGui.QLabel(self)
        cache_label.setText('Limit thumbnail cache size to ')
        
        self._thumbs_cache_sb = QtGui.QSpinBox(self)
        self._thumbs_cache_sb.setRange(10,128)
        self._thumbs_cache_sb.setValue(10)
        self._thumbs_cache_sb.setSuffix('MB')
        self._thumbs_cache_sb.stepBy(5)
        
        self._clear_thumbs_cache_btn = QtGui.QPushButton(self)
        self._clear_thumbs_cache_btn.setText("Clear Cache")
        
        hlayout.addWidget(cache_label)
        hlayout.addWidget(self._thumbs_cache_sb)
        hlayout.addWidget(self._clear_thumbs_cache_btn)
        layout.addLayout(hlayout)
        
        hlayout = QtGui.QHBoxLayout()
        cache_label2 = QtGui.QLabel(self)
        cache_label2.setText("Cache Directory:")
        self._thumbs_cache_directory_edt = QtGui.QLineEdit(self)
        self._thumbs_cache_directory_btn = QtGui.QPushButton("...", self)
        hlayout.addWidget(cache_label2)
        hlayout.addWidget(self._thumbs_cache_directory_edt)
        hlayout.addWidget(self._thumbs_cache_directory_btn)
        layout.addLayout(hlayout)
        layout.addStretch()

    def connect_signals(self):
        # We need to connect only one of the radio buttons signal because
        # only one of them will be checked at a time
        
        #Auto save signals
        self.connect(self._autosave_always,
                     QtCore.SIGNAL('toggled(bool)'),
                     self.autosave_changed)
        self.connect(self._autosave_cb,
                     QtCore.SIGNAL('toggled(bool)'),
                     self.temp_autosave_changed)
        
        #Thumbnails for tagged versions only signals
        self.connect(self._tagsonly_always,
                     QtCore.SIGNAL('toggled(bool)'),
                     self.tagsonly_changed)
        self.connect(self._tagsonly_cb,
                     QtCore.SIGNAL('stateChanged(int)'),
                     self.temp_tagsonly_changed)
        
        #Show thumbnails on mouser hover events signals
        self.connect(self._mouse_hover_always,
                     QtCore.SIGNAL('toggled(bool)'),
                     self.mouse_hover_changed)
        self.connect(self._mouse_hover_cb,
                     QtCore.SIGNAL('stateChanged(int)'),
                     self.temp_mouse_hover_changed)
        
        #Other widget signals
        self.connect(self._thumbs_cache_sb,
                     QtCore.SIGNAL('valueChanged(int)'),
                     self.thumbs_cache_changed)
        self.connect(self._clear_thumbs_cache_btn,
                     QtCore.SIGNAL('clicked()'),
                     self.clear_thumbs_cache_pressed)
        self.connect(self._thumbs_cache_directory_edt,
                     QtCore.SIGNAL('editingFinished()'),
                     self.thumbs_cache_directory_changed)
        self.connect(self._thumbs_cache_directory_btn,
                     QtCore.SIGNAL('clicked()'),
                     self.show_directory_chooser)
        
    def update_state(self, persistent_config, temp_config):
        """ update_state(persistent_config, temp_config: VistrailConfiguration) 
                                     -> None
        Update the dialog state based on a new configuration
        
        """
        self._configuration = persistent_config
        self._temp_configuration = temp_config
        #Auto save
        if self._configuration.has('thumbs'):
            if self._configuration.thumbs.has('autoSave'):
                if self._configuration.autosave == True:
                    self._autosave_always.setChecked(True)
                    self._autosave_never.setChecked(False)
                    self._autosave_cb.setText("No (for this session only)")
                    self._autosave_cb.setChecked(
                                not self._temp_configuration.thumbs.autoSave)
                    
                else:
                    self._autosave_always.setChecked(False)
                    self._autosave_never.setChecked(True)
                    self._autosave_cb.setText("Yes (for this session only)")        
                    self._autosave_cb.setChecked(
                                self._temp_configuration.thumbs.autoSave)
            #Thumbnails for tagged versions only    
            if self._configuration.thumbs.has('tagsOnly'):
                if self._configuration.thumbs.tagsOnly == True:
                    self._tagsonly_always.setChecked(True)
                    self._tagsonly_never.setChecked(False)
                    self._tagsonly_cb.setText("No (for this session only)")
                    self._tagsonly_cb.setChecked(
                                not self._temp_configuration.thumbs.tagsOnly)
                    
                else:
                    self._tagsonly_always.setChecked(False)
                    self._tagsonly_never.setChecked(True)
                    self._tagsonly_cb.setText("Yes (for this session only)")        
                    self._tagsonly_cb.setChecked(
                                    self._temp_configuration.thumbs.tagsOnly)
            #Show thumbnails on mouser hover events
            if self._configuration.thumbs.has('mouseHover'):
                if self._configuration.thumbs.mouseHover == True:
                    self._mouse_hover_always.setChecked(True)
                    self._mouse_hover_never.setChecked(False)
                    self._mouse_hover_cb.setText("No (for this session only)")
                    self._mouse_hover_cb.setChecked(
                                not self._temp_configuration.thumbs.mouseHover)
                    
                else:
                    self._mouse_hover_always.setChecked(False)
                    self._mouse_hover_never.setChecked(True)
                    self._mouse_hover_cb.setText("Yes (for this session only)")        
                    self._mouse_hover_cb.setChecked(
                                self._temp_configuration.thumbs.mouseHover)
            # Other widgets
            if self._configuration.thumbs.has('cacheSize'):
                self._thumbs_cache_sb.setValue(
                    self._configuration.thumbs.cacheSize)
            if self._configuration.thumbs.has('cacheDirectory'):
                self._thumbs_cache_directory_edt.setText(
                    self._configuration.thumbs.cacheDirectory)
                
    def autosave_changed(self, on):
        """ autosave_changed(on: bool) -> None
        
        """
        debug.log("thumbs_auto_save_changed")
        if self._autosave_always.isChecked() == True:
            value = True
            self._autosave_cb.setText("No (for this session only)")
            self._autosave_cb.setChecked(False)
        else:
            value = False
            self._autosave_cb.setText("Yes (for this session only)")
            self._autosave_cb.setChecked(False)
            
        self._configuration.thumbs.autoSave = value
        self._temp_configuration.thumbs.autoSave = value
        self.emit(QtCore.SIGNAL('configuration_changed'),
                  None, bool(on))
        
    def temp_autosave_changed(self, on):
        """ temp_autosave_changed(on: int) -> None
        
        """
        debug.log("thumbs_temp_auto_save_changed")
        value = bool(on)
        if self._autosave_cb.text() == "No (for this session only)":
            value = not bool(on)
        
        self._temp_configuration.thumbs.autoSave = value

    def tagsonly_changed(self, on):
        """ tagsonly_changed(on: bool) -> None
        
        """
        debug.log("thumbs_tagsonly_changed")
        if self._tagsonly_always.isChecked() == True:
            value = True
            self._tagsonly_cb.setText("No (for this session only)")
            self._tagsonly_cb.setChecked(False)
        else:
            value = False
            self._tagsonly_cb.setText("Yes (for this session only)")
            self._tagsonly_cb.setChecked(False)
            
        self._configuration.thumbs.tagsOnly = value
        self._temp_configuration.thumbs.tagsOnly = value
        
        self.emit(QtCore.SIGNAL('configuration_changed'),
                  None, bool(on))
        
    def temp_tagsonly_changed(self, on):
        """ temp_tagsonly_changed(on: int) -> None
        
        """
        debug.log("thumbs_temp_tagsonly_changed")
        value = bool(on)
        if self._tagsonly_cb.text() == "No (for this session only)":
            value = not bool(on)
        
        self._temp_configuration.thumbs.tagsOnly = value
        
    def mouse_hover_changed(self, on):
        """ mouse_hover_changed(on: bool) -> None
        
        """
        debug.log("thumbs_mouse_hover_changed")
        if self._mouse_hover_always.isChecked() == True:
            value = True
            self._mouse_hover_cb.setText("No (for this session only)")
            self._mouse_hover_cb.setChecked(False)
        else:
            value = False
            self._mouse_hover_cb.setText("Yes (for this session only)")
            self._mouse_hover_cb.setChecked(False)
            
        self._configuration.thumbs.mouseHover = value
        self._temp_configuration.thumbs.mouseHover = value
        
        self.emit(QtCore.SIGNAL('configuration_changed'),
                  None, bool(on))
        
    def temp_mouse_hover_changed(self, on):
        """ temp_mouse_hover_changed(on: int) -> None
        
        """
        debug.log("thumbs_temp_mouse_hover_changed")
        value = bool(on)
        if self._mouse_hover_cb.text() == "No (for this session only)":
            value = not bool(on)
        
        self._temp_configuration.thumbs.mouseHover = value
        
    def thumbs_cache_changed(self, v):
        """ thumbs_cache_changed(v: int) -> None
        
        """
        self._configuration.thumbs.cacheSize = v
        self._temp_configuration.thumbs.cacheSize = v
        self.emit(QtCore.SIGNAL('configuration_changed'),
                  None, v)
        
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
            
    def show_directory_chooser(self):
        """show_directory_chooser() -> None
        Shows a dialog for choosing a directory 
        
        """
        dir = QtGui.QFileDialog.getExistingDirectory(
                  self,
                  "Choose a new directory for storing thumbnail chache files",
                  "",
                  QtGui.QFileDialog.ShowDirsOnly)
        if not dir.isEmpty():
            self._thumbs_cache_directory_edt.setText(dir)
            self.thumbs_cache_directory_changed()
            
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
 
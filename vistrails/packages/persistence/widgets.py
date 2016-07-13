###############################################################################
##
## Copyright (C) 2014-2016, New York University.
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
##  - Neither the name of the New York University nor the names of its
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
from __future__ import division

from PyQt4 import QtCore, QtGui
import os
import re
import uuid

from vistrails.core.modules.basic_modules import Path
from vistrails.gui.common_widgets import QSearchBox
from vistrails.gui.modules.constant_configuration import ConstantWidgetMixin
from vistrails.gui.modules.module_configure import StandardModuleConfigurationWidget

from db_utils import DatabaseAccessSingleton
from identifiers import identifier as persistence_pkg
import repo

class IntegerWrapper(object):
    def __init__(self, idx):
        self.idx = idx

class PersistentRefModelSingleton(object):
    def __new__(self, *args, **kw):
        if PersistentRefModel._instance is None:
            obj = PersistentRefModel(*args, **kw)
            PersistentRefModel._instance = obj
        return PersistentRefModel._instance

class PersistentRefModel(QtCore.QAbstractItemModel):

    _instance = None

    # 2013-09-03 18:57:53.133000
    _DATE_FORMAT = re.compile(r'^(?P<y>[0-9]{4})-'
                              r'(?P<m>[0-9]{2})-'
                              r'(?P<d>[0-9]{2}) '
                              r'(?P<H>[0-9]{2}):'
                              r'(?P<M>[0-9]{2}):'
                              r'(?P<S>[0-9]{2}).'
                              r'(?P<ms>[0-9]+)$')

    cols = {0: "name",
            1: "type",
            2: "tags",
            3: "user",
            4: "date_created",
            5: "date_modified",
            6: "id",
            7: "version",
            8: "content_hash",
            9: "signature"}
    idxs = dict((v,k) for (k,v) in cols.iteritems())
    headers = {"id": "ID",
               "name": "Name",
               "tags": "Tags",
               "user": "User",
               "date_created": "Date Created",
               "date_modified": "Date Modified",
               "content_hash": "Content Hash",
               "version": "Version",
               "signature": "Signature",
               "type": "Type"}

    def __init__(self, parent=None):
        QtCore.QAbstractItemModel.__init__(self, parent)

        self.db_access = DatabaseAccessSingleton()
        self.db_access.set_model(self)
        rows = self.db_access.read_database(
            [c[1] for c in sorted(self.cols.iteritems())])
        rows = map(self.fix_dates, rows)

        self.id_lists = {}
        for ref in rows:
            if ref[self.idxs['id']] not in self.id_lists:
                self.id_lists[ref[self.idxs['id']]] = []
            self.id_lists[ref[self.idxs['id']]].append(ref)

        self.id_lists_keys = self.id_lists.keys()

        self.integer_wrappers = {}

    @staticmethod
    def fix_dates(row):
        row = list(row)
        for c in ('date_created', 'date_modified'):
            c = PersistentRefModel.idxs[c]
            m = PersistentRefModel._DATE_FORMAT.match(row[c])
            if m is not None:
                row[c] = '{y}-{m}-{d} {H}:{M}'.format(**m.groupdict())
        return tuple(row)

    def rowCount(self, parent=QtCore.QModelIndex()):
        if not parent.isValid():
            # print 'rowCount:', len(self.id_lists_keys)
            return len(self.id_lists_keys)
        # print 'parentValid rowCount:', \
        #     len(self.id_lists[self.id_lists_keys[parent.row()]])
        return len(self.id_lists[self.id_lists_keys[parent.row()]])
 
    def columnCount(self, parent=QtCore.QModelIndex()):
        # print 'columnCount:', len(self.headers)
        return len(self.headers)
    
    def hasChildren(self, parent=QtCore.QModelIndex()):
        # print 'hasChildren:'
        if not parent.isValid():
            # print '  True'
            return True
        else:
            # print '  PARENT:', parent.row(), parent.column(), \
            #     parent.internalPointer()
            if not parent.parent().isValid():
                # print '  TRUE'
                return True
        # print '  False'
        return False

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.DisplayRole:
            return None
        if section in self.cols:
            return self.headers[self.cols[section]]
        return None
    
    def data(self, index, role):
        if not index.isValid() or role != QtCore.Qt.DisplayRole:
            return None
        # if index.parent().isValid():
        #     print 'data', index.row(), index.column(), index.parent().row()
        if index.parent().isValid():
            # have a child node
            # print 'got child node!', index.parent().row()
            id_list = self.id_lists[self.id_lists_keys[index.parent().row()]]
            data = id_list[index.row()]
        else:
            # have a parent node    
            id_list = self.id_lists[self.id_lists_keys[index.row()]]
            data = id_list[0]
            # want to have the earliest created date and latest modified date
            if index.column() == self.idxs['date_created']:
                dates = [l[index.column()] for l in id_list]
                return min(dates)
            if index.column() == self.idxs['date_modified']:
                dates = [l[index.column()] for l in id_list]
                return max(dates)
            if index.column() == self.idxs['version'] or \
                    index.column() == self.idxs['signature'] or \
                    index.column() == self.idxs['content_hash'] or \
                    index.column() == self.idxs['user']:
                return None

        if index.column() < len(data):
            return data[index.column()]
        return None
    
    def parent(self, index):
        # print 'calling parent() method'
        if index.isValid():
            # print '  index is valid', index.row(), index.column()
            if index.internalPointer():
                parent_item = index.internalPointer().idx
                # print '  parent_item:', parent_item
                return self.createIndex(parent_item, 0, None)
#             else:
#                 # print '  internalPointer is not valid'
#         else:
#             # print 'index not valid for parent call'
        return QtCore.QModelIndex()

    def index(self, row, column, parent):
        # print 'index:', row, column
        if not parent.isValid():
            if len(self.id_lists_keys) > row:
                # print '  no parent item'
                return self.createIndex(row, column, None)
        else:
            # print '  **** parent_item', row, column, parent.row()
            if len(self.id_lists[self.id_lists_keys[parent.row()]]) > row:
                # print '  ++++ creating index'
                # !!! internalPointer is a weakref in PyQt !!!
                if parent.row() not in self.integer_wrappers:
                    integer_wrapper = IntegerWrapper(parent.row())
                    self.integer_wrappers[parent.row()] = integer_wrapper
                else:
                    integer_wrapper = self.integer_wrappers[parent.row()]
                # print '  ---- created parent wrapper'
                return self.createIndex(row, column, integer_wrapper)
        return QtCore.QModelIndex()

    def sort(self, column, order=QtCore.Qt.AscendingOrder):
        self.emit(QtCore.SIGNAL('layoutAboutToBeChanged()'))
        if column == -1:
            return
        self.id_lists_keys.sort(key=lambda x: self.id_lists[x][0][column], 
                                reverse=(order==QtCore.Qt.AscendingOrder))
        self.emit(QtCore.SIGNAL('layoutChanged()'))

    def find_row(self, id, version=None):
        if id in self.id_lists:
            i = self.id_lists_keys.index(id)
            if version is not None:
                for j, data in enumerate(self.id_lists[id]):
                    if data[self.idxs['version']] == version:
                        if i not in self.integer_wrappers:
                            integer_wrapper = IntegerWrapper(i)
                            self.integer_wrappers[i] = integer_wrapper
                        else:
                            integer_wrapper = self.integer_wrappers[i]
                        return self.createIndex(j, 0, integer_wrapper)
            return self.createIndex(i, 0, 0)
#             for i, id in enumerate(self.id_lists_keys):
            
#             if version is not None:
#                 for data in enumerate(self.id_lists[id]):
#                     if
#         for i, data in enumerate(self.id_lists):
#             if data[self.idxs['id']] == id and \
#                     (not version or data[self.idxs['version']] == version):
#                 return self.createIndex(i, 0, 0)
        return QtCore.QModelIndex()

    def add_data(self, value_dict):
        id = value_dict['id']
        value_list = []
        for _, c in sorted(self.cols.iteritems()):
            if c in value_dict:
                value_list.append(str(value_dict[c]))
            else:
                value_list.append(None)
        if id not in self.id_lists:
            self.id_lists[id] = []
            self.id_lists_keys.append(id)
        self.id_lists[id].append(self.fix_dates(value_list))
        self.reset()

    def remove_data(self, where_dict):
        id = where_dict['id']
        version = where_dict.get('version', None)
        if version is not None:
            for idx, value_tuple in enumerate(self.id_lists[id]):
                if value_tuple[self.idxs['version']] == version:
                    del self.id_lists[id][idx]
                    break
        else:
            path_type = self.id_lists[id][0][self.idxs['type']]
            for idx, key_id in enumerate(self.id_lists_keys):
                if key_id == id:
                    del self.id_lists_keys[idx]
                    break
            del self.id_lists[id]
        self.reset()

class PersistentRefView(QtGui.QTreeView):
    def __init__(self, path_type=None, parent=None):
        QtGui.QTreeView.__init__(self, parent)
        self.my_model = PersistentRefModelSingleton()
        print 'my_model:', id(self.my_model)
        proxy_model = QtGui.QSortFilterProxyModel(self)
        proxy_model.setSourceModel(self.my_model)
        proxy_model.setFilterKeyColumn(-1)
        self.setModel(proxy_model)
        self.set_visibility(path_type)

        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.setSortingEnabled(True)
        self.current_id = None
        self.current_version = None

        for i in xrange(self.my_model.columnCount()):
            self.resizeColumnToContents(i)

    def set_visibility(self, path_type=None):
        if path_type == "blob":
            self.header().hideSection(self.my_model.idxs["type"])
            for i, key in enumerate(self.my_model.id_lists_keys):
                id_list = self.my_model.id_lists[key]
                if id_list[0][self.my_model.idxs["type"]] != "blob":
                    # if i not in self.my_model.file_idxs:
                    print "setting index", i, "to hidden"
                    my_index = self.my_model.createIndex(i, 0, None)
                    index = self.model().mapFromSource(my_index)
                    self.setRowHidden(index.row(), QtCore.QModelIndex(), True)
        elif path_type == "tree":
            self.header().hideSection(self.my_model.idxs["type"])
            for i, key in enumerate(self.my_model.id_lists_keys):
                id_list = self.my_model.id_lists[key]
                if id_list[0][self.my_model.idxs["type"]] != "tree":
                    # if i not in self.my_model.dir_idxs:
                    print "setting index", i, "to hidden"
                    my_index = self.my_model.createIndex(i, 0, None)
                    index = self.model().mapFromSource(my_index)
                    self.setRowHidden(index.row(), QtCore.QModelIndex(), True)
        
    def set_selection(self):
        if self.current_id:
            my_index = self.my_model.find_row(self.current_id, 
                                              self.current_version)
            
            index = self.model().mapFromSource(my_index)
            if index.isValid():
                print 'checking internalPointer', my_index.internalPointer()
                if my_index.internalPointer():
                    my_expand_index = \
                        self.my_model.createIndex(
                        my_index.internalPointer().idx, 0, 0)
                    expand_index = self.model().mapFromSource(my_expand_index)
                    self.expand(expand_index)
                self.selectionModel().select(
                    index, QtGui.QItemSelectionModel.ClearAndSelect | \
                        QtGui.QItemSelectionModel.Rows)
                return True
        return False

    def set_id(self, id):
        self.current_id = id
        return self.set_selection()

    def set_version(self, version):
        self.current_version = version
        return self.set_selection()

    def get_id(self):
        sf_index = self.selectionModel().selectedRows()[0]
        index = self.model().mapToSource(sf_index)
        if index.internalPointer():
            paridx = index.internalPointer().idx
            id_list = \
                self.my_model.id_lists[self.my_model.id_lists_keys[paridx]]
            id = id_list[index.row()][self.my_model.idxs['id']]
        else:
            id_list = \
                self.my_model.id_lists[self.my_model.id_lists_keys[index.row()]]
            id = id_list[0][self.my_model.idxs['id']]
        return str(id)

    def get_version(self):
        sf_index = self.selectionModel().selectedRows()[0]
        index = self.model().mapToSource(sf_index)
        if index.internalPointer():
            paridx = index.internalPointer().idx
            id_list = \
                self.my_model.id_lists[self.my_model.id_lists_keys[paridx]]
            version = id_list[index.row()][self.my_model.idxs['version']]
            return str(version)        
        return None
        
    def get_info(self):
        return self.get_info_list()[0]

    def get_info_list(self):
        s_indexes = self.selectionModel().selectedRows()
        info_list = []
        for s_idx in s_indexes:
            index = self.model().mapToSource(s_idx)
            if index.internalPointer():
                paridx = index.internalPointer().idx
                id_list = \
                    self.my_model.id_lists[self.my_model.id_lists_keys[paridx]]
                info = id_list[index.row()]
                version = str(info[self.my_model.idxs['version']])
            else:
                id_list = self.my_model.id_lists[ \
                    self.my_model.id_lists_keys[index.row()]]
                info = id_list[0]
                version = None
            info_list.append((str(info[self.my_model.idxs['id']]),
                              version,
                              str(info[self.my_model.idxs['name']]),
                              str(info[self.my_model.idxs['tags']])))
        return info_list

class PersistentRefDialog(QtGui.QDialog):
    def __init__(self, param, parent=None):
        QtGui.QDialog.__init__(self, parent)
        # two tabs, one for starting from managed, one for local file
        # options are set accordingly
        # uuid assigned when options are set, either new or existing
        # don't compute uuid for local file that hasn't been run
        # need PersistentReference parameter
        # allow user to pass contents in to PersistentRef
        self.setWindowTitle("Configure Persistent Reference...")

        self.settings = {'ref_id': None,
                         'ref_version': None,
                         'local_path': None,
                         'versioning': False,
                         'local_read_priority': True,
                         'write_back': True}

        self.current_file = ""
        db_file = "/vistrails/managed/files.db"

        layout = QtGui.QVBoxLayout()
        managed_group = QtGui.QGroupBox("Persistent Data")
        managed_layout = QtGui.QVBoxLayout()
        search = QSearchBox(False, False)

        def keyPressEvent(obj, e):
            print "got to key press event", e.key()
            if e.key() in (QtCore.Qt.Key_Return,QtCore.Qt.Key_Enter):
                if obj.currentText():
                    obj.emit(QtCore.SIGNAL('executeSearch(QString)'),  
                             obj.searchEdit.currentText())
                else:
                    obj.emit(QtCore.SIGNAL('resetSearch()'))
            QtGui.QComboBox.keyPressEvent(obj, e)

        print 'keyPressEvent:', search.searchEdit.keyPressEvent
        search.searchEdit.keyPressEvent = keyPressEvent
        print 'keyPressEvent:', search.searchEdit.keyPressEvent
        self.connect(search, QtCore.SIGNAL('executeSearch(QString)'),
                     self.search_string)
        self.connect(search, QtCore.SIGNAL('resetSearch()'),
                     self.reset_search)
        managed_layout.addWidget(search)
        self.table = PersistentRefView(db_file, self)
        managed_layout.addWidget(self.table)
        managed_group.setLayout(managed_layout)
        layout.addWidget(managed_group)

        local_group = QtGui.QGroupBox("Local Data")
        local_layout = QtGui.QHBoxLayout()
        self.filename_edit = QtGui.QLineEdit()
        local_layout.addWidget(self.filename_edit)

        filename_button = QtGui.QToolButton()
        filename_button.setIcon(
            QtGui.QIcon(filename_button.style().standardPixmap(
                    QtGui.QStyle.SP_DirOpenIcon)))
        filename_button.setIconSize(QtCore.QSize(12,12))
        filename_button.connect(filename_button,
                                QtCore.SIGNAL('clicked()'),
                                self.choose_file)
        local_layout.addWidget(filename_button)
        local_group.setLayout(local_layout)
        layout.addWidget(local_group)

        pref_layout = QtGui.QHBoxLayout()
        version_group = QtGui.QGroupBox("Versioning")
        version_layout = QtGui.QVBoxLayout()
        version_off = QtGui.QRadioButton("Create New ID")
        version_layout.addWidget(version_off)
        version_on = QtGui.QRadioButton("Create New Version")
        version_layout.addWidget(version_on)
        version_group.setLayout(version_layout)
        pref_layout.addWidget(version_group)

        r_priority_group = QtGui.QGroupBox("Read Priority")
        r_priority_layout = QtGui.QVBoxLayout()
        r_priority_off = QtGui.QRadioButton("Local")
        r_priority_layout.addWidget(r_priority_off)
        r_priority_on = QtGui.QRadioButton("Persistent Store")
        r_priority_layout.addWidget(r_priority_on)
        r_priority_group.setLayout(r_priority_layout)
        pref_layout.addWidget(r_priority_group)
        
        w_priority_group = QtGui.QGroupBox("Write Priority")
        w_priority_layout = QtGui.QVBoxLayout()
        w_priority_off = QtGui.QRadioButton("Local")
        w_priority_layout.addWidget(w_priority_off)
        w_priority_on = QtGui.QRadioButton("Persistent Store")
        w_priority_layout.addWidget(w_priority_on)
        w_priority_group.setLayout(w_priority_layout)
        pref_layout.addWidget(w_priority_group)
        layout.addLayout(pref_layout)

        button_layout = QtGui.QHBoxLayout()
        button_layout.setDirection(QtGui.QBoxLayout.RightToLeft)
        button_layout.setAlignment(QtCore.Qt.AlignRight)
        ok_button = QtGui.QPushButton("OK")
        ok_button.setFixedWidth(100)
        self.connect(ok_button, QtCore.SIGNAL('clicked()'), self.close)
        button_layout.addWidget(ok_button)
        cancel_button = QtGui.QPushButton("Cancel")
        cancel_button.setFixedWidth(100)
        self.connect(cancel_button, QtCore.SIGNAL('clicked()'), self.cancel)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def close(self):
        self.done(QtGui.QDialog.Accepted)

    def cancel(self):
        self.done(QtGui.QDialog.Rejected)

    def choose_file(self):
        chosen_file = \
            QtGui.QFileDialog.getOpenFileName(self,
                                              'Use File...',
                                              self.current_file,
                                              'All files (*.*)')
        if chosen_file:
            self.current_file = chosen_file
            self.filename_edit.setText(self.current_file)
    
    def build_table(self):
        # read sql table from sqlite3 
        # display table
        pass
    
    def select_file(self):
        # present file dialog and allow user to choose file
        # compute file hash
        # if content exists in persistent store, ask to reuse 
        # (or set reuse checkbox)
        # set use_local checkbox to True
        # don't transfer until execution?
        # create uuid for file
        pass

    def select_remote(self):
        # present table of data with search box
        # each data has name, id, user, date, tags, etc.
        # if user selects, check use_local checkbox to False
        # store local is False, too?
        # don't transfer file until execution?
        # populate uuid
        pass


    # starting choice: local file or find existing managed file?
    # allow branch off of existing managed file -- ie no longer a
    # version of the initial file?
    
    # === options ===
    # overwrite managed on change
    # overwrite local on change
    # local is authoritative
    # keep local copy -- need to allow where to store

class PathChooserLayout(QtGui.QHBoxLayout):
    def __init__(self, is_dir=False, par_widget=None, parent=None):
        # QtGui.QWidget.__init__(self, parent)
        QtGui.QHBoxLayout.__init__(self, parent)
        self.par_widget = par_widget
        # layout = QtGui.QHBoxLayout()
        self.pathname_edit = QtGui.QLineEdit()
        self.addWidget(self.pathname_edit)

        pathname_button = QtGui.QToolButton()
        pathname_button.setIcon(
            QtGui.QIcon(pathname_button.style().standardPixmap(
                    QtGui.QStyle.SP_DirOpenIcon)))
        pathname_button.setIconSize(QtCore.QSize(12,12))
        pathname_button.connect(pathname_button,
                                QtCore.SIGNAL('clicked()'),
                                self.choose_path)
        self.addWidget(pathname_button)
        # layout.setContentsMargins(1,1,1,1)
        # self.setLayout(layout)
        self.is_dir = is_dir
        
    def choose_path(self):
        if self.is_dir:
            chosen_path = \
                QtGui.QFileDialog.getExistingDirectory(self.par_widget,
                                                       'Use Directory...',
                                                       self.pathname_edit.text())
        else:
            chosen_path = \
                QtGui.QFileDialog.getOpenFileName(self.par_widget,
                                                  'Use File...',
                                                  self.pathname_edit.text(),
                                                  'All files (*.*)')

        if chosen_path and chosen_path:
            self.pathname_edit.setText(chosen_path)
            self.emit(QtCore.SIGNAL('pathnameChanged()'))

    def get_path(self):
        return str(self.pathname_edit.text())

    def set_path(self, pathname):
        if pathname:
            self.pathname_edit.setText(pathname)
        else:
            self.pathname_edit.clear()

class PersistentRefViewSearch(QtGui.QGroupBox):
    def __init__(self, path_type=None, parent=None):
        QtGui.QGroupBox.__init__(self, parent)
        self.build_gui(path_type)

    def build_gui(self, path_type):
        layout = QtGui.QVBoxLayout()
        self.search_ref = QSearchBox(False, False)

        self.connect(self.search_ref, 
                     QtCore.SIGNAL('executeSearch(QString)'),
                     self.search_string)
        self.connect(self.search_ref, 
                     QtCore.SIGNAL('resetSearch()'),
                     self.reset_search)

        layout.addWidget(self.search_ref)
        self.ref_widget = PersistentRefView(path_type, self)
        layout.addWidget(self.ref_widget)
        layout.setMargin(0)
        self.setLayout(layout)

    def search_string(self, str):
        self.ref_widget.model().setFilterWildcard(str)

    def reset_search(self):
        self.ref_widget.model().setFilterWildcard('')
        self.ref_widget.model().invalidate()
    

class PersistentPathConfiguration(StandardModuleConfigurationWidget):
    def __init__(self, module, controller, parent=None, 
                 is_input=None, path_type=None):
        StandardModuleConfigurationWidget.__init__(self, module, controller, 
                                                   parent)

        # set title
        if module.has_annotation_with_key('__desc__'):
            label = module.get_annotation_by_key('__desc__').value.strip()
            title = '%s (%s) Module Configuration' % (label, module.name)
        else:
            title = '%s Module Configuration' % module.name
        self.setWindowTitle(title)

        self.build_gui(is_input, path_type)
        self.set_values()

    def sizeHint(self):
        return QtCore.QSize(800, 600)

    def build_gui(self, is_input, path_type):
        self.current_path = ""

        layout = QtGui.QVBoxLayout()
#         layout.setMargin(0)
#         layout.setSpacing(0)

        if not is_input:
            self.managed_change = \
                QtGui.QRadioButton("Always Create New Reference")
            layout.addWidget(self.managed_change)
            self.connect(self.managed_change, QtCore.SIGNAL("toggled(bool)"),
                         self.managed_toggle)

        else:
            self.managed_change = None

        self.managed_new = QtGui.QRadioButton("Create New Reference")
        self.connect(self.managed_new, QtCore.SIGNAL("toggled(bool)"),
                     self.new_toggle)
        layout.addWidget(self.managed_new)
        self.new_group = QtGui.QGroupBox()
        new_layout = QtGui.QGridLayout()
        self.new_file = None
        if is_input:
            new_layout.addWidget(QtGui.QLabel("Path:"), 0, 0)
            self.new_file = self.get_chooser_layout()
            if hasattr(self.new_file, 'pathname_edit'):
                self.connect(self.new_file.pathname_edit,
                             QtCore.SIGNAL("textChanged(QString)"),
                             self.stateChange)
            new_layout.addLayout(self.new_file, 0, 1)
            self.connect(self.new_file, QtCore.SIGNAL("pathnameChanged()"),
                         self.new_file_changed)
        new_layout.addWidget(QtGui.QLabel("Name:"), 1, 0)
        self.name_edit = QtGui.QLineEdit()
        self.connect(self.name_edit, QtCore.SIGNAL("textChanged(QString)"),
                     self.stateChange)
        new_layout.addWidget(self.name_edit, 1, 1)
        new_layout.addWidget(QtGui.QLabel("Tags:"), 2, 0)
        self.tags_edit = QtGui.QLineEdit()
        self.connect(self.tags_edit, QtCore.SIGNAL("textChanged(QString)"),
                     self.stateChange)
        new_layout.addWidget(self.tags_edit, 2, 1)
        self.new_group.setLayout(new_layout)
        layout.addWidget(self.new_group)

        self.managed_existing = QtGui.QRadioButton("Use Existing Reference")
        self.connect(self.managed_existing, QtCore.SIGNAL("toggled(bool)"),
                     self.existing_toggle)
        layout.addWidget(self.managed_existing)

        # self.existing_group = QtGui.QGroupBox()
        # existing_layout = QtGui.QVBoxLayout()
        # self.search_ref = QSearchBox(False, False)

        # self.connect(self.search_ref, 
        #              QtCore.SIGNAL('executeSearch(QString)'),
        #              self.search_string)
        # self.connect(self.search_ref, 
        #              QtCore.SIGNAL('resetSearch()'),
        #              self.reset_search)

        # existing_layout.addWidget(self.search_ref)
        # self.ref_widget = PersistentRefView(path_type, self)
        # existing_layout.addWidget(self.ref_widget)
        # self.existing_group.setLayout(existing_layout)
        self.existing_group = PersistentRefViewSearch(path_type)
        self.ref_widget = self.existing_group.ref_widget
        self.connect(self.ref_widget,
                     QtCore.SIGNAL("clicked(QModelIndex)"),
                     self.ref_changed)
        layout.addWidget(self.existing_group)

        self.keep_local = QtGui.QCheckBox("Keep Local Version")
        layout.addWidget(self.keep_local)
        self.connect(self.keep_local, QtCore.SIGNAL("toggled(bool)"),
                     self.local_toggle)
        self.local_group = QtGui.QGroupBox()
        local_layout = QtGui.QGridLayout()
        self.local_path = self.get_chooser_layout()
        if hasattr(self.local_path, 'pathname_edit'):
            self.connect(self.local_path.pathname_edit,
                         QtCore.SIGNAL("textChanged(QString)"),
                         self.stateChange)
        local_layout.addLayout(self.local_path,0,0,1,2)

        self.r_priority_local = QtGui.QCheckBox("Read From Local Path")
        local_layout.addWidget(self.r_priority_local,1,0)
        self.write_managed_checkbox = QtGui.QCheckBox("Write To Local Path")
        self.connect(self.write_managed_checkbox, QtCore.SIGNAL("toggled(bool)"),
                     self.stateChange)
        local_layout.addWidget(self.write_managed_checkbox,1,1)
        self.local_group.setLayout(local_layout)
        layout.addWidget(self.local_group)

        if is_input:
            self.r_priority_local.setEnabled(True)
            self.write_managed_checkbox.setEnabled(False)
        else:
            self.r_priority_local.setEnabled(False)
            self.write_managed_checkbox.setEnabled(True)

        button_layout = QtGui.QHBoxLayout()
        button_layout.setDirection(QtGui.QBoxLayout.RightToLeft)
        button_layout.setAlignment(QtCore.Qt.AlignRight)
        self.saveButton = QtGui.QPushButton("Save")
        self.saveButton.setFixedWidth(100)
        self.connect(self.saveButton, QtCore.SIGNAL('clicked(bool)'),
                     self.saveTriggered)
        button_layout.addWidget(self.saveButton)
        self.resetButton = QtGui.QPushButton("Reset")
        self.resetButton.setFixedWidth(100)
        self.connect(self.resetButton, QtCore.SIGNAL('clicked()'),
                     self.resetTriggered)
        button_layout.addWidget(self.resetButton)
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def saveTriggered(self, checked = False):
        self.get_values()
        self.saveButton.setEnabled(False)
        self.resetButton.setEnabled(False)
        self.state_changed = False
        self.emit(QtCore.SIGNAL('doneConfigure'), self.module.id)
        
    def closeEvent(self, event):
        self.askToSaveChanges()
        event.accept()
                
    def resetTriggered(self):
        self.set_values()
        self.setUpdatesEnabled(True)
        self.state_changed = False
        self.saveButton.setEnabled(False)
        self.resetButton.setEnabled(False)
        
    def stateChange(self, checked = False, old = None):
        if not self.state_changed:
            self.state_changed = True
            self.saveButton.setEnabled(True)
            self.resetButton.setEnabled(True)
    
    def managed_toggle(self, checked):
        self.stateChange()
        self.new_group.setEnabled(not checked)
        self.existing_group.setEnabled(not checked)

    def new_toggle(self, checked):
        self.stateChange()
        self.new_group.setEnabled(checked)
        self.existing_group.setEnabled(not checked)
        if not checked and self.keep_local.isChecked():
            self.keep_local.setChecked(False)

    def existing_toggle(self, checked):
        self.stateChange()
        self.existing_group.setEnabled(checked)
        self.new_group.setEnabled(not checked)

    def local_toggle(self, checked):
        self.stateChange()
        self.local_group.setEnabled(checked)

    def new_file_changed(self):
        self.stateChange()
        new_file = str(self.new_file.get_path())
        if new_file:
            base_name = os.path.basename(new_file)
        else:
            base_name = ''
        self.name_edit.setText(base_name)
        self.keep_local.setChecked(True)
        self.local_path.set_path(new_file)
        self.r_priority_local.setChecked(True)
        self.write_managed_checkbox.setChecked(False)

    def ref_changed(self, index):
        self.stateChange()
        if self.keep_local.isChecked():
            self.keep_local.setChecked(False)

    def set_values(self):
        from vistrails.core.modules.module_registry import get_module_registry
        reg = get_module_registry()
        PersistentRef = \
            reg.get_descriptor_by_name(persistence_pkg, 'PersistentRef').module

        def func_to_bool(function):
            try:
                value = function.parameters[0].strValue
            except IndexError:
                return False
            if value and value == 'True':
                return True

        ref_exists = False
        self.existing_ref = None
        local_path = None
        local_read = None
        local_write = None
        for function in self.module.functions:
            if function.name == 'ref':
                self.existing_ref = PersistentRef.translate_to_python(
                    function.parameters[0].strValue)
                self.ref_widget.set_id(self.existing_ref.id)
                ref_exists = \
                    self.ref_widget.set_version(self.existing_ref.version)
                self.existing_ref._exists = ref_exists
                print 'ref_exists:', ref_exists, self.existing_ref.id, \
                    self.existing_ref.version
            elif function.name == 'value':
                if self.new_file:
                    self.new_file.set_path(function.parameters[0].strValue)
            elif function.name == 'localPath':
                local_path = Path.translate_to_python(
                    function.parameters[0].strValue).name
            elif function.name == 'readLocal':
                local_read = func_to_bool(function)
            elif function.name == 'writeLocal':
                local_write = func_to_bool(function)

        if ref_exists:
            self.managed_existing.setChecked(True)
            self.existing_toggle(True)
        elif self.managed_change and (not self.existing_ref or \
                                          not self.existing_ref.id):
            self.managed_change.setChecked(True)
            self.managed_toggle(True)
        else:
            self.managed_new.setChecked(True)
            self.new_toggle(True)
            if self.existing_ref:
                self.name_edit.setText(self.existing_ref.name)
                self.tags_edit.setText(self.existing_ref.tags)
        
        if self.existing_ref:
            if self.existing_ref.local_path:
                self.keep_local.setChecked(True)
                self.local_toggle(True)
            else:
                self.keep_local.setChecked(False)
                self.local_toggle(False)
            self.local_path.set_path(self.existing_ref.local_path)
            self.r_priority_local.setChecked(self.existing_ref.local_read)
            self.write_managed_checkbox.setChecked(
                self.existing_ref.local_writeback)
        else:
            self.keep_local.setChecked(False)
            self.local_toggle(False)

        if local_path is not None:
            if local_path:
                self.keep_local.setChecked(True)
                self.local_toggle(True)
            else:
                self.keep_local.setChecked(False)
                self.local_toggle(False)
            self.local_path.set_path(local_path)
        if local_read is not None:
            self.r_priority_local.setChecked(local_read)
        if local_write is not None:
            self.write_managed_checkbox.setChecked(local_write)
        self.saveButton.setEnabled(False)
        self.resetButton.setEnabled(False)
        self.state_changed = False

    def get_values(self):
        from vistrails.core.modules.module_registry import get_module_registry
        reg = get_module_registry()
        PersistentRef = \
            reg.get_descriptor_by_name(persistence_pkg, 'PersistentRef').module

        functions = []
        if self.new_file and self.new_file.get_path() and \
                self.managed_new.isChecked():
        # if self.new_file and self.new_file.get_path():
            functions.append(('value', [self.new_file.get_path()]))
        else:
            functions.append(('value', None))
            pass
        ref = PersistentRef()
        if self.managed_new.isChecked():
            if self.existing_ref and not self.existing_ref._exists:
                ref.id = self.existing_ref.id
                ref.version = self.existing_ref.version
            else:
                ref.id = str(uuid.uuid1())
                ref.version = None
            # endif
            ref.name = str(self.name_edit.text())
            ref.tags = str(self.tags_edit.text())
        elif self.managed_existing.isChecked():
            (ref.id, ref.version, ref.name, ref.tags) = \
                self.ref_widget.get_info()
        if self.keep_local.isChecked():
            functions.append(('localPath', [self.local_path.get_path()]))
            functions.append(('readLocal', 
                              [str(self.r_priority_local.isChecked())]))
            functions.append(('writeLocal',
                              [str(self.write_managed_checkbox.isChecked())]))
#             ref.local_path = self.local_path.get_path()
#             ref.local_read = self.r_priority_local.isChecked()
#             ref.local_writeback = self.write_managed_checkbox.isChecked()
        else:
            ref.local_path = None
            # functions.append(('localPath', None))
            functions.append(('readLocal', None))
            functions.append(('writeLocal', None))
            pass
        functions.append(('ref', [PersistentRef.translate_to_string(ref)]))
        self.controller.update_functions(self.module, functions)

class PersistentInputPathConfiguration(PersistentPathConfiguration):
    def __init__(self, module, controller, parent=None, path_type=None):
        PersistentPathConfiguration.__init__(self, module, controller, parent,
                                          True, path_type)
        
class PersistentOutputPathConfiguration(PersistentPathConfiguration):
    def __init__(self, module, controller, parent=None, path_type=None):
        PersistentPathConfiguration.__init__(self, module, controller, parent,
                                          False, path_type)

class PersistentRefInlineWidget(QtGui.QWidget, ConstantWidgetMixin):
    contentsChanged = QtCore.pyqtSignal(tuple)
    def __init__(self, param, parent=None):
        self.param = param
        self.strValue = param.strValue
        contentsType = param.type
        QtGui.QWidget.__init__(self, parent)
        ConstantWidgetMixin.__init__(self, param.strValue)
        layout = QtGui.QHBoxLayout()
        # FIXME Use a greyed QLineEdit?
        # layout.addWidget(QtGui.QLabel("File Info:"))
        button = QtGui.QPushButton("Configure")
        button.setMaximumWidth(100)
        self.connect(button, QtCore.SIGNAL('clicked()'), self.run_dialog)
        layout.addWidget(button)
        layout.setMargin(5)
        layout.setSpacing(5)
        self.setLayout(layout)
        
    def run_dialog(self):
        dialog = PersistentRefDialog(self.param)
        if dialog.exec_() == QtGui.QDialog.Accepted:
            self.setContents("test")
            #use same translate call?, False)

    def contents(self):
        return self.strValue

    def setContents(self, strValue, silent=True):
        self.strValue = strValue
        if not silent:
            self.update_parent()

class PersistentInputFileConfiguration(PersistentInputPathConfiguration):
    def __init__(self, module, controller, parent=None):
        PersistentInputPathConfiguration.__init__(self, module, controller, 
                                               parent, "blob")
    def get_chooser_layout(self):
        return PathChooserLayout(False, self)
    
class PersistentInputDirConfiguration(PersistentInputPathConfiguration):
    def __init__(self, module, controller, parent=None):
        PersistentInputPathConfiguration.__init__(self, module, controller, 
                                               parent, "tree")

    def get_chooser_layout(self):
        return PathChooserLayout(True, self)

class PersistentOutputFileConfiguration(PersistentOutputPathConfiguration):
    def __init__(self, module, controller, parent=None):
        PersistentOutputPathConfiguration.__init__(self, module, controller, 
                                               parent, "blob")

    def get_chooser_layout(self):
        return PathChooserLayout(False, self)

class PersistentOutputDirConfiguration(PersistentOutputPathConfiguration):
    def __init__(self, module, controller, parent=None):
        PersistentOutputPathConfiguration.__init__(self, module, controller, 
                                               parent, "tree")

    def get_chooser_layout(self):
        return PathChooserLayout(True, self)
    
class PersistentConfiguration(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setModal(False)
        self.build_gui()
        self.db_access = DatabaseAccessSingleton()

    def build_gui(self):
        layout = QtGui.QVBoxLayout()
        self.ref_search = PersistentRefViewSearch(None)
        self.ref_search.ref_widget.setSelectionMode(
            QtGui.QAbstractItemView.ExtendedSelection)
        layout.addWidget(self.ref_search)
        
        button_layout = QtGui.QHBoxLayout()
        button_layout.setAlignment(QtCore.Qt.AlignRight)
        write_button = QtGui.QPushButton("Write...")
        write_button.setAutoDefault(False)
        self.connect(write_button, QtCore.SIGNAL("clicked()"), self.write)
        button_layout.addWidget(write_button)
        delete_button = QtGui.QPushButton("Delete...")
        delete_button.setAutoDefault(False)
        self.connect(delete_button, QtCore.SIGNAL("clicked()"), self.delete)
        button_layout.addWidget(delete_button)
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def sizeHint(self):
        return QtCore.QSize(800,320)

    def write(self):
        info_list = self.ref_search.ref_widget.get_info_list()
        if len(info_list) < 1:
            return
        elif len(info_list) == 1:
            # save single file/dir
            info = info_list[0]
            name = info[2]
            chosen_path = QtGui.QFileDialog.getSaveFileName(
                    self,
                    'Save...',
                    name)
            if not chosen_path:
                return

            # FIXME really should move this calls to a higher level so
            # we don't need to instantiate a module
            if info[1] is None:
                version = "HEAD"
            else:
                version = info[1]
            repo.get_current_repo().get_path(info[0], version, None, 
                                             chosen_path)
        else:
            # have multiple files/dirs
            chosen_path = QtGui.QFileDialog.getExistingDirectory(
                    self,
                    'Save All to Directory...')
            has_overwrite = False
            # if untitled (no name, use the uuid)
            for info in info_list:
                if info[2]:
                    name = info[2]
                else:
                    name = info[0]
                full_path = os.path.join(chosen_path, name)
                if os.path.exists(full_path):
                    has_overwrite = True
            if has_overwrite:
                question_str = "One or more of the paths already exist.  " + \
                    "Overwrite?"
                ret_val = \
                    QtGui.QMessageBox.question(self, "Overwrite", \
                                                   question_str, \
                                                   QtGui.QMessageBox.Cancel | \
                                                   QtGui.QMessageBox.No | \
                                                   QtGui.QMessageBox.Yes)
                if ret_val != QtGui.QMessageBox.Yes:
                    return

            for info in info_list:
                if info[1] is None:
                    version = "HEAD"
                else:
                    version = info[1]
                if info[2]:
                    name = info[2]
                else:
                    name = info[0]
                full_path = os.path.join(chosen_path, name)
                repo.get_current_repo().git_get_path(info[0], version, None, 
                                                     full_path)
            
    def delete(self):
        QtGui.QMessageBox.critical(self, "Delete",
                                   "This feature is not functional in the "
                                   "current version of VisTrails and has been "
                                   "disabled for this release.")
        return

        from init import PersistentPath
        info_list = self.ref_search.ref_widget.get_info_list()
        if len(info_list) < 1:
            return

        delete_str = "This will permanently delete the selected data " + \
            "from the peristent store.  This cannot be undone.  Proceed?"
        question_f = QtGui.QMessageBox.question
        ret_val = question_f(self, "Delete", delete_str, \
                                 QtGui.QMessageBox.Cancel | \
                                 QtGui.QMessageBox.Ok)
        if ret_val != QtGui.QMessageBox.Ok:
            return
            
        git_util = PersistentPath()
        db_access = DatabaseAccessSingleton()
        # FIXME keep entry in database with flag for deleted?
        # NEED TO update the model...
        for info in info_list:
            delete_where = {'id': info[0]}
            if info[1] is None:
                git_util.git_remove_path(info[0])
                db_access.delete_from_database(delete_where)
            else:
                # FIXME implement delete for versions...
                delete_where['version'] = info[1]
                print "NOT IMPLEMENTED FOR VERSIONS!!"
                
                
        

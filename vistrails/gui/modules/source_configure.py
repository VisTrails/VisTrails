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
from vistrails.core import system, debug
from vistrails.core.utils import PortAlreadyExists
from vistrails.core.vistrail.module_function import ModuleFunction
from vistrails.core.vistrail.module_param import ModuleParam
from vistrails.gui.modules.module_configure import StandardModuleConfigurationWidget
from vistrails.gui.modules.tuple_configuration import PortTableConfigurationWidget, \
    PortTable
from vistrails.gui.theme import CurrentTheme
import urllib

class SourceEditor(QtGui.QTextEdit):

    def __init__(self, parent=None):
        QtGui.QTextEdit.__init__(self, parent)
        self.setAcceptRichText(False)
        self.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        self.formatChanged(None)
        self.setCursorWidth(8)
        self.connect(self,
                     QtCore.SIGNAL('currentCharFormatChanged(QTextCharFormat)'),
                     self.formatChanged)

        self.setFocusPolicy(QtCore.Qt.WheelFocus)

    def formatChanged(self, f):
        self.setFont(CurrentTheme.PYTHON_SOURCE_EDITOR_FONT)

class SourceWidget(PortTableConfigurationWidget):
    def __init__(self, module, controller, editor_class=None,
                 has_inputs=True, has_outputs=True, parent=None,
                 encode=True, portName='source'):
        PortTableConfigurationWidget.__init__(self, module, controller, parent)
        if editor_class is None:
            editor_class = SourceEditor
        self.codeEditor = editor_class(parent)
        self.setWindowTitle('%s Configuration' % module.name)
        self.setLayout(QtGui.QVBoxLayout())
        self.layout().setMargin(0)
        self.layout().setSpacing(0)
        self.has_inputs = has_inputs
        self.has_outputs = has_outputs
        self.sourcePortName = portName
        self.sourceEncode = encode
        self.createPortTable(has_inputs, has_outputs)
        self.setupEditor()
        self.adjustSize()

    def createPortTable(self, has_inputs=True, has_outputs=True):
        if has_inputs:
            self.inputPortTable = PortTable(self)
            labels = ["Input Port Name", "Type", "List Depth"]
            self.inputPortTable.setHorizontalHeaderLabels(labels)
            self.inputPortTable.initializePorts(self.module.input_port_specs)
            self.layout().addWidget(self.inputPortTable)
            horiz = self.inputPortTable.horizontalHeader()
            horiz.setResizeMode(1, QtGui.QHeaderView.Stretch)
        if has_outputs:
            self.outputPortTable = PortTable(self)
            labels = ["Output Port Name", "Type", "List Depth"]
            self.outputPortTable.setHorizontalHeaderLabels(labels)
            self.outputPortTable.initializePorts(self.module.output_port_specs,
                                                 True)
            self.layout().addWidget(self.outputPortTable)
            horiz = self.outputPortTable.horizontalHeader()
            horiz.setResizeMode(1, QtGui.QHeaderView.Stretch)
        if has_inputs:
            self.inputPortTable.fixGeometry()
            # resize input ports in case there are no output ports
            self.inputPortTable.resizeColumnToContents(0)
            self.inputPortTable.resizeColumnToContents(2)
        if has_inputs and has_outputs:
            self.performPortConnection(self.connect)
        if has_outputs:
            self.outputPortTable.fixGeometry()
            # Resize output (because it is largest) and trigger sync
            self.outputPortTable.resizeColumnToContents(0)
            self.outputPortTable.resizeColumnToContents(2)

    def initializeCode(self):
        self.codeEditor.clear()
        fid = self.findSourceFunction()
        code = None
        # Get code from a function
        if fid!=-1:
            f = self.module.functions[fid]
            code = f.params[0].strValue
        # Get code from the default on the port
        else:
            port = self.module.get_port_spec(self.sourcePortName, 'input')
            if port.defaults:
                code, = port.defaults
        if code is not None:
            if self.sourceEncode:
                code = urllib.unquote(code).decode('utf-8')
            self.codeEditor.setPlainText(code)
        if self.codeEditor.__class__.__name__ not in ['_PythonEditor', '_TextEditor']:
            self.codeEditor.document().setModified(False)
        else:
            self.codeEditor.setModified(False)
        self.codeEditor.setFocus()

    def findSourceFunction(self):
        fid = -1
        for i in xrange(self.module.getNumFunctions()):
            if self.module.functions[i].name==self.sourcePortName:
                fid = i
                break
        return fid

    def setupEditor(self):
        self.initializeCode()
        self.layout().addWidget(self.codeEditor, 1)

        self.cursorLabel = QtGui.QLabel()
        self.layout().addWidget(self.cursorLabel)
        if self.codeEditor.__class__.__name__ not in ['_PythonEditor', '_TextEditor']:
            self.connect(self.codeEditor,
                         QtCore.SIGNAL('cursorPositionChanged()'),
                         self.updateCursorLabel)
        else:
            self.connect(self.codeEditor,
                         QtCore.SIGNAL('cursorPositionChanged(int, int)'),
                         self.updateCursorLabel)
        self.updateCursorLabel()

    def updateCursorLabel(self, x=0, y=0):
        if self.codeEditor.__class__.__name__ not in ['_PythonEditor', '_TextEditor']:
            cursor = self.codeEditor.textCursor()
            x = cursor.blockNumber()
            y = cursor.columnNumber()

        self.cursorLabel.setText('Line: %d / Col: %d' % (x+1, y+1))

    def sizeHint(self):
        return QtCore.QSize(512, 512)

    def performPortConnection(self, operation):
        operation(self.inputPortTable.horizontalHeader(),
                  QtCore.SIGNAL('sectionResized(int,int,int)'),
                  self.portTableResize)
        operation(self.outputPortTable.horizontalHeader(),
                  QtCore.SIGNAL('sectionResized(int,int,int)'),
                  self.portTableResize)

    def portTableResize(self, logicalIndex, oldSize, newSize):
        self.performPortConnection(self.disconnect)
        if self.inputPortTable.horizontalHeader().sectionSize(logicalIndex)!=newSize:
            self.inputPortTable.horizontalHeader().resizeSection(logicalIndex,newSize)
        if self.outputPortTable.horizontalHeader().sectionSize(logicalIndex)!=newSize:
            self.outputPortTable.horizontalHeader().resizeSection(logicalIndex,newSize)
        QtGui.QApplication.processEvents()
        self.performPortConnection(self.connect)

    def activate(self):
        self.codeEditor.setFocus(QtCore.Qt.MouseFocusReason)

class SourceViewerWidget(SourceWidget):
    def __init__(self, module, controller, editor_class=None,
                 has_inputs=True, has_outputs=True, parent=None,
                 encode=True, portName='source'):
        SourceWidget.__init__(self, module, controller, editor_class,
                              has_inputs, has_outputs, parent, encode,
                              portName)
        self.codeEditor.setReadOnly(True)
        self.createCloseButton()
        self.setWindowTitle('%s Configuration (Read-Only)' % module.name)
        self.setWindowFlags(QtCore.Qt.Window)
        self.adjustSize()

    def createPortTable(self, has_inputs=True, has_outputs=True):
        if has_inputs:
            self.inputPortTable = QtGui.QTableWidget(1, 3, self)
            self.inputPortTable.horizontalHeader().setMovable(False)
            self.inputPortTable.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
            self.inputPortTable.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
            labels = ["Input Port Name", "Type", "List Depth"]
            self.inputPortTable.setHorizontalHeaderLabels(labels)
            self.initializePorts(self.inputPortTable,
                                 self.module.input_port_specs)
            self.layout().addWidget(self.inputPortTable)
            horiz = self.inputPortTable.horizontalHeader()
            horiz.setResizeMode(1, QtGui.QHeaderView.Stretch)
        if has_outputs:
            self.outputPortTable = QtGui.QTableWidget(1, 3, self)
            self.outputPortTable.horizontalHeader().setMovable(False)
            self.outputPortTable.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
            self.outputPortTable.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
            labels = ["Output Port Name", "Type", "List Depth"]
            self.outputPortTable.setHorizontalHeaderLabels(labels)
            self.initializePorts(self.outputPortTable,
                                 self.module.output_port_specs, True)
            self.layout().addWidget(self.outputPortTable)
            horiz = self.outputPortTable.horizontalHeader()
            horiz.setResizeMode(1, QtGui.QHeaderView.Stretch)
        if has_inputs:
            self.fixTableGeometry(self.inputPortTable)
            # resize input ports in case there are no output ports
            self.inputPortTable.resizeColumnToContents(0)
            self.inputPortTable.resizeColumnToContents(2)
        if has_inputs and has_outputs:
            self.performPortConnection(self.connect)
        if has_outputs:
            self.fixTableGeometry(self.outputPortTable)
            # Resize output (because it is largest) and trigger sync
            self.outputPortTable.resizeColumnToContents(0)
            self.outputPortTable.resizeColumnToContents(2)

    def initializePorts(self, table, port_specs, reverse_order=False):
        if reverse_order:
            port_specs_iter = reversed(port_specs)
        else:
            port_specs_iter = port_specs
        for p in port_specs_iter:
            row = table.rowCount()-1
            sigstring = p.sigstring[1:-1]
            siglist = sigstring.split(':')
            short_name = "%s (%s)" % (siglist[1], siglist[0])

            item = QtGui.QTableWidgetItem(p.name)
            item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled)
            table.setItem(row, 0, item)
            item = QtGui.QTableWidgetItem(short_name)
            item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled)
            table.setItem(row, 1, item)
            item = QtGui.QTableWidgetItem(str(p.depth))
            item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled)
            table.setItem(row, 2, item)
            table.setRowCount(table.rowCount()+1)

    def fixTableGeometry(self, table):
        rect = table.visualRect(table.model().index(table.rowCount()-1,
                                                    table.columnCount()-1))
        table.setFixedHeight(table.horizontalHeader().height()+
                             rect.y()+rect.height()+1)
    def createCloseButton(self):
        hboxlayout = QtGui.QHBoxLayout()
        self.closeButton = QtGui.QPushButton("Close")
        self.connect(self.closeButton, QtCore.SIGNAL("clicked()"),
                     self.closeWidget)
        hboxlayout.addStretch()
        hboxlayout.addWidget(self.closeButton)
        hboxlayout.addStretch()
        self.layout().addLayout(hboxlayout)

    def closeWidget(self):
        self.emit(QtCore.SIGNAL("widgetClosed"))
        self.close()

class SourceConfigurationWidget(SourceWidget):

    def __init__(self, module, controller, editor_class=None,
                 has_inputs=True, has_outputs=True, parent=None,
                 encode=True, portName='source'):
        SourceWidget.__init__(self, module, controller, editor_class,
                              has_inputs, has_outputs, parent, encode,
                              portName)
        self.detached_windows = []
        self.createButtons()
        #connect signals
        if has_inputs:
            self.connect(self.inputPortTable, QtCore.SIGNAL("contentsChanged"),
                         self.updateState)
        if has_outputs:
            self.connect(self.outputPortTable, QtCore.SIGNAL("contentsChanged"),
                         self.updateState)
        self.connect(self.codeEditor, QtCore.SIGNAL("textChanged()"),
                     self.updateState)
        self.adjustSize()
        self.setMouseTracking(True)
        self.mouseOver = False

    def enterEvent(self, event):
        self.mouseOver = True

    def leaveEvent(self, event):
        self.mouseOver = False

    def createButtons(self):
        """ createButtons() -> None
        Create and connect signals to Save & Reset button

        """
        self.buttonLayout = QtGui.QHBoxLayout()
        self.buttonLayout.setMargin(5)
        self.detachButton = QtGui.QPushButton("Show read-only window")
        self.buttonLayout.addWidget(self.detachButton)
        self.buttonLayout.addStretch()
        self.saveButton = QtGui.QPushButton('&Save', self)
        self.saveButton.setFixedWidth(100)
        self.saveButton.setEnabled(False)
        self.buttonLayout.addWidget(self.saveButton)
        self.resetButton = QtGui.QPushButton('&Reset', self)
        self.resetButton.setFixedWidth(100)
        self.resetButton.setEnabled(False)
        self.buttonLayout.addSpacing(10)
        self.buttonLayout.addWidget(self.resetButton)
        self.layout().addLayout(self.buttonLayout)
        self.connect(self.detachButton, QtCore.SIGNAL("clicked()"),
                     self.detachReadOnlyWindow)
        self.connect(self.saveButton, QtCore.SIGNAL('clicked(bool)'),
                     self.saveTriggered)
        self.connect(self.resetButton, QtCore.SIGNAL('clicked(bool)'),
                     self.resetTriggered)

    def detachReadOnlyWindow(self):
        from vistrails.gui.vistrails_window import _app
        widget = SourceViewerWidget(self.module, self.controller,
                                           type(self.codeEditor),
                                           self.has_inputs, self.has_outputs,
                                           None, self.sourceEncode,
                                           self.sourcePortName)
        window = QtGui.QMainWindow()
        window.setCentralWidget(widget)
        window.setWindowTitle(widget.windowTitle())
        self.connect(widget, QtCore.SIGNAL("widgetClosed"),
                    window.close)
        widget.setVisible(True)
        _app.palette_window.windows.append(window)
        window.show()

    def updateVistrail(self):
        """updateVistrail() -> None
        Update vistrail to contain changes to the python source

        """
        deleted_ports = []
        added_ports = []
        if self.has_inputs:
            (input_deleted_ports, input_added_ports) = \
                self.getPortDiff('input', self.inputPortTable)
            deleted_ports.extend(input_deleted_ports)
            added_ports.extend(input_added_ports)
        if self.has_outputs:
            (output_deleted_ports, output_added_ports) = \
                self.getPortDiff('output', self.outputPortTable)
            deleted_ports.extend(output_deleted_ports)
            added_ports.extend(output_added_ports)

        functions = []
        modified = False
        if self.codeEditor.__class__.__name__ not in ['_PythonEditor', '_TextEditor']:
            modified = self.codeEditor.document().isModified()
        else:
            modified = self.codeEditor.isModified()

        if (self.codeEditor is not None and modified):
            code = self.codeEditor.toPlainText().encode('utf-8')
            if self.sourceEncode:
                code = urllib.quote(code)
            functions.append((self.sourcePortName, [code]))
        if len(deleted_ports) + len(added_ports) + len(functions) == 0:
            # nothing changed
            return True
        try:
            self.controller.update_ports_and_functions(self.module.id,
                                                       deleted_ports,
                                                       added_ports,
                                                       functions)
        except PortAlreadyExists, e:
            debug.critical('Port Already Exists %s' % e)
            return False
        return True

    def resetTriggered(self, checked = False):
        if self.has_inputs:
            self.inputPortTable.clearContents()
            self.inputPortTable.setRowCount(1)
            self.inputPortTable.initializePorts(self.module.input_port_specs)
            self.inputPortTable.fixGeometry()
        if self.has_outputs:
            self.outputPortTable.clearContents()
            self.outputPortTable.setRowCount(1)
            self.outputPortTable.initializePorts(self.module.output_port_specs,
                                             True)
            self.outputPortTable.fixGeometry()

        self.initializeCode()
        self.saveButton.setEnabled(False)
        self.resetButton.setEnabled(False)
        self.state_changed = False
        self.emit(QtCore.SIGNAL("stateChanged"))

    def updateState(self):
        self.saveButton.setEnabled(True)
        self.resetButton.setEnabled(True)
        if not self.state_changed:
            self.state_changed = True
            self.emit(QtCore.SIGNAL("stateChanged"))

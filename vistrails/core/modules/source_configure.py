############################################################################
##
## Copyright (C) 2006-2010 University of Utah. All rights reserved.
##
## This file is part of VisTrails.
##
## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following to ensure GNU General Public
## Licensing requirements will be met:
## http://www.opensource.org/licenses/gpl-license.php
##
## If you are unsure which license is appropriate for your use (for
## instance, you are interested in developing a commercial derivative
## of VisTrails), please contact us at vistrails@sci.utah.edu.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################

from PyQt4 import QtCore, QtGui
from core import system, debug
from core.modules.module_configure import StandardModuleConfigurationWidget
from core.modules.tuple_configuration import PortTableConfigurationWidget, \
    PortTable
from core.utils import PortAlreadyExists
from core.vistrail.module_function import ModuleFunction
from core.vistrail.module_param import ModuleParam
from gui.theme import CurrentTheme
import urllib

class SourceEditor(QtGui.QTextEdit):

    def __init__(self, parent=None):
        QtGui.QTextEdit.__init__(self, parent)
        self.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        self.formatChanged(None)
        self.setCursorWidth(8)
        self.connect(self,
                     QtCore.SIGNAL('currentCharFormatChanged(QTextCharFormat)'),
                     self.formatChanged)

    def formatChanged(self, f):
        self.setFont(CurrentTheme.PYTHON_SOURCE_EDITOR_FONT)

class SourceConfigurationWidget(PortTableConfigurationWidget):

    def __init__(self, module, controller, editor_class=None,
                 has_inputs=True, has_outputs=True, parent=None,
                 encode=True, portName='source'):
        PortTableConfigurationWidget.__init__(self, module, controller, parent)
        if editor_class is None:
            editor_class = SourceEditor
        self.codeEditor = editor_class(self)
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
        self.createButtons()

    def sizeHint(self):
        return QtCore.QSize(512, 512)

    def createPortTable(self, has_inputs=True, has_outputs=True):
        if has_inputs:
            self.inputPortTable = PortTable(self)
            labels = QtCore.QStringList() << "Input Port Name" << "Type"
            self.inputPortTable.setHorizontalHeaderLabels(labels)
            self.inputPortTable.initializePorts(self.module.input_port_specs)
            self.layout().addWidget(self.inputPortTable)
        if has_outputs:
            self.outputPortTable = PortTable(self)
            labels = QtCore.QStringList() << "Output Port Name" << "Type"
            self.outputPortTable.setHorizontalHeaderLabels(labels)
            self.outputPortTable.initializePorts(self.module.output_port_specs, 
                                                 True)
            self.layout().addWidget(self.outputPortTable)
        if has_inputs and has_outputs:
            self.performPortConnection(self.connect)
        if has_inputs:
            self.inputPortTable.fixGeometry()
        if has_outputs:
            self.outputPortTable.fixGeometry()

    def findSourceFunction(self):
        fid = -1
        for i in xrange(self.module.getNumFunctions()):
            if self.module.functions[i].name==self.sourcePortName:
                fid = i
                break
        return fid

    def setupEditor(self):
        fid = self.findSourceFunction()
        if fid!=-1:
            f = self.module.functions[fid]
            code = f.params[0].strValue
            if self.sourceEncode:
                code = urllib.unquote(code)
            self.codeEditor.setPlainText(code)
        self.codeEditor.document().setModified(False)
        self.layout().addWidget(self.codeEditor, 1)
        
        self.cursorLabel = QtGui.QLabel()
        self.layout().addWidget(self.cursorLabel)
        self.connect(self.codeEditor, QtCore.SIGNAL('cursorPositionChanged()'),
                     self.updateCursorLabel)
        self.updateCursorLabel()

    def updateCursorLabel(self):
        cursor = self.codeEditor.textCursor()
        self.cursorLabel.setText('Line: %d / Col: %d' % (cursor.blockNumber()+1,
                                                            cursor.columnNumber()+1))

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
        self.performPortConnection(self.connect)

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
        if (self.codeEditor is not None and
            self.codeEditor.document().isModified()):
            code = str(self.codeEditor.toPlainText())
            if self.sourceEncode:
                code = urllib.quote(code)
            functions.append((self.sourcePortName, [code]))
        if len(deleted_ports) + len(added_ports) + len(functions) == 0:
            # nothing changed
            return
        try:
            self.controller.update_ports_and_functions(self.module.id, 
                                                       deleted_ports, 
                                                       added_ports,
                                                       functions)
        except PortAlreadyExists, e:
            debug.critical('Port Already Exists %s' % str(e))
            return False
        return True

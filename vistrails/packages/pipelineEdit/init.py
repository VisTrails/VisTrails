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
import api
from core.utils import DummyView
from core.vistrail.controller import VistrailController

class QPipelineEditor(QtGui.QWidget):
    """QPipelineEditor is a simple widget that can load a vistrail,
    select a pipeline and dipslay aliases of that pipeline."""
    
    def __init__(self, parent=None):
        """ init(parent: QWidget) -> None
        Construct and layout GUI elements

        """
        QtGui.QWidget.__init__(self, parent)
        self.setWindowTitle('Pipeline Editor')

        self.vistrail = None
        self.versions = []
        
        vbox = QtGui.QVBoxLayout()
        self.setLayout(vbox)

        hbox = QtGui.QHBoxLayout()
        vbox.addLayout(hbox)

        self.filenameLabel = QtGui.QLabel('Vistrail: N/A')
        hbox.addWidget(self.filenameLabel)
        self.browseButton = QtGui.QPushButton('Browse...')
        hbox.addWidget(self.browseButton)
        self.connect(self.browseButton, QtCore.SIGNAL('clicked()'),
                     self.selectFile)

        vbox.addWidget(QtGui.QLabel('Pipelines'))
        self.pipelineList = QtGui.QListWidget()
        vbox.addWidget(self.pipelineList)
        self.connect(self.pipelineList, QtCore.SIGNAL('currentRowChanged(int)'),
                     self.currentPipelineChanged)
        
        vbox.addWidget(QtGui.QLabel('Aliases'))
        self.aliasTable = QtGui.QTableWidget(0, 2)
        self.aliasTable.horizontalHeader().setStretchLastSection(True)
        vbox.addWidget(self.aliasTable)

        hbox = QtGui.QHBoxLayout()
        vbox.addLayout(hbox)
        self.executeButton = QtGui.QPushButton('Execute')
        hbox.addWidget(self.executeButton)
        self.connect(self.executeButton, QtCore.SIGNAL('clicked()'),
                     self.execute)
        
    def selectFile(self):
        """ selectFile() -> None
        Open a file dialog and select a vistrail file. Then display a
        list of tagged version on the pipeline list.

        """
        fn = QtGui.QFileDialog.getOpenFileName(self,
                                               'Load Vistrail',
                                               '.',
                                               'Vistrail (*.vt)')
        if not fn.isNull():
            self.filenameLabel.setText('Vistrail: %s' % fn)
            self.vistrail = api.get_vistrail_from_file(str(fn))
            for item in self.vistrail.get_tagMap().items():
                self.versions.append(item)
            self.pipelineList.clear()
            self.pipelineList.addItems([version for (name, version) in self.versions])

    def currentPipelineChanged(self, row):
        """ currentPipelineChanged(row: int) -> None
        When the current pipeline is changed in the pipeline list,
        update the alias table with aliases in that pipeline.
        
        """
        if row<0:
            self.aliasTable.setRowCount(0)
        else:
            versionName = self.pipelineList.currentItem().text()
            pipeline = self.vistrail.getPipelineVersionName(str(versionName))
            aliases = pipeline.aliases.keys()
            self.aliasTable.setRowCount(len(aliases))
            row = 0
            for name in aliases:
                self.aliasTable.setItem(row, 0, QtGui.QTableWidgetItem(name))
                value = pipeline.get_alias_str_value(name)
                self.aliasTable.setItem(row, 1, QtGui.QTableWidgetItem(value))
                row += 1

    def execute(self):
        """ execute() -> None
        Execute the selected pipeline with the edited aliases

        """
        aliases = {}
        for r in xrange(self.aliasTable.rowCount()):
            name = str(self.aliasTable.item(r, 0).text())
            value = str(self.aliasTable.item(r, 1).text())
            aliases[name] = value

        versionNumber = self.versions[self.pipelineList.currentIndex().row()][0]
        pipeline = self.vistrail.getPipelineVersionNumber(versionNumber)
        controller = VistrailController(self.vistrail)
        controller.execute_workflow_list([(self.vistrail.locator,
                                           versionNumber,
                                           pipeline,
                                           DummyView(),
                                           aliases,
                                           None)])

def initialize(*args, **keywords):
    """ initialize() -> None    
    Package-entry to initialize the package. We just create and show
    the main window, a QPipelineEditor widget, here.
    
    """
    global mainWindow
    mainWindow = QPipelineEditor()
    mainWindow.show()

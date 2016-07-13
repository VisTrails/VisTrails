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
import vistrails.api
from vistrails.core.utils import DummyView
from vistrails.core.vistrail.controller import VistrailController

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
            self.vistrail = vistrails.api.get_vistrail_from_file(str(fn))
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

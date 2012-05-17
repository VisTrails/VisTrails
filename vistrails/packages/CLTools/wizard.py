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

import sys
import os
import json
import subprocess
import platform
from PyQt4 import QtCore, QtGui

encode_list = [['\xe2\x80\x90', '-'],
               ['\xe2\x80\x9d', '"'],
               ['\xe2\x80\x9c', '"']]

SUFFIX = '.clt'

def default_dir():
    systemType = platform.system()
    if systemType in ['Windows', 'Microsoft']:
        if len(os.environ['HOMEPATH']) == 0:
            root = '\\'
        else:
            root = os.environ['HOMEDRIVE'] + os.environ['HOMEPATH']
    else:
        root = os.getenv('HOME')
    default_dir = os.path.join(root, '.vistrails', 'CLTools')
    if not os.path.exists(default_dir):
        os.mkdir(default_dir)
    return default_dir
    
class QCLToolsWizard(QtGui.QWidget):
    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.vbox = QtGui.QVBoxLayout()
        self.setLayout(self.vbox)
        self.setTitle()
        self.file = None

        self.toolBar = QtGui.QToolBar()
        self.layout().addWidget(self.toolBar)
        self.newFileAction = QtGui.QAction(
            self.get_icon('document-new'), 'New', self)
        self.newFileAction.setToolTip('Start on a new Wrapper')
        self.connect(self.newFileAction, QtCore.SIGNAL('triggered()'),
                     self.newFile)
        self.toolBar.addAction(self.newFileAction)
        self.openFileAction = QtGui.QAction(
            self.get_icon('document-open'), 'Open', self)
        self.openFileAction.setToolTip('Open an existing wrapper')
        self.connect(self.openFileAction, QtCore.SIGNAL('triggered()'),
                     self.openFile)
        self.toolBar.addAction(self.openFileAction)
        self.saveFileAction = QtGui.QAction(
            self.get_icon('document-save'), 'Save', self)
        self.saveFileAction.setToolTip('Save wrapper')
        self.connect(self.saveFileAction, QtCore.SIGNAL('triggered()'),
                     self.save)
        self.toolBar.addAction(self.saveFileAction)
        self.saveFileAsAction = QtGui.QAction(
            self.get_icon('document-save-as'), 'Save As', self)
        self.saveFileAsAction.setToolTip('Save wrapper as a new file')
        self.connect(self.saveFileAsAction, QtCore.SIGNAL('triggered()'),
                     self.saveAs)
        self.toolBar.addAction(self.saveFileAsAction)
        
        self.toolBar.addSeparator()
        self.addAction = QtGui.QAction(
            self.get_icon('list-add'), 'Add', self)
        self.addAction.setToolTip('Add a new argument')
        self.connect(self.addAction, QtCore.SIGNAL('triggered()'),
                     self.addArgument)
        self.toolBar.addAction(self.addAction)
        self.removeAction = QtGui.QAction(
            self.get_icon('list-remove'), 'Remove', self)
        self.removeAction.setToolTip('Remove the selected argument')
        self.connect(self.removeAction, QtCore.SIGNAL('triggered()'),
                     self.removeArgument)
        self.toolBar.addAction(self.removeAction)
        self.upAction = QtGui.QAction(
            self.get_icon('go-up'), 'Move up', self)
        self.upAction.setToolTip('Move argument up one position')
        self.connect(self.upAction, QtCore.SIGNAL('triggered()'),
                     self.moveUp)
        self.toolBar.addAction(self.upAction)
        self.downAction = QtGui.QAction(
            self.get_icon('go-down'), 'Move down', self)
        self.downAction.setToolTip('Move argument down one position')
        self.connect(self.downAction, QtCore.SIGNAL('triggered()'),
                     self.moveDown)
        self.toolBar.addAction(self.downAction)
        
        self.toolBar.addSeparator()
        self.showStdin = QtGui.QAction('stdin', self)
        self.showStdin.setToolTip('Check to use standard input as an input port')
        self.showStdin.setCheckable(True)
        self.toolBar.addAction(self.showStdin)
        self.showStdout = QtGui.QAction("stdout", self)
        self.showStdout.setToolTip('Check to use standard output as an output port')
        self.showStdout.setCheckable(True)
        self.toolBar.addAction(self.showStdout)
        self.showStderr = QtGui.QAction("stderr", self)
        self.showStderr.setToolTip('Check to use standard error as an output port')
        self.showStderr.setCheckable(True)
        self.toolBar.addAction(self.showStderr)
        
        self.toolBar.addSeparator()
        self.stdAsFiles = QtGui.QAction('std file processing', self)
        self.stdAsFiles.setToolTip('Check to make pipes communicate using files instead of strings\nOnly useful when processing large files')
        self.stdAsFiles.setCheckable(True)
        self.toolBar.addAction(self.stdAsFiles)

        self.commandLayout = QtGui.QHBoxLayout()
        self.commandLayout.addWidget(QtGui.QLabel("command:"))
        self.command = QtGui.QLineEdit()
        self.commandLayout.addWidget(self.command)
        self.vbox.addLayout(self.commandLayout)

        self.importLayout = QtGui.QHBoxLayout()
        self.importLayout.setAlignment(QtCore.Qt.AlignLeft)
        self.importLayout.addWidget(QtGui.QLabel("Man page:"))
        self.viewManButton = QtGui.QPushButton("view")
        self.viewManButton.setToolTip('View the man page for the current command')
        self.connect(self.viewManButton, QtCore.SIGNAL('clicked()'),
                     self.viewManPage)
        self.importLayout.addWidget(self.viewManButton)
        self.importManButton = QtGui.QPushButton("import")
        self.importManButton.setToolTip('Import arguments from the man page for the current command')
        self.connect(self.importManButton, QtCore.SIGNAL('clicked()'),
                     self.generateFromManPage)
        self.importLayout.addWidget(self.importManButton)

        self.importLayout.addWidget(QtGui.QLabel("help page (-h):"))
        self.viewHelpButton = QtGui.QPushButton("view")
        self.viewHelpButton.setToolTip('View the help (-h) page for the current command')
        self.connect(self.viewHelpButton, QtCore.SIGNAL('clicked()'),
                     self.viewHelpPage)
        self.importLayout.addWidget(self.viewHelpButton)
        self.importHelpButton = QtGui.QPushButton("import")
        self.importHelpButton.setToolTip('Import arguments from the help (-h) page for the current command')
        self.connect(self.importHelpButton, QtCore.SIGNAL('clicked()'),
                     self.generateFromHelpPage)
        self.importLayout.addWidget(self.importHelpButton)

        self.importLayout.addWidget(QtGui.QLabel("help page (--help):"))
        self.viewHelpButton2 = QtGui.QPushButton("view")
        self.viewHelpButton2.setToolTip('View the help (--help) page for the current command')
        self.connect(self.viewHelpButton2, QtCore.SIGNAL('clicked()'),
                     self.viewHelpPage2)
        self.importLayout.addWidget(self.viewHelpButton2)
        self.importHelpButton2 = QtGui.QPushButton("import")
        self.importHelpButton2.setToolTip('Import arguments from the help (--help) page for the current command')
        self.connect(self.importHelpButton2, QtCore.SIGNAL('clicked()'),
                     self.generateFromHelpPage2)
        self.importLayout.addWidget(self.importHelpButton2)
        self.vbox.addLayout(self.importLayout)

        self.stdinWidget = QArgWidget('stdin')
        self.stdinGroup = QtGui.QGroupBox('Standard input')
        self.stdinGroup.setLayout(QtGui.QHBoxLayout())
        self.stdinGroup.layout().addWidget(self.stdinWidget)
        self.layout().addWidget(self.stdinGroup)
        self.stdinGroup.setVisible(False)
        self.stdoutWidget = QArgWidget('stdout')
        self.stdoutGroup = QtGui.QGroupBox('Standard output')
        self.stdoutGroup.setLayout(QtGui.QHBoxLayout())
        self.stdoutGroup.layout().addWidget(self.stdoutWidget)
        self.layout().addWidget(self.stdoutGroup)
        self.stdoutGroup.setVisible(False)
        self.stderrWidget = QArgWidget('stderr')
        self.stderrGroup = QtGui.QGroupBox('Standard error')
        self.stderrGroup.setLayout(QtGui.QHBoxLayout())
        self.stderrGroup.layout().addWidget(self.stderrWidget)
        self.layout().addWidget(self.stderrGroup)
        self.stderrGroup.setVisible(False)

        self.connect(self.showStdin, QtCore.SIGNAL('toggled(bool)'),
                     self.stdinGroup.setVisible)
        self.connect(self.showStdout, QtCore.SIGNAL('toggled(bool)'),
                     self.stdoutGroup.setVisible)
        self.connect(self.showStderr, QtCore.SIGNAL('toggled(bool)'),
                     self.stderrGroup.setVisible)
        
        self.argList = QtGui.QListWidget()
        self.layout().addWidget(self.argList)

    def get_icon(self, name):
        return QtGui.QIcon(os.path.join(os.path.dirname(__file__),
                                        "icons",
                                        "%s.png" % name))
    def setTitle(self, file=None):
        self.parent().setWindowTitle("CLTools Wizard - " + (file if file else "untitled"))

    def newFile(self):
        self.file = None
        self.command.clear()
        self.showStdin.setChecked(False)
        self.showStdout.setChecked(False)
        self.showStderr.setChecked(False)
        while self.argList.count():
            item = self.argList.item(0)
            itemWidget = self.argList.itemWidget(item)
            itemWidget.setVisible(False)
            itemWidget.setParent(None)
            self.argList.removeItemWidget(item)
            item.setHidden(True)
            self.argList.takeItem(0)
        self.argList.hide()
        self.layout().takeAt(self.layout().indexOf(self.argList))
        self.argList = QtGui.QListWidget()
        self.layout().addWidget(self.argList)
        self.stdAsFiles.setChecked(False)
        self.setTitle()
    
    def openFile(self):
        fileName = QtGui.QFileDialog.getOpenFileName(self,
                "Open Wrapper",
                self.file if self.file else default_dir(),
                "Wrappers (*%s)" % SUFFIX)
        if not fileName:
            return
        try:
            conf = json.load(open(fileName))
        except  ValueError as exc:
            print "Error opening Wrapper '%s': %s" % (fileName, exc)
            return
        self.newFile()
        self.file = fileName
        self.setTitle(self.file)
        self.command.setText(conf.get('command', ''))
        if 'stdin' in conf:
            self.stdinWidget.fromList(conf['stdin'])
        self.stdinGroup.setVisible('stdin' in conf)
        self.showStdin.setChecked('stdin' in conf)
        if 'stdout' in conf:
            self.stdoutWidget.fromList(conf['stdout'])
        self.stdoutGroup.setVisible('stdout' in conf)
        self.showStdout.setChecked('stdout' in conf)
        if 'stderr' in conf:
            self.stderrWidget.fromList(conf['stderr'])
        self.stderrGroup.setVisible('stderr' in conf)
        self.showStderr.setChecked('stderr' in conf)
        for argConf in conf.get('args', []):
            arg = QArgWidget()
            arg.fromList(argConf)
            item = QtGui.QListWidgetItem()
            item.setSizeHint(arg.sizeHint())
            self.argList.addItem(item)
            self.argList.setItemWidget(item, arg)
        if 'options' in conf:
            self.stdAsFiles.setChecked('std_using_files' in conf['options'])

    def save(self):
        if not self.file:
            self.saveAs()
            if not self.file:
                return
        conf = {}
        conf['command'] = str(self.command.text()).strip()
        if self.stdinGroup.isVisible():
            conf['stdin'] = self.stdinWidget.toList()
        if self.stdoutGroup.isVisible():
            conf['stdout'] = self.stdoutWidget.toList()
        if self.stderrGroup.isVisible():
            conf['stderr'] = self.stderrWidget.toList()
        args = []
        for row in xrange(self.argList.count()):
            arg = self.argList.itemWidget(self.argList.item(row))
            args.append(arg.toList())
        conf['args'] = args
        if self.stdAsFiles.isChecked():
            if not 'options' in conf:
                conf['options'] = {}
            conf['options']['std_using_files'] = ''

        f = open(self.file, "w")
        conf = json.dump(conf, f, sort_keys=True, indent=4)
        f.close()

    def saveAs(self):
        fileName = QtGui.QFileDialog.getSaveFileName(self,
                            "Save Wrapper as",
                            self.file if self.file else default_dir(),
                            "Wrappers (*%s)" % SUFFIX)
        if fileName:
            self.file = str(fileName)
            if not self.file.endswith(SUFFIX):
                self.file += SUFFIX
            self.save()
            self.setTitle(self.file)

    def loadFromCommand(self, argv):
        self.command.setText(argv[0])
        pos = 0
        for argName in argv[1:]:
            arg = QArgWidget()
            arg.guess(argName, pos)
            pos += 1
            item = QtGui.QListWidgetItem()
            item.setSizeHint(arg.sizeHint())
            self.argList.addItem(item)
            self.argList.setItemWidget(item, arg)

    def addArgument(self):
        arg = QArgWidget()
        item = QtGui.QListWidgetItem()
        item.setSizeHint(arg.sizeHint())
        self.argList.addItem(item)
        self.argList.setItemWidget(item, arg)

    def moveUp(self):
        currentRow = self.argList.currentRow()
        if currentRow < 1:
            return
        # moving widgets does not work so we just switch contents
        w0 = self.argList.itemWidget(self.argList.item(currentRow-1))
        w1 = self.argList.itemWidget(self.argList.item(currentRow))
        arg0 = w0.toList()
        arg1 = w1.toList()
        w0.fromList(arg1)
        w1.fromList(arg0)
        self.argList.setCurrentRow(currentRow - 1)

    def moveDown(self):
        currentRow = self.argList.currentRow()
        if currentRow<0 or currentRow>self.argList.count()-2:
            return
        # moving widgets does not work so we just switch contents
        w1 = self.argList.itemWidget(self.argList.item(currentRow))
        w2 = self.argList.itemWidget(self.argList.item(currentRow+1))
        arg1 = w1.toList()
        arg2 = w2.toList()
        w1.fromList(arg2)
        w2.fromList(arg1)
        self.argList.setCurrentRow(currentRow + 1)

    def removeArgument(self):
        currentRow = self.argList.currentRow()
        if currentRow<0:
            return
        self.argList.takeItem(currentRow)

    def keyPressEvent(self, event):
        if event.key() in [QtCore.Qt.Key_Delete, QtCore.Qt.Key_Backspace]:
            self.removeArgument()
        else:
            QtGui.QWidget.keyPressEvent(self, event)
    
    def parse(self, text):
        """ parse(self, text)
        parses the description of a command and extracts possible arguments
        works on both man pages and help (-h) pages
        """
        lines = text.split('\n')
        args = []
        arg = None
        for line in lines:
            line = line.strip()
            if len(line)>1 and line[0] == '-':
                # make sure description is removed
                flag = line.split('   ')[0].strip()
                # use the last in the list of equal flags
                #it is assumed to be most descriptive
                flag = flag.split(',')[-1].strip()
                # remove any special characters after flag
                for i in ['=', '[', ' ']:
                    flag = flag.split(i)[0].strip()
                # new arg (type, flag, description)
                arg = ['Flag', flag, line]
                if '=' in line: # assume string attribute with prefix 
                    arg[0] = 'String'
                args.append(arg)
            elif arg:
                if not line:
                    arg = None
                else:
                    arg[2] += ' %s' % line.strip()
        #print "args:"
        #for arg in args:
        #    print arg
        return args
        
    def runProcess(self, args):
        try:
            text, stderr = subprocess.Popen(args,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, shell=True).communicate()
            if not (text and len(text)):
                text = stderr
                if not (text and len(text)) or (text and text.beginswith('No ')):
                    return None
            # fix weird formatting
            for a, b in encode_list:
                text = text.replace(a, b)
            return text
        except:
            return None
    
    def generateFromManPage(self):
        command = str(self.command.text())
        if command == '':
            return
        text = self.runProcess(['-c', 'man %s | col -b' % command])
        if not text:
            QtGui.QMessageBox.warning(self, "Man page not found",
                                      "For command '%s'" % command)
            return
        args = self.parse(text)
        title = "Import arguments from man page for '%s'" % command
        self.manpageImport = QManpageImport(title, args, self)
        self.connect(self.manpageImport,
                       QtCore.SIGNAL("importArgs(PyQt_PyObject)"),
                       self.importArgs)
        self.manpageImport.show()

    def generateFromHelpPage(self):
        command = str(self.command.text())
        if command == '':
            return
        text = self.runProcess([command, '-h'])
        if not text:
            QtGui.QMessageBox.warning(self, "Help page (-h) not found",
                                      "For command '%s'" % command)
            return
        args = self.parse(text)

        title = "Import arguments from help page (-h) for '%s'" % command
        self.helppageImport = QManpageImport(title, args, self)
        self.connect(self.helppageImport,
                       QtCore.SIGNAL("importArgs(PyQt_PyObject)"),
                       self.importArgs)
        self.helppageImport.show()

    def generateFromHelpPage2(self):
        command = str(self.command.text())
        if command == '':
            return
        text = self.runProcess([command, '--help'])
        if not text:
            QtGui.QMessageBox.warning(self, "Help page (--help) not found",
                                      "For command '%s'" % command)
            return
        args = self.parse(text)

        title = "Import arguments from help page (--help) for '%s'" % command
        self.helppageImport = QManpageImport(title, args, self)
        self.connect(self.helppageImport,
                       QtCore.SIGNAL("importArgs(PyQt_PyObject)"),
                       self.importArgs)
        self.helppageImport.show()

    def viewManPage(self):
        command = str(self.command.text())
        if command == '':
            return
        text = self.runProcess(['-c', 'man %s | col -b' % command])
        if not text:
            QtGui.QMessageBox.warning(self, "Man page not found",
                                      "For command '%s'" % command)
            return
        title = "man page for '%s'" % command
        self.manpageView = QManpageDialog(title, text, self)
        self.manpageView.show()

    def viewHelpPage(self):
        command = str(self.command.text())
        if command == '':
            return
        text = self.runProcess([command, '-h'])
        if not text:
            QtGui.QMessageBox.warning(self, "Help page (-h) not found",
                                      "For command '%s'" % command)
            return
        title = "Help page for '%s'" % command
        self.helppageView = QManpageDialog(title, text, self)
        self.helppageView.show()

    def viewHelpPage2(self):
        command = str(self.command.text())
        if command == '':
            return
        text = self.runProcess([command, '--help'])
        if not text:
            QtGui.QMessageBox.warning(self, "Help page (--help) not found",
                                      "For command '%s'" % command)
            return
        title = "Help page for '%s'" % command
        self.helppageView = QManpageDialog(title, text, self)
        self.helppageView.show()

    def importArgs(self, args):
        for arg in args:
            item = QtGui.QListWidgetItem()
            item.setSizeHint(arg.sizeHint())
            self.argList.insertItem(0, item)
            self.argList.setItemWidget(item, arg)

class QArgWidget(QtGui.QWidget):
    """ Widget for configuring an argument """
    def __init__(self, argtype='Input', name='untitled', klass='Flag', options={}, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.stdTypes = ['stdin', 'stdout', 'stderr']
        self.stdLabels = ['Standard input', 'Standard output', 'Standard error']
        self.stdDict = dict(zip(self.stdTypes, self.stdLabels))
        
        self.argtype = argtype
        self.name = name
        self.klass = klass
        self.options = options

        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)

        self.buildWidget()
        
    def buildWidget(self):
        layout = self.layout()
        # remove any previous layout
        layout1 = QtGui.QHBoxLayout()
        layout.addLayout(layout1)
        if self.argtype not in self.stdTypes:
            layout2 = QtGui.QHBoxLayout()
            layout.addLayout(layout2)
        else:
            layout2 = layout1
        # type of argument
        if self.argtype not in self.stdTypes:
            self.typeList = QtGui.QComboBox()
            self.types = ['Input', 'Output', 'Constant']
            self.typeDict = dict(zip(self.types, xrange(len(self.types))))
            self.typeDict.update(dict(zip([s.lower() for s in self.types], xrange(len(self.types)))))
            self.typeList.addItems(self.types)
            self.typeList.setCurrentIndex(self.typeDict.get(self.argtype, 0))
            label = QtGui.QLabel('Type:')
            label.setToolTip('Sets if arg will be an input, output or a constant argument')
            layout1.addWidget(label)
            layout1.addWidget(self.typeList)
        # name of port
        self.nameLine = QtGui.QLineEdit(self.name)
        label = QtGui.QLabel('Name:')
        label.setToolTip('Name of the port, or the value for constants')
        layout1.addWidget(label)
        layout1.addWidget(self.nameLine)
        # type of port
        self.klassList = QtGui.QComboBox()
        self.klasses = ['Flag', 'String', 'File', 'List']
        if self.argtype in self.stdTypes:
            self.klasses = ['String', 'File']
        self.klassDict = dict(zip(self.klasses, xrange(len(self.klasses))))
        self.klassDict.update(dict(zip([s.lower() for s in self.klasses], xrange(len(self.klasses)))))
        self.klassList.addItems(self.klasses)
        self.klassList.setCurrentIndex(self.klassDict.get(self.klass, 0))
        label = QtGui.QLabel('Class:')
        label.setToolTip('Port Type. Can be String, File or Flag. List means an input list of one of the other types')
        layout1.addWidget(label)
        layout1.addWidget(self.klassList)
        # options are different for each widget
        # all args can have flag
        if self.argtype not in self.stdTypes:
            self.flag = QtGui.QLineEdit(self.options.get('flag', ''))
            label = QtGui.QLabel('flag:')
            label.setToolTip('a flag before your input. Example: "-f" -> "-f yourinput"')
            layout1.addWidget(label)
            layout1.addWidget(self.flag)
        
        if self.argtype not in self.stdTypes:
            # all args can have prefix
            self.prefix = QtGui.QLineEdit(self.options.get('prefix', ''))
            label = QtGui.QLabel('prefix:')
            label.setToolTip('a prefix to your input. Example: "--X=" -> "--X=yourinput"')
            layout1.addWidget(label)
            layout1.addWidget(self.prefix)

        # all can be required
        self.required = QtGui.QCheckBox()
        self.required.setChecked('required' in self.options)
        label = QtGui.QLabel('required:')
        label.setToolTip('Check to make port always visible in VisTrails')
        layout2.addWidget(label)
        layout2.addWidget(self.required)
        
        # subtype
        self.subList = ['String', 'File']
        self.subDict = dict(zip(self.subList, xrange(len(self.subList))))
        self.subDict.update(dict(zip([s.lower() for s in self.subList], xrange(len(self.subList)))))
        self.subtype = QtGui.QComboBox()
        self.subtype.addItems(self.subList)
        self.subtype.setCurrentIndex(self.subDict.get(self.options.get('type', 'String'), 0))
        self.listLabel = QtGui.QLabel('List type:')
        self.listLabel.setToolTip('Choose type of values in List')
        layout2.addWidget(self.listLabel)
        layout2.addWidget(self.subtype)
        self.listLabel.setVisible(self.klass == "List")
        self.subtype.setVisible(self.klass == "List")

        # description
        self.desc = QtGui.QLineEdit(self.options.get('desc', ''))
        label = QtGui.QLabel('description:')
        label.setToolTip('Add a helpful description of the port')
        layout2.addWidget(label)
        layout2.addWidget(self.desc)
        
        if self.argtype not in self.stdTypes:
            self.connect(self.klassList, QtCore.SIGNAL('currentIndexChanged(int)'),
                     self.klassChanged)

    def getValues(self):
        """ get the values from the widgets and store them """
        if self.argtype not in self.stdTypes:
            self.argtype = str(self.typeList.currentText())
        self.klass = str(self.klassList.currentText())
        self.name = str(self.nameLine.text())
        self.options = {}
        if self.argtype not in self.stdTypes:
            flag = str(self.flag.text()).strip()
            if flag:
                self.options['flag'] = flag
            prefix = str(self.prefix.text()).strip()
            if prefix:
                self.options['prefix'] = prefix
        desc = str(self.desc.text()).strip()
        if desc:
            self.options['desc'] = desc
        if self.required.isChecked():
            self.options['required'] = ''
        if self.klass == 'List':
            subtype = str(self.subtype.currentText()).strip()
            if subtype:
                self.options['type'] = subtype

    def setValues(self):
        if self.argtype not in self.stdTypes:
            self.typeList.setCurrentIndex(self.typeDict.get(self.argtype, 0))
        self.nameLine.setText(self.name)
        self.klassList.setCurrentIndex(self.klassDict.get(self.klass, 0))
        if self.argtype not in self.stdTypes:
            self.flag.setText(self.options.get('flag', ''))
            self.prefix.setText(self.options.get('prefix', ''))
            self.subtype.setCurrentIndex(self.subDict.get(self.options.get('type', 'String'), 0))
        self.required.setChecked('required' in self.options)
        self.desc.setText(self.options.get('desc', ''))
        self.klassChanged(None)
            
    def toList(self):
        self.getValues()
        if self.argtype not in self.stdTypes:
            return [self.argtype, self.name, self.klass, self.options]
        else:
            return [self.name, self.klass, self.options]
            
    def fromList(self, arg):
        if self.argtype not in self.stdTypes:
            self.argtype, self.name, self.klass, self.options = arg
        else:
            self.name, self.klass, self.options = arg
        self.setValues()

    def klassChanged(self, index):
        if self.argtype in self.stdTypes:
            return
        klass = str(self.klassList.currentText())
        self.listLabel.setVisible(klass == "List")
        self.subtype.setVisible(klass == "List")

    def guess(self, name, count=0):
        """ add argument by guessing what the arg might be """
        if '.' in name or '/' in name or '\\' in name: # guess file
            self.fromList(['Input', 'file%s' % count, 'File',
                           {'desc':'"%s" guessed to be an Input file' % name}])
        elif name.startswith('-'): # guess flag
            self.fromList(['Input', 'flag%s' % name, 'Flag',
                           {'desc':'"%s" guessed to be a flag' % name,
                            'flag':name}])
        else: # guess string
            self.fromList(['Input', 'input%s' % count, 'String',
                           {'desc':'"%s" guessed to be an input string' % name}])
            

class QManpageDialog(QtGui.QDialog):
    def __init__(self, title, text, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(title)
        text = "<pre>%s</pre>" % text
        self.textEdit = QtGui.QTextEdit(text)
        self.textEdit.setReadOnly(True)
        self.setLayout(QtGui.QHBoxLayout())
        self.layout().addWidget(self.textEdit)
        self.resize(800,600)

class QManpageImport(QtGui.QDialog):
    def __init__(self, title, args, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(title)
        self.argLayout = QtGui.QVBoxLayout()
        for arg in args:
            if arg[0] == 'Flag':
                w = QArgWidget(name=arg[1], options={'flag':arg[1],
                                                     'desc':arg[2]})
            else:
            #if arg[0] == 'String':
                w = QArgWidget(klass='String', name=arg[1],
                               options={'prefix':arg[1] + '=',
                                        'desc':arg[2]})
            widgetLayout = QtGui.QHBoxLayout()
            widgetLayout.addWidget(QtGui.QCheckBox())
            widgetLayout.addWidget(w)
            self.argLayout.addLayout(widgetLayout)
        scroll = QtGui.QScrollArea()
        w = QtGui.QWidget()
        w.setLayout(self.argLayout)
        scroll.setWidget(w)
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        scroll.setWidgetResizable(True)
        self.setLayout(QtGui.QVBoxLayout())
        self.layout().addWidget(scroll)
        layout2 = QtGui.QHBoxLayout()
        self.layout().addLayout(layout2)
        self.closeButton = QtGui.QPushButton('Close')
        self.closeButton.setToolTip('Close this window')
        self.connect(self.closeButton, QtCore.SIGNAL('clicked()'),
                     self.close)
        layout2.addWidget(self.closeButton)
        self.selectAllButton = QtGui.QPushButton('Select All')
        self.selectAllButton.setToolTip('Select All arguments')
        self.connect(self.selectAllButton, QtCore.SIGNAL('clicked()'),
                     self.selectAll)
        layout2.addWidget(self.selectAllButton)
        self.selectNoneButton = QtGui.QPushButton('Select None')
        self.selectNoneButton.setToolTip('Unselect All arguments')
        self.connect(self.selectNoneButton, QtCore.SIGNAL('clicked()'),
                     self.selectNone)
        layout2.addWidget(self.selectNoneButton)
        self.addSelectedButton = QtGui.QPushButton('Import Selected')
        self.addSelectedButton.setToolTip('Import all selected arguments')
        self.connect(self.addSelectedButton, QtCore.SIGNAL('clicked()'),
                     self.addSelected)
        layout2.addWidget(self.addSelectedButton)
        self.resize(800,600)

    def selectAll(self):
        for i in xrange(self.argLayout.count()):
            w = self.argLayout.layout().itemAt(i)
            w.layout().itemAt(0).widget().setChecked(True)
        
    def selectNone(self):
        for i in xrange(self.argLayout.count()):
            w = self.argLayout.layout().itemAt(i)
            w.layout().itemAt(0).widget().setChecked(False)

    def addSelected(self):
        # collect selected arguments and send through signal
        args = []
        remove_list = []
        for i in xrange(self.argLayout.count()):
            w = self.argLayout.layout().itemAt(i)
            if w.layout().itemAt(0).widget().isChecked():
                remove_list.append(w)
                args.append(w.layout().itemAt(1).widget())
        for w in remove_list:
            w.layout().itemAt(0).widget().setChecked(False)
            w.layout().itemAt(0).widget().hide()
            w.layout().itemAt(1).widget().hide()
            self.argLayout.removeItem(w)

        self.emit(QtCore.SIGNAL('importArgs(PyQt_PyObject)'), args)

class QCLToolsWizardWindow(QtGui.QMainWindow):

    def __init__(self, parent = None):
        QtGui.QMainWindow.__init__(self, parent)
        self.wizard = QCLToolsWizard(self)
        self.setCentralWidget(self.wizard)
        self.setWindowTitle("CLTools Wizard")
        self.resize(800,600)
        
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = QCLToolsWizardWindow()
    if len(sys.argv)>2 and sys.argv[1] == '-c':
        # read command from command line
        window.wizard.loadFromCommand(sys.argv[2:])
    window.show()
    app.exec_()

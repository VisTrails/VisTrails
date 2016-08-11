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

if __name__ == '__main__':
    import sip
    sip.setapi('QString', 2)
    sip.setapi('QVariant', 2)

import json
import os
import platform
import string
import subprocess
import sys
import threading
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

def quote_arg(arg):
    arg = arg.replace('\\', '\\\\')
    if '"' in arg or any(c in arg for c in string.whitespace):
        return '"%s"' % arg.replace('"', '\\"')
    else:
        return arg

# From: https://gist.github.com/kirpit/1306188
class Command(object):
    """
    Enables to run subprocess commands in a different thread with TIMEOUT option.
 
    Based on jcollado's solution:
    http://stackoverflow.com/questions/1191374/subprocess-with-timeout/4825933#4825933
    """
    command = None
    process = None
    status = None
    output, error = '', ''
 
    def __init__(self, command):
        self.command = command
 
    def run(self, timeout=5, **kwargs):
        """ Run a command then return: (status, output, error). """
        def target(**kwargs):
            try:
                self.process = subprocess.Popen(self.command, **kwargs)
                self.output, self.error = self.process.communicate()
                self.status = self.process.returncode
            except Exception:
                import traceback
                self.error = traceback.format_exc()
                self.status = -1
        # default stdout and stderr
        if 'stdout' not in kwargs:
            kwargs['stdout'] = subprocess.PIPE
        if 'stderr' not in kwargs:
            kwargs['stderr'] = subprocess.PIPE
        # thread
        print "calling with kwargs", target, kwargs
        thread = threading.Thread(target=target, kwargs=kwargs)
        thread.start()
        thread.join(timeout)
        if thread.is_alive():
            self.process.terminate()
            thread.join()
        return self.status, self.output, self.error

class QCLToolsWizard(QtGui.QWidget):
    def __init__(self, parent, reload_scripts=None):
        QtGui.QWidget.__init__(self, parent)

        self.vbox = QtGui.QVBoxLayout()
        self.vbox.setContentsMargins(5,5,5,5)

        self.setLayout(self.vbox)
        self.setTitle()
        self.file = None
        self.conf = None
        self.reload_scripts = reload_scripts

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

        if self.reload_scripts:
            self.reloadAction = QtGui.QAction(
                self.get_icon('view-refresh'), 'Refresh', self)
            self.reloadAction.setToolTip('Save and Reload CLTools Modules in VisTrails')
            self.connect(self.reloadAction, QtCore.SIGNAL('triggered()'),
                         self.refresh)
            self.toolBar.addAction(self.reloadAction)
        
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
        self.envPort = QtGui.QAction("env", self)
        self.envPort.setToolTip('Check to add the "env" input port for specifying environment variables')
        self.envPort.setCheckable(True)
        self.toolBar.addAction(self.envPort)
        
        self.toolBar.addSeparator()

        self.stdAsFiles = QtGui.QAction('std file processing', self)
        self.stdAsFiles.setToolTip('Check to make pipes communicate using files instead of strings\nOnly useful when processing large files')
        self.stdAsFiles.setCheckable(True)
        self.toolBar.addAction(self.stdAsFiles)

        self.failWithCmd = QtGui.QAction('fail execution if return != 0', self)
        self.failWithCmd.setToolTip('If selected, VisTrails will check the exitcode, and abort the execution if not 0')
        self.failWithCmd.setCheckable(True)
        self.failWithCmd.setChecked(True)
        self.toolBar.addAction(self.failWithCmd)

        self.toolBar.addSeparator()

        self.previewPorts = QtGui.QAction('preview', self)
        self.previewPorts.setToolTip('Check which ports will be available for this module')
        self.connect(self.previewPorts, QtCore.SIGNAL('triggered()'),
                     self.preview_ports)
        self.toolBar.addAction(self.previewPorts)

        
        self.envOption = None
        
        self.commandLayout = QtGui.QHBoxLayout()
        self.commandLayout.setContentsMargins(5,5,5,5)
        tooltip = 'The command to execute'
        label = QtGui.QLabel("Command:")
        label.setFixedWidth(80)
        label.setToolTip(tooltip)
        self.commandLayout.addWidget(label)
        self.command = QtGui.QLineEdit()
        self.command.setToolTip(tooltip)
        self.commandLayout.addWidget(self.command)
        tooltip = 'Sets directory to execute from. Leave blank to ignore.'
        label = QtGui.QLabel("Directory:")
        label.setToolTip(tooltip)
        self.commandLayout.addWidget(label)
        self.dir = QtGui.QLineEdit()
        self.dir.setFixedWidth(140)
        self.dir.setToolTip(tooltip)
        self.commandLayout.addWidget(self.dir)
        self.vbox.addLayout(self.commandLayout)

        self.previewLayout = QtGui.QHBoxLayout()
        self.previewLayout.setContentsMargins(5,5,5,5)
        self.previewLayout.setAlignment(QtCore.Qt.AlignLeft)
        tooltip = 'Shows what the command will look like when executed in the command line'
        label = QtGui.QLabel("Preview:")
        label.setToolTip(tooltip)
        label.setFixedWidth(80)
        self.previewLayout.addWidget(label)
        self.preview = QtGui.QLabel()
        self.preview.setToolTip(tooltip)
        self.preview.setMaximumWidth(600)
        self.previewLayout.addWidget(self.preview)
        self.vbox.addLayout(self.previewLayout)

        self.importLayout = QtGui.QHBoxLayout()
        self.importLayout.setContentsMargins(5,5,5,5)
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
        self.conf = None
        self.file = None
        self.command.clear()
        self.dir.clear()
        self.showStdin.setChecked(False)
        self.showStdout.setChecked(False)
        self.showStderr.setChecked(False)
        self.envPort.setChecked(False)
        self.envOption = None
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
        self.failWithCmd.setChecked(True)
        self.setTitle()
        self.generate_preview()
    
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
        self.dir.setText(conf.get('dir', ''))
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
        self.envPort.setChecked('options' in conf and
                                'env_port' in conf['options'])
        self.stdAsFiles.setChecked('options' in conf and
                                   'std_using_files' in conf['options'])
        self.failWithCmd.setChecked('options' in conf and
                                    'fail_with_cmd' in conf['options'])
        self.envOption = conf['options']['env'] \
                 if ('options' in conf and 'env' in conf['options']) else None
        self.conf = conf
        self.generate_preview()
            
    def get_current_conf(self):
        conf = {}
        conf['command'] = self.command.text()
        dir = self.dir.text()
        if dir:
            conf['dir'] = dir
            
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

        options = {}
        if self.stdAsFiles.isChecked():
            options['std_using_files'] = ''
        if self.failWithCmd.isChecked():
            options['fail_with_cmd'] = ''
        if self.envPort.isChecked():
            options['env_port'] = ''
        if self.envOption:
            options['env'] = self.envOption
        if options:
            conf['options'] = options
        return conf
    
    def save(self):
        if not self.file:
            self.saveAs()
            if not self.file:
                return
        self.conf = self.get_current_conf()
        f = open(self.file, "w")
        json.dump(self.conf, f, sort_keys=True, indent=4)
        f.close()
        self.generate_preview()

    def saveAs(self):
        fileName = QtGui.QFileDialog.getSaveFileName(self,
                            "Save Wrapper as",
                            self.file if self.file else default_dir(),
                            "Wrappers (*%s)" % SUFFIX)
        if fileName:
            self.file = fileName
            if not self.file.endswith(SUFFIX):
                self.file += SUFFIX
            self.save()
            self.setTitle(self.file)

    def refresh(self):
        self.save()
        self.reload_scripts()
    
    def generate_preview(self):
        # generate preview from self.conf
        c = self.get_current_conf()
        if not c:
            self.preview.setText('')
            self.preview.setToolTip('')
            return
        
        text = ''

        # show env as bash-style prefix
        if 'options' in c:
            o = c['options']
            # env_port
            if 'env_port' in o:
                text += '<env_port>'
            # env
            if 'env' in o:
                if text:
                    text += ' '
                text += c['options']['env']
            if text:
                text += ' '

        # command
        text += c['command']

        # args
        if 'args' in c:
            for type, name, klass, opts in c['args']:
                type = type.lower()
                klass = klass.lower()
                text += ' '
                if type == 'constant':
                    if 'flag' in opts:
                        text += opts['flag'] + ' '
                    text += quote_arg(name)
                    continue
                if 'required' not in opts:
                    text += '['
                if klass in 'list':
                    text += '{'
                if 'flag' in opts:
                    text += opts['flag']
                    if klass != 'flag':
                        text += ' '
                if 'prefix' in opts:
                    text += opts['prefix']
                if type!='input' or klass != 'flag':
                    text += '<'
                if klass == 'list':
                    text += opts['type'].lower() \
                            if ('type' in opts and opts['type']) else 'string'
                elif type=='input' and klass == 'flag':
                    if 'flag' not in opts:
                        text += quote_arg(name)
                elif type in ['output', 'inputoutput']:
                    text += 'file'
                else:
                    text += klass
                if type!='input' or klass != 'flag':
                    text += '>'
                if klass == 'list':
                    text += '}'
                if 'required' not in opts:
                    text += ']' 
                
        self.preview.setText(text)
        self.preview.setToolTip(text)

    def preview_ports(self):
        # show dialog with the ports that this module will have
        self.generate_preview()
        conf = self.get_current_conf()
        if not conf:
            return

        intext = []
        outtext = []

        if 'stdin' in conf:
            name, type, options = conf['stdin']
            optional = " (visible)" if "required" in options else ""
            intext.append("%s: %s%s" % (name, type, optional))
        if 'stdout' in conf:
            name, type, options = conf['stdout']
            optional = " (visible)" if "required" in options else ""
            outtext.append("%s: %s%s" % (name, type, optional))
        if 'stderr' in conf:
            name, type, options = conf['stderr']
            optional = " (visible)" if "required" in options else ""
            outtext.append("%s: %s%s" % (name, type, optional))
        if 'options' in conf and 'env_port' in conf['options']:
            intext.append('env: String')
        for type, name, klass, options in conf['args']:
            optional = " (visible)" if "required" in options else ""
            if 'input' == type.lower():
                intext.append("%s: %s%s" % (name, klass, optional))
            elif 'output' == type.lower():
                outtext.append("%s: %s%s" % (name, klass, optional))
            elif 'inputoutput' == type.lower():
                intext.append("%s: %s%s" % (name, 'File', optional))
                outtext.append("%s: %s%s" % (name, 'File', optional))
        
        intext = ''.join(['Input %s. %s\n' % (i+1, t)
                          for i, t in zip(xrange(len(intext)), intext)])
        outtext = ''.join(['Output %s. %s\n' % (i+1, t)
                            for i, t in zip(xrange(len(outtext)), outtext)])
        
        self.helppageView = QManpageDialog("Module Ports for this Wrapper",
                                     intext + "\n" + outtext, self)
        self.helppageView.show()
    
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
            command = Command(args)
            status, text, stderr = command.run(stdout=subprocess.PIPE,
                                               stderr=subprocess.PIPE,
                                               shell=True)
            if not (text and len(text)):
                text = stderr
                if not (text and len(text)) or (text and text.startswith('No ')):
                    return None
            # fix weird formatting
            for a, b in encode_list:
                text = text.replace(a, b)
            return text
        except Exception:
            return None
    
    def generateFromManPage(self):
        command = self.command.text()
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
        command = self.command.text()
        if command == '':
            return
        text = self.runProcess(['-c', command + ' -h'])
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
        command = self.command.text()
        if command == '':
            return
        text = self.runProcess(['-c', command + ' --help'])
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
        command = self.command.text()
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
        command = self.command.text()
        if command == '':
            return
        text = self.runProcess(['-c', command + ' -h'])
        if not text:
            QtGui.QMessageBox.warning(self, "Help page (-h) not found",
                                      "For command '%s'" % command)
            return
        title = "Help page for '%s'" % command
        self.helppageView = QManpageDialog(title, text, self)
        self.helppageView.show()

    def viewHelpPage2(self):
        command = self.command.text()
        if command == '':
            return
        text = self.runProcess(['-c', command + ' --help'])
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
    KLASSES = {
            'input': ['flag', 'file', 'path', 'directory',
                      'string', 'integer', 'float', 'list'],
            'output': ['file', 'string'],
            'inputoutput': ['file'],
            'stdin': ['file', 'string'],
            'stdout': ['file', 'string'],
            'stderr': ['file', 'string'],
        }
    KLASSNAMES = {
            'flag': 'Boolean flag',
            'string': 'String',
            'integer': 'Integer',
            'float': 'Float',
            'file': 'File',
            'path': 'Path',
            'directory': 'Directory',
            'list': 'List',
        }

    TYPES = ['input', 'output', 'inputoutput', 'constant']
    TYPENAMES = {
            'input': 'Input Port',
            'output': 'Output Port',
            'inputoutput': 'InputOutput Port',
            'constant': 'Constant',
        }

    def __init__(self, argtype='Input', name='untitled', klass='Flag', options={}, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.stdTypes = ['stdin', 'stdout', 'stderr']
        self.stdLabels = ['Standard input', 'Standard output', 'Standard error']
        self.stdDict = dict(zip(self.stdTypes, self.stdLabels))

        self.argtype = argtype.lower()
        self.name = name
        self.klass = klass.lower()
        self.options = options

        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)

        self.buildWidget()

    def buildWidget(self):
        layout = self.layout()
        layout.setContentsMargins(2,2,2,2)
        # remove any previous layout
        layout1 = QtGui.QHBoxLayout()
        layout1.setContentsMargins(2,2,2,2)
        layout.addLayout(layout1)
        if self.argtype not in self.stdTypes:
            layout2 = QtGui.QHBoxLayout()
            layout2.setContentsMargins(2,2,2,2)
            layout.addLayout(layout2)
        else:
            layout2 = layout1
        # type of argument
        if self.argtype not in self.stdTypes:
            self.typeList = QtGui.QComboBox()
            self.typeDict = {}
            for i, n in enumerate(self.TYPES):
                self.typeList.addItem(self.TYPENAMES[n], n)
                self.typeDict[n] = i
            self.typeList.setCurrentIndex(self.typeDict.get(self.argtype, 0))
            #label = QtGui.QLabel('Type:')
            tt = "Select if argument will be an input port, output port, both, or a hidden constant. InputOutput's are always files."
            #label.setToolTip(tt)
            self.typeList.setToolTip(tt)
            #layout1.addWidget(label)
            layout1.addWidget(self.typeList)
        else:
            self.typeList = None
        # type of port
        self.klassList = QtGui.QComboBox()
        klasses = self.KLASSES[self.argtype]
        self.klassDict = {}
        for i, n in enumerate(klasses):
            self.klassList.addItem(self.KLASSNAMES[n], n)
            self.klassDict[n] = i
        self.klassList.setCurrentIndex(self.klassDict.get(self.klass, 0))
        #label = QtGui.QLabel('Class:')
        tt = 'Port Type. Can be String, Integer, Float, File/Directory/Path or Boolean Flag. List means an input list of one of the other types. Only File and String should be used for output ports.'
        self.klassList.setToolTip(tt)
        #label.setToolTip(tt)
        #layout1.addWidget(label)
        layout1.addWidget(self.klassList)
        # name of port
        self.nameLine = QtGui.QLineEdit(self.name)
        label = QtGui.QLabel('Name:')
        tt = 'Name of the port, or the value for constants'
        label.setToolTip(tt)
        self.nameLine.setToolTip(tt)
        layout1.addWidget(label)
        layout1.addWidget(self.nameLine)
        # options are different for each widget
        if self.argtype not in self.stdTypes:
            # all args can have flag
            self.flag = QtGui.QLineEdit(self.options.get('flag', ''))
            label = QtGui.QLabel('Flag:')
            tt = 'a short-style flag before your input. Example: "-f" -> "-f yourinput"'
            label.setToolTip(tt)
            self.flag.setToolTip(tt)
            self.flag.setFixedWidth(100)
            layout1.addWidget(label)
            layout1.addWidget(self.flag)
        
            # all args can have prefix
            self.prefix = QtGui.QLineEdit(self.options.get('prefix', ''))
            label = QtGui.QLabel('Prefix:')
            tt = 'a long-style prefix to your input. Example: "--X=" -> "--X=yourinput"'
            label.setToolTip(tt)
            self.prefix.setToolTip(tt)
            layout1.addWidget(label)
            layout1.addWidget(self.prefix)

        # all can be required
        self.required = QtGui.QCheckBox()
        self.required.setChecked('required' in self.options)
        label = QtGui.QLabel('Visible:')
        tt = 'Check to make port always visible in VisTrails'
        label.setToolTip(tt)
        self.required.setToolTip(tt)
        layout2.addWidget(label)
        layout2.addWidget(self.required)
        
        # subtype
        self.subList = ['String', 'Integer', 'Float', 'File', 'Directory', 'Path']
        self.subDict = dict(zip(self.subList, xrange(len(self.subList))))
        self.subDict.update(dict(zip([s.lower() for s in self.subList], xrange(len(self.subList)))))
        self.subtype = QtGui.QComboBox()
        self.subtype.addItems(self.subList)
        self.subtype.setCurrentIndex(self.subDict.get(self.options.get('type', 'String'), 0))
        self.listLabel = QtGui.QLabel('List type:')
        self.subtype.setVisible(False)
        tt = 'Choose type of values in List'
        self.subtype.setToolTip(tt)
        self.listLabel.setToolTip(tt)
        layout2.addWidget(self.listLabel)
        layout2.addWidget(self.subtype)
        self.listLabel.setVisible(False)
        self.subtype.setVisible(False)
        
        # input files and inputoutput's can set file suffix
        self.suffix = QtGui.QLineEdit(self.options.get('suffix', ''))
        self.suffixLabel = QtGui.QLabel('File suffix:')
        tt = 'Sets the specified file ending on the created file, like for example: ".txt"'
        self.suffixLabel.setToolTip(tt)
        self.suffix.setToolTip(tt)
        self.suffix.setFixedWidth(50)
        layout2.addWidget(self.suffixLabel)
        layout2.addWidget(self.suffix)

        self.typeChanged()
        self.klassChanged()

        # description
        self.desc = QtGui.QLineEdit(self.options.get('desc', ''))
        label = QtGui.QLabel('Description:')
        tt = 'Add a helpful description of the port'
        label.setToolTip(tt)
        self.desc.setToolTip(tt)
        layout2.addWidget(label)
        layout2.addWidget(self.desc)
        
        if self.argtype not in self.stdTypes:
            self.connect(self.klassList, QtCore.SIGNAL('currentIndexChanged(int)'),
                     self.klassChanged)
            self.connect(self.typeList, QtCore.SIGNAL('currentIndexChanged(int)'),
                     self.typeChanged)

    def getValues(self):
        """ get the values from the widgets and store them """
        self.klass = self.klassList.itemData(self.klassList.currentIndex())
        self.name = self.nameLine.text()
        self.options = {}
        if self.argtype not in self.stdTypes:
            flag = self.flag.text()
            if flag:
                self.options['flag'] = flag
            prefix = self.prefix.text()
            if prefix:
                self.options['prefix'] = prefix
        desc = self.desc.text()
        if desc:
            self.options['desc'] = desc
        if self.required.isChecked():
            self.options['required'] = ''
        if self.klass == 'list':
            subtype = self.subtype.currentText()
            if subtype:
                self.options['type'] = subtype
        type = self.argtype.lower()
        suffix = self.suffix.text()
        if (type == 'output' or type == 'inputoutput') and suffix:
            self.options['suffix'] = suffix

    def setValues(self):
        if self.argtype not in self.stdTypes:
            self.typeList.setCurrentIndex(self.typeDict.get(self.argtype, 0))
        self.nameLine.setText(self.name)
        self.klassList.setCurrentIndex(self.klassDict[self.klass])
        if self.argtype not in self.stdTypes:
            self.flag.setText(self.options.get('flag', ''))
            self.prefix.setText(self.options.get('prefix', ''))
            self.subtype.setCurrentIndex(self.subDict.get(self.options.get('type', 'String')))
            self.subtype.setCurrentIndex(self.subDict.get(self.options.get('type', 'String'), 0))
        self.required.setChecked('required' in self.options)
        self.desc.setText(self.options.get('desc', ''))
        type = self.argtype.lower()
        if type == 'output' or type == 'inputoutput':
            self.suffix.setText(self.options.get('suffix', ''))
        self.typeChanged()
        self.klassChanged()

    def toList(self):
        self.getValues()
        if self.argtype not in self.stdTypes:
            return [self.argtype, self.name, self.klass, dict(self.options)]
        else:
            return [self.name, self.klass, dict(self.options)]

    def fromList(self, arg):
        if self.argtype not in self.stdTypes:
            self.argtype, self.name, klass, self.options = arg
        else:
            self.name, klass, self.options = arg
        self.klass = klass.lower()
        self.setValues()

    def klassChanged(self, index=None):
        if self.argtype in self.stdTypes:
            return
        klass = self.klassList.itemData(self.klassList.currentIndex())
        type = self.typeList.itemData(self.typeList.currentIndex())
        self.listLabel.setVisible(klass == "list" and type == 'input')
        self.subtype.setVisible(klass == "list" and type == 'input')

    def typeChanged(self, index=None):
        if self.argtype in self.stdTypes:
            return
        type = self.typeList.itemData(self.typeList.currentIndex())
        if index is not None and type == self.argtype:
            return
        self.argtype = type
        if type in ('constant', 'inputoutput'):
            self.klassList.hide()
        else:
            self.klassList.show()
            self.klassList.clear()
            klasses = self.KLASSES[self.argtype]
            self.klassDict = {}
            for i, n in enumerate(klasses):
                self.klassList.addItem(self.KLASSNAMES[n], n)
                self.klassDict[n] = i
            self.klassList.setCurrentIndex(self.klassDict.get(self.klass, 0))
        self.suffixLabel.setVisible(type == 'output' or type == 'inputoutput')
        self.suffix.setVisible(type == 'output' or type == 'inputoutput')

    def guess(self, name, count=0):
        """ add argument by guessing what the arg might be """
        if '.' in name or '/' in name or '\\' in name: # guess path
            if os.path.isfile(name):
                guessed, type_ = 'file', 'File'
            elif os.path.isdir(name):
                guessed, type_ = 'directory', 'Directory'
            else:
                guessed, type_ = 'path', 'Path'
            self.fromList(['Input', '%s%d' % (guessed, count), type_,
                           {'desc':'"%s" guessed to be an Input %s' % (name, guessed)}])
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

    def __init__(self, parent=None, reload_scripts=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.wizard = QCLToolsWizard(self, reload_scripts)
        self.setCentralWidget(self.wizard)
        self.setWindowTitle("CLTools Wizard")
        self.resize(1000,600)
        
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = QCLToolsWizardWindow()
    if len(sys.argv)>2 and sys.argv[1] == '-c':
        # read command from command line
        window.wizard.loadFromCommand(sys.argv[2:])
    window.show()
    app.exec_()

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
""" This module defines the following classes:
    - QShellDialog
    - QShell

QShell is based on ideas and code from PyCute developed by Gerard Vermeulen.
Used with the author's permission.
More information on PyCute, visit:
http://gerard.vermeulen.free.fr/html/pycute-intro.html

"""
from PyQt4 import QtGui, QtCore
from code import InteractiveInterpreter
import copy
import sys
import time
import os.path

import vistrails.api
from vistrails.core.configuration import get_vistrails_configuration
from vistrails.core.interpreter.default import get_default_interpreter
import vistrails.core.modules.module_registry
from vistrails.core.modules.utils import create_port_spec_string
import vistrails.core.system
from vistrails.core.system import strftime
from vistrails.core.vistrail.port_spec import PortSpec
from vistrails.gui.vistrails_palette import QVistrailsPaletteInterface
from vistrails.core.utils import all

################################################################################

class QShellDialog(QtGui.QWidget, QVistrailsPaletteInterface):
    """This class incorporates the QShell into a dockable widget for use in the
    VisTrails environment"""
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent=parent)
        #locals() returns the original dictionary, not a copy as
        #the docs say
        self.firstLocals = copy.copy(locals())
        self.shell = QShell(self.firstLocals,None)
        layout = QtGui.QVBoxLayout()
        layout.setMargin(0)
        layout.setSpacing(0)
        layout.addWidget(self.shell)
        self.setLayout(layout)
        # self.setWidget(self.shell)
        self.setWindowTitle(self.shell.windowTitle())
        # self.setTitleBarWidget(QtGui.QLabel(self.shell.windowTitle()))
        # self.monitorWindowTitle(self.shell)
        self.vistrails_interpreter = get_default_interpreter()
    
    def createMenu(self):
        """createMenu() -> None
        Creates a menu bar and adds it to the main layout.

        """
        self.newSessionAct = QtGui.QAction("&Restart",self)
        self.newSessionAct.setShortcut("Ctrl+R")
        self.connect(self.newSessionAct, QtCore.SIGNAL("triggered()"),
                     self.newSession)

        self.saveSessionAct = QtGui.QAction("&Save", self)
        self.saveSessionAct.setShortcut("Ctrl+S")
        self.connect(self.saveSessionAct, QtCore.SIGNAL("triggered()"),
                     self.saveSession)

        self.closeSessionAct = QtGui.QAction("Close", self)
        self.closeSessionAct.setShortcut("Ctrl+W")
        self.connect(self.closeSessionAct,QtCore.SIGNAL("triggered()"), 
                     self.closeSession)
        
        self.menuBar = QtGui.QMenuBar(self)
        menu = self.menuBar.addMenu("&Session")
        menu.addAction(self.newSessionAct)
        menu.addAction(self.saveSessionAct)
        menu.addAction(self.closeSessionAct)

        self.layout().setMenuBar(self.menuBar)

    def closeEvent(self, e):
        """closeEvent(e) -> None
        Event handler called when the dialog is about to close."""
        self.closeSession()
        self.emit(QtCore.SIGNAL("shellHidden()"))
    
    def showEvent(self, e):
        """showEvent(e) -> None
        Event handler called when the dialog acquires focus 

        """
        self.shell.show()

    def closeSession(self):
        """closeSession() -> None.
        Hides the dialog instead of closing it, so the session continues open.

        """
        self.hide()

    def newSession(self):
        """newSession() -> None
        Tells the shell to start a new session passing a copy of the original
        locals dictionary.

        """
        self.shell.restart(copy.copy(self.firstLocals))

    def saveSession(self):
        """saveSession() -> None
        Opens a File Save dialog and passes the filename to shell's saveSession.

        """
        default = 'visTrails' + '-' + strftime("%Y%m%d-%H%M.log")
        default = os.path.join(vistrails.core.system.vistrails_file_directory(),default)
        fileName = QtGui.QFileDialog.getSaveFileName(self,
                                                     "Save Session As..",
                                                     default,
                                                     "Log files (*.log)")
        if not fileName:
            return

        self.shell.saveSession(str(fileName))

    def visibility_changed(self, visible):
        QVistrailsPaletteInterface.visibility_changed(self, visible)
        if visible:
            self.shell.show()
        else:
            self.shell.hide()

##############################################################################
# QShell
        

class vistrails_port(object):
    def __init__(self, vistrails_module, port_spec):
        # print 'calling vistrails_port.__init__'
        self._vistrails_module = vistrails_module
        self._port_spec = port_spec

    def __call__(self, *args, **kwargs):
        if len(args) + len(kwargs) > 0:
            self._vistrails_module._update_func(self._port_spec,
                                                *args, **kwargs)
            return None
        return self

class vistrails_module(object):
    def __init__(self, *args, **kwargs):
        if not hasattr(self, '_module'):
            self._module = \
                vistrails.api.add_module_from_descriptor(self._module_desc)
            # FIXME if constant, we can use args
            module_desc = self._module_desc
            for attr_name, value in kwargs.iteritems():
                self._process_attr_value(attr_name, value)

    def _process_attr_value(self, attr_name, value):
        if self._module.has_port_spec(attr_name, 'input'):
            port_spec = self._module.get_port_spec(attr_name, 'input')

            args = None
            # FIXME want this to be any iterable
            if isinstance(value, tuple):
                args = value
            else:
                args = (value,)
            self._update_func(port_spec, *args)
        else:
            raise AttributeError("type object '%s' has no "
                                 "attribute '%s'" % \
                                     (self.__class__.__name__,
                                      attr_name))                

    def __getattr__(self, attr_name):
        def create_port(port_spec):
            return vistrails_port(self, port_spec)
        try:
            return self.__dict__[attr_name]
        except KeyError:
            if self._module.has_port_spec(attr_name, 'output'):
                port_spec = \
                    self._module.get_port_spec(attr_name, 'output')
                return create_port(port_spec)
            elif self._module.has_port_spec(attr_name, 'input'):
                port_spec = \
                    self._module.get_port_spec(attr_name, 'input')
                return create_port(port_spec)
            else:
                raise AttributeError("type object '%s' has no "
                                     "attribute '%s'" % \
                                         (self.__class__.__name__, 
                                          attr_name))

    def __setattr__(self, attr_name, value):
        if attr_name.startswith('_'):
            self.__dict__[attr_name] = value
        else:
            self._process_attr_value(attr_name, value)

    def _update_func(self, port_spec, *args, **kwargs):
        # print 'running _update_func', port_spec.name
        # print args

        if port_spec.type != 'input':
            if self._module.has_port_spec(port_spec.name, 'input'):
                port_spec = \
                    self._module.get_port_spec(port_spec.name, 'input')
            else:
                raise TypeError("cannot update an output port spec")

        # FIXME deal with kwargs
        num_ports = 0
        num_params = 0
        for value in args:
            # print 'processing', type(value), value
            if isinstance(value, vistrails_port):
                # make connection to specified output port
                # print 'updating port'
                num_ports += 1
            elif isinstance(value, vistrails_module):
                # make connection to 'self' output port of value
                # print 'updating module'
                num_ports += 1
            else:
                # print 'update literal', type(value), value
                num_params += 1
        if num_ports > 1 or (num_ports == 1 and num_params > 0):
            reg = vistrails.core.modules.module_registry.get_module_registry()
            tuple_desc = reg.get_descriptor_by_name(
                vistrails.core.system.get_vistrails_basic_pkg_id(), 'Tuple')

            d = {'_module_desc': tuple_desc,
                 '_package': self._package,}
            tuple = type('module', (vistrails_module,), d)()

            output_port_spec = PortSpec(id=-1,
                                        name='value',
                                        type='output',
                                        sigstring=port_spec.sigstring)
            vistrails.api.add_port_spec(tuple._module.id, output_port_spec)
            self._update_func(port_spec, *[tuple.value()])
            assert len(port_spec.descriptors()) == len(args)
            for i, descriptor in enumerate(port_spec.descriptors()):
                arg_name = 'arg%d' % i
                sigstring = create_port_spec_string([descriptor.spec_tuple])
                tuple_port_spec = PortSpec(id=-1,
                                           name=arg_name,
                                           type='input',
                                           sigstring=sigstring)
                vistrails.api.add_port_spec(tuple._module.id, tuple_port_spec)
                tuple._process_attr_value(arg_name, args[i])
                
                
            # create tuple object
            pass
        elif num_ports == 1:
            other = args[0]
            if isinstance(other, vistrails_port):
                if other._port_spec.type != 'output':
                    other_module = other._vistrails_module._module
                    if other_module.has_port_spec(port_spec.name, 
                                                   'output'):
                        other_port_spec = \
                            other_module.get_port_spec(port_spec.name, 
                                                        'output')
                    else:
                        raise TypeError("cannot update an input "
                                        "port spec")
                else:
                    other_port_spec = other._port_spec

                vistrails.api.add_connection(other._vistrails_module._module.id,
                                   other_port_spec,
                                   self._module.id, 
                                   port_spec)
            elif isinstance(other, vistrails_module):
                other_port_spec = \
                    other._module.get_port_spec('self', 'output')
                vistrails.api.add_connection(other._module.id, 
                                   other_port_spec,
                                   self._module.id,
                                   port_spec)
        else:
            vistrails.api.change_parameter(self._module.id,
                                 port_spec.name,
                                 [str(x) for x in args])

class QShell(QtGui.QTextEdit):
    """This class embeds a python interperter in a QTextEdit Widget
    It is based on PyCute developed by Gerard Vermeulen.
    
    """
    def __init__(self, locals=None, parent=None):
        """Constructor.

        The optional 'locals' argument specifies the dictionary in which code
        will be executed; it defaults to a newly created dictionary with key 
        "__name__" set to "__console__" and key "__doc__" set to None.

        The optional 'log' argument specifies the file in which the interpreter
        session is to be logged.
        
        The optional 'parent' argument specifies the parent widget. If no parent
        widget has been specified, it is possible to exit the interpreter 
        by Ctrl-D.

        """

        QtGui.QTextEdit.__init__(self, parent)
        self.setReadOnly(False)
        self.setWindowTitle("Console")
        # to exit the main interpreter by a Ctrl-D if QShell has no parent
        if parent is None:
            self.eofKey = QtCore.Qt.Key_D
        else:
            self.eofKey = None

        # flag for knowing when selecting text
        self.selectMode = False
        self.interpreter = None
        self.controller = None
        # storing current state
        #this is not working on mac
        #self.prev_stdout = sys.stdout
        #self.prev_stdin = sys.stdin
        #self.prev_stderr = sys.stderr
        # capture all interactive input/output
        #sys.stdout   = self
        #sys.stderr   = self
        #sys.stdin    = self
        
        # user interface setup
        
        self.setAcceptRichText(False)
        self.setWordWrapMode(QtGui.QTextOption.WrapAnywhere)
        
        conf = get_vistrails_configuration()
        shell_conf = conf.shell
        # font
        font = QtGui.QFont(shell_conf.fontFace, shell_conf.fontSize)
        font.setFixedPitch(1)
        self.setFont(font)
        self.reset(locals)

    def load_package(self, pkg_name):
        reg = vistrails.core.modules.module_registry.get_module_registry()
        package = reg.get_package_by_name(pkg_name)
        
        def create_dict(modules, ns, m, mdesc):
            md = {}
            if len(ns) == 0:
                d = {'_module_desc': mdesc,
                     '_package': pkg,}
                modules[m] = type('module', (vistrails_module,), d)
            else:
                if ns[0] in modules:
                    md = create_dict(modules[ns[0]], ns[1:], m, mdesc)
                else:
                    md = create_dict(md, ns[1:], m, mdesc)
                    modules[ns[0]] = md
            return modules
        
        def create_namespace_path(root, modules):
            for k,v in modules.iteritems():
                if isinstance(v, dict):
                    d = create_namespace_path(k,v)
                    modules[k] = d
            
            if root is not None:
                modules['_package'] = pkg
                return type(root, (object,), modules)()
            else:
                return modules
        
        def get_module_init(module_desc):
            def init(self, *args, **kwargs):
                self.__dict__['module'] = \
                    vistrails.api.add_module_from_descriptor(module_desc)
            return init
        
        def get_module(package):
            def getter(self, attr_name):
                desc_tuple = (attr_name, '')
                if desc_tuple in package.descriptors:
                    module_desc = package.descriptors[desc_tuple]
                    d = {'_module_desc': module_desc,
                         '_package': self,}
                    return type('module', (vistrails_module,), d)
                else:
                    raise AttributeError("type object '%s' has no attribute "
                                         "'%s'" % (self.__class__.__name__, 
                                                   attr_name))
            return getter
        
        d = {'__getattr__': get_module(package),}
        pkg = type(package.name, (object,), d)()
        
        modules = {}
        for (m,ns) in package.descriptors:
            module_desc = package.descriptors[(m,ns)]
            modules = create_dict(modules, ns.split('|'), m, module_desc)   
        
        modules = create_namespace_path(None, modules)
        
        for (k,v) in modules.iteritems():
            setattr(pkg, k, v)
        return pkg

    def selected_modules(self):
        shell_modules = []
        modules = vistrails.api.get_selected_modules()
        for module in modules:
            d = {'_module': module}
            shell_modules.append(type('module', (vistrails_module,), d)())
        return shell_modules

    def reset(self, locals):
        """reset(locals) -> None
        Reset shell preparing it for a new session.
        
        """
        locals['load_package'] = self.load_package
        locals['selected_modules'] = self.selected_modules
        if self.interpreter:
            del self.interpreter
        self.interpreter = InteractiveInterpreter(locals)
 
        # last line + last incomplete lines
        self.line    = ''
        self.lines   = []
        # the cursor position in the last line
        self.point   = 0
        # flag: the interpreter needs more input to run the last lines. 
        self.more    = 0
        # flag: readline() is being used for e.g. raw_input() and input()
        self.reading = 0
        # history
        self.history = []
        self.pointer = 0
        self.last   = 0
                # interpreter prompt.
        if hasattr(sys, "ps1"):
            sys.ps1
        else:
            sys.ps1 = ">>> "
        if hasattr(sys, "ps2"):
            sys.ps2
        else:
            sys.ps2 = "... "
        
        # interpreter banner
        
        self.write('VisTrails shell running Python %s on %s.\n' %
                   (sys.version, sys.platform))
        self.write('Type "copyright", "credits" or "license"'
                   ' for more information on Python.\n')
        self.write(sys.ps1)


    def flush(self):
        """flush() -> None. 
        Simulate stdin, stdout, and stderr.
        
        """
        pass

    def isatty(self):
        """isatty() -> int
        Simulate stdin, stdout, and stderr.
        
        """
        return 1

    def readline(self):
        """readline() -> str
        
        Simulate stdin, stdout, and stderr.
        
        """
        self.reading = 1
        self.__clearLine()
        cursor = self.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        self.setTextCursor(cursor)
      
        while self.reading:
            qApp.processOneEvent()
        if len(self.line) == 0:
            return '\n'
        else:
            return self.line 
    
    def write(self, text):
        """write(text: str) -> None
        Simulate stdin, stdout, and stderr.
        
        """
                
        cursor = self.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.clearSelection()
        self.setTextCursor(cursor)
        self.insertPlainText(text)
        cursor = self.textCursor()
        self.last = cursor.position()

    def insertFromMimeData(self, source):
        if source.hasText():
            cursor = self.textCursor()
            cursor.movePosition(QtGui.QTextCursor.End)
            cursor.clearSelection()
            self.setTextCursor(cursor)
            self.__insertText(source.text())
        
    def scroll_bar_at_bottom(self):
        """Returns true if vertical bar exists and is at bottom, or if
        vertical bar does not exist."""
        bar = self.verticalScrollBar()
        if not bar:
            return True
        return bar.value() == bar.maximum()
        
    def __run(self):
        """__run() -> None
        Append the last line to the history list, let the interpreter execute
        the last line(s), and clean up accounting for the interpreter results:
        (1) the interpreter succeeds
        (2) the interpreter fails, finds no errors and wants more line(s)
        (3) the interpreter fails, finds errors and writes them to sys.stderr
        
        """
        cursor = self.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        self.setTextCursor(cursor)
        # self.set_controller()
        should_scroll = self.scroll_bar_at_bottom()
        self.pointer = 0
        self.history.append(self.line)
        self.lines.append(self.line)
        source = '\n'.join(self.lines)
        self.write('\n')
        self.more = self.interpreter.runsource(source)
        if self.more:
            self.write(sys.ps2)
        else:
            self.write(sys.ps1)
            self.lines = []
        self.__clearLine()
        if should_scroll:
            bar = self.verticalScrollBar()
            if bar:
                bar.setValue(bar.maximum())

    def __clearLine(self):
        """__clearLine() -> None
        Clear input line buffer.
        
        """
        self.line = ""
        self.point = 0
        
    def __insertText(self, text):
        """__insertText(text) -> None
        Insert text at the current cursor position.
        
        """
        self.insertPlainText(text)
        self.line = self.line[:self.point] + text + self.line[self.point:]
        self.point += len(text)

    # def add_pipeline(self, p):
    #     """
    #     add_pipeline(p) -> None
    #     Set the active pipeline in the command shell.  This replaces the modules
    #     variable with the list of current active modules of the selected pipeline.
    #     """
    #     if self.controller:
    #         self.interpreter.active_pipeline = self.controller.current_pipeline
    #     else:
    #         self.interpreter.active_pipeline = p
    #     cmd = 'active_pipeline = self.shell.interpreter.active_pipeline'
    #     self.interpreter.runcode(cmd)
    #     cmd = 'modules = self.vistrails_interpreter.find_persistent_entities(active_pipeline)[0]'
    #     self.interpreter.runcode(cmd)

    def set_controller(self, controller=None):
        """set_controller(controller: VistrailController) -> None
        Set the current VistrailController on the shell.
        """
        self.controller = controller
        if controller:
            self.interpreter.active_pipeline = self.controller.current_pipeline
            cmd = 'active_pipeline = self.shell.interpreter.active_pipeline'
            self.interpreter.runcode(cmd)
            cmd = 'modules = self.vistrails_interpreter.' \
                'find_persistent_entities(active_pipeline)[0]'
            self.interpreter.runcode(cmd)

    # def set_pipeline(self):
    #     """set_active_pipeline() -> None
    #     Makes sure that the pipeline being displayed is present in the shell for
    #     direct inspection and manipulation
    #     """
    #     self.add_pipeline(None)
        
    def keyPressEvent(self, e):
        """keyPressEvent(e) -> None
        Handle user input a key at a time.

        Notice that text might come more than one keypress at a time
        if user is a fast enough typist!
        
        """
        text  = e.text()
        key   = e.key()

        # NB: Sometimes len(str(text)) > 1!
        if len(text) and all(ord(x) >= 32 and
                             ord(x) < 127
                             for x in str(text)):
        # exit select mode and jump to end of text
            cursor = self.textCursor()
            if self.selectMode or cursor.hasSelection():
                self.selectMode = False
                cursor.movePosition(QtGui.QTextCursor.End)
                cursor.clearSelection()
                self.setTextCursor(cursor)
            self.__insertText(text)
            return
 
        if e.modifiers() & QtCore.Qt.MetaModifier and key == self.eofKey:
            self.parent().closeSession()
        
        if e.modifiers() & QtCore.Qt.ControlModifier:
            if key == QtCore.Qt.Key_C or key == QtCore.Qt.Key_Insert:
                self.copy()
            elif key == QtCore.Qt.Key_V:
                cursor = self.textCursor()
                cursor.movePosition(QtGui.QTextCursor.End)
                cursor.clearSelection()
                self.setTextCursor(cursor)
                self.paste()
            elif key == QtCore.Qt.Key_A:
                self.selectAll()
                self.selectMode = True
            else:
                e.ignore()
            return

        if e.modifiers() & QtCore.Qt.ShiftModifier:
            if key == QtCore.Qt.Key_Insert:
                cursor = self.textCursor()
                cursor.movePosition(QtGui.QTextCursor.End)
                cursor.clearSelection()
                self.setTextCursor(cursor)
                self.paste()
            else:
                e.ignore()
            return

        # exit select mode and jump to end of text
        cursor = self.textCursor()
        if self.selectMode or cursor.hasSelection():
            self.selectMode = False
            cursor.movePosition(QtGui.QTextCursor.End)
            cursor.clearSelection()
            self.setTextCursor(cursor)

        if key == QtCore.Qt.Key_Backspace:
            if self.point:
                QtGui.QTextEdit.keyPressEvent(self, e)
                self.point -= 1
                self.line = self.line[:self.point] + self.line[self.point+1:]
        elif key == QtCore.Qt.Key_Delete:
            QtGui.QTextEdit.keyPressEvent(self, e)
            self.line = self.line[:self.point] + self.line[self.point+1:]
        elif key == QtCore.Qt.Key_Return or key == QtCore.Qt.Key_Enter:
            if self.reading:
                self.reading = 0
            else:
                self.__run()
        elif key == QtCore.Qt.Key_Tab:
            self.__insertText(text)
        elif key == QtCore.Qt.Key_Left:
            if self.point:
                QtGui.QTextEdit.keyPressEvent(self, e)
                self.point -= 1
        elif key == QtCore.Qt.Key_Right:
            if self.point < len(self.line):
                QtGui.QTextEdit.keyPressEvent(self, e)
                self.point += 1
        elif key == QtCore.Qt.Key_Home:
            cursor = self.textCursor()
            cursor.movePosition(QtGui.QTextCursor.StartOfLine)
            cursor.setPosition(cursor.position() + 4)
            self.setTextCursor(cursor)
            self.point = 0
        elif key == QtCore.Qt.Key_End:
            QtGui.QTextEdit.keyPressEvent(self, e)
            self.point = len(self.line)
        elif key == QtCore.Qt.Key_Up:
            if len(self.history):
                if self.pointer == 0:
                    self.pointer = len(self.history)
                self.pointer -= 1
                self.__recall()
        elif key == QtCore.Qt.Key_Down:
            if len(self.history):
                self.pointer += 1
                if self.pointer == len(self.history):
                    self.pointer = 0
                self.__recall()
        else:
            e.ignore()

    def __recall(self):
        """__recall() -> None
        Display the current item from the command history.
        
        """
        cursor = self.textCursor()
        cursor.setPosition(self.last)
        
        cursor.select(QtGui.QTextCursor.LineUnderCursor)

        cursor.removeSelectedText()
        self.setTextCursor(cursor)
        self.insertPlainText(sys.ps1)
        self.__clearLine()
        self.__insertText(self.history[self.pointer])

        
    def focusNextPrevChild(self, next):
        """focusNextPrevChild(next) -> None
        Suppress tabbing to the next window in multi-line commands. 
        
        """
        if next and self.more:
            return 0
        return QtGui.QTextEdit.focusNextPrevChild(self, next)

    def mousePressEvent(self, e):
        """mousePressEvent(e) -> None
        Keep the cursor after the last prompt.
        """
        if e.button() == QtCore.Qt.LeftButton:
            self.selectMode = True
            QtGui.QTextEdit.mousePressEvent(self, e)
#            cursor = self.textCursor()
#            cursor.movePosition(QtGui.QTextCursor.End)
#            self.setTextCursor(cursor)
        return

    def hide(self):
        """suspend() -> None
        Called when hiding the parent window in order to recover the previous
        state.

        """
        #recovering the state
        sys.stdout   = sys.__stdout__
        sys.stderr   = sys.__stderr__
        sys.stdin    = sys.__stdin__

    def show(self):
        """show() -> None
        Store previous state and starts capturing all interactive input and 
        output.
        
        """
        # capture all interactive input/output
        sys.stdout   = self
        sys.stderr   = self
        sys.stdin    = self
        self.setFocus()

    def saveSession(self, fileName):
        """saveSession(fileName: str) -> None 
        Write its contents to a file """
        output = open(str(fileName), 'w')
        output.write(self.toPlainText())
        output.close()

    def restart(self, locals=None):
        """restart(locals=None) -> None 
        Restart a new session 

        """
        self.clear()
        self.reset(locals)

    def contentsContextMenuEvent(self,ev):
        """
        contentsContextMenuEvent(ev) -> None
        Suppress the right button context menu.
        
        """
        return

################################################################################

def getIPythonDialog():
    from IPython.qt.console.rich_ipython_widget import RichIPythonWidget
    from IPython.qt.inprocess import QtInProcessKernelManager
#    from IPython.kernel.inprocess.ipkernel import InProcessKernel

    km = QtInProcessKernelManager()
    km.start_kernel()
    kernel = km.kernel
    kernel.gui = 'qt4'

    kernel_client = km.client()
    kernel_client.start_channels()

    def stop():
        kernel_client.stop_channels()
        km.shutdown_kernel()

    class IPythonDialog(RichIPythonWidget, QVistrailsPaletteInterface):
        """This class incorporates an  IPython shell into a dockable widget for use in the
        VisTrails environment"""
        def __init__(self, parent=None):
            RichIPythonWidget.__init__(self, parent)
            self.running_workflow = False
            self.kernel_manager = km
            self.kernel_client = kernel_client
            self.exit_requested.connect(stop)
            #locals() returns the original dictionary, not a copy as
            #the docs say
    #        self.firstLocals = copy.copy(locals())
    #        self.shell = IPythonXXX(self.firstLocals,None)
    #        layout = QtGui.QVBoxLayout()
    #        layout.setMargin(0)
    #        layout.setSpacing(0)
    #        layout.addWidget(self.shell)
    #        self.setLayout(layout)
            # self.setWidget(self.shell)
            self.setWindowTitle("Console")
            # self.setTitleBarWidget(QtGui.QLabel(self.shell.windowTitle()))
            # self.monitorWindowTitle(self.shell)
            self.vistrails_interpreter = get_default_interpreter()

        def visibility_changed(self, visible):
            QVistrailsPaletteInterface.visibility_changed(self, visible)
            if visible:
                self.show()
            else:
                self.hide()

        def hide(self):
            """suspend() -> None
            Called when hiding the parent window in order to recover the previous
            state.
    
            """
            #recovering the state
            sys.stdout   = sys.__stdout__
            sys.stderr   = sys.__stderr__
            sys.stdin    = sys.__stdin__
            RichIPythonWidget.hide(self)
    
        def show(self):
            """show() -> None
            Store previous state and starts capturing all interactive input and 
            output.
            
            """
            # capture all interactive input/output
            sys.stdout   = self
            sys.stderr   = self
            sys.stdin    = self
            RichIPythonWidget.show(self)

        def showEvent(self, e):
            """showEvent(e) -> None
            Event handler called when the dialog acquires focus 
    
            """
            self.show()

        def flush(self):
            """flush() -> None. 
            Simulate stdin, stdout, and stderr.
            
            """
            pass
    
        def isatty(self):
            """isatty() -> int
            Simulate stdin, stdout, and stderr.
            
            """
            return 1
    
        def readline(self):
            """readline() -> str
            
            Simulate stdin, stdout, and stderr.
            
            """
            return ""
        
        def write(self, text):
            """write(text: str) -> None
            Simulate stdin, stdout, and stderr.
            
            """
            self.input_buffer = ''
            if not self.running_workflow:
                self.running_workflow = True
                # make text blue
                self._append_plain_text("\n\x1b[34m<STANDARD OUTPUT>\x1b[0m\n", True)
            self._append_plain_text(text, True)
            self._prompt_pos = self._get_end_cursor().position()
            self._control.ensureCursorVisible()
            self._control.moveCursor(QtGui.QTextCursor.End)


        def eventFilter(self, obj, event):
            """ Reimplemented to ensure a console-like behavior in the underlying
                text widgets.
            """
            etype = event.type()
            if etype == QtCore.QEvent.KeyPress:
                self.running_workflow = False
            return RichIPythonWidget.eventFilter(self, obj, event)

    return IPythonDialog

#install_attempted = False
#installed = vistrails.core.requirements.python_module_exists('IPython.frontend.qt')
#if not installed and not install_attempted:
#    print "attempt to install"
#    install_attempted = True
#    from vistrails.core.bundles import installbundle
#    installed = installbundle.install({'linux-ubuntu': 'ipython-qtconsole'})
#if installed:
#    print "installed!"
#    QShellDialog = getIPythonDialog()

# This is tested with IPython 1.0.0 and its beta versions
# TODO: Once IPython 1.0 is included in the distro we should add auto-install
try:
    from IPython.qt.inprocess import QtInProcessKernelManager
    try:
        QShellDialog = getIPythonDialog()
    except Exception, e:
        import traceback; traceback.print_exc()
except Exception:
    pass

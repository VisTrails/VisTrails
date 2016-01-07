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
""" This module defines the following classes:
    - QShellDialog
    - QShell

QShell is based on ideas and code from PyCute developed by Gerard Vermeulen.
Used with the author's permission.
More information on PyCute, visit:
http://gerard.vermeulen.free.fr/html/pycute-intro.html

"""
from __future__ import division

from PyQt4 import QtGui, QtCore
import sys

from vistrails.core.bundles import py_import
from vistrails.core.interpreter.default import get_default_interpreter
from vistrails.gui.vistrails_palette import QVistrailsPaletteInterface

################################################################################

_shell_dialog = None

def get_shell_dialog():
    global _shell_dialog

    if _shell_dialog is not None:
        return _shell_dialog

    try:
        deps = {'pip': 'ipython>=1.0',
                'linux-ubuntu': 'ipython-qtconsole',
                'linux-debian': 'ipython-qtconsole'}

        IPython = py_import('IPython.qt.console.rich_ipython_widget', deps,
                            True)
        RichIPythonWidget = \
                IPython.qt.console.rich_ipython_widget.RichIPythonWidget
        py_import('IPython.qt.inprocess', deps, True)
        QtInProcessKernelManager = \
                IPython.qt.inprocess.QtInProcessKernelManager
    except ImportError:
        return None

    km = QtInProcessKernelManager()
    km.start_kernel()
    kernel = km.kernel
    kernel.gui = 'qt4'

    kernel_client = km.client()
    kernel_client.start_channels()

    class IPythonDialog(RichIPythonWidget, QVistrailsPaletteInterface):
        """This class incorporates an  IPython shell into a dockable widget for use in the
        VisTrails environment"""
        def __init__(self, parent=None):
            RichIPythonWidget.__init__(self, parent)
            self.old_streams = None
            self.running_workflow = False
            self.kernel_manager = km
            self.kernel_client = kernel_client
            self.exit_requested.connect(self.stop)
            self.setWindowTitle("Console")
            self.vistrails_interpreter = get_default_interpreter()

        def visibility_changed(self, visible):
            QVistrailsPaletteInterface.visibility_changed(self, visible)
            if visible:
                self.show()
            else:
                self.hide()
        def stop(self):
            kernel_client.stop_channels()
            km.shutdown_kernel()

        def hide(self):
            """suspend() -> None
            Called when hiding the parent window in order to recover the previous
            state.

            """
            #recovering the state
            if self.old_streams is not None:
                sys.stdout, sys.stderr, sys.stdin = self.old_streams
                self.old_streams = None
            RichIPythonWidget.hide(self)

        def show(self):
            """show() -> None
            Store previous state and starts capturing all interactive input and
            output.

            """
            # capture all interactive input/output
            if self.old_streams is None:
                self.old_streams = sys.stdout, sys.stderr, sys.stdin
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

    _shell_dialog = IPythonDialog
    return IPythonDialog

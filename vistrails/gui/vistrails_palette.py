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
from gui.common_widgets import QToolWindowInterface

class QVistrailsPaletteInterface(QToolWindowInterface):
    def __init__(self):
        QToolWindowInterface.__init__(self)
        self.controller = None
        self.title = None
        self.p_id = None
        self.main_window = None
 
    @classmethod
    def instance(klass):
        if not hasattr(klass, '_instance'):
            klass._instance = klass()
        return klass._instance

    def toolWindow(self):
        tool_window = QToolWindowInterface.toolWindow(self)
        return tool_window

    def set_id(self, p_id):
        self.p_id = p_id

    def get_id(self):
        return self.p_id

    def set_title(self, title):
        self.setWindowTitle(title)

    def get_title(self):
        return self.windowTitle()

    def set_action(self, action):
        self.action = action
        self.connect(self.toolWindow(), 
                     QtCore.SIGNAL("visibilityChanged(bool)"),
                     self.visibility_changed)

    def get_action(self):
        return self.action
        # return self.toolWindow().toggleViewAction()

    def get_action_tuple(self):
        return (self.get_title(), self.get_title(), 
                {'checkable': True, 
                 'checked': True,
                 'callback': self.set_visible})

    def set_main_window(self, mw):
        self.main_window = mw

    def set_visible(self, enabled):
        if enabled and hasattr(self, 'main_window') and \
                self.main_window is not None:
            self.main_window.show()
            self.main_window.raise_()

        if enabled:
            self.toolWindow().raise_()

    def set_controller(self, controller):
        self.controller = controller

    def get_controller(self):
        return self.controller

    def set_module(self, module):
        self.module = module
        
    def get_module(self):
        return self.module

    def set_descriptor(self, descriptor):
        self.descriptor = descriptor

    def get_descriptor(self):
        return self.descriptor

    def visibility_changed(self, visible):
        self.action.setChecked(visible)

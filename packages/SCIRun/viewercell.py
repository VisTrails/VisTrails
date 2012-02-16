############################################################################
##
## Copyright (C) 2006-2007 University of Utah. All rights reserved.
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
## of VisTrails), please contact us at contact@vistrails.org.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################
from PyQt4 import QtCore, QtGui, QtOpenGL
import sip
from core import system
from core.modules.module_registry import registry
from packages.spreadsheet.basic_widgets import SpreadsheetCell, CellLocation
from packages.spreadsheet.spreadsheet_cell import QCellWidget, QCellToolBar
import gc
from gui.qt import qt_super
from core.vistrail.action import Action
from core.vistrail.port import Port
from core.vistrail import module
from core.vistrail import connection
from core.vistrail.module_function import ModuleFunction
from core.vistrail.module_param import ModuleParam
from core.modules.vistrails_module import Module, ModuleError
import db.services.action
import copy
import sr_py
import time
import uuid
from renderbase import Render, registerRender


################################################################################
class ViewerCell(Render):
    """
    ViewerCell is a VisTrails Module that can display SCIRun Viewer.
    
    """
    def compute(self):
        """ compute() -> None
        Dispatch the SCIRun scene graph to the Viewer
        """
        sg = self.forceGetInputListFromPort('Scene Graph')
        self.display(QViewerWidget, (sg))
        


class QViewerWidget(QtOpenGL.QGLWidget) :
    """
    QViewerWidget is the actual rendering widget that can display
    a SCIRun scene graph inside a Qt QWidget
    
    """
    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
        """ QViewerWidget(parent: QWidget, f: WindowFlags) -> QViewerWidget
        Initialize QViewerWidget.
        context
        
        """
        QtOpenGL.QGLWidget.__init__(self, parent)

        self.setAttribute(QtCore.Qt.WA_OpaquePaintEvent)
        self.setAttribute(QtCore.Qt.WA_PaintOnScreen)
        self.setMouseTracking(True)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,
                                             QtGui.QSizePolicy.Expanding))


        
        self.sci_context = sr_py.CallbackOpenGLContext()
        self.sci_context.set_pymake_current_func(self.make_current)
        self.sci_context.set_pyswap_func(self.swap)
        self.sci_context.set_pywidth_func(self.get_width)
        self.sci_context.set_pyheight_func(self.get_height)
        self.sci_context.set_pyrelease_func(self.release)
        unique_id = uuid.uuid4()
        self._id = "sr_viewer_%s" % str(unique_id)
        #print self._id
        self.full_speed = False
        self.timer = QtCore.QTimer()
        self.connect(self.timer,
                     QtCore.SIGNAL("timeout()"), self.updateGL)
        
    def make_current(self) :
        if self.isValid() :
            self.makeCurrent()
            return 1
        return 0

    def swap(self) :
        if self.isValid() :
            self.swapBuffers() 
            return 1
        return 0

    def get_width(self) :
        if self.isValid() :
            w = self.width()
            return w
        return 0

    def get_height(self) :
        if self.isValid() :
            h = self.height()
            return h
        return 0
    
    def release(self) :
        #self.doneCurrent()
        pass

    def pointer_event(self, e, event) :
        e.set_x(event.x())
        e.set_y(event.y())

        mask = e.get_modifiers()
        mask = self.get_sr_py_modifier_mask(event, mask) 
        e.set_modifiers(mask)
        
        state = e.get_pointer_state()
        state, n = self.get_sr_py_pointer_modifier_mask(event, state)
        e.set_pointer_state(state)
        sr_py.add_pointer_event(e, self._id)
        
    def get_sr_py_modifier_mask(self, event, mask) :
        if event.modifiers() & QtCore.Qt.ShiftModifier :
            mask  |= sr_py.EventModifiers.SHIFT_E
        if event.modifiers() & QtCore.Qt.ControlModifier :
            mask  |= sr_py.EventModifiers.CONTROL_E
        if event.modifiers() & QtCore.Qt.AltModifier :
            mask  |= sr_py.EventModifiers.ALT_E
        if event.modifiers() & QtCore.Qt.MetaModifier :
            mask  |= sr_py.EventModifiers.M1_E
        return mask

    def get_sr_py_pointer_modifier_mask(self, event, mask) :
        n = 0

        if event.buttons() & QtCore.Qt.LeftButton :
            mask  |= sr_py.PointerEvent.BUTTON_1_E
            n = 1
        if event.buttons() & QtCore.Qt.MidButton :
            mask  |= sr_py.PointerEvent.BUTTON_2_E
            n = 2
        if event.buttons() & QtCore.Qt.RightButton :
            mask  |= sr_py.PointerEvent.BUTTON_3_E
            n = 3
        return mask, n

    def initializeGL(self):
        # create the viewer
        self.vid = sr_py.create_viewer(self.sci_context, self._id)
        #start the timer
        #self.timer.start(33)
        
##     def paintGL(self):
##         #self.doneCurrent()
##         pass

    def glDraw(self):
        sr_py.update_viewer(self.vid);
        
        if self.timer.isActive() and not self.full_speed :
            self.full_speed = True
            self.timer.start(55)

        if not self.timer.isActive() :
            self.timer.start(1000)
            

    
    def mousePressEvent(self, event):
        """ mousePressEvent(e: QMouseEvent) -> None
        Echo mouse event to SCIRun event system.
        
        """
        e = sr_py.PointerEvent()
        e.set_pointer_state(sr_py.PointerEvent.BUTTON_PRESS_E)
        self.pointer_event(e, event)

    def mouseReleaseEvent(self, event):
        """ mouseReleaseEvent(e: QEvent) -> None
        Echo mouse event to SCIRun event system.
        
        """
        e = sr_py.PointerEvent()
        #e.set_time(long(event.time))
        e.set_pointer_state(sr_py.PointerEvent.BUTTON_RELEASE_E)
        self.pointer_event(e, event)

    def mouseMoveEvent(self, event):
        """ mouseMoveEvent(e: QMouseEvent) -> None
        Echo mouse event to SCIRun event system.
        
        """
        e = sr_py.PointerEvent()
        #e.set_time(long(event.time))
        e.set_pointer_state(sr_py.PointerEvent.MOTION_E)
        self.pointer_event(e, event)
                  
    def enterEvent(self,e):
        """ enterEvent(e: QEvent) -> None
        
        """

    def leaveEvent(self,e):
        """ leaveEvent(e: QEvent) -> None
        
        """
        
        
    def keyPressEvent(self, event):
        """ keyPressEvent(e: QKeyEvent) -> None
        Echo the key event to the SCIRun event system.
        
        """

        ascii_key = None
        if event.text().length()>0:
            ascii_key = event.text().toLatin1()[0]
        else:
            ascii_key = chr(0)

        #for now use native...
        keysym = event.nativeVirtualKey()
        e = sr_py.KeyEvent()
        #e.set_time(long(event.time))
        # translate qt modifiers to sci modifiers
        mask = e.get_modifiers()
        e.set_modifiers(self.get_sr_py_modifier_mask(event, mask))
        e.set_keyval(keysym)
        e.set_key_string(ascii_key)
        e.set_key_state(sr_py.KeyEvent.KEY_PRESS_E)
        sr_py.add_key_event(e, self._id)
        
        
    def keyReleaseEvent(self,e):
        """ keyReleaseEvent(e: QKeyEvent) -> None
        
        """
        #print "keyReleaseEvent"

    def wheelEvent(self,e):
        """ wheelEvent(e: QWheelEvent) -> None
        Zoom in/out while scrolling the mouse
        
        """
        print "wheelEvent"
        
    def updateContents(self, inputPorts):
        """ updateContents(inputPorts: tuple)
        Connects the input scene graph to this viewer
        
        """
        for p in inputPorts :
          try:
            for i in p:
              if i != 0 :
                print i
                sr_py.send_scene(i, self._id);
          except:
            if p != 0 :
              sr_py.send_scene(p, self._id);
def registerSelf():
    """ registerSelf() -> None
    Registry module with the registry
    """
    identifier = "edu.utah.sci.vistrails.scirun"
    registerRender()
    registry.add_module(ViewerCell)
    registry.add_input_port(ViewerCell, "Location", CellLocation)
    registry.add_input_port(ViewerCell, "Scene Graph",
                            registry.get_module_by_name(identifier,
                                                        'Geometry'),
                            'Scene Graph')


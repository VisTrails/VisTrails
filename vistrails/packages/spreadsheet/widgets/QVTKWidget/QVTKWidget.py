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
## of VisTrails), please contact us at vistrails@sci.utah.edu.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################
################################################################################
# File QVTKWidget.py
# File for displaying a vtkRenderWindow in a Qt's QWidget ported from
# VTK/GUISupport/QVTK. Combine altogether to a single class: QVTKWidget
################################################################################
import vtk
from PyQt4 import QtCore, QtGui
from core import system
from packages.spreadsheet.basic_widgets import SpreadsheetCell
from packages.spreadsheet.spreadsheet_helpers import CellToolBar
import QVTKWidget_rc
import datetime
import os

################################################################################

class VTKCell(SpreadsheetCell):
    """
    VTKCell is a VisTrails Module that can display vtkRenderWindow inside a cell
    
    """
    def compute(self):
        """ compute() -> None
        Dispatch the vtkRenderer to the actual rendering widget
        """
        renderers = self.forceGetInputListFromPort('AddRenderer')
        self.display(QVTKWidget, (renderers,))

AsciiToKeySymTable = ( None, None, None, None, None, None, None,
                       None, None,
                       "Tab", None, None, None, None, None, None,
                       None, None, None, None, None, None,
                       None, None, None, None, None, None,
                       None, None, None, None,
                       "space", "exclam", "quotedbl", "numbersign",
                       "dollar", "percent", "ampersand", "quoteright",
                       "parenleft", "parenright", "asterisk", "plus",
                       "comma", "minus", "period", "slash",
                       "0", "1", "2", "3", "4", "5", "6", "7",
                       "8", "9", "colon", "semicolon", "less", "equal",
                       "greater", "question",
                       "at", "A", "B", "C", "D", "E", "F", "G",
                       "H", "I", "J", "K", "L", "M", "N", "O",
                       "P", "Q", "R", "S", "T", "U", "V", "W",
                       "X", "Y", "Z", "bracketleft",
                       "backslash", "bracketright", "asciicircum",
                       "underscore",
                       "quoteleft", "a", "b", "c", "d", "e", "f", "g",
                       "h", "i", "j", "k", "l", "m", "n", "o",
                       "p", "q", "r", "s", "t", "u", "v", "w",
                       "x", "y", "z", "braceleft", "bar", "braceright",
                       "asciitilde", "Delete",
                       None, None, None, None, None, None, None, None, 
                       None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None, 
                       None, None, None, None, None, None, None, None, 
                       None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None, None)


class QVTKWidget(QtGui.QWidget):
    """
    QVTKWidget is the actual rendering widget that can display
    vtkRenderer inside a Qt QWidget
    
    """
    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
        """ QVTKWidget(parent: QWidget, f: WindowFlags) -> QVTKWidget
        Initialize QVTKWidget with a toolbar with its own device
        context
        
        """
        QtGui.QWidget.__init__(self, parent, f | QtCore.Qt.MSWindowsOwnDC)

        self.interacting = None
        self.mRenWin = None
        self.setAttribute(QtCore.Qt.WA_OpaquePaintEvent)
        self.setAttribute(QtCore.Qt.WA_PaintOnScreen)
        self.setMouseTracking(True)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,
                                             QtGui.QSizePolicy.Expanding))
        self.toolBarType = QVTKWidgetToolBar
        self.historyImages = []
        self.player = QtGui.QLabel(self.parent())
        self.player.setFocusPolicy(QtCore.Qt.NoFocus)
        self.player.setScaledContents(True)
        self.playerTimer = QtCore.QTimer()
        self.playerTimer.setSingleShot(True)
        self.connect(self.playerTimer,
                     QtCore.SIGNAL('timeout()'),
                     self.playNextFrame)
        self.currentFrame = 0
        self.playing = False
        
    def deleteLater(self):
        """ deleteLater() -> None        
        Make sure to free render window resource when
        deallocating. Overriding PyQt deleteLater to free up
        resources
        
        """        
        for ren in self.getRendererList():
            self.mRenWin.RemoveRenderer(ren)
            del ren

        iren = self.mRenWin.GetInteractor()
        if iren:
            style = iren.GetInteractorStyle()
            style.RemoveObservers("InteractionEvent")
            style.RemoveObservers("CharEvent")
            style.RemoveObservers("MouseWheelForwardEvent")
            style.RemoveObservers("MouseWheelBackwardEvent")
            
        del self.mRenWin
        self.mRenWin = None
        
        self.clearHistory()
        QtGui.QWidget.deleteLater(self)

    def updateContents(self, inputPorts):
        """ updateContents(inputPorts: tuple)
        Updates the cell contents with new vtkRenderer
        
        """
        renWin = self.GetRenderWindow()

        # Remove old renderers first
        oldRenderers = self.getRendererList()
        for renderer in oldRenderers:
            renWin.RemoveRenderer(renderer)
        
        (renderers,) = inputPorts
        for renderer in renderers:
            renWin.AddRenderer(renderer.vtkInstance)
            if hasattr(renderer.vtkInstance, 'IsActiveCameraCreated'):
                if not renderer.vtkInstance.IsActiveCameraCreated():
                    renderer.vtkInstance.ResetCamera()
        renWin.Render()

        # Capture window into history for playback
        self.captureWindow(True)

    def GetRenderWindow(self):
        """ GetRenderWindow() -> vtkRenderWindow
        Return the associated vtkRenderWindow
        
        """
        if not self.mRenWin:
            win = vtk.vtkRenderWindow()
            win.DoubleBufferOn()
            self.SetRenderWindow(win)
            del win

        return self.mRenWin

    def SetRenderWindow(self,w):
        """ SetRenderWindow(w: vtkRenderWindow)        
        Set a new render window to QVTKWidget and initialize the
        interactor as well
        
        """
        if w == self.mRenWin:
            return
        
        if self.mRenWin:
            if self.mRenWin.GetMapped():
                self.mRenWin.Finalize()
            self.mRenWin.SetDisplayId(None)
            self.mRenWin.SetParentId(None)
            self.mRenWin.SetWindowId(None)
            self.mRenWin.UnRegister(None)
            
        self.mRenWin = w
        
        if self.mRenWin:
            self.mRenWin.Register(None)
            if self.mRenWin.GetMapped():
                self.mRenWin.Finalize()
            if system.systemType=='Linux':
                vp = '_%s_void_p' % (hex(int(QtGui.QX11Info.display()))[2:])
                self.mRenWin.SetDisplayId(vp)
                self.mRenWin.SetSize(1,1)
            self.mRenWin.SetWindowInfo(str(int(self.winId())))
            if self.isVisible():
                self.mRenWin.Start()

            if not self.mRenWin.GetInteractor():
                iren = vtk.vtkRenderWindowInteractor()
                iren.SetRenderWindow(self.mRenWin)
                iren.Initialize()
                if system.systemType=='Linux':
                    system.XDestroyWindow(self.mRenWin.GetGenericDisplayId(),
                                          self.mRenWin.GetGenericWindowId())
                self.mRenWin.SetWindowInfo(str(int(self.winId())))
                self.mRenWin.SetSize(self.width(), self.height())
                self.mRenWin.SetPosition(self.x(), self.y())
                s = vtk.vtkInteractorStyleTrackballCamera()
                iren.SetInteractorStyle(s)
                s.AddObserver("InteractionEvent", self.interactionEvent)
                s.AddObserver("CharEvent", self.charEvent)
                s.AddObserver("MouseWheelForwardEvent", self.interactionEvent)
                s.AddObserver("MouseWheelBackwardEvent", self.interactionEvent)
                del s
                del iren

    def GetInteractor(self):
        """ GetInteractor() -> vtkInteractor
        Return the vtkInteractor control this QVTKWidget
        """
        return self.GetRenderWindow().GetInteractor()

    def event(self, e):
        """ event(e: QEvent) -> depends on event type
        Process window and interaction events
        
        """
        if e.type()==QtCore.QEvent.ParentAboutToChange:            
            if self.mRenWin:
                if self.mRenWin.GetMapped():
                    self.mRenWin.Finalize()
        else:
            if e.type==QtCore.QEvent.ParentChange:
                print 'PARENT CHANGE IS NOT IMPLEMENTED'
                if self.mRenWin:
                    self.mRenWin.SetWindowId(windId())
                    if self.isVisible():
                        self.mRenWin.Start()
        
        if QtCore.QObject.event(self,e):
            return 1

        if e.type() == QtCore.QEvent.KeyPress:
            self.keyPressEvent(e)
            if e.isAccepted():
                return e.isAccepted()

        return QtGui.QWidget.event(self,e)

    def resizeEvent(self, e):
        """ resizeEvent(e: QEvent) -> None
        Re-adjust the vtkRenderWindow size then QVTKWidget resized
        
        """
        QtGui.QWidget.resizeEvent(self,e)

        if self.player.isVisible():
            self.player.setGeometry(self.geometry())
            
        if not self.mRenWin:
            return

        ########################################################
        # VTK - BUGGGGGGGGG - GRRRRRRRRR
        # This is a 'bug' in vtkWin32OpenGLRenderWindow(.cxx)
        # If a render window is mapped to screen, the actual
        # window size is the client area of the window in Win32.
        # However, this real window size is only updated through
        # vtkWin32OpenGLRenderWindow::GetSize(). So this has to
        # be called here to get the cell size correctly. This
        # invalidates the condition in the next SetSize().
        # We can use self.mRenWin.SetSize(0,0) here but it will
        # cause flickering and decrease performance!
        # SetPosition(curX,curY) also works here but slower.
        self.mRenWin.GetSize()
        
        self.mRenWin.SetSize(self.width(),self.height())
        if self.mRenWin.GetInteractor():
            self.mRenWin.GetInteractor().SetSize(self.width(),self.height())            

    def moveEvent(self,e):
        """ moveEvent(e: QEvent) -> None
        Echo the move event into vtkRenderWindow
        
        """
        QtGui.QWidget.moveEvent(self,e)
        if not self.mRenWin:
            return

        self.mRenWin.SetPosition(self.x(),self.y())

    def paintEvent(self,e):
        """ paintEvent(e: QPaintEvent) -> None
        Paint the QVTKWidget with vtkRenderWindow
        
        """
        iren = None
        if self.mRenWin:
            iren = self.mRenWin.GetInteractor()

        if (not iren) or (not iren.GetEnabled()):
            return
        iren.Render()        

    def SelectActiveRenderer(self,iren):
        """ SelectActiveRenderer(iren: vtkRenderWindowIteractor) -> None
        Only make the vtkRenderer below the mouse cursor active
        
        """
        epos = iren.GetEventPosition()
        rens = iren.GetRenderWindow().GetRenderers()
        rens.InitTraversal()
        for i in range(rens.GetNumberOfItems()):
            ren = rens.GetNextItem()
            ren.SetInteractive(ren.IsInViewport(epos[0], epos[1]))

    def mousePressEvent(self,e):
        """ mousePressEvent(e: QMouseEvent) -> None
        Echo mouse event to vtkRenderWindowwInteractor
        
        """
        self.emit(QtCore.SIGNAL("mouseEvent(QMouseEvent)"),e)

        iren = None
        if self.mRenWin:
            iren = self.mRenWin.GetInteractor()

        if (not iren) or (not iren.GetEnabled()):
            return

        ctrl = (e.modifiers()&QtCore.Qt.ControlModifier)
        isDoubleClick = e.type()==QtCore.QEvent.MouseButtonDblClick
        iren.SetEventInformationFlipY(e.x(),e.y(),
                                      ctrl,
                                      (e.modifiers()&QtCore.Qt.ShiftModifier),
                                      chr(0),
                                      isDoubleClick,
                                      None)

        invoke = {QtCore.Qt.LeftButton:"LeftButtonPressEvent",
                  QtCore.Qt.MidButton:"MiddleButtonPressEvent",
                  QtCore.Qt.RightButton:"RightButtonPressEvent"}

        self.SelectActiveRenderer(iren)

        if ctrl:
            e.ignore()
            return
        
        self.interacting = self.getActiveRenderer(iren)
        
        if e.button() in invoke:
            iren.InvokeEvent(invoke[e.button()])

    def mouseMoveEvent(self,e):
        """ mouseMoveEvent(e: QMouseEvent) -> None
        Echo mouse event to vtkRenderWindowwInteractor
        
        """
        iren = None
        if self.mRenWin:
            iren = self.mRenWin.GetInteractor()

        if (not iren) or (not iren.GetEnabled()):
            return

        iren.SetEventInformationFlipY(e.x(),e.y(),
                                      (e.modifiers()&QtCore.Qt.ControlModifier),
                                      (e.modifiers()&QtCore.Qt.ShiftModifier),
                                      chr(0), 0, None)

        iren.InvokeEvent("MouseMoveEvent")
                  
    def enterEvent(self,e):
        """ enterEvent(e: QEvent) -> None
        Echo mouse event to vtkRenderWindowwInteractor
        
        """
        iren = None
        if self.mRenWin:
            iren = self.mRenWin.GetInteractor()

        if (not iren) or (not iren.GetEnabled()):
            return

        iren.InvokeEvent("EnterEvent")

    def leaveEvent(self,e):
        """ leaveEvent(e: QEvent) -> None
        Echo mouse event to vtkRenderWindowwInteractor
        
        """
        iren = None
        if self.mRenWin:
            iren = self.mRenWin.GetInteractor()

        if (not iren) or (not iren.GetEnabled()):
            return

        iren.InvokeEvent("LeaveEvent")

    def mouseReleaseEvent(self,e):
        """ mouseReleaseEvent(e: QEvent) -> None
        Echo mouse event to vtkRenderWindowwInteractor
        
        """
        iren = None
        if self.mRenWin:
            iren = self.mRenWin.GetInteractor()

        if (not iren) or (not iren.GetEnabled()):
            return

        iren.SetEventInformationFlipY(e.x(),e.y(),
                                      (e.modifiers()&QtCore.Qt.ControlModifier),
                                      (e.modifiers()&QtCore.Qt.ShiftModifier),
                                      chr(0),0,None)

        invoke = {QtCore.Qt.LeftButton:"LeftButtonReleaseEvent",
                  QtCore.Qt.MidButton:"MiddleButtonReleaseEvent",
                  QtCore.Qt.RightButton:"RightButtonReleaseEvent"}

        self.interacting = None
        
        if e.button() in invoke:
            iren.InvokeEvent(invoke[e.button()])

    def keyPressEvent(self,e):
        """ keyPressEvent(e: QKeyEvent) -> None
        Disallow 'quit' key in vtkRenderWindowwInteractor and sync the others
        
        """
        iren = None
        if self.mRenWin:
            iren = self.mRenWin.GetInteractor()

        if (not iren) or (not iren.GetEnabled()):
            return

        ascii_key = None
        if e.text().length()>0:
            ascii_key = e.text().toLatin1()[0]
        else:
            ascii_key = chr(0)

        keysym = self.ascii_to_key_sym(ord(ascii_key))

        if not keysym:
            keysym = self.qt_key_to_key_sym(e.key())

        # Ignore 'q' or 'e' or Ctrl-anykey
        ctrl = (e.modifiers()&QtCore.Qt.ControlModifier)
        shift = (e.modifiers()&QtCore.Qt.ShiftModifier)
        if not(keysym in ['w','s','r','f'] and not ctrl):
            e.ignore()
            return
        
        iren.SetKeyEventInformation(ctrl,shift,ascii_key, e.count(), keysym)

        iren.InvokeEvent("KeyPressEvent")

        if ascii_key:
            iren.InvokeEvent("CharEvent")

        
    def keyReleaseEvent(self,e):
        """ keyReleaseEvent(e: QKeyEvent) -> None
        Disallow 'quit' key in vtkRenderWindowwInteractor and sync the others
        
        """
        iren = None
        if self.mRenWin:
            iren = self.mRenWin.GetInteractor()

        if (not iren) or (not iren.GetEnabled()):
            return

        ascii_key = None
        if e.text().length()>0:
            ascii_key = e.text().toLatin1()[0]
        else:
            ascii_key = chr(0)

        keysym = self.ascii_to_key_sym(ord(ascii_key))

        if not keysym:
            keysym = self.qt_key_to_key_sym(e.key())

        # Ignore 'q' or 'e' or Ctrl-anykey
        ctrl = (e.modifiers()&QtCore.Qt.ControlModifier)
        shift = (e.modifiers()&QtCore.Qt.ShiftModifier)
        if not(keysym in ['w','s','r','f'] and not ctrl):
            e.ignore()
            return
        
        iren.SetKeyEventInformation(ctrl, shift, ascii_key, e.count(), keysym)

        iren.InvokeEvent("KeyReleaseEvent")

    def wheelEvent(self,e):
        """ wheelEvent(e: QWheelEvent) -> None
        Zoom in/out while scrolling the mouse
        
        """
        iren = None
        if self.mRenWin:
            iren = self.mRenWin.GetInteractor()

        if (not iren) or (not iren.GetEnabled()):
            return

        iren.SetEventInformationFlipY(e.x(),e.y(),
                                      (e.modifiers()&QtCore.Qt.ControlModifier),
                                      (e.modifiers()&QtCore.Qt.ShiftModifier),
                                      chr(0),0,None)
        
        self.SelectActiveRenderer(iren)
        
        if e.delta()>0:
            iren.InvokeEvent("MouseWheelForwardEvent")
        else:
            iren.InvokeEvent("MouseWheelBackwardEvent")

    def focusInEvent(self,e):
        """ focusInEvent(e: QFocusEvent) -> None
        Ignore focus event
        
        """
        pass

    def focusOutEvent(self,e):
        """ focusOutEvent(e: QFocusEvent) -> None
        Ignore focus event
        
        """
        pass

    def contextMenuEvent(self,e):
        """ contextMenuEvent(e: QContextMenuEvent) -> None        
        Make sure to get the right mouse position for the context menu
        event, i.e. also the right click
        
        """
        iren = None
        if self.mRenWin:
            iren = self.mRenWin.GetInteractor()

        if (not iren) or (not iren.GetEnabled()):
            return

        ctrl = int(e.modifiers()&QtCore.Qt.ControlModifier)
        shift = int(e.modifiers()&QtCore.Qt.ShiftModifier)
        iren.SetEventInformationFlipY(e.x(),e.y(),ctrl,shift,chr(0),0,None)
        iren.InvokeEvent("ContextMenuEvent")

    def ascii_to_key_sym(self,i):
        """ ascii_to_key_sym(i: int) -> str
        Convert ASCII code into key name
        
        """
        global AsciiToKeySymTable
        return AsciiToKeySymTable[i]

    def qt_key_to_key_sym(self,i):
        """ qt_key_to_key_sym(i: QtCore.Qt.Keycode) -> str
        Convert Qt key code into key name
        
        """
        handler = {QtCore.Qt.Key_Backspace:"BackSpace",
                   QtCore.Qt.Key_Tab:"Tab",
                   QtCore.Qt.Key_Backtab:"Tab",
                   QtCore.Qt.Key_Return:"Return",
                   QtCore.Qt.Key_Enter:"Return",
                   QtCore.Qt.Key_Shift:"Shift_L",
                   QtCore.Qt.Key_Control:"Control_L",
                   QtCore.Qt.Key_Alt:"Alt_L",
                   QtCore.Qt.Key_Pause:"Pause",
                   QtCore.Qt.Key_CapsLock:"Caps_Lock",
                   QtCore.Qt.Key_Escape:"Escape",
                   QtCore.Qt.Key_Space:"space",
                   QtCore.Qt.Key_End:"End",
                   QtCore.Qt.Key_Home:"Home",
                   QtCore.Qt.Key_Left:"Left",
                   QtCore.Qt.Key_Up:"Up",
                   QtCore.Qt.Key_Right:"Right",
                   QtCore.Qt.Key_Down:"Down",
                   QtCore.Qt.Key_SysReq:"Snapshot",
                   QtCore.Qt.Key_Insert:"Insert",
                   QtCore.Qt.Key_Delete:"Delete",
                   QtCore.Qt.Key_Help:"Help",
                   QtCore.Qt.Key_0:"0",
                   QtCore.Qt.Key_1:"1",
                   QtCore.Qt.Key_2:"2",
                   QtCore.Qt.Key_3:"3",
                   QtCore.Qt.Key_4:"4",
                   QtCore.Qt.Key_5:"5",
                   QtCore.Qt.Key_6:"6",
                   QtCore.Qt.Key_7:"7",
                   QtCore.Qt.Key_8:"8",
                   QtCore.Qt.Key_9:"9",
                   QtCore.Qt.Key_A:"a",
                   QtCore.Qt.Key_B:"b",
                   QtCore.Qt.Key_C:"c",
                   QtCore.Qt.Key_D:"d",
                   QtCore.Qt.Key_E:"e",
                   QtCore.Qt.Key_F:"f",
                   QtCore.Qt.Key_G:"g",
                   QtCore.Qt.Key_H:"h",
                   QtCore.Qt.Key_I:"i",
                   QtCore.Qt.Key_J:"h",
                   QtCore.Qt.Key_K:"k",
                   QtCore.Qt.Key_L:"l",
                   QtCore.Qt.Key_M:"m",
                   QtCore.Qt.Key_N:"n",
                   QtCore.Qt.Key_O:"o",
                   QtCore.Qt.Key_P:"p",
                   QtCore.Qt.Key_Q:"q",
                   QtCore.Qt.Key_R:"r",
                   QtCore.Qt.Key_S:"s",
                   QtCore.Qt.Key_T:"t",
                   QtCore.Qt.Key_U:"u",
                   QtCore.Qt.Key_V:"v",
                   QtCore.Qt.Key_W:"w",
                   QtCore.Qt.Key_X:"x",
                   QtCore.Qt.Key_Y:"y",
                   QtCore.Qt.Key_Z:"z",
                   QtCore.Qt.Key_Asterisk:"asterisk",
                   QtCore.Qt.Key_Plus:"plus",
                   QtCore.Qt.Key_Minus:"minus",
                   QtCore.Qt.Key_Period:"period",
                   QtCore.Qt.Key_Slash:"slash",
                   QtCore.Qt.Key_F1:"F1",
                   QtCore.Qt.Key_F2:"F2",
                   QtCore.Qt.Key_F3:"F3",
                   QtCore.Qt.Key_F4:"F4",
                   QtCore.Qt.Key_F5:"F5",
                   QtCore.Qt.Key_F6:"F6",
                   QtCore.Qt.Key_F7:"F7",
                   QtCore.Qt.Key_F8:"F8",
                   QtCore.Qt.Key_F9:"F9",
                   QtCore.Qt.Key_F10:"F10",
                   QtCore.Qt.Key_F11:"F11",
                   QtCore.Qt.Key_F12:"F12",
                   QtCore.Qt.Key_F13:"F13",
                   QtCore.Qt.Key_F14:"F14",
                   QtCore.Qt.Key_F15:"F15",
                   QtCore.Qt.Key_F16:"F16",
                   QtCore.Qt.Key_F17:"F17",
                   QtCore.Qt.Key_F18:"F18",
                   QtCore.Qt.Key_F19:"F19",
                   QtCore.Qt.Key_F20:"F20",
                   QtCore.Qt.Key_F21:"F21",
                   QtCore.Qt.Key_F22:"F22",
                   QtCore.Qt.Key_F23:"F23",
                   QtCore.Qt.Key_F24:"F24",
                   QtCore.Qt.Key_NumLock:"Num_Lock",
                   QtCore.Qt.Key_ScrollLock:"Scroll_Lock"}
        if i in handler:            
            return handler[i]
        else:
            return "None"

    def getRendererList(self):
        """ getRendererList() -> list
        Return a list of vtkRenderer running in this QVTKWidget
        """
        result = []
        renWin = self.GetRenderWindow()
        renderers = renWin.GetRenderers()
        renderers.InitTraversal()
        for i in range(renderers.GetNumberOfItems()):
            result.append(renderers.GetNextItem())
        return result

    def getActiveRenderer(self, iren):
        """ getActiveRenderer(iren: vtkRenderWindowwInteractor) -> vtkRenderer
        Return the active vtkRenderer under mouse
        
        """
        epos = iren.GetEventPosition()
        rens = iren.GetRenderWindow().GetRenderers()
        rens.InitTraversal()
        for i in range(rens.GetNumberOfItems()):
            ren = rens.GetNextItem()
            if ren.IsInViewport(epos[0], epos[1]):
                return ren
        return None

    def findSheetTabWidget(self):
        """ findSheetTabWidget() -> QTabWidget
        Find and return the sheet tab widget
        
        """
        p = self.parent()
        while p:
            if hasattr(p, 'isSheetTabWidget'):
                if p.isSheetTabWidget()==True:
                    return p
            p = p.parent()
        return None

    def interactionEvent(self, istyle, name):
        """ interactionEvent(istyle: vtkInteractorStyle, name: str) -> None
        Make sure interactions sync across selected renderers
        
        """
        if name=='MouseWheelForwardEvent':
            istyle.OnMouseWheelForward()
        if name=='MouseWheelBackwardEvent':
            istyle.OnMouseWheelBackward()        
        sheet = self.findSheetTabWidget()
        if sheet:
            iren = istyle.GetInteractor()
            ren = self.interacting
            if not ren: ren = self.getActiveRenderer(iren)
            if ren:
                cam = ren.GetActiveCamera()
                cpos = cam.GetPosition()
                cfol = cam.GetFocalPoint()
                cup = cam.GetViewUp()
                cells = sheet.getSelectedLocations()
                for (row, col) in cells:
                    cell = sheet.getCell(row, col)
                    if hasattr(cell, 'getRendererList'):
                        rens = cell.getRendererList()
                        for r in rens:
                            if r!=ren:
                                dcam = r.GetActiveCamera()
                                dcam.SetPosition(cpos)
                                dcam.SetFocalPoint(cfol)
                                dcam.SetViewUp(cup)
                                r.ResetCameraClippingRange()
                        cell.GetRenderWindow().Render()

    def charEvent(self, istyle, name):
        """ charEvent(istyle: vtkInteractorStyle, name: str) -> None
        Make sure key presses also sync across selected renderers
        
        """
        sheet = self.findSheetTabWidget()
        if sheet:
            iren = istyle.GetInteractor()
            keyCode = iren.GetKeyCode()
            if keyCode in ['w','W','s','S','r','R']:
                cells = sheet.getSelectedLocations()
                for (row, col) in cells:
                    cell = sheet.getCell(row, col)
                    if hasattr(cell, 'GetInteractor'):
                        selectedIren = cell.GetInteractor()
                        selectedIren.SetKeyCode(keyCode)
                        selectedIren.GetInteractorStyle().OnChar()
                        selectedIren.Render()
            istyle.OnChar()

    def captureWindow(self, toHistory):
        """ captureWindow(toHistory: bool) -> None        
        Capture the window contents to file (toHistory=False) or to
        history
        
        """
        if not toHistory:
            fn = QtGui.QFileDialog.getSaveFileName(None,
                                                   "Save file as...",
                                                   "screenshot.png",
                                                   "Images (*.png)")
            if fn.isNull():
                return
            fn = str(fn)
        else:
            current = datetime.datetime.now()
            tmpDir = system.temporaryDirectory()
            fn = (tmpDir + "hist_" +
                  current.strftime("%Y_%m_%d__%H_%M_%S") +
                  "_" + str(current.microsecond)+".png")
        w2i = vtk.vtkWindowToImageFilter()
        w2i.SetInput(self.mRenWin)
        w2i.Update()
        writer = vtk.vtkPNGWriter()
        writer.SetInputConnection(w2i.GetOutputPort())
        writer.SetFileName(fn)
        self.mRenWin.Render()
        writer.Write()
        if toHistory:
            self.historyImages.append(fn)

    def clearHistory(self):
        """ clearHistory() -> None
        Clear all history files
        
        """
        for fn in self.historyImages:
            os.remove(fn)
        self.historyImages = []

    def setPlayerFrame(self, frame):
        """ setPlayerFrame(frame: int) -> None
        Set the player to display a particular frame number
        
        """
        if frame>=len(self.historyImages):
            frame = frame % len(self.historyImages)
        if frame>=len(self.historyImages):
            return
        self.player.setPixmap(QtGui.QPixmap(self.historyImages[frame]))

    def startPlayer(self):
        """ startPlayer() -> None
        Adjust the size of the player to the cell and show it
        
        """
        self.player.setParent(self.parent())
        self.player.setGeometry(self.geometry())
        self.player.raise_()
        self.currentFrame = -1
        self.playNextFrame()
        self.player.show()
        self.playing = True
        
    def stopPlayer(self):
        """ startPlayer() -> None
        Adjust the size of the player to the cell and show it
        
        """
        self.playerTimer.stop()
        self.player.hide()
        self.playing = False

    def showNextFrame(self):
        """ showNextFrame() -> None
        Display the next frame in the history
        
        """
        self.currentFrame += 1
        if self.currentFrame>=len(self.historyImages):
            self.currentFrame = 0
        self.setPlayerFrame(self.currentFrame)
        
    def playNextFrame(self):
        """ playNextFrame() -> None        
        Display the next frame in the history and start the timer for
        the frame after
        
        """
        self.showNextFrame()
        self.playerTimer.start(100)

class QVTKWidgetCapture(QtGui.QAction):
    """
    QVTKWidgetCapture is the action to capture the vtk rendering
    window to an image
    
    """
    def __init__(self, parent=None):
        """ QVTKWidgetCapture(parent: QWidget) -> QVTKWidgetCapture
        Setup the image, status tip, etc. of the action
        
        """
        QtGui.QAction.__init__(self,
                               QtGui.QIcon(":/images/camera.png"),
                               "&Capture image to file",
                               parent)
        self.setStatusTip("Capture the rendered image to a file")

    def triggeredSlot(self, checked=False):
        """ toggledSlot(checked: boolean) -> None
        Execute the action when the button is clicked
        
        """
        cellWidget = self.toolBar.getSnappedWidget()
        cellWidget.captureWindow(False)        

class QVTKWidgetCaptureToHistory(QtGui.QAction):
    """
    QVTKWidgetCaptureToHistory is the action to capture the vtk rendering
    window to the history
    
    """
    def __init__(self, parent=None):
        """ QVTKWidgetCaptureToHistory(parent: QWidget)
                                       -> QVTKWidgetCaptureToHistory
        Setup the image, status tip, etc. of the action
        
        """
        QtGui.QAction.__init__(self,
                               QtGui.QIcon(":/images/camera_mount.png"),
                               "&Capture image to history",
                               parent)
        self.setStatusTip("Capture the rendered image to the history for "
                          "playback later")

    def triggeredSlot(self, checked=False):
        """ toggledSlot(checked: boolean) -> None
        Execute the action when the button is clicked
        
        """
        cellWidget = self.toolBar.getSnappedWidget()
        self.toolBar.hide()
        cellWidget.captureWindow(True)
        self.toolBar.updateToolBar()
        self.toolBar.show()
        
class QVTKWidgetPlayHistory(QtGui.QAction):
    """
    QVTKWidgetPlayHistory is the action to play the history as an animation
    
    """
    def __init__(self, parent=None):
        """ QVTKWidgetPlayHistory(parent: QWidget)
                                       -> QVTKWidgetPlayHistory
        Setup the image, status tip, etc. of the action
        
        """
        self.icons = [QtGui.QIcon(":/images/player_play.png"),
                      QtGui.QIcon(":/images/player_pause.png")]
        self.toolTips = ["&Play the history",
                         "Pa&use the history playback"]
        self.statusTips = ["Playback all image files kept in the history",
                           "Pause the playback, later it can be resumed"]
        QtGui.QAction.__init__(self, self.icons[0], self.toolTips[0], parent)
        self.setStatusTip(self.statusTips[0])
        self.status = 0

    def triggeredSlot(self, checked=False):
        """ toggledSlot(checked: boolean) -> None
        Execute the action when the button is clicked
        
        """
        cellWidget = self.toolBar.getSnappedWidget()
        if self.status==0:            
            cellWidget.startPlayer()
        else:
            cellWidget.stopPlayer()
        self.toolBar.updateToolBar()

    def updateStatus(self, info):
        """ updateStatus(info: tuple) -> None
        Updates the status of the button based on the input info
        
        """
        (sheet, row, col, cellWidget) = info
        if cellWidget:            
            newStatus = int(cellWidget.playing)
            if newStatus!=self.status:
                self.status = newStatus
                self.setIcon(self.icons[self.status])
                self.setToolTip(self.toolTips[self.status])
                self.setStatusTip(self.statusTips[self.status])
            self.setEnabled(len(cellWidget.historyImages)>0)                

class QVTKWidgetClearHistory(QtGui.QAction):
    """
    QVTKWidgetClearHistory is the action to reset cell history
    
    """
    def __init__(self, parent=None):
        """ QVTKWidgetClearHistory(parent: QWidget)
                                       -> QVTKWidgetClearHistory
        Setup the image, status tip, etc. of the action
        
        """
        QtGui.QAction.__init__(self,
                               QtGui.QIcon(":/images/noatunloopsong.png"),
                               "&Clear this cell history",
                               parent)
        self.setStatusTip("Clear the cell history and its temporary "
                          "image files on disk")        
        
    def triggeredSlot(self, checked=False):
        """ toggledSlot(checked: boolean) -> None
        Execute the action when the button is clicked
        
        """
        cellWidget = self.toolBar.getSnappedWidget()
        cellWidget.clearHistory()
        self.toolBar.updateToolBar()
        
    def updateStatus(self, info):
        """ updateStatus(info: tuple) -> None
        Updates the status of the button based on the input info
        
        """
        (sheet, row, col, cellWidget) = info
        if cellWidget:
            self.setEnabled((len(cellWidget.historyImages)>0
                             and cellWidget.playing==False))
                
class QVTKWidgetToolBar(CellToolBar):
    """
    QVTKWidgetToolBar derives from CellToolBar to give the VTKCell
    a customizable toolbar
    
    """
    def createToolBar(self):
        """ createToolBar() -> None
        This will get call initiallly to add customizable widgets
        
        """
        self.setOrientation(QtCore.Qt.Vertical)
        self.appendAction(QVTKWidgetCapture(self))
        self.appendAction(QVTKWidgetCaptureToHistory(self))
        self.appendAction(QVTKWidgetPlayHistory(self))
        self.appendAction(QVTKWidgetClearHistory(self))

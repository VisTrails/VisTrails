""" File QVTKWidget.py
File for displaying a vtkRenderWindow in a Qt's QWidget ported from
VTK/GUISupport/QVTK. Combine altogether to a single class: QVTKWidget
"""
import sys
import vtk
from PyQt4 import QtCore, QtGui
from packages.spreadsheet.basic_widgets import SpreadsheetCell
from packages.spreadsheet.spreadsheet_helpers import *
from core import system

import QVTKWidget_rc

class VTKCell(SpreadsheetCell):

    def compute(self):
        renderers = self.forceGetInputListFromPort('AddRenderer')
        self.display(QVTKWidget, (renderers,))

AsciiToKeySymTable = ( None, None, None, None, None, None, None, None, None, "Tab", None, None, None, None, None, None,
  None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
  "space", "exclam", "quotedbl", "numbersign",
  "dollar", "percent", "ampersand", "quoteright",
  "parenleft", "parenright", "asterisk", "plus",
  "comma", "minus", "period", "slash",
  "0", "1", "2", "3", "4", "5", "6", "7",
  "8", "9", "colon", "semicolon", "less", "equal", "greater", "question",
  "at", "A", "B", "C", "D", "E", "F", "G",
  "H", "I", "J", "K", "L", "M", "N", "O",
  "P", "Q", "R", "S", "T", "U", "V", "W",
  "X", "Y", "Z", "bracketleft",
  "backslash", "bracketright", "asciicircum", "underscore",
  "quoteleft", "a", "b", "c", "d", "e", "f", "g",
  "h", "i", "j", "k", "l", "m", "n", "o",
  "p", "q", "r", "s", "t", "u", "v", "w",
  "x", "y", "z", "braceleft", "bar", "braceright", "asciitilde", "Delete",
  None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
  None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
  None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
  None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
  None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
  None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
  None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
  None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None)


class QVTKWidget(QtGui.QWidget):
    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):                
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
        #MAC?
        #  this->DirtyRegionHandler = 0;
        #  this->DirtyRegionHandlerUPP = 0;

    def __del__(self):
        del self.mRenWin

    def updateContents(self, inputPorts):
        (renderers,) = inputPorts
        renWin = self.GetRenderWindow()
        for renderer in renderers:            
            renWin.AddRenderer(renderer.vtkInstance)
            if hasattr(renderer.vtkInstance, 'IsActiveCameraCreated'):
                if not renderer.vtkInstance.IsActiveCameraCreated():
                    renderer.vtkInstance.ResetCamera()            
        renWin.Render()

    def GetRenderWindow(self):
        if not self.mRenWin:
            win = vtk.vtkRenderWindow()
            win.DoubleBufferOn()
            self.SetRenderWindow(win)
            del win

        return self.mRenWin

    def SetRenderWindow(self,w):        
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
            #X11?
            SetDisplayInfo = getattr(self.mRenWin, "SetDisplayInfo", None)
            if SetDisplayInfo:
                SetDisplayInfo(str(int(QtGui.QX11Info.display())))
            self.mRenWin.SetWindowInfo(str(int(self.winId())))
            self.mRenWin.SetParentInfo(str(int(self.parent().winId())))
            #MAC?
            #self.mRenWin.SetWindowId(str(int(self.handle())));
            #self.mRenWin->SetParentId(reinterpret_cast<void*>(0x1));
            self.mRenWin.SetSize(self.width(), self.height())
            self.mRenWin.SetPosition(self.x(), self.y())
            
            if system.systemType != "Linux" and self.isVisible():
                self.mRenWin.Start()

            if not self.mRenWin.GetInteractor():
                iren = vtk.vtkRenderWindowInteractor()
                self.mRenWin.SetInteractor(iren)
                iren.Initialize()
                HideTopShell = getattr(iren, "HideTopShell", None)
                if HideTopShell:
                    HideTopShell(str(int(self.winId())))
                else:
                    self.mRenWin.SetWindowInfo(str(int(self.winId())))                
                s = vtk.vtkInteractorStyleTrackballCamera()
                iren.SetInteractorStyle(s)
                s.AddObserver("InteractionEvent", self.interactionEvent);
                s.AddObserver("CharEvent", self.charEvent);
                s.AddObserver("MouseWheelForwardEvent", self.interactionEvent);
                s.AddObserver("MouseWheelBackwardEvent", self.interactionEvent);
                del iren
                del s

            self.mRenWin.GetInteractor().SetSize(self.width(),self.height())

        #MAC?
        # if(mRenWin && !this->DirtyRegionHandlerUPP)
        # {
        #     this->DirtyRegionHandlerUPP = NewEventHandlerUPP(QVTKWidget::DirtyRegionProcessor);
        #     static EventTypeSpec events[] = { {'cute', 20} };  
        #        // kEventClassQt, kEventQtRequestWindowChange from qt_mac_p.h
        #        // Suggested by Sam Magnuson at Trolltech as best portabile hack 
        #        // around Apple's missing functionality in HI Toolbox.
        #     InstallEventHandler(GetApplicationEventTarget(), this->DirtyRegionHandlerUPP, 
        #                         GetEventTypeCount(events), events, 
        #                         reinterpret_cast<void*>(this), &this->DirtyRegionHandler);
        #     }
        #   else if(!mRenWin && this->DirtyRegionHandlerUPP)
        #     {
        #     RemoveEventHandler(this->DirtyRegionHandler);
        #     DisposeEventHandlerUPP(this->DirtyRegionHandlerUPP);
        #     this->DirtyRegionHandler = 0;
        #     this->DirtyRegionHandlerUPP = 0;
        #     }

    def GetInteractor(self):
        return self.GetRenderWindow().GetInteractor()

    def event(self, e):
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
        QtGui.QWidget.resizeEvent(self,e)

        if not self.mRenWin:
            return

        ########################################################
        # VTK - BUGGGGGGGGG - GRRRRRRRRR
        # This is a 'bug' in vtkWin32OpenGLRenderWindow(.cxx)
        # If a render window is mapped to screen, the actual
        # window size is the client area of the window in Win32.
        # However, this real window size is only updated through
        # vtkWin32OpenGLRenderWindow::GetSize(). So this has to
        # be called here to get the cells size correctly. This
        # invalidates the condition in the next SetSize().
        # We can use self.mRenWin.SetSize(0,0) here but it will
        # cause flickering and decrease performance!
        # SetPosition(curX,curY) also works here but slower.
        self.mRenWin.GetSize()
        
        self.mRenWin.SetSize(self.width(),self.height())
        if self.mRenWin.GetInteractor():
            self.mRenWin.GetInteractor().SetSize(self.width(),self.height())

    def moveEvent(self,e):
        QtGui.QWidget.moveEvent(self,e)
        if not self.mRenWin:
            return

        self.mRenWin.SetPosition(self.x(),self.y())

    def paintEvent(self,e):
        iren = None
        if self.mRenWin:
            iren = self.mRenWin.GetInteractor()

        if (not iren) or (not iren.GetEnabled()):
            return
        iren.Render()        

    # Only make the one below the mouse cursor active
    def SelectActiveRenderer(self,iren):
        epos = iren.GetEventPosition()
        rens = iren.GetRenderWindow().GetRenderers()
        rens.InitTraversal()
        for i in range(rens.GetNumberOfItems()):
            ren = rens.GetNextItem()
            ren.SetInteractive(ren.IsInViewport(epos[0], epos[1]))

    def mousePressEvent(self,e):
        self.emit(QtCore.SIGNAL("mouseEvent(QMouseEvent)"),e)

        iren = None
        if self.mRenWin:
            iren = self.mRenWin.GetInteractor()

        if (not iren) or (not iren.GetEnabled()):
            return

        ctrl = (e.modifiers()&QtCore.Qt.ControlModifier)
        iren.SetEventInformationFlipY(e.x(),e.y(),
                                      ctrl,
                                      (e.modifiers()&QtCore.Qt.ShiftModifier),
                                      chr(0),
                                      e.type()==QtCore.QEvent.MouseButtonDblClick, None)

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
        iren = None
        if self.mRenWin:
            iren = self.mRenWin.GetInteractor()

        if (not iren) or (not iren.GetEnabled()):
            return

        iren.InvokeEvent("EnterEvent")

    def leaveEvent(self,e):
        iren = None
        if self.mRenWin:
            iren = self.mRenWin.GetInteractor()

        if (not iren) or (not iren.GetEnabled()):
            return

        iren.InvokeEvent("LeaveEvent")

    def mouseReleaseEvent(self,e):
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
        pass

    def focusOutEvent(self,e):
        pass

    def contextMenuEvent(self,e):
        iren = None
        if self.mRenWin:
            iren = self.mRenWin.GetInteractor()

        if (not iren) or (not iren.GetEnabled()):
            return

        ctrl = int(e.modifiers()&QtCore.Qt.ControlModifier)
        shift = int(e.modifiers()&QtCore.Qt.ShiftModifier)
        iren.SetEventInformationFlipY(e.x(),e.y(),ctrl,shift,chr(0),0,None)
        iren.InvokeEvent("ContextMenuEvent")

    def paintEngine(self):
        return None

    def ascii_to_key_sym(self,i):
        global AsciiToKeySymTable
        return AsciiToKeySymTable[i]

    def qt_key_to_key_sym(self,i):
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
        result = []
        renWin = self.GetRenderWindow()
        renderers = renWin.GetRenderers()
        renderers.InitTraversal()
        for i in range(renderers.GetNumberOfItems()):
            result.append(renderers.GetNextItem())
        return result

    def getActiveRenderer(self, iren):
        epos = iren.GetEventPosition()
        rens = iren.GetRenderWindow().GetRenderers()
        rens.InitTraversal()
        for i in range(rens.GetNumberOfItems()):
            ren = rens.GetNextItem()
            if ren.IsInViewport(epos[0], epos[1]):
                return ren
        return None

    def findSheetTabWidget(self):
        p = self.parent()
        while p:
            if hasattr(p, 'isSheetTabWidget'):
                if p.isSheetTabWidget()==True:
                    return p
            p = p.parent()
        return None

    def interactionEvent(self, istyle, name):
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


class QVTKWidgetCapture(QtGui.QAction):
    def __init__(self, parent=None):
        QtGui.QAction.__init__(self,
                               QtGui.QIcon(":/images/camera.png"),
                               "&Capture image to file",
                               parent)
        self.setStatusTip("Capture the rendered image to a file")


class QVTKWidgetCaptureToHistory(QtGui.QAction):
    def __init__(self, parent=None):
        QtGui.QAction.__init__(self,
                               QtGui.QIcon(":/images/camera_mount.png"),
                               "&Capture image to history",
                               parent)
        self.setStatusTip("Capture the rendered image to the history for playback later")

class QVTKWidgetPlayHistory(QtGui.QAction):
    def __init__(self, parent=None):
        QtGui.QAction.__init__(self,
                               QtGui.QIcon(":/images/player_play.png"),
                               "&Play the history",
                               parent)
        self.setStatusTip("Playback all image files kept in the history")

class QVTKWidgetPauseHistory(QtGui.QAction):
    def __init__(self, parent=None):
        QtGui.QAction.__init__(self,
                               QtGui.QIcon(":/images/player_pause.png"),
                               "Pa&use the history playback",
                               parent)
        self.setStatusTip("Pause the playback, later it can be resumed")

class QVTKWidgetEjectHistory(QtGui.QAction):
    def __init__(self, parent=None):
        QtGui.QAction.__init__(self,
                               QtGui.QIcon(":/images/player_eject.png"),
                               "&Return to VTK interactive mode",
                               parent)
        self.setStatusTip("Stop the playback and returned to the interactive mode")

class QVTKWidgetToolBar(CellToolBar):
    def createToolBar(self):
        self.setOrientation(QtCore.Qt.Vertical)
        self.appendAction(QVTKWidgetCapture(self))
        self.appendAction(QVTKWidgetCaptureToHistory(self))
        self.appendAction(QVTKWidgetPlayHistory(self))
        self.appendAction(QVTKWidgetPauseHistory(self))

import os
from PyQt4 import QtCore, QtGui
import sip
import vtk
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from vistrails.core import system
import vistrails.core.db.action
from vistrails.gui.qt import qt_super
from vistrails.packages.spreadsheet.spreadsheet_cell import QCellWidget, QCellToolBar


class QVTKWidget(QCellWidget):
    """
    QVTKWidget is the actual rendering widget that can display
    vtkRenderer inside a Qt QWidget

    """
    save_formats = ["PNG image (*.png)", "PDF files (*.pdf)"]

    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags(), **args ):
        """ QVTKWidget(parent: QWidget, f: WindowFlags) -> QVTKWidget
        Initialize QVTKWidget with a toolbar with its own device
        context

        """
        QCellWidget.__init__(self, parent, f | QtCore.Qt.MSWindowsOwnDC)

        self.interacting = None
        self.mRenWin = None
        self.iren = None
        self.createInteractor = args.get( 'createInteractor', True )
        self.setAttribute(QtCore.Qt.WA_OpaquePaintEvent)
        self.setAttribute(QtCore.Qt.WA_PaintOnScreen)
        self.setMouseTracking(True)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,
                                             QtGui.QSizePolicy.Expanding))
        self.toolBarType = QVTKWidgetToolBar
        self.iHandlers = []
        self.setAnimationEnabled(True)
        self.renderer_maps = {}

    def removeObserversFromInteractorStyle(self):
        """ removeObserversFromInteractorStyle() -> None
        Remove all python binding from interactor style observers for
        safely freeing the cell

        """
        if self.iren:
            style = self.iren.GetInteractorStyle()
            style.RemoveObservers("InteractionEvent")
            style.RemoveObservers("EndPickEvent")
            style.RemoveObservers("CharEvent")
            style.RemoveObservers("MouseWheelForwardEvent")
            style.RemoveObservers("MouseWheelBackwardEvent")

    def addObserversToInteractorStyle(self):
        """ addObserversToInteractorStyle() -> None
        Assign observer to the current interactor style

        """
        if self.iren:
            style = self.iren.GetInteractorStyle()
            style.AddObserver("InteractionEvent", self.interactionEvent)
            style.AddObserver("EndPickEvent", self.interactionEvent)
            style.AddObserver("CharEvent", self.charEvent)
            style.AddObserver("MouseWheelForwardEvent", self.interactionEvent)
            style.AddObserver("MouseWheelBackwardEvent", self.interactionEvent)

    def deleteLater(self):
        """ deleteLater() -> None
        Make sure to free render window resource when
        deallocating. Overriding PyQt deleteLater to free up
        resources

        """
        self.renderer_maps = {}
        for ren in self.getRendererList():
            self.mRenWin.RemoveRenderer(ren)

        self.removeObserversFromInteractorStyle()

        self.updateContents(([], None, [], None, None))

        self.SetRenderWindow(None)

        QCellWidget.deleteLater(self)

    def updateContents(self, inputPorts, cameralist = None):
        """ updateContents(inputPorts: tuple)
        Updates the cell contents with new vtkRenderer

        """
        renWin = self.GetRenderWindow()
        for iHandler in self.iHandlers:
            if iHandler.observer:
                iHandler.observer.vtkInstance.SetInteractor(None)
            iHandler.clear()

        # Remove old renderers first
        oldRenderers = self.getRendererList()
        for renderer in oldRenderers:
            renWin.RemoveRenderer(renderer)
            renderer.SetRenderWindow(None)
        del oldRenderers

        (renderers, renderView, self.iHandlers, iStyle, picker) = inputPorts
        if renderView:
            renderView.vtkInstance.SetupRenderWindow(renWin)
            renderers = [renderView.vtkInstance.GetRenderer()]
        self.renderer_maps = {}
        self.usecameras = False
        if cameralist != None and len(cameralist) == len(renderers):
            self.usecameras = True
        j = 0
        for renderer in renderers:
            if renderView==None:
                vtkInstance = renderer.vtkInstance
                renWin.AddRenderer(vtkInstance)
                self.renderer_maps[vtkInstance] = renderer.moduleInfo['moduleId']
            else:
                vtkInstance = renderer
            if hasattr(vtkInstance, 'IsActiveCameraCreated'):
                if self.usecameras:
                    vtkInstance.SetActiveCamera(cameralist[j])
                    j = j + 1
                if not vtkInstance.IsActiveCameraCreated():
                    vtkInstance.ResetCamera()
                else:
                    vtkInstance.ResetCameraClippingRange()

        if picker:
            self.iren.SetPicker(picker.vtkInstance)

        # Update interactor style
        self.removeObserversFromInteractorStyle()
        if renderView==None:
            if iStyle==None:
                iStyleInstance = vtk.vtkInteractorStyleTrackballCamera()
            else:
                iStyleInstance = iStyle.vtkInstance
            self.iren.SetInteractorStyle(iStyleInstance)
        self.addObserversToInteractorStyle()

        for iHandler in self.iHandlers:
            if iHandler.observer:
                iHandler.observer.vtkInstance.SetInteractor(self.iren)
        renWin.Render()

        # Capture window into history for playback
        # Call this at the end to capture the image after rendering
        QCellWidget.updateContents(self, inputPorts)

    def GetRenderWindow(self):
        """ GetRenderWindow() -> vtkRenderWindow
        Return the associated vtkRenderWindow

        """
        if not self.mRenWin:
            win = vtk.vtkRenderWindow()
            win.DoubleBufferOn()
            win.StereoCapableWindowOn()
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
            if system.systemType!='Linux':
                self.mRenWin.SetInteractor(None)
            if self.mRenWin.GetMapped():
                self.mRenWin.Finalize()

        self.mRenWin = w

        if self.mRenWin:
            self.mRenWin.Register(None)
            if self.mRenWin.GetMapped():
                self.mRenWin.Finalize()
            if system.systemType=='Linux':
                try:
                    display = int(QtGui.QX11Info.display())
                except TypeError:
                    # This was changed for PyQt4.2
                    assert isinstance(QtGui.QX11Info.display(), QtGui.Display)
                    display = sip.unwrapinstance(QtGui.QX11Info.display())
                v = vtk.vtkVersion()
                version = [v.GetVTKMajorVersion(),
                           v.GetVTKMinorVersion(),
                           v.GetVTKBuildVersion()]
                display = hex(display)[2:]
                if version < [5, 7, 0]:
                    vp = ('_%s_void_p\0x00' % display)
                elif version < [6, 2, 0]:
                    vp = ('_%s_void_p' % display)
                else:
                    vp = ('_%s_p_void' % display)
                self.mRenWin.SetDisplayId(vp)
                self.resizeWindow(1,1)
            self.mRenWin.SetWindowInfo(str(int(self.winId())))
            if self.isVisible():
                self.mRenWin.Start()

            if not self.mRenWin.GetInteractor():
                if self.createInteractor:
                    self.iren = QVTKRenderWindowInteractor(rw=self.mRenWin)
#                    iren = vtk.vtkGenericRenderWindowInteractor()
#                if system.systemType=='Darwin':
#                    iren.InstallMessageProcOff()
#                    self.iren.Initialize()
#                if system.systemType=='Linux':
#                    system.XDestroyWindow(self.mRenWin.GetGenericDisplayId(),
#                                          self.mRenWin.GetGenericWindowId())
                self.mRenWin.SetWindowInfo(str(int(self.winId())))
                self.resizeWindow(self.width(), self.height())
                self.mRenWin.SetPosition(self.x(), self.y())

    def GetInteractor(self):
        """ GetInteractor() -> vtkInteractor
        Return the vtkInteractor control this QVTKWidget
        """
        return self.GetRenderWindow().GetInteractor()

    def event(self, e):
        """ event(e: QEvent) -> depends on event type
        Process window and interaction events

        """
#        print "Window Event: %s"  % ( str(e) )
        if e.type()==QtCore.QEvent.ParentAboutToChange:
            if self.mRenWin:
                if self.mRenWin.GetMapped():
                    self.mRenWin.Finalize()
        else:
            if e.type()==QtCore.QEvent.ParentChange:
                if self.mRenWin:
                    self.mRenWin.SetWindowInfo(str(int(self.winId())))
                    if self.isVisible():
                        self.mRenWin.Start()

        if QtCore.QObject.event(self,e):
            return 1

        if e.type() == QtCore.QEvent.KeyPress:
            self.keyPressEvent(e)
            if e.isAccepted():
                return e.isAccepted()

        return qt_super(QVTKWidget, self).event(e)

        # return QtGui.QWidget.event(self,e)
        # Was this right? Wasn't this supposed to be QCellWidget.event()?

    def resizeWindow(self, width, height):
        """ resizeWindow(width: int, height: int) -> None
        Work around vtk bugs for resizing window

        """
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

        self.mRenWin.SetSize(width, height)
        self.mRenWin.Modified()
        if self.mRenWin.GetInteractor():
            self.mRenWin.GetInteractor().UpdateSize(width, height)
            self.mRenWin.GetInteractor().InvokeEvent(vtk.vtkCommand.ConfigureEvent)

    def resizeEvent(self, e):
        """ resizeEvent(e: QEvent) -> None
        Re-adjust the vtkRenderWindow size then QVTKWidget resized

        """
        qt_super(QVTKWidget, self).resizeEvent(e)
        if not self.mRenWin:
            return

        self.resizeWindow(self.width(), self.height())
        if self.mRenWin.GetInteractor():
            self.mRenWin.GetInteractor().Render()
        else:
            self.mRenWin.Render()

    def moveEvent(self,e):
        """ moveEvent(e: QEvent) -> None
        Echo the move event into vtkRenderWindow

        """
        qt_super(QVTKWidget, self).moveEvent(e)
        if not self.mRenWin:
            return

        self.mRenWin.SetPosition(self.x(),self.y())

    def paintEngine(self):
        """ paintEngine() -> QPaintEngine
        On Windows, this has to return None to fully disable
        double-buffer (we let vtkRenderWindow handle this instead).

        """
        if system.systemType in ['Windows', 'Microsoft']:
            return None
        else:
            return QCellWidget.paintEngine(self)

    def paintEvent(self, e):
        """ paintEvent(e: QPaintEvent) -> None
        Paint the QVTKWidget with vtkRenderWindow

        """

        if (not self.iren) or (not self.iren.GetEnabled()):
            return

        if hasattr(self.mRenWin, 'UpdateGLRegion'):
            self.mRenWin.UpdateGLRegion()
        if self.mRenWin.GetInteractor():
            self.mRenWin.GetInteractor().Render()
        else:
            self.mRenWin.Render()

    def SelectActiveRenderer(self,iren):
        """ SelectActiveRenderer(iren: vtkRenderWindowIteractor) -> None
        Only make the vtkRenderer below the mouse cursor active

        """
        epos = iren.GetEventPosition()
        rens = iren.GetRenderWindow().GetRenderers()
        rens.InitTraversal()
        for i in xrange(rens.GetNumberOfItems()):
            ren = rens.GetNextItem()
            ren.SetInteractive(ren.IsInViewport(epos[0], epos[1]))

    def mousePressEvent(self,e):
        """ mousePressEvent(e: QMouseEvent) -> None
        Echo mouse event to vtkRenderWindowwInteractor

        """
        if (not self.iren) or (not self.iren.GetEnabled()):
            return


        ctrl = bool(e.modifiers() & QtCore.Qt.ControlModifier)

        isDoubleClick = e.type()==QtCore.QEvent.MouseButtonDblClick

        self.iren.SetEventInformationFlipY(e.x(),e.y(),
                                      ctrl,
                                      bool(e.modifiers()&QtCore.Qt.ShiftModifier),
                                      chr(0),
                                      isDoubleClick,
                                      None)
        invoke = {QtCore.Qt.LeftButton:"LeftButtonPressEvent",
                  QtCore.Qt.MidButton:"MiddleButtonPressEvent",
                  QtCore.Qt.RightButton:"RightButtonPressEvent"}

        self.SelectActiveRenderer(self.iren)

        if ctrl:
            e.ignore()

        self.interacting = self.getActiveRenderer(self.iren)

        if e.button() in invoke:
            self.iren.InvokeEvent(invoke[e.button()])


    def mouseMoveEvent(self,e):
        """ mouseMoveEvent(e: QMouseEvent) -> None
        Echo mouse event to vtkRenderWindowwInteractor

        """
        if (not self.iren) or (not self.iren.GetEnabled()):
            return


        ctrl = bool(e.modifiers() & QtCore.Qt.ControlModifier)

        self.iren.SetEventInformationFlipY(e.x(),e.y(),
                                      ctrl,
                                      bool(e.modifiers()&QtCore.Qt.ShiftModifier),
                                      chr(0), 0, None)

        self.iren.InvokeEvent("MouseMoveEvent")

    def enterEvent(self,e):
        """ enterEvent(e: QEvent) -> None
        Echo mouse event to vtkRenderWindowwInteractor

        """

        if (not self.iren) or (not self.iren.GetEnabled()):
            return

        self.iren.InvokeEvent("EnterEvent")

    def leaveEvent(self,e):
        """ leaveEvent(e: QEvent) -> None
        Echo mouse event to vtkRenderWindowwInteractor

        """

        if (not self.iren) or (not self.iren.GetEnabled()):
            return

        self.iren.InvokeEvent("LeaveEvent")

    def mouseReleaseEvent(self,e):
        """ mouseReleaseEvent(e: QEvent) -> None
        Echo mouse event to vtkRenderWindowwInteractor

        """

        if (not self.iren) or (not self.iren.GetEnabled()):
            return


        ctrl = bool(e.modifiers() & QtCore.Qt.ControlModifier)

        self.iren.SetEventInformationFlipY(e.x(),e.y(),
                                      ctrl,
                                      bool(e.modifiers()&QtCore.Qt.ShiftModifier),
                                      chr(0),0,None)

        invoke = {QtCore.Qt.LeftButton:"LeftButtonReleaseEvent",
                  QtCore.Qt.MidButton:"MiddleButtonReleaseEvent",
                  QtCore.Qt.RightButton:"RightButtonReleaseEvent"}

        self.interacting = None

        if e.button() in invoke:
            self.iren.InvokeEvent(invoke[e.button()])

    def keyPressEvent(self,e):
        """ keyPressEvent(e: QKeyEvent) -> None
        Disallow 'quit' key in vtkRenderWindowwInteractor and sync the others

        """
        if (not self.iren) or (not self.iren.GetEnabled()):
            return

        ascii_key = None
        if e.text().length()>0:
            ascii_key = e.text().toLatin1()[0]
        else:
            ascii_key = chr(0)

        keysym = self.ascii_to_key_sym(ord(ascii_key))

        if not keysym:
            keysym = self.qt_key_to_key_sym(e.key())

        # Ignore Ctrl-anykey

        ctrl = bool(e.modifiers() & QtCore.Qt.ControlModifier)

        shift = bool(e.modifiers()&QtCore.Qt.ShiftModifier)
        if ctrl:
            e.ignore()
            return

        self.iren.SetKeyEventInformation(ctrl,shift,ascii_key, e.count(), keysym)

        self.iren.InvokeEvent("KeyPressEvent")

        if ascii_key:
            self.iren.InvokeEvent("CharEvent")


    def keyReleaseEvent(self,e):
        """ keyReleaseEvent(e: QKeyEvent) -> None
        Disallow 'quit' key in vtkRenderWindowwInteractor and sync the others

        """
        if (not self.iren) or (not self.iren.GetEnabled()):
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

        ctrl = bool(e.modifiers() & QtCore.Qt.ControlModifier)
        shift = bool(e.modifiers()&QtCore.Qt.ShiftModifier)
        if (keysym in ['q','e'] or ctrl):
            e.ignore()
            return

        self.iren.SetKeyEventInformation(ctrl, shift, ascii_key, e.count(), keysym)

        self.iren.InvokeEvent("KeyReleaseEvent")

    def wheelEvent(self,e):
        """ wheelEvent(e: QWheelEvent) -> None
        Zoom in/out while scrolling the mouse

        """

        if (not self.iren) or (not self.iren.GetEnabled()):
            return

        ctrl = bool(e.modifiers() & QtCore.Qt.ControlModifier)
        self.iren.SetEventInformationFlipY(e.x(),e.y(),
                                      ctrl,
                                      bool(e.modifiers()&QtCore.Qt.ShiftModifier),
                                      chr(0),0,None)

        self.SelectActiveRenderer(self.iren)

        if e.delta()>0:
            self.iren.InvokeEvent("MouseWheelForwardEvent")
        else:
            self.iren.InvokeEvent("MouseWheelBackwardEvent")

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
        if (not self.iren) or (not self.iren.GetEnabled()):
            return

        ctrl = int(e.modifiers() & QtCore.Qt.ControlModifier)

        shift = int(e.modifiers()&QtCore.Qt.ShiftModifier)
        self.iren.SetEventInformationFlipY(e.x(),e.y(),ctrl,shift,chr(0),0,None)
        self.iren.InvokeEvent("ContextMenuEvent")

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
        handler = {QtCore.Qt.Key_Backspace:"Backspace",
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
        for i in xrange(renderers.GetNumberOfItems()):
            result.append(renderers.GetNextItem())
        return result

    def getActiveRenderer(self, iren):
        """ getActiveRenderer(iren: vtkRenderWindowwInteractor) -> vtkRenderer
        Return the active vtkRenderer under mouse

        """
        epos = list(iren.GetEventPosition())
        if epos[1]<0:
            epos[1] = -epos[1]
        rens = iren.GetRenderWindow().GetRenderers()
        rens.InitTraversal()
        for i in xrange(rens.GetNumberOfItems()):
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

    def getRenderersInCellList(self, sheet, cells):
        """ isRendererIn(sheet: spreadsheet.StandardWidgetSheet,
                         cells: [(int,int)]) -> bool
        Get the list of renderers in side a list of (row, column)
        cells.

        """
        rens = []
        for (row, col) in cells:
            cell = sheet.getCell(row, col)
            if hasattr(cell, 'getRendererList'):
                rens += cell.getRendererList()
        return rens

    def getSelectedCellWidgets(self):
        sheet = self.findSheetTabWidget()
        if sheet:
            ren = self.interacting
            if not ren and self.iren and self.iren.GetEnabled():
                ren = self.getActiveRenderer(self.iren)
            if ren:
                cells = sheet.getSelectedLocations()
                if (ren in self.getRenderersInCellList(sheet, cells)):
                    return [sheet.getCell(row, col)
                            for (row, col) in cells
                            if hasattr(sheet.getCell(row, col),
                                       'getRendererList')]
        return []

    def interactionEvent(self, istyle, name):
        """ interactionEvent(istyle: vtkInteractorStyle, name: str) -> None
        Make sure interactions sync across selected renderers

        """
        if name=='MouseWheelForwardEvent':
            istyle.OnMouseWheelForward()
        if name=='MouseWheelBackwardEvent':
            istyle.OnMouseWheelBackward()
        ren = self.interacting
        if not ren:
            ren = self.getActiveRenderer(istyle.GetInteractor())
        if ren:
            cam = ren.GetActiveCamera()
            cpos = cam.GetPosition()
            cfol = cam.GetFocalPoint()
            cup = cam.GetViewUp()
            for cell in self.getSelectedCellWidgets():
                if cell!=self and hasattr(cell, 'getRendererList'):
                    rens = cell.getRendererList()
                    for r in rens:
                        if r!=ren:
                            dcam = r.GetActiveCamera()
                            dcam.SetPosition(cpos)
                            dcam.SetFocalPoint(cfol)
                            dcam.SetViewUp(cup)
                            r.ResetCameraClippingRange()
                    cell.update()

    def charEvent(self, istyle, name):
        """ charEvent(istyle: vtkInteractorStyle, name: str) -> None
        Make sure key presses also sync across selected renderers

        """
        iren = istyle.GetInteractor()
        ren = self.interacting
        if not ren: ren = self.getActiveRenderer(iren)
        if ren:
            keyCode = iren.GetKeyCode()
            if keyCode in ['w','W','s','S','r','R','p','P']:
                for cell in self.getSelectedCellWidgets():
                    if hasattr(cell, 'GetInteractor'):
                        selectedIren = cell.GetInteractor()
                        selectedIren.SetKeyCode(keyCode)
                        selectedIren.GetInteractorStyle().OnChar()
                        selectedIren.Render()
            istyle.OnChar()

    def saveToPNG(self, filename):
        """ saveToPNG(filename: str) -> filename or vtkUnsignedCharArray

        Save the current widget contents to an image file. If
        filename is None, then it returns the vtkUnsignedCharArray containing
        the PNG image. Otherwise, the filename is returned.

        """
        w2i = vtk.vtkWindowToImageFilter()
        w2i.ReadFrontBufferOff()
        w2i.SetInput(self.mRenWin)
        # Render twice to get a clean image on the back buffer
        if self.mRenWin.GetInteractor():
            self.mRenWin.GetInteractor().Render()
            self.mRenWin.GetInteractor().Render()
        else:
            self.mRenWin.Render()
            self.mRenWin.Render()
        w2i.Update()
        writer = vtk.vtkPNGWriter()
        writer.SetInputConnection(w2i.GetOutputPort())
        if filename is not None:
            writer.SetFileName(filename)
        else:
            writer.WriteToMemoryOn()
        writer.Write()
        if filename is not None:
            return filename
        else:
            return writer.GetResult()

    def grabWindowPixmap(self):
        """ grabWindowImage() -> QPixmap
        Widget special grabbing function

        """
        uchar = self.saveToPNG(None)

        ba = QtCore.QByteArray()
        buf = QtCore.QBuffer(ba)
        buf.open(QtCore.QIODevice.WriteOnly)
        for i in xrange(uchar.GetNumberOfTuples()):
            c = uchar.GetValue(i)
            buf.putChar(chr(c))
        buf.close()

        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(ba, 'PNG')
        return pixmap

    def dumpToFile(self, filename):
        """dumpToFile() -> None
        Dumps itself as an image to a file, calling saveToPNG
        """
        ext = os.path.splitext(filename)[1].lower()
        if ext == '.pdf':
            self.saveToPDF(filename)
        else:
            self.saveToPNG(filename)

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



class QVTKWidgetToolBar(QCellToolBar):
    """
    QVTKWidgetToolBar derives from QCellToolBar to give the VTKCell
    a customizable toolbar

    """
    def createToolBar(self):
        """ createToolBar() -> None
        This will get call initiallly to add customizable widgets

        """
        self.addAnimationButtons()
        self.appendAction(QVTKWidgetSaveCamera(self))

class QVTKWidgetSaveCamera(QtGui.QAction):
    """
    QVTKWidgetSaveCamera is the action to capture the current camera
    of the vtk renderers and save it back to the pipeline

    """
    def __init__(self, parent=None):
        """ QVTKWidgetSaveCamera(parent: QWidget) -> QVTKWidgetSaveCamera
        Setup the image, status tip, etc. of the action

        """
        QtGui.QAction.__init__(self,
                               "Save &Camera",
                               parent)
        self.setStatusTip("Save current camera views to the pipeline")

    def setCamera(self, controller):
        ops = []
        pipeline = controller.current_pipeline
        cellWidget = self.toolBar.getSnappedWidget()
        renderers = cellWidget.getRendererList()
        for ren in renderers:
            cam = ren.GetActiveCamera()
            cpos = cam.GetPosition()
            cfol = cam.GetFocalPoint()
            cup = cam.GetViewUp()
            rendererId = cellWidget.renderer_maps[ren]
            # Looking for SetActiveCamera()
            camera = None
            renderer = pipeline.modules[rendererId]
            for c in pipeline.connections.values():
                if c.destination.moduleId==rendererId:
                    if c.destination.name=='SetActiveCamera':
                        camera = pipeline.modules[c.source.moduleId]
                        break

            if not camera:
                # Create camera
                vtk_package = 'edu.utah.sci.vistrails.vtk'
                camera = controller.create_module(vtk_package, 'vtkCamera', '',
                                                  0.0, 0.0)
                ops.append(('add', camera))

                # Connect camera to renderer
                camera_conn = controller.create_connection(camera, 'self',
                                                           renderer,
                                                           'SetActiveCamera')
                ops.append(('add', camera_conn))
            # update functions
            def convert_to_str(arglist):
                new_arglist = []
                for arg in arglist:
                    new_arglist.append(str(arg))
                return new_arglist
            functions = [('SetPosition', convert_to_str(cpos)),
                         ('SetFocalPoint', convert_to_str(cfol)),
                         ('SetViewUp', convert_to_str(cup))]
            ops.extend(controller.update_functions_ops(camera, functions))

        action = vistrails.core.db.action.create_action(ops)
        controller.add_new_action(action)
        controller.perform_action(action)
        controller.select_latest_version()

    def triggeredSlot(self, checked=False):
        """ toggledSlot(checked: boolean) -> None
        Execute the action when the button is clicked

        """
        visApp = QtCore.QCoreApplication.instance()
        if hasattr(visApp, 'builderWindow'):
            builderWindow = visApp.builderWindow
            if builderWindow:
                info = self.toolBar.sheet.getCellPipelineInfo(
                    self.toolBar.row, self.toolBar.col)
                if info:
                    info = info[0]
                    view = builderWindow.ensureVistrail(info['locator'])
                    if view:
                        controller = view.controller
                        controller.change_selected_version(info['version'])
                        self.setCamera(controller)

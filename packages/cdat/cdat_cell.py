from PyQt4 import QtCore, QtGui
from packages.spreadsheet.spreadsheet_cell import QCellWidget, QCellToolBar
from packages.spreadsheet.spreadsheet_controller import spreadsheetController
import vcs

class QCDATWidget(QCellWidget):

    def __init__(self, parent=None):
        QCellWidget.__init__(self, parent)
        self.setAttribute(QtCore.Qt.WA_PaintOnScreen)
        self.canvas = None
        self.backingStoreUpToDate = False
        self.backingStorePixmap = QtGui.QPixmap()

    def setCanvas(self, canvas):
        if self.canvas!=None:
            self.canvas.canvas.connect_gui_and_canvas(0)
        if canvas!=None:
            canvas.canvas.connect_gui_and_canvas(self.winId())
        self.canvas = canvas

    def paintEvent(self, e):
        if self.canvas!=None:
            if self.backingStoreUpToDate:
                painter = QtGui.QPainter(self)
                painter.drawPixmap(0, 0, self.backingStorePixmap)
                painter.end()
            else:
                self.canvas.canvas.paintcanvas()
                self.backingStorePixmap = QtGui.QPixmap.grabWindow(self.winId())
                self.backingStoreUpToDate = True

    def mousePressEvent(self, e):
        if self.canvas!=None:
            if e.button()==QtCore.Qt.LeftButton:
                tip = self.canvas.canvas.getdatainfo(e.x(), e.y())
                if tip!=None:
                    QtGui.QToolTip.showText(e.globalPos(), tip)

    def mouseReleaseEvent(self, e):
        QtGui.QToolTip.hideText()

    def resizeEvent(self, e):
        if self.canvas!=None:
            self.backingStoreUpToDate = False
            self.update()

    def updateContents(self, inputPorts):
        spreadsheetWindow = spreadsheetController.findSpreadsheetWindow()
        spreadsheetWindow.setUpdatesEnabled(False)
       
        if self.canvas==None:
            vcsCanvas = vcs.init()
            self.setCanvas(vcsCanvas)
        self.canvas.plot(*inputPorts)
       
        spreadsheetWindow.setUpdatesEnabled(True)

    def event(self, e):
        if self.canvas!=None:
            if e.type()==QtCore.QEvent.WindowActivate:
                self.backingStoreUpToDate = False
                self.update()
        return QCellWidget.event(self, e)

    def deleteLater(self):
        """ deleteLater() -> None        
        Make sure to free render window resource when
        deallocating. Overriding PyQt deleteLater to free up
        resources
        
        """
        self.setCanvas(None)
        QCellWidget.deleteLater(self)   

from PyQt4 import QtCore, QtGui

DisplayCellEventType = QtCore.QEvent.Type(QtCore.QEvent.User)
BatchDisplayCellEventType = QtCore.QEvent.Type(QtCore.QEvent.User+1)


class DisplayCellEvent(QtCore.QEvent):
    def __init__(self):
        QtCore.QEvent.__init__(self, DisplayCellEventType)
        self.sheetReference = None
        self.row = -1
        self.col = -1
        self.cellType = None
        self.inputPorts = None
        self.vistrail = None

class BatchDisplayCellEvent(QtCore.QEvent):
    def __init__(self):
        QtCore.QEvent.__init__(self, BatchDisplayCellEventType)
        self.displayEvents = []
        self.vistrail = None

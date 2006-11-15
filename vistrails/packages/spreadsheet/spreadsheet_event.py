################################################################################
# This file contains all Spreadsheet special Qt event classes
################################################################################
from PyQt4 import QtCore, QtGui

################################################################################

# A list of newly added events starting from QtCore.QEvent.User
DisplayCellEventType = QtCore.QEvent.Type(QtCore.QEvent.User)
BatchDisplayCellEventType = QtCore.QEvent.Type(QtCore.QEvent.User+1)

class DisplayCellEvent(QtCore.QEvent):
    """
    DisplayCellEvent is an event to notify the spreadsheet that we want to
    display input data on a specific type of widget. This is more of a data
    container class
    
    """
    def __init__(self):
        """ DisplayCellEvent() -> DisplayCellEvent
        Instantiate a display event with no location, cell type, input data nor
        an associated vistrail
        
        """
        QtCore.QEvent.__init__(self, DisplayCellEventType)
        self.sheetReference = None
        self.row = -1
        self.col = -1
        self.cellType = None
        self.inputPorts = None
        self.vistrail = None

class BatchDisplayCellEvent(QtCore.QEvent):
    """
    BatchDisplayCellEvent is similar to DisplayCellEvent but it is holding a
    serie of DisplayCellEvent. This is very helpful since DisplayCellEvent
    requires a thread-safe procedure, thus, very slow/un-safe when displaying
    more than one cell with multiple events.
    
    """    
    def __init__(self):
        """ BatchDisplayCellEvent()
        Instantiate an empty BatchDisplayCellEvent
        """
        QtCore.QEvent.__init__(self, BatchDisplayCellEventType)
        self.displayEvents = []
        self.vistrail = None

################################################################################
# This file contains the spreadsheet controller to take care of
# interactions to the spreadsheet:
#   SpreadsheetController
################################################################################
from PyQt4 import QtCore, QtGui
from spreadsheet_window import SpreadsheetWindow

################################################################################

class SpreadsheetController(object):
    """
    SpreadsheetController will act like an event dispatcher to
    interact and control the spreadsheet in a thread-safe manner
    (postEvent).

    """
    def __init__(self):
        """ SpreadsheetController() -> SpreadsheetController
        This class is more like an interface where there is no data inside
        
        """
        pass

    def findSpreadsheetWindow(self):
        """ findSpreadsheetWindow() -> QWidget
        Looking for the spreadsheet window
        
        """
        wList = QtGui.QApplication.topLevelWidgets()
        for w in wList:
            if type(w)==SpreadsheetWindow:
                return w
        return None
        
    def postEventToSpreadsheet(self, event):
        """ postEventToSpreadsheet(event: QEvent) -> None
        Post an event to the spreadsheet to make thread-safe connection
        """
        spreadsheetWindow = self.findSpreadsheetWindow()
        if spreadsheetWindow:
            QtCore.QCoreApplication.postEvent(spreadsheetWindow, QtGui.QShowEvent())
            QtCore.QCoreApplication.postEvent(spreadsheetWindow, event)    

spreadsheetController = SpreadsheetController()
registeredWidgets = {}

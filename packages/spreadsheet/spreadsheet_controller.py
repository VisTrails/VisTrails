from PyQt4 import QtCore, QtGui
from spreadsheet_window import SpreadsheetWindow

################################################################################
################################################################################
### SpreadsheetController: This will act like an event dispatcher to
### interact and control the spreadsheet in a thread-safe manner
### (postEvent).
class SpreadsheetController(object):

    def __init__(self):
        pass

    ### Looking for the spreadsheet window
    def findSpreadsheetWindow(self):
        wList = QtGui.QApplication.topLevelWidgets()
        for w in wList:
            if type(w)==SpreadsheetWindow:
                return w
        return None
        
    ### Post an event to the spreadsheet
    def postEventToSpreadsheet(self, event):
        spreadsheetWindow = self.findSpreadsheetWindow()
        if spreadsheetWindow:
            QtCore.QCoreApplication.postEvent(spreadsheetWindow, QtGui.QShowEvent())
            QtCore.QCoreApplication.postEvent(spreadsheetWindow, event)    

spreadsheetController = SpreadsheetController()
registeredWidgets = {}

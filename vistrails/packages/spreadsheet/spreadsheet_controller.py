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

    def findSpreadsheetWindow(self, show=True):
        """ findSpreadsheetWindow() -> QWidget
        Looking for the spreadsheet window
        
        """
        wList = QtGui.QApplication.topLevelWidgets()
        for w in wList:
            if type(w)==SpreadsheetWindow:
                return w
        global spreadsheetWindow
        spreadsheetWindow = SpreadsheetWindow()
        if show:
            spreadsheetWindow.configShow()
        return spreadsheetWindow
        
    def postEventToSpreadsheet(self, event):
        """ postEventToSpreadsheet(event: QEvent) -> None
        Post an event to the spreadsheet to make thread-safe connection
        """
        spreadsheetWindow = self.findSpreadsheetWindow()
        if spreadsheetWindow:
            QtCore.QCoreApplication.postEvent(spreadsheetWindow, QtGui.QShowEvent())
            QtCore.QCoreApplication.postEvent(spreadsheetWindow, event)

    def getBuilderWindow(self):
        """ getBuilderWindow() -> QWidget        
        Return the builder window of the application, or None if
        couldn't fine one
        
        """
        spreadsheetWindow = self.findSpreadsheetWindow()
        if hasattr(spreadsheetWindow.visApp, 'builderWindow'):
            return spreadsheetWindow.visApp.builderWindow
        else:
            return None

    def setEchoMode(self, echo):
        """ setEchoMode(echo: bool)
        Instruct the spreadsheet to dispatch (echo) all cell widgets
        instead of managing them on the spreadsheet

        """
        spreadsheetWindow = self.findSpreadsheetWindow(show=False)
        if spreadsheetWindow:
            spreadsheetWindow.setEchoMode(echo)

    def echoMode(self):
        """ echoMode() -> bool
        Return true if the spreadsheet is in echo mode

        """
        spreadsheetWindow = self.findSpreadsheetWindow(show=False)
        if spreadsheetWindow:
            return spreadsheetWindow.echoMode
        return None

    def getEchoCellEvents(self):
        """ getEchoCellEvents() -> [DisplayCellEvent]
        Echo back the list of all cell events that have been captured
        earlier
        
        """
        spreadsheetWindow = self.findSpreadsheetWindow(show=False)
        if spreadsheetWindow:
            events = spreadsheetWindow.getEchoCellEvents()
            spreadsheetWindow.clearEchoCellEvents()
            return events
        return None

spreadsheetController = SpreadsheetController()
registeredWidgets = {}

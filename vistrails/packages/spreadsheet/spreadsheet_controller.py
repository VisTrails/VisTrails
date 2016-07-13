###############################################################################
##
## Copyright (C) 2014-2016, New York University.
## Copyright (C) 2011-2014, NYU-Poly.
## Copyright (C) 2006-2011, University of Utah.
## All rights reserved.
## Contact: contact@vistrails.org
##
## This file is part of VisTrails.
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met:
##
##  - Redistributions of source code must retain the above copyright notice,
##    this list of conditions and the following disclaimer.
##  - Redistributions in binary form must reproduce the above copyright
##    notice, this list of conditions and the following disclaimer in the
##    documentation and/or other materials provided with the distribution.
##  - Neither the name of the New York University nor the names of its
##    contributors may be used to endorse or promote products derived from
##    this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
## AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
## THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
## PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
## OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
## WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
## OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
## ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
###############################################################################

"""This file contains the spreadsheet controller to take care of interactions
to the spreadsheet:
  SpreadsheetController
"""

from __future__ import division

from PyQt4 import QtCore, QtGui

from .spreadsheet_window import SpreadsheetWindow


spreadsheetWindow = None

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

    def findSpreadsheetWindow(self, show=True, create=True):
        """ findSpreadsheetWindow() -> QWidget
        Looking for the spreadsheet window

        """
        global spreadsheetWindow
        if spreadsheetWindow is not None:
            return spreadsheetWindow
        wList = QtGui.QApplication.topLevelWidgets()
        for w in wList:
            if isinstance(w, SpreadsheetWindow):
                spreadsheetWindow = w
                return w
        if not create:
            return None
        spreadsheetWindow = SpreadsheetWindow()
        if show:
            spreadsheetWindow.configShow()
        return spreadsheetWindow

    def postEventToSpreadsheet(self, event):
        """ postEventToSpreadsheet(event: QEvent) -> None
        Post an event to the spreadsheet to make thread-safe connection
        """
        spreadsheetWindow = self.findSpreadsheetWindow()
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
        spreadsheetWindow.setEchoMode(echo)

    def echoMode(self):
        """ echoMode() -> bool
        Return true if the spreadsheet is in echo mode

        """
        spreadsheetWindow = self.findSpreadsheetWindow(show=False)
        return spreadsheetWindow.echoMode

    def getEchoCellEvents(self):
        """ getEchoCellEvents() -> [DisplayCellEvent]
        Echo back the list of all cell events that have been captured
        earlier

        """
        spreadsheetWindow = self.findSpreadsheetWindow(show=False)
        events = spreadsheetWindow.getEchoCellEvents()
        spreadsheetWindow.clearEchoCellEvents()
        return events


spreadsheetController = SpreadsheetController()
registeredWidgets = {}

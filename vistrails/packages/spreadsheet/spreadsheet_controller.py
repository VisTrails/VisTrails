###############################################################################
##
## Copyright (C) 2011-2013, NYU-Poly.
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
##  - Neither the name of the University of Utah nor the names of its 
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
################################################################################
# This file contains the spreadsheet controller to take care of
# interactions to the spreadsheet:
#   SpreadsheetController
################################################################################
from PyQt4 import QtCore, QtGui

import warnings

################################################################################

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
        self._cellContainerClass = None
                # This could be in SpreadsheetWindow but findSpreadsheetWindow
                # is unnecessarily slow
        self._ss_hooks = None

    def findSpreadsheetWindow(self, show=True, create=True, **kwargs):
        """ findSpreadsheetWindow(...) -> QWidget
        Returns (and optionally creates) the spreadsheet window.

        You can pass keyword parameters to the constructor. A warning will be
        issued if they were ignored because the window already existed.

        """
        global spreadsheetWindow
        created = False
        if spreadsheetWindow is None and create:
            from spreadsheet_window import SpreadsheetWindow
            wList = QtGui.QApplication.topLevelWidgets()
            for w in wList:
                if isinstance(w, SpreadsheetWindow):
                    spreadsheetWindow = w
                    break
            if spreadsheetWindow is None:
                spreadsheetWindow = SpreadsheetWindow(**kwargs)
                created = True
                if show:
                    spreadsheetWindow.configShow()
        if kwargs and not created:
            warnings.warn("spreadsheetController.findSpreadsheetWindow() was "
                          "called with kwargs for the\nconstructor, but the "
                          "window already existed. Ignored.")
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

    def getCellContainerClass(self):
        if self._cellContainerClass is None:
            from vistrails.packages.spreadsheet import spreadsheet_cell
            self._cellContainerClass = spreadsheet_cell.QCellContainer
        return self._cellContainerClass

    def setCellContainerClass(self, containerclass):
        if (self._cellContainerClass is not None and
                containerclass != self._cellContainerClass):
            warnings.warn(
                    "spreadsheetController: the container class was changed!\n"
                    "This shouldn't happen and could have unknown effects on "
                    "the application\n"
                    "It either means that two different module try to set a "
                    "different container\nclass, or that "
                    "setCellContainerClass() was called after the first "
                    "access to\ngetCellContainerClass()",
                    stacklevel=2)
        self._cellContainerClass = containerclass

    _default_hooks = dict(
            # The window's menu
            window_menubar=None,
            window_menu_main=True,
            window_menu_view=True,
            window_menu_window=True,
            # Allows to close the application from the spreadsheet via Ctrl+Q
            window_quit_action=True,

            # Creates a first empty sheet 'Sheet 1' when creating the window
            window_create_first_sheet=True,
            # Allows to create a new sheet from a sheet's toolbar
            tab_create_sheet=True,
            tab_create_sheet_action=None,
            # Add the 'Open sheet' button on the toolbar
            tab_open_sheet=True,
            # Add the 'Save sheet' button on the toolbar
            tab_save_sheet=True,
            # Allows to rename a sheet from the tab bar
            tab_rename_sheet=True,
            tab_begin_rename_action=None,
            tab_end_rename_action=None,
            # Allows to close a sheet from the tab bar
            tab_close_sheet=True,
            tab_close_sheet_action=None,
            # Allows to delete (i.e. empty) a cell in the sheet
            tab_delete_cell=True,
            # Additional actions or widgets to add to the toolbar
            toolbar_actions=None,
    )

    def set_hooks(self, ss_hooks):
        if self._ss_hooks is not None:
            warnings.warn(
                    "spreadsheetController: the hooks dict was changed!\n"
                    "This shouldn't happen and could have unknown effects on "
                    "the application\n"
                    "It either means that two different module try to set a "
                    "different set of hooks,\nor that the dict was assigned "
                    "after the first access",
                    stacklevel=2)
        self._ss_hooks = ss_hooks

    def _get_hook(self, hook):
        if self._ss_hooks is None:
            self._ss_hooks = dict()
        try:
            return self._ss_hooks[hook]
        except KeyError:
            return self._default_hooks[hook]

spreadsheetController = SpreadsheetController()
get_ss_hook = spreadsheetController._get_hook
registeredWidgets = {}

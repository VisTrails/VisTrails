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
# This file contains all Spreadsheet special Qt event classes
################################################################################
from PyQt4 import QtCore, QtGui

################################################################################

# A list of newly added events starting from QtCore.QEvent.User
DisplayCellEventType = QtCore.QEvent.Type(QtCore.QEvent.User)
BatchDisplayCellEventType = QtCore.QEvent.Type(QtCore.QEvent.User+1)
RepaintCurrentSheetEventType = QtCore.QEvent.Type(QtCore.QEvent.User+2)

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

class RepaintCurrentSheetEvent(QtCore.QEvent):
    """
    RepaintCurrentSheetEvent signal the spreadsheet to call repaint
    for all cells in the current sheet
    
    """    
    def __init__(self):
        """ RepaintCurrentSheetEvent() -> RepaintCurrentSheetEvent
        Initialize the event type
        
        """
        QtCore.QEvent.__init__(self, RepaintCurrentSheetEventType)

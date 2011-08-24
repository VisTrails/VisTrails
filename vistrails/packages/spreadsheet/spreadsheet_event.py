###############################################################################
##
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
        self.rowSpan = -1
        self.colSpan = -1
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

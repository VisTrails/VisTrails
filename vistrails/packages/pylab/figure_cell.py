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
""" This file describe a new type of spreadsheet cell to embed
Matplotlib viewer into our spreadsheet

"""
from PyQt4 import QtGui
from packages.spreadsheet.basic_widgets import SpreadsheetCell
from packages.spreadsheet.spreadsheet_cell import QCellWidget
import pylab

################################################################################

class MplFigureCell(SpreadsheetCell):
    """
    MplFigureCell is a spreadsheet cell for displaying Figure from
    Matplotlib

    """
    def compute(self):
        """ compute() -> None        
        The class will take the figure manager and embed it into the spreadsheet
        
        """
        if self.hasInputFromPort('FigureManager'):
            mfm = self.getInputFromPort('FigureManager')
            self.displayAndWait(MplFigureCellWidget, (mfm.figManager, ))

class MplFigureCellWidget(QCellWidget):
    """
    MplFigureCellWidget is the actual QWidget taking the FigureManager
    as a child for displaying figures
    
    """
    def __init__(self, parent=None):
        """ MplFigureCellWidget(parent: QWidget) -> MplFigureCellWidget
        Initialize the widget with its central layout
        
        """
        QCellWidget.__init__(self, parent)
        centralLayout = QtGui.QVBoxLayout()
        self.setLayout(centralLayout)
        centralLayout.setMargin(0)
        centralLayout.setSpacing(0)
        self.figManager = None

    def updateContents(self, inputPorts):
        """ updateContents(inputPorts: tuple) -> None
        Update the widget contents based on the input data
        
        """
        (newFigManager, ) = inputPorts
        # Update the new figure canvas
        newFigManager.canvas.draw()

        # Replace the old one with the new one
        if newFigManager!=self.figManager:
            
            # Remove the old figure manager
            if self.figManager:
                self.figManager.window.hide()
                self.layout().removeWidget(self.figManager.window)

            # Add the new one in
            self.layout().addWidget(newFigManager.window)

            # Destroy the old one if possible
            if self.figManager:
                
                try:                    
                    pylab.close(self.figManager.canvas.figure)
                # There is a bug in Matplotlib backend_qt4. It is a
                # wrong command for Qt4. Just ignore it and continue
                # to destroy the widget
                except:
                    pass
                
                self.figManager.window.deleteLater()
                del self.figManager

            # Save back the manager
            self.figManager = newFigManager
            self.update()

    def deleteLater(self):
        """ deleteLater() -> None        
        Overriding PyQt deleteLater to free up resources
        
        """
        # Destroy the old one if possible
        if self.figManager:
             
            try:                    
                pylab.close(self.figManager.canvas.figure)
            # There is a bug in Matplotlib backend_qt4. It is a
            # wrong command for Qt4. Just ignore it and continue
            # to destroy the widget
            except:
                pass
            
            self.figManager.window.deleteLater()
        QCellWidget.deleteLater(self)

    def grabWindowPixmap(self):
        """ grabWindowPixmap() -> QPixmap
        Widget special grabbing function
 	       
        """
        return QtGui.QPixmap.grabWidget(self.figManager.canvas)

    def dumpToFile(self, filename):
        #resizing to default size so the image is not clipped
        previous_size = tuple(self.figManager.canvas.figure.get_size_inches())
        self.figManager.canvas.figure.set_size_inches(8.0,6.0)
        self.figManager.canvas.print_figure(filename)
        self.figManager.canvas.figure.set_size_inches(*previous_size, forward=True)
        
    def saveToPDF(self, filename):
        #resizing to default size so the image is not clipped
        previous_size = tuple(self.figManager.canvas.figure.get_size_inches())
        self.figManager.canvas.figure.set_size_inches(8.0,6.0)
        self.figManager.canvas.print_figure(filename)
        self.figManager.canvas.figure.set_size_inches(*previous_size, forward=True)

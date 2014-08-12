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
from PyQt4 import QtCore, QtGui
import os

import matplotlib
import pylab
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.backend_bases import NavigationToolbar2, FigureManagerBase

from vistrails.packages.spreadsheet.basic_widgets import SpreadsheetCell, SpreadsheetMode
from vistrails.packages.spreadsheet.spreadsheet_cell import QCellWidget, QCellToolBar

FigureCanvasQTAgg.DEBUG = True

################################################################################

class MplFigureToSpreadsheet(SpreadsheetMode):
    @classmethod
    def can_compute(cls):
        return SpreadsheetMode.can_compute()
        return True

    def compute_output(self, output_module, configuration=None):
        fig = output_module.get_input('value')
        self.display_and_wait(output_module, configuration,
                              MplFigureCellWidget, (fig,))

class MplFigureCell(SpreadsheetCell):
    """
    MplFigureCell is a spreadsheet cell for displaying Figure from
    Matplotlib

    """
    _input_ports = [("figure", "(MplFigure)")]

    def compute(self):
        """ compute() -> None        
        The class will take the figure manager and embed it into the spreadsheet
        
        """
        if self.has_input('figure'):
            fig = self.get_input('figure')
            self.displayAndWait(MplFigureCellWidget, (fig, ))

class MplFigureCellWidget(QCellWidget):
    """
    MplFigureCellWidget is the actual QWidget taking the FigureManager
    as a child for displaying figures

    """
    save_formats = ["Portable Document Format (*.pdf)",
                    "Portable Network Graphic (*.png)",
                    "PostScript (*.ps *.eps)",
                    "Raw images (*.raw *.rgba)",
                    "Scalable Vector Graphics (*.svg *.svgz)"]

    def __init__(self, parent=None):
        """ MplFigureCellWidget(parent: QWidget) -> MplFigureCellWidget
        Initialize the widget with its central layout
        
        """
        QCellWidget.__init__(self, parent)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        centralLayout = QtGui.QVBoxLayout()
        self.setLayout(centralLayout)
        centralLayout.setMargin(0)
        centralLayout.setSpacing(0)
        self.canvas = None
        self.figure = None
        self.figManager = None
        self.toolBarType = MplFigureCellToolBar
        self.mplToolbar = None

    def updateContents(self, inputPorts):
        """ updateContents(inputPorts: tuple) -> None
        Update the widget contents based on the input data
        
        """
        (fig, ) = inputPorts
        if not self.figure or self.figure.number != fig.figInstance.number:
            if self.layout().count() > 0:
                self.layout().removeWidget(self.canvas)

            self.figure = fig.figInstance

            self.canvas = FigureCanvasQTAgg(self.figure)
            self.mplToolbar = MplNavigationToolbar(self.canvas, None)
            self.canvas.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                      QtGui.QSizePolicy.Expanding)
            self.layout().addWidget(self.canvas)

    def keyPressEvent(self, event):
        print "KEY PRESS:",  event.key()
        self.canvas.keyPressEvent(event)

    def keyReleaseEvent(self, event):
        print "KEY RELEASE:", event.key()
        self.canvas.keyReleaseEvent(event)

    def deleteLater(self):
        """ deleteLater() -> None        
        Overriding PyQt deleteLater to free up resources
        
        """
        # Destroy the old one if possible
        if self.figure is not None:
            print "pylab:", pylab
            print "self.figure:", self.figure
            pylab.close(self.figure)

        QCellWidget.deleteLater(self)

    def grabWindowPixmap(self):
        """ grabWindowPixmap() -> QPixmap
        Widget special grabbing function
        
        """
        return QtGui.QPixmap.grabWidget(self.canvas)

    def dumpToFile(self, filename):
        previous_size = tuple(self.figure.get_size_inches())
        self.figure.set_size_inches(8.0,6.0)
        self.canvas.print_figure(filename)
        self.figure.set_size_inches(previous_size[0],previous_size[1])
        self.canvas.draw()
        
    def saveToPDF(self, filename):
        previous_size = tuple(self.figure.get_size_inches())
        self.figure.set_size_inches(8.0,6.0)
        self.canvas.print_figure(filename)
        self.figure.set_size_inches(previous_size[0],previous_size[1])
        self.canvas.draw()

class MplNavigationToolbar(NavigationToolbar2QT):
    # override a bunch of stuff here...
    def __init__(self, canvas, parent):
        self.canvas = canvas
        NavigationToolbar2.__init__(self, canvas)

    def _init_toolbar(self):
        self.adj_window = None

    def destroy(self):
        pass

    def pan(self, *args):
        NavigationToolbar2.pan(self, *args)
    
    def zoom(self, *args):
        NavigationToolbar2.zoom(self, *args)
        
    def set_message(self, s):
        pass

    def save_figure(self, *args):
        pass

    def set_history_buttons(self):
        pass

class MplFigureCellToolBar(QCellToolBar):
    def createToolBar(self):
        # can be copied from NavigationToolbar2QT... with checkable added
        toolitems = (
            ('Home', 'Reset original view', 'home.ppm', 'home', False),
            ('Back', 'Back to  previous view','back.ppm', 'back', False),
            ('Forward', 'Forward to next view','forward.ppm', 'forward', 
             False),
            ('Pan', 'Pan axes with left mouse, zoom with right', 'move.ppm', 
             'pan', True),
            ('Zoom', 'Zoom to rectangle','zoom_to_rect.ppm', 'zoom', True),
            )
        icondir = os.path.join(matplotlib.rcParams[ 'datapath' ],'images')
        exclusive_actions = {}
        actions = {}
        for (text, tooltip_text, image_file, callback, checkable) in toolitems:
            icon = QtGui.QIcon(os.path.join(icondir, image_file))
            action = QtGui.QAction(icon, text, self)
            action.setStatusTip(tooltip_text)
            action.setCheckable(checkable)
            actions[text] = action
            if text == 'Pan' or text == 'Zoom':
                exclusive_actions[text] = action

        def get_callback(act, cb, txt):
            print "CONSTRUCTING CALLBACK!", act, cb, txt
            def callback():
                print "GOT CALLBACK!!"
                cellWidget = act.toolBar.getSnappedWidget()
                print "CALLING callback", cb
                getattr(cellWidget.mplToolbar, cb)()
                if txt in exclusive_actions:
                    for t, a in exclusive_actions.iteritems():
                        if txt != t:
                            a.setChecked(False)
            return callback


        for (text, tooltip_text, image_file, callback, checkable) in toolitems:
            action = actions[text]
            action.triggeredSlot = get_callback(action, callback, text)
            self.appendAction(action)

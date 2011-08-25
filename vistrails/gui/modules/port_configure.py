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
from PyQt4 import QtCore, QtGui
from core.utils import any
import gui.modules.resources.colorconfig_rc

class StandardPortConfigureContainer(QtGui.QDialog):

    def __init__(self, configureWidget, params, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowMinMaxButtonsHint)
        self.setLayout(QtGui.QVBoxLayout(self))
        self.layout().setMargin(0)
        self.layout().setSpacing(0)
        self.layout().addWidget(configureWidget)

class ColorWheel(QtGui.QWidget):
    colorWheelImage = None
    colorWheelPixmap = None

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.palette().setColor(QtGui.QPalette.Window, QtCore.Qt.white)
        self.setAutoFillBackground(True)
        self.dragging = False
        if not self.colorWheelImage:
            self.colorWheelImage = QtGui.QImage(':colorwheel.png')
            self.colorWheelPixmap = QtGui.QPixmap(':colorwheel.png')
        

    def sizeHint(self):
        return QtCore.QSize(256, 256)

    def paintEvent(self, event):
        QtGui.QWidget.paintEvent(self, event)
        # super(ColorWheel, self).paintEvent(event)
        painter = QtGui.QPainter(self)
        painter.drawPixmap(-1, -1,
                           self.width()+1, self.height()+1,
                           ColorWheel.colorWheelPixmap)

    def getColor(self, ex, ey):
        x = int(float(ex)/self.width()*self.colorWheelImage.width())
        y = int(float(ey)/self.height()*self.colorWheelImage.height())
        if x<0 or y<0 or x>=self.colorWheelImage.width() or y>=self.colorWheelImage.height():
            return QtCore.Qt.white
        return self.colorWheelImage.pixel(x,y)

    def mousePressEvent(self, event):
        if event.buttons()&QtCore.Qt.LeftButton:
            color = self.getColor(event.x(), event.y())
            self.emit(QtCore.SIGNAL('colorChanged'), color)
            self.dragging = True

    def mouseMoveEvent(self, event):
        if self.dragging:
            color = self.getColor(event.x(), event.y())
            self.emit(QtCore.SIGNAL('colorChanged'), color)
            self.dragging = True            
    
class ColorIndicator(QtGui.QFrame):

    def __init__(self, parent=None):
        QtGui.QFrame.__init__(self, parent)
        self.setFrameStyle(QtGui.QFrame.Box | QtGui.QFrame.Plain)
        self.palette().setColor(QtGui.QPalette.Window, QtCore.Qt.white)        
        self.setAutoFillBackground(True)

    def setColor(self, color):
        self.palette().setColor(QtGui.QPalette.Window, QtGui.QColor(color[0]*255,
                                                                    color[1]*255,
                                                                    color[2]*255))
        self.repaint()

    def sizeHint(self):
        return QtCore.QSize(24,24)

class ColorConfigurationWidget(QtGui.QWidget):

    def __init__(self, module, portName, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.module = module
        self.portName= portName
        self.setLayout(QtGui.QVBoxLayout(self))
        self.layout().setMargin(0)
        self.layout().setSpacing(0)
        self.colorWheel = ColorWheel(self)
        self.connect(self.colorWheel, QtCore.SIGNAL('colorChanged'), self.colorChanged)
        self.layout().addWidget(self.colorWheel, 1)
        bottomLayout = QtGui.QHBoxLayout()
        bottomLayout.setMargin(10)
        bottomLayout.setSpacing(0)
        self.result = [(1.0, 1.0, 1.0)]
        self.colorIndicator = ColorIndicator(self)
        self.colorIndicator.setColor(self.result[0])
        bottomLayout.addWidget(self.colorIndicator, 0)
        bottomLayout.addWidget(QtGui.QWidget(), 1)
        self.layout().addLayout(bottomLayout, 0)
    
    def colorChanged(self, color):
        qcolor = QtGui.QColor(color)
        self.result[0] = (qcolor.redF(), qcolor.greenF(), qcolor.blueF())
        self.colorIndicator.setColor(self.result[0])

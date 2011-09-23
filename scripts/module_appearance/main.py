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

#!/usr/bin/env python
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
##############################################################################
# create_module_appearance.py helps VisTrails package developers customize
# the appearance of modules in their packages.

from PyQt4 import QtGui, QtCore, Qt
from module_appearance import Ui_MainWindow
import sys

default_pen = QtGui.QPen()
default_pen.setWidth(2)
default_pen.setColor(QtCore.Qt.black)

selected_pen = QtGui.QPen()
selected_pen.setWidth(3)
selected_pen.setColor(QtCore.Qt.yellow)

##############################################################################

class ModuleFringeJoint(QtGui.QGraphicsEllipseItem):
    
    brush = QtGui.QBrush(QtGui.QColor(192, 192, 192))
    def __init__(self, leftLine, rightLine):
        pt = rightLine.line().p1()
        sz = 5
        QtGui.QGraphicsEllipseItem.__init__(self, -sz/2, -sz/2, sz, sz)
        self.setPos(pt)
        self.leftLine = leftLine
        self.rightLine = rightLine
        self.setAcceptHoverEvents(True)
        self.setPen(default_pen)
        self.setBrush(self.brush)
        self.setZValue(1.0)
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsFocusable, True)
        
    def removeSelf(self):
        scene = self.scene()
        scene.removeItem(self)
        scene.removeItem(self.rightLine)
        self.leftLine.rightJoint = self.rightLine.rightJoint
        self.leftLine.moveRightPoint(self.rightLine.line().p2())
        if self.rightLine.rightJoint is not None:
            self.rightLine.rightJoint.leftLine = self.leftLine
        
    def mouseMoveEvent(self, event):
        QtGui.QGraphicsItem.mouseMoveEvent(self, event)
        self.leftLine.moveRightPoint(self.scenePos())
        self.rightLine.moveLeftPoint(self.scenePos())
        app.window.update_text_view()

    def keyPressEvent(self, event):
        if event.matches(QtGui.QKeySequence.Delete):
            self.removeSelf()

    def hoverEnterEvent(self, event):
        self.setPen(selected_pen)
        self.setFocus(QtCore.Qt.OtherFocusReason)

    def hoverLeaveEvent(self, event):
        self.setPen(default_pen)
        self.clearFocus()

    @staticmethod
    def toScene(pt, side):
        if side == 'left':
            raise Exception("unimplemented")
        elif side == 'right':
            return QtCore.QPointF(pt[0] * 80.0 + 100.0, pt[1] * 80.0 - 40.0)
        else:
            raise Exception("side must be either 'right' or 'left'")
        
    def toVisTrails(self, side):
        px, py = self.scenePos().x(), self.scenePos().y()
        if side == 'left':
            return ((100.0+px)/80.0, (40.0-py)/80.0)
        elif side == 'right':
            return ((px-100.0)/80.0, (40.0-py)/80.0)
        else:
            raise Exception("side must be either 'right' or 'left'")

class ModuleFringeLine(QtGui.QGraphicsLineItem):

    def __init__(self, leftJoint, rightJoint, *args, **kwargs):
        QtGui.QGraphicsLineItem.__init__(self, *args, **kwargs)
        self.setAcceptHoverEvents(True)
        self.setPen(default_pen)
        self.setAcceptedMouseButtons(QtCore.Qt.LeftButton)
        self.leftJoint = leftJoint
        self.rightJoint = rightJoint
        self.setZValue(0.0)

    def mouseDoubleClickEvent(self, event):
        self.createNewLine(event.pos())
        app.window.update_text_view()

    def hoverEnterEvent(self, event):
        self.setPen(selected_pen)

    def hoverLeaveEvent(self, event):
        self.setPen(default_pen)

    def moveLeftPoint(self, pt):
        self.setLine(QtCore.QLineF(pt, self.line().p2()))

    def moveRightPoint(self, pt):
        self.setLine(QtCore.QLineF(self.line().p1(), pt))

    def createNewLine(self, pt):
        old_line = self.line()
        self.setLine(QtCore.QLineF(old_line.p1(), pt))
        new_line = QtCore.QLineF(pt, old_line.p2())
        
        old_joint = self.rightJoint

        new_fringe_line = ModuleFringeLine(None, self.rightJoint, new_line)
        new_joint = ModuleFringeJoint(self, new_fringe_line)

        self.rightJoint = new_joint
        new_fringe_line.leftJoint = new_joint
        if old_joint is not None:
            old_joint.leftLine = new_fringe_line
        
        scene = self.scene()
        scene.addItem(new_fringe_line)
        scene.addItem(new_joint)
        return new_fringe_line

##############################################################################

class MainWindow(QtGui.QMainWindow):

    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.gv = self.ui.graphicsView
        self.setup_graphics_view()
        self.connect(self.ui.pushButton_Quit,
                     QtCore.SIGNAL("clicked()"),
                     QtGui.qApp.quit)
        self.connect(self.ui.pushButton_symmetric,
                     QtCore.SIGNAL("clicked()"),
                     self.make_symmetric)
        self.connect(self.ui.pushButton_mirrored,
                     QtCore.SIGNAL("clicked()"),
                     self.make_mirrored)
        self.connect(self.ui.pushButton_Clear,
                     QtCore.SIGNAL("clicked()"),
                     self.clear_points)

    def setup_graphics_view(self):
        self.scene = QtGui.QGraphicsScene()
        self.gv.setScene(self.scene)
        self.gv.setBackgroundBrush(QtCore.Qt.gray)
        pen = QtGui.QPen()
        pen.setWidth(2)
        pen.setColor(QtCore.Qt.black)

        self.scene.addLine(-100,-40,100,-40,pen)
        self.scene.addLine(-100, 40,100, 40,pen)

        # l1 is the left line
        self.l1 = ModuleFringeLine(None, None, -100,  40, -100, -40)

        # l2 is the right line
        self.l2 = ModuleFringeLine(None, None,  100, -40,  100,  40)
        
        self.scene.addItem(self.l1)
        self.scene.addItem(self.l2)

        self.update_text_view()

    @staticmethod
    def get_points(line, side):
        lst = []
        while not (line.rightJoint is None):
            lst.append(line.rightJoint.toVisTrails(side))
            line = line.rightJoint.rightLine
        return lst
    
    def update_text_view(self):
        s = ''
        left_list = self.get_points(self.l1, 'left')
        right_list = self.get_points(self.l2, 'right')
        
        for (preamble, postamble,
             side, pts) in zip(['reg.add_module(your_class,\n               moduleLeftFringe=[(0.0, 0.0), ',
                                '               moduleRightFringe=[(0.0, 0.0), '],
                               ['(0.0, 1.0)],\n', '(0.0, 1.0)])\n'],
                               ['left', 'right'],
                               [left_list, reversed(right_list)]):
            f = pts
            s += preamble
            for p in pts:
                s += ('(%.4f, %.4f), ' % p)
            s += postamble
        self.ui.textEdit.clear()
        self.ui.textEdit.append(s)

    ##########################################################################
    # slots

    def make_symmetric(self):
        while not (self.l2.rightJoint is None):
            self.l2.rightJoint.removeSelf()
        l1 = self.l1
        l2 = self.l2
        while not (l1.rightJoint is None):
            t = l1.rightJoint.toVisTrails('left')
            t = (-t[0], t[1])
            p = ModuleFringeJoint.toScene(t, 'right')
            l2 = l2.createNewLine(p)
            l1 = l1.rightJoint.rightLine
        self.update_text_view()

    def make_mirrored(self):
        while not (self.l2.rightJoint is None):
            self.l2.rightJoint.removeSelf()
        l1 = self.l1
        pl = []
        while not (l1.rightJoint is None):
            p = l1.rightJoint.scenePos()
            pl.append(QtCore.QPointF(-p.x(), p.y()))
            l1 = l1.rightJoint.rightLine
        l2 = self.l2
        for p in reversed(pl):
            l2 = l2.createNewLine(p)
        self.update_text_view()

    def clear_points(self):
        while not (self.l2.rightJoint is None):
            self.l2.rightJoint.removeSelf()
        while not (self.l1.rightJoint is None):
            self.l1.rightJoint.removeSelf()
        self.update_text_view()

##############################################################################

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    app.window = MainWindow()
    app.window.show()
    app.exec_()


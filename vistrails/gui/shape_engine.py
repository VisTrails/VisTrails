#!/usr/bin/env python

# Qt opengl widget that controls a 2D shape rendering engine

from PyQt4 import QtCore, QtGui, QtOpenGL
from core.debug import notify, DebugPrint, timecall
from core.vistrail.connection import Connection
from core.vistrail.port import PortEndPoint
from core.utils.color import PresetColor
from gui.intersect import Intersect
from gui.shape import *
import bisect
import gui.shape
import math
import pickle
import sys
import copy

try:
    from OpenGL.GL import *
    from OpenGL.GLU import *
except ImportError:
    app = QtGui.QApplication(sys.argv)
    QtGui.QMessageBox.critical(None, "OpenGL",
                               "PyOpenGL must be installed to run this.",
                               QtGui.QMessageBox.Ok | QtGui.QMessageBox.Default,
                               QtGui.QMessageBox.NoButton)
    sys.exit(1)

class GLWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        format = QtOpenGL.QGLFormat()
        format.setDoubleBuffer(1)
        format.setRgba(1)
        QtOpenGL.QGLWidget.__init__(self, format, parent)
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
	self.setAttribute(QtCore.Qt.WA_NoSystemBackground)
        self.shapes = {}
        self.connectionShapesUnder = []
        self.connectionShapesOver = []
        self.portConnections = {}
        self.endPortDrag = Point(0,0)
        self.endPortSnap = Point(0,0)
        self.draggingPortConnection = False
        self.startDraggingPortConnection = False
        self.draggingPortConnectionEnabled = True
        self.panX = 0
        self.panY = 0
        self.panZ = 1
        self.width = 0
        self.height = 0
        self.lastPos = Point(0,0)
        self.currentMoves = {}
        self.moveable = True
        self.currentShape = None
        self.bgColor = PresetColor.PAINT_BACKGROUND
        self.font = QtGui.QFont("Arial", 24, QtGui.QFont.Bold)
        self.scale = 4.0
        self.setMouseTracking(True)
        self.lineWidth = 0.05
        self.dragPixmap = QtGui.QPixmap("./images/dragging.png")
        self.startDrag = None
        self.firstMouseStatus = QtCore.Qt.MouseButton()
        self.controller = None
        self.setAcceptDrops(True)
        self.bgTexture = None
        self.selectedShapes = []  #for multiple shapes manipulation
        self.selectionBox = Rectangle()
        c = PresetColor.SELECTION_BOX
        self.selectionBox.color=[c[0],c[1],c[2],0.30] #blending
        self.selectionBox.outlineColor = PresetColor.SELECTION_BOX_BORDER
        self.selectionBox.outline = True
        self.selectionBox.outlineWidth=2.0
        self.beginDragPosition = Point()
        self.keepSelecting = False

    def __del__(self):
        pass

    def initializeGL(self):
        glShadeModel(GL_SMOOTH)
        glDrawBuffer(GL_BACK)
        glReadBuffer(GL_BACK)

    def paintGL(self):
        if (not self.isVisible()):
            return
        self.makeCurrent()
        glClearColor(self.bgColor[0], self.bgColor[1], 
                     self.bgColor[2], 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glScalef(self.panZ, self.panZ, self.panZ);
        gluLookAt(self.panX, self.panY, self.panZ, self.panX, self.panY, 0, 0, 1, 0)
        if self.bgTexture:
            self.drawTexturedBackground()
        self.drawShapes()
        glFinish()

    def resizeGL(self, width, height):
        glViewport(0,0,width,height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        h = 1.0
        if (height != 0):
            w = (float(width)/float(height))
        else:
            w = 1.0
        glOrtho(-w,w,-h,h, -100.0, 100.0);
        self.width = width
        self.height = height

    def event(self, event):
        if (event.type() == QtCore.QEvent.ToolTip):
            shape = self.pick(Point(event.pos().x(), self.height-event.pos().y()))
            if shape and shape.hasToolTip():
                QtGui.QToolTip.showText(event.globalPos(), shape.toolTip())
            self.updateGL()
        if (event.type() == QtCore.QEvent.MouseButtonDblClick):
            shape = self.pick(Point(event.pos().x(), self.height-event.pos().y()))
            self.emit(QtCore.SIGNAL('doubleClick'), shape)
        return QtOpenGL.QGLWidget.event(self, event)

    def mousePressEvent(self, event):
        st = event.buttons()
        b = event.modifiers()
        if st == QtCore.Qt.LeftButton and (b & QtCore.Qt.ShiftModifier):
            st = QtCore.Qt.MidButton
        elif st == QtCore.Qt.LeftButton and (b & QtCore.Qt.MetaModifier):
            st = QtCore.Qt.RightButton
        multiPick = b==QtCore.Qt.ControlModifier
        self.firstMouseStatus = st
        if st & QtCore.Qt.LeftButton:
            self.makeCurrent()
            self.lastPos = self.screenToWorld(Point(event.pos().x(),
                                                    self.height-event.pos().y()))
            self.pickShape(Point(event.pos().x(), self.height-event.pos().y()))
            if multiPick:
		#if self.currentShape not in self.selectedShapes:
		    #self.selectedShapes.append(self.currentShape)
                self.emit(QtCore.SIGNAL("ctrlClick()"))
            elif self.controller and self.currentShape:
                self.startDrag = Point(event.pos().x(),self.height-event.pos().y())
            if not multiPick: 
                self.keepSelecting=False
            self.beginDragPosition = self.screenToWorld(Point(event.pos().x(),
                                                              self.height-event.pos().y()))
        if (st & QtCore.Qt.RightButton) and (b & QtCore.Qt.ControlModifier):
            self.emit(QtCore.SIGNAL("rightClick"), event)

        elif st & QtCore.Qt.RightButton:
	    self.makeCurrent()
	    self.pickShape(Point(event.pos().x(), self.height-event.pos().y()))
            glPushMatrix()
            glLoadIdentity()
            self.lastPos = self.screenToWorld(Point(event.pos().x(),
                                                    self.height-event.pos().y()))
	    glPopMatrix()
	elif st & QtCore.Qt.MidButton:
            self.makeCurrent()
            glPushMatrix()
            glLoadIdentity()
            self.lastPos = self.screenToWorld(Point(event.pos().x(),
                                                    self.height-event.pos().y()))
	    glPopMatrix()
	
        if not multiPick and (not self.currentShape or 
			      (self.currentShape not in self.selectedShapes)):
            for sh in self.selectedShapes:
                sh.setSelected(False)
            self.selectedShapes = []
	    if self.currentShape:
		self.selectedShapes.append(self.currentShape)
        for sh in self.selectedShapes:
            sh.setSelected(True)
        self.updateGL()

    def mouseMoveEvent(self, event):
        st = event.buttons()
        b = event.modifiers()
        if st == QtCore.Qt.LeftButton and (b & QtCore.Qt.ShiftModifier):
            st = QtCore.Qt.MidButton
        elif st == QtCore.Qt.LeftButton and (b & QtCore.Qt.MetaModifier):
            st = QtCore.Qt.RightButton

        curPos = self.lastPos
        self.hover(Point(event.pos().x(), self.height-event.pos().y()))
        if (st & QtCore.Qt.LeftButton):
            self.makeCurrent()
            curPos = self.screenToWorld(Point(event.pos().x(), 
                                         self.height-event.pos().y()))
        elif (st & QtCore.Qt.MidButton or
              st & QtCore.Qt.RightButton):
            self.makeCurrent()
            glPushMatrix()
            glLoadIdentity()
            curPos = self.screenToWorld(Point(event.pos().x(),
                                         self.height-event.pos().y()))
            glPopMatrix()

        dx = curPos.x - self.lastPos.x
        dy = curPos.y - self.lastPos.y
  
        if (st & QtCore.Qt.LeftButton):
            if (self.firstMouseStatus and
                (self.firstMouseStatus & QtCore.Qt.LeftButton)):
                self.keepSelecting = (b & QtCore.Qt.ControlModifier)
		self.move(dx,dy)

        elif (st & QtCore.Qt.MidButton):
            self.panX -= dx/self.panZ
            self.panY -= dy/self.panZ
        elif (st & QtCore.Qt.RightButton):
            self.panZ *= 1.0 - (dy/2.0)
            if (self.panZ < 1e-10):
                self.panZ = 1e-10
                
        self.updateGL()

        if self.startDrag:
            self.makeCurrent()
            cp = self.worldToScreen(curPos)
            dist = abs(self.startDrag.x-cp.x) + abs(self.startDrag.y-cp.y)
            if dist>4:
                if self.controller and self.currentShape:
                    controllerName = self.controller.name
                    drag = QtGui.QDrag(self)
                    mimeData = QtCore.QMimeData()
                    mimeData.setText("VisTrailsVersion")
                    mimeData.setData("ControllerName", QtCore.QByteArray(controllerName))
                    drag.setMimeData(mimeData)
                    drag.setPixmap(self.dragPixmap)
                    drag.setHotSpot(QtCore.QPoint(self.dragPixmap.width()/2,self.dragPixmap.height()/2))
                    dropAction = drag.start(QtCore.Qt.ActionMask)
                self.startDrag = None

        if self.startDraggingPortConnection:            
            cp = curPos
            dist = abs(self.endPortDrag.x-cp.x) + abs(self.endPortDrag.y-cp.y)
            if dist>4:
                self.draggingPortConnection = True
                self.startDraggingPortConnection = False
        self.lastPos = curPos

    def mouseReleaseEvent(self, event):
	st = event.button()
        b = event.modifiers()
        if st == QtCore.Qt.LeftButton and (b & QtCore.Qt.ShiftModifier):
            st = QtCore.Qt.MidButton
        elif st == QtCore.Qt.LeftButton and (b & QtCore.Qt.MetaModifier):
            st = QtCore.Qt.RightButton

        self.selectionBox.width=self.selectionBox.height=0.0
	
        if self.currentShape:
            if self.draggingPortConnection:
                self.draggingPortConnection = False
                self.makeConnection()
            elif isinstance(self.currentShape, ModuleShape):
		if st & QtCore.Qt.LeftButton and not b & QtCore.Qt.ControlModifier:
		    if len(self.currentMoves) > 0:
			import copy
			dict = copy.deepcopy(self.currentMoves)
			self.emit(QtCore.SIGNAL("shapesMove"),dict)
			self.currentMoves = {}
		    else:
			for sh in self.selectedShapes:
			    sh.setSelected(False)
			self.selectedShapes = []
			self.selectedShapes.append(self.currentShape)
			self.currentShape.setSelected(True)
		if st & QtCore.Qt.RightButton:
		    self.emit(QtCore.SIGNAL("rightClick"), event)
	#turn the last selected shape the current shape
	if not self.currentShape and st & QtCore.Qt.LeftButton:
	    if len(self.selectedShapes) > 0:
		self.currentShape = self.selectedShapes[-1]

        self.startDrag = None
        self.startDraggingPortConnection = False
        self.firstMouseStatus = event.buttons()
        self.updateGL()
	if len(self.selectedShapes) > 0:
	    self.emit(QtCore.SIGNAL("shapesSelected"),True)

	else:
	    self.emit(QtCore.SIGNAL("shapesSelected"),False)

    def mouseDoubleClickEvent(self, event):
        #print self
        #print self.controller
        #self.controller.vistrail.setExp(self.pickedShapes)
        self.emit(QtCore.SIGNAL("doubleClick(QEvent)"), event) #caught in version_tree
        self.updateGL()
        
    def keyPressEvent(self, event):
        if (event.key() == QtCore.Qt.Key_Delete or event.key() == QtCore.Qt.Key_Backspace):
            self.makeCurrent()
            self.deleteShape()
            self.updateGL()
        if event.key()==QtCore.Qt.Key_Control:
            if self.currentShape and not isinstance(self.currentShape, ModuleShape) and self.selectedShapes==[]:
                if self.controller.vistrail.getTerseGraph().vertices.has_key(self.currentShape.id):
                    self.selectedShapes.append(self.currentShape)
                else:
                    self.currentShape.setSelected(False)
		    
        else:
            event.ignore()

    def dragEnterEvent(self, event):
        mimeData = event.mimeData()
        if (mimeData and mimeData.text()=='VisTrailsVersion') or (event.source() != self):
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        mimeData = event.mimeData()
        if mimeData and mimeData.text()=='VisTrailsVersion':
            vshape = self.pick(Point(event.pos().x(), self.height - event.pos().y()))
            if vshape and self.controller.vistrail.hasVersion(vshape.id):
                event.accept()
            else:
                event.ignore()
            self.updateGL()

    def dropEvent(self, event):
        data = event.mimeData()
        if data:
            text = data.text()
            if text=='VisTrailsVersion': # Visual Diff
                vshape = self.pick(Point(event.pos().x(), self.height - event.pos().y()))
                if vshape and self.controller.vistrail.hasVersion(vshape.id):
                    event.accept()
                    self.showVisualDiff(self.controller.currentVersion, vshape.id) 
                self.updateGL()
            else:
                try:
                    obj = pickle.loads(str(text))
                    dropType = obj[0]
                    moduleName = obj[1]
                except:
                    return                
                if dropType != "Module":
                    if dropType=="Method":
                        try:
                            obj = pickle.loads(str(text))
                            vtkclass = obj[3]
                            vtkmethod = obj[2]
                        except:
                            return
                        p = self.pick(Point(event.pos().x(), self.height-event.pos().y()))
                        if p and p.text.text==vtkclass:                            
                            p.setPortVisible(vtkmethod, True)
                            self.pipelineView.setPipeline(self.pipelineView.controller.currentPipeline)
                    return
                self.makeCurrent()
                pos = self.screenToWorld(Point(event.pos().x(), self.height-event.pos().y()))
                self.emit(QtCore.SIGNAL("moduleToBeAdded"), moduleName, pos.x, pos.y)
        QtOpenGL.QGLWidget.dropEvent(self, event)

    def hover(self, p):
        shape = self.pick(p)
        if shape:
            self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        else:
            self.setCursor(QtGui.QCursor())

    def drawShapes(self):
        gui.shape.current_context = self
        lw = self.lineWidth * self.height*self.panZ*0.2

        for c in self.connectionShapesUnder:
            c.draw(lw)

        # Temporarily using the next line to work around the bug for
        # rendering textoverlay where clicking on the spreadsheet can
        # blackout the first module in the pipeline view.        
        # If comment the text drawing line, i.e. self.drawText(s), all
        # modules will be blackened out, not only the first module.
	# if self.shapes: self.drawText(self.shapes[0])

        for s in self.shapes.itervalues():
            s.draw(lw*2)
            self.drawText(s)

        for c in self.connectionShapesOver:
            c.draw(lw*2)

        if (self.currentShape and self.draggingPortConnection):
            p1 = Point(self.currentShape.x,self.currentShape.y)
            p2 = self.endPortSnap
            l = PolyLine(p1,p2, False, False)
            l.draw(lw*2)

        if self.shapes.has_key(0) and not self.selectionBox.width==0:
            self.selectionBox.draw(0.50)

    __fonts = []
    def setApproxFont(self, ps):
        if not len(self.__fonts):
            print "Building fonts"
            for i in range(2,120):
                f = QtGui.QFont("Arial", 24, QtGui.QFont.Bold)
                f.setPixelSize(i)
                self.__fonts.append((i, f, QtGui.QFontMetrics(f)))
            i = 120
            while i < 1500:
                f = QtGui.QFont("Arial", 24, QtGui.QFont.Bold)
                f.setPixelSize(i)
                self.__fonts.append((i, f, QtGui.QFontMetrics(f)))
                i *= 1.5
        ix = bisect.bisect(self.__fonts, (ps, None))
        if ix > 0:
            ix -= 1
        self.font = self.__fonts[ix][1]
        return self.__fonts[ix][2]
        
    def drawText(self, s):
        ps = s.height*self.height*self.panZ*0.18
        if ps > 1:
            t = s.text
            if t.text:
                fm = self.setApproxFont(ps)
                tw = fm.width(t.text)
                p = self.worldToScreen(Point(t.x,t.y-s.height*0.15))
                glColor4fv(t.color)
                self.renderText(p.x-tw/2, self.height-p.y, t.text, self.font, 2000 + int(ps)*256)

    def pickShape(self, p):
        if (self.currentShape):
            if self.currentShape not in self.selectedShapes:
                self.currentShape.setSelected(False)
        self.currentShape = self.pick(p)
        if self.currentShape:
	    #if self.currentShape.id != -1 and isinstance(self.currentShape,ModuleShape):
                #self.currentMoves[self.currentShape.id] = Point(0,0)
            self.currentShape.setSelected(True)
            if isinstance(self.currentShape, PortShape) and self.draggingPortConnectionEnabled:
                self.startDraggingPortConnection = True
                self.endPortDrag = Point(self.lastPos.x, self.lastPos.y)
                self.endPortSnap = self.endPortDrag
            if (isinstance(self.currentShape, VersionShape) or
                isinstance(self.currentShape, ModuleShape)):
                self.emit(QtCore.SIGNAL('shapeSelected(int)'),
                          self.currentShape.id)
            elif isinstance(self.currentShape,PolyLine):
                self.emit(QtCore.SIGNAL('polyLineSelected(int)'),
                          self.currentShape.id)
            else:
                self.emit(QtCore.SIGNAL('shapeUnselected()'))
        else:
            self.emit(QtCore.SIGNAL('shapeUnselected()'))

    def pick(self, p):
	self.makeCurrent()
        picker = ColorPicker()
        for c in self.connectionShapesUnder:
            c.drawSelect(picker)
        for c in self.connectionShapesOver:
            c.drawSelect(picker) 
        for s in self.shapes.itervalues():
            s.drawSelect(picker)
        return picker.getPicked(p)
    
    def move(self, dx, dy):
	
        if not self.currentShape:
            if not self.keepSelecting:
                for s in self.selectedShapes:
                    s.setSelected(False)
                self.selectedShapes=[]
            
            self.selectionBox.width+=dx
            self.selectionBox.height+=dy
            self.selectionBox.x = self.beginDragPosition.x + (self.selectionBox.width/2)
            self.selectionBox.y = self.beginDragPosition.y + (self.selectionBox.height/2)
            i=Intersect()

            for s in self.shapes.keys():
                if i.intersect(self.shapes[s],self.selectionBox):
                    if self.shapes[s] not in self.selectedShapes:
                        self.selectedShapes.append(self.shapes[s])
            for s in self.selectedShapes:
                s.setSelected(True)
            return
            
        if self.moveable:
            if self.draggingPortConnection:
                self.endPortDrag.x = self.lastPos.x + dx
                self.endPortDrag.y = self.lastPos.y + dy
                self.endPortSnap = self.endPortDrag
                self.moveConnection()
            elif isinstance(self.currentShape, ModuleShape):
		for s in self.selectedShapes:
		    if isinstance(s, ModuleShape):
			s.move(dx,dy)
			if not self.currentMoves.has_key(s.id):
			    self.currentMoves[s.id] = Point(0,0)
			self.currentMoves[s.id].x += dx
			self.currentMoves[s.id].y += dy
        self.updatePortShapes()
            
    def screenToWorld(self, p):
        vp = glGetIntegerv(GL_VIEWPORT)
        mvmatrix = glGetDoublev(GL_MODELVIEW_MATRIX)
        pmatrix = glGetDoublev(GL_PROJECTION_MATRIX)
        result = gluUnProject(p.x, p.y, 0.0, mvmatrix, pmatrix, vp)
        if not result:
            return Point(0, 0)
        else:
            return Point(result[0], result[1])

    def worldToScreen(self, p):
        vp = glGetIntegerv(GL_VIEWPORT)
        mvmatrix = glGetDoublev(GL_MODELVIEW_MATRIX)
        pmatrix = glGetDoublev(GL_PROJECTION_MATRIX)
        result = gluProject(p.x, p.y, 0.0, mvmatrix, pmatrix, vp)
        return Point(result[0], result[1])

    def addVersionShape(self, id, n, p, w, h, sat, user, matched):
        if matched:
            if user == self.controller.vistrail.getUser():
                c = PresetColor.VERSION_TREE
            else:
                c = PresetColor.OTHER_USER_VT
            qc = QtGui.QColor(c[0]*255, c[1]*255, c[2]*255)
            hsv = qc.getHsv()
            qc.setHsv(hsv[0], hsv[1]*sat, hsv[2] + (255-hsv[2])*(1.0-sat))
            col = qc.getRgb()
            finalColor = [float(col[0])/255.0, float(col[1])/255.0, float(col[2])/255.0]
            vs = VersionShape(id, n, p.x, p.y, w, h, finalColor)
        else:
            finalColor = PresetColor.GHOSTED_VERSION
            outlineColor = PresetColor.GHOSTED_VERSION_OUTLINE
            vs = VersionShape(id, n, p.x, p.y, w, h, finalColor, outlineColor, False)
        self.shapes[id] = vs

    def addModuleShape(self, m, mColor = None, matched = True):
        if mColor:
            color = mColor
            outlineColor = PresetColor.OUTLINE
        else:
            if matched:
                if (m.type == VistrailModuleType.Filter): 
                    color = PresetColor.FILTER
                else:
                    color = PresetColor.OBJECT
                outlineColor = PresetColor.OUTLINE
            else:
                color = PresetColor.GHOSTED_MODULE
                outlineColor = PresetColor.GHOSTED_MODULE_OUTLINE
        if len(color)<4: color += [1.0]*(4-len(color))
        h = 24*3
        w = len(m.name)*18
        ms = ModuleShape(m.id, m.sourcePorts(), m.destinationPorts(), m.name, 
                         m.center.x, m.center.y, w, h, color, outlineColor, matched, m)
        self.shapes[m.id] = ms
        return ms

    def deleteShape(self):
        """ It deletes all shapes in self.selectedShapes"""
        mList=[]
        cList=[]

        if self.currentShape:
            if isinstance(self.currentShape, ModuleShape):
                mList.append(self.currentShape.id)
            elif isinstance(self.currentShape, PolyLine):
                cList.append(self.currentShape.id)
                
        for s in self.selectedShapes:
            if isinstance(s, ModuleShape) and (s.id not in mList):
                mList.append(s.id)
            elif isinstance(s, PolyLine) and (s.id not in cList):
                cList.append(s.id)

        if len(mList) > 0:
            self.emit(QtCore.SIGNAL("modulesToBeDeleted"), 
                          mList)
        if len(cList) > 0:
            self.emit(QtCore.SIGNAL("connectionsToBeDeleted"), 
                          cList)
        # if self.selectedShape:
#             if isinstance(self.selectedShape, ModuleShape):
#                 self.emit(QtCore.SIGNAL("moduleToBeDeleted(int)"), 
#                           self.selectedShape.id)
#             elif isinstance(self.selectedShape, PolyLine):
#                 self.emit(QtCore.SIGNAL("connectionToBeDeleted(int)"), 
#                           self.selectedShape.id)   

    def makeConnection(self):
        self.makeCurrent()
        end = self.worldToScreen(Point(self.endPortDrag.x, self.endPortDrag.y))
        endShape = self.pick(end)
        if endShape != self.currentShape:
            if isinstance(endShape, ModuleShape) or isinstance(endShape, PortShape):
                sourcePort = None
                destPort = None
                sourceModule = None
                destModule = None
                endModule = endShape
                if isinstance(endShape, PortShape):
                    endModule = self.shapes[endShape.parentId]
                if (self.currentShape.port.endPoint == PortEndPoint.Destination):
                    sourcePort = endModule.getSourcePort(self.endPortDrag,
                                                     self.currentShape.port)
                    destPort = self.currentShape.port      
                    sourceModule = endModule
                    destModule = self.shapes[self.currentShape.parentId]
                else:
                    sourcePort = self.currentShape.port
                    destPort = endModule.getDestPort(self.endPortDrag,
                                                 self.currentShape.port)
                    sourceModule = self.shapes[self.currentShape.parentId]
                    destModule = endModule
                if sourcePort and destPort and sourceModule != destModule:
                    conn = Connection.fromPorts(sourcePort, destPort)
                    conn.sourceId = sourceModule.id
                    conn.destinationId = destModule.id
                    #print sourcePort
                    #print destPort
                    self.emit(QtCore.SIGNAL("connectionToBeAdded"), conn)

    def moveConnection(self):
        self.makeCurrent()
        end = self.worldToScreen(Point(self.endPortDrag.x, self.endPortDrag.y))
        endShape = self.pick(end)
        if endShape != self.currentShape:
            if isinstance(endShape, ModuleShape) or isinstance(endShape, PortShape):
                port = None
                endModule = endShape
                if isinstance(endShape, PortShape):
                    endModule = self.shapes[endShape.parentId]
                if endModule == self.shapes[self.currentShape.parentId]:
                    return
                if (self.currentShape.port.endPoint == PortEndPoint.Destination):
                    port = endModule.getSourcePort(self.endPortDrag,
                                               self.currentShape.port)
                    if port:
                        self.endPortSnap = endModule.getSourcePortPosition(port)
                else:
                    port = endModule.getDestPort(self.endPortDrag,
                                             self.currentShape.port)
                    if port:
                        self.endPortSnap = endModule.getDestPortPosition(port)
            
    def addConnection(self, id1, id2, annotated, ghosted = False):
        if ghosted:
            color = copy.copy([0.7, 0.7, 0.7, 1.0])
        else:
            color = copy.copy([0.0, 0.0, 0.0, 1.0])
        l = PolyLine(Point(self.shapes[id1].x,
                           self.shapes[id1].y),
                     Point(self.shapes[id2].x,
                           self.shapes[id2].y), annotated, False, color)
        self.connectionShapesUnder.append(l)

    def setPortConnections(self, con):
        self.portConnections = con
        self.updatePortShapes()

    def updatePortShapes(self):
        OCS = {}
        for l in self.connectionShapesOver: OCS[l.id] = l.color
        self.connectionShapesOver = []
        for (i,c) in self.portConnections.items():
            sourceModule = self.shapes[c.sourceId]
            destModule = self.shapes[c.destinationId]
            sp = sourceModule.getSourcePortPosition(c.source)
            dp = destModule.getDestPortPosition(c.destination)
            if not (sourceModule.matched and destModule.matched):
                color = [0.35, 0.35, 0.35, 1.0]
            else:
                color = [0, 0, 0, 1.0]
            l = PolyLine(sp,dp, False, True, color)
            l.id = i
            if l.id in OCS: l.color = OCS[l.id]
            self.connectionShapesOver.append(l)

    def clearShapes(self):
        self.shapes = {}
        self.connectionShapesUnder = [] 
        self.connectionShapesOver = []  
        self.portConnections = {}

    def selectShapes(self, l):
	""" selectShapes(l) -> None
	Set all shapes in l to selected and put them in self.selectedShapes """
	for s in self.selectedShapes:
	    s.setSelected(False)
	self.selectedShapes = []
	for id in l:
	    self.shapes[id].setSelected(True)
	    self.selectedShapes.append(self.shapes[id])

    def setupBackgroundTexture(self, imagePath):
        if not imagePath:
            return
        self.makeCurrent()
        image = QtGui.QImage(imagePath)
        self.bgTexture = self.bindTexture(image)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

    def drawTexturedBackground(self):        
        glEnable(GL_TEXTURE_2D)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
        glBindTexture(GL_TEXTURE_2D, self.bgTexture)
        ll = self.screenToWorld(Point(0,0))
        ur = self.screenToWorld(Point(self.width, self.height))
        tll = ll*(2.0/self.scale)
        tur = ur*(2.0/self.scale)
        glBegin(GL_QUADS)
        glTexCoord2f(tll.x, tll.y)
        glVertex2f(ll.x, ll.y)
        glTexCoord2f(tll.x, tur.y)
        glVertex2f(ll.x, ur.y)
        glTexCoord2f(tur.x, tur.y)
        glVertex2f(ur.x, ur.y)
        glTexCoord2f(tur.x, tll.y)
        glVertex2f(ur.x, ll.y)
        glEnd()
        glDisable(GL_TEXTURE_2D)

    def showVisualDiff(self, v1, v2):
        from  vis_diff import VisualDiff
        if (v1 == 0 or v2 == 0):
            return
        if (v1 == v2):
            return
        vis = VisualDiff(self.controller.vistrail, v1, v2)
        vis.show()
        vis.activateWindow()
        vis.setFocus()

    def zoomToFit(self, padding=0.2):
        minX = 1.0e20
        minY = 1.0e20
        maxX = -1.0e20
        maxY = -1.0e20
        for (idx,sh) in self.shapes.items():
            s1 = Point(sh.x-sh.width/2,sh.y-sh.height/2)
            s2 = Point(sh.x+sh.width/2,sh.y+sh.height/2)
            if s1.x<minX: minX = s1.x
            if s1.y<minY: minY = s1.y
            if s2.x>maxX: maxX = s2.x
            if s2.y>maxY: maxY = s2.y
        w = maxX-minX
        h = maxY-minY
        scale = max(w,h)/2 * (1.0 + padding)
        self.panX = (maxX+minX)/2
        self.panY = (maxY+minY)/2
        self.panZ = 1.0/scale
        self.scale = scale
        return float(w/h)
    
    
def isInPath(parent, bottom, top):
    """tells whether bottom is a descendent of top
       (useful for the expansion of multiple selected shapes)
    """
    curr=bottom
    while curr>top:
        if parent[curr]==top:
            return True
        curr=parent[curr]
    return False

class ColorPicker(object):
    def __init__(self):
        self.colorDict = {}
        self.id = 0
        glDrawBuffer(GL_BACK)
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClear(GL_COLOR_BUFFER_BIT)

    def setColor(self, obj):
        self.colorDict[self.id] = obj
        self.id+=1
        glColor3ub(self.id & 255, (self.id >> 8)&255, (self.id >> 16)& 255)

    convert = {'array': int,
               'str': ord}
    
    def getPicked(self, p):
        glFlush()
        glReadBuffer(GL_BACK)
        b = glReadPixelsub(int(p.x),int(p.y), 1, 1, GL_RGB)[0][0]
        fun = self.convert[type(b[0]).__name__]
        id = fun(b[0]) + (fun(b[1])<<8) + (fun(b[2])<<16) - 1
        if id == -1 or not self.colorDict.has_key(id):
            return None
        else:
            return self.colorDict[id]

class MainWindow(QtGui.QMainWindow):
    def __init__(self):        
        QtGui.QMainWindow.__init__(self)

        centralWidget = GLWidget()
        self.setCentralWidget(centralWidget)

        self.setWindowTitle(self.tr("Grabber"))
        self.resize(512,512)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())    


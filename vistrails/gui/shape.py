#!/usr/bin/env python

# Opengl shapes

from OpenGL.GL import *
from OpenGL.GLU import *
from core.utils import abstract
from core.utils.color import ColorByName
from core.data_structures import Point
from core.debug import timecall
from core.modules import module_registry
from core.vis_types import *
import math
import sys

WS_LINE_WIDTH = 0.02

current_context = None # So very ugly

class Shape(object):
    __fields__ = ['id','x','y','width','height','color','outline',
                  'outlineColor','selectedColor','outlineWidth',
                  'selected','type']
    def __init__(self):
        self.id = -1
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        self.color = [0.0,0.0,0.0,0.0]
        self.outline = False
        self.outlineColor = [0.0, 0.0, 0.0, 0.0]
        self.selectedColor = ColorByName.get(SELECTED_COLOR)
        self.outlineWidth = 2.0
        self.selected = False
        self.__dlistId = -1

    def toShapeSpace(self):
        glTranslatef(self.x, self.y, 0)

    def displayListDraw(self, lineWidth):
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        self.toShapeSpace()
        glLineWidth(self.outlineWidth*lineWidth)
        glCallList(self.__dlistId)
        glPopMatrix()

    def createDisplayList(self):
        self.__dlistId = glGenLists(1)
        glNewList(self.__dlistId, GL_COMPILE)
        self.realDraw()
        glEndList()
        self.draw = self.displayListDraw

    def clearDisplayList(self):
        if self.__dlistId != -1:
            glDeleteLists(self.__dlistId, 1)

    def updateDisplayList(self):
        self.clearDisplayList()
        self.createDisplayList()

    def __del__(self):
        self.clearDisplayList()

    def draw(self, lineWidth=0):
        abstract()
        
    def drawSelect(self, picker, parent=None):
        abstract()

    def pick(self, p):
        abstract()

    def snap(self, p):
        abstract()
    
    def move(self, dx, dy):
        abstract()

    def setSelected(self, s):
        abstract()

    def hasToolTip(self):
        return False

    def toolTip(self):
        return ""
        
class Rectangle(Shape):
    def __init__(self, x=0,y=0,w=0,h=0):
        Shape.__init__(self)
        self.x = x
        self.y = y
        self.width = w
        self.height = h

    def realDraw(self):
        glEnable(GL_BLEND)
        ll = [-self.width/2,-self.height/2]
        ur = [self.width/2,self.height/2]
        glColor4fv(self.color)
        glBegin(GL_QUADS)
        glVertex2f(ll[0],ll[1])
        glVertex2f(ll[0],ur[1])
        glVertex2f(ur[0],ur[1])
        glVertex2f(ur[0],ll[1])
        glEnd()
        if self.outline:
            if self.selected:
                glColor4fv(self.selectedColor)
            else:
                glColor4fv(self.outlineColor)
            glBegin(GL_LINE_LOOP)
            glVertex2f(ll[0],ll[1])
            glVertex2f(ll[0],ur[1])
            glVertex2f(ur[0],ur[1])
            glVertex2f(ur[0],ll[1])
            glEnd()
        glDisable(GL_BLEND)
    
    def draw(self, lineWidth):
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        self.toShapeSpace()
        glLineWidth(self.outlineWidth*lineWidth)
        self.realDraw()
        glPopMatrix()
        
    def drawSelect(self, picker, parent=None):
        if (parent):
            picker.setColor(parent)
        else:
            picker.setColor(self)
        ll = [self.x-self.width/2,self.y-self.height/2]
        ur = [self.x+self.width/2,self.y+self.height/2]
        glBegin(GL_QUADS)
        glVertex2f(ll[0],ll[1])
        glVertex2f(ll[0],ur[1])
        glVertex2f(ur[0],ur[1])
        glVertex2f(ur[0],ll[1])
        glEnd()

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def pick(self, p):
        pass

    def snap(self):
        pass

    def setSelected(self, s):
        self.selected = s

class ShadowRectangle(Shape):
    def __init__(self, x=0,y=0,w=0,h=0):
        Shape.__init__(self)
        self.x = x
        self.y = y
        self.width = w
        self.height = h
        self.color = [0, 0, 0, 1.0]

    def realDraw(self):
        border = self.height/5
        glPushMatrix()
        glTranslatef(border, -border, 0)
        c1 = [0.0, 0.0, 0.0, 0.8]
        c2 = [0.0, 0.0, 0.0, 0.0]
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glBegin(GL_QUADS)

        #Bottom Polygon
        ll = [-self.width/2, -self.height/2]
        ur = [self.width/2-border, -self.height/2+border]
        glColor4fv(c1)
        glVertex2f(ur[0],ur[1])
        glVertex2f(ll[0],ur[1])
        glColor4fv(c2)
        glVertex2f(ll[0],ll[1])
        glVertex2f(ur[0],ll[1])

        #Right Polygon
        ll = [self.width/2-border, -self.height/2+border]
        ur = [self.width/2, self.height/2]
        glColor4fv(c1)
        glVertex2f(ll[0],ur[1])
        glVertex2f(ll[0],ll[1])
        glColor4fv(c2)
        glVertex2f(ur[0],ll[1])
        glVertex2f(ur[0],ur[1])

        glEnd()

        #BottomLeft Corner
        ur = [-self.width/2, -self.height/2+border]
        glBegin(GL_POLYGON)
        glColor4fv(c1)
        glVertex2f(ur[0],ur[1])
        glColor4fv(c2)
        for i in [180, 210, 240, 270]:
            rads = float(i)*math.pi/180.0
            glVertex2f(ur[0] + math.cos(rads)*border,
                       ur[1] + math.sin(rads)*border)
        glEnd()
        
        #BottomRight Corner
        ul = [self.width/2-border, -self.height/2+border]
        glBegin(GL_POLYGON)
        glColor4fv(c1)
        glVertex2f(ul[0],ul[1])
        glColor4fv(c2)
        for i in [270, 300, 330, 360]:
            rads = float(i)*math.pi/180.0
            glVertex2f(ul[0] + math.cos(rads)*border,
                       ul[1] + math.sin(rads)*border)
        glEnd()

        #UpperRight Corner
        ll = [self.width/2-border, self.height/2]
        glBegin(GL_POLYGON)
        glColor4fv(c1)
        glVertex2f(ll[0],ll[1])
        glColor4fv(c2)
        for i in [0, 30, 60, 90]:
            rads = float(i)*math.pi/180.0
            glVertex2f(ll[0] + math.cos(rads)*border,
                       ll[1] + math.sin(rads)*border)
        glEnd()


        glDisable(GL_BLEND)
        glPopMatrix()

    def draw(self, lineWidth):
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        self.toShapeSpace()
        self.realDraw()
        glPopMatrix()
       
    def drawSelect(self, picker, parent=None):
        pass
        
    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def pick(self, p):
        pass

    def snap(self):
        pass

    def setSelected(self, s):
        self.selected = s


class Ellipse(Shape):
    def __init__(self,x=0,y=0,w=0,h=0):
        Shape.__init__(self)
        self.x = x
        self.y = y
        self.width = w
        self.height = h
        self.fixedLineWidth = True
        self.lineWidth = WS_LINE_WIDTH

    EllipseDL = {}
    def ensureDL(self):
        if not Ellipse.EllipseDL.has_key(id(current_context)):
            Ellipse.EllipseDL[id(current_context)] = glGenLists(1)
            l = Ellipse.EllipseDL[id(current_context)]
            glNewList(l, GL_COMPILE)
            glBegin(GL_POLYGON)
            for i in range(361):
                rads = i*math.pi/180;
                glVertex2f(math.cos(rads), math.sin(rads))
            glEnd()
            glEndList()
        
    def realDraw(self):
        self.ensureDL()
        if self.outline:
            if self.selected:
                glColor4fv(self.selectedColor)
            else:
                glColor4fv(self.outlineColor)
            glPushMatrix()
            glScalef(self.width/2.0, self.height/2.0, 1)
            glCallList(Ellipse.EllipseDL[id(current_context)])
            glPopMatrix()
            glPushMatrix()
            glColor4fv(self.color)
            glScalef((self.width-2*self.lineWidth)/2.0,
                     (self.height-2*self.lineWidth)/2.0, 1)
            glCallList(Ellipse.EllipseDL[id(current_context)])
            glPopMatrix()
            
        else:
            glColor4fv(self.color)
            glPushMatrix()
            glScalef(self.width/2.0, self.height/2.0, 1)
            glCallList(Ellipse.EllipseDL[id(current_context)])
            glPopMatrix()
    
    def draw(self, lineWidth):
        glPushMatrix()
        self.toShapeSpace()
        glLineWidth(self.outlineWidth*lineWidth)
        if not self.fixedLineWidth:
            self.lineWidth = self.outlineWidth
        self.realDraw()
        glPopMatrix()
    
    def drawSelect(self, picker, parent=None):
        if(parent):
            picker.setColor(parent)
        else:
            picker.setColor(self)
        self.ensureDL()
        glPushMatrix()
        glTranslatef(self.x, self.y, 0)
        glScalef(self.width/2, self.height/2, 1)
        glCallList(Ellipse.EllipseDL[id(current_context)])
        glPopMatrix()

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def pick(self, p):
        pass

    def snap(self):
        pass

    def setSelected(self, s):
        self.selected = s

class ShadowEllipse(Shape):
    def __init__(self, x=0,y=0,w=0,h=0):
        Shape.__init__(self)
        self.x = x
        self.y = y
        self.width = w
        self.height = h

    ShadowEllipseDL = {}

    def realDraw(self):
        if not ShadowEllipse.ShadowEllipseDL.has_key(id(current_context)):
            ShadowEllipse.ShadowEllipseDL[id(current_context)] = glGenLists(1)
            c1 = [0.0, 0.0, 0.0, 0.8]
            c2 = [0.0, 0.0, 0.0, 0.0]
            glNewList(ShadowEllipse.ShadowEllipseDL[id(current_context)], GL_COMPILE)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

            glBegin(GL_TRIANGLE_STRIP)
            for i in range(361):
                offset = self.height * (5.0/60.0)
                rads = float(i)*math.pi/180.0
                glColor4fv(c2)
                glVertex2f(math.cos(rads),
                           math.sin(rads))
                glColor4fv(c1)
                glVertex2f(math.cos(rads)*0.5,
                           math.sin(rads)*0.5)

            glEnd()
            glDisable(GL_BLEND)
            glEndList()

        glPushMatrix()
        glTranslatef(self.height/12.0, -self.height/12.0, 0)
        glScalef(self.width/2.0, self.height/2.0, 1.0)
        glCallList(ShadowEllipse.ShadowEllipseDL[id(current_context)])
        glPopMatrix()
        
   
    def draw(self, lineWidth):
        glPushMatrix()
        self.toShapeSpace()
        self.realDraw()
        glPopMatrix()
        
    def drawSelect(self, picker, parent=None):
        pass
        
    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def pick(self, p):
        pass

    def snap(self):
        pass

    def setSelected(self, s):
        self.selected = s

class PolyLine(Shape):
    __fields__ = ['annotated', 'start', 'end', 'curved']
    def __init__(self,p1=0,p2=0,a=False, c=False, color=[0.0, 0.0, 0.0, 0.0]):
        Shape.__init__(self)
        self.start = p1
        self.end = p2
        self.annotated = a
        self.color = color
        self.curved = c

    def draw(self, lineWidth):
        if (self.selected):
            glColor4fv(self.selectedColor)
        else:
            glColor4fv(self.color)
        glLineWidth(self.outlineWidth*lineWidth)
        if self.annotated:
            glBegin(GL_LINES)
            p1 = Point(self.start.x,self.start.y)
            p2 = Point(self.end.x, self.end.y)
            barSize = WS_LINE_WIDTH
            delta = p2-p1
            delta_norm = delta*(1.0/delta.length())
            mid = p1 + delta * 0.5
            glVertex2f(p1.x, p1.y)
            glVertex2f(mid.x - (delta_norm * barSize * 4).x, mid.y - (delta_norm * barSize * 4).y)
            glVertex2f(mid.x + (delta_norm * barSize * 4).x, mid.y + (delta_norm * barSize * 4).y)
            glVertex2f(p2.x, p2.y)
            
            n = Point(-delta_norm.y, delta_norm.x)
            c = mid - (delta_norm*barSize*2)
            glVertex2f(c.x + (n*barSize*3).x, c.y + (n*barSize*3).y)
            glVertex2f(c.x - (n*barSize*3).x, c.y - (n*barSize*3).y)
            c = mid
            glVertex2f(c.x + (n*barSize*3).x, c.y + (n*barSize*3).y)
            glVertex2f(c.x - (n*barSize*3).x, c.y - (n*barSize*3).y)
            c = mid + (delta_norm*barSize*2)
            glVertex2f(c.x + (n*barSize*3).x, c.y + (n*barSize*3).y)
            glVertex2f(c.x - (n*barSize*3).x, c.y - (n*barSize*3).y)
            glEnd()
        elif self.curved:
            self.drawCurve()
        else:
            glBegin(GL_LINES)
            glVertex2f(self.start.x, self.start.y)
            glVertex2f(self.end.x, self.end.y)
            glEnd()

    def drawSelect(self, picker, parent=None):
        picker.setColor(self)
        glLineWidth(self.outlineWidth*3)
        if self.curved:
            self.drawCurve()
        else:
            glBegin(GL_LINES)
            glVertex2f(self.start.x, self.start.y)
            glVertex2f(self.end.x, self.end.y)
            glEnd()

    def drawCurve(self):
        glBegin(GL_LINE_STRIP)
        p1 = self.start
        p2 = self.end
        steps = 50
        r = p2-p1
        horizontal = False
        if p2.y > p1.y and p2.x > p1.x:
            horizontal = True
        for i in range(steps):
            t = float(i)/float(steps)
            if horizontal:
                glVertex2f(p1.x+r.x*t,
                           p1.y+r.y*(0.5+math.sin(math.pi*(t-0.5))*0.5))
            else:
                glVertex2f(p1.x+r.x*(0.5+math.sin(math.pi*(t-0.5))*0.5),
                           p1.y+r.y*t)
        glEnd()

    def pick(self, p):  
        pass

    def snap(self):
        pass

    def move(self, dx, dy):
        pass

    def setSelected(self, s):
        self.selected = s

class TextShape(Shape):
    __fields__ = ['text']
    def __init__(self, n=None, x=0, y=0, c=[0.0, 0.0, 0.0, 1.0]):
        Shape.__init__(self)
        self.text = n
        self.x = x
        self.y = y
        self.color = c[0:3]+[1.0]
        
    def draw(self):
        pass

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def pick(self, p):  
        pass

    def snap(self):
        pass

class PortShape(Shape):
    __fields__ = ['port', 'parentId', 'rectangle']
    def __init__(self, pid=0, p=0,x=0,y=0,w=0,h=0,c=0,optional=False, hidden=True):
        Shape.__init__(self)
        self.parentId = pid
        self.port = p
        self.x = x
        self.y = y
        self.width = w
        self.height = h
        if optional:
            self.rectangle = Ellipse(x,y,w,h)
            self.rectangle.fixedLineWidth = False
            self.rectangle.outlineWidth = 1.5
        else:
            self.rectangle = Rectangle(x,y,w,h)            
            self.rectangle.outlineWidth = 1.0
        self.rectangle.outline = True
        self.rectangle.color = c
        self.rectangle.outlineColor = ColorByName.get("black")
        self.optional = optional
        self.hidden = optional and hidden

    def draw(self, lineWidth):
        self.rectangle.draw(lineWidth)

    def drawSelect(self, picker, parent=None):
        self.rectangle.drawSelect(picker, self)

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        self.rectangle.move(dx,dy)

    def pick(self, p):
        pass
        
    def snap(self):
        pass
 
    def setSelected(self, s):
        self.selected = s

    def setColor(self, c):
        self.rectangle.color = c

    def toolTip(self):
        return self.port.toolTip()

    def hasToolTip(self):
        return True

class ModuleShape(Shape):
    __fields__ = ['portSize', 'portSpace', 'rectangle', 'shadow',
                  'text', 'sourcePorts', 'destPorts', 'sourcePortShapes',
                  'destPortShapes']
#    def __init__(self, id=0, sp=0, dp=0,n=None, x=0, y=0, w=0, h=0,c=0,oc=0,s=True):
    def __init__(self, id=0, sp=0, dp=0,n=None, x=0, y=0, w=0, h=0,c=0,oc=0,s=True,m=None):
        Shape.__init__(self)
        self.toolTipMsg = ""
        self.id = id
        self.x = x
        self.y = y
        self.width = w
        self.height = h
        self.portSize = 16
        self.portSpace = 18
        self.text = TextShape(n,x,y)
        self.sourcePorts = sp
        self.destPorts = dp
        self.sourcePortShapes = {}
        self.destPortShapes = {}
        self.module = m
        self.createPortShapes(s) # createPortShapes() might adjust self.width
        self.rectangle = Rectangle(x,y,self.width,self.height)
        self.rectangle.color = c
        self.color = c
        self.outlineColor = oc
        self.rectangle.outline = True
        self.matched = s
        self.rectangle.outlineColor = oc
        self.text.color = oc
        if (s):
            self.shadowRectangle = ShadowRectangle(x, y, w, h)
        else:
            self.shadowRectangle = NullShape()
            
    def draw(self, lineWidth):
        self.shadowRectangle.draw(lineWidth)
        self.rectangle.draw(lineWidth)
        for p in self.destPortShapes.itervalues():
            if (not p.optional) or (not p.hidden):
                p.draw(lineWidth)
        for p in self.sourcePortShapes.itervalues():
            if (not p.optional) or (not p.hidden):
                p.draw(lineWidth)

    def drawSelect(self,picker,parent=None):
        self.rectangle.drawSelect(picker,self)
        for v in self.destPortShapes.itervalues():
            if (not v.optional) or (not v.hidden):
                v.drawSelect(picker)
        for v in self.sourcePortShapes.itervalues():
            if (not v.optional) or (not v.hidden):
                v.drawSelect(picker)

    def move(self, dx, dy):
        self.x +=dx
        self.y +=dy
        self.shadowRectangle.move(dx,dy)
        self.rectangle.move(dx,dy)
        self.text.move(dx,dy)
        for p in self.destPortShapes.itervalues():
            p.move(dx,dy)
        for p in self.sourcePortShapes.itervalues():
            p.move(dx,dy)
        
    def pick(self, p):  
        pass

    def snap(self):
        pass    

    def setSelected(self,s):
        self.selected = s
        self.rectangle.setSelected(s)
       
    objectPortColor = [ColorByName.get(OBJECT_COLOR)[0] * 0.85,
                       ColorByName.get(OBJECT_COLOR)[1] * 0.85,
                       ColorByName.get(OBJECT_COLOR)[2] * 0.85,1]
    filterPortColor = [ColorByName.get(FILTER_COLOR)[0] * 0.85,
                       ColorByName.get(FILTER_COLOR)[1] * 0.85,
                       ColorByName.get(FILTER_COLOR)[2] * 0.85,1]
    successPortColor = [ColorByName.get(SUCCESS_COLOR)[0] * 0.85,
                        ColorByName.get(SUCCESS_COLOR)[1] * 0.85,
                        ColorByName.get(SUCCESS_COLOR)[2] * 0.85,1]
    errorPortColor = [ColorByName.get(ERROR_COLOR)[0] * 0.85,
                      ColorByName.get(ERROR_COLOR)[1] * 0.85,
                      ColorByName.get(ERROR_COLOR)[2] * 0.85,1]
    notExecutedPortColor = [ColorByName.get(NOT_EXECUTED_COLOR)[0] * 0.85,
                            ColorByName.get(NOT_EXECUTED_COLOR)[1] * 0.85,
                            ColorByName.get(NOT_EXECUTED_COLOR)[2] * 0.85,1]
    activePortColor = [ColorByName.get(ACTIVE_COLOR)[0] * 0.85,
                       ColorByName.get(ACTIVE_COLOR)[1] * 0.85,
                       ColorByName.get(ACTIVE_COLOR)[2] * 0.85,1]
    computePortColor = [ColorByName.get(COMPUTE_COLOR)[0] * 0.85,
                        ColorByName.get(COMPUTE_COLOR)[1] * 0.85,
                        ColorByName.get(COMPUTE_COLOR)[2] * 0.85,1]


    def setSuccess(self):
        self.toolTipMsg = 'Module executed successfully'
        self.rectangle.color = ColorByName.get(SUCCESS_COLOR)
        for p in self.destPortShapes.itervalues():
            p.setColor(self.successPortColor)
        for p in self.sourcePortShapes.itervalues():
            p.setColor(self.successPortColor)

    def setActive(self):
        self.toolTipMsg = 'Module is currently active'
        self.rectangle.color = ColorByName.get(ACTIVE_COLOR)
        for p in self.destPortShapes.itervalues():
            p.setColor(self.activePortColor)
        for p in self.sourcePortShapes.itervalues():
            p.setColor(self.activePortColor)

    def setComputing(self):
        self.toolTipMsg = 'Module is currently being executed'
        self.rectangle.color = ColorByName.get(COMPUTE_COLOR)
        for p in self.destPortShapes.itervalues():
            p.setColor(self.computePortColor)
        for p in self.sourcePortShapes.itervalues():
            p.setColor(self.computePortColor)


    def setError(self, me):
        self.toolTipMsg = me.msg 
        self.rectangle.color = ColorByName.get(ERROR_COLOR)
        for p in self.destPortShapes.itervalues():
            p.setColor(self.errorPortColor)
        for p in self.sourcePortShapes.itervalues():
            p.setColor(self.errorPortColor)

    def setNotExecuted(self):
        self.toolTipMsg = 'Module not executed because of pipeline errors'
        self.rectangle.color = ColorByName.get(NOT_EXECUTED_COLOR)
        for p in self.destPortShapes.itervalues():
            p.setColor(self.notExecutedPortColor)
        for p in self.sourcePortShapes.itervalues():
            p.setColor(self.notExecutedPortColor)

    def setDefault(self):
        self.rectangle.color = color

    def createPortShapes(self,matched=True):
        def portColor(d):
            if d.type == VistrailModuleType.Filter:
                return ModuleShape.filterPortColor
            else:
                return ModuleShape.objectPortColor
            
        destStart = [self.x-self.width/2+self.portSize/2+5,
                     self.y+self.height/2-self.portSize/2-5]
        sourceStart = [self.x+self.width/2-self.portSize/2-5, 
                       self.y-self.height/2+self.portSize/2+5]
        x = destStart[0]
        for d in self.destPorts:
            y = destStart[1]
            if matched:
                c = portColor(d)
            else:
                c = [0.45, 0.45, 0.45, 1.0]
            hidden = True
            if self.module and d.name in self.module.portVisible: hidden = False
            p = PortShape(self.id, d, x, y, self.portSize, self.portSize, c, d.optional, hidden)
            if not matched:
                p.rectangle.outlineColor = [0.35, 0.35, 0.35, 1.0]
            if not d.optional or not hidden:
                x += self.portSpace
            self.destPortShapes[d] = p
        x = sourceStart[0]
        for d in self.sourcePorts:
            y = sourceStart[1]
            if matched:
                c = portColor(d)
            else:
                c = [0.45, 0.45, 0.45, 1.0]
            hidden = True
            if self.module and d.name in self.module.portVisible: hidden = False
            p = PortShape(self.id, d, x, y, self.portSize, self.portSize, c, d.optional, hidden)
            if not matched:
                p.rectangle.outlineColor = [0.35, 0.35, 0.35, 1.0]
            if not d.optional or not hidden:
                x -= self.portSpace
            self.sourcePortShapes[d] = p

    def nextPosition(self, dst=True):
        if dst:
            x = self.x-self.width/2+self.portSize/2+5
            for d in self.destPortShapes.itervalues():
                if not d.hidden:
                    x += self.portSpace
        else:
            x = self.x+self.width/2-self.portSize/2-5
            for d in self.sourcePortShapes.itervalues():
                if not d.hidden:
                    x -= self.portSpace
        return x

    def getSourcePortPosition(self, port):
        for p in self.sourcePorts:
            if module_registry.registry.isPortSubType(super=port, sub=p):
                return Point(self.sourcePortShapes[p].x, self.sourcePortShapes[p].y)
        raise VistrailsInternalError("Error: did not find destination port")

    def getDestPortPosition(self, port):
        for p in self.destPorts:
            if module_registry.registry.isPortSubType(super=p, sub=port):
                return Point(self.destPortShapes[p].x, self.destPortShapes[p].y)
        raise VistrailsInternalError("Error: did not find destination port")

    def getSourcePort(self, point, port):
        matches = []
        for p in self.sourcePorts:
            if (module_registry.registry.portsCanConnect(p, port) and
                not self.sourcePortShapes[p].hidden):
                matches.append(p)
        if (len(matches) < 1):
            return None
        elif (len(matches) == 1):
            return matches[0]
        else:
            closest = matches[0]
            minDist = 1e40
            for p in matches:
                pos = self.getSourcePortPosition(p)         
                dist = ((point.x-pos.x)*(point.x-pos.x) + (point.y-pos.y)*(point.y-pos.y))
                if (dist < minDist):
                    minDist = dist
                    closest = p
            return closest

    def getDestPort(self, point, port):
        matches = []
        for p in self.destPorts:
            if (module_registry.registry.portsCanConnect(port, p) and
                not self.destPortShapes[p].hidden):
                matches.append(p)
        if (len(matches) < 1):
            return None
        elif (len(matches) == 1):
            return matches[0]
        else:
            closest = matches[0]
            minDist = 1e40
            for p in matches:
                pos = self.getDestPortPosition(p)           
                dist = ((point.x-pos.x)*(point.x-pos.x) + (point.y-pos.y)*(point.y-pos.y))
                if (dist < minDist):
                    minDist = dist
                    closest = p
            return closest

    def hasToolTip(self):
        return self.toolTipMsg != ""

    def toolTip(self):
        return self.toolTipMsg
    
    def setPortVisible(self, name, b):
        for s in self.sourcePorts:
            if s.name==name:
                shape = self.sourcePortShapes[s]
                if shape.optional:
                    shape.hidden = not b
                    if self.module:
                        if b: self.module.portVisible.add(name)
                        else: self.module.portVisible.discard(name)
                    shape.x = self.nextPosition(False)

        for d in self.destPorts:
            if d.name==name:
                shape = self.destPortShapes[d]
                if shape.optional:
                    shape.hidden = not b
                    if self.module:
                        if b: self.module.portVisible.add(name)
                        else: self.module.portVisible.discard(name)
                    shape.x = self.nextPosition(True)
        del self.module


class VersionShape(Shape):
    __fields__ = ['ellipse', 'text', 'shadowEllipse']
    def __init__(self, id=0, n=None, x=0, y=0, w=0, h=0, c=0, oc=ColorByName.get("black"), shadow=True):
        Shape.__init__(self)
        self.id = id
        self.x = x
        self.y = y
        self.width = w
        self.height = h
        self.ellipse = Ellipse(x,y,w,h)
        self.ellipse.outline = True
        self.ellipse.color = c
        self.ellipse.outlineColor = oc
        self.ellipse.id = id
        if shadow:
            self.shadowEllipse = ShadowEllipse(x, y, w+h/5, h+h/5)
        else:
            self.shadowEllipse = NullShape()
        self.text = TextShape(n,x,y,oc)

    def realDraw(self):
        self.shadowEllipse.realDraw()
        self.ellipse.realDraw()
    
    def draw(self, lineWidth):
        self.shadowEllipse.draw(lineWidth)
        self.ellipse.draw(lineWidth)
#        self.createDisplayList()
#        self.displayListDraw(lineWidth)

    def drawSelect(self, picker, parent=None):
        self.ellipse.drawSelect(picker, self)

    def move(self, dx, dy):
        self.x +=dx
        self.y +=dy
        self.ellipse.move(dx,dy)
        self.shadowEllipse.move(dx,dy)
        self.text.move(dx,dy)

    def pick(self, p):  
        pass

    def snap(self):
        pass

    def setSelected(self, s):
        self.selected = s
        self.ellipse.selected = s

class NullShape(Shape):
    def draw(self, lineWidth=0):
        pass

    def drawSelect(self, picker, parent=None):
        pass

    def pick(self, p):
        pass

    def snap(self, p):
        pass

    def move(self, dx, dy):
        pass

    def setSelected(self, s):
        pass

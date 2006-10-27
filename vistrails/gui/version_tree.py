from PyQt4 import QtCore, QtGui
from core.debug import DebugPrint
from core.vistrail import Vistrail
from core.data_structures import *
from gui.builder_utils import *
from gui.qt import SignalSet
from gui.shape import PolyLine, Ellipse
from gui.shape_engine import GLWidget
import core.system
import core.common
import gui.version_tree_search
import os

class DotNode(object):
    def __init__(self):
        self.p = Point(0,0)
        self.height = 0.0

        self.width = 0.0
        self.id = 0

class DotLayout(object):
    def __init__(self):
        self.nodes = {}
        self.height = 0.0
        self.scale = 0.0
        self.width = 0.0

class QVersionTree(QtGui.QScrollArea):
    def __init__(self, parent=None, controller=None):
	"""
	Parameters

	----------
	
	- parent = 'QtGui.QWidget'
	- controller = 'VistrailController'
	"""
	QtGui.QScrollArea.__init__(self,parent)
	self.setAcceptDrops(True)
	self.controller = controller
	self.shapeEngine = GLWidget()
        texPath = core.system.resourceDirectory() + "images/version_bg.png"
        self.shapeEngine.setupBackgroundTexture(texPath)
	self.shapeEngine.moveable = False
        self.shapeEngine.lineWidth = 0.02
        self.shapeEngine.versionTree = self
        self.shapeEngine.controller = controller
        #print "Set shapeEngine's controller to", controller
        #print "shapeEngine:", self.shapeEngine
	self.setWidget(self.shapeEngine)
	self.setWidgetResizable(True)
	self.versionGraph = self.controller.vistrail.getTerseGraph()
        self.signalSet = SignalSet(self,
                                   [(self.controller, QtCore.SIGNAL('versionWasChanged'), self.changeSelectedVersion)
                                   ,(self.controller, QtCore.SIGNAL('vistrailChanged()'), self.invalidateLayout)
                                   ,(self.shapeEngine, QtCore.SIGNAL('shapeSelected(int)'), self.controller.changeSelectedVersion)
                                   ,(self.shapeEngine, QtCore.SIGNAL('expandShapes()'), self.setSemiTerseTree)
                                   ,(self.shapeEngine, QtCore.SIGNAL('doubleClick(QEvent)'), self.dblClickExpansion)
                                   ,(self.shapeEngine, QtCore.SIGNAL('ctrlClick()'), self.selectMultiShapes)
                                   ,(self.shapeEngine, QtCore.SIGNAL('rightClick'), self.rclickMenu)])
        self.signalSet.plug()
	self.layout = DotLayout()
        self.search = gui.version_tree_search.TrueSearch()
        self.setTerseTree()
        self.refine = None

    def copySel(self, *args):
        """Ignore this call for now, might be useful later."""
        pass

    def paste(self, *args):
        """Ignore this call for now, might be useful later."""
        pass

    def updateBuilderOnChangeView(self, builder):
        """updateBuilderOnChangeView(self, builder) -> None.

        Shows the stack that is appropriate for a version tree on builder's
        stack widget, and allows editing of refine lineEdit.

        (updateBuilderOnChangeView gets called whenever this widget becomes
        visible on the builder's tabWidget.)"""
        builder.stackWidget.setCurrentIndex(0)
        builder.refineLineEdit.setReadOnly(False)
        builder.executeStackWidget.setCurrentIndex(0)
        
    def changeSelectedVersion(self, id):
        # Why doesn't this work?
        if self.shapeEngine.shapes.has_key(id):
            if self.shapeEngine.currentShape:
                self.shapeEngine.currentShape.setSelected(False)
            self.shapeEngine.currentShape = self.shapeEngine.shapes[id]
            self.shapeEngine.currentShape.setSelected(True)
#            self.shapeEngine.makeCurrent()
#            self.shapeEngine.paintGL()
    def invalidateLayout(self):
	self.dirty = True
	self.drawGraph()
        self.shapeEngine.updateGL()

    def setCompleteTree(self):
        self.refine=None
        self.getVersionGraph = self.controller.vistrail.getVersionGraph
        self.dirty = True
        self.controller.vistrail.currentGraph=None
        self.drawGraph()

    def setTerseTree(self):
        self.refine=None
        self.getVersionGraph = self.controller.vistrail.getTerseGraph
        self.dirty = True
        self.controller.vistrail.currentGraph=None
	self.drawGraph()
        
    def setSemiTerseTree(self):
        self.getVersionGraph = self.controller.vistrail.getSemiTerseGraph
        self.dirty = True
        self.drawGraph()

    def setRefineTree(self):  #refine from entire terse graph
        self.controller.vistrail.currentGraph=None
        self.getVersionGraph = self.controller.vistrail.getTerseGraph
        #self.invalidateLayout()
        #self.dirty=True
        #self.shapeEngine.clearShapes()
        #self.layoutGraph()
        self.refineGraph()
        self.getVersionGraph = self.controller.vistrail.getCurrentGraph
        self.invalidateLayout()
        #self.dirty=True
        #self.drawGraph()

    def dblClickExpansion(self, event):
        #pickedShapes = self.controller.vistrail.expand
        #for double click on annotated line, expand
        self.shapeEngine.pickShape(Point(event.pos().x(), self.shapeEngine.height-event.pos().y()))
        if self.shapeEngine.currentShape:
            if isinstance(self.shapeEngine.currentShape,PolyLine):
                if self.shapeEngine.currentShape.annotated:
                    tgraph = self.controller.vistrail.getTerseGraph()
                    fgraph = self.controller.vistrail.getVersionGraph()
                    xe=self.shapeEngine.currentShape.end.x
                    ye=self.shapeEngine.currentShape.end.y
                    self.shapeEngine.pickShape(self.shapeEngine.worldToScreen(Point(xe,ye)))
                    s1=self.shapeEngine.currentShape.id
                    s2 = self.controller.vistrail.getCurrentGraph().parent(s1)
                    if self.refine: self.setRefineTree()
                    else: self.setTerseTree()
                    self.expandSel([s1,s2])
        else:
             #double click on multiple shape selection
            if len(self.shapeEngine.selectedShapes) == 0:
                if self.refine:
                    self.setRefineTree()
                else:
                    self.setTerseTree()
                
            self.expandSel()

    def selectMultiShapes(self):
        if self.shapeEngine.currentShape:
            if self.controller.vistrail.getCurrentGraph().vertices.has_key(self.shapeEngine.currentShape.id):
                if self.shapeEngine.currentShape not in self.shapeEngine.selectedShapes:
                    self.shapeEngine.selectedShapes.append(self.shapeEngine.currentShape)
                else:
                    self.shapeEngine.selectedShapes.remove(self.shapeEngine.currentShape)
                    self.shapeEngine.currentShape.setSelected(False)
            else:
                self.shapeEngine.currentShape.setSelected(False)

    def expandSel(self, selShapes=None):
        """expands selected nodes"""
        if selShapes == None: #workaround since lists are mutable
            selShapes = []
        tgraph = self.controller.vistrail.getTerseGraph()
        fgraph = self.controller.vistrail.getVersionGraph()
        sShapes = []
        if not len(selShapes):
            for s in self.shapeEngine.selectedShapes:
                sShapes.append(s)

            while len(sShapes):
                s=sShapes.pop()
                if tgraph.vertices.has_key(s.id):
                    selShapes.append(s.id)

        expand=[]

        if len(selShapes):
            expand = getExpand(tgraph, fgraph, selShapes)
        self.controller.vistrail.setExp(expand)
        self.setSemiTerseTree()

        for s in self.shapeEngine.selectedShapes:
            s.setSelected(False)
        self.shapeEngine.selectedShapes = []
        self.shapeEngine.currentShape = None
        selShapes = []
    def rclickMenu(self, event):
        """creates a right click menu for expanding, collapsing, etc the version tree"""
        menu = QtGui.QMenu()

        expandAct = QtGui.QAction(self.tr("E&xpand Selection"),self)
        terseAct = QtGui.QAction(self.tr("&Terse View"),self)
        fullAct = QtGui.QAction(self.tr("&Full View"),self)
        copyAct = QtGui.QAction(self.tr("&Copy Selection"),self)
        pasteAct = QtGui.QAction(self.tr("&Paste"),self)
        stickAct = QtGui.QAction(self.tr("&Path to Root"),self)
        subtreeAct = QtGui.QAction(self.tr("Select &Subtree"),self)

        expandAct.setStatusTip(self.tr("Expand Selected Nodes"))
        terseAct.setStatusTip(self.tr("View Standard Annotation on Version Tree"))
        fullAct.setStatusTip(self.tr("View the Entire Version Tree"))
        copyAct.setStatusTip(self.tr("Copy the Selected Nodes"))
        pasteAct.setStatusTip(self.tr("Paste to Version Tree"))
        stickAct.setStatusTip(self.tr("Expands from the selected node to the root of the Version Tree"))
        subtreeAct.setStatusTip(self.tr("Selects the subtree with the selected node as the root"))
                                   
        
        self.connect(expandAct, QtCore.SIGNAL("triggered()"), self.expandSel)
        self.connect(terseAct, QtCore.SIGNAL("triggered()"), self.setTerseTree)
        self.connect(fullAct, QtCore.SIGNAL("triggered()"), self.setCompleteTree)
        self.connect(copyAct, QtCore.SIGNAL("triggered()"), self.copySel)
        self.connect(pasteAct, QtCore.SIGNAL("triggered()"), self.pasteSel)
        self.connect(stickAct, QtCore.SIGNAL("triggered()"), self.stickSel)
        self.connect(subtreeAct, QtCore.SIGNAL("triggered()"), self.subtreeSel)

        menu.addAction(expandAct)
        menu.addAction(terseAct)
        menu.addAction(fullAct)
        menu.addAction(copyAct)
        menu.addAction(pasteAct)
        menu.addAction(stickAct)
        menu.addAction(subtreeAct)
        
        #p = self.shapeEngine.screenToWorld(Point(event.pos().x(), self.shapeEngine.height-event.pos().y()))
        menu.exec_(event.globalPos())

    def copySel(self):
        print "Copy operation not yet implemented"

    def pasteSel(self):
        print "Paste operation not yet implemented"

    def stickSel(self):
        if self.shapeEngine.currentShape:
            self.expandSel([0,self.shapeEngine.currentShape.id])
        elif len(self.shapeEngine.selectedShapes):
            self.expandSel([0,self.shapeEngine.selectedShapes[0].id])
    
    def subtreeSel(self):
        the_shape = 0
        newselection = []
        if self.shapeEngine.currentShape:
            the_shape = self.shapeEngine.currentShape.id
        elif len(self.shapeEngine.selectedShapes):
            ss = []
            for s in self.shapeEngine.selectedShapes:
                ss.append(s.id)
            the_shape = min(ss)
        for sh in self.shapeEngine.selectedShapes:
            sh.setSelected(False)
        self.shapeEngine.selectedShapes=[]
        ds = self.controller.vistrail.getCurrentGraph().descendants(the_shape)
        for d in ds:
            self.shapeEngine.shapes[d].setSelected(True)
            self.shapeEngine.selectedShapes.append(self.shapeEngine.shapes[d])

    def drawGraph(self):
        self.shapeEngine.clearShapes()
	self.layoutGraph()
	self.shapeEngine.panX = self.layout.width/2.0
	self.shapeEngine.panY = self.layout.height/2.0
	self.shapeEngine.panZ = min(1.0/self.layout.width, 1.0/self.layout.height)
	itm = self.controller.vistrail.inverseTagMap
        am = self.controller.vistrail.actionMap

        # sort by ids
        idlist = []
        for b2 in self.layout.nodes.values():
            idlist.append(b2.id)

        sidlist = sorted(idlist)
        count = 0
        idmap = {}
        for id in sidlist:
            idmap[id] = count
            count += 1

        selected = {}
        selected_ord = []
        selected_mx = 0
        for b2 in self.layout.nodes.itervalues():
            s = (b2.id != 0) and self.search.match(am[b2.id])
            selected[b2] = s
            if s:
                selected_ord.append(b2.id)
        selected_ord.sort()
        selected_pos = dict((id,pos) for (pos,id) in core.common.withIndex(selected_ord))
	for b1,b2 in self.layout.nodes.items():
            if itm.has_key(b1):
                f = itm[b1]
            else:
                f = None
            if am.has_key(b2.id):
                user = am[b2.id].user
            else:
                user=None

            sat = 1.0
            if selected[b2]:
                sat = (float(selected_pos[b2.id]) + 1.0) / float(len(selected_pos))
	    self.shapeEngine.addVersionShape(b2.id, f, b2.p,
					     b2.width, b2.height,
                                             sat, user, selected[b2])

	for b in self.versionGraph.vertices.keys():
            eFrom = self.versionGraph.edgesFrom(b)
            for (e1,e2) in eFrom:
                g = not (selected_pos.has_key(self.layout.nodes[b].id) and
                         selected_pos.has_key(self.layout.nodes[e1].id))
                self.shapeEngine.addConnection(self.layout.nodes[b].id,
					       self.layout.nodes[e1].id,
					       e2 != 0,
                                               g)

    def refineGraph(self):
        """uses self.refine to annotate the graph based on user-defined terms"""
        if self.refine:
            terse = self.controller.vistrail.getTerseGraph().__copy__()
            am = self.controller.vistrail.actionMap
            full = self.controller.vistrail.getVersionGraph()
            x=[0]
            while len(x):
                current=x.pop()
                efrom = []
                eto = []
                for f in terse.edgesFrom(current):
                    efrom.append(f)
                for t in terse.edgesTo(current):
                    eto.append(t)
                for (e1,e2) in efrom:
                    x.append(e1)
                if current !=0 and not self.refine.match(am[current]) and terse.vertices.__contains__(current):
                    to_me = eto[0][0]
                    if terse.vertices.__contains__(to_me):
                        terse.deleteEdge(to_me, current, None)
                    for from_me in efrom:
                        f_me = from_me[0]
                        if terse.vertices.__contains__(f_me):
                            annotated = -1
                            if full.parent(f_me)==to_me:
                                annotated=0
                            terse.deleteEdge(current, f_me, None)
                            terse.addEdge(to_me, f_me, annotated)
                    terse.deleteVertex(current)
            self.controller.vistrail.setCurrentGraph(terse)

    def outputVistrailGraph(self, f):
        """
        Parameters
        ----------

        - f : file-like object
        """
        itm = self.controller.vistrail.inverseTagMap
        for v,t in itm.items():
            f.write('  %s [label="%s"];\n' % (v, t))

        f.write('  0;\n')
        self.maxId = 0
        self.minid = 0
        for id in self.versionGraph.vertices.keys():
            froom = self.versionGraph.edgesFrom(id)
            for (first,second) in froom:
                f.write('%s -> %s;\n' % (id, first))

    def parseOutput(self, file):
        """
        Parameters
        ----------

        - file : 'open file object'
        
        """
        result = DotLayout()

        import tokenize

        src = tokenize.generate_tokens(file.readline)
        token = src.next()

        while token[0] is not tokenize.ENDMARKER:
            if token[0] is tokenize.NAME:
                #read the first line, which is something like
                #graph scale width height
                if token[1] == 'graph':
                    token = src.next()
                    result.scale = float(token[1])
                    token = src.next()
                    result.width = float(token[1])
                    token = src.next()
                    result.height = float(token[1]) 
                elif token[1] == 'node':
                    n = DotNode()
                    token = src.next()
                    n.id = int(token[1])
                    token = src.next()
                    x = float(token[1])
                    token = src.next()
                    y = float(token[1])
                    n.p = Point(x,y)
                    token = src.next()
                    n.width = float(token[1])
                    token = src.next()
                    n.height = float(token[1])
                    result.nodes[n.id] = n
                elif token[1] == 'stop':
                    break
            token = src.next()
        return result

    def layoutGraph(self):
	if not self.dirty:
	    return
        self.versionGraph = self.getVersionGraph()
        self.controller.vistrail.setCurrentGraph(self.versionGraph)
	f = file(core.system.temporaryDirectory() + "dot_tmp_vistrails.txt","w")
        f.write("digraph G {\n")
        self.outputVistrailGraph(f)
        f.write("}\n")
        f.close()

        tempDir = core.system.temporaryDirectory()
        cmdline = (core.system.graphVizDotCommandLine() +
                   tempDir + "dot_output_vistrails.txt " +
                   tempDir + "dot_tmp_vistrails.txt")

        os.system(cmdline)

        fileIn = open(core.system.temporaryDirectory() + "dot_output_vistrails.txt")

        self.layout = self.parseOutput(fileIn)

        #since some of the nodes are refined away
        newnodes = {}
        for v in self.versionGraph.vertices:
            newnodes[v] = self.layout.nodes[v]
        self.layout.nodes = newnodes

        #removing temp files
        core.system.removeGraphvizTemporaries()
        
        self.dirty = False

    def showEvent(self, event):
        self.shapeEngine.updateGL()
        self.emit(QtCore.SIGNAL("makeCurrent"),self)
    
    def keyPressEvent(self, event):
	if(event.key() == QtCore.Qt.Key_R and (event.modifiers() & QtCore.Qt.ControlModifier)):
	    self.resetCamera()
	else:
	    event.ignore()
    
    def resetCamera(self):
	self.panX = 0
        self.panY = 0
        self.panZ = 1
	self.invalidateLayout()

def isInPath(parent, bottom, top): #used for dblClickExpansion
    """tells whether bottom is a descendent of top
    (useful for the expansion of multiple selected shapes)
    """
    curr=bottom
    while curr>top:
        if parent[curr]==top:
            return True
        curr=parent[curr]
    return False

def getExpand(tgraph, fullgraph, selShapes):
    """creates a list of tuples between which the graph should be expanded.

    Parameters
    ----------
    -tgraph : 'Graph' - terse graph
    -fgraph : 'Graph' - complete version tree
    -selShapes : 'list' - currently selected shapes (int ids)

    Returns
    -------
    - 'list' [(v1,v2), (v2,v3), (v10,v19)...] to expand between 1,2; 2,3; 10,19;
    """

    expand=[]
    p=tgraph.bfs(0)
    if len (selShapes):
        selShapes.sort()
    while len(selShapes)>1:
        currentBottom=selShapes.pop()
        for currentTop in selShapes:
            if isInPath(p, currentBottom, currentTop):
                b=currentBottom
                while b>currentTop:
                    next=tgraph.parent(b)
                    if not fullgraph.parent(b)==next:
                        expand.append((b,next))
                    b=next
    return expand

#     p = terse.bfs(0)
#     expand = []
#     if isInPath(p, max(selShapes), min(selShapes)):
#         selShapes.sort()
#         if len(selShapes):
#             bottom=selShapes.pop()
#         while len(selShapes):
#             nxt = selShapes.pop()
#             if full.parent(bottom) != nxt:
#                 expand.append((bottom,terse.parent(bottom)))
#             bottom=nxt
#     print expand
#     return expand



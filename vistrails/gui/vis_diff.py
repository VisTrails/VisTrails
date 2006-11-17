from PyQt4 import QtCore, QtGui
from gui.shape_engine import *
from core.vistrail import *
from core.data_structures import *
import string
from core.utils import *
from core import system

class FunctionItemModel(QtGui.QStandardItemModel):
    def __init__(self,row,col,parent=None):
        QtGui.QStandardItemModel.__init__(self,row,col,parent)
        self.disabledRows = {}

    def flags(self, index):
        if index.isValid() and self.disabledRows.has_key(index.row()):
            return QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled | QtCore.Qt.ItemIsSelectable
        return QtGui.QStandardItemModel.flags(self,index)

    def clearList(self):
        self.disabledRows = {}
        self.removeRows(0,self.rowCount())

    def disableRow(self,row):
        self.disabledRows[row] = None

class ParamChanges(QtGui.QWidget):
    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
        QtGui.QWidget.__init__(self, parent, f | QtCore.Qt.Tool)
        self.setWindowTitle('Parameter Changes - None')
        self.firstTime = True
        self.boxLayout = QtGui.QVBoxLayout()
        self.boxLayout.setMargin(0)
        self.boxLayout.setSpacing(0)
        self.tabWidget = QtGui.QTabWidget()
        self.tabWidget.setTabPosition(QtGui.QTabWidget.North)
        self.tabWidget.setTabShape(QtGui.QTabWidget.Triangular)
        self.fFont = QtGui.QFont('Arial', 10)

        self.allFunctionsModel = FunctionItemModel(0,2,self)
        self.allFunctionsModel.setHeaderData(0,QtCore.Qt.Horizontal,QtCore.QVariant(self.parent().v1name))
        self.allFunctionsModel.setHeaderData(1,QtCore.Qt.Horizontal,QtCore.QVariant(self.parent().v2name))
        self.allFunctionsSelModel = QtGui.QItemSelectionModel(self.allFunctionsModel)
        self.allFunctions = QtGui.QTableView()
        self.allFunctions.setModel(self.allFunctionsModel)
        self.allFunctions.setSelectionModel(self.allFunctionsSelModel)
        self.allFunctions.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.allFunctions.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.allFunctions.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.allFunctions.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.allFunctions.setFont(self.fFont)
        self.tabWidget.addTab(self.allFunctions, 'Functions')

        self.annotationsModel = FunctionItemModel(0,2,self)        
        self.annotationsModel.setHeaderData(0,QtCore.Qt.Horizontal,QtCore.QVariant(self.parent().v1name))
        self.annotationsModel.setHeaderData(1,QtCore.Qt.Horizontal,QtCore.QVariant(self.parent().v2name))
        self.annotationsSelModel = QtGui.QItemSelectionModel(self.annotationsModel)
        self.annotations = QtGui.QTableView()
        self.annotations.setModel(self.annotationsModel)
        self.annotations.setSelectionModel(self.annotationsSelModel)
        self.annotations.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.annotations.horizontalHeader().setStretchLastSection(True)
        self.annotations.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.annotations.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.annotations.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.annotations.setFont(self.fFont)
        self.tabWidget.addTab(self.annotations, 'Annotations')
        
        self.boxLayout.addWidget(self.tabWidget)
        self.boxLayout.addWidget(QtGui.QSizeGrip(self))
        self.setLayout(self.boxLayout)

    def closeEvent(self,e):
        e.ignore()
        self.parent().showParamsAction.setChecked(False)

class LegendBox(QtGui.QFrame):
    def __init__(self, color, size, parent=None, f=QtCore.Qt.WindowFlags()):
        QtGui.QFrame.__init__(self, parent, f)
        self.setFrameStyle(QtGui.QFrame.Box | QtGui.QFrame.Plain)
        self.setAttribute(QtCore.Qt.WA_PaintOnScreen)
        self.setAutoFillBackground(True)
        self.palette().setColor(QtGui.QPalette.Window,
                                QtGui.QColor(color[0]*255,
                                             color[1]*255,
                                             color[2]*255))
        self.setFixedSize(size)

class LegendWindow(QtGui.QWidget):
    def __init__(self, size, parent=None, f=QtCore.Qt.WindowFlags()):
        QtGui.QWidget.__init__(self, parent, f | QtCore.Qt.Tool)
        self.setWindowTitle('Visual Diff Legend')
        self.firstTime = True
        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setMargin(10)
        self.gridLayout.setSpacing(10)
        self.lFont = QtGui.QFont('Arial', 9)
        self.setFont(self.lFont)
        
        parent = self.parent()
        self.legendSize = size

        self.legendV1Box = LegendBox(parent.v1Color, parent.legendSize, self)
        self.gridLayout.addWidget(self.legendV1Box,0,0)
        self.legendV1 = QtGui.QLabel("Version '" + parent.v1name + "'", self)
        self.gridLayout.addWidget(self.legendV1,0,1)
        
        self.legendV2Box = LegendBox(parent.v2Color, self.legendSize, self)
        self.gridLayout.addWidget(self.legendV2Box,1,0)
        self.legendV2 = QtGui.QLabel("Version '" + parent.v2name + "'", self)
        self.gridLayout.addWidget(self.legendV2,1,1)
        
        self.legendV12Box = LegendBox(parent.commonColor, self.legendSize, self)
        self.gridLayout.addWidget(self.legendV12Box,2,0)
        self.legendV12 = QtGui.QLabel("Shared", self)
        self.gridLayout.addWidget(self.legendV12,2,1)
        
        self.legendParamBox = LegendBox(parent.paramColor, self.legendSize, self)
        self.gridLayout.addWidget(self.legendParamBox,3,0)
        self.legendParam = QtGui.QLabel("Parameter Changes", self)
        self.gridLayout.addWidget(self.legendParam,3,1)
        
    def closeEvent(self,e):
        e.ignore()
        self.parent().showLegendsAction.setChecked(False)

class VisualDiff(QtGui.QMainWindow):
    def __init__(self, vistrail, v1, v2, parent=None, f=QtCore.Qt.WindowFlags()):
        self.vistrail = vistrail
        self.v1 = v1
        self.v2 = v2
        self.commonColor = [0.45]*3
        self.v1Color = ColorByName.get("melon")
        self.v2Color = ColorByName.get("steel_blue_light")
        self.paramColor = ColorByName.get("light_grey")
        
        self.v1andv2 = self.v1andv2Ver = self.v1andv2Sig = []        
        self.v1param = self.v2param = self.v1paramVer = self.v2paramVer = self.v1paramSig = self.v2paramSig = {}
        self.pl = self.plVer = self.plSig = []
        self.modChanged = self.modChangedVer = self.modChangedSig = []
        self.moduleShift = 0
        self.vistrail = vistrail
        self.v1name = self.vistrail.getVersionName(self.v1)
        if not self.v1name:
            self.v1name = '"unnamed"'
        self.v2name = self.vistrail.getVersionName(self.v2)
        if not self.v2name:
            self.v2name = '"unnamed"'
        
        visDiffParent = QtCore.QCoreApplication.instance().visDiffParent
        QtGui.QMainWindow.__init__(self, visDiffParent, f | QtCore.Qt.Dialog)
        self.setWindowTitle('Visual Diff - ' + self.v1name + ' vs. ' + self.v2name)
        self.setMouseTracking(True)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,
                                             QtGui.QSizePolicy.Expanding))
        self.shapeEngine = GLWidget()
        root = system.visTrailsRootDirectory()+'/gui/resources/'
        texPath = root + "/images/pipeline_bg.png"
        self.shapeEngine.setupBackgroundTexture(texPath)
        self.shapeEngine.lineWidth = 2.0
        self.shapeEngine.draggingPortConnectionEnabled = False        
        self.connect(self.shapeEngine, QtCore.SIGNAL("shapeSelected(int)"), self.moduleSelected)
        self.connect(self.shapeEngine, QtCore.SIGNAL("shapeUnselected()"), self.moduleUnselected)
        self.selectedModule = -1
        
        self.setCentralWidget(self.shapeEngine)
        self.iconSize = QtCore.QSize(24,24)
        self.legendSize = QtCore.QSize(16,16)
        self.toolBar = self.addToolBar('Visual Diff Toolbar')
        self.toolBar.setMovable(False)
        self.toolBar.setIconSize(self.iconSize)
        self.matchBySigAction = self.toolBar.addAction(QtGui.QIcon(root + "/images/match_by_sig.png"),
                                                       'Match modules/functions by signature')
        self.matchBySigAction.setCheckable(True)
        self.matchBySigAction.setChecked(True)
        self.connect(self.matchBySigAction, QtCore.SIGNAL("toggled(bool)"), self.matchChanged)
        
        self.showParamsAction = self.toolBar.addAction(QtGui.QIcon(root + "/images/show_params.png"),
                                                       'Show Parameter Changes window')
        self.showParamsAction.setCheckable(True)
        self.connect(self.showParamsAction, QtCore.SIGNAL("toggled(bool)"), self.paramChanged)
        self.showLegendsAction = self.toolBar.addAction(QtGui.QIcon(root + "/images/show_legends.png"),
                                                       'Show Legends')
        self.showLegendsAction.setCheckable(True)
        self.connect(self.showLegendsAction, QtCore.SIGNAL("toggled(bool)"), self.legendChanged)
        
        self.genDiff(v1, v2)
        self.matchChanged()
        self.resize(512,512/self.shapeEngine.zoomToFit())

        self.paramWindow = ParamChanges(self)
        self.paramWindow.resize(384,256)
        self.aModel = self.paramWindow.allFunctionsModel
        self.nModel = self.paramWindow.annotationsModel

        self.legendWindow = LegendWindow(self.legendSize,self)

    def moduleSelected(self, id):
        self.selectedModule = id
        self.aModel.clearList()        
        self.nModel.clearList()
        funcList = {}
        v1f = v2f = []
        lmax = 0
        keys = []
        k1 = k2 = {}
        if id in self.v1paramSig:
            v1f = self.v1paramSig[id]
            for f in v1f: funcList[f] = None
            lmax = max(lmax, len(v1f))
            self.paramWindow.setWindowTitle('Parameter Changes - ' + self.plSig[0].modules[id].name)
            k1 = self.plSig[0].modules[id].annotations
            keys += k1.keys()
        if id in self.v2paramSig:
            v2f = self.v2paramSig[id]
            for f in self.v2paramSig[id]: funcList[f] = None
            lmax = max(lmax, len(v2f))
            self.paramWindow.setWindowTitle('Parameter Changes - ' + self.plSig[1].modules[id].name)
            k2 = self.plSig[1].modules[id].annotations
            keys += k2.keys()

        self.aModel.insertRows(0,len(funcList))
        l1 = l2 = f1 = f2 = r = 0
        sortedFunc = funcList.keys()
        sortedFunc.sort()
        for f in sortedFunc:
            finv1 = False
            finv2 = False
            if f in v1f:
                self.aModel.setData(self.aModel.index(r,0), QtCore.QVariant(f))
                finv1 = True
            if f in v2f:
                self.aModel.setData(self.aModel.index(r,1), QtCore.QVariant(f))
                finv2 = True
            if finv1 and finv2:
                self.aModel.disableRow(r)                
            r += 1

        keys.sort()
        for i in reversed(range(len(keys)-1)):
            if keys[i+1]==keys[i]: del keys[i+1]
        self.nModel.insertRows(0,len(keys))
        for i in range(len(keys)):
            key = keys[i]
            self.nModel.setHeaderData(i, QtCore.Qt.Vertical, QtCore.QVariant(key))
            s1 = s2 = '<undefined>'
            if key in k1: s1 = k1[key]
            if key in k2: s2 = k2[key]
            self.nModel.setData(self.nModel.index(i,0), QtCore.QVariant(s1))
            self.nModel.setData(self.nModel.index(i,1), QtCore.QVariant(s2))
            if s1==s2:
                self.nModel.disableRow(i)
            
        self.paramWindow.allFunctions.resizeRowsToContents()
        self.paramWindow.annotations.resizeRowsToContents()

    def moduleUnselected(self):
        self.selectedModule = -1
        self.aModel.clearList()
        self.nModel.clearList()
        self.paramWindow.setWindowTitle('Parameter Changes - None')

    def matchChanged(self):
        self.updateDiff()
	if (self.isVisible()):
	    self.shapeEngine.updateGL()
        
    def paramChanged(self):
        if self.paramWindow.firstTime:
            self.paramWindow.move(self.pos().x()+self.frameSize().width(),self.pos().y())
            self.paramWindow.firstTime = False
        self.paramWindow.setVisible(self.showParamsAction.isChecked())
            
    def legendChanged(self):
        if self.legendWindow.firstTime:
            self.legendWindow.move(self.pos().x()+self.frameSize().width(),self.pos().y())
        self.legendWindow.setVisible(self.showLegendsAction.isChecked())
        if self.legendWindow.firstTime:
            self.legendWindow.firstTime = False
            self.legendWindow.setFixedSize(self.legendWindow.size())            

    def genDiff(self, v1, v2):
        if v1 == 0 or v2 == 0:
            raise VistrailsInternalError("Should not be called with either v1 or v2 equals 0")
        [self.v1andv2Ver,self.v1paramVer,self.v2paramVer] = self.vistrail.getPipelineShare(v1,v2)

        # Diff only based on version tree
        self.plVer = [self.vistrail.getPipelineVersionNumber(v1),
                      self.vistrail.getPipelineVersionNumber(v2)]
        self.modChangedVer = {}
        for i in self.v1paramVer.keys(): self.modChangedVer[i] = None
        for i in self.v2paramVer.keys(): self.modChangedVer[i] = None
        self.modChangedVer = self.modChangedVer.keys()

        # Diff by looking at module/function signatures
        # Find more shared modules by looking at modules names
        # just a N^2 straight-forward comparisons
        self.v1andv2Sig = copy.deepcopy(self.v1andv2Ver)
        self.plSig = [self.vistrail.getPipelineVersionNumber(v1),
                      self.vistrail.getPipelineVersionNumber(v2)]                
        newIdBase = max(i for k in range(2) for (i,j) in self.plSig[k].modules.items())+1
        for (i,m) in self.plSig[0].modules.items():
            if not (m.id in self.v1andv2Sig):
                for (j,n) in self.plSig[1].modules.items():
                    if not (n.id in self.v1andv2Sig):
                        if m.name==n.name:
                            # Get a new Id for this module
                            newId = newIdBase
                            newIdBase += 1
                            # Correct all connections
                            for (l,c) in self.plSig[0].connections.items():
                                if c.sourceId==m.id: c.sourceId = newId
                                if c.destinationId==m.id: c.destinationId = newId
                            for (l,c) in self.plSig[1].connections.items():
                                if c.sourceId==n.id: c.sourceId = newId
                                if c.destinationId==n.id: c.destinationId = newId
                            m.id = newId
                            self.plSig[0].modules[newId] = m
                            del(self.plSig[0].modules[i])
                            n.id = newId
                            self.plSig[1].modules[newId] = n
                            del(self.plSig[1].modules[j])
                            self.v1andv2Sig.append(newId)

        # Capture parameter changes
        self.v1paramSig = {}
        self.v2paramSig = {}
        for (m,m1) in self.plSig[0].modules.items():
            if not (m) in self.v1paramSig: self.v1paramSig[m] = []
            for f in m1.functions:
                values = string.joinfields([str(v.strValue) for v in f.params],',')
                self.v1paramSig[m].append(string.joinfields([f.name,'(',values,')'],''))
        for (m,m2) in self.plSig[1].modules.items():
            if not (m) in self.v2paramSig: self.v2paramSig[m] = []
            for f in m2.functions:
                values = string.joinfields([str(v.strValue) for v in f.params],',')
                self.v2paramSig[m].append(string.joinfields([f.name,'(',values,')'],''))
        # Eliminate anything that have the same function list
        self.modChangedSig = []
        for m in self.v1andv2Sig:
            if (string.joinfields(self.v1paramSig[m],'|')!=string.joinfields(self.v2paramSig[m], '|') or
                self.plSig[0].modules[m].annotations!=self.plSig[1].modules[m].annotations):
                self.modChangedSig.append(m)
                
    def selectDiff(self,match=None):
        if not match:
            match = self.matchBySigAction.isChecked()
        if match:
            self.v1andv2 = self.v1andv2Sig
            self.v1param = self.v1paramSig
            self.v2param = self.v2paramSig
            self.pl = self.plSig
            self.modChanged = self.modChangedSig
        else:
            self.v1andv2 = self.v1andv2Ver
            self.v1param = self.v1paramVer
            self.v2param = self.v2paramVer
            self.pl = self.plVer
            self.modChanged = self.modChangedVer

    def updateDiff(self,match=None):
        self.selectDiff(match)
        self.shapeEngine.clearShapes()
        for (id,m) in self.pl[0].modules.items():
            if not (m.id in self.v1andv2):
                sh = self.shapeEngine.addModuleShape(m, self.v1Color)
            else:
                if m.id in self.modChanged:
                    sh = self.shapeEngine.addModuleShape(m, self.paramColor)
                else:
                    sh = self.shapeEngine.addModuleShape(m, None, False)
        self.moduleShift = max(i for (i,j) in self.pl[0].modules.items())+1
        for (id,m) in self.pl[1].modules.items():
            if not (m.id in self.v1andv2):
                m.id += self.moduleShift
                sh = self.shapeEngine.addModuleShape(m, self.v2Color)                
            else:
                continue

        # Correct connections
        connectionShift = max(i for (i,j) in self.pl[0].connections.items())+1
        allConnections = self.pl[0].connections
        for (i,c) in self.pl[1].connections.items():            
            if not (c.sourceId in self.v1andv2):
                c.sourceId += self.moduleShift
            if not (c.destinationId in self.v1andv2):
                c.destinationId += self.moduleShift
            allConnections[connectionShift+i] = c

        # Color Code Connection
        self.shapeEngine.setPortConnections(allConnections)
        for l in self.shapeEngine.connectionShapesOver:
            c = allConnections[l.id]
            sv = None
            if not (c.sourceId in self.v1andv2):
                sv = c.sourceId
            if not (c.destinationId in self.v1andv2):
                sv = c.destinationId
            if sv:
                if sv<self.moduleShift:
                    l.color = self.v1Color
                else:
                    l.color = self.v2Color
            else:
                found = False
                for (i,j) in self.pl[0].connections.items():
                    if ((c.sourceId==j.sourceId and c.destinationId==j.destinationId) or
                        (c.sourceId==j.destinationId and c.destinationId==j.sourceId) ):
                        found = True
                if not found:
                    l.color = self.v2Color
                else:
                    found = False
                    for (i,j) in self.pl[1].connections.items():
                        if ((c.sourceId==j.sourceId and c.destinationId==j.destinationId) or
                            (c.sourceId==j.destinationId and c.destinationId==j.sourceId) ):
                            found = True
                    if not found:
                        l.color = self.v1Color

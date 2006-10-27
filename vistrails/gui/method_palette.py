from PyQt4 import QtCore, QtGui, QtOpenGL
from gui.qframebox import *
from gui.qmodulefunctiongroupbox import *
from gui.qgroupboxscrollarea import *
from gui.qbuildertreewidget import *

class ModuleMethods(object):
    
    def __init__(self, builder):
        self.builder = builder
        self.buildModuleMethods()
        self.buildMethodValuesView()
        
    def buildModuleMethods(_self):
        """Builds the module method frame and palette."""
        self = _self.builder
        #method palette splitter
        fr = QtGui.QWidget()
        lfr = QtGui.QVBoxLayout()
        lfr.setSpacing(0)
        lfr.setMargin(0)
        fr.setLayout(lfr)
        w = QVTKMethodTreeWidget(fr)
        fr.layout().addWidget(w)
        w.setColumnCount(2)
        
        labels = QtCore.QStringList()
        labels << self.tr("Method") << self.tr("Signature")
        w.setHeaderLabels(labels)
        w.header().setResizeMode(QtGui.QHeaderView.Interactive)
        w.header().setMovable(False)
        w.header().resizeSection(0,200)
        w.setRootIsDecorated(True)
        w.setSortingEnabled(False)
        w.setDragEnabled(True)
        self.vtkMethodPalette = w
        self.vtkModuleMethods = fr

    def buildMethodValuesView(_self):
        """
        Parameters
        ----------

        - parent : 'QtGui.QWidget'
        
        """
        self = _self.builder
        parent = self.vtkModuleMethods
        self.methodValuesArea = QVTKMethodScrollArea(self)
        parent.layout().addWidget(self.methodValuesArea)
            
        self.methodValuesArea.setAcceptDrops(True)
        #self.methodValuesArea.viewport().setAcceptDrops(True)

        self.connect(self.methodValuesArea, QtCore.SIGNAL("newMethod"),
                     self.addNewMethod)
        self.connect(self.methodValuesArea, QtCore.SIGNAL("deleteMethod(int)"),
                     self.deleteMethod)
        self.connect(self.methodValuesArea,
                     QtCore.SIGNAL("valuesToBeChanged"),
                     self.changeValues)

        sp = QtGui.QSizePolicy()
        sp.setHorizontalPolicy(QtGui.QSizePolicy.MinimumExpanding)
        sp.setVerticalPolicy(QtGui.QSizePolicy.MinimumExpanding)
        self.methodValuesArea.setSizePolicy(sp)

        

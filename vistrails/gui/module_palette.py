from PyQt4 import QtCore, QtGui, QtOpenGL
from qframebox import *
from qmodulefunctiongroupbox import *
from qgroupboxscrollarea import *
from qbuildertreewidget import *
import generate_module_tree

##################################################################

class ModulePalette(object):

    def __init__(self, builder):
        self.builder = builder
        self.buildModulePalette()

    def buildModulePalette(self):
        w = QVTKClassTreeWidget()
        w.setSortingEnabled(True)
        w.sortItems(0,QtCore.Qt.AscendingOrder)
        w.setColumnCount(2)
        labels = QtCore.QStringList()
        labels << "Name" << "Type"
        w.setHeaderLabels(labels)
        w.header().setResizeMode(QtGui.QHeaderView.Interactive)
        w.header().setMovable(False)
        w.header().resizeSection(0,230)
        w.header().resizeSection(1,50)
        w.setRootIsDecorated(True)
        w.setDragEnabled(True)

        w.allItems = []
        self.treeManager = generate_module_tree.GenerateModuleTree(w)
        self.treeManager.generateModuleHierarchy()

#        w.setMinimumHeight(600)
#        w.setMinimumWidth(400)

        sp = QtGui.QSizePolicy()
        sp.setHorizontalPolicy(QtGui.QSizePolicy.Fixed)
        sp.setVerticalPolicy(QtGui.QSizePolicy.Expanding)
        w.setSizePolicy(sp)

        return w

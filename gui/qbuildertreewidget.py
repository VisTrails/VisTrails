from PyQt4 import QtCore, QtGui, QtOpenGL
import pickle

################################################################################

class MyQTreeWidgetItem(QtGui.QTreeWidgetItem):
    def __init__(self,parent,labelList):
        self.index = None
        self.hideProtect = False
        QtGui.QTreeWidgetItem.__init__(self,parent,labelList)

    def protectFromHide(self):
        self.hideProtect = True
        p = self.parent()
        if p:
            self.treeWidget().setExpanded(self.index,True)
            p.protectFromHide()

    def unprotectFromHide(self):
        self.hideProtect = False

################################################################################

class QBuilderTreeWidget(QtGui.QTreeWidget):

    def __init__(self, parent=None):
        QtGui.QTreeWidget.__init__(self, parent)
        
    def unprotectAllItems(self):
        self.reset()
        for i in self.allItems:
            i.hideProtect = False
            self.expand(self.indexFromItem(i))

    def startDrag(self, event):
        if self.currentItem():
            parent = self.currentItem().parent()
            if parent:
                result = self.payload()
                mimeData = QtCore.QMimeData()
                mimeData.setText(result)
                drag = QtGui.QDrag(self)
                drag.setMimeData(mimeData)
                drag.start(QtCore.Qt.CopyAction)
            
    def showMatchedItems(self,text):
        items = self.findItems(text, QtCore.Qt.MatchContains | QtCore.Qt.MatchRecursive)
        for i in items:
            while i and not i.hideProtect:
                i.hideProtect = True
                i = i.parent()
        for i in self.allItems:
            self.setRowHidden(i.index.row(),i.index.parent(),not i.hideProtect)
            
   
################################################################################

class QVTKMethodTreeWidget(QBuilderTreeWidget):

    def __init__(self, parent=None):
        QBuilderTreeWidget.__init__(self, parent)
        self.allItems = []

    def payload(self):        
        parent = self.currentItem().parent()
        payload = ["Method", str(parent.text(0)),
                   str(self.currentItem().text(0)),
                   str(self.topLevelItem(0).text(0)),
                   str(self.currentItem().text(1))]
        return pickle.dumps(payload)


class QVTKRangeTreeWidget(QBuilderTreeWidget):

    def __init__(self, parent, builder):
        QBuilderTreeWidget.__init__(self, parent)
        self.builder = builder

    def payload(self):
        parent = self.currentItem().parent()
        payload = ["Range", str(parent.text(0)),
                   str(self.currentItem().text(0)),
                   self.builder.selectedModule,
                   str(self.currentItem().text(1))]
        return pickle.dumps(payload)

class QVTKClassTreeWidget(QBuilderTreeWidget):

    def __init__(self, parent=None):
        QBuilderTreeWidget.__init__(self, parent)
        self.allItems = []

    def payload(self):
        payload = ["Module", str(self.currentItem().text(0))]
        return pickle.dumps(payload)

################################################################################

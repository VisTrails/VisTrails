from PyQt4 import QtCore, QtGui, QtOpenGL

################################################################################

class QFrameBox(QtGui.QWidget):
    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self,parent)
        layout = QtGui.QVBoxLayout()
        layout.setSpacing(0)        
        layout.setMargin(0)
        layout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(layout)
        self.widget = None

    def validateLayout(self):
        self.setMinimumWidth(0)
        self.setMaximumWidth(16772980)
        self.setMinimumHeight(0)
        self.setMaximumHeight(16772980)
        self.scroll.setWidgetResizable(False)
        self.adjustSize()
        self.setMinimumHeight(self.height())
        self.setMaximumHeight(self.height())
        self.scroll.setWidgetResizable(True)
        self.update()

    def removeFunction(self,widget):
        self.layout().removeWidget(widget)
        self.layout().invalidate()
        self.validateLayout()
          
    def addFunction(self, widget):
        self.layout().addWidget(widget)
        self.layout().addStretch(1)
        self.layout().invalidate()
        self.validateLayout()

    def clear(self):
        #deleting the layout doesn't work
        #pyqt keeps saying that we are trying to add a layout to
        #a widget that already has one
        #need to remove all widgets by hand
        for c in self.children():
            if c.__class__ is not QtGui.QVBoxLayout:
                self.layout().removeWidget(c)
                c.deleteLater()
        self.layout().invalidate()
        self.setMinimumHeight(0)
        self.setMaximumHeight(0)
        self.update()

################################################################################

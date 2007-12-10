############################################################################
##
## Copyright (C) 2006-2007 University of Utah. All rights reserved.
##
## This file is part of VisTrails.
##
## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following to ensure GNU General Public
## Licensing requirements will be met:
## http://www.opensource.org/licenses/gpl-license.php
##
## If you are unsure which license is appropriate for your use (for
## instance, you are interested in developing a commercial derivative
## of VisTrails), please contact us at vistrails@sci.utah.edu.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################
"""
This module creates Widgets to handle Parameter Exploration in
VisTrails

QParameterExploration
"""
import thread
from PyQt4 import QtCore, QtGui, QtOpenGL
from core.param_explore import InterpolateDiscreteParam, ParameterExploration
from gui.common_widgets import QToolWindowInterface, MultiLineWidget
from gui.method_dropbox import QMethodDropBox, QMethodInputForm
from gui.theme import CurrentTheme
################################################################################

class QParameterExploration(QtGui.QWidget, QToolWindowInterface):
    """
    QParameterExploration provides interface to collect
    parameter information from the GUI and pass it to
    core.param_explore.ParameterExploration. This also takes
    responsibility to setup the GUI in the builder

    """
    def __init__(self, parent=None):
        """ QParameterExploration(parent: QWidget)
                                        -> QParameterExploration
        Generate tab labels
        
        """
        QtGui.QWidget.__init__(self, parent)
        self.setWindowTitle('Param Exploration')
        self.dimLabels = ['Dim %d' % (i+1) for i in xrange(4)]
        vLayout = QtGui.QVBoxLayout()
        vLayout.setSpacing(0)
        vLayout.setMargin(0)
        self.setLayout(vLayout)
        self.dimTab = QtGui.QTabWidget()
        for t in xrange(4):
            tab = QDimensionWidget()
            tab.paramEx = self
            self.dimTab.addTab(tab, self.dimLabels[t]+' (1)')
            self.connect(tab.methodList,
                         QtCore.SIGNAL("paramsAreaChanged"),
                         self.updateButton)
        vLayout.addWidget(self.dimTab)
        
        self.peButton = QtGui.QPushButton("Perform Exploration")
        self.peButton.setEnabled(False)
        vLayout.addWidget(self.peButton)
        self.connect(self.peButton, QtCore.SIGNAL('clicked()'),
                     self.startParameterExploration)
        self.controller = None
        
    def updateButton(self):
        """updateButton() -> None
        enable/disable peButton according to data to be explored 
        
        """
        enable = False
        for dim in xrange(self.dimTab.count()):
            tab = self.dimTab.widget(dim)
            if tab.methodList.vWidget.layout().count() > 0:
                enable = True
        self.peButton.setEnabled(enable)

    def clear(self):
        """ clear() -> None
        Clear all settings and leave the GUI empty
        
        """
        for dim in xrange(self.dimTab.count()):
            tab = self.dimTab.widget(dim)
            tab.methodList.vWidget.clear()
        
    def startParameterExploration(self):
        """ startParameterExploration() -> None
        Collects inputs from widgets and the builders to setup and
        start a parameter exploration
        
        """
        if (not self.controller) or (not self.controller.currentPipeline):
            return
        specs = []
        dimCount = 0
        for dim in xrange(self.dimTab.count()):
            tab = self.dimTab.widget(dim)
            stepCount = tab.sizeEdit.value()
            specsPerDim = []
            for i in xrange(tab.methodList.vWidget.layout().count()):
                c = tab.methodList.vWidget.layout().itemAt(i).widget()
                ranges = []
                for v in c.fields:
                    if v[0]=='String':
                        strCount = v[1].count()
                        strings = [str(v[1].item(i%strCount).text())
                                   for i in xrange(stepCount)]
                        ranges.append(strings)
                    else:                        
                        convert = {'Integer': int,
                                   'Float': float}
                        cv = convert[v[0]]
                        ranges.append((cv(v[1].text()),cv(v[2].text())))
                interpolator = InterpolateDiscreteParam(c.moduleId,
                                                        c.functionName(),
                                                        ranges,
                                                        stepCount)
                specsPerDim.append(interpolator)                
            specs.append(specsPerDim)
        p = ParameterExploration(specs)
        pipelineList = p.explore(self.controller.currentPipeline)
        vistrails = ()
        for pipeline in pipelineList:
            vistrails += ((self.controller.locator,
                           self.controller.currentVersion,
                           pipeline,
                           self.controller.currentPipelineView,
                           None),)
        self.controller.executeWorkflowList(vistrails)
            
class QDimensionWidget(QtGui.QWidget):
    """
    QDimensionWidget is the tab widget holding parameter info for a
    single dimension
    
    """
    def __init__(self, parent=None):
        """ QDimensionWidget(parant: QWidget) -> QDimensionWidget                             
        Initialize the tab with appropriate labels and connect all
        signals and slots
                             
        """
        QtGui.QWidget.__init__(self, parent)
        self.sizeLabel = QtGui.QLabel('&Step Count')
        self.sizeEdit = QtGui.QSpinBox()
        self.sizeEdit.setMinimum(1)        
        self.connect(self.sizeEdit,QtCore.SIGNAL("valueChanged(int)"),
                     self.stepCountChanged)
        self.sizeLabel.setBuddy(self.sizeEdit)
        
        sizeLayout = QtGui.QHBoxLayout()
        sizeLayout.addWidget(self.sizeLabel)
        sizeLayout.addWidget(self.sizeEdit)
        sizeLayout.addStretch(0)
        
        topLayout = QtGui.QVBoxLayout()
        topLayout.addLayout(sizeLayout)
        
        self.methodList = QMethodDropBox()
        self.methodList.vWidget.formType = QRangeFunctionGroupBox
        topLayout.addWidget(self.methodList)
        self.setLayout(topLayout)
        self.paramEx = None
        
    def stepCountChanged(self, count):
        """ stepCountChanged(count: int)        
        When the number step in this dimension is changed, notify and
        invalidate all of its children
        
        """
        idx = self.paramEx.dimTab.indexOf(self)
        self.paramEx.dimTab.setTabText(idx,
                                       self.paramEx.dimLabels[idx] +
                                       ' (' + str(count) + ')')
        for i in xrange(self.methodList.vWidget.layout().count()):
            child = self.methodList.vWidget.layout().itemAt(i).widget()
            for field in child.fields:
                if field[0]=='String':
                    child.updateStepCount(field[1].count())

class QRangeFunctionGroupBox(QMethodInputForm):
    def __init__(self, parent=None):
        QMethodInputForm.__init__(self, parent)
        self.function = None
        self.fields = []
  
    def parameterCount(self):
        return self.function.getNumParams()

    def type(self, paramId):
        return self.function.params[paramId].type

    def functionName(self):
        return self.function.name

    def stepCount(self):
        return self.parent().parent().parent().parent().sizeEdit.value()

    def updateStepCount(self, count):
        display = str(count)
        stepCount = self.stepCount()
        if count>stepCount:
            display = display + ' (Too many values)'
        if count<stepCount:
            display = display + ' (Need more values)'        
        self.el.setText(display)

    def updateFunction(self, function):
        self.function = function
        self.setTitle(function.name)
        gLayout = self.layout()
        self.elLabel = QtGui.QLabel("Count")
        gLayout.addWidget(self.elLabel,0,0)
        self.el = QtGui.QLineEdit(str(self.stepCount),self)
        self.el.setEnabled(False)
        gLayout.addWidget(self.el,0,1)
        self.lStart = QtGui.QLabel("Start",self)
        gLayout.addWidget(self.lStart,1,1)
        self.lEnd = QtGui.QLabel("End",self)
        gLayout.addWidget(self.lEnd,1,2)

        row = 2
        for p in function.params:
            self.createField(p, row)
            row += 1
        self.update()

    def createField(self, p, row):
        def dorange(Validator):
            self.lStart.setVisible(True)
            self.lEnd.setVisible(True)
            self.elLabel.setVisible(False)
            self.el.setVisible(False)

            valueEdit1 = QtGui.QLineEdit(p.strValue, self)
            gLayout.addWidget(valueEdit1, row, 1)
            valueEdit2 = QtGui.QLineEdit(p.strValue, self)
            gLayout.addWidget(valueEdit2, row, 2)
            self.fields.append((p.type, valueEdit1, valueEdit2))
            if Validator:
                valueEdit1.setValidator(Validator(self))
                valueEdit2.setValidator(Validator(self))

        def dolist(dummy):
           self.lStart.setVisible(False)
           self.lEnd.setVisible(False)
           self.elLabel.setVisible(True)
           self.el.setVisible(True)
           self.el.setText(str(0))
           wgt = QRangeString(row, self)
           gLayout.addWidget(wgt, row, 1, 1, 2)
           self.fields.append((p.type,wgt.listWidget))
           self.connect(wgt.listWidget,QtCore.SIGNAL("changed(int)"),self.updateStepCount)
           self.updateStepCount(wgt.listWidget.count())
        doit = {'Integer': [dorange,QtGui.QIntValidator],
                'Float': [dorange,QtGui.QDoubleValidator],
                'String': [dolist, None]}
        gLayout = self.layout()
        lbl = QtGui.QLabel(QtCore.QString(p.type),self)
        gLayout.addWidget(lbl, row, 0)
        doit[p.type][0](doit[p.type][1])

class QRangeString(QtGui.QFrame):

    def __init__(self, row, parent=None):
        QtGui.QFrame.__init__(self, parent)
        self.setObjectName('RangeString')
        layout = QtGui.QVBoxLayout()
        self.groupBox = parent
        self.setLayout(layout)
        self.frame = self # hack to make qvaluelineedit happy
        self.strings = []
        self.row = row
        self.setLineEdits()
    
    def setLineEdits(self):
        self.setUpdatesEnabled(False)
        hl = QtGui.QHBoxLayout()
        
        self.lineEdit = MultiLineWidget('','String', self, multiLines=True)
        hl.addWidget(self.lineEdit)
        self.addBtn = QtGui.QToolButton()
        self.addBtn.setToolTip(self.tr("Add string"))
        self.addBtn.setIcon(CurrentTheme.ADD_STRING_ICON)
        self.addBtn.setIconSize(QtCore.QSize(16,16))
        self.connect(self.addBtn, QtCore.SIGNAL("clicked()"), self.addString)
        hl.addWidget(self.addBtn)
        hl.setSpacing(0)
        hl.setMargin(0)
        self.layout().addLayout(hl)
        self.layout().setSpacing(0)
        self.layout().setMargin(0)
        
        self.listWidget = QStringListWidget(self.groupBox)        
        vl = QtGui.QVBoxLayout()
        vl.setSpacing(0)
        vl.setMargin(0)

        self.upBtn = QtGui.QToolButton()
        self.upBtn.setToolTip(self.tr("Move up"))
        self.upBtn.setIcon(CurrentTheme.UP_STRING_ICON)
        self.upBtn.setIconSize(QtCore.QSize(16,16))
        self.connect(self.upBtn, QtCore.SIGNAL("clicked()"), self.moveUp)
        vl.addWidget(self.upBtn)

        self.downBtn = QtGui.QToolButton()
        self.downBtn.setToolTip(self.tr("Move down"))
        self.downBtn.setIcon(CurrentTheme.DOWN_STRING_ICON)
        self.downBtn.setIconSize(QtCore.QSize(16,16))
        self.connect(self.downBtn, QtCore.SIGNAL("clicked()"), self.moveDown)
        vl.addWidget(self.downBtn)

        hl2 = QtGui.QHBoxLayout()
        hl2.setSpacing(0)
        hl2.setMargin(0)
        hl2.addWidget(self.listWidget)
        hl2.addLayout(vl)
        self.parent().layout().addLayout(hl2,self.row + 1, 1, 1, 2)
        
        
        self.setUpdatesEnabled(True)
        self.parent().adjustSize()
        if self.parent().parent().layout():
            self.parent().parent().layout().invalidate()

    def addString(self):
        if not self.lineEdit.text().isEmpty():
            slist = self.lineEdit.text().split(",",QtCore.QString.SkipEmptyParts)
            self.listWidget.addText(slist)

    def moveUp(self):
        row = self.listWidget.currentRow()
        if row > 0:
            item = self.listWidget.takeItem(row)
            self.listWidget.insertItem(row-1,item)
            self.listWidget.setCurrentRow(row-1)

    def moveDown(self):
        row = self.listWidget.currentRow()
        if row < self.listWidget.count()-1:
            item = self.listWidget.takeItem(row)
            self.listWidget.insertItem(row+1,item)
            self.listWidget.setCurrentRow(row+1)
    
    def updateMethod(self):
        pass

class QStringListWidget(QtGui.QListWidget):

    def __init__(self,parent=None):
        QtGui.QListWidget.__init__(self,parent)
        

    def keyPressEvent(self, event):
        k = event.key()
        s = event.modifiers()
        if (k == QtCore.Qt.Key_Delete or k == QtCore.Qt.Key_Backspace) and s == QtCore.Qt.NoModifier:
            if self.currentRow() >= 0:
                self.takeItem(self.currentRow())
                self.updateCount()
        elif (k == QtCore.Qt.Key_Delete or k == QtCore.Qt.Key_Backspace) and s & QtCore.Qt.ControlModifier:
            self.clear()
            self.updateCount()
        else:
            QtGui.QListWidget.keyPressEvent(self,event)
            # super(QStringListWidget, self).keyPressEvent(event)

    def sizeHint(self):
        #Return an invalid sizeHint
        return QtCore.QSize()

    def addText(self,slist):
        self.addItems(slist)
        self.updateCount()

    def updateCount(self):
        self.emit(QtCore.SIGNAL("changed(int)"),self.count())

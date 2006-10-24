from PyQt4 import QtCore, QtGui, QtOpenGL
from qframebox import *
from qmodulefunctiongroupbox import *
from qgroupboxscrollarea import *
from qbuildertreewidget import *

import pipeline_analyzer

class BulkChanges(object):
    """BulkChanges is a class that encapsulates all the UI aspects of the
Bulk Changes behavior (aka parameter exploration)"""
    def __init__(self, builder):
        self.builder = builder
        self.dimMethods = None
        self.dimLabels = ['Dim %d' % (i+1) for i in range(4)]

    def clear(self):
        #self.methodRangesArea.clear()
        pass

    def bulkChangeClicked(self):
        convert = {'Integer': int,
                   'Float': float}
        def donumber(stepCount, v):
            cv = convert[v[0]]
            mnParam = cv(v[1].text())
            mxParam = cv(v[2].text())
            rng = mxParam - mnParam
            thisparam = []
            for i in range(stepCount):
                if stepCount>1: t = i/float(stepCount-1)
                else: t = 0
                thisparam.append(cv(mnParam + rng * t))
            return thisparam
        def dostring(stepCount, v):
            result = []
            for i in range(stepCount):
                result.append(str(v[1].item(i%v[1].count()).text().toLatin1()))
            return result

        doit = {'Integer': donumber,
                'Float': donumber,
                'String': dostring}
        specs = []
        dimCount = 0
        stepCounts = []
        for dim in range(self.dimTab.count()):
            tab = self.dimTab.widget(dim)
            stepCount = tab.sizeEdit.value()
            dimSpecs = []
            for c in tab.methodList._children:
                paramValues = [doit[v[0]](stepCount, v) for v in c.fields]
                params = zip(*paramValues) # This is too smart for my own good - it's a transpose
                dimSpecs.append(pipeline_analyzer.InterpolateDiscreteParam(c.selectedModule,
                                                                           c.functionName(),
                                                                           params))
            specs.append(dimSpecs)
            if dimSpecs: stepCounts.append(stepCount)
            else: stepCounts.append(1)
                
        p = pipeline_analyzer.ParameterStudy()
        controller = self.builder.controllers[self.builder.currentControllerName]
        bulk = p.parameterStudyExplicit(controller.currentPipeline, stepCounts, specs)
        vistrails = ()
        for pipeline in bulk[1]:
            vistrails += ((controller.name,
                           controller.currentVersion,
                           pipeline,
                           controller.currentPipelineView,
                           None),)
        import thread
        thread.start_new_thread(controller.executeWorkflow, (vistrails,))
#         self.builder.spreadsheet.setBulkVistrail(controller,
#                                                  controller.vistrail,
#                                                  controller.currentVersion,
#                                                  controller.currentPipeline,
#                                                  bulk,
#                                                  controller.spreadsheet.getCurrentSheet().SelectedCells)

    def buildPalette(self):
        frame = QtGui.QWidget()
        layoutFrame = QtGui.QVBoxLayout()
        layoutFrame.setSpacing(0)
        layoutFrame.setMargin(0)
        frame.setLayout(layoutFrame)
        self.buildTreeWidget(frame)
        self.buildMethodRangesView(frame)
#        self.ToSelectedCell = QtGui.QCheckBox("Start from a selected cell", frame)
#        layoutFrame.addWidget(self.ToSelectedCell)
        createButton = QtGui.QPushButton("Bulk Change")
        frame.layout().addWidget(createButton)
        self.builder.connect(createButton, QtCore.SIGNAL("clicked()"),
                             self.bulkChangeClicked)
        return frame
    
    def buildTreeWidget(self, frame):
        """
        Parameters
        ----------

        - frame : 'QtGui.QWidget'
        
        """
        x = QVTKRangeTreeWidget(frame, self.builder)
        frame.layout().addWidget(x)
        x.setColumnCount(2)
        labels = QtCore.QStringList()
        labels << self.builder.tr("Method") << self.builder.tr("Signature")
        x.setHeaderLabels(labels)
        x.header().setResizeMode(QtGui.QHeaderView.Interactive)
        x.header().setMovable(False)
        x.header().resizeSection(0,200)
        x.setRootIsDecorated(True)
        x.setSortingEnabled(False)
        x.setDragEnabled(True)
        self.builder.vtkParameterExplorationTreeWidget = x

    def buildMethodRangesView(self, frame):
        """
        Parameters
        ----------

        - frame : 'QtGui.QWidget'
        
        """
        self.dimTab = QtGui.QTabWidget()        
        for t in range(4):
            tabWidget = QDimensionWidget(self)
            self.dimTab.addTab(tabWidget, self.dimLabels[t]+' (1)')
        
        frame.layout().addWidget(self.dimTab)
        
class QDimensionWidget(QtGui.QWidget):
    def __init__(self, bulkChanges, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.bulkChanges = bulkChanges        
        self.sizeLabel = QtGui.QLabel('&Step Count')
        self.sizeEdit = QtGui.QSpinBox()
        self.sizeEdit.setMinimum(1)        
        self.connect(self.sizeEdit,QtCore.SIGNAL("valueChanged(int)"),self.stepCountChanged)
        self.sizeLabel.setBuddy(self.sizeEdit)
        
        sizeLayout = QtGui.QHBoxLayout()
        sizeLayout.addWidget(self.sizeLabel)
        sizeLayout.addWidget(self.sizeEdit)
        sizeLayout.addStretch(0)
        
        self.methodList = QVTKRangeScrollArea(self.bulkChanges.builder)
        self.methodList.setAcceptDrops(True)
        
        topLayout = QtGui.QVBoxLayout()
        topLayout.addLayout(sizeLayout)
        topLayout.addWidget(self.methodList)

        self.setLayout(topLayout)
        
    def stepCountChanged(self, count):
        idx = self.bulkChanges.dimTab.indexOf(self)
        self.bulkChanges.dimTab.setTabText(idx, self.bulkChanges.dimLabels[idx] + ' (' + str(count) + ')')
        for child in self.methodList._children:
            for field in child.fields:
                if field[0]=='string':
                    child.updateStepCount(field[1].count())

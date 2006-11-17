"""
This module creates Widgets to handle Parameter Exploration in
VisTrails
"""
import thread
from PyQt4 import QtCore, QtGui, QtOpenGL
from core.param_explore import InterpolateDiscreteParam, ParameterExploration
from gui.qbuildertreewidget import QVTKRangeTreeWidget
from gui.qgroupboxscrollarea import QVTKRangeScrollArea
################################################################################

class ParameterExplorationManager(object):
    """
    ParameterExplorationManager provides interface to collect
    parameter information from the GUI and pass it to
    core.param_explore.ParameterExploration. This also takes
    responsibility to setup the GUI in the builder

    """
    def __init__(self, builder):
        """ ParameterExplorationManager(builder: QBuilder)
                                        -> ParameterExplorationManager
        Store the builder instance and generate tab labels
        """
        self.builder = builder
        self.dimLabels = ['Dim %d' % (i+1) for i in range(4)]

    def clear(self):
        """ clear() -> None
        Clear all settings and leave the GUI empty
        
        """
        for dim in range(self.dimTab.count()):
            tab = self.dimTab.widget(dim)
            tab.methodList.clear()
        

    def startParameterExploration(self):
        """ startParameterExploration() -> None
        Collects inputs from widgets and the builders to setup and
        start a parameter exploration
        
        """
        specs = []
        dimCount = 0
        for dim in range(self.dimTab.count()):
            tab = self.dimTab.widget(dim)
            stepCount = tab.sizeEdit.value()
            specsPerDim = []
            for c in tab.methodList._children:
                ranges = []
                for v in c.fields:
                    if v[0]=='String':
                        strCount = v[1].count()
                        strings = [str(v[1].item(i%strCount).text().toLatin1())
                                   for i in range(stepCount)]
                        ranges.append(strings)
                    else:                        
                        convert = {'Integer': int,
                                   'Float': float}
                        cv = convert[v[0]]
                        ranges.append((cv(v[1]),cv(v[2])))
                interpolator = InterpolateDiscreteParam(c.selectedModule,
                                                        c.functionName(),
                                                        ranges,
                                                        stepCount)
                specsPerDim.append(interpolator)                
            specs.append(specsPerDim)                
        p = ParameterExploration(specs)
        controllerName = self.builder.currentControllerName
        controller = self.builder.controllers[controllerName]
        pipelineList = p.explore(controller.currentPipeline)
        vistrails = ()
        for pipeline in pipelineList:
            vistrails += ((controllerName,
                           controller.currentVersion,
                           pipeline,
                           controller.currentPipelineView,
                           None),)
        thread.start_new_thread(controller.executeWorkflow, (vistrails,))

    def buildPalette(self):
        """ buildPalette() -> None
        Construct the paramter exploration widgets in the builder
        
        """
        frame = QtGui.QWidget()
        layoutFrame = QtGui.QVBoxLayout()
        layoutFrame.setSpacing(0)
        layoutFrame.setMargin(0)
        frame.setLayout(layoutFrame)
        self.buildTreeWidget(frame)
        self.buildMethodRangesView(frame)
        createButton = QtGui.QPushButton("Bulk Change")
        frame.layout().addWidget(createButton)
        self.builder.connect(createButton, QtCore.SIGNAL("clicked()"),
                             self.startParameterExploration)
        return frame
    
    def buildTreeWidget(self, frame):
        """ buildTreeWidget(frame: QWidget) -> None
        Build the method tree widget to drag to the parameter exploration area
        
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
        """ buildMethodRangesView(frame: QWidget) -> None
        Build the scroll area where methods can be dropped to
        
        """
        self.dimTab = QtGui.QTabWidget()        
        for t in range(4):
            tabWidget = QDimensionWidget(self)
            self.dimTab.addTab(tabWidget, self.dimLabels[t]+' (1)')        
        frame.layout().addWidget(self.dimTab)
        
class QDimensionWidget(QtGui.QWidget):
    """
    QDimensionWidget is the tab widget holding parameter info for a
    single dimension
    
    """
    def __init__(self, bulkChanges, parent=None):
        """ QDimensionWidget(bulkChanges: ParameterExplorationManager,
                             parant: QWidget) -> QDimensionWidget                             
        Initialize the tab with appropriate labels and connect all
        signals and slots
                             
        """
        QtGui.QWidget.__init__(self, parent)
        self.bulkChanges = bulkChanges        
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
        
        self.methodList = QVTKRangeScrollArea(self.bulkChanges.builder)
        self.methodList.setAcceptDrops(True)
        
        topLayout = QtGui.QVBoxLayout()
        topLayout.addLayout(sizeLayout)
        topLayout.addWidget(self.methodList)

        self.setLayout(topLayout)
        
    def stepCountChanged(self, count):
        """ stepCountChanged(count: int)        
        When the number step in this dimension is changed, notify and
        invalidate all of its children
        
        """
        idx = self.bulkChanges.dimTab.indexOf(self)
        self.bulkChanges.dimTab.setTabText(idx,
                                           self.bulkChanges.dimLabels[idx] +
                                           ' (' + str(count) + ')')
        for child in self.methodList._children:
            for field in child.fields:
                if field[0]=='string':
                    child.updateStepCount(field[1].count())

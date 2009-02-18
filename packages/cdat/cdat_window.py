from PyQt4 import QtCore, QtGui
from packages.spreadsheet.spreadsheet_controller import spreadsheetController
from packages.spreadsheet.spreadsheet_event import DisplayCellEvent
from cdat_cell import QCDATWidget
import cdms2
import core.modules.module_registry
import core.modules.vistrails_module
from logging import debug, warn
from core.vistrail.connection import Connection
from core.vistrail.port import Port
import os
import api

def setup_open_call(filename, variable, plotType, axes):
    """ hack to see if the `api' module works better."""
    cdat_id = "edu.utah.sci.vistrails.cdat"

#    api.get_current_vistrail()

    cdat_package = "edu.utah.sci.vistrails.cdat"
    # Create all our modules.
    m_open = api.add_module(0,400, cdat_id, 'open', "cdms2")
    m_call = api.add_module(10,300, cdat_id, '__call__', "cdms2|dataset")
    m_quickplot = api.add_module(0,200, cdat_package, 'quickplot', 'cdat')

    reg = api.get_module_registry()

    debug("giving fn of: %s" % filename)
    api.get_current_controller().update_function(m_open,'uri', [filename])
    api.get_current_controller().update_function(m_quickplot,'plot',
                                                 [plotType])
    api.get_current_controller().update_function(m_quickplot,'axes', [axes])
    api.get_current_controller().update_function(m_call,'id',
                                                 [variable])

    # get all the ports so we can ...
    open_out = reg.get_port_spec(cdat_id, 'open', 'cdms2', 'dataset', 'output')
    call_in = reg.get_port_spec(cdat_id, '__call__', 'cdms2|dataset',
                                'cdmsfile', 'input')
    call_out = reg.get_port_spec(cdat_id, '__call__', 'cdms2|dataset',
                                 'variable', 'output')

    quickplot_in_var = reg.get_port_spec(cdat_package, 'quickplot', 'cdat',
                                         'variable', 'input')
    quickplot_in_ds = reg.get_port_spec(cdat_package, 'quickplot', 'cdat',
                                        'dataset', 'input')
    quickplot_in_cvs = reg.get_port_spec(cdat_package, 'quickplot', 'cdat',
                                         'plot', 'input')

    # ... connect them!
    cnxns = (
        (m_open,open_out, m_call,call_in),
        (m_call,call_out, m_quickplot,quickplot_in_ds),
    )
#        (m_isoline,isoline_cvs_out, m_quickplot,quickplot_in_cvs)
#        (m_isofill,isofill_out, m_isoline,isoline_in2)
#        (m_call,call_out, m_quickplot,quickplot_in_ds),
    [api.add_connection(c[0].id,c[1], c[2].id,c[3]) for c in cnxns]

    api.switch_to_pipeline_view()
        
class QCDATWindow(QtGui.QWidget):

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setWindowTitle('CDAT')
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)
        vsplitter  = QtGui.QSplitter(QtCore.Qt.Vertical)
        fileWidget = QLabeledWidgetContainer(QCDATFileWidget(), 'FILE VARIABLES')
        vsplitter.addWidget(fileWidget)
        definedVar = QLabeledWidgetContainer(QDefinedVariable(), 'DEFINED VARIABLES')
        vsplitter.addWidget(definedVar)
            
        hsplitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
        hsplitter.addWidget(vsplitter)
    
        varView = QLabeledWidgetContainer(QVariableView(fileWidget.widget), 'PLOTTING')
        hsplitter.addWidget(varView)
        hsplitter.setStretchFactor(1, 1)
        layout.addWidget(hsplitter)

    def sizeHint(self):
        return QtCore.QSize(1024, 600)
        

class QFileDialogWidget(QtGui.QFileDialog):
    
    def __init__(self, parent=None):
        QtGui.QFileDialog.__init__(self, parent, QtCore.Qt.Widget)
        self.setModal(False)
        self.setSizeGripEnabled(False)
        self.setFileMode(QtGui.QFileDialog.ExistingFile)
        self.setLabelText(QtGui.QFileDialog.LookIn, 'Directory')
        self.setSidebarUrls([
                QtCore.QUrl('file://')
                ])

        gridLayout = self.findChild(QtGui.QGridLayout, 'gridLayout')
        if gridLayout:
            gridLayout.setMargin(0)
            gridLayout.setVerticalSpacing(0)
            gridLayout.setColumnStretch(1, 1)
            hBoxLayout = gridLayout.itemAtPosition(0, 1).layout()
            if hBoxLayout:
                hBoxLayout.setSpacing(0)
        
        # Hide the Back and Forward button
        backButton = self.findChild(QtGui.QToolButton, 'backButton')
        if backButton: backButton.hide()
        forwardButton = self.findChild(QtGui.QToolButton, 'forwardButton')
        if forwardButton: forwardButton.hide()            
        
        # Hide the File Name indicators
        fileNameLabel = self.findChild(QtGui.QLabel, 'fileNameLabel')
        if fileNameLabel: fileNameLabel.hide()
        fileNameEdit = self.findChild(QtGui.QLineEdit, 'fileNameEdit')
        if fileNameEdit: fileNameEdit.hide()

        # Hide the File Type indicators
        fileTypeLabel = self.findChild(QtGui.QLabel, 'fileTypeLabel')
        if fileTypeLabel: fileTypeLabel.hide()
        fileTypeCombo = self.findChild(QtGui.QComboBox, 'fileTypeCombo')
        if fileTypeCombo: fileTypeCombo.hide()

        # Hide the dialog buttons
        buttonBox = self.findChild(QtGui.QDialogButtonBox, 'buttonBox')
        buttonBox.hide()

        # Adjust the sidebar width
        splitter = self.findChild(QtGui.QSplitter, 'splitter')
        splitter.setSizes([0, 1])

        # Simplify the Details view to List View
        stackedWidget = splitter.widget(1).findChild(QtGui.QStackedWidget, 'stackedWidget')
        listView = stackedWidget.widget(0).findChild(QtGui.QListView, 'listView')
        listView.setAlternatingRowColors(True)
        listView.setWrapping(False)
        self.setViewMode(QtGui.QFileDialog.List)

    def done(self, result):
        pass

    def sizeHint(self):
        return QtCore.QSize(384, 150)

class QCDATFileWidget(QtGui.QWidget):

    FILTER = "CDAT data (*.cdms *.ctl *.dic *.hdf *.nc *.xml)"

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        
        # Local variables
        self.cdmsFile = None

        # Start the layout
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)
        layout.setMargin(0)

        self.fileDialog = QFileDialogWidget()
        self.fileDialog.setNameFilter(QCDATFileWidget.FILTER)
        layout.addWidget(self.fileDialog)

        # A shared layout of the bottom half
        vbox = QtGui.QVBoxLayout()
        vbox.setMargin(0)
        vbox.setSpacing(0)
        layout.addLayout(vbox)
        self.fileVarLayout = vbox
        
        # Create the bottom horizontal indicator
        hbox = QtGui.QHBoxLayout()
        
        self.drawerButton = QtGui.QToolButton()
        self.drawerButton.setArrowType(QtCore.Qt.UpArrow)
        self.drawerButton.setAutoRaise(True)
        self.drawerButton.setIconSize(QtCore.QSize(8, 8))
        hbox.addWidget(self.drawerButton)
        
        hline = QtGui.QFrame()
        hline.setFrameStyle(QtGui.QFrame.HLine | QtGui.QFrame.Sunken)
        hbox.addWidget(hline)

        self.connect(self.drawerButton, QtCore.SIGNAL('clicked(bool)'),
                     self.toggleFileDialog)

        vbox.addLayout(hbox)
        
        # Create the file name box
        grid = QtGui.QGridLayout()
        grid.setHorizontalSpacing(10)
        vbox.addLayout(grid)

        # First line: File
        fileNameLabel = QtGui.QLabel('File')
        grid.addWidget(fileNameLabel)

        hbox = QtGui.QHBoxLayout()
        hbox.setSpacing(6)
        self.fileNameEdit = QtGui.QLineEdit()
        hbox.addWidget(self.fileNameEdit, 1)

        self.fileSelectButton = QtGui.QToolButton()
        self.fileSelectButton.setText('...')
        hbox.addWidget(self.fileSelectButton)
        
        grid.addLayout(hbox, 0, 1)

        # Second line: Var
        varNameLabel = QtGui.QLabel('Variable')
        grid.addWidget(varNameLabel, 1, 0)

        hbox = QtGui.QHBoxLayout()
        hbox.setSpacing(6)
        
        self.varCombo = QtGui.QComboBox()
        self.varCombo.setMinimumContentsLength(10)
        hbox.addWidget(self.varCombo, 1)
        
        self.defineVarButton = QtGui.QPushButton('&Define')
        hbox.addWidget(self.defineVarButton)
        
        grid.addLayout(hbox, 1, 1)

        # Connect signals
        self.connect(self.fileDialog, QtCore.SIGNAL('filesSelected(const QStringList&)'),
                     self.filesSelected)
        self.connect(self.fileNameEdit, QtCore.SIGNAL('returnPressed()'),
                     self.updateCDMSFile)
        self.connect(self.fileSelectButton, QtCore.SIGNAL('clicked(bool)'),
                     self.openSelectFileDialog)
        self.connect(self.varCombo, QtCore.SIGNAL('currentIndexChanged(const QString&)'),
                     self.variableChanged)
        self.connect(self.defineVarButton, QtCore.SIGNAL('clicked(bool)'),
                     self.defineVariable)

        # Init the widget with its file dialog hidden
        self.fileDialog.hide()
        self.setFileName('/home/hvo/src/CDAT/Packages/dat/clt.nc')
        self.varCombo.setCurrentIndex(1)

    def updateSizeConstraints(self):
        isDialogVisible = self.fileDialog.isVisible()
        if isDialogVisible:
            self.drawerButton.setArrowType(QtCore.Qt.UpArrow)
            self.setMaximumHeight(16777215)
        else:
            self.drawerButton.setArrowType(QtCore.Qt.DownArrow)
            self.setMaximumHeight(self.fileVarLayout.contentsRect().height())
        self.fileSelectButton.setVisible(not isDialogVisible)

    def toggleFileDialog(self, ignored=False):
        self.fileDialog.setVisible(not self.fileDialog.isVisible())
        self.updateSizeConstraints()

    def showEvent(self, e):
        self.updateSizeConstraints()
        self.variableChanged(self.varCombo.currentText())

    def setFileName(self, fn):
        self.fileNameEdit.setText(fn)
        self.updateCDMSFile()

    def updateCDMSFile(self):
        fn = str(self.fileNameEdit.text())
        fi = QtCore.QFileInfo(fn)
        if fi.exists():
            self.fileDialog.setDirectory(fi.dir())
            self.cdmsFile = cdms2.open(fn)
        else:
            self.cdmsFile = None
        self.updateVariableList()

    def filesSelected(self, files):
        if files.count()>0:
            self.setFileName(files[0])
            
    def updateVariableList(self):
        self.varCombo.clear()
        if self.cdmsFile!=None:
            # Add Variables sorted based on their dimensions
            curDim = -1
            for (dim, varId) in sorted([(len(var.listdimnames()), var.id)
                                          for var in self.cdmsFile.variables.itervalues()]):
                if dim!=curDim:
                    curDim = dim
                    count = self.varCombo.count()
                    self.varCombo.insertSeparator(count)
                    self.varCombo.model().item(count, 0).setText('%dD VARIABLES' % dim)
                var = self.cdmsFile.variables[varId]
                varName = var.id + ' ' + str(var.shape) + ' ['
                if hasattr(var, 'long_name'):
                    varName += var.long_name
                if var.units!='':
                    if varName[-1]!='[': varName += ' '
                    varName += var.units
                varName += ']'
                self.varCombo.addItem(varName, QtCore.QVariant(QtCore.QStringList(['variables', var.id])))

            # Add Axis List
            count = self.varCombo.count()
            self.varCombo.insertSeparator(count)
            self.varCombo.model().item(count, 0).setText('AXIS LIST')
            for axis in self.cdmsFile.axes.itervalues():
                axisName = axis.id + " (" + str(len(axis)) + ") - [" + axis.units + ":  (" + str(axis[0]) + ", " + str(axis[-1]) + ")]"                
                self.varCombo.addItem(axisName, QtCore.QVariant(QtCore.QStringList(['axes', axis.id])))

            # By default, not selecting anything
            self.varCombo.setCurrentIndex(-1)

    def openSelectFileDialog(self):
        file = QtGui.QFileDialog.getOpenFileName(self, 'Open CDAT data file...',
                                                 self.fileDialog.directory().absolutePath(),
                                                 QCDATFileWidget.FILTER + ';;All files (*.*)')
        if not file.isNull():
            self.setFileName(file)

    def variableChanged(self, varName):
        self.defineVarButton.setEnabled(not varName.isNull())
        self.emit(QtCore.SIGNAL('variableChanged'), self.getCDMSFile(), self.getCDMSVariable())

    def defineVariable(self):
        print 'Define Variable: not yet implemented'

    def getCDMSFile(self):
        return self.cdmsFile

    def getCDMSVariable(self):
        if self.cdmsFile!=None:
            data = self.varCombo.itemData(self.varCombo.currentIndex()).toStringList()
            if data.count()>0:
                return getattr(self.cdmsFile, str(data[0]))[str(data[1])]
        return None
        

class QLabeledWidgetContainer(QtGui.QWidget):

    def __init__(self, widget, label='', parent=None):
        QtGui.QWidget.__init__(self, parent)
        
        vbox = QtGui.QVBoxLayout()
        vbox.setMargin(0)
        
        self.label = QtGui.QLabel(label)
        self.label.setAutoFillBackground(True)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Raised)
        vbox.addWidget(self.label, 0)

        if widget!=None:
            self.widget = widget
        else:
            self.widget = QtGui.QWidget()
        vbox.addWidget(self.widget, 1)
        
        self.setLayout(vbox)

    def event(self, e):
        if e.type()==76:#QtCore.QEvent.LayoutRequest:
            self.setMaximumHeight(min(self.label.height()+self.layout().spacing()+
                                      self.widget.maximumHeight(), 16777215))
        return False

class QDefinedVariable(QtGui.QWidget):

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        vbox = QtGui.QVBoxLayout()
        vbox.setMargin(0)

        self.createToolbar()
        vbox.addWidget(self.toolBar)

        self.varList = QtGui.QListWidget()
        self.varList.setAlternatingRowColors(True)
        vbox.addWidget(self.varList)
        
        self.setLayout(vbox)

    def createToolbar(self):
        ICONPATH = os.path.join(cdms2.__path__[0], '..', '..', '..', '..', 'bin')
        self.toolBar = QtGui.QToolBar()
        self.toolBar.setIconSize(QtCore.QSize(16, 16))
        actionInfo = [
            ('edit_20.gif', 'Edit (in memory) selected defined variable.'),
            ('save_20.gif', 'Save selected defined variable to a netCDF file.'),
            ('info_20.gif', 'Display selected defined variable information.'),
            ('editdelete_20.gif', 'Move selected defined variable(s) to trashcan for disposal.'),
            ('recycle_20.gif', 'Move [ALL] defined variables to trashcan for disposal.'),
            ('log_20.gif', 'Logged information about the defined variables.'),
            ('trashcan_empty_20.gif', 'Defined variable items that can be disposed of permanetly or restored.'),
            ]
        for info in actionInfo:
            icon = QtGui.QIcon(os.path.join(ICONPATH, info[0]))
            action = self.toolBar.addAction(icon, '')
            action.setStatusTip(info[1])
            action.setToolTip(info[1])
        self.toolBar.addSeparator()

        self.opButton = QtGui.QToolButton()
        self.opButton.setText('Ops')
        
        # Operations Menu
        menu = QtGui.QMenu(self)
        grid = QtGui.QGridLayout()
        grid.setMargin(0)
        grid.setSpacing(0)
        menu.setLayout(grid)
        opDefs =[
            ['Add a number or two (or more)\nselected Defined Variables.\n(Can be used as "or")','add.gif','add'],
            ['Subtract a number or two (or more)\nselected Defined Variables.','subtract.gif','subtract'],
            ['Multiply a number or two (or more)\nselected Defined Variables.\n(Can be used as "and")','multiply.gif','multiply'],
            ['Divide a number or two (or more)\nselected Defined Variables.','divide.gif','divide'],
            ['"Grows" variable 1 and variable 2 so that they end up having the same dimensions\n(order of variable 1 plus any extra dims)','grower.gif','grower'],
            ['Spatially regrid the first selected Defined Variable\nto the second selected Defined Variable.','regrid.gif','regrid'],
            ['Mask variable 2 where variable 1 is "true".','mask.gif','mask'],
            ['Get variable mask','getmask.gif','getmask'],
            ['Return true where variable 1 is less than variable 2 (or number)','less.gif','less'],
            ['Return true where variable 1 is greater than variable 2 (or number)','greater.gif','greater'],
            ['Return true where variable 1 is equal than variable 2 (or number)','equal.gif','equal'],
            ['Return not of variable','not.gif','not'],
            ['Compute the standard deviation\n(over first axis)','std.gif','std'],
            ['Power (i.e., x ** y) of the most recently\nselected two Defined Variables, where\nx = variable 1 and y = variable 2 or float number.','power.gif','power'],
            ['Exp (i.e., e ** x) of the most recently\nselected Defined Variable.','exp.gif','exp'],
            ['Log (i.e., natural log) of the most recently\nselected Defined Variable.','mlog.gif','log'],
            ['Base10 (i.e., 10 ** x) of the most recently\nselected Defined Variable.','base10.gif','base10'],
            ['Log10 (i.e., log base 10) of the most\nrecently selected Defined Variable. ','mlog10.gif','log10'],
            ['Inverse (i.e., 1/x) of the most recently\nselected Defined Variable.','inverse.gif','inverse'],
            ['Abs (i.e., absolute value of x) of the most\nrecently selected Defined Variable.','fabs.gif','fabs'],
            ['Sine (i.e., sin) of the most recently\nselected Defined Variable.','sin.gif','sin'],
            ['Hyperbolic sine (i.e., sinh) of the most recently\nselected Defined Variable.','sinh.gif','sinh'],
            ['Cosine (i.e., cos) of the most recently\nselected Defined Variable.','cos.gif', 'cos'],
            ['Hyperbolic cosine (i.e., cosh) of the most recently\nselected Defined Variable.','cosh.gif','cosh'],
            ['Tangent (i.e., tan) of the most recently\nselected Defined Variable.','tan.gif','tan'],
            ['Hyperbolic tangent (i.e., tanh) of the most recently\nselected Defined Variable.','tanh.gif','tanh'],
            ]
        self.opActions = []
        for i in xrange(len(opDefs)):
            action = QtGui.QAction(QtGui.QIcon(os.path.join(ICONPATH, opDefs[i][1])), opDefs[i][2], menu)
            action.setStatusTip(opDefs[i][0])
            action.setToolTip(opDefs[i][0])
            self.opActions.append(action)
            b = QtGui.QToolButton()
            b.setDefaultAction(action)
            grid.addWidget(b, i/2, i%2)

        self.opButton.setMenu(menu)
        self.opButton.setPopupMode(QtGui.QToolButton.InstantPopup)
        self.connect(self.opButton, QtCore.SIGNAL('clicked(bool)'), self.opButton.showMenu)
        
        self.toolBar.addWidget(self.opButton)

class QRangedBar(QtGui.QWidget):

    BORDERPEN = QtGui.QPen(QtGui.QColor(0, 95, 191))
    BUBBLEPEN = QtGui.QPen(QtGui.QColor(0, 95, 255))
    ACTIVEBRUSH = QtGui.QColor(0, 127, 255)
    EMPTYBRUSH  = QtGui.QBrush(QtCore.Qt.NoBrush)
    
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.range = [0.0, 1.0]
        self.setFixedHeight(8)

    def paintEvent(self, event):
        fullRect = QtCore.QRectF(0, 0, self.width()-1, self.height()-1)
        activeRect = QtCore.QRectF(self.range[0]*fullRect.width(), 0,
                                   (self.range[1]-self.range[0])*fullRect.width(),
                                   self.height()-1)
        painter = QtGui.QPainter(self)
        # Fill the bar
        painter.fillRect(fullRect, QRangedBar.EMPTYBRUSH)
        painter.fillRect(activeRect, QRangedBar.ACTIVEBRUSH)
        
        # Extra-fancy barriers (optional)
        painter.setPen(QRangedBar.BUBBLEPEN)
        painter.setBrush(QRangedBar.ACTIVEBRUSH)
        for i in xrange(int(activeRect.height()+2)/3):
            painter.drawEllipse(activeRect.left()-1, i*3, 2, 2)
            painter.drawEllipse(activeRect.right()-1, i*3, 2, 2)
        
        # Draw the border on top
        painter.setPen(QRangedBar.BORDERPEN)
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.drawRect(fullRect)

        painter.end()

    def sizeHint(self):
        return QtCore.QSize(8, 8)

    def setRange(self, min, max):
        self.range = [min, max]
        self.update()

    def setMin(self, min):
        self.range[0] = min
        self.update()

    def setMax(self, max):
        self.range[1] = max
        self.update()

    def min(self):
        return self.range[0]

    def max(self):
        return self.range[1]

class QSlidingAxis(QtGui.QWidget):

    def __init__(self, axis, parent=None):
        QtGui.QWidget.__init__(self, parent)

        vbox = QtGui.QVBoxLayout()
        self.setLayout(vbox)
        vbox.setSpacing(0)
        vbox.setMargin(0)

        # Create up and down pixmaps
        self.createPixmaps()

        # Top Indicator
        hbox = QtGui.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.setSpacing(0)
        hbox.setMargin(0)

        self.topIndent = QtGui.QSpacerItem(0, 0)
        hbox.addItem(self.topIndent)

        self.topIndicator = QtGui.QLabel()
        hbox.addWidget(self.topIndicator)
        self.topIndicator.setPixmap(self.downArrow)
        self.topIndicator.installEventFilter(self)
        
        hbox.addStretch()

        # A bar showing the range in the middle
        self.barLayout = QtGui.QHBoxLayout()
        vbox.addLayout(self.barLayout, 1)

        leftSpace = max(self.downArrow.width(), self.upArrow.width())/2
        rightSpace = max(self.downArrow.width(), self.upArrow.width()) - leftSpace
        self.barLayout.addSpacing(leftSpace)
        self.rangedBar = QRangedBar()
        self.barLayout.addWidget(self.rangedBar)
        self.barLayout.addSpacing(rightSpace)

        # Bottom Indicator
        hbox = QtGui.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.setSpacing(0)
        hbox.setMargin(0)
        
        self.bottomIndent = QtGui.QSpacerItem(0, 0)
        hbox.addItem(self.bottomIndent)

        self.bottomIndicator = QtGui.QLabel()
        hbox.addWidget(self.bottomIndicator)
        self.bottomIndicator.setPixmap(self.upArrow)
        self.bottomIndicator.installEventFilter(self)

        hbox.addStretch()
        
        # Floating labels
        self.topLabel = QtGui.QLabel('From', self)
        self.bottomLabel = QtGui.QLabel('To', self)

        # Tracking variables
        self.isTracking = False
        self.startX = 0
        self.startWidth = 0

        # Initialize the axis
        self.setAxis(axis)

    def createPixmaps(self):
        # Create down triangle polygon
        downPoly = QtGui.QPolygon(3)
        downPoly.clear()
        downPoly.append(QtCore.QPoint(3, 3))
        downPoly.append(QtCore.QPoint(11, 3))
        downPoly.append(QtCore.QPoint(7, 11))

        # Draw it to a pixmap
        self.downArrow = QtGui.QPixmap(15, 14)
        self.downArrow.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter(self.downArrow)
        painter.setPen(QtCore.Qt.black)
        painter.setBrush(QtCore.Qt.black)
        painter.drawConvexPolygon(downPoly)
        painter.end()

        self.upArrow = self.downArrow.transformed(QtGui.QTransform().rotate(180))

    def setAxis(self, axis):
        self.axis = axis
        if axis!=None:
            if self.axis.isTime():
                self.axisValues = [repr(t.tocomponent()) for t in axis.asRelativeTime()]
            else:
                self.axisValues = axis.getValue()
        else:
            self.axisValues = [str(i) for i in xrange(10)]
        self.axisMaxIndex = len(self.axisValues)-1
        self.minIndex = 0
        self.maxIndex = self.axisMaxIndex

    def getCurrentValues(self):
        return (self.axisValues[self.minIndex], self.axisValues[self.maxIndex])
        
    def resizeEvent(self, e):
        self.updateIndicators()
        self.updateIndicatorLabels()

    def updateIndicatorLabels(self):
        self.topLabel.setText(str(self.axisValues[self.minIndex]))
        self.bottomLabel.setText(str(self.axisValues[self.maxIndex]))
        for (label, indicator, align) in ((self.topLabel, self.topIndicator,
                                           QtCore.Qt.AlignLeft),
                                          (self.bottomLabel, self.bottomIndicator,
                                           QtCore.Qt.AlignRight)):
            label.adjustSize()
            if (align==QtCore.Qt.AlignRight and
                indicator.geometry().right()+label.width()>self.width()):
                align = QtCore.Qt.AlignLeft
            elif (align==QtCore.Qt.AlignLeft and indicator.x()-label.width()<0):
                align = QtCore.Qt.AlignRight
            if align==QtCore.Qt.AlignRight:
                label.move(indicator.geometry().topRight())
            else:
                label.move(indicator.x()-label.width(), indicator.y())

    def updateIndicators(self):
        if self.axisMaxIndex>0:
            topRatio = float(self.minIndex)/self.axisMaxIndex
            bottomRatio = float(self.maxIndex)/self.axisMaxIndex
        else:
            topRatio = 0
            bottomRatio = 1
        self.topIndent.changeSize(topRatio*self.rangedBar.width(),
                                  self.topIndent.geometry().height(),
                                  QtGui.QSizePolicy.Preferred)
        self.bottomIndent.changeSize(bottomRatio*self.rangedBar.width(),
                                     self.bottomIndent.geometry().height(),
                                     QtGui.QSizePolicy.Preferred)
        self.layout().update()
        self.layout().activate()

    def updateRangedBar(self):
        newMin = float(self.topIndent.geometry().width())/self.rangedBar.width()
        newMax = float(self.bottomIndent.geometry().width())/self.rangedBar.width()
        self.rangedBar.setRange(newMin, newMax)

    def getAxisValue(self, newWidth):
        if newWidth<0: newWidth = 0
        if newWidth>self.rangedBar.width(): newWidth = self.rangedBar.width()
        value = int(float(newWidth)/self.rangedBar.width()*self.axisMaxIndex+0.5)
        return value
        
    def eventFilter(self, obj, event):
        indentMap = {self.topIndicator: self.topIndent,
                     self.bottomIndicator: self.bottomIndent}
        if indentMap.has_key(obj):
            indent = indentMap[obj]
            if event.type()==2:#QtCore.QEvent.MouseButtonPress:
                if not self.isTracking:
                    self.isTracking =  True
                    self.startX = event.globalX()
                    self.startWidth = indent.geometry().width()
            elif event.type()==5:#QtCore.QEvent.MouseMove:
                if self.isTracking:
                    newWidth = self.startWidth+event.globalX()-self.startX
                    newValue = self.getAxisValue(newWidth)
                    if indent==self.topIndent:
                        self.minIndex = newValue
                    else:
                        self.maxIndex = newValue
                    self.updateIndicators()
                    self.updateRangedBar()
                    self.updateIndicatorLabels()
            elif event.type()==3:#QtCore.QEvent.MouseButtonRelease:
                if self.isTracking:
                    self.isTracking = False
        return False

class QAxisList(QtGui.QFrame):
    def __init__(self, parent=None):
        QtGui.QFrame.__init__(self, parent)
        self.setFrameStyle(QtGui.QFrame.StyledPanel | QtGui.QFrame.Plain)
        vbox = QtGui.QVBoxLayout()
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setMargin(0)
        vbox.addLayout(self.gridLayout)
        vbox.addStretch()
        self.setLayout(vbox)
        self.axisWidgets = []

    def clear(self):
        self.gridLayout.setRowStretch(self.gridLayout.rowCount()-1, 0)
        for i in reversed(range(self.gridLayout.count())):
            item = self.gridLayout.itemAt(i)
            axis = item.widget()
            if axis:
                self.gridLayout.removeWidget(axis)
                axis.hide()
                axis.deleteLater()
            else:
                self.gridLayout.removeItem(item)
        self.axisWidgets = []

    def setupVariableAxes(self, var): 
        self.clear()
        axisList = var.getAxisList()
        axisLabels = ['T', 'X', 'Y', 'Z'] + [chr(ord('S')-i) for i in xrange(18)]
        c = 0
        for axis in axisList:
            row = self.gridLayout.rowCount()
            label = QtGui.QLabel(axisLabels[c] + ' - ' + axis.id)
            label.font().setBold(True)
            c += 1
            self.gridLayout.addWidget(label, row, 0)
            axisWidget = QSlidingAxis(axis)
            self.axisWidgets.append(axisWidget)
            self.gridLayout.addWidget(axisWidget, row, 1)
            vline = QtGui.QFrame()
            vline.setFrameStyle(QtGui.QFrame.HLine | QtGui.QFrame.Sunken)
            self.gridLayout.addWidget(vline, row+1, 0, 1, self.gridLayout.columnCount())
        self.gridLayout.setRowStretch(self.gridLayout.rowCount(), 1)

    def generateKwArgs(self):
        kwargs = {}
        for axisWidget in self.axisWidgets:
            kwargs[axisWidget.axis.id] = axisWidget.getCurrentValues()
        return kwargs

class QVariableView(QtGui.QWidget):
    
    def __init__(self, fileWidget=None, parent=None):
        QtGui.QWidget.__init__(self, parent)
        vbox = QtGui.QVBoxLayout()
        vbox.setMargin(0)
        self.setLayout(vbox)

        hbox = QtGui.QHBoxLayout()
        self.plotButton = QtGui.QPushButton('&Plot')
        hbox.addWidget(self.plotButton)

        self.plotTypeCombo = QtGui.QComboBox()
        plotTypes = ['Boxfill', 'Isofill', 'Isoline',
                     'Meshfill', 'Outfill', 'Outline', 'Scatter',
                     'Taylordiagram', 'Vector', 'XvsY', 'Xyvsy',
                     'Yxvsx','Ext']
        self.plotTypeCombo.addItems(plotTypes)
        hbox.addWidget(self.plotTypeCombo)
        
        hbox.addStretch()
        vbox.addLayout(hbox)

        self.axisList = QAxisList()
        vbox.addWidget(self.axisList)
        
        self.file = None
        self.var = None

        if fileWidget!=None:
            self.connect(fileWidget, QtCore.SIGNAL('variableChanged'),
                         self.setupVariableAxes)
        self.connect(self.plotButton, QtCore.SIGNAL('clicked(bool)'),
                     self.plot)

    def setupVariableAxes(self, file, var):
        self.file = file
        self.var = var
        if type(var)!=type(None):
            self.axisList.setupVariableAxes(var)
        else:
            self.axisList.clear()

    def constructVariable(self):
        if type(self.var)!=type(None):
            kwargs = self.axisList.generateKwArgs()
            return self.var(**kwargs)
        return None

    def plot(self):
        if type(self.var)!=type(None):
            api.get_current_controller().change_selected_version(0)
            setup_open_call(self.file.id, self.var.id,
                            str(self.plotTypeCombo.currentText()),
                            repr(self.axisList.generateKwArgs()))
            api.get_current_controller().execute_current_workflow()

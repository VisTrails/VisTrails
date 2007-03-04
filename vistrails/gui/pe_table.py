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
""" The file describes the parameter exploration table for VisTrails

QParameterExplorationTable
"""


from PyQt4 import QtCore, QtGui
from gui.common_widgets import QPromptWidget, QStringEdit
from gui.param_view import QParameterTreeWidget
from gui.theme import CurrentTheme
from gui.utils import show_warning
from core.modules.module_configure import PythonEditor
from core.vistrail.action import ChangeParameterAction

################################################################################
class QParameterExplorationWidget(QtGui.QScrollArea):
    """
    QParameterExplorationWidget is a place holder for
    QParameterExplorationTable

    is a grid layout widget having 4
    comlumns corresponding to 4 dimensions of exploration. It accept
    method/alias drops and can be fully configured onto any
    dimension. For each parameter, 3 different approach can be chosen
    to assign the value of that parameter during the exploration:
    linear interpolation (for int, float), list (for int, float and
    string) and user-define function (for int, float, and string)
    
    """
    def __init__(self, parent=None):
        """ QParameterExplorationWidget(parent: QWidget)
                                       -> QParameterExplorationWidget
        Put the QParameterExplorationTable as a main widget
        
        """
        QtGui.QScrollArea.__init__(self, parent)
        self.setAcceptDrops(True)
        self.setWidgetResizable(True)
        self.table = QParameterExplorationTable()
        self.setWidget(self.table)

    def dragEnterEvent(self, event):
        """ dragEnterEvent(event: QDragEnterEvent) -> None
        Set to accept drops from the parameter list
        
        """
        if type(event.source())==QParameterTreeWidget:            
            data = event.mimeData()
            if hasattr(data, 'items'):
                event.accept()
                return
        event.ignore()
        
    def dropEvent(self, event):
        """ dropEvent(event: QDragMoveEvent) -> None
        Accept drop event to add a new method
        
        """
        if type(event.source())==QParameterTreeWidget:
            data = event.mimeData()
            if hasattr(data, 'items'):
                event.accept()
                for item in data.items:
                    self.table.addParameter(item.parameter)
            vsb = self.verticalScrollBar()
            vsb.setValue(vsb.maximum())

    def updatePipeline(self, pipeline):
        """ updatePipeline(pipeline: Pipeline) -> None
        Assign a pipeline to the table
        
        """
        self.table.setPipeline(pipeline)
                    
class QParameterExplorationTable(QPromptWidget):
    """
    QParameterExplorationTable is a grid layout widget having 4
    comlumns corresponding to 4 dimensions of exploration. It accept
    method/alias drops and can be fully configured onto any
    dimension. For each parameter, 3 different approach can be chosen
    to assign the value of that parameter during the exploration:
    linear interpolation (for int, float), list (for int, float and
    string) and user-define function (for int, float, and string)
    
    """
    def __init__(self, parent=None):
        """ QParameterExplorationTable(parent: QWidget)
                                       -> QParameterExplorationTable
        Create an grid layout and accept drops
        
        """
        QPromptWidget.__init__(self, parent)
        self.pipeline = None
        self.setSizePolicy(QtGui.QSizePolicy.Expanding,
                           QtGui.QSizePolicy.Expanding)
        self.setPromptText('Drag aliases/parameters here for a parameter '
                           'exploration')
        self.showPrompt()
        
        vLayout = QtGui.QVBoxLayout(self)
        vLayout.setSpacing(0)
        vLayout.setMargin(0)
        vLayout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(vLayout)

        self.label = QDimensionLabel()
        self.connect(self.label.params.button, QtCore.SIGNAL('clicked()'),
                     self.performParameterExploration)
        for labelIcon in self.label.labelIcons:
            self.connect(labelIcon.countWidget,
                         QtCore.SIGNAL('editingFinished()'),
                         self.updateUserDefinedFunctions)
        vLayout.addWidget(self.label)

        for i in range(2):
            hBar = QtGui.QFrame()
            hBar.setFrameStyle(QtGui.QFrame.HLine | QtGui.QFrame.Sunken)
            vLayout.addWidget(hBar)

    def addParameter(self, paramInfo):
        """ addParameter(paramInfo: (str, [tuple]) -> None
        Add a parameter to the table. The parameter info is specified
        in QParameterTreeWidgetItem
        
        """
        # Check to see paramInfo is not a subset of some other parameter set
        params = paramInfo[1]
        for i in range(self.layout().count()):
            pEditor = self.layout().itemAt(i).widget()
            if pEditor and type(pEditor)==QParameterSetEditor:
                subset = True
                for p in params:
                    if not (p in pEditor.info[1]):
                        subset = False
                        break                    
                if subset:
                    show_warning('Parameter Exists',
                                 'The parameter you are trying to add is '
                                 'already in the list.')
                    return
        self.showPrompt(False)
        newEditor = QParameterSetEditor(paramInfo, self)

        # Make sure to disable all duplicated parameter
        for p in range(len(params)):
            for i in range(self.layout().count()):
                pEditor = self.layout().itemAt(i).widget()
                if pEditor and type(pEditor)==QParameterSetEditor:
                    if params[p] in pEditor.info[1]:
                        widget = newEditor.paramWidgets[p]
                        widget.setDimension(4)
                        widget.setDuplicate(True)
                        widget.setEnabled(False)
                        break
        
        self.layout().addWidget(newEditor)
        newEditor.show()
        self.setMinimumHeight(self.layout().minimumSize().height())

    def removeParameter(self, ps):
        """ removeParameterSet(ps: QParameterSetEditor) -> None
        Remove a parameter set from the table and validate the rest
        
        """
        self.layout().removeWidget(ps)
        # Restore disabled parameter
        for i in range(self.layout().count()):
            pEditor = self.layout().itemAt(i).widget()
            if pEditor and type(pEditor)==QParameterSetEditor:
                for p in range(len(pEditor.info[1])):
                    param = pEditor.info[1][p]
                    widget = pEditor.paramWidgets[p]                    
                    if (param in ps.info[1] and (not widget.isEnabled())):
                        widget.setDimension(0)
                        widget.setDuplicate(False)
                        widget.setEnabled(True)
                        break
        self.showPrompt(self.layout().count()<=3)

    def updateUserDefinedFunctions(self):
        """ updateUserDefinedFunctions() -> None
        Update all user-defined function to reflect the step count
        
        """
        # Go through all possible parameter widgets
        counts = self.label.getCounts()
        for i in range(self.layout().count()):
            pEditor = self.layout().itemAt(i).widget()
            if pEditor and type(pEditor)==QParameterSetEditor:
                for paramWidget in pEditor.paramWidgets:
                    dim = paramWidget.getDimension()
                    if dim in [0, 1, 2, 3]:
                        userWidget = paramWidget.editor.stackedEditors.widget(2)
                        userWidget.setSize(counts[dim])

    def clear(self):
        """ clear() -> None
        Clear all widgets
        
        """
        for i in reversed(range(self.layout().count())):
            pEditor = self.layout().itemAt(i).widget()
            if pEditor and type(pEditor)==QParameterSetEditor:
                pEditor.table = None
                self.layout().removeWidget(pEditor)
        self.label.resetCounts()
        self.showPrompt()

    def setPipeline(self, pipeline):
        """ setPipeline(pipeline: Pipeline) -> None
        Assign a pipeline to the current table
        
        """
        if pipeline!=self.pipeline:
            self.pipeline = pipeline
            self.clear()
        self.label.setEnabled(self.pipeline!=None)

    def collectParameterActions(self):
        """ collectParameterActions() -> list
        Return a list of action lists corresponding to each dimension
        
        """
        if not self.pipeline:
            return None
        parameterValues = [[], [], [], []]
        typeCast = {'Integer': int, 'Float': float, 'String': str}
        counts = self.label.getCounts()
        for i in range(self.layout().count()):
            pEditor = self.layout().itemAt(i).widget()
            if pEditor and type(pEditor)==QParameterSetEditor:
                for paramWidget in pEditor.paramWidgets:
                    editor = paramWidget.editor
                    interpolator = editor.stackedEditors.currentWidget()
                    paramInfo = paramWidget.param
                    realType = typeCast[paramInfo[0]]
                    dim = paramWidget.getDimension()
                    if dim in [0, 1, 2, 3]:
                        count = counts[dim]
                        if type(interpolator)==QLinearInterpolationEditor:
                            values = interpolator.getValues(count)
                        if type(interpolator)==QListInterpolationEditor:
                            values = interpolator.getValues()
                            if (len(values)!=count):
                                show_warning('Inconsistent Size',
                                             'One of the <i>%s</i>\'s list '
                                             'interpolated '
                                             'values has a different '
                                             'size from the step count. '
                                             'Parameter Exploration aborted.'
                                             % pEditor.info[0])
                                return None
                        if type(interpolator)==QUserFunctionEditor:
                            values = interpolator.getValues()
                            if [True for v in values if type(v)!=realType]:
                                show_warning('Inconsistent Size',
                                             'One of the <i>%s</i>\'s user defined '
                                             'functions has generated '
                                             'a value of type different '
                                             'than that specified by the '
                                             'parameter. Parameter Exploration '
                                              'aborted.' % pEditor.info[0])
                                return None
                        (mId, fId, pId) = tuple(paramInfo[2:5])
                        function = self.pipeline.modules[mId].functions[fId]
                        fName = function.name
                        pName = function.params[pId].name
                        pAlias = function.params[pId].alias
                        actions = []
                        for v in values:
                            action = ChangeParameterAction()
                            action.addParameter(mId, fId, pId, fName, pName,
                                                str(v), paramInfo[0], pAlias)
                            actions.append(action)
                        parameterValues[dim].append(actions)
        return [zip(*p) for p in parameterValues]

    def performParameterExploration(self):
        """ performParameterExploration() -> None
        Validate all interpolation values and perform the parameter exploration
        
        """
        actions = self.collectParameterActions()
        self.emit(QtCore.SIGNAL('requestParameterExploration'), actions)

class QDimensionLabel(QtGui.QWidget):
    """
    QDimensionLabel represents a horizontal header item of the
    parameter window. It has 4 small icons represents the dimensions
    and a Skip label. It represents a group box.
    
    """
    def __init__(self, parent=None):
        """ QDimensionLabel(parent: QWidget) -> None
        Initialize icons and labels
        
        """
        QtGui.QWidget.__init__(self, parent)
        self.setAutoFillBackground(True)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding,
                           QtGui.QSizePolicy.Maximum)

        hLayout = QtGui.QHBoxLayout(self)
        hLayout.setMargin(0)
        hLayout.setSpacing(0)
        self.setLayout(hLayout)        

        self.params = QDimensionLabelText('Parameters')
        hLayout.addWidget(self.params)
        self.params.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                  QtGui.QSizePolicy.Expanding)
        hLayout.addWidget(QDimensionLabelSeparator())
        
        pixes = [CurrentTheme.EXPLORE_COLUMN_PIXMAP,
                 CurrentTheme.EXPLORE_ROW_PIXMAP,
                 CurrentTheme.EXPLORE_SHEET_PIXMAP,
                 CurrentTheme.EXPLORE_TIME_PIXMAP]
        self.labelIcons = []
        for pix in pixes:
            labelIcon = QDimensionLabelIcon(pix)
            hLayout.addWidget(labelIcon)
            self.labelIcons.append(labelIcon)            
            hLayout.addWidget(QDimensionLabelSeparator())

        hLayout.addWidget(QDimensionLabelIcon(CurrentTheme.EXPLORE_SKIP_PIXMAP,
                                              False))

    def getCounts(self):
        """ getCounts() -> [int]        
        Return a list of 4 ints denoting the step count desired for
        each dimension
        
        """
        return [l.countWidget.value() for l in self.labelIcons]

    def resetCounts(self):
        """ resetCounts() -> None
        Reset all counts to 1
        
        """
        for l in self.labelIcons:
            l.countWidget.setValue(1)
    
class QDimensionSpinBox(QtGui.QSpinBox):
    """
    QDimensionSpinBox is just an overrided spin box that will also emit
    'editingFinished()' signal when the user interact with mouse
    
    """    
    def mouseReleaseEvent(self, event):
        """ mouseReleaseEvent(event: QMouseEvent) -> None
        Emit 'editingFinished()' signal when the user release a mouse button
        
        """
        QtGui.QSpinBox.mouseReleaseEvent(self, event)
        self.emit(QtCore.SIGNAL("editingFinished()"))

class QDimensionLabelIcon(QtGui.QWidget):
    """
    QDimensionLabelIcon describes those icons staying on the header
    view of the table
    
    """
    def __init__(self, pix, hasCount = True, parent=None):
        """ QDimensionalLabelIcon(pix: QPixmap, hasCount: bool, parent: QWidget)
                                  -> QDimensionalLabelIcon
        Using size 32x32 and a margin of 2
        
        """
        QtGui.QWidget.__init__(self, parent)
        layout = QtGui.QVBoxLayout()
        layout.setMargin(0)
        layout.setSpacing(0)
        self.setLayout(layout)

        label = QtGui.QLabel()
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setPixmap(pix.scaled(32, 32, QtCore.Qt.KeepAspectRatio,
                                  QtCore.Qt.SmoothTransformation))
        layout.addWidget(label)

        if hasCount:
            self.countWidget = QDimensionSpinBox()
            self.countWidget.setFixedWidth(32)
            self.countWidget.setRange(1, 10000000)
            self.countWidget.setAlignment(QtCore.Qt.AlignRight)
            self.countWidget.setFrame(False)
            pal = QtGui.QPalette(self.countWidget.lineEdit().palette())
            pal.setBrush(QtGui.QPalette.Base,
                         QtGui.QBrush(QtCore.Qt.NoBrush))
            self.countWidget.lineEdit().setPalette(pal)
            layout.addWidget(self.countWidget)
            
        self.setSizePolicy(QtGui.QSizePolicy.Maximum,
                            QtGui.QSizePolicy.Maximum)        
                
class QDimensionLabelText(QtGui.QWidget):
    """
    QDimensionLabelText describes those texts staying on the header
    view of the table. It also has a button to perform exploration
    
    """
    def __init__(self, text, parent=None):
        """ QDimensionalLabelText(text: str, parent: QWidget)
                                   -> QDimensionalLabelText
        Putting the text bold in the center
        
        """
        QtGui.QWidget.__init__(self, parent)
        hLayout = QtGui.QHBoxLayout()
        self.setLayout(hLayout)

        hLayout.addStretch()
        
        self.button = QtGui.QToolButton()
        self.button.setIcon(CurrentTheme.PERFORM_PARAMETER_EXPLORATION_ICON)
        self.button.setIconSize(QtCore.QSize(32, 32))
        hLayout.addWidget(self.button)
        
        hLayout.addSpacing(2)

        hLayout.addWidget(QtGui.QLabel('<b>Parameters</b>'))

        hLayout.addStretch()
        
        
class QDimensionLabelSeparator(QtGui.QFrame):
    """
    QDimensionLabelSeparator is acting as a vertical separator which
    has an appropriate style to go with the QDimensionalLabel
    
    """
    def __init__(self, parent=None):
        """ QDimensionalLabelSeparator(parent: QWidget)
                                       -> QDimensionalLabelSeparator
        Make sure the frame only has a width of 2
        
        """
        QtGui.QFrame.__init__(self, parent)
        self.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Sunken)
        self.setFixedWidth(2)

class QParameterSetEditor(QtGui.QWidget):
    """
    QParameterSetEditor is a widget controlling a set of
    parameters. The set can contain a single parameter (aliases) or
    multiple of them (module methods).
    
    """
    def __init__(self, info, table=None, parent=None):
        """ QParameterSetEditor(info: paraminfo,
                                table: QParameterExplorationTable,
                                parent: QWidget)
                                -> QParameterSetEditor
        Construct a parameter editing widget based on the paraminfo
        (described in QParameterTreeWidgetItem)
        
        """
        QtGui.QWidget.__init__(self, parent)
        self.info = info
        self.table = table
        (name, paramList) = info
        if table:
            size = table.label.getCounts()[0]
        else:
            size = 1
        
        vLayout = QtGui.QVBoxLayout(self)
        vLayout.setMargin(0)
        vLayout.setSpacing(0)
        self.setLayout(vLayout)

        label = QParameterSetLabel(name)
        self.connect(label.removeButton, QtCore.SIGNAL('clicked()'),
                     self.removeSelf)
        vLayout.addWidget(label)
        
        self.paramWidgets = []
        for param in paramList:
            paramWidget = QParameterWidget(param, size)
            vLayout.addWidget(paramWidget)
            self.paramWidgets.append(paramWidget)

        vLayout.addSpacing(10)

        hBar = QtGui.QFrame()
        hBar.setFrameStyle(QtGui.QFrame.HLine | QtGui.QFrame.Sunken)
        vLayout.addWidget(hBar)

    def removeSelf(self):
        """ removeSelf() -> None
        Remove itself out of the parent layout()
        
        """
        if self.table:
            self.table.removeParameter(self)            
            self.table = None
            self.close()
            self.deleteLater()

class QParameterSetLabel(QtGui.QWidget):
    """
    QParameterSetLabel is the label bar showing at the top of the
    parameter set editor. It also has a Remove button to remove the
    parameter
    
    """
    def __init__(self, text, parent=None):
        """ QParameterSetLabel(text: str, parent: QWidget) -> QParameterSetLabel
        Init a label and a button
        
        """
        QtGui.QWidget.__init__(self, parent)        
        hLayout = QtGui.QHBoxLayout(self)
        hLayout.setMargin(0)
        hLayout.setSpacing(0)
        self.setLayout(hLayout)

        hLayout.addSpacing(5)

        label = QtGui.QLabel(text)
        font = QtGui.QFont(label.font())
        font.setBold(True)
        label.setFont(font)
        hLayout.addWidget(label)

        hLayout.addSpacing(5)
        
        self.removeButton = QtGui.QToolButton()
        self.removeButton.setAutoRaise(True)
        self.removeButton.setIcon(QtGui.QIcon(
            self.style().standardPixmap(QtGui.QStyle.SP_DialogCloseButton)))
        self.removeButton.setIconSize(QtCore.QSize(12, 12))
        self.removeButton.setFixedWidth(16)
        hLayout.addWidget(self.removeButton)

        hLayout.addStretch()
        
class QParameterWidget(QtGui.QWidget):
    """
    QParameterWidget is a row widget containing a label, a parameter
    editor and a radio group.
    
    """
    def __init__(self, param, size, parent=None):
        """ QParameterWidget(param: tuple, size: int, parent: QWidget)
                             -> QParameterWidget
        Initialize the widget with param = (aType, mId, fId, pId)
        
        """
        QtGui.QWidget.__init__(self, parent)
        self.param = param
        self.prevWidget = 0
        
        hLayout = QtGui.QHBoxLayout(self)
        hLayout.setMargin(0)
        hLayout.setSpacing(0)        
        self.setLayout(hLayout)

        hLayout.addSpacing(5+16+5)

        self.label = QtGui.QLabel(param[0])
        self.label.setFixedWidth(50)
        hLayout.addWidget(self.label)

        self.editor = QParameterEditor(param[0], param[1], size)
        hLayout.addWidget(self.editor)

        self.selector = QDimensionSelector()
        self.connect(self.selector.radioButtons[4],
                     QtCore.SIGNAL('toggled(bool)'),
                     self.disableParameter)
        hLayout.addWidget(self.selector)

    def getDimension(self):
        """ getDimension() -> int        
        Return a number 0-4 indicating which radio button is
        selected. If none is selected (should not be in this case),
        return -1
        
        """
        for i in range(5):
            if self.selector.radioButtons[i].isChecked():
                return i
        return -1

    def disableParameter(self, disabled=True):
        """ disableParameter(disabled: bool) -> None
        Disable/Enable this parameter when disabled is True/False
        
        """
        self.label.setEnabled(not disabled)
        self.editor.setEnabled(not disabled)

    def setDimension(self, dim):
        """ setDimension(dim: int) -> None
        Select a dimension for this parameter
        
        """
        if dim in range(5):
            self.selector.radioButtons[dim].setChecked(True)

    def setDuplicate(self, duplicate):
        """ setDuplicate(duplicate: True) -> None
        Set if this parameter is a duplicate parameter
        
        """
        if duplicate:
            self.prevWidget = self.editor.stackedEditors.currentIndex()
            self.editor.stackedEditors.setCurrentIndex(3)
        else:
            self.editor.stackedEditors.setCurrentIndex(self.prevWidget)

class QDimensionSelector(QtGui.QWidget):
    """
    QDimensionSelector provides 5 radio buttons to select dimension of
    exploration or just skipping it.
    
    """
    def __init__(self, parent=None):
        """ QDimensionSelector(parent: QWidget) -> QDimensionSelector
        Initialize the horizontal layout and set the width to be fixed
        equal to the QDimensionLabel
        
        """
        QtGui.QWidget.__init__(self, parent)
        self.setSizePolicy(QtGui.QSizePolicy.Maximum,
                           QtGui.QSizePolicy.Maximum)
        
        hLayout = QtGui.QHBoxLayout(self)
        hLayout.setMargin(0)
        hLayout.setSpacing(0)        
        self.setLayout(hLayout)

        self.radioButtons = []
        for i in range(5):
            hLayout.addSpacing(2)
            button = QDimensionRadioButton()
            self.radioButtons.append(button)
            button.setFixedWidth(32)
            hLayout.addWidget(button)
        self.radioButtons[0].setChecked(True)

class QDimensionRadioButton(QtGui.QRadioButton):
    """
    QDimensionRadioButton is a replacement of QRadioButton with
    simpler appearance. We just need to override the paint event
    
    """
    def paintEvent(self, event):
        """ paintEvent(event: QPaintEvent) -> None
        Draw an outer circle and another solid one in side
        
        """
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(self.palette().color(QtGui.QPalette.Dark))
        painter.setBrush(QtCore.Qt.NoBrush)
        l = min(self.width()-2, self.height()-2, 12)
        r = QtCore.QRect(0, 0, l, l)
        r.moveCenter(self.rect().center())
        painter.drawEllipse(r)

        if self.isChecked():
            r.adjust(3, 3, -3, -3)
            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(self.palette().color(QtGui.QPalette.WindowText))
            painter.drawEllipse(r)
        
        painter.end()

    def mousePressEvent(self, event):
        """ mousePressEvent(event: QMouseEvent) -> None
        Force toggling the radio button
        
        """
        self.click()


class QParameterEditor(QtGui.QWidget):
    """
    QParameterEditor specifies the method used for interpolating
    parameter values. It suppports Linear Interpolation, List and
    User-define function. There are only 3 types that can be editable
    with this editor: Integer, Float and String
    
    """
    def __init__(self, pType, pValue, size, parent=None):
        """ QParameterEditor(pType: str, pValue: str, parent: QWidget,
                             size: int) -> QParameterEditor
        Put a stacked widget and a popup button
        
        """
        QtGui.QWidget.__init__(self, parent)
        self.type = pType
        self.defaultValue = pValue
        
        hLayout = QtGui.QHBoxLayout(self)
        hLayout.setMargin(0)
        hLayout.setSpacing(0)        
        self.setLayout(hLayout)

        self.stackedEditors = QtGui.QStackedWidget()
        self.stackedEditors.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                          QtGui.QSizePolicy.Maximum)
        self.stackedEditors.addWidget(QLinearInterpolationEditor(pType,
                                                                 pValue))
        self.stackedEditors.addWidget(QListInterpolationEditor(pType,
                                                               pValue))
        self.stackedEditors.addWidget(QUserFunctionEditor(pType,
                                                          pValue,
                                                          size))
        self.stackedEditors.addWidget(QtGui.QLabel('<i>This is a duplicated '
                                                   'parameter</i>'))
        hLayout.addWidget(self.stackedEditors)

        selector = QParameterEditorSelector(pType)
        self.connect(selector.actionGroup,
                     QtCore.SIGNAL('triggered(QAction*)'),
                     self.changeInterpolator)
        hLayout.addWidget(selector)
        selector.initAction()

    def changeInterpolator(self, action):
        """ changeInterpolator(action: QAction) -> None        
        Bring the correct interpolation editing widget to front in the
        stacked widget
        
        """
        widgetIdx = action.data().toInt()[0]
        if widgetIdx<self.stackedEditors.count():
            self.stackedEditors.setCurrentIndex(widgetIdx)

class QParameterEditorSelector(QtGui.QToolButton):
    """
    QParameterEditorSelector is a button with a down arrow allowing
    users to select which type of interpolator he/she wants to use
    
    """
    def __init__(self, pType, parent=None):
        """ QParameterEditorSelector(pType: str, parent: QWidget)
                                     -> QParameterEditorSelector
        Put a stacked widget and a popup button
        
        """
        QtGui.QToolButton.__init__(self, parent)
        self.type = pType        
        self.setAutoRaise(True)
        self.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        self.setPopupMode(QtGui.QToolButton.InstantPopup)
        
        self.setText(QtCore.QString(QtCore.QChar(0x25bc))) # Down triangle

        self.actionGroup = QtGui.QActionGroup(self)
        
        self.linearAction = QtGui.QAction('Linear Interpolation',
                                          self.actionGroup)
        self.listAction = QtGui.QAction('List', self.actionGroup)
        self.userAction = QtGui.QAction('User-defined Function',
                                        self.actionGroup)
        aId = 0
        for action in self.actionGroup.actions():
            action.setCheckable(True)
            action.setData(QtCore.QVariant(aId))
            aId += 1

        if pType=='String':
            self.linearAction.setEnabled(False)
            
        menu = QtGui.QMenu(self)
        menu.addActions(self.actionGroup.actions())
        self.setMenu(menu)

    def initAction(self):
        """ initAction() -> None
        Select the first choice of selector based on self.type
        
        """
        if self.type=='String':
            self.listAction.trigger()
        else:
            self.linearAction.trigger()

class LinearInterpolator(object):

    def __init__(self, ptype, mn, mx, steps):
        self._ptype = ptype
        self._mn = mn
        self._mx = mx
        self._steps = steps

    def get_values(self):
        cast = self._ptype
        begin = self._mn
        end = self._mx
        size = self._steps
        if size<=1:
            return [begin]
        result = [cast(begin + (((end-begin)*i) / cast(size-1)))
                  for i in range(size)]
        return result

class QLinearInterpolationEditor(QtGui.QWidget):
    """
    QLinearInterpolationEditor is the actual widget allowing users to
    edit his/her linear interpolation parameters.
    
    """
    def __init__(self, pType, pValue, parent=None):
        """ QLinearInterpolationEditor(pType: str, pValue: str, parent: QWidget)
                                       -> QLinearInterpolationEditor
        Construct 2 edit box for From and To
        
        """
        QtGui.QWidget.__init__(self, parent)
        self.type = pType
        
        hLayout = QtGui.QHBoxLayout(self)
        hLayout.setMargin(0)
        hLayout.setSpacing(0)
        self.setLayout(hLayout)

        if pType=='Integer':            
            validatorType = QtGui.QIntValidator
        else:
            validatorType = QtGui.QDoubleValidator

        self.fromEdit = QtGui.QLineEdit(pValue)
        self.fromEdit.setValidator(validatorType(self.fromEdit))
        hLayout.addWidget(self.fromEdit)

        hLayout.addSpacing(5)

        rightArrow = QtGui.QLabel()
        pixmap = self.style().standardPixmap(QtGui.QStyle.SP_ArrowRight)
        rightArrow.setPixmap(CurrentTheme.RIGHT_ARROW_PIXMAP)
        hLayout.addWidget(rightArrow)
        
        hLayout.addSpacing(5)
        
        self.toEdit = QtGui.QLineEdit(pValue)
        self.toEdit.setValidator(validatorType(self.toEdit))
        hLayout.addWidget(self.toEdit)

    def getValues(self, size):
        """ getValues(size: int) -> tuple
        Return the linear interpolated list containing 'size' values
        
        """
        cast = {'Integer': int, 'Float': float}[self.type]
        begin = cast(str(self.fromEdit.text()))
        end = cast(str(self.toEdit.text()))
        lerp = LinearInterpolator(cast,
                                  begin,
                                  end,
                                  size)
        return lerp.get_values()
    
class QListInterpolationEditor(QtGui.QWidget):
    """
    QListInterpolationEditor is the actual widget allowing users to
    enter a list of values for interpolation
    
    """
    def __init__(self, pType, pValue, parent=None):
        """ QListInterpolationEditor(pType: str, pValue: str, parent: QWidget)
                                     -> QListInterpolationEditor
        Construct an edit box with a button for bringing up the dialog
        
        """
        QtGui.QWidget.__init__(self, parent)
        self.type = pType
        
        hLayout = QtGui.QHBoxLayout(self)
        hLayout.setMargin(0)
        hLayout.setSpacing(0)
        self.setLayout(hLayout)
        
        self.listValues = QtGui.QLineEdit()
        if pType=='String':
            self.listValues.setText("['%s']" % pValue.replace("'", "\'"))
        else:
            self.listValues.setText('[%s]' % pValue)
        self.listValues.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                      QtGui.QSizePolicy.Maximum)
        self.listValues.home(False)
        hLayout.addWidget(self.listValues)

        inputButton = QtGui.QToolButton()
        inputButton.setText('...')
        self.connect(inputButton, QtCore.SIGNAL('clicked()'),
                     self.editListValues)
        hLayout.addWidget(inputButton)

    def getValues(self):
        """ getValues() -> []        
        Convert the list values into a list
        
        """
        text = str(self.listValues.text())
        try:
            return [str(v) for v in eval(text)]
        except:
            i = text.find('[')
            if i!=-1:
                j = text.find(']')
                if j>i:
                    return text[i+1:j].split(',')
            return [text]

    def editListValues(self):
        """ editListValues() -> None
        Show a dialog for editing the values
        
        """
        dialog = QListEditDialog(self.type, self.getValues(), None)
        if dialog.exec_()==QtGui.QDialog.Accepted:
            values = dialog.getList()
            if self.type=='String':
                values = ["'%s'" % v.replace("'", "\'")
                          for v in values]
            self.listValues.setText('[%s]' % ', '.join(values))
            self.listValues.home(False)
        dialog.deleteLater()

class QListEditDialog(QtGui.QDialog):
    """
    QListEditDialog provides an interface for user to edit a list of
    values and export to a string
    
    """
    def __init__(self, pType, values, parent=None):
        """ QListEditDialog(pType: str, values: list, parent: QWidget)
                            -> QListEditDialog
        Parse values and setup the table
        
        """
        QtGui.QDialog.__init__(self, parent)
        self.pType = pType
        vLayout = QtGui.QVBoxLayout()
        vLayout.setMargin(0)
        vLayout.setSpacing(0)
        self.setLayout(vLayout)
        
        label = QtGui.QLabel("Please enter values in boxes below. Drag "
                             "rows up and down to arrange your list values. "
                             "'Add' appends an empty value to the list. "
                             "And 'Del' removes the selected values.")
        label.setMargin(5)
        label.setWordWrap(True)
        vLayout.addWidget(label)

        self.table = QtGui.QTableWidget(0, 1, parent)
        self.table.setHorizontalHeaderLabels(QtCore.QStringList('Values'))
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setMovable(True)
        self.table.verticalHeader().setResizeMode(
            QtGui.QHeaderView.ResizeToContents)
        self.delegate = QListEditItemDelegate()
        self.table.setItemDelegate(self.delegate)
        self.table.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        for i in range(len(values)):
            self.addRow(str(values[i]))
        self.connect(self.table.verticalHeader(),
                     QtCore.SIGNAL('sectionMoved(int,int,int)'),
                     self.rowMoved)
        vLayout.addWidget(self.table)

        hLayout = QtGui.QHBoxLayout()        
        vLayout.addLayout(hLayout)

        okButton = QtGui.QPushButton('&OK')
        okButton.setSizePolicy(QtGui.QSizePolicy.Maximum,
                               QtGui.QSizePolicy.Maximum)
        self.connect(okButton, QtCore.SIGNAL('clicked()'), self.accept)
        hLayout.addWidget(okButton)

        cancelButton = QtGui.QPushButton('&Cancel')
        cancelButton.setSizePolicy(QtGui.QSizePolicy.Maximum,
                                   QtGui.QSizePolicy.Maximum)
        self.connect(cancelButton, QtCore.SIGNAL('clicked()'), self.reject)
        hLayout.addWidget(cancelButton)

        addButton = QtGui.QPushButton('&Add')
        addButton.setIcon(CurrentTheme.ADD_STRING_ICON)
        addButton.setSizePolicy(QtGui.QSizePolicy.Maximum,
                                QtGui.QSizePolicy.Maximum)
        self.connect(addButton, QtCore.SIGNAL('clicked()'), self.addRow)
        hLayout.addWidget(addButton)
        
        removeButton = QtGui.QPushButton('&Del')
        removeButton.setIcon(QtGui.QIcon(
            self.style().standardPixmap(QtGui.QStyle.SP_DialogCancelButton)))
        removeButton.setSizePolicy(QtGui.QSizePolicy.Maximum,
                                   QtGui.QSizePolicy.Maximum)
        self.connect(removeButton, QtCore.SIGNAL('clicked()'),
                     self.removeSelection)
        hLayout.addWidget(removeButton)
        
    def sizeHint(self):
        """ sizeHint() -> QSize
        Return the recommended size for the widget
        
        """
        return QtCore.QSize(256, 384)

    def getList(self):
        """ getList() -> list of str values
        Return a list of values
        
        """
        result = []
        for i in range(self.table.rowCount()):
            logicalIndex = self.table.verticalHeader().logicalIndex(i)
            value = self.table.item(logicalIndex, 0).text()            
            result.append(str(value))
        return result

    def rowMoved(self, row, old, new):
        """ rowMove(row: int, old: int, new: int) -> None
        Renumber the vertical header labels when row moved
        
        """
        vHeader = self.table.verticalHeader()
        labels = QtCore.QStringList()        
        for i in range(self.table.rowCount()):
            labels << str(vHeader.visualIndex(i)+1)
        self.table.setVerticalHeaderLabels(labels)

    def addRow(self, text=None):
        """ addRow(text: str) -> QListStringEdit
        Add an extra row to the end of the table
        
        """
        self.table.setRowCount(self.table.rowCount()+1)
        if text:
            item = QtGui.QTableWidgetItem(text)
        else:
            item = QtGui.QTableWidgetItem()
        row = self.table.rowCount()-1
        self.table.setItem(row, 0, item)

    def removeSelection(self):
        """ removeSelection() -> None
        Remove selected rows on the table
        
        """
        for item in self.table.selectedItems():
            self.table.removeRow(item.row())

class QListEditItemDelegate(QtGui.QItemDelegate):
    """
    QListEditItemDelegate sets up the editor for the QListEditDialog
    table
    
    """
    def createEditor(self, parent, option, index):
        """ createEditor(parent: QWidget,
                         option: QStyleOptionViewItem,
                         index: QModelIndex) -> QStringEdit
        Return the editor widget for the index
        
        """
        return QStringEdit(parent)

    def setEditorData(self, editor, index):
        """ setEditorData(editor: QWidget, index: QModelIndex) -> None
        Set the editor to reflects data at index
        
        """
        editor.setText(index.data().toString())
        editor.selectAll()

    def updateEditorGeometry(self, editor, option, index):
        """ updateEditorGeometry(editor: QStringEdit,
                                 option: QStyleOptionViewItem,
                                 index: QModelIndex) -> None
        Update the geometry of the editor based on the style option
        
        """
        editor.setGeometry(option.rect)

    def setModelData(self, editor, model, index):
        """ setModelData(editor: QStringEdit,
                         model: QAbstractItemModel,
                         index: QModelIndex) -> None
        Set the text of the editor back to the item model
        
        """
        model.setData(index, QtCore.QVariant(editor.text()))

class QUserFunctionEditor(QtGui.QFrame):
    """
    QUserFunctionEditor shows user-defined interpolation function
    
    """
    def __init__(self, pType, pValue, size, parent=None):
        """ QUserFunctionEditor(pType: str, pValue: str, parent: QWidget)
                                -> QUserFunctionEditor
        Create a read-only line edit widget and a button for
        customizing the user-defined function
        
        """
        QtGui.QFrame.__init__(self, parent)
        self.setFrameStyle(QtGui.QFrame.Box | QtGui.QFrame.Sunken)
        self.size = -1
        self.type = pType
        self.defaultValue = pValue
        self.function = self.defaultFunction()
        
        hLayout = QtGui.QHBoxLayout(self)
        hLayout.setMargin(0)
        hLayout.setSpacing(0)
        self.setLayout(hLayout)
        
        hLayout.addSpacing(2)
        self.label = QtGui.QLabel()
        hLayout.addWidget(self.label)

        self.listValues = QtGui.QLineEdit()
        self.listValues.setFrame(False)        
        self.listValues.palette().setBrush(QtGui.QPalette.Base,
                                           QtGui.QBrush(QtCore.Qt.NoBrush))
        self.listValues.setReadOnly(True)
        self.listValues.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                      QtGui.QSizePolicy.Maximum)
        self.listValues.home(False)
        hLayout.addWidget(self.listValues)

        self.setSize(size)

        inputButton = QtGui.QToolButton()
        inputButton.setText('...')
        self.connect(inputButton, QtCore.SIGNAL('clicked()'),
                     self.editFunction)
        hLayout.addWidget(inputButton)

    def defaultFunction(self):
        """ defaultFunction() -> str
        Return the default function definition
        
        """
        if self.type=='String':
            quote = '"'
        else:
            quote = ''
        pythonType = {'Integer': 'int', 'Float': 'float', 'String': 'str'}
        return 'def value(i):\n    """ value(i: int) -> %s\n'\
               '    Return the interpolated value at step i\n'\
               '    i is from 0 to <step count>-1\n\n'\
               '    """\n'\
               '    return %s%s%s'\
               % (pythonType[self.type], quote, str(self.defaultValue), quote)

    def getValues(self):
        """ getValues() -> []        
        Convert the user define function into a list. Size specifies the size
        request.
        
        """
        firstError = True
        values = []
        for i in range(self.size):
            v = self.defaultValue
            try:
                exec(self.function + '\nv = value(%d)' % i)
            except:
                v = 'ERROR'
            values.append(v)
        return values

    def getValuesString(self):
        """ getValuesString() -> str
        Return a string representation of the parameter list
        
        """
        return '{%s}' % ','.join([str(v) for v in self.getValues()])

    def editFunction(self):
        """ editFunction() -> None
        Pop up a dialog for editing user-defined function
        
        """
        dialog = QUserFunctionDialog(self.function)        
        if dialog.exec_()==QtGui.QDialog.Accepted:
            self.function = str(dialog.editor.toPlainText())
            self.listValues.setText(self.getValuesString())
        dialog.deleteLater()

    def setSize(self, size):
        """ setSize(size: int) -> None
        Set the size of the interpolation. Values are re-calculated
        
        """
        if size!=self.size:
            self.size = size
            htmlText = '<html><big>&fnof;</big>(n) <b>:</b> ' \
                       '[0,%d) &rarr; </html>' % size
            self.label.setText(htmlText)
            self.listValues.setText(self.getValuesString())
    
class QUserFunctionDialog(QtGui.QDialog):
    """
    QUserFunctionDialog provides an interface for user to edit a
    python function
    
    """
    def __init__(self, function, parent=None):
        """ QUserFunctionDialog(function: str, parent: QWidget)
                                -> QUserFunctionDialog
        Set up a python source editor
        
        """
        QtGui.QDialog.__init__(self, parent)
        vLayout = QtGui.QVBoxLayout()
        vLayout.setMargin(0)
        vLayout.setSpacing(0)
        self.setLayout(vLayout)
        
        label = QtGui.QLabel("Please define your function below. This "
                             "'value(i)' function will be iteratively called "
                             "for <step count> numbers. For each step, "
                             "it should return a value of parameter type.")
        label.setMargin(5)
        label.setWordWrap(True)
        vLayout.addWidget(label)

        self.editor = PythonEditor(self)
        self.editor.setPlainText(function)
        self.editor.moveCursor(QtGui.QTextCursor.End)
        vLayout.addWidget(self.editor)

        hLayout = QtGui.QHBoxLayout()        
        vLayout.addLayout(hLayout)

        okButton = QtGui.QPushButton('&OK')
        okButton.setSizePolicy(QtGui.QSizePolicy.Maximum,
                               QtGui.QSizePolicy.Maximum)
        self.connect(okButton, QtCore.SIGNAL('clicked()'), self.accept)
        hLayout.addWidget(okButton)

        cancelButton = QtGui.QPushButton('&Cancel')
        cancelButton.setSizePolicy(QtGui.QSizePolicy.Maximum,
                                   QtGui.QSizePolicy.Maximum)
        self.connect(cancelButton, QtCore.SIGNAL('clicked()'), self.reject)
        hLayout.addWidget(cancelButton)
        
    def sizeHint(self):
        """ sizeHint() -> QSize
        Return the recommended size for the widget
        
        """
        return QtCore.QSize(512, 512)
            
################################################################################

import unittest

class TestLinearInterpolator(unittest.TestCase):

    def test_int(self):
        x = LinearInterpolator(int, 0, 999, 1000)
        assert x.get_values() == range(1000)

    def test_float(self):
        # test the property that differences in value must be linearly
        # proportional to differences in index for a linear interpolation
        import random
        s = random.randint(4, 10000)
        v1 = random.random()
        v2 = random.random()
        mn = min(v1, v2)
        mx = max(v1, v2)
        x = LinearInterpolator(float, mn, mx, s).get_values()
        v1 = random.randint(0, s-1)
        v2 = 0
        while v2 == v1:
            v2 = random.randint(0, s-1)
        v3 = random.randint(0, s-1)
        v4 = 0
        while v3 == v4:
            v4 = random.randint(0, s-1)
        r1 = (v2 - v1) / (x[v2] - x[v1])
        r2 = (v4 - v3) / (x[v4] - x[v3])
        assert abs(r1 - r2) < 1e-6        

if __name__=="__main__":        
    import sys
    import gui.theme
    app = QtGui.QApplication(sys.argv)
    gui.theme.initializeCurrentTheme()
    vc = QDimensionLabel(CurrentTheme.EXPLORE_SHEET_PIXMAP, 'Hello World')
    vc.show()
    sys.exit(app.exec_())

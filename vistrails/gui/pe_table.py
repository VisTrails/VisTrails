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
from gui.common_widgets import QPromptWidget
from gui.theme import CurrentTheme
from gui.param_view import QParameterTreeWidget

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
        self.setSizePolicy(QtGui.QSizePolicy.Expanding,
                           QtGui.QSizePolicy.Expanding)
        self.setPromptText('Drag aliases/parameters here for a parameter '
                           'exploration')
#        self.showPrompt()
        
        vLayout = QtGui.QVBoxLayout(self)
        vLayout.setSpacing(0)
        vLayout.setMargin(0)
        vLayout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(vLayout)

        vLayout.addWidget(QDimensionLabel())

        for i in range(2):
            hBar = QtGui.QFrame()
            hBar.setFrameStyle(QtGui.QFrame.HLine | QtGui.QFrame.Sunken)
            vLayout.addWidget(hBar)

    def addParameter(self, paramInfo):
        """ addParameter(paramInfo: (str, [tuple]) -> None
        Add a parameter to the table. The parameter info is specified
        in QParameterTreeWidgetItem
        
        """
        p = QParameterSetEditor(paramInfo, self)
        self.layout().addWidget(p)
        p.show()
        self.setMinimumHeight(self.layout().minimumSize().height())

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

        params = QDimensionLabelText('Parameters')
        hLayout.addWidget(params)
        params.setSizePolicy(QtGui.QSizePolicy.Expanding,
                             QtGui.QSizePolicy.Expanding)
        hLayout.addWidget(QDimensionLabelSeparator())
        
        pixes = [CurrentTheme.EXPLORE_COLUMN_PIXMAP,
                 CurrentTheme.EXPLORE_ROW_PIXMAP,
                 CurrentTheme.EXPLORE_SHEET_PIXMAP,
                 CurrentTheme.EXPLORE_TIME_PIXMAP]
        for pix in pixes:
            hLayout.addWidget(QDimensionLabelIcon(pix))
            hLayout.addWidget(QDimensionLabelSeparator())

        hLayout.addWidget(QDimensionLabelIcon(CurrentTheme.EXPLORE_SKIP_PIXMAP,
                                              False))

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
            self.countWidget = QtGui.QSpinBox()
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
                
class QDimensionLabelText(QtGui.QLabel):
    """
    QDimensionLabelText describes those texts staying on the header
    view of the table
    
    """
    def __init__(self, text, parent=None):
        """ QDimensionalLabelText(text: str, parent: QWidget)
                                   -> QDimensionalLabelText
        Putting the text bold in the center
        
        """
        QtGui.QLabel.__init__(self, text, parent)
        font = QtGui.QFont(self.font())
        font.setItalic(False)
        font.setBold(True)
        self.setFont(font)
        self.setAlignment(QtCore.Qt.AlignCenter)
        
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
        
        vLayout = QtGui.QVBoxLayout(self)
        vLayout.setMargin(0)
        vLayout.setSpacing(0)
        self.setLayout(vLayout)

        label = QParameterSetLabel(name)
        self.connect(label.removeButton, QtCore.SIGNAL('clicked()'),
                     self.removeSelf)
        vLayout.addWidget(label)

        for param in paramList:
            vLayout.addWidget(QParameterWidget(param))

        vLayout.addSpacing(10)

        hBar = QtGui.QFrame()
        hBar.setFrameStyle(QtGui.QFrame.HLine | QtGui.QFrame.Sunken)
        vLayout.addWidget(hBar)

    def removeSelf(self):
        """ removeSelf() -> None
        Remove itself out of the parent layout()
        
        """
        if self.table:
            self.table.layout().removeWidget(self)
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
    def __init__(self, param, parent=None):
        """ QParameterWidget(param: tuple, parent: QWidget) -> QParameterWidget
        Initialize the widget with param = (aType, mId, fId, fId)
        
        """
        QtGui.QWidget.__init__(self, parent)
        self.param = param
        
        hLayout = QtGui.QHBoxLayout(self)
        hLayout.setMargin(0)
        hLayout.setSpacing(0)        
        self.setLayout(hLayout)

        hLayout.addSpacing(5+16+5)

        label = QtGui.QLabel(param[0])
        label.setFixedWidth(50)
        hLayout.addWidget(label)

        self.editor = QParameterEditor(param[0], param[1])
        hLayout.addWidget(self.editor)

        hLayout.addWidget(QDimensionSelector())

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
        if self.isChecked():
            painter.setPen(self.palette().color(QtGui.QPalette.WindowText))
        else:
            painter.setPen(self.palette().color(QtGui.QPalette.Dark))
        painter.setBrush(QtCore.Qt.NoBrush)
        l = min(self.width()-2, self.height()-2, 12)
        r = QtCore.QRect(0, 0, l, l)
        r.moveCenter(self.rect().center())
        painter.drawEllipse(r)

        if self.isChecked():
            r.adjust(2, 2, -2, -2)
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
    def __init__(self, pType, pValue, parent=None):
        """ QParameterEditor(pType: str, pValue: str, parent: QWidget)
                             -> QParameterEditor
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
            self.listValues.setText('["%s"]' % pValue.replace('"', '\"'))
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

    def getValues(self, size):
        """ getValues(size: int) -> []        
        Convert the list values into a list. Size specifies the size
        request. We ignore this for the list interpolator
        
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
        dialog = QListEditDialog(self.getValues(0), None)
        if dialog.exec_()==QtGui.QDialog.Accepted:
            values = dialog.getList()
            if self.type=='String':
                values = ['"%s"' % v.replace('"', '\"')
                          for v in values]
            self.listValues.setText('[%s]' % ', '.join(values))
            self.listValues.home(False)
        dialog.deleteLater()

class QListEditDialog(QtGui.QDialog):
    """
    QListEditDialog provides an interface for user to edit a list of
    values and export to a string
    """
    def __init__(self, values, parent=None):
        """ QListEditDialog(values: list, parent: QWidget) -> QListEditDialog
        Parse values and setup the table
        
        """
        QtGui.QDialog.__init__(self, parent)
        vLayout = QtGui.QVBoxLayout()
        vLayout.setMargin(0)
        vLayout.setSpacing(0)
        self.setLayout(vLayout)
        
        label = QtGui.QLabel('Please enter values in boxes below. '
                             'Drag rows up and down to arrange your '
                             'list values')
        label.setMargin(5)
        label.setWordWrap(True)
        vLayout.addWidget(label)

        self.table = QtGui.QTableWidget(len(values), 1)
        self.table.setHorizontalHeaderLabels(QtCore.QStringList('Values'))
        self.table.horizontalHeader().setStretchLastSection(True)            
        self.table.verticalHeader().setMovable(True)
        for i in range(len(values)):
            self.table.setItem(i, 0, QtGui.QTableWidgetItem(str(values[i])))
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
    
################################################################################

if __name__=="__main__":        
    import sys
    import gui.theme
    app = QtGui.QApplication(sys.argv)
    gui.theme.initializeCurrentTheme()
    vc = QDimensionLabel(CurrentTheme.EXPLORE_SHEET_PIXMAP, 'Hello World')
    vc.show()
    sys.exit(app.exec_())

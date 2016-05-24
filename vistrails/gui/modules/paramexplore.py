###############################################################################
##
## Copyright (C) 2014-2016, New York University.
## Copyright (C) 2011-2014, NYU-Poly.
## Copyright (C) 2006-2011, University of Utah.
## All rights reserved.
## Contact: contact@vistrails.org
##
## This file is part of VisTrails.
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met:
##
##  - Redistributions of source code must retain the above copyright notice,
##    this list of conditions and the following disclaimer.
##  - Redistributions in binary form must reproduce the above copyright
##    notice, this list of conditions and the following disclaimer in the
##    documentation and/or other materials provided with the distribution.
##  - Neither the name of the New York University nor the names of its
##    contributors may be used to endorse or promote products derived from
##    this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
## AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
## THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
## PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
## OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
## WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
## OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
## ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
###############################################################################
""" This file provides the basic infrastructure for extensible parameter
exploration. This allows user-defined constants to be used as dimensions
in parameter exploration, provided the user implements the appropriate
API in the classes.
"""
from __future__ import division

from PyQt4 import QtCore, QtGui
from vistrails.core.modules.basic_modules import Color
from vistrails.core import debug
from vistrails.core.modules.paramexplore import IntegerLinearInterpolator, \
   FloatLinearInterpolator, RGBColorInterpolator, HSVColorInterpolator

from vistrails.gui.common_widgets import QStringEdit
from vistrails.gui.modules.constant_configuration import ColorChooserButton
from vistrails.gui.modules.python_source_configure import PythonEditor
from vistrails.gui.modules.utils import get_param_explore_widget_list
from vistrails.gui.theme import CurrentTheme
from vistrails.gui.utils import show_warning
from vistrails.core.utils import all, unimplemented

##############################################################################

class QParameterEditor(QtGui.QWidget):
    """
    QParameterEditor specifies the method used for interpolating
    parameter values. It suppports Linear Interpolation, List and
    User-define function.
    
    """
    def __init__(self, param_info, size, parent=None):
        """ QParameterEditor(param_info: ParameterInfo,
                             size: int, parent=None: QWidget) -> QParameterEditor
        Put a stacked widget and a popup button
        
        """
        QtGui.QWidget.__init__(self, parent)
        self._param_info = param_info
        self.type = param_info.spec.descriptor.name
        self.defaultValue = param_info.value
        
        hLayout = QtGui.QHBoxLayout(self)
        hLayout.setMargin(0)
        hLayout.setSpacing(0)
        self.setLayout(hLayout)

        descriptor = param_info.spec.descriptor

        self.stackedEditors = QtGui.QStackedWidget()
        self.stackedEditors.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                          QtGui.QSizePolicy.Maximum)
        self._exploration_widgets = []

        def add_exploration_widget(wd):
            self._exploration_widgets.append(wd)
            self.stackedEditors.addWidget(wd)

        for widget_class in get_param_explore_widget_list(descriptor):
            new_widget = widget_class(param_info, size)
            add_exploration_widget(new_widget)

        add_exploration_widget(QListInterpolationEditor(param_info, size))
        add_exploration_widget(QUserFunctionEditor(param_info, size))

        hLayout.addWidget(self.stackedEditors)

        self.selector = QParameterEditorSelector(param_info, self._exploration_widgets)
        self.connect(self.selector.actionGroup,
                     QtCore.SIGNAL('triggered(QAction*)'),
                     self.changeInterpolator)
        hLayout.addWidget(self.selector)
        self.selector.initAction()

    def changeInterpolator(self, action):
        """ changeInterpolator(action: QAction) -> None        
        Bring the correct interpolation editing widget to front in the
        stacked widget
        
        """
        widgetIdx = action.data()
        if widgetIdx < self.stackedEditors.count():
            self.stackedEditors.setCurrentIndex(widgetIdx)

    def selectInterpolator(self, type):
        """ selectInterpolator(type: string) -> None
        Programatically (without requiring a user action) selects
        the interpolator specified by the name 'type'.  If no
        matching 'type' is found, no action is taken.
        
        """
        types = [widget.exploration_name for widget in self._exploration_widgets]
        if type in types:
            type_idx = types.index(type)
            self.selector._actions[type_idx].trigger()

class QParameterEditorSelector(QtGui.QToolButton):
    """
    QParameterEditorSelector is a button with a down arrow allowing
    users to select which type of interpolator he/she wants to use
    
    """
    def __init__(self, param_info, widget_list, parent=None):
        """ QParameterEditorSelector(param_info: ParameterInfo,
        widget_list: list of widgets that conform to the parameter
        exploration widget interface.
        """
        QtGui.QToolButton.__init__(self, parent)
        self._param_info = param_info
        self.type = param_info.spec.descriptor.name
        self.setAutoRaise(True)
        self.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        self.setPopupMode(QtGui.QToolButton.InstantPopup)
        
        self.setText(unichr(0x25bc)) # Down triangle

        self.actionGroup = QtGui.QActionGroup(self)

        self._actions = []
        for widget in widget_list:
            action = QtGui.QAction(widget.exploration_name, self.actionGroup)
            self._actions.append(action)

        aId = 0
        for action in self.actionGroup.actions():
            action.setCheckable(True)
            action.setData(aId)
            aId += 1

        menu = QtGui.QMenu(self)
        menu.addActions(self.actionGroup.actions())
        self.setMenu(menu)

    def initAction(self):
        """ initAction() -> None
        Select the first choice of selector based on self.type
        
        """
        self._actions[0].trigger()

##############################################################################

class BasePEWidget(object):
    def get_value(self):
        unimplemented()
    def set_value(self):
        unimplemented()
        
class QIntegerLineEdit(QtGui.QLineEdit, BasePEWidget):
    def __init__(self, param_info, parent=None):
        QtGui.QLineEdit.__init__(self, param_info.value, parent)
        self.setValidator(QtGui.QIntValidator(self))
    def get_value(self):
        return int(str(self.text()))
    def set_value(self, str_value):
        self.setText(str_value)
        
class QFloatLineEdit(QtGui.QLineEdit, BasePEWidget):
    def __init__(self, param_info, parent=None):
        QtGui.QLineEdit.__init__(self, param_info.value, parent)
        self.setValidator(QtGui.QDoubleValidator(self))
    def get_value(self):
        return float(str(self.text()))
    def set_value(self, str_value):
        self.setText(str_value)
##############################################################################

def make_interpolator(widget_class, interpolator_class, name):
    class InterpolationEditor(QtGui.QWidget):
        """
        QLinearInterpolationEditor is the actual widget allowing users to
        edit his/her linear interpolation parameters.

        """
        def __init__(self, param_info, size, parent=None):
            QtGui.QWidget.__init__(self, parent)
            self._param_info = param_info
            self.type = param_info.spec.descriptor.name

            hLayout = QtGui.QHBoxLayout(self)
            hLayout.setMargin(0)
            hLayout.setSpacing(0)
            self.setLayout(hLayout)

            self.fromEdit = widget_class(param_info)
            hLayout.addWidget(self.fromEdit)

            hLayout.addSpacing(5)

            rightArrow = QtGui.QLabel()
            pixmap = self.style().standardPixmap(QtGui.QStyle.SP_ArrowRight)
            rightArrow.setPixmap(CurrentTheme.RIGHT_ARROW_PIXMAP)
            hLayout.addWidget(rightArrow)

            hLayout.addSpacing(5)

            self.toEdit = widget_class(param_info)
            hLayout.addWidget(self.toEdit)
            self.exploration_name = name

        def get_values(self, size):
            """ get_values(size: int) -> tuple
            Return the interpolated list containing 'size' values

            """
            begin = self.fromEdit.get_value()
            end = self.toEdit.get_value()
            lerp = interpolator_class(begin, end, size)
            return lerp.get_values()
    return InterpolationEditor

FloatExploreWidget = make_interpolator(QFloatLineEdit,
                                       FloatLinearInterpolator,
                                       'Linear Interpolation')
IntegerExploreWidget = make_interpolator(QIntegerLineEdit,
                                         IntegerLinearInterpolator,
                                         'Linear Interpolation')

class PEColorChooserButton(ColorChooserButton, BasePEWidget):

    def __init__(self, param_info, parent=None):
        ColorChooserButton.__init__(self, parent)
        try:
            r,g,b = [int(float(i) * 255) for i in param_info.value.split(',')]
        except ValueError:
            r,g,b = (0.0, 0.0, 0.0)
        self.setColor(QtGui.QColor(r,g,b))
        self.setFixedHeight(22)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding,
                           QtGui.QSizePolicy.Fixed)

    def get_value(self):
        return Color.to_string(self.qcolor.redF(),
                               self.qcolor.greenF(),
                               self.qcolor.blueF())
        
    def set_value(self, str_value):
        color = str_value.split(',')
        qcolor = QtGui.QColor(float(color[0])*255,
                              float(color[1])*255,
                              float(color[2])*255)
        self.setColor(qcolor)

RGBExploreWidget = make_interpolator(PEColorChooserButton,
                                     RGBColorInterpolator,
                                     'RGB Interpolation')
HSVExploreWidget = make_interpolator(PEColorChooserButton,
                                     HSVColorInterpolator,
                                     'HSV Interpolation')

##############################################################################

class QListInterpolationEditor(QtGui.QWidget):
    """
    QListInterpolationEditor is the actual widget allowing users to
    enter a list of values for interpolation
    
    """
    def __init__(self, param_info, size, parent=None):
        """ QListInterpolationEditor(param_info: ParameterInfo, parent: QWidget)
                                     -> QListInterpolationEditor
        Construct an edit box with a button for bringing up the dialog
        
        """
        QtGui.QWidget.__init__(self, parent)
        self._param_info = param_info
        self.type = param_info.spec.descriptor.name
        
        hLayout = QtGui.QHBoxLayout(self)
        hLayout.setMargin(0)
        hLayout.setSpacing(0)
        self.setLayout(hLayout)
        
        self.listValues = QtGui.QLineEdit()
        if self.type=='String':
            self.listValues.setText("['%s']" % param_info.value.replace("'", "\'"))
        else:
            self.listValues.setText('[%s]' % param_info.value)
        self.listValues.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                      QtGui.QSizePolicy.Maximum)
        self.listValues.home(False)
        hLayout.addWidget(self.listValues)

        self.connect(self.listValues, QtCore.SIGNAL('textEdited(QString)'),
                     self.values_were_edited)

        inputButton = QtGui.QToolButton()
        inputButton.setText('...')
        self.connect(inputButton, QtCore.SIGNAL('clicked()'),
                     self.editListValues)
        hLayout.addWidget(inputButton)
        self.exploration_name = 'List'
        self._str_values = [param_info.value]

    def values_were_edited(self, new_text):
        """values_were_edited(new_text): None

        Connected to self.listValues.textEdited. Updates self._str_values.
        
        NB: Allowing the user to edit the LineEdit field directly is
        not a very good idea, because we don't know what are the
        syntactic rules for the translate_to_python() calls in
        arbitrary classes.  Right now, I'm assuming removing the
        leading and trailing brackets and splitting on ',' is
        enough. (in passing, The previous call to eval() is just
        broken is a general scenario like we have now)

        For example, this will break horribly if the user manually edits
        a list of strings with commas in them."""

        t = str(new_text)
        if len(t) < 2:
            self._str_values = []
            return
        if not (t[0] == '[' and t[-1] == ']'):
            self._str_values = []
        else: 
            self._str_values = t[1:-1].split(',')
            if self._param_info.spec.descriptor.name=='String':
                for i, val in enumerate(self._str_values):
                    val = val.strip()
                    if len(val) >= 2 and  \
                            ((val[0] == "'" and val[-1] == "'") or 
                             (val[0] == '"' and val[-1] == '"')):
                        self._str_values[i] = val.strip()[1:-1]

    def get_values(self, count):
        """ get_values(count) -> []        
        Convert the list values into a list

        count should be an integer with the expected size of the list (given
        by the dimension 'size' in the exploration)
        
        """

        param_info = self._param_info
        module = param_info.spec.descriptor.module
        result = [module.translate_to_python(m)
                  for m in self._str_values]
        if len(result) != count:
            show_warning('Inconsistent Size',
                         'One of the <i>%s</i>\'s list '
                         'interpolated '
                         'values has a different '
                         'size from the step count. '
                         'Expected %d, got %d instead. '
                         'Parameter Exploration aborted.'
                         % (self.type, count, len(result)))
            return None
        return result

    def editListValues(self):
        """ editListValues() -> None
        Show a dialog for editing the values
        
        """
        dialog = QListEditDialog(self.type, self._str_values, None)
        if dialog.exec_() == QtGui.QDialog.Accepted:
            values = dialog.getList()
            self._str_values = [str(v) for v in values]
            if self.type == 'String':
                values = ["'%s'" % v.replace("'", "\'")
                          for v in values]
            self.listValues.setText('[%s]' % ', '.join(values))
            self.listValues.home(False)
        dialog.deleteLater()

##############################################################################

class QListEditDialog(QtGui.QDialog):
    """
    QListEditDialog provides an interface for user to edit a list of
    values and export to a string
    
    """
    def __init__(self, pType, strValues, parent=None):
        """ QListEditDialog(pType: str, strValues: list, parent: QWidget)
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
        self.table.setHorizontalHeaderLabels(['Values'])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setMovable(True)
        self.table.verticalHeader().setResizeMode(
            QtGui.QHeaderView.ResizeToContents)
        self.delegate = QListEditItemDelegate()
        self.table.setItemDelegate(self.delegate)
        self.table.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        for v in strValues:
            self.addRow(v)
        self.connect(self.table.verticalHeader(),
                     QtCore.SIGNAL('sectionMoved(int,int,int)'),
                     self.rowMoved)
        vLayout.addWidget(self.table)

        hLayout = QtGui.QHBoxLayout()        
        vLayout.addLayout(hLayout)

        okButton = QtGui.QPushButton('&OK')
        okButton.setSizePolicy(QtGui.QSizePolicy.Maximum,
                               QtGui.QSizePolicy.Maximum)
        self.connect(okButton, QtCore.SIGNAL('clicked()'), self.okButtonPressed)
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

    def okButtonPressed(self):
        """ okButtonPressed() -> None
        Make sure to commit the editor data before accepting
        
        """
        self.table.itemDelegate().finishEditing()
        self.accept()

    def getList(self):
        """ getList() -> list of str values
        Return a list of values
        
        """
        result = []
        for i in xrange(self.table.rowCount()):
            logicalIndex = self.table.verticalHeader().logicalIndex(i)
            value = self.table.item(logicalIndex, 0).text()            
            result.append(str(value))
        return result

    def rowMoved(self, row, old, new):
        """ rowMove(row: int, old: int, new: int) -> None
        Renumber the vertical header labels when row moved
        
        """
        vHeader = self.table.verticalHeader()
        labels = []        
        for i in xrange(self.table.rowCount()):
            labels.append(str(vHeader.visualIndex(i)+1))
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

##############################################################################

class QListEditItemDelegate(QtGui.QItemDelegate):
    """
    QListEditItemDelegate sets up the editor for the QListEditDialog
    table
    
    """

    def __init__(self, parent=None):
        """ QListEditItemDelegate(parent: QWidget) -> QListEditItemDelegate
        Store the uncommit editor for commit later
        
        """
        QtGui.QItemDelegate.__init__(self, parent)
        self.editor = None
        
    def createEditor(self, parent, option, index):
        """ createEditor(parent: QWidget,
                         option: QStyleOptionViewItem,
                         index: QModelIndex) -> QStringEdit
        Return the editor widget for the index
        
        """
        self.editor = QStringEdit(parent)
        return self.editor

    def setEditorData(self, editor, index):
        """ setEditorData(editor: QWidget, index: QModelIndex) -> None
        Set the editor to reflects data at index
        
        """
        editor.setText(index.data())
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
        model.setData(index, editor.text())
        self.editor = None

    def finishEditing(self):
        if self.editor:
            self.emit(QtCore.SIGNAL('commitData(QWidget*)'), self.editor)

##############################################################################

class QUserFunctionEditor(QtGui.QFrame):
    """
    QUserFunctionEditor shows user-defined interpolation function
    
    """
    def __init__(self, param_info, size, parent=None):
        """ QUserFunctionEditor(param_info: ParameterInfo, parent: QWidget)
                                -> QUserFunctionEditor
        Create a read-only line edit widget and a button for
        customizing the user-defined function
        
        """
        QtGui.QFrame.__init__(self, parent)
        self.setFrameStyle(QtGui.QFrame.Box | QtGui.QFrame.Sunken)
        self.size = -1
        self._param_info = param_info
        self.type = param_info.spec.descriptor.name
        self.defaultValue = param_info.value
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

        self.size_was_updated(size)

        inputButton = QtGui.QToolButton()
        inputButton.setText('...')
        self.connect(inputButton, QtCore.SIGNAL('clicked()'),
                     self.editFunction)
        hLayout.addWidget(inputButton)
        self.exploration_name = 'User-defined Function'

    def defaultFunction(self):
        """ defaultFunction() -> str
        Return the default function definition
        
        """
        if self.type=='String':
            quote = '"'
        else:
            quote = ''
        return 'def value(i):\n    """ value(i: int) -> value\n'\
               '    Returns the i-th value\n'\
               '    i is from 0 to <step count>-1.\n'\
               '    If this function has an error, the value will be\n'\
               '    the default constant value\n'\
               '    """\n'\
               '    # Define your function here\n'

    def get_values(self, count):
        """ get_values() -> []        
        Convert the user define function into a list. Size specifies the size
        request.
        
        """
        param_info = self._param_info
        module = param_info.spec.descriptor.module
        def get():
            values = []
            d = {}
            try:
                exec(self.function) in {}, d
            except Exception, e:
                return [module.default_value] * count
            def evaluate(i):
                try:
                    v = d['value'](i)
                    if v is None:
                        return module.default_value
                    return v
                except Exception, e:
                    debug.unexpected_exception(e)
                    return debug.format_exception(e)
            return [evaluate(i) for i in xrange(self.size)]
        result = get()
        
        if not all(module.validate(x) for x in result):
            show_warning('Failed Validation',
                         'One of the <i>%s</i>\'s user defined '
                         'functions has failed validation, '
                         'which usually means it generated a '
                         'value of a type different '
                         'than that specified by the '
                         'parameter. Parameter Exploration '
                         'aborted.' % param_info.spec.descriptor.name)
            return None
        return result
        

    def getValuesString(self):
        """ getValuesString() -> str
        Return a string representation of the parameter list
        
        """
        r = self.get_values(self.size)
        if r is None:
            return '{ERROR}'
        else:
            return '{%s}' % ','.join([str(v) for v in r])

    def editFunction(self):
        """ editFunction() -> None
        Pop up a dialog for editing user-defined function
        
        """
        dialog = QUserFunctionDialog(self.function)        
        if dialog.exec_()==QtGui.QDialog.Accepted:
            self.function = str(dialog.editor.toPlainText())
            self.listValues.setText(self.getValuesString())
        dialog.deleteLater()

    def size_was_updated(self, size):
        """ size_was_updated(size: int) -> None

        This is called whenever the size of the interpolation is changed.
        Values are re-calculated."""
        if size!=self.size:
            self.size = size
            htmlText = '<html><big>&fnof;</big>(n) <b>:</b> ' \
                       '[0,%d) &rarr; </html>' % size
            self.label.setText(htmlText)
            self.listValues.setText(self.getValuesString())

##############################################################################

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
        self.setWindowTitle('User-defined Function')
        
        label = QtGui.QLabel("Please define your function below. This "
                             "'value(i)' function will be iteratively called "
                             "for <step count> numbers. For each step, "
                             "it should return a value of parameter type.")
        label.setMargin(5)
        label.setWordWrap(True)
        vLayout.addWidget(label)

        self.editor = PythonEditor(self)
        self.editor.setPlainText(function)
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

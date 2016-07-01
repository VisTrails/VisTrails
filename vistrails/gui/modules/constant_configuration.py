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
""" This file specifies the configuration widget for Constant
modules. Please notice that this is different from the module configuration
widget described in module_configure.py. We present a Color constant to be
used as a template for creating a configuration widget for other custom
constants.

"""

from __future__ import division

from PyQt4 import QtCore, QtGui
from vistrails.core.utils import any, expression, versions_increasing
from vistrails.core import system
from vistrails.gui.theme import CurrentTheme

import copy
import os

############################################################################

def setPlaceholderTextCompat(self, value):
    """ Qt pre 4.7.0 does not have setPlaceholderText
    """
    if versions_increasing(QtCore.QT_VERSION_STR, '4.7.0'):
        self.setText(value)
    else:
        self.setPlaceholderText(value)

class ConstantWidgetMixin(object):

    # subclasses need to add this signal:
    # contentsChanged = QtCore.pyqtSignal(tuple)

    def __init__(self, contents=None):
        if not hasattr(self, 'contentsChanged'):
            raise Exception('ConstantWidget must define contentsChanged signal')
        self._last_contents = contents
        self.psi = None

    def update_parent(self):
        newContents = self.contents()
        
        if newContents != self._last_contents:
            if self.parent() and hasattr(self.parent(), 'updateMethod'):
                self.parent().updateMethod()
            self._last_contents = newContents
            self.contentsChanged.emit((self, newContents))

class ConstantWidgetBase(ConstantWidgetMixin):
    class FocusFilter(QtCore.QObject):
        def __init__(self, cwidget):
            QtCore.QObject.__init__(self, cwidget)
            self.__cwidget = cwidget

        def eventFilter(self, o, event):
            if event.type() == QtCore.QEvent.FocusIn:
                self.__cwidget._focus_in(event)
            elif event.type() == QtCore.QEvent.FocusOut:
                self.__cwidget._focus_out(event)
            return False

    def __init__(self, param):
        if param is None:
            raise ValueError("Must pass param as first argument.")
        psi = param.port_spec_item

        if not param.strValue and psi and psi.default:
            value = psi.default
        else:
            value = param.strValue
        ConstantWidgetMixin.__init__(self, value)

        self.psi = psi
        if psi and psi.default and param.strValue == '':
            self.setDefault(psi.default)
        else:
            self.setContents(param.strValue)

        self.__focus_filter = self.FocusFilter(self)
        self.installEventFilter(self.__focus_filter)

    def watchForFocusEvents(self, widget):
        widget.installEventFilter(self.__focus_filter)

    def setDefault(self, value):
        # default to setting the contents silenty
        self.setContents(value, True)

    def setContents(self, strValue, silent=True):
        raise NotImplementedError("Subclass must implement this method.")

    def contents(self):
        raise NotImplementedError("Subclass must implement this method.")

    def eventFilter(self, o, event):
        if event.type() == QtCore.QEvent.FocusIn:
            self._focus_in(event)
        elif event.type() == QtCore.QEvent.FocusOut:
            self._focus_out(event)
        return False

    def _focus_in(self, event):
        """ focusInEvent(event: QEvent) -> None
        Pass the event to the parent

        """
        if self.parent():
            QtCore.QCoreApplication.sendEvent(self.parent(), event)

    def _focus_out(self, event):
        self.update_parent()
        if self.parent():
            QtCore.QCoreApplication.sendEvent(self.parent(), event)

class ConstantEnumWidgetBase(ConstantWidgetBase):
    def __init__(self, param):
        psi = param.port_spec_item
        self.setValues(psi.values)

        self.setFree(psi.entry_type == "enumFree")
        self.setNonEmpty(psi.entry_type == "enumNonEmpty")

        ConstantWidgetBase.__init__(self, param)

    def setValues(self, values):
        raise NotImplementedError("Subclass must implement this method.")

    def setFree(self, is_free):
        pass

    def setNonEmpty(self, is_non_empty):
        pass

class QGraphicsLineEdit(QtGui.QGraphicsTextItem, ConstantWidgetBase):
    """ A GraphicsItem version of ConstantWidget

    """
    contentsChanged = QtCore.pyqtSignal(tuple)
    def __init__(self, param, parent=None):
        QtGui.QGraphicsTextItem.__init__(self, parent)
        self.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)
        self.setTabChangesFocus(True)
        self.setFont(CurrentTheme.MODULE_EDIT_FONT)
        self.installEventFilter(self)
        self.offset = 0
        self.is_valid = True
        self.document().setDocumentMargin(1)
        ConstantWidgetBase.__init__(self, param)
        self.document().contentsChanged.connect(self.ensureCursorVisible)

    def setContents(self, value, silent=False):
        self.setPlainText(expression.evaluate_expressions(value))
        if not silent:
            self.update_parent()
        block = self.document().firstBlock()
        w = self.document().documentLayout().blockBoundingRect(block).width()
        self.offset = max(w - 140, 0)
        block.layout().lineAt(0).setPosition(QtCore.QPointF(-self.offset,0))
        self.validate(value)

    def contents(self):
        contents = expression.evaluate_expressions(unicode(self.toPlainText()))
        self.setPlainText(contents)
        self.validate(contents)
        return contents

    def validate(self, value):
        try:
            self.psi and \
            self.psi.descriptor.module.translate_to_python(value)
        except Exception, e:
            self.setToolTip("Invalid value: %s" % str(e))
            self.is_valid = False
        else:
            self.setToolTip("")
            self.is_valid = True

    def setDefault(self, value):
        self.setContents(value, silent=True)

    def boundingRect(self):
        # calc font height
        #height = CurrentTheme.MODULE_EDIT_FONT_METRIC.height()
        height = 11 # hardcoded because fontmetric can give wrong value
        return QtCore.QRectF(0.0, 0.0, 150, height + 3)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress and \
           event.key() in [QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return]:
                self.clearFocus()
                return True
        result = QtGui.QGraphicsTextItem.eventFilter(self, obj, event)
        if event.type() in [QtCore.QEvent.KeyPress, QtCore.QEvent.MouseButtonPress, QtCore.QEvent.GraphicsSceneMouseMove]:
            if not self.hasFocus():
                self.setFocus()
            self.ensureCursorVisible()
        return result

    def ensureCursorVisible(self):
        block = self.document().firstBlock()
        line = block.layout().lineAt(0)
        pos = line.cursorToX(self.textCursor().positionInBlock())
        cursor = self.document().documentLayout().blockBoundingRect(\
                                     block).y() + pos[0] - line.position().x()
        w = self.document().documentLayout().blockBoundingRect(block).width()
        if cursor - self.offset > 130:
            self.offset = min(w-140, self.offset + 25)
        if cursor - self.offset < 20:
            self.offset = max(0, self.offset - 25)
        line.setPosition(QtCore.QPointF(-self.offset,0))
        self.update()

    def focusOutEvent(self, event):
        self.update_parent()
        result = QtGui.QGraphicsTextItem.focusOutEvent(self, event)
        # show last part of text
        block = self.document().firstBlock()
        w = self.document().documentLayout().blockBoundingRect(block).width()
        self.offset = max(w - 140, 0)
        block.layout().lineAt(0).setPosition(QtCore.QPointF(-self.offset,0))
        return result

    def focusInEvent(self, event):
        result = QtGui.QGraphicsTextItem.focusInEvent(self, event)
        # set cursor to last if not already set
        cursor = self.textCursor()
        cursor.setPosition(self.document().firstBlock().length()-1)
        self.setTextCursor(cursor)
        return result

    def paint(self, painter, option, widget):
        """ Override striped selection border
            First unset selected and hasfocus flags
            Then draw custom rect """
        s = QtGui.QStyle.State_Selected | QtGui.QStyle.State_HasFocus
        state = s.__class__(option.state) # option.state
        option.state &= ~s
        painter.pen().setWidth(1)
        result = QtGui.QGraphicsTextItem.paint(self, painter, option, widget)
        option.state = state

        if state & s:
            color = QtGui.QApplication.palette().color(QtGui.QPalette.Highlight)
            painter.setPen(QtGui.QPen(color, 0))
            painter.drawRect(self.boundingRect())
        elif not self.is_valid:
            painter.setPen(QtGui.QPen(CurrentTheme.PARAM_INVALID_COLOR, 0))
            painter.drawRect(self.boundingRect())
        else:
            color = QtGui.QApplication.palette().color(QtGui.QPalette.Dark)
            painter.setPen(QtGui.QPen(color, 0))
            painter.drawRect(self.boundingRect())
        return result

class StandardConstantWidget(QtGui.QLineEdit,ConstantWidgetBase):
    contentsChanged = QtCore.pyqtSignal(tuple)
    GraphicsItem = QGraphicsLineEdit
    def __init__(self, param, parent=None):
        QtGui.QLineEdit.__init__(self, parent)
        ConstantWidgetBase.__init__(self, param)
        self.connect(self, QtCore.SIGNAL("returnPressed()"), 
                     self.update_parent)

    def setContents(self, value, silent=False):
        self.setText(expression.evaluate_expressions(value))
        self.validate(value)
        if not silent:
            self.update_parent()

    def contents(self):
        contents = expression.evaluate_expressions(unicode(self.text()))
        self.setText(contents)
        self.validate(contents)
        return contents

    def validate(self, value):
        try:
            self.psi and \
            self.psi.descriptor.module.translate_to_python(value)
        except Exception, e:
            # Color background yellow and add tooltip
            self.setStyleSheet("border:2px dashed %s;" %
                               CurrentTheme.PARAM_INVALID_COLOR.name())
            self.setToolTip("Invalid value: %s" % str(e))
        else:
            self.setStyleSheet("")
            self.setToolTip("")

    def setDefault(self, value):
        setPlaceholderTextCompat(self, value)

def findEmbeddedParentWidget(widget):
    """ See showPopup below

    """
    if widget.graphicsProxyWidget():
        return widget
    elif widget.parentWidget():
        return findEmbeddedParentWidget(widget.parentWidget())
    return None

class StandardConstantEnumWidget(QtGui.QComboBox, ConstantEnumWidgetBase):
    contentsChanged = QtCore.pyqtSignal(tuple)
    GraphicsItem = None
    def __init__(self, param, parent=None):
        QtGui.QComboBox.__init__(self, parent)
        ConstantEnumWidgetBase.__init__(self, param)
        self.connect(self,
                     QtCore.SIGNAL('currentIndexChanged(int)'),
                     self.update_parent)

    def setValues(self, values):
        self.addItems(values)

    def setFree(self, is_free):
        if is_free:
            self.setEditable(True)
            self.setInsertPolicy(QtGui.QComboBox.NoInsert)
            self.connect(self.lineEdit(),
                         QtCore.SIGNAL('returnPressed()'),
                         self.update_parent)

    def setNonEmpty(self, is_non_empty):
        if not is_non_empty:
            self.setCurrentIndex(-1)

    def contents(self):
        return self.currentText()

    def setContents(self, strValue, silent=True):
        idx = self.findText(strValue)
        if idx > -1:
            self.setCurrentIndex(idx)
            if self.isEditable():
                self.lineEdit().setText(strValue)
        elif self.isEditable():
            self.lineEdit().setText(strValue)

    def setDefault(self, value):
        idx = self.findText(value)
        if idx > -1:
            self.setCurrentIndex(idx)
            if self.isEditable():
                setPlaceholderTextCompat(self.lineEdit(), value)
        elif self.isEditable():
            setPlaceholderTextCompat(self.lineEdit(), value)

    def showPopup(self, *args, **kwargs):
        """ Fixes popup when use in a GraphicsView. See:
             https://bugreports.qt-project.org/browse/QTBUG-14090

        """

        QtGui.QComboBox.showPopup(self, *args, **kwargs)
        parent = findEmbeddedParentWidget(self)
        if parent:
            item = parent.graphicsProxyWidget()
            scene = item.scene()
            view = None
            if scene:
                views = scene.views()
                for v in views:
                    if v == QtGui.QApplication.focusWidget():
                        view = v
                if not view:
                    view = views[0]
            if view:
                br = item.boundingRect()
                rightPos = view.mapToGlobal(view.mapFromScene(item.mapToScene(
                                    QtCore.QPointF(br.width(), br.height()))))
                pos = view.mapToGlobal(view.mapFromScene(item.mapToScene(
                                             QtCore.QPointF(0, br.height()))))
                self.view().parentWidget().move(pos)
                self.view().parentWidget().setFixedWidth(rightPos.x()-pos.x())
                self.view().parentWidget().installEventFilter(self)

    def eventFilter(self, o, e):
        """ See showPopup

        """

        if o.parentWidget() and e.type() == QtCore.QEvent.MouseButtonPress:
            return True
        return QtGui.QComboBox.eventFilter(self, o, e)



###############################################################################
# Multi-line String Widget

class MultiLineStringWidget(QtGui.QTextEdit, ConstantWidgetBase):
    contentsChanged = QtCore.pyqtSignal(tuple)
    def __init__(self, param, parent=None):
        QtGui.QTextEdit.__init__(self, parent)
        self.setAcceptRichText(False)
        ConstantWidgetBase.__init__(self, param)

    def setContents(self, contents):
        self.setPlainText(expression.evaluate_expressions(contents))

    def contents(self):
        contents = expression.evaluate_expressions(unicode(self.toPlainText()))
        self.setPlainText(contents)
        return contents

    def sizeHint(self):
        metrics = QtGui.QFontMetrics(self.font())
        # On Mac OS X 10.8, the scrollbar doesn't show up correctly
        # with 3 lines
        return QtCore.QSize(QtGui.QTextEdit.sizeHint(self).width(),
                            (metrics.height() + 1) * 4 + 5)

    def minimumSizeHint(self):
        return self.sizeHint()

###############################################################################
# File Constant Widgets

class PathChooserWidget(QtGui.QWidget, ConstantWidgetMixin):
    """
    PathChooserWidget is a widget containing a line edit and a button that
    opens a browser for paths. The lineEdit is updated with the pathname that is
    selected.

    """    
    contentsChanged = QtCore.pyqtSignal(tuple)
    def __init__(self, param, parent=None):
        """__init__(param: core.vistrail.module_param.ModuleParam,
        parent: QWidget)
        Initializes the line edit with contents

        """
        QtGui.QWidget.__init__(self, parent)
        ConstantWidgetMixin.__init__(self, param.strValue)
        layout = QtGui.QHBoxLayout()
        self.line_edit = StandardConstantWidget(param, self)
        self.browse_button = self.create_browse_button()
        layout.setMargin(0)
        layout.setSpacing(5)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.browse_button)
        self.setLayout(layout)

    def create_browse_button(self, cls=None):
        from vistrails.gui.common_widgets import QPathChooserToolButton
        if cls is None:
            cls = QPathChooserToolButton
        button = cls(self, self.line_edit, 
                     defaultPath=system.vistrails_data_directory())
        button.pathChanged.connect(self.update_parent)
        return button

    def updateMethod(self):
        if self.parent() and hasattr(self.parent(), 'updateMethod'):
            self.parent().updateMethod()

    def contents(self):
        """contents() -> str
        Return the contents of the line_edit

        """
        return self.line_edit.contents()
    
    def setContents(self, strValue, silent=True):
        """setContents(strValue: str) -> None
        Updates the contents of the line_edit 
        """
        self.line_edit.setContents(strValue, silent)
        if not silent:
            self.update_parent()
 
        
    def focusInEvent(self, event):
        """ focusInEvent(event: QEvent) -> None
        Pass the event to the parent

        """
        if self.parent():
            QtCore.QCoreApplication.sendEvent(self.parent(), event)
        QtGui.QWidget.focusInEvent(self, event)   
        
    def focusOutEvent(self, event):
        self.update_parent()
        QtGui.QWidget.focusOutEvent(self, event)
        if self.parent():
            QtCore.QCoreApplication.sendEvent(self.parent(), event)

class FileChooserWidget(PathChooserWidget):
    def create_browse_button(self):
        from vistrails.gui.common_widgets import QFileChooserToolButton
        return PathChooserWidget.create_browse_button(self, 
                                                      QFileChooserToolButton)

class DirectoryChooserWidget(PathChooserWidget):
    def create_browse_button(self):
        from vistrails.gui.common_widgets import QDirectoryChooserToolButton
        return PathChooserWidget.create_browse_button(self, 
                                                QDirectoryChooserToolButton)

class OutputPathChooserWidget(PathChooserWidget):
    def create_browse_button(self):
        from vistrails.gui.common_widgets import QOutputPathChooserToolButton
        return PathChooserWidget.create_browse_button(self, 
                                                QOutputPathChooserToolButton)

###############################################################################
# Constant Boolean widget

class BooleanWidget(QtGui.QCheckBox, ConstantWidgetBase):

    _values = ['True', 'False']
    _states = [QtCore.Qt.Checked, QtCore.Qt.Unchecked]

    contentsChanged = QtCore.pyqtSignal(tuple)
    def __init__(self, param, parent=None):
        """__init__(param: core.vistrail.module_param.ModuleParam,
                    parent: QWidget)
        Initializes the line edit with contents
        """
        QtGui.QCheckBox.__init__(self, parent)
        ConstantWidgetBase.__init__(self, param)
        self.connect(self, QtCore.SIGNAL('stateChanged(int)'),
                     self.change_state)
        
    def contents(self):
        return self._values[self._states.index(self.checkState())]

    def setContents(self, strValue, silent=True):
        if strValue not in self._values:
            return
        self.setCheckState(self._states[self._values.index(strValue)])
        if not silent:
            self.update_parent()


    def change_state(self, state):
        self.update_parent()

###############################################################################
# Constant Color widgets

# FIXME ColorChooserButton remains because the parameter exploration
# code uses it, really should be removed at some point
class ColorChooserButton(QtGui.QPushButton):
    contentsChanged = QtCore.pyqtSignal(tuple)
    def __init__(self, parent=None):
        QtGui.QPushButton.__init__(self, parent)
        # self.setFrameStyle(QtGui.QFrame.Box | QtGui.QFrame.Plain)
        # self.setAttribute(QtCore.Qt.WA_PaintOnScreen)
        self.setFlat(True)
        self.setAutoFillBackground(True)
        self.setColor(QtGui.QColor(255,255,255))
        self.setFixedSize(30,22)
        if system.systemType == 'Darwin':
            #the mac's nice look messes up with the colors
            self.setAttribute(QtCore.Qt.WA_MacMetalStyle, False)
        self.clicked.connect(self.openChooser)

    def setColor(self, qcolor, silent=True):
        self.qcolor = qcolor
        self.setStyleSheet("border: 1px solid black; "
                           "background-color: rgb(%d, %d, %d);" %
                           (qcolor.red(), qcolor.green(), qcolor.blue()))
        self.update()
        if not silent:
            self.emit(QtCore.SIGNAL("color_selected"))

    def sizeHint(self):
        return QtCore.QSize(24,24)

    def openChooser(self):
        """
        openChooser() -> None

        """
        color = QtGui.QColorDialog.getColor(self.qcolor, self.parent())
        if color.isValid():
            self.setColor(color, silent=False)
        else:
            self.setColor(self.qcolor)

class QColorWidget(QtGui.QToolButton):
    def __init__(self, parent=None):
        QtGui.QToolButton.__init__(self, parent)
        self.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.setIconSize(QtCore.QSize(26,18))        
        self.color_str = '1.0,1.0,1.0'

    def colorFromString(self, color_str):
        color = color_str.split(',')
        return QtGui.QColor(float(color[0])*255,
                            float(color[1])*255,
                            float(color[2])*255)

    def stringFromColor(self, qcolor):
        return "%s,%s,%s" % (qcolor.redF(), qcolor.greenF(), qcolor.blueF())

    def buildIcon(self, qcolor, qsize):
        pixmap = QtGui.QPixmap(qsize)
        pixmap.fill(qcolor)
        return QtGui.QIcon(pixmap)

    def setColorString(self, color_str, silent=True):
        if color_str != '':
            self.color_str = color_str
            qcolor = self.colorFromString(color_str)
            self.setIcon(self.buildIcon(qcolor, self.iconSize()))
            if not silent:
                self.update_parent()

    def setColor(self, qcolor, silent=True):
        self.setIcon(self.buildIcon(qcolor, self.iconSize()))
        self.color_str = self.stringFromColor(qcolor)
        if not silent:
            self.update_parent()

    def openChooser(self):
        """
        openChooser() -> None

        """
        qcolor = self.colorFromString(self.color_str)
        color = QtGui.QColorDialog.getColor(qcolor, self.parent())
        if color.isValid():
            self.setColor(color, silent=False)
        else:
            self.setColor(qcolor)

class ColorWidget(QColorWidget, ConstantWidgetBase):
    contentsChanged = QtCore.pyqtSignal(tuple)
    def __init__(self, param, parent=None):
        QColorWidget.__init__(self, parent)
        ConstantWidgetBase.__init__(self, param)
        self.connect(self, QtCore.SIGNAL("clicked()"), self.openChooser)

    def contents(self):
        return self.color_str

    def setContents(self, strValue, silent=True):
        self.setColorString(strValue, silent)

class ColorEnumWidget(QColorWidget, ConstantEnumWidgetBase):
    contentsChanged = QtCore.pyqtSignal(tuple)
    def __init__(self, param, parent=None):
        QColorWidget.__init__(self, parent)
        self.setPopupMode(QtGui.QToolButton.MenuButtonPopup)
        ConstantEnumWidgetBase.__init__(self, param)
    
    def setFree(self, is_free):
        if is_free:
            self.connect(self, QtCore.SIGNAL("clicked()"), self.openChooser)

    def wasTriggered(self, action):
        self.setColorString(action.data())
        self.update_parent()

    def setValues(self, values):
        menu = QtGui.QMenu()
        self.action_group = QtGui.QActionGroup(menu)
        self.action_group.setExclusive(True)
        self.connect(self.action_group, QtCore.SIGNAL('triggered(QAction*)'),
                     self.wasTriggered)
        size = menu.style().pixelMetric(QtGui.QStyle.PM_SmallIconSize)
        for i, color_str in enumerate(values):
            qcolor = self.colorFromString(color_str)
            icon = self.buildIcon(qcolor, QtCore.QSize(size, size))
            action = menu.addAction(icon, "")
            action.setIconVisibleInMenu(True)
            action.setData(color_str)
            action.setCheckable(True)
            self.action_group.addAction(action)
        self.setMenu(menu)

    def contents(self):
        return self.color_str

    def setContents(self, strValue, silent=True):
        self.setColorString(strValue)
        for action in self.action_group.actions():
            if action.data() == strValue:
                action.setChecked(True)

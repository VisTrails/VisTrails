###############################################################################
##
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
##  - Neither the name of the University of Utah nor the names of its 
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
""" This file contains widgets that can be used for dropping Constant class
variables. It will construct an input form for the value.

QVariableDropBox
QVerticalWidget
QVariableInputWidget
QVariableInputForm
QDragVariableLabel
QHoverVariableLabel
"""
from PyQt4 import QtCore, QtGui
from vistrails.core import debug
from vistrails.core.vistrail.module_function import ModuleFunction
from vistrails.core.vistrail.module_param import ModuleParam
from vistrails.core.modules import module_registry
from vistrails.core.modules.basic_modules import Constant
from vistrails.core.vistrail.vistrailvariable import VistrailVariable
from vistrails.gui.common_widgets import QPromptWidget
from vistrails.gui.modules.utils import get_widget_class
from vistrails.gui.modules.constant_configuration import StandardConstantWidget
from vistrails.gui.module_palette import QModuleTreeWidget
from vistrails.gui.theme import CurrentTheme
from vistrails.gui.utils import show_question, YES_BUTTON, NO_BUTTON
import uuid

################################################################################

class QVariableDropBox(QtGui.QScrollArea):
    """
    QVariableDropBox is just a widget such that items that subclass
    Constant from the module palette can be dropped into its client rect.
    It then constructs an input form based on the type of handling widget
    
    """
    def __init__(self, parent=None):
        """ QVariableDropBox(parent: QWidget) -> QVariableDropBox
        Initialize widget constraints
        
        """
        QtGui.QScrollArea.__init__(self, parent)
        self.setAcceptDrops(True)
        self.setWidgetResizable(True)
        self.vWidget = QVerticalWidget()
        self.setWidget(self.vWidget)
        self.updateLocked = False
        self.controller = None

    def dragEnterEvent(self, event):
        """ dragEnterEvent(event: QDragEnterEvent) -> None
        Set to accept drops from the module palette
        
        """
        if isinstance(event.source(), QModuleTreeWidget):
            data = event.mimeData()
            if hasattr(data, 'items'):
                event.accept()
        else:
            event.ignore()
        
    def dragMoveEvent(self, event):
        """ dragMoveEvent(event: QDragMoveEvent) -> None
        Set to accept drag move event from the module palette
        
        """
        if isinstance(event.source(), QModuleTreeWidget):
            data = event.mimeData()
            if hasattr(data, 'items'):
                event.accept()

    def dropEvent(self, event):
        """ dropEvent(event: QDragMoveEvent) -> None
        Accept drop event to add a new variable
        
        """
        if isinstance(event.source(), QModuleTreeWidget):
            data = event.mimeData()
            if hasattr(data, 'items'):
                event.accept()
                assert len(data.items) == 1
                item = data.items[0]
                if issubclass(item.descriptor.module, Constant):
                    if item.descriptor and self.controller:
                        self.lockUpdate()
                        (text, ok) = QtGui.QInputDialog.getText(self,
                                                                'Set Variable Name',
                                                                'Enter the variable name',
                                                                QtGui.QLineEdit.Normal,
                                                                '')
                        var_name = str(text).strip()
                        while ok and self.controller.check_vistrail_variable(var_name):
                            msg =" This variable name is already being used.\
 Please enter a different variable name "
                            (text, ok) = QtGui.QInputDialog.getText(self,
                                                                    'Set Variable Name',
                                                                    msg,
                                                                    QtGui.QLineEdit.Normal,
                                                                    text)
                            var_name = str(text).strip()
                        if ok:
                            self.vWidget.addVariable(str(uuid.uuid1()), var_name, item.descriptor)
                            self.scrollContentsBy(0, self.viewport().height())
                        self.unlockUpdate()
                #self.emit(QtCore.SIGNAL("paramsAreaChanged"))

    def updateController(self, controller):
        """ updateController(controller: VistrailController) -> None
        Construct input forms for a controller's variables
        
        """
        # we shouldn't do this whenver the controller changes...
        if self.controller != controller:
            self.controller = controller
            if self.updateLocked: return
            self.vWidget.clear()
            if controller:
                reg = module_registry.get_module_registry()
                for var in [v for v in controller.vistrail.vistrail_vars]:
                    try:
                        descriptor = reg.get_descriptor_by_name(var.package,
                                                                var.module, 
                                                                var.namespace)
                    except module_registry.ModuleRegistryException:
                        debug.critical("Missing Module Descriptor for vistrail"
                                       " variable %s\nPackage: %s\nType: %s"
                                       "\nNamespace: %s" % \
                                           (var.name, var.package, var.module, 
                                            var.namespace))
                        continue
                    self.vWidget.addVariable(var.uuid, var.name, descriptor, 
                                             var.value)
                self.vWidget.showPromptByChildren()
            else:
                self.vWidget.showPrompt(False)

    def lockUpdate(self):
        """ lockUpdate() -> None
        Do not allow updateModule()
        
        """
        self.updateLocked = True
        
    def unlockUpdate(self):
        """ unlockUpdate() -> None
        Allow updateModule()
        
        """
        self.updateLocked = False

class QVerticalWidget(QPromptWidget):
    """
    QVerticalWidget is a widget holding other variable widgets
    vertically
    
    """
    def __init__(self, parent=None):
        """ QVerticalWidget(parent: QWidget) -> QVerticalWidget
        Initialize with a vertical layout
        
        """
        QPromptWidget.__init__(self, parent)
        self.setPromptText("Drag a constant from the Modules panel to create a variable")
        self.setLayout(QtGui.QVBoxLayout())
        self.layout().setMargin(0)
        self.layout().setSpacing(5)
        self.layout().setAlignment(QtCore.Qt.AlignTop)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding,
                           QtGui.QSizePolicy.Expanding)
        self.setMinimumHeight(20)
        self._variable_widgets = []
        
    def addVariable(self, uuid, name, descriptor, value=''):
        """ addVariable(uuid:str, name: str, descriptor: ModuleDescriptor, value: str) -> None
        Add an input form for the variable
        
        """
        inputForm = QVariableInputWidget(uuid, name, descriptor, value, self)
        self.connect(inputForm, QtCore.SIGNAL('deleted(QWidget*)'), 
                     self.delete_form)
        self.layout().addWidget(inputForm)
        inputForm.show()
        self.setMinimumHeight(self.layout().minimumSize().height())
        self.showPrompt(False)
        self._variable_widgets.append(inputForm)

    def clear(self):
        """ clear() -> None
        Clear and delete all widgets in the layout
        
        """
        self.setEnabled(False)
        for v in self._variable_widgets:
            self.disconnect(v, QtCore.SIGNAL('deleted(QWidget*)'), 
                         self.delete_form)
            self.layout().removeWidget(v)
            v.setParent(None)
            v.deleteLater()
        self._variable_widgets = []
        self.setEnabled(True)

    def delete_form(self, input_form):
        self.disconnect(input_form, QtCore.SIGNAL('deleted(QWidget*)'), 
                     self.delete_form)
        var_name = input_form.var_name
        variableBox = self.parent().parent()
        self.layout().removeWidget(input_form)
        self._variable_widgets.remove(input_form)
        input_form.setParent(None)
        input_form.deleteLater()
        self.showPromptByChildren()

        if variableBox.controller:
            variableBox.lockUpdate()
            variableBox.controller.set_vistrail_variable(var_name, None)
            variableBox.unlockUpdate()
        self.setMinimumHeight(self.layout().minimumSize().height())


class QVariableInputWidget(QtGui.QDockWidget):
    def __init__(self, uuid, name, descriptor, value='', parent=None):
        QtGui.QDockWidget.__init__(self, parent)
        self.var_uuid = uuid
        self.var_name = name
        self.descriptor = descriptor
        self.setFeatures(QtGui.QDockWidget.DockWidgetClosable)
        # Create group and titlebar widgets for input widget
        self.group_box = QVariableInputForm(descriptor, value, self)
        self.setWidget(self.group_box)
        title_widget = QtGui.QWidget()
        title_layout = QtGui.QHBoxLayout()
        self.closeButton = QtGui.QToolButton()
        self.closeButton.setAutoRaise(True)
        self.closeButton.setIcon(QtGui.QIcon(self.style().standardPixmap(QtGui.QStyle.SP_TitleBarCloseButton)))
        self.closeButton.setIconSize(QtCore.QSize(13, 13))
        self.closeButton.setFixedWidth(16)
        self.label = QHoverVariableLabel(name)
        title_layout.addWidget(self.label)
        title_layout.addWidget(self.closeButton)
        title_widget.setLayout(title_layout)
        self.setTitleBarWidget(title_widget)
        self.connect(self.closeButton, QtCore.SIGNAL('clicked()'), self.close)
        
    def renameVariable(self, var_name):
        # First delete old var entry
        variableBox = self.parent().parent().parent()
        if variableBox.controller:
            variableBox.lockUpdate()
            variableBox.controller.set_vistrail_variable(self.var_name, None, False)
            variableBox.unlockUpdate()
        # Create var entry with new name, but keeping the same uuid
        self.var_name = var_name
        self.label.setText(var_name)
        self.group_box.updateMethod()
        
    def closeEvent(self, event):
        choice = show_question('Delete %s?'%self.var_name,
           'Are you sure you want to permanently delete the VisTrail variable\
 "%s"?\n\nNote:  Any workflows using this variable will be left in an invalid state.'%self.var_name,
                               [NO_BUTTON,YES_BUTTON],
                               NO_BUTTON)
        if choice == NO_BUTTON:
            event.ignore()
            return
        self.emit(QtCore.SIGNAL('deleted(QWidget*)'), self)

    def keyPressEvent(self, e):
        if e.key() in [QtCore.Qt.Key_Delete, QtCore.Qt.Key_Backspace]:
            self.close()
        else:
            QtGui.QDockWidget.keyPressEvent(self, e)
    
    def check_variable(self, name):
        """ check_variable(name: str) -> Boolean
        Returns True if the vistrail already has the variable name

        """
        variableBox = self.parent().parent().parent()
        if variableBox.controller:
            return variableBox.controller.check_vistrail_variable(name)
        return False

class QVariableInputForm(QtGui.QGroupBox):
    """
    QVariableInputForm is a widget with multiple input lines depends on
    the method signature
    
    """
    def __init__(self, descriptor, var_strValue="", parent=None):
        """ QVariableInputForm(descriptor: ModuleDescriptor, var_strValue: str,
                               parent: QWidget) -> QVariableInputForm
        Initialize with a vertical layout
        
        """
        QtGui.QGroupBox.__init__(self, parent)
        self.setLayout(QtGui.QGridLayout())
        self.layout().setMargin(5)
        self.layout().setSpacing(5)
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.setSizePolicy(QtGui.QSizePolicy.Preferred,
                           QtGui.QSizePolicy.Fixed)
        self.palette().setColor(QtGui.QPalette.Window,
                                CurrentTheme.METHOD_SELECT_COLOR)
        # Create widget for editing variable
        p = ModuleParam(type=descriptor.name, identifier=descriptor.identifier,
                        namespace=descriptor.namespace)
        p.strValue = var_strValue
        widget_type = get_widget_class(descriptor)
        self.widget = widget_type(p, self)
        self.label = QDragVariableLabel(p.type)
        self.layout().addWidget(self.label, 0, 0)
        self.layout().addWidget(self.widget, 0, 1)
        self.updateMethod()

    def focusInEvent(self, event):
        """ gotFocus() -> None
        Make sure the form painted as selected
        
        """
        self.setAutoFillBackground(True)

    def focusOutEvent(self, event):
        """ lostFocus() -> None
        Make sure the form painted as non-selected and then
        perform a parameter changes
        
        """
        self.setAutoFillBackground(False)

    def updateMethod(self):
        """ updateMethod() -> None
        Update the variable values in vistrail controller
        
        """
        inputWidget = self.parent()
        variableBox = inputWidget.parent().parent().parent()
        if variableBox.controller:
            variableBox.lockUpdate()
            descriptor = inputWidget.descriptor
            var = VistrailVariable(inputWidget.var_name, inputWidget.var_uuid,
                                   descriptor.identifier, descriptor.name,
                                   descriptor.namespace, str(self.widget.contents()))
            variableBox.controller.set_vistrail_variable(inputWidget.var_name, var)
            variableBox.unlockUpdate()

class QDragVariableLabel(QtGui.QLabel):
    """
    QDragVariableLabel is a QLabel that can be dragged to connect
    to an input port
    """
    def __init__(self, var_type='', parent=None):
        """ QDragVariableLabel(var_type:str,
                                parent: QWidget) -> QDragVariableLabel
        Initialize the label with a variable type
        
        """
        QtGui.QLabel.__init__(self, parent)
        self.var_type = var_type
        self.setText(var_type)
        self.setAttribute(QtCore.Qt.WA_Hover)
        self.setCursor(CurrentTheme.OPEN_HAND_CURSOR)
        self.setToolTip('Drag to an input port')
        self.palette().setColor(QtGui.QPalette.WindowText,
                                CurrentTheme.HOVER_DEFAULT_COLOR)

    def event(self, event):
        """ event(event: QEvent) -> Event Result
        Override to handle hover enter and leave events for hot links
        
        """
        if event.type()==QtCore.QEvent.HoverEnter:
            self.palette().setColor(QtGui.QPalette.WindowText,
                                    CurrentTheme.HOVER_SELECT_COLOR)
        if event.type()==QtCore.QEvent.HoverLeave:
            self.palette().setColor(QtGui.QPalette.WindowText,
                                    CurrentTheme.HOVER_DEFAULT_COLOR)
        return QtGui.QLabel.event(self, event)

    def mousePressEvent(self, event):
        """ mousePressEvent(event: QMouseEvent) -> None        
        If mouse click on the label, show up a dialog to change/add
        the variable name
        
        """
        if event.button()==QtCore.Qt.LeftButton:
            inputWidget = self.parent().parent()
            var_name = inputWidget.var_name
            var_uuid = inputWidget.var_uuid
            # Create pixmap from variable name and type
            drag_str = var_name + ' : ' + self.var_type
            drag_label = QDragVariableLabel(drag_str)
            drag_label.adjustSize()
            painter = QtGui.QPainter()
            font = QtGui.QFont()
            size = drag_label.size()
            image = QtGui.QImage(size.width()+4, size.height()+4, QtGui.QImage.Format_ARGB32_Premultiplied)
            image.fill(0)
            painter.begin(image)
            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(self.palette().highlight())
            painter.drawRect(QtCore.QRectF(0, 0, image.width(), image.height()))
            painter.setFont(font)
            painter.setPen(QtCore.Qt.black)
            painter.drawText(QtCore.QRect(QtCore.QPoint(2,2), size), QtCore.Qt.AlignLeft | QtCore.Qt.TextSingleLine, drag_str)
            painter.end()
            pixmap = QtGui.QPixmap.fromImage(image)
            # Create drag action
            mimeData = QtCore.QMimeData()
            portspec = inputWidget.descriptor.get_port_spec('value', 'output')
            mimeData.variableData = (portspec, var_uuid, var_name)
            drag = QtGui.QDrag(self)
            drag.setMimeData(mimeData)
            drag.setHotSpot(pixmap.rect().bottomRight())
            drag.setPixmap(pixmap)
            drag.start(QtCore.Qt.MoveAction)

class QHoverVariableLabel(QtGui.QLabel):
    """
    QHoverVariableLabel is a QLabel that supports hover actions similar
    to a hot link
    """
    def __init__(self, var_name='', parent=None):
        """ QHoverVariableLabel(var_name:str,
                                parent: QWidget) -> QHoverVariableLabel
        Initialize the label with a variable name
        
        """
        QtGui.QLabel.__init__(self, parent)
        self.var_name = var_name
        self.setText(var_name)
        self.setAttribute(QtCore.Qt.WA_Hover)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setToolTip('Click to rename')
        self.palette().setColor(QtGui.QPalette.WindowText,
                                CurrentTheme.HOVER_DEFAULT_COLOR)

    def event(self, event):
        """ event(event: QEvent) -> Event Result
        Override to handle hover enter and leave events for hot links
        
        """
        if event.type()==QtCore.QEvent.HoverEnter:
            self.palette().setColor(QtGui.QPalette.WindowText,
                                    CurrentTheme.HOVER_SELECT_COLOR)
        if event.type()==QtCore.QEvent.HoverLeave:
            self.palette().setColor(QtGui.QPalette.WindowText,
                                    CurrentTheme.HOVER_DEFAULT_COLOR)
        return QtGui.QLabel.event(self, event)

    def mousePressEvent(self, event):
        """ mousePressEvent(event: QMouseEvent) -> None        
        If mouse click on the label, show up a dialog to change/add
        the variable name
        
        """
        if event.button()==QtCore.Qt.LeftButton:
            inputWidget = self.parent().parent()
            orig_var_name = inputWidget.var_name
            (text, ok) = QtGui.QInputDialog.getText(self,
                                                    'Set New Variable Name',
                                                    'Enter the new variable name',
                                                    QtGui.QLineEdit.Normal,
                                                    orig_var_name)
            var_name = str(text).strip()
            while ok and self.parent().parent().check_variable(var_name):
                msg =" This variable name is already being used.\
 Please enter a different variable name "
                (text, ok) = QtGui.QInputDialog.getText(self,
                                                        'Set New Variable Name',
                                                        msg,
                                                        QtGui.QLineEdit.Normal,
                                                        text)
                var_name = str(text).strip()
            if ok and var_name != orig_var_name:
                self.setText(var_name)
                inputWidget.renameVariable(var_name)


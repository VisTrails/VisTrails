###############################################################################
##
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
""" This file contains widgets that can be used for dropping
methods. It will construct an input form for that method

QMethodDropBox
QVerticalWidget
QMethodInputForm
QHoverAliasLabel
"""

from PyQt4 import QtCore, QtGui
from core import debug
from core.utils import expression
from core.vistrail.module_function import ModuleFunction
from core.modules import module_registry
from gui.modules import get_widget_class
from gui.modules.constant_configuration import StandardConstantWidget, \
    FileChooserToolButton
from gui.common_widgets import QPromptWidget
from gui.method_palette import QMethodTreeWidget
from gui.theme import CurrentTheme

################################################################################

class QMethodDropBox(QtGui.QScrollArea):
    """
    QMethodDropBox is just a widget such that method items from
    QMethodPalette can be dropped into its client rect. It then
    construct an input form based on the type of handling widget
    
    """
    def __init__(self, parent=None):
        """ QMethodPalette(parent: QWidget) -> QMethodPalette
        Initialize widget constraints
        
        """
        QtGui.QScrollArea.__init__(self, parent)
        self.setAcceptDrops(True)
        self.setWidgetResizable(True)
        self.vWidget = QVerticalWidget()
        self.setWidget(self.vWidget)
        self.updateLocked = False
        self.controller = None
        self.module = None

    def dragEnterEvent(self, event):
        """ dragEnterEvent(event: QDragEnterEvent) -> None
        Set to accept drops from the method palette
        
        """
        if type(event.source())==QMethodTreeWidget:
            data = event.mimeData()
            if hasattr(data, 'items'):
                event.accept()
        else:
            event.ignore()
        
    def dragMoveEvent(self, event):
        """ dragMoveEvent(event: QDragMoveEvent) -> None
        Set to accept drag move event from the method palette
        
        """
        if type(event.source())==QMethodTreeWidget:
            data = event.mimeData()
            if hasattr(data, 'items'):
                event.accept()

    def dropEvent(self, event):
        """ dropEvent(event: QDragMoveEvent) -> None
        Accept drop event to add a new method
        
        """
        if type(event.source())==QMethodTreeWidget:
            data = event.mimeData()
            if hasattr(data, 'items'):
                event.accept()
                for item in data.items:
                    if item.spec and self.controller:
                        self.lockUpdate()
                        function = self.controller.add_function(self.module, 
                                                                item.spec.name)
                        self.vWidget.addFunction(self.module, function.pos,
                                                 function)
                        self.scrollContentsBy(0, self.viewport().height())
                        self.unlockUpdate()

                self.emit(QtCore.SIGNAL("paramsAreaChanged"))

    def updateModule(self, module):
        """ updateModule(module: Module) -> None        
        Construct input forms with the list of functions of a module
        
        """
        self.module = module
        if self.updateLocked: return
        self.vWidget.clear()
        if module:
            fId = 0
            for f in module.functions:
                self.vWidget.addFunction(module, fId, f)
                fId += 1
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
    QVerticalWidget is a widget holding other function widgets
    vertically
    
    """
    def __init__(self, parent=None):
        """ QVerticalWidget(parent: QWidget) -> QVerticalWidget
        Initialize with a vertical layout
        
        """
        QPromptWidget.__init__(self, parent)
        self.setPromptText("Drag methods here to set parameters")
        self.setLayout(QtGui.QVBoxLayout())
        self.layout().setMargin(0)
        self.layout().setSpacing(5)
        self.layout().setAlignment(QtCore.Qt.AlignTop)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding,
                           QtGui.QSizePolicy.Expanding)
        self.formType = QMethodInputForm
        self.setMinimumHeight(50)
        self._functions = []
        
    def addFunction(self, module, fId, function):
        """ addFunction(module: Module, fId: int,
                        function: ModuleFunction) -> None
        Add an input form for the function
        
        """
        if not function.is_valid:
            debug.critical("FUNCTION NOT VALID!")
            return
        inputForm = QMethodInputWidget(self.formType, self)
        inputForm.moduleId = module.id
        inputForm.fId = fId

        port_spec = None
        if module.is_valid:
            # call module.get_port_spec(function.name) to get labels
            port_spec = module.get_port_spec(function.name, 'input')
        inputForm.updateFunction(function, port_spec)
        self.connect(inputForm, QtCore.SIGNAL('deleted(QWidget*)'), 
                     self.delete_form)
        self.layout().addWidget(inputForm)
        inputForm.show()
        self.setMinimumHeight(self.layout().minimumSize().height())
        self.showPrompt(False)
        self._functions.append(inputForm)

    def clear(self):
        """ clear() -> None
        Clear and delete all widgets in the layout
        
        """
        self.setEnabled(False)
        for v in self._functions:
            self.layout().removeWidget(v)
            v.deleteLater()
        self._functions = []
        self.setEnabled(True)

    def delete_form(self, input_form):
        methodBox = self.parent().parent()
        self.layout().removeWidget(input_form)
        self._functions.remove(input_form)
        input_form.deleteLater()
        self.showPromptByChildren()
        for i in xrange(self.layout().count()):
            self.layout().itemAt(i).widget().fId = i

        methodBox.lockUpdate()
        if methodBox.controller:
            methodBox.controller.delete_method(input_form.fId,
                                               methodBox.module.id)
        methodBox.unlockUpdate()
        methodBox.emit(QtCore.SIGNAL("paramsAreaChanged"))


class QMethodInputWidget(QtGui.QDockWidget):
    def __init__(self, formType, parent=None):
        QtGui.QDockWidget.__init__(self, parent)
        self.setFeatures(QtGui.QDockWidget.DockWidgetClosable)
        self.group_box = formType(self)
        self.setWidget(self.group_box)

    def updateFunction(self, function, port_spec):
        self.setWindowTitle(function.name)
        self.group_box.updateFunction(function, port_spec)

    def closeEvent(self, event):
        self.emit(QtCore.SIGNAL('deleted(QWidget*)'), self)

    def keyPressEvent(self, e):
        if e.key() in [QtCore.Qt.Key_Delete, QtCore.Qt.Key_Backspace]:
            self.close()
        else:
            QtGui.QDockWidget.keyPressEvent(self, e)

class QMethodInputForm(QtGui.QGroupBox):
    """
    QMethodInputForm is a widget with multiple input lines depends on
    the method signature
    
    """
    def __init__(self, parent=None):
        """ QMethodInputForm(parent: QWidget) -> QMethodInputForm
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
        self.fId = -1
        self.function = None

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
        Update the method values to vistrail
        
        """
        methodBox = self.parent().parent().parent().parent()
        if methodBox.controller:
            methodBox.lockUpdate()
            methodBox.controller.update_function(methodBox.module,
                                                 self.function.name,
                                                 [str(w.contents()) 
                                                  for w in self.widgets],
                                                 self.function.real_id,
                                                 [str(label.alias)
                                                  for label in self.labels])
            
            methodBox.unlockUpdate()

    def check_alias(self, name):
        """ check_alias(name: str) -> Boolean
        Returns True if the current pipeline already has the alias name

        """
        methodBox = self.parent().parent().parent().parent()
        if methodBox.controller:
            return methodBox.controller.check_alias(name)
        return False

    def updateFunction(self, function, port_spec):
        """ updateFunction(function: ModuleFunction,
                           port_spec: PortSpec) -> None
        Auto create widgets to describes the function 'function'
        
        """
        reg = module_registry.get_module_registry()
        self.function = function
        self.widgets = []
        self.labels = []

        ps_labels = None
        if port_spec is not None:
            ps_labels = port_spec.labels
        for pIndex in xrange(len(function.params)):
            p = function.params[pIndex]
            # FIXME: Find the source of this problem instead
            # of working around it here.
            if p.identifier == '':
                idn = 'edu.utah.sci.vistrails.basic'
            else:
                idn = p.identifier

            p_module = None
            try:
                p_module = reg.get_module_by_name(idn,
                                                  p.type,
                                                  p.namespace)
            except module_registry.ModuleRegistryException:
                debug.critical("HIT ModuleRegistryException in DROPBOX")
                pass
            widget_type = get_widget_class(p_module)
            ps_label = ''
            if ps_labels is not None and len(ps_labels) > pIndex:
                ps_label = str(ps_labels[pIndex])
            label = QHoverAliasLabel(p.alias, p.type, ps_label)

            constant_widget = widget_type(p, self)
            self.widgets.append(constant_widget)
            self.labels.append(label)
            self.layout().addWidget(label, pIndex, 0)
            self.layout().addWidget(constant_widget, pIndex, 1)
            # Ugly hack to add browse button to methods that look like
            # they have to do with files
            if('file' in function.name.lower() and p.type == 'String'):
                browseButton = FileChooserToolButton(self, constant_widget)
                self.layout().addWidget(browseButton, pIndex, 2)

class QHoverAliasLabel(QtGui.QLabel):
    """
    QHoverAliasLabel is a QLabel that supports hover actions similar
    to a hot link
    """
    def __init__(self, alias='', text='', default_label='', parent=None):
        """ QHoverAliasLabel(alias:str , text: str, default_label: str,
                             parent: QWidget) -> QHoverAliasLabel
        Initialize the label with a text
        
        """
        QtGui.QLabel.__init__(self, parent)
        self.alias = alias
        self.caption = text
        self.default_label = default_label
        self.updateText()
        self.setAttribute(QtCore.Qt.WA_Hover)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setToolTip(alias)
        self.palette().setColor(QtGui.QPalette.WindowText,
                                CurrentTheme.HOVER_DEFAULT_COLOR)

    def updateText(self):
        """ updateText() -> None
        Update the label text to contain the alias name when appropriate
        
        """
        if self.alias != '':
            self.setText(self.alias + ': ' + self.caption)
        elif self.default_label != '':
            self.setText(self.default_label + ': ' + self.caption)
        else:
            self.setText(self.caption)

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
        # return super(QHoverAliasLabel, self).event(event)

    def mousePressEvent(self, event):
        """ mousePressEvent(event: QMouseEvent) -> None        
        If mouse click on the label, show up a dialog to change/add
        the alias name
        
        """
        if event.button()==QtCore.Qt.LeftButton:
            (text, ok) = QtGui.QInputDialog.getText(self,
                                                    'Set Parameter Alias',
                                                    'Enter the parameter alias',
                                                    QtGui.QLineEdit.Normal,
                                                    self.alias)
            while ok and self.parent().check_alias(str(text)):
                msg =" This alias is already being used.\
 Please enter a different parameter alias "
                (text, ok) = QtGui.QInputDialog.getText(self,
                                                        'Set Parameter Alias',
                                                        msg,
                                                        QtGui.QLineEdit.Normal,
                                                        text)
            if ok and str(text)!=self.alias:
                if not self.parent().check_alias(str(text)):
                    self.alias = str(text).strip()
                    self.updateText()
                    self.parent().updateMethod()


############################################################################
##
## Copyright (C) 2006-2010 University of Utah. All rights reserved.
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
from PyQt4 import QtCore, QtGui
from gui.theme import CurrentTheme
from core.modules.constant_configuration import ConstantWidgetMixin
from core.modules.constant_configuration import StandardConstantWidget
from core.modules.module_registry import get_module_registry

class QAliasSliderWidget(QtGui.QWidget):
    def __init__(self, alias, vtparam, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.alias = alias
        self.vtparam = vtparam
        self.palette().setColor(QtGui.QPalette.Window,
                                CurrentTheme.METHOD_SELECT_COLOR)
        label = QtGui.QLabel(alias.name)
        label.font().setBold(True)
        self.value = QSliderIntegerWidget(param=vtparam,
                                          parent=self)
        self.value.setRange(int(alias.component.minVal), 
                            int(alias.component.maxVal))
        self.value.setSingleStep(int(alias.component.stepSize))

        self.connect(self.value,
                     QtCore.SIGNAL("contentsChanged"),
                     self.contents_changed)
        
        hbox = QtGui.QHBoxLayout()
        hbox.setMargin(8)
        hbox.addWidget(label)
        hbox.addWidget(self.value)
        self.setLayout(hbox)    
   
    def contents_changed(self, info):
        #print "drop down emitting"
        self.emit(QtCore.SIGNAL('contentsChanged'), (self, info))
             
    def focusInEvent(self, event):
        self.emit(QtCore.SIGNAL("receivedfocus"), self)
        
    def focusOutEvent(self, event):
        self.emit(QtCore.SIGNAL("removedfocus"), self)
        
###############################################################################        

class QSliderIntegerWidget(ConstantWidgetMixin, QtGui.QSlider):
    def __init__(self, param, parent=None):
        QtGui.QSlider.__init__(self, QtCore.Qt.Horizontal, parent)
        ConstantWidgetMixin.__init__(self, param.strValue)
        assert param.type == 'Integer'
        assert param.identifier == 'edu.utah.sci.vistrails.basic'
        
        self.connect(self, QtCore.SIGNAL('valueChanged(int)'),
                     self.change_val)
        self.setContents(param.strValue)
        self.setTickPosition(QtGui.QSlider.TicksAbove)
        
    def contents(self):
        return self.value()

    def setContents(self, strValue, silent=True):
        if strValue:
            value = strValue
        else:
            value = "0"
        self.setValue(int(value))
        self.setToolTip(value)
        
        if not silent:
            self.update_parent()
            
    def change_val(self, newval):
        self.setToolTip(str(newval))
        self.update_parent()
        
###############################################################################

class QAliasNumericStepperWidget(QtGui.QWidget):
    def __init__(self, alias, vtparam, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.alias = alias
        self.vtparam = vtparam
        self.palette().setColor(QtGui.QPalette.Window,
                                CurrentTheme.METHOD_SELECT_COLOR)
        label = QtGui.QLabel(alias.name)
        label.font().setBold(True)
        if self.alias.component.type == "Integer":
            self.value = QNumericStepperIntegerWidget(param=vtparam,
                                                      parent=self)
            self.value.setRange(int(alias.component.minVal), 
                                int(alias.component.maxVal))
            self.value.setSingleStep(int(alias.component.stepSize))
        elif self.alias.component.type == "Float":
            self.value = QNumericStepperFloatWidget(param=vtparam,
                                                    parent=self)
            self.value.setRange(float(alias.component.minVal), 
                                float(alias.component.maxVal))
            self.value.setSingleStep(float(alias.component.stepSize))

        self.connect(self.value,
                     QtCore.SIGNAL("contentsChanged"),
                     self.contents_changed)
        
        hbox = QtGui.QHBoxLayout()
        hbox.setMargin(8)
        hbox.addWidget(label)
        hbox.addWidget(self.value)
        self.setLayout(hbox)    
   
    def contents_changed(self, info):
        #print "drop down emitting"
        self.emit(QtCore.SIGNAL('contentsChanged'), (self, info))
             
    def focusInEvent(self, event):
        self.emit(QtCore.SIGNAL("receivedfocus"), self)
        
    def focusOutEvent(self, event):
        self.emit(QtCore.SIGNAL("removedfocus"), self)
        
###############################################################################
class QNumericStepperIntegerWidget(ConstantWidgetMixin, QtGui.QSpinBox):
    def __init__(self, param, parent=None):
        QtGui.QSpinBox.__init__(self, parent)
        ConstantWidgetMixin.__init__(self, param.strValue)
        assert param.type == 'Integer'
        assert param.identifier == 'edu.utah.sci.vistrails.basic'
        
        self.connect(self, QtCore.SIGNAL('valueChanged(int)'),
                     self.change_val)
        self.setContents(param.strValue)
        
    def contents(self):
        return self.value()

    def setContents(self, strValue, silent=True):
        if strValue:
            value = strValue
        else:
            value = "0"
        self.setValue(int(value))
        
        if not silent:
            self.update_parent()
            
    def change_val(self, newval):
        self.update_parent()
###############################################################################

class QNumericStepperFloatWidget(ConstantWidgetMixin, QtGui.QDoubleSpinBox):
    def __init__(self, param, parent=None):
        QtGui.QDoubleSpinBox.__init__(self, parent)
        ConstantWidgetMixin.__init__(self, param.strValue)
        assert param.type == 'Float'
        assert param.identifier == 'edu.utah.sci.vistrails.basic'
        
        self.connect(self, QtCore.SIGNAL('valueChanged(double)'),
                     self.change_val)
        self.setContents(param.strValue)
        
    def contents(self):
        return self.value()

    def setContents(self, strValue, silent=True):
        if strValue:
            value = strValue
        else:
            value = "0"
        self.setValue(float(value))
        
        if not silent:
            self.update_parent()
            
    def change_val(self, newval):
        self.update_parent()

###############################################################################

class QDropDownWidget(QtGui.QWidget):
    def __init__(self, alias, vtparam, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.alias = alias
        self.vtparam = vtparam
        self.palette().setColor(QtGui.QPalette.Window,
                                CurrentTheme.METHOD_SELECT_COLOR)
        label = QtGui.QLabel(alias.name)
        label.font().setBold(True)
        self.value = self.createAliasWidget(val=self.alias.component.val,
                                            parent=self)
        self.connect(self.value,
                     QtCore.SIGNAL("contentsChanged"),
                     self.contents_changed)
        self.dropdownbtn = QtGui.QToolButton(self)
        self.dropdownbtn.setArrowType(QtCore.Qt.DownArrow)
        self.dropdownbtn.setAutoRaise(True)
            
        #menu button
        self.createMenu()
        self.dropdownbtn.setPopupMode(QtGui.QToolButton.InstantPopup)
            
        hbox = QtGui.QHBoxLayout()
        hbox.setMargin(8)
        hbox.addWidget(label)
        hbox.addWidget(self.value)
        hbox.addWidget(self.dropdownbtn)
        self.setLayout(hbox)    
        
    def createMenu(self):
        self.menu = QtGui.QMenu(self)
        self.menu.setSizePolicy(QtGui.QSizePolicy.Preferred,
                                QtGui.QSizePolicy.Maximum)
        mbox = QtGui.QVBoxLayout()
        mbox.setSpacing(1)
        mbox.setMargin(2)
        self.menu_widgets = {}   
        valuelist = self.alias.component.valueList
       
        for v in valuelist:
            hbox = QtGui.QHBoxLayout()
            rb = QMenuRadioButton()
            rb.setChecked(False)
            vw = self.createAliasWidget(val=v, parent=self)
            vw.setFocusProxy(rb)
            vw.setSizePolicy(QtGui.QSizePolicy.Preferred,
                                QtGui.QSizePolicy.Maximum)
            
            self.menu_widgets[rb] = vw
            hbox.addWidget(rb)
            hbox.addWidget(vw)
            mbox.addLayout(hbox)
           
            self.connect(rb,
                         QtCore.SIGNAL("clicked(bool)"),
                         self.menu.hide)
        self.menu.setLayout(mbox)
        self.dropdownbtn.setMenu(self.menu)
        
        #there's a bug on a mac that causes the menu to be always displayed
        #where it was shown for the first time... We need to ensure
        #the right position.
        self.connect(self.menu,
                     QtCore.SIGNAL("aboutToShow()"),
                     self.ensure_menu_position)
        self.connect(self.menu,
                     QtCore.SIGNAL("aboutToHide()"),
                     self.value_selected)
        
    def contents_changed(self, info):
        #print "drop down emitting"
        self.emit(QtCore.SIGNAL('contentsChanged'), (self, info))
        
    def ensure_menu_position(self):
        #print self.dropdownbtn.pos(), 
        newpos = QtCore.QPoint(self.dropdownbtn.pos().x(),
                               self.dropdownbtn.pos().y() + self.dropdownbtn.frameSize().height())
        self.menu.move(self.mapToGlobal(newpos))  
        #print self.menu.pos()
        
    def createAliasWidget(self, val=None, parent=None):
        if self.vtparam.identifier == '':
            idn = 'edu.utah.sci.vistrails.basic'
        else:
            idn = self.vtparam.identifier
        reg = get_module_registry()
        p_module = reg.get_module_by_name(idn, self.vtparam.type, 
                                          self.vtparam.namespace)
        if p_module is not None:
            widget_type = p_module.get_widget_class()
        else:
            widget_type = StandardConstantWidget
        if val:
            self.vtparam.strValue = val
        return widget_type(self.vtparam, parent)
            
    def value_selected(self):
        #print "value_selected", self.menu.pos()
        for rb, vw in self.menu_widgets.iteritems():
            if rb.isChecked():
                self.value.setContents(vw.contents(), silent=False)
                vw.setFocus()
                rb.setChecked(False)
                self.menu.hide()
                break
                
    def focusInEvent(self, event):
        self.emit(QtCore.SIGNAL("receivedfocus"), self)
        
    def focusOutEvent(self, event):
        self.emit(QtCore.SIGNAL("removedfocus"), self)
        
class QMenuRadioButton(QtGui.QRadioButton):
    def focusInEvent(self, event):
        self.setChecked(True)
        #self.emit(QtCore.SIGNAL("clicked(bool)"), True)
        QtGui.QRadioButton.focusInEvent(self, event)
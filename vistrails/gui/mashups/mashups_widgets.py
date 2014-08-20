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
from PyQt4 import QtCore, QtGui
from vistrails.core.system import get_vistrails_basic_pkg_id
from vistrails.gui.theme import CurrentTheme
from vistrails.gui.modules.utils import get_widget_class
from vistrails.gui.modules.constant_configuration import ConstantWidgetMixin, \
    StandardConstantWidget
from vistrails.core.modules.module_registry import get_module_registry

class QAliasSliderWidget(QtGui.QWidget):
    def __init__(self, alias, vtparam, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.alias = alias
        self.vtparam = vtparam
        self.palette().setColor(QtGui.QPalette.Window,
                                CurrentTheme.METHOD_SELECT_COLOR)
        label = QtGui.QLabel(alias.name)
        label.font().setBold(True)
        self.value = QSliderWidget(param=vtparam, parent=self)
        self.value.setRange(alias.component.minVal, alias.component.maxVal)
        self.value.setSingleStep(alias.component.stepSize)
        self.value.setContents(self.alias.component.val)
        
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

class QSliderWidget(ConstantWidgetMixin, QtGui.QSlider):
    def __init__(self, param, parent=None):
        QtGui.QSlider.__init__(self, QtCore.Qt.Horizontal, parent)
        ConstantWidgetMixin.__init__(self, param.strValue)
        assert param.type in['Integer', 'Float']
        self.sliderType = int if param.type == 'Integer' else float
        assert param.identifier == get_vistrails_basic_pkg_id()
        
        self.connect(self, QtCore.SIGNAL('valueChanged(int)'),self.change_val)
        QtGui.QSlider.setSingleStep(self, 1)
        QtGui.QSlider.setPageStep(self, 5)
        self.floatMinVal = 0.0
        self.floatMaxVal = 1.0
        self.floatStepSize = 1
        self.numSteps = 1
        self.setContents(param.strValue)
        self.setTickPosition(QtGui.QSlider.TicksAbove)        
    
    def contents(self):
        floatVal = float(self.value()) * self.floatStepSize + self.floatMinVal
        return self.sliderType(floatVal)

    def setContents(self, strValue, silent=True):
        """ encodes a number to a scaled integer """
        if strValue:
            value = strValue
        else:
            value = "0.0"
        floatVal = float(value)
        value = int((floatVal-self.floatMinVal)/self.floatStepSize)
        self.setValue(int(value))
        self.setToolTip("%g" % floatVal)
        
        if not silent:
            self.update_parent()
            
    def change_val(self, newval):
        """ decodes a scaled integer to the correct number """
        floatVal = float(newval) * self.floatStepSize + self.floatMinVal
        self.setToolTip("%g" % floatVal)
        self.update_parent()

    def setRange(self, minVal, maxVal):
        self.floatMinVal = float(minVal)
        self.floatMaxVal = float(maxVal)
        QtGui.QSlider.setRange(self, 0, 1)
        self.setSingleStep(self.floatStepSize)
        
    def setSingleStep(self, stepSize):
        """ stepSize tells the step between values. We need to calculate the
            number of steps """
        self.floatStepSize = float(stepSize)
        self.numSteps = int((self.floatMaxVal - self.floatMinVal)/self.floatStepSize)
        QtGui.QSlider.setRange(self, 0, self.numSteps)

        
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
            self.value.setContents(self.alias.component.val)            
        elif self.alias.component.type == "Float":
            self.value = QNumericStepperFloatWidget(param=vtparam,
                                                    parent=self)
            self.value.setRange(float(alias.component.minVal), 
                                float(alias.component.maxVal))
            self.value.setSingleStep(float(alias.component.stepSize))
            self.value.setContents(self.alias.component.val)

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
        assert param.identifier == get_vistrails_basic_pkg_id()
        
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
        assert param.identifier == get_vistrails_basic_pkg_id()
        
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
        self.menu = QMenuValue(self)
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
            vw = self.createMenuAliasWidget(val=v, parent=self)
            vw.setSizePolicy(QtGui.QSizePolicy.Preferred,
                                QtGui.QSizePolicy.Maximum)
            vw.setReadOnly(True)
            
            self.menu_widgets[rb] = vw
            hbox.addWidget(rb)
            hbox.addWidget(vw)
            mbox.addLayout(hbox)
           
            self.connect(rb,
                         QtCore.SIGNAL("clicked(bool)"),
                         self.menu.hide)
            self.connect(vw,
                         QtCore.SIGNAL("clicked(bool)"),
                         rb.setChecked)
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
            idn = get_vistrails_basic_pkg_id()
        else:
            idn = self.vtparam.identifier
        reg = get_module_registry()
        p_descriptor = reg.get_descriptor_by_name(idn, self.vtparam.type,
                                                  self.vtparam.namespace)
        widget_type = get_widget_class(p_descriptor)
        if val:
            self.vtparam.strValue = val
        return widget_type(self.vtparam, parent)
    
    def createMenuAliasWidget(self, val=None, parent=None):
        widget = self.createAliasWidget(val)
        return QMenuValueItem(widget, parent)
    
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
        
class QMenuValue(QtGui.QMenu):    
    def mousePressEvent(self, e):
        vw = self.childAt(e.pos())
        while vw is not None and not isinstance(vw, QMenuValueItem):
            vw = vw.parent()
        if vw is not None:
            vw.emit(QtCore.SIGNAL("clicked(bool)"), True)
        QtGui.QMenu.mousePressEvent(self, e)
        
class QMenuValueItem(QtGui.QWidget):
    def __init__(self, widget, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.widget = widget
        vlayout = QtGui.QVBoxLayout()
        vlayout.setMargin(0)
        vlayout.setSpacing(0)
        vlayout.addWidget(self.widget)
        self.setLayout(vlayout)
        
    def setReadOnly(self, on):
        self.setEnabled(not on)
        
    def contents(self):
        return self.widget.contents()
    
    def mousePressEvent(self, e):
        self.emit(QtCore.SIGNAL("clicked(bool)"), True)

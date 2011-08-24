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

##############################################################################
# Enumeration Widget for Web Services

from PyQt4 import QtCore, QtGui
import core.modules
from core.modules.constant_configuration import ConstantWidgetMixin
from core.modules.basic_modules import Constant, Module
from core.modules.constant_configuration import StandardConstantWidget
import core.modules.module_registry
from core.modules.vistrails_module import new_module
import packages.webServices

class EnumerationWidget(QtGui.QComboBox, ConstantWidgetMixin):
    enumerationlist = []
    def __init__(self, param, parent=None):
        """__init__(param: core.vistrail.module_param.ModuleParam,
                    parent: QWidget)
        Initializes the line edit with contents
        """
        dictkey = param._namespace
        typedict = packages.webServices.webServicesmodulesDict[dictkey]
        w = param._namespace.replace('|Types','')
        dictkey = w + "." + param._type
        obj = typedict[dictkey]
        self.enumerationlist = obj.ports[0][0]
        QtGui.QComboBox.__init__(self, parent)
        ConstantWidgetMixin.__init__(self, param.strValue)
        QtGui.QComboBox.clear(self)
        listqt = QtCore.QStringList()
        for element in self.enumerationlist:
            listqt.append(element)
            
        QtGui.QComboBox.addItems(self, listqt)
        foundindex = self.findText(param.strValue)
        if not foundindex == -1:
            self.setCurrentIndex(foundindex)
        else:
            self.setCurrentIndex(0)
            param.strValue = self.enumerationlist[self.currentIndex()]
        self.connect(self, QtCore.SIGNAL('activated(int)'), self.change_state)

    def contents(self):
        return self.enumerationlist[self.currentIndex()]
    
    def change_state(self, state):
        self.update_parent()
    
def initialize(namemodule,namespace,identifier, version):
    enumerationConstant = new_constant(namemodule,
                                            namespace,
                                            identifier,
                                            version,
                                            EnumerationWidget)
    return enumerationConstant

def new_constant(name, namespace, identifier, 
                 version, widget_type=StandardConstantWidget):
    """new_constant(name: str, namespace: str,widget_type: QWidget type) -> Module
    
    new_constant dynamically creates a new Module derived from Constant
    with a widget type."""
    reg = core.modules.module_registry.get_module_registry()
    
    def __init__(self):
        Constant.__init__(self)

    @staticmethod
    def get_widget_class():
        return widget_type

    @staticmethod
    def conversion(self): return self
    
    m = new_module(Constant, name, {'__init__': __init__,
                                    'get_widget_class': get_widget_class,
                                    'translate_to_python': conversion})
    m.name = name
    m.isEnumeration = True
    reg.add_module(m,namespace=namespace,package=identifier,
                   package_version=version)
    return m

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

##############################################################################
# Enumeration Widget for Web Services

from PyQt4 import QtCore, QtGui
import core.modules
from core.modules.constant_configuration import ConstantWidgetMixin
from core.modules.basic_modules import Constant, Module
from core.modules.constant_configuration import StandardConstantWidget
from core.modules.module_registry import registry
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
        ConstantWidgetMixin.__init__(self)
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
    
def initialize(namemodule,namespace,identifier):
    enumerationConstant = new_constant(namemodule,
                                            namespace,
                                            identifier,
                                            EnumerationWidget)
    return enumerationConstant

def new_constant(name, namespace, identifier, widget_type=StandardConstantWidget):
    """new_constant(name: str, namespace: str,widget_type: QWidget type) -> Module
    
    new_constant dynamically creates a new Module derived from Constant
    with a widget type."""
    reg = core.modules.module_registry
    
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
    reg.add_module(m,namespace=namespace)
    return m

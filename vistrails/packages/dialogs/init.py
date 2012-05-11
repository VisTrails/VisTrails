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

from core.modules.vistrails_module import Module, ModuleError
import core.modules
import core.modules.basic_modules
import core.modules.module_registry
import core.system
import gui.application
from PyQt4 import QtCore, QtGui

##############################################################################

class Dialog(Module):
    pass

class TextDialog(Dialog):
    password = False

    def __init__(self, *args, **kwargs):
        super(TextDialog,self).__init__(*args, **kwargs)
        self.cacheable_dialog = False

    def is_cacheable(self):
        return self.cacheable_dialog

    def compute(self):
        if self.hasInputFromPort('title'):
            title = self.getInputFromPort('title')
        else:
            title = 'VisTrails Dialog'
        if self.hasInputFromPort('label'):
            label = self.getInputFromPort('label')
        else:
            label = ''
            if self.password:
                label = 'Password'

        if self.hasInputFromPort('default'):
            default = QtCore.QString(self.getInputFromPort('default'))
        else:
            default = QtCore.QString('')
            
        if self.hasInputFromPort('cacheable') and self.getInputFromPort('cacheable'):
            self.cacheable_dialog = True
        else:
            self.cacheable_dialog = False

        mode =  QtGui.QLineEdit.Normal
        if self.password:
            mode = QtGui.QLineEdit.Password

        (result, ok) = QtGui.QInputDialog.getText(None, title, label,
                                                  mode,
                                                  default)
        if not ok:
            raise ModuleError(self, "Canceled")
        self.setResult('result', str(result))


class PasswordDialog(TextDialog):
    password = True


##############################################################################

def initialize(*args, **keywords):
    reg = core.modules.module_registry.get_module_registry()
    basic = core.modules.basic_modules
    reg.add_module(Dialog)
    reg.add_module(TextDialog)

    reg.add_input_port(TextDialog, "title", basic.String)
    reg.add_input_port(TextDialog, "label", basic.String)
    reg.add_input_port(TextDialog, "default", basic.String)
    reg.add_input_port(TextDialog, "cacheable", basic.Boolean)
    reg.add_output_port(TextDialog, "result", basic.String)
    
    reg.add_module(PasswordDialog)

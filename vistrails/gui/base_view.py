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

from PyQt4 import QtCore, QtGui

class BaseView(object):
    """ BaseView is the base class for the views in VisTrails.


    """

    def __init__(self):
        self.controller = None
        self.title = None
        self.index = -1
        self.tab_idx = -1

        self.palette_layout = {}
        self.set_default_layout()
        self.action_links = {}
        self.action_defaults = {}
        BaseView.set_action_defaults(self)
        self.set_action_defaults()
        self.set_action_links()
        self.detachable = False
        self.vistrail_view = None

    def set_default_layout(self):
        raise Exception("Class must define the layout as self.palette_layout")

    def set_palette_layout(self, layout):
        self.palette_layout = layout

    def set_action_links(self):
        raise Exception("Class must define the action links")

    def set_action_defaults(self):
        self.action_defaults.update(
            {'history'    : [('setEnabled', False, True)],
             'search'     : [('setEnabled', False, True)],
             'explore'    : [('setEnabled', False, True)],
             'provenance' : [('setEnabled', False, True)],
             'mashup'     : [('setEnabled', False, True)]
             })

    def set_title(self, title):
        self.title = title

    def get_title(self):
        return self.title

    def set_long_title(self, title):
        self.long_title = title
        
    def get_long_title(self):
        return self.title
    
    def get_index(self):
        return self.index

    def set_index(self, index):
        self.index = index

    def get_tab_idx(self):
        return self.tab_idx

    def set_tab_idx(self, tab_idx):
        self.tab_idx = tab_idx

    def set_controller(self, controller):
        pass
    
    def set_vistrail_view(self, view):
        self.vistrail_view = view
        
    def get_vistrail_view(self):
        return self.vistrail_view
    
    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.WindowTitleChange:
            self.emit(QtCore.SIGNAL("windowTitleChanged"), self)
        QtGui.QWidget.changeEvent(self, event)

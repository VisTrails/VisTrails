###############################################################################
##
## Copyright (C) 2006-2011, University of Utah. 
## All rights reserved.
## Contact: vistrails@sci.utah.edu
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

from core.db.io import load_vistrail
from core.modules.module_registry import ModuleRegistryException
from vistrail_view import JVistrailView

from javax.swing import JComponent


class JViewManager(JComponent):
    
    def __init__(self):
        pass
    
    def add_vistrail_view(self, view):
        viewComponent = view.controller
        self.add(viewComponent)
    
    def open_vistrail(self, locator, version = None, is_abstraction=False):
        try:
            (vistrail, abstraction_files, thumbnail_files) = \
                                        load_vistrail(locator, is_abstraction)                                                
            result = self.set_vistrail_view(vistrail, locator, 
                                            abstraction_files, thumbnail_files,
                                            version)
            return result
        except ModuleRegistryException:
            raise
        except Exception:
            raise
    
    def set_vistrail_view(self, vistrail, locator, abstraction_files=None,
                          thumbnail_files=None, version=None):   
        vistrailView = JVistrailView(vistrail, locator)
        vistrailView.set_vistrail(vistrail, locator, abstraction_files,
                                  thumbnail_files)
        self.add_vistrail_view(vistrailView)
        return vistrailView

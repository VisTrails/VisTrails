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

import core.db.io
import core.modules.basic_modules
from core.vistrail.controller import VistrailController as BaseController
from javax.swing import JComponent
from core.utils import DummyView

class JVistrailController(BaseController, JComponent):

    def __init__(self):
        super(JVistrailController, self).__init__()
        self.fileName  = ""

    def set_vistrail(self, vistrail, locator, abstractions=None, thumbnails=None):
        """ set_vistrail(vistrail: Vistrail, locator: VistrailLocator) -> None
        Start controlling a vistrail
        """
        # self.vistrail = vistrail
        super(JVistrailController, self).set_vistrail(vistrail, locator, abstractions,
                                    thumbnails)
        if locator != None:
            self.fileName = locator.name
        else:
            self.fileName = ''
        if locator and locator.has_temporaries():
            self.set_changed(True)

        self.set_graph()

        print "JVistrailController#set_vistrail():"
        print "  current_version = %d" % self.current_version
        print "  current_session = %d" % self.current_session

    def set_graph(self):
        if (self.current_version == -1 or
                self.current_version > self.vistrail.get_latest_version()):
            self.current_version = self.vistrail.get_latest_version()

        self.current_pipeline = core.db.io.get_workflow(
                self.vistrail, self.current_version)

        for module in self.current_pipeline._get_modules():
            # FIXME : Replaces information panels by providing test values
            # Should be done before each execution?
            if self.current_pipeline.modules[module]._get_module_descriptor().module() is core.modules.basic_modules.String:
                self.current_pipeline.modules[module]._get_module_descriptor().module().setValue("testString")

    def execute_current_workflow(self, custom_aliases=None, custom_params=None,
                                 reason='Pipeline Execution'):
        self.flush_delayed_actions()
        if self.current_pipeline:
            locator = self.get_locator()
            if locator:
                locator.clean_temporaries()
                if self._auto_save:
                    locator.save_temporary(self.vistrail)
            view = self.current_pipeline_view or DummyView()
            return self.execute_workflow_list([(self.locator,
                                                self.current_version,
                                                self.current_pipeline,
                                                view,
                                                custom_aliases,
                                                custom_params,
                                                reason,
                                                None)])

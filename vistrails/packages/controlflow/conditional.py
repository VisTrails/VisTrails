###############################################################################
##
## Copyright (C) 2011-2013, NYU-Poly.
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
from vistrails.core.modules.vistrails_module import Module, ModuleError
from vistrails.core.modules.basic_modules import NotCacheable

#################################################################################
## If Operator

class If(Module, NotCacheable):
    """
    Return one of two values depending on a boolean condition.

    Note that the modules upstream of the port that is not chosen won't get
    executed (short-circuit).
    """

    def update(self):
        self.logging.begin_update(self)
        self.updateUpstream(
                self.condition_ready,
                [self.getInputConnector('Condition')])

    def condition_ready(self, connectors):
        if self.suspended:
            self.done()
            return

        self.__condition = self.getInputFromPort('Condition')
        if self.__condition:
            port_name = 'TruePort'
        else:
            port_name = 'FalsePort'
        self.updateUpstream(
                self.input_ready,
                [self.getInputConnector(port_name)],
                priority=50)
        # This module does nothing, it just forwards the value we get from
        # upstream, so we might as well give it a higher priority

    def input_ready(self, connectors):
        self.done()
        self.logging.begin_compute(self)
        if self.__condition:
            self.setResult('Result', self.getInputFromPort('TruePort'))
        else:
            self.setResult('Result', self.getInputFromPort('FalsePort'))
        self.upToDate = True
        self.logging.end_update(self)
        self.logging.signalSuccess(self)

#################################################################################
## Default module

class Default(Module, NotCacheable):
    """
    The Default module allows the user to provide a default value.

    This module can be put in the middle of a connection to provide a default
    value from the Default port in case nothing is set on the Input port. This
    is particularly useful when using subworkflows, with InputPort modules with
    optional set to True.

    Note that if a value is set on the Input port, the modules upstream of the
    Default port won't be executed (short-circuit).
    """

    def updateUpstream(self, callback=None, priority=None):
        try:
            self.__connector = self.getInputConnector('Input')
        except ModuleError:
            self.__connector = self.getInputConnector('Default')

        super(Default, self).updateUpstream(
                callback,
                [self.__connector],
                priority)

    def compute(self):
        self.setResult('Result', self.__connector())

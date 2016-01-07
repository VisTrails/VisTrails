###############################################################################
##
## Copyright (C) 2014-2016, New York University.
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
##  - Neither the name of the New York University nor the names of its
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

from __future__ import division

from vistrails.core.modules.vistrails_module import Module
from vistrails.core.modules.module_registry import get_module_registry
from vistrails.core.modules.basic_modules import List, String

from engine_manager import EngineManager
from map import Map


def initialize(*args,**keywords):
    reg = get_module_registry()

    reg.add_module(Map)
    reg.add_input_port(Map, 'FunctionPort', (Module, ''))
    reg.add_input_port(Map, 'InputList', (List, ''))
    reg.add_input_port(Map, 'InputPort', (List, ''))
    reg.add_input_port(Map, 'OutputPort', (String, ''))
    reg.add_output_port(Map, 'Result', (List, ''))


def finalize():
    EngineManager.cleanup()


def menu_items():
    return (
            ("Start new engine processes",
             lambda: EngineManager.start_engines()),
            ("Show information on the cluster",
             lambda: EngineManager.info()),
            ("Change profile",
             lambda: EngineManager.change_profile()),
            ("Cleanup started processes",
             lambda: EngineManager.cleanup()),
            ("Request cluster shutdown",
             lambda: EngineManager.shutdown_cluster()),
    )

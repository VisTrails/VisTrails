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
""" 
This file is responsible for importing all VisTrails python modules so 
they can be used by an external application without having to import them.
This is necessary because VisTrails assumes that 'vistrails/' folder is 
always the root of the application. You won't be able to use it as a library 
without adding 'vistrails/' to PYTHONPATH. Furthermore, vistrails modules 
imported from outside vistrails are considered different from the same modules
imported from inside.

For example:
Suppose you have the following directory structure:
myapp/
  |- myapp.py
  |- file1.py
  |- vistrails/
         |- api
         |-core
         |-db
         .
         : (current vistrails directory structure)

And you added myapp/vistrails to the PYTHONPATH

In myapp.py file you have:
  import vistrails.core.configuration
  import vistrails.core.startup
  conf = vistrails.core.configuration.default()
  self.vistrailsStartup = vistrails.core.startup.VistrailsStartup(
             conf)
             
  when trying to run myapp.py you will see an error similar to this:
  
  Traceback (most recent call last):
  
  File "myapp.py", line 4, in <module>
    conf)
  File "vistrails/core/startup.py", line 59, in __init__
    isinstance(config, core.configuration.ConfigurationObject))
AssertionError

Because your conf is vistrails.core.configuration.ConfigurationObject as you
imported in myapp.py and it's not the same as core.configuration.ConfigurationObject
imported somewhere in vistrails.

The solution for now is import everything from here and make the external 
application import only this file once in the beginning 
and use the imported modules from there.
           

"""
import core.command_line
import core.configuration
import core.console_mode
import core.data_structures.bijectivedict
import core.data_structures.graph
import core.db.locator
import core.debug
import core.external_connection
import core.interpreter.default
import core.interpreter.cached
import core.keychain
import core.log
import core.log.controller
import core.log.log
import core.modules.module_utils
import core.modules.module_registry
import core.modules.constant_configuration
import core.repository
import core.repository.poster
import core.repository.poster.encode
import core.repository.poster.streaminghttp
import core.startup
import core.system
import core.utils
import core.utils.color
import core.utils.enum
import core.utils.uxml
import core.vistrail.connection
import core.vistrail.controller
import core.vistrail.module
import core.vistrail.module_function
import core.vistrail.pipeline
import core.vistrail.port
import core.vistrail.vistrail
import db.services.io
import gui.common_widgets
import gui.graphics_view
import gui.method_palette
import gui.module_methods
import gui.pipeline_tab
import gui.pipeline_view
import gui.qt
import gui.theme
import gui.utils
import gui.version_view
import gui.vistrail_controller
import gui.vistrails_tree_layout_lw
spreadsheet = __import__('packages.spreadsheet', globals(), locals(), 
                            ['spreadsheet_controller'], -1) 

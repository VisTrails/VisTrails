############################################################################
##
## Copyright (C) 2006-2010 University of Utah. All rights reserved.
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
import core.vistrails_tree_layout_lw
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
spreadsheet = __import__('packages.spreadsheet', globals(), locals(), 
                            ['spreadsheet_controller'], -1) 

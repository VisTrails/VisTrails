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

from core.upgradeworkflow import UpgradeWorkflowHandler

def initialize():
    # can we copy over old configuration info to the new persistence package?
    pass

def handle_module_upgrade_request(controller, module_id, pipeline):
    module_remap = {'ManagedRef': \
                        [('0.1.0', None, 'persistence:PersistentRef', {})], 
                    'ManagedPath': \
                        [('0.1.0', None, 'persistence:PersistentPath', {})], 
                    'ManagedFile': \
                        [('0.1.0', None, 'persistence:PersistentFile', {})], 
                    'ManagedDir': \
                        [('0.1.0', None, 'persistence:PersistentDir', {})],
                    'ManagedInputFile': \
                        [('0.1.0', None, 
                          'persistence:PersistentInputFile', {})], 
                    'ManagedOutputFile': \
                        [('0.1.0', None, 
                          'persistence:PersistentOutputFile', {})],
                    'ManagedIntermediateFile': \
                        [('0.1.0', None, 
                          'persistence:PersistentIntermediateFile', {})],
                    'ManagedInputDir': \
                        [('0.1.0', None, 
                          'persistence:PersistentInputDir', {})],
                    'ManagedOutputDir': \
                        [('0.1.0', None, 
                          'persistence:PersistentOutputDir', {})],
                    'ManagedIntermediateDir': \
                        [('0.1.0', None, 
                          'persistence:PersistentIntermediateDir', {})]
                    }

    return UpgradeWorkflowHandler.remap_module(controller, module_id, pipeline,
                                               module_remap)

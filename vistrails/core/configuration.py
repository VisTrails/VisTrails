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

"""Configuration variables for controlling specific things in VisTrails."""

from core import debug
from core import system
from core.utils import InstanceObject
import copy
import core.logger
import core.packagemanager
import os.path
import shutil
import sys
import tempfile

##############################################################################

def default():
    """ default() -> InstanceObject
    Returns the default configuration of VisTrails
    
    """

    base_dir = {
        'dataDirectory': None,
        'debugSignals': False,
        'dotVistrails': system.default_dot_vistrails(),
        'fileRepository': default_file_repository(),
        'interactiveMode': True,
        'logger': default_logger(),
        'db': default_db(),
        'maxMemory': -1,
        'maximizeWindows': False,
        'minMemory': -1,
        'multiHeads': False,
        'nologger': False,
        'packageDirectory': None,
        'pythonPrompt': False,
        'rootDirectory': None,
        'shell': default_shell(),
        'showMovies': True,
        'showSplash': True,
        'useCache': True,
        'userPackageDirectory': None,
        'verbosenessLevel': -1,
        }
    return InstanceObject(**base_dir)

def default_file_repository():
    """default_file_repository() -> InstanceObject
    Returns the default configuration for the VisTrails file repository
    
    """
    file_repository_dir = {
        'dbHost': '',
        'dbName': '',
        'dbPasswd': '',
        'dbPort': 0,
        'dbUser': '',
        'localDir': '',
        'sshDir': '',
        'sshHost': '',
        'sshPort': 0,
        'sshUser': '',
        }
    return InstanceObject(**file_repository_dir)

def default_logger():
    """default_logger() -> InstanceObject
    Returns the default configuration for the VisTrails logger
    
    """
    logger_dir = {
        'dbHost': '',
        'dbName': '',
        'dbPasswd': '',
        'dbPort': 0,
        'dbUser': '',
        }
    return InstanceObject(**logger_dir)

def default_db():
    """default_db() -> InstanceObject
    Returns the default configuration for VisTrails db
    
    """
    db = {
        'host': '',
        'database': '',
        'passwd': '',
        'port': 0,
        'user': '',
        }
    return InstanceObject(**db)

def default_shell():
    """default_shell() -> InstanceObject
    Returns the default configuration for the VisTrails shell
    
    """
    if system.systemType == 'Linux':
        shell_dir = {
            'font_face': 'Fixed',
            'font_size': 12,
            }
    elif system.systemType in ['Windows', 'Microsoft']:
        shell_dir = {
            'font_face': 'Courier New',
            'font_size': 8,
            }
    elif system.systemType == 'Darwin':
        shell_dir = {
            'font_face': 'Monaco',
            'font_size': 12,
            }
    else:
        raise VistrailsInternalError('system type not recognized')
    return InstanceObject(**shell_dir)

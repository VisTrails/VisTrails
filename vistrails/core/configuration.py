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
from core.utils.uxml import (named_elements,
                             elements_filter, eval_xml_value,
                             quote_xml_value)
from PyQt4 import QtCore
import copy
import core.logger
import os.path
import shutil
import sys
import tempfile

##############################################################################

class ConfigurationObject(InstanceObject):
    """A ConfigurationObject is an InstanceObject that respects the
    following convention: values that are not 'present' in the object
    should have value (None, type), where type is the type of the
    expected object.

    ConfigurationObject exists so that the GUI can automatically infer
    the right types for the widgets.

    """

    def has(self, key):
        """has(key) -> bool.

        Returns true if key has valid value in the object.
        """
        
        if not hasattr(self, key):
            return False
        v = getattr(self, key)
        if type(v) == tuple and v[0] is None and type(v[1]) == type:
            return False
        return True

    def check(self, key):
        """check(key) -> obj

        Returns False if key is absent in object, and returns object
        otherwise.
        """
        
        return self.has(key) and getattr(self, key)

    def keys(self):
        """keys() -> list of strings

        Returns all options stored in this object.
        """
        
        return self.__dict__.keys()

    def write_to_dom(self, dom, element):
        conf_element = dom.createElement('configuration')
        element.appendChild(conf_element)
        for (key, value) in self.__dict__.iteritems():
            key_element = dom.createElement('key')
            key_element.setAttribute('name', key)
            if type(value) in [int, str, bool, float]:
                conf_element.appendChild(key_element)
                value_element = quote_xml_value(dom, value)
                key_element.appendChild(value_element)
            elif type(value) == tuple:
                pass
            else:
                assert isinstance(value, ConfigurationObject)
                conf_element.appendChild(key_element)
                value.write_to_dom(dom, key_element)

    def set_from_dom_node(self, node):
        assert str(node.nodeName) == 'configuration'
        for key in elements_filter(node, lambda node: node.nodeName == 'key'):
            key_name = str(key.attributes['name'].value)
            value = [x for x in
                     elements_filter(key, lambda node: node.nodeName in
                                    ['bool', 'str', 'int', 'float', 'configuration'])][0]
            value_type = value.nodeName
            if value_type == 'configuration':
                getattr(self, key_name).set_from_dom_node(value)
            elif value_type in ['bool', 'str', 'int', 'float']:
                setattr(self, key_name, eval_xml_value(value))
        

    def __copy__(self):
        result = ConfigurationObject()
        for (key, value) in self.__dict__.iteritems():
            setattr(result, key, copy.copy(value))
        return result

def default():
    """ default() -> ConfigurationObject
    Returns the default configuration of VisTrails
    
    """

    base_dir = {
        'dataDirectory': (None, str),
        'dbDefault': False,
        'debugSignals': False,
        'dotVistrails': system.default_dot_vistrails(),
        'fileDirectory': (None, str),
        'fileRepository': default_file_repository(),
        'interactiveMode': True,
        'logger': default_logger(),
        'db': default_db(),
        'maxMemory': (None, int),
        'maximizeWindows': False,
        'minMemory': (None, int),
        'multiHeads': False,
        'nologger': True,
        'packageDirectory': (None, str),
        'pythonPrompt': False,
        'rootDirectory': (None, str),
        'shell': default_shell(),
        'showMovies': True,
        'showSplash': True,
        'useCache': True,
        'userPackageDirectory': (None, str),
        'verbosenessLevel': (None, int),
        }
    return ConfigurationObject(**base_dir)

def default_file_repository():
    """default_file_repository() -> ConfigurationObject
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
    return ConfigurationObject(**file_repository_dir)

def default_logger():
    """default_logger() -> ConfigurationObject
    Returns the default configuration for the VisTrails logger
    
    """
    logger_dir = {
        'dbHost': '',
        'dbName': '',
        'dbPasswd': '',
        'dbPort': 0,
        'dbUser': '',
        }
    return ConfigurationObject(**logger_dir)

def default_db():
    """default_db() -> ConfigurationObject
    Returns the default configuration for VisTrails db
    
    """
    db = {
        'host': '',
        'database': '',
        'passwd': '',
        'port': 0,
        'user': '',
        }
    return ConfigurationObject(**db)

def default_shell():
    """default_shell() -> ConfigurationObject
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
    return ConfigurationObject(**shell_dir)

def get_vistrails_configuration():
    return QtCore.QCoreApplication.instance().configuration

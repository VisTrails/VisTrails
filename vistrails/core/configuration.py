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

"""Configuration variables for controlling specific things in VisTrails."""

import copy
import os.path
import shutil
import sys
import tempfile
import weakref

from core import debug
from core import system
from core.utils import (InstanceObject, Ref, append_to_dict_of_lists,
                        VistrailsInternalError)
from core.utils.uxml import (named_elements,
                             elements_filter, eval_xml_value,
                             quote_xml_value)

##############################################################################

class ConfigurationObject(InstanceObject):
    """A ConfigurationObject is an InstanceObject that respects the
    following convention: values that are not 'present' in the object
    should have value (None, type), where type is the type of the
    expected object.

    ConfigurationObject exists so that the GUI can automatically infer
    the right types for the widgets.

    """

    def __init__(self, *args, **kwargs):
        InstanceObject.__init__(self, *args, **kwargs)
        self.__subscribers__ = {}
   
    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)
        if name == '__subscribers__':
            return
        if name in self.__subscribers__:
            to_remove = []
            for subscriber in self.__subscribers__[name]:
                obj = subscriber()
                if obj:
                    obj(name, value)
                else:
                    to_remove.append(obj)
            for ref in to_remove:
                self.__subscribers__[name].remove(ref)

    def unsubscribe(self, field, callable_):
        """unsubscribe(field, callable_): remove observer from subject
        """
        self.__subscribers__[field].remove(weakref.ref(callable_))
        
    def subscribe(self, field, callable_):
        """subscribe(field, callable_): call observer callable_ when
        self.field is set.
        """
        append_to_dict_of_lists(self.__subscribers__, field,
                                Ref(callable_))
                  
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

    def allkeys(self):
        """allkeys() -> list of strings

        Returns all options stored in this object.
        """
        
        return self.__dict__.keys()

    def keys(self):
        """keys(self) -> list of strings
        Returns all public options stored in this object.
        Public options are keys that do not start with a _
        """
        return [k for k in self.__dict__.keys() if not k.startswith('_')]
    
    def write_to_dom(self, dom, element):
        conf_element = dom.createElement('configuration')
        element.appendChild(conf_element)
        for (key, value) in self.__dict__.iteritems():
            if key == '__subscribers__':
                continue
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
                if hasattr(self,key_name):
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
        'abstractionsDirectory': (None, str),
        'alwaysShowDebugPopup': False,
        'autosave': True,
        'dataDirectory': (None, str),
        'dbDefault': False,
#        'debugSignals': False,
        'defaultFileType':system.vistrails_default_file_type(),
        'detachHistoryView': False,
        'dotVistrails': system.default_dot_vistrails(),
        'executeWorkflows': False,
        'fileDirectory': (None, str),
#        'evolutionGraph': (None, str),
        'interactiveMode': True,
        'logFile': (None, str),
        'logger': default_logger(),
        'maxMemory': (None, int),
        'maximizeWindows': False,
        'maxRecentVistrails': 5,
        'migrateTags': False,
        'minMemory': (None, int),
        'multiHeads': False,
        'nologger': True,
        'packageDirectory': (None, str),
        'pythonPrompt': False,
        'recentVistrailList': (None, str),
        'repositoryLocalPath': (None, str),
        'repositoryHTTPURL': "http://www.vistrails.org/packages",
        'reviewMode': False,
        'rootDirectory': (None, str),
        'shell': default_shell(),
        'showScrollbars': True,
        'showMovies': True,
        'showSplash': True,
        'showSpreadsheetOnly': False,
        'spreadsheetDumpCells': (None, str),
        'spreadsheetDumpPDF': False,
        'staticRegistry': (None, str),
        'thumbs': default_thumbs(),
        'upgradeOn': True,
        'upgradeDelay': True,
        'upgradeModuleFailPrompt': True,
        'useCache': True,
        'userPackageDirectory': (None, str),
        'verbosenessLevel': (None, int),
#        'workflowGraph': (None, str),
#        'workflowInfo': (None, str),
        'webRepositoryLogin': (None, str),
        'webRepositoryURL': "http://www.crowdlabs.org",
        'isInServerMode': False,
        }
    specific_dir = add_specific_config(base_dir)
    return ConfigurationObject(**specific_dir)

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

def default_thumbs():
    """default_thumbs() -> ConfigurationObject
    Returns the default configuration for VisTrails Pipelines Thumbnails    
    """
    thumbs_dir = {
                  'autoSave': True,
                  'cacheDirectory': (None, str),
                  'cacheSize': 20,
                  'mouseHover': False,
                  'tagsOnly': False,
                }
    return ConfigurationObject(**thumbs_dir)

def add_specific_config(base_dir):
     """add_specific_config() -> dict
    Returns a dict with other specific configuration
    to the current platform added to base_dir
    
    """
     newdir = dict(base_dir)
     if system.systemType == 'Darwin':
         newdir['useMacBrushedMetalStyle'] = True
         
     return newdir

def get_vistrails_persistent_configuration():
    """get_vistrails_persistent_configuration() -> ConfigurationObject or None
    Returns the persistent configuration of the application. It returns None if
    configuration was not found (when running as a bogus application
    for example.
    Notice that this function should be use only to write configurations to
    the user's startup.xml file. Otherwise, use get_vistrails_configuration  or
    get_vistrails_temp_configuration.

    """
    from core.application import get_vistrails_application
    app = get_vistrails_application()
    if hasattr(app, 'configuration'):
        return app.configuration
    else:
        return None
    
def get_vistrails_configuration():
    """get_vistrails_configuration() -> ConfigurationObject or None
    Returns the current configuration of the application. It returns None if
    configuration was not found (when running as a bogus application
    for example. This configuration is the one that is used just for the
    current session and is not persistent. To make changes persistent, 
    use get_vistrails_persistent_configuration() instead.
    
    """
    from core.application import get_vistrails_application
    app = get_vistrails_application()
    if hasattr(app, 'temp_configuration'):
        return app.temp_configuration
    else:
        return None

def get_vistrails_temp_configuration():
    """get_vistrails_temp_configuration() -> ConfigurationObject or None
    Returns the temp configuration of the application. It returns None if
    configuration was not found (when running as a bogus application
    for example. The temp configuration is the one that is used just for the
    current session and is not persistent. To make changes persistent, 
    use get_vistrails_persistent_configuration() instead.
    
    """
    from core.application import get_vistrails_application
    app = get_vistrails_application()
    if hasattr(app, 'temp_configuration'):
        return app.temp_configuration
    else:
        return None

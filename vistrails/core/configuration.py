##############################################################################
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

"""Configuration variables for controlling specific things in VisTrails."""
import copy
import os.path
import shutil
import sys
import tempfile
import weakref

from vistrails.core import debug
from vistrails.core import system
from vistrails.core.utils import (InstanceObject, Ref, append_to_dict_of_lists,
                        VistrailsInternalError)
from vistrails.core.utils.uxml import (named_elements,
                             elements_filter, eval_xml_value,
                             quote_xml_value)
from vistrails.db.domain import DBConfiguration, DBConfigKey, DBConfigStr, \
    DBConfigInt, DBConfigFloat, DBConfigBool

##############################################################################

class ConfigValue(object):
    @staticmethod
    def create(value):
        if isinstance(value, bool):
            obj = ConfigBool()
        elif isinstance(value, basestring):
            obj = ConfigStr()
        elif isinstance(value, int):
            obj = ConfigInt()
        elif isinstance(value, float):
            obj = ConfigFloat()
        elif isinstance(value, ConfigurationObject):
            obj = value
        elif value is None:
            obj = None
        else:
            raise Exception('Cannot create ConfigValue from value "%s"' % value)
        if obj is not None:
            obj.set_value(value)
        return obj

    def get_value(self):
        return self.db_value

    def set_value(self, val):
        self.db_value = val
        
class ConfigBool(DBConfigBool, ConfigValue):
    def __copy__(self):
        """ __copy__() -> ConfigBool - Returns a clone of itself """ 
        return ConfigBool.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBConfigBool.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = ConfigBool
        return cp

    @staticmethod
    def convert(_val):
        _val.__class__ = ConfigBool

    def get_value(self):
        return self.db_value.lower() == "true"

    def set_value(self, val):
        self.db_value = unicode(val)

class ConfigInt(DBConfigInt, ConfigValue):
    def __copy__(self):
        """ __copy__() -> ConfigInt - Returns a clone of itself """ 
        return ConfigInt.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBConfigInt.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = ConfigInt
        return cp

    @staticmethod
    def convert(_val):
        _val.__class__ = ConfigInt

class ConfigStr(DBConfigStr, ConfigValue):
    def __copy__(self):
        """ __copy__() -> ConfigStr - Returns a clone of itself """ 
        return ConfigStr.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBConfigStr.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = ConfigStr
        return cp

    @staticmethod
    def convert(_val):
        _val.__class__ = ConfigStr

class ConfigFloat(DBConfigFloat, ConfigValue):
    def __copy__(self):
        """ __copy__() -> ConfigFloat - Returns a clone of itself """ 
        return ConfigFloat.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBConfigFloat.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = ConfigFloat
        return cp

    @staticmethod
    def convert(_val):
        _val.__class__ = ConfigFloat

class ConfigKey(DBConfigKey):
    def __init__(self, name, value):
        if isinstance(value, tuple):
            DBConfigKey.__init__(self, name=name)
            self.set_type(value[1])
        else:
            DBConfigKey.__init__(self, name=name, 
                                 value=ConfigValue.create(value))
            self.set_type(type(value))

    def __copy__(self):
        """ __copy__() -> ConfigKey - Returns a clone of itself """ 
        return ConfigKey.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBConfigKey.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = ConfigKey
        cp._type = self._type
        return cp
        
    @staticmethod
    def convert(_key):
        _key.__class__ = ConfigKey
        if isinstance(_key.db_value, DBConfiguration):
            ConfigurationObject.convert(_key.db_value)
        elif isinstance(_key.db_value, DBConfigBool):
            ConfigBool.convert(_key.db_value)
        elif isinstance(_key.db_value, DBConfigStr):
            ConfigStr.convert(_key.db_value)
        elif isinstance(_key.db_value, DBConfigInt):
            ConfigInt.convert(_key.db_value)
        elif isinstance(_key.db_value, DBConfigFloat):
            ConfigFloat.convert(_key.db_value)
        _key.set_type(type(_key.value))
    
    def _get_value(self):
        if self.db_value is not None:
            return self.db_value.get_value()
        return None
    def _set_value(self, val):
        if not self.check_type(val):
            raise TypeError("Value does not match type %s" % self._type)
        self.db_value = ConfigValue.create(val)
    value = property(_get_value, _set_value)

    def set_type(self, t):
        if issubclass(t, basestring):
            t = basestring
        self._type = t

    def check_type(self, val):
        return val is None or isinstance(val, self._type)

class ConfigurationObject(DBConfiguration):
    """A ConfigurationObject is an InstanceObject that respects the
    following convention: values that are not 'present' in the object
    should have value (None, type), where type is the type of the
    expected object.

    ConfigurationObject exists so that the GUI can automatically infer
    the right types for the widgets.

    """


    def __init__(self, **kwargs):
        self._in_init = True
        self._unset_keys = {}
        DBConfiguration.__init__(self)
        self._in_init = False
        for k, v in kwargs.iteritems():
            if type(v) == tuple:
                self._unset_keys[k] = v
            else:
                key = ConfigKey(name=k, value=v)
                self.db_add_config_key(key)
            
        # InstanceObject.__init__(self, *args, **kwargs)
        self.__subscribers__ = {}

    def __copy__(self):
        """ __copy__() -> ConfigurationObject - Returns a clone of itself """ 
        return ConfigurationObject.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBConfiguration.do_copy(self, new_ids, id_scope, id_remap)
        cp._in_init = False
        cp.__class__ = ConfigurationObject
        cp._unset_keys = copy.copy(self._unset_keys)
        cp.__subscribers__ = copy.copy(self.__subscribers__)
        return cp

    @staticmethod
    def convert(_config_obj):
        _config_obj._in_init = False
        _config_obj.__class__ = ConfigurationObject
        for _key in _config_obj.db_config_keys:
            ConfigKey.convert(_key)
        _config_obj.__subscribers__ = {}
        _config_obj._unset_keys = {}
   
    def get_value(self):
        return self
        
    def set_value(self, val):
        # it itself is the value already
        pass

    def matches_type(self, value, t):
        if t == str:
            t = basestring
        return isinstance(value, t)

    def __getattr__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            try:
                return self.get(name)
            except:
                raise AttributeError(name)

    def __setattr__(self, name, value):
        if name == '__subscribers__' or name == '_unset_keys' or name == '_in_init' or name == 'is_dirty' or \
           self._in_init:
            object.__setattr__(self, name, value)
        else:
            if name in self.db_config_keys_name_index:
                config_key = self.db_config_keys_name_index[name]
                config_key.value = value
            else:
                if name not in self._unset_keys:
                    return
                    # raise AttributeError('Key "%s" was not defined when '
                    #                      'ConfigurationObject was created' % 
                    #                      name)
                if not self.matches_type(value, self._unset_keys[name][1]):
                    raise TypeError('Value "%s" does match type "%s" for "%"' %
                                    (value, self._unset_keys[name][1], name))
                del self._unset_keys[name]
                config_key = ConfigKey(name=name, value=value)
                self.db_add_config_key(config_key)
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

    def update(self, other):
        for name, other_key in other.db_config_keys_name_index.iteritems():
            self.__setattr__(name, other_key.value)

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
        
        return key in self.db_config_keys_name_index

    def get(self, key):
        if key in self._unset_keys:
            return self._unset_keys[key]
        config_key = self.db_config_keys_name_index[key]
        return config_key.value

    def get_deep_value(self, keys_str):
        # keys_str is something like "thmbs.cacheDirectory"
        keys = keys_str.split('.')
        config = self
        for key in keys:
            config = config.get(key)
        return config

    def has_deep_value(self, keys_str):
        # keys_str is something like "thmbs.cacheDirectory"
        keys = keys_str.split('.')
        config = self
        for key in keys:
            if config.has(key):
                config = config.get(key)
            else:
                return False
        return True

    def set_deep_value(self, keys_str, value):
        keys = keys_str.split('.')
        config = self
        for key in keys[:-1]:
            config = config.get(key)
        config.__setattr__(keys[-1], value)

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
        
        return self.db_config_keys_name_index.keys()

    def keys(self):
        """keys(self) -> list of strings
        Returns all public options stored in this object.
        Public options are keys that do not start with a _
        """
        return [k for k in self.db_config_keys_name_index
                if not k.startswith('_')]
    
    def write_to_dom(self, dom, element):
        conf_element = dom.createElement('configuration')
        element.appendChild(conf_element)
        for (key, value) in self.__dict__.iteritems():
            if key == '__subscribers__':
                continue
            key_element = dom.createElement('key')
            key_element.setAttribute('name', key)
            if isinstance(value, (int, long, basestring, bool, float)):
                conf_element.appendChild(key_element)
                value_element = quote_xml_value(dom, value)
                key_element.appendChild(value_element)
            elif isinstance(value, tuple):
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
                                    ['unicode', 'bool', 'str', 'int', 'float', 'configuration'])][0]
            value_type = value.nodeName
            if value_type == 'configuration':
                if hasattr(self,key_name):
                    getattr(self, key_name).set_from_dom_node(value)
            elif value_type in ['bool', 'str', 'int', 'float']:
                setattr(self, key_name, eval_xml_value(value))
        

    # def __copy__(self):
    #     result = ConfigurationObject()
    #     for (key, value) in self.__dict__.iteritems():
    #         setattr(result, key, copy.copy(value))
    #     return result

def default():
    """ default() -> ConfigurationObject
    Returns the default configuration of VisTrails
    
    """

    base_dir = {
        'abstractionsDirectory': os.path.join("$DOT_VISTRAILS",
                                              "subworkflows"),
        'alwaysShowDebugPopup': False,
        'autoConnect': True,
        'autosave': True,
        'dataDirectory': (None, str),
        'dbDefault': False,
#        'debugSignals': False,
        'defaultFileType':system.vistrails_default_file_type(),
        'detachHistoryView': False,
        'dotVistrails': system.default_dot_vistrails(),
        'enablePackagesSilently': False,
        'errorOnConnectionTypeerror': False,
        'errorOnVariantTypeerror': True,
        'executeWorkflows': False,
        'fileDirectory': (None, str),
        'fixedSpreadsheetCells': False,
#        'evolutionGraph': (None, str),
        'installBundles': True,
        'installBundlesWithPip': False,
        'interactiveMode': True,
        'logFile': os.path.join("$DOT_VISTRAILS", "vistrails.log"),
        'logger': default_logger(),
        'maxMemory': (None, int),
        'maximizeWindows': False,
        'maxRecentVistrails': 5,
        'migrateTags': False,
        'minMemory': (None, int),
        'multiHeads': False,
        'nologger': False,
        'packageDirectory': (None, str),
        'pythonPrompt': False,
        'recentVistrailList': (None, str),
        'repositoryLocalPath': (None, str),
        'repositoryHTTPURL': "http://www.vistrails.org/packages",
        'reviewMode': False,
        'rootDirectory': (None, str),
        'runningJobsList': (None, str),
        'shell': default_shell(),
        'showScrollbars': True,
        'showMovies': True,
        'showSplash': True,
        'showSpreadsheetOnly': False,
        'singleInstance': True,
        'spreadsheetDumpCells': (None, str),
        'spreadsheetDumpPDF': False,
        'staticRegistry': (None, str),
        'stopOnError': True,
        'temporaryDirectory': (None, str),
        'thumbs': default_thumbs(),
        'upgradeOn': True,
        'upgradeDelay': True,
        'upgradeModuleFailPrompt': True,
        'useCache': True,
        'userPackageDirectory': os.path.join("$DOT_VISTRAILS", "userpackages"),
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
                  'cacheDirectory': os.path.join("$DOT_VISTRAILS", "thumbs"),
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
    from vistrails.core.application import get_vistrails_application
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
    from vistrails.core.application import get_vistrails_application
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
    from vistrails.core.application import get_vistrails_application
    app = get_vistrails_application()
    if hasattr(app, 'temp_configuration'):
        return app.temp_configuration
    else:
        return None

import os
import tempfile
import unittest

class TestConfiguration(unittest.TestCase):
    def test_config(self):
        conf = ConfigurationObject(a="blah", b=3.45, c=1, d=True)
        self.assertEqual(conf.a, "blah")
        self.assertAlmostEqual(conf.b, 3.45)
        self.assertEqual(conf.c, 1)
        self.assertEqual(conf.d, True)

    def test_default(self):
        conf = default()
        self.assertEqual(conf.showSpreadsheetOnly, False)
        self.assertEqual(conf.logger.dbPort, 0)

    def test_has(self):
        conf = default()
        self.assertTrue(conf.has("showSpreadsheetOnly"))
        self.assertFalse(conf.has("reallyDoesNotExist"))
    
    def test_check(self):
        conf = default()
        self.assertFalse(conf.check("showSpreadsheetOnly"))
        self.assertTrue(conf.check("autosave"))

    def test_update(self):
        conf1 = default()
        conf2 = ConfigurationObject(showSpreadsheetOnly=True, 
                                    logFile="/tmp/vt.log",
                                    shell=ConfigurationObject(font_face='Fixed',
                                                              font_size=12))

        conf1.update(conf2)
        self.assertTrue(conf1.showSpreadsheetOnly)
        self.assertEqual(conf1.logFile, "/tmp/vt.log")
        self.assertEqual(conf1.shell.font_face, 'Fixed')
        
        conf2.showSpreadsheetOnly = False
        self.assertTrue(conf1.showSpreadsheetOnly)

    def test_type_mismatch(self):
        conf = default()
        with self.assertRaises(TypeError):
            conf.showSpreadsheetOnly = 1

        # allowing this now
        # with self.assertRaises(AttributeError):
        #     conf.reallyDoesNotExist = True

    def check_equality(self, c1, c2):
        for name in c1.keys():
            self.assertIn(name, c2.keys())
            val1 = getattr(c1, name)
            val2 = getattr(c2, name)
            self.assertEqual(type(val1), type(val2), "Error on type for '%s'" % name)
            if isinstance(val1, ConfigurationObject):
                self.check_equality(val1, val2)
            else:
                self.assertEqual(val1, val2)

    def test_serialize(self):
        from vistrails.db.persistence import DAOList
        conf1 = default()
        (fd, fname) = tempfile.mkstemp()
        os.close(fd)
        try:
            dao = DAOList()
            dao.save_to_xml(conf1, fname, {})
            conf2 = dao.open_from_xml(fname, ConfigurationObject.vtType)
            ConfigurationObject.convert(conf2)
        finally:
            os.unlink(fname)

        self.check_equality(conf1, conf2)

    def test_copy(self):
        conf1 = default()
        conf2 = copy.copy(conf1)
        self.check_equality(conf1, conf2)
        self.assertItemsEqual(conf1._unset_keys.keys(), 
                              conf2._unset_keys.keys())

if __name__ == '__main__':
    unittest.main()


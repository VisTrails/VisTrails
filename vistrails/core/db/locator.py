###############################################################################
##
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
import base64
import getpass
import os.path
from vistrails.core import get_vistrails_application
from vistrails.core.configuration import get_vistrails_configuration
from vistrails.core.system import vistrails_default_file_type, get_elementtree_library, \
                        default_connections_file, vistrails_examples_directory
from vistrails.core.external_connection import ExtConnectionList, DBConnection
from vistrails.core.thumbnails import ThumbnailCache
from vistrails.core import debug
from vistrails.db.services.locator import XMLFileLocator as _XMLFileLocator, \
    DBLocator as _DBLocator, ZIPFileLocator as _ZIPFileLocator, \
    BaseLocator as _BaseLocator, UntitledLocator as _UntitledLocator
from vistrails.db.services.io import SaveBundle, test_db_connection
from vistrails.db import VistrailsDBException
from vistrails.db.domain import DBWorkflow
ElementTree = get_elementtree_library()

class BaseLocator(_BaseLocator):
    @staticmethod
    def convert_locator(locator):
        if locator.__class__ == _XMLFileLocator:
            locator.__class__ = XMLFileLocator
        elif locator.__class__ == _ZIPFileLocator:
            locator.__class__ = ZIPFileLocator
        elif locator.__class__ == _DBLocator:
            DBLocator.convert(locator)
        elif locator.__class__ == _UntitledLocator:
            locator.__class__ = UntitledLocator
            
    @staticmethod
    def from_url(url):
        locator = _BaseLocator.from_url(url)
        BaseLocator.convert_locator(locator)
        return locator

class CoreLocator(object):
    @staticmethod
    def prompt_autosave(parent_widget):
        pass # Opens a dialog that prompts the user if they want to
             # use temporaries


    @staticmethod
    def load_from_gui(parent_widget, obj_type):
        pass # Opens a dialog that the user will be able to use to
             # show the right values, and returns a locator suitable
             # for loading a file

    @staticmethod
    def save_from_gui(parent_widget, obj_type, locator):
        pass # Opens a dialog that the user will be able to use to
             # show the right values, and returns a locator suitable
             # for saving a file

    def update_from_gui(self, klass=None):
        pass

    # FIXME Need to do some more intelligent conversions anywhere this
    # function gets called
    @staticmethod
    def get_convert_klass(vt_type):
        from vistrails.core.vistrail.vistrail import Vistrail
        from vistrails.core.vistrail.pipeline import Pipeline
        from vistrails.core.log.log import Log
        from vistrails.core.modules.module_registry import ModuleRegistry
        from vistrails.core.log.opm_graph import OpmGraph
        
        klass_map = {Vistrail.vtType: Vistrail,
                     Pipeline.vtType: Pipeline,
                     Log.vtType: Log,
                     ModuleRegistry.vtType: ModuleRegistry,
                     OpmGraph.vtType: OpmGraph}
        return klass_map[vt_type]

class UntitledLocator(_UntitledLocator, CoreLocator):
    def load(self, klass=None):
        from vistrails.core.vistrail.vistrail import Vistrail
        if klass is None:
            klass = Vistrail
        obj = _UntitledLocator.load(self, klass.vtType)
        klass.convert(obj)
        obj.locator = self
        return obj

class XMLFileLocator(_XMLFileLocator, CoreLocator):

    def __init__(self, filename, **kwargs):
        _XMLFileLocator.__init__(self, filename, **kwargs)
        
    def load(self, klass=None):
        from vistrails.core.vistrail.vistrail import Vistrail
        if klass is None:
            klass = Vistrail
        obj = _XMLFileLocator.load(self, klass.vtType)
        klass.convert(obj)
        obj.locator = self
        return obj

    def save(self, obj):
        is_bundle = False
        if type(obj) == type(SaveBundle(None)):
            is_bundle = True
            save_bundle = obj
            obj = save_bundle.get_primary_obj()
        klass = obj.__class__
        obj = _XMLFileLocator.save(self, obj, False)
        klass.convert(obj)
        obj.locator = self
        if is_bundle:
            return SaveBundle(save_bundle.bundle_type, obj)
        return obj

    def save_as(self, obj, version=None):
        is_bundle = False
        if type(obj) == type(SaveBundle(None)):
            is_bundle = True
            save_bundle = obj
            obj = save_bundle.get_primary_obj()
        klass = obj.__class__
        obj = _XMLFileLocator.save(self, obj, True, version)
        klass.convert(obj)
        obj.locator = self
        if is_bundle:
            return SaveBundle(save_bundle.bundle_type, obj)
        return obj

    ##########################################################################

    def __eq__(self, other):
        if not isinstance(other, XMLFileLocator):
            return False
        return self._name == other._name

    ##########################################################################

    @staticmethod
    def prompt_autosave(parent_widget):
        import vistrails.gui.extras.core.db.locator as db_gui
        return db_gui.get_autosave_prompt(parent_widget)
        
    @staticmethod
    def load_from_gui(parent_widget, obj_type):
        import vistrails.gui.extras.core.db.locator as db_gui
        return db_gui.get_load_file_locator_from_gui(parent_widget, obj_type)

    @staticmethod
    def save_from_gui(parent_widget, obj_type, locator=None):
        import vistrails.gui.extras.core.db.locator as db_gui
        return db_gui.get_save_file_locator_from_gui(parent_widget, obj_type,
                                                         locator)

#    def update_from_gui(self, parent_widget, klass=None):
#        from core.vistrail.vistrail import Vistrail
#        if klass is None:
#            klass = Vistrail
#        import gui.extras.core.db.locator as db_gui
#        return db_gui.get_load_file_locator_from_gui(parent_widget, klass.vtType)

class DBLocator(_DBLocator, CoreLocator):
    class getKeyChain(object):
        def set_key(self, key, passwd):
            get_vistrails_application().keyChain.set_key(key,passwd)
        
        def get_key(self, key):
            return get_vistrails_application().keyChain.get_key(key)
    
    keyChain = getKeyChain()
    
    def __init__(self, host, port, database, user, passwd, name=None,
                 **kwargs):
        _DBLocator.__init__(self, host, port, database, user, passwd, name,
                            **kwargs)
        self.__list = ExtConnectionList.getInstance(default_connections_file())
        self.ext_connection_id = -1

    def load(self, klass=None):
        from vistrails.core.vistrail.vistrail import Vistrail
        if klass is None:
            klass = Vistrail
        save_bundle = _DBLocator.load(self, klass.vtType, ThumbnailCache.getInstance().get_directory())
        if klass.vtType == DBWorkflow.vtType:
            wf = save_bundle
            klass = self.get_convert_klass(wf.vtType)
            klass.convert(wf)
            wf.locator = self
            return wf
        for obj in save_bundle.get_db_objs():
            klass = self.get_convert_klass(obj.vtType)
            klass.convert(obj)
            obj.locator = self
        return save_bundle

    def save(self, save_bundle):
        save_bundle = _DBLocator.save(self, save_bundle, False)
        for obj in save_bundle.get_db_objs():
            klass = self.get_convert_klass(obj.vtType)
            klass.convert(obj)
            obj.locator = self
        return save_bundle

    def save_as(self, save_bundle, version=None):
        save_bundle = _DBLocator.save(self, save_bundle, True, version)
        for obj in save_bundle.get_db_objs():
            klass = self.get_convert_klass(obj.vtType)
            klass.convert(obj)
            obj.locator = self
        # Need to copy images into thumbnail cache directory so references
        # won't become invalid if they are in a temp dir that gets destroyed
        # when the previous locator is closed
        import shutil
        thumb_cache = ThumbnailCache.getInstance()
        thumb_cache_dir = thumb_cache.get_directory()
        new_thumbnails = []
        for thumbnail in save_bundle.thumbnails:
            if os.path.dirname(thumbnail) == thumb_cache_dir:
                new_thumbnails.append(thumbnail)
            else:
                cachedir_thumbnail = os.path.join(thumb_cache_dir, os.path.basename(thumbnail))
                try:
                    shutil.copyfile(thumbnail, cachedir_thumbnail)
                    new_thumbnails.append(cachedir_thumbnail)
                except Exception, e:
                    debug.critical("copying %s -> %s failed" % (
                                   thumbnail, cachedir_thumbnail),
                                   e)
        save_bundle.thumbnails = new_thumbnails
        # Need to update thumbnail cache in case some references have changed
        thumb_cache.add_entries_from_files(save_bundle.thumbnails)
        return save_bundle

    def update_from_gui(self, parent_widget, klass=None):
        from vistrails.core.vistrail.vistrail import Vistrail
        import vistrails.gui.extras.core.db.locator as db_gui
        if klass is None:
            klass = Vistrail
        config = self.find_connection_info(self._host, self._port, self._db) 
        if config is None or config['succeeded']==False:
            config = db_gui.get_db_connection_from_gui(parent_widget,
                                                       -1,
                                                       "",
                                                       self._host,
                                                       self._port,
                                                       self._user,
                                                       self._passwd,
                                                       self._db)
        
        if config is not None and config['succeeded'] == True:
            self._host = config['host']
            self._port = config['port']
            self._db = config['db']
            self._user = config['user']
            self._passwd = config['passwd']
            self.ext_connection_id = self.set_connection_info(**config)
            return True
        
        return False
    
    def update_from_console(self):
        config = self.find_connection_info(self._host, self._port, self._db)
        
        if config is None:
            # the problem here is if VisTrails is being run through command
            # line from LaTex, stdout is being redirected to a log file, so
            # the user does not see the prompt in raw_input. getpass uses the 
            # controlling terminal so it works fine. Just to make sure he sees 
            # the first message prompt we will the controlling terminal
            try:
                f= open('/dev/tty', 'w')
                f.write("\nConnect to db with username [%s]: "%self._user)
                f.close()
                user = raw_input()
            except IOError:
                debug.warning("Couldn't write to terminal. Will try stdout")
                user = raw_input("Connecting to db with username[%s]: "%self._user)
            try:
                if user != '':
                    self._user = user
                passwd = getpass.getpass("password:")
                self._passwd = passwd
                config = {'host': self._host,
                          'port': int(self._port),
                          'user': self._user,
                          'passwd': self._passwd,
                          'db': self._db
                          }
                test_db_connection(config)
                config['succeeded'] = True
                config['name'] = '%s@%s'%(self._user,self._host)
                config['id'] = -1
            except VistrailsDBException, e:
                debug.critical('VisTrails DB Exception',  e)
                config['succeeded'] = False
            except Exception, e2:
                debug.critical('VisTrails Exception', e2)
                config['succeeded'] = False
        if config is not None:
            if config['succeeded'] == False:
                passwd = getpass.getpass("\nVisTrails DB password for user %s:"%config['user'])
                self._user = config['user']
                self._passwd = passwd
                dbconfig = {'host': self._host,
                          'port': int(self._port),
                          'user': self._user,
                          'passwd': self._passwd,
                          'db': self._db
                          }
                try:
                    test_db_connection(dbconfig)
                    config['succeeded'] = True
                    config['passwd'] = self._passwd
                except VistrailsDBException, e:
                    debug.critical('VisTrails DB Exception', e)
                    config['succeeded'] = False
            
            if config['succeeded'] == True:
                self._host = config['host']
                self._port = config['port']
                self._db = config['db']
                self._user = config['user']
                self._passwd = config['passwd']
                self.ext_connection_id = self.set_connection_info(**config)
                return True
            return False
        return False
        
    def find_connection_info(self, host, port, db):
        """find_connection_info(host:str, port: int, db: str) -> dict
        Returns complete info of a connection with the given parameters

        """
        id = self.__list.find_db_connection(host,port,db)
        if id != -1:
            return self.get_connection_info(id)
        else:
            return None
    
    def get_connection_info(self, id):
        """get_connection_info(id: int) -> dict
        Returns info of ExtConnection """
        conn = self.__list.get_connection(id)
        if conn != None:
            succeeded = False
            key = str(conn.id) + "." + conn.name + "." + conn.host
            passwd = DBLocator.keyChain.get_key(key)
            config = {'host': conn.host,
                      'port': conn.port,
                      'user': conn.user,
                      'passwd': passwd}
            try:
                test_db_connection(config)
                succeeded = True
            except VistrailsDBException:
                succeeded = False
                
            config['id'] = conn.id
            config['name'] = conn.name
            config['db'] = conn.database
            config['succeeded'] = succeeded
        else:
            config = None
        return config
    
    def set_connection_info(self, *args, **kwargs):
        """set_connection_info(id: int, name: str, host: str, port:int,
                     user:str, passwd:str, db:str) -> None
        If the connection exists it will update it, else it will add it

        """
        if kwargs.has_key("id"):
            id = kwargs["id"]
        if kwargs.has_key("name"):
            name = kwargs["name"]
        if kwargs.has_key("host"):
            host = kwargs["host"]
        if kwargs.has_key("port"):
            port = kwargs["port"]
        if kwargs.has_key("user"):
            user = kwargs["user"]
        if kwargs.has_key("passwd"):
            passwd = kwargs["passwd"]
        if kwargs.has_key("db"):
            db = kwargs["db"]

        conn = DBConnection(id=id,
                            name=name,
                            host=host,
                            port=port,
                            user=user,
                            passwd='',
                            database=db,
                            dbtype='MySQL')
        
        if self.__list.has_connection(id):   
            self.__list.set_connection(id,conn)
        else:
            if conn.id == -1:
                conn.id = self.__list.get_fresh_id()
            self.__list.add_connection(conn)
        key = str(conn.id) + "." + conn.name + "." + conn.host
        DBLocator.keyChain.set_key(key,passwd)
        return conn.id
    
    ##########################################################################

    def __eq__(self, other):
        if type(other) != type(self):
            return False
        return (self._host == other._host and
                self._port == other._port and
                self._db == other._db and
                self._user == other._user and
                #self._name == other._name and
                long(self._obj_id) == long(other._obj_id) and
                self._obj_type == other._obj_type)

    ##########################################################################

    @staticmethod
    def prompt_autosave(parent_widget):
        return True

    @staticmethod
    def load_from_gui(parent_widget, obj_type):
        import vistrails.gui.extras.core.db.locator as db_gui
        return db_gui.get_load_db_locator_from_gui(parent_widget, obj_type)

    @staticmethod
    def save_from_gui(parent_widget, obj_type, locator=None):
        import vistrails.gui.extras.core.db.locator as db_gui
        return db_gui.get_save_db_locator_from_gui(parent_widget, obj_type,
                                                   locator)

    @staticmethod
    def from_xml(node, include_name=False):
        locator = _DBLocator.from_xml(node, include_name)
        locator.__class__ = DBLocator
        return locator
    
    @staticmethod
    def convert(locator):
        locator.__class__ = DBLocator
        locator.__list = ExtConnectionList.getInstance(
                                                   default_connections_file())

class ZIPFileLocator(_ZIPFileLocator, CoreLocator):

    def __init__(self, filename, **kwargs):
        _ZIPFileLocator.__init__(self, filename, **kwargs)

    def load(self, klass=None):
        from vistrails.core.vistrail.vistrail import Vistrail
        if klass is None:
            klass = Vistrail
        save_bundle = _ZIPFileLocator.load(self, klass.vtType)
        for obj in save_bundle.get_db_objs():
            klass = self.get_convert_klass(obj.vtType)
            klass.convert(obj)
            obj.locator = self
        return save_bundle

    def save(self, save_bundle):
        save_bundle = _ZIPFileLocator.save(self, save_bundle, False)
        for obj in save_bundle.get_db_objs():
            klass = self.get_convert_klass(obj.vtType)
            klass.convert(obj)
            obj.locator = self
        return save_bundle

    def save_as(self, save_bundle, version=None):
        save_bundle = _ZIPFileLocator.save(self, save_bundle, True, version)
        for obj in save_bundle.get_db_objs():
            klass = self.get_convert_klass(obj.vtType)
            klass.convert(obj)
            obj.locator = self
        # Need to update thumbnail cache since files have moved
        ThumbnailCache.getInstance().add_entries_from_files(save_bundle.thumbnails)
        return save_bundle

    ##########################################################################

    def __eq__(self, other):
        if not isinstance(other, ZIPFileLocator):
            return False
        return self._name == other._name

    ##########################################################################

    @staticmethod
    def prompt_autosave(parent_widget):
        import vistrails.gui.extras.core.db.locator as db_gui
        return db_gui.get_autosave_prompt(parent_widget)

    @staticmethod
    def load_from_gui(parent_widget, obj_type):
        import vistrails.gui.extras.core.db.locator as db_gui
        return db_gui.get_load_file_locator_from_gui(parent_widget, obj_type)

    @staticmethod
    def save_from_gui(parent_widget, obj_type, locator=None):
        import vistrails.gui.extras.core.db.locator as db_gui
        return db_gui.get_save_file_locator_from_gui(parent_widget, obj_type,
                                                         locator)

class FileLocator(CoreLocator):
    def __new__(self, filename=None, **kwargs):
        if filename:
            if filename.endswith('.vt'):
                return ZIPFileLocator(filename, **kwargs)
            elif filename.endswith('.vtl'):
                return FileLocator.from_link_file(filename)
            else:
                return XMLFileLocator(filename, **kwargs)
        else:
            #return class based on default file type
            if vistrails_default_file_type() == '.vt':
                return ZIPFileLocator
            else:
                return XMLFileLocator

    @staticmethod
    def prompt_autosave(parent_widget):
        import vistrails.gui.extras.core.db.locator as db_gui
        return db_gui.get_autosave_prompt(parent_widget)
    
    @staticmethod
    def load_from_gui(parent_widget, obj_type):
        import vistrails.gui.extras.core.db.locator as db_gui
        return db_gui.get_load_file_locator_from_gui(parent_widget, obj_type)

    @staticmethod
    def save_from_gui(parent_widget, obj_type, locator=None):
        import vistrails.gui.extras.core.db.locator as db_gui
        return db_gui.get_save_file_locator_from_gui(parent_widget, obj_type,
                                                         locator)

    @staticmethod
    def parse(element):
        """ parse(element) -> XMLFileLocator
        Parse an XML object representing a locator and returns an
        XMLFileLocator or a ZIPFileLocator object.

        """
        if str(element.getAttribute('type')) == 'file':
            for n in element.childNodes:
                if n.localName == "name":
                    filename = str(n.firstChild.nodeValue).strip(" \n\t")
                    return FileLocator(filename)
            return None
        else:
            return None
    
    #ElementTree port
    @staticmethod
    def from_xml(node):
        """from_xml(node:ElementTree.Element) -> XMLFileLocator or None
        Parse an XML object representing a locator and returns a
        XMLFileLocator or a ZIPFileLocator object."""
        if node.tag != 'locator':
            return None
        type_ = node.get('type', '')
        if str(type_) == 'file':
            for child in node.getchildren():
                if child.tag == 'name':
                    filename = child.text.encode('latin-1').strip()
                    return FileLocator(filename)
        return None
    
    @staticmethod
    def from_link_file(filename):
        """from_link_file(filename: str) -> DBLocator
        This will parse a '.vtl' file and  will create a DBLocator. .vtl files
        are vistrail link files and they are used to point vistrails to open
        vistrails from the database on the web. """
        def convert_from_str(value,type):
            def bool_conv(x):
                s = str(x).upper()
                if s == 'TRUE':
                    return True
                if s == 'FALSE':
                    return False
            
            if value is not None:
                if type == 'str':
                    return str(value)
                elif value.strip() != '':
                    if type == 'long':
                        return long(value)
                    elif type == 'float':
                        return float(value)
                    elif type == 'int':
                        return int(value)
                    elif type == 'bool':
                        return bool_conv(value)
                    elif type == 'base64':
                        return base64.b64decode(value)
            return None
        
        def guess_extension_from_contents(contents):
            if contents.startswith("<vistrail"):
                return ".xml"
            else:
                return ".vt"
            
        tree = ElementTree.parse(filename)
        node = tree.getroot()
        if node.tag != 'vtlink':
            return None
        #read attributes
        data = node.get('host', None)
        host = convert_from_str(data, 'str')
        data = node.get('port', None)
        port = convert_from_str(data,'int')
        data = node.get('database', None)
        database = convert_from_str(data,'str')
        data = node.get('vtid')
        vt_id = convert_from_str(data, 'int')
        data = node.get('version')
        version = convert_from_str(data, 'str')
        data = node.get('tag')
        tag = convert_from_str(data, 'str')
        data = node.get('execute')
        execute = convert_from_str(data, 'bool')
        data = node.get('showSpreadsheetOnly')
        showSpreadsheetOnly = convert_from_str(data, 'bool')
        data = node.get('url', None)
        url = convert_from_str(data,'str')
        data = node.get('vtcontent', None)
        vtcontent = convert_from_str(data,'base64')
        data = node.get('filename', None)
        vtname = convert_from_str(data, 'str')
        data = node.get('forceDB',None)
        forceDB = convert_from_str(data,'bool')
        data = node.get('mashuptrail', None)
        mashuptrail = convert_from_str(data, 'str')
        data = node.get('mashupVersion', None)
        mashupVersion = convert_from_str(data, 'int')
        data = node.get('parameterExploration', None)
        parameterExploration = convert_from_str(data, 'int')
        
        #if execute is False, we will show the builder too
        if showSpreadsheetOnly and not execute:
            showSpreadsheetOnly = False
        try:
            version = int(version)
        except (ValueError, TypeError):
            pass

        if tag is None:
            tag = '';
            
        ## execute and showSpreadsheetOnly should be written to the current
        ## configuration
        config = get_vistrails_configuration()
        config.execute = execute
        config.showWindow = not showSpreadsheetOnly
        if not forceDB:
            if vtcontent is not None:
                if url is not None:
                    basename = url.split('/')[-1]
                    base,ext = os.path.splitext(basename)
                    dirname = os.path.dirname(filename)
                    fname = os.path.join(dirname,basename)
                else:
                    basename = os.path.basename(filename)
                    base,ext = os.path.splitext(basename)
                    ext = guess_extension_from_contents(vtcontent)
                    dirname = os.path.dirname(filename)
                    fname = os.path.join(dirname,"%s%s"%(base,ext))
                create_file = True
                if os.path.exists(fname): #file was extracted before
                    create_file = False
                    oldf = open(fname)
                    oldcontents = oldf.read()
                    if oldcontents != vtcontent:
                        import vistrails.gui.extras.core.db.locator as db_gui
                        (overwrite, newname) = \
                                 db_gui.ask_to_overwrite_file(None, 'vistrail')
                        create_file = True
                        if newname:
                            fname = newname
                        elif overwrite == False:
                            i=1
                            while os.path.exists(fname):
                                newbase = "%s_%s%s" % (base, i, ext)
                                fname = os.path.join(dirname,newbase)
                                i+=1
                        
                if create_file:
                    f = open(fname,'wb')
                    f.write(vtcontent)
                    f.close()
                return FileLocator(fname, version_node=version, version_tag=tag,
                                   mashuptrail=mashuptrail,
                                   mashupVersion=mashupVersion,
                                   parameterExploration=parameterExploration)
        if host is not None:
            user = ""
            passwd = ""
            
            return DBLocator(host, port, database,
                             user, passwd, None, obj_id=vt_id,
                             obj_type='vistrail',connection_id=None,
                             version_node=version, version_tag=tag,
                             mashuptrail=mashuptrail,
                             mashupVersion=mashupVersion,
                             parameterExploration=parameterExploration)
        elif vtname is not None:
            if os.path.dirname(vtname) == '':
                #check if file exists in the same directory as the .vtl file
                dirname = os.path.dirname(filename)
                newvtname = os.path.join(dirname,vtname)
                if os.path.exists(newvtname):
                    vtname = newvtname
            #check for magic strings
            if "@examples" in vtname:
                vtname=vtname.replace("@examples", vistrails_examples_directory())
            return FileLocator(vtname, version_node=version, version_tag=tag,
                               mashuptrail=mashuptrail,
                               mashupVersion=mashupVersion,
                               parameterExploration=parameterExploration)

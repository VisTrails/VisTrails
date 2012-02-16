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

"""Describes the start-up process of VisTrails"""

from core import debug
from core import system
from core.utils.uxml import named_elements, elements_filter, \
     eval_xml_value, enter_named_element
import copy
import core.packagemanager
import core.utils
import os.path
import shutil
import sys
import tempfile
import core.configuration
import xml.dom.minidom

################################################################################

class VistrailsStartup(object):
    """
    VistrailsStartup is the class that initializes VisTrails based on
    a configuration. Both application mode (interactive and
    non-interactive) and import mode of VisTrails use this start up
    process to install packages and run .vistrails file. The purpose
    of this class is to separate the initialization process with Qt
    Application
    
    """

    def __init__(self, config=None, tempconfig=None):
        """ VistrailsStartup(config, tempconfig: ConfigurationObject,
                             optionsDict: dict) -> None
        Setup the configuration. config is the persistent configuration and 
        tempconfig is the current configuration.
        
        """
        assert (config is None or
                isinstance(config, core.configuration.ConfigurationObject))
        assert (tempconfig is None or
                isinstance(tempconfig, core.configuration.ConfigurationObject))
        if config:
            self.configuration = config
        else:
            self.configuration = core.configuration.default()
        if tempconfig:
            self.temp_configuration = tempconfig
        else:
            self.temp_configuration = copy.copy(self.configuration)
        
        self.startupHooks = []
        
        # This needs to be here because we want to log all initialization
        # steps
        self.setupLogFile()
        self._python_environment = self.runDotVistrails()
        self.load_configuration()
        
        #the problem is that maybe the logFile now points to a different place
        self.setupLogFile()
        
        self.setupDefaultFolders()
        #package_manager needs the persistent configuration    
        self._package_manager = core.packagemanager.PackageManager(
            self.configuration)
            
        self._do_load_packages = True
        self._package_dictionary = {}
        # stores all packages that must be enabled on startup
        self._needed_packages = []
        
    def init(self):
        """ init() -> None        
        Initialize VisTrails with optionsDict. optionsDict can be
        another VisTrails Configuration object, e.g. ConfigurationObject
        
        """
        if self._do_load_packages:
            self.load_packages()
        if self._do_load_packages:
            # don't call this anymore since we do an add_package for it now
            # self.setupBaseModules()
            self.installPackages()
        self.runStartupHooks()

    def set_needed_packages(self, package_list):
        self._needed_packages = package_list

    ##########################################################################
    # startup.xml related

    def startup_dom(self):
        filename = os.path.join(self.temp_configuration.dotVistrails,'startup.xml')
        return xml.dom.minidom.parse(filename)

    def write_startup_dom(self, dom):
        filename = os.path.join(self.temp_configuration.dotVistrails,'startup.xml')
        f = file(filename, 'w')
        f.write(dom.toxml())
                
    def load_configuration(self):
        """load_configuration() -> None
        Loads the appropriate configuration from .vistrails/startup.xml.
        This will overwrite both configuration and temp_configuration
        
        """
        dom = self.startup_dom()
        conf = enter_named_element(dom.documentElement, 'configuration')
        self.configuration.set_from_dom_node(conf)
        self.temp_configuration.set_from_dom_node(conf)
        
    def load_packages(self):
        """load_packages() -> None

        Loads the appropriate packages from .vistrails/startup.xml.
        """
        
        for package_name in self._needed_packages:
            self._package_manager.add_package(package_name)

        def parse_package(node):
            is_value = (lambda node: node.nodeName in
                        set(['bool', 'str', 'int', 'float']))
            package_name = str(node.attributes['name'].value)
            # FIXME use more robust checks here!
            if package_name != 'basic_modules' and \
                    package_name != 'abstraction':
                self._package_manager.add_package(package_name)
        dom = self.startup_dom()
        doc = dom.documentElement
        packages_node = enter_named_element(doc, 'packages')
        for package_node in named_elements(packages_node, 'package'):
            parse_package(package_node)

    ##########################################################################

    def get_python_environment(self):
        """get_python_environment(): returns the python environment generated
by startup.py. This should only be called after init()."""
        return self._python_environment

    def create_default_directory(self):
        if os.path.lexists(self.temp_configuration.dotVistrails):
            return

        debug.log('Will try to create default directory')
        try:
            os.mkdir(self.temp_configuration.dotVistrails)
            debug.log('Succeeded!')
        except:
            debug.critical("""Failed to create initialization directory.
                    This could be an indication of a permissions problem.
                    Make sure parent directory of '%s' is writable."""
                    % self.temp_configuration.dotVistrails)
            sys.exit(1)
                
    def runDotVistrails(self):
        """ runDotVistrails() -> None
        Setup to run user .vistrails file

        """        
        def addStartupHook(hook):
            """ addStartupHook(hook: function) -> None
            Add a hook for start-up after initialization
            
            """
            self.startupHooks.append(hook)

        def addPackage(packageName, *args, **keywords):
            """ addPackage(packageName: str, *args) -> None
            """
            self._package_manager.add_package(packageName)

        def create_user_packages_init(userpackagesname):
            try:
                name = os.path.join(userpackagesname, '__init__.py')
                f = file(name, 'w')
                f.write('pass\n')
                f.close()
            except:
                msg = ("""Failed to create file '%s'. This could indicate a
                rare combination of a race condition and a permissions problem.
                Please make sure it is writable.""" % name)
                debug.critical(msg)
                sys.exit(1)

        def create_user_packages_dir(userpackagesname=None):
            debug.warning('Will try to create userpackages directory')
            if userpackagesname is None:
                userpackagesname = os.path.join(self.temp_configuration.dotVistrails,
                                            'userpackages')
            if not os.path.isdir(userpackagesname):
                try:
                    os.mkdir(userpackagesname)
                    self.configuration.userPackageDirectory = userpackagesname
                    self.temp_configuration.userPackageDirectory = \
                        userpackagesname
                except:
                    msg = ("""Failed to create userpackages directory: '%s'.
                    This could be an indication of a permissions problem.
                    Make sure directory '%s' in writable.""" %
                           (userpackagesname,
                            self.configuration.dotVistrails))
                    debug.critical(msg)
                    sys.exit(1)
            create_user_packages_init(userpackagesname)
                
        def create_thumbnails_dir(thumbnails_dir=None):
            debug.log('Will try to create thumbnails directory')
            if thumbnails_dir is None:
                thumbnails_dir = os.path.join(self.temp_configuration.dotVistrails,
                                            'thumbs')

            if not os.path.isdir(thumbnails_dir):
                try:
                    os.mkdir(thumbnails_dir)
                    self.configuration.thumbs.cacheDirectory = thumbnails_dir
                    self.temp_configuration.thumbs.cacheDirectory = \
                        thumbnails_dir
                except:
                    msg = ("Failed to create thumbnails cache directory: '%s'.  "
                           "This could be an indication of a permissions "
                           "problem.  Make sure directory '%s' is writable." % \
                               (thumbnails_dir, 
                                self.configuration.dotVistrails))
                    debug.critical(msg)
                    sys.exit(1)   
                                
        def create_abstractions_dir(abstractions_dir=None):
            debug.log('Will try to create subworkflows directory')
            abstractions_dir = os.path.join(self.temp_configuration.dotVistrails,
                                            'subworkflows')

            if not os.path.isdir(abstractions_dir):
                try:
                    os.mkdir(abstractions_dir)
                    self.configuration.abstractionsDirectory = abstractions_dir
                    self.temp_configuration.abstractionsDirectory = \
                        abstractions_dir
                except:
                    msg = ("Failed to create subworkflows directory: '%s'.  "
                           "This could be an indication of a permissions "
                           "problem.  Make sure directory '%s' is writable." % \
                               (abstractions_dir, 
                                self.configuration.dotVistrails))
                    debug.critical(msg)
                    sys.exit(1)
#             try:
#                 root_dir = core.system.vistrails_root_directory()
#                 default_file = os.path.join(root_dir,'core','resources',
#                                             'abstractions_init')
#                 user_file = os.path.join(abstractions_dir, '__init__.py')
#                 print 'copying', default_file, '->', abstractions_dir
#                 shutil.copyfile(default_file, user_file)
#                 debug.log('Succeeded!')
#             except Exception, e:
#                 print e
#                 debug.critical("Failed to copy default file to abstractions "
#                                "package.  This could be an indication of a "
#                                "permissions problem. Make sure directory "
#                                "'%s' is writable" % abstractions_dir)
#                 sys.exit(1)

        def install_default_startup():
            debug.log('Will try to create default startup script')
            try:
                root_dir = core.system.vistrails_root_directory()
                default_file = os.path.join(root_dir,'core','resources',
                                            'default_vistrails_startup')
                user_file = os.path.join(self.temp_configuration.dotVistrails,
                                         'startup.py')
                shutil.copyfile(default_file,user_file)
                debug.log('Succeeded!')
            except:
                debug.critical("""Failed to copy default file %s.
                This could be an indication of a permissions problem.
                Make sure directory '%s' is writable"""
                % (user_file,self.temp_configuration.dotVistrails))
                sys.exit(1)

        def install_default_startupxml_if_needed():
            fname = os.path.join(self.temp_configuration.dotVistrails,
                                 'startup.xml')
            root_dir = core.system.vistrails_root_directory() 
            origin = os.path.join(root_dir, 'core','resources',
                                  'default_vistrails_startup_xml')
            def skip():
                if os.path.isfile(fname):
                    try:
                        d = self.startup_dom()
                        v = str(d.getElementsByTagName('startup')[0].attributes['version'].value)
                        r = core.utils.version_string_to_list(v)
                        return r >= [0, 1]
                    except:
                        return False
                else:
                    return False
            if skip():
                return
            try:
                shutil.copyfile(origin, fname)
                debug.log('Succeeded!')
            except:
                debug.critical("""Failed to copy default configuration
                file to %s. This could be an indication of a
                permissions problem. Please make sure '%s' is writable."""
                               % (fname,
                                  self.temp_configuration.dotVistrails))

        def execDotVistrails(tried_once=False):
            """ execDotVistrails() -> None
            Actually execute the Vistrail initialization
            
            """
            # if it is file, then must move old-style .vistrails to
            # directory.
            if os.path.isfile(self.temp_configuration.dotVistrails):
                debug.warning("Old-style initialization hooks. Will try to set things correctly.")
                (fd, name) = tempfile.mkstemp()
                os.close(fd)
                shutil.copyfile(self.temp_configuration.dotVistrails, name)
                try:
                    os.unlink(self.temp_configuration.dotVistrails)
                except:
                    debug.critical("""Failed to remove old initialization file.
                    This could be an indication of a permissions problem.
                    Make sure file '%s' is writable."""
                    % self.temp_configuration.dotVistrails)
                    sys.exit(1)
                self.create_default_directory()
                try:
                    destiny = os.path.join(self.temp_configuration.dotVistrails,
                                           'startup.py')
                    shutil.copyfile(name, destiny)
                except:
                    debug.critical("""Failed to copy old initialization file to
                    newly-created initialization directory. This must have been
                    a race condition. Please remove '%s' and
                    restart VisTrails."""
                    % self.temp_configuration.dotVistrails)
                    sys.exit(1)
                debug.critical("Successful move!")
                try:
                    os.unlink(name)
                except:
                    debug.warning("Failed to erase temporary file.")

            if os.path.isdir(self.temp_configuration.dotVistrails):
                if self.temp_configuration.check('userPackageDirectory'):
                    userpackages = self.temp_configuration.userPackageDirectory
                else:
                    userpackages = os.path.join(self.temp_configuration.dotVistrails,
                                            'userpackages')
                startup = os.path.join(self.temp_configuration.dotVistrails,
                                       'startup.py')
                if self.temp_configuration.check('abstractionsDirectory'):
                    abstractions = self.temp_configuration.abstractionsDirectory
                else:
                    abstractions = os.path.join(self.temp_configuration.dotVistrails,
                                            'subworkflows')
                if (self.temp_configuration.has('thumbs') and
                    self.temp_configuration.thumbs.check('cacheDirectory')):
                    thumbnails = self.temp_configuration.thumbs.cacheDirectory
                else:
                    thumbnails = os.path.join(self.temp_configuration.dotVistrails,
                                          'thumbs')
                if not os.path.isdir(userpackages):
                    create_user_packages_dir(userpackages)
                if not os.path.isfile(os.path.join(userpackages, 
                                                   '__init__.py')):
                    create_user_packages_init(userpackages)
                if not os.path.isdir(abstractions):
                    create_abstractions_dir(abstractions)
                if not os.path.isdir(thumbnails):
                    create_thumbnails_dir(thumbnails)
                try:
                    
                    dotVistrails = file(startup)
                    g = {}
                    localsDir = {'configuration': self.temp_configuration,
                                 'addStartupHook': addStartupHook,
                                 'addPackage': addPackage}
                    old_path = copy.copy(sys.path)
                    sys.path.append(self.temp_configuration.dotVistrails)
                    exec dotVistrails in localsDir
                    sys.path = old_path
                    del localsDir['addPackage']
                    del localsDir['addStartupHook']
                    return localsDir
                except IOError:
                    if tried_once:
                        debug.critical("""Still cannot find default file.
                        Something has gone wrong. Please make sure ~/.vistrails
                        exists, is writable, and ~/.vistrails/startup.py does
                        not exist.""")
                        sys.exit(1)
                    debug.critical('%s not found' % startup)
                    debug.critical('Will try to install default '
                                              'startup file')
                    install_default_startup()
                    install_default_startupxml_if_needed()
                    return execDotVistrails(True)
            elif not os.path.lexists(self.temp_configuration.dotVistrails):
                debug.log('%s not found' % self.temp_configuration.dotVistrails)
                self.create_default_directory()
                create_user_packages_dir()
                create_abstractions_dir()
                create_thumbnails_dir()
                install_default_startup()
                install_default_startupxml_if_needed()
                return execDotVistrails(True)

        #install_default_startupxml_if_needed()
        # Now execute the dot vistrails
        return execDotVistrails()

    def setupDefaultFolders(self):
        """ setupDefaultFolders() -> None        
        Give default values to folders when there are no values specified
        
        """
        if self.temp_configuration.has('rootDirectory'):
            system.set_vistrails_root_directory(self.temp_configuration.rootDirectory)
        if self.temp_configuration.has('dataDirectory'):
            system.set_vistrails_data_directory( \
                self.temp_configuration.dataDirectory)
        if self.temp_configuration.has('fileDirectory'):
            system.set_vistrails_file_directory( \
                self.temp_configuration.fileDirectory)
        if (self.temp_configuration.has('verbosenessLevel') and
            self.temp_configuration.verbosenessLevel != -1):
            verbose = self.temp_configuration.verbosenessLevel
            if verbose < 0:
                msg = ("""Don't know how to set verboseness level to %s - "
                       "setting to the lowest one I know of: 0""" % verbose)
                debug.critical(msg)
                verbose = 0
            if verbose > 2:
                msg = ("""Don't know how to set verboseness level to %s - "
                       "setting to the highest one I know of: 2""" % verbose)
                debug.critical(msg)
                verbose = 2
            dbg = debug.DebugPrint.getInstance()
            levels = [dbg.Critical, dbg.Warning, dbg.Log]
            dbg.set_message_level(levels[verbose])
            debug.log("Set verboseness level to %s" % verbose)
        
        #these checks may need to update the persistent configuration, so
        # we have to change both objects
        #userpackages directory
        if not self.temp_configuration.check('userPackageDirectory'):
            s = os.path.join(self.temp_configuration.dotVistrails,
                             'userpackages')
            self.temp_configuration.userPackageDirectory = s
        if not self.configuration.check('userPackageDirectory'):
            s = os.path.join(self.configuration.dotVistrails,
                             'userpackages')
            self.configuration.userPackageDirectory = s
        #abstractions directory    
        if not self.temp_configuration.check('abstractionsDirectory') or \
                self.temp_configuration.abstractionsDirectory == \
                os.path.join(self.temp_configuration.userPackageDirectory, 
                             'abstractions'):
            s = os.path.join(self.temp_configuration.dotVistrails,
                             'subworkflows')
            self.temp_configuration.abstractionsDirectory = s
        if not self.configuration.check('abstractionsDirectory') or \
                self.configuration.abstractionsDirectory == \
                os.path.join(self.configuration.userPackageDirectory, 
                             'abstractions'):
            s = os.path.join(self.configuration.dotVistrails,
                             'subworkflows')
            self.configuration.abstractionsDirectory = s
        #thumbnails directory    
        if self.temp_configuration.has('thumbs'):
            if not self.temp_configuration.thumbs.check('cacheDirectory'):
                s = os.path.join(self.temp_configuration.dotVistrails,'thumbs')
                self.temp_configuration.thumbs.cacheDirectory = s
        if self.configuration.has('thumbs'):
            if not self.configuration.thumbs.check('cacheDirectory'):
                s = os.path.join(self.configuration.dotVistrails, 'thumbs')
                self.configuration.thumbs.cacheDirectory = s
        
    def setupLogFile(self):
        def get_version():
            import core.system
            version = core.system.vistrails_version()
            return version.replace(".","_")
        #To make sure we always save a log file name according to the
        #current version, we will only consider the directory stored in
        # logFile and append a name with the correct version encoded. 
        if not self.temp_configuration.check('logFile'):
            s = os.path.join(self.temp_configuration.dotVistrails,
                             'vistrails_%s.log'%(get_version()))
            self.temp_configuration.logFile = s
        else:
            dirname = os.path.dirname(self.temp_configuration.logFile)
            self.temp_configuration.logFile = os.path.join(dirname,
                                        'vistrails_%s.log'%(get_version()))
        if not self.configuration.check('logFile'):
            # if this was not set before, it should point to the
            # value in temp_configuration
            s = os.path.join(self.temp_configuration.dotVistrails,
                             'vistrails_%s.log'%(get_version()))
            self.configuration.logFile = s
        else:
            dirname = os.path.dirname(self.configuration.logFile)
            self.configuration.logFile = os.path.join(dirname,
                                        'vistrails_%s.log'%(get_version()))
        if not os.path.lexists(self.temp_configuration.dotVistrails):
            self.create_default_directory()
        debug.DebugPrint.getInstance().set_logfile(self.temp_configuration.logFile)
        
    def setupBaseModules(self):
        """ setupBaseModules() -> None        
        Import basic modules for self-registration. The import here is
        on purpose, not a typo against the coding rule
        
        """
        import core.modules.vistrails_module
        import core.modules.basic_modules
        import core.modules.sub_module

    def installPackages(self):
        """ installPackages() -> None
        Scheme through packages directory and initialize them all
        """
        # Imports standard packages directory
        self._package_manager.initialize_packages(self._package_dictionary)

        # Enable abstractions
        import core.modules.abstraction
        abstraction_pkg = "abstraction"
        abstraction_dict = {abstraction_pkg: 'core.modules.'}
        self._package_manager.initialize_abstraction_pkg(abstraction_dict)

    def runStartupHooks(self):
        """ runStartupHooks() -> None
        After initialization, need to run all start up hooks registered
        
        """
        for hook in self.startupHooks:
            try:
                hook()
            except Exception, e:
                debug.critical("Exception raised during hook: %s - %s" %
                             (e.__class__, e))

    def destroy(self):
        """ destroy() -> None
        Finalize all packages to, such as, get rid of temp files
        
        """
        self._package_manager.finalize_packages()

    def set_registry(self, registry_filename=None):
        if registry_filename is not None:
            self._do_load_packages = False
        self._package_manager.init_registry(registry_filename)
            

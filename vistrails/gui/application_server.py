############################################################################
##
## Copyright (C) 2006-2009 University of Utah. All rights reserved.
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
""" This is the application for vistrails when running as a server.

"""

import hashlib
import sys
import logging
import os.path

from PyQt4 import QtGui, QtCore
from SimpleXMLRPCServer import SimpleXMLRPCServer

from gui.application import VistrailsApplicationInterface
from gui import qt
from core.db.locator import DBLocator
from core.db import io 
from core.utils import InstanceObject
from core import command_line
from core import system

import core.requirements
import core.console_mode

################################################################################
class StoppableXMLRPCServer(SimpleXMLRPCServer):
    accessList = ['localhost',
                  '127.0.0.1',
                  'vistrails.sci.utah.edu',
                  'vistrails',
                  '155.98.58.144'
                  ]

    allow_reuse_address = True

    def serve_forever(self):
        self.stop = False
        while not self.stop:
            self.handle_request()
    
    def verify_request(self, request, client_address):
        if client_address[0] in StoppableXMLRPCServer.accessList:
            return 1
        else:
            return 0


################################################################################
class VistrailsServerSingleton(VistrailsApplicationInterface,
                               QtGui.QApplication):
    """
    VistrailsServerSingleton is the singleton of the application,
    there will be only one instance of the application during VisTrails
    
    """
    def __call__(self):
        """ __call__() -> VistrailsServerSingleton
        Return self for calling method
        
        """
        if not self._initialized:
            self.init()
        return self
    
    def __init__(self):
        QtGui.QApplication.__init__(self, sys.argv)
        VistrailsApplicationInterface.__init__(self)
        if QtCore.QT_VERSION < 0x40400: # 0x40400 = 4.4.0
            raise core.requirements.MissingRequirement("Qt version >= 4.4")
        self.rpcserver = None
        self.temp_xml_rpc_options = InstanceObject(server=None,
                                                   port=None,
                                                   log_file=None)
        
        qt.allowQObjects()
    
    def make_logger(self, filename):
        """self.make_logger(filename:str) -> logger. Creates a logging object to
        be used for the server so we can log requests in file f."""
        f = open(filename, 'a')
        logger = logging.getLogger("VistrailsRPC")
        handler = logging.StreamHandler(f)
        handler.setFormatter(logging.Formatter('VisTrails RPC - %(asctime)s %(levelname)-8s %(message)s'))
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        return logger
    
    def init(self, optionsDict=None):
        """ init(optionDict: dict) -> boolean
        Create the application with a dict of settings
        
        """
        VistrailsApplicationInterface.init(self,optionsDict)
            
        self.vistrailsStartup.init()
        print self.temp_xml_rpc_options.log_file
        self.server_logger = self.make_logger(self.temp_xml_rpc_options.log_file)
        self._python_environment = self.vistrailsStartup.get_python_environment()
        self._initialized = True    
        return True

    def run_server(self):
        """run_server() -> None
        This will run forever until the server receives a quit request, done
        via xml-rpc.
        
        """
        self.rpcserver = StoppableXMLRPCServer((self.temp_xml_rpc_options.server,
                                               self.temp_xml_rpc_options.port))
        self.rpcserver.register_introspection_functions()
        self.rpcserver.register_function(self.run_vistrail_from_db, "run_from_db")
        self.rpcserver.register_function(self.get_tag_version,
                                         "get_tag_version")
        self.rpcserver.register_function(self.get_vt_xml, "get_vt_xml")
        self.rpcserver.register_function(self.get_wf_xml, "get_wf_xml")
        self.rpcserver.register_function(self.get_db_vistrail_list,
                                         "get_db_vt_list")
        self.rpcserver.register_function(self.quit_server, "quit")
        self.server_logger.info("Vistrails XML RPC Server is listening on http://%s:%s"% \
                        (self.temp_xml_rpc_options.server,
                         self.temp_xml_rpc_options.port))
        self.rpcserver.serve_forever()
        self.rpcserver.server_close()
        return 0
        
    def quit_server(self):
        self.rpcserver.stop = True
        result = "Vistrails XML RPC Server is quitting."
        self.server_logger.info(result)
        return result
    
    def get_tag_version(self, host, port, db_name, vt_id, vt_tag):
        self.server_logger.info("Request: get_tag_version(%s,%s,%s,%s,%s)"%(host,
                                                                 port,
                                                                 db_name,
                                                                 vt_id,
                                                                 vt_tag))
        version = -1
        try:
            locator = DBLocator(host=host,
                                port=int(port),
                                database=db_name,
                                user='vtserver',
                                passwd='',
                                obj_id=int(vt_id),
                                obj_type=None,
                                connection_id=None)
        
            (v, abstractions , thumbnails)  = io.load_vistrail(locator)
            if v.has_tag_with_name(vt_tag):
                version = v.get_tag_by_name(vt_tag).time
            self.server_logger.info("Answer: %s"%version)
            
        except Exception, e:
            self.server_logger.info("Error: %s"%str(e))
            
        return version
    
    def run_vistrail_from_db(self, host, port, db_name, vt_id, path_to_figures,
                             version=None, vt_tag='', parameters=''):
        self.server_logger.info("Request: run_vistrail_from_db(%s,%s,%s,%s,%s,%s,%s,%s)"%\
                                                            (host,
                                                             port,
                                                             db_name,
                                                             vt_id,
                                                             path_to_figures,
                                                             version,
                                                             vt_tag,
                                                             parameters))
        self.temp_configuration.spreadsheetDumpCells = path_to_figures
        result = ''
        if vt_tag !='':
            version = vt_tag;
        try:
            locator = DBLocator(host=host,
                                port=int(port),
                                database=db_name,
                                user='vtserver',
                                passwd='',
                                obj_id=int(vt_id),
                                obj_type=None,
                                connection_id=None)
            
            results = core.console_mode.run_and_get_results([(locator,int(version))],
                                                            parameters)
            ok = True
            for r in results:
                (objs, errors, executed) = (r.objects, r.errors, r.executed)
                for i in objs.iterkeys():
                    if errors.has_key(i):
                        ok = False
                        result += str(errors[i])
            if ok:
                self.server_logger.info("Success")
                return "SUCCESS"
            else:
                self.server_logger.info("Failure: %s"%result)
                return "FAILURE: " + result
        except Exception, e:
            self.server_logger.info("Failure: %s"% str(e))
            return "FAILURE: %s"% str(e)
        
    def get_db_vistrail_list(self, host, port, db_name):
        self.server_logger.info("Request: get_db_vistrail_list(%s,%s,%s)"%(host,
                                                                 port,
                                                                 db_name))
        config = {}
        config['host'] = host
        config['port'] = int(port)
        config['db'] = db_name
        config['user'] = 'vtserver'
        config['passwd'] = ''
        try:
            result = '<vistrails>'
            rows = io.get_db_vistrail_list(config)
            for (id, name, mod_time) in rows:
                result += '<vistrail id="%s" name="%s" mod_time="%s" />'% \
                                                            (id,name,mod_time)
            result += '</vistrails>'
            return result
        except Exception, e:
            self.server_logger.info("Error: %s"%str(e))
            return "FAILURE: %s" %str(e)
        
    def get_vt_xml(self, host, port, db_name, vt_id):
        self.server_logger.info("Request: get_vt_xml(%s,%s,%s,%s)"%(host,
                                                                 port,
                                                                 db_name,
                                                                 vt_id))
        try:
            locator = DBLocator(host=host,
                                port=int(port),
                                database=db_name,
                                user='vtserver',
                                passwd='',
                                obj_id=int(vt_id),
                                obj_type=None,
                                connection_id=None)
        
            (v, abstractions , thumbnails)  = io.load_vistrail(locator)
            result = io.serialize(v)
            self.server_logger.info("SUCCESS!")
            return result
        except Exception, e:
            self.server_logger.info("Error: %s"%str(e))
            return "FAILURE: %s" %str(e)
    
    def get_wf_xml(self, host, port, db_name, vt_id, version):
        self.server_logger.info("Request: get_wf_xml(%s,%s,%s,%s,%s)"%(host,
                                                                       port,
                                                                       db_name,
                                                                       vt_id,
                                                                       version))
        try:
            locator = DBLocator(host=host,
                                port=int(port),
                                database=db_name,
                                user='vtserver',
                                passwd='',
                                obj_id=int(vt_id),
                                obj_type=None,
                                connection_id=None)
        
            (v, abstractions , thumbnails)  = io.load_vistrail(locator)
            p = v.getPipeline(long(version))
            if p:
                result = io.serialize(p)
                print result
            else:
                result = "Error: Pipeline was not materialized"
                self.server_logger.info(result)
        except Exception, e:
            result = "Error: %s"%str(e)
            self.server_logger.info(result)
            
        return result
    
    def setupOptions(self):
        """ setupOptions() -> None
        Check and store all command-line arguments
        
        """
        add = command_line.CommandLineParser.add_option
        
        add("-T", "--xml_rpc_server", action="store", dest="rpcserver",
            help="hostname or ip address where this xml rpc server will work")
        add("-R", "--xml_rpc_port", action="store", type="int", default=8080,
            dest="rpcport", help="database port")
        add("-L", "--xml_rpc_log_file", action="store", dest="rpclogfile",
            default=os.path.join(system.vistrails_root_directory(),
                                 'rpcserver.log'),
            help="log file for XML RPC server")
        VistrailsApplicationInterface.setupOptions(self)
        
    def readOptions(self):
        """ readOptions() -> None
        Read arguments from the command line
        
        """
        get = command_line.CommandLineParser().get_option
        self.temp_xml_rpc_options = InstanceObject(server=get('rpcserver'),
                                                   port=get('rpcport'),
                                                   log_file=get('rpclogfile'))
        VistrailsApplicationInterface.readOptions(self)
        
    

# The initialization must be explicitly signalled. Otherwise, any
# modules importing vis_application will try to initialize the entire
# app.
def start_server(optionsDict=None):
    """Initializes the application singleton."""
    global VistrailsServer
    if VistrailsServer:
        print "Server already started."""
        return
    VistrailsServer = VistrailsServerSingleton()
    try:
        core.requirements.check_all_vistrails_requirements()
    except core.requirements.MissingRequirement, e:
        msg = ("VisTrails requires %s to properly run.\n" %
               e.requirement)
        print msg
        sys.exit(1)
    x = VistrailsServer.init(optionsDict)
    if x == True:
        return 0
    else:
        return 1

VistrailsServer = None

def stop_server():
    """Stop and finalize the application singleton."""
    global VistrailsServer
    VistrailsServer.save_configuration()
    VistrailsServer.destroy()
    VistrailsServer.deleteLater()
    
    


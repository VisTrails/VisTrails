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
""" This is the application for vistrails when running as a server.

"""
import Queue
import base64
import hashlib
import sys
import logging
import os
import os.path
import subprocess
import tempfile
import time
import urllib
import xmlrpclib

from PyQt4 import QtGui, QtCore
import SocketServer
from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from datetime import date, datetime
from time import strptime

from core.configuration import get_vistrails_configuration
from gui.application import VistrailsApplicationInterface
from gui import qt
from core.db.locator import DBLocator, ZIPFileLocator, FileLocator
from core.db import io
from core import debug
import core.db.action

from core.utils import InstanceObject
from core.vistrail.vistrail import Vistrail
from core import command_line
from core import system
from core.modules.module_registry import get_module_registry as module_registry
from core import interpreter
from gui.vistrail_controller import VistrailController
import core
import db.services.io
import gc
import traceback
ElementTree = core.system.get_elementtree_library()

import core.requirements
import core.console_mode

from db.versions import currentVersion

db_host = 'host.example.com'
db_read_user = 'vtserver'
db_read_pass = ''
db_write_user = 'repository'
db_write_pass = 'somepass'

################################################################################
class StoppableXMLRPCServer(SimpleXMLRPCServer):
    """This class allows a server to be stopped by a external request"""
    #accessList contains the list of ip addresses and hostnames that can send
    #request to this server. Change this according to your server
    accessList = ['localhost',
                  '127.0.0.1',
                  'vistrails.sci.utah.edu',
                  'vistrails',
                  ]

    allow_reuse_address = True

    def serve_forever(self):
        self.stop = False
        while not self.stop:
            self.handle_request()

    def verify_request(self, request, client_address):
        if client_address[0] in StoppableXMLRPCServer.accessList:
            debug.log("Request from %s allowed!" % client_address)
            return 1
        else:
            debug.log("Request from %s denied!" % client_address)
            return 0

################################################################################

class ThreadedXMLRPCServer(SocketServer.ThreadingMixIn,
                           StoppableXMLRPCServer): pass
"""This is a multithreaded version of the RPC Server. For each request, the 
    server will spawn a thread. Notice that these threads cannot use any Qt
    related objects because they won't be in the main thread."""
################################################################################

class RequestHandler(object):
    """This class will handle all the requests sent to the server. 
    Add new methods here and they will be exposed through the XML-RPC interface
    """
    def __init__(self, logger, instances):
        self.server_logger = logger
        self.instances = instances
        self.medley_objs = {}
        self.proxies_queue = None
        self.instantiate_proxies()

    #proxies
    def instantiate_proxies(self):
        """instantiate_proxies() -> None 
        If this server started other instances of VisTrails, this will create 
        the client proxies to connect to them. 
        """
        if len(self.instances) > 0:
            self.proxies_queue = Queue.Queue()
            for uri in self.instances:
                try:
                    proxy = xmlrpclib.ServerProxy(uri)
                    self.proxies_queue.put(proxy)
                    debug.log("Instantiated client for %s" % uri)
                except Exception, e:
                    debug.log("Error when instantiating proxy %s" % uri)
                    debug.log("Exception: %s" % str(e))
    #utils
    def memory_usage(self):
        """memory_usage() -> dict
        Memory usage of the current process in kilobytes. We plan to 
        use this to clear cache on demand later. 
        I believe this works on Linux only.
        """
        status = None
        result = {'peak': 0, 'rss': 0}
        try:
            # This will only work on systems with a /proc file system
            # (like Linux).
            status = open('/proc/self/status')
            for line in status:
                parts = line.split()
                key = parts[0][2:-1].lower()
                if key in result:
                    result[key] = int(parts[1])
        finally:
            if status is not None:
                status.close()
        return result

    def path_exists_and_not_empty(self, path):
        """path_exists_and_not_empty(path:str) -> boolean
        Returns True if given path exists and it's not empty, otherwise returns
        False.
        """
        if os.path.exists(path):
            n = 0
            for root, dirs, file_names in os.walk(path):
                n += len(file_names)
            if n > 0:
                return True
        return False

    #crowdlabs
    def get_wf_modules(self, host, port, db_name, vt_id, version):
        """get_wf_modules(host:str, port:int, db_name:str, vt_id:int, 
                          version:int) -> list of dict
           Returns a list of information about the modules used in a workflow 
           in a list of dictionaries. The dictionary has the following keys:
           name, package, documentation.
        """
        self.server_logger.info("Request: get_wf_modules(%s,%s,%s,%s,%s)"%(host,
                                                                       port,
                                                                       db_name,
                                                                       vt_id,
                                                                       version))
        try:
            locator = DBLocator(host=host,
                                port=int(port),
                                database=db_name,
                                user=db_read_user,
                                passwd=db_read_pass,
                                obj_id=int(vt_id),
                                obj_type=None,
                                connection_id=None)

            v = locator.load().vistrail
            p = v.getPipeline(long(version))

            if p:
                result = []
                for module in p.module_list:
                    descriptor = \
                       module_registry().get_descriptor_by_name(module.package,
                                                                module.name,
                                                                module.namespace)
                    if descriptor.module.__doc__:
                        documentation = descriptor.module.__doc__
                    else:
                        documentation = "Documentation not available."
                    result.append({'name':module.name, 'package':module.package, 
                                   'documentation':documentation})
                return result
            else:
                result = "Error: Pipeline was not materialized"
                self.server_logger.info(result)
        except Exception, e:
            result = "Error: %s"%str(e)
            self.server_logger.info(result)

        return result

    def get_packages(self):
        """get_packages()-> dict
        This returns a dictionary with all the packages available in the 
        VisTrails registry.
        The keys are the package identifier and for each identifier there's a 
        dictionary with modules and description.
        """
        try:
            package_dic = {}

            for package in module_registry().package_list:
                package_dic[package.identifier] = {}
                package_dic[package.identifier]['modules'] = []
                for module in package._db_module_descriptors:
                    if module.module.__doc__:
                        documentation = module.module.__doc__
                    else:
                        documentation = "Documentation not available."
                    package_dic[package.identifier]['modules'].append({'name':module.name, 'package':module.package, 'documentation':documentation})
                package_dic[package.identifier]['description'] = package.description if package.description else "No description available"
            return package_dic
        except Exception, e:
            self.server_logger.info("Error: %s"%str(e))
            return "FAILURE: %s" %str(e)
        
    def add_vt_to_db(self, host, port, db_name, user, vt_filepath, filename, 
                     repository_vt_id, repository_creator):
        """add_vt_to_db(host:str, port:int, db_name:str, user:str, 
                        vt_filepath:str, filename:str, repository_vt_id:int, 
                        repository_creator:str) -> int 
        This will add a vistrail in vt_filepath to the the database. Before
        adding it it will annotate the vistrail with the repository_vt_id and 
        repository_creator.
                        
        """                
        try:
            locator = ZIPFileLocator(vt_filepath).load()
            # set some crowdlabs id info
            if repository_vt_id != -1:
                vistrail = locator.vistrail
                vistrail.set_annotation('repository_vt_id', repository_vt_id)
                vistrail.set_annotation('repository_creator', repository_creator)
            #print "name=%s"%filename
            db_locator = DBLocator(host=host, port=int(port), database=db_name,
                                   name=filename, user=db_write_user, passwd=db_write_pass)
            db_locator.save_as(locator)
            #print "db_locator obj_id %s" % db_locator.obj_id
            return db_locator.obj_id
        except Exception, e:
            self.server_logger.info("Error: %s"%str(e))
            return "FAILURE: %s" %str(e)

    def merge_vt(self, host, port, db_name, user, new_vt_filepath,
                 old_db_vt_id):
        # XXX: It should be complete now, but I haven't tested it (--Manu).
        try:
            new_locator = ZIPFileLocator(new_vt_filepath)
            new_bundle = new_locator.load()
            new_locator.save(new_bundle)
            old_db_locator = DBLocator(host=host, port=int(port), database=db_name,
                                       obj_id=old_db_vt_id, user=db_write_user, passwd=db_write_pass)
            old_db_bundle = old_db_locator.load()
            db.services.vistrail.merge(old_db_bundle, new_bundle, 'vistrails')
            old_db_locator.save(old_db_bundle)
            new_locator.save(old_db_bundle)
            return 1
        except Exception, e:
            self.server_logger.info("Error: %s"%str(e))
            import traceback
            traceback.print_exc()
            return "FAILURE: %s" %str(e)
        
    def remove_vt_from_db(self, host, port, db_name, user, vt_id):
        """remove_vt_from_db(host:str, port:int, db_name:str, user:str,
                             vt_id:int) -> 0 or 1
        Remove a vistrail from the repository
        """
        config = {}
        config['host'] = host
        config['port'] = int(port)
        config['db'] = db_name
        config['user'] = db_write_user
        config['passwd'] = db_write_pass
        try:
            conn = db.services.io.open_db_connection(config)
            db.services.io.delete_entity_from_db(conn,'vistrail', vt_id)
            db.services.io.close_db_connection(conn)
            return 1
        except Exception, e:
            self.server_logger.info("Error: %s"%str(e))
            if conn:
                db.services.io.close_db_connection(conn)
            return "FAILURE: %s" %str(e)

    def get_runnable_workflows(self, host, port, db_name, vt_id):
        print "get_runnable_workflows"
        try:
            locator = DBLocator(host=host,
                                port=int(port),
                                database=db_name,
                                user=db_read_user,
                                passwd=db_read_pass,
                                obj_id=int(vt_id),
                                obj_type=None,
                                connection_id=None)
            (vistrail, _, _)  = io.load_vistrail(locator)

            # get server packages
            local_packages = [x.identifier for x in \
                              module_registry().package_list]

            runnable_workflows = []
            py_source_workflows = []
            local_data_modules = ['File', 'FileSink', 'Path']

            # find runnable workflows
            for version_id, version_tag in vistrail.get_tagMap().iteritems():
                pipeline = vistrail.getPipeline(version_id)
                workflow_packages = set()
                on_repo = True
                has_python_source = False
                for module in pipeline.module_list:
                    # count modules that use data unavailable to web repo
                    if module.name[-6:] == 'Reader' or \
                       module.name in local_data_modules:
                        has_accessible_data = False
                        for edge in pipeline.graph.edges_to(module.id):
                            # TODO check for RepoSync checksum param
                            if pipeline.modules[edge[0]].name in \
                               ['HTTPFile', 'RepoSync']:
                                has_accessible_data = True

                        if not has_accessible_data:
                            on_repo = False

                    elif module.name == "PythonSource":
                        has_python_source = True

                    # get packages used in tagged versions of this VisTrail
                    workflow_packages.add(module.package)

                # ensure workflow doesn't use unsupported packages
                if not filter(lambda p: p not in local_packages,
                              workflow_packages):
                    if has_python_source and on_repo and \
                       version_id not in py_source_workflows:
                        py_source_workflows.append(version_id)

                    elif not has_python_source and on_repo and \
                            version_id not in runnable_workflows:
                        runnable_workflows.append(version_id)

            self.server_logger.info("SUCCESS!")
            print "\n\nRunnable Workflows Return"
            for wf_id in runnable_workflows:
                print vistrail.get_tag(wf_id)
            print "\n\nPython Source Workflows Return"
            for wf_id in py_source_workflows:
                print vistrail.tagMap[wf_id].name
            print "\n\n"
            return runnable_workflows, py_source_workflows

        except Exception, e:
            self.server_logger.info("Error: %s"%str(e))
            return "FAILURE: %s" %str(e)
    
    def get_package_list(self):
        """ get_package_list() -> str
         Returns a list of supported packages identifiers delimited by || """
        packages = [x.identifier for x in module_registry().package_list]
        return '||'.join(packages)    
        
    def get_wf_datasets(self, host, port, db_name, vt_id, version):
        print 'get workflow datasets'
        self.server_logger.info("Request: get_wf_datasets(%s,%s,%s,%s,%s)"%(host,
                                                                           port,
                                                                           db_name,
                                                                           vt_id,
                                                                           version))
        try:
            locator = DBLocator(host=host,
                                port=int(port),
                                database=db_name,
                                user=db_read_user,
                                passwd=db_read_pass,
                                obj_id=int(vt_id),
                                obj_type=None,
                                connection_id=None)

            v = locator.load().vistrail
            p = v.getPipeline(long(version))

            if p:
                result = []
                for module in p.module_list:
                    if module.name == "RepoSync":
                        for function in module.functions:
                            if function.name == 'checksum':
                                result.append(function.parameters[0].value())
                return result
            else:
                result = "Error: Pipeline was not materialized"
                self.server_logger.info(result)
        except Exception, e:
            result = "Error: %s"%str(e)
            self.server_logger.info(result)
        return result
    
    #vistrails
    def run_from_db(self, host, port, db_name, vt_id, path_to_figures,
                    version=None,  pdf=False, vt_tag='',parameters=''):
#        self.server_logger.info("Request: run_vistrail_from_db(%s,%s,%s,%s,%s,%s,%s,%s)"%\
        print "Request: run_from_db(%s,%s,%s,%s,%s,%s,%s,%s,%s)"%\
                                                            (host,
                                                             port,
                                                             db_name,
                                                             vt_id,
                                                             path_to_figures,
                                                             version,
                                                             pdf,
                                                             vt_tag,
                                                             parameters)
        print self.path_exists_and_not_empty(path_to_figures)
        print self.proxies_queue
        if (not self.path_exists_and_not_empty(path_to_figures) and
            self.proxies_queue is not None):
            print "Will forward request "
            #this server can send requests to other instances
            proxy = self.proxies_queue.get()
            try:
                print "Sending request to ", proxy
                result = proxy.run_from_db(host, port, db_name, vt_id, 
                                           path_to_figures, version, pdf, vt_tag,
                                           parameters)
                self.proxies_queue.put(proxy)
                print "returning %s"% result
                self.server_logger.info("returning %s"% result)
                return result
            except Exception, e:
                print "Exception: ", str(e)
                return ""
            
        extra_info = {}
        extra_info['pathDumpCells'] = path_to_figures
        extra_info['pdf'] = pdf
        # execute workflow
        ok = True
        print "will execute here"
        if not self.path_exists_and_not_empty(extra_info ['pathDumpCells']):
            if not os.path.exists(extra_info ['pathDumpCells']):
                os.mkdir(extra_info ['pathDumpCells'])
            result = ''
            if vt_tag !='':
                version = vt_tag;
            try:
                locator = DBLocator(host=host,
                                    port=int(port),
                                    database=db_name,
                                    user=db_write_user,
                                    passwd=db_write_pass,
                                    obj_id=int(vt_id),
                                    obj_type=None,
                                    connection_id=None)

                results = []
                try:
                    results = \
                    core.console_mode.run_and_get_results([(locator,
                                                          int(version))],
                                                          parameters,
                                                          extra_info=extra_info)
                    print "results: %s" % results

                except Exception, e:
                    print str(e)
                ok = True
                for r in results:
                    print r
                    (objs, errors, _) = (r.objects, r.errors, r.executed)
                    for i in objs.iterkeys():
                        if errors.has_key(i):
                            ok = False
                            result += str(errors[i])
            except Exception, e:
                self.server_logger.info("Failure: %s"% str(e))
                return "FAILURE: %s"% str(e)

        if ok:
            self.server_logger.info("Success")
            return "SUCCESS"
        else:
            self.server_logger.info("Failure: %s"%result)
            return "FAILURE: " + result
        
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
                                user=db_read_user,
                                passwd=db_read_pass,
                                obj_id=int(vt_id),
                                obj_type=None,
                                connection_id=None)

            (v, _ , _)  = io.load_vistrail(locator)
            if v.has_tag_str(vt_tag):
                version = v.get_tag_str(vt_tag).action_id
            self.server_logger.info("Answer: %s"%version)

        except Exception, e:
            self.server_logger.info("Error: %s"%str(e))

        return version
                      
                      
    def get_vt_xml(self, host, port, db_name, vt_id):
        self.server_logger.info("Request: get_vt_xml(%s,%s,%s,%s)"%(host,
                                                                 port,
                                                                 db_name,
                                                                 vt_id))
        try:
            locator = DBLocator(host=host,
                                port=int(port),
                                database=db_name,
                                user=db_read_user,
                                passwd=db_read_pass,
                                obj_id=int(vt_id),
                                obj_type=None,
                                connection_id=None)

            (v, _ , _)  = io.load_vistrail(locator)
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
                                user=db_read_user,
                                passwd=db_read_pass,
                                obj_id=int(vt_id),
                                obj_type=None,
                                connection_id=None)

            print "start"
            (v, _ , _)  = io.load_vistrail(locator)
            print "v is setup"
            p = v.getPipeline(long(version))
            print "pipeline setup"
            if p:
                result = io.serialize(p)
                print "pipeline serialized"
            else:
                result = "Error: Pipeline was not materialized"
                self.server_logger.info(result)
        except Exception, e:
            result = "get_wf_xml Error: %s"%str(e)
            self.server_logger.info(result)

        return result

    def get_wf_graph_pdf(self, host, port, db_name, vt_id, version):
        """get_wf_graph_pdf(host:str, port:int, db_name:str, vt_id:int, 
                          version:int) -> str
         Returns the relative url to the generated PDF
         """
        self.server_logger.info( "get_wf_graph_pdf(%s,%s,%s,%s,%s) request received"%(host,
                                                                                    port,
                                                                                    db_name,
                                                                                    vt_id,
                                                                                    version))
        print "get_wf_graph_pdf(%s,%s,%s,%s,%s) request received"%(host,
                                                      port,
                                                      db_name,
                                                      vt_id,
                                                      version)
        try:
            vt_id = long(vt_id)
            version = long(version)            
            subdir = 'workflows'
            filepath = os.path.join('/server/crowdlabs/site_media/media/graphs',
                                  subdir)
            base_fname = "graph_%s_%s.pdf" % (vt_id, version)
            filename = os.path.join(filepath,base_fname)
            if ((not os.path.exists(filepath) or
                os.path.exists(filepath) and not os.path.exists(filename)) 
                and self.proxies_queue is not None):
                #this server can send requests to other instances
                proxy = self.proxies_queue.get()
                try:
                    print "Sending request to ", proxy
                    result = proxy.get_wf_graph_pdf(host,port,db_name, vt_id, version)
                    self.proxies_queue.put(proxy)
                    print "returning %s"% result
                    self.server_logger.info("returning %s"% result)
                    return result
                except Exception, e:
                    print "Exception: ", str(e)
                    return ""
            
            if not os.path.exists(filepath):
                os.mkdir(filepath)
           
            if not os.path.exists(filename):
                locator = DBLocator(host=host,
                                    port=port,
                                    database=db_name,
                                    user=db_read_user,
                                    passwd=db_read_pass,
                                    obj_id=vt_id,
                                    obj_type=None,
                                    connection_id=None)

                (v, abstractions , thumbnails)  = io.load_vistrail(locator)
                controller = VistrailController()
                controller.set_vistrail(v, locator, abstractions, thumbnails)
                controller.change_selected_version(version)

                p = controller.current_pipeline
                from gui.pipeline_view import QPipelineView
                pipeline_view = QPipelineView()
                pipeline_view.scene().setupScene(p)
                pipeline_view.scene().saveToPDF(filename)
                del pipeline_view
            else:
                print "found cached pdf: ", filename
            return os.path.join(subdir,base_fname)
        except Exception, e:
            print "Error when saving pdf: ", str(e)
            
    def get_wf_graph_png(self, host, port, db_name, vt_id, version):
        """get_wf_graph_png(host:str, port:int, db_name:str, vt_id:int, 
                          version:int) -> str
         Returns the relative url to the generated image
         """
        self.server_logger.info( "get_wf_graph_png(%s,%s,%s,%s,%s) request received"%(host,
                                                                                    port,
                                                                                    db_name,
                                                                                    vt_id,
                                                                                    version))
        print "get_wf_graph_png(%s,%s,%s,%s,%s) request received"%(host,
                                                      port,
                                                      db_name,
                                                      vt_id,
                                                      version)
        try:
            vt_id = long(vt_id)
            version = long(version)            
            subdir = 'workflows'
            filepath = os.path.join('/server/crowdlabs/site_media/media/graphs',
                                  subdir)
            base_fname = "graph_%s_%s.png" % (vt_id, version)
            filename = os.path.join(filepath,base_fname)
            if ((not os.path.exists(filepath) or
                os.path.exists(filepath) and not os.path.exists(filename)) 
                and self.proxies_queue is not None):
                #this server can send requests to other instances
                proxy = self.proxies_queue.get()
                try:
                    print "Sending request to ", proxy
                    result = proxy.get_wf_graph_png(host, port, db_name, vt_id, version)
                    self.proxies_queue.put(proxy)
                    print "returning %s"% result
                    self.server_logger.info("returning %s"% result)
                    return result
                except Exception, e:
                    print "Exception: ", str(e)
                    return ""
            #if it gets here, this means that we will execute on this instance
            if not os.path.exists(filepath):
                os.mkdir(filepath)

            if not os.path.exists(filename):
                locator = DBLocator(host=host,
                                    port=port,
                                    database=db_name,
                                    user=db_read_user,
                                    passwd=db_read_pass,
                                    obj_id=vt_id,
                                    obj_type=None,
                                    connection_id=None)
                (v, abstractions , thumbnails)  = io.load_vistrail(locator)
                controller = VistrailController()
                controller.set_vistrail(v, locator, abstractions, thumbnails)
                controller.change_selected_version(version)
                p = controller.current_pipeline
                from gui.pipeline_view import QPipelineView
                pipeline_view = QPipelineView()
                pipeline_view.scene().setupScene(p)
                pipeline_view.scene().saveToPNG(filename)
                del pipeline_view
            else:
                print "Found cached image: ", filename
            return os.path.join(subdir,base_fname)
        except Exception, e:
            print "Error when saving png: ", str(e)
            
    def get_vt_graph_png(self, host, port, db_name, vt_id):
        """get_vt_graph_png(host:str, port: str, db_name: str, vt_id:str) -> str
        Returns the relative url of the generated image
        
        """
        try:
            vt_id = long(vt_id) 
            subdir = 'vistrails'
            filepath = os.path.join('/server/crowdlabs/site_media/media/graphs',
                                  subdir)
            base_fname = "graph_%s.png" % (vt_id)
            filename = os.path.join(filepath,base_fname)
            if ((not os.path.exists(filepath) or
                os.path.exists(filepath) and not os.path.exists(filename)) 
                and self.proxies_queue is not None):
                #this server can send requests to other instances
                proxy = self.proxies_queue.get()
                try:
                    print "Sending request to ", proxy
                    result = proxy.get_vt_graph_png(host, port, db_name, vt_id)
                    self.proxies_queue.put(proxy)
                    print "returning %s"% result
                    self.server_logger.info("returning %s"% result)
                    return result
                except Exception, e:
                    print "Exception: ", str(e)
                    return ""
            #if it gets here, this means that we will execute on this instance
            if not os.path.exists(filepath):
                os.mkdir(filepath)

            if not os.path.exists(filename):
                locator = DBLocator(host=host,
                                    port=port,
                                    database=db_name,
                                    user=db_read_user,
                                    passwd=db_read_pass,
                                    obj_id=vt_id,
                                    obj_type=None,
                                    connection_id=None)
                (v, abstractions , thumbnails)  = io.load_vistrail(locator)
                controller = VistrailController()
                controller.set_vistrail(v, locator, abstractions, thumbnails)
                from gui.version_view import QVersionTreeView
                version_view = QVersionTreeView()
                version_view.scene().setupScene(controller)
                version_view.scene().saveToPNG(filename)
                del version_view
            else:
                print "Found cached image: ", filename
            return os.path.join(subdir,base_fname)
        except Exception, e:
            print "Error when saving png: ", str(e)
            
    def get_vt_zip(self, host, port, db_name, vt_id):
        """get_vt_zip(host:str, port: str, db_name: str, vt_id:str) -> str
        Returns a .vt file encoded as base64 string
        
        """
        self.server_logger.info("Request: get_vt_zip(%s,%s,%s,%s)"%(host,
                                                                 port,
                                                                 db_name,
                                                                 vt_id))
        try:
            locator = DBLocator(host=host,
                                port=int(port),
                                database=db_name,
                                user=db_read_user,
                                passwd=db_read_pass,
                                obj_id=int(vt_id),
                                obj_type=None,
                                connection_id=None)
            save_bundle = locator.load()
            #annotate the vistrail
            save_bundle.vistrail.update_checkout_version('vistrails')
            #create temporary file
            (fd, name) = tempfile.mkstemp(prefix='vt_tmp',
                                          suffix='.vt')
            os.close(fd)
            fileLocator = FileLocator(name)
            fileLocator.save(save_bundle)
            contents = open(name).read()
            result = base64.b64encode(contents)
            os.unlink(name)
            self.server_logger.info("SUCCESS!")
            return result
        except Exception, e:
            self.server_logger.info("Error: %s"%str(e))
            return "FAILURE: %s" %str(e)
        
    def get_wf_vt_zip(self, host, port, db_name, vt_id, version):
        """get_wf_vt_zip(host:str, port:str, db_name:str, vt_id:str,
                         version:str) -> str
        Returns a vt file containing the single workflow defined by version 
        encoded as base64 string
        
        """
        self.server_logger.info("Request: get_wf_vt_zip(%s,%s,%s,%s,%s)"%(host,
                                                                       port,
                                                                       db_name,
                                                                       vt_id,
                                                                       version))
        try:
            locator = DBLocator(host=host,
                                port=int(port),
                                database=db_name,
                                user=db_read_user,
                                passwd=db_read_pass,
                                obj_id=int(vt_id),
                                obj_type=None,
                                connection_id=None)
        
            (v, _ , _)  = io.load_vistrail(locator)
            p = v.getPipeline(long(version))
            if p:
                vistrail = Vistrail()
                action_list = []
                for module in p.module_list:
                    action_list.append(('add', module))
                for connection in p.connection_list:
                    action_list.append(('add', connection))
                action = core.db.action.create_action(action_list)
                vistrail.add_action(action, 0L)
                vistrail.addTag("Imported workflow", action.id)
                if not vistrail.db_version:
                    vistrail.db_version = currentVersion
                pipxmlstr = io.serialize(vistrail)
                result = base64.b64encode(pipxmlstr)
            else:
                result = "Error: Pipeline was not materialized"
                self.server_logger.info(result)
        except Exception, e:
            result = "Error: %s"%str(e)
            self.server_logger.info(result)
            
        return result

    def get_db_vt_list(self, host, port, db_name):
        self.server_logger.info("Request: get_db_vistrail_list(%s,%s,%s)"%(host,
                                                                 port,
                                                                 db_name))
        config = {}
        config['host'] = host
        config['port'] = int(port)
        config['db'] = db_name
        config['user'] = db_read_user
        config['passwd'] = db_read_pass
        try:
            rows = io.get_db_vistrail_list(config)
            return rows
        except Exception, e:
            self.server_logger.info("Error: %s"%str(e))
            print "Error: ", str(e)
            return "FAILURE: %s" %str(e)
        
    def get_db_vt_list_xml(self, host, port, db_name):
        self.server_logger.info("Request: get_db_vistrail_list(%s,%s,%s)"%(host,
                                                                 port,
                                                                 db_name))
        config = {}
        config['host'] = host
        config['port'] = int(port)
        config['db'] = db_name
        config['user'] = db_read_user
        config['passwd'] = db_read_pass
        try:
            rows = io.get_db_vistrail_list(config)
            result = '<vistrails>'
            for (id, name, mod_time) in rows:
                result += '<vistrail id="%s" name="%s" mod_time="%s" />'%(id,name,mod_time)
            result += '</vistrails>'
            return result
        except Exception, e:
            self.server_logger.info("Error: %s"%str(e))
            return "FAILURE: %s" %str(e)

    def get_vt_tagged_versions(self, host, port, db_name, vt_id):
        self.server_logger.info("Request: get_vt_tagged_versions(%s,%s,%s,%s)"%(host,
                                                                 port,
                                                                 db_name,
                                                                 vt_id))
        try:
            locator = DBLocator(host=host,
                                port=int(port),
                                database=db_name,
                                user=db_read_user,
                                passwd=db_read_pass,
                                obj_id=int(vt_id),
                                obj_type=None,
                                connection_id=None)

            result = []
            v = locator.load().vistrail
            for elem, tag in v.get_tagMap().iteritems():
                action_map = v.actionMap[long(elem)]
                if v.get_thumbnail(elem):
                    thumbnail_fname = os.path.join(
                        get_vistrails_configuration().thumbs.cacheDirectory,
                        v.get_thumbnail(elem))
                else:
                    thumbnail_fname = ""
                result.append({'id': elem, 'name': tag,
                               'notes': v.get_notes(elem) or '',
                               'user':action_map.user or '', 
                               'date':action_map.date,
                               'thumbnail': thumbnail_fname})
            self.server_logger.info("SUCCESS!")
            return result
        except Exception, e:
            self.server_logger.info("Error: %s"%str(e))
            return "FAILURE: %s" %str(e)

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
        if QtCore.QT_VERSION < 0x40200: # 0x40200 = 4.2.0
            raise core.requirements.MissingRequirement("Qt version >= 4.2")
        
        self.rpcserver = None
        self.images_url = "http://vistrails.sci.utah.edu/medleys/images/"
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
        self.start_other_instances(self.temp_xml_rpc_options.instances)
        self._python_environment = self.vistrailsStartup.get_python_environment()
        self._initialized = True
        return True

    def start_other_instances(self, number):
        self.others = []
        host = self.temp_xml_rpc_options.server
        port = self.temp_xml_rpc_options.port
        virtual_display = 5
        script = '/server/vistrails/trunk/scripts/start_vistrails_xvfb.sh'
        for x in xrange(number):
            port += 1
            virtual_display += 1
            args = [script,":%s"%virtual_display,host,str(port),'0', '0']
            try:
                p = subprocess.Popen(args)
                time.sleep(20)
                self.others.append("http://%s:%s"%(host,port))
            except Exception, e:
                debug.critical("Couldn't start the instance on display: %s port: %s" % (virtual_display, port)
                debug.critical("Exception: %s" % str(e))
                 
    def stop_other_instances(self): 
        script = '/server/vistrails/trunk/vistrails/stop_vistrails_server.py'
        for o in self.others:
            args = ['python', script, o]
            try:
                subprocess.Popen(args)
                time.sleep(15)
            except Exception, e:
                debug.critical("Couldn't stop instance: %s" % o)
                debug.critical("Exception: %s" % str(e))
                       
    def run_server(self):
        """run_server() -> None
        This will run forever until the server receives a quit request, done
        via xml-rpc.

        """
        if self.temp_xml_rpc_options.multithread:
            self.rpcserver = ThreadedXMLRPCServer((self.temp_xml_rpc_options.server,
                                                   self.temp_xml_rpc_options.port))
            debug.log("Server is running on http://%s:%s multithreaded"%
                      (self.temp_xml_rpc_options.server,
                       self.temp_xml_rpc_options.port))
        else:
            self.rpcserver = StoppableXMLRPCServer((self.temp_xml_rpc_options.server,
                                                   self.temp_xml_rpc_options.port))
            debug.log("Server is running on http://%s:%s singlethreaded"%
                      (self.temp_xml_rpc_options.server,
                       self.temp_xml_rpc_options.port))
        #self.rpcserver.register_introspection_functions()
        self.rpcserver.register_instance(RequestHandler(self.server_logger,
                                                        self.others))
        self.rpcserver.register_function(self.quit_server, "quit")
        self.server_logger.info("Vistrails XML RPC Server is listening on http://%s:%s"% \
                        (self.temp_xml_rpc_options.server,
                         self.temp_xml_rpc_options.port))
        self.rpcserver.serve_forever()
        self.rpcserver.server_close()
        return 0
    
    def quit_server(self):
        result = "Vistrails XML RPC Server is quitting."
        self.stop_other_instances()
        self.server_logger.info(result)
        self.rpcserver.stop = True
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
        add("-O", "--xml_rpc_instances", action="store", type='int', default=0,
            dest="rpcinstances",
            help="number of other instances that vistrails should start")
        add("-M", "--multithreaded", action="store_true",
            default = None, dest='multithread',
            help="server will start a thread for each request")
        VistrailsApplicationInterface.setupOptions(self)

    def readOptions(self):
        """ readOptions() -> None
        Read arguments from the command line

        """
        get = command_line.CommandLineParser().get_option
        self.temp_xml_rpc_options = InstanceObject(server=get('rpcserver'),
                                                   port=get('rpcport'),
                                                   log_file=get('rpclogfile'),
                                                   instances=get('rpcinstances'),
                                                   multithread=get('multithread'))
        VistrailsApplicationInterface.readOptions(self)

# The initialization must be explicitly signalled. Otherwise, any
# modules importing vis_application will try to initialize the entire
# app.
def start_server(optionsDict=None):
    """Initializes the application singleton."""
    global VistrailsServer
    if VistrailsServer:
        print "Server already started."
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

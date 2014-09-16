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
""" This is the application for vistrails when running as a server. """
import Queue
import base64
import hashlib
import inspect
import sys
import logging
import logging.handlers
import os
import re
import shutil
import subprocess
import tempfile
import time
import traceback
import urllib
import xmlrpclib
import ConfigParser

from PyQt4 import QtGui, QtCore
import SocketServer
from SimpleXMLRPCServer import SimpleXMLRPCServer
from datetime import date, datetime

from vistrails.core.configuration import get_vistrails_configuration
from vistrails.core.application import VistrailsApplicationInterface
import vistrails.gui.theme
import vistrails.core.application
from vistrails.gui import qt
from vistrails.core.db.locator import DBLocator, ZIPFileLocator, FileLocator
from vistrails.core.db import io
import vistrails.core.db.action

from vistrails.core.utils import InstanceObject
from vistrails.core.vistrail.vistrail import Vistrail
from vistrails.core import command_line
from vistrails.core import system
from vistrails.core.modules.module_registry import get_module_registry as module_registry
from vistrails.core import interpreter
from vistrails.core.packagemanager import get_package_manager
from vistrails.core.thumbnails import ThumbnailCache
import vistrails.db.services.io
import gc

import vistrails.core.requirements
import vistrails.core.console_mode

from vistrails.db.versions import currentVersion

ElementTree = system.get_elementtree_library()



################################################################################
class StoppableXMLRPCServer(SimpleXMLRPCServer):
    """This class allows a server to be stopped by a external request"""
    #accessList contains the list of ip addresses and hostnames that can send
    #request to this server. Change this according to your server
    global accessList

    allow_reuse_address = True
    def __init__(self, addr, logger):
        self.logger = logger
        SimpleXMLRPCServer.__init__(self, addr)

    def serve_forever(self):
        self.stop = False
        while not self.stop:
            self.handle_request()

    def verify_request(self, request, client_address):
        if client_address[0] in accessList:
            self.logger.info("Request from %s allowed!"%str(client_address))
            return 1
        else:
            self.logger.info("Request from %s denied!"%str(client_address))
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
                    self.server_logger.info("Instantiated client for %s" % uri)
                except Exception, e:
                    self.server_logger.error("Error when instantiating proxy %s" % uri)
                    self.server_logger.error(str(e))
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

    def try_ping(self):
        return 1

    #crowdlabs
    def get_wf_modules(self, host, port, db_name, vt_id, version):
        """get_wf_modules(host:str, port:int, db_name:str, vt_id:int,
                          version:int) -> (return_status, list of dict)
           Returns a list of information about the modules used in a workflow
           in a list of dictionaries. The dictionary has the following keys:
           name, package, documentation.
        """
        self.server_logger.info("Request: get_wf_modules(%s,%s,%s,%s,%s)" % \
                                (host, port, db_name, vt_id, version))
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
                    descriptor = module_registry().get_descriptor_by_name(
                            module.package,
                            module.name,
                            module.namespace)
                    documentation = descriptor.module_documentation(module)
                    result.append({'name':module.name,
                                              'package':module.package,
                                              'documentation':documentation})
                return (result, 1)
            else:
                result = "Pipeline was not materialized"
                self.server_logger.error(str(result))
        except xmlrpclib.ProtocolError, err:
            err_msg = ("A protocol error occurred\n"
                       "URL: %s\n"
                       "HTTP/HTTPS headers: %s\n"
                       "Error code: %d\n"
                       "Error message: %s\n") % (err.url, err.headers,
                                                 err.errcode, err.errmsg)
            self.server_logger.error(err_msg)
            return (str(err), 0)
        except Exception, e:
            result = str(e)
            self.server_logger.error(result)
            self.server_logger.error(traceback.format_exc())
        return (result, 0)

    def get_wf_mashups(self, host, port, db_name, vt_id, version):
        """get_wf_mashups(host:str, port:int, db_name:str, vt_id:int,
                          version:int) -> (return_status, list of dict)
           Returns a list of mashups in a workflow
           in a list of dictionaries. The dictionary has the following keys:
           name, package, documentation.
        """
        self.server_logger.info("Request: get_wf_mashups(%s,%s,%s,%s,%s)" % \
                                (host, port, db_name, vt_id, version))
        result = []
        try:
            locator = DBLocator(host=host,
                                port=int(port),
                                database=db_name,
                                user=db_read_user,
                                passwd=db_read_pass,
                                obj_id=int(vt_id),
                                obj_type=None,
                                connection_id=None)
            (vistrail, abstractions, thumbnails, mashups) = \
                                                      io.load_vistrail(locator)
            for mashuptrail in mashups:
                # Find tagged mashups for this version
                if mashuptrail.vtVersion == version:
                    for name, mashup_id in mashuptrail.getTagMap().iteritems():
                        if name != 'ROOT':
                            mashup = MedleySimpleGUI.from_mashup(
                                                 mashuptrail.getMashup(mashup_id))
                            result.append([name, ElementTree.tostring(mashup.to_xml())])
            return (result, 1)
        except xmlrpclib.ProtocolError, err:
            err_msg = ("A protocol error occurred\n"
                       "URL: %s\n"
                       "HTTP/HTTPS headers: %s\n"
                       "Error code: %d\n"
                       "Error message: %s\n") % (err.url, err.headers,
                                                 err.errcode, err.errmsg)
            self.server_logger.error(err_msg)
            return (str(err), 0)
        except Exception, e:
            result = str(e)
            self.server_logger.error(result)
            self.server_logger.error(traceback.format_exc())
        return (result, 0)

    def get_packages(self):
        """get_packages()-> dict
        This returns a dictionary with all the packages available in the
        VisTrails registry.
        The keys are the package identifier and for each identifier there's a
        dictionary with modules and description.
        """
        self.server_logger.info("Request: get_packages()")
        try:
            package_dic = {}

            for package in module_registry().package_list:
                package_dic[package.identifier] = {}
                package_dic[package.identifier]['modules'] = []
                for module in package._db_module_descriptors:
                    documentation = inspect.getdoc(module.module)
                    if documentation:
                        documentation = re.sub('^ *\n', '', documentation.rstrip())
                    else:
                        documentation = "(No documentation available)"
                    package_dic[package.identifier]['modules'].append({'name':module.name,
                                                                       'package':module.package,
                                                                       'documentation':documentation})
                package_dic[package.identifier]['description'] = \
                        package.description if package.description else "(No description available)"
            return (package_dic, 1)
        except xmlrpclib.ProtocolError, err:
            err_msg = ("A protocol error occurred\n"
                       "URL: %s\n"
                       "HTTP/HTTPS headers: %s\n"
                       "Error code: %d\n"
                       "Error message: %s\n") % (err.url, err.headers,
                                                 err.errcode, err.errmsg)
            self.server_logger.error(err_msg)
            return (str(err), 0)
        except Exception, e:
            self.server_logger.error(str(e))
            self.server_logger.error(traceback.format_exc())
            return (str(e), 0)

    def get_server_packages(self, codepath=None, status=None):
        """get_server_packages()-> dict
        This returns a dictionary with all the packages to vistrails with
        status indicating wether it is loaded.
        It is also possible to enable/disable a package by passing a package
        codepath and the desired status on/off
        The keys are the package identifier.
        """
        self.server_logger.info("Request: get_server_packages()")

        messages = []
        if self.proxies_queue is not None:
            # collect all proxies:
            proxies = []
            while len(proxies) < len(self.instances):
                self.server_logger.info("Proxies: %s Instances: %s" % (len(proxies), len(self.instances)))
                if self.proxies_queue.empty():
                    for p in  proxies:
                        self.proxies_queue.put(p)
                    return [[[],
                        "Not all vistrail instances are free, please try again."], 1]
                proxies.append(self.proxies_queue.get())
            for proxy in proxies:
                try:
                    if codepath and status is not None:
                        result, s = proxy.get_server_packages(codepath, status)
                    else:
                        result, s = proxy.get_server_packages()
                except xmlrpclib.ProtocolError, err:
                    err_msg = ("A protocol error occurred\n"
                           "URL: %s\n"
                           "HTTP/HTTPS headers: %s\n"
                           "Error code: %d\n"
                           "Error message: %s\n") % (err.url, err.headers,
                                                 err.errcode, err.errmsg)
                    self.server_logger.error(err_msg)
                finally:
                    self.proxies_queue.put(proxy)
                if s == 0:
                    messages.append('An error occurred: %s' % result)
                else:
                    messages.append(result[1])

        try:
            pkg_manager = get_package_manager()
            message = ''
            if codepath and status is not None:
                if int(status):
                    # Try to enable package
                    try:
                        pkg_manager.late_enable_package(codepath)
                        message = "Successfully enabled package '%s'" % codepath
                    except Exception, e:
                        message = "Could not enable package '%s': %s %s" % \
                                         (codepath, str(e), traceback.format_exc())
                else:
                    # Try to disable package
                    if codepath in ["basic_modules", 'abstraction']:
                        message = "Package '%s' cannot be disabled" % codepath
                    elif not pkg_manager.can_be_disabled(
                             pkg_manager.get_package_by_codepath(codepath).identifier):
                        message = "Package '%s' cannot be disabled because other packages depends on it." % codepath
                    else:
                        try:
                            pkg_manager.remove_package(codepath)
                            message = "Successfully disabled package '%s'" % codepath
                        except Exception, e:
                            message = "Could not disable package '%s': %s %s" % \
                                      (codepath, str(e), traceback.format_exc())
            packages = []
            enabled_pkgs = sorted(pkg_manager.enabled_package_list())
            enabled_pkg_dict = dict([(pkg.codepath, pkg) for
                                      pkg in enabled_pkgs])
            for pkg in sorted([pkg.codepath for pkg in enabled_pkgs]):
                packages.append([pkg, True])
            available_pkg_names = [pkg for pkg in 
                                   sorted(pkg_manager.available_package_names_list())
                                   if pkg not in enabled_pkg_dict]
            for pkg in available_pkg_names:
                packages.append([pkg, False])

            if codepath and messages:
                # we are the main instance so assemble messages
                message = ''.join(["Main instance: %s" % message] + \
                   ["<br/>Instance %s: %s" % (i+1, m) for i, m in
                                              zip(xrange(len(messages)), messages)])
            return [[packages, message], 1]
        except xmlrpclib.ProtocolError, err:
            err_msg = ("A protocol error occurred\n"
                       "URL: %s\n"
                       "HTTP/HTTPS headers: %s\n"
                       "Error code: %d\n"
                       "Error message: %s\n") % (err.url, err.headers,
                                                 err.errcode, err.errmsg)
            self.server_logger.error(err_msg)
            return (str(err), 0)
        except Exception, e:
            self.server_logger.error(str(e))
            self.server_logger.error(traceback.format_exc())
            return (str(e), 0)

    def add_vt_to_db(self, host, port, db_name, user, vt_filepath, filename,
                     repository_vt_id, repository_creator, is_local=True):
        """add_vt_to_db(host:str, port:int, db_name:str, user:str,
                        vt_filepath:str(or datastream), filename:str,
                        repository_vt_id:int, repository_creator:str) -> 
                        (return_status, int)
        This will add a vistrail in vt_filepath to the the database. If running
        on a remote machine, vt_filepath will contain vt file data stream.
        Before adding it it will annotate the vistrail with the 
        repository_vt_id and repository_creator.

        """
        try:
            if is_local:
                bundle = ZIPFileLocator(vt_filepath).load()
            else:
                # vt_filepath contains vt file datastream
                # write to tmp file, read into FileLocator
                # TODO: can we just read the file stream directly in?
                (fd, fname) = tempfile.mkstemp(prefix='vt_tmp',
                                              suffix='.vt')
                os.close(fd)
                try:
                    vt_file = open(fname, "wb")
                    vt_file.write(vt_filepath.data)
                    vt_file.close()
                    bundle = ZIPFileLocator(fname).load()
                finally:
                    os.unlink(fname)

            # set some crowdlabs id info
            if repository_vt_id != -1:
                vistrail = bundle.vistrail
                vistrail.set_annotation('repository_vt_id', repository_vt_id)
                vistrail.set_annotation('repository_creator', repository_creator)

            db_locator = DBLocator(host=host, port=int(port), database=db_name,
                                   name=filename, user=db_write_user, passwd=db_write_pass)
            db_locator.save_as(bundle)
            return (db_locator.obj_id, 1)

        except xmlrpclib.ProtocolError, err:
            err_msg = ("A protocol error occurred\n"
                       "URL: %s\n"
                       "HTTP/HTTPS headers: %s\n"
                       "Error code: %d\n"
                       "Error message: %s\n") % (err.url, err.headers,
                                                 err.errcode, err.errmsg)
            self.server_logger.error(err_msg)
            return (str(err), 0)
        except Exception, e:
            self.server_logger.error(str(e))
            self.server_logger.error(traceback.format_exc())
            return (str(e), 0)

    def merge_vt(self, host, port, db_name, user, new_vt_filepath,
                 old_db_vt_id, is_local=True):
        """
        Merge new_vt (new_vt_filepath) with current vt (old_db_vt_id)

        new_vt_filepath is either filepath to vt, or datastream of vt,
        depending on if the server is on a remote machine
        """
        self.server_logger.info("Request: merge_vt(%s,%s,%s,%s,%s,%s,%s)" % \
                                (host, port, db_name, user, new_vt_filepath,
                                 old_db_vt_id, is_local))
        try:
            tmp_file = None
            if is_local:
                new_locator = ZIPFileLocator(new_vt_filepath)
            else:
                # vt_filepath contains vt file datastream
                # write to tmp file, read into FileLocator
                # TODO: can we just read the file stream directly in?
                (fd, tmp_file) = tempfile.mkstemp(prefix='vt_tmp',
                                              suffix='.vt')
                os.close(fd)
                vt_file = open(tmp_file, "wb")
                vt_file.write(new_vt_filepath.data)
                vt_file.close()
                new_locator = ZIPFileLocator(tmp_file)

            new_bundle = new_locator.load()
            # add thumbnails to cache
            ThumbnailCache.getInstance()._copy_thumbnails(new_bundle.thumbnails)
            new_locator.save(new_bundle)
            old_db_locator = DBLocator(host=host, port=int(port), database=db_name,
                                       obj_id=int(old_db_vt_id), user=db_write_user, passwd=db_write_pass)
            old_db_bundle = old_db_locator.load()
            vistrails.db.services.vistrail.merge(old_db_bundle, new_bundle, 'vistrails')
            old_db_locator.save(old_db_bundle)
            new_locator.save(old_db_bundle)
            if tmp_file is not None:
                os.unlink(tmp_file)
            return (1, 1)
        except xmlrpclib.ProtocolError, err:
            err_msg = ("A protocol error occurred\n"
                       "URL: %s\n"
                       "HTTP/HTTPS headers: %s\n"
                       "Error code: %d\n"
                       "Error message: %s\n") % (err.url, err.headers,
                                                 err.errcode, err.errmsg)
            self.server_logger.error(err_msg)
            return (str(err), 0)
        except Exception, e:
            self.server_logger.error(str(e))
            self.server_logger.error(traceback.format_exc())
            return (str(e), 0)

    def remove_vt_from_db(self, host, port, db_name, user, vt_id):
        """remove_vt_from_db(host:str, port:int, db_name:str, user:str,
                             vt_id:int) -> (return_status, 0 or 1)
        Remove a vistrail from the repository
        """
        config = {}
        config['host'] = host
        config['port'] = int(port)
        config['db'] = db_name
        config['user'] = db_write_user
        config['passwd'] = db_write_pass
        try:
            conn = vistrails.db.services.io.open_db_connection(config)
            vistrails.db.services.io.delete_entity_from_db(conn,'vistrail', vt_id)
            vistrails.db.services.io.close_db_connection(conn)
            return (1, 1)
        except Exception, e:
            self.server_logger.error(str(e))
            if conn:
                vistrails.db.services.io.close_db_connection(conn)
            return (str(e), 0)

    def get_runnable_workflows(self, host, port, db_name, vt_id):
        try:
            locator = DBLocator(host=host,
                                port=int(port),
                                database=db_name,
                                user=db_read_user,
                                passwd=db_read_pass,
                                obj_id=int(vt_id),
                                obj_type=None,
                                connection_id=None)
            (vistrail, _, _, _)  = io.load_vistrail(locator)

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

            return ((runnable_workflows, py_source_workflows), 1)

        except xmlrpclib.ProtocolError, err:
            err_msg = ("A protocol error occurred\n"
                       "URL: %s\n"
                       "HTTP/HTTPS headers: %s\n"
                       "Error code: %d\n"
                       "Error message: %s\n") % (err.url, err.headers,
                                                 err.errcode, err.errmsg)
            self.server_logger.error(err_msg)
            return (str(err), 0)
        except Exception, e:
            self.server_logger.error(str(e))
            return (str(e), 0)

    #webgl
    def run_from_db_webgl(self, host, port, db_name, vt_id, path_to_figures,
                        version=None,  pdf=False, vt_tag='', build_always=False,
                        parameters='', is_local=True):
        # get vistrail
        locator = DBLocator(host=host,
                            port=int(port),
                            database=db_name,
                            user=db_read_user,
                            passwd=db_read_pass,
                            obj_id=int(vt_id),
                            obj_type=None,
                            connection_id=None)
        (vistrail, abstractions , thumbnails, mashups)  = io.load_vistrail(locator)
        from core.vistrail.controller import VistrailController as BaseController
        c = BaseController()
        c.set_vistrail(vistrail, locator, abstractions, thumbnails, mashups)

        # get server packages
        local_packages = [x.identifier for x in module_registry().package_list]
        version_id = 0
        version_tag = 0

        from db.domain import IdScope
        from core.vistrail.connection import Connection
        from core.vistrail.module import Module
        from core.vistrail.port import Port

        # get last pipeline
        workflow = False
        if (vt_tag == ''):
            version = vistrail.get_latest_version()#-1;
        else:
            version = int(vt_tag)

        c.change_selected_version(version)
        workflow = c.current_pipeline.__copy__()

        #id_scope = IdScope(version)
        id_scope = vistrail.idScope
        if workflow:
            # if doesnt have VTKWebView and vtkRenderer
            if ("vtkRenderer" not in [x.name for x in workflow.module_list]):
                return (str("Doesn't have vtkRenderer"), 1)

            # if already have VTKWebView, execute it
            if ("VTKWebView" not in [x.name for x in workflow.module_list]):
                # else, add VTKWebView to vtkRenderer and execute it
                renderer = workflow.module_list[[x.name for x in workflow.module_list].index('vtkRenderer')]

                action_list = []

                mWeb = Module(id=id_scope.getNewId(Module.vtType),
                           name='VTKWebView',
                           package='edu.utah.sci.vistrails.vtWebGL',
                           functions=[])
                mWeb.version = '0.0.2'
                workflow.add_module(mWeb);
                # create connection from render to web
                source = Port(id=id_scope.getNewId(Port.vtType),
                              type='source',
                              moduleId=renderer.id,
                              moduleName='vtkRenderer',
                              name='self',
                              signature='(edu.utah.sci.vistrails.vtk:vtkRenderer)')
                destination = Port(id=id_scope.getNewId(Port.vtType),
                                   type='destination',
                                   moduleId=mWeb.id,
                                   moduleName='VTKWebView',
                                   name='vtkrenderer',
                                   signature='(edu.utah.sci.vistrails.vtk:vtkRenderer)')
                c1 = Connection(id=id_scope.getNewId(Connection.vtType), ports=[source, destination])
                # add connection to action list.
                workflow.add_connection(c1)
                workflow.validate()

            c.current_pipeline = workflow;
            (results, x) = c.execute_current_workflow()
            if len(results[0].errors.values()) > 0:
                print "> ERROR: ", results[0].errors
                return (-1, str(results[0].errors.values()[0]))
            else: return (1, 1)

        return ("Doesnt have working workflow.", 1)

    #medleys
    
    def executeMedley(self, xml_medley, extra_info=None):
        self.server_logger.info("executeMedley request received")
        try:
            self.server_logger.info(xml_medley)
            xml_string = xml_medley.replace('\\"','"')
            root = ElementTree.fromstring(xml_string)
            try:
                medley = MedleySimpleGUI.from_xml(root)
            except Exception:
                #even if this error occurred there's still a chance of
                # recovering from it... (the server can find cached images)
                self.server_logger.error("couldn't instantiate medley")

            self.server_logger.debug("%s medley: %s"%(medley._type, medley._name))
            result = ""
            subdir = hashlib.sha224(xml_string).hexdigest()
            path_to_images = \
               os.path.join(media_dir, 'medleys/images', subdir)
            if (not self.path_exists_and_not_empty(path_to_images) and
                self.proxies_queue is not None):
                #this server can send requests to other instances
                proxy = self.proxies_queue.get()
                try:
                    self.server_logger.info("Sending request to %s" % proxy)
                    if extra_info is not None:
                        result = proxy.executeMedley(xml_medley, extra_info)
                    else:
                        result = proxy.executeMedley(xml_medley)
                    self.proxies_queue.put(proxy)
                    self.server_logger.info("returning %s"% result)
                    return result
                except Exception, e:
                    self.server_logger.error(str(e))
                    return (str(e), 0)

            if extra_info is None:
                extra_info = {}

            if extra_info.has_key('pathDumpCells'):
                if extra_info['pathDumpCells']:
                    extra_path = extra_info['pathDumpCells']
            else:
                extra_info['pathDumpCells'] = path_to_images

            if not self.path_exists_and_not_empty(extra_info['pathDumpCells']):
                if not os.path.exists(extra_info['pathDumpCells']):
                    os.mkdir(extra_info['pathDumpCells'])
                
                if medley._type == 'vistrail':
                    locator = DBLocator(host=db_host,
                                        port=3306,
                                        database='vistrails',
                                        user=db_write_user,
                                        passwd=db_write_pass,
                                        obj_id=medley._vtid,
                                        obj_type=None,
                                        connection_id=None)

                    extra_info['mashup_id'] = medley._id
                    workflow = medley._version
                    sequence = False
                    for (k,v) in medley._alias_list.iteritems():
                        if v._component._seq == True:
                            sequence = True
                            val = XMLObject.convert_from_str(v._component._minVal,
                                                             v._component._spec)
                            maxval = XMLObject.convert_from_str(v._component._maxVal,
                                                             v._component._spec)
                            #making sure the filenames are generated in order
                            mask = '%s'
                            if isinstance(maxval, (int, long)):
                                mask = '%0' + str(len(v._component._maxVal)) + 'd'

                            while val <= maxval:
                                s_alias = "%s=%s$&$" % (k,val)
                                for (k2,v2) in medley._alias_list.iteritems():
                                    if k2 != k and v2._component._val != '':
                                        s_alias += "%s=%s$&$" % (k2,v2._component._val)
                                if s_alias != '':
                                    s_alias = s_alias[:-3]
                                    self.server_logger.info("Aliases: %s" % s_alias)
                                try:
                                    gc.collect()
                                    results = \
                                      vistrails.core.console_mode.run_and_get_results( \
                                                    [(locator,int(workflow))],
                                                    s_alias,
                                                    update_vistrail=False,
                                                    extra_info=extra_info)
                                    self.server_logger.info("Memory usage: %s"% self.memory_usage())
                                    interpreter.cached.CachedInterpreter.flush()
                                except Exception, e:
                                    self.server_logger.error(str(e))
                                    return (str(e), 0)
                                ok = True
                                for r in results:
                                    (objs, errors, _) = (r.objects, r.errors, r.executed)
                                    for e in errors.itervalues():
                                        self.server_logger.error("Module failed: %s"% str(e))
                                    for i in objs.iterkeys():
                                        if errors.has_key(long(i)):
                                            ok = False
                                            result += str(errors[i])
                                if ok:
                                    self.server_logger.info("renaming files")
                                    for root, dirs, file_names in os.walk(extra_info['pathDumpCells']):
                                        break
                                    s = []
                                    for f in file_names:
                                        if f.lower().endswith(".png"):
                                            fmask = "%s_"+mask+"%s"
                                            os.renames(os.path.join(root,f),
                                                       os.path.join(root,"%s" % f[:-4],
                                                                    fmask% (f[:-4],val,f[-4:])))
                                if val < maxval:
                                    val += XMLObject.convert_from_str(v._component._stepSize,
                                                                      v._component._spec)
                                    if val > maxval:
                                        val = maxval
                                else:
                                    break

                    if not sequence:
                        s_alias = ''
                        for (k,v) in medley._alias_list.iteritems():
                            if v._component._val != '':
                                s_alias += "%s=%s$&$" % (k,v._component._val)
                        if s_alias != '':
                            s_alias = s_alias[:-3]
                            self.server_logger.info("Not sequence aliases: %s"% s_alias)
                        try:
                            results = \
                               vistrails.core.console_mode.run_and_get_results( \
                                                [(locator,int(workflow))],
                                                    s_alias,
                                                    extra_info=extra_info)
                        except Exception, e:
                            self.server_logger.error(str(e))
                            return (str(e), 0)
                        ok = True
                        for r in results:
                            (objs, errors, _) = (r.objects, r.errors, r.executed)
                            for e in errors.itervalues():
                                self.server_logger.error(str(e))
                            for i in objs.iterkeys():
                                if errors.has_key(long(i)):
                                    ok = False
                                    result += str(errors[i])

                    self.server_logger.info( "success?  %s"% ok)

                elif medley._type == 'visit':
                    cur_dir = os.getcwd()
                    os.chdir(self.temp_configuration.outputDirectory)
                    if medley._id == 6:
                        session_file = 'crotamine.session'
                    elif medley._id == 7:
                        session_file = '1NTS.session'
                    else:
                        session_file = 'head.session'
                    session_file = '/server/code/visit/saved_sessions/' + session_file
                    self.server_logger.info("session_file: %s" % session_file)
                    ok = os.system('/server/code/visit/vistrails_plugin/visit/render-session.sh ' + \
                                   session_file) == 0
                    self.server_logger.info( "success?  %s" % ok)
                    os.chdir(cur_dir)
            else:
                self.server_logger.info("Found cached images.")
                ok = True

            if ok:
                s = []
                self.server_logger.info("images path: %s"%extra_info['pathDumpCells'])
                for root, dirs, file_names in os.walk(extra_info['pathDumpCells']):
                    sub = []
                    #n = len(file_names)
                    #print "%s file(s) generated" % n
                    file_names.sort()
                    for f in file_names:
                        sub.append(os.path.join(root[root.find(subdir):],
                                              f))
                    if len(sub):
                        s.append(";".join(sub))
                result = ":::".join(s)
                # FIXME: copy images to extra_path
            self.server_logger.info("returning %s" % result)
            return (result, 1)
        except xmlrpclib.ProtocolError, err:
            err_msg = ("A protocol error occurred\n"
                       "URL: %s\n"
                       "HTTP/HTTPS headers: %s\n"
                       "Error code: %d\n"
                       "Error message: %s\n") % (err.url, err.headers,
                                                 err.errcode, err.errmsg)
            self.server_logger.error(err_msg)
            return (str(err), 0)
        except Exception, e:
            self.server_logger.error(str(e))
            return (str(e), 0)

    #vistrails
    def run_from_db(self, host, port, db_name, vt_id, path_to_figures,
                    version=None,  pdf=False, vt_tag='', build_always=False,
                    parameters='', is_local=True):
        self.server_logger.info("Request: run_vistrail_from_db(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)" % \
                                (host, port, db_name, vt_id,
                                 path_to_figures, version, pdf,
                                 vt_tag, build_always, parameters, is_local))

        self.server_logger.info("path_exists_and_not_empty? %s" % self.path_exists_and_not_empty(path_to_figures))
        self.server_logger.info("build_always? %s" % build_always)
        self.server_logger.info(str(self.proxies_queue))

        if not is_local:
            # use same hashing as on crowdlabs webserver
            dest_version = "%s_%s_%d_%d_%d" % (host, db_name, int(port), int(vt_id), int(version))
            dest_version = hashlib.sha1(dest_version).hexdigest()
            path_to_figures = os.path.join(media_dir, "photos", "wf_execution", dest_version)

        if ((not self.path_exists_and_not_empty(path_to_figures) or 
             build_always) and self.proxies_queue is not None):
            self.server_logger.info("will forward request")
            #this server can send requests to other instances
            proxy = self.proxies_queue.get()
            try:
                self.server_logger.info("Sending request to %s" % proxy)
                result = proxy.run_from_db(host, port, db_name, vt_id,
                                           path_to_figures, version, pdf, vt_tag,
                                           build_always, parameters, is_local)
                self.proxies_queue.put(proxy)
                self.server_logger.info("returning %s" % result)
                return result
            except xmlrpclib.ProtocolError, err:
                    err_msg = ("A protocol error occurred\n"
                               "URL: %s\n"
                               "HTTP/HTTPS headers: %s\n"
                               "Error code: %d\n"
                               "Error message: %s\n") % (err.url, err.headers,
                                                         err.errcode, err.errmsg)
                    self.server_logger.error(err_msg)
                    return (str(err), 0)
            except Exception, e:
                self.server_logger.error(str(e))
                return (str(e), 0)

        extra_info = {}
        extra_info['pathDumpCells'] = path_to_figures
        self.server_logger.debug(path_to_figures)
        # TODO: really want to push this into spreadsheet settings,
        # perhaps the issue here is getting global access to package
        # configuration?
        extra_info['pdf'] = pdf
        self.server_logger.debug("pdf: %s" % pdf)
        # execute workflow
        ok = True
        if (not self.path_exists_and_not_empty(extra_info['pathDumpCells'])
            or build_always):
            if os.path.exists(extra_info['pathDumpCells']):
                shutil.rmtree(extra_info['pathDumpCells'])
            os.mkdir(extra_info['pathDumpCells'])

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
                self.server_logger.info("run_and_get_results(%s,%s,%s,%s,%s)" % \
                            (locator, version, parameters, True, extra_info))
                try:
                    results = \
                    vistrails.core.console_mode.run_and_get_results([(locator,
                                                          int(version))],
                                                          parameters,
                                                          update_vistrail=True,
                                                          extra_info=extra_info,
                                                          reason="Server Pipeline Execution")
                except Exception, e:
                    self.server_logger.error("workflow execution failed:")
                    self.server_logger.error(str(e))
                    self.server_logger.error(traceback.format_exc())
                    return (str(e), 0)
                ok = True

                for r in results:
                    (objs, errors, _) = (r.objects, r.errors, r.executed)

                    for i in objs.iterkeys():
                        if errors.has_key(i):
                            ok = False
                            result += str(errors[i])
            except Exception, e:
                self.server_logger.error(str(e))
                self.server_logger.error(traceback.format_exc())
                return (str(e), 0)

        if ok:
            if is_local:
                return (1, 1)
            else:
                # TODO pdf version
                images = [im for im in os.listdir(path_to_figures) if im[-3:] == "png"]
                results = {}
                for image in images:
                    handler = open(os.path.join(path_to_figures, image), "rb")
                    image_data = handler.read()
                    handler.close()
                    results[image] = xmlrpclib.Binary(image_data)
                return (results, 1)
        else:
            self.server_logger.error(result)
            return (result, 0)

    def get_package_list(self):
        """ get_package_list() -> str
         Returns a list of supported packages identifiers delimited by || """
        self.server_logger.info("Request: get_package_list()")
        try:
            packages = [x.identifier for x in module_registry().package_list]
            return (packages, 1)
        except xmlrpclib.ProtocolError, err:
            err_msg = ("A protocol error occurred\n"
                       "URL: %s\n"
                       "HTTP/HTTPS headers: %s\n"
                       "Error code: %d\n"
                       "Error message: %s\n") % (err.url, err.headers,
                                                 err.errcode, err.errmsg)
            self.server_logger.error(err_msg)
            return (str(err), 0)
        except Exception, e:
            self.server_logger.error(str(e))
            self.server_logger.error(traceback.format_exc())
            return (str(e), 0)

    def get_wf_datasets(self, host, port, db_name, vt_id, version):
        self.server_logger.info("Request: get_wf_datasets(%s,%s,%s,%s,%s)" % \
                                (host, port, db_name, vt_id, version))
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
                return (result, 1)
            else:
                result = "Pipeline was not materialized"
                self.server_logger.error(result)
        except xmlrpclib.ProtocolError, err:
            err_msg = ("A protocol error occurred\n"
                       "URL: %s\n"
                       "HTTP/HTTPS headers: %s\n"
                       "Error code: %d\n"
                       "Error message: %s\n") % (err.url, err.headers,
                                                 err.errcode, err.errmsg)
            self.server_logger.error(err_msg)
            return (str(err), 0)
        except Exception, e:
            result = str(e)
            self.server_logger.error(result)
            self.server_logger.error(traceback.format_exc())
        return (result, 0)

    def get_tag_version(self, host, port, db_name, vt_id, vt_tag):
        self.server_logger.info("Request: get_tag_version(%s,%s,%s,%s,%s)" % \
                                (host, port, db_name, vt_id, vt_tag))
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

            (v, _ , _, _)  = io.load_vistrail(locator)
            if v.has_tag_str(vt_tag):
                version = v.get_tag_str(vt_tag).action_id
            self.server_logger.info("Answer: %s" % version)
            return (version, 1)

        except xmlrpclib.ProtocolError, err:
            err_msg = ("A protocol error occurred\n"
                       "URL: %s\n"
                       "HTTP/HTTPS headers: %s\n"
                       "Error code: %d\n"
                       "Error message: %s\n") % (err.url, err.headers,
                                                 err.errcode, err.errmsg)
            self.server_logger.error(err_msg)
            return (str(err), 0)
        except Exception, e:
            self.server_logger.error(str(e))
            self.server_logger.error(traceback.format_exc())
            return (str(e), 0)


    def get_vt_xml(self, host, port, db_name, vt_id):
        self.server_logger.info("Request: get_vt_xml(%s,%s,%s,%s)" % \
                                (host, port, db_name, vt_id))
        try:
            locator = DBLocator(host=host,
                                port=int(port),
                                database=db_name,
                                user=db_read_user,
                                passwd=db_read_pass,
                                obj_id=int(vt_id),
                                obj_type=None,
                                connection_id=None)

            (v, _ , _, _)  = io.load_vistrail(locator)
            result = io.serialize(v)
            return (result, 1)
        except xmlrpclib.ProtocolError, err:
            err_msg = ("A protocol error occurred\n"
                       "URL: %s\n"
                       "HTTP/HTTPS headers: %s\n"
                       "Error code: %d\n"
                       "Error message: %s\n") % (err.url, err.headers,
                                                 err.errcode, err.errmsg)
            self.server_logger.error(err_msg)
            return (str(err), 0)
        except Exception, e:
            self.server_logger.error(str(e))
            self.server_logger.error(traceback.format_exc())
            return (str(e), 0)

    def get_wf_xml(self, host, port, db_name, vt_id, version):
        self.server_logger.info("Request: get_wf_xml(%s,%s,%s,%s,%s)" % \
                                (host, port, db_name, vt_id, version))
        try:
            locator = DBLocator(host=host,
                                port=int(port),
                                database=db_name,
                                user=db_read_user,
                                passwd=db_read_pass,
                                obj_id=int(vt_id),
                                obj_type=None,
                                connection_id=None)

            (v, _ , _, _)  = io.load_vistrail(locator)
            p = v.getPipeline(long(version))
            if p:
                result = io.serialize(p)
                self.server_logger.info("success")
                return (result, 1)
            else:
                result = "Pipeline was not materialized"
                self.server_logger.info(result)
        except xmlrpclib.ProtocolError, err:
            err_msg = ("A protocol error occurred\n"
                       "URL: %s\n"
                       "HTTP/HTTPS headers: %s\n"
                       "Error code: %d\n"
                       "Error message: %s\n") % (err.url, err.headers,
                                                 err.errcode, err.errmsg)
            self.server_logger.error(err_msg)
            return (str(err), 0)
        except Exception, e:
            result = str(e)
            self.server_logger.error(result)
            self.server_logger.error(traceback.format_exc())
        return (result, 0)

    def get_wf_graph_pdf(self, host, port, db_name, vt_id, version, is_local=True):
        """get_wf_graph_pdf(host:str, port:int, db_name:str, vt_id:int,
                          version:int) -> str
         Returns the relative url to the generated PDF
         """
        self.server_logger.info("get_wf_graph_pdf(%s,%s,%s,%s,%s) request received" % \
                                (host, port, db_name, vt_id, version))
        try:
            vt_id = long(vt_id)
            version = long(version)
            subdir = 'workflows'
            filepath = os.path.join(media_dir, 'graphs', subdir)
            base_fname = "graph_%s_%s.pdf" % (vt_id, version)
            filename = os.path.join(filepath,base_fname)
            if ((not os.path.exists(filepath) or
                os.path.exists(filepath) and not os.path.exists(filename))
                and self.proxies_queue is not None):
                #this server can send requests to other instances
                proxy = self.proxies_queue.get()
                try:
                    result = proxy.get_wf_graph_pdf(host,port,db_name, vt_id, version, is_local)
                    self.proxies_queue.put(proxy)
                    self.server_logger.info("get_wf_graph_pdf returning %s"% result)
                    return result
                except xmlrpclib.ProtocolError, err:
                    err_msg = ("A protocol error occurred\n"
                               "URL: %s\n"
                               "HTTP/HTTPS headers: %s\n"
                               "Error code: %d\n"
                               "Error message: %s\n") % (err.url, err.headers,
                                                         err.errcode, err.errmsg)
                    self.server_logger.error(err_msg)
                    return (str(err), 0)
                except Exception, e:
                    self.server_logger.error(str(e))
                    self.server_logger.error(traceback.format_exc())
                    return (str(e), 0)

            if not os.path.exists(filepath):
                os.mkdir(filepath)

            if not os.path.exists(filename):
                from vistrails.gui.vistrail_controller import VistrailController

                locator = DBLocator(host=host,
                                    port=int(port),
                                    database=db_name,
                                    user=db_read_user,
                                    passwd=db_read_pass,
                                    obj_id=int(vt_id),
                                    obj_type=None,
                                    connection_id=None)

                (v, abstractions , thumbnails, mashups)  = io.load_vistrail(locator)
                controller = VistrailController(v, locator, abstractions, 
                                                thumbnails, mashups)
                controller.change_selected_version(version)
                controller.updatePipelineScene()
                controller.current_pipeline_scene.saveToPDF(filename)
            else:
                self.server_logger.info("found cached pdf: %s" % filename)

            if is_local:
                return (os.path.join(subdir,base_fname), 1)
            else:
                f = open(filename, 'rb')
                contents = f.read()
                f.close()
                return (xmlrpclib.Binary(contents), 1)

        except xmlrpclib.ProtocolError, err:
            err_msg = ("A protocol error occurred\n"
                       "URL: %s\n"
                       "HTTP/HTTPS headers: %s\n"
                       "Error code: %d\n"
                       "Error message: %s\n") % (err.url, err.headers,
                                                 err.errcode, err.errmsg)
            self.server_logger.error(err_msg)
            return (str(err), 0)
        except Exception, e:
            self.server_logger.error("Error when saving pdf: %s" % str(e))
            self.server_logger.error(traceback.format_exc())
            return (str(e), 0)

    def get_wf_graph_png(self, host, port, db_name, vt_id, version, is_local=True):
        """get_wf_graph_png(host:str, port:int, db_name:str, vt_id:int,
                          version:int) -> str
         Returns the relative url to the generated image
         """
        self.server_logger.info("get_wf_graph_png(%s,%s,%s,%s,%s) request received" % \
                                (host, port, db_name, vt_id, version))
        try:
            vt_id = long(vt_id)
            version = long(version)
            subdir = 'workflows'
            filepath = os.path.join(media_dir, 'graphs', subdir)
            base_fname = "graph_%s_%s.png" % (vt_id, version)
            filename = os.path.join(filepath,base_fname)
            if ((not os.path.exists(filepath) or
                os.path.exists(filepath) and not os.path.exists(filename))
                and self.proxies_queue is not None):
                #this server can send requests to other instances
                proxy = self.proxies_queue.get()
                try:
                    self.server_logger.info("Sending request to %s" % proxy)
                    result = proxy.get_wf_graph_png(host, port, db_name, vt_id, version, is_local)
                    self.proxies_queue.put(proxy)
                    self.server_logger.info("returning %s" % result)
                    return result
                except xmlrpclib.ProtocolError, err:
                    err_msg = ("A protocol error occurred\n"
                               "URL: %s\n"
                               "HTTP/HTTPS headers: %s\n"
                               "Error code: %d\n"
                               "Error message: %s\n") % (err.url, err.headers,
                                                         err.errcode, err.errmsg)
                    self.server_logger.error(err_msg)
                    return (str(err), 0)
                except Exception, e:
                    self.server_logger.error(str(e))
                    self.server_logger.error(traceback.format_exc())
                    return (str(e), 0)
            #if it gets here, this means that we will execute on this instance
            if not os.path.exists(filepath):
                os.mkdir(filepath)

            if not os.path.exists(filename):
                from vistrails.gui.vistrail_controller import VistrailController

                locator = DBLocator(host=host,
                                    port=port,
                                    database=db_name,
                                    user=db_read_user,
                                    passwd=db_read_pass,
                                    obj_id=int(vt_id),
                                    obj_type=None,
                                    connection_id=None)
                (v, abstractions , thumbnails, mashups)  = io.load_vistrail(locator)
                controller = VistrailController(v, locator, abstractions, 
                                                thumbnails, mashups)
                controller.change_selected_version(version)
                controller.updatePipelineScene()
                controller.current_pipeline_scene.saveToPNG(filename)
            else:
                self.server_logger.info("found cached image: %s" % filename)
            if is_local:
                return (os.path.join(subdir,base_fname), 1)
            else:
                f = open(filename, 'rb')
                contents = f.read()
                f.close()
                return (xmlrpclib.Binary(contents), 1)
        except xmlrpclib.ProtocolError, err:
            err_msg = ("A protocol error occurred\n"
                       "URL: %s\n"
                       "HTTP/HTTPS headers: %s\n"
                       "Error code: %d\n"
                       "Error message: %s\n") % (err.url, err.headers,
                                                 err.errcode, err.errmsg)
            self.server_logger.error(err_msg)
            return (str(err), 0)
        except Exception, e:
            self.server_logger.error("Error when saving png %s" % str(e))
            self.server_logger.error(traceback.format_exc())
            return (str(e), 0)

    def _is_image_stale(self, filename, host, port, db_name, vt_id):
        statinfo = os.stat(filename)
        image_time = datetime.fromtimestamp(statinfo.st_mtime)
        locator = DBLocator(host=host,
                            port=int(port),
                            database=db_name,
                            user=db_read_user,
                            passwd=db_read_pass,
                            obj_id=int(vt_id),
                            obj_type=None,
                            connection_id=None)
        vt_mod_time = locator.get_db_modification_time()
        self.server_logger.info("image time: %s, vt time: %s"%(image_time,
                                                               vt_mod_time))
        if image_time < vt_mod_time:
            return True
        else:
            return False

    def get_vt_graph_png(self, host, port, db_name, vt_id, is_local=True):
        """get_vt_graph_png(host:str, port: str, db_name: str, vt_id:str) -> str
        Returns the relative url of the generated image
        """
        
        self.server_logger.info("get_vt_graph_png(%s, %s, %s, %s)" % (host, port, db_name, vt_id))
        try:
            vt_id = long(vt_id)
            subdir = 'vistrails'
            filepath = os.path.join(media_dir, 'graphs', subdir)
            base_fname = "graph_%s.png" % (vt_id)
            filename = os.path.join(filepath,base_fname)
            if ((not os.path.exists(filepath) or
                (os.path.exists(filepath) and not os.path.exists(filename)) or
                 self._is_image_stale(filename, host, port, db_name, vt_id)) and 
                self.proxies_queue is not None):
                #this server can send requests to other instances
                proxy = self.proxies_queue.get()
                try:
                    self.server_logger.info("Sending request to %s" % proxy)
                    result = proxy.get_vt_graph_png(host, port, db_name, vt_id, is_local)
                    self.proxies_queue.put(proxy)
                    self.server_logger.info("returning %s" % result)
                    return result
                except xmlrpclib.ProtocolError, err:
                    err_msg = ("A protocol error occurred\n"
                               "URL: %s\n"
                               "HTTP/HTTPS headers: %s\n"
                               "Error code: %d\n"
                               "Error message: %s\n") % (err.url, err.headers,
                                                         err.errcode, err.errmsg)
                    self.server_logger.error(err_msg)
                    return (str(err), 0)
                except Exception, e:
                    self.server_logger.error(str(e))
                    self.server_logger.error(traceback.format_exc())
                    return (str(e), 0)

            #if it gets here, this means that we will execute on this instance
            if (not os.path.exists(filepath) or
                (os.path.exists(filepath) and not os.path.exists(filename)) or
                 self._is_image_stale(filename, host, port, db_name, vt_id)):

                from vistrails.gui.vistrail_controller import VistrailController

                if os.path.exists(filepath):
                    shutil.rmtree(filepath)

                os.mkdir(filepath)
            
                locator = DBLocator(host=host,
                                    port=int(port),
                                    database=db_name,
                                    user=db_read_user,
                                    passwd=db_read_pass,
                                    obj_id=int(vt_id),
                                    obj_type=None,
                                    connection_id=None)
                (v, abstractions , thumbnails, mashups)  = io.load_vistrail(locator)
                controller = VistrailController(v, locator, abstractions, 
                                                thumbnails, mashups)
                from vistrails.gui.version_view import QVersionTreeView
                version_view = QVersionTreeView()
                version_view.scene().setupScene(controller)
                version_view.scene().saveToPNG(filename)
                del version_view
            else:
                self.server_logger.info("Found cached image: %s" % filename)
            if is_local:
                return (os.path.join(subdir,base_fname), 1)
            else:
                f = open(filename, 'rb')
                contents = f.read()
                f.close()
                return (xmlrpclib.Binary(contents), 1)
        except xmlrpclib.ProtocolError, err:
            err_msg = ("A protocol error occurred\n"
                       "URL: %s\n"
                       "HTTP/HTTPS headers: %s\n"
                       "Error code: %d\n"
                       "Error message: %s\n") % (err.url, err.headers,
                                                 err.errcode, err.errmsg)
            self.server_logger.error(err_msg)
            return (str(err), 0)
        except Exception, e:
            self.server_logger.error("Error when saving png: %s" % str(e))
            self.server_logger.error(traceback.format_exc())
            return (str(e), 0)

    def get_vt_graph_pdf(self, host, port, db_name, vt_id, is_local=True):
        """get_vt_graph_pdf(host:str, port: str, db_name: str, vt_id:str) -> str
        Returns the relative url of the generated image
        """

        self.server_logger.info("get_vt_graph_pdf(%s, %s, %s, %s)" % (host, port, db_name, vt_id))
        try:
            vt_id = long(vt_id)
            subdir = 'vistrails'
            filepath = os.path.join(media_dir, 'graphs', subdir)
            base_fname = "graph_%s.pdf" % (vt_id)
            filename = os.path.join(filepath,base_fname)
            if ((not os.path.exists(filepath) or
                (os.path.exists(filepath) and not os.path.exists(filename)) or
                 self._is_image_stale(filename, host, port, db_name, vt_id)) and 
                self.proxies_queue is not None):
                #this server can send requests to other instances
                proxy = self.proxies_queue.get()
                try:
                    self.server_logger.info("Sending request to %s" % proxy)
                    result = proxy.get_vt_graph_pdf(host, port, db_name, vt_id, is_local)
                    self.proxies_queue.put(proxy)
                    self.server_logger.info("returning %s" % result)
                    return result
                except xmlrpclib.ProtocolError, err:
                    err_msg = ("A protocol error occurred\n"
                               "URL: %s\n"
                               "HTTP/HTTPS headers: %s\n"
                               "Error code: %d\n"
                               "Error message: %s\n") % (err.url, err.headers,
                                                         err.errcode, err.errmsg)
                    self.server_logger.error(err_msg)
                    return (str(err), 0)
                except Exception, e:
                    self.server_logger.error(str(e))
                    self.server_logger.error(traceback.format_exc())
                    return (str(e), 0)


            #if it gets here, this means that we will execute on this instance
            if (not os.path.exists(filepath) or
                (os.path.exists(filepath) and not os.path.exists(filename)) or
                 self._is_image_stale(filename, host, port, db_name, vt_id)):

                from vistrails.gui.vistrail_controller import VistrailController

                if os.path.exists(filepath):
                    shutil.rmtree(filepath)

                os.mkdir(filepath)

                locator = DBLocator(host=host,
                                    port=int(port),
                                    database=db_name,
                                    user=db_read_user,
                                    passwd=db_read_pass,
                                    obj_id=int(vt_id),
                                    obj_type=None,
                                    connection_id=None)
                (v, abstractions , thumbnails, mashups)  = io.load_vistrail(locator)
                controller = VistrailController(v, locator, abstractions, 
                                                thumbnails, mashups)
                from vistrails.gui.version_view import QVersionTreeView
                version_view = QVersionTreeView()
                version_view.scene().setupScene(controller)
                version_view.scene().saveToPDF(filename)
                del version_view
            else:
                self.server_logger.info("Found cached pdf: %s" % filename)
            if is_local:
                return (os.path.join(subdir,base_fname), 1)
            else:
                f = open(filename, 'rb')
                contents = f.read()
                f.close()
                return (xmlrpclib.Binary(contents), 1)
        except xmlrpclib.ProtocolError, err:
            err_msg = ("A protocol error occurred\n"
                       "URL: %s\n"
                       "HTTP/HTTPS headers: %s\n"
                       "Error code: %d\n"
                       "Error message: %s\n") % (err.url, err.headers,
                                                 err.errcode, err.errmsg)
            self.server_logger.error(err_msg)
            return (str(err), 0)
        except Exception, e:
            self.server_logger.error("Error when saving pdf: %s" % str(e))
            self.server_logger.error(traceback.format_exc())
            return (str(e), 0)
        
    def get_vt_zip(self, host, port, db_name, vt_id):
        """get_vt_zip(host:str, port: str, db_name: str, vt_id:str) -> str
        Returns a .vt file encoded as base64 string
        """

        self.server_logger.info("Request: get_vt_zip(%s,%s,%s,%s)" % \
                                (host, port, db_name, vt_id))
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
            try:
                fileLocator = FileLocator(name)
                fileLocator.save(save_bundle)
                contents = open(name).read()
                result = base64.b64encode(contents)
            finally:
                os.unlink(name)
            return (result, 1)
        except xmlrpclib.ProtocolError, err:
            err_msg = ("A protocol error occurred\n"
                       "URL: %s\n"
                       "HTTP/HTTPS headers: %s\n"
                       "Error code: %d\n"
                       "Error message: %s\n") % (err.url, err.headers,
                                                 err.errcode, err.errmsg)
            self.server_logger.error(err_msg)
            return (str(err), 0)
        except Exception, e:
            self.server_logger.error(str(e))
            self.server_logger.error(traceback.format_exc())
            return (str(e), 0)

    def get_wf_vt_zip(self, host, port, db_name, vt_id, version):
        """get_wf_vt_zip(host:str, port:str, db_name:str, vt_id:str,
                         version:str) -> str
        Returns a vt file containing the single workflow defined by version
        encoded as base64 string

        """
        self.server_logger.info("Request: get_wf_vt_zip(%s,%s,%s,%s,%s)" % \
                                (host, port, db_name, vt_id, version))
        try:
            locator = DBLocator(host=host,
                                port=int(port),
                                database=db_name,
                                user=db_read_user,
                                passwd=db_read_pass,
                                obj_id=int(vt_id),
                                obj_type=None,
                                connection_id=None)

            (v, _ , _, _)  = io.load_vistrail(locator)
            p = v.getPipeline(long(version))
            if p:
                vistrail = Vistrail()
                action_list = []
                for module in p.module_list:
                    action_list.append(('add', module))
                for connection in p.connection_list:
                    action_list.append(('add', connection))
                action = vistrails.core.db.action.create_action(action_list)
                vistrail.add_action(action, 0L)
                vistrail.addTag("Imported workflow", action.id)
                if not vistrail.db_version:
                    vistrail.db_version = currentVersion
                pipxmlstr = io.serialize(vistrail)
                result = base64.b64encode(pipxmlstr)
                return (result, 1)
            else:
                result = "Error: Pipeline was not materialized"
                self.server_logger.info(result)
                return (result, 0)
        except xmlrpclib.ProtocolError, err:
            err_msg = ("A protocol error occurred\n"
                       "URL: %s\n"
                       "HTTP/HTTPS headers: %s\n"
                       "Error code: %d\n"
                       "Error message: %s\n") % (err.url, err.headers,
                                                 err.errcode, err.errmsg)
            self.server_logger.error(err_msg)
            return (str(err), 0)
        except Exception, e:
            self.server_logger.info(str(e))
            self.server_logger.error(traceback.format_exc())
            return (str(e), 0)

    def get_db_vt_list(self, host, port, db_name):
        self.server_logger.info("Request: get_db_vistrail_list(%s,%s,%s)" % \
                                (host, port, db_name))
        config = {}
        config['host'] = host
        config['port'] = int(port)
        config['db'] = db_name
        config['user'] = db_read_user
        config['passwd'] = db_read_pass
        try:
            rows = io.get_db_vistrail_list(config)
            self.server_logger.info("returning %s" % str(rows))
            return (rows, 1)
        except xmlrpclib.ProtocolError, err:
            err_msg = ("A protocol error occurred\n"
                       "URL: %s\n"
                       "HTTP/HTTPS headers: %s\n"
                       "Error code: %d\n"
                       "Error message: %s\n") % (err.url, err.headers,
                                                 err.errcode, err.errmsg)
            self.server_logger.error(err_msg)
            return (str(err), 0)
        except Exception, e:
            self.server_logger.error(str(e))
            return (str(e), 0)

    def get_db_vt_list_xml(self, host, port, db_name):
        self.server_logger.info("Request: get_db_vistrail_list(%s,%s,%s)" % \
                                (host, port, db_name))
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
            return (result, 1)
        except xmlrpclib.ProtocolError, err:
            err_msg = ("A protocol error occurred\n"
                       "URL: %s\n"
                       "HTTP/HTTPS headers: %s\n"
                       "Error code: %d\n"
                       "Error message: %s\n") % (err.url, err.headers,
                                                 err.errcode, err.errmsg)
            self.server_logger.error(err_msg)
            return (str(err), 0)
        except Exception, e:
            self.server_logger.error(str(e))
            self.server_logger.error(traceback.format_exc())
            return (str(e), 0)

    def get_vt_tagged_versions(self, host, port, db_name, vt_id, is_local=True):
        self.server_logger.info("Request: get_vt_tagged_versions(%s,%s,%s,%s,%s)" % \
                                (host, port, db_name, vt_id, is_local))
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
                thumbnail_fname = ""
                if v.get_thumbnail(elem):
                    thumbnail_dir = system.get_vistrails_directory(
                        "thumbs.cacheDir")
                    if thumbnail_dir is not None:
                        thumbnail_fname = os.path.join(thumbnail_dir,
                                                       v.get_thumbnail(elem))
                if not thumbnail_fname or is_local:
                    result.append({'id': elem, 'name': tag,
                                   'notes': v.get_notes(elem) or '',
                                   'user':action_map.user or '',
                                   'date':action_map.date,
                                   'thumbnail': thumbnail_fname})
                else:
                    handler = open(thumbnail_fname, "rb")
                    thumbnail_data = handler.read()
                    handler.close()
                    result.append({'id': elem, 'name': tag,
                                   'notes': v.get_notes(elem) or '',
                                   'user':action_map.user or '',
                                   'date':action_map.date,
                                   'thumbnail': xmlrpclib.Binary(thumbnail_data)})
            return (result, 1)
        except xmlrpclib.ProtocolError, err:
            err_msg = ("A protocol error occurred\n"
                       "URL: %s\n"
                       "HTTP/HTTPS headers: %s\n"
                       "Error code: %d\n"
                       "Error message: %s\n") % (err.url, err.headers,
                                                 err.errcode, err.errmsg)
            self.server_logger.error(err_msg)
            return (str(err), 0)
        except Exception, e:
            self.server_logger.error(str(e))
            self.server_logger.error(traceback.format_exc())
            return (str(e), 0)

################################################################################
# Some Medley code
class XMLObject(object):
    @staticmethod
    def convert_from_str(value, type):
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
                elif type == 'date':
                    return date(*system.time_strptime(value, '%Y-%m-%d')[0:3])
                elif type == 'datetime':
                    return datetime(*system.time_strptime(value, '%Y-%m-%d %H:%M:%S')[0:6])
        return None

    @staticmethod
    def convert_to_str(value,type):
        if value is not None:
            if type == 'date':
                return value.isoformat()
            elif type == 'datetime':
                return system.strftime(value, '%Y-%m-%d %H:%M:%S')
            else:
                return str(value)
        return ''

    @staticmethod
    def type_name(type):
        d = {'Integer':'int',
             'String':'str',
             'Long':'long',
             'Float':'float',
             'Boolean':'bool',
             'Date':'date',
             'DateTime':'datetime',
             }
        return d.get(type, 'str')
################################################################################

class MedleySimpleGUI(XMLObject):
    def __init__(self, id, name, vtid=None, version=None, alias_list=None,
                 t='vistrail', has_seq=None):
        self._id = id
        self._name = name
        self._version = version
        self._alias_list = alias_list
        self._vtid = vtid
        self._type = t

        if has_seq == None:
            self._has_seq = False
            if isinstance(self._alias_list, dict):
                for v in self._alias_list.itervalues():
                    if v._component._seq == True:
                        self._has_seq = True
        else:
            self._has_seq = has_seq

    def to_xml(self, node=None):
        """to_xml(node: ElementTree.Element) -> ElementTree.Element
           writes itself to xml
        """

        if node is None:
            node = ElementTree.Element('medley_simple_gui')

        #set attributes
        node.set('id', self.convert_to_str(self._id,'long'))
        node.set('version', self.convert_to_str(self._version,'long'))
        node.set('vtid', self.convert_to_str(self._vtid,'long'))
        node.set('name', self.convert_to_str(self._name,'str'))
        node.set('type', self.convert_to_str(self._type,'str'))
        node.set('has_seq', self.convert_to_str(self._has_seq,'bool'))
        for (k,v) in self._alias_list.iteritems():
            child_ = ElementTree.SubElement(node, 'alias')
            v.to_xml(child_)
        return node

    @staticmethod
    def from_xml(node):
        if node.tag != 'medley_simple_gui':
            print "node.tag != 'medley_simple_gui'"
            return None
        #read attributes
        data = node.get('id', None)
        id = MedleySimpleGUI.convert_from_str(data, 'long')
        data = node.get('name', None)
        name = MedleySimpleGUI.convert_from_str(data, 'str')
        data = node.get('version', None)
        version = MedleySimpleGUI.convert_from_str(data, 'long')
        data = node.get('vtid', None)
        vtid = MedleySimpleGUI.convert_from_str(data, 'long')
        data = node.get('type', None)
        type = MedleySimpleGUI.convert_from_str(data, 'str')
        data = node.get('has_seq', None)
        seq = ComponentSimpleGUI.convert_from_str(data, 'bool')
        alias_list = {}
        for child in node.getchildren():
            if child.tag == "alias":
                alias = AliasSimpleGUI.from_xml(child)
                alias_list[alias._name] = alias
        return MedleySimpleGUI(id=id, name=name, vtid=vtid, version=version,
                               alias_list=alias_list, t=type, has_seq=seq)
        
    @staticmethod
    def from_mashup(mashup):
        #read attributes
        alias_list = {}
        for child in mashup.aliases:
            alias = AliasSimpleGUI.from_alias(child)
            alias_list[alias._name] = alias
        return MedleySimpleGUI(id=mashup.id,
                               name=mashup.name,
                               vtid=mashup.vtid,
                               version=mashup.version,
                               alias_list=alias_list,
                               t=mashup.type,
                               has_seq=mashup.has_seq)

################################################################################

class AliasSimpleGUI(XMLObject):
    def __init__(self, id, name, component=None):
        self._id = id
        self._name = name
        self._component = component

    def to_xml(self, node=None):
        """to_xml(node: ElementTree.Element) -> ElementTree.Element
            writes itself to xml
        """
        if node is None:
            node = ElementTree.Element('alias')

        #set attributes
        node.set('id', self.convert_to_str(self._id,'long'))
        node.set('name', self.convert_to_str(self._name,'str'))
        child_ = ElementTree.SubElement(node, 'component')
        self._component.to_xml(child_)

        return node

    @staticmethod
    def from_xml(node):
        if node.tag != 'alias':
            return None

        #read attributes
        data = node.get('id', None)
        id = AliasSimpleGUI.convert_from_str(data, 'long')
        data = node.get('name', None)
        name = AliasSimpleGUI.convert_from_str(data, 'str')
        for child in node.getchildren():
            if child.tag == "component":
                component = ComponentSimpleGUI.from_xml(child)
        alias = AliasSimpleGUI(id,name,component)
        return alias

    @staticmethod
    def from_alias(alias):
        component = ComponentSimpleGUI.from_component(alias.component)
        alias = AliasSimpleGUI(alias.id, alias.name, component)
        return alias

################################################################################

class ComponentSimpleGUI(XMLObject):
    def __init__(self, id, pos, ctype, spec, val=None, minVal=None, maxVal=None,
                 stepSize=None, strvalueList="", parent=None, seq=False,
                 widget="text"):
        """ComponentSimpleGUI()
        widget can be: text, slider, combobox, numericstepper, checkbox

        """
        self._id = id
        self._pos = pos
        self._spec = spec
        self._ctype = ctype
        self._val = val
        self._minVal = minVal
        self._maxVal = maxVal
        self._stepSize = stepSize
        self._strvaluelist = strvalueList
        self._parent = parent
        self._seq = seq
        self._widget = widget

    def _get_valuelist(self):
        data = self._strvaluelist.split(',')
        result = []
        for d in data:
            result.append(urllib.unquote_plus(d))
        return result
    def _set_valuelist(self, valuelist):
        q = []
        for v in valuelist:
            q.append(urllib.quote_plus(v))
        self._strvaluelist = ",".join(q)

    _valueList = property(_get_valuelist,_set_valuelist)

    def to_xml(self, node=None):
        """to_xml(node: ElementTree.Element) -> ElementTree.Element
             writes itself to xml
        """
        if node is None:
            node = ElementTree.Element('component')

        #set attributes
        node.set('id', self.convert_to_str(self._id,'long'))
        node.set('pos', self.convert_to_str(self._pos,'long'))
        node.set('spec', self.convert_to_str(self._spec,'str'))
        node.set('ctype', self.convert_to_str(self._ctype,'str'))
        node.set('val', self.convert_to_str(self._val, 'str'))
        node.set('minVal', self.convert_to_str(self._minVal,'str'))
        node.set('maxVal', self.convert_to_str(self._maxVal,'str'))
        node.set('stepSize', self.convert_to_str(self._stepSize,'str'))
        node.set('valueList',self.convert_to_str(self._strvaluelist,'str'))
        node.set('parent', self.convert_to_str(self._parent,'str'))
        node.set('seq', self.convert_to_str(self._seq,'bool'))
        node.set('widget',self.convert_to_str(self._widget,'str'))
        return node

    @staticmethod
    def from_xml(node):
        if node.tag != 'component':
            return None

        #read attributes
        data = node.get('id', None)
        id = ComponentSimpleGUI.convert_from_str(data, 'long')
        data = node.get('pos', None)
        pos = ComponentSimpleGUI.convert_from_str(data, 'long')
        data = node.get('ctype', None)
        ctype = ComponentSimpleGUI.convert_from_str(data, 'str')
        data = node.get('spec', None)
        spec = ComponentSimpleGUI.convert_from_str(data, 'str')
        data = node.get('val', None)
        val = ComponentSimpleGUI.convert_from_str(data, 'str')
        val = val.replace("&lt;", "<")
        val = val.replace("&gt;", ">")
        val = val.replace("&amp;","&")
        data = node.get('minVal', None)
        minVal = ComponentSimpleGUI.convert_from_str(data, 'str')
        data = node.get('maxVal', None)
        maxVal = ComponentSimpleGUI.convert_from_str(data, 'str')
        data = node.get('stepSize', None)
        stepSize = ComponentSimpleGUI.convert_from_str(data, 'str')
        data = node.get('valueList', None)
        values = ComponentSimpleGUI.convert_from_str(data, 'str')
        values = values.replace("&lt;", "<")
        values = values.replace("&gt;", ">")
        values = values.replace("&amp;","&")
        data = node.get('parent', None)
        parent = ComponentSimpleGUI.convert_from_str(data, 'str')
        data = node.get('seq', None)
        seq = ComponentSimpleGUI.convert_from_str(data, 'bool')
        data = node.get('widget', None)
        widget = ComponentSimpleGUI.convert_from_str(data, 'str')
        component = ComponentSimpleGUI(id=id,
                                       pos=pos,
                                       ctype=ctype,
                                       spec=spec,
                                       val=val,
                                       minVal=minVal,
                                       maxVal=maxVal,
                                       stepSize=stepSize,
                                       strvalueList=values,
                                       parent=parent,
                                       seq=seq,
                                       widget=widget)
        return component
    
    @staticmethod
    def from_component(c):
        component = ComponentSimpleGUI(id=c.id,
                                       pos=c.pos,
                                       ctype='Parameter',
                                       spec=ComponentSimpleGUI.type_name(c.type),
                                       val=c.val,
                                       minVal=c.minVal,
                                       maxVal=c.maxVal,
                                       stepSize=c.stepSize,
                                       strvalueList=c.strvaluelist,
                                       parent=c.parent,
                                       seq=c.seq,
                                       widget=c.widget)
        return component

################################################################################
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
            raise vistrails.core.requirements.MissingRequirement("Qt version >= 4.2")

        self.rpcserver = None
        self.pingserver = None
        self.images_url = "http://vistrails.sci.utah.edu/medleys/images/"
        qt.allowQObjects()

    def is_running_gui(self):
        return True

    def make_logger(self, filename, label):
        """self.make_logger(filename:str) -> logger. Creates a logging object to
        be used for the server so we can log requests in file f."""
        logger = logging.getLogger("VistrailsRPC[%s]"%label)
        handler = logging.handlers.RotatingFileHandler(filename, maxBytes = 1024*1024,
                                                       backupCount=5)
        handler.setFormatter(logging.Formatter('%(name)s - %(asctime)s %(levelname)-8s %(message)s'))
        handler.setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        return logger

    def load_config(self, filename):
        """ Load in server parameters from config file.
        If parameters are missing, write them in and raise error.
        If file doesn't exist, create one and raise error. """

        global accessList, db_host, db_read_user, db_read_pass, db_write_user, db_write_pass, media_dir, script_file, virtual_display
        accessList = []
        db_host = ''
        db_read_user = ''
        db_read_pass = ''
        db_write_user = ''
        db_write_pass = ''
        media_dir = ''
        script_file = ''
        virtual_display = ''

        config = ConfigParser.ConfigParser()
        file_opened = config.read(filename)
        has_changed = False

        if not file_opened:
            # new file to store default (empt) config
            new_filename = os.path.join(system.vistrails_root_directory(), 'server.cfg')

        # load or create access fields
        if config.has_option("access", "permitted_addresses"):
            read_accessList = config.get("access", "permitted_addresses")
            accessList = [elem.strip() for elem in read_accessList.split(',')]
        else:
            if not config.has_section("access"):
                config.add_section("access")
            config.set("access", "permitted_addresses", "localhost,")
            accessList = []
            has_changed = True

        # load or create database fields
        if not config.has_section("database"):
            config.add_section("database")
            has_changed = True

        if config.has_option("database", "host"):
            db_host = config.get("database", "host")
        else:
            config.set("database", "host", "")
            has_changed = True

        if config.has_option("database", "read_user"):
            db_read_user = config.get("database", "read_user")
        else:
            config.set("database", "read_user", "")
            has_changed = True

        if config.has_option("database", "read_password"):
            db_read_pass = config.get("database", "read_password")
        else:
            config.set("database", "read_password", "")
            has_changed = True

        if config.has_option("database", "write_user"):
            db_write_user = config.get("database", "write_user")
        else:
            config.set("database", "write_user", "")
            has_changed = True

        if config.has_option("database", "write_password"):
            db_write_pass = config.get("database", "write_password")
        else:
            config.set("database", "write_password", "")
            has_changed = True

        if not config.has_section("media"):
            config.add_section("media")
            has_changed = True

        if config.has_option("media", "media_dir"):
            media_dir = config.get("media", "media_dir")
            if not os.path.exists(media_dir):
                raise ValueError("media_dir %s doesn't exist." % media_dir)

        if not config.has_section("script"):
            config.add_section("script")
            has_changed = True

        if config.has_option("script", "script_file"):
            script_file = config.get("script", "script_file")
            if not os.path.exists(script_file):
                raise ValueError("script_file %s doesn't exist." % script_file)
        else:
            config.set("script", "script_file", "")
            has_changed = True

        if config.has_option("script", "virtual_display"):
            virtual_display = config.get("script", "virtual_display")
        
        if virtual_display == "":
            virtual_display = "0"

        # check if all required parameters are present
        missing_req_fields = [y for (x,y) in ((db_host,"host"),
                                              (db_read_user,"read_user"),
                                              (db_write_user,"write_user"),
                                              (media_dir,"media_dir"),
                                              (script_file,"script_file"),
                                              (accessList,"permission_addresses")) if not x]
        if missing_req_fields:
            self.server_logger.error(("Following required parameters where missing "
                                      "from %s config file: %s ") % \
                                     (filename, ", ".join(missing_req_fields)))
            if not has_changed:
                raise ValueError("Following required parameters where missing from %s config file: %s " %
                                 (filename, ", ".join(missing_req_fields)))

        if has_changed:
            # save changes to passed config file
            if file_opened:
                config.write(open(filename, "wb"))
                self.server_logger.error("Invalid config file, the missing fields have been "
                                         "added to your config, please populate them")
                raise RuntimeError("Invalid config file, the missing fields have been "
                                   "added to your config, please populate them")
            else:
                # save changes to default config file
                config.write(open(new_filename, "wb"))
                self.server_logger.error("Config file %s doesn't exist. Creating new file at %s. "
                                         "Please populated it with the correct values and use it" %
                                         (filename, new_filename))
                raise RuntimeError("Config file %s doesn't exist. Creating new file at %s. "
                                   "Please populate it with the correct values and use it" %
                                   (filename, new_filename))

    def init(self, optionsDict=None, args=[]):
        """ init(optionDict: dict) -> boolean
        Create the application with a dict of settings

        """
        VistrailsApplicationInterface.init(self,optionsDict, args)

        # self.vistrailsStartup.init()
        self.server_logger = self.make_logger(self.temp_configuration.check('rpcLogFile'),
                                              self.temp_configuration.check('rpcPort'))
        self.load_config(self.temp_configuration.check('rpcConfig'))
        self.start_other_instances(self.temp_configuration.check('rpcInstances'))
        self._initialized = True
        return True

    def start_other_instances(self, number):
        global virtual_display, script_file
        self.others = []
        host = self.temp_configuration.check('rpcServer')
        port = self.temp_configuration.check('rpcPort')
        virt_disp = int(virtual_display)
        for x in xrange(number):
            port += 1   # each instance needs one port space for now
                        #later we might need 2 (normal requests and status requests)
            virt_disp += 1
            args = [script_file,":%s"%virt_disp,host,str(port),'0', '0']
            try:
                p = subprocess.Popen(args)
                time.sleep(20)
                self.others.append("http://%s:%s"%(host,port))
            except Exception, e:
                self.server_logger.error(("Couldn't start the instance on display:"
                                          "%s port: %s") % (virtual_display, port))
                self.server_logger.error(str(e))

    def stop_other_instances(self):
        script = os.path.join(system.vistrails_root_directory(), "stop_vistrails_server.py")
        for o in self.others:
            args = ['python', script, o]
            try:
                subprocess.Popen(args)
                time.sleep(15)
            except Exception, e:
                self.server_logger.error("Couldn't stop instance: %s" % o)
                self.server_logger.error(str(e))

    def run_server(self):
        """run_server() -> None
        This will run forever until the server receives a quit request, done
        via xml-rpc.
        """

        self.server_logger.info("Server is running on http://%s:%s"%(
                                   self.temp_configuration.check('rpcServer'),
                                   self.temp_configuration.check('rpcPort')))
        if self.temp_configuration.check('multithread'):
            self.rpcserver = ThreadedXMLRPCServer(
                                  (self.temp_configuration.check('rpcServer'),
                                   self.temp_configuration.check('rpcPort')),
                                  self.server_logger)
            self.server_logger.info("    multithreaded instance")
        else:
            self.rpcserver = StoppableXMLRPCServer(
                                  (self.temp_configuration.check('rpcServer'),
                                   self.temp_configuration.check('rpcPort')),
                                  self.server_logger)
            """
            self.pingserver = StoppableXMLRPCServer(
                                 (self.temp_configuration.check('rpcServer'),
                                  self.temp_configuration.check('rpcPort')-1),
                                 self.server_logger)
            """
            self.server_logger.info("    singlethreaded instance")
        #self.rpcserver.register_introspection_functions()
        self.rpcserver.register_instance(RequestHandler(self.server_logger,
                                                        self.others))
        if self.pingserver:
            self.pingserver.register_instance(RequestHandler(
                                                      self.server_logger, []))
            self.server_logger.info(
                       "Status XML RPC Server is listening on http://%s:%s"% \
                            (self.temp_configuration.check('rpcServer'),
                             self.temp_configuration.check('rpcPort')-1))
            self.pingserver.register_function(self.quit_server, "quit")
            self.pingserver.serve_forever()
            self.pingserver.serve_close()

        self.rpcserver.register_function(self.quit_server, "quit")
        self.server_logger.info(
                    "Vistrails XML RPC Server is listening on http://%s:%s"% \
                        (self.temp_configuration.check('rpcServer'),
                         self.temp_configuration.check('rpcPort')))
        self.rpcserver.serve_forever()
        self.rpcserver.server_close()
        return 0

    def quit_server(self):
        result = "Vistrails XML RPC Server is quitting."
        self.stop_other_instances()
        self.server_logger.info(result)
        self.rpcserver.stop = True
        return result

# The initialization must be explicitly signalled. Otherwise, any
# modules importing vis_application will try to initialize the entire
# app.
def start_server(optionsDict=None, args=[]):
    """Initializes the application singleton."""
    global VistrailsServer
    if VistrailsServer:
        print "Server already started."
        return
    VistrailsServer = VistrailsServerSingleton()
    vistrails.gui.theme.initializeCurrentTheme()
    vistrails.core.application.set_vistrails_application(VistrailsServer)
    x = VistrailsServer.init(optionsDict, args)
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

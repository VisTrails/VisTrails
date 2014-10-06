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
from vistrails.db.versions.v1_0_4.domain import DBVistrail, DBVistrailVariable, \
                                      DBWorkflow, DBLog, DBRegistry, \
                                      DBAdd, DBChange, DBDelete, \
                                      DBPortSpec, DBPortSpecItem, \
                                      DBParameterExploration, \
                                      DBPEParameter, DBPEFunction, \
                                      IdScope, DBAbstraction, \
                                      DBModule, DBGroup, DBAnnotation, \
                                      DBActionAnnotation, DBStartup, \
                                      DBConfigKey, DBConfigBool, DBConfigStr, \
                                      DBConfigInt, DBConfigFloat, \
                                      DBConfiguration, DBStartupPackage, \
                                      DBLoopIteration, DBLoopExec, \
                                      DBModuleExec, DBGroupExec

from vistrails.db.services.vistrail import materializeWorkflow
from xml.dom.minidom import parseString
from itertools import izip
import os
import shutil
import string
import tempfile
from ast import literal_eval
import unittest

id_scope = None

def translateVistrail(_vistrail):
    """ Translate old annotation based vistrail variables to new
        DBVistrailVariable class """
    global id_scope

    def update_workflow(old_obj, trans_dict):
        return DBWorkflow.update_version(old_obj.db_workflow, 
                                         trans_dict, DBWorkflow())

    translate_dict = {'DBGroup': {'workflow': update_workflow}}
    vistrail = DBVistrail()
    id_scope = vistrail.idScope
    vistrail = DBVistrail.update_version(_vistrail, translate_dict, vistrail)

    vistrail.db_version = '1.0.4'
    return vistrail

def translateWorkflow(_workflow):
    global id_scope
    def update_workflow(old_obj, translate_dict):
        return DBWorkflow.update_version(old_obj.db_workflow, translate_dict)
    translate_dict = {'DBGroup': {'workflow': update_workflow}}

    workflow = DBWorkflow()
    id_scope = IdScope(remap={DBAbstraction.vtType: DBModule.vtType, DBGroup.vtType: DBModule.vtType})
    workflow = DBWorkflow.update_version(_workflow, translate_dict, workflow)
    workflow.db_version = '1.0.4'
    return workflow

def translateLog(_log):
    global id_scope
    def update_loop_execs(old_obj, translate_dict):
        if len(old_obj.db_loop_execs) == 0:
            return []
        # create new LoopExec and add existing as LoopIteration's
        ts_start = None
        ts_end = None
        new_iters = []
        for loop_exec in old_obj.db_loop_execs:
            item_execs = []
            for item_exec in loop_exec.db_item_execs:
                if item_exec.vtType == DBModuleExec.vtType:
                    item_execs.append(DBModuleExec.update_version(item_exec,
                                                                  translate_dict))
                if item_exec.vtType == DBGroupExec.vtType:
                    item_execs.append(DBGroupExec.update_version(item_exec,
                                                                 translate_dict))
                # skip DBLoopExecs
            new_iter = DBLoopIteration(item_execs=item_execs,
                                       id=id_scope.getNewId(DBLoopIteration.vtType),
                                       ts_start=loop_exec.db_ts_start,
                                       ts_end=loop_exec.db_ts_end,
                                       iteration=loop_exec.db_iteration,
                                       completed=loop_exec.db_completed,
                                       error=loop_exec.db_error)
            new_iters.append(new_iter)
            if ts_start is None or ts_start > loop_exec.db_ts_start:
                ts_start = loop_exec.db_ts_start
            if ts_end is None or ts_end < loop_exec.db_ts_end:
                ts_end = loop_exec.db_ts_end
        return [DBLoopExec(id=id_scope.getNewId(DBLoopExec.vtType),
                                       ts_start=ts_start,
                                       ts_end=ts_end,
                                       loop_iterations=new_iters)]

    def update_item_execs(old_obj, translate_dict):
        # remove loop_execs and add them as loop_iterations under a single loop_exec
        new_objs = []
        ts_start = None
        ts_end = None
        new_iters = []
        for obj in old_obj.db_item_execs:
            if obj.vtType == DBModuleExec.vtType:
                new_objs.append(DBModuleExec.update_version(obj,
                                                            translate_dict))
            if obj.vtType == DBGroupExec.vtType:
                new_objs.append(DBGroupExec.update_version(obj,
                                                           translate_dict))
            if obj.vtType == DBLoopExec.vtType:
                item_execs = []
                for item_exec in obj.db_item_execs:
                    if item_exec.vtType == DBModuleExec.vtType:
                        item_execs.append(DBModuleExec.update_version(item_exec,
                                                                      translate_dict))
                    if item_exec.vtType == DBGroupExec.vtType:
                        item_execs.append(DBGroupExec.update_version(item_exec,
                                                                     translate_dict))
                    # skip DBLoopExecs
                new_iter = DBLoopIteration(item_execs=item_execs,
                                           id=id_scope.getNewId(DBLoopIteration.vtType),
                                           ts_start=obj.db_ts_start,
                                           ts_end=obj.db_ts_end,
                                           iteration=obj.db_iteration,
                                           completed=obj.db_completed,
                                           error=obj.db_error)
                new_iters.append(new_iter)
                if ts_start is None or ts_start > obj.db_ts_start:
                    ts_start = obj.db_ts_start
                if ts_end is None or ts_end < obj.db_ts_end:
                    ts_end = obj.db_ts_end
        if len(new_iters):
            new_objs.append(DBLoopExec(id=id_scope.getNewId(DBLoopExec.vtType),
                                       ts_start=ts_start,
                                       ts_end=ts_end,
                                       loop_iterations=new_iters))
        return new_objs

        
        return DBWorkflow.update_version(old_obj.db_workflow, translate_dict)
    translate_dict = {'DBModuleExec': {'loop_execs': update_loop_execs},
                      'DBGroupExec': {'item_execs': update_item_execs}}
    log = DBLog.update_version(_log, translate_dict)
    log.db_version = '1.0.4'
    return log

def translateRegistry(_registry):
    global id_scope
    translate_dict = {}
    registry = DBRegistry()
    id_scope = registry.idScope
    registry = DBRegistry.update_version(_registry, translate_dict, registry)
    registry.db_version = '1.0.4'
    return registry

def translateStartup(_startup):
    # format is {<old_name>: <new_name>} or
    # {<old_name>: (<new_name> | None, [conversion_f | None, inner_d | None])
    # conversion_f is a function that mutates the value and
    # inner_d recurses the translation for inner configurations

    dot_vt_path = None
    startup_dir = os.path.dirname(_startup._filename)
    if os.path.isabs(startup_dir):
        dot_vt_path = startup_dir

    def change_value(cls, conv_f, _key, t_dict):
        cls_name = cls.__name__
        old_t_value = None
        if cls_name in t_dict:
            if 'value' in t_dict[cls_name]:
                old_t_value = t_dict[cls_name]['value']
        else:
            t_dict[cls_name] = {}
        t_dict[cls_name]['value'] = conv_f
        new_value = cls.update_version(_key.db_value, t_dict)
        del t_dict[cls_name]['value']
        if old_t_value is not None:
            t_dict[cls_name]['value'] = old_t_value
        if len(t_dict[cls_name]) < 1:
            del t_dict[cls_name]
        return new_value

    def invert_bool(_key, t_dict):
        def invert_value(_value, t):
            return unicode(not (_value.db_value.lower() == 'true'))
        return change_value(DBConfigBool, invert_value, _key, t_dict)

    def use_dirname(_key, t_dict):
        def get_dirname(_value, t):
            dir_name = os.path.dirname(_value.db_value)
            if os.path.isabs(dir_name) and dir_name.startswith(dot_vt_path):
                dir_name = dir_name[len(dot_vt_path)+1:]
                if not dir_name.strip():
                    dir_name = "logs"
            return dir_name
        return change_value(DBConfigStr, get_dirname, _key, t_dict)

    def update_dirname(_key, t_dict):
        def change_dirname(_value, t):
            abs_path = _value.db_value
            if os.path.isabs(abs_path) and abs_path.startswith(dot_vt_path):
                return abs_path[len(dot_vt_path)+1:]
            return abs_path
        return change_value(DBConfigStr, change_dirname, _key, t_dict)

    def pdf_bool_to_str(_value):
        s_val = "PNG"
        if _value.db_value.lower() == "true":
            s_val = "PDF"
        return DBConfigStr(value=s_val)

    t = {'alwaysShowDebugPopup': 'showDebugPopups',
         'autosave': 'autoSave',
         'errorOnConnectionTypeerror': 'showConnectionErrors',
         'errorOnVariantTypeerror': 'showVariantErrors',
         'interactiveMode': ('batch', invert_bool),
         'logFile': ('logDir', use_dirname),
         'logger': None, # DELETE
         'maxMemory': None,
         'minMemory': None,
         'nologger': ('executionLog', invert_bool),
         'pythonPrompt': None,
         'reviewMode': None, # unknown what this was/is
         'shell': ('shell', None, {'font_face': 'fontFace',
                                   'font_size': 'fontSize'}),
         'showMovies': None,
         'showSpreadsheetOnly': ('showWindow', invert_bool),
         'spreadsheetDumpCells': 'outputDirectory',
         'upgradeOn': 'upgrades',
         'useCache': 'cache',
         'verbosenessLevel': 'debugLevel',
         'webRepositoryLogin': 'webRespositoryUser',
         'evolutionGraph': 'withVersionTree',
         'workflowGraph': 'withWorkflow',
         # 'workflowInfo': 'outputWorkflowInfo',
         'workflowInfo': 'outputDirectory',
         'executeWorkflows': 'execute',

         'thumbs': ('thumbs', None,
                    {'cacheDirectory': ('cacheDir', update_dirname)}),
         'abstractionsDirectory': ('subworkflowsDir', update_dirname),
         'userPackageDirectory': ('userPackageDir', update_dirname),
         'temporaryDirectory': 'temporaryDir',
         'dataDirectory': 'dataDir',
         'fileDirectory': 'fileDir',
         'packageDirectory': 'packageDir',

         }

    # these are moving to package configurations
    t_package = {
         'spreadsheetDumpPDF': ('spreadsheet', 'dumpfileType', pdf_bool_to_str),
         'fixedSpreadsheetCells': ('spreadsheet', 'fixedCellSize'),
    }

    def get_key_name_update(new_name):
        def update_key_name(_key, t_dict):
            return new_name
        return update_key_name

    def update_config_keys(_config, t_dict):
        # just update __startup_translate__ as we recurse,
        # update_key_name and update_key_value take care of the rest
        cur_t = t_dict['__startup_translate__']
        cur_t_pkg = t_dict['__startup_translate_pkg__']
        new_keys = []
        for key in _config.db_config_keys:
            to_delete = False
            new_name = None
            conv_f = None
            inner_t = None
            if key.db_name in cur_t:
                t_obj = cur_t[key.db_name]
                if type(t_obj) == tuple:
                    new_name = t_obj[0]
                    if len(t_obj) > 1:
                        conv_f = t_obj[1]
                    if len(t_obj) > 2:
                        inner_t = t_obj[2]
                elif t_obj is None:
                    to_delete = True
                else:
                    new_name = t_obj

            if key.db_name in cur_t_pkg:
                updated_key = DBConfigKey.update_version(key, t_dict)
                pkg_t = cur_t_pkg[key.db_name]
                pkg_name = pkg_t[0]
                key_name = pkg_t[1]
                config_dict = t_dict['__startup_package_config__']

                if pkg_name not in config_dict:
                    config_dict[pkg_name] = []
                if len(pkg_t) > 2:
                    value_f = pkg_t[2]
                    new_value = value_f(key.db_value)
                else:
                    # have to update version here?
                    new_value = updated_key.db_value
                config_dict[pkg_name].append(DBConfigKey(name=key_name,
                                                         value=new_value))

            # if we have already set a key, don't override the new
            # setting in general (may want to if swapping existing
            # names, but this should be the exception)
            elif (not to_delete and
                (new_name == key.db_name or
                 new_name not in _config.db_config_keys_name_index)):
                # always overwrite DBConfigKey settings so recursion
                # doesn't wrap over itself
                key_t_dict = {}
                if new_name is not None and new_name != key.db_name:
                    key_t_dict['name'] = get_key_name_update(new_name)
                if conv_f is not None:
                    key_t_dict['value'] = conv_f
                old_t_name = None
                old_t_value = None
                if len(key_t_dict) > 0:
                    if 'DBConfigKey' in t_dict:
                        if 'name' in t_dict['DBConfigKey']:
                            old_t_name = t_dict['DBConfigKey']['name']
                            del t_dict['DBConfigKey']['name']
                        if 'value' in t_dict['DBConfigKey']:
                            old_t_value = t_dict['DBConfigKey']['value']
                            del t_dict['DBConfigKey']['value']
                        t_dict['DBConfigKey'].update(key_t_dict)
                    else:
                        t_dict['DBConfigKey'] = key_t_dict
                if inner_t is not None:
                    t_dict['__startup_translate__'] = inner_t
                new_keys.append(DBConfigKey.update_version(key, t_dict))
                if inner_t is not None:
                    t_dict['__startup_translate__'] = cur_t
                if len(key_t_dict) > 0:
                    if 'name' in t_dict['DBConfigKey']:
                        del t_dict['DBConfigKey']['name']
                    if 'value' in t_dict['DBConfigKey']:
                        del t_dict['DBConfigKey']['value']
                    if old_t_name is not None:
                        t_dict['DBConfigKey']['name'] = old_t_name
                    if old_t_value is not None:
                        t_dict['DBConfigKey']['value'] = old_t_value
                    if len(t_dict['DBConfigKey']) < 1:
                        del t_dict['DBConfigKey']
        return new_keys

    def update_package_config(_startup_pkg, t_dict):
        _config = _startup_pkg.db_configuration
        package_config = t_dict['__startup_package_config__']
        if _config is not None:
            config = DBConfiguration.update_version(_config, t_dict)
            if _startup_pkg.db_name in package_config:
                for new_key in package_config[_startup_pkg.db_name]:
                    if new_key.db_name in config.db_config_keys_name_index:
                        # already have, don't replace new setting
                        continue
                    else:
                        config.db_add_config_key(new_key)
                del package_config[_startup_pkg.db_name]
            return config
        return None

    # need to recurse both key name changes and key value changes
    # (could also change types...)
    translate_dict = {'DBConfiguration': {'config_keys': update_config_keys},
                      'DBStartupPackage': {'configuration':
                                           update_package_config},
                      '__startup_translate__': t,
                      '__startup_translate_pkg__': t_package,
                      '__startup_package_config__': dict()}
    startup = DBStartup()
    startup = DBStartup.update_version(_startup, translate_dict, startup)

    # add any translations to packages, creating startup_pkg and
    # configuration if necessary
    for pkg, keys in translate_dict['__startup_package_config__'].iteritems():
        if pkg in startup.db_enabled_packages.db_packages_name_index:
            s_pkg = startup.db_enabled_packages.db_packages_name_index[pkg]
        elif pkg in startup.db_disabled_packages.db_packages_name_index:
            s_pkg = startup.db_disabled_packages.db_packages_name_index[pkg]
        else:
            s_pkg = DBStartupPackage(name=pkg)
            startup.db_disabled_packages.db_add_package(s_pkg)
        if s_pkg.db_configuration is None:
            s_pkg.db_configuration = DBConfiguration(config_keys=keys)
        else:
            for new_key in keys:
                if new_key.db_name not in s_pkg.db_configuration:
                    # only add if new setting doesn't already exist
                    s_pkg.db_configuration.db_add_config_key(new_key)

    startup.db_version = '1.0.4'
    return startup

class TestTranslate(unittest.TestCase):
    def test_startup_update(self):
        from vistrails.db.services.io import open_startup_from_xml
        from vistrails.core.system import vistrails_root_directory
        import os

        startup_tmpl = os.path.join(vistrails_root_directory(),
                                    'tests', 'resources',
                                    'startup-0.1.xml.tmpl')
        f = open(startup_tmpl, 'r')
        template = string.Template(f.read())

        startup_dir = tempfile.mkdtemp(prefix="vt_startup")
        startup_fname = os.path.join(startup_dir, "startup.xml")
        with open(startup_fname, 'w') as f:
            f.write(template.substitute({'startup_dir': startup_dir}))
        try:
            # FIXME need to generate startup from local path
            startup = open_startup_from_xml(startup_fname)
            name_idx = startup.db_configuration.db_config_keys_name_index
            self.assertNotIn('nologger', name_idx)
            self.assertIn('executionLog', name_idx)
            self.assertFalse(
                name_idx['executionLog'].db_value.db_value.lower() == 'true')
            self.assertNotIn('showMovies', name_idx)
            self.assertIn('logDir', name_idx)
            self.assertEqual(name_idx['logDir'].db_value.db_value, 'logs')
            self.assertIn('userPackageDir', name_idx)
            self.assertEqual(name_idx['userPackageDir'].db_value.db_value,
                             'userpackages')
            self.assertIn('thumbs', name_idx)
            thumbs_name_idx = \
                    name_idx['thumbs'].db_value.db_config_keys_name_index
            self.assertIn('cacheDir', thumbs_name_idx)
            self.assertEqual(thumbs_name_idx['cacheDir'].db_value.db_value,
                             '/path/to/thumbs')
            self.assertIn('subworkflowsDir', name_idx)
            self.assertEqual(name_idx['subworkflowsDir'].db_value.db_value,
                             'subworkflows')

            # note: have checked with spreadsheet removed from all
            # packages list, too
            # TODO: make this a permanent test (new template?)
            self.assertNotIn('fixedSpreadsheetCells', name_idx)
            enabled_names = startup.db_enabled_packages.db_packages_name_index
            self.assertIn('spreadsheet', enabled_names)
            spreadsheet_config = enabled_names['spreadsheet'].db_configuration
            self.assertIsNotNone(spreadsheet_config)
            spreadsheet_name_idx = spreadsheet_config.db_config_keys_name_index
            self.assertIn('fixedCellSize', spreadsheet_name_idx)
            self.assertTrue(spreadsheet_name_idx['fixedCellSize'].db_value.db_value.lower() == "true")
            self.assertIn('dumpfileType', spreadsheet_name_idx)
            self.assertEqual(spreadsheet_name_idx['dumpfileType'].db_value.db_value, "PNG")
        finally:
            shutil.rmtree(startup_dir)

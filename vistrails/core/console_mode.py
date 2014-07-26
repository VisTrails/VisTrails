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
""" Module used when running  vistrails uninteractively """
from __future__ import absolute_import
import os.path
import uuid
from vistrails.core.application import is_running_gui
from vistrails.core.configuration import get_vistrails_configuration
import vistrails.core.interpreter.default
import vistrails.core.db.io
from vistrails.core.db.io import load_vistrail
from vistrails.core.db.locator import XMLFileLocator, ZIPFileLocator
from vistrails.core import debug
from vistrails.core.interpreter.job import JobMonitor, Workflow as JobWorkflow
from vistrails.core.utils import VistrailsInternalError, expression
from vistrails.core.vistrail.controller import VistrailController
from vistrails.core.vistrail.vistrail import Vistrail

import vistrails.core.packagemanager
import vistrails.core.system
import unittest
import vistrails.core.vistrail
import vistrails.db

################################################################################
    
def run_and_get_results(w_list, parameters='', output_dir=None, 
                        update_vistrail=True, extra_info=None, 
                        reason='Console Mode Execution'):
    """run_and_get_results(w_list: list of (locator, version), parameters: str,
                           output_dir:str, update_vistrail: boolean,
                           extra_info:dict)
    Run all workflows in w_list, and returns an interpreter result object.
    version can be a tag name or a version id.
    
    """
    elements = parameters.split("$&$")
    aliases = {}
    params = []
    result = []
    for locator, workflow in w_list:
        (v, abstractions , thumbnails, mashups)  = load_vistrail(locator)
        controller = VistrailController(v, locator, abstractions, thumbnails, 
                                        mashups, auto_save=update_vistrail)
        if isinstance(workflow, basestring):
            version = v.get_version_number(workflow)
        elif isinstance(workflow, (int, long)):
            version = workflow
        elif workflow is None:
            version = controller.get_latest_version_in_graph()
        else:
            msg = "Invalid version tag or number: %s" % workflow
            raise VistrailsInternalError(msg)
        controller.change_selected_version(version)
        
        for e in elements:
            pos = e.find("=")
            if pos != -1:
                key = e[:pos].strip()
                value = e[pos+1:].strip()
            
                if controller.current_pipeline.has_alias(key):
                    aliases[key] = value
                elif 'mashup_id' in extra_info:
                    # new-style mashups can have aliases not existing in pipeline
                    for mashuptrail in mashups:
                        if mashuptrail.vtVersion == version:
                            mashup = mashuptrail.getMashup(extra_info['mashup_id'])
                            c = mashup.getAliasByName(key).component
                            params.append((c.vttype, c.vtid, value))

        if output_dir is not None and controller.current_pipeline is not None:
            # FIXME DAK: why is this always done?!? there is a flag for it...
            if is_running_gui():
                controller.updatePipelineScene()
                base_fname = "%s_%s_pipeline.pdf" % (locator.short_filename, version)
                filename = os.path.join(output_dir, base_fname)
                controller.current_pipeline_scene.saveToPDF(filename)
            else:
                debug.critical("Cannot save pipeline figure when not "
                               "running in gui mode")
            base_fname = "%s_%s_pipeline.xml" % (locator.short_filename, version)
            filename = os.path.join(output_dir, base_fname)
            vistrails.core.db.io.save_workflow(controller.current_pipeline, filename)
        if not update_vistrail:
            conf = get_vistrails_configuration()
            if conf.has('thumbs'):
                conf.thumbs.autoSave = False
        
        jobMonitor = JobMonitor.getInstance()
        current_workflow = jobMonitor.currentWorkflow()
        if not current_workflow:
            for job in jobMonitor._running_workflows.itervalues():
                try:
                    job_version = int(job.version)
                except ValueError:
                    job_version =  v.get_version_number(job.version)
                if version == job_version and locator.to_url() == job.vistrail:
                    current_workflow = job
                    jobMonitor.startWorkflow(job)
            if not current_workflow:
                current_workflow = JobWorkflow(locator.to_url(), version)
                jobMonitor.getInstance().startWorkflow(current_workflow)

        try:
            (results, _) = \
            controller.execute_current_workflow(custom_aliases=aliases,
                                                custom_params=params,
                                                extra_info=extra_info,
                                                reason=reason)
        finally:
            jobMonitor.finishWorkflow()
        new_version = controller.current_version
        if new_version != version:
            debug.log("Version '%s' (%s) was upgraded. The actual "
                      "version executed was %s" % (
                      workflow, version, new_version))
        run = results[0]
        run.workflow_info = (locator.name, new_version)
        run.pipeline = controller.current_pipeline

        if update_vistrail:
            controller.write_vistrail(locator)
        result.append(run)
        if current_workflow.modules:
            if current_workflow.completed():
                run.job = "COMPLETED"
            else:
                run.job = "RUNNING: %s" % current_workflow.id
                for job in current_workflow.modules.itervalues():
                    if not job.finished:
                        run.job += "\n  %s %s %s" % (job.start, job.name, job.description())
            print run.job
    return result

################################################################################

def get_wf_graph(w_list, output_dir=None, pdf=False):
    """run_and_get_results(w_list: list of (locator, version), 
                           output_dir:str, pdf:bool)
    Load all workflows in wf_list and dump their graph to output_dir.
    
    """
    result = []
    if is_running_gui():
        from vistrails.gui.vistrail_controller import VistrailController as \
             GUIVistrailController
        for locator, workflow in w_list:
            try:
                (v, abstractions , thumbnails, mashups)  = load_vistrail(locator)
                controller = GUIVistrailController(v, locator, abstractions, 
                                                   thumbnails, mashups,
                                                   auto_save=False)
                version = None
                if isinstance(workflow, basestring):
                    version = v.get_version_number(workflow)
                elif isinstance(workflow, (int, long)):
                    version = workflow
                elif workflow is None:
                    version = controller.get_latest_version_in_graph()
                else:
                    msg = "Invalid version tag or number: %s" % workflow
                    raise VistrailsInternalError(msg)
            
                if (output_dir is not None and 
                    controller.current_pipeline is not None):
                    controller.updatePipelineScene()
                    if pdf:
                        base_fname = "%s_%s_pipeline.pdf" % \
                                     (locator.short_filename, version)
                        filename = os.path.join(output_dir, base_fname)
                        controller.current_pipeline_scene.saveToPDF(filename)
                    else:
                        base_fname = "%s_%s_pipeline.png" % \
                                     (locator.short_filename, version)
                        filename = os.path.join(output_dir, base_fname)
                        controller.current_pipeline_scene.saveToPNG(filename)
                    result.append((True, ""))
            except Exception, e:
                result.append((False, debug.format_exception(e)))
    else:
        error_str = "Cannot save pipeline figure when not " \
            "running in gui mode"
        debug.critical(error_str)
        result.append((False, error_str))
    return result

################################################################################

def get_vt_graph(vt_list, tree_info, pdf=False):
    """get_vt_graph(vt_list: list of locator, tree_info:str)
    Load all vistrails in vt_list and dump their tree to tree_info.
    
    """
    result = []
    if is_running_gui():
        from vistrails.gui.vistrail_controller import VistrailController as \
             GUIVistrailController
        for locator in vt_list:
            try:
                (v, abstractions , thumbnails, mashups)  = load_vistrail(locator)
                controller = GUIVistrailController(v, locator, abstractions, 
                                                   thumbnails, mashups)
                if tree_info is not None:
                        from vistrails.gui.version_view import QVersionTreeView
                        version_view = QVersionTreeView()
                        version_view.scene().setupScene(controller)
                        if pdf:
                            base_fname = "graph_%s.pdf" % locator.short_filename
                            filename = os.path.join(tree_info, base_fname)
                            version_view.scene().saveToPDF(filename)
                        else:
                            base_fname = "graph_%s.png" % locator.short_filename
                            filename = os.path.join(tree_info, base_fname)
                            version_view.scene().saveToPNG(filename)
                        del version_view
                        result.append((True, ""))
            except Exception, e:
                result.append((False, debug.format_exception(e)))
    else:
        error_str = "Cannot save version tree figure when not " \
            "running in gui mode"
        debug.critical(error_str)
        result.append((False, error_str))
    return result

################################################################################

def run(w_list, parameters='', output_dir=None, update_vistrail=True,
        extra_info=None, reason="Console Mode Execution"):
    """run(w_list: list of (locator, version), parameters: str) -> boolean
    Run all workflows in w_list, version can be a tag name or a version id.
    Returns list of errors (empty list if there are no errors)
    """
    all_errors = []
    results = run_and_get_results(w_list, parameters, output_dir, 
                                  update_vistrail,extra_info, reason)
    for result in results:
        (objs, errors, executed) = (result.objects,
                                    result.errors, result.executed)
        for err in sorted(errors.iteritems()):
            all_errors.append(result.workflow_info + err)
    return all_errors

def run_parameter_exploration(locator, pe_id, extra_info = {},
                              reason="Console Mode Parameter Exploration Execution"):
    """run_parameter_exploration(w_list: (locator, version),
                                 pe_id: str/int,
                                 reason: str) -> (pe_id, [error msg])
    Run parameter exploration in w, and returns an interpreter result object.
    version can be a tag name or a version id.
    
    """
    if is_running_gui():
        from vistrails.gui.vistrail_controller import VistrailController as \
             GUIVistrailController
        try:
            (v, abstractions , thumbnails, mashups)  = load_vistrail(locator)
            controller = GUIVistrailController(v, locator, abstractions, 
                                               thumbnails, mashups)
            try:
                pe_id = int(pe_id)
                pe = controller.vistrail.get_paramexp(pe_id)
            except ValueError:
                pe = controller.vistrail.get_named_paramexp(pe_id)
            controller.change_selected_version(pe.action_id)
            controller.executeParameterExploration(pe, extra_info=extra_info,
                                                   showProgress=False)
        except Exception, e:
            import traceback
            return (locator, pe_id,
                    debug.format_exception(e), traceback.format_exc())

def run_parameter_explorations(w_list, extra_info = {},
                       reason="Console Mode Parameter Exploration Execution"):
    """run(w_list: list of (locator, pe_id), reason: str) -> boolean
    For each workflow in w_list, run parameter exploration pe_id
    version can be a tag name or a version id.
    Returns list of errors (empty list if there are no errors)
    """
    all_errors = []
    for locator, pe_id in w_list:
        result = run_parameter_exploration(locator, pe_id, reason=reason,
                                           extra_info=extra_info)
        if result:
            all_errors.append(result)
    return all_errors

def cleanup():
    vistrails.core.interpreter.cached.CachedInterpreter.cleanup()

################################################################################
#Testing


class TestConsoleMode(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        manager = vistrails.core.packagemanager.get_package_manager()
        if manager.has_package('org.vistrails.vistrails.console_mode_test'):
            return

        d = {'console_mode_test': 'vistrails.tests.resources.'}
        manager.late_enable_package('console_mode_test',d)

    @classmethod
    def tearDownClass(cls):
        manager = vistrails.core.packagemanager.get_package_manager()
        if manager.has_package('org.vistrails.vistrails.console_mode_test'):
            manager.late_disable_package('console_mode_test')
            
    def test1(self):
        from vistrails.core.modules.basic_modules import StandardOutput
        values = []
        def mycompute(s):
            v = s.get_input('value')
            values.append(v)
        orig_compute = StandardOutput.compute
        StandardOutput.compute = mycompute
        try:
            locator = XMLFileLocator(vistrails.core.system.vistrails_root_directory() +
                                     '/tests/resources/dummy.xml')
            result = run([(locator, "int chain")], update_vistrail=False)
            self.assertEqual(len(result), 0)
            self.assertEqual(values, [2])
        finally:
            StandardOutput.compute = orig_compute

    def test_tuple(self):
        from vistrails.core.vistrail.module_param import ModuleParam
        from vistrails.core.vistrail.module_function import ModuleFunction
        from vistrails.core.utils import DummyView
        from vistrails.core.vistrail.module import Module
        import vistrails.db.domain
       
        id_scope = vistrails.db.domain.IdScope()
        interpreter = vistrails.core.interpreter.default.get_default_interpreter()
        v = DummyView()
        p = vistrails.core.vistrail.pipeline.Pipeline()
        params = [ModuleParam(id=id_scope.getNewId(ModuleParam.vtType),
                              pos=0,
                              type='Float',
                              val='2.0',
                              ),
                  ModuleParam(id=id_scope.getNewId(ModuleParam.vtType),
                              pos=1,
                              type='Float',
                              val='2.0',
                              )]
        function = ModuleFunction(id=id_scope.getNewId(ModuleFunction.vtType),
                                  name='input')
        function.add_parameters(params)
        module = Module(id=id_scope.getNewId(Module.vtType),
                           name='TestTupleExecution',
                           package='org.vistrails.vistrails.console_mode_test',
                           version='0.9.1')
        module.add_function(function)

        p.add_module(module)

        interpreter.execute(p,
                            locator=XMLFileLocator('foo'),
                            current_version=1L,
                            view=v)

    def test_python_source(self):
        locator = XMLFileLocator(vistrails.core.system.vistrails_root_directory() +
                                 '/tests/resources/pythonsource.xml')
        result = run([(locator,"testPortsAndFail")], update_vistrail=False)
        self.assertEqual(len(result), 0)

    def test_python_source_2(self):
        locator = XMLFileLocator(vistrails.core.system.vistrails_root_directory() +
                                 '/tests/resources/pythonsource.xml')
        result = run_and_get_results([(locator, "test_simple_success")],
                                     update_vistrail=False)[0]
        self.assertEquals(len(result.executed), 1)

    def test_dynamic_module_error(self):
        locator = XMLFileLocator(vistrails.core.system.vistrails_root_directory() + 
                                 '/tests/resources/dynamic_module_error.xml')
        result = run([(locator, "test")], update_vistrail=False)
        self.assertNotEqual(len(result), 0)

    def test_change_parameter(self):
        locator = XMLFileLocator(vistrails.core.system.vistrails_root_directory() + 
                                 '/tests/resources/test_change_vistrail.xml')
        result = run([(locator, "v1")], update_vistrail=False)
        self.assertEqual(len(result), 0)

        result = run([(locator, "v2")], update_vistrail=False)
        self.assertEquals(len(result), 0)

    def test_ticket_73(self):
        # Tests serializing a custom-named module to disk
        locator = XMLFileLocator(vistrails.core.system.vistrails_root_directory() + 
                                 '/tests/resources/test_ticket_73.xml')
        v = locator.load()

        import tempfile
        (fd, filename) = tempfile.mkstemp()
        os.close(fd)
        locator = XMLFileLocator(filename)
        try:
            locator.save(v)
        finally:
            os.remove(filename)

if __name__ == '__main__':
    unittest.main()

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

import copy
import math
import os
import uuid

from PyQt4 import QtCore, QtGui

import vistrails.core.analogy
from vistrails.core.configuration import get_vistrails_configuration
from vistrails.core.data_structures.graph import Graph
from vistrails.core import debug
import vistrails.core.db.action
from vistrails.core.interpreter.default import get_default_interpreter
from vistrails.core.interpreter.job import Workflow as JobWorkflow
from vistrails.core.layout.version_tree_layout import VistrailsTreeLayoutLW
from vistrails.core.log.opm_graph import OpmGraph
from vistrails.core.log.prov_document import ProvDocument
from vistrails.core.modules.abstraction import identifier as abstraction_pkg
from vistrails.core.modules.module_registry import get_module_registry
from vistrails.core.param_explore import ActionBasedParameterExploration
from vistrails.core.query.version import TrueSearch
from vistrails.core.query.visual import VisualQuery
from vistrails.core.utils import DummyView, VistrailsInternalError, InvalidPipeline
import vistrails.core.system
from vistrails.core.vistrail.controller import VistrailController as BaseController
from vistrails.core.vistrail.pipeline import Pipeline
from vistrails.core.vistrail.vistrail import Vistrail, TagExists
from vistrails.gui.pipeline_view import QPipelineView
from vistrails.gui.theme import CurrentTheme
import vistrails.gui.utils
from vistrails.gui.utils import show_warning, show_question, YES_BUTTON, NO_BUTTON
from vistrails.gui.version_prop import QVersionProp


################################################################################

class ExecutionProgressDialog(QtGui.QProgressDialog):
    def __init__(self, parent=None):
        QtGui.QProgressDialog.__init__(self, 'Executing Workflow',
                                       '&Cancel',
                                       0, 100,
                                       parent, QtCore.Qt.Dialog)
        self.setWindowTitle('Executing')
        self.setWindowModality(QtCore.Qt.WindowModal)
        self._last_set_value = 0
        self._progress_canceled = False
        # if suspended is true we should not wait for a job to complete
        self.suspended = False

    def setValue(self, value):
        self._last_set_value = value
        super(ExecutionProgressDialog, self).setValue(value)

    def goOn(self):
        self.reset()
        self.show()
        super(ExecutionProgressDialog, self).setValue(self._last_set_value)


class VistrailController(QtCore.QObject, BaseController):
    """
    VistrailController is the class handling all action control in
    VisTrails. It updates pipeline, vistrail and emit signals to
    update the view

    Signals emitted:

    vistrailChanged(): emitted when the version tree needs to be
    recreated (for example, a node was added/deleted or the layout
    changed).

    versionWasChanged(): emitted when the current version (the one
    being displayed by the pipeline view) has changed.

    searchChanged(): emitted when the search statement from the
    version view has changed.

    stateChanged(): stateChanged is called when a vistrail goes from
    unsaved to saved or vice-versa.
    
    notesChanged(): notesChanged is called when the version notes have
    been updated

    """

    def __init__(self, vistrail=None, locator=None, abstractions=None,
                 thumbnails=None, mashups=None, pipeline_view=None, 
                 id_scope=None, set_log_on_vt=True, auto_save=True, name=''):
        """ VistrailController(vistrail: Vistrail, 
                               locator: BaseLocator,
                               abstractions: [<filename strings>],
                               thumbnails: [<filename strings>],
                               mashups: [<filename strings>],
                               pipeline_view: QPipelineView
                               id_scope: IdScope,
                               set_log_on_vt: bool,
                               auto_save: bool, 
                               name: str) -> VistrailController
        Create a controller for a vistrail.

        """

        QtCore.QObject.__init__(self)

        if pipeline_view is None:
            self.current_pipeline_view = QPipelineView()
        else:
            self.current_pipeline_view = pipeline_view

        self.vistrail_view = None
        self.reset_pipeline_view = False
        self.reset_version_view = True
        self.quiet = False
        self.progress = None
        
        self.analogy = {}
        # if self._auto_save is True, an auto_saving timer will save a temporary
        # file every 2 minutes
        self._auto_save = auto_save
        self.timer = None
        if self._auto_save:
            self.setup_timer()
        
        self._previous_graph_layout = None

        def width_f(text):
            return CurrentTheme.VERSION_FONT_METRIC.width(text)
        self._current_graph_layout = \
            VistrailsTreeLayoutLW(width_f, 
                                  CurrentTheme.VERSION_FONT_METRIC.height(), 
                                  CurrentTheme.VERSION_LABEL_MARGIN[0], 
                                  CurrentTheme.VERSION_LABEL_MARGIN[1])
        self.animate_layout = False
        #this was moved to BaseController
        #self.num_versions_always_shown = 1
        BaseController.__init__(self, vistrail, locator, abstractions, 
                                thumbnails, mashups, id_scope, set_log_on_vt, 
                                auto_save)

    def _get_current_pipeline_scene(self):
        return self.current_pipeline_view.scene()
    current_pipeline_scene = property(_get_current_pipeline_scene)

    # just need to switch current_pipeline_view to update controller to
    # new version and pipeline...
    def _get_current_version(self):
        if self.current_pipeline_view is None:
            return -1
        return self.current_pipeline_view.scene().current_version
    def _set_current_version(self, version):
        # print "set_current_version:", version, id(self.current_pipeline_view)
        if self.current_pipeline_view is not None:
            self.current_pipeline_view.scene().current_version = version
    current_version = property(_get_current_version, _set_current_version)

    def _get_current_pipeline(self):
        if self.current_pipeline_view is None:
            return None
        return self.current_pipeline_view.scene().current_pipeline
    def _set_current_pipeline(self, pipeline):
        if self.current_pipeline_view is not None:
            self.current_pipeline_view.scene().current_pipeline = pipeline
    current_pipeline = property(_get_current_pipeline, _set_current_pipeline)

    def set_pipeline_view(self, pipeline_view):
        if self.current_pipeline_view is not None:
            self.disconnect(self, QtCore.SIGNAL('versionWasChanged'),
                            self.current_pipeline_view.version_changed)
        self.current_pipeline_view = pipeline_view
        self.connect(self, QtCore.SIGNAL('versionWasChanged'),
                     self.current_pipeline_view.version_changed)
    
    def setup_timer(self):
        self.timer = QtCore.QTimer(self)
        self.connect(self.timer, QtCore.SIGNAL("timeout()"), self.write_temporary)
        self.timer.start(1000 * 60 * 2) # Save every two minutes
        
    def stop_timer(self):
        if self.timer:
            self.disconnect(self.timer, QtCore.SIGNAL("timeout()"), self.write_temporary)
            self.timer.stop()
            
    ##########################################################################
    # Signal vistrail relayout / redraw

    def replace_unnamed_node_in_version_tree(self, old_version, new_version):
        """method analogous to invalidate_version_tree but when only
        a single unnamed node and links need to be updated. Much faster."""
        self.reset_version_view = False
        try:
            self.emit(QtCore.SIGNAL('invalidateSingleNodeInVersionTree'),
                                    old_version, new_version)
        finally:
            self.reset_version_view = True

    def invalidate_version_tree(self, reset_version_view=True, animate_layout=False):
        """ invalidate_version_tree(reset_version_tree: bool, animate_layout: bool) -> None
        
        """
        self.reset_version_view = reset_version_view
        self.animate_layout = animate_layout
        #FIXME: in the future, rename the signal
        try:
            self.emit(QtCore.SIGNAL('vistrailChanged()'))
        finally:
            self.reset_version_view = True

    def has_move_actions(self):
        return self.current_pipeline_scene.hasMoveActions()

    def flush_move_actions(self):
        return self.current_pipeline_scene.flushMoveActions()

    ##########################################################################
    # Pipeline View Methods

    def updatePipelineScene(self):
        self.current_pipeline_scene.setupScene(self.current_pipeline)

    ##########################################################################
    # Autosave

    def enable_autosave(self):
        self._auto_save = True

    def disable_autosave(self):
        self._auto_save = False

    def get_locator(self):
        from vistrails.gui.application import get_vistrails_application
        if (self._auto_save and 
            get_vistrails_application().configuration.check('autoSave')):
            if self.locator is None:
                raise ValueError("locator is None")
            return self.locator
        else:
            return None

    def cleanup(self):
        locator = self.get_locator()
        if locator:
            locator.clean_temporaries()
        if self._auto_save or self.timer:
            self.stop_timer()
        # close associated mashup apps
        version_prop = QVersionProp.instance()
        for app in version_prop.versionMashups.apps.values():
            if app and app.view == self.vistrail_view:
                app.close()


    ##########################################################################
    # Actions, etc
    
    def perform_action(self, action, quiet=None):
        """ performAction(action: Action, quiet=None) -> timestep

        performs given action on current pipeline.

        quiet and self.quiet control invalidation of version
        tree. If quiet is set to any value, it overrides the field
        value self.quiet.

        If the value is True, then no invalidation happens (gui is not
        updated.)
        
        """
        if action is not None:
            BaseController.perform_action(self,action)

            if quiet is None:
                if not self.quiet:
                    self.invalidate_version_tree(False)
            else:
                if not quiet:
                    self.invalidate_version_tree(False)
            return action.db_id
        return None

    def add_new_action(self, action, description=None):
        """add_new_action(action) -> None

        Call this function to add a new action to the vistrail being
        controlled by the vistrailcontroller.

        FIXME: In the future, this function should watch the vistrail
        and get notified of the change.

        """
        if action is not None:
            BaseController.add_new_action(self, action, description)
            self.emit(QtCore.SIGNAL("new_action"), action)
            self.recompute_terse_graph()

    ##########################################################################

    def add_module(self, x, y, identifier, name, namespace='', 
                   internal_version=-1):
        return BaseController.add_module(self, identifier, name, namespace, x, y,
                                         internal_version)

    def create_abstraction_with_prompt(self, module_ids, connection_ids, 
                                       name=""):
        name = self.get_abstraction_name(name)
        if name is None:
            return
        return self.create_abstraction(module_ids, connection_ids, name)

    def update_notes(self, notes):
        """
        Parameters
        ----------

        - notes : 'string'
        
        """
        self.flush_delayed_actions()
        
        if self.vistrail.set_notes(self.current_version, str(notes)):
            self.emit(QtCore.SIGNAL('notesChanged()'))

    ##########################################################################
    # Workflow Execution
    
    def execute_workflow_list(self, vistrails):
        old_quiet = self.quiet
        self.quiet = True
        self.current_pipeline_scene.reset_module_colors()
        self.current_pipeline_scene.update()
        (results, changed) = BaseController.execute_workflow_list(self, 
                                                                  vistrails)        
        self.quiet = old_quiet
        if changed:
            self.invalidate_version_tree(False)
        return (results, changed)

    def execute_current_workflow(self, custom_aliases=None, custom_params=None,
                                 extra_info=None, reason='Pipeline Execution',
                                 sinks=None):
        """ execute_current_workflow() -> None
        Execute the current workflow (if exists)
        
        """
        self.flush_delayed_actions()
        if self.current_pipeline:
            locator = self.get_locator()
            if locator:
                locator.clean_temporaries()
                locator.save_temporary(self.vistrail)
            try:
                return self.execute_workflow_list([(self.locator,
                                             self.current_version,
                                             self.current_pipeline,
                                             self.current_pipeline_scene,
                                             custom_aliases,
                                             custom_params,
                                             reason,
                                             sinks,
                                             extra_info)])
            except Exception, e:
                debug.unexpected_exception(e)
                raise
        return ([], False)


    def execute_user_workflow(self, reason='Pipeline Execution', sinks=None):
        """ execute_user_workflow() -> None
        Execute the current workflow (if exists) and monitors it if it contains jobs
        
        """
        # reset job view
        from vistrails.gui.job_monitor import QJobView
        jobView = QJobView.instance()
        if jobView.updating_now:
            debug.critical("Execution Aborted: Job Monitor is updating. "
                           "Please wait a few seconds and try again.")
            return
        jobView.updating_now = True

        if not jobView.jobMonitor.currentWorkflow():
            version_id = self.current_version
            url = self.locator.to_url()
            # check if a job for this workflow exists
            current_workflow = None
            for job in jobView.jobMonitor._running_workflows.itervalues():
                try:
                    job_version = int(job.version)
                except ValueError:
                    job_version = self.vistrail.get_version_number(job.version)
                if version_id == job_version and url == job.vistrail:
                    current_workflow = job
                    jobView.jobMonitor.startWorkflow(job)
            if not current_workflow:
                current_workflow = JobWorkflow(url, version_id)
                jobView.jobMonitor.startWorkflow(current_workflow)
        try:
            self.progress = ExecutionProgressDialog(self.vistrail_view)
            self.progress.show()

            result =  self.execute_current_workflow(reason=reason, sinks=sinks)

            self.progress.setValue(100)
        finally:
            self.progress.hide()
            self.progress.deleteLater()
            self.progress = None
            jobView.jobMonitor.finishWorkflow()
            jobView.updating_now = False

        return result

    def enable_missing_package(self, identifier, deps):
        configuration = get_vistrails_configuration()
        if getattr(configuration, 'enablePackagesSilently', False):
            return True

        msg = "VisTrails needs to enable package '%s'." % identifier
        if len(deps) > 0:
            msg += (" This will also enable the dependencies: %s." 
                    " Do you want to enable these packages?" % (
                    ", ".join(deps),))
        else:
            msg += " Do you want to enable this package?"
        res = show_question('Enable package?',
                            msg,
                            [YES_BUTTON, NO_BUTTON], 
                            YES_BUTTON)
        if res == NO_BUTTON:
            return False
        return True

    def install_missing_package(self, identifier):
        res = show_question('Install package?',
                            "This pipeline contains a module"
                            " in package '%s', which"
                            " is not installed. Do you want to"
                            " install and enable that package?" % \
                                identifier, [YES_BUTTON, NO_BUTTON],
                            YES_BUTTON)
        return res == YES_BUTTON

    def change_selected_version(self, new_version, report_all_errors=True,
                                do_validate=True, from_root=False):
        """change_selected_version(new_version: int,
                                   report_all_errors: boolean,
                                   do_validate: boolean,
                                   from_root: boolean)

        Change the current vistrail version into new_version and emit a
        notification signal.

        NB: in most situations, the following post-condition holds:

        >>> controller.change_selected_version(v)
        >>> assert v == controller.current_version

        In some occasions, however, the controller will not be able to
        switch to the desired version. One example where this can
        happen is when the selected version has obsolete modules (that
        is, the currently installed package for those modules has
        module upgrades). In these cases, change_selected_version will
        return a new version which corresponds to a workflow that was
        created by the upgrading mechanism that packages can provide.
        
        """

        try:
            self.do_version_switch(new_version, report_all_errors,
                                   do_validate, from_root)
        except InvalidPipeline, e:
#            from vistrails.gui.application import get_vistrails_application
#
#             def process_err(err):
#                 if isinstance(err, Package.InitializationFailed):
#                     QtGui.QMessageBox.critical(
#                         get_vistrails_application().builderWindow,
#                         'Package load failed',
#                         'Package "%s" failed during initialization. '
#                         'Please contact the developer of that package '
#                         'and report a bug.' % err.package.name)
#                 elif isinstance(err, MissingPackage):
#                     QtGui.QMessageBox.critical(
#                         get_vistrails_application().builderWindow,
#                         'Unavailable package',
#                         'Cannot find package "%s" in\n'
#                         'list of available packages. \n'
#                         'Please install it first.' % err._identifier)
#                 elif issubclass(err.__class__, MissingPort):
#                     msg = ('Cannot find %s port "%s" for module "%s" '
#                            'in loaded package "%s". A different package '
#                            'version might be necessary.') % \
#                            (err._port_type, err._port_name, 
#                             err._module_name, err._package_name)
#                     QtGui.QMessageBox.critical(
#                         get_vistrails_application().builderWindow, 'Missing port',
#                         msg)
#                 else:
#                     QtGui.QMessageBox.critical(
#                         get_vistrails_application().builderWindow,
#                         'Invalid Pipeline', str(err))

            # VisTrails will not raise upgrade exceptions unless
            # configured to do so. To get the upgrade requests,
            # configuration option upgradeModules must be set to True.

            exception_set = e.get_exception_set()
            if len(exception_set) > 0:
#                msg_box = QtGui.QMessageBox(get_vistrails_application().builderWindow)
#                msg_box.setIcon(QtGui.QMessageBox.Warning)
#                msg_box.setText("The current workflow could not be validated.")
#                msg_box.setInformativeText("Errors occurred when trying to "
#                                           "construct this workflow.")
#                msg_box.setStandardButtons(QtGui.QMessageBox.Ok)
#                msg_box.setDefaultButton(QtGui.QMessageBox.Ok)
#                msg_box.setDetailedText(debug.format_exception(e))
#                msg_box.exec_()
                # text = "The current workflow could not be validated."
                # debug.critical(text, e)
                debug.critical("Error changing version", e)

#                 print 'got to exception set'
#                 # Process all errors as usual
#                 if report_all_errors:
#                     for exc in exception_set:
#                         print 'processing', exc
#                         process_err(exc)
#                 else:
#                     process_err(exception_set.__iter__().next())

        except Exception, e:
            import traceback
            debug.critical('Unexpected Exception',
                           traceback.format_exc())
        
        # FIXME: this code breaks undo/redo, and seems to be ok with normal
        # pipeline manipulations so I am leaving it commented out for now

        # if not self._current_terse_graph or \
        #         new_version not in self._current_terse_graph.vertices:
        #     self.recompute_terse_graph()

        self.emit(QtCore.SIGNAL('versionWasChanged'), self.current_version)

    def set_search(self, search, text=''):
        """ set_search(search: SearchStmt, text: str) -> None
        Change the currrent version tree search statement
        
        """
        if self.search != search or self.search_str != text:
            self.search = search
            self.search_str = text
            if self.search:
                self.search.run(self.vistrail, '')
                self.invalidate_version_tree(True)
            if self.refine:
                # need to recompute the graph because the refined items might
                # have changed since last time
                self.recompute_terse_graph()
                self.invalidate_version_tree(True)
            else:
                self.invalidate_version_tree(False)
            
            self.emit(QtCore.SIGNAL('searchChanged'))

    def set_refine(self, refine):
        """ set_refine(refine: bool) -> None
        Set the refine state to True or False
        
        """
        if self.refine!=refine:
            self.refine = refine
            # need to recompute the graph because the refined items might
            # have changed since last time
            self.recompute_terse_graph()
            self.invalidate_version_tree(True)

    def set_full_tree(self, full):
        """ set_full_tree(full: bool) -> None        
        Set if Vistrails should show a complete version tree or just a
        terse tree
        
        """
        if full != self.full_tree:
            self.full_tree = full
            self.invalidate_version_tree(True)

    def recompute_terse_graph(self):
        BaseController.recompute_terse_graph(self)
        self._previous_graph_layout = copy.deepcopy(self._current_graph_layout)
        self._current_graph_layout.layout_from(self.vistrail,
                                               self._current_terse_graph)

    def refine_graph(self, step=1.0):
        """ refine_graph(step: float in [0,1]) -> (Graph, Graph)        
        Refine the graph of the current vistrail based the search
        status of the controller. It also return the full graph as a
        reference
        
        """
        if self._current_full_graph is None:
            self.recompute_terse_graph()

        if not self.animate_layout:
            return (self._current_terse_graph, self._current_full_graph,
                    self._current_graph_layout)

        graph_layout = copy.deepcopy(self._current_graph_layout)
        terse_graph = copy.deepcopy(self._current_terse_graph)
        am = self.vistrail.actionMap
        step = 1.0/(1.0+math.exp(-(step*12-6))) # use a logistic sigmoid function
        
        # Adding nodes to tree
        for (c_id, c_node) in self._current_graph_layout.nodes.iteritems():
            if self._previous_graph_layout.nodes.has_key(c_id):
                p_node = self._previous_graph_layout.nodes[c_id]
            else: 
                p_id = c_id
                # Find closest child of contained in both graphs
                while not self._previous_graph_layout.nodes.has_key(p_id):
                    # Should always have exactly one child
                    p_id = [to for (to, _) in \
                                self._current_full_graph.adjacency_list[p_id]
                            if (to in am) and \
                                not self.vistrail.is_pruned(to)][0]
                p_node = self._previous_graph_layout.nodes[p_id]

            # Interpolate position
            x = p_node.p.x - c_node.p.x
            y = p_node.p.y - c_node.p.y
            graph_layout.move_node(c_id, x*(1.0-step), y*(1.0-step))
            
        # Removing nodes from tree
        for (p_id, p_node) in self._previous_graph_layout.nodes.iteritems():
            if not self._current_graph_layout.nodes.has_key(p_id):
                # Find closest parent contained in both graphs
                shared_parent = p_id
                while (shared_parent > 0 and 
                       shared_parent not in self._current_graph_layout.nodes):
                    shared_parent = \
                        self._current_full_graph.parent(shared_parent)

                # Find closest child contained in both graphs
                c_id = p_id
                while not self._current_graph_layout.nodes.has_key(c_id):
                    # Should always have exactly one child
                    c_id = [to for (to, _) in \
                                self._current_full_graph.adjacency_list[c_id]
                            if (to in am) and \
                                not self.vistrail.is_pruned(to)][0]
                    
                # Don't show edge that skips the disappearing nodes
                if terse_graph.has_edge(shared_parent, c_id):
                    terse_graph.delete_edge(shared_parent, c_id)

                # Add the disappearing node to the graph and layout
                c_node = copy.deepcopy(self._current_graph_layout.nodes[c_id])
                c_node.id = p_id
                graph_layout.add_node(p_id, c_node)
                terse_graph.add_vertex(p_id)
                p_parent = self._current_full_graph.parent(p_id)
                if not terse_graph.has_edge(p_id, p_parent):
                    terse_graph.add_edge(p_parent, p_id)
                p_child = p_id
                while p_child not in self._current_graph_layout.nodes:
                    # Should always have exactly one child
                    p_child = [to for (to, _) in \
                                   self._current_full_graph.adjacency_list[p_child]
                               if (to in am) and \
                                   not self.vistrail.is_pruned(to)][0]
                if not terse_graph.has_edge(p_id, p_child):
                    terse_graph.add_edge(p_id, p_child)

                # Interpolate position
                x = p_node.p.x - c_node.p.x
                y = p_node.p.y - c_node.p.y
                graph_layout.move_node(p_id, x*(1.0-step), y*(1.0-step))

        return (terse_graph, self._current_full_graph,
                graph_layout)

    ##########################################################################
    # undo/redo navigation

    def _change_version_short_hop(self, new_version):
        """_change_version_short_hop is used internally to
        change versions when we're moving exactly one action up or down.
        This allows a few optimizations that improve interactivity."""
        
        if self.current_version <> new_version:
            # Instead of recomputing the terse graph, simply update it

            # There are two variables in play:
            # a) whether or not the destination node is currently on the
            # terse tree (it will certainly be after the move)
            # b) whether or not the current node will be visible (it
            # certainly is now, since it's the current one)

            dest_node_in_terse_tree = new_version in self._current_terse_graph.vertices
            
            current = self.current_version
            tree = self.vistrail.tree.getVersionTree()
            # same logic as recompute_terse_graph except for current
            children_count = len([x for (x, _) in tree.adjacency_list[current]
                                  if (x in self.vistrail.actionMap and
                                      not self.vistrail.is_pruned(x))])
            current_node_will_be_visible = \
                (self.full_tree or
                 self.vistrail.has_tag(self.current_version) or
                 children_count <> 1)

            self.change_selected_version(new_version)
            # case 1:
            if not dest_node_in_terse_tree and \
                    not current_node_will_be_visible and not current == 0:
                # we're going from one boring node to another,
                # so just rename the node on the terse graph
                self._current_terse_graph.rename_vertex(current, new_version)
                self.replace_unnamed_node_in_version_tree(current, new_version)
            else:
                # bail, for now
                self.recompute_terse_graph()
                self.invalidate_version_tree(False)
        

    def show_parent_version(self):
        """ show_parent_version() -> None
        Go back one from the current version and display it

        """
        # NOTE cscheid: Slight change in the logic under refined views:
        # before r1185, undo would back up more than one action in the
        # presence of non-matching refined nodes. That seems wrong. Undo
        # should always move one step only.         

        prev = None
        try:
            prev = self._current_full_graph.parent(self.current_version)
        except Graph.VertexHasNoParentError:
            prev = 0

        self._change_version_short_hop(prev)

    def show_child_version(self, which_child):
        """ show_child_version(which_child: int) -> None
        Go forward one version and display it. This is used in redo.

        ONLY CALL THIS FUNCTION IF which_child IS A CHILD OF self.current_version

        """
        self._change_version_short_hop(which_child)
        

    def prune_versions(self, versions):
        """ prune_versions(versions: list of version numbers) -> None
        Prune all versions in 'versions' out of the view
        
        """
        # We need to go up-stream to the highest invisible node
        current = self._current_terse_graph
        if not current:
            (current, full, layout) = self.refine_graph()
        else:
            full = self._current_full_graph
        changed = False
        new_current_version = None
        for v in versions:
            if v!=0: # not root
                highest = v
                while True:
                    p = full.parent(highest)
                    if p==-1:
                        break
                    if p in current.vertices:
                        break
                    highest = p
                if highest!=0:
                    changed = True
                    if highest == self.current_version:
                        new_current_version = full.parent(highest)
                self.vistrail.pruneVersion(highest)
        if changed:
            self.set_changed(True)
        if new_current_version is not None:
            self.change_selected_version(new_current_version)
        self.recompute_terse_graph()
        self.invalidate_version_tree(False)

    def hide_versions_below(self, v=None):
        """ hide_versions_below(v: int) -> None
        Hide all versions including and below v
        
        """
        if v is None:
            v = self.current_version
        full = self.vistrail.getVersionGraph()
        x = [v]

        am = self.vistrail.actionMap

        changed = False

        while 1:
            try:
                current=x.pop()
            except IndexError:
                break

            children = [to for (to, _) in full.adjacency_list[current]
                        if (to in am) and \
                            not self.vistrail.is_pruned(to)]
            self.vistrail.hideVersion(current)
            changed = True

            for child in children:
                x.append(child)

        if changed:
            self.set_changed(True)
        self.recompute_terse_graph()
        self.invalidate_version_tree(False, False) 

    def show_all_versions(self):
        """ show_all_versions() -> None
        Unprune (graft?) all pruned versions

        """
        am = self.vistrail.actionMap
        for a in am.iterkeys():
            self.vistrail.showVersion(a)
        self.set_changed(True)
        self.recompute_terse_graph()
        self.invalidate_version_tree(False, False)

    def expand_versions(self, v1, v2):
        """ expand_versions(v1: int, v2: int) -> None
        Expand all versions between v1 and v2
        
        """
        full = self.vistrail.getVersionGraph()
        changed = False
        p = full.parent(v2)
        while p>v1:
            self.vistrail.expandVersion(p)
            changed = True
            p = full.parent(p)
        if changed:
            self.set_changed(True)
        self.recompute_terse_graph()
        self.invalidate_version_tree(False, True)

    def collapse_versions(self, v):
        """ collapse_versions(v: int) -> None
        Collapse all versions including and under version v until the next tag or branch
        
        """
        full = self.vistrail.getVersionGraph()
        x = [v]

        am = self.vistrail.actionMap
        tm = self.vistrail.get_tagMap()

        changed = False

        while 1:
            try:
                current=x.pop()
            except IndexError:
                break

            children = [to for (to, _) in full.adjacency_list[current]
                        if (to in am) and not self.vistrail.is_pruned(to)]
            if len(children) > 1:
                break;
            self.vistrail.collapseVersion(current)
            changed = True

            for child in children:
                if (not child in tm and  # has no Tag
                    child != self.current_version): # not selected
                    x.append(child)

        if changed:
            self.set_changed(True)
        self.recompute_terse_graph()
        self.invalidate_version_tree(False, True) 

    def expand_or_collapse_all_versions_below(self, v=None, expand=True):
        """ expand_or_collapse_all_versions_below(v: int) -> None
        Expand/Collapse all versions including and under version v
        
        """
        if v is None:
            v = self.current_version

        full = self.vistrail.getVersionGraph()
        x = [v]
        
        am = self.vistrail.actionMap

        changed = False

        while 1:
            try:
                current=x.pop()
            except IndexError:
                break

            children = [to for (to, _) in full.adjacency_list[current]
                        if (to in am) and not self.vistrail.is_pruned(to)]
            if expand:
                self.vistrail.expandVersion(current)
            else:
                self.vistrail.collapseVersion(current)
            changed = True

            for child in children:
                x.append(child)

        if changed:
            self.set_changed(True)
        self.recompute_terse_graph()
        self.invalidate_version_tree(False, True) 

    def expand_all_versions_below(self, v=None):
        self.expand_or_collapse_all_versions_below(v, True)

    def collapse_all_versions_below(self, v=None):
        self.expand_or_collapse_all_versions_below(v, False)

    def collapse_all_versions(self):
        """ collapse_all_versions() -> None
        Collapse all expanded versions

        """
        am = self.vistrail.actionMap
        for a in am.iterkeys():
            self.vistrail.collapseVersion(a)
        self.set_changed(True)
        self.recompute_terse_graph()
        self.invalidate_version_tree(False, True)

    def set_num_versions_always_shown(self, num):
        """ set_num_versions_always_shown(num: int) -> None

        """
        if num <> self.num_versions_always_shown:
            self.num_versions_always_shown = num
            self.set_changed(True)
            self.recompute_terse_graph()
            self.invalidate_version_tree(False)

    def setSavedQueries(self, queries):
        """ setSavedQueries(queries: list of (str, str, str)) -> None
        Set the saved queries of a vistail
        
        """
        self.vistrail.setSavedQueries(queries)
        self.set_changed(True)
        
    def update_current_tag(self,tag):
        """ update_current_tag(tag: str) -> Bool
        Update the current vistrail tag and return success predicate
        
        """
        self.flush_delayed_actions()
        try:
            if self.vistrail.hasTag(self.current_version):
                self.vistrail.changeTag(tag, self.current_version)
            else:
                self.vistrail.addTag(tag, self.current_version)
        except TagExists:
            show_warning('Name Exists',
                         "There is already another version named '%s'.\n"
                         "Please enter a different one." % tag)
            return False
        self.set_changed(True)
        self.recompute_terse_graph()
        self.invalidate_version_tree(False)
        return True

    def perform_param_changes(self, actions):
        """perform_param_changes(actions) -> None

        Performs a series of parameter change actions to the current version.

        FIXME: this function seems to be called from a single place in
        the spreadsheet cell code. Do we need it?
        """
        if len(actions) == 0:
            return
        for action in actions:
            for operation in action.operations:
                if operation.vtType == 'add' or operation.vtType == 'change':
                    if operation.new_obj_id < 0:
                        data = operation.data
                        new_id = self.vistrail.idScope.getNewId(data.vtType)
                        data.real_id = new_id
                        operation.new_obj_id = new_id
            self.add_new_action(action)
            self.perform_action(action, quiet=True)
        self.set_changed(True)
        self.invalidate_version_tree(False)

    def get_pipeline_name(self, version=None):
        if version == None:
            version = self.current_version
        return self.vistrail.get_pipeline_name(version)

    ###########################################################################
    # Clipboard, copy/paste

    def get_selected_item_ids(self):
        return self.current_pipeline_scene.get_selected_item_ids()

    def copy_modules_and_connections(self, module_ids, connection_ids):
        """copy_modules_and_connections(module_ids: [long],
                                     connection_ids: [long]) -> str
        Serializes a list of modules and connections
        """
        self.flush_delayed_actions()

        def process_group(group):
            # reset pipeline id for db
            group.pipeline.id = None
            # recurse
            for module in group.pipeline.module_list:
                if module.is_group():
                    process_group(module)

        pipeline = Pipeline()
        sum_x = 0.0
        sum_y = 0.0
        for module_id in module_ids:
            module = self.current_pipeline.modules[module_id]
            sum_x += module.location.x
            sum_y += module.location.y
            if module.is_group():
                process_group(module)

        center_x = sum_x / len(module_ids)
        center_y = sum_y / len(module_ids)
        for module_id in module_ids:
            module = self.current_pipeline.modules[module_id]
            module = module.do_copy()
            module.location.x -= center_x
            module.location.y -= center_y
            pipeline.add_module(module)
        for connection_id in connection_ids:
            connection = self.current_pipeline.connections[connection_id]
            pipeline.add_connection(connection)
        return vistrails.core.db.io.serialize(pipeline)
        
    def paste_modules_and_connections(self, str, center):
        """ paste_modules_and_connections(str,
                                          center: (float, float)) -> [id list]
        Paste a list of modules and connections into the current pipeline.

        Returns the list of module ids of added modules

        """
        def remove_duplicate_aliases(pip):
            aliases = self.current_pipeline.aliases.keys()
            for a in aliases:
                if a in pip.aliases:
                    (type, oId, parentType, parentId, mid) = pip.aliases[a]
                    pip.remove_alias_by_name(a)
                    _mod = pip.modules[mid]
                    _fun = _mod.function_idx[parentId]
                    _par = _fun.parameter_idx[oId]
                    _par.alias = ''
                                    
        self.flush_delayed_actions()
        pipeline = vistrails.core.db.io.unserialize(str, Pipeline)
        remove_duplicate_aliases(pipeline)

        modules = []
        if pipeline:
            def process_group(group):
                # reset pipeline id for db
                group.pipeline.id = None
                # recurse
                for module in group.pipeline.module_list:
                    if module.is_group():
                        process_group(module)

            for module in pipeline.module_list:
                module.location.x += center[0]
                module.location.y += center[1]
                if module.is_group():
                    process_group(module)

            id_remap = {}
            action = vistrails.core.db.action.create_paste_action(pipeline, 
                                                        self.vistrail.idScope,
                                                        id_remap)

            modules = [op.objectId
                       for op in action.operations
                       if (op.what == 'module' or 
                           op.what == 'abstraction' or
                           op.what == 'group')]

            self.add_new_action(action)
            self.vistrail.change_description("Paste", action.id)
            self.perform_action(action)
            self.validate(self.current_pipeline, False)
        return modules

    def get_abstraction_name(self, name="", check_exists=True):
        name = self.do_abstraction_prompt(name)
        if name is None:
            return None
        while name == "" or (check_exists and self.abstraction_exists(name)):
            name = self.do_abstraction_prompt(name, name != "")
            if name is None:
                return None
        return name

    def do_abstraction_prompt(self, name="", exists=False):
        if exists:
            prompt = "'%s' already exists.  Enter a new subworkflow name" % \
                name
        else:
            prompt = 'Enter subworkflow name'
            
        (text, ok) = QtGui.QInputDialog.getText(None, 
                                                'Set SubWorkflow Name',
                                                prompt,
                                                QtGui.QLineEdit.Normal,
                                                name)
        if ok and text:
            return str(text).strip().rstrip()
        if not ok:
            return None
        return ""

    def import_abstractions(self, abstraction_ids):
        for abstraction_id in abstraction_ids:
            abstraction = self.current_pipeline.modules[abstraction_id]
            new_name = self.get_abstraction_name(abstraction.name)
            if new_name:
                self.import_abstraction(new_name,
                                        abstraction.package,
                                        abstraction.name, 
                                        abstraction.namespace,
                                        abstraction.internal_version)
        
    def do_export_prompt(self, title, prompt):
        (text, ok) = QtGui.QInputDialog.getText(None,
                                                title,
                                                prompt,
                                                QtGui.QLineEdit.Normal,
                                                '')
        if ok and not text:
            return str(text).strip().rstrip()
        return ''
            
    def do_save_dir_prompt(self):
        dialog = QtGui.QFileDialog.getExistingDirectory
        dir_name = dialog(None, "Save Subworkflows...",
                          vistrails.core.system.vistrails_file_directory())
        if dir_name:
            return None
        dir_name = os.path.abspath(str(dir_name))
        setattr(get_vistrails_configuration(), 'fileDir', dir_name)
        vistrails.core.system.set_vistrails_file_directory(dir_name)
        return dir_name
    
    def export_abstractions(self, abstraction_ids):
        save_dir = self.do_save_dir_prompt()
        if not save_dir:
            return 

        def read_init(dir_name):
            import imp
            found_attrs = {}
            found_lists = {}
            attrs = ['identifier', 'name', 'version']
            lists = ['_subworkflows', '_dependencies']
            try:
                (file, pathname, description) = \
                    imp.find_module(os.path.basename(dir_name), 
                                    [os.path.dirname(dir_name)])
                module = imp.load_module(os.path.basename(dir_name), file,
                                         pathname, description)
                for attr in attrs:
                    if hasattr(module, attr):
                        found_attrs[attr] = getattr(module, attr)
                for attr in lists:
                    if hasattr(module, attr):
                        found_lists[attr] = getattr(module, attr)
            except Exception, e:
                debug.critical("Exception: %s" % e)
                pass
            return (found_attrs, found_lists)

        def write_init(save_dir, found_attrs, found_lists, attrs, lists):
            init_file = os.path.join(save_dir, '__init__.py')
            if os.path.exists(init_file):
                f = open(init_file, 'a')
            else:
                f = open(init_file, 'w')
            for attr, val in attrs.iteritems():
                if attr not in found_attrs:
                    print >>f, "%s = '%s'" % (attr, val)
            for attr, val_list in lists.iteritems():
                if attr not in found_lists:
                    print >>f, "%s = %s" % (attr, str(val_list))
                else:
                    diff_list = []
                    for val in val_list:
                        if val not in found_lists[attr]:
                            diff_list.append(val)
                    print >>f, '%s.extend(%s)' % (attr, str(diff_list))
            f.close()

        if os.path.exists(os.path.join(save_dir, '__init__.py')):
            (found_attrs, found_lists) = read_init(save_dir)
        else:
            found_attrs = {}
            found_lists = {}

        if 'name' in found_attrs:
            pkg_name = found_attrs['name']
        else:
            pkg_name = self.do_export_prompt("Target Package Name",
                                             "Enter target package name")
            if not pkg_name:
                return

        if 'identifier' in found_attrs:
            pkg_identifier = found_attrs['identifier']
        else:
            pkg_identifier = self.do_export_prompt("Target Package Identifier",
                                                   "Enter target package "
                                                   "identifier (e.g. "
                                                   "org.place.user.package)")
            if not pkg_identifier:
                return

        abstractions = []
        for abstraction_id in abstraction_ids:
            abstraction = self.current_pipeline.modules[abstraction_id]
            if abstraction.is_abstraction() and \
                    abstraction.package == abstraction_pkg:
                abstractions.append(abstraction)
                [abstractions.extend(v) for v in self.find_abstractions(abstraction.vistrail).itervalues()]
        pkg_subworkflows = []
        pkg_dependencies = set()
        for abstraction in abstractions:
            new_name = self.get_abstraction_name(abstraction.name, False)
            if not new_name:
                break
            (subworkflow, dependencies) = \
                self.export_abstraction(new_name,
                                        pkg_identifier,
                                        save_dir,
                                        abstraction.package,
                                        abstraction.name, 
                                        abstraction.namespace,
                                        str(abstraction.internal_version))
            pkg_subworkflows.append(subworkflow)
            pkg_dependencies.update(dependencies)

        attrs = {'identifier': pkg_identifier,
                 'name': pkg_name,
                 'version': '0.0.1'}
        lists = {'_subworkflows': pkg_subworkflows,
                 '_dependencies': list(pkg_dependencies)}
        write_init(save_dir, found_attrs, found_lists, attrs, lists)

    def set_changed(self, changed):
        """ set_changed(changed: bool) -> None
        Set the current state of changed and emit signal accordingly
        
        """
        BaseController.set_changed(self, changed)
        if changed:
            # FIXME: emit different signal in the future
            self.emit(QtCore.SIGNAL('stateChanged'))

    def set_file_name(self, file_name):
        """ set_file_name(file_name: str) -> None
        Change the controller file name
        
        """
        old_name = self.file_name
        BaseController.set_file_name(self, file_name)
        if old_name!=file_name:
            self.emit(QtCore.SIGNAL('stateChanged'))

    def write_vistrail(self, locator, version=None, export=False):
        need_invalidate = BaseController.write_vistrail(self, locator,
                                                        version, export)
        if need_invalidate and not export:
            self.invalidate_version_tree(False)
            self.set_changed(False)

    def write_opm(self, locator):
        if self.log:
            if self.vistrail.db_log_filename is not None:
                log = vistrails.core.db.io.merge_logs(self.log, 
                                            self.vistrail.db_log_filename)
            else:
                log = self.log
            opm_graph = OpmGraph(log=log, 
                                 version=self.current_version,
                                 workflow=self.current_pipeline,
                                 registry=get_module_registry())
            locator.save_as(opm_graph)
            
    def write_prov(self, locator):
        if self.log:
            if self.vistrail.db_log_filename is not None:
                log = vistrails.core.db.io.merge_logs(self.log, 
                                            self.vistrail.db_log_filename)
            else:
                log = self.log
            prov_document = ProvDocument(log=log, 
                                         version=self.current_version,
                                         workflow=self.current_pipeline,
                                         registry=get_module_registry())
            locator.save_as(prov_document)

    def query_by_example(self, pipeline):
        """ query_by_example(pipeline: Pipeline) -> None
        Perform visual query on the current vistrail
        
        """
        if len(pipeline.modules)==0:
            search = TrueSearch()
        else:
            if not self._current_terse_graph:
                self.recompute_terse_graph()
            versions_to_check = \
                set(self._current_terse_graph.vertices.iterkeys())
            search = VisualQuery(pipeline, versions_to_check)

        self.set_search(search, '') # pipeline.dump_to_string())

    ##########################################################################
    # analogies

    def add_analogy(self, analogy_name, version_from, version_to):
        assert isinstance(analogy_name, str)
        assert isinstance(version_from, (int, long))
        assert isinstance(version_to, (int, long))
        if analogy_name in self.analogy:
            raise VistrailsInternalError("duplicated analogy name '%s'" %
                                         analogy_name)
        self.analogy[analogy_name] = (version_from, version_to)

    def remove_analogy(self, analogy_name):
        if analogy_name not in self.analogy:
            raise VistrailsInternalError("missing analogy '%s'" %
                                         analogy_name)
        del self.analogy[analogy_name]

    def perform_analogy(self, analogy_name, analogy_target):
        if analogy_name not in self.analogy:
            raise VistrailsInternalError("missing analogy '%s'" %
                                         analogy_name)

        # remove delayed actions since we're not necessarily using
        # current_version
        self._delayed_actions = []

        (a, b) = self.analogy[analogy_name]
        c = analogy_target
        if self.current_version != c:
            self.change_selected_version(c)

        try:
            pipeline_a = self.vistrail.getPipeline(a)
            self.validate(pipeline_a)
        except InvalidPipeline, e:
            (_, pipeline_a) = \
                self.handle_invalid_pipeline(e, a, Vistrail())
            self._delayed_actions = []
        try:
            pipeline_c = self.vistrail.getPipeline(c)
            self.validate(pipeline_c)
        except InvalidPipeline, e:
            (_, pipeline_c) = self.handle_invalid_pipeline(e, a, Vistrail())
            self._delayed_actions = []
                                                     
        action = vistrails.core.analogy.perform_analogy_on_vistrail(self.vistrail,
                                                          a, b, c, 
                                                          pipeline_a,
                                                          pipeline_c)
        self.add_new_action(action)
        self.vistrail.change_description("Analogy", action.id)
        self.vistrail.change_analogy_info("(%s -> %s)(%s)" % (a, b, c), 
                                          action.id)
        
        # make sure that the output from the analogy is as up-to-date
        # as we can make it
        self.change_selected_version(action.id, from_root=True)
        self.flush_delayed_actions()
        self.invalidate_version_tree()
        
    def executeParameterExploration(self, pe, view=None, extra_info={}, showProgress=True):
        """ execute(pe: ParameterExploration, view: QVistrailView,
            extra_info: dict, showProgress: bool) -> None
        Perform the exploration by collecting a list of actions
        corresponding to each dimension
        
        """
        reg = get_module_registry()
        spreadsheet_pkg = '%s.spreadsheet' % \
                vistrails.core.system.get_vistrails_default_pkg_prefix()
        use_spreadsheet = reg.has_module(spreadsheet_pkg, 'CellLocation') and\
                          reg.has_module(spreadsheet_pkg, 'SheetReference')

        if pe.action_id != self.current_version:
            self.change_selected_version(pe.action_id)
        actions, pre_actions, vistrail_vars = \
                        pe.collectParameterActions(self.current_pipeline)

        if self.current_pipeline and actions:
            pe_log_id = uuid.uuid1()
            explorer = ActionBasedParameterExploration()
            (pipelines, performedActions) = explorer.explore(
                self.current_pipeline, actions, pre_actions)
            
            dim = [max(1, len(a)) for a in actions]
            if use_spreadsheet:
                from vistrails.gui.paramexplore.virtual_cell import positionPipelines, assembleThumbnails
                from vistrails.gui.paramexplore.pe_view import QParamExploreView
                modifiedPipelines, pipelinePositions = positionPipelines(
                    'PE#%d %s' % (QParamExploreView.explorationId, self.name),
                    dim[2], dim[1], dim[0], pipelines, pe.layout, self)
                QParamExploreView.explorationId += 1
            else:
                from vistrails.core.param_explore import _pipelinePositions
                modifiedPipelines = pipelines
                pipelinePositions = _pipelinePositions(
                    dim[2], dim[1], dim[0], pipelines)

            mCount = []
            for p in modifiedPipelines:
                if len(mCount)==0:
                    mCount.append(0)
                else:
                    mCount.append(len(p.modules)+mCount[len(mCount)-1])
                
            # Now execute the pipelines
            if showProgress:
                totalProgress = sum([len(p.modules) for p in modifiedPipelines])
                progress = QtGui.QProgressDialog('Performing Parameter '
                                                 'Exploration...',
                                                 '&Cancel',
                                                 0, totalProgress)
                progress.setWindowTitle('Parameter Exploration')
                progress.setWindowModality(QtCore.Qt.WindowModal)
                progress.show()

            interpreter = get_default_interpreter()
            
            images = {}
            errors = []
            for pi in xrange(len(modifiedPipelines)):
                if showProgress:
                    progress.setValue(mCount[pi])
                    QtCore.QCoreApplication.processEvents()
                    if progress.wasCanceled():
                        break
                    def moduleExecuted(objId):
                        if not progress.wasCanceled():
                            progress.setValue(progress.value()+1)
                            QtCore.QCoreApplication.processEvents()
                if use_spreadsheet:
                    name = os.path.splitext(self.name)[0] + \
                                         ("_%s_%s_%s" % pipelinePositions[pi])
                    extra_info['nameDumpCells'] = name
                    if 'pathDumpCells' in extra_info:
                        images[pipelinePositions[pi]] = \
                                   os.path.join(extra_info['pathDumpCells'], name)
                pe_cell_id = (pe_log_id,) + pipelinePositions[pi]
                kwargs = {'locator': self.locator,
                          'current_version': self.current_version,
                          'reason': 'Parameter Exploration %s %s_%s_%s' % pe_cell_id,
                          'logger': self.get_logger(),
                          'actions': performedActions[pi],
                          'extra_info': extra_info
                          }
                if view:
                    kwargs['view'] = view
                if showProgress:
                    kwargs['module_executed_hook'] = [moduleExecuted]
                if self.get_vistrail_variables():
                    # remove vars used in pe
                    vars = dict([(v.uuid, v) for v in self.get_vistrail_variables()
                            if v.uuid not in vistrail_vars])
                    kwargs['vistrail_variables'] = lambda x: vars.get(x, None)
                result = interpreter.execute(modifiedPipelines[pi], **kwargs)
                for error in result.errors.itervalues():
                    if use_spreadsheet:
                        pp = pipelinePositions[pi]
                        errors.append(((pp[1], pp[0], pp[2]), error))
                    else:
                        errors.append(((0,0,0), error))

            if showProgress:
                progress.setValue(totalProgress)
            if 'pathDumpCells' in extra_info:
                filename = os.path.join(extra_info['pathDumpCells'],
                                        os.path.splitext(self.name)[0])
                assembleThumbnails(images, filename)
            from vistrails.gui.vistrails_window import _app
            _app.notify('execution_updated')
            return errors

################################################################################
# Testing


class TestVistrailController(vistrails.gui.utils.TestVisTrailsGUI):

    # def test_add_module(self):
    #     v = api.new_vistrail()
       
    def tearDown(self):
        vistrails.gui.utils.TestVisTrailsGUI.tearDown(self)

        d = vistrails.core.system.get_vistrails_directory('subworkflowsDir')
        filename = os.path.join(d, '__TestFloatList.xml')
        if os.path.exists(filename):
            os.remove(filename)

    def test_create_functions(self):
        controller = VistrailController(Vistrail(), None, 
                                        pipeline_view=DummyView(),
                                        auto_save=False)
        controller.change_selected_version(0L)
        module = controller.add_module(0.0,0.0, 
                        vistrails.core.system.get_vistrails_basic_pkg_id(), 
                        'ConcatenateString')
        functions = [('str1', ['foo'], -1, True),
                     ('str2', ['bar'], -1, True)]
        controller.update_functions(module, functions)

        self.assertEquals(len(controller.current_pipeline.module_list), 1)
        p_module = controller.current_pipeline.modules[module.id]
        self.assertEquals(len(p_module.functions), 2)
        self.assertEquals(p_module.functions[0].params[0].strValue, 'foo')
        self.assertEquals(p_module.functions[1].params[0].strValue, 'bar')

        # make sure updates work correctly
        # also check that we can add more than one function w/ same name
        # by passing False as should_replace
        new_functions = [('str1', ['baz'], -1, True),
                         ('str2', ['foo'], -1, False),
                         ('str3', ['bar'], -1, False)]
        controller.update_functions(p_module, new_functions)
        self.assertEquals(len(p_module.functions), 4)

    def test_abstraction_create(self):
        from vistrails.core.db.locator import XMLFileLocator
        d = vistrails.core.system.get_vistrails_directory('subworkflowsDir')
        filename = os.path.join(d, '__TestFloatList.xml')
        locator = XMLFileLocator(vistrails.core.system.vistrails_root_directory() +
                           '/tests/resources/test_abstraction.xml')
        v = locator.load()
        controller = VistrailController(v, locator, pipeline_view=DummyView(),
                                        auto_save=False)
        # DAK: version is different because of upgrades
        # controller.change_selected_version(9L)
        controller.select_latest_version()
        self.assertNotEqual(controller.current_pipeline, None)

        # If getting a KeyError here, run the upgrade on the vistrail and
        # update the ids
        # TODO : rewrite test so we don't have to update this unrelated code
        # each time new upgrades are introduced
        # Original ids:
        #     module_ids = [1, 2, 3]
        #     connection_ids = [1, 2, 3]
        module_ids = [15, 13, 14]
        connection_ids = [21, 18, 20]
        controller.create_abstraction(module_ids, connection_ids,
                                      '__TestFloatList')
        self.assert_(os.path.exists(filename))

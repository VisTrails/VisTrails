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

from gui.application import VistrailsApplication
_app = VistrailsApplication

##############################################################################
# Exceptions

class NoVistrail(Exception):
    pass

class NoGUI(Exception):
    pass

##############################################################################

def switch_to_pipeline_view():
    """switch_to_pipeline_view():

    Changes current viewing mode to pipeline view in the builder window.

    """
    _app.builderWindow.viewModeChanged(0)

def switch_to_history_view():
    """switch_to_history_view():

    Changes current viewing mode to history view in the builder window.

    """
    _app.builderWindow.viewModeChanged(1)

def switch_to_query_view():
    """switch_to_query_view():

    Changes current viewing mode to query view in the builder window.

    """
    _app.builderWindow.viewModeChanged(2)

################################################################################
# Access to current state

def get_builder_window():
    """get_builder_window():

    returns the main VisTrails GUI window

    raises NoGUI.

    """
    try:
        return _app.builderWindow
    except AttributeError:
        raise NoGUI
    
def get_current_controller():
    """get_current_controller():

    returns the VistrailController of the currently selected vistrail.

    raises NoVistrail.

    """
    try:
        return get_builder_window().viewManager.currentWidget().controller
    except AttributeError:
        raise NoVistrail

def get_current_vistrail():
    """get_current_vistrail():

    Returns the currently selected vistrail.

    """
    return get_current_controller().vistrail

def get_current_vistrail_view():
    """get_current_vistrail():

    Returns the currently selected vistrail view.

    """
    return get_current_controller().vistrail_view

def close_current_vistrail(quiet=False):
    get_builder_window().viewManager.closeVistrail(get_current_vistrail_view())

def get_module_registry():
    from core.modules.module_registry import get_module_registry
    return get_module_registry()

##############################################################################
# Do things

def add_module(x, y, identifier, name, namespace, controller=None):
    if controller is None:
        controller = get_current_controller()
    result = controller.add_module(x, y, identifier, name, namespace)
    controller.current_pipeline_view.setupScene(controller.current_pipeline)
    result = controller.current_pipeline.modules[result.id]
    return result
    
def add_module_from_descriptor(descriptor, x=0.0, y=0.0, 
                               internal_version=-1, controller=None):
    if controller is None:
        controller = get_current_controller()
    result = controller.add_module_from_descriptor(descriptor, x, y, 
                                                   internal_version)
    controller.current_pipeline_view.setupScene(controller.current_pipeline)
    result = controller.current_pipeline.modules[result.id]
    return result
    
def add_connection(output_id, output_port_spec, input_id, input_port_spec, 
                   controller=None):
    if controller is None:
        controller = get_current_controller()
    result = controller.add_connection(output_id, output_port_spec,
                                       input_id, input_port_spec)
    controller.current_pipeline_view.setupScene(controller.current_pipeline)
    result = controller.current_pipeline.connections[result.id]
    return result

def create_group(module_ids, connection_ids, controller=None):
    if controller is None:
        controller = get_current_controller()
    controller.create_group(module_ids, connection_ids)
    controller.current_pipeline_view.setupScene(controller.current_pipeline)

def get_modules_by_name(name, package=None, namespace=None, controller=None):
    if controller is None:
        controller = get_current_controller()
    res = []
    for module in controller.current_pipeline.modules.itervalues():
        if (module.name == name and
            (package is None or module.package == package) and
            (namespace is None or module.namespace == namespace)):
            res.append(module)
    return res

def get_selected_modules(controller=None):
    if controller is None:
        controller = get_current_controller()
    modules = []
    for m_id in controller.get_selected_item_ids()[0]:
        modules.append(controller.current_pipeline.modules[m_id])
    return modules
    
def change_parameter(module_id, function_name, param_list, function_id=-1L,
                     alias_list=[], controller=None):
    """change_parameter(module_id: long, 
                        function_name: str, 
                        param_list: list(str),
                        function_id: long,
                        alias_list: list(str),
                        controller: VistrailController,
                        ) -> None
    Note: param_list is a list of strings no matter what the parameter type!
    Note: alias_list will be REMOVED!!
    """
    if controller is None:
        controller = get_current_controller()
    module = controller.current_pipeline.modules[module_id]
    controller.update_function(module, function_name, param_list, function_id, 
                               alias_list)
    controller.current_pipeline_view.setupScene(controller.current_pipeline)

def change_parameter_by_id(module_id, function_id, old_param_id, new_value, 
                           controller=None):
    """change_parameter_by_id(module_id: long,
                             function_id: long,
                             old_param_id: long,
                             new_value: str,
                             controller: VistrailController) -> long
    Returns the id of the new parameter.
    Note: function_id is the real_id! Use f.real_id to access real_id
    Note: old_param_id is the real_id! Use p.real_id to access real_id
    """
    if controller is None:
        controller = get_current_controller()
    module = controller.current_pipeline.modules[module_id]
    function = module.function_idx[function_id]
    pos = function.parameter_idx[old_param_id].pos
    controller.update_parameter(function, old_param_id, new_value)
    controller.current_pipeline_view.setupScene(controller.current_pipeline)
    return function.params[pos].real_id

def change_parameter_by_pos(module_id, function_pos, old_param_pos, new_value,
                            controller=None):
    """change_parameter_by_id(module_id: long,
                             function_pos: int,
                             old_param_pos: int,
                             new_value: str,
                             controller: VistrailController) -> long
    Returns the id of the new parameter.
    """
    if controller is None:
        controller = get_current_controller()
    module = controller.current_pipeline.modules[module_id]
    function = module.functions[function_pos]
    old_param_id = function.params[old_param_pos].real_id
    controller.update_parameter(function, old_param_id, new_value)
    controller.current_pipeline_view.setupScene(controller.current_pipeline)
    return function.params[old_param_pos].real_id

def add_port_spec(module_id, port_spec, controller=None):
    if controller is None:
        controller = get_current_controller()
    # module = controller.current_pipeline.modules[module_id]
    controller.add_module_port(module_id, (port_spec.type, port_spec.name,
                                           port_spec.sigstring))
    controller.current_pipeline_view.setupScene(controller.current_pipeline)

##############################################################################

def select_version(version, ctrl=None):
    """select_version(int or str, ctrl=None):

    Given an integer, selects a version with the given number from the
    given vistrail (or the current one if no controller is given).

    Given a string, selects a version with that tag.

    """
    if ctrl is None:
        ctrl = get_current_controller()
    vistrail = ctrl.vistrail
    if type(version) == str:
        version = vistrail.get_tag_str(version).action_id
    ctrl.change_selected_version(version)
    ctrl.invalidate_version_tree(False)

def undo():
    get_current_vistrail_view().undo()

def redo():
    get_current_vistrail_view().redo()

def get_available_versions():
    """get_available_version(): ([int], {int: str})

    From the currently selected vistrail, return all available
    versions and the existing tags.

    """
    ctrl = get_current_controller()
    vistrail = ctrl.vistrail
    return (vistrail.actionMap.keys(), vistrail.get_tagMap())

def open_vistrail_from_file(filename):
    from core.db.locator import FileLocator

    f = FileLocator(filename)
    
    manager = get_builder_window().viewManager
    view = manager.open_vistrail(f)
    return view

def close_vistrail(view, quiet=True):
    get_builder_window().viewManager.closeVistrail(view, quiet=quiet)

def new_vistrail():
    # Returns VistrailView - remember to be consistent about it..
    result = _app.builderWindow.viewManager.newVistrail(False)
    return result

##############################################################################
# Testing

import unittest
import copy
import random
import gui.utils

class TestAPI(gui.utils.TestVisTrailsGUI):

    def test_close_current_vistrail_no_vistrail(self):
        self.assertRaises(NoVistrail, lambda: get_current_vistrail_view())

    def test_new_vistrail_no_save(self):
        v = new_vistrail()
        import gui.vistrail_view
        assert isinstance(v, gui.vistrail_view.QVistrailView)
        assert not v.controller.changed
        close_vistrail(v)

    def test_new_vistrail_button_states(self):
        assert _app.builderWindow.newVistrailAction.isEnabled()
        assert not _app.builderWindow.closeVistrailAction.isEnabled()
        assert not _app.builderWindow.saveFileAction.isEnabled()
        assert not _app.builderWindow.saveFileAsAction.isEnabled()
        new_vistrail()
        assert _app.builderWindow.newVistrailAction.isEnabled()
        assert _app.builderWindow.closeVistrailAction.isEnabled()
        assert _app.builderWindow.saveFileAction.isEnabled()
        assert _app.builderWindow.saveFileAsAction.isEnabled()

    
    
    

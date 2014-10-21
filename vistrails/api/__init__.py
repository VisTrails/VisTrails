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
from vistrails.gui.application import get_vistrails_application

import unittest
import copy
import random
import vistrails.gui.utils

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
    get_vistrails_application().builderWindow.qactions['pipeline'].trigger()

def switch_to_history_view():
    """switch_to_history_view():

    Changes current viewing mode to history view in the builder window.

    """
    get_vistrails_application().builderWindow.qactions['history'].trigger()
    
def switch_to_query_view():
    """switch_to_query_view():

    Changes current viewing mode to query view in the builder window.

    """
    get_vistrails_application().builderWindow.qactions['search'].trigger()

def switch_to_mashup_view():
    """switch_to_mashup_view():

    Changes current viewing mode to mashup view in the builder window.

    """
    get_vistrails_application().builderWindow.qactions['mashup'].trigger()
 
################################################################################
# Access to current state

def get_builder_window():
    """get_builder_window():

    returns the main VisTrails GUI window

    raises NoGUI.

    """
    try:
        return get_vistrails_application().builderWindow
    except AttributeError:
        raise NoGUI
    
def get_current_controller():
    """get_current_controller():

    returns the VistrailController of the currently selected vistrail.

    raises NoVistrail.

    """
    try:
        return get_vistrails_application().builderWindow.get_current_controller()
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
    view = get_vistrails_application().builderWindow.get_current_view()
    if view is None:
        raise NoVistrail
    return view    

def close_current_vistrail(quiet=False):
    get_vistrails_application().builderWindow.close_vistrail(get_current_vistrail_view())

def get_module_registry():
    from vistrails.core.modules.module_registry import get_module_registry
    return get_module_registry()

##############################################################################
# Do things

def add_module(x, y, identifier, name, namespace, controller=None):
    if controller is None:
        controller = get_current_controller()
    if controller.current_version==-1:
        controller.change_selected_version(0)
    result = controller.add_module(x, y, identifier, name, namespace)
    controller.updatePipelineScene()
    result = controller.current_pipeline.modules[result.id]
    return result
    
def add_module_from_descriptor(descriptor, x=0.0, y=0.0, 
                               internal_version=-1, controller=None):
    if controller is None:
        controller = get_current_controller()
    if controller.current_version==-1:
        controller.change_selected_version(0)
    result = controller.add_module_from_descriptor(descriptor, x, y, 
                                                   internal_version)
    controller.updatePipelineScene()
    result = controller.current_pipeline.modules[result.id]
    return result
    
def add_connection(output_id, output_port_spec, input_id, input_port_spec, 
                   controller=None):
    if controller is None:
        controller = get_current_controller()
    result = controller.add_connection(output_id, output_port_spec,
                                       input_id, input_port_spec)
    controller.updatePipelineScene()
    result = controller.current_pipeline.connections[result.id]
    return result

def create_group(module_ids, connection_ids, controller=None):
    if controller is None:
        controller = get_current_controller()
    group = controller.create_group(module_ids, connection_ids)
    controller.updatePipelineScene()
    return group

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
    selected = controller.get_selected_item_ids()
    if selected is None:
        return []
    (sel_module_ids, sel_connection_ids) = selected
    for m_id in sel_module_ids:
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
    controller.updatePipelineScene()

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
    controller.updatePipelineScene()
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
    controller.updatePipelineScene()
    return function.params[old_param_pos].real_id

def add_port_spec(module_id, port_spec, controller=None):
    if controller is None:
        controller = get_current_controller()
    # module = controller.current_pipeline.modules[module_id]
    controller.add_module_port(module_id, (port_spec.type, port_spec.name,
                                           port_spec.sigstring))
    controller.updatePipelineScene()

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
    if isinstance(version, str):
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
    from vistrails.core.db.locator import FileLocator

    f = FileLocator(filename)
    view = get_builder_window().open_vistrail(f)
    return view

def close_vistrail(view, quiet=True):
    """close_vistrail(view: QVistrailView, quiet:bool)-> None
    Closes vistrail in view. If quiet is True it will discard changes
    automatically.
    
    """
    get_builder_window().close_vistrail(view, quiet=quiet)

def close_all_vistrails(quiet=True):
    get_builder_window().close_all_vistrails(quiet)
    
def new_vistrail():
    # Returns VistrailView - remember to be consistent about it..
    get_vistrails_application().builderWindow.new_vistrail(False)
    result = get_vistrails_application().builderWindow.get_current_view()
    return result

def get_vistrail_from_file(filename):
    from vistrails.core.db.locator import FileLocator
    from vistrails.core.vistrail.vistrail import Vistrail
    v = FileLocator(filename).load()
    if not isinstance(v, Vistrail):
        v = v.vistrail
    return v

##############################################################################
# Testing


class TestAPI(vistrails.gui.utils.TestVisTrailsGUI):

    def setUp(self):
        app = vistrails.gui.application.get_vistrails_application()
        app.builderWindow.auto_view = False
        app.builderWindow.close_all_vistrails(True)

    def test_close_current_vistrail_no_vistrail(self):
        self.assertRaises(NoVistrail, lambda: get_current_vistrail_view())

    def test_new_vistrail_no_save(self):
        v = new_vistrail()
        import vistrails.gui.vistrail_view
        assert isinstance(v, vistrails.gui.vistrail_view.QVistrailView)
        assert not v.controller.changed
        close_vistrail(v)

    def test_new_vistrail_button_states(self):
        assert get_vistrails_application().builderWindow.qactions['newVistrail'].isEnabled()
        assert not get_vistrails_application().builderWindow.qactions['closeVistrail'].isEnabled()
        assert not get_vistrails_application().builderWindow.qactions['saveFile'].isEnabled()
        assert not get_vistrails_application().builderWindow.qactions['saveFileAs'].isEnabled()
        view = new_vistrail()
        assert get_vistrails_application().builderWindow.qactions['newVistrail'].isEnabled()
        assert get_vistrails_application().builderWindow.qactions['closeVistrail'].isEnabled()
        self.assertEqual(get_vistrails_application().builderWindow.qactions['saveFile'].isEnabled(),
                         view.has_changes())
        assert get_vistrails_application().builderWindow.qactions['saveFileAs'].isEnabled()

    def test_detach_vistrail(self):
        view = new_vistrail()
        get_vistrails_application().builderWindow.detach_view(view)
        get_vistrails_application().builderWindow.attach_view(view)
        close_vistrail(view)

    
    
    

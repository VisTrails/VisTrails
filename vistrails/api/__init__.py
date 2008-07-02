############################################################################
##
## Copyright (C) 2006-2008 University of Utah. All rights reserved.
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

def get_current_controller():
    """get_current_controller():

    returns the VistrailController of the currently selected vistrail.

    """
    return _app.builderWindow.viewManager.currentWidget().controller    

def get_current_vistrail():
    """get_current_vistrail():

    Returns the currently selected vistrail.

    """
    return get_current_controller().vistrail

def get_current_vistrail_view():
    """get_current_vistrail():

    Returns the currently selected vistrail.

    """
    return get_current_controller().vistrail_view
    

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
        version = vistrail.get_tag_by_name(version).id
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
    return (vistrail.actionMap.keys(),
            dict([(t.time, t.name) for t in vistrail.tagMap.values()]))

def open_vistrail_from_file(filename):
    from core.db.locator import FileLocator

    f = FileLocator(filename)
    
    manager = _app.builderWindow.viewManager
    view = manager.open_vistrail(f)
    return view

def close_vistrail(view):
    _app.builderWindow.viewManager.closeVistrail(view, quiet=True)
    

# def get_open_vistrails():
#     """get_open_vistrails():

#     Returns list of (locator)"""

##############################################################################
# Testing

# import unittest
# import copy
# import random

# class TestAPI(unittest.TestCase):
#     pass

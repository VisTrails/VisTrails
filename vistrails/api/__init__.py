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

def select_version(version):
    """select_version(int or str):

    Given an integer, selects a version with the given number in the
    currently selected vistrail.

    Given a string, selects a version with that tag in the currently
    selected vistrail.

    """
    ctrl = get_current_controller()
    vistrail = ctrl.vistrail
    if type(version) == str:
        version = vistrail.get_tag_by_name(version).id
    ctrl.changeSelectedVersion(version)
    ctrl.invalidate_version_tree(False)

# def get_available_versions():
#     """get_available_version(): ([int], {int: str})

#     From the currently selected vistrail, return all available
#     versions and the existing tags.

#     """
#     ctrl = get_current_controller()
#     vistrail = ctrl.vistrail
    
    

# def get_open_vistrails():
#     """get_open_vistrails():

#     Returns list of (locator)"""

##############################################################################
# Testing

import unittest
import copy
import random

class TestAPI(unittest.TestCase):

    def test_switch_mode(self):
        switch_to_pipeline_view()
        switch_to_history_view()
        switch_to_query_view()
        switch_to_pipeline_view()
        switch_to_history_view()
        switch_to_query_view()

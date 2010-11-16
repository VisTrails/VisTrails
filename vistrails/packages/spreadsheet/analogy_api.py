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
################################################################################
# This file describes the analogy structure the spreadsheet holding
# and it should be reimplemented to integrate between the spreadsheet
# and the analogy
################################################################################

import os
import core.analogy

class SpreadsheetAnalogyObject(object):
    """
    SpreadsheetAnalogyObject provides a API functions to integrate
    between the spreadsheet and the analogy. There will be only one
    instance of the analogy object
    
    """
    def __init__(self):
        """ SpreadsheetAnalogyObject() -> SpreadsheetAnalogyObject
        Initialize object properties
        
        """
        pass

    def isValid(self):
        """ isValid() -> bool        
        Is the current analogy object is valid and can be applied to
        other pipeline
        
        """
        return True
        
    def createAnalogy(self, p1Info, p2Info):
        """ createAnalogy(p1Info: tuple, p2Info) -> bool        
        p1Info, p2Info: (vistrailName, versionNumber, actions, pipeline)
        
        Setup an analogy object from p1 to p2 given their info in
        p1Info and p2Info. CAUTION: sometimes the actual 'pipeline' on
        the spreadsheet is different than the one created from the
        vistrailName:versionNumber. For example, the parameter
        exploration.  If that is the case, actions is a list of all
        actions has performed on the original pipeline to get to the
        pipeline.

        This function should return a boolean saying if the analogy
        has been successfully created or not.
        
        """
#         (p1_vistrail, p1_number, p1_actions, p1_pipeline) = p1Info
#         (p2_vistrail, p2_number, p2_actions, p2_pipeline) = p2Info
        self._p1Info = p1Info
        self._p2Info = p2Info
        return True

    def applyAnalogy(self, pInfo):
        """ createAnalogy(pInfo: tuple) -> pInfo
        pInfo: (vistrailName, versionNumber, actions, pipeline)

        Given the analogy, apply on the pipeline in pInfo and return
        the modified pipeline as a result. Along with the pipeline is
        the list of actions that has been applied. If no actions
        given (i.e. []), this can not be put back to the builder. If
        analogy is not applicable, this should return None
        
        """
        def get_controller_by_locator(locator):
            import gui.application
            app = gui.application.VistrailsApplication
            m = app.builderWindow.viewManager
            # slow, but who cares
            for v in app.builderWindow.viewManager._views.values():
                if v.locator == locator:
                    return v
            if not v:
                raise Exception("Couldn't find")


        (p1_locator, p1_number, p1_actions, p1_pipeline) = self._p1Info
        (p2_locator, p2_number, p2_actions, p2_pipeline) = self._p2Info
        (p3_locator, p3_number, p3_actions, p3_pipeline) = pInfo

        # print type(p1_locator), p1_locator
        if (p1_locator != p2_locator or
            p1_locator != p3_locator or
            p1_actions or
            p2_actions or
            p3_actions):
            return None
        #p1_locator = os.path.split(p1_vistrail)[1]

        perform = core.analogy.perform_analogy_on_vistrail

        controller = get_controller_by_locator(p3_locator)
        vt = controller.vistrail
        action = perform( vt, p1_number, p2_number, p3_number)
        
        controller.add_new_action(action)
        controller.perform_action(action)
        
        new_version = controller.current_version
        new_pipeline = vt.getPipeline(new_version)
        return (p3_locator, new_version, [], new_pipeline)

    def __call__(self):
        """ __call__() -> SpreadsheetAnalogy
        Return self for calling method
        
        """
        return self

SpreadsheetAnalogy = SpreadsheetAnalogyObject()

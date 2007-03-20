############################################################################
##
## Copyright (C) 2006-2007 University of Utah. All rights reserved.
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
        if self.isValid():
            return pInfo
        return None

    def __call__(self):
        """ __call__() -> VistrailsApplicationSingleton
        Return self for calling method
        
        """
        return self

SpreadsheetAnalogy = SpreadsheetAnalogyObject()

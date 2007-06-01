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

from core.vistrail.pipeline import Pipeline
from db.services import io, vistrail
from xml.dom.minidom import parse, getDOMImplementation

def openVistrail(filename):
    return io.openVistrailFromXML(filename)    

def getWorkflow(vt, version):
    workflow = vistrail.materializeWorkflow(vt, version)
#    Pipeline.convert(workflow)
    return workflow

def saveVistrail(vt, filename):
    io.saveVistrailToXML(vt, filename)

def saveWorkflow(workflow, filename):
    io.saveWorkflowToXML(workflow, filename)

def fromXML(vtType, dom):
    """returns VisTrails entity given DOM for XML rep"""

    result = io.readXMLObjects(vtType, dom.documentElement)
    return result[0]

def toXML(object):
    """returns DOM for XML rep of any VisTrails entity"""

    dom = getDOMImplementation().createDocument(None, None, None)
    root = io.writeXMLObjects([object], dom)
    dom.appendChild(root)
    return dom

def getWorkflowDiff(vt, v1, v2):
    (v1, v2, pairs, v1Only, v2Only, paramChanges) = \
        vistrail.getWorkflowDiff(vt, v1, v2, True)
    Pipeline.convert(v1)
    Pipeline.convert(v2)
    #     print 'pairs:', pairs
    #     print 'v1Only:', v1Only
    #     print 'v2Only:', v2Only
    #     print 'paramChanges:', paramChanges
    return (v1, v2, pairs, v1Only, v2Only, paramChanges)

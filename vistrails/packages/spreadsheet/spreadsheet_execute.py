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
# This file contains useful functions for executing pipelines on the spreadsheet
# assignPipelineCellLocations
# executePipelineWithProgress
################################################################################

from PyQt4 import QtCore, QtGui
# FIXME broke this as Actions have been changed around
#
# from core.vistrail.action import AddModuleAction, AddConnectionAction, \
#      DeleteConnectionAction, ChangeParameterAction
from core.modules.module_registry import registry
from core.vistrail import module
from core.vistrail import connection
from core.interpreter.default import get_default_interpreter
from core.utils import DummyView
import copy

################################################################################

def assignPipelineCellLocations(inPipeline, sheetName, row, col, cellIds=[]):
    """ assignPipelineCellLocations(inPipeline: Pipline, 
                                      sheetName: str,
                                      row: int,
                                      col: int,
                                      cellIds: [int]) -> Pipeline                                      
    Modify the inPipeline to have its spreadsheet cells given in
    cellIds to be located at the same location (sheetName, row,
    col). If cellIds is empty, this will search for all spreadsheet
    cells in inPipeline. The modified output is returned as the
    result.
    
    """
    pipeline = copy.copy(inPipeline)
    if cellIds==[]:
        cellIds = pipeline.modules.keys()
    SpreadsheetCell = registry.get_descriptor_by_name('edu.utah.sci.vistrails.spreadsheet',
                                                      'SpreadsheetCell').module
    for mId in cellIds:
        md = pipeline.modules[mId]
        moduleClass = registry.get_descriptor_by_name(md.package, md.name).module
        if not issubclass(moduleClass, SpreadsheetCell):
            continue
        # Walk through all connection and remove all
        # CellLocation connected to this spreadsheet cell
        delConn = DeleteConnectionAction()
        for (cId,c) in pipeline.connections.iteritems():
            if (c.destinationId==mId and
                pipeline.modules[c.sourceId].name=="CellLocation"):
                delConn.addId(cId)
        delConn.perform(pipeline)

        # Add a sheet reference with a specific name
        sheetReference = module.Module()
        sheetReference.id = pipeline.fresh_module_id()
        sheetReference.name = "SheetReference"
        sheetReference.package = "edu.utah.sci.vistrails.spreadsheet"
        addModule = AddModuleAction()
        addModule.module = sheetReference
        addModule.perform(pipeline)
        addParam = ChangeParameterAction()
        addParam.addParameter(sheetReference.id, 0, 0,
                              "SheetName", "", sheetName, "String", "" )
        addParam.addParameter(sheetReference.id, 1, 0,
                              "MinRowCount", "",
                              str(row+1), "Integer", "" )
        addParam.addParameter(sheetReference.id, 2, 0,
                              "MinColumnCount", "",
                              str(col+1), "Integer", "" )
        addParam.perform(pipeline)

        # Add a cell location module with a specific row and column
        cellLocation = module.Module()
        cellLocation.id = pipeline.fresh_module_id()
        cellLocation.name = "CellLocation"
        cellLocation.package = "edu.utah.sci.vistrails.spreadsheet"
        addModule = AddModuleAction()
        addModule.module = cellLocation
        addModule.perform(pipeline)

        addParam = ChangeParameterAction()                
        addParam.addParameter(cellLocation.id, 0, 0,
                              "Row", "", str(row+1),
                              "Integer", "" )
        addParam.addParameter(cellLocation.id, 1, 0,
                              "Column", "", str(col+1),
                              "Integer", "" )
        addParam.perform(pipeline)

        # Then connect the SheetReference to the CellLocation
        conn = connection.Connection()
        conn.id = pipeline.fresh_connection_id()
        conn.source.moduleId = sheetReference.id
        conn.source.moduleName = sheetReference.name
        conn.source.name = "self"
        conn.source.spec = registry.get_output_port_spec(
            sheetReference, "self")
        conn.connectionId = conn.id
        conn.destination.moduleId = cellLocation.id
        conn.destination.moduleName = cellLocation.name
        conn.destination.name = "SheetReference"
        conn.destination.spec = registry.get_input_port_spec(
            cellLocation, "SheetReference")
        addConnection = AddConnectionAction()
        addConnection.connection = conn
        addConnection.perform(pipeline)

        # Then connect the CellLocation to the spreadsheet cell
        conn = connection.Connection()
        conn.id = pipeline.fresh_connection_id()
        conn.source.moduleId = cellLocation.id
        conn.source.moduleName = cellLocation.name
        conn.source.name = "self"
        conn.source.spec = registry.get_output_port_spec(
            cellLocation, "self")
        conn.connectionId = conn.id
        conn.destination.moduleId = mId
        conn.destination.moduleName = pipeline.modules[mId].name
        conn.destination.name = "Location"
        conn.destination.spec = registry.get_input_port_spec(
            cellLocation, "Location")
        addConnection = AddConnectionAction()
        addConnection.connection = conn
        addConnection.perform(pipeline)
    return pipeline

def executePipelineWithProgress(pipeline,
                                pTitle='Pipeline Execution',
                                pCaption='Executing...',
                                pCancel='&Cancel',
                                **kwargs):
    """ executePipelineWithProgress(pipeline: Pipeline,                                    
                                    pTitle: str, pCaption: str, pCancel: str,
                                    kwargs: keyword arguments) -> bool
    Execute the pipeline while showing a progress dialog with title
    pTitle, caption pCaption and the cancel button text
    pCancel. kwargs is the keyword arguments that will be passed to
    the interpreter. A bool will be returned indicating if the
    execution was performed without cancel or not.
    
    """
    withoutCancel = True
    totalProgress = len(pipeline.modules)
    progress = QtGui.QProgressDialog(pCaption,
                                     pCancel,
                                     0, totalProgress)
    progress.setWindowTitle(pTitle)
    progress.setWindowModality(QtCore.Qt.WindowModal)
    progress.show()
    def moduleExecuted(objId):
        if not progress.wasCanceled():
            progress.setValue(progress.value()+1)
            QtCore.QCoreApplication.processEvents()
        else:
            withoutCancel = False
    interpreter = get_default_interpreter()
    if kwargs.has_key('moduleExecutedHook'):
        kwargs['moduleExecutedHook'].append(moduleExecuted)
    else:
        kwargs['moduleExecutedHook'] = [moduleExecuted]
    kwargs['pipeline'] = pipeline
    kwargs['view'] = DummyView()
    interpreter.execute(None, **kwargs)                        
    progress.setValue(totalProgress)
    return withoutCancel

###############################################################################
##
## Copyright (C) 2006-2011, University of Utah. 
## All rights reserved.
## Contact: vistrails@sci.utah.edu
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
from core.modules.module_registry import get_module_registry
from core.interpreter.default import get_default_interpreter
from core.utils import DummyView
from core.vistrail.action import Action
from core.vistrail.module_function import ModuleFunction
from core.vistrail.module_param import ModuleParam
from core.vistrail.port import Port
from core.vistrail import module
from core.vistrail import connection
import db.services.action
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
    registry = get_module_registry()
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
        action_list = []
        for (cId,c) in pipeline.connections.iteritems():
            if (c.destinationId==mId and 
                pipeline.modules[c.sourceId].name=="CellLocation"):
                action_list.append(('delete', c))
        action = db.services.action.create_action(action_list)
        Action.convert(action)
        pipeline.perform_action(action)

        # Add a sheet reference with a specific name
        param_id = -pipeline.tmp_id.getNewId(ModuleParam.vtType)
        sheetNameParam = ModuleParam(id=param_id,
                                     pos=0,
                                     name="",
                                     val=sheetName,
                                     type="String",
                                     alias="",
                                     )
        function_id = -pipeline.tmp_id.getNewId(ModuleFunction.vtType)
        sheetNameFunction = ModuleFunction(id=function_id,
                                           pos=0,
                                           name="SheetName",
                                           parameters=[sheetNameParam],
                                           )
        param_id = -pipeline.tmp_id.getNewId(ModuleParam.vtType)
        minRowParam = ModuleParam(id=param_id,
                                  pos=0,
                                  name="",
                                  val=str(row+1),
                                  type="Integer",
                                  alias="",
                                  )
        function_id = -pipeline.tmp_id.getNewId(ModuleFunction.vtType)
        minRowFunction = ModuleFunction(id=function_id,
                                        pos=1,
                                        name="MinRowCount",
                                        parameters=[minRowParam],
                                        )
        param_id = -pipeline.tmp_id.getNewId(ModuleParam.vtType)
        minColParam = ModuleParam(id=param_id,
                                  pos=0,
                                  name="",
                                  val=str(col+1),
                                  type="Integer",
                                  alias="",
                                  )
        function_id = -pipeline.tmp_id.getNewId(ModuleFunction.vtType)
        minColFunction = ModuleFunction(id=function_id,
                                        pos=2,
                                        name="MinColumnCount",
                                        parameters=[minColParam],
                                        )
        module_id = -pipeline.tmp_id.getNewId(module.Module.vtType)
        sheetReference = module.Module(id=module_id,
                                       name="SheetReference",
                                       package="edu.utah.sci.vistrails.spreadsheet",
                                       functions=[sheetNameFunction,
                                                  minRowFunction,
                                                  minColFunction])
        action = db.services.action.create_action([('add', 
                                                   sheetReference)])
        # FIXME: this should go to dbservice
        Action.convert(action)
        pipeline.perform_action(action)

        # Add a cell location module with a specific row and column
        param_id = -pipeline.tmp_id.getNewId(ModuleParam.vtType)
        rowParam = ModuleParam(id=param_id,
                               pos=0,
                               name="",
                               val=str(row+1),
                               type="Integer",
                               alias="",
                               )
        function_id = -pipeline.tmp_id.getNewId(ModuleFunction.vtType)
        rowFunction = ModuleFunction(id=function_id,
                                     pos=0,
                                     name="Row",
                                     parameters=[rowParam],
                                     )
        param_id = -pipeline.tmp_id.getNewId(ModuleParam.vtType)
        colParam = ModuleParam(id=param_id,
                               pos=0,
                               name="",
                               val=str(col+1),
                               type="Integer",
                               alias="",
                               )
        function_id = -pipeline.tmp_id.getNewId(ModuleFunction.vtType)
        colFunction = ModuleFunction(id=function_id,
                                     pos=1,
                                     name="Column",
                                     parameters=[colParam],
                                     )
        module_id = -pipeline.tmp_id.getNewId(module.Module.vtType)
        cellLocation = module.Module(id=module_id,
                                     name="CellLocation",
                                     package="edu.utah.sci.vistrails.spreadsheet",
                                     functions=[rowFunction,
                                                colFunction])
        action = db.services.action.create_action([('add', 
                                                   cellLocation)])
        # FIXME: this should go to dbservice
        Action.convert(action)
        pipeline.perform_action(action)

        # Then connect the SheetReference to the CellLocation
        port_id = -pipeline.tmp_id.getNewId(Port.vtType)
        source = Port(id=port_id,
                      type='source',
                      moduleId=sheetReference.id,
                      moduleName=sheetReference.name)
        source.name = "self"
        source.spec = sheetReference.get_port_spec("self", "output")
        port_id = -pipeline.tmp_id.getNewId(Port.vtType)
        destination = Port(id=port_id,
                           type='destination',
                           moduleId=cellLocation.id,
                           moduleName=cellLocation.name)
        destination.name = "SheetReference"
        destination.spec = cellLocation.get_port_spec("SheetReference", 
                                                      "input")
        c_id = -pipeline.tmp_id.getNewId(connection.Connection.vtType)
        conn = connection.Connection(id=c_id,
                                     ports=[source, destination])
        action = db.services.action.create_action([('add', 
                                                   conn)])
        # FIXME: this should go to dbservice
        Action.convert(action)
        pipeline.perform_action(action)

        # Then connect the CellLocation to the spreadsheet cell
        port_id = -pipeline.tmp_id.getNewId(Port.vtType)
        source = Port(id=port_id,
                      type='source',
                      moduleId=cellLocation.id,
                      moduleName=cellLocation.name)
        source.name = "self"
        source.spec = cellLocation.get_port_spec("self", "output")
        port_id = -pipeline.tmp_id.getNewId(Port.vtType)
        cell_module = pipeline.get_module_by_id(mId)
        destination = Port(id=port_id,
                           type='destination',
                           moduleId=mId,
                           moduleName=pipeline.modules[mId].name)
        destination.name = "Location"
        destination.spec = cell_module.get_port_spec("Location", "input")
        c_id = -pipeline.tmp_id.getNewId(connection.Connection.vtType)
        conn = connection.Connection(id=c_id,
                                     ports=[source, destination])
        action = db.services.action.create_action([('add', 
                                                   conn)])
        # FIXME: this should go to dbservice
        Action.convert(action)
        pipeline.perform_action(action)
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
    if kwargs.has_key('module_executed_hook'):
        kwargs['module_executed_hook'].append(moduleExecuted)
    else:
        kwargs['module_executed_hook'] = [moduleExecuted]
    kwargs['view'] = DummyView()
    interpreter.execute(pipeline, **kwargs)
    progress.setValue(totalProgress)
    return withoutCancel

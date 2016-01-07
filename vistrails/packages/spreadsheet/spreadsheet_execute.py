###############################################################################
##
## Copyright (C) 2014-2016, New York University.
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
##  - Neither the name of the New York University nor the names of its
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

"""This file contains useful functions for executing pipelines on the
spreadsheet:
  assignPipelineCellLocations
  executePipelineWithProgress
"""

from __future__ import division

import copy
from PyQt4 import QtCore, QtGui

from vistrails.core.inspector import PipelineInspector
from vistrails.core.interpreter.default import get_default_interpreter
from vistrails.core.modules.module_registry import get_module_registry
from vistrails.core.vistrail.controller import VistrailController
from vistrails.core.utils import DummyView

from .identifiers import identifier as spreadsheet_pkg


def assignPipelineCellLocations(pipeline, sheetName,
                                row, col, cellIds=None,
                                minRowCount=None, minColCount=None):

    reg = get_module_registry()
    spreadsheet_cell_desc = reg.get_descriptor_by_name(spreadsheet_pkg,
                                                       'SpreadsheetCell')
    output_module_desc = reg.get_descriptor_by_name(
            'org.vistrails.vistrails.basic', 'OutputModule')

    create_module = VistrailController.create_module_static
    create_function = VistrailController.create_function_static
    create_connection = VistrailController.create_connection_static

    pipeline = copy.copy(pipeline)
    root_pipeline = pipeline
    if cellIds is None:
        inspector = PipelineInspector()
        inspector.inspect_spreadsheet_cells(pipeline)
        inspector.inspect_ambiguous_modules(pipeline)
        cellIds = inspector.spreadsheet_cells

    def fix_cell_module(pipeline, mId):
        # Delete connections to 'Location' input port
        conns_to_delete = []
        for c in pipeline.connection_list:
            if c.destinationId == mId and c.destination.name == 'Location':
                conns_to_delete.append(c.id)
        for c_id in conns_to_delete:
            pipeline.delete_connection(c_id)

        # a hack to first get the id_scope to the local pipeline scope
        # then make them negative by hacking the getNewId method
        # all of this is reset at the end of this block
        id_scope = pipeline.tmp_id
        orig_getNewId = pipeline.tmp_id.__class__.getNewId
        def getNewId(self, objType):
            return -orig_getNewId(self, objType)
        pipeline.tmp_id.__class__.getNewId = getNewId

        # Add a sheet reference with a specific name
        sheetReference = create_module(id_scope, spreadsheet_pkg,
                                       "SheetReference")
        sheetNameFunction = create_function(id_scope, sheetReference,
                                            "SheetName", [str(sheetName)])
            # ["%s %d" % (sheetPrefix, sheet)])

        sheetReference.add_function(sheetNameFunction)

        if minRowCount is not None:
            minRowFunction = create_function(id_scope, sheetReference,
                                             "MinRowCount", [str(minRowCount)])
                                                   # [str(rowCount*vRCount)])
            sheetReference.add_function(minRowFunction)
        if minColCount is not None:
            minColFunction = create_function(id_scope, sheetReference,
                                             "MinColumnCount",
                                             [str(minColCount)])
                                                   # [str(colCount*vCCount)])
            sheetReference.add_function(minColFunction)

        # Add a cell location module with a specific row and column
        cellLocation = create_module(id_scope, spreadsheet_pkg,
                                     "CellLocation")
        rowFunction = create_function(id_scope, cellLocation, "Row", [str(row)])
                                                 # [str(row*vRCount+vRow+1)])
        colFunction = create_function(id_scope, cellLocation, "Column",
                                      [str(col)])
                                                 # [str(col*vCCount+vCol+1)])

        cellLocation.add_function(rowFunction)
        cellLocation.add_function(colFunction)

        # Then connect the SheetReference to the CellLocation
        sheet_conn = create_connection(id_scope, sheetReference, "value",
                                       cellLocation, "SheetReference")

        # Then connect the CellLocation to the spreadsheet cell
        cell_module = pipeline.get_module_by_id(mId)
        cell_conn = create_connection(id_scope, cellLocation, "value",
                                      cell_module, "Location")

        pipeline.add_module(sheetReference)
        pipeline.add_module(cellLocation)
        pipeline.add_connection(sheet_conn)
        pipeline.add_connection(cell_conn)

        # replace the getNewId method
        pipeline.tmp_id.__class__.getNewId = orig_getNewId

    def fix_output_module(pipeline, mId):
        # Remove all connections to 'configuration' input port
        conns_to_delete = []
        for c in pipeline.connection_list:
            if (c.destinationId == mId and
                    c.destination.name == 'configuration'):
                conns_to_delete.append(c.id)
        for c_id in conns_to_delete:
            pipeline.delete_connection(c_id)

        m = pipeline.modules[mId]

        # Remove all functions on 'configuration' input port
        funcs_to_delete = []
        for f in m.functions:
            if f.name == 'configuration':
                funcs_to_delete.append(f.real_id)
        for f_id in funcs_to_delete:
            m.delete_function_by_real_id(f_id)

        # a hack to first get the id_scope to the local pipeline scope
        # then make them negative by hacking the getNewId method
        # all of this is reset at the end of this block
        id_scope = pipeline.tmp_id
        orig_getNewId = pipeline.tmp_id.__class__.getNewId
        def getNewId(self, objType):
            return -orig_getNewId(self, objType)
        pipeline.tmp_id.__class__.getNewId = getNewId

        config = {'row': row - 1, 'col': col - 1}
        if minRowCount is not None:
            config['sheetRowCount'] = minRowCount
        if minColCount is not None:
            config['sheetColCount'] = minColCount
        if sheetName is not None:
            config['sheetName']= sheetName
        config = {'spreadsheet': config}
        config_function = create_function(id_scope, m,
                                          'configuration', [repr(config)])
        m.add_function(config_function)

        # replace the getNewId method
        pipeline.tmp_id.__class__.getNewId = orig_getNewId

    for id_list in cellIds:
        cell_pipeline = pipeline

        # find at which depth we need to be working
        if isinstance(id_list, (int, long)):
            mId = id_list
            m = cell_pipeline.modules[mId]
        else:
            id_iter = iter(id_list)
            mId = next(id_iter)
            m = cell_pipeline.modules[mId]
            for mId in id_iter:
                cell_pipeline = m.pipeline
                m = cell_pipeline.modules[mId]

        if reg.is_descriptor_subclass(m.module_descriptor,
                                      spreadsheet_cell_desc):
            fix_cell_module(cell_pipeline, mId)
        elif reg.is_descriptor_subclass(m.module_descriptor,
                                        output_module_desc):
            fix_output_module(cell_pipeline, mId)

    return root_pipeline


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

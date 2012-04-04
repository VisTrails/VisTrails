###############################################################################
##
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
""" The file describes the parameter exploration tab for VisTrails

QParameterExplorationTab
"""

from PyQt4 import QtCore, QtGui
from xml.dom.minidom import parseString
from xml.sax.saxutils import escape
from core import debug
from core.interpreter.default import get_default_interpreter
from core.modules.module_registry import get_module_registry
from core.param_explore import ActionBasedParameterExploration
from core.system import current_time
from gui.common_widgets import QDockContainer, QToolWindowInterface
from gui.paramexplore.pe_table import QParameterExplorationWidget, QParameterSetEditor
from gui.paramexplore.virtual_cell import QVirtualCellWindow
from gui.paramexplore.param_view import QParameterView
from gui.paramexplore.pe_pipeline import QAnnotatedPipelineView

################################################################################

class QParameterExplorationTab(QDockContainer, QToolWindowInterface):
    """
    QParameterExplorationTab is a tab containing different widgets
    related to parameter exploration
    
    """
    explorationId = 0
    
    def __init__(self, parent=None):
        """ QParameterExplorationTab(parent: QWidget)
                                    -> QParameterExplorationTab
        Make it a main window with dockable area and a
        QParameterExplorationTable
        
        """
        QDockContainer.__init__(self, parent)
        self.setWindowTitle('Parameter Exploration')
        self.toolWindow().setFeatures(QtGui.QDockWidget.NoDockWidgetFeatures)
        self.toolWindow().hide()

        self.peWidget = QParameterExplorationWidget()
        self.setCentralWidget(self.peWidget)
        self.connect(self.peWidget.table,
                     QtCore.SIGNAL('exploreChange(bool)'),
                     self.exploreChange)

        self.paramView = QParameterView(self)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea,
                           self.paramView.toolWindow())
        
        self.annotatedPipelineView = QAnnotatedPipelineView(self)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea,
                           self.annotatedPipelineView.toolWindow())
        
        self.virtualCell = QVirtualCellWindow(self)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea,
                           self.virtualCell.toolWindow())
        
        self.controller = None
        self.currentVersion = -1

    def addViewActionsToMenu(self, menu):
        """addViewActionsToMenu(menu: QMenu) -> None
        Add toggle view actions to menu
        
        """
        menu.addAction(self.paramView.toolWindow().toggleViewAction())
        menu.addAction(self.annotatedPipelineView.toolWindow().toggleViewAction())
        menu.addAction(self.virtualCell.toolWindow().toggleViewAction())

    def removeViewActionsFromMenu(self, menu):
        """removeViewActionsFromMenu(menu: QMenu) -> None
        Remove toggle view actions from menu
        
        """
        menu.removeAction(self.paramView.toolWindow().toggleViewAction())
        menu.removeAction(self.annotatedPipelineView.toolWindow().toggleViewAction())
        menu.removeAction(self.virtualCell.toolWindow().toggleViewAction())
        
    def setController(self, controller):
        """ setController(controller: VistrailController) -> None
        Assign a controller to the parameter exploration tab
        
        """
        self.controller = controller

    def getParameterExploration(self):
        """ getParameterExploration() -> string
        Generates an XML string that represents the current
        parameter exploration, and which can be loaded with
        setParameterExploration().
        
        """
        # Construct xml for persisting parameter exploration
        escape_dict = { "'":"&apos;", '"':'&quot;', '\n':'&#xa;' }
        timestamp = current_time().strftime('%Y-%m-%d %H:%M:%S')
        # TODO: For now, we use the timestamp as the 'name' - Later, we should set 'name' based on a UI input field
        xml = '\t<paramexp dims="%s" layout="%s" date="%s" name="%s">' % (str(self.peWidget.table.label.getCounts()), str(self.virtualCell.getConfiguration()[2]), timestamp, timestamp)
        for i in xrange(self.peWidget.table.layout().count()):
            pEditor = self.peWidget.table.layout().itemAt(i).widget()
            if pEditor and type(pEditor)==QParameterSetEditor:
                firstParam = True
                for paramWidget in pEditor.paramWidgets:
                    paramInfo = paramWidget.param
                    interpolator = paramWidget.editor.stackedEditors.currentWidget()
                    intType = interpolator.exploration_name
                    # Write function tag prior to the first parameter of the function
                    if firstParam:
                        xml += '\n\t\t<function id="%s" alias="%s" name="%s">' % (paramInfo.parent_id, paramInfo.is_alias, pEditor.info[0])
                        firstParam = False
                    # Write parameter tag
                    xml += '\n\t\t\t<param id="%s" dim="%s" interp="%s"' % (paramInfo.id, paramWidget.getDimension(), intType)
                    if intType == 'Linear Interpolation':
                        xml += ' min="%s" max="%s"' % (interpolator.fromEdit.get_value(), interpolator.toEdit.get_value())
                    elif intType == 'List':
                        xml += ' values="%s"' % escape(str(interpolator._str_values), escape_dict)
                    elif intType == 'User-defined Function':
                        xml += ' code="%s"' % escape(interpolator.function, escape_dict)
                    xml += '/>'
                xml += '\n\t\t</function>'
        xml += '\n\t</paramexp>'
        return xml

    def setParameterExploration(self, xmlString):
        """ setParameterExploration(xmlString: string) -> None
        Sets the current parameter exploration to the one
        defined by 'xmlString'.
        
        """
        if not xmlString:
            return
        # Parse/validate the xml
        try:
            xmlDoc = parseString(xmlString).documentElement
        except:
            debug.critical("Parameter Exploration load failed because of "
                           "invalid XML:\n\n%s" % xmlString)
            return
        # Set the exploration dimensions
        dims = eval(str(xmlDoc.attributes['dims'].value))
        self.peWidget.table.label.setCounts(dims)
        # Set the virtual cell layout
        layout = eval(str(xmlDoc.attributes['layout'].value))
        self.virtualCell.setConfiguration(layout)
        # Populate parameter exploration window with stored functions and aliases
        for f in xmlDoc.getElementsByTagName('function'):
            # Retrieve function attributes
            f_id = long(f.attributes['id'].value)
            f_name = str(f.attributes['name'].value)
            f_is_alias = (str(f.attributes['alias'].value) == 'True')
            # Search the parameter treeWidget for this function and add it directly
            newEditor = None
            for tidx in xrange(self.paramView.treeWidget.topLevelItemCount()):
                moduleItem = self.paramView.treeWidget.topLevelItem(tidx)
                for cidx in xrange(moduleItem.childCount()):
                    paramInfo = moduleItem.child(cidx).parameter
                    name, params = paramInfo
                    if params[0].parent_id == f_id and params[0].is_alias == f_is_alias:
                        newEditor = self.peWidget.table.addParameter(paramInfo)
            # Retrieve params for this function and set their values in the UI
            if newEditor:
                for p in f.getElementsByTagName('param'):
                    # Locate the param in the newly added param editor and set values
                    p_id = long(p.attributes['id'].value)
                    for paramWidget in newEditor.paramWidgets:
                        if paramWidget.param.id == p_id:
                            # Set Parameter Dimension (radio button)
                            p_dim = int(p.attributes['dim'].value)
                            paramWidget.setDimension(p_dim)
                            # Set Interpolator Type (dropdown list)
                            p_intType = str(p.attributes['interp'].value)
                            paramWidget.editor.selectInterpolator(p_intType)
                            # Set Interpolator Value(s)
                            interpolator = paramWidget.editor.stackedEditors.currentWidget()
                            if p_intType == 'Linear Interpolation':
                                # Set min/max
                                p_min = str(p.attributes['min'].value)
                                p_max = str(p.attributes['max'].value)
                                interpolator.fromEdit.setText(p_min)
                                interpolator.toEdit.setText(p_max)
                            elif p_intType == 'List':
                                p_values = str(p.attributes['values'].value)
                                # Set internal list structure
                                interpolator._str_values = eval(p_values)
                                # Update UI list
                                if interpolator.type == 'String':
                                    interpolator.listValues.setText(p_values)
                                else:
                                    interpolator.listValues.setText(p_values.replace("'", "").replace('"', ''))
                            elif p_intType == 'User-defined Function':
                                # Set function code
                                p_code = str(p.attributes['code'].value)
                                interpolator.function = p_code

    def showEvent(self, event):
        """ showEvent(event: QShowEvent) -> None
        Update the tab when it is shown
        
        """
        if self.currentVersion!=self.controller.current_version:
            self.currentVersion = self.controller.current_version
            # Update the virtual cell
            pipeline = self.controller.current_pipeline
            self.virtualCell.updateVirtualCell(pipeline)

            # Now we need to inspect the parameter list
            self.paramView.treeWidget.updateFromPipeline(pipeline)

            # Update the annotated ids
            self.annotatedPipelineView.updateAnnotatedIds(pipeline)

            # Update the parameter exploration table
            self.peWidget.updatePipeline(pipeline)

            # Update the UI with the most recent parameter exploration
            # TODO: For now, we just strip the root tags since there's only one
            #       exploration - Later we should parse the root tree and select
            #       the active exploration based on date, or user choice
            xmlString = self.controller.vistrail.get_paramexp(self.currentVersion)
            if xmlString is not None:
                striplen = len("<paramexps>")
                xmlString = xmlString[striplen:-(striplen+1)].strip()
                self.setParameterExploration(xmlString)

    def performParameterExploration(self):
        """ performParameterExploration() -> None        
        Perform the exploration by collecting a list of actions
        corresponding to each dimension
        
        """
        registry = get_module_registry()
        actions = self.peWidget.table.collectParameterActions()

        # Set the annotation to persist the parameter exploration
        # TODO: For now, we just replace the existing exploration - Later we should append them.
        xmlString = "<paramexps>\n" + self.getParameterExploration() + "\n</paramexps>"
        self.controller.vistrail.set_paramexp(self.currentVersion, xmlString)
        self.controller.set_changed(True)

        if self.controller.current_pipeline and actions:
            explorer = ActionBasedParameterExploration()
            (pipelines, performedActions) = explorer.explore(
                self.controller.current_pipeline, actions)
            
            dim = [max(1, len(a)) for a in actions]
            if (registry.has_module('edu.utah.sci.vistrails.spreadsheet', 'CellLocation') and
                registry.has_module('edu.utah.sci.vistrails.spreadsheet', 'SheetReference')):
                modifiedPipelines = self.virtualCell.positionPipelines(
                    'PE#%d %s' % (QParameterExplorationTab.explorationId,
                                  self.controller.name),
                    dim[2], dim[1], dim[0], pipelines, self.controller)
            else:
                modifiedPipelines = pipelines

            mCount = []
            for p in modifiedPipelines:
                if len(mCount)==0:
                    mCount.append(0)
                else:
                    mCount.append(len(p.modules)+mCount[len(mCount)-1])
                
            # Now execute the pipelines
            totalProgress = sum([len(p.modules) for p in modifiedPipelines])
            progress = QtGui.QProgressDialog('Performing Parameter '
                                             'Exploration...',
                                             '&Cancel',
                                             0, totalProgress)
            progress.setWindowTitle('Parameter Exploration')
            progress.setWindowModality(QtCore.Qt.WindowModal)
            progress.show()

            QParameterExplorationTab.explorationId += 1
            interpreter = get_default_interpreter()
            for pi in xrange(len(modifiedPipelines)):
                progress.setValue(mCount[pi])
                QtCore.QCoreApplication.processEvents()
                if progress.wasCanceled():
                    break
                def moduleExecuted(objId):
                    if not progress.wasCanceled():
                        #progress.setValue(progress.value()+1)
                        #the call above was crashing when used by multithreaded
                        #code, replacing with the call below (thanks to Terence
                        #for submitting this fix). 
                        QtCore.QMetaObject.invokeMethod(progress, "setValue", 
                                        QtCore.Q_ARG(int,progress.value()+1))
                        QtCore.QCoreApplication.processEvents()
                kwargs = {'locator': self.controller.locator,
                          'current_version': self.controller.current_version,
                          'view': self.controller.current_pipeline_view,
                          'module_executed_hook': [moduleExecuted],
                          'reason': 'Parameter Exploration',
                          'actions': performedActions[pi],
                          }
                interpreter.execute(modifiedPipelines[pi], **kwargs)
            progress.setValue(totalProgress)

    def exploreChange(self, notEmpty):
        """ exploreChange(notEmpty: bool) -> None
        echo the signal
        
        """
        self.emit(QtCore.SIGNAL('exploreChange(bool)'), notEmpty)

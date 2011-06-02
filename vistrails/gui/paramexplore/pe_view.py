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

from PyQt4 import QtCore, QtGui

from core.interpreter.default import get_default_interpreter
from core.modules.module_registry import get_module_registry
from core.param_explore import ActionBasedParameterExploration
from gui.base_view import BaseView
from gui.paramexplore.pe_table import QParameterExplorationWidget
from gui.theme import CurrentTheme

class QParamExploreView(QParameterExplorationWidget, BaseView):
    explorationId = 0
    
    def __init__(self, parent=None):
        QParameterExplorationWidget.__init__(self, parent)
        BaseView.__init__(self)

        self.set_title("Explore")
        self.connect(self.table,
                     QtCore.SIGNAL('exploreChange(bool)'),
                     self.exploreChange)

    def set_controller(self, controller):
        self.controller = controller
        
    def set_default_layout(self):
        from gui.paramexplore.pe_palette import QParamExplorePalette
        from gui.paramexplore.param_view import QParameterView
        self.layout = \
            {QtCore.Qt.LeftDockWidgetArea: QParamExplorePalette,
             QtCore.Qt.RightDockWidgetArea: QParameterView,
             }
            
    def set_action_links(self):
        self.action_links = \
            {
              'execute': ('explore_changed', self.explore_non_empty),
            }

    def set_action_defaults(self):
        self.action_defaults = \
            { 'execute': [('setEnabled', True, self.set_execute_action),
                          ('setIcon', False, CurrentTheme.EXECUTE_EXPLORE_ICON),
                          ('setToolTip', False, 'Execute the parameter exploration')],
            }
            
    def set_execute_action(self):
        if self.controller and self.controller.vistrail:
            versionId = self.controller.current_version
            return self.controller.vistrail.get_paramexp(versionId) != None
        return False
    
    def explore_non_empty(self, on):
        return on
    
    def exploreChange(self, on):
        from gui.vistrails_window import _app
        _app.notify('explore_changed', on)
        
    def execute(self):
        """ execute() -> None        
        Perform the exploration by collecting a list of actions
        corresponding to each dimension
        
        """
        registry = get_module_registry()
        actions = self.table.collectParameterActions()
        palette = self.get_palette()
        # Set the annotation to persist the parameter exploration
        # TODO: For now, we just replace the existing exploration - Later we should append them.
        xmlString = "<paramexps>\n" + self.getParameterExploration() + "\n</paramexps>"
        self.controller.vistrail.set_paramexp(self.controller.current_version, xmlString)
        self.controller.set_changed(True)

        if palette.pipeline and actions:
            explorer = ActionBasedParameterExploration()
            (pipelines, performedActions) = explorer.explore(
                palette.pipeline, actions)
            
            dim = [max(1, len(a)) for a in actions]
            if (registry.has_module('edu.utah.sci.vistrails.spreadsheet', 'CellLocation') and
                registry.has_module('edu.utah.sci.vistrails.spreadsheet', 'SheetReference')):
                modifiedPipelines = palette.virtual_cell.positionPipelines(
                    'PE#%d %s' % (QParamExploreView.explorationId,
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

            QParamExploreView.explorationId += 1
            interpreter = get_default_interpreter()
            for pi in xrange(len(modifiedPipelines)):
                progress.setValue(mCount[pi])
                QtCore.QCoreApplication.processEvents()
                if progress.wasCanceled():
                    break
                def moduleExecuted(objId):
                    if not progress.wasCanceled():
                        progress.setValue(progress.value()+1)
                        QtCore.QCoreApplication.processEvents()
                kwargs = {'locator': self.controller.locator,
                          'current_version': self.controller.current_version,
                          'view': palette.pipeline_view.scene(),
                          'module_executed_hook': [moduleExecuted],
                          'reason': 'Parameter Exploration',
                          'actions': performedActions[pi],
                          }
                interpreter.execute(modifiedPipelines[pi], **kwargs)
            progress.setValue(totalProgress)
        
        
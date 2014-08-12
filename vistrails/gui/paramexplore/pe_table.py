###############################################################################
##
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
from getpass import getuser

from PyQt4 import QtCore, QtGui
from ast import literal_eval
from xml.dom.minidom import parseString
from xml.sax.saxutils import escape, unescape
from vistrails.gui.theme import CurrentTheme
from vistrails.gui.common_widgets import QPromptWidget
from vistrails.gui.modules.paramexplore import QParameterEditor
from vistrails.gui.paramexplore.param_view import QParameterTreeWidget
from vistrails.gui.utils import show_warning
from vistrails.core import debug
from vistrails.core.modules.basic_modules import Constant
from vistrails.core.modules.module_registry import get_module_registry
from vistrails.core.system import current_time, strftime
from vistrails.core.paramexplore.param import PEParam
from vistrails.core.paramexplore.function import PEFunction
from vistrails.core.vistrail.module import Module as VistrailModule
from vistrails.core.paramexplore.paramexplore import ParameterExploration
import vistrails.core.db.action

""" The file describes the parameter exploration table for VisTrails

QParameterExplorationTable
"""


################################################################################
class QParameterExplorationWidget(QtGui.QScrollArea):
    """
    QParameterExplorationWidget is a place holder for
    QParameterExplorationTable

    is a grid layout widget having 4 comlumns corresponding to 4
    dimensions of exploration. It accept method/alias drops and can be
    fully configured onto any dimension. For each parameter, 3
    different approach can be chosen to assign the value of that
    parameter during the exploration: linear interpolation (for int,
    float), list (for int, float, string and boolean) and user-define
    function (for int, float, string and boolean)
    
    """
    def __init__(self, parent=None):
        """ QParameterExplorationWidget(parent: QWidget)
                                       -> QParameterExplorationWidget
        Put the QParameterExplorationTable as a main widget
        
        """
        QtGui.QScrollArea.__init__(self, parent)
        self.setAcceptDrops(True)
        self.setWidgetResizable(True)
        self.table = QParameterExplorationTable()
        self.setWidget(self.table)

    def dragEnterEvent(self, event):
        """ dragEnterEvent(event: QDragEnterEvent) -> None
        Set to accept drops from the parameter list
        
        """
        if isinstance(event.source(), QParameterTreeWidget):
            data = event.mimeData()
            if hasattr(data, 'items'):
                event.accept()
                return
        event.ignore()
        
    def dropEvent(self, event):
        """ dropEvent(event: QDragMoveEvent) -> None
        Accept drop event to add a new method
        
        """
        if isinstance(event.source(), QParameterTreeWidget):
            data = event.mimeData()
            if hasattr(data, 'items'):
                event.accept()
                self.setFocus()
                for item in data.items:
                    self.table.addParameter(item.parameter)
            vsb = self.verticalScrollBar()
            vsb.setValue(vsb.maximum())

    def updatePipeline(self, pipeline):
        """ updatePipeline(pipeline: Pipeline) -> None
        Assign a pipeline to the table
        
        """
        self.table.setPipeline(pipeline)
        # Update the UI with the most recent parameter exploration
        if self.controller:
            currentVersion = self.controller.current_version
            pe = self.controller.vistrail.get_paramexp(currentVersion)
            self.controller.current_parameter_exploration = pe
            self.setParameterExploration(pe)

    def getParameterExplorationOld(self):
        """ getParameterExploration() -> string
        Generates an XML string that represents the current
        parameter exploration, and which can be loaded with
        setParameterExploration().
        
        """
        # Construct xml for persisting parameter exploration
        escape_dict = { "'":"&apos;", '"':'&quot;', '\n':'&#xa;' }
        timestamp = strftime(current_time(), '%Y-%m-%d %H:%M:%S')
        palette = self.get_palette()
        # TODO: For now, we use the timestamp as the 'name' - Later, we should set 'name' based on a UI input field
        xml = '\t<paramexp dims="%s" layout="%s" date="%s" name="%s">' % (str(self.table.label.getCounts()), str(palette.virtual_cell.getConfiguration()[2]), timestamp, timestamp)
        for i in xrange(self.table.layout().count()):
            pEditor = self.table.layout().itemAt(i).widget()
            if pEditor and isinstance(pEditor, QParameterSetEditor):
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
                    if intType in ['Linear Interpolation', 'RGB Interpolation',
                                   'HSV Interpolation']:
                        xml += ' min="%s" max="%s"' % (interpolator.fromEdit.get_value(), interpolator.toEdit.get_value())
                    elif intType == 'List':
                        xml += ' values="%s"' % escape(str(interpolator._str_values), escape_dict)
                    elif intType == 'User-defined Function':
                        xml += ' code="%s"' % escape(interpolator.function, escape_dict)
                    xml += '/>'
                xml += '\n\t\t</function>'
        xml += '\n\t</paramexp>'
        return xml
    
    def getParameterExploration(self):
        """ getParameterExploration() -> ParameterExploration
        Generates a ParameterExploration object hat represents the current
        parameter exploration, and which can be loaded with
        setParameterExploration().
        
        """
        # Construct xml for persisting parameter exploration
        escape_dict = { "'":"&apos;", '"':'&quot;', '\n':'&#xa;' }
        palette = self.get_palette()
        id_scope = self.controller.id_scope
        functions = []
        for i in xrange(self.table.layout().count()):
            pEditor = self.table.layout().itemAt(i).widget()
            if pEditor and isinstance(pEditor, QParameterSetEditor):
                function = None
                firstParam = True
                for paramWidget in pEditor.paramWidgets:
                    paramInfo = paramWidget.param
                    interpolator = paramWidget.editor.stackedEditors.currentWidget()
                    intType = interpolator.exploration_name
                    # Write function tag prior to the first parameter of the function
                    if firstParam:
                        function = PEFunction(id=id_scope.getNewId(PEFunction.vtType),
                                              module_id=paramInfo.module_id,
                                              port_name=paramInfo.name,
                                              is_alias = 1 if paramInfo.is_alias else 0)
                        firstParam = False

                    if intType in ['Linear Interpolation', 'RGB Interpolation',
                                   'HSV Interpolation']:
                        value = '["%s", "%s"]' % (interpolator.fromEdit.get_value(),
                                                  interpolator.toEdit.get_value())
                    elif intType == 'List':
                        value = '%s' % escape(str(interpolator._str_values), escape_dict)
                    elif intType == 'User-defined Function':
                        value ='%s' % escape(interpolator.function, escape_dict)
                    # Write parameter tag
                    param = PEParam(id=id_scope.getNewId(PEParam.vtType),
                                    pos=paramInfo.pos,
                                    interpolator=intType,
                                    value=value,
                                    dimension=paramWidget.getDimension())
                    function.addParameter(param)
                functions.append(function)
        pe = ParameterExploration(dims=str(self.table.label.getCounts()),
                      layout=repr(palette.virtual_cell.getConfiguration()[2]),
                      date=current_time(),
                      user=getuser(),
                      functions=functions)
        return pe

    def setParameterExploration(self, pe, update_inspector=True):
        """ setParameterExploration(pe: ParameterExploration) -> None
        Sets the current parameter exploration to the one defined by pe
        
        """
        self.table.clear()
        palette = self.get_palette()
        if update_inspector:
            palette.stateChanged()
        if not pe:
            return
        unescape_dict = { "&apos;":"'", '&quot;':'"', '&#xa;':'\n' }
        paramView = self.get_param_view()
        # Set the exploration dimensions
        self.table.label.setCounts(pe.dims)
        # Set the virtual cell layout
        palette.virtual_cell.setConfiguration(pe.layout)
        # Populate parameter exploration window with stored functions and aliases
        for f in pe.functions:
            # Search the parameter treeWidget for this function and add it directly
            newEditor = None
            for tidx in xrange(paramView.treeWidget.topLevelItemCount()):
                moduleItem = paramView.treeWidget.topLevelItem(tidx)
                for cidx in xrange(moduleItem.childCount()):
                    paramInfo = moduleItem.child(cidx).parameter
                    name, params = paramInfo
                    if params[0].module_id == f.module_id and \
                       params[0].name == f.port_name and \
                       params[0].is_alias == f.is_alias:
                        newEditor = self.table.addParameter(paramInfo)
                        
            # Retrieve params for this function and set their values in the UI
            if newEditor:
                for p in f.parameters:
                    # Locate the param in the newly added param editor and set values
                    for paramWidget in newEditor.paramWidgets:
                        if paramWidget.param.pos == p.pos:
                            # Set Parameter Dimension (radio button)
                            paramWidget.setDimension(p.dimension)
                            # Set Interpolator Type (dropdown list)
                            paramWidget.editor.selectInterpolator(p.interpolator)
                            # Set Interpolator Value(s)
                            interpolator = paramWidget.editor.stackedEditors.currentWidget()
                            if p.interpolator in ['Linear Interpolation',
                                                  'RGB Interpolation',
                                                  'HSV Interpolation']:
                                try:
                                    # Set min/max
                                    i_range = literal_eval('%s' % unescape(
                                                           p.value,
                                                           unescape_dict))
                                    p_min = str(i_range[0])
                                    p_max =str(i_range[1])
                                    interpolator.fromEdit.set_value(p_min)
                                    interpolator.toEdit.set_value(p_max)
                                except Exception:
                                    pass
                            elif p.interpolator == 'List':
                                p_values = '%s' % unescape(p.value,
                                                        unescape_dict)
                                # Set internal list structure
                                interpolator._str_values = \
                                        literal_eval(p_values)
                                # Update UI list
                                if interpolator.type == 'String':
                                    interpolator.listValues.setText(p_values)
                                else:
                                    interpolator.listValues.setText(
                                     p_values.replace("'","").replace('"',''))
                            elif p.interpolator == 'User-defined Function':
                                # Set function code
                                interpolator.function = '%s' % unescape(
                                                  str(p.value), unescape_dict)

    def setParameterExplorationOld(self, xmlString):
        """ setParameterExploration(xmlString: string) -> None
        Sets the current parameter exploration to the one
        defined by 'xmlString'.
        
        """
        if not xmlString:
            return
        # Parse/validate the xml
        try:
            xmlDoc = parseString(xmlString).documentElement
        except Exception, e:
            debug.unexpected_exception(e)
            debug.critical("Parameter Exploration load failed because of "
                           "invalid XML:\n\n%s" % xmlString)
            return
        palette = self.get_palette()
        paramView = self.get_param_view()
        # Set the exploration dimensions
        dims = literal_eval(xmlDoc.attributes['dims'].value)
        self.table.label.setCounts(dims)
        # Set the virtual cell layout
        layout = literal_eval(xmlDoc.attributes['layout'].value)
        palette.virtual_cell.setConfiguration(layout)
        # Populate parameter exploration window with stored functions and aliases
        for f in xmlDoc.getElementsByTagName('function'):
            # Retrieve function attributes
            f_id = long(f.attributes['id'].value)
            f_name = str(f.attributes['name'].value)
            f_is_alias = (str(f.attributes['alias'].value) == 'True')
            # Search the parameter treeWidget for this function and add it directly
            newEditor = None
            for tidx in xrange(paramView.treeWidget.topLevelItemCount()):
                moduleItem = paramView.treeWidget.topLevelItem(tidx)
                for cidx in xrange(moduleItem.childCount()):
                    paramInfo = moduleItem.child(cidx).parameter
                    name, params = paramInfo
                    if params[0].parent_id == f_id and params[0].is_alias == f_is_alias:
                        newEditor = self.table.addParameter(paramInfo)
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
                            if p_intType in ['Linear Interpolation', 'RGB Interpolation',
                                             'HSV Interpolation']:
                                try:
                                    # Set min/max
                                    p_min = str(p.attributes['min'].value)
                                    p_max = str(p.attributes['max'].value)
                                    interpolator.fromEdit.set_value(p_min)
                                    interpolator.toEdit.set_value(p_max)
                                except Exception:
                                    pass
                            elif p_intType == 'List':
                                p_values = str(p.attributes['values'].value)
                                # Set internal list structure
                                interpolator._str_values = literal_eval(p_values)
                                # Update UI list
                                if interpolator.type == 'String':
                                    interpolator.listValues.setText(p_values)
                                else:
                                    interpolator.listValues.setText(p_values.replace("'", "").replace('"', ''))
                            elif p_intType == 'User-defined Function':
                                # Set function code
                                p_code = str(p.attributes['code'].value)
                                interpolator.function = p_code

    def get_palette(self):
        from vistrails.gui.paramexplore.pe_inspector import QParamExploreInspector
        return QParamExploreInspector.instance()
    
    def get_param_view(self):
        from vistrails.gui.paramexplore.param_view import QParameterView
        return QParameterView.instance()
    
class QParameterExplorationTable(QPromptWidget):
    """
    QParameterExplorationTable is a grid layout widget having 4
    comlumns corresponding to 4 dimensions of exploration. It accept
    method/alias drops and can be fully configured onto any
    dimension. For each parameter, 3 different approach can be chosen
    to assign the value of that parameter during the exploration:
    linear interpolation (for int, float), list (for int, float,
    string and boolean) and user-define function (for int, float,
    string and boolean)
    
    """
    def __init__(self, parent=None):
        """ QParameterExplorationTable(parent: QWidget)
                                       -> QParameterExplorationTable
        Create an grid layout and accept drops
        
        """
        QPromptWidget.__init__(self, parent)
        self.pipeline = None
        self.setSizePolicy(QtGui.QSizePolicy.Expanding,
                           QtGui.QSizePolicy.Expanding)
        self.setPromptText('Drag aliases/parameters here for a parameter '
                           'exploration')
        self.showPrompt()
        
        vLayout = QtGui.QVBoxLayout(self)
        vLayout.setSpacing(0)
        vLayout.setMargin(0)
        vLayout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(vLayout)

        self.label = QDimensionLabel()

        for labelIcon in self.label.labelIcons:
            self.connect(labelIcon.countWidget,
                         QtCore.SIGNAL('editingFinished()'),
                         self.updateWidgets)
        vLayout.addWidget(self.label)

        for i in xrange(2):
            hBar = QtGui.QFrame()
            hBar.setFrameStyle(QtGui.QFrame.HLine | QtGui.QFrame.Sunken)
            vLayout.addWidget(hBar)
        self._parameterCount = 0

    def addParameter(self, paramInfo):
        """ addParameter(paramInfo: (str, [ParameterInfo]) -> None
        Add a parameter to the table. The parameter info is specified
        in QParameterTreeWidgetItem
        
        """
        # Check to see paramInfo is not a subset of some other parameter set
        params = paramInfo[1]
        for i in xrange(self.layout().count()):
            pEditor = self.layout().itemAt(i).widget()
            if pEditor and isinstance(pEditor, QParameterSetEditor):
                subset = True
                for p in params:
                    if not (p in pEditor.info[1]):
                        subset = False
                        break                    
                if subset:
                    show_warning('Parameter Exists',
                                 'The parameter you are trying to add is '
                                 'already in the list.')
                    return
        self.showPrompt(False)
        newEditor = QParameterSetEditor(paramInfo, self)

        # Make sure to disable all duplicated parameter
        for p in xrange(len(params)):
            for i in xrange(self.layout().count()):
                pEditor = self.layout().itemAt(i).widget()
                if pEditor and isinstance(pEditor, QParameterSetEditor):
                    if params[p] in pEditor.info[1]:
                        widget = newEditor.paramWidgets[p]
                        widget.setDimension(4)
                        widget.setDuplicate(True)
                        widget.setEnabled(False)
                        break
        
        self.layout().addWidget(newEditor)
        newEditor.show()
        self.setMinimumHeight(self.layout().minimumSize().height())
        self.emit(QtCore.SIGNAL('exploreChange(bool)'), self.layout().count() > 3)
        return newEditor

    def removeParameter(self, ps):
        """ removeParameterSet(ps: QParameterSetEditor) -> None
        Remove a parameter set from the table and validate the rest
        
        """
        self.layout().removeWidget(ps)
        # Restore disabled parameter
        for i in xrange(self.layout().count()):
            pEditor = self.layout().itemAt(i).widget()
            if pEditor and isinstance(pEditor, QParameterSetEditor):
                for p in xrange(len(pEditor.info[1])):
                    param = pEditor.info[1][p]
                    widget = pEditor.paramWidgets[p]                    
                    if (param in ps.info[1] and (not widget.isEnabled())):
                        widget.setDimension(0)
                        widget.setDuplicate(False)
                        widget.setEnabled(True)
                        break
        self.showPrompt(self.layout().count()<=3)
        self.emit(QtCore.SIGNAL('exploreChange(bool)'), self.layout().count() > 3)

    def updateWidgets(self):
        """ updateWidgets() -> None
        Update all widgets to reflect the step count
        
        """
        # Go through all possible parameter widgets
        counts = self.label.getCounts()
        for i in xrange(self.layout().count()):
            pEditor = self.layout().itemAt(i).widget()
            if pEditor and isinstance(pEditor, QParameterSetEditor):
                for paramWidget in pEditor.paramWidgets:
                    dim = paramWidget.getDimension()
                    if dim in [0, 1, 2, 3]:
                        se = paramWidget.editor.stackedEditors
                        # Notifies editor widgets of size update 
                        for i in xrange(se.count()):
                            wd = se.widget(i)
                            if hasattr(wd, 'size_was_updated'):
                                wd.size_was_updated(counts[dim])

    def clear(self):
        """ clear() -> None
        Clear all widgets
        
        """
        for i in reversed(range(self.layout().count())):
            pEditor = self.layout().itemAt(i).widget()
            if pEditor and isinstance(pEditor, QParameterSetEditor):
                pEditor.table = None
                self.layout().removeWidget(pEditor)
                pEditor.hide()
                pEditor.deleteLater()
        self.label.resetCounts()
        self.showPrompt()
        self.emit(QtCore.SIGNAL('exploreChange(bool)'), self.layout().count() > 3)

    def setPipeline(self, pipeline):
        """ setPipeline(pipeline: Pipeline) -> None
        Assign a pipeline to the current table
        
        """
        if pipeline:
            to_be_deleted = []
            for i in xrange(self.layout().count()):
                pEditor = self.layout().itemAt(i).widget()
                if pEditor and isinstance(pEditor, QParameterSetEditor):
                    for param in pEditor.info[1]:
                        # We no longer require the parameter to exist
                        # we check if the module still exists
                        if not pipeline.db_has_object(VistrailModule.vtType,
                                                      param.module_id):
                            to_be_deleted.append(pEditor)
            for pEditor in to_be_deleted:
                pEditor.removeSelf()
        else:
            self.clear()
        self.pipeline = pipeline
        self.label.setEnabled(self.pipeline!=None)

    def collectParameterActions(self):
        """ collectParameterActions() -> list
        Return a list of action lists corresponding to each dimension
        
        """
        if not self.pipeline:
            return None

        reg = get_module_registry()
        parameterValues = [[], [], [], []]
        counts = self.label.getCounts()
        for i in xrange(self.layout().count()):
            pEditor = self.layout().itemAt(i).widget()
            if pEditor and isinstance(pEditor, QParameterSetEditor):
                for paramWidget in pEditor.paramWidgets:
                    editor = paramWidget.editor
                    interpolator = editor.stackedEditors.currentWidget()
                    paramInfo = paramWidget.param
                    dim = paramWidget.getDimension()
                    if dim in [0, 1, 2, 3]:
                        count = counts[dim]
                        values = interpolator.get_values(count)
                        if not values:
                            return None
                        pId = paramInfo.id
                        pType = paramInfo.dbtype
                        parentType = paramInfo.parent_dbtype
                        parentId = paramInfo.parent_id
                        function = self.pipeline.db_get_object(parentType,
                                                               parentId)  
                        fName = function.name
                        old_param = self.pipeline.db_get_object(pType,pId)
                        pName = old_param.name
                        pAlias = old_param.alias
                        pIdentifier = old_param.identifier
                        actions = []
                        tmp_id = -1L
                        for v in values:
                            getter = reg.get_descriptor_by_name
                            desc = getter(paramInfo.identifier,
                                          paramInfo.type,
                                          paramInfo.namespace)
                            if not isinstance(v, str):
                                str_value = desc.module.translate_to_string(v)
                            else:
                                str_value = v
                            new_param = ModuleParam(id=tmp_id,
                                                    pos=old_param.pos,
                                                    name=pName,
                                                    alias=pAlias,
                                                    val=str_value,
                                                    type=paramInfo.type,
                                                    identifier=pIdentifier
                                                    )
                            action_spec = ('change', old_param, new_param,
                                           parentType, function.real_id)
                            action = vistrails.core.db.action.create_action([action_spec])
                            actions.append(action)
                        parameterValues[dim].append(actions)
                        tmp_id -= 1
        return [zip(*p) for p in parameterValues]

class QDimensionLabel(QtGui.QWidget):
    """
    QDimensionLabel represents a horizontal header item of the
    parameter window. It has 4 small icons represents the dimensions
    and a Skip label. It represents a group box.
    
    """
    def __init__(self, parent=None):
        """ QDimensionLabel(parent: QWidget) -> None
        Initialize icons and labels
        
        """
        QtGui.QWidget.__init__(self, parent)
        self.setAutoFillBackground(True)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding,
                           QtGui.QSizePolicy.Maximum)

        hLayout = QtGui.QHBoxLayout(self)
        hLayout.setMargin(0)
        hLayout.setSpacing(0)
        self.setLayout(hLayout)        

        self.params = QDimensionLabelText('Parameters')
        hLayout.addWidget(self.params)
        self.params.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                  QtGui.QSizePolicy.Expanding)
        hLayout.addWidget(QDimensionLabelSeparator())
        
        pixes = [CurrentTheme.EXPLORE_COLUMN_PIXMAP,
                 CurrentTheme.EXPLORE_ROW_PIXMAP,
                 CurrentTheme.EXPLORE_SHEET_PIXMAP,
                 CurrentTheme.EXPLORE_TIME_PIXMAP]
        self.labelIcons = []
        for pix in pixes:
            labelIcon = QDimensionLabelIcon(pix)
            hLayout.addWidget(labelIcon)
            self.labelIcons.append(labelIcon)            
            hLayout.addWidget(QDimensionLabelSeparator())

        hLayout.addWidget(QDimensionLabelIcon(CurrentTheme.EXPLORE_SKIP_PIXMAP,
                                              False))

    def getCounts(self):
        """ getCounts() -> [int]        
        Return a list of 4 ints denoting the step count desired for
        each dimension
        
        """
        return [l.countWidget.value() for l in self.labelIcons]

    def setCounts(self, counts):
        """ setCounts(counts:list) -> None
        Set the 4 step counts for each dimension from a list of 4 ints

        """
        dim = len(self.getCounts())
        if len(counts) != dim:
            return
        for i in xrange(0, dim):
            self.labelIcons[i].countWidget.setValue(counts[i])

    def resetCounts(self):
        """ resetCounts() -> None
        Reset all counts to 1
        
        """
        for l in self.labelIcons:
            l.countWidget.setValue(1)
    
class QDimensionSpinBox(QtGui.QSpinBox):
    """
    QDimensionSpinBox is just an overrided spin box that will also emit
    'editingFinished()' signal when the user interact with mouse
    
    """    
    def mouseReleaseEvent(self, event):
        """ mouseReleaseEvent(event: QMouseEvent) -> None
        Emit 'editingFinished()' signal when the user release a mouse button
        
        """
        QtGui.QSpinBox.mouseReleaseEvent(self, event)
        # super(QDimensionSpinBox, self).mouseReleaseEvent(event)
        self.emit(QtCore.SIGNAL("editingFinished()"))

class QDimensionLabelIcon(QtGui.QWidget):
    """
    QDimensionLabelIcon describes those icons staying on the header
    view of the table
    
    """
    def __init__(self, pix, hasCount = True, parent=None):
        """ QDimensionalLabelIcon(pix: QPixmap, hasCount: bool, parent: QWidget)
                                  -> QDimensionalLabelIcon
        Using size 32x32 and a margin of 2
        
        """
        QtGui.QWidget.__init__(self, parent)
        layout = QtGui.QVBoxLayout()
        layout.setMargin(0)
        layout.setSpacing(0)
        self.setLayout(layout)

        label = QtGui.QLabel()
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setPixmap(pix.scaled(32, 32, QtCore.Qt.KeepAspectRatio,
                                  QtCore.Qt.SmoothTransformation))
        layout.addWidget(label)

        if hasCount:
            self.countWidget = QDimensionSpinBox()
            self.countWidget.setFixedWidth(32)
            self.countWidget.setRange(1, 10000000)
            self.countWidget.setAlignment(QtCore.Qt.AlignRight)
            self.countWidget.setFrame(False)
            pal = QtGui.QPalette(self.countWidget.lineEdit().palette())
            pal.setBrush(QtGui.QPalette.Base,
                         QtGui.QBrush(QtCore.Qt.NoBrush))
            self.countWidget.lineEdit().setPalette(pal)
            layout.addWidget(self.countWidget)
            
        self.setSizePolicy(QtGui.QSizePolicy.Maximum,
                            QtGui.QSizePolicy.Maximum)        
                
class QDimensionLabelText(QtGui.QWidget):
    """
    QDimensionLabelText describes those texts staying on the header
    view of the table. It also has a button to perform exploration
    
    """
    def __init__(self, text, parent=None):
        """ QDimensionalLabelText(text: str, parent: QWidget)
                                   -> QDimensionalLabelText
        Putting the text bold in the center
        
        """
        QtGui.QWidget.__init__(self, parent)
        hLayout = QtGui.QHBoxLayout()
        self.setLayout(hLayout)

        hLayout.addStretch()
        
        hLayout.addWidget(QtGui.QLabel('<b>Parameters</b>'))

        hLayout.addStretch()
        
        
class QDimensionLabelSeparator(QtGui.QFrame):
    """
    QDimensionLabelSeparator is acting as a vertical separator which
    has an appropriate style to go with the QDimensionalLabel
    
    """
    def __init__(self, parent=None):
        """ QDimensionalLabelSeparator(parent: QWidget)
                                       -> QDimensionalLabelSeparator
        Make sure the frame only has a width of 2
        
        """
        QtGui.QFrame.__init__(self, parent)
        self.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Sunken)
        self.setFixedWidth(2)

class QParameterSetEditor(QtGui.QWidget):
    """
    QParameterSetEditor is a widget controlling a set of
    parameters. The set can contain a single parameter (aliases) or
    multiple of them (module methods).
    
    """
    def __init__(self, info, table=None, parent=None):
        """ QParameterSetEditor(info: paraminfo,
                                table: QParameterExplorationTable,
                                parent: QWidget)
                                -> QParameterSetEditor
        Construct a parameter editing widget based on the paraminfo
        (described in QParameterTreeWidgetItem)
        
        """
        QtGui.QWidget.__init__(self, parent)
        self.info = info
        self.table = table
        (name, paramList) = info
        if table:
            size = table.label.getCounts()[0]
        else:
            size = 1
        
        vLayout = QtGui.QVBoxLayout(self)
        vLayout.setMargin(0)
        vLayout.setSpacing(0)
        self.setLayout(vLayout)

        label = QParameterSetLabel(name)
        self.connect(label.removeButton, QtCore.SIGNAL('clicked()'),
                     self.removeSelf)
        vLayout.addWidget(label)
        
        self.paramWidgets = []
        for param in paramList:
            paramWidget = QParameterWidget(param, size)
            vLayout.addWidget(paramWidget)
            self.paramWidgets.append(paramWidget)

        vLayout.addSpacing(10)

        hBar = QtGui.QFrame()
        hBar.setFrameStyle(QtGui.QFrame.HLine | QtGui.QFrame.Sunken)
        vLayout.addWidget(hBar)

    def removeSelf(self):
        """ removeSelf() -> None
        Remove itself out of the parent layout()
        
        """
        if self.table:
            self.table.removeParameter(self)            
            self.table = None
            self.close()
            self.deleteLater()

class QParameterSetLabel(QtGui.QWidget):
    """
    QParameterSetLabel is the label bar showing at the top of the
    parameter set editor. It also has a Remove button to remove the
    parameter
    
    """
    def __init__(self, text, parent=None):
        """ QParameterSetLabel(text: str, parent: QWidget) -> QParameterSetLabel
        Init a label and a button
        
        """
        QtGui.QWidget.__init__(self, parent)        
        hLayout = QtGui.QHBoxLayout(self)
        hLayout.setMargin(0)
        hLayout.setSpacing(0)
        self.setLayout(hLayout)

        hLayout.addSpacing(5)

        label = QtGui.QLabel(text)
        font = QtGui.QFont(label.font())
        font.setBold(True)
        label.setFont(font)
        hLayout.addWidget(label)

        hLayout.addSpacing(5)
        
        self.removeButton = QtGui.QToolButton()
        self.removeButton.setAutoRaise(True)
        self.removeButton.setIcon(QtGui.QIcon(
            self.style().standardPixmap(QtGui.QStyle.SP_DialogCloseButton)))
        self.removeButton.setIconSize(QtCore.QSize(12, 12))
        self.removeButton.setFixedWidth(16)
        hLayout.addWidget(self.removeButton)

        hLayout.addStretch()
        
class QParameterWidget(QtGui.QWidget):
    """
    QParameterWidget is a row widget containing a label, a parameter
    editor and a radio group.
    
    """
    def __init__(self, param, size, parent=None):
        """ QParameterWidget(param: ParameterInfo, size: int, parent: QWidget)
                             -> QParameterWidget
        """
        QtGui.QWidget.__init__(self, parent)
        self.param = param
        self.prevWidget = 0
        
        hLayout = QtGui.QHBoxLayout(self)
        hLayout.setMargin(0)
        hLayout.setSpacing(0)        
        self.setLayout(hLayout)

        hLayout.addSpacing(5+16+5)

        self.label = QtGui.QLabel(param.spec.module)
        self.label.setFixedWidth(50)
        hLayout.addWidget(self.label)

        registry = get_module_registry()
        module = param.spec.descriptor.module
        assert issubclass(module, Constant)

        self.editor = QParameterEditor(param, size)
        hLayout.addWidget(self.editor)

        self.selector = QDimensionSelector()
        self.connect(self.selector.radioButtons[4],
                     QtCore.SIGNAL('toggled(bool)'),
                     self.disableParameter)
        hLayout.addWidget(self.selector)

    def getDimension(self):
        """ getDimension() -> int        
        Return a number 0-4 indicating which radio button is
        selected. If none is selected (should not be in this case),
        return -1
        
        """
        for i in xrange(5):
            if self.selector.radioButtons[i].isChecked():
                return i
        return -1

    def disableParameter(self, disabled=True):
        """ disableParameter(disabled: bool) -> None
        Disable/Enable this parameter when disabled is True/False
        
        """
        self.label.setEnabled(not disabled)
        self.editor.setEnabled(not disabled)

    def setDimension(self, dim):
        """ setDimension(dim: int) -> None
        Select a dimension for this parameter
        
        """
        if dim in xrange(5):
            self.selector.radioButtons[dim].setChecked(True)

    def setDuplicate(self, duplicate):
        """ setDuplicate(duplicate: True) -> None
        Set if this parameter is a duplicate parameter
        
        """
        if duplicate:
            self.prevWidget = self.editor.stackedEditors.currentIndex()
            self.editor.stackedEditors.setCurrentIndex(3)
        else:
            self.editor.stackedEditors.setCurrentIndex(self.prevWidget)

class QDimensionSelector(QtGui.QWidget):
    """
    QDimensionSelector provides 5 radio buttons to select dimension of
    exploration or just skipping it.
    
    """
    def __init__(self, parent=None):
        """ QDimensionSelector(parent: QWidget) -> QDimensionSelector
        Initialize the horizontal layout and set the width to be fixed
        equal to the QDimensionLabel
        
        """
        QtGui.QWidget.__init__(self, parent)
        self.setSizePolicy(QtGui.QSizePolicy.Maximum,
                           QtGui.QSizePolicy.Maximum)
        
        hLayout = QtGui.QHBoxLayout(self)
        hLayout.setMargin(0)
        hLayout.setSpacing(0)        
        self.setLayout(hLayout)

        self.radioButtons = []
        for i in xrange(5):
            hLayout.addSpacing(2)
            button = QDimensionRadioButton()
            self.radioButtons.append(button)
            button.setFixedWidth(32)
            hLayout.addWidget(button)
        self.radioButtons[0].setChecked(True)

class QDimensionRadioButton(QtGui.QRadioButton):
    """
    QDimensionRadioButton is a replacement of QRadioButton with
    simpler appearance. We just need to override the paint event
    
    """
    def paintEvent(self, event):
        """ paintEvent(event: QPaintEvent) -> None
        Draw an outer circle and another solid one in side
        
        """
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(self.palette().color(QtGui.QPalette.Dark))
        painter.setBrush(QtCore.Qt.NoBrush)
        l = min(self.width()-2, self.height()-2, 12)
        r = QtCore.QRect(0, 0, l, l)
        r.moveCenter(self.rect().center())
        painter.drawEllipse(r)

        if self.isChecked():
            r.adjust(3, 3, -3, -3)
            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(self.palette().color(QtGui.QPalette.WindowText))
            painter.drawEllipse(r)
        
        painter.end()

    def mousePressEvent(self, event):
        """ mousePressEvent(event: QMouseEvent) -> None
        Force toggling the radio button
        
        """
        self.click()

################################################################################

if __name__=="__main__":        
    import sys
    import vistrails.gui.theme
    app = QtGui.QApplication(sys.argv)
    vistrails.gui.theme.initializeCurrentTheme()
    vc = QDimensionLabel(CurrentTheme.EXPLORE_SHEET_PIXMAP, 'Hello World')
    vc.show()
    sys.exit(app.exec_())

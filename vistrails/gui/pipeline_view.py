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
""" This is a QGraphicsView for pipeline view, it also holds different
types of graphics items that are only available in the pipeline
view. It only handles GUI-related actions, the rest of the
functionalities are implemented at somewhere else,
e.g. core.vistrails

QGraphicsConnectionItem
QGraphicsPortItem
QGraphicsConfigureItem
QGraphicsModuleItem
QPipelineScene
QPipelineView
"""

from PyQt4 import QtCore, QtGui
from core.configuration import get_vistrails_configuration
from core import debug
from core.db.action import create_action
from core.system import systemType
from core.utils import profile
from core.vistrail.annotation import Annotation
from gui.modules.module_configure import DefaultModuleConfigurationWidget
from core.modules.module_registry import get_module_registry, \
    ModuleRegistryException

from core.vistrail.port import PortEndPoint
from core.vistrail.port_spec import PortSpec
from core.vistrail.vistrail import Vistrail
from core.interpreter.default import get_default_interpreter
from gui.base_view import BaseView
from gui.controlflow_assist import QControlFlowAssistDialog
from gui.graphics_view import (QInteractiveGraphicsScene,
                               QInteractiveGraphicsView,
                               QGraphicsItemInterface)
from gui.module_annotation import QModuleAnnotation
from gui.module_palette import QModuleTreeWidget
from gui.module_documentation import QModuleDocumentation
from gui.theme import CurrentTheme
from gui.utils import getBuilderWindow
from gui.variable_dropbox import QDragVariableLabel

import copy
import math
import operator


##############################################################################
# 2008-06-24 cscheid
#
#   - Profiling has shown that calling setPen and setBrush takes a longer
#   time than we expected. Watch out for that in the future.

##############################################################################
# QGraphicsPortItem

class QGraphicsPortItem(QtGui.QGraphicsRectItem):
    """
    QGraphicsPortItem is a small port shape drawing on top (a child)
    of QGraphicsModuleItem, it can either be rectangle or rounded
    
    """
    def __init__(self, x, y, ghosted, parent=None, optional=False):
        """ QGraphicsPortItem(parent: QGraphicsItem,
                              optional: bool)
                              -> QGraphicsPortItem
        Create the shape, initialize its pen and brush accordingly
        
        """
        # local lookups are faster than global lookups..
        _rect = CurrentTheme.PORT_RECT
        QtGui.QGraphicsRectItem.__init__(self, _rect.translated(x, y), parent)
        self.setZValue(1)
        self.setFlags(QtGui.QGraphicsItem.ItemIsSelectable)
        if not optional:
            self.paint = self.paintRect
        else:
            self.paint = self.paintEllipse
        self.controller = None
        self.port = None
        self.dragging = False
        self.connection = None
        self.ghosted = None
        self.invalid = None
        self.setGhosted(ghosted)
        self.setInvalid(False)
        self.createActions()

    def setGhosted(self, ghosted):
        """ setGhosted(ghosted: True) -> None
        Set this link to be ghosted or not
        
        """
        if self.ghosted <> ghosted:
            self.ghosted = ghosted
            if ghosted:
                self.setPen(CurrentTheme.GHOSTED_PORT_PEN)
                self.setBrush(CurrentTheme.GHOSTED_PORT_BRUSH)
            else:
                self.setPen(CurrentTheme.PORT_PEN)
                self.setBrush(CurrentTheme.PORT_BRUSH)

    def setInvalid(self, invalid):
        if self.invalid != invalid:
            self.invalid = invalid
            if not self.ghosted:
                if invalid:
                    self.setPen(CurrentTheme.INVALID_PORT_PEN)
                    self.setBrush(CurrentTheme.INVALID_PORT_BRUSH)
                else:
                    self.setPen(CurrentTheme.PORT_PEN)
                    self.setBrush(CurrentTheme.PORT_BRUSH)

    def paintEllipse(self, painter, option, widget=None):
        """ paintEllipse(painter: QPainter, option: QStyleOptionGraphicsItem,
                  widget: QWidget) -> None
        Peform actual painting of the optional port
        
        """
        painter.setBrush(self.brush())
        painter.setPen(self.pen())
        painter.drawEllipse(self.rect())

    def paintRect(self, painter, option, widget=None):
        """ paintRect(painter: QPainter, option: QStyleOptionGraphicsItem,
                  widget: QWidget) -> None
        Peform actual painting of the regular port
        
        """
        QtGui.QGraphicsRectItem.paint(self, painter, option, widget)
    
    def contextMenuEvent(self, event):
        """contextMenuEvent(event: QGraphicsSceneContextMenuEvent) -> None
        Captures context menu event.

        """
        #module = self.controller.current_pipeline.modules[self.moduleId]
        connections = self.controller.get_connections_to(self.controller.current_pipeline, [self.parentItem().module.id], self.port.name)
        for connection in connections:
            if self.scene().modules[connection.source.moduleId].module.has_annotation_with_key('__vistrail_var__'):
                menu = QtGui.QMenu()
                menu.addAction(self.removeVarsAct)
                menu.exec_(event.screenPos())
                break

    def createActions(self):
        """ createActions() -> None
        Create actions related to context menu

        """
        self.removeVarsAct = QtGui.QAction("Disconnect Vistrail Variables", self.scene())
        self.removeVarsAct.setStatusTip("Disconnects Vistrail Variables from the port")
        QtCore.QObject.connect(self.removeVarsAct,
                               QtCore.SIGNAL("triggered()"),
                               self.removeVars)
        
    def removeVars(self):
        # Unhighlight the port
        self.setBrush(CurrentTheme.PORT_BRUSH)
        # Get all connections to vistrail variables for this port
        remove_connections = []
        remove_modules = set()
        connections = self.controller.get_connections_to(self.controller.current_pipeline, [self.parentItem().module.id], self.port.name)
        for connection in connections:
            module_item = self.scene().modules[connection.source.moduleId]
            if module_item.module.has_annotation_with_key('__vistrail_var__'):
                var_connections = self.controller.get_connections_from(self.controller.current_pipeline, [module_item.module.id])
                if len(var_connections) == 1:
                    # Tag variable module for removal if it isn't connected to anything else
                    remove_modules.add(module_item)
                else:
                    # Otherwise just tag the connection for removal
                    remove_connections.append(connection)
        # Get ops for deleting connections to vistrail variables
        ops = []
        if len(remove_connections) > 0:
            self.controller.reset_pipeline_view = False
            idList = [conn.id for conn in remove_connections]
            self.scene()._old_connection_ids.difference_update(set(idList))
            for cId in idList:
                del self.scene().connections[cId]
            ops.extend([('delete', self.controller.current_pipeline.connections[c_id]) for c_id in idList])
        # Get ops for deleting unconnected variable modules
        if len(remove_modules) > 0:
            self.scene().noUpdate = True
            idList = [m.id for m in remove_modules]
            connection_ids = set()
            for m in remove_modules:
                # dependingConnectionItems requires the module item to be in the scene
                self.scene().addItem(m)
                connection_ids.update(m.dependingConnectionItems().iterkeys())
            #update the dependency list on the other side of connections
            connections = []
            for c_id in connection_ids:
                conn = self.scene().connections[c_id]
                connections.append(conn)
                self.scene()._old_connection_ids.remove(c_id)
                del self.scene().connections[c_id]
            ops.extend(self.controller.delete_module_list_ops(self.controller.current_pipeline, idList))
            for (mId, item) in self.scene().modules.items():
                if item in remove_modules:
                    self.scene().remove_module(mId)
        # Create and execute the removal action
        var_action = create_action(ops)
        self.controller.flush_delayed_actions()
        self.controller.add_new_action(var_action)
        self.controller.vistrail.change_description("Disconnected Vistrail Variables", var_action.id)
        self.controller.perform_action(var_action)
        # Handle scene refresh
        self.scene().reset_module_colors()
        if len(remove_connections) > 0:
            self.controller.reset_pipeline_view = True
        if len(remove_modules) > 0:
            self.scene().updateSceneBoundingRect()
            self.scene().update()
            self.scene().noUpdate = False
        # Update the version view node to fit text properly
        version_item = self.controller.vistrail_view.version_view.scene().versions[self.controller.current_version]
        version_item.updateWidthFromLabel()
        # Update the tooltip for this version
        try:
            tooltip = self.port.toolTip()
            self.setToolTip(tooltip)
        except:
            self.setToolTip("ERROR with tool tip")

    def mousePressEvent(self, event):
        """ mousePressEvent(event: QMouseEvent) -> None
        Prepare for dragging a connection
        
        """
        if (self.controller and event.buttons() & QtCore.Qt.LeftButton
            and not self.scene().read_only_mode):
            self.dragging = True
            self.setPen(CurrentTheme.PORT_SELECTED_PEN);
            event.accept()
        QtGui.QGraphicsRectItem.mousePressEvent(self, event)
        # super(QGraphicsPortItem, self).mousePressEvent(event)

    def add_connection_event(self, event):
        """Adds a new connection from a mouseReleaseEvent"""
        snapModuleId = self.connection.snapPort.parentItem().id
        # if self.port.endPoint==PortEndPoint.Source:
        if self.port.type == 'output':
            conn_info = (self.parentItem().id, self.port,
                         snapModuleId, self.connection.snapPort.port)
        elif self.port.type == 'input':
            conn_info = (snapModuleId, self.connection.snapPort.port,
                         self.parentItem().id, self.port)
        conn = self.controller.add_connection(*conn_info)
        scene = self.scene()
        scene.addConnection(conn)
        scene.removeItem(self.connection)
        self.connection.snapPort.setPen(CurrentTheme.PORT_PEN)
        self.connection = None
        scene.reset_module_colors()
        # controller changed pipeline: update ids on scene
        scene._old_connection_ids = \
            set(self.controller.current_pipeline.connections)
        scene._old_module_ids = set(self.controller.current_pipeline.modules)
        
    def mouseReleaseEvent(self, event):
        """ mouseReleaseEvent(event: QMouseEvent) -> None
        Apply the connection
        
        """
        if self.connection and self.connection.snapPort and self.controller:
            self.add_connection_event(event)
        if self.connection:
            self.scene().removeItem(self.connection)
            self.connection = None
        self.dragging = False
        self.setPen(CurrentTheme.PORT_PEN)
        QtGui.QGraphicsRectItem.mouseReleaseEvent(self, event)
        # super(QGraphicsPortItem, self).mouseReleaseEvent(event)
        
    def mouseMoveEvent(self, event):
        """ mouseMoveEvent(event: QMouseEvent) -> None
        Change the connection
        
        """
        if self.dragging:
            if not self.connection:
                self.connection = QtGui.QGraphicsLineItem(None, self.scene())
                self.connection.setPen(CurrentTheme.CONNECTION_SELECTED_PEN)
                modules = self.controller.current_pipeline.modules
                max_module_id = max([x for
                                     x in modules.iterkeys()])
                self.connection.setZValue(max_module_id + 1)
                self.connection.snapPort = None
            startPos = self.sceneBoundingRect().center()
            endPos = event.scenePos()
            # Return connected port to unselected color
            if (self.connection.snapPort):
                self.connection.snapPort.setPen(CurrentTheme.PORT_PEN)
            # Find new connected port
            self.connection.snapPort = self.findSnappedPort(endPos)
            if self.connection.snapPort:
                endPos = self.connection.snapPort.sceneBoundingRect().center()
                QtGui.QToolTip.showText(event.screenPos(),
                                        self.connection.snapPort.toolTip())
                # Change connected port to selected color
                self.connection.snapPort.setPen(
                    CurrentTheme.PORT_SELECTED_PEN)
            else:
                QtGui.QToolTip.hideText()
            self.connection.prepareGeometryChange()
            self.connection.setLine(startPos.x(), startPos.y(),
                                    endPos.x(), endPos.y())
        QtGui.QGraphicsRectItem.mouseMoveEvent(self, event)
        # super(QGraphicsPortItem, self).mouseMoveEvent(event)
        
    def findModuleUnder(self, pos, scene=None):
        """ findModuleUnder(pos: QPoint) -> QGraphicsItem
        Search all items under pos and return the top-most module item if any
        
        """
        if scene is None:
            scene = self.scene()
        itemsUnder = scene.items(pos)
        for item in itemsUnder:
            if type(item)==QGraphicsModuleItem:
                return item
        return None
        
    def findSnappedPort(self, pos, scene=None):
        """ findSnappedPort(pos: QPoint) -> Port        
        Search all ports of the module under mouse cursor (if any) to
        find the closest matched port
        
        """
        # FIXME don't hardcode input/output strings...
        snapModule = self.findModuleUnder(pos, scene)
        if snapModule and snapModule!=self.parentItem():
            if self.port.type == 'output':
                return snapModule.getDestPort(pos, self.port)
            elif self.port.type == 'input':
                return snapModule.getSourcePort(pos, self.port)
        else:
            return None
        
    def itemChange(self, change, value):
        """ itemChange(change: GraphicsItemChange, value: QVariant) -> QVariant
        Do not allow port to be selected

        """
        if change==QtGui.QGraphicsItem.ItemSelectedChange and value.toBool():
            return QtCore.QVariant(False)
        return QtGui.QGraphicsRectItem.itemChange(self, change, value)


################################################################################
# QGraphicsConfigureItem

class QGraphicsConfigureItem(QtGui.QGraphicsPolygonItem):
    """
    QGraphicsConfigureItem is a small triangle shape drawing on top (a child)
    of QGraphicsModuleItem
    
    """
    def __init__(self, parent=None, scene=None):
        """ QGraphicsConfigureItem(parent: QGraphicsItem, scene: QGraphicsScene)
                              -> QGraphicsConfigureItem
        Create the shape, initialize its pen and brush accordingly
        
        """
        _pen = CurrentTheme.CONFIGURE_PEN
        _brush = CurrentTheme.CONFIGURE_BRUSH
        _shape = CurrentTheme.CONFIGURE_SHAPE
        QtGui.QGraphicsPolygonItem.__init__(self, _shape, parent, scene)
        self.setZValue(1)
        self.setPen(_pen)
        self.setBrush(_brush)
        self.ghosted = False
        self.controller = None
        self.moduleId = None
        self.is_breakpoint = False
        self.createActions()

    def setGhosted(self, ghosted):
        """ setGhosted(ghosted: Bool) -> None
        Set this link to be ghosted or not
        
        """
        if ghosted <> self.ghosted:
            self.ghosted = ghosted
            if ghosted:
                self.setPen(CurrentTheme.GHOSTED_CONFIGURE_PEN)
                self.setBrush(CurrentTheme.GHOSTED_CONFIGURE_BRUSH)
            else:
                self.setPen(CurrentTheme.CONFIGURE_PEN)
                self.setBrush(CurrentTheme.CONFIGURE_BRUSH)

    def setBreakpoint(self, breakpoint):
        if self.is_breakpoint != breakpoint:
            if breakpoint:
                self.setBreakpointAct.setText("Remove Breakpoint")
                self.setBreakpointAct.setStatusTip("Remove Breakpoint")
            else:
                self.setBreakpointAct.setText("Set Breakpoint")
                self.setBreakpointAct.setStatusTip("Set Breakpoint")

    def mousePressEvent(self, event):
        """ mousePressEvent(event: QMouseEvent) -> None
        Open the context menu
        
        """
        self.scene().clearSelection()
        self.parentItem().setSelected(True)
        self.contextMenuEvent(event)
        
    def contextMenuEvent(self, event):
        """contextMenuEvent(event: QGraphicsSceneContextMenuEvent) -> None
        Captures context menu event.

        """
        module = self.controller.current_pipeline.modules[self.moduleId]
        menu = QtGui.QMenu()
        menu.addAction(self.configureAct)
        menu.addAction(self.annotateAct)
        menu.addAction(self.viewDocumentationAct)
        menu.addAction(self.changeModuleLabelAct)
        menu.addAction(self.setBreakpointAct)
        menu.addAction(self.setWatchedAct)
        menu.addAction(self.setErrorAct)
        if module.is_abstraction() and not module.is_latest_version():
            menu.addAction(self.upgradeAbstractionAct)
        menu.exec_(event.screenPos())

    def createActions(self):
        """ createActions() -> None
        Create actions related to context menu 

        """
        self.configureAct = QtGui.QAction("Edit Configuration\tCtrl+E", self.scene())
        self.configureAct.setStatusTip("Edit the Configure of the module")
        QtCore.QObject.connect(self.configureAct, 
                               QtCore.SIGNAL("triggered()"),
                               self.configure)
        self.annotateAct = QtGui.QAction("Annotate", self.scene())
        self.annotateAct.setStatusTip("Annotate the module")
        QtCore.QObject.connect(self.annotateAct,
                               QtCore.SIGNAL("triggered()"),
                               self.annotate)
        self.viewDocumentationAct = QtGui.QAction("View Documentation", self.scene())
        self.viewDocumentationAct.setStatusTip("View module documentation")
        QtCore.QObject.connect(self.viewDocumentationAct,
                               QtCore.SIGNAL("triggered()"),
                               self.viewDocumentation)
        self.changeModuleLabelAct = QtGui.QAction("Set Module Label...", self.scene())
        self.changeModuleLabelAct.setStatusTip("Set or remove module label")
        QtCore.QObject.connect(self.changeModuleLabelAct,
                               QtCore.SIGNAL("triggered()"),
                               self.changeModuleLabel)
        self.setBreakpointAct = QtGui.QAction("Set Breakpoint", self.scene())
        self.setBreakpointAct.setStatusTip("Set Breakpoint")
        QtCore.QObject.connect(self.setBreakpointAct,
			       QtCore.SIGNAL("triggered()"),
			       self.set_breakpoint)
        self.setWatchedAct = QtGui.QAction("Watch Module", self.scene())
        self.setWatchedAct.setStatusTip("Watch Module")
        QtCore.QObject.connect(self.setWatchedAct,
			       QtCore.SIGNAL("triggered()"),
			       self.set_watched)
        self.setErrorAct = QtGui.QAction("Show Error", self.scene())
        self.setErrorAct.setStatusTip("Show Error")
        QtCore.QObject.connect(self.setErrorAct,
                               QtCore.SIGNAL("triggered()"),
                               self.set_error)
        self.upgradeAbstractionAct = QtGui.QAction("Upgrade Module", self.scene())
        self.upgradeAbstractionAct.setStatusTip("Upgrade the subworkflow module")
        QtCore.QObject.connect(self.upgradeAbstractionAct,
                   QtCore.SIGNAL("triggered()"),
                   self.upgradeAbstraction)

    def set_breakpoint(self):
        """ set_breakpoint() -> None
        Sets this module as a breakpoint for execution
        """
        if self.moduleId >= 0:
            self.scene().toggle_breakpoint(self.moduleId)
            self.setBreakpoint(not self.is_breakpoint)
        debug = get_default_interpreter().debugger
        if debug:
            debug.update()

    def set_watched(self):
        if self.moduleId >= 0:
            self.scene().toggle_watched(self.moduleId)
        debug = get_default_interpreter().debugger
        if debug:
            debug.update()

    def set_error(self):
        if self.moduleId >= 0:
            self.scene().print_error(self.moduleId)

    def configure(self):
        """ configure() -> None
        Open the modal configuration window
        """
        if self.moduleId>=0:
            self.scene().open_configure_window(self.moduleId)

    def annotate(self):
        """ anotate() -> None
        Open the annotations window
        """
        if self.moduleId>=0:
            self.scene().open_annotations_window(self.moduleId)

    def viewDocumentation(self):
        """ viewDocumentation() -> None
        Show the documentation for the module
        """
        assert self.moduleId >= 0
        self.scene().open_documentation_window(self.moduleId)

    def changeModuleLabel(self):
        """ changeModuleLabel() -> None
        Show the module label configuration widget
        """
        if self.moduleId>=0:
            self.scene().open_module_label_window(self.moduleId)

    def upgradeAbstraction(self):
        """ upgradeAbstraction() -> None
        Upgrade the abstraction to the latest version
        """
        if self.moduleId>=0:
            (connections_preserved, missing_ports) = self.controller.upgrade_abstraction_module(self.moduleId, test_only=True)
            upgrade_fail_prompt = getattr(get_vistrails_configuration(), 'upgradeModuleFailPrompt', True)
            do_upgrade = True
            if not connections_preserved and upgrade_fail_prompt:
                ports_msg = '\n'.join(["  - %s port '%s'" % (p[0].capitalize(), p[1]) for p in missing_ports])
                r = QtGui.QMessageBox.question(getBuilderWindow(), 'Modify Pipeline',
                                       'Upgrading this module will change the pipeline because the following ports no longer exist in the upgraded module:\n\n'
                                       + ports_msg +
                                       '\n\nIf you proceed, function calls or connections to these ports will no longer exist and the pipeline may not execute properly.\n\n'
                                       'Are you sure you want to proceed?',
                                       QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                       QtGui.QMessageBox.No)
                do_upgrade = (r==QtGui.QMessageBox.Yes)
            if do_upgrade:
                self.controller.upgrade_abstraction_module(self.moduleId)
                self.scene().setupScene(self.controller.current_pipeline)
                self.controller.invalidate_version_tree()
        
        
                                               
##############################################################################
# QGraphicsConnectionItem

# set this to True to have old sine-wave connections
__old_connection = False
if __old_connection:
    class QGraphicsConnectionItem(QGraphicsItemInterface,
                                  QtGui.QGraphicsPolygonItem):
        """
        QGraphicsConnectionItem is a connection shape connecting two port items

        """
        def __init__(self, srcPoint, dstPoint, srcModule, dstModule,
                     connection, parent=None):
            """ QGraphicsConnectionItem(srcPoint, dstPoint: QPointF
            srcModule, dstModule: QGraphicsModuleItem
            connection
            parent: QGraphicsItem)
                                        -> QGraphicsConnectionItem
            Create the shape, initialize its pen and brush accordingly

            """
            QtGui.QGraphicsPolygonItem.__init__(self, parent)
            self.startPos = QtCore.QPointF()
            self.endPos = QtCore.QPointF()
            self.visualPolygon = QtGui.QPolygonF()
            self.setupConnection(srcPoint, dstPoint)
            self.setFlags(QtGui.QGraphicsItem.ItemIsSelectable)
            # Bump it slightly higher than the highest module
            self.setZValue(max(srcModule.id,
                               dstModule.id) + 0.1)
            self.connectionPen = CurrentTheme.CONNECTION_PEN
            
            self.connectingModules = (srcModule, dstModule)
            self.id = connection.id
            self.ghosted = False
            self.connection = connection
            # Keep a flag for changing selection state during module selection
            self.useSelectionRules = True

        def setupConnection(self, startPos, endPos):
            """ setupConnection(startPos: QPointF, endPos: QPointF) -> None
            Setup curve ends and store info

            """
            self.startPos = startPos
            self.endPos = endPos

            # Generate the polygon passing through two points
            steps = CurrentTheme.CONNECTION_CONTROL_POINTS
            polygon = QtGui.QPolygonF()
            self.visualPolygon = QtGui.QPolygonF()
            p1 = self.startPos
            p2 = self.endPos
            r = p2-p1
            horizontal = False        
            if p2.y() > p1.y() and p2.x() > p1.x():
                horizontal = True
            p1x = p1.x()
            p1y = p1.y()
            rx = r.x()
            ry = r.y()
            points = []
            for i in xrange(steps):
                t = float(i)/float(steps-1)
                s = (0.5+math.sin(math.pi*(t-0.5))*0.5)
                if horizontal:
                    x = p1x+rx*t
                    y = p1y+ry*s
                    polygon.append(QtCore.QPointF(x,y-2))
                    self.visualPolygon.append(QtCore.QPointF(x,y))
                    points.append(QtCore.QPointF(x, y+2))
                else:
                    x = p1x+rx*s
                    y = p1y+ry*t
                    polygon.append(QtCore.QPointF(x-2, y))
                    self.visualPolygon.append(QtCore.QPointF(x, y))
                    points.append(QtCore.QPointF(x+2, y))

            for p in reversed(points):
                polygon.append(p)
            polygon.append(polygon.at(0))
            self.setPolygon(polygon)

        def setGhosted(self, ghosted):
            """ setGhosted(ghosted: True) -> None
            Set this link to be ghosted or not

            """
            self.ghosted = ghosted
            if ghosted:
                self.connectionPen = CurrentTheme.GHOSTED_CONNECTION_PEN
            else:
                self.connectionPen = CurrentTheme.CONNECTION_PEN

        def set_custom_brush(self, brush):
            self.connectionPen = QtGui.QPen(CurrentTheme.CONNECTION_PEN)
            self.connectionPen.setBrush(brush)

        def paint(self, painter, option, widget=None):
            """ paint(painter: QPainter, option: QStyleOptionGraphicsItem,
                      widget: QWidget) -> None
            Peform actual painting of the connection

            """
            if self.isSelected():
                painter.setPen(CurrentTheme.CONNECTION_SELECTED_PEN)
            else:
                painter.setPen(self.connectionPen)
            painter.drawPolyline(self.visualPolygon)

        def itemChange(self, change, value):
            """ itemChange(change: GraphicsItemChange, value: QVariant) -> QVariant
            Do not allow connection to be selected unless both modules 
            are selected

            """
            # Selection rules to be used only when a module isn't forcing 
            # the update
            if (change==QtGui.QGraphicsItem.ItemSelectedChange and 
                self.useSelectionRules):
                # Check for a selected module
                selectedItems = self.scene().selectedItems()
                selectedModules = False
                for item in selectedItems:
                    if type(item)==QGraphicsModuleItem:
                        selectedModules = True
                        break
                if selectedModules:
                    # Don't allow a connection between selected
                    # modules to be deselected
                    if (self.connectingModules[0].isSelected() and
                        self.connectingModules[1].isSelected()):
                        if not value.toBool():
                            return QtCore.QVariant(True)
                    # Don't allow a connection to be selected if
                    # it is not between selected modules
                    else:
                        if value.toBool():
                            return QtCore.QVariant(False)
            self.useSelectionRules = True
            return QtGui.QGraphicsPolygonItem.itemChange(self, change, value)
else:
    class QGraphicsConnectionItem(QGraphicsItemInterface,
                                  QtGui.QGraphicsPathItem):
        """
        QGraphicsConnectionItem is a connection shape connecting two port items

        """

        def create_path(self, startPos, endPos):
            self.startPos = startPos
            self.endPos = endPos

            dx = abs(self.endPos.x() - self.startPos.x())
            dy = (self.startPos.y() - self.endPos.y())

            # This is reasonably ugly logic to get reasonably nice
            # curves. Here goes: we use a cubic bezier p0,p1,p2,p3, where:

            # p0 is the source port center
            # p3 is the destination port center
            # p1 is a control point displaced vertically from p0
            # p2 is a control point displaced vertically from p3

            # We want most curves to be "straight": they shouldn't bend
            # much.  However, we want "inverted" connections (connections
            # that go against the natural up-down flow) to bend a little
            # as they go out of the ports. So the logic is:

            # As dy/dx -> oo, we want the control point displacement to go
            # to max(dy/2, m) (m is described below)

            # As dy/dx -> 0, we want the control point displacement to go
            # to m 

            # As dy/dx -> -oo, we want the control point displacement to go
            # to max(-dy/2, m)

            # On points away from infinity, we want some smooth transition.
            # I'm using f(x) = 2/pi arctan (x) as the mapping, since:

            # f(-oo) = -1
            # f(0) = 0
            # f(oo) = 1

            # m is the monotonicity breakdown point: this is the minimum
            # displacement when dy/dx is low
            m = float(CurrentTheme.MODULE_LABEL_MARGIN[0]) * 3.0

            # positive_d and negative_d are the displacements when dy/dx is
            # large positive and large negative
            positive_d = max(m/3.0, dy / 2.0)
            negative_d = max(m/3.0, -dy / 4.0)

            if dx == 0.0:
                v = 0.0
            else:
                w = math.atan(dy/dx) * (2 / math.pi)
                if w < 0:
                    w = -w
                    v = w * negative_d + (1.0 - w) * m
                else:
                    v = w * positive_d + (1.0 - w) * m

            displacement = QtCore.QPointF(0.0, v)
            self._control_1 = startPos + displacement
            # !!! MAC OS X BUG !!!
            # the difference between startPos.y and control_1.y cannot be
            # equal to the difference between control_2.y and endPos.y
            self._control_2 = self.endPos - displacement + \
                QtCore.QPointF(0.0, 1e-10)
            # self._control_2 = endPos - displacement

            path = QtGui.QPainterPath(self.startPos)
            path.cubicTo(self._control_1, self._control_2, self.endPos)
            return path
            
        def __init__(self,
                     srcPoint, dstPoint,
                     srcModule, dstModule,
                     connection,
                     parent=None):
            """ QGraphicsConnectionItem(
            srcPoint, dstPoint: QPointF
            srcModule, dstModule: QGraphicsModuleItem
            connection
            parent: QGraphicsItem)
                                        -> QGraphicsConnectionItem
            Create the shape, initialize its pen and brush accordingly

            """
            path = self.create_path(srcPoint, dstPoint)
            QtGui.QGraphicsPolygonItem.__init__(self, path, parent)
            self.setFlags(QtGui.QGraphicsItem.ItemIsSelectable)
            # Bump it slightly higher than the highest module
            self.setZValue(max(srcModule.id,
                               dstModule.id) + 0.1)
            self.connectionPen = CurrentTheme.CONNECTION_PEN
            self.connectingModules = (srcModule, dstModule)
            self.ghosted = False
            self.connection = connection
            self.id = connection.id
            # Keep a flag for changing selection state during module selection
            self.useSelectionRules = True

        def setGhosted(self, ghosted):
            """ setGhosted(ghosted: True) -> None
            Set this link to be ghosted or not

            """
            self.ghosted = ghosted
            if ghosted:
                self.connectionPen = CurrentTheme.GHOSTED_CONNECTION_PEN
            else:
                self.connectionPen = CurrentTheme.CONNECTION_PEN

        def set_custom_brush(self, brush):
            self.connectionPen = QtGui.QPen(CurrentTheme.CONNECTION_PEN)
            self.connectionPen.setBrush(brush)

        def paint(self, painter, option, widget=None):
            """ paint(painter: QPainter, option: QStyleOptionGraphicsItem,
                      widget: QWidget) -> None
            Peform actual painting of the connection

            """
            if self.isSelected():
                painter.setPen(CurrentTheme.CONNECTION_SELECTED_PEN)
            else:
                painter.setPen(self.connectionPen)
            painter.drawPath(self.path())

        def setupConnection(self, startPos, endPos):
            path = self.create_path(startPos, endPos)
            self.setPath(path)
            
        def itemChange(self, change, value):
            """ itemChange(change: GraphicsItemChange, value: QVariant) -> QVariant
            If modules are selected, only allow connections between 
            selected modules 

            """
            # Selection rules to be used only when a module isn't forcing 
            # the update
            if (change==QtGui.QGraphicsItem.ItemSelectedChange and 
                self.useSelectionRules):
                # Check for a selected module
                selectedItems = self.scene().selectedItems()
                selectedModules = False
                for item in selectedItems:
                    if type(item)==QGraphicsModuleItem:
                        selectedModules = True
                        break
                if selectedModules:
                    # Don't allow a connection between selected
                    # modules to be deselected
                    if (self.connectingModules[0].isSelected() and
                        self.connectingModules[1].isSelected()):
                        if not value.toBool():
                            return QtCore.QVariant(True)
                    # Don't allow a connection to be selected if
                    # it is not between selected modules
                    else:
                        if value.toBool():
                            return QtCore.QVariant(False)
            self.useSelectionRules = True
            return QtGui.QGraphicsPathItem.itemChange(self, change, value)    

##############################################################################
# QGraphicsModuleItem

class QGraphicsModuleItem(QGraphicsItemInterface, QtGui.QGraphicsItem):
    """
    QGraphicsModuleItem knows how to draw a Vistrail Module into the
    pipeline view. It is usually a rectangular shape with a bold text
    in the center. It also has its input/output port shapes as its
    children. Another remark is that connections are also children of
    module shapes. Each connection belongs to its source module
    ('output port' end of the connection)
    
    """
    def __init__(self, parent=None, scene=None):
        """ QGraphicsModuleItem(parent: QGraphicsItem, scene: QGraphicsScene)
                                -> QGraphicsModuleItem
        Create the shape, initialize its pen and brush accordingly
        
        """
        QtGui.QGraphicsItem.__init__(self, parent, scene)
        self.paddedRect = QtCore.QRectF()
        if QtCore.QT_VERSION >= 0x40600:
            #Qt 4.6 specific flags
            self.setFlags(QtGui.QGraphicsItem.ItemIsSelectable |
                          QtGui.QGraphicsItem.ItemIsMovable |
                          QtGui.QGraphicsItem.ItemSendsGeometryChanges)
        else:
            self.setFlags(QtGui.QGraphicsItem.ItemIsSelectable |
                          QtGui.QGraphicsItem.ItemIsMovable)
        self.setZValue(0)
        self.labelFont = CurrentTheme.MODULE_FONT
        self.labelFontMetric = CurrentTheme.MODULE_FONT_METRIC
        self.descFont = CurrentTheme.MODULE_DESC_FONT
        self.descFontMetric = CurrentTheme.MODULE_DESC_FONT_METRIC
        self.modulePen = CurrentTheme.MODULE_PEN
        self.moduleBrush = CurrentTheme.MODULE_BRUSH
        self.labelPen = CurrentTheme.MODULE_LABEL_PEN
        self.customBrush = None
        self.statusBrush = None
        self.labelRect = QtCore.QRectF()
        self.descRect = QtCore.QRectF()
        self.abstRect = QtCore.QRectF()
        self.id = -1
        self.label = ''
        self.description = ''
        self.inputPorts = {}
        self.outputPorts = {}
        self.controller = None
        self.module = None
        self.ghosted = False
        self.invalid = False
        self._module_shape = None
        self._original_module_shape = None
        self._old_connection_ids = None
        self.errorTrace = None
        self.is_breakpoint = False
        self._needs_state_updated = True
        self.progress = 0.0
        self.progressBrush = CurrentTheme.SUCCESS_MODULE_BRUSH
        self.connectionItems = {}

    def moduleHasChanged(self, core_module):
        def module_text_has_changed(m1, m2):
            m1_has = '__desc__' in m1.db_annotations_key_index
            if m1_has != ('__desc__' in m2.db_annotations_key_index):
                return True
            if (m1_has and
                # m2_has, since m1_has and previous condition
                m1.db_annotations_key_index['__desc__'].value.strip()!=
                m2.db_annotations_key_index['__desc__'].value.strip()):
                return True            
            return False

        if self.scenePos().x() != core_module.center.x or \
                -self.scenePos().y() != core_module.center.y:
            return True
        elif module_text_has_changed(self.module, core_module):
            return True
        else:
            # Check for changed ports
            # _db_name because this shows up in the profile.
            cip = sorted([x.key_no_id() for x in self.inputPorts])
            cop = sorted([x.key_no_id() for x in self.outputPorts])
            d = PortEndPoint.Destination
            s = PortEndPoint.Source
            pv = core_module.portVisible
            new_ip = []
            new_op = []
            try:
                new_ip = sorted([x.key_no_id() 
                                 for x in core_module.destinationPorts()
                                 if (not x.optional or (d, x._db_name) in pv)])
                new_op = sorted([x.key_no_id() 
                                 for x in core_module.sourcePorts()
                                 if (not x.optional or (s, x._db_name) in pv)])
            except ModuleRegistryException, e:
                debug.critical("MODULE REGISTRY EXCEPTION: %s" % e)
            if cip <> new_ip or cop <> new_op:
                return True
        return False
        

    def setProgress(self, progress):
        self.progress = progress
        
    def computeBoundingRect(self):
        """ computeBoundingRect() -> None
        Adjust the module size according to the text size
        
        """
        labelRect = self.labelFontMetric.boundingRect(self.label)
        if self.description:
            self.description = '(' + self.description + ')'
            descRect = self.descFontMetric.boundingRect(self.description)
            # adjust labelRect in case descRect is wider
            labelRect = labelRect.united(descRect)
            descRect.adjust(0, 0, 0, CurrentTheme.MODULE_PORT_MARGIN[3])
        else:
            descRect = QtCore.QRectF(0, 0, 0, 0)

        labelRect.translate(-labelRect.center().x(), -labelRect.center().y())
        self.paddedRect = QtCore.QRectF(
            labelRect.adjusted(-CurrentTheme.MODULE_LABEL_MARGIN[0],
                                -CurrentTheme.MODULE_LABEL_MARGIN[1]
                                -descRect.height()/2,
                                CurrentTheme.MODULE_LABEL_MARGIN[2],
                                CurrentTheme.MODULE_LABEL_MARGIN[3]
                                +descRect.height()/2))
        
        self.labelRect = QtCore.QRectF(
            self.paddedRect.left(),
            -(labelRect.height()+descRect.height())/2,
            self.paddedRect.width(),
            labelRect.height())
        self.descRect = QtCore.QRectF(
            self.paddedRect.left(),
            self.labelRect.bottom(),
            self.paddedRect.width(),
            descRect.height())
        self.abstRect = QtCore.QRectF(
            self.paddedRect.left(),
            -self.labelRect.top()-CurrentTheme.MODULE_PORT_MARGIN[3],
            labelRect.left()-self.paddedRect.left(),
            self.paddedRect.bottom()+self.labelRect.top())

    def boundingRect(self):
        """ boundingRect() -> QRectF
        Returns the bounding box of the module
        
        """
        try:
            r = self.paddedRect.adjusted(-2, -2, 2, 2)
        except:
            r = QtCore.QRectF()
        return r

    def setPainterState(self, is_selected=None):
        if is_selected is None:
            is_selected = self.isSelected()
        if is_selected:
            self.modulePen = CurrentTheme.MODULE_SELECTED_PEN
            self.labelPen = CurrentTheme.MODULE_LABEL_SELECTED_PEN
        elif self.is_breakpoint:
            self.modulePen = CurrentTheme.BREAKPOINT_MODULE_PEN
            self.labelPen = CurrentTheme.BREAKPOINT_MODULE_LABEL_PEN
        elif self.ghosted:
            self.modulePen = CurrentTheme.GHOSTED_MODULE_PEN
            self.labelPen = CurrentTheme.GHOSTED_MODULE_LABEL_PEN
        elif self.invalid:
            self.modulePen = CurrentTheme.INVALID_MODULE_PEN
            self.labelPen = CurrentTheme.INVALID_MODULE_LABEL_PEN
        else:
            self.labelPen = CurrentTheme.MODULE_LABEL_PEN
            if self.module is not None and self.module.is_abstraction():
                self.modulePen = CurrentTheme.ABSTRACTION_PEN
            elif self.module is not None and self.module.is_group():
                self.modulePen = CurrentTheme.GROUP_PEN
            else:
                self.modulePen = CurrentTheme.MODULE_PEN

        if self.customBrush:
            self.moduleBrush = self.customBrush
        elif self.is_breakpoint:
            self.moduleBrush = CurrentTheme.BREAKPOINT_MODULE_BRUSH
        elif self.ghosted:
            self.moduleBrush = CurrentTheme.GHOSTED_MODULE_BRUSH
        elif self.invalid:
            self.moduleBrush = CurrentTheme.INVALID_MODULE_BRUSH
        elif self.statusBrush:
            self.moduleBrush = self.statusBrush
        else:
            self.moduleBrush = CurrentTheme.MODULE_BRUSH
            
    def setGhosted(self, ghosted):
        """ setGhosted(ghosted: True) -> None
        Set this link to be ghosted or not
        
        """
        if self.ghosted != ghosted:
            self.ghosted = ghosted
            for port in self.inputPorts.itervalues():
                port.setGhosted(ghosted)
            for port in self.outputPorts.itervalues():
                port.setGhosted(ghosted)
            self._needs_state_udpated = True

#             if ghosted:
#                 self.modulePen = CurrentTheme.GHOSTED_MODULE_PEN
#                 self.moduleBrush = CurrentTheme.GHOSTED_MODULE_BRUSH
#                 self.labelPen = CurrentTheme.GHOSTED_MODULE_LABEL_PEN
#             else:
#                 self.modulePen = CurrentTheme.MODULE_PEN
#                 self.moduleBrush = CurrentTheme.MODULE_BRUSH
#                 self.labelPen = CurrentTheme.MODULE_LABEL_PEN

    def setInvalid(self, invalid):
        if self.invalid != invalid:
            self.invalid = invalid
            for port in self.inputPorts.itervalues():
                port.setInvalid(invalid)
            for port in self.outputPorts.itervalues():
                port.setInvalid(invalid)
            self._needs_state_updated = True

    def setBreakpoint(self, breakpoint):
        if self.is_breakpoint != breakpoint:
            self.is_breakpoint = breakpoint
            if breakpoint:
                self._original_module_shape = self._module_shape
                self.set_module_shape(self.create_shape_from_fringe(
                        CurrentTheme.BREAKPOINT_FRINGE))
            else:
                self._module_shape = self._original_module_shape
            self._needs_state_updated = True

#             if breakpoint:
#                 self.modulePen = CurrentTheme.BREAKPOINT_MODULE_PEN
#                 self.moduleBrush = CurrentTheme.BREAKPOINT_MODULE_BRUSH
#                 self.labelPen = CurrentTheme.BREAKPOINT_MODULE_LABEL_PEN
            
    def set_module_shape(self, module_shape=None):
        self._module_shape = module_shape
        if self._module_shape is not None:
            self.paddedRect = self._module_shape.boundingRect()

    def set_custom_brush(self, brush):
        self.customBrush = brush
        self._needs_state_updated = True

    def paint(self, painter, option, widget=None):
        """ paint(painter: QPainter, option: QStyleOptionGraphicsItem,
                  widget: QWidget) -> None
        Peform actual painting of the module
        
        """
        if self.progress>0.0:
            width = (self.progress-1.0)*self.paddedRect.width()
            progressRect = self.paddedRect.adjusted(0, 0, width, 0)
            
        if self._needs_state_updated:
            self.setPainterState()
            self._needs_state_updated = False
            
        # draw module shape
        painter.setBrush(self.moduleBrush)
        painter.setPen(self.modulePen)
        if self._module_shape:
            painter.drawPolygon(self._module_shape)
            if self.progress>0.0:
                painter.setClipRect(progressRect)
                painter.setBrush(self.progressBrush)
                painter.drawPolygon(self._module_shape)
                painter.setClipping(False)
            painter.drawPolyline(self._module_shape)
        else:
            painter.fillRect(self.paddedRect, painter.brush())
            if self.progress>0.0:
                painter.fillRect(progressRect, self.progressBrush)
            painter.setBrush(QtCore.Qt.NoBrush)
            painter.drawRect(self.paddedRect)
    
        # draw module labels
        painter.setPen(self.labelPen)
        painter.setFont(self.labelFont)
        painter.drawText(self.labelRect, QtCore.Qt.AlignCenter, self.label)
        if self.module.is_abstraction() and not self.module.is_latest_version():
            painter.drawText(self.abstRect, QtCore.Qt.AlignCenter, '!')
        if self.descRect:
            painter.setFont(self.descFont)
            painter.drawText(self.descRect, QtCore.Qt.AlignCenter,
                             self.description)

    def adjustWidthToMin(self, minWidth):
        """ adjustWidthToContain(minWidth: int) -> None
        Resize the module width to at least be minWidth
        
        """
        if minWidth>self.paddedRect.width():
            diff = minWidth - self.paddedRect.width() + 1
            self.paddedRect.adjust(-diff/2, 0, diff/2, 0)

    def setupModule(self, module):
        """ setupModule(module: Module) -> None
        Set up the item to reflect the info in 'module'
        
        """
        # Update module info and visual
        self.id = module.id
        self.setZValue(float(self.id))
        self.module = module
        self.center = copy.copy(module.center)
        if '__desc__' in module.db_annotations_key_index:
            self.label = module.get_annotation_by_key('__desc__').value.strip()
            self.description = module.label
        else:
            self.label = module.label
            self.description = ''
        self.setToolTip(self.description)
        self.computeBoundingRect()
        self.resetMatrix()
        self.translate(module.center.x, -module.center.y)

        # Check to see which ports will be shown on the screen
        # setupModule is in a hotpath, performance-wise, which is the
        # reason for the strange ._db_name lookup - we're
        # avoiding property calls
        inputPorts = []
        self.inputPorts = {}
        visibleOptionalInputPorts = []
        self.optionalInputPorts = []

        outputPorts = []
        self.outputPorts = {}
        visibleOptionalOutputPorts = []
        self.optionalOutputPorts = []

        error = None
        if module.is_valid:
            try:
                d = PortEndPoint.Destination
                for p in module.destinationPorts():
                    if not p.optional:
                        inputPorts.append(p)
                    # elif (d, p.name) in module.portVisible:
                    elif p.name in module.visible_input_ports:
                        visibleOptionalInputPorts.append(p)
                    else:
                        self.optionalInputPorts.append(p)
                inputPorts += visibleOptionalInputPorts

                s = PortEndPoint.Source
                for p in module.sourcePorts():
                    if not p.optional:
                        outputPorts.append(p)
                    # elif (s, p.name) in module.portVisible:
                    elif p.name in module.visible_output_ports:
                        visibleOptionalOutputPorts.append(p)
                    else:
                        self.optionalOutputPorts.append(p)
                outputPorts += visibleOptionalOutputPorts
            except ModuleRegistryException, e:
                error = e

        # Local dictionary lookups are faster than global ones..
        t = CurrentTheme
        (mpm0, mpm1, mpm2, mpm3) = t.MODULE_PORT_MARGIN

        # Adjust the width to fit all ports
        maxPortCount = max(len(inputPorts), len(outputPorts))
        minWidth = (mpm0 +
                    t.PORT_WIDTH*maxPortCount +
                    t.MODULE_PORT_SPACE*(maxPortCount-1) +
                    mpm2 +
                    t.MODULE_PORT_PADDED_SPACE)
        self.adjustWidthToMin(minWidth)

        self.nextInputPortPos = [self.paddedRect.x() + mpm0,
                                 self.paddedRect.y() + mpm1]
        self.nextOutputPortPos = [self.paddedRect.right() - \
                                      t.PORT_WIDTH - mpm2,
                                  self.paddedRect.bottom() - \
                                      t.PORT_HEIGHT - mpm3]

        # Update input ports
        [x, y] = self.nextInputPortPos
        for port in inputPorts:
            self.inputPorts[port] = self.createPortItem(port, x, y)
            x += t.PORT_WIDTH + t.MODULE_PORT_SPACE
        self.nextInputPortPos = [x,y]

        # Update output ports
        [x, y] = self.nextOutputPortPos
        for port in outputPorts:            
            self.outputPorts[port] = self.createPortItem(port, x, y)
            x -= t.PORT_WIDTH + t.MODULE_PORT_SPACE
        self.nextOutputPortPos = [x, y]

        # Add a configure button
        y = self.paddedRect.y() + mpm1
        x = (self.paddedRect.right() - t.CONFIGURE_WIDTH
             - mpm2)
        self.createConfigureItem(x, y)

        if module.is_valid:
            try:
                # update module color and shape
                descriptor = module.module_descriptor
    #             c = registry.get_module_color(module.package, module.name, 
    #                                       module.namespace)
                c = descriptor.module_color()
                if c:
                    ic = [int(cl*255) for cl in c]
                    b = QtGui.QBrush(QtGui.QColor(ic[0], ic[1], ic[2]))
                    self.set_custom_brush(b)
    #             fringe = registry.get_module_fringe(module.package,
    #                                                 module.name,
    #                                                 module.namespace)
                fringe = descriptor.module_fringe()
                if fringe:
                    self.set_module_shape(self.create_shape_from_fringe(fringe))
            except ModuleRegistryException, e:
                error = e
        else:
            self.setInvalid(True)
            
    def create_shape_from_fringe(self, fringe):
        left_fringe, right_fringe = fringe
        if left_fringe[0] != (0.0, 0.0):
            left_fringe = [(0.0, 0.0)] + left_fringe
        if left_fringe[-1] != (0.0, 1.0):
            left_fringe = left_fringe + [(0.0, 1.0)]

        if right_fringe[0] != (0.0, 0.0):
            right_fringe = [(0.0, 0.0)] + right_fringe
        if right_fringe[-1] != (0.0, 1.0):
            right_fringe = right_fringe + [(0.0, 1.0)]

        P = QtCore.QPointF
        module_shape = QtGui.QPolygonF()
        height = self.paddedRect.height()

        # right side of shape
        for (px, py) in right_fringe:
            p = P(px, -py)
            p *= height
            p += self.paddedRect.bottomRight()
            module_shape.append(p)

        # left side of shape
        for (px, py) in reversed(left_fringe):
            p = P(px, -py)
            p *= height
            p += self.paddedRect.bottomLeft()
            module_shape.append(p)
        # close polygon
        module_shape.append(module_shape[0])
        return module_shape

    def createPortItem(self, port, x, y):
        """ createPortItem(port: Port, x: int, y: int) -> QGraphicsPortItem
        Create a item from the port spec
        
        """
        portShape = QGraphicsPortItem(x, y, self.ghosted, self, port.optional)
        portShape.controller = self.controller
        portShape.port = port
        if not port.is_valid:
            portShape.setInvalid(True)
        try:
            portShape.setToolTip(port.toolTip())
        except:
            portShape.setToolTip("ERROR with tool tip")
        return portShape

    def createConfigureItem(self, x, y):
        """ createConfigureItem(x: int, y: int) -> QGraphicsConfigureItem
        Create a item from the configure spec
        
        """
        if self.module.is_valid:
            configureShape = QGraphicsConfigureItem(self, self.scene())
            configureShape.controller = self.controller
            configureShape.moduleId = self.id
            configureShape.setGhosted(self.ghosted)
            configureShape.setBreakpoint(self.module.is_breakpoint)
            configureShape.translate(x, y)
            return configureShape
        return None

    def getPortPosition(self, port, port_dict, optional_ports, next_pos, 
                        next_op, default_sig):
        """ getPortPosition(port: Port,
                            port_dict: {PortSpec: QGraphicsPortItem},
                            optional_ports: [PortSpec],
                            next_pos: [float, float],
                            next_op: operator (operator.add, operator.sub),
                            default_sig: str
                            )
                            -> QPointF
        Return the scene position of a port matched 'port' in port_dict
        
        """
        registry = get_module_registry()

        # if we haven't validated pipeline, don't try to use the registry
        if self.module.is_valid:
            # check enabled ports
            for (p, item) in port_dict.iteritems():
                if registry.port_and_port_spec_match(port, p):
                    return item.sceneBoundingRect().center()
                
            # check optional ports
            for p in optional_ports:
                if registry.port_and_port_spec_match(port, p):
                    item = self.createPortItem(p, *next_pos)
                    port_dict[p] = item
                    next_pos[0] = next_op(next_pos[0], 
                                          (CurrentTheme.PORT_WIDTH +
                                           CurrentTheme.MODULE_PORT_SPACE))
                    return item.sceneBoundingRect().center()
        
        # FIXME Raise Error!
        # else not available for some reason, just draw port and raise error?
        # can also decide to use Variant/Module types
        # or use types from the signature
        # port_descs = port.descriptors()
                
        # first, check if we've already added the port
        for (p, item) in port_dict.iteritems():
            if (PortSpec.port_type_map.inverse[port.type] == p.type and
                port.name == p.name and 
                port.sigstring == p.sigstring):
                return item.sceneBoundingRect().center()
        
        debug.log("PORT SIG:" + port.signature)
        if not port.signature or port.signature == '()':
            # or len(port_descs) == 0:
            sigstring = default_sig
        else:
            sigstring = port.signature
        port_type = PortSpec.port_type_map.inverse[port.type]
        names = []
        for sig in sigstring[1:-1].split(','):
            k = sig.split(':', 2)
            if len(k) < 2:
                names.append(k[0])
            else:
                names.append(k[1])
        short_sigstring = '(' + ','.join(names) + ')'
        tooltip = "%s port %s\n%s" % (port_type.capitalize(),
                                      port.name,
                                      short_sigstring)
        new_spec = PortSpec(id=-1,
                            name=port.name,
                            type=port_type,
                            sigstring=sigstring,
                            tooltip=tooltip,
                            optional=True)

        item = self.createPortItem(new_spec, *next_pos)
        item.setInvalid(True)
        port_dict[new_spec] = item
        next_pos[0] = next_op(next_pos[0], 
                              (CurrentTheme.PORT_WIDTH +
                               CurrentTheme.MODULE_PORT_SPACE))
        return item.sceneBoundingRect().center()

    def getInputPortPosition(self, port):
        """ getInputPortPosition(port: Port) -> QPointF
        Just an overload function of getPortPosition to get from input ports
        
        """        
        return self.getPortPosition(port, self.inputPorts, 
                                    self.optionalInputPorts,
                                    self.nextInputPortPos,
                                    operator.add,
                                    '(edu.utah.sci.vistrails.basic:Variant)')
        
    def getOutputPortPosition(self, port):
        """ getOutputPortPosition(port: Port} -> QRectF
        Just an overload function of getPortPosition to get from output ports
        
        """
        return self.getPortPosition(port, self.outputPorts,
                                    self.optionalOutputPorts,
                                    self.nextOutputPortPos,
                                    operator.sub,
                                    '(edu.utah.sci.vistrails.basic:Module)')

    def addConnectionItem(self, item):
        self.connectionItems[item.connection.id] = item

    def removeConnectionItem(self, item):
        del self.connectionItems[item.connection.id]

    # returns a dictionary of (id, connection) key-value pairs!
    def dependingConnectionItems(self):
        return self.connectionItems

    # this is a generator that yields (connection, is_source [bool]) pairs
    def dependingConnectionItemsWithDir(self):
        for item in self.connectionItems.itervalues():
            if item.connectingModules[0].id == self.id:
                yield (item, False)
            else:
                yield (item, True)

    def itemChange(self, change, value):
        """ itemChange(change: GraphicsItemChange, value: QVariant) -> QVariant
        Capture move event to also move the connections.  Also unselect any
        connections between unselected modules
        
        """
        # Move connections with modules
        if change==QtGui.QGraphicsItem.ItemPositionChange:
            oldPos = self.pos()
            newPos = value.toPointF()
            dis = newPos - oldPos
            for connectionItem, s in self.dependingConnectionItemsWithDir():
                # If both modules are selected, both of them will
                # trigger itemChange events.

                # If we just add 'dis' to both connection endpoints, we'll
                # end up moving each endpoint twice.

                # But we also don't want to call setupConnection twice on these
                # connections, so we ignore one of the endpoint dependencies and
                # perform the change on the other one

                (srcModule, dstModule) = connectionItem.connectingModules
                start_s = srcModule.isSelected()
                end_s = dstModule.isSelected()

                if start_s and end_s and s:
                    continue

                start = connectionItem.startPos
                end = connectionItem.endPos
                
                if start_s: start += dis
                if end_s: end += dis
                
                connectionItem.prepareGeometryChange()
                connectionItem.setupConnection(start, end)
        # Do not allow lone connections to be selected with modules.
        # Also autoselect connections between selected modules.  Thus the
        # selection is always the subgraph
        elif change==QtGui.QGraphicsItem.ItemSelectedHasChanged:
            # Unselect any connections between modules that are not selected
            for item in self.scene().selectedItems():
                if isinstance(item,QGraphicsConnectionItem):
                    (srcModule, dstModule) = item.connectingModules
                    if (not srcModule.isSelected() or 
                        not dstModule.isSelected()):
                        item.useSelectionRules = False
                        item.setSelected(False)
            # Handle connections from self
            for item in self.dependingConnectionItems().itervalues():
                # Select any connections between self and other selected modules
                (srcModule, dstModule) = item.connectingModules
                if value.toBool():
                    if (srcModule==self and dstModule.isSelected() or
                        dstModule==self and srcModule.isSelected()):
                        # Because we are setting a state variable in the
                        # connection, do not make the change unless it is
                        # actually going to be performed
                        if not item.isSelected():
                            item.useSelectionRules = False
                            item.setSelected(True)
                # Unselect any connections between self and other modules
                else:
                    if item.isSelected():
                        item.useSelectionRules = False
                        item.setSelected(False)
            # Capture only selected modules + or - self for selection signal
            selectedItems = [m for m in self.scene().selectedItems()
                             if isinstance(m, QGraphicsModuleItem)]
            #print "selectedItems", selectedItems
            selectedId = -1
            if len(selectedItems)==1:
                selectedId = selectedItems[0].id
            self.scene().emit(QtCore.SIGNAL('moduleSelected'),
                              selectedId, selectedItems)
            self._needs_state_updated = True
        return QtGui.QGraphicsItem.itemChange(self, change, value)

    def getDestPort(self, pos, srcPort):
        """ getDestPort(self, pos: QPointF, srcPort: Port) -> QGraphicsPortItem
        Look for the destination port match 'port' and closest to pos
        
        """
        result = None
        minDis = None
        registry = get_module_registry()
        for (dstPort, dstItem) in self.inputPorts.items():
            if (registry.ports_can_connect(srcPort, dstPort) and
                dstItem.isVisible()):                
                vector = (pos - dstItem.sceneBoundingRect().center())
                dis = vector.x()*vector.x() + vector.y()*vector.y()
                if result==None or dis<minDis:
                    minDis = dis
                    result = dstItem
        return result

    def getSourcePort(self, pos, dstPort):
        """ getSourcePort(self, pos: QPointF, dstPort: Port)
                          -> QGraphicsPortItem
        Look for the source port match 'port' and closest to pos
        
        """
        result = None
        minDis = None
        registry = get_module_registry()
        for (srcPort, srcItem) in self.outputPorts.items():
            if (registry.ports_can_connect(srcPort, dstPort) and
                srcItem.isVisible()):
                vector = (pos - srcItem.sceneBoundingRect().center())
                dis = vector.x()*vector.x() + vector.y()*vector.y()
                if result==None or dis<minDis:
                    minDis = dis
                    result = srcItem
        return result


##############################################################################
# QPipelineScene

class QPipelineScene(QInteractiveGraphicsScene):
    """
    QPipelineScene inherits from QInteractiveGraphicsScene to keep track of the
    pipeline scenes, i.e. modules, connections, selection
    
    """

    def __init__(self, parent=None):
        """ QPipelineScene(parent: QWidget) -> QPipelineScene
        Initialize the graphics scene with no shapes
        
        """
        QInteractiveGraphicsScene.__init__(self, parent)
        self.setBackgroundBrush(CurrentTheme.PIPELINE_VIEW_BACKGROUND_BRUSH)
        self.setSceneRect(QtCore.QRectF(-5000, -5000, 10000, 10000))
        self.controller = None
        self.modules = {}
        self.connections = {}
        self.noUpdate = False
        self.installEventFilter(self)
        self.pipeline_tab = None
        self._old_module_ids = set()
        self._old_connection_ids = set()
        self._var_selected_port = None
        self.pipeline = None
        self.read_only_mode = False
        self.current_pipeline = None
        self.current_version = -1

#        menu = QtGui.QMenu()
#        self._create_abstraction = QtGui.QAction("Create abstraction", self)
#        menu.addAction(self._create_abstraction)
#        self._context_menu = menu
#        self.connect(self._create_abstraction,
#                     QtCore.SIGNAL("triggered()"),
#                     self.create_abstraction)

    def addModule(self, module, moduleBrush=None):
        """ addModule(module: Module, moduleBrush: QBrush) -> QGraphicsModuleItem
        Add a module to the scene
        
        """
        moduleItem = QGraphicsModuleItem(None)
        if self.controller and self.controller.search:
            moduleQuery = (self.controller.current_version, module)
            matched = self.controller.search.matchModule(*moduleQuery)
            moduleItem.setGhosted(not matched)
        moduleItem.controller = self.controller
        moduleItem.setupModule(module)
        moduleItem.setBreakpoint(module.is_breakpoint)
        if moduleBrush:
            moduleItem.set_custom_brush(moduleBrush)
        if not module.has_annotation_with_key('__vistrail_var__'):
            # Don't add hidden vistrail variable modules to the scene
            self.addItem(moduleItem)
        self.modules[module.id] = moduleItem
        self._old_module_ids.add(module.id)
        return moduleItem

    def addConnection(self, connection, connectionBrush=None):
        """ addConnection(connection: Connection) -> QGraphicsConnectionItem
        Add a connection to the scene
        
        """
        srcModule = self.modules[connection.source.moduleId]
        dstModule = self.modules[connection.destination.moduleId]
        srcPoint = srcModule.getOutputPortPosition(connection.source)
        dstPoint = dstModule.getInputPortPosition(connection.destination)
        connectionItem = QGraphicsConnectionItem(srcPoint, dstPoint,
                                                 srcModule, dstModule,
                                                 connection)
        connectionItem.id = connection.id
        connectionItem.connection = connection
        if connectionBrush:
            connectionItem.set_custom_brush(connectionBrush)
        if not srcModule.module.has_annotation_with_key('__vistrail_var__'):
            # Don't add connections to hidden vistrail variable modules to the scene
            self.addItem(connectionItem)
        else:
            var_uuid = srcModule.module.get_annotation_by_key('__vistrail_var__').value
            var_name = self.controller.get_vistrail_variable_name_by_uuid(var_uuid)
            port_item = dstModule.inputPorts[connection.destination.spec]
            port_item.setBrush(CurrentTheme.PORT_FILLED_BRUSH)
            # Update the tooltip for this version
            try:
                tooltip = port_item.toolTip() + '\nVistrail Variable: "%s"'%var_name
                port_item.setToolTip(tooltip)
            except Exception, e:
                port_item.setToolTip("ERROR with tool tip")
                raise e
        self.connections[connection.id] = connectionItem
        self._old_connection_ids.add(connection.id)
        srcModule.addConnectionItem(connectionItem)
        dstModule.addConnectionItem(connectionItem)
        return connectionItem

    def selected_subgraph(self):
        """Returns the subgraph containing the selected modules and its
        mutual connections.
        
        """
        items = self.selectedItems()
        modules = [x.id
                   for x in items
                   if type(x) == QGraphicsModuleItem]
        return self.controller.current_pipeline.graph.subgraph(modules)

#     def create_abstraction(self):
#         subgraph = self.selected_subgraph()
#         try:
#             self.controller.create_abstraction(subgraph)
#         except Vistrail.InvalidAbstraction, e:
#             dlg = QtGui.QMessageBox.warning(None,
#                                             "Invalid Abstraction",
#                                             str(e))

#    def contextMenuEvent(self, event):
#        selectedItems = self.selectedItems()
#        if len(selectedItems) == 0:
#            return QInteractiveGraphicsScene.contextMenuEvent(self, event)
#        else:
#            self._context_menu.exec_(event.screenPos())

    def clear(self):
        """ clear() -> None
        Clear the whole scene
        
        """
        self.modules = {}
        self.connections = {}
        self._old_module_ids = set()
        self._old_connection_ids = set()
        self.unselect_all()
        self.clearItems()
        
    def remove_module(self, m_id):
        """remove_module(m_id): None

        Removes module from scene, updating appropriate data structures.

        """
        core_module = self.modules[m_id].module
        if not core_module.has_annotation_with_key('__vistrail_var__'):
            self.removeItem(self.modules[m_id])
        del self.modules[m_id]
        self._old_module_ids.remove(m_id)

    def remove_connection(self, c_id):
        """remove_connection(c_id): None

        Removes connection from scene, updating appropriate data structures.

        """
        # if c_id in self.connections:
        connItem = self.connections[c_id]
        (srcModule, dstModule) = connItem.connectingModules
        srcModule.removeConnectionItem(connItem)
        dstModule.removeConnectionItem(connItem)
        if not srcModule.module.has_annotation_with_key('__vistrail_var__'):
            self.removeItem(self.connections[c_id])
        del self.connections[c_id]
        self._old_connection_ids.remove(c_id)
        

    def recreate_module(self, pipeline, m_id):
        """recreate_module(pipeline, m_id): None

        Recreates a module on the scene."""
        selected = self.modules[m_id].isSelected()

        depending_connections = \
            [c_id for c_id in self.modules[m_id].dependingConnectionItems()]
        # old_depending_connections = self.modules[m_id]._old_connection_ids
        
        self.remove_module(m_id)
        
        #when configuring a python source, maybe connections were deleted
        # but are not in the current pipeline. So we need to check the depending
        # connections of the module just before the configure. 
        for c_id in depending_connections:
            self.remove_connection(c_id)
        
        self.addModule(pipeline.modules[m_id])
        for c_id in depending_connections:
            # only add back those connections that are in the pipeline
            if c_id in pipeline.connections:
                self.addConnection(pipeline.connections[c_id])
                               
        if selected:
            self.modules[m_id].setSelected(True)
            
    def setupScene(self, pipeline):
        """ setupScene(pipeline: Pipeline) -> None
        Construct the scene to view a pipeline
        
        """
        old_pipeline = self.pipeline
        self.pipeline = pipeline

        if self.noUpdate: return
        if (pipeline is None or 
            (old_pipeline and not old_pipeline.is_valid) or 
            (pipeline and not pipeline.is_valid)):
            # clear things
            self.clear()
        if not pipeline: return 
            
        needReset = len(self.items())==0
        try:
            new_modules = set(pipeline.modules)
            modules_to_be_added = new_modules - self._old_module_ids
            modules_to_be_deleted = self._old_module_ids - new_modules
            common_modules = new_modules.intersection(self._old_module_ids)

            new_connections = set(pipeline.connections)
            connections_to_be_added = new_connections - self._old_connection_ids
            connections_to_be_deleted = self._old_connection_ids - new_connections
            common_connections = new_connections.intersection(self._old_connection_ids)

            # Check if connections to be added require 
            # optional ports in modules to be visible
            for c_id in connections_to_be_added:
                connection = pipeline.connections[c_id]
                smid = connection.source.moduleId
                s = connection.source.spec
                if s and s.optional:
                    smm = pipeline.modules[smid]
                    smm.portVisible.add((PortEndPoint.Source,s.name))
                dmid = connection.destination.moduleId   
                d = connection.destination.spec
                if d and d.optional:
                    dmm = pipeline.modules[dmid]
                    dmm.portVisible.add((PortEndPoint.Destination,d.name))

            # remove old connection shapes
            for c_id in connections_to_be_deleted:
                self.remove_connection(c_id)
            # remove old module shapes
            for m_id in modules_to_be_deleted:
                self.remove_module(m_id)

            selected_modules = []
            # create new module shapes
            for m_id in modules_to_be_added:
                self.addModule(pipeline.modules[m_id])
                if self.modules[m_id].isSelected():
                    selected_modules.append(m_id)

            moved = set()
            # Update common modules
            for m_id in common_modules:
                tm_item = self.modules[m_id]
                tm = tm_item.module
                nm = pipeline.modules[m_id]
                if tm_item.moduleHasChanged(nm):
                    self.recreate_module(pipeline, m_id)
                if tm_item.isSelected():
                    selected_modules.append(m_id)
                if self.controller and self.controller.search:
                    moduleQuery = (self.controller.current_version, nm)
                    matched = \
                        self.controller.search.matchModule(*moduleQuery)
                    tm_item.setGhosted(not matched)
                else:
                    tm_item.setGhosted(False)
                tm_item.setBreakpoint(nm.is_breakpoint)

            # create new connection shapes
            for c_id in connections_to_be_added:
                self.addConnection(pipeline.connections[c_id])

            # Update common connections
            for c_id in common_connections:
                connection = pipeline.connections[c_id]
                pip_c = self.connections[c_id]
                pip_c.connectingModules = (self.modules[connection.source.moduleId],
                                           self.modules[connection.destination.moduleId])
                (srcModule, dstModule) = pip_c.connectingModules

            self._old_module_ids = new_modules
            self._old_connection_ids = new_connections
            self.unselect_all()
            self.reset_module_colors()
            for m_id in selected_modules:
                self.modules[m_id].setSelected(True)
        except ModuleRegistryException, e:
            import traceback
            traceback.print_exc()
            views = self.views()
            assert len(views) > 0
            debug.critical("Missing package/module",
                ("Package '%s' is missing (or module '%s' is not present " +
                "in that package)") % (e._identifier, e._name))
            self.clear()
            self.controller.change_selected_version(0)

        if needReset and len(self.items())>0:
            self.fitToAllViews()

    def dragEnterEvent(self, event):
        """ dragEnterEvent(event: QDragEnterEvent) -> None
        Set to accept drops from the module palette
        
        """
        if (self.controller and
            (type(event.source())==QModuleTreeWidget or
             type(event.source())==QDragVariableLabel)):
            data = event.mimeData()
            if (hasattr(data, 'items') or hasattr(data, 'variableData')
                and not self.read_only_mode):
                event.accept()
                return
        # Ignore if not accepted and returned by this point
        event.ignore()
        
    def dragMoveEvent(self, event):
        """ dragMoveEvent(event: QDragMoveEvent) -> None
        Set to accept drag move event from the module palette
        
        """
        if (self.controller and
            (type(event.source())==QModuleTreeWidget or
             type(event.source())==QDragVariableLabel)):
            data = event.mimeData()
            if hasattr(data, 'items') and not self.read_only_mode:
                event.accept()
                return
            elif hasattr(data, 'variableData'):
                # Find nearest suitable port
                tmp_port = QGraphicsPortItem(0, 0, False)
                tmp_port.port = data.variableData[0]
                nearest_port = tmp_port.findSnappedPort(event.scenePos(), self)
                # Unhighlight previous nearest port
                if self._var_selected_port is not None:
                    self._var_selected_port.setPen(CurrentTheme.PORT_PEN)
                self._var_selected_port = nearest_port
                # Highlight new nearest port
                if nearest_port is not None:
                    nearest_port.setPen(CurrentTheme.PORT_SELECTED_PEN)
                    QtGui.QToolTip.showText(event.screenPos(), nearest_port.toolTip())
                    event.accept()
                    return
                else:
                    QtGui.QToolTip.hideText()
        # Ignore if not accepted and returned by this point
        if not systemType in ['Darwin']:
            # Workaround: On a Mac, dropEvent isn't called if dragMoveEvent is ignored
            event.ignore()

    def dragLeaveEvent(self, event):
        if type(event.source()) == QDragVariableLabel:
            data = event.mimeData()
            if hasattr(data, 'variableData'):
                if self._var_selected_port is not None:
                    self._var_selected_port.setPen(CurrentTheme.PORT_PEN)
                    self._var_selected_port = None
                event.accept()

    def unselect_all(self):
        self.clearSelection()
        if self.pipeline_tab:
            self.pipeline_tab.moduleSelected(-1)

    def add_module_event(self, event, data):
        """Adds a new module from a drop event"""
        item = data.items[0]
        self.controller.reset_pipeline_view = False
        self.noUpdate = True
        internal_version = -1L
        reg = get_module_registry()
        if reg.is_abstraction(item.descriptor):
            internal_version = item.descriptor.module.internal_version
        adder = self.controller.add_module_from_descriptor
        module = adder(item.descriptor, 
                       event.scenePos().x(),
                       -event.scenePos().y(),
                       internal_version)
        self.reset_module_colors()
        graphics_item = self.addModule(module)
        graphics_item.update()
        self.unselect_all()
        # Change selection
        graphics_item.setSelected(True)

        # controller changed pipeline: update ids
        self._old_connection_ids = set(self.controller.current_pipeline.connections)
        self._old_module_ids = set(self.controller.current_pipeline.modules)

        # We are assuming the first view is the real pipeline view                
        self.views()[0].setFocus()

        self.noUpdate = False


    def dropEvent(self, event):
        """ dropEvent(event: QDragMoveEvent) -> None
        Accept drop event to add a new module
        
        """
        if (self.controller and
            (type(event.source())==QModuleTreeWidget or
             type(event.source())==QDragVariableLabel)):
            data = event.mimeData()
            if hasattr(data, 'items') and not self.read_only_mode:
                assert len(data.items) == 1
                if self.controller.current_version==-1:
                    self.controller.change_selected_version(0)
                self.add_module_event(event, data)
                event.accept()
                return
            elif hasattr(data, 'variableData'):
                if self._var_selected_port is not None:
                    # Unhighlight selected port and get var data
                    self._var_selected_port.setPen(CurrentTheme.PORT_PEN)
                    output_portspec = data.variableData[0]
                    var_uuid = data.variableData[1]
                    var_name = data.variableData[2]
                    descriptor = output_portspec.descriptors()[0]
                    input_module = self._var_selected_port.parentItem().module
                    input_portspec = self._var_selected_port.port
                    # If no module exists for this var, create one
                    ops = []
                    var_module = None
                    var_module_added = False
                    for m_item in self.modules.itervalues():
                        if m_item.module.has_annotation_with_key('__vistrail_var__') and m_item.module.get_annotation_by_key('__vistrail_var__').value == var_uuid:
                            var_module = m_item.module
                            break
                    if var_module is None:
                        var_module = self.controller.create_module_from_descriptor(descriptor, event.scenePos().x(), -event.scenePos().y())
                        var_annotation = Annotation(id=self.controller.id_scope.getNewId(Annotation.vtType), key='__vistrail_var__', value=var_uuid)
                        var_module.add_annotation(var_annotation)
                        var_func = self.controller.create_function(var_module, 'value')
                        var_module.add_function(var_func)
                        ops.append(('add', var_module))
                        var_module_added = True
                    else:
                        # Check if selected port is already connected to vistrail var module
                        connections = self.controller.get_connections_to(self.controller.current_pipeline, [input_module.id])
                        for connection in connections:
                            if connection.source.moduleId == var_module.id:
                                QtGui.QMessageBox.information(None, 'Already Connected', 'Vistrail Variable "%s" is already connected to this port.'%var_name)
                                event.accept()
                                return
                    # Connect selected port to vistrail var module
                    var_connection = self.controller.create_connection(var_module, output_portspec, input_module, input_portspec)
                    ops.append(('add', var_connection))
                    var_action = create_action(ops)
                    self.controller.flush_delayed_actions()
                    self.controller.add_new_action(var_action)
                    self.controller.vistrail.change_description("Connected Vistrail Variable", var_action.id)
                    self.controller.perform_action(var_action)
                    # Add [hidden] items for module and connection to pipeline view
                    if var_module_added:
                        self.addModule(var_module)
                    self.addConnection(var_connection)
                    # Update the version view node to fit text properly
                    version_item = self.controller.vistrail_view.version_view.scene().versions[self.controller.current_version]
                    version_item.updateWidthFromLabel()
                    self._var_selected_port = None
                    event.accept()
                    return
        # Ignore if not accepted and returned by this point
        event.ignore()

    def delete_selected_items(self):
        selectedItems = self.selectedItems()
        if len(selectedItems)>0:
            modules = []
            module_ids = []
            connection_ids = []
            for it in selectedItems:
                if isinstance(it, QGraphicsModuleItem):
                    modules.append(it)
                    module_ids.append(it.id)
                elif isinstance(it, QGraphicsConnectionItem):
                    connection_ids.append(it.id)
            if len(modules)>0:
                self.noUpdate = True
                dep_connection_ids = set()
                for m in modules:
                    dep_connection_ids.update(
                        m.dependingConnectionItems().iterkeys())
                # remove_connection updates the dependency list on the
                # other side of connections, cannot use removeItem
                for c_id in dep_connection_ids:
                    self.remove_connection(c_id)
                for m_id in module_ids:
                    self.remove_module(m_id)
                self.controller.delete_module_list(module_ids)
                self.updateSceneBoundingRect()
                self.reset_module_colors()
                self.update()
                self.noUpdate = False
                # Notify that no module is selected
                self.emit(QtCore.SIGNAL('moduleSelected'),
                          -1, selectedItems)
                # Current pipeline changed, so we need to change the
                # _old_*_ids. However, remove_module takes care of
                # module ids, and the for loop above takes care of
                # connection ids. So we don't need to call anything.
            else:
                for c_id in connection_ids:
                    self.remove_connection(c_id)
                self.controller.reset_pipeline_view = False
                self.controller.delete_connection_list(connection_ids)
                self.reset_module_colors()
                self.controller.reset_pipeline_view = True
                # Current pipeline changed, so we need to change the
                # _old_connection_ids. However, remove_connection
                # above takes care of connection ids, so we don't need
                # to call anything.        

    def keyPressEvent(self, event):
        """ keyPressEvent(event: QKeyEvent) -> None
        Capture 'Del', 'Backspace' for deleting modules.
        Ctrl+C, Ctrl+V, Ctrl+A for copy, paste and select all
        
        """        
        if (self.controller and
            event.key() in [QtCore.Qt.Key_Backspace, QtCore.Qt.Key_Delete]):
            if not self.read_only_mode:
                self.delete_selected_items()
        else:
            QInteractiveGraphicsScene.keyPressEvent(self, event)
            # super(QPipelineScene, self).keyPressEvent(event)

    def get_selected_module_ids(self):
        module_ids = []
        for item in self.selectedItems():
            if type(item) == QGraphicsModuleItem:
                module_ids.append(item.module.id)
        return module_ids

    def get_selected_item_ids(self, dangling=False):
        """get_selected_item_ids( self, dangling: bool) -> 
             (module_ids : list, connection_ids : list)
           returns the list of selected modules and the connections
           between them.  If dangling is true, it includes connections
           for which only one end point is selected, otherwise it only
           includes connectiosn where both end points are selected

        """
        selectedItems = self.selectedItems()
        if len(selectedItems) <= 0:
            return None
        
        connection_ids = {}
        module_ids = {}
        for item in selectedItems:
            if type(item)==QGraphicsModuleItem:
                module_ids[item.module.id] = 1
        for item in selectedItems:
            if type(item)==QGraphicsModuleItem:
                for connItem in item.dependingConnectionItems().itervalues():
                    conn = connItem.connection
                    if not conn.id in connection_ids:
                        source_exists = conn.sourceId in module_ids
                        dest_exists = conn.destinationId in module_ids
                        if source_exists and dest_exists:
                            connection_ids[conn.id] = 1
                        elif dangling and (source_exists or dest_exists):
                            connection_ids[conn.id] = 1
        return (module_ids.keys(), connection_ids.keys())

    def group(self):
        items = self.get_selected_item_ids(True)
        if items is not None:
            # self.clear()
            self.controller.create_group(items[0], items[1])
            self.setupScene(self.controller.current_pipeline)

    def ungroup(self):
        items = self.get_selected_item_ids(True)
        if items is not None:
            # self.clear()
            self.controller.ungroup_set(items[0])
            self.setupScene(self.controller.current_pipeline)
        
    def makeAbstraction(self):
        items = self.get_selected_item_ids(True)
        if items is not None:
            # self.clear()
            self.controller.create_abstraction_with_prompt(items[0], items[1])
            self.setupScene(self.controller.current_pipeline)

    def convertToAbstraction(self):
        items = self.get_selected_item_ids(False)
        if items is not None:
            # self.clear()
            self.controller.create_abstractions_from_groups(items[0])
            self.setupScene(self.controller.current_pipeline)

    def importAbstraction(self):
        items = self.get_selected_item_ids(False)
        if items is not None:
            self.controller.import_abstractions(items[0])

    def exportAbstraction(self):
        items = self.get_selected_item_ids(False)
        if items is not None:
            self.controller.export_abstractions(items[0])

    def copySelection(self):
        """ copySelection() -> None
        Copy the current selected modules into clipboard
        
        """
        items = self.get_selected_item_ids(False)
        if items is not None:
            cb = QtGui.QApplication.clipboard()
            text = self.controller.copy_modules_and_connections(items[0],items[1])
            cb.setText(text)
            
    def pasteFromClipboard(self, center):
        """ pasteFromClipboard(center: (float, float)) -> None
        Paste modules/connections from the clipboard into this pipeline view
        
        """
        if self.controller and not self.read_only_mode:
            if self.controller.current_version == -1:
                self.controller.change_selected_version(0)
            cb = QtGui.QApplication.clipboard()        
            text = str(cb.text().toAscii())
            if text=='' or not text.startswith("<workflow"): return
            ids = self.controller.paste_modules_and_connections(text, center)
            self.setupScene(self.controller.current_pipeline)
            self.reset_module_colors()
            if len(ids) > 0:
                self.unselect_all()
            for moduleId in ids:
                self.modules[moduleId].setSelected(True)
            
    def event(self, e):
        """ event(e: QEvent) -> None        
        Process the set module color events
        
        """
        if e.type()==QModuleStatusEvent.TYPE:
            if e.moduleId>=0:
                item = self.modules.get(e.moduleId, None)
                if not item:
                    return True
                item.setToolTip(e.toolTip)
                item.errorTrace = e.errorTrace
                statusMap =  {
                    0: CurrentTheme.SUCCESS_MODULE_BRUSH,
                    1: CurrentTheme.ERROR_MODULE_BRUSH,
                    2: CurrentTheme.NOT_EXECUTED_MODULE_BRUSH,
                    3: CurrentTheme.ACTIVE_MODULE_BRUSH,
                    4: CurrentTheme.COMPUTING_MODULE_BRUSH,
                    6: CurrentTheme.PERSISTENT_MODULE_BRUSH,
                    7: CurrentTheme.SUSPENDED_MODULE_BRUSH,
                    }
                item.setProgress(e.progress)
                if e.status in statusMap:
                    item.statusBrush = statusMap[e.status]
                else:
                    item.statusBrush = None
                item._needs_state_updated = True
                item.update()
            return True
        return QInteractiveGraphicsScene.event(self, e)

    def selectAll(self):
        """ selectAll() -> None
        Select all module items in the scene
        
        """
        for item in self.items():
            item.setSelected(True)

    def open_configure_window(self, id):
        """ open_configure_window(int) -> None
        Open the modal configuration window for module with given id
        """
        from gui.vistrails_window import _app
        _app.configure_module()
            
    def perform_configure_done_actions(self, module_id):
        if self.controller:
            self.reset_module_colors()
            self.flushMoveActions()
            self.recreate_module(self.controller.current_pipeline, module_id)
             
    def open_documentation_window(self, id):
        """ open_documentation_window(int) -> None
        Opens the modal module documentation window for module with given id
        """
        from gui.vistrails_window import _app
        _app.show_documentation()

    def toggle_breakpoint(self, id):
        """ toggle_breakpoint(int) -> None
        Toggles the breakpoint attribute for the module with given id
        """
        if self.controller:
            module = self.controller.current_pipeline.modules[id]
            module.toggle_breakpoint()
            self.recreate_module(self.controller.current_pipeline, id)

    def toggle_watched(self, id):
        if self.controller:
            module = self.controller.current_pipeline.modules[id]
            module.toggle_watched()

    def print_error(self, id):
        toolTip = str(self.modules[id].toolTip())
        errorTrace = self.modules[id].errorTrace
        if not toolTip and not errorTrace:
            return
        text = toolTip
        if errorTrace and errorTrace.strip() != 'None':
            text += '\n\n' + errorTrace
        class StackPopup(QtGui.QDialog):
            def __init__(self, errorTrace='', parent=None):
                QtGui.QDialog.__init__(self, parent)
                self.resize(700, 400)
                self.setWindowTitle('Module Error')
                layout = QtGui.QVBoxLayout()
                self.setLayout(layout)
                text = QtGui.QTextEdit('')
                text.insertPlainText(errorTrace)
                text.setReadOnly(True)
                text.setLineWrapMode(QtGui.QTextEdit.NoWrap)
                layout.addWidget(text)
                close = QtGui.QPushButton('Close', self)
                close.setFixedWidth(100)
                layout.addWidget(close)
                self.connect(close, QtCore.SIGNAL('clicked()'),
                             self, QtCore.SLOT('close()'))
        sp = StackPopup(text)
        sp.exec_()

    def open_annotations_window(self, id):
        """ open_annotations_window(int) -> None
        Opens the modal annotations window for module with given id
        """
        if self.controller:
            from gui.module_info import QModuleInfo
            module_info = QModuleInfo.instance()
            module_info.show_annotations()

    def open_module_label_window(self, id):
        """ open_module_label_window(int) -> None
        Opens the modal module label window for setting module label
        """
        if self.controller:
            module = self.controller.current_pipeline.modules[id]
            if module.has_annotation_with_key('__desc__'):
                currentLabel = module.get_annotation_by_key('__desc__').value.strip()
            else:
                currentLabel = ''
            (text, ok) = QtGui.QInputDialog.getText(None, 'Set Module Label',
                                                    'Enter the module label',
                                                    QtGui.QLineEdit.Normal,
                                                    currentLabel)
            if ok:
                if text.isEmpty():
                    if module.has_annotation_with_key('__desc__'):
                        self.controller.delete_annotation('__desc__', id)
                        self.recreate_module(self.controller.current_pipeline, id)
                else:
                    self.controller.add_annotation(('__desc__', str(text)), id)
                    self.recreate_module(self.controller.current_pipeline, id)

    ##########################################################################
    # Execution reporting API

    def set_module_success(self, moduleId):
        """ set_module_success(moduleId: int) -> None
        Post an event to the scene (self) for updating the module color
        
        """
        QtGui.QApplication.postEvent(self,
                                     QModuleStatusEvent(moduleId, 0, ''))
        QtCore.QCoreApplication.processEvents()

    def set_module_error(self, moduleId, error, errorTrace=None):
        """ set_module_error(moduleId: int, error: str) -> None
        Post an event to the scene (self) for updating the module color
        
        """
        QtGui.QApplication.postEvent(self,
                                     QModuleStatusEvent(moduleId, 1, error,
                                                      errorTrace = errorTrace))
        QtCore.QCoreApplication.processEvents()

    def set_module_not_executed(self, moduleId):
        """ set_module_not_executed(moduleId: int) -> None
        Post an event to the scene (self) for updating the module color
        
        """
        QtGui.QApplication.postEvent(self,
                                     QModuleStatusEvent(moduleId, 2, ''))
        QtCore.QCoreApplication.processEvents()

    def set_module_active(self, moduleId):
        """ set_module_active(moduleId: int) -> None
        Post an event to the scene (self) for updating the module color
        
        """
        QtGui.QApplication.postEvent(self,
                                     QModuleStatusEvent(moduleId, 3, ''))
        QtCore.QCoreApplication.processEvents()

    def set_module_computing(self, moduleId):
        """ set_module_computing(moduleId: int) -> None
        Post an event to the scene (self) for updating the module color
        
        """
        QtGui.QApplication.postEvent(self,
                                     QModuleStatusEvent(moduleId, 4, ''))
        QtCore.QCoreApplication.processEvents()
        
    def set_module_progress(self, moduleId, progress=0.0):
        """ set_module_computing(moduleId: int, progress: float) -> None
        Post an event to the scene (self) for updating the module color
        
        """
        QtGui.QApplication.postEvent(self,
                                     QModuleStatusEvent(moduleId, 5,
                                                        '%d%% Completed' % int(progress*100),
                                                        progress))
        QtCore.QCoreApplication.processEvents()

    def set_module_persistent(self, moduleId):
        QtGui.QApplication.postEvent(self,
                                     QModuleStatusEvent(moduleId, 6, ''))
        QtCore.QCoreApplication.processEvents()

    def set_module_suspended(self, moduleId, error):
        """ set_module_suspended(moduleId: int, error: str) -> None
        Post an event to the scene (self) for updating the module color
        
        """
        text = "Module is suspended, reason: %s" % error
        QtGui.QApplication.postEvent(self,
                                     QModuleStatusEvent(moduleId, 7, text))
        QtCore.QCoreApplication.processEvents()


    def reset_module_colors(self):
        for module in self.modules.itervalues():
            module.statusBrush = None
            module._needs_state_updated = True

    def hasMoveActions(self):
        controller = self.controller
        for (mId, item) in self.modules.iteritems():
            module = controller.current_pipeline.modules[mId]
            (dx,dy) = (item.scenePos().x(), -item.scenePos().y())
            if (dx != module.center.x or dy != module.center.y):
                return True
        return False

    def flushMoveActions(self):
        """ flushMoveActions() -> None
        Update all move actions into vistrail
        
        """
        controller = self.controller
        moves = []
        for (mId, item) in self.modules.iteritems():
            module = controller.current_pipeline.modules[mId]
            (dx,dy) = (item.scenePos().x(), -item.scenePos().y())
            if (dx != module.center.x or dy != module.center.y):
                moves.append((mId, dx, dy))
        if len(moves)>0:
            controller.quiet = True
            controller.move_module_list(moves)
            controller.quiet = False
            return True
        return False

    def set_read_only_mode(self, on):
        """set_read_only_mode(on: bool) -> None
        This will prevent user to add/remove modules and connections."""
        self.read_only_mode = on

class QModuleStatusEvent(QtCore.QEvent):
    """
    QModuleStatusEvent is trying to handle thread-safe real-time
    module updates in the scene through post-event
    
    """
    TYPE = QtCore.QEvent.Type(QtCore.QEvent.User)
    def __init__(self, moduleId, status, toolTip, progress=0.0,
                 errorTrace=None):
        """ QModuleStatusEvent(type: int) -> None        
        Initialize the specific event with the module status. Status 0
        for success, 1 for error and 2 for not execute, 3 for active,
        and 4 for computing
        
        """
        QtCore.QEvent.__init__(self, QModuleStatusEvent.TYPE)
        self.moduleId = moduleId
        self.status = status
        self.toolTip = toolTip
        self.progress = progress
        self.errorTrace = errorTrace
            
class QPipelineView(QInteractiveGraphicsView, BaseView):
    """
    QPipelineView inherits from QInteractiveGraphicsView that will
    handle drawing of module, connection shapes and selecting
    mechanism.
    
    """

    def __init__(self, parent=None):
        """ QPipelineView(parent: QWidget) -> QPipelineView
        Initialize the graphics view and its properties
        
        """
        QInteractiveGraphicsView.__init__(self, parent)
        BaseView.__init__(self)
        self.setScene(QPipelineScene(self))
        self.set_title('Pipeline')
        self.controller = None
        self.detachable = True

    def set_default_layout(self):
        from gui.module_palette import QModulePalette
        from gui.module_info import QModuleInfo
        self.set_palette_layout(
            {QtCore.Qt.LeftDockWidgetArea: QModulePalette,
             QtCore.Qt.RightDockWidgetArea: QModuleInfo,
             })
            
    def set_action_links(self):
        # FIXME execute should be tied to a pipleine_changed signal...
        self.action_links = \
            {'copy': ('module_changed', self.has_selected_modules),
             'paste': ('clipboard_changed', self.clipboard_non_empty),
             'group': ('module_changed', self.has_selected_modules),
             'ungroup': ('module_changed', self.has_selected_groups),
             'showGroup': ('module_changed', self.has_selected_group),
             'makeAbstraction': ('module_changed', self.has_selected_modules),
             'execute': ('pipeline_changed', self.pipeline_non_empty),
             'configureModule': ('module_changed', self.has_selected_module),
             'documentModule': ('module_changed', self.has_selected_module),
             'makeAbstraction': ('module_changed', self.has_selected_modules),
             'convertToAbstraction': ('module_changed', 
                                      self.has_selected_group),
             'editAbstraction': ('module_changed', self.has_selected_abs),
             'importAbstraction': ('module_changed', self.has_selected_abs),
             'exportAbstraction': ('module_changed', self.has_selected_abs),
             'publishWeb' : ('pipeline_changed', self.check_publish_db),
             'publishPaper' : ('pipeline_changed', self.pipeline_non_empty),
             'controlFlowAssist': ('pipeline_changed', self.pipeline_non_empty),
             'redo': ('version_changed', self.can_redo),
             'undo': ('version_changed', self.can_undo),
             }

    def can_redo(self, versionId):
        return self.controller and self.controller.can_redo()

    def can_undo(self, versionId):
        return self.controller and self.controller.can_undo()
    
    def set_action_defaults(self):
        self.action_defaults.update(
        { 'execute': [('setEnabled', True, self.set_execute_action),
                      ('setIcon', False, CurrentTheme.EXECUTE_PIPELINE_ICON),
                      ('setToolTip', False, 'Execute the current pipeline')],
        })
        
    def set_execute_action(self):
        if self.controller:
            return self.pipeline_non_empty(self.controller.current_pipeline)
        return False
    
    def execute(self):
        # view.checkModuleConfigPanel()
        self.controller.execute_current_workflow()
        from gui.vistrails_window import _app
        _app.notify('execution_updated')
        
    def publish_to_web(self):
        from gui.publishing import QVersionEmbed
        panel = QVersionEmbed.instance()
        panel.switchType('Wiki')
        panel.set_visible(True)
        
    def publish_to_paper(self):
        from gui.publishing import QVersionEmbed
        panel = QVersionEmbed.instance()
        panel.switchType('Latex')
        panel.set_visible(True)
        
    def check_publish_db(self, pipeline):
        loc = self.controller.locator
        result = False
        if hasattr(loc,'host'):
            result = True    
        return result and self.pipeline_non_empty(pipeline)
    
    def has_selected_modules(self, module, only_one=False):
        module_ids_len = len(self.scene().get_selected_module_ids())
        #print '  module_ids_len:', module_ids_len
        if only_one and module_ids_len != 1:
            return False
        return module_ids_len > 0

    def has_selected_module(self, module):
        #print 'calling has_selected_module'
        return self.has_selected_modules(module, True)

    def has_selected_groups(self, module, only_one=False):
        module_ids = self.scene().get_selected_module_ids()
        if len(module_ids) <= 0:
            return False
        if only_one and len(module_ids) != 1:
            return False
        for m_id in module_ids:
            if not self.scene().current_pipeline.modules[m_id].is_group():
                return False
        return True

    def has_selected_group(self, module):
        return self.has_selected_groups(True)

    def has_selected_abs(self, module):
        module_ids = self.scene().get_selected_module_ids()
        if len(module_ids) != 1:
            return False
        for m_id in module_ids:
            if not self.scene().current_pipeline.modules[m_id].is_abstraction():
                return False
        return True        

    def clipboard_non_empty(self):
        clipboard = QtGui.QApplication.clipboard()
        clipboard_text = clipboard.text()
        return not clipboard_text.isEmpty() #and \
        #    str(clipboard_text).startswith("<workflow")

    def pipeline_non_empty(self, pipeline):
        return pipeline is not None and len(pipeline.modules) > 0

    def pasteFromClipboard(self):
        center = self.mapToScene(self.width()/2.0, self.height()/2.0)
        self.scene().pasteFromClipboard((center.x(), -center.y()))

    def setQueryEnabled(self, on):
        QInteractiveGraphicsView.setQueryEnabled(self, on)
        if not self.scene().noUpdate and self.scene().controller:
            self.scene().setupScene(self.scene().controller.current_pipeline)
            
    def setReadOnlyMode(self, on):
        self.scene().set_read_only_mode(on)

    def set_title(self, title):
        BaseView.set_title(self, title)
        self.setWindowTitle(title)

    def set_controller(self, controller):
        oldController = self.controller
        if oldController != controller:
            if oldController != None:
                # self.disconnect(oldController,
                #                 QtCore.SIGNAL('versionWasChanged'),
                #                 self.version_changed)
                oldController.current_pipeline_view = None
            self.controller = controller
            self.scene().controller = controller
            # self.connect(controller,
            #              QtCore.SIGNAL('versionWasChanged'),
            #              self.version_changed)
            # self.module_info.set_controller(controller)
            # self.moduleConfig.controller = controller
            # controller.current_pipeline_view = self.scene()

    def set_to_current(self):
        if self.controller.current_pipeline_view is not None:
            self.disconnect(self.controller,
                            QtCore.SIGNAL('versionWasChanged'),
                            self.controller.current_pipeline_view.parent().version_changed)
        self.controller.current_pipeline_view = self.scene()
        self.connect(self.controller,
                     QtCore.SIGNAL('versionWasChanged'),
                     self.version_changed)
        
    def get_long_title(self):
        pip_name = self.controller.get_pipeline_name()
        vt_name = self.controller.name
        self.long_title = "%s from %s"%(pip_name,vt_name)
        return self.long_title
    
    def get_controller(self):
        return self.controller

    def version_changed(self):
        self.scene().setupScene(self.controller.current_pipeline)

    def run_control_flow_assist(self):
        currentScene = self.scene()
        if currentScene.controller:
            selected_items = currentScene.get_selected_item_ids(True)
            if selected_items is None:
                selected_items = ([],[])
            selected_module_ids = selected_items[0]
            selected_connection_ids = selected_items[1]
            if len(selected_module_ids) > 0:
                dialog = QControlFlowAssistDialog(self, selected_module_ids, 
                                                  selected_connection_ids, 
                                                  currentScene)
                dialog.exec_()
            else:
                show_info('No Modules Selected', 
                          'You must select at least one module to use the '
                          'Control Flow Assistant.')
                
    def done_configure(self, mid):
        self.scene().perform_configure_done_actions(mid)

################################################################################
# Testing

import api
import gui.utils

class TestPipelineView(gui.utils.TestVisTrailsGUI):

    def test_quick_change_version_with_ports(self):
        import core.system
        filename = (core.system.vistrails_root_directory() + 
                    '/tests/resources/triangle_count.vt')
        view = api.open_vistrail_from_file(filename)
        api.select_version(-1, view.controller)
        api.select_version('count + area', view.controller)
        api.select_version('writing to file', view.controller)

    def test_change_version_with_common_connections(self):
        import core.system
        filename = (core.system.vistrails_root_directory() + 
                    '/tests/resources/terminator.vt')
        view = api.open_vistrail_from_file(filename)
        api.select_version('Image Slices HW', view.controller)
        api.select_version('Combined Rendering HW', view.controller)

    def test_switch_mode(self):
        api.switch_to_pipeline_view()
        api.switch_to_history_view()
        api.switch_to_query_view()
        api.switch_to_pipeline_view()
        api.switch_to_history_view()
        api.switch_to_query_view()

    def test_group(self):
        api.new_vistrail()
        m1 = api.add_module(0, 0,    'edu.utah.sci.vistrails.basic', 'File', '')
        m2 = api.add_module(0, -100, 'edu.utah.sci.vistrails.basic', 'File', '')
        m3 = api.add_module(0, -100, 'edu.utah.sci.vistrails.basic', 'File', '')
        r = api.get_module_registry()
        src = r.get_port_spec('edu.utah.sci.vistrails.basic', 'File', None,
                              'value_as_string', 'output')
        dst = r.get_port_spec('edu.utah.sci.vistrails.basic', 'File', None,
                              'name', 'input')
#         src = r.module_source_ports(True, 'edu.utah.sci.vistrails.basic', 'File', '')[1]
#         assert src.name == 'value_as_string'
#         dst = r.module_destination_ports(True, 'edu.utah.sci.vistrails.basic', 'File', '')[1]
#         assert dst.name == 'name'
        api.add_connection(m1.id, src, m2.id, dst)
        api.add_connection(m2.id, src, m3.id, dst)
        api.create_group([0, 1, 2], [0, 1])


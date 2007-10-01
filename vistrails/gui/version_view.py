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
""" This is a QGraphicsView for pipeline view, it also holds different
types of graphics items that are only available in the pipeline
view. It only handles GUI-related actions, the rest of the
functionalities are implemented at somewhere else,
e.g. core.vistrails

QGraphicsLinkItem
QGraphicsVersionItem
QVersionTreeScene
QVersionTreeView
"""

from PyQt4 import QtCore, QtGui
from core.dotty import DotLayout
from core.system import systemType
from gui.graphics_view import (QInteractiveGraphicsScene,
                               QInteractiveGraphicsView,
                               QGraphicsItemInterface,
                               QGraphicsRubberBandItem)
from gui.theme import CurrentTheme
from gui.vis_diff import QVisualDiff
from gui.qt import qt_super
import gui.utils
import math

################################################################################
# QGraphicsLinkItem

class QGraphicsLinkItem(QGraphicsItemInterface, QtGui.QGraphicsPolygonItem):
    """
    QGraphicsLinkItem is a connection shape connecting two versions
    
    """
    def __init__(self, parent=None, scene=None):
        """ QGraphicsLinkItem(parent: QGraphicsItem,
                              scene: QGraphicsScene) -> QGraphicsLinkItem
        Create the shape, initialize its pen and brush accordingly
        
        """
        QtGui.QGraphicsPolygonItem.__init__(self, parent, scene)
        self.setFlags(QtGui.QGraphicsItem.ItemIsSelectable)
        self.setZValue(0)
        self.linkPen = CurrentTheme.LINK_PEN
        self.startVersion = -1
        self.endVersion = -1
        self.ghosted = False

    def setGhosted(self, ghosted):
        """ setGhosted(ghosted: True) -> None
        Set this link to be ghosted or not
        
        """
        self.ghosted = ghosted
        if ghosted:
            self.linkPen = CurrentTheme.GHOSTED_LINK_PEN
        else:
            self.linkPen = CurrentTheme.LINK_PEN

    def setupLink(self, v1, v2, compact=True):
        """ setupLink(v1, v2: QGraphicsVersionItem, compact: bool) -> None
        Setup a line connecting v1 and v2 items
        
        """
        self.startVersion = min(v1.id, v2.id)
        self.endVersion = max(v1.id, v2.id)
        c1 = v1.sceneBoundingRect().center()
        c2 = v2.sceneBoundingRect().center()

        # Compute the line of the link and its normal line throught
        # the midpoint
        mainLine = QtCore.QLineF(c1.x(), c1.y(), c2.x(), c2.y())
        normalLine = mainLine.normalVector()        
        normalLine.setLength(CurrentTheme.LINK_SEGMENT_LENGTH)
        dis = (mainLine.pointAt(0.5)-mainLine.p1()+
               normalLine.p1()-normalLine.pointAt(0.5))
        normalLine.translate(dis.x(), dis.y())

        # Generate 2 segments along the main line and 3 segments along
        # the normal line
        if compact:
            self.lines = [mainLine]
            poly = QtGui.QPolygonF()
            poly.append(self.lines[0].p1())
            poly.append(self.lines[0].p2())
            poly.append(self.lines[0].p1())
            self.setPolygon(poly)
        else:
            self.lines = []
            gapLine = QtCore.QLineF(mainLine)
            gapLine.setLength(CurrentTheme.LINK_SEGMENT_GAP)
            gapVector = gapLine.p2()-gapLine.p1()

            # Fist segment along the main line
            line = QtCore.QLineF(mainLine)
            line.setLength(line.length()/2-CurrentTheme.LINK_SEGMENT_GAP*2)
            self.lines.append(QtCore.QLineF(line))

            # Second segment along the main line
            line.translate(line.p2()-line.p1()+gapVector*4)
            self.lines.append(QtCore.QLineF(line))

            # First normal segment in front
            line = QtCore.QLineF(normalLine)
            line.translate(gapVector*(-1.0))
            self.lines.append(QtCore.QLineF(line))

            # Middle normal segment
            self.lines.append(QtCore.QLineF(normalLine))

            # Third normal segment in back
            line = QtCore.QLineF(normalLine)
            line.translate(gapVector)
            self.lines.append(QtCore.QLineF(line))

            # Create the poly line for selection and redraw
            poly = QtGui.QPolygonF()
            poly.append(self.lines[0].p1())
            poly.append(self.lines[2].p1())
            poly.append(self.lines[4].p1())
            poly.append(self.lines[1].p2())
            poly.append(self.lines[4].p2())
            poly.append(self.lines[2].p2())
            poly.append(self.lines[0].p1())
            self.setPolygon(poly)

        self.setGhosted(v1.ghosted or v2.ghosted)

    def paint(self, painter, option, widget=None):
        """ paint(painter: QPainter, option: QStyleOptionGraphicsItem,
                  widget: QWidget) -> None
        Peform actual painting of the link
        
        """
        if self.isSelected():
            painter.setPen(CurrentTheme.LINK_SELECTED_PEN)
        else:
            painter.setPen(self.linkPen)
        for line in self.lines:
            painter.drawLine(line)

    def itemChange(self, change, value):
        """ itemChange(change: GraphicsItemChange, value: QVariant) -> QVariant
        Do not allow link to be selected with version shape
        
        """
        if change==QtGui.QGraphicsItem.ItemSelectedChange and value.toBool():
            selectedItems = self.scene().selectedItems()
            for item in selectedItems:
                if type(item)==QGraphicsVersionItem:
                    return QtCore.QVariant(False)
        return QtGui.QGraphicsPolygonItem.itemChange(self, change, value)

##############################################################################
# QGraphicsVersionItem


class QGraphicsVersionItem(QGraphicsItemInterface, QtGui.QGraphicsEllipseItem):
    """
    QGraphicsVersionItem is the version shape holding version id and
    label
    
    """
    def __init__(self, parent=None, scene=None):
        """ QGraphicsVersionItem(parent: QGraphicsItem, scene: QGraphicsScene)
                                -> QGraphicsVersionItem
        Create the shape, initialize its pen and brush accordingly
        
        """
        QtGui.QGraphicsEllipseItem.__init__(self, parent, scene)
        self.setZValue(1)
        self.setAcceptDrops(True)
        self.versionPen = CurrentTheme.VERSION_PEN
        self.versionLabelPen = CurrentTheme.VERSION_LABEL_PEN
        self.versionBrush = CurrentTheme.VERSION_USER_BRUSH
        self.setFlags(QtGui.QGraphicsItem.ItemIsSelectable)
        self.id = -1
        self.label = ''
        self.dragging = False
        self.ghosted = False
        self.createActions()
        
        # Need a timer to start a drag to avoid stalls on QGraphicsView
        self.dragTimer = QtCore.QTimer()
        self.dragTimer.setSingleShot(True)
        self.dragTimer.connect(self.dragTimer,
                               QtCore.SIGNAL('timeout()'),
                               self.startDrag)

        self.dragPos = QtCore.QPoint()

    def setGhosted(self, ghosted=True):
        """ setGhosted(ghosted: True) -> None
        Set this version to be ghosted or not
        
        """
        self.ghosted = ghosted
        if ghosted:
            self.versionPen = CurrentTheme.GHOSTED_VERSION_PEN
            self.versionLabelPen = CurrentTheme.GHOSTED_VERSION_LABEL_PEN
            self.versionBrush = CurrentTheme.GHOSTED_VERSION_USER_BRUSH
        else:
            self.versionPen = CurrentTheme.VERSION_PEN
            self.versionLabelPen = CurrentTheme.VERSION_LABEL_PEN
            self.versionBrush = CurrentTheme.VERSION_USER_BRUSH

    def setSaturation(self, isThisUser, sat):
        """ setSaturation(isThisUser: bool, sat: float) -> None        
        Set the color of this version depending on whose is the user
        and its saturation
        
        """
        if not self.ghosted:
            if isThisUser:
                brush = CurrentTheme.VERSION_USER_BRUSH
            else:
                brush = CurrentTheme.VERSION_OTHER_BRUSH

            (h, s, v, a) = brush.color().getHsvF()
            newHsv = (h, s*sat, v+(1.0-v)*(1-sat), a)
            self.versionBrush = QtGui.QBrush(QtGui.QColor.fromHsvF(*newHsv))

    def setupVersion(self, node, label):
        """ setupPort(node: DotNode, label: str) -> None
        Update the version dimensions and id
        
        """
        self.id = node.id
        self.label = label
        self.setRect(QtCore.QRectF(node.p.x-node.width/2,
                                   -node.p.y/2,
                                   node.width,
                                   node.height))
    def boundingRect(self):
        """ boundingRect() -> QRectF
        Add a padded space to avoid un-updated area
        """
        return self.rect().adjusted(-2, -2, 2, 2)

    def paint(self, painter, option, widget=None):
        """ paint(painter: QPainter, option: QStyleOptionGraphicsItem,
                  widget: QWidget) -> None
        Peform actual painting of the version shape
        
        """
        if self.isSelected():
            painter.setPen(CurrentTheme.VERSION_SELECTED_PEN)
        else:
            painter.setPen(self.versionPen)
        painter.setBrush(self.versionBrush)
        painter.drawEllipse(self.rect())
        if self.isSelected() and not self.ghosted:
            painter.setPen(CurrentTheme.VERSION_LABEL_SELECTED_PEN)
        else:
            painter.setPen(self.versionLabelPen)
        painter.setFont(CurrentTheme.VERSION_FONT)
        painter.drawText(self.rect(), QtCore.Qt.AlignCenter, self.label)

    def itemChange(self, change, value):
        """ itemChange(change: GraphicsItemChange, value: QVariant) -> QVariant
        # Do not allow links to be selected with version
        
        """
        if ((change==QtGui.QGraphicsItem.ItemSelectedChange and value.toBool()) or
            (change==QtGui.QGraphicsItem.ItemSelectedChange and
             ((not value.toBool()) and
              len(self.scene().selectedItems()) == 1))):
            selectedItems = self.scene().selectedItems()
            selectedId = -1
            selectByClick = not self.scene().multiSelecting
            if value.toBool():
                for item in selectedItems:
                    if type(item)==QGraphicsLinkItem:
                        item.setSelected(False)
                        item.update()
                selectedItems = self.scene().selectedItems()
                if len(selectedItems)==0:
                    selectedId = self.id
            elif len(selectedItems)==2:
                if selectedItems[0]==self:
                    selectedId = selectedItems[1].id
                else:
                    selectedId = selectedItems[0].id
            selectByClick = self.scene().mouseGrabberItem() == self
            if not selectByClick:
                for item in self.scene().items():
                    if type(item)==QGraphicsRubberBandItem:
                        selectByClick = True
                        break
#             self.scene().emit(QtCore.SIGNAL('versionSelected(int,bool)'),
#                               selectedId, selectByClick)
            # Update the selected items list to include only versions and 
            # check if two versions selected
            selectedVersions = [item for item in 
                                self.scene().selectedItems() 
                                if type(item) == QGraphicsVersionItem]
            # If adding a version, the ids are self and other selected version
            if (len(selectedVersions) == 1 and value.toBool()): 
                self.scene().emit(QtCore.SIGNAL('twoVersionsSelected(int,int)'),
                                  selectedVersions[0].id, self.id)
            # If deleting a version, the ids are the two selected versions that
            # are not self
            if (len(selectedVersions) == 3 and not value.toBool()):
                if selectedVersions[0] == self:
                    self.scene().emit(QtCore.SIGNAL(
                            'twoVersionsSelected(int,int)'),
                                      selectedVersions[1].id, 
                                      selectedVersions[2].id)
                elif selectedVersions[1] == self:
                    self.scene().emit(QtCore.SIGNAL(
                            'twoVersionsSelected(int,int)'),
                                      selectedVersions[0].id, 
                                      selectedVersions[2].id)
                else:
                    self.scene().emit(QtCore.SIGNAL(
                            'twoVersionsSelected(int,int)'),
                                      selectedVersions[0].id, 
                                      selectedVersions[1].id)

        return QtGui.QGraphicsItem.itemChange(self, change, value)    

    def mousePressEvent(self, event):
        """ mousePressEvent(event: QMouseEvent) -> None
        Start dragging a version to someplaces...
        
        """
        if event.button()==QtCore.Qt.LeftButton:
            self.dragging = True
            self.dragPos = QtCore.QPoint(event.screenPos())
            self.scene().emit(QtCore.SIGNAL('versionSelected(int, bool)'),
                              self.id, True)
        return QtGui.QGraphicsEllipseItem.mousePressEvent(self, event)
        # super(QGraphicsVersionItem, self).mousePressEvent(event)
        
    def mouseMoveEvent(self, event):
        """ mouseMoveEvent(event: QMouseEvent) -> None        
        Now set the timer preparing for dragging. Must use a timer in
        junction with QDrag in order to avoid problem updates stall of
        QGraphicsView, especially on Linux
        
        """
        if (self.dragging and
            (event.screenPos()-self.dragPos).manhattanLength()>2):
            self.dragging = False
            #the timer has undesirable effects on Windows
            if systemType not in ['Windows', 'Microsoft']:
                self.dragTimer.start(1)
            else:
                self.startDrag()
        QtGui.QGraphicsEllipseItem.mouseMoveEvent(self, event)
        # super(QGraphicsVersionItem, self).mouseMoveEvent(event)

    def startDrag(self):
        """ startDrag() -> None
        Start the drag of QDrag
        
        """
        data = QtCore.QMimeData()
        data.versionId = self.id
        data.controller = self.scene().controller
        drag = QtGui.QDrag(self.scene().views()[0])
        drag.setMimeData(data)
        drag.setPixmap(CurrentTheme.VERSION_DRAG_PIXMAP)
        drag.start()

    def mouseReleaseEvent(self, event):
        """ mouseReleaseEvent(event: QMouseEvent) -> None
        Cancel the drag
        
        """
        self.dragging = False
        qt_super(QGraphicsVersionItem, self).mouseReleaseEvent(event)

    def dragEnterEvent(self, event):
        """ dragEnterEvent(event: QDragEnterEvent) -> None
        Capture version-to-version drag-and-drop
        
        """
        data = event.mimeData()
        if (hasattr(data, 'versionId') and
            hasattr(data, 'controller') and
            data.versionId!=self.id):
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        data = event.mimeData()
        if (hasattr(data, 'versionId') and hasattr(data, 'controller') and
            data.controller==self.scene().controller):
            event.accept()
            visDiff = QVisualDiff(self.scene().controller.vistrail,
                                  data.versionId,
                                  self.id,
                                  self.scene().controller,
                                  self.scene().views()[0])
            visDiff.show()
        else:
            event.ignore()  

    def perform_analogy(self):
        sender = self.scene().sender()
        analogy_name = str(sender.text())
        selectedItems = self.scene().selectedItems()
        controller = self.scene().controller
        for item in selectedItems:
            controller.perform_analogy(analogy_name, item.id, invalidate=False)
        controller.invalidate_version_tree()

    def contextMenuEvent(self, event):
        """contextMenuEvent(event: QGraphicsSceneContextMenuEvent) -> None
        Captures context menu event.

        """
        menu = QtGui.QMenu()
        #menu.addAction(self.addToBookmarksAct)
        controller = self.scene().controller
        if len(controller.analogy) > 0:
            analogies = QtGui.QMenu("Perform analogy...")
            for title in sorted(controller.analogy.keys()):
                act = QtGui.QAction(title, self.scene())
                analogies.addAction(act)
                QtCore.QObject.connect(act,
                                       QtCore.SIGNAL("triggered()"),
                                       self.perform_analogy)
            menu.addMenu(analogies)
        menu.exec_(event.screenPos())

    def createActions(self):
        """ createActions() -> None
        Create actions related to context menu 

        """
        self.addToBookmarksAct = QtGui.QAction("Add To Bookmarks", self.scene())
        self.addToBookmarksAct.setStatusTip("Add this pipeline to bookmarks")
#         QtCore.QObject.connect(self.addToBookmarksAct, 
#                                QtCore.SIGNAL("triggered()"),
#                                self.add_bookmark)

#     def add_bookmark(self):
#         """add_bookmark() -> None
#         Emit signal containing version info: tag and number 
        
#         """
#         modified = False
#         if self.scene().controller.changed:
#             modified = True
#             res = gui.utils.show_question("VisTrails",
#                                     "You need to save your file before\
#  adding a bookmark.\nDo you want to save your changes?",
#                                     [gui.utils.SAVE_BUTTON, 
#                                      gui.utils.CANCEL_BUTTON],
#                                     gui.utils.SAVE_BUTTON)
#             if res == gui.utils.SAVE_BUTTON:
#                 fileName = self.scene().controller.fileName
#                 self.scene().controller.writeVistrail(str(fileName))
#                 modified = False

#         if not modified:
#             self.scene().emit( QtCore.SIGNAL('addToBookmarks'), 
#                                self.id, self.label) 

class QVersionTreeScene(QInteractiveGraphicsScene):
    """
    QVersionTree inherits from QInteractiveGraphicsScene to keep track
    of the version scenes, i.e. versions, connections, etc.
    
    """

    def __init__(self, parent=None):
        """ QVersionTree(parent: QWidget) -> QVersionTree
        Initialize the graphics scene with no shapes
        
        """
        QInteractiveGraphicsScene.__init__(self, parent)
        self.setBackgroundBrush(CurrentTheme.VERSION_TREE_BACKGROUND_BRUSH)
        self.setSceneRect(QtCore.QRectF(-5000, -5000, 10000, 10000))
        self.versions = {}
        self.controller = None
        self.fullGraph = None

    def addVersion(self, node, label):
        """ addModule(node: DotNode) -> None
        Add a module to the scene
        
        """
        versionShape = QGraphicsVersionItem(None)
        versionShape.setupVersion(node, label)
        self.addItem(versionShape)
        self.versions[node.id] = versionShape

    def addLink(self, v1, v2):
        """ addLink(v1, v2: QGraphicsVersionItem) -> None
        Add a link to the scene
        
        """
        linkShape = QGraphicsLinkItem()
        linkShape.setupLink(v1, v2,
                            (self.fullGraph.parent(v1.id)==v2.id or
                             self.fullGraph.parent(v2.id)==v1.id))
        self.addItem(linkShape)
        
    def clear(self):
        """ clear() -> None
        Clear the whole scene
        
        """
        self.versions = {}
        self.clearItems()

    def adjustVersionColors(self, controller):
        """ adjustVersionColors(controller: VistrailController) -> None
        Based on the controller to set version colors
        
        """
        currentUser = controller.vistrail.getUser()
        thisNodes = {}
        otherNodes = {}
        for nodeId in sorted(self.versions.keys()):
            if nodeId!=0:
                nodeUser = controller.vistrail.actionMap[nodeId].user
                if nodeUser==currentUser:
                    thisNodes[nodeId] = len(thisNodes)
                else:
                    otherNodes[nodeId] = len(otherNodes)
        thisNorm = float(len(thisNodes))
        otherNorm = float(len(otherNodes))
    
        for (nodeId, item) in self.versions.items():
            ghosted = False
            if controller.search and nodeId!=0:
                action = controller.vistrail.actionMap[nodeId]
                ghosted = not controller.search.match(controller.vistrail, 
                                                      action)
            item.setGhosted(nodeId==0 or ghosted)
            if thisNodes.has_key(nodeId):
                item.setSaturation(True,
                                   float(thisNodes[nodeId]+1)/thisNorm)
            elif otherNodes.has_key(nodeId):
                item.setSaturation(False,
                                   float(otherNodes[nodeId]+1)/otherNorm)
            

    def setupScene(self, controller):
        """ setupScene(vistrail: VistrailController) -> None
        Construct the scene to view a version tree
        
        """
        # Clean the previous scene
        self.clear()
        
        self.controller = controller

        # Call dotty to perform graph layout
        (graph, self.fullGraph) = controller.refineGraph()
        layout = DotLayout()
        layout.layout_from(controller.vistrail, graph)

        # Put the layout to the graphics view
        for node in layout.nodes.itervalues():
            label = ''
            if controller.vistrail.tagMap.has_key(node.id):
                label = controller.vistrail.tagMap[node.id].name
            self.addVersion(node, label)
            if node.id==controller.currentVersion:
                self.versions[node.id].setSelected(True)
                
        self.adjustVersionColors(controller)
            
        # Add version links
        for nodeId in graph.vertices.keys():
            eFrom = graph.edges_from(nodeId)
            for (v1, v2) in eFrom:
                if self.versions.has_key(nodeId) and self.versions.has_key(v1):
                    self.addLink(self.versions[nodeId], self.versions[v1])
            
        # Update bounding rects and fit to all view
        self.updateSceneBoundingRect()

    def keyPressEvent(self, event):
        """ keyPressEvent(event: QKeyEvent) -> None
        Capture 'Del', 'Backspace' for pruning versions.
        
        """        
        selectedItems = self.selectedItems()
        if (self.controller and len(selectedItems)>0 and
            event.key() in [QtCore.Qt.Key_Backspace, QtCore.Qt.Key_Delete]):
            versions = [item.id for item in selectedItems]
            res = gui.utils.show_question("VisTrails",
                                          "Are you sure that you want to "
                                          "prune the selected version(s)?",
                                          [gui.utils.YES_BUTTON,
                                           gui.utils.NO_BUTTON],
                                          gui.utils.NO_BUTTON)
            if res == gui.utils.YES_BUTTON:
                self.controller.pruneVersions(versions)

    def mouseReleaseEvent(self, event):
        """ mouseReleaseEvent(event: QMouseEvent) -> None
        
        """
        if len(self.selectedItems()) != 1:
            self._pipeline_scene.clear()
        qt_super(QVersionTreeScene, self).mouseReleaseEvent(event)

class QVersionTreeView(QInteractiveGraphicsView):
    """
    QVersionTreeView inherits from QInteractiveGraphicsView that will
    handle drawing of versions layout output from Dotty
    
    """

    def __init__(self, parent=None):
        """ QVersionTreeView(parent: QWidget) -> QVersionTreeView
        Initialize the graphics view and its properties
        
        """
        QInteractiveGraphicsView.__init__(self, parent)
        self.setWindowTitle('Version Tree')
        self.setScene(QVersionTreeScene(self))

################################################################################


# if __name__=="__main__":
    
#     # Initialize the Vistrails Application and Theme
#     import sys
#     from gui import qt, theme
#     import vis_application
#     vis_application.start_application()
#     app = vis_application.VistrailsApplication
#     theme.initializeCurrentTheme()

#     # Get the vistrail
#     from core.xml_parser import XMLParser
#     parser = XMLParser()
#     parser.openVistrail('d:/hvo/vgc/src/vistrails/trunk/examples/lung.xml')
#     vistrail = parser.getVistrail()
    
#     # Now visually test QVersionTreeView
#     vt = QVersionTreeView(None)
#     vt.scene().setupScene(vistrail)
#     vt.show()
#     sys.exit(vis_application.VistrailsApplication.exec_())

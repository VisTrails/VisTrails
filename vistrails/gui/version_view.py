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
""" This is a QGraphicsView for pipeline view, it also holds different
types of graphics items that are only available in the pipeline
view. It only handles GUI-related actions, the rest of the
functionalities are implemented at somewhere else,
e.g. core.vistrails

QGraphicsLinkItem
QGraphicsVersionTextItem
QGraphicsVersionItem
QVersionTreeScene
QVersionTreeView
"""
from __future__ import division

from PyQt4 import QtCore, QtGui
from vistrails.core.configuration import get_vistrails_configuration
from vistrails.core import debug
from vistrails.core.system import systemType
from vistrails.core.thumbnails import ThumbnailCache
from vistrails.core.vistrail.controller import custom_color_key, \
    parse_custom_color
from vistrails.core.vistrail.vistrail import Vistrail
from vistrails.gui.base_view import BaseView
from vistrails.gui.graphics_view import (QInteractiveGraphicsScene,
                               QInteractiveGraphicsView,
                               QGraphicsItemInterface)
from vistrails.gui.qt import qt_super
from vistrails.gui.theme import CurrentTheme
from vistrails.gui.version_prop import QVersionPropOverlay
from vistrails.gui.collection.workspace import QParamExplorationEntityItem
import vistrails.gui.utils


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
        self.ghosted = False
        
        # cache link endpoints to improve performance on scene updates
        self.c1 = None
        self.c2 = None
        self.expand = None
        self.collapse = None

    def mousePressEvent(self, event):
        """ mousePressEvent(event: QMouseEvent) -> None

        """
        qt_super(QGraphicsLinkItem, self).mousePressEvent(event)
        self.setSelected(True)

    def mouseReleaseEvent(self, event):
        """ mouseReleaseEvent(event: QMouseEvent) -> None
        
        """
        qt_super(QGraphicsLinkItem, self).mouseReleaseEvent(event)
        if self.expand:
            self.scene().controller.expand_versions(self.startVersion, self.endVersion)
        elif self.collapse:
            self.scene().controller.collapse_versions(self.endVersion)
        self.setSelected(False)

    def setGhosted(self, ghosted):
        """ setGhosted(ghosted: True) -> None
        Set this link to be ghosted or not
        
        """
        if self.ghosted <> ghosted:
            self.ghosted = ghosted
            if ghosted:
                self.linkPen = CurrentTheme.GHOSTED_LINK_PEN
            else:
                self.linkPen = CurrentTheme.LINK_PEN

    def setupLink(self, v1, v2, expand=False, collapse=False):
        """ setupLink(v1, v2: QGraphicsVersionItem, compact: bool) -> None
        Setup a line connecting v1 and v2 items
        
        """
        self.startVersion = min(v1.id, v2.id)
        self.endVersion = max(v1.id, v2.id)
        
        c1 = v1.sceneBoundingRect().center()
        c2 = v2.sceneBoundingRect().center()

        # check if it is the same geometry 
        # improves performance on updates
        if self.c1 is not None and self.c2 is not None and \
                self.expand is not None and self.collapse !=None:
            isTheSame = self.c1 == c1 and \
                self.c2 == c2 and \
                self.expand == expand and \
                self.collapse == collapse
            if isTheSame:
                return
        
        # update current state
        self.c1 = c1
        self.c2 = c2
        self.collapse = collapse
        self.expand = expand

        # Compute the line of the link and its normal line throught
        # the midpoint
        mainLine = QtCore.QLineF(c1, c2)
        normalLine = mainLine.normalVector()        
        normalLine.setLength(CurrentTheme.LINK_SEGMENT_LENGTH)
        dis = (mainLine.pointAt(0.5)-mainLine.p1()+
               normalLine.p1()-normalLine.pointAt(0.5))
        normalLine.translate(dis.x(), dis.y())

        # Generate 2 segments along the main line and 3 segments along
        # the normal line
        if not self.collapse and not self.expand:
            self.lines = [mainLine]
            poly = QtGui.QPolygonF()
            poly.append(self.lines[0].p1())
            poly.append(self.lines[0].p2())
            poly.append(self.lines[0].p1())
            self.setPolygon(poly)
        else:
            self.lines = []
            
            normalLine = mainLine.normalVector()        
            normalLine.setLength(CurrentTheme.LINK_SEGMENT_SQUARE_LENGTH)
            dis = (mainLine.pointAt(0.5)-mainLine.p1()+
                   normalLine.p1()-normalLine.pointAt(0.5))
            normalLine.translate(dis.x(), dis.y())
            
            gapLine = QtCore.QLineF(mainLine)
            gapLine.setLength(CurrentTheme.LINK_SEGMENT_SQUARE_LENGTH/2)
            gapVector = gapLine.p2()-gapLine.p1()
            
            # First segment along the main line
            line = QtCore.QLineF(mainLine)
            line.setLength(line.length()/2-CurrentTheme.LINK_SEGMENT_SQUARE_LENGTH/2)
            self.lines.append(QtCore.QLineF(line))
            
            # Second segment along the main line
            line.translate(line.p2()-line.p1()+gapVector*2)
            self.lines.append(QtCore.QLineF(line))
            
            # First normal segment in front
            line_t = QtCore.QLineF(normalLine)
            line_t.translate(gapVector*(-1.0))
            self.lines.append(QtCore.QLineF(line_t))
        
            # Second normal segment in back
            line_b = QtCore.QLineF(normalLine)
            line_b.translate(gapVector)
            self.lines.append(QtCore.QLineF(line_b))
        
            # Left box
            line = QtCore.QLineF(line_t.p1(),line_b.p1())
            self.lines.append(QtCore.QLineF(line))
        
            # Right box
            line = QtCore.QLineF(line_t.p2(),line_b.p2())
            self.lines.append(QtCore.QLineF(line))

            # Horizontal plus
            line_h = QtCore.QLineF(normalLine.pointAt(0.2),normalLine.pointAt(0.8))
            self.lines.append(QtCore.QLineF(line_h))
            
            if self.expand:
                # Vertical plus
                line = QtCore.QLineF(mainLine)
                line.translate((line.p2()-line.p1())/2-gapVector)
                line.setLength(CurrentTheme.LINK_SEGMENT_SQUARE_LENGTH)
                line_v = QtCore.QLineF(line.pointAt(0.2), line.pointAt(0.8))
                self.lines.append(QtCore.QLineF(line_v))
        
            # Create the poly line for selection and redraw
            poly = QtGui.QPolygonF()
            poly.append(self.lines[0].p1())
            poly.append(self.lines[2].p1())
            poly.append(self.lines[3].p1())
            poly.append(self.lines[1].p2())
            poly.append(self.lines[3].p2())
            poly.append(self.lines[2].p2())
            poly.append(self.lines[0].p1())
            self.setPolygon(poly)

        self.setGhosted(v1.ghosted and v2.ghosted)

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
        """ itemChange(change: GraphicsItemChange, value: variant) -> variant
        Do not allow link to be selected with version shape
        
        """
        if change==QtGui.QGraphicsItem.ItemSelectedChange and value:
            return False
        return QtGui.QGraphicsPolygonItem.itemChange(self, change, value)


##############################################################################
# QGraphicsVerstionTextItem

class QGraphicsVersionTextItem(QGraphicsItemInterface, QtGui.QGraphicsTextItem):
    """
    QGraphicsVersionTextItem is an editable text item that appears on top of
    a QGraphicsVersionItem to allow the tag to be changed

    """
    def __init__(self, parent=None, scene=None):
        """ QGraphicsVersionTextItem(parent: QGraphicsVersionItem, 
        scene: QGraphicsScene) -> QGraphicsVersionTextItem

        Create the shape, intialize its drawing style

        """
        QtGui.QGraphicsTextItem.__init__(self, parent, scene)
        self.timer = None
        self.isEditable = None
        self.setEditable(False)
        self.setFont(CurrentTheme.VERSION_FONT)
        self.setTextWidth(CurrentTheme.VERSION_LABEL_MARGIN[0])
        self.setDefaultTextColor(CurrentTheme.VERSION_LABEL_COLOR)
        self.centerX = 0.0
        self.centerY = 0.0
        self.label = ''
        self.isTag = True
        self.updatingTag = False

    def setEditable(self, editable=True):
        if self.timer:
            self.timer.stop()
            self.timer = None
        if editable == self.isEditable:
            return
        self.isEditable = editable
        if editable:
            self.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)
        else:
            if self.textCursor():
                c = self.textCursor()
                c.clearSelection()
                self.setTextCursor(c)
            self.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)

    def setEditableLater(self):
        self.timer = QtCore.QTimer(self)
        self.timer.setSingleShot(True)
        self.connect(self.timer, QtCore.SIGNAL("timeout()"), self.setEditable)
        self.timer.start(QtGui.QApplication.doubleClickInterval() + 5)

    def setGhosted(self, ghosted):
        if ghosted:
            self.setDefaultTextColor(CurrentTheme.GHOSTED_VERSION_LABEL_COLOR)
        else:
            self.setDefaultTextColor(CurrentTheme.VERSION_LABEL_COLOR)

    def changed(self, x, y, label, tag=True):
        """ changed(x: float, y: float, label: str) -> None
        Change the position and text label from outside the editor

        """
        if self.centerX <> x or self.centerY <> y or self.label <> label:
            self.centerX = x
            self.centerY = y
            self.label = label
            self.isTag = tag
            if self.isTag:
                self.setFont(CurrentTheme.VERSION_FONT)
            else:
                self.setFont(CurrentTheme.VERSION_DESCRIPTION_FONT)
            self.reset()

    def reset(self):
        """ reset() -> None
        Resets the text label, width, and positions to the stored values

        """
        self.setPlainText(self.label)
        self.setEditable(False)
        if (len(str(self.label)) > 0):
            self.setTextWidth(-1)
        else:
            self.setTextWidth(CurrentTheme.VERSION_LABEL_MARGIN[0])
            
        if self.isTag:
            self.setFont(CurrentTheme.VERSION_FONT)
        else:
            self.setFont(CurrentTheme.VERSION_DESCRIPTION_FONT)  
        self.updatePos()
        self.parentItem().updateWidthFromLabel()

    def updatePos(self):
        """ updatePos() -> None
        Center the text, by default it uses the upper left corner
        
        """
        self.setPos(self.centerX-self.boundingRect().width()/2.0,
                    self.centerY-self.boundingRect().height()/2.0)

    def keyPressEvent(self, event):
        """ keyPressEvent(event: QEvent) -> None
        Enter and Return keys signal a change in the label.  Other keys
        update the position and size of the parent ellipse during key entry.

        """
        if event.key() in [QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return]:
            self.updatingTag = True
            if (self.label == str(self.toPlainText()) or
                not self.scene().controller.update_current_tag(str(self.toPlainText()))):
                self.reset()
            self.updatingTag = False
            event.ignore()
            self.clearFocus()
            return
        qt_super(QGraphicsVersionTextItem, self).keyPressEvent(event)
        if (len(str(self.toPlainText())) > 0):
            self.setTextWidth(-1)
        self.updatePos()
        self.parentItem().updateWidthFromLabel()

    def focusOutEvent(self, event):
        """ focusOutEvent(event: QEvent) -> None
        Update the tag if the text has changed

        """
        qt_super(QGraphicsVersionTextItem, self).focusOutEvent(event)
        if not self.updatingTag and self.label != self.toPlainText():
            self.updatingTag = True
            if (self.label == str(self.toPlainText()) or 
                not self.scene().controller.update_current_tag(str(self.toPlainText()))):
                self.reset()
            self.updatingTag = False

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
        self.setFlags(QtGui.QGraphicsItem.ItemIsSelectable)
        self._versionPenNormal = CurrentTheme.VERSION_PEN
        self._versionPen = CurrentTheme.VERSION_PEN
        self._versionBrush = CurrentTheme.VERSION_USER_BRUSH
        self.id = -1
        self.label = ''
        self.descriptionLabel = ''
        self.dragging = False
        self.ghosted = False
        self.updatePainterState()

        # self.rank is a positive number that determines the
        # saturation of the node. Two version nodes might have the
        # same rank if they were created by different users
        # self.max_rank is the maximum rank for that version class
        self.rank = -1
        self.max_rank = -1
        
        # Editable text item that remains hidden unless the version is selected
        self.text = QGraphicsVersionTextItem(self)

        # Need a timer to start a drag to avoid stalls on QGraphicsView
        self.dragTimer = QtCore.QTimer()
        self.dragTimer.setSingleShot(True)
        self.dragTimer.connect(self.dragTimer,
                               QtCore.SIGNAL('timeout()'),
                               self.startDrag)

        self.dragPos = QtCore.QPoint()

    def _get_versionPen(self):
        return self._versionPen
    def _set_versionPen(self, pen):
        self._versionPen = pen
        self.updatePainterState()
    versionPen = property(_get_versionPen, _set_versionPen)

    def _get_versionBrush(self):
        return self._versionBrush
    def _set_versionBrush(self, brush):
        self._versionBrush = brush
        self.updatePainterState()
    versionBrush = property(_get_versionBrush, _set_versionBrush)

    def itemChange(self, change, value):
        if change == QtGui.QGraphicsItem.ItemSelectedHasChanged:
            if self.isSelected():
                self.versionPen = CurrentTheme.VERSION_SELECTED_PEN
                self.text.setEditableLater()
            else:
                self.versionPen = self._versionPenNormal
                self.text.setEditable(False)
            self.updatePainterState()
        return QtGui.QGraphicsItem.itemChange(self, change, value)

    def setGhosted(self, ghosted=True):
        """ setGhosted(ghosted: True) -> None
        Set this version to be ghosted or not
        
        """
        if self.ghosted <> ghosted:
            self.ghosted = ghosted
            self.text.setGhosted(ghosted)
            if ghosted:
                self._versionPenNormal = CurrentTheme.GHOSTED_VERSION_PEN
                self._versionBrush = CurrentTheme.GHOSTED_VERSION_USER_BRUSH
            else:
                self._versionPenNormal = CurrentTheme.VERSION_PEN
                self._versionBrush = CurrentTheme.VERSION_USER_BRUSH
            if not self.isSelected():
                self._versionPen = self._versionPenNormal
            self.updatePainterState()

    def update_color(self, isThisUs, new_rank, new_max_rank, new_ghosted,
                     new_customcolor):
        """ update_color(isThisUs: bool,
                         new_rank, new_max_rank: int) -> None

        If necessary, update the colors of this version node based on
        who owns the node and new ranks

        NOTE: if username changes during execution, this might break.
        """
        if (new_rank == self.rank and new_max_rank == self.max_rank and
            new_ghosted == self.ghosted and
            new_customcolor == self.custom_color):
            # nothing changed
            return
        self.setGhosted(new_ghosted)
        self.custom_color = new_customcolor
        self.rank = new_rank
        self.max_rank = new_max_rank
        if not self.ghosted:
            if self.custom_color is not None:
                configuration = get_vistrails_configuration()
                sat_from_rank = not configuration.check(
                        'fixedCustomVersionColorSaturation')
                brush = QtGui.QBrush(QtGui.QColor.fromRgb(*self.custom_color))
            else:
                if isThisUs:
                    brush = CurrentTheme.VERSION_USER_BRUSH
                else:
                    brush = CurrentTheme.VERSION_OTHER_BRUSH
                sat_from_rank = True
            if sat_from_rank:
                sat = float(new_rank+1) / new_max_rank
                (h, s, v, a) = brush.color().getHsvF()
                newHsv = (h, s*sat, v+(1.0-v)*(1-sat), a)
                brush = QtGui.QBrush(brush)
                brush.setColor(QtGui.QColor.fromHsvF(*newHsv))
            self.versionBrush = brush
        self.update()

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
    
    def updateWidthFromLabel(self):
        """ updateWidthFromLabel() -> None
        Change the width of the ellipse based on a temporary change in the label

        """
        prevWidth = self.rect().width()
        width = self.text.boundingRect().width() + \
            CurrentTheme.VERSION_LABEL_MARGIN[0] - 4
        r = self.rect()
        r.setX(r.x()+(prevWidth-width)/2.0)
        r.setWidth(width)
        self.setRect(r)
        self.update()

    def setupVersion(self, node, action, tag, description):
        """ setupPort(node: DotNode,
                      action: DBAction,
                      tag: str,
                      description: str) -> None
        Update the version dimensions and id
        
        """
        # Lauro:
        # what was this hacking??? the coordinates inside
        # the input "node" should come to this point ready. This is
        # not the point to do layout calculations (e.g. -node.p.y/2)

        # Carlos:
        # This is not layout as much as dealing with the way Qt
        # specifies rectangles. Besides, moving this back here reduces
        # code duplication, and allows customized behavior for
        # subclasses.

        rect = QtCore.QRectF(node.p.x-node.width/2.0,
                             node.p.y-node.height/2.0,
                             node.width,
                             node.height)
        validLabel = True
        if tag is None:
            label = ''
            validLabel=False
        else:
            label = tag

        self.id = node.id
        self.label = label
        if description is None:
            self.descriptionLabel = ''
        else:
            self.descriptionLabel = description
        if validLabel:
            textToDraw=self.label
        else:
            textToDraw=self.descriptionLabel

        if (ThumbnailCache.getInstance().conf.mouseHover and
            action and action.thumbnail is not None):
            fname = ThumbnailCache.getInstance().get_abs_name_entry(action.thumbnail)
            self.setToolTip('<img src="%s" height="128" border="1"/>'%fname)
        else:
            self.setToolTip('')    
        self.text.changed(node.p.x, node.p.y, textToDraw, validLabel)
        self.setRect(rect)

    def boundingRect(self):
        """ boundingRect() -> QRectF
        Add a padded space to avoid un-updated area
        """
        return self.rect().adjusted(-2, -2, 2, 2)

    def paint(self, painter, option, widget=None):
        option.state &= ~QtGui.QStyle.State_Selected
        QtGui.QGraphicsEllipseItem.paint(self, painter, option, widget)

    def updatePainterState(self):
        self.setPen(self._versionPen)
        self.setBrush(self._versionBrush)

    def mousePressEvent(self, event):
        """ mousePressEvent(event: QMouseEvent) -> None
        Start dragging a version to someplaces...
        
        """
        if event.button()==QtCore.Qt.LeftButton:
            self.dragging = True
            self.dragPos = QtCore.QPoint(event.screenPos())
        return QtGui.QGraphicsEllipseItem.mousePressEvent(self, event)
        
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
        QtGui.QGraphicsEllipseItem.mouseReleaseEvent(self, event)

    def dragEnterEvent(self, event):
        """ dragEnterEvent(event: QDragEnterEvent) -> None
        Capture version-to-version drag-and-drop
        Also capture parameter exploration assignment
        """
        data = event.mimeData()
        if (hasattr(data, 'versionId') and
            hasattr(data, 'controller') and
            data.versionId!=self.id) or \
           (hasattr(data, 'items') and 
            len(data.items) == 1 and
            isinstance(data.items[0], QParamExplorationEntityItem)):
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        data = event.mimeData()
        if (hasattr(data, 'versionId') and hasattr(data, 'controller') and
            data.controller==self.scene().controller):
            event.accept()
            self.scene().emit(QtCore.SIGNAL('diffRequested(int,int)'),
                              data.versionId, self.id)
            # visDiff = QVisualDiff(self.scene().controller.vistrail,
            #                       data.versionId,
            #                       self.id,
            #                       self.scene().controller,
            #                       self.scene().views()[0])
            # visDiff.show()
        elif (hasattr(data, 'items') and 
              len(data.items) == 1 and
              isinstance(data.items[0], QParamExplorationEntityItem)):
            # apply this parameter exploration to the new version, validate it and switch to PE view
            from vistrails.gui.vistrails_window import _app
            view = _app.get_current_view()
            view.apply_parameter_exploration(self.id, data.items[0].entity.pe)
            event.accept()
        else:
            event.ignore()  

    def perform_analogy(self):
        sender = self.scene().sender()
        analogy_name = str(sender.text())
        # selectedItems = self.scene().selectedItems()
        controller = self.scene().controller
        print "calling perform analogy", analogy_name, self.id
        # for item in selectedItems:
        controller.perform_analogy(analogy_name, self.id)

    def show_raw_pipeline(self):
        self.scene().emit_selection = False
        for item in self.scene().selectedItems():
            item.setSelected(False)
        self.setSelected(True)
        self.scene().emit_selection = True
        self.scene().emit(
            QtCore.SIGNAL('versionSelected(int,bool,bool,bool,bool)'),
            self.id, True, False, True, True)
            
    def construct_from_root(self):
        self.scene().emit_selection = False
        for item in self.scene().selectedItems():
            item.setSelected(False)
        self.setSelected(True)
        self.scene().emit_selection = True
        self.scene().emit(
            QtCore.SIGNAL('versionSelected(int,bool,bool,bool,bool)'),
            self.id, True, True, True, True)

    def contextMenuEvent(self, event):
        """contextMenuEvent(event: QGraphicsSceneContextMenuEvent) -> None
        Captures context menu event.

        """
        controller = self.scene().controller
        menu = QtGui.QMenu()
        raw_action = QtGui.QAction("Display raw pipeline", self.scene())
        from_root_action = QtGui.QAction("Construct from root", self.scene())
        QtCore.QObject.connect(raw_action,
                               QtCore.SIGNAL("triggered()"),
                               self.show_raw_pipeline)
        QtCore.QObject.connect(from_root_action,
                               QtCore.SIGNAL("triggered()"),
                               self.construct_from_root)
        menu.addAction(raw_action)
        menu.addAction(from_root_action)
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

    def mouseDoubleClickEvent(self, event):
        # QtGui.QGraphicsEllipseItem.mouseDoubleClickEvent(self, event)
        event.accept()
        self.scene().double_click(self.id)


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
        self.versions = {}  # id -> version gui object
        self.edges = {}     # (sourceVersion, targetVersion) -> edge gui object
        self.controller = None
        self.fullGraph = None
        self.emit_selection = True
        self.select_by_click = True
        self.connect(self, QtCore.SIGNAL("selectionChanged()"),
                     self.selectionChanged)

    def addVersion(self, node, action, tag, description):
        """ addModule(node, action: DBAction, tag: str, description: str,
                custom_color: (int, int, int))
                -> None
        Add a module to the scene.

        """
        versionShape = QGraphicsVersionItem(None)
        versionShape.setupVersion(node, action, tag, description)
        self.addItem(versionShape)
        self.versions[node.id] = versionShape

    def removeVersion(self, v):
        """ addLink(v: integer) -> None
        Remove version from scene and mapping
        
        """
        versionShape = self.versions[v]
        self.removeItem(versionShape)
        self.versions.pop(v)

    def addLink(self, guiSource, guiTarget, expand, collapse):
        """ addLink(v1, v2: QGraphicsVersionItem) -> None
        Add a link to the scene
        
        """
        linkShape = QGraphicsLinkItem()
        linkShape.setupLink(guiSource, guiTarget, expand, collapse)
        self.addItem(linkShape)
        self.edges[(guiSource.id, guiTarget.id)] = linkShape
        
    def removeLink(self, source, target):
        """ removeLink(v1, v2: integers) -> None
        Remove link from scene and mapping
        
        """
        linkShape = self.edges[(source,target)]
        self.removeItem(linkShape)
        self.edges.pop((source, target))

    def clear(self):
        """ clear() -> None
        Clear the whole scene
        
        """
        self.versions = {}
        self.clearItems()

    def adjust_version_colors(self, controller):
        """ adjust_version_colors(controller: VistrailController) -> None
        Based on the controller to set version colors
        
        """
        currentUser = controller.vistrail.getUser()
        ranks = {}
        ourMaxRank = 0
        otherMaxRank = 0
        am = controller.vistrail.actionMap
        for nodeId in sorted(self.versions.keys()):
            if nodeId!=0:
                nodeUser = am[nodeId].user
                if nodeUser==currentUser:
                    ranks[nodeId] = ourMaxRank
                    ourMaxRank += 1
                else:
                    ranks[nodeId] = otherMaxRank
                    otherMaxRank += 1
        for (nodeId, item) in self.versions.iteritems():
            if nodeId == 0:
                item.setGhosted(True)
                continue
            nodeUser = am[nodeId].user
            if controller.search and nodeId!=0:
                action = am[nodeId]
                if getattr(get_vistrails_configuration(), 'hideUpgrades',
                           True):
                    # Use upgraded version to match
                    action = am[controller.vistrail.get_upgrade(nodeId, False)]
                ghosted = not controller.search.match(controller, action)
            else:
                ghosted = False
                
            #item.setGhosted(ghosted) # we won't set it now so we can check if
                                      # the state changed in update_color
            if nodeUser==currentUser:
                max_rank = ourMaxRank
            else:
                max_rank = otherMaxRank
#             max_rank = ourMaxRank if nodeUser==currentUser else otherMaxRank
            configuration = get_vistrails_configuration()
            if configuration.check('customVersionColors'):
                custom_color = controller.vistrail.get_action_annotation(
                    nodeId,
                    custom_color_key)
                if custom_color is not None:
                    try:
                        custom_color = parse_custom_color(custom_color.value)
                    except ValueError, e:
                        debug.warning("Version %r has invalid color annotation "
                                      "(%s)" % (nodeId, e))
                        custom_color = None
            else:
                custom_color = None
            ####
            item.update_color(nodeUser==currentUser,
                              ranks[nodeId],
                              max_rank, ghosted, custom_color)
        for (version_from, version_to), link in self.edges.iteritems():
            if self.versions[version_from].ghosted and \
                    self.versions[version_to].ghosted:
                link.setGhosted(True)
            else:
                link.setGhosted(False)

    def update_scene_single_node_change(self, controller, old_version, new_version):
        """ update_scene_single_node_change(controller: VistrailController,
        old_version, new_version: int) -> None

        Faster alternative to setup_scene when a single version is
        changed. When this is called, we know that both old_version
        and new_version don't have tags associated, so no layout
        changes happen
    
        """
        # self.setupScene(controller)

        # we need to call this every time because version ranks might
        # change
        self.adjust_version_colors(controller)

        # update version item
        v = self.versions[old_version]
        old_desc = controller.vistrail.get_description(old_version)
        new_desc = controller.vistrail.get_description(new_version)
        if old_desc != new_desc:
            v.descriptionLabel = new_desc
            v.text.changed(v.text.centerX, v.text.centerY, new_desc, False)
            v.updateWidthFromLabel()
        self.versions[new_version] = v
        del self.versions[old_version]
        v.id = new_version

        # update link items
        dst = controller._current_terse_graph.edges_from(new_version)
        for eto, (expand, collapse) in dst:
            edge = self.edges[(old_version, eto)]
            edge.setupLink(self.versions[new_version],
                           self.versions[eto],
                           expand,
                           False) # We shouldn't ever need a collapse here
            self.edges[(new_version, eto)] = edge
            del self.edges[(old_version, eto)]

        src = controller._current_terse_graph.edges_to(new_version)
        for efrom, (expand, collapse) in src:
            edge = self.edges[(efrom, old_version)]
            edge.setupLink(self.versions[efrom],
                           self.versions[new_version],
                           expand,
                           False) # We shouldn't ever need a collapse here
            self.edges[(efrom, new_version)] = edge
            del self.edges[(efrom, old_version)]

    def setupScene(self, controller, select_node=True):
        """ setupScene(controller: VistrailController) -> None
        Construct the scene to view a version tree
        
        """
        self.select_by_click = False        
        self.controller = controller

        # perform graph layout
        (tree, self.fullGraph, layout) = controller.refine_graph()

        # compute nodes that should be removed
        # O(n  * (hashmap query key time)) on 
        # where n is the number of current 
        # nodes in the scene
        removeNodeSet = set(i for i in self.versions
                            if not i in tree.vertices)

        # compute edges to be removed
        # O(n * (hashmap query key time)) 
        # where n is the number of current 
        # edges in the scene
        removeEdgeSet = set((s, t) for (s, t) in self.edges
                            if (s in removeNodeSet or
                                t in removeNodeSet or
                                not tree.has_edge(s, t)))

        # loop on the nodes of the tree
        vistrail = controller.vistrail
        am = vistrail.actionMap
        last_n = vistrail.getLastActions(controller.num_versions_always_shown)

        self.emit_selection = False
        for node in layout.nodes.itervalues():
            # version id
            v = node.id

            # version tag
            tag = tree.vertices.get(v, None)
            action = am.get(v, None)
            description = vistrail.get_description(v)

            # if the version gui object already exists...
            if v in self.versions:
                versionShape = self.versions[v]
                versionShape.setupVersion(node, action, tag, description)
            else:
                self.addVersion(node, action, tag, description)
            if select_node:
                self.versions[v].setSelected(v == controller.current_base_version)

        self.emit_selection = True
        self.selectionChanged()

        # remove gui edges from scene
        for (v1, v2) in removeEdgeSet:
            self.removeLink(v1,v2)

        # remove gui nodes from scene
        for v in removeNodeSet:
            self.removeVersion(v)

        # adjust the colors
        self.adjust_version_colors(controller)

        # Add or update links
        for source, source_tag in tree.vertices.iteritems():
            eFrom = tree.edges_from(source)
            for target, (expand, collapse) in eFrom:
                guiSource = self.versions[source]
                guiTarget = self.versions[target]
                if self.edges.has_key((source,target)):
                    linkShape = self.edges[(source,target)]
                    linkShape.setupLink(guiSource, guiTarget,
                                        expand, collapse)
                else:
                    self.addLink(guiSource, guiTarget, 
                                 expand, collapse)

        # Update bounding rects and fit to all view
        self.updateSceneBoundingRect()

        self.select_by_click = True

    def keyPressEvent(self, event):
        """ keyPressEvent(event: QKeyEvent) -> None
        Capture 'Del', 'Backspace' for pruning versions when not editing a tag
       
        """        
        selectedItems = self.selectedItems()
        versions = [item.id for item in selectedItems 
                    if isinstance(item, QGraphicsVersionItem)
                    and not item.text.hasFocus()] 
        if (self.controller and len(versions)>0 and
            event.key() in [QtCore.Qt.Key_Backspace, QtCore.Qt.Key_Delete]):
            event.accept()
            versions = [item.id for item in selectedItems]
            res = vistrails.gui.utils.show_question("VisTrails",
                                           "Are you sure that you want to "
                                           "prune the selected version(s)?",
                                           [vistrails.gui.utils.YES_BUTTON,
                                            vistrails.gui.utils.NO_BUTTON],
                                           vistrails.gui.utils.NO_BUTTON)
            if res == vistrails.gui.utils.YES_BUTTON:
                self.controller.prune_versions(versions)
        else:
            qt_super(QVersionTreeScene, self).keyPressEvent(event)

    def selectionChanged(self):
        if not self.emit_selection:
            return

        selected_items = self.selectedItems()
        if len(selected_items) == 1:
            # emit versionSelected selected_id
            self.emit(QtCore.SIGNAL('versionSelected(int,bool,bool,bool,bool)'),
                      selected_items[0].id, self.select_by_click, 
                      True, False, False)
        else:
            # emit versionSelected -1
            for item in selected_items:
                if item.text.isEditable:
                    item.text.setEditable(False)
            self.emit(QtCore.SIGNAL('versionSelected(int,bool,bool,bool,bool)'),
                      -1, self.select_by_click, True, False, False)

        if len(selected_items) == 2:
            self.emit(
                QtCore.SIGNAL('twoVersionsSelected(int, int)'),
                selected_items[0].id, selected_items[1].id)

    def double_click(self, version_id):
        self.mouseGrabberItem().ungrabMouse()
        self.emit(QtCore.SIGNAL('versionSelected(int,bool,bool,bool,bool)'),
                  version_id, self.select_by_click, True, False, True)

class QVersionTreeView(QInteractiveGraphicsView, BaseView):
    """
    QVersionTreeView inherits from QInteractiveGraphicsView that will
    handle drawing of versions layout output from Dotty
    
    """

    def __init__(self, parent=None):
        """ QVersionTreeView(parent: QWidget) -> QVersionTreeView
        Initialize the graphics view and its properties
        
        """
        QInteractiveGraphicsView.__init__(self, parent)
        BaseView.__init__(self)
        self.controller = None
        self.set_title('Version Tree')
        self.setScene(QVersionTreeScene(self))
        self.versionProp = QVersionPropOverlay(self, self.viewport())
        self.versionProp.hide()

    def set_default_layout(self):
        from vistrails.gui.collection.workspace import QWorkspaceWindow
        from vistrails.gui.version_prop import QVersionProp
        self.set_palette_layout(
            {QtCore.Qt.LeftDockWidgetArea: QWorkspaceWindow,
             QtCore.Qt.RightDockWidgetArea: QVersionProp,
             })
            
    def set_action_links(self):
        self.action_links = \
            {
             'publishWeb' : ('version_changed', self.check_publish_db),
             'publishPaper': ('version_changed', self.check_publish),
             'redo': ('version_changed', self.can_redo),
             'undo': ('version_changed', self.can_undo),
             'execute': ('pipeline_changed', self.can_execute)
            }
        
    def set_action_defaults(self):
        self.action_defaults['execute'] = \
            [('setEnabled', True, self.set_action_execute_default)]

    def set_action_execute_default(self):
        if self.controller:
            if self.controller.current_pipeline:
                return len(self.controller.current_pipeline.modules) > 0
        return False
    
    def check_publish_db(self, versionId):
        loc = self.controller.locator
        result = False
        if hasattr(loc,'host'):
            result = True    
        return result and self.check_publish(versionId)
    
    def check_publish(self, versionId):
        return versionId > 0 

    def can_redo(self, versionId):
        return self.controller and self.controller.can_redo()

    def can_undo(self, versionId):
        return self.controller and self.controller.can_undo()
    
    def can_execute(self, pipeline):
        return pipeline is not None and len(pipeline.modules) > 0
    
    def execute(self):
        res = self.controller.execute_user_workflow()
        from vistrails.gui.vistrails_window import _app
        if len(res[0][0].errors) > 0:
            _app.qactions['pipeline'].trigger()
        _app.notify('execution_updated')
        
    def publish_to_web(self):
        from vistrails.gui.publishing import QVersionEmbed
        panel = QVersionEmbed.instance()
        panel.switchType('Wiki')
        panel.set_visible(True)
        
    def publish_to_paper(self):
        from vistrails.gui.publishing import QVersionEmbed
        panel = QVersionEmbed.instance()
        panel.switchType('Latex')
        panel.set_visible(True)
        
    def selectModules(self):
        """ selectModules() -> None
        Overrides parent class to disable text items if you click on background

        """
        if self.canSelectRectangle:
            br = self.selectionBox.sceneBoundingRect()
        else:
            br = QtCore.QRectF(self.startSelectingPos,
                               self.startSelectingPos)
        items = self.scene().items(br)
        if len(items)==0 or items==[self.selectionBox]:
            for item in self.scene().selectedItems():
                if isinstance(item, QGraphicsVersionItem):
                    item.text.clearFocus()
        qt_super(QVersionTreeView, self).selectModules()
                
    def set_title(self, title):
        BaseView.set_title(self, title)
        self.setWindowTitle(title)

    def set_controller(self, controller):
        oldController = self.controller
        if oldController != controller:
            if oldController is not None:
                self.disconnect(oldController,
                                QtCore.SIGNAL('vistrailChanged()'),
                                self.vistrailChanged)
                self.disconnect(oldController,
                                QtCore.SIGNAL('invalidateSingleNodeInVersionTree'),
                                self.single_node_changed)
                self.disconnect(oldController,
                                QtCore.SIGNAL('notesChanged()'),
                                self.notesChanged)
            self.controller = controller
            self.scene().controller = controller
            self.connect(controller,
                         QtCore.SIGNAL('vistrailChanged()'),
                         self.vistrailChanged)
            self.connect(controller,
                         QtCore.SIGNAL('invalidateSingleNodeInVersionTree'),
                         self.single_node_changed)
            self.connect(controller,
                         QtCore.SIGNAL("notesChanged()"),
                         self.notesChanged)
            if controller:
                self.versionProp.updateController(controller)
                self.scene().setupScene(controller)
                # self.vistrailChanged()
                # self.versionProp.updateController(controller)
                # self.versionView.versionProp.updateController(controller)

    def vistrailChanged(self):
        """ vistrailChanged() -> None
        An action was performed on the current vistrail
        
        """
        from vistrails.gui.vistrails_window import _app
        select_node = True
        if _app._previous_view and _app._previous_view.window() != self.window():
            select_node = False
        self.scene().setupScene(self.controller, select_node)
        if self.controller and self.controller.reset_version_view:
            self.scene().fitToAllViews()
        if self.controller:
            # self.versionProp.updateVersion(self.controller.current_version)
            self.versionProp.updateVersion(self.controller.current_version)
        self.emit(QtCore.SIGNAL("vistrailChanged()"))

    def single_node_changed(self, old_version, new_version):
        """ single_node_changed(old_version, new_version)
        Handle single node change on version tree by not recomputing
        entire scene.

        """
        self.scene().update_scene_single_node_change(self.controller,
                                                     old_version,
                                                     new_version)
        if self.controller and self.controller.reset_version_view:
            self.scene().fitToAllViews()
        if self.controller:
            # self.versionProp.updateVersion(self.controller.current_version)
            self.versionProp.updateVersion(self.controller.current_version)
        self.emit(QtCore.SIGNAL("vistrailChanged()"))

    def notesChanged(self):
        """ notesChanged() -> None
        The notes for the current vistrail version changed

        """
        if self.controller:
            self.versionProp.updateVersion(self.controller.current_version)

    def select_current_version(self):
        self.scene().setupScene(self.controller)

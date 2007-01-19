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
"""
This module describes a theme structure for VisTrails GUI. It
specifies colors, background images and other measurements
"""

from PyQt4 import QtCore, QtGui
from core.utils.color import ColorByName, ColorManipulator
import core.system
################################################################################

class DefaultTheme(object):
    """
    This is the default theme which contains color, images,
    measurements, etc. for Vistrail. Other themes should derive from
    this class and change appropriate values
    
    """
    ######################
    #### MEASUREMENTS ####

    # Padded space of Module shape into its label
    MODULE_LABEL_MARGIN = (20, 20, 20, 15)
    
    # Margin of Module shape into its ports
    MODULE_PORT_MARGIN = (5, 5, 5, 5)
    
    # Space between ports inside a module
    MODULE_PORT_SPACE = 5
    
    # The space added to the end of port shapes before it reaches the
    # margin of the module
    MODULE_PORT_PADDED_SPACE = 20
    
    # Width and Height of Port shape
    PORT_WIDTH = 10
    PORT_HEIGHT = 10

    # The number of control points when drawing connection curve
    CONNECTION_CONTROL_POINTS = 20

    # Control the size and gap for the 3 little segments when
    # draw connections between versions
    LINK_SEGMENT_LENGTH = 15
    LINK_SEGMENT_GAP = 5

    # The size of the frame containing the PIP graphics view
    PIP_IN_FRAME_WIDTH = 5
    PIP_OUT_FRAME_WIDTH = 1

    # The size of the frame containing the PIP graphics view
    PIP_DEFAULT_SIZE = (256, 256)

    # Default Paramter Inspector Window dimension
    VISUAL_DIFF_PARAMETER_WINDOW_SIZE = (348,256)

    # Default legend size (small rectangular shape)
    VISUAL_DIFF_LEGEND_SIZE = (16, 16)
    
    def __init__(self):
        """ DefaultTheme() -> DefaultTheme
        This is for initializing all Qt objects
        
        """        
        #### BRUSH & PEN ####
        # Background brush of the pipeline view
        self.PIPELINE_VIEW_BACKGROUND_BRUSH = QtGui.QBrush(
            QtGui.QImage(core.system.visTrailsRootDirectory() +
                         '/gui/resources/images/pipeline_bg.png'))

        # Background brush of the version tree
        self.VERSION_TREE_BACKGROUND_BRUSH = QtGui.QBrush(
            QtGui.QImage(core.system.visTrailsRootDirectory() +
                         '/gui/resources/images/version_bg.png'))
        
        # Background brush of the query pipeline view
        self.QUERY_BACKGROUND_BRUSH = QtGui.QBrush(
            QtGui.QImage(core.system.visTrailsRootDirectory() +
                         '/gui/resources/images/query_bg.png'))

        # Pen to draw a module shape at regular state
        self.MODULE_PEN = QtGui.QPen(QtGui.QBrush(
            QtGui.QColor(*(ColorByName.getInt('black')))), 2)
        # Pen to draw a module shape when selected
        self.MODULE_SELECTED_PEN = QtGui.QPen(QtGui.QBrush(
            QtGui.QColor(*(ColorByName.getInt('banana')))), 2)
        # Brush and pen to draw a module label
        self.MODULE_LABEL_PEN = QtGui.QPen(QtGui.QBrush(
            QtGui.QColor(*(ColorByName.getInt('black')))), 2)
        self.MODULE_LABEL_SELECTED_PEN = QtGui.QPen(QtGui.QBrush(
            QtGui.QColor(*(ColorByName.getInt('black')))), 2)
        # Pen to draw module label when it is unmatched due to a query
        self.GHOSTED_MODULE_LABEL_PEN = QtGui.QPen(QtGui.QBrush(
            QtGui.QColor(*(ColorByName.getInt('dark_dim_grey')))), 2)
        # Brush to draw a module shape at different states
        self.MODULE_BRUSH = QtGui.QBrush(
            QtGui.QColor(*(ColorByName.getInt('light_grey'))))
        self.ERROR_MODULE_BRUSH = QtGui.QBrush(
            QtGui.QColor(*(ColorByName.getInt('salmon'))))
        self.SUCCESS_MODULE_BRUSH = QtGui.QBrush(
            QtGui.QColor(*(ColorByName.getInt('mint'))))
        self.ACTIVE_MODULE_BRUSH = QtGui.QBrush(
            QtGui.QColor(*(ColorByName.getInt('navajo_white'))))
        self.COMPUTING_MODULE_BRUSH = QtGui.QBrush(
            QtGui.QColor(*(ColorByName.getInt('yellow'))))
        self.NOT_EXECUTE_MODULE_BRUSH = QtGui.QBrush(
            QtGui.QColor(*(ColorByName.getInt('light_goldenrod'))))

        # Pen and brush for un-matched queried modules
        self.GHOSTED_MODULE_PEN = QtGui.QPen(QtGui.QBrush(
            QtGui.QColor(*(ColorByName.getInt('dark_dim_grey')))), 2)
        self.GHOSTED_MODULE_BRUSH = QtGui.QBrush(
            QtGui.QColor(*(ColorByName.getInt('light_dim_grey'))))

        # Brush and pen to draw a port shape at regular state
        self.PORT_PEN = QtGui.QPen(QtGui.QBrush(
            QtGui.QColor(*(ColorByName.getInt('black')))), 1)
        self.PORT_BRUSH = QtGui.QBrush(
            QtGui.QColor(*(ColorByName.getInt('light_grey'))))
        self.PORT_OPTIONAL_PEN = QtGui.QPen(QtGui.QBrush(
            QtGui.QColor(*(ColorByName.getInt('lamp_black')))), 1)
        self.PORT_OPTIONAL_BRUSH = QtGui.QBrush(
            QtGui.QColor(*(ColorByName.getInt('titanium_white'))))
        
        # Pen and brush for drawing ports of ghosted modules
        self.GHOSTED_PORT_PEN = QtGui.QPen(QtGui.QBrush(
            QtGui.QColor(*(ColorByName.getInt('dark_dim_grey')))), 2)
        self.GHOSTED_PORT_BRUSH = QtGui.QBrush(
            QtGui.QColor(*(ColorByName.getInt('light_dim_grey'))))

        # Brush and pen to draw connections
        self.CONNECTION_PEN = QtGui.QPen(QtGui.QBrush(
            QtGui.QColor(*(ColorByName.getInt('black')))), 2)
        self.CONNECTION_SELECTED_PEN = QtGui.QPen(QtGui.QBrush(
            QtGui.QColor(*(ColorByName.getInt('banana')))), 2)
        self.CONNECTION_BRUSH = QtGui.QBrush(
            QtGui.QColor(*(ColorByName.getInt('black'))))

        # Pen for drawing while connecting any ghosted modules
        self.GHOSTED_CONNECTION_PEN = QtGui.QPen(QtGui.QBrush(
            QtGui.QColor(*(ColorByName.getInt('dark_dim_grey')))), 2)

        # Pen to draw version tree node
        self.VERSION_PEN = QtGui.QPen(QtGui.QBrush(
            QtGui.QColor(*(ColorByName.getInt('black')))), 2)    
        self.GHOSTED_VERSION_PEN = QtGui.QPen(QtGui.QBrush(
            QtGui.QColor(*(ColorByName.getInt('light_grey')))), 2)    
        self.VERSION_SELECTED_PEN = QtGui.QPen(QtGui.QBrush(
            QtGui.QColor(*(ColorByName.getInt('banana')))), 2)

        # Brush and pen to draw a version label
        self.VERSION_LABEL_PEN = QtGui.QPen(QtGui.QBrush(
            QtGui.QColor(*(ColorByName.getInt('black')))), 2)
        self.GHOSTED_VERSION_LABEL_PEN = QtGui.QPen(QtGui.QBrush(
            QtGui.QColor(*(ColorByName.getInt('light_grey')))), 2)
        self.VERSION_LABEL_SELECTED_PEN = QtGui.QPen(QtGui.QBrush(
            QtGui.QColor(*(ColorByName.getInt('black')))), 2)

        # Brush to draw version belongs to the current user
        self.VERSION_USER_BRUSH = QtGui.QBrush(
            QtGui.QColor(*(ColorByName.getInt('desatcornflower'))))
        self.GHOSTED_VERSION_USER_BRUSH = QtGui.QBrush(
            QtGui.QColor(*(ColorByName.getInt('very_light_grey'))))

        # Brush to draw version belongs to the other users
        self.VERSION_OTHER_BRUSH = QtGui.QBrush(
            QtGui.QColor(*(ColorByName.getInt('melon'))))
    
        # Brush and pen to draw a link between two versions
        self.LINK_PEN = QtGui.QPen(QtGui.QBrush(
            QtGui.QColor(*(ColorByName.getInt('black')))), 1.5)
        self.LINK_SELECTED_PEN = QtGui.QPen(QtGui.QBrush(
            QtGui.QColor(*(ColorByName.getInt('banana')))), 2)
        self.GHOSTED_LINK_PEN = QtGui.QPen(QtGui.QBrush(
            QtGui.QColor(*(ColorByName.getInt('light_grey')))), 2)

        # Selection box color
        self.SELECTION_BOX_BRUSH = QtGui.QBrush(
            QtGui.QColor(*ColorByName.getInt('light_grey')))
        self.SELECTION_BOX_PEN = QtGui.QPen(QtGui.QBrush(
            QtGui.QColor(*ColorByName.getInt('lamp_black'))), 1)
        
        # Color of the version is being diff from in
        self.VISUAL_DIFF_FROM_VERSION_BRUSH = QtGui.QBrush(
            QtGui.QColor(*ColorByName.getInt('melon')))
        
        # Color of the version is being diff to in
        self.VISUAL_DIFF_TO_VERSION_BRUSH = QtGui.QBrush(
            QtGui.QColor(*ColorByName.getInt('steel_blue_light')))
        
        # Color of the paramter changed modules in Visual Diff
        self.VISUAL_DIFF_PARAMETER_CHANGED_BRUSH = QtGui.QBrush(
            QtGui.QColor(*ColorByName.getInt('light_grey')))
        
        # Color of the shared modules in Visual Diff
        self.VISUAL_DIFF_SHARED_BRUSH = QtGui.QBrush(
            QtGui.QColor(155, 155, 155, 255))
    
        #### FONTS ####        
        # Font for shape engine text
        self.MODULE_FONT = QtGui.QFont("Arial", 14, QtGui.QFont.Bold)
        self.MODULE_FONT_METRIC = QtGui.QFontMetrics(self.MODULE_FONT)
    
        # Font for shape engine text
        self.VERSION_FONT = QtGui.QFont("Arial", 15, QtGui.QFont.Bold)
        self.VERSION_FONT_METRIC = QtGui.QFontMetrics(self.VERSION_FONT)
        
        # Font showing on the Parameter Inspector window of Visual Diff
        self.VISUAL_DIFF_PARAMETER_FONT = QtGui.QFont('Arial', 10)
        
        # Font showing on the Legend window of Visual Diff
        self.VISUAL_DIFF_LEGEND_FONT = QtGui.QFont('Arial', 9)


        #### ICONS & IMAGES ####
        # The execute icons in the first spot of vistrail view toolbar
        self.EXECUTE_PIPELINE_ICON = QtGui.QIcon(
            core.system.visTrailsRootDirectory() +
            '/gui/resources/images/execute_pipeline.png')
    
        # Icon to select the tabbed view
        self.TABBED_VIEW_ICON = QtGui.QIcon(
            core.system.visTrailsRootDirectory() +
            '/gui/resources/images/tabbed_view.png')
    
        # Icon to select the horizontal split view
        self.HORIZONTAL_VIEW_ICON = QtGui.QIcon(
            core.system.visTrailsRootDirectory() +
            '/gui/resources/images/hor_view.png')
    
        # Icon to select the vertical split view
        self.VERTICAL_VIEW_ICON = QtGui.QIcon(
            core.system.visTrailsRootDirectory() +
            '/gui/resources/images/ver_view.png')
    
        # Icon to select the docking-style view
        self.DOCK_VIEW_ICON = QtGui.QIcon(
            core.system.visTrailsRootDirectory() +
            '/gui/resources/images/dock_view.png')
    
        # Toolbar icon for creating a new Vistrail
        self.NEW_VISTRAIL_ICON = QtGui.QIcon(
            core.system.visTrailsRootDirectory() +
            '/gui/resources/images/new_vistrail.png')
        
        # Toolbar icon for openning a new Vistrail
        self.OPEN_VISTRAIL_ICON = QtGui.QIcon(
            core.system.visTrailsRootDirectory() +
            '/gui/resources/images/open_vistrail.png')
        
        # Toolbar icon for save the current Vistrail
        self.SAVE_VISTRAIL_ICON = QtGui.QIcon(
            core.system.visTrailsRootDirectory() +
            '/gui/resources/images/save_vistrail.png')
    
        # Toolbar icon for toggling console mode window
        self.CONSOLE_MODE_ICON = QtGui.QIcon(
            core.system.visTrailsRootDirectory() +
            '/gui/resources/images/console.png')

        # Toolbar icon for toggling bookmarks window
        self.BOOKMARKS_ICON = QtGui.QIcon(
            core.system.visTrailsRootDirectory() +
            '/gui/resources/images/bookmarks.png')
    
        # Background image of the Visual Diff pipeline view
        self.VISUAL_DIFF_BACKGROUND_IMAGE = QtGui.QImage(
            core.system.visTrailsRootDirectory() +
            '/gui/resources/images/pipeline_bg.png')
        
        # Toolbar icon for showing the Parameter Inspector window
        self.VISUAL_DIFF_SHOW_PARAM_ICON = QtGui.QIcon(
            core.system.visTrailsRootDirectory() +
            '/gui/resources/images/show_params.png')
        
        # Toolbar icon for showing the Legend window
        self.VISUAL_DIFF_SHOW_LEGEND_ICON = QtGui.QIcon(
            core.system.visTrailsRootDirectory() +
            '/gui/resources/images/show_legends.png')

        # Toolbar icon for close button on the vistrail tabbar
        self.VIEW_MANAGER_CLOSE_ICON = QtGui.QIcon(
            core.system.visTrailsRootDirectory() +
            '/gui/resources/images/closeview.png')

        # Toolbar icon for the dock toolbutton on the splitted window
        self.DOCK_BACK_ICON = QtGui.QIcon(
            core.system.visTrailsRootDirectory() +
            '/gui/resources/images/dockback.png')

        # Icon for adding string in the parameter exploration widget
        self.ADD_STRING_ICON = QtGui.QIcon(
            core.system.visTrailsRootDirectory() +
            '/gui/resources/images/edit_add.png')

        # Icon for moving string up in the parameter exploration widget
        self.UP_STRING_ICON = QtGui.QIcon(
            core.system.visTrailsRootDirectory() +
            '/gui/resources/images/up.png')

        # Icon for moving string up in the parameter exploration widget
        self.DOWN_STRING_ICON = QtGui.QIcon(
            core.system.visTrailsRootDirectory() +
            '/gui/resources/images/down.png')

        # Toolbar icon for visual query on a vistrail
        self.VISUAL_QUERY_ICON = QtGui.QIcon(
            core.system.visTrailsRootDirectory() +
            '/gui/resources/images/visual_query.png')
        
        # Toolbar icon for viewing the whole version tree
        self.VIEW_FULL_TREE_ICON = QtGui.QIcon(
            core.system.visTrailsRootDirectory() +
            '/gui/resources/images/full_tree.png')
        
        # Toolbar icon for dragging pixmap of VisDiff
        self.VERSION_DRAG_PIXMAP = QtGui.QPixmap(
            core.system.visTrailsRootDirectory() +
            '/gui/resources/images/dragging.png')

        # Cursor for zoom in/out graphics views
        self.SELECT_CURSOR = QtGui.QCursor(QtCore.Qt.ArrowCursor)
        self.OPEN_HAND_CURSOR = QtGui.QCursor(QtGui.QPixmap(
            core.system.visTrailsRootDirectory() +
            '/gui/resources/images/open_hand.png'))
        self.CLOSE_HAND_CURSOR = QtGui.QCursor(QtGui.QPixmap(
            core.system.visTrailsRootDirectory() +
            '/gui/resources/images/close_hand.png'))
        self.ZOOM_CURSOR = QtGui.QCursor(QtGui.QPixmap(
            core.system.visTrailsRootDirectory() +
            '/gui/resources/images/zoom.png'))
                
        # Cursor icon for zoom in/out graphics views
        self.SELECT_ICON = QtGui.QIcon(QtGui.QPixmap(
            core.system.visTrailsRootDirectory() +
            '/gui/resources/images/select_icon.png'))        
        self.PAN_ICON = QtGui.QIcon(QtGui.QPixmap(
            core.system.visTrailsRootDirectory() +
            '/gui/resources/images/pan_icon.png'))
        self.ZOOM_ICON = QtGui.QIcon(QtGui.QPixmap(
            core.system.visTrailsRootDirectory() +
            '/gui/resources/images/zoom_icon.png'))
                
        #### COLORS ####
        # Color for the PIP frame
        self.PIP_FRAME_COLOR = QtGui.QColor(
            *(ColorByName.getInt('yellow_light')))

        # Color of selected methods in the modules method area
        self.METHOD_SELECT_COLOR = QtGui.QColor(
            *ColorByName.getInt('yellow_light'))

        # Color of the hover/unhover alias labels
        self.HOVER_DEFAULT_COLOR = QtGui.QColor(
            *ColorByName.getInt('black'))
        self.HOVER_SELECT_COLOR = QtGui.QColor(
            *ColorByName.getInt('blue'))


class ThemeHolder(object):
    """
    ThemeHolder is a class holding a theme and exposed that theme
    atrributes as attributes of itself. This is useful for global
    import of the CurrentTheme variable
    
    """
    def __init__(self):
        object.__init__(self)
        self.theme = None

    def __getattr__(self, attr):
        """ __getattr__(attr: str) -> value
        Look-up attr in self.theme instead of itself
        
        """
        return getattr(self.theme,attr)

    def setTheme(self, theme):
        """ setTheme(theme: subclass of DefaultTheme) -> None
        Set the current theme to theme
        
        """
        self.theme = theme

def initializeCurrentTheme():
    """ initializeCurrentTheme() -> None
    Assign the current theme to the default theme
    
    """
    global CurrentTheme
    CurrentTheme.setTheme(DefaultTheme())

global CurrentTheme
CurrentTheme = ThemeHolder()
    
################################################################################

import unittest

class TestPresetColor(unittest.TestCase):
    """
    A few simple tests to make sure Preset is working as expected
    
    """
    def testColorValues(self):
        self.assertEquals(CurrentTheme.CONNECTION_CONTROL_POINT,
                          20)
        self.assertEquals(CurrentTheme.GHOSTED_VERSION_COLOR,
                          ColorByName.get('very_light_grey'))

        
if __name__ == '__main__':
    unittest.main()

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
"""
This module describes a theme structure for VisTrails GUI. It
specifies colors, background images and other measurements
"""
from __future__ import division

from PyQt4 import QtCore, QtGui

from vistrails.core.utils.color import ColorByName
from vistrails.core.theme import DefaultCoreTheme
import vistrails.core.system

import unittest
import vistrails.gui.qt

################################################################################

def _create_configure_shape(w, h):
    poly = QtGui.QPolygon(3)
    poly.setPoint(0, 0, 0)
    poly.setPoint(1, 0, h)
    poly.setPoint(2, w, h/2)
    return QtGui.QPolygonF(poly)
    

class DefaultTheme(DefaultCoreTheme):
    """
    This is the default theme which contains color, images,
    measurements, etc. for Vistrail. Other themes should derive from
    this class and change appropriate values
    
    """
    
    def __init__(self):
        """ DefaultTheme() -> DefaultTheme
        This is for initializing all Qt objects
        
        """
        DefaultCoreTheme.__init__(self)
        ######################
        #### MEASUREMENTS ####

        # pipeline view bounding rect
        self.BOUNDING_RECT_MINIMUM = 512

        # Port shape
        self.PORT_RECT = QtCore.QRectF(0, 0, self.PORT_WIDTH, self.PORT_HEIGHT)

        # Configure button shape
        self.CONFIGURE_SHAPE = _create_configure_shape(self.CONFIGURE_WIDTH,
                                                       self.CONFIGURE_HEIGHT)

        #### BRUSH & PEN ####
        # Background brush of the pipeline view
        # self.PIPELINE_VIEW_BACKGROUND_BRUSH = QtGui.QBrush(
        #     QtGui.QImage(vistrails.core.system.vistrails_root_directory() +
        #                  '/gui/resources/images/pipeline_bg.png'))
        #     #QtGui.QColor("white"))
        # # Background brush of the version tree
        # self.VERSION_TREE_BACKGROUND_BRUSH = QtGui.QBrush(
        #     QtGui.QImage(vistrails.core.system.vistrails_root_directory() +
        #                  '/gui/resources/images/version_bg.png'))
        # Background brush of the query pipeline view
        # self.QUERY_BACKGROUND_BRUSH = QtGui.QBrush(
        #     QtGui.QImage(vistrails.core.system.vistrails_root_directory() +
        #                  '/gui/resources/images/query_bg.png'))
        self.PIPELINE_VIEW_BACKGROUND_BRUSH = QtGui.QBrush(
            QtGui.QColor(128, 128, 128))
        self.VERSION_TREE_BACKGROUND_BRUSH = QtGui.QBrush(
            QtGui.QColor(240, 240, 240))
        self.QUERY_BACKGROUND_BRUSH = QtGui.QBrush(
            QtGui.QColor(119, 143, 159))
        self.QUERY_RESULT_BACKGROUND_BRUSH = QtGui.QBrush(
            QtGui.QColor(208, 226, 239))

        # Pen to draw a module shape at regular state
        self.MODULE_PEN = QtGui.QPen(QtGui.QBrush(
            QtGui.QColor(*(ColorByName.get_int('black')))), 2)
        # Pen to draw a module shape when selected
        self.MODULE_SELECTED_PEN = QtGui.QPen(QtGui.QBrush(
            QtGui.QColor(*(ColorByName.get_int('goldenrod_medium')))), 3)
        # Brush and pen to draw a module label
        self.MODULE_LABEL_PEN = QtGui.QPen(QtGui.QBrush(
            QtGui.QColor(*(ColorByName.get_int('black')))), 2)
        self.MODULE_LABEL_SELECTED_PEN = QtGui.QPen(QtGui.QBrush(
            QtGui.QColor(*(ColorByName.get_int('black')))), 2)
        # Brush to draw a module shape at different states
        self.MODULE_BRUSH = QtGui.QBrush(
            QtGui.QColor(*(ColorByName.get_int('light_grey'))))
        self.ERROR_MODULE_BRUSH = QtGui.QBrush(
            QtGui.QColor(*(ColorByName.get_int('salmon'))))
        self.SUCCESS_MODULE_BRUSH = QtGui.QBrush(
            QtGui.QColor(*(ColorByName.get_int('mint'))))
        self.ACTIVE_MODULE_BRUSH = QtGui.QBrush(
            QtGui.QColor(*(ColorByName.get_int('navajo_white'))))
        self.COMPUTING_MODULE_BRUSH = QtGui.QBrush(
            QtGui.QColor(*(ColorByName.get_int('yellow'))))
        self.NOT_EXECUTED_MODULE_BRUSH = QtGui.QBrush(
            QtGui.QColor(*(ColorByName.get_int('light_goldenrod'))))
        self.PERSISTENT_MODULE_BRUSH = QtGui.QBrush(
            QtGui.QColor(*(ColorByName.get_int('slate_blue'))))
        self.SUSPENDED_MODULE_BRUSH = QtGui.QBrush(
            QtGui.QColor(*(ColorByName.get_int('aureoline_yellow'))))

        self.INVALID_MODULE_PEN = QtGui.QPen(QtGui.QBrush(
                QtGui.QColor(51, 51, 51, 255)), 2)
        self.INVALID_MODULE_LABEL_PEN = QtGui.QPen(QtGui.QBrush(
            QtGui.QColor(51, 51, 51, 255)), 2)
        self.INVALID_MODULE_BRUSH = QtGui.QBrush(
            QtGui.QColor(125, 92, 92, 255))

        # Pen and brush for un-matched queried modules
        self.GHOSTED_MODULE_PEN = QtGui.QPen(QtGui.QBrush(
                QtGui.QColor(*(ColorByName.get_int('dark_dim_grey')))), 2)
        # Pen to draw module label when it is unmatched due to a query
        self.GHOSTED_MODULE_LABEL_PEN = QtGui.QPen(QtGui.QBrush(
                QtGui.QColor(*(ColorByName.get_int('dark_dim_grey')))), 2)
        self.GHOSTED_MODULE_BRUSH = QtGui.QBrush(
            QtGui.QColor(*(ColorByName.get_int('light_dim_grey'))))

        # Pen and brush for breakpoint modules
        self.BREAKPOINT_MODULE_PEN = QtGui.QPen(QtGui.QBrush(
                QtGui.QColor(*(ColorByName.get_int('dark_dim_grey')))), 2)
        self.BREAKPOINT_MODULE_BRUSH = QtGui.QBrush(
            QtGui.QColor(*(ColorByName.get_int('light_dim_grey'))))
        self.BREAKPOINT_MODULE_LABEL_PEN = QtGui.QPen(QtGui.QBrush(
                QtGui.QColor(*(ColorByName.get_int('dark_dim_grey')))), 2)

        # Module pen styles
        self.ABSTRACTION_PEN = QtGui.QPen(QtGui.QBrush(
            QtGui.QColor(*(ColorByName.get_int('black')))), 2,
                                          QtCore.Qt.DotLine)
        self.GROUP_PEN = QtGui.QPen(QtGui.QBrush(
            QtGui.QColor(*(ColorByName.get_int('black')))), 2,
                                          QtCore.Qt.DashLine)

        # Brush and pen to draw a port shape at regular state
        self.PORT_PEN_WIDTH_MANDATORY = 'mandatory'
        self.PORT_PEN_WIDTH_NORMAL = 'normal'
        self.PORT_PEN_WIDTH_SELECTED = 'selected'
        self.PORT_PEN_WIDTHS = {self.PORT_PEN_WIDTH_MANDATORY: 1.5, 
                                self.PORT_PEN_WIDTH_NORMAL: 1.0, 
                                self.PORT_PEN_WIDTH_SELECTED: 3.0}
        self.PORT_PEN_COLOR_NORMAL = 'normal'
        self.PORT_PEN_COLOR_FULL = 'full'
        self.PORT_PEN_COLOR_INVALID = 'invalid'
        self.PORT_PEN_COLOR_GHOSTED = 'ghosted'
        self.PORT_PEN_COLOR_SELECTED = 'selected'
        self.PORT_PEN_COLORS = \
            {self.PORT_PEN_COLOR_NORMAL: \
                 QtGui.QColor(*(ColorByName.get_int('black'))),
             self.PORT_PEN_COLOR_FULL: \
                 QtGui.QColor(*(ColorByName.get_int('dark_dim_grey'))),
             self.PORT_PEN_COLOR_INVALID: QtGui.QColor(51, 51, 51, 255),
             self.PORT_PEN_COLOR_GHOSTED: \
                 QtGui.QColor(*(ColorByName.get_int('dark_dim_grey'))),
             self.PORT_PEN_COLOR_SELECTED: \
                 QtGui.QColor(*(ColorByName.get_int('goldenrod_medium')))
             }
            
        self.PORT_PENS = {}
        for (color_type, color) in self.PORT_PEN_COLORS.iteritems():
            for (width_type, width) in self.PORT_PEN_WIDTHS.iteritems():
                self.PORT_PENS[(color_type, width_type)] = \
                    QtGui.QPen(QtGui.QBrush(color), width)

        self.PORT_CONNECTED_BRUSH = QtGui.QBrush(
            QtGui.QColor(0,0,0,60))
        self.PORT_BRUSH = QtGui.QBrush(QtCore.Qt.NoBrush)
        self.PORT_MANDATORY_BRUSH = QtGui.QBrush(QtGui.QColor(255,255,255,180))
        self.GHOSTED_PORT_BRUSH = QtGui.QBrush(
            QtGui.QColor(*(ColorByName.get_int('light_dim_grey'))))
        self.INVALID_PORT_BRUSH = QtGui.QBrush(
            QtGui.QColor(125, 92, 92, 255))

        # Pen and brush for drawing the configure button
        self.CONFIGURE_PEN = QtGui.QPen(QtGui.QBrush(
            QtGui.QColor(*(ColorByName.get_int('black')))), 1)
        self.CONFIGURE_BRUSH= QtGui.QBrush(
            QtGui.QColor(*(ColorByName.get_int('black'))))

        # Pen and brush for drawing the ghosted configure button
        self.GHOSTED_CONFIGURE_PEN = QtGui.QPen(QtGui.QBrush(
            QtGui.QColor(*(ColorByName.get_int('dark_dim_grey')))), 2)
        self.GHOSTED_CONFIGURE_BRUSH = QtGui.QBrush(
            QtGui.QColor(*(ColorByName.get_int('dark_dim_grey'))))

        # Brush and pen to draw connections
        self.CONNECTION_PEN = QtGui.QPen(QtGui.QBrush(
            QtGui.QColor(*(ColorByName.get_int('black')))), 2)
        self.CONNECTION_SELECTED_PEN = QtGui.QPen(
                QtGui.QBrush(
                    QtGui.QColor(*(ColorByName.get_int('goldenrod_medium')))),
                3,
                QtCore.Qt.SolidLine)
        self.CONNECTION_SELECTED_CONVERTING_PEN = QtGui.QPen(
                QtGui.QBrush(
                    QtGui.QColor(*(ColorByName.get_int('goldenrod_medium')))),
                3,
                QtCore.Qt.DotLine)
        self.CONNECTION_BRUSH = QtGui.QBrush(
            QtGui.QColor(*(ColorByName.get_int('black'))))

        # Pen for drawing while connecting any ghosted modules
        self.GHOSTED_CONNECTION_PEN = QtGui.QPen(QtGui.QBrush(
            QtGui.QColor(*(ColorByName.get_int('dark_dim_grey')))), 2)

        # Pen to draw version tree node
        self.VERSION_PEN = QtGui.QPen(QtGui.QBrush(
            QtGui.QColor(*(ColorByName.get_int('black')))), 2)    
        self.GHOSTED_VERSION_PEN = QtGui.QPen(QtGui.QBrush(
            QtGui.QColor(*(ColorByName.get_int('light_grey')))), 2)    
        self.VERSION_SELECTED_PEN = QtGui.QPen(QtGui.QBrush(
            QtGui.QColor(*(ColorByName.get_int('goldenrod_medium')))), 4)

        self.VERSION_LABEL_COLOR = \
            QtGui.QColor(*(ColorByName.get_int('black')))
        self.GHOSTED_VERSION_LABEL_COLOR = \
            QtGui.QColor(*(ColorByName.get_int('light_grey')))

        # Brush to draw version belongs to the current user
        self.VERSION_USER_BRUSH = QtGui.QBrush(
            QtGui.QColor(*(ColorByName.get_int('desatcornflower'))))
        self.GHOSTED_VERSION_USER_BRUSH = QtGui.QBrush(
            QtGui.QColor(*(ColorByName.get_int('very_light_grey'))))

        # Brush to draw version belongs to the other users
        self.VERSION_OTHER_BRUSH = QtGui.QBrush(
            QtGui.QColor(*(ColorByName.get_int('melon'))))
    
        # Brush and pen to draw a link between two versions
        self.LINK_PEN = QtGui.QPen(QtGui.QBrush(
            QtGui.QColor(*(ColorByName.get_int('black')))), 1.5)
        self.LINK_SELECTED_PEN = QtGui.QPen(QtGui.QBrush(
            QtGui.QColor(*(ColorByName.get_int('goldenrod_medium')))), 3)
        self.GHOSTED_LINK_PEN = QtGui.QPen(QtGui.QBrush(
            QtGui.QColor(*(ColorByName.get_int('light_grey')))), 2)

        # Selection box color
        self.SELECTION_BOX_BRUSH = QtGui.QBrush(
            QtGui.QColor(*ColorByName.get_int('light_grey')))
        self.SELECTION_BOX_PEN = QtGui.QPen(QtGui.QBrush(
            QtGui.QColor(*ColorByName.get_int('lamp_black'))), 1)
        
        # Color of the version is being diff from in
        self.VISUAL_DIFF_FROM_VERSION_BRUSH = QtGui.QBrush(
            QtGui.QColor(*ColorByName.get_int('melon')))
        
        # Color of the version is being diff to in
        self.VISUAL_DIFF_TO_VERSION_BRUSH = QtGui.QBrush(
            QtGui.QColor(*ColorByName.get_int('steel_blue_light')))
        
        # Color of the paramter changed modules in Visual Diff
        self.VISUAL_DIFF_PARAMETER_CHANGED_BRUSH = QtGui.QBrush(
            QtGui.QColor(*ColorByName.get_int('light_grey')))
        
        # Color of the shared modules in Visual Diff
        self.VISUAL_DIFF_SHARED_BRUSH = QtGui.QBrush(
            QtGui.QColor(155, 155, 155, 255))

        # Color of shared modules in Visual Diff matched by heuristic
        self.VISUAL_DIFF_MATCH_BRUSH = QtGui.QBrush(
            QtGui.QColor(*ColorByName.get_int('white')))
        
        # Color of partially shared modules in Visual Diff
        self.VISUAL_DIFF_SUMMARY_BRUSH = QtGui.QBrush(
            QtGui.QColor(*ColorByName.get_int('spring_green')))

        # Pen & Brush of the circled id on the right corner of the
        # virtual cell label
        self.ANNOTATED_ID_PEN = QtGui.QPen(
            QtCore.Qt.white)
        self.ANNOTATED_ID_BRUSH = QtGui.QBrush(
            QtGui.QColor(157, 0, 0, 255))
    
        #### FONTS ####        
        # Font for module text
        # Use fixed dpi to get same font size on all platforms
        def fixDPI(i):
            return i*72//QtGui.QApplication.desktop().logicalDpiY()
        GRAPHICS_FONT = "Arial"
        self.MODULE_FONT = QtGui.QFont(GRAPHICS_FONT, fixDPI(14), QtGui.QFont.Bold)
        self.MODULE_FONT_METRIC = QtGui.QFontMetrics(self.MODULE_FONT)
        self.MODULE_DESC_FONT = QtGui.QFont(GRAPHICS_FONT, fixDPI(12))
        self.MODULE_DESC_FONT_METRIC = QtGui.QFontMetrics(self.MODULE_DESC_FONT)
        self.MODULE_EDIT_FONT = QtGui.QFont(GRAPHICS_FONT, fixDPI(10))
        self.MODULE_EDIT_FONT_METRIC = QtGui.QFontMetrics(self.MODULE_EDIT_FONT)
    
        # Font for version text
        self.VERSION_FONT = QtGui.QFont(GRAPHICS_FONT, fixDPI(15), QtGui.QFont.Bold)
        self.VERSION_FONT_METRIC = QtGui.QFontMetrics(self.VERSION_FONT)
        self.VERSION_DESCRIPTION_FONT = QtGui.QFont(GRAPHICS_FONT, fixDPI(15),
                                                    QtGui.QFont.Normal, True)
        self.VERSION_DESCRIPTION_FONT_METRIC = \
            QtGui.QFontMetrics(self.VERSION_DESCRIPTION_FONT)

        self.VERSION_PROPERTIES_FONT = QtGui.QFont("Arial", 12)
        self.VERSION_PROPERTIES_FONT_METRIC = \
            QtGui.QFontMetrics(self.VERSION_PROPERTIES_FONT)
        self.VERSION_PROPERTIES_PEN =  QtGui.QBrush(
            QtGui.QColor(20, 100, 20, 255))
            

        # Font showing on the Parameter Inspector window of Visual Diff
        self.VISUAL_DIFF_PARAMETER_FONT = QtGui.QFont('Arial', 10)
        
        # Font showing on the Legend window of Visual Diff
        self.VISUAL_DIFF_LEGEND_FONT = QtGui.QFont('Arial', 9)

        # Font for PythonSource
        self.PYTHON_SOURCE_EDITOR_FONT = QtGui.QFont('Courier', 10, 
                                                     QtGui.QFont.Normal)
        # Font for Splash Screen messages
        self.SPLASH_SCREEN_FONT = QtGui.QFont('Arial', 10,
                                              QtGui.QFont.Normal)
        #### ICONS & IMAGES ####
        #The application disclaimer image
        self.DISCLAIMER_IMAGE = QtGui.QPixmap(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/disclaimer.png')
        #The application icon
        self.APPLICATION_ICON = QtGui.QIcon(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/vistrails_icon_small.png')

        #The application pixmap
        self.APPLICATION_PIXMAP = QtGui.QPixmap(
             vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/vistrails_icon_small.png')

        # The execute icons in the first spot of vistrail view toolbar
        self.EXECUTE_PIPELINE_ICON = QtGui.QIcon(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/execute.png')
        self.EXECUTE_EXPLORE_ICON = QtGui.QIcon(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/execute_explore.png')

        # The undo icons for the vistrail view toolbar
        self.UNDO_ICON = QtGui.QIcon(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/undo.png')

        # The redo icons for the vistrail view toolbar
        self.REDO_ICON = QtGui.QIcon(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/redo.png')

        # Icon to select the tabbed view
        self.TABBED_VIEW_ICON = QtGui.QIcon(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/tabbed_view.png')
    
        # Icon to select the horizontal split view
        self.HORIZONTAL_VIEW_ICON = QtGui.QIcon(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/hor_view.png')
    
        # Icon to select the vertical split view
        self.VERTICAL_VIEW_ICON = QtGui.QIcon(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/ver_view.png')
    
        # Icon to select the docking-style view
        self.DOCK_VIEW_ICON = QtGui.QIcon(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/dock_view.png')
    
        # Toolbar icon for creating a new Vistrail
        self.NEW_VISTRAIL_ICON = QtGui.QIcon(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/new_vistrail.png')
        
        # Toolbar icon for opening a vistrail
        self.OPEN_VISTRAIL_ICON = QtGui.QIcon(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/open_vistrail.png')

        #Toolbar icon for opening a vistrail from a database
        self.OPEN_VISTRAIL_DB_ICON = QtGui.QIcon(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/openfromdb.png')

        #Icon for database connections
        self.DB_ICON = QtGui.QIcon(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/database.png')

        #Icon for vistrails files
        self.FILE_ICON = QtGui.QIcon(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/file.png')
        
        # Toolbar icon for save the current Vistrail
        self.SAVE_VISTRAIL_ICON = QtGui.QIcon(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/save_vistrail.png')
    
        # Toolbar icon for toggling console mode window
        self.CONSOLE_MODE_ICON = QtGui.QIcon(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/console.png')

        # Background image of the Visual Diff pipeline view
        self.VISUAL_DIFF_BACKGROUND_IMAGE = QtGui.QImage(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/pipeline_bg.png')
        
        # Toolbar icon for showing the Parameter Inspector window
        self.VISUAL_DIFF_SHOW_PARAM_ICON = QtGui.QIcon(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/show_params.png')
        
        # Toolbar icon for showing the Legend window
        self.VISUAL_DIFF_SHOW_LEGEND_ICON = QtGui.QIcon(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/show_legends.png')

        # Toolbar icon for creating an analogy
        self.VISUAL_DIFF_CREATE_ANALOGY_ICON = QtGui.QIcon(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/analogy.png')

        # Toolbar icon for close button on the vistrail tabbar
        self.VIEW_MANAGER_CLOSE_ICON = QtGui.QIcon(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/closeview.png')

        # Toolbar icon for the dock toolbutton on the splitted window
        self.DOCK_BACK_ICON = QtGui.QIcon(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/dockback.png')

        # Icon for adding string in the parameter exploration widget
        self.ADD_STRING_ICON = QtGui.QIcon(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/edit_add.png')

        # Icon for moving string up in the parameter exploration widget
        self.UP_STRING_ICON = QtGui.QIcon(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/up.png')

        # Icon for moving string up in the parameter exploration widget
        self.DOWN_STRING_ICON = QtGui.QIcon(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/down.png')

        # Icon for expand all/collapse all buttons in the Module Palette
        self.EXPAND_ALL_ICON = QtGui.QIcon(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/expand_all.png')
        
        self.COLLAPSE_ALL_ICON = QtGui.QIcon(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/collapse_all.png')
        
        # Icons for tree/list view buttons in the Workspace
        self.LIST_VIEW_ICON = QtGui.QIcon(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/list_view.png')
        
        self.TREE_VIEW_ICON = QtGui.QIcon(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/tree_view.png')

        # Toolbar icons for views
        self.PIPELINE_ICON = QtGui.QIcon(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/pipeline.png')
        self.HISTORY_ICON = QtGui.QIcon(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/history.png')
        self.QUERY_ICON = QtGui.QIcon(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/full_tree.png')
        self.EXPLORE_ICON = QtGui.QIcon(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/explore.png')
        self.PROVENANCE_ICON = QtGui.QIcon(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/search_database.png')

        # Toolbar icon for visual query on a vistrail
        self.VISUAL_QUERY_ICON = QtGui.QIcon(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/visual_query.png')
        
        # Toolbar icon for viewing the whole version tree
        self.VIEW_FULL_TREE_ICON = QtGui.QIcon(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/full_tree.png')

        # Toolbar icon for viewing the whole version tree
        self.PERFORM_PARAMETER_EXPLORATION_ICON = QtGui.QIcon(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/perform_pe.png')

        # Toolbar icon for dragging pixmap of VisDiff
        self.VERSION_DRAG_PIXMAP = QtGui.QPixmap(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/dragging.png')

        #Tabbar icon for detach a tab        
        self.DETACH_TAB_ICON = QtGui.QIcon()
        self.DETACH_TAB_ICON.addFile(vistrails.core.system.vistrails_root_directory() +
                                     '/gui/resources/images/detach.png',
                                     mode=QtGui.QIcon.Normal)
        self.DETACH_TAB_ICON.addFile(vistrails.core.system.vistrails_root_directory() +
                                     '/gui/resources/images/detach_on.png',
                                     mode=QtGui.QIcon.Active)

        #toolbutton icon for pin/unpin palette
        self.PINNED_PALETTE_ICON = QtGui.QIcon(
                                vistrails.core.system.vistrails_root_directory() +
                                '/gui/resources/images/pinned.png')
        self.UNPINNED_PALETTE_ICON = QtGui.QIcon(
                                vistrails.core.system.vistrails_root_directory() +
                                '/gui/resources/images/unpinned.png')
        # Parameter Exploration Pixmaps
        self.EXPLORE_COLUMN_PIXMAP = QtGui.QPixmap(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/column.png')
        self.EXPLORE_ROW_PIXMAP = QtGui.QPixmap(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/row.png')
        self.EXPLORE_SHEET_PIXMAP = QtGui.QPixmap(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/sheet.png')
        self.EXPLORE_TIME_PIXMAP = QtGui.QPixmap(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/time.png')        
        self.EXPLORE_SKIP_PIXMAP = QtGui.QPixmap(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/skip.png')        
        self.REMOVE_PARAM_PIXMAP = QtGui.QPixmap(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/remove_param.png')        
        self.RIGHT_ARROW_PIXMAP = QtGui.QPixmap(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/right.png')        
        self.LEFT_ARROW_PIXMAP = QtGui.QPixmap(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/left.png')
        
        # Cursor for zoom in/out graphics views
        self.SELECT_CURSOR = QtGui.QCursor(QtCore.Qt.ArrowCursor)
        self.OPEN_HAND_CURSOR = QtGui.QCursor(QtGui.QPixmap(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/open_hand.png'))
        self.CLOSE_HAND_CURSOR = QtGui.QCursor(QtGui.QPixmap(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/close_hand.png'))
        self.ZOOM_CURSOR = QtGui.QCursor(QtGui.QPixmap(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/zoom.png'))
                
        # Cursor icon for zoom in/out graphics views
        self.SELECT_ICON = QtGui.QIcon(QtGui.QPixmap(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/select_icon.png'))
        self.PAN_ICON = QtGui.QIcon(QtGui.QPixmap(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/pan_icon.png'))
        self.ZOOM_ICON = QtGui.QIcon(QtGui.QPixmap(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/zoom_icon.png'))
        
        # Mashup Icons
        self.EXECUTE_MASHUP_ICON = QtGui.QIcon(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/mashup_execute.png')
        self.MASHUP_ICON = QtGui.QIcon(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/mashup_create.png')
        self.MASHUP_ALIAS_ICON = QtGui.QIcon(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/alias.png')

        # Job View Icons
        self.JOB_SCHEDULED = QtGui.QIcon(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/appointment-new.png')
        self.JOB_FINISHED = QtGui.QIcon(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/emblem-important.png')
        self.JOB_CHECKING = QtGui.QIcon(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/view-refresh.png')
        
        # Saved Queries icons
        self.QUERY_VIEW_ICON = self.ZOOM_ICON
        self.QUERY_ARROW_ICON = QtGui.QIcon(QtGui.QPixmap(
                vistrails.core.system.vistrails_root_directory() +
                '/gui/resources/images/zoom_arrow_icon.png'))
        self.QUERY_EDIT_ICON = QtGui.QIcon(QtGui.QPixmap(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/edit.png'))

        # Icon on the button to switch to single/multi line string edition
        self.MULTILINE_STRING_ICON = QtGui.QIcon(QtGui.QPixmap(
                vistrails.core.system.vistrails_root_directory() +
                '/gui/resources/images/multiline_string_icon.png'))

        # icons for the port list combination modes
        self.DOT_PRODUCT_ICON = QtGui.QIcon(QtGui.QPixmap(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/macro.png'))

        self.CROSS_PRODUCT_ICON = QtGui.QIcon(QtGui.QPixmap(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/remove_param.png'))

        #### COLORS ####
        # Color for the PIP frame
        self.PIP_FRAME_COLOR = QtGui.QColor(
            *(ColorByName.get_int('yellow_light')))

        # Color for invalid parameter frames
        self.PARAM_INVALID_COLOR = QtGui.QColor('#efef00')

        # Color of selected methods in the modules method area
        self.METHOD_SELECT_COLOR = QtGui.QColor(
            *ColorByName.get_int('yellow_light'))

        # Color of the hover/unhover alias labels
        self.HOVER_DEFAULT_COLOR = QtGui.QColor(
            *ColorByName.get_int('black'))
        self.HOVER_SELECT_COLOR = QtGui.QColor(
            *ColorByName.get_int('blue'))
        
        # colors for debug messages
        self.DEBUG_COLORS = {
                'DEBUG': QtGui.QColor("#777777"),
                'INFO': QtGui.QColor(QtCore.Qt.black),
                'WARNING': QtGui.QColor("#707000"),
                'CRITICAL': QtGui.QColor(QtCore.Qt.red),
            }
        class QTransparentColor(QtGui.QColor):
            def name(self):
                return 'transparent'
        self.DEBUG_FILTER_BACKGROUND_COLOR = QTransparentColor("transparent")
        
class MacTheme(DefaultTheme):
    def __init__(self):
        
        DefaultTheme.__init__(self)
        #### ICONS & IMAGES ####
        #The application icon
        self.APPLICATION_ICON = QtGui.QIcon(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/vistrails_icon.png')

        #The application pixmap
        self.APPLICATION_PIXMAP = QtGui.QPixmap(
             vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/vistrails_icon.png')

        # Toolbar icon for close button on the vistrail tabbar
        self.VIEW_MANAGER_CLOSE_ICON = QtGui.QIcon(
            vistrails.core.system.vistrails_root_directory() +
            '/gui/resources/images/mac/closetab.png')
        
        #### FONTS ####
        # Font for PythonSource
        self.PYTHON_SOURCE_EDITOR_FONT = QtGui.QFont('Monaco', 11, 
                                                     QtGui.QFont.Normal)
        
        # Font for Splash Screen messages
        self.SPLASH_SCREEN_FONT = QtGui.QFont('Helvetica', 10,
                                              QtGui.QFont.Light)
        
class LinuxTheme(DefaultTheme):
    def __init__(self):
        DefaultTheme.__init__(self)
        #### FONTS ####
        # Font for PythonSource
        self.PYTHON_SOURCE_EDITOR_FONT = QtGui.QFont('Monospace', 10, 
                                                     QtGui.QFont.Normal)
                
class ThemeHolder(object):
    """
    ThemeHolder is a class holding a theme and exposed that theme
    atrributes as attributes of itself. This is useful for global
    import of the CurrentTheme variable
    
    """
    def __init__(self):
        object.__init__(self)
        self.theme = None

    def setTheme(self, theme):
        """ setTheme(theme: subclass of DefaultTheme) -> None
        Set the current theme to theme
        
        """
        # This way, the lookups into the theme are much faster, since
        # there's no function calls involved
        self.__dict__.update(theme.__dict__)

def get_current_theme():
    """get_current_theme() -> subclass of DefaultTheme
    Instantiates the theme according to the current platform """
    if vistrails.core.system.systemType in ['Darwin']:
        return MacTheme()
    elif vistrails.core.system.systemType in ['Linux']:
        return LinuxTheme()
    else:
        return DefaultTheme()
    
def initializeCurrentTheme():
    """ initializeCurrentTheme() -> None
    Assign the current theme to the default theme
    
    """
    CurrentTheme.setTheme(get_current_theme())

global CurrentTheme
CurrentTheme = ThemeHolder()
    
################################################################################


class TestPresetColor(unittest.TestCase):
    """
    A few simple tests to make sure Preset is working as expected
    
    """
    def setUp(self):
        vistrails.gui.qt.createBogusQtGuiApp()

    def testColorValues(self):
        initializeCurrentTheme()
        self.assertEquals(CurrentTheme.CONNECTION_CONTROL_POINTS,
                          20)
        
if __name__ == '__main__':
    unittest.main()

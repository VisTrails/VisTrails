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
This module describes a core theme structure for VisTrails GUI. It
specifies measurements
"""

from __future__ import division

from vistrails.core.utils.color import ColorByName
import vistrails.core.system
################################################################################

class DefaultCoreTheme(object):
    """
    This is the default core theme which contains non-qt values,
    measurements for Vistrail. Other core themes should derive from
    this class and change appropriate values
    
    """
    
    def __init__(self):
        """ DefaultTheme() -> DefaultTheme
        This is for initializing all non-Qt values
        
        """
        ######################
        #### MEASUREMENTS ####

        # Padded space of Version shape and its label
        self.VERSION_LABEL_MARGIN = (60, 35)

        # Padded space of Module shape into its label
        self.MODULE_LABEL_MARGIN = (20, 20, 20, 15)

        # Padded space of Module shape into its edit widget
        self.MODULE_EDIT_MARGIN = (8, 4, 8, 4)

        # Margin of Module shape into its ports
        self.MODULE_PORT_MARGIN = (4, 4, 4, 4)

        # Space between ports inside a module
        self.MODULE_PORT_SPACE = 4

        # The space added to the end of port shapes before it reaches the
        # margin of the module
        self.MODULE_PORT_PADDED_SPACE = 20

        # Width and Height of Port shape
        self.PORT_WIDTH = 10
        self.PORT_HEIGHT = 10

        # Width and Height of Configure button shape
        self.CONFIGURE_WIDTH = 6
        self.CONFIGURE_HEIGHT = 10

        self.BREAKPOINT_FRINGE = \
            (((0.0,0.0),(-0.5,0.25),(-0.5,0.75),(0.0,1.0)),
             ((0.0,0.0),(0.5,0.25),(0.5,0.75),(0.0,1.0)))
                                       

        # The number of control points when drawing connection curve
        self.CONNECTION_CONTROL_POINTS = 20

        # Control the size and gap for the 3 little segments when
        # draw connections between versions
        self.LINK_SEGMENT_LENGTH = 15
        self.LINK_SEGMENT_GAP = 5
        self.LINK_SEGMENT_SQUARE_LENGTH = 12

        # The size of the frame containing the PIP graphics view
        self.PIP_IN_FRAME_WIDTH = 5
        self.PIP_OUT_FRAME_WIDTH = 1

        # The size of the frame containing the PIP graphics view
        self.PIP_DEFAULT_SIZE = (128, 128)

        # The default minimum size of the graphics views
        self.BOUNDING_RECT_MINIMUM = 512

        # Default Paramter Inspector Window dimension
        self.VISUAL_DIFF_PARAMETER_WINDOW_SIZE = (348,256)

        # Default legend size (small rectangular shape)
        self.VISUAL_DIFF_LEGEND_SIZE = (16, 16)

        # Virtual Cell Label default  size
        self.VIRTUAL_CELL_LABEL_SIZE = (40, 40)

        # Query Preview Size
        self.QUERY_PREVIEW_SIZE = (256, 256)

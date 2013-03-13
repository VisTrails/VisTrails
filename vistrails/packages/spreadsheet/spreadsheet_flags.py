###############################################################################
##
## Copyright (C) 2014-2015, New York University.
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

from __future__ import division

"""Flags controlling various options.

This is intended to be used by third-party applications that embed VisTrails,
to change the spreadsheet's behavior and capabilities.

DEFAULTS contain the default settings of the spreadsheet, the ones that are
used in VisTrails.
"""

# The window's menu
WINDOW_MENU_MAIN = 1 << 0
WINDOW_MENU_VIEW = 1 << 1
WINDOW_MENU_WINDOW = 1 << 2
# Allows to close the application from the spreadsheet via Ctrl+Q
WINDOW_QUIT_ACTION = 1 << 3

# Creates a first empty sheet 'Sheet 1' when creating the window
WINDOW_CREATE_FIRST_SHEET = 1 << 4
# Allows to create a new sheet from a sheet's toolbar
TAB_CREATE_SHEET = 1 << 5
# Allows to rename a sheet from the tab bar
TAB_RENAME_SHEET = 1 << 6
# Allows to close a sheet from the tab bar
TAB_CLOSE_SHEET = 1 << 7
# Allows to delete (i.e. empty) a cell in the sheet
TAB_DELETE_CELL = 1 << 8

DEFAULTS = (
        WINDOW_MENU_MAIN | WINDOW_MENU_VIEW | WINDOW_MENU_WINDOW |
        WINDOW_QUIT_ACTION |

        WINDOW_CREATE_FIRST_SHEET |
        TAB_CREATE_SHEET |
        TAB_RENAME_SHEET |
        TAB_CLOSE_SHEET |
        TAB_DELETE_CELL)

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
        TAB_RENAME_SHEET)

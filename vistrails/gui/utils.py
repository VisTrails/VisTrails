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

""" Utilities for creating simple dialogs, notifications in Vistrails
without exposing Qt codes """

from PyQt4 import QtGui

################################################################################

OK_BUTTON              = QtGui.QMessageBox.Ok
OPEN_BUTTON            = QtGui.QMessageBox.Open
SAVE_BUTTON            = QtGui.QMessageBox.Save
CANCEL_BUTTON          = QtGui.QMessageBox.Cancel
CLOSE_BUTTON           = QtGui.QMessageBox.Close
DISCARD_BUTTON         = QtGui.QMessageBox.Discard
APPLY_BUTTON           = QtGui.QMessageBox.Apply
RESET_BUTTON           = QtGui.QMessageBox.Reset
RESTOREDEFAULTS_BUTTON = QtGui.QMessageBox.RestoreDefaults
HELP_BUTTON            = QtGui.QMessageBox.Help
SAVEALL_BUTTON         = QtGui.QMessageBox.SaveAll
YES_BUTTON             = QtGui.QMessageBox.Yes
YESTOALL_BUTTON        = QtGui.QMessageBox.YesToAll
NO_BUTTON              = QtGui.QMessageBox.No
NOTOALL_BUTTON         = QtGui.QMessageBox.NoToAll
ABORT_BUTTON           = QtGui.QMessageBox.Abort
RETRY_BUTTON           = QtGui.QMessageBox.Retry
IGNORE_BUTTON          = QtGui.QMessageBox.Ignore
NOBUTTON_BUTTON        = QtGui.QMessageBox.NoButton

def show_warning(title, message):
    """ show_warning(title: str, message: str) -> None
    Show a warning  message box with a specific title and contents
    
    """
    QtGui.QMessageBox.warning(None, title, message)

def show_question(title,
                  message,
                  buttons = [OK_BUTTON],
                  default = NOBUTTON_BUTTON):
    """ show_question(title: str,
                      message: str,
                      buttons: list of buttons (defined above),
                      default: button (defined above)) -> button
    Show a question message with a specific title, message and a set
    of buttons defined by the list buttons. Default button is the
    button that will take role when the user press 'Enter' without
    selecting a button. The function returns the button that ends the
    dialog.
    
    """
    qButtons = QtGui.QMessageBox.StandardButtons()
    for button in buttons:
        qButtons |= button
    return QtGui.QMessageBox.question(None, title, message, qButtons, default)

def show_custom(title, message,
                button1, button2='', button3='',
                default=0, escape=-1):
    """ show_custom(title: str,
                    message: str,
                    button0, button1, button2: str,
                    default: int,
                    escape: int) -> int                    
    Show a custom dialog box with up to 3 buttons. The 3 buttons will
    have labels as specified in button0, button1, button2. If a label
    is empty. The button will not be shown. The function return a
    number as specified which button is pressed. Default and escape
    defined which button or value returned when Enter/Esc keys are
    pressed.
    
    """
    if button0=='': button0 = QtCore.QString()
    if button1=='': button1 = QtCore.QString()
    if button2=='': button2 = QtCore.QString()
    return QtGui.QMessageBox.question(None, title, message,
                                      button0, button1, button2,
                                      default, escape)

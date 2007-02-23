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
""" The file describes the parameter exploration table for VisTrails

QParameterExplorationTable
"""


from PyQt4 import QtCore, QtGui
from gui.common_widgets import QPromptWidget
from gui.theme import CurrentTheme

################################################################################
class QParameterExplorationTable(QPromptWidget):
    """
    QParameterExplorationTable is a grid layout widget having 4
    comlumns corresponding to 4 dimensions of exploration. It accept
    method/alias drops and can be fully configured onto any
    dimension. For each parameter, 3 different approach can be chosen
    to assign the value of that parameter during the exploration:
    linear interpolation (for int, float), list (for int, float and
    string) and user-define function (for int, float, and string)
    
    """
    def __init__(self, parent=None):
        """ QParameterExplorationTable(parent: QLabel)
                                      -> QParameterExplorationTable
        Create an grid layout and accept drops
        
        """
        QPromptWidget.__init__(self, parent)
        self.setPromptText('Drag parameter here for a paramter exploration')
        self.showPrompt()
        self.setAcceptDrops(True)
        
        gridLayout = QtGui.QGridLayout(self)
        gridLayout.setMargin(0)
        gridLayout.setSpacing(0)
        self.setLayout(gridLayout)
        
        columnLabel = QtGui.QLabel()
        columnLabel.setFrameStyle(QtGui.QFrame.StyledPanel)
        columnLabel.setPixmap(CurrentTheme.EXPLORE_COLUMN_PIXMAP)
        gridLayout.addWidget(columnLabel,
                             0, 1, 1, 1,
                             QtCore.Qt.AlignCenter)

        rowLabel = QtGui.QLabel()
        rowLabel.setFrameStyle(QtGui.QFrame.StyledPanel)
        rowLabel.setPixmap(CurrentTheme.EXPLORE_ROW_PIXMAP)
        gridLayout.addWidget(rowLabel,
                             0, 2, 1, 1,
                             QtCore.Qt.AlignCenter)

        sheetLabel = QtGui.QLabel()
        sheetLabel.setFrameStyle(QtGui.QFrame.StyledPanel)
        sheetLabel.setPixmap(CurrentTheme.EXPLORE_SHEET_PIXMAP)
        gridLayout.addWidget(sheetLabel,
                             0, 3, 1, 1,
                             QtCore.Qt.AlignCenter)

        timeLabel = QtGui.QLabel()
        timeLabel.setFrameStyle(QtGui.QFrame.StyledPanel)
        timeLabel.setPixmap(CurrentTheme.EXPLORE_TIME_PIXMAP)
        gridLayout.addWidget(timeLabel,
                             0, 4, 1, 1,
                             QtCore.Qt.AlignCenter)

        paddedSouth = QtGui.QLabel()
        paddedSouth.setAutoFillBackground(False)
        paddedSouth.setSizePolicy(QtGui.QSizePolicy.Ignored,
                                  QtGui.QSizePolicy.Expanding)
        gridLayout.addWidget(paddedSouth, 1, 1)

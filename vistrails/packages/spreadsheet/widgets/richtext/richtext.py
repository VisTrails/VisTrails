################################################################################
# Richtext widgets implementation
################################################################################
from core.modules.vistrails_module import Module
from PyQt4 import QtCore, QtGui
from packages.spreadsheet.basic_widgets import SpreadsheetCell

################################################################################

class RichTextCell(SpreadsheetCell):
    """
    RichTextCell is a custom Module to view HTML files
    
    """
    def compute(self):
        """ compute() -> None
        Dispatch the HTML contents to the spreadsheet
        """
        if self.hasInputFromPort("File"):
            fileValue = self.getInputFromPort("File")
        else:
            fileValue = None
        self.display(RichTextCellWidget, (fileValue,))

class RichTextCellWidget(QtGui.QTextBrowser):
    """
    RichTextCellWidget derives from the QTextBrowser to display HTML files
    
    """
    def __init__(self, parent=None):
        """ RichTextCellWidget(parent: QWidget) -> RichTextCellWidget
        Create a rich text cell without a toolbar
        
        """
        QtGui.QTextBrowser.__init__(self, parent)
        self.setMouseTracking(True)
        self.controlBarType = None

    def updateContents(self, inputPorts):
        """ updateContents(inputPorts: tuple) -> None
        Updates the contents with a new changed in filename
        
        """
        (fileValue,) = inputPorts
        if fileValue:
            try:
                fi = open(fileValue.name, "r")
            except IOError:
                self.setText("Cannot load the HTML file!")
                return            
            self.setHtml(fi.read())
            fi.close()
        else:
            self.setText("No HTML file is specified!")

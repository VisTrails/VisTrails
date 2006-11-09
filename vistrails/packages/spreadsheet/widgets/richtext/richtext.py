from core.modules.vistrails_module import Module
from PyQt4 import QtCore, QtGui
from packages.spreadsheet.basic_widgets import SpreadsheetCell

# A custom widget to edit text
class RichTextCell(SpreadsheetCell):
    
    def compute(self):
        if self.hasInputFromPort("File"): fileValue = self.getInputFromPort("File")
        else: fileValue = None
        self.display(RichTextCellWidget, (fileValue,))

### Rich Text Cell  widget type
class RichTextCellWidget(QtGui.QTextBrowser):
    def __init__(self, parent=None):
        QtGui.QTextBrowser.__init__(self, parent)
        self.setMouseTracking(True)
        self.controlBarType = None

    def updateContents(self, inputPorts):
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

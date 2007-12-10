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
""" This file specifies the configuration widget for Constant
modules. Please notice that this is different from the module configuration
widget described in module_configure.py. We present a Color constand to be
used as a template for creating a configuration widget for other custom
constants.

"""
from PyQt4 import QtCore, QtGui
from core.modules.module_registry import registry
from core.utils import any, expression
from core import system
############################################################################
class StandardConstantWidget(QtGui.QLineEdit):
    """
    StandardConstantWidget is a basic widget to be used
    to edit int/float/string values in VisTrails.

    When creating your own widget, you can subclass from this widget if you
    need only a QLineEdit or use your own QT widget. There are two things you
    need to pay attention to:

    1) Re-implement the contents() method so we can get the current value
       stored in the widget.

    2) When the user is done with configuration, make sure to call
       update_parent() so VisTrails can pass that information to the Provenance
       System. In this example we do that on focusOutEvent and when the user
       presses the return key.

    """
    def __init__(self, contents, contentType, parent=None):
        """__init__(contents: str, contentType: str, parent: QWidget) ->
                                             StandardConstantWidget
        Initialize the line edit with its contents. Content type is limited
        to 'int', 'float', and 'string'
        
        """
        QtGui.QWidget.__init__(self, parent)
        self.setText(contents)
        self._contentType = contentType
        self._last_text = None
        self.contentIsString = contentType=='String'
        self.connect(self,
                     QtCore.SIGNAL('returnPressed()'),
                     self.update_parent)               
        
    def contents(self):
        """contents() -> str
        Re-implement this method to make sure that it will return a string
        representation of the value that it will be passed to the module
        As this is a QLineEdit, we just call text()

        """
        self.update_text()
        return str(self.text())

    def update_text(self):
        """ update_text() -> None
        Update the text to the result of the evaluation
        
        """
        base = expression.evaluate_expressions(self.text())
        if self.contentIsString:
            self.setText(base)
        else:
            try:
                self.setText(str(eval(str(base), None, None)))
            except:
                self.setText(base)
                
    def update_parent(self):
        if self.parent():
            newText = self.contents()
            if newText!= self._last_text:
                self.parent().updateMethod()
                self._last_text = newText
                
    ###########################################################################
    # event handlers
    
    def focusInEvent(self, event):
        """ focusInEvent(event: QEvent) -> None
        Pass the event to the parent
        
        """
        self._contents = str(self.text())
        if self.parent():
            self.parent().focusInEvent(event)
        QtGui.QLineEdit.focusInEvent(self, event)
        
    def focusOutEvent(self, event):
        self.update_parent()
        QtGui.QWidget.focusOutEvent(self, event)

###############################################################################
# File Constant Widgets

class FileChooserToolButton(QtGui.QToolButton):
    """ 
    MethodFileChooser is a toolbar button that opens a browser for
    files.  The lineEdit is updated with the filename that is
    selected.  

    """
    def __init__(self, parent=None, lineEdit=None):
        """
        FileChooserButton(parent: QWidget, lineEdit: StandardConstantWidget) ->
                 FileChooserToolButton

        """
        QtGui.QToolButton.__init__(self, parent)
        self.setIcon(QtGui.QIcon(
                self.style().standardPixmap(QtGui.QStyle.SP_DirOpenIcon)))
        self.setIconSize(QtCore.QSize(12,12))
        self.setToolTip('Open a file chooser')
        self.setAutoRaise(True)
        self.lineEdit = lineEdit
        self.connect(self,
                     QtCore.SIGNAL('clicked()'),
                     self.openChooser)
             

    def openChooser(self):
        """
        openChooser() -> None
        
        """
        fileName = QtGui.QFileDialog.getOpenFileName(self,
                                                     'Use Filename '
                                                     'as Value...',
                                                     self.text(),
                                                     'All files '
                                                     '(*.*)')
        if self.lineEdit and not fileName.isEmpty():
            self.lineEdit.setText(fileName)
            self.lineEdit.update_parent()
            
class FileChooserWidget(QtGui.QWidget):
    """ 
    FileChooserWidget is a widget containing a line edit and a button that
    opens a browser for files. The lineEdit is updated with the filename that is
    selected.  

    """
    def __init__(self, contents, contentType, parent=None):
        """__init__(contents: str, contentType: str, parent: QWidget) ->
                                              FileChooserWidget
        Initializes the line edit with contents
        
        """
        QtGui.QWidget.__init__(self)
        layout = QtGui.QHBoxLayout()
        self.line_edit = StandardConstantWidget(contents, contentType, self)
        self.browse_button = FileChooserToolButton(self, self.line_edit) 
        layout.setMargin(5)
        layout.setSpacing(5)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.browse_button)
        self.setLayout(layout)

    def updateMethod(self):
        if self.parent():
            self.parent().updateMethod()

    def contents(self):
        """contents() -> str
        Return the contents of the line_edit

        """
        return self.line_edit.contents()

###############################################################################
# Constant Color widgets

class ColorChooserButton(QtGui.QFrame):
    def __init__(self, parent=None):
        QtGui.QFrame.__init__(self, parent)
        self.setFrameStyle(QtGui.QFrame.Box | QtGui.QFrame.Plain)
        self.setAttribute(QtCore.Qt.WA_PaintOnScreen)
        self.setAutoFillBackground(True)
        self.setColor(QtCore.Qt.white)
        self.setFixedSize(30,22)
        if system.systemType in ['Darwin']:
            #the mac's nice look messes up with the colors
            self.setAttribute(QtCore.Qt.WA_MacMetalStyle, False)
        
    def setColor(self, qcolor):
        self.qcolor = qcolor
        self.palette().setBrush(QtGui.QPalette.Window, self.qcolor)
        self.repaint()

    def sizeHint(self):
        return QtCore.QSize(24,24)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.openChooser()

    def openChooser(self):
        """
        openChooser() -> None
        
        """
        color = QtGui.QColorDialog.getColor(self.qcolor, self.parent())
        if color.isValid():
            self.setColor(color)
            self.emit(QtCore.SIGNAL("color_selected"))
        else:
            self.setColor(self.qcolor)

            
class ColorWidget(QtGui.QWidget):
    def __init__(self, contents, contentType, parent=None):
        """__init__(contents: str, contentType: str, parent: QWidget) ->
                                              ColorWidget
        """
        QtGui.QWidget.__init__(self, parent)
        layout = QtGui.QHBoxLayout()
        self.color_indicator = ColorChooserButton(self)
        self.connect(self.color_indicator,
                     QtCore.SIGNAL("color_selected"),
                     self.update_parent)
        self._last_contents = contents
        layout.setMargin(5)
        layout.setSpacing(5)
        layout.addWidget(self.color_indicator)
        layout.addStretch(1)
        self.setLayout(layout)
        if contents != "":
            color = contents.split(',')
            qcolor = QtGui.QColor(float(color[0])*255,
                                  float(color[1])*255,
                                  float(color[2])*255)
            self.color_indicator.setColor(qcolor)
        #self.update()

    def contents(self):
        """contents() -> str
        Return the string representation of color_indicator

        """
        return "%s,%s,%s" % (self.color_indicator.qcolor.redF(),
                             self.color_indicator.qcolor.greenF(),
                             self.color_indicator.qcolor.blueF())

    def update_parent(self):
        if self.parent():
            newContents = self.contents()
            if newContents!= self._last_contents:
                self.parent().updateMethod()
                self._last_contents = newContents
                
# class QPythonValueLineEdit(QtGui.QLineEdit):
#     """
#     QPythonValueLineEdit is a line edit that can be used to edit
#     int/float/string contents.
    
#     """
#     def __init__(self, contents, contentType, parent=None):
#         """ QPythonValueLineEdit(contents: str,
#                                  contentType: str,
#                                  parent: QWidget) -> QPythonValueLineEdit                                 
#         Initialize the line edit with its container and
#         contents. Content type is limited to 'int', 'float', and
#         'string'
        
#         """
#         QtGui.QLineEdit.__init__(self, contents, parent)
#         self._contents = contents
#         self._contentType = contentType
#         self.contentIsString = contentType=='String'
#         self.connect(self,
#                      QtCore.SIGNAL('returnPressed()'),
#                      self.update_parent)                     

#     def keyPressEvent(self, event):
#         """ keyPressEvent(event) -> None        
#         If this is a string line edit, we can use Shift+Enter to enter
#         the file name
        
#         """
#         k = event.key()
#         s = event.modifiers()
#         if (k == QtCore.Qt.Key_Enter or k == QtCore.Qt.Key_Return):
#             if s & QtCore.Qt.ShiftModifier:
#                 event.accept()
#                 if self.contentIsString and not self.multiLines:
#                     fileName = QtGui.QFileDialog.getOpenFileName(self,
#                                                                  'Use Filename '
#                                                                  'as Value...',
#                                                                  self.text(),
#                                                                  'All files '
#                                                                  '(*.*)')
#                     if not fileName.isEmpty():
#                         self.setText(fileName)
#                         self.update_parent()
                        

#                 # if self.contentIsString and self.multiLines:
# #                     fileNames = QtGui.QFileDialog.getOpenFileNames(self,
# #                                                                  'Use Filename '
# #                                                                  'as Value...',
# #                                                                  self.text(),
# #                                                                  'All files '
# #                                                                  '(*.*)')
# #                     fileName = fileNames.join(',')
# #                     if not fileName.isEmpty():
# #                         self.setText(fileName)
# #                         self.updateParent()
# #                         return
                
#             else:
#                 event.accept()
#                 self.update_text()
#         QtGui.QLineEdit.keyPressEvent(self,event)
#         # super(QPythonValueLineEdit, self).keyPressEvent(event)

#     def focusInEvent(self, event):
#         """ focusInEvent(event: QEvent) -> None
#         Pass the event to the parent
        
#         """
#         self._contents = str(self.text())
#         if self.parent():
#             self.parent().focusInEvent(event)
#         QtGui.QLineEdit.focusInEvent(self, event)
#         # super(QPythonValueLineEdit, self).focusInEvent(event)

#     def focusOutEvent(self, event):
#         """ focusOutEvent(event: QEvent) -> None
#         Update when finishing editing, then pass the event to the parent
        
#         """
#         self.update_parent()
#         if self.parent():
#             self.parent().focusOutEvent(event)
#         QtGui.QLineEdit.focusOutEvent(self, event)
#         # super(QPythonValueLineEdit, self).focusOutEvent(event)

#     def update_parent(self):
#         """ update_parent() -> None
#         Update parent parameters info if necessary
        
#         """
#         self.update_text()
#         if self.parent():
#             newText = str(self.contents())
#             if newText!=self.last_text:
#                 self.parent().updateMethod()
#                 self.last_text = newText

#     def update_text(self):
#         """ update_text() -> None
#         Update the text to the result of the evaluation
        
#         """
#         base = expression.evaluate_expressions(self.text())
#         if self.contentIsString:
#             self.setText(base)
#         else:
#             try:
#                 self.setText(str(eval(str(base), None, None)))
#             except:
#                 self.setText(base)

#     def contents(self):
#         """contents() -> str
#         As this is a QLineEdit, we just call text() """
#         return str(self.text())
    

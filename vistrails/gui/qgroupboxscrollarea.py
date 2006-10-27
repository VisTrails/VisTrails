from PyQt4 import QtCore, QtGui, QtOpenGL
from qframebox import *
from qmodulefunctiongroupbox import *
import pickle
import re

################################################################################

class QGroupBoxScrollArea(QtGui.QScrollArea):
    """Common class for the scroll areas for method values and
parameter explorations."""
    def __init__(self, builder, parent=None):
        """
        Parameters
        ----------

        - builder : 'QBuilder'

        - parent : 'QWidget'

        - name : 'str'
        
        """
        QtGui.QScrollArea.__init__(self,parent)
        self.qbuilder = builder
        self.module = None
        self._children = []

        self.box = QFrameBox(self)
        self.box.scroll = self
        self.setWidget(self.box)
        self.setWidgetResizable(True)
        self.box.show()
       
        self.update()
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Background,
                         palette.button().color())
        self.setPalette(palette)

    def setVisModule(self, module):
        """
        Parameters
        ----------

        - module : 'VisModule'
        
        """
        if module == self.module:
            return
        self.module = module
        self.clear()
        self.addWidgets()
        self.update()
       
    def clear(self):
        self._children = []
        self.box.clear()

    def dragEnterEvent(self,event):
        """
        Parameters
        ----------

        - event : 'QtGui.QDragEnterEvent'
        
        """
        if event.source() != self:
            event.accept()
        else:
            event.ignore()

################################################################################

#TODO: Rename this.
class QVTKMethodScrollArea(QGroupBoxScrollArea):

    def deleteChild(self, child):
        """
        Parameters
        ----------

        - child: QClickableGroupBox
        
        """
        id = child.functionId
        del self._children[id]
        for i in range(len(self._children)):
            self._children[i].functionId = i
            
        self.emit(QtCore.SIGNAL("deleteMethod(int)"),id)

    def changeValues(self, functionId):
        """
        Parameters
        ----------

        - functionId : 'int'
       
        """
        self.emit(QtCore.SIGNAL("valuesToBeChanged"),
                  functionId, self._children[functionId])

    def addWidgets(self):
        """
       
        """
        if not self.module:
            return

        paramList = {}
        funOrder = {}
        
        for i in range(len(self.module.functions)):
            fun = self.module.functions[i]
            params = tuple([p.value() for p in fun.params])
            if fun.name in paramList:
                funOrder[fun.name] += 1
                paramList[fun.name].append(params)
            else:
                funOrder[fun.name] = 0
                paramList[fun.name] = [params]
                
        for i in range(len(self.module.functions)):
            fun = self.module.functions[i]
            from core.modules.module_registry import registry
            configureWidgetType = registry.getPortConfigureWidgetType(self.module.name, fun.name)
            order = funOrder[fun.name]
            funOrder[fun.name] += -1
            if configureWidgetType==None or order==0:
                frame = QModuleFunctionGroupBox(fun,i,
                                                QtCore.QString(fun.name),
                                                self.box,
                                                configureWidgetType,
                                                paramList[fun.name])
                self.box.addFunction(frame)
                self.connect(frame, QtCore.SIGNAL("deleteMe"),
                             self.deleteChild)
                
                self.connect(frame, QtCore.SIGNAL("valuesHaveChanged(int)"),
                             self.changeValues)
                
                self.connect(self, QtCore.SIGNAL("requestValueChanges()"),
                             frame.provideValueChanges)

                self.connect(frame, QtCore.SIGNAL("applyConfiguration"),
                             self.applyConfiguration)

                self._children.append(frame)
            
                frame.show()
                self.box.update()
       
        self.update()

    def applyConfiguration(self, conf):
        (functionName, paramList) = conf
        if self.qbuilder.controllers.has_key(self.qbuilder.currentControllerName):
            controller = self.qbuilder.controllers[self.qbuilder.currentControllerName]
            controller.replaceModuleParams(self.module, functionName, paramList)

    def dropEvent(self,event):
        """
        Parameters
        ----------

        - event : 'QtGui.QDropEvent'

        """        
        text = event.mimeData().text()
        if text:
            try:
                obj = pickle.loads(str(text))
                dropType = obj[0]
                vtkclass = obj[1]
                vtkmethod = obj[2]
                vtksig = obj[4]
            except:
                return
            if dropType != "Method":
                return
            self.emit(QtCore.SIGNAL("newMethod"), (vtkclass, vtkmethod, vtksig))
        self.update()

################################################################################

class QVTKRangeScrollArea(QGroupBoxScrollArea):

    def deleteChild(self, child):
        """
        Parameters
        ----------

        - child : QClickableGroupBox
        
        """
        
        self.box.removeFunction(child)
        self._children.remove(child)
        child.deleteLater()

    def addWidget(self, fun):
        """
       
        """
        moduleId = self.qbuilder.pipelineView.selectedModule
        frame = QRangeFunctionGroupBox(fun, moduleId, QtCore.QString(fun.name), self.box)
        self.box.addFunction(frame)
        self.connect(frame, QtCore.SIGNAL("deleteMe"),
                     self.deleteChild)
        self._children.append(frame)
        
        
        frame.show()
        self.box.update()        
        self.update()

    def dropEvent(self,event):
        """
        Parameters
        ----------

        - event : 'QtGui.QDropEvent'

        """
        text = event.mimeData().text()
        if text:
            try:
                obj = pickle.loads(str(text))
                dropType = obj[0]
                vtkclass = obj[1]
                vtkmethod = obj[2]
            except:
                return
            if dropType != "Range":
                return
            from core.modules import module_registry
            functions = module_registry.registry.userSetMethods(vtkclass)
            f = functions[vtkclass][vtkmethod]
            assert len(f) == 1 # This will be invalid for overloaded functions..
            self.addWidget(f[0])
            self.update()

################################################################################
